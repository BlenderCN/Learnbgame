import bpy

class WalkCycleRemoveMove(bpy.types.Operator):
    """Remove a bone from walk cycle"""
    bl_idname = "armature.walk_cycle_remove_move"
    bl_label = "Remove Bone"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'awc_bone')

    def invoke(self, context, event):
        nb = context.object.data.aut_walk_cycle.new_bones
        for i, b in enumerate(nb):
            if b == context.awc_bone:
                nb.remove(i)
                return {'FINISHED'}
        else:
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(WalkCycleRemoveMove)

def unregister():
    bpy.utils.unregister_class(WalkCycleRemoveMove)

if __name__ == "__main__":
    register()
