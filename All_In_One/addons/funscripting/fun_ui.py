# ##### BEGIN BSD LICENSE BLOCK #####
#
# Copyright 2017 Funjack
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ##### END BSD LICENSE BLOCK #####

import bpy
import json
from bpy_extras.io_utils import ExportHelper,ImportHelper

from . import fun_script

class FunscriptSettings(bpy.types.PropertyGroup):
    """Funscript Settings.

    Funscript user settings that are used by all other components.
    """
    script_range = bpy.props.IntProperty(
        name = "Range",
        description = "Range of the Launch to use",
        subtype = "PERCENTAGE",
        default = 90,
        min = 10,
        max = 100)
    script_min_speed = bpy.props.IntProperty(
        name = "Min speed",
        description="Minimal speed to hint for",
        subtype = "PERCENTAGE",
        default = 20,
        min = 20,
        max = 80)
    script_max_speed = bpy.props.IntProperty(
        name = "Max speed",
        description="Maximum speed to hint for",
        subtype = "PERCENTAGE",
        default = 80,
        min = 20,
        max = 90)
    script_interval = bpy.props.IntProperty(
        name = "Min interval",
        description="Minimal interval in ms to alert on",
        subtype = "TIME",
        default = 150,
        min = 100,
        max = 200)

class FunscriptPanel(bpy.types.Panel):
    """Funscript UI panel.

    Funscript UI panel added to the sequencer.
    """
    bl_label = "Funscript"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return context.selected_sequences is not None \
                and len(context.selected_sequences) == 1

    def limitinfo(self, context):
        """Labels with hints of the limitations"""
        scene = context.scene
        settings = scene.funscripting
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        layout = self.layout
        row = layout.row(align=True)
        box = row.box()
        bcol = box.column(align=True)
        row = bcol.row(align=True)
        col = row.column(align=True)
        last = {"frame":1, "value":0}
        if keyframes is not None:
            for kf in reversed(keyframes):
                frame = kf.co[0]
                value = kf.co[1]
                if frame > scene.frame_current:
                    continue
                if frame < scene.frame_current:
                    last = {"frame":frame, "value":value}
                    break
        interval = fun_script.frame_to_ms(scene.frame_current) - fun_script.frame_to_ms(last["frame"])
        icon = "FILE_TICK" if interval > settings.script_interval or last["frame"] == 1 else "ERROR"
        if interval > 1000:
            icon = "TIME"
        mindist = int(fun_script.launch_distance(settings.script_min_speed, interval) * (100.0/settings.script_range))
        maxdist = int(fun_script.launch_distance(settings.script_max_speed, interval) * (100.0/settings.script_range))

        col.label(text="Previous: %d" % last["value"])
        col = row.column(align=True)
        col.operator("funscript.delete", text="Delete").last=True
        row = bcol.row(align=True)
        col = row.column(align=True)
        col.label(text="Interval: %d ms" % interval, icon=icon)
        row = bcol.row(align=True)
        col = row.column(align=True)
        col.label("Slowest: %d" % mindist)
        col = row.column(align=True)
        col.label("Fastest: %d" % maxdist)
        row = bcol.row(align=True)
        col = row.column(align=True)
        laststroke = fun_script.last_stroke(seq, scene.frame_current)
        if laststroke is not None:
            up = fun_script.frame_to_ms(laststroke[1]["frame"])
            down = fun_script.frame_to_ms(laststroke[2]["frame"])
            col.label("Last stroke: %d+%d=%d ms" % (up, down, up+down))

    def draw(self, context):
        self.limitinfo(context)
        layout = self.layout
        row = layout.row(align=True)
        box = row.box()
        bcol = box.column(align=True)
        bcol.label(text="Insert position")
        for x in [100, 70, 40, 10, 0]:
            row = bcol.row(align=True)
            row.alignment = 'EXPAND'
            if x == 0 or x == 100:
                label = "%d (%s)" % (x, "Up" if x == 100 else "Down")
                row.operator("funscript.position", text=label).launchPosition=x
            else:
                for i in range(x,x+30,10):
                    row.operator("funscript.position", text=str(i)).launchPosition=i
        row = bcol.row(align=True)
        row.operator("funscript.positionlimit", text="Same").limitType="same"
        row.operator("funscript.positionlimit", text="Shortest").limitType="shortest"
        row.operator("funscript.positionlimit", text="Longest").limitType="longest"

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        box = row.box()
        bcol = box.column(align=True)
        bcol.label(text="Generate actions")
        row = bcol.row(align=True)
        row.operator("funscript.repeat")
        row.operator("funscript.fill")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        box = row.box()
        bcol = box.column(align=True)
        bcol.label(text="Selection operations")
        row = bcol.row(align=True)
        row.operator("funscript.selectionaverage")
        row.operator("funscript.selectioninvert")
        row = bcol.row(align=True)
        row.operator("funscript.selectionshiftleft")
        row.operator("funscript.selectionshiftright")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        box = row.box()
        bcol = box.column(align=True)
        bcol.label("Import/Export Funscript")
        row = bcol.row(align=True)
        row.operator("funscript.import")
        row = bcol.row(align=True)
        row.operator("funscript.export")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        box = row.box()
        bcol = box.column(align=True)
        bcol.label("Hint settings")
        row = bcol.row(align=True)
        row.prop(context.scene.funscripting, "script_range")
        row.prop(context.scene.funscripting, "script_interval")
        row = bcol.row(align=True)
        row.prop(context.scene.funscripting, "script_min_speed")
        row.prop(context.scene.funscripting, "script_max_speed")


