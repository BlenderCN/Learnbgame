# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================


bl_info = {
    "name": "BookGen",
    "description": "Generate books to fill shelves",
    "author": "Oliver Weissbarth, Seojin Sim",
    "version": (0, 6),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh",
    "warning": "Alpha",
    "wiki_url": "",
    "category": "Learnbgame",
    }

from .operator import OBJECT_OT_BookGenRebuild, BookGen_SelectShelf, OBJECT_OT_BookGenRemoveShelf
from .panel import OBJECT_PT_BookGenPanel, OBJECT_PT_BookGen_MainPanel
from .properties import BookGenProperties, BookGenShelfProperties
from .shelf_list import BOOKGEN_UL_Shelves



classes = [
    BookGenProperties,
    BookGenShelfProperties,
    OBJECT_OT_BookGenRebuild,
    OBJECT_OT_BookGenRemoveShelf,
    OBJECT_PT_BookGen_MainPanel,
    OBJECT_PT_BookGenPanel,
    BookGen_SelectShelf,
    BOOKGEN_UL_Shelves
]

def register():
    from bpy.utils import register_class
    import bpy
    

    for cls in classes:
        register_class(cls)

    bpy.types.Collection.BookGenProperties = bpy.props.PointerProperty(type=BookGenProperties)
    bpy.types.Collection.BookGenShelfProperties = bpy.props.PointerProperty(type=BookGenShelfProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)