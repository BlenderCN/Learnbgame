'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy.props import PointerProperty

from .blender_import import ImportGMDC
from .blender_export import ExportGMDC
from .ui_panel       import(PROP_GmdcSettings,
                            OP_AddMorph,
                            OP_UpdateNeckFix,
                            OP_UpdateMorphNames,
                            OP_HideShadows,
                            OP_UnhideShadows,
                            OP_HideArmature,
                            OP_UnHideArmature,
                            OP_SyncMorphs,
                            GmdcPanel)


bl_info = {
    "name": "Sims 2 GMDC Tools",
    "category": "Import-Export",
	"version": (0, 2, '1B'),
	"blender": (2, 79, 0),
	"location": "File > Import/Export",
	"description": "Importer and exporter for Sims 2 GMDC(.5gd) files"
}


def menu_func_im(self, context):
    self.layout.operator(ImportGMDC.bl_idname)

def menu_func_ex(self, context):
    self.layout.operator(ExportGMDC.bl_idname)

def register():
    # IO
    bpy.utils.register_class(ImportGMDC)
    bpy.utils.register_class(ExportGMDC)
    bpy.types.INFO_MT_file_import.append(menu_func_im)
    bpy.types.INFO_MT_file_export.append(menu_func_ex)

    # Tool Panel
    bpy.utils.register_class(GmdcPanel)
    bpy.utils.register_class(OP_AddMorph)
    bpy.utils.register_class(OP_UpdateMorphNames)
    bpy.utils.register_class(OP_UpdateNeckFix)
    bpy.utils.register_class(OP_HideShadows)
    bpy.utils.register_class(OP_UnhideShadows)
    bpy.utils.register_class(OP_HideArmature)
    bpy.utils.register_class(OP_UnHideArmature)
    bpy.utils.register_class(OP_SyncMorphs)
    bpy.utils.register_class(PROP_GmdcSettings)
    bpy.types.Scene.gmdc_props = PointerProperty(type=PROP_GmdcSettings)


def unregister():
    # IO
    bpy.utils.unregister_class(ImportGMDC)
    bpy.utils.unregister_class(ExportGMDC)
    bpy.types.INFO_MT_file_import.remove(menu_func_im)
    bpy.types.INFO_MT_file_export.remove(menu_func_ex)

    # Tool Panel
    bpy.utils.unregister_class(GmdcPanel)
    bpy.utils.unregister_class(OP_AddMorph)
    bpy.utils.unregister_class(OP_UpdateMorphNames)
    bpy.utils.unregister_class(OP_UpdateNeckFix)
    bpy.utils.unregister_class(OP_HideShadows)
    bpy.utils.unregister_class(OP_UnhideShadows)
    bpy.utils.unregister_class(OP_HideArmature)
    bpy.utils.unregister_class(OP_UnHideArmature)
    bpy.utils.unregister_class(OP_SyncMorphs)
    bpy.utils.unregister_class(PROP_GmdcSettings)
    del bpy.types.Scene.gmdc_props


if __name__ == "__main__":
    register()
