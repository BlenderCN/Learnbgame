#VSE Quick Functions
#
#
#Features that this script includes:
#
#Quickfades -
#   Can be found in the sequence editor properties panel, or by pressing the
#        'f' key over the sequencer.
#   Fade Length - The target length for fade editing or creating.
#   Set Fadein/Set Fadeout - Allows easy adding, detecting and changing of
#       fade in/out.  The script will check the curve for any fades already
#       applied to the clip (either manually or by the script), and edit them
#        if found.  Can apply the same fade to multiple clips at once.
#   Transition Type - Selects the type of transition for adding.
#   Crossfade Prev/Next Clip - Allows easy adding of transitions between clips.
#       Will simply find an overlapping clip from the active clip and add
#       a transition.
#   Smart Cross to Prev/Next - Adjust the length of the active clip and the
#       next clip to create a transition of the target fade length.  Will also
#       attempt to avoid extending the clips past their end points if possible.
#
#Quicksnaps -
#   Can be found in the sequence editor 'Strip' menu, or by pressing the
#       's' key over the sequencer.
#   Allows quickly snapping clips to each other or moving the cursor to clips.
#   Cursor To Nearest Second - Will round the cursor position to the nearest
#       second, based on framerate.
#   Cursor To Beginning/End Of Clip - Will move the cursor to the beginning or
#       end of the active clip.
#   Clip Beginning/End To Cursor - Moves all selected clips so their
#       beginning/end is at the cursor.
#   Clip To Previous/Next Clip - Detects the previous or next clip in the
#       timeline from the active clip.  Moves the active clip so it's beginning
#       or end matches the previous clip's end or beginning.
#
#Quickzooms -
#   Can be found in the sequence editor 'View' menu, or by pressing the
#       'z' key over the sequencer.
#   Zoom All - Zooms the sequencer out to show all clips.
#   Zoom Selected - Zooms the sequencer to show the currently selected clip(s).
#   Zoom Cursor - Zooms the sequencer to an amount of frames around the cursor.
#   Size - How many frames should be shown by using Zoom Cursor.
#       Changing this value will automatically activate Zoom Cursor.
#
#Quickparents -
#   Can be found in the sequence editor properties panel, or by pressing the
#       'Ctrl-p' key over the sequencer.
#   This implements a parenting system for sequencer clips, allowing easy
#       selecting of multiple related clips.  Note that any relationships will
#       be broken if a clip is renamed!
#   Select Children - Selects any child clips found for the currently selected
#       clip(s).  Also can be accomplished with the shortcut 'Shift-p'
#   Set Active As Parent - If multiple clips are selected, this will set
#       selected clips as children of the active (lastly selected) clip.
#   Clear Parent - Removes parent relationships from selected children clips.
#   Clear Children - Removes child relationships from selected parent clips.
#   Children or Parents of selected clip will be shown at the bottom of
#       the Panel/Menu.
#
#Quickcontinuous -
#   Settings can be found in the sequence editor 'View' menu.
#   When Quickcontinuous is enabled, it will constantly run and detect clip
#       editing events.
#   Cursor Following - Automatically moves the sequencer timeline to try and
#       follow the cursor.  Unfortunately, this can be fooled if the cursor is
#       offscreen, or if the cursor is moved a large amount.
#   Clip Auto Snapping - If a clip is grabbed and placed, the closest clip will
#       be found, if this clip is within the snapping distance, the dropped
#       clip will be snapped to the closest clip.
#   Cut/Move Clip Children - Works with  Quickparents by finding any children
#       of a moved or cut clip and performing the same operation on them.
#       If the clip is cut, any children under the cursor will be cut as well,
#       and the script will attempt to duplicate parent/child relationships to
#       the cut clips.  Note, if you cut a clip with the mouse on the left
#       side of the cursor this will not work because the cut parent isnt
#       selected (so keep the mouse on the right side of the cursor).
#
#Quicktitling -
#   Can be found in the sequence editor properties panel.
#   This will create and edit simple scenes for title overlays.
#   Create Title Scene - This will create a title scene with the settings
#       shown below.
#   Update Title Scene - If an already-created title scene is selected,
#       this will apply the current settings to that scene.
#   Scene Length - The length in frames of the title scene.
#   Text Font - A menu of the currently loaded fonts in the blend file.
#   Text Material - A menu of all materials in the blend file.
#   Text X/Y Location - Determines the center point of the text with 0,0 being
#       the center of the screen.
#   Text Size - Scale of the text.
#   Extrude - Amount of extrusion to create a 3D look.
#   Bevel Size - Amount of beveling to apply to the text.
#   Bevel Resolution - Subdivisions of the bevel.
#   Text - Title text.
#   Shadow Amount - Determines the opacity of the drop shadow.
#   Distance - How far away the shadow plane is from the text object, larger
#       values result in a larger shadow
#   Soft - The amount of blur applied to the drop shadow.
#
#Quicklist -
#   Can be found in the sequence editor properties panel.
#   Displays a list of loaded clips and allows you to change various settings.
#   Sort by - Reorders the list based on timeline position, title, or length.
#   Eye Icon - Mutes/unmutes clip.
#   Padlock Icon - Locks/unlocks clip.
#   Clip Type Button - Allows selecting and deselecting clip.
#   Clip Title - Allows editing of clip name.
#   Length/Position - Move or resize the clip.
#   Proxy settings - Enable/disable proxy and sizes.
#
#
#Todo:
#   fix:
#       parent/child relationship copy info not showing
#       detecting cut clips isn't currently possible when the first clip isnt selected after the cut
#       fades get really screwed up when the in/out points of a clip are changed after fade is added
#       cursor following is pretty buggy
#       continuous mode may stop working and need to be disabled and re-enabled
#   add:
#       add functions for quicklist - swap clip with previous or next if in position sort
#       make quicklist more streamlined, maybe put it in a modal dialog

import bpy
import math
import os
from bpy.app.handlers import persistent


bl_info = {
    "name": "VSE Quick Functions",
    "description": "Improves funcionality of the sequencer by adding new menus for snapping, adding fades, zooming, strip parenting, and playback speed",
    "author": "Hudson Barkley (Snu)",
    "version": (0, 88),
    "blender": (2, 71, 0),
    "location": "Sequencer Panels; Sequencer Menus; Sequencer S, F, Z, Ctrl-P, Shift-P Shortcuts",
    "wiki_url": "http://blenderaddonlist.blogspot.com.au/2014/06/addon-vse-quick-functions.html",
    "category": "Sequencer"
}


#Functions used by various features
def find_next_clip(sequences, clip, mode='overlap'):
    #if mode is overlap, will only return overlapping sequences
    #if mode is channel, will only return sequences in clip's channel
    #if mode is set to other, all clips are considered
    overlaps = []
    nexts = []
    for sequence in sequences:
        if (sequence.type != 'SOUND'):
            if (mode == 'channel'):
                if ((clip.frame_final_end <= sequence.frame_final_start) & (clip.channel == sequence.channel)):
                    nexts.append(sequence)
            else:
                #if clip's end point overlaps the sequence, and the sequence begins after the clip
                if ((clip.frame_final_end > sequence.frame_final_start) & (clip.frame_final_end < sequence.frame_final_end) & (clip.frame_final_start < sequence.frame_final_start)):
                    overlaps.append(sequence)
                if (mode != 'overlap'):
                    if (clip.frame_final_end == sequence.frame_final_start):
                        overlaps.append(sequence)
                if (clip.frame_final_end <= sequence.frame_final_start):
                    nexts.append(sequence)
    if (len(overlaps) > 0):
        return min(overlaps, key=lambda overlap: abs(overlap.channel - clip.channel))
    elif ((mode != 'overlap') & (len(nexts) > 0)):
        return min(nexts, key=lambda next: (next.frame_final_start - clip.frame_final_end))
    else:
        return False

