"""Code used both by creation.py and pose_thumbnails.py"""

import os.path

import bpy


def get_thumbnail_from_pose(pose: bpy.types.TimelineMarker):
    """Get the thumbnail that belongs to the pose.

    Args:
        pose (pose_marker): a pose in the pose library

    Returns:
        thumbnail PropertyGroup
    """
    if pose is None:
        return
    poselib = pose.id_data
    for thumbnail in poselib.pose_thumbnails:
        if thumbnail.frame == pose.frame:
            return thumbnail


def get_no_thumbnail_path() -> str:
    """Get the path to the 'no thumbnail' image."""
    no_thumbnail_path = os.path.join(
        os.path.dirname(__file__),
        'thumbnails',
        'no_thumbnail.png',
    )
    return no_thumbnail_path


def clear_cached_pose_thumbnails(*, full_clear=False):
    """Clear the cache of get_enum_items()."""
    from .core import get_enum_items, preview_collections

    if full_clear:
        pcoll = preview_collections['pose_library']
        pcoll.clear()

    get_enum_items.cache_clear()
