#
# This Blender add-on creates writing animation for the selected Bezier curves
# Supported Blender Version: 2.8 Beta
#
# Copyright (C) 2018  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/writinganimation/blob/master/LICENSE)
#

# Not yet pep8 compliant 
bl_info = {
    "name": "Create Writing Animation",
    "author": "Shrinivas Kulkarni",
    "location": "Properties > Active Tool and Workspace Settings > Assign Shape Keys",
    "category": "Learnbgame",
    "blender": (2, 80, 0),    
}

import bpy
import bmesh

from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty
from bpy.props import EnumProperty, PointerProperty
from mathutils import Vector, Euler, Quaternion
from math import radians, floor, ceil
from enum import Enum 

DEF_ERR_MARGIN = 0.0001
DEFAULT_DEPTH = 0.001

OBJTYPE_MODIFIER = 'MODIFIER'
OBJTYPE_NONMODIFIER = 'NONMODIFIER'
NEW_DATA_PREFIX = 'WritingAnim_'

def floatCmpWithMargin(float1, float2, margin = DEF_ERR_MARGIN):
    return abs(float1 - float2) < margin

def vectCmpWithMargin(vect1, vect2, margin = DEF_ERR_MARGIN):
    return all(abs(vect2[i] - vect1[i]) < margin for i in range(0, len(vect1)))

def isBezier(bObj):
    return bObj.type == 'CURVE' and len(bObj.data.splines) > 0 \
        and bObj.data.splines[0].type == 'BEZIER'
            
class DrawableCurve:
    def __init__(self, curveObj, objType = OBJTYPE_NONMODIFIER):
            
        self.bCurveObj = curveObj
        self.scale = curveObj.scale[:]        
        curveCopyData = curveObj.data.copy()

        #Non-zero values of the following attributes impacts length
        curveCopyData.bevel_depth = 0
        curveCopyData.extrude = 0
        curveCopyData.offset = 0

        curveCopyObj = curveObj.copy()
        curveCopyObj.data = curveCopyData

        apply_modifiers = (objType == OBJTYPE_MODIFIER)

        self.curveMeshData = curveCopyObj.to_mesh(depsgraph = bpy.context.depsgraph, \
                apply_modifiers = apply_modifiers, calc_undeformed = False)

        #Convert co to world space and calculate length and approximate normal
        tmpBM = bmesh.new()

        self.curveLength = 0
        self.mw = self.bCurveObj.matrix_world

        for i in range(0, len(self.curveMeshData.vertices)):
            self.curveMeshData.vertices[i].co = \
                self.mw @ self.curveMeshData.vertices[i].co

            if(i > 0):
                segLen = (self.curveMeshData.vertices[i].co - \
                    self.curveMeshData.vertices[i-1].co).length

                self.curveLength += segLen

            tmpBM.verts.new(self.curveMeshData.vertices[i].co)

        self.startCo = self.curveMeshData.vertices[0].co
        self.endCo = self.curveMeshData.vertices[-1].co

        tmpFace = tmpBM.faces.new(tmpBM.verts)
        tmpBM.faces.ensure_lookup_table()
        
        #Normal of co-linear verts is not zero every time, so check area
        if(floatCmpWithMargin(tmpFace.calc_area(), 0)):
            self.curveNormal = Vector((0,0,0))
        else:
            tmpFace.normal_update()
            self.curveNormal = tmpFace.normal.copy()
        
        tmpBM.free()

        #TODO: copying the object also copies the old bbox;
        #find a way to force recalculation
        #soln: bpy.context.scene.update()???

        # ~ worldBBox = []
        # ~ for val in self.bCurveObj.bound_box:
            # ~ worldBBox.append(mw * Vector((val[0], val[1], val[2])))

        #leftBot_rgtTop
        # ~ self.bbox = [min(b[0] for b in worldBBox),
                        # ~ min(b[1] for b in worldBBox),
                        # ~ max(b[0] for b in worldBBox),
                        # ~ max(b[1] for b in worldBBox)]

    def copySrcObjProps(copyObjData, newCurveData):
        
        #Copying just a few attributes        
        newCurveData.dimensions = copyObjData.dimensions

        newCurveData.resolution_u = copyObjData.resolution_u
        newCurveData.render_resolution_u = copyObjData.render_resolution_u    
        newCurveData.fill_mode = copyObjData.fill_mode
        
        newCurveData.use_fill_deform = copyObjData.use_fill_deform
        newCurveData.use_radius = copyObjData.use_radius
        newCurveData.use_stretch = copyObjData.use_stretch
        newCurveData.use_deform_bounds = copyObjData.use_deform_bounds

        newCurveData.twist_smooth = copyObjData.twist_smooth
        newCurveData.twist_mode = copyObjData.twist_mode
        
        newCurveData.offset = copyObjData.offset
        newCurveData.extrude = copyObjData.extrude
        newCurveData.bevel_depth = copyObjData.bevel_depth
        newCurveData.bevel_resolution = copyObjData.bevel_resolution
        
        for material in copyObjData.materials:
            newCurveData.materials.append(material)

    #static method
    def copyBezierPt(src, target):
        target.co = src.co
        target.handle_left = src.handle_left
        target.handle_left_type = 'FREE'
        target.handle_right = src.handle_right
        target.handle_right_type = 'FREE'

    #static method
    def createNoncyclicSpline(curveData, srcSpline, forceNoncyclic):
        spline = curveData.splines.new('BEZIER')
        spline.bezier_points.add(len(srcSpline.bezier_points)-1)

        if(forceNoncyclic):
            spline.use_cyclic_u = False
        else:
            spline.use_cyclic_u = srcSpline.use_cyclic_u

        for i in range(0, len(srcSpline.bezier_points)):
            DrawableCurve.copyBezierPt(srcSpline.bezier_points[i], 
                spline.bezier_points[i])

        if(forceNoncyclic == True and srcSpline.use_cyclic_u == True):
            spline.bezier_points.add(1)
            DrawableCurve.copyBezierPt(srcSpline.bezier_points[0], 
                spline.bezier_points[-1])

    #static method
    def getDCObjsForSpline(curveObj, objType, defaultDepth, nameStartIdx, 
        group = None, copyPropObj = None):

        #Nurbs curve excuded for now
        if(not isBezier(curveObj)):
            return []
            
        activeIdx = None #Needed, because active_index is object (not data) attribute

        copyData = bpy.data.curves.new(NEW_DATA_PREFIX+'tmp', 'CURVE')
        
        if(copyPropObj != None):            
            #If object is bezier curve copy curve properties and material
            if(isBezier(copyPropObj)):
                DrawableCurve.copySrcObjProps(copyPropObj.data, copyData)
            #If not a curve copy only material
            else:
                DrawableCurve.copySrcObjProps(curveObj.data, copyData)
                if(len(copyPropObj.data.materials) > 0):
                    copyMatIdx = copyPropObj.active_material_index
                    mat = copyPropObj.data.materials[copyMatIdx]
                    if(len(copyData.materials) == 0 or 
                        mat.name not in copyData.materials):
                            
                        copyData.materials.append(mat)
                        activeIdx = -1 #Last
                    else:
                        activeIdx = copyData.materials.find(mat.name)
        else:
            DrawableCurve.copySrcObjProps(curveObj.data, copyData)

        dcObjs = []
        idSuffix = 0
        for i, spline in enumerate(curveObj.data.splines):
            
            dataCopy = copyData.copy()
            dataCopy.splines.clear()
            DrawableCurve.createNoncyclicSpline(dataCopy, spline, forceNoncyclic = True)
            dataCopy.animation_data_clear()

            #Default settings
            dataCopy.bevel_factor_mapping_end = 'SPLINE'

            if(dataCopy.bevel_depth == 0):
                dataCopy.bevel_depth = defaultDepth
                dataCopy.offset = -defaultDepth / 2

            objCopy = curveObj.copy()
            objCopy.name = curveObj.name + str(idSuffix).zfill(2)
            objCopy.data = dataCopy
            
            if(dataCopy.shape_keys != None):
                for i in range(0, len(dataCopy.shape_keys.key_blocks)):
                    objCopy.shape_key_remove(dataCopy.shape_keys.key_blocks[0])

            objCopy.animation_data_clear()

            # ~ bpy.context.scene.collection.objects.link(objCopy) #In 2.8 add to group only

            if(objType == OBJTYPE_MODIFIER):
                dcObj = ModifierDrawableCurve(objCopy)
            else:
                dcObj = DrawableCurve(objCopy)
                
            if(activeIdx != None):
                dcObj.active_material_index = activeIdx
                
            dcObjs.append(dcObj)

            if(group != None):
                group.objects.link(dcObj.bCurveObj)

        bpy.data.curves.remove(copyData)
        
        return dcObjs

