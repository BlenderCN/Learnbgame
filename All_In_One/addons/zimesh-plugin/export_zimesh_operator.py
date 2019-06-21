import bpy
import bpy_extras
import json

from .data_packer import *

class ZimeshJSONWriter:
    def write(self, packedData, filepath):
        try:
            fileStream = open(filepath, 'w')
            json.dump(packedData, fileStream, indent=4, sort_keys=True)
            fileStream.close()
        except IOError:
            return False
        return True

class ExportZimesh(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = 'export.zimesh'
    bl_label = 'Export Zimesh JSON'


    # ExportHelper mixin class uses this
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(default='*.json', options={'HIDDEN'})

    selectedOnly = bpy.props.BoolProperty(
        name="Selected only",
        description="Export only selected objects.",
        default=True
    )

    packer = DataPacker()
    writer = ZimeshJSONWriter()

    def execute(self, context):
        packedData = self.packer.packData(self, context)
        self.writer.write(packedData, self.filepath)

        return {'FINISHED'}
