bl_info = {
    "name": "Fibonacci Lattice",
    "author": "Jan Pinter",
    "version": (3, 9),
    "blender": (2, 63, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add Fibonacci lattice mesh",
    "category": "Add Mesh",
}

if "bpy" in locals():
    import importlib
    importlib.reload(FibonacciLattice)
else:
    from add_fibonacci_lattice import FibonacciLattice

import bpy

################################################################################
##### REGISTER #####

def add_fibonacci_lattice_button(self, context):
    self.layout.operator(FibonacciLattice.add_mesh_fibonacci_lattice.bl_idname, text="Fib. lattice", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(add_fibonacci_lattice_button)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(add_fibonacci_lattice_button)

if __name__ == "__main__":
    register()
