from copy import deepcopy as copy

import bpy

from mathutils import *

from bpy.types import Operator
from bpy.props import *

from . utility import addon, bbox, dpi, insert, ray, remove, update, view3d

smart_enabled = True
try: from . utility import smart
except: smart_enabled = False

class Purchase(Operator):
    bl_idname = 'kitops.purchase'
    bl_label = 'KIT OPS PRO'
    bl_description = 'Buy KIT OPS PRO'

    def execute(self, context):

        return {'FINISHED'}

class visit(Operator):
    bl_idname = 'kitops.visit'
    bl_label = 'Visit the KIT OPS website'
    bl_description = 'Visit the KIT OPS website'

    def execute(self, context):
        bpy.ops.wm.url_open('INVOKE_DEFAULT', url='https://www.kit-ops.com/')

        return {'FINISHED'}

class Documentation(Operator):
    bl_idname = 'kitops.documentation'
    bl_label = 'Documentation'
    bl_description = 'View the KIT OPS documentation'

    authoring = BoolProperty(default=False)

    def execute(self, context):
        bpy.ops.wm.url_open('INVOKE_DEFAULT', url='https://docs.google.com/document/d/1vFtPnfFbV6Dyu8P9pbD3deK4afoibPi0axBD2deOWvQ/edit?usp=sharing' if self.authoring else 'https://docs.google.com/document/d/1rjyJ-AbKuPRL-J9-48l5KPNHBkDcFE4UQ51Jsm5eqiM/edit?usp=sharing')

        return {'FINISHED'}

class AddKPackPath(Operator):
    bl_idname = 'kitops.add_kpack_path'
    bl_label = 'Add KIT OPS KPACK path'
    bl_description = 'Add a path to a KIT OPS KPACK'

    def execute(self, context):
        preference = addon.preference()

        folder = preference.folders.add()
        folder['location'] = 'Choose Path'

        return {'FINISHED'}

class RemoveKPackPath(Operator):
    bl_idname = 'kitops.remove_kpack_path'
    bl_label = 'Remove path'
    bl_description = 'Remove path'

    index = IntProperty()

    def execute(self, context):
        preference = addon.preference()

        preference.folders.remove(self.index)

        update.kpack(None, context)

        return {'FINISHED'}

class RefreshKPacks(Operator):
    bl_idname = 'kitops.refresh_kpacks'
    bl_label = 'Refresh KIT OPS KPACKS'
    bl_description = 'Refresh KIT OPS KPACKS'

    def execute(self, context):
        update.kpack(None, context)
        return {'FINISHED'}

