import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader
import mathutils
import time
from .utilities.grid_utils import *
from .utilities.math_utils import *

redC = (0.984, 0.2, 0.318, 1.0)
greenC = (0.525, 0.824, 0.012, 1.0)
blueC = (0.157, 0.557, 0.988, 1.0)
vcolors = [greenC, greenC, redC, redC, blueC, blueC]

def QSpaceDrawHandler(qSpace, context):
    bgl.glLineWidth(2)
    pos = qSpace.wMatrix.translation
    mat = qSpace.wMatrix.to_3x3()
    vecX = pos + mat.col[0] 
    vecY = pos + mat.col[1] 
    vecZ = pos + mat.col[2] 

    coords = [pos, vecX, pos, vecY, pos, vecZ]
    shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords, "color": vcolors})

    shader.bind()
    batch.draw(shader)


class CoordSysClass:
    operator = None
    context = None
    lastHitresult = (False, None, None, None, None, None)
    isGridhit = False
    isModifiedMesh = False
    mesh_data = None
    wMatrix = mathutils.Matrix()
    isPropAxis = True

    def __init__(self, _context, _op, _isAxis):
        self.operator = _op
        self.context = _context
        self.isPropAxis = _isAxis
        if _isAxis:
            args = (self, _context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(QSpaceDrawHandler, args, 'WINDOW', 'POST_VIEW')
        print("CoordSysClass created!")

    def CleanUp(self):
        if self.isPropAxis and self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        print("SnappingClass cleaned!")

    def ToggleAxis(self, _state):
        if self.isPropAxis:
            if _state:
                if not self._handle:
                    args = (self, self.context)
                    self._handle = bpy.types.SpaceView3D.draw_handler_add(QSpaceDrawHandler, args, 'WINDOW', 'POST_VIEW')
            else:
                if self._handle:
                    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                    self._handle = None





    def VecToMatrix(self, _vecZ, _pos):
        vecZ = _vecZ.normalized()
        if abs(vecZ[2]) == 1:
            vecY = vecZ.cross(mathutils.Vector((1.0, 0.0, 0.0)))
        else:
            vecY = vecZ.cross(mathutils.Vector((0.0, 0.0, -1.0)))
        vecY.normalize()
        vecX = vecY.cross(vecZ)
        vecX.normalize()

        matrix = mathutils.Matrix()
        matrix[0].xyz = vecX[0], vecY[0], vecZ[0]
        matrix[1].xyz = vecX[1], vecY[1], vecZ[1]
        matrix[2].xyz = vecX[2], vecY[2], vecZ[2]
        matrix.translation = _pos
        return matrix

    # raycast into scene from mouse pos
    def HitScene(self, context, coord):
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
        hitresult = scene.ray_cast(context.view_layer, ray_origin, view_vector)
        return hitresult

    def ResetResult(self):
        self.lastHitresult = (False, None, None, None, None, None)

    # main function
    def GetCoordSys(self, context, coord, isoriented):
        # time_start = time.time() # timetest
        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(True)
        hitresult = self.HitScene(context, coord)
        cSysMatrix = None
        # if object hit
        if hitresult[0] and hitresult[4].type == 'MESH':
            # if oriented
            if isoriented:
                if hitresult[4] != self.lastHitresult[4]:
                    # check if modified object
                    if len(hitresult[4].modifiers) != 0:
                        self.mesh_data = hitresult[4].to_mesh(context.depsgraph, apply_modifiers=True)
                        self.mesh_data.name = "TempMesh"
                        self.isModifiedMesh = True
                    elif self.isModifiedMesh:
                        bpy.data.meshes.remove(self.mesh_data)
                        self.mesh_data = None
                        self.isModifiedMesh = False
                if self.isModifiedMesh:
                    cSysMatrix = self.GetOrientedAlign(hitresult, self.mesh_data)
                else:
                    cSysMatrix = self.GetOrientedAlign(hitresult, hitresult[4].data)
            # if axis aligned
            else:
                cSysMatrix = self.GetAxisAlign(hitresult)
            self.isGridhit = False
        # if gridhit       
        else:     
            if self.isModifiedMesh:
                bpy.data.meshes.remove(self.mesh_data, do_unlink=True)
                self.isModifiedMesh = False
                self.mesh_data = None
            if self.operator.isWorkingPlane:
                cSysMatrix = self.GetWPlaneAlign(context, coord, self.operator.workingplane.matrix)
            else:
                cSysMatrix = self.GetGridAlign(context, coord)
 
            self.isGridhit = True
        if self.operator.toolstage != 0:
            self.operator.qObject.HideObject(False)
        self.lastHitresult = hitresult
        self.wMatrix = cSysMatrix 
        return cSysMatrix

    # AXIS ALIGNED
    def GetAxisAlign(self, _hitresult):
        ret_matrix = self.VecToMatrix(_hitresult[2], _hitresult[1])
        return ret_matrix

    # GRID ALIGNED
    def GetGridAlign(self, context, coord):
        # get view ray
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

        # check grid and collide with view ray
        grid_vector = GetGridVector(context)
        hitpoint = LinePlaneCollision(view_vector, ray_origin, (0.0, 0.0, 0.0), grid_vector)

        # create matrix
        grid_vector = mathutils.Vector(grid_vector)
        ret_matrix = self.VecToMatrix(grid_vector, hitpoint)
        return ret_matrix  

    # WPLANE ALIGNED
    def GetWPlaneAlign(self, context, coord, _matrix):
        # get view ray
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        view_vector = region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

        grid_vector = _matrix.col[2].xyz
        hitpoint = LinePlaneCollision(view_vector, ray_origin, _matrix.translation, grid_vector)

        # create matrix
        ret_matrix = _matrix.copy()
        ret_matrix.translation = hitpoint
        return ret_matrix  

    # ORIENTED ALIGN
    def GetOrientedAlign(self, _hitresult, meshData):
        verts = self.GetTargetPolyVerts(_hitresult, meshData)

        if _hitresult[4] == self.lastHitresult[4] and _hitresult[2] == self.lastHitresult[2]:
                self.wMatrix.translation = _hitresult[1]
                return self.wMatrix
        else:
            # create matrix from face normal
            matrix = self.VecToMatrix(_hitresult[2], _hitresult[1])
            mat_inv = matrix.inverted()

            # transform verts to poly space
            vertsL = []
            for v in verts:
                v2 = mat_inv @ v
                v2[2] = 0.0
                vertsL.append(v2)

            # calc best rotation
            verts2DL = [(p[0], p[1]) for p in vertsL]
            bboxangle = mathutils.geometry.box_fit_2d(verts2DL)
            mat_rot = mathutils.Matrix.Rotation(-bboxangle, 4, 'Z')
            ret_matrix = matrix @ mat_rot   
            return ret_matrix

    # get vertices from polygon in world space
    def GetTargetPolyVerts(self, _hitresult, meshData):
        verts = []
        meshFace = meshData.polygons[_hitresult[3]]
        matrix = _hitresult[4].matrix_world.copy()
        for v in meshFace.vertices:
            pos = _hitresult[4].matrix_world @ (meshData.vertices[v].co)
            verts.append(pos)
        return verts