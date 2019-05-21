
import os
import time

import bpy
import bpy_extras

from . import read


class StalkerImportOGFOperator(
        bpy.types.Operator, bpy_extras.io_utils.ImportHelper):

    bl_idname = 'xray_import.ogf'
    bl_label = 'Import *.ogf'
    bl_options = {'REGISTER', 'UNDO'}

    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement
    )
    filter_glob = bpy.props.StringProperty(default='*.ogf', options={'HIDDEN'})

    def execute(self, context):

        io_scene_xray_addon = bpy.context.user_preferences.addons.get(
            'io_scene_xray'
        )

        try:

            import io_scene_xray

            has_io_scene_xray = True

        except ImportError:
            has_io_scene_xray = False

        if not io_scene_xray_addon or not has_io_scene_xray:
            self.report({'WARNING'}, 'Cannot find "io_scene_xray" addon')
            return {'FINISHED'}

        start_time = time.time()
        for file in self.files:
            read.file(os.path.join(self.directory, file.name))
        print('total time: ', time.time() - start_time)

        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)
