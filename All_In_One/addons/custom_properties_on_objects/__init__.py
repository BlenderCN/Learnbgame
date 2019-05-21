from . import core

bl_info = {
  "name": "Custom properties on objects",
  "description": "Demo of adding a custom object to a property",
  "author": "Hellmouth",
  "version": (0, 0, 1),
  "blender": (2, 79, 0),
  "location": "",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Object"
}

def register():
  core.register()

def unregister():
  core.unregister()

if __name__ == "__main__":
  register()