import bpy
from bpy.types import Menu


class EditorSwitcherPieMenuOptions(bpy.types.Operator):
	bl_idname = 'nodes.pie_menu_enum'
	bl_label = 'Editor Switcher Pie Menu Options'

	# https://docs.blender.org/api/2.79/bpy.types.Area.html#bpy.types.Area.type
	mode_options = [
		('VIEW_3D', '3D View', '', 'VIEW3D', 0),
		('IMAGE_EDITOR', 'UV/Image Editor', '', 'IMAGE_COL', 1),
		('NODE_EDITOR', 'Node Editor', '', 'NODETREE', 2),
		('DOPESHEET_EDITOR', 'Dope Sheet', '', 'ACTION', 3),
		('GRAPH_EDITOR', 'Graph Editor', '', 'IPO', 4),
		('TEXT_EDITOR', 'Text Editor', '', 'TEXT', 5),
		# TODO: add more ...
	]

	selected_mode = bpy.props.EnumProperty(
		items=mode_options,
		default='VIEW_3D'
	)

	def execute(self, context):
		bpy.context.area.type = self.selected_mode
		return {'FINISHED'}


class EditorSwitcherPieMenu(Menu):
	bl_label = 'Switch to:'

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		pie.operator_enum(EditorSwitcherPieMenuOptions.bl_idname, 'selected_mode')
