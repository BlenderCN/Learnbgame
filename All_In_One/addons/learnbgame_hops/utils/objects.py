import bpy


def set_active(object, select = False, only_select = False):
    bpy.context.view_layer.objects.active = object
    if only_select: deselect_all()
    if select or only_select: bpy.context.view_layer.objects.active.select_set(state=True)


def link_objects_to_scene(objects):
    for object in objects:
        link_object_to_scene(object)


def link_object_to_scene(object):
    bpy.context.scene.objects.link(object)


def only_select(objects):
    if not hasattr(objects, "__iter__"): objects = [objects]

    deselect_all()
    for object in objects:
        object.select_set(state=True)


def deselect_all():
    for object in bpy.context.view_layer.objects:
        object.select_set(state=False)


def get_inactive_selected_objects():
    selected_objects = list(bpy.context.selected_objects)
    if bpy.context.active_object in selected_objects:
        selected_objects.remove(bpy.context.active_object)
    return selected_objects


def get_objects_in_same_group(object):
    groups = [group for group in bpy.data.groups if object in group.objects]
    return [object for object in group.objects for group in groups]


def remove_object_from_scene(object):
    bpy.context.scene.objects.unlink(object)


def link_objects_to_group(group, objects):
    for object in objects:
        group.objects.link(object)


def get_or_create_group(name):
    group = bpy.data.groups.get(name)
    if group is None:
        group = bpy.data.groups.new(name)
    return group


def get_modifier_with_type(object, modifier_type):
    for modifier in object.modifiers:
        if modifier.type == modifier_type:
            return modifier
    return None


def apply_modifiers(object, modtypes):
    modifiers = object.modifiers
    for mod in modifiers:
        if mod.type in modtypes:
            if mod.type == "BOOLEAN":
                if mod.object and not mod.object.hops.status == "BOOLSHAPE2":
                    bpy.ops.object.modifier_apply(apply_as="DATA", modifier=mod.name)
            else:
                bpy.ops.object.modifier_apply(apply_as="DATA", modifier=mod.name)


def apply_modifier(modifier):
    set_active(modifier.id_data)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def move_modifier_up(modifier):
    object = modifier.id_data
    for _ in range(list(object.modifiers).index(modifier)):
        bpy.ops.object.modifier_move_up(modifier=modifier.name)


def new_deep_object_copy(object):
    new_data = object.data.copy()
    new_object = object.copy()
    new_object.data = new_data
    return new_object


def join_objects(*objects):
    only_select(objects)
    set_active(objects[0])
    bpy.ops.object.join()
    return objects[0]


def obj_quads_to_tris():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')


def get_current_selected_status():
    active_object = bpy.context.active_object
    other_objects = get_inactive_selected_objects()
    other_object = None
    if len(other_objects) == 1:
            other_object = other_objects[0]

    return active_object, other_objects, other_object


def mesh_of_activeobj_select(select='SELECT'):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    if select == 'SELECT':
        bpy.ops.mesh.select_all(action='SELECT')
    elif select == 'DESELECT':
        bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
