'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

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

import bpy
import bmesh
import mathutils
import random
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np
from .utils.helper_functions import draw_text_line
from .utils.fsm_oper import ModalCommon, CookieCutter_FSM
from mathutils.bvhtree import BVHTree
from mathutils import Matrix, Vector
from bpy_extras import view3d_utils
from mathutils.geometry import intersect_line_sphere


class GTOOL_OT_RayCastEditPins(bpy.types.Operator, ModalCommon, CookieCutter_FSM):
    """Modal object selection with a ray cast"""
    bl_idname = "cloth.raycast_edit_pins"
    bl_label = "Edit Pins"
    bl_description = "Edit garment Pins by selecting 2D curve object and \nthen selecting point on curve. Repeat to define target pin"
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty(default=0)
    pin_idx: bpy.props.IntProperty(default=0)

    current_pin_pos = None  # if None -> we do not have the pin pos yet

    @staticmethod
    def draw_text(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        draw_text_lines = []
        if self._state == 'main':
            draw_text_lines.append(["Select source pattern - LMB", 'H1'])
            draw_text_lines.append(["Change Pin ID - MMB Scroll", 'p'])
            draw_text_lines.append(["(A)dd / (R)remove Pin", 'p'])
            draw_text_lines.append(["Confirm - Enter", 'p'])
        if self._state == 'pick_target_obj':
                draw_text_lines.append(["Select target pattern - LMB", 'H1'])
        if self._state in ('pick_source_pin_pos', 'pick_target_pin_pos'):
            draw_text_lines.append(["Pick point on surface - LMB", 'H1'])

        draw_text_lines.append(["Editing pin ID: " + str(self.pin_index+1) + "/" + str(len(garment.pins)), 'p'])
        draw_text_line(draw_text_lines)


    @staticmethod
    def draw_px(self, context):
        shader = self.shader
        garment = context.scene.cloth_garment_data[self.garment_index]
        if len(garment.pins) == 0:
            return
        current_pin = garment.pins[self.pin_index]

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glPointSize(12)
        bgl.glLineWidth(2.0)

        if self._state in ['pick_target_pin_pos', 'pick_source_pin_pos'] and self.current_pin_pos:
            pin_pos = None
            if self._state == 'pick_source_pin_pos' and current_pin.source_obj:
                pin_pos = current_pin.source_obj.matrix_world @ Vector(self.current_pin_pos)
            elif current_pin.target_obj:
                pin_pos = current_pin.target_obj.matrix_world @ Vector(self.current_pin_pos)
            if pin_pos:
                batch = batch_for_shader(shader, "POINTS", {"pos": [pin_pos[:]]})
                shader.bind()
                shader.uniform_float("color", (0.2, 0.9, 0.2, 0.5))
                batch.draw(shader)

        points = []
        # drawing all pins
        for i, pin in enumerate(garment.pins):
            #skip drawing if we are editing pin pin_idx
            if i == self.pin_index and self._state in ['pick_source_pin_pos', 'pick_target_obj']:
                continue
            if pin.source_obj and pin.target_obj:
                if pin.source_obj.name not in self.patter_segments_cache.keys() or pin.target_obj.name not in self.patter_segments_cache:
                    continue

                verts_form = pin.source_obj.matrix_world @ Vector(pin.source_co)
                if self.pin_index == i and self.current_pin_pos != None:
                    verts_to = pin.source_obj.matrix_world @ Vector(
                        self.current_pin_pos) if self._state == 'pick_source_pin_pos' else pin.target_obj.matrix_world @ Vector(self.current_pin_pos)
                else:
                    verts_to = pin.target_obj.matrix_world @ Vector(pin.target_co)
            else:
                continue

            points = [verts_form[:], verts_to[:]]
            shader.bind()
            batch = batch_for_shader(shader, 'LINES', {"pos": points})
            if self.pin_index == i:  # draw currently defined pin
                shader.uniform_float("color", (0.2, 0.9, 0.2, 0.5))
            else:
                shader.uniform_float("color", (1.0, 0.8, 0.0, 0.5))
            batch.draw(shader)
        # batch = shader.new_batch('LINES', {"pos": points})

        #restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glPointSize(1)
        bgl.glDisable(bgl.GL_BLEND)
        # bgl.glDisable(bgl.GL_LINE_STIPPLE)

    def get_visible_pins(self):
        return [idx for idx, pin in enumerate(self.garment.pins) if pin.source_obj in self.context.visible_objects and pin.target_obj in self.context.visible_objects]

    def next_pin(self, forward=True, get_last = False):
        visible_pins_ids = self.get_visible_pins()
        visible_pins_count = len(visible_pins_ids)
        if visible_pins_count == 0:
            self.pin_index = -1
            return

        if visible_pins_count == 1:
            self.pin_index = visible_pins_ids[0]
            return

        if get_last:
            self.pin_index = visible_pins_ids[-1]
            return
        one = 1 if forward else -1
        current_sewing_idx = visible_pins_ids.index(self.pin_index)
        self.pin_index = visible_pins_ids[(current_sewing_idx + one) % visible_pins_count]
        


    @CookieCutter_FSM.FSM_State('main')
    def modal_main(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            if curve_obj is not None:
                curve_obj.select_set(True)
                if self.pin_index == -1:
                    self.garment.pins.add()
                    self.pin_index = len(self.garment.pins) - 1
                self.garment.pins[self.pin_index].source_obj = curve_obj
                self.assign_target_obj_to_garment(curve_obj)
                return 'pick_source_pin_pos'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return  # stay in this state

        elif self.event.type == 'A' and self.event.value == 'PRESS':
            self.garment.pins.add()
            self.pin_index = len(self.garment.pins) - 1
            return #stay in same state

        elif self.event.type == 'R' and self.event.value == 'PRESS':
            if self.pin_index != -1:
                curretn_pin_id = self.pin_index
                self.next_pin(False)  # get prev_pin
                self.garment.pins.remove(curretn_pin_id)
                if curretn_pin_id == self.pin_index:  # if prevous pin is same as current, then wa are removing last visible pin.
                    self.pin_index = -1  # so set current to -1
                # cos when getting previous we got prevous element.id > len(sewings)
                elif self.pin_index > len(self.garment.pins)-1:
                    self.next_pin(get_last=True)

        #change pin ++ id when not in edith pin mode
        elif self.event.type == 'WHEELUPMOUSE':
            self.next_pin()

        #change pin -- id when not in edith pin mode
        elif self.event.type == 'WHEELDOWNMOUSE':
            self.next_pin(False)

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True
        
        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.end_cancel()
            return
        elif (self.event.type == 'RET' or self.event.type == 'SPACE') and self.event.value == 'PRESS':
            self.end_commit()
            return


    # finish pin_from/pin_to and close
    @CookieCutter_FSM.FSM_State('pick_source_pin_pos')
    def pick_source_pin_pos(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            # draw the points and pick
            if self.current_pin_pos != None:
                self.garment.pins[self.pin_index].source_co = self.current_pin_pos
            self.current_pin_pos = None
            return 'pick_target_obj'

        elif self.event.type == 'MOUSEMOVE':
            mouse_hit_pos = self.hit_obj_pos(self.context, self.garment.pins[self.pin_index].source_obj)
            self.current_pin_pos = self.current_pin_pos if mouse_hit_pos is None else mouse_hit_pos
            # return {'PASS_THROUGH'}
        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True
        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_pin()
            return 'main'


    # finish pin_from/pin_to and close
    @CookieCutter_FSM.FSM_State('pick_target_obj')
    def pick_target_obj(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            if curve_obj is not None:
                curve_obj.select_set(True)
                self.garment.pins[self.pin_index].target_obj = curve_obj
                self.assign_target_obj_to_garment(curve_obj)
                return 'pick_target_pin_pos'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return  # stay in this state

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True
        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_pin()
            return 'main'


    # finish pin_from/pin_to and close
    @CookieCutter_FSM.FSM_State('pick_target_pin_pos')
    def pick_target_pin_pos(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            # draw the points and pick
            if self.current_pin_pos != None:
                self.garment.pins[self.pin_index].target_co = self.current_pin_pos

            self.current_pin_pos = None
            return 'main'

        elif self.event.type == 'MOUSEMOVE':
            mouse_hit_pos = self.hit_obj_pos(self.context,  self.garment.pins[self.pin_index].target_obj)
            self.current_pin_pos = self.current_pin_pos if mouse_hit_pos is None else mouse_hit_pos
            # return {'PASS_THROUGH'}
        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True
        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_pin()
            return 'main'

    def cancel_current_pin(self):  # disable enable sewing, cycle through them
        self.garment.pins[self.pin_index].target_obj = None
        self.garment.pins[self.pin_index].source_obj = None
        self.current_pin_pos = None

    def before_start(self):
        visible_pins_ids = self.get_visible_pins()
        visible_pins_count = len(visible_pins_ids)
        if visible_pins_count == 0:
            self.pin_index = -1
        else:
            self.pin_index = visible_pins_ids[0]


    def modal(self, context, event):
        self.context = context
        self.event = event
        context.area.tag_redraw()

        if self.done:
            return {self.done}

        self.fsm_update()
        if self.allow_nav:
            self.allow_nav = False
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            self.invoke_common(context, event)
            self.fsm_init()
            self.before_start()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}


