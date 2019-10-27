#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re

from app.spider.basic import Basic
from app.spider.data18 import Data18
from app.spider.onejav import Onejav
from app.spider.javbus import Javbus
from app.spider.arzon_anime import ArzonAnime
from app.spider.arzon import Arzon

import base64
import requests as req
from flask import Flask
from flask import render_template
from flask import send_file
import json
from PIL import Image
from io import BytesIO
import io

import sys

if sys.version.find('2', 0, 1) == 0:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import StringIO

# 必填且与plex对应
from config import PLUGIN_TOKEN
from config import PATTERN_LIST

app = Flask(__name__)


@app.route("/")
@app.route("/index")
@app.route("/warning")
def warning():
    return render_template(
        'warning.html'
    )


@app.route("/img/<data>")
def img(data):
    image = Basic().pictureProcessing(data)
    if image != None:
        img_io = StringIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpg')
    else:
        return ''


@app.route("/manual/<lang>/<q>/<token>")
def manual(lang, q, token):
    '''
    手动查询：返回所有成功的item
    '''
    if PLUGIN_TOKEN != '':
        if token != PLUGIN_TOKEN:
            return 'T-Error!'
    else:
        return 'T-Error!'

    jsondata = ''
    items = {
        'issuccess': 'false',
        'json_data': [],
        'ex': ''
    }
    if lang == 'en':
        '欧美'
        ########################################################################
        ### https://data18.empirestores.co/ ###
        ########################################################################
        data18_items = Data18().search(q)
        for data18_item in data18_items:
            if data18_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Data18': data18_item['data']})
        ########################################################################

    elif lang == 'ja':
        '日本'

        ########################################################################
        ### AV https://www.arzon.jp/ ###
        ########################################################################
        arzon_item_list = Arzon().search(q)
        for arzon_item in arzon_item_list:
            if arzon_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Arzon': arzon_item['data']})
        ########################################################################

        ########################################################################
        ### https://www.javbus.com/ ###
        ########################################################################
        javbus_item_list = Javbus().search(q)
        for javbus_item in javbus_item_list:
            if javbus_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Javbus': javbus_item['data']})
        ########################################################################

        ########################################################################
        ### https://onejav.com/ ###
        ########################################################################
        onejav_item_list = Onejav().search(q)
        for onejav_item in onejav_item_list:
            if onejav_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Onejav': onejav_item['data']})
        ########################################################################

        ########################################################################
        ### Anime https://www.arzon.jp/ ###
        ########################################################################
        arzon_anime_item_list = ArzonAnime().search(q)
        for arzon_anime_item in arzon_anime_item_list:
            if arzon_anime_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append(
                    {'ArzonAnime': arzon_anime_item['data']})
        ########################################################################

    jsondata = json.dumps(items)
    base64jsondata = base64.b64encode(jsondata)
    return base64jsondata


@app.route('/auto/<lang>/<q>/<token>')
def auto(lang, q, token):
    '''
    自动查询：返回最先成功的item
    '''
    if PLUGIN_TOKEN != '':
        if token != PLUGIN_TOKEN:
            return 'T-Error!'
    else:
        return 'T-Error!'

    # 正则列表

    for pattern in PATTERN_LIST:
        codeList = re.findall(re.compile(pattern), q)
        if len(codeList) == 0:
            break
        for code in codeList:
            items = searchAuto(lang, formatName(code))
            if items.get("issuccess") == "issuccess":
                return json.dumps(items)

    return json.dumps({'issuccess': 'false', 'json_data': [], 'ex': ''})


def formatName(code):
    if code[-4] != "-":
        listCoed = list(code)
        listCoed.insert(len(code) - 3, "-")
        return "".join(listCoed)
    return code


def searchAuto(lang, q):
    print(q)
    items = {
        'issuccess': 'false',
        'json_data': [],
        'ex': ''
    }
    if lang == 'en':
        ########################################################################
        ### https://data18.empirestores.co/ ###
        ########################################################################
        data18_items = Data18().search(q)
        for data18_item in data18_items:
            if data18_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Data18': data18_item['data']})
                return items
        ########################################################################

        ########################################################################
        ### https://www.dorcelvision.com/en/ ###
        ########################################################################
        '''       
        dorcelvision_item = Dorcelvision().search(q)
        if dorcelvision_item['issuccess']:
            items.update({'issuccess': 'true', 'json_data': [{
                        'Dorcelvision': dorcelvision_item['data']}]})
            jsondata = json.dumps(items)
            return jsondata
        '''
        ########################################################################

    elif lang == 'ja':
        ########################################################################
        ### AV https://www.arzon.jp/ ###
        ########################################################################
        arzon_items = Arzon().search(q)
        for arzon_item in arzon_items:
            if arzon_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Arzon': arzon_item['data']})
                return items
        ########################################################################

        ########################################################################
        ### https://www.javbus.com/ ###
        ########################################################################
        javbus_items = Javbus().search(q)
        for javbus_item in javbus_items:
            if javbus_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Javbus': javbus_item['data']})
                return items
        ########################################################################

        ########################################################################
        ### https://onejav.com/ ###
        ########################################################################
        onejav_itemS = Onejav().search(q)
        for onejav_item in onejav_itemS:
            if onejav_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({'Onejav': onejav_item['data']})
                return items
        ########################################################################

        ########################################################################
        ### Anime https://www.arzon.jp/ ###
        ########################################################################
        arzon_anime_items = ArzonAnime().search(q)
        for arzon_anime_item in arzon_anime_items:
            if arzon_anime_item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append(
                    {'ArzonAnime': arzon_anime_item['data']})
                return items
        ########################################################################


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8888,
        debug=False
    )
