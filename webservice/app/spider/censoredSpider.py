from app.internel.config import ConfigManager
from app.internel.tools import Tools
from app.spider.basic import Basic
from app.spider.basiceSpider import BasicSpider


class CensoredSpider(BasicSpider):

    def __init__(self):
        self.basic = Basic()
        self.tools = Tools()
        self.configmanager = ConfigManager()
