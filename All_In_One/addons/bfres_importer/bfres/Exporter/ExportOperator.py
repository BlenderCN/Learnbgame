import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import os
import os.path
from .Exporter import Exporter


class ExportOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export a BFRES model file"""

    bl_idname    = "export_scene.nxbfres"
    bl_label     = "Export NX BFRES"
    bl_options   = {'UNDO'}
    #filename_ext = ".bfres"
    filename_ext = ".dat"

    filter_glob  = bpy.props.StringProperty(
        default="*.sbfres;*.bfres",
        options={'HIDDEN'},
    )
    filepath = bpy.props.StringProperty(
        name="File Path",
        #maxlen=1024,
        description="Filepath used for exporting the BFRES file")

    export_tex_file = bpy.props.BoolProperty(name="Write .Tex File",
        description="Write textures to .Tex file with same name.",
        default=True)


    def draw(self, context):
        box = self.layout.box()
        box.label("Texture Options:", icon='TEXTURE')
        box.prop(self, "export_tex_file")


    def execute(self, context):
        # enter Object mode if not already
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError: pass

        if self.export_tex_file:
            path, ext = os.path.splitext(self.properties.filepath)
            path = path + '.Tex' + ext
            if os.path.exists(path):
                log.info("Exporting linked file: %s", path)
                exporter = Exporter(self, context)
                exporter.exportTextures(path)
        log.info("exporting: %s", self.properties.filepath)
        exporter = Exporter(self, context)
        return exporter.run(self.properties.filepath)


    @staticmethod
    def menu_func_export(self, context):
        """Handle the Export menu item."""
        self.layout.operator(
            ExportOperator.bl_idname,
            text="Nintendo Switch BFRES (.bfres)")
