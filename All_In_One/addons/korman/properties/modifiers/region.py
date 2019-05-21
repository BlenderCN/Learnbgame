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

from ...exporter import ExportError, ExportAssertionError
from ...helpers import TemporaryObject
from ... import idprops

from .base import PlasmaModifierProperties, PlasmaModifierLogicWiz
from ..prop_camera import PlasmaCameraProperties
from .physics import bounds_types

footstep_surface_ids = {
    "dirt": 0,
    # 1 = NULL
    "puddle": 2,
    # 3 = tile (NULL in MOUL)
    "metal": 4,
    "woodbridge": 5,
    "rope": 6,
    "grass": 7,
    # 8 = NULL
    "woodfloor": 9,
    "rug": 10,
    "stone": 11,
    # 12 = NULL
    # 13 = metal ladder (dupe of metal)
    "woodladder": 14,
    "water": 15,
    # 16 = maintainer's glass (NULL in PotS)
    # 17 = maintainer's metal grating (NULL in PotS)
    # 18 = swimming (why would you want this?)
}

footstep_surfaces = [("dirt", "Dirt", "Dirt"),
                     ("grass", "Grass", "Grass"),
                     ("metal", "Metal", "Metal Catwalk"),
                     ("puddle", "Puddle", "Shallow Water"),
                     ("rope", "Rope", "Rope Ladder"),
                     ("rug", "Rug", "Carpet Rug"),
                     ("stone", "Stone", "Stone Tile"),
                     ("water", "Water", "Deep Water"),
                     ("woodbridge", "Wood Bridge", "Wood Bridge"),
                     ("woodfloor", "Wood Floor", "Wood Floor"),
                     ("woodladder", "Wood Ladder", "Wood Ladder")]

class PlasmaCameraRegion(PlasmaModifierProperties):
    pl_id = "camera_rgn"

    bl_category = "Region"
    bl_label = "Camera Region"
    bl_description = "Camera Region"
    bl_icon = "CAMERA_DATA"

    camera_type = EnumProperty(name="Camera Type",
                               description="What kind of camera should be used?",
                               items=[("auto_follow", "Auto Follow Camera", "Automatically generated follow camera"),
                                      ("manual", "Manual Camera", "User specified camera object")],
                               default="manual",
                               options=set())
    camera_object = PointerProperty(name="Camera",
                                    description="Switches to this camera",
                                    type=bpy.types.Object,
                                    poll=idprops.poll_camera_objects,
                                    options=set())
    auto_camera = PointerProperty(type=PlasmaCameraProperties, options=set())

    def export(self, exporter, bo, so):
        if self.camera_type == "manual":
            if self.camera_object is None:
                raise ExportError("Camera Modifier '{}' does not specify a valid camera object".format(self.id_data.name))
            camera_so_key = exporter.mgr.find_create_key(plSceneObject, bl=self.camera_object)
            camera_props = self.camera_object.data.plasma_camera.settings
        else:
            assert self.camera_type[:4] == "auto"

            # Wheedoggy! We get to export the doggone camera now.
            camera_props = self.auto_camera
            camera_type = self.camera_type[5:]
            exporter.camera.export_camera(so, bo, camera_type, camera_props)
            camera_so_key = so.key

        # Setup physical stuff
        phys_mod = bo.plasma_modifiers.collision
        simIface, physical = exporter.physics.generate_physical(bo, so, phys_mod.bounds, self.key_name)
        physical.memberGroup = plSimDefs.kGroupDetector
        physical.reportGroup = 1 << plSimDefs.kGroupAvatar
        simIface.setProperty(plSimulationInterface.kPinned, True)
        physical.setProperty(plSimulationInterface.kPinned, True)

        # I don't feel evil enough to make this generate a logic tree...
        msg = plCameraMsg()
        msg.BCastFlags |= plMessage.kLocalPropagate | plMessage.kBCastByType
        msg.setCmd(plCameraMsg.kRegionPushCamera)
        msg.setCmd(plCameraMsg.kSetAsPrimary, camera_props.primary_camera)
        msg.newCam = camera_so_key

        region = exporter.mgr.find_create_object(plCameraRegionDetector, so=so)
        region.addMessage(msg)

    def harvest_actors(self):
        if self.camera_type == "manual":
            if self.camera_object is None:
                raise ExportError("Camera Modifier '{}' does not specify a valid camera object".format(self.id_data.name))
            camera = self.camera_object.data.plasma_camera.settings
        else:
            camera = self.auto_camera
        return camera.harvest_actors()


