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
    """ This class is responsible for writing data to a GEOM file """


    def __init__(self):
        self.data = []


    def write_out(self, filedata):
        for value in self.data:
            filedata.write(value)


    def write_byte(self, num):
        self.data.append( struct.pack('B', num) )


    def write_string(self, str):
        self.write_byte(len(str))
        self.data.append( str.encode("utf-8") )


    def write_int16(self, num):
        self.data.append( struct.pack('<h', num) )


    def write_uint16(self, num):
        self.data.append( struct.pack('<H', num) )


    def write_int32(self, num):
        self.data.append( struct.pack('<i', num) )


    def write_uint32(self, num):
        self.data.append( struct.pack('<I', num) )


    def write_int64(self, num):
        self.data.append( struct.pack('<q', num) )


    def write_uint64(self, num):
        self.data.append( struct.pack('<Q', num) )


    def write_float(self, num):
        self.data.append( struct.pack('<f', num) )
