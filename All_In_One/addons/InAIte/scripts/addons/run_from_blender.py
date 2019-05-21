for f in range(30):
    print("")

import bpy

import sys
path = r'''C:\Users\Peter\Documents\Hills road\Computing\A2\COMP4\CrowdFX\scripts\addons'''
sys.path.append(path)

import imp
from types import ModuleType

done = []


def rreload(module):
    """Recursively reload modules."""
    done.append(module)
    print("Name", module.__name__)
    imp.reload(module)
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if type(attribute) is ModuleType:
            if attribute not in done and attribute.__name__[:3] == "cfx":
                rreload(attribute)

import CrowdFX
#rreload(CrowdFX)
#from .CrowdFX import bl_info, register, unregister
bl_info = CrowdFX.bl_info
register = CrowdFX.register
unregister = CrowdFX.unregister
register()
