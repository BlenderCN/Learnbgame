import os
import sys

addonPath = os.path.abspath(os.path.dirname(__file__))
packagesPath = os.path.abspath(os.path.join(addonPath, "env/lib/python3.6/site-packages"))

sys.path.append(addonPath)
sys.path.append(packagesPath)

import hy
import main

bl_info = {
    "name": "Blender Hy",
    "category": "Development",
    "description": "hy lang integration kit"
}

def register():
    main.register()

def unregister():
    main.unregister()

if __name__ == "__main__":
    register()

