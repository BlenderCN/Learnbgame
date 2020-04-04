

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    
    edges = []
    
    verts = [(1.0, 0.9999999403953552, -1.0), (1.0, -1.0, -1.0), (-1.0000001192092896, -0.9999998211860657, -1.0), (-0.9999996423721313, 1.0000003576278687, -1.0), (1.0000004768371582, 0.999999463558197, 1.0), (0.9999993443489075, -1.0000005960464478, 1.0), (-1.0000003576278687, -0.9999996423721313, 1.0), (-0.9999999403953552, 1.0, 1.0), (0.9999998807907104, -5.364418029785156e-07, 1.0), (2.384185791015625e-07, 0.9999997615814209, 1.0), (-5.364418029785156e-07, -1.0000001192092896, 1.0), (-1.0000001192092896, 1.7881393432617188e-07, 1.0), (-1.4901161193847656e-07, -1.7881393432617188e-07, 2.5804858207702637)]
    faces = [(0, 1, 2, 3), (12, 11, 6, 10), (0, 4, 8, 5, 1), (1, 5, 10, 6, 2), (2, 6, 11, 7, 3), (4, 0, 3, 7, 9), (8, 12, 10, 5), (4, 9, 12, 8), (9, 7, 11, 12)]

        
          
    try:
        
        mesh = bpy.data.meshes.new(name="New Object Mesh")
        mesh.from_pydata(verts, edges, faces)
        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        object_data_add(context, mesh, operator=self)
    except:
        print("select one symbol")

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new  Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "cube cone"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Object",
        icon='PLUGIN')

def menu_draw(self, context):
        self.layout.operator(OBJECT_OT_add_object.bl_idname)


        
    

def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_draw)


if __name__ == "__main__":
    register()