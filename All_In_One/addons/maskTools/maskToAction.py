
from mathutils import Vector

import bmesh
import bpy
import collections
import mathutils
import math
from bpy_extras import view3d_utils
from bpy.types import (
		Operator,
		Menu,
		Panel,
		PropertyGroup,
		AddonPreferences,
		)
from bpy.props import (
		BoolProperty,
		EnumProperty,
		FloatProperty,
		IntProperty,
		PointerProperty,
		StringProperty,
		)


class MaskModSmooth(bpy.types.Operator):
	'''Mask Smooth Surface'''
	bl_idname = "mesh.maskmod_smooth"
	bl_label = "Mask Smooth Surface"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'

	bpy.types.Scene.maskmod_smooth_strength = bpy.props.IntProperty(name = "Smooth strength", default = 10, min=-100, max=100)
	bpy.types.Scene.maskmod_smooth_apply = bpy.props.BoolProperty(name = "Smooth Apply", default = True)

	def execute(self, context):
		maskmod_smooth_strength = context.scene.maskmod_smooth_strength # update property from user input
		maskmod_smooth_apply = context.scene.maskmod_smooth_apply # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :

			bpy.ops.mesh.masktovgroup()
			bpy.ops.mesh.masktovgroup_append()
			bpy.ops.sculpt.sculptmode_toggle()
			bpy.ops.object.modifier_add(type='SMOOTH')
			bpy.context.object.modifiers["Smooth"].iterations = maskmod_smooth_strength
			bpy.context.object.modifiers["Smooth"].vertex_group = "Mask"
			if maskmod_smooth_apply == True:
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")
				bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

			bpy.ops.sculpt.sculptmode_toggle()
			# bpy.ops.mesh.vgrouptomask_append()


		if dynatopoEnabled :
			bpy.ops.sculpt.dynamic_topology_toggle()
		return {'FINISHED'}

class MaskModDisplace(bpy.types.Operator):
	'''Mask Smooth Surface'''
	bl_idname = "mesh.maskmod_displace"
	bl_label = "Mask Displace Surface"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'

	bpy.types.Scene.maskmod_displace_strength = bpy.props.FloatProperty(name = "Displace strength", default = 0.2, min=-100, max=100)
	bpy.types.Scene.maskmod_displace_apply = bpy.props.BoolProperty(name = "Displace Apply", default = True)

	# bpy.types.Scene.maskmod_displace_apply: bpy.props.BoolProperty(
	# name="maskmod_displace_apply",
	# default=True,
	# description="maskmod_displace_apply"
	# )



	def execute(self, context):
		maskmod_displace_strength = context.scene.maskmod_displace_strength # update property from user input
		maskmod_displace_apply = context.scene.maskmod_displace_apply # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :

			bpy.ops.mesh.masktovgroup()
			bpy.ops.mesh.masktovgroup_append()
			bpy.ops.sculpt.sculptmode_toggle()
			bpy.ops.object.modifier_add(type='DISPLACE')
			# bpy.context.object.modifiers["Displace"].name = "Displace_mask"

			bpy.context.object.modifiers["Displace"].strength = maskmod_displace_strength
			bpy.context.object.modifiers["Displace"].vertex_group = "Mask"
			if maskmod_displace_apply == True:
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Displace")
				bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

			bpy.ops.sculpt.sculptmode_toggle()
			# bpy.ops.mesh.vgrouptomask_append()


		if dynatopoEnabled :
			bpy.ops.sculpt.dynamic_topology_toggle()
		return {'FINISHED'}


