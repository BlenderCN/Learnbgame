#
#
# This Blender add-on imports paths and shapeKeys from an  SVG file
# Supported Blender Version: 2.8 Beta
#
# Copyright (C) 2018  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/shapeKeyimport/blob/master/LICENSE)
#

# Not yet pep8 compliant 

# Scaling not done based on the unit of the SVG document, but based simply on value
# If precise scaling is needed, appropriate unit (mm) needs to be set in the source SVG

bl_info = {
    "name": "Import Paths and Shape Keys from SVG",
    "author": "Shrinivas Kulkarni",
    "location": "File > Import > Import Paths & Shape Keys (.svg)",
    "category": "Learnbgame",
    "blender": (2, 80, 0),
}


import bpy, copy, math, re, time
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty
from bpy.props import CollectionProperty, EnumProperty
from xml.dom import minidom
from collections import OrderedDict
from mathutils import Vector, Matrix
from math import sqrt, cos, sin, acos, degrees, radians, tan
from cmath import exp, sqrt as csqrt, phase
from collections import MutableSequence

#################### UI and Registration Stuff ####################


noneStr = "-None-"
CURVE_NAME_PREFIX = 'Curve'

def getCurveNames(scene, context):
    return [(noneStr, noneStr, '-1')] + [(obj.name, obj.name, str(i)) for i, obj in 
            enumerate(context.scene.objects) if obj.type == 'CURVE']

def getAlignmentList(scene, context):
    alignListStrs = [*getAlignSegsFn().keys()]
    return [(noneStr, noneStr, '-1')] + [(str(align), str(align), str(i))  
            for i, align in enumerate(alignListStrs)]

def getMatchPartList(scene, context):
    arrangeListStrs = [*getAlignPartsFn().keys()]
    return [(noneStr, noneStr, '-1')] + [(str(arrange), str(arrange), str(i)) 
        for i, arrange in enumerate(arrangeListStrs)]

class ObjectImportShapeKeys(bpy.types.Operator):
    
    bl_idname = "object.import_shapekeys" 
    bl_label = "Import Paths & Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob : StringProperty(default="*.svg")    
    filepath : StringProperty(subtype='FILE_PATH')

    #User input 
    
    byGroup : BoolProperty(name="Import By Group", \
        description = "Import target and shape key paths forming a group in SVG", \
            default = True)
        
    byAttrib : BoolProperty(name="Import By Attribute", \
        description = "Import targets having attribute defining shape key path IDs in SVG", \
            default = True)
        
    shapeKeyAttribName : StringProperty(name="Attribute", \
        description = "Name of target path attribute used to define shape keys in SVG", 
            default = 'shapekeys')
        
    addShapeKeyPaths : BoolProperty(name="Retain Shape Key Paths", \
        description = "Import shape key paths as paths as well as shape keys", \
            default = False)
        
    addNontargetPaths : BoolProperty(name="Import Non-target Paths", \
        description = "Import paths that are neither targets nor shape keys", \
            default = True)
        
    addPathsFromHiddenLayer : BoolProperty(name="Import Hidden Layer Paths", 
        description='Import paths from layers marked as hidden in SVG', \
            default = False)
        
    originToGeometry : BoolProperty(name="Origin To Geometry", \
        description="Shift the imported path's origin to its geometry center", \
            default = False)
    
    xScale : FloatProperty(name="X", \
        description="X scale factor for imported paths", \
        default = 0.01)
        
    yScale : FloatProperty(name="Y", \
        description="Y scale factor for imported paths", \
            default = 0.01)

    zLocation : FloatProperty(name="Z Location", \
        description='Z coordiate value for imported paths', default = 0)
        
    resolution : IntProperty(name="Resolution", \
        description='Higher value gives smoother transition but more complex geometry', \
            default = 0, min=0)
        
    objList : EnumProperty(name="Copy Properties From", items = getCurveNames, \
        description='Curve whose material, depth etc. should be copied on to imported paths')
        
    partMatchList : EnumProperty(name="Match Parts By", items = getMatchPartList, \
        description='Match disconnected parts of target and shape key based on (BBox -> Bounding Box)')
        
    alignList : EnumProperty(name="Node Alignment Order", items = getAlignmentList, \
        description = 'Start aligning the nodes of target and shape keys (paths or parts) from')
    
    def execute(self, context):
        createdObjsMap = main(infilePath = self.filepath, \
                              shapeKeyAttribName = self.shapeKeyAttribName, \
                              byGroup = self.byGroup, \
                              byAttrib = self.byAttrib, \
                              addShapeKeyPaths = self.addShapeKeyPaths, \
                              addNontargetPaths = self.addNontargetPaths, \
                              scale = [self.xScale, -self.yScale, 1], \
                              zVal = self.zLocation, \
                              resolution = self.resolution, \
                              copyObjName = self.objList, \
                              partArrangeOrder = self.partMatchList, \
                              alignOrder = self.alignList, \
                              pathsFromHiddenLayer = self.addPathsFromHiddenLayer, \
                              originToGeometry = self.originToGeometry)
        return {'FINISHED'}
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.prop(self, "byGroup")
        row = col.row()
        row.prop(self, "byAttrib")
        row = col.row()
        row.prop(self, "shapeKeyAttribName")
        row = col.row()
        row.prop(self, "addShapeKeyPaths")
        row = col.row()
        row.prop(self, "addNontargetPaths")
        row = col.row()
        row.prop(self, "addPathsFromHiddenLayer")
        row = col.row()
        row.prop(self, "originToGeometry")
        layout.row().separator()
        row = col.row()
        row.label(text = 'Scale')                
        row = col.row()
        row.prop(self, "xScale")
        row.prop(self, "yScale")
        row = col.row()
        row.prop(self, "zLocation")
        layout.row().separator()
        row = col.row()        
        row.prop(self, "resolution")
        row = col.row()
        row.prop(self, "objList")
        row = col.row()
        row.prop(self, "partMatchList")
        row = col.row()
        row.prop(self, "alignList")

    def invoke(self, context, event):
        alignListStrs = [*getAlignSegsFn().keys()]
        arrangeListStrs = [*getAlignPartsFn().keys()]
        
        #default values
        self.objList = noneStr
        self.partMatchList = str(arrangeListStrs[-1])
        self.alignList = str(alignListStrs[-1])
        
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}

def menuImportShapeKeys(self, context):
    self.layout.operator(ObjectImportShapeKeys.bl_idname, 
        text="Import Paths & Shape Keys (.svg)")

def register():
    bpy.utils.register_class(ObjectImportShapeKeys)
    bpy.types.TOPBAR_MT_file_import.append(menuImportShapeKeys)

def unregister():
    bpy.utils.unregister_class(ObjectImportShapeKeys)
    bpy.types.TOPBAR_MT_file_import.remove(menuImportShapeKeys)

if __name__ == "__main__":
    register()

###################### addon code start ####################

DEF_ERR_MARGIN = 0.0001
hiddenLayerAttr = 'display:none'

def isValidPath(pathElem):
    dVal = pathElem.getAttribute('d')
    return (dVal != None) and (dVal.strip() != "") and \
        (dVal[0] in set('MLHVCSQTAmlhvcsqa'))
    
class OrderedSet(OrderedDict):        
    def add(self, item):
         super(OrderedSet, self).__setitem__(item, '')

    def __iter__(self):
        return super.keys().__iter__()
        
    #...Other methods to be added when needed
    
