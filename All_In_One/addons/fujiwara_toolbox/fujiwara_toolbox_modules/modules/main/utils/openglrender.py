import bpy
import os

dir = os.path.dirname(bpy.data.filepath)
renderdir = dir + os.sep + "render" + os.sep 
renderpath = renderdir + "GLRENDERTEST" + ".png"
bpy.context.scene.render.filepath = renderpath



# bpy.ops.render.opengl("INVOKE_DEFAULT",view_context=True,write_still=True)
bpy.ops.render.opengl(write_still=True)

