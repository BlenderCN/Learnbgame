import os

import bpy

from bpy.types import Operator
from bpy.props import *

from . import addon, bbox, id, insert, remove

def authoring_save_pre():
    option = addon.option()

    if insert.authoring() and bpy.data.filepath != addon.path.thumbnail_scene():

        bpy.ops.object.mode_set(mode='OBJECT')
        for object in bpy.data.objects:
            object.kitops.id = ''
            object.kitops.author = option.author
            object.kitops.insert = True
            object.kitops.animated = bpy.context.scene.kitops.animated

            if object.data:
                object.data.kitops.id = id.uuid()
                object.data.kitops.insert = True

        main = [object for object in bpy.context.scene.objects if object.kitops.main][0]
        bpy.context.scene.objects.active = main

        if bpy.context.scene.kitops.auto_parent and not bpy.context.scene.kitops.thumbnail_scene:
            bpy.ops.object.visual_transform_apply()

            for object in bpy.context.scene.objects:
                object.parent = None

            for object in bpy.context.scene.objects:
                object.select = True

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

def authoring_load_post():
    option = addon.option()

    author = False
    for object in bpy.data.objects:
        if object.kitops.author:
            author = object.kitops.author
            break

    if author:
        option.author = author

    else:
        option.author = addon.preference().author
        for object in bpy.data.objects:
            object.kitops.author = addon.preference().author

    main = False
    for object in bpy.data.objects:
        if object.kitops.main:
            main = True
            break

    if not main:
        if bpy.context.active_object:
            bpy.context.active_object.kitops.main = True
        elif len(bpy.data.objects):
            bpy.data.objects[0].kitops['main'] = True

def toggles_scene_update_post():
    option = addon.option()

    solid_inserts = insert.collect(solids=True, all=True)
    count = 0
    for object in solid_inserts:
        if object.hide:
            option['show_solid_objects'] = False
            break
        elif not object.select:
            count += 1

    if count > 2 and count == len(solid_inserts):
        option['show_solid_objects'] = True

    boolean_inserts = insert.collect(cutters=True, all=True)
    count = 0
    for object in boolean_inserts:
        if object.hide:
            option['show_cutter_objects'] = False
            break
        elif not object.select:
            count += 1

    if count > 2 and count == len(boolean_inserts):
        option['show_cutter_objects'] = True

    wire_inserts = insert.collect(wires=True, all=True)
    count = 0
    for object in wire_inserts:
        if object.hide:
            option['show_wire_objects'] = False
            break
        elif not object.select:
            count += 1

    if count > 2 and count == len(wire_inserts):
        option['show_wire_objects'] = True

def authoring_scene_update_post():
    if len(bpy.data.objects) == 1:
        bpy.data.objects[0].kitops['main'] = True

    for object in bpy.data.objects:
        if object.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE'}:
            object.kitops.type = 'WIRE'
        if object.type != 'MESH' and object.kitops.type == 'CUTTER':
            object.kitops.type = 'WIRE'
        if object.kitops.main and object.kitops.selection_ignore:
            object.kitops.selection_ignore = False

def insert_scene_update_pre():
    if addon.preference().mode == 'SMART':
        if not insert.operator:
            insert.show_solid_objects()
            insert.show_cutter_objects()
            insert.show_wire_objects()

        objects = [object for object in bpy.data.objects if not object.kitops.insert and object.type == 'MESH']
        inserts = [object for object in sorted(bpy.data.objects, key=lambda object: object.name) if object.kitops.insert and not object.kitops.applied]

        for object in inserts:
            if object.kitops.type == 'CUTTER' and object.kitops.insert_target:
                available = False
                for modifier in object.kitops.insert_target.modifiers:
                    if modifier.type == 'BOOLEAN' and modifier.object == object:
                        available = True

                        break

                if not available:
                    #TODO: remove all bools for insert and reapply in order (maintain consistent order)
                    insert.add_boolean(object)

            if object.kitops.type == 'CUTTER':
                for target in objects:
                    for modifier in target.modifiers:
                        if modifier.type == 'BOOLEAN' and modifier.object == object and target != object.kitops.insert_target:

                            target.modifiers.remove(modifier)

