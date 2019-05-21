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
This module contains classes and methods for used vor visualization
valid user at Verse server
"""

import bpy
from .vrsent import vrsent
from . import ui


class BlenderUser(vrsent.VerseUser):
    """
    This class represent Verse user account at Verse server
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor of AvatarView node
        """

        super(BlenderUser, self).__init__(*args, **kwargs)

        wm = bpy.context.window_manager
        wm.verse_users.add()
        wm.verse_users[-1].node_id = self.id

        # Force redraw of properties
        ui.update_all_views(('PROPERTIES',))