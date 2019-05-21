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
	"name": "Linked Physics",
	"author": "Cenek Strichel",
	"version": (1, 0, 3),
	"blender": (2, 79, 0),
	"location": "Physics > Linked Physic",
	"description": "Change settings for linked physic",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Header, Panel


# GUI ###############################################################
class VIEW3D_PT_tools_linkedPhysics(bpy.types.Panel):
	
	bl_label = "Linked Physics"
	bl_idname = "LINKED_PHYSICS_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Physics"
	bl_context = "objectmode"


	bpy.types.Scene.LinkedObjectName = StringProperty( name = "Cloth Object", description = "", default = "" )
	bpy.types.Scene.LinkedStartFrane = IntProperty( name = "Start Frame", description = "", default = 0 )
	bpy.types.Scene.LinkedEndFrane = IntProperty( name = "End Frame", description = "", default = 100 )
	
	
	def draw(self, context):
		
		scn = context.scene
		layout = self.layout

		col = layout.column(align=True)
		col.label("Cloth Name")
		col.prop(scn, "LinkedObjectName", text = "")


		row = layout.row(align=True)
		row.prop(scn, "LinkedStartFrane", text="Start")
		row.prop(scn, "LinkedEndFrane", text="End")
		
		col = layout.column(align=True)
		col.operator("object.linked_physics_set", text="Set Range", icon = "PHYSICS")
		
		'''
		col = layout.column(align=True)
		col.operator("ptcache.bake", text="Bake").bake = True
		col.operator("ptcache.free_bake", text="Free Bake")
		'''

class LinkedPhysicsSet(bpy.types.Operator):
	
	'''Set linked physics parameters'''
	bl_idname = "object.linked_physics_set"
	bl_label = "Set linked physics options"

	def execute(self, context):
		
		scn = bpy.context.scene
		obj = bpy.context.object
		
		try:
			ob = bpy.data.objects[ scn.LinkedObjectName ]
		except:
			self.report({'ERROR'}, "Object was not found!")
			return {'FINISHED'}
			
		modifier = False
		
		try:
			cache = ob.modifiers["Cloth"].point_cache
			cache.frame_start = scn.LinkedStartFrane
			cache.frame_end = scn.LinkedEndFrane
			modifier = True
		except:
			pass
		
		try:
			cache = ob.modifiers["Softbody"].point_cache
			cache.frame_start = scn.LinkedStartFrane
			cache.frame_end = scn.LinkedEndFrane
			modifier = True
		except:
			pass
		
		if(not modifier):
			self.report({'ERROR'}, "Supported physic modifier is not available!")
			
		for area in bpy.context.screen.areas:
			if area.type == 'PROPERTIES':
				area.tag_redraw()
		
		
		return {'FINISHED'}	



################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()