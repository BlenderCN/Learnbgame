# <pep8-80 compliant>
import bpy
import aud

from bpy.props import BoolProperty
from sound_drivers.utils import getAction, getSpeaker
from bpy.utils import register_class, unregister_class
from bpy.types import Panel
#from sound_drivers.sound_bake import BakeSoundPanel
from math import sqrt

bpy.types.Speaker.play_speaker = BoolProperty(default=False)

DBG = False

sound_buffer = {}

def showFilterBox(layout, context, speaker, action):
    dns = bpy.app.driver_namespace
    if action:
        scene = context.scene
        minf = -1
        maxf = -1
        if "row_height" not in action.keys():
            return
        scale = action["row_height"]
        name = "Channel"
        if "Channels" in action:
            channels = action["Channels"]
            name = channel_name = action["channel_name"]
            minf = action["minf"]
            maxf = action["maxf"]
            MIN = action["min"]
            MAX = action["max"]
            start = action["start"]
            end = action["end"]
        else:
            channels = len(action.fcurves)
            minf = 0.0
            MIN = 0.0
            maxf = 0.0
            MAX = 0.0
            start = 0
            end = channels

        if start >= end:
            end = start + 1
        i = start
        box = layout
        row = box.row()
        row.prop(speaker, "filter_sound", toggle=True)
        #row = box.row()
        #row.prop(scene, "sync_play", toggle=True, text="PLAY", icon="PLAY")
        b = dns.get("ST_buffer")
        h = dns.get("ST_handle")
        if b and not h:
            row = layout.row()
            row.label("BUFFERING %s" % b, icon='INFO')
        if b:
            row = layout.row()
            row.label("BUFFERED %s" % b, icon='INFO')
        if h:
            row = layout.row()
            if not h.status:
                row.label("Handle %s" % h.status, icon='INFO')
            else:
                row.label("Handle.position %d %0.2fs" % (h.status, h.position),
                          icon='INFO')

        row = box.row()
        COLS = int(sqrt(channels))

        sound_channel_id = "%s__@__%s" % (speaker.name, action.name)
        sound_item = None
        from sound_drivers.filter_playback import sound_buffer
        if sound_buffer:
            sound_item = sound_buffer.get(sound_channel_id)
        filter_item = scene.sound_channels.get(sound_channel_id)
        if filter_item is not None:
            '''
            row = box.row()
            row.prop(filter_item, "buffered")
            row = box.row()
            row.prop(filter_item, "valid_handle")
            '''
            for i in range(start, end + 1):
                cn = "channel%02d" % i
                if not i % COLS:
                    row = box.row()
                col = row.column()
                # BUGGY on speaker object
                icon = 'OUTLINER_DATA_SPEAKER'
                if sound_item and sound_item.get(cn):
                    icon = 'OUTLINER_OB_SPEAKER'
                col.prop(filter_item,
                         cn,
                         text="%s" % i,
                         icon=icon,
                         toggle=True)


class FilterSoundPanel(Panel):
    bl_label = "Filter Sound"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker and 'OUT' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='FILTER')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not bpy.types.BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)
        showFilterBox(layout, context, speaker, action)

def dprint(str):
    global DBG
    if DBG:
        print(str)


def playspeaker(name, volume=1.0, limit=[], highpass=None, lowpass=None):
    speaker_obj = bpy.data.objects.get(name)
    if not speaker_obj:
        dprint("No speaker object named %s" % name)
        return 0.0
    speaker = speaker_obj.data
    on = speaker.filter_sound
    if on:
        device = aud.device()
        #load the factory
        dprint("-" * 80)
        dprint("playing %s" % speaker.sound.filepath)
        dprint("-" * 80)
        dprint("limit %s" % str(limit))
        dprint("lowpass %s" % str(lowpass))
        dprint("highpass %s" % str(highpass))
        f = speaker.sound.factory
        #f = aud.Factory(speaker.sound.filepath)
        if len(limit):
            f = f.limit(limit[0], limit[1])
        if lowpass is not None:
            f = f.highpass(highpass)
        if highpass is not None:
            f = f.highpass(highpass)
        #apply the
        device.play(f)
    else:
        dprint('speaker.on = False')

#use console for test call
'''
Set the speaker to on to test..
in console
>>> C.object.data.on
False

>>> C.object.data.on = True

>>> ps = bpy.app.driver_namespace['ST_play_speaker']
>>> ps("Speaker")
------------------------------------------------------------------------------
playing C:\blender_test\audio\batman.wav
------------------------------------------------------------------------------
limit []
lowpass None
highpass None
'''
bpy.app.driver_namespace["ST_play_speaker"] = playspeaker
soundeffects = {}
soundeffects["Speaker"] = {1: {"limit": [], "low": 135, "high": 208},
                           200: {"limit": [], "low": None, "high": None}
                           }
