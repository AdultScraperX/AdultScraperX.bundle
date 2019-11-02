from app.formatter.basicFormatter import BasicFormater

class CensoredFormatter(BasicFormater):

    def format(code):
        if code[-4] != "-":
            if code[-4] == " ":
                return code.replace(" ", "-")
            else:
                listCoed = list(code)
                listCoed.insert(len(code) - 3, "-")
                return "".join(listCoed)
        return code.replace(' ').replace('-')
