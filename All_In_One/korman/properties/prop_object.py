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
from PyHSPlasma import *

class PlasmaObject(bpy.types.PropertyGroup):
    def _enabled(self, context):
        # This makes me sad
        if not self.is_inited:
            self._init(context)
            self.is_inited = True

    def _init(self, context):
        o = context.object
        age = context.scene.world.plasma_age

        # We want to encourage the pages = layers paradigm.
        # So, let's see which layers we're on and check for a page whose
        #    suffix matches our layers. We'll take the first match.
        num_layers = len(o.layers)
        for page in age.pages:
            if page.seq_suffix > num_layers:
                continue
            if o.layers[page.seq_suffix - 1]:
                o.plasma_object.page = page.name
                break


    enabled = BoolProperty(name="Export",
                           description="Export this as a discrete object",
                           default=False,
                           update=_enabled)
    page = StringProperty(name="Page",
                          description="Page this object will be exported to")

    # Implementation Details
    is_inited = BoolProperty(description="INTERNAL: Init proc complete",
                             default=False,
                             options={"HIDDEN"})

    @property
    def ci_type(self):
        if self.id_data.plasma_modifiers.animation_filter.enabled:
            return plFilterCoordInterface
        else:
            return plCoordinateInterface

    @property
    def has_animation_data(self):
        bo = self.id_data
        if bo.animation_data is not None:
            if bo.animation_data.action is not None:
                return True
        data = getattr(bo, "data", None)
        if data is not None:
            if data.animation_data is not None:
                if data.animation_data.action is not None:
                    return True
        return False

    @property
    def has_transform_animation(self):
        bo = self.id_data
        if bo.animation_data is not None:
            if bo.animation_data.action is not None:
                data_paths = frozenset((i.data_path for i in bo.animation_data.action.fcurves))
                return {"location", "rotation_euler", "scale"} & data_paths
        return False

    @property
    def subworld(self):
        bo = self.id_data
        while bo is not None:
            if bo.plasma_modifiers.subworld_def.enabled:
                return bo
            else:
                bo = bo.parent
        return None


class PlasmaNet(bpy.types.PropertyGroup):
    manual_sdl = BoolProperty(name="Override SDL",
                              description="ADVANCED: Manually track high level states on this object",
                              default=False)
    sdl_names = set()

    def propagate_synch_options(self, scnobj, synobj):
        volatile, exclude = set(synobj.volatiles), set(synobj.excludes)
        if self.manual_sdl:
            for attr in self.sdl_names:
                value = getattr(self, attr)
                if value == "volatile":
                    volatile.add(attr)
                elif value == "exclude":
                    exclude.add(attr)
        else:
            # This SynchedObject may have already excluded or volatile'd everything
            # If so, bail.
            if synobj.synchFlags & plSynchedObject.kExcludeAllPersistentState or \
               synobj.synchFlags & plSynchedObject.kAllStateIsVolatile:
                return

            # Is this a kickable?
            if scnobj.sim is not None:
                phys = scnobj.sim.object.physical.object
                has_kickable = (phys.memberGroup == plSimDefs.kGroupDynamic)
            else:
                has_kickable = False

            # Is there a PythonFileMod?
            for modKey in scnobj.modifiers:
                if isinstance(modKey.object, plPythonFileMod):
                    has_pfm = True
                    break
            else:
                has_pfm = False

            # If we have either a kickable or a PFM, the PlasmaMax default is to exclude all the
            # logic-type stuff for higher level processing (namely, python)
            if has_kickable or has_pfm:
                exclude.add("AGMaster")
                exclude.add("Layer")
                exclude.add("Responder")
                exclude.add("Sound")
                exclude.add("XRegion")
            else:
                exclude.update(self.sdl_names)

        # It doesn't make sense for a state to be both excluded and volatile.
        # So, if it somehow appears in both lists, we will exclude that state.
        volatile = volatile.difference(exclude)

        # Inspect and apply volatile states, if any
        if len(volatile) == len(self.sdl_names):
            synobj.synchFlags |= plSynchedObject.kAllStateIsVolatile
        elif volatile:
            synobj.synchFlags |= plSynchedObject.kHasVolatileState
            synobj.volatiles = sorted(volatile)

        # Inspect and apply exclude states, if any
        if len(exclude) == len(self.sdl_names):
            synobj.synchFlags |= plSynchedObject.kExcludeAllPersistentState
        elif exclude:
            synobj.synchFlags |= plSynchedObject.kExcludePersistentState
            synobj.excludes = sorted(exclude)

    @classmethod
    def register(cls):
        def SdlEnumProperty(name):
            value = bpy.props.EnumProperty(name=name,
                                           description="{} state synchronization".format(name),
                                           items=[
                                               ("save", "Save to Server", "Save state on the server"),
                                               ("volatile", "Volatile on Server", "Throw away state when the age shuts down"),
                                               ("exclude", "Don't Send to Server", "Don't synchronize with the server"),
                                            ],
                                            default="exclude")
            setattr(PlasmaNet, name, value)
            PlasmaNet.sdl_names.add(name)
        agmaster = SdlEnumProperty("AGMaster")
        avatar = SdlEnumProperty("Avatar")
        avatar_phys = SdlEnumProperty("AvatarPhysical")
        clone = SdlEnumProperty("CloneMessage")
        clothing = SdlEnumProperty("Clothing")
        layer = SdlEnumProperty("Layer")
        morph = SdlEnumProperty("MorphSequence")
        particle = SdlEnumProperty("ParticleSystem")
        physical = SdlEnumProperty("Physical")
        responder = SdlEnumProperty("Responder")
        sound = SdlEnumProperty("Sound")
        xregion = SdlEnumProperty("XRegion")
