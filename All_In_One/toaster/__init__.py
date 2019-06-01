import bpy
from bpy.props import PointerProperty, BoolProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup


# Have to import everything with classes which need to be registered
from . engine.toaster import ToasterRenderEngine

bl_info = {
    "name": "Toaster",
    "author": "Jean-Francois Romang (jromang)",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "Info header, render engine menu",
    "description": "Toaster renderer",
    "warning": "",
    "wiki_url": "https://github.com/jromang/toaster/wiki",
    "tracker_url": "https://github.com/jromang/toaster/issues/new",
}


# https://blender.stackexchange.com/questions/6975/is-it-possible-to-use-bpy-props-pointerproperty-to-store-a-pointer-to-an-object
class ToasterProperties(PropertyGroup):
    SPP_DESC = "Number of samples per pixel"
    spp: IntProperty(name="SPP", default=10, min=1, soft_max=100000, description=SPP_DESC)


def draw_panel(self, context):
    # https://docs.blender.org/api/blender2.8/bpy.types.UILayout.html#bpy.types.UILayout.prop
    # https://docs.blender.org/api/blender2.8/info_quickstart.html
    layout = self.layout
    scene = context.scene

    if context.engine == "toaster_renderer":
        # view = context.space_data
        layout.prop(scene.toaster, "spp")


def register():
    print("Hello, REGISTER : "+__name__)
    # Register the RenderEngine
    bpy.utils.register_class(ToasterRenderEngine)
    # bpy.utils.register_module(__name__)

    # dictionaries can be assigned as long as they only use basic types.
    # collection = bpy.data.collections.new("MyTestCollection")
    # collection["MySettings"] = {"foo": 10, "bar": "spam", "baz": {}}

    # RenderEngines also need to tell UI Panels that they are compatible
    # Otherwise most of the UI will be empty when the engine is selected.
    # In this example, we need to see the main render image button and
    # the material preview panel.
    # from bl_ui import (
    #    properties_render,
    #   properties_material,
    # )
    # properties_render.RENDER_PT_render.COMPAT_ENGINES.add(ToasterRenderEngine.bl_idname)
    bpy.types.RENDER_PT_context.append(draw_panel)
    # properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)

    bpy.utils.register_class(ToasterProperties)
    bpy.types.Scene.toaster = bpy.props.PointerProperty(type=ToasterProperties)


def unregister():
    bpy.utils.unregister_class(ToasterRenderEngine)
    # bpy.utils.unregister_module(__name__)

    # from bl_ui import (
    #    properties_render,
    #    properties_material,
    # )
    # properties_render.RENDER_PT_render.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    bpy.types.RENDER_PT_context.remove(draw_panel)
    # properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)


if __name__ == "__main__":
    register()
