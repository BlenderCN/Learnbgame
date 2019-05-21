# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche
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

from ...outputs.luxcore_api import pyluxcore
from ...export import get_worldscale
from ...export import object_anim_matrices
from ...export import fix_matrix_order

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
    
    
    def __convert_viewport_camera(self):
        if self.context.region_data is None:
            return

        view_persp = self.context.region_data.view_perspective
        view_matrix = mathutils.Matrix(self.context.region_data.view_matrix)
        view_lens = self.context.space_data.lens
        view_camera_zoom = self.context.region_data.view_camera_zoom
        view_camera_offset = list(self.context.region_data.view_camera_offset)

        luxCamera = self.context.scene.camera.data.luxrender_camera if self.context.scene.camera is not None else None

        if view_persp == 'ORTHO':
            raise Exception('Orthographic camera is not supported')
        else:
            lensradius = 0.0
            focaldistance = 0.0

            zoom = 1.0
            dx = 0.0
            dy = 0.0

            lookat = self.__convert_lookat(view_matrix.inverted())
            cam_origin = list(lookat[0:3])
            cam_lookat = list(lookat[3:6])
            cam_up = list(lookat[6:9])

            cam_fov = 2 * math.atan(0.5 * 32.0 / view_lens)

            if self.context.region.width > self.context.region.height:
                xaspect = 1.0
                yaspect = self.context.region.height / self.context.region.width
            else:
                xaspect = self.context.region.width / self.context.region.height
                yaspect = 1.0

            if view_persp == 'CAMERA':
                blCamera = self.context.scene.camera
                # magic zoom formula for camera viewport zoom from blender source
                zoom = view_camera_zoom
                zoom = (1.41421 + zoom / 50.0)
                zoom *= zoom
                zoom = 2.0 / zoom

                #camera plane offset in camera viewport
                view_camera_shift_x = self.context.scene.camera.data.shift_x
                view_camera_shift_y = self.context.scene.camera.data.shift_y
                dx = 2.0 * (view_camera_shift_x + view_camera_offset[0] * xaspect * 2.0)
                dy = 2.0 * (view_camera_shift_y + view_camera_offset[1] * yaspect * 2.0)

                cam_fov = blCamera.data.angle

                lookat = luxCamera.lookAt(blCamera)
                cam_origin = list(lookat[0:3])
                cam_lookat = list(lookat[3:6])
                cam_up = list(lookat[6:9])

                if luxCamera.use_dof:
                    # Do not world-scale this, it is already in meters!
                    lensradius = (blCamera.data.lens / 1000.0) / (2.0 * luxCamera.fstop)

                ws = get_worldscale(as_scalematrix=False)

                if luxCamera.use_dof:
                    if blCamera.data.dof_object is not None:
                        focaldistance = ws * ((blCamera.location - blCamera.data.dof_object.location).length)
                    elif blCamera.data.dof_distance > 0:
                        focaldistance = ws * blCamera.data.dof_distance

            zoom *= 2.0

            scr_left = -xaspect * zoom
            scr_right = xaspect * zoom
            scr_bottom = -yaspect * zoom
            scr_top = yaspect * zoom

            screenwindow = [scr_left + dx, scr_right + dx, scr_bottom + dy, scr_top + dy]

            self.properties.Set(pyluxcore.Property('scene.camera.lookat.target', cam_lookat))
            self.properties.Set(pyluxcore.Property('scene.camera.lookat.orig', cam_origin))
            self.properties.Set(pyluxcore.Property('scene.camera.up', cam_up))
            self.properties.Set(pyluxcore.Property('scene.camera.screenwindow', screenwindow))
            self.properties.Set(pyluxcore.Property('scene.camera.fieldofview', math.degrees(cam_fov)))
            self.properties.Set(pyluxcore.Property('scene.camera.lensradius', lensradius))
            self.properties.Set(pyluxcore.Property('scene.camera.focaldistance', focaldistance))

            if luxCamera is not None:
                # arbitrary clipping plane
                self.__convert_clipping_plane(luxCamera)
                # Shutter open/close
                self.__convert_shutter(luxCamera)
    

    def __convert_final_camera(self):
        blCamera = self.blender_scene.camera
        blCameraData = blCamera.data
        luxCamera = blCameraData.luxrender_camera

        # Motion blur
        self.__convert_camera_motion_blur(blCamera)

        # Shutter open/close
        self.__convert_shutter(luxCamera)

        # Field of view
        if blCameraData.type == 'PERSP' and luxCamera.type == 'perspective':
            self.properties.Set(pyluxcore.Property('scene.camera.fieldofview', [math.degrees(blCameraData.angle)]))

        # screenwindow (for border rendering and camera shift)
        width, height = luxCamera.luxrender_film.resolution(self.blender_scene)
        screenwindow = luxCamera.screenwindow(width, height, self.blender_scene, blCameraData,
                                              luxcore_export=self.blender_scene.render.use_border)
        self.properties.Set(pyluxcore.Property('scene.camera.screenwindow', screenwindow))

        if luxCamera.use_dof:
            # Do not world-scale this, it is already in meters
            self.properties.Set(pyluxcore.Property('scene.camera.lensradius', (blCameraData.lens / 1000.0) / (2.0 * luxCamera.fstop)))

        ws = get_worldscale(as_scalematrix=False)

        if luxCamera.use_dof:
            if blCameraData.dof_object is not None:
                self.properties.Set(pyluxcore.Property('scene.camera.focaldistance', ws * (
                    (blCamera.location - blCameraData.dof_object.location).length)))
            elif blCameraData.dof_distance > 0:
                self.properties.Set(pyluxcore.Property('scene.camera.focaldistance', ws * blCameraData.dof_distance))

        if luxCamera.use_clipping:
            self.properties.Set(pyluxcore.Property('scene.camera.cliphither', ws * blCameraData.clip_start))
            self.properties.Set(pyluxcore.Property('scene.camera.clipyon', ws * blCameraData.clip_end))

        # arbitrary clipping plane
        self.__convert_clipping_plane(luxCamera)


    def __convert_lookat(self, matrix):
        """
        Derive a list describing 3 points for a LuxRender LookAt statement
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

        return pos[:3] + target[:3] + up[:3]


    def __convert_camera_motion_blur(self, blCamera):
        luxCamera = blCamera.data.luxrender_camera

        if luxCamera.usemblur and luxCamera.cammblur:
            # Complete transformation is handled by motion.x.transformation below
            self.properties.Set(pyluxcore.Property('scene.camera.lookat.orig', [0, 0, 0]))
            self.properties.Set(pyluxcore.Property('scene.camera.lookat.target', [0, 0, -1]))
            self.properties.Set(pyluxcore.Property('scene.camera.up', [0, 1, 0]))

            anim_matrices = object_anim_matrices(self.blender_scene, blCamera, steps=luxCamera.motion_blur_samples)

            if anim_matrices:
                for i in range(len(anim_matrices)):
                    time = float(i) / (len(anim_matrices) - 1)
                    matrix = matrix_to_list(anim_matrices[i], apply_worldscale=True)
                    self.properties.Set(pyluxcore.Property('scene.camera.motion.%d.time' % i, time))
                    self.properties.Set(pyluxcore.Property('scene.camera.motion.%d.transformation' % i, matrix))
                return

        # No camera motion blur
        lookat = luxCamera.lookAt(blCamera)
        orig = list(lookat[0:3])
        target = list(lookat[3:6])
        up = list(lookat[6:9])

        self.properties.Set(pyluxcore.Property('scene.camera.lookat.orig', orig))
        self.properties.Set(pyluxcore.Property('scene.camera.lookat.target', target))
        self.properties.Set(pyluxcore.Property('scene.camera.up', up))


    def __convert_clipping_plane(self, lux_camera_settings):
        if lux_camera_settings.enable_clipping_plane:
            obj_name = lux_camera_settings.clipping_plane_obj

            try:
                obj = bpy.data.objects[obj_name]

                position = [obj.location.x, obj.location.y, obj.location.z]
                normal_vector = obj.rotation_euler.to_matrix() * mathutils.Vector((0.0, 0.0, 1.0))
                normal = [normal_vector.x, normal_vector.y, normal_vector.z]

                self.properties.Set(pyluxcore.Property('scene.camera.clippingplane.enable', [True]))
                self.properties.Set(pyluxcore.Property('scene.camera.clippingplane.center', position))
                self.properties.Set(pyluxcore.Property('scene.camera.clippingplane.normal', normal))
            except KeyError:
                # No valid clipping plane object selected
                self.properties.Set(pyluxcore.Property('scene.camera.clippingplane.enable', [False]))
        else:
            self.properties.Set(pyluxcore.Property('scene.camera.clippingplane.enable', [False]))


    def __convert_shutter(self, lux_camera_settings):
        shutter_open, shutter_close = calc_shutter(self.blender_scene, lux_camera_settings)

        self.properties.Set(pyluxcore.Property('scene.camera.shutteropen', shutter_open))
        self.properties.Set(pyluxcore.Property('scene.camera.shutterclose', shutter_close))
