import bpy


class HelloWorldPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "my_prop")

def update_cb(self, context):
    # self is bpy.context.scene
    print("Selected:", self.my_prop)

def items_cb(self, context):
    l = []
    for ob in context.scene.objects:
        # Could use arbitrary conditions here
        #if ob.name.startswith("C"):
        
        l.append((ob.name, ob.name, ob.type))
    return l

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_prop = bpy.props.EnumProperty(items=items_cb, update=update_cb)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_prop


if __name__ == "__main__":
    register()