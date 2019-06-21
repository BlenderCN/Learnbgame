##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

import bpy, math
from . import help_funcs
from mathutils import Vector, Color, Quaternion, Matrix


class BoundingBox:
    def __init__(self):
        self.center = 0
        self.unknown4 = 0.1460939
        self.corner1 = 0
        self.corner2 = 0

    def print_self(self):
        co1 = self.corner1
        co2 = self.corner2
        diag = math.sqrt((co1[0] - co2[0]) ** 2 + (co1[1] - co2[1]) ** 2 + (co1[2] - co2[2]) ** 2)
        help_funcs.PrintDeb(co1, co2, diag)


class PMGHeader:
    def __init__(self):
        self.version = 0
        self.no_models = 0
        self.no_sections = 0
        self.no_bones = 0
        self.no_dummies = 0
        self.mainBB = BoundingBox()
        self.bone_defs_offset = 0
        self.sections_offset = 0
        self.dummies_offset = 0
        self.models_offset = 0
        self.dummies_names_offset = 0
        self.dummies_names_size = 0
        self.bone_field_offset = 0
        self.bone_field_size = 0
        self.geometry_offset = 0
        self.geometry_size = 0
        self.uv_map_offset = 0
        self.uv_map_size = 0
        self.faces_offset = 0
        self.faces_size = 0

    def read_header(self, f):
        self.version = help_funcs.ReadUInt32(f)
        self.no_models = help_funcs.ReadUInt32(f)
        self.no_sections = help_funcs.ReadUInt32(f)
        self.no_bones = help_funcs.ReadUInt32(f)
        self.no_dummies = help_funcs.ReadUInt32(f)

        self.mainBB.center = help_funcs.ReadFloatVector(f)
        self.mainBB.unknown4 = help_funcs.ReadFloat(f)
        self.mainBB.corner1 = help_funcs.ReadFloatVector(f)
        self.mainBB.corner2 = help_funcs.ReadFloatVector(f)
        #self.mainBB.print_self()

        self.bone_defs_offset = help_funcs.ReadUInt32(f)
        self.sections_offset = help_funcs.ReadUInt32(f)
        self.dummies_offset = help_funcs.ReadUInt32(f)
        self.models_offset = help_funcs.ReadUInt32(f)
        self.dummies_names_offset = help_funcs.ReadUInt32(f)
        self.dummies_names_size = help_funcs.ReadUInt32(f)
        self.bone_field_offset = help_funcs.ReadUInt32(f)
        self.bone_field_size = help_funcs.ReadUInt32(f)
        self.geometry_offset = help_funcs.ReadUInt32(f)
        self.geometry_size = help_funcs.ReadUInt32(f)
        self.uv_map_offset = help_funcs.ReadUInt32(f)
        self.uv_map_size = help_funcs.ReadUInt32(f)
        self.faces_offset = help_funcs.ReadUInt32(f)
        self.faces_size = help_funcs.ReadUInt32(f)


class PMGVertex:
    def __init__(self, coord=(0.0, 0.0, 0.0)):
        self.co = coord #size 3
        self.direct = [] #size 3
        self.uv = [] #size 2
        self.col = 0 #size 4
        self.bones = []
        self.bones_weights = []

    def get_unique_vert_key(self):
        formatter = "%.4f"
        curr_key = ""
        for j in range(0, 3):
            curr_key += formatter % self.co[j]
            curr_key += formatter % self.direct[j]
            if j < 2:
                uv_indx = 0
                while uv_indx < len(self.uv):
                    curr_key += formatter % self.uv[uv_indx][j]
                    uv_indx += 1

        for bone in self.bones:
            curr_key = curr_key + " " + str(bone)

        #print(curr_key)
        return curr_key


