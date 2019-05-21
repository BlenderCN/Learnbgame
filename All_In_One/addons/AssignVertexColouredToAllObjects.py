bl_info = \
{
    "name" : "Assign VertexColoured material to all objects",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "Assigns a new material called VertexColoured to all objects",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import bpy

class AssignVertexColouredMaterial(bpy.types.Operator):
    bl_idname = "mesh.assign_vertexcoloured_material"
    bl_label = "Assign VertexColoured material to all objects"

    def execute( self, context ):
        try:
            vertexColouredMaterial = bpy.data.materials["VertexColoured"]
        except:
            vertexColouredMaterial = bpy.data.materials.new("VertexColoured")

        scene = bpy.context.scene
        all_objs = [obj for obj in scene.objects]
        for obj in all_objs:
            if obj.active_material is not None:
                if obj.active_material.active_texture is None:
                    obj.active_material = vertexColouredMaterial
            for material_slot in obj.material_slots:
                if material_slot.material.active_texture is None:
                    material_slot.material = vertexColouredMaterial
            
        return {"FINISHED"}

def register():
    bpy.utils.register_class(AssignVertexColouredMaterial)

def unregister():
    bpy.utils.unregister_class(AssignVertexColouredMaterial)

if __name__ == "__main__":
    register()