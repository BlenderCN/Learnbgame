import bpy
import mathutils
from .qobject import *


class Qcube(Qobject):
    basetype = 1

    def copyData(self, _op):
        newQ = Qcube(_op)
        return newQ

    def UpdateMesh(self):
        bmeshNew = bmesh.new()
        if self.isFlat:
            bmesh.ops.create_grid(bmeshNew,
                                x_segments=1,
                                y_segments=1,
                                size=1.0,
                                matrix=mathutils.Matrix.Translation((0.0, 0.0, 0.0)),
                                calc_uvs=True)
        else:
            transformS = GetTransformOffset(self.isCentered)
            bmesh.ops.create_cube(bmeshNew,
                                size=2.0,
                                matrix=transformS,
                                calc_uvs=True)

        bmeshNew.to_mesh(self.bMesh)
        self.bMesh.update()
        bpy.context.scene.update()
