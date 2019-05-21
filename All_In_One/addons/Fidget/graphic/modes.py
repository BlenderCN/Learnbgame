import bpy
from bgl import *
import math
from mathutils import Vector
from .. preferences import get_preferences
from .. utils.region import scale, inside_polygon, rotate
from .. utils.drawing import set_color


def draw_mode1(self, context):

    center = Vector((35.0, 21.0))

    origin = 0, 0
    value = get_preferences().fidget_manimulator_scale + get_preferences().fidget_manimulator_dots_scale
    angle = math.radians(get_preferences().fidget_manimulator_rotation)
    center = scale(origin, center, value)
    center = rotate(origin, center, angle)
    center = center[0] + self.center[0], center[1] + self.center[1]

    radius = get_preferences().fidget_manimulator_radius
    amount = 36

    self.list = calc_circle_pints(center, radius, amount)

    polygon = []
    for x, y in zip(self.list[0], self.list[1]):
        polygon.append([x, y])

    if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], polygon):

        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode1_color_hover)
        glColor4f(bgR, bgG, bgB, bgA)
        self.is_over_mode1 = True
    else:
        self.is_over_mode1 = False
        if get_preferences().mode == "MODE1":
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode1_color_hover)
            glColor4f(bgR, bgG, bgB, bgA)
        else:
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode1_color)
            glColor4f(bgR, bgG, bgB, bgA)

    polygon[:] = []

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    glBegin(GL_TRIANGLE_FAN)

    for x, y in zip(self.list[0], self.list[1]):
        glVertex2f(x, y)

    glEnd()

    if get_preferences().fidget_enable_outline:
        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_outline)
        glColor4f(bgR, bgG, bgB, bgA)

        glLineWidth(get_preferences().fidget_outline_width)

        glBegin(GL_LINE_LOOP)

        for x, y in zip(self.list[0], self.list[1]):
            glVertex2f(x, y)

        glEnd()

    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)


def draw_mode2(self, context):

    center = Vector((-35.0, 21.0))

    origin = 0, 0
    value = get_preferences().fidget_manimulator_scale + get_preferences().fidget_manimulator_dots_scale
    angle = math.radians(get_preferences().fidget_manimulator_rotation)
    center = scale(origin, center, value)
    center = rotate(origin, center, angle)
    center = center[0] + self.center[0], center[1] + self.center[1]

    radius = get_preferences().fidget_manimulator_radius
    amount = 36

    self.list = calc_circle_pints(center, radius, amount)

    polygon = []
    for x, y in zip(self.list[0], self.list[1]):
        polygon.append([x, y])

    if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], polygon):
        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode2_color_hover)
        glColor4f(bgR, bgG, bgB, bgA)
        self.is_over_mode2 = True
    else:
        self.is_over_mode2 = False
        if get_preferences().mode == "MODE2":
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode2_color_hover)
            glColor4f(bgR, bgG, bgB, bgA)
        else:
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode2_color)
            glColor4f(bgR, bgG, bgB, bgA)

    polygon[:] = []

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    glBegin(GL_TRIANGLE_FAN)

    for x, y in zip(self.list[0], self.list[1]):
        glVertex2f(x, y)

    glEnd()

    if get_preferences().fidget_enable_outline:
        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_outline)
        glColor4f(bgR, bgG, bgB, bgA)

        glLineWidth(get_preferences().fidget_outline_width)

        glBegin(GL_LINE_LOOP)

        for x, y in zip(self.list[0], self.list[1]):
            glVertex2f(x, y)

        glEnd()

    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)


def draw_mode3(self, context):

    center = Vector((0.0, -40.0))

    origin = 0, 0
    value = get_preferences().fidget_manimulator_scale + get_preferences().fidget_manimulator_dots_scale
    angle = math.radians(get_preferences().fidget_manimulator_rotation)
    center = scale(origin, center, value)
    center = rotate(origin, center, angle)
    center = center[0] + self.center[0], center[1] + self.center[1]

    radius = get_preferences().fidget_manimulator_radius
    amount = 36

    self.list = calc_circle_pints(center, radius, amount)

    polygon = []
    for x, y in zip(self.list[0], self.list[1]):
        polygon.append([x, y])

    if inside_polygon(self.mouse_pos[0], self.mouse_pos[1], polygon):
        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode3_color_hover)
        glColor4f(bgR, bgG, bgB, bgA)
        self.is_over_mode3 = True
    else:
        self.is_over_mode3 = False
        if get_preferences().mode == "MODE3":
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode3_color_hover)
            glColor4f(bgR, bgG, bgB, bgA)
        else:
            bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_mode3_color)
            glColor4f(bgR, bgG, bgB, bgA)

    polygon[:] = []

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    glBegin(GL_TRIANGLE_FAN)

    for x, y in zip(self.list[0], self.list[1]):
        glVertex2f(x, y)

    glEnd()

    if get_preferences().fidget_enable_outline:
        bgR, bgG, bgB, bgA = set_color(get_preferences().fidget_outline)
        glColor4f(bgR, bgG, bgB, bgA)

        glLineWidth(get_preferences().fidget_outline_width)

        glBegin(GL_LINE_LOOP)

        for x, y in zip(self.list[0], self.list[1]):
            glVertex2f(x, y)

        glEnd()

    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)


def calc_circle_pints(center, radius, amount):
    list_dx = []
    list_dy = []

    x_offset, y_offset = center
    angle = math.radians(360 / amount)
    for i in range(amount):
        list_dx.append(math.cos(i*angle) * radius + x_offset)
        list_dy.append(math.sin(i*angle) * radius + y_offset)

    return list_dx, list_dy
