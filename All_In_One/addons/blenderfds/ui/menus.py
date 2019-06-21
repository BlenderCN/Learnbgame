"""BlenderFDS, Blender menus"""

import bpy
import os.path
from bpy_extras.io_utils import ExportHelper, ImportHelper
from blenderfds.lib import io

### Export to FDS

def export_fds_menu(self, context):
    """Export FDS menu funtion"""
    # Prepare default filepath
    filepath = "{0}.fds".format(os.path.splitext(bpy.data.filepath)[0])
    directory = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    # If the context scene contains path and basename, use them
    sc = context.scene
    if sc.bf_head_directory: directory = sc.bf_head_directory
    if sc.name: basename = "{0}.fds".format(bpy.path.clean_name(sc.name))
    # Call the exporter operator
    filepath = "{0}/{1}".format(directory, basename)
    self.layout.operator(ExportFDS.bl_idname, text="Fire Dynamics Simulator Case (.fds)").filepath = filepath

class ExportFDS(bpy.types.Operator, ExportHelper):
    """Export FDS operator"""
    bl_label = "Export scene as FDS case"
    bl_idname = "export_scene.nist_fds"
    bl_description = "Export current Blender Scene as an FDS case file"
    filename_ext = ".fds"
    filter_glob = bpy.props.StringProperty(default="*.fds", options={'HIDDEN'})

    def execute(self, context):
        return io.scene_to_fds(self, context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

### Import from FDS

def import_fds_menu(self, context):
    """Import FDS menu funtion"""
    self.layout.operator(ImportFDS.bl_idname, text="Fire Dynamics Simulator Case (.fds)")

class ImportFDS(bpy.types.Operator, ImportHelper):
    """Import FDS operator"""
    bl_label = "Import FDS case"
    bl_idname = "import_scene.nist_fds"
    bl_description = "Import FDS case file into current Blender Scene"
    filename_ext = ".fds"
    filter_glob = bpy.props.StringProperty(default="*.fds", options={'HIDDEN'})

    def execute(self, context):
        return io.scene_from_fds(self, context, **self.as_keywords(ignore=("check_existing", "filter_glob")))
