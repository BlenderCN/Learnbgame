# Plugin Infos
bl_info = {
    "name": "easyText",
    "author": "Mic Schwarz",
    "version": (0, 7, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tools",
    "description": "easy Text making",
    "category": "Object"
}

if "bpy" in locals():
    import importlib

    importlib.reload(createtextletters)
    importlib.reload(createtextword)
    importlib.reload(font)
    print("Reloaded multifiles")
else:
    from . import createtextletters
    from . import createtextword
    from . import font

    print("Imported multifiles")

import bpy
import os
from bpy.props import *

atr = bpy.types.Scene

atr.content = StringProperty(name="Content", default="easytext", description="text content")
atr.spaceletters = FloatProperty(name="Space", default=0.5, description="space between letters")
atr.spaceword = FloatProperty(name="Space", default=1.0, description="space between letters")
atr.font = StringProperty(name="Font", description="Font of text")
atr.filebuff = StringProperty(name="", description="Choose Font to Import", subtype="FILE_PATH")

atr.extrude = FloatProperty(name="Text Extrude", default=0.1, description="Extrude of text")
atr.offset = FloatProperty(name="Text Offset", default=0, description="Offset of text")
atr.depth = FloatProperty(name="Text Depth", default=0.005, description="Depth of text")
atr.resolution = FloatProperty(name="Text Resolution", default=10, description="Resolution of Depth")

atr.mesh = BoolProperty(name="Meshconvert", default=True, description="Convert to mesh")
atr.edgesplit = BoolProperty(name="EdgeSplit", default=True, description="Auto-Edgesplit")
atr.uv = BoolProperty(name="UVmap", default=True, description="Auto-UV-Map")


# Window: Create Text
class WindowCreate(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Create Text"
    bl_category = "easyText"

    def draw(self, context):
        # shorts
        layout = self.layout
        scene = bpy.context.scene
        pcoll = preview_collections["main"]

        col = layout.column(align=True)

        # icons
        icon_add_one = pcoll["icon_add_one"]
        icon_add_two = pcoll["icon_add_two"]
        icon_text = pcoll["icon_text"]

        # content
        col.operator("create.textword", text="New Text (Word)", icon_value=icon_add_one.icon_id)
        col.prop(scene, "spaceletters")

        col = layout.column(align=True)

        col.operator("create.textletters", text="New Text (Letters)", icon_value=icon_add_two.icon_id)
        col.prop(scene, "spaceword")

        layout.prop(scene, "content", icon_value=icon_text.icon_id)


# Window: Properties
class WindowProperties(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Properties"
    bl_category = "easyText"

    def draw(self, context):
        # shorts
        layout = self.layout
        col = layout.column(align=True)
        scene = bpy.context.scene
        fonts = bpy.context.blend_data
        pcoll = preview_collections["main"]

        col.prop(scene, "extrude")
        col.prop(scene, "offset")
        col.prop(scene, "depth")
        col.prop(scene, "resolution")

        layout = self.layout
        layout.prop_search(scene, "font", fonts, "fonts")


class WindowOptions(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Options"
    bl_category = "easyText"

    def draw(self, context):
        # icons
        pcoll = preview_collections["main"]
        icon_settings = pcoll["icon_settings"]

        # shorts
        scene = bpy.context.scene
        layout = self.layout
        layout.label("(De-)Activate Features", icon_value=icon_settings.icon_id)

        col = layout.column(align=True)

        col.prop(scene, "mesh")
        col.prop(scene, "edgesplit")
        col.prop(scene, "uv")


class WindowImportFont(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Import Font"
    bl_category = "easyText"

    def draw(self, context):
        # shorts
        scene = bpy.context.scene
        fonts = bpy.context.blend_data
        pcoll = preview_collections["main"]
        icon_fontsettings = pcoll["icon_fontsettings"]
        layout = self.layout
        layout.label("Choose + Import Font", icon_value=icon_fontsettings.icon_id)

        col = layout.column(align=True)
        # icons
        icon_font = pcoll["icon_font"]
        icon_import = pcoll["icon_import"]

        col.prop(scene, "filebuff", icon_value=icon_font.icon_id)
        col.operator("load.font", text="Import", icon_value=icon_import.icon_id)


# Buttons

class ObjectOtButtoncreateletters(bpy.types.Operator):
    bl_label = "Create"
    bl_idname = "create.textletters"
    bl_description = "creates a text"

    def execute(self, context):
        s = bpy.context.scene
        createtextletters.create(s.content, s.spaceletters, font.search(s.font), s.extrude, s.offset, s.depth,
                                 s.resolution, s.mesh, s.edgesplit, s.uv)
        self.report({'INFO'}, "Text created")
        return {'FINISHED'}


class ObjectOtButtoncreateword(bpy.types.Operator):
    bl_label = "Create"
    bl_idname = "create.textword"
    bl_description = "creates a text"

    def execute(self, context):
        s = bpy.context.scene
        createtextword.create(s.content, s.spaceword, font.search(s.font), s.extrude, s.offset, s.depth, s.resolution,
                              s.mesh, s.edgesplit, s.uv)
        self.report({'INFO'}, "Text created")
        return {'FINISHED'}


class ObjectOtButtonloadfont(bpy.types.Operator):
    bl_label = "Load Font"
    bl_idname = "load.font"
    bl_description = "Import the choosen Font"

    def execute(self, context):
        scene = bpy.context.scene
        fontb = scene.filebuff

        bpy.context.window.cursor_set("WAIT")
        bpy.data.fonts.load(filepath=fontb, check_existing=True)
        self.report({'INFO'}, "Font loaded")
        bpy.context.window.cursor_set("DEFAULT")
        return {'FINISHED'}


preview_collections = {}


def register():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    # icons
    pcoll.load("icon_text", os.path.join(my_icons_dir, "text.png"), 'IMAGE')
    pcoll.load("icon_add_one", os.path.join(my_icons_dir, "add_one.png"), 'IMAGE')
    pcoll.load("icon_add_two", os.path.join(my_icons_dir, "add_two.png"), 'IMAGE')
    pcoll.load("icon_font", os.path.join(my_icons_dir, "loadfont.png"), 'IMAGE')
    pcoll.load("icon_import", os.path.join(my_icons_dir, "import.png"), 'IMAGE')
    pcoll.load("icon_settings", os.path.join(my_icons_dir, "settings.png"), 'IMAGE')
    pcoll.load("icon_fontsettings", os.path.join(my_icons_dir, "font.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    bpy.utils.register_module(__name__)


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__": register()
