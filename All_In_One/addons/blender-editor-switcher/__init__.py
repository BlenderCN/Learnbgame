import bpy
from .menu import EditorSwitcherPieMenu, EditorSwitcherPieMenuOptions


bl_info = {
	'name': 'Editor Switcher Pie Menu',
	'description': 'Pie menu to quickly switch to a different editor type',
	'category': 'User Interface',
	'support': 'COMMUNITY',
	# 'author': '...',
	# 'version': (1, 0),
	# 'blender': (2, 65, 0),
}


class EditorSwitcherOperator(bpy.types.Operator):
	bl_idname = 'wm.editor_switcher'
	bl_label = 'Editor Switcher'
	bl_options = {'REGISTER'}

	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name='EditorSwitcherPieMenu')
		return {'FINISHED'}


addon_keymaps = []


def register():
	bpy.utils.register_class(EditorSwitcherPieMenu)
	bpy.utils.register_class(EditorSwitcherPieMenuOptions)
	bpy.utils.register_class(EditorSwitcherOperator)

	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(
		name='Window',
		space_type='EMPTY',
		region_type='WINDOW'
	)
	# https://docs.blender.org/api/2.79/bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new
	kmi = km.keymap_items.new(
		EditorSwitcherOperator.bl_idname,
		type='ACCENT_GRAVE',
		value='PRESS',
		alt=True
	)
	addon_keymaps.append(km)


def unregister():
	bpy.utils.unregister_class(EditorSwitcherPieMenu)
	bpy.utils.unregister_class(EditorSwitcherPieMenuOptions)
	bpy.utils.unregister_class(EditorSwitcherOperator)

	wm = bpy.context.window_manager
	for km in addon_keymaps:
		wm.keyconfigs.addon.keymaps.remove(km)
	del addon_keymaps[:]


if __name__ == '__main__':
	register()
