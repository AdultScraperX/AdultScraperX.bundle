# -*- coding: utf-8 -*-
import base64
import json
from io import BytesIO

import requests  # 请求库
from PIL import Image
from app.internel.tools import Tools
from app.spider.kcc import KCC
from lxml import etree  # Xpath包


class Basic():
    '''
    基础操作类
    '''

    def __init__(self):
        '''
        初始化
        '''
        self.tools = Tools()
        self.client_session = requests.Session()
        k = KCC()
        if not k.g(self.client_session.get(k.r())):
            self.client_session = None

    def webSiteConfirmByurl(self, url, headers):
        '''
        针对有需要确认访问声明的站点
        return: <dict{issuccess,ex}>
        '''
        item = {
            'issuccess': False,
            'ex': None
        }
        self.client_session.headers = headers
        try:
            self.client_session.get(
                url, allow_redirects=False)
        except requests.RequestException as e:
            item.update({'issuccess': False, 'ex': e})

        item.update({'issuccess': True, 'ex': None})
        return item

    def getimage(self, url):
        try:
            r = self.client_session.get(url)
        except requests.RequestException as e:

            return r.content

    def getHtmlByurl(self, url):
        '''
        获取html对象函数
        url：需要访问的地址<str>
        return:<dict{issuccess,ex,html}>
        '''
        html = None
        item = {'issuccess': False, 'html': None, 'ex': None}
        try:
            r = self.client_session.get(url)
        except requests.RequestException as e:
            item.update({'issuccess': False, 'html': None, 'ex': e})
            return item

        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            t = r.text.replace('\r', '').replace(
                '\n', '').replace('\r\n', '')
            t = t.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
            t = t.replace(
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"', '')
            t = t.replace(
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">', '')

            html = etree.HTML(t)
            item.update({'issuccess': True, 'html': html, 'ex': None})
        else:
            scc = self.tools.statusCodeConvert(r.status_code)
            item.update({'issuccess': False, 'html': None,
                         'execpt': scc})
        return item

    def getHtmlByurlheaders(self, url, headers):
        '''
        获取html对象函数
        url：需要访问的地址<str>
        return:<dict{issuccess,ex,html}>
        '''
        html = None
        item = {'issuccess': False, 'html': None, 'ex': None}
        try:
            self.client_session.headers = headers
            r = self.client_session.get(url, allow_redirects=False)
        except requests.RequestException as e:
            item.update({'issuccess': False, 'html': None, 'ex': e})
            return item

        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            t = r.text.replace('\r', '').replace(
                '\n', '').replace('\r\n', '')
            t = t.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
            t = t.replace(
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"', '')
            t = t.replace(
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">', '')

            html = etree.HTML(t)
            item.update({'issuccess': True, 'html': html, 'ex': None})
        else:
            scc = self.tools.statusCodeConvert(r.status_code)
            item.update({'issuccess': False, 'html': None,
                         'execpt': scc})
        return item

    def getitemspage(self, html, xpaths):
        url = html.xpath(xpaths)
        return url

    def pictureProcessing(self, data):
        data = base64.b64decode(data)
        data = json.loads(data)
        mode = data['mode']
        url = data['url']
        r = data['r']
        w = data['w']
        h = data['h']
        webkey = data['webkey']
        cropped = None

        # 开始剪切
        if mode == 'poster':
            if webkey == 'arzon' or webkey == 'arzonanime':
                headers = {
                    'Accept': 'image/webp,*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Charset': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Connection': 'keep-alive',
                    'Cookie': '__utma=217774537.2052325145.1549811165.1549811165.1549811165.1;__utmb=217774537.9.10.1549811165;__utmc=217774537;__utmz=217774537.1549811165.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1',
                    'Host': 'img.arzon.jp',
                    'Referer': 'https://www.arzon.jp/item_1502421.html',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'
                }
                try:
                    response = self.client_session.get(url, headers=headers)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                if img.size[0] < img.size[1]:
                    # (left, upper, right, lower)
                    cropped = img.crop((0, 0, img.size[0], img.size[1]))
                elif img.size[0] > img.size[1]:
                    rimg = img.resize((int(w), int(h)), Image.ANTIALIAS)
                    # (left, upper, right, lower)
                    cropped = rimg.crop((int(w) - int(r), 0, int(w), int(h)))

            if webkey == 'javbus':
                try:
                    response = self.client_session.get(url)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                rimg = img.resize((int(w), int(h)), Image.ANTIALIAS)
                # (left, upper, right, lower)
                cropped = rimg.crop((int(w) - int(r), 0, int(w), int(h)))

            if webkey == 'onejav':
                try:
                    response = self.client_session.get(url)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                rimg = img.resize((int(w), int(h)), Image.ANTIALIAS)
                # (left, upper, right, lower)
                cropped = rimg.crop((int(w) - int(r), 0, int(w), int(h)))

            if webkey == 'data18':
                try:
                    response = self.client_session.get(url)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                # (left, upper, right, lower)
                cropped = img.crop((0, 0, img.size[0], img.size[1]))

            if webkey == 'caribbean':
                try:
                    response = self.client_session.get(url)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                # (left, upper, right, lower)
                cropped = img.crop((0, 0, img.size[0], img.size[1]))


        if mode == 'art':
            if webkey == 'arzon':
                headers = {
                    'Accept': 'image/webp,*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Charset': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Connection': 'keep-alive',
                    'Cookie': '__utma=217774537.2052325145.1549811165.1549811165.1549811165.1;__utmb=217774537.9.10.1549811165;__utmc=217774537;__utmz=217774537.1549811165.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1',
                    'Host': 'img.arzon.jp',
                    'Referer': 'https://www.arzon.jp/item_1502421.html',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'
                }
                try:
                    response = self.client_session.get(url, headers=headers)
                except Exception as ex:
                    print('error : %s' % repr(ex))
                    return cropped

                img = Image.open(BytesIO(response.content))
                # (left, upper, right, lower)
                cropped = img.crop((0, 0, img.size[0], img.size[1]))

        return cropped
