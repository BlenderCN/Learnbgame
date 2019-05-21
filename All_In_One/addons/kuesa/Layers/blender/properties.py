# properties.py
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
from ..layermanager import LayerManager

# Blender Property Types for Layers
# KuesaLayersListItem (use by SideMenu to show scene layers)
# KuesaLayerPropertyGroup (represent a layer as seen on an object)
# KuesaLayersPropertyGroup (uses to show all KuesaLayerPropertyGroup assigned to one object)

class KuesaLayersListItem(bpy.types.PropertyGroup):

    STATE_OFF = 0
    STATE_MID = 1
    STATE_ON = 2

    name = bpy.props.StringProperty(default="")
    state = bpy.props.IntProperty(default=STATE_OFF)


class KuesaLayerPropertyGroup(bpy.types.PropertyGroup):
    # definition of a Kuesa layer in blender, for now it's just a name
    name = bpy.props.StringProperty(default="")


class KuesaLayersPropertyGroup(bpy.types.PropertyGroup):

    # property callbacks
    def update_layer_index(self, context):
        if self.layer_index not in range(len(self.layer_names_list)):
            return
        self.current_layer_name = self.layer_names_list[self.layer_index].name

    # properties
    layer_names_list = bpy.props.CollectionProperty(type=KuesaLayersListItem)
    layer_index = bpy.props.IntProperty(name="Index", default=-1, update=update_layer_index)
    current_layer_name = bpy.props.StringProperty(name="Name", default="")

    @staticmethod
    def update_refresh_op(context):
        context.scene.kuesa_layers.refresh(context)

    # methods
    def refresh(self, context):
        print("refresh")
        # Update = clearing list and reinserting up to date list items
        # Clear the layer list property
        self.clear_layer_list_property()
        # Gather all layer names (looks up all scene objects an gather layer names)
        layer_manager = LayerManager(context)
        layer_names = layer_manager.gather_layer_names()
        # Insert new list item for each layer name
        for layer_name in layer_names:
            # Add new item to CollectionProperty
            item = self.layer_names_list.add()
            item.name = layer_name
            # Set state of the property list item based on whether the
            # blender scene objects currently selected contain the
            # layer name or not
            if layer_manager.meets_intersect(layer_name):
                item.state = KuesaLayersListItem.STATE_ON
            elif layer_manager.meets_union(layer_name):
                item.state = KuesaLayersListItem.STATE_MID
            else:
                item.state = KuesaLayersListItem.STATE_OFF
        # Note: any layer that wasn't referenced by a scene object would get
        # removed from the list of layers following a refresh

    def clear_layer_list_property(self):
        # Remove all items from the list property
        for i in self.layer_names_list:
            self.layer_names_list.remove(0)

    def new_layer(self, context):
        print("new layer")

        def add_layer_name(target_new_layer_name, existing_layer_names):
            target_new_layer_name = target_new_layer_name.replace(",", "_").replace(" ", "_")

            # Return if trying to add a layer already existing
            if target_new_layer_name in existing_layer_names:
                return False

            # Create new list item and set its name
            item = self.layer_names_list.add()
            item.name = target_new_layer_name

            # Add layer_name to all selected objects using the LayerManager
            layer_manager = LayerManager(context)
            layer_manager.add([target_new_layer_name])
            item.state = KuesaLayersListItem.STATE_ON
            self.layer_index = len(self.layer_names_list) - 1
            return True

        # Gather all layer names (looks up all scene objects an gather layer names)
        layer_manager = LayerManager(context)
        layer_names = layer_manager.gather_layer_names()

        # Gather layer names from the list of items
        # and insert into layer_names any name contained
        # in the list that it didn't already contain
        for item in self.layer_names_list:
            if item.name not in layer_names:
                layer_names.append(item.name)

        # We enter this case when someone write a new name and press add
        name = self.current_layer_name
        if name and add_layer_name(name, layer_names):
            return

        # If the above failed, the name already existed for some reason
        # We will try to autogenerate one and repeat and until we succeed

        number = len(self.layer_names_list)
        # We loop until we have found a satisfying name
        # that could be added
        while (True):
            name = "VL{}".format(number)
            # If insert successful we are done
            # Otherwise we already have such a name contained in layer_names
            if add_layer_name(name, layer_names):
                return
            number += 1

    def rename_layer(self, context):
        print("rename layer")
        if self.layer_index not in range(len(self.layer_names_list)):
            return
        layer_manager = LayerManager(context)
        layer_manager.rename(self.layer_names_list[self.layer_index].name, self.current_layer_name)
        self.layer_names_list[self.layer_index].name = self.current_layer_name
