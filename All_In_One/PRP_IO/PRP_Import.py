import json
import random
from pathlib import Path
from pprint import pprint
from typing import Dict, List

import bpy
import mathutils
from mathutils import *


def split(array, n=3):
    return [array[i:i + n] for i in range(0, len(array), n)]


def fix_matrix(matrix):
    t = matrix
    matrix = [[0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0, 0.0]]
    matrix[0][0] = t[0]
    matrix[1][0] = t[1]
    matrix[2][0] = t[2]
    matrix[3][0] = t[3]
    matrix[0][1] = t[4]
    matrix[1][1] = t[5]
    matrix[2][1] = t[6]
    matrix[3][1] = t[7]
    matrix[0][2] = t[8]
    matrix[1][2] = t[9]
    matrix[2][2] = t[10]
    matrix[3][2] = t[11]
    matrix[0][3] = t[12]
    matrix[1][3] = t[13]
    matrix[2][3] = t[14]
    matrix[3][3] = t[15]
    return matrix


class PRPIO:
    def __init__(self, path: str = '', json_data={}, import_textures=False, join_bones=False):
        # TODO: make import_textures to do stuff
        self.import_textures = import_textures
        self.path = Path(path)
        self.name = self.path.stem
        self.join_bones = join_bones
        if json_data:
            self.model_json = json_data
        else:
            self.model_json = json.load(self.path.open('r'))

        self.armature_obj = None
        self.armature = None

        # just a temp containers
        self.mesh_obj = None
        self.mesh_data = None

        self.create_models()
        # bpy.ops.object.mode_set(mode='OBJECT')

    def create_skeleton(self, bone_data: Dict, normal_bones=False):

        bpy.ops.object.armature_add(enter_editmode=True)

        self.armature_obj = bpy.context.object
        self.armature_obj.show_x_ray = True
        self.armature_obj.name = self.name + '_ARM'

        self.armature = self.armature_obj.data
        self.armature.name = self.name + "_ARM_DATA"
        self.armature.edit_bones.remove(self.armature.edit_bones[0])

        bpy.ops.object.mode_set(mode='EDIT')
        bones = []
        for se_bone in bone_data:
            bones.append((self.armature.edit_bones.new(se_bone['name']), se_bone))

        for bl_bone, se_bone in bones:  # type: bpy.types.EditBone, Dict
            if se_bone['parent'] != -1:
                bl_parent, parent = bones[se_bone['parent']]
                bl_bone.parent = bl_parent
            else:
                pass
            bl_bone.tail = Vector([0, 0, 1]) + bl_bone.head

        bpy.ops.object.mode_set(mode='POSE')
        for se_bone in bone_data:  # type:Dict
            bl_bone = self.armature_obj.pose.bones.get(se_bone['name'])
            mat = Matrix(fix_matrix(se_bone['matrix']))
            bl_bone.matrix_basis.identity()
            if bl_bone.parent:
                bl_bone.matrix = bl_bone.parent.matrix * mat
            else:
                bl_bone.matrix = mat
        bpy.ops.pose.armature_apply()
        bpy.ops.object.mode_set(mode='EDIT')
        if normal_bones:
            for name, bl_bone in self.armature.edit_bones.items():
                if not bl_bone.parent:
                    continue
                parent = bl_bone.parent
                if len(parent.children) > 1:
                    bl_bone.use_connect = False
                    parent.tail = sum([ch.head for ch in parent.children],
                                      mathutils.Vector()) / len(parent.children)
                else:
                    parent.tail = bl_bone.head
                    bl_bone.use_connect = True
                    if bl_bone.children == 0:
                        par = bl_bone.parent
                        if par.children > 1:
                            bl_bone.tail = bl_bone.head + (par.tail - par.head)
                    if bl_bone.parent == 0 and bl_bone.children > 1:
                        bl_bone.tail = (bl_bone.head + bl_bone.tail) * 2
                if not bl_bone.children:
                    vec = bl_bone.parent.head - bl_bone.head
                    bl_bone.tail = bl_bone.head - vec / 2
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def get_material(mat_name, model_ob):
        if mat_name:
            mat_name = mat_name
        else:
            mat_name = "Material"
        mat_ind = 0
        md = model_ob.data
        mat = None
        for candidate in bpy.data.materials:  # Do we have this material already?
            if candidate.name == mat_name:
                mat = candidate
        if mat:
            if md.materials.get(mat.name):  # Look for it on this mesh_data
                for i in range(len(md.materials)):
                    if md.materials[i].name == mat.name:
                        mat_ind = i
                        break
            else:  # material exists, but not on this mesh_data
                md.materials.append(mat)
                mat_ind = len(md.materials) - 1
        else:  # material does not exist
            mat = bpy.data.materials.new(mat_name)
            md.materials.append(mat)
            # Give it a random colour
            rand_col = []
            for i in range(3):
                rand_col.append(random.uniform(.4, 1))
            mat.diffuse_color = rand_col

            mat_ind = len(md.materials) - 1

        return mat_ind

    def remap_materials(self, used_materials, all_materials):
        remap = {}
        for n, used_material in enumerate(used_materials):
            remap[all_materials.index(used_material)] = n

        return remap

    @staticmethod
    def strip_to_list(indices):
        new_indices = []
        for v in range(0, len(indices) - 2):
            if v & 1:
                new_indices.append(indices[v])
                new_indices.append(indices[v + 1])
                new_indices.append(indices[v + 2])
            else:
                new_indices.append(indices[v])
                new_indices.append(indices[v + 2])
                new_indices.append(indices[v + 1])
        new_indices = list(filter(lambda a: len(set(a)) == 3, split(new_indices)))
        return new_indices

    def build_meshes(self, mesh_data):

        # base_name = mesh_data['name']
        for m, (mesh_id, mat_id) in enumerate(mesh_data['mesh_data']):
            mesh_json = self.model_json['meshes'][mesh_id]
            # pprint(mesh_json)
            mat_json = self.model_json['materials'][mat_id]
            name = mesh_json['name']
            mesh_obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            bpy.context.scene.objects.link(mesh_obj)
            mesh = mesh_obj.data
            if self.armature_obj:
                mesh_obj.parent = self.armature_obj

                modifier = mesh_obj.modifiers.new(type="ARMATURE", name="Armature")
                modifier.object = self.armature_obj

            # bones = [bone_list[i] for i in remap_list]

            if mesh_data['bones']:
                print('Bone list available, creating vertex groups')
                weight_groups = {bone['name']: mesh_obj.vertex_groups.new(bone['name']) for bone in
                                 mesh_data['bones']}
            uvs = mesh_json['vertices']['uv']
            print('Building mesh:', name)
            print('Mesh mode:', mesh_json['mode'])
            # new_indices = split(mesh_json['indices'])

            new_indices = self.strip_to_list(mesh_json['indices'])
            # if len(new_indices) % 3 != 0:
            #     print('Indices:', len(new_indices) / 3)
            #     print('Skipping')
            #     continue
            mesh.from_pydata(mesh_json['vertices']['pos'], [], new_indices)
            mesh.update()
            mesh.uv_textures.new()
            uv_data = mesh.uv_layers[0].data
            for i in range(len(uv_data)):
                u = uvs[mesh.loops[i].vertex_index]
                uv_data[i].uv = u
            if mesh_data['bones']:
                for n, (bones, weights) in enumerate(
                        zip(mesh_json['vertices']['weight']['bone'], mesh_json['vertices']['weight']['weight'])):
                    for bone, weight in zip(bones, weights):
                        if weight != 0:
                            # if bone in mesh_data['bone_map']:
                            bone_id = mesh_data['bone_map'][m][bone]
                            bone_name = mesh_data['name_list'][str(bone_id)]  # ['name']
                            weight_groups[bone_name].add([n], weight / 255, 'REPLACE')
            self.get_material(mat_json['name'], mesh_obj)
            bpy.ops.object.select_all(action="DESELECT")
            mesh_obj.select = True
            bpy.context.scene.objects.active = mesh_obj
            bpy.ops.object.shade_smooth()
            # mesh.normals_split_custom_set(normals)
            mesh.use_auto_smooth = True

    def create_models(self):
        for model in self.model_json['models'].values():
            # pprint(model)
            if model['bones']:
                self.create_skeleton(model['bones'], self.join_bones)
            else:
                self.armature = None
                self.armature_obj = None
            self.build_meshes(model)

    # def add_flexes(self, mdlmodel: MDL_DATA.SourceMdlModel):
    #     # Creating base shape key
    #     self.mesh_obj.shape_key_add(name='base')
    #
    #     # Going through all flex frames in SourceMdlModel
    #     for flex_frame in mdlmodel.flex_frames:
    #
    #         # Now for every flex and vertex_offset(bodyAndMeshVertexIndexStarts)
    #         for flex, vertex_offset in zip(flex_frame.flexes, flex_frame.vertex_offsets):
    #
    #             flex_desc = self.MDL.file_data.flex_descs[flex.flex_desc_index]
    #             flex_name = flex_desc.name
    #             # if blender mesh_data does not have FLEX_NAME - create it,
    #             # otherwise work with existing
    #             if not self.mesh_obj.data.shape_keys.key_blocks.get(flex_name):
    #                 self.mesh_obj.shape_key_add(name=flex_name)
    #
    #             # iterating over all VertAnims
    #             for flex_vert in flex.the_vert_anims:  # type: MDL_DATA.SourceMdlVertAnim
    #                 vertex_index = flex_vert.index + vertex_offset  # <- bodyAndMeshVertexIndexStarts
    #                 vx = self.mesh_obj.data.vertices[vertex_index].co.x
    #                 vy = self.mesh_obj.data.vertices[vertex_index].co.y
    #                 vz = self.mesh_obj.data.vertices[vertex_index].co.z
    #                 fx, fy, fz = flex_vert.the_delta
    #                 self.mesh_obj.data.shape_keys.key_blocks[flex_name].data[vertex_index].co = (
    #                     fx + vx, fy + vy, fz + vz)


if __name__ == '__main__':
    a = PRPIO(r"D:\SteamLibrary\steamapps\common\Overlord II\Resources\dump\Character Minion Bard\model.json")
