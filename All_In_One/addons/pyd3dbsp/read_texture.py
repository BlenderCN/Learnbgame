import struct
import os
import re

from collections import namedtuple
from enum import Enum

import texture_decoder as DECODER

TEXTHeader = namedtuple('TEXTHeader', 
    ('magic, version,'
    'format,'
    'usage,'
    'width, height,'
    'filesize,'
    'texture_ofs, mipmap1_ofs, mipmap2_ofs')
    )
fmt_TEXTHeader = '<3sBBBHH2xIIII'

class TextureUsage(Enum):
    Color = 0x00
    Default = 0x01
    Skybox = 0x05

class TextureFormat(Enum):
    ARGB32 = 0x01
    RGB24 = 0x02
    GA16 = 0x03
    A8 = 0x04
    DXT1 = 0x0B
    DXT3 = 0x0C
    DXT5 = 0x0D

class Texture():

    def __init__(self):
        self.header = None
        self.texture_data = None
        #self.mipmap1_data = None
        #self.mipmap2_data = None

        self.width = None
        self.height = None
        self.format = None
        self.usage = None

    def _read_header(self, file):
        file.seek(0)
        header_data = file.read(struct.calcsize(fmt_TEXTHeader))
        self.header = TEXTHeader._make(struct.unpack(fmt_TEXTHeader, header_data))
        self.header = self.header._replace(magic = self.header.magic.decode('utf-8'))
        
        self.width = self.header.width
        self.height = self.header.height
        self.format = self.header.format
        self.usage = self.header.usage
        

    def _read_raw_data(self, file):
        file.seek(self.header.texture_ofs, os.SEEK_SET)
        raw_data = file.read(self.header.filesize - self.header.texture_ofs)
        if(self.format == TextureFormat.DXT1.value):
            self.texture_data = DECODER.decode_dxt1(raw_data, self.width, self.height)
        elif(self.format and ( TextureFormat.DXT3.value or TextureFormat.DXT5.value )):
            self.texture_data = DECODER.decode_dxt5(raw_data, self.width, self.height)
        #TODO rest of the decoding if there is any
        

    def load_texture(self, filepath):
        with open(filepath, 'rb') as file:
            self._read_header(file)
            if(self.header.magic == 'IWi' and self.header.version == 5):
                self._read_raw_data(file)
                return True
            else:
                return False
