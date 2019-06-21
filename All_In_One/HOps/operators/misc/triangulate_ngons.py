import bpy


class HOPS_OT_TriangulateNgons(bpy.types.Operator):
    bl_idname = "hops.triangulate_ngons"
    bl_label = "triangulate ngons"
    bl_description = "triangulate ngons"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.convert(target='MESH')
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.editmode_toggle()

        return {"FINISHED"}


class HOPS_OT_TriangulateModifier(bpy.types.Operator):
    bl_idname = "hops.triangulate_mod"
    bl_label = "triangulate mod"
    bl_description = "triangulate mod"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        selected = context.selected_objects
        for obj in selected:
            obj.modifiers.new(name="Triangulate", type="TRIANGULATE")

        return {"FINISHED"}
