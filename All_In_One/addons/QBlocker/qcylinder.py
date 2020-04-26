import bpy
import mathutils
from .qobject import *


class QCylinder(Qobject):
    basetype = 3
    isSmooth = True

    def copyData(self, _op):
        newQ = QCylinder(_op)
        return newQ

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        if self.isFlat:
            bmesh.ops.create_circle(bmeshNew,
                                    segments=self.meshSegments,
                                    cap_ends=True,
                                    cap_tris=False,
                                    radius=1.0,
                                    matrix=mathutils.Matrix.Translation((0.0, 0.0, 0.0)),
                                    calc_uvs=True)
        else:
            transformS = GetTransformOffset(self.isCentered)
            bmesh.ops.create_cone(bmeshNew,
                                    segments=self.meshSegments,
                                    cap_ends=True,
                                    cap_tris=False,
                                    diameter1=1.0,
                                    diameter2=1.0,
                                    depth=2.0,
                                    matrix=transformS,
                                    calc_uvs=True)
        bmeshNew.to_mesh(self.bMesh)
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        self.bMesh.update()
        bpy.context.scene.update()
