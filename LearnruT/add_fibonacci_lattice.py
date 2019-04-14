import bpy
import math
import mathutils

from bpy.props import *

def align_matrix(context):
    loc = mathutils.Matrix.Translation(context.scene.cursor.location)
    obj_align = context.preferences.edit.object_align
    
    if (context.space_data.type == 'VIEW_3D'
        and obj_align == 'VIEW'):
        rot = context.space_data.region_3d.view_matrix.to_3x3().inverted().to_4x4()
    else:
        rot = mathutils.Matrix()
        
    result = loc @ rot
    
    return result

class add_mesh_fibonacci_lattice(bpy.types.Operator):
    """"""
    bl_idname = "mesh.fibonacci_lattice_add"
    bl_label = "Add Fibonacci lattice"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    bl_description = "adds Fibonacci lattice"
  
    # Whether to add or update.
    edit : BoolProperty(name="",
        description="",
        default=False,
        options={'HIDDEN'})
    
    # Number of lattice points
    fl_Num_Points : IntProperty(attr='fl_Num_Points',
        name='Number of points', default = 50,
        min = 1, soft_min = 1,
        description='Number of points to be distributed on Fibonacci lattice')
       
    # Radius
    fl_Radius : FloatProperty(attr='fl_Radius',
        name='Radius', default = 1,
        min = 0, soft_min = 0,
        description='Sphere which the Fibonacci lattice will be wrapped around')

    fl_Edges : BoolProperty(attr='fl_Edges',
        name="Generate edges", default = False,
        description="Generate edges for lattice spiral (uncheck for vertices only)")
                        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        col.prop(self, 'fl_Num_Points')
        col.prop(self, 'fl_Radius')
        col.prop(self, 'fl_Edges')

    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return context.scene != None

    ##### EXECUTE #####
    def execute(self, context):
        vertices = []
        edges = []
        
        offset = 2.0 / self.fl_Num_Points
        increment = math.pi * (3.0 - math.sqrt(5.0))
        
        for i in range(self.fl_Num_Points):
            z = ((i * offset) - 1.0) + (offset / 2.0)
            r = math.sqrt(1.0 - pow(z, 2.0))
            
            phi = ((i + 1) % self.fl_Num_Points) * increment
            
            x = math.cos(phi) * r
            y = math.sin(phi) * r
            
            vertices.append((self.fl_Radius * x, self.fl_Radius * y, self.fl_Radius * z))
        
        if self.fl_Edges:
            for i in range(self.fl_Num_Points - 1):
                edges.append([i, i + 1])

        fiblat_mesh = bpy.data.meshes.new("FibonacciLatticeMesh")
        fiblat_mesh.from_pydata(vertices, edges, [])
        fiblat_mesh.update()

        fiblat_object = bpy.data.objects.new("FibonacciLattice", fiblat_mesh)
        fiblat_object.matrix_world = align_matrix(context)

        scene = bpy.context.scene
        scene.collection.objects.link(fiblat_object)
        
        bpy.ops.object.select_all(action='DESELECT')
        fiblat_object.select_set(True)
        
        return {'FINISHED'}
        
    ##### INVOKE #####
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


def add_fibonacci_lattice_button(self, context):
    self.layout.operator(add_mesh_fibonacci_lattice.bl_idname, text="Fib. lattice", icon="PLUGIN")

def register():
    bpy.utils.register_class(add_mesh_fibonacci_lattice)
    bpy.types.VIEW3D_MT_mesh_add.append(add_fibonacci_lattice_button)

def unregister():
    bpy.utils.unregister_class(add_mesh_fibonacci_lattice)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_fibonacci_lattice_button)

if __name__ == "__main__":
    register()