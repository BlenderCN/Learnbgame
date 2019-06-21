import bpy
import bgl
import gpu
import mathutils
from gpu_extras.batch import batch_for_shader


def QWPlaneDrawHandler(wPlane, context):
    bgl.glLineWidth(2)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    coords = []

    for x in range(wPlane.numSteps * 2 + 1):
        coordX = wPlane.bRectMinMax[0] + x * wPlane.gridstep
        posX1 = mathutils.Vector((coordX, wPlane.bRectMinMax[0], 0)) 
        posX2 = mathutils.Vector((coordX, wPlane.bRectMinMax[1], 0))
        posY1 = mathutils.Vector((wPlane.bRectMinMax[0], coordX, 0)) 
        posY2 = mathutils.Vector((wPlane.bRectMinMax[1], coordX, 0))
        posX1 = wPlane.matrix @ posX1
        posX2 = wPlane.matrix @ posX2
        posY1 = wPlane.matrix @ posY1
        posY2 = wPlane.matrix @ posY2
        coords.extend([posX1,posX2, posY1, posY2])

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})

    shader.bind()
    shader.uniform_float("color", (0.655, 0.655, 0.655, 0.2))
    batch.draw(shader)

class WorkingPlane:
    Instance = None
    matrix = mathutils.Matrix()
    gridstep = 1.0
    origFloor = True
    isActive = False
    wasActive = False

    numSteps = 5
    bRectMinMax = (0, 0)

    def __init__(self, _context, _matrix):
        self.matrix = _matrix.copy()
        self.gridstep = _context.space_data.overlay.grid_scale_unit 
        edgeDist = self.numSteps * self.gridstep
        self.bRectMinMax = (-edgeDist, edgeDist)
        print("QWPlane created!")

    def SetMatrix(self, _matrix):
        self.matrix = _matrix.copy()

    def SetActive(self, _context, _state):
        if _state:
            self.gridstep = _context.space_data.overlay.grid_scale_unit 
            edgeDist = self.numSteps * self.gridstep
            self.bRectMinMax = (-edgeDist, edgeDist)
            args = (self, _context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(QWPlaneDrawHandler, args, 'WINDOW', 'POST_VIEW')
            self.origFloor = _context.space_data.overlay.show_floor
            _context.space_data.overlay.show_floor = False
            self.isActive = True
        else:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            _context.space_data.overlay.show_floor = self.origFloor
            self.isActive = False


    def ChangeStepDist(self, _distp):
        x = _distp[0]
        y = _distp[1]
        if x > y:
            self.gridstep = x
        else:
            self.gridstep = y
        edgeDist = self.numSteps * self.gridstep
        self.bRectMinMax = ( -edgeDist, edgeDist)

