# coding=utf-8

""" Copyright 2014 - 2018, Wybren van Keulen, The Grove """


import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from .Translation import t


class TheGrove6Preferences(AddonPreferences):
    bl_idname = __package__

    show_refresh_warning : BoolProperty(name="Show Refresh Warning", default=False, options={'HIDDEN'})

    twigs_path : StringProperty(
        name=t('twigs_path'), description=t('twigs_path_tt'), subtype='DIR_PATH')

    textures_path : StringProperty(
        name=t('textures_path'), description=t('textures_path_tt'), subtype='DIR_PATH')

    set_scene_units : BoolProperty(
            name=t('set_scene_units'),
            default=True,
            description=t('set_scene_units_tt'))

    def update_language(self, context):
        """ The Grove's user preferences allow you to pick a language. This sets Blender's overall language,
            but if international fonts is enabled, but Interface and Tooltips below are disabled,
            only The Grove's interface is translated.
            There seems to be no way to reload the addon to update the language, because once the addon is disabled,
            it is impossible to re-enable it. Therefore, I use the refresh warning to tell the user to
            press F8 to reload the addon and show the selected language. """

        print('updating')
        print(self.language)
        preferences = context.preferences.view
        preferences.language = self.language
        preferences.use_international_fonts = True
        self.show_refresh_warning = True

    languages = [
        ('en_US', 'English', 'English')]

    language : EnumProperty(
        name=t('language_tt'), description=t('language_tt'),
        items=languages,
        default='en_US',
        update=update_language)

    def draw(self, context):
        preferences = context.preferences.view
        if preferences.use_international_fonts == False and self.languages != 'en_US':
            preferences.use_international_fonts = True

        layout = self.layout
        layout.prop(self, 'twigs_path')
        layout.prop(self, 'textures_path')

        layout.separator()
        layout.prop(self, 'set_scene_units')

        layout.separator()
        row = layout.row()
        row.scale_y = 1.4
        row.operator('wm.save_userpref')

        layout.separator()
        layout.separator()

def register():

    bpy.utils.register_class(TheGrove6Preferences)
   


def unregister():

    bpy.utils.unregister_class(TheGrove6Preferences)
