################################################################################
# Addon metatada
################################################################################

bl_info = {
    "name":        "Vulcano File Format (.vffmsh)",
    "author":      "Zingam the Great",
    "version":     (0, 0, 1),
    "blender":     (2, 80, 0),
    "location":    "File > Export > Vulcano (.vmsh)",
    "description": "This script exports Blender geometry in Vulcano file "
                   "format (.vmsh).",
    "warning":     "Work in progress...",
    "wiki_url":    "",
    "support":     "COMMUNITY",
    "category": "Learnbgame",
}

################################################################################
# Module reloading support
################################################################################

# This is required to support reloading of modules in Blender with F8
if "bpy" in locals():
    import importlib
    importlib.reload(operator)
    importlib.reload(exporter)
else:
    from . import operator
    from . import exporter

################################################################################
# Blender imports
################################################################################

import bpy

################################################################################
# Module constants
################################################################################

ADDON_MESSAGE = ( "\n" +
"================================================================================\n" +
"  Loading addon \"" + bl_info.get("name") + "\" from file:\n" +
"    " + __file__ + "\n" +
"================================================================================\n")

################################################################################
# Add-on registration
################################################################################

# A list of classes to be registered. Operator subclasses must be registered 
# before accessing them from Blender.
classes = (
    operator.VulcanoExporter
)

# GUI item functions
def export_menu(self, context):
    separator = "> "
    index = bl_info.get("location").rindex(separator) + len(separator)
    label = bl_info.get("location")[index:]
    self.layout.operator(operator.VulcanoExporter.bl_idname, 
        text=label)

# Register the add-on
def register():
    # Print message on add-on initialization
    print(ADDON_MESSAGE)
    # Register classes
    bpy.utils.register_class(operator.VulcanoExporter)
    # Register UI elements
    bpy.types.TOPBAR_MT_file_export.append(export_menu)

# Unregister the add-on
def unregister():
    # Unregister in reverse order
    bpy.types.TOPBAR_MT_file_export.remove(export_menu)
    bpy.utils.unregister_class(operator.VulcanoExporter)
    
################################################################################
# Script Entry Point
################################################################################
    
if __name__ == "__main__":
    register()
