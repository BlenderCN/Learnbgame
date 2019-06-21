import bpy

class WalkCycleAddMove(bpy.types.Operator):
    """Add a new bone for walk cycle"""
    bl_idname = "armature.walk_cycle_add_move"
    bl_label = "Add Move"

    @classmethod
    def poll(cls, context):
        if not context.armature:
            return False
        return True

    def invoke(self, context, event):
        awc = context.object.data.aut_walk_cycle
        awc.new_bones.add()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(WalkCycleAddMove)

def unregister():
    bpy.utils.unregister_class(WalkCycleAddMove)

if __name__ == "__main__":
    register()
