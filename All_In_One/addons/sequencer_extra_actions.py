# <pep8 compliant>
#
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

bl_info = {
    'name': 'Extra Sequencer Actions',
    'author': 'Turi Scandurra',
    'version': (2, 0),
    'blender': (2, 6, 2, 1),
    'api': 44812,
    'category': 'Sequencer',
    'location': 'Sequencer',
    'description': 'Collection of extra operators to manipulate VSE strips',
    'wiki_url': 'http://wiki.blender.org/index.php/'
    'Extensions:2.6/Py/Scripts/Sequencer/Extra_Sequencer_Actions',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?func=detail'\
        '&aid=30474',
    'support': 'COMMUNITY'}

'''
Usage:
    - Install the script by copying its .py file to your Blender addons
        folder. Enable the script in User Preferences > Addons > Sequencer.
        The script is composed of a collection of several operators placed in
        different locations.

    Location: Timeline > Frame
    - Trim to Timeline Content
        Automatically set start and end frames of current scene according to
        the content of the Sequence Editor.
    - Trim to Selection
        Set start and end frames of current scene to match selected strips
        in the Sequence Editor.

    Location: Video Sequence Editor > Select
    - Select All by Type
        Select all the strips of the specified type in the Sequence Editor.
    - Current-Frame-Aware Select
        Select strips on all channels according to current frame. Available
        modes are:
        Before (select all strips before current frame),
        After (select all strips after current frame),
        On (select all strips underneath playhead).
    - Inverse
        Inverse the selection of strips.

    Location: Video Sequence Editor > Strip
    - Ripple Delete
        Delete the active strip and shift back all other strips the number of
        frames between the beginning of deleted strip and the next edit in the
        sequence.
    - Ripple Cut
        Same as above, but copying active strip to memory buffer before
        deleting it. Copied strip can be pasted in place as usual, for example
        using the keystroke combination ctrl-V.
    - Insert
        Shift forward all strips after current frame and insert active strip.
    - Insert (Single Channel)
        Same as above, but shifting occurs only on the same channel as active
        strip.
    - Slide
        Alter in and out points of a strip but not its duration. Only available
        when a the type of active strip is Movie, Scene or Meta.
        Click 'Input...' to choose the amount of sliding desired. The start and
        end frame of active strip will be moved, but its length and position
        will remain unchanged. This action is also known as slipping.
        Click 'Current Frame to Start' or 'Current Frame to End' to perform the
        slide according to current frame.
    - Slide Grab
        Same as above, interactive mode. Move mouse cursor along X axis to jog.
        To exit, click left or right mouse button or hit ESC.
    - Copy Properties
        Copy properties of active strip to selected strips. Start selecting
        multiple strips, then make active the strip whose properties need to be
        copied to the selected strips. Click the desired operator to perform
        the action. Some operators affect single properties, while some others
        affect a group of properties.
    - Fade
        Fade opacity of active strip, or its volume if its type is Sound,
        creating keyframes for the corresponding property.
        Possible fade directions are In, Out, In and Out.
        Duration defines the number of frames between the start and the end
        of the fade.
        Amount defines the maximum value that the fade will set. For opacity
        fades, the maximum value is 1.0.
        The minimum value reached by the fade is always 0.
        Keyframes created with this operator can be manipulated through the
        F-Curve Editor.
    - Distribute
        Evenly distribute selected strips along the timeline according to a
        specified offset. This operator is useful to reassign strip length to
        every element of an image sequence.
        The operator also allows to reverse the order of the distributed
        strips.
        To perform a simple reversion of an image sequence, first separate its
        images and select them, then run Distribute with Offset set to 1 and
        Reverse Order enabled.

    Location: Video Sequence Editor > Input
    - Open with Editor
        Open active strip with Movie Clip Editor or Image Editor, according to
        strip type. If a clip is already loaded, existing data is used.
    - Open with External Editor
        Open active image strip with the default external image editor. To use
        this operator a valid path to the external editor must be specified in
        User Preferences > File.
    - File Name to Strip Name
        Set strip name to input file name. This operator is useful after
        separating images of a sequence.

    Location: Video Sequence Editor
    - File Place
        Place active file from File Browser to Sequencer Editor on current
        frame.
    - File Insert
        Same as above, but also shift forward forward all strips after current
        frame.
    - Navigate Up
        Move current view to parent timeline. Only enabled when current view is
        relative to a Meta strip. This operator does not perform any
        modification to timeline elements.

    Location: Movie Clip Editor
    - Open from File Browser
        Load a Movie or Image Sequence from File Browser to Movie Clip Editor.
        If a clip is already loaded, existing data is used.
    - Open Active Strip
        Load a Movie or Image Sequence from Sequence Editor to Movie Clip
        Editor. If a clip is already loaded, existing data is used.

    Location: Movie Clip Editor, Video Sequence Editor (with preview), Timeline
    - Jog/Shuttle
        Jog through current sequence, looping between start and end frames.
        This action is known as jogging, shuttling or scrubbing.
        Click the operator to enter interactive mode. Move mouse cursor along X
        axis to jog. To exit, click left or right mouse button or hit ESC.

    Location: Timeline, Video Sequence Editor
    - Skip One Second
        Skip through the Timeline by one-second increments. The number of
        frames to skip is based on render settings for current scene.
        The script enables two new key bindings:
        ctrl + shift + left arrow to skip back one second,
        ctrl + shift + right arrow to skip forward one second.

Discussion:
    - http://blenderartists.org/forum/showthread.php?
    248129-Extra-Sequencer-Actions

Version History:
    - http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Sequencer/
    Extra_Sequencer_Actions/version_history
'''

import bpy
import os.path

from bpy.types import Menu
from bpy.types import Header

from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import EnumProperty
from bpy.props import BoolProperty


