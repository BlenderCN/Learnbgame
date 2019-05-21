'''
Created on 20 sie 2015

@author: Komi
'''
from math import fabs, sqrt, acos, degrees, pi, radians

from mathutils import Vector

import bmesh
import bpy
from roundedprofile.coords_converter import CoordsConverter
from roundedprofile.geometry_calculator import GeometryCalculator

WRONG_FLOAT = 1e10
two_pi = 2 * pi
defaultZ = 0


class Updater():
    updateCountsEnabled = True
    updatedProfileCount = 0
    updatedConnectionsRadiusForAutoadjustCount = 0
    updatedCoordinatesOnCoordChangeCount = 0
    updatedTypeCount = 0
    updatedCoordinatesOnCoordSystemChangeCount = 0
    updatedCornerAndConnectionPropertiesFromMasterCount = 0


    @staticmethod
    def resetCounts(self):
        Updater.updatedProfileCount = 0
        Updater.updatedConnectionsRadiusForAutoadjustCount = 0
        Updater.updatedCoordinatesOnCoordChangeCount = 0
        Updater.updatedTypeCount = 0
        Updater.updatedCoordinatesOnCoordSystemChangeCount = 0
        Updater.updatedCornerAndConnectionPropertiesFromMasterCount = 0

    @staticmethod
    def addMesh(roundedProfileObject):
        corners = roundedProfileObject.RoundedProfileProps[0].corners
        connections = roundedProfileObject.RoundedProfileProps[0].connections
        drawMode = roundedProfileObject.RoundedProfileProps[0].drawMode
        roundedtype = roundedProfileObject.RoundedProfileProps[0].type

        mesh = roundedProfileObject.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        drawFunction = StrategyFactory.getDrawStrategy(drawMode, roundedtype)
        drawFunction(corners, connections, mesh, bm)

    @staticmethod
    def createRoundedProfile(self, context):
        # deselect all objects
        for o in bpy.data.objects:
            o.select = False

        # we create main object and mesh for walls
        roundedProfileMesh = bpy.data.meshes.new("RoundedProfile")
        roundedProfileObject = bpy.data.objects.new("RoundedProfile", roundedProfileMesh)
        roundedProfileObject.location = bpy.context.scene.cursor_location

        bpy.context.scene.objects.link(roundedProfileObject)
        roundedProfileObject.RoundedProfileProps.add()
        roundedProfileObject.RoundedProfileProps[0].corners.add()
        roundedProfileObject.RoundedProfileProps[0].corners.add()
        roundedProfileObject.RoundedProfileProps[0].connections.add()
        roundedProfileObject.RoundedProfileProps[0].connections.add()
        roundedProfileObject.RoundedProfileProps[0].updateEnabledFlag = True

        Updater.addMesh(roundedProfileObject)
        # we select, and activate, main object for the room.
        roundedProfileObject.select = True
        bpy.context.scene.objects.active = roundedProfileObject


    @staticmethod
    def removeCornerFromRoundedProfile (self, context, id):
        props = Updater.getPropertiesFromContext(self, context)
        props.corners.remove(id)
        props.connections.remove(id)
        props.previousNumOfCorners = len(props.corners)
        Updater.updateCornerAndConnectionPropertiesFromMaster(self, context)


    @staticmethod
    def addCornerToRoundedProfile (self, context, id):
        props = Updater.getPropertiesFromContext(self, context)

        props.updateEnabledFlag = False
        props.corners.add()
        length = len(props.corners)
        lastIndex = length - 1
        targetIndex = id + 1
        props.corners.move(lastIndex, targetIndex)
        assignCornerProperties(props.corners[targetIndex], props.corners[id])
        Updater.updateCoordinatesOnCoordChange(props.corners[targetIndex], context)
        props.previousNumOfCorners = length

        props.connections.add()
        length = len(props.connections)
        lastIndex = length - 1
        props.connections.move(lastIndex, targetIndex)
        props.updateEnabledFlag = True
        Updater.updateCornerAndConnectionPropertiesFromMaster(self, context)

    @staticmethod
    def recalculateCornerIds (self, context):
        props = Updater.getPropertiesFromContext(self, context)
        corners = props.corners
        for id in range (0, len(corners)):
            corners[id].id = id


    @staticmethod
    def updateConnectionsRadiusForAutoadjust(self, context):
        if Updater.updateCountsEnabled:
            Updater.updatedConnectionsRadiusForAutoadjustCount += 1
            print ("updatedConnectionsRadiusForAutoadjustCount: " + str(Updater.updatedConnectionsRadiusForAutoadjustCount))

        roundedProfileObject = bpy.context.active_object
        props = roundedProfileObject.RoundedProfileProps[0]
        autoadjust = props.connectionAutoAdjustEnabled
        if autoadjust:
            corners = props.corners
            connections = props.connections
            lastIndex = len(corners) - 1
            props.updateEnabledFlag = False
            for i in range(lastIndex):
                Updater.updateConnectionRadius(corners[i], corners[i + 1], connections[i])
            Updater.updateConnectionRadius(corners[lastIndex], corners[0], connections[lastIndex])
            props.updateEnabledFlag = True
        Updater.updateProfile(self, context)

    @staticmethod
    def updateConnectionRadius(corner1, corner2, connection):
        c1 = Vector((corner1.x, corner1.y, defaultZ))
        c2 = Vector((corner2.x, corner2.y, defaultZ))
        geomCalc = GeometryCalculator()
        c1c2, c1c2Length = geomCalc.getVectorAndLengthFrom2Points(c1, c2)
        if (corner1.radius + corner2.radius) <= c1c2Length:
            connection.radius = c1c2Length
        else:
            connection.radius = corner1.radius + corner2.radius

    # TODO - think it through how and when to update alpha and radius and when to update X and Y??? what about reference angular and reference XY
    @staticmethod
    def updateCoordinatesOnCoordSystemChange(self, context):
        if Updater.updateCountsEnabled:
            Updater.updatedCoordinatesOnCoordSystemChangeCount += 1
            print ("updatedCoordinatesOnCoordSystemChangeCount: " + str(Updater.updatedCoordinatesOnCoordSystemChangeCount))
        roundedProfileObject = bpy.context.active_object
        props = Updater.getPropertiesFromContext(self, context)
        corners = props.corners
        coordSystem = props.coordSystem
        props.coordSystemChangingFlag = True
        props.updateEnabledFlag = False
        converterToNewCoords = StrategyFactory.getConverterOnCoordsSystemChange(coordSystem)
        converterToNewCoords(corners)
        props.updateEnabledFlag = True
        props.coordSystemChangingFlag = False


    @staticmethod
    def updateCoordinatesOnCoordChange(self, context):
        if Updater.updateCountsEnabled:
            Updater.updatedCoordinatesOnCoordChangeCount += 1
            print ('Updater.updatedCoordinatesOnCoordChangeCount: ' + str(Updater.updatedCoordinatesOnCoordChangeCount))

        roundedProfileObject = bpy.context.active_object