class PMGModel:
    def __init__(self):
        self.name = "" #used for show name in blender
        self.no_faces = -1
        self.no_vertices = -1
        self.uvs_mask = -1
        self.uvs_count = -1
        self.no_bones_per_dic_entry = -1
        self.mat_idx = -1
        self.bbox = BoundingBox()
        self.vert_coord_offset = 0
        self.vert_direct_offset = 0
        self.vert_uv_offset = 0
        self.vert_color_offset = 0
        self.vert_color2_offset = 0
        self.vert_tangent_offset = 0
        self.faces_offset = 0
        self.bone_data_offset = 0
        self.bone_dic_offset = 0
        self.bone_weights_dic_offset = 0
        self.verts = []
        self.faces = []

    def read_header(self, f):

        self.no_faces = help_funcs.ReadUInt32(f) / 3
        self.no_vertices = help_funcs.ReadUInt32(f)
        self.uvs_mask = f.read(4)
        self.uvs_count = help_funcs.ReadUInt32(f)
        self.no_bones_per_dic_entry = help_funcs.ReadUInt32(f)
        self.mat_idx = help_funcs.ReadUInt32(f)

        self.bbox.center = help_funcs.ReadFloatVector(f)
        self.bbox.unknown4 = help_funcs.ReadFloat(f)
        self.bbox.corner1 = help_funcs.ReadFloatVector(f)
        self.bbox.corner2 = help_funcs.ReadFloatVector(f)
        #self.bbox.print_self()

        self.vert_coord_offset = help_funcs.ReadUInt32(f)
        self.vert_direct_offset = help_funcs.ReadUInt32(f)
        self.vert_uv_offset = help_funcs.ReadUInt32(f)
        self.vert_color_offset = help_funcs.ReadUInt32(f)
        self.vert_color2_offset = help_funcs.ReadUInt32(f)
        self.vert_tangent_offset = help_funcs.ReadUInt32(f)
        self.faces_offset = help_funcs.ReadUInt32(f)
        self.bone_data_offset = help_funcs.ReadUInt32(f)
        self.bone_dic_offset = help_funcs.ReadUInt32(f)
        self.bone_weights_dic_offset = help_funcs.ReadUInt32(f)

    def read_verts(self, f, version):
        if version & 0xff == 18:
            self.__read_verts_v1_3_1(f)
        elif version & 0xff == 19:
            self.__read_verts_v1_4_x(f)

    def __read_verts_v1_4_x(self, f):
        f.seek(self.vert_coord_offset)
        i = 0
        while i < self.no_vertices:
            vertex = PMGVertex(help_funcs.ReadFloatVector(f))
            vertex.direct = help_funcs.ReadFloatVector(f)

            if self.vert_tangent_offset != 0xffffffff:
                help_funcs.ReadFloatVector4(f)

            #if model has bones read only loc, direct and tangents
            if self.no_bones_per_dic_entry > 0:
                i += 1
                self.verts.append(vertex)
                continue

            self.__read_colors_and_uv_v1_4_1(vertex, f)
            self.verts.append(vertex)
            i += 1

        if self.no_bones_per_dic_entry > 0:
            f.seek(self.vert_color_offset)
            i = 0
            while i < self.no_vertices:
                vertex = self.verts[i]
                self.__read_colors_and_uv_v1_4_1(vertex, f)
                i += 1

    def __read_colors_and_uv_v1_4_1(self, vertex, f):
        vertex.col = help_funcs.ReadCharVector4(f)

        if self.vert_color2_offset != 0xffffffff:
            vertex.col2 = help_funcs.ReadCharVector4(f)

        uv_indx = 0
        while uv_indx < self.uvs_count:
            uv = help_funcs.ReadFloatVector2(f)
            #convert uv mapping to blender mappings
            uv = (uv[0], -uv[1] + 1)
            vertex.uv.append(uv)
            uv_indx += 1

    def __read_verts_v1_3_1(self, f):
        f.seek(self.vert_coord_offset)
        i = 0
        while i < self.no_vertices:
            self.verts.append(PMGVertex(help_funcs.ReadFloatVector(f)))
            i += 1
        f.seek(self.vert_direct_offset)
        i = 0
        while i < self.no_vertices:
            self.verts[i].direct = help_funcs.ReadFloatVector(f)
            i += 1
        f.seek(self.vert_uv_offset)
        i = 0
        while i < self.no_vertices:
            uv = help_funcs.ReadFloatVector2(f)
            #convert uv mapping to blender mappings
            uv = (uv[0], -uv[1] + 1)
            self.verts[i].uv.append(uv)
            i += 1
            #check for additional uv
        if self.uvs_count == 2:
            i = 0
            while i < self.no_vertices:
                uv = help_funcs.ReadFloatVector2(f)
                #convert uv mapping to blender mappings
                uv = (uv[0], -uv[1] + 1)
                self.verts[i].uv.append(uv)
                i += 1
                #help_funcs.PrintDeb("2UVs - Expected file pos:",
                #        self.vert_uv_offset+self.no_vertices*4*2*2, "Actuall pos:", f.tell())
        else:
            pass
            #help_funcs.PrintDeb("Expected file pos:", 
            #        self.vert_uv_offset+self.no_vertices*4*2, "Actuall pos:", f.tell())

        f.seek(self.vert_color_offset)
        i = 0
        while i < self.no_vertices:
            self.verts[i].col = help_funcs.ReadCharVector4(f)
            i += 1

    def read_faces(self, f):
        f.seek(self.faces_offset)
        i = 0
        while i < self.no_faces:
            self.faces.append(help_funcs.ReadUInt16Vector(f))
            i += 1

    def read_bones_data(self, f):
        #read dictionary of bones per vertex combinations from file
        bone_anims_dic = {}
        bone_anims_weights_dic = {}
        f.seek(self.bone_dic_offset)
        bone_dic_indx = 0
        while f.tell() < self.bone_weights_dic_offset:
            j = 0
            curr_bones_l = []
            while j < self.no_bones_per_dic_entry:
                curr_bone = help_funcs.ReadChar(f)
                if curr_bone != 0xff: #if 0xff that means no bone for current combination
                    curr_bones_l.append(curr_bone)
                j += 1
            bone_anims_dic[bone_dic_indx] = curr_bones_l
            bone_dic_indx += 1
        if f.tell() != self.bone_weights_dic_offset:
            help_funcs.PrintDeb("Bone data reading under/overflow! import_pmg.py:267")
            #print("Checking file pos:", f.tell(), "/", self.bone_dic_count_offset)

        #read weights for all dictionary entries
        f.seek(self.bone_weights_dic_offset)
        bone_dic_size = bone_dic_indx
        bone_dic_indx = 0
        while bone_dic_indx < bone_dic_size:
            j = 0
            curr_bone_w_l = []
            while j < self.no_bones_per_dic_entry:
                curr_weight = help_funcs.ReadChar(f) / 255.0
                curr_bone_w_l.append(curr_weight)
                j += 1
            bone_anims_weights_dic[bone_dic_indx] = curr_bone_w_l
            bone_dic_indx += 1

        #apply readed data to PMGVertex objects
        if len(bone_anims_dic.keys()) > 0:
            #for each vertex get bones indexes from dictionary
            f.seek(self.bone_data_offset)
            i = 0
            while i < self.no_vertices:
                dict_indx = help_funcs.ReadUInt16(f)
                vertex = self.verts[i]
                #add bones to vertex from bone_anims_dic on given index
                for j in range(0, len(bone_anims_dic[dict_indx])):
                    bone_indx = bone_anims_dic[dict_indx][j]
                    weight = bone_anims_weights_dic[dict_indx][j]
                    if bone_indx not in vertex.bones:
                        vertex.bones.append(bone_indx)
                        vertex.bones_weights.append(weight)
                i += 1
            if f.tell() != self.bone_dic_offset:
                help_funcs.PrintDeb("Bone data reading under/overflow! import_pmg.py:281")
                #print("Checking file pos:", f.tell(), "/", self.bone_dic_offset)


    def draw_model(self, postfix, parent_ob, bones_data, optimize, stat_counters):
        """Draws model from verts and faces data 
        postfix - number of model used for model name
        parent_ob - parent section object to which models should be added
        bones_data - readed data about bones of SCS model
        optimize - tells if vertices with same characteristics should be merged (same co, normal, uvs)"""

        me = bpy.data.meshes.new("MeshModel" + postfix)
        ob = bpy.data.objects.new("Model" + postfix, me)
        self.name = ob.name
        ob["mat_indx"] = self.mat_idx

        #create object from vertices and faces data        
        ob.location = Vector()
        bpy.context.scene.objects.link(ob)
        ob.parent = parent_ob
        coords = []
        verts_dupl_dict = {}
        verts_mapping_dict = {}
        origin_mapping_dict = {}
        merged_verts_count = 0
        i = 0
        while i < self.no_vertices:
            curr_key = self.verts[i].get_unique_vert_key()
            #print("Curr key:", curr_key)
            if optimize and curr_key in verts_dupl_dict:
                verts_mapping_dict[i] = verts_dupl_dict[curr_key]
                merged_verts_count += 1
            else:
                verts_dupl_dict[curr_key] = len(coords)
                verts_mapping_dict[i] = len(coords)
                origin_mapping_dict[len(coords)] = i
                #converts verts coordinates to blender coordinate system
                self.verts[i].co = ( -self.verts[i].co[0],
                                     self.verts[i].co[1],
                                     -self.verts[i].co[2])
                coords.append(self.verts[i].co)
            i += 1
        faces = []
        faces_dic = {}
        duplicates_count = 0
        fake_faces_count = 0
        i = 0
        while i < self.no_faces:
            #convert faces to blender so that order is switched
            face = list(self.faces[i][::-1])
            for j in range(0, len(face)):
                face[j] = verts_mapping_dict[face[j]]

            if face[0] == face[1] or face[1] == face[2] or face[0] == face[2]:
                fake_faces_count += 1
                i += 1
                continue

            if str(face) in faces_dic:
                duplicates_count += 1
            else:
                faces_dic[str(face)] = 1
                faces.append(tuple(face))
            i += 1

        me.from_pydata(coords, [], faces)
        me.update()


        #set vertex color
        col_map = ob.data.vertex_colors.new()
        if self.vert_color2_offset != 0xffffffff:
            col_map2 = ob.data.vertex_colors.new()

        i = 0
        for p in me.polygons:
            #use smooth shading
            p.use_smooth = True
            for idx in p.loop_indices:
                v = ob.data.loops[idx].vertex_index
                v = origin_mapping_dict[v]

                colV = self.verts[v].col
                col = Color((colV[0] / 255.0, colV[1] / 255.0, colV[2] / 255.0))
                col_map.data[i].color = col

                if 'col_map2' in locals():
                    colV = self.verts[v].col2
                    col = Color((colV[0] / 255.0, colV[1] / 255.0, colV[2] / 255.0))
                    col_map2.data[i].color = col

                i += 1

        #add uv maps
        uv_indx = 0
        while uv_indx < self.uvs_count:
            self.add_uv(ob, me, origin_mapping_dict)
            uv_indx += 1

        if len(bones_data) > 0:
            #add vertex groups for bones on current model
            verts_bone_map = {}
            verts_bone_w_map = {}
            i = 0
            while i < self.no_vertices:
                vertex = self.verts[i]
                for j in range(0, len(vertex.bones)):
                    bone_indx = vertex.bones[j]
                    for bone_data in bones_data:
                        if bone_data.bone_indx == bone_indx:
                            #bone = "scs_bones:"+str(bone)
                            bone_indx = bone_data.name
                            #add vertex group for current bone if not yet created
                            if bone_indx not in verts_bone_map.keys():
                                verts_bone_map[bone_indx] = []
                                verts_bone_w_map[bone_indx] = []
                            verts_bone_map[bone_indx].append(verts_mapping_dict[i])
                            #add bone weight from curetn vertex
                            verts_bone_w_map[bone_indx].append(vertex.bones_weights[j])
                            break
                i += 1
                #add vertex an it's weight to vertex group
            for bone_indx in verts_bone_map.keys():
                ob.vertex_groups.new(bone_indx)
                for i in range(0, len(verts_bone_map[bone_indx])):
                    #vertex_groups[bone_indx] can be used because blender preserve
                    #order of appending new vertex groups
                    ob.vertex_groups[bone_indx].add([verts_bone_map[bone_indx][i]],
                                                    verts_bone_w_map[bone_indx][i], 'ADD')


            #add armature modifier
            modif = ob.modifiers.new("SCS_armature", 'ARMATURE')
            modif.object = bpy.data.objects["anim_armature_object"]

        stat_counters[0] += duplicates_count
        stat_counters[1] += fake_faces_count
        stat_counters[2] += merged_verts_count
        stat_counters[3] += 1
        out_stat_str = "\r" + str(stat_counters[3]) + "/" + str(stat_counters[4]) + " done: [" + str(
            stat_counters[0]) + "] double & [" + str(stat_counters[
            1]) + "] fake faces; [" + str(stat_counters[2]) + "] double verts"
        help_funcs.PrintDeb(out_stat_str, end="")

        #remove nested vertices if there are any because of merging
        #remove this kinda problem in game:
        #00:00:38.605 : [dx9] [render_item]     0 vtx/    0 idx, mat /vehicle/trailer_eu/tes2/materials/6357cab4480892baac3f73a299f38852090b51.mat
        # - [fx /effect/eut2/lamp/eut2.lamp.add.env.rfx, bias 0] (tx /vehicle/trailer_eu/tes2/textures/aero_dynamic_001.tobj
        # - /vehicle/trailer_eu/tes2/textures/lamp_mask.tobj)
        ob.select = True
        bpy.ops.object.scs_remove_nested_vertices()
        ob.select = False

        return ob

    def add_uv(self, object, mesh, verts_mapping_dict):
        """Adds new UV layer to object
        object - object where uv should be added
        mesh - mesh of drawing object
        verts_mapping_dict - dictionary of vertices mapping"""
        object.data.uv_textures.new()
        n_lay = len(object.data.uv_layers) - 1
        uv_map = object.data.uv_layers[n_lay]
        i = 0
        for p in mesh.polygons:
            for idx in p.loop_indices:
                v = object.data.loops[idx].vertex_index
                v = verts_mapping_dict[v]
                uv_map.data[i].uv = self.verts[v].uv[n_lay]
                i += 1