# ##### UTILS #####
def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def detect_strip_type(filepath):
    imb_ext_image = [
    # IMG
    ".png",
    ".tga",
    ".bmp",
    ".jpg", ".jpeg",
    ".sgi", ".rgb", ".rgba",
    ".tif", ".tiff", ".tx",
    ".jp2",
    ".hdr",
    ".dds",
    ".dpx",
    ".cin",
    ".exr",
    # IMG QT
    ".gif",
    ".psd",
    ".pct", ".pict",
    ".pntg",
    ".qtif",
    ]

    imb_ext_movie = [
    ".avi",
    ".flc",
    ".mov",
    ".movie",
    ".mp4",
    ".m4v",
    ".m2v",
    ".m2t",
    ".m2ts",
    ".mts",
    ".mv",
    ".avs",
    ".wmv",
    ".ogv",
    ".dv",
    ".mpeg",
    ".mpg",
    ".mpg2",
    ".vob",
    ".mkv",
    ".flv",
    ".divx",
    ".xvid",
    ".mxf",
    ]

    imb_ext_audio = [
    ".wav",
    ".ogg",
    ".oga",
    ".mp3",
    ".mp2",
    ".ac3",
    ".aac",
    ".flac",
    ".wma",
    ".eac3",
    ".aif",
    ".aiff",
    ".m4a",
    ]

    extension = os.path.splitext(filepath)[1]
    extension = extension.lower()
    if extension in imb_ext_image:
        type = 'IMAGE'
    elif extension in imb_ext_movie:
        type = 'MOVIE'
    elif extension in imb_ext_audio:
        type = 'SOUND'
    else:
        type = None

    return type


# ##### INITIALIZATION #####
def initSceneProperties(scn):
    try:
        if bpy.context.scene.scene_initialized == True:
            return False
    except AttributeError:
        pass

    bpy.types.Scene.default_slide_offset = IntProperty(
    name='Offset',
    description='Number of frames to slide',
    min=-250, max=250,
    default=0)
    scn.default_slide_offset = 0

    bpy.types.Scene.default_fade_duration = IntProperty(
    name='Duration',
    description='Number of frames to fade',
    min=1, max=250,
    default=scn.render.fps)
    scn.default_fade_duration = scn.render.fps

    bpy.types.Scene.default_fade_amount = FloatProperty(
        name='Amount',
        description='Maximum value of fade',
        min=0.0,
        max=100.0,
        default=1.0)
    scn.default_fade_amount = 1.0

    bpy.types.Scene.default_distribute_offset = IntProperty(
        name='Offset',
        description='Number of frames between strip start frames',
        min=1,
        max=250,
        default=2)
    scn.default_distribute_offset = 2

    bpy.types.Scene.default_distribute_reverse = BoolProperty(
        name='Reverse Order',
        description='Reverse the order of selected strips',
        default=False)
    scn.default_distribute_reverse = False

    bpy.types.Scene.scene_initialized = BoolProperty(
        name='Init',
        default=False)
    scn.scene_initialized = True

    return True


# ##### CLASSES #####

# TRIM TIMELINE
class Sequencer_Extra_TrimTimeline(bpy.types.Operator):
    bl_label = 'Trim to Timeline Content'
    bl_idname = 'timeextra.trimtimeline'
    bl_description = 'Automatically set start and end frames'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]

        frame_start = 300000
        frame_end = -300000
        for i in seq.sequences:
            try:
                if i.frame_final_start < frame_start:
                    frame_start = i.frame_final_start
                if i.frame_final_end > frame_end:
                    frame_end = i.frame_final_end - 1
            except AttributeError:
                    pass

        if frame_start != 300000:
            scn.frame_start = frame_start
        if frame_end != -300000:
            scn.frame_end = frame_end
        return {'FINISHED'}


# TRIM TIMELINE TO SELECTION
class Sequencer_Extra_TrimTimelineToSelection(bpy.types.Operator):
    bl_label = 'Trim to Selection'
    bl_idname = 'timeextra.trimtimelinetoselection'
    bl_description = 'Set start and end frames to selection'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]

        frame_start = 300000
        frame_end = -300000
        for i in seq.sequences:
            try:
                if i.frame_final_start < frame_start and i.select == True:
                    frame_start = i.frame_final_start
                if i.frame_final_end > frame_end and i.select == True:
                    frame_end = i.frame_final_end - 1
            except AttributeError:
                    pass

        if frame_start != 300000:
            scn.frame_start = frame_start
        if frame_end != -300000:
            scn.frame_end = frame_end
        return {'FINISHED'}


# SLIDE STRIP
class Sequencer_Extra_SlideStrip(bpy.types.Operator):
    bl_label = 'Slide'
    bl_idname = 'sequencerextra.slide'
    bl_description = 'Alter in and out points but not duration of a strip'
    mode = EnumProperty(
        name='Mode',
        items=(
        ('TOSTART', 'Current Frame to Strip Start', ''),
        ('TOEND', 'Current Frame to Strip End', ''),
        ('INPUT', 'Input...', '')),
        default='INPUT',
        options={'HIDDEN'}
        )
    bl_options = {'REGISTER', 'UNDO'}

    initSceneProperties(bpy.context.scene)

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return strip.type in ('MOVIE', 'IMAGE', 'META', 'SCENE')
        else:
            return False

    slide_offset = bpy.types.Scene.default_slide_offset

    def execute(self, context):
        strip = act_strip(context)
        scn = context.scene
        cf = scn.frame_current

        if self.mode == 'TOSTART':
            sx = strip.frame_final_start - cf
        elif self.mode == 'TOEND':
            sx = strip.frame_final_end - cf
        else:
            sx = self.slide_offset

        frame_end = strip.frame_start + strip.frame_duration
        pad_left = strip.frame_final_start - strip.frame_start
        pad_right = (frame_end - strip.frame_final_end) * -1

        if sx > pad_left:
            sx = pad_left
        elif sx < pad_right:
            sx = pad_right

        strip.frame_start += sx
        strip.frame_final_start -= sx
        strip.frame_final_end -= sx

        self.report({'INFO'}, 'Strip slid %d frame(s)' % (sx))
        scn.default_slide_offset = sx
        bpy.ops.sequencer.reload()
        return {'FINISHED'}

    def invoke(self, context, event):
        scn = context.scene
        self.slide_offset = scn.default_slide_offset
        if self.mode == 'INPUT':
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


