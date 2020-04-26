#----------------------------------------------------------
# File mysphere.py
#----------------------------------------------------------
import bpy
 
def makeMesh(z):
    bpy.ops.mesh.primitive_ico_sphere_add(location=(0,0,z))
    return bpy.context.object
 
if __name__ == "__main__":
    ob = makeMesh(3)
    print(ob, "created")