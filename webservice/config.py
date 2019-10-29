from app.formatter.censoredFormatter import CensoredFormatter
from app.spider.arzon import Arzon
from app.spider.javbus import Javbus
from app.spider.onejav import Onejav

HOST = '0.0.0.0'
PORT = 9999
DEBUG = False

PLUGIN_TOKEN = '123'
PATTERN_LIST = ["[a-zA-Z]+[\ -]?\d{3}", "\w+[\ -]?\d{3}"]

SOURCE_LIST = {
    # 无码搜刮
    'censored': [
        # 常规有码影片搜刮
        {
            "pattern": "[a-zA-Z]+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Arzon, Javbus, Onejav]
        }],
    # 有码搜刮
    'uncensored': [

        {
            "pattern": "[a-zA-Z]+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Arzon, Javbus, Onejav]
        }
    ],

    # 动漫搜刮
    'animation': [

        {
            "pattern": "[a-zA-Z]+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Arzon, Javbus, Onejav]
        }
    ],

    # 欧美搜刮
    'europe': [
        {
            "pattern": "[a-zA-Z]+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Arzon, Javbus, Onejav]
        }
    ]
}
