bl_info = {
    "name": "Speaker",
    "author": "batFINGER",
    "location": "View3D > Add > Speaker",
    "description": "Speaker Settings",
    "warning": "Still in Testing",
    "wiki_url": "",
    "version": (1, 0),
    "blender": (2, 7, 7),
    "tracker_url": "",
    "icon": 'NONE',
    "support": 'TESTING',
    "category": "Animation",
    }

import bpy

from bpy.props import *
from bpy.types import Panel, Operator
from bpy.utils import register_class, unregister_class
from bpy_extras import object_utils

from sound_drivers.utils import get_driver_settings, propfromtype,\
                icon_from_bpy_datapath, getSpeaker, getAction,\
                set_channel_idprop_rna, f, get_context_area

# testing scene property context speaker

def get_soundspeaker_list(self):
    wf = [a['wavfile'] for a in bpy.data.actions if 'wavfile' in a.keys()]
    speakers = [sp.data
                for sp in self.objects
                if sp.type == 'SPEAKER'
                and sp.data.sound is not None
                and sp.data.sound.name in wf]
    return speakers
    #return  [s for s in bpy.data.speakers  if 'vismode' in s.keys() and '_RNA_UI' in s.keys() and 'vismode' in s['_RNA_UI'].keys() and 'context' in s['_RNA_UI']['vismode'].keys()]

bpy.types.Scene.soundspeakers = property(get_soundspeaker_list)

def get_channel_names(self):
    channels = []
    if not self.sound:
        return [] # TODO change bugfix
    actions = [a for a in bpy.data.actions 
                if 'channel_name' in a.keys()
                #and a['channel_name'] in channels
                and "wavfile" in a.keys()
                and a['wavfile'] == self.sound.name]

    for a in actions: # TODO
        if "MIDI" in a.keys(): # midi file
            channels.extend(a["channels"])
        else:
            channels.append(a["channel_name"])
    return list(set(channels))

bpy.types.Speaker.channels = property(get_channel_names)

def set_context_speaker(self, speaker):
    if speaker is not None and speaker.rna_type.identifier != "Speaker":
        raise TypeError("Context Speaker must be a Speaker type")
        return None

    #look for previous context speaker
    if speaker is None:
        return None

    if speaker not in self.soundspeakers:
        print("Speaker must be baked before it can have context")
        return None

    for s in self.soundspeakers:
        if s != speaker:
            s.is_context_speaker = False
    return speaker

def get_context_speaker(self):

    #make sure that every speaker has an ['_RNA_UI']['vismode']
    

    speakers = [sp for sp in get_soundspeaker_list(self) if
                sp.is_context_speaker]

    return speakers[0] if len(speakers) else None

bpy.types.Scene.speaker = property(get_context_speaker, set_context_speaker)


class Speaker():
    def __init__(self, speaker):
        pass


class SpeakerPanel():
    bl_label = "Speaker Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    def get_action(self, context):
        return getAction(getSpeaker(context), search=True)

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        return speaker is not None and 'SPEAKER' in speaker.vismode and hasattr(context, "speaker")


class SpeakerDataPanel(SpeakerPanel, Panel):

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='SPEAKER')

    def draw(self, context):
        space = context.space_data
        if space.use_pin_id:
            speaker = space.pin_id
        else:
            speaker = context.speaker

        layout = self.layout
        action = getAction(speaker)
        layout.label("NOT IMPLEMENTED YET", icon='INFO')
        layout.separator()
        layout.label("Spatial Layouts ie (STEREO, 5.1 Surround)")
        return

        speakerL = None
        speakerR = None
        actionL = None
        actionR = None
        '''
        STEREO
        if context.object.parent:
            for sp in context.object.parent.children:
                if "LEFT" in sp.data.keys() and sp.data["LEFT"]:
                    speakerL = sp.data
                    actionL = getAction(speakerL)
                    print('LEFT')
                elif "RIGHT" in sp.data.keys() and sp.data["RIGHT"]:
                    speakerR = sp.data
                    print('RIGHT')
                    actionR = getAction(speakerR)
        '''
        #print(context.object.parent, action, actionL, actionR)


