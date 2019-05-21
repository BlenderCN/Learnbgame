from pathlib import Path

try:
    from .Blocks.VBIB import *
except:
    from Source2.Blocks.VBIB import *
import bpy
import os.path

from mathutils import Vector, Matrix


# model_path = r'E:\PYTHON\io_mesh_SourceMDL/test_data/source2/bad_ancient_destruction_pitrim_model.vmesh_c'


class VMESH_IO:

    def __init__(self, vmesh_path):
        self.valve_file = ValveFile(vmesh_path)
        self.valve_file.read_block_info()
        self.valve_file.check_external_resources()

        morph_set = self.valve_file.data.data[0]['m_morphSet']
        if morph_set in self.valve_file.available_resources:
            m_path = Path(self.valve_file.available_resources[morph_set])
            self.morf_set = ValveFile(m_path)
            self.morf_set.read_block_info()
            self.morf_set.check_external_resources()
            ext_vtex = self.morf_set.rerl.resources[0]
            m_path = self.morf_set.available_resources[ext_vtex]
            self.morf_vtex = ValveFile(m_path)
            self.morf_vtex.read_block_info()
            self.morf_vtex.check_external_resources()

        self.mesh_name = str(os.path.basename(vmesh_path).split('.')[0])
        self.name = self.mesh_name
        self.armature_obj = None
        self.armature = None
        # self.build_meshes()

    def build_skeleton(self):
        for skeleton_data in self.valve_file.data.data:
            bpy.ops.object.armature_add(enter_editmode=True)

            self.armature_obj = bpy.context.object
            self.armature_obj.show_x_ray = True

            self.armature = self.armature_obj.data
            self.armature.name = self.name + "_ARM"
            self.armature.edit_bones.remove(self.armature.edit_bones[0])

            bpy.ops.object.mode_set(mode='EDIT')
            bones = {}
            skeleton = skeleton_data['m_skeleton']
            for se_bone in skeleton['m_bones']:  # type:
                bones[se_bone['m_boneName']] = (self.armature.edit_bones.new(se_bone['m_boneName']), se_bone)

            for bone_name, (bl_bone, se_bone) in bones.items():
                bl_bone.use_relative_parent = True
                m = se_bone['m_invBindPose']
                inverseBindPose = Matrix([[m[0], m[1], m[2], m[3]],
                                          [m[4], m[5], m[6], m[7]],
                                          [m[8], m[9], m[10], m[11]],
                                          [0, 0, 0, 1]])

                inverseBindPose.invert()
                if se_bone['m_parentName'] is not None:
                    bl_parent, parent = bones[se_bone['m_parentName']]
                    bl_bone.parent = bl_parent
                    bl_bone.tail = Vector([0, 0, 1]) + bl_bone.head
                else:
                    pass
                    bl_bone.tail = Vector([0, 0, 1]) + bl_bone.head
                bl_bone.matrix = inverseBindPose
        bpy.ops.object.mode_set(mode='OBJECT')

    def build_meshes(self, bone_list=None, remap_list=None):
        for n, (v_mesh, indexes) in enumerate(
                zip(self.valve_file.vbib.vertex_buffer,
                    self.valve_file.vbib.index_buffer)):  # type: int,VertexBuffer,IndexBuffer

            name = self.mesh_name + str(n)
            mesh_obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            bpy.context.scene.objects.link(mesh_obj)

            # bones = [bone_list[i] for i in remap_list]
            mesh = mesh_obj.data

            if self.armature_obj:
                mesh_obj.parent = self.armature_obj
                modifier = mesh_obj.modifiers.new(type="ARMATURE", name="Armature")
                modifier.object = self.armature_obj

            if bone_list:
                print('Bone list available, creating vertex groups')
                weight_groups = {bone: mesh_obj.vertex_groups.new(bone) for bone in
                                 bone_list}
            vertexes = []
            uvs = []
            normals = []
            # Extracting vertex coordinates,UVs and normals
            for vertex in v_mesh.vertexes:
                vertexes.append(vertex.position.as_list)
                uvs.append([vertex.texCoordX, vertex.texCoordY])
                vertex.normal.convert()
            for poly in indexes.indexes:
                for v in poly:
                    normals.append(v_mesh.vertexes[v].normal.as_list)

            mesh.from_pydata(vertexes, [], indexes.indexes)
            mesh.update()
            mesh.uv_textures.new()
            uv_data = mesh.uv_layers[0].data
            for i in range(len(uv_data)):
                u = uvs[mesh.loops[i].vertex_index]
                uv_data[i].uv = u
            if bone_list:
                for n, vertex in enumerate(v_mesh.vertexes):
                    for bone_index, weight in zip(vertex.boneWeight.bone, vertex.boneWeight.weight):
                        if weight > 0:
                            bone_name = bone_list[remap_list[bone_index]]
                            weight_groups[bone_name].add([n], weight, 'REPLACE')
            bpy.ops.object.shade_smooth()
            mesh.normals_split_custom_set(normals)
            mesh.use_auto_smooth = True


if __name__ == '__main__':
    a = VMESH_IO(r'F:\PYTHON\io_mesh_SourceMDL/test_data/source2/sniper_model.vmesh_c')
    # with open('test.h', 'w') as f:
    #     a.valve_file.dump_structs(f)
