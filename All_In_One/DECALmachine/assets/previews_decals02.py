import bpy
from bpy.props import EnumProperty
from .. utils.previews import enum_items_from_previews, load_previews_in_directory
from .. utils.asset_loader import icons_folder
import bpy.utils.previews

preview_collection = None

insert_on_selection_change = True

# don't insert the decal02 when the selection changes


def change_selected_decal02(name):
    global insert_on_selection_change
    insert_on_selection_change = False
    bpy.context.window_manager.decals02_preview = name
    insert_on_selection_change = True


def selected_decal02_changed(self, context):
    if insert_on_selection_change:
        bpy.ops.machin3.insert_decal02(decal02_name=context.window_manager.decals02_preview)


def register_and_load_decals02():
    global preview_collection

    preview_collection = bpy.utils.previews.new()

    load_previews_in_directory(preview_collection, icons_folder("decals02"))
    load_previews_in_directory(preview_collection, icons_folder("decals02", custom=True))
    enum_items = enum_items_from_previews(preview_collection)

    bpy.types.WindowManager.decals02_preview = EnumProperty(items=enum_items, update=selected_decal02_changed)


def unregister_and_unload_decals02():
    global preview_collection

    del bpy.types.WindowManager.decals02_preview
    bpy.utils.previews.remove(preview_collection)
    preview_collection = None
