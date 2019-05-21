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
from ..properties.modifiers.region import footstep_surfaces, footstep_surface_ids
from ..exporter import ExportError
from .. import idprops

class PlasmaMessageSocketBase(PlasmaNodeSocketBase):
    bl_color = (0.004, 0.282, 0.349, 1.0)
class PlasmaMessageSocket(PlasmaMessageSocketBase, bpy.types.NodeSocket):
    pass


class PlasmaMessageNode(PlasmaNodeBase):
    input_sockets = OrderedDict([
        ("sender", {
            "text": "Sender",
            "type": "PlasmaMessageSocket",
            "valid_link_sockets": "PlasmaMessageSocket",
            "spawn_empty": True,
        }),
    ])

    @property
    def has_callbacks(self):
        """This message does not have callbacks that can be waited on by a Responder"""
        return False


class PlasmaMessageWithCallbacksNode(PlasmaMessageNode):
    output_sockets = OrderedDict([
        ("msgs", {
            "can_link": "can_link_callback",
            "text": "Send On Completion",
            "type": "PlasmaMessageSocket",
            "valid_link_sockets": "PlasmaMessageSocket",
        }),
    ])

    @property
    def can_link_callback(self):
        """Determines if a callback message can be linked to this socket"""

        # Node Graphs enable us to draw lots of fancy logic, unfortunately, not
        # everything that can potentially be represented in a node tree can be
        # exported to URU in a way that will actually work. Responder commands can
        # wait on other responder commands, but the way they are executed in Plasma is
        # serialized. It's really a list of commands that are executed until a wait
        # is encountered. At that time, Plasma waits and resumes running the list when
        # the wait callback is received.
        # So what does this mean???
        # It means that only one "branch" of message nodes can  have waits.
        def check_for_callbacks(parent_node, child_node):
            for sibling_node in parent_node.find_outputs("msgs"):
                if sibling_node == child_node:
                    continue
                if getattr(sibling_node, "has_linked_callbacks", False):
                    return True
            for grandparent_node in parent_node.find_inputs("sender"):
                return check_for_callbacks(grandparent_node, parent_node)
            return False

        for sender_node in self.find_inputs("sender"):
            if check_for_callbacks(sender_node, self):
                return False
        return True

    @property
    def has_callbacks(self):
        """This message has callbacks that can be waited on by a Responder"""
        return True

    @property
    def has_linked_callbacks(self):
        return self.find_output("msgs") is not None