class PlasmaFootstepRegion(PlasmaModifierProperties, PlasmaModifierLogicWiz):
    pl_id = "footstep"

    bl_category = "Region"
    bl_label = "Footstep"
    bl_description = "Footstep Region"

    surface = EnumProperty(name="Surface",
                           description="What kind of surface are we walking on?",
                           items=footstep_surfaces,
                           default="stone")
    bounds = EnumProperty(name="Region Bounds",
                          description="Physical object's bounds",
                          items=bounds_types,
                          default="hull")

    def export(self, exporter, bo, so):
        with self.generate_logic(bo) as tree:
            tree.export(exporter, bo, so)

    def logicwiz(self, bo, tree):
        nodes = tree.nodes

        # Region Sensor
        volsens = nodes.new("PlasmaVolumeSensorNode")
        volsens.name = "RegionSensor"
        volsens.region_object = bo
        volsens.bounds = self.bounds
        volsens.find_input_socket("enter").allow = True
        volsens.find_input_socket("exit").allow = True

        # Responder
        respmod = nodes.new("PlasmaResponderNode")
        respmod.name = "Resp"
        respmod.link_input(volsens, "satisfies", "condition")
        respstate = nodes.new("PlasmaResponderStateNode")
        respstate.link_input(respmod, "state_refs", "resp")

        # ArmatureEffectStateMsg
        msg = nodes.new("PlasmaFootstepSoundMsgNode")
        msg.link_input(respstate, "msgs", "sender")
        msg.surface = self.surface

    @property
    def key_name(self):
        return "{}_FootRgn".format(self.id_data.name)


class PlasmaPanicLinkRegion(PlasmaModifierProperties):
    pl_id = "paniclink"

    bl_category = "Region"
    bl_label = "Panic Link"
    bl_description = "Panic Link Region"

    play_anim = BoolProperty(name="Play Animation",
                             description="Play the link-out animation when panic linking",
                             default=True)

    def export(self, exporter, bo, so):
        phys_mod = bo.plasma_modifiers.collision
        simIface, physical = exporter.physics.generate_physical(bo, so, phys_mod.bounds, self.key_name)

        # Now setup the region detector properties
        physical.memberGroup = plSimDefs.kGroupDetector
        physical.reportGroup = 1 << plSimDefs.kGroupAvatar

        # Finally, the panic link region proper
        reg = exporter.mgr.add_object(plPanicLinkRegion, name=self.key_name, so=so)
        reg.playLinkOutAnim = self.play_anim

    @property
    def key_name(self):
        return "{}_PanicLinkRgn".format(self.id_data.name)

    @property
    def requires_actor(self):
        return True


class PlasmaSoftVolume(idprops.IDPropMixin, PlasmaModifierProperties):
    pl_id = "softvolume"

    bl_category = "Region"
    bl_label = "Soft Volume"
    bl_description = "Soft-Boundary Region"

    # Advanced
    use_nodes = BoolProperty(name="Use Nodes",
                             description="Make this a node-based Soft Volume",
                             default=False)
    node_tree = PointerProperty(name="Node Tree",
                                description="Node Tree detailing soft volume logic",
                                type=bpy.types.NodeTree)

    # Basic
    invert = BoolProperty(name="Invert",
                          description="Invert the soft region")
    inside_strength = IntProperty(name="Inside", description="Strength inside the region",
                                  subtype="PERCENTAGE", default=100, min=0, max=100)
    outside_strength = IntProperty(name="Outside", description="Strength outside the region",
                                   subtype="PERCENTAGE", default=0, min=0, max=100)
    soft_distance = FloatProperty(name="Distance", description="Soft Distance",
                                  default=0.0, min=0.0, max=500.0)

    def _apply_settings(self, sv):
        sv.insideStrength = self.inside_strength / 100.0
        sv.outsideStrength = self.outside_strength / 100.0

    def get_key(self, exporter, so=None):
        """Fetches the key appropriate for this Soft Volume"""
        if so is None:
            so = exporter.mgr.find_create_object(plSceneObject, bl=self.id_data)

        if self.use_nodes:
            tree = self.get_node_tree()
            output = tree.find_output("PlasmaSoftVolumeOutputNode")
            if output is None:
                raise ExportError("SoftVolume '{}' Node Tree '{}' has no output node!".format(self.key_name, tree.name))
            return output.get_key(exporter, so)
        else:
            pClass = plSoftVolumeInvert if self.invert else plSoftVolumeSimple
            return exporter.mgr.find_create_key(pClass, bl=self.id_data, so=so)

    def export(self, exporter, bo, so):
        if self.use_nodes:
            self._export_sv_nodes(exporter, bo, so)
        else:
            self._export_convex_region(exporter, bo, so)

    def _export_convex_region(self, exporter, bo, so):
        if bo.type != "MESH":
            raise ExportError("SoftVolume '{}': Simple SoftVolumes can only be meshes!".format(bo.name))

        # Grab the SoftVolume KO
        sv = self.get_key(exporter, so).object
        self._apply_settings(sv)

        # If "invert" was checked, we got a SoftVolumeInvert, but we need to make a Simple for the
        # region data to be exported into..
        if isinstance(sv, plSoftVolumeInvert):
            svSimple = exporter.mgr.find_create_object(plSoftVolumeSimple, bl=bo, so=so)
            self._apply_settings(svSimple)
            sv.addSubVolume(svSimple.key)
            sv = svSimple
        sv.softDist = self.soft_distance

        # Initialize the plVolumeIsect. Currently, we only support convex isects. If you want parallel
        # isects from empties, be my guest...
        with TemporaryObject(bo.to_mesh(bpy.context.scene, True, "RENDER", calc_tessface=False), bpy.data.meshes.remove) as mesh:
            mesh.transform(bo.matrix_world)

            isect = plConvexIsect()
            for i in mesh.vertices:
                isect.addPlane(hsVector3(*i.normal), hsVector3(*i.co))
            sv.volume = isect

    def _export_sv_nodes(self, exporter, bo, so):
        tree = self.get_node_tree()
        if tree.name not in exporter.node_trees_exported:
            exporter.node_trees_exported.add(tree.name)
            tree.export(exporter, bo, so)

    def get_node_tree(self):
        if self.node_tree is None:
            raise ExportError("SoftVolume '{}' does not specify a valid Node Tree!".format(self.key_name))
        return self.node_tree

    @classmethod
    def _idprop_mapping(cls):
        return {"node_tree": "node_tree_name"}

    def _idprop_sources(self):
        return {"node_tree_name": bpy.data.node_groups}


