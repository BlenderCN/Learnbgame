# vim:ts=4:et
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

quotables = ("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             + "abcdefghijklmnopqrstuvwxyz!#$%&*+-./:?@|~_^")

class PListError(Exception):
    def __init__(self, line, message):
        Exception.__init__(self, "%d: %s" % (line, message))
        self.line = line

class pldata:
    def __init__(self, src = ''):
        self.src = src
        self.pos = 0;
        self.end = len(self.src)
        self.line = 1
    def skip_space(self):
        while self.pos < self.end:
            c = self.src[self.pos]
            if not c.isspace():
                if c == '/' and self.pos < self.end - 1: #comments
                    if self.src[self.pos + 1] == '/':   # // coment
                        self.pos += 2
                        while self.pos < self.end:
                            c = self.src[self.pos]
                            if c == '\n':
                                break
                            self.pos += 1
                        if self.pos >= self.end:
                            raise PListError(self.line,
                                "Reached end of string in comment")
                    elif self.src[self.pos + 1] == '*': # /* comment */
                        start_line = self.line
                        self.pos += 2
                        while self.pos < self.end:
                            c = self.src[self.pos]
                            if c == '\n':
                                self.line += 1
                            elif (c == '*' and self.pos < self.end - 1
                                  and self.src[self.pos + 1] == '/'):
                                self.pos += 1
                                break
                            self.pos += 1
                        if self.pos >= self.end:
                            raise PListError(start_line,
                                "Reached end of string in comment")
                    else:
                        return True
                else:
                    return True
            if c == '\n':
                self.line += 1
            self.pos += 1
        raise PListError(self.line, "Reached end of string")
    def parse_quoted_string(self):
        start_line = self.line
        long_string = False
        escaped = 0
        shrink = 0
        hexa = False
        self.pos += 1
        start = self.pos
        if (self.pos < self.end - 1 and self.src[self.pos] == '"'
            and self.src[self.pos + 1] == '"'):
            self.pos += 2
            long_string = True
            start += 2
        while self.pos < self.end:
            c = self.src[self.pos]
            if escaped:
                if escaped == 1 and c == '0':
                    escaped += 1
                    hexa = False
                elif escaped > 1:
                    if escaped == 2 and c == 'x':
                        hexa = True
                        shring += 1
                        escaped += 1
                    elif hex and c.isxdigit():
                        shrink += 1
                        escaped += 1
                    elif c in range(0, 8):
                        shrink += 1
                        escaped += 1
                    else:
                        self.pos -= 1
                        escaped = 0
                else:
                    escaped = 0
            else:
                if c == '\\':
                    escaped = 1
                    shrink += 1
                elif (c == '"'
                      and (not long_string
                           or (self.pos < self.end - 2
                               and self.src[self.pos + 1] == '"'
                               and self.src[self.pos + 2] == '"'))):
                    break
            if c == '\n':
                self.line += 1
            self.pos += 1
        if self.pos >= self.end:
            raise PListError(start_line,
                "Reached end of string while parsing quoted string")
        if self.pos - start - shrink == 0:
            return ""
        s = self.src[start:self.pos]
        self.pos += 1
        if long_string:
            self.pos += 2
        return eval('"""' + s + '"""')
    def parse_unquoted_string(self):
        start = self.pos
        while self.pos < self.end:
            if self.src[self.pos] not in quotables:
                break
            self.pos += 1
        return self.src[start:self.pos]
    def parse_data(self):
        start_line = self.line
        self.pos += 1
        start = self.pos
        nibbles = 0
        while self.pos < self.end:
            if self.src[self.pos].isxdigit:
                nibbles += 1
                self.pos += 1
                continue
            if self.src[self.pos] == '>':
                if nibbles & 1:
                    raise PListError(self.line,
                        "Invalid data, missing nibble")
                s = self.src[start:self.pos]
                self.pos += 1
                return binascii.a2b_hex(s)
            raise PListError(self.line,
                "Invalid character in data")
        raise PListError(start_line,
            "Reached end of string while parsing data")
    def parse(self):
        self.skip_space()
        if self.src[self.pos] == '{':
            item = {}
            self.pos += 1
            while self.skip_space() and self.src[self.pos] != '}':
                key = self.parse()
                if type(key) != str:
                    raise PListError(self.line,
                        "Key is not a string")
                self.skip_space()
                if self.src[self.pos] != '=':
                    raise PListError(self.line,
                        "Unexpected character (expected '=')")
                self.pos += 1
                value = self.parse()
                if self.src[self.pos] == ';':
                    self.pos += 1
                elif self.src[self.pos] != '}':
                    raise PListError(self.line,
                        "Unexpected character (wanted ';' or '}')")
                item[key] = value
            if self.pos >= self.end:
                raise PListError(self.line,
                    "Unexpected end of string when parsing dictionary")
            self.pos += 1
            return item
        elif self.src[self.pos] == '(':
            item = []
            self.pos += 1
            while self.skip_space() and self.src[self.pos] != ')':
                value = self.parse()
                self.skip_space()
                if self.src[self.pos] == ',':
                    self.pos += 1
                elif self.src[self.pos] != ')':
                    raise PListError(self.line,
                        "Unexpected character (wanted ',' or ')')")
                item.append(value)
            self.pos += 1
            return item
        elif self.src[self.pos] == '<':
            return self.parse_data()
        elif self.src[self.pos] == '"':
            return self.parse_quoted_string()
        else:
            return self.parse_unquoted_string()
    def write_string(self, item):
        quote = False
        for i in item:
            if i not in quotables:
                quote = True
                break
        if quote:
            item = repr(item)
            # repr uses ', we want "
            item = '"' + item[1:-1].replace('"', '\\"') + '"'
        self.data.append(item)
    def write_item(self, item, level):
        if type(item) == dict:
            if not item:
                self.data.append("{ }")
                return
            self.data.append("{\n")
            for i in item.items():
                self.data.append('\t' * (level + 1))
                self.write_string(i[0])
                self.data.append(' = ')
                self.write_item(i[1], level + 1)
                self.data.append(';\n')
            self.data.append('\t' * (level))
            self.data.append("}")
        elif type(item) in(list, tuple):
            if not item:
                self.data.append("( )")
                return
            self.data.append("(\n")
            for n, i in enumerate(item):
                self.data.append('\t' * (level + 1))
                self.write_item(i, level + 1)
                if n < len(item) - 1:
                    self.data.append(',\n')
            self.data.append('\n')
            self.data.append('\t' * (level))
            self.data.append(")")
        elif type(item) == bytes:
            self.data.append('<')
            self.data.append(binascii.b2a_hex(item))
            self.data.append('>')
        elif type(item) == str:
            self.write_string(item)
        elif type(item) in [int, float]:
            self.write_string(str(item))
        else:
            raise PListError(0, "unsupported type")
    def write(self, item):
        self.data = []
        self.write_item(item, 0)
        return ''.join(self.data)