class Part():
    def __init__(self, segments, isClosed):
        self.segs = segments
        self.isClosed = isClosed
        
        if(len(segments) > 0):
            self.partToClose = self.isContinuous()
            
    def copy(self, start, end):
        if(start == None):
            start = 0
        if(end == None):
            end = len(self.segs)
        return Part(self.segs[start:end], None)#IsClosing not defined, so set to None 
        
    def getSeg(self, idx):
        return self.segs[idx]
        
    def getSegs(self):
        return self.segs
        
    def getSegsCopy(self, start, end):
        if(start == None):
            start = 0
        if(end == None):
            end = len(self.segs)
        return self.segs[start:end]
        
    def bbox(self):
        leftBot_rgtTop = [[None]*2,[None]*2] 
        for seg in self.segs:
            bb = bboxCubicBezier(seg)
            for i in range(0, 2):
                if (leftBot_rgtTop[0][i] == None or bb[0][i] < leftBot_rgtTop[0][i]):
                    leftBot_rgtTop[0][i] = bb[0][i]
            for i in range(0, 2):
                if (leftBot_rgtTop[1][i] == None or bb[1][i] > leftBot_rgtTop[1][i]):
                    leftBot_rgtTop[1][i] = bb[1][i]
                    
        return leftBot_rgtTop
    
    def isContinuous(self):
        return cmplxCmpWithMargin(self.segs[0].start, self.segs[-1].end)
        
    def getSegCnt(self):
        return len(self.segs)
        
    def length(self, error):
        return sum(seg.length(error = error) for seg in self.segs)
        
class PathElem:
    def __init__(self, path, attributes, transList, seqId):
        self.parts = getDisconnParts(path)
        self.pathId = attributes['id'].value
        self.attributes = attributes
        self.transList = transList
        self.seqId = seqId

    def getPartCnt(self):
        return len(self.parts)
        
    def getPartView(self):
        p = Part([seg for part in self.parts for seg in part.getSegs()], None)
        return p
    
    def getPartBoundaryIdxs(self):
        cumulCntList = set()
        cumulCnt = 0
        
        for p in self.parts:
            cumulCnt += p.getSegCnt()
            cumulCntList.add(cumulCnt)
            
        return cumulCntList
        
    def updatePartsList(self, segCntsPerPart, byPart):
        monolithicSegList = [seg for part in self.parts for seg in part.getSegs()]
        self.parts.clear()
        
        for i in range(0, len(segCntsPerPart)):
            if( i == 0):
                currIdx = 0
            else:
                currIdx = segCntsPerPart[i-1]
                
            nextIdx = segCntsPerPart[i]
            isClosed = None
            
            if(byPart == True and i < len(self.parts)):
                isClosed = self.parts[i].isClosed  # Let's retain as far as possible
                
            self.parts.append(Part(monolithicSegList[currIdx:nextIdx], isClosed))
            
    def __repr__(self):
        return self.pathId
        
class BlenderBezierPoint:
    #all points are complex values not 3d vectors
    def __init__(self, pt, handleLeft, handleRight):
        self.pt = pt
        self.handleLeft = handleLeft
        self.handleRight = handleRight
        
    def __repr__(self):
        return str(self.pt)

def getPathElemMap(doc, pathsFromHiddenLayer):
    elemMap = {}
    seqId = 0
    for pathXMLElem in doc.getElementsByTagName('path'):
        if (isElemSelectable(pathXMLElem, pathsFromHiddenLayer) and
            isValidPath(pathXMLElem)):
            dVal = pathXMLElem.getAttribute('d')
            transList = []
            idAttr = pathXMLElem.getAttribute('id')
            parsedPath = parse_path(dVal)
            getTransformAttribs(pathXMLElem, transList)
            pathElem = PathElem(parsedPath, pathXMLElem.attributes, transList, seqId)
            elemMap[idAttr] = pathElem
            seqId += 1
    return elemMap

def main(infilePath, shapeKeyAttribName, byGroup, byAttrib, addShapeKeyPaths, 
            addNontargetPaths, scale, zVal, resolution, copyObjName, partArrangeOrder, alignOrder, 
                pathsFromHiddenLayer, originToGeometry):

    doc = minidom.parse(infilePath)
        
    pathElemsMap = getPathElemMap(doc, pathsFromHiddenLayer)
            
    pathElems = [*pathElemsMap.values()]

    normalizePathElems(pathElems, alignOrder, partArrangeOrder)
    
    targetShapeKeyMap = {}
    allShapeKeyIdsSet = set()
    
    if(byGroup == True):
        updateShapeKeyMapByGroup(targetShapeKeyMap, allShapeKeyIdsSet, doc, pathsFromHiddenLayer)

    if(byAttrib == True):
        updateShapeKeyMapByAttrib(targetShapeKeyMap, pathElemsMap, allShapeKeyIdsSet, shapeKeyAttribName)
    
    #List of lists with all the interdependent paths that need to be homogenized
    dependentPathIdsSets = getDependentPathIdsSets(targetShapeKeyMap)

    byPart = (partArrangeOrder != noneStr)
    for prntIdx, dependentPathIdsSet in enumerate(dependentPathIdsSets):
        dependentPathsSet = [pathElemsMap.get(dependentPathId) for dependentPathId in dependentPathIdsSet 
                             if pathElemsMap.get(dependentPathId) != None]
                    
        addMissingSegs(dependentPathsSet, byPart = byPart, resolution = resolution)
        
        bIdxs = set()
        for pathElem in dependentPathsSet:
            bIdxs = bIdxs.union(pathElem.getPartBoundaryIdxs())
        
        for pathElem in dependentPathsSet:
            pathElem.updatePartsList(sorted(list(bIdxs)), byPart)
            
        #All will have same part count by now        
        allToClose = [all(pathElem.parts[j].partToClose for pathElem in dependentPathsSet) 
            for j in range(0, len(dependentPathsSet[0].parts))]
        
        #All interdependent paths will have the same no of splines with the same no of bezier points
        for pathElem in dependentPathsSet:
            for j, part in enumerate(pathElem.parts):
                part.partToClose = allToClose[j]
            
    objPathIds = set(targetShapeKeyMap.keys())
    
    if(addNontargetPaths == True):
        nontargetIds = (pathElemsMap.keys() - targetShapeKeyMap.keys()) - allShapeKeyIdsSet    
        objPathIds = objPathIds.union(nontargetIds)

    if(addShapeKeyPaths == True):
        #in case shapeKeys are also targets
        shapeKeyIdsToAdd = allShapeKeyIdsSet - targetShapeKeyMap.keys() 
        objPathIds = objPathIds.union(shapeKeyIdsToAdd.intersection(pathElemsMap.keys()))
    
    copyObj = bpy.data.objects.get(copyObjName)#Can be None
    
    objMap = {}
        
    for objPathId in objPathIds:
        addSvg2Blender(objMap, pathElemsMap[objPathId], scale, zVal, copyObj, originToGeometry)
    
    for pathElemId in targetShapeKeyMap.keys():
        pathObj = objMap[pathElemId]
        pathObj.shape_key_add(name = 'Basis')
        shapeKeyElemIds = targetShapeKeyMap[pathElemId].keys()
        for shapeKeyElemId in shapeKeyElemIds:
            shapeKeyElem = pathElemsMap.get(shapeKeyElemId)
            if(shapeKeyElem != None):#Maybe no need after so many checks earlier
                addShapeKey(pathObj, shapeKeyElem, shapeKeyElemId, scale, zVal, originToGeometry)    

    return objMap

#Avoid errors due to floating point conversions/comparisons
def cmplxCmpWithMargin(complex1, complex2, margin = DEF_ERR_MARGIN):
    return floatCmpWithMargin(complex1.real, complex2.real, margin) and \
        floatCmpWithMargin(complex1.imag, complex2.imag, margin)

def floatCmpWithMargin(float1, float2, margin = DEF_ERR_MARGIN):
    return abs(float1 - float2) < margin 

#TODO: Would be more conditions like defs. Need a better solution
def isElemSelectable(elem, pathsFromHiddenLayer):
    return getParentInHierarchy(elem, 'defs') == None and \
        (pathsFromHiddenLayer == True or not isInHiddenLayer(elem))