class MaskModSolidify(bpy.types.Operator):
	'''Mask Solidify'''
	bl_idname = "mesh.maskmod_solidify"
	bl_label = "Mask Solidify"
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	#
	# def poll(cls, context):
	#
	# 	return context.active_object is not None and context.active_object.mode == 'SCULPT'

	bpy.types.Scene.maskmod_solidify_thickness = bpy.props.FloatProperty(name = "Solidify strength", default = 0.2, min=-100, max=100)
	bpy.types.Scene.maskmod_solidify_apply = bpy.props.BoolProperty(name = "Solidify Apply", default = True)

	# bpy.types.Scene.maskmod_displace_apply: bpy.props.BoolProperty(
	# name="maskmod_displace_apply",
	# default=True,
	# description="maskmod_displace_apply"
	# )



	def execute(self, context):
		maskmod_solidify_thickness = context.scene.maskmod_solidify_thickness # update property from user input
		maskmod_solidify_apply = context.scene.maskmod_solidify_apply # update property from user input


		# dynatopoEnabled = False

		# if context.active_object.mode == 'SCULPT' :

		# bpy.ops.mesh.masktovgroup()
		# bpy.ops.mesh.masktovgroup_append()
		# bpy.ops.sculpt.sculptmode_toggle()
		bpy.ops.object.modifier_add(type='SOLIDIFY')
		# bpy.context.object.modifiers["Displace"].name = "Displace_mask"

		bpy.context.object.modifiers["Solidify"].thickness = maskmod_solidify_thickness
		# bpy.context.object.modifiers["Solidify"].vertex_group = "Mask"
		if maskmod_solidify_apply == True:
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
			# bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

			# bpy.ops.sculpt.sculptmode_toggle()
			# bpy.ops.mesh.vgrouptomask_append()


		# if dynatopoEnabled :
		# 	bpy.ops.sculpt.dynamic_topology_toggle()
		return {'FINISHED'}







class MaskExturde(bpy.types.Operator):
	''' Mask Exturde '''
	bl_idname = "masktools.mask_exturde"
	bl_label = "Mask Exturde"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'

	# bpy.types.Scene.mask_exturde = bpy.props.FloatProperty(name = "Mask Exturde Volume", default = -0.2)
	bpy.types.Scene.mask_exturde_volume = bpy.props.FloatProperty(name = "Exturde Volume", default = 0.2, min=-100, max=100)
	bpy.types.Scene.mask_exturde_edgerelax = bpy.props.BoolProperty(name = "Exturde Edge Relax", default = True)

	def execute(self, context):
		mask_exturde_volume = context.scene.mask_exturde_volume # update property from user input
		mask_exturde_edgerelax = context.scene.mask_exturde_edgerelax # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :


			# bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
			bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
			# bpy.ops.object.mode_set(mode="EDIT")
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
			bpy.ops.mesh.reveal()
			if mask_exturde_edgerelax == True:
				bpy.ops.mesh.region_to_loop()
				bpy.ops.mesh.looptools_relax(input='selected', interpolation='cubic', iterations='25', regular=True)
				bpy.ops.mesh.loop_to_region()
			bpy.ops.mesh.extrude_region_shrink_fatten(MESH_OT_extrude_region={},TRANSFORM_OT_shrink_fatten={"value": mask_exturde_volume,})
			bpy.ops.sculpt.sculptmode_toggle()

			if dynatopoEnabled :
				bpy.ops.sculpt.dynamic_topology_toggle()

		return {'FINISHED'}





class MaskDuplicate(bpy.types.Operator):
	''' Mask Duplicate '''
	bl_idname = "mesh.mask_duplicate"
	bl_label = "Mask Duplicate"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'

	def execute(self, context):
		# mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :
		   bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		   bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードに戻す
		   bpy.ops.object.select_all(action='DESELECT') #全選択解除で最後に選択するものを複製したものだけにする
		   bpy.ops.object.editmode_toggle() # 編集モード
		   bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		   bpy.ops.mesh.reveal() # 隠しているものを表示
		   #   	 bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0))
		   bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		   bpy.context.scene.tool_settings.use_mesh_automerge = False
		   bpy.ops.mesh.duplicate_move(MESH_OT_duplicate=None, TRANSFORM_OT_translate=None)
		   # bpy.ops.mesh.duplicate_move() # 選択部分を複製
		   #   	bpy.ops.mesh.edge_face_add() # 閉じたオブジェクトにする
		   #   	bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY') # 閉じた面を三角形化
		   bpy.ops.mesh.separate(type='SELECTED') # 選択部分を分離
		   bpy.ops.object.editmode_toggle() # オブジェクトモード
		   bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') #重心に原点を配置して、回転しやすいように
		   bpy.context.scene.tool_settings.use_mesh_automerge = True

		   if dynatopoEnabled :
			   bpy.ops.sculpt.dynamic_topology_toggle()

		return {'FINISHED'}



