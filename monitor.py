import argparse
import logging
import requests
import sys
import pytz
from datetime import datetime
from time import sleep


parser = argparse.ArgumentParser()
parser.add_argument('path', type=str, help='Расположение файла со списком url адресов')
parser.add_argument('delay', type=int, help='Задержка в секундах между опросами')
parser.add_argument('proxy_telegram', type=str, help='Прокси для telegram, формат socks5://user:pass@host:port')
parser.add_argument('bot_api_key', type=str, help='Ключ API для бота telegram')
parser.add_argument('chat_id', type=str, help='Идентификатор чата, формат - @chat_name')
parser.add_argument('log_to_file', type=int, help='Логировать в файл если равно 1, при любом другом значении лог в консоль')
args = parser.parse_args()


# настройка логгера
log_file_name = f'{(__file__)[:-3]}.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if args.log_to_file == 1:
    handler = logging.FileHandler(log_file_name)
else:
    handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(str(datetime.now(pytz.timezone('Europe/Moscow'))) + ' - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


TELEGRAM_URL = 'https://api.telegram.org'

# используемые коды ошибок
SUCCESS_CODE = 200
CON_ERROR_CODE = -1
CON_TIMEOUT_CODE = -2


# глобальная переменная для хранения информации о серверах в процессе выполнения
servers_info_list = []


# функция инициализирует глобальную переменную servers_info_list
def init_servers_info(urls_list):
    global servers_info_list
    for server in urls_list:
        servers_info_list.append({
            'url': server,
            'last_status': SUCCESS_CODE,
        })


def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf8') as f:
            lines = f.read().splitlines()
        return lines
    except FileNotFoundError:
        logger.error(f'Файл "{filename}" не найден')
        sys.exit(1)
    except:
        logger.error('Ошибка в процессе чтения файла')
        sys.exit(1)


def get_server_response(url):
    try:
        resp = requests.get(url)
        return resp.status_code
    except requests.exceptions.ConnectionError:
        return CON_ERROR_CODE
    except requests.exceptions.Timeout:
        return CON_TIMEOUT_CODE


# основная функция, которая перебирает url'ы и шлет оповещения
def servers_status_processing():
    global servers_info_list
    check_telegram_connect()
    for server in servers_info_list:
        current_status = get_server_response(server['url'])
        # проверяем, что текущий статус есть в списке знакомых нам статусов
        if current_status in [SUCCESS_CODE, CON_ERROR_CODE, CON_TIMEOUT_CODE]:
            # проверяем на стутус 200
            if current_status == SUCCESS_CODE and server['last_status'] != SUCCESS_CODE:
                msg = f'Сервер доступен - {server["url"]}'
                logger.info(msg)
                send_server_status_to_user(msg)

            # проверяем на requests.exceptions.ConnectionError
            if current_status == CON_ERROR_CODE and server['last_status'] != CON_ERROR_CODE:
                msg = f'Ошибка подключения - {server["url"]}'
                logger.error(msg)
                send_server_status_to_user(msg)

            # проверяем на requests.exceptions.Timeout
            if current_status == CON_TIMEOUT_CODE and server['last_status'] != CON_TIMEOUT_CODE:
                msg = f'Ошибка таймаута - {server["url"]}'
                logger.error(msg)
                send_server_status_to_user(msg)
        else:
            # обрабатываем код ответа отличный от SUCCESS_CODE
            if server['last_status'] != current_status:
                msg = f'Ошибка с кодом {current_status} - {server["url"]}'
                logger.error(msg)
                send_server_status_to_user(msg)

        server['last_status'] = current_status


def add_datetime_to_string(user_string):
    tz_moscow = pytz.timezone('Europe/Moscow')
    return f'{datetime.now(tz_moscow).strftime("%d-%m-%Y %H:%M:%S")} - {user_string}'


def check_telegram_connect():
    proxy_address = args.proxy_telegram
    proxies = {
        'http': proxy_address,
        'https': proxy_address,
    }
    try:
        resp = requests.get(
            url=f'{TELEGRAM_URL}',
            proxies=proxies,
        )
        if resp.status_code != SUCCESS_CODE:
            logger.error(f'Ошибка с кодом {resp.status_code} - {TELEGRAM_URL}')
    except requests.exceptions.ConnectionError:
        logger.error(f'Ошибка подключения - {TELEGRAM_URL}')
    except requests.exceptions.Timeout:
        logger.error(f'Ошибка таймаута - {TELEGRAM_URL}')


def send_msg_to_telegram_chanel(msg):
    proxy_address = args.proxy_telegram
    proxies = {
        'http': proxy_address,
        'https': proxy_address,
    }
    params = {
        'chat_id': args.chat_id,
        'text': add_datetime_to_string(msg),
    }
    try:
        url = f'{TELEGRAM_URL}/bot{args.bot_api_key}/sendMessage'
        resp = requests.get(
            url=url,
            params=params,
            proxies=proxies,
        )
        if resp.status_code != SUCCESS_CODE:
            logger.error(f'Ошибка с кодом {resp.status_code} - {url}')
    except requests.exceptions.ConnectionError:
        logger.error(f'Ошибка подключения - {TELEGRAM_URL}')
    except requests.exceptions.Timeout:
        logger.error(f'Ошибка таймаута - {TELEGRAM_URL}')



# функция отправляет статус сервера пользователю
# реализация любая (telegram, sms, slack и т.д.)
def send_server_status_to_user(msg):
    send_msg_to_telegram_chanel(msg)


# функция запускает бесконечный цикл для проверки серверов по интервалу sec
def run_check(sec):
    while True:
        logger.info('Опрос адресов ...')
        servers_status_processing()
        logger.info('Опрос завершен ...')
        sleep(sec)


# Запуск скрипта
logger.info('Скрипт запущен ...')
urls_list = read_file(args.path)
init_servers_info(urls_list)
run_check(args.delay)
