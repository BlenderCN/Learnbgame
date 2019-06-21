import bpy
from . registration import get_addon


def gp_add_to_edit_mode_group(context, obj):
    grouppro, _, _, _ = get_addon("Group Pro")

    # check if gp is in edit mode then add the decal
    if grouppro and len(context.scene.storedGroupSettings):
        bpy.ops.object.add_to_grouppro()

        # gp deselects, so select it again
        obj.select_set(True)
        context.view_layer.objects.active = obj


def gp_get_edit_group(context):
    last = len(context.scene.storedGroupSettings) - 1
    storage = context.scene.storedGroupSettings[last]
    return bpy.data.objects.get(storage.currentEmptyName)
