bl_info = {
    "name": "Sound Action",
    "author": "batFINGER",
    "location": "View3D > Add > Speaker",
    "description": "Sound Action",
    "warning": "Still in Testing",
    "wiki_url": "",
    "version": (1, 0),
    "blender": (2, 7, 7),
    "tracker_url": "",
    "icon": 'NONE',
    "support": 'TESTING',
    "category": "Animation",
    }
# <pep8-80 compliant>
import bpy
from bpy.app.handlers import persistent
from bpy.props import (StringProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       BoolProperty,
                       BoolVectorProperty,
                       FloatVectorProperty,
                       CollectionProperty,
                       PointerProperty,
                       )
from bpy.utils import (preset_find,
                       preset_paths,
                       register_class,
                       unregister_class
                       )
from bpy.types import PropertyGroup, Operator, Panel

from math import log, sqrt
from mathutils import Vector, Color
from sound_drivers.NLALipsync import SoundTools_LipSync_PT
from sound_drivers.presets import AddPresetSoundToolOperator
from bl_ui.properties_data_speaker  import (DATA_PT_context_speaker,
                DATA_PT_speaker, DATA_PT_cone, DATA_PT_distance,
                DATA_PT_custom_props_speaker)

# TODO fix or prepend eg utils.getSpeaker
from sound_drivers.utils import (getSpeaker, getAction,
                                 copy_sound_action,
                                 nla_drop,
                                 get_context_area,
                set_channel_idprop_rna, f, get_channel_index, unique_name)

from sound_drivers.filter_playback import (setup_buffer, play_buffer,
                mix_buffer)

@persistent
def InitSoundTools(dummy):
    dns = bpy.app.driver_namespace
    if "SoundDrive" not in dns:
        print("SoundDrive Added to drivers namespace")
        bpy.app.driver_namespace["SoundDrive"] = SoundDrive
    if "GetLocals" not in dns:
        dns["GetLocals"] = local_grabber
    handler = bpy.app.handlers.frame_change_pre
    handlers = [f for f in handler if f.__name__ == "live_speaker_view"]
    for f in handlers:
        handler.remove(f)
    handler.append(live_speaker_view)
    if dummy is not None:
        for speaker in bpy.data.speakers:
            speaker.filter_sound = False

def live_speaker_view(scene):
    '''
    Update the visualiser in the PROPERTIES Panel
    this can be very heavy when animating so check if needed
    '''
    if len(scene.soundspeakers) == 0:
        return None
    if scene is None:
        return None

    if scene.speaker is None:
        return None

    if 'VISUAL' not in scene.speaker.vismode:
        return None
    
    #for window in wm.windows:
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'PROPERTIES':
                if not (area.spaces.active.pin_id is not None and area.spaces.active.pin_id == scene.speaker):
                    if scene.objects.active is not None:
                        if scene.objects.active.type != 'SPEAKER':
                            return None
                if area.spaces.active.context == 'DATA':
                    area.tag_redraw()
    return None

# DRIVER methods
def local_grabber(index, locs, dm):
    '''
    dns = bpy.app.driver_namespace
    dm = dns.get("DriverManager")
    '''
    if dm is None:
        return 0.0
    ed = dm.find(index)

    if ed is not None:
        setattr(ed, "locs", locs)
    return 0.0


def SoundDrive(channels, **kwargs):
    if isinstance(channels, float):
        channel = channels
    elif isinstance(channels, list):
        op = kwargs.get('op', 'avg')
        if op == 'avg':
            if len(channels) > 0:
                channel = sum(channels) / len(channels)
            else:
                channel = 0.0
        elif op in ['sum', 'min', 'max']:
            channel = eval("%s(channels)" % op)
    else:
        print("SoundDrive %f" % channel)
        return 0.0  # somethings gone wrong
    del(channels)

    value = kwargs.get('amplify', 1.0) * kwargs.get('norm', 1.0) * channel
    if 'threshold' not in kwargs.keys():
        return(value)
    if value > kwargs.get('threshold', 0.00):
        return(value)
    else:
        return(0.0)


def getrange(fcurve, tolerance):
    '''
    #get the minimum and maximum points from an fcurve

    REJECT = tolerance  # reject frequencty
    #print(len(fcurve.sampled_points))
    points = [0.0]
    for point in fcurve.sampled_points:
        # bake sound to fcurve returns some rubbish when the frequency
        # is out of range
        # often the only usable point is in the first
        if point.co[1] > -REJECT and point.co[1] < REJECT:
            points.append(point.co[1])
    #print(points)
    #print("GETRANGE",min(points),max(points))
    '''
    (minv, maxv), (min_pos, max_pos) = fcurve.minmax

    hasrange = abs(maxv - minv) > 0.01

    return hasrange, round(minv, 4), round(maxv, 4)


