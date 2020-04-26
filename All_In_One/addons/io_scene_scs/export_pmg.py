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

import bpy, math, time
from . import help_funcs
from mathutils import Vector, Matrix, Quaternion

###############################################
#
# Base classes for pmg exporting
#
###############################################

class BoundingBox:
    def __init__(self, corner1, corner2):
        """
        corner1 - minimal corner of bounding box
        corner2 - maximal corner of bounding box
        """
        if corner1 is None:
            corner1 = (0,0,0)
        if corner2 is None:
            corner2 = (0,0,0)

        self.__corner1=corner1
        self.__corner2=corner2
        c1 = self.__corner1
        c2 = self.__corner2
        self.__center = ((c1[0]+c2[0])/2, (c1[1]+c2[1])/2, (c1[2]+c2[2])/2)
        self.__diag_size = math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2+(c1[2]-c2[2])**2)/2

    def to_scs_bytes(self):
        bytes = help_funcs.FloatVecToByts(self.__center)
        bytes += help_funcs.FloatToByts(self.__diag_size)
        bytes += help_funcs.FloatVecToByts(self.__corner1)
        bytes += help_funcs.FloatVecToByts(self.__corner2)
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())



class PMGVertex:
    def __init__(self, co, normal):
        """
        co - location of vertex: (x,y,z)
        normal - normals of vertex: (x,y,z)
        uvs - tuples of uv coordinates, example 2uvs: ((u1,v1),(u2,v2))
        color - vertex color given in tuple: (r,g,b,a)
        """
        self.__loc = co
        self.__normal = normal
        self.__uvs = []
        self.__uvs_masks = []
        self.__color = None
        self.__tangent = None
        self.__bone_dic_indx = None

    def get_normal(self):
        return Vector(self.__normal)

    def set_color(self, color):
        """
        color - tuple of vertex color: (r,g,b,a)
        """
        self.__color = (int(color[0]),int(color[1]),int(color[2]),int(color[3]))

    def set_tangent(self, tangent):
        """
        tangent - tuple of 4d tangent vector: (x,y,z,w)
        """
        self.__tangent = (tangent.x, tangent.y, tangent.z, tangent.w)

    def set_bone_dic_indx(self, indx):
        """
        indx - integer index for bones indexes dictionary
        """
        self.__bone_dic_indx = indx

    def add_uv(self, uv):
        """
        uv - tuple of uv coordinates, example: (u1,v1)
        """
        self.__uvs.append(uv)

    def to_scs_bytes(self, attr, indx = -1):
        """
        attr - tells what attribute needs to be returned: 
               ('COORD', 'NORMAL', 'UV', 'COL', 'TANGENT', BONE_INDX')
        indx - tells which index of given attribute will be read
        """
        bytes = b''
        if attr == 'COORD':
            bytes = help_funcs.FloatVecToByts(self.__loc)
        elif attr == 'NORMAL':
            bytes = help_funcs.FloatVecToByts(self.__normal)
        elif attr == 'UV':
            if len(self.__uvs) > indx:
                bytes = help_funcs.FloatVec2ToByts(self.__uvs[indx])
            else:
                bytes = help_funcs.FloatVec2ToByts((0,0))
        elif attr == 'COL':
            bytes = help_funcs.CharVec4ToByts(self.__color)
        elif attr == 'TANGENT':
            if self.__tangent is not None:
                bytes = help_funcs.FloatQuatToByts(self.__tangent)
        elif attr == 'BONES_DIC_INDX':
            if self.__bone_dic_indx is not None:
                bytes = help_funcs.CharToByts(self.__bone_dic_indx)
        return bytes

    def bytes_len(self):
        bytes = b''
        bytes += self.to_scs_bytes('COORD')
        bytes += self.to_scs_bytes('NORMAL')
        uv_indx = 0
        while uv_indx < len(self.__uvs):
            bytes += self.to_scs_bytes('UV', uv_indx)
            uv_indx+=1
        bytes += self.to_scs_bytes('COL')
        bytes += self.to_scs_bytes('TANGENT')
        bytes += self.to_scs_bytes('BONES_DIC_INDX')
        return len(bytes)



class PMGFace:
    def __init__(self, links):
        """
        links - vertices indexes which defines face: (v1,v2,v3)
        """
        self.__links = links
    def to_scs_bytes(self):
        return help_funcs.UInt16VecToByts(self.__links)

    def bytes_len(self):
        return len(self.to_scs_bytes())





