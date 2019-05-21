import os

import bpy


preview_collections = {}


def load_icons():
    if 'icon32' in preview_collections:
        return

    pcoll = bpy.utils.previews.new()
    icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
    pcoll.load('set_plane', os.path.join(icon_dir, 'set_plane.png'), 'IMAGE')
    pcoll.load('set_axis', os.path.join(icon_dir, 'set_axis.png'), 'IMAGE')
    pcoll.load('align', os.path.join(icon_dir, 'align.png'), 'IMAGE')
    pcoll.load('align_to_plane',
               os.path.join(icon_dir, 'align_to_plane.png'), 'IMAGE')
    pcoll.load('distribute', os.path.join(icon_dir, 'distribute.png'), 'IMAGE')
    pcoll.load('edge_align_to_plane',
               os.path.join(icon_dir, 'edge_align_to_plane.png'), 'IMAGE')
    pcoll.load('edge_intersect',
               os.path.join(icon_dir, 'edge_intersect.png'), 'IMAGE')
    pcoll.load('edge_unbend',
               os.path.join(icon_dir, 'edge_unbend.png'), 'IMAGE')
    pcoll.load('shift_tangent',
               os.path.join(icon_dir, 'shift_tangent.png'), 'IMAGE')
    pcoll.load('shift_normal',
               os.path.join(icon_dir, 'shift_normal.png'), 'IMAGE')
    pcoll.load('mode_center',
               os.path.join(icon_dir, 'mode_center.png'), 'IMAGE')
    pcoll.load('mode_negative',
               os.path.join(icon_dir, 'mode_negative.png'), 'IMAGE')
    pcoll.load('mode_positive',
               os.path.join(icon_dir, 'mode_positive.png'), 'IMAGE')
    pcoll.load('mode_pivot',
               os.path.join(icon_dir, 'mode_pivot.png'), 'IMAGE')
    pcoll.load('mode_dimension',
               os.path.join(icon_dir, 'mode_dimension.png'), 'IMAGE')

    preview_collections['icon32'] = pcoll


def unload_icons():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