#         corners = roundedProfileObject.RoundedProfileProps[0].corners
        coordSystem = roundedProfileObject.RoundedProfileProps[0].coordSystem
        flag = roundedProfileObject.RoundedProfileProps[0].coordSystemChangingFlag
        Updater.recalculateCornerIds(self, context)
        if flag == False:
            converterToXY = StrategyFactory.getConverterOnCoordsValueChange(coordSystem)
            converterToXY(self)
        Updater.updateConnectionsRadiusForAutoadjust(self, context)

    @staticmethod
    def displayCoords(self, corners):
        print("-X-Y-ALPHA-RADIUS-")
        for corner in corners:
            print("------")
            print(str(corner.x) + " --- " + str(corner.y) + " --- " + str(corner.coordAngle) + " --- " + str(corner.coordRadius))
        print("========================")

    @staticmethod
    def updateCornerAndConnectionPropertiesFromMaster(self, context):
        if Updater.updateCountsEnabled:
            Updater.updatedCornerAndConnectionPropertiesFromMasterCount += 1
            print("Updater.updatedCornerAndConnectionPropertiesFromMasterCount: " + str(Updater.updatedCornerAndConnectionPropertiesFromMasterCount))
        roundedProfileObject = bpy.context.active_object
        props = roundedProfileObject.RoundedProfileProps[0]
        props.updateEnabledFlag = False
        if props.masterCornerEnabled:
            for c in props.corners:
                c.radius = props.masterCornerRadius
                c.sides = props.masterCornerSides
                c.flipAngle = props.masterCornerFlipAngle
        if props.masterConnectionEnabled:
            for c in props.connections:
                c.type = props.masterConnectionType
                c.inout = props.masterConnectionInout
                c.flipCenter = props.masterConnectionflipCenter
                c.flipAngle = props.masterConnectionflipAngle
                c.radius = props.masterConnectionRadius
                c.sides = props.masterConnectionSides
        props.updateEnabledFlag = True
        Updater.updateProfile(self, context)

    @staticmethod
    def updateType(self, context):
        if Updater.updateCountsEnabled:
            Updater.updatedTypeCount += 1
            print ('Updater.updatedTypeCount: ' + str(Updater.updatedTypeCount))
        props = Updater.getPropertiesFromContext(self, context)
        props.updateEnabledFlag = False
        profileType = props.type
        previousCoordSystem = props.coordSystem
        props.coordSystem = 'XY'  # this is to allow changing profileType in XY coords space
        adjust = StrategyFactory.getTypeAdjust(profileType)
        adjust(props)
        props.coordSystem = previousCoordSystem  # switch back to original coords system
        props.updateEnabledFlag = True
        Updater.updateProfile(self, context)

    @staticmethod
    def updateProfile(self, context):
        props = Updater.getPropertiesFromContext(self, context)
        if (props.updateEnabledFlag == False):
            return
        if Updater.updateCountsEnabled:
            Updater.updatedProfileCount = Updater.updatedProfileCount + 1
            print("updatedProfileCount: " + str(Updater.updatedProfileCount))

        o = bpy.context.active_object
        o.select = False
        o.data.user_clear()
        bpy.data.meshes.remove(o.data)
        roundedProfileMesh = bpy.data.meshes.new("RoundedProfile")
        o.data = roundedProfileMesh
        o.data.use_fake_user = True

        Updater.refreshTotalSides(o)
        Updater.addMesh(o)
        o.select = True
        bpy.context.scene.objects.active = o



    @staticmethod
    def refreshTotalSides(roundedProfileObject):
        corners = roundedProfileObject.RoundedProfileProps[0].corners
        connections = roundedProfileObject.RoundedProfileProps[0].connections
        drawMode = roundedProfileObject.RoundedProfileProps[0].drawMode

        sidesAccumulator = 0
        if drawMode == 'Both' or drawMode == 'Merged result':
            for corner in corners:
                if corner.radius > 0:
                    sidesAccumulator = sidesAccumulator + corner.sides
            for corner in connections:
                sidesAccumulator = sidesAccumulator + corner.sides
        elif drawMode == 'Corners':
            for corner in corners:
                if corner.radius > 0:
                    sidesAccumulator = sidesAccumulator + corner.sides
        elif drawMode == 'Connections':
            for corner in connections:
                sidesAccumulator = sidesAccumulator + corner.sides
        roundedProfileObject.RoundedProfileProps[0].totalSides = sidesAccumulator

    @staticmethod
    def getPropertiesFromContext(self, context):
        roundedProfileObject = bpy.context.active_object
        props = roundedProfileObject.RoundedProfileProps[0]
        return props
