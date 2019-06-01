import bpy


class Object_MirrorOperator(bpy.types.Operator):
    bl_idname = "object.object_mirror"
    bl_label = "Object_Mirror"
    bl_description = "Mirrors selected objects with active object as mirror point/plane"

    def execute(self, context):

        all_ob = bpy.context.selected_objects
        act_ob = bpy.context.active_object

        for obj in all_ob:
            if obj == act_ob:
                all_ob.remove(obj)
        
        for obj in all_ob:
            mod = obj.modifiers.new(type='MIRROR', name='Mirror_object')
            mod.mirror_object = act_ob

        return {'FINISHED'}

