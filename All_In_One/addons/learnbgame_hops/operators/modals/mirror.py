import bpy
import bpy_extras.view3d_utils
import mathutils
import math
from bgl import *
from ... graphics.drawing2d import draw_text
from ... utils.space_3d import centroid, scale, rotate_z, rotate_x, rotate_y, transform3D
from ... utils.space_2d import inside_polygon
from ... utils.region import get_rv3d
from ... preferences import get_preferences
from ... utils.context import ExecutionContext
from .. misc.mirrormirror import operation


class HOPS_OT_ModalMirror(bpy.types.Operator):
    bl_idname = "view3d.hops_modal_mirror"
    bl_label = "Modal Mirror"
    bl_description = """modal mirror, x,y,z to set axis"""
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    button_x_positive = False
    button_x_negative = False
    button_y_positive = False
    button_y_negative = False
    button_z_positive = False
    button_z_negative = False

    @classmethod
    def poll(cls, context):
        active_object = bpy.context.active_object
        return getattr(active_object, "type", "") in {"MESH", "EMPTY", "CURVE"}

    def invoke(self, context, event):
        self.last_mouse_x = event.mouse_region_x
        self.points_x_p = []
        self.points_x_p_region = []
        self.mouse_pos = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        selected = context.selected_objects
        if len(selected) == 1:
            self.multiselection = False
        else:
            self.multiselection = True

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            self.mouse_pos = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))

        if event.type == 'MIDDLEMOUSE':
            return {"PASS_THROUGH"}

        if event.type == 'WHEELUPMOUSE':
            if event.value == 'PRESS':
                return {"PASS_THROUGH"}

        if event.type == 'WHEELDOWNMOUSE':
            if event.value == 'PRESS':
                return {"PASS_THROUGH"}

        if event.type in ("SPACE", "LEFTMOUSE"):
            if event.value == 'PRESS':
                if self.multiselection:
                    if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad4):
                        get_preferences().Hops_mirror_modes_multi = "VIA_ACTIVE"

                    elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad3):
                        get_preferences().Hops_mirror_modes_multi = "SYMMETRY"

                else:
                    if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad2):
                        get_preferences().Hops_mirror_modes = "SYMMETRY"

                    elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad3):
                        get_preferences().Hops_mirror_modes = "BISECT"

                    elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad4):
                        get_preferences().Hops_mirror_modes = "MODIFIER"

                    elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad5):
                        get_preferences().Hops_mirror_modal_use_cursor = True

                    elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.quad6):
                        get_preferences().Hops_mirror_modal_use_cursor = False

                if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_x_p_region):
                    self._operation = "MIRROR_X"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_X"
                    else:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_X"
                    self.used_axis = "X"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((1, 0, 0))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

                elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_x_n_region):
                    self._operation = "MIRROR_X"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_X"
                    else:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_X"
                    self.used_axis = "X"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((1, 0, 0))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

                elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_y_p_region):
                    self._operation = "MIRROR_Y"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_Y"
                    else:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_Y"
                    self.used_axis = "Y"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((0, 1, 0))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

                elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_y_n_region):
                    self._operation = "MIRROR_Y"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_Y"
                    else:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_Y"
                    self.used_axis = "Y"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((0, 1, 0))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

                elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_z_p_region):
                    self._operation = "MIRROR_Z"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_Z"
                    else:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_Z"
                    self.used_axis = "Z"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((0, 0, 1))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

                elif inside_polygon(self.mouse_pos[0], self.mouse_pos[1], self.points_z_n_region):
                    self._operation = "MIRROR_Z"
                    if get_preferences().Hops_mirror_modal_revert:
                        get_preferences().Hops_mirror_direction = "+"
                        self.direction = "POSITIVE_Z"
                    else:
                        get_preferences().Hops_mirror_direction = "-"
                        self.direction = "NEGATIVE_Z"
                    self.used_axis = "Z"

                    if get_preferences().Hops_mirror_modal_use_cursor:
                        self.x, self.y, self.z = bpy.context.scene.cursor_location
                    else:
                        self.x, self.y, self.z = bpy.context.object.location
                    self.zx, self.zy, self.zz = bpy.context.object.rotation_euler
                    vec = mathutils.Vector((0, 0, 1))
                    mat = mathutils.Matrix.Rotation(self.zx, 4, "X")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zy, 4, "Y")
                    vec.rotate(mat)
                    mat = mathutils.Matrix.Rotation(self.zz, 4, "Z")
                    vec.rotate(mat)
                    self.nx = vec[0]
                    self.ny = vec[1]
                    self.nz = vec[2]

                    return self.execute(context)

        if event.type in ("ESC", "RIGHTMOUSE"):
            return self.finish(context)

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if get_preferences().Hops_mirror_modal_use_cursor:
            if self.multiselection is False:
                with ExecutionContext(mode="OBJECT", active_object=bpy.context.active_object):
                        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        operation(context, self._operation, self.x, self.y, self.z, self.nx, self.ny, self.nz, self.direction, self.used_axis)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        context.area.tag_redraw()
        return {"CANCELLED"}

    def draw(self, context):
        object = bpy.context.active_object
        region = context.region
        rv3d = context.region_data

        scale_value = get_preferences().Hops_mirror_modal_sides_scale
        zoom_fix = rv3d.view_distance / bpy.context.space_data.lens
        zoom_value = get_preferences().Hops_mirror_modal_scale

        # it is view target not view location
        location = rv3d.view_location
        if get_preferences().Hops_mirror_modal_use_cursor:
            if self.multiselection:
                center_loc = object.location
            else:
                center_loc = bpy.context.scene.cursor_location
        else:
            center_loc = object.location

        point1 = location.x - 1, location.y + 1, location.z + 1
        point2 = location.x - 1, location.y - 1, location.z + 1
        point3 = location.x - 1, location.y - 1, location.z - 1
        point4 = location.x - 1, location.y + 1, location.z - 1
        point5 = location.x + 1, location.y + 1, location.z + 1
        point6 = location.x + 1, location.y - 1, location.z + 1
        point7 = location.x + 1, location.y - 1, location.z - 1
        point8 = location.x + 1, location.y + 1, location.z - 1

        point1 = scale(location, point1, zoom_fix)
        point2 = scale(location, point2, zoom_fix)
        point3 = scale(location, point3, zoom_fix)
        point4 = scale(location, point4, zoom_fix)
        point5 = scale(location, point5, zoom_fix)
        point6 = scale(location, point6, zoom_fix)
        point7 = scale(location, point7, zoom_fix)
        point8 = scale(location, point8, zoom_fix)

        point1 = scale(location, point1, zoom_value)
        point2 = scale(location, point2, zoom_value)
        point3 = scale(location, point3, zoom_value)
        point4 = scale(location, point4, zoom_value)
        point5 = scale(location, point5, zoom_value)
        point6 = scale(location, point6, zoom_value)
        point7 = scale(location, point7, zoom_value)
        point8 = scale(location, point8, zoom_value)

        angle = object.rotation_euler[0] + math.radians(90)
        point1 = rotate_x(location, point1, angle)
        point2 = rotate_x(location, point2, angle)
        point3 = rotate_x(location, point3, angle)
        point4 = rotate_x(location, point4, angle)
        point5 = rotate_x(location, point5, angle)
        point6 = rotate_x(location, point6, angle)
        point7 = rotate_x(location, point7, angle)
        point8 = rotate_x(location, point8, angle)

        angle = object.rotation_euler[1] + math.radians(90)
        point1 = rotate_y(location, point1, angle)
        point2 = rotate_y(location, point2, angle)
        point3 = rotate_y(location, point3, angle)
        point4 = rotate_y(location, point4, angle)
        point5 = rotate_y(location, point5, angle)
        point6 = rotate_y(location, point6, angle)
        point7 = rotate_y(location, point7, angle)
        point8 = rotate_y(location, point8, angle)

        angle = object.rotation_euler[2]
        point1 = rotate_z(location, point1, angle)
        point2 = rotate_z(location, point2, angle)
        point3 = rotate_z(location, point3, angle)
        point4 = rotate_z(location, point4, angle)
        point5 = rotate_z(location, point5, angle)
        point6 = rotate_z(location, point6, angle)
        point7 = rotate_z(location, point7, angle)
        point8 = rotate_z(location, point8, angle)

        point1 = transform3D(point1, location, center_loc)
        point2 = transform3D(point2, location, center_loc)
        point3 = transform3D(point3, location, center_loc)
        point4 = transform3D(point4, location, center_loc)
        point5 = transform3D(point5, location, center_loc)
        point6 = transform3D(point6, location, center_loc)
        point7 = transform3D(point7, location, center_loc)
        point8 = transform3D(point8, location, center_loc)

        # location_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, location)

        # X
        # if self._operation == "MIRROR_X":
        glEnable(GL_BLEND)
        glBegin(GL_QUADS)
        glColor4f(0.863, 0, 0, 0.7)

        # if get_preferences().Hops_mirror_direction == "+":

        points = [point1, point2, point3, point4]
        self.center_point_x_p = centroid(points)

        self.point1x = scale(self.center_point_x_p, point1, scale_value)
        self.point2x = scale(self.center_point_x_p, point2, scale_value)
        self.point3x = scale(self.center_point_x_p, point3, scale_value)
        self.point4x = scale(self.center_point_x_p, point4, scale_value)

        self.points_x_p = [self.point1x, self.point2x, self.point3x, self.point4x]
        self.points_x_p_region = []
        for p in self.points_x_p:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_x_p_region.append(p)

        glVertex2f(self.points_x_p_region[0][0], self.points_x_p_region[0][1])
        glVertex2f(self.points_x_p_region[1][0], self.points_x_p_region[1][1])
        glVertex2f(self.points_x_p_region[2][0], self.points_x_p_region[2][1])
        glVertex2f(self.points_x_p_region[3][0], self.points_x_p_region[3][1])

        points = [point5, point6, point7, point8]
        self.center_point_x_n = centroid(points)

        self.point5x = scale(self.center_point_x_n, point5, scale_value)
        self.point6x = scale(self.center_point_x_n, point6, scale_value)
        self.point7x = scale(self.center_point_x_n, point7, scale_value)
        self.point8x = scale(self.center_point_x_n, point8, scale_value)

        self.points_x_n = [self.point5x, self.point6x, self.point7x, self.point8x]
        self.points_x_n_region = []
        for p in self.points_x_n:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_x_n_region.append(p)

        glVertex2f(self.points_x_n_region[0][0], self.points_x_n_region[0][1])
        glVertex2f(self.points_x_n_region[1][0], self.points_x_n_region[1][1])
        glVertex2f(self.points_x_n_region[2][0], self.points_x_n_region[2][1])
        glVertex2f(self.points_x_n_region[3][0], self.points_x_n_region[3][1])

        glEnd()

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0, 0, 0, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_x_p_region[0][0], self.points_x_p_region[0][1])
        glVertex2f(self.points_x_p_region[1][0], self.points_x_p_region[1][1])
        glVertex2f(self.points_x_p_region[2][0], self.points_x_p_region[2][1])
        glVertex2f(self.points_x_p_region[3][0], self.points_x_p_region[3][1])
        glEnd()
        glEnable(GL_BLEND)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_x_n_region[0][0], self.points_x_n_region[0][1])
        glVertex2f(self.points_x_n_region[1][0], self.points_x_n_region[1][1])
        glVertex2f(self.points_x_n_region[2][0], self.points_x_n_region[2][1])
        glVertex2f(self.points_x_n_region[3][0], self.points_x_n_region[3][1])
        glEnd()

        # Z

        # if self._operation == "MIRROR_Y":
        glEnable(GL_BLEND)
        glBegin(GL_QUADS)
        glColor4f(0, 0, 0.863, 0.7)
        # if get_preferences().Hops_mirror_direction == "+":

        points = [point3, point7, point8, point4]
        self.center_point_z_p = centroid(points)

        self.point3z = scale(self.center_point_z_p, point3, scale_value)
        self.point7z = scale(self.center_point_z_p, point7, scale_value)
        self.point8z = scale(self.center_point_z_p, point8, scale_value)
        self.point4z = scale(self.center_point_z_p, point4, scale_value)

        self.points_z_p = [self.point3z, self.point7z, self.point8z, self.point4z]
        self.points_z_p_region = []
        for p in self.points_z_p:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_z_p_region.append(p)

        glVertex2f(self.points_z_p_region[0][0], self.points_z_p_region[0][1])
        glVertex2f(self.points_z_p_region[1][0], self.points_z_p_region[1][1])
        glVertex2f(self.points_z_p_region[2][0], self.points_z_p_region[2][1])
        glVertex2f(self.points_z_p_region[3][0], self.points_z_p_region[3][1])

        points = [point5, point1, point2, point6]
        self.center_point_z_n = centroid(points)

        self.point5z = scale(self.center_point_z_n, point5, scale_value)
        self.point1z = scale(self.center_point_z_n, point1, scale_value)
        self.point2z = scale(self.center_point_z_n, point2, scale_value)
        self.point6z = scale(self.center_point_z_n, point6, scale_value)

        self.points_z_n = [self.point5z, self.point1z, self.point2z, self.point6z]
        self.points_z_n_region = []
        for p in self.points_z_n:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_z_n_region.append(p)

        glVertex2f(self.points_z_n_region[0][0], self.points_z_n_region[0][1])
        glVertex2f(self.points_z_n_region[1][0], self.points_z_n_region[1][1])
        glVertex2f(self.points_z_n_region[2][0], self.points_z_n_region[2][1])
        glVertex2f(self.points_z_n_region[3][0], self.points_z_n_region[3][1])

        glEnd()

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0, 0, 0, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_z_p_region[0][0], self.points_z_p_region[0][1])
        glVertex2f(self.points_z_p_region[1][0], self.points_z_p_region[1][1])
        glVertex2f(self.points_z_p_region[2][0], self.points_z_p_region[2][1])
        glVertex2f(self.points_z_p_region[3][0], self.points_z_p_region[3][1])
        glEnd()
        glEnable(GL_BLEND)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_z_n_region[0][0], self.points_z_n_region[0][1])
        glVertex2f(self.points_z_n_region[1][0], self.points_z_n_region[1][1])
        glVertex2f(self.points_z_n_region[2][0], self.points_z_n_region[2][1])
        glVertex2f(self.points_z_n_region[3][0], self.points_z_n_region[3][1])
        glEnd()

        # Y
        # if self._operation == "MIRROR_Z":
        glEnable(GL_BLEND)
        glBegin(GL_QUADS)
        glColor4f(0, 0.863, 0, 0.7)
        # if get_preferences().Hops_mirror_direction == "+":

        points = [point3, point2, point6, point7]
        self.center_point_y_p = centroid(points)

        self.point3y = scale(self.center_point_y_p, point3, scale_value)
        self.point2y = scale(self.center_point_y_p, point2, scale_value)
        self.point6y = scale(self.center_point_y_p, point6, scale_value)
        self.point7y = scale(self.center_point_y_p, point7, scale_value)

        self.points_y_p = [self.point3y, self.point2y, self.point6y, self.point7y]
        self.points_y_p_region = []
        for p in self.points_y_p:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_y_p_region.append(p)

        glVertex2f(self.points_y_p_region[0][0], self.points_y_p_region[0][1])
        glVertex2f(self.points_y_p_region[1][0], self.points_y_p_region[1][1])
        glVertex2f(self.points_y_p_region[2][0], self.points_y_p_region[2][1])
        glVertex2f(self.points_y_p_region[3][0], self.points_y_p_region[3][1])

        # else:
        points = [point8, point5, point1, point4]
        self.center_point_y_n = centroid(points)

        self.point8y = scale(self.center_point_y_n, point8, scale_value)
        self.point5y = scale(self.center_point_y_n, point5, scale_value)
        self.point1y = scale(self.center_point_y_n, point1, scale_value)
        self.point4y = scale(self.center_point_y_n, point4, scale_value)

        self.points_y_n = [self.point8y, self.point5y, self.point1y, self.point4y]
        self.points_y_n_region = []
        for p in self.points_y_n:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            self.points_y_n_region.append(p)

        glVertex2f(self.points_y_n_region[0][0], self.points_y_n_region[0][1])
        glVertex2f(self.points_y_n_region[1][0], self.points_y_n_region[1][1])
        glVertex2f(self.points_y_n_region[2][0], self.points_y_n_region[2][1])
        glVertex2f(self.points_y_n_region[3][0], self.points_y_n_region[3][1])

        glEnd()

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0, 0, 0, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_y_p_region[0][0], self.points_y_p_region[0][1])
        glVertex2f(self.points_y_p_region[1][0], self.points_y_p_region[1][1])
        glVertex2f(self.points_y_p_region[2][0], self.points_y_p_region[2][1])
        glVertex2f(self.points_y_p_region[3][0], self.points_y_p_region[3][1])
        glEnd()
        glEnable(GL_BLEND)
        glBegin(GL_LINE_LOOP)
        glVertex2f(self.points_y_n_region[0][0], self.points_y_n_region[0][1])
        glVertex2f(self.points_y_n_region[1][0], self.points_y_n_region[1][1])
        glVertex2f(self.points_y_n_region[2][0], self.points_y_n_region[2][1])
        glVertex2f(self.points_y_n_region[3][0], self.points_y_n_region[3][1])
        glEnd()

        region = context.region
        rv3d = get_rv3d(self, context)
        self.center_point_x_p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_x_p)
        self.center_point_x_n = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_x_n)
        self.center_point_y_p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_y_p)
        self.center_point_y_n = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_y_n)
        self.center_point_z_p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_z_p)
        self.center_point_z_n = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, self.center_point_z_n)

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0.863, 0, 0, 0.7)
        glBegin(GL_LINES)
        glVertex2f(self.center_point_x_p[0], self.center_point_x_p[1])
        glVertex2f(self.center_point_x_n[0], self.center_point_x_n[1])
        glEnd()

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0, 0.863, 0, 0.7)
        glBegin(GL_LINES)
        glVertex2f(self.center_point_y_p[0], self.center_point_y_p[1])
        glVertex2f(self.center_point_y_n[0], self.center_point_y_n[1])
        glEnd()

        glEnable(GL_BLEND)
        glLineWidth(1)
        glColor4f(0, 0, 0.863, 0.7)
        glBegin(GL_LINES)
        glVertex2f(self.center_point_z_p[0], self.center_point_z_p[1])
        glVertex2f(self.center_point_z_n[0], self.center_point_z_n[1])
        glEnd()

        all_3d_pints = [point1, point2, point3, point4, point5, point6, point7, point8]
        all_2d_pints = []
        for p in all_3d_pints:
            p = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, p)
            all_2d_pints.append(p)

        all_2d_pints_x = []
        all_2d_pints_y = []
        for v in all_2d_pints:
            all_2d_pints_x.append(v.x)
            all_2d_pints_y.append(v.y)

        point9 = [min(all_2d_pints_x), min(all_2d_pints_y)]
        mirror_interface_scale = get_preferences().Hops_mirror_modal_Interface_scale
        square_size = 30*mirror_interface_scale
        square_space_x = 40*mirror_interface_scale
        square_space_y = 60*mirror_interface_scale

        self.quad1 = [(point9[0] - square_size, point9[1]), (point9[0]-square_size, point9[1]+square_size), (point9[0], point9[1]+square_size), (point9[0], point9[1])]
        self.quad2 = [(point9[0] - square_size - square_space_x, point9[1]), (point9[0] - square_size - square_space_x, point9[1]+square_size), (point9[0] - square_space_x, point9[1]+square_size), (point9[0] - square_space_x, point9[1])]
        self.quad3 = [(point9[0] - square_size - square_space_x*2, point9[1]), (point9[0] - square_size - square_space_x*2, point9[1]+square_size), (point9[0] - square_space_x*2, point9[1]+square_size), (point9[0] - square_space_x*2, point9[1])]
        self.quad4 = [(point9[0] - square_size - square_space_x*3, point9[1]), (point9[0] - square_size - square_space_x*3, point9[1]+square_size), (point9[0] - square_space_x*3, point9[1]+square_size), (point9[0] - square_space_x*3, point9[1])]

        self.quad5 = [(point9[0] - square_size - square_space_x*2, point9[1] - square_space_y), (point9[0] - square_size - square_space_x*2, point9[1]+square_size - square_space_y), (point9[0] - square_space_x*2, point9[1]+square_size - square_space_y), (point9[0] - square_space_x*2, point9[1] - square_space_y)]
        self.quad6 = [(point9[0] - square_size - square_space_x*3, point9[1] - square_space_y), (point9[0] - square_size - square_space_x*3, point9[1]+square_size - square_space_y), (point9[0] - square_space_x*3, point9[1]+square_size - square_space_y), (point9[0] - square_space_x*3, point9[1] - square_space_y)]

        if self.multiselection is False:

            glEnable(GL_BLEND)
        
            glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad1[0][0], self.quad1[0][1])
            glVertex2f(self.quad1[1][0], self.quad1[1][1])
            glVertex2f(self.quad1[2][0], self.quad1[2][1])
            glVertex2f(self.quad1[3][0], self.quad1[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modes == "SYMMETRY":
                draw_text("symmetry", self.quad4[0][0]+4, self.quad4[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.29, 0.52, 1.0, 0.9)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad2[0][0], self.quad2[0][1])
            glVertex2f(self.quad2[1][0], self.quad2[1][1])
            glVertex2f(self.quad2[2][0], self.quad2[2][1])
            glVertex2f(self.quad2[3][0], self.quad2[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modes == "BISECT":
                draw_text("bisect", self.quad4[0][0]+4, self.quad4[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.29, 0.52, 1.0, 0.9)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad3[0][0], self.quad3[0][1])
            glVertex2f(self.quad3[1][0], self.quad3[1][1])
            glVertex2f(self.quad3[2][0], self.quad3[2][1])
            glVertex2f(self.quad3[3][0], self.quad3[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modes == "MODIFIER":
                draw_text("modifier", self.quad4[0][0]+4, self.quad4[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.29, 0.52, 1.0, 0.9)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad4[0][0], self.quad4[0][1])
            glVertex2f(self.quad4[1][0], self.quad4[1][1])
            glVertex2f(self.quad4[2][0], self.quad4[2][1])
            glVertex2f(self.quad4[3][0], self.quad4[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modal_use_cursor:
                draw_text("via cursor", self.quad6[0][0]+4, self.quad6[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.49, 0.32, 1.0, 0.9)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad5[0][0], self.quad5[0][1])
            glVertex2f(self.quad5[1][0], self.quad5[1][1])
            glVertex2f(self.quad5[2][0], self.quad5[2][1])
            glVertex2f(self.quad5[3][0], self.quad5[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modal_use_cursor is False:
                draw_text("via origin", self.quad6[0][0]+4, self.quad6[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.49, 0.32, 1.0, 0.9)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad6[0][0], self.quad6[0][1])
            glVertex2f(self.quad6[1][0], self.quad6[1][1])
            glVertex2f(self.quad6[2][0], self.quad6[2][1])
            glVertex2f(self.quad6[3][0], self.quad6[3][1])
            glEnd()

        else:

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modes_multi == "VIA_ACTIVE":
                draw_text("mirror across active", self.quad4[0][0]+4, self.quad4[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.35, 1, 0.29, 0.53)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad4[0][0], self.quad4[0][1])
            glVertex2f(self.quad4[1][0], self.quad4[1][1])
            glVertex2f(self.quad4[2][0], self.quad4[2][1])
            glVertex2f(self.quad4[3][0], self.quad4[3][1])
            glEnd()

            glEnable(GL_BLEND)
            if get_preferences().Hops_mirror_modes_multi == "SYMMETRY":
                draw_text("Symmetry", self.quad4[0][0]+4, self.quad4[0][1]-14, align="LEFT", size=10, color=(1, 1, 1, 1))
                glColor4f(0.35, 1, 0.29, 0.53)
            else:
                glColor4f(0.1, 0.1, 0.1, 0.6)
            glBegin(GL_QUADS)
            glVertex2f(self.quad3[0][0], self.quad3[0][1])
            glVertex2f(self.quad3[1][0], self.quad3[1][1])
            glVertex2f(self.quad3[2][0], self.quad3[2][1])
            glVertex2f(self.quad3[3][0], self.quad3[3][1])
            glEnd()
