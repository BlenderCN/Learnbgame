bl_info = {
    "name": "Staircase",
    "author": "James Jacob" ,
    "version": (1, 1),
    "blender": (2, 78, 0),
    "location": "View3D > Add > Mesh > Staircase",
    "description": "A simple staircase generator.",
    "category": "Add Mesh",
    }


import bpy
from bpy.types import Operator

class Staircase(Operator):
    """Create a Staircase"""
    bl_idname = "mesh.add_staircase"
    bl_label = "Add Staircase"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        i=1   
        while(i<=20):
            bpy.ops.mesh.primitive_cube_add(location=(0,i,i))
            bpy.context.selected_objects[0].name='staircase'+str(i)
            bpy.ops.object.editmode_toggle()
            bpy.ops.transform.resize(value=(6,1,1))
            bpy.ops.object.editmode_toggle()
            i+=2
        bpy.ops.object.select_pattern(pattern="staircase*")
        bpy.ops.object.join()
        bpy.context.selected_objects[0].name='staircase'
        return {'FINISHED'} 


# Registration
def add_staircase_button(self, context):
    self.layout.operator(
        Staircase.bl_idname,
        text="Staircase",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(Staircase)
    bpy.types.INFO_MT_mesh_add.append(add_staircase_button)

def unregister():
    bpy.utils.unregister_class(Staircase)
    bpy.types.INFO_MT_mesh_add.remove(add_staircase_button)


if __name__ == "__main__":
    register()