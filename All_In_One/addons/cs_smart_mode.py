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
	"name": "Smart Mode Switcher",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"location": "object.smart_mode command",
	"description": "Smart switch between Object / Edit mode with change Properties",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import StringProperty #, IntProperty, BoolProperty, EnumProperty
#from bpy.types import Header, Panel


# change object mode by selection			
class SmartObjectMode(bpy.types.Operator):


	'''Smart Object Mode'''
	bl_idname = "object.smart_mode"
	bl_label = "Smart Object Mode"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):
		
		obj = context.active_object
		print("Smart Mode Type: " + obj.type)
		
		########################################
		# ARMATURE #
		########################################
		if(obj.type == "ARMATURE"):
			
			# try use my rig switcher
			try:
				if context.active_object.mode == 'OBJECT':
					bpy.ops.cenda.pose() # rig switcher
				else:
					bpy.ops.cenda.object() # rig switcher
					
			# else normal switch
			except:
				bpy.ops.object.posemode_toggle()
				
			SetPropertiesPanel( 'DATA' )
		
		########################################
		# MESH #
		########################################
		elif(obj.type == "MESH"):
			if context.active_object.mode == 'OBJECT':
				bpy.ops.object.mode_set(mode='EDIT', toggle=False)
			else:
				bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
				
		########################################
		# LATTICE & CURVE #
		########################################
		elif(obj.type == "LATTICE" or obj.type == "CURVE"):
			bpy.ops.object.editmode_toggle()
			SetPropertiesPanel( 'DATA' )
			
		########################################	
		# CAMERA & EMPTY & LAMP #
		########################################
		elif(obj.type == "CAMERA" or obj.type == "EMPTY" or obj.type == "LAMP"):
			SetPropertiesPanel( 'DATA', onlyObjectMode = True )
			
		########################################	
		# OTHERS #
		########################################
		else:
			bpy.ops.object.editmode_toggle()
			
		return {'FINISHED'}
	
	
def SetPropertiesPanel( panelName , onlyObjectMode = False ):
	

	for area in bpy.context.screen.areas: # iterate through areas in current screen
		if area.type == 'PROPERTIES':
			for space in area.spaces: # iterate through all founded panels
				if space.type == 'PROPERTIES':
					space.context = panelName

				
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()