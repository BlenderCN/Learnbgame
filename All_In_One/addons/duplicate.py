bl_info = {
    "name" : "Duplicate:CustomAddon",
    "category": "MyAddon",    
    "author": "AkashManna"
}




import bpy


class CustomMenu(bpy.types.Menu):
    bl_label = "Custom Menu"
    bl_idname = "custom_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.primitive_cube_add")
        layout.operator("object.duplicate_move")


def register():
    bpy.utils.register_class(CustomMenu)


def unregister():
    bpy.utils.unregister_class(CustomMenu)


if __name__ == "__main__":
    register()
