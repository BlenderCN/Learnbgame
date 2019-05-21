#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
from collections import OrderedDict
from PyHSPlasma import *

from .node_core import PlasmaNodeBase, PlasmaNodeSocketBase, PlasmaTreeOutputNodeBase
from .. import idprops

class PlasmaSoftVolumeOutputNode(PlasmaTreeOutputNodeBase, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumeOutputNode"
    bl_label = "Soft Volume Output"

    input_sockets = OrderedDict([
        ("input", {
            "text": "Final Volume",
            "type": "PlasmaSoftVolumeNodeSocket",
        }),
    ])

    def get_key(self, exporter, so):
        svNode = self.find_input("input")
        if svNode is not None:
            return svNode.get_key(exporter, so)
        return None


class PlasmaSoftVolumeNodeSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.133, 0.094, 0.345, 1.0)
class PlasmaSoftVolumePropertiesNodeSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.067, 0.40, 0.067, 1.0)


class PlasmaSoftVolumePropertiesNode(PlasmaNodeBase, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumePropertiesNode"
    bl_label = "Soft Volume Properties"

    output_sockets = OrderedDict([
        ("target", {
            "text": "Volume",
            "type": "PlasmaSoftVolumePropertiesNodeSocket"
        }),
    ])

    inside_strength = IntProperty(name="Inside", description="Strength inside the region",
                                  subtype="PERCENTAGE", default=100, min=0, max=100)
    outside_strength = IntProperty(name="Outside", description="Strength outside the region",
                                   subtype="PERCENTAGE", default=0, min=0, max=100)

    def draw_buttons(self, context, layout):
        layout.prop(self, "inside_strength")
        layout.prop(self, "outside_strength")

    def propagate(self, softvolume):
        softvolume.insideStrength = self.inside_strength / 100
        softvolume.outsideStrength = self.outside_strength / 100


class PlasmaSoftVolumeReferenceNode(idprops.IDPropObjectMixin, PlasmaNodeBase, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumeReferenceNode"
    bl_label = "Soft Region"
    bl_width_default = 150

    output_sockets = OrderedDict([
        ("output", {
            "text": "Volume",
            "type": "PlasmaSoftVolumeNodeSocket"
        }),
    ])

    soft_volume = PointerProperty(name="Soft Volume",
                                  description="Object whose Soft Volume modifier we should use",
                                  type=bpy.types.Object,
                                  poll=idprops.poll_softvolume_objects)

    def draw_buttons(self, context, layout):
        layout.prop(self, "soft_volume", text="")

    def get_key(self, exporter, so):
        if self.soft_volume is None:
            self.raise_error("Invalid SoftVolume object reference")
        # Don't use SO here because that's the tree owner's SO. This soft region will find or create
        # its own SceneObject. Yay!
        return self.soft_volume.plasma_modifiers.softvolume.get_key(exporter)

    @classmethod
    def _idprop_mapping(cls):
        return {"soft_volume": "soft_object"}


class PlasmaSoftVolumeInvertNode(PlasmaNodeBase, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumeInvertNode"
    bl_label = "Soft Volume Invert"

    # The only difference between this and PlasmaSoftVolumeLinkNode is this can only have ONE input
    input_sockets = OrderedDict([
        ("properties", {
            "text": "Properties",
            "type": "PlasmaSoftVolumePropertiesNodeSocket",
        }),
        ("input", {
            "text": "Input Volume",
            "type": "PlasmaSoftVolumeNodeSocket",
        }),
    ])

    output_sockets = OrderedDict([
        ("output", {
            "text": "Output Volume",
            "type": "PlasmaSoftVolumeNodeSocket"
        }),
    ])

    def get_key(self, exporter, so):
        return exporter.mgr.find_create_key(plSoftVolumeInvert, name=self.key_name, so=so)

    def export(self, exporter, bo, so):
        parent = self.find_input("input")
        if parent is None:
            self.raise_error("SoftVolume Invert requires an input volume!")

        sv = self.get_key(exporter, so).object
        sv.addSubVolume(parent.get_key(exporter, so))

        props = self.find_input("properties")
        if props is not None:
            props.propagate(sv)
        else:
            sv.insideStrength = 1.0
            sv.outsideStrength = 0.0


class PlasmaSoftVolumeLinkNode(PlasmaNodeBase):
    input_sockets = OrderedDict([
        ("properties", {
            "text": "Properties",
            "type": "PlasmaSoftVolumePropertiesNodeSocket",
        }),
        ("input", {
            "text": "Input Volume",
            "type": "PlasmaSoftVolumeNodeSocket",
            "spawn_empty": True,
        }),
    ])

    output_sockets = OrderedDict([
        ("output", {
            "text": "Output Volume",
            "type": "PlasmaSoftVolumeNodeSocket"
        }),
    ])

    def export(self, exporter, bo, so):
        sv = self.get_key(exporter, so).object
        for node in self.find_inputs("input"):
            sv.addSubVolume(node.get_key(exporter, so))

        props = self.find_input("properties")
        if props is not None:
            props.propagate(sv)
        else:
            sv.insideStrength = 1.0
            sv.outsideStrength = 0.0


class PlasmaSoftVolumeIntersectNode(PlasmaSoftVolumeLinkNode, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumeIntersectNode"
    bl_label = "Soft Volume Intersect"

    def get_key(self, exporter, so):
        ## FIXME: SoftVolumeIntersect should not be listed as an interface
        return exporter.mgr.find_create_key(plSoftVolumeIntersect, name=self.key_name, so=so)


class PlasmaSoftVolumeUnionNode(PlasmaSoftVolumeLinkNode, bpy.types.Node):
    bl_category = "SV"
    bl_idname = "PlasmaSoftVolumeUnionNode"
    bl_label = "Soft Volume Union"

    def get_key(self, exporter, so):
        ## FIXME: SoftVolumeUnion should not be listed as an interface
        return exporter.mgr.find_create_key(plSoftVolumeUnion, name=self.key_name, so=so)
