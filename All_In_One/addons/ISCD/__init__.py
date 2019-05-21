bl_info = {
    'name':     'ISCD I/O',
    'category': 'Import-Export',
    'version': (0, 1, 0),
    'blender': (2, 79, 0),
    "description": "I/O for ISCD",
    "author": "Loïc NORGEOT"
}

import sys
import importlib

modulesNames = ['op_export_mesh', "op_import_mesh", "op_import_mesh_sequence_fluids", "op_import_mesh_sequence_morphing", "op_import_mesh_sequence_fds", 'GUI']

modulesFullNames = {}
for currentModuleName in modulesNames:
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
