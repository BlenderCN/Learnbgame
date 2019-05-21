import bpy

from bpy.types import Panel, UIList

from . utility import addon, dpi, insert

smart_enabled = True
try: from . utility import smart
except: smart_enabled = False

class Tools(Panel):
    bl_idname = 'kitops.tools'
    bl_space_type = 'VIEW_3D'
    bl_label = 'KIT OPS'
    bl_region_type = 'TOOLS'
    bl_category = 'KIT OPS' # 'Tools'

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
                    layout.label(text='KPACKS')
                    layout.template_list('kitops.list', 'kitops.kpack', option.kpack, 'categories', option.kpack, 'active_index', rows=2)
                    layout.separator()

                    catagory = option.kpack.categories[option.kpack.active_index]
                    layout.template_list('kitops.list', 'kitops.library', catagory, 'blends', catagory, 'active_index', rows=2)

                    row = layout.row()
                    row.label(text='INSERT Name: {}'.format(catagory.blends[catagory.active_index].name))

                    if smart_enabled:
                        split = layout.split(percentage=0.3)
                        split.label(text='Mode:')
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
                layout.label('Display:')

                row = layout.row()
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.prop(option, 'show_modifiers', text='', icon_value=addon.icons['main']['modifier' if option.show_modifiers else 'modifier-off'].icon_id, toggle=True)
                row.prop(option, 'show_solid_objects', text='', icon_value=addon.icons['main']['solid' if option.show_solid_objects else 'solid-off'].icon_id, toggle=True)
                row.prop(option, 'show_cutter_objects', text='', icon_value=addon.icons['main']['cutter'if option.show_cutter_objects else 'cutter-off'].icon_id, toggle=True)
                row.prop(option, 'show_wire_objects', text='', icon_value=addon.icons['main']['wire' if option.show_wire_objects else 'wire-off'].icon_id, toggle=True)

                if not context.scene.kitops.thumbnail_scene:

                    layout.separator()

                    row = layout.row(align=True)
                    row.scale_y = 1.5
                    op = row.operator('kitops.add_insert', icon='BLANK1')
                    op.location = catagory.blends[catagory.active_index].location

                    if context.active_object and context.active_object.kitops.insert:
                        layout.label(text='INSERT Name: {}'.format(context.active_object.kitops.label))

                        if preference.mode == 'SMART':
                            if context.active_object.kitops.insert_target and preference.mode == 'SMART':
                                split = layout.split(percentage=0.3)
                                split.enabled = smart_enabled
                                split.label(text='Mirror:')
                                split.prop(context.active_object.kitops, 'mirror_x')
                                split.prop(context.active_object.kitops, 'mirror_y')
                                split.prop(context.active_object.kitops, 'mirror_z')

                            row = layout.row(align=True)
                            row.enabled = smart_enabled
                            row.prop(context.active_object.kitops, 'insert_target', text='')
                            if context.active_object.kitops.insert_target:
                                row.prop(context.active_object.kitops.insert_target, 'hide_select', text='', icon='RESTRICT_SELECT_OFF' if not context.active_object.hide_select else 'RESTRICT_SELECT_ON')

                            row = layout.row()
                            row.active = smart_enabled
                            sub = row.row()
                            sub.enabled = bool(context.active_object.kitops.insert_target)
                            sub.operator('kitops.apply_insert' if smart_enabled else 'kitops.purchase', text='{}{}'.format(' '*(3*int(dpi.factor())), 'Apply'))
                            row.operator('kitops.remove_insert' if smart_enabled else 'kitops.purchase', text='{}{}'.format(' '*(3*int(dpi.factor())), 'Delete'))

                    row = layout.row()
                    row.scale_y = 1.5
                    row.operator('kitops.select_inserts', icon='BLANK1')

                else:
                    row = layout.row()
                    row.enabled = smart_enabled
                    row.scale_y = 1.5
                    op = row.operator('kitops.render_thumbnail' if smart_enabled else 'kitops.purchase', text='Render thumbnail', icon='BLANK1' )
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
            row.operator('kitops.render_thumbnail' if smart_enabled else 'kitops.purchase', text='Render thumbnail', icon='BLANK1' )

            layout.separator()

            row = layout.row()
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.operator('kitops.visit', text='', icon_value=addon.icons['main']['pro' if smart_enabled else 'free'].icon_id)
            op = row.operator('kitops.documentation', text='', icon_value=addon.icons['main']['question-sign'].icon_id)
            op.authoring = True

        elif not context.scene.kitops.thumbnail_scene:
            if preference.mode == 'SMART' and context.active_object and context.active_object.kitops.insert_target:
                layout.label(text='Align')

                row = layout.row()
                row.active = smart_enabled
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator('kitops.align_top' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-top'].icon_id)
                row.operator('kitops.align_bottom' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-bottom'].icon_id)
                row.operator('kitops.align_left' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-left'].icon_id)
                row.operator('kitops.align_right' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-right'].icon_id)

                row = layout.row()
                row.active = smart_enabled
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator('kitops.align_horizontal' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-horiz'].icon_id)
                row.operator('kitops.align_vertical' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['align-vert'].icon_id)
                row.operator('kitops.stretch_wide' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['stretch-wide'].icon_id)
                row.operator('kitops.stretch_tall' if smart_enabled else 'kitops.purchase', text='', icon_value=addon.icons['main']['stretch-tall'].icon_id)

            layout.separator()

            row = layout.row()
            row.enabled = True
            row.alignment = 'RIGHT'
            row.scale_x = 1.5
            row.scale_y = 1.5
            row.operator('kitops.visit', text='', icon_value=addon.icons['main']['pro' if smart_enabled else 'free'].icon_id)
            op = row.operator('kitops.documentation', text='', icon_value=addon.icons['main']['question-sign'].icon_id)
            op.authoring = False

class List(UIList):
    bl_idname = 'kitops.list'

    def draw_item(self, context, layout, data, item, icon, active_data, active_prop):
        preference = addon.preference()

        if item.icon == 'FILE_FOLDER':
            if preference.popup_location == 'LEFT':
                row = layout.row(align=True)

                sub = row.row(align=True)
                sub.scale_x = 0.16
                sub.scale_y = 0.16
                sub.template_icon_view(item, 'thumbnail', show_labels=preference.thumbnail_labels)

                row.scale_y = 1.1
                row.prop(item, 'name', text='', emboss=False)
            else:
                row = layout.row()

                row.scale_y = 1.1
                row.prop(item, 'name', text='', emboss=False, icon=item.icon)

                sub = row.row()
                sub.scale_x = 0.16
                sub.scale_y = 0.16
                sub.template_icon_view(item, 'thumbnail', show_labels=preference.thumbnail_labels)
        else:

            row = layout.row()
            if preference.thumbnails_in_list:
                row.prop(item, 'name', text='', emboss=False, icon_value=item.icon_id)
            else:
                row.prop(item, 'name', text='', emboss=False, icon=item.icon)