###############################################
#
# Base classes for definitions in pmg
#
###############################################
class PMGSection:
    def __init__(self, name, no_models, m_start_idx,
            no_dummies, d_start_idx):
        """
        name - name of section (max length 12)
        no_models - how many models are in this section
        m_start_idx - index of first model in models array
        no_dummies - how many dummies are in this section
        d_start_idx - index of first dummy in dummies array
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())
        self.__no_models = no_models
        self.__m_s_idx = m_start_idx
        self.__no_dummies = no_dummies
        self.__d_s_idx = d_start_idx

    def to_scs_bytes(self):
        bytes = help_funcs.UInt64ToByts(self.__name)
        bytes += help_funcs.UInt32ToByts(self.__no_models)
        bytes += help_funcs.UInt32ToByts(self.__m_s_idx)
        bytes += help_funcs.UInt32ToByts(self.__no_dummies)
        bytes += help_funcs.UInt32ToByts(self.__d_s_idx)
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())

class PMGBone:
    def __init__(self, name="", transf_mat=Matrix(), rot_quat=Quaternion(),
                trans_vec=Vector(), scale_vec=Vector((1.0,1.0,1.0)), mat_det_sign=0,
                stretch_quat=Quaternion((1.0,0.0,0.0,0.0)), parent=255, bone_indx=0):
        """
        name - name of bone (max length 12)
        transf_mat - transformation matrix
        rot_quat - rotation quaternion
        trans_vec - translation vector
        scale_vec - scale vector
        mat_det_sign - sign of matrix determinant
        stretch_quat - stretch quaterinon
        parent - index of parent bone (default 255 which is no parent)
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())
        self.__transf_mat = transf_mat
        self.__rot_quat = rot_quat
        self.__trans_vec = trans_vec
        self.__scale_vec = scale_vec
        self.__mat_det_sign = mat_det_sign
        self.__stretch_quat = stretch_quat
        self.__parent = parent

        #TODO delete when PMA supported
        self.bone_indx = bone_indx
        self.name = name

    def to_scs_bytes(self):
        bytes = help_funcs.UInt64ToByts(self.__name)
        for i in range(0, 4):
            bytes += help_funcs.FloatQuatToByts(self.__transf_mat.row[i])
        inv_mat = self.__transf_mat.inverted()
        for i in range(0, 4):
            bytes += help_funcs.FloatQuatToByts(inv_mat.row[i])
        bytes += help_funcs.FloatQuatToByts(self.__stretch_quat)
        bytes += help_funcs.FloatQuatToByts(self.__rot_quat)
        bytes += help_funcs.FloatVecToByts(self.__trans_vec)
        bytes += help_funcs.FloatVecToByts(self.__scale_vec)
        bytes += help_funcs.FloatToByts(self.__mat_det_sign)
        bytes += help_funcs.UInt32ToByts(self.__parent)
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())

