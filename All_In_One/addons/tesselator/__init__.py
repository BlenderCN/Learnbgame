'''
Copyright (C) 2018 Jean Da Costa machado.
Jean3dimensional@gmail.com

Created by Jean Da Costa machado

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Tesselator",
    "description": "retopology tools",
    "author": "Jean Da Costa Machado",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "wiki_url": "",
    "category": "Learnbgame",
    "location": "3D View > Properties (shortcut : N) > Tesselator tab"}

import bpy

# load and reload submodules
##################################

modules = [
    "surface_particles",
    "draw_3d",
    "vector_fields",
    "particle_remesher",
    "ui",
]

import importlib

imported_modules = []
register_types = {
    bpy.types.Operator,
    bpy.types.PropertyGroup,
    bpy.types.Panel,
}
for module in modules:
    if module in locals():
        imported_modules.append(locals()[module])
        importlib.reload(locals()[module])
    else:
        exec("from . import %s" % module)
        imported_modules.append(locals()[module])

classes = []
for module in imported_modules:
    for item_name in module.__dict__:
        item = module.__dict__[item_name]
        try:
            if "TAG_REGISTER" in item.__dict__:
                classes.append(item)
        except AttributeError:
            pass
print(classes)


def register():
    for cls in classes:
        print(cls)
        bpy.utils.register_class(cls)
    for module in imported_modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    for module in imported_modules:
        if hasattr(module, "unregister"):
            module.unregister()
