"""
Name:    img_in
Purpose: Imports image files.

Description:


"""

import bpy
import os

def load_image(filepath):
    # Guesses texture name and path
    texture_name = os.path.basename(filepath)

    # Gets image if it already exists
    # image = bpy.data.images.get(texture_name)
    # Loads image if it doesn't exit yet
    # if not image:
    if os.path.exists(filepath):
        image = bpy.data.images.load(filepath)
        # Sets a fake user because it doesn't get automatically set
        image.use_fake_user = True
    else:
        # Finds existing dummy texture
        for img in bpy.data.images:
            if img.name == texture_name:
                return img
        # Creates a dummy texture
        print("Texture not found: ", filepath)
        bpy.ops.image.new(name=texture_name, width=512, height=512,
                          generated_type="UV_GRID")
        image = bpy.data.images.get(texture_name)

    return image

def import_file(filepath):
    return load_image(filepath)
