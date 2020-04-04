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

bl_info = {
    "name": "Rotate UV Selection",
    "description": "Rotate UV selection left or right by 90 degrees",
    "author": "Ray Mairlot",
    "version": (1, 1, 2),
    "blender": (2, 72, 0),
    "location": "UV/Image Editor > Shift+R or Ctrl+Shift+R",
    "category": "Learnbgame",
}
    
import bpy   
from math import radians 

modifierKeys = ["any", "shift", "ctrl", "alt", "oskey"] # "type", "key_modifier"]

operators = [
            ["Rotate UV Selection Left", "uv.rotate_selection_left"],
            ["Rotate UV Selection Right", "uv.rotate_selection_right"]
            ]      

#User preferences appear under addon when enabled      
class RotateUVPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  
    
    uv_rotation_angle = bpy.props.IntProperty(name="UV Rotation Angle",default=90,description="Angle by which to rotate the selected UVs by")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "uv_rotation_angle")
        row.label("")
        row.label("")
                
        row = layout.row()
        row.label("Shortcuts:")

        for operator in operators:
            
            row = layout.row()
            row.label(operator[0]+":")
            
            row.operator("wm.edit_shortcut", text="Edit Shortcut").shortcut = operator[1]


class RotateUVLeftOperator(bpy.types.Operator):
    """ Rotate UV selection to the left """
    bl_idname = "uv.rotate_selection_left"
    bl_label = "Rotate UV Selection Left"
    bl_options = {"UNDO"}

    def execute(self, context):
        main(context,"Left")
        return {'FINISHED'}
    
    
class RotateUVRightOperator(bpy.types.Operator):
    """ Rotate UV selection to the right """
    bl_idname = "uv.rotate_selection_right"
    bl_label = "Rotate UV Selection Right"
    bl_options = {"UNDO"}    

    def execute(self, context):
        main(context, "Right")
        return {'FINISHED'}    
    
    
class EditShortcutOperator(bpy.types.Operator):
    """ Edit shortcuts for this addon """
    bl_idname = "wm.edit_shortcut"
    bl_label = "View and edit shortcuts for this addon"

    shortcut = bpy.props.StringProperty()

    def execute(self, context):
        editShortcuts(self,context)
        return {'FINISHED'} 


#Same function used for both operators, pass in direction
def main(context, direction=""):
    
    #Get user preference value and convert to radians
    angle = radians(bpy.context.user_preferences.addons['UV Rotate'].preferences.uv_rotation_angle)
        
    if direction=="Left":
        bpy.ops.transform.rotate(value=-angle)
    else:
        bpy.ops.transform.rotate(value=angle)        


def editShortcuts(self,context):
    
    bpy.context.user_preferences.active_section = 'INPUT'
    context.area.spaces[0].filter_text = self.shortcut#"Rotate UV Selection"
    
    bpy.context.window_manager.keyconfigs.addon.keymaps['Image'].keymap_items[self.shortcut].show_expanded = True
    

keymaps = []

def register():

    bpy.utils.register_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:

        km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new("uv.rotate_selection_left", 'R', 'PRESS', ctrl=True, shift=True)
        keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new("uv.rotate_selection_right", 'R', 'PRESS', shift=True)
        keymaps.append((km, kmi))

def unregister():

    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
