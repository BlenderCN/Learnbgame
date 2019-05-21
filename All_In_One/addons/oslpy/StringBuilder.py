from io import StringIO


class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def Append(self, str):
        self._file_str.write(str)

    def WriteLine(self, str):
        self._file_str.write(str + "\n")

    def __str__(self):
        return self._file_str.getvalue()