# SLIDE GRAB
class Sequencer_Extra_SlideGrab(bpy.types.Operator):
    bl_label = 'Slide Grab'
    bl_idname = 'sequencerextra.slidegrab'
    bl_description = 'Alter in and out points but not duration of a strip'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return strip.type in ('MOVIE', 'IMAGE', 'META', 'SCENE')
        else:
            return False

    def execute(self, context):
        strip = act_strip(context)
        scn = context.scene

        diff = self.prev_x - self.x
        self.prev_x = self.x
        sx = int(diff / 2)

        frame_end = strip.frame_start + strip.frame_duration
        pad_left = strip.frame_final_start - strip.frame_start
        pad_right = (frame_end - strip.frame_final_end) * -1

        if sx > pad_left:
            sx = pad_left
        elif sx < pad_right:
            sx = pad_right

        strip.frame_start += sx
        strip.frame_final_start -= sx
        strip.frame_final_end -= sx

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.x = event.mouse_x
            self.execute(context)
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scn = context.scene
        self.x = event.mouse_x
        self.prev_x = event.mouse_x
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# FILE NAME TO STRIP NAME
class Sequencer_Extra_FileNameToStripName(bpy.types.Operator):
    bl_label = 'File Name to Selected Strips Name'
    bl_idname = 'sequencerextra.striprename'
    bl_description = 'Set strip name to input file name'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        selection = False
        for i in seq.sequences:
            if i.select == True:
                if i.type == 'IMAGE' and not i.mute:
                    selection = True
                    i.name = i.elements[0].filename
                if (i.type == 'SOUND' or i.type == 'MOVIE') and not i.mute:
                    selection = True
                    i.name = bpy.path.display_name_from_filepath(i.filepath)
        if selection == False:
            self.report({'ERROR_INVALID_INPUT'},
            'No image or movie strip selected')
            return {'CANCELLED'}
        return {'FINISHED'}


# NAVIGATE UP
class Sequencer_Extra_NavigateUp(bpy.types.Operator):
    bl_label = 'Navigate Up'
    bl_idname = 'sequencerextra.navigateup'
    bl_description = 'Move to Parent Timeline'

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        try:
            if context.scene.sequence_editor.meta_stack:
                return True
            else:
                return False
        except:
            return False

    def execute(self, context):
        if (act_strip(context)):
            strip = act_strip(context)
            seq_type = strip.type
            if seq_type == 'META':
                context.scene.sequence_editor.active_strip = None

        bpy.ops.sequencer.meta_toggle()
        return {'FINISHED'}


# RIPPLE DELETE
class Sequencer_Extra_RippleDelete(bpy.types.Operator):
    bl_label = 'Ripple Delete'
    bl_idname = 'sequencerextra.rippledelete'
    bl_description = 'Delete a strip and shift back following ones'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return True
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        strip = act_strip(context)
        cut_frame = strip.frame_final_start
        next_edit = 300000
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        bpy.ops.sequencer.delete()
        striplist = []
        for i in seq.sequences:
            try:
                if (i.frame_final_start > cut_frame
                and not i.mute):
                    if i.frame_final_start < next_edit:
                        next_edit = i.frame_final_start
                if not i.mute:
                    striplist.append(i)
            except AttributeError:
                    pass

        if next_edit == 300000:
            return {'FINISHED'}
        ripple_length = next_edit - cut_frame
        for i in range(len(striplist)):
            str = striplist[i]
            try:
                if str.frame_final_start > cut_frame:
                    str.frame_start = str.frame_start - ripple_length
            except AttributeError:
                    pass

        bpy.ops.sequencer.reload()
        return {'FINISHED'}


# RIPPLE CUT
class Sequencer_Extra_RippleCut(bpy.types.Operator):
    bl_label = 'Ripple Cut'
    bl_idname = 'sequencerextra.ripplecut'
    bl_description = 'Move a strip to buffer and shift back following ones'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return True
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        strip = act_strip(context)
        bpy.ops.sequencer.select_all(action='DESELECT')
        strip.select = True
        temp_cf = scn.frame_current
        scn.frame_current = strip.frame_final_start
        bpy.ops.sequencer.copy()
        scn.frame_current = temp_cf

        bpy.ops.sequencerextra.rippledelete()
        return {'FINISHED'}


# INSERT
class Sequencer_Extra_Insert(bpy.types.Operator):
    bl_label = 'Insert'
    bl_idname = 'sequencerextra.insert'
    bl_description = 'Move active strip to current frame and shift '\
    'forward following ones'
    singlechannel = BoolProperty(
    name='Single Channel',
    default=False
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return True
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        strip = act_strip(context)
        gap = strip.frame_final_duration
        bpy.ops.sequencer.select_all(action='DESELECT')
        current_frame = scn.frame_current

        striplist = []
        for i in seq.sequences:
            try:
                if (i.frame_final_start >= current_frame
                and not i.mute):
                    if self.singlechannel == True:
                        if i.channel == strip.channel:
                            striplist.append(i)
                    else:
                        striplist.append(i)
            except AttributeError:
                    pass
        try:
            bpy.ops.sequencerextra.selectcurrentframe('EXEC_DEFAULT',
            mode='AFTER')
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'Execution Error, '\
            'check your Blender version')
            return {'CANCELLED'}

        for i in range(len(striplist)):
            str = striplist[i]
            try:
                if str.select == True:
                    str.frame_start += gap
            except AttributeError:
                    pass
        try:
            diff = current_frame - strip.frame_final_start
            strip.frame_start += diff
        except AttributeError:
                pass

        strip = act_strip(context)
        scn.frame_current += strip.frame_final_duration
        bpy.ops.sequencer.reload()

        return {'FINISHED'}


# PLACE FROM FILE BROWSER
class Sequencer_Extra_PlaceFromFileBrowser(bpy.types.Operator):
    bl_label = 'Place'
    bl_idname = 'sequencerextra.placefromfilebrowser'
    bl_description = 'Place or insert active file from File Browser'
    insert = BoolProperty(
    name='Insert',
    default=False
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                break
        try:
            params
        except UnboundLocalError:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if params.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}
        path = params.directory + params.filename
        frame = context.scene.frame_current
        strip_type = detect_strip_type(params.filename)

        try:
            if strip_type == 'IMAGE':
                image_file = []
                filename = {"name": params.filename}
                image_file.append(filename)
                f_in = scn.frame_current
                f_out = f_in + scn.render.fps - 1
                bpy.ops.sequencer.image_strip_add(files=image_file,
                directory=params.directory, frame_start=f_in,
                frame_end=f_out, relative_path=False)
            elif strip_type == 'MOVIE':
                bpy.ops.sequencer.movie_strip_add(filepath=path,
                frame_start=frame, relative_path=False)
            elif strip_type == 'SOUND':
                bpy.ops.sequencer.sound_strip_add(filepath=path,
                frame_start=frame, relative_path=False)
            else:
                self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
                return {'CANCELLED'}
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'Error loading file')
            return {'CANCELLED'}

        if self.insert == True:
            try:
                bpy.ops.sequencerextra.insert()
            except:
                self.report({'ERROR_INVALID_INPUT'}, 'Execution Error, '\
                'check your Blender version')
                return {'CANCELLED'}
        else:
            strip = act_strip(context)
            scn.frame_current += strip.frame_final_duration
            bpy.ops.sequencer.reload()

        return {'FINISHED'}


