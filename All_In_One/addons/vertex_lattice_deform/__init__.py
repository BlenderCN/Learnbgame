#    <Vertex Lattice Deform, Blender addon for quickly creating lattice deformations on objects.>
#    Copyright (C) <2017> <Nikko Miu>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from .vertex_lattice_deform import OBJECT_OT_create_lattice_deform
from .vertex_lattice_deform import OBJECT_OT_finish_lattice_deform_confirm
from .vertex_lattice_deform import OBJECT_OT_lattice_deform_custom
from .vertex_lattice_deform import OBJECT_PT_lattice_deform
from .vertex_lattice_deform import OBJECT_PT_lattice_deform_confirm


bl_info = {
    'name': 'Vertex Lattice Deform',
    'description': 'Adds a menu in the operator panel for quickly creating, applying, and cleaning up vertex lattice deformation modifiers',
    'category': '3D View',
    'author': 'Nikko Miu',
    'version': (1,0,3),
    'support': 'COMMUNITY',
    'location': 'View3D > Tools > Vertex Lattice Deform'
}

def register():
    bpy.utils.register_class(OBJECT_OT_create_lattice_deform)
    bpy.utils.register_class(OBJECT_OT_finish_lattice_deform_confirm)
    bpy.utils.register_class(OBJECT_OT_lattice_deform_custom)
    bpy.utils.register_class(OBJECT_PT_lattice_deform)
    bpy.utils.register_class(OBJECT_PT_lattice_deform_confirm)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_create_lattice_deform)
    bpy.utils.unregister_class(OBJECT_OT_finish_lattice_deform_confirm)
    bpy.utils.unregister_class(OBJECT_OT_lattice_deform_custom)
    bpy.utils.unregister_class(OBJECT_PT_lattice_deform)
    bpy.utils.unregister_class(OBJECT_PT_lattice_deform_confirm)
