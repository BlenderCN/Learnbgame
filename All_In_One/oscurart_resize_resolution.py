# Compensa el tamanio de imagen al modificar el lente de la camara.


bl_info = {
    "name": "Resize Render Resolution",
    "author": "Oscurart",
    "version": (1, 0),
    "blender": (2, 66, 0),
    "location": "Search > Resize Resolution by Camera Angle",
    "description": "Resize render dimension by camera angle.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import math


def defResizeResolution(context, anguloInicio, anguloPrimero, resx, resy): 
    # calcula valores
    anguloActual= math.degrees(anguloInicio/ 2)
    proportionxy = resx  / resy
    
    opuesto = resx / 2
    adyacente = opuesto / math.tan(anguloInicio / 2)
    newx = (adyacente * math.tan(math.radians(anguloPrimero/2))) * 2

    # setea valores
    context.scene.render.resolution_x = newx
    context.scene.render.resolution_y = newx / proportionxy
    context.scene.camera.data.angle = math.radians(anguloPrimero)



class ResizeResolution(bpy.types.Operator):
    bl_idname = "scene.resize_resolution"
    bl_label = "Resize Resolution by Camera Angle"
    bl_options = {"REGISTER", "UNDO"}
    
    anguloPrimero = bpy.props.FloatProperty(name="Field of View", default=math.degrees(.8575), min=.01 )
        
    def execute(self, context):
        anguloInicio = context.scene.camera.data.angle    
        resx = context.scene.render.resolution_x
        resy = context.scene.render.resolution_y
        print(resx)
        defResizeResolution(context, anguloInicio, self.anguloPrimero, resx, resy)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ResizeResolution)


def unregister():
    bpy.utils.unregister_class(ResizeResolution)


if __name__ == "__main__":
    register()
