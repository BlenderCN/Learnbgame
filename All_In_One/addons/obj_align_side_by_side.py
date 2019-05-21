bl_info = {
	"name": "Align Objects Side by Side",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 79, 0),
	"location": "View3D > Operator Search > Align Objects Side by Side",
	"description": "Aligns objects side by side by their bounding boxes",
	"warning": "Changes objects origins",
	"wiki_url": "",
	"category": "Object"
}

import bpy
from bpy.props import EnumProperty, FloatProperty

"""
Class and bl_idname Names
[A-Z][A-Z0-9]*_{ABBREV}_[A-Za-z0-9_]+
Abbrev:
_HT_ Header
_MT_ Menu
_OT_ Operator
_PT_ Panel
_UL_ UIList
Ex:
Classname = ADDONABBREVIATION_OT_something
idname = object.addonabbreviation_ot_something
"""


class AOSBS_OT_align_obj_side_by_side(bpy.types.Operator):
	"""Aligns objects side by side by their bounding boxes"""
	bl_idname = "object.aosbs_ot_align_obj_side_by_side"
	bl_label = "Align Objects Side by Side"
	"""
		REGISTER
			Display in info window and support redo toolbar panel
		UNDO
			Push an undo event, needed for operator redo
		BLOCKING
			Block anthing else from moving the cursor
		MACRO
			?
		GRAB_POINTER
			Enables wrapping when continuous grab is enabled
		PRESET
			Display a preset button with operator settings
		INTERNAL
			Removes operator from search results
	"""
	bl_options = {'REGISTER', 'UNDO'}
	
	# Properties
	axis = EnumProperty(
		items=[
			("0","X","X axis","COLOR_RED",0),
			("1","Y","Y axis","COLOR_GREEN",1),
			("2","Z","Z axis","COLOR_BLUE",2)
			],
		name="Align Axis",
		description="Axis which the objects are aligned",
		default="0"
	)
		
	padding = FloatProperty(
		name="Padding",
		description="Padding added between objects",
		default=0
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.area.type == 'VIEW_3D'

	def execute(self, context):
		axis = int(self.axis)
		# Create a list
		objects = context.selected_objects[:]
		# Sort objects by axis
		objects.sort(key=lambda obj:obj.location[axis])
		# Set origins to center of their bounding boxes
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
		# Remove 1st object
		obj  = objects.pop(0)
		# Set Placer at 1st obj's position
		placer = obj.location[axis]
		# Add half of 1st obj's BB dimensions to Placer
		placer += (obj.dimensions[axis] / 2)
		# Add padding
		placer += self.padding
		# Repeat for rest
		while(objects):
			obj = objects.pop(0)
			placer += (obj.dimensions[axis] / 2)
			obj.location[axis] = placer
			placer += (obj.dimensions[axis] / 2)
			placer += self.padding
		
		return {'FINISHED'}


def register():
	bpy.utils.register_class(AOSBS_OT_align_obj_side_by_side)


def unregister():
	bpy.utils.unregister_class(AOSBS_OT_align_obj_side_by_side)


if __name__ == "__main__":
	register()

