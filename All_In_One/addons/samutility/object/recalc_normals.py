import bpy

class recalculate_normals_outside(bpy.types.Operator):
    bl_idname = "samutils.recalculate_normals_outside"
    bl_label = "Recalculate Normals Outside"
    bl_description = "recalculate normal outside for all selected objects"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        act= context.active_object

        for o in context.selected_objects:
            if o.type == 'MESH':
                bpy.context.scene.objects.active = o
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')

        #reset active
        bpy.context.scene.objects.active = act
        return {"FINISHED"}
