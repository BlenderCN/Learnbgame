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
	"name": "Bones Color",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "N-Panel",
	"description": "Set bone color template",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy

from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import  Panel


class VIEW3D_PT_Bones_Color(Panel):

	
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Bones Color"
	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.active_object.type == 'ARMATURE' and context.active_object.mode == 'POSE')
	
	
	def draw(self, context):

		layout = self.layout

		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Red", icon = "COLORSET_01_VEC").themeName='THEME01'
		row.operator("view3d.set_bone_color", text="Orange", icon = "COLORSET_02_VEC").themeName='THEME02'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Green", icon = "COLORSET_03_VEC").themeName='THEME03'
		row.operator("view3d.set_bone_color", text="Blue", icon = "COLORSET_04_VEC").themeName='THEME04'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Pink", icon = "COLORSET_05_VEC").themeName='THEME05'
		row.operator("view3d.set_bone_color", text="Purple", icon = "COLORSET_06_VEC").themeName='THEME06'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Green L", icon = "COLORSET_07_VEC").themeName='THEME07'
		row.operator("view3d.set_bone_color", text="Blue L", icon = "COLORSET_08_VEC").themeName='THEME08'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Yellow", icon = "COLORSET_09_VEC").themeName='THEME09'
		row.operator("view3d.set_bone_color", text="White", icon = "COLORSET_10_VEC").themeName='THEME10'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Pink", icon = "COLORSET_11_VEC").themeName='THEME11'
		row.operator("view3d.set_bone_color", text="Green L", icon = "COLORSET_12_VEC").themeName='THEME12'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Grey", icon = "COLORSET_13_VEC").themeName='THEME13'
		row.operator("view3d.set_bone_color", text="Brown", icon = "COLORSET_14_VEC").themeName='THEME14'
		
		row = layout.row(align = True)
		row.operator("view3d.set_bone_color", text="Green D", icon = "COLORSET_15_VEC").themeName='THEME15'
	
		
class SetBoneColor(bpy.types.Operator):

	'''Cut strip by scene setting'''
	bl_idname = "view3d.set_bone_color"
	bl_label = "Set Bone Color"
	bl_options = {'REGISTER', 'UNDO'}

	themeName = StringProperty(name="Theme Name")
	
	def execute(self, context):
	
		# new group
		bpy.ops.pose.group_assign(type=0)

		obj = bpy.context.active_object
		obj.pose.bone_groups[ len(obj.pose.bone_groups)-1 ].name = self.themeName # new name by theme name
		
		groupName = ( obj.pose.bone_groups[ len(obj.pose.bone_groups)-1 ].name )
		bone_group = obj.pose.bone_groups[ groupName ]
		
		# change color group
		bone_group.color_set = self.themeName
		
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