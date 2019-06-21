import bpy
import sys

from . import blut
from . import ut

from bpy_extras.io_utils import ExportHelper

from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.props import FloatProperty
from bpy.types import Operator


svgUnit = 'cm'
svgCoord = 'XY'
svgCoordIdx = 0
svgStrokeWidth = 0.1


def coordNameToIdx(coord):
    if coord == 'XY':
        return 0
    if coord == 'YZ':
        return 1
    if coord == 'XZ':
        return 2
    return 0

def setCoord(coord):
    global svgCoord
    global svgCoordIdx
    svgCoord = coord
    svgCoordIdx = coordNameToIdx(coord)

def adjustCoord(v):
    if svgCoordIdx == 0:
        return [v[0], -v[1]]
    if svgCoordIdx == 1:
        return [v[1], -v[2]]
    if svgCoordIdx == 2:
        return [v[0], -v[2]]
    return v

def isMesh(obj):
    return obj.type == 'MESH'

def isCurve(obj):
    return obj.type == 'CURVE'

def isSupportedType(obj):
    if isCurve(obj):
        return True
    if isMesh(obj):
        return True
    return False

def expandMs(bb, obj):
    ms = blut.getModifiedMesh(obj)
    for v in ms.vertices:
        bb.expand(adjustCoord(blut.getVertPosW(obj, v)))

def expandCurve(bb, obj):
    cv = obj.data
    for spl in cv.splines:
        for v in spl.points:
            bb.expand(adjustCoord(blut.getVertPosWSP(obj, v)))

def getBoundingBox(objects):
    bb = ut.BBox2D()
    for obj in objects:
        if isMesh(obj):
            expandMs(bb, obj)
        elif isCurve(obj):
            expandCurve(bb, obj)
    return bb

def svgParam(name, val):
    return '{0}="{1}"'.format(name, val)

def beginSVG(f, objects):
    bb = getBoundingBox(objects)
    rw = bb.getW(0)
    rh = bb.getW(1)
    f.write('<svg\n')
    f.write('  xmlns="http://www.w3.org/2000/svg"\n')
    f.write('  xmlns:xlink="http://www.w3.org/1999/xlink"\n')
    f.write('  width="{0}{2}" height="{1}{2}"\n'.format(rw, rh, svgUnit))
    f.write('  viewBox="{0} {1} {2} {3}">\n'.format(0, 0, rw, rh))

def endSVG(f):
    f.write('</svg>\n')

def beginGroup(f):
    f.write('<g\n')
    f.write('  fill="none"\n')
    f.write('  stroke="black"\n')
    f.write('  stroke-width="' + str(svgStrokeWidth) + '"\n')
    f.write('  stroke-linecap="round"\n')
    f.write('>\n')

def endGroup(f):
    f.write('</g>\n')

def writeLine(f, v0, v1):
    vv0 = adjustCoord(v0)
    vv1 = adjustCoord(v1)
    s = '<line'
    s += ' ' + svgParam('x1', vv0[0])
    s += ' ' + svgParam('y1', vv0[1])
    s += ' ' + svgParam('x2', vv1[0])
    s += ' ' + svgParam('y2', vv1[1])
    s += '/>\n'
    f.write(s)

def writeMeshStrokes(f, obj):
    ms = blut.getModifiedMesh(obj)
    for e in ms.edges:
        v0 = ms.vertices[e.vertices[0]]
        v1 = ms.vertices[e.vertices[1]]
        vp0 = blut.getVertPosW(obj, v0)
        vp1 = blut.getVertPosW(obj, v1)
        writeLine(f, vp0, vp1)

def writeSpline(f, obj, spl):
    if len(spl.points) == 0:
        return
    s = ''
    if spl.use_cyclic_u:
        s += '<polygon'
    else:
        s += '<polyline'
    s += ' points="'
    for v in spl.points:
        p = blut.getVertPosWSP(obj, v)
        pc = adjustCoord(p)
        s += ' ' + str(pc[0]) + ' ' + str(pc[1])
    s += '"/>\n'
    f.write(s)

def writeCurveStrokes(f, obj):
    cv = obj.data
    for spl in cv.splines:
        writeSpline(f, obj, spl)

def writeMeshPath(f, obj):
    beginGroup(f)
    writeMeshStrokes(f, obj)
    endGroup(f)

def writeCurvePath(f, obj):
    beginGroup(f)
    writeCurveStrokes(f, obj)
    endGroup(f)

def writeObject(f, obj):
    if isMesh(obj):
        writeMeshPath(f, obj)
    elif isCurve(obj):
        writeCurvePath(f, obj)

def getTarget(sel_only):
    s = []
    for obj in bpy.data.objects:
        if not isSupportedType(obj):
            continue
        if sel_only:
            if not obj.select:
                continue
        s.append(obj)
    return s

def saveSVGMain(f, sel_only):
    objects = getTarget(sel_only)
    beginSVG(f, objects)
    for obj in objects:
        writeObject(f, obj)
    endSVG(f)

def writeSVG(context, filepath, sel_only, unit, coord, strokeWidth):
    global svgUnit
    global svgStrokeWidth
    svgUnit = unit
    svgStrokeWidth = strokeWidth
    setCoord(coord)
    f = open(filepath, 'w', encoding='utf-8')
    try:
        saveSVGMain(f, sel_only)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        f.close()
        raise
    f.close()
    return {'FINISHED'}


class FKHD_IO_ExportSvgPath(Operator, ExportHelper):
    """Export strokes to SVG"""
    bl_idname = "fkhd.fkhd_io_export_svg_path"
    bl_label = "Export strokes to SVG"

    filename_ext = ".svg"

    filter_glob = StringProperty(
            default = "*.svg",
            options = {'HIDDEN'},
            maxlen = 255,
            )

    sel_only = BoolProperty(
            name = "Select only",
            description = "Select only",
            default = True,
            )

    unit = EnumProperty(
            name="Unit",
            description="Export unit",
            items=(('cm', "cm", "cm"),
                   ('mm', "mm", "mm")),
            default='cm',
            )

    coord = EnumProperty(
            name="Coordinate",
            description="Export coordination",
            items=(('XY', "XY", "XY"),
                   ('YZ', "YZ", "YZ"),
                   ('XZ', "XZ", "XZ")),
            default='XY',
            )

    strokeWidth = FloatProperty(
            name="Stroke width",
            description="Stroke width",
            default=0.1,
            )

    def execute(self, context):
        return writeSVG(context, self.filepath, self.sel_only, self.unit, self.coord, self.strokeWidth)

def fkhd_menu_svgpath_export(self, context):
    self.layout.operator(FKHD_IO_ExportSvgPath.bl_idname, text="Export strokes to SVG")

def regOps(reg):
    if reg:
        bpy.utils.register_class(FKHD_IO_ExportSvgPath)
        bpy.types.INFO_MT_file_export.append(fkhd_menu_svgpath_export)
    else:
        bpy.utils.unregister_class(FKHD_IO_ExportSvgPath)
        bpy.types.INFO_MT_file_export.remove(fkhd_menu_svgpath_export)
