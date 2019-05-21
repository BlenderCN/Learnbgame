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
import mathutils
from PyHSPlasma import *

from .base import PlasmaModifierProperties, PlasmaModifierLogicWiz
from ...exporter.explosions import ExportError
from ...helpers import find_modifier
from ... import idprops


class PlasmaLadderModifier(PlasmaModifierProperties):
    pl_id = "laddermod"

    bl_category = "Avatar"
    bl_label = "Ladder"
    bl_description = "Climbable Ladder"
    bl_icon = "COLLAPSEMENU"

    is_enabled = BoolProperty(name="Enabled",
                              description="Ladder enabled by default at Age start",
                              default=True)
    direction = EnumProperty(name="Direction",
                             description="Direction of climb",
                             items=[("UP", "Up", "The avatar will mount the ladder and climb upward"),
                                    ("DOWN", "Down", "The avatar will mount the ladder and climb downward"),],
                             default="DOWN")
    num_loops = IntProperty(name="Loops",
                            description="How many full animation loops after the first to play before dismounting",
                            min=0, default=4)
    facing_object = PointerProperty(name="Facing Object",
                                    description="Target object the avatar must be facing through this region to trigger climb (optional)",
                                    type=bpy.types.Object,
                                    poll=idprops.poll_mesh_objects)

    def export(self, exporter, bo, so):
        # Create the ladder modifier
        mod = exporter.mgr.find_create_object(plAvLadderMod, so=so, name=self.key_name)
        mod.type = plAvLadderMod.kBig
        mod.loops = self.num_loops
        mod.enabled = self.is_enabled
        mod.goingUp = self.direction == "UP"

        # Create vector pointing from the Facing Object to the Detector.
        # Animation only activates if the avatar is facing it within
        # engine-defined (45 degree) tolerance
        if self.facing_object is not None:
            # Use object if one has been selected
            ladderVec = self.facing_object.matrix_world.translation - bo.matrix_world.translation
        else:
            # Make our own artificial target -1.0 units back on the local Y axis.
            world = bo.matrix_world.copy()
            world.invert()
            target = bo.location - (mathutils.Vector((0.0, 1.0, 0.0)) * world)
            ladderVec = target - bo.matrix_local.translation
        mod.ladderView = hsVector3(ladderVec.x, ladderVec.y, 0.0)
        mod.ladderView.normalize()

        # Generate the detector's physical bounds
        det_name = "{}_LadderDetector".format(self.id_data.name)
        bounds = "hull" if not bo.plasma_modifiers.collision.enabled else bo.plasma_modifiers.collision.bounds
        simIface, physical = exporter.physics.generate_physical(bo, so, bounds, det_name)
        physical.memberGroup = plSimDefs.kGroupDetector
        physical.reportGroup |= 1 << plSimDefs.kGroupAvatar
        physical.setProperty(plSimulationInterface.kPinned, True)
        simIface.setProperty(plSimulationInterface.kPinned, True)
        if physical.mass == 0.0:
            physical.mass = 1.0

    @property
    def requires_actor(self):
        return True


sitting_approach_flags = [("kApproachFront", "Front", "Approach from the font"),
                          ("kApproachLeft", "Left", "Approach from the left"),
                          ("kApproachRight", "Right", "Approach from the right"),
                          ("kApproachRear", "Rear", "Approach from the rear guard")]

class PlasmaSittingBehavior(idprops.IDPropObjectMixin, PlasmaModifierProperties, PlasmaModifierLogicWiz):
    pl_id = "sittingmod"

    bl_category = "Avatar"
    bl_label = "Sitting Behavior"
    bl_description = "Avatar sitting position"

    approach = EnumProperty(name="Approach",
                            description="Directions an avatar can approach the seat from",
                            items=sitting_approach_flags,
                            default={"kApproachFront", "kApproachLeft", "kApproachRight"},
                            options={"ENUM_FLAG"})

    clickable_object = PointerProperty(name="Clickable",
                                       description="Object that defines the clickable area",
                                       type=bpy.types.Object,
                                       poll=idprops.poll_mesh_objects)
    region_object = PointerProperty(name="Region",
                                    description="Object that defines the region mesh",
                                    type=bpy.types.Object,
                                    poll=idprops.poll_mesh_objects)

    facing_enabled = BoolProperty(name="Avatar Facing",
                                  description="The avatar must be facing the clickable's Y-axis",
                                  default=True)
    facing_degrees = IntProperty(name="Tolerance",
                                 description="How far away we will tolerate the avatar facing the clickable",
                                 min=-180, max=180, default=45)

    def export(self, exporter, bo, so):
        # The user absolutely MUST specify a clickable or this won't export worth crap.
        if self.clickable_object is None:
            raise ExportError("'{}': Sitting Behavior's clickable object is invalid".format(self.key_name))

        # Generate the logic nodes now
        with self.generate_logic(bo) as tree:
            tree.export(exporter, bo, so)

    def harvest_actors(self):
        if self.facing_enabled:
            return (self.clickable_object.name,)
        return ()

    def logicwiz(self, bo, tree):
        nodes = tree.nodes

        # Sitting Modifier
        sittingmod = nodes.new("PlasmaSittingBehaviorNode")
        sittingmod.approach = self.approach
        sittingmod.name = "SittingBeh"

        # Clickable
        clickable = nodes.new("PlasmaClickableNode")
        clickable.link_output(sittingmod, "satisfies", "condition")
        clickable.clickable_object = self.clickable_object
        clickable.bounds = find_modifier(self.clickable_object, "collision").bounds

        # Avatar Region (optional)
        region_phys = find_modifier(self.region_object, "collision")
        if region_phys is not None:
            region = nodes.new("PlasmaClickableRegionNode")
            region.link_output(clickable, "satisfies", "region")
            region.name = "ClickableAvRegion"
            region.region_object = self.region_object
            region.bounds = region_phys.bounds

        # Facing Target (optional)
        if self.facing_enabled:
            facing = nodes.new("PlasmaFacingTargetNode")
            facing.link_output(clickable, "satisfies", "facing")
            facing.name = "FacingClickable"
            facing.directional = True
            facing.tolerance = self.facing_degrees
        else:
            # this socket must be explicitly disabled, otherwise it automatically generates a default
            # facing target conditional for us. isn't that nice?
            clickable.find_input_socket("facing").allow_simple = False

    @classmethod
    def _idprop_mapping(cls):
        return {"clickable_object": "clickable_obj",
                "region_object": "region_obj"}

    @property
    def key_name(self):
        return "{}_SitBeh".format(self.id_data.name)

    @property
    def requires_actor(self):
        # This should be an empty, really...
        return True