def getParentInHierarchy(elem, parentTag):
    parent = elem.parentNode 
    
    while(parent != None and parent.parentNode != None and parent.tagName != parentTag):
        parent = parent.parentNode 
        
    #TODO: Better way to detect the Document node
    if(parent.parentNode == None):
        return None
        
    return parent

def getTransformAttribs(elem, transList):
    if(elem.nodeType == elem.DOCUMENT_NODE):
        return
        
    transAttr = elem.getAttribute('transform')
    if(transAttr != None):
        transList.append(transAttr)
    if(elem.parentNode != None):
        getTransformAttribs(elem.parentNode, transList)

def isInHiddenLayer(elem):
    parent = elem.parentNode 
    
    while(parent != None and parent.nodeType == parent.ELEMENT_NODE and \
        (parent.tagName != 'g' or (parent.parentNode != None and  \
            parent.parentNode.tagName != 'svg'))):
        parent = parent.parentNode 
        
    if(parent != None and parent.nodeType == parent.ELEMENT_NODE):
        return parent.getAttribute('style').startswith(hiddenLayerAttr)
        
    return False

def getDependentPathIdsSets(shapeKeyMap):
    pathIdSets = []
    allAddedPathIds = set()
    for targetId in shapeKeyMap.keys():
        #Keep track of the added path Ids since the target can be a shapeKey, 
        #or a target of one of the shapeKeys of this target (many->many relation)
        if(targetId not in allAddedPathIds):
            pathIdSet = set()
            addDependentPathsToList(shapeKeyMap, pathIdSet, targetId)
            pathIdSets.append(pathIdSet)
            allAddedPathIds = allAddedPathIds.union(pathIdSet)
    return pathIdSets

#Reverse lookup
def getKeysetWithValue(srcMap, value):
    keySet = set()
    for key in srcMap:
        if(value in srcMap[key]):
          keySet.add(key)
    return keySet

#All the shape keys and their other targets are added recursively
def addDependentPathsToList(shapeKeyMap, pathIdSet, targetId):
    if(targetId in pathIdSet):
        return pathIdSet
        
    pathIdSet.add(targetId)
    shapeKeyElemIdMap = shapeKeyMap.get(targetId)
    
    if(shapeKeyElemIdMap == None):
        return pathIdSet
        
    shapeKeyElemIdList = shapeKeyElemIdMap.keys()
    if(shapeKeyElemIdList == None):
        return pathIdSet
        
    for shapeKeyElemId in shapeKeyElemIdList:
        #Recuresively add the Ids that are shape key of this shape key
        addDependentPathsToList(shapeKeyMap, pathIdSet, shapeKeyElemId)
        
        #Recursively add the Ids that are other targets of this shape key
        keyset = getKeysetWithValue(shapeKeyMap, shapeKeyElemId)
        for key in keyset:
            addDependentPathsToList(shapeKeyMap, pathIdSet, key)
        
    return pathIdSet

def getAllPathElemsInGroup(parentElem, pathElems):
    for childNode in parentElem.childNodes:    
        if childNode.nodeType == childNode.ELEMENT_NODE:    
            if(childNode.tagName == 'path' and isValidPath(childNode)):
                pathElems.append(childNode)
            elif(childNode.tagName == 'g'):
                getAllPathElemsInGroup(childNode, pathElems)

def updateShapeKeyMapByGroup(targetShapeKeyMap, allShapeKeyIdsSet, doc, pathsFromHiddenLayer):
    groupElems = [groupElem for groupElem in doc.getElementsByTagName('g') 
      if (groupElem.parentNode.tagName != 'svg' and 
        isElemSelectable(groupElem, pathsFromHiddenLayer))]
        
    for groupElem in groupElems:
        pathElems = []
        getAllPathElemsInGroup(groupElem, pathElems)
        if(pathElems != None and len(pathElems) > 1 ):
            targetId = pathElems[0].getAttribute('id')
            if(targetShapeKeyMap.get(targetId) == None):
                targetShapeKeyMap[targetId] = OrderedSet()
                
            for i in range(1, len(pathElems)):
                shapeKeyId = pathElems[i].getAttribute('id')
                targetShapeKeyMap[targetId].add(shapeKeyId)
                allShapeKeyIdsSet.add(shapeKeyId)

def updateShapeKeyMapByAttrib(targetShapeKeyMap, pathElemsMap, \
    allShapeKeyIdsSet, shapeKeyAttribName):
    for key in pathElemsMap.keys():
        targetPathElem = pathElemsMap[key]
        attributes = targetPathElem.attributes        
        shapeKeyIdAttrs = attributes.get(shapeKeyAttribName)
        if(shapeKeyIdAttrs != None):
            shapeKeyIds = shapeKeyIdAttrs.value
            shapeKeyIdsStr = str(shapeKeyIds)
            shapeKeyIdList = shapeKeyIdsStr.replace(' ','').split(',')
            if(targetShapeKeyMap.get(key) == None):
                targetShapeKeyMap[key] = OrderedSet()
            for keyId in shapeKeyIdList:
                if(pathElemsMap.get(keyId) != None):
                    targetShapeKeyMap[key].add(keyId)
                    allShapeKeyIdsSet.add(keyId)

def bboxArea(leftBot_rgtTop):
    return abs((leftBot_rgtTop[1][0]-leftBot_rgtTop[0][0]) * \
        (leftBot_rgtTop[1][1]-leftBot_rgtTop[0][1]))

#see https://stackoverflow.com/questions/24809978/calculating-the-bounding-box-of-cubic-bezier-curve
#(3 D - 9 C + 9 B - 3 A) t^2 + (6 A - 12 B + 6 C) t + 3 (B - A)
def bboxCubicBezier(bezier):    
    def evalBez(AA, BB, CC, DD, t):
        return AA * (1 - t) * (1 - t) * (1 - t) + \
                3 * BB * t * (1 - t) * (1 - t) + \
                    3 * CC * t * t * (1 - t) + \
                        DD * t * t * t
        
    A = [bezier.start.real, bezier.start.imag]
    B = [bezier.control1.real, bezier.control1.imag]
    C = [bezier.control2.real, bezier.control2.imag]
    D = [bezier.end.real, bezier.end.imag]
    
    MINXY = [min([A[0], D[0]]), min([A[1], D[1]])]
    MAXXY = [max([A[0], D[0]]), max([A[1], D[1]])]
    leftBot_rgtTop = [MINXY, MAXXY]

    a = [3 * D[i] - 9 * C[i] + 9 * B[i] - 3 * A[i] for i in range(0, 2)]
    b = [6 * A[i] - 12 * B[i] + 6 * C[i] for i in range(0, 2)]
    c = [3 * (B[i] - A[i]) for i in range(0, 2)]
    
    solnsxy = []
    for i in range(0, 2):
        solns = []
        if(a[i] == 0):
            if(b[i] == 0):
                solns.append(0)#Independent of t so lets take the starting pt
            else:
                solns.append(c[i] / b[i])
        else:
            rootFact = b[i] * b[i] - 4 * a[i] * c[i]
            if(rootFact >=0 ):
                #Two solutions with + and - sqrt
                solns.append((-b[i] + sqrt(rootFact)) / (2 * a[i]))
                solns.append((-b[i] - sqrt(rootFact)) / (2 * a[i]))
        solnsxy.append(solns)
    
    for i, soln in enumerate(solnsxy):
        for j, t in enumerate(soln):
            if(t < 1 and t > 0):                
                co = evalBez(A[i], B[i], C[i], D[i], t)
                if(co < leftBot_rgtTop[0][i]):
                    leftBot_rgtTop[0][i] = co
                if(co > leftBot_rgtTop[1][i]):
                    leftBot_rgtTop[1][i] = co 
                                       
    return leftBot_rgtTop

def getLineSegment(start, end, t0, t1):
    xt0, yt0 = (1 - t0) * start.real + t0 * end.real , (1 - t0) * start.imag + t0 * end.imag
    xt1, yt1 = (1 - t1) * start.real + t1 * end.real , (1 - t1) * start.imag + t1 * end.imag
    
    return CubicBezier(complex(xt0, yt0), complex(xt0, yt0), 
            complex(xt1, yt1), complex(xt1, yt1))