##################################
class StrategyFactory():
    @staticmethod
    def getDrawStrategy(drawMode, roundedProfileType):
        if drawMode == 'Corners':
            return drawModeCorners
        elif drawMode == 'Connections':
            return drawModeConnections
        elif drawMode == 'Both':
            return drawModeBoth
        elif drawMode == 'Merged result' and roundedProfileType != 'Curve':
            return drawModeMergedResult
        elif drawMode == 'Merged result' and roundedProfileType == 'Curve':
            return drawModeMergedResultForCurve

    @staticmethod
    def getDrawTangentStrategy(inout):
        if inout == 'Outer':
            return drawOuterTangentConnection
        elif inout == 'Inner':
            return drawInnerTangentConnection
        elif inout == 'Outer-Inner':
            return drawOuterInnerTangentConnection
        elif inout == 'Inner-Outer':
            return drawInnerOuterTangentConnection

    @staticmethod
    def getDrawTangentLineStrategy(inout):
        if (inout == 'Outer' or inout == 'Inner'):
            return drawTangentLine
        else:
            return drawTangentLineMixed

    @staticmethod
    def getConverterOnCoordsSystemChange(coords):
        if coords == 'XY':
            return convertXYFake
        elif coords == 'Angular':
            return convertFromXYToGlobalAngular
#         elif coords == 'DeltaXY':
#             return convertFromXYToDxDy
#         elif coords == 'DeltaAngular':
#             return convertFromXYToRefAngular

    @staticmethod
    def getConverterOnCoordsValueChange(coords):
        if coords == 'XY':
            return convertXYFake
        elif coords == 'Angular':
            return convertFromGlobalAngularToXY
