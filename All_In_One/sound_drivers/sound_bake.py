import bpy
import time
from bpy.types import (Panel, Operator)
from bpy.props import (StringProperty, IntProperty)
from bpy.utils import register_class, unregister_class
from sound_drivers import utils
from sound_drivers import presets # TODO better name for presets
from sound_drivers.screen_panels import ScreenLayoutPanel
from sound_drivers.sound_action import SoundActionBaseOperator

from math import log

class BakeSoundGUIPanel():
    sd_operator = "wm.bake_sound_to_action"
    sd_operator_text = "BAKE"
    action = None
    baking = False
    status = []  # status of each fcurve
    bakeoptions = None
    current = 0
    report = ""
    wait = 0

    def draw_progress_slider(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row()
        row.scale_y = 0.4
        row.prop(wm, '["bake_progress"]', text="", slider=True, emboss=True)
        #WWWW

    def draw_fcurve_slider(self, context):
        layout = self.layout
        action = self.action
        channels = action["Channels"]
        row = layout.row()
        #row.scale_y = 0.5
        if action:
            cf = row.column_flow(columns=channels, align=True)
            cf.scale_y = 0.5
            for i in range(channels):
                fc = action.fcurves[i]
                if not fc.mute:
                    cf.prop(fc, "color", text="")

    def draw_current_fcurve_slider(self, context, i=0):
        channels = len(self.status)
        layout = self.layout
        action = self.action
        row = layout.row()
        if action:
            baked_channels = len([i for i in range(channels)
                                  if self.status[i]])
            pc = (baked_channels / channels)
            fc = action.fcurves[i]
            split = row.split(percentage=pc)
            split.prop(fc, "color", text="")
            split.scale_y = 0.5
            if self.wait:
                row = layout.row()
                tick = self.wait // 4
                if tick < 2:
                    row.label(str(pc), icon='INFO')
                else:
                    row.label(str(pc), icon='ERROR')

class BakeSoundPanel(ScreenLayoutPanel, BakeSoundGUIPanel, Panel):
    bl_label = "Bake Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    sd_operator = "wm.bake_sound_to_action"
    sd_operator_text = "BAKE"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = utils.getSpeaker(context)
        if speaker is not None and 'BAKE' in speaker.vismode:
            return True

        return False

    def draw_area_operator(self, context, layout, index):
        speaker = utils.getSpeaker(context)
        sound = speaker.sound
        op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                             icon='FCURVE')
        op.sound_name = sound.name
        op.speaker_name = speaker.name
        op.area_index = index
        

    def draw_freqs(self, layout, bakeoptions):
        if bakeoptions.sound_type == 'MUSIC':
            layout.label('Note Range (From-To)', icon='SOUND')
            box = layout.box()
            row = box.row()
            row.prop(bakeoptions, "music_start_note", text="")
            row.prop(bakeoptions, "music_end_note", text="")
        else:
            layout.label("Frequencies")
            row = layout.row()
            cbox = row.box()
            crow = cbox.row(align=True)
            sub = crow.row()
            sub.alignment = 'LEFT'
            sub.prop(bakeoptions, "auto_adjust", text="", icon='AUTO')
            crow.prop(bakeoptions, "minf", text="")
            crow.prop(bakeoptions, "maxf", text="")
            sub = crow.row()
            sub.alignment = 'RIGHT'
            sub.scale_x = 0.5
            sub.prop(bakeoptions, "use_log", toggle=True, text="LOG")

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='FCURVE')

    def draw(self, context):
        space = context.space_data
        layout = self.layout

        if self.baking:
            action = self.action
            #self.draw_progress_slider(context)

            row = layout.row()
            row.label("[%s] %s" % (action["channel_name"], action.name), icon='ACTION')
            self.draw_progress_slider(context)
            '''
            if channels > 24:
                i = getattr(self, "channel", 0)
                self.draw_current_fcurve_slider(context, i=i)
            else:
                self.draw_fcurve_slider(context)
            '''
            box = layout.box()
            if len(action.fcurves):
                row = box.row(align=False)
                i = getattr(self, "channel", 0)
                fc = action.fcurves[i]
                sub = row.row()
                sub.alignment = 'LEFT'
                sub.label(fc.data_path.strip('["]'))
                color = [c for c in fc.color]
                color.append(1.0)
                row.label("Baking...")
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.template_node_socket(color=color)

            box = layout.box()

            if len(self.bake_times):
                row = box.row(align=False)
                i = getattr(self, "channel", 0)
                fc = action.fcurves[i]
                sub = row.row()
                sub.alignment = 'LEFT'
                sub.label(fc.data_path.strip('["]'))
                color = [c for c in fc.color]
                color.append(1.0)
                row.label("Baked")
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.template_node_socket(color=color)
                row = box.row(align=False)
                row.label(BakeSoundPanel.report)
                row = box.row()
                row.label("Baked in: %02d:%02d.%02d" % utils.splittime(self.bake_times[-1]))
                row = box.row()
                te = sum(self.bake_times)
                abt = te / len(self.bake_times)
                channels = self.action.get("Channels", 0)
                tr = (channels - len(self.bake_times)) * abt

                row.label("Elapsed: %02d:%02d.%02d" % utils.splittime(te))
                row.label("Remaining: %02d:%02d.%02d" % utils.splittime(tr))
            #row.column_flow(columns=10, align=True)

            return None


        speaker = utils.getSpeaker(context)
        sound = speaker.sound

        if sound is None:
            row = layout.row()
            row.label("No Sound to Bake", icon='INFO')
            return None

        scene = context.scene

        bakeoptions = sound.bakeoptions
        bake_operator = bakeoptions.bake_operator

        # Settings for bake sound to fcurve Operator
        if not self.baking:
            areas = [a.type for a in context.screen.areas]
            if 'GRAPH_EDITOR' in areas:
                area_index = areas.index('GRAPH_EDITOR')
                op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                                icon='FCURVE')
                op.area_index = area_index
                op.sound_name = sound.name
                op.speaker_name = speaker.name
    
            elif len(areas) > 1:
                self.draw_area_buttons(context)
            else:
                op = layout.operator("wm.bake_sound_to_action", text="BAKE",
                                icon='FCURVE')
    
                op.sound_name = sound.name
                op.speaker_name = speaker.name

        ### TEST FOR SQUIZ
        action = None
        channels = 0
        if speaker.animation_data:
            action = speaker.animation_data.action
            if action is not None:
                channels = action["Channels"]


        #row.operator(self.bl_idname).preset = "FOOBAR"
        row = layout.row()
        
        col = layout.column_flow(align=True)
        col.label("Bake Options")
        row = col.row(align=True)
        row.menu("speaker.preset_menu",
                 text=getattr(bpy.types, "speaker.preset_menu").bl_label)
        row.operator("wm.soundtool_operator_preset_add", text="", icon='ZOOMIN')
        row.operator("wm.soundtool_operator_preset_add", text="", icon='ZOOMOUT').remove_active = True
        
        
        #row.prop(bakeoptions, "show_graph_editor", toggle=True, emboss=True)
        '''
        preset_box = row.box()
        row = preset_box.row()
        if len(bakeoptions.preset) == 0:
            txt = "Select Preset"
        else:
            txt = bakeoptions.preset
        row.menu("speaker.preset_menu", text=txt)
        row = preset_box.row()
        #row.prop(bakeoptions, "save_preset")
        preset_row = preset_box.row()
        preset_row.prop(bakeoptions, "preset")
        row = layout.row()
        row.menu("sound.music_notes")
        '''
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        channel_name = utils.unique_name(channels, "AA")
        row = layout.row()
        row.label("%s_%s_%s" % (bakeoptions.sound_type, channel_name, sound.name), icon='ACTION')
        abox = layout.box()
        arow = abox.row(align=True)
        arow.prop(bakeoptions, "sound_type", text="")

        arow.label(channel_name)
        #arow.prop(bakeoptions, "channel_name", text="")
        arow.label(sound.name)
        #arow.prop(bakeoptions, "action_name", text="") # REFACTO OUT

        row = layout.row()
        '''
        if not validate_channel_name(context):
            row.label("Channel in USE or INVALID", icon='ERROR')
            row.alert = True
            row = layout.row()

        '''
        #col.scale_x = row.scale_y = 2

        row.label("Channel")
        row = layout.row()
        box = row.box()
        #col.scale_x = row.scale_y = 2
        brow = box.row(align=True)
        #brow.prop(bakeoptions, "channel_name", text="Name")
        sub = brow.row()
        sub.prop(bakeoptions, "channels", text="")
        sub.enabled = bakeoptions.sound_type != 'MUSIC'
        row = layout.row()

        self.draw_freqs(layout, bakeoptions)
        row = layout.row()

        row.label("Bake Sound to F-Curves", icon='IPO')
        box = layout.box()
        #box.operator("graph.sound_bake", icon='IPO')
        box.prop(bake_operator, "threshold")
        box.prop(bake_operator, "release")
        box.prop(bake_operator, 'attack')
        box.prop(bake_operator, "use_additive", icon="PLUS")
        box.prop(bake_operator, "use_accumulate", icon="PLUS")

        row = box.row()

        split = row.split(percentage=0.20)
        split.prop(bake_operator, "use_square")
        split.prop(bake_operator, "sthreshold")
        #layout.prop(self, "TOL")