# SELECT BY TYPE
class Sequencer_Extra_SelectAllByType(bpy.types.Operator):
    bl_label = 'All by Type'
    bl_idname = 'sequencerextra.select_all_by_type'
    bl_description = 'Select all the strips of the same type'
    type = EnumProperty(
            name='Strip Type',
            items=(
            ('ACTIVE', 'Same as Active Strip', ''),
            ('IMAGE', 'Image', ''),
            ('META', 'Meta', ''),
            ('SCENE', 'Scene', ''),
            ('MOVIE', 'Movie', ''),
            ('SOUND', 'Sound', ''),
            ('TRANSFORM', 'Transform', ''),
            ('COLOR', 'Color', '')),
            default='ACTIVE',
            )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        strip_type = self.type
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        active_strip = act_strip(context)
        if strip_type == 'ACTIVE':
            if active_strip == None:
                self.report({'ERROR_INVALID_INPUT'},
                'No active strip')
                return {'CANCELLED'}
            strip_type = active_strip.type

        striplist = []
        for i in seq.sequences:
            try:
                if (i.type == strip_type
                and not i.mute):
                    striplist.append(i)
            except AttributeError:
                    pass
        for i in range(len(striplist)):
            str = striplist[i]
            try:
                str.select = True
            except AttributeError:
                    pass

        return {'FINISHED'}


# CURRENT-FRAME-AWARE SELECT
class Sequencer_Extra_SelectCurrentFrame(bpy.types.Operator):
    bl_label = 'Current-Frame-Aware Select'
    bl_idname = 'sequencerextra.selectcurrentframe'
    bl_description = 'Select strips according to current frame'
    mode = EnumProperty(
            name='Mode',
            items=(
            ('BEFORE', 'Before Current Frame', ''),
            ('AFTER', 'After Current Frame', ''),
            ('ON', 'On Current Frame', '')),
            default='BEFORE',
            )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        mode = self.mode
        scn = context.scene
        seq = scn.sequence_editor
        cf = scn.frame_current
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]

        if mode == 'AFTER':
            for i in seq.sequences:
                try:
                    if (i.frame_final_start >= cf
                    and not i.mute):
                        i.select = True
                except AttributeError:
                        pass
        elif mode == 'ON':
            for i in seq.sequences:
                try:
                    if (i.frame_final_start <= cf
                    and i.frame_final_end > cf
                    and not i.mute):
                        i.select = True
                except AttributeError:
                        pass
        else:
            for i in seq.sequences:
                try:
                    if (i.frame_final_end < cf
                    and not i.mute):
                        i.select = True
                except AttributeError:
                        pass

        return {'FINISHED'}


# SELECT INVERSE
class Sequencer_Extra_SelectInverse(bpy.types.Operator):
    bl_label = 'Inverse'
    bl_idname = 'sequencerextra.selectinverse'
    bl_description = 'Inverse selection of strips'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]

        for i in seq.sequences:
            try:
                if (i.select == False
                and not i.mute):
                    i.select = True
                else:
                    i.select = False
            except AttributeError:
                    pass

        return {'FINISHED'}


# OPEN IMAGE WITH EXTERNAL EDITOR
class Sequencer_Extra_EditExternally(bpy.types.Operator):
    bl_label = 'Open with External Editor'
    bl_idname = 'sequencerextra.editexternally'
    bl_description = 'Open with the default external image editor'

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return strip.type == 'IMAGE'
        else:
            return False

    def execute(self, context):
        strip = act_strip(context)
        scn = context.scene
        base_dir = bpy.path.abspath(strip.directory)
        strip_elem = strip.getStripElem(scn.frame_current)
        path = base_dir + strip_elem.filename

        try:
            bpy.ops.image.external_edit(filepath=path)
        except:
            self.report({'ERROR_INVALID_INPUT'},
            'Please specify an Image Editor in Preferences > File')
            return {'CANCELLED'}

        return {'FINISHED'}


# OPEN IMAGE WITH EDITOR
class Sequencer_Extra_Edit(bpy.types.Operator):
    bl_label = 'Open with Editor'
    bl_idname = 'sequencerextra.edit'
    bl_description = 'Open with Movie Clip or Image Editor'

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return strip.type in ('MOVIE', 'IMAGE')
        else:
            return False

    def execute(self, context):
        strip = act_strip(context)
        scn = context.scene
        data_exists = False

        if strip.type == 'MOVIE':
            path = strip.filepath

            for i in bpy.data.movieclips:
                if i.filepath == path:
                    data_exists = True
                    data = i

            if data_exists == False:
                try:
                    data = bpy.data.movieclips.load(filepath=path)
                except:
                    self.report({'ERROR_INVALID_INPUT'}, 'Error loading file')
                    return {'CANCELLED'}

        elif strip.type == 'IMAGE':
            base_dir = bpy.path.abspath(strip.directory)
            strip_elem = strip.getStripElem(scn.frame_current)
            elem_name = strip_elem.filename
            path = base_dir + elem_name

            for i in bpy.data.images:
                if i.filepath == path:
                    data_exists = True
                    data = i

            if data_exists == False:
                try:
                    data = bpy.data.images.load(filepath=path)
                except:
                    self.report({'ERROR_INVALID_INPUT'}, 'Error loading file')
                    return {'CANCELLED'}

        if strip.type == 'MOVIE':
            for a in context.window.screen.areas:
                if a.type == 'CLIP_EDITOR':
                    a.spaces[0].clip = data
        elif strip.type == 'IMAGE':
            for a in context.window.screen.areas:
                if a.type == 'IMAGE_EDITOR':
                    a.spaces[0].image = data

        return {'FINISHED'}


