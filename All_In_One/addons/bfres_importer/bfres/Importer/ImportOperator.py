import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import os
import os.path
from .Importer import Importer


class ImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a BFRES model file"""

    bl_idname    = "import_scene.nxbfres"
    bl_label     = "Import NX BFRES"
    bl_options   = {'UNDO'}
    filename_ext = ".bfres"

    filter_glob  = bpy.props.StringProperty(
        default="*.sbfres;*.bfres;*.fres;*.szs",
        options={'HIDDEN'},
    )
    filepath = bpy.props.StringProperty(
        name="File Path",
        #maxlen=1024,
        description="Filepath used for importing the BFRES or compressed SZS file")

    import_tex_file = bpy.props.BoolProperty(name="Import .Tex File",
        description="Import textures from .Tex file with same name.",
        default=True)

    dump_textures = bpy.props.BoolProperty(name="Dump Textures",
        description="Export textures to PNG.",
        default=False)

    dump_debug = bpy.props.BoolProperty(name="Dump Debug Info",
        description="Create `fres-SomeFile-dump.txt` files for debugging.",
        default=False)

    smooth_faces = bpy.props.BoolProperty(name="Smooth Faces",
        description="Set smooth=True on generated faces.",
        default=False)

    save_decompressed = bpy.props.BoolProperty(name="Save Decompressed Files",
        description="Keep decompressed FRES files.",
        default=False)

    parent_ob_name = bpy.props.StringProperty(name="Name of a parent object to which FSHP mesh objects will be added.")

    mat_name_prefix = bpy.props.StringProperty(name="Text prepended to material names to keep them unique.")


    def draw(self, context):
        box = self.layout.box()
        box.label("Texture Options:", icon='TEXTURE')
        box.prop(self, "import_tex_file")
        box.prop(self, "dump_textures")

        box = self.layout.box()
        box.label("Mesh Options:", icon='OUTLINER_OB_MESH')
        box.prop(self, "smooth_faces")

        box = self.layout.box()
        box.label("Misc Options:", icon='PREFERENCES')
        box.prop(self, "save_decompressed")
        box.prop(self, "dump_debug")


    def execute(self, context):
        #user_preferences = context.user_preferences
        #addon_prefs = user_preferences.addons[self.bl_idname].preferences
        #print("PREFS:", user_preferences, addon_prefs)

        # enter Object mode if not already
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError: pass

        if self.import_tex_file:
            path, ext = os.path.splitext(self.properties.filepath)
            path = path + '.Tex' + ext
            if os.path.exists(path):
                log.info("Importing linked file: %s", path)
                importer = Importer(self, context)
                importer.run(path)
        log.info("importing: %s", self.properties.filepath)
        importer = Importer(self, context)
        return importer.run(self.properties.filepath)


    @staticmethod
    def menu_func_import(self, context):
        """Handle the Import menu item."""
        self.layout.operator(
            ImportOperator.bl_idname,
            text="Nintendo Switch BFRES (.bfres/.szs)")
