# Switch common formats
import logging; log = logging.getLogger(__name__)
from .. import BinaryStruct, BinaryObject
from ..Offset import Offset
from ..StringOffset import StringOffset

class Offset32(Offset):
    """A 32-bit offset in a Switch file header."""
    def __init__(self, name):
        super().__init__(name, '<I')


class Offset64(Offset):
    """A 64-bit offset in a Switch file header."""
    def __init__(self, name):
        super().__init__(name, '<Q')


class String(StringOffset):
    """An offset of a string in a Switch file header."""
    # maxlen=1024 is arbitrary here. should never see a string that
    # long, so this just helps catch issues.
    def __init__(self, name, fmt='<I', maxlen=1024,
    encoding='shift-jis', lenprefix='<H'):
        super().__init__(name, fmt, maxlen, encoding, lenprefix)
