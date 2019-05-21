######################## add-in info ######################

bl_info = {
    "name": "Convert KBAP Paths to POLY",
    "category": "Mesh",
    "author": "Julian Ewers-Peters"
}

######################## imports ##########################

import bpy
import bpy.types
import os.path
import struct

######################## main #############################

class PathConverter(bpy.types.Operator):
    """Convert KBAP Paths to POLY"""
    bl_idname   = "export.convert_paths"
    bl_label    = "Convert KBAP Paths to POLY"
    bl_options  = {'REGISTER'}

    def execute(self, context):
        ## get list of objects from scene ##
        object_list = list(bpy.data.objects)

        for scene_obj in object_list:
            if scene_obj.type == 'CURVE' and scene_obj.name[:5] == 'kbap_':
                scene_obj.data.splines[0].type = 'POLY'
                scene_obj.data.twist_mode = 'Z_UP'
        
        return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(PathConverter.bl_idname, text="Convert KBAP Paths to POLY");

######################## add-in functions #################

def register():
    bpy.utils.register_class(PathConverter)
    bpy.types.INFO_MT_file_export.append(menu_func);
    
def unregister():
    bpy.utils.unregister_class(PathConverter)
    bpy.types.INFO_MT_file_export.remove(menu_func);

if __name__ == "__main__":
    register()