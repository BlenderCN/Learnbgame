# __init__.py
#
# This file is part of Kuesa.
#
# Copyright (C) 2018 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Mike Krus <mike.krus@kdab.com>
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
from .operators import KuesaLayersOp_ItemRemove,\
                       KuesaLayersOp_ItemAdd,\
                       KuesaLayersOp_ItemSelect,\
                       KuesaLayersOp_Refresh,\
                       KuesaLayersOp_NewLayer,\
                       KuesaLayersOp_RenameLayer
from .properties import KuesaLayerPropertyGroup,\
                        KuesaLayersListItem,\
                        KuesaLayersPropertyGroup
from .panel import KuesaLayersList,\
                   KuesaLayerManager


def register():
    print("register Kuesa layers plugin")
    bpy.utils.register_class(KuesaLayerPropertyGroup)
    bpy.utils.register_class(KuesaLayersOp_ItemRemove)
    bpy.utils.register_class(KuesaLayersOp_ItemAdd)
    bpy.utils.register_class(KuesaLayersOp_ItemSelect)
    bpy.utils.register_class(KuesaLayersListItem)
    bpy.utils.register_class(KuesaLayersList)
    bpy.utils.register_class(KuesaLayersPropertyGroup)
    bpy.utils.register_class(KuesaLayersOp_Refresh)
    bpy.utils.register_class(KuesaLayersOp_NewLayer)
    bpy.utils.register_class(KuesaLayersOp_RenameLayer)
    bpy.utils.register_class(KuesaLayerManager)
    bpy.types.Scene.kuesa_layers = bpy.props.PointerProperty(type=KuesaLayersPropertyGroup)


def unregister():
    print("unregister Kuesa layers plugin")
    del bpy.types.Scene.kuesa_layers
    bpy.utils.unregister_class(KuesaLayerManager)
    bpy.utils.unregister_class(KuesaLayersOp_RenameLayer)
    bpy.utils.unregister_class(KuesaLayersOp_NewLayer)
    bpy.utils.unregister_class(KuesaLayersOp_Refresh)
    bpy.utils.unregister_class(KuesaLayersPropertyGroup)
    bpy.utils.unregister_class(KuesaLayersList)
    bpy.utils.unregister_class(KuesaLayersListItem)
    bpy.utils.unregister_class(KuesaLayersOp_ItemSelect)
    bpy.utils.unregister_class(KuesaLayersOp_ItemAdd)
    bpy.utils.unregister_class(KuesaLayersOp_ItemRemove)
    bpy.utils.unregister_class(KuesaLayerPropertyGroup)