#see https://stackoverflow.com/questions/878862/drawing-part-of-a-b%c3%a9zier-curve-by-reusing-a-basic-b%c3%a9zier-curve-function/879213#879213
def getCurveSegment(seg, t0, t1):    
    ctrlPts = seg
        
    if(t0 > t1):
        tt = t1
        t1 = t0
        t0 = tt
    
    #Let's make at least the line segments of predictable length :)
    if(ctrlPts[0] == ctrlPts[1] and ctrlPts[2] == ctrlPts[3]):
        return getLineSegment(ctrlPts[0], ctrlPts[2], t0, t1)
        
    x1, y1 = ctrlPts[0].real, ctrlPts[0].imag
    bx1, by1 = ctrlPts[1].real, ctrlPts[1].imag
    bx2, by2 = ctrlPts[2].real, ctrlPts[2].imag
    x2, y2 = ctrlPts[3].real, ctrlPts[3].imag
    
    u0 = 1.0 - t0
    u1 = 1.0 - t1

    qxa =  x1*u0*u0 + bx1*2*t0*u0 + bx2*t0*t0
    qxb =  x1*u1*u1 + bx1*2*t1*u1 + bx2*t1*t1
    qxc = bx1*u0*u0 + bx2*2*t0*u0 +  x2*t0*t0
    qxd = bx1*u1*u1 + bx2*2*t1*u1 +  x2*t1*t1

    qya =  y1*u0*u0 + by1*2*t0*u0 + by2*t0*t0
    qyb =  y1*u1*u1 + by1*2*t1*u1 + by2*t1*t1
    qyc = by1*u0*u0 + by2*2*t0*u0 +  y2*t0*t0
    qyd = by1*u1*u1 + by2*2*t1*u1 +  y2*t1*t1

    xa = qxa*u0 + qxc*t0
    xb = qxa*u1 + qxc*t1
    xc = qxb*u0 + qxd*t0
    xd = qxb*u1 + qxd*t1

    ya = qya*u0 + qyc*t0
    yb = qya*u1 + qyc*t1
    yc = qyb*u0 + qyd*t0
    yd = qyb*u1 + qyd*t1
    
    return CubicBezier(complex(xa, ya), complex(xb, yb), 
            complex(xc, yc), complex(xd, yd))


def subdivideSeg(origSeg, noSegs):
    if(noSegs < 2):
        return [origSeg]
        
    segs = []
    oldT = 0
    segLen = origSeg.length(error = DEF_ERR_MARGIN) / noSegs
    for i in range(0, noSegs-1):
        t = float(i+1) / noSegs
        cBezier = getCurveSegment(origSeg, oldT, t)
        segs.append(cBezier)
        oldT = t
    
    cBezier = getCurveSegment(origSeg, oldT, 1)
    segs.append(cBezier)
    
    return segs
    

def getSubdivCntPerSeg(part, toAddCnt):
    
    class ItemWrapper:
        def __init__(self, idx, item):
            self.idx = idx
            self.item = item
            self.length = item.length(error = DEF_ERR_MARGIN)
        
    class PartWrapper:
        def __init__(self, part):
            self.itemList = []
            self.itemCnt = len(part.getSegs())
            for idx, seg in enumerate(part.getSegs()):
                self.itemList.append(ItemWrapper(idx, seg))
        
    partWrapper = PartWrapper(part)
    partLen = part.length(DEF_ERR_MARGIN)
    avgLen = partLen / (partWrapper.itemCnt + toAddCnt)

    segsToDivide = [item for item in partWrapper.itemList if item.length >= avgLen]
    segToDivideCnt = len(segsToDivide)
    avgLen = sum(item.length for item in segsToDivide) / (segToDivideCnt + toAddCnt)

    segsToDivide = sorted(segsToDivide, key=lambda x: x.length, reverse = True)

    cnts = [0] * partWrapper.itemCnt
    addedCnt = 0
    
    
    for i in range(0, segToDivideCnt):
        segLen = segsToDivide[i].length

        divideCnt = int(round(segLen/avgLen)) - 1
        if(divideCnt == 0):
            break
            
        if((addedCnt + divideCnt) >= toAddCnt):
            cnts[segsToDivide[i].idx] = toAddCnt - addedCnt
            addedCnt = toAddCnt
            break

        cnts[segsToDivide[i].idx] = divideCnt

        addedCnt += divideCnt
        
    #TODO: Verify if needed
    while(toAddCnt > addedCnt):
        for i in range(0, segToDivideCnt):
            cnts[segsToDivide[i].idx] += 1
            addedCnt += 1
            if(toAddCnt == addedCnt):
                break
                
    return cnts

def getDisconnParts(path):
    prevSeg = None
    disconnParts = []
    segs = []
    
    for i in range(0, len(path)):
        seg = path[i]
        if((prevSeg== None) or not cmplxCmpWithMargin(prevSeg.end, seg.start)):
            if(len(segs) > 0):
                disconnParts.append(Part(segs, segs[-1].isClosing))
            segs = []
        prevSeg = seg
        segs.append(seg)

    if(len(path) > 0 and len(segs) > 0):
        disconnParts.append(Part(segs, segs[-1].isClosing))

    return disconnParts

def normalizePathElems(pathElems, alignOrder, partArrangeOrder):
    for pathElem in pathElems:
        toTransformedCBezier(pathElem)
        alignPath(pathElem, alignOrder, partArrangeOrder)

#Resolution is mapped to parts
#The value 100 means 1 segment per unit length (whatever it is in source SVG) of Part
def getSegCntForResolution(part, resolution):
    segCnt = part.getSegCnt()    
    segCntForRes = int(part.length(error = DEF_ERR_MARGIN) * resolution / 100)
    
    if(segCnt > segCntForRes):
        return segCnt
    else:
        return segCntForRes

#Distribute equally; this is likely a rare condition. So why complicate?
def distributeCnt(maxSegCntsByPart, startIdx, extraCnt):    
    added = 0
    elemCnt = len(maxSegCntsByPart) - startIdx
    cntPerElem = math.floor(extraCnt / elemCnt)
    remainder = extraCnt % elemCnt
    for i in range(startIdx, len(maxSegCntsByPart)):
        maxSegCntsByPart[i] += cntPerElem
        if(i < remainder + startIdx):
            maxSegCntsByPart[i] += 1