class PlasmaAnimCmdMsgNode(idprops.IDPropMixin, PlasmaMessageWithCallbacksNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaAnimCmdMsgNode"
    bl_label = "Animation Command"
    bl_width_default = 190

    anim_type = EnumProperty(name="Type",
                             description="Animation type to affect",
                             items=[("OBJECT", "Object", "Mesh Action"),
                                    ("TEXTURE", "Texture", "Texture Action")],
                             default="OBJECT")

    def _poll_material_textures(self, value):
        if self.target_object is None:
            return False
        if self.target_material is None:
            return False
        return value.name in self.target_material.texture_slots

    def _poll_mesh_materials(self, value):
        if self.target_object is None:
            return False
        if self.target_object.type != "MESH":
            return False
        return value.name in self.target_object.data.materials

    target_object = PointerProperty(name="Object",
                                    description="Target object",
                                    type=bpy.types.Object)
    target_material = PointerProperty(name="Material",
                                      description="Target material",
                                      type=bpy.types.Material,
                                      poll=_poll_mesh_materials)
    target_texture = PointerProperty(name="Texture",
                                     description="Target texture",
                                     type=bpy.types.Texture,
                                     poll=_poll_material_textures)

    go_to = EnumProperty(name="Go To",
                         description="Where should the animation start?",
                         items=[("kGoToBegin", "Beginning", "The beginning"),
                                ("kGoToLoopBegin", "Loop Beginning", "The beginning of the active loop"),
                                ("CURRENT", "(Don't Change)", "The current position"),
                                ("kGoToEnd", "Ending", "The end"),
                                ("kGoToLoopEnd", "Loop Ending", "The end of the active loop")],
                         default="CURRENT")
    action = EnumProperty(name="Action",
                          description="What do you want the animation to do?",
                          items=[("kContinue", "Play", "Plays the animation"),
                                 ("kPlayToPercent", "Play to Percent", "Plays the animation until a given percent is complete"),
                                 ("kPlayToTime", "Play to Frame", "Plays the animation up to a given frame number"),
                                 ("kStop", "Stop", "Stops the animation",),
                                 ("kToggleState", "Toggle", "Toggles between Play and Stop"),
                                 ("CURRENT", "(Don't Change)", "Don't change the animation's playing state")],
                          default="CURRENT")
    play_direction = EnumProperty(name="Direction",
                                  description="Which direction do you want to play from?",
                                  items=[("kSetForwards", "Forward", "Play forwards"),
                                         ("kSetBackwards", "Backwards", "Play backwards"),
                                         ("CURRENT", "(Don't Change)", "Don't change the  play direction")],
                                  default="CURRENT")
    play_to_percent = IntProperty(name="Play To",
                                  description="Percentage at which to stop the animation",
                                  subtype="PERCENTAGE",
                                  min=0, max=100, default=50)
    play_to_frame = IntProperty(name="Play To",
                                  description="Frame at which to stop the animation",
                                  min=0)

    def _set_loop_name(self, context):
        """Updates loop_begin and loop_end when the loop name is changed"""
        pass

    looping = EnumProperty(name="Looping",
                           description="Is the animation looping?",
                           items=[("kSetLooping", "Yes", "The animation is looping",),
                                  ("CURRENT", "(Don't Change)", "Don't change the loop status"),
                                  ("kSetUnLooping", "No", "The animation is NOT looping")],
                           default="CURRENT")
    loop_name = StringProperty(name="Active Loop",
                               description="Name of the active loop",
                               update=_set_loop_name)
    loop_begin = IntProperty(name="Loop Begin",
                             description="Frame number at which the loop begins",
                             min=0)
    loop_end = IntProperty(name="Loop End",
                           description="Frame number at which the loop ends",
                           min=0)

    event = EnumProperty(name="Callback",
                         description="Event upon which to callback the Responder",
                         items=[("kEnd", "End", "When the action ends"),
                                ("NONE", "(None)", "Don't notify the Responder at all"),
                                ("kStop", "Stop", "When the action is stopped by a message")],
                         default="kEnd")

    def draw_buttons(self, context, layout):
        layout.prop(self, "anim_type")
        layout.prop(self, "target_object")

        if self.anim_type != "OBJECT":
            col = layout.column()
            col.enabled = self.target_object is not None
            col.prop(self, "target_material")

            col = layout.column()
            col.enabled = self.target_object is not None and self.target_material is not None
            col.prop(self, "target_texture")

        layout.prop(self, "go_to")
        layout.prop(self, "action")
        layout.prop(self, "play_direction")
        if self.action == "kPlayToPercent":
            layout.prop(self, "play_to_percent")
        elif self.action == "kPlayToTime":
            layout.prop(self, "play_to_frame")

        layout.prop(self, "looping")
        col = layout.column()
        col.enabled = self.looping != "CURRENT"
        if self.anim_type != "OBJECT":
            loops = None
        else:
            loops = None if self.target_object is None else self.target_object.plasma_modifiers.animation_loop
        if loops is not None and loops.enabled:
            layout.prop_search(self, "loop_name", loops, "loops", icon="PMARKER_ACT")
        else:
            layout.prop(self, "loop_begin")
            layout.prop(self, "loop_end")

        layout.prop(self, "event")

    def convert_callback_message(self, exporter, so, msg, target, wait):
        cb = plEventCallbackMsg()
        cb.addReceiver(target)
        cb.event = globals()[self.event]
        cb.user = wait
        msg.addCallback(cb)
        msg.setCmd(plAnimCmdMsg.kAddCallbacks, True)

    def convert_message(self, exporter, so):
        msg = plAnimCmdMsg()

        # We're either sending this off to an AGMasterMod or a LayerAnim
        obj = self.target_object
        if obj is None:
            self.raise_error("target object must be specified")
        if self.anim_type == "OBJECT":
            if not obj.plasma_object.has_animation_data:
                self.raise_error("invalid animation")
            target = exporter.animation.get_animation_key(obj)
        else:
            material = self.target_material
            if material is None:
                self.raise_error("target material must be specified")
            texture = self.target_texture
            if texture is None:
                self.raise_error("target texture must be specified")
            target = exporter.mesh.material.get_texture_animation_key(obj, material, texture)

        if target is None:
            raise RuntimeError()
        if isinstance(target.object, plLayerSDLAnimation):
            self.raise_error("Cannot control an SDL Animation")
        msg.addReceiver(target)

        # Check the enum properties to see what commands we need to add
        for prop in (self.go_to, self.action, self.play_direction, self.looping):
            cmd = getattr(plAnimCmdMsg, prop, None)
            if cmd is not None:
                msg.setCmd(cmd, True)

        # Easier part starts here???
        fps = bpy.context.scene.render.fps
        if self.action == "kPlayToPercent":
            msg.time = self.play_to_percent
        elif self.action == "kPlayToTime":
            msg.time = self.play_to_frame / fps

        # Implicit s better than explicit, I guess...
        if self.loop_begin != self.loop_end:
            # NOTE: loop name is not used in the engine AFAICT
            msg.setCmd(plAnimCmdMsg.kSetLoopBegin, True)
            msg.setCmd(plAnimCmdMsg.kSetLoopEnd, True)
            msg.loopBegin = self.loop_begin / fps
            msg.loopEnd = self.loop_end / fps

        # Whew, this was crazy
        return msg

    @property
    def has_callbacks(self):
        return self.event != "NONE"

    @classmethod
    def _idprop_mapping(cls):
        return {"target_object": "object_name",
                "target_material": "material_name",
                "target_texture": "texture_name"}

    def _idprop_sources(self):
        return {"object_name": bpy.data.objects,
                "material_name": bpy.data.materials,
                "texture_name": bpy.data.textures}


class PlasmaCameraMsgNode(PlasmaMessageNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaCameraMsgNode"
    bl_label = "Camera"
    bl_width_default = 200

    cmd = EnumProperty(name="Command",
                       description="Command to send to the camera system",
                       items=[("push", "Push Camera", "Pushes a new camera onto the camera stack and transitions to it"),
                              ("pop", "Pop Camera", "Pops the camera off the camera stack"),
                              ("disablefp", "Disable First Person", "Forces the camera into third person if it is currently in first person and disables first person mode"),
                              ("enablefp", "Enable First Person", "Reenables the first person camera and switches back to it if the player was in first person previously")],
                       options=set())
    camera = PointerProperty(name="Camera",
                             type=bpy.types.Object,
                             poll=idprops.poll_camera_objects,
                             options=set())
    cut = BoolProperty(name="Cut Transition",
                       description="Immediately swap over to the new camera without a transition animation",
                       options=set())

    def convert_message(self, exporter, so):
        msg = plCameraMsg()
        msg.BCastFlags |= plMessage.kLocalPropagate | plMessage.kBCastByType
        if self.cmd in {"push", "pop"}:
            if self.camera is not None:
                msg.newCam = exporter.mgr.find_create_key(plSceneObject, bl=self.camera)
            # It appears that kRegionPopCamera is unused. pushing is controlled by observing
            # the presence of the kResponderTrigger command.
            msg.setCmd(plCameraMsg.kResponderTrigger, self.cmd == "push")
            msg.setCmd(plCameraMsg.kRegionPushCamera, True)
            msg.setCmd(plCameraMsg.kSetAsPrimary, self.camera is None
                       or self.camera.data.plasma_camera.settings.primary_camera)
            msg.setCmd(plCameraMsg.kCut, self.cut)
        elif self.cmd == "disablefp":
            msg.setCmd(plCameraMsg.kResponderSetThirdPerson)
        elif self.cmd == "enablefp":
            msg.setCmd(plCameraMsg.kResponderUndoThirdPerson)
        else:
            raise RuntimeError()
        return msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "cmd")
        if self.cmd in {"push", "pop"}:
            layout.prop(self, "camera")
            layout.prop(self, "cut")


class PlasmaEnableMsgNode(PlasmaMessageNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaEnableMsgNode"
    bl_label = "Enable/Disable"

    output_sockets = OrderedDict([
        ("receivers", {
            "text": "Send To",
            "type": "PlasmaEnableMessageSocket",
            "valid_link_sockets": {"PlasmaEnableMessageSocket", "PlasmaNodeSocketInputGeneral"},
        }),
    ])

    cmd = EnumProperty(name="Command",
                       description="How should we affect the object's state?",
                       items=[("kDisable", "Disable", "Deactivate the object"),
                              ("kEnable", "Enable", "Activate the object")],
                       default="kEnable")
    settings = EnumProperty(name="Affects",
                            description="Which attributes should we change",
                            items=[("kAudible", "Audio", "Sounds played by this object"),
                                   ("kPhysical", "Physics", "Physical simulation of the object"),
                                   ("kDrawable", "Visibility", "Visibility of the object")],
                            options={"ENUM_FLAG"},
                            default={"kAudible", "kDrawable", "kPhysical"})

    def convert_message(self, exporter, so):
        msg = plEnableMsg()
        for i in self.find_outputs("receivers"):
            key = i.get_key(exporter, so)
            if isinstance(key, tuple):
                for j in key:
                    msg.addReceiver(j)
            else:
                msg.addReceiver(key)
        msg.setCmd(getattr(plEnableMsg, self.cmd), True)

        # If we have a full house, let's send it to all the SO's generic modifiers as by compressing
        # to kAll :) -- And no, this is not a bug. We do put the named types in commands. The types
        # bit vector is for raw Plasma class IDs listing which modifier types we prop to if "kByType"
        # is a command. Nice flexibility--I have no idea where that's used in Uru though...
        if len(self.settings) == 3:
            msg.setCmd(plEnableMsg.kAll, True)
        else:
            for i in self.settings:
                msg.setCmd(getattr(plEnableMsg, i), True)
        return msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "cmd", text="Cmd")
        layout.prop(self, "settings")


class PlasmaEnableMessageSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.427, 0.196, 0.0, 1.0)


