import bpy

class WorldProperty(bpy.types.PropertyGroup):
    intensity = bpy.props.FloatProperty(name="Intensity", default=1.0)
    color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=[0.0,0.0,0.0])

class ElaraWorldPanel(bpy.types.Panel):
    bl_label = "Environment"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "world"

    def draw(self, context):
        layout = self.layout
        elara_env = context.scene.elara_env
        layout.prop(elara_env, "intensity", text="intensity")
        layout.prop(elara_env, "color", text="color")


def register():
    bpy.utils.register_class(ElaraWorldPanel)
    bpy.utils.register_class(WorldProperty)
    bpy.types.Scene.elara_env = bpy.props.PointerProperty(type=WorldProperty)

def unregister():
    bpy.utils.unregister_class(ElaraWorldPanel)
    bpy.utils.unregister_class(WorldProperty)
    del bpy.types.Scene.elara_env