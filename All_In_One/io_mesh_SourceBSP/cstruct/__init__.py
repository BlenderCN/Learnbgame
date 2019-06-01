# -*- coding: utf-8 -*-
"""C-style structs for Python

Convert C struct definitions into Python classes with methods for
serializing/deserializing.
The usage is very simple: create a class subclassing cstruct.CStruct
and add a C struct definition as a string in the __struct__ field.
The C struct definition is parsed at runtime and the struct format string
is generated. The class offers the method "unpack" for deserializing
a string of bytes into a Python object and the method "pack" for
serializing the values into a string.

Example:
The following program reads the DOS partition information from a disk.

#!/usr/bin/python
import cstruct

class Position(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        unsigned char head;
        unsigned char sector;
        unsigned char cyl;
    \"\"\"

class Partition(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        unsigned char status;       /* 0x80 - active */
        struct Position start;
        unsigned char partition_type;
        struct Position end;
        unsigned int start_sect;    /* starting sector counting from 0 */
        unsigned int sectors;       /* nr of sectors in partition */
    \"\"\"

    def print_info(self):
        print("bootable: %s" % ((self.status & 0x80) and "Y" or "N"))
        print("partition_type: %02X" % self.partition_type)
        print("start: head: %X sectory: %X cyl: %X" % (self.start.head, self.start.sector, self.start.cyl))
        print("end: head: %X sectory: %X cyl: %X" % (self.end.head, self.end.sector, self.end.cyl))
        print("starting sector: %08X" % self.start_sect)
        print("size MB: %s" % (self.sectors / 2 / 1024))

class MBR(cstruct.CStruct):
    __byte_order__ = cstruct.LITTLE_ENDIAN
    __struct__ = \"\"\"
        char unused[440];
        unsigned char disk_signature[4];
        unsigned char usualy_nulls[2];
        struct Partition partitions[4];
        char signature[2];
    \"\"\"

    def print_info(self):
        print("disk signature: %s" % "".join(["%02X" % x for x in self.disk_signature]))
        print("usualy nulls: %s" % "".join(["%02X" % x for x in self.usualy_nulls]))
        for i, partition in enumerate(self.partitions):
            print("")
            print("partition: %s" % i)
            partition.print_info()

disk = "mbr"
f = open(disk, "rb")
mbr = MBR()
data = f.read(len(mbr))
mbr.unpack(data)
mbr.print_info()
f.close()

"""

#*****************************************************************************
#
# Copyright (c) 2013 Andrea Bonomi <andrea.bonomi@gmail.com>
#
# Published under the terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
#*****************************************************************************

__author__  = 'Andrea Bonomi <andrea.bonomi@gmail.com>'
__license__ = 'MIT'
__version__ = '1.0'
__date__ = '15 August 2013'

import re
import struct
import sys

__all__ = ['LITTLE_ENDIAN',
           'BIG_ENDIAN',
           'CStruct',
           'define',
           'typedef',
          ]

LITTLE_ENDIAN = '<'
BIG_ENDIAN = '>'

C_TYPE_TO_FORMAT = {
    'char':                 's',
    'signed char':          'b',
    'unsigned char':        'B',
    'short':                'h',
    'ushort':               'H',
    'unsigned short':       'H',
    'int':                  'i',
    'unsigned int':         'I',
    'long':                 'l',
    'unsigned long':        'L',
    'long long':            'q',
    'unsigned long long':   'Q',
    'float':                'f',
    'double':               'd',
    'void *':               'P',
    'int8':                 'b',
    'uint8':                'B',
    'int16':                'h',
    'uint16':               'H',
    'int32':                'i',
    'uint32':               'I',
    'int64':                'l',
    'uint64':               'L',
}

STRUCTS = {
}

DEFINES = {
}

TYPEDEFS = {
}

def define(key, value):
    """
    Add a definition that can be used in the C struct
    """
    DEFINES[key] = value

def typedef(type_, alias):
    """
    Define an alias for a data type
    """
    TYPEDEFS[alias] = type_

