#
#
# Main module of Blender Stroke Font add-on.
# The stroke font xml files are assumed to be in the strokefontdata subdirectory.
#
# Supported Blender Version: 2.8 Beta
#
# Copyright (C) 2019  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/blenderstrokefont/blob/master/LICENSE)
#
# Not yet pep8 compliant 

import os, sys, re, math
from mathutils import Vector, Matrix
from xml.dom.minidom import parse, Document
import bpy, bmesh

from . stroke_font_manager import getFontNames, FontData, CharData, DrawContext

DEF_ERR_MARGIN = 0.0001

def getfontNameList(scene, context):
    if(getfontNameList.fontNames != None):
        return getfontNameList.fontNames

    parentPath = os.path.dirname(__file__)
    getfontNameList.fontNames = [(n, n, n) for n in getFontNames(parentPath)]

    return getfontNameList.fontNames

#Called too many times, so cache
getfontNameList.fontNames = None

def subdivide(bm, subdivCnt, w, h):    
    wIncr = w / subdivCnt 
    hIncr = h / subdivCnt

    wStart = -w/2
    hStart = -h/2

    for i in range(1, subdivCnt):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], \
            plane_co=(wStart + wIncr * i, 0,0), plane_no=Vector((1,0,0)))
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], \
            plane_co=(0, hStart + hIncr * i, 0), plane_no=Vector((0, 1,0)))
    
def createPlane(leftTop, bottomRight, collection):
    z = leftTop[2] #z is same for both
    w = bottomRight[0] - leftTop[0]
    h = leftTop[1] - bottomRight[1]
    
    bm = bmesh.new()
    v0 = bm.verts.new((-w/2, -h/2, 0))
    v1 = bm.verts.new((w/2, -h/2, 0))
    v2 = bm.verts.new((-w/2, h/2, 0))
    v3 = bm.verts.new((w/2, h/2, 0))
    
    bm.faces.new((v0, v1, v3, v2))

    subdivide(bm, subdivCnt = 50, w = w, h = h)
    
    me   = bpy.data.meshes.new('plane')
    bm.to_mesh(me)
    bm.free()

    obj   = bpy.data.objects.new('plane', me)
    collection.objects.link(obj)
    obj.location = (leftTop[0] + w / 2, bottomRight[1] + h / 2, z)
    
    return obj
          
def main(context, rectangles = None):
    params = context.window_manager.AddStrokeFontTextParams
    
    action = params.action    
    text = params.text
    filePath = bpy.path.abspath(params.filePath)

    fontName = params.fontName
    fontSize = params.fontSize

    charSpacing = params.charSpacing
    lineSpacing = params.lineSpacing        
    copyPropObj = params.copyPropertiesCurve

    try:
        if(params.copyPropertiesCurve != None):
            params.copyPropertiesCurve.data
    except:
        params.copyPropertiesCurve = None
    

    cloneGlyphs = params.cloneGlyphs
    confined = params.confined
    width = params.width
    height = params.height
    margin = params.margin
    hAlignment = params.hAlignment
    vAlignment = params.vAlignment
    expandDir = None if params.expandDir == 'none' else params.expandDir
    expandDist = params.expandDist
    addPlane = params.addPlane
    
    return addText(fontName, fontSize, charSpacing, lineSpacing, copyPropObj, text, \
        cloneGlyphs, action, filePath, confined, width, height, margin, hAlignment, \
            vAlignment, expandDir, expandDist, rectangles, addPlane)

