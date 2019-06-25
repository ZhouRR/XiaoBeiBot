# -*- coding: utf-8 -*-

import itchat
import json
import time
import base64
from django.conf import settings

from . import request_api
from . import baidu_api


@itchat.msg_register(['Text', 'Map', 'Card', 'Note', 'Sharing'])
def text_reply(msg):
    request_api.log('personal received: ', json.dumps(msg))
    # itchat.send('%s' % get_response(msg['Text']), msg['FromUserName'])


@itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'])
def download_files(msg):
    if msg.type is 'Picture':
        path = settings.CACHE_DIR + '/' + msg.fileName
        msg.download(path)
        type_symbol = {
            'Picture': 'img',
            'Video': 'vid'}.get(msg.type, 'fil')
        request_api.log('file:', '@%s@%s' % (type_symbol, msg.fileName))
        base64_data = base64_image(path)
        reply = baidu_api.get_photo_response(base64_data)
        itchat.send('%s' % reply, msg['FromUserName'])


@itchat.msg_register('Friends')
def add_friend(msg):
    itchat.add_friend(**msg['Text'])
    # itchat.get_contract()
    # itchat.send('很高兴见到你!', msg['RecommendInfo']['UserName'])


@itchat.msg_register('Text', 'Picture', isGroupChat=True)
def group_reply(msg):
    # request_api.log('group received: ', msg.type)
    if msg['isAt']:
        request_api.log('received: ', json.dumps(msg))

        # if msg['User']['Self']['NickName'] is not settings.BOT_NAME:
        #         #     return

        all_msg = msg['Content']

        if all_msg is '':
            return

        half_msg = all_msg.replace('@' + msg['User']['Self']['NickName'], '')
        half_msg = half_msg.replace('@' + settings.BOT_NAME, '')
        half_msg = half_msg.lstrip()
        time.sleep(1)
        reply = baidu_api.get_response(half_msg, msg['ActualUserName'])
        reply.replace('<USER-NAME>', msg['ActualNickName'])
        itchat.send(u'@%s %s' % (msg['ActualNickName'], reply), msg['FromUserName'])


def base64_image(file_dir):
    # 图片编码为base64
    with open(file_dir, 'rb') as fin:
        image_data = fin.read()
        base64_data = base64.b64encode(image_data)
        return base64_data


def qr_complete(uuid, status, qrcode):
    # print(uuid)
    # print(status)
    settings.qr_code = qrcode


def reply_text(to_user, from_user, content):
    """
    以文本类型的方式回复请求
    """
    return """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(to_user, from_user, int(time.time() * 1000), content)
