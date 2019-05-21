#	
#	Copyright (C) 2018 Team Motorway
#	
#	This file is part of Project Motorway source code.
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#	
# <pep8-80 compliant>

version = ( 3, 0, 0, 0 )

bl_info = {
	"name": "Project Motorway Mesh",
	"author": "Team Motorway",
	"version": ( 2, 0, 0 ),
	"blender": ( 2, 77, 0 ),
	"location": "File > Import-Export",
	"description": "Export .mesh (Project Motorway Mesh)",
	"warning": "",
	"wiki_url": ""
				"",
	"support": 'OFFICIAL',
	"category": "Learnbgame"
}

if "bpy" in locals():
	import imp
	if "export" in locals():
		imp.reload(export)

import bpy
from bpy.props import (EnumProperty,StringProperty,BoolProperty)
from bpy_extras.io_utils import (ImportHelper,
							 ExportHelper,
							 path_reference_mode,
							 axis_conversion,
							 )

class ExportMesh(bpy.types.Operator, ExportHelper):
	bl_idname = "export.mesh"
	bl_label = 'Export Project Motorway Mesh'
	bl_options = {'PRESET'}

	filename_ext = ".mesh"
	filter_glob = StringProperty(
			default="*.mesh;",
			options={'HIDDEN'},
			)
	create_convex_collider = BoolProperty(
		name="Export Convex Collision Shape",
		description="Include geometry optimized for collision detection within the file.",
		default=False,
	)
 
	path_mode = path_reference_mode
	check_extension = True

	def execute(self, context):
		from . import export
		from mathutils import Matrix
		keywords = self.as_keywords(ignore=("filter_glob","path_mode","filepath","check_existing",))
		global_matrix = ( Matrix.Identity( 4 ) * axis_conversion( to_forward='Z',to_up='Y' ).to_4x4())

		keywords["global_matrix"] = global_matrix
		keywords["create_convex_collider"] = False
		keywords["version"] = version
		return export.save(self.filepath, **keywords)
		
	def draw(self, context):
		layout = self.layout
		row = layout.row(align=True)

		
def menu_func_export(self, context):
	self.layout.operator(ExportMesh.bl_idname, text="Project Motorway Mesh (.mesh)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()