class ModifierDrawableCurve(DrawableCurve):
    def __init__(self, curveObj):
        DrawableCurve.__init__(self, curveObj, OBJTYPE_MODIFIER)

    #Given the count, return the intgerpolated coordinates of the equally spaced vertices
    #numPts is numSegs + 1 (first and last verts are included)
    def getInterpolatedVertsCo(self, numPts):
        totalLength = self.curveLength

        if(floatCmpWithMargin(totalLength, 0)):
            return [self.curveMeshData.vertices[0].co] * numPts

        segLen = totalLength / (numPts-1)
        vertCos = [self.curveMeshData.vertices[0].co]
        
        actualLen = 0
        vertIdx = 0

        for i in range(1, numPts - 1):
            co = None
            targetLen = i * segLen
            
            while(not floatCmpWithMargin(actualLen, targetLen) 
                and actualLen < targetLen):
                
                vert = self.curveMeshData.vertices[vertIdx]
                vertIdx += 1
                nextVert = self.curveMeshData.vertices[vertIdx]
                actualLen += (nextVert.co - vert.co).length

            if(floatCmpWithMargin(actualLen, targetLen)):
                co = self.curveMeshData.vertices[vertIdx].co

            else:   #interpolate
                diff = actualLen - targetLen
                co = (nextVert.co - (nextVert.co - vert.co) * \
                    (diff/(nextVert.co - vert.co).length))

                #Revert to last pt
                vertIdx -= 1
                actualLen -= (nextVert.co - vert.co).length
            vertCos.append(co)

        vertCos.append(self.curveMeshData.vertices[-1].co)
        return vertCos

