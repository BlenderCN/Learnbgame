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


class GMDCLinkage:

    def __init__(self):
        self.indices            = None

        self.ref_array_size     = None
        self.active_elements    = None

        self.submodel_vertices  = None
        self.submodel_normals   = None
        self.submodel_uvs       = None

    def read_data(self, data_read):
        count = data_read.read_int32()
        self.indices = []
        for i in range(0,count):
            temp_val = data_read.read_int16()
            self.indices.append(temp_val)

        self.ref_array_size = data_read.read_int32()
        self.active_elements = data_read.read_int32()

        count = data_read.read_int32()
        self.submodel_vertices = []
        for i in range(0,count):
            temp_val = data_read.read_int16()
            self.submodel_vertices.append(temp_val)

        count = data_read.read_int32()
        self.submodel_normals = []
        for i in range(0,count):
            temp_val = data_read.read_int16()
            self.submodel_normals.append(temp_val)

        count = data_read.read_int32()
        self.submodel_uvs = []
        for i in range(0,count):
            temp_val = data_read.read_int16()
            self.submodel_uvs.append(temp_val)


    def write(self, writer):
        writer.write_int32( len(self.indices) )
        for ind in self.indices:
            writer.write_int16(ind)

        writer.write_int32(self.ref_array_size)
        writer.write_int32(self.active_elements)

        writer.write_int32( len(self.submodel_vertices) )
        for vert_ind in self.submodel_vertices:
            writer.write_int16(vert_ind)

        writer.write_int32( len(self.submodel_normals) )
        for norm_ind in self.submodel_normals:
            writer.write_int16(norm_ind)

        writer.write_int32( len(self.submodel_normals) )
        for uv_ind in self.submodel_uvs:
            writer.write_int16(uv_ind)


    @staticmethod
    def build_data(b_models, grplinks):
        linkages = []

        for i, mod in enumerate(b_models):
            linkage = GMDCLinkage()

            linkage.indices = grplinks[i]
            linkage.ref_array_size = len(mod.vertices)
            linkage.active_elements = len(linkage.indices)

            linkage.submodel_vertices = []
            linkage.submodel_uvs = []
            linkage.submodel_normals = []

            linkages.append(linkage)

        return(linkages)