def new_empty():
    empty = bpy.data.objects.new('KIT OPS Mirror Target', None)
    empty.location = bpy.context.active_object.kitops.insert_target.location
    empty.empty_draw_size = 0.01

    bpy.context.scene.objects.link(empty)

    return empty

def add_mirror(object, axis='X'):
    object.kitops.mirror = True
    modifier = object.modifiers.new(name='KIT OPS Mirror', type='MIRROR')
    if modifier:
        modifier.use_x = False

        setattr(modifier, 'use_{}'.format(axis.lower()), getattr(object.kitops, 'mirror_{}'.format(axis.lower())))

        empty = None
        for obj in bpy.data.objects:
            if obj and obj.type == 'EMPTY' and obj.location == object.kitops.insert_target.location:
                empty = obj

        modifier.mirror_object = empty if empty else new_empty()
        object.kitops.mirror_target = modifier.mirror_object

def validate_mirror(inserts, axis='X'):
    for object in inserts:
        if object.kitops.mirror:

            available = False
            # assuming our mirror is most recent
            for modifier in reversed(object.modifiers):

                if modifier.type == 'MIRROR' and modifier.mirror_object == object.kitops.mirror_target:
                    available = True
                    setattr(modifier, 'use_{}'.format(axis.lower()), getattr(object.kitops, 'mirror_{}'.format(axis.lower())))

                    if (modifier.use_x, modifier.use_y, modifier.use_z) == (False, False, False):
                        object.kitops.mirror = False
                        remove.object(object.kitops.mirror_target)
                        object.kitops.mirror_target = None
                        object.modifiers.remove(modifier)

                    break

            if not available:
                add_mirror(object, axis=axis)

        else:
            add_mirror(object, axis=axis)

def apply_booleans(inserts):
    targets = []
    for object in inserts:
        if object.kitops.insert_target not in targets:
            targets.append(object.kitops.insert_target)

    for target in targets:
        duplicate = target.copy()
        duplicate.data = target.data.copy()

        target_inserts = []
        for modifier in duplicate.modifiers:
            if modifier.type == 'BOOLEAN' and modifier.object in inserts:
                target_inserts.append(modifier.object)

        duplicate.modifiers.clear()

        for object in target_inserts:
            object.kitops['insert_target'] = duplicate

        bpy.context.scene.update()

        duplicate.data = duplicate.to_mesh(bpy.context.scene, apply_modifiers=True, settings='PREVIEW', calc_tessface=False)

        old_data = bpy.data.meshes[target.data.name]
        name = old_data.name

        target.data = duplicate.data
        target.data.name = name

        duplicate.data = old_data
        remove.object(duplicate, data=True)

def remove_booleans(inserts, targets=[], clear_target=False):
    for object in inserts:
        if object.kitops.insert_target and object.kitops.insert_target not in targets:
            targets.append(object.kitops.insert_target)

    for target in targets:

        modifiers = []
        try:
            for modifier in target.modifiers:
                if modifier.type == 'BOOLEAN' and modifier.object in inserts:
                    modifiers.append(modifier)
        except: pass

        for modifier in modifiers:
            target.modifiers.remove(modifier)

    if clear_target:
        for object in inserts:
            object.kitops['insert_target'] = None

def clear(inserts):
    for object in inserts:
        object.kitops.insert = False
        object.kitops['insert_target'] = None

def delete(inserts):
    for object in inserts:
        remove.object(object, data=True)