def insertKF(obj, dataPath, frame):
    obj.keyframe_insert(data_path = dataPath, frame = frame)
    CreateWritingAnimOp.keyframeCnt += 1
    
#Needed in follow path constraint based animation
def setInterpolationLinear(empty):
    fcs = empty.animation_data.action.fcurves
    for fc in fcs:
        if(fc.data_path.endswith('offset') or fc.data_path.endswith('location')):
            for k in fc.keyframe_points:
                 k.interpolation = 'LINEAR'

def createEmptyWithInitKF(name, startFrame, initCo, initDirection, parentObjs, hide_viewport, group):    
    empty = bpy.data.objects.new(name, None)
    # ~ bpy.context.scene.collection.objects.link(empty) #In 2.8 add to group only
    bpy.context.scene.update()
    empty.hide_viewport = hide_viewport


    if(initDirection != None):
        empty.rotation_mode = 'QUATERNION'
        empty.rotation_quaternion = initDirection.to_track_quat('Z','Y')
        insertKF(obj = empty, dataPath = 'rotation_quaternion', frame = startFrame)

    if( len(parentObjs) > 0 ):
        for parentObj in parentObjs:
            const = empty.constraints.new(type='FOLLOW_PATH')

            const.target = parentObj
            const.name = parentObj.name
            const.forward_axis = 'FORWARD_Y'
            const.influence = 0
            const.offset = 0

    empty.location = initCo
    insertKF(obj = empty, dataPath = 'location', frame = startFrame)

    if(group != None):
        group.objects.link(empty)

    return empty

def addCustomWriterKFs(customWriter, empty, startFrame, endFrame, resetLocation):
    if(resetLocation == True):
        insertKF(obj = customWriter, dataPath = 'location', frame = (startFrame - 1))
        customWriter.location = (0,0,0)
        insertKF(obj = customWriter, dataPath = 'location', frame = startFrame)
        insertKF(obj = customWriter, dataPath = 'location', frame = endFrame)
    
    const = customWriter.constraints.new(type='CHILD_OF')
    const.target = empty
    const.name = NEW_DATA_PREFIX + 'Constraint'
    const.influence = 0
    insertKF(obj = const, dataPath = 'influence', frame = (startFrame - 1))
    
    const.influence = 1
    insertKF(obj = const, dataPath = 'influence', frame = startFrame)
    insertKF(obj = const, dataPath = 'influence', frame = endFrame)

    const.influence = 0
    insertKF(obj = const, dataPath = 'influence', frame = (endFrame + 1))

def createPencil(name, co, segs = 12, tipDepth = .1, height = 1, diameter = .033, 
        endTipPerc = 15, endTipDia = 0.0033, sharpCutOffset = 0.01, 
            tilt = 45, group = None):
            
    def createMaterialNode(obj, colorVal, matName):
        if(bpy.data.materials.get(matName)== None):
            mat = bpy.data.materials.new(matName)
            if(bpy.context.scene.render.engine == 'CYCLES'):
                mat.use_nodes = True            
                defNode = mat.node_tree.nodes[1]
                defNode.inputs[0].default_value = colorVal
            elif(bpy.context.scene.render.engine == 'BLENDER_EEVEE'):
                mat.diffuse_color = colorVal
        else:
            mat = bpy.data.materials[matName]
        obj.data.materials.append(mat)
        return mat
        
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends = True, segments = segs, 
        depth = tipDepth * (100-endTipPerc)/100, diameter1 = endTipDia, 
            diameter2 = diameter)

    up = Vector((0, 0, 1))
    bm.normal_update()

    topFace = [f for f in bm.faces if f.normal.angle(up) < radians(3)][0]
    oldFaces = [f for f in bm.faces]
    info = bmesh.ops.extrude_face_region(bm, geom=[topFace])
    bmesh.ops.translate(bm, vec = Vector((0, 0, height)), 
        verts=[v for v in info["geom"] if isinstance(v, bmesh.types.BMVert)])
    for f in bm.faces:
        if (f not in oldFaces):
            f.material_index = 0
        else:
            f.material_index = 1
    oldFaces = [f for f in bm.faces]

    offsetVerts = [v for i, v in enumerate(topFace.verts) if i % 2 == 0]
    bmesh.ops.translate(bm, vec = (0, 0, sharpCutOffset), verts = offsetVerts)

    info = bmesh.ops.create_cone(bm, cap_ends = True, segments = segs * 2, 
        depth = tipDepth * endTipPerc/100, diameter1 = 0, diameter2 = endTipDia)
        
    bmesh.ops.translate(bm, vec = (0, 0, -tipDepth * .5), verts = info['verts'])

    for f in bm.faces:
        if (f not in oldFaces):
            f.material_index = 2

    mesh = bpy.data.meshes.new(name)
    pObj = bpy.data.objects.new(name, mesh)
    # ~ bpy.context.scene.collection.objects.link(pObj) #In 2.8 add to group only
    bpy.context.scene.update()
    bm.to_mesh(mesh)
    
    bodyColor = [0.00, 0.35, 0.44, 1.00]
    sharpenedTipColor = [0.80, 0.55, 0.09, 1.00]
    endTipColor = [0.00, 0.00, 0.00, 1.00]
    createMaterialNode(pObj, bodyColor, NEW_DATA_PREFIX+'BodyMat')
    createMaterialNode(pObj, sharpenedTipColor, NEW_DATA_PREFIX + 'Tip1Mat')
    createMaterialNode(pObj, endTipColor, NEW_DATA_PREFIX + 'Tip2Mat')
    
    #pObj.data.uv_textures.new() # 2.8 Changed?

    for vert in mesh.vertices:
        vert.co.z += (tipDepth + tipDepth * endTipPerc/100) / 2

    pObj.rotation_euler = Euler((radians(tilt), 0,0), 'XYZ')
    
    if(group != None):
        group.objects.link(pObj)

    return pObj


