import bpy


class HOPS_OT_EditBoolUnion(bpy.types.Operator):
    bl_idname = "hops.edit_bool_union"
    bl_label = "Hops Union Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Union Boolean in Edit Mode"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object.mode == "EDIT" and object.type == "MESH":
            return True

    def draw(self, context):
        layout = self.layout
        layout.lable('')

    def execute(self, context):

        bpy.ops.mesh.intersect_boolean(operation='UNION')

        return {'FINISHED'}
