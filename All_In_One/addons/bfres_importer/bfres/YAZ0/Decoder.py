import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject, Offset
from bfres.BinaryFile import BinaryFile

class Header(BinaryStruct):
    """YAZ0 file header."""
    magic = (b'Yaz0', b'Yaz1')
    fields = (
        ('4s', 'magic'),
        ('>I', 'size'),
    )


class Decoder:
    """YAZ0 decoder."""
    def __init__(self, file:BinaryFile, progressCallback=None):
        self.file     = file
        self.header   = Header().readFromFile(file)
        self.src_pos  = 16
        self.dest_pos = 0
        self.size     = self.header['size']
        self.dest_end = self.size
        self._output  = []
        self._outputStart = 0
        if progressCallback is None:
            progressCallback = lambda cur, total: cur
        self.progressCallback = progressCallback
        progressCallback(0, self.size)


    def _nextByte(self) -> bytes:
        """Return next byte from input, or EOF."""
        self.file.seek(self.src_pos)
        self.src_pos += 1
        return self.file.read(1)[0]


    def _outputByte(self, b:(int,bytes)) -> bytes:
        """Write byte to output and return it."""
        if type(b) is int: b = bytes((b,))
        self._output.append(b)

        # we only need to keep the last 0x1111 bytes of the output
        # since that's the furthest back we can seek to copy from.
        excess = len(self._output) - 0x1111
        if excess > 0:
            self._output = self._output[-0x1111:]
            self._outputStart += excess

        self.dest_pos += 1
        if self.dest_pos & 0x3FF == 0 or self.dest_pos >= self.size:
            self.progressCallback(self.dest_pos, self.size)
        return b


    def bytes(self):
        """Generator that yields bytes from the decompressed stream."""
        code     = 0
        code_len = 0
        while self.dest_pos < self.dest_end:
            if not code_len:
                code = self._nextByte()
                code_len = 8
            if code & 0x80: # output next byte from input
                yield self._outputByte(self._nextByte())
            else: # repeat some bytes from output
                b1 = self._nextByte()
                b2 = self._nextByte()
                offs = ((b1 & 0x0F) << 8) | b2
                copy_src = self.dest_pos - (offs & 0xFFF) - 1
                n = b1 >> 4
                if n: n += 2
                else: n = self._nextByte() + 0x12
                assert (3 <= n <= 0x111)
                for i in range(n):
                    p = copy_src - self._outputStart
                    yield self._outputByte(self._output[p])
                    copy_src += 1
            code <<= 1
            code_len -= 1


    def read(self, size:int=-1) -> bytes:
        """File-like interface for reading decompressed stream."""
        res = []
        data = self.bytes()
        while size < 0 or len(res) < size:
            try: res.append(next(data))
            except StopIteration: break
        return b''.join(res)


    def __str__(self):
        return "<Yaz0 stream at 0x%x>" % id(self)
