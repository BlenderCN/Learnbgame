import bpy


class ui_panel_main(bpy.types.Panel):
    bl_label = "Minecraft Animation"
    bl_idname = "MCANIM_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Minecraft"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("mcanim.import_rig")
        row = layout.row()
        row.operator("mcanim.export")


def register():
    print("Registered Main Panel")
    #bpy.utils.register_class(ui_panel_main)


def unregister():
    print("Unregistered Main Panel")
    #bpy.utils.unregister_class(ui_panel_main)


if __name__ == "__main__":
    register()
