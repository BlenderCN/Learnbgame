'''
Created on Oct 8, 2015

@author: Patrick
'''

import math
import bgl

from bpy_extras import view3d_utils
from mathutils import Vector, Matrix, Color

from .. import common_drawing
from ..cookiecutter.cookiecutter import CookieCutter
from ..common.shaders import circleShader

from .polytrim_datastructure import InputPoint, CurveNode, SplineSegment


# some useful colors
clear       = (0.0, 0.0, 0.0, 0.0)
red         = (1.0, 0.1, 0.1, 1.0)
orange      = (1.0, 0.8, 0.2, 1.0)
orange2     = (1.0, 0.65, 0.2, 1.0)
yellow      = (1.0, 1.0, 0.1, 1.0)
green       = (0.3, 1.0, 0.3, 1.0)
green_trans = (0.3, 1.0, 0.3, 0.5)
green2      = (0.2, 0.5, 0.2, 1.0)
cyan        = (0.0, 1.0, 1.0, 1.0)
blue        = (0.1, 0.1, 0.8, 1.0)
blue_trans  = (0.0, 0.0, 1.0, 0.2)
blue2       = (0.1, 0.2, 1.0, 0.8)
navy_trans  = (0.0, 0.2, 0.2, 0.5)
purple      = (0.8, 0.1, 0.8, 1.0)
pink        = (1.0, 0.8, 0.8, 1.0)

preview_line_clr = (0.0, 1.0, 0.0, 0.4)
preview_line_wdth = 2


def set_depthrange(near, far, points, view_loc, view_ortho):
    d2 = min((view_loc-p).length_squared for p in points)
    d = math.sqrt(d2)
    d2 /= 10.0
    near = near / d2
    far = 1.0 - ((1.0 - far) / d2)
    if view_ortho:
        far *= 0.9999
    near = max(0.0, min(1.0, near))
    far = max(near, min(1.0, far))
    bgl.glDepthRange(near, far)
    #bgl.glDepthRange(0.0, 0.5)

# draws points
def draw3d_points(points, color, size, view_loc, view_ortho, zfar=0.997):
    if not points: return
    bgl.glColor4f(*color)
    bgl.glPointSize(size)
    set_depthrange(0.0, zfar, points, view_loc, view_ortho)
    bgl.glBegin(bgl.GL_POINTS)
    for coord in points: bgl.glVertex3f(*coord)
    bgl.glEnd()
    bgl.glPointSize(1.0)

# draws polylines.
def draw3d_polyline(points, color, thickness, view_loc, view_ortho, stipple=False, zfar=0.997):
    if not points: return
    if stipple:
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    set_depthrange(0.0, zfar, points, view_loc, view_ortho)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points: bgl.glVertex3f(*coord)
    bgl.glEnd()
    bgl.glLineWidth(1)
    if stipple:
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterrupted lines

def draw2d_polyline(points, color, thickness, stipple=False):
    if stipple:
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points: bgl.glVertex2f(*coord)
    bgl.glEnd()
    bgl.glLineWidth(1)
    if stipple:
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines




