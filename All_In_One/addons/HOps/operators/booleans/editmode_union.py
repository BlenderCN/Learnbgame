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
        layout.label(text='')

    def execute(self, context):

        bpy.ops.mesh.intersect_boolean(operation='UNION')

        return {'FINISHED'}


class HOPS_OT_EditBoolInt(bpy.types.Operator):
    bl_idname = "hops.edit_bool_intersect"
    bl_label = "Hops INTERSECT Boolean Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Cuts mesh using Intersect Boolean"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object.mode == "EDIT" and object.type == "MESH":
            return True

    def draw(self, context):
        layout = self.layout
        layout.label(text='')

    def execute(self, context):

        bpy.ops.mesh.intersect_boolean(operation='INTERSECT')

        return {'FINISHED'}
