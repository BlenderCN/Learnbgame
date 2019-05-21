bl_info = {
    "name": "Wiresterizer format",
    "author": "Ohmnivore",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "Export to wiresterizer format",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    if "export_wire" in locals():
        importlib.reload(export_wire)
    if "lib_wire" in locals():
        importlib.reload(lib_wire)


from . import lib_wire

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty
    )
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper_factory,
    path_reference_mode,
    axis_conversion,
    )


WIRESTERIZER_FORMAT_VERSION = 0


IOOBJOrientationHelper = orientation_helper_factory(
    "IOOBJOrientationHelper",
    axis_forward='-Z',
    axis_up='Y'
    )


class ExportWire(bpy.types.Operator, ExportHelper, IOOBJOrientationHelper):
    """Save a Wiresterizer File"""

    bl_idname = "export_mesh.wire"
    bl_label = 'Export Wiresterizer mesh'
    bl_options = {'PRESET'}

    filename_ext = ".wire"
    filter_glob = StringProperty(
        default="*.wire",
        options={'HIDDEN'},
        )

    # context group
    use_selection = BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    # object group
    use_mesh_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers",
        default=True,
        )
    use_mesh_modifiers_render = BoolProperty(
        name="Use Modifiers Render Settings",
        description="Use render settings when applying modifiers to mesh objects",
        default=False,
        )

    # extra data group
    use_header = BoolProperty(
        name="Include Header",
        description="Write the format header",
        default=True,
        )
    use_text_mode = BoolProperty(
        name="Use Text Mode",
        description="Use the Wiresterizer text format (useful for debugging)",
        default=True,
        )
    use_triangles = BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=False,
        )
    use_n_gons = BoolProperty(
        name="Use N-Gons",
        description="Faces in source meshes have an arbitrary amounts of edges",
        default=False,
        )
    use_indexing = BoolProperty(
        name="Use Indexing",
        description="Faces will contain indexes to vertex data",
        default=True,
        )
    use_vertex_normals = BoolProperty(
        name="Write Vertex Normals",
        description="Include a normal per vertex",
        default=False,
        )
    use_face_normals = BoolProperty(
        name="Write Face Normals",
        description="Include a normal per face",
        default=False,
        )

    global_scale = FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
        )

    path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_wire

        from mathutils import Matrix
        keywords = {}
        keywords["use_mesh_modifiers"] = self.use_mesh_modifiers
        keywords["use_mesh_modifiers_render"] = self.use_mesh_modifiers_render
        keywords["use_selection"] = self.use_selection
        keywords["path_mode"] = self.path_mode

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                        ).to_4x4())
        keywords["global_matrix"] = global_matrix

        # Wiresterizer options
        wire_opts = lib_wire.WireOptions()
        wire_opts.version = WIRESTERIZER_FORMAT_VERSION
        wire_opts.header = self.use_header
        wire_opts.text_mode = self.use_text_mode
        wire_opts.triangles = self.use_triangles
        wire_opts.indexing = self.use_indexing
        wire_opts.vertex_normals = self.use_vertex_normals
        wire_opts.face_normals = self.use_face_normals
        wire_opts.n_gons = self.use_n_gons

        return export_wire.save(context, self.filepath, wire_opts, **keywords)


def menu_func_export(self, _context):
    self.layout.operator(ExportWire.bl_idname, text="Wiresterizer (.wire)")


classes = (
    ExportWire,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