class PlasmaExcludeRegionMsg(PlasmaMessageNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaExcludeRegionMsg"
    bl_label = "Exclude Region"

    output_sockets = OrderedDict([
        ("region", {
            "text": "Region",
            "type": "PlasmaExcludeMessageSocket"
        }),
    ])

    cmd = EnumProperty(name="Command",
                       description="Exclude Region State",
                       items=[("kClear", "Clear", "Clear all avatars from the region"),
                              ("kRelease", "Release", "Allow avatars to enter the region")],
                       default="kClear")

    def convert_message(self, exporter, so):
        msg = plExcludeRegionMsg()
        for i in self.find_outputs("region"):
            msg.addReceiver(i.get_key(exporter, so))
        msg.cmd = getattr(plExcludeRegionMsg, self.cmd)
        return msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "cmd", text="Cmd")


class PlasmaLinkToAgeMsg(PlasmaMessageNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaLinkToAgeMsg"
    bl_label = "Link to Age"
    bl_width_default = 280

    rules = EnumProperty(name="Rules",
                         description="Rules describing which age instance to link to",
                         items=[("kOriginalBook", "Original Age", "Links to a personally owned instance, creating if none exists"),
                                ("kOwnedBook", "Owned Age", "Links to a personally owned instance, fails if none exists"),
                                ("kChildAgeBook", "Child Age", "Links to an age instance parented to another personal age"),
                                ("kSubAgeBook", "Sub Age", "Links to an age instance owned by the current age instance"),
                                ("kBasicLink", "Basic", "Links to a specific age instance")])
    parent_filename = StringProperty(name="Parent Age",
                                     description="Filename of the age that owns the age instance we're linking to")

    age_filename = StringProperty(name="Age Filename",
                                  description="Filename of the age to link to (eg 'Garden'")
    age_instance = StringProperty(name="Age Instance",
                                  description="Instance name of the age to link to (eg 'Eder Kemo')")
    age_uuid = StringProperty(name="Age Guid",
                              description="Instance GUID to link to (eg 'ea489821-6c35-4bd0-9dae-bb17c585e680')")

    spawn_title = StringProperty(name="Spawn Title",
                                 description="Title of the Spawn Point to use",
                                 default="Default")
    spawn_point = StringProperty(name="Spawn Point",
                                 description="Name of the Spawn Point's Plasma Object",
                                 default="LinkInPointDefault")

    def convert_message(self, exporter, so):
        msg = plLinkToAgeMsg()
        als = msg.ageLink
        ais, spi = als.ageInfo, als.spawnPoint

        als.linkingRules = getattr(plAgeLinkStruct, self.rules)
        if self.rules == "kChildAgeBook":
            als.parentAgeFilename = self.parent_filename
        ais.ageFilename = self.age_filename
        ais.ageInstanceName = self.age_instance if self.age_instance else self.age_filename
        if self.rules == "kBasicLink":
            try:
                ais.ageInstanceGuid = self.age_uuid
            except ValueError:
                self.raise_error("Age Instance GUID is not a valid UUID")
        spi.title = self.spawn_title
        spi.spawnPt = self.spawn_point
        return msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "rules")
        if self.rules == "kChildAgeBook":
            layout.prop(self, "parent_filename")
        layout.separator()

        layout.prop(self, "age_filename")
        layout.prop(self, "age_instance")
        if self.rules == "kBasicLink":
            layout.prop(self, "age_uuid")
        layout.separator()

        layout.prop(self, "spawn_title")
        layout.prop(self, "spawn_point")