def createKfs(empty, dcObj, startFrame, curveFrameCnt, alignToVert, objType):
    curveObj = dcObj.bCurveObj

    curveObj.data.bevel_factor_end = 0
    insertKF(obj = curveObj.data, dataPath = 'bevel_factor_end', frame = startFrame)
    
    currFrame = startFrame

    if(objType == OBJTYPE_NONMODIFIER):
        oldRot = empty.rotation_euler.copy()
        if(curveFrameCnt > 1):
            if(alignToVert):
                empty.rotation_euler = dcObj.mw.to_euler()
            insertKF(obj = empty, dataPath = 'rotation_euler', frame = startFrame)                
            insertKF(obj = empty, dataPath = 'location', frame = startFrame)                

            if(not alignToVert):
                empty.rotation_euler = dcObj.mw.inverted().to_euler()
            else:
                empty.rotation_euler = empty.matrix_world.inverted().to_euler()
                
            insertKF(obj = empty, dataPath = 'rotation_euler', frame = (startFrame + 1))                
            empty.location = [0,0,0]
            insertKF(obj = empty, dataPath = 'location', frame = (startFrame + 1))

            con = empty.constraints[curveObj.name]

            con.influence = 0
            insertKF(obj = con, dataPath = 'influence', frame = startFrame)

            con.influence = 1
            insertKF(obj = con, dataPath = 'influence', frame = (startFrame + 1))

            con.offset = 0
            insertKF(obj = empty, dataPath = 'constraints["'+curveObj.name+'"].offset', \
                frame = startFrame)

            con.offset = -100
            insertKF(obj = empty, dataPath = 'constraints["'+curveObj.name+'"].offset', \
                frame = (startFrame + curveFrameCnt))

            con.influence = 1
            insertKF(obj = con, dataPath = 'influence', \
                frame = (startFrame + curveFrameCnt - 1))

            con.influence = 0
            insertKF(obj = con, dataPath = 'influence', \
                frame = (startFrame + curveFrameCnt))

            insertKF(obj = empty, dataPath = 'location', \
                frame = (startFrame + curveFrameCnt - 1))
            insertKF(obj = empty, dataPath = 'rotation_euler', \
                frame = (startFrame + curveFrameCnt - 1))

        empty.location = dcObj.endCo
        insertKF(obj = empty, dataPath = 'location', frame = (startFrame + curveFrameCnt))
        
        if(not alignToVert):
            empty.rotation_euler = oldRot
        else:
            empty.rotation_euler = dcObj.mw.to_euler()

        insertKF(obj = empty, dataPath = 'rotation_euler', \
            frame = (startFrame + curveFrameCnt))

    else:
        objCos = dcObj.getInterpolatedVertsCo(curveFrameCnt + 1)
                
        if(alignToVert):            
            oldRot = empty.rotation_quaternion
            rotate = dcObj.curveNormal.rotation_difference(empty.matrix_world.to_euler())
            empty.rotation_quaternion = rotate

            insertKF(obj = empty, dataPath = 'rotation_quaternion', frame = startFrame)

            if(curveFrameCnt > 1):
                insertKF(obj = empty, dataPath = 'rotation_quaternion', \
                    frame = (startFrame + curveFrameCnt - 1))

        #Start from the second, since first is already covered by lift
        for i  in range(1, len(objCos)):
            currFrame += 1
            empty.location = objCos[i]
            insertKF(obj = empty, dataPath = 'location', frame = currFrame)

    curveObj.data.bevel_factor_end = 1
    insertKF(obj = curveObj.data, dataPath = 'bevel_factor_end', \
        frame = (startFrame + curveFrameCnt))
    
    fc = curveObj.data.animation_data.action.fcurves.find('bevel_factor_end')    
    for kfp in fc.keyframe_points:
        kfp.interpolation = 'LINEAR'

def getLiftMidPtCo(objStart, objEnd, liftAxis, lift, reverseLift):
    startCo = objStart.endCo
    endCo = objEnd.startCo

    if(all(co==0 for co in objStart.curveNormal)):
        moveAxis = liftAxis 
    else:
        moveAxis = [i for i in range(0, len(objStart.curveNormal)) \
            if(abs(objStart.curveNormal[i]) == abs(max(objStart.curveNormal, key=abs)))][0]
            
    midPtCo = startCo + (endCo - startCo) / 2.
    midPtCo[moveAxis] = max(startCo[moveAxis], endCo[moveAxis], key=abs) 
    
    dirn = 1
    if(endCo[moveAxis] < startCo[moveAxis]):
        dirn = -1
        
    if(reverseLift):
        dirn *= -1 
    
    midPtCo[moveAxis] += dirn * lift
    return midPtCo

