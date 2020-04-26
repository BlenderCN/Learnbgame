import bpy
import ATOM_Types
import ctypes

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       CollectionProperty)
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       Property,
                       AddonPreferences)

def draw(self, context):
    layout = self.layout
    row = layout.row()

    row.prop(context.window_manager.ATOM_io_Proprties, "project_folder")

class FileManager(ATOM_Types.Module):

    def __init__(self):

        bpy.types.OpenProjectSettingDialog.addElement(draw)