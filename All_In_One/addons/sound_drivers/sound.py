import bpy
from bpy.types import PropertyGroup, Panel, Operator, Menu
from bpy.props import *
from bpy.utils import register_class, unregister_class
from math import log, sqrt
from mathutils import Vector

#from sound_drivers.Equalizer import action_normalise_set
from sound_drivers import debug
from sound_drivers.sound_action import action_normalise_set

from sound_drivers.utils import get_driver_settings,\
                icon_from_bpy_datapath, getSpeaker, getAction,\
                set_channel_idprop_rna, f, propfromtype,\
                get_channel_index, copy_sound_action, nla_drop,\
                validate_channel_name, splittime,\
                get_context_area, replace_speaker_action

# validate_channel_name phase out
from sound_drivers.presets import notes_enum, note_from_freq,\
                freq_ranges, shownote

class Sound():
    def __init__(self, sound):
        pass

class SoundPanel(Panel):
    bl_label = "Sound"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    #Open this one to see the big OPEN SOUND button
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker and 'SOUND' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='SOUND')

    def draw(self, context):
        layout = self.layout
        from sound_drivers.sound_bake import BakeSoundPanel
        layout.enabled = not BakeSoundPanel.baking
        # get speaker returns the PROPERTIES PANEL speaker
        speaker = getSpeaker(context)
        # refactored code
        box = layout
        has_sound = (speaker.sound is not None)
        if not has_sound:
            row = box.row()
            row.template_ID(speaker, "sound", open="sound.open_mono")
            return

        row = box.row(align=True)

        if 'SOUND' in speaker.vismode:
            soundbox = box.box()
            row = soundbox.row(align=True)
            row.template_ID(speaker, "sound", open="sound.open_mono")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(speaker, "muted", text="")
            row = soundbox.row()
            row.prop(speaker, "volume")
            row.prop(speaker, "pitch")

            box.label("Distance", icon='ARROW_LEFTRIGHT')
            distancebox = box.box()
            split = distancebox.split()

            col = split.column()
            col.label("Volume:")
            col.prop(speaker, "volume_min", text="Minimum")
            col.prop(speaker, "volume_max", text="Maximum")
            col.prop(speaker, "attenuation")

            col = split.column()
            col.label("Distance:")
            col.prop(speaker, "distance_max", text="Maximum")
            col.prop(speaker, "distance_reference", text="Reference")

            box.label("Cone", icon='MESH_CONE')
            conebox = box.box()
            split = conebox.split()
            col = split.column()

            col.label("Angle:")
            col.prop(speaker, "cone_angle_outer", text="Outer")
            col.prop(speaker, "cone_angle_inner", text="Inner")

            col = split.column()

            col.label("Volume:")
            col.prop(speaker, "cone_volume_outer", text="Outer")

class SoundVisMenu(Menu):
    bl_idname = "soundtest.menu"
    bl_label = "Select a Sound"
    vismode = 'VISUAL'

    def draw(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        #speaker = context.scene.speaker
        #if SoundVisMenu.vismode in ["VISUAL", "SOUND", "DRIVERS"]:
        if True:
            actions = [action for action in bpy.data.actions
                       if "wavfile" in action
                       and action["wavfile"] == speaker.sound.name]

            
            for action in actions:
                if "channels" in action.keys(): # midi atm TODO
                    channels = action["channels"]
                    channels.sort()
                    '''
                    layout.label("MIDI %s" %  action["wavfile"])
                    layout.separator()
                    '''
                    groups = [g.name for g in action.groups]
                    groups.sort()
                    for channel in channels:
                        cn = groups[channels.index(channel)]
                        layout.operator_context = 'EXEC_DEFAULT'
                        op = layout.operator("soundaction.change",
                             text="%s" % (cn))
                        op.action = action.name
                        op.channel = channel
                else:
                    #layout.label("MUSIC %s" % action.name)
                    #layout.separator()
                    channel = action["channel_name"]
                    op = layout.operator("soundaction.change",
                         text="%s" % (channel))
                    op.action = action.name

def get_dm():
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    return dm

def register():
    #bakeop = bpy.types.GRAPH_OT_sound_bake
    bakeop = bpy.ops.graph.sound_bake.get_rna()
    propdic = {}
    propfromtype(propdic, bakeop)
    bakeprops = type("BakeFCProperties", (PropertyGroup,), propdic)

    register_class(bakeprops)
    propdic = {}
    sound_type = EnumProperty(items=(
                ("SOUND", "SOUND", "Basic Sound"),
                ("SFX", "SFX", "Sound Effects"),
                ("MUSIC", "MUSIC", "Music"),
                ("VOICE", "VOICE", "Voice"),
                #("MIDI", "MIDI", "Midi"),
                ),
                name="type",
                default="SOUND",
                description="Input Type",
                update=shownote
                )
    propdic["sound_type"] = sound_type

    propdic["preset"] = StringProperty(name="Preset",
                            default="",
                            #update=test,
                            options={'SKIP_SAVE'},
                            description="Save Preset")

    propdic["action_name"] = StringProperty(name="Action Name",
                                            default="SoundAction")

    propdic["channel_name"] = StringProperty(name="Channel Name",
                                             default="AA",
                              description="Limit Name to two Uppercase chars")

    propdic["channels"] = IntProperty(name="Channels",
                           default=16,
                           description="Number of frequencies to split",
                           min=1,
                           max=1000)
    propdic["minf"] = FloatProperty(name="Min Freq",
                         default=4.0,
                         description="Minimum Freq",
                         min=0,
                         max=10000.0)
    propdic["maxf"] = FloatProperty(name="Max Freq",
                         default=10000.0,
                         description="Maximum Freq",
                         min=100.0,
                         max=1000000.0)

    propdic["use_log"] = BoolProperty(name="Log Scale",
                           default=True,
                           description="Use Log scale for channels")

    '''
    # REFACTO................ OUT!!!!!!!!!!!!!!!!!
    propdic["show_graph_editor"] = BoolProperty(name="3DView to Graph",
           description="Change 3D view to Graph Editor to visualise bake",\
           default=True)
    '''
    propdic["music_start_note"] = notes_enum
    propdic["music_end_note"] = notes_enum

    # doh.. this is useless.
    propdic["log_base"] = IntProperty(name="log_base",
                           default=2,
                           description="log base to use",
                           min=2,
                           soft_min=2,
                           soft_max=32,
                           max=64)
    txt = "Automatically adjust end ranges for nill bake data"
    propdic["auto_adjust"] = BoolProperty(default=True, description=txt)

    propdic["bake_operator"] = PointerProperty(type=bakeprops)

    BakeOptions = type("BakeOptions", (PropertyGroup,), propdic)
    register_class(BakeOptions)


    dic = {"type": StringProperty(),
           "threshold": FloatProperty(default=0.0001, max=0.01),
           "keyframe_count": IntProperty(default=0),
           "fcurve_count": IntProperty(default=0),
           "samples_count": IntProperty(default=0),
           "channel_name": StringProperty(default='AA'),
           }

    SD_ActionPostPro = type("SD_ActionPostPro", (PropertyGroup,), dic)

    bpy.utils.register_class(SD_ActionPostPro)

    bpy.types.Action.tweaks = CollectionProperty(type=SD_ActionPostPro)    
    #Menus
    register_class(SoundVisMenu)

    # Operators

    bpy.types.Sound.bakeoptions = PointerProperty(type=BakeOptions)
    # Panels
    register_class(SoundPanel)

def unregister():
    unregister_class(SoundVisMenu)
    unregister_class(SoundPanel)