def find_previous_clip(sequences, clip, mode='overlap'):
    overlaps = []
    previous = []
    for sequence in sequences:
        if (mode == 'channel'):
            if ((clip.frame_final_start >= sequence.frame_final_end) & (clip.channel == sequence.channel)):
                previous.append(sequence)
        else:
            if ((clip.frame_final_start > sequence.frame_final_start) & (clip.frame_final_start < sequence.frame_final_end) & (clip.frame_final_end > sequence.frame_final_end)):
                overlaps.append(sequence)
            if (mode != 'overlap'):
                if (clip.frame_final_start == sequence.frame_final_end):
                    overlaps.append(sequence)
            if (clip.frame_final_start >= sequence.frame_final_end):
                previous.append(sequence)
    if (len(overlaps) > 0):
        return min(overlaps, key=lambda overlap: abs(overlap.channel - clip.channel))
    elif ((mode != 'overlap') & (len(previous) > 0)):
        return min(previous, key=lambda prev: (clip.frame_final_start - prev.frame_final_end))
    else:
        return False

def timecode_from_frames(frame, framespersecond, levels=0, subsecondtype='miliseconds'):
    if (levels > 4):
        levels = 4
    if (subsecondtype == 'frames'):
        subseconddivisor = framespersecond
    else:
        subseconddivisor = 100
    totalhours = math.modf(frame/framespersecond/60/60)
    totalminutes = math.modf(totalhours[0] * 60)
    remainingseconds = math.modf(totalminutes[0] * 60)
    hours = int(totalhours[1])
    minutes = int(totalminutes[1])
    seconds = int(remainingseconds[1])
    subseconds = int(remainingseconds[0] * subseconddivisor)
    time = str(hours).zfill(2)+':'+str(minutes).zfill(2)+':'+str(seconds).zfill(2)+':'+str(subseconds).zfill(2)[-2:]
    if (levels == 0):
        while (time[0:3] == '00:'):
            time = time[3:len(time)]
        return time
    else:
        return time.split(':', 4 - levels)[-1]


#Functions related to continuous update
def draw_quickcontinuous_menu(self, context):
    layout = self.layout
    layout.menu('vseqf.continuous_menu', text="Quick Continuous Settings")

def find_sound_clip(clipname, clips):
    soundclip = None
    os.path.splitext(clipname)[0]
    for clip in clips:
        if ((os.path.splitext(clip.name)[0] == os.path.splitext(clipname)[0]) & (clip.type == 'SOUND')):
            return clip

@persistent
def toggle_continuous(self, context=bpy.context):
    bpy.ops.vseqf.continuous('INVOKE_DEFAULT')


#Functions related to QuickTitling
def titling_scene():
    sequence = bpy.context.scene.sequence_editor.active_strip
    if (sequence == None):
        scene = bpy.context.scene
    elif (('QuickTitle: ' in sequence.name) & (sequence.type == 'SCENE')):
        scene = sequence.scene
    else:
        scene = bpy.context.scene
    return scene


#Functions related to QuickSpeed
@persistent
def frame_step(scene):
    scene = bpy.context.scene
    step = scene.step
    if (step == 1):
        if (scene.frame_current % 3 == 0):
            scene.frame_current = scene.frame_current + 1
    if (step > 1):
        scene.frame_current = scene.frame_current + (step - 1)

def draw_quickspeed_header(self, context):
    layout = self.layout
    scene = context.scene
    self.layout_width = 30
    layout.prop(scene, 'step', text="Speed Step")


#Functions related to QuickZoom
def draw_quickzoom_menu(self, context):
    layout = self.layout
    layout.menu('vseqf.quickzooms_menu', text="Quick Zoom")

def zoom_custom(begin, end):
    scene = bpy.context.scene
    selected = []
    try:
        sequences = bpy.context.sequences
    except:
        scene.sequence_editor_create()
        sequences = bpy.context.sequences
    for sequence in sequences:
        if (sequence.select):
            selected.append(sequence)
            sequence.select = False
    zoomClip = scene.sequence_editor.sequences.new_effect(name='temp', type='ADJUSTMENT', channel=1, frame_start=begin, frame_end=end)
    active = bpy.context.scene.sequence_editor.active_strip
    scene.sequence_editor.active_strip = zoomClip
    for region in bpy.context.area.regions:
        if (region.type == 'WINDOW'):
            override = {'region': region, 'window': bpy.context.window, 'screen': bpy.context.screen, 'area': bpy.context.area, 'scene': bpy.context.scene}
            bpy.ops.sequencer.view_selected(override)
    scene.sequence_editor.sequences.remove(zoomClip)
    for sequence in selected:
        sequence.select = True
    bpy.context.scene.sequence_editor.active_strip = active

def zoom_cursor(self=None, context=None):
    cursor = bpy.context.scene.frame_current
    zoom_custom(cursor, (cursor + bpy.context.scene.zoom))


#Functions related to QuickFades
def crossfade(firstClip, secondClip):
    type = bpy.context.scene.transition
    sequences = bpy.context.sequences
    bpy.ops.sequencer.select_all(action='DESELECT')
    firstClip.select = True
    secondClip.select = True
    bpy.context.scene.sequence_editor.active_strip = secondClip
    bpy.ops.sequencer.effect_strip_add(type=type)

def fades(strip, fade, type, mode):
    #strip = vse strip
    #fade = positive value of fade in frames
    #type = 'in' or 'out'
    #mode = 'detect' or 'set' or 'clear'
    scene = bpy.context.scene
    #these functions check for the needed variables and create them if in set mode.  Otherwise, ends the function.
    if (scene.animation_data == None):
        #no animation data in scene, create it
        if (mode == 'set'):
            scene.animation_data_create()
        else:
            return 0
    if (scene.animation_data.action == None):
        #no action in scene, create it
        if (mode == 'set'):
            action = bpy.data.actions.new(scene.name+"Action")
            scene.animation_data.action = action
        else:
            return 0
    fcurves = scene.animation_data.action.fcurves
    fadeZero = False
    fadeFull = False
    keyframes = False
    if (strip.type == 'SOUND'):
        fadeVariable = 'volume'
    else:
        fadeVariable = 'blend_alpha'
    #attempts to find the fade keyframes
    for curve in fcurves:
        if (curve.data_path == 'sequence_editor.sequences_all["'+strip.name+'"].'+fadeVariable):
            #keyframes found
            fcurve = curve
            if (mode == 'clear'):
                fcurves.remove(curve)
                return 0
            keyframes = curve.keyframe_points
            if (type == 'in'):
                if (len(keyframes) > 0):
                    fadeZero = keyframes[0]
                if (len(keyframes) > 1):
                    fadeFull = keyframes[1]
            elif (type == 'out'):
                if (len(keyframes) > 0):
                    fadeZero = keyframes[len(keyframes) - 1]
                if (len(keyframes) > 1):
                    fadeFull = keyframes[len(keyframes) - 2]
    if (keyframes == False):
        #no keyframes found, create them if instructed to
        if (mode == 'set'):
            curve = fcurves.new(data_path=strip.path_from_id(fadeVariable))
            keyframes = curve.keyframe_points
        else:
            return 0
    alpha = 1
    if (type == 'in'):
        stripFadeEnd = strip.frame_final_start
    elif (type == 'out'):
        stripFadeEnd = strip.frame_final_end
        fade = -fade
    if (fadeZero):
        #keyframes found, need to be adjusted
        if (fadeZero.co[0] == stripFadeEnd):
            if (fadeFull):
                #start and end are present, start is where it needs to be
                if (mode == 'set'):
                    if (fade != 0):
                        offset = ((stripFadeEnd + fade) - fadeFull.co[0])
                        fadeFull.co = (((fadeFull.co[0] + offset), alpha))
                        fadeFull.handle_left = ((fadeFull.handle_left[0] + offset, alpha))
                        fadeFull.handle_right = ((fadeFull.handle_right[0] + offset, alpha))
                        fadeZero.co = ((fadeZero.co[0], 0))
                    elif (fade == 0):
                        keyframes.remove(fadeZero)
                else:
                    return abs(fadeFull.co[0] - fadeZero.co[0])
            else:
                #start is present and where it needs to be, no second, set alpha to start
                if (mode == 'set'):
                    alpha = fadeZero.co[1]
                    fadeZero.co = ((fadeZero.co[0], 0))
                    keyframes.insert(frame=(stripFadeEnd + fade), value=alpha)
                else:
                    return 0
        else:
            #no start and end where they need to be, but keyframe exists to set alpha
            if (mode == 'set'):
                #determine alpha from value at stripFadeEnd
                alpha = fcurve.evaluate(stripFadeEnd)
                #clear any keyframes before the beginning or after the end
                index = len(keyframes) - 1
                while index >= 0:
                    keyframe = keyframes[index]
                    if (type == 'in'):
                        if (keyframe.co[0] < stripFadeEnd):
                            keyframes.remove(keyframe)
                    elif (type == 'out'):
                        if (keyframe.co[0] > stripFadeEnd):
                            keyframes.remove(keyframe)
                    index = index - 1
                keyframes.insert(frame=stripFadeEnd, value=0)
                keyframes.insert(frame=(stripFadeEnd + fade), value=alpha)
            else:
                return 0
    else:
        #no keyframes found, create them
        if (mode == 'set'):
            alpha = getattr(strip, fadeVariable)
            keyframes.insert(frame=stripFadeEnd, value=0)
            keyframes.insert(frame=(stripFadeEnd + fade), value=alpha)
        else:
            return 0


