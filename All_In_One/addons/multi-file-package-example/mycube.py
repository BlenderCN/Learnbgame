#----------------------------------------------------------
# File mycube.py
#----------------------------------------------------------
import bpy
 
def makeMesh(z):
    bpy.ops.mesh.primitive_cube_add(location=(0,0,z))
    return bpy.context.object
 
if __name__ == "__main__":
    ob = makeMesh(1)
    print(ob, "created")