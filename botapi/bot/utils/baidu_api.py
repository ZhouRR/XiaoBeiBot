# -*- coding: utf-8 -*-

from django.conf import settings
import json
import urllib.parse

from . import request_api


def get_token(client_id, client_secret):
    # 获取TOKEN
    url = 'https://aip.baidubce.com/oauth/2.0/token?' \
           'grant_type=client_credentials&' \
           'client_id=$client_id&client_secret=$client_secret'
    url = url.replace('$client_id', client_id)
    url = url.replace('$client_secret', client_secret)

    data = request_api.get(url, 'application/json; charset=utf-8')

    return data['access_token']


def get_response(msg, user_name):
    request_api.log('message: ', msg)
    url = settings.INTERACTION_URL + settings.access_token
    post_data = {
        "log_id": "UNITTEST_10000",
        "version": "2.0",
        "service_id": settings.SERVICE_ID,
        "session_id": settings.session_id,
        "request": {
            "query": msg,
            "user_id": user_name
        },
        "dialog_state": {
            "contexts": {
                'SYS_REMEMBERED_SKILLS': settings.SKILL_IDS
            }
        }
    }
    data = request_api.post(url, json.dumps(post_data) + "\n\n", 'application/json; charset=utf-8')
    err_code = str(data['error_code'])
    request_api.log('error_code: ' + err_code)

    if err_code != '0':
        return '好的，我在听。'
    elif data['result']['response_list'] is None or len(data['result']['response_list']) == 0:
        return '我不能明白你在说什么。'
    elif data['result']['response_list'][0]['action_list'] is None or \
            len(data['result']['response_list'][0]['action_list']) == 0:
        return '我不能明白你想做什么。'
    reply = data['result']['response_list'][0]['action_list'][0]['say']
    reply = reply + "\r\n\r\n--------------分析--------------\r\n" + parse_reply(data['result'])
    request_api.log('reply: ', reply)
    settings.session_id = str(data['result']['session_id'])
    # 对话消息
    return reply


def parse_reply(rep_res):
    reply = ''
    for response in rep_res['response_list']:
        reply += '技能ID：' + response['origin'] + '\r\n'
        reply += '意图：\r\n'
        if 'schema' in response:
            reply += '--意图内容：%s 意图置信度：%s\r\n' % (response['schema']['intent'],
                                                 str(response['schema']['intent_confidence'])) + '\r\n'
            if 'slots' in response['schema']:
                reply += '--意图词槽：\r\n'
                for slot in response['schema']['slots']:
                    reply += "----词槽名称:%s 词槽值:%s 开始位置:%s 长度:%s 置信度 %s\r\n" % (slot['name'],
                                                                              slot['original_word'],
                                                                              str(slot['begin']),
                                                                              str(slot['length']),
                                                                              str(slot['confidence']))
        if 'action_list' in response:
            reply = reply + '--意图动作：\r\n'
            for action in response['action_list']:
                reply = reply + "----动作ID:%s 回答:%s 置信度:%s\r\n" % (str(action['action_id']),
                                                                  action['say'], str(action['confidence']))
        reply += '\r\n'
    return reply


def get_photo_response(img):
    url = settings.DISTINGUISH_URL + settings.photo_access_token
    print('img: ', str(img))
    post_data = {
        "image": img,
        "probability": True
    }

    data = request_api.post(url, urllib.parse.urlencode(post_data), 'application/x-www-form-urlencoded')
    err_code = None
    reply = ''
    if err_code is not None:
        reply = '识别失败'
    elif data['words_result'] is not None:
        for word in data['words_result']:
            reply += word['words']

    request_api.log('reply: ', reply)
    # 用于接收来自朋友间的对话消息
    return reply
