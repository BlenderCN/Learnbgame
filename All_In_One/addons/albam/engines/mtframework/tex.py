from ctypes import c_int, c_uint, c_char, c_short, c_float, c_byte, sizeof
import os

from albam.image_formats.dds import DDSHeader, DDS
from albam.lib.structure import DynamicStructure
from albam.engines.mtframework.defaults import DEFAULT_TEXTURE


class Tex112(DynamicStructure):

    ID_MAGIC = b'TEX'
    _defaults_ = DEFAULT_TEXTURE
    _fields_ = (('id_magic', c_char * 4),
                ('version', c_short),
                ('revision', c_short),
                ('mipmap_count', c_byte),
                ('unk_byte_1', c_byte),
                ('unk_byte_2', c_byte),
                ('unk_byte_3', c_byte),
                ('width', c_short),
                ('height', c_short),
                ('reserved_1', c_int),
                ('compression_format', c_char * 4),
                ('unk_float_1', c_float),
                ('unk_float_2', c_float),
                ('unk_float_3', c_float),
                ('unk_float_4', c_float),
                ('mipmap_offsets', lambda s: c_uint * s.mipmap_count),
                ('dds_data', lambda s, f: c_byte * (os.path.getsize(f) - 40 -
                 sizeof(s.mipmap_offsets)) if f else c_byte * len(s.dds_data)),
                )

    def to_dds(self):
        header = DDSHeader(dwHeight=self.height, dwWidth=self.width,
                           dwMipMapCount=self.mipmap_count,
                           pixelfmt_dwFourCC=self.compression_format)
        dds = DDS(header=header, data=self.dds_data)
        dds.set_constants()
        dds.set_variables()
        return dds

    @classmethod
    def from_dds(cls, file_path):
        dds = DDS(file_path=file_path)
        mipmap_count = dds.header.dwMipMapCount
        width = dds.header.dwWidth
        height = dds.header.dwHeight
        compression_format = dds.header.pixelfmt_dwFourCC
        fixed_size_of_header = 40
        start_offset = fixed_size_of_header + (mipmap_count * 4)
        mipmap_offsets = cls.calculate_mipmap_offsets(mipmap_count, width, height, compression_format, start_offset)
        assert len(mipmap_offsets) == mipmap_count
        mipmap_offsets = (c_uint * len(mipmap_offsets))(*mipmap_offsets)
        dds_data = (c_byte * len(dds.data)).from_buffer(dds.data)

        # TODO: Don't hardcode uknown floats (seem to be brightness values)
        tex = cls(id_magic=cls.ID_MAGIC,
                  version=112,
                  revision=34,
                  mipmap_count=mipmap_count,
                  unk_byte_1=1,
                  unk_byte_2=0,
                  unk_byte_3=0,
                  width=width,
                  height=height,
                  compression_format=compression_format,
                  unk_float_1=0.76,
                  unk_float_2=0.76,
                  unk_float_3=0.76,
                  unk_float_4=0,
                  mipmap_offsets=mipmap_offsets,
                  dds_data=dds_data)

        return tex

    @classmethod
    def from_multiple_dds(cls, version=112, *file_paths):
        return (cls.from_dds(file_path) for file_path in file_paths)

    @staticmethod
    def calculate_mipmap_offsets(mipmap_count, width, height, fmt, start_offset):
        offsets = [start_offset]
        current_offset = start_offset
        for i in range(mipmap_count - 1):
            size = DDS.calculate_mipmap_size(width, height, i, fmt)
            current_offset += size
            offsets.append(current_offset)
        return offsets
