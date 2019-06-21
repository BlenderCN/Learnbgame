import bpy

class CreateVisemesPanel(bpy.types.Panel):
    bl_label = "IKify Visemes"
    bl_idname = "OBJECT_PT_CreateVisemes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.create_visemes")


def register():
    bpy.utils.register_class(CreateVisemesPanel)


def unregister():
    bpy.utils.unregister_class(CreateVisemesPanel)


if __name__ == "__main__":
    register()
    