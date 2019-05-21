bl_info = {
    "name": "Matrix Extrude Add-on",
    "author" : "Prof. M.",
    "version" : (1, 0, 0),
    "blender" : (2, 7, 9),
    "description" : "Repeatedly extrude, move, scale and rotate selected faces",    
    "category": "Mesh",
    "support": "TESTING",
    "location" : "View 3D > Edit Mode > Mesh",
}

import bpy

class MatrixExtrude(bpy.types.Operator):
    bl_idname = "mesh.matrix_extrude"
    bl_label = "Matrix Extrude selected faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for i in range(5):
            bpy.ops.mesh.extrude_region_shrink_fatten(
                MESH_OT_extrude_region={"mirror":False},
                TRANSFORM_OT_shrink_fatten={
                    "value":-0.5,
                    "use_even_offset":False,
                    "mirror":False,
                    "proportional":'DISABLED',
                    "proportional_edit_falloff":'SMOOTH',
                    "proportional_size":0.0001})
            bpy.ops.transform.resize(
                value=(0.777742, 0.777742, 0.777742), 
                constraint_axis=(False, False, False), 
                constraint_orientation='LOCAL', 
                mirror=False, 
                proportional='DISABLED', 
                proportional_edit_falloff='SMOOTH', 
                proportional_size=1)
            bpy.ops.transform.rotate(
                value=0.220425, 
                axis=(-0.521318, -0.822086, 0.228913), 
                constraint_axis=(False, False, False), 
                constraint_orientation='LOCAL', 
                mirror=False, proportional='DISABLED', 
                proportional_edit_falloff='SMOOTH', 
                proportional_size=1)
        return {'FINISHED'}

def register():
    print("Registering Matrix Extrude")
    bpy.utils.register_class(MatrixExtrude)

def unregister():
    print("Unregistering Matrix Extrude")
    bpy.utils.unregister_class(MatrixExtrude)