#Functions related to QuickParents
def select_children(parent):
    clean_relationships()
    sequences = bpy.context.sequences
    childrennames = find_children(parent)
    for sequence in sequences:
        if (sequence.name in childrennames):
            sequence.select = True

def add_children(parent, children):
    clean_relationships()
    for child in children:
        if (child.name != parent.name):
            children = parent.name
            if (child.name not in children):
                relationship = bpy.context.scene.parenting.add()
                relationship.parent = parent.name
                relationship.child = child.name

def clear_children(parent):
    clean_relationships()
    if (type(parent) == str):
        parentname = parent
    else:
        parentname = parent.name
    scene = bpy.context.scene
    index = 0
    while index < len(scene.parenting):
        if (scene.parenting[index].parent == parentname):
            scene.parenting.remove(index)
        else:
            index = index + 1

def clear_parent(child):
    clean_relationships()
    if (type(child) == str):
        childname = child
    else:
        childname = child.name
    scene = bpy.context.scene
    for index, relationship in enumerate(scene.parenting):
        if (relationship.child == childname):
            scene.parenting.remove(index)

def find_parent(child):
    if (type(child) == str):
        childname = child
    else:
        childname = child.name
    scene = bpy.context.scene
    for relationship in scene.parenting:
        if (relationship.child == childname):
            return relationship.parent
    return "None"

def find_children(parent):
    if (type(parent) == str):
        parentname = parent
    else:
        parentname = parent.name
    scene = bpy.context.scene
    childrennames = []
    for relationship in scene.parenting:
        if (relationship.parent == parentname):
            childrennames.append(relationship.child)
    return childrennames

def clean_relationships():
    scene = bpy.context.scene
    sequences = scene.sequence_editor.sequences_all
    for index, relationship in enumerate(scene.parenting):
        if ( (sequences.find(relationship.parent) == -1) | (sequences.find(relationship.child) == -1) ):
            scene.parenting.remove(index)


#Functions related to QuickSnaps
def draw_quicksnap_menu(self, context):
    layout = self.layout
    layout.menu('vseqf.quicksnaps_menu', text="Quick Snaps")


#Classes related to QuickList
class VSEQFQuickListPanel(bpy.types.Panel):
    bl_label = "Quick List"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    @classmethod
    def poll(self, context):
        if (bpy.context.sequences):
            if (len(bpy.context.sequences) > 0):
                return True
            else:
                return False
        else:
            return False
    def draw(self, contex):
        layout = self.layout
        scene = bpy.context.scene
        sequencer = scene.sequence_editor
        sequences = bpy.context.sequences
        row = layout.row()
        row.operator('vseqf.quicklist_select', text='Select/Deselect All Clips').clip = ''
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label('Sort By:')
        sub = row.column(align=True)
        sub.operator('vseqf.quicklist_sortby', text='Position').method = 'Position'
        if (scene.quicklistsort == 'Position'):
            sub.active = True
        else:
            sub.active = False
        sub = row.column(align=True)
        sub.operator('vseqf.quicklist_sortby', text='Title').method = 'Title'
        if (scene.quicklistsort == 'Title'):
            sub.active = True
        else:
            sub.active = False
        sub = row.column(align=True)
        sub.operator('vseqf.quicklist_sortby', text='Length').method = 'Length'
        if (scene.quicklistsort == 'Length'):
            sub.active = True
        else:
            sub.active = False
        sorted = list(sequences)
        if (scene.quicklistsort == 'Title'):
            sorted.sort(key=lambda sequence: sequence.name)
        elif (scene.quicklistsort =='Length'):
            sorted.sort(key=lambda sequence: sequence.frame_final_duration)
        else:
            sorted.sort(key=lambda sequence: sequence.frame_final_start)
        for clip in sorted:
            if (hasattr(clip, 'input_1')):
                resort = sorted.pop(sorted.index(clip))
                parentindex = sorted.index(clip.input_1)
                sorted.insert(parentindex + 1, resort)
        for index, sequence in enumerate(sorted):
            if (hasattr(sequence, 'input_1')):
                row = layout.row()
                row.separator()
                row.separator()
                outline = row.box()
            else:
                outline = layout.box()
            box = outline.column()
            row = box.row(align=True)
            split = row.split(align=True)
            split.prop(sequence, 'mute', text='')
            split.prop(sequence, 'lock', text='')
            split = row.split(align=True, percentage=0.2)
            col = split.column(align=True)
            col.operator('vseqf.quicklist_select', text="("+sequence.type+")").clip = sequence.name
            col.active = sequence.select
            col = split.column(align=True)
            col.prop(sequence, 'name', text='')
            row = box.row()
            split = row.split(percentage=0.8)
            col = split.row(align=True)
            col.prop(sequence, 'frame_final_duration', text="Length: ("+timecode_from_frames(sequence.frame_final_duration, scene.render.fps)+"), Frame")
            col.prop(sequence, 'frame_start', text="Position: ("+timecode_from_frames(sequence.frame_start, scene.render.fps)+"), Frame")
            col = split.row()
            if (sequence.type != 'SOUND'):
                col.prop(sequence, 'use_proxy', text='Proxy')
                if (sequence.use_proxy):
                    row = box.row()
                    split = row.split(percentage=0.33)
                    col = split.row(align=True)
                    col.prop(sequence.proxy, 'quality')
                    col = split.row(align=True)
                    col.prop(sequence.proxy, 'build_25')
                    col.prop(sequence.proxy, 'build_50')
                    col.prop(sequence.proxy, 'build_75')
                    col.prop(sequence.proxy, 'build_100')
            children = find_children(sequence)
            if (len(children) > 0):
                row = box.row()
                split = row.split(percentage=0.25)
                col = split.column()
                col.label('Children:')
                col = split.column()
                for child in children:
                    col.label(child)
            if (sequence.type == 'META'):
                row = box.row()
                split = row.split(percentage=0.25)
                col = split.column()
                col.label('Subclips:')
                col = split.column()
                for subclip in sequence.sequences:
                    col.label(subclip.name)


class VSEQFQuickListSortBy(bpy.types.Operator):
    bl_idname = "vseqf.quicklist_sortby"
    bl_label = "VSEQF Quick List Sort By"
    method = bpy.props.StringProperty()
    def execute(self, context):
        scene = context.scene
        scene.quicklistsort = self.method
        return {'FINISHED'}

class VSEQFQuickListSelect(bpy.types.Operator):
    bl_idname = "vseqf.quicklist_select"
    bl_label = "VSEQF Quick List Select Clip"
    clip = bpy.props.StringProperty()
    def execute(self, context):
        sequences = context.sequences
        if (self.clip == ''):
            bpy.ops.sequencer.select_all(action='TOGGLE')
        else:
            for sequence in sequences:
                if (sequence.name == self.clip):
                    sequence.select = not sequence.select
        return {'FINISHED'}


