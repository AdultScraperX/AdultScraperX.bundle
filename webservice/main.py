#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import re
import sys

from app.spider.basic import Basic
from flask import Flask
from flask import render_template
from flask import send_file

if sys.version.find('2', 0, 1) == 0:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import StringIO
    from io import BytesIO

# 必填且与plex对应
import config as CONFIG

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
        try:
            img_io = StringIO()
            image.save(img_io, 'PNG')
        except Exception:
            img_io = BytesIO()
            image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpg')
    else:
        return ''


@app.route("/manual/<dirTagLine>/<q>/<token>")
def manual(dirTagLine, q, token):
    '''
    手动查询：返回所有成功的item
    '''
    if CONFIG.PLUGIN_TOKEN != '':
        if token != CONFIG.PLUGIN_TOKEN:
            return 'T-Error!'
    else:
        return 'T-Error!'
        
    q = base64.b64decode(q.replace('[s]', '/')).decode("utf-8")

    items = []
    if dirTagLine != "" or not CONFIG.SOURCE_LIST[dirTagLine]:
        for template in CONFIG.SOURCE_LIST[dirTagLine]:
            items = search(template['webList'], q, False)
    jsondata = json.dumps(items)
    base64jsondata = base64.b64encode(jsondata)
    return base64jsondata


@app.route('/auto/<dirTagLine>/<q>/<token>')
def auto(dirTagLine, q, token):
    '''
    自动查询：返回最先成功的item
    '''
    if CONFIG.PLUGIN_TOKEN != '':
        if token != CONFIG.PLUGIN_TOKEN:
            return 'T-Error!'
    else:
        return 'T-Error!'

    q = base64.b64decode(q.replace('[s]', '/')).decode("utf-8")
    print("filename=" + q)
    print("dirTagLine=" + dirTagLine)

    if dirTagLine != "" or not CONFIG.SOURCE_LIST[dirTagLine]:
        for template in CONFIG.SOURCE_LIST[dirTagLine]:
            # 循环模板列表
            codeList = re.findall(re.compile(template['pattern']), q)
            if len(codeList) == 0:
                break
            # 对正则匹配结果进行搜索
            for code in codeList:
                items = search(template['webList'], template['formatter'].format(code), True)
                if items.get("issuccess") == "true":
                    print("success")
                    return json.dumps(items)

    return json.dumps({'issuccess': 'false', 'json_data': [], 'ex': ''})


def search(webList, q, autoFlag):
    """
    根据搜刮网站列表进行数据搜刮
    :param webList: 搜刮网站的List 类型应为 app.spider.BasicSpider 的子类
    :param q: 待匹配的文件名
    :param autoFlag: 自动表示 True 为开启，开启后仅返回搜索到的第一个结果 ，False 为关闭
    :return:
        未查询到example
        {
            'issuccess': 'false',
            'json_data': [],
            'ex': ''
        }
        查询到
        {
        'issuccess': 'true',
        'json_data': [some json data],
        'ex': ''
        }
    """

    print("code=" + q)
    result = {
        'issuccess': 'false',
        'json_data': [],
        'ex': ''
    }
    for webSiteClass in webList:
        webSite = webSiteClass()
        items = webSite.search(q)
        for item in items:
            if item['issuccess']:
                result.update({'issuccess': 'true'})
                result['json_data'].append({webSite.getName(): item['data']})
                print("match=" + q)
                if autoFlag:
                    return result
    return result


if __name__ == "__main__":
    app.run(
        host=CONFIG.HOST,
        port=CONFIG.PORT,
        debug=CONFIG.DEBUG
    )
