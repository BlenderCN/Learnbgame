import bpy
from bpy.props import EnumProperty
from .. utils.previews import enum_items_from_previews, load_previews_in_directory
from .. utils.asset_loader import icons_folder
import bpy.utils.previews

preview_collection = None

insert_on_selection_change = True

# don't insert the info_decal when the selection changes


def change_selected_info_decal(name):
    global insert_on_selection_change
    insert_on_selection_change = False
    bpy.context.window_manager.info01_preview = name
    insert_on_selection_change = True


def selected_info_decal_changed(self, context):
    if insert_on_selection_change:
        bpy.ops.machin3.insert_info01(info01_name=context.window_manager.info01_preview)


def register_and_load_info01():
    global preview_collection

    preview_collection = bpy.utils.previews.new()

    load_previews_in_directory(preview_collection, icons_folder("info01"))
    load_previews_in_directory(preview_collection, icons_folder("info01", custom=True))
    enum_items = enum_items_from_previews(preview_collection)

    bpy.types.WindowManager.info01_preview = EnumProperty(items=enum_items, update=selected_info_decal_changed)


def unregister_and_unload_info01():
    global preview_collection

    del bpy.types.WindowManager.info01_preview
    bpy.utils.previews.remove(preview_collection)
    preview_collection = None
