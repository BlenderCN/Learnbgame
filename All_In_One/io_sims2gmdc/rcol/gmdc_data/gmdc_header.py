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


class GMDCHeader:


    def __init__(self, language, stringstyle, repeatval, indexval, filetype,
                        blockname, block_id, version, resname, res_id,
                        res_version, filename):
        self.language           = language
        self.string_style       = stringstyle
        self.repeat_value       = repeatval
        self.index_value        = indexval
        self.file_type          = filetype
        self.block_name         = blockname
        self.block_id           = block_id
        self.version            = version
        self.res_name           = resname
        self.res_id             = res_id
        self.res_version        = res_version
        self.file_name          = filename


    @staticmethod
    def from_data(data_read):
        language           = data_read.read_int16()
        stringstyle        = data_read.read_int16()
        repeatval          = data_read.read_int32()
        indexval           = data_read.read_int32()
        filetype           = data_read.read_uint32()
        blockname          = data_read.read_byte_string()
        block_id           = data_read.read_uint32()
        version            = data_read.read_int32()
        resname            = data_read.read_byte_string()
        res_id             = data_read.read_int32()
        res_version        = data_read.read_int32()
        filename           = data_read.read_byte_string()

        return GMDCHeader( language, stringstyle, repeatval, indexval, filetype,
                            blockname, block_id, version, resname, res_id,
                            res_version, filename)


    @staticmethod
    def build_data(filename):
        language    = 0x0001        # WORD
        stringstyle = 0xffff        # WORD
        repeatval   = 0             # DWORD
        indexval    = 1             # DWORD
        filetype    = 0xAC4F8687    # DWORD, GMDC Identifier
        blockname   = 'cGeometryDataContainer'
        block_id    = 0xAC4F8687    # DWORD, GMDC Identifier
        version     = 4             # DWORD, needs support for 1 and 2 later
        resname     = 'cSGResource'
        res_id      = 0             # DWORD
        res_version = 2             # DWORD
        # filename

        return GMDCHeader( language, stringstyle, repeatval, indexval, filetype,
                            blockname, block_id, version, resname, res_id,
                            res_version, filename)


    def write(self, writer):
        writer.write_int16(self.language)
        writer.write_int16(self.string_style)
        writer.write_int32(self.repeat_value)
        writer.write_int32(self.index_value)
        writer.write_uint32(self.file_type)
        writer.write_byte_string(self.block_name)
        writer.write_uint32(self.block_id)
        writer.write_int32(self.version)
        writer.write_byte_string(self.res_name)
        writer.write_uint32(self.res_id)
        writer.write_int32(self.res_version)
        writer.write_byte_string(self.file_name)
