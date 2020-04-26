import logging; log = logging.getLogger(__name__)
from .BinaryObject import BinaryObject
import struct

class Offset(BinaryObject):
    """An offset of another object in a binary file."""
    DisplayFormat = '0x%08X'
