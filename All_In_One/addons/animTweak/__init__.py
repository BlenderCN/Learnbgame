bl_info = {
    "name": "Animation Tweaks",
    "author": "Christophe Seux, Manuel Rais",
    "version": (0, 1),
    "blender": (2, 77, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    imp.reload(operators)
    imp.reload(panels)

else:
    from . import operators
    from . import panels

import bpy

def storedPoseLib(scene, context):
    items = []

    ob = context.object

    if ob is not None:
        if ob.type == 'ARMATURE':
            poseLibs = [a.name for a in bpy.data.actions if len(a.pose_markers)>0]
            if ob.PoseLibCustom.filtered == True :

                idName = ob.name.split('_')[0]
                poseLibs = [p for p in poseLibs if p.split('_')[0] == idName]

                for i,poseLib in enumerate(sorted(poseLibs, reverse=True)):
                    items.append((poseLib,poseLib,"",'ACTION',i))
            else :
                for i,poseLib in enumerate(sorted(poseLibs, reverse=True)):
                    items.append((poseLib,poseLib,"",'ACTION',i))
    return items


class PoseLibCustomSettings(bpy.types.PropertyGroup) :
    filtered = bpy.props.BoolProperty(default = True,description='Filter by base Name')
    poseLibs = bpy.props.EnumProperty(items =storedPoseLib,name= 'Pose Library')


addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.PoseLibCustom = bpy.props.PointerProperty(type = PoseLibCustomSettings)
    bpy.types.Armature.DefaultValues = bpy.props.PointerProperty(type= bpy.types.PropertyGroup)

    addon = bpy.context.window_manager.keyconfigs.addon
    if addon:
        km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
        km.keymap_items.new("pose.insert_keyframe", type = "K", value = "PRESS")
        km.keymap_items.new("pose.reset_props", type = "X", value = "PRESS")
        addon_keymaps.append(km)


def unregister():
    del bpy.types.Armature.DefaultValues
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    bpy.utils.unregister_module(__name__)
