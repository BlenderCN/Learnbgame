# layermanager.py
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

class LayerManager (object):
    # helper class for managing Kuesa layers on objects
    # current blender context
    blender_context = None
    # gathered layer names of all scene objects
    layer_names = None

    def __init__(self, context):
        self.blender_context = context
        self.layer_names = []

    def __repr__(self):
        names = ""
        for i in self.layer_names:
            names += "'{}', ".format(i)
        if (len(names) > 0):
            names = names[:-2]
        return "KuesaLayers{{{}}}".format(names)

    def gather_layer_names(self, blender_scene_object=None):
        if blender_scene_object is not None:
            return list({layer.name
                         for layer in blender_scene_object.kuesa.layers}) \
                if LayerManager.has_kuesa_layers_property(blender_scene_object) else []
        else:
            self.layer_names = list({name
                                     for blender_scene_object in self.blender_context.scene.objects
                                     for name in self.gather_layer_names(blender_scene_object=blender_scene_object)})
            self.layer_names.sort()
            return self.layer_names

    def meets_union(self, layer_name):
        for blender_scene_object in self.blender_context.selected_objects:
            if LayerManager.has_kuesa_layers_property(blender_scene_object):
                if any(layer.name == layer_name for layer in blender_scene_object.kuesa.layers):
                    return True
        return False

    def meets_intersect(self, layer_name):
        for blender_scene_object in self.blender_context.selected_objects:
            if LayerManager.has_kuesa_layers_property(blender_scene_object):
                found = any(layer.name == layer_name for layer in blender_scene_object.kuesa.layers)
                if not found:
                    return False
        return True

    def select_match_one(self, layer_names):
        print("select match one")
        for blender_scene_object in self.blender_context.scene.objects:
            select = False
            for layer_name in self.gather_layer_names(blender_scene_object=blender_scene_object):
                if layer_name in layer_names:
                    select = True
                    break
            blender_scene_object.select = select

    def select_match_all(self, layer_names):
        print("select match all")
        for blender_scene_object in self.blender_context.scene.objects:
            names = self.gather_layer_names(blender_scene_object=blender_scene_object)
            s = True
            for layer_name in layer_names:
                if layer_name not in names:
                    s = False
                    break
            blender_scene_object.select = s

    def sub(self, layer_names, blender_scene_object=None):
        if blender_scene_object is None:
            print("sub {}".format(layer_names))
            for blender_scene_object in self.blender_context.selected_objects:
                self.sub(layer_names, blender_scene_object=blender_scene_object)
            return
        if not LayerManager.has_kuesa_layers_property(blender_scene_object):
            blender_scene_object.kuesa.__init__()
        indices = list(range(len(blender_scene_object.kuesa.layers)))
        indices.reverse()
        for i in indices:
            if blender_scene_object.kuesa.layers[i].name in layer_names:
                blender_scene_object.kuesa.layers.remove(i)

    def add(self, layer_names, blender_scene_object=None):
        if blender_scene_object is None:
            print("add {}".format(layer_names))
            for blender_scene_object in self.blender_context.selected_objects:
                self.add(layer_names, blender_scene_object=blender_scene_object)
            return
        if not LayerManager.has_kuesa_layers_property(blender_scene_object):
            blender_scene_object.kuesa.__init__()
        layer_names_for_scene_object = self.gather_layer_names(blender_scene_object=blender_scene_object)
        for name in layer_names:
            if name not in layer_names_for_scene_object:
                new_layer = blender_scene_object.kuesa.layers.add()
                new_layer.name = name

    def rename(self, old_layer_name, new_layer_name):
        new_layer_name = new_layer_name.replace(",", "_").replace(" ", "_")
        for obj in self.blender_context.scene.objects:
            if LayerManager.has_kuesa_layers_property(obj):
                for layer in obj.kuesa.layers:
                    if layer.name == old_layer_name:
                        layer.name = new_layer_name

    @classmethod
    def has_kuesa_layers_property(cls, blender_scene_object):
        return("kuesa" in blender_scene_object.keys() and "layers" in blender_scene_object.kuesa.keys())