def addLiftKeyFrames(empty, objStart, objEnd, liftAxis, lift, currFrame, \
    liftFrameCnt, reverseLift):
    
    empty.location = getLiftMidPtCo(objStart, objEnd, liftAxis, lift, reverseLift)
    insertKF(obj = empty, dataPath = 'location', \
        frame = round(currFrame + liftFrameCnt / 2))    
        
    empty.location = objEnd.startCo
    insertKF(obj = empty, dataPath = 'location', frame = (currFrame + liftFrameCnt))    

def getTransitionInfo(allDcObjs, liftAxis, maxLift, transitionSpeed, 
    proportionalLift, reverseLift):
        transitionLengths = []
        transitionLifts = []

        if(len(allDcObjs) <= 1):
            return transitionLengths, transitionLifts

        flatTransitionLengths = [(allDcObjs[i].startCo - \
            allDcObjs[i-1].endCo).length for i in range(1, len(allDcObjs))]

        maxFlatLength = max(flatTransitionLengths)

        for i, fl in enumerate(flatTransitionLengths):
            transitionLength = 0
            lift = 0
            startObj = allDcObjs[i]
            endObj = allDcObjs[i+1]

            if(maxFlatLength > 0):
                if(proportionalLift):
                    lift = maxLift * (fl / maxFlatLength)
                else:
                    lift = maxLift
                    
                midPtCo = getLiftMidPtCo(startObj, endObj, liftAxis, lift, reverseLift)

                transitionLength = ((midPtCo - startObj.endCo).length + \
                    (endObj.startCo - midPtCo).length) / transitionSpeed

            transitionLengths.append(transitionLength)
            transitionLifts.append(lift)

        return transitionLengths, transitionLifts

def getCurveDCObjs(selObjs, objType, defaultDepth, retain, copyPropObj, group = None):
    curveDCObjs = []

    idx = 0    #Only for naming the new objects

    for obj in selObjs:
        dcObjs = DrawableCurve.getDCObjsForSpline(obj, objType, 
            defaultDepth, idx, group, copyPropObj)

        if(len(dcObjs) == 0 ):
            continue

        idx += len(dcObjs)

        if(retain == 'Copy'):
            obj.hide_viewport = True
            obj.hide_render = True
            
        curveDCObjs.append(dcObjs)
            
    return curveDCObjs

def showOrigCurve(zeroFrameCurveDCObjs, zeroFrameOrigCurves, currFrame, retain):
    for i, origCurve in enumerate(zeroFrameOrigCurves):

        origCurve.scale = [0,0,0]
        insertKF(obj = origCurve, dataPath = 'scale', frame = (currFrame-1))        

        origCurve.scale = zeroFrameCurveDCObjs[i][0].scale[:]
        insertKF(obj = origCurve, dataPath = 'scale', frame = (currFrame))        
        
        if(retain != 'Both'):
            for dcObj in zeroFrameCurveDCObjs[i]:
                dcObj.bCurveObj.scale = dcObj.scale[:]
                insertKF(obj = dcObj.bCurveObj, dataPath = 'scale', frame = (currFrame-1))        
                dcObj.bCurveObj.scale = [0,0,0]
                insertKF(obj = dcObj.bCurveObj, dataPath = 'scale', frame = (currFrame))        

#TODO: Find a better way to calculate frame count proportional to the length
def getFrameCntForLength(totalFrames, totalLength, remainingLength, 
    remainingFrames, elemLength):
        cnt1 = remainingFrames * elemLength / remainingLength
        return floor(cnt1)

