# ##### BEGIN LGPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END LGPL LICENSE BLOCK #####


from mathutils import Vector
import sys
import shutil
import os
import subprocess
import time
import logging
import bpy

logger = logging.getLogger(__name__)


class Scene(object):
    log = logging.getLogger('scene.Scene')

    def __init__(self, context):
        self.log.debug('__init__ called')

        cf = context.scene.cookie_factory
        self.in_blender = not bpy.app.background
        self.cwd = os.path.dirname(cf.config_filepath)

        # Set to object mode
        if context.active_object and context.active_object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Reset World setting
        world = context.scene.world
        world.light_settings.use_ambient_occlusion = False
        world.light_settings.ao_blend_type = 'ADD'
        world.light_settings.samples = 5
        world.mist_settings.use_mist = False
        world.horizon_color = (0.051, 0.051, 0.051)

        # Clear frame handlers
        bpy.app.handlers.frame_change_pre.clear()
        bpy.app.handlers.render_pre.clear()

        # Clear all objects and corresponding data
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                scene.objects.unlink(obj)

        bpy_data_types = [bpy.data.objects, bpy.data.meshes, bpy.data.lamps, bpy.data.cameras, bpy.data.materials, bpy.data.curves]
        for bpy_data in bpy_data_types:
            for id_data in bpy_data:
                if id_data.users > 0:
                    id_data.user_clear()
                bpy_data.remove(id_data)

        # Set current frame and number of frames
        self.frame = context.scene.frame_current
        self.frames = context.scene.frame_end

        self.setup()

        # Set frame_change_pre or render_pre handler
        if self.in_blender:
            bpy.app.handlers.frame_change_pre.append(
                self.__frameChangeHandler)
        else:
            bpy.app.handlers.render_pre.append(
                self.__frameChangeHandler)


    def __frameChangeHandler(self, scene):
        if (not self.in_blender) and (scene.frame_current > scene.frame_end):
            bpy.ops.wm.quit_blender()

        self.log.info("frameChangeHandler frame : {}/{}".format(
                        scene.frame_current, scene.frame_end))

        self.frame = scene.frame_current
        self.frames = scene.frame_end
        if self.frame < 1:
            self.frame = 1

        if self.frame >= self.frames:
            self.frame = self.frames

        self.draw()


    # Main methods of Scene
    def setup(self):
        raise NotImplementedError()

    def draw(self):
        pass


class BmeshAnimation(object):
    log = logging.getLogger('scene.BmeshAnimation')

    def __init__(self, composition, frame_function=None, single_frame=True):
        self.bmList = None
        self.frame_function = frame_function
        self.composition = composition

        # Create object and mesh for scene
        self.mesh = bpy.data.meshes.new("AnimationObjectMesh")
        self.obj = bpy.data.objects.new("AnimationObject", self.mesh)
        bpy.context.scene.objects.link(self.obj)

        # Precompute all the geometry
        if not single_frame:
            self.bmList = []
            for frame in range(self.composition.frames):
                self.log.debug("Calculating geometry for frame %03i/%03i" % \
                            (frame + 1, self.composition.frames))
                self.bmList.append(self.frame_function(frame, self.composition.frames))

        # Set frame_change_pre or render_prehandler
        if composition.in_blender:
            bpy.app.handlers.frame_change_pre.append(self.__frameChangeHandler)
        else:
            bpy.app.handlers.render_pre.append(self.__frameChangeHandler)

    def __frameChangeHandler(self, scene):
        frame = bpy.context.scene.frame_current - 1

        # Clip frame number
        if(frame < 1):
            frame = 1
        if(frame >= self.composition.frames):
            frame = self.composition.frames

        if(self.bmList):
            bm = self.bmList[frame]
            bm.to_mesh(self.mesh)
            self.mesh.update()
        else:
            bm = self.frame_function(frame, self.composition.frames)
            bm.to_mesh(self.mesh)
            self.mesh.update()
            bm.free()

    def append_material(self, mat):
        self.obj.data.materials.append(mat)
