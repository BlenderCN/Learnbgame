bl_info = \
{
    "name" : "Delete All Materials",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "Removes all materials from all objects",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import bpy

class DeleteAllMaterials(bpy.types.Operator):
    bl_idname = "mesh.delete_all_materials"
    bl_label = "Delete All Materials"

    def execute( self, context ):
        scene = bpy.context.scene
        all_objs = [obj for obj in scene.objects]
        for obj in all_objs:
            if obj.active_material is not None:
                obj.active_material = None
            obj.data.materials.clear()

        for mat in bpy.data.materials:
            mat.user_clear()
            if not mat.users:
                bpy.data.materials.remove( mat )

            
        return {"FINISHED"}

def register():
    bpy.utils.register_class(DeleteAllMaterials)

def unregister():
    bpy.utils.unregister_class(DeleteAllMaterials)

if __name__ == "__main__":
    register()
