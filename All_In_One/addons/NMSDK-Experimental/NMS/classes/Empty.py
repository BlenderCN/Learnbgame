# Empty structure for compatibility with exporting directly to mbins

from struct import pack


class Empty():
    def __init__(self, length):
        self.size = length

    def serialize(self, output):
        output.write(pack('{}s'.format(self.size), b''))

    def __str__(self):
        return '{0:#x} Padding'.format(self.size)
