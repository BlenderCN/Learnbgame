"""
.. module:: Switches to the screen layout of the given name
   :platform: OS X, Windows, Linux
   :synopsis: —

.. moduleauthor:: Original code by Blitzen


"""
# ##### BEGIN GPL LICENSE BLOCK #####
#
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
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Screen Switcher",
	"description": "Switches to the screen layout of the given name",
	"location": "User Preferences>Input>Screen>",
	"author": "Rombout Versluijs / kilbeeu",
	"version": (0, 3, 3),
	"blender": (2, 7, 8),
	"warning": "",
	"category": "Learnbgame"
}


import bpy
import rna_keymap_ui


def avail_screens(self,context):
	'''
	enumerates available screen layouts and adding more items:
	Maximize Area - will toggle current area to maximum window size
	User Preferences - opens User Preferences window
	'''
	screen = bpy.data.screens
	screens = [ ("User Preferences", "User Preferences", "User Preferences")
				] # (identifier, name, description) optionally: (.., icon name, unique number)

	for screen in bpy.data.screens:
		screens.append((screen.name, screen.name, screen.name))
	return screens

addon_keymaps = [] # store hotkey items on addon level for quick referencel todo: actually move this to addon preferences to keep it clean


def get_hotkey_entry_item(km, kmi_name, kmi_value):
	'''
	returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
	if there are multiple hotkeys!)
	'''
	for i, km_item in enumerate(km.keymap_items):
		if km.keymap_items.keys()[i] == kmi_name:
			try:
				if km.keymap_items[i].properties.name == kmi_value:
					return km_item
			except:
				pass
			try:
				if km.keymap_items[i].properties.layoutName == kmi_value:
					return km_item
			except:
				pass
	return None # not needed, since no return means None, but keeping for readability


def add_hotkey():
	user_preferences = bpy.context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	wm = bpy.context.window_manager

	kc = wm.keyconfigs.addon    # for hotkeys within an addon
	km = kc.keymaps.new(name = "Screen", space_type = "EMPTY")
	hKeys = [("NUMPAD_1"), ("NUMPAD_2"), ("NUMPAD_3"), ("NUMPAD_4"),("NUMPAD_5"),("NUMPAD_6"),("NUMPAD_7"), ("NUMPAD_8")]
	i=0
	for screen in hKeys:
		kmi = km.keymap_items.new("screen.set_layout", hKeys[i], "PRESS", oskey=True)  # ...and if not found then add it
		kmi.properties.layoutName = "ScreenSwitcher"+str(i)  # also set proper name
		kmi.active = True
		addon_keymaps.append((km, kmi)) # also append to global (addon level) hotkey list for easy management
		i+=1
	#Add quick menu
	kmi = km.keymap_items.new("wm.call_menu", "NONE", "PRESS")
	kmi.properties.name = "screen.switch_menu"
	kmi.active = True
	addon_keymaps.append((km, kmi))


class QuickSwitchMeny(bpy.types.Menu):
	bl_label = "Quick Switch Menu"
	bl_idname = "screen.switch_menu"


	def draw(self, context):
		layout = self.layout

		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[0][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[0][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[1][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[1][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[2][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[2][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[3][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[3][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[4][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[4][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[5][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[5][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[6][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[6][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[7][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[7][1]
		layout.operator("screen.set_layout", text='{}'.format(avail_screens(self, context)[8][1]), icon='SPLITSCREEN').layoutItems1=avail_screens(self, context)[8][1]

		layout.separator()


class SetScreenLayout(bpy.types.Operator):
	"""Switches to the screen layout of the given name."""
	bl_idname="screen.set_layout"
	bl_label="Switch to Screen Layout"

	layoutItems1 = bpy.props.EnumProperty(name = "Screen Layout", items = avail_screens)
	layoutName = bpy.props.StringProperty()

	def execute(self,context):
		if self.layoutItems1 == "User Preferences":
			bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
			#bpy.context.user_preferences.active_section = 'ADDONS'
			return{'FINISHED'}
		else:
			try:
				bpy.context.window.screen=bpy.data.screens[self.layoutItems1]
				return{'FINISHED'}
			except:
				# except layout doesn't exists
				self.report({'INFO'}, 'Screen layout [{}] doesn\'t exist! Create it or pick another in addon settings.'.format(self.layoutName))

	def invoke(self,context,event):
		return self.execute(context)


#-- ADDON PREFS --#
class VIEW3D_ScreenSwitcher(bpy.types.AddonPreferences):
	""" Preference Settings Addon Panel"""
	bl_idname = __name__

	def draw(self, context):
		layout = self.layout
		col = layout.column()

		col.label('Hotkeys:')
		col.label('Do NOT remove hotkeys, disable them instead!')

		box=layout.box()
		split = box.split()
		col = split.column()

		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user
		km = kc.keymaps['Screen']

		col.label('Screen Layouts:')
		for i in range(0,8):
#			if km.keymap_items.keys()[i] == 'Switch to Screen Layout':
			kmi = get_hotkey_entry_item(km, "screen.set_layout", "ScreenSwitcher"+str(i))
			if kmi:
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
			else:
				col.label("restore hotkeys from interface tab")
		col.label('Set each shortcut in the dropdown menu named "Screen Layout"')

		box=layout.box()
		split = box.split()
		col = split.column()
		kmi = get_hotkey_entry_item(km, "wm.call_menu", "screen.switch_menu")
		if kmi:
			col.label('Quick Switch Menu:')
			col.context_pointer_set("keymap", km)
			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
		else:
			col.label("restore hotkeys from interface tab")




### Register #####################################################################
def register():
	bpy.utils.register_module(__name__)

	# hotkey setup
	add_hotkey()


def unregister():
	# hotkey cleanup
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