# COPY STRIP PROPERTIES
class Sequencer_Extra_CopyProperties(bpy.types.Operator):
    bl_label = 'Copy Properties'
    bl_idname = 'sequencerextra.copyproperties'
    bl_description = 'Copy properties of active strip to selected strips'
    bl_options = {'REGISTER', 'UNDO'}

    prop = EnumProperty(
    name='Property',
    items=[
    # COMMON
    ('name', 'Name', ''),
    ('blend_alpha', 'Opacity', ''),
    ('blend_type', 'Blend Mode', ''),
    ('animation_offset', 'Input - Trim Duration', ''),
    # NON-SOUND
    ('use_translation', 'Input - Image Offset', ''),
    ('crop', 'Input - Image Crop', ''),
    ('proxy', 'Proxy / Timecode', ''),
    ('strobe', 'Filter - Strobe', ''),
    ('color_balance', 'Filter - Color Balance', ''),
    ('color_multiply', 'Filter - Multiply', ''),
    ('color_saturation', 'Filter - Saturation', ''),
    ('deinterlace', 'Filter - De-Interlace', ''),
    ('flip', 'Filter - Flip', ''),
    ('float', 'Filter - Convert Float', ''),
    ('premultiply', 'Filter - Premultiply', ''),
    ('reverse', 'Filter - Backwards', ''),
    # SOUND
    ('pan', 'Sound - Pan', ''),
    ('pitch', 'Sound - Pitch', ''),
    ('volume', 'Sound - Volume', ''),
    ('cache', 'Sound - Caching', ''),
    # IMAGE
    ('directory', 'Image - Directory', ''),
    # MOVIE
    ('mpeg_preseek', 'Movie - MPEG Preseek', ''),
    ('stream_index', 'Movie - Stream Index', ''),
    # WIPE
    ('wipe', 'Effect - Wipe', ''),
    # TRANSFORM
    ('transform', 'Effect - Transform', ''),
    # COLOR
    ('color', 'Effect - Color', ''),
    # SPEED
    ('speed', 'Effect - Speed', ''),
    # MULTICAM
    ('multicam_source', 'Effect - Multicam Source', ''),
    # EFFECT
    ('effect_fader', 'Effect - Effect Fader', ''),
    ],
    default='blend_alpha')

    @classmethod
    def poll(self, context):
        strip = act_strip(context)
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return True
        else:
            return False

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        strip = act_strip(context)

        for i in seq.sequences:
            if (i.select == True and not i.mute):
                try:
                    if self.prop == 'name':
                        i.name = strip.name
                    elif self.prop == 'blend_alpha':
                        i.blend_alpha = strip.blend_alpha
                    elif self.prop == 'blend_type':
                        i.blend_type = strip.blend_type
                    elif self.prop == 'animation_offset':
                        i.animation_offset_start = strip.animation_offset_start
                        i.animation_offset_end = strip.animation_offset_end
                    elif self.prop == 'use_translation':
                        i.use_translation = strip.use_translation
                        i.transform.offset_x = strip.transform.offset_x
                        i.transform.offset_y = strip.transform.offset_y
                    elif self.prop == 'crop':
                        i.use_crop = strip.use_crop
                        i.crop.min_x = strip.crop.min_x
                        i.crop.min_y = strip.crop.min_y
                        i.crop.max_x = strip.crop.max_x
                        i.crop.max_y = strip.crop.max_y
                    elif self.prop == 'proxy':
                        i.use_proxy = strip.use_proxy
                        i.use_proxy_custom_file = strip.use_proxy_custom_file
                        p = strip.use_proxy_custom_directory  # pep80
                        i.use_proxy_custom_directory = p
                        i.proxy.filepath = strip.proxy.filepath
                        i.proxy.directory = strip.proxy.directory
                        i.proxy.build_25 = strip.proxy.build_25
                        i.proxy.build_50 = strip.proxy.build_50
                        i.proxy.build_75 = strip.proxy.build_75
                        i.proxy.build_100 = strip.proxy.build_100
                        i.proxy.quality = strip.proxy.quality
                        i.proxy.timecode = strip.proxy.timecode
                    elif self.prop == 'strobe':
                        i.strobe = strip.strobe
                    elif self.prop == 'color_balance':
                        i.use_color_balance = strip.use_color_balance
                        i.use_color_balance = strip.use_color_balance
                        i.color_balance.lift = strip.color_balance.lift
                        i.color_balance.gamma = strip.color_balance.gamma
                        i.color_balance.gain = strip.color_balance.gain
                        p = strip.color_balance.invert_lift  # pep80
                        i.color_balance.invert_lift = p
                        p = strip.color_balance.invert_gamma  # pep80
                        i.color_balance.invert_gamma = p
                        p = strip.color_balance.invert_gain  # pep80
                        i.color_balance.invert_gain = p
                    elif self.prop == 'color_multiply':
                        i.color_multiply = strip.color_multiply
                    elif self.prop == 'color_saturation':
                        i.color_saturation = strip.color_saturation
                    elif self.prop == 'deinterlace':
                        i.use_deinterlace = strip.use_deinterlace
                    elif self.prop == 'flip':
                        i.use_flip_x = strip.use_flip_x
                        i.use_flip_y = strip.use_flip_y
                    elif self.prop == 'float':
                        i.use_float = strip.use_float
                    elif self.prop == 'premultiply':
                        i.use_premultiply = strip.use_premultiply
                    elif self.prop == 'reverse':
                        i.use_reverse_frames = strip.use_reverse_frames
                    elif self.prop == 'pan':
                        i.pan = strip.pan
                    elif self.prop == 'pitch':
                        i.pitch = strip.pitch
                    elif self.prop == 'volume':
                        i.volume = strip.volume
                    elif self.prop == 'cache':
                        i.use_memory_cache = strip.use_memory_cache
                    elif self.prop == 'directory':
                        i.directory = strip.directory
                    elif self.prop == 'mpeg_preseek':
                        i.mpeg_preseek = strip.mpeg_preseek
                    elif self.prop == 'stream_index':
                        i.stream_index = strip.stream_index
                    elif self.prop == 'wipe':
                        i.angle = strip.angle
                        i.blur_width = strip.blur_width
                        i.direction = strip.direction
                        i.transition_type = strip.transition_type
                    elif self.prop == 'transform':
                        i.interpolation = strip.interpolation
                        i.rotation_start = strip.rotation_start
                        i.use_uniform_scale = strip.use_uniform_scale
                        i.scale_start_x = strip.scale_start_x
                        i.scale_start_y = strip.scale_start_y
                        i.translation_unit = strip.translation_unit
                        i.translate_start_x = strip.translate_start_x
                        i.translate_start_y = strip.translate_start_y
                    elif self.prop == 'color':
                        i.color = strip.color
                    elif self.prop == 'speed':
                        i.use_default_fade = strip.use_default_fade
                        i.speed_factor = strip.speed_factor
                        i.use_as_speed = strip.use_as_speed
                        i.scale_to_length = strip.scale_to_length
                        i.multiply_speed = strip.multiply_speed
                        i.use_frame_blend = strip.use_frame_blend
                    elif self.prop == 'multicam_source':
                        i.multicam_source = strip.multicam_source
                    elif self.prop == 'effect_fader':
                        i.use_default_fade = strip.use_default_fade
                        i.effect_fader = strip.effect_fader
                except:
                    pass

        bpy.ops.sequencer.reload()
        return {'FINISHED'}


