import bpy
import os
import sys
import importlib


bl_info = {
    'name': 'Sliced Surface',
    'author': 'Nikolai Janakiev (njanakiev)',
    'version': (1, 0),
    'blender': (2, 77, 0),
    'location': 'View3D > Add > Mesh > Sliced Surface',
    'description': 'Adds a Sliced Surface to the scene',
    'warning': '',
	'wiki_url': '',
	'tracker_url': '',
    "category": "Learnbgame",
}


modulesNames = ['addSlicedSurface', 'slicedSurfacePanel', 'exportSlicedSurface', 'generators']

modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)


def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()
