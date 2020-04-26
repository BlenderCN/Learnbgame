import bpy
import gpu
import mathutils
from mathutils import Vector
import numpy
import math
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from .utilities.raycast_utils import *
from .utilities.grid_utils import *
from .utilities.draw_utils import *


def SnapDrawHandler(snapClass, context):
    if snapClass.isSnapActive:
        region = context.region
        rv3d = context.region_data
        # draw snap targets
        posBatch = []
        for pos in snapClass.snaptargets:
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            posBatch.append(pos2D)
        if snapClass.isPolyGridActive:
            cColor = (0.12, 0.56, 1.0, 0.7)
        else:
            cColor = (1.0, 0.56, 0.0, 0.7)
        draw_multicircles_fill_2d(positions=posBatch, color=cColor, radius=5, segments=12, alpha=True)
        # draw closest target
        if snapClass.closestPoint is not None:
            pos = snapClass.closestPoint
            pos2D = location_3d_to_region_2d(region, rv3d, pos, default=None)
            draw_circle_fill_2d(position=pos2D, color=(1.0, 1.0, 1.0, 1.0), radius=6, segments=12, alpha=True)


class SnappingClass:
    operator = None
    context = None
    snaptargets = []
    edgediv = 2
    orig_edgediv = 1
    closestPoint = None
    isSnapActive = False
    isPolyGridActive = False
    gridMatrix = None

    def __init__(self, _operator, _qspace,  _context, _edgediv):
        self.edgediv = _edgediv
        self.context = _context
        self.operator = _operator
        self.coordsys = _qspace
        args = (self, _context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(SnapDrawHandler, args, 'WINDOW', 'POST_PIXEL')
        print("SnappingClass created!")

    def CleanUp(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        print("SnappingClass cleaned!")

    # set snapping active
    def SetState(self, _state, _mousepos):
        if _state:
            self.isSnapActive = True
            self.CheckSnappingTarget(self.context, _mousepos)
        else:
            self.isSnapActive = False
            self.snaptargets = []

    # set snapping active
    def ToggleState(self, _mousepos):
        if self.isSnapActive:
            self.isSnapActive = False
            self.snaptargets = []
        else:
            self.isSnapActive = True
            self.CheckSnappingTarget(self.context, _mousepos)


    def SetPolyGrid(self, _state, _mousepos):
        if _state:
            self.isPolyGridActive = True
        else:
            self.isPolyGridActive = False
        if self.isSnapActive:
            self.CheckSnappingTarget(self.context, _mousepos)

    # check snapping target and update list
    def CheckSnappingTarget(self, context, coord):
        if self.coordsys.isGridhit:
            if self.operator.isWorkingPlane:
                self.GetGridVerts(context, self.operator.workingplane.matrix.translation, self.operator.workingplane.gridstep )
            else:
                self.GetGridVerts(context, mathutils.Vector((0, 0, 0)), context.space_data.overlay.grid_scale_unit )
        else:
            self.UpdateSnapPoints()


    # recalculate points at edge divison user input
    def UpdateSnapPoints(self):
        self.snaptargets = []
        meshdata = None
        if self.coordsys.isModifiedMesh:
            meshdata = self.coordsys.mesh_data
        else:
            meshdata = self.coordsys.lastHitresult[4].data

        if self.isPolyGridActive:
            self.GeneratePolyPoints(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], self.edgediv, meshdata)
        else:
            self.AddTargetPolyVerts(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], meshdata)
            self.AddTargetPolyEdges(self.coordsys.lastHitresult[4], self.coordsys.lastHitresult[3], self.edgediv, meshdata)
        self.GetClosestPoint(self.coordsys.lastHitresult[1])

    # get closest point to a given position WP
    def GetClosestPoint(self, point):
        if len(self.snaptargets) != 0:
            actDist = numpy.linalg.norm(self.snaptargets[0]-point)
            actID = 0
            counter = 1
            itertargets = iter(self.snaptargets)
            next(itertargets)
            for pos in itertargets:
                dist = numpy.linalg.norm(pos-point)
                if dist < actDist:
                    actID = counter
                    actDist = dist
                counter += 1
            self.closestPoint = self.snaptargets[actID]

    def GetClosestPointOnGrid(self, matrix):
        matrix_inv = matrix.inverted()
        pointS = matrix_inv @ self.closestPoint
        pointS[2] = 0.0
        return pointS

    def GetGridVerts(self, context, _position, _girdsize):
        self.snaptargets = []
        gridhit = self.operator.wMatrix.translation
        matW = self.operator.wMatrix.copy()
        matW.translation = _position
        gridcorners = self.GetGridBRect(_girdsize, matW, gridhit)
        gridpointsall = self.GeneratePoints(gridcorners[0], gridcorners[1], matW, self.edgediv)
        self.snaptargets.extend(gridpointsall)
        self.GetClosestPoint(gridhit)

    # get target grid bounding rect corners in GridSpace
    def GetGridBRect(self, gridstep, gridmatrix, position):
        mat = gridmatrix.copy()
        mat_inv = mat.inverted()
        pos = mathutils.Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        return [Vector((Xf, Yf, 0.0)), Vector((Xc, Yc, 0.0))]

    # generate sub-grid points on grid
    def GeneratePoints(self, p1, p2, matrix, _steps):
        if self.isPolyGridActive:
            steps = _steps
        else:
            steps = 1
        points = []
        stepX = (p2.x - p1.x) / steps
        stepY = (p2.y - p1.y) / steps
        for x in range(steps+1):
            for y in range(steps+1):
                posX = p1.x + x * stepX
                posY = p1.y + y * stepY
                point = Vector((posX, posY, 0.0))
                point = matrix @ point
                points.append(point)
        return points


    # get target grid corner points in GridSpace
    def GetGridCorners(self, gridstep, gridmatrix, position):
        mat_inv = gridmatrix.inverted()
        pos = mathutils.Vector(position)
        pos = mat_inv @ pos
        Xf = math.floor(pos.x / gridstep) * gridstep
        Yf = math.floor(pos.y / gridstep) * gridstep
        Xc = Xf + gridstep
        Yc = Yf + gridstep
        points = [Vector((Xf, Yf, 0.0)), Vector((Xc, Yf, 0.0)), Vector((Xc, Yc, 0.0)), Vector((Xf, Yc, 0.0))]
        return points

    # get target polygon data on object for snap
    def AddTargetPolyVerts(self, object, faceID, meshData):
        meshFace = meshData.polygons[faceID]
        matrix = object.matrix_world.copy()
        for v in meshFace.vertices:
            pos = matrix @ (meshData.vertices[v].co)
            self.snaptargets.append(pos)

    # get target polygon data on object for snap
    def AddTargetPolyEdges(self, object, faceID, edgeDiv, meshData):
        mesh_data = meshData
        meshFace = mesh_data.polygons[faceID]
        matrix = object.matrix_world.copy()
        for ek in meshFace.edge_keys:
            edge = mesh_data.edges[mesh_data.edge_keys.index(ek)]
            vert1 = mesh_data.vertices[edge.vertices[0]].co
            vert2 = mesh_data.vertices[edge.vertices[1]].co
            vertc = (vert1 + vert2) / 2
            for d in range(1, edgeDiv):
                div = d / edgeDiv
                dPoint_X = vert1[0] + div * (vert2[0] - vert1[0])
                dPoint_Y = vert1[1] + div * (vert2[1] - vert1[1])
                dPoint_Z = vert1[2] + div * (vert2[2] - vert1[2])
                # transform to world space
                vec = mathutils.Vector((dPoint_X, dPoint_Y, dPoint_Z))
                vec = matrix @ vec
                self.snaptargets.append(vec)

    # generate sub-grid points on grid
    def GeneratePolyPoints(self, object, faceID, steps, meshData):
        points = []
        bbox = self.GetPolyOBB(object, faceID, meshData)
        centerX = (bbox[0].x + bbox[1].x) / 2
        centerY = (bbox[0].y + bbox[1].y) / 2
        stepX = (bbox[1].x - bbox[0].x) / steps
        stepY = (bbox[1].y - bbox[0].y) / steps
        for x in range(steps+1):
            for y in range(steps+1):
                posX = bbox[0].x + x * stepX
                posY = bbox[0].y + y * stepY
                point = Vector((posX, posY, 0.0))
                point = self.coordsys.wMatrix @ point
                self.snaptargets.append(point)

    # get oriented bbox for poly
    def GetPolyOBB(self, object, faceID, meshData):
        verts = self.GetTargetPolyVerts(object, faceID, meshData)
        mat_inv = self.coordsys.wMatrix.inverted()
        # transform verts to poly space
        vertsL = []
        for v in verts:
            v2 = mat_inv @ v
            v2[2] = 0.0
            vertsL.append(v2)
        # calc brect
        LocBrect = GetBRect(vertsL)
        return LocBrect

    # get target polygon data on object for snap
    def GetTargetPolyVerts(self, object, faceID, meshData):
        verts = []
        meshFace = meshData.polygons[faceID]
        for v in meshFace.vertices:
            pos = object.matrix_world @ (meshData.vertices[v].co)
            verts.append(pos)
        return verts
