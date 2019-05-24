from . import core
from . import ui 

bl_info = {
  "name": "Creating UI controls for properties",
  "description": "Demo of adding a UI element for a custom object property",
  "author": "Hellmouth",
  "version": (0, 0, 1),
  "blender": (2, 79, 0),
  "location": "",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Learnbgame",
}

def register():
  core.register()
  ui.register()

def unregister():
  core.unregister()
  ui.unregister()

if __name__ == "__main__":
  register()