class PMGDummy:
    """
    Class for storing dummies data
    """

    def __init__(self):
        self.name = 0
        self.co = 0
        self.unkn_const = 0
        self.rot = []
        self.name_blck_offset = 0
        self.name_data = ""

    def read_header(self, f):
        self.name = help_funcs.ReadUInt64(f)
        self.co = help_funcs.ReadFloatVector(f)
        self.unkn_const = help_funcs.ReadFloat(f)
        self.rot = help_funcs.ReadFloatQuaternion(f)
        self.name_blck_offset = help_funcs.ReadUInt32(f)

    def set_name_data(self, name):
        self.name_data = name

    def draw_dummy(self, parent_ob):
        #convert rotation and location to blender coo system
        self.co = (-self.co[0], self.co[1], -self.co[2])
        rot = Quaternion((self.rot[0], -self.rot[1], self.rot[2], -self.rot[3]))
        if len(self.name_data) == 0:
            ty = 'CUBE'
            d_size = 0.05
        else:
            ty = 'ARROWS'
            d_size = 0.1
        bpy.ops.object.empty_add(type=ty, location=self.co)
        dummy_ob = bpy.context.object
        dummy_ob.rotation_mode = 'QUATERNION'
        dummy_ob.rotation_quaternion = rot
        dummy_ob.empty_draw_size = d_size
        dummy_ob.name = help_funcs.DecodeNameCRC(self.name) + '[' + self.name_data + ']'
        dummy_ob.parent = parent_ob


