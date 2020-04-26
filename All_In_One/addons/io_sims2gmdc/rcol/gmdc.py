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
from .gmdc_data import gmdc_header, gmdc_element, gmdc_linkage, gmdc_group, gmdc_model, gmdc_subset
from .gmdc_data.gmdc_header import GMDCHeader
from .data_reader import DataReader
from .data_writer import DataWriter

class GMDC:


    element_ids = {
        0x1C4AFC56: 'Blend Indices',
        0x5C4AFC5C: 'Blend Weights',
        0x7C4DEE82: 'Target Indices',
        0xCB6F3A6A: 'Normal Morph Deltas',
        0xCB7206A1: 'Colour',
        0xEB720693: 'Colour Deltas',
        0x3B83078B: 'Normals List',
        0x5B830781: 'Vertices',
        0xBB8307AB: 'UV Coordinates',
        0xDB830795: 'UV Coordinate Deltas',
        0x9BB38AFB: 'Binormals',
        0x3BD70105: 'Bone Weights',
        0xFBD70111: 'Bone Assignments',
        0x89D92BA0: 'Bump Map Normals',
        0x69D92B93: 'Bump Map Normal Deltas',
        0x5CF2CFE1: 'Morph Vertex Deltas',
        0xDCF2CFDC: 'Morph Vertex Map',
        0x114113C3: '(EP4) VertexID',
        0x114113CD: '(EP4) RegionMask'
    }


    GMDC_IDENTIFIER = 0xAC4F8687


    def __init__(self, file_data, byte_offset):
        self.data_read  = DataReader(file_data, byte_offset)

        self.header     = None
        self.elements   = None
        self.linkages   = None
        self.groups     = None
        self.model      = None
        self.subsets    = None


    @staticmethod
    def from_file_data(file_path):
        print("reading .5gd file...\n")

        file = open(file_path, "rb")
        file_data = file.read()
        byte_offset = 0
        file.close()
        return GMDC(file_data, byte_offset)


    def write(self, path):
        print("writing .5gd file...\n")

        file_data = open(path, "wb")
        writer = DataWriter()

        # HEADER
        self.header.write(writer)

        # ELEMENTS
        writer.write_int32( len(self.elements) )
        for el in self.elements:
            el.write(writer)

        # LINKAGES
        writer.write_int32( len(self.linkages) )
        for li in self.linkages:
            li.write(writer)

        # GROUPS
        writer.write_int32( len(self.groups) )
        for gr in self.groups:
            gr.write(writer)

        # MODEL
        self.model.write(writer)

        # SUBSETS
        writer.write_int32( len(self.subsets) )
        for su in self.subsets:
            su.write(writer)

        writer.write_out(file_data)
        file_data.close()



    def load_header(self):
        self.header = GMDCHeader.from_data(self.data_read)

        if self.header.version != 4 or self.header.file_type != self.GMDC_IDENTIFIER:
            return False
        return True

    @staticmethod
    def build_data(filename, b_models, bones, boundmesh, riggedbounds):
        gmdc_data = GMDC(None, None)

        # HEADER
        gmdc_data.header = GMDCHeader.build_data(filename)

        # ELEMENTS
        # Tuple ( elements[], group_element_links[][] )
        element_data = gmdc_element.GMDCElement.from_blender(b_models, bones)
        gmdc_data.elements = element_data[0]

        # LINKAGES
        gmdc_data.linkages = gmdc_linkage.GMDCLinkage.build_data(
            b_models, element_data[1]
        )

        # GROUPS
        gmdc_data.groups = gmdc_group.GMDCGroup.build_data(
            b_models, bones
        )

        # MODEL
        gmdc_data.model = gmdc_model.GMDCModel.build_data(
            b_models, bones, boundmesh
        )

        # SUBSETS
        gmdc_data.subsets = gmdc_subset.GMDCSubset.build_data(
            b_models, bones, riggedbounds
        )

        return gmdc_data


    def load_data(self):
        # ELEMENTS
        count = self.data_read.read_int32()
        self.elements = []
        for i in range(0,count):
            temp_element = gmdc_element.GMDCElement()
            temp_element.read_data(self.data_read)
            self.elements.append(temp_element)

        # LINKAGES
        count = self.data_read.read_int32()
        self.linkages = []
        for i in range(0,count):
            temp_linkage = gmdc_linkage.GMDCLinkage()
            temp_linkage.read_data(self.data_read)
            self.linkages.append(temp_linkage)

        # GROUPS
        count = self.data_read.read_int32()
        self.groups = []
        for i in range(0,count):
            temp_group = gmdc_group.GMDCGroup()
            temp_group.read_data(self.data_read, self.header.version)
            self.groups.append(temp_group)

        # MODEL
        self.model = gmdc_model.GMDCModel()
        self.model.read_data(self.data_read)

        # SUBSETS
        count = self.data_read.read_int32()
        self.subsets = []
        for i in range(0,count):
            temp_subset = gmdc_subset.GMDCSubset()
            temp_subset.read_data(self.data_read)
            self.subsets.append(temp_subset)