class PlasmaOneShotMsgNode(idprops.IDPropObjectMixin, PlasmaMessageWithCallbacksNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaOneShotMsgNode"
    bl_label = "One Shot"
    bl_width_default = 210

    pos_object = PointerProperty(name="Position",
                                 description="Object defining the OneShot position",
                                 type=bpy.types.Object)
    seek = EnumProperty(name="Seek",
                        description="How the avatar should approach the OneShot position",
                        items=[("SMART", "Smart Seek", "Let the engine figure out the best path"),
                               ("DUMB", "Seek", "Shuffle to the OneShot position"),
                               ("NONE", "Warp", "Warp the avatar to the OneShot position")],
                        default="SMART")

    animation = StringProperty(name="Animation",
                               description="Name of the animation the avatar should execute")
    marker = StringProperty(name="Marker",
                            description="Name of the marker specifying when to notify the Responder")
    drivable = BoolProperty(name="Drivable",
                            description="Player retains control of the avatar during the OneShot",
                            default=False)
    reversable = BoolProperty(name="Reversable",
                              description="Player can reverse the OneShot",
                              default=False)

    def convert_callback_message(self, exporter, so, msg, target, wait):
        msg.addCallback(self.marker, target, wait)

    def convert_message(self, exporter, so):
        msg = plOneShotMsg()
        msg.addReceiver(self.get_key(exporter, so))
        return msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "animation", text="Anim")
        layout.prop(self, "marker")
        row = layout.row()
        row.prop(self, "drivable")
        row.prop(self, "reversable")
        layout.prop(self, "pos_object", icon="EMPTY_DATA")
        layout.prop(self, "seek")

    def export(self, exporter, bo, so):
        oneshotmod = self.get_key(exporter, so).object
        oneshotmod.animName = self.animation
        oneshotmod.drivable = self.drivable
        oneshotmod.reversable = self.reversable
        oneshotmod.smartSeek = self.seek == "SMART"
        oneshotmod.noSeek = self.seek == "NONE"
        oneshotmod.seekDuration = 1.0

    def get_key(self, exporter, so):
        name = self.key_name
        if self.pos_object is not None:
            pos_so = exporter.mgr.find_create_object(plSceneObject, bl=self.pos_object)
            return exporter.mgr.find_create_key(plOneShotMod, name=name, so=pos_so)
        else:
            return exporter.mgr.find_create_key(plOneShotMod, name=name, so=so)

    def harvest_actors(self):
        if self.pos_object:
            return (self.pos_object.name,)

    @property
    def has_callbacks(self):
        return bool(self.marker)

    @classmethod
    def _idprop_mapping(cls):
        return {"pos_object": "pos"}


