import bpy
import bmesh
import gpu
from .op_mesh import *
from .qsphere import *


# box create op new
class SphereCreateOperator(MeshCreateOperator):
    bl_idname = "object.sphere_create"
    bl_label = "Sphere Create Operator"

    drawcallback = draw_callback_sphere
    objectType = 3
    basetype = 4
    isSmooth = True
    isCentered = True

    meshSegments = 16
    originalSegments = 16

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = QSphere(self)

    # toggle smooth mesh
    def ToggleMeshSmooth(self):
        self.isSmooth = self.qObject.ToggleSmoothFaces()

    def ChangeMeshSegments(self):
        allstep = int((self.mouse_pos[0] - self.mouseStart[0]) // self.inc_px)
        prevalue = max(4, min(128, self.qObject.originalSegments + allstep))
        if prevalue != self.qObject.meshSegments:
            self.qObject.meshSegments = prevalue
            self.mouseEnd_x = self.mouseStart[0] + ((prevalue - self.qObject.originalSegments) * self.inc_px)
            self.qObject.UpdateMesh()
        self.meshSegments = self.qObject.meshSegments
