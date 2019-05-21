import math
import bpy
from arnold import *
from . import utils
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty

#################
# Camera
################
Cam = bpy.types.Camera
Cam.BtoA_aperture_size = FloatProperty(name="Aperture",description="Aperture Size",
                        min = 0,max=100,default=0)
Cam.BtoA_aperture_blades =  IntProperty(
        name="Aperture Blades", description="Blades",
        min=0, max=16, default=0)

from bl_ui import properties_data_camera
cc = properties_data_camera
for member in dir(properties_data_camera):
    subclass = getattr(properties_data_camera, member)
    try:
        if subclass.bl_label != "Lens":
            subclass.COMPAT_ENGINES.add('BtoA')
    except:
        pass

class BtoA_camera_lens(cc.CameraButtonsPanel, bpy.types.Panel):
    bl_label = "Lens"
    COMPAT_ENGINES = {'BtoA'}

    def draw(self, context):
        layout = self.layout

        cam = context.camera

        layout.prop(cam, "type", expand=True)

        split = layout.split()

        col = split.column()
        if cam.type == 'PERSP':
            if cam.lens_unit == 'MILLIMETERS':
                col.prop(cam, "lens")
            elif cam.lens_unit == 'DEGREES':
                col.prop(cam, "angle")
            col = split.column()
            col.prop(cam, "lens_unit", text="")

        elif cam.type == 'ORTHO':
            col.prop(cam, "ortho_scale")

        col = layout.column()
        if cam.type == 'ORTHO':
            if cam.use_panorama:
                col.alert = True
            else:
                col.enabled = False

        col.prop(cam, "use_panorama")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Shift:")
        col.prop(cam, "shift_x", text="X")
        col.prop(cam, "shift_y", text="Y")

        col = split.column(align=True)
        col.label(text="Clipping:")
        col.prop(cam, "clip_start", text="Start")
        col.prop(cam, "clip_end", text="End")

        layout.label(text="Depth of Field:")

        split = layout.split()
        split.prop(cam, "dof_object", text="")

        col = split.column()

        if cam.dof_object != None:
            col.enabled = False
        col.prop(cam, "dof_distance", text="Distance")
        
        split = layout.split()
        split.prop(cam,"BtoA_aperture_size")
        split.prop(cam,"BtoA_aperture_blades")

del properties_data_camera


class Camera():
    def __init__(self,render):
        self.scene  = bpy.context.scene
        self.camera = bpy.data.cameras[self.scene.camera.name]
        self.render = render
 
    def writeCamera(self):

        #create the node
        acam = AiNode(b"persp_camera")
        self.ArnoldCamera = acam
        self.name = self.camera.name
        AiNodeSetStr(acam,b"name",self.name.encode('utf-8'))
 
        # FOV
        if self.render.size_x > self.render.size_y:
            self.fov = self.camera.angle
        else:
            FovV = 2.0 * ( math.atan( ( self.render.size_y / 2.0 ) / self.camera.angle ) )
            self.fov = ( self.render.size_x / 2.0 ) / math.tan( FovV / 2.0 )
       
        fovAr = AiArrayAllocate(1, 1, AI_TYPE_FLOAT)
        AiArraySetFlt(fovAr, 0, math.degrees(self.fov))
        AiNodeSetArray(acam,b"fov",fovAr)
        
        #AiNodeSetFlt(acam,b"aspec_ratio",self.render.size_x/self.render.size_y)
        # matrix
        matrices = AiArrayAllocate(1, 1, AI_TYPE_MATRIX);
        bmatrix= self.scene.camera.matrix_world.copy()
        #bmatrix = Matrix.Rotation(math.radians(-90),4,'X')  * bmatrix 
        matrix = utils.getYUpMatrix(bmatrix)
        AiArraySetMtx(matrices,  0 , matrix)
        AiNodeSetArray(acam, b"matrix", matrices)
        # clipping
        AiNodeSetFlt(acam,b"near_clip",self.camera.clip_start)
        AiNodeSetFlt(acam,b"far_clip",self.camera.clip_end)
        # DOF
        AiNodeSetFlt(acam,b"aperture_size",self.camera.BtoA_aperture_size)
        fpAr = AiArrayAllocate(1, 1, AI_TYPE_FLOAT)
        AiArraySetFlt(fpAr, 0, self.camera.dof_distance)
        AiNodeSetArray(acam,b"focus_distance",fpAr)
