import os

import bpy

from bpy.types import Operator
from bpy.props import *
from bpy.utils import register_class, unregister_class

from . import addon, bbox, id, insert, remove


def authoring_save_pre():
    option = addon.option()

    if insert.authoring() and bpy.data.filepath != addon.path.thumbnail_scene():

        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.visible_objects:
            obj.kitops.inserted = False

        for obj in bpy.data.objects:
            obj.kitops.id = ''
            obj.kitops.author = option.author
            obj.kitops.insert = False
            obj.kitops.applied = False
            obj.kitops.animated = bpy.context.scene.kitops.animated

            if obj.data:
                obj.data.kitops.id = id.uuid()
                obj.data.kitops.insert = False

        main = [obj for obj in bpy.data.objects if obj.kitops.main][0]
        bpy.context.view_layer.objects.active = main
        main.select_set(True)

        if bpy.context.scene.kitops.auto_parent:
            # bpy.ops.object.visual_transform_apply()

            for obj in bpy.data.objects:
                obj.parent = None

            for obj in bpy.data.objects:
                obj.select_set(True)

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)


def authoring_load_post():
    option = addon.option()

    author = False
    for obj in bpy.data.objects:
        if obj.kitops.author:
            author = obj.kitops.author
            break

    if author:
        option.author = author

    else:
        option.author = addon.preference().author
        for obj in bpy.data.objects:
            obj.kitops.author = addon.preference().author

    main = False
    for obj in bpy.data.objects:
        if obj.kitops.main:
            main = True
            break

    if not main:
        if bpy.context.active_object:
            bpy.context.active_object.kitops.main = True
        elif len(bpy.data.objects):
            bpy.data.objects[0].kitops['main'] = True


#XXX: type and reference error
def toggles_depsgraph_update_post():
    option = addon.option()

    solid_inserts = insert.collect(solids=True, all=True)
    count = 0
    for obj in solid_inserts:
        try:
            if obj.hide_viewport:
                option['show_solid_objects'] = False
                break
            elif obj in bpy.context.view_layer.objects and not obj.select_get():
                count += 1
        except: pass

    if count > 2 and count == len(solid_inserts):
        option['show_solid_objects'] = True

    boolean_inserts = insert.collect(cutters=True, all=True)
    count = 0
    for obj in boolean_inserts:
        try:
            if obj.hide_viewport:
                option['show_cutter_objects'] = False
                break
            elif not obj.select_get():
                count += 1
        except RuntimeError: pass

    if count > 2 and count == len(boolean_inserts):
        option['show_cutter_objects'] = True

    wire_inserts = insert.collect(wires=True, all=True)
    count = 0
    for obj in wire_inserts:
        try:
            if obj.hide_viewport:
                option['show_wire_objects'] = False
                break
            elif not obj.select_get():
                count += 1
        except RuntimeError: pass

    if count > 2 and count == len(wire_inserts):
        option['show_wire_objects'] = True


def authoring_depsgraph_update_post():
    if len(bpy.data.objects) == 1:
        bpy.data.objects[0].kitops['main'] = True

    for obj in bpy.data.objects:
        if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE'}:
            obj.kitops.type = 'WIRE'
        if obj.type != 'MESH' and obj.kitops.type == 'CUTTER':
            obj.kitops.type = 'WIRE'
        if obj.kitops.main and obj.kitops.selection_ignore:
            obj.kitops.selection_ignore = False


def insert_depsgraph_update_pre():
    if addon.preference().mode == 'SMART':
        if not insert.operator:
            insert.show_solid_objects()
            insert.show_cutter_objects()
            insert.show_wire_objects()

        objs = [obj for obj in bpy.data.objects if not obj.kitops.insert and obj.type == 'MESH']
        inserts = [obj for obj in sorted(bpy.data.objects, key=lambda obj: obj.name) if obj.kitops.insert and not obj.kitops.applied]

        for obj in inserts:
            if obj.kitops.type == 'CUTTER' and obj.kitops.insert_target:
                available = False
                for modifier in obj.kitops.insert_target.modifiers:
                    if modifier.type == 'BOOLEAN' and modifier.object == obj:
                        available = True

                        break

                if not available:
                    #TODO: remove all bools for insert and reapply in order (maintain consistent order)
                    insert.add_boolean(obj)

            if obj.kitops.type == 'CUTTER':
                for target in objs:
                    for modifier in target.modifiers:
                        if modifier.type == 'BOOLEAN' and modifier.object == obj and target != obj.kitops.insert_target:

                            target.modifiers.remove(modifier)