class PlasmaSubworldRegion(PlasmaModifierProperties):
    pl_id = "subworld_rgn"

    bl_category = "Region"
    bl_label = "Subworld Region"
    bl_description = "Subworld transition region"

    subworld = PointerProperty(name="Subworld",
                               description="Subworld to transition into",
                               type=bpy.types.Object,
                               poll=idprops.poll_subworld_objects)
    transition = EnumProperty(name="Transition",
                              description="When to transition to the new subworld",
                              items=[("enter", "On Enter", "Transition when the avatar enters the region"),
                                     ("exit", "On Exit", "Transition when the avatar exits the region")],
                              default="enter",
                              options=set())

    def export(self, exporter, bo, so):
        # Due to the fact that our subworld modifier can produce both RidingAnimatedPhysical
        # and [HK|PX]Subworlds depending on the situation, this could get hairy, fast. 
        # Start by surveying the lay of the land.
        from_sub, to_sub = bo.plasma_object.subworld, self.subworld
        from_isded = exporter.physics.is_dedicated_subworld(from_sub)
        to_isded = exporter.physics.is_dedicated_subworld(to_sub)
        if 1:
            def get_log_text(bo, isded):
                main = "[Main World]" if bo is None else bo.name
                sub = "Subworld" if isded or bo is None else "RidingAnimatedPhysical"
                return main, sub
            from_name, from_type = get_log_text(from_sub, from_isded)
            to_name, to_type = get_log_text(to_sub, to_isded)
            exporter.report.msg("Transition from '{}' ({}) to '{}' ({})",
                                 from_name, from_type, to_name, to_type,
                                 indent=2)

        # I think the best solution here is to not worry about the excitement mentioned above.
        # If we encounter anything truly interesting, we can fix it in CWE more easily IMO because
        # the game actually knows more about the avatar's state than we do here in the exporter.
        if to_isded or (from_isded and to_sub is None):
            region = exporter.mgr.find_create_object(plSubworldRegionDetector, so=so)
            if to_sub is not None:
                region.subworld = exporter.mgr.find_create_key(plSceneObject, bl=to_sub)
            region.onExit = self.transition == "exit"
        else:
            msg = plRideAnimatedPhysMsg()
            msg.BCastFlags |= plMessage.kLocalPropagate | plMessage.kPropagateToModifiers
            msg.sender = so.key
            msg.entering = to_sub is not None

            # In Cyan's PlasmaMAX RAP detector, it acts as more of a traditional region
            # that changes us over to a dynamic character controller on region enter and
            # reverts on region exit. We're going for an approach that is backwards compatible
            # with subworlds, so our enter/exit regions are separate. Here, enter/exit message
            # corresponds with when we should trigger the transition.
            region = exporter.mgr.find_create_object(plRidingAnimatedPhysicalDetector, so=so)
            if self.transition == "enter":
                region.enterMsg = msg
            elif self.transition == "exit":
                region.exitMsg = msg
            else:
                raise ExportAssertionError()

        # Fancy pants region collider type shit
        simIface, physical = exporter.physics.generate_physical(bo, so, self.id_data.plasma_modifiers.collision.bounds, self.key_name)
        physical.memberGroup = plSimDefs.kGroupDetector
        physical.reportGroup |= 1 << plSimDefs.kGroupAvatar
