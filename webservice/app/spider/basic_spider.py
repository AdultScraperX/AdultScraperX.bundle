# -*- coding: utf-8 -*-
from lxml import etree  # Xpath包
import sys
if sys.version.find('2', 0, 1) == 0:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import StringIO
    from io import BytesIO

from PIL import Image

from app.internel.config import ConfigManager
import requests

from app.internel.tools import Tools


class BasicSpider:

    def __init__(self):
        self.tools = Tools()
        self.configmanager = ConfigManager()
        self.client_session = requests.Session()

    def search(self, q):
        """
        根据番号爬取数据（子类必须实现）
        :param q: 番号
        :return:  json格式的数据plex直接使用
        """
        raise RuntimeError('未实现接口')

    def analysisMediaHtmlByxpath(self, html, q):
        """
       根据爬取的数据格式化为plex能使用的数据（子类必须实现，供search（q）方法使用的工具方法）
       :param html: 番号
       :param q: 番号
       :return:  格式化后的网站数据，可被plex使用
       """
        raise RuntimeError('未实现接口')

    def posterPicture(self, url, r, w, h):
        """
       处理海报图片，默认实现根据webui配置进行剪裁，如果子类无特殊需求不需要重写
       :param url: 图片地址
       :param r: 横向裁切位置
       :param w: 缩放比例:宽
       :param h: 缩放比例:高
       :return: 处理后的图片
       """
        cropped = None
        try:
            response = self.client_session.get(url)
        except Exception as ex:
            print('error : %s' % repr(ex))
            return cropped

        img = Image.open(BytesIO(response.content))
        rimg = img.resize((int(w), int(h)), Image.ANTIALIAS)
        # (left, upper, right, lower)
        cropped = rimg.crop((int(w) - int(r), 0, int(w), int(h)))
        return cropped

    def artPicture(self, url, r, w, h):
        """
        处理艺人图片，默认实现不进行剪裁，如果子类无特殊需求不需要重写
        :param url: 图片地址
        :param r: 横向裁切位置
        :param w: 缩放比例:宽
        :param h: 缩放比例:高
        :return: 处理后的图片
        """
        # TODO 目前除Arzon实现了演员图片外其他站未实现，且默认实现未提供
        return None

    # TODO 实现背景图功能

    def getName(self):
        return self.__class__.__name__

    def pictureProcessing(self, data):
        mode = data['mode']
        url = data['url']
        r = data['r']
        w = data['w']
        h = data['h']
        webkey = data['webkey']
        cropped = None
        # 开始剪切
        if mode == 'poster':
            cropped = self.posterPicture(url, r, w, h)
        if mode == 'art':
            cropped = self.artPicture(url, r, w, h)
        return cropped

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
            print('匹配数据结果：%s' % scc)
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