class PMGSection:
    """
    Class for storing pmg section data
    """

    def __init__(self):
        self.name = 0
        self.no_models = 0
        self.unkwnown4 = 0
        self.no_dummies = 0
        self.unknown6 = 0
        self.first_m = 0
        self.last_m = 0
        self.first_d = 0
        self.last_d = 0

    def read_header(self, f, model_idx, dummy_idx):
        self.name = help_funcs.ReadUInt64(f)
        self.no_models = help_funcs.ReadUInt32(f)
        self.unkwnown4 = help_funcs.ReadUInt32(f)
        self.no_dummies = help_funcs.ReadUInt32(f)
        self.unknown6 = help_funcs.ReadUInt32(f)
        self.first_m = model_idx
        self.last_m = model_idx + self.no_models
        self.first_d = dummy_idx
        self.last_d = dummy_idx + self.no_dummies

    def draw_section(self, index, models, dummies, bones, parent_ob, optimize, stat_counters):
        bpy.ops.object.empty_add(type='CUBE', location=Vector())
        section_ob = bpy.context.object
        section_ob.empty_draw_size = 0.1
        section_ob.name = help_funcs.DecodeNameCRC(self.name)
        section_ob.parent = parent_ob
        i = 0
        model_objs = []
        for model in models[self.first_m:self.last_m]:
            model_objs.append(model.draw_model(str(index) + '.' + str(i), section_ob, bones, optimize, stat_counters))
            i += 1
        for dummy in dummies[self.first_d:self.last_d]:
            dummy.draw_dummy(section_ob)
        return model_objs