#Default options if called from writing animation
def addText(fontName, fontSize, charSpacing, lineSpacing, copyPropObj, text, cloneGlyphs, \
    action = 'addInputText', filePath = None, confined = False, width = None, height = None, \
        margin = None, hAlignment = None, vAlignment = None, expandDir = None, \
            expandDist  = None, rectangles = None, addPlane = None):        
    
    parentPath = os.path.dirname(__file__)
    
    bevelDepth = 0.01 * fontSize
    
    renderer = BlenderFontRenderer(copyPropObj, bevelDepth, cloneGlyphs)

    context = DrawContext(parentPath, fontName, fontSize, charSpacing, lineSpacing, 
        BlenderCharDataFactory(), renderer, bottomToTop = True) 
    
    if(action == "addGlyphTable"):
        context.renderGlyphTable()
        
    else:
        if(action == 'addInputText'):
            text = text.replace('\\n','\n').replace('\\\n','\\n')

        elif(action == "addFromFile"):
            try:
                with open(filePath, 'rU') as f: 
                    text = f.read() 
            except:
                return None

        if(text[0] == u'\ufeff'):
            text = text[1:]

        if(rectangles):
            context.renderCharsInSelBoxes(text, rectangles, margin, hAlignment, vAlignment, addPlane)
            
        elif(confined):
            x1, y1, z1 = bpy.context.scene.cursor.location
            x2, y2, z2 = x1 + width, y1 - height, z1
            rectangles = [[Vector((x1, y1, z1)), Vector((x2, y2, z2))]]
            context.renderCharsInSelBoxes(text, rectangles, margin, hAlignment, \
                vAlignment, addPlane, expandDir, expandDist)
        else:
            context.renderCharsWithoutBox(text)
        
    return renderer.collection
        
class BlenderCharData(CharData):
    def __init__(self, char, bbox, rOffset, segs):
        self.char = char
        self.bbox = bbox
        self.rOffset = rOffset
        self.segs = segs
    
    #Implementation of abstract method
    def scaleGlyphPts(self, scale):
        self.bbox[2] *= - 1
        self.bbox[3] *= - 1
        for i, seg in enumerate(self.segs):
            pts = []
            for j in range(0, len(seg)):
                pts.append(complex(seg[j].real * scale, -scale * seg[j].imag))            
                
            self.segs[i] = CubicBezier(*pts)
        
class BlenderCharDataFactory:
    def __init__(self):
        pass
        
    def getCharData(self, char, bbox, rOffset, pathStr):
        segs = parse_path(pathStr)
        return BlenderCharData(char, bbox, rOffset, segs)

class BlenderFontRenderer:
    def __init__(self, copyPropObj, bevelDepth, cloneGlyphs):
        self.copyPropObj = copyPropObj
        self.collection = None
        self.currCollection = None
        self.z = bpy.context.scene.cursor.location[2]
        self.bevelDepth = bevelDepth
        self.currPlane = None
        self.cloneGlyphs = cloneGlyphs
        self.charObjDataCache = {}

    def renderChar(self, charData, x, y, naChar):
        curveData = self.charObjDataCache.get(charData.char)
        curve = CPath().addCurve(charData, self.copyPropObj, curveData, self.cloneGlyphs)
        if(curveData == None):
            self.charObjDataCache[charData.char] = curve.data
            
        self.currCollection.objects.link(curve)
        if(self.copyPropObj == None):
            curve.data.bevel_depth = self.bevelDepth
            curve.data.bevel_resolution = 0
            curve.data.twist_smooth = 0

        curve.location[0] += x
        curve.location[1] += y
        curve.location[2] = self.z
        if(self.currPlane != None):
            curve.parent = self.currPlane
            curve.matrix_parent_inverse = self.currPlane.matrix_world.inverted()
            mod = curve.modifiers.new('mod', type='SHRINKWRAP')
            mod.target = self.currPlane
            mod.offset = -0.001
            
        curve.select_set(False)
        
    def beforeRender(self):
        self.collection = bpy.data.collections.new('StrokeFontText')
        bpy.context.scene.collection.children.link(self.collection)
        self.currCollection = self.collection
    
    def newBoxToBeRendered(self, box, addPlane):        
        self.currCollection = bpy.data.collections.new('StrokeFontTextBox')
        self.collection.children.link(self.currCollection)     
        self.z = box[0][2]
        if(addPlane):
            self.currPlane = createPlane(box[0], box[1], self.currCollection)
            bpy.context.scene.update()        

    
    def moveBoxInYDir(self, moveBy):
        for o in self.currCollection.objects:
            if(o.type == 'CURVE'):
                o.location[1] += moveBy

    def centerInView(self, width, height):          
        pass

    def renderPlainText(self, text, size, x, y, objName):
        myFont = bpy.data.curves.new(type = "FONT", name = objName)
        fontOb = bpy.data.objects.new(objName, myFont)
        fontOb.data.body = text
        self.collection.objects.link(fontOb)
        fontOb.location = Vector((x, y, self.z))
        fontOb.scale = [size, size, 1]

        if(self.copyPropObj != None and \
            len(self.copyPropObj.data.materials) > 0):
            copyMatIdx = self.copyPropObj.active_material_index
            mat = self.copyPropObj.data.materials[copyMatIdx]
            fontOb.data.materials.append(mat)
            fontOb.active_material_index = 0
        
        # ~ return fontOb
        
    def getBoxLeftTopRightBottom(self, box):
        x1 = box[0][0]
        y1 = box[0][1]

        x2 = box[1][0]
        y2 = box[1][1]
        
        return min(x1, x2), max(y1, y2), max(x1, x2), min(y1, y2)
        
    def getBoxFromCoords(self, x1, y1, x2, y2):
        return [Vector((x1, y1, self.z)), Vector((x2, y2, self.z))]
        
    def getDefaultStartLocation(self):
        x, y, z = bpy.context.scene.cursor.location
        return x, y
        