#         elif coords == 'DeltaXY':
#             return convertFromDxDyToXY
#         elif coords == 'DeltaAngular':
#             return convertFromRefAngularToXY

    @staticmethod
    def getTypeAdjust(profileType):
        if profileType == 'Polygon':
            return adjustToPolygon
        elif profileType == 'Curve':
            return adjustToCurve
        elif profileType == 'Chain':
            return adjustToChain
##################################

def adjustToPolygon(properties):
    corners = properties.corners
    corners_count = len(corners)
    connections = properties.connections
    previousNumOfCorners = properties.previousNumOfCorners

    # if switching from chain remove additional
    while corners_count > previousNumOfCorners:
        corners.remove(corners_count - 1)
        corners_count = len(corners)

    connections_count = len(connections)
    if(connections_count > corners_count):
        while(connections_count > corners_count):
            connections.remove(connections_count - 1)
            connections_count = len(connections)
    else:
        while(connections_count < corners_count):
            connections.add()
            connections_count = len(connections)

def adjustToCurve(properties):
    corners = properties.corners
    corners_count = len(corners)
    connections = properties.connections
    previousNumOfCorners = properties.previousNumOfCorners

    # if switching from chain remove itional
    while corners_count > previousNumOfCorners:
        corners.remove(corners_count - 1)
        corners_count = len(corners)
    
    connections_count = len(connections)
    if(connections_count >= corners_count):
        while(connections_count >= corners_count):
            connections.remove(connections_count - 1)
            connections_count = len(connections)
    else:
        while(connections_count < corners_count - 1):
            connections.add()
            connections_count = len(connections)
    

def adjustToChain(properties):
    adjustToCurve(properties)
    corners = properties.corners
    baseCornersCount = len(corners)
    connections = properties.connections
    baseConnectionsCount = len(connections)

    # middle corners are duplicated (2,3,4), start and end stays the same
    # original 1 - 2 - 3 - 4 - 5
    #          /  2  -  3 -  4 \
    #        1                   5
    #          \  2' -  3'-  4'/


    for k in reversed(range(0, baseConnectionsCount)):
        connections.add()
        lastConnectionIndex = len(connections) - 1
        assignConnectionProperties(connections[lastConnectionIndex], connections[k])
    for i in reversed(range(1, baseCornersCount - 1)):
        corners.add()
        lastCornerIndex = len(corners) - 1
        assignCornerProperties(corners[lastCornerIndex], corners[i])


def assignCornerProperties(target, source):
    target.x = source.x
    target.y = source.y
    target.coordAngle = source.coordAngle
    target.coordRadius = source.coordRadius
    target.startx = source.startx
    target.starty = source.starty
    target.endx = source.endx
    target.endy = source.endy
    target.flipAngle = source.flipAngle
    target.radius = source.radius
    target.sides = source.sides

def assignConnectionProperties(target, source):

    target.type = source.type
    target.inout = source.inout
    target.flipCenter = source.flipCenter
    target.flipAngle = source.flipAngle
    target.radius = source.radius
    target.sides = source.sides

def convertXYFake(corners):
    pass

def convertFromXYToGlobalAngular(corners):
    for c in corners:
        angle, radius = CoordsConverter.ToAngular(0, 0, c.x, c.y)
        c.coordAngle = degrees(angle)
        c.coordRadius = radius

def convertFromGlobalAngularToXY(c):
    c.x, c.y = CoordsConverter.ToXY(0, 0, radians(c.coordAngle), c.coordRadius)

# def convertFromXYToDxDy(corners):
#     lastIndex = len(corners) - 1
#     corners[0].dx = corners[0].x
#     corners[0].dy = corners[0].y
#     for i in range(0, lastIndex):
#         corners[i + 1].dx = corners[i + 1].x - corners[i].x
#         corners[i + 1].dy = corners[i + 1].y - corners[i].y
#
# def convertFromDxDyToXY(corners):
#     lastIndex = len(corners) - 1
#     corners[0].x = corners[0].dx
#     corners[0].y = corners[0].dy
#     for i in range(0, lastIndex):
#         corners[i + 1].x = corners[i].x + corners[i + 1].dx
#         corners[i + 1].y = corners[i].y + corners[i + 1].dy
#
# def convertFromXYToRefAngular(corners):
#     c0 = corners[0]
#     angle, c0.deltaCoordRadius = CoordsConverter.ToAngular(0, 0, c0.x, c0.y)
#     c0.deltaCoordAngle = degrees(angle)
#
#     lastIndex = len(corners) - 1
#     for i in range(0, lastIndex):
#         angle, radius = CoordsConverter.ToAngular(corners[i].x, corners[i].y, corners[i + 1].x, corners[i + 1].y)
#         corners[i + 1].deltaCoordAngle = degrees(angle)
#         corners[i + 1].deltaCoordRadius = radius
#
# def convertFromRefAngularToXY(corners):
#     c0 = corners[0]
#     c0.x, c0.y = CoordsConverter.ToXY(0, 0, radians(c0.deltaCoordAngle), c0.deltaCoordRadius)
#
#     lastIndex = len(corners) - 1
#     for i in range(0, lastIndex):
#         corners[i + 1].x, corners[i + 1].y = CoordsConverter.ToXY(corners[i].x, corners[i].y,
#                                                                radians(corners[i + 1].deltaCoordAngle), corners[i + 1].deltaCoordRadius)

