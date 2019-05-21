bl_info = {
    "name": "Blender 2.80beta PorpertiesRenderButtons",
    "author": "Olaf Haag",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Output > Dimensions",
    "description": "Adds Render Buttons to Output tab in Properties.",
    "warning": "Blender 2.8 is still in development, so usability of this addon might change.",
    "wiki_url": "https://github.com/OlafHaag/Blender2_80beta_RenderButtons/blob/master/README.md",
    "tracker_url": "https://github.com/OlafHaag/Blender2_80beta_RenderButtons/issues",
    "category": "Learnbgame",
    }

from bpy.utils import register_class, unregister_class
from . addpropertiesrenderbuttons import AddRenderButtons

#    Registration
def register():
    register_class(AddRenderButtons)

def unregister():
    unregister_class(AddRenderButtons)

if __name__ == "__main__":
    register()