#Avoid errors due to floating point conversions/comparisons
def cmplxCmpWithMargin(complex1, complex2, margin = DEF_ERR_MARGIN):
    return floatCmpWithMargin(complex1.real, complex2.real, margin) and \
        floatCmpWithMargin(complex1.imag, complex2.imag, margin)

def floatCmpWithMargin(float1, float2, margin = DEF_ERR_MARGIN):
    return abs(float1 - float2) < margin 
    
def getDisconnParts(segs):
    prevSeg = None
    disconnParts = []
    newSegs = []
    
    for i in range(0, len(segs)):
        seg = segs[i]
        if((prevSeg== None) or not cmplxCmpWithMargin(prevSeg.end, seg.start)):
            if(len(newSegs) > 0):
                disconnParts.append(Path(newSegs, isClosed = segs[-1].isClosing))
            newSegs = []
        prevSeg = seg
        newSegs.append(seg)

    if(len(segs) > 0 and len(newSegs) > 0):
        disconnParts.append(Path(newSegs, isClosed = newSegs[-1].isClosing))

    return disconnParts

def get3DVector(cmplx, z = 0):
    return Vector((cmplx.real, cmplx.imag, z))


def isBezier(bObj):
    return bObj.type == 'CURVE' and len(bObj.data.splines) > 0 \
        and bObj.data.splines[0].type == 'BEZIER'
            
class CPath:

    def __init__(self):
        pass

    def getNewCurveData(self, charData, copyPropObj):
        segs = charData.segs
        parts = getDisconnParts(segs)
        
        if(copyPropObj != None and isBezier(copyPropObj)):
            newCurveData = copyPropObj.data.copy()
            newCurveData.name = charData.char
            newCurveData.splines.clear()
        else:
            newCurveData = bpy.data.curves.new(charData.char, 'CURVE')
            
        splinesData = []

        for i, part in enumerate(parts):
            splinesData.append(part.getBezierPtsInfo())

        for i, newPoints in enumerate(splinesData):

            spline = newCurveData.splines.new('BEZIER')
            spline.bezier_points.add(len(newPoints)-1)
            spline.use_cyclic_u = parts[i].isClosed
            
            for j in range(0, len(spline.bezier_points)):
                newPoint = newPoints[j]
                spline.bezier_points[j].co = newPoint[0]
                spline.bezier_points[j].handle_left = newPoint[1]
                spline.bezier_points[j].handle_right = newPoint[2]
                spline.bezier_points[j].handle_right_type = 'FREE'

        return newCurveData

    def addCurve(self, charData, copyPropObj, curveData, cloneGlyphs):
        if(curveData == None):
            curveData = self.getNewCurveData(charData, copyPropObj)
        elif(not cloneGlyphs):
            curveData = curveData.copy()
            
        if(copyPropObj != None and isBezier(copyPropObj)):
            obj = copyPropObj.copy()
            obj.name = 't'
            obj.matrix_world = Matrix()
            obj.data = curveData
            if(curveData.shape_keys != None):
                keyblocks = reversed(curveData.shape_keys.key_blocks)
                for sk in keyblocks:
                    obj.shape_key_remove(sk)            
        else:
            obj = bpy.data.objects.new('t', curveData)
        
        curveData.dimensions = '3D'            
        obj.location = (0, 0, 0)
        return obj

#
# The following section is a Python conversion of the javascript
# a2c function at: https://github.com/fontello/svgpath
# (Copyright (C) 2013-2015 by Vitaly Puzrin)
#
######################## a2c start #######################

