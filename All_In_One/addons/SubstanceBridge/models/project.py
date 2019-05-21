import bpy

from bpy.props import *


# ----------------------------------------------------------------------------
# Variable to all project
# ----------------------------------------------------------------------------
class SbsProjectItems(bpy.types.PropertyGroup):
    # Name of Substance Project
    prj_name = bpy.props.StringProperty(
        name="Project Name",
        default="Sbs Project",
        )
    # Path File to edit this project
    path_spp = StringProperty(
        name="Project Path",
        default="C:/",
        description="Field project path",
        subtype='FILE_PATH'
    )
    # List of mesh
    meshs_name = []

    # List of Texture Set
    tx_set_index = StringProperty(
        name="Name Set",
        default="Default",
        )


def register():
    bpy.utils.register_class(SbsProjectItems)
    bpy.types.Scene.sbs_project_settings = \
        bpy.props.PointerProperty(type=SbsProjectItems)


def unregister():
    bpy.utils.unregister_class(SbsProjectItems)
    del bpy.types.Scene.sbs_project_settings
