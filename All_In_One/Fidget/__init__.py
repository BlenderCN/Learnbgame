'''
Copyright (C) 2015 masterxeon1001
masterxeon1001@gmail.com

Created by masterxeon1001 and team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Fidget",
    "description": "Touchscreen Interface Prototype",
    "author": "MX, AR","Proxe"
    "version": (0, 0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    # "warning": ",
    "wiki_url": "none",
    "category": "Learnbgame",
}

import bpy
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
from . nodes.nodes import nodes_register, nodes_unregister
from . keymap import register_keymap, unregister_keymap
# from . registration import register_all, unregister_all


def draw_header(cls, context):
    if "Fidget" in context.user_preferences.addons:
        cls.layout.operator("wm.addon_disable", text="Disable Fidget", icon="CHECKBOX_HLT", emboss=False).module = "Fidget"
        if context.space_data.tree_type == "FidgetNodeTree":
            op = cls.layout.operator("fidget.update", text="Update All Outputs")
            op.write = True
            op.update_all_outputs = True
            cls.layout.operator("fidget.save_startup", text="Save Tree as Startup")
            cls.layout.operator("fidget.load_startup", text="Reload Saved Load Tree")
    else:
        cls.layout.operator("wm.addon_enable", text="Enable Fidget", icon="CHECKBOX_DEHLT", emboss=False).module = "Fidget"


bpy.types.NODE_HT_header.append(draw_header)


def register():
    bpy.utils.register_module(__name__)
    nodes_register()
    register_keymap()
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))


def unregister():
    bpy.utils.unregister_module(__name__)
    nodes_unregister()
    unregister_keymap()
    print("Unregistered {}".format(bl_info["name"]))