class PlasmaOneShotCallbackSocket(PlasmaMessageSocketBase, bpy.types.NodeSocket):
    marker = StringProperty(name="Marker",
                            description="Marker specifying the time at which to send a callback to this Responder")

    def draw(self, context, layout, node, text):
        layout.prop(self, "marker")


class PlasmaSceneObjectMsgRcvrNode(idprops.IDPropObjectMixin, PlasmaNodeBase, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaSceneObjectMsgRcvrNode"
    bl_label = "Send To Object"
    bl_width_default = 190

    input_sockets = OrderedDict([
        ("message", {
            "text": "Message",
            "type": "PlasmaNodeSocketInputGeneral",
            "valid_link_sockets": {"PlasmaEnableMessageSocket"},
            "spawn_empty": True,
        }),
    ])

    target_object = PointerProperty(name="Object",
                                    description="Object to send the message to",
                                    type=bpy.types.Object)

    def draw_buttons(self, context, layout):
        layout.prop(self, "target_object")

    def get_key(self, exporter, so):
        bo = self.target_object
        if bo is None:
            self.raise_error("target object must be specified")
        ref_so_key = exporter.mgr.find_create_key(plSceneObject, bl=bo)
        return ref_so_key

    @classmethod
    def _idprop_mapping(cls):
        return {"target_object": "object_name"}


class PlasmaSoundMsgNode(idprops.IDPropObjectMixin, PlasmaMessageWithCallbacksNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaSoundMsgNode"
    bl_label = "Sound"
    bl_width_default = 190

    def _poll_sound_emitters(self, value):
        return value.plasma_modifiers.soundemit.enabled

    emitter_object = PointerProperty(name="Object",
                                     description="Sound emitter object",
                                     type=bpy.types.Object,
                                     poll=_poll_sound_emitters)
    sound_name = StringProperty(name="Sound",
                                description="Sound datablock")

    go_to = EnumProperty(name="Go To",
                         description="Where should the sound start?",
                         items=[("BEGIN", "Beginning", "The beginning"),
                                ("CURRENT", "(Don't Change)", "The current position"),
                                ("TIME", "Time", "The time specified in seconds")],
                         default="CURRENT")
    looping = EnumProperty(name="Looping",
                           description="Is the sound looping?",
                           items=[("kSetLooping", "Yes", "The sound is looping",),
                                  ("CURRENT", "(Don't Change)", "Don't change the loop status"),
                                  ("kUnSetLooping", "No", "The sound is NOT looping")],
                           default="CURRENT")
    action = EnumProperty(name="Action",
                          description="What do you want the sound to do?",
                          items=[("kPlay", "Play", "Plays the sound"),
                                 ("kStop", "Stop", "Stops the sound",),
                                 ("kToggleState", "Toggle", "Toggles between Play and Stop"),
                                 ("CURRENT", "(Don't Change)", "Don't change the sound's playing state")],
                          default="CURRENT")
    volume = EnumProperty(name="Volume",
                          description="What should happen to the volume?",
                          items=[("MUTE", "Mute", "Mutes the volume"),
                                 ("CURRENT", "(Don't Change)", "Don't change the volume"),
                                 ("CUSTOM", "Custom", "Manually specify the volume")],
                          default="CURRENT")

    time = FloatProperty(name="Time",
                         description="Time in seconds to begin playing from",
                         min=0.0, default=0.0,
                         options=set(), subtype="TIME", unit="TIME")
    volume_pct = IntProperty(name="Volume Level",
                             description="Volume to play the sound",
                             min=0, max=100, default=100,
                             options=set(),
                             subtype="PERCENTAGE")

    def convert_callback_message(self, exporter, so, msg, target, wait):
        cb = plEventCallbackMsg()
        cb.addReceiver(target)
        cb.event = kEnd
        cb.user = wait
        msg.addCallback(cb)
        msg.setCmd(plSoundMsg.kAddCallbacks)

    def convert_message(self, exporter, so):
        if self.emitter_object is None:
            self.raise_error("Sound emitter must be set")
        soundemit = self.emitter_object.plasma_modifiers.soundemit
        if not soundemit.enabled:
            self.raise_error("'{}' is not a valid Sound Emitter".format(self.emitter_object.name))

        # Always test the specified audible for validity
        if self.sound_name and soundemit.sounds.get(self.sound_name, None) is None:
            self.raise_error("Invalid Sound '{}' requested from Sound Emitter '{}'".format(self.sound_name, self.emitter_object.name))

        # Remember that 3D stereo sounds are exported as two emitters...
        # But, if we only have one sound attached, who cares, we can just address the message to all
        audible_key = exporter.mgr.find_create_key(plAudioInterface, bl=self.emitter_object)
        indices = (-1,) if not self.sound_name or len(soundemit.sounds) == 1 else soundemit.get_sound_indices(self.sound_name)
        for idx in indices:
            msg = plSoundMsg()
            msg.addReceiver(audible_key)
            msg.index = idx

            # NOTE: There are a number of commands in Plasma's enumeration that do nothing.
            #       This is what I determine to be the most useful and functional subset...
            #       Please see plAudioInterface::MsgReceive for more details.
            if self.go_to == "BEGIN":
                msg.setCmd(plSoundMsg.kGoToTime)
                msg.time = 0.0
            elif self.go_to == "TIME":
                msg.setCmd(plSoundMsg.kGoToTime)
                msg.time = self.time

            if self.volume == "MUTE":
                msg.setCmd(plSoundMsg.kSetVolume)
                msg.volume = 0.0
            elif self.volume == "CUSTOM":
                msg.setCmd(plSoundMsg.kSetVolume)
                msg.volume = self.volume_pct

            if self.looping != "CURRENT":
                msg.setCmd(getattr(plSoundMsg, self.looping))
            if self.action != "CURRENT":
                msg.setCmd(getattr(plSoundMsg, self.action))

            # Because we might be giving two messages here...
            yield msg

    def draw_buttons(self, context, layout):
        layout.prop(self, "emitter_object")
        if self.emitter_object is not None:
            soundemit = self.emitter_object.plasma_modifiers.soundemit
            if soundemit.enabled:
                layout.prop_search(self, "sound_name", soundemit, "sounds", icon="SOUND")
            else:
                layout.label("Not a Sound Emitter", icon="ERROR")

        layout.prop(self, "go_to")
        if self.go_to == "TIME":
            layout.prop(self, "time")
        layout.prop(self, "action")
        if self.volume == "CUSTOM":
            layout.prop(self, "volume_pct")
        layout.prop(self, "looping")
        layout.prop(self, "volume")

    @classmethod
    def _idprop_mapping(cls):
        return {"emitter_object": "object_name"}


class PlasmaTimerCallbackMsgNode(PlasmaMessageWithCallbacksNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaTimerCallbackMsgNode"
    bl_label = "Timed Callback"

    delay = FloatProperty(name="Delay",
                          description="Time (in seconds) to wait until continuing",
                          min=0.1,
                          default=1.0)

    def draw_buttons(self, context, layout):
        layout.prop(self, "delay")

    def convert_callback_message(self, exporter, so, msg, target, wait):
        msg.addReceiver(target)
        msg.ID = wait

    def convert_message(self, exporter, so):
        msg = plTimerCallbackMsg()
        msg.time = self.delay
        return msg


class PlasmaFootstepSoundMsgNode(PlasmaMessageNode, bpy.types.Node):
    bl_category = "MSG"
    bl_idname = "PlasmaFootstepSoundMsgNode"
    bl_label = "Footstep Sound"

    surface = EnumProperty(name="Surface",
                           description="What kind of surface are we walking on?",
                           items=footstep_surfaces,
                           default="stone")

    def draw_buttons(self, context, layout):
        layout.prop(self, "surface")

    def convert_message(self, exporter, so):
        msg = plArmatureEffectStateMsg()
        msg.BCastFlags |= (plMessage.kPropagateToModifiers | plMessage.kNetPropagate)
        msg.surface = footstep_surface_ids[self.surface]
        return msg
