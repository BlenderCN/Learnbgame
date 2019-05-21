import bpy
import random
from math import sqrt
from mathutils import Vector
from time import time

from .functions import draw_callback_3d

global_cameras = []

class ViewCameraField(bpy.types.Operator):
    bl_idname = "camerafield.view_field"
    bl_label = "Add Camera Frustum"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Press escape to quit"

    def modal(self, context, event):
        try:
            context.area.tag_redraw()
        except AttributeError:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            global_cameras.clear()
            return {'CANCELLED'}

        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            global_cameras.clear()
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            scene = context.scene
            self.current_frame = scene.frame_current

            if global_cameras:
                op_running = True
            else:
                op_running = False

            if scene.camera_frustum_settings.only_active:
                cams = (scene.camera,)
            else:
                cams = [o for o in context.visible_objects if o.type == 'CAMERA']

            ratio = context.scene.render.resolution_y / context.scene.render.resolution_x

            tmp_frame = []

            seed = time()  # Different seed at each execution

            for cam in cams:
                cam_color = cam.data.camera_frustum_settings.color
                camera_points = {"color": cam_color,
                                 "co": []}

                for i in range(scene.frame_start, scene.frame_end + 1):
                    scene.frame_set(i)
                    random.seed(seed)  # Use a predictable seed

                    if not cam.data.camera_frustum_settings.active:
                        continue

                    if cam.data.type not in ('PERSP', 'ORTHO'):
                        self.report({'WARNING'}, "Camera type unsupported: " + cam.name)
                        continue

                    cam_coord = cam.matrix_world.to_translation()
                    cam_direction = Vector(cam.matrix_world.transposed()[2][:-1])

                    frame = cam.data.view_frame(scene)

                    density = scene.camera_frustum_settings.density

                    frame = [cam.matrix_world.normalized() * corner for corner in frame]

                    vector_x = frame[0] - frame[3]
                    vector_y = frame[2] - frame[3]

                    if scene.camera_frustum_settings.distribution == 'Random':
                        points = [(random.random(), random.random())
                                  for z in range(density)
                                  ]

                    elif scene.camera_frustum_settings.distribution == 'Grid':
                        density_x = sqrt(density) / sqrt(ratio)
                        density_y = sqrt(density) * sqrt(ratio)

                        points = [(x / (int(density_x) - 1),
                                   y / (int(density_y) - 1)
                                   )
                                  for x in range(int(density_x))
                                  for y in range(int(density_y))
                                  ]

                    for x, y in points:
                            point = (frame[3] + vector_x * x + vector_y * y)

                            if cam.data.type == 'PERSP':
                                ray = scene.ray_cast(cam_coord, point - cam_coord)
                            elif cam.data.type == 'ORTHO':
                                ray = scene.ray_cast(point, -cam_direction)

                            if ray[0]:
                                ray_closer = ray[1] + (point-ray[1]).normalized() * 0.02
                                if not ray_closer in camera_points["co"]:
                                    camera_points["co"].append(ray_closer)
                print(len(camera_points["co"]), 'points')
                global_cameras.append(camera_points)

            if op_running:
                return {'FINISHED'}
            else:
                # the arguments we pass the callback
                args = (global_cameras,)
                # Add the region OpenGL drawing callback
                # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
                self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, 'WINDOW', 'POST_VIEW')

                context.window_manager.modal_handler_add(self)

                return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
