# -*- coding: utf-8 -*-

from app.spider.censoredSpider import CensoredSpider


class Caribbean(CensoredSpider):

    def search(self, q):
        '''
        执行查询函数
        '''
        item = []

        '获取查询结果页html对象'
        url = 'https://cn.caribbeancom.com/moviepages/%s/index.html' % q
        html_item = self.basic.getHtmlByurl(url)
        if html_item['issuccess']:
            media_item = self.analysisMediaHtmlByxpath(
                html_item['html'], q)
            item.append({'issuccess': True, 'data': media_item})
        else:
            pass  # print repr(html_item['ex'])

        return item

    def analysisMediaHtmlByxpath(self, html, q):
        '''
        根据html对象与xpath解析数据
        html:<object>
        html_xpath_dict:<dict>
        return:<dict{issuccess,ex,dict}>
        '''
        media = {
            'm_id': '',
            'm_number': '',
            'm_title': '',
            'm_poster': '',
            'm_summary': '',
            'm_studio': '',
            'm_directors': '',
            'm_collections': '',
            'm_year': '',
            'm_originallyAvailableAt': '',
            'm_category': '',
            'm_actor': ''
        }

        number = self.tools.cleanstr(q.upper())
        media.update({'m_number': number})

        xpath_title = "//div[@class='video-detail']/h1/text()"
        title = html.xpath(xpath_title)
        if len(title) > 0:
            title = self.tools.cleantitlenumber(
                self.tools.cleanstr(title[0]), number)
            media.update({'m_title': title})

        xpath_summary = "//div[@class='movie-comment']/p/text()"
        summary = html.xpath(xpath_summary)
        if len(summary) > 0:
            summary = summary[0]
            media.update({'m_summary': summary})

        xpath_poster = "//div[@id='bigmovie']/div[@id='player_outer']/img/@src"
        poster = html.xpath(xpath_poster)
        if len(poster) > 0:
            poster = self.tools.cleanstr(poster[0])
            media.update({'m_poster': poster})

        # xpath_studio = "//div[@class='col-md-3 info']/p[5]/a/text()"
        # studio = html.xpath(xpath_studio)
        # if len(studio) > 0:
        studio = 'Caribbean'
        media.update({'m_studio': studio})

        # xpath_directors = "//div[@class='col-md-3 info']/p[4]/a/text()"
        # directors = html.xpath(xpath_directors)
        # if len(directors) > 0:
        directors = ''
        media.update({'m_directors': directors})

        # xpath_collections = "//div[@class='col-md-3 info']/p[6]/a/text()"
        # collections = html.xpath(xpath_collections)
        # if len(collections) > 0:
        collections = 'Caribbean'
        media.update({'m_collections': collections})

        xpath_year = "//div[@class='movie-info']/dl[3]/dd"
        year = html.xpath(xpath_year)
        if len(year) > 0:
            year = self.tools.cleanstr(year[0].text)
            media.update({'m_year': year})
            media.update({'m_originallyAvailableAt': year})

        xpath_category = "//dl[@class='movie-info-cat']/dd/a/text()"
        categorys = html.xpath(xpath_category)
        category_list = []
        for category in categorys:
            category_list.append(self.tools.cleanstr(category))
        categorys = ','.join(category_list)
        if len(categorys) > 0:
            media.update({'m_category': categorys})

        actor = {}
        xpath_actor_name = "//div[@class='movie-info']/dl[1]/dd/a/span/text()"
        # xpath_actor_url = "//div[@class='video-performer']/a/img/@style"
        actor_name = html.xpath(xpath_actor_name)
        # actor_url = html.xpath(xpath_actor_url)
        if len(actor_name) > 0:
            for i, actorname in enumerate(actor_name):
                # actorimageurl = actor_url[i].replace('background-image:url(', '').replace(');', '')
                '''
                actor.update({self.tools.cleanstr2(
                    actorname): actorimageurl})
                '''
                actor.update({self.tools.cleanstr2(
                    actorname): ''})

            media.update({'m_actor': actor})

        return media