def new_empty():
    empty = bpy.data.objects.new('KIT OPS Mirror Target', None)
    empty.location = bpy.context.active_object.kitops.insert_target.location
    empty.empty_display_size = 0.01

    bpy.data.collections['INSERTS'].objects.link(empty)

    return empty


def add_mirror(obj, axis='X'):
    obj.kitops.mirror = True
    mod = obj.modifiers.new(name='KIT OPS Mirror', type='MIRROR')

    if mod:
        mod.show_expanded = False
        mod.use_axis[0] = False

        index = {'X': 0, 'Y': 1, 'Z': 2} # patch inplace for api change
        mod.use_axis[index[axis]] = getattr(obj.kitops, F'mirror_{axis.lower()}')

        mod.mirror_object = obj.kitops.insert_target
        obj.kitops.mirror_target = obj.kitops.insert_target


def validate_mirror(inserts, axis='X'):
    for obj in inserts:
        if obj.kitops.mirror:

            available = False
            # assuming our mirror is most recent
            for modifier in reversed(obj.modifiers):

                if modifier.type == 'MIRROR' and modifier.mirror_object == obj.kitops.mirror_target:
                    available = True
                    index = {'X': 0, 'Y': 1, 'Z': 2} # patch inplace for api change
                    modifier.use_axis[index[axis]] = getattr(obj.kitops, F'mirror_{axis.lower()}')

                    if True not in modifier.use_axis[:]:
                        obj.kitops.mirror = False
                        obj.kitops.mirror_target = None
                        obj.modifiers.remove(modifier)

                    break

            if not available:
                add_mirror(obj, axis=axis)

        else:
            add_mirror(obj, axis=axis)


def apply_booleans(inserts):
    targets = []
    for obj in inserts:
        if obj.kitops.insert_target not in targets:
            targets.append(obj.kitops.insert_target)

    for target in targets:
        duplicate = target.copy()
        duplicate.data = target.data.copy()

        target_inserts = []
        for modifier in duplicate.modifiers:
            if modifier.type == 'BOOLEAN' and modifier.object in inserts:
                target_inserts.append(modifier.object)

        duplicate.modifiers.clear()

        for obj in target_inserts:
            obj.kitops['insert_target'] = duplicate

        bpy.context.scene.update()

        duplicate.data = duplicate.to_mesh(bpy.context.depsgraph, apply_modifiers=True)

        old_data = bpy.data.meshes[target.data.name]
        name = old_data.name

        target.data = duplicate.data
        target.data.name = name

        duplicate.data = old_data
        remove.object(duplicate, data=True)


def remove_booleans(inserts, targets=[], clear_target=False):
    for obj in inserts:
        if obj.kitops.insert_target and obj.kitops.insert_target not in targets:
            targets.append(obj.kitops.insert_target)

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
        for obj in inserts:
            obj.kitops['insert_target'] = None


def clear(inserts):
    for obj in inserts:
        obj.kitops.insert = False
        obj.kitops['insert_target'] = None


def delete(inserts):
    for obj in inserts:
        remove.object(obj, data=True)


class KO_OT_apply_insert(Operator):
    bl_idname = 'ko.apply_insert'
    bl_label = 'Apply'
    bl_description = 'Apply selected INSERTS\n  Shift - Apply modifiers\n'
    bl_options = {'UNDO'}

    def invoke(self, context, event):

        inserts = insert.collect(context.selected_objects)

        if event.shift:
            apply_booleans(inserts)

        clear(inserts)

        return {'FINISHED'}


class KO_OT_remove_insert(Operator):
    bl_idname = 'ko.remove_insert'
    bl_label = 'Delete'
    bl_description = 'Remove selected INSERTS\n  Shift - KITOPS properties only'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        inserts = insert.collect(context.selected_objects)

        if not event.shift:
            for obj in inserts:
                for o in bpy.data.objects:
                    for modifier in o.modifiers:
                        if modifier.type == 'BOOLEAN' and modifier.object == obj:
                            o.modifiers.remove(modifier)

            for obj in inserts:
                remove.object(obj, data=True)

        else:
            clear(inserts)

        return {'FINISHED'}