#Make all the paths to have the maximum number of segments in the set
def addMissingSegs(pathElems, byPart, resolution):    
    maxSegCntsByPart = []
    samePartCnt = True
    maxSegCnt = 0
    
    resSegCnt = []
    sortedElems = sorted(pathElems, key = lambda p: -len(p.parts))
    for i, pathElem in enumerate(sortedElems):
        if(byPart == False):
            segCnt = getSegCntForResolution(pathElem.getPartView(), resolution)
            if(segCnt > maxSegCnt):
                maxSegCnt = segCnt

        else:
            resSegCnt.append([])                        
            for j, part in enumerate(pathElem.parts):
                partSegCnt = getSegCntForResolution(part, resolution)
                resSegCnt[i].append(partSegCnt)
                #First path                 
                if(j == len(maxSegCntsByPart)):
                    maxSegCntsByPart.append(partSegCnt)
                    
                #last part of this path, but other paths in set have more parts
                elif((j == len(pathElem.parts) - 1) and 
                    len(maxSegCntsByPart) > len(pathElem.parts)):
                        
                    remainingSegs = sum(maxSegCntsByPart[j:])
                    if(partSegCnt <= remainingSegs):
                        resSegCnt[i][j] = remainingSegs
                    else:
                        #This part has more segs than the sum of the remaining part segs
                        #So distribute the extra count
                        distributeCnt(maxSegCntsByPart, j, (partSegCnt - remainingSegs))
                        
                        #Also, adjust the seg count of the last part of the previous 
                        #segments that had fewer than max number of parts
                        for k in range(0, i):
                            if(len(sortedElems[k].parts) < len(maxSegCntsByPart)):
                                totalSegs = sum(maxSegCntsByPart)
                                existingSegs = sum(maxSegCntsByPart[:len(sortedElems[k].parts)-1])
                                resSegCnt[k][-1] = totalSegs - existingSegs
                    
                elif(partSegCnt > maxSegCntsByPart[j]):
                    maxSegCntsByPart[j] = partSegCnt

    for i, pathElem in enumerate(sortedElems):

        if(byPart == False):
            partView = pathElem.getPartView()
            segCnt = partView.getSegCnt()
            diff = maxSegCnt - segCnt

            if(diff > 0):
                cnts = getSubdivCntPerSeg(partView, diff)
                cumulSegIdx = 0
                for j in range(0, len(pathElem.parts)):
                    part = pathElem.parts[j]
                    newSegs = []
                    for k, seg in enumerate(part.getSegs()):
                        numSubdivs = cnts[cumulSegIdx] + 1
                        newSegs += subdivideSeg(seg, numSubdivs)
                        cumulSegIdx += 1
                    
                    #isClosed won't be used, but let's update anyway
                    pathElem.parts[j] = Part(newSegs, part.isClosed)
            
        else:
            for j in range(0, len(pathElem.parts)):
                part = pathElem.parts[j]
                newSegs = []

                partSegCnt = part.getSegCnt()

                #TODO: Adding everything in the last part?
                if(j == (len(pathElem.parts)-1) and 
                    len(maxSegCntsByPart) > len(pathElem.parts)):
                    diff = resSegCnt[i][j] - partSegCnt
                else:    
                    diff = maxSegCntsByPart[j] - partSegCnt
                    
                if(diff > 0):
                    cnts = getSubdivCntPerSeg(part, diff)

                    for k, seg in enumerate(part.getSegs()):
                        seg = part.getSeg(k)
                        subdivCnt = cnts[k] + 1 #1 for the existing one
                        newSegs += subdivideSeg(seg, subdivCnt)
                    
                    #isClosed won't be used, but let's update anyway
                    pathElem.parts[j] = Part(newSegs, part.isClosed)


def transTranslate(elems):
    y = 0
    if(len(elems) > 1):
        y = elems[1]
    return Matrix.Translation((elems[0], y, 0))

def transScale(elems):
    y = 0
    if(len(elems) > 1):
        y = elems[1]

    return Matrix.Scale(elems[0], 4, (1, 0, 0)) @ \
        Matrix.Scale(y, 4, (0, 1, 0))

def transRotate(elems):
    m = Matrix()
    if(len(elems) > 1):
        m = transTranslate(elems[1:])

    return m @ Matrix.Rotation(radians(elems[0]), 4, Vector((0, 0, 1))) \
        @ m.inverted()

def transSkewX(elems):
    mat = Matrix()
    mat[0][1] = tan(radians(elems[0]))
    return mat

def transSkewY(elems):
    mat = Matrix()
    mat[1][0] = tan(radians(elems[0]))
    return mat

def transMatrix(elems):
    #standard matrix with diagonal elems = 1
    mat = Matrix()
    mat[0][0] = elems[0]
    mat[0][1] = elems[2]
    mat[0][3] = elems[4]
    mat[1][0] = elems[1]
    mat[1][1] = elems[3]
    mat[1][3] = elems[5]
    return mat
   
transforms = {'translate': transTranslate,
              'scale': transScale,
              'rotate': transRotate,
              'skewX': transSkewX,
              'skewY': transSkewY,
              'matrix': transMatrix}

def getTransformMatrix(transList):
    mat = Matrix()    
    regEx = re.compile('([^\(]+)\(([^\)]+)\)')
    for transform in transList:        
        results = regEx.findall(transform)
        if(results != None and len(results) > 0):
            for res in results:
                fnStr = res[0]
                elems = [float(e) for e in res[1].split(',')]
                fn = transforms.get(fnStr)
                if(fn != None):
                    mat = fn(elems) @ mat
        res = regEx.search(transform)
    return mat
    
def getTransformedSeg(bezierSeg, mat):
    pts = []
    for pt in bezierSeg:
        pt3d = Vector((pt.real, pt.imag, 0))
        pt3d = mat @ pt3d
        pts.append(complex(pt3d[0], pt3d[1]))
    return CubicBezier(*pts)

#format (key, value): [(order_str, seg_cmp_fn), ...] 
#(Listed clockwise in the dropdown)
#round-off to int as we don't want to be over-precise with the comparison... 
#...der Gleichheitsbedingung wird lediglich  visuell geprueft werden :)
def getAlignSegsFn():
    return OrderedDict([
        ('Top-Left', lambda x, y: ((int(x.imag) < int(y.imag)) or \
            (int(x.imag) == int(y.imag) and int(x.real) < int(y.real)))),
            
        ('Top-Right', lambda x, y: ((int(x.imag) < int(y.imag)) or \
            (int(x.imag) == int(y.imag) and int(x.real) > int(y.real)))),

        ('Right-Top', lambda x, y: ((int(x.real) > int(y.real)) or \
            (int(x.real) == int(y.real) and int(x.imag) < int(y.imag)))),

        ('Right-Bottom', lambda x, y: ((int(x.real) > int(y.real)) or \
            (int(x.real) == int(y.real) and int(x.imag) > int(y.imag)))),
            
        ('Bottom-Right', lambda x, y: ((int(x.imag) > int(y.imag)) or \
            (int(x.imag) == int(y.imag) and int(x.real) > int(y.real)))),
            
        ('Bottom-left', lambda x, y: ((int(x.imag) > int(y.imag)) or \
            (int(x.imag) == int(y.imag) and int(x.real) < int(y.real)))),
            
        ('Left-Bottom', lambda x, y: ((int(x.real) < int(y.real)) or \
            (int(x.real) == int(y.real) and int(x.imag) > int(y.imag)))),
            
        ('Left-Top', lambda x, y: ((int(x.real) < int(y.real)) or \
            (int(x.real) == int(y.real) and int(x.imag) < int(y.imag)))),
        ])
    

def getAlignPartsFn():
    
    #Order of the list returned by bbox - Left[0,0]-bottom[0,1]-right[1,0]-top[1,1]
    return OrderedDict([            
        #Sorting in reverse order so that the bigger parts get matched first
        ('Node Count ', lambda part: -1 * part.getSegCnt()),
    
        ('BBox Area', lambda part: -1 * bboxArea(part.bbox())),
        
        ('BBox Height', lambda part: -1 * (part.bbox()[1][1] - part.bbox()[0][1])),
        
        ('BBox Width', lambda part: -1 * (part.bbox()[1][0] - part.bbox()[0][0])),
        
        ('BBox:Top-Left', lambda part: (part.bbox()[0][1], #Top of SVG is bottom of blender
            part.bbox()[0][0])),
            
        ('BBox:Top-Right', lambda part: (part.bbox()[0][1], 
            part.bbox()[1][0])),
            
        ('BBox:Right-Top', lambda part: (part.bbox()[1][0], 
            part.bbox()[0][1])),
            
        ('BBox:Right-Bottom', lambda part: (part.bbox()[1][0], 
            part.bbox()[1][1])),
            
        ('BBox:Bottom-Right', lambda part: (part.bbox()[1][1], 
            part.bbox()[1][0])),

        ('BBox:Bottom-left', lambda part: (part.bbox()[1][1], 
            part.bbox()[0][0])),

        ('BBox:Left-Bottom', lambda part: (part.bbox()[0][0], 
            part.bbox()[1][1])),
            
        ('BBox:Left-Top', lambda part: (part.bbox()[0][0], 
            part.bbox()[0][1])),
        ])