class ApplyInsert(Operator):
    bl_idname = 'kitops.apply_insert'
    bl_label = 'Apply'
    bl_description = 'Apply selected INSERTS'
    bl_options = {'REGISTER', 'UNDO'}

    apply_modifiers = BoolProperty(
        name = 'Apply modifiers',
        description = 'Apply modifiers for the selected ISNERTS',
        default = True)

    keep_insert = BoolProperty(
        name = 'Keep INSERT',
        description = 'Keep the selected INSERTS after applying',
        default = True)

    make_real = BoolProperty(
        name = 'Make real',
        description = 'Strip selected INSERTS of all kitops related behavior permanently',
        default = False)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'apply_modifiers')
        layout.prop(self, 'keep_insert')

        if self.keep_insert:
            layout.prop(self, 'make_real')

    def execute(self, context):

        inserts = insert.collect(context.selected_objects)

        if self.apply_modifiers:
            apply_booleans(inserts)

            for object in inserts:
                object.kitops['insert_target'] = None
        else:
            for object in inserts:
                object.kitops.applied = True
                object.kitops['insert_target'] = None

        if not self.keep_insert:
            delete(inserts)

        if self.make_real:
            try: insert.clear(inserts)
            except: pass

        return {'FINISHED'}

class RemoveInsert(Operator):
    bl_idname = 'kitops.remove_insert'
    bl_label = 'Delete'
    bl_description = 'Remove selected INSERTS'
    bl_options = {'REGISTER', 'UNDO'}

    apply_modifiers = BoolProperty(
        name = 'Apply modifiers',
        description = 'Apply modifiers for the selected INSERTS',
        default = False)

    make_real = BoolProperty(
        name = 'Make real',
        description = 'Strip selected INSERTS of all kitops related behavior permanently',
        default = False)

    def execute(self, context):
        inserts = insert.collect(context.selected_objects)

        if self.apply_modifiers:
            apply_booleans(inserts)

        if self.make_real:
            clear(inserts)

        else:
            for object in inserts:
                remove.object(object, data=True)

        return {'FINISHED'}

