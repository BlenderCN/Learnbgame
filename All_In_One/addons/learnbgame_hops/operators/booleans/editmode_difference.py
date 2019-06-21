import bpy


class HOPS_OT_EditBoolDifference(bpy.types.Operator):
    bl_idname = "hops.edit_bool_difference"
    bl_label = "Hops Difference Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Difference Boolean in Edit Mode"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object.mode == "EDIT" and object.type == "MESH":
            return True

    def draw(self, context):
        layout = self.layout
        layout.label(text='')

    def execute(self, context):

        bpy.ops.mesh.intersect_boolean(operation='DIFFERENCE')

        return {'FINISHED'}