def alignPath(pathElem, alignOrderSegs, partArrangeOrder):

    alignSegCmpFn = getAlignSegsFn().get(alignOrderSegs)
    alignPartCmpFn = getAlignPartsFn().get(partArrangeOrder)

    parts = pathElem.parts[:]

    if(alignPartCmpFn != None):
        parts = sorted(parts, key = alignPartCmpFn)
                    
    startPt = None
    startIdx = None
    
    for i in range(0, len(parts)):
        
        #Only truly closed parts
        if(alignSegCmpFn != None and parts[i].isClosed):
            for j in range(0, parts[i].getSegCnt()):
                seg = parts[i].getSeg(j)
                if(j == 0 or alignSegCmpFn(seg.start, startPt)):
                    startPt = seg.start
                    startIdx = j
            pathElem.parts[i]= Part(parts[i].getSegsCopy(startIdx, None) + \
                parts[i].getSegsCopy(None, startIdx), parts[i].isClosed)
        else:
            pathElem.parts[i] = parts[i]

#Convert all segments to cubic bezier and apply transforms
def toTransformedCBezier(pathElem):
    for i in range(0, len(pathElem.parts)):
        part = pathElem.parts[i]
        newPartSegs = []
            
        for seg in part.getSegs():
            
            if(type(seg).__name__ is 'Line'):
                newPartSegs.append(CubicBezier(seg[0], seg[0], seg[1], seg[1]))
                
            elif(type(seg).__name__ is 'QuadraticBezier'):
                cp0 = seg[0]
                cp3 = seg[2]

                cp1 = seg[0] + 2/3 *(seg[1]-seg[0])
                cp2 = seg[2] + 2/3 *(seg[1]-seg[2])

                newPartSegs.append(CubicBezier(cp0, cp1, cp2, cp3))
                
            elif(type(seg).__name__ is 'Arc'):
                x1, y1 = seg.start.real, seg.start.imag
                x2, y2 = seg.end.real, seg.end.imag
                fa = seg.large_arc
                fs = seg.sweep
                rx, ry = seg.radius.real, seg.radius.imag
                phi = seg.rotation
                curvesPts = a2c(x1, y1, x2, y2, fa, fs, rx, ry, phi)
                
                for curvePts in curvesPts:
                    newPartSegs.append(CubicBezier(curvePts[0], curvePts[1], 
                        curvePts[2], curvePts[3]))
                    
            elif(type(seg).__name__ is 'CubicBezier'):
                newPartSegs.append(seg)
                
            else:
                print('Strange! Never thought of this.', type(seg).__name__)
                # ~ assert False    #nope.. let's continue for now
                continue
                
        if(len(pathElem.transList) > 0):
            mat = getTransformMatrix(pathElem.transList)
            newPartSegs = [getTransformedSeg(seg, mat) for seg in newPartSegs]
            
        pathElem.parts[i] = Part(newPartSegs, part.isClosed)
                
#Paths must have already been homogenized
def addShapeKey(targetCurve, shapeKeyElem, shapeKeyName, scale, zVal, originToGeometry):
    splineData = getSplineDataForPath(shapeKeyElem, scale, zVal)

    offsetLocation = Vector([0,0,0])
    if(originToGeometry == True):
        offsetLocation = targetCurve.location

    key = targetCurve.shape_key_add(name = shapeKeyName)

    i = 0
    for ptSet in splineData:
        for bezierPt in ptSet:            
            co = Vector(get3DPt(bezierPt.pt, scale, zVal)) - offsetLocation
            handleLeft = Vector(get3DPt(bezierPt.handleLeft, scale, zVal)) - offsetLocation
            handleRight = Vector(get3DPt(bezierPt.handleRight, scale, zVal)) - offsetLocation
            
            key.data[i].co = co            
            key.data[i].handle_left = handleLeft
            key.data[i].handle_right = handleRight
            
            i += 1
    
def get3DPt(point, scale, zVal):
    return [point.real * scale[0], point.imag * scale[1], zVal * scale[2]]

#All segments must have already been converted to cubic bezier
def addSvg2Blender(objMap, pathElem, scale, zVal, copyObj, originToGeometry):
    
    pathId = pathElem.pathId
    splineData = getSplineDataForPath(pathElem, scale, zVal)

    curveName = CURVE_NAME_PREFIX + str(pathElem.seqId).zfill(5)
    obj = createCurveFromData(curveName, splineData, copyObj, pathElem, 
            originToGeometry, scale, zVal)
            
    objMap[pathId] = obj

def createCurveFromData(curveName, splineData, copyObj, pathElem, 
        originToGeometry, scale, zVal):
    
    curveData = getNewCurveData(bpy, splineData, copyObj, pathElem, scale, zVal)
    obj = bpy.data.objects.new(curveName, curveData)
    bpy.context.scene.collection.objects.link(obj)    
    
    if(originToGeometry == True):
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
    return obj

def copySrcObjProps(copyObj, newCurveData):
    
    #Copying just a few attributes
    copyObjData = copyObj.data
    
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


def getNewCurveData(bpy, splinesData, copyObj, pathElem, scale, zVal):

    newCurveData = bpy.data.curves.new(pathElem.pathId, 'CURVE')
    if(copyObj != None):
        copySrcObjProps(copyObj, newCurveData)
        #Copying won't work, params set from too many places
        # ~ newCurveData = copyObj.data.copy()
        # ~ newCurveData.splines.clear()
        # ~ newCurveData.animation_data_clear()
    else:
        newCurveData.dimensions = '3D'


    for i, pointSets in enumerate(splinesData):
        spline = newCurveData.splines.new('BEZIER')
        spline.bezier_points.add(len(pointSets)-1)
        spline.use_cyclic_u = pathElem.parts[i].partToClose
        
        for j in range(0, len(spline.bezier_points)):
            pointSet = pointSets[j]
            spline.bezier_points[j].co = get3DPt(pointSet.pt, scale, zVal)
            spline.bezier_points[j].handle_left = get3DPt(pointSet.handleLeft, scale, zVal)
            spline.bezier_points[j].handle_right = get3DPt(pointSet.handleRight, scale, zVal)
            spline.bezier_points[j].handle_right_type = 'FREE'

    return newCurveData
    
def getSplineDataForPath(pathElem, scale = None, zVal = None):
    splinesData = []
    
    for i, part in enumerate(pathElem.parts):
        prevSeg = None
        pointSets = []

        for j, seg in enumerate(part.getSegs()):
            
            pt = seg.start
            handleRight = seg.control1
            
            if(j == 0):
                if(pathElem.parts[i].partToClose):
                    handleLeft = part.getSeg(-1).control2
                else:
                    handleLeft = pt
            else:
                handleLeft = prevSeg.control2
                
            pointSets.append(BlenderBezierPoint(pt, handleLeft = handleLeft, 
                handleRight = handleRight))
            prevSeg = seg
    
        if(pathElem.parts[i].partToClose == True):
            pointSets[-1].handleRight = seg.control1
        else:
            pointSets.append(BlenderBezierPoint(prevSeg.end, 
                handleLeft = prevSeg.control2, handleRight = prevSeg.end))
            
        splinesData.append(pointSets)
        
    return splinesData


###################### addon code end ####################

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
# Changes are mde to maintain which of the disconnected parts are closed (isClosing)
# and floating point comparison in parse_path is changed to have tolerance
#
# Many explanatory comments are excluded
#
#################### svgpathtools start ###################

LENGTH_MIN_DEPTH = 5

LENGTH_ERROR = 1e-12 

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