#Classes related to continuous update
class VSEQFContinuousMenu(bpy.types.Menu):
    bl_idname = "vseqf.continuous_menu"
    bl_label = "Continuous Settings"
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        layout.prop(scene, 'quickcontinuousenable')
        if (scene.quickcontinuousenable):
            layout.separator()
            layout.prop(scene, 'quickcontinuousfollow')
            layout.prop(scene, 'quickcontinuoussnap')
            layout.prop(scene, 'quickcontinuoussnapdistance')
            layout.prop(scene, 'quickcontinuouschildren')

class VSEQFContinuous(bpy.types.Operator):
    bl_idname = "vseqf.continuous"
    bl_label = "VSEQF Continuous Modal Operator"
    lastScene = bpy.props.StringProperty()
    lastClip = bpy.props.StringProperty()
    lastClipStart = bpy.props.IntProperty()
    lastClipLength = bpy.props.IntProperty()
    lastClipChannel = bpy.props.IntProperty()
    lastCursor = bpy.props.IntProperty()
    lastNumberOfClips = bpy.props.IntProperty()
    def set_old_variables(self):
        scene = bpy.context.scene
        sequencer = scene.sequence_editor
        sequences = bpy.context.sequences
        if (hasattr(sequencer, 'active_strip')):
            clip = sequencer.active_strip
        else:
            clip = None
        self.lastScene = scene.name
        if (hasattr(clip, 'name')):
            self.lastClip = clip.name
            self.lastClipStart = clip.frame_final_start
            self.lastClipLength = clip.frame_final_duration
            self.lastClipChannel = clip.channel
            self.lastNumberOfClips = len(sequencer.sequences_all)
        else:
            self.lastClip = 'None'
            self.lastClipStart = 0
            self.lastClipLength = 0
            self.lastClipChannel = 0
            self.lastNumberOfClips = 0
        self.lastCursor = scene.frame_current
    def modal(self, context, event):
        scene = context.scene
        if (scene.quickcontinuousenable):
            if (self.lastScene == scene.name):
                if (self.lastClip != 'None'):
                    sequencer = scene.sequence_editor
                    sequences = bpy.context.sequences
                    clip = sequencer.active_strip
                    if (clip.name == self.lastClip):
                        if ((clip.frame_final_start != self.lastClipStart) & (clip.frame_final_duration == self.lastClipLength)):
                            if (scene.quickcontinuoussnap):
                                nextclip = find_next_clip(sequences, clip, mode='channel')
                                previousclip = find_previous_clip(sequences, clip, mode='channel')
                                try:
                                    nextdistance = nextclip.frame_final_start - clip.frame_final_end
                                except:
                                    nextdistance = scene.quickcontinuoussnapdistance + 1
                                try:
                                    previousdistance = clip.frame_final_start - previousclip.frame_final_end
                                except:
                                    previousdistance = scene.quickcontinuoussnapdistance + 1
                                snapclip = min([[nextdistance, 'next'], [previousdistance, 'previous']])
                                if (snapclip[0] <= scene.quickcontinuoussnapdistance):
                                    if (snapclip[1] == 'next'):
                                        clip.frame_start = clip.frame_start + nextdistance
                                    else:
                                        clip.frame_start = clip.frame_start - previousdistance
                            if (scene.quickcontinuouschildren):
                                childrennames = find_children(clip)
                                if (childrennames):
                                    offset = clip.frame_final_start - self.lastClipStart
                                    for childname in childrennames:
                                        for sequence in sequences:
                                            if (sequence.name == childname):
                                                sequence.frame_start = sequence.frame_start + offset
                        elif (clip.frame_final_duration != self.lastClipLength):
                            if ((clip.frame_final_start == self.lastClipStart) & (len(sequencer.sequences_all) == self.lastNumberOfClips + 1)):
                                #clip was cut because beginning point is the same, duration is different, and total clips are increased by one
                                if (scene.quickcontinuouschildren):
                                    childrennames = find_children(clip)
                                    if (childrennames):
                                        cutchildren = []
                                        #unfortunately, cutting doesnt always select both parts of the cut...
                                        #and there seems to be no way of finding the second part
                                        #so if the cut parent isnt selected, the children arent copied over
                                        cutparent = bpy.context.selected_sequences[0]
                                        if ((cutparent.name == clip.name) | (cutparent.name.split('.')[0] != clip.name.split('.')[0])):
                                            cutparent = False
                                        for childname in childrennames:
                                            for child in sequences:
                                                if (child.name == childname):
                                                    if ((child.frame_final_start < scene.frame_current) & (child.frame_final_end > scene.frame_current)):
                                                        bpy.ops.sequencer.select_all(action='DESELECT')
                                                        child.select = True
                                                        bpy.ops.sequencer.cut(frame=scene.frame_current)
                                                        selected = bpy.context.selected_sequences
                                                        selected.remove(child)
                                                        cutchildren.extend(selected)
                                        bpy.ops.sequencer.select_all(action='DESELECT')
                                        if (cutparent):
                                            cutparent.select = True
                                            sequencer.active_strip = cutparent
                                            add_children(cutparent, cutchildren)
                                            self.report({'INFO'}, "Duplicated child cut clips to cut parent")
                                            #report doesnt work so we have to fall back to print, lame
                                            print("Duplicated child cut clips to cut parent")
                                        else:
                                            self.report({'WARNING'}, "Could not determine cut parent clip")
                                            print("Could not determine cut parent clip")
                            else:
                                #clip was resized
                                pass
                    else:
                        if (len(sequencer.sequences_all) > self.lastNumberOfClips):
                            #clip was added
                            selected = bpy.context.selected_sequences
                            if (len(selected) > 1):
                                for clip in selected:
                                    if (clip.type == 'MOVIE'):
                                        soundclip = find_sound_clip(clip.name, selected)
                                        if (soundclip):
                                            self.report({'INFO'}, "Parenting "+soundclip.name+" to "+clip.name)
                                            add_children(clip, [soundclip])
                if (scene.frame_current != self.lastCursor):
                    if (scene.quickcontinuousfollow):
                        #move timeline to follow cursor
                        for area in bpy.context.screen.areas:
                            if (area.type == 'SEQUENCE_EDITOR'):
                                for region in area.regions:
                                    if (region.type == 'WINDOW'):
                                        if (area.spaces[0].view_type == 'SEQUENCER'):
                                            override = {'area': area, 'window': bpy.context.window, 'region': region, 'screen': bpy.context.screen}
                                            offset = scene.frame_current - self.lastCursor
                                            bpy.ops.view2d.pan(override, deltax=offset)
            self.set_old_variables()
            return {'PASS_THROUGH'}
        else:
            return {'FINISHED'}
    def invoke(self, context, event):
        if (context.scene.quickcontinuousenable):
            self.set_old_variables()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


#Classes related to QuickTitling
class VSEQFQuickTitlingPanel(bpy.types.Panel):
    bl_label = "Quick Titling"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw(self, contex):
        layout = self.layout
        row = layout.row()
        try:
            sequence = bpy.context.scene.sequence_editor.active_strip
            if (('QuickTitle: ' in sequence.name) & (sequence.type == 'SCENE')):
                row.operator('vseqf.quicktitling', text='Update Title Scene').action = 'update'
                scene = sequence.scene
            else:
                row.operator('vseqf.quicktitling', text='Create Title Scene').action = 'create'
                scene = bpy.context.scene
        except:
            row.operator('vseqf.quicktitling', text='Create Title Scene').action = 'create'
            scene = bpy.context.scene
        row = layout.row()
        row.prop(scene, 'quicktitlerlength')
        row = layout.row()
        row.prop(scene, 'quicktitlertext')
        outline = layout.box()
        row = outline.row()
        row.label('Text Font:')
        row.menu('vseqf.quicktitler_fonts_menu', text=scene.quicktitlerfont)
        row = outline.row(align=True)
        split = row.split()
        split.label('Material:')
        split = row.split(percentage=0.66, align=True)
        split.menu('vseqf.quicktitler_materials_menu', text=scene.quicktitlermaterial)
        split.operator('vseqf.quicktitler_new_material', text='+')
        index = bpy.data.materials.find(scene.quicktitlermaterial)
        if (index >= 0):
            material = bpy.data.materials[index]
            split.prop(material, 'diffuse_color', text='')
        outline = layout.box()
        row = outline.row()
        split = row.split(align=True)
        split.prop(scene, 'quicktitlerx', text='X Loc:')
        split.prop(scene, 'quicktitlery', text='Y Loc:')
        row = outline.row()
        row.prop(scene, 'quicktitlersize', text='Size')
        outline = layout.box()
        row = outline.row()
        row.prop(scene, 'quicktitlerextrude')
        row = outline.row()
        split = row.split(align=True)
        split.prop(scene, 'quicktitlerbevelsize')
        split.prop(scene, 'quicktitlerbevelresolution')
        outline = layout.box()
        row = outline.row()
        row.prop(scene, 'quicktitlershadow')
        row = outline.row()
        row.prop(scene, 'quicktitlershadowsize', text='Distance')
        row.prop(scene, 'quicktitlershadowsoft', text='Soft')

