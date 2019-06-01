bl_info = {
	"name": "DMC4SE tool",
	"author": "Qing Guo",
	"blender": (2, 76, 0),
	"location": "View3D -> Tool Shelf -> DMC4SE tool",
	"description": "Tool that assists loading model & motion for DMC4SE.",
	"warning": "",
	"category": "Learnbgame",
}

import os
import bpy
import random
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
from .load_model_operator import LoadModelOperator
from .load_motion_operator import LoadMotionOperator, MOTION_FOLDER_MAP
from .play_motion_operator import PlayMotionOperator
from . import glb

def get_model_list():
	root = os.environ["DMC4SE_DATA_DIR"]
	model_root = os.path.join(root, "model/game")
	fnames = os.listdir(model_root)
	model_list = []
	for name in fnames:
		path = os.path.join(model_root, name)
		if not os.path.isdir(path):
			continue
		model_list.append((
			name, # identifier,
			name, # name,
			"", # description
			# icon(optional)
			# number(optional)
		))
	return model_list

def get_motion_list(self, context):
	model = context.scene.model
	root = os.environ["DMC4SE_DATA_DIR"]
	motion_folder = MOTION_FOLDER_MAP.get(model, model)
	motion_root = os.path.join(root, "motion/%s" % motion_folder)
	motion_list = []
	for dirpath, dirnames, filenames in os.walk(motion_root):
		for fname in filenames:
			if fname.endswith(".lmt"):
				name = os.path.splitext(fname)[0]
				name = os.path.normpath(os.path.join(dirpath, name))
				name = os.path.relpath(name, start=motion_root)
				motion_list.append((
					name, # identifier,
					name, # name,
					"", # description
					# icon(optional)
					# number(optional)
				))
	return motion_list

class DMC4SEPanel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_dmc4se"
	bl_label = "DMC4SE Tool"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'
	bl_category = 'Tools'
	
	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.prop(context.scene, "model", text="MOD")
		row.operator("dmc4se.load_model", text="Load")
		row = layout.row()
		row.prop(context.scene, "motion", text="MOT")
		row.operator("dmc4se.load_motion", text="Load")
		
		layout.prop(context.scene, "motion_index", text="Motion Id")
		row = layout.row()
		
		op = row.operator("dmc4se.play_motion", text="Prev")
		op.op = "PREV"
		op.index = context.scene.motion_index
		
		if context.screen.is_animation_playing:
			op = row.operator("dmc4se.play_motion", text="Pause")
			op.op = "PAUSE"
		else:
			op = row.operator("dmc4se.play_motion", text="Play")
			op.op = "PLAY"
		op.index = context.scene.motion_index
		
		op = row.operator("dmc4se.play_motion", text="Next")
		op.index = context.scene.motion_index
		op.op = "NEXT"
	
def register():
	bpy.utils.register_class(DMC4SEPanel)
	bpy.utils.register_class(LoadModelOperator)
	bpy.utils.register_class(LoadMotionOperator)
	bpy.utils.register_class(PlayMotionOperator)
	bpy.types.Scene.model = bpy.props.EnumProperty(
		items=get_model_list(),
		name="Model",
	)
	bpy.types.Scene.motion = bpy.props.EnumProperty(
		items=get_motion_list,
		name="Motion",
	)
	bpy.types.Scene.motion_index = bpy.props.IntProperty()
	
def unregister():
	bpy.utils.unregister_class(DMC4SEPanel)
	bpy.utils.unregister_class(LoadModelOperator)
	bpy.utils.unregister_class(LoadMotionOperator)
	bpy.utils.unregister_class(PlayMotionOperator)
	del bpy.types.Scene.model
	del bpy.types.Scene.motion
	del bpy.types.Scene.motion_index

if __name__ == '__main__':
	register()