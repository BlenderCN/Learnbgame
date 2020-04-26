import time
import bpy
print("Hello World") #Print will show in console


rs = bpy.context.scene.render
rs.resolution_x = 1000 #Direct modification of scene properties.
rs.resolution_y = 500
#Do be careful though as Blender will not tolerate the UI and this thread acessing the
# same resource. You have been warned.

#Note your context or your script will terminate.

time.sleep(12) #We can Have the operator going without interupting the drawing thread