# -*- coding: utf8 -*-
# Blender WCP IFF mesh import/export script by Kevin Caccamo
# Copyright © 2013-2016 Kevin Caccamo
# E-mail: kevin@ciinet.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# <pep8-80 compliant>

# IFF reader class
from os.path import exists as fexists
from struct import unpack
from io import BytesIO


class IffReader:

    _iff_heads = (b"FORM", b"CAT ", b"LIST")

    def __init__(self, iff_file):
        if isinstance(iff_file, str):
            self._iff_file = open(iff_file, "rb")
        elif isinstance(iff_file, bytes) or isinstance(iff_file, bytearray):
            self._iff_file = BytesIO(iff_file)

    def id_isvalid(self, iffid):
        if len(iffid) != 4:
            raise TypeError("Invalid Chunk/Form ID length!")

        if isinstance(iffid, bytes):
            for idchar in iffid:
                if idchar < 0x20 or idchar > 0x7E:
                    raise ValueError("Invalid Chunk/Form ID!")
        elif isinstance(iffid, str):
            for idchar in iffid:
                if ord(idchar) < 0x20 or ord(idchar) > 0x7E:
                    raise ValueError("Invalid Chunk/Form ID!")

        return True  # No error was raised, so it's valid

    def skip_data(self):
        orig_pos = self._iff_file.tell()
        head = self._iff_file.read(4)
        if head in self._iff_heads:
            self._iff_file.seek(self._iff_file.tell() + 8)
            # Don't skip the entire FORM, just the header (length and name).
        elif self.id_isvalid(head):
            # Skip the entire CHUNK
            length = unpack(">i", self._iff_file.read(4))[0]
            bytes_to_skip = length
            bytes_to_skip += 1 if length % 2 == 1 else 0
            self._iff_file.seek(self._iff_file.tell() + bytes_to_skip)

            # IFF Chunks and FORMs are aligned at even offsets
            if self._iff_file.tell() % 2 == 1: self._iff_file.read(1)
        else:
            raise TypeError("This file is not a valid IFF file!")
        del orig_pos
        del head
        return None

    def read_data(self):
        orig_pos = self._iff_file.tell()
        head = self._iff_file.read(4)

        if head in self._iff_heads:

            length = (unpack(">i", self._iff_file.read(4))[0])
            name = self._iff_file.read(4)

            return {
                "type": "form",
                "length": length,
                "name": name,
                "offset": orig_pos
            }

            # =================================================================
            #
            # NOTE: This method (as well as the similar skip_data method)
            # doesn't read everything inside a form, and if you're counting the
            # number of bytes to determine whether you've read the FORM
            # completely, start the counter at 4, and remember to add 8 each
            # time to take the FORM/CHUNK header into account!! (The 4 bytes
            # representing the length of the FORM as a 32-bit unsigned integer
            # is counted as part of the inside of the FORM)
            #
            # ========================= LIKE THIS =============================
            #
            # form = iff.read_data()
            # ...
            # # Initialize bytes read counter at 4
            # form_read = 4
            # while form_read < form["length"]:
            #     data = iff.read_data()  # Read the data
            #
            #     # Parse the data
            #     if data["type"] == 'chunk' and data["name"] == b"BLAH":
            #         parse(data)
            #     elif:
            #         ...
            #     else:
            #         ...
            #
            #     # Add to bytes read counter.
            #     form_read += 8 + data["length"]
            #     if data["length"] % 2 == 1: form_read += 1

        elif self.id_isvalid(head):
            name = head
            length = unpack(">i", self._iff_file.read(4))[0]
            data = self._iff_file.read(length)

            # IFF Chunks and FORMs are aligned at even offsets
            if self._iff_file.tell() % 2 == 1:
                self._iff_file.read(1)
                length += 1

            return {
                "type": "chunk",
                "length": length,
                "name": name,
                "offset": orig_pos,
                "data": data
            }

            # NOTE: The chunk data is contained in the "data" key
        else:
            raise TypeError("Tried to read an invalid IFF file!")
        return None  # Shouldn't be reachable

    def close(self):
        self._iff_file.close()
