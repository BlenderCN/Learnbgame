import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
import json

bl_info = {
    "name": "Multicam Export",
    "author": "Matt Reid",
    "version": (0, 0, 1),
    "blender": (2, 74, 0),
    "description": "Export Multicam Sequence", 
    "warning": "",
    "location": "File > Export > Export Multicam",
    "category": "Import-Export",
}

def get_multicam():
    return bpy.context.selected_sequences[0]

def get_mc_fcurve(mc):
    mc_path = mc.path_from_id()
    action = bpy.context.scene.animation_data.action
    for fc in action.fcurves.values():
        if mc_path not in fc.data_path:
            continue
        if 'multicam_source' not in fc.data_path:
            continue
        return fc
    
def iter_keyframes(fc):
    for kf in fc.keyframe_points.values():
        yield kf.co
    
def export_multicam(filename):
    mc = get_multicam()
    fc = get_mc_fcurve(mc)
    keyframes = {}
    for frame, value in iter_keyframes(fc):
        keyframes[frame] = value
    with open(filename, 'w') as f:
        f.write(json.dumps(keyframes, indent=2))

class MulticamExport(Operator, ExportHelper):
    '''Export the active Multicam strip keyframes'''
    bl_idname = 'multicam_export.export'
    bl_label = 'Multicam Export'
    filename_ext = '.json'
    def execute(self, context):
        export_multicam(self.filepath)
        return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(MulticamExport.bl_idname, text='Export Multicam')
    
def register():
    bpy.utils.register_class(MulticamExport)
    bpy.types.INFO_MT_file_export.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(MulticamExport)
    bpy.types.INFO_MT_file_export.remove(menu_func)
    
if __name__ == '__main__':
    register()

    
