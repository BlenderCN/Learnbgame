# Just a simple test script, based on a web Blender scripting tutorial(fixed)
bl_info={
        "name": "Create Cube at Cursor For Test",
        "author": "Merzliutin Mikhail",
        "category": "Add Mesh",
        "version": (0, 2),
        "location": "View3D > Add > Mesh",
       }
 

import bpy
from math import sin, cos, radians


def create_cube_ring(coordinates, size, radius):
    addCubeMethod = bpy.ops.mesh.primitive_cube_add
    if not addCubeMethod:
        return

    layers = [False] * 20
    layers[0] = True
    
    anglesInRadians = [radians(degree) for degree in range(0, 360, 36)]
    
    for angle in anglesInRadians:
        x = coordinates.x + radius * cos(angle)
        y = coordinates.y + radius * sin(angle)
        z = coordinates.z
        addCubeMethod(location=(x, y, z), layers=layers, radius=size)


class TutorialCreateCubesRing(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.tutorial_cubes_ring"
    bl_label = "Cubes Ring At Cursor"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        create_cube_ring(context.scene.cursor_location, .5, 5)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(TutorialCreateCubesRing.bl_idname, icon='MESH_CUBE')

def register():
    bpy.utils.register_class(TutorialCreateCubesRing)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TutorialCreateCubesRing)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.tutorial_cubes_ring()
    
unregister()