class FunscriptPositionButton(bpy.types.Operator):
    """Position input button.

    Button that inserts a Launch position in the currently selected Sequence.
    """
    bl_idname = "funscript.position"
    bl_label = "Position"
    bl_options = {'REGISTER', 'UNDO'}
    launchPosition = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        fun_script.insert_position(seq, self.launchPosition, scene.frame_current)
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}

class FunscriptPositionLimitButton(bpy.types.Operator):
    """Position input button based on a limit.

    Button that inserts a Launch position in the currently selected Sequence
    based on the limit.
    """
    bl_idname = "funscript.positionlimit"
    bl_label = "Position limit"
    bl_options = {'REGISTER', 'UNDO'}
    limitType = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        settings = scene.funscripting
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)

        # XXX clean this up :)
        beforelast = {"frame":1, "value":0}
        last = {"frame":1, "value":0}
        if keyframes is not None:
            for kf in reversed(keyframes):
                frame = kf.co[0]
                value = kf.co[1]
                if last["frame"] > 1:
                    beforelast = {"frame":frame, "value":value}
                    break
                if frame > scene.frame_current:
                    continue
                if frame < scene.frame_current:
                    last = {"frame":frame, "value":value}
        direction = "up" if last["value"] < beforelast["value"] or last["value"] == 0 else "down"
        interval = fun_script.frame_to_ms(scene.frame_current) - fun_script.frame_to_ms(last["frame"])
        mindist = int(fun_script.launch_distance(settings.script_min_speed, interval) * (100.0/settings.script_range))
        maxdist = int(fun_script.launch_distance(settings.script_max_speed, interval) * (100.0/settings.script_range))
        value = 0
        if self.limitType == "same":
            dist = abs(last["value"] - beforelast["value"])
            value = last["value"]+dist if direction == "up" else last["value"]-dist
        elif self.limitType == "shortest":
            value = last["value"]+mindist if direction == "up" else last["value"]-mindist
        elif self.limitType == "longest":
            value = last["value"]+maxdist if direction == "up" else last["value"]-maxdist
        else:
            self.report({'ERROR_INVALID_CONTEXT'}, "Invalid limit operation.")
            return{'CANCELLED'}
        fun_script.insert_position(seq, fun_script.clamp(value), scene.frame_current)
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}

class FunscriptDeleteButton(bpy.types.Operator):
    """Position delete button.

    Button that deletes a Launch position from the currently selected Sequence.
    """
    bl_idname = "funscript.delete"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}
    frame = bpy.props.IntProperty()
    last = bpy.props.BoolProperty()

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        delete_frame = self.frame
        if self.last:
            keyframes = fun_script.launch_keyframes(seq.name)
            last = {"frame":1, "value":0}
            if keyframes is not None:
                for kf in reversed(keyframes):
                    frame = kf.co[0]
                    value = kf.co[1]
                    if frame > scene.frame_current:
                        continue
                    if frame < scene.frame_current:
                        last = {"frame":frame, "value":value}
                        break
            delete_frame = last["frame"]
        fun_script.delete_position(seq, delete_frame)
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}

