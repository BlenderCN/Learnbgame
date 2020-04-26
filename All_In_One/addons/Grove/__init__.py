# coding=utf-8

#  The Grove. Blender Addon to grow true to nature 3D trees.
#  Copyright 2014 - 2018, Wybren van Keulen, The Grove
#
#  ***** BEGIN GPL LICENSE BLOCK *****
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
    "name": "The Grove 6",
    "author": "Wybren van Keulen, The Grove",
    "version": (6, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh > The Grove 6",
    "description": "Grow true to nature 3D trees.",
    "warning": "",
    "wiki_url": "https://www.thegrove3d.com/learn/",
    "category": "Add Mesh"}

if "bpy" in locals():
    import importlib

    importlib.reload(Translation)
    importlib.reload(Languages)
    importlib.reload(Preferences)
    importlib.reload(Operator)
    importlib.reload(Grove)
    importlib.reload(Branch)
    importlib.reload(Node)
    importlib.reload(TwigInstance)
    importlib.reload(Presets)
    importlib.reload(Twigs)
    importlib.reload(Textures)
    importlib.reload(Utils)
else:
    from . import Preferences
    from . import Operator

import bpy
from os.path import join, dirname

icons = None
language = 'English'


def add_operator_to_mesh_menu(self, context):
    self.layout.operator(Operator.TheGrove6.bl_idname, text="The Grove 6", icon_value=icons["IconLogo"].icon_id)


def register():
    global icons
    icons = bpy.utils.previews.new()
    icons_directory = join(dirname(__file__), "Icons")
    icons.load("IconLogo",  join(icons_directory, "IconLogo.png"),  'IMAGE')

    bpy.utils.register_class(Operator.TheGrove6)
    bpy.utils.register_class(Preferences.TheGrove6Preferences)
    bpy.context.user_preferences.addons[__package__].preferences.show_refresh_warning = False
    bpy.types.INFO_MT_mesh_add.append(add_operator_to_mesh_menu)


def unregister():
    bpy.utils.previews.remove(icons)
    bpy.utils.previews.remove(Operator.icons)

    bpy.utils.unregister_class(Operator.TheGrove6)
    bpy.utils.unregister_class(Preferences.TheGrove6Preferences)
    bpy.types.INFO_MT_mesh_add.remove(add_operator_to_mesh_menu)
