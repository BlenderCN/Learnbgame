import bpy

class OBJECT_OT_IMPORTPOINTS(bpy.types.Operator):
    """Import points as empty objects from a txt file"""
    bl_idname = "shift_from.blendergis"
    bl_label = "Copy from BlenderGis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        scene['BL_x_shift'] = scene['crs x']
        scene['BL_y_shift'] = scene['crs y']

        return {'FINISHED'}