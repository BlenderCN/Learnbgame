from ctypes import Structure, sizeof, c_int, c_uint, c_char, c_short, c_ubyte
import ntpath
import os
import zlib

from albam.engines.mtframework.mappers import FILE_ID_TO_EXTENSION, EXTENSION_TO_FILE_ID
from albam.lib.structure import DynamicStructure


class FileEntry(Structure):
    MAX_FILE_PATH = 64

    _fields_ = (('file_path', c_char * MAX_FILE_PATH),
                ('file_id', c_int),
                ('zsize', c_uint),
                ('size', c_uint, 24),
                ('flags', c_uint, 8),
                ('offset', c_uint),
                )


def get_padding(tmp_struct):
    padding = 32768 - sizeof(tmp_struct)
    if padding < 0:
        padding += 32768
    return padding


def get_data_length(tmp_struct, file_path=None):
    if file_path:
        try:
            length = os.path.getsize(file_path) - sizeof(tmp_struct)
        except TypeError:
            # XXX: inefficient?
            length = len(file_path.getbuffer()) - sizeof(tmp_struct)
    else:
        length = len(tmp_struct.data)
    return length


class Arc(DynamicStructure):
    ID_MAGIC = b'ARC'

    _fields_ = (('id_magic', c_char * 4),
                ('version', c_short),
                ('files_count', c_short),
                ('file_entries', lambda s: FileEntry * s.files_count),
                ('padding', lambda s: c_ubyte * get_padding(s)),
                ('data', lambda s, f: c_ubyte * get_data_length(s, f)),
                )

    def unpack(self, output_dir='.'):
        data = memoryview(self.data)
        offset = 0
        output_dir = os.path.abspath(output_dir)
        for i in range(self.files_count):
            fe = self.file_entries[i]
            file_path = self._get_path(fe.file_path, fe.file_id, output_dir)
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            with open(file_path, 'wb') as w:
                w.write(zlib.decompress(data[offset: offset + fe.zsize]))
            offset += fe.zsize

    @classmethod
    def from_dir(cls, source_path):
        file_paths = {os.path.join(root, f) for root, _, files in os.walk(source_path)
                      for f in files}
        files_count = len(file_paths)
        file_entries = (FileEntry * files_count)()
        current_offset = 32768
        data = bytearray()
        for i, file_path in enumerate(sorted(file_paths)):
            with open(file_path, 'rb') as f:
                chunk = zlib.compress(f.read())
            data.extend(chunk)
            ext = os.path.splitext(file_path)[1].replace('.', '')
            file_entries[i] = FileEntry(file_path=cls._set_path(source_path, file_path),
                                        file_id=EXTENSION_TO_FILE_ID.get(ext) or 0,
                                        flags=64,  # always compressing
                                        size=os.path.getsize(file_path),
                                        zsize=len(chunk), offset=current_offset)
            current_offset += len(chunk)

        data = (c_ubyte * len(data)).from_buffer(data)
        return cls(id_magic=cls.ID_MAGIC, version=7, files_count=files_count,
                   file_entries=file_entries, data=data)

    @staticmethod
    def _get_path(file_path, file_type_id, output_path):
        file_extension = FILE_ID_TO_EXTENSION.get(file_type_id) or str(file_type_id)
        file_path = file_path.decode('ascii')
        file_path = '.'.join((file_path, file_extension))
        parts = file_path.split(ntpath.sep)
        file_path = os.path.join(output_path, *parts)
        return file_path

    @staticmethod
    def _set_path(source_path, file_path):
        source_path = source_path + os.path.sep if not source_path.endswith(os.path.sep) else source_path
        file_path = file_path.replace(source_path, '')
        file_path = os.path.splitext(file_path)[0]
        parts = file_path.split(os.path.sep)
        return ntpath.join('', *parts).encode('ascii')
