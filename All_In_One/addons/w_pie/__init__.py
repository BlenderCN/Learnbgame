#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import sys
import os, csv, codecs

from . import *
from . import w_pie
from . import add_pie
from . import uv_pie
from . import misc_pie
from bpy.types import Operator, AddonPreferences

import bpy, os
from bpy.types import Menu, Header
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
from mathutils import *
import math

import sys


bl_info = {
	"name": "w_pie",
	"author": "Bookyakuno & Cédric Lepiller & Jimmy & DavideDozza & Lapineige & Leafar & 0rAngE & chaosdesk",
	"version": (0, 2, 8),
	"blender": (2, 79, 0),
	"description": "Extend Right click with pie menu.",
	"category": "Learnbgame"
}


def _call_globals(attr_name):
	for m in globals().values():
		if hasattr(m, attr_name):
			getattr(m, attr_name)()


def _flush_modules(pkg_name):
	pkg_name = pkg_name.lower()
	for k in tuple(sys.modules.keys()):
		if k.lower().startswith(pkg_name):
			del sys.modules[k]













class w_pie_Prefs(bpy.types.AddonPreferences):

	bl_idname = __name__

	bpy.types.Scene.Enable_Tab_01 = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.Enable_Tab_02 = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.Enable_Tab_03 = bpy.props.BoolProperty(default=False)

	def draw(self, context):
		layout = self.layout

		layout.prop(context.scene, "Enable_Tab_01", text="Info", icon="QUESTION")
		if context.scene.Enable_Tab_01:
			row = layout.row()

			# layout.label(text="It will not be saved if you change it with keymap list of this addon.")
			layout.label(text="Extend Right click with pie menu.")
			layout.label(text="Only necessary functions - Accessible - Easy to use concept as a concept,")
			layout.label(text="Key setting with centering on Right click.")
			layout.label(text="Other, addition of objects, selection with UV editor, fine addition function, etc.")
			layout.label(text="")
			# # # # # # # # # # # # # # # # # # # # # # # #
			#
			# # # # # # # # # # # # # # # # # # # # # # # #

			row = layout.row(align=False)
			box = row.box()
			box.label(text="-Shortcut-")
			layout.label(text="(SELECTMOUSE is write it as a LEFT)")

			# このアドオンは、"wazou pie menu" をコンパクトに改造し、さらに機能を追加したものです。
			# >右クリックからの呼び出し
			# >"新規オブジェクト追加 pie"
			# >"UV pie"を追加





			scene = context.scene
			cscene = scene.cycles
			rd = context.scene.render



			col = layout.column(align=True)


			# col = split.column()
			row = col.row(align=True)
			row.label(text="Mesh Select Mode", icon='FACESEL')
			row.label(text="Right Mouse")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Add", icon='MONKEY')
			row.label(text="Right Mouse + Shift")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Shading", icon='MATERIAL')
			row.label(text="Right Mouse + Shift + Alt")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Pivot", icon='ROTATECOLLECTION')
			row.label(text="Right Mouse + Alt")


			split = layout.split()
			row = col.row(align=True)
			row.label(text="Views", icon='NODETREE')
			row.label(text="Ctrl + Q")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Views misc", icon='NODETREE')
			row.label(text="Ctrl + shift + Q")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Cursor/Origin", icon='CURSOR')
			row.label(text="Shift + S")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Select", icon='BORDER_RECT')
			row.label(text="Shift + G")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="UV", icon='OUTLINER_OB_LATTICE')
			row.label(text="Ctrl + D")

			split = layout.split()
			row = col.row(align=True)
			row.label(text="Misc/Modeling toolkit", icon='COLOR')
			row.label(text="Ctrl + F")

			# # # # # # # # # # # # # # # # # # # # # # # #
			#
			# # # # # # # # # # # # # # # # # # # # # # # #
			row = layout.row(align=False)
			box = row.box()
			box.label(text="-Setting-")
			layout.label(text="Change the the system setting select button to the LEFT!!", icon="ERROR")
			input_prefs = context.user_preferences.inputs
			row = layout.row()
			col = row.column()
			sub = col.column()
			row.label(text="User Preferences")
			row.label(text="Select With:")
			row.row().prop(input_prefs, "select_mouse", expand=True)

			# # # # # # # # # # # # # # # # # # # # # # # #
			#
			# # # # # # # # # # # # # # # # # # # # # # # #

			row = layout.row()
			col = row.column()
			sub = col.column()
			col.label(text="")
			box = col.box()
			box.label(text="-Use Addon-")
			col.label(text="You can access the following addon with Pie misc with Ctrl + F.")
			row = col.row(align=True)
			row.label(text="- LoopTools", icon='META_EMPTY')
			row.label(text="Mesh modeling toolkit (Installed by default. But it is disabled). ")
			row = col.row(align=True)
			row.label(text="- Bool Tool", icon='ROTATECOLLECTION')
			row.label(text="Boolean toolkit (Installed by default. But it is disabled). ")
			row = col.row(align=True)
			row.separator()
			row.label(text="You can access the following addon In the mesh select mode with the Right click.")
			row = col.row(align=True)
			row.operator("wm.url_open", text="- Multi Object UV Editing" , icon="URL").url = "https://github.com/ndee85/Multi-Object-UV-Editing"
			row.label(text="a quick way to create one UV Layout for multiple objects.")
			layout.label(text="")





		layout.prop(context.scene, "Enable_Tab_03", text="URL's", icon="URL")
		if context.scene.Enable_Tab_03:
			row = layout.row()


			layout.label(text="This add-on is a compact modified 'wazou pie menu'and added functions.")
			layout.label(text="Combined add-ons")
			layout.label(text="> Jimmy_pie_uv")
			layout.label(text="> Add Object Pie Menu")
			layout.operator("wm.url_open", text="Wazou Pie Menus" , icon="URL").url = "https://github.com/pitiwazou/Scripts-Blender/blob/Older-Scripts/Wazou_Pie_Menus"
			layout.operator("wm.url_open", text="Multi Object UV Editing" , icon="URL").url = "https://github.com/ndee85/Multi-Object-UV-Editing"
			layout.operator("wm.url_open", text="Project From Normal" , icon="URL").url = "https://github.com/chaosdesk/blender_uv_prj_from_normal/blob/master/uv_prj_from_normal.py"
			layout.separator()
			row = layout.row()
			row.operator("wm.url_open", text="Bookyakuno github" , icon="URL").url = "https://github.com/bookyakuno/-Blender-/blob/master/w_pie.zip"
			row = layout.row()
			row.operator("wm.url_open", text="Pitiwazou.com" , icon="URL").url = "http://www.pitiwazou.com/"
			row.operator("wm.url_open", text="Wazou's Ghitub" , icon="URL").url = "https://github.com/pitiwazou/Scripts-Blender"
			row.operator("wm.url_open", text="BlenderLounge Forum" , icon="URL").url = "http://blenderlounge.fr/forum/"
			row.operator("wm.url_open", text="chaosdesk" , icon="URL").url = "http://chaosdesk.blog123.fc2.com/"
			row = layout.row()






