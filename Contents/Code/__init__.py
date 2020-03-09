# -*- coding: utf-8 -*-
import os
import shutil
import io
import fnmatch
import re
import base64
import json
import urllib
from datetime import datetime


PREFIX = '/video/libraryupdater'
NAME = 'AdultScraperX Beta1.2.0'
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
        'com.plexapp.agents.subzero',        
        'com.plexapp.agents.xbmcnfo'
    ]
    contributes_to = [
        'com.plexapp.agents.themoviedb',
        'com.plexapp.agents.imdb',
        'com.plexapp.agents.data18',
        'com.plexapp.agents.xbmcnfo'
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

                    Log('匹配数据结果：%s 【success】' % LocalFileName)
                else:
                    Log('匹配数据结果：%s 【无】' % LocalFileName)
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

            if media_item == 'm_title':
                metadata.original_title = data.get(media_item)

            if media_item == 'm_summary':

                if Prefs['Transum'] == '开启':
                    Log("简介翻译：开启")
                    HTTP.ClearCache()
                    HTTP.CacheTime = CACHE_1MONTH
                    tran_url = '%s:%s/t/%s/%s' % (Prefs['Service_IP'], Prefs['Service_Port'],
                                                  dirTagLine, base64.b64encode(data.get(media_item)).replace('/', ';<*'))
                    if not data.get(media_item) == '':
                        Log('翻译连接：%s', tran_url)
                        tran_summary = HTTP.Request(
                            tran_url, timeout=timeout).content
                        metadata.summary = tran_summary
                    else:
                        metadata.summary = data.get(media_item)
                else:
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
                    Log('上映日期：%s' % date_object)
                except Exception as ex:
                    Log('捕获异常：%s' % ex)

            if media_item == 'm_year':
                try:
                    metadata.year = int(data.get(media_item).split('-')[0])
                    Log('影片年份：%s' % data.get(media_item).split('-')[0])
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
                purl = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                         Prefs['Service_Port'], base64.b64encode(poster_data_json))
                Log('海报：%s' % purl)
                try:
                    poster = HTTP.Request(purl, timeout=timeout).content
                except Exception as ex:
                    Log('捕获异常：%s:%s' % (ex, purl))
                if not poster == None:
                    metadata.posters[purl] = Proxy.Media(poster)
                    ioposter = Proxy.Media(poster)

            if media_item == 'm_art_url':
                art_url = data.get(media_item)

                art_data = {
                    'mode': 'art',
                    'url': art_url,
                    'webkey': webkey.lower()
                }
                art_data_json = json.dumps(art_data)
                aurl = '%s:%s/img/%s' % (Prefs['Service_IP'],
                                        Prefs['Service_Port'], base64.b64encode(art_data_json))
                Log('背景：%s' % url)
                try:
                    art = HTTP.Request(aurl, timeout=timeout).content
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
                            Log('演员 %s 头像：%s' % (role.name, url))
                            role.photo = url

        # 设置影片级别
        metadata.content_rating = 'R18'
        if Prefs['BKNFO'] == '开启':
            self.createNFO(metadata, media, number, poster, purl, art, aurl)

        Log('更新媒体信息 ：【%s】 结束' % m_id)
        Log('======结束执行更新媒体信息======')

    def createNFO(self, metadata, media, number, poster, purl, art, aurl):
        Log('开始生成NFO文件，海报 , 演员图片')

        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        xml = xml + '<movie>\n'
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
                    actor = HTTP.Request(role.photo, timeout=timeout).content
                    with io.open(rolepath, 'wb') as f:
                        f.write(actor)
                        
                #xml = xml + '<thumb>%s</thumb>\n' % rolepath
                xml = xml + '<thumb>%s</thumb>\n' % role.photo
            except Exception as ex:
                Log('下载演员 %s 发生异常：%s' % (role.name, ex))
            xml = xml + '</actor>\n'

        # 海报
        filepath = newfilepath + '/' + filename+'-poster'+'.jpg'
        try:
            if not os.path.exists(filepath):
                with io.open(filepath, 'wb') as f:
                    f.write(poster)
            # xml = xml + '<thumb>%s</thumb>\n' % filepath
            xml = xml + '<thumb>%s</thumb>\n' % purl
        except Exception as ex:
            Log('下载 %s 海报发生异常：%s' % (number, ex))
        
        # 背景
        filepath = newfilepath + '/' + filename+'-fanart'+'.jpg'
        try:
            if not os.path.exists(filepath):
                with io.open(filepath, 'wb') as f:
                    f.write(art)
        except Exception as ex:
            Log('下载 %s 背景发生异常：%s' % (number, ex))

        xml = xml + '</movie>'

        # 保存 NFO
        nfofilepath = newfilepath+'/'+number+'.nfo'
        fo = io.open(nfofilepath, "w")
        fo.write(xml)
        fo.close()

        try:
            if not srcfilepath == newfilepath+'/'+filenameall:
                shutil.move(srcfilepath, newfilepath)                
                Log('文件 %s 移动至：%s' % (filenameall, newfilepath))
            else:
                Log('源文件： %s  与  新文件：%s  目录相同跳过移动文件' % (srcfilepath, newfilepath+'/'+filenameall))                
        except Exception as ex:
            Log('移动媒体文件 %s 时发生异常：%s' % (filenameall, ex))

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

    def searchFilesPath(self,filepath, fname):
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
                if fname in item:
                    # 如果在，将该文件路径加入结果reslut中
                    result.append(item_path+';')
        
        return result