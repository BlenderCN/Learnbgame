#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bl_ui import space_info
from bpy.props import *
import exporter
import importer

def menu_func_export(self, context):
    self.layout.operator(exporter.PlasmaExportAge.bl_idname, text="Plasma Age (.age)")
    self.layout.operator(exporter.PlasmaExportResourcePage.bl_idname, text="Plasma Page (.prp)")


def menu_func_import(self, context):
    self.layout.operator(importer.PlasmaImport.bl_idname, text="Plasma (.age)")

def register():
    exporter.register()
    importer.register()
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    exporter.unregister()
    importer.unregister()

