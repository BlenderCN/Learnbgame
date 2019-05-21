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
	"name": "Rename Bones",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Tools > Bones Renamer (Armature Edit Mode)",
	"description": "Rename duplicated bones",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	

import bpy


class StringsGroup(bpy.types.PropertyGroup):
	
	bpy.types.Scene.OldName = bpy.props.StringProperty(name = "Find", default = "Back" )
	bpy.types.Scene.NewName = bpy.props.StringProperty(name = "Replace", default = "Middle" )
	bpy.types.Scene.DelName = bpy.props.StringProperty(name = "Postfix", default = ".001", description = "Postfix for delete" )


class RenamePanel(bpy.types.Panel):
	
	bl_label = "Bones Renamer"
	bl_idname = "BONE_RENAME_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Tools"
	bl_context = "armature_edit"


	def draw(self, context):

		layout = self.layout
		scn = context.scene
		
		layout.row().prop( scn, "OldName")
		layout.row().prop( scn, "NewName")
		layout.row().prop( scn, "DelName")
		
		# button
		layout.operator("view3d.bone_rename")
		

# rename button	
class Rename(bpy.types.Operator):
	
	"""Rename selected bones"""
	bl_label = "Rename Bones"
	bl_idname = "view3d.bone_rename"
	

	def execute(self, context ):
		
		scn = context.scene
		
		oldName = scn.OldName
		newName = scn.NewName
		deleteName = scn.DelName

		for bone in bpy.context.selected_bones :
			
			# new name
			bone.name = bone.name.replace(oldName, newName)
			
			# delete
			if(len(deleteName) > 0):
				bone.name = bone.name [::-1].replace(deleteName[::-1], ""[::-1], 1)[::-1]	
			#	bone.name = bone.name.split(".")[].replace(deleteName, '')
				
			
		self.report({'INFO'},"All bones was renamed")
		
		return{'FINISHED'} 
	
			
################################################################
# register #	
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()