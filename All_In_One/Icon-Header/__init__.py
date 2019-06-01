import sys
import importlib

modulesNames = [
    # Views
    'views.header',
    # Controllers
    'controllers.checker',
    'controllers.cursor_uv',
    'controllers.grid',
    'controllers.location',
    'controllers.retopo',
    'controllers.smooth',
    ]

modulesFullNames = []
for currentModule in modulesNames:
    modulesFullNames.append('{}.{}'.format(__name__, currentModule))

for currentModule in modulesFullNames:
    if currentModule in sys.modules:
        importlib.reload(sys.modules[currentModule])
    else:
        globals()[currentModule] = importlib.import_module(currentModule)

# -----------------------------------------------------------------------------
# MetaData Add-On Blender
# -----------------------------------------------------------------------------
bl_info = {
    "name": "Icon Header",
    "author": "stilobique",
    "version": (1, 2, 1),
    "blender": (2, 78),
    "location": "3D View > Header",
    "description": "Various new operator.",
    "warning": "",
    "wiki_url": "https://github.com/stilobique/Grid/wiki",
    "category": "Learnbgame",
    "tracker_url": "https://github.com/stilobique/Grid/issues",
}


# -----------------------------------------------------------------------------
# Register all module and append UI in 3D View Header
# -----------------------------------------------------------------------------
def register():
    for currentModule in modulesFullNames:
        if currentModule in sys.modules:
            if hasattr(sys.modules[currentModule], 'register'):
                sys.modules[currentModule].register()


# -----------------------------------------------------------------------------
# Delete register
# -----------------------------------------------------------------------------
def unregister():
    for currentModule in modulesFullNames:
        if currentModule in sys.modules:
            if hasattr(sys.modules[currentModule], 'unregister'):
                sys.modules[currentModule].unregister()


if __name__ == "__main__":
    register()
