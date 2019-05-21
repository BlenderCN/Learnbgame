'''
Slowly being taken out.... 

'''
import bpy
import re
from math import sqrt
from mathutils import Vector, Color, Euler, Quaternion
from random import random
from bpy.props import \
        StringProperty, IntProperty, EnumProperty, FloatProperty, \
        BoolVectorProperty, BoolProperty


from sound_drivers.sound_action import  SoundActionMenuRow

from sound_drivers.utils import \
        get_driver_settings, \
        icon_from_bpy_datapath, format_data_path, getAction, getSpeaker

from sound_drivers.filter_playback import setup_buffer, play_buffer,\
     mix_buffer, sound_buffer, remove_filter_handlers, setup_filter_handlers
# <pep8-80 compliant>


def dprint(str):
    DEBUG = False
    if bpy.app.debug or DEBUG:
        print(str)


def sync_play(self, context):
    screen = context.screen
    if screen.is_animation_playing:
        if not self.sync_play:
            # this will stop it
            bpy.ops.screen.animation_play()
            return None
    else:
        if self.sync_play:
            # this will start it
            bpy.ops.screen.animation_play()

    return None




class ContextSpeakerMenu(bpy.types.Menu):
    bl_idname = "speaker.contextspeaker"
    bl_label = "Choose speaker to drive"
    driver = None

    def draw(self, context):
        layout = self.layout
        layout = layout.column(align=True)

        actions = [a for a in bpy.data.actions if 'wavfile' in a.keys()]
        speaker_dict = {}
        wf = [a["wavfile"] for a in actions]
        speakers = [s for s in bpy.data.speakers if "vismode" in s.keys()]

        for speaker in speakers:
            row = layout.row()
            row.label(speaker.name, icon='SPEAKER')
            row = layout.row()
            #row.separator()
            sp = speaker_dict.setdefault(speaker.name, {})
            sounds = [s for s in bpy.data.sounds if s.name in wf]
            for sound in sounds:
                row = layout.row()
                row.label(sound.name)
                sp[sound.name] = [a for a in actions
                                  if a["wavfile"] == sound.name]
                for a in sp[sound.name]:
                    '''
                    row = layout.row()
                    row.label(text=" ")
                    '''
                    text = "[%s] %s" % (a["channel_name"], a.name)
                    op = row.operator("soundaction.change", text=text)
                    op.action = a.name


def register():

    #bpy.utils.register_class(SimpleOperator)
    #bpy.types.Scene.sync_play =  BoolProperty(default=False, update=sync_play)
    bpy.utils.register_class(ContextSpeakerSelectMenu)
    #bpy.utils.register_class(AddCustomSoundDriverToChannel)
    bpy.utils.register_class(ContextSpeakerMenu)
    ###bpy.utils.register_class(SoundToolPanel)


def unregister():
    #bpy.utils.unregister_class(SimpleOperator)
    #bpy.utils.unregister_class(AddCustomSoundDriverToChannel)
    bpy.utils.unregister_class(ContextSpeakerMenu)
    bpy.utils.unregister_class(ContextSpeakerSelectMenu)
    ###bpy.utils.unregister_class(SoundToolPanel)
