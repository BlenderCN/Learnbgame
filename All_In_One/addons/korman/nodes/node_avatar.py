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

from .node_core import PlasmaNodeBase, PlasmaNodeSocketBase
from ..properties.modifiers.avatar import sitting_approach_flags

class PlasmaSittingBehaviorNode(PlasmaNodeBase, bpy.types.Node):
    bl_category = "AVATAR"
    bl_idname = "PlasmaSittingBehaviorNode"
    bl_label = "Sitting Behavior"
    bl_default_width = 100

    approach = EnumProperty(name="Approach",
                            description="Directions an avatar can approach the seat from",
                            items=sitting_approach_flags,
                            default={"kApproachFront", "kApproachLeft", "kApproachRight"},
                            options={"ENUM_FLAG"})

    input_sockets = OrderedDict([
        ("condition", {
            "text": "Condition",
            "type": "PlasmaConditionSocket",
        }),
    ])

    output_sockets = OrderedDict([
        ("satisfies", {
            "text": "Satisfies",
            "type": "PlasmaConditionSocket",
        }),
    ])

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.label("Approach:")
        col.prop(self, "approach")

    def draw_buttons_ext(self, context, layout):
        layout.prop_menu_enum(self, "approach")

    def get_key(self, exporter, so):
        return exporter.mgr.find_create_key(plSittingModifier, name=self.key_name, so=so)

    def export(self, exporter, bo, so):
        sitmod = self.get_key(exporter, so).object
        for flag in self.approach:
            sitmod.miscFlags |= getattr(plSittingModifier, flag)
        for i in self.find_outputs("satisfies"):
            if i is not None:
                sitmod.addNotifyKey(i.get_key(exporter, so))
            else:
                exporter.report.warn("'{}' Node '{}' doesn't expose a key. It won't be triggered by '{}'!".format(i.bl_idname, i.name, self.name), indent=3)
