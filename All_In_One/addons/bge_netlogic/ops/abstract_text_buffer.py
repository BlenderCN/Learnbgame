class AbstractTextBuffer(object):
    def __init__(self):
        from io import StringIO
        self.buffer = StringIO()
        self._indent_level = 0
        self._indent = ""

    def set_indent_level(self, int_value):
        self._indent_level = int_value
        self._indent = " " * int(4 * int_value)
        pass

    def write(self, string, *args):
        if not args:
            self.buffer.write(string)
        else:
            self.buffer.write(string.format(*args))

    def write_line(self, string, *args):
        self.write(self._indent + string + "\n", *args)

    def close(self):
        self.buffer.close()
    pass