import os

import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty, IntProperty
from .config import defaults as default


class selected_bounds(AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    enabled_default = BoolProperty(
        name = 'Enabled By Default',
        description = 'Enable the bound indicators at start up. (Requires Save)',
        default = default['selected_bounds']
    )

    mode = EnumProperty(
        name = 'Display Mode',
        description = 'What objects to display bound indicators around.',
        items = [
            ('SELECTED', 'Selected Objects', 'The selected objects.'),
            ('ACTIVE', 'Active Object', 'The active object.'),
        ],
        default = default['mode']
    )

    color = FloatVectorProperty(
        name = 'Color',
        description = 'Color of the bound indicators.',
        subtype = 'COLOR',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = default['color']
    )

    use_object_color = BoolProperty(
        name = 'Use Object Color',
        description = 'Use the object\'s color.',
        default = default['use_object_color']
    )

    width = IntProperty(
        name = 'Pixel Width',
        description = 'Width of the bound indicator lines in pixels.',
        min = 1,
        max = 8,
        subtype = 'PIXEL',
        default = default['width']
    )

    length = IntProperty(
        name = 'Length',
        description = 'Length of the bound indicator lines as they extend toward the corners. (50% makes a complete box)',
        min = 1,
        soft_min = 10,
        max = 50,
        subtype = 'PERCENTAGE',
        default = default['length']
    )

    scene_independent = BoolProperty(
        name = 'Independent Scene Options',
        description = 'Use independent scene options in the viewport rather then using these preferences directly, you can find those options in: 3D View \N{Rightwards Arrow} Properties Shelf \N{Rightwards Arrow} Display',
        default = default['scene_independent']
    )

    display_preferences = BoolProperty(
        name = 'Display Preferences',
        description = 'Display these preferences in: 3D View \N{Rightwards Arrow} Properties Shelf \N{Rightwards Arrow} Display',
        default = default['display_preferences']
    )

    mode_only = BoolProperty(
        name = 'Mode Only',
        description = 'Only display the mode menu.',
        default = default['mode_only']
    )


    def draw(self, context):

        layout = self.layout

        column = layout.column()

        if not context.window_manager.is_selected_bounds_drawn:

            column.scale_y = 2

            column.operator('view3d.selected_bounds')

        else:

            column.prop(self, 'enabled_default')

            column.separator()

            row = column.row(align=True)

            row.prop(self, 'mode')

            sub = row.row(align=True)
            sub.scale_x = 0.5
            sub.prop(self, 'color', text='')

            subsub = sub.row(align=True)
            subsub.scale_x = 2
            subsub.prop(self, 'use_object_color', text='', icon='OBJECT_DATA')

            row = column.row()

            row.prop(self, 'width')
            row.prop(self, 'length', slider=True)

            column.separator()

            row = column.row()
            split = row.split()
            split.prop(self, 'scene_independent')

            sub = split.row()
            sub.enabled = not self.scene_independent
            sub.prop(self, 'display_preferences')

            subsub = sub.row()
            subsub.enabled = self.display_preferences
            subsub.prop(self, 'mode_only')

            column.separator()

            row = column.row()
            row.alignment = 'RIGHT'
            row.scale_y = 1.5

            row.operator('wm.update_selected_bound_settings')
            row.operator('wm.save_selected_bound_defaults')


class update(Operator):
    bl_idname = 'wm.update_selected_bound_settings'
    bl_label = 'Update'
    bl_description = 'Update the scenes with the current preference values.'
    bl_options = {'INTERNAL'}


    @classmethod
    def poll(operator, context):

        return context.user_preferences.addons[__name__.partition('.')[0]].preferences.scene_independent


    def execute(self, context):

        preference = context.user_preferences.addons[__name__.partition('.')[0]].preferences

        for scene in bpy.data.scenes:

            option = scene.selected_bounds

            option.mode = preference.mode
            option.color = preference.color
            option.use_object_color = preference.use_object_color
            option.width = preference.width
            option.length = preference.length

        return {'FINISHED'}


class save(Operator):
    bl_idname = 'wm.save_selected_bound_defaults'
    bl_label = 'Save'
    bl_description = 'Permanently store these settings in a config file located in the addon directory, this will make the values the new defaults for this addon.'
    bl_options = {'INTERNAL'}


    def execute(self, context):

        preference = context.user_preferences.addons[__name__.partition('.')[0]].preferences

        defaults = {
            'selected_bounds': preference.enabled_default,
            'mode': preference.mode,
            'color': preference.color[:],
            'use_object_color': preference.use_object_color,
            'width': preference.width,
            'length': preference.length,
            'scene_independent': preference.scene_independent,
            'display_preferences': preference.display_preferences,
            'mode_only': preference.mode_only,
        }

        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.py'))

        with open(filepath, '+r') as config:
            config.truncate()
            config.write('# Generated by preferences.save\ndefaults = {}'.format(str(defaults)))

        return {'FINISHED'}
