# operators.py
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
from .properties import KuesaLayersListItem
from ..layermanager import LayerManager

# operators for buttons of the list items


class KuesaLayersOp_ItemRemove(bpy.types.Operator):
    """ Remove from selected objects """

    bl_idname = "kuesa_layers.item_remove"
    bl_label = "Remove from selected objects"

    index = bpy.props.IntProperty()

    def execute(self, context):
        layer_manager = LayerManager(context)
        layer_name = context.scene.kuesa_layers.layer_names_list[self.index].name
        layer_manager.sub([layer_name])
        context.scene.kuesa_layers.layer_names_list[self.index].state = KuesaLayersListItem.STATE_OFF
        return{'FINISHED'}


class KuesaLayersOp_ItemAdd(bpy.types.Operator):
    """ Add layer to selected objects """

    bl_idname = "kuesa_layers.item_add"
    bl_label = "Add layer to selected objects"

    index = bpy.props.IntProperty()

    def execute(self, context):
        layer_manager = LayerManager(context)
        layer_name = context.scene.kuesa_layers.layer_names_list[self.index].name
        layer_manager.add([layer_name])
        context.scene.kuesa_layers.layer_names_list[self.index].state = KuesaLayersListItem.STATE_ON
        return{'FINISHED'}


class KuesaLayersOp_ItemSelect(bpy.types.Operator):
    """ Select objects with this layer """

    bl_idname = "kuesa_layers.item_select"
    bl_label = "Select objects with this layer"

    index = bpy.props.IntProperty()

    def execute(self, context):
        layer_manager = LayerManager(context)
        layer_name = context.scene.kuesa_layers.layer_names_list[self.index].name
        layer_manager.select_match_one([layer_name])
        return{'FINISHED'}

# operators for buttons of the KuesaLayer panel


class KuesaLayersOp_Refresh(bpy.types.Operator):
    """ Refresh """

    bl_idname = "kuesa_layers.refresh"
    bl_label = "Refresh"

    def execute(self, context):
        context.scene.kuesa_layers.refresh(context)
        return{'FINISHED'}


class KuesaLayersOp_NewLayer(bpy.types.Operator):
    """ Create new layer and apply to selection """

    bl_idname = "kuesa_layers.new_layer"
    bl_label = "Create new layer and apply to selection"

    def execute(self, context):
        context.scene.kuesa_layers.new_layer(context)
        return{'FINISHED'}


class KuesaLayersOp_RenameLayer(bpy.types.Operator):
    """ Rename Layer """

    bl_idname = "kuesa_layers.rename_layer"
    bl_label = "Rename Layer"

    def execute(self, context):
        context.scene.kuesa_layers.rename_layer(context)
        return{'FINISHED'}
