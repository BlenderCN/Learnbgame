############################################################################
#     Copyright (C) 2014 by Ralf Kaestner                                   #
#     ralf.kaestner@gmail.com                                               #
#                                                                           #
#                                                                           #  
#     URDF ADDON INSTALLATION FILE FOR  BLENDER                             #
#     Usage:                                                                #
#       - Create symbolic link in blender addon folder                      #
#         ln -s PROJECT_DIR/blender-urdf/src/io_scene_urdf                  #
#               ~/.config/blender/VERSION/scripts/addons                    #
#       - Activate the addon in blender                                     #
#         File > User Preferences > Addons                                  #
#       - To import/export URDF                                             #
#         File > Import/Export > Unified Robot Description Format ...       #
#                                                                           #  
#                                                                           #
#     This program is free software; you can redistribute it and#or modify  #
#     it under the terms of the GNU General Public License as published by  #
#     the Free Software Foundation; either version 2 of the License, or     #
#     (at your option) any later version.                                   #
#                                                                           #
#     This program is distributed in the hope that it will be useful,       #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#     GNU General Public License for more details.                          #
#                                                                           #
#     You should have received a copy of the GNU General Public License     #
#     along with this program; if not, write to the                         #
#     Free Software Foundation, Inc.,                                       #
#     59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
#                                                                           #
#############################################################################

import sys
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/home/nngoc/miror_workspace/morse_install/lib/python3/dist-packages')



bl_info = {
  "name": "Unified Robot Description Format (URDF)",
  "author": "Ralf Kaestner",
  "blender": (2, 6, 3),
  "description": "Import-Export Unified Robot Description Format (URDF)",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "http://github.com/kralf/blender-urdf",
  "support": "COMMUNITY",
  "category": "Import-Export"
}


if "bpy" in locals():
  import imp
  if "import_urdf" in locals():
    imp.reload(import_urdf)
  if "import_urdf_xacro" in locals():
    imp.reload(import_urdf_xacro)
  if "export_urdf" in locals():
    imp.reload(export_urdf)
  if "export_urdf_xacro" in locals():
    imp.reload(export_urdf_xacro)


import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportURDF(bpy.types.Operator, ImportHelper):
  bl_idname = "import_scene.urdf"
  bl_label = "Import URDF"
  bl_options = {"PRESET", "UNDO"}

  filename_ext = ".urdf"
  filter_glob = StringProperty(default="*.urdf", options = {"HIDDEN"})

  def execute(self, context):
    keywords = self.as_keywords()
       
    from . import import_urdf
    return import_urdf.load(self, context, keywords['filepath'])
  

class ImportURDFXacro(bpy.types.Operator, ImportHelper):
  bl_idname = "import_scene_urdf.xacro"
  bl_label = "Import URDF/Xacro"
  bl_options = {"PRESET", "UNDO"}

  filename_ext = ".urdf.xacro"
  filter_glob = StringProperty(default="*.urdf.xacro", options = {"HIDDEN"})

  def execute(self, context):
    keywords = self.as_keywords()
    
    from . import import_urdf_xacro
    return import_urdf_xacro.load(self, context, **keywords)
  
  
class ExportURDF(bpy.types.Operator, ExportHelper):
  bl_idname = "export_scene.urdf"
  bl_label = "Export URDF"
  bl_options = {"PRESET", "UNDO"}

  filename_ext = ".urdf"
  filter_glob = StringProperty(default = "*.urdf",
    options = {"HIDDEN"})

  def execute(self, context):
    keywords = self.as_keywords()
    
    from . import import_urdf
    return export_urdf.save(self, context, **keywords)
  

class ExportURDFXacro(bpy.types.Operator, ExportHelper):
  bl_idname = "export_scene_urdf.xacro"
  bl_label = "Export URDF/Xacro"
  bl_options = {"PRESET", "UNDO"}

  filename_ext = ".urdf"
  filter_glob = StringProperty(default = "*.urdf.xacro",
    options = {"HIDDEN"})

  def execute(self, context):
    keywords = self.as_keywords()
    
    from . import import_urdf_xacro
    return export_urdf_xacro.save(self, context, **keywords)
  
  
def menu_func_import(self, context):
  self.layout.operator(ImportURDF.bl_idname,
    text="Unified Robot Description Format (.urdf)")
  self.layout.operator(ImportURDFXacro.bl_idname,
    text="Unified Robot Description Format/Xacro (.urdf.xacro)")


def menu_func_export(self, context):
  self.layout.operator(ExportURDF.bl_idname,
    text="Unified Robot Description Format (.urdf)")
  self.layout.operator(ExportURDFXacro.bl_idname,
    text="Unified Robot Description Format/Xacro (.urdf.xacro)")


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
