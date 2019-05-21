import bpy
import os
from bpy.props import EnumProperty
from .. utils.previews import enum_items_from_previews, load_previews_in_directory
from .. utils.asset_loader import icons_folder
import bpy.utils.previews
from .. utils.operators import save_json

preview_collection = None

insert_on_selection_change = True

# don't insert the panel_decal when the selection changes


def change_selected_panel_decal(name):
    global insert_on_selection_change
    insert_on_selection_change = False
    bpy.context.window_manager.paneling01_preview = name
    insert_on_selection_change = True


def selected_panel_decal_changed(self, context):
    if insert_on_selection_change:
        bpy.ops.machin3.insert_panel_decal01(panel_decal01_name=context.window_manager.paneling01_preview)


def register_and_load_paneling01():
    global preview_collection

    preview_collection = bpy.utils.previews.new()

    load_previews_in_directory(preview_collection, icons_folder("paneling01"))
    load_previews_in_directory(preview_collection, icons_folder("paneling01", custom=True))
    enum_items = enum_items_from_previews(preview_collection)

    bpy.types.WindowManager.paneling01_preview = EnumProperty(items=enum_items, update=selected_panel_decal_changed)

    save_paneling(enum_items)


def unregister_and_unload_paneling01():
    global preview_collection

    del bpy.types.WindowManager.paneling01_preview
    bpy.utils.previews.remove(preview_collection)
    preview_collection = None


def save_paneling(panellist):
    DMpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.DMpath
    panelingpath = os.path.join(DMpath, "operators", "paneling.json")

    panelinglist = [panel for panel in panellist]

    save_json(panelinglist, panelingpath)
