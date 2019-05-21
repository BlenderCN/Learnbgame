import bpy

bl_info = {
    "name": "Subsurf Toggler",
    "author": "Stefan Heinemann",
    "blender": (2, 77, 0),
    "version": (0, 0, 4),
    "location": "Key Bindings",
    "description": "Provides an operator for keybindings to toggle the "
                   "subsurf modifiers",
    "category": "Object"
}


class ToggleSubsurf(bpy.types.Operator):
    bl_idname = 'object.toggle_subsurf'
    bl_label = "Subsurf toggler"

    def cur_object(self):
        return bpy.context.scene.objects.active

    def execute(self, context):
        obj = self.cur_object()
        modifiers = obj.modifiers

        for mod in modifiers:
            if mod.type == 'SUBSURF':
                mod.show_viewport = not mod.show_viewport

        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
