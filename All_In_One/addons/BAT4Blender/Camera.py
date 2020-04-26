import bpy
from math import radians, sin, cos
from .Config import CAM_NAME
from .Enums import Zoom, Rotation

camera_range = 190
angle_zoom = [radians(60), radians(55), radians(50), radians(45)]
angle_rotation = [radians(-67.5), radians(22.5), radians(112.5), radians(202.5)]


class Camera:
    @staticmethod
    def get_location_and_rotation(rotation, zoom):
        level = zoom.value
        if level > 3:  # zoom 4, 5 & 6 all use the same camera angle
            level = 3

        x = camera_range * sin(angle_zoom[level]) * cos(angle_rotation[rotation.value])
        y = camera_range * sin(angle_zoom[level]) * sin(angle_rotation[rotation.value])
        z = camera_range * cos(angle_zoom[level])
        loc = (x, y, z)
        rot = (angle_zoom[level], 0,
               angle_rotation[rotation.value] + radians(90))  # need to add 90 for proper camera location in scene. .
        return [loc, rot]

    @staticmethod
    def set_camera(location, angles):
        cam = bpy.data.cameras.new(CAM_NAME)
        cam_ob = bpy.data.objects.new(CAM_NAME, cam)
        cam_ob.data.type = "ORTHO"
        cam_ob.data.clip_end = 10000  # in meters, i.e. 10 km seems sufficient
        cam_ob.rotation_mode = "XYZ"
        cam_ob.location = location
        cam_ob.rotation_euler = angles
        cam_ob.data.shift_x = 0.0
        cam_ob.data.shift_y = 0.0
        bpy.context.scene.objects.link(cam_ob)

    @staticmethod
    def update(rotation, zoom):
        (loc, rot) = Camera.get_location_and_rotation(rotation, zoom)
        bpy.data.objects[CAM_NAME].location = loc
        bpy.data.objects[CAM_NAME].rotation_euler = rot
        bpy.context.scene.update()


    @staticmethod
    def add_to_scene():
        if CAM_NAME not in bpy.data.objects:
            (location, rotation) = Camera.get_location_and_rotation(Rotation.NORTH, Zoom.FIVE)
            Camera.set_camera(location, rotation)

    @staticmethod
    def delete_from_scene():
        if CAM_NAME in bpy.data.objects:
            ob = bpy.data.objects[CAM_NAME]
            bpy.data.cameras.remove(ob.data, do_unlink=True)

    # @staticmethod
    # def gui_ops_camera(rotation, zoom):
    #     # if CAM_NAME not in bpy.data.objects:
    #     for ob in bpy.data.objects:
    #         if ob.type == 'CAMERA' and ob.name == CAM_NAME:
    #             bpy.data.cameras.remove(ob.data, do_unlink=True)
    #     (location, rotation) = Camera.get_location_and_rotation(rotation, zoom)
    #     Camera.set_camera(location, rotation)


# debug
# gui_ops_camera(View.NORTH, Zoom.FIVE)
