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
# from bpy_extras.io_utils import ImportHelper

from .geom_import import ImportGeom


bl_info = {
    "name": "Sims 3 GEOM Tools",
    "category": "Import-Export",
	"version": (0, 0, 0),
	"blender": (2, 79, 0),
	"location": "File > Import/Export",
	"description": "Importer and exporter for Sims 3 GEOM(.simgeom) files"
}


def menu_func_import(self, context):
    self.layout.operator(ImportGeom.bl_idname)


def menu_func_export(self, context):
    pass


def register():
    bpy.utils.register_class(ImportGeom)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportGeom)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
