# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche, Michael Klemm
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#

import bpy, math, mathutils
from mathutils import Vector

from ...outputs.luxcore_api import pyluxcore, set_prop_cam
from ...export import get_worldscale
from ...export import object_anim_matrices
from ...export import fix_matrix_order
from ...export import matrix_to_list

from .utils import calc_shutter


class CameraExporter(object):
    def __init__(self, blender_scene, is_viewport_render=False, context=None):
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        self.context = context
        self.properties = pyluxcore.Properties()


    def convert(self):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        if self.is_viewport_render:
            self.__convert_viewport_camera()
        else:
            self.__convert_final_camera()

        return self.properties


    def __calc_screenwindow(self, dx, dy, xaspect, yaspect, zoom):
        scr_left = -xaspect * zoom
        scr_right = xaspect * zoom
        scr_bottom = -yaspect * zoom
        scr_top = yaspect * zoom

        return [scr_left + dx, scr_right + dx, scr_bottom + dy, scr_top + dy]


    def __convert_viewport_camera(self):
        if self.context.region_data is None:
            return

        view_persp = self.context.region_data.view_perspective
        view_matrix = mathutils.Matrix(self.context.region_data.view_matrix)
        view_lens = self.context.space_data.lens
        view_camera_zoom = self.context.region_data.view_camera_zoom
        view_camera_offset = list(self.context.region_data.view_camera_offset)
        view_ortho_zoom = self.context.space_data.region_3d.view_distance

        luxCamera = self.context.scene.camera.data.pbrtv3_camera if self.context.scene.camera is not None else None

        if self.context.region.width > self.context.region.height:
            xaspect = 1.0
            yaspect = self.context.region.height / self.context.region.width
        else:
            xaspect = self.context.region.width / self.context.region.height
            yaspect = 1.0

        if view_persp == 'ORTHO':
            # Viewport cam in orthographic mode
            zoom = view_ortho_zoom
            dx = 0.0
            dy = 0.0
            screenwindow = self.__calc_screenwindow(dx, dy, xaspect, yaspect, zoom)

            cam_origin, cam_target, cam_up = self.__convert_lookat(view_matrix.inverted())

            # Move the camera origin away from the viewport center to avoid clipping
            origin = Vector(cam_origin)
            target = Vector(cam_target)
            origin += (origin - target) * 50
            cam_origin = list(origin)

            set_prop_cam(self.properties, 'type', 'orthographic')
            set_prop_cam(self.properties, 'lookat.target', cam_target)
            set_prop_cam(self.properties, 'lookat.orig', cam_origin)
            set_prop_cam(self.properties, 'up', cam_up)
            set_prop_cam(self.properties, 'screenwindow', screenwindow)
            set_prop_cam(self.properties, 'lensradius', 0.0)
            set_prop_cam(self.properties, 'focaldistance', 0.0)

        elif view_persp == 'PERSP':
            # Viewport cam in perspective mode
            zoom = 2.0
            dx = 0.0
            dy = 0.0
            screenwindow = self.__calc_screenwindow(dx, dy, xaspect, yaspect, zoom)

            cam_origin, cam_target, cam_up = self.__convert_lookat(view_matrix.inverted())

            cam_fov = 2 * math.atan(0.5 * 32.0 / view_lens)

            set_prop_cam(self.properties, 'type', 'perspective')
            set_prop_cam(self.properties, 'lookat.target', cam_target)
            set_prop_cam(self.properties, 'lookat.orig', cam_origin)
            set_prop_cam(self.properties, 'up', cam_up)
            set_prop_cam(self.properties, 'screenwindow', screenwindow)
            set_prop_cam(self.properties, 'fieldofview', math.degrees(cam_fov))
            set_prop_cam(self.properties, 'lensradius', 0.0)
            set_prop_cam(self.properties, 'focaldistance', 0.0)

        elif view_persp == 'CAMERA':
            # Using final render camera in viewport
            self.__convert_final_camera()

            # magic zoom formula for camera viewport zoom from blender source
            zoom = view_camera_zoom
            zoom = (1.41421 + zoom / 50.0)
            zoom *= zoom
            zoom = 2.0 / zoom
            zoom *= 2

            blCamera = self.context.scene.camera
            if blCamera.data.type == 'ORTHO':
                zoom *= blCamera.data.ortho_scale / 2

            #camera plane offset in camera viewport
            view_camera_shift_x = self.context.scene.camera.data.shift_x
            view_camera_shift_y = self.context.scene.camera.data.shift_y
            dx = 2.0 * (view_camera_shift_x + view_camera_offset[0] * xaspect * 2.0)
            dy = 2.0 * (view_camera_shift_y + view_camera_offset[1] * yaspect * 2.0)

            # TODO: in border render mode, the screenwindow should be adapted to the border

            if blCamera.data.sensor_fit == 'VERTICAL':
                aspect_fix = yaspect
            elif blCamera.data.sensor_fit == 'HORIZONTAL':
                aspect_fix = xaspect
            else:
                aspect_fix = 1.0

            screenwindow = self.__calc_screenwindow(dx, dy, xaspect / aspect_fix, yaspect / aspect_fix, zoom)
            set_prop_cam(self.properties, 'screenwindow', screenwindow)

        if luxCamera is not None:
            # arbitrary clipping plane
            self.__convert_clipping_plane(luxCamera)
            # Shutter open/close
            self.__convert_shutter(luxCamera)


    def __convert_final_camera(self):
        blCamera = self.blender_scene.camera
        blCameraData = blCamera.data
        luxCamera = blCameraData.pbrtv3_camera

        if blCameraData.type == 'ORTHO':
            set_prop_cam(self.properties, 'type', 'orthographic')
        elif blCameraData.type == 'PANO':
            set_prop_cam(self.properties, 'type', 'environment')
        else:
            set_prop_cam(self.properties, 'type', 'perspective')

        # Motion blur
        self.__convert_camera_motion_blur(blCamera)

        # Shutter open/close
        self.__convert_shutter(luxCamera)

        # Field of view
        # Correction for vertical fit sensor, must truncate the float to .1f precision and round down !
        width, height = luxCamera.pbrtv3_film.resolution(self.blender_scene)

        if blCameraData.sensor_fit == 'VERTICAL' and not self.is_viewport_render and width > height:
            aspect_fix = round(width / height - 0.05, 1) # make sure it rounds down
        else:
            aspect_fix = 1.0

        if blCameraData.type == 'PERSP' and luxCamera.type == 'perspective':
            set_prop_cam(self.properties, 'fieldofview', math.degrees(blCameraData.angle * aspect_fix))

        # screenwindow (for border rendering and camera shift)
        screenwindow = luxCamera.screenwindow(width, height, self.blender_scene, blCameraData,
                                              luxcore_export=self.blender_scene.render.use_border)
        set_prop_cam(self.properties, 'screenwindow', screenwindow)

        if luxCamera.use_dof:
            # Do not world-scale this, it is already in meters
            lensradius = (blCameraData.lens / 1000.0) / (2.0 * luxCamera.fstop)
            set_prop_cam(self.properties, 'lensradius', lensradius)
            set_prop_cam(self.properties, 'autofocus.enable', luxCamera.autofocus)

        ws = get_worldscale(as_scalematrix=False)

        if luxCamera.use_dof:
            if blCameraData.dof_object is not None:
                distance = ws * (blCamera.location - blCameraData.dof_object.location).length
                set_prop_cam(self.properties, 'focaldistance', distance)
            elif blCameraData.dof_distance > 0:
                set_prop_cam(self.properties, 'focaldistance', ws * blCameraData.dof_distance)

        if luxCamera.use_clipping:
            set_prop_cam(self.properties, 'cliphither', ws * blCameraData.clip_start)
            set_prop_cam(self.properties, 'clipyon', ws * blCameraData.clip_end)

        # arbitrary clipping plane
        self.__convert_clipping_plane(luxCamera)


    def __convert_lookat(self, matrix):
        """
        Derive a list describing 3 points for a PBRTv3 LookAt statement
        Copied from properties/camera.py because realtime preview needs access to this without a camera object

        Returns     tuple(9) (floats)
        """
        ws = get_worldscale()
        matrix *= ws
        ws = get_worldscale(as_scalematrix=False)
        matrix = fix_matrix_order(matrix)  # matrix indexing hack
        matrix[0][3] *= ws
        matrix[1][3] *= ws
        matrix[2][3] *= ws

        # transpose to extract columns
        matrix = matrix.transposed()
        pos = matrix[3]
        forwards = -matrix[2]
        target = (pos + forwards)
        up = matrix[1]

        lookat = pos[:3] + target[:3] + up[:3]

        cam_origin = list(lookat[0:3])
        cam_target = list(lookat[3:6])
        cam_up = list(lookat[6:9])

        return cam_origin, cam_target, cam_up


    def __convert_camera_motion_blur(self, blCamera):
        luxCamera = blCamera.data.pbrtv3_camera

        # Note: enabling this in viewport leads to constant refresing of the render, even when cam is not animated
        if luxCamera.usemblur and luxCamera.cammblur and not self.is_viewport_render:
            # Complete transformation is handled by motion.x.transformation below
            set_prop_cam(self.properties, 'lookat.orig', [0, 0, 0])
            set_prop_cam(self.properties, 'lookat.target', [0, 0, -1])
            set_prop_cam(self.properties, 'up', [0, 1, 0])

            anim_matrices = object_anim_matrices(self.blender_scene, blCamera, steps=luxCamera.motion_blur_samples)

            if anim_matrices:
                for i in range(len(anim_matrices)):
                    time = float(i) / (len(anim_matrices) - 1)
                    matrix = matrix_to_list(anim_matrices[i], apply_worldscale=True)
                    set_prop_cam(self.properties, 'motion.%d.time' % i, time)
                    set_prop_cam(self.properties, 'motion.%d.transformation' % i, matrix)
                return

        # No camera motion blur
        lookat = luxCamera.lookAt(blCamera)
        orig = list(lookat[0:3])
        target = list(lookat[3:6])
        up = list(lookat[6:9])

        set_prop_cam(self.properties, 'lookat.orig', orig)
        set_prop_cam(self.properties, 'lookat.target', target)
        set_prop_cam(self.properties, 'up', up)


    def __convert_clipping_plane(self, lux_camera_settings):
        if lux_camera_settings.enable_clipping_plane:
            obj_name = lux_camera_settings.clipping_plane_obj

            try:
                obj = bpy.data.objects[obj_name]

                position = [obj.location.x, obj.location.y, obj.location.z]
                normal_vector = obj.rotation_euler.to_matrix() * mathutils.Vector((0.0, 0.0, 1.0))
                normal = [normal_vector.x, normal_vector.y, normal_vector.z]

                set_prop_cam(self.properties, 'clippingplane.enable', True)
                set_prop_cam(self.properties, 'clippingplane.center', position)
                set_prop_cam(self.properties, 'clippingplane.normal', normal)
            except KeyError:
                # No valid clipping plane object selected
                set_prop_cam(self.properties, 'clippingplane.enable', False)
        else:
            set_prop_cam(self.properties, 'clippingplane.enable', False)


    def __convert_shutter(self, lux_camera_settings):
        shutter_open, shutter_close = calc_shutter(self.blender_scene, lux_camera_settings)

        set_prop_cam(self.properties, 'shutteropen', shutter_open)
        set_prop_cam(self.properties, 'shutterclose', shutter_close)
