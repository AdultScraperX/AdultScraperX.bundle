# -*- coding: utf-8 -*-
import os
import io
import fnmatch
import re
import base64
import json
from datetime import datetime

PREFIX = '/video/libraryupdater'
NAME = 'AdultScraperX Bate1.0.0'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PMS_URL = 'http://127.0.0.1:32400/library/sections/'


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

            timeout = 300

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
                            for item_key in data:
                                if item_key == 'm_number':
                                    id = data.get(item_key)
                                if item_key == 'm_title':
                                    poster_url = data['m_poster']
                                    poster_data = {
                                        'mode': 'poster',
                                        'url': poster_url,
                                        'webkey': wk.lower()
                                    }
                                    poster_data_json = json.dumps(poster_data)
                                    url = '%s:%s/img/%s' % (
                                        Prefs['Service_IP'], Prefs['Service_Port'], base64.b64encode(poster_data_json))

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
                    Log('匹配数据结果：success')
                else:
                    Log('匹配数据结果：无')
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
                            for item_key in media_dict:
                                if item_key == 'm_number':
                                    id = media_dict.get(item_key)
                                if item_key == 'm_title':
                                    name = media_dict.get(item_key)

                            media_d = json.dumps(media_dict)
                        id = base64.b64encode('%s|A|%s|%s|%s' % (
                            id, wk, media_d, dirTagLine))
                        score = 100
                        new_result = dict(id=id, name=name,
                                          year='', score=score, lang=lang)
                        results.Append(MetadataSearchResult(**new_result))
                        Log('匹配数据结果：success')
                    else:
                        Log('匹配数据结果：无')
        Log('======结束查询======')

    def update(self, metadata, media, lang):
        Log('======开始执行更新媒体信息======')
        timeout = 300
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

        '在标语处显示来源元数据站点'
        metadata.tagline = webkey
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
                                metadata.title = data['m_title']
                            elif Prefs['Title_jp_anime'] == '番号,标题':
                                metadata.title = '%s %s' % (
                                    number, data['m_title'])
                        else:
                            if Prefs['Title_jp'] == '番号':
                                metadata.title = number
                            elif Prefs['Title_jp'] == '标题':
                                metadata.title = data['m_title']
                            elif Prefs['Title_jp'] == '番号,标题':
                                metadata.title = '%s %s' % (
                                    number, data['m_title'])

            if media_item == 'm_title':
                metadata.original_title = data.get(media_item)

            if media_item == 'm_summary':
                metadata.summary = data.get(media_item)

            if media_item == 'm_studio':
                metadata.studio = data.get(media_item)

            if media_item == 'm_collections':
                metadata.collections.add(data.get(media_item))

            if media_item == 'm_originallyAvailableAt':
                try:
                    date_object = datetime.strptime(
                        data.get(media_item), r'%Y-%m-%d')
                    metadata.originally_available_at = date_object
                except Exception as ex:
                    Log('捕获异常：%s' % ex)

            if media_item == 'm_year':
                try:
                    metadata.year = metadata.originally_available_at.year
                except Exception as ex:
                    Log('捕获异常：%s' % ex)

            if media_item == 'm_directors':
                metadata.directors.clear()
                metadata.directors.new().name = data.get(media_item)

            if media_item == 'm_category':
                metadata.genres.clear()
                genres_list = data.get(media_item).split(',')
                for genres_name in genres_list:
                    metadata.genres.add(genres_name)

            if media_item == 'm_poster':
                poster_url = data.get(media_item)

                poster_data = {
                    'mode': 'poster',
                    'url': poster_url,
                    'webkey': webkey.lower()
                }
                poster_data_json = json.dumps(poster_data)
                url = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                        Prefs['Service_Port'], base64.b64encode(poster_data_json))
                Log('海报：%s' % url)
                poster = None
                try:
                    poster = HTTP.Request(url, timeout=timeout).content
                except Exception as ex:
                    Log('捕获异常：%s:%s' % (ex, url))
                if not poster == None:
                    metadata.posters[url] = Proxy.Media(poster)

            if media_item == 'm_art_url':
                art_url = data.get(media_item)

                art_data = {
                    'mode': 'art',
                    'url': art_url,
                    'webkey': webkey.lower()
                }
                art_data_json = json.dumps(art_data)
                url = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                        Prefs['Service_Port'], base64.b64encode(art_data_json))
                Log('背景：%s' % url)
                art = None
                try:
                    art = HTTP.Request(url, timeout=timeout).content
                except Exception as ex:
                    Log('捕获异常：%s:%s' % (ex, url))
                if not art == None:
                    metadata.art[url] = Proxy.Media(art)

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
                            url = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                                    Prefs['Service_Port'], base64.b64encode(art_data_json))
                            Log('演员头像：%s' % url)
                            role.photo = url

        #s设置影片级别
        metadata.content_rating = 'R18'
        Log('======结束执行更新媒体信息======')

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
