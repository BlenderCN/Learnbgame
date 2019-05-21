# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Procedural building generator
#  Copyright (C) 2019 Luka Simic
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import UI
from . import Generator


bl_info = {
    "name": "Procedural building generator",
    "description": "Proceduraly generate and edit buildings",
    "author": "Luka Šimić",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Toolbox > PBG",
    "warning": "Under development. Might cause stability issues.",
    "wiki_url": "https://lsimic.github.io/ProceduralBuildingGenerator/index.html",
    "tracker_url": "https://github.com/lsimic/ProceduralBuildingGenerator/issues",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}


def register():
    bpy.utils.register_class(UI.PBGPropertyGroup)
    bpy.types.Scene.PBGPropertyGroup = bpy.props.PointerProperty(type=UI.PBGPropertyGroup)
    bpy.utils.register_class(UI.PBGToolbarGeneralPanel)
    bpy.utils.register_class(UI.PBGToolbarLayoutPanel)
    bpy.utils.register_class(UI.PBGToolbarPillarPanel)
    bpy.utils.register_class(UI.PBGToolbarWallPanel)
    bpy.utils.register_class(UI.PBGToolbarWindowPanel)
    bpy.utils.register_class(UI.PBGToolbarGeneratePanel)
    bpy.utils.register_class(Generator.Generator)


def unregister():
    del bpy.types.Scene.PBGPropertyGroup
    bpy.utils.unregister_class(UI.PBGPropertyGroup)
    bpy.utils.unregister_class(UI.PBGToolbarGeneralPanel)
    bpy.utils.unregister_class(UI.PBGToolbarLayoutPanel)
    bpy.utils.unregister_class(UI.PBGToolbarPillarPanel)
    bpy.utils.unregister_class(UI.PBGToolbarWallPanel)
    bpy.utils.unregister_class(UI.PBGToolbarWindowPanel)
    bpy.utils.unregister_class(UI.PBGToolbarGeneratePanel)
    bpy.utils.unregister_class(Generator.Generator)
