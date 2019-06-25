# -*- coding: utf-8 -*-

from django.conf import settings
import urllib3
import json
import os
import time


def log(*args, console=True):
    if not settings.DEBUG:
        return
    log_out = ''
    for arg in args:
        if arg is None:
            continue
        log_out += str(arg)
    if console:
        print(log_out)
    save_log(log_out)


def save_log(log_str):
    date = time.strftime("%Y-%m-%d", time.localtime())
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_path = os.path.join(settings.BASE_DIR, 'cache/log/')
    log_last = ''
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    elif os.path.exists(log_path + date + '.log'):
        with open(log_path + date + '.log', 'r', encoding='utf-8', errors='ignore') as fp:
            log_last = fp.read()
    with open(log_path + date + '.log', 'w', encoding='utf-8', errors='ignore') as fpo:
        fpo.write(log_last)
        fpo.write(u'\n')
        fpo.write(date_time)
        fpo.write(u'\n')
        fpo.write(log_str)
        fpo.write(u'\n')


def get(url, content):
    log('GET:', url)

    pool_manger = urllib3.PoolManager()
    resp = pool_manger.request('GET', url, headers={
        'Content-Type': content
    })
    log('status:', resp.status)
    data = json.loads(resp.data.decode())

    return data


def post(url, post_data, content):
    log('POST:', url)
    log('post_data', post_data)

    pool_manger = urllib3.PoolManager()
    resp = pool_manger.request('POST', url, body=post_data, headers={
        'Content-Type': content
    })
    log('status:', resp.status)
    log('data:', resp.data.decode(), console=False)
    data = json.loads(resp.data.decode())
    return data
