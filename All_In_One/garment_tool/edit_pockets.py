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
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .utils.fsm_oper import ModalCommon, CookieCutter_FSM
from .utils.helper_functions import draw_text_line


class GTOOL_OT_RayCastEditPockets(bpy.types.Operator, ModalCommon, CookieCutter_FSM):
    """Modal object selection with a ray cast"""
    bl_idname = "garment.raycast_edit_pocket"
    bl_label = "Edit Pocket"
    bl_description = "Edit garment Pockets"
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()
    pocket_index: bpy.props.IntProperty(default=0)

    pocket_sewing_index = 1
    # patter_segments_cache = {}  # store curve patter borders resampled

    def draw_text(self, cla, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        pockets_count = len(garment.pockets)
        draw_text_lines = []
        # draw_text_lines.append(["State: "+self._state,'H1'])
        if self._state == 'main':
            draw_text_lines.append(["Select pocket object - LMB", 'H1'])
            draw_text_lines.append(["change pocket -MMB Scroll", 'p'])
            draw_text_lines.append(["(A)dd / (R)remove - Pocket", 'p'])
            draw_text_lines.append(["Edit Pocket sewing - Spacebar", 'p'])
            draw_text_lines.append(["Confirm - Enter", 'p'])

        if self._state == 'pick_pocket_target':
            draw_text_lines.append([" Select target obj - LMB", 'H1'])
            draw_text_lines.append(["Cancel pocket - ESC/RMB", 'p'])

        if self._state == 'manage_pocket_sewing':
            draw_text_lines.append(["forward sewing - MMB Scroll", 'p'])
            draw_text_lines.append(["Enable/Disable sewing - Shift + MMB", 'p'])
            draw_text_lines.append(["Cancel pocket - ESC/RMB", 'p'])
            draw_text_lines.append(["Confirm - Enter / Spacebar", 'p'])
            # draw_text_lines.append(["Editing sewing: " + str(self.pocket_sewing_index+1) + "/" + str(len(self.patter_segments_cache[self.pocket_obj _name])), 'p'])
        draw_text_lines.append(["Editing Pocket: " + str(self.pocket_index+1) + "/" + str(pockets_count), 'p'])
        draw_text_line(draw_text_lines)


    def draw_px(self, cla, context):
        if len(self.garment.pockets) == 0 or self.pocket_index == -1:
            return
        current_pocket = self.garment.pockets[self.pocket_index]

        if self._state in ['main', 'manage_pocket_sewing']:  # hover highlight
            if current_pocket.pocketObj and current_pocket.target_pattern:
                shader=self.shader
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glPointSize(6)
                bgl.glLineWidth(2.0)

                draw_points = []
                pocket_segments = self.patter_segments_cache[current_pocket.pocketObj.name]
                pocket_active_sewing = [int(x) for x in current_pocket.pocket_sewing]
                target_segments = self.patter_segments_cache[current_pocket.pocketObj.name+'target']
                for i, (source, target) in enumerate(zip(pocket_segments, target_segments)):
                    if i in pocket_active_sewing:
                        for (point_from, point_to) in zip(source, target):
                            draw_points.extend([(point_from.x, point_from.y, point_from.z), (point_to.x, point_to.y, point_to.z)])

                batch = batch_for_shader(shader, 'LINES', {"pos": draw_points})
                shader.bind()  # draw currently defined sewing
                shader.uniform_float("color", (0.2, 0.9, 0.2, 0.8))
                batch.draw(shader)

                batch = batch_for_shader(shader, "POINTS", {"pos": draw_points})
                shader.bind()
                shader.uniform_float("color", (0.2, 0.9, 0.2, 0.8))
                batch.draw(shader)
                if self._state == 'manage_pocket_sewing':
                    active_segment = []
                    for seg_id, segment in enumerate(pocket_segments):
                        if self.pocket_sewing_index == seg_id:
                            active_segment.extend([(point[0], point[1], point[2]) for point in segment])

                    batch = batch_for_shader(shader, "POINTS", {"pos": active_segment})
                    shader.bind()
                    shader.uniform_float("color", (1, 1, 1, 0.8))
                    batch.draw(shader)

                #restore opengl defaults
                bgl.glLineWidth(1)
                bgl.glPointSize(1)
                bgl.glDisable(bgl.GL_BLEND)

    def get_visible_pockets(self):
        return [idx for idx, pocket in enumerate(self.garment.pockets) if pocket.pocketObj in self.context.visible_objects and pocket.target_pattern in self.context.visible_objects]

    def next_pocket(self, forward=True, get_last = False):
        visible_pockets_ids = self.get_visible_pockets()
        visible_pockets_count = len(visible_pockets_ids)
        if visible_pockets_count == 0:
            self.pocket_index = -1
            return

        if visible_pockets_count == 1:
            self.pocket_index = visible_pockets_ids[0]
            return

        if get_last:
            self.pocket_index = visible_pockets_ids[-1]
            return
        one = 1 if forward else -1
        #use sewing from visible objs
        current_sewing_idx = visible_pockets_ids.index(self.pocket_index)
        self.pocket_index = visible_pockets_ids[(current_sewing_idx + one) % visible_pockets_count]



    def cache_target_points(self, pocket_index):
        current_pocket = self.garment.pockets[pocket_index]
        if current_pocket.target_pattern and current_pocket.pocketObj:
            #get verts from pockets
            target_mat_inv = current_pocket.target_pattern.matrix_world.inverted()
            self.patter_segments_cache[current_pocket.pocketObj.name+'target'] = [] #cos we store projected points for pocket_obj
            for segment_points in self.patter_segments_cache[current_pocket.pocketObj.name]:
                #if current sewing and prevous are neibors then skip first vert\
                target_verts_co = [target_mat_inv@ point for point in segment_points]  # points in cache are already in world space m_w @ p.co
                flat_projected_points = [current_pocket.target_pattern.matrix_world@Vector((p.x, p.y, 0)) for p in target_verts_co]
                self.patter_segments_cache[current_pocket.pocketObj.name+'target'].append(flat_projected_points)


    @CookieCutter_FSM.FSM_State('main')
    def modal_main(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            if curve_obj is not None:
                bpy.ops.object.select_all(action='DESELECT')
                curve_obj.select_set(True)
                if self.pocket_index == -1:
                    self.garment.pockets.add()
                    self.pocket_index = len(self.garment.pockets) - 1
                self.garment.pockets[self.pocket_index].pocketObj = curve_obj
                enabled_sewing = [str(i) for i in range(len(curve_obj.data.splines[0].bezier_points))]
                current_pocket = self.garment.pockets[self.pocket_index]
                current_pocket.pocket_sewing = set(enabled_sewing)
                return 'pick_pocket_target'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return # stay in this state

        elif self.event.type == 'SPACE' and self.event.value == 'PRESS':
            return 'manage_pocket_sewing'
        
        elif self.event.type == 'WHEELUPMOUSE':
            self.next_pocket()

        elif self.event.type == 'WHEELDOWNMOUSE':
            self.next_pocket(False)
                
        elif self.event.type == 'A' and self.event.value == 'PRESS':
            self.garment.pockets.add()
            self.pocket_index = len(self.garment.pockets) - 1

        elif self.event.type == 'R' and self.event.value == 'PRESS':
            if self.pocket_index != -1:  # do not allow to delete last sewing  so len(sewing) >= 2
                curretn_pocket_id = self.pocket_index
                self.next_pocket(False)  # get prev_pocket
                self.garment.pockets.remove(curretn_pocket_id)
                if curretn_pocket_id == self.pocket_index:  # if prevous pocket is same as current, then wa are removing last visible pocket.
                    self.pocket_index = -1  # so set current to -1
                elif self.pocket_index > len(self.garment.pockets)-1:
                    self.next_pocket(get_last=True)
                bpy.ops.object.select_all(action='DESELECT')
                if self.pocket_index != -1:
                    current_pocket = self.garment.pockets[self.pocket_index]
                    if current_pocket.pocketObj:
                        current_pocket.pocketObj.select_set(True)

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            self.end_cancel()
            return
        
        elif self.event.type == 'RET' and self.event.value == 'PRESS':
            self.end_commit()
            return 'main'

        
    @CookieCutter_FSM.FSM_State('pick_pocket_target')
    def pick_pocket_target(self):
        if self.event.type == 'LEFTMOUSE' and self.event.value == 'PRESS':
            curve_obj = self.find_curve_under_cursor(self.context, self.event)
            current_pocket = self.garment.pockets[self.pocket_index]
            if curve_obj is not None:
                if curve_obj.name == current_pocket.pocketObj.name:
                    self.report({'INFO'}, 'Target Cant be the same as pocket object. Click Again')
                    return  # stay in this state
                curve_obj.select_set(True)
                current_pocket.target_pattern = curve_obj
                self.assign_target_obj_to_garment(curve_obj)
                self.cache_target_points(self.pocket_index)
                return 'manage_pocket_sewing'
            else:
                self.report({'INFO'}, 'No close pattern detected. Click Again')
                return  # stay in this state

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            pockets_count = len(self.garment.pockets)
            if pockets_count > 1:  # do not allow to delete last sewing  so len(sewing) >= 2
                self.garment.pockets.remove(self.pocket_index)
                self.pocket_index = (self.pocket_index-1) % (pockets_count-1)
            return 'main'



    @CookieCutter_FSM.FSM_State('manage_pocket_sewing')
    def manage_pocket_sewing(self): #disable enable sewing, cycle through them
        current_pocket = self.garment.pockets[self.pocket_index]
        pocket_sewing_count = len(self.patter_segments_cache[current_pocket.pocketObj.name]) if current_pocket is not None else 0

        if self.event.type == 'WHEELUPMOUSE' and self.event.shift and self.event.value == 'PRESS':
            if str(self.pocket_sewing_index) in current_pocket.pocket_sewing:
                current_pocket.pocket_sewing = current_pocket.pocket_sewing.difference(str(self.pocket_sewing_index))
            else:
                current_pocket.pocket_sewing = current_pocket.pocket_sewing.union(str(self.pocket_sewing_index))

        if self.event.type == 'WHEELUPMOUSE' and not self.event.shift and pocket_sewing_count > 1:
            self.pocket_sewing_index = (self.pocket_sewing_index + 1) % pocket_sewing_count

        elif self.event.type == 'WHEELDOWNMOUSE' and not self.event.shift and pocket_sewing_count > 1:
            self.pocket_sewing_index = (self.pocket_sewing_index - 1) % pocket_sewing_count

        elif self.event.type == 'MIDDLEMOUSE':
            self.allow_nav = True

        elif self.event.type in {'RIGHTMOUSE', 'ESC'} and self.event.value == 'PRESS':
            pockets_count = len(self.garment.pockets)
            if pockets_count > 1:  # do not allow to delete last sewing  so len(sewing) >= 2
                self.garment.pockets.remove(self.pocket_index)
                self.pocket_index = (self.pocket_index-1) % (pockets_count-1)
            return 'main'

        elif (self.event.type == 'RET' or self.event.type == 'SPACE') and self.event.value == 'PRESS':
            # self.end_commit()
            return 'main'



    def before_start(self):
        visible_pockets_ids = self.get_visible_pockets()
        visible_pockets_count = len(visible_pockets_ids)
        if visible_pockets_count == 0:
            self.pocket_index = -1
        else:
            self.pocket_index = visible_pockets_ids[0]

        if self.pocket_index != -1:
            current_pocket = self.garment.pockets[self.pocket_index]
            if current_pocket.pocketObj:
                bpy.ops.object.select_all(action='DESELECT')
                current_pocket.pocketObj.select_set(True)

        for pocket_id in visible_pockets_ids:
            pocket = self.garment.pockets[pocket_id]
            if pocket.pocketObj and pocket.target_pattern:
                self.cache_target_points(pocket_id)


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
