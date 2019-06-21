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


"""
This file contains callback method used for drawing into the 3D view.
"""


import bpy
from . import avatar_view
from . import session
from . import object3d

# TODO: this should be in some class
HANDLER = None


def draw3d_cb(context):
    """
    This draw callback for io_verse Add-on is called, when view to 3D is
    changed.
    """

    # This callback should affect only for 3D View and should be executed,
    # when Blender is connected and subscribed to shared scene.
    if session.VerseSession.instance() is None or \
            bpy.context.scene.subscribed is False or \
            context.area.type != 'VIEW_3D':
        return

    # Draw all shared objects first
    for obj in object3d.VerseObject.objects.values():
        obj.draw(context)

    # If avatar view of this client doesn't exist yet, then try to 
    # get it
    my_avatar_view = avatar_view.AvatarView.my_view()
    if my_avatar_view is not None:
        # Update information about avatar's view, when needed
        my_avatar_view.update(context)

    # Draw other avatars, when there is any
    for avatar in avatar_view.AvatarView.other_views().values():
        if avatar.visualized is True and \
                context.scene.verse_node_id != -1 and \
                context.scene.subscribed is True and \
                context.scene.verse_node_id == avatar.scene_node_id.value[0]:
            avatar.draw(context)
