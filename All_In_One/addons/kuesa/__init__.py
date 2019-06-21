# __init__.py
#
# This file is part of Kuesa.
#
# Copyright (C) 2018 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Timo Buske <timo.buske@kdab.com>
#
# Licensees holding valid proprietary KDAB Kuesa licenses may use this file in
# accordance with the Kuesa Enterprise License Agreement provided with the Software in the
# LICENSE.KUESA.ENTERPRISE file.
#
# Contact info@kdab.com if any conditions of this licensing are not clear to you.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bpy
from . import Layers

bl_info = {
    "name": "KDAB - Kuesa Tools For Blender",
    "author": "Timo Buske <timo.buske@kdab.com>",
    "version": (0, 0, 1),
    "blender": (2, 7, 9),
    "description": "KDAB - Kuesa Tools For Blender",
    "category": "Learnbgame",
}

class KuesaPropertyGroup (bpy.types.PropertyGroup):
        # main Kuesa property group
        # this keeps the blender ui clean as we can just drop
        # all later property groups in here
        layers = bpy.props.CollectionProperty(type=Layers.blender.KuesaLayerPropertyGroup)

def register():
    # Register layer classes with Blender
    Layers.blender.register()
    bpy.utils.register_class(KuesaPropertyGroup)
    bpy.types.Object.kuesa = bpy.props.PointerProperty(type=KuesaPropertyGroup)

def unregister():
    del bpy.types.Object.kuesa
    bpy.utils.unregister_class(KuesaPropertyGroup)
    # Unregister layer classes with Blender
    Layers.blender.unregister()

if __name__ == "__main__":
    register()
