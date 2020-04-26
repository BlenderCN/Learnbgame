import bpy

from bpy.types import Panel, UIList
from bpy.utils import register_class, unregister_class

from .. utility import addon, dpi, insert, update

smart_enabled = True
try: from .. utility import smart
except: smart_enabled = False


# TODO: on no categories show add path preferences
# TODO: should display options for the render scene, ground box toggle
class KO_PT_ui(Panel):
    bl_space_type = 'VIEW_3D'
    bl_label = 'KIT OPS'
    bl_region_type = 'UI'
    bl_category = 'KIT OPS'

    def draw(self, context):
        global smart_enabled

        layout = self.layout
        preference = addon.preference()
        option = addon.option()
        scene = context.scene

        if not smart_enabled and preference.mode == 'SMART':
            preference.mode = 'REGULAR'

        if insert.authoring():
            if not smart_enabled:
                layout.label(icon='ERROR', text='Purchase KIT OPS PRO')
                layout.label(icon='BLANK1', text='To use these features')

            column = layout.column()
            column.enabled = smart_enabled
            column.label(text='Author')
            column.prop(option, 'author', text='')

        if not insert.authoring():

            if len(option.kpack.categories):
                if not context.scene.kitops.thumbnail_scene:
                    category = option.kpack.categories[option.kpack.active_index]

                    layout.label(text='KPACKS')

                    column = layout.column(align=True)
                    row = column.row(align=True)
                    row.prop(option, 'filter', text='', icon='VIEWZOOM')
                    column.separator()

                    row = column.row(align=True)
                    row.prop(option, 'kpacks', text='')
                    row.operator('ko.refresh_kpacks', text='', icon='FILE_REFRESH')

                    row = column.row(align=True)

                    sub = row.row(align=True)
                    sub.scale_y = 6
                    sub.operator('ko.previous_kpack', text='', icon='TRIA_LEFT')

                    row.template_icon_view(category, 'thumbnail', show_labels=preference.thumbnail_labels)

                    sub = row.row(align=True)
                    sub.scale_y = 6
                    sub.operator('ko.next_kpack', text='', icon='TRIA_RIGHT')

                    row = column.row(align=True)
                    row.scale_y = 1.5
                    op = row.operator('ko.add_insert')
                    op.location = category.blends[category.active_index].location

                    row = layout.row()
                    row.label(text='INSERT Name: {}'.format(category.blends[category.active_index].name))

                    if smart_enabled:
                        split = layout.split(factor=0.3)
                        split.label(text='Mode')
                        row = split.row()
                        row.prop(preference, 'mode', expand=True)

                    column = layout.column(align=True)
                    column.enabled = option.auto_scale
                    row = column.row(align=True)
                    row.prop(preference, 'insert_scale', expand=True)
                    column.prop(preference, '{}_scale'.format(preference.insert_scale.lower()), text='Scale')
                    layout.separator()

                    layout.prop(option, 'auto_scale')

                column = layout.column()
                column.active = preference.mode == 'SMART' or preference.enable_auto_select
                column.prop(option, 'auto_select')
                layout.label(text='Display')

                row = layout.row()
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.prop(option, 'show_modifiers', text='', icon_value=addon.icons['main']['modifier' if option.show_modifiers else 'modifier-off'].icon_id, toggle=True)
                row.prop(option, 'show_solid_objects', text='', icon_value=addon.icons['main']['solid' if option.show_solid_objects else 'solid-off'].icon_id, toggle=True)
                row.prop(option, 'show_cutter_objects', text='', icon_value=addon.icons['main']['cutter'if option.show_cutter_objects else 'cutter-off'].icon_id, toggle=True)
                row.prop(option, 'show_wire_objects', text='', icon_value=addon.icons['main']['wire' if option.show_wire_objects else 'wire-off'].icon_id, toggle=True)

                if not context.scene.kitops.thumbnail_scene:

                    if context.active_object and context.active_object.kitops.insert:
                        layout.label(text='INSERT Name: {}'.format(context.active_object.kitops.label))

                        if preference.mode == 'SMART':
                            if context.active_object.kitops.insert_target and preference.mode == 'SMART':
                                row = layout.row()
                                row.enabled = smart_enabled
                                row.label(text='Mirror')

                                sub = row.row(align=True)
                                sub.alignment = 'RIGHT'
                                sub.scale_x = 0.75
                                sub.prop(context.active_object.kitops, 'mirror_x', text='X', toggle=True)
                                sub.prop(context.active_object.kitops, 'mirror_y', text='Y', toggle=True)
                                sub.prop(context.active_object.kitops, 'mirror_z', text='Z', toggle=True)

                            row = layout.row(align=True)
                            row.enabled = smart_enabled
                            if context.active_object.kitops.insert_target:
                                row.prop(context.active_object.kitops.insert_target, 'hide_select', text='', icon='RESTRICT_SELECT_OFF' if not context.active_object.hide_select else 'RESTRICT_SELECT_ON')
                            row.prop(context.active_object.kitops, 'insert_target', text='')

                            row = layout.row()
                            row.active = smart_enabled
                            sub = row.row()
                            sub.enabled = bool(context.active_object.kitops.insert_target)
                            sub.operator('ko.apply_insert' if smart_enabled else 'ko.purchase', text='Apply')
                            row.operator('ko.remove_insert' if smart_enabled else 'ko.purchase', text='Delete')

                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator('ko.select_inserts')

                else:
                    row = layout.row()
                    row.enabled = smart_enabled
                    row.scale_y = 1.5
                    op = row.operator('ko.render_thumbnail' if smart_enabled else 'ko.purchase', text='Render thumbnail')
                    if smart_enabled:
                        op.render = True

        elif context.active_object and not scene.kitops.thumbnail_scene:
            if context.active_object.type not in {'LAMP', 'CAMERA', 'SPEAKER', 'EMPTY'}:
                row = layout.row()
                row.enabled = smart_enabled
                row.prop(context.active_object.kitops, 'main')

            row = layout.row()
            row.enabled = smart_enabled
            row.prop(context.active_object.kitops, 'type', expand=True)

            if context.active_object.type == 'MESH' and context.active_object.kitops.type == 'CUTTER':
                row = layout.row()
                row.enabled = smart_enabled
                row.prop(context.active_object.kitops, 'boolean_type', text='Type')

            row = layout.row()
            row.enabled = smart_enabled and not context.active_object.kitops.main
            row.prop(context.active_object.kitops, 'selection_ignore')

        elif context.active_object and context.active_object.type == 'MESH' and scene.kitops.thumbnail_scene:
            row = layout.row()
            row.enabled = smart_enabled
            row.prop(context.active_object.kitops, 'ground_box')

        if insert.authoring():
            if not context.scene.kitops.thumbnail_scene:
                layout.separator()

                column = layout.column()
                column.enabled = smart_enabled
                column.prop(scene.kitops, 'animated')
                column.prop(scene.kitops, 'auto_parent')

            layout.separator()

            row = layout.row()
            row.active = smart_enabled
            row.scale_y = 1.5
            row.operator('ko.render_thumbnail' if smart_enabled else 'ko.purchase', text='Render thumbnail')

            layout.separator()

            row = layout.row()
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.operator('ko.visit', text='', icon_value=addon.icons['main']['pro' if smart_enabled else 'free'].icon_id)
            op = row.operator('ko.documentation', text='', icon_value=addon.icons['main']['question-sign'].icon_id)
            op.authoring = True

        elif not context.scene.kitops.thumbnail_scene:
            if preference.mode == 'SMART' and context.active_object and context.active_object.kitops.insert_target:
                layout.label(text='Align')

                row = layout.row()
                row.active = smart_enabled
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator('ko.align_top' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-top'].icon_id)
                row.operator('ko.align_bottom' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-bottom'].icon_id)
                row.operator('ko.align_left' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-left'].icon_id)
                row.operator('ko.align_right' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-right'].icon_id)

                row = layout.row()
                row.active = smart_enabled
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator('ko.align_horizontal' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-horiz'].icon_id)
                row.operator('ko.align_vertical' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['align-vert'].icon_id)
                row.operator('ko.stretch_wide' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['stretch-wide'].icon_id)
                row.operator('ko.stretch_tall' if smart_enabled else 'ko.purchase', text='', icon_value=addon.icons['main']['stretch-tall'].icon_id)

            layout.separator()

            row = layout.row()
            row.enabled = True
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.operator('ko.visit', text='', icon_value=addon.icons['main']['pro' if smart_enabled else 'free'].icon_id)
            op = row.operator('ko.documentation', text='', icon_value=addon.icons['main']['question-sign'].icon_id)
            op.authoring = False

classes = [
    KO_PT_ui]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
