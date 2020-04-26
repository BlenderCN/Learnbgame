'''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

# addon info
bl_info = {
    'name': 'Selected Bounds',
    'author': 'Trentin Frederick (proxe)',
    'version': (0, '7a', 48),
    'blender': (2, 78, 0),
    'location': '3D View \N{Rightwards Arrow} Properties Shelf \N{Rightwards Arrow} Display',
    'description': 'Display bound box indicators around selected objects.',
    # 'wiki_url': '',
    # 'tracker_url': '',
    "category": "Learnbgame",
}

# imports
import bpy
from bpy.app.handlers import persistent
from bpy.utils import register_module, unregister_module
from bpy.props import PointerProperty, BoolProperty

from .addon import interface, operator, preferences, properties
from .addon.config import defaults as default


@persistent
def load_handler(self):

    if bpy.context.user_preferences.addons[__name__].preferences.scene_independent:

        update_settings()

    bpy.ops.view3d.selected_bounds('EXEC_DEFAULT')


def update_settings():

    preference = bpy.context.user_preferences.addons[__name__].preferences

    for scene in bpy.data.scenes:

        options = scene.selected_bounds

        for option in default:

            if option not in {'selected_bounds', 'scene_independent', 'display_preferences', 'mode_only'}:
                if option != 'color':
                    if getattr(options, option) == default[option]:

                        setattr(options, option, getattr(preference, option))

                elif options.color[:] == default[option]:

                    options.color = preference.color


def register():

    register_module(__name__)

    bpy.types.Scene.selected_bounds = PointerProperty(
        type = properties.selected_bounds,
        name = 'Selected Bounds',
        description = 'Storage location for selected bounds settings.'
    )

    bpy.types.WindowManager.is_selected_bounds_drawn = BoolProperty(
        name = 'Selected Bounds Checker',
        description = 'Used by the addon selected bounds to prevent multiple draw handlers from being created.',
        default = False
    )

    bpy.types.WindowManager.selected_bounds = BoolProperty(
        name = 'Selected Bounds',
        description = 'Display bound indicators around objects.',
        default = default['selected_bounds']
    )

    bpy.types.VIEW3D_PT_view3d_display.prepend(interface.draw)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():

    unregister_module(__name__)

    bpy.types.VIEW3D_PT_view3d_display.remove(interface.draw)
    bpy.app.handlers.load_post.remove(load_handler)

    del bpy.types.Scene.selected_bounds
    del bpy.types.WindowManager.is_selected_bounds_drawn
    del bpy.types.WindowManager.selected_bounds