ps = bpy.app.driver_namespace['ST_play_speaker']


bpy.app.driver_namespace["ST_handle"] = None
bpy.app.driver_namespace["ST_buffer"] = None


def ST__FT_playback_status(scene):
    dprint("Play STATUS")
    context = bpy.context
    screen = context.screen
    device = aud.device()
    buffer = bpy.app.driver_namespace.get("ST_buffer")
    handle = bpy.app.driver_namespace.get("ST_handle")
    if handle and handle.status:
        if not screen.is_animation_playing:
            handle.pause()
        else:
            handle.resume()
        #device.stopAll()
        return None


def ST__FT_filter_playback(scene):
    dprint("filter playbakc")
    context = bpy.context
    screen = context.screen
    device = aud.device()
    buffer = bpy.app.driver_namespace.get("ST_buffer")
    handle = bpy.app.driver_namespace.get("ST_handle")
    if handle and handle.status == 0:
        handle = None
        bpy.app.driver_namespace["ST_handle"] = None

    if not screen.is_animation_playing:
        if handle:
            dprint("PAUSE PAUSE PAUSE")
            handle.pause()
        #device.stopAll()
        return None
    cf = scene.frame_current
    if scene.use_preview_range:
        frame_start = scene.frame_preview_start
        frame_end = scene.frame_preview_end
    else:
        frame_start = scene.frame_start
        frame_end = scene.frame_end

    fps = scene.render.fps / scene.render.fps_base
    '''
    if cf == frame_start:
        if not handle and buffer:
            handle =  device.play(buffer)
            handle.keep = True
            bpy.app.driver_namespace["ST_handle"] = handle

    '''
    if handle:
        if cf == frame_start:
            device.lock()
            handle.pause()
            handle.position = max(cf / fps, 0.0)  # don't like negs
            if cf >= 0.0:
                handle.resume()
            device.unlock()

        elif cf == frame_end:
            handle.pause()
        fr = int(handle.position * fps)
        '''
        if fr > cf and cf > 1:
            scene.frame_set(fr)
            return None

        '''

def mix_buffer(context):
    dprint("mix BUff")
    #make a buffer from the channel mix
    # set up a buffer with the same dictionary structure as the
    device = aud.device()
    scene = context.scene
    fps = scene.render.fps / scene.render.fps_base
    if not context:
        return None

    if scene.use_preview_range:
        frame_start = scene.frame_preview_start
        frame_end = scene.frame_preview_end
    else:
        frame_start = scene.frame_start
        frame_end = scene.frame_end
    # get
    g = None
    for name, value in scene.sound_channels.items():
        mix = sound_buffer.get(name)
        if mix is None:
            continue
        speaker_name, action_name = name.split("__@__")
        speaker = bpy.data.speakers.get(speaker_name)
        if not speaker:
            continue
        action = getAction(speaker)
        if not speaker.filter_sound \
               or action_name != action.name:  # using the mute as a flag
            continue

        channel_name = action["channel_name"]
        fs = int(max(frame_start, action.frame_range.x))
        fe = min(frame_end, action.frame_range.y)
        if True:

            for i in range(action["start"], action["end"]):
                ch = "channel%02d" % i
                if value.get(ch):  # channel selected for mix
                    f = mix.get(ch)
                    if g:
                        #f = f.join(g) # join
                        f = f.mix(g)
                    g = f

    if g:
        #factory_buffered =
        #aud.Factory.buffer(g.limit((fs-1) / fps, (fe-1) / fps))
        bpy.app.driver_namespace["ST_buffer"] = g
        factory_buffered = aud.Factory.buffer(g)
        dprint("buffered")
        return factory_buffered

    return None


def play_buffer(buffer):
    dprint("Play BUff")
    device = aud.device()
    if not buffer:
        return None
    handle = device.play(buffer)
    handle.keep = True
    bpy.app.driver_namespace["ST_handle"] = handle
    return handle


