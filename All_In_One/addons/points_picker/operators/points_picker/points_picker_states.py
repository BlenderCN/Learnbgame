# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
from mathutils import Vector

# Addon imports
from ...addon_common.cookiecutter.cookiecutter import CookieCutter
from ...functions.common import tag_redraw_areas


class PointsPicker_States():

    #############################################
    # State keymap

    default_keymap = {
        "add":    {"LEFTMOUSE"},
        "grab":   {"LEFTMOUSE"},
        "remove": {"ALT+LEFTMOUSE"},
        "commit": {"RET"},
        "cancel": {"ESC"},
    }

    #############################################
    # State functions

    @CookieCutter.FSM_State("main")
    def modal_main(self):
        # update hovered point
        if self.actions.mousemove or self.actions.navigating():
            x, y = self.event.mouse_region_x, self.event.mouse_region_y
            self.hover(bpy.context, x, y)
        self.cursor_modal_set("HAND" if self.hovered[0] == "POINT" and not self.event.alt else "CROSSHAIR")

        # actions for no hovered point
        if self.hovered[0] is None:
            if self.actions.pressed("add"):
                x, y = self.event.mouse_region_x, self.event.mouse_region_y
                if not self.add_point_pre(Vector((x, y))): return "main"
                self.click_add_point(bpy.context, x, y)
                self.add_point_post(self.b_pts[self.hovered[1]])
                # update hovered point
                x, y = self.event.mouse_region_x, self.event.mouse_region_y
                self.hover(bpy.context, x, y)
                self.cursor_modal_set("HAND")
                return "grab"
        # actions for hovered point
        else:
            if self.actions.pressed("remove"):
                self.click_remove_point()
                return "main"
            if self.actions.pressed("grab"):
                return "grab"

        # other actions
        if self.actions.pressed("commit") and self.can_commit():
            self.done();
            return
        if self.actions.pressed("cancel") and self.can_cancel():
            self.done(cancel=True)
            return

    @CookieCutter.FSM_State("grab", "can enter")
    def can_start_grab(self):
        return self.hovered[0] == "POINT"

    @CookieCutter.FSM_State("grab", "enter")
    def start_grab(self):
        self.selected = self.hovered[1]
        self.grab_undo_loc = self.b_pts[self.selected].location
        self.grab_undo_mp = self.b_pts[self.selected].surface_normal

    @CookieCutter.FSM_State("grab")
    def modal_grab(self):
        if self.actions.released("grab"):
            self.grab_undo_loc = None
            return "main"

        if self.actions.mousemove:
            x, y = self.event.mouse_region_x, self.event.mouse_region_y
            self.grab_mouse_move(bpy.context, x, y)

    @CookieCutter.FSM_State("grab", "exit")
    def exit_grab(self):
        self.move_point_post(self.b_pts[self.hovered[1]])
