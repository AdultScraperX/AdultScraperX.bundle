# -*- coding: utf-8 -*-

import base64
import json
import re
from datetime import datetime

PREFIX = '/video/libraryupdater'
NAME = 'AdultScraperSE v2.2.0'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PMS_URL = 'http://127.0.0.1:32400/library/sections/'


def Start():
    HTTP.CacheTime = 0
    # fpath = '/volume1/@appstore/Plex Media Server/Resources/'
    # fname = 'chunk-2-'
    # # 路径（鼠标右键查看文件属性）
    # path = '/volume1/@appstore/"Plex Media Server"/Resources'
    # files = os.listdir(path)
    # # 查找文件名字含有fish且以.png后缀的文件
    # for f in files:
    #     if fname in f and f.endswith('.js'):
    #         Log('Found it!' + f)


@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():
    oc = ObjectContainer(no_cache=True)
    all_keys = []
    try:
        sections = XML.ElementFromURL(PMS_URL).xpath('//Directory')
        for section in sections:
            key = section.get('key')
            title = section.get('title')
            oc.add(DirectoryObject(key=Callback(
                UpdateType, title=title, key=[key]), title='' + title + ''))
            all_keys.append(key)
    except:
        pass
    if len(all_keys) > 0:
        oc.add(DirectoryObject(key=Callback(
            UpdateType, title=u'' + unicode('所有部分', "utf-8"), key=all_keys),
            title=u'' + unicode('更新所有部分,请返回到片库查看!', "utf-8")))
    oc.add(PrefsObject(title=u'' + unicode('设置', "utf-8"), thumb=R('icon-prefs.png')))
    return oc


@route(PREFIX + '/type', key=int)
def UpdateType(title, key):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(
        UpdateSection, title=title, key=key), title=u'' + unicode('扫描', "utf-8")))
    oc.add(DirectoryObject(key=Callback(UpdateSection, title=title,
                                        key=key, analyze=True), title=u'' + unicode('分析媒体', "utf-8")))
    oc.add(DirectoryObject(key=Callback(UpdateSection, title=title,
                                        key=key, force=True), title=u'' + unicode('强制元数据刷新', "utf-8")))
    return oc


@route(PREFIX + '/section', key=int, force=bool, analyze=bool)
def UpdateSection(title, key, force=False, analyze=False):
    for section in key:
        if analyze:
            url = PMS_URL + section + '/analyze'
            method = "PUT"
        else:
            method = "GET"
            url = PMS_URL + section + '/refresh'
            if force:
                url += '?force=1'
        Thread.Create(Update, url=url, method=method)
    if title == 'All sections':
        return ObjectContainer(header=title, message='所有部分都将更新,请返回到片库查看!')
    elif len(key) > 1:
        return ObjectContainer(header=title, message='所有选定的部分都将更新,请返回到片库查看!')
    else:
        return ObjectContainer(header=title, message='部分 "' + title + '" 将会被更新,请返回到片库查看!')


@route(PREFIX + '/update')
def Update(url, method):
    update = HTTP.Request(url, cacheTime=0, method=method).content
    return