# 翻訳辞書の取得
def GetTranslationDict():
	dict = {}
	path = os.path.join(os.path.dirname(__file__), "TranslationDictionary.csv")
	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		dict['ja_JP'] = {}
		for row in reader:
			for context in bpy.app.translations.contexts:
				dict['ja_JP'][(context, row[1])] = row[0]
		"""
		for lang in bpy.app.translations.locales:
			if (lang == 'ja_JP'):
				continue
			dict[lang] = {}
			for row in reader:
				for context in bpy.app.translations.contexts:
					dict[lang][(context, row[0])] = row[1]
		"""
	return dict












addon_keymaps = []

def register():
	bpy.utils.register_class(w_pie_Prefs)
	bpy.utils.register_module(__name__)
	# bpy.app.translations.register(__name__, translation_dict)   # 辞書の登録

	translation_dict = GetTranslationDict()
	bpy.app.translations.register(__name__, translation_dict)


# Keympa Config

	wm = bpy.context.window_manager

	if wm.keyconfigs.addon:
		#Select Mode
		km = wm.keyconfigs.addon.keymaps.new('Object Non-modal', space_type='EMPTY', region_type='WINDOW', modal=False)
		kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS')
		kmi.properties.name = "pie.objecteditmode"

		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS')
		kmi.properties.name = "pie.objecteditmode"

		#Views
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS', ctrl=True)
		kmi.properties.name = "pie.areaviews"
		#Views
		km = wm.keyconfigs.addon.keymaps.new(name='Window')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'Q', 'PRESS', ctrl=True, shift=True)
		kmi.properties.name = "pie.view_misc"

		#Origin/Pivot
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS', alt=True)
		kmi.properties.name = "pie.pivotpoint"

		# cursor
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True)
		kmi.properties.name = "pie.originpivot"
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True)
		kmi.properties.name = "pie.originpivot"

		#Shading
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS', alt=True, shift=True)
		kmi.properties.name = "pie.shadingview"

		# #Object shading
		# km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		# kmi = km.keymap_items.new('wm.call_menu_pie', 'Z', 'PRESS', shift=True)
		# kmi.properties.name = "pie.objectshading"

		#Selection Object Mode
		km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'G', 'PRESS', shift=True)
		kmi.properties.name = "pie.selectionsom"

		#Selection Edit Mode
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'G', 'PRESS', shift=True)
		kmi.properties.name = "pie.selectionsem"

		#uv_pie
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'D', 'PRESS', ctrl=True)
		kmi.properties.name = "pie.uv_pie"

		#uv_pie
		km = wm.keyconfigs.addon.keymaps.new(name = 'Image', space_type='IMAGE_EDITOR')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'D', 'PRESS', ctrl=True)
		kmi.properties.name = "pie.uv_pie"

		#misc_pie
		km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'F', 'PRESS', ctrl=True)
		kmi.properties.name = "pie.misc_pie"

		#misc_edit_pie
		km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
		kmi = km.keymap_items.new('wm.call_menu_pie', 'F', 'PRESS', ctrl=True)
		kmi.properties.name = "pie.misc_edit_pie"


