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


class GMDCGroup:

    def __init__(self):
        self.primitive_type = None
        self.link_index     = None
        self.name           = None
        self.faces          = None
        self.opacity_amount = None
        self.subsets        = None

    def read_data(self, data_read, version):
        self.primitive_type = data_read.read_int32()
        self.link_index     = data_read.read_int32()
        self.name           = data_read.read_byte_string()

        count = data_read.read_int32()
        self.faces = []
        for i in range(0,count):
            vertex_ref = data_read.read_int16()
            self.faces.append(vertex_ref)

        self.opacity_amount = data_read.read_int32()

        if version != 1:
            count = data_read.read_int32()
            self.subsets = []
            for i in range(0,count):
                subset_ref = data_read.read_int16()
                self.subsets.append(subset_ref)


    def write(self, writer):
        writer.write_int32(self.primitive_type)
        writer.write_int32(self.link_index)
        writer.write_byte_string(self.name)

        writer.write_int32( len(self.faces) )
        for vert_ind in self.faces:
            writer.write_int16(vert_ind)

        writer.write_int32(self.opacity_amount)

        writer.write_int32( len(self.subsets) )
        for subset in self.subsets:
            writer.write_int16(subset)


    def build_data(b_models, bones):
        groups = []

        for i, mod in enumerate(b_models):
            grp = GMDCGroup()

            grp.primitive_type = 2
            grp.link_index = i
            grp.name = mod.name

            grp.faces = []
            for f in mod.faces:
                for val in f:
                    grp.faces.append(val)

            grp.opacity_amount = mod.opacity_amount

            grp.subsets = []
            if bones:
                for i in range(len(bones)):
                    grp.subsets.append(i)

            groups.append(grp)

        return(groups)