class PMGBoneDef:
    """
    Class for storing pmg bones definition
    """

    def __init__(self):
        self.name = 0
        self.transf_mat = Matrix()
        self.transf_inv_mat = Matrix()
        self.stretch_quat = None
        self.rot_quat = None
        self.trans_vec = None
        self.scale_vec = None
        self.mat_det_sign = 0
        self.parent = 255
        self.bone_indx = 0

    def read_header(self, f, bone_indx):
        self.bone_indx = bone_indx
        self.name = help_funcs.DecodeNameCRC(help_funcs.ReadUInt64(f))
        for i in range(0, 4):
            self.transf_mat[i].xyzw = help_funcs.ReadFloatVector4(f)
        for i in range(0, 4):
            self.transf_inv_mat[i].xyzw = help_funcs.ReadFloatVector4(f)
        self.stretch_quat = Quaternion(help_funcs.ReadFloatVector4(f))
        self.rot_quat = Quaternion(help_funcs.ReadFloatVector4(f))
        self.trans_vec = Vector(help_funcs.ReadFloatVector(f))
        self.scale_vec = Vector(help_funcs.ReadFloatVector(f))
        self.mat_det_sign = help_funcs.ReadFloat(f)
        self.parent = help_funcs.ReadUInt32(f)

    def draw_bone(self, parent_bone):
        bpy.ops.armature.bone_primitive_add(name=self.name)
        curr_bone = bpy.context.object.data.edit_bones[self.name]

        curr_bone["scs_b_transf_mat"] = self.transf_mat
        #curr_bone["scs_b_transf_inv_mat"] = self.transf_inv_mat
        curr_bone["scs_b_stretch_quat"] = self.stretch_quat
        curr_bone["scs_b_rot_quat"] = self.rot_quat
        curr_bone["scs_b_trans_vec"] = self.trans_vec
        curr_bone["scs_b_scale_vec"] = self.scale_vec
        curr_bone["scs_b_mat_det_sign"] = self.mat_det_sign
        #TODO needed as long as I don't export pma by myself
        curr_bone["scs_b_indx"] = self.bone_indx
        curr_bone["scs_b_parent"] = self.parent

        trans = self.trans_vec
        #convert translation to Blender coordinate system
        trans.x = -trans.x
        trans.z = -trans.z
        if parent_bone is not None:
            trans += parent_bone.head
        curr_bone.head = trans
        curr_bone.tail = curr_bone.head + Vector((0.0, 0.1, 0.0))

        if parent_bone is not None:
            #make parent with parent_bone
            bpy.ops.armature.select_all(action='DESELECT')
            curr_bone.select = True
            parent_bone.select = True
            bpy.context.object.data.edit_bones.active = parent_bone
            bpy.ops.armature.parent_set(type='OFFSET')

        return curr_bone