TAU = math.pi * 2

# eslint-disable space-infix-ops

# Calculate an angle between two unit vectors
#
# Since we measure angle between radii of circular arcs,
# we can use simplified math (without length normalization)
#
def unit_vector_angle(ux, uy, vx, vy):
    if(ux * vy - uy * vx < 0):
        sign = -1
    else:
        sign = 1
        
    dot  = ux * vx + uy * vy

    # Add this to work with arbitrary vectors:
    # dot /= math.sqrt(ux * ux + uy * uy) * math.sqrt(vx * vx + vy * vy)

    # rounding errors, e.g. -1.0000000000000002 can screw up this
    if (dot >  1.0): 
        dot =  1.0
        
    if (dot < -1.0):
        dot = -1.0

    return sign * math.acos(dot)


# Convert from endpoint to center parameterization,
# see http:#www.w3.org/TR/SVG11/implnote.html#ArcImplementationNotes
#
# Return [cx, cy, theta1, delta_theta]
#
def get_arc_center(x1, y1, x2, y2, fa, fs, rx, ry, sin_phi, cos_phi):
    # Step 1.
    #
    # Moving an ellipse so origin will be the middlepoint between our two
    # points. After that, rotate it to line up ellipse axes with coordinate
    # axes.
    #
    x1p =  cos_phi*(x1-x2)/2 + sin_phi*(y1-y2)/2
    y1p = -sin_phi*(x1-x2)/2 + cos_phi*(y1-y2)/2

    rx_sq  =  rx * rx
    ry_sq  =  ry * ry
    x1p_sq = x1p * x1p
    y1p_sq = y1p * y1p

    # Step 2.
    #
    # Compute coordinates of the centre of this ellipse (cx', cy')
    # in the new coordinate system.
    #
    radicant = (rx_sq * ry_sq) - (rx_sq * y1p_sq) - (ry_sq * x1p_sq)

    if (radicant < 0):
        # due to rounding errors it might be e.g. -1.3877787807814457e-17
        radicant = 0

    radicant /=   (rx_sq * y1p_sq) + (ry_sq * x1p_sq)
    factor = 1
    if(fa == fs):# Migration Note: note ===
        factor = -1
    radicant = math.sqrt(radicant) * factor #(fa === fs ? -1 : 1)

    cxp = radicant *  rx/ry * y1p
    cyp = radicant * -ry/rx * x1p

    # Step 3.
    #
    # Transform back to get centre coordinates (cx, cy) in the original
    # coordinate system.
    #
    cx = cos_phi*cxp - sin_phi*cyp + (x1+x2)/2
    cy = sin_phi*cxp + cos_phi*cyp + (y1+y2)/2

    # Step 4.
    #
    # Compute angles (theta1, delta_theta).
    #
    v1x =  (x1p - cxp) / rx
    v1y =  (y1p - cyp) / ry
    v2x = (-x1p - cxp) / rx
    v2y = (-y1p - cyp) / ry

    theta1 = unit_vector_angle(1, 0, v1x, v1y)
    delta_theta = unit_vector_angle(v1x, v1y, v2x, v2y)

    if (fs == 0 and delta_theta > 0):#Migration Note: note ===
        delta_theta -= TAU
    
    if (fs == 1 and delta_theta < 0):#Migration Note: note ===
        delta_theta += TAU    

    return [ cx, cy, theta1, delta_theta ]

#
# Approximate one unit arc segment with bezier curves,
# see http:#math.stackexchange.com/questions/873224
#
def approximate_unit_arc(theta1, delta_theta):
    alpha = 4.0/3 * math.tan(delta_theta/4)

    x1 = math.cos(theta1)
    y1 = math.sin(theta1)
    x2 = math.cos(theta1 + delta_theta)
    y2 = math.sin(theta1 + delta_theta)

    return [ x1, y1, x1 - y1*alpha, y1 + x1*alpha, x2 + y2*alpha, y2 - x2*alpha, x2, y2 ]

