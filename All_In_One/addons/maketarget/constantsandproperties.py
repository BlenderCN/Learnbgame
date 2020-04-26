import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

def registerMakeTargetObjectProperties():

    bpy.types.Scene.MhUnlock = BoolProperty(default=False)
    bpy.types.Object.ProxyFile = StringProperty(default="")
    bpy.types.Object.ObjFile = StringProperty(default="")
    bpy.types.Object.MhHuman = BoolProperty(default=False)
    bpy.types.Object.MhDeleteHelpers = BoolProperty(name="Delete Helpers", default=False)
    bpy.types.Object.MhUseMaterials = BoolProperty(name="Use Materials", default=False)
    bpy.types.Object.MhPruneWholeDir = BoolProperty(name="Prune Entire Directory", default=False)
    bpy.types.Object.MhPruneEnabled = BoolProperty(name="Pruning Enabled", default=False)
    bpy.types.Object.MhPruneRecursively = BoolProperty(name="Prune Folders Recursively", default=False)
    bpy.types.Object.MhFilePath = StringProperty(default="")
    bpy.types.Object.MhMeshVersion = StringProperty(default="None")

    bpy.types.Object.MhAffectOnly = EnumProperty(
        items=[('Body', 'Body', 'Body'),
               ('Tights', 'Tights', 'Tights'),
               ('Skirt', 'Skirt', 'Skirt'),
               ('Hair', 'Hair', 'Hair'),
               ('All', 'All', 'All')],
        default='All')

    bpy.types.Object.MhIrrelevantDeleted = BoolProperty(name="Irrelevant deleted", default=False)
    bpy.types.Object.MhMeshVertsDeleted = BoolProperty(name="Cannot load", default=False)
    bpy.types.Object.SelectedOnly = BoolProperty(name="Selected verts only", default=True)
    bpy.types.Object.MhZeroOtherTargets = BoolProperty(name="Active target only", description="Save the active (last) target only, setting the values of all other targets to 0", default=False)

def registerMakeTargetSceneProperties():

    bpy.types.Scene.MhBodyType = EnumProperty(
        items=[('None', 'Base Mesh', 'None'),
               ('caucasian-male-young', 'Average Male', 'caucasian-male-young'),
               ('caucasian-female-young', 'Average Female', 'caucasian-female-young'),
               ],
        description="Character to load",
        default='caucasian-female-young')



