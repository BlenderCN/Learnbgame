import bpy
import os
from os import listdir
from os.path import isfile, join
#from . add_object_to_selection import add_from_dess_insert

nexus_five_preview_collections = {}

def enumPreviewsFromDirectoryItems(self, context):
    """EnumProperty callback"""
    enum_items = []
 
    if context is None:
        return enum_items
   
    #directory = join(os.path.dirname(__file__), "icons", "dSet1")
    directory = join(os.path.dirname(__file__), "icons")
    # Get the preview collection (defined in register func).
    pcoll = Hard_Ops_preview_collections["main"]
 
    if directory == pcoll.nexus_five_previews_dir:
        return pcoll.nexus_five_previews
 
    # print("Scanning directory: %s" % directory)
 
    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)
 
        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, "", thumb.icon_id, i))
 
    pcoll.nexus_five_previews = enum_items
    pcoll.nexus_five_dir = directory
 
    return pcoll.nexus_five_previews
 
 
def register_nexus_five_pcoll():  
    from bpy.types import WindowManager
    from bpy.props import (
            EnumProperty,
            BoolProperty)
 
    WindowManager.nexus_five_previews = EnumProperty(
            items=enumPreviewsFromDirectoryItems,
            update=add_from_dess_insert)
 
    import bpy.utils.previews
    wm = bpy.context.window_manager
    pcoll = bpy.utils.previews.new()
    pcoll.nexus_five_previews_dir = ""
    pcoll.nexus_five_previews = ()
 
    nexus_five_preview_collections["main"] = pcoll
 
 
def unregister_Hard_Ops_pcoll():
    from bpy.types import WindowManager
 
    del WindowManager.nexus_five_previews
 
    for pcoll in nexus_five_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    nexus_five_preview_collections.clear()
