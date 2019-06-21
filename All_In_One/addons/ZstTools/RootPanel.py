import bpy, ZstTools.RootOperator
print("Load RootPanel Class")

class RootPanel(bpy.types.Panel):
    my_float = bpy.props.FloatProperty()
    bl_idname = "OBJECT_PT_RootPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "ZstTools Root Panel"
    bl_label = "Root Panel"
    bl_context = "objectmode"

    def draw(self, context):
        print("Drawing in RootaPanel")
        # 記載する必要がある
        self.layout.operator_context = "INVOKE_DEFAULT"
#        self.layout.operator("",
#                                text="RootControlPanel")
        self.layout.prop(context.scene, 'encouraging_message')

    @classmethod
    def register(cls):
        print("Register in RootPanel")
        # Register properties related to the class here

    def unregister():
        print("Unregister in RootPanel")
        bpy.utils.unregister_module(__name__)
        print("%s unregister complete\n " % bl_info.get('name'))

if __name__ == "__main__":
    register()

bpy.utils.register_class(RootPanel)
