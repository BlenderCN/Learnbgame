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

    segment_count = bpy.props.IntProperty(
        name="Segments",
        description="Number of segments to extrude",
        default=5,
        min=0,
        soft_max=30,
        )

    scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale value applied to the extruded face during each iteration",
        default=0.8,
        min=0.01,
        soft_max=2,       
    )

    angle = bpy.props.FloatProperty(
        name="Angle",
        description="Angle in degrees to rotate each face during each iteration",
        default=10,
        min=-80,
        max=80,       
    )

    def execute(self, context):
        for i in range(self.segment_count):
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
                value=(self.scale, self.scale, self.scale), 
                constraint_axis=(False, False, False), 
                constraint_orientation='LOCAL', 
                mirror=False, 
                proportional='DISABLED', 
                proportional_edit_falloff='SMOOTH', 
                proportional_size=1)
            bpy.ops.transform.rotate(
                value=self.angle*3.141592/180.0, 
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