'''
Operators
'''
class OBJECT_OT_speaker_add(bpy.types.Operator, object_utils.AddObjectHelper):
    """Add a Speaker to SoundDrive"""
    bl_idname = "object.speaker_add"
    bl_label = "Add Speaker"
    bl_options = {'REGISTER', 'UNDO'}
    '''
    Override the add speaker operator.
    Copy the props from the original operator to make it seemless
    Set the panels to {'SOUND'}
    '''
    propdic = {}

    propfromtype(propdic, bpy.ops.object.speaker_add.get_rna())

    for k,v in propdic.items():
        exec("%s = v" % k)
        #(OBJECT_OT_speaker_add, k, v)


    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        if ob.type != 'SPEAKER':
            return
        sound = (hasattr(ob, "data") and getattr(ob.data, "sound", None) is not None)
        layout.enabled = (len(context.screen.areas) > 1) and not sound
        #layout.label(str(sound))
        col = layout.column(align=True)
        col.prop(self, 'view_align')

        col = layout.column(align=True)
        col.label(text="Location")
        col.prop(self, 'location', text="")

        col = layout.column(align=True)
        col.enabled = not self.view_align
        col.label(text="Rotation")
        col.prop(self, 'rotation', text="")


    def invoke(self, context, event):
        object_utils.object_add_grid_scale_apply_operator(self, context)
        return self.execute(context)

    def execute(self, context):
        spk = bpy.data.speakers.new('Speaker')
        base = object_utils.object_data_add(context, spk, operator=self)
        ob = base.object
        context.scene.frame_set(1)
        #return {'FINISHED'}
        if not getattr(ob, "animation_data", None):
            d = context.copy()
            info = None
            nla = None
            #find any area that is not the current area
            ob.animation_data_create()
            soundtrack = ob.animation_data.nla_tracks.new()
            soundtrack.name = "SoundTrack"
            areas = [a for a in context.screen.areas if a != context.area]
            if len(areas):
                area = areas[0]
                t =  area.type
                area.type = 'NLA_EDITOR'
                d["area"] = area
                # add an NLA track
                nla = get_context_area(context, d, area_type='NLA_EDITOR')
                bpy.ops.nla.soundclip_add(d)
                soundtrack.select = False #  Otherwise you get track on track.
                area.type = t
            else:
                # ok no override available.. going to have to flip into NLA_ED
                # draw method unavailable. feck it.
                context.area.type = 'NLA_EDITOR'
                bpy.ops.nla.soundclip_add()
                context.area.type = 'VIEW_3D'

            spk.vismode = {'SOUND'}

            props = get_context_area(context, {}, area_type='PROPERTIES',
                                     context_screen = True)
            if props is not None:
                if getattr(props.spaces.active, "context", None):
                    try:
                        props.spaces.active.context = 'DATA'
                    except:
                        pass

        return {'FINISHED'}


class SpeakerSelectorOperator(bpy.types.Operator):
    """Edit Driver"""
    bl_idname = "speaker.select_context"
    bl_label = "Set Context Speaker"
    bl_description = "Set Context Speaker"
    contextspeakername = StringProperty(default="")
    @classmethod
    def poll(cls, context):
        #global dm
        speakers = [s for s in context.scene.objects if s.type == 'SPEAKER']
        return len(speakers) > 0

    def invoke(self, context, event):
        return self.execute(context)

        speaker = bpy.data.speakers.get(self.contextspeakername)
        speaker.is_context_speaker = True
        #context.scene.speaker = speaker
        wm = context.window_manager
        return wm.invoke_popup(self)
        bpy.ops.wm.call_menu("soundtest.menu")
        return {'FINISHED'}

    def execute(self, context):
        speaker = bpy.data.speakers.get(self.contextspeakername)
        if speaker:
            speaker.is_context_speaker = True
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout = layout.column(align=True)
        speaker = bpy.data.speakers.get(self.contextspeakername)
        speakers = [speaker]

        actions = [a for a in bpy.data.actions if 'wavfile' in a.keys()]# and "%s%d" % (a['channel_name'],0) in sp.keys()]
        wf = [a["wavfile"] for a in actions]

        for speaker in speakers:
            row = layout.row()
            row.label(speaker.name, icon='SPEAKER')
            row = layout.row()
            #row.separator()
            sounds = [s for s in bpy.data.sounds if s.name in wf]
            for sound in sounds:
                row = layout.row()
                row.label(sound.name)
                sp = [a for a in actions if a["wavfile"] == sound.name]
                for a in sp:
                    '''
                    row.label(text=" ")
                    '''
                    row = layout.row()
                    text = "[%s] %s" % (a["channel_name"], a.name)
                    op = row.operator("soundaction.change", text=text)
                    op.action = a.name

def toggle_context_speaker(self, context):
    if self.is_context_speaker:
        context.scene.speaker = self

    #context.scene.speaker = self

class ClosePopupWindow(Operator):
    """Close Popup Window (and remove screen)"""
    bl_idname = "wm.close_popup_window"
    bl_label = "Close Popup Window"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        screen = context.screen
        windows = [w for w in context.window_manager.windows if w != context.window]
        c = {"screen": screen,
             "window": context.window
             }

        if len(windows):
            bpy.ops.wm.window_close('INVOKE_DEFAULT')
            c["window"] = windows[0]
            screen = windows[0].screen
            print("GO BACK TO SCREEN ", screen.name)
            bpy.ops.screen.delete(c, 'INVOKE_DEFAULT')
            windows[0].screen = screen
            print(windows[0].screen.name)

        else:
            bpy.ops.screen.delete(c)

        return {'FINISHED'}

