# Working Copy Panel
class WorkingCopyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "WorkingCopy Operator"
    bl_context = "objectmode"

    def draw(self, context):
        self.layout.operator("object.woring_copy",
                            text="Copy your working after push Start")
        self.layout.prop(context.scene, 'Working Copy Tool")

    @classmethod
    def register(cls):
        print("Registered class %s " % cls.bl_label)

# Finish Working Copy Panel