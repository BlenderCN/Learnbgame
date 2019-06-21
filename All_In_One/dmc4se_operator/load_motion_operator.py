import os
import bpy
import random
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
from . import glb

MOTION_FOLDER_MAP = {
	"pl000_ex00": "pl000",
	"pl000_ex01": "pl000",
}

class LoadMotionOperator(bpy.types.Operator):
	bl_idname = "dmc4se.load_motion"
	bl_label = "Load Motion"
	
	def execute(self, context):
		# clear all motions
		for action in bpy.data.actions:
			action.user_clear()
			bpy.data.actions.remove(action)
		glb.all_motions = {}
		glb.motion_indices = []
		motion = context.scene.motion
		model = context.scene.model
		load = getattr(self, "load_motion_%s" % model, self.load_motion_default)
		load(context, model, motion)
		self.update_motion_list()
		return {"FINISHED"}
	
	def load_motion_default(self, context, model, motion):
		armat = context.scene.objects['armat']
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armat
		armat.select = True
		motion_folder = MOTION_FOLDER_MAP.get(model, model)
		self._load_lmt_file(model, motion)
	
	def load_motion_pl000(self, context, model, motion):
		armat = context.scene.objects['armat_body']
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armat
		armat.select = True
		self._load_lmt_file("pl000", motion)
		armat.select = False

		armat = context.scene.objects['armat_coat']
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armat
		armat.select = True
		self._load_lmt_file("pl000_03", motion.replace("pl000", "pl000_03"))
		
	def load_motion_pl006(self, context, model, motion):
		armat = context.scene.objects['armat_body']
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armat
		armat.select = True
		self._load_lmt_file("pl006", motion)
		armat.select = False

		armat = context.scene.objects['armat_coat']
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armat
		armat.select = True
		self._load_lmt_file("pl006_03", motion.replace("pl006", "pl006_03"))
		
	def _load_lmt_file(self, motion_folder, motion):
		directory = os.path.join(os.environ["DMC4SE_DATA_DIR"], "motion/%s" % motion_folder)
		if "/" in motion or "\\" in motion:
			directory = os.path.join(directory, os.path.split(motion)[0])
			motion = os.path.split(motion)[1]
		directory = os.path.normpath(directory)
		bpy.ops.import_animation.gtb(
			'EXEC_DEFAULT', directory=directory, files=[{"name": motion + ".gtba"}]
		)
		
	def update_motion_list(self):
		all_motions = {}
		for name, action in bpy.data.actions.items():
			name = name.split(".")[0]
			index = int("".join(filter(str.isdigit, name)))
			if index not in all_motions:
				all_motions[index] = []
			all_motions[index].append(action)
		glb.all_motions = all_motions
		glb.motion_indices = sorted(all_motions.keys())