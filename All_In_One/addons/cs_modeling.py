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
	"name": "Modeling Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 3),
	"blender": (2, 79, 0),
	"location": "Hotkeys",
	"description": "Combined modeling tools",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
#import bgl
#import blf
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import Header, Panel


#####
# Q #
#####	
class Tool_1(bpy.types.Operator):
	
	bl_idname = "mesh.tool_1"
	bl_label = "Dissolve, Merge & Fill"

	def execute(self, context):

		if( ActiveComponent() == 'VERTEX' ):	

			numberOfVertices = NumberOfVertices()
			
			# DISSOLVE ONE VERTEX #
			if(numberOfVertices == 1):
				bpy.context.window_manager.popup_menu(DissolveConfirm, title="Confirm", icon='INFO')
				
			# MERGE CENTER #	
			if(numberOfVertices >= 2):
				bpy.ops.mesh.merge(True, type='CENTER')
				
				
		elif( ActiveComponent() == 'EDGE' ):
			
			# FILL GRID #
			try:
				bpy.ops.mesh.fill_grid(True)
				
			# FILL TRIANGLE #
			except:
				bpy.ops.mesh.fill(True, use_beauty=True)
			
		return {'FINISHED'}


#####
# A #
#####
class Tool_2(bpy.types.Operator):
	
	bl_idname = "mesh.tool_2"
	bl_label = "Path Connect & Dissolve Edge & UV Map"

	def execute(self, context):
		
		'''
		x = 60
		y = 100
		RED = (1, 0, 0, 1)
		GREEN = (0, 1, 0, 1)
		BLUE = (0, 0, 1, 1)
		ps = [("Blue ", RED),("Yellow ", BLUE),("White ", GREEN)]
		draw_string(x, y, ps)
		'''
	
		if( ActiveComponent() == 'VERTEX' ):	
			
			numberOfVertices = NumberOfVertices()
			
			# DISSOLVE ONE VERTEX #
		#	if(numberOfVertices == 1):
		#		bpy.context.window_manager.popup_menu(DissolveConfirm, title="Confirm", icon='INFO')
				
			# CONNECT VERTICES #	
			if(numberOfVertices >= 2):	
				bpy.ops.mesh.vert_connect_path(True)
				
				
		elif( ActiveComponent() == 'EDGE' ):
			
			# DISSOLVE EDGE #
			bpy.ops.mesh.dissolve_mode(True, use_verts=True)


		elif( ActiveComponent() == 'FACE' ):
			bpy.ops.wm.call_menu( 'INVOKE_DEFAULT', name = "VIEW3D_MT_uv_map" )
			
		return {'FINISHED'}
	
	
	
def DissolveConfirm(self, context):
	self.layout.operator("mesh.dissolve_verts" ).use_face_split=True


	
'''	
def draw_string(x, y, packed_strings):

	font_id = 0
	blf.size(font_id, 18, 72) 
	x_offset = 0
	
	
	for pstr, pcol in packed_strings:
		bgl.glColor4f(*pcol)
		text_width, text_height = blf.dimensions(font_id, pstr)
		blf.position(font_id, (x + x_offset), y, 0)
		blf.draw(font_id, pstr)
		x_offset += text_width
'''
	
	
def ActiveComponent():
	
	if( bpy.context.tool_settings.mesh_select_mode[0] ):
		return 'VERTEX'
	
	elif( bpy.context.tool_settings.mesh_select_mode[1] ):
		return 'EDGE'
	
	elif( bpy.context.tool_settings.mesh_select_mode[2] ):
		return 'FACE'


def NumberOfVertices():
	
	obj = bpy.context.active_object
	obj.update_from_editmode()
	
	return ( len([v for v in obj.data.vertices if v.select]) )
		
					
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()