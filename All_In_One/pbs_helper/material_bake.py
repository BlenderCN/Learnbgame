# Copyright (C) 2019 ywabygl@gmail.com
#
# PBS Helper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PBS Helper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PBS Helper. If not, see <http://www.gnu.org/licenses/>.

# bake a material to simple pbr material

from bpy.types import (
    Operator,
    ShaderNodeGroup,
    Panel
)
from bpy.props import (
    EnumProperty,
)
from mathutils import Color, Vector
import bpy
import os


class BakeMaterial(Operator):
    '''Bake texture from a material,need cycles. '''
    bl_label = "Bake A Material"
    bl_idname = "pbs_helper.bake"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT' and
                space.node_tree and
                context.scene.render.engine == 'CYCLES')

    def execute(self, context):
        obj = context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        data_path = os.path.join(os.path.dirname(
            __file__), 'data.blend')  # TODO to be func load all
        with bpy.data.libraries.load(data_path, link=True) as (data_from, data_to):
            data_to.node_groups = data_from.node_groups
        self.obj = context.active_object
        self.orign_mat = self.obj.active_material
        self.mat = self.orign_mat.copy()
        self.obj.active_material = self.mat
        self.tree = self.mat.node_tree
        self.nodes = self.tree.nodes
        self.links = self.tree.links
        self.output_node = [node for node in self.nodes if node.bl_idname ==
                            'ShaderNodeOutputMaterial' and node.is_active_output][0]
        # init bake set
        self.tree_parse()
        self.bake_images()
        self.obj.active_material = self.orign_mat
        bpy.data.materials.remove(self.mat)
        print(" Bake finish, save image or pack it yourself!")
        return{'FINISHED'}

    def mix_alpha(self, merge_image, alpha_image):
        pixels = list(merge_image.pixels)  # [:]
        alpha_pixels = alpha_image.pixels[:]
        for i in range(3, len(pixels), 4):  # TODO use numpy for faster
            pixels[i] = alpha_pixels[i-3]
        merge_image.pixels[:] = pixels
        merge_image.update()

    def node_group_new(self, group_name: str) -> ShaderNodeGroup:
        node = self.nodes.new('ShaderNodeGroup')
        node.node_tree = bpy.data.node_groups[group_name]
        return node

    def copy_input(self, input_copy_to, input_copy_from, copy_value=True):
        if input_copy_from.links:
            self.links.new(input_copy_to, input_copy_from.links[0].from_socket)
        elif copy_value:
            input_copy_to.default_value = input_copy_from.default_value
        return

    def tree_recurse_parse(self, bake_socket, link):
        '''
        parse node = link.from_node
        '''
        from_node = link.from_node
        to_node = link.to_node

        def copy_output(output_to, link):
            '''copy link to output_to'''
            if to_node.bl_idname == 'ShaderNodeOutputMaterial':
                for link in bake_socket.links:
                    self.links.new(output_to, link.to_socket)
            else:
                self.links.new(output_to,
                               link.to_socket)

        if bake_socket.name == 'Normal' or bake_socket.name == 'Clearcoat Normal':
            if from_node.bl_idname == 'ShaderNodeMixShader':
                convert_node = self.node_group_new('PBSH Normal Blend')
                copy_output(convert_node.outputs['Normal'], link)
                self.copy_input(convert_node.inputs['Fac'],
                                from_node.inputs['Fac'])
                self.copy_input(convert_node.inputs[1],
                                from_node.inputs[1], False)
                self.copy_input(convert_node.inputs[2],
                                from_node.inputs[2], False)
            elif from_node.bl_idname == 'ShaderNodeBsdfPrincipled':
                convert_node = self.nodes.new('ShaderNodeVectorMath')
                convert_node.inputs[0].default_value = Vector(
                    (0.216, 0.216, 1.0))
                convert_node.inputs[1].default_value = Vector((0, 0, 0))
                copy_output(convert_node.outputs['Vector'], link)
                self.copy_input(convert_node.inputs[0],
                                from_node.inputs[bake_socket.name], False)
            elif from_node.outputs[0].type == 'SHADER':
                self.links.remove(link)
                return
            else:
                return
        elif bake_socket.type == 'VECTOR':
            if from_node.bl_idname == 'ShaderNodeMixShader':
                convert_node = self.nodes.new('ShaderNodeMixRGB')
                copy_output(convert_node.outputs['Normal'], link)
                self.copy_input(convert_node.inputs['Fac'],
                                from_node.inputs['Fac'])
                self.copy_input(convert_node.inputs[1],
                                from_node.inputs[1], False)
                self.copy_input(convert_node.inputs[2],
                                from_node.inputs[2], False)
            elif from_node.bl_idname == 'ShaderNodeBsdfPrincipled':
                convert_node = self.nodes.new('ShaderNodeVectorMath')
                convert_node.inputs[1].default_value = Vector((0, 0, 0))
                copy_output(convert_node.outputs['Vector'], link)
                self.copy_input(convert_node.inputs[0],
                                from_node.inputs[bake_socket.name], False)
            elif from_node.outputs[0].type == 'SHADER':
                self.links.remove(link)
                return
            else:
                return
        elif bake_socket.type == 'RGBA':
            if from_node.bl_idname == 'ShaderNodeMixShader':
                convert_node = self.nodes.new('ShaderNodeMixRGB')
                copy_output(convert_node.outputs['Color'], link)
                self.copy_input(convert_node.inputs['Fac'],
                                from_node.inputs['Fac'])
                self.copy_input(convert_node.inputs[1],
                                from_node.inputs[1], False)
                self.copy_input(convert_node.inputs[2],
                                from_node.inputs[2], False)
            elif from_node.bl_idname == 'ShaderNodeBsdfPrincipled':
                convert_node = self.nodes.new('ShaderNodeMixRGB')
                convert_node.inputs['Fac'].default_value = 0
                copy_output(convert_node.outputs['Color'], link)
                self.copy_input(convert_node.inputs[1],
                                from_node.inputs[bake_socket.name])
            elif from_node.outputs[0].type == 'SHADER':
                self.links.remove(link)
                return
            else:
                return
        elif bake_socket.type == 'VALUE':
            if from_node.bl_idname == 'ShaderNodeMixShader':
                convert_node = self.node_group_new('PBSH Mix Value')
                copy_output(convert_node.outputs['Value'], link)
                self.copy_input(convert_node.inputs['Fac'],
                                from_node.inputs['Fac'])
                self.copy_input(convert_node.inputs[1],
                                from_node.inputs[1], False)
                self.copy_input(convert_node.inputs[2],
                                from_node.inputs[2], False)
            elif from_node.bl_idname == 'ShaderNodeBsdfPrincipled':
                convert_node = self.nodes.new('ShaderNodeMath')
                convert_node.inputs[1].default_value = 0
                copy_output(convert_node.outputs['Value'], link)
                self.copy_input(convert_node.inputs[0],
                                from_node.inputs[bake_socket.name])
            elif from_node.outputs[0].type == 'SHADER':
                self.links.remove(link)
                return
            else:
                return
        # TODO emission type
        for node_input in convert_node.inputs:
            for link in node_input.links:
                self.tree_recurse_parse(bake_socket, link)

    def tree_parse(self):
        # Principled BSDF Bake
        shader_bake_nodes = [node for node in self.nodes
                             if node.pbs_node_type == 'PBSH Principled BSDF Bake']
        for bake_node in shader_bake_nodes:
            for output in [output for output in bake_node.outputs if output.links]:
                link = self.output_node.inputs[0].links[0]
                self.tree_recurse_parse(output, link)
        # emisssion bake
        # displacement bake
        if self.output_node.inputs['Displacement'].links:
            shader_bake_nodes = [node for node in self.nodes
                                 if node.pbs_node_type == 'PBSH Displacement Bake']
            for bake_node in shader_bake_nodes:
                if not bake_node.outputs['Displacement'].links:
                    continue
                for link in output.links:
                    self.links.new(self.output_node.inputs['Displacement'].links[0].from_socket,
                                   link.to_socket)

    def bake_images(self):
        bake_image_nodes = [node for node in self.nodes
                            if node.pbs_node_type == 'PBSH Image Bake']
        emit_node = self.nodes.new('ShaderNodeEmission')
        self.links.new(emit_node.outputs['Emission'],
                       self.output_node.inputs['Surface'])
        for bake_image_node in bake_image_nodes:
            bake_image = bake_image_node.image
            if not bake_image_node.inputs[0].links:
                continue
            if not bake_image:
                self.report({'INFO'}, 
                            f'bake node "{bake_image_node.name}" missing image')
                continue
            before_bake_node = bake_image_node.inputs[0].links[0].from_node
            if before_bake_node.pbs_node_type == 'PBSH Mix Alpha':
                # bake color
                self.copy_input(emit_node.inputs['Color'],
                                before_bake_node.inputs['Color'])
                self.nodes.active = bake_image_node
                bpy.ops.object.bake(type='EMIT')
                # bake alpha
                self.copy_input(emit_node.inputs['Color'],
                                before_bake_node.inputs['Alpha'])
                alpha_tmp = bpy.data.images.new('alpha.tmp',
                                                bake_image.size[0],
                                                bake_image.size[1],
                                                alpha=False,
                                                float_buffer=bake_image.is_float)
                bake_alpha_node = self.nodes.new(type='ShaderNodeTexImage')
                bake_alpha_node.image = alpha_tmp
                self.nodes.active = bake_alpha_node
                bpy.ops.object.bake(type='EMIT')
                # mix alpha+color
                self.mix_alpha(bake_image, alpha_tmp)
                bpy.data.images.remove(alpha_tmp)
            else:
                self.copy_input(emit_node.inputs['Color'],
                                bake_image_node.inputs[0])
                self.nodes.active = bake_image_node
                bpy.ops.object.bake(type='EMIT')


