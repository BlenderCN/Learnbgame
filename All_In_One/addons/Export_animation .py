bl_info = {
    "name": "Export animation frames as mesh files",
    "category": "Export",
}

import bpy

class frameExportMesh( bpy.types.Operator):
    """Export animation frames as mesh files."""
    bl_idname = "frame.export_mesh"
    bl_label = "Export frames as mesh files"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene

        for frame in range( scene.frame_start, scene.frame_end):
            scene.frame_set(frame)
            scene.update()
            the_path = bpy.path.abspath('//')
            the_file = scene.name + "_" + str( scene.frame_current) + ".stl"
            bpy.ops.export_mesh.stl(filepath = the_path + the_file)
        
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(frameExportMesh)
    
def unregister():
    bpy.utils.unregister_class(frameExportMesh)
        
if __name__ == "__main__":
    register() 
