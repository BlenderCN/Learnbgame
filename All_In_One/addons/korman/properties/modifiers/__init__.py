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

from .base import PlasmaModifierProperties
from .anim import *
from .avatar import *
from .gui import *
from .logic import *
from .physics import *
from .region import *
from .render import *
from .sound import *
from .water import *

class PlasmaModifiers(bpy.types.PropertyGroup):
    def determine_next_id(self):
        """Gets the ID for the next modifier in the UI"""
        # This is NOT a property, otherwise the modifiers property would access this...
        # Which acesses the modifiers property... INFINITE RECURSION! :D
        ids = [mod.display_order for mod in self.modifiers]
        if ids:
            return max(ids) + 1
        else:
            return 0

    @property
    def modifiers(self):
        """Generates all of the enabled modifiers.
           NOTE: We do not promise to return modifiers in their display_order!
        """
        for i in dir(self):
            attr = getattr(self, i, None)
            # Assumes each modifier is a single pointer to PlasmaModifierProperties
            if isinstance(attr, PlasmaModifierProperties):
                if attr.enabled:
                    yield attr

    @classmethod
    def register(cls):
        # Okay, so we have N plasma modifer property groups...
        # Rather than have (dis)organized chaos on the Blender Object, we will collect all of the
        #     property groups of type PlasmaModifierProperties and generate on-the-fly a PlasmaModifier
        #     property group to rule them all. The class attribute 'pl_id' will determine the name of
        #     the property group in PlasmaModifiers.
        # Also, just to spite us, Blender doesn't seem to handle PropertyGroup inheritance... at all.
        #     So, we're going to have to create our base properties on all of the PropertyGroups.
        #     It's times like these that make me wonder about life...
        # Enjoy!
        for i in PlasmaModifierProperties.__subclasses__():
            for name, (prop, kwargs) in PlasmaModifierProperties._subprops.items():
                setattr(i, name, prop(**kwargs))
            setattr(cls, i.pl_id, bpy.props.PointerProperty(type=i))
        bpy.types.Object.plasma_modifiers = bpy.props.PointerProperty(type=cls)


class PlasmaModifierSpec(bpy.types.PropertyGroup):
    pass


def modifier_mapping():
    """This returns a dict mapping Plasma Modifier categories to names"""

    d = {}
    sorted_modifiers = sorted(PlasmaModifierProperties.__subclasses__(), key=lambda x: x.bl_label)
    for i, mod in enumerate(sorted_modifiers):
        pl_id, category, label, description = mod.pl_id, mod.bl_category, mod.bl_label, mod.bl_description
        icon = getattr(mod, "bl_icon", "")

        # The modifier might include the cateogry name in its name, so we'll strip that.
        if label != category:
            if label.startswith(category):
                label = label[len(category)+1:]
            if label.endswith(category):
                label = label[:-len(category)-1]

        tup = (pl_id, label, description, icon, i)
        d_cat = d.setdefault(category, [])
        d_cat.append(tup)
    return d