class PMGDummy:
    def __init__(self, name="", loc=(0,0,0), rot=(0,0,0,0), offset=-1):
        """
        name - name of dummy (max length 12)
        loc - position coordinates of dummy
        rot - quaternion rotation of dummy
        offset - offset of dummy "flare" in names block
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())
        self.__loc = loc
        self.__rot = rot
        self.__offset = offset

    def to_scs_bytes(self):
        bytes = help_funcs.UInt64ToByts(self.__name)
        bytes += help_funcs.FloatVecToByts(self.__loc)
        bytes += help_funcs.FloatToByts(1)
        bytes += help_funcs.FloatQuatToByts(self.__rot)
        bytes += help_funcs.Int32ToByts(self.__offset)
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())


class PMGModel:

    @staticmethod
    def __get_uvs_mask(no_uvs, mat_shader_name):
        """
        Depending on number of uvs and material shader name create mask property
        no_uvs - number of uv layers in model
        mat_shader_name - name of shader from which mask should be extracted
        """
        uv_mask = None

        if mat_shader_name is not None:
            if "tsnmapuv16" in mat_shader_name:
                if no_uvs == 3:
                    uv_mask = b'\x10\xf2\xff\xf0'
            elif "tsnmapuv" in mat_shader_name:
                if no_uvs == 2:
                    uv_mask = b'\xf0\xff\xff\xf1'
                elif no_uvs == 1:
                    uv_mask = b'\xf0\xff\xff\xf0'
            elif mat_shader_name in [   "eut2.truckpaint.airbrush",
                                        "eut2.truckpaint.altuv",
                                        "eut2.truckpaint.flipflake.altuv"]:
                if no_uvs == 2:
                    uv_mask = b'\x10\xf0\xff\xff'
            elif mat_shader_name in [   "eut2.dif.weight.dif",
                                        "eut2.lamp",
                                        "eut2.sky",
                                        "eut2.sky.over" ]:
                uv_mask = b'\x00\xff\xff\xff'
            elif mat_shader_name in [   "eut2.dif.spec.mult.dif.spec.iamod.dif.spec" ]:
                if no_uvs == 1:
                    uv_mask = b'\x00\xf0\xff\xff'
                elif no_uvs == 2:
                    uv_mask = b'\x10\xf1\xff\xff'
                elif no_uvs == 3:
                    uv_mask = b'\x10\xf2\xff\xff'
            elif mat_shader_name in [   "eut2.dif.spec.weight.weight.dif.spec.weight",
                                        "eut2.dif.spec.weight.weight.dif.spec.weight.tg0.tg1",
                                        "eut2.dif.spec.weight.weight.dif.spec.weight.tg1",
                                        "eut2.dif.weight.dif.tg0"]:
                if no_uvs == 1:
                    uv_mask = b'\x00\xff\xff\xff'

        # fallback to standard flags common to rest of used effects by SCS
        if uv_mask is None:
            if no_uvs == 1:
                uv_mask = b'\xf0\xff\xff\xff'
            elif no_uvs == 2:
                uv_mask = b'\x10\xff\xff\xff'
            elif no_uvs == 3:
                uv_mask = b'\x10\xf2\xff\xff'
            else:
                uv_mask = b'\xff\xff\xff\xff'

        return uv_mask

    def __init__(self, bbox, no_polys, no_verts, no_uvs, mat_shader_name,
            mat_idx, calc_tan):
        """
        bbox - bounding box of model
        no_polys - number of triangles in model
        no_verts - number of vertices in model
        mat_shader_name - name of shader used on the model
        no_uvs - number of uvs on model
        mat_idx - index of material
        calc_tan - flag indicating need to calculate tangents
        """
        self.__no_polys=no_polys
        self.__no_verts=no_verts
        self.__no_uvs=no_uvs
        self.__uvs_mask=self.__get_uvs_mask(self.__no_uvs, mat_shader_name)
        self.__bones_per_dic_entry=0
        self.__mat_idx=mat_idx
        self.__bbox=bbox
        #verts_offset - offsets to vertices data, must include offsets
        #in order: coord, normal, uv, color, unknown11ff, tangents
        self.__verts_offset=[-1,-1,-1,-1,-1,-1]
        #polys_offset - offset to polygons data
        self.__polys_offset=-1
        #bone_offset - offsets to bones data, must include offsets
        #in order: bind, end_bones_1, end_bones_2
        self.__bone_offset=[-1,-1,-1]
        self.interupted = False
        self.calc_tan = calc_tan

    def set_no_verts(self, no_v):
        self.__no_verts=no_v

    def set_no_polys(self, no_p):
        self.__no_polys=no_p

    def set_no_uvs(self, no_uv):
        self.__no_uvs=no_uv

    def set_no_bones_per_entry(self, no_bones_per_entry):
        self.__bones_per_dic_entry=no_bones_per_entry

    def set_vert_co_offs(self, offset):
        self.__verts_offset[0] = offset

    def set_vert_normal_offs(self, offset):
        self.__verts_offset[1] = offset

    def set_vert_uv_offs(self, offset):
        self.__verts_offset[2] = offset

    def set_vert_col_offs(self, offset):
        self.__verts_offset[3] = offset

    def set_vert_tangent_offs(self, offset):
        self.__verts_offset[5] = offset

    def set_polys_offs(self, offset):
        self.__polys_offset = offset

    def set_bones_dic_indx_offs(self, offset):
        self.__bone_offset[0] = offset

    def set_bones_dic_offs(self, offset):
        self.__bone_offset[1] = offset

    def set_bones_weights_dic_offs(self, offset):
        self.__bone_offset[2] = offset

    def get_no_polys(self):
        return self.__no_polys

    def get_num_uvs(self):
        return self.__no_uvs

    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__no_polys*3)
        bytes += help_funcs.UInt32ToByts(self.__no_verts)
        bytes += self.__uvs_mask
        bytes += help_funcs.UInt32ToByts(self.__no_uvs)
        bytes += help_funcs.UInt32ToByts(self.__bones_per_dic_entry)
        bytes += help_funcs.UInt32ToByts(self.__mat_idx)
        bytes += self.__bbox.to_scs_bytes()
        for i in range(0,len(self.__verts_offset)):
            bytes += help_funcs.Int32ToByts(self.__verts_offset[i])
        bytes += help_funcs.Int32ToByts(self.__polys_offset)
        for i in range(0,3):
            bytes += help_funcs.Int32ToByts(self.__bone_offset[i])

        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())



class PMGHeader:
    def __init__(self, bbox, version, no_parts=(0,0,0,0),
            def_offs=(0,0,0,0), dummy_data=(0,0), bone_data=(0,0),
            geometry_data=(0,0), uv_color_data=(0,0), poly_data=(0,0)):
        """
        version - version of pmg (ETS2 = 1349347090)
        no_parts - number of different parts in pmg: 
            (models, sections, bones, dummies)
        bbox - bounding box of whole pmg
        def_offs - offsets of definitions in pmg:
            (bones, sections, dummies, models)
        dummy_data - offset to dummy names and size of names block: (offset, size)
        bone_data - offset to bones and size of bones data: (offset, size)
        geometry_data - vertices coordinates and normals infos: (offset, size)
        uv_color_data - vertices uvs and vertex colors infos: (offset, size)
        poly_data - vertices connections infos: (offset, size)
        """
        self.version = version
        self.no_parts = no_parts

        self.__animated_model = no_parts[2] > 0
        if bbox is None:
            self.bbox = BoundingBox((0,0,0), (0,0,0))
        else:
            self.bbox = bbox
        self.def_offs = def_offs
        self.dummy_data = dummy_data
        self.bone_data = bone_data
        self.geometry_data = geometry_data
        self.uv_color_data = uv_color_data
        self.poly_data = poly_data

    def is_model_animated(self):
        return self.__animated_model

    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.version)

        for i in range(0,4):
            bytes += help_funcs.UInt32ToByts(self.no_parts[i])

        bytes += self.bbox.to_scs_bytes()

        for i in range(0,4):
            bytes += help_funcs.UInt32ToByts(self.def_offs[i])

        bytes += help_funcs.UInt32ToByts(self.dummy_data[0])
        bytes += help_funcs.UInt32ToByts(self.dummy_data[1])

        bytes += help_funcs.UInt32ToByts(self.bone_data[0])
        bytes += help_funcs.UInt32ToByts(self.bone_data[1])

        bytes += help_funcs.UInt32ToByts(self.geometry_data[0])
        bytes += help_funcs.UInt32ToByts(self.geometry_data[1])

        bytes += help_funcs.UInt32ToByts(self.uv_color_data[0])
        bytes += help_funcs.UInt32ToByts(self.uv_color_data[1])

        bytes += help_funcs.UInt32ToByts(self.poly_data[0])
        bytes += help_funcs.UInt32ToByts(self.poly_data[1])
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())

###############################################
#
# Main class for saving pmg file
#
###############################################
class PMGSave:
    def __init__(self, root_ob, mat_idx_lib, no_looks, version):
        #bbc1 minimal) and bbc2(maximal) are corners 
        #for global root bounding box needed in pmg header
        self.__bbc1 = None
        self.__bbc2 = None
        self.__dum_data = "" #string with dummies unique flare names
        mod_ob_li = [] #list of all blender model objects sorted by sections
        sec_def_li = [] #list of section definitions
        dum_def_li = [] #list of dummies definitions
        mod_def_li = [] #list of model definitions
        sec_list = [ob for ob in root_ob.children if "scs_variant_visib" in ob]
        for sec_ob in sec_list:
            sec_name = sec_ob.name
            mod_objs = [ob for ob in sec_ob.children if ob.type == 'MESH']
            dum_objs = [ob for ob in sec_ob.children if ob.type == 'EMPTY']
            curr_s = PMGSection(sec_name,
                    len(mod_objs), len(mod_def_li),
                    len(dum_objs), len(dum_def_li))
            sec_def_li.append(curr_s)

            for dum_ob in dum_objs:
                open_caret = dum_ob.name.find('[')
                close_caret = dum_ob.name.rfind(']')
                dum_name = dum_ob.name[:open_caret]
                dum_data = dum_ob.name.strip()[open_caret+1:close_caret] #eg: flare.sth
                dum_loc = dum_ob.location
                dum_rot = dum_ob.rotation_quaternion
                dum_off = self.__dummy_nameblock_offset(dum_data)
                curr_d = PMGDummy(name=dum_name,
                        loc=(-dum_loc.x, dum_loc.y, -dum_loc.z),
                        rot=(dum_rot.w, -dum_rot.x, dum_rot.y, -dum_rot.z),
                        offset=dum_off)
                dum_def_li.append(curr_d)
                #if len(dum_data) > 0:
                #    print("\nDummy: ", dum_ob.name, " Set offset: ", dum_off, "\nActuall string: ", self.__dum_data)

            for modl_ob in mod_objs:
                ob_dat = modl_ob.data
                ob_mat_key = ""
                for look_indx in range(0, no_looks):
                    ob_mat_key += modl_ob.material_slots[look_indx].material.name
                #check if object needs calculation of tangents
                calc_tan = False
                for tex_slot in modl_ob.material_slots[0].material.texture_slots:
                    if tex_slot is None:
                        break
                    if tex_slot.use_map_normal:
                        calc_tan = True
                        break
                curr_m = PMGModel(self.__get_bbox(modl_ob),
                        len(ob_dat.polygons), len(ob_dat.vertices),
                        len(ob_dat.uv_layers), modl_ob.material_slots[0].material.scs_shading,
                        mat_idx_lib[ob_mat_key], calc_tan)
                mod_def_li.append(curr_m)
                mod_ob_li.append(modl_ob)

        #parse armature and bones and create definitions for PMG
        bone_def_size = 0
        self.__bone_def_li = []
        bone_def_li = [] #list of bone definitions
        if ("anim_armature_object" in bpy.data.objects and
                    "anim_armature" in bpy.data.armatures and
                    len(bpy.data.armatures["anim_armature"].bones) > 0):
            bones_indx_dic = {} #dictionary for saving index of bone by it's name
            #select armature object and go to edit mode, to get data of edit_bones
            bpy.data.scenes[bpy.context.scene.name].objects.active = bpy.data.objects['anim_armature_object']
            bpy.ops.object.mode_set(mode='EDIT')
            bones_pose_li = bpy.data.objects['anim_armature_object'].pose.bones
            bones_obj_li = bpy.data.armatures['anim_armature'].edit_bones

            i=0
            for pose_bone in bones_pose_li:
                bone_obj = bones_obj_li[pose_bone.name]
                bones_indx_dic[bone_obj.name]=i

                parent_indx = 255
                if bone_obj.parent is not None:
                    parent_indx = bones_indx_dic[bone_obj.parent.name]

                #TODO actually recalculate bones transformation to apply rest position when PMA supported
                #curr_transf_mat = help_funcs.ConvertSCSMatrix(bone_obj.matrix)
                #curr_trans_vec = bone_obj.head.copy()
                ##convert Blender coordinate system to SCS
                #curr_trans_vec.x *= -1
                #curr_trans_vec.z *= -1
                # curr_b = PMGBone(name=bone_obj.name,
                #                  transf_mat=curr_transf_mat,
                #                  mat_det_sign=curr_transf_mat.determinant(),
                #                  rot_quat=curr_transf_mat.to_quaternion(),
                #                  trans_vec=curr_trans_vec,
                #                  parent=bone_obj["scs_b_parent"],
                #                  bone_indx=bone_obj["scs_b_indx"]
                #                  )
                curr_b = PMGBone(name=bone_obj.name,
                                 transf_mat=Matrix(bone_obj["scs_b_transf_mat"]),
                                 rot_quat=Quaternion(bone_obj["scs_b_rot_quat"]),
                                 trans_vec=Vector(bone_obj["scs_b_trans_vec"]),
                                 scale_vec=Vector(bone_obj["scs_b_scale_vec"]),
                                 mat_det_sign=bone_obj["scs_b_mat_det_sign"],
                                 stretch_quat=Quaternion(bone_obj["scs_b_stretch_quat"]),
                                 #parent=parent_indx,
                                 parent=bone_obj["scs_b_parent"],
                                 bone_indx=bone_obj["scs_b_indx"])
                bone_def_li.append(curr_b)
                i+=1
            bone_def_size = bone_def_li[0].bytes_len()*len(bone_def_li)
            self.__bone_def_li = bone_def_li
            bpy.ops.object.mode_set(mode='OBJECT')

        #defines header offsets
        bone_offs = PMGHeader(None, 0).bytes_len()
        sec_offs = bone_offs+bone_def_size
        dum_offs = sec_offs+sec_def_li[0].bytes_len()*len(sec_def_li)
        mod_offs = dum_offs+PMGDummy().bytes_len()*len(dum_def_li)

        self.__header = PMGHeader(
                BoundingBox(self.__bbc1, self.__bbc2),
                version,
                no_parts=(len(mod_ob_li), len(sec_def_li), len(bone_def_li), len(dum_def_li)),
                def_offs=(bone_offs, sec_offs, dum_offs, mod_offs))

        self.__mod_ob_li = mod_ob_li
        self.__sec_def_li = sec_def_li
        self.__dum_def_li = dum_def_li
        self.__mod_def_li = mod_def_li

    def __dummy_nameblock_offset(self, dummy_data):
        """
        Returns offset of given dummy_data in global dummy string
        """
        if len(dummy_data) == 0:
            return -1
        indx = self.__dum_data.rfind(dummy_data)
        nxt_ch_indx = indx+len(dummy_data)
        #do correction if dummy_data match partial data
        #example: licence.plate_rear already in, dummy_data="licence.plate"
        if (indx > 0 and
            nxt_ch_indx < len(self.__dum_data) and
            self.__dum_data[nxt_ch_indx] != "|"):
            #print("Done fixing:", dummy_data, "\nString till now:", self.__dum_data, "\n")
            indx = -1

        #id flare name is not yet in string then add it and return indx
        #otherwise return find index which is actuall offset
        if indx == -1:
            if len(self.__dum_data) > 0:
                self.__dum_data += "|"
                offset = len(self.__dum_data)
            else:
                offset = 0
            self.__dum_data += dummy_data
            return offset
        else:
            return indx

    def __get_bbox(self, ob):
        """
        Returns object bounding box and updates global root bounding box
        if necessary
        """
        c1 = Vector(ob.bound_box[1])
        c1.z = -c1.z #for transforming coordinates to scs system
        c2 = Vector(ob.bound_box[7])
        c2.z = -c2.z #for transforming coordinates to scs system

        #rest of method for calculating root bounding box
        if self.__bbc1 is None:
            self.__bbc1 = c1
        if self.__bbc2 == None:
            self.__bbc2 = c2

        for j in range(0,3):
            if c1[j] < self.__bbc1[j]:
                self.__bbc1[j] = c1[j]
            if c2[j] > self.__bbc2[j]:
                self.__bbc2[j] = c2[j]
        return BoundingBox(c1, c2)

    @staticmethod
    def __triangulate_mesh(me):
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()

    @staticmethod
    def  __calc_tangent(p, ob_data, idx):
        v1 = ob_data.vertices[p.vertices[0]].co
        v2 = ob_data.vertices[p.vertices[1]].co
        v3 = ob_data.vertices[p.vertices[2]].co

        uv_map = ob_data.uv_layers[0]
        w1 = uv_map.data[idx].uv
        w2 = uv_map.data[idx+1].uv
        w3 = uv_map.data[idx+2].uv

        vec1 = v2-v1
        vec2 = v3-v1

        uv1 = w2-w1
        uv2 = w3-w1

        divide = (uv1.x*uv2.y-uv2.x*uv1.y)
        if divide != 0.0:
            r = 1.0/divide
        else:
            r = 0
        sdir = (uv2.y*vec1-uv1.y*vec2)*r
        tdir = (uv1.x*vec2-uv2.x*vec1)*r

        return [sdir, tdir]

    @staticmethod
    def __calc_final_tangent(n, t, t2):
        tangent = t-n*n.dot(t)
        tangent.normalize()

        tangent = tangent.to_4d()
        if (n.cross(t)).dot(t2) < 0.0:
            tangent.w = -1.0
        else:
            tangent.w = 1.0
        return tangent

    def write(self, f):
        """
        Parse model data and writes definitions and data to pmg file
        """
        #first write header and definitions with some unset data
        f.write(self.__header.to_scs_bytes())
        for bone in self.__bone_def_li:
            f.write(bone.to_scs_bytes()) #bones data are already final
        for section in self.__sec_def_li:
            f.write(section.to_scs_bytes())
        for dummy in self.__dum_def_li:
            f.write(dummy.to_scs_bytes())
        for model in self.__mod_def_li:
            f.write(model.to_scs_bytes())
        #write dummies name data
        offset_start = f.tell()
        w_len = 0
        for ch in self.__dum_data:
            if ch == "|":
                f.write((0).to_bytes(1, 'little'))
            else:
                f.write(help_funcs.CharToByts(ord(ch)))
            w_len +=1

        if len(self.__dum_data) > 0:
            #if name data length modul is 0 add 4 empty bytes
            if w_len % 4 == 0:
                for i in range(0,4):
                    f.write((0).to_bytes(1, 'little'))
            else:
                while w_len % 4 != 0:
                    f.write((0).to_bytes(1, 'little'))
                    w_len +=1
        self.__header.dummy_data = (offset_start, w_len)


        #fill up objects for models vertices, tangents, faces, vert_indexes for bone_dic linking and
        #dictionaries for bones and bone weights
        [models_verts, models_verts_tan, models_faces, models_verts_bones_dic_keys,
         models_bones_dic, models_bones_w_dic, models_bones_dic_max_sizes] = self.___get_blender_geometry()


        offset_start = f.tell()
        i=0
        for model in self.__mod_def_li:
            if not model.interupted:
                m_bones_dic_max_size = models_bones_dic_max_sizes[i]
                model.set_no_bones_per_entry(m_bones_dic_max_size)

                m_bones_dic = models_bones_dic[i]
                m_bones_w_dic = models_bones_w_dic[i]
                m_verts_bones_dic_keys = models_verts_bones_dic_keys[i]
                #convert bones indexes dictionary keys to list so vert_bones_dict_indx can be extracted
                m_bones_dic_keys_li = list(m_bones_dic.keys())

                #write vertices bones dictionary indexes
                if len(m_verts_bones_dic_keys.keys()) > 0:
                    model.set_bones_dic_indx_offs(f.tell())
                else:
                    model.set_bones_dic_indx_offs(-1)
                for vert in m_verts_bones_dic_keys:
                    m_vert_bones_dic_key = m_verts_bones_dic_keys[vert]
                    #get index of current vertex bone dictionary key
                    j=0
                    #print("Search key:", m_vert_bones_dic_key)
                    while m_vert_bones_dic_key != m_bones_dic_keys_li[j]:
                        #print("Key:", m_bones_dic_keys_li[j])
                        j+=1
                    f.write(help_funcs.UInt16ToByts(j))

                #write bones indexes dictionary data
                if len(m_bones_dic_keys_li) > 0:
                    model.set_bones_dic_offs(f.tell())
                else:
                    model.set_bones_dic_offs(-1)
                for dic_key in m_bones_dic_keys_li:
                    m_bones_dic_entry = m_bones_dic[dic_key]
                    for k in range(0, m_bones_dic_max_size):
                        #if current entry still have data write them
                        #otherwise write 255 which means no bone
                        if k < len(m_bones_dic_entry):
                            f.write(help_funcs.CharToByts(m_bones_dic_entry[k]))
                        else:
                            f.write(help_funcs.CharToByts(255))

                #write bones weights dictionary data
                if len(m_bones_dic_keys_li) > 0:
                    model.set_bones_weights_dic_offs(f.tell())
                else:
                    model.set_bones_weights_dic_offs(-1)
                #print("Model",model.get_no_polys())
                for dic_key in m_bones_dic_keys_li:
                    m_bones_w_dic_entry = m_bones_w_dic[dic_key]
                    #print("Bones dic size:", len(m_bones_w_dic_entry))
                    for k in range(0, m_bones_dic_max_size):
                        #convert float weight to int from 0 to 255
                        #print(k)
                        if k < len(m_bones_w_dic_entry):
                            f.write(help_funcs.CharToByts(int(m_bones_w_dic_entry[k]*255)))
                        else:
                            f.write(help_funcs.CharToByts(0))
                    #print("\n")
                f.write(help_funcs.UInt16ToByts(0)) #write two zero for ending bytes: 00 00
            else:
                off = f.tell()
                model.set_bones_dic_indx_offs(off)
                model.set_bones_dic_offs(off)
                model.set_bones_weights_dic_offs(off)
            i+=1
        self.__header.bone_data = (offset_start, f.tell()-offset_start)


        #write models vertexes coord, direction, vertex color, uv map  
        if self.__header.version == 1349347090: #until 1.3.1
            offset_start = f.tell()
            help_funcs.PrintDeb("\nWriting vertices coord and normals v1.3.1...")
            #write models vertices coord and normals
            i=0
            for model in self.__mod_def_li:
                if not model.interupted:
                    m_verts = models_verts[i].values()
                    #write vertex coordinates
                    model.set_vert_co_offs(f.tell())
                    for vert in m_verts:
                        f.write(vert.to_scs_bytes('COORD'))
                    #write vertex normals
                    model.set_vert_normal_offs(f.tell())
                    for vert in m_verts:
                        f.write(vert.to_scs_bytes('NORMAL'))
                i+=1

            self.__header.geometry_data = (offset_start, f.tell()-offset_start)
            offset_start = f.tell()
            help_funcs.PrintDeb("Writing vertices uvs v1.3.1...")
            #write models vertices uvs and colors    
            i=0
            for model in self.__mod_def_li:
                if not model.interupted:
                    m_verts = models_verts[i].values()
                    #write vertex uvs
                    model.set_vert_uv_offs(f.tell())
                    uv_indx = 0
                    while uv_indx < model.get_num_uvs():
                        for vert in m_verts:
                            f.write(vert.to_scs_bytes('UV', uv_indx))
                        uv_indx+=1
                    #write vertex color
                    model.set_vert_col_offs(f.tell())
                    for vert in m_verts:
                        f.write(vert.to_scs_bytes('COL'))
                i+=1
            self.__header.uv_color_data = (offset_start, f.tell()-offset_start)
        elif self.__header.version == 1349347091: #1.4.x
            if not self.__header.is_model_animated():
                help_funcs.PrintDeb("\nRecognized model type: RIGID")
                self.__header.geometry_data = (f.tell(), 0)
                offset_start = f.tell()
                help_funcs.PrintDeb("Writing vertices data v1.4.x...")
                i=0
                for model in self.__mod_def_li:
                    off = f.tell()
                    model.set_vert_co_offs(off)
                    off += 12
                    model.set_vert_normal_offs(off)
                    off += 12
                    #if model needs tangents calculations
                    if model.calc_tan:
                        model.set_vert_tangent_offs(off)
                        off += 16
                    model.set_vert_col_offs(off)
                    off += 4
                    model.set_vert_uv_offs(off)
                    if not model.interupted:
                        m_verts = models_verts[i]
                        m_verts_tan = models_verts_tan[i]

                        for key in m_verts.keys():
                            vert = m_verts[key]
                            #if model needs tangents calculations
                            if model.calc_tan:
                                t = m_verts_tan[key][0]
                                t2 = m_verts_tan[key][1]
                                vert.set_tangent(self.__calc_final_tangent(vert.get_normal(), t, t2))

                            f.write(vert.to_scs_bytes('COORD'))
                            f.write(vert.to_scs_bytes('NORMAL'))
                            #if model needs tangents calculations
                            if model.calc_tan:
                                f.write(vert.to_scs_bytes('TANGENT'))
                            f.write(vert.to_scs_bytes('COL'))
                            uv_indx = 0
                            while uv_indx < model.get_num_uvs():
                                f.write(vert.to_scs_bytes('UV', uv_indx))
                                uv_indx+=1
                    i+=1

                self.__header.uv_color_data = (offset_start, f.tell()-offset_start)
            else:
                help_funcs.PrintDeb("\nRecognized model type: ANIMATED")
                offset_start = f.tell()
                help_funcs.PrintDeb("Writing vertices data v1.4.x...")
                i=0
                for model in self.__mod_def_li:
                    if not model.interupted:
                        m_verts = models_verts[i]
                        m_verts_tan = models_verts_tan[i]

                        #by SCS: "dynamic: sizeof(positions (float3) + normals (float3) + tangents (float4 if present))"
                        off = f.tell()
                        model.set_vert_co_offs(off)
                        off += 12
                        model.set_vert_normal_offs(off)
                        off += 12
                        #if model needs tangents calculations
                        if model.calc_tan:
                            model.set_vert_tangent_offs(off)
                        for key in m_verts.keys():
                            vert = m_verts[key]
                            #if model needs tangents calculations
                            if model.calc_tan:
                                t = m_verts_tan[key][0]
                                t2 = m_verts_tan[key][1]
                                vert.set_tangent(self.__calc_final_tangent(vert.get_normal(), t, t2))

                            f.write(vert.to_scs_bytes('COORD'))
                            f.write(vert.to_scs_bytes('NORMAL'))
                            #if model needs tangents calculations
                            if model.calc_tan:
                                f.write(vert.to_scs_bytes('TANGENT'))
                    else:
                        off = f.tell()
                        model.set_vert_co_offs(off)
                        off += 12
                        model.set_vert_normal_offs(off)
                    i+=1

                self.__header.geometry_data=(offset_start, f.tell()-offset_start)
                offset_start = f.tell()
                i=0
                for model in self.__mod_def_li:
                    if not model.interupted:
                        m_verts = models_verts[i]

                        #by SCS: "static : sizeof(colors (u32) + colors2 (u32 if present) + texcoords (float2 * coord_count))"
                        off = f.tell()
                        model.set_vert_col_offs(off)
                        off += 4
                        model.set_vert_uv_offs(off)
                        for key in m_verts.keys():
                            vert = m_verts[key]
                            f.write(vert.to_scs_bytes('COL'))
                            uv_indx = 0
                            while uv_indx < model.get_num_uvs():
                                f.write(vert.to_scs_bytes('UV', uv_indx))
                                uv_indx+=1
                    else:
                        off = f.tell()+12
                        #if model needs tangents calculations
                        if model.calc_tan:
                            model.set_vert_tangent_offs(off)
                            off += 16
                        model.set_vert_col_offs(off)
                        off += 4
                        model.set_vert_uv_offs(off)
                    i+=1
                self.__header.uv_color_data=(offset_start, f.tell()-offset_start)

        offset_start = f.tell()
        help_funcs.PrintDeb("Writing vertices connections...")
        #write models faces
        i=0
        for model in self.__mod_def_li:
            model.set_polys_offs(f.tell())
            if not model.interupted:
                for face in models_faces[i]:
                    f.write(face.to_scs_bytes())
            i+=1
        self.__header.poly_data = (offset_start, f.tell()-offset_start)

        help_funcs.PrintDeb("Rewriting definitions...")
        #rewrite definitions
        f.seek(0)
        f.write(self.__header.to_scs_bytes())
        #TODO find a way not to rewrite it and change back to default order when PMA supported
        #for bone in self.__bone_def_li:
        #    f.write(bone.to_scs_bytes())
        for i in range(0, len(self.__bone_def_li)):
            for bone in self.__bone_def_li:
                if bone.bone_indx == i:
                    f.write(bone.to_scs_bytes())

        for section in self.__sec_def_li:
            f.write(section.to_scs_bytes())
        for dummy in self.__dum_def_li:
            f.write(dummy.to_scs_bytes())
        for model in self.__mod_def_li:
            f.write(model.to_scs_bytes())

        help_funcs.PrintDeb("Done! PMG saved.")


    def ___get_blender_geometry(self):
        """
        Gether all structures needed for writing PMG models data
        @return [models_verts - [PMG vertices data for each model],
                models_verts_tan - [tangent data for PMG vertices for each model],
                models_faces - [PMG faces data for each model],
                models_verts_bones_dic_keys - [vertex dictionary keys which belongs to each vertex also list for all models],
                models_bones_dic - [bones indexes dictionary for each model],
                models_bones_weights_dic - [bones weights dictionary for each model],
                models_bones_dic_max_sizes - [maximal number of bones in dictionary entries for each model]]
        """
        help_funcs.PrintDeb("Creating SCS model objects ", end=" ")
        #read models data
        i=0
        models_verts = []
        models_verts_tan = []
        models_faces = []
        models_verts_bones_dic_keys = []
        models_bones_dic = []
        models_bones_dic_max_sizes = []
        models_bones_weights_dic = []
        #flag for indicating if bones data for model exists
        bones_data_exist = "anim_armature_object" in bpy.data.objects and "anim_armature" in bpy.data.armatures
        no_models = len(self.__mod_def_li)
        for model in self.__mod_def_li:
            m_ob = self.__mod_ob_li[i]
            dots = "."*int(i/int(no_models/10+1))
            help_funcs.PrintDeb("\rCreating SCS model objects "+str(i+1)+" of "+str(no_models)+dots, end="")
            m_verts = {}
            m_verts_tan = {}
            m_verts_bones_dic_keys = {}

            m_bones_dic_max_size=0 #max size of entry in bones indexes dictionary
            m_bones_dic = {} #bones indexes dictionary for curent model
            m_bones_w_dic = {} #bones weight indexes dictionary for current model

            #set uv map coordinates and vertex color to PMGVertex objects
            col_map = None
            if len(m_ob.data.vertex_colors) > 0:
                col_map = m_ob.data.vertex_colors[0]
            uv_maps = None
            if len(m_ob.data.uv_layers) > 0:
                uv_maps = []
                for uv_lay in m_ob.data.uv_layers:
                    uv_maps.append(uv_lay)
            m_faces = []
            j=0 #vertices indexer
            msg = None
            for p in m_ob.data.polygons:
                vert_li = [] #used for storing edges of current polygon
                if len(p.vertices) != 3:
                    model.interupted = True
                    msg = "\n\nError: Object '"+m_ob.name+"' has at least one polygon which is not triangle and it won't be exported.\nPlease use triangulate modifier on that object.\n\n"
                    break
                #if model needs tangents calculations
                if model.calc_tan:
                    [tan1, tan2] = self.__calc_tangent(p, m_ob.data, j)
                for v in p.vertices:
                    vert_li.append(v)
                    if not v in m_verts:
                        #if model needs tangents calculations
                        if model.calc_tan:
                            #add current triangle tangent to vertexes tangents
                            m_verts_tan[v] = [tan1, tan2]
                        ver = m_ob.data.vertices[v]

                        #read coordinates and normal
                        #convert blender vertex to SCS vertex
                        curr_v = PMGVertex((-ver.co.x, ver.co.y, -ver.co.z),
                            (-ver.normal.x, ver.normal.y, -ver.normal.z))

                        #read col map
                        if col_map is not None:
                            v_col = col_map.data[j].color*255
                            curr_v.set_color((v_col.r, v_col.g, v_col.b, 255))
                        else:
                            msg = "\n\nWarning: Object '"+m_ob.name+"' has no vertex colors, all vertices color will be set to RGB(#FFFFFF)\n"
                            curr_v.set_color((255,255,255,255))

                        #read uv maps
                        if uv_maps is not None:
                            for uv_map in uv_maps:
                                #transforming y uv to SCS data format
                                curr_v.add_uv((uv_map.data[j].uv.x,
                                               1-uv_map.data[j].uv.y))
                        else:
                            msg = "\n\nWarning: Object '"+m_ob.name+"' has no UV layers, all vertices UVs will be set to 0,0\n"
                            curr_v.add_uv((0.0,0.0))
                            model.set_no_uvs(1)

                        #read bones weights for vertex and create dictionary entry
                        if bones_data_exist:
                            curr_dic_max_size=0
                            ver_bones_dic_entry = [] #bones indexes dictionary entry for current vertex
                            ver_bones_w_dic_entry = [] #bones weights dictionary entry for current vertex
                            ver_bones_dic_entry_key = "" #unique key for representing bones indexes and weights dictionary entries
                            for ver_group in ver.groups:
                                k=0 #index for bone (same index order is used by writing bones definitions)
                                for bone in bpy.data.armatures["anim_armature"].bones:
                                    #check if vertex group belongs to bone
                                    if m_ob.vertex_groups[ver_group.group].name == bone.name:
                                        #TODO change back to default order when PMA is supported
                                        #ver_bones_dic_entry.append(k)
                                        for pmg_bone in self.__bone_def_li:
                                            if pmg_bone.name == bone.name:
                                                ver_bones_dic_entry.append(pmg_bone.bone_indx)
                                                break

                                        ver_bones_w_dic_entry.append(ver_group.weight)
                                        #"%.4f" formatter for float value with 4 decimals
                                        ver_bones_dic_entry_key += str(k)+","+("%.4f" % ver_group.weight)+","
                                        curr_dic_max_size+=1
                                        break
                                    k+=1
                            #if there is no entry with current bones indexes and weights combination then insert it
                            if not ver_bones_dic_entry_key in m_bones_dic:
                                m_bones_dic[ver_bones_dic_entry_key] = ver_bones_dic_entry
                                m_bones_w_dic[ver_bones_dic_entry_key] = ver_bones_w_dic_entry
                                #update max size of bones indexes dictionary entryies
                                if m_bones_dic_max_size < curr_dic_max_size:
                                    m_bones_dic_max_size = curr_dic_max_size
                            m_verts_bones_dic_keys[v] = ver_bones_dic_entry_key

                        #add vertex to dictionary
                        m_verts[v] = curr_v
                    else:
                        #if model needs tangents calculations
                        if model.calc_tan:
                            m_verts_tan[v][0] = m_verts_tan[v][0] + tan1
                            m_verts_tan[v][1] = m_verts_tan[v][1] + tan2
                    j+=1
                m_faces.append(PMGFace(vert_li[::-1])) #::-1 to convert from Blender to SCS order

            if len(m_verts) < len(m_ob.data.vertices):
                model.interupted = True
                msg = "\n\nError: Object '"+m_ob.name+"'has nested vertices and won't be exported.\nPlease use 'Remove Nested Verts' command under object properties\n\n"

            if msg is not None:
                help_funcs.PrintDeb(msg)

            if model.interupted:
                model.set_no_polys(0)
                model.set_no_verts(0)
                model.set_no_bones_per_entry(1)
            else:
                model.set_no_polys(len(m_faces))
                model.set_no_verts(len(m_verts))

            models_verts.append(m_verts)
            models_verts_tan.append(m_verts_tan)
            models_faces.append(m_faces)

            models_verts_bones_dic_keys.append(m_verts_bones_dic_keys)
            models_bones_dic.append(m_bones_dic)
            models_bones_weights_dic.append(m_bones_w_dic)
            models_bones_dic_max_sizes.append(m_bones_dic_max_size)

            i+=1

        return [models_verts, models_verts_tan,
                models_faces, models_verts_bones_dic_keys,
                models_bones_dic, models_bones_weights_dic, models_bones_dic_max_sizes]

def save(exportpath, root_ob, mat_idx_lib, no_looks, version):
    with open(exportpath+'/'+root_ob.name+'.pmg', "wb") as f:
        t = time.clock()
        pmg = PMGSave(root_ob, mat_idx_lib, no_looks, version)
        pmg.write(f)
        help_funcs.PrintDeb("Exporting of PMG took:", str(time.clock()-t)[:4], "seconds")

"""
print(save("C:\\Users\\Simon\\Documents\\Euro Truck Simulator 2\\mod\\zzzz\\vehicle\\truck\\daf_xf\\truck.pmg", bpy.data.objects['Btruck']))
"""