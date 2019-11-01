# -*- coding: utf-8 -*-

from app.spider.censoredSpider import CensoredSpider


class Arzon(CensoredSpider):

    def search(self, q):
        '''
        执行查询函数
        '''
        item = []

        '确认站点'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'utf-8',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        wsc_url = 'https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F'
        wsc_item = self.basic.webSiteConfirmByurl(wsc_url, headers)

        '获取查询结果列表页html对象'
        if wsc_item['issuccess']:
            url = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=%s' % q
            list_html_item = self.basic.getHtmlByurl(url)
            if list_html_item['issuccess']:

                '检测是否是为查询到结果'
                xpath_404 = "//div[@id='list']/img/@src"
                if len(list_html_item['html'].xpath(xpath_404)) > 0:
                    return item

                '获取html对象'
                xpaths = "//div[@class='pictlist']/dl[@class='hentry']/dd[@class='entry-title']/h2/a/@href"
                page_url_list = self.basic.getitemspage(
                    list_html_item['html'], xpaths)
                for page_url in page_url_list:
                    if page_url != '':
                        page_url = 'https://www.arzon.jp%s' % page_url
                        html_item = self.basic.getHtmlByurl(page_url)
                        '解析html对象'
                        media_item = self.analysisMediaHtmlByxpath(
                            html_item['html'],q)
                        item.append({'issuccess': True, 'data': media_item})

            else:
                print (list_html_item['ex'])
        else:
            print (wsc_item['ex'])

        return item

    def analysisMediaHtmlByxpath(self, html,q):
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

        '''
        xpath_number = "//div[@class='item_register']//table[@class='item']//tr[8]/td[2]/text()"
        number = html.xpath(xpath_number)
        if len(number) > 0:
            number = self.tools.cleanstr(number[0])
            media.update({'m_number': number})
        '''
        number = self.tools.cleanstr(q.upper())
        media.update({'m_number': number})

        xpath_title = "//div[@class='detail_title_new2']/table/tr/td[2]/h1"
        title = html.xpath(xpath_title)
        if len(title) > 0:
            title = self.tools.cleanstr(title[0].text)
            media.update({'m_title': title})

        xpath_poster = "//table[@class='item_detail']//tr[1]//td[1]//a//img[@class='item_img']/@src"
        poster = html.xpath(xpath_poster)
        if len(poster) > 0:
            poster = self.tools.cleanstr(poster[0])
            media.update({'m_poster': 'https:%s' % poster})

        xpath_summary = "//table[@class='item_detail']//tr[2]//td[@class='text']//div[@class='item_text']/text()"
        summary = html.xpath(xpath_summary)
        if len(summary) > 0:
            summary = self.tools.cleanstr(summary[1])
            media.update({'m_summary': summary})

        xpath_studio = "//div[@class='item_register']/table[@class='item']//tr[2]/td[2]/a"
        studio = html.xpath(xpath_studio)
        if len(studio) > 0:
            studio = self.tools.cleanstr(studio[0].text)
            media.update({'m_studio': studio})

        xpath_directors = "//table[@class='item']//tr[5]//td[2]/a"
        directors = html.xpath(xpath_directors)
        if len(directors) > 0:
            directors = self.tools.cleanstr(directors[0].text)
            media.update({'m_directors': directors})

        xpath_collections = "//table[@class='item']//tr[4]//td[2]//a"
        collections = html.xpath(xpath_collections)
        if collections[0].text != None:
            collections = self.tools.cleanstr(collections[0].text)
            media.update({'m_collections': collections})

        xpath_year = "//table[@class='item']//tr[6]/td[2]/text()"
        year = html.xpath(xpath_year)
        if len(year) > 0:
            year = self.tools.cleanstr(year[0])
            media.update({'m_year': self.tools.formatdatetime(year)})

        xpath_originallyAvailableAt = "//table[@class='item']//tr[6]/td[2]/text()"
        originallyAvailableAt = html.xpath(xpath_originallyAvailableAt)
        if len(originallyAvailableAt) > 0:
            originallyAvailableAt = self.tools.cleanstr(
                originallyAvailableAt[0])
            media.update(
                {'m_originallyAvailableAt': self.tools.formatdatetime(originallyAvailableAt)})

        xpath_category = "//div[@id='adultgenre2']//table//tr/td[2]//ul//li/a"
        categorys = html.xpath(xpath_category)
        category_list = []
        for category in categorys:
            category_list.append(self.tools.cleanstr(category.text))
        categorys = ','.join(category_list)
        if len(categorys) > 0:
            media.update({'m_category': categorys})

        actor = {}
        xpath_actor_name = "//div[@class='item_register']//table[@class='item']//tr[1]/td[2]//a"
        xpath_actor_url = "//div[@class='item_register']//table[@class='item']//tr[1]/td[2]/a/@href"

        actor_name = html.xpath(xpath_actor_name)
        actor_url = html.xpath(xpath_actor_url)

        if len(actor_name) > 0:
            for i, actorname in enumerate(actor_name):
                html = self.basic.getHtmlByurl(
                    'https://www.arzon.jp%s' % actor_url[i])
                if html['issuccess']:
                    xpath_actor_image = "//table[@class='p_list1']//img/@src"
                    actorimageurl = html['html'].xpath(xpath_actor_image)

                actor.update({actorname.text: 'https:%s' % actorimageurl[0]})

            media.update({'m_actor': actor})

        return media
