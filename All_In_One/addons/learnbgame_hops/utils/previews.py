import os
import bpy

def load_previews_in_directory(preview_collection, directory):
    for name in os.listdir(directory):
        if name.endswith(".png"):
            real_name = name[:-4] # cut off '.png'
            path = os.path.join(directory, name)
            preview_collection.load(real_name, path, 'IMAGE')

def enum_items_from_previews(preview_collection):
    items = []
    for name, preview in preview_collection.items():
        items.append((name, name, "", preview.icon_id, preview.icon_id))
    return items
