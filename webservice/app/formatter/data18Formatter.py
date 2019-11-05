from app.formatter.basicFormatter import BasicFormater
import re


class Data18Formatter(BasicFormater):

    def format(code):
        reg = r'(?i)vol[0-9]{1,3}'
        re.compile(reg)
        code = re.sub(reg, '', code)
        return code
