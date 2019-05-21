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
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
from bpy.props import BoolProperty, IntProperty
from .ribbons_operations import CurvesUVRefresh
import time
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

import bgl
import blf

def draw_callback_px(self, context, hair_uv_points):
    # print("mouse points", len(self.mouse_pos))

    font_id = 0
    region = context.region
    # x, y = region.view2d.region_to_view(self.mouse_pos[0], self.mouse_pos[1]) # vies space to UV (0,1 space)
    # x, y = self.mouse_pos[0], self.mouse_pos[1] # vies space to UV (0,1 space)
    # blf.size(font_id, 20, 72)
    # blf.position(font_id, 15, 80 , 0)
    # blf.draw(font_id, "X" + str(x))
    # blf.position(font_id, 15, 50, 0)
    # blf.draw(font_id, "Y" + str(y))
    # bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    # blf.size(font_id, 16, 62)
    # blf.position(font_id, 15, 30, 0)

    fontBottomMargin = 160
    if self.mouse_pos[1] >35 or self.mouse_pos[0] > 110:
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        blf.size(font_id, 16, 60)
        blf.position(font_id, 15, 15, 0)
        blf.draw(font_id, "[Hair uv help]")
    else:
        # draw box
        x0 = 0
        y0 = 0
        x1 = 330
        y1 = fontBottomMargin
        positions = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(bgl.GL_QUADS)
        bgl.glColor4f(0, 0, 0, 0.3)
        for v1, v2 in positions:
            bgl.glVertex2f(v1, v2)
        bgl.glEnd()

        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        blf.size(font_id, 16, 60)
        blf.position(font_id, 15, 135, 0)
        blf.draw(font_id, "Draw rectangular shape with LMB")
        blf.position(font_id, 15, 120, 0)
        blf.draw(font_id, "Click and drag corner points to adjust box size ")
        blf.position(font_id, 15, 95, 0)
        blf.draw(font_id, "ENTER - confirm ")
        blf.position(font_id, 15, 75, 0)
        blf.draw(font_id, "DELETE - delete box")
        blf.position(font_id, 15, 55, 0)
        blf.draw(font_id, "SHIFT+DELETE - rest uv")
        blf.position(font_id, 15, 35, 0)
        blf.draw(font_id, "CTRL+Mouse Wheel - change seed ")
        blf.position(font_id, 15, 15, 0)
        blf.draw(font_id, "ESC / RMB - cancel")
    # 50% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.2, 1.0, 0.0, 0.5)
    bgl.glLineWidth(2)
    # bgl.glBegin(bgl.GL_LINE_STRIP)
    # for x, y in self.mouse_pos:
    #     bgl.glVertex2i(x, y)
    #
    # edgesUV =[[0.1,0.1]]
    drawMouse = self.LMB_Clicked
    if len(hair_uv_points)>0:
        bgl.glColor4f(0.8, 0.8, 0.8, 0.7)
        region = context.region
        if drawMouse: #draw not edited uv boxes
            if self.edit_point_index == -1: #draw all exept new one
                pointsToDraw = hair_uv_points[:-1]
            else:
                pointsToDraw = hair_uv_points[:]
                pointsToDraw.pop(self.edit_point_index)
        else:  #draw all uv boxes
            pointsToDraw = hair_uv_points[:]
        for uv_point in pointsToDraw: #draw non edited boxes
            x1, y1 = region.view2d.view_to_region(uv_point.start_point[0], uv_point.start_point[1],clip = False) # vies space to UV (0,1 space)
            x2, y2 = region.view2d.view_to_region(uv_point.end_point[0], uv_point.end_point[1],clip = False) # vies space to UV (0,1 space)
            # x1  = max(min(x1,region.width-1),1)
            # y1  = max(min(y1,region.height-1),1)
            # x2 = max(min(x2, region.width-1), 1)
            # y2 = max(min(y2, region.height-1), 1)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2i(x1, y1)
            bgl.glVertex2i(x1, y2)
            bgl.glVertex2i(x2, y2)
            bgl.glVertex2i(x2, y1)
            bgl.glVertex2i(x1, y1)

            bgl.glEnd()

            bgl.glPointSize(6)
            bgl.glBegin(bgl.GL_POINTS)
            bgl.glVertex2f(x1, y1)
            bgl.glVertex2f(x2, y2)
            bgl.glEnd()

    if drawMouse:  #draw currently edited box
        if self.edit_point_index == -1:
            start_point = self.mouse_start
            end_point = self.mouse_pos
        else:
            box = hair_uv_points[self.edit_point_index]
            if self.edit_start_point:
                start_point = self.mouse_pos
                x2, y2 = region.view2d.view_to_region(box.end_point[0], box.end_point[1],clip = False)
                end_point = [x2, y2]
            if self.edit_end_point:
                x1, y1 = region.view2d.view_to_region(box.start_point[0], box.start_point[1],clip = False) # vies space to UV (0,1 space)
                start_point = [x1,y1]
                end_point = self.mouse_pos
        bgl.glColor4f(0.4, 1.0, 0.2, 1)
        bgl.glBegin(bgl.GL_LINE_STRIP)

        bgl.glVertex2i(start_point[0], start_point[1])
        bgl.glVertex2i(start_point[0], end_point[1])
        bgl.glVertex2i(end_point[0], end_point[1])
        bgl.glVertex2i(end_point[0], start_point[1])
        bgl.glVertex2i(start_point[0], start_point[1])

        bgl.glEnd()

        bgl.glPointSize(10)
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex2f(start_point[0], start_point[1])
        bgl.glVertex2f(end_point[0], end_point[1])
        bgl.glEnd()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class ModalUvRangeSelect(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "uv.hair_uv_area_select"
    bl_label = "Draw uv area for Hair"
    bl_description = "Draw box in UV editor to define hair ribbons uv's"
    bl_options = {"REGISTER", "UNDO"}

    Seed = IntProperty(name="Noise Seed", default=20, min=1, max=1000)
    _handle = None
    UVBackup= []
    uv_seedBackup = 1

    selfDrawMouse = False  #true when drawing new uv box
    edit_end_point = False #true when updating existing uv box
    edit_start_point = False #true when updating existing uv box
    edit_point_index  = -1  #if not editing any points then -1

    mouse_pos = []  #we need it to pass as self.mouse_pos to draw handler
    # def poll(self, context):
    #     return context.active_object.type == "MESH"

    def manualUndo(self,curveHairRibbon):
        curveHairRibbon.hair_settings.hair_uv_points.clear()
        for points in self.UVBackup:
            curveHairRibbon.hair_settings.hair_uv_points.add()
            for p in points.keys():  # copy start and end point
                curveHairRibbon["hair_settings"]["hair_uv_points"][-1][p] = points[p]
                curveHairRibbon.hair_settings.uv_seed = self.uv_seedBackup
                CurvesUVRefresh.uvCurveRefresh(curveHairRibbon)

    def save_xy_to_uv_box(self,uvHairPoints,boxIndex,x,y):
        if self.edit_start_point == False:  #if editing end point - or normally placing second uv box point
            if x > uvHairPoints[boxIndex].start_point[0]:  # make sure (x,y) is on bottom right position if not fix it
                uvHairPoints[boxIndex].end_point[0] = x
            else:
                uvHairPoints[boxIndex].end_point[0] = uvHairPoints[boxIndex].start_point[0]
                uvHairPoints[boxIndex].start_point[0] = x
            if y < uvHairPoints[boxIndex].start_point[1]:
                uvHairPoints[boxIndex].end_point[1] = y
            else:
                uvHairPoints[boxIndex].end_point[1] = uvHairPoints[boxIndex].start_point[1]
                uvHairPoints[boxIndex].start_point[1] = y
        else:  #if first point is being edited
            if x < uvHairPoints[boxIndex].end_point[0]:  # make sure (x,y) is on bottom right position if not fix it
                uvHairPoints[boxIndex].start_point[0] = x
            else:
                uvHairPoints[boxIndex].start_point[0] = uvHairPoints[boxIndex].end_point[0]
                uvHairPoints[boxIndex].end_point[0] = x
            if y > uvHairPoints[boxIndex].end_point[1]:
                uvHairPoints[boxIndex].start_point[1] = y
            else:
                uvHairPoints[boxIndex].start_point[1] = uvHairPoints[boxIndex].end_point[1]
                uvHairPoints[boxIndex].end_point[1] = y

    def modal(self, context, event):
        context.area.tag_redraw()
        region = context.region
        curveHairRibbon = context.active_object
        uvHairPoints = curveHairRibbon.hair_settings.hair_uv_points
        curveHairRibbon.hair_settings.uv_seed = self.Seed
        if event.type == 'MOUSEMOVE':
            self.mouse_pos = [event.mouse_region_x, event.mouse_region_y]

        elif event.type == 'LEFTMOUSE' and self.LMB_Clicked == True and self.edit_point_index == -1:  # finish drawing box, and calculate uv Transformation
            x, y = region.view2d.region_to_view(self.mouse_pos[0], self.mouse_pos[1])  # vies space to UV (0,1 space)
            self.save_xy_to_uv_box(uvHairPoints,-1,x,y)
            self.LMB_Clicked = False
            CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)

        elif event.type == 'LEFTMOUSE' and self.LMB_Clicked == True and self.edit_point_index != -1:
            x, y = region.view2d.region_to_view(self.mouse_pos[0], self.mouse_pos[1])  # vies space to UV (0,1 space)
            self.save_xy_to_uv_box(uvHairPoints,self.edit_point_index,x,y)
            self.edit_end_point = False
            self.edit_start_point = False
            self.edit_point_index = -1
            self.LMB_Clicked = False
            CurvesUVRefresh.uvCurveRefresh(curveHairRibbon, self.Seed)

        elif event.type == 'LEFTMOUSE' and self.LMB_Clicked == False:
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self.mouse_start = [event.mouse_region_x, event.mouse_region_y]
            x, y = region.view2d.region_to_view(self.mouse_pos[0], self.mouse_pos[1])  # vies space to UV (0,1 space)

            if len(uvHairPoints)==1 and uvHairPoints[0].start_point[0] == 0 and uvHairPoints[0].start_point[1] == 1: #delete default uv
                uvHairPoints.clear()
            delta = 0.03
            for point_index,points in enumerate(uvHairPoints):
                if x-delta < points.start_point[0] < x + delta and  y-delta < points.start_point[1] < y + delta:
                    self.edit_start_point = True
                    self.edit_point_index = point_index
                    print("editing point!")
                    break
                if x-delta < points.end_point[0] < x + delta and  y-delta < points.end_point[1] < y + delta:
                    self.edit_end_point = True
                    self.edit_point_index = point_index
                    print("editing point!")
                    break

            if self.edit_point_index == -1: #if not edtiting points then start new uv box
                uvHairPoints.add()
                uvHairPoints[-1].start_point = [x, y]
            self.LMB_Clicked = True

        elif event.ctrl and event.type == 'Z' and event.value == 'PRESS':
            if len(uvHairPoints)>1:
                uvHairPoints.remove(len(uvHairPoints)-1)
                CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)

        elif event.type == 'WHEELUPMOUSE' and event.ctrl:
            self.Seed += 1
            curveHairRibbon.hair_settings.uv_seed = self.Seed
            CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)

        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl:
            self.Seed -= 1
            curveHairRibbon.hair_settings.uv_seed = self.Seed
            CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)

        elif event.type == 'DEL' and  event.shift == False: #delete box/boxes
            x, y = region.view2d.region_to_view(self.mouse_pos[0], self.mouse_pos[1])  # vies space to UV (0,1 space)
            if len(uvHairPoints) > 0:
                for i,hair_uv_point in enumerate(uvHairPoints):
                    startX,startY = hair_uv_point.start_point
                    endX,endY = hair_uv_point.end_point
                    if startX < x < endX and endY < y < startY:
                        uvHairPoints.remove(i)
                        force_uv_reset = True if len(uvHairPoints) == 0 else False
                        CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)
                        break
        elif event.type == 'DEL' and event.shift:
            print("Shift deletion")
            if len(uvHairPoints)>0:
                uvHairPoints.clear()
                CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed, force_uv_reset = True)
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self._handle:
                bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
            self.manualUndo( curveHairRibbon)
            self.report({'INFO'}, 'CANCELLED')
            return {'CANCELLED'}

        elif event.type in {'NUMPAD_ENTER', 'RET'} and time.time()-self.startTime>1:
            if self._handle:
                bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')

            context.scene.last_hair_settings.hair_uv_points.clear()
            for uvPoint in uvHairPoints:
                context.scene.last_hair_settings.hair_uv_points.add()
                context.scene.last_hair_settings.hair_uv_points[-1].start_point = uvPoint.start_point
                context.scene.last_hair_settings.hair_uv_points[-1].end_point = uvPoint.end_point
                # ipdb.set_trace()
            CurvesUVRefresh.uvCurveRefresh(curveHairRibbon,self.Seed)
            self.report({'INFO'}, 'Finished')
            return {'FINISHED'}

        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.startTime=time.time()
        curveHairRibbon = context.active_object
        if curveHairRibbon.type != 'CURVE':
            self.report({'WARNING'}, "Operator works only on curve ribbons! Cancelling")
            return {'CANCELLED'}
            # mesheHair = bpy.data.objects[curveHairRibbon.hair_settings.hair_curve_child]
        if context.area.type == 'IMAGE_EDITOR':
            # the arguments we pass the the callback
            # manual undo begin backup
            self.UVBackup.clear()
            self.edit_point_index == -1
            self.uv_seedBackup = curveHairRibbon.hair_settings.uv_seed
            for point in curveHairRibbon.hair_settings.hair_uv_points:
                self.UVBackup.append({'start_point':[point.start_point[0],point.start_point[1]],
                                      'end_point':[point.end_point[0],point.end_point[1]]})
            # curveHairRibbon.hair_settings.hair_uv_points.clear()
            self.LMB_Clicked = False
            args = (self, context, curveHairRibbon.hair_settings.hair_uv_points)
            self._handle = bpy.types.SpaceImageEditor.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            self.mouse_pos = []
            self.report({'INFO'}, 'Draw box shape in UV editor')
            self.Seed = curveHairRibbon.hair_settings.uv_seed
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "You must run this operator in UV editor! Cancelling")
            return {'CANCELLED'}