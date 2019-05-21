# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Thanks to Simon Kirkby and David Anderson for their previous
# versions of this script!

bl_info = {
  'name': 'Import RepRap G-code for FFF',
  'author': 'Ted Milker',
  'version': (0,0,4),
  'blender': (2, 6, 5),
  'location': 'File > Import',
  'description': 'Import gcode files for reprap FFF printers .gcode',
  'warning': 'may not work',
  "wiki_url": "",
  "tracker_url": "",
  'category': 'Import-Export'
}

if "bpy" in locals():
  import imp

  if "import_gcode" in locals():
    imp.reload(import_gcode)

import bpy
from bpy.props import StringProperty

from bpy_extras.io_utils import(ImportHelper)

class ImportGcode(bpy.types.Operator, ImportHelper):
  bl_idname = "import_scene.reprap_gcode"
  bl_label = "Import RepRap G-code"
  bl_options = {'UNDO'}

  filename_ext = ".gcode"
  filter_glob = StringProperty(default="*.gcode", options={'HIDDEN'})

  def execute(self, context):
    from . import import_gcode

    keywords = self.as_keywords()

    return import_gcode.load(self, context, **keywords)

def menu_func_import(self, context):
  self.layout.operator(ImportGcode.bl_idname, text="RepRap G-code (.gcode)")

def register():
  bpy.utils.register_module(__name__)

  bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
  bpy.utils.unregister_module(__name__)

  bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
  register();