class RenderThumbnail(Operator):
    bl_idname = 'kitops.render_thumbnail'
    bl_label = 'Render thumbnail'
    bl_description = 'Render and save a thumbnail for this INSERT\n  CTRL - Import thumbnail scene\n  ALT - Render all thumbnails for the current working directory\n\n  Use system console to see progress (Window > Toggle system console)'
    bl_options = {'INTERNAL'}

    render = BoolProperty(default=False)

    max_dimension = 1.8

    def invoke(self, context, event):
        preference = addon.preference()
        init_active = bpy.data.objects[context.active_object.name]
        init_scene = bpy.data.scenes[context.scene.name]
        duplicates = []
        parents = []

        if not self.render:

            print('\nKIT OPS beginning thumbnail rendering')
            preference.mode = 'SMART'

            with bpy.data.libraries.load(addon.path.thumbnail_scene()) as (blend, thumbnail):
                print('\tImported thumbnail rendering scene')
                thumbnail.scenes = blend.scenes
                thumbnail.materials = blend.materials

            scene = thumbnail.scenes[0]
            context.screen.scene = scene

            for object in scene.objects:
                object.select = False

            floor = [object for object in context.scene.objects if object.kitops.ground_box][0]

            for object in init_scene.objects:
                duplicate = object.copy()
                duplicate.name = 'ko_duplicate_{}'.format(object.name)
                if duplicate.type != 'EMPTY':
                    duplicate.data = object.data.copy()

                duplicates.append(duplicate)
                parents.append((duplicate, object.parent))

                context.scene.objects.link(duplicate)

                duplicate.kitops.insert = True
                duplicate.kitops.id = 'tmp'
                duplicate.kitops.applied = False
                duplicate.kitops['insert_target'] = floor

                duplicate.select = True
                duplicate.hide = False

                if duplicate.kitops.type == 'CUTTER' and duplicate.kitops.boolean_type == 'UNION':
                    duplicate.data.materials.clear()
                    duplicate.data.materials.append(bpy.data.materials['ADD'])

                elif duplicate.kitops.type == 'CUTTER' and duplicate.kitops.boolean_type in {'DIFFERENCE', 'INTERSECT'}:
                    duplicate.data.materials.clear()
                    duplicate.data.materials.append(bpy.data.materials['SUB'])

                elif duplicate.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                    if not len(duplicate.data.materials):
                        duplicate.data.materials.append(bpy.data.materials['OBJECT'])

            print('\tDuplicated objects from initial scene')
            print('\tConverted duplicates into a temporary insert')
            print('\nUpdated:')
            print('\tInsert materials')

            for duplicate, parent in parents:
                if parent and 'ko_duplicate_{}'.format(parent.name) in [duplicate.name for duplicate in duplicates]:
                    duplicate.parent = bpy.data.objects['ko_duplicate_{}'.format(parent.name)]

            print('\tInsert parenting')

            if event.alt or event.ctrl:
                main = [duplicate for duplicate in duplicates if duplicate.kitops.main][0]
                context.scene.objects.active = main
                bpy.ops.view3d.viewnumpad(type='CAMERA')
                dimension = main.dimensions

                axis = 'x'
                if dimension.y > dimension.x:
                    axis = 'y'
                if dimension.z > getattr(dimension, axis):
                    axis = 'z'

                setattr(dimension, axis, self.max_dimension)

                remaining_axis = [a for a in 'xyz' if a != axis]
                setattr(main.scale, remaining_axis[0], getattr(main.scale, axis))
                setattr(main.scale, remaining_axis[1], getattr(main.scale, axis))

                print('\tInsert size (max dimension of {})'.format(self.max_dimension))

            context.scene.render.filepath = bpy.data.filepath[:-6] + '.png'
            print('\tRender path: {}'.format(context.scene.render.filepath))

            if not event.ctrl:
                print('\nRendering...')
                bpy.ops.render.render(write_still=True)

            if not event.alt and not event.ctrl:

                print('Cleaning up\n')
                for object in duplicates:
                    remove.object(object, data=True)

                context.screen.scene = init_scene

                for scene in thumbnail.scenes:
                    for object in scene.objects:
                        remove.object(object, data=True)

                    bpy.data.scenes.remove(scene, do_unlink=True)

                for material in thumbnail.materials:
                    bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                init_scene.objects.active = init_active

                for object in init_scene.objects:
                    object.select = True
                    object.hide = False

                print('Finished\n')

            if event.alt and not event.ctrl:

                print('Removing insert')
                for object in duplicates:
                    remove.object(object, data=True)

                working_directory = os.path.abspath(os.path.join(bpy.data.filepath, '..'))
                print('\n\nBeginning batch rendering in {}\n'.format(working_directory))
                for file in os.listdir(working_directory):
                    if file.endswith('.blend') and os.path.join(working_directory, file) != bpy.data.filepath:
                        location = os.path.join(working_directory, file)

                        with bpy.data.libraries.load(location) as (blend, imported):
                            print('\nImported objects from {}'.format(location))
                            imported.scenes = blend.scenes
                            imported.materials = blend.materials

                        scene = [scene for scene in imported.scenes if not scene.kitops.thumbnail_scene][0]

                        if not len(scene.objects):
                            print('Invalid file... skipping\n')
                            continue

                        elif not len([object for object in scene.objects if object.kitops.main]):
                            print('Invalid file... skipping\n')
                            continue

                        for object in scene.objects:
                            context.scene.objects.link(object)

                            object.kitops.insert = True
                            object.kitops.id = 'tmp'
                            object.kitops.applied = False
                            object.kitops['insert_target'] = floor

                            object.select = True
                            object.hide = False

                            if object.kitops.type == 'CUTTER' and object.kitops.boolean_type == 'UNION':
                                object.data.materials.clear()
                                object.data.materials.append(bpy.data.materials['ADD'])

                            elif object.kitops.type == 'CUTTER' and object.kitops.boolean_type in {'DIFFERENCE', 'INTERSECT'}:
                                object.data.materials.clear()
                                object.data.materials.append(bpy.data.materials['SUB'])

                            elif object.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}:
                                if not len(object.data.materials):
                                    object.data.materials.append(bpy.data.materials['OBJECT'])

                        print('\nUpdated:')
                        print('\tInsert target: {}'.format(floor.name))
                        print('\tInsert materials')

                        main = [object for object in context.scene.objects if object.kitops.main][0]
                        dimension = main.dimensions

                        axis = 'x'
                        if dimension.y > dimension.x:
                            axis = 'y'
                        if dimension.z > getattr(dimension, axis):
                            axis = 'z'

                        setattr(dimension, axis, self.max_dimension)

                        remaining_axis = [a for a in 'xyz' if a != axis]
                        setattr(main.scale, remaining_axis[0], getattr(main.scale, axis))
                        setattr(main.scale, remaining_axis[1], getattr(main.scale, axis))

                        print('\tInsert size (max dimension of {})'.format(self.max_dimension))

                        context.scene.render.filepath = location[:-6] + '.png'
                        print('\tRender path: {}'.format(context.scene.render.filepath))
                        context.scene.update()
                        context.area.tag_redraw()

                        print('\nRendering...')
                        bpy.ops.render.render(write_still=True)

                        print('Cleaning up\n')
                        for scene in imported.scenes:
                            for object in scene.objects:
                                remove.object(object, data=True)

                            bpy.data.scenes.remove(scene, do_unlink=True)

                        for material in imported.materials:
                            bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                else:
                    context.screen.scene = init_scene

                    for scene in thumbnail.scenes:
                        for object in scene.objects:
                            remove.object(object, data=True)

                        bpy.data.scenes.remove(scene, do_unlink=True)

                    for material in thumbnail.materials:
                        bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                    init_scene.objects.active = init_active

                    for object in init_scene.objects:
                        object.select = True
                        object.hide = False

                    print('Finished\n')

        else:
            bpy.ops.render.render(write_still=True)

        return {'FINISHED'}

