bl_info = \
{
    "name" : "Prepare Sketchup Model",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "Prepares a Sketchup model using my signature workflow",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import bpy

class PrepareSketchupModel(bpy.types.Operator):
    bl_idname = "mesh.prepare_sketchup_model"
    bl_label = "Prepare Sketchup Model"

    def execute( self, context ):
        bpy.ops.object.select_all( action='SELECT' )
        bpy.ops.object.make_single_user( type='SELECTED_OBJECTS', object=True, obdata=True )
        bpy.ops.object.transform_apply( rotation=True, scale=True )
        bpy.ops.object.select_all( action='DESELECT' )
        bpy.ops.mesh.make_imagepalette()
        bpy.ops.mesh.collapse_hierarchy()
        bpy.ops.mesh.assign_vertexcoloured_material()

        return {"FINISHED"}

def register():
    bpy.utils.register_class(PrepareSketchupModel)

def unregister():
    bpy.utils.unregister_class(PrepareSketchupModel)

if __name__ == "__main__":
    register()