def main(retain, defaultDepth, startFrame, totalFrames,
    liftAxis, maxLift, transitionSpeed, alignToVert, proportionalLift, objType, 
        copyPropObj, customWriter, reverseLift, resetLocation):

    selObjs = [o for o in bpy.data.objects if o in bpy.context.selected_objects
        and o != customWriter and isBezier(o)]
        
    # ~ selObjs = bpy.context.selected_objects[:]    #sequence incorrect
    group = bpy.data.collections.new(NEW_DATA_PREFIX+'Collection')
    bpy.context.scene.collection.children.link(group)

    curveDCObjs = getCurveDCObjs(selObjs, objType, defaultDepth, 
        retain, copyPropObj, group)

    currFrame = -1

    if(len(curveDCObjs) == 0):
        return currFrame

    initCo = curveDCObjs[0][0].startCo
    initTangent = None

    if(alignToVert and objType == OBJTYPE_MODIFIER):
        initTangent = curveDCObjs[0][0].curveNormal

    allDcObjs = [d for c in curveDCObjs for d in c]
    parentObjs = []

    if(objType == OBJTYPE_NONMODIFIER):
        parentObjs = [o.bCurveObj for o in allDcObjs]

    empty = createEmptyWithInitKF(NEW_DATA_PREFIX + 'Guide', startFrame, initCo,
        initTangent, parentObjs = parentObjs, hide_viewport = False, group = group)

    if(customWriter == None):
        pObj = createPencil(NEW_DATA_PREFIX + 'Writer', initCo, tilt = 45, group = group)
        pObj.parent = empty

    transitionLengths, transitionLifts = \
        getTransitionInfo(allDcObjs, liftAxis, maxLift, transitionSpeed, \
            proportionalLift, reverseLift)

    totalLength = sum(o.curveLength for o in allDcObjs) + sum(transitionLengths)
    remainingLength = totalLength

    currFrame = startFrame
    zeroFrameCurves = []
    oldOrigCurveIdx = 0
    lastButOneFrame = False
    i = 0

    #inline method, makes changes to local variables
    def _createPendingKfs(empty, alignToVert):
        nonlocal zeroFrameCurves
        nonlocal currFrame
        nonlocal remainingLength

        length = 0
        for dcObj in zeroFrameCurves:
            createKfs(empty, dcObj, currFrame, curveFrameCnt = 1,
                alignToVert = alignToVert, objType = objType)
            length += dcObj.curveLength

        zeroFrameCurves = []
        currFrame += 1
        remainingLength -= length

    for j, curveDcObj in enumerate(curveDCObjs):
        for k, dcObj in enumerate(curveDcObj):

            if(lastButOneFrame):
                zeroFrameCurves.append(dcObj)
                continue

            if(i > 0):
                remainingFrames = totalFrames - currFrame + startFrame
                liftFrameCnt = getFrameCntForLength(totalFrames, totalLength, 
                    remainingLength, remainingFrames, transitionLengths[i-1])
    
                if(liftFrameCnt == remainingFrames and
                    i < len(allDcObjs)-1):
                    lastButOneFrame = True
                    zeroFrameCurves.append(dcObj)
                    continue

                if(liftFrameCnt > 0):
                    if(len(zeroFrameCurves) > 0):
                        addedLength = \
                            _createPendingKfs(empty, alignToVert)

                        liftFrameCnt -= 1

                    if(liftFrameCnt > 0):
                        addLiftKeyFrames(empty, prevDcObj, dcObj, liftAxis,
                            transitionLifts[i-1], currFrame, liftFrameCnt, reverseLift)
                        currFrame += liftFrameCnt

                remainingLength -= transitionLengths[i-1]

            remainingFrames = totalFrames - currFrame + startFrame
            
            if(i == len(allDcObjs)-1):
                curveFrameCnt = remainingFrames
            else:
                curveFrameCnt = getFrameCntForLength(totalFrames, totalLength, 
                    remainingLength, remainingFrames, dcObj.curveLength)
                    
            #Condition will be rare, but should be taken care of
            if(curveFrameCnt >= remainingFrames and i < len(allDcObjs)-1):
                lastButOneFrame = True
                curveFrameCnt -= 1

            if(curveFrameCnt == 0):
                zeroFrameCurves.append(dcObj)
                totalEndingFrameCnt = round(remainingFrames * \
                    (sum(o.curveLength for o in zeroFrameCurves) / remainingLength))

                if(totalEndingFrameCnt > 0 and
                    not lastButOneFrame and remainingFrames > 1):
                    _createPendingKfs(empty, alignToVert)
            else:
                if(curveFrameCnt == 1):
                    zeroFrameCurves.append(dcObj)
                    _createPendingKfs(empty, alignToVert)
                else:
                    if(len(zeroFrameCurves) > 0):
                        _createPendingKfs(empty, alignToVert)
                        curveFrameCnt -= 1
                    createKfs(empty, dcObj, currFrame, curveFrameCnt,
                        alignToVert, objType)
                    currFrame += curveFrameCnt
                    remainingLength -= dcObj.curveLength

            prevDcObj = dcObj
            i += 1

        if(retain != 'Copy'):
            totalProcessed = sum(len(c) for x, c in enumerate(curveDCObjs) if x <= j)
            totalProcessed -= len(zeroFrameCurves)
            newOrigCurveIdx = 0
            processed = 0
            
            while(processed < totalProcessed):
                processed += len(curveDCObjs[newOrigCurveIdx])
                newOrigCurveIdx += 1

            if(processed > totalProcessed):
                newOrigCurveIdx -= 1
                
            showOrigCurve(curveDCObjs[oldOrigCurveIdx:newOrigCurveIdx], 
                selObjs[oldOrigCurveIdx:newOrigCurveIdx], currFrame, retain)

            oldOrigCurveIdx = newOrigCurveIdx

    if(len(zeroFrameCurves) > 0):
        addedLength = _createPendingKfs(empty, alignToVert)
        if(retain != 'Copy'):
            showOrigCurve(curveDCObjs[oldOrigCurveIdx:], selObjs[oldOrigCurveIdx:], 
                currFrame, retain)

    setInterpolationLinear(empty)

    if(customWriter != None):
        addCustomWriterKFs(customWriter, empty, startFrame, currFrame, resetLocation)
    
    if(bpy.context.scene.frame_end < currFrame):
        bpy.context.scene.frame_end = currFrame
        
    bpy.context.scene.frame_current = startFrame

    return currFrame

def isAddTextAvailable():
    try:
        from addstrokefont_2_8.strokefontmain import getfontNameList, addText
        return True
    except Exception as e:
        print(e)
        return False

