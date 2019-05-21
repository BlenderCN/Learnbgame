'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import struct


class DataWriter:


    def __init__(self):
        self.data_array = []


    def write_out(self, file_data):
        for val in self.data_array:
            file_data.write(val)


    def write_byte(self, num):
        val = struct.pack('B', num)
        self.data_array.append(val)

    def write_byte_string(self, str):
        self.write_byte(len(str))
        b_str = str.encode("utf-8")
        self.data_array.append(b_str)

    def write_int16(self, num):
        val = struct.pack('<H', num)
        self.data_array.append(val)

    def write_int32(self, num):
        val = struct.pack('<i', num)
        self.data_array.append(val)

    def write_uint32(self, num):
        val = struct.pack('<I', num)
        self.data_array.append(val)

    def write_float(self, num):
        val = struct.pack('<f', num)
        self.data_array.append(val)
