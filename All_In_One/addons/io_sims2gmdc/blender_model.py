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
from .element_id    import ElementID
from .morphmap      import MorphMap

class BlenderModel:

    def __init__(self, vertices, normals, tangents, faces, uvs, name,
                    bone_assign, bone_weight, opacity_amount, morphs,
                    morph_bytemap):
        self.name           = name
        self.vertices       = vertices
        self.normals        = normals
        self.tangents       = tangents
        self.faces          = faces
        self.uvs            = uvs
        self.bone_assign    = bone_assign
        self.bone_weight    = bone_weight
        self.opacity_amount = opacity_amount
        self.morphs         = morphs
        self.morph_bytemap  = morph_bytemap

    @staticmethod
    def groups_from_gmdc(gmdc_data):
        groups = []
        for g in gmdc_data.groups:
            # Load single group from a linkage

            # Get all linked elements
            element_indices = []
            for i in gmdc_data.linkages[g.link_index].indices:
                element_indices.append(i)
            groups.append(element_indices)

        models = []
        for i, element_indices in enumerate(groups):
            tmp_model = BlenderModel.from_gmdc(gmdc_data, element_indices, i)
            models.append(tmp_model)

        return models

    # Build the necessary data for blender from the gmdc data
    @staticmethod
    def from_gmdc(gmdc_data, element_indices, group_index):
        # Get all linked elements
        # elements = []
        # for link in gmdc_data.linkages:
        #     for ref in link.indices:
        #         elements.append(gmdc_data.elements[ref])
        # print(elements)

        vertices    = None
        uvs         = None
        normals     = None
        bone_assign = []
        bone_weight = []
        morphs      = []
        for ind in element_indices:
            # Vertices
            if gmdc_data.elements[ind].element_identity == ElementID.VERTICES:
                vertices = []
                for v in gmdc_data.elements[ind].element_values:
                    # Flip X and Y axis, Sims 2 has these reversed
                    values = (-v[0], -v[1], v[2])
                    vertices.append(values)

            # UV coordinates
            if gmdc_data.elements[ind].element_identity == ElementID.UV_COORDINATES:
                uvs = []
                for v in gmdc_data.elements[ind].element_values:
                    # Flip v value and add 1 to make it work in blender
                    uv_set = (v[0], -v[1] + 1)
                    uvs.append(uv_set)

            # Normals
            if gmdc_data.elements[ind].element_identity == ElementID.NORMALS_LIST:
                normals = []
                for v in gmdc_data.elements[ind].element_values:
                    # Flip X and Y axis, Sims 2 has these reversed
                    normal_set = (-v[0], -v[1], v[2])
                    normals.append(normal_set)

            # Bone Assignments
            if gmdc_data.elements[ind].element_identity == ElementID.BONE_ASSIGNMENTS:
                bone_assign = []
                testarr = []
                for v in gmdc_data.elements[ind].element_values:
                    temp_array = []
                    for num in v:
                        if num != 255:
                            # The true index of the bone, as stored in the group's
                            # Subset section.
                            truenum = gmdc_data.groups[group_index].subsets[num]
                            temp_array.append(truenum)
                    bone_assign.append(temp_array)

            # Bone Weights
            if gmdc_data.elements[ind].element_identity == ElementID.BONE_WEIGHTS:
                bone_weight = gmdc_data.elements[ind].element_values



        # Faces
        faces = []
        face_count = int(len(gmdc_data.groups[group_index].faces) / 3)
        for i in range(0,face_count):
            face = (
                gmdc_data.groups[group_index].faces[i*3 + 0],
                gmdc_data.groups[group_index].faces[i*3 + 1],
                gmdc_data.groups[group_index].faces[i*3 + 2]
            )
            faces.append(face)


        # Name and opacity
        name = gmdc_data.groups[group_index].name
        opacity_amount = gmdc_data.groups[group_index].opacity_amount


        # Morphs
        morphs = MorphMap.make_morphs(gmdc_data, group_index, element_indices)


        return BlenderModel(vertices, normals, None, faces, uvs, name,
                            bone_assign, bone_weight, opacity_amount,
                            morphs, None)
