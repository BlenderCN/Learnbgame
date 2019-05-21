bl_info = {
    "name": "Kabanero Map Format",
    "author": "Toni Pesola",
    "version": (0, 1, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import importlib
    if "export_kabanero" in locals():
        importlib.reload(export_kabanero)

import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )

# Property definitions

bpy.types.Scene.kb_bgcolor = bpy.props.FloatVectorProperty(
    name="Background Color",
    description="Color value",
    default = (0.0, 0.0, 0.0),
    min = 0.0,
    max = 1.0,
    precision = 2,
    subtype='COLOR'
)

bpy.types.Object.kb_actor = bpy.props.StringProperty(
    name="Actor",
    description="Actor file",
    default="",
    subtype='FILE_PATH'
)

bpy.types.Object.kb_collide = bpy.props.BoolProperty(
    name="Collide",
    description="Is collider active",
    default=True,
)

bpy.types.Object.kb_active = bpy.props.BoolProperty(
    name="Active",
    description="Is active",
    default=True,
)

def _get_visible(self):
    if "kb_visible" in self:
        return self["kb_visible"]
    else:
        return True

def _set_visible(self, value):
    self["kb_visible"] = value
    self.draw_type = "TEXTURED" if value else "WIRE"
    return None

bpy.types.Object.kb_visible_prop = bpy.props.BoolProperty(
    name="Visible",
    description="Is visible",
    set=_set_visible,
    get=_get_visible
)

IOKBOrientationHelper = orientation_helper_factory("IOKBOrientationHelper", axis_forward='-Z', axis_up='Y')

class ExportKabanero(bpy.types.Operator, ExportHelper, IOKBOrientationHelper):
    """Save a Kabanero map file"""

    bl_idname = "export_scene.kbmap"
    bl_label = 'Export Kabanero Map'
    bl_options = {'PRESET'}

    filename_ext = ".kbmap"
    filter_glob = StringProperty(
            default="*.kbmap",
            options={'HIDDEN'},
            )

    # context group
    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )

    # path_mode = path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_kabanero

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["script_version"] = bl_info["version"]

        keywords["global_matrix"] = global_matrix
        return export_kabanero.save(context, **keywords)

class KabaneroObjectPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Kabanero Object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.prop(obj, "name")
        row = layout.row()
        row.prop(obj, "kb_actor")
        row = layout.row()
        row.prop(obj, "kb_collide")
        row.prop(obj, "kb_active")
        row.prop(obj, "kb_visible_prop")

class KabaneroWorldPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Kabanero Map"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "name")
        row = layout.row()
        row.prop(scene, "kb_bgcolor")


def menu_func_export(self, context):
    self.layout.operator(ExportKabanero.bl_idname, text="Kabanero Map (.kbmap)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    # bpy.utils.register_class(KabaneroObjectPanel)
    # bpy.utils.register_class(KabaneroWorldPanel)



def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    # bpy.utils.unregister_class(KabaneroObjectPanel)
    # bpy.utils.unregister_class(KabaneroWorldPanel)


if __name__ == "__main__":
    register()