class CStructMeta(type):

    def __new__(mcs, name, bases, dict):
        __struct__ = dict.get("__struct__", None)
        if __struct__ is not None:
            dict['__fmt__'], dict['__fields__'], dict['__fields_types__'] = mcs.parse_struct(__struct__)
            if '__byte_order__' in dict:
                dict['__fmt__'] = dict['__byte_order__'] + dict['__fmt__']
            # Add the missing fields to the class
            for field in dict['__fields__']:
                if field not in dict:
                    dict[field] = None
            # Calculate the structure size
            if '<' in dict['__fmt__']:
                dict['__fmt__'] =dict['__fmt__'].replace('<','=')
            if '=' not in dict['__fmt__']:
                dict['__fmt__'] = '=' + dict['__fmt__']

            dict['__size__'] = struct.calcsize(dict['__fmt__'])
        new_class = type.__new__(mcs, name, bases, dict)
        if __struct__ is not None:
            STRUCTS[name] = new_class
        return new_class

    @staticmethod
    def parse_struct(st):
        # naive C struct parsing

        fmt = []
        fields = []
        fields_types = {}
        # remove the comments
        st = st.replace("*/","*/\n")
        st = "  ".join(re.split("/\*.*\*/",st))
        st.replace("\n", " ")
        for line_s in st.split(";"):
            line_s = line_s.strip()

            if line_s:

                line = line_s.split()

                if len(line) < 2:
                    raise Exception("Error parsing: " + line_s)
                vtype = line[0].strip()
                # signed/unsigned/struct
                if vtype == 'unsigned' or vtype == 'signed' or vtype == 'struct' and len(line) > 2:
                    vtype = vtype + " " + line[1].strip()
                    del line[0]
                vname = line[1]
                # long long
                if vname == 'long':
                    vtype = vtype +  ' long'
                    del line[0]
                    vname = line[1]
                # void *
                if vname.startswith("*"):
                    vname = vname[1:]
                    vtype = 'void *'
                # parse length
                vlen = 1
                if "[" in vname:
                    t = vname.split("[")
                    if len(t) != 2:
                        raise Exception("Error parsing: " + line_s)
                    vname = t[0].strip()
                    vlen = t[1]
                    vlen = vlen.split("]")[0].strip()
                    try:
                        vlen = int(vlen)
                    except:
                        vlen = DEFINES.get(vlen, None)
                        if vlen is None:
                            raise
                        else:
                            vlen = int(vlen)
                while vtype in TYPEDEFS:
                    vtype = TYPEDEFS[vtype]
                if vtype.startswith('struct '):
                    vtype = vtype[7:]
                    t = STRUCTS.get(vtype, None)
                    if t is None:
                        raise Exception("Unknow struct \"" + vtype + "\"")
                    vtype = t
                    ttype = "c"
                    vlen = vtype.size * vlen
                else:

                    ttype = C_TYPE_TO_FORMAT.get(vtype, None)

                    if ttype is None:
                        raise Exception("Unknow type \"" + vtype + "\"")
                fields.append(vname)
                fields_types[vname] = (vtype, vlen)
                if vlen > 1:
                    fmt.append(str(vlen))
                fmt.append(ttype)
        fmt = "".join(fmt)
        return fmt, fields, fields_types

    def __len__(cls):
        return cls.__size__

    @property
    def size(cls):
        """ Structure size (in bytes) """
        return cls.__size__

# Workaround for Python 2.x/3.x metaclass, thanks to
# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/#using-the-metaclass-in-python-2-x-and-3-x
_CStructParent = CStructMeta('_CStructParent', (object, ), {})

if sys.version_info < (2, 6):
    EMPTY_BYTES_STRING = str()
else:
    EMPTY_BYTES_STRING = bytes()

class CStruct(_CStructParent):
    """
    Convert C struct definitions into Python classes.

    __struct__ = definition of the struct in C syntax
    __byte_order__ = (optional) valid values are LITTLE_ENDIAN and BIG_ENDIAN

    The following fields are generated from the C struct definition
    __fmt__ = struct format string
    __size__ = lenght of the structure in bytes
    __fields__ = list of structure fields
    __fields_types__ = dictionary mapping field names to types
    Every fields defined in the structure is added to the class

    """

    def __init__(self, string=None, **kargs):
        if string is not None:
            self.unpack(string)
        for key, value in kargs.items():
            setattr(self, key, value)

    def unpack(self, string):
        """
        Unpack the string containing packed C structure data
        """
        data = struct.unpack(self.__fmt__, string)
        i = 0
        for field in self.__fields__:
            (vtype, vlen) = self.__fields_types__[field]
            if vtype == 'char': # string
                setattr(self, field, data[i])
                i = i + 1
            elif isinstance(vtype, CStructMeta):
                num = int(vlen / vtype.size)
                if num == 1: # single struct
                    sub_struct = vtype()
                    sub_struct.unpack(EMPTY_BYTES_STRING.join(data[i:i+sub_struct.size]))
                    setattr(self, field, sub_struct)
                    i = i + sub_struct.size
                else: # multiple struct
                    sub_structs = []
                    for j in range(0, num):
                        sub_struct = vtype()
                        sub_struct.unpack(EMPTY_BYTES_STRING.join(data[i:i+sub_struct.size]))
                        i = i + sub_struct.size
                        sub_structs.append(sub_struct)
                    setattr(self, field, sub_structs)
            elif vlen == 1:
                setattr(self, field, data[i])
                i = i + vlen
            else:
                setattr(self, field, list(data[i:i+vlen]))
                i = i + vlen

    def pack(self):
        """
        Pack the structure data into a string
        """
        data = []
        for field in self.__fields__:
            (vtype, vlen) = self.__fields_types__[field]
            if vtype == 'char': # string
                data.append(getattr(self, field))
            elif isinstance(vtype, CStructMeta):
                num = int(vlen / vtype.size)
                if num == 1: # single struct
                    v = getattr(self, field, vtype())
                    v = v.pack()
                    if sys.version_info >= (3, 0):
                        v = ([bytes([x]) for x in v])
                    data.extend(v)
                else: # multiple struct
                    values = getattr(self, field, [])
                    for j in range(0, num):
                        try:
                            v = values[j]
                        except:
                            v = vtype()
                        v = v.pack()
                        if sys.version_info >= (3, 0):
                            v = ([bytes([x]) for x in v])
                        data.extend(v)
            elif vlen == 1:
                data.append(getattr(self, field))
            else:
                v = getattr(self, field)
                v = v[:vlen] + [0] * (vlen - len(v))
                data.extend(v)
        return struct.pack(self.__fmt__, *data)

    def __len__(self):
        """ Structure size (in bytes) """
        return self.__size__

    @property
    def size(self):
        """ Structure size (in bytes) """
        return self.__size__

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        result = []
        for field in self.__fields__:
            result.append(field + "=" + str(getattr(self, field, None)))
        return type(self).__name__ + "(" + ", ".join(result) + ")"

    def __repr__(self):
        return self.__str__()

