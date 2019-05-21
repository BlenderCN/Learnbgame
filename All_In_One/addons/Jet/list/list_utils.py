import bpy

def get_hi_res_prop(context):
    low_res = context.scene.Jet.list_low_res
    items = len(low_res.obj_list)
    idx = low_res.obj_list_index
    idx = idx if idx < items else 0
    return low_res.obj_list[idx].list_high_res

def check_selected_objs(context):
    # Enabled when, at least, one mesh object is selected
    selected_objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
    return len(selected_objs) > 0

def add_obj_to_list(prop, obj):
    # Add the obj to the list
    item = prop.obj_list.add()
    # item.obj stores the obj
    item.object = obj

def add_objs(prop, context):
    # Retrieve the ids of all objects in the list
    objs_in_list = [o.object for o in prop.obj_list]
    for obj in [o for o in context.scene.objects if o.select and o.type == 'MESH']:
        # If the object id is already on the list, continue to the next object
        if obj in objs_in_list:
            continue

        add_obj_to_list(prop, obj)

    if len(prop.obj_list)==1:
        prop.obj_list_index = 0


def remove_obj(prop):
    # Index of the selected item in the list
    obj_idx = prop.obj_list_index

    new_idx = 0 if obj_idx < 1 else obj_idx-1
    prop.obj_list_index = new_idx

    # The selected item is removed from the list
    prop.obj_list.remove(obj_idx)

def clear_objs(prop):
    items = len(prop.obj_list)
    for obj_idx in reversed(range(items)):
        prop.obj_list.remove(obj_idx)


def select_objs(prop, select):
    for obj in prop.obj_list:
        if not hasattr(obj, "object") or type(obj.object) != bpy.types.Object:
            continue
        obj.object.select = select

def hide_objs(prop, hide):
    for obj in prop.obj_list:
        if not hasattr(obj, "object") or type(obj.object) != bpy.types.Object:
            continue
        obj.object.hide = hide