# 'XY', 'Angular', 'DeltaXY','DeltaAngular'
def drawModeCorners(corners, connections, mesh, bm):
    for corner in corners:
        drawCornerCircle(corner, bm)
    bm.to_mesh(mesh)

def drawModeConnections(corners, connections, mesh, bm):
    drawConnections(corners, connections, bm)
    bm.to_mesh(mesh)


def drawModeBoth(corners, connections, mesh, bm):
    drawModeCorners(corners, connections, mesh, bm)
    drawConnections(corners, connections, bm)
    bm.to_mesh(mesh)

def drawModeMergedResult(corners, connections, mesh, bm):
    drawConnections(corners, connections, bm)
    for corner in corners:
        drawCornerAsArc(corner, bm)

    bm.to_mesh(mesh)

    selectedVerts = [f for f in bm.verts]
    bmesh.ops.remove_doubles(bm, verts = selectedVerts, dist = 0.001)

    bm.to_mesh(mesh)

def drawModeMergedResultForCurve(corners, connections, mesh, bm):
    drawConnections(corners, connections, bm)

    for index in range(1, len(corners) - 1):
        drawCornerAsArc(corners[index], bm)

    bm.to_mesh(mesh)

    selectedVerts = [f for f in bm.verts]
    bmesh.ops.remove_doubles(bm, verts = selectedVerts, dist = 0.001)

    bm.to_mesh(mesh)

def drawCornerCircle(corner, bm):
    center = Vector((corner.x, corner.y, defaultZ))
    startPoint = center + Vector((0, 1, 0)) * corner.radius
    spinAxis = Vector((0, 0, 1))
    angle = two_pi
    v0 = bm.verts.new(startPoint)
    result = bmesh.ops.spin(bm, geom = [v0], cent = center, axis = spinAxis, \
                                   angle = angle, steps = corner.sides, use_duplicate = False)
def drawCornerAsArc(corner, bm):
    if corner.startx == WRONG_FLOAT or corner.starty == WRONG_FLOAT or corner.endx == WRONG_FLOAT or corner.endy == WRONG_FLOAT:
        return
    center = Vector((corner.x, corner.y, defaultZ))
    startPoint = Vector ((corner.startx, corner.starty, defaultZ))
    endPoint = Vector ((corner.endx, corner.endy, defaultZ))

    geomCalc = GeometryCalculator()
    angleDeg, angle = geomCalc.getPositiveAngleBetween3Points(startPoint, center, endPoint)

    spinAxis = Vector((0, 0, 1))
    v0 = bm.verts.new(startPoint)
    if corner.flipAngle:
        v0 = bm.verts.new(endPoint)
        angle = two_pi - angle
    result = bmesh.ops.spin(bm, geom = [v0], cent = center, axis = spinAxis, \
                                   angle = -angle, steps = corner.sides, use_duplicate = False)

def drawConnections(corners, connections, bm):
    connectionsLastIndex = len(connections) - 1
    cornersLastIndex = len(corners) - 1
    for i in range(cornersLastIndex):
        drawConnection(corners[i], corners[i + 1], connections[i], bm)
    if connectionsLastIndex == cornersLastIndex:
        drawConnection(corners[cornersLastIndex], corners[0], connections[cornersLastIndex], bm)

def drawTangentLineMixed(corner1, corner2, connection, bm):
    geomCalc = GeometryCalculator()
    inout = connection.inout
    corner1TangentPoint, corner2TangentPoint = calculateMixedLineTangentPoints(corner1, corner2, geomCalc, inout)
    makeEdgeBetweenCorners(corner1, corner2, corner1TangentPoint, corner2TangentPoint, bm)

