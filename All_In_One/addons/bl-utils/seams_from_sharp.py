import bpy


bl_info = {
    'name': "Seams From Sharp Edges",
    'description': "Create seams based on current sharp edges.",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    "category": "Learnbgame",
}


class SeamsFromSharp(bpy.types.Operator):
    bl_description = "Create seams based on current sharp edges."
    bl_idname = "mesh.seams_from_sharp"
    bl_label = "Seams from sharp edges."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for edge in bpy.context.active_object.data.edges:
            if edge.use_edge_sharp:
                edge.use_seam = True
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
