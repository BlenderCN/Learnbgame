import os

import bpy

from . import addon, id, ray, remove, regex, update

thumbnails = {}
operator = None

def authoring():
    preference = addon.preference()

    insert_file = False
    for folder in preference.folders:
        if os.path.commonprefix([bpy.data.filepath, folder.location]) == folder.location:
            if os.path.basename(bpy.data.filepath) != 'render_scene.blend':
                insert_file = True
                break

    return insert_file if not bpy.context.scene.kitops.thumbnail_scene else False

def hide_handler(op):
    option = addon.option()
    hide = False

    if op.duplicate:
        ray.cast(op)
        hide = not ray.success

        for object in op.inserts:
            object.hide = hide

        for object in op.cutter_objects:
            for modifier in op.boolean_target.modifiers:
                if modifier.type == 'BOOLEAN' and modifier.object == object:
                    modifier.show_viewport = not hide

def collect(objects=[], mains=False, solids=False, cutters=False, wires=False, all=False):

    if all:
        inserts = [object for object in bpy.data.objects if object.kitops.insert]

    else:
        inserts = [object for object in objects if object.kitops.insert]

        for check_object in inserts:
            for object in bpy.context.scene.objects:
                if object.kitops.id == check_object.kitops.id:
                    if object not in inserts:
                        inserts.append(object)

    if mains:
        return [object for object in inserts if object.kitops.main]

    elif solids:
        return [object for object in inserts if object.kitops.type == 'SOLID']

    elif cutters:
        return [object for object in inserts if object.kitops.type == 'CUTTER']

    elif wires:
        return [object for object in inserts if object.kitops.type == 'WIRE']

    return inserts

def add(op, context):
    preference = addon.preference()
    option = addon.option()

    with bpy.data.libraries.load(op.location) as (blend, imported):
        imported.scenes = blend.scenes
        imported.materials = blend.materials

    op.inserts = []
    for scene in imported.scenes:
        if not scene.kitops.thumbnail_scene:
            for object in sorted(scene.objects, key=lambda object: object.name):
                if object not in op.inserts and object.kitops.insert and not object.kitops.inserted:
                    op.inserts.append(object)

    op.cutter_objects = [object for object in op.inserts if object.kitops.type == 'CUTTER']

    new_id = id.uuid()
    for object in op.inserts:
        object.name = 'ko_{}_{}'.format(os.path.basename(op.location)[:-6], object.name.lower())
        object.kitops.inserted = True
        object.kitops.id = new_id
        object.kitops.label = regex.clean_name(os.path.basename(op.location), use_re=preference.clean_names)
        object.kitops.collection = regex.clean_name(os.path.basename(str(op.location)[:-len(os.path.basename(op.location)) - 1]), use_re=preference.clean_names)

        if preference.mode == 'REGULAR':
            object.kitops.applied = True

        if op.boolean_target:
            object.kitops['insert_target'] = op.boolean_target
            object.kitops.reserved_target = op.boolean_target

        for slot in object.material_slots:
            if slot.material and 'ko_{}'.format(slot.material.name) in bpy.data.materials:
                old_material = bpy.data.materials[slot.material.name]
                slot.material = bpy.data.materials['ko_{}'.format(old_material.name)]
                bpy.data.materials.remove(old_material, do_unlink=True, do_id_user=True, do_ui_user=True)
            elif slot.material:
                bpy.data.materials[slot.material.name].name = 'ko_{}'.format(slot.material.name)

    blacklist = []
    for object in op.inserts:
        if not object.layers[:][0] == True:
            blacklist.append(object)

    for object in op.inserts:
        if object not in blacklist:
            context.scene.objects.link(object)

            if object.kitops.label not in bpy.data.groups:
                bpy.data.groups.new(object.kitops.label)

            bpy.data.groups[object.kitops.label].objects.link(object)

            if object.kitops.main:
                object.select = True
                context.scene.objects.active = object
            else:
                object.select = False

    if op.boolean_target:
        for object in op.cutter_objects:
            add_boolean(object)

    op.main = context.active_object

    for object in op.inserts:
        object.kitops.main_object = op.main

    if op.init_selected and op.boolean_target:
        update.insert_scale(None, context)

    for scene in imported.scenes:
        bpy.data.scenes.remove(scene, do_unlink=True)

    for material in imported.materials:
        try:
            if not material.name.startswith('ko_'):
                bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)
        except: continue

    update.insert_scale(None, context)

def add_boolean(object):
    modifier = object.kitops.insert_target.modifiers.new(name='{}: {}'.format(object.kitops.boolean_type.title(), object.name), type='BOOLEAN')
    modifier.show_expanded = False
    modifier.operation = object.kitops.boolean_type
    modifier.object = object
    object.show_all_edges = False

def select():
    global operator

    if addon.option().auto_select:
        inserts = collect(bpy.context.selected_objects)
        main_objects = collect(inserts, mains=True)

        for object in inserts:
            if not operator:
                if object.kitops.selection_ignore and object.select:
                    addon.option().auto_select = False

                    for deselect in inserts:
                        if deselect != object:
                           deselect.object.select = False

                    break

                elif not object.kitops.selection_ignore:
                    object.select = True
            else:
                object.select = True

            if not operator:
                object.hide = False

            if bpy.context.active_object and bpy.context.active_object.kitops.insert:
                for main in main_objects:
                    if main.kitops.id == bpy.context.active_object.kitops.id:
                        bpy.context.scene.objects.active = main

                        if not operator and main:
                            bpy.context.active_object.hide = False

def show_solid_objects():
    for object in collect(solids=True, all=True):
        if not object.select and not addon.option().show_solid_objects:
            object.hide = True

        elif addon.option().show_solid_objects:
            object.hide = False

def show_cutter_objects():
    for object in collect(cutters=True, all=True):
        if not object.select and not addon.option().show_cutter_objects:
            object.hide = True

        elif addon.option().show_cutter_objects:
            object.hide = False

def show_wire_objects():
    for object in collect(wires=True, all=True):
        if not object.select and not addon.option().show_wire_objects:
            object.hide = True

        elif addon.option().show_wire_objects:
            object.hide = False

def correct_ids():
    main_objects = collect(mains=True, all=True)

    ids = []
    correct = []
    for object in main_objects:
        if object.kitops.id not in ids:
            ids.append(object.kitops.id)
        else:
            correct.append(object)

    inserts = collect(all=True)

    for main in correct:
        new_id = id.uuid()
        for object in inserts:
            if object.kitops.main_object == main:
                object.kitops.id = new_id