class VSEQFQuickTitlingNewMaterial(bpy.types.Operator):
    bl_idname = 'vseqf.quicktitler_new_material'
    bl_label = 'New Material'
    bl_description = 'Creates A New Material, Duplicates Current If Available'
    def execute(self, context):
        scene = bpy.context.scene
        index = bpy.data.materials.find(scene.quicktitlermaterial)
        if (index >= 0):
            material = bpy.data.materials[index].copy()
        else:
            material = bpy.data.materials.new('QuickTitler Material')
        scene.quicktitlermaterial = material.name
        return {'FINISHED'}

class VSEQFQuickTitling(bpy.types.Operator):
    bl_idname = 'vseqf.quicktitling'
    bl_label = 'VSEQF Quick Titling'
    bl_description = 'Creates or updates a titler scene'
    action = bpy.props.StringProperty()
    def execute(self, context):
        scene = titling_scene()
        sequencer = bpy.context.scene.sequence_editor
        if (self.action == 'create'):
            bpy.ops.scene.new(type='EMPTY')
            titleScene = bpy.context.scene
            titleScene.quicktitlerfont = scene.quicktitlerfont
            titleScene.quicktitlerx = scene.quicktitlerx
            titleScene.quicktitlery = scene.quicktitlery
            titleScene.quicktitlersize = scene.quicktitlersize
            titleScene.quicktitlerextrude = scene.quicktitlerextrude
            titleScene.quicktitlerbevelsize = scene.quicktitlerbevelsize
            titleScene.quicktitlerbevelresolution = scene.quicktitlerbevelresolution
            titleScene.quicktitlertext = scene.quicktitlertext
            titleScene.quicktitlerlength = scene.quicktitlerlength
            titleScene.name = "QuickTitle: "+titleScene.quicktitlertext
            titleScene.frame_end = titleScene.quicktitlerlength
            titleScene.layers = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]
            bpy.ops.object.camera_add()
            camera = bpy.context.scene.objects.active
            titleScene.camera = camera
            camera.location = ((0, 0, 15))
            camera.name = "QuickTitlerCamera"
            lampEnergy = 0.5
            bpy.ops.object.lamp_add(location=(-4, -2.5, 2))
            lamp1 = bpy.context.scene.objects.active
            lamp1.data.energy = lampEnergy
            lamp1.data.shadow_method = 'NOSHADOW'
            bpy.ops.object.lamp_add(location=(4, -2.5, 2))
            lamp2 = bpy.context.scene.objects.active
            lamp2.data.energy = lampEnergy
            lamp2.data.shadow_method = 'NOSHADOW'
            bpy.ops.object.lamp_add(location=(-4, 2.5, 2))
            lamp3 = bpy.context.scene.objects.active
            lamp3.data.energy = lampEnergy
            lamp3.data.shadow_method = 'NOSHADOW'
            bpy.ops.object.lamp_add(location=(4, 2.5, 2))
            lamp4 = bpy.context.scene.objects.active
            lamp4.data.energy = lampEnergy
            lamp4.data.shadow_method = 'NOSHADOW'
            bpy.ops.object.lamp_add(type= 'SPOT', location=(0, 0, 4))
            shadowLamp = bpy.context.scene.objects.active
            shadowLamp.name = 'QuickTitlerLamp'
            shadowLamp.data.use_only_shadow = True
            shadowLamp.data.shadow_method = 'BUFFER_SHADOW'
            shadowLamp.data.shadow_buffer_type = 'REGULAR'
            shadowLamp.data.shadow_buffer_soft = 10
            shadowLamp.data.shadow_buffer_bias = 0.1
            shadowLamp.data.shadow_buffer_size = 512
            shadowLamp.data.shadow_buffer_samples = 8
            shadowLamp.data.spot_size = 2.182
            bpy.ops.object.text_add()
            text = bpy.context.scene.objects.active
            text.data.align = 'CENTER'
            text.name = "QuickTitlerText"
            bpy.ops.mesh.primitive_plane_add(radius=10)
            shadow = bpy.context.scene.objects.active
            shadow.name = "QuickTitlerShadow"
            shadow.draw_type = 'WIRE'
            shadowMaterial = bpy.data.materials.new('QuickTitlerShadow')
            shadowMaterial.diffuse_color = (0, 0, 0)
            shadowMaterial.diffuse_intensity = 1
            shadowMaterial.specular_intensity = 0
            shadowMaterial.use_transparency = True
            shadowMaterial.use_cast_buffer_shadows = False
            shadowMaterial.shadow_only_type = 'SHADOW_ONLY'
            shadowMaterial.use_only_shadow = True
            shadow.data.materials.append(shadowMaterial)
            titleScene.render.engine = 'BLENDER_RENDER'
            titleScene.render.alpha_mode = 'TRANSPARENT'
            titleScene.render.image_settings.file_format = 'PNG'
            titleScene.render.image_settings.color_mode = 'RGBA'
            bpy.context.screen.scene = scene
            bpy.ops.sequencer.scene_strip_add(frame_start=scene.frame_current, scene=titleScene.name)
            sequence = sequencer.active_strip
            sequence.blend_type = 'ALPHA_OVER'
            scene = titleScene
        else:
            sequence = bpy.context.scene.sequence_editor.active_strip
            text = None
            shadow = None
            shadowLamp = None
            for object in scene.objects:
                if (object.type == 'FONT'):
                    text = object
                if ("QuickTitlerShadow" in object.name):
                    shadow = object
                if ("QuickTitlerLamp" in object.name):
                    shadowLamp = object
            if ((text == None) or (shadow == None) or (shadowLamp == None)):
                self.report({'WARNING'}, 'Selected Title Scene Is Incomplete')
                return {'CANCELLED'}
        scene.frame_end = scene.quicktitlerlength
        index = bpy.data.materials.find(scene.quicktitlermaterial)
        if (index >= 0):
            text.data.materials.clear()
            text.data.materials.append(bpy.data.materials[index])
        else:
            material = bpy.data.materials.new('QuickTitler Material')
            scene.quicktitlermaterial = material.name
        text.location = (scene.quicktitlerx, scene.quicktitlery, 0)
        text.scale = (scene.quicktitlersize, scene.quicktitlersize, scene.quicktitlersize)
        text.data.extrude = scene.quicktitlerextrude
        text.data.bevel_depth = scene.quicktitlerbevelsize
        text.data.bevel_resolution = scene.quicktitlerbevelresolution
        text.data.body = scene.quicktitlertext
        text.data.font = bpy.data.fonts[scene.quicktitlerfont]
        shadow.material_slots[0].material.alpha = scene.quicktitlershadow
        shadowLamp.data.shadow_buffer_soft = scene.quicktitlershadowsoft * 10
        shadow.location = (0, 0, -(scene.quicktitlershadowsize / 8))
        scene.name = "QuickTitle: "+scene.quicktitlertext
        sequence.name = "QuickTitle: "+scene.quicktitlertext
        bpy.ops.sequencer.reload(adjust_length=True)
        bpy.ops.sequencer.refresh_all()
        return {'FINISHED'}