def drawTangentLine(corner1, corner2, connection, bm):
    geomCalc = GeometryCalculator()
    inout = connection.inout

    if (corner1.radius == corner2.radius):
        drawTangentLineForEqualRadius(geomCalc, corner1, corner2, inout, bm)
    else:
        corner1TangentPoint, corner2TangentPoint = calculateLineTangentPoints(corner1, corner2, geomCalc, inout)
        makeEdgeBetweenCorners(corner1, corner2, corner1TangentPoint, corner2TangentPoint, bm)

def calculateLineTangentPoints(corner1, corner2, geomCalc, inout):
    c1Center = Vector((corner1.x, corner1.y, defaultZ))
    c2Center = Vector((corner2.x, corner2.y, defaultZ))
    centerVector, centerVectorLen = geomCalc.getVectorAndLengthFrom2Points(c1Center, c2Center)

    centerCircleRadius = 0.5 * centerVectorLen
    centerCircleCenter = c1Center + 0.5 * centerVector
    tempRadius = fabs(corner1.radius - corner2.radius)
    intersections = None
    largerCircle = None
    if (corner1.radius > corner2.radius):
        intersections = geomCalc.getCircleIntersections(c1Center, tempRadius, centerCircleCenter, centerCircleRadius)
        largerCircle = c1Center
    else:
        intersections = geomCalc.getCircleIntersections(centerCircleCenter, centerCircleRadius, c2Center, tempRadius)
        largerCircle = c2Center

    if intersections == None or len(intersections) == 1:
        assignCornerEndPoint(corner1, None)
        assignCornerStartPoint(corner2, None)
        return None, None

    tempTangencyPoint = intersections[0]
    if inout == 'Outer':
        tempTangencyPoint = intersections[0]
    elif inout == 'Inner':
        tempTangencyPoint = intersections[1]

    #tempTangencyPoint = geomCalc.getFarthestPointToRefPoint(intersections, Vector((0, 0, 0)))

    radialVector, radialVectorLength = geomCalc.getVectorAndLengthFrom2Points(largerCircle, tempTangencyPoint)

    c2TangentPoint = c2Center + radialVector * (corner2.radius / radialVectorLength)
    c1TangentPoint = c1Center + radialVector * (corner1.radius / radialVectorLength)
    return c1TangentPoint, c2TangentPoint

# calculateMixedLineTangentPoints
def calculateMixedLineTangentPoints(corner1, corner2, geomCalc, inout):
    c1Center = Vector((corner1.x, corner1.y, defaultZ))
    c2Center = Vector((corner2.x, corner2.y, defaultZ))
    r1 = corner1.radius
    r2 = corner2.radius
    c1TangentPoint = None
    c2TangentPoint = None

    centerVector, centerVectorLen = geomCalc.getVectorAndLengthFrom2Points(c1Center, c2Center)

    sumOfRadius = r1 + r2
    # It only makes sense to calculate In-Out tangent line if center vector lenght is higher then sum of radius
    if centerVectorLen <= sumOfRadius:
        return c1TangentPoint, c2TangentPoint


    Qc2Distance = centerVectorLen / (1 + (r1 / r2))
    c1QDistance = Qc2Distance * (r1 / r2)
    # Q is the point on C1C2 line which is intersected by the in-out tangent line
    Q = c1Center + (c1QDistance / centerVectorLen) * centerVector

    c1QVector, c1QVectorLen = geomCalc.getVectorAndLengthFrom2Points(c1Center, Q)

    firstHelperCircleRadius = 0.5 * c1QDistance
    firstHelperCircleCenter = c1Center + 0.5 * c1QVector
    firstCircleIntersections = None
    firstCircleIntersections = geomCalc.getCircleIntersections(c1Center, r1, firstHelperCircleCenter, firstHelperCircleRadius)

    Qc2Vector, Qc2VectorLen = geomCalc.getVectorAndLengthFrom2Points(Q, c2Center)
    secondHelperCircleRadius = 0.5 * Qc2Distance
    secondHelperCircleCenter = c2Center - 0.5 * Qc2Vector
    secondCircleIntersections = None
    secondCircleIntersections = geomCalc.getCircleIntersections(secondHelperCircleCenter, secondHelperCircleRadius, c2Center, r2)

    if inout == 'Outer-Inner':
        c1TangentPoint = firstCircleIntersections[0]
        c2TangentPoint = secondCircleIntersections[1]
    elif inout == 'Inner-Outer':
        c1TangentPoint = firstCircleIntersections[1]
        c2TangentPoint = secondCircleIntersections[0]

    return c1TangentPoint, c2TangentPoint

