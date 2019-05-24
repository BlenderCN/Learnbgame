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
Blender Add-on with Verse integration
"""

bl_info = {
    "name": "Verse Client",
    "author": "Jiri Hnidek",
    "version": (0, 1),
    "blender": (2, 6, 5),
    "location": "File > Verse",
    "description": "Adds integration of Verse protocol",
    "warning": "Alpha quality, Works only at Linux OS, Requires verse module",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import verse as vrs
from . import session
from . import connection
from . import scene
from . import ui_scene
from . import avatar_view
from . import ui_avatar_view
from . import object3d
from . import ui_object3d
from . import mesh
from . import ui
from . import user


def register():
    """
    Call register methods in submodules 
    """
    ui.register()
    session.register()
    connection.register()
    ui_scene.register()
    ui_avatar_view.register()
    ui_object3d.register()
    mesh.register()


def unregister():
    """
    Call unregister methods in submodules
    """
    ui.unregister()
    session.unregister()
    connection.unregister()
    ui_scene.unregister()
    ui_avatar_view.unregister()
    ui_object3d.unregister()
    mesh.unregister()


# Print all debug messages
vrs.set_debug_level(vrs.PRINT_DEBUG_MSG)
vrs.set_client_info("Blender", bpy.app.version_string)


if __name__ == "__main__":
    # Register all modules
    register()