class VSEQFQuickTitlingFontMenu(bpy.types.Menu):
    bl_idname = 'vseqf.quicktitler_fonts_menu'
    bl_label = 'List of loaded fonts'
    def draw(self, context):
        fonts = bpy.data.fonts
        layout = self.layout
        for font in fonts:
            layout.operator('vseqf.quicktitler_change_font', text=font.name).font = font.name

class VSEQFQuickTitlingMaterialMenu(bpy.types.Menu):
    bl_idname = 'vseqf.quicktitler_materials_menu'
    bl_label = 'List of loaded materials'
    def draw(self, context):
        materials = bpy.data.materials
        layout = self.layout
        for material in materials:
            layout.operator('vseqf.quicktitler_change_material', text=material.name).material = material.name

class VSEQFQuickTitlingChangeFont(bpy.types.Operator):
    bl_idname = 'vseqf.quicktitler_change_font'
    bl_label = 'Change Font'
    font = bpy.props.StringProperty()
    def execute(self, context):
        scene = titling_scene()
        scene.quicktitlerfont = self.font
        return {'FINISHED'}

class VSEQFQuickTitlingChangeMaterial(bpy.types.Operator):
    bl_idname = 'vseqf.quicktitler_change_material'
    bl_label = 'Change Material'
    material = bpy.props.StringProperty()
    def execute(self, context):
        scene = titling_scene()
        scene.quicktitlermaterial = self.material
        return {'FINISHED'}


#Classes related to QuickParents
class ParentRelationship(bpy.types.PropertyGroup):
    parent=bpy.props.StringProperty(name="Parent", default="None")
    child=bpy.props.StringProperty(name="Children", default="None")

class VSEQFQuickParentsPanel(bpy.types.Panel):
    bl_label = "Quick Parents"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    @classmethod
    def poll(self, context):
        try:
            sequence = context.scene.sequence_editor.active_strip
            if (sequence):
                return True
            else:
                return False
        except:
            return False
    def draw(self, context):
        scene = bpy.context.scene
        strip = scene.sequence_editor.active_strip
        selected = bpy.context.selected_sequences
        childrennames = find_children(strip.name)
        parentname = find_parent(strip.name)
        layout = self.layout
        row = layout.row()
        row.operator('vseqf.quickparents', text='Select Children').action = 'selectchildren'
        row = layout.row()
        if (len(selected) <= 1):
            row.enabled = False
        row.operator('vseqf.quickparents', text='Set Active As Parent').action = 'add'
        row = layout.row()
        row.operator('vseqf.quickparents', text='Clear Parent').action = 'clearparent'
        row.operator('vseqf.quickparents', text='Clear Children').action = 'clearchildren'
        if (parentname != 'None'):
            row = layout.row()
            row.label("Parent: "+parentname)
        if (len(childrennames) > 0):
            row = layout.row()
            row.label("Children: "+childrennames[0])
            index = 1
            while index < len(childrennames):
                row = layout.row()
                row.label(childrennames[index])
                index = index + 1

class VSEQFQuickParentsMenu(bpy.types.Menu):
    bl_idname = "vseqf.quickparents_menu"
    bl_label = "Quick Parents"
    def draw(self, context):
        scene = bpy.context.scene
        strip = scene.sequence_editor.active_strip
        layout = self.layout
        if (strip):
            selected = bpy.context.selected_sequences
            childrennames = find_children(strip.name)
            parentname = find_parent(strip.name)
            layout.operator('vseqf.quickparents', text='Select Children').action = 'selectchildren'
            if (len(selected) > 1):
                layout.operator('vseqf.quickparents', text='Set Active As Parent').action = 'add'
            layout.operator('vseqf.quickparents', text='Clear Parent').action = 'clearparent'
            layout.operator('vseqf.quickparents', text='Clear Children').action = 'clearchildren'
            layout.separator()
            if (parentname != 'None'):
                layout.label("     Parent: ")
                layout.label(parentname)
                layout.separator()
            if (len(childrennames) > 0):
                layout.label("     Children:")
                index = 0
                while index < len(childrennames):
                    layout.label(childrennames[index])
                    index = index + 1
                layout.separator()
        else:
            layout.label('No Strip Selected')

class VSEQFQuickParents(bpy.types.Operator):
    bl_idname = 'vseqf.quickparents'
    bl_label = 'VSEQF Quick Parents'
    bl_description = 'Sets Or Removes Strip Parents'
    action = bpy.props.StringProperty()
    def execute(self, context):
        clean_relationships()
        selected = bpy.context.selected_sequences
        active = bpy.context.scene.sequence_editor.active_strip
        if (self.action == 'add'):
            if (len(selected) > 1):
                add_children(active, selected)
        for clip in selected:
            if (self.action == 'selectchildren'):
                select_children(clip.name)
            if (self.action == 'clearparent'):
                clear_parent(clip.name)
            if (self.action == 'clearchildren'):
                clear_children(clip.name)
        return {'FINISHED'}


#Classes related to QuickSnaps
class VSEQFQuickSnapsMenu(bpy.types.Menu):
    bl_idname = "vseqf.quicksnaps_menu"
    bl_label = "Quick Snaps"
    def draw(self, context):
        layout = self.layout
        layout.operator('vseqf.quicksnaps', text='Cursor To Nearest Second').type = 'cursor_to_seconds'
        scene = bpy.context.scene
        try:
            strip = scene.sequence_editor.active_strip
            if (strip):
                layout.operator('vseqf.quicksnaps', text='Cursor To Beginning Of Clip').type = 'cursor_to_beginning'
                layout.operator('vseqf.quicksnaps', text='Cursor To End Of Clip').type = 'cursor_to_end'
                layout.separator()
                layout.operator('vseqf.quicksnaps', text='Clip Beginning To Cursor').type = 'begin_to_cursor'
                layout.operator('vseqf.quicksnaps', text='Clip End To Cursor').type = 'end_to_cursor'
                layout.operator('vseqf.quicksnaps', text='Clip To Previous Clip').type = 'clip_to_previous'
                layout.operator('vseqf.quicksnaps', text='Clip To Next Clip').type = 'clip_to_next'
        except:
            pass

class VSEQFQuickSnaps(bpy.types.Operator):
    bl_idname = 'vseqf.quicksnaps'
    bl_label = 'VSEQF Quick Snaps'
    bl_description = 'Snaps selected sequencer clips'
    type = bpy.props.StringProperty()
    def execute(self, context):
        selected = bpy.context.selected_sequences
        scene = bpy.context.scene
        active = bpy.context.scene.sequence_editor.active_strip
        frame = scene.frame_current
        if (self.type == 'cursor_to_seconds'):
            fps = scene.render.fps / scene.render.fps_base
            scene.frame_current = round(round(scene.frame_current / fps) * fps)
        if (self.type == 'cursor_to_beginning'):
            scene.frame_current = active.frame_final_start
        if (self.type == 'cursor_to_end'):
            scene.frame_current = active.frame_final_end
        if (self.type == 'begin_to_cursor'):
            for clip in selected:
                offset = clip.frame_final_start - clip.frame_start
                clip.frame_start = (frame - offset)
        if (self.type == 'end_to_cursor'):
            for clip in selected:
                offset = clip.frame_final_start - clip.frame_start
                clip.frame_start = (frame - offset - clip.frame_final_duration)
        if (self.type == 'clip_to_previous'):
            previous = find_previous_clip(scene.sequence_editor.sequences, active, 'any')
            if (previous):
                for clip in selected:
                    offset = clip.frame_final_start - clip.frame_start
                    clip.frame_start = (previous.frame_final_end - offset)
            else:
                self.report({'WARNING'}, 'No Previous Clip Found')
        if (self.type == 'clip_to_next'):
            next = find_next_clip(scene.sequence_editor.sequences, active, 'any')
            if (next):
                for clip in selected:
                    offset = clip.frame_final_start - clip.frame_start
                    clip.frame_start = (next.frame_final_start - offset - clip.frame_final_duration)
            else:
                self.report({'WARNING'}, 'No Next Clip Found')
        return{'FINISHED'}