class Polytrim_UI_Draw():
    @CookieCutter.Draw('post3d')
    def draw_postview(self):

        self.draw_3D_stuff()

        # skip the rest of the drawing if user is navigating or doing stuff with ui
        if self._nav or self._ui: return

        if self.net_ui_context.hovered_near[0] in {'NON_MAN_ED', 'NON_MAN_VERT'}:
            # draw non-manifold circle
            loc = self.net_ui_context.hovered_near[1][1]
            self.draw_circle(loc, 10, .7, green_trans, clear)

        #INSERT POINT HINT
        if self.net_ui_context.hovered_near[0] in {'EDGE'}:
            # draw insertion circle
            loc = self.net_ui_context.hovered_mesh['world loc']
            self.draw_circle(loc, 10, .7, green_trans, clear)
            
           
        if self.net_ui_context.hovered_near[0] in {'POINT'}:
            # draw selection circle
            loc = self.net_ui_context.hovered_near[1].world_loc
            self.draw_circle(loc, 12, .7, green_trans, clear)

        if self.net_ui_context.snap_element:
            # draw snap/sketch circle
            loc = self.net_ui_context.snap_element.world_loc
            self.draw_circle(loc, 24, .7, green_trans, clear)

        # draw region paint brush
        if self._state == 'region':
            self.brush.draw_postview(self.context, self.actions.mouse)

    @CookieCutter.Draw('post2d')
    def draw_postpixel(self):
        self.draw_2D_stuff()
        # if self.sketcher.has_locs:
        if self._state == 'spline' and self.spline_fsm.state == 'sketch':
            draw2d_polyline(self.sketcher.get_locs(), (0.0, 1.0, 0.0, 0.4), 2)


    #TODO: Clean up/ Organize this function into parts
    def draw_2D_stuff(self):
        context = self.context
        mouse_loc = self.actions.mouse
        ctrl_pressed = self.actions.ctrl
        loc3d_reg2D = view3d_utils.location_3d_to_region_2d

        if self._state == 'spline':
            ## Selected Point
            if self.net_ui_context.selected:
                if isinstance(self.net_ui_context.selected, InputPoint):
                    common_drawing.draw_3d_points(context,[self.net_ui_context.selected.world_loc], 8, orange)
                elif isinstance(self.net_ui_context.selected, CurveNode):
                    common_drawing.draw_3d_points(context,[self.net_ui_context.selected.world_loc], 8, green)

        #draw  bad segment hints
        if self.hint_bad:
            for seg in self.input_net.segments:
                if not seg.is_bad: continue
                mid = .5 * (seg.ip0.world_loc + seg.ip1.world_loc)
                common_drawing.draw_3d_points(context,[mid], 10, red)
        
        
        if self._state == 'spline' and self.net_ui_context.snap_element and self.net_ui_context.selected:
            psnap = self.net_ui_context.snap_element
            psel = self.net_ui_context.selected
            
            if psnap != psel:
                pn = psnap.world_loc
                ps = psel.world_loc
                pts_2d = [loc3d_reg2D(context.region, context.space_data.region_3d, pt_3d) for pt_3d in [pn, ps]]
                draw2d_polyline(pts_2d, preview_line_clr, preview_line_wdth)
            
            
        if self._state == 'spline' and self.net_ui_context.hovered_near[0] == 'EDGE':
            seg = self.net_ui_context.hovered_near[1]
            
            p0 = seg.n0.world_loc
            p1 = seg.n1.world_loc
            pn = self.net_ui_context.hovered_mesh['world loc']

            pts_2d = [loc3d_reg2D(context.region, context.space_data.region_3d, pt_3d) for pt_3d in [p0, pn, p1]]
            draw2d_polyline(pts_2d, preview_line_clr, preview_line_wdth)

            
            
        # skip the rest of the drawing if user is navigating or doing stuff with ui
        if self._nav or self._ui: return

        ###############
        # Draw hints

        # # Hovered Non-manifold Edge or Vert
        # if self.net_ui_context.hovered_near[0] in {'NON_MAN_ED', 'NON_MAN_VERT'}:
        #     ed, pt = self.net_ui_context.hovered_near[1]
        #     common_drawing.draw_3d_points(context,[pt], 6, green)

        # # Hovered Point
        # if self.net_ui_context.hovered_near[0] == 'POINT':
        #     common_drawing.draw_3d_points(context,[self.net_ui_context.hovered_near[1].world_loc], 8, color=(0,1,0,1))

        # # Insertion Lines (for adding in a point to edge)
        # elif self.net_ui_context.hovered_near[0] == 'EDGE':
        #     seg = self.net_ui_context.hovered_near[1]
        #     if isinstance(seg, SplineSegment):
        #         a = loc3d_reg2D(context.region, context.space_data.region_3d, seg.n0.world_loc)
        #         b = loc3d_reg2D(context.region, context.space_data.region_3d, seg.n1.world_loc)
        #     else:
        #         a = loc3d_reg2D(context.region, context.space_data.region_3d, seg.ip0.world_loc)
        #         b = loc3d_reg2D(context.region, context.space_data.region_3d, seg.ip1.world_loc)
        #     if a and b:
        #         draw2d_polyline([a, mouse_loc, b], preview_line_clr, preview_line_wdth)

        # # Insertion Lines (for adding closing loop)
        # elif self.net_ui_context.snap_element != None and self.net_ui_context.connect_element != None:
        #     a = loc3d_reg2D(context.region, context.space_data.region_3d, self.net_ui_context.connect_element.world_loc)
        #     b = loc3d_reg2D(context.region, context.space_data.region_3d, self.net_ui_context.snap_element.world_loc)
        #     if a and b:
        #         draw2d_polyline([a, b], preview_line_clr, preview_line_wdth)

        # # Insertion Line (for general adding of points)
        # elif self.net_ui_context.closest_ep and not ctrl_pressed:
        #     ep_screen_loc = loc3d_reg2D(context.region, context.space_data.region_3d, self.net_ui_context.closest_ep.world_loc)
        #     if self.net_ui_context.hovered_near[0] in {'NON_MAN_ED', 'NON_MAN_VERT'}:
        #         point_loc = loc3d_reg2D(context.region, context.space_data.region_3d, self.net_ui_context.hovered_near[1][1])
        #     else: point_loc = mouse_loc
        #     draw2d_polyline([ep_screen_loc, point_loc], preview_line_clr, preview_line_wdth)


    def draw_3D_stuff(self):
        context = self.context
        region,r3d = context.region,context.space_data.region_3d
        view_dir = r3d.view_rotation * Vector((0,0,-1))
        view_loc = r3d.view_location - view_dir * r3d.view_distance
        view_ortho = (r3d.view_perspective == 'ORTHO')
        if view_ortho: view_loc -= view_dir * 1000.0

        bgl.glEnable(bgl.GL_POINT_SMOOTH)
        bgl.glDepthRange(0.0, 1.0)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glLineWidth(1)
        bgl.glDepthRange(0.0, 1.0)

        if self._state != 'segmentation':
            #CurveNetwork, BezierSegments
            for seg in self.spline_net.segments:
                if len(seg.draw_tessellation) == 0: continue
    
                #has not been successfully converted to InputPoints and InputSegments
                if seg.is_inet_dirty:
                    draw3d_polyline(seg.draw_tessellation, orange2, 4, view_loc, view_ortho)
    
                #if len(seg.ip_tesselation):
                #    draw3d_polyline(seg.ip_tesselation,  blue, 2, view_loc, view_ortho)
                #    draw3d_points(seg.ip_tesselation, green2, 4, view_loc, view_ortho)
    
            draw3d_points(self.spline_net.point_world_locs, green2, 6, view_loc, view_ortho)
    
            # Polylines...InputSegments
            for seg in self.input_net.segments:
                #bad segment with a preview path provided by geodesic
                if seg.bad_segment and not len(seg.path) > 2:
                    draw3d_polyline([seg.ip0.world_loc, seg.ip1.world_loc], pink, 2, view_loc, view_ortho)
    
                #s
                elif len(seg.path) >= 2 and not seg.bad_segment and seg not in self.network_cutter.completed_segments:
                    draw3d_polyline(seg.path,  blue, 2, view_loc, view_ortho)
    
                elif len(seg.path) >= 2 and not seg.bad_segment and seg in self.network_cutter.completed_segments:
                    draw3d_polyline(seg.path,  green2, 2, view_loc, view_ortho)
    
                elif len(seg.path) >= 2 and seg.bad_segment:
                    draw3d_polyline(seg.path,  orange2, 2, view_loc, view_ortho)
                    draw3d_polyline([seg.ip0.world_loc, seg.ip1.world_loc], orange2, 2, view_loc, view_ortho)
    
                elif seg.calculation_complete == False:
                    draw3d_polyline([seg.ip0.world_loc, seg.ip1.world_loc], orange2, 2, view_loc, view_ortho)
                else:
                    draw3d_polyline([seg.ip0.world_loc, seg.ip1.world_loc], blue2, 2, view_loc, view_ortho)
    
    
            if self.network_cutter.the_bad_segment:
                seg = self.network_cutter.the_bad_segment
                draw3d_polyline([seg.ip0.world_loc, seg.ip1.world_loc],  red, 4, view_loc, view_ortho)


        if self._state == 'segmentation':
            #draw the hovered patch
            #TODO, segmentation only happens AFTER CUtting
            #So it would be MUCH easier to just draw the damn edges of the patch
            if self.net_ui_context.hovered_near[0] == 'PATCH':
                p = self.net_ui_context.hovered_near[1]
                if p != self.network_cutter.active_patch:
                    for spline_seg in p.spline_net_segments:
                        for iseg in spline_seg.input_segments:
                            draw3d_polyline([iseg.ip0.world_loc] + iseg.path + [iseg.ip1.world_loc],  orange2, 4, view_loc, view_ortho)
            
            if self.network_cutter.active_patch:                    
                for spline_seg in self.network_cutter.active_patch.spline_net_segments:
                    for iseg in spline_seg.input_segments:
                            draw3d_polyline([iseg.ip0.world_loc] + iseg.path + [iseg.ip1.world_loc],  orange2, 4, view_loc, view_ortho)

        if self._state == 'spline':
            draw3d_points(self.input_net.point_world_locs, blue, 2, view_loc, view_ortho)
        elif self._state != 'segmentation':
            draw3d_points(self.input_net.point_world_locs, blue, 6, view_loc, view_ortho)

        #draw the seed/face patch points
        draw3d_points([p.world_loc for p in self.network_cutter.face_patches], orange2, 6, view_loc, view_ortho)


        #draw the actively processing Input Point (IP Steper Debug) for debug stepper cutting
        if self.network_cutter.active_ip:
            draw3d_points([self.network_cutter.active_ip.world_loc], purple, 20, view_loc, view_ortho)
            draw3d_points([ip.world_loc for ip in self.network_cutter.ip_chain], purple, 12, view_loc, view_ortho)

        if self.network_cutter.seg_enter:
            draw3d_polyline(self.network_cutter.seg_enter.path, green2, 4, view_loc, view_ortho)

        if self.network_cutter.seg_exit:
            draw3d_polyline(self.network_cutter.seg_exit.path, red, 4, view_loc, view_ortho)

        bgl.glLineWidth(1)
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthRange(0.0, 1.0)
        bgl.glDepthMask(bgl.GL_TRUE)

    def draw_circle(self, world_loc, radius, inner_ratio, color_outside, color_inside):
        bgl.glDepthRange(0, 0.9999)     # squeeze depth just a bit
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glDepthMask(bgl.GL_FALSE)   # do not overwrite depth
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glDepthFunc(bgl.GL_LEQUAL)  # draw in front of geometry

        circleShader.enable()
        self.drawing.point_size(2.0 * radius)
        circleShader['uMVPMatrix'] = self.drawing.get_view_matrix_buffer()
        circleShader['uInOut']     = inner_ratio

        bgl.glBegin(bgl.GL_POINTS)
        circleShader['vOutColor'] = color_outside
        circleShader['vInColor']  = color_inside
        bgl.glVertex3f(*world_loc)
        bgl.glEnd()

        circleShader.disable()

        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthRange(0.0, 1.0)
        bgl.glDepthMask(bgl.GL_TRUE)
