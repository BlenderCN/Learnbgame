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

from .node_core import *
from ..properties.modifiers.physics import bounds_types, bounds_type_index
from .. import idprops

class PlasmaExcludeRegionNode(idprops.IDPropObjectMixin, PlasmaNodeBase, bpy.types.Node):
    bl_category = "LOGIC"
    bl_idname = "PlasmaExcludeRegionNode"
    bl_label = "Exclude Region"
    bl_width_default = 195

    # ohey, this can be a Python attribute
    pl_attribs = {"ptAttribExcludeRegion"}

    def _get_bounds(self):
        if self.region_object is not None:
            return bounds_type_index(self.region_object.plasma_modifiers.collision.bounds)
        return bounds_type_index("hull")
    def _set_bounds(self, value):
        if self.region_object is not None:
            self.region_object.plasma_modifiers.collision.bounds = value

    region_object = PointerProperty(name="Region",
                                    description="Region object's name",
                                    type=bpy.types.Object,
                                    poll=idprops.poll_mesh_objects)
    bounds = EnumProperty(name="Bounds",
                          description="Region bounds",
                          items=bounds_types,
                          get=_get_bounds,
                          set=_set_bounds)
    block_cameras = BoolProperty(name="Block Cameras",
                                description="The region blocks cameras when it has been cleared")

    input_sockets = OrderedDict([
        ("safe_point", {
            "type": "PlasmaExcludeSafePointSocket",
            "text": "Safe Point",
            "spawn_empty": True,
            # This never links to anything...
            "valid_link_sockets": frozenset(),
        }),
        ("msg", {
            "type": "PlasmaExcludeMessageSocket",
            "text": "Message",
            "spawn_empty": True,
        }),
    ])

    output_sockets = OrderedDict([
        ("keyref", {
            "text": "References",
            "type": "PlasmaPythonReferenceNodeSocket",
            "valid_link_nodes": {"PlasmaPythonFileNode"},
        }),
    ])

    def draw_buttons(self, context, layout):
        layout.prop(self, "region_object", icon="MESH_DATA")
        layout.prop(self, "bounds")
        layout.prop(self, "block_cameras")

    def get_key(self, exporter, parent_so):
        if self.region_object is None:
            self.raise_error("Region must be set")
        return exporter.mgr.find_create_key(plExcludeRegionModifier, bl=self.region_object, name=self.key_name)

    def harvest_actors(self):
        return [i.safepoint.name for i in self.find_input_sockets("safe_points") if i.safepoint is not None]

    def export(self, exporter, bo, parent_so):
        excludergn = self.get_key(exporter, parent_so).object
        excludergn.setFlag(plExcludeRegionModifier.kBlockCameras, self.block_cameras)
        region_so = exporter.mgr.find_create_object(plSceneObject, bl=self.region_object)

        # Safe points
        for i in self.find_input_sockets("safe_point"):
            safept = i.safepoint_object
            if safept:
                excludergn.addSafePoint(exporter.mgr.find_create_key(plSceneObject, bl=safept))

        # Ensure the region is exported
        phys_name = "{}_XRgn".format(self.region_object.name)
        simIface, physical = exporter.physics.generate_physical(self.region_object, region_so, self.bounds, phys_name)
        simIface.setProperty(plSimulationInterface.kPinned, True)
        physical.setProperty(plSimulationInterface.kPinned, True)
        physical.LOSDBs |= plSimDefs.kLOSDBUIBlockers
        if exporter.mgr.getVer() < pvMoul:
            physical.memberGroup = plSimDefs.kGroupDetector
            physical.collideGroup |= 1 << plSimDefs.kGroupDynamic

    @classmethod
    def _idprop_mapping(cls):
        return {"region_object": "region"}


class PlasmaExcludeSafePointSocket(idprops.IDPropObjectMixin, PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.0, 0.0, 0.0, 0.0)

    safepoint_object = PointerProperty(name="Safe Point",
                                       description="A point outside of this exclude region to move the avatar to",
                                       type=bpy.types.Object)

    def draw(self, context, layout, node, text):
        layout.prop(self, "safepoint_object", icon="EMPTY_DATA")

    @classmethod
    def _idprop_mapping(cls):
        return {"safepoint_object": "safepoint_name"}

    @property
    def is_used(self):
        return self.safepoint_object is not None


class PlasmaExcludeMessageSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.467, 0.576, 0.424, 1.0)
