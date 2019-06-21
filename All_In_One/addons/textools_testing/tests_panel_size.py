import bpy
import os

from . import utilities

tests = []

# tests_size.append( TT_Test('size_dropdown', call=None))
# tests_size.append( TT_Test('op_uv_size_get', call=None))
# tests_size.append( TT_Test('op_uv_crop', call=None))
# tests_size.append( TT_Test('op_uv_resize', call=None))
# tests_size.append( TT_Test('op_texture_reload_all', call=None))
# tests_size.append( TT_Test('uv_channel', call=None))
# tests_size.append( TT_Test('op_uv_channel_add', call=None))
# tests_size.append( TT_Test('op_uv_channel_swap', call=None))


def test_op_uv_size_get():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.uv.textools_uv_size_get()
	size = bpy.context.scene.texToolsSettings.size
	return size[0] == 128 and size[1] == 32
tests.append( utilities.Op_Test('op_uv_size_get', python='op_uv_size_get', blend="test_op_uv_size_get", test=test_op_uv_size_get))


def test_op_uv_crop():
	for area in bpy.context.screen.areas:
		if area.type == 'IMAGE_EDITOR':
			# area.spaces[0].image = image
			print("... {}".format(type(area)))

	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.mode_set(mode='EDIT')
	override = utilities.get_context_override_uv()
	bpy.ops.uv.textools_uv_crop(override)
	return True
tests.append( utilities.Op_Test('op_uv_crop', python='op_uv_crop', blend="", test=test_op_uv_crop))
tests.append( utilities.Op_Test('op_uv_resize', python='op_uv_resize', blend=""))
tests.append( utilities.Op_Test('op_texture_reload_all', python='op_texture_reload_all', blend=""))
tests.append( utilities.Op_Test('uv_channel', python='uv_channel', blend=""))
tests.append( utilities.Op_Test('op_uv_channel_add', python='op_uv_channel_add', blend=""))
tests.append( utilities.Op_Test('op_uv_channel_swap', python='op_uv_channel_swap', blend=""))
tests.append( utilities.Op_Test('size_dropdown', python='', blend=""))

