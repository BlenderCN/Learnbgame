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
import bmesh
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from mathutils.geometry import intersect_line_line, intersect_point_line, intersect_line_plane

# Addon imports
from .points_picker_states import PointsPicker_States
from .points_picker_ui_init import PointsPicker_UI_Init
from .points_picker_ui_draw import PointsPicker_UI_Draw
from .points_picker_datastructure import D3Point
from ...addon_common.cookiecutter.cookiecutter import CookieCutter
from ...addon_common.common.blender import bversion
from ...addon_common.common.maths import Point, Point2D
from ...addon_common.common.decorators import PersistentOptions
from ...functions.common import *


class VIEW3D_OT_points_picker(PointsPicker_States, PointsPicker_UI_Init, PointsPicker_UI_Draw, CookieCutter):
    """ Place and move points on surface of target mesh """
    operator_id    = "view3d.points_picker"
    bl_idname      = "view3d.points_picker"
    bl_label       = "Points Picker"
    bl_description = "Place and move points on surface of target mesh"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"

    ################################################
    # CookieCutter Operator methods

    @classmethod
    def can_start(cls, context):
        """ Start only if editing a mesh """
        ob = context.active_object
        return ob is not None and ob.type == "MESH"

    def start(self):
        """ ExtruCut tool is starting """
        scn = bpy.context.scene

        bpy.ops.ed.undo_push()  # push current state to undo

        self.header_text_set("PointsPicker")
        self.cursor_modal_set("CROSSHAIR")
        self.manipulator_hide()

        self.ui_setup()
        self.ui_setup_post()

        self.snap_type = "OBJECT"  #'SCENE' 'OBJECT'
        self.snap_ob = bpy.context.object
        self.started = False
        self.b_pts = list()  # list of 'Point' objects (see /lib/point.py)
        self.selected = -1
        self.hovered = [None, -1]

        self.grab_undo_loc = None
        self.grab_undo_no = None
        self.mouse = (None, None)
        self.start_post()

    def end_commit(self):
        """ Commit changes to mesh! """
        scn = bpy.context.scene
        for pt in self.b_pts:
            point_obj = bpy.data.objects.new(pt.label, None)
            point_obj.location = pt.location
            scn.objects.link(point_obj)
        self.end_commit_post()

    def end_cancel(self):
        """ Cancel changes """
        bpy.ops.ed.undo()   # undo geometry hide

    def end(self):
        """ Restore everything, because we're done """
        self.manipulator_restore()
        self.header_text_restore()
        self.cursor_modal_restore()

    def update(self):
        """ Check if we need to update any internal data structures """
        pass

    ###################################################
    # class variables

    # NONE!

    #############################################
    # class methods

    def resetLabels(self):
        for i,pt in enumerate(self.b_pts):
            pt.label = self.getLabel(i)

    def getLabel(self, idx):
        return "P%(idx)s" % locals()

    def closest_extrude_Point(self, p2D : Point2D) -> Point:
        r = self.drawing.Point2D_to_Ray(p2D)
        p,_ = intersect_line_line(
            self.extrude_pt0, self.extrude_pt1,
            r.o, r.o + r.d,
            )
        return Point(p)

    def grab_mouse_move(self,context,x,y):
        region = context.region
        rv3d = context.region_data
        coord = x, y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)


        hit = False
        if self.snap_type == 'SCENE':

            mx = Matrix.Identity(4) #scene ray cast returns world coords
            imx = Matrix.Identity(4)
            no_mx = imx.to_3x3().transposed()
            if bversion() < '002.077.000':
                res, obj, omx, loc, no = context.scene.ray_cast(ray_origin, ray_target)
            else:
                res, loc, no, ind, obj, omx = context.scene.ray_cast(ray_origin, view_vector)

            if res:
                hit = True

            else:
                #cast the ray into a plane a
                #perpendicular to the view dir, at the last bez point of the curve
                hit = True
                view_direction = rv3d.view_rotation * Vector((0,0,-1))
                plane_pt = self.grab_undo_loc
                loc = intersect_line_plane(ray_origin, ray_target,plane_pt, view_direction)
                no = view_direction
        elif self.snap_type == 'OBJECT':
            mx = self.snap_ob.matrix_world
            imx = mx.inverted()
            no_mx = imx.to_3x3().transposed()
            if bversion() < '002.077.000':
                loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target)
                if face_ind != -1:
                    hit = True
            else:
                ok, loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target - imx*ray_origin)
                if ok:
                    hit = True

        if not hit:
            self.grab_cancel()

        else:
            self.b_pts[self.selected].location = mx * loc
            self.b_pts[self.selected].surface_normal = no_mx * no

    def grab_cancel(self):
        old_co =  self.grab_undo_loc
        self.b_pts[self.selected].location = old_co

    def click_add_point(self, context, x, y):
        '''
        x,y = event.mouse_region_x, event.mouse_region_y

        this will add a point into the bezier curve or
        close the curve into a cyclic curve
        '''
        region = context.region
        rv3d = context.region_data
        coord = x, y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)

        hit = False
        # ray cast on the any object
        if self.snap_type == 'SCENE':
            mx = Matrix.Identity(4)  # loc is given in world loc...no need to multiply by obj matrix
            imx = Matrix.Identity(4)
            no_mx = Matrix.Identity(3)
            if bversion() < '002.077.000':
                hit, obj, omx, loc, no = context.scene.ray_cast(ray_origin, ray_target)  #changed in 2.77
            else:
                hit, loc, no, ind, obj, omx = context.scene.ray_cast(ray_origin, view_vector)
                iomx = omx.inverted()
                no_mx = iomx.to_3x3().transposed()
            # if not hit:
            #     # cast the ray into a plane perpendicular to the view dir, at the last bez point of the curve
            #
            #     view_direction = rv3d.view_rotation * Vector((0,0,-1))
            #
            #     if len(self.b_pts):
            #         plane_pt = self.b_pts[-1].location
            #     else:
            #         plane_pt = context.scene.cursor_location
            #     loc = intersect_line_plane(ray_origin, ray_target,plane_pt, view_direction)
            #     hit = True
        # ray cast on self.snap_ob
        elif self.snap_type == 'OBJECT':
            mx = self.snap_ob.matrix_world
            imx = mx.inverted()
            no_mx = imx.to_3x3().transposed()

            if bversion() < '002.077.000':
                loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target)[0 if bversion() < '002.077.000' else 1:]
            else:
                hit, loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target - imx*ray_origin)

            if face_ind != -1:
                hit = True

        # no object was hit
        if not hit:
            self.selected = -1
            return False

        # select existing point
        if self.hovered[0] == 'POINT':
            self.selected = self.hovered[1]
            return False
        # add new point
        elif self.hovered[0] == None:
            new_point = D3Point(location=mx * loc, surface_normal=no_mx * no, view_direction=view_vector, source_object=obj if self.snap_type == "SCENE" else self.snap_ob)
            self.b_pts.append(new_point)
            new_point.label = self.getLabel(len(self.b_pts) - 1)
            self.hovered = ['POINT', len(self.b_pts) - 1]
            return True

    def click_remove_point(self, mode='mouse'):
        if mode == 'mouse':
            if not self.hovered[0] == 'POINT': return
            self.b_pts.pop(self.hovered[1])
            if self.selected == self.hovered[1]: self.selected = -1
            elif self.selected > self.hovered[1]: self.selected -= 1
            self.hovered = [None, -1]
        else:
            if self.selected == -1: return
            self.b_pts.pop(self.selected)
            self.selected = -1
        self.resetLabels()

    def hover(self, context, x, y):
        '''
        hovering happens in mixed 3d and screen space.  It's a mess!
        '''

        if len(self.b_pts) == 0:
            return

        region = context.region
        rv3d = context.region_data
        self.mouse = Vector((x, y))
        coord = x, y
        loc3d_reg2D = view3d_utils.location_3d_to_region_2d

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)

        if self.snap_type == 'OBJECT':
            mx = self.snap_ob.matrix_world
            imx = mx.inverted()

            if bversion() < '002.077.000':
                loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target)
                if face_ind == -1:
                    #do some shit
                    pass
            else:
                res, loc, no, face_ind = self.snap_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
                if not res:
                    #do some shit
                    pass
        elif self.snap_type == 'SCENE':

            mx = Matrix.Identity(4) #scene ray cast returns world coords
            if bversion() < '002.077.000':
                res, obj, omx, loc, no = context.scene.ray_cast(ray_origin, ray_target)
            else:
                res, loc, no, ind, obj, omx = context.scene.ray_cast(ray_origin, view_vector)


        def dist(v):
            diff = v - Vector((x,y))
            return diff.length

        def dist3d(pt):
            if pt.location is None:
                return 100000000
            delt = pt.location - mx * loc
            return delt.length

        closest_3d_point = min(self.b_pts, key=dist3d)
        screen_dist = dist(loc3d_reg2D(context.region, context.space_data.region_3d, closest_3d_point.location))

        self.hovered = ['POINT', self.b_pts.index(closest_3d_point)] if screen_dist < 20 else [None, -1]

    #############################################
    # Subclassing functions

    def ui_setup_post(self):
        pass

    def start_post(self):
        pass

    def add_point_pre(self, loc):  # returns True if point can be added, else False`
        return True

    def add_point_post(self, new_point):
        pass

    def move_point_post(self, moved_point):
        pass

    def end_commit_post(self):
        pass

    def can_commit(self):
        return True

    def can_cancel(self):
        return True

    #############################################
