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

import bpy

class MaskModifierAdd(bpy.types.Operator):
    """ Add a mask modifier for the selected verts """
    bl_idname = 'mesh.mask_modifier_add'
    bl_label = 'Add Mask modifier'

    group_name = bpy.props.StringProperty(
        default="group",name="group name", description="Name of Group to Hide")

    animation = bpy.props.EnumProperty(
        items =[('NONE','no animation', "Don't set keyframes", 0),
        ('FORWARD', 'switch on', 'Hide group at current frame', 1),
        ('BACKWARD', 'switch off', 'Reveal group at current frame', 2)],
        name="Animate",
        description="Turn the modifier on or off at the current frame")


    @classmethod
    def poll(cls, context):
        return context.object and context.mode == 'EDIT_MESH'

    def execute(self, context):
        ob = context.object
        scene = context.scene
        name = self.properties.group_name
        animate = self.properties.animation

        top_mask = top_subsurf = 0
        for index, mod in enumerate(ob.modifiers):
            if mod.type == 'MASK':
                top_mask = index
            elif mod.type == 'SUBSURF':
                top_subsurf = index
        my_index = max(top_mask + 1, top_subsurf - 1)
        # create a new group based on selected verts
        bpy.ops.object.editmode_toggle()
        group = ob.vertex_groups.new(name=name)
        group.add(
            [v.index for v in ob.data.vertices if v.select], 1.0, 'REPLACE')
        # create a modifier hiding that group
        mod = ob.modifiers.new(name=name, type='MASK')
        mod.vertex_group = group.name
        mod.invert_vertex_group = True
        # move modifier in the stack adjacent to other mask modifiers
        for idx in range(len(ob.modifiers), my_index, -1):
            bpy.ops.object.modifier_move_up(modifier=mod.name)
        # optionally:
        # animate modifier visibility based on settings and current frame
        if animate != 'NONE':
            data_path = 'modifiers["{}"].show_viewport'.format(mod.name)
            mod.show_viewport = animate != 'FORWARD'
            ob.keyframe_insert(data_path, -1, scene.frame_start)
            mod.show_viewport = animate == 'FORWARD'
            ob.keyframe_insert(data_path, -1)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    layout = self.layout
    row = layout.row()
    row.operator_context = 'INVOKE_DEFAULT'
    row.operator(MaskModifierAdd.bl_idname, text="Add Mask", icon="PLUGIN")
    layout.separator()

def register():
    bpy.utils.register_class(MaskModifierAdd)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)

def unregister():
    bpy.utils.unregister_class(MaskModifierAdd)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
