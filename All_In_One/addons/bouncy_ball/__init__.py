# ------------------------------------------------------------------------------
# LICENSE
#
# (c) Copyright Diego Gangl (januz) - 2017
# <diego@sinestesia.co>
#
# This addon is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------

import os
import pkgutil
import importlib
import math

from time import time
import numpy as np


bl_info = {
    "name": "Bouncy Ball",
    "description": "Yup, just a ball that bounces around",
    "author": "Diego Gangl <diego@sinestesia.co>",
    "version": (1, 0, 0),
    "BLENDER": (2, 70, 0),
    "location": "3D View",
    "warning": "",
    "link": "",
    "tracker_url": "",
    "category": "3D View"
}


# ------------------------------------------------------------------------------
# Package Setup
# ------------------------------------------------------------------------------
def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path=path[0], root=""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else:
                module_names.append(root + module_name)
        return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            if name == 'batch_render.dispatcher':
                continue

            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)

    names = get_submodule_names()
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return modules


modules = setup_addon_modules(__path__, __name__, "bpy" in locals())

import bpy
from bpy.props import (FloatProperty, FloatVectorProperty, PointerProperty)
from . import ball


# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------

class Bouncy_PROP_Main(bpy.types.PropertyGroup):

    gravity = FloatProperty(name='Gravity',
                            description='Gravity',
                            default=50,
                            min=10,
                            max=100,
                            precision=1,
                            subtype='PERCENTAGE')

    bounciness = FloatProperty(name='Bounciness',
                               description='Restituion coefficient',
                               default=90,
                               min=0,
                               max=100,
                               precision=1,
                               subtype='PERCENTAGE')

    radius = FloatProperty(name='Radius',
                           description='Size of the ball',
                           default=50,
                           min=10,
                           max=100,
                           precision=1)

    color = FloatVectorProperty(name='Color',
                                description='Ball Color',
                                min=0,
                                max=1,
                                default=(1, 0.55, 0.06),
                                subtype='COLOR')


# ------------------------------------------------------------------------------
# Operator
# ------------------------------------------------------------------------------

add_handler = bpy.types.SpaceView3D.draw_handler_add
remove_handler = bpy.types.SpaceView3D.draw_handler_remove
add_timer = bpy.context.window_manager.event_timer_add
remove_timer = bpy.context.window_manager.event_timer_remove


class BouncyBall(bpy.types.Operator):
    """Create a ball that bounces around the 3D View"""

    bl_idname = "view3d.bouncy_ball"
    bl_label = "Bouncy Ball"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):

        context.area.tag_redraw()
        message = '{0} bounces so far | Press ESC to stop bouncing'
        context.area.header_text_set(message.format(self.args['state'].bounces))

        if event.type == 'TIMER' and not self.drag:
            self.args['state'] = self._move(self.args['state'])

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            click = np.array((event.mouse_region_x, event.mouse_region_y))
            distance = np.linalg.norm(click - self.args['state'].position)

            if distance <= self.args['settings'].radius:
                context.window.cursor_set('HAND')
                self.args['ever_dragged'] = True

                origin = (event.mouse_region_x, event.mouse_region_y)

                self.drag, self.release = ball.drag_start(self.args['settings'],
                                                          self.args['state'],
                                                          origin)

        elif (event.type == 'LEFTMOUSE' and event.value == 'RELEASE' 
              and self.drag):

            context.window.cursor_set('DEFAULT')
            self._dragging = False

            position = np.array((event.mouse_region_x, event.mouse_region_y))
            velocity = self.release(position)

            self.args['state'] = self._move(self.args['state'], velocity)
            self.drag = None
            self.release = None

        elif event.type == 'MOUSEMOVE' and self.drag:
            self.args['state'] = self.drag(event)

        elif event.type == 'ESC':
            remove_handler(self._handle, 'WINDOW')
            remove_timer(self._timer)
            context.area.header_text_set()

            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        center = np.array((context.area.width / 2, context.area.height / 2))
        ui_settings = context.window_manager.bouncy
        settings = ball.Settings(ui_settings.radius,
                                 np.array(ui_settings.color),
                                 ui_settings.gravity / 25,
                                 ui_settings.bounciness / 100)

        self.args = {
                        'settings': settings,
                        'ever_dragged': False,
                        'state': ball.State(position=center,
                                            velocity=np.zeros(2),
                                            bounces=0)
                    }

        self.drag = None
        self.release = None

        self._move = ball.physics_setup(settings)
        self._timer = add_timer(1/60, context.window)
        self._handle = add_handler(ball.callback, (self.args,), 
                                   'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# ------------------------------------------------------------------------------
# UI
# ------------------------------------------------------------------------------

class Bouncy_Panel(bpy.types.Panel):
    bl_idname = "bouncy.panel"
    bl_label = "Bouncy Ball"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = 'Tools'

    def draw(self, context):
        """ Draw terrain Panel """

        layout = self.layout
        settings = context.window_manager.bouncy

        col = layout.column(align=True)
        col.prop(settings, 'bounciness')
        col.prop(settings, 'gravity')

        row = layout.row()
        row.prop(settings, 'color')

        row = layout.row()
        row.prop(settings, 'radius')

        layout.separator()
        layout.separator()

        row = layout.row()
        row.scale_y = 1.2
        row.operator('view3d.bouncy_ball', text='Bounce!', icon='MOD_PHYSICS')


# ------------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.bouncy = PointerProperty(type=Bouncy_PROP_Main)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.WindowManager.bouncy 


if __name__ == "__main__":
    register()
