import bpy


def get_inactive_selected_objects():
    selected_objects = list(bpy.context.selected_objects)
    if bpy.context.active_object in selected_objects:
        selected_objects.remove(bpy.context.active_object)
    return selected_objects


def get_current_selected_status():
    active_object = bpy.context.active_object
    other_objects = get_inactive_selected_objects()
    other_object = None
    if len(other_objects) == 1:
            other_object = other_objects[0]

    return active_object, other_objects, other_object