class AlignHorizontal(Operator):
    bl_idname = 'kitops.align_horizontal'
    bl_label = 'Align horizontal'
    bl_description = 'Align selected INSERTS horizontally within target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis = BoolProperty(
        name = 'Y Axis',
        description = 'Use the y axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        # get mains
        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                center = bbox.center(main.kitops.insert_target)
                setattr(main.location, 'y' if self.y_axis else 'x', getattr(center, 'y' if self.y_axis else 'x'))

        return {'FINISHED'}

class AlignVertical(Operator):
    bl_idname = 'kitops.align_vertical'
    bl_label = 'Align vertical'
    bl_description = 'Align selected INSERTS vertically within target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis = BoolProperty(
        name = 'Z Axis',
        description = 'Use the Z axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        # get mains
        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                center = bbox.center(main.kitops.insert_target)
                setattr(main.location, 'z' if self.z_axis else 'y', getattr(center, 'z' if self.z_axis else 'y'))

        return {'FINISHED'}

class AlignLeft(Operator):
    bl_idname = 'kitops.align_left'
    bl_label = 'Align left'
    bl_description = 'Align selected INSERTS to the left of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis = BoolProperty(
        name = 'Y Axis',
        description = 'Use the y axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                left = bbox.back(main.kitops.insert_target).y if self.y_axis else bbox.left(main.kitops.insert_target).x
                setattr(main.location, 'y' if self.y_axis else 'x', left)

        return {'FINISHED'}

class AlignRight(Operator):
    bl_idname = 'kitops.align_right'
    bl_label = 'Align right'
    bl_description = 'Align selected INSERTS to the right of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis = BoolProperty(
        name = 'Y Axis',
        description = 'Use the y axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                right = bbox.front(main.kitops.insert_target).y if self.y_axis else bbox.right(main.kitops.insert_target).x
                setattr(main.location, 'y' if self.y_axis else 'x', right)

        return {'FINISHED'}

class AlignTop(Operator):
    bl_idname = 'kitops.align_top'
    bl_label = 'Align top'
    bl_description = 'Align selected INSERTS to the top of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis = BoolProperty(
        name = 'Z Axis',
        description = 'Use the Z axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                top = bbox.top(main.kitops.insert_target).z if self.z_axis else bbox.back(main.kitops.insert_target).y
                setattr(main.location, 'z' if self.z_axis else 'y', top)

        return {'FINISHED'}

