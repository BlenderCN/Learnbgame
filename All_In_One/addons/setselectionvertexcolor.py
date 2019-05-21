# Set Selection Vertex Color v.01
# by Diego F. Goberna (@feiss) http://feiss.be

# Adds operator "Set Selection Vertex Color". 
# Run it with "Blender Render" active, so vertex colors are displayed on viewport

bl_info = {
	"name": "Set Selection Vertex Color",
	"author": "Diego F. Goberna",
	"version": (1, 0),
	"blender": (2, 75, 0),
	"location": "???",
	"description": "Assigs a color to the current vertex/edge/poly selection",
	"warning": "",
	"wiki_url": "",
	"category": "Mesh",
	}



import bpy
import random
from bpy.props import *

svc_red= 1.0
svc_blue= 0.0
svc_green= 0.0

class SetSelectionVertexColorOperator(bpy.types.Operator):
	
	bl_idname= "object.set_selection_vertex_color_operator"
	bl_label="Set Selection Vertex Color"
	col= FloatVectorProperty(name="Color", subtype="COLOR", default=(1.0, 0.0, 0.0), min=0.0, max=1.0, description="picker")
	randomfactor= FloatProperty(name="Randomize", default=0.0, min=0.0, max=1.0, description="amount of randomization")
	
	def execute(self, context):
		mesh= context.object.data

		#get selection (must be done in object mode)
		bpy.ops.object.mode_set(mode='OBJECT')
		selected= [v for v in mesh.vertices if v.select]
		#switch to vertex paint mode
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		if not mesh.vertex_colors.active: 
			bpy.ops.mesh.vertex_color_add()
		vclayer= mesh.vertex_colors.active
		
		col= list(self.col)
		for poly in mesh.polygons:
			r = (random.random() - 0.5) * self.randomfactor
			for idx in poly.loop_indices:
				is_selected= [v for v in selected if v.index==mesh.loops[idx].vertex_index]
				if not is_selected:	continue
				col2 = list(col)
				if self.randomfactor > 0:
					col2[0] += r
					col2[1] += r
					col2[2] += r
					col2[0] = max(0, min(col2[0], 1))
					col2[1] = max(0, min(col2[1], 1))
					col2[2] = max(0, min(col2[2], 1))
				vclayer.data[idx].color= col2
		#switch back to edit mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.context.space_data.viewport_shade= 'TEXTURED'
		return {'FINISHED'}
	
	def invoke(self, context, event):
		global svc_red, svc_blue, svc_green
		return context.window_manager.invoke_props_dialog(self)


class SetSelectionVertexColorPanel(bpy.types.Panel):
	"""Assigs a color to the current vertex/edge/poly selection"""
	bl_label = "Set Selection Vertex Color"
	bl_idname = "OBJECT_TOOLS_SetSelectionVertexColor"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'WINDOW'
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		obj = context.object
		vc= obj.vertex_colors.active.name or '<no vertex color map>'
		
		row = layout.row()
		row.label(text="Object: " + obj.name)
		row = layout.row()
		row.label(text="Vertex color: "+vc, icon='WORLD_DATA')

		row = layout.row()
		row.operator("object.set_selection_vertex_color_operator")


	
#bpy.utils.register_class(SetSelectionVertexColorOperator)
#bpy.utils.register_module(__name__)


def register():
	bpy.utils.register_class(SetSelectionVertexColorOperator)
	bpy.utils.register_class(SetSelectionVertexColorPanel)

def unregister():
	bpy.utils.unregister_class(SetSelectionVertexColorOperator)
	bpy.utils.unregister_class(SetSelectionVertexColorPanel)

if __name__ == "__main__":
	register()
