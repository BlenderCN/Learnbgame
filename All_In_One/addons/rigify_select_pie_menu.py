###########################################

# RigifyPicker Addon download Link
#
# Downloads | Salva Artero
# http://salvadorartero.com/downloads/

###########################################
#
# THIS SCRIPT IS LICENSED UNDER GPL,
# please read the license block.
#
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
	"name": "rigify select Pie menu",
	"author": "Bookyakuno",
	"version": (1, 0, 0),
	"blender": (2,77,0),
	"description": "rigify rig Quick Select. ",
	"location": "Pose mode > Ctrl + W",
	"category": "Learnbgame",
    "warning": "Use RigifyPicker Addon !!  http://salvadorartero.com/downloads/" 
    }


import bpy
from bpy.types import Menu



import bpy, os
from bpy.types import Menu, Header
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
from mathutils import *
import math



class rigify_select_Prefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    bpy.types.Scene.Enable_Tab_01 = bpy.props.BoolProperty(default=False)


    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "Enable_Tab_01", text="Info", icon="QUESTION")
        if context.scene.Enable_Tab_01:

            row = layout.row()
            layout.label(text="timeline")
            layout.label(text="RigifyPicker Addon download Link")


            row.operator("wm.url_open", text="Downloads | Salva Artero").url = "http://salvadorartero.com/downloads/"











##################
# Pie Menu Class #
##################
class rigify_select_x(Menu):
	bl_idname = "object.rigify_select"
	bl_label = "Add Modifier"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()

		#4 - LEFT
		pie.operator("operador.mano_r", text="hand.ik.R", icon='HAND')
		#6 - RIGHT
		pie.operator("operador.mano_l", text="hand.ik.L", icon='HAND')
		#2 - BOTTOM
		pie.operator("operador.torso", text="Torso", icon='MONKEY')
		#8 - TOP
		pie.operator("operador.cabeza", text="Head", icon='BLENDER')
		#7 - TOP - LEFT
		pie.operator("operador.rodilla_r", text="foot_ROOL.R", icon='CURSOR')
		#9 - TOP - RIGHT
		pie.operator("operador.rodilla_l", text="foot_ROOL.L", icon='CURSOR')
		#1 - BOTTOM - LEFT
		pie.operator("operador.pie_r", text="foot.R", icon='EXPORT')
		#3 - BOTTOM - RIGHT
		pie.operator("operador.pie_l", text="foot.L", icon='EXPORT')








############
# Register #
############
addon_keymaps = []
def register():
	bpy.utils.register_class(rigify_select_x)


	### Keymap ###
	wm = bpy.context.window_manager

	km = wm.keyconfigs.addon.keymaps.new(name="Pose")
	kmi = km.keymap_items.new("wm.call_menu_pie", "W", "PRESS", ctrl=True)
	kmi.properties.name="object.rigify_select"
	addon_keymaps.append(km)


##############
# Unregister #
##############
def unregister():
	bpy.utils.unregister_class(rigify_select_x)

	### Keymap ###
	for km in addon_keymaps:
		for kmi in km.keymap_items:
			km.keymap_items.remove(kmi)

	wm.keyconfigs.addon.keymaps.remove(km)

	# clear the list
	del addon_keymaps[:]


if __name__ == "__main__":
	register()

	#bpy.ops.wm.call_menu_pie(name="object.rigify_select")
