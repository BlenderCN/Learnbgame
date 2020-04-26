import bpy


def load_image(selected_items,link=True):
    for item in selected_items :
        img = bpy.data.images.load(item.path,True)
