# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   blend/animation.py
# Date:   2014-11-05
# Author: Peter Felfer
#
# Description:
# Blender script for setting up animation
# =============================================================================

import bpy

# === Constants ===
START_FRAME = 1

# === Defaults ===
CAM_ORTH_SCALE  = 150               # Orthographic scale of camera
CAM_CLIP_DIST   = 500
TIME            = 4                 # Seconds
FPS             = 25
ROT_ANGLE       = 360 * 3.1416/180  # Angle the camera will rotate in rad
RESX            = 1024
RESY            = 1024

def add(target,
        offset,
        cam_orth_scale=CAM_ORTH_SCALE,
        cam_clip_dist=CAM_CLIP_DIST,
        time=TIME,
        fps=FPS,
        rot_angle=ROT_ANGLE,
        resx=RESX,
        resy=RESY
        ):
    # Scene setup
    end_frame = START_FRAME + time * fps - 1

    bpy.context.scene.frame_start =  START_FRAME
    bpy.context.scene.frame_end =  end_frame

    for scene in bpy.data.scenes:
        scene.render.resolution_x = resx
        scene.render.resolution_y = resy

    bpy.ops.object.select_all(action='DESELECT')

    # Create objects
    # Empties (act as reference coordinates)
    bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=target)
    bpy.context.object.empty_draw_size = 20
    bpy.context.object.name = "Cam master"

    bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=target)
    bpy.context.object.empty_draw_size = 20
    bpy.context.object.name = "Cam target"


    # Camera + constraint
    bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=offset, rotation=(0,0,0))
    bpy.context.object.name = "Animation cam"
    bpy.context.object.data.type = 'ORTHO'
    bpy.context.object.data.ortho_scale = cam_orth_scale
    bpy.context.object.data.show_limits = True
    bpy.context.object.data.clip_end = cam_clip_dist

    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.object.constraints["Track To"].target = bpy.data.objects["Cam target"]
    bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
    bpy.context.object.data.show_guide = {'THIRDS'}

    # Set parenting
    master = bpy.data.objects['Cam master']
    target = bpy.data.objects['Cam target']

    master.select = True
    target.select = True

    bpy.context.scene.objects.active = master
    bpy.ops.object.parent_set()

    bpy.ops.object.select_all(action='DESELECT') # Deselect all

    # Add animation
    master.select = True
    bpy.context.scene.objects.active = master

    # Set rotation for first frame
    bpy.context.scene.frame_set(START_FRAME)
    bpy.ops.anim.keyframe_insert(type='Rotation')
    # Set rotation for last frame
    bpy.context.scene.frame_set(end_frame)
    master.rotation_euler = (0, 0, rot_angle)
    bpy.ops.anim.keyframe_insert(type='Rotation')

    # Turn graph handles to vector
    old_area_type = bpy.context.area.type

    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.handle_type(type='VECTOR')
    bpy.ops.graph.extrapolation_type(type='LINEAR')

    bpy.context.area.type = old_area_type