class CreateWritingAnimParams(bpy.types.PropertyGroup):
    retain : EnumProperty(name="Retain", 
            items = [('Both', 'Both', ""), ('Original', 'Original', ""), 
                ('Copy', 'Copy', "")], 
            default = 'Copy',
            description='What to Retain After Finishing Animation')

    startFrame : IntProperty(
            name = "Start",
            description = "Start Frame of Animation",
            min = 1,
            default = 1)

    totalFrames : IntProperty(
            name = "Length",
            description = "Total Animation Frames",
            min = 1,
            default = 500)

    transitionSpeed : FloatProperty(
            name = "Speed",
            description = "Speed of Writer During Lift (X Times Normal Speed)",
            min = 0.1,
            default = 1.5)

    maxLift : FloatProperty(
            name = "Max Lift",
            description = "Maximum Upward Distance to Traverse During Transition",
            precision = 3,
            default = 0.3)

    proportionalLift : BoolProperty(
            name = "Proportional Lift",
            description = "Should Lift Height Be Proportional to Transition Distance",
            default = True)

    liftAxis : EnumProperty(name="Axis", 
            items = [('0', 'X', ""), ('1', 'Y', ""), ('2', 'Z', "")], 
            default = '2', 
            description='Axis Along Which Writer Is to Be Lifted (If Curve Is Linear)')

    reverseLift : BoolProperty(
            name = "Reverse",
            description = "Reverse Direction of Lift",
            default = False)

    alignToVert : BoolProperty(
            name = "Aligned (Experimental)",
            description = "Align Writer to Curve Normal (Works Differently Based on Anim Types)",
            default = False)

    resetLocation : BoolProperty(
            name = "Reset Location",
            description = "Reset Location of Custom Writer to Origin For Anim Duration",
            default = True)

    animType : EnumProperty(name = "Type",
            description='Follow Path Or Location Based Animation.',    
            items = [(OBJTYPE_NONMODIFIER, 'Follow Path', ""), 
                (OBJTYPE_MODIFIER, 'Location', "")], 
            default = OBJTYPE_MODIFIER)
            
    copyPropertiesCurve : PointerProperty(
            name = 'Properties of', 
            description = "Copy Properties (Material, Bevel Depth etc.) of Object",
            type = bpy.types.Object)
        
    customWriter : PointerProperty(
            name = 'Custom Writer', 
            description = "Custom Object To Be Used As Writer",
            type = bpy.types.Object)
            
    if(isAddTextAvailable()):
        #TODO: Why this is needed two times?
        from addstrokefont_2_8.strokefontmain import getfontNameList, addText
        
        animate : EnumProperty(name="Animate", 
            items = [('selCurves', 'Selected Curves', "Create animation for selected curves"), \
                ('text', 'Text', "Create animation for stroke font text")], 
                default = 'text',
                description='Generate drawing animation for selected curves or text')
                
        text : StringProperty(name = "Text", default = 'Hello\nWorld!', description = 'Text to add')
        
        fontName : EnumProperty(name = "Font", description='Text Font', items = getfontNameList)    
        
        fontSize : FloatProperty(name = "Font Size", description = 'Text Font Size', default = 0.25)
        
        charSpacing : FloatProperty(name = "Char Spacing", \
            description='Spacing between characters', default = 1)
            
        lineSpacing : FloatProperty(name = "Line Spacing", \
            description='Spacing between lines', default = 1)


class CreateWritingAnimOp(bpy.types.Operator):

    bl_idname = "object.create_writing_anim"
    bl_label = "Create Writing Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    keyframeCnt = 0

    def execute(self, context):
        CreateWritingAnimOp.keyframeCnt = 0 
        params = context.window_manager.createWritingAnimParams
        
        retain = params.retain
        startFrame = params.startFrame
        totalFrames = params.totalFrames
        transitionSpeed = params.transitionSpeed
        liftAxis = int(params.liftAxis)
        maxLift = params.maxLift
        alignToVert = params.alignToVert
        proportionalLift = params.proportionalLift
        reverseLift = params.reverseLift
        animType = params.animType
        copyPropObj = params.copyPropertiesCurve
        customWriter = params.customWriter
        resetLocation = params.resetLocation
        
        if(copyPropObj == None or not hasattr(copyPropObj, 'type') or \
            copyPropObj.type not in(['CURVE','MESH'])):
            copyPropObj = None
            
        textColl = None
        if(hasattr(params, 'animate') and params.animate == 'text'):
            textColl = createText(context, copyPropObj)
            alignToVert = False            
            animType = OBJTYPE_NONMODIFIER
            retain = 'Copy'
            liftAxis = 2 #Z in case of text
    
        endFrame = main(retain, DEFAULT_DEPTH, startFrame, totalFrames,
            liftAxis, maxLift, transitionSpeed, alignToVert, proportionalLift, animType, 
                copyPropObj, customWriter, reverseLift, resetLocation)
                
        if(endFrame < 0):
            self.report({'WARNING'}, "No Curve Objects Selected to Create Animation")
        else:
            self.report({'INFO'}, "Created " + 
                str(CreateWritingAnimOp.keyframeCnt)+ " new keyframes")
                
        if(textColl != None):
            textObjs = textColl.objects[:]
            for o in textObjs:
                if(o.type == 'CURVE'):
                    textColl.objects.unlink(o)
                    bpy.data.curves.remove(o.data)#TODO: Also removes object?
            bpy.context.scene.collection.children.unlink(textColl)
            bpy.data.collections.remove(textColl)

        return {'FINISHED'}