# FADE IN AND OUT
class Sequencer_Extra_FadeInOut(bpy.types.Operator):
    bl_idname = 'sequencerextra.fadeinout'
    bl_label = 'Fade...'
    bl_description = 'Fade volume or opacity of active strip'
    mode = EnumProperty(
            name='Direction',
            items=(
            ('IN', 'Fade In...', ''),
            ('OUT', 'Fade Out...', ''),
            ('INOUT', 'Fade In and Out...', '')),
            default='IN',
            )
    bl_options = {'REGISTER', 'UNDO'}

    initSceneProperties(bpy.context.scene)

    @classmethod
    def poll(cls, context):
        scn = context.scene
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return True
        else:
            return False

    fade_duration = bpy.types.Scene.default_fade_duration
    fade_amount = bpy.types.Scene.default_fade_amount

    def execute(self, context):
        seq = context.scene.sequence_editor
        scn = context.scene
        strip = seq.active_strip
        tmp_current_frame = context.scene.frame_current

        if strip.type == 'SOUND':
            if(self.mode) == 'OUT':
                scn.frame_current = strip.frame_final_end - self.fade_duration
                strip.volume = self.fade_amount
                strip.keyframe_insert('volume')
                scn.frame_current = strip.frame_final_end
                strip.volume = 0
                strip.keyframe_insert('volume')
            elif(self.mode) == 'INOUT':
                scn.frame_current = strip.frame_final_start
                strip.volume = 0
                strip.keyframe_insert('volume')
                scn.frame_current += self.fade_duration
                strip.volume = self.fade_amount
                strip.keyframe_insert('volume')
                scn.frame_current = strip.frame_final_end - self.fade_duration
                strip.volume = self.fade_amount
                strip.keyframe_insert('volume')
                scn.frame_current = strip.frame_final_end
                strip.volume = 0
                strip.keyframe_insert('volume')
            else:
                scn.frame_current = strip.frame_final_start
                strip.volume = 0
                strip.keyframe_insert('volume')
                scn.frame_current += self.fade_duration
                strip.volume = self.fade_amount
                strip.keyframe_insert('volume')

        else:
            if(self.mode) == 'OUT':
                scn.frame_current = strip.frame_final_end - self.fade_duration
                strip.blend_alpha = self.fade_amount
                strip.keyframe_insert('blend_alpha')
                scn.frame_current = strip.frame_final_end
                strip.blend_alpha = 0
                strip.keyframe_insert('blend_alpha')
            elif(self.mode) == 'INOUT':
                scn.frame_current = strip.frame_final_start
                strip.blend_alpha = 0
                strip.keyframe_insert('blend_alpha')
                scn.frame_current += self.fade_duration
                strip.blend_alpha = self.fade_amount
                strip.keyframe_insert('blend_alpha')
                scn.frame_current = strip.frame_final_end - self.fade_duration
                strip.blend_alpha = self.fade_amount
                strip.keyframe_insert('blend_alpha')
                scn.frame_current = strip.frame_final_end
                strip.blend_alpha = 0
                strip.keyframe_insert('blend_alpha')
            else:
                scn.frame_current = strip.frame_final_start
                strip.blend_alpha = 0
                strip.keyframe_insert('blend_alpha')
                scn.frame_current += self.fade_duration
                strip.blend_alpha = self.fade_amount
                strip.keyframe_insert('blend_alpha')

        scn.frame_current = tmp_current_frame

        scn.default_fade_duration = self.fade_duration
        scn.default_fade_amount = self.fade_amount
        return{'FINISHED'}

    def invoke(self, context, event):
        scn = context.scene
        self.fade_duration = scn.default_fade_duration
        self.fade_amount = scn.default_fade_amount
        return context.window_manager.invoke_props_dialog(self)


# DISTRIBUTE
class Sequencer_Extra_Distribute(bpy.types.Operator):
    bl_idname = 'sequencerextra.distribute'
    bl_label = 'Distribute...'
    bl_description = 'Evenly distribute selected strips'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        scn = context.scene
        if scn and scn.sequence_editor:
            return scn.sequence_editor.sequences
        else:
            return False

    initSceneProperties(bpy.context.scene)

    distribute_offset = bpy.types.Scene.default_distribute_offset
    distribute_reverse = bpy.types.Scene.default_distribute_reverse

    def execute(self, context):
        scn = context.scene
        seq = scn.sequence_editor
        seq_all = scn.sequence_editor
        meta_level = len(seq.meta_stack)
        if meta_level > 0:
            seq = seq.meta_stack[meta_level - 1]
        seq_list = {}
        first_start = 300000
        item_num = 0
        for i in seq.sequences:
            if i.select == True:
                seq_list[i.frame_start] = i.name
                item_num += 1
                if i.frame_start < first_start:
                    first_start = i.frame_start
        n = item_num - 1
        if(self.distribute_reverse):
            for key in sorted(seq_list.keys()):
                dest = first_start + (n * self.distribute_offset)
                seq_all.sequences_all[str(seq_list[key])].frame_start = dest
                n -= 1
        else:
            for key in sorted(seq_list.keys(), reverse=True):
                dest = first_start + (n * self.distribute_offset)
                seq_all.sequences_all[str(seq_list[key])].frame_start = dest
                n -= 1

        scn.default_distribute_offset = self.distribute_offset
        scn.default_distribute_reverse = self.distribute_reverse
        return{'FINISHED'}

    def invoke(self, context, event):
        scn = context.scene
        self.distribute_offset = scn.default_distribute_offset
        self.distribute_reverse = scn.default_distribute_reverse
        return context.window_manager.invoke_props_dialog(self)


# SKIP ONE SECOND
class Sequencer_Extra_FrameSkip(bpy.types.Operator):
    bl_label = 'Skip One Second'
    bl_idname = 'screenextra.frame_skip'
    bl_description = 'Skip through the Timeline by one-second increments'
    bl_options = {'REGISTER', 'UNDO'}
    back = BoolProperty(
        name='Back',
        default=False
        )

    def execute(self, context):
        one_second = bpy.context.scene.render.fps
        if self.back == True:
            one_second *= -1
        bpy.ops.screen.frame_offset(delta=one_second)
        return {'FINISHED'}


