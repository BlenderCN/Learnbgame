import bpy


def get_selected_or_all():
    selected = bpy.context.selected_objects
    if len(selected) < 1:
        selected = bpy.data.objects
    return selected