def a2c(x1, y1, x2, y2, fa, fs, rx, ry, phi):
    sin_phi = math.sin(phi * TAU / 360)
    cos_phi = math.cos(phi * TAU / 360)

    # Make sure radii are valid
    #
    x1p =  cos_phi*(x1-x2)/2 + sin_phi*(y1-y2)/2
    y1p = -sin_phi*(x1-x2)/2 + cos_phi*(y1-y2)/2

    if (x1p == 0 and y1p == 0): # Migration Note: note ===
        # we're asked to draw line to itself
        return []

    if (rx == 0 or ry == 0): # Migration Note: note ===
        # one of the radii is zero
        return []

    # Compensate out-of-range radii
    #
    rx = abs(rx)
    ry = abs(ry)

    lmbd = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if (lmbd > 1):
        rx *= math.sqrt(lmbd)
        ry *= math.sqrt(lmbd)


    # Get center parameters (cx, cy, theta1, delta_theta)
    #
    cc = get_arc_center(x1, y1, x2, y2, fa, fs, rx, ry, sin_phi, cos_phi)

    result = []
    theta1 = cc[2]
    delta_theta = cc[3]

    # Split an arc to multiple segments, so each segment
    # will be less than 90
    #
    segments = int(max(math.ceil(abs(delta_theta) / (TAU / 4)), 1))
    delta_theta /= segments

    for i in range(0, segments):
        result.append(approximate_unit_arc(theta1, delta_theta))

        theta1 += delta_theta
        
    # We have a bezier approximation of a unit circle,
    # now need to transform back to the original ellipse
    #
    return getMappedList(result, rx, ry, sin_phi, cos_phi, cc)

def getMappedList(result, rx, ry, sin_phi, cos_phi, cc):
    mappedList = []
    for elem in result:
        curve = []
        for i in range(0, len(elem), 2):
            x = elem[i + 0]
            y = elem[i + 1]

            # scale
            x *= rx
            y *= ry

            # rotate
            xp = cos_phi*x - sin_phi*y
            yp = sin_phi*x + cos_phi*y

            # translate
            elem[i + 0] = xp + cc[0]
            elem[i + 1] = yp + cc[1]        
            curve.append(complex(elem[i + 0], elem[i + 1]))
        mappedList.append(curve)
    return mappedList

######################### a2c end ########################

    

#
# The following section is an extract
# from svgpathtools (https://github.com/mathandy/svgpathtools)
# (Copyright (c) 2015 Andrew Allan Port, Copyright (c) 2013-2014 Lennart Regebro)
#
#################### svgpathtools start ###################


COMMANDS = set('MmZzLlHhVvCcSsQqTtAa')
UPPERCASE = set('MZLHVCSQTA')

COMMAND_RE = re.compile("([MmZzLlHhVvCcSsQqTtAa])")
FLOAT_RE = re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")

def _tokenize_path(pathdef):
    for x in COMMAND_RE.split(pathdef):
        if x in COMMANDS:
            yield x
        for token in FLOAT_RE.findall(x):
            yield token

# Added for stroke font text
def getCBForQBPts(start, ctrl, end):
    cp0 = start
    cp3 = end

    cp1 = start + 2/3 * (ctrl - start)
    cp2 = end + 2/3 * (ctrl - end)
    
    return CubicBezier(cp0, cp1, cp2, cp3)
    
# Added for stroke font text
def getCBForArcPts(start, radius, rotation, large_arc, sweep, end):
    x1, y1 = start.real, start.imag
    x2, y2 = end.real, end.imag
    fa = large_arc
    fs = sweep
    rx, ry = radius.real, radius.imag
    phi = rotation
    curvesPts = a2c(x1, y1, x2, y2, fa, fs, rx, ry, phi)
    newPartSegs = []
    for curvePts in curvesPts:
        newPartSegs.append(CubicBezier(curvePts[0], curvePts[1], 
            curvePts[2], curvePts[3]))
    return newSegs
    

