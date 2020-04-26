from struct import unpack

class BinaryReader:

    def __init__(self, buffer):
        self.__buffer = buffer
        self.length = len(buffer)
        self.pos = 0

    def read(self, num=None):
        if self.pos < 0 or self.pos >= self.length:
            raise IndexError("Read position out of bounds!")
        if num is None:
            ret = self.__buffer[self.pos:]
            self.pos = self.length
            return ret
        else:
            if num < 0:
                raise IndexError("Amount to read has to be positive!")
            if self.pos + num > self.length:
                raise IndexError("Can't read that many bytes!")
            ret = self.__buffer[self.pos:self.pos+num]
            self.pos += num
            return ret

    def read_char(self, num=None):
        if num is None:
            return unpack('c', self.read(1))[0].decode('iso-8859-1')
        else:
            return [byte.decode('iso-8859-1') for byte in unpack(str(num) +
                    'c', self.read(num))]

    def read_byte(self, num=None, signed=False):
        if signed:
            format = 'b'
        else:
            format = 'B'
        if num is None:
            return unpack(format, self.read(1))[0]
        else:
            return unpack(str(num) + format, self.read(num))

    def read_hex(self):
        bytes = self.read_byte(4)
        hex = [format(byte, '02x') for byte in bytes]
        hex.reverse()
        return "".join(hex).upper()

    def read_short(self, num=None, signed=False):
        if signed:
            format = 'h'
        else:
            format = 'H'
        if num is None:
            return unpack(format, self.read(2))[0]
        else:
            return unpack(str(num) + format, self.read(num * 2))

    def read_int(self, num=None, signed=False):
        if signed:
            format = 'i'
        else:
            format = 'I'
        if num is None:
            return unpack(format, self.read(4))[0]
        else:
            return unpack(str(num) + format, self.read(num * 4))

    def read_float(self, num=None):
        if num is None:
            return unpack('f', self.read(4))[0]
        else:
            return unpack(str(num) + 'f', self.read(num * 4))

    def read_double(self, num=None):
        if num is None:
            return unpack('d', self.read(8))[0]
        else:
            return unpack(str(num) + 'd', self.read(num * 8))

    def read_string(self, num=None):
        if num is None:
            chars = []
            chars.append(self.read_char())
            while chars[-1] != "\0":
                chars.append(self.read_char())
            return "".join(chars[:-1])
        else:
            buffer = self.read(num)
            return buffer.rstrip(b"\0").decode('utf-8')

    def tell(self):
        return self.pos

    def seek(self, offset, from_what=0):
        if from_what == 0:
            self.pos = offset
        elif from_what == 1:
            self.pos += offset
        elif from_what == 2:
            self.pos = self.length - offset

    def end_of_stream(self):
        return self.pos >= self.length

