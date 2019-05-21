from bpy.types import Operator


class DecimateMeshButton(Operator):
    """Reduce polygon mesh count
    """
    bl_idname = 'mesh_to_xcode.decimate_button'
    bl_label = 'Add'

    def execute(self, context):
        scene = context.scene
        obj = context.active_object

        if not obj.modifiers.get('Decimate'):
            dm = obj.modifiers.new('Decimate','DECIMATE')
            dm.ratio = 1

        return { 'FINISHED' }


class ApplyModifiersButton(Operator):
    """Apply all the added modifiers
    """
    bl_idname = 'mesh_to_xcode.apply_modifiers'
    bl_label = 'Apply All'

    # TODO Cannot apply modifier
    def execute(self, context):
        scene = context.scene

        obj = context.active_object
        bpy.context.scene.objects.active = obj

        for mod in obj.modifiers:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        return { 'FINISHED' }


class RemoveModifiersButton(Operator):
    """Remove all modifiers from the object
    """
    bl_idname = 'mesh_to_xcode.remove_modifiers'
    bl_label = 'Remove All'

    # TODO remove all
    def execute(self, context):
        obj = context.active_object

        for mod in obj.modifiers:
            print(mod.name)

        return { 'FINISHED' }


# TODO Keep the modifier alignment always the same