class MaskSeparate(bpy.types.Operator):
	''' Mask Separate '''
	bl_idname = "mesh.mask_separate"
	bl_label = "Mask Separate"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'

	def execute(self, context):
		# mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :
		   bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		   bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードに戻す
		   bpy.ops.object.select_all(action='DESELECT') #全選択解除で最後に選択するものを複製したものだけにする
		   bpy.ops.object.editmode_toggle() # 編集モード
		   bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		   bpy.ops.mesh.reveal() # 隠しているものを表示
		   #   	 bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0))
		   bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		   bpy.ops.mesh.separate(type='SELECTED') # 選択部分を分離
		   bpy.ops.object.editmode_toggle() # オブジェクトモード
		   bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') #重心に原点を配置して、回転しやすいように

		   if dynatopoEnabled :
			   bpy.ops.sculpt.dynamic_topology_toggle()

		return {'FINISHED'}



class MaskOutlinerelax(bpy.types.Operator):
	''' Mask relax '''
	bl_idname = "mesh.mask_outline_relax"
	bl_label = "Mask Outline Relax"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod

	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == 'SCULPT'
	bpy.types.Scene.mask_outlinerelax_remove_doubles = bpy.props.FloatProperty(name = "Exturde Volume", default = 0.00, min=0, max=10)

	def execute(self, context):
		# mask_sharp_thick = context.scene.mask_sharp_thick # update property from user input
		mask_outlinerelax_remove_doubles = context.scene.mask_outlinerelax_remove_doubles # update property from user input


		dynatopoEnabled = False

		if context.active_object.mode == 'SCULPT' :
			bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
			bpy.ops.mesh.reveal()
			bpy.ops.mesh.region_to_loop()
			bpy.ops.mesh.remove_doubles(threshold=mask_outlinerelax_remove_doubles)
			bpy.ops.mesh.looptools_relax(input='selected', interpolation='cubic', iterations='25', regular=True)
			bpy.ops.mesh.loop_to_region()
			bpy.ops.sculpt.sculptmode_toggle()

			if dynatopoEnabled :
				bpy.ops.sculpt.dynamic_topology_toggle()

		return {'FINISHED'}


class MaskOpenall(bpy.types.Operator):
	''' Mask Separate '''
	bl_idname = "masktools.open_all"
	bl_label = "mask tools menu open all"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.screen.open_all == False:
			bpy.context.screen.open_vgroup = True
			bpy.context.screen.open_mask = True
			bpy.context.screen.open_smoothsharp = True
			bpy.context.screen.open_fatless = True
			bpy.context.screen.open_edgecavity = True
			bpy.context.screen.open_modifier = True
			bpy.context.screen.open_misc = True
			bpy.context.screen.open_all = True

		elif context.screen.open_all == True:
			bpy.context.screen.open_vgroup = False
			bpy.context.screen.open_mask = False
			bpy.context.screen.open_smoothsharp = False
			bpy.context.screen.open_fatless = False
			bpy.context.screen.open_edgecavity = False
			bpy.context.screen.open_modifier = False
			bpy.context.screen.open_misc = False
			bpy.context.screen.open_all = False



		return {'FINISHED'}






def register():

	bpy.types.Scene.mask_outlinerelax_remove_doubles = MaskModSmooth.mask_outlinerelax_remove_doubles
	bpy.types.Scene.mask_exturde_volume = MaskModSmooth.mask_exturde_volume
	bpy.types.Scene.mask_exturde_edgerelax = MaskModSmooth.mask_exturde_edgerelax
	bpy.types.Scene.maskmod_smooth_strength = MaskModSmooth.maskmod_smooth_strength
	bpy.types.Scene.maskmod_smooth_apply = MaskModSmooth.maskmod_smooth_apply
	bpy.types.Scene.maskmod_displace_strength = MaskModDisplace.maskmod_displace_strength
	bpy.types.Scene.maskmod_displace_apply = MaskModDisplace.maskmod_displace_apply
	bpy.types.Scene.maskmod_solidify_thickness = MaskModSolidify.maskmod_Solidify_thickness
	bpy.types.Scene.maskmod_solidify_apply = MaskModSolidify.maskmod_Solidify_apply


	bpy.utils.register_module(__name__)


def unregister():

	bpy.types.Scene.mask_outlinerelax_remove_doubles
	bpy.types.Scene.mask_exturde_volume
	bpy.types.Scene.mask_exturde_edgerelax
	bpy.types.Scene.maskmod_smooth_strength
	bpy.types.Scene.maskmod_smooth_apply
	bpy.types.Scene.maskmod_displace_strength
	bpy.types.Scene.maskmod_displace_apply
	bpy.types.Scene.maskmod_solidify_thickness
	bpy.types.Scene.maskmod_solidify_apply

	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