# ((id, name, dest),...) node group name==id
PBS_NODE_TYPES = (('Build In', 'Build In', ''),
                  ('PBSH Emission Bake', 'PBSH Emission Bake', ''),
                  ('PBSH Principled BSDF Bake', 'PBSH Principled BSDF Bake', ''),
                  ('PBSH Displacement Bake', 'PBSH Displacement Bake', ''),
                  ('PBSH Image Bake', 'PBSH Image Bake', ''),
                  ('PBSH Mix Alpha', 'PBSH Mix Alpha', ''))

PBS_NODE_ADD_TYPES = (
    ('PBSH Emission Bake', 'PBSH Emission Bake', ''),
    ('PBSH Principled BSDF Bake', 'PBSH Principled BSDF Bake', ''),
    ('PBSH Displacement Bake', 'PBSH Displacement Bake', ''),
    ('PBSH Image Bake', 'PBSH Image Bake', ''),
    ('PBSH Mix Alpha', 'PBSH Mix Alpha', ''))


class FixData(Operator):
    '''Add godot bake preset,fix broken link node group'''
    bl_label = "Fix Data"
    bl_idname = "pbs_helper.fix_data"
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT' and
                space.node_tree)

    def execute(self, context):
        data_path = os.path.join(os.path.dirname(__file__), 'data.blend')
        #rm orgin library
        
        with bpy.data.libraries.load(data_path, link=True) as (data_from, data_to):
            data_to.node_groups = data_from.node_groups
        mats = context.materials
        for mat in mats:
            tree = mat.node_tree
            nodes = tree.nodes
            for node in nodes:
                if node.pbs_node_type != 'Build In' and node.bl_idname == 'ShaderNodeGroup':
                    node.node_tree = bpy.data.node_groups[node.pbs_node_type]
        return {"FINISHED"}


class AddPBSHplerNode(Operator):
    bl_idname = 'pbs_helper.add_shader_bake_node'
    bl_label = 'Add A PBS Helper Node'
    node_type: EnumProperty(items=PBS_NODE_ADD_TYPES,
                            default='PBSH Image Bake',
                            name='PBS Node Type')

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT' and
                space.node_tree)

    def execute(self, context):
        if self.node_type == 'Build In':
            return {'CANCELLED'}
        data_path = os.path.join(os.path.dirname(
            __file__), 'data.blend')  # TODO to be func load all
        with bpy.data.libraries.load(data_path, link=True) as (data_from, data_to):
            data_to.node_groups = data_from.node_groups
        obj = context.active_object
        mat = obj.active_material
        tree = mat.node_tree
        nodes = tree.nodes
        if self.node_type == 'PBSH Image Bake':
            bpy.ops.node.add_node('INVOKE_DEFAULT', type="ShaderNodeTexImage")
            node = nodes.active
        else:
            bpy.ops.node.add_node('INVOKE_DEFAULT',
                                  type="ShaderNodeGroup",)
            node = nodes.active
            node.node_tree = bpy.data.node_groups[self.node_type]
        node.pbs_node_type = self.node_type
        bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        return {'FINISHED'}


class PBS_HELPER_PT_tools(Panel):
    '''Material bake tools'''
    bl_space_type = 'NODE_EDITOR'
    bl_label = "PBS Helper"
    bl_category = 'PBS Helper'
    bl_region_type = 'UI'
    #bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'CYCLES'}
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.tree_type == 'ShaderNodeTree' and
                space.shader_type == 'OBJECT')
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("pbs_helper.bake")
        row = layout.row()
        row.operator("pbs_helper.fix_data")


def pbs_node_type_set(self, context):
    '''Add pbs_node_type set to node properties'''
    nodes = context.active_node.id_data.nodes
    layout = self.layout
    node = nodes.active
    if node.bl_idname == 'ShaderNodeGroup' or node.bl_idname == 'ShaderNodeTexImage':
        row = layout.row()
        row.prop(node, 'pbs_node_type')


def add_PBS_helper_nodes(self, context):
    '''Add PBSH node to shader editor -> add menu'''
    space = context.space_data
    if (space.type == 'NODE_EDITOR' and
        space.tree_type == 'ShaderNodeTree' and
        space.shader_type == 'OBJECT' and
        space.node_tree):
        self.layout.operator_menu_enum(AddPBSHplerNode.bl_idname,
                                   "node_type",
                                   text="PBS helper Nodes")


classes = [
    BakeMaterial,
    AddPBSHplerNode,
    PBS_HELPER_PT_tools,
    FixData
]


def register():
    bpy.types.ShaderNode.pbs_node_type = EnumProperty(items=PBS_NODE_TYPES,
                                                      name='PBS Node Type',
                                                      default='Build In')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.NODE_MT_add.append(add_PBS_helper_nodes)
    bpy.types.NODE_PT_active_node_properties.append(pbs_node_type_set)


def unregister():
    del bpy.types.ShaderNode.pbs_node_type
    bpy.types.NODE_MT_add.remove(add_PBS_helper_nodes)
    bpy.types.NODE_PT_active_node_properties.remove(pbs_node_type_set)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