#TODO: render scene needs to be the kpack render scene if any
#TOOD: progress report update
class KO_OT_render_thumbnail(Operator):
    bl_idname = 'ko.render_thumbnail'
    bl_label = 'Render thumbnail'
    bl_description = 'Render and save a thumbnail for this INSERT.\n  Shift - Import thumbnail scene\n  Ctrl - Render all thumbnails for the current working directory\n  Alt - Prevent scale fitting\n\n  Use system console to see progress (Window > Toggle system console)'
    bl_options = {'INTERNAL'}

    render: BoolProperty(default=False)
    max_dimension = 1.8
    skip_scale = False

    def invoke(self, context, event):
        preference = addon.preference()
        init_active = bpy.data.objects[context.active_object.name]
        init_scene = bpy.data.scenes[context.scene.name]
        init_objects = bpy.data.objects[:]
        duplicates = []
        parents = []
        self.skip_scale = event.alt

        if not self.render:

            print('\nKIT OPS beginning thumbnail rendering')
            preference.mode = 'SMART'

            with bpy.data.libraries.load(addon.path.thumbnail_scene()) as (blend, imported):
                print('\tImported thumbnail rendering scene')
                imported.scenes = blend.scenes
                imported.materials = blend.materials

            scene = imported.scenes[0]
            scene.kitops.thumbnail_scene = True
            context.window.scene = scene

            for object in scene.collection.objects:
                object.select_set(False)

            floor = [object for object in context.scene.collection.objects if object.kitops.ground_box][0]

            for object in init_objects:
                duplicate = object.copy()
                duplicate.name = 'ko_duplicate_{}'.format(object.name)
                if duplicate.type != 'EMPTY':
                    duplicate.data = object.data.copy()

                duplicates.append(duplicate)
                parents.append((duplicate, object.parent))

                context.scene.collection.objects.link(duplicate)

                duplicate.kitops.insert = True
                duplicate.kitops.id = 'tmp'
                duplicate.kitops.applied = False
                duplicate.kitops['insert_target'] = floor

                duplicate.select_set(True)
                duplicate.hide_viewport = False

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

            main = [duplicate for duplicate in duplicates if duplicate.kitops.main][0]
            context.view_layer.objects.active = main
            bpy.ops.view3d.view_camera()
            dimension = main.dimensions

            if not self.skip_scale:
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

            if event.shift:
                bpy.ops.object.convert(target='MESH')

            else:
                print('\nRendering...')
                bpy.ops.render.render(write_still=True)

            if not event.shift and not event.ctrl:

                print('Cleaning up\n')
                for object in duplicates:
                    remove.object(object, data=True)

                context.window.scene = init_scene

                for scene in imported.scenes:
                    for object in scene.collection.objects:
                        remove.object(object, data=True)

                    bpy.data.scenes.remove(scene, do_unlink=True)

                for material in imported.materials:
                    bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                context.view_layer.objects.active = init_active

                for object in init_scene.collection.objects:
                    object.select_set(True)
                    object.hide_viewport = False

                print('Finished\n')

            if not event.shift and event.ctrl:

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

                        if not len(scene.collection.objects):
                            print('Invalid file... skipping\n')
                            continue

                        elif not len([object for object in scene.collection.objects if object.kitops.main]):
                            print('Invalid file... skipping\n')
                            continue

                        for object in scene.collection.objects:
                            context.scene.collection.objects.link(object)

                            object.kitops.insert = True
                            object.kitops.id = 'tmp'
                            object.kitops.applied = False
                            object.kitops['insert_target'] = floor

                            object.select_set(True)
                            object.hide_viewport = False

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

                        main = [object for object in context.scene.collection.objects if object.kitops.main][0]
                        dimension = main.dimensions

                        if not self.skip_scale:
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
                            for object in scene.collection.objects:
                                remove.object(object, data=True)

                            bpy.data.scenes.remove(scene, do_unlink=True)

                        for material in imported.materials:
                            bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                else:
                    context.window.scene = init_scene

                    for scene in imported.scenes:
                        for object in scene.collection.objects:
                            remove.object(object, data=True)

                        bpy.data.scenes.remove(scene, do_unlink=True)

                    for material in imported.materials:
                        bpy.data.materials.remove(material, do_unlink=True, do_id_user=True, do_ui_user=True)

                    context.view_layer.objects.active = init_active

                    for object in init_scene.collection.objects:
                        object.select_set(True)
                        object.hide_viewport = False

                    print('Finished\n')

        else:
            bpy.ops.render.render(write_still=True)

        return {'FINISHED'}



#XXX: align needs to check dimensions with current insert disabled
class KO_OT_align_horizontal(Operator):
    bl_idname = 'ko.align_horizontal'
    bl_label = 'Align horizontal'
    bl_description = 'Align selected INSERTS horizontally within target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis: BoolProperty(
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


class KO_OT_align_vertical(Operator):
    bl_idname = 'ko.align_vertical'
    bl_label = 'Align vertical'
    bl_description = 'Align selected INSERTS vertically within target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis: BoolProperty(
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


