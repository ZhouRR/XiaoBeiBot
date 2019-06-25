# -*- coding: utf-8 -*-

from django.conf import settings
import urllib3
import json
import os
import datetime
from pytz import timezone

cst_tz = timezone('Asia/Shanghai')


def log(*args, console=True):
    if not settings.DEBUG:
        return
    output(args, console=console)


def output(*args, console=True):
    log_out = ''
    for arg in args:
        if arg is None:
            continue
        log_out += str(arg)
    if console:
        print(log_out)
    save_log(log_out)


def save_log(log_str):
    now = datetime.datetime.now(cst_tz)
    date = now.strftime("%Y-%m-%d")
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(settings.BASE_DIR, 'cache/log/')
    log_last = ''
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    elif os.path.exists(log_path + date + '.log'):
        with open(log_path + date + '.log', 'r', encoding='utf-8', errors='ignore') as fp:
            log_last = fp.read()
    with open(log_path + date + '.log', 'w', encoding='utf-8', errors='ignore') as fpo:
        fpo.write(log_last)
        fpo.write(date_time + '   ' + log_str + u'\n')


def get(url, content):
    output('GET:', url)

    pool_manger = urllib3.PoolManager()
    resp = pool_manger.request('GET', url, headers={
        'Content-Type': content
    })
    output('status:', resp.status)
    data = json.loads(resp.data.decode())
    output('data:', data, console=False)
    return data


def post(url, post_data, content):
    output('POST:', url)
    output('post_data', post_data)

    pool_manger = urllib3.PoolManager()
    resp = pool_manger.request('POST', url, body=post_data, headers={
        'Content-Type': content
    })
    output('status:', resp.status)
    data = json.loads(resp.data.decode())
    output('data:', data, console=False)
    return data