#Classes related to QuickFades
class VSEQFQuickFadesPanel(bpy.types.Panel):
    bl_label = "Quick Fades"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    @classmethod
    def poll(self, context):
        try:
            sequence = context.scene.sequence_editor.active_strip
            if (sequence):
                return True
            else:
                return False
        except:
            return False
    def draw(self, context):
        scene = bpy.context.scene
        strip = scene.sequence_editor.active_strip
        frame = scene.frame_current
        sequenceEditor = bpy.context.area.spaces.active
        layout = self.layout
        row = layout.row()
        fadein = fades(strip=strip, fade=0, type='in', mode='detect')
        fadeout = fades(strip=strip, fade=0, type='out', mode='detect')
        if (fadein > 0):
            row.label("Fadein: "+str(round(fadein))+" Frames")
        else:
            row.label("No Fadein Detected")
        if (fadeout > 0):
            row.label("Fadeout: "+str(round(fadeout))+" Frames")
        else:
            row.label("No Fadeout Detected")
        row = layout.row()
        row.prop(scene, 'fade')
        row = layout.row()
        row.operator('vseqf.quickfades', text='Set Fadein').type = 'in'
        row.operator('vseqf.quickfades', text='Set Fadeout').type = 'out'
        row = layout.row()
        row.operator('vseqf.quickfades_clear', text='Clear Fades')
        row = layout.row()
        row.separator()
        row = layout.row()
        row.menu('vseqf.quickfades_transition_menu', text="Transition Type: "+scene.transition)
        row = layout.row()
        row.operator('vseqf.quickfades_cross', text='Crossfade Prev Clip').type = 'previous'
        row.operator('vseqf.quickfades_cross', text='Crossfade Next Clip').type = 'next'
        row = layout.row()
        row.operator('vseqf.quickfades_cross', text='Smart Cross to Prev').type = 'previoussmart'
        row.operator('vseqf.quickfades_cross', text='Smart Cross to Next').type = 'nextsmart'

class VSEQFQuickFadesClear(bpy.types.Operator):
    bl_idname = 'vseqf.quickfades_clear'
    bl_label = 'VSEQF Quick Fades Clear Fades'
    bl_description = 'Clears fade in and out for selected clips'
    def execute(self, context):
        for sequence in bpy.context.selected_sequences:
            fades(strip=sequence, fade=bpy.context.scene.fade, type='both', mode='clear')
            sequence.blend_alpha = 1
        return{'FINISHED'}

class VSEQFQuickFadesMenu(bpy.types.Menu):
    bl_idname = "vseqf.quickfades_menu"
    bl_label = "Quick Fades"
    def draw(self, context):
        scene = bpy.context.scene
        strip = scene.sequence_editor.active_strip
        layout = self.layout
        if (strip):
            frame = scene.frame_current
            sequenceEditor = bpy.context.area.spaces.active
            fadein = fades(strip=strip, fade=0, type='in', mode='detect')
            fadeout = fades(strip=strip, fade=0, type='out', mode='detect')
            if (fadein > 0):
                fadeinlabel = "Fadein: "+str(round(fadein))+" Frames"
            else:
                fadeinlabel = "No Fadein Detected"
            if (fadeout > 0):
                fadeoutlabel = "Fadeout: "+str(round(fadeout))+" Frames"
            else:
                fadeoutlabel = "No Fadeout Detected"
            layout.label(fadeinlabel)
            layout.label(fadeoutlabel)
            layout.prop(scene, 'fade')
            layout.operator('vseqf.quickfades_fade', text='Set Fadein').type = 'in'
            layout.operator('vseqf.quickfades_fade', text='Set Fadeout').type = 'out'
            layout.operator('vseqf.quickfades_clear', text='Clear Fades')
            layout.separator()
            layout.menu('vseqf.quickfades_transition_menu', text="Transition Type: "+scene.transition)
            layout.operator('vseqf.quickfades_cross', text='Crossfade Prev Clip').type = 'previous'
            layout.operator('vseqf.quickfades_cross', text='Crossfade Next Clip').type = 'next'
            layout.operator('vseqf.quickfades_cross', text='Smart Cross to Prev').type = 'previoussmart'
            layout.operator('vseqf.quickfades_cross', text='Smart Cross to Next').type = 'nextsmart'
        else:
            layout.label("No Strip Selected")

class VSEQFQuickFades(bpy.types.Operator):
    bl_idname = 'vseqf.quickfades'
    bl_label = 'VSEQF Quick Fades Set Fade'
    bl_description = 'Adds or changes fade for selected clips'
    type = bpy.props.StringProperty()
    def execute(self, context):
        for sequence in bpy.context.selected_sequences:
            fades(strip=sequence, fade=bpy.context.scene.fade, type=self.type, mode='set')
        return{'FINISHED'}

class VSEQFQuickFadesCross(bpy.types.Operator):
    bl_idname = 'vseqf.quickfades_cross'
    bl_label = 'VSEQF Quick Fades Add Crossfade'
    bl_description = 'Adds a crossfade between selected strip and next or previous strip in timeline if they overlap'
    type = bpy.props.StringProperty()
    def execute(self, context):
        sequences = bpy.context.sequences
        #store a list of selected sequences since adding a crossfade destroys the selection
        selectedSequences = bpy.context.selected_sequences
        #iterate through selected sequences and add crossfades to previous or next clip
        for sequence in selectedSequences:
            if (self.type == 'nextsmart'):
                firstClip = sequence
                secondClip = find_next_clip(sequences, firstClip, mode='all')
            if (self.type == 'previoussmart'):
                secondClip = sequence
                firstClip = find_previous_clip(sequences, secondClip, mode='all')
            if (self.type == 'next'):
                firstClip = sequence
                secondClip = find_next_clip(sequences, firstClip)
            elif (self.type == 'previous'):
                secondClip = sequence
                firstClip = find_previous_clip(sequences, secondClip)
            if ((secondClip != False) & (firstClip != False)):
                if ('smart' in self.type):
                    #adjust start and end frames of clips based on frame_offset_end/start to overlap by amount of crossfade
                    targetFade = bpy.context.scene.fade
                    currentFade = firstClip.frame_final_end - secondClip.frame_final_start
                    fadeOffset = abs(currentFade - targetFade)
                    firstOffset = round((fadeOffset/2)+.1)
                    secondOffset = round((fadeOffset/2)-.1)
                    firstClip.frame_final_end
                    secondClip.frame_final_start
                    if (currentFade < targetFade):
                        #extend frame end and start based on how much offset
                        if (((firstClip.frame_offset_end > firstOffset) & (secondClip.frame_offset_start > secondOffset)) | ((firstClip.frame_offset_end == 0) & (secondClip.frame_offset_start == 0))):
                            #both clip offsets are larger than both target offsets or neither clip has offsets
                            firstClip.frame_final_end = firstClip.frame_final_end + firstOffset
                            secondClip.frame_final_start = secondClip.frame_final_start - secondOffset
                        else:
                            #clip offsets need to be adjusted individually
                            currentOffset = firstClip.frame_offset_end + secondClip.frame_offset_start
                            firstOffsetPercent = firstClip.frame_offset_end / currentOffset
                            secondOffsetPercent = secondClip.frame_offset_start / currentOffset
                            firstClip.frame_final_end = firstClip.frame_final_end + (round(firstOffsetPercent * fadeOffset))
                            secondClip.frame_final_start = secondClip.frame_final_start - (round(secondOffsetPercent * fadeOffset))
                    elif (currentFade > targetFade):
                        #overlap is larger than target fade, subtract equal amounts from each clip
                        firstClip.frame_final_end = firstClip.frame_final_end - firstOffset
                        secondClip.frame_final_start = secondClip.frame_final_start + secondOffset
                crossfade(firstClip, secondClip)
            else:
                self.report({'WARNING'}, 'No Second Clip Found')
        return{'FINISHED'}

class VSEQFQuickFadesTransitionMenu(bpy.types.Menu):
    bl_idname = 'vseqf.quickfades_transition_menu'
    bl_label = 'List Available Transitions'
    def draw(self, context):
        layout = self.layout
        layout.operator("vseqf.quickfades_change_transition", text="Crossfade").transition = "CROSS"
        layout.operator("vseqf.quickfades_change_transition", text="Wipe").transition = "WIPE"
        layout.operator("vseqf.quickfades_change_transition", text="Gamma Cross").transition = "GAMMA_CROSS"

