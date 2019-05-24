import bpy


bl_info = {
    'name': "Toggle SubD",
    'description': "Toggle Subsurf modifier or its cage.",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    "category": "Learnbgame",
}


class ToggleSubD(bpy.types.Operator):
    bl_description = ("Toggle show_viewport option in current first Subsurf "
                      "modifier or create one if there's none.")
    bl_idname = "mesh.toggle_subd"
    bl_label = "Toggle Subsurf modifier visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            try:
                if obj.modifiers["Subsurf"].show_viewport:
                    obj.modifiers["Subsurf"].show_viewport = False
                else:
                    obj.modifiers["Subsurf"].show_viewport = True
            except KeyError:
                bpy.ops.object.modifier_add(type='SUBSURF')
        return {'FINISHED'}


class ToggleSubDCage(bpy.types.Operator):
    bl_description = "Toggle show_on_cage option in current first Subsurf mod."
    bl_idname = "mesh.toggle_subd_cage"
    bl_label = "Toggle Subsurf modifier show cage option"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            try:
                if obj.modifiers["Subsurf"].show_on_cage:
                    obj.modifiers["Subsurf"].show_on_cage = False
                else:
                    obj.modifiers["Subsurf"].show_on_cage = True
            except KeyError:
                pass  # No modifier found.
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