class AddInsert(Operator):
    bl_idname = 'kitops.add_insert'
    bl_label = 'Add INSERT'
    bl_description = 'Add INSERT to the scene'
    bl_options = {'REGISTER', 'UNDO'}

    location = StringProperty(
        name = 'Blend path',
        description = 'Path to blend file')

    mouse = Vector()
    main = None
    duplicate = None

    data_to = None
    boolean_target = None

    inserts = list()

    init_active = None
    init_selected = list()
    init_show_manipulator = bool()

    insert_scale = ('LARGE', 'MEDIUM', 'SMALL')

    @classmethod
    def poll(cls, context):
        return not context.space_data.region_quadviews and not context.space_data.local_view

    def invoke(self, context, event):
        global smart_enabled

        preference = addon.preference()
        option = addon.option()

        insert.operator = self

        self.init_active = bpy.data.objects[context.active_object.name] if context.active_object and context.active_object.select else None
        self.init_selected = [bpy.data.objects[object.name] for object in context.selected_objects]

        self.init_show_manipulator = copy(context.space_data.show_manipulator)
        context.space_data.show_manipulator = False

        for object in bpy.data.objects:
            for modifier in object.modifiers:
                if modifier.type == 'BOOLEAN' and not modifier.object:
                    object.modifiers.remove(modifier)

        if self.init_active:
            if self.init_active.kitops.insert and self.init_active.kitops.insert_target:
                self.boolean_target = self.init_active.kitops.insert_target
            elif preference.mode == 'REGULAR' and self.init_active.kitops.reserved_target:
                self.boolean_target = self.init_active.kitops.reserved_target
            elif self.init_active.kitops.insert:
                self.boolean_target = None
            elif self.init_active.type == 'MESH':
                self.boolean_target = self.init_active
            else:
                self.boolean_target = None
        else:
            self.boolean_target = None

        for object in context.selected_objects:
            object.select = False

        insert.show_solid_objects()
        insert.show_cutter_objects()
        insert.show_wire_objects()

        if self.init_active and self.init_active.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if self.boolean_target:
            ray.make_duplicate(self, self.boolean_target)

        insert.add(self, context)

        if self.main.kitops.animated:
            bpy.ops.screen.animation_play()

        if self.init_selected and self.boolean_target:
            self.mouse = Vector((event.mouse_x, event.mouse_y))
            self.mouse.x -= view3d.region().x - preference.insert_offset_x * dpi.factor()
            self.mouse.y -= view3d.region().y - preference.insert_offset_y * dpi.factor()

            insert.hide_handler(self)

            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}
        else:
            self.main.location = bpy.context.space_data.cursor_location
            self.exit(context)
            return {'FINISHED'}

    def modal(self, context, event):
        preference = addon.preference()
        option = addon.option()

        if not insert.operator:
            self.exit(context)
            return {'FINISHED'}

        if event.type == 'MOUSEMOVE':
            self.mouse = Vector((event.mouse_x, event.mouse_y))
            self.mouse.x -= view3d.region().x - preference.insert_offset_x * dpi.factor()
            self.mouse.y -= view3d.region().y - preference.insert_offset_y * dpi.factor()
            update.location()

        insert.hide_handler(self)

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':

            self.exit(context, clear=True)
            return {'CANCELLED'}

        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if ray.success:
                if event.shift and preference.mode == 'SMART':
                    self.exit(context)
                    bpy.ops.kitops.add_insert('INVOKE_DEFAULT', location=self.location)
                else:
                    self.exit(context)
                return{'FINISHED'}
            else:

                self.exit(context, clear=True)
                return {'CANCELLED'}

        elif event.type == 'WHEELDOWNMOUSE':
            if option.auto_scale:
                if self.insert_scale.index(preference.insert_scale) + 1 < len(self.insert_scale):
                    preference.insert_scale = self.insert_scale[self.insert_scale.index(preference.insert_scale) + 1]
            else:
                step = 0.1 if not event.shift else 0.01
                self.main.scale -= self.main.scale * step
            return {'RUNNING_MODAL'}

        elif event.type == 'WHEELUPMOUSE':
            if option.auto_scale:
                if self.insert_scale.index(preference.insert_scale) - 1 >= 0:
                    preference.insert_scale = self.insert_scale[self.insert_scale.index(preference.insert_scale) - 1]
            else:
                step = 0.1 if not event.shift else 0.01
                self.main.scale += self.main.scale * step
            return {'RUNNING_MODAL'}

        elif event.type in {'G', 'R', 'S'}:
            insert.operator = None

        if option.auto_scale:
            update.insert_scale(None, context)

        return {'PASS_THROUGH'}

    def exit(self, context, clear=False):
        preference = addon.preference()
        option = addon.option()
        tool_settings = context.scene.tool_settings

        context.space_data.show_manipulator = self.init_show_manipulator

        if self.main.kitops.animated:
            bpy.ops.screen.animation_cancel(restore_frame=True)

        if not option.show_cutter_objects:
            for object in self.cutter_objects:
                object.hide = True

        if clear:
            for object in self.inserts:
                remove.object(object, data=True)

            for object in self.init_selected:
                object.select = True

            if self.init_active:
                context.scene.objects.active = self.init_active

        else:
            for object in self.inserts:
                if object.select and object.kitops.selection_ignore:
                    object.select = False

        ray.success = bool()
        ray.location = Vector()
        ray.normal = Vector()
        ray.face_index = int()

        insert.operator = None

class SelectInserts(Operator):
    bl_idname = 'kitops.select_inserts'
    bl_label = 'Select All'
    bl_description = 'Select all INSERTS'
    bl_options = {'REGISTER', 'UNDO'}

    solids = BoolProperty(
        name = 'Solid inserts',
        description = 'Select solid INSERTS',
        default = True)

    cutters = BoolProperty(
        name = 'Cutter inserts',
        description = 'Select cutter INSERTS',
        default = True)

    wires = BoolProperty(
        name = 'Wire inserts',
        description = 'Select wire INSERTS',
        default = True)

    def draw(self, context):
        layout = self.layout

        preference = addon.preference()
        option = addon.option()

        if preference.mode == 'SMART':
            layout.prop(option, 'auto_select')

        column = layout.column()
        column.active = not option.auto_select or preference.mode == 'REGULAR'
        column.prop(self, 'solids')
        column.prop(self, 'cutters')
        column.prop(self, 'wires')

    def check(self, context):
        return True

    def execute(self, context):
        solids = insert.collect(solids=True, all=True)
        cutters = insert.collect(cutters=True, all=True)
        wires = insert.collect(wires=True, all=True)

        if self.solids:
            for object in solids:
                object.select = True

        if self.cutters:
            for object in cutters:
                object.select = True

        if self.wires:
            for object in wires:
                object.select = True

        return {'FINISHED'}
