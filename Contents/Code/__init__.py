# -*- coding: utf-8 -*-
import os
import shutil
import io
import fnmatch
import re
import base64
import json
import urllib
import time
from datetime import datetime
from io import StringIO
from lxml import etree

element_from_string = XML.ElementFromString
load_file = Core.storage.load

PREFIX = '/video/AdultScraperX'
NAME = 'AdultScraperX Beta1.6.3'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PMS_URL = 'http://127.0.0.1:32400/library/sections/'

# HTTP
timeout = 3600


def Start():
    HTTP.CacheTime = 0


class AdultScraperXAgent(Agent.Movies):
    name = NAME
    languages = [Locale.Language.English]
    primary_provider = True
    accepts_from = [
        'com.plexapp.agents.localmedia',
        'com.plexapp.agents.opensubtitles',
        'com.plexapp.agents.podnapisi',
        'com.plexapp.agents.subzero'
    ]
    contributes_to = [
        'com.plexapp.agents.themoviedb',
        'com.plexapp.agents.imdb',
        'com.plexapp.agents.data18'
    ]

    def search(self, results, media, lang, manual):
        # 源文件路径
        msrcfilepath = os.path.join('/'.join(media.items[0].parts[0].file.split('/')[
                                    0:len(media.items[0].parts[0].file.split('/'))-1]))
        Log('源文件路径：%s' % msrcfilepath)
        nfopath = self.searchFilesPath(msrcfilepath, '.nfo')
        Log(nfopath)

        # 海报剪切微调
        '''
        :param r: 横向裁切位置
        :param w: 缩放比例:宽
        :param h: 缩放比例:高
        '''
        pcft = {}
        r = 0
        w = 0
        h = 0
        if len(re.findall('--pcft', media.name)) > 0:
            Log('海报微调模式：开启')
            tmps = media.name.split('--pcft')
            tmp = tmps[1].split(',')
            for index, rwh in enumerate(range(len(tmp))):
                res = re.findall(r'\d[0-9]{0,}', tmp[index].replace(' ',''))
                if len(res)>0:   
                    if index == 0:
                        r = res[0]
                    if index == 1:
                        w = res[0]
                    if index == 2:
                        h = res[0]
            media.name = tmps[0]
            pcft.update({'r':r,'w':w,'h':h})
            Log('\n横向裁切位置r: %s\n缩放比例:宽w: %s\n缩放比例:高h: %s\n参数0为默认执行' % (r, w, h))
        else:            
            Log('海报微调模式：关闭')
            pcft.update({'r':r,'w':w,'h':h})
            #Log('\n横向裁切位置r: %s\n缩放比例:宽w: %s\n缩放比例:高h: %s\n参数0为默认执行' % (r, w, h))


        if len(re.findall('--checkState', media.name)) > 0 or len(re.findall('--checkSpider', media.name)) > 0 or len(re.findall('--nore', media.name)) > 0:
            Log('命令模式：开启')
            #self.searchLocalMediaNFO(results, media, lang, manual, nfopath)
            self.searchOnlineMediaInfo(results, media, lang, manual,pcft)
        else:
            if len(nfopath) > 0:
                Log('查询模式：local')
                if not self.searchLocalMediaNFO(results, media, lang, manual, nfopath):
                    self.searchOnlineMediaInfo(results, media, lang, manual,pcft)
            else:
                Log('查询模式：Online')
                self.searchOnlineMediaInfo(results, media, lang, manual,pcft)

    def assrtDownSubTitle(self, number, path):
        # 射手
        assrt_domain = 'https://assrt.net'
        assrt_search_url = assrt_domain+'/sub/?searchword='+number
        assrt_down_url = assrt_domain+'/download/****/-/**/*.*'
        assrt_diteall_paths = ''
        c = 0
        try:
            # 搜索字幕
            HTTP.ClearCache()
            HTTP.CacheTime = CACHE_1MONTH
            assrt_result = HTTP.Request(
                assrt_search_url, timeout=timeout).content
            rep_html = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
            assrt_result = assrt_result.replace(rep_html, '')
            rep_html = '<html xmlns:wb="http://open.weibo.com/wb" lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
            assrt_result = assrt_result.replace(rep_html, '<html>')
            rep_html = r'<!--<base href="/search2/%E7%94%9F%E6%B4%BB%E5%A4%A7%E7%88%86%E7%82%B8/">-->'
            assrt_result = assrt_result.replace(rep_html, '')
            assrt_diteall_paths = etree.HTML(assrt_result).xpath(
                '//div[@class="sublist_box_title"]//a/@href')
        except Exception as ex:
            Log(ex)
            return c

        if len(assrt_diteall_paths) > 0:
            Log('在assrt匹配到字幕：%s' % number)
            try:
                assrt_id = assrt_diteall_paths[0].split(
                    '/')[len(assrt_diteall_paths[0].split('/'))-1].split('.')[0]
                Log('assrt 字幕id：%s' % assrt_id)
                HTTP.ClearCache()
                HTTP.CacheTime = CACHE_1MONTH
                assrt_result = HTTP.Request(
                    assrt_domain+assrt_diteall_paths[0], timeout=timeout).content
                rep_html = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
                assrt_result = assrt_result.replace(rep_html, '')
                rep_html = '<html xmlns:wb="http://open.weibo.com/wb" lang="zh-CN"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
                assrt_result = assrt_result.replace(rep_html, '<html>')
                rep_html = r'<!--<base href="/search2/%E7%94%9F%E6%B4%BB%E5%A4%A7%E7%88%86%E7%82%B8/">-->'
                assrt_result = assrt_result.replace(rep_html, '')
                assrt_file_paths = etree.HTML(assrt_result).xpath(
                    '//div[@class="waves-effect"]/@onclick')
                if len(assrt_file_paths) > 0:
                    art_download_count = 1
                    for files in assrt_file_paths:
                        try:
                            tmps = files.replace('onthefly(', '').replace(
                                '"', '').replace(')', '').split(',')
                            houzhui = tmps[2].split('.')[1]
                            if houzhui == 'ass' or houzhui == 'ssa' or houzhui == 'srt' or houzhui == 'sub' or houzhui == 'smi' or houzhui == 'idx' or houzhui == 'smi' or houzhui == 'psg':
                                assrt_down_url = assrt_down_url.replace(
                                    '****', tmps[0]).replace('**', tmps[1]).replace('*.*', tmps[2])
                                HTTP.ClearCache()
                                HTTP.CacheTime = CACHE_1MONTH
                                assrt_result = HTTP.Request(
                                    assrt_down_url, timeout=timeout).content

                                subtitle_path = os.path.join(
                                    path+'/'+number+'.'+tmps[2].split('.')[1])
                                if os.path.exists(subtitle_path):
                                    tmps = number+'.'+datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace(
                                        '-', '').replace(':', '').replace(' ', '')+'.'+tmps[2].split('.')[1]
                                    subtitle_path = os.path.join(path+'/'+tmps)
                                fo = io.open(subtitle_path, "w",
                                             encoding='utf-8')
                                fo.write(u''+assrt_result)
                                fo.close()
                                if os.path.getsize(subtitle_path) > 1:
                                    Log('字幕 %s 下载完成' % tmps[2].split('.')[0])
                                    c = c+1
                                    break
                                elif art_download_count == int(Prefs['Cycles']):
                                    Log('字幕 %s 下载失败' % tmps[2].split('.')[0])
                                    break
                                else:
                                    art_download_count = int(
                                        art_download_count+1)
                            else:
                                break
                        except Exception as ex:
                            Log(ex)
                            return c
            except Exception as ex:
                Log(ex)
                return c
            return c
        return c

    def searchLocalMediaNFO(self, results, media, lang, manual, nfopath):
        data = {
            "m_studio": "",
            "m_id": "",
            "m_actor": {},
            "m_directors": "",
            "m_summary": "",
            "m_collections": "",
            "m_number": "",
            "m_title": "",
            "m_category": "",
            "m_art_url": "",
            "m_originallyAvailableAt": "",
            "m_year": "",
            "m_poster": ""
        }
        nfo_file = nfopath[0]
        NFO_TEXT_REGEX_1 = re.compile(
            r'&(?![A-Za-z]+[0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)'
        )
        NFO_TEXT_REGEX_2 = re.compile(r'^\s*<.*/>[\r\n]+', flags=re.MULTILINE)
        RATING_REGEX_1 = re.compile(
            r'(?:Rated\s)?(?P<mpaa>[A-z0-9-+/.]+(?:\s[0-9]+[A-z]?)?)?'
        )
        RATING_REGEX_2 = re.compile(r'\s*\(.*?\)')

        nfo_text = load_file(nfo_file)

        nfo_text = NFO_TEXT_REGEX_1.sub('&amp;', nfo_text)

        nfo_text = NFO_TEXT_REGEX_2.sub('', nfo_text)

        nfo_text_lower = nfo_text.lower()
        if nfo_text_lower.count('<movie') > 0 and nfo_text_lower.count('</movie>') > 0:

            nfo_text = '{content}</movie>'.format(
                content=nfo_text.rsplit('</movie>', 1)[0]
            )

            # likely an xbmc nfo file
            try:
                nfo_xml = element_from_string(nfo_text).xpath('//movie')[0]
            except Exception as ex:
                Log(ex)
                return False

            # number
            try:
                data.update({'m_number': nfo_xml.xpath('number')[0].text})
            except Exception as ex:
                Log('NFO number : %s' % ex)
                return False

            # Title
            try:
                data.update({'m_title': nfo_xml.xpath('title')[0].text})
            except Exception as ex:
                Log('NFO Title : %s' % ex)
                return False

            # original_title
            try:
                data.update(
                    {'original_title': nfo_xml.xpath('originaltitle')[0].text})
            except Exception as ex:
                Log('NFO original_title : %s' % ex)
                return False

            # summary
            try:
                data.update({'m_summary': nfo_xml.xpath('outline')[0].text})
            except Exception as ex:
                Log('NFO summary : %s' % ex)
                return False

            # year
            try:
                data.update({'m_year': nfo_xml.xpath('year')[0].text})
            except Exception as ex:
                Log('NFO year : %s' % ex)
                return False

            # originallyAvailableAt
            try:
                data.update(
                    {'m_originallyAvailableAt': nfo_xml.xpath('premiered')[0].text})
            except Exception as ex:
                Log('NFO originallyAvailableAt : %s' % ex)
                return False

            # category
            try:
                categorys = []
                for citem in nfo_xml.xpath('genre'):
                    categorys.append(citem.text)
                if categorys[0] == None:
                    categorys = ''
                data.update({'m_category': ','.join(categorys)})
            except Exception as ex:
                Log('NFO category : %s' % ex)
                return False

            # director
            try:
                data.update({'m_directors': nfo_xml.xpath('director')[0].text})
            except Exception as ex:
                Log('director : %s' % ex)
                return False

            # collections
            try:
                collections = []
                for colitem in nfo_xml.xpath('collections'):
                    if isinstance(colitem, list):
                        collections.append(colitem[0].text)
                    else:
                        coltmp = colitem.text
                        collections.append(coltmp)
                if len(collections) < 1:
                    collections = ''
                data.update({'m_collections': collections})
            except Exception as ex:
                Log('NFO collections : %s' % ex)
                return False

            # poster
            try:
                data.update({'m_poster': nfo_xml.xpath('thumb')[0].text})
            except Exception as ex:
                Log('poster : %s' % ex)
                return False

            # actor
            actors = nfo_xml.xpath('actor')
            items = {}
            try:
                for actor in actors:
                    if len(actor.xpath('thumb')) > 0:
                        items.update(
                            {actor.xpath('name')[0].text: actor.xpath('thumb')[0].text})
                    else:
                        items.update(
                            {actor.xpath('name')[0].text: ''})
                data.update({'m_actor': items})
            except Exception as ex:
                Log('NFO actor : %s' % ex)
                return False

            # dirTagLine
            try:
                data.update(
                    {'dirtagline': nfo_xml.xpath('dirtagline')[0].text})
            except Exception as ex:
                Log('NFO dirTagLine : %s' % ex)
                return False
            data.update(
                {'r':0,'w':0,'h':0}
                )
            jsondata = json.dumps(data)

            Log('查询结果数据：%s' % jsondata)

            id = data['m_number']
            wk = 'NFO'
            name = '%s : %s' % (wk, data['m_title'])
            media_d = jsondata
            dirTagLine = data['dirtagline']

            id = base64.b64encode('%s|A|%s|%s|%s' % (
                id, wk, media_d, dirTagLine))
            score = 100
            new_result = dict(id=id, name=name,
                              year='', score=score, lang=lang)
            results.Append(MetadataSearchResult(**new_result))

            Log('匹配数据结果：%s 【success】' % data['m_number'])
            return True
        else:
            return False

    def searchOnlineMediaInfo(self, results, media, lang, manual,pcft):
        Log('======开始查询======')
        # 获取path
        dirTagLine = None
        filePath = media.items[0].parts[0].file
        mediaPath = String.Unquote(filePath, usePlus=False)
        Log('本地文件路径：%s' % filePath)
        mediaPathSplitItems = mediaPath.split('/')
        for item in mediaPathSplitItems:
            # 正则判断是否匹配 有结果就给出
            tmp = re.findall(Prefs['Dir_M'], item)
            if len(tmp) == 1:
                dirTagLine = 'censored'
                break
            tmp = re.findall(Prefs['Dir_NM'], item)
            if len(tmp) == 1:
                dirTagLine = 'uncensored'
                break
            tmp = re.findall(Prefs['Dir_A'], item)
            if len(tmp) == 1:
                dirTagLine = 'animation'
                break
            tmp = re.findall(Prefs['Dir_E'], item)
            if len(tmp) == 1:
                dirTagLine = 'europe'
                break
        Log("本地文件判别类型标记：%s" % dirTagLine)

        if dirTagLine != None:

            if manual:
                LocalFileName = media.name
                queryname = base64.b64encode(LocalFileName).replace('/', '[s]')
                Log('手动匹配Plex输出文件名：%s' % media.name)
                Log('格式化后文件名：%s' % LocalFileName)
                Log('base64后的关键字：%s' % queryname)

                Log('执行模式：手动')
                HTTP.ClearCache()
                HTTP.CacheTime = CACHE_1MONTH
                jsondata = HTTP.Request('%s:%s/manual/%s/%s/%s/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine,
                                                                         queryname, Prefs['Service_Token'], Prefs['User_DDNS'], Prefs['Plex_Port']), timeout=timeout).content

                dict_data_list = json.loads(jsondata)
                if dict_data_list['issuccess'] == 'true':
                    json_data_list = dict_data_list['json_data']
                    if Prefs['Orderby'] == '反序':
                        Log('结果输出排序方式：反序')
                    elif Prefs['Orderby'] == '默认':
                        Log('结果输出排序方式：默认')
                        json_data_list.reverse()

                    for json_data in json_data_list:
                        for data_list_key in json_data:
                            id = ''
                            name = ''
                            media_d = ''
                            wk = data_list_key
                            data = json_data.get(data_list_key)                            
                            data.update(pcft)# 微调海报参数
                            Log(pcft)
                            data.update(original_title='')
                            for item_key in data:
                                if item_key == 'm_number':
                                    id = data.get(item_key)
                                if item_key == 'm_title':
                                    data['original_title'] = data['m_title']
                                    poster_url = data['m_poster']
                                    poster_data = {
                                        'mode': 'poster',
                                        'url': poster_url,
                                        'webkey': wk.lower()
                                    }
                                    poster_data_json = json.dumps(poster_data)
                                    url = '%s:%s/img/%s/%s/%s/%s' % (
                                        Prefs['Service_IP'], Prefs['Service_Port'], base64.b64encode(poster_data_json),pcft['r'],pcft['w'],pcft['h'])

                                    thumb = url
                                    name = '%s: %s %s' % (
                                        wk, data['m_number'], data.get(item_key))
                            data_d = json.dumps(data)
                            id = base64.b64encode(
                                '%s|M|%s|%s|%s' % (id, wk, data_d, dirTagLine))
                            score = 100
                            new_result = dict(
                                id=id, name=name, year='', score=score, lang=lang, thumb=thumb)
                            results.Append(
                                MetadataSearchResult(**new_result))
                    Log('匹配数据结果：%s 【success】' % LocalFileName)
                else:
                    Log('匹配数据结果：%s 【无】' % LocalFileName)
            else:
                LocalFileName = self.getMediaLocalFileName(media)
                queryname = base64.b64encode(LocalFileName).replace('/', '[s]')
                Log('本地文件名：%s' % LocalFileName)
                Log('base64后的关键字：%s' % queryname)
                Log('模式：自动')
                HTTP.ClearCache()
                HTTP.CacheTime = CACHE_1MONTH
                jsondata = HTTP.Request('%s:%s/auto/%s/%s/%s/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine,
                                                                       queryname, Prefs['Service_Token'], Prefs['User_DDNS'], Prefs['Plex_Port']), timeout=timeout).content
                dict_data = json.loads(jsondata)

                Log('查询结果数据：%s' % jsondata)
                if dict_data['issuccess'] == 'true':
                    data_list = dict_data['json_data']
                    data_list.reverse()
                    for data in data_list:
                        id = ''
                        name = ''
                        media_d = ''
                        wk = data
                        for webkey in data:
                            media_dict = data.get(webkey)
                            wk = webkey
                            media_dict.update(original_title='')            
                            for item_key in media_dict:
                                if item_key == 'm_number':
                                    id = media_dict.get(item_key)
                                if item_key == 'm_title':
                                    media_dict['original_title'] = media_dict.get(
                                        item_key)
                                    name = media_dict.get(item_key)

                            media_dict.update(pcft)# 微调海报参数
                            media_d = json.dumps(media_dict)
                                                             
                        id = base64.b64encode('%s|A|%s|%s|%s' % (
                            id, wk, media_d, dirTagLine))
                        score = 100
                        new_result = dict(id=id, name=name,
                                          year='', score=score, lang=lang)
                        results.Append(MetadataSearchResult(**new_result))

                    Log('匹配数据结果：%s 【success】' % LocalFileName)
                else:
                    Log('匹配数据结果：%s 【无】' % LocalFileName)
        Log('======结束查询======')

    def update(self, metadata, media, lang):

        msrcfilepath = os.path.join('/'.join(media.items[0].parts[0].file.split('/')[
                                    0:len(media.items[0].parts[0].file.split('/'))-1]))
        Log('======开始执行更新媒体信息======')
        metadata_list = base64.b64decode(metadata.id).split('|')
        m_id = metadata_list[0]
        Log('解析base64传递数据-番号：%s' % m_id)
        manual = metadata_list[1]
        Log('解析base64传递数据-执行模式：%s' % manual)
        webkey = metadata_list[2]
        Log('解析base64传递数据-元数据站点：%s' % webkey)
        data = metadata_list[3]
        Log('解析base64传递数据-更新数据：%s' % data)
        data = json.loads(data)
        dirTagLine = metadata_list[4]
        Log('解析base64传递数据-文件类型判别标记：%s' % dirTagLine)
        
        # 微调参数
        try:            
            r = data['r']
        except Exception as ex:
            r = 0
        try:            
            w = data['w']
        except Exception as ex:
            w = 0
        try:            
            h = data['h']
        except Exception as ex:
            h = 0


        '在标语处显示来源元数据站点'
        metadata.tagline = webkey
        number = ''
        poster = None
        art = None
        for i, media_item in enumerate(data):
            if media_item == 'm_number':
                number = data.get(media_item)
                if dirTagLine == 'europe':
                    Log('标题模式：欧美')
                    metadata.title = data['m_title']
                else:
                    Log('标题模式：日本')
                    if number == '':
                        metadata.title = data['m_title']
                    else:
                        if webkey == 'ArzonAnime':
                            if Prefs['Title_jp_anime'] == '番号':
                                metadata.title = number
                            elif Prefs['Title_jp_anime'] == '标题':
                                if Prefs['Trantitle'] == '开启':
                                    Log("标题翻译：开启")
                                    HTTP.ClearCache()
                                    HTTP.CacheTime = CACHE_1MONTH
                                    tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, base64.b64encode(
                                        data['m_title']).replace('/', ';<*'))
                                    if not data['m_title'] == '':
                                        Log('翻译连接：%s', tran_url)
                                        tran_title = HTTP.Request(
                                            tran_url, timeout=timeout).content
                                        metadata.title = tran_title
                                    else:
                                        metadata.title = data['m_title']
                                else:
                                    metadata.title = data['m_title']

                            elif Prefs['Title_jp_anime'] == '番号,标题':
                                if Prefs['Trantitle'] == '开启':
                                    Log("标题翻译：开启")
                                    HTTP.ClearCache()
                                    HTTP.CacheTime = CACHE_1MONTH
                                    tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, base64.b64encode(
                                        data['m_title']).replace('/', ';<*'))
                                    if not data['m_title'] == '':
                                        Log('翻译连接：%s', tran_url)
                                        tran_title = HTTP.Request(
                                            tran_url, timeout=timeout).content
                                        metadata.title = '%s %s' % (
                                            number, tran_title)
                                    else:
                                        metadata.title = '%s %s' % (
                                            number, data['m_title'])
                                else:
                                    metadata.title = '%s %s' % (
                                        number, data['m_title'])
                        else:
                            if Prefs['Title_jp'] == '番号':
                                metadata.title = number
                            elif Prefs['Title_jp'] == '标题':
                                if Prefs['Trantitle'] == '开启':
                                    Log("标题翻译：开启")
                                    HTTP.ClearCache()
                                    HTTP.CacheTime = CACHE_1MONTH
                                    tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, base64.b64encode(
                                        data['m_title']).replace('/', ';<*'))
                                    if not data['m_title'] == '':
                                        Log('翻译连接：%s', tran_url)
                                        tran_title = HTTP.Request(
                                            tran_url, timeout=timeout).content
                                        metadata.title = tran_title
                                    else:
                                        metadata.title = data['m_title']
                                else:
                                    metadata.title = data['m_title']

                            elif Prefs['Title_jp'] == '番号,标题':
                                if Prefs['Trantitle'] == '开启':
                                    Log("标题翻译：开启")
                                    HTTP.ClearCache()
                                    HTTP.CacheTime = CACHE_1MONTH
                                    tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, base64.b64encode(
                                        data['m_title']).replace('/', ';<*'))
                                    if not data['m_title'] == '':
                                        Log('翻译连接：%s', tran_url)
                                        tran_title = HTTP.Request(
                                            tran_url, timeout=timeout).content
                                        metadata.title = '%s %s' % (
                                            number, tran_title)
                                    else:
                                        metadata.title = '%s %s' % (
                                            number, data['m_title'])
                                else:
                                    metadata.title = '%s %s' % (
                                        number, data['m_title'])

            if media_item == 'original_title':
                metadata.original_title = data.get(media_item)

            if media_item == 'm_summary':
                if Prefs['Transum'] == '开启':
                    if data.get(media_item) == '' or data.get(media_item) == None:
                        metadata.summary = data.get(media_item)
                    else:
                        Log("简介翻译：开启")
                        HTTP.ClearCache()
                        HTTP.CacheTime = CACHE_1MONTH
                        tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'],
                                                      dirTagLine, base64.b64encode(data.get(media_item)).replace('/', ';<*'))
                        Log('翻译连接：%s', tran_url)
                        tran_summary = HTTP.Request(
                            tran_url, timeout=timeout).content
                        metadata.summary = tran_summary
                else:
                    metadata.summary = data.get(media_item)

            if media_item == 'm_studio':
                metadata.studio = data.get(media_item)

            if media_item == 'm_collections':
                metadata.collections.clear()
                mediaPathSplitItems = msrcfilepath.split('/')
                tmp = ''
                for item in mediaPathSplitItems:
                    if len(re.findall(Prefs['Dir_C'], item)) > 0:
                        tmp = item
                if len(tmp) > 0:
                    tmp = tmp.replace(Prefs['Dir_C'], '')
                    Log('检测到合集标志并以 %s 作为合集名' % tmp)
                    metadata.collections.add(tmp)
                else:
                    if not data.get(media_item) == '':
                        if isinstance(data.get(media_item), list):
                            metadata.collections.add(data.get(media_item)[0])
                        else:
                            metadata.collections.add(
                                data.get(media_item).encode("UTF-8"))
                    else:
                        metadata.collections.add('')

            if media_item == 'm_originallyAvailableAt':
                try:
                    if not data.get(media_item) == '':
                        date_object = datetime.strptime(
                            data.get(media_item).replace('/', '-'), r'%Y-%m-%d')
                        metadata.originally_available_at = date_object
                        Log('上映日期：%s' % date_object)
                    else:
                        metadata.originally_available_at = datetime.strptime(
                            '1900-01-01', r'%Y-%m-%d')
                except Exception as ex:
                    Log('上映日期：捕获异常：%s', ex)

            if media_item == 'm_year':
                try:
                    metadata.year = int(
                        data.get(media_item).replace('/', '-').split('-')[0])
                    Log('影片年份：%s' % data.get(media_item).replace(
                        '/', '-').split('-')[0])
                except Exception as ex:
                    Log('影片年份：%s 捕获异常：%s' % (data.get(media_item), ex))

            if media_item == 'm_directors':
                metadata.directors.clear()
                metadata.directors.new().name = data.get(media_item)

            if media_item == 'm_category':
                metadata.genres.clear()
                genres_list = data.get(media_item).split(',')
                for genres_name in genres_list:
                    metadata.genres.add(genres_name)

            if media_item == 'm_poster':
                if webkey == 'NFO':
                    try:
                        posterpath = self.searchFilesPath(
                            msrcfilepath, '-poster.jpg')
                        if posterpath.count>0:
                            posterpath=posterpath[0]
                            metadata.posters[posterpath] = Proxy.Media(
                                load_file(posterpath))
                    except Exception as ex:
                        Log('NFO海报 : 捕获异常：%s:%s' % (ex, posterpath))
                else:
                    try:
                        poster_url = data.get(media_item)

                        poster_data = {
                            'mode': 'poster',
                            'url': poster_url,
                            'webkey': webkey.lower()
                        }
                        poster_data_json = json.dumps(poster_data)
                        purl = '%s:%s/img/%s/%s/%s/%s' % (Prefs['Service_IP'],
                                                Prefs['Service_Port'], base64.b64encode(poster_data_json),r,w,h)
                        Log('海报：%s' % purl)
                        poster = HTTP.Request(purl, timeout=timeout).content
                    except Exception as ex:
                        Log('海报捕获异常：%s:%s' % (ex, purl))
                    if not poster == None:
                        metadata.posters[purl] = Proxy.Media(poster)

            if media_item == 'm_art_url':
                if webkey == 'NFO':
                    try:
                        artpath = self.searchFilesPath(msrcfilepath, '-fanart.jpg')
                        if artpath.count>0:
                            artpath=artpath[0]
                            metadata.art[artpath] = Proxy.Media(
                                load_file(artpath))
                    except Exception as ex:
                        Log('NFO背景 ： 捕获异常：%s:%s' % (ex, artpath))
                else:
                    try:
                        art_url = data.get(media_item)

                        art_data = {
                            'mode': 'art',
                            'url': art_url,
                            'webkey': webkey.lower()
                        }
                        art_data_json = json.dumps(art_data)
                        aurl = '%s:%s/img/%s/%s/%s/%s' % (Prefs['Service_IP'],
                                                Prefs['Service_Port'], base64.b64encode(art_data_json),r,w,h)
                        Log('背景：%s' % aurl)
                        art = HTTP.Request(aurl, timeout=timeout).content
                    except Exception as ex:
                        Log('背景捕获异常：%s:%s' % (ex, aurl))
                    if not art == None:
                        metadata.art[aurl] = Proxy.Media(art)

            if media_item == 'm_actor':
                metadata.roles.clear()
                actors_list = data.get(media_item)
                if actors_list != '':
                    for key in actors_list:
                        role = metadata.roles.new()
                        role.name = key
                        imgurl = actors_list.get(key)
                        if imgurl != '':
                            art_data = {
                                'mode': 'actor',
                                'url': imgurl,
                                'webkey': webkey.lower()
                            }
                            art_data_json = json.dumps(art_data)

                            if webkey == 'NFO':
                                url = imgurl
                            else:
                                url = '%s:%s/img/%s/%s/%s/%s' % (Prefs['Service_IP'],
                                                        Prefs['Service_Port'], base64.b64encode(art_data_json),r,w,h)
                                Log('演员 %s 头像：%s' % (role.name, url))

                            role.photo = url
                        else:
                            role.photo = ''

        # 设置影片级别
        metadata.content_rating = 'R18'

        # 下载字幕
        if Prefs['SubtitleDown'] == '开启':
            dcount = self.assrtDownSubTitle(number, msrcfilepath)
            if dcount > 0:
                Log('匹配到字幕并下载完成 %s 个' % dcount)

        if not webkey == 'NFO':
            if Prefs['BKNFO'] == '开启':
                if not dirTagLine == 'europe':
                    self.createNFO(metadata, media, number, poster,
                                purl, art, aurl, dirTagLine)

        Log('更新媒体信息 ：【%s】 结束' % m_id)
        Log('======结束执行更新媒体信息======')

    def createNFO(self, metadata, media, number, poster, purl, art, aurl, dirtagline):
        Log('开始生成NFO文件，海报 , 演员图片')

        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        xml = xml + '<movie>\n'

        # dirtagline
        xml = xml + '<dirtagline>%s</dirtagline>\n' % dirtagline

        # number
        xml = xml + '<number>%s</number>\n' % number
        # 标题
        xml = xml + '<title>%s</title>\n' % metadata.title
        xml = xml + '<originaltitle>%s</originaltitle>\n' % metadata.original_title
        # 简介
        xml = xml + '<outline>%s</outline>\n' % metadata.summary
        # 标语
        xml = xml+'<tagline>%s</tagline>\n' % metadata.tagline
        # 影片年份
        xml = xml + '<year>%s</year>\n' % metadata.year
        # 上映日期
        xml = xml+'<premiered>%s</premiered>\n' % metadata.originally_available_at
        # 级别
        xml = xml+'<mpaa>R18</mpaa>\n'

        # 类型
        for genre in metadata.genres:
            xml = xml + '<genre>%s</genre>\n' % genre

        # 工作室
        '<studio>%s</studio>\n' % metadata.studio
        # 导演
        for director in metadata.directors:
            xml = xml + '<director>%s</director>\n' % director.name

        # 系列
        for collections in metadata.collections:
            if not collections == None or collections == '':
                xml = xml+'<collections>%s</collections>\n' % collections

        # 同名目录没有则创建
        # src文件名拆分
        filepathlist = media.items[0].parts[0].file.split('/')
        Log('src文件名拆分：%s' % filepathlist)

        # 文件名+后缀
        filenameall = filepathlist[len(filepathlist)-1]
        Log('文件名+后缀：%s' % filenameall)

        # 文件名
        filename = filenameall.split('.')[0]
        Log('文件名：%s' % filename)

        # 原文件全路径
        srcfilepath = os.path.join(media.items[0].parts[0].file)
        Log('原文件全路径： %s' % srcfilepath)

        # 新文件路径
        ftmp = srcfilepath.replace('/'+filenameall, '').replace('/'+number, '')
        newfilepath = ftmp+'/'+number
        Log('新文件路径：%s' % newfilepath)

        if not os.path.exists(newfilepath):
            try:
                os.makedirs(newfilepath)
                Log('创建 %s 目录：%s' % (number, newfilepath))
            except Exception as ex:
                Log('创建目录发生异常：%s \r\n %s ' % (newfilepath, ex))

        # 移动所有同名文件
        msrcfilepath = os.path.join('/'.join(media.items[0].parts[0].file.split('/')[
                                    0:len(media.items[0].parts[0].file.split('/'))-1]))
        Log(msrcfilepath)
        msrcfilepaths = self.searchFilesPath(msrcfilepath, number)
        Log(msrcfilepaths)
        for file_path in msrcfilepaths:
            try:
                if not os.path.exists(newfilepath+'/'+file_path.split('/')[len(file_path.split('/'))-1]):
                    shutil.move(file_path, newfilepath)
                    Log('文件 %s 移动至：%s' % (file_path, newfilepath+'/' +
                                          file_path.split('/')[len(file_path.split('/'))-1]))
                else:
                    Log('文件  %s  已存在' % (newfilepath+'/' +
                                         file_path.split('/')[len(file_path.split('/'))-1]))
            except Exception as ex:
                Log('移动媒体文件 %s 时发生异常：%s' % (newfilepath+'/' +
                                            file_path.split('/')[len(file_path.split('/'))-1], ex))

        # 演员
        actor_path = newfilepath+'/.actors'
        for role in metadata.roles:
            xml = xml + '<actor>\n'
            xml = xml + '<name>%s</name>\n' % role.name
            try:
                if not os.path.exists(actor_path):
                    os.makedirs(actor_path)
                    Log('创建 .actors 目录：%s' % actor_path)
            except Exception as ex:
                Log('创建目录发生异常：%s \r\n %s ' % (actor_path, ex))

            try:
                rolepath = os.path.join(
                    actor_path + '/'+role.name + '-actor.jpg')
                if not os.path.exists(rolepath):
                    if not role.photo == '':
                        actor_download_count = 1
                        for index in range(int(Prefs['Cycles'])):
                            Log('尝试头像 %s 第 %s/%s 次下载' %
                                (role.name, int(index+1), Prefs['Cycles']))
                            HTTP.ClearCache()
                            HTTP.CacheTime = CACHE_1MONTH
                            actor = HTTP.Request(
                                role.photo, timeout=timeout).content
                            with io.open(rolepath, 'wb') as f:
                                f.write(actor)
                            if os.path.getsize(rolepath) > 1:
                                Log('头像 %s 下载完成' % role.name)
                                break
                            elif actor_download_count == int(Prefs['Cycles']):
                                Log('头像 %s 下载失败' % role.name)
                            else:
                                actor_download_count = int(
                                    actor_download_count+1)
                xml = xml + '<thumb>%s</thumb>\n' % role.photo
            except Exception as ex:
                Log('下载演员 %s 发生异常：%s' % (role.name, ex))
            xml = xml + '</actor>\n'

        # 海报
        filepath = newfilepath + '/' + filename+'-poster'+'.jpg'
        try:
            if not os.path.exists(filepath):
                poster_download_count = 1
                for index in range(int(Prefs['Cycles'])):
                    Log('尝试海报 %s 第 %s/%s 次下载' %
                        (number, int(index+1), Prefs['Cycles']))
                    HTTP.ClearCache()
                    HTTP.CacheTime = CACHE_1MONTH
                    poster = HTTP.Request(
                        purl, timeout=timeout).content
                    with io.open(filepath, 'wb') as f:
                        f.write(poster)
                    if os.path.getsize(filepath) > 1:
                        Log('海报 %s 下载完成' % number)
                        break
                    elif poster_download_count == int(Prefs['Cycles']):
                        Log('海报 %s 下载失败' % number)
                    else:
                        poster_download_count = int(poster_download_count+1)
            xml = xml + '<thumb>%s</thumb>\n' % purl
        except Exception as ex:
            Log('下载 %s 海报发生异常：%s' % (number, ex))

        # 背景
        filepath = newfilepath + '/' + filename+'-fanart'+'.jpg'
        try:
            if not os.path.exists(filepath):
                art_download_count = 1
                for index in range(int(Prefs['Cycles'])):
                    Log('尝试背景 %s 第 %s/%s 次下载' %
                        (number, int(index+1), Prefs['Cycles']))
                    HTTP.ClearCache()
                    HTTP.CacheTime = CACHE_1MONTH
                    art = HTTP.Request(
                        aurl, timeout=timeout).content
                    with io.open(filepath, 'wb') as f:
                        f.write(art)
                    if os.path.getsize(filepath) > 1:
                        Log('背景 %s 下载完成' % number)
                        break
                    elif art_download_count == int(Prefs['Cycles']):
                        Log('背景 %s 下载失败' % number)
                    else:
                        art_download_count = int(art_download_count+1)

        except Exception as ex:
            Log('下载 %s 背景发生异常：%s' % (number, ex))

        xml = xml + '</movie>'

        # 保存 NFO
        nfofilepath = newfilepath+'/'+number+'.nfo'
        fo = io.open(nfofilepath, "w")
        fo.write(xml)
        fo.close()

    def getMediaLocalPath(self, media):
        '''
        获取本地媒体路径
        '''
        mediafilepath = ''
        mediafilepathlist = media.items[0].parts[0].file.split('/')
        medianame = ''
        extensionname = ''

        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                medianame = mediafilepathlist[i].split('.')[0]
                extensionname = mediafilepathlist[i].split('.')[1]

        file = medianame + '.' + extensionname
        mediafilepath = media.filename.replace(file, '')

        return mediafilepath

    def getMediaLocalFileName(self, media):
        '''
        获得本地媒体文件名
        '''
        tmp = []
        relist = []
        mediafilepathlist = media.items[0].parts[0].file.split('/')
        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                medianamelist = mediafilepathlist[i].split('.')
                for j in range(len(medianamelist)):
                    if j < (len(medianamelist)-1):
                        tmp.append(medianamelist[j])
        medianame = ' '.join(tmp)
        return medianame

    def getMediaLocalFileExtensionName(self, media):
        '''
        获得本地媒体后缀名
        '''
        extensionname = ''
        mediafilepathlist = media.items[0].parts[0].file.split('/')
        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                extensionname = mediafilepathlist[i].split('0')[1]

        return extensionname

    def searchFilesPath(self, filepath, fname):
        result = []
        # 遍历当前文件夹下面的所有文件
        for item in os.listdir(filepath):
            # 遍历时，拼接好当前文件的路径
            item_path = os.path.join(filepath, item)

            # 如果当前文件类型为文件夹
            if os.path.isdir(item_path):
                # 调用自身search递归查找
                self.searchFilesPath(item_path, fname)

            # 如果当前文件为文件
            elif os.path.isfile(item_path):
                # 判断fname是否在item中
                if fname.lower() in item.lower():
                    # 如果在，将该文件路径加入结果reslut中
                    result.append(item_path+'')

        return result
