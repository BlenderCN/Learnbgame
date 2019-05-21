"""TODO: DOC"""

# import os
import struct

import bpy

from . import nax2
from . import nax3


def create_anims(context, nax_groups, nax_keys, nax_curves):
    """TODO: DOC"""
    scene = bpy.context.scene
    for obj in scene:
        pass


def load_nax2(context, filepath):
    """TODO: DOC"""
    with open(filepath, mode='rb') as f:
        # Read header
        header = nax2.Header._make(struct.unpack('<4s2i', f.read(12)))
        # Read groups
        sfmt = '<4i2f1i512s'
        ssize = struct.calcsize(sfmt)
        nax2_groups = [nax2.Group._make(struct.unpack(sfmt, f.read(ssize)))
                       for i in range(header.num_groups)]
        # Read curves, num_curves = (nc = nc+g.num_curves for g in nax2_groups)
        sfmt = '<3i4f'
        ssize = struct.calcsize(sfmt)
        nax2_curves = []
        for g in nax2_groups:
            per_group_curves = []
            nax2_curves.append(per_group_curves)
            for i in range(g.num_curves):
                cdata = struct.unpack(sfmt, f.read(ssize))
                curve = nax2.Curve(ipol_type=cdata[0],
                                   first_key_idx=cdata[1],
                                   curve_type=i % 3,
                                   is_static=(-1 == cdata[1]),
                                   static_key=(tuple(cdata[3:])))
                per_group_curves.append(curve)
        # Read keys
        sfmt = '<4f'
        ssize = 16
        nax2_keys = [struct.unpack(sfmt, f.read(ssize))
                     for i in range(header.num_keys)]

        create_anims(context, nax2_groups, nax2_curves, [], nax2_keys)
    return {'FINISHED'}


def load_nax3(context, filepath):
    """TODO: DOC"""
    # nax 3 is: header, list of (clip, event list, curve list), list of keys
    with open(filepath, mode='rb') as f:
        # Read header
        header = nax3.Header._make(struct.unpack('<4s2i', f.read(12)))
        # Read Clips, events and curves
        nax3_clips = []
        cl_fmt = '<5H2B1H64s'
        cl_size = struct.calcsize(cl_fmt)
        nax3_events = []
        ev_fmt = '<47s15s1H'
        ev_size = struct.calcsize(ev_fmt)
        nax3_curves = []
        cv_fmt = '<1i3B1B4f'
        cv_size = struct.calcsize(cv_fmt)
        for cl_idx in range(header.num_clips):
            # Read clip data
            clip = nax3.Clip._make(struct.unpack(cl_fmt, f.read(cl_size)))
            nax3_clips.append(clip)
            # Read events
            per_clip_events = \
                [nax3.Event._make(struct.unpack(ev_fmt, f.read(ev_size)))
                 for i in range(clip.num_events)]
            nax3_events.append(per_clip_events)
            # Read curves
            per_clip_curves = \
                [nax3.CurveRaw._make(struct.unpack(cv_fmt, f.read(cv_size)))
                 for i in range(clip.num_curves)]
            nax3_curves.append(per_clip_curves)
        # Read keys
        k_fmt = '<4f'
        k_size = 16
        nax2_keys = [struct.unpack(k_fmt, f.read(k_size))
                     for i in range(header.num_keys)]

        create_anims(context, nax3_clips, nax3_curves, nax3_events, nax2_keys)
    return {'FINISHED'}


def load(context,
         filepath=''):
    """Called by the user interface or another script."""
    # only nax2, nax3 seems to be unimplemented
    load_nax2(context, filepath)

    return {'CANCELLED'}
