from app.formatter.basicFormatter import BasicFormater


class CaribbeanFormatter(BasicFormater):

    def format(code):
        if code[-4] != "-":
            if code[-4] == " ":
                return code.replace(" ", "-")
        return code