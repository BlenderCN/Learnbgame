bl_info = {
    "name": "Bmexp",
    "category": "Learnbgame",
}

if "bpy" in locals(): #reloading
    import importlib
    if "bmexp" in locals():
        importlib.reload(bmexp)

else:
    import bpy
    from mathutils import Vector, Matrix
    from . import (
        bmexp
        )



class Bmexp(bpy.types.Operator):
    """Bmexp"""
    bl_idname = "object.bmexp"
    bl_label = "Bmexp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bmexp.main()
        return {'FINISHED'}

def register():
    print("######################Registering Bmexp####################")
    bpy.utils.register_class(Bmexp)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
<<<<<<< HEAD
        kmi = km.keymap_items.new('object.bmexp', 'Y', 'PRESS', shift=True)
=======
        kmi = km.keymap_items.new('object.bmexp', 'T', 'PRESS', shift=True)
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b


def unregister():
    bpy.utils.unregister_class(Bmexp)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
      km = kc.keymaps["3D View"]
      for kmi in km.keymap_items:
        if kmi.idname == 'object.bmexp':
            km.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()