#### Описание
Скрипт для мониторинга доступности сайтов. После запуска скрипт работает до прерывания его работы пользователем. Уведомления рассылаются только в случае смены статуса доступности сервера. Работа скрипта логируется в консоль или файл `monitor.log`. Уведомления отправляются в телеграм канал от имени бота.

Скрипт умеет обрабатывать следующие состояния:
 - ошибку ConnectionError
 - ошибку Timeout
 - код ответа 200
 - остальные коды ответа (текст "Ошибка с кодом {код ответа сервра} - {url}") 
 
 
#### Требования к ПО
- Установленный Python 3.7
- Установленный инструмент для работы с виртуальными окружениями virtualenv
```bash
pip install virtualenv
```

#### Установка
```bash
git clone https://github.com/arkuz/site_monitor
cd site_monitor
virtualenv env
env/scripts/activate
pip install -r requirements.txt
```

#### Формат файла со списком url адресов
```bash
http://127.0.0.1:5000/blog/
http://yandex.ru
http://google.com
```

#### Настройки telegram
Для получения уведомлений в телеграм необходимо:
1. Создать бота через `@BotFather`
2. Создать беседу в телеграм
3. Добавить бота в беседу
4. Добавить всех пользователей, которые хотят получать уведомления, в беседу созданную на шаге 2

#### Параметры запуска
Скрипт `monitor.py` принимает 6 обязвтельных позиционных параметров:
```bash
  path            Расположение файла со списком url адресов
  delay           Задержка в секундах между опросами
  proxy_telegram  Прокси для telegram, формат socks5://user:pass@host:port
  bot_api_key     Ключ API для бота telegram
  chat_id         Идентификатор чата, формат - @chat_name
  log_to_file     Логировать в файл если равно 1, при любом другом значении
                  лог в консоль
```

#### Запуск
```bash
python monitor.py urls.txt 60 socks5://login:pass@my-site.ru:1080 111111111:AAHH7k7pklz9ZFBcTucu8e2OWb43OKcl4UE @my_group 0
```

#### Пример работы
```bash
05-12-2019 14:38:07 - Ошибка подключения - http://127.0.0.1:5000/blog/
05-12-2019 14:38:34 - Сервер доступен - http://127.0.0.1:5000/blog/
```
