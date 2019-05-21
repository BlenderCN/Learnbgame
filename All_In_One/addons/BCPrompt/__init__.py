# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Console Prompt",
    "author": "Dealga McArdle",
    "version": (0, 1, 3),
    "blender": (2, 80, 0),
    "location": "Console - keystrokes",
    "description": "Adds feature to intercept console input and parse accordingly.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
    }

if 'bpy' in globals():

    msg = ": detected reload event! cool."
    if 'bc_utils' in globals():
        bc_utils.print_addon_msg(__package__, msg)
    else:
        print(__package__ + msg)

    if 'bc_operators' in globals():
        import importlib as imp
        imp.reload(bc_operators)
        imp.reload(bc_panels)
        imp.reload(bc_utils)
        imp.reload(bc_search_utils)
        imp.reload(bc_gist_utils)
        imp.reload(bc_scene_utils)
        imp.reload(bc_update_utils)
        imp.reload(bc_CAD_utils)
        imp.reload(bc_TEXT_utils)
        imp.reload(bc_theme_utils)
        imp.reload(bc_text_repr_utils)
        imp.reload(bc_package_manager)
        imp.reload(bc_command_dispatch)
        imp.reload(sub_util)
        imp.reload(fast_ops.curve_handle_equalizer)
        imp.reload(fast_ops.curve_nurbs_to_polyline)
        imp.reload(keymaps.console_keymaps)

        from .bc_utils import print_addon_msg
        print_addon_msg(__package__, ': reloaded')


else:
    from . import bc_operators
    from . import bc_panels
    from . import bc_TEXT_utils
    from .fast_ops import curve_handle_equalizer
    from .fast_ops import curve_nurbs_to_polyline
    from .keymaps import console_keymaps

import bpy


def menu_func(self, context):
    self.layout.operator("curve.curve_handle_eq")
    self.layout.operator("curve.nurbs_to_polyline")


def text_toolblock_func(self, context):
    self.layout.separator()
    self.layout.operator("text.duplicate_textblock", text="Duplicate TextBlock")


def console_buttons_func(self, context):
    self.layout.operator('wm.set_editmode_shortcuts', text='123')
    row = self.layout.row()
    row.alert = True
    row.operator("script.reload", text="Refresh Python")

# this files have ops that need registration
module_files = [bc_operators, bc_panels, bc_TEXT_utils]


def register():
    for module in module_files:
        module.register()

    bpy.types.VIEW3D_MT_edit_curve_context_menu.append(menu_func)
    bpy.types.CONSOLE_HT_header.append(console_buttons_func)
    bpy.types.TEXT_MT_toolbox.prepend(text_toolblock_func)
    console_keymaps.add_keymap(__package__)


def unregister():
    console_keymaps.remove_keymap()

    bpy.types.VIEW3D_MT_edit_curve_context_menu.remove(menu_func)
    bpy.types.CONSOLE_HT_header.remove(console_buttons_func)
    bpy.types.TEXT_MT_toolbox.remove(text_toolblock_func)
    for module in module_files[::-1]:
        module.unregister()    
