# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
import itchat
import threading
import time
import hashlib

import xml.etree.ElementTree as EleTree

from bot.serializers.serializers import *
from bot.utils import baidu_api, request_api, bot


class LoginThread (threading.Thread):

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        itchat.auto_login(picDir=settings.QR_FILE, qrCallback=bot.qr_complete)
        itchat.run()
        print("Exiting " + self.name)


class BotLoginViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        if not hasattr(settings, 'access_token') or settings.access_token is '':
            settings.access_token = baidu_api.get_token(settings.INTER_API_KEY, settings.INTER_SECRET_KEY)
        if not hasattr(settings, 'session_id'):
            settings.session_id = ''
        settings.qr_code = ''
        itchat.logout()
        child_thread = LoginThread(1, "Thread-1", 1)
        child_thread.start()
        # itchat.auto_login(picDir=settings.QR_FILE)
        # itchat.run()

        time_out = 0
        while True and time_out <= settings.QR_TIMEOUT:
            time.sleep(1)
            if settings.qr_code is not '':
                break
            time_out += 1
        return HttpResponse(settings.qr_code, content_type="image/png")

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        return Response('', status=status.HTTP_400_BAD_REQUEST)


class PublicVerifyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = GroupSerializer

    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        params = request.query_params
        request_api.log(params)

        token = 'xiaobei777'

        # 进行字典排序
        data = [token, params['timestamp'], params['nonce']]
        data.sort()

        # 进行sha1加密
        sha1 = hashlib.sha1()
        sha1.update(data[0].encode("utf-8"))
        sha1.update(data[1].encode("utf-8"))
        sha1.update(data[2].encode("utf-8"))
        signature = sha1.hexdigest()

        if signature == params['signature']:
            return HttpResponse(params['echostr'])
        else:
            return HttpResponse('')

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        utf8_parser = EleTree.XMLParser(encoding='utf-8')
        xml = EleTree.fromstring(request.body, utf8_parser)
        to_user = xml.find('ToUserName').text
        from_user = xml.find('FromUserName').text
        msg_type = xml.find("MsgType").text
        # create_time = xml.find("CreateTime")
        # 判断类型并回复
        if msg_type == "text":
            content = xml.find('Content').text
            if not hasattr(settings, 'access_token') or settings.access_token is '':
                settings.access_token = baidu_api.get_token(settings.INTER_API_KEY, settings.INTER_SECRET_KEY)
            if not hasattr(settings, 'session_id'):
                settings.session_id = ''
            return HttpResponse(bot.reply_text(from_user, to_user, baidu_api.get_response(content, from_user)))
        else:
            return HttpResponse('请输入文字')