# JOG/SHUTTLE
class Sequencer_Extra_JogShuttle(bpy.types.Operator):
    bl_label = 'Jog/Shuttle'
    bl_idname = 'sequencerextra.jogshuttle'
    bl_description = 'Jog through current sequence'

    def execute(self, context):
        scn = context.scene
        start_frame = scn.frame_start
        end_frame = scn.frame_end
        duration = end_frame - start_frame
        diff = self.x - self.init_x
        diff /= 5
        diff = int(diff)
        extended_frame = diff + (self.init_current_frame - start_frame)
        looped_frame = extended_frame % (duration + 1)
        target_frame = start_frame + looped_frame
        context.scene.frame_current = target_frame

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.x = event.mouse_x
            self.execute(context)
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scn = context.scene
        self.x = event.mouse_x
        self.init_x = self.x
        self.init_current_frame = scn.frame_current
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# OPEN IN MOVIE CLIP EDITOR FROM FILE BROWSER
class Clip_Extra_OpenFromFileBrowser(bpy.types.Operator):
    bl_label = 'Open from File Browser'
    bl_idname = 'clipextra.openfromfilebrowser'
    bl_description = 'Load a Movie or Image Sequence from File Browser'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for a in context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                break
        try:
            params
        except:
            self.report({'ERROR_INVALID_INPUT'}, 'No visible File Browser')
            return {'CANCELLED'}

        if params.filename == '':
            self.report({'ERROR_INVALID_INPUT'}, 'No file selected')
            return {'CANCELLED'}

        strip = act_strip(context)
        path = params.directory + params.filename
        strip_type = detect_strip_type(params.filename)
        data_exists = False

        if strip_type in ('MOVIE', 'IMAGE'):
            for i in bpy.data.movieclips:
                if i.filepath == path:
                    data_exists = True
                    data = i

            if data_exists == False:
                try:
                    data = bpy.data.movieclips.load(filepath=path)
                except:
                    self.report({'ERROR_INVALID_INPUT'}, 'Error loading file')
                    return {'CANCELLED'}
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}

        for a in context.window.screen.areas:
            if a.type == 'CLIP_EDITOR':
                a.spaces[0].clip = data

        return {'FINISHED'}


# OPEN IN MOVIE CLIP EDITOR FROM SEQUENCER
class Clip_Extra_OpenActiveStrip(bpy.types.Operator):
    bl_label = 'Open Active Strip'
    bl_idname = 'clipextra.openactivestrip'
    bl_description = 'Load a Movie or Image Sequence from Sequence Editor'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scn = context.scene
        strip = act_strip(context)
        if scn and scn.sequence_editor and scn.sequence_editor.active_strip:
            return strip.type in ('MOVIE', 'IMAGE')
        else:
            return False

    def execute(self, context):
        strip = act_strip(context)
        data_exists = False

        if strip.type == 'MOVIE':
            path = strip.filepath
        elif strip.type == 'IMAGE':
            base_dir = bpy.path.relpath(strip.directory)
            filename = strip.elements[0].filename
            path = base_dir + '/' + filename
        else:
            self.report({'ERROR_INVALID_INPUT'}, 'Invalid file format')
            return {'CANCELLED'}

        for i in bpy.data.movieclips:
            if i.filepath == path:
                data_exists = True
                data = i
        if data_exists == False:
            try:
                data = bpy.data.movieclips.load(filepath=path)
            except:
                self.report({'ERROR_INVALID_INPUT'}, 'Error loading file')
                return {'CANCELLED'}

        for a in context.window.screen.areas:
            if a.type == 'CLIP_EDITOR':
                a.spaces[0].clip = data

        return {'FINISHED'}


# ##### UI #####
class SEQUENCER_EXTRA_MT_input(Menu):
    bl_label = "Input"

    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator('sequencerextra.striprename',
        text='File Name to Strip Name', icon='PLUGIN')
        self.layout.operator('sequencerextra.editexternally',
        text='Open with External Editor', icon='PLUGIN')
        self.layout.operator('sequencerextra.edit',
        text='Open with Editor', icon='PLUGIN')


def sequencer_select_menu_func(self, context):
    self.layout.operator_menu_enum('sequencerextra.select_all_by_type',
    'type', text='All by Type', icon='PLUGIN')
    self.layout.separator()
    self.layout.operator('sequencerextra.selectinverse',
    text='Inverse', icon='PLUGIN')
    self.layout.separator()
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='Before Current Frame', icon='PLUGIN').mode = 'BEFORE'
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='After Current Frame', icon='PLUGIN').mode = 'AFTER'
    self.layout.operator('sequencerextra.selectcurrentframe',
    text='On Current Frame', icon='PLUGIN').mode = 'ON'
    self.layout.separator()


def sequencer_strip_menu_func(self, context):
    self.layout.operator('sequencerextra.distribute',
    text='Distribute', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.fadeinout',
    'mode', text='Fade', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.copyproperties',
    'prop', icon='PLUGIN')
    self.layout.operator('sequencerextra.slidegrab',
    text='Slide Grab', icon='PLUGIN')
    self.layout.operator_menu_enum('sequencerextra.slide',
    'mode', icon='PLUGIN')
    self.layout.operator('sequencerextra.insert',
    text='Insert (Single Channel)', icon='PLUGIN').singlechannel = True
    self.layout.operator('sequencerextra.insert',
    text='Insert', icon='PLUGIN')
    self.layout.operator('sequencerextra.ripplecut',
    text='Ripple Cut', icon='PLUGIN')
    self.layout.operator('sequencerextra.rippledelete',
    text='Ripple Delete', icon='PLUGIN')
    self.layout.separator()


def sequencer_header_func(self, context):
    self.layout.menu("SEQUENCER_EXTRA_MT_input")
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowser',
        text='File Place', icon='PLUGIN')
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.placefromfilebrowser',
        text='File Insert', icon='PLUGIN').insert = True
    if context.space_data.view_type in ('PREVIEW', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.jogshuttle',
        text='Jog/Shuttle', icon='PLUGIN')
    if context.space_data.view_type in ('SEQUENCER', 'SEQUENCER_PREVIEW'):
        self.layout.operator('sequencerextra.navigateup',
        text='Navigate Up', icon='PLUGIN')


