"""
Name:    texanim
Purpose: Provides operators and functions for the texture animation panel

Description:
Moved from operators and panels here to reduce script line amount

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

import bpy
from . import common
from . import rvstruct
from .common import *


import bpy


class ButtonCopyUvToFrame(bpy.types.Operator):
    bl_idname = "texanim.copy_uv_to_frame"
    bl_label = "UV to Frame"
    bl_description = "Copies the UV coordinates of the currently selected face to the texture animation frame"

    def execute(self, context):
        copy_uv_to_frame(context)
        redraw()
        return{"FINISHED"}

class ButtonCopyFrameToUv(bpy.types.Operator):
    bl_idname = "texanim.copy_frame_to_uv"
    bl_label = "Frame to UV"
    bl_description = "Copies the UV coordinates of the frame to the currently selected face"

    def execute(self, context):
        copy_frame_to_uv(context)
        redraw()
        return{"FINISHED"}


class PreviewNextFrame(bpy.types.Operator):
    bl_idname = "texanim.prev_next"
    bl_label = "Preview Next"
    bl_description = "Loads the next frame and previews it on the selected face"

    def execute(self, context):
        props = context.scene.revolt

        props.ta_current_frame += 1
        copy_frame_to_uv(context)
        return{"FINISHED"}


class PreviewPrevFrame(bpy.types.Operator):
    bl_idname = "texanim.prev_prev"
    bl_label = "Preview Previous"
    bl_description = "Loads the previous frame and previews it on the selected face"

    def execute(self, context):
        props = context.scene.revolt

        props.ta_current_frame -= 1
        copy_frame_to_uv(context)
        return{"FINISHED"}

class TexAnimTransform(bpy.types.Operator):
    bl_idname = "texanim.transform"
    bl_label = "Transform Animation"
    bl_description = "Creates a linear animation from one frame to another"

    frame_start = bpy.props.IntProperty(
        name = "Start Frame",
        description = "Start frame of the animation",
        min = 0
    )
    frame_end = bpy.props.IntProperty(
        name = "End Frame",
        description = "End frame of the animation",
        min = 0,
    )
    delay = bpy.props.FloatProperty(
        name = "Frame duration",
        description = "Duration of every frame",
        min = 0.0,
        default = 0.02,
    )
    texture = bpy.props.IntProperty(
        name = "Texture",
        default = 0,
        min = -1,
        max = 9,
        description = "Texture for every frame"
    )

    def execute(self, context):
        props = context.scene.revolt

        ta = eval(props.texture_animations)
        slot = props.ta_current_slot
        max_frames = props.ta_max_frames

        frame_start = self.frame_start
        frame_end = self.frame_end

        if self.frame_end > max_frames - 1:
            msg_box(
                "Frame out of range.\n"
                "Please set the amount of frames to {}.".format(
                    frame_end + 1),
                "ERROR"
            )

            return {'FINISHED'}
        elif self.frame_start == self.frame_end:
            msg_box("Frame range too short.", "ERROR")
            return {'FINISHED'}


        uv_start = (
            (ta[slot]["frames"][frame_start]["uv"][0]["u"],
             ta[slot]["frames"][frame_start]["uv"][0]["v"]),
            (ta[slot]["frames"][frame_start]["uv"][1]["u"],
             ta[slot]["frames"][frame_start]["uv"][1]["v"]),
            (ta[slot]["frames"][frame_start]["uv"][2]["u"],
             ta[slot]["frames"][frame_start]["uv"][2]["v"]),
            (ta[slot]["frames"][frame_start]["uv"][3]["u"],
             ta[slot]["frames"][frame_start]["uv"][3]["v"])
        )

        uv_end = (
            (ta[slot]["frames"][frame_end]["uv"][0]["u"],
             ta[slot]["frames"][frame_end]["uv"][0]["v"]),
            (ta[slot]["frames"][frame_end]["uv"][1]["u"],
             ta[slot]["frames"][frame_end]["uv"][1]["v"]),
            (ta[slot]["frames"][frame_end]["uv"][2]["u"],
             ta[slot]["frames"][frame_end]["uv"][2]["v"]),
            (ta[slot]["frames"][frame_end]["uv"][3]["u"],
             ta[slot]["frames"][frame_end]["uv"][3]["v"])
        )

        nframes = abs(frame_end - frame_start) + 1

        for i in range(0, nframes):
            current_frame = frame_start + i
            prog = i / (frame_end - frame_start)

            ta[slot]["frames"][frame_start + i]["delay"] = self.delay
            ta[slot]["frames"][frame_start + i]["texture"] = self.texture

            for j in range(0, 4):
                new_u = uv_start[j][0] * (1 - prog) + uv_end[j][0] * prog
                new_v = uv_start[j][1] * (1 - prog) + uv_end[j][1] * prog

                ta[slot]["frames"][frame_start + i]["uv"][j]["u"] = new_u
                ta[slot]["frames"][frame_start + i]["uv"][j]["v"] = new_v

        props.texture_animations = str(ta)
        update_ta_current_frame(self, context)

        msg_box("Animation from frame {} to {} completed.".format(
            frame_start, frame_end),
            icon = "FILE_TICK"
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "frame_start")
        row.prop(self, "frame_end")

        row = layout.row()
        row.prop(self, "delay", icon="PREVIEW_RANGE")
        row.prop(self, "texture", icon="TEXTURE")

class TexAnimGrid(bpy.types.Operator):
    bl_idname = "texanim.grid"
    bl_label = "Grid Animation"
    bl_description = "Creates an animation based on a grid texture."

    frame_start = bpy.props.IntProperty(
        name = "Start Frame",
        min = 0,
        description = "Start frame of the animation"
    )
    grid_x = bpy.props.IntProperty(
        name = "X Resolution",
        min = 1,
        default = 2,
        description = "Amount of frames along the X axis"
    )
    grid_y = bpy.props.IntProperty(
        name = "Y Resolution",
        min = 1,
        default = 2,
        description = "Amount of frames along the Y axis"
    )
    delay = bpy.props.FloatProperty(
        name = "Frame duration",
        description = "Duration of every frame",
        min = 0.0,
        default = 0.02,
    )
    texture = bpy.props.IntProperty(
        name = "Texture",
        default = 0,
        min = -1,
        max = 9,
        description = "Texture for every frame"
    )

    def execute(self, context):
        props = context.scene.revolt

        ta = eval(props.texture_animations)
        slot = props.ta_current_slot
        max_frames = props.ta_max_frames

        frame_start = self.frame_start
        grid_x = self.grid_x
        grid_y = self.grid_y
        nframes = grid_x * grid_y

        if nframes > max_frames:
            msg_box(
                "Frame out of range.\n"
                "Please set the amount of frames to {}.".format(
                    frame_end + 1),
                "ERROR"
            )
            return {'FINISHED'}

        i = 0
        for y in range(grid_x):
            for x in range(grid_y):
                uv0 = (x/grid_x, y/grid_y)
                uv1 = ((x+1)/grid_x, y/grid_y)
                uv2 = ((x+1)/grid_x, (y+1)/grid_y)
                uv3 = (x/grid_x, (y+1)/grid_y)

                ta[slot]["frames"][frame_start + i]["delay"] = self.delay
                ta[slot]["frames"][frame_start + i]["texture"] = self.texture

                ta[slot]["frames"][frame_start + i]["uv"][0]["u"] = uv0[0]
                ta[slot]["frames"][frame_start + i]["uv"][0]["v"] = uv0[1]
                ta[slot]["frames"][frame_start + i]["uv"][1]["u"] = uv1[0]
                ta[slot]["frames"][frame_start + i]["uv"][1]["v"] = uv1[1]
                ta[slot]["frames"][frame_start + i]["uv"][2]["u"] = uv2[0]
                ta[slot]["frames"][frame_start + i]["uv"][2]["v"] = uv2[1]
                ta[slot]["frames"][frame_start + i]["uv"][3]["u"] = uv3[0]
                ta[slot]["frames"][frame_start + i]["uv"][3]["v"] = uv3[1]

                i += 1

        props.texture_animations = str(ta)
        update_ta_current_frame(self, context)

        msg_box("Animation of {} frames completed.".format(
            nframes),
            icon = "FILE_TICK"
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "frame_start")

        row = layout.row(align=True)
        row.prop(self, "grid_x")
        row.prop(self, "grid_y")

        row = layout.row()
        row.prop(self, "delay", icon="PREVIEW_RANGE")
        row.prop(self, "texture", icon="TEXTURE")


def update_ta_max_slots(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    if props.ta_max_slots > 0:
        dprint("TexAnim: Updating max slots..")

        # Converts the texture animations from string to dict
        ta = eval(props.texture_animations)

        # Creates a new texture animation if there is none in the slot
        while len(ta) < props.ta_max_slots:
            dprint("TexAnim: Creating new animation slot... ({}/{})".format(
                len(ta) + 1, props.ta_max_slots)
            )
            ta.append(rvstruct.TexAnimation().as_dict())

        # Saves the texture animation
        props.texture_animations = str(ta)

        # Updates the rest of the UI
        # update_ta_current_slot(self, context)


def update_ta_max_frames(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    # frame = props.ta_current_frame

    dprint("TexAnim: Updating max frames..")
    ta = eval(props.texture_animations)
    ta[slot]["frame_count"] = props.ta_max_frames

    # Creates new empty frames if there are none for the current slot
    while len(ta[slot]["frames"]) < props.ta_max_frames:
        dprint("Creating new animation frame... ({}/{})".format(
            len(ta[slot]["frames"]) + 1, props.ta_max_frames))

        new_frame = rvstruct.Frame().as_dict()
        ta[slot]["frames"].append(new_frame)

    props.texture_animations = str(ta)


def update_ta_current_slot(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    dprint("TexAnim: Updating current slot..")

    # Converts the texture animations from string to dict
    ta = eval(props.texture_animations)

    # Resets the number if it's out of bounds
    if slot > props.ta_max_slots - 1:
        props.ta_current_slot = props.ta_max_slots - 1
        return

    # Saves the texture animations
    props.texture_animations = str(ta)

    # Updates the rest of the UI
    # props.ta_max_frames = len(ta[slot]["frames"])
    props.ta_max_frames = ta[slot]["frame_count"]
    # update_ta_max_frames(self, context)
    update_ta_current_frame(self, context)


# Texture Animation
def update_ta_current_frame(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    dprint("TexAnim: Updating current frame..")

    # Converts the texture animations from string to dict
    ta = eval(props.texture_animations)

    # Resets the number if it's out of bounds
    if frame > props.ta_max_frames - 1:
        props.ta_current_frame = props.ta_max_frames - 1
        return

    props.ta_current_frame_tex = ta[slot]["frames"][frame]["texture"]
    props.ta_current_frame_delay = ta[slot]["frames"][frame]["delay"]
    uv = ta[slot]["frames"][frame]["uv"]
    props.ta_current_frame_uv0 = (uv[3]["u"], 1 - uv[3]["v"])
    props.ta_current_frame_uv1 = (uv[2]["u"], 1 - uv[2]["v"])
    props.ta_current_frame_uv2 = (uv[1]["u"], 1 - uv[1]["v"])
    props.ta_current_frame_uv3 = (uv[0]["u"], 1 - uv[0]["v"])


def update_ta_current_frame_tex(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    dprint("TexAnim: Updating current frame texture..")

    # Converts the texture animations from string to dict
    ta = eval(props.texture_animations)
    # Sets the frame's texture
    ta[slot]["frames"][frame]["texture"] = props.ta_current_frame_tex
    # Saves the string again
    props.texture_animations = str(ta)


def update_ta_current_frame_delay(self, context):
    props = context.scene.revolt
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    dprint("TexAnim: Updating current frame delay..")

    # Converts the texture animations from string to dict
    ta = eval(props.texture_animations)
    # Sets the frame's delay/duration
    ta[slot]["frames"][frame]["delay"] = props.ta_current_frame_delay
    # Saves the string again
    props.texture_animations = str(ta)


def update_ta_current_frame_uv(context, num):
    props = bpy.context.scene.revolt
    prop_str = "ta_current_frame_uv{}".format(num)
    slot = props.ta_current_slot
    frame = props.ta_current_frame

    # Reverses the accessor since they're saved in reverse order
    num = [0, 1, 2, 3][::-1][num]

    dprint("TexAnim: Updating current frame UV for {}..".format(num))

    ta = eval(props.texture_animations)
    ta[slot]["frames"][frame]["uv"][num]["u"] = getattr(props, prop_str)[0]
    ta[slot]["frames"][frame]["uv"][num]["v"] = 1 - getattr(props, prop_str)[1]
    props.texture_animations = str(ta)


def copy_uv_to_frame(context):
    props = context.scene.revolt
    # Copies over UV coordinates from the mesh
    if context.object.data:
        bm = get_edit_bmesh(context.object)
        uv_layer = bm.loops.layers.uv.get("UVMap")
        sel_face = get_active_face(bm)
        if not sel_face:
            msg_box("Please select a face first")
            return
        if not uv_layer:
            msg_box("Please create a UV layer first")
            return
        for lnum in range(len(sel_face.loops)):
            uv = sel_face.loops[lnum][uv_layer].uv
            if lnum == 0:
                props.ta_current_frame_uv0 = (uv[0], uv[1])
            elif lnum == 1:
                props.ta_current_frame_uv1 = (uv[0], uv[1])
            elif lnum == 2:
                props.ta_current_frame_uv2 = (uv[0], uv[1])
            elif lnum == 3:
                props.ta_current_frame_uv3 = (uv[0], uv[1])
    else:
        dprint("No object for UV anim")


def copy_frame_to_uv(context):
    props = context.scene.revolt
    if context.object.data:
        bm = get_edit_bmesh(context.object)
        uv_layer = bm.loops.layers.uv.get("UVMap")
        sel_face = get_active_face(bm)
        if not sel_face:
            msg_box("Please select a face first")
            return
        if not uv_layer:
            msg_box("Please create a UV layer first")
            return
        for lnum in range(len(sel_face.loops)):
            uv0 = props.ta_current_frame_uv0
            uv1 = props.ta_current_frame_uv1
            uv2 = props.ta_current_frame_uv2
            uv3 = props.ta_current_frame_uv3
            if lnum == 0:
                sel_face.loops[lnum][uv_layer].uv = uv0
            elif lnum == 1:
                sel_face.loops[lnum][uv_layer].uv = uv1
            elif lnum == 2:
                sel_face.loops[lnum][uv_layer].uv = uv2
            elif lnum == 3:
                sel_face.loops[lnum][uv_layer].uv = uv3
    else:
        dprint("No object for UV anim")