class KO_OT_align_left(Operator):
    bl_idname = 'ko.align_left'
    bl_label = 'Align left'
    bl_description = 'Align selected INSERTS to the left of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis: BoolProperty(
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


class KO_OT_align_right(Operator):
    bl_idname = 'ko.align_right'
    bl_label = 'Align right'
    bl_description = 'Align selected INSERTS to the right of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis: BoolProperty(
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


class KO_OT_align_top(Operator):
    bl_idname = 'ko.align_top'
    bl_label = 'Align top'
    bl_description = 'Align selected INSERTS to the top of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis: BoolProperty(
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


class KO_OT_align_bottom(Operator):
    bl_idname = 'ko.align_bottom'
    bl_label = 'Align bottom'
    bl_description = 'Align selected INSERTS to the bottom of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis: BoolProperty(
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


class KO_OT_stretch_wide(Operator):
    bl_idname = 'ko.stretch_wide'
    bl_label = 'Stretch wide'
    bl_description = 'Stretch selected INSERTS to the width of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    y_axis: BoolProperty(
        name = 'X axis',
        description = 'Use the Y axis of the INSERT TARGET for stretching',
        default = False)

    halve: BoolProperty(
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

                main.scale.x = dimension / main.dimensions[0] * main.scale.x

        return {'FINISHED'}


class KO_OT_stretch_tall(Operator):
    bl_idname = 'ko.stretch_tall'
    bl_label = 'Stretch tall'
    bl_description = 'Stretch selected INSERTS to the height of the target bounds'
    bl_options = {'REGISTER', 'UNDO'}

    z_axis: BoolProperty(
        name = 'Side',
        description = 'Use the Z axis of the INSERT TARGET for stretching',
        default = False)

    halve: BoolProperty(
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

                main.scale.y = dimension / main.dimensions[1] * main.scale.y

        return {'FINISHED'}


class update:

    def main(prop, context):
        for obj in bpy.data.objects:
            if obj != context.active_object:
                obj.kitops['main'] = False
            else:
                obj.kitops['main'] = True

    def author(prop, context):
        for obj in bpy.data.objects:
            obj.kitops.author = context.active_object.kitops.author

    def type(prop, context):
        obj = context.active_object

        for obj in bpy.data.objects:

            if obj.kitops.type == 'SOLID':
                obj.display_type = 'SOLID'

                obj.hide_render = False

                obj.cycles_visibility.camera = True
                obj.cycles_visibility.diffuse = True
                obj.cycles_visibility.glossy = True
                obj.cycles_visibility.transmission = True
                obj.cycles_visibility.scatter = True
                obj.cycles_visibility.shadow = True

            elif obj.kitops.type == 'WIRE' or obj.kitops.type == 'CUTTER':

                obj.display_type = 'WIRE'

                obj.hide_render = True

                obj.cycles_visibility.camera = False
                obj.cycles_visibility.diffuse = False
                obj.cycles_visibility.glossy = False
                obj.cycles_visibility.transmission = False
                obj.cycles_visibility.scatter = False
                obj.cycles_visibility.shadow = False

    def insert_target(prop, context):
        inserts = insert.collect(context.selected_objects)

        for obj in inserts:
            obj.kitops.applied = False
            obj.kitops['insert_target'] = context.active_object.kitops.insert_target

            if obj.kitops.insert_target:
                obj.kitops.reserved_target = context.active_object.kitops.insert_target

    def mirror_x(prop, context):
        inserts = insert.collect(context.selected_objects)

        for obj in inserts:
            obj.kitops['mirror_x'] = bpy.context.active_object.kitops.mirror_x

        validate_mirror(inserts, axis='X')

    def mirror_y(prop, context):
        inserts = insert.collect(context.selected_objects)

        for obj in inserts:
            obj.kitops['mirror_y'] = bpy.context.active_object.kitops.mirror_y

        validate_mirror(inserts, axis='Y')

    def mirror_z(prop, context):
        inserts = insert.collect(context.selected_objects)

        for obj in inserts:
            obj.kitops['mirror_z'] = bpy.context.active_object.kitops.mirror_z

        validate_mirror(inserts, axis='Z')


classes = [
    KO_OT_apply_insert,
    KO_OT_remove_insert,
    KO_OT_render_thumbnail,
    KO_OT_align_horizontal,
    KO_OT_align_vertical,
    KO_OT_align_left,
    KO_OT_align_right,
    KO_OT_align_top,
    KO_OT_align_bottom,
    KO_OT_stretch_wide,
    KO_OT_stretch_tall]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
