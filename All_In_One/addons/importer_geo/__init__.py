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

# <pep8-80 compliant>

bl_info = {
    "name": "Houdini GEO Importer",
    "author": "Francis Pimenta",
    "version": (0, 0, 1),
    "blender": (2, 74, 0),
    "location": "File > Import",
    "description": "Import GEO files",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/GEO",
    "support": 'TESTING',
    "category": "Import-Export",
}


# @todo write wiki page and some other stuff

"""
Import-Export GEO files (Houdini Export: .json, .geo)

- Import basic import of mesh
- Export no export support

Issues: missing a lot off attribute import options
"""
import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

if "bpy" in locals():
    import importlib
    if "h2c" in locals():
        importlib.reload(h2c)
    if "h2bimporter" in locals():
        importlib.reload(h2bimporter)

class GEO_Importer(bpy.types.Operator, ImportHelper):
	bl_idname= "import_mesh.json"
	bl_description = 'Imports Houdini geo Files'
	bl_label = "Houdini GEO Importer"
	filename_ext = ".json"
	filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
	
	filepath= StringProperty(name="File Path", description="Filepath used for importing the GEO file", maxlen=1024, default="")
	
	def execute(self, context): 
		"""Execute the Importer Function"""
		from . import h2c
		from . import h2bimporter
				
		h2c.load(self.filepath)
		h2bimporter.load(h2c.hdata)
		return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(GEO_Importer.bl_idname, text="Houdini GEO Importer")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
