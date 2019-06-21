
"""hka export operator
"""

import os
import subprocess

import bpy
from bpy_extras.io_utils import ExportHelper
from io_anim_hkx.hka_export import export_hkafile


class hkaExportOperator(bpy.types.Operator, ExportHelper):
    """Export a hkaAnimationContainer file
    """
    bl_idname = "export_anim.hkx"

    bl_label = "Export hkx"

    filename_ext = ".hkx"
    filter_glob = bpy.props.StringProperty(default="*.hkx", options={'HIDDEN'})

    def execute(self, context):
        dirname = os.path.dirname(os.path.abspath(__file__))

        skeleton_file = dirname + "/resources/skeleton.bin"
        anim_hkx_file = self.properties.filepath

        basename = os.path.basename(anim_hkx_file)
        basename, extension = os.path.splitext(basename)
        anim_bin_file = dirname + '/tmp/' + basename + '.bin'

        export_hkafile(skeleton_file, anim_bin_file)

        command = dirname + '/bin/hkconv.exe'
        process = subprocess.run([command, '-o', anim_hkx_file, anim_bin_file])

        return {'FINISHED'}
