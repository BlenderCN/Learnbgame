# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# <pep8-80 compliant>

bl_info = {
    "name": "Sound Drivers",
    "author": "batFINGER",
    "location": "Properties > Speaker > Toolshelf",
    "description": "Drive Animations with baked sound files",
    "warning": "Still in Testing",
    "wiki_url": "https://github.com/batFINGER/batFINGER-blender-addons/wiki/sound-drivers",
    "version": (3, 1, 0),
    "blender": (2, 7, 6),
    "tracker_url": "",
    "support": 'TESTING',
    "category": "Learnbgame",
}

#reload_flag = "bpy" in locals()
reload_flag = True  # in test mode

utilities_names = (
             "subaddon",
             "utils",
             "screen_panels",
        )

subaddon_names = (
             ("sounddriver", True, True),
             ("driver_panels", True, True),
             ("driver_manager", True, True),
             ("speaker", True, True),
             ("sound", True, True),
             ("midi", False, False),
             ("visualiser", True, True),
             ("sound_action", True, True),
             ("soundaction_visualiser", False, False),
             ("sound_bake", True, True),
             ("sound_nla", True, True),
             #("EqMenu", True, False), # GONE BABY GONE (orginal)
             ("NLALipsync", True, True),
             ("filter_playback", False, False),
             ("graph", True, True),
             ("BGL_draw_visualiser", False, False),
             ("presets", True, True),
             ("pie_menu_template", True, True),
             ("icons", True, True),
             )

# use importlib for imports
from importlib import import_module, reload as reload_module
# dictionary of utilities modules
utilities = {}
for name in utilities_names:
    mod = import_module("%s.%s" % (__package__, name))
    if reload_flag:
        print("RELOAD", mod)
        reload_module(mod)
    utilities[name] = mod

SubAddon = getattr(utilities["subaddon"], "SubAddon")
draw = getattr(utilities["subaddon"], "draw")
create_addon_prefs = getattr(utilities["subaddon"], "create_addon_prefs")
handle_registration = getattr(utilities["subaddon"], "handle_registration")


import bpy
from rna_keymap_ui import draw_kmi
from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.utils import register_class, unregister_class

addons = {}
def draw(self, context):
    layout = self.layout

    def icon(test):
        if test:
            icon = 'FILE_TICK'
        else:
            icon = 'ERROR'
        return icon

    layout = self.layout
    # check that automatic scripts are enabled
    UserPrefs = context.user_preferences
    paths = UserPrefs.filepaths
    dns = bpy.app.driver_namespace
    row = layout.row()
    row.prop(UserPrefs.system, "use_scripts_auto_execute")

    if not UserPrefs.system.use_scripts_auto_execute:
        row = layout.row()
        row.label("Warning Will not work unless Auto Scripts Enabled",
                  icon='ERROR')
        return

    cf = layout.column()

    for subaddon in addons.values():
        module = subaddon.module
        info = subaddon.info
        # make a debug switch or similar
        if not hasattr(module, "bl_info"):
            continue
        #TODO better name for mod
        mod = getattr(self, subaddon.name, None)
        box = cf.box()
        subaddon.draw(box, context)

subaddonprefs = {"bl_idname": __package__,
                 "draw": draw,
                 "addons": {},
                 }

