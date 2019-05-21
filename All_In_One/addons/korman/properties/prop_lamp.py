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

from .. import idprops

class PlasmaLamp(idprops.IDPropObjectMixin, bpy.types.PropertyGroup):
    affect_characters = BoolProperty(name="Affect Avatars",
                                     description="This lamp affects avatars",
                                     options=set(),
                                     default=True)

    # Shadow settings
    cast_shadows = BoolProperty(name="Cast",
                                description="This lamp casts runtime shadows",
                                default=True)
    shadow_falloff = FloatProperty(name="Falloff",
                                   description="Distance from the Lamp past which we don't cast shadows",
                                   min=5.0, max=50.0, default=10.0,
                                   options=set())
    shadow_distance = FloatProperty(name="Fade Distance",
                                    description="Distance at which the shadow has completely faded out",
                                    min=0.0, max=500.0, default=0.0,
                                    options=set())
    shadow_power = IntProperty(name="Power",
                                 description="Multiplier for the shadow's intensity",
                                 min=0, max=200, default=100,
                                 options=set(), subtype="PERCENTAGE")
    shadow_self = BoolProperty(name="Self-Shadow",
                               description="This light can cause objects to cast shadows on themselves",
                               default=False,
                               options=set())

    lamp_region = PointerProperty(name="Soft Volume",
                                  description="Soft region this light is active inside",
                                  type=bpy.types.Object,
                                  poll=idprops.poll_softvolume_objects)

    # For LimitedDirLights
    size_height = FloatProperty(name="Height",
                               description="Size of the area for the Area Lamp in the Z direction",
                               min=0.0, default=200.0,
                               options=set())

    def has_light_group(self, bo):
        return bool(bo.users_group)

    @classmethod
    def _idprop_mapping(cls):
        return {"lamp_region": "soft_region"}
