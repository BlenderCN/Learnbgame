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


__version__ = '1.0.1'

bl_info = {
    'name': 'Pose Library Thumbnails',
    'author': ('Jasper van Nieuwenhuizen (jasperge), Sybren A. Stüvel (dr_sybren)'
               ' & Patrick W. Crawford (TheDuckCow)'),
    'version': (1, 0, 1),
    'blender': (2, 7, 8),
    'location': 'Properties > Armature > Pose Library',
    'description': 'Add thumbnails for the poses of a pose Library',
    'wiki_url': 'https://github.com/jasperges/pose-thumbnails/wiki',
    'tracker_url': 'https://github.com/jasperges/pose-thumbnails/issues',
    'support': 'COMMUNITY',
    'category': 'Animation',
}

if 'bpy' in locals():
    import importlib

    if 'core' in locals():
        importlib.reload(core)
        importlib.reload(creation)
else:
    from . import core, creation
import bpy


def register():
    """Register all pose thumbnail related things."""
    core.register()
    creation.register()


def unregister():
    """Unregister all pose thumbnails related things."""
    core.unregister()
    creation.unregister()


if __name__ == '__main__':
    register()