def parse_path(pathdef, current_pos=0j):

    elements = list(_tokenize_path(pathdef))

    elements.reverse()

    segments = []
    start_pos = None
    command = None

    while elements:

        if elements[-1] in COMMANDS:
            last_command = command
            command = elements.pop()
            absolute = command in UPPERCASE
            command = command.upper()
        else:
            if command is None:
                raise ValueError("Unallowed implicit command in %s, position %s" % (
                    pathdef, len(pathdef.split()) - len(elements)))

        if command == 'M':
            x = elements.pop()
            y = elements.pop()
            pos = float(x) + float(y) * 1j
            if absolute:
                current_pos = pos
            else:
                current_pos += pos

            start_pos = current_pos
            command = 'L'

        elif command == 'Z':
            if not (cmplxCmpWithMargin(current_pos, start_pos)):
                segments.append(CubicBezier(current_pos, current_pos, start_pos, start_pos))
            segments[-1].isClosing = True
            current_pos = start_pos
            start_pos = None
            command = None

        elif command == 'L':
            x = elements.pop()
            y = elements.pop()
            pos = float(x) + float(y) * 1j
            if not absolute:
                pos += current_pos
            segments.append(CubicBezier(current_pos, current_pos, pos, pos))
            current_pos = pos

        elif command == 'H':
            x = elements.pop()
            pos = float(x) + current_pos.imag * 1j
            if not absolute:
                pos += current_pos.real
            segments.append(CubicBezier(current_pos, current_pos, pos, pos))
            current_pos = pos

        elif command == 'V':
            y = elements.pop()
            pos = current_pos.real + float(y) * 1j
            if not absolute:
                pos += current_pos.imag * 1j
            segments.append(CubicBezier(current_pos, current_pos, pos, pos))
            current_pos = pos

        elif command == 'C':
            control1 = float(elements.pop()) + float(elements.pop()) * 1j
            control2 = float(elements.pop()) + float(elements.pop()) * 1j
            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                control1 += current_pos
                control2 += current_pos
                end += current_pos

            segments.append(CubicBezier(current_pos, control1, control2, end))
            current_pos = end

        elif command == 'S':
            if last_command not in 'CS':
                control1 = current_pos
            else:
                control1 = current_pos + current_pos - segments[-1].control2

            control2 = float(elements.pop()) + float(elements.pop()) * 1j
            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                control2 += current_pos
                end += current_pos

            segments.append(CubicBezier(current_pos, control1, control2, end))
            current_pos = end

        elif command == 'Q':
            control = float(elements.pop()) + float(elements.pop()) * 1j
            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                control += current_pos
                end += current_pos

            segments.append(getCBForQBPts(current_pos, control, end))
            current_pos = end

        elif command == 'T':
            if last_command not in 'QT':
                control = current_pos
            else:
                control = current_pos + current_pos - segments[-1].control

            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                end += current_pos

            segments.append(getCBForQBPts(current_pos, control, end))
            current_pos = end

        elif command == 'A':
            radius = float(elements.pop()) + float(elements.pop()) * 1j
            rotation = float(elements.pop())
            arc = float(elements.pop())
            sweep = float(elements.pop())
            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                end += current_pos

            segments += getCBForArcPts(current_pos, radius, rotation, arc, sweep, end)
            current_pos = end

    return segments

class CubicBezier(object):
    def __init__(self, start, control1, control2, end):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end
        self.isClosing = False

    def __eq__(self, other):
        if not isinstance(other, CubicBezier):
            return NotImplemented
        return self.start == other.start and self.end == other.end \
            and self.control1 == other.control1 \
            and self.control2 == other.control2

    def __ne__(self, other):
        if not isinstance(other, CubicBezier):
            return NotImplemented
        return not self == other

    def bpoints(self):
        return self.start, self.control1, self.control2, self.end

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 4

class Path:
    def __init__(self, segments, isClosed = False):
        self.segments = segments
        self.isClosed = isClosed
        
    def getBezierPtsInfo(self):
        prevSeg = None
        bezierPtsInfo = []

        for j, seg in enumerate(self.segments):
            
            pt = get3DVector(seg.start)
            handleRight = get3DVector(seg.control1)
            
            if(j == 0):
                if(self.isClosed):
                    handleLeft = get3DVector(self.segments[-1].control2)
                else:
                    handleLeft = pt
            else:
                handleLeft = get3DVector(prevSeg.control2)
                
            bezierPtsInfo.append([pt, handleLeft, handleRight])
            prevSeg = seg
    
        if(self.isClosed == True):
            bezierPtsInfo[-1][2] = get3DVector(seg.control1)
        else:
            bezierPtsInfo.append([get3DVector(prevSeg.end), \
                get3DVector(prevSeg.control2), get3DVector(prevSeg.end)])
                
        return bezierPtsInfo

##################### svgpathtools end ####################