def parse_path(pathdef, current_pos=0j):
    # In the SVG specs, initial movetos are absolute, even if
    # specified as 'm'. This is the default behavior here as well.
    # But if you pass in a current_pos variable, the initial moveto
    # will be relative to that current_pos. This is useful.
    elements = list(_tokenize_path(pathdef))
    # Reverse for easy use of .pop()
    elements.reverse()

    segments = Path()
    start_pos = None
    command = None

    while elements:

        if elements[-1] in COMMANDS:
            # New command.
            last_command = command  # Used by S and T
            command = elements.pop()
            absolute = command in UPPERCASE
            command = command.upper()
        else:
            # If this element starts with numbers, it is an implicit command
            # and we don't change the command. Check that it's allowed:
            if command is None:
                raise ValueError("Unallowed implicit command in %s, position %s" % (
                    pathdef, len(pathdef.split()) - len(elements)))

        if command == 'M':
            # Moveto command.
            x = elements.pop()
            y = elements.pop()
            pos = float(x) + float(y) * 1j
            if absolute:
                current_pos = pos
            else:
                current_pos += pos

            # when M is called, reset start_pos
            # This behavior of Z is defined in svg spec:
            # http://www.w3.org/TR/SVG/paths.html#PathDataClosePathCommand
            start_pos = current_pos

            # Implicit moveto commands are treated as lineto commands.
            # So we set command to lineto here, in case there are
            # further implicit commands after this moveto.
            command = 'L'

        elif command == 'Z':
            # Close path
            if not (cmplxCmpWithMargin(current_pos, start_pos)): #For Shape key import
            #~ if not (current_pos == start_pos):
                segments.append(Line(current_pos, start_pos))
            segments[-1].isClosing = True  #For Shape key import
            segments.closed = True
            current_pos = start_pos
            start_pos = None
            command = None  # You can't have implicit commands after closing.

        elif command == 'L':
            x = elements.pop()
            y = elements.pop()
            pos = float(x) + float(y) * 1j
            if not absolute:
                pos += current_pos
            segments.append(Line(current_pos, pos))
            current_pos = pos

        elif command == 'H':
            x = elements.pop()
            pos = float(x) + current_pos.imag * 1j
            if not absolute:
                pos += current_pos.real
            segments.append(Line(current_pos, pos))
            current_pos = pos

        elif command == 'V':
            y = elements.pop()
            pos = current_pos.real + float(y) * 1j
            if not absolute:
                pos += current_pos.imag * 1j
            segments.append(Line(current_pos, pos))
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
            # Smooth curve. First control point is the "reflection" of
            # the second control point in the previous path.

            if last_command not in 'CS':
                # If there is no previous command or if the previous command
                # was not an C, c, S or s, assume the first control point is
                # coincident with the current point.
                control1 = current_pos
            else:
                # The first control point is assumed to be the reflection of
                # the second control point on the previous command relative
                # to the current point.
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

            segments.append(QuadraticBezier(current_pos, control, end))
            current_pos = end

        elif command == 'T':
            # Smooth curve. Control point is the "reflection" of
            # the second control point in the previous path.

            if last_command not in 'QT':
                # If there is no previous command or if the previous command
                # was not an Q, q, T or t, assume the first control point is
                # coincident with the current point.
                control = current_pos
            else:
                # The control point is assumed to be the reflection of
                # the control point on the previous command relative
                # to the current point.
                control = current_pos + current_pos - segments[-1].control

            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                end += current_pos

            segments.append(QuadraticBezier(current_pos, control, end))
            current_pos = end

        elif command == 'A':
            radius = float(elements.pop()) + float(elements.pop()) * 1j
            rotation = float(elements.pop())
            arc = float(elements.pop())
            sweep = float(elements.pop())
            end = float(elements.pop()) + float(elements.pop()) * 1j

            if not absolute:
                end += current_pos

            segments.append(Arc(current_pos, radius, rotation, arc, sweep, end))
            current_pos = end

    return segments

def segment_length(curve, start, end, start_point, end_point,
                   error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH, depth=0):

    mid = (start + end)/2
    mid_point = curve.point(mid)
    length = abs(end_point - start_point)
    first_half = abs(mid_point - start_point)
    second_half = abs(end_point - mid_point)

    length2 = first_half + second_half
    if (length2 - length > error) or (depth < min_depth):
        depth += 1
        return (segment_length(curve, start, mid, start_point, mid_point,
                               error, min_depth, depth) +
                segment_length(curve, mid, end, mid_point, end_point,
                               error, min_depth, depth))
    return length2


