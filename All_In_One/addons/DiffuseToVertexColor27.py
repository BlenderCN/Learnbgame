bl_info = \
{
    "name" : "Diffuse Color to Vertex Color",
    "author" : "Bronson Zgeb <bronson.zgeb@gmail.com>",
    "version" : (1, 0, 0),
    "blender" : (2, 6, 9),
    "location" : "",
    "description" : "Applies all diffuse colors to meshes as vertex colors, and if the material has a texture it sets the diffuse color to white. This was mainly written for cleaning models from Sketchup",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}

import bpy

class MakeVertexColors(bpy.types.Operator):
    bl_idname = "mesh.make_vertexcolors"
    bl_label = "Convert Diffuse to Vertex Colors"


    def execute(self, context):
        for obj in bpy.data.objects:
            if not obj.active_material is None:
                if obj.type == 'MESH':
                    if not obj.active_material.active_texture is None:
                        obj.active_material.diffuse_color = [1,1,1]

                    color = obj.active_material.diffuse_color



                    mesh = obj.data

                    if not mesh.vertex_colors:
                        mesh.vertex_colors.new()

                    color_layer = mesh.vertex_colors[0]

                    i = 0
                    for poly in mesh.polygons:
                        for idx in poly.loop_indices:
                            color_layer.data[i].color = color
                            i += 1
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MakeVertexColors)

def unregister():
    bpy.utils.unregister_class(MakeVertexColors)

if __name__ == "__main__":
    register()