class VSEQFQuickFadesChangeTransition(bpy.types.Operator):
    bl_idname = 'vseqf.quickfades_change_transition'
    bl_label = 'VSEQF Quick Fades Change Transition'
    transition = bpy.props.StringProperty()
    def execute(self, context):
        bpy.context.scene.transition = self.transition
        return{'FINISHED'}


#Classes related to QuickZooms
class VSEQFQuickZoomsMenu(bpy.types.Menu):
    bl_idname = "vseqf.quickzooms_menu"
    bl_label = "Quick Zooms"
    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        layout.operator('vseqf.quickzooms', text='Zoom All').area = 'all'
        if (len(bpy.context.selected_sequences) > 0):
            layout.operator('vseqf.quickzooms', text='Zoom Selected').area = 'selected'
        layout.operator('vseqf.quickzooms', text='Zoom Cursor').area = 'cursor'
        layout.prop(scene, 'zoom', text="Size")

class VSEQFQuickZooms(bpy.types.Operator):
    bl_idname = 'vseqf.quickzooms'
    bl_label = 'VSEQF Quick Zooms'
    bl_description = 'Changes zoom level of the sequencer timeline'
    area = bpy.props.StringProperty()
    def execute(self, context):
        if (self.area == 'all'):
            bpy.ops.sequencer.view_all()
        elif (self.area == 'selected'):
            bpy.ops.sequencer.view_selected()
        elif (self.area == 'cursor'):
            zoom_cursor()
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    #add menus
    bpy.types.SEQUENCER_HT_header.append(draw_quickspeed_header)
    bpy.types.SEQUENCER_MT_view.append(draw_quickzoom_menu)
    bpy.types.SEQUENCER_MT_view.prepend(draw_quickcontinuous_menu)
    bpy.types.SEQUENCER_MT_strip.prepend(draw_quicksnap_menu)
    #register properties
    bpy.types.Scene.step = bpy.props.IntProperty(
        name = "Frame Step",
        default = 0,
        min = 0,
        max = 2)
    bpy.types.Scene.transition = bpy.props.StringProperty(
        name = "Transition Type",
        default = "CROSS")
    bpy.types.Scene.fade = bpy.props.IntProperty(
        name = "Fade Length",
        default = 0,
        min = 0,
        description = "Fade Length In Frames")
    bpy.types.Scene.zoom = bpy.props.IntProperty(
        name = 'Zoom Amount',
        default = 200,
        min = 1,
        description = "Zoom size in frames",
        update = zoom_cursor)
    bpy.types.Scene.parenting = bpy.props.CollectionProperty(type=ParentRelationship)
    bpy.types.Scene.quicktitlerfont = bpy.props.StringProperty(
        name = "Font",
        default = "Bfont",
        description = "Quick Titler Selected Font")
    bpy.types.Scene.quicktitlerx = bpy.props.FloatProperty(
        name = "Text X Location",
        default = 0)
    bpy.types.Scene.quicktitlery = bpy.props.FloatProperty(
        name = "Text Y Location",
        default = -3)
    bpy.types.Scene.quicktitlersize = bpy.props.FloatProperty(
        name = "Text Size",
        default = 1,
        min = 0)
    bpy.types.Scene.quicktitlerextrude = bpy.props.FloatProperty(
        name = "Extrude Amount",
        default = 0,
        min = 0)
    bpy.types.Scene.quicktitlerbevelsize = bpy.props.FloatProperty(
        name = "Bevel Size",
        default = 0,
        min = 0)
    bpy.types.Scene.quicktitlerbevelresolution = bpy.props.IntProperty(
        name = "Bevel Resolution",
        default = 0,
        min = 0)
    bpy.types.Scene.quicktitlertext = bpy.props.StringProperty(
        name = "Text",
        default = "None")
    bpy.types.Scene.quicktitlerlength = bpy.props.IntProperty(
        name = "Scene Length",
        default = 300)
    bpy.types.Scene.quicktitlershadowsize = bpy.props.FloatProperty(
        name = "Shadow Distance",
        default = 1,
        min = 0)
    bpy.types.Scene.quicktitlershadow = bpy.props.FloatProperty(
        name = "Shadow Amount",
        default = 0,
        max = 1,
        min = 0)
    bpy.types.Scene.quicktitlershadowsoft = bpy.props.FloatProperty(
        name = "Shadow Softness",
        default = 1,
        min = 0)
    bpy.types.Scene.quicktitlermaterial = bpy.props.StringProperty(
        name = "Material",
        default = "None")
    bpy.types.Scene.quickcontinuousenable = bpy.props.BoolProperty(
        name = "Enable Continuous Options",
        default = False,
        update = toggle_continuous)
    bpy.types.Scene.quickcontinuousfollow = bpy.props.BoolProperty(
        name = "Cursor Following",
        default = False)
    bpy.types.Scene.quickcontinuoussnap = bpy.props.BoolProperty(
        name = "Clip Auto Snapping",
        default = True)
    bpy.types.Scene.quickcontinuoussnapdistance = bpy.props.IntProperty(
        name = "Snapping Distance Frames",
        default = 5)
    bpy.types.Scene.quickcontinuouschildren = bpy.props.BoolProperty(
        name = "Cut/Move Clip Children",
        default = True)
    bpy.types.Scene.quicklistsort = bpy.props.StringProperty(
        name = "Sort Method",
        default = 'Position')
    #register shortcuts
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW')
    keymapitems = keymap.keymap_items
    for keymapitem in keymapitems:
        if ((keymapitem.type == 'Z') | (keymapitem.type == 'P') | (keymapitem.type == 'F') | (keymapitem.type == 'S')):
            keymapitems.remove(keymapitem)
    keymapzoom = keymapitems.new('wm.call_menu', 'Z', 'PRESS')
    keymapzoom.properties.name = 'vseqf.quickzooms_menu'
    keymapfade = keymapitems.new('wm.call_menu', 'F', 'PRESS')
    keymapfade.properties.name = 'vseqf.quickfades_menu'
    keymapsnap = keymapitems.new('wm.call_menu', 'S', 'PRESS')
    keymapsnap.properties.name = 'vseqf.quicksnaps_menu'
    keymapparent = keymapitems.new('wm.call_menu', 'P', 'PRESS', ctrl=True)
    keymapparent.properties.name = 'vseqf.quickparents_menu'
    keymapparentselect = keymapitems.new('vseqf.quickparents', 'P', 'PRESS', shift=True)
    keymapparentselect.properties.action = 'selectchildren'
    #register handler and modal operator
    handlers = bpy.app.handlers.frame_change_post
    for handler in handlers:
        if (" frame_step " in str(handler)):
            handlers.remove(handler)
    handlers.append(frame_step)
    handlers = bpy.app.handlers.load_post
    for handler in handlers:
        if (" toggle_continuous " in str(handler)):
            handlers.remove(handler)
    handlers.append(toggle_continuous)

def unregister():
    bpy.types.SEQUENCER_HT_header.remove(draw_quickspeed_header)
    bpy.types.SEQUENCER_MT_view.remove(draw_quickzoom_menu)
    bpy.types.SEQUENCER_MT_view.remove(draw_quickcontinuous_menu)
    bpy.types.SEQUENCER_MT_strip.remove(draw_quicksnap_menu)
    del bpy.types.Scene.step
    del bpy.types.Scene.quicklistsort
    keymapitems = bpy.context.window_manager.keyconfigs.addon.keymaps['Sequencer'].keymap_items
    for keymapitem in keymapitems:
        if ((keymapitem.type == 'Z') | (keymapitem.type == 'F') | (keymapitem.type == 'S')):
            keymapitems.remove(keymapitem)
    handlers = bpy.app.handlers.frame_change_post
    for handler in handlers:
        if (" frame_step " in str(handler)):
            handlers.remove(handler)
    handlers = bpy.app.handlers.load_post
    for handler in handlers:
        if (" toggle_continuous " in str(handler)):
            handlers.remove(handler)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
