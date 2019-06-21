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

import abc
import bpy
from bpy.props import *
from contextlib import contextmanager

class PlasmaModifierProperties(bpy.types.PropertyGroup):
    def created(self):
        pass

    def destroyed(self):
        pass

    @property
    def enabled(self):
        return self.display_order >= 0

    def harvest_actors(self):
        return ()

    @property
    def key_name(self):
        return self.id_data.name

    @property
    def requires_actor(self):
        """Indicates if this modifier requires the object to be a movable actor"""
        return False

    @property
    def requires_face_sort(self):
        """Indicates that the geometry's faces must be sorted by the engine"""
        return False

    @property
    def requires_span_sort(self):
        """Indicates that the geometry's Spans must be sorted with those from other Drawables that
           will render in the same pass"""
        return False

    # Guess what?
    # You can't register properties on a base class--Blender isn't smart enough to do inheritance,
    # you see... So, we'll store our definitions in a dict and make those properties on each subclass
    # at runtime. What joy. Python FTW. See register() in __init__.py
    _subprops = {
        "display_order": (IntProperty, {"name": "INTERNAL: Display Ordering",
                                        "description": "Position in the list of buttons",
                                        "default": -1,
                                        "options": {"HIDDEN"}}),
        "show_expanded": (BoolProperty, {"name": "INTERNAL: Actually draw the modifier",
                                         "default": True,
                                         "options": {"HIDDEN"}}),
        "current_version": (IntProperty, {"name": "INTERNAL: Modifier version",
                                          "default": 1,
                                          "options": {"HIDDEN"}}),
    }


class PlasmaModifierLogicWiz:
    @contextmanager
    def generate_logic(self, bo, **kwargs):
        name = kwargs.pop("name", self.key_name)
        assert not "tree" in kwargs
        tree = bpy.data.node_groups.new(name, "PlasmaNodeTree")
        kwargs["tree"] = tree
        try:
            self.logicwiz(bo, **kwargs)
            yield tree
        finally:
            bpy.data.node_groups.remove(tree)

    @abc.abstractmethod
    def logicwiz(self, bo, tree):
        pass


class PlasmaModifierUpgradable:
    @property
    @abc.abstractmethod
    def latest_version(self):
        raise NotImplementedError()

    @property
    def requires_upgrade(self):
        current_version, latest_version = self.current_version, self.latest_version
        assert current_version <= latest_version
        return current_version < latest_version

    @abc.abstractmethod
    def upgrade(self):
        raise NotImplementedError()


@bpy.app.handlers.persistent
def _restore_properties(dummy):
    # When Blender opens, it loads the default blend. The post load handler
    # below is executed and deprecated properties are unregistered. When the
    # user goes to load a new blend file, the handler below tries to execute
    # again and BOOM--there are no deprecated properties available. Therefore,
    # we reregister them here.
    for mod_cls in PlasmaModifierUpgradable.__subclasses__():
        for prop_name in mod_cls.deprecated_properties:
            # Unregistered propertes are a sequence of (property function,
            # property keyword arguments). Interesting design decision :)
            prop_cb, prop_kwargs = getattr(mod_cls, prop_name)
            del prop_kwargs["attr"] # Prevents proper registration
            setattr(mod_cls, prop_name, prop_cb(**prop_kwargs))
bpy.app.handlers.load_pre.append(_restore_properties)

@bpy.app.handlers.persistent
def _upgrade_modifiers(dummy):
    # First, run all the upgrades
    for i in bpy.data.objects:
        for mod_cls in PlasmaModifierUpgradable.__subclasses__():
            mod = getattr(i.plasma_modifiers, mod_cls.pl_id)
            if mod.requires_upgrade:
                mod.upgrade()

    # Now that everything is upgraded, forcibly remove all properties
    # from the modifiers to prevent sneaky zombie-data type export bugs
    for mod_cls in PlasmaModifierUpgradable.__subclasses__():
        for prop in mod_cls.deprecated_properties:
            RemoveProperty(mod_cls, attr=prop)
bpy.app.handlers.load_post.append(_upgrade_modifiers)