def createText(context, copyPropObj):
    stParams = context.window_manager.createWritingAnimParams
    
    fontName = stParams.fontName
    fontSize = stParams.fontSize
    charSpacing = stParams.charSpacing
    lineSpacing = stParams.lineSpacing
    text = stParams.text

    #TODO: Why this is needed again?
    from addstrokefont_2_8.strokefontmain import getFontNames, addText
    collection = addText(fontName, fontSize, charSpacing, lineSpacing, copyPropObj, \
        text, cloneGlyphs = False)
        
    for o in bpy.data.objects:
        try:
            o.select_set(False)
        except:
            pass
        
    for o in collection.all_objects:
        o.select_set(True)

    context.scene.update()
    
    return collection

class SeparateSplinesObjsOp(bpy.types.Operator):

    bl_idname = "object.separate_splines"
    bl_label = "Separate Bezier Splines"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selObjs = bpy.context.selected_objects
        changeCnt = 0
        splineCnt = 0
        
        if(len(selObjs) == 0):
            self.report({'WARNING'}, "No Curve Objects Selected")
            return {'FINISHED'}
        
        for obj in selObjs:

            if(not isBezier(obj) or len(obj.data.splines) <= 1):
                continue
            collections = obj.users_collection
            for i, spline in enumerate(obj.data.splines):
                objCopy = obj.copy()
                objCopy.name = obj.name+"_"+ str(i).zfill(4)
                dataCopy = obj.data.copy()
                dataCopy.splines.clear()
                objCopy.data = dataCopy
                DrawableCurve.createNoncyclicSpline(dataCopy,
                    spline, forceNoncyclic = False)
                for collection in collections:
                    collection.objects.link(objCopy)
                if(obj.name in bpy.context.scene.collection.objects and \
                    objCopy.name not in bpy.context.scene.collection.objects):
                    bpy.context.scene.collection.objects.link(objCopy)
            for collection in collections:
                collection.objects.unlink(obj)
            if(obj.name in bpy.context.scene.collection.objects):
                bpy.context.scene.collection.objects.unlink(obj)
            bpy.data.curves.remove(obj.data)
            # ~ bpy.data.objects.remove(obj) #2.8 Changed?
            changeCnt += 1
            splineCnt += (i + 1)
            
        self.report({'INFO'}, "Separated "+ str(changeCnt) + " curve object" + \
            ("s" if(changeCnt > 1) else "") + " into " +str(splineCnt) + " new ones")
            
        return {'FINISHED'}


class CreateWritingAnimPanel(bpy.types.Panel):    
    bl_label = "Writing Animation"
    bl_idname = "CURVE_PT_writinganim"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.objectmode'
    
    def draw(self, context):
        params = bpy.context.window_manager.createWritingAnimParams
        
        layout = self.layout
        layout.use_property_split = True

        obj = context.object
        col = layout.column()

        col.operator("object.separate_splines")
        
        col.separator()
        col.label(text="Animation", icon="ANIM")
        
        if(hasattr(params, 'animate')):
            col.prop(params, "animate")
        
            if(params.animate == 'text'):
                col.prop(params, 'text')
                col.prop(params, 'fontName')
                col.prop(params, 'fontSize')
                col.prop(params, 'charSpacing')
                col.prop(params, 'lineSpacing')
                
        if(not hasattr(params, 'animate') or params.animate != 'text'):
            col.prop(params, 'animType')
            col.prop(params, "retain")
                
        col.prop(params, "startFrame")
        col.prop(params, "totalFrames")
        col.prop(params, "copyPropertiesCurve")

        col.separator()
        col.label(text="Transition", icon="ARROW_LEFTRIGHT")

        col.prop(params, "transitionSpeed")
        col.prop(params, "maxLift")
        
        #Always Z in case of text
        if(not hasattr(params, 'animate') or params.animate != 'text'):
            col.prop(params, "liftAxis")
            
        col.prop(params, "proportionalLift")
        col.prop(params, "reverseLift")

        col.separator()
        col.label(text="Writer", icon="GREASEPENCIL")

        if(not hasattr(params, 'animate') or params.animate != 'text'):
            col.prop(params, "alignToVert")

        col.prop(params, "customWriter")
        
        col.prop(params, "resetLocation")

        col.separator()
        col.operator("object.create_writing_anim")

def register():
    bpy.utils.register_class(CreateWritingAnimPanel)
    bpy.utils.register_class(CreateWritingAnimOp)
    bpy.utils.register_class(SeparateSplinesObjsOp)
    bpy.utils.register_class(CreateWritingAnimParams)
    bpy.types.WindowManager.createWritingAnimParams = \
        bpy.props.PointerProperty(type=CreateWritingAnimParams)

def unregister():
    bpy.utils.unregister_class(CreateWritingAnimPanel)
    bpy.utils.unregister_class(CreateWritingAnimOp)
    bpy.utils.unregister_class(SeparateSplinesObjsOp)
    del bpy.types.WindowManager.createWritingAnimParams
    bpy.utils.unregister_class(CreateWritingAnimParams)

if __name__ == "__main__":
    register()
