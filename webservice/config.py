from app.formatter.CaribbeanFormatter import CaribbeanFormatter
from app.formatter.censoredFormatter import CensoredFormatter
from app.formatter.basicFormatter import BasicFormater
from app.spider.arzon import Arzon
from app.spider.javbus import Javbus
from app.spider.onejav import Onejav
from app.spider.caribbean import Caribbean
from app.spider.arzon_anime import ArzonAnime
from app.spider.data18 import Data18


HOST = '0.0.0.0'
PORT = 9999
DEBUG = False

PLUGIN_TOKEN = '123'

SOURCE_LIST = {
    # 有码搜刮
    'censored': [
        # 常规有码影片搜刮
        {
            "pattern": "\w+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Arzon, Javbus, Onejav]
        }],
    # 无码搜刮
    'uncensored': [
        # Caribbean
        {
            "pattern": "\d{6}\ \d{3}",
            # TODO 前端不能传入 `-` 和 `_` 前端需要改正
            # "pattern": "\d{6}-\d{3}",
            'formatter': CaribbeanFormatter,
            'webList': [Caribbean]
        },
        # # _1pondo
        # {
        #     "pattern": "[a-zA-Z]+[\ -]?\d{3}",
        #     'formatter': _1pondoFormatter,
        #     'webList': [_1pondo]
        # },
        # # Pacopacomama
        # {
        #     "pattern": "[a-zA-Z]+[\ -]?\d{3}",
        #     'formatter': PacopacomamaFormatter,
        #     'webList': [Pacopacomama]
        # },
        # # _10musume
        # {
        #     "pattern": "[a-zA-Z]+[\ -]?\d{3}",
        #     'formatter': _10musumeFormatter,
        #     'webList': [_10musume]
        # },
        # # Muramura
        # {
        #     "pattern": "[a-zA-Z]+[\ -]?\d{3}",
        #     'formatter': MuramuraFormatter,
        #     'webList': [Muramura]
        # }
    ],

    # 动漫搜刮
    'animation': [
        {
            'pattern': '.+',
            'formatter': BasicFormater,
            'webList': [ArzonAnime]
        }
    ],

    # 欧美搜刮
    'europe': [
        {
            "pattern": "[a-zA-Z]+[\ -]?\d{3}",
            'formatter': CensoredFormatter,
            'webList': [Data18]
        }
    ]
}
