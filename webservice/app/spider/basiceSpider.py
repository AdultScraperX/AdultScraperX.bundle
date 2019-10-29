class BasicSpider:

    def getName(self):
        return self.__class__.__name__

    def search(self, q):
        raise RuntimeError('未实现接口')

    def analysisMediaHtmlByxpath(self, html, q):
        raise RuntimeError('未实现接口')
