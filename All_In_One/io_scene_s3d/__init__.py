#!/usr/bin/python3
#
# io_scene_s3d
#
# Copyright (C) 2011 Steven J Thompson
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Storm3D S3D",
    "author": "Steven J Thompson",
    "version": (0, 3),
    "blender": (2, 5, 8),
    "api": 36079,
    "location": "File > Import-Export ",
    "description": "Import and Export S3D files which are used in the Frozenbyte Storm3D engine",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import os
import pickle
from .S3DFile import S3DFile
from .B3DFile import B3DFile
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

class ImportS3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import.s3d"
    bl_label = "Import S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    getB3D = BoolProperty(name = "Import B3D (Bones)", description = "Import data from the B3D file if present", default = True)
    switchGLSL = BoolProperty(name = "Use GLSL", description = "Allow the script to switch to GLSL shading", default = True)
    removeDoubles = BoolProperty(name = "Remove doubles from mesh", description = "Removes doubles from the mesh. This causes problem UVs on s3d export.", default = True)

    def execute(self, context):
        s3d = S3DFile()
        s3d.open(self.filepath, self.switchGLSL, self.removeDoubles)
        b3d = B3DFile()
        b3d.open(self.filepath, self.getB3D)
        return {'FINISHED'}

class ExportS3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export.s3d"
    bl_label = "Export S3D"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".s3d"
    filter_glob = StringProperty(default = "*.s3d", options = {'HIDDEN'})

    #getB3D = BoolProperty(name = "Export B3D (Bones)", description = "Export data to a B3D file", default = True)

    def execute(self, context):
        s3d = S3DFile()
        s3d.write(self.filepath)
        return {'FINISHED'}

def getFileSystemSlash():
    if os.name == "posix":
        ## POSIX, use forward slash
        slash = "/"
    else:
        ## Probably Windows, use backslash
        slash = "\\"
    return slash

def getSettingsFilePath():
    addonDir = os.path.abspath(__file__)
    slash = getFileSystemSlash()
    addonPath = slash.join(addonDir.split(slash)[0:-1])
    addonPath = addonPath + slash + 'settings.pkl'
    return addonPath

class UserPref(bpy.types.Panel):
    bl_idname = "OBJECT_PT_storm_3d"
    bl_label = "Storm3D Settings"
    bl_space_type = 'USER_PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    bpy.types.WindowManager.jcdata = StringProperty(name = 'Jack Claw Data Directory', subtype = 'DIR_PATH')

    settingsPath = getSettingsFilePath()
    if os.path.exists(settingsPath):
        settingsFile = open(settingsPath, 'rb')
        settings = pickle.load(settingsFile)
        bpy.context.window_manager.jcdata = settings['jcdata']
        settingsFile.close()

    @classmethod
    def poll(cls, context):
        atFilesSection = context.user_preferences.active_section == 'FILES'
        return atFilesSection

    def draw(self, context):
        layout = self.layout
        layout.prop(context.window_manager, 'jcdata')
        row = layout.row()
        row.operator('jcdata.save', text = 'Save Settings')

class UserPrefSaveButton(bpy.types.Operator):
    bl_idname = 'jcdata.save'
    bl_label = 'Button'

    def execute(self, context):
        settingsFile = open(getSettingsFilePath(), 'wb')
        settings = {'jcdata': bpy.context.window_manager.jcdata}
        pickle.dump(settings, settingsFile)
        settingsFile.close()

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportS3D.bl_idname, text="Storm3D S3D (.s3d)")

def menu_func_export(self, context):
    self.layout.operator(ExportS3D.bl_idname, text="Storm3D S3D (.s3d)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