############################################
############################################
# add pie menu

		# object mode
		km = wm.keyconfigs.addon.keymaps.new(name="Object Mode")
		kmi = km.keymap_items.new("wm.call_menu_pie", "ACTIONMOUSE", "PRESS", shift=True)
		kmi.properties.name="add.menu"
		addon_keymaps.append(km)
		print(kmi.properties.name)

		#mesh edit mode
		km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
		# km = wm.keyconfigs.addon.keymaps.new(name="Mesh")
		kmi = km.keymap_items.new("wm.call_menu_pie", "ACTIONMOUSE", "PRESS", shift=True)
		kmi.properties.name="add.mesh"
		addon_keymaps.append(km)
		print(kmi.properties.name)

		#curve edit mode
		km = wm.keyconfigs.addon.keymaps.new(name="Curve")
		kmi = km.keymap_items.new("wm.call_menu_pie", "ACTIONMOUSE", "PRESS", shift=True)
		kmi.properties.name="add.curve"
		addon_keymaps.append(km)
		print(kmi.properties.name)

		#mataball edit mode
		km = wm.keyconfigs.addon.keymaps.new(name="Metaball")
		kmi = km.keymap_items.new("wm.call_menu_pie", "ACTIONMOUSE", "PRESS", shift=True)
		kmi.properties.name="add.metaball"
		addon_keymaps.append(km)

		print(kmi.properties.name)



		#Node Editor
		km = wm.keyconfigs.addon.keymaps.new(name = "Node Editor", space_type = "NODE_EDITOR")
		kmi = km.keymap_items.new("wm.call_menu_pie", "ACTIONMOUSE", "PRESS", shift=True)
		kmi.properties.name="pie.add_node"
		addon_keymaps.append(km)

		############################################
		############################################
		# UV pie select mode
		# km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
		km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
		kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS')
		kmi.properties.name = "pie.uv_select_mode"

		addon_keymaps.append(km)









# Register / Unregister Classes
def unregister():
	bpy.utils.unregister_class(w_pie_Prefs)
	bpy.utils.unregister_module(__name__)
	# bpy.app.translations.unregister(__name__)   # 辞書の削除
	bpy.app.translations.unregister(__name__)

if __name__ == "__main__":
	register()