def setup_buffer(context):
    dprint("Setup BUffer")
    # set up a buffer with the same dictionary structure as the
    device = aud.device()
    scene = context.scene
    fps = scene.render.fps / scene.render.fps_base
    if not context:
        return False

    if scene.use_preview_range:
        frame_start = scene.frame_preview_start
        frame_end = scene.frame_preview_end
    else:
        frame_start = scene.frame_start
        frame_end = scene.frame_end
    # get
    for name, value in scene.sound_channels.items():
        mix = sound_buffer[name] = {}
        speaker_name, action_name = name.split("__@__")
        speaker = bpy.data.speakers.get(speaker_name)
        if speaker is None:
            continue
        action = getAction(speaker)
        if action is None:
            continue
        if not speaker.filter_sound \
               or action_name != action.name:  # using the mute as a flag
            continue

        channel_name = action["channel_name"]
        rna_ui = speaker['_RNA_UI']
        fs = int(max(frame_start, action.frame_range.x))
        fe = min(frame_end, action.frame_range.y)
        if True:

            for i in range(action["start"], action["end"]):
                if True:
                    low = rna_ui['%s%d' % (channel_name, i)]['low']
                    high = rna_ui['%s%d' % (channel_name, i)]['high']
                    f = speaker.sound.factory
                    #f = aud.Factory(speaker.sound.filepath)
                    f = f.lowpass(low).highpass(high).buffer()
                    mix["channel%02d" % i] = f

    return True

# remove if there


def remove_handlers_by_prefix(prefix):
    handlers = bpy.app.handlers
    my_handlers = [getattr(handlers, name)
                   for name in dir(handlers)
                   if isinstance(getattr(handlers, name), list)]

    for h in my_handlers:
        fs = [f for f in h if callable(f) and f.__name__.startswith(prefix)]
        for f in fs:
            h.remove(f)


def ST__FT_scrubber(scene):
    frame = scene.frame_current
    fps = scene.render.fps
    if not frame % fps:

        start_time = frame // fps
        end_time = (start_time + 1 - 1 / fps)
        device.stopAll()
        ps("Speaker", limit=[start_time, end_time])

def get_sound_channel(scene, name):
    sound_channel = scene.sound_channels.get(name)
    if not sound_channel:
        sound_channel = scene.sound_channels.add()
        sound_channel.name = name
    return sound_channel

def filter_sound(speaker, action, context):
    #print("FILTER SOUND", self.filter_sound)
    scene = context.scene

    name = "%s__@__%s" % (speaker.name, action.name)
    #speaker_filter_sound(speaker, context)
    if True:

        sound_channel = get_sound_channel(scene, name)
        if scene.use_preview_range:
            frame_start = scene.frame_preview_start
            frame_end = scene.frame_preview_end
        else:
            frame_start = scene.frame_start
            frame_end = scene.frame_end
        fs = max(action.frame_range.x, frame_start)
        # have to go back to start to enable effect
        #scene.frame_set(fs)

        '''
        for i in action["Channels"]
            ch = "channel%02d" % i
            if getattr(sound_channel, ch) != sw:
                setattr(sound_channel, ch, sw)
        '''

def speaker_filter_sound(self, context):
    if not self.filter_sound:
        remove_filter_handlers()
        return
    # stop playback and go to frame 1
    screen = context.screen
    scene = context.scene
    filter_sound(self, self.animation_data.action, context)
    playing = screen.is_animation_playing
    if playing:
        #this will stop it
        bpy.ops.screen.animation_play()
    scene.frame_set(1)

    self.muted = self.filter_sound
    h = bpy.app.driver_namespace.get("ST_handle")
    if not self.filter_sound:
        if h and h.status:
            h.stop()
        return None

    b = bpy.app.driver_namespace.get("ST_buffer")
    if not b:
        if setup_buffer(context):
            b = bpy.app.driver_namespace["ST_buffer"] = mix_buffer(context)

    if not h:
        bpy.app.driver_namespace["ST_handle"] = play_buffer(b)
    if playing:
        #this will restart it
        bpy.ops.screen.animation_play()
    setup_filter_handlers()
    return None


def remove_filter_handlers():
    remove_handlers_by_prefix('ST__FT_')


def setup_filter_handlers():
    remove_filter_handlers()
    bpy.app.handlers.frame_change_post.append(ST__FT_filter_playback)
    bpy.app.handlers.scene_update_post.append(ST__FT_playback_status)


def register():
    #setup_filter_handlers()
    register_class(FilterSoundPanel)
    bpy.types.Speaker.filter_sound = BoolProperty(default=False,
                                                  update=speaker_filter_sound)
    bpy.app.driver_namespace["ST_setup_buffer"] = setup_buffer

def unregister():
    unregister_class(FilterSoundPanel)
    del(bpy.types.Speaker.filter_sound)
    #setup_filter_handlers()
    #bpy.app.driver_namespace["ST_setup_buffer"] = setup_buffer
