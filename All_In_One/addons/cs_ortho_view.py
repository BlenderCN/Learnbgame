# ***** BEGIN GPL LICENSE BLOCK *****
#
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
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Ortho View",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "N-Panel",
	"description": "Panel for set ortho view",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.types import  Panel


class VIEW3D_PT_view3d_display_view_side(Panel):
	
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Ortho View"
	
	def draw(self, context):
		
		layout = self.layout
		
		row = layout.row(align = True)
		row.operator("view3d.viewnumpad", text="Top").type='TOP'
		
		box = layout.box()
		row = box.row(align = True)
		row.operator("view3d.viewnumpad", text="Front" ).type='FRONT'
		
		row = box.row(align = True)
		row.operator("view3d.viewnumpad", text="Left" ).type='LEFT'
		row.operator("view3d.viewnumpad", text="Right" ).type='RIGHT'
		
		row = box.row(align = True)
		row.operator("view3d.viewnumpad", text="Back" ).type='BACK'



################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()