class SpeakerToolsAddonPreferences(AddonPreferences):

    ''' Speaker Tools User Prefs '''
    bl_idname = "sound_drivers"

    temp_folder = StringProperty(
            name="Example File Path",
            subtype='DIR_PATH',
            )

    midi_support = BoolProperty(
            name="Midi Support",
            description="Enable Midi Support",
            default=False,
            )
    smf_dir = StringProperty(
            name="smf (midi) python path",
            description="folder where smf is installed",
            subtype='DIR_PATH',
            )
    audio_dir = StringProperty(
            name="Audio Files Folder",
            description="folder where audio files are",
            subtype='DIR_PATH',
            )
    driver_manager_update_speed = IntProperty(
                                  name="Driver Manager Update Speed",
                                  min=1,
                                  max=100,
                                  description="Update timer, lower value = faster updates, higher value slow self update use refresh",
                                  default=10)

    def draw(self, context):
        def icon(test):
            if test:
                icon = 'FILE_TICK'
            else:
                icon = 'ERROR'
            return icon

        layout = self.layout
        # check that automatic scripts are enabled
        UserPrefs = context.user_preferences
        paths = UserPrefs.filepaths
        dns = bpy.app.driver_namespace
        row = layout.row()
        row.prop(UserPrefs.system, "use_scripts_auto_execute")

        if not UserPrefs.system.use_scripts_auto_execute:
            row = layout.row()
            row.label("Warning Will not work unless Auto Scripts Enabled",
                      icon='ERROR')
            return
        row = layout.row()
        row.label("SoundDrive in Driver Namespace", icon=icon("SoundDrive" in
                                                              dns))
        row = layout.row()
        row.label("GetLocals in Driver Namespace", icon=icon("GetLocals" in
                                                              dns))
        row = layout.row()
        row.label("DriverManager Started", icon=icon(test))
        row = layout.row()
        test = "DriverManager" in dns
        if not test:
            row.operator("drivermanager.update")
        else:
            row.prop(self, "driver_manager_update_speed", slider=True)
        row = layout.row()
        row = layout.prop(self, "midi_support")

        # midi support
        if self.midi_support:
            row = layout.row()
            row.prop(self, "smf_dir")
            row = layout.row()
            op = row.operator("wm.url_open", icon='INFO', text="GitHub PySMF Project (Cython)")
            op.url = "https://github.com/dsacre/pysmf"
            row = layout.row()
            if "smf" in locals():
                row.label("SMF IMPORTED OK...", icon='FILE_TICK')
            else:
                try:
                    import sys
                    sys.path.append(self.smf_dir)
                    import smf
                    row.label("SMF IMPORTED OK", icon='FILE_TICK')
                except:
                    row.label("SMF FAILED", icon='ERROR')

        # end midi support
        row = layout.row()
        row.prop(self, "audio_dir", icon='SOUND')
        row = layout.row()
        row.prop(paths, "sound_directory", icon='SOUND')
        row = layout.row()
        col = row.column()
        #draw_filtered(pie_menu.addon_keymaps, 'NAME', 'drivers pie menu', col)
        #draw_filtered(pie_menu.addon_keymaps, '', '', col)

        '''
        # buggy n core-dumpy
        kc = bpy.context.window_manager.keyconfigs.addon
        from sound_drivers.pie_menu  import addon_keymaps
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            draw_kmi([], kc, km, kmi, col, 0)

        for akm in pie_menu.addon_keymaps:
            row.label(str(akm))
        '''

# Open addon prefs to here op.

class SoundDriversShowPrefs(Operator):

    bl_idname = "sound_drivers.pref_show"
    bl_description = 'Display SoundDrivers addons preferences'
    bl_label = "Preferences"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        wm = context.window_manager
        #addon_utils.modules_refresh()
        mod = importlib.import_module(__package__)
        if mod is None:
            print("Something is HORRIBLY WRONG...")
            return {'CANCELLED'}
        bl_info = getattr(mod, "bl_info", {})
        mod.bl_info['show_expanded'] = True
        context.user_preferences.active_section = 'ADDONS'
        wm.addon_search = bl_info.get("name", __package__)
        wm.addon_filter = bl_info.get("category", 'ALL')
        wm.addon_support = wm.addon_support.union({bl_info.get("support", 'TESTING')})
        #mod = addon_utils.addons_fake_modules.get("sound_drivers")

        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'FINISHED'}

addonprefs = None
def register():
    addonprefs = create_addon_prefs(__package__, subaddon_names, subaddonprefs=subaddonprefs, addons=addons)
    register_class(addonprefs)
    register_class(SoundDriversShowPrefs)
    handle_registration(True, addons)
    from addon_utils import check

def unregister():
    if addonprefs:
        unregister_class(addonprefs)
    unregister_class(SoundDriversShowPrefs)
    handle_registration(False, addons)