def time_frame_menu_func(self, context):
    self.layout.operator('timeextra.trimtimelinetoselection',
    text='Trim to Selection', icon='PLUGIN')
    self.layout.operator('timeextra.trimtimeline',
    text='Trim to Timeline Content', icon='PLUGIN')
    self.layout.separator()
    self.layout.operator('screenextra.frame_skip',
    text='Skip Forward One Second', icon='PLUGIN')
    self.layout.operator('screenextra.frame_skip',
    text='Skip Back One Second', icon='PLUGIN').back = True
    self.layout.separator()


def time_header_func(self, context):
    self.layout.operator('sequencerextra.jogshuttle',
    text='Jog/Shuttle', icon='PLUGIN')


def clip_header_func(self, context):
    self.layout.operator('sequencerextra.jogshuttle',
    text='Jog/Shuttle', icon='PLUGIN')


def clip_clip_menu_func(self, context):
    self.layout.operator('clipextra.openactivestrip',
    text='Open Active Strip', icon='PLUGIN')
    self.layout.operator('clipextra.openfromfilebrowser',
    text='Open from File Browser', icon='PLUGIN')
    self.layout.separator()


# ##### REGISTRATION #####
def register():
    bpy.utils.register_class(Sequencer_Extra_TrimTimeline)
    bpy.utils.register_class(Sequencer_Extra_TrimTimelineToSelection)
    bpy.utils.register_class(Sequencer_Extra_SlideStrip)
    bpy.utils.register_class(Sequencer_Extra_SlideGrab)
    bpy.utils.register_class(Sequencer_Extra_FileNameToStripName)
    bpy.utils.register_class(Sequencer_Extra_NavigateUp)
    bpy.utils.register_class(Sequencer_Extra_RippleDelete)
    bpy.utils.register_class(Sequencer_Extra_RippleCut)
    bpy.utils.register_class(Sequencer_Extra_Insert)
    bpy.utils.register_class(Sequencer_Extra_PlaceFromFileBrowser)
    bpy.utils.register_class(Sequencer_Extra_SelectAllByType)
    bpy.utils.register_class(Sequencer_Extra_SelectInverse)
    bpy.utils.register_class(Sequencer_Extra_SelectCurrentFrame)
    bpy.utils.register_class(Sequencer_Extra_Edit)
    bpy.utils.register_class(Sequencer_Extra_EditExternally)
    bpy.utils.register_class(Sequencer_Extra_CopyProperties)
    bpy.utils.register_class(Sequencer_Extra_FadeInOut)
    bpy.utils.register_class(Sequencer_Extra_Distribute)
    bpy.utils.register_class(Sequencer_Extra_FrameSkip)
    bpy.utils.register_class(Sequencer_Extra_JogShuttle)
    bpy.utils.register_class(Clip_Extra_OpenFromFileBrowser)
    bpy.utils.register_class(Clip_Extra_OpenActiveStrip)
    bpy.utils.register_class(SEQUENCER_EXTRA_MT_input)
    bpy.types.SEQUENCER_MT_select.prepend(sequencer_select_menu_func)
    bpy.types.SEQUENCER_MT_strip.prepend(sequencer_strip_menu_func)
    bpy.types.SEQUENCER_HT_header.append(sequencer_header_func)
    bpy.types.CLIP_HT_header.append(clip_header_func)
    bpy.types.CLIP_MT_clip.prepend(clip_clip_menu_func)
    bpy.types.TIME_MT_frame.prepend(time_frame_menu_func)
    bpy.types.TIME_HT_header.append(time_header_func)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Frames')
    kmi = km.keymap_items.new('screenextra.frame_skip',
    'RIGHT_ARROW', 'PRESS', ctrl=True, shift=True)
    kmi.properties.back = False
    kmi = km.keymap_items.new('screenextra.frame_skip',
    'LEFT_ARROW', 'PRESS', ctrl=True, shift=True)
    kmi.properties.back = True


def unregister():
    bpy.utils.unregister_class(Sequencer_Extra_TrimTimeline)
    bpy.utils.unregister_class(Sequencer_Extra_TrimTimelineToSelection)
    bpy.utils.unregister_class(Sequencer_Extra_SlideStrip)
    bpy.utils.unregister_class(Sequencer_Extra_SlideGrab)
    bpy.utils.unregister_class(Sequencer_Extra_FileNameToStripName)
    bpy.utils.unregister_class(Sequencer_Extra_NavigateUp)
    bpy.utils.unregister_class(Sequencer_Extra_RippleDelete)
    bpy.utils.unregister_class(Sequencer_Extra_RippleCut)
    bpy.utils.unregister_class(Sequencer_Extra_Insert)
    bpy.utils.unregister_class(Sequencer_Extra_PlaceFromFileBrowser)
    bpy.utils.unregister_class(Sequencer_Extra_SelectAllByType)
    bpy.utils.unregister_class(Sequencer_Extra_SelectInverse)
    bpy.utils.unregister_class(Sequencer_Extra_SelectCurrentFrame)
    bpy.utils.unregister_class(Sequencer_Extra_Edit)
    bpy.utils.unregister_class(Sequencer_Extra_EditExternally)
    bpy.utils.unregister_class(Sequencer_Extra_CopyProperties)
    bpy.utils.unregister_class(Sequencer_Extra_FadeInOut)
    bpy.utils.unregister_class(Sequencer_Extra_Distribute)
    bpy.utils.unregister_class(Sequencer_Extra_FrameSkip)
    bpy.utils.unregister_class(Sequencer_Extra_JogShuttle)
    bpy.utils.unregister_class(Clip_Extra_OpenFromFileBrowser)
    bpy.utils.unregister_class(Clip_Extra_OpenActiveStrip)
    bpy.utils.unregister_class(SEQUENCER_EXTRA_MT_input)
    bpy.types.SEQUENCER_MT_select.remove(sequencer_select_menu_func)
    bpy.types.SEQUENCER_MT_strip.remove(sequencer_strip_menu_func)
    bpy.types.SEQUENCER_HT_header.remove(sequencer_header_func)
    bpy.types.CLIP_HT_header.remove(clip_header_func)
    bpy.types.CLIP_MT_clip.remove(clip_clip_menu_func)
    bpy.types.TIME_MT_frame.remove(time_frame_menu_func)
    bpy.types.TIME_HT_header.remove(time_header_func)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps['Frames']
    km.keymap_items.remove(km.keymap_items['screenextra.frame_skip'])
    km.keymap_items.remove(km.keymap_items['screenextra.frame_skip'])


if __name__ == '__main__':
    register()
