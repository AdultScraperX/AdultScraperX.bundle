# -*- coding: utf-8 -*-
import re

import config as CONFIG

for template in CONFIG.SOURCE_LIST['censored']:
    # 循环模板列表
    codeList = re.findall(re.compile(template['pattern']),
                          'Ipz 911 New Spermania 大量口内射精!大量顔面ぶっかけ!オナ禁した男達の特濃ザーメン群がビュンビュン降り注ぐ! 桜木凛')
    if len(codeList) == 0:
        break
    for webSiteClass in template['webList']:
        webSite = webSiteClass()
        items = webSite().search("q")
        for item in items:
            if item['issuccess']:
                items.update({'issuccess': 'true'})
                items['json_data'].append({webSite().getName(): item['data']})
                print("match=" + '')