class FunscriptRepeatButton(bpy.types.Operator):
    """Repeat last stroke button.

    Button that will repeat the last stroke on the selected sequence.
    """
    bl_idname = "funscript.repeat"
    bl_label = "Repeat stroke"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        lastframe = fun_script.repeat_stroke(seq, scene.frame_current)
        if lastframe is not None:
            scene.frame_set(lastframe)
        return{'FINISHED'}

class FunscriptFillButton(bpy.types.Operator):
    """Fill last stroke button.

    Button that will repeat the last stroke on the selected sequence until the
    current frame is reached.
    """
    bl_idname = "funscript.fill"
    bl_label = "Fill stroke"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        lastframe = fun_script.repeat_fill_stroke(seq, scene.frame_current)
        if lastframe is not None:
            scene.frame_set(lastframe)
        return{'FINISHED'}

class FunscriptExport(bpy.types.Operator, ExportHelper):
    """Export as Funscript file button.

    Button that exports all Launch position keyframes in the sequences as
    Funscript file.
    """
    bl_idname = "funscript.export"
    bl_label = "Export as Funscript"

    filename_ext = ".funscript"
    filter_glob = bpy.props.StringProperty(
            default="*.funscript",
            options={'HIDDEN'},
            maxlen=255,
            )
    inverted = bpy.props.BoolProperty(name="inverted",
        description="Flip up and down positions", default=False)

    def execute(self, context):
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        script = fun_script.create_funscript(
                keyframes,
                self.inverted,
                context.scene.funscripting.script_range)
        with open(self.filepath, 'w') as outfile:
            json.dump(script, outfile)
        return {'FINISHED'}

class FunscriptImport(bpy.types.Operator, ImportHelper):
    """Import as Funscript file button.

    Button that imports Launch position keyframes in the sequences from a
    Funscript file.
    """
    bl_idname = "funscript.import"
    bl_label = "Import Funscript on frame"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".funscript"
    filter_glob = bpy.props.StringProperty(
            default="*.funscript",
            options={'HIDDEN'},
            maxlen=255,
            )

    def execute(self, context):
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        with open(self.filepath) as infile:
            fs = json.load(infile)
            if not "actions" in fs:
                self.report({'ERROR_INVALID_INPUT'}, "Input is not valid funscript.")
                return{'CANCELLED'}
            fun_script.insert_actions(seq, fs["actions"], context.scene.frame_current)
        return {'FINISHED'}

class FunscriptSelectionInvert(bpy.types.Operator):
    """Invert the Launch value for selected points.

    Button that will invert the Launch value for all the selected keyframes.
    """
    bl_idname = "funscript.selectioninvert"
    bl_label = "Invert"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        fun_script.invert_launch_values(fun_script.selected_keyframes(keyframes))
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}

class FunscriptSelectionShiftRight(bpy.types.Operator):
    """Shift all the Launch values for selected points to the right.

    Button that will shift all values one keyframe to the right.
    """
    bl_idname = "funscript.selectionshiftright"
    bl_label = "Shift right"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        fun_script.shift_launch_values(fun_script.selected_keyframes(keyframes))
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}


class FunscriptSelectionShiftLeft(bpy.types.Operator):
    """Shift all the Launch values for selected points to the left.

    Button that will shift all values one keyframe to the left.
    """
    bl_idname = "funscript.selectionshiftleft"
    bl_label = "Shift left"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        fun_script.shift_launch_values(reversed(list(fun_script.selected_keyframes(keyframes))))
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}

class FunscriptSelectionAverage(bpy.types.Operator):
    """Average out the the Launch values of all even and odd points.

    Button that will average out the values in all the even points and odd
    points resulting a stable stroke pattern.
    """
    bl_idname = "funscript.selectionaverage"
    bl_label = "Average"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if len(context.selected_sequences) < 1:
            self.report({'ERROR_INVALID_CONTEXT'}, "No sequence selected.")
            return{'CANCELLED'}
        seq = context.selected_sequences[0]
        keyframes = fun_script.launch_keyframes(seq.name)
        fun_script.average_even_odd_keyframes(fun_script.selected_keyframes(keyframes))
        scene.frame_set(scene.frame_current)
        return{'FINISHED'}
