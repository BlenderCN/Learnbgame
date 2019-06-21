import bpy
from .. utils.decal import apply_decal, set_defaults
from .. utils.collection import sort_into_collections
from .. utils.ui import popup_message


class ReApply(bpy.types.Operator):
    bl_idname = "machin3.reapply_decal"
    bl_label = "MACHIN3: Re-Apply Decal"
    bl_description = "Re-Apply Decal to (new) Object. Parents Decal, Sets Up Custom Normals and Auto-Matches Materials\nALT: Forcibly auto-match Material, even if a specific Material is selected."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj for obj in context.selected_objects if obj.DM.isdecal)

    def invoke(self, context, event):
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal]
        target = context.active_object if context.active_object and context.active_object in context.selected_objects and not context.active_object.DM.isdecal else None

        failed = []

        for obj in decals:

            # apply the decal to the target, use a raycast, if the target is None
            applied = apply_decal(obj, target=target, force_automatch=event.alt)

            # follow up by setting defaults as well
            if applied:
                set_defaults(decalobj=obj, decalmat=obj.active_material)

                # also re-ssort the collections
                sort_into_collections(context.scene, obj)

            # if it fails to apply(because the raycast/find_nearest failed), pop an error
            else:
                failed.append(obj)


        if failed:
            msg = ["Re-applying the following decals failed:"]

            for obj in failed:
                msg.append(" » " + obj.name)

            msg.append("Try again on a different area of the model!")
            msg.append("You can also force apply to an non-decal object by selecting it last.")

            popup_message(msg)

        return {'FINISHED'}
