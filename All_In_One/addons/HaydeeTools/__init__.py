# -*- coding: utf-8 -*-
# <pep8 compliant>

bl_info = {
    "name": "Haydee I/O Scripts",
    "author": "johnzero7",
    "version": (1, 1, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > HaydeeTools",
    "description": "Import-Export scripts for Haydee",
    "warning": "",
	"wiki_url":    "https://github.com/johnzero7/HaydeeTools",
	"tracker_url": "https://github.com/johnzero7/HaydeeTools/issues",
    "category": "Learnbgame",
}


#############################################
# support reloading sub-modules
_modules = [
    'HaydeeMenuIcon',
    'HaydeePanels',
    'HaydeeExporter',
    'HaydeeImporter',
    'HaydeeUtils',
    'HaydeeNodeMat',
    'addon_updater_ops',
]

#Reload previously loaded modules
if "bpy" in locals():
    from importlib import reload
    _modules_loaded[:] = [reload(module) for module in _modules_loaded]
    del reload


#First import the modules
__import__(name=__name__, fromlist=_modules)
_namespace = globals()
_modules_loaded = [_namespace[name] for name in _modules]
del _namespace
# support reloading sub-modules
#############################################

import bpy


class UpdaterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__


    # addon updater preferences from `__init__`, be sure to copy all of them
    auto_check_update : bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
    )
    updater_intrval_months : bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days : bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours : bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes : bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )


    def draw(self, context):
        addon_updater_ops.update_settings_ui(self, context)

#
# Registration
#


classesToRegister = [
    UpdaterPreferences,
    HaydeePanels.HaydeeToolsImportPanel,
    HaydeePanels.HaydeeToolsExportPanel,
    HaydeePanels.HaydeeToolsSkelPanel,

    HaydeeExporter.ExportHaydeeDSkel,
    HaydeeExporter.ExportHaydeeDPose,
    HaydeeExporter.ExportHaydeeDMotion,
    HaydeeExporter.ExportHaydeeDMesh,
    HaydeeExporter.HaydeeExportSubMenu,

    HaydeeImporter.ImportHaydeeSkel,
    HaydeeImporter.ImportHaydeeDSkel,
    HaydeeImporter.ImportHaydeeDMesh,
    HaydeeImporter.ImportHaydeeMesh,
    HaydeeImporter.ImportHaydeeMotion,
    HaydeeImporter.ImportHaydeeDMotion,
    HaydeeImporter.ImportHaydeePose,
    HaydeeImporter.ImportHaydeeDPose,
    HaydeeImporter.ImportHaydeeOutfit,
    HaydeeImporter.ImportHaydeeSkin,
    HaydeeImporter.ImportHaydeeMaterial,
    HaydeeImporter.HaydeeImportSubMenu,

    HaydeeUtils.HaydeeToolFitArmature_Op,
    HaydeeUtils.HaydeeToolFitMesh_Op,
]


#Use factory to create method to register and unregister the classes
registerClasses, unregisterClasses = bpy.utils.register_classes_factory(classesToRegister)


def register():
    HaydeeMenuIcon.registerCustomIcon()
    registerClasses()
    HaydeeExporter.register()
    HaydeeImporter.register()
    addon_updater_ops.register(bl_info)


def unregister():
    addon_updater_ops.unregister()
    HaydeeExporter.unregister()
    HaydeeImporter.unregister()
    unregisterClasses()
    HaydeeMenuIcon.unregisterCustomIcon()

if __name__ == "__main__":
    register()

    # call exporter
    # bpy.ops.xps_tools.export_model('INVOKE_DEFAULT')

    # call importer
    # bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')
