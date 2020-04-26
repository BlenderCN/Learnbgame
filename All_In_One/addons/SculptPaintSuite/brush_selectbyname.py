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

bl_info = {
    "name": "Brush Select By Name",
    "description": "Cycle through specific brushes based on their names.",
    "author": "Jean Ayer (vrav)", # legal / tracker name: Cody Burrow
    "version": (0, 5, 3),
    "blender": (2, 80, 0),
    "location": "User Preferences > Keymap > add 'brush.set_by_name'",
    "category": "Paint"
}

# brush_selectbyname.py
# brush.select_by_name for hotkeys
# USAGE:
# Assign brush.set_by_name to a hotkey in User Settings > Input.
# Enter the names of the brushes for this key to cycle through.
# Examples:
#   Clay,Clay Strips,Draw
#   Flatten/Contrast,Polish
#   Grab,Snake Hook

# Known bugs:
#   In 2.80 beta, the brush settings bar above the viewport doesn't redraw.
#     Nonetheless, the brush is changed and it redraws on mouseover.
#   Loading the addon complains about brushnames not being annotated. Not sure how to fix.

import bpy

class PAINT_OT_select_by_name(bpy.types.Operator):
    bl_idname = "brush.select_by_name"
    bl_label = "Set Brush by Name"
    bl_options = {'INTERNAL'}
    
    brushnames = bpy.props.StringProperty(
        name        = "Names",
        description = "Brushes to cycle separated by commas (ie: Clay,Clay Strips,Draw).",
        default     = "Clay,Clay Strips,Draw",
        subtype     = 'NONE')
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D'
            and context.mode in {'SCULPT', 'PAINT_WEIGHT', 'PAINT_VERTEX', 'PAINT_TEXTURE'})
        
    def execute(self, context):
        if context.mode == 'SCULPT':
            ts = context.tool_settings.sculpt
        elif context.mode == 'PAINT_WEIGHT':
            ts = context.tool_settings.weight_paint
        elif context.mode == 'PAINT_VERTEX':
            ts = context.tool_settings.vertex_paint
        elif context.mode == 'PAINT_TEXTURE':
            ts = context.tool_settings.image_paint
        
        current = ts.brush.name
        names = self.brushnames.split(',')
        
        if len(names) == 1:
            if names[0] == current:
                pass
            elif names[0] in bpy.data.brushes:
                ts.brush = bpy.data.brushes[names[0]]
            return {'FINISHED'}
        
        select_next = False;
        
        for name in names:
            name = name.strip()
        
        i=0
        for name in names:
            if select_next:
                if name in bpy.data.brushes:
                    ts.brush = bpy.data.brushes[name]
                break
            if current == name:
                select_next = True
            i+=1
        
        if ts.brush.name == current:
            if  bpy.data.brushes.__contains__(names[0]):
                ts.brush = bpy.data.brushes[names[0]]
        
        return {'FINISHED'}
        
classes = (
    PAINT_OT_select_by_name,
)
register, unregister = bpy.utils.register_classes_factory(classes)