class AdultScraperSEAgent(Agent.Movies):
    name = NAME
    languages = [Locale.Language.English, Locale.Language.Japanese]
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

        # 获取path
        dirTagLine = None
        mediaPath = String.Unquote(media.filename, usePlus=False)
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
        Log("dirTagLine======" + dirTagLine)
        if dirTagLine != None:

            timeout = 300
            queryname = base64.b64encode(media.name).replace('/', '[s]')
            Log("filename========" + media.name)
            Log("queryname========" + queryname)

            if manual:
                HTTP.ClearCache()
                HTTP.CacheTime = CACHE_1MONTH
                jsondata = HTTP.Request(
                    '%s:%s/manual/%s/%s/%s' % (
                        Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, queryname, Prefs['Service_Token']),
                    timeout=timeout).content
                base64jsondata = base64.b64decode(jsondata)
                Log(base64jsondata)
                dict_data_list = json.loads(base64jsondata)
                if dict_data_list['issuccess'] == 'true':
                    json_data_list = dict_data_list['json_data']

                    if Prefs['Orderby'] == '默认':
                        pass
                    elif Prefs['Orderby'] == '反序':
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
                                    r = Prefs['Poster_Cutting_X']
                                    w = Prefs['Poster_Cutting_W']
                                    h = Prefs['Poster_Cutting_H']
                                    poster_data = {
                                        'mode': 'poster',
                                        'url': poster_url,
                                        'r': r,
                                        'w': w,
                                        'h': h,
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
                                '%s|M|%s|%s' % (id, wk, data_d))
                            score = 100
                            new_result = dict(
                                id=id, name=name, year='', score=score, lang=lang, thumb=thumb)
                            results.Append(
                                MetadataSearchResult(**new_result))
            else:
                HTTP.ClearCache()
                HTTP.CacheTime = CACHE_1MONTH
                jsondata = HTTP.Request(
                    '%s:%s/auto/%s/%s/%s' % (
                        Prefs['Service_IP'], Prefs['Service_Port'], dirTagLine, queryname, Prefs['Service_Token']),
                    timeout=timeout).content
                dict_data = json.loads(jsondata)
                if dict_data['issuccess'] == 'true':
                    data_list = dict_data['json_data']
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
                        id = base64.b64encode('%s|A|%s|%s' % (id, wk, media_d))
                        score = 100
                        new_result = dict(
                            id=id, name=name, year='', score=score, lang=lang)
                        results.Append(
                            MetadataSearchResult(**new_result))

    def update(self, metadata, media, lang):

        dirTagLine = None
        mediaPath = String.Unquote(media.filename, usePlus=False)
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
        Log("dirTagLine======" + dirTagLine)
        if dirTagLine != None:

            timeout = 300
            metadata_list = base64.b64decode(metadata.id).split('|')
            m_id = metadata_list[0]
            manual = metadata_list[1]
            webkey = metadata_list[2]
            data = metadata_list[3]
            data = json.loads(data)

            '在标语处显示来源元数据站点'
            metadata.tagline = webkey

            for i, media_item in enumerate(data):
                if media_item == 'm_number':
                    number = data.get(media_item)
                    if dirTagLine == Prefs['Dir_E']:
                        '欧美标题'
                        metadata.title = data['m_title']
                    else:
                        '日本标题'
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
                        Log(ex)

                if media_item == 'm_year':
                    try:
                        metadata.year = metadata.originally_available_at.year
                    except Exception as ex:
                        Log(ex)

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
                    r = Prefs['Poster_Cutting_X']
                    w = Prefs['Poster_Cutting_W']
                    h = Prefs['Poster_Cutting_H']

                    poster_data = {
                        'mode': 'poster',
                        'url': poster_url,
                        'r': r,
                        'w': w,
                        'h': h,
                        'webkey': webkey.lower()
                    }
                    poster_data_json = json.dumps(poster_data)
                    url = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                            Prefs['Service_Port'], base64.b64encode(poster_data_json))
                    poster = None
                    try:
                        poster = HTTP.Request(url, timeout=timeout).content
                    except Exception as ex:
                        Log('%s:%s' % (ex, url))
                    if not poster == None:
                        metadata.posters[url] = Proxy.Media(poster)

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
                                    'mode': 'art',
                                    'url': imgurl,
                                    'r': 0,
                                    'w': 125,
                                    'h': 125,
                                    'webkey': webkey.lower()
                                }
                                art_data_json = json.dumps(art_data)
                                url = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                                        Prefs['Service_Port'], base64.b64encode(art_data_json))
                                Log('art-url:%s' % url)
                                role.photo = url

    def querynameVoleClean(self, st):
        st = st.lower().split('-')
        name = []
        for s in st:
            if s.find('vol') >= 0:
                if not s[3].isdigit():
                    name.append(s)
            else:
                name.append(s)
        ss = '-'.join(name)
        return ss

    def getMediaLocalPath(self, media):
        '''
        获取本地媒体路径
        '''
        mediafilepath = ''
        mediafilepathlist = media.filename.split('%2F')
        medianame = ''
        extensionname = ''

        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                medianame = mediafilepathlist[i].split('%2E')[0]
                extensionname = mediafilepathlist[i].split('%2E')[1]

        file = medianame + '%2E' + extensionname
        mediafilepath = media.filename.replace(file, '')

        return mediafilepath

    def getMediaLocalFileName(self, media):
        '''
        获得本地媒体文件名
        '''
        medianame = ''
        mediafilepathlist = media.filename.split('%2F')
        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                medianame = mediafilepathlist[i].split('%2E')[0]

        return medianame

    def getMediaLocalFileExtensionName(self, media):
        '''
        获得本地媒体后缀名
        '''
        extensionname = ''
        mediafilepathlist = media.filename.split('%2F')
        for i in range(len(mediafilepathlist)):
            if i == (len(mediafilepathlist) - 1):
                extensionname = mediafilepathlist[i].split('%2E')[1]

        return extensionname

    def rex(self, re_str, st):
        # Log(re_str)
        upper_lower_count = 0
        number_dict = []
        re_items = re.findall(re_str, st)
        if re_items != None:
            for re_item in re_items:
                if re_item.isupper():
                    upper_lower_count + 1
                    number_dict.append(re_item)
                if re_item.islower():
                    upper_lower_count + 1
                    number_dict.append(re_item)
        # Log(number_dict[0])
        return number_dict[0]
