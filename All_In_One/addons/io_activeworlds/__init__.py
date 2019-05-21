import os
import json
import bpy
from bpy_extras.io_utils import ImportHelper

from .awsequences.sequence import Sequence

EXTENSION = '.seq'

DATA_PATH_FORMAT = 'pose.bones["%s"].rotation_quaternion'

bl_info = {
    'name': 'Active Worlds Avatar Sequence',
    'author': 'John Groszko',
    'version': (0, 0, 1),
    'blender': (2, 67, 0),
    'location': 'File > Import-Export',
    'description': 'Import Active Worlds avatar sequence files',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Import-Export',
}

class ImportSeq(bpy.types.Operator, ImportHelper):
    bl_idname = 'import.activeworldsseq'
    bl_label = 'Import Active Worlds Sequence'

    filename_ext = EXTENSION

    def execute(self, context):
        sequence = Sequence.from_file(self.properties.filepath)
        name = os.path.splitext(
            os.path.basename(
                self.properties.filepath
            )
        )[0]

        import pdb; pdb.set_trace()

        obj = bpy.context.object
        obj.animation_data_create()

        obj.animation_data.action = bpy.data.actions.new(name=name)

        for _, joint in sequence.joints.items():
            print(DATA_PATH_FORMAT % joint['name'])
            fcu_rotation = [
                obj.animation_data.action.fcurves.new(
                    data_path=DATA_PATH_FORMAT % joint['name'],
                    index=i,
                    action_group=joint['name']
                )
                for i in range(0, 4)]
            
            [fcu.keyframe_points.add(len(joint['frames']))
             for fcu in fcu_rotation]

            for i, frame in enumerate(joint['frames']):
                for ii in range(0, 4):
                    fcu_rotation[ii].keyframe_points[i].co = (
                        frame['frame'],
                        frame['quat'][ii]
                    )

        return {'FINISHED'}

def menu_func_import(self, context):
    default_path = bpy.data.filepath.replace('.blend', EXTENSION)
    text = 'Active Worlds Avatar Sequence (%s)' % EXTENSION
    operator = self.layout.operator(ImportSeq.bl_idname, text=text)
    operator.filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__=='__main__':
    register()
