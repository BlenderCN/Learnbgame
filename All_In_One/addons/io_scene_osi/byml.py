# Copyright 2018 leoetlino <leo@leolam.fr>
# Licensed under MIT

from __future__ import absolute_import
from enum import IntEnum
import ctypes
from .sortedcontainers import SortedDict
import struct
import typing
from itertools import *

class NodeType(IntEnum):
    STRING = 0xa0
    ARRAY = 0xc0
    HASH = 0xc1
    STRING_TABLE = 0xc2
    BOOL = 0xd0
    INT = 0xd1
    FLOAT = 0xd2
    UINT = 0xd3
    INT64 = 0xd4
    UINT64 = 0xd5
    DOUBLE = 0xd6
    NULL = 0xff

_NUL_CHAR = b'\x00'

def _get_unpack_endian_character(big_endian):
    return u'>' if big_endian else u'<'

def _align_up(value, size):
    return value + (size - value % size) % size

def _is_container_type(node_type):
    return node_type == NodeType.ARRAY or node_type == NodeType.HASH

def _is_value_type(node_type):
    return node_type == NodeType.STRING or (NodeType.BOOL <= node_type <= NodeType.UINT) or node_type == NodeType.NULL

# Nintendo uses uint nodes for some crc32 hashes. The problem is that they seem to be using
# uints randomly and the signed getters in their byml library will not look at uint nodes.
# So uints will be represented by specific classes in order to not lose type information.
# And while we are at it, let's use classes for other types to avoid unintended type conversions.
class Int(int):
    pass
class Float(float):
    pass
class UInt(int):
    pass
class Int64(int):
    pass
class UInt64(int):
    pass
class Double(float):
    pass

class Byml(object):
    u"""A simple BYMLv2 parser that handles both big endian and little endian documents."""

    def __init__(self, data):
        self._data = data

        magic = self._data[0:2]
        if magic == b'BY':
            self._be = True
        elif magic == b'YB':
            self._be = False
        else:
            raise ValueError(u"Invalid magic: %s (expected 'BY' or 'YB')" % magic)

        version = self._read_u16(2)
        if not (1 <= version <= 3):
            raise ValueError(u"Invalid version: %u (expected 1-3)" % version)
        if version == 1 and self._be:
            raise ValueError(u"Invalid version: %u-wiiu (expected 1-3)" % version)

        self._hash_key_table_offset = self._read_u32(4)
        self._string_table_offset = self._read_u32(8)

        self._hash_key_table = self._parse_string_table(self._hash_key_table_offset)
        if self._string_table_offset != 0:
            self._string_table = self._parse_string_table(self._string_table_offset)

    def parse(self):
        u"""Parse the BYML and get the root node with all children."""
        node_type = self._data[self._read_u32(12)]
        if not _is_container_type(node_type):
            raise ValueError(u"Invalid root node: expected array or dict, got type 0x%x" % node_type)
        return self._parse_node(node_type, 12)

    def _parse_string_table(self, offset):
        if self._data[offset] != NodeType.STRING_TABLE:
            raise ValueError(u"Invalid node type: 0x%x (expected 0xc2)" % self._data[offset])

        array = list()
        size = self._read_u24(offset + 1)
        for i in range(size):
            string_offset = offset + self._read_u32(offset + 4 + 4*i)
            array.append(self._read_string(string_offset))
        return array

    def _parse_node(self, node_type, offset):
        if node_type == NodeType.STRING:
            return self._parse_string_node(self._read_u32(offset))
        if node_type == NodeType.ARRAY:
            return self._parse_array_node(self._read_u32(offset))
        if node_type == NodeType.HASH:
            return self._parse_hash_node(self._read_u32(offset))
        if node_type == NodeType.BOOL:
            return self._parse_bool_node(offset)
        if node_type == NodeType.INT:
            return self._parse_int_node(offset)
        if node_type == NodeType.FLOAT:
            return self._parse_float_node(offset)
        if node_type == NodeType.UINT:
            return self._parse_uint_node(offset)
        if node_type == NodeType.INT64:
            return self._parse_int64_node(self._read_u32(offset))
        if node_type == NodeType.UINT64:
            return self._parse_uint64_node(self._read_u32(offset))
        if node_type == NodeType.DOUBLE:
            return self._parse_double_node(self._read_u32(offset))
        if node_type == NodeType.NULL:
            return None
        raise ValueError(u"Unknown node type: 0x%x" % node_type)

    def _parse_string_node(self, index):
        return self._string_table[index]

    def _parse_array_node(self, offset):
        size = self._read_u24(offset + 1)
        array = list(list())
        value_array_offset = int(offset + _align_up(size, 4) + 4)
        for i in range(size):
            node_type = self._data[offset + 4 + i]
            array.append(self._parse_node(node_type, value_array_offset + 4*i))
        return array

    def _parse_hash_node(self, offset):
        size = self._read_u24(offset + 1)
        result = dict(dict())
        for i in range(size):
            entry_offset = int(offset + 4 + 8*i)
            string_index = int(self._read_u24(entry_offset + 0))
            name = str(self._hash_key_table[string_index])

            node_type = self._data[entry_offset + 3]
            result[name] = self._parse_node(node_type, entry_offset + 4)

        return result

    def _parse_bool_node(self, offset):
        return self._parse_uint_node(offset) != 0

    def _parse_int_node(self, offset):
        return Int(struct.unpack_from(_get_unpack_endian_character(self._be) + u'i', self._data, offset)[0])

    def _parse_float_node(self, offset):
        return Float(struct.unpack_from(_get_unpack_endian_character(self._be) + u'f', self._data, offset)[0])

    def _parse_uint_node(self, offset):
        return UInt(self._read_u32(offset))

    def _parse_int64_node(self, offset):
        return Int64(struct.unpack_from(_get_unpack_endian_character(self._be) + u'q', self._data, offset)[0])

    def _parse_uint64_node(self, offset):
        return UInt64(struct.unpack_from(_get_unpack_endian_character(self._be) + u'Q', self._data, offset)[0])

    def _parse_double_node(self, offset):
        return Double(struct.unpack_from(_get_unpack_endian_character(self._be) + u'd', self._data, offset)[0])

    def _read_u16(self, offset):
        return struct.unpack_from(_get_unpack_endian_character(self._be) + u'H', self._data, offset)[0]

    def _read_u24(self, offset):
        if self._be:
            return struct.unpack('>I', _NUL_CHAR + self._data[offset:offset+3])[0]
        return struct.unpack('<I', self._data[offset:offset+3] + _NUL_CHAR)[0]

    def _read_u32(self, offset):
        return struct.unpack_from(_get_unpack_endian_character(self._be) + u'I', self._data, offset)[0]

    def _read_string(self, offset):
        end = self._data.find(_NUL_CHAR, offset)
        return self._data[offset:end].decode(u'utf-8')

