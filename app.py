from flask import Flask, request, make_response, jsonify
import json
import base64
import time
import os
import datetime
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
bot_token = '5230558404:AAHe_TJo0bHER0c6o7vaj2o5i44RgM-aKNg'# put your (bot) token here
link = f'https://api.telegram.org/bot{bot_token}/sendMessage'
chat_id = 774802054# chat id with bot

import datetime


class Shedule(object):

    def __init__(self, time_delta=datetime.timedelta(minutes=10)):
        self.time_delta = time_delta

        self.alarm_time = datetime.timedelta(hours=8, minutes=0)
        self.coffe_time = datetime.timedelta(hours=8, minutes=20)
        self.car_time = datetime.timedelta(hours=8, minutes=40)
        self.burger_time = datetime.timedelta(hours=9, minutes=0)
        self.lunch_start_time = datetime.timedelta(hours=14, minutes=0)
        self.lunch_end_time = datetime.timedelta(hours=15, minutes=0)
        self.turnoff_work_time = datetime.timedelta(hours=18, minutes=0)
        self.turnoff_home_time = datetime.timedelta(hours=23, minutes=0)

    # dict with keys: 'call_num', 'call_type', 'call_time'
    def get_current_action(self, call_info):

        if call_info['call_type'] == 'click':
            result = self.one_click_handler(call_info)
        elif call_info['call_type'] == 'double_click':
            result = self.double_click_handler(call_info)
        elif call_info['call_type'] == 'long_press':
            result = self.long_press_handler(call_info)
        else:
            result = self.unknown_type_handler(call_info)
        return result

    def one_click_handler(self, call_info):

        call_num = call_info['call_num']
        call_type = call_info['call_type']
        call_time = call_info['call_time']
        call_time = call_time.hour * 3600 + call_time.minute * 60 + call_time.second
        call_time = datetime.timedelta(seconds=call_time)

        info_ = 'call_num:' + str(call_info['call_num']) + 'call_type:' + str(call_info['call_type']) + 'call_time:' + str(call_info['call_time'])
        
        if call_time - self.alarm_time < self.time_delta:
            return {'action_type': 'Выключить будильник.' + info_}

        elif call_time - self.coffe_time < self.time_delta:
            return {'action_type': 'Поставить готовиться кофе.' + info_}

        elif call_time - self.car_time < self.time_delta:
            return {'action_type': 'Поставить машину на автоподогрев.' + info_}

        elif call_time - self.burger_time < self.time_delta:
            return {'action_type': 'Сделать стандартный заказ в Бургер Кинге.' + info_}

        elif call_time >= self.lunch_start_time and call_time <= self.lunch_end_time:
            return {'action_type': 'Заказать стандартный обед в столовке офиса.' + info_}

        elif call_time - self.turnoff_work_time < self.time_delta:
            return {'action_type': 'Выключить все системы на рабочем месте.' + info_}

        elif call_time >= self.turnoff_home_time:
            return {'action_type': 'Выключить свет, телевизор и тд. в квартире.' + info_}

        else:
            return {'action_type': 'В данный момент действий не запланировано.' + info_}

    def double_click_handler(self, call_info):
        return {'action_type': 'Сообщение начальнику, что опоздаешь.'}

    def long_press_handler(self, call_info):
        return {'action_type': 'Запуск ядерной боеголовки.'}

    def unknown_type_handler(self, call_info):
        raise TypeError(f'Обработка нажатия типа {call_info["call_type"]} не реализована.')


my_shedule = Shedule()
demo_idx = 0
demo_time = [
            datetime.datetime.fromisoformat("2012-12-12 08:00:00"),
            datetime.datetime.fromisoformat("2012-12-12 08:20:00"),
    datetime.datetime.fromisoformat("2012-12-12 08:40:00"),
             datetime.datetime.fromisoformat("2012-12-12 09:00:00"),
    datetime.datetime.fromisoformat("2012-12-12 14:00:00"),
             datetime.datetime.fromisoformat("2012-12-12 15:00:00"),
    datetime.datetime.fromisoformat("2012-12-12 18:00:00"),
    datetime.datetime.fromisoformat("2012-12-12 23:00:00"),
             ]
def make_curl(text):
    return f"\
                curl -X POST -H \'Content-Type: application/json\' -d\
                \'{{\
                    \"chat_id\": \"-{chat_id}\",\
                    \"text\": \"`{text}`\",\
                    \"disable_notification\": true,\
                    \"parse_mode\": \"MarkdownV2\"\
                }}\' {link}\
            "
def send_notification(text):
    curl_body = make_curl(text)
    telegram_response = json.loads(os.popen(curl_body).read())
    if not telegram_response['ok']:
        raise TimeoutError("Something goes wrong...")  # more complex cases are possible
    # safely send parts

@app.route('/', methods=['POST'])
def hello_world():  # put application's code here
    global demo_idx # for demo
    global demo_time # for demo

    query_time = time.time()

    data_json = json.loads(request.data)
    button_response = json.loads(base64.b64decode(data_json["data"].encode('utf-8')))
    press_type = button_response['telemetry']['firstButton']['status']
    query_time = datetime.datetime.fromtimestamp(query_time) # will be instead of demo_time
    if demo_idx == len(demo_time):
        demo_idx = 0 # reset states for demo
    action_exec = my_shedule.get_current_action(
        {'call_num':demo_idx, 'call_type':press_type, 'call_time':demo_time[demo_idx]}
    )
    send_notification(action_exec['action_type']) # тут все действия
    if press_type == 'click':
        demo_idx+=1 # cool demo
    return 'Bot triggered'

@app.route("/", methods=['OPTIONS'], provide_automatic_options=False)
def inde1x():
    response = (jsonify({'status': 200}))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Origin: *');
    response.headers.add('Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE, OPTIONS');
    response.headers.add('Access-Control-Allow-Headers: Origin, Content-Type, X-Auth-Token');

    return make_response(response, 200)
@app.route("/")
def index():
    return 'Это сервер для респонсов. Сервер сделан Аркадием, Алексеем и Владом.'
