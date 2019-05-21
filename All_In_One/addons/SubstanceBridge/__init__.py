# ##### Substance Bridge #####
# A simple bridge between painter and blender.
#
# Thx Jerem.

# -----------------------------------------------------------------------------
# Import all Package addon
# -----------------------------------------------------------------------------
import sys
import importlib

modulesNames = [
    # Models
    'models.paths',
    'models.project',
    # Views
    # 'views.baking',
    'views.dataview',
    'views.moresopt',
    'views.settings',
    'views.substanceproject',
    'views.texturesetlist',
    # Controllers
    'controllers.debug',
    'controllers.substancecheck',
    'controllers.substancecontroller',
    'controllers.substancepainter',
    'controllers.substancesetup',
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
    "name": "Substance Bridge",
    "author": "stilobique",
    "version": (0, 5, 6),
    "blender": (2, 80, 0),
    "location": "Tool Shelf > Substance Panel",
    "description": "A simple way to export into substance painter.",
    "warning": "",
    "wiki_url": "https://github.com/stilobique/SubstanceBridge/wiki",
    "category": "Learnbgame",
    "tracker_url": "https://github.com/stilobique/SubstanceBridge/issues",
}


# -----------------------------------------------------------------------------
def register():
    # Add all class present in this addon
    for module in modulesFullNames:
        if module in sys.modules:
            if hasattr(sys.modules[module], 'register'):
                sys.modules[module].register()


# -----------------------------------------------------------------------------
# Delete register
# -----------------------------------------------------------------------------
def unregister():
    for module in modulesFullNames:
        if module in sys.modules:
            if hasattr(sys.modules[module], 'unregister'):
                sys.modules[module].unregister()
