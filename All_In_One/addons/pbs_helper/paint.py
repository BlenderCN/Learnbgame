import bpy
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
'''
helper for PBR paint workflow
'''


from bpy.types import (
    Operator,
    PropertyGroup,
    AddonPreferences,
    ShaderNodeGroup
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

# brush lib


class Paint2Node(Operator):
    '''Sync paint texture with active node'''
    bl_idname = "pbs_helper.paint2node"
    bl_label = "Paint to Active Node"
    custom_event: bpy.props.EnumProperty(
        name="Event",
        items=(('EXIT', 'EXIT', ''),
               ('NONE', 'NONE', '')
               ),
        default='NONE'
    )

    def __init__(self):
        self.sync_paint_node = True  # context.preferences.sync_paint_node
        self.active_node = bpy.context.active_object.active_material.node_tree.nodes.active

    def __del__(self):
        print('run __del__')

    @classmethod
    def poll(cls, context): 
        return True
        brush = context.tool_settings.image_paint.brush
        ob = context.active_object
        return (brush is not None and ob is not None)

    def modal(self, context, event):
        mat = context.active_object.active_material
        active_node = mat.node_tree.nodes.active
        if mat.paint_active_slot change
        slot -> node.select = True
        if active_node != self.active_node:
            if context.tool_settings.image_paint.mode == 'MATERIAL' and active_node.bl_idname == 'ShaderNodeTexImage' and active_node.image:
                self.active_node = active_node
                mat.node_tree.nodes.update()
                mat.paint_active_slot = mat.texture_paint_images.find(
                    active_shader_node)
        if not self.sync_paint_node:
            return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


classes = [Paint2Node]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# for test
if __name__ == "__main__":
    register()
    bpy.ops.pbs_helper.paint2node('INVOKE_DEFAULT')
