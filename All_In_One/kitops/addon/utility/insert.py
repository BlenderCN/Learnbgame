import os

import bpy

from . import addon, id, ray, remove, regex, update, modifier

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

        for obj in op.inserts:
            obj.hide_viewport = hide

        for obj in op.cutter_objects:
            for modifier in op.boolean_target.modifiers:
                if modifier.type == 'BOOLEAN' and modifier.object == obj:
                    modifier.show_viewport = not hide

def collect(objs=[], mains=False, solids=False, cutters=False, wires=False, all=False):

    if all:
        inserts = [obj for obj in bpy.data.objects if obj.kitops.insert]

    else:
        inserts = [obj for obj in objs if obj.kitops.insert]

        for check_object in inserts:
            for obj in bpy.data.objects:
                if obj.kitops.id == check_object.kitops.id:
                    if obj not in inserts:
                        inserts.append(obj)

    if mains:
        return [obj for obj in inserts if obj.kitops.main]

    elif solids:
        return [obj for obj in inserts if obj.kitops.type == 'SOLID']

    elif cutters:
        return [obj for obj in inserts if obj.kitops.type == 'CUTTER']

    elif wires:
        return [obj for obj in inserts if obj.kitops.type == 'WIRE']

    return inserts

def add(op, context):
    preference = addon.preference()
    option = addon.option()

    basename = os.path.basename(op.location)

    with bpy.data.libraries.load(op.location) as (blend, imported):
        imported.objects = blend.objects
        # imported.scenes = blend.scenes
        imported.materials = blend.materials

    op.inserts = []

    for obj in sorted(imported.objects, key=lambda obj: obj.name):
        op.inserts.append(obj)

    op.cutter_objects = [obj for obj in op.inserts if obj.kitops.type == 'CUTTER']

    new_id = id.uuid()
    kitops_materials = [mat.name for mat in bpy.data.materials if mat.kitops.material]

    for obj in op.inserts:
        obj.name = regex.clean_name(F'{basename[:-6].title()}_{obj.name.title()}', use_re=preference.clean_names)
        obj.kitops.inserted = True
        obj.kitops.id = new_id
        obj.kitops.label = regex.clean_name(basename, use_re=preference.clean_names)
        obj.kitops.collection = regex.clean_name(os.path.basename(str(op.location)[:-len(os.path.basename(op.location)) - 1]), use_re=preference.clean_names)

        if preference.mode == 'REGULAR':
            obj.kitops.applied = True

        if op.boolean_target:
            obj.kitops['insert_target'] = op.boolean_target
            obj.kitops.reserved_target = op.boolean_target

        for slot in obj.material_slots:
            if slot.material and regex.clean_name(slot.material.name, use_re=preference.clean_names) in kitops_materials and not op.material:
                old_material = bpy.data.materials[slot.material.name]
                slot.material = bpy.data.materials[regex.clean_name(slot.material.name, use_re=preference.clean_names)]

                if old_material.users == 0:
                    bpy.data.materials.remove(old_material, do_unlink=True, do_id_user=True, do_ui_user=True)

            elif slot.material and not op.material:
                bpy.data.materials[slot.material.name].name = regex.clean_name(slot.material.name, use_re=preference.clean_names)
                bpy.data.materials[slot.material.name].kitops.material = True

            elif slot.material:
                if op.material_link and regex.clean_name(slot.material.name, use_re=preference.clean_names) in kitops_materials:
                    op.import_material = bpy.data.materials[regex.clean_name(slot.material.name, use_re=preference.clean_names)]
                    break

                else:
                    bpy.data.materials[slot.material.name].name = regex.clean_name(slot.material.name, use_re=preference.clean_names)
                    op.import_material = slot.material
                    bpy.data.materials[slot.material.name].kitops.material = True
                    break

    blacklist = []

    for obj in op.inserts:
        if obj not in blacklist:
            if regex.clean_name(basename[:-6].title(), use_re=preference.clean_names) not in bpy.data.collections:
                bpy.data.collections['INSERTS'].children.link(bpy.data.collections.new(name=regex.clean_name(basename[:-6].title(), use_re=preference.clean_names)))

            bpy.data.collections[regex.clean_name(basename[:-6].title(), use_re=preference.clean_names)].objects.link(obj)
            obj.kitops.applied = False

            if obj.kitops.main:
                bpy.context.view_layer.objects.active = obj


    if op.boolean_target:
        for obj in op.cutter_objects:
            add_boolean(obj)

    op.main = context.active_object
    # if op.init_active:
    #     op.main.parent = op.init_active

    for obj in op.inserts:
        obj.kitops.main_object = op.main

    if op.init_selected and op.boolean_target:
        update.insert_scale(None, context)

    for scene in imported.scenes:
        bpy.data.scenes.remove(scene, do_unlink=True)

    for material in imported.materials:
        try:
            if not material.kitops.material:
                bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)
        except: continue

    for obj in op.inserts:
        obj.kitops.insert = True
        obj.data.kitops.insert = True

    update.insert_scale(None, context)

def add_boolean(obj):
    mod = obj.kitops.insert_target.modifiers.new(name='{}: {}'.format(obj.kitops.boolean_type.title(), obj.name), type='BOOLEAN')
    mod.show_expanded = False
    mod.operation = obj.kitops.boolean_type
    mod.object = obj
    obj.show_all_edges = False

    modifier.sort(obj.kitops.insert_target)

def select():
    global operator

    if addon.option().auto_select:
        inserts = collect(bpy.context.selected_objects)
        main_objects = collect(inserts, mains=True)

        for obj in inserts:
            if not operator:
                if obj.kitops.selection_ignore and obj.select_get():
                    addon.option().auto_select = False

                    for deselect in inserts:
                        if deselect != obj:
                           deselect.select_set(False)

                    break

                elif not obj.kitops.selection_ignore:
                    obj.select_set(True)
            else:
                obj.select_set(True)

            if not operator:
                obj.hide_viewport = False

            if bpy.context.active_object and bpy.context.active_object.kitops.insert:
                for main in main_objects:
                    if main.kitops.id == bpy.context.active_object.kitops.id:
                        bpy.context.view_layer.objects.active = main

                        if not operator and main:
                            bpy.context.active_object.hide_viewport = False

def show_solid_objects():
    for obj in collect(solids=True, all=True):
        try:
            if not obj.select_get() and not addon.option().show_solid_objects:
                obj.hide_viewport = True

            elif addon.option().show_solid_objects:
                obj.hide_viewport = False
        except RuntimeError: pass

def show_cutter_objects():
    for obj in collect(cutters=True, all=True):
        try:
            if not obj.select_get() and not addon.option().show_cutter_objects:
                obj.hide_viewport = True

            elif addon.option().show_cutter_objects:
                obj.hide_viewport = False
        except RuntimeError: pass

def show_wire_objects():
    for obj in collect(wires=True, all=True):
        try:
            if not obj.select_get() and not addon.option().show_wire_objects:
                obj.hide_viewport = True

            elif addon.option().show_wire_objects:
                obj.hide_viewport = False
        except RuntimeError: pass

def correct_ids():
    main_objects = collect(mains=True, all=True)

    ids = []
    correct = []
    for obj in main_objects:
        if obj.kitops.id not in ids:
            ids.append(obj.kitops.id)
        else:
            correct.append(obj)

    inserts = collect(all=True)

    for main in correct:
        new_id = id.uuid()
        for obj in inserts:
            if obj.kitops.main_object == main:
                obj.kitops.id = new_id
