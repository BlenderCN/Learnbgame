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


class GMDCSubset:

    vertex_coords = 3    # position [x,y,z]

    def __init__(self):
        self.vertices   = None
        self.faces      = None

    def read_data(self, data_read):
        vert_count = data_read.read_int32()
        self.vertices = []
        if vert_count > 0:
            face_count = data_read.read_int32()

            for i in range(0,vert_count):
                temp_verts = []
                for i in range(0,GMDCSubset.vertex_coords):
                    temp_val = data_read.read_float()
                    temp_verts.append(temp_val)
                self.vertices.append(temp_verts)

            self.faces = []
            for i in range(0,face_count):
                temp_val = data_read.read_int16()
                self.faces.append(temp_val)


    def write(self, writer):
        writer.write_int32( len(self.vertices) )
        if len(self.vertices) == 0:
            return

        writer.write_int32( len(self.faces) )
        for vert in self.vertices:
            for val in vert:
                writer.write_float(val)

        for vert_ind in self.faces:
            writer.write_int16(vert_ind)


    @staticmethod
    def build_data(b_models, bones, riggedbounds):
        subsets = []

        if bones:
            for b in bones:
                subset = GMDCSubset()
                subset.vertices = []
                subset.faces = []

                subset.vertices = riggedbounds[b.subset].vertices
                for f in riggedbounds[b.subset].faces:
                    for idx in f:
                        subset.faces.append(idx)

                subsets.append(subset)

        return subsets