def SoundActionMenuRow(row, speaker, action, has_sound):
    if has_sound:
        col = row.column()
        col.alignment = 'LEFT'
        col.menu("soundtest.menu", text="", icon='SOUND')
    #col.alignment="LEFT"
    if action:
        col = row.column()
        col.prop(action, "name", emboss=True, text="")
    else:
        col = row.column()
        #col.label("NO SOUND BAKED")
        col.operator("speaker.visualise",
                     text="Bake %s" % speaker.sound.name)
    col = row.column()
    col.alignment = 'RIGHT'
    split = col.split()
    split.alignment = 'RIGHT'
    if not has_sound:
        return
    if action:
        split.prop(action, "use_fake_user",
                   toggle=True, text="F", emboss=True)
    op = split.operator("speaker.visualise", text="", icon='ZOOMIN')
    return(op)

class SoundActionBaseOperator:
    sd_tweak_type = 'BAKED'

    def count_keyframes(self, action):
        keyframes = [len(fc.keyframe_points) for fc in action.fcurves]
        samples = [len(fc.sampled_points) for fc in action.fcurves]
        return sum(samples), sum(keyframes)

    def add_to_tweaks(self, action):
        tw = action.tweaks.add()  
        #tw.type = "COPIED FROM %s" % original_action.name
        tw.type = self.sd_tweak_type
        tw.samples_count, tw.keyframe_count = self.count_keyframes(action)
        tw.fcurve_count = len(action.fcurves)
        tw.channel_name = action.get("channel_name", "AA")

class ChangeSoundAction(Operator):
    """Make Action Active"""
    bl_idname = "soundaction.change"
    bl_label = "Load Action"
    action = StringProperty(default="", options={'SKIP_SAVE'})
    #action = StringProperty(default="")
    channel = StringProperty(default="", options={'SKIP_SAVE'})
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        return speaker is not None

    def draw(self, context):
        speaker = getSpeaker(context)
        layout = self.layout
        if not speaker:
            return {'CANCELLED'}
        soundaction = getAction(speaker)

        soundaction = bpy.data.actions.get(self.action, None)
        #soundaction = bpy.data.actions.get(self.action)
        #layout.enabled = False
        #layout.menu("soundtest.menu", text=soundaction.get("channel_name", "AA"))
        layout.enabled = True
        layout.operator("wm.call_menu", text=soundaction.get("channel_name", "AA"), emboss=True).name = "soundtest.menu"


    def execute(self, context):
        #speaker = context.scene.speaker
        speaker = getSpeaker(context)
        if not speaker:
            return {'CANCELLED'}
        soundaction = bpy.data.actions.get(self.action)
        if soundaction is not None:
            from sound_drivers.sound import SoundVisMenu
            SoundVisMenu.bl_label = soundaction["channel_name"]
            speaker.animation_data.action = soundaction
            if self.channel:
                # set channel for now TODO
                soundaction["channel_name"] = self.channel
            action_normalise_set(soundaction, context)

        dm = bpy.app.driver_namespace.get('DriverManager')
        if dm is not None:
            dm.set_edit_driver_gui(context)
        return {'FINISHED'}

class CopySoundAction(SoundActionBaseOperator, Operator):
    """Copy Action with new channel name"""
    bl_idname = "soundaction.copy"
    bl_label = "Sound Action Copy"
    new_channel_name = StringProperty(default="AA")
    nla_drop = BoolProperty(default=True)
    sd_tweak_type = 'COPIED'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None)

    def execute(self, context):
        speaker = getSpeaker(context)
        original_action = speaker.animation_data.action
        newaction = copy_sound_action(speaker, self.new_channel_name)
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]

        if newaction is not None:
            speaker.animation_data.action = newaction
            speaker.sound.bakeoptions.channel_name =\
                    unique_name(channels, "AA")
                    #unique_name(channels, self.new_channel_name)

            if self.nla_drop:
                # need to override context to use.. cbf'd
                nla_drop(speaker, newaction, 1, self.new_channel_name)

            self.add_to_tweaks(newaction)
            #tw.type = "COPIED FROM %s" % original_action.name
            return {'FINISHED'}

        return {'CANCELLED'}

class SoundSwitchAction(SoundActionBaseOperator, Operator):
    """Create a switch action from current"""
    bl_idname = "soundaction.copy_to_switches"
    bl_label = "SoundAction Threshold Copy to Switch"
    new_channel_name = StringProperty(default="AA")
    nla_drop = BoolProperty(default=True)
    threshold = IntProperty(default=50, min=1, max=99,
                              soft_min=10,
                              soft_max=80,
                              name="Threshold",
                              description="switch = 1 if val > threshold else 0",
                              )
                              
    bl_options = {'REGISTER', 'UNDO'}
    sd_tweak_type = 'COPIED_SWITCH'

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        return (speaker is not None)

    def execute(self, context):
        def evaluate(co, channel, mx):
            #co = p.co
            x, y  = co.x, 1 if co.y > self.threshold / 100 * mx else 0
            #p.co = (x, y)
            return (x, y)
        
        speaker = getSpeaker(context)
        original_action = speaker.animation_data.action
        self.new_channel_name = unique_name(speaker.channels, original_action.get("channel_name", "AA"))
        newaction = copy_sound_action(speaker, self.new_channel_name)
        ch = newaction["channel_name"]
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]

        if newaction is None:
            return {'CANCELLED'}

        start, end = newaction.frame_range
        speaker.animation_data.action = newaction
        speaker.sound.bakeoptions.channel_name =\
                unique_name(channels, self.new_channel_name)

        rna = eval(newaction["rna"])

        fcurves = [f for f in newaction.fcurves]    
        for fcurve in fcurves:
            dp = fcurve.data_path
            channel = fcurve.data_path.strip("\"'[]")
            #print(rna[channel])
            pts = [x for  p in fcurve.sampled_points for x in evaluate(p.co, channel, rna[channel]["b"])]
            #print(pts)
            rna[channel]["a"] = 0
            rna[channel]["b"] = 1
            newaction["min"] =  rna[channel]["min"] = rna[channel]["soft_min"] = 0
            newaction["max"] =  rna[channel]["max"] = rna[channel]["soft_max"] = 1
            newaction.fcurves.remove(fcurve)
            new_fcurve = newaction.fcurves.new(dp, action_group=ch)
            new_fcurve.extrapolation = 'CONSTANT'
            new_fcurve.keyframe_points.add(len(pts) // 2)
            new_fcurve.keyframe_points.foreach_set("co", pts)
            for p in new_fcurve.keyframe_points:
                p.interpolation = 'CONSTANT'
            new_fcurve.convert_to_samples(start, end)

        newaction["rna"] = str(rna)
        speaker['_RNA_UI'].update(rna)

        if self.nla_drop:
            # need to override context to use.. cbf'd
            nla_drop(speaker, newaction, 1, self.new_channel_name)

        # testcode TODO
        self.add_to_tweaks(newaction)
        newaction.normalise = 'NONE'
        #tw.type = "COPIED FROM %s" % original_action.name
        return {'FINISHED'}


class UnbakeSoundAction(SoundActionBaseOperator, Operator):
    '''Unbake'''
    bl_idname = 'soundaction.unbake'
    bl_label = 'unBake to Key-frames'
    bl_description = 'Unbake to keyframes'
    bl_options = {'UNDO'}
    sd_tweak_type = 'UNBAKE'
    bake_all = BoolProperty(default=True, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        sp = getSpeaker(context)
        a = getAction(sp)
        samples = [1 for fc in a.fcurves if len(fc.sampled_points)]

        return len(samples)


    def execute(self, context):
        #unbake action
        speaker = getSpeaker(context)
        action = getAction(speaker)
        name = action.name
        print("-" * 72)
        print("Unbake action %s to keyframe points" % name)
        print("-" * 72)
        rna = speaker["_RNA_UI"]
        
        save_fcurve_select = [0] * len(action.fcurves)
        action.fcurves.foreach_get("select", save_fcurve_select)
        #action["max"] = -float("inf")
        #action["min"] = float("inf")
        channel_prefix = action["channel_name"]
        #keys.normalise = 'NONE'
        fcurves = [fc for fc in action.fcurves if len(fc.sampled_points)]
        sp_rna = speaker.get("_RNA_UI").to_dict()
        
        pts = [(fc, [(sp.co[0], fc.evaluate(sp.co[0])) for sp in fc.sampled_points]) for fc in fcurves if fc.select or self.bake_all]
        
        for fcu, fd in pts:
            dp = fcu.data_path
            i = fcu.array_index
            action.fcurves.remove(fcu)
            fc = action.fcurves.new(dp, index=i, action_group=channel_prefix)
            channel_name = dp.strip('["]')
            #fc.keyframe_points.foreach_set("co", [v for c in fd for v in c])
            for p in fd:
                w = fc.keyframe_points.insert(*p)

            is_music = False
            channel_rna = rna[channel_name]
            fc_range, points = fc.minmax
            low = channel_rna['low']
            high = channel_rna['high']
            (_min, _max) = fc_range
            if _min < action["min"]:
                action["min"] = _min
            if _max > action["max"]:
                action["max"] = _max

            set_channel_idprop_rna(channel_name,
                                   rna,
                                   low,
                                   high,
                                   fc_range,
                                   fc_range,
                                   is_music=is_music)

            sp_rna[channel_name] = channel_rna.to_dict()
            print("%4s %8s %8s %10.4f %10.4f" %\
                      (channel_name,\
                       f(low),\
                       f(high),\
                       fc_range[0],\
                       fc_range[1]))
        
        action['rna'] = str(sp_rna)
        action.normalise = 'NONE'
        action.fcurves.foreach_set("select", save_fcurve_select)
        #replace_speaker_action(speaker, action, keys)
        self.add_to_tweaks(speaker.animation_data.action)
        return{'FINISHED'}

class ReBakeSoundAction(SoundActionBaseOperator, Operator):
    bl_idname = 'soundaction.rebake'
    bl_label = 'ReBake to Samples'
    bl_description = 'Resample baked f-curve to a new Action / f-curve'
    bl_options = {'UNDO'}
    sd_tweak_type = 'REBAKE'
    bake_all = BoolProperty(default=True, options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        sp = getSpeaker(context)
        a = getAction(sp)
        kfps = [1 for fc in a.fcurves if len(fc.keyframe_points)]

        return len(kfps)

    def finished(self, context):
        return {'FINISHED'}

    def execute(self, context):
        # rebake action using modifiers
        scene = context.scene
        speaker = getSpeaker(context)
        action = getAction(speaker)
        name = action.name
        print("-" * 72)
        print("Rebake  action %s to sampled points" % name)
        print("-" * 72)
        rna = speaker["_RNA_UI"]
        sp_rna = {}
        pts = [(c, [(sp.co[0], c.evaluate(sp.co[0])) for sp in c.keyframe_points]) for c in action.fcurves if c.select or self.bake_all]
        action.normalise = 'NONE'
        action["max"] = -float("inf")
        action["min"] = float("inf")

        start, end = action.frame_range[0], action.frame_range[1]

        for fc, sam in pts:
            
            #if self.RGB: fcu.color_mode = 'AUTO_RGB'
            
            for i, p in enumerate(sam):
                frame, v = p
                fc.keyframe_points[i].co.y = v
            
            fc.keyframe_points.update()

            channel_name = fc.data_path.strip('["]')
            
            is_music = False
            fc_range, points = fc.minmax
            low = rna[channel_name]['low']
            high = rna[channel_name]['high']
            (_min, _max) = fc_range
            if _min < action["min"]:
                action["min"] = _min
            if _max > action["max"]:
                action["max"] = _max

            set_channel_idprop_rna(channel_name,
                                   rna,
                                   low,
                                   high,
                                   fc_range,
                                   fc_range,
                                   is_music=is_music)
            sp_rna[channel_name] = rna[channel_name].to_dict()
            print("%4s %8s %8s %10.4f %10.4f" % (channel_name, f(low), f(high), fc_range[0], fc_range[1]))
            # ok now bake
            fc.convert_to_samples(start, end)
        
        self.add_to_tweaks(action)

        return{'FINISHED'}

class SD_ReBakeTweak(SoundActionBaseOperator, Operator):
    bl_idname = "soundaction.tweak"
    bl_label = "Tweak"
    bl_options = {'REGISTER', 'UNDO'}
    ''' Pre Bake Clean / Smooth '''
    type=EnumProperty(items = (('CLEAN', 'CLEAN', 'CLEAN'),
                               ('SMOOTH', 'SMOOTH', 'SMOOTH')),
                      default = 'CLEAN',
                      )
    threshold = FloatProperty(default=0.0001, min=0.0001 , max=0.1, step=0.001) 

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "type", expand=True)
        box = layout
        row = box.row()

        #box.seperate()
        if self.type == 'CLEAN':
            box.prop(self, "threshold", slider=True)
            
        #layout.operator("ed.undo_history")
        #layout.operator(self.bl_idname, text="Done")

    def invoke(self, context, event):
        wm = context.window_manager
        if self.type in ['CLEAN']:
            return  wm.invoke_props_dialog(self)
        else:
            return self.execute(context)
        #return  wm.invoke_popup(self)

    def execute(self, context):
        action = getAction(context.scene.speaker)
        c = {}
        graph = get_context_area(context, c, 'GRAPH_EDITOR')
        '''
        c["area"] = graph
        c["screen"] = context.screen
        c["region"] = graph.regions[-1]
        c["window"] = context.window
        c["scene"] = context.scene
        '''
        #hs = action.tweaks.add()
        #hs.type = self.type

        if self.type == 'CLEAN':
            bpy.ops.graph.clean(c, threshold=self.threshold)
            print("clean")
            #hs.threshold = self.threshold

        elif self.type == 'SMOOTH':
            bpy.ops.graph.smooth(c)
            print("smooth")

        self.sd_tweak_type = self.type
        self.add_to_tweaks(action)
        return {'FINISHED'}

class SoundActionMethods:
    icons = ['BLANK1', 'CHECKBOX_DEHLT', 'MESH_PLANE', 'OUTLINER_OB_LATTICE']
    icontable = []
    vismode = 'NONE'

    @classmethod
    def poll(cls, context):

        if not hasattr(context, "speaker"):
            return False

        speaker = getSpeaker(context)
        action = getAction(speaker)

        return (context.speaker and speaker and action\
                and cls.vismode in speaker.vismode)

    def drawnormalise(self, context):
        layout = self.layout
        action = getAction(getSpeaker(context))
        row = layout.row(align=True)
        row.prop(action, "normalise", expand=True)
        row = layout.row()
        row.scale_y = row.scale_x = 0.5
        row.label("min: %6.2f" % action["min"])
        row.label("max: %6.2f" % action["max"])
        sub = layout.row()
        sub.enabled = action.normalise != 'NONE'
        sub.prop(action, "normalise_range", text="", expand=True)
        return

    def draw_tweaks(self, layout, context):

        scene = context.scene

        # Create a simple row.

        row = layout.row()
        '''
        row.context_pointer_set("scene", context.scene)
        row.context_pointer_set("area", context.screen.areas[0])
        row.context_pointer_set("window", context.window)
        row.context_pointer_set("screen", context.screen)
        row.context_pointer_set("region", context.screen.areas[0].regions[-1])
        op = row.operator("graph.clean")
        '''
        op = row.operator("soundaction.tweak", text="CLEAN")
        op.type = 'CLEAN'
        op = row.operator("soundaction.tweak", text="SMOOTH")
        op.type = 'SMOOTH'
        
        row = layout.row()
        #row.prop(op, "threshold")
        action = getAction(context.scene.speaker)
        for xx in action.tweaks:
            row = layout.row()
            row.label("[%s] %s " % (xx.channel_name, xx.type))

            #row.label("%.4f" % xx.threshold)
            row.label("%d" % xx.fcurve_count)
            row.label("%d" % xx.samples_count)
            row.label("%d" % xx.keyframe_count)
                    
    def nla_tracks(self, context):
        layout = self.layout
        speaker = getSpeaker(context)

        row = layout.row()
        if not getattr(speaker, "animation_data", None):
            row.label("NO ANITION DATA", icon='ERROR')
            return None
        row.prop(speaker.animation_data, "use_nla", toggle=True)
        if not speaker.animation_data.use_nla:
            return None
        l = len(speaker.animation_data.nla_tracks) - 1
        for i in range(l):
            nla_track = speaker.animation_data.nla_tracks[l - i]
            # need to fix for only strips with soundactions.. for R'ON
            row = layout.row()
            row = layout.row(align=True)
            for strip in nla_track.strips:
                action = strip.action
                ch = action.get("channel_name")
                if ch is None:
                    continue
                sub = row.row()
                sub.alignment = 'LEFT'
                op = sub.operator("soundaction.change", text=ch)
                op.action = strip.action.name
                sub.enabled = action != speaker.animation_data.action

                #sub.label(strip.action["channel_name"])
                if not nla_track.mute:
                    icon = "MUTE_IPO_OFF"
                else:
                    icon = "MUTE_IPO_ON"
                row.prop(action, "normalise_range", text="", expand=True)
                row.prop(nla_track, "mute",  icon=icon,
                         text="", icon_only=True)

    def copy_action(self, context):
        speaker = getSpeaker(context)
        sound = speaker.sound
        bakeoptions = sound.bakeoptions
        scene = context.scene
        layout = self.layout
        row = layout.row(align=True)
        sub = row.row()
        sub.scale_x = 2

        channels = [c for sp in scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        new_channel_name = unique_name(channels, bakeoptions.channel_name)
        op = sub.operator("soundaction.copy", text="Copy to Channel %s" % new_channel_name)
        op.new_channel_name = new_channel_name
        col = layout.column()
        col.operator_context = 'INVOKE_DEFAULT'
        op = col.operator("soundaction.copy_to_switches")

        '''
        row = layout.row()
        op = row.operator("sound.bake_animation")
        row = layout.column()
        row.prop(scene, "sync_mode", expand=True)
        '''
        return

    def FCurveSliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]

        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column_flow(columns=1)
        #cf.scale_y = action["row_height"]
        fcurves = action.fcurves
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            v = speaker[channel]
            MIN = speaker["_RNA_UI"][channel]['min']
            MAX = speaker["_RNA_UI"][channel]['max']
            diff = MAX - MIN
            pc = 0.0
            if diff > 0.0000001:
                pc = (v - MIN) / diff
            #row = cf.row()
            #row.scale_y = action["row_height"]
            if pc < 0.00001:
                split = cf.split(percentage=0.0001)
                split.scale_y = action["row_height"]
                split.label("")
                continue
            split = cf.split(percentage=pc)
            split.scale_y = action["row_height"]
            split.prop(fcurves[i], "color", text="")
        row = box.row()
        row.scale_y = 0.2
        row.label(icon='BLANK1')

    def ColSliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]
        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column()
        cf.scale_y = action["row_height"]
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            cf.prop(speaker, '["%s"]' % channel, slider=True,
                       emboss=True, text="")

    def Sliders(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not (action and speaker):
            return None

        channel_name = action["channel_name"]
        start = action["start"]
        end = action["end"]
        box = layout.box()
        #row  = box.row()
        #box.scale_y = 0.4
        cf = box.column_flow(columns=1)
        cf.scale_y = action["row_height"]
        for i in range(start, end + 1):
            channel = "%s%d" % (channel_name, i)
            # TODO ADDED with MIDI
            if channel not in speaker.keys():
                continue
            cf.prop(speaker, '["%s"]' % channel, slider=True,
                       emboss=True, text="")

    def EBT(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        # max and min of whole action

        def icon(ch, pc):
            cn = action["channel_name"]
            chi = "%s%d" % (cn, ch)
            mn = speaker['_RNA_UI'][chi]["min"]
            mx = speaker['_RNA_UI'][chi]["max"]
            vol_range = Vector((mx, mn)).magnitude
            mx = max(mn, mx)
            b = speaker['_RNA_UI'][chi]["b"]
            a = speaker['_RNA_UI'][chi]["a"]
            map_range = Vector((a, b)).magnitude
            v = map_range * abs(speaker[chi]) / vol_range

            o = 0  # no output
            if v >= vol_range * pc:
                o = 3
            elif  pc * vol_range < (abs(map_range)):
                o = 1
                #return 'CHECKBOX_DEHLT'
            return o

        # create a list channels x 10
        channels = action["Channels"]
        #row = layout.row()

        self.icontable = [[icon(j, (i + 1) / 20.0)
                           for i in range(20)]
                          for j in range(channels)]
        for l in self.icontable:
            i = l.count(3)
            if i:
                l[i - 1] = 2
        '''
        # horizontal
        cf = self.column_flow(columns=10, align=True)
        cf.scale_y = 0.4
        for i in range(10):
            for j in range(channels):
                cf.label(text='', icon=icontable[j][i])
        '''
        row = layout.box()
        row.scale_x = 0.5

        #row = row.row()
        cf = row.column_flow(columns=channels + 1)
        cf.scale_y = action["row_height"]
        cf.scale_x = action["row_height"]

        for j in range(channels + 1):
            if j == channels:
                for i in range(19, -1, -1):
                    cf.label("")
                continue
            for i in range(19, -1, -1):
                #col.label(text='', icon=self.icons[self.icontable[j][i]])
                cf.label(text='', icon=self.icons[self.icontable[j][i]])

# XXXX

class DataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return getattr(context, "speaker", None) is not None\
               and getSpeaker(context) is not None


class OLDSoundVisualiserPanel(DataButtonsPanel, bpy.types.Panel):
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    #bl_space_type = "GRAPH_EDITOR"
    #bl_region_type = "UI"
    driver_index = 0

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        layout.menu("soundtest.menu", text="Select Sound Action", icon='SOUND')

    def drawvisenum(self, context):
        speaker = getSpeaker(context)
        layout = self.layout
        row = layout.row()
        row.prop(speaker, 'vismode', expand=True, icon_only=True)

    def drawcontextspeaker(self, context):
        layout = self.layout
        ob = context.active_object
        speaker = getSpeaker(context)

        space = context.space_data
        row = layout.row(align=True)

        if not space.pin_id:
            row.template_ID(ob, "data")
        else:
            row.template_ID(space, "pin_id")

        if speaker.sound is not None:
            row = layout.row(align=True)
            sub = row.row()
            sub.alignment = 'LEFT'
            #use solo icon to show speaker has context
            if speaker.is_context_speaker:
                sub.prop(speaker, "is_context_speaker",
                         icon='SOLO_ON', text="", emboss=False)
            else:
                sub.prop(speaker, "is_context_speaker",
                         icon='SOLO_OFF', text="", emboss=False)

            row.label(speaker.sound.name)

    def draw(self, context):
        layout = self.layout
        sce = context.scene
        space = context.space_data
        speaker = getSpeaker(context)
        '''
        # Call menu executes the operator...
        row = layout.row()
        row.operator("wm.call_menu").name="speaker.preset_menu"
        row = layout.row()
        row.menu("speaker.preset_menu")

        '''
        nla = False
        action = None
        frame = sce.frame_current
        self.drawvisenum(context)
        '''
        if speaker.vismode == 'BAKE':
            return None
        '''
        self.drawcontextspeaker(context)

        return
        '''

            elif speaker.vismode == 'LIPSYNC':
                bpy.types.SoundTools_LipSync_PT.draw(self, context)
            #print("ACTION",action)
            #timemarkers = ['rest']

        '''


def test(self, context):
    if self.save_preset:
        if len(self.preset) == 0:
            self.save_preset = False
    return None


class DriverMenu(bpy.types.Menu):
    bl_idname = "sound_drivers.driver_menu"
    bl_label = "Select a Driver"

    def draw(self, context):
        pass

def action_normalise_set(self, context):
    # add normal envelope
    '''
    NONE : No normalisation  # all modifiers off
    ACTION: Normalised to ACTION  always modifier 0
    CHANNEL: Normalised to CHANNEL  always modifier 1
             (Note could make this
             one use previous, and factor or TOGGLE)
    '''
    scene = context.scene
    speaker = getSpeaker(context, action=self)
    # boo (bakeoptions) change. Add if doesn't exist.
    if "boo" not in self.keys():
        # set to default.
        self["boo"] = 'SOUND'
    if speaker is None:
        print("SPEAKER IS NONE")
        return None
    speaker_rna = self.get('rna')
    speaker_rna = eval(speaker_rna)

    def add_normal_envelope(fcurve, type):
        '''
        mods = [m for m in fcurve.modifiers if m.type == 'ENVELOPE']
        # remove mods (shouldn't be any)
        for m in mods:
            fcurve.modifiers.remove(m)
        '''
        m = fcurve.modifiers.new(type='ENVELOPE')
        # add a control point at start end
        for f in self.frame_range:
            cp = m.control_points.add(f)
            cp.min = self.normalise_range[0]
            cp.max = self.normalise_range[1]
        m.mute = True
        m.show_expanded = False
        return m

    def set_modifiers(type='ENVELOPE'):
        scene = context.scene
        #speaker = getSpeaker(context)
        for f in self.fcurves:
            channel = f.data_path.strip('[""]')
            touched = False
            while len(f.modifiers) < 2:
            # add muted envelope modifiers
                add_normal_envelope(f, type='ENVELOPE')
                touched = True
            for i, m in enumerate(f.modifiers):
                m.mute = True
                if self.normalise == 'NONE':
                    continue
                m.reference_value = 0.0
                m.default_min = self["min"]\
                                if not i else speaker_rna[channel]["min"]
                m.default_max = self["max"]\
                                if not i else speaker_rna[channel]["max"]

            low = speaker_rna[channel]["low"]
            high = speaker_rna[channel]["high"]
            sp_rna = speaker['_RNA_UI']

            map_range = Vector((self['min'], self['max']))
            if self.normalise == 'NONE':
                fc_range = Vector((speaker_rna[channel]['a'],
                                  speaker_rna[channel]['b']))
                '''
                speaker['_RNA_UI'][channel] = speaker_rna[channel]
                speaker['_RNA_UI']['a'] = self['min']
                speaker['_RNA_UI']['b'] = self['max']
                '''
                pass
            else:
                # could use the mods ID prop to get indexes
                if self.normalise == 'ACTION':
                    m = f.modifiers[0]
                    b = Vector(self.normalise_range).magnitude
                    fc_range = Vector((speaker_rna[channel]['a'],
                                      speaker_rna[channel]['b']))
                    a = map_range.magnitude
                    fc_range *= b / a
                    map_range = Vector(self.normalise_range)
                if self.normalise == 'CHANNEL':
                    m = f.modifiers[1]
                    fc_range = map_range = self.normalise_range
                for cp in m.control_points:
                    cp.min = self.normalise_range[0]
                    cp.max = self.normalise_range[1]

                m.mute = False

            set_channel_idprop_rna(channel,
                                   sp_rna,
                                   low,
                                   high,
                                   fc_range,
                                   map_range,
                                   is_music=(self["boo"] == 'MUSIC'))

        # flag the mods are added
        self["mods"] = True

    def change_range(self):
        pass

    def check_range(self):
        '''
        Check Envelope Modifier Range
        '''
        # check range
        if self.normalise_range[0] == self.normalise_range[1]:
            self.normalise_range[1] += 0.0000001
            return None
        if self.normalise_range[0] > self.normalise_range[1]:
            self.normalise_range[0] = self.normalise_range[1]
            return None

        elif self.normalise_range[1] < self.normalise_range[0]:
            self.normalise_range[1] = self.normalise_range[0]
            return None

    if True or not self.get('mods', False):
        set_modifiers(type='EVELOPE')

    #check_range(self)
    #normalise_action(speaker)
    bpy.ops.graph.view_all_with_bgl_graph()
    return None


def defaultPanels(regflag):
    if regflag:
        bpy.utils.register_class(DATA_PT_speaker)
        bpy.utils.register_class(DATA_PT_context_speaker)
        bpy.utils.register_class(DATA_PT_cone)
        bpy.utils.register_class(DATA_PT_distance)
        bpy.utils.register_class(DATA_PT_custom_props_speaker)
    else:
        bpy.utils.unregister_class(DATA_PT_speaker)
        bpy.utils.unregister_class(DATA_PT_context_speaker)
        bpy.utils.unregister_class(DATA_PT_cone)
        bpy.utils.unregister_class(DATA_PT_distance)
        bpy.utils.unregister_class(DATA_PT_custom_props_speaker)


class SoundToolSettings(PropertyGroup):
    show_vis = BoolProperty(default=True, description="Show Visualiser")
    use_filter = BoolProperty(default=False,
                                 description="Filter Drivers")
    filter_object = BoolProperty(default=True,
                                 description="Filter Drivers by Objects")
    filter_context = BoolProperty(default=True,
                                  description="Filter Drivers by Context")
    filter_material = BoolProperty(default=True,
                                   description="Filter Drivers by Material")
    filter_monkey = BoolProperty(default=True,
                                 description="Filter Drivers by New (Monkeys)")
    filter_texture = BoolProperty(default=True,
                                  description="Filter Drivers by Texture")
    filter_world = BoolProperty(default=True,
                                description="Filter Drivers by World")
    filter_speaker = BoolProperty(default=True,
                                description="Filter Drivers by Speaker")
    context_speaker = StringProperty(default="None")


def speaker_channel_buffer(self, context):
    dns = bpy.app.driver_namespace

    #b = dns.get("ST_buffer")
    h = dns.get("ST_handle")
    b = dns["ST_buffer"] = mix_buffer(context)
    if h:
        h.stop()
    return None


class SoundChannels(PropertyGroup):
    name = StringProperty(default="SoundChannels")
    buffered = BoolProperty(default=False, description="Buffered")
    valid_handle = BoolProperty(default=False, description="Has Valid Handle")
    action_name = StringProperty(default="SoundChannels")
    pass

for i in range(96):
    setattr(SoundChannels,
            "channel%02d" % i,
            BoolProperty(default=(i == 0),
                         description="Channel %02d" % i,
                         update=speaker_channel_buffer))


def dummy(self, context):
    return None

    # check for modifiers
    mods = [mod for mod in self.modifiers if not mod.mute and mod.is_valid]
    if len(mods):
        #evaluate at frame
        v = [self.evaluate(p.co[0]) for p in col]
    else:
        #use the value at frame
        v = [p.co[1] for p in col]

    _min = min(v)
    _max = max(v)
    return ((_min, _max), (v.index(_min), v.index(_max)))


def register():
    defaultPanels(False)
    bpy.types.Scene.SoundToolsGUISettings =\
                BoolVectorProperty(name="GUI_Booleans",
                                   size=32,
                                   default=(False for i in range(0, 32)))

    bpy.types.Action.normalise = EnumProperty(items=(
                ('NONE', "None", "No Normalisation (As Baked)", 'BLANK', 0),
                ('CHANNEL', "Channel", "Normalise each CHANNEL", 'BLANK', 1),
                ('ACTION', "Action",
                 "Normalise to Maximumum Channel Value in ACTION", 'ACTION', 2)
                ),
                name="Normalise",
                default="NONE",
                description="Normalise to MIN MAX of Channel or Action",
                update=action_normalise_set,
                options={'HIDDEN'},
                )

    bpy.types.Action.normalise_range = FloatVectorProperty(default=(0, 1),
                                 size=2,
                                 description="Remap Action RANGE",
                                 update=action_normalise_set)

    bpy.types.Action.vismode = EnumProperty(items=(
                ("SLIDER", "Sliders", "Display as Property Sliders"),
                ("VERTICAL", "Whitey",\
                 "Horizontal Icons (Vanishes on high channel count"),
                ("FCURVE", "Fcurve Colors",
                 "Horizontal Display of Fcurve colors")
                ),
                name="Visual Type",
                default="SLIDER",
                description="Visualisation Type",
                options={'HIDDEN'},
                )

    bpy.utils.register_class(SoundChannels)
    #BUGGY on SPEAKER object
    bpy.types.Scene.sound_channels = CollectionProperty(type=SoundChannels)

    bpy.types.Scene.play = BoolProperty("Play",
                default=True,
                description="Play Live")
                #update=dummy)

    bpy.utils.register_class(SoundToolSettings)
    bpy.types.Scene.speaker_tool_settings = \
            PointerProperty(type=SoundToolSettings)

    bpy.types.Action.show_freq = BoolProperty(default=True)
    bpy.utils.register_class(OLDSoundVisualiserPanel)

    register_class(SD_ReBakeTweak)
    register_class(SoundActionPanel)
    #register_class(SoundVisualiserPanel)
    register_class(ChangeSoundAction)
    register_class(CopySoundAction)
    register_class(SoundSwitchAction)
    register_class(UnbakeSoundAction)
    register_class(ReBakeSoundAction)

    bpy.app.handlers.load_post.append(InitSoundTools)
    if ("GetLocals" not in bpy.app.driver_namespace 
            or "SoundDrive" not in bpy.app.driver_namespace):
        InitSoundTools(None)


class SoundActionPanel(SoundActionMethods, Panel):
    bl_label = "Sound Action"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    vismode = 'ACTION'
    #bl_options = {'DEFAULT_CLOSED'}

    def SoundActionMenu(self, context, speaker=None,
                        action=None, has_sound=True):
        speaker = getSpeaker(context)
        action = getAction(speaker)
        layout = self.layout
        if action is None:
            layout.label("NO ACTION", icon='INFO')
            return
        channel_name = action.get("channel_name")
        if channel_name is None:
            return
        row = layout.row(align=True)
        if has_sound:
            sub = row.row()
            sub.alignment = 'LEFT'
            #col.alignment = 'LEFT'
            sub.menu("soundtest.menu", text=channel_name)
            #sub = row.row()
            row.prop(action, "name", text="")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(action, "use_fake_user",
                       toggle=True, text="F")

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='ACTION')

    def draw(self, context):
        layout = self.layout
        layout.enabled = not bpy.types.BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)
        self.SoundActionMenu(context)

        row = layout.row(align=True)
        self.drawnormalise(context)
        self.copy_action(context)
        row = layout.row()
        enabled = getattr(context.active_object, "data", None) == speaker
        if enabled:
            row=layout.row()
            op = row.operator("soundaction.unbake")
            if bpy.ops.soundaction.rebake.poll() :
                col = layout.column()
                self.draw_tweaks(col, context)
            row=layout.row()
            row.operator("soundaction.rebake")
        else:
            row = layout.row()
            row.label("Select Speaker to (un)(re)bake", icon='INFO')


def unregister():
    #del(bpy.types.FCurve.minmax)
    defaultPanels(True)
    unregister_class(SoundChannels)
    unregister_class(SD_ReBakeTweak)
    unregister_class(OLDSoundVisualiserPanel)
    unregister_class(SoundToolSettings)
    unregister_class(ChangeSoundAction)
    unregister_class(CopySoundAction)
    unregister_class(SoundSwitchAction)
    unregister_class(UnbakeSoundAction)
    unregister_class(ReBakeSoundAction)

    #unregister_class(SoundVisualiserPanel)
    bpy.app.handlers.load_post.remove(InitSoundTools)
    dns = bpy.app.driver_namespace
    drivers = ["SoundDrive", "GetLocals", "DriverManager"]
    for d in drivers:
        if d in dns:
            dns.pop(d)
