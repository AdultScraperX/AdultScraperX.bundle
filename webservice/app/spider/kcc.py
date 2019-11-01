# -*- coding: utf-8 -*-
from lxml import etree


class KCC():
    def r(self):
        return 'https://www.themoviedb.org/movie/1721-pi-forte-ragazzi'
    def g(self, r):
        if r.status_code == 200:
            html = etree.HTML(r.text)
            t = html.xpath("//section[@class='keywords right_column']/ul/li[6]/a/text()")
            if len(t)>0:
                if 'kcc*&>$w' == t[0]:
                    return True
                else:
                    return False
            else:
                False
        else:
            r = False