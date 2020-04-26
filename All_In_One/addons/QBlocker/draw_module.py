import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from .help_text import *


mouseXoffset = 40

def draw_callback_cube(self, op, context, _uidpi, _uifactor):
    blf.size(0, 14, _uidpi)
    DrawHelp(helpstring_box, _uifactor)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    else:
        BoolDraw(op.mouse_pos, -40, op.isOriented, "Align", "Oriented", "Axis", _uifactor)
        BoolDraw(op.mouse_pos, -20, op.qObject.isFlat, "Mesh", "Plane", "Cube", _uifactor)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 40, _uifactor)


def draw_callback_cylinder(self, op, context, _uidpi, _uifactor):
    blf.size(0, 14, _uidpi)
    DrawHelp(helpstring_cylinder, _uifactor)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    elif op.segkeyHold:
        SliderDraw(op, context, op.qObject.meshSegments)

    else:
        BoolDraw(op.mouse_pos, -40, op.isOriented, "Align", "Oriented", "Axis", _uifactor)
        BoolDraw(op.mouse_pos, -20, op.qObject.isFlat, "Mesh", "Circle", "Cylinder", _uifactor)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor)
        NumberDraw(op.meshSegments, op.mouse_pos, "Segments", 40, _uifactor)
        BoolDraw(op.mouse_pos, 60, op.qObject.isSmooth, "Shading", "Smooth", "Flat", _uifactor)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 80, _uifactor)


def draw_callback_sphere(self, op, context, _uidpi, _uifactor):
    blf.size(0, 14, _uidpi)
    DrawHelp(helpstring_sphere, _uifactor)

    if op.snapSegHold:
        SliderDraw(op, context, op.snapClass.edgediv)

    elif op.segkeyHold:
        SliderDraw(op, context, op.qObject.meshSegments)

    else:
        BoolDraw(op.mouse_pos, -20, op.isOriented, "Align", "Oriented", "Axis", _uifactor)
        GroundTypeDraw(op.qObject.basetype, op.mouse_pos, 0, True, _uifactor)
        BoolDraw(op.mouse_pos, 20, op.qObject.isCentered, "Origin", "Center", "Base", _uifactor)
        NumberDraw(op.meshSegments, op.mouse_pos, "Segments", 40, _uifactor)
        BoolDraw(op.mouse_pos, 60, op.qObject.isSmooth, "Shading", "Smooth", "Flat", _uifactor)
        NumberDraw(op.snapClass.edgediv, op.mouse_pos, "Snap Div", 80, _uifactor)


def DrawHelp(htext, _uifactor):
    textsize = 14
    # blf.size(0, textsize, 72)
    # get leftbottom corner
    offset = textsize + 40
    columnoffs = 320 * _uifactor
    for line in reversed(htext):
        blf.color(0, 1.0, 1.0, 1.0, 1.0)
        blf.position(0, 60 * _uifactor, offset, 0)
        blf.draw(0, line[0])

        blf.color(0, 1.0, 0.86, 0.0, 1.0)
        textdim = blf.dimensions(0, line[1])
        coloffset = columnoffs - textdim[0]
        blf.position(0, coloffset, offset, 0)
        blf.draw(0, line[1])
        offset += 20 * _uifactor


def BoolDraw(pos, offset, value, textname, text1, text2, _uifactor):
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    offsetfac = offset * _uifactor
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, textname)
    blf.color(0, 1.0, 0.86, 0.0, 1.0)
    textToDraw = text1 if value else text2
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


def NumberDraw(value, pos, text, offset, _uifactor):
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    offsetfac = offset * _uifactor
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, text)
    blf.color(0, 1.0, 0.86, 0.0, 1.0)
    textToDraw = str(value)
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


def GroundTypeDraw(basetype, pos, offset, active, _uifactor):
    offsetfac = offset * _uifactor
    if active:
        blf.color(0, 1.0, 1.0, 1.0, 1.0)
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    blf.position(0, pos[0] + mouseXoffset, pos[1] - offsetfac, 0)
    blf.draw(0, "BaseType")
    if active:
        blf.color(0, 1.0, 0.86, 0.0, 1.0)
    else:
        blf.color(0, 0.5, 0.5, 0.5, 0.5)
    # set matching text
    if basetype == 1:
        textToDraw = "Corners"
    elif basetype == 2:
        textToDraw = "Midpoint"
    elif basetype == 3:
        textToDraw = "Uniform"
    elif basetype == 4:
        textToDraw = "Uniform all"
    textdim = blf.dimensions(0, textToDraw)
    Roffset = (180 * _uifactor) - textdim[0]
    blf.position(0, pos[0] + 20 + Roffset, pos[1] - offsetfac, 0)
    blf.draw(0, textToDraw)


# draw Slider
def SliderDraw(op, context, value):
    bgl.glLineWidth(2)

    x = op.mouseStart[0]
    x2 = op.mouseEnd_x
    y = op.mouseStart[1]
    ytop = op.mouseStart[1] + 15

    with gpu.matrix.push_pop():
        coords = [(x, ytop), (x, y), (x, y), (x2, y), (x2, y), (x2, ytop)]
        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        batch.draw(shader)

    # draw segments text
    textToDraw = str(value)
    blf.position(0, op.mouseEnd_x + 2, op.mouseStart[1] + 3, 0)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.draw(0, textToDraw)
