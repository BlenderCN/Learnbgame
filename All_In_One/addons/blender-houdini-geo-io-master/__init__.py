import os
import sys

import numpy

import bpy

from bpy.types import Panel, Menu
from bpy.types import PropertyGroup
from bpy.props import (
	BoolProperty,
	IntProperty,
	EnumProperty,
	FloatVectorProperty,
	StringProperty,
	PointerProperty,
)

import importlib

from .hio import hio
importlib.reload(hio)

from . import exporter
importlib.reload(exporter)

from . import importer
importlib.reload(importer)

bl_info = {
	"name": "Houdini Geo IO",
	"author": "satoruhiga",
	"version": (1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"description": "",
	"warning": "",
	"support": "COMMUNITY",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"
}

class SCENE_OT_LoadGeo(bpy.types.Operator):
	bl_idname = "houdini_io.load_geo"
	bl_label = "NOP"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		path = bpy.context.object.houdini_io.filepath
		
		if not path:
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode="OBJECT")

		path = bpy.path.abspath(path)
		ob = bpy.context.object
		opts = {}

		new_data = importer.import_(path, ob, opts)

		if not new_data:
			return {'CANCELLED'}
		
		name = ob.data.name
		
		old_data = ob.data
		old_data.name = '_temp_' + name

		new_data.name = name
		ob.data = new_data

		# remove old data
		db = eval(repr(old_data).split('[')[0])
		db.remove(old_data)

		ob.update_from_editmode()

		return {'FINISHED'}

class SCENE_OT_SaveGeo(bpy.types.Operator):
	bl_idname = "houdini_io.save_geo"
	bl_label = "NOP"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		path = bpy.context.object.houdini_io.filepath
		
		if not path:
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode="OBJECT")

		path = bpy.path.abspath(path)
		ob = bpy.context.object

		opts = {}
		res = exporter.export(path, ob, opts)

		if not res:
			return {'CANCELLED'}

		return {'FINISHED'}

class SCENE_PT_HoudiniIO(Panel):
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	bl_label = "Houdini Geo IO"

	@classmethod
	def poll(cls, context):
		ob = context.object
		data = ob.data

		if (isinstance(data, bpy.types.Mesh)
			or isinstance(data, bpy.types.Curve)
			# or isinstance(data, bpy.types.GreasePencil)
			):
			return True

		return False

	def draw_header(self, context):
		layout = self.layout
		layout.label(text="", icon='MESH_MONKEY')

	def draw(self, context):
		scene = context.scene

		layout = self.layout

		layout.prop(bpy.context.object.houdini_io, 'load_sequence', text='Load Sequence')

		if bpy.context.object.houdini_io.load_sequence:
			layout.prop(bpy.context.object.houdini_io, 'filepath_template', text="Path Template")	
			layout.prop(bpy.context.object.houdini_io, 'frame', text='Frame')

		layout.prop(bpy.context.object.houdini_io, 'filepath', text="File")

		layout.operator(SCENE_OT_LoadGeo.bl_idname, text="Load Geo")
		layout.operator(SCENE_OT_SaveGeo.bl_idname, text="Save Geo")


###

frame_update_targets = []

def update_geometry(o):
	try:
		s = o.filepath_template.format(o.frame)
		o.filepath = s
	except:
		print('invalid filepath format:', o)
	
	ob = o.id_data

	bpy.ops.object.mode_set(mode="OBJECT")

	path = o.filepath
	path = bpy.path.abspath(path)

	opts = {}

	new_data = importer.import_(path, ob, opts)

	if not new_data:
		return {'CANCELLED'}
	
	name = ob.data.name
	
	old_data = ob.data
	old_data.name = '_temp_' + name

	new_data.name = name
	ob.data = new_data

	# remove old data
	db = eval(repr(old_data).split('[')[0])
	db.remove(old_data)

	ob.update_from_editmode()

def frame_change_cb(scene):
	for x in frame_update_targets:
		update_geometry(x)

def append_frame_change_cb(self, context):
	if not frame_change_cb in bpy.app.handlers.frame_change_post:
		bpy.app.handlers.frame_change_post.append(frame_change_cb)
	
	global frame_update_targets

	try:
		if self.load_sequence:
			frame_update_targets.append(self)
		else:
			frame_update_targets.remove(self)
	except:
		print('update frame_update_targets failed')

def frame_number_changed_cb(self, context):
	update_geometry(self)

###

class ObjectHoudiniIO(PropertyGroup):
	load_sequence: BoolProperty(name='Load Sequence', update=append_frame_change_cb)
	filepath_template: StringProperty(name='Path Template', subtype='FILE_PATH')
	frame: IntProperty(name='Frame', update=frame_number_changed_cb)

	filepath: StringProperty(name='File Path', subtype='FILE_PATH')

classes = (
	ObjectHoudiniIO,
	SCENE_PT_HoudiniIO,
	SCENE_OT_LoadGeo,
	SCENE_OT_SaveGeo,
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)

	bpy.types.Object.houdini_io = PointerProperty(type=ObjectHoudiniIO)

def unregister():
	del bpy.types.Object.houdini_io

	from bpy.utils import unregister_class
	for cls in classes:
		unregister_class(cls)

if __name__ == "__main__":
	register()

