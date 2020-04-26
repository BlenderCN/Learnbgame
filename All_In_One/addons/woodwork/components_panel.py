import bpy


class ComponentsPanel(bpy.types.Panel):

    bl_label = "Woodworking components"
    bl_idname = "woodworking_components_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Woodworking'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.operator("mesh.woodwork_workpiece")


def register():
    bpy.utils.register_class(ComponentsPanel)


def unregister():
    bpy.utils.unregister_class(ComponentsPanel)

if __name__ == "__main__":
    register()