class _PlaceholderOffsetWriter(object):
    u"""Writes a placeholder offset value that will be filled later."""
    def __init__(self, stream, parent):
        self._stream = stream
        self._offset = stream.tell()
        self._parent = parent
    def write_placeholder(self):
        self._stream.write(self._parent._u32(0xffffffff))
    def write_offset(self, offset, base = 0):
        current_offset = self._stream.tell()
        self._stream.seek(self._offset)
        self._stream.write(self._parent._u32(offset - base))
        self._stream.seek(current_offset)
    def write_current_offset(self, base = 0):
        self.write_offset(self._stream.tell(), base)

_NodeToOffsetMap = typing.Dict[typing.Tuple[NodeType, int], int]
def _hash(o):
    def _freeze(o):
        if isinstance(o, dict):
            return frozenset(dict(( k, _freeze(v)) for k,v in o.items()).items())
        if isinstance(o, list):
            return tuple([_freeze(v) for v in o])
        return o
    return hash(_freeze(o))

class Writer(object):
    u"""BYMLv2 writer."""

    def __init__(self, data, be=False, version=2):
        self._data = data
        self._be = be
        self._version = version

        if not isinstance(data, list) and not isinstance(data, dict):
            raise ValueError(u"Data should be a dict or a list")

        if not (1 <= version <= 3):
            raise ValueError(u"Invalid version: %u (expected 1-3)" % version)
        if version == 1 and be:
            raise ValueError(u"Invalid version: %u-wiiu (expected 1-3)" % version)

        self._hash_key_table = SortedDict[str, int](SortedDict())
        self._string_table = SortedDict[str, int](SortedDict())
        self._make_string_table(self._data, self._hash_key_table, self._string_table)
        # Nintendo seems to sort entries in alphabetical order.
        self._sort_string_table(self._hash_key_table)
        self._sort_string_table(self._string_table)

    def write(self, stream):
        # Header
        stream.write(b'BY' if self._be else b'YB')
        stream.write(self._u16(self._version))
        if self._hash_key_table:
            hash_key_table_offset_writer = self._write_placeholder_offset(stream)
        else:
            stream.write(self._u32(0))
        if self._string_table:
            string_table_offset_writer = self._write_placeholder_offset(stream)
        else:
            stream.write(self._u32(0))
        root_node_offset_writer = self._write_placeholder_offset(stream)

        # Hash key table
        if self._hash_key_table:
            hash_key_table_offset_writer.write_current_offset()
            self._write_string_table(stream, self._hash_key_table)
            stream.seek(_align_up(stream.tell(), 4))

        # String table
        if self._string_table:
            string_table_offset_writer.write_current_offset()
            self._write_string_table(stream, self._string_table)
            stream.seek(_align_up(stream.tell(), 4))

        # Root node
        root_node_offset_writer.write_current_offset()
        # Nintendo attempts to minimize document size by reusing nodes where possible.
        # Let us do so too.
        node_to_offset_map = _NodeToOffsetMap(dict())
        self._write_nonvalue_node(stream, self._data, node_to_offset_map)
        stream.seek(_align_up(stream.tell(), 4))

    def _make_string_table(self, data, hash_key_table, string_table):
        if isinstance(data, str) and data not in string_table:
            string_table[data] = 0xffffffff
        elif isinstance(data, list):
            for item in data:
                self._make_string_table(item, hash_key_table, string_table)
        elif isinstance(data, dict):
            for (key, value) in data.items():
                if key not in hash_key_table:
                    hash_key_table[key] = 0xffffffff
                self._make_string_table(value, hash_key_table, string_table)

    def _sort_string_table(self, table):
        for (i, key) in enumerate(table.keys()):
            table[key] = i

    def _write_string_table(self, stream, table):
        base = stream.tell()
        stream.write(self._u8(NodeType.STRING_TABLE))
        stream.write(self._u24(len(table)))
        offset_writers = typing.List[_PlaceholderOffsetWriter]([])
        for i in range(len(table)):
            offset_writers.append(self._write_placeholder_offset(stream))
        last_offset_writer = self._write_placeholder_offset(stream)

        for (string, offset_writer) in izip(table.keys(), offset_writers):
            offset_writer.write_current_offset(base)
            stream.write(str(string).encode("utf8"))
            stream.write(_NUL_CHAR)
        last_offset_writer.write_current_offset(base)

    def _write_nonvalue_node(self, stream, data, node_to_offset_map):
        nonvalue_nodes = typing.List[typing.Tuple[typing.Any, _PlaceholderOffsetWriter]]([])

        if isinstance(data, list):
            stream.write(self._u8(NodeType.ARRAY))
            stream.write(self._u24(len(data)))
            for item in data:
                stream.write(self._u8(self._to_byml_type(item)))
            stream.seek(_align_up(stream.tell(), 4))
            for item in data:
                if _is_value_type(self._to_byml_type(item)):
                    stream.write(self._to_byml_value(item))
                else:
                    nonvalue_nodes.append((item, self._write_placeholder_offset(stream)))
        elif isinstance(data, dict):
            stream.write(self._u8(NodeType.HASH))
            stream.write(self._u24(len(data)))
            for (key, value) in data.items():
                stream.write(self._u24(self._hash_key_table[key]))
                node_type = self._to_byml_type(value)
                stream.write(self._u8(node_type))
                if _is_value_type(node_type):
                    stream.write(self._to_byml_value(value))
                else:
                    nonvalue_nodes.append((value, self._write_placeholder_offset(stream)))
        elif isinstance(data, UInt64):
            stream.write(self._u64(data))
        elif isinstance(data, Int64):
            stream.write(self._s64(data))
        elif isinstance(data, Double):
            stream.write(self._f64(data))
        elif isinstance(data, int) or isinstance(data, float):
            raise ValueError(u"Implicit conversions from int/float are not supported -- "
                             u"please use Int/Float/UInt/Int64/UInt64/Double")
        else:
            raise ValueError(u"Invalid non-value type")

        for (data, offset_writer) in nonvalue_nodes:
            node = (self._to_byml_type(data), _hash(data))
            if node in node_to_offset_map:
                offset_writer.write_offset(node_to_offset_map[node])
            else:
                offset_writer.write_current_offset()
                node_to_offset_map[node] = stream.tell()
                self._write_nonvalue_node(stream, data, node_to_offset_map)

    def _to_byml_type(self, data):
        if isinstance(data, str):
            return NodeType.STRING
        if isinstance(data, list):
            return NodeType.ARRAY
        if isinstance(data, dict):
            return NodeType.HASH
        if isinstance(data, bool):
            return NodeType.BOOL
        if isinstance(data, Int):
            return NodeType.INT
        if isinstance(data, Float):
            return NodeType.FLOAT
        if isinstance(data, UInt):
            return NodeType.UINT
        if isinstance(data, Int64):
            return NodeType.INT64
        if isinstance(data, UInt64):
            return NodeType.UINT64
        if isinstance(data, Double):
            return NodeType.DOUBLE
        if isinstance(data, int) or isinstance(data, float):
            raise ValueError(u"Implicit conversions from int/float are not supported -- "
                             u"please use Int/Float/UInt/Int64/UInt64/Double")
        raise ValueError(u"Invalid value type")

    def _to_byml_value(self, value):
        if isinstance(value, str):
            return self._u32(self._string_table[value])
        if isinstance(value, bool):
            return self._u32(1 if value != 0 else 0)
        if isinstance(value, Int):
            return self._s32(value)
        if isinstance(value, UInt):
            return self._u32(value)
        if isinstance(value, Float):
            return self._f32(value)
        raise ValueError(u"Invalid value type")

    def _write_placeholder_offset(self, stream):
        p = _PlaceholderOffsetWriter(stream, self)
        p.write_placeholder()
        return p

    def _u8(self, value):
        return struct.pack(u'B', value)
    def _u16(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'H', value)
    def _s16(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'h', value)
    def _u24(self, value):
        b = struct.pack(_get_unpack_endian_character(self._be) + u'I', value)
        return b[1:] if self._be else b[:-1]
    def _u32(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'I', value)
    def _s32(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'i', value)
    def _u64(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'Q', value)
    def _s64(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'q', value)
    def _f32(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'f', value)
    def _f64(self, value):
        return struct.pack(_get_unpack_endian_character(self._be) + u'd', value)
