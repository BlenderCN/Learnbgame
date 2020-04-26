import bpy
from bpy.app.handlers import persistent
from bpy.props import EnumProperty

preview_collection = None


@persistent
def brush_load_handler(none):
    global preview_collection

    unregister_and_unload_brushes()
    register_and_load_brushes()


@persistent
def brush_update_handler(scene):
    global preview_collection

    try:
        if bpy.context.window_manager.brush_previews != bpy.context.tool_settings.sculpt.brush.name:
            bpy.context.window_manager.brush_previews = bpy.context.tool_settings.sculpt.brush.name
    except:
        pass

    if preview_collection:
        if not (set(brush.name for brush in bpy.data.brushes if brush.use_paint_sculpt) <= set(item[0] for item in preview_collection.items())):
            bpy.utils.previews.remove(preview_collection)
            add_brushes()
            bpy.types.WindowManager.brush_previews = EnumProperty(items=brush_enum_items(), update=brush_changed)


def add_brushes():
    global preview_collection

    preview_collection = bpy.utils.previews.new()
    brushes = [brush for brush in bpy.data.brushes if brush.use_paint_sculpt]

    for brush in brushes:
        preview_collection.new(brush.name)


def brush_enum_items():
    global preview_collection

    enum_items = []

    for name, preview in preview_collection.items():
        enum_items.append((name, name, name, "BRUSH_{}".format(bpy.data.brushes[name].sculpt_tool if bpy.data.brushes[name].sculpt_tool != "DRAW" else "SCULPT_DRAW"), preview.icon_id))

    return enum_items


def brush_changed(self, context):
    wm = context.window_manager
    context.tool_settings.sculpt.brush = bpy.data.brushes[wm.brush_previews]


def register_and_load_brushes():
    global preview_collection

    add_brushes()

    bpy.types.WindowManager.brush_previews = EnumProperty(items=brush_enum_items(), update=brush_changed)


def unregister_and_unload_brushes():
    global preview_collection

    if preview_collection:
        bpy.utils.previews.remove(preview_collection)
        preview_collection = None
