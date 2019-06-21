import bpy
from math import radians
from .. preferences import get_preferences
from .. utils.blender_ui import get_dpi_factor

presets = {
    "Width": [0.01, 0.02, 0.1],
    "Segments": [1, 3, 4, 6, 12],
    "Profile": [0.3, 0.5, 0.7],
    "Angle": [30, 45, 60]}


class HOPS_OT_bevel_helper(bpy.types.Operator):
    bl_idname = 'hops.bevel_helper'
    bl_description = 'Display HOps Bevel Helper'
    bl_label = 'HOps Bevel Helper'

    mods: list = []
    label: bool = False

    @classmethod
    def poll(cls, context):
        active = context.active_object
        bevel = False

        if not active:
            return False

        for mod in reversed(active.modifiers[:]):
            if mod.type == 'BEVEL':
                bevel = True

                break

        return bevel


    def check(self, context):
        return True


    def invoke(self, context, event):
        preference = get_preferences()
        self.mods = []

        for mod in context.active_object.modifiers:
            if mod.type == 'BEVEL':
                mod.show_expanded = False
                self.mods.append(mod)

        if preference.use_bevel_helper_popup:
            self.label = True
            return context.window_manager.invoke_popup(self, width=240 * get_dpi_factor(force=False))
        else:
            return context.window_manager.invoke_props_dialog(self, width=240 * get_dpi_factor(force=False))


    def execute(self, context):
        return {'FINISHED'}


    def draw(self, context):
        if self.label:
            self.layout.label(text='HOps Bevel Helper')

        for index, mod in enumerate(self.mods):
            self.draw_bevel(context, mod, index=index)


    def draw_bevel(self, context, mod, index=0):
        preference = get_preferences()
        layout = self.layout

        split = layout.split(factor=0.5)

        row = split.row()
        row.alignment = 'LEFT'
        row.prop(mod, 'show_expanded', text='', emboss=False)
        row.prop(mod, 'name', text='', icon='MOD_BEVEL', emboss=False)

        row = split.row(align=True)
        row.alignment = 'RIGHT'
        if index == 0:
            row.prop(preference, 'show_presets', text='', icon=F'RESTRICT_SELECT_O{"FF" if preference.show_presets else "N"}', emboss=False)
        row.prop(mod, 'show_viewport', text='', emboss=False)

        split = layout.split(factor=0.1)
        column = split.column()
        column.separator()

        column = split.column(align=True)

        if mod.show_expanded:
            self.expanded(context, column, mod)

        else:
            self.label_row(context, column, mod, 'width', label='Width')
            self.label_row(context, column, mod, 'segments', label='Segments')


    def expanded(self, context, layout, mod):
        self.label_row(context, layout, mod, 'width', label='Width')
        self.label_row(context, layout, mod, 'segments', label='Segments')

        self.label_row(context, layout, mod, 'profile', label='Profile')

        layout.separator()

        self.label_row(context, layout, mod, 'limit_method', label='Method')

        if mod.limit_method == 'ANGLE':
            self.label_row(context, layout, mod, 'angle_limit', label='Angle')
            layout.separator()

        elif mod.limit_method == 'VGROUP':
            self.label_row(context, layout, mod, 'vertex_group', label='Vertex Group')
            layout.separator()

        self.label_row(context, layout, mod, 'offset_type', label='Width Method')

        layout.separator()

        self.label_row(context, layout, mod, 'miter_outer', label='Outer')
        self.label_row(context, layout, mod, 'miter_inner', label='Inner')
        self.label_row(context, layout, mod, 'spread', label='Spread')

        layout.separator()

        self.label_row(context, layout, mod, 'use_clamp_overlap', label='Clamp Overlap')

        layout.separator()


    def label_row(self, context, layout, path, prop, label='Label'):
        preference = get_preferences()
        column = layout.column(align=True)
        split = column.split(factor=0.5, align=True)

        split.label(text=label)

        row = split.row(align=True)
        if label == 'Width':
            width = context.active_object.modifiers[path.name].width

            sub = row.row(align=True)
            sub.scale_x = 0.3

            ot = sub.operator('wm.context_set_float', text='/')
            ot.data_path = F'active_object.modifiers["{path.name}"].width'
            ot.value = width / 2

            row.prop(path, prop, text='')

            sub = row.row(align=True)
            sub.scale_x = 0.3
            ot = sub.operator('wm.context_set_float', text='*')
            ot.data_path = F'active_object.modifiers["{path.name}"].width'
            ot.value = width * 2
        else:
            row.prop(path, prop, text='')


        if label in {'Width', 'Segments', 'Profile', 'Angle'} and preference.show_presets:
            split = column.split(factor=0.5, align=True)
            split.separator()
            row = split.row(align=True)

            for preset in presets[label]:
                ot = row.operator(
                    F'wm.context_set_{"int" if label not in {"Width", "Profile"} else "float"}', text=str(preset))
                ot.data_path = F'active_object.modifiers["{path.name}"].{prop}'
                ot.value = preset if label != 'ANGLE' else radians(preset)

            if label not in  {'Profile', 'Angle'}:
                column.separator()
