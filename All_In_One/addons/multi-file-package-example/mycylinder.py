#----------------------------------------------------------
# File mycylinder.py
#----------------------------------------------------------
import bpy
 
def makeMesh(z):
    bpy.ops.mesh.primitive_cylinder_add(location=(0,0,z))
    return bpy.context.object
 
if __name__ == "__main__":
    ob = makeMesh(5)
    print(ob, "created")