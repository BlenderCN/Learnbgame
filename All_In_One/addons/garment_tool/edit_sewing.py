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

import bgl
import blf
import bpy
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader

from .utils.fsm_oper import ModalCommon, CookieCutter_FSM
from .utils.helper_functions import draw_text_line


class GTOOL_OT_EditSewings(bpy.types.Operator, ModalCommon, CookieCutter_FSM):
    """Modal object selection with a ray cast"""
    bl_idname = "cloth.raycast_edit_sewing"
    bl_label = "Edit Sewings"
    bl_description = "Edit Sewings"
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty(default=0)
    sewing_index: bpy.props.IntProperty(default=0)
    edit_patter_sewing: bpy.props.IntProperty(default=-1)  # if bigger than one edit only selected pattern sewing

    closest_segment_id = -1  # if -1 -> we do not have the sewing segment id yet

    @staticmethod
    def draw_text(self, context):
        sewing_count = len(self.garment.garment_sewings)
        draw_text_lines = []
        if self._state == 'pick_target_pattern':
            draw_text_lines.append(["Select target pattern - LMB", 'H1'])

        if self._state == 'main':
            draw_text_lines.append(["Select source pattern - LMB", 'H1'])
            draw_text_lines.append(["Change sewing - MMB Scroll", 'p'])
            draw_text_lines.append(["(A)dd / (R)remove - sewing", 'p]'])
            draw_text_lines.append(["Finish - Enter / Spacebar", 'p]'])

            if self.sewing_index >= 0:
                current_sewing = self.garment.garment_sewings[self.sewing_index] if sewing_count != 0 else None
                if current_sewing and current_sewing.source_obj and current_sewing.target_obj:
                    #draw segment proportions forward to it
                    region = context.region
                    rv3d = context.region_data

                    position1 = view3d_utils.location_3d_to_region_2d(
                        region, rv3d, self.patter_segments_cache[current_sewing.source_obj.name][current_sewing.segment_id_from][3])
                    position2 = view3d_utils.location_3d_to_region_2d(
                        region, rv3d, self.patter_segments_cache[current_sewing.target_obj.name][current_sewing.segment_id_to][3])
                    seg_len1 = self.patter_segments_cache[current_sewing.source_obj.name+'_len'][current_sewing.segment_id_from]
                    seg_len2 = self.patter_segments_cache[current_sewing.target_obj.name+'_len'][current_sewing.segment_id_to]

                    blf.size(0, 20, 60)
                    blf.position(0, position1[0], position1[1], 0)
                    blf.draw(0, str(round(seg_len1/seg_len2, 2)))

                    blf.position(0, position2[0], position2[1], 0)
                    blf.draw(0, str(round(seg_len2/seg_len1, 2)))

        if self._state in ['pick_target_segment', 'pick_source_segment']:
            draw_text_lines.append(["LMB - pick segment...", 'H1'])
        if self._state == 'pick_target_segment':
            draw_text_lines.append(["MMB Scroll  - flip sewing", 'p'])

        draw_text_lines.append(["Editing sewing: " + str(self.sewing_index+1) + "/" + str(sewing_count), 'p'])
        draw_text_line(draw_text_lines)


    @staticmethod
    def draw_px(self, context):
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glPointSize(8)
        bgl.glLineWidth(2.0)

        shader = self.shader
        if self.sewing_index >=0: #if we are negative, we are not editing sewing.
            current_sewing = self.garment.garment_sewings[self.sewing_index] if self.sewing_index >= 0 else None
            if self._state in ['pick_target_segment', 'pick_source_segment'] and current_sewing:  # hover highlight
                pattern_obj_name = current_sewing.source_obj.name if self._state == 'pick_source_segment' else current_sewing.target_obj.name
                segments = self.patter_segments_cache[pattern_obj_name]
                points = None
                for seg_id, segment in enumerate(segments):
                    if self.closest_segment_id == seg_id:
                        points = [(point[0], point[1], point[2]) for point in segment]
                        break
                if points:
                    batch = batch_for_shader(shader, "POINTS", {"pos": points})
                    shader.bind()
                    shader.uniform_float("color", (0.2, 0.9, 0.2, 0.5))
                    batch.draw(shader)

            if self._state in ['pick_target_pattern'] and current_sewing:  # higligh source segment, when defining target
                segments = self.patter_segments_cache[current_sewing.source_obj.name]
                segment = segments[current_sewing.segment_id_from]
                points = [(point[0], point[1], point[2]) for point in segment]
                if points:
                    batch = batch_for_shader(shader, "POINTS", {"pos": points})
                    shader.bind()
                    shader.uniform_float("color", (0.2, 0.9, 0.2, 0.5))
                    batch.draw(shader)

        points = []
        # drawing  sewing
        for i, sewing in enumerate(self.garment.garment_sewings):
            # self.closest_segment_id<0: #skip sewing if we are defining sewing_to
            if self.sewing_index == i and self._state in ['pick_source_segment', 'pick_target_pattern']:
                continue

            if sewing.source_obj is not None and sewing.target_obj is not None:
                if sewing.source_obj.name not in self.patter_segments_cache.keys() or sewing.target_obj.name not in self.patter_segments_cache:
                    continue
                vert_stich_01_list = self.patter_segments_cache[sewing.source_obj.name]
                vert_stich_02_list = self.patter_segments_cache[sewing.target_obj.name]

                if sewing.segment_id_from >= len(vert_stich_01_list):
                    sewing.segment_id_from = 0
                if sewing.segment_id_to >= len(vert_stich_02_list):
                    sewing.segment_id_to = 0

                verts_form = vert_stich_01_list[sewing.segment_id_from]
                if self.sewing_index == i and self.closest_segment_id >= 0:
                    verts_to = vert_stich_02_list[self.closest_segment_id]
                else:
                    verts_to = vert_stich_02_list[sewing.segment_id_to]
            else:
                continue

            if sewing.flip:
                verts_to = list(reversed(verts_to))

            points = []
            for (point_from, point_to) in zip(verts_form, verts_to):
                points.extend([(point_from.x, point_from.y, point_from.z), (point_to.x, point_to.y, point_to.z)])
            batch = batch_for_shader(shader, 'LINES', {"pos": points})
            shader.bind()
            if self.sewing_index == i:  # draw currently defined sewing
                shader.uniform_float("color", (0.2, 0.9, 0.2, 0.5))
            else:
                shader.uniform_float("color", (1.0, 0.8, 0.0, 0.5))
            batch.draw(shader)
        # batch = shader.new_batch('LINES', {"pos": points})

        #restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glPointSize(1)
        bgl.glDisable(bgl.GL_BLEND)

    def get_visible_sewing(self):
        return [idx for idx, sewing in enumerate( self.garment.garment_sewings) if sewing.source_obj in self.context.visible_objects and sewing.target_obj in self.context.visible_objects]

    def get_pattern_sewing(self):
        pattern_obj = self.garment.sewing_patterns[self.edit_patter_sewing].pattern_obj
        return [idx for idx, sewing in enumerate(self.garment.garment_sewings) if pattern_obj == sewing.source_obj or pattern_obj == sewing.target_obj]

    def next_sewing(self, forward = True):
        sewing_count = len(self.garment.garment_sewings)
        visible_sewing_ids = self.get_visible_sewing()
        visible_sewing_count = len(visible_sewing_ids)
        if sewing_count == 0 or visible_sewing_count == 0:
            self.sewing_index = -1
            return
        
        if visible_sewing_count == 1:
            self.sewing_index = visible_sewing_ids[0]
            return

        one = 1 if forward else -1
        if self.edit_patter_sewing >= 0:  # if bigger than -1 edit only selected pattern sewinge. Called from operator props
            pattern_sewing_ids = self.get_pattern_sewing()
            visible_and_pattern_ids = sorted(list(set(pattern_sewing_ids).intersection(visible_sewing_ids)))
            if visible_and_pattern_ids:
                current_sewing_idx = visible_and_pattern_ids.index(self.sewing_index)
                
                self.sewing_index = visible_and_pattern_ids[(current_sewing_idx + one) % len(visible_and_pattern_ids)]
                return
            else:
                self.sewing_index = -1
                return 
            return
        #use sewing from visible objs
        current_sewing_idx = visible_sewing_ids.index(self.sewing_index)
        self.sewing_index = visible_sewing_ids[(current_sewing_idx + one) % visible_sewing_count]

    def get_last_sewing(self):
        sewing_count = len(self.garment.garment_sewings)
        visible_sewing_ids = self.get_visible_sewing()
        visible_sewing_count = len(visible_sewing_ids)
        if sewing_count == 0 or visible_sewing_count == 0:
            self.sewing_index = -1
            return

        if visible_sewing_count == 1:
            self.sewing_index = visible_sewing_ids[0]
            return

        if self.edit_patter_sewing >= 0:  # if bigger than -1 edit only selected pattern sewinge. Called from operator props
            pattern_sewing_ids = self.get_pattern_sewing()
            visible_and_pattern_ids = sorted(list(set(pattern_sewing_ids).intersection(visible_sewing_ids)))
            if visible_and_pattern_ids:
                self.sewing_index = visible_and_pattern_ids[-1]
                return
            else:
                self.sewing_index = -1
                return 
            return
        self.sewing_index = visible_sewing_ids[-1]



    def find_closes_sewing(self, context, event, curve_name):
        ''' Return index of sewing closest to mouse'''
        region = context.region
        rv3d = context.region_data
        segments = self.patter_segments_cache[curve_name]
        segments_points_count = 0
        for segment in segments:
            segments_points_count += len(segment)

        kd = mathutils.kdtree.KDTree(segments_points_count)
        for seg_id, segment in enumerate(segments):
            for point in segment:
                point_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, point, default=None)
                kd.insert(Vector((point_2d[0], point_2d[1], 0)), seg_id)
        kd.balance()
        # Find the closest point to the center
        co, index, dist = kd.find(Vector((event.mouse_region_x, event.mouse_region_y, 0)))
        return index


    @CookieCutter_FSM.FSM_State('main')
    def modal_main(self):
        sewing_count = len(self.garment.garment_sewings)
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            if curve_obj is not None:
                curve_obj.select_set(True)
                if self.sewing_index == -1:
                    self.garment.garment_sewings.add()
                    self.sewing_index = len(self.garment.garment_sewings)-1
                self.garment.garment_sewings[self.sewing_index].source_obj = curve_obj
                self.assign_target_obj_to_garment(curve_obj)
                return 'pick_source_segment'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return  # stay in same state

        elif self.event.type == 'A' and self.event.value == 'PRESS':
            self.garment.garment_sewings.add()
            self.sewing_index = len(self.garment.garment_sewings)-1

        elif self.event.type == 'R' and self.event.value == 'PRESS':
            if self.sewing_index != -1:  #if we have any sewing selected
                curretn_sewing_id = self.sewing_index
                self.next_sewing(False) #get prev_sewing
                self.garment.garment_sewings.remove(curretn_sewing_id)
                if curretn_sewing_id == self.sewing_index: #if prevous sewing is same as current, then wa are removing last visible sewing. 
                    self.sewing_index = -1  # so set current to -1
                elif self.sewing_index > len(self.garment.garment_sewings)-1: #cos when getting previous we got prevous element.id > len(sewings)
                    self.get_last_sewing()

        #change sewing ++ id when not in edith sewing mode
        elif self.event.type == 'WHEELUPMOUSE':
            self.next_sewing()

        #change sewing -- id when not in edith sewing mode
        elif self.event.type == 'WHEELDOWNMOUSE':
            self.next_sewing(False)

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.end_cancel()
            return

        elif (self.event.type == 'RET' or self.event.type == 'SPACE') and self.event.value == 'PRESS':
            self.end_commit()
            return
            
    # finish pin_from/pin_to and close
    @CookieCutter_FSM.FSM_State('pick_source_segment')
    def pick_source_segment(self):
        # finish sewing_from/sewing_to and close
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':  
            # draw the points and pick
            if self.closest_segment_id >= 0:
                current_sewing = self.garment.garment_sewings[self.sewing_index]
                current_sewing.segment_id_from = self.closest_segment_id
                self.closest_segment_id = -1
                return 'pick_target_pattern'
            else:
                return #stay in the same state
        
        elif self.event.type == 'MOUSEMOVE':
            current_sewing = self.garment.garment_sewings[self.sewing_index]
            self.closest_segment_id = self.find_closes_sewing(self.context, self.event, current_sewing.source_obj.name)
            # return {'PASS_THROUGH'}

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_sewing()
            return 'main'


    # finish pin_from/pin_to and close
    @CookieCutter_FSM.FSM_State('pick_target_pattern')
    def pick_target_pattern(self):
        #finish picking curve pattern for sewing source/target
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            if curve_obj is not None:
                curve_obj.select_set(True)
                current_sewing = self.garment.garment_sewings[self.sewing_index]
                current_sewing.target_obj = curve_obj
                self.assign_target_obj_to_garment(curve_obj)
                return 'pick_target_segment'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return #stay in same state

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_sewing()
            return 'main'


    @CookieCutter_FSM.FSM_State('pick_target_segment')
    def pick_target_segment(self):
        current_sewing = self.garment.garment_sewings[self.sewing_index]
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            # draw the points and pick
            if self.closest_segment_id >= 0:
                current_sewing.segment_id_to = self.closest_segment_id
                self.closest_segment_id = -1
                return 'main'
            else:
                self.report({'INFO'}, 'No close sewing. Click Again')
                return  # stay in the same state

        elif self.event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            current_sewing.flip = not current_sewing.flip

        elif self.event.type == 'MOUSEMOVE':
            self.closest_segment_id = self.find_closes_sewing(self.context, self.event, current_sewing.target_obj.name)
            # return {'PASS_THROUGH'}

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.cancel_current_sewing()
            return 'main'


    #cancall currently edited sewing
    def cancel_current_sewing(self):
        current_sewing = self.garment.garment_sewings[self.sewing_index]
        current_sewing.target_obj = None
        current_sewing.source_obj = None
        self.closest_segment_id = -1
        print('undo sewing')

  
    def before_start(self):
        sewing_count = len(self.garment.garment_sewings)
        visible_sewing_ids = self.get_visible_sewing()
        visible_sewing_count = len(visible_sewing_ids)
        #init sewing_index from visible_sewing, or pattern and visible_sewing
        if sewing_count == 0 or visible_sewing_count == 0:
            self.sewing_index = -1
            return

        if visible_sewing_count == 1:
            self.sewing_index = visible_sewing_ids[0]
            return

        if self.edit_patter_sewing >= 0:  # if bigger than -1 edit only selected pattern sewinge. Called from operator props
            pattern_sewing_ids = self.get_pattern_sewing()
            visible_and_pattern_ids = sorted(list(set(pattern_sewing_ids).intersection(visible_sewing_ids)))
            if visible_and_pattern_ids:
                self.sewing_index = visible_and_pattern_ids[0]
                return
            else: # no pattern sewing to edit, or it is not visible...
                self.sewing_index = -1
                self.report({'WARNING'}, "You have tried to edit sewing for invisible pattern. Cancelling!")
                self.end_cancel()
                return
            return
        else:
            self.sewing_index = visible_sewing_ids[0]

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
