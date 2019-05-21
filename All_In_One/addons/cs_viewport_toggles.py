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
	"name": "Viewport Toggles",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "View 3D header",
	"description": "Several commands in 3D View header",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	
import bpy
from bpy.types import Header, Panel
	
###################################	
# VIEW 3D HEADER #
###################################
class VIEW3D_HT_header_cenda(Header):
	
	bl_space_type = 'VIEW_3D'


	def draw(self, context):
		
		space = bpy.context.space_data
		
		# Normal view
		if(space.region_3d.view_perspective != 'CAMERA'): # only for non camera
		
			layout = self.layout
			
			row = layout.row(align=True)
			row = layout.row(align=True)
			
			#################################################
			# quad view
			row.operator("screen.region_quadview", text = "Quad View", icon = "GRID")
			
			# simplify			
			state = bpy.context.scene.render.use_simplify
			
			if (state) :
				current_icon = 'CHECKBOX_HLT'
			else:
				current_icon = 'CHECKBOX_DEHLT'
				
			row.operator("scene.simplify_toggle", icon = current_icon)
				
			#################################################	
			# culling	
			row = layout.row(align=True)	
			state = bpy.context.space_data.show_backface_culling

			if (state) :
				current_icon = 'CHECKBOX_HLT'
			else:
				current_icon = 'CHECKBOX_DEHLT'
			
			row.operator("scene.backface_toggle", icon = current_icon)

			# texture	
			if( context.scene.render.engine == "BLENDER_RENDER" and context.object.type == "MESH"):
				row.operator("scene.texture_toggle")
			
			'''
			#################################################
			# export
			row = layout.row(align=True)
			
			if(bpy.context.active_object.mode  == 'OBJECT'):
				row.enabled = True
			else:
				row.enabled = False
				
			# only first override is used
			textExport = context.scene.ExportPath.rsplit('\\', 1)[-1]
		#	icon = "EXPORT"
			
			for obj in bpy.context.selected_objects:
				if( obj.ExportOverride ):
					textExport = "[ " + context.object.ExportPathOverride.rsplit('\\', 1)[-1] + " ]"	
				#	icon = "PMARKER_ACT"
					break
				
			if(len(textExport) > 0):
				row.operator("cenda.export_to_place", icon = "EXPORT", text = textExport)
			'''
			'''
			# fluid bake
			obj = bpy.context.active_object
			if "Fluidsim" in obj.modifiers :
			#	if fluid.type == 'DOMAIN':
			#	row.operator("fluid.bake", text="Bake",translate=False, icon='MOD_FLUIDSIM')
				row.operator("object.bake_fluid", text="Bake",translate=False, icon='MOD_FLUIDSIM')
			'''

'''
class BakeFluid(bpy.types.Operator):

	bl_idname = "object.bake_fluid"
	bl_label = "Bake Fluid"
#	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.fluid.bake()
		return {'FINISHED'}
'''		


class SimplifyToggle(bpy.types.Operator):

	'''Simplify Toggle'''
	bl_idname = "scene.simplify_toggle"
	bl_label = "Simplify"
	
	def execute(self, context):

		bpy.context.scene.render.use_simplify = not bpy.context.scene.render.use_simplify

		return {'FINISHED'}
	
	
class BackfaceToggle(bpy.types.Operator):

	'''Backface'''
	bl_idname = "scene.backface_toggle"
	bl_label = "Culling"
	
	def execute(self, context):

		bpy.context.space_data.show_backface_culling = not bpy.context.space_data.show_backface_culling

		return {'FINISHED'}

		
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()