def drawTangentLineForEqualRadius(geomCalc, corner1, corner2, inout, bm):
    c1Vector = Vector((corner1.x, corner1.y, defaultZ))
    c2Vector = Vector((corner2.x, corner2.y, defaultZ))

    centerVector, centerVectorLen = geomCalc.getVectorAndLengthFrom2Points(c1Vector, c2Vector)
    perpendicularVector = geomCalc.getPerpendicularVector(centerVector)

    if (centerVectorLen == 0):
        return

    factor = corner1.radius / centerVectorLen
    if inout == 'Outer':
        factor = factor
    elif inout == 'Inner':
        factor = -factor
    v1Vector = c1Vector + perpendicularVector * factor
    v2Vector = c2Vector + perpendicularVector * factor

    makeEdgeBetweenCorners(corner1, corner2, v1Vector, v2Vector, bm)

def makeEdgeBetweenCorners(corner1, corner2, v1Vector, v2Vector, bm):
    if (v1Vector == None) or (v2Vector == None) :
        return

    v1 = bm.verts.new(v1Vector)
    v2 = bm.verts.new(v2Vector)
    assignCornerEndPoint(corner1, v1Vector)
    assignCornerStartPoint(corner2, v2Vector)
    bm.edges.new([v1, v2])

def drawConnection(corner1, corner2, connection, bm):
    if (connection.type == 'Arc'):
        drawTangentConnection = StrategyFactory.getDrawTangentStrategy(connection.inout)
        drawTangentConnection(corner1, corner2, connection, bm)
    elif (connection.type == 'Line'):
        drawTangentLine = StrategyFactory.getDrawTangentLineStrategy(connection.inout)
        drawTangentLine(corner1, corner2, connection, bm)

def assignCornerEndPoint(corner, endPoint):
    if endPoint != None:
        corner.endx = endPoint[0]
        corner.endy = endPoint[1]
        corner.endz = defaultZ
    else:
        corner.endx = WRONG_FLOAT
        corner.endy = WRONG_FLOAT
        corner.endz = WRONG_FLOAT

def assignCornerStartPoint(corner, startPoint):
    if startPoint != None:
        corner.startx = startPoint[0]
        corner.starty = startPoint[1]
        corner.startz = defaultZ
    else:
        corner.startx = WRONG_FLOAT
        corner.starty = WRONG_FLOAT
        corner.startz = WRONG_FLOAT

def drawTangentConnectionTemplate(corner1, corner2, connection, bm, getRadiusesForIntersections, getConnectionEndPoints):
    c1 = Vector((corner1.x, corner1.y, defaultZ))
    c2 = Vector((corner2.x, corner2.y, defaultZ))
    r1, r2 = getRadiusesForIntersections(connection.radius, corner1.radius, corner2.radius)

    geomCalc = GeometryCalculator()

    intersections = geomCalc.getCircleIntersections(c1, r1, c2, r2)
    if intersections == None:
        assignCornerEndPoint(corner1, None)
        assignCornerStartPoint(corner2, None)
        return

    center = None

    if len(intersections) == 1:
        center = intersections[0]
    elif len(intersections) == 2:
        if not connection.flipCenter:
            center = intersections[1]
        else:
            center = intersections[0]

    connectionStartPoint, connectionEndPoint = getConnectionEndPoints(geomCalc, center, c1, corner1.radius, c2, corner2.radius, connection.radius)
    
    assignCornerEndPoint(corner1, connectionStartPoint)
    assignCornerStartPoint(corner2, connectionEndPoint)

    angleDeg, angleRad = geomCalc.getPositiveAngleBetween3Points(connectionStartPoint, center, connectionEndPoint)
    if (angleDeg == None) or (angleRad == None):
        return
    if connection.flipAngle:
        angleRad = -(2 * pi - angleRad)

    spinAxis = Vector((0, 0, 1))
    v0 = bm.verts.new(connectionEndPoint)
    result = bmesh.ops.spin(bm, geom = [v0], cent = center, axis = spinAxis, \
                                   angle = angleRad, steps = connection.sides, use_duplicate = False)


def getRadiusesForOuterIntersections(connectionRadius, c1Radius, c2Radius):
    r1 = connectionRadius - c1Radius
    r2 = connectionRadius - c2Radius
    return r1, r2

