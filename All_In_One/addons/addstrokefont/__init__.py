#
#
# This Blender add-on lets the user render text with stroke fonts. 
#
# Supported Blender Version: 2.8 Beta
#
# Copyright (C) 2019  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/blenderstrokefont/blob/master/LICENSE)
#
# Not yet pep8 compliant 

from . strokefontui import register, unregister

bl_info = {
    "name": "Add Stroke Font Text",
    "author": "Shrinivas Kulkarni",
    "location": "Properties > Active Tool and Workspace Settings > Add Stroke Font Text",
    "category": "Learnbgame",
    "blender": (2, 80, 0),    
}

if __name__ == "__main__":
    register()
