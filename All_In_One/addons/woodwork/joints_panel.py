import bpy


class JointsPanel(bpy.types.Panel):

    bl_label = "Woodworking joints"
    bl_idname = "woodworking_joints_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Woodworking'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.operator("mesh.woodwork_tenon")
        row.operator("mesh.woodwork_mortise")


def register():
    bpy.utils.register_class(JointsPanel)


def unregister():
    bpy.utils.unregister_class(JointsPanel)

if __name__ == "__main__":
    register()
