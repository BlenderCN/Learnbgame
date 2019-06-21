bl_info = {
    "name": "Gear Generator",
    "author": "Joseph Eagar",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "Properties > Object > GearGen",
    "description": "Generates gears, based on object sizes.  Replaces existing mesh data.",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

__all__ = [
  "main",
  "myprops",
  "involute",
  "involute_gen",
  "involute_gen_node",
  "myrandom"
];

registered = False

import imp

from . import myrandom, involute_gen, main, involute, myprops, involute_gen_node

imp.reload(myrandom)
imp.reload(myprops);
imp.reload(involute_gen_node);
imp.reload(involute_gen);
imp.reload(involute);
imp.reload(main);

def register():
  from . import main
  
  global registered
  
  if registered:
      try:
        main.unregister()
      except:
        print("Failed to unregister gears module")
      
  registered = True
  main.register()

def unregister():
  from . import main
  main.unregister()
  
  registered = False
  
if __name__ == "__main__":
  register()
