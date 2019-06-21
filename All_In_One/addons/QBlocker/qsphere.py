import bpy
import mathutils
from .qobject import *


class QSphere(Qobject):
    basetype = 4
    isSmooth = True
    isCentered = True

    def copyData(self, _op):
        newQ = QSphere(_op)

        return newQ

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        transformS = GetTransformOffset(self.isCentered)
        bmesh.ops.create_uvsphere(bmeshNew,
                                  u_segments=self.meshSegments,
                                  v_segments=int(self.meshSegments / 2),
                                  diameter=1.0,
                                  matrix=transformS,
                                  calc_uvs=True)
        bmeshNew.to_mesh(self.bMesh)
        self.bMesh.auto_smooth_angle = 1.386
        self.SetSmoothFaces()
        self.bMesh.update()
        bpy.context.scene.update()
