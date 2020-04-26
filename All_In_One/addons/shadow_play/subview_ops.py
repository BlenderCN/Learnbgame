import os
import sys
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import bpy
from bgl import *
import bpy.utils.previews
import bmesh
from rna_prop_ui import PropertyPanel
from bpy.app.handlers import persistent
from bpy.types import (Panel, Operator, PropertyGroup, UIList, Menu)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_extras.view3d_utils import region_2d_to_location_3d, region_2d_to_vector_3d
from bpy.props import FloatVectorProperty
from bpy.app.handlers import persistent

# depends on sklean
import numpy as np
import random
import copy
from numpy import linalg as LA
from sklearn.decomposition import PCA
from . import opengl_utils

################################################################################
# OverView Drawing Using OpenGL
# Modified from https://github.com/dfelinto/blender/blob/master/doc/python_api/examples/gpu.offscreen.1.py
################################################################################
class OffScreenOperatorDraw(bpy.types.Operator):
    bl_idname = "view3d.offscreen_draw"
    bl_label = "View3D Offscreen Draw"

    _handle_calc = None
    _handle_draw = None
    is_enabled = False

    # manage draw handler
    @staticmethod
    def draw_callback_px(self, context):
        aspect_ratio = 1.0
        self._update_offscreen(context, self._offscreen)
        ncamera = len(context.scene.recording_array)
        camera_trajectory = []
        objects_pos = []
        for i in range(ncamera):
            camera_trajectory.append((context.scene.recording_array[i].camera_position0,context.scene.recording_array[i].camera_position1,context.scene.recording_array[i].camera_rotation_euler))

        for obj in bpy.data.objects:
            if obj.name!='Camera':
                objects_pos.append((obj.location[0], obj.location[1]))

        camera_pos = bpy.data.objects['Camera'].location
        camera_orientation = bpy.data.objects['Camera'].rotation_euler[2]
        current_camera = (camera_pos[0],camera_pos[1],camera_orientation)
        self._opengl_draw(context, self._texture, aspect_ratio, 0.2, ncamera, camera_trajectory, current_camera, objects_pos)

    @staticmethod
    def handle_add(self, context):
        OffScreenOperatorDraw._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')

    @staticmethod
    def handle_remove():
        if OffScreenOperatorDraw._handle_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(OffScreenOperatorDraw._handle_draw, 'WINDOW')
        OffScreenOperatorDraw._handle_draw = None

    # off-screen buffer
    @staticmethod
    def _setup_offscreen(context):
        import gpu
        try:
            offscreen = gpu.offscreen.new(512, 512)
        except Exception as e:
            print(e)
            offscreen = None
        return offscreen

    @staticmethod
    def _update_offscreen(context, offscreen):
        scene = context.scene
        render = scene.render
        camera = scene.camera

        modelview_matrix = camera.matrix_world.inverted()
        projection_matrix = camera.calc_matrix_camera(
                render.resolution_x,
                render.resolution_y,
                render.pixel_aspect_x,
                render.pixel_aspect_y,
                )

        offscreen.draw_view3d(
                scene,
                context.space_data,
                context.region,
                projection_matrix,
                modelview_matrix,
                )

    @staticmethod
    def _opengl_draw(context, texture, aspect_ratio, scale, ncamera, camera_trajectory, current_camera, objects_pos):
        """
        OpenGL code to draw a rectangle in the viewport
        """

        glDisable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        # view setup
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glOrtho(-1, 1, -1, 1, -15, 15)
        gluLookAt(0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        act_tex = Buffer(GL_INT, 1)
        glGetIntegerv(GL_TEXTURE_2D, act_tex)

        viewport = Buffer(GL_INT, 4)
        glGetIntegerv(GL_VIEWPORT, viewport)

        width = int(scale * viewport[2])
        height = int(width / aspect_ratio)

        glViewport(viewport[0], viewport[1], width, height)
        glScissor(viewport[0], viewport[1], width, height)

        # draw routine
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)

        # glBindTexture(GL_TEXTURE_2D, texture)

        # texco = [(1, 1), (0, 1), (0, 0), (1, 0)]
        verco = [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)]

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        for i in range(4):
            # glTexCoord3f(texco[i][0], texco[i][1], 0.0)
            glVertex2f(verco[i][0], verco[i][1])
        glEnd()

        # plot grid
        LINE_N = 10
        for i in range(LINE_N):
            point0 = (-1.0+2.0*i/LINE_N,-1.0)
            point1 = (-1.0+2.0*i/LINE_N,1.0)
            glBegin(GL_LINES)
            glLineWidth(0.1)
            glColor3f(0.8,0.8,0.8)
            glVertex3f(point0[0],point0[1],0)
            glVertex3f(point1[0],point1[1],0)
            glEnd()

            point0 = (-1.0,-1.0+2.0*i/LINE_N)
            point1 = (1.0,-1.0+2.0*i/LINE_N)
            glBegin(GL_LINES)
            glLineWidth(0.1)
            glColor3f(0.8,0.8,0.8)
            glVertex3f(point0[0],point0[1],0)
            glVertex3f(point1[0],point1[1],0)
            glEnd()


        for i in range(ncamera):
            glBegin(GL_TRIANGLES)
            glColor3f(0.5, 0.5, 0.5)
            transform_matrix = mathutils.Matrix.Rotation(camera_trajectory[i][2], 3, 'Z')
            translation = Vector((camera_trajectory[i][0]/20.0, camera_trajectory[i][1]/20.0, 0))
            point0 = transform_matrix * Vector((-0.1,0.1,0)) + translation
            point1 = transform_matrix * Vector((0.1,0.1,0)) + translation
            glVertex3f(camera_trajectory[i][0]/20.0, camera_trajectory[i][1]/20.0, 0)
            glVertex3f(point0[0],point0[1],0)
            glVertex3f(point1[0],point1[1],0)
            glEnd()

        if ncamera>1:
            for i in range(ncamera-1):
                glBegin(GL_LINES);
                glColor3f(0.1, 0.1, 0.1);
                glLineWidth(0.3);
                glVertex2f(camera_trajectory[i][0]/20.0, camera_trajectory[i][1]/20.0);
                glVertex2f(camera_trajectory[i+1][0]/20.0, camera_trajectory[i+1][1]/20.0);
                glEnd();

        # current camera
        glBegin(GL_TRIANGLES)
        glColor3f(0.8, 0.3, 0.3)
        transform_matrix = mathutils.Matrix.Rotation(current_camera[2], 3, 'Z')
        translation = Vector((current_camera[0]/20.0, current_camera[1]/20.0, 0))
        point0 = transform_matrix * Vector((-0.1,0.1,0)) + translation
        point1 = transform_matrix * Vector((0.1,0.1,0)) + translation
        glVertex3f(current_camera[0]/20.0, current_camera[1]/20.0, 0)
        glVertex3f(point0[0],point0[1],0)
        glVertex3f(point1[0],point1[1],0)
        glEnd()
        opengl_utils.draw_dot(current_camera[0]/20.0, current_camera[1]/20.0, 0.9)

        # OBJECTS DRAWING
        for loc in objects_pos:
            opengl_utils.draw_dot(loc[0]/20.0, loc[1]/20.0, 0.0)

        # restoring settings
        # glBindTexture(GL_TEXTURE_2D, act_tex[0])

        glDisable(GL_TEXTURE_2D)

        # reset view
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glViewport(viewport[0], viewport[1], viewport[2], viewport[3])
        glScissor(viewport[0], viewport[1], viewport[2], viewport[3])

    # operator functions
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if OffScreenOperatorDraw.is_enabled:
            self.cancel(context)
            return {'FINISHED'}
        else:
            self._offscreen = OffScreenOperatorDraw._setup_offscreen(context)
            if self._offscreen:
                self._texture = self._offscreen.color_texture
            else:
                self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
                return {'CANCELLED'}

            OffScreenOperatorDraw.handle_add(self, context)
            OffScreenOperatorDraw.is_enabled = True

            if context.area:
                context.area.tag_redraw()

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def cancel(self, context):
        OffScreenOperatorDraw.handle_remove()
        OffScreenOperatorDraw.is_enabled = False

        if context.area:
            context.area.tag_redraw()
