######################################################################    
# Author: IK3D -- Issanou Kamardine                                                 
# License: GPL v3                                                  
######################################################################


bl_info = {
    "name": "Sculpt Broshes",
    "author": "IK3D",
    "version": (0, 7),
    "blender": (2,80,0),
    "location": "View 3D > Sculpt mod > Tool",
    "description": "UI Palette sculpt brush",
    "category": "Learnbgame",
}
    

if "bpy" in locals():
    import imp
    imp.reload(main_brush)
    

import bpy
from bpy.props import *
import os

root = bpy.utils.script_path_user()
sep = os.sep


#charger le script main_brush.py
def execscript():
    lien = root + sep + "addons" + sep + "sculpt_brushes" + sep + "main_brush.py"
    bpy.ops.script.python_file_run( filepath = lien )

#operateur charger main_brush.py
class ReloadOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.reload_operator"
    bl_label = "Reload Brushes"
 
    def execute(self, context):
        if bpy.context.mode == 'SCULPT':
            execscript()
        else:
            bpy.ops.sculpt.sculptmode_toggle()
            execscript()
        return {'FINISHED'}

    
#charger le script main_brush.py
def gosculpt():
    bpy.ops.script.python_file_run( filepath = lien )


 
#layout afichage de brosse
class BrushPanel(bpy.types.Panel):
    bl_label = "Brushes"
    bl_idname = "Brushes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Brushes"
    

    def draw(self, context):
        if bpy.context.mode == 'SCULPT':
            layout = self.layout
            row = layout.row()
            row.scale_y = 1.2
            row.operator("object.reload_operator", icon = 'FILE_REFRESH')
        else:
            layout = self.layout
            row = layout.row()
            row.scale_y = 1.2
            row.operator("object.reload_operator", text= 'Sculpt Mode', icon = 'SCULPTMODE_HLT')


       

def register():
    bpy.utils.register_class(ReloadOperator)
    bpy.utils.register_class(BrushPanel)

def unregister():
    bpy.utils.unregister_class(ReloadOperator)
    bpy.utils.unregister_class(BrushPanel)


if __name__ == "__main__":
    register()



    