class SD_CancelBakeOperator(Operator):
    """Cancel Baking"""
    bl_idname = "sounddrivers.cancel_baking"
    bl_label = "Cancel"

    def execute(self, context):
        #from sound_drivers.sound_bake import BakeSoundPanel
        BakeSoundPanel.cancel_baking = True
        return {'FINISHED'}

class BakeSoundAction(SoundActionBaseOperator, Operator):
    """Bake Multiple Sound Frequencies to Action"""
    bl_idname = "wm.bake_sound_to_action"
    bl_label = "Bake Sound"
    bl_options = {'INTERNAL'}
    sd_tweak_type = 'BAKE'

    _timer = None
    speaker_name = StringProperty(name="Speaker", default="Speaker")
    sound_name = StringProperty(name="Speaker", default="Sound")
    area_index = IntProperty(default=-1, options={'SKIP_SAVE'})
    count = 0
    channels = 0
    fp = None
    c = {}
    context_override = False
    baking = False
    baked = False
    sound = None
    speaker = None
    graph = None
    view3d = None
    _view3d = "VIEW_3D"
    change_last = False
    bakeorder = []
    #bake_times = []
    retries = []  # add channel here if it has no range.
    cancel_baking = False

    @classmethod
    def poll(cls, context):
        
        if getattr(context.space_data, "pin_id", None) is not None and context.space_data.pin_id != context.scene.objects.active.data:
            return False
        return True

    def channel_range(self):
        bakeoptions = self.sound.bakeoptions

        # get the channel
        channel = self.bakeorder[self.count]
        channels = bakeoptions.channels
        if bakeoptions.sound_type == 'MUSIC':
            return presets.freq_ranges(bakeoptions.music_start_note,\
                               bakeoptions.music_end_note)[channel]

        if bakeoptions.use_log:
            # 0Hz is silence? shouldn't get thru trap anyway
            if bakeoptions.minf == 0:
                bakeoptions.minf = 1
            LOW = log(bakeoptions.minf, bakeoptions.log_base)
            HIGH = log(bakeoptions.maxf, bakeoptions.log_base)
            RANGE = HIGH - LOW
            low = LOW + (channel) * RANGE / channels
            high = LOW + (channel + 1) * RANGE / channels
            low = bakeoptions.log_base ** low
            high = bakeoptions.log_base ** high

        else:
            LOW = bakeoptions.minf
            HIGH = bakeoptions.maxf
            RANGE = HIGH - LOW
            low = LOW + (channel) * RANGE / channels
            high = LOW + (channel + 1) * RANGE / channels

        return (low, high)


    def modal(self, context, event):
        if getattr(context, "area", None):
            context.area.tag_redraw()
        wm = context.window_manager

        '''
        if BakeSoundPanel.wait > 0:
            debug.print("waiting", BakeSoundPanel.wait)
        '''

        def confirm_cancel(self, context):
            layout = self.layout
            layout.operator("sounddrivers.cancel_baking")
            layout.operator("sounddrivers.continue_baking")
        
        if BakeSoundPanel.cancel_baking:
            self.clean()
            return self.cancel(context)

        BakeSoundPanel.baking = True

        bakeoptions = self.sound.bakeoptions
        channels = bakeoptions.channels
        bake_operator = bakeoptions.bake_operator
        sound = self.sound
        speaker = self.speaker
        action = speaker.animation_data.action
        
        if event.type == 'ESC' or not BakeSoundPanel.baking:
            context.window_manager.popup_menu(confirm_cancel, title="Baking", icon='SOUND')
            BakeSoundPanel.wait = 1000000
            return {'PASS_THROUGH'}
            self.clean()
            return self.cancel(context)

        if BakeSoundPanel.wait > 0:
            BakeSoundPanel.wait -= 1
            return {'PASS_THROUGH'}

        if  self.count >= bakeoptions.channels:
            # Success do PostPro
            # return {'PASS_THROUGH'}
            return self.finished(context)

        if self.baking:
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            if self.baking:
                return {'PASS_THROUGH'}
            #context.scene.frame_set(1)
            self.baking = True
            fc = action.fcurves[self.bakeorder[self.count]]

            channel = self.bakeorder[self.count]
            wm["bake_progress"] = 100 * self.count / channels
            setattr(BakeSoundPanel, "channel", channel)
            BakeSoundPanel.report = "[%s%d]" % (bakeoptions.channel_name,
                                                      channel)

            fc.select = True
            #FIXME FIXME FIXME
            fp = bpy.path.abspath(sound.filepath)
            low, high = self.channel_range()
            if not self.context_override or not self.graph:
                context.area.type = 'GRAPH_EDITOR'
                context.area.spaces.active.mode = 'FCURVES'
                self.c = context.copy()

            context.scene.frame_set(1)
            #context.area.type = 'GRAPH_EDITOR'

            t0 = time.clock()
            try:
                #x = bpy.ops.graph.sound_bake(

                x = bpy.ops.graph.sound_bake(self.c,
                             filepath=fp,
                             low=low,
                             high=high,
                             attack=bake_operator.attack,
                             release=bake_operator.release,
                             threshold=bake_operator.threshold,
                             use_accumulate=bake_operator.use_accumulate,
                             use_additive=bake_operator.use_additive,
                             use_square=bake_operator.use_square,
                             sthreshold=bake_operator.sthreshold)
            except:
                print("ERROR IN BAKE OP")
                '''
                for k in self.c.keys():
                    print(k, ":", self.c[k])

                '''
                return self.cancel(context)

            '''
            if self.graph:
                #bpy.ops.graph.view_all(self.c)
                bpy.ops.graph.view_all_with_bgl_graph()
            '''

            context.area.type = 'PROPERTIES'
            t1 = time.clock()
            BakeSoundPanel.bake_times.append(t1 - t0)

            fc_range, points = fc.minmax
            vol_range = abs(fc_range[1] - fc_range[0])
            # FIXME make retry count an addon var.
            if self.retries.count(channel) > channels // 5:
                print("TOO MANY RETRIES")
                self.clean()
                return self.cancel(context)
            if bakeoptions.auto_adjust\
                and (vol_range < 0.0001 or vol_range > 1e10):
                print("NO RANGE", vol_range)
                self.retries.append(channel)
                BakeSoundPanel.status[channel] = 99
                if channel == 0:
                    BakeSoundPanel.report = "[%s%d] NO Lo RANGE.. adjusting" \
                    % (bakeoptions.channel_name, channel)
                    bakeoptions.minf = high
                elif channel == (bakeoptions.channels - 1):
                    BakeSoundPanel.report = "[%s%d] NO Hi RANGE .. adjusting" \
                                       % (bakeoptions.channel_name, channel)
                    self.change_last == True
                    bakeoptions.maxf = low
                else:
                    BakeSoundPanel.wait = 20  # wait 2 seconds to continue
                    BakeSoundPanel.report = "[%s%d] NO Mid RANGE\
                            .. continuing" % (bakeoptions.channel_name,\
                                                      channel)
                    self.count += 1
                    bpy.ops.graph.view_all_with_bgl_graph()
                #need to set count down one
            else:
                BakeSoundPanel.status[channel] = 1
                # set up the rna
                rna = speaker["_RNA_UI"]
                channel_name = "%s%d" % (bakeoptions.channel_name, channel)

                is_music = bakeoptions.sound_type == 'MUSIC'
                utils.set_channel_idprop_rna(channel_name,
                                       rna,
                                       low,
                                       high,
                                       fc_range,
                                       fc_range,
                                       is_music=is_music)

                print("%4s %8s %8s %10.4f %10.4f" %\
                          (channel_name,\
                           utils.f(low),\
                           utils.f(high),\
                           fc_range[0],\
                           fc_range[1]),\
                           end="")
                print(" %02d:%02d:%02d" % (utils.splittime(t1 - t0)))
                BakeSoundPanel.report = rna[channel_name]["description"]\
                        .replace("Frequency", "")
                if channel == (bakeoptions.channels - 1)\
                        and self.change_last:
                    self.change_last = False
                    action.fcurves[0].mute = True
                    bakeorder[0], bakeorder[channels - 1] =\
                            bakeorder[channels - 1], bakeorder[0]
                    # need to swap n clear first fcurve
                    # mute the first fcurve
                _min, _max = fc_range
                if _min < action["min"]:
                    action["min"] = _min
                if _max > action["max"]:
                    action["max"] = _max
                self.count += 1

            fc.mute = not bool(BakeSoundPanel.status[channel])
            fc.select = False
            self.baking = False
            self.baked = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        
        BakeSoundPanel.bake_times = []
        wm = context.window_manager
        wm_rnaui = wm.get("_RNA_UI")
        if wm_rnaui is None:
            wm_rnaui = wm["_RNA_UI"] = {}
            wm["_RNA_UI"]["bake_progress"] = {
                                              "min": 0.0,
                                              "soft_min":0.0,
                                              "hard_min":0.0,
                                              "soft_max":100.0,
                                              "hard_max":100.0,
                                              "max":100.0,
                                              "description": "Baking....",
                                              }
        wm["bake_progress"] = 0.0
        BakeSoundPanel.cancel_baking = False
        self.speaker = bpy.data.speakers.get(self.speaker_name)
        self.c = context.copy()
        self.first_baked = False
        self.last_baked = False
        self.sound = bpy.data.sounds.get(self.sound_name)
        if not (self.sound and self.speaker):
            return {'CANCELLED'}
        bakeoptions = self.sound.bakeoptions
        channels = [c for sp in context.scene.objects if sp.type == 'SPEAKER' for c in sp.data.channels]
        bakeoptions.channel_name = utils.unique_name(channels, "AA") # AAAA
        self.retries = []

        if self.area_index > -1:
            '''
            self.view3d = get_context_area(context, {}, 'VIEW_3D',
                                  context_screen=True)
            '''
            self.view3d = context.screen.areas[self.area_index]
            self._view3d = self.view3d.type
            if self.view3d is not None:
                self.view3d.type = 'GRAPH_EDITOR'

        # NEEDS REFACTO to get BGL Graph Area if there is one
        self.graph = utils.get_context_area(context,
                              self.c,
                              'GRAPH_EDITOR',
                              context_screen=(self.area_index != -1))

        self.context_override = self.graph is not None\
                and self.graph.spaces.active.mode != 'DRIVERS'

        if "_RNA_UI" not in self.speaker.keys():
            self.speaker["_RNA_UI"] = dict()

        context.scene.frame_set(1)
        channels = bakeoptions.channels

        # Create the action # might move this to see if one channel baked
        current_action = None
        if not self.speaker.animation_data:
            self.speaker.animation_data_create()
        elif self.speaker.animation_data.action:
            current_action = self.speaker.animation_data.action

        name = "%s_%s_%s" % (bakeoptions.sound_type, bakeoptions.channel_name, self.sound.name)

        action = bpy.data.actions.new(name)

        if current_action:
            #take some settings from last baked
            action.vismode = current_action.vismode

        action["Channels"] = channels
        action["channel_name"] = bakeoptions.channel_name
        action["minf"] = bakeoptions.minf
        action["maxf"] = bakeoptions.maxf
        action["use_log"] = bakeoptions.use_log
        action["wavfile"] = self.sound.name
        action["min"] = 1000000
        action["max"] = -1000000
        action["start"] = 0
        action["end"] = channels - 1

        #keep some UI stuff here too like the row height of each channel

        # use 0.4 as a default value
        action["row_height"] = 0.4
        action_rna = {}
        action_rna["row_height"] = {"min": 0.001,
                                    "max": 1.0,
                                    "description": "Alter the row height",
                                    "soft_min": 0.0,
                                    "soft_max": 1.0}
        action_rna["start"] = {"min": 0,
                               "max": 1.0,
                               "description": "Clip Start",
                               "soft_min": 0,
                               "soft_max": channels - 1}
        action_rna["end"] = {"min": 1,
                             "max": channels - 1,
                             "description": "Clip End",
                             "soft_min": 1,
                             "soft_max": channels - 1}

        action["_RNA_UI"] = action_rna
        #action["rna"] = str(action_rna)
        # set up the fcurves
        BakeSoundPanel.action = action
        BakeSoundPanel.wait = 0
        BakeSoundPanel.status = [0 for i in range(channels)]
        for i in range(channels):
            p = "%s%d" % (bakeoptions.channel_name, i)
            self.speaker[p] = 0.0
            fc = action.fcurves.new('["%s"]' % p, action_group=bakeoptions.channel_name)
            fc.select = False
            fc.mute = True

        bakeorder = [i for i in range(channels)]
        if channels > 1:
            bakeorder[1], bakeorder[channels - 1] = bakeorder[channels - 1],\
                                                    bakeorder[1]
        self.bakeorder = bakeorder

        self.speaker.animation_data.action = action
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        self.wait = 30
        print("-" * 80)
        print("BAKING %s to action %s" % (self.sound.name, action.name))
        print("-" * 80)

        return {'RUNNING_MODAL'}

    def finished(self, context):
        # return to view3d

        if self.view3d is not None:
            self.view3d.type = self._view3d
        print("TOTAL BAKE TIME: %02d:%02d:%02d" %
                  utils.splittime(sum(BakeSoundPanel.bake_times)))
        BakeSoundPanel.report = "Finished Baking"
        #context.area.header_text_set()
        # set up the rnas
        sp = self.speaker
        sound = self.sound
        action = sp.animation_data.action
        bakeoptions = sound.bakeoptions
        boo = bakeoptions.bake_operator
        # save non defaults to an ID prop.

        action['boo'] = bakeoptions.sound_type

        action['_RNA_UI']['boo'] = dict(boo.items())

        channel_name = action['channel_name']
        vcns = ["%s%d" % (channel_name, i) for i in
                range(bakeoptions.channels)]

        sp_rna = {k: sp['_RNA_UI'][k].to_dict()
                  for k in sp['_RNA_UI'].keys()
                  if k in vcns}

        action['rna'] = str(sp_rna)

        BakeSoundPanel.baking = False
        # drop the action into the NLA
        utils.nla_drop(sp, action, 1, "%s %s" %(channel_name, channel_name))
        # normalise to action. This will set the
        action.normalise = 'ACTION'

        if context.scene.speaker is None:
            sp.is_context_speaker = True

        context.window_manager.event_timer_remove(self._timer)
        bpy.ops.graph.view_all_with_bgl_graph()
        self.add_to_tweaks(action)
        return {'FINISHED'}

    def clean(self):
        speaker = self.speaker
        action = speaker.animation_data.action
        if action:
            speaker.animation_data.action = None
            del(action["wavfile"])
            del(action["channel_name"])
            del(action["Channels"])
            for t in speaker.animation_data.nla_tracks:
                for s in t.strips:
                    if s.action == action:
                        #remove track
                        speaker.animation_data.nla_tracks.remove(t)
                        break
            if not action.users:
                bpy.data.actions.remove(action)

    def cancel(self, context):
        if self.view3d is not None:
            #self._view3d = self.view3d.type
            self.view3d.type = self._view3d

        BakeSoundPanel.report = "User Cancelled Cleaning..."
        BakeSoundPanel.baking = False
        
        #context.area.header_text_set()
        context.window_manager.event_timer_remove(self._timer)
        print("BAKING CANCELLED.")
        return {'CANCELLED'}

class SD_ContinueBakeOperator(Operator):
    """Continue Baking"""
    bl_idname = "sounddrivers.continue_baking"
    bl_label = "Continue"

    def execute(self, context):
        from sound_drivers.sound_bake import BakeSoundPanel
        BakeSoundPanel.wait = 2
        BakeSoundPanel.cancel_baking = False
        return {'FINISHED'}

def register():
    register_class(BakeSoundPanel)
    register_class(BakeSoundAction)
    register_class(SD_CancelBakeOperator)
    register_class(SD_ContinueBakeOperator)

def unregister():
    unregister_class(BakeSoundPanel)
    unregister_class(BakeSoundAction)
    register_class(SD_CancelBakeOperator)
    register_class(SD_ContinueBakeOperator)
