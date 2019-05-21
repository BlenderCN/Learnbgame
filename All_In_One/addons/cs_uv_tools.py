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
	"name": "UV Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Many commands",
	"description": "Smart switch mode and components for UV Editor",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import StringProperty, EnumProperty #, IntProperty, BoolProperty, EnumProperty
#from bpy.types import Header, Panel


# Only switch between modes (UV and Vertex) with remain settings component	
class SmartSwitchUVMode(bpy.types.Operator):

	'''Smart UV Mode'''
	bl_idname = "uv.smart_switch_mode"
	bl_label = "Smart Switch UV Mode"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):

		# go to EDIT mode first
		if(bpy.context.active_object.mode == 'OBJECT'):
			bpy.ops.object.mode_set(mode = 'EDIT')
		
		# switch between sync mode	
		else:
			
			# UV MODE #
			if(not bpy.context.tool_settings.use_uv_select_sync):
				
				# synchronize same component
				if(bpy.context.scene.tool_settings.uv_select_mode == 'VERTEX'):
					bpy.context.tool_settings.mesh_select_mode = (True, False, False)
				
				elif(bpy.context.scene.tool_settings.uv_select_mode == 'EDGE'):
					bpy.context.tool_settings.mesh_select_mode = (False, True, False)
					
				elif(bpy.context.scene.tool_settings.uv_select_mode == 'FACE'):
					bpy.context.tool_settings.mesh_select_mode = (False, False, True)
					
				elif(bpy.context.scene.tool_settings.uv_select_mode == 'ISLAND'):
					bpy.context.tool_settings.mesh_select_mode = (False, False, True)
							
				bpy.context.tool_settings.use_uv_select_sync = True
				
				bpy.ops.mesh.select_all(action='DESELECT') # deselect all because it is not needed
				
			#  VERTEX VIEW 3D SYNC #	
			else:
				
				# synchronize same component
				if(bpy.context.tool_settings.mesh_select_mode[0] ):
					bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
					
				elif(bpy.context.tool_settings.mesh_select_mode[1] ):
					bpy.context.scene.tool_settings.uv_select_mode = 'EDGE'
					
				elif(bpy.context.tool_settings.mesh_select_mode[2] ):
					bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

				bpy.context.tool_settings.use_uv_select_sync = False
				bpy.ops.mesh.select_all(action='SELECT') # select all for show all UV
	
		return {'FINISHED'}
	
	
class SmartUVComponentMode(bpy.types.Operator):

	'''Smart UV Component Mode'''
	bl_idname = "uv.smart_component_mode"
	bl_label = "Smart UV Component Mode"
#	bl_options = {'REGISTER', 'UNDO'}


	ComponentTypeEnum = [
		("VERTEX", "Vertex", "", "", 0),
	    ("EDGE", "Edge", "", "", 100),
		("FACE", "Face", "", "", 200),
		("ISLAND", "Island", "", "", 300)
	    ]
	
	component = EnumProperty( name = "Component", description = "", items=ComponentTypeEnum )
	
	
	def execute(self, context):

		# Component sync #
		if( bpy.context.tool_settings.use_uv_select_sync ):
			
			if(self.component == 'VERTEX'):
				bpy.context.tool_settings.mesh_select_mode = (True, False, False)
				
			elif(self.component == 'EDGE'):
				bpy.context.tool_settings.mesh_select_mode = (False, True, False)
				
			elif(self.component == 'FACE'):
				bpy.context.tool_settings.mesh_select_mode = (False, False, True)	
		
		# Classic UV mode #
		else:

			# vertex mode is also switcher
			if( (context.scene.tool_settings.uv_select_mode == 'VERTEX') and (self.component == 'VERTEX') and (context.space_data.uv_editor.sticky_select_mode != 'DISABLED') ):
				bpy.ops.uv.sticky_switch(stickyMode = 'DISABLED')
			
			elif( (context.scene.tool_settings.uv_select_mode == 'EDGE') and (self.component == 'EDGE') and (context.space_data.uv_editor.sticky_select_mode != 'SHARED_LOCATION') ):
				bpy.ops.uv.sticky_switch(stickyMode = 'SHARED_LOCATION')
			
			# Face / Island switch
			elif( (context.scene.tool_settings.uv_select_mode == 'FACE') and (self.component == 'FACE') ):
				bpy.ops.uv.sticky_switch(stickyMode = 'SHARED_LOCATION')
				bpy.context.scene.tool_settings.uv_select_mode = 'ISLAND'
				
			else:
				
				# setting for all
				bpy.context.scene.tool_settings.uv_select_mode = self.component
	
				if(self.component == 'VERTEX'):
					bpy.ops.uv.sticky_switch(stickyMode = 'SHARED_LOCATION')
					
				elif(self.component == 'EDGE'):
					bpy.ops.uv.sticky_switch(stickyMode = 'SHARED_VERTEX')
					
				elif(self.component == 'FACE'):
					bpy.ops.uv.sticky_switch(stickyMode = 'DISABLED')
				
				elif(self.component == 'ISLAND'):
					bpy.ops.uv.sticky_switch(stickyMode = 'SHARED_LOCATION')
				
		return {'FINISHED'}


# change object mode by selection			
class StickyModeSwitch(bpy.types.Operator):

	'''Switch Sticky Mode'''
	bl_idname = "uv.sticky_switch"
	bl_label = "Switch Sticky Mode"
#	bl_options = {'REGISTER', 'UNDO'}


	StickyModeEnum = [
		("DISABLED", "Disabled", "", "", 0),
	    ("SHARED_LOCATION", "Shared Location", "", "", 100),
		("SHARED_VERTEX", "Shared Vertex", "", "", 200)
	    ]
	
	stickyMode = EnumProperty( name = "Sticky Mode", description = "", items=StickyModeEnum )
	
	
	def execute(self, context):

		space = bpy.context.space_data
		space.uv_editor.sticky_select_mode = self.stickyMode
		
		return {'FINISHED'}
	

				
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()