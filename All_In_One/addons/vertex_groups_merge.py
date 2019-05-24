 # ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# copyright (c) 2015 urchn.org,
# Bassam Kurdali

# Add Vertex Groups Together

bl_info = {
    "name": "Vertex Weights Add",
    "author": "Bassam Kurdali",
    "version": (0, 0),
    "blender": (2, 76, 0),
    "location": "View3D > Tools > Weight Tools",
    "description": "Add Another Vertex Group into the Active One",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

"""
Add Another Vertex Group into the Active One
"""

import bpy


def get_verts_in_group(vertices, weight_group):
    """ List weights as floats or None if vertex not in weight_group """
    v_list = []
    index = weight_group.index
    for vert in vertices:
        # print(vert.index)
        result = [
            vertex_group.weight for vertex_group in vert.groups
            if vertex_group.group == index]
        if result:
            v_list.append(result[0])
        else:
            v_list.append(None)
    return v_list


def merge_weights_to_group(ob, target_group, source_group, blend_mode):
    """ merge source weights into target group using blend_mode """
    vertices = ob.data.vertices
    source_weights = get_verts_in_group(vertices, source_group)
    target_weights = get_verts_in_group(vertices, target_group)
    new_weights = []
    for idx, weights in enumerate(zip(source_weights, target_weights)):
        non_zeros = [w for w in weights if w is not None]
        if non_zeros:
            target_group.add([idx], sum(non_zeros), 'REPLACE') # TODO blend_mode


def get_weight_groups(self, context):
    return [tuple([g.name] * 3) for g in context.object.vertex_groups]


class WeightGroupMerge(bpy.types.Operator):
    """ Merge Source Weights into Active Weight Group """
    bl_idname = 'object.vertex_group_merge_weights'
    bl_label = "Vertex Group Merge Weights"

    source_group = bpy.props.EnumProperty(
        items=get_weight_groups, name='Blend From Group')
    blend_mode = bpy.props.EnumProperty(
        items=[("ADD", "Add", "Add Source to Active", 0)],
        name='Blend Mode')
    
    @classmethod
    def poll(cls, context):
        return (
            context.object and
            context.object.type == 'MESH' and
            context.object.vertex_groups.active)
    
    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ob = context.object
        target_group = ob.vertex_groups.active
        source_group = ob.vertex_groups[self.source_group]
        merge_weights_to_group(ob, target_group, source_group, self.blend_mode)
        return {'FINISHED'}


def draw_func(self, context):
    """ Add Operator to Panel """
    col = self.layout.column()
    col.operator(
        WeightGroupMerge.bl_idname, text="Merge Weights")


def register():
    bpy.utils.register_class(WeightGroupMerge)
    bpy.types.VIEW3D_PT_tools_weightpaint.append(draw_func)
    bpy.types.VIEW3D_PT_tools_meshweight.append(draw_func)


def unregister():
    bpy.types.VIEW3D_PT_tools_meshweight.remove(draw_func)
    bpy.types.VIEW3D_PT_tools_weightpaint.remove(draw_func)
    bpy.utils.unregister_class(WeightGroupMerge)

if __name__ == "__main__":
    register()             
