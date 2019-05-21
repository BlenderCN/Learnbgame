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


class GMDCModel:

    trans_block_vals    = 7    # quaternion(x,y,z,w) and transform(x,y,z) values
    name_pair_vals      = 2    # ['blend group name', 'assigned element name']
    vertex_coords       = 3    # position [x,y,z]

    def __init__(self):
        self.transforms = None
        self.name_pairs = None
        self.vertices   = None
        self.faces      = None

    def read_data(self, data_read):
        count = data_read.read_int32()
        self.transforms = []
        for i in range(0,count):
            temp_block = []
            for j in range(0,GMDCModel.trans_block_vals):
                temp_val = data_read.read_float()
                temp_block.append(temp_val)
            self.transforms.append(temp_block)

        count = data_read.read_int32()
        self.name_pairs = []
        for i in range(0,count):
            temp_pair = []
            for j in range(0,GMDCModel.name_pair_vals):
                temp_name = data_read.read_byte_string()
                temp_pair.append(temp_name)
            self.name_pairs.append(temp_pair)

        vert_count = data_read.read_int32()
        self.vertices = []
        if vert_count > 0:
            face_count = data_read.read_int32()

            for i in range(0,vert_count):
                temp_verts = []
                for j in range(0,GMDCModel.vertex_coords):
                    temp_vert = data_read.read_float()
                    temp_verts.append(temp_vert)
                self.vertices.append(temp_verts)

            self.faces = []
            for i in range(0,face_count):
                temp_face = data_read.read_int16()
                self.faces.append(temp_face)


    def write(self, writer):
        writer.write_int32( len(self.transforms) )
        for transform in self.transforms:
            for val in transform:
                writer.write_float(val)

        writer.write_int32( len(self.name_pairs) )
        for pair in self.name_pairs:
            for name in pair:
                writer.write_byte_string(name)

        # Skip next section if vertcount == 0
        writer.write_int32( len(self.vertices) )
        if len(self.vertices) == 0:
            return

        writer.write_int32( len(self.faces) )

        for vert in self.vertices:
            for val in vert:
                writer.write_float(val)

        for face_ind in self.faces:
            writer.write_int16(face_ind)


    @staticmethod
    def build_data(b_models, bones, boundmesh):
        model = GMDCModel()

        model.transforms = []
        if bones:
            for b in bones:
                transformlist = []
                transformlist.append( b.rotation[1] )
                transformlist.append( b.rotation[2] )
                transformlist.append( b.rotation[3] )
                transformlist.append( b.rotation[0] )
                transformlist.append( b.position[0] )
                transformlist.append( b.position[1] )
                transformlist.append( b.position[2] )
                model.transforms.append(transformlist)

        model.name_pairs = []
        if b_models[0].morphs:
            namepairct = len(b_models[0].morphs)
            for i in range( namepairct + 1 ):
                if i == 0:
                    model.name_pairs.append( ['',''] )
                    continue

                model.name_pairs.append(
                    b_models[0].morphs[i - 1].name.split(', ')
                )

        model.vertices = []
        model.faces = []
        if boundmesh:
            model.vertices = boundmesh.vertices
            for f in boundmesh.faces:
                for ind in f:
                    model.faces.append(ind)

        return model