class PMG:
    """
    Class for storing all pmg data
    """

    def __init__(self, f):
        self.header = PMGHeader()
        self.header.read_header(f)
        self.models = self.__read_models(f)
        self.sections = self.__read_sections(f)
        self.dummies = self.__read_dummies(f)
        self.bones = self.__read_bone_defs(f)

    def __read_models(self, f):
        f.seek(self.header.models_offset)
        i = 0
        ret = []
        help_funcs.PrintDeb("Loading model headers...", end=" -> ")
        while i < self.header.no_models:
            curr_m = PMGModel()
            curr_m.read_header(f)
            ret.append(curr_m)
            i += 1
        help_funcs.PrintDeb("Done!")
        i = 0
        help_funcs.PrintDeb("Reading model vertices...", end=" -> ")
        while i < self.header.no_models:
            ret[i].read_verts(f, self.header.version)
            i += 1
        help_funcs.PrintDeb("Done!")
        i = 0
        help_funcs.PrintDeb("Reading model faces...", end=" -> ")
        while i < self.header.no_models:
            ret[i].read_faces(f)
            i += 1
        help_funcs.PrintDeb("Done!")
        i = 0
        help_funcs.PrintDeb("Reading model bones...", end=" -> ")
        while i < self.header.no_models:
            ret[i].read_bones_data(f)
            i += 1
        help_funcs.PrintDeb("Done!")
        return ret

    def __read_dummies(self, f):
        f.seek(self.header.dummies_offset)
        i = 0
        ret = []
        help_funcs.PrintDeb("Loading dummies...", end=" -> ")
        while i < self.header.no_dummies:
            curr_d = PMGDummy()
            curr_d.read_header(f)
            ret.append(curr_d)
            i += 1
        help_funcs.PrintDeb("Done!")
        i = 0
        help_funcs.PrintDeb("Getting dummies names data...", end=" -> ")
        while i < self.header.no_dummies:
            f.seek(ret[i].name_blck_offset + self.header.dummies_names_offset)
            val = help_funcs.ReadChar(f)
            name = ""
            while val != 0:
                name += chr(val)
                val = help_funcs.ReadChar(f)
            ret[i].set_name_data(name)
            i += 1
        help_funcs.PrintDeb("Done!")
        return ret

    def __read_sections(self, f):
        f.seek(self.header.sections_offset)
        i = 0
        ret = []
        model_i = 0
        dummy_i = 0
        help_funcs.PrintDeb("Loading sections...", end=" -> ")
        while i < self.header.no_sections:
            curr_s = PMGSection()
            curr_s.read_header(f, model_i, dummy_i)
            model_i = curr_s.last_m
            dummy_i = curr_s.last_d
            ret.append(curr_s)
            i += 1
        help_funcs.PrintDeb("Done!")
        return ret

    def __read_bone_defs(self, f):
        f.seek(self.header.bone_defs_offset)
        help_funcs.PrintDeb("Loading bones definitions...", end=" -> ")
        i = 0
        ret = []
        while i < self.header.no_bones:
            curr_a = PMGBoneDef()
            curr_a.read_header(f, i)
            ret.append(curr_a)
            i += 1

        if f.tell() != self.header.bone_defs_offset + self.header.no_bones * 200:
            help_funcs.PrintDeb("Bone definitions reading under/overflow! import_pmg.py:597")
            #help_funcs.PrintDeb("Checking position: ",
        #                    f.tell(), 
        #                    self.header.bone_defs_offset+
        #                    self.header.no_bones*200)
        help_funcs.PrintDeb("Done!")
        return ret

    def draw_model(self, name, optimize):
        #create root empty
        bpy.ops.object.empty_add(type='CUBE', location=Vector())
        pmg_ob = bpy.context.active_object
        pmg_ob.empty_draw_size = 0.1
        pmg_ob.name = name
        #TODO be aware of this rotation
        pmg_ob.rotation_euler.x = 90.0 * math.pi / 180

        help_funcs.PrintDeb("Creating and drawing bones in blender...", end=" -> ")
        if self.header.no_bones > 0:
            #create bones armature object
            bpy.ops.object.armature_add(location=Vector())
            bone_root = bpy.context.object
            bone_root.parent = pmg_ob
            bone_root.name = "anim_armature_object"
            bone_root.data.name = "anim_armature"
            bone_root.data.draw_type = 'STICK'

            #clear all the default bones
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            i = 0
            added_bones = {}
            while i < self.header.no_bones:
                curr_a = self.bones[i]
                if curr_a.parent == 255:
                    added_bones[curr_a.bone_indx] = curr_a.draw_bone(None)
                else:
                    if curr_a.parent in added_bones:
                        added_bones[curr_a.bone_indx] = curr_a.draw_bone(added_bones[curr_a.parent])
                    else:
                        help_funcs.PrintDeb("\nWarning: Incorrectly written bone data! Bone with name \"", curr_a.name,
                                            "\" has wrong parent index:", curr_a.parent, "\n")
                        #fallback to rescue mode with wrong bones data
                        curr_a.parent = 255
                        if curr_a.name != "" and curr_a.name is not None:
                            added_bones[curr_a.bone_indx] = curr_a.draw_bone(None)
                i += 1


            #apply rotation and scale transformations on bones
            bpy.ops.object.mode_set(mode='POSE')
            for bone in bpy.data.objects["anim_armature_object"].pose.bones:
                bone_origin = bpy.data.armatures["anim_armature"].bones[bone.name]
                if "scs_b_rot_quat" in bone_origin:
                    rot_vec = Quaternion(bone_origin["scs_b_rot_quat"])
                    #convert to Blender coordinate system
                    rot_vec.x = -rot_vec.x
                    rot_vec.z = -rot_vec.z
                    bone.rotation_quaternion = rot_vec
                    bone.scale = Vector(bone_origin["scs_b_scale_vec"])
                # del bone_origin["scs_b_rot_quat"]
                # del bone_origin["scs_b_scale_vec"]
                # del bone_origin["scs_b_stretch_quat"]
                # del bone_origin["scs_b_trans_vec"]
                # del bone_origin["scs_b_transf_mat"]
            bpy.ops.pose.armature_apply()

            #normalize tails of bones if they got bigger because of scale
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in bpy.context.object.data.edit_bones:
                bpy.ops.armature.select_all(action='DESELECT')
                bone.select_tail = True
                scale = 0.1 / (bone.head - bone.tail).magnitude
                bpy.ops.transform.resize(value=(scale, scale, scale), constraint_orientation='LOCAL')

            # #TODO: work on sclaes!!
            # for bone in bpy.data.objects["anim_armature_object"].pose.bones:
            #     bone_origin = bpy.data.armatures["anim_armature"].bones[bone.name]
            #     if "scs_b_scale_vec" in bone_origin:
            #         bone.scale = Vector(bone_origin["scs_b_scale_vec"])

            bpy.ops.object.mode_set(mode='OBJECT')

        help_funcs.PrintDeb("Done!\nCreating and drawing model in blender:\n")
        i = 0
        models_objs = []
        stat_counters = [0, 0, 0, 0, len(self.models)]
        while i < self.header.no_sections:
            models_objs += self.sections[i].draw_section(i, self.models, self.dummies, self.bones, pmg_ob, optimize,
                                                         stat_counters)
            i += 1

        help_funcs.PrintDeb(" > Done!\n")

        return pmg_ob


def load(filepath):
    help_funcs.PrintDeb("\nImporting PMG -----------------\n")
    with open(filepath, 'rb') as f:
        pmg_version = help_funcs.ReadUInt32(f)
        if (pmg_version == 1349347090 or
                    pmg_version == 1349347091):
            f.seek(0)
            pmg = PMG(f)
        else:
            return None
    return pmg

    '''
    print("Saving pickle...")
    with open("E:\data.dump", "wb") as output:
        import pickle
        pickle.dump(pmg, output, pickle.HIGHEST_PROTOCOL)
    
    print("Loading pickle...")
    pmg_loaded = 0
    with open("E:\data.dump", "rb") as input:
        import pickle
        pmg_loaded = pickle.load(input)
    
    pmg_loaded.draw_model("truck")
    '''
    