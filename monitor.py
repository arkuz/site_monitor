import argparse
import logging
import os
import requests
import sys
from datetime import datetime
from time import sleep


parser = argparse.ArgumentParser()
parser.add_argument('path', type=str, help='Расположение файла со списком url адресов')
parser.add_argument('delay', type=int, help='Задержка в секундах между опросами')
args = parser.parse_args()


log_file_name = f'{os.path.basename(os.path.abspath(__file__))[:-3]}.log'
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename=log_file_name,
                    )


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
            'last_status': SUCCESS_CODE
        })


def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf8') as f:
            lines = f.read().splitlines()
        return lines
    except FileNotFoundError:
        logging.error(f'Файл "{filename}" не найден')
        sys.exit(1)
    except:
        logging.error('Ошибка в процессе чтения файла')
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
    for server in servers_info_list:
        current_status = get_server_response(server['url'])
        # проверяем, что текущий статус есть в списке знакомых нам статусов
        if current_status in [SUCCESS_CODE, CON_ERROR_CODE, CON_TIMEOUT_CODE]:
            # проверяем на стутус 200
            if current_status == SUCCESS_CODE and server['last_status'] != SUCCESS_CODE:
                msg = f'Сервер доступен - {server["url"]}'
                logging.info(msg)
                send_server_status_to_user(msg)

            # проверяем на requests.exceptions.ConnectionError
            if current_status == CON_ERROR_CODE and server['last_status'] != CON_ERROR_CODE:
                msg = f'Ошибка подключения - {server["url"]}'
                logging.error(msg)
                send_server_status_to_user(msg)

            # проверяем на requests.exceptions.Timeout
            if current_status == CON_TIMEOUT_CODE and server['last_status'] != CON_TIMEOUT_CODE:
                msg = f'Ошибка таймаута - {server["url"]}'
                logging.error(msg)
                send_server_status_to_user(msg)
        else:
            # обрабатываем код ответа отличный от SUCCESS_CODE
            if server['last_status'] != current_status:
                msg = f'Ошибка с кодом {current_status} - {server["url"]}'
                logging.error(msg)
                send_server_status_to_user(msg)

        server['last_status'] = current_status


def add_datetime_to_string(user_string):
    return f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - {user_string}'


# функция отправляет статус сервера пользователю
# реализация любая (telegram, sms, slack и т.д.)
def send_server_status_to_user(msg):
    print(add_datetime_to_string(msg))


# функция запускает бесконечный цикл для проверки серверов по интервалу sec
def run_check(sec):
    while True:
        servers_status_processing()
        sleep(sec)


# Запуск скрипта
urls_list = read_file(args.path)
init_servers_info(urls_list)
run_check(args.delay)