class Line(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.isClosing = False  #For Shape key import

    def __repr__(self):
        return 'Line(start=%s, end=%s)' % (self.start, self.end)

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __ne__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return not self == other

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 2
        
    def bpoints(self):
        return self.start, self.end
        
    def length(self, t0=0, t1=1, error=None, min_depth=None):
        """returns the length of the line segment between t0 and t1."""
        return abs(self.end - self.start)*(t1-t0)
        

class QuadraticBezier(object):
    def __init__(self, start, control, end):
        self.start = start
        self.end = end
        self.control = control

        self._length_info = {'length': None, 'bpoints': None}
        self.isClosing = False  #For Shape key import

    def __repr__(self):
        return 'QuadraticBezier(start=%s, control=%s, end=%s)' % (
            self.start, self.control, self.end)

    def __eq__(self, other):
        if not isinstance(other, QuadraticBezier):
            return NotImplemented
        return self.start == other.start and self.end == other.end \
            and self.control == other.control

    def __ne__(self, other):
        if not isinstance(other, QuadraticBezier):
            return NotImplemented
        return not self == other

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 3

    def bpoints(self):
        return self.start, self.control, self.end

class CubicBezier(object):
    _length_info = {'length': None, 'bpoints': None, 'error': None,
                    'min_depth': None}

    def __init__(self, start, control1, control2, end):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end

        self._length_info = {'length': None, 'bpoints': None, 'error': None,
                             'min_depth': None}
        self.isClosing = False  #For Shape key import

    def __repr__(self):
        return 'CubicBezier(start=%s, control1=%s, control2=%s, end=%s)' % (
            self.start, self.control1, self.control2, self.end)

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

    def __getitem__(self, item):
        return self.bpoints()[item]

    def __len__(self):
        return 4

    def bpoints(self):
        return self.start, self.control1, self.control2, self.end
        
    def length(self, t0=0, t1=1, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        if t0 == 0 and t1 == 1:
            if self._length_info['bpoints'] == self.bpoints() \
                    and self._length_info['error'] >= error \
                    and self._length_info['min_depth'] >= min_depth:
                return self._length_info['length']

        s = segment_length(self, t0, t1, self.point(t0), self.point(t1),
                           error, min_depth, 0)

        if t0 == 0 and t1 == 1:
            self._length_info['length'] = s
            self._length_info['bpoints'] = self.bpoints()
            self._length_info['error'] = error
            self._length_info['min_depth'] = min_depth
            return self._length_info['length']
        else:
            return s
            
    def point(self, t):
        return self.start + t*(
            3*(self.control1 - self.start) + t*(
                3*(self.start + self.control2) - 6*self.control1 + t*(
                    -self.start + 3*(self.control1 - self.control2) + self.end
                )))

class Arc(object):
    def __init__(self, start, radius, rotation, large_arc, sweep, end,
                 autoscale_radius=True):
        assert start != end
        assert radius.real != 0 and radius.imag != 0

        self.start = start
        self.radius = abs(radius.real) + 1j*abs(radius.imag)
        self.rotation = rotation
        self.large_arc = bool(large_arc)
        self.sweep = bool(sweep)
        self.end = end
        self.autoscale_radius = autoscale_radius

        self.phi = radians(self.rotation)
        self.rot_matrix = exp(1j*self.phi)

        self._parameterize()
        self.isClosing = False  #For Shape key import

    def __repr__(self):
        params = (self.start, self.radius, self.rotation,
                  self.large_arc, self.sweep, self.end)
        return ("Arc(start={}, radius={}, rotation={}, "
                "large_arc={}, sweep={}, end={})".format(*params))

    def __eq__(self, other):
        if not isinstance(other, Arc):
            return NotImplemented
        return self.start == other.start and self.end == other.end \
            and self.radius == other.radius \
            and self.rotation == other.rotation \
            and self.large_arc == other.large_arc and self.sweep == other.sweep

    def __ne__(self, other):
        if not isinstance(other, Arc):
            return NotImplemented
        return not self == other

    def _parameterize(self):
        rx = self.radius.real
        ry = self.radius.imag
        rx_sqd = rx*rx
        ry_sqd = ry*ry

        zp1 = (1/self.rot_matrix)*(self.start - self.end)/2
        x1p, y1p = zp1.real, zp1.imag
        x1p_sqd = x1p*x1p
        y1p_sqd = y1p*y1p

        radius_check = (x1p_sqd/rx_sqd) + (y1p_sqd/ry_sqd)
        if radius_check > 1:
            if self.autoscale_radius:
                rx *= sqrt(radius_check)
                ry *= sqrt(radius_check)
                self.radius = rx + 1j*ry
                rx_sqd = rx*rx
                ry_sqd = ry*ry
            else:
                raise ValueError("No such elliptic arc exists.")

        tmp = rx_sqd*y1p_sqd + ry_sqd*x1p_sqd
        radicand = (rx_sqd*ry_sqd - tmp) / tmp
        try:
            radical = sqrt(radicand)
        except ValueError:
            radical = 0
        if self.large_arc == self.sweep:
            cp = -radical*(rx*y1p/ry - 1j*ry*x1p/rx)
        else:
            cp = radical*(rx*y1p/ry - 1j*ry*x1p/rx)

        self.center = exp(1j*self.phi)*cp + (self.start + self.end)/2

        u1 = (x1p - cp.real)/rx + 1j*(y1p - cp.imag)/ry  # transformed start
        u2 = (-x1p - cp.real)/rx + 1j*(-y1p - cp.imag)/ry  # transformed end

        u1_real_rounded = u1.real
        if u1.real > 1 or u1.real < -1:
            u1_real_rounded = round(u1.real)
        if u1.imag > 0:
            self.theta = degrees(acos(u1_real_rounded))
        elif u1.imag < 0:
            self.theta = -degrees(acos(u1_real_rounded))
        else:
            if u1.real > 0:  # start is on pos u_x axis
                self.theta = 0
            else:  # start is on neg u_x axis
                self.theta = 180

        det_uv = u1.real*u2.imag - u1.imag*u2.real

        acosand = u1.real*u2.real + u1.imag*u2.imag
        if acosand > 1 or acosand < -1:
            acosand = round(acosand)
        if det_uv > 0:
            self.delta = degrees(acos(acosand))
        elif det_uv < 0:
            self.delta = -degrees(acos(acosand))
        else:
            if u1.real*u2.real + u1.imag*u2.imag > 0:
                # u1 == u2
                self.delta = 0
            else:
                # u1 == -u2
                self.delta = 180

        if not self.sweep and self.delta >= 0:
            self.delta -= 360
        elif self.large_arc and self.delta <= 0:
            self.delta += 360

class Path(MutableSequence):

    _closed = False
    _start = None
    _end = None

    def __init__(self, *segments, **kw):
        self._segments = list(segments)
        self._length = None
        self._lengths = None
        if 'closed' in kw:
            self.closed = kw['closed']  # DEPRECATED
        if self._segments:
            self._start = self._segments[0].start
            self._end = self._segments[-1].end
        else:
            self._start = None
            self._end = None

    def __getitem__(self, index):
        return self._segments[index]

    def __setitem__(self, index, value):
        self._segments[index] = value
        self._length = None
        self._start = self._segments[0].start
        self._end = self._segments[-1].end

    def __delitem__(self, index):
        del self._segments[index]
        self._length = None
        self._start = self._segments[0].start
        self._end = self._segments[-1].end

    def __iter__(self):
        return self._segments.__iter__()

    def __contains__(self, x):
        return self._segments.__contains__(x)

    def insert(self, index, value):
        self._segments.insert(index, value)
        self._length = None
        self._start = self._segments[0].start
        self._end = self._segments[-1].end

    def reversed(self):
        newpath = [seg.reversed() for seg in self]
        newpath.reverse()
        return Path(*newpath)

    def __len__(self):
        return len(self._segments)

    def __repr__(self):
        return "Path({})".format(
            ",\n     ".join(repr(x) for x in self._segments))

    def __eq__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        if len(self) != len(other):
            return False
        for s, o in zip(self._segments, other._segments):
            if not s == o:
                return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Path):
            return NotImplemented
        return not self == other

    def _calc_lengths(self, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        if self._length is not None:
            return

        lengths = [each.length(error=error, min_depth=min_depth) for each in
                   self._segments]
        self._length = sum(lengths)
        self._lengths = [each/self._length for each in lengths]

    def length(self, T0=0, T1=1, error=LENGTH_ERROR, min_depth=LENGTH_MIN_DEPTH):
        self._calc_lengths(error=error, min_depth=min_depth)
        if T0 == 0 and T1 == 1:
            return self._length
        else:
            if len(self) == 1:
                return self[0].length(t0=T0, t1=T1)
            idx0, t0 = self.T2t(T0)
            idx1, t1 = self.T2t(T1)
            if idx0 == idx1:
                return self[idx0].length(t0=t0, t1=t1)
            return (self[idx0].length(t0=t0) +
                    sum(self[idx].length() for idx in range(idx0 + 1, idx1)) +
                    self[idx1].length(t1=t1))

    @property
    def start(self):
        if not self._start:
            self._start = self._segments[0].start
        return self._start

    @start.setter
    def start(self, pt):
        self._start = pt
        self._segments[0].start = pt

    @property
    def end(self):
        if not self._end:
            self._end = self._segments[-1].end
        return self._end

    @end.setter
    def end(self, pt):
        self._end = pt
        self._segments[-1].end = pt

    def d(self, useSandT=False, use_closed_attrib=False):

        if use_closed_attrib:
            self_closed = self.closed(warning_on=False)
            if self_closed:
                segments = self[:-1]
            else:
                segments = self[:]
        else:
            self_closed = False
            segments = self[:]

        current_pos = None
        parts = []
        previous_segment = None
        end = self[-1].end

        for segment in segments:
            seg_start = segment.start
            if current_pos != seg_start or \
                    (self_closed and seg_start == end and use_closed_attrib):
                parts.append('M {},{}'.format(seg_start.real, seg_start.imag))

            if isinstance(segment, Line):
                args = segment.end.real, segment.end.imag
                parts.append('L {},{}'.format(*args))
            elif isinstance(segment, CubicBezier):
                if useSandT and segment.is_smooth_from(previous_segment,
                                                       warning_on=False):
                    args = (segment.control2.real, segment.control2.imag,
                            segment.end.real, segment.end.imag)
                    parts.append('S {},{} {},{}'.format(*args))
                else:
                    args = (segment.control1.real, segment.control1.imag,
                            segment.control2.real, segment.control2.imag,
                            segment.end.real, segment.end.imag)
                    parts.append('C {},{} {},{} {},{}'.format(*args))
            elif isinstance(segment, QuadraticBezier):
                if useSandT and segment.is_smooth_from(previous_segment,
                                                       warning_on=False):
                    args = segment.end.real, segment.end.imag
                    parts.append('T {},{}'.format(*args))
                else:
                    args = (segment.control.real, segment.control.imag,
                            segment.end.real, segment.end.imag)
                    parts.append('Q {},{} {},{}'.format(*args))

            elif isinstance(segment, Arc):
                args = (segment.radius.real, segment.radius.imag,
                        segment.rotation,int(segment.large_arc),
                        int(segment.sweep),segment.end.real, segment.end.imag)
                parts.append('A {},{} {} {:d},{:d} {},{}'.format(*args))
            current_pos = segment.end
            previous_segment = segment

        if self_closed:
            parts.append('Z')

        return ' '.join(parts)

##################### svgpathtools end ####################

