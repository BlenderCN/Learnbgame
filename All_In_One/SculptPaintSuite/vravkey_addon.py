#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

# <pep8-80 compliant> (or attempting to be)

bl_info = {
    "name": "VravKey Addon",
    "description": "Smattering of tools to be assigned to custom hotkeys.",
    "author": "Jean Ayer (vrav)", # legal / tracker name: Cody Burrow
    "version": (0, 5, 1),
    "blender": (2, 80, 0),
    "location": "User Preferences > Keymap",
    "category": "System"
}

# Not intended for release, created for personal use

# Commands available to assign:
#   Object Mode - object.transforms_clear
#   Sculpt Mode - sculpt.brush_direction_toggle
#   Sclpt/Paint - brush.pressure_toggle
#   Edit (Mesh) - mesh.merge_context
#   Edit (Mesh) - mesh.delete_context
#   Edit (Mesh) - mesh.delete_context_special

# Menus available to assign:
#   Object Mode - wm.call_menu, OBJECT_MT_ClearTransMenu
#   Pose Mode   - wm.call_menu, OBJECT_MT_ClearTransMenu

# Known bugs:
#   - with brush.pressure_toggle, the tool pane doesn't always update visually

# TODO:
#   - Wrap-to-start and wrap-to-end when cursoring through frame start/end
#   - Center to 3D cursor when in camera affected by moving frames? or center to selection

import bpy

# Clear all transforms of selected objects
# Intended for use in Object Mode
class OBJECT_OT_transforms_clear(bpy.types.Operator):
    bl_idname = "object.transforms_clear"
    bl_label = "Clear All Transforms"
    
    def execute(self, context):
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()
        return {'FINISHED'}

# Menu which contains transform clear options
# Usable in Object and Pose mode
class OBJECT_MT_ClearTransMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_ClearTransMenu"
    bl_label = "Clear Transform"
    
    def draw(self, context):
        if context.mode == 'OBJECT':
            layout = self.layout
            layout.operator("object.location_clear", text="Clear Location")
            layout.operator("object.rotation_clear", text="Clear Rotation")
            layout.operator("object.scale_clear", text="Clear Scale")
            layout.separator()
            layout.operator("object.transforms_clear",text="Clear All")
        elif context.mode == 'POSE':
            layout = self.layout
            layout.operator("pose.loc_clear", text="Clear Pose Location")
            layout.operator("pose.rot_clear", text="Clear Pose Rotation")
            layout.operator("pose.scale_clear", text="Clear Pose Scale")
            layout.separator()
            layout.operator("pose.transforms_clear", text="Clear Pose")

# Invert enum value in tool_settings.sculpt.brush.direction
# Reads from hardcoded lists, could do this differently
class SCULPT_OT_brush_direction_toggle(bpy.types.Operator):
    bl_idname = "sculpt.brush_direction_toggle"
    bl_label = "Sculpt Brush Direction Toggle"
    bl_description = "Inverts active sculpt brush"
    
    def execute(self, context):
        brush_settings = context.tool_settings.sculpt.brush
        add_list = ('ADD','FILL','PINCH','SCRAPE','FLATTEN','INFLATE')
        sub_list = ('SUBTRACT','DEEPEN','MAGNIFY','PEAKS','CONTRAST','DEFLATE')
        
        # For brushes that have no direction. Still spams console with warning.
        # The same spam occurs when accessing this on a no-dir brush
        #   via the python console. Possibly a blender bug.
        if len(brush_settings.direction) > 0:
            i = 0
            while i < 6: # length of add and sub lists
                if brush_settings.direction == add_list[i]:
                    brush_settings.direction = sub_list[i]
                    return {'FINISHED'}
                if brush_settings.direction == sub_list[i]:
                    brush_settings.direction = add_list[i]
                    return {'FINISHED'}
                i += 1
        else:
            return {'CANCELLED'}

