bl_info = {
    "name": "Crateriffic",
    "author": "Benjamin Humpherys",
    "location": "View3D > Tools > Crateriffic",
    "category": "Learnbgame",
    "blender": (2, 80, 0)
}

# When bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    print("===========Reloading Crateriffic============")
    # ...so we need to reload our submodule(s) using importlib
    # TODO: Automate register/unregister
    import importlib
    if "HighlightFacing" in locals():
        importlib.reload(HighlightFacing)
        
    if "rayscan" in locals():
        importlib.reload(rayscan)

    if "SavePoints" in locals():
        importlib.reload(SavePoints)
    
    if "import_footprint" in locals():
        importlib.reload(import_footprint)


# This is only relevant on first run, on later reloads those modules
# are already in locals() and those statements do not do anything.
import bpy
from . import HighlightFacing, rayscan, SavePoints, import_footprint
classes = [HighlightFacing.PSY_OT_HighlightFacing,
            rayscan.PSY_OT_RayScan,
            SavePoints.PSY_OT_ExportRayScan,
            import_footprint.PSY_OT_ImportFootprint]

def register():
    for c in classes:
        print("Registering class "+c.__name__)
        bpy.utils.register_class(c)
    
    # SavePoints.ExportRayScan.register()
    
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    # SavePoints.ExportRayScan.unregister()

if __name__ == "__main__":
    register()