def sd_popout(self, context):
    screen = context.screen
    space = context.space_data
    layout = self.layout
    if len(screen.areas) == 1:
        layout.operator("wm.close_popup_window", icon='X')
        for x in screen.sound_driver_areas:
            layout.label(x.name)
    if space.pin_id == context.scene.speaker and len(screen.areas) > 1:
        
        layout.operator("screen.area_dupli",
                        text="Popout")
    return None

class ContextSpeakerSelectMenu(bpy.types.Menu):
    bl_idname = "speaker.select_contextspeaker"
    bl_label = "Choose speaker to drive"
    driver = None

    def draw(self, context):
        # sounds in baked actions

        for speaker in context.scene.soundspeakers:
            text = "%s (%s)" % (speaker.name, speaker.sound.name)
            self.layout.operator("speaker.select_context",
                                 text=text).contextspeakername = speaker.name

def vismode_panel_items(self, context):
    # if is_baking then only show bake panel
    #print("PANEL ITEMS", self, context.scene)
    userprefs = context.user_preferences.addons[__package__].preferences
    midiprefs = userprefs.addons["midi"].preferences
    midi_support = userprefs.addons["midi"].enabled
    filter_support = userprefs.addons["filter_playback"].enabled
    ui_visualiser_support = userprefs.addons["soundaction_visualiser"].enabled
    bgl_visualiser_support = userprefs.addons["BGL_draw_visualiser"].enabled
    visualiser_support = bgl_visualiser_support or ui_visualiser_support
    if bpy.types.BakeSoundPanel.baking:
        return [("BAKE", "BAKE", "Bake Sound to FCurves", 'FCURVE', 64)]
    
    pv = [("SPEAKER", "SPEAKER", "Edit Speaker properties", 'SPEAKER', 1),
          ("SOUND", "SOUND", "Edit sound properties", 'SOUND', 2)]

    if midi_support and midiprefs.midi_support:
        from sound_drivers.icons import get_icon
        icon = get_icon("main", "midi")

        pv.append(
          ("MIDI", "MIDI", "Associate a midi file", icon.icon_id, 128))
    if self.sound is not None:
        pv.extend([("BAKE", "BAKE", "Bake Sound to FCurves", 'FCURVE', 64)])
    if not getattr(self, "animation_data", None):
        pass
    else:
        if self.animation_data.action is not None:
            if visualiser_support:
                pv.append(("VISUAL",
                           "VISUAL",
                           "Show sound visualiser",
                           'SEQ_HISTOGRAM', 16))
            pv.append(("ACTION", "ACTION", "Sound Action Properties", 'ACTION', 4))
            if filter_support:
                  pv.append(("OUT", "OUT", "Filter Output", 'FILTER', 32))

        if len(self.animation_data.nla_tracks) > 1:
            pv.extend([("NLA", "NLA", "NLA SoundTracks", 'NLA', 8)])
        '''
        pv = [("SPEAKER", "SPEAKER", "Edit Speaker properties",'SPEAKER',1),
              ("SOUND", "SOUND", "Edit sound properties",'SOUND',2),
              ("ACTION", "ACTION", "Sound Action Properties",'ACTION',4),
              ("NLA", "NLA", "NLA SoundTracks",'NLA',8),
              ("VISUAL", "VISUAL", "Show sound visualiser",'SEQ_HISTOGRAM',16),
              ("OUT", "OUT", "Filter Output",'FILTER',32),
              ("BAKE", "BAKE", "Bake Sound to FCurves",'FCURVE',64),]
        '''
    return pv

def register():
    bpy.types.Speaker.vismode = EnumProperty(items=vismode_panel_items,
                                name="SoundDriver",
                                description="Panel Filters",
                                options={'HIDDEN', 'ENUM_FLAG'})



    bpy.types.Speaker.is_context_speaker = BoolProperty(name="ContextSpeaker",
                                           description="(Un)Set context Speaker",
                                           default=False,
                                           update=toggle_context_speaker)
    bpy.types.PROPERTIES_HT_header.append(sd_popout)
    register_class(ClosePopupWindow)
    register_class(OBJECT_OT_speaker_add)
    register_class(SpeakerDataPanel)
    register_class(SpeakerSelectorOperator)
    register_class(ContextSpeakerSelectMenu)

def unregister():
    unregister_class(ClosePopupWindow)
    unregister_class(OBJECT_OT_speaker_add)
    #from bpy.types import OBJECT_OT_speaker_add as AddSpeaker
    # re-register the old one
    #register_class(AddSpeaker)
    unregister_class(SpeakerDataPanel)
    unregister_class(SpeakerSelectorOperator)
    unregister_class(ContextSpeakerSelectMenu)
    bpy.types.PROPERTIES_HT_header.remove(sd_popout)
    # remove property defs
    del(bpy.types.Speaker.vismode)
    del(bpy.types.Speaker.channels)
    del(bpy.types.Speaker.is_context_speaker)
    del(bpy.types.Scene.soundspeakers)