# Invert each pressure toggle on active brush
# Compatible with unified brush settings
class PAINT_OT_pressure_toggle(bpy.types.Operator):
    bl_idname = "brush.pressure_toggle"
    bl_label = "Brush Pressure Toggle"
    bl_description = "Toggles both size and strength pressure sensitivity."
    
    def execute(self, context):
        unify_settings = context.tool_settings.unified_paint_settings
        brush_settings = context.tool_settings.sculpt.brush
        
        # size pressure toggle
        uni = unify_settings.use_unified_size
        if uni:
            uni = unify_settings.use_pressure_size
            if uni:
                unify_settings.use_pressure_size = False
            else:
                unify_settings.use_pressure_size = True
        else:
            uni = brush_settings.use_pressure_size
            if uni:
                brush_settings.use_pressure_size = False
            else:
                brush_settings.use_pressure_size = True
        
        # strength pressure toggle
        uni = unify_settings.use_unified_strength
        if uni:
            uni = unify_settings.use_pressure_strength
            if uni:
                unify_settings.use_pressure_strength = False
            else:
                unify_settings.use_pressure_strength = True
        else:
            uni = brush_settings.use_pressure_strength
            if uni:
                brush_settings.use_pressure_strength = False
            else:
                brush_settings.use_pressure_strength = True
        
        return {'FINISHED'}

# Merge in Edit Mode with different settings for verts, edges, faces
# Possible modes: FIRST, LAST, CURSOR, CENTER, COLLAPSE
class EDIT_OT_merge_context(bpy.types.Operator):
    bl_idname = "mesh.merge_context"
    bl_label = "Merge Context Sensitive"
    bl_description = "Applies different merge types for different selections"
    
    def execute(self, context):
        if context.tool_settings.mesh_select_mode[0] == (True): #Vertex Mode
            # This is not good
            try: bpy.ops.mesh.merge(type='LAST', uvs=True)
            except: bpy.ops.mesh.merge(type='CENTER', uvs=True)
        if context.tool_settings.mesh_select_mode[1] == (True): #Edge Mode
            bpy.ops.mesh.merge(type='COLLAPSE', uvs=True)
        if context.tool_settings.mesh_select_mode[2] == (True): #Face Mode
            bpy.ops.mesh.merge(type='CENTER', uvs=True)
        return {'FINISHED'}

# Performs delete command in Edit Mode in a context-sensitive manner
# Possible types: VERT, EDGE, FACE, ALL, EDGE_FACE, ONLY_FACE, EDGE_LOOP
class EDIT_OT_delete_context(bpy.types.Operator):
    bl_idname = "mesh.delete_context"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = "Delete Context Sensitive"
    bl_description = "Applies different deletion types per selection mode."
    
    def execute(self, context):
        if context.tool_settings.mesh_select_mode[0] == (True):
            bpy.ops.mesh.delete(type='VERT')
        elif context.tool_settings.mesh_select_mode[1] == (True):
            bpy.ops.mesh.delete(type='EDGE')
        elif context.tool_settings.mesh_select_mode[2] == (True):
            bpy.ops.mesh.delete(type='FACE')
        return {'FINISHED'}

# A secondary set of context-sensitive deletions according to selection type
# Possible types: VERT, EDGE, FACE, ALL, EDGE_FACE, ONLY_FACE, EDGE_LOOP
class EDIT_OT_delete_context_special(bpy.types.Operator):
    bl_idname = "mesh.delete_context_special"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = "Delete Context Sensitive Special"
    bl_description = "Applies different deletion types per selection mode."
    
    def execute(self, context):
        if context.tool_settings.mesh_select_mode[0] == (True):
            bpy.ops.mesh.delete(type='EDGE_FACE')
        elif context.tool_settings.mesh_select_mode[1] == (True):
            bpy.ops.mesh.delete_edgeloop()
        elif context.tool_settings.mesh_select_mode[2] == (True):
            bpy.ops.mesh.delete(type='ONLY_FACE')
        return {'FINISHED'}
#

classes = (
    OBJECT_OT_transforms_clear,
    OBJECT_MT_ClearTransMenu,
    SCULPT_OT_brush_direction_toggle,
    PAINT_OT_pressure_toggle,
    EDIT_OT_merge_context,
    EDIT_OT_delete_context,
    EDIT_OT_delete_context_special,
)
register, unregister = bpy.utils.register_classes_factory(classes)
