import bpy
import bmesh
import gpu
from .op_mesh import *
from .qcylinder import *


# box create op new
class CylinderCreateOperator(MeshCreateOperator):
    bl_idname = "object.cylinder_create"
    bl_label = "Cylinder Create Operator"

    drawcallback = draw_callback_cylinder
    objectType = 2
    basetype = 3
    isSmooth = True
    isCentered = False

    meshSegments = 16
    originalSegments = 16

    # create Qobject tpye
    def CreateQobject(self):
        self.qObject = QCylinder(self)

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
