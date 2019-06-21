import os
import bpy
import random
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)

class LoadModelOperator(bpy.types.Operator):
	bl_idname = "dmc4se.load_model"
	bl_label = "Load Model"
	
	def execute(self, context):
		# clear all model & armature
		if context.scene.objects:
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_by_type(type='MESH')
			bpy.ops.object.delete(use_global=False)
			bpy.ops.object.select_by_type(type='ARMATURE')
			bpy.ops.object.delete(use_global=False)
		
		model = context.scene.model
		load = getattr(self, "load_model_%s" % model, self.load_model_default)
		load(context, model)
		
		return {"FINISHED"}
	
	def load_model_default(self, context, model):
		self._load_mod_file(model, model + ".gtb")
		
	def load_model_em000(self, context, model):
		self._load_mod_file(model, random.choice(("em000", "em000_01")) + ".gtb")

	def load_model_em001(self, context, model):
		self._load_mod_file(model, random.choice(("em001", "em001_02")) + ".gtb")
		
	def load_model_em009(self, context, model):
		self._load_model_parts(model, 6)
	
	def load_model_em015(self, context, model):
		self._load_model_parts(model, 3)

	def load_model_em018(self, context, model):
		self._load_model_parts(model, 2)
		
	def load_model_em021(self, context, model):
		self.load_model_default(context, model)
		for i in range(1, 6):
			self._load_mod_file(model, model + "_%02d" % i + ".gtb")

	def load_model_em026(self, context, model):
		self._load_model_parts(model, 2)
		
	# Nero
	def load_model_pl000(self, context, model):
		self.get_load_pl_general(0)(context, model)
		
	def load_model_pl000_ex00(self, context, model):
		self.get_load_pl_general(0)(context, model)

	def load_model_pl000_ex01(self, context, model):
		self.get_load_pl_general(0)(context, model)

	def load_model_pl001(self, context, model):
		self._load_mod_file(model, "pl001.gtb")
		self._load_mod_file(model, "pl001_01.gtb")
		self._load_mod_file(model, "pl001_02.gtb")

	def load_model_pl002(self, context, model):
		self.get_load_pl_general(2)(context, model)

	def load_model_pl004(self, context, model):
		self.get_load_pl_general(4)(context, model)
		
	def load_model_pl006(self, context, model):
		self.get_load_pl_general(6, constraint=self.constraint_pl006_ex01)(context, model)
		
	def load_model_pl006_ex00(self, context, model):
		self.get_load_pl_general(6, constraint=self.constraint_pl006_ex01)(context, model)

	def load_model_pl006_ex01(self, context, model):
		self.get_load_pl_general(6, constraint=self.constraint_pl006_ex01)(context, model)

	def constraint_pl006_ex01(self, body, head, hair, coat):
		self._copy_transform(head, body, zip((0, 1, 2, 3, 4), (2, 3, 4, 5, 30)))
		if hair:
			self._copy_transform(hair, head, zip((0, 1), (1, 2)))
		# original: 0 -> 2
		
		# 3, 4, 6, 7,2, 5
		# 6,29,31,54,5,30
		self._copy_transform(coat, body, zip((0, 3, 4, 6, 7,2, 5), (2, 6,29,31,54,5,30)))
		
	# Lady
	def load_model_pl007(self, context, model):
		self.get_load_pl_general(7, constraint=self.constraint_pl007)(context, model)

	def load_model_pl007_ex01(self, context, model):
		self.get_load_pl_general(7, constraint=self.constraint_pl007)(context, model)

	def constraint_pl007(self, body, head, hair, coat):
		self._copy_transform(head, body, zip((0, 1, 2, 3, 4), (2, 53, 54, 3, 28)))
		if hair:
			self._copy_transform(hair, head, zip((0, 1), (1, 2)))
		self._copy_transform(coat, body, zip((0, ), (2, )))
		
	def load_model_pl008(self, context, model):
		self.get_load_pl_general(8, constraint=self.constraint_pl007)(context, model)
		
	def load_model_pl008_ex01(self, context, model):
		self.get_load_pl_general(8, constraint=self.constraint_pl007)(context, model)

	def load_model_pl022(self, context, model):
		self.get_load_pl_general(22)(context, model)

	def load_model_pl023(self, context, model):
		self.get_load_pl_general(23)(context, model)

	def load_model_pl024(self, context, model):
		self.get_load_pl_general(24)(context, model)
		
	def load_model_pl024_ex00(self, context, model):
		self.get_load_pl_general(24)(context, model)

	def load_model_pl024_ex01(self, context, model):
		self.get_load_pl_general(24)(context, model)
		
	# Vergil
	def load_model_pl030(self, context, model):
		cand = []
		for pl_index in (30, 32, 33):
			cand.append(self.get_load_pl_general(pl_index))
			cand.append(self.get_load_pl_general(pl_index, suf="_v"))
		load = random.choice(cand)		
		load(context, model)
		
	def load_model_pl030_ex00(self, context, model):
		return self.load_model_pl030(context, model)

	def load_model_pl030_ex01(self, context, model):
		return self.load_model_pl030(context, model)

	def _load_model_parts(self, model, n):
		for i in range(n):
			self._load_mod_file(model, model + "_%02d" % i + ".gtb")
			
	def _load_mod_file(self, model, mod_file, armat_name="armat"):
		directory = os.path.join(os.environ["DMC4SE_DATA_DIR"], "model/game/%s" % model)
		if not os.path.exists(os.path.join(directory, mod_file)):
			return
		bpy.ops.import_mesh.gtb(
			'EXEC_DEFAULT',
			directory=directory,
			files=[{"name": mod_file}],
			armat_name=armat_name,
		)
	
	def _copy_transform(self, armt_dst, armt_src, bone_pairs):
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = armt_dst
		armt_dst.select = True
		bpy.ops.object.mode_set(mode='POSE')
		for i, j in bone_pairs:
			b = armt_dst.pose.bones["Bone%d" % i]
			armt_dst.data.bones.active = b.bone	# wtf, poorly documented
			bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')
			cns = b.constraints['Copy Transforms']
			cns.target = armt_src
			cns.subtarget = "Bone%d" % j
		bpy.ops.object.mode_set(mode='OBJECT')
		armt_dst.select = False
		
	def constraint_pl_general(self, body, head, hair, coat):
		self._copy_transform(head, body, zip((0, 1, 2, 3, 4), (2, 3, 4, 5, 32)))
		if hair:
			self._copy_transform(hair, head, zip((0, 1), (1, 2)))
		self._copy_transform(coat, body, zip((0, ), (2, )))
		
	def get_load_pl_general(self, pl_index, suf="", use_constraint=True, constraint=None):
		if use_constraint and constraint is None:
			constraint = self.constraint_pl_general
		def load(context, model):
			base = "pl%03d%s" % (pl_index, suf)
			self._load_mod_file(model, base + ".gtb", armat_name="armat_body")
			self._load_mod_file(model, base + "_01.gtb", armat_name="armat_head")
			self._load_mod_file(model, base + "_02.gtb", armat_name="armat_hair")
			self._load_mod_file(model, base + "_03.gtb", armat_name="armat_coat")
			o = context.scene.objects
			if use_constraint:
				constraint(o["armat_body"], o["armat_head"], o.get("armat_hair"),
						   o.get("armat_coat"))
		return load