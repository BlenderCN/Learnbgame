import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_size"
	bl_label = "Scale to Size"
	bl_description = "Scale Islands to match their width or height"
	bl_options = {'REGISTER', 'UNDO'}

	mode : bpy.props.StringProperty(name="Mode", default="HEIGHT")
	padding : bpy.props.FloatProperty(description="Padding between UV islands", default=0.05)

	@classmethod
	def poll(cls, context):
		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True


	def execute(self, context):
		#Store selection
		utilities_uv.selection_store()

		main(context, self.mode, self.padding)

		#Restore selection
		utilities_uv.selection_restore()

		return {'FINISHED'}



def main(context, mode, padding):

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uv_layer = bm.loops.layers.uv.verify()
	
	# Face mode
	bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	islands = utilities_uv.getSelectionIslands()
	islands_size = {}
	islands_center = {}

	# Collect bounds
	for i in range(0, len(islands)):

		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.set_selected_uv_faces(islands[i])

		# Collect BBox sizes
		bounds = utilities_uv.getSelectionBBox()
		islands_size[i]= bounds['width'] if mode == 'WIDTH' else bounds['height']
		islands_center[i] = bounds['center'].x if mode =='WIDTH' else bounds['center'].y

	# Sort largest to smallest
	sorted_size = sorted(islands_size.items(), key=operator.itemgetter(1))#Sort by values, store tuples
	sorted_size.reverse()

	# Apply size to match largest
	for i in range(0, len(islands)):
		index = sorted_size[i][0]
		scale = sorted_size[0][1] / islands_size[index]

		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.set_selected_uv_faces(islands[index])

		bpy.ops.transform.resize(value=(scale, scale, 1), constraint_axis=(True, True, False), orient_type='GLOBAL')


	# Sort by position 
	sorted_center = sorted(islands_center.items(), key=operator.itemgetter(1))

	# Set position in order
	offset = None
	for i in range(0, len(islands)):
		index = sorted_size[i][0]
		
		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.set_selected_uv_faces(islands[index])

		bounds = utilities_uv.getSelectionBBox()

		if i > 0:
			if mode == 'HEIGHT':
				delta = offset - bounds['min']
				delta.y-= bounds['height']
				delta.x+= padding
				bpy.ops.transform.translate(value=(delta.x, delta.y, 0))
			else:
				delta = offset - bounds['max']
				delta.x+= bounds['width']
				delta.y-= padding
				bpy.ops.transform.translate(value=(delta.x, delta.y, 0))
			

			utilities_uv.set_selected_uv_faces(islands[index])
			bounds = utilities_uv.getSelectionBBox()

		if mode == 'HEIGHT':
			offset = bounds['max']
		else:
			offset = bounds['min']

def register():
	bpy.utils.register_class(op)

def unregister():
	bpy.utils.unregister_class(op)