def getRadiusesForInnerIntersections(connectionRadius, c1Radius, c2Radius):
    r1 = connectionRadius + c1Radius
    r2 = connectionRadius + c2Radius
    return r1, r2

def getRadiusesForOuterInnerIntersections(connectionRadius, c1Radius, c2Radius):
    r1 = connectionRadius - c1Radius
    r2 = connectionRadius + c2Radius
    return r1, r2

def getRadiusesForInnerOuterIntersections(connectionRadius, c1Radius, c2Radius):
    r1 = connectionRadius + c1Radius
    r2 = connectionRadius - c2Radius
    return r1, r2

def getConnectionEndPointsForOuterTangent(geomCalc, center, c1, c1radius, c2, c2radius, connectionRadius):
    connectionStartPoint = getFarthestTangencyPoint(geomCalc, center, c1, c1radius)
    connectionEndPoint = getFarthestTangencyPoint(geomCalc, center, c2, c2radius)
    return connectionStartPoint, connectionEndPoint

def getConnectionEndPointsForInnerTangent(geomCalc, center, c1, c1radius, c2, c2radius, connectionRadius):
    connectionStartPoint = getClosestTangencyPoint(geomCalc, c1, center, connectionRadius)
    connectionEndPoint = getClosestTangencyPoint(geomCalc, c2, center, connectionRadius)
    return connectionStartPoint, connectionEndPoint

def getConnectionEndPointsForInnerOuterTangent(geomCalc, center, c1, c1radius, c2, c2radius, connectionRadius):
    connectionStartPoint = getClosestTangencyPoint(geomCalc, c1, center, connectionRadius)
    connectionEndPoint = getFarthestTangencyPoint(geomCalc, center, c2, c2radius)
    return connectionStartPoint, connectionEndPoint

def getConnectionEndPointsForOuterInnerTangent(geomCalc, center, c1, c1radius, c2, c2radius, connectionRadius):
    connectionStartPoint = getFarthestTangencyPoint(geomCalc, center, c1, c1radius)
    connectionEndPoint = getClosestTangencyPoint(geomCalc, c2, center, connectionRadius)
    return connectionStartPoint, connectionEndPoint

    
def drawOuterTangentConnection(corner1, corner2, connection, bm):
    drawTangentConnectionTemplate(corner1, corner2, connection, bm, \
        getRadiusesForOuterIntersections, getConnectionEndPointsForOuterTangent)

def drawInnerTangentConnection(corner1, corner2, connection, bm):
    drawTangentConnectionTemplate(corner1, corner2, connection, bm, \
        getRadiusesForInnerIntersections, getConnectionEndPointsForInnerTangent)

def drawInnerOuterTangentConnection(corner1, corner2, connection, bm):
    drawTangentConnectionTemplate(corner1, corner2, connection, bm, \
        getRadiusesForInnerOuterIntersections, getConnectionEndPointsForInnerOuterTangent)

def drawOuterInnerTangentConnection(corner1, corner2, connection, bm):
    drawTangentConnectionTemplate(corner1, corner2, connection, bm, \
        getRadiusesForOuterInnerIntersections, getConnectionEndPointsForOuterInnerTangent)


def getLineCircleIntersections(geomCalc, RefPoint, Center, Radius):
    lineAB1 = geomCalc.getCoefficientsForLineThrough2Points(RefPoint, Center)
    lineCircleIntersections = None
    if RefPoint[0] == Center[0]:
        lineCircleIntersections = geomCalc.getLineCircleIntersectionsWhenXPerpendicular(RefPoint, Center, Radius)
    else:
        lineCircleIntersections = geomCalc.getLineCircleIntersections(lineAB1, Center, Radius)
    return lineCircleIntersections


def getClosestTangencyPoint(geomCalc, refPoint, center, radius):
    lineCircleIntersections = getLineCircleIntersections(geomCalc, refPoint, center, radius)
    if lineCircleIntersections == None:
        return None

    tangencyPoint = geomCalc.getClosestPointToRefPoint(lineCircleIntersections, refPoint)
    return tangencyPoint


def getFarthestTangencyPoint(geomCalc, refPoint, center, radius):
    lineCircleIntersections = getLineCircleIntersections(geomCalc, refPoint, center, radius)
    if lineCircleIntersections == None:
        return None

    tangencyPoint = geomCalc.getFarthestPointToRefPoint(lineCircleIntersections, refPoint)
    return tangencyPoint
