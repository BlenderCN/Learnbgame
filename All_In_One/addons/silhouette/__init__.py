'''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    'name': 'Silhouette',
    'author': 'Trentin Frederick (proxe)',
    'version': (0, 5, 22),
    'blender': (2, 76, 0),
    'location': '3D View \N{Rightwards Arrow} Properties Shelf \N{Rightwards Arrow} Shading',
    'description': 'Quickly toggle the viewport into a silhouette mode.',
    'warning': 'Beta',
    # 'wiki_url': '',
    # 'tracker_url': '',
    'category': '3D View'
}

import bpy

from bpy.props import PointerProperty
from bpy.utils import register_module, unregister_module

from .addon import preferences, properties, interface


def register():

    register_module(__name__)

    bpy.types.Scene.silhouette = PointerProperty(
        type = properties.silhouette,
        name = 'Silhouette Addon',
        description = 'Storage location for silhouette addon.',
    )

    bpy.types.VIEW3D_PT_view3d_shading.append(interface.toggle)


def unregister():

    bpy.types.VIEW3D_PT_view3d_shading.remove(interface.toggle)

    del bpy.types.Scene.silhouette

    unregister_module(__name__)