class AlignBottom(Operator):
    bl_idname = 'kitops.align_bottom'
    bl_label = 'Align bottom'
    bl_description = 'Align selected INSERTS to the bottom of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis = BoolProperty(
        name = 'Z Axis',
        description = 'Use the Z axis of the INSERT TARGET for alignment',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                bottom = bbox.bottom(main.kitops.insert_target).z if self.z_axis else bbox.front(main.kitops.insert_target).y
                setattr(main.location, 'z' if self.z_axis else 'y', bottom)

        return {'FINISHED'}

class StretchWide(Operator):
    bl_idname = 'kitops.stretch_wide'
    bl_label = 'Stretch wide'
    bl_description = 'Stretch selected INSERTS to the width of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis = BoolProperty(
        name = 'X axis',
        description = 'Use the Y axis of the INSERT TARGET for stretching',
        default = False)

    halve = BoolProperty(
        name = 'Halve',
        description = 'Halve the stretch amount',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                dimension = main.kitops.insert_target.dimensions[1 if self.y_axis else 0]

                if self.halve:
                    dimension /= 2

                main.dimensions[0] = dimension

        return {'FINISHED'}

class StretchTall(Operator):
    bl_idname = 'kitops.stretch_tall'
    bl_label = 'Stretch tall'
    bl_description = 'Stretch selected INSERTS to the height of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis = BoolProperty(
        name = 'Side',
        description = 'Use the Z axis of the INSERT TARGET for stretching',
        default = False)

    halve = BoolProperty(
        name = 'Halve',
        description = 'Halve the stretch amount',
        default = False)

    def execute(self, context):

        mains = insert.collect(context.selected_objects, mains=True)

        for main in mains:
            if main.kitops.insert_target:
                dimension = main.kitops.insert_target.dimensions[2 if self.z_axis else 1]

                if self.halve:
                    dimension /= 2

                main.dimensions[1] = dimension

        return {'FINISHED'}

class update:

    def main(prop, context):
        for object in bpy.data.objects:
            if object != context.active_object:
                object.kitops['main'] = False
            else:
                object.kitops['main'] = True

    def author(prop, context):
        for object in bpy.data.objects:
            object.kitops.author = context.active_object.kitops.author

    def type(prop, context):
        object = context.active_object

        for object in bpy.data.objects:

            if object.kitops.type == 'SOLID':
                object.draw_type = 'SOLID'

                object.hide_render = False

                object.cycles_visibility.camera = True
                object.cycles_visibility.diffuse = True
                object.cycles_visibility.glossy = True
                object.cycles_visibility.transmission = True
                object.cycles_visibility.scatter = True
                object.cycles_visibility.shadow = True

            elif object.kitops.type == 'WIRE' or object.kitops.type == 'CUTTER':

                object.draw_type = 'WIRE'

                object.hide_render = True

                object.cycles_visibility.camera = False
                object.cycles_visibility.diffuse = False
                object.cycles_visibility.glossy = False
                object.cycles_visibility.transmission = False
                object.cycles_visibility.scatter = False
                object.cycles_visibility.shadow = False

    def insert_target(prop, context):
        inserts = insert.collect(context.selected_objects)

        for object in inserts:
            object.kitops.applied = False
            object.kitops['insert_target'] = context.active_object.kitops.insert_target

            if object.kitops.insert_target:
                object.kitops.reserved_target = context.active_object.kitops.insert_target

    def mirror_x(prop, context):
        inserts = insert.collect(context.selected_objects)

        for object in inserts:
            object.kitops['mirror_x'] = bpy.context.active_object.kitops.mirror_x

        validate_mirror(inserts, axis='X')

    def mirror_y(prop, context):
        inserts = insert.collect(context.selected_objects)

        for object in inserts:
            object.kitops['mirror_y'] = bpy.context.active_object.kitops.mirror_y

        validate_mirror(inserts, axis='Y')

    def mirror_z(prop, context):
        inserts = insert.collect(context.selected_objects)

        for object in inserts:
            object.kitops['mirror_z'] = bpy.context.active_object.kitops.mirror_z

        validate_mirror(inserts, axis='Z')
