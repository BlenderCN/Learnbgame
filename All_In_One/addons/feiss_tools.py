bl_info={
	"name":"Feiss Tools",
	"category": "3D View",
	"author": "feiss"
}

import bpy


class FeissMenu(bpy.types.Menu):
    bl_label = "Feiss Tools"
    bl_idname = "OBJECT_MT_feiss_tools_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile")


def register():
    bpy.utils.register_class(FeissMenu)


def unregister():
    bpy.utils.unregister_class(FeissMenu)

if __name__ == "__main__":
    register()

    # The menu can also be called from scripts
    bpy.ops.wm.call_menu(name=FeissMenu.bl_idname)
