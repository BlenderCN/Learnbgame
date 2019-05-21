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
import itertools
import math
import mathutils
from PyHSPlasma import *
import weakref

from . import utils

class AnimationConverter:
    def __init__(self, exporter):
        self._exporter = weakref.ref(exporter)
        self._bl_fps = bpy.context.scene.render.fps

    def _convert_frame_time(self, frame_num):
        return frame_num / self._bl_fps

    def convert_object_animations(self, bo, so):
        if not bo.plasma_object.has_animation_data:
            return

        def fetch_animation_data(id_data):
            if id_data is not None:
                if id_data.animation_data is not None:
                    action = id_data.animation_data.action
                    return action, getattr(action, "fcurves", None)
            return None, None

        # TODO: At some point, we should consider supporting NLA stuff.
        # But for now, this seems sufficient.
        obj_action, obj_fcurves = fetch_animation_data(bo)
        data_action, data_fcurves = fetch_animation_data(bo.data)

        # We're basically just going to throw all the FCurves at the controller converter (read: wall)
        # and see what sticks. PlasmaMAX has some nice animation channel stuff that allows for some
        # form of separation, but Blender's NLA editor is way confusing and appears to not work with
        # things that aren't the typical position, rotation, scale animations.
        applicators = []
        if isinstance(bo.data, bpy.types.Camera):
            applicators.append(self._convert_camera_animation(bo, so, obj_fcurves, data_fcurves))
        else:
            applicators.append(self._convert_transform_animation(bo.name, obj_fcurves, bo.matrix_basis))
        if bo.plasma_modifiers.soundemit.enabled:
            applicators.extend(self._convert_sound_volume_animation(bo.name, obj_fcurves, bo.plasma_modifiers.soundemit))
        if isinstance(bo.data, bpy.types.Lamp):
            lamp = bo.data
            applicators.extend(self._convert_lamp_color_animation(bo.name, data_fcurves, lamp))
            if isinstance(lamp, bpy.types.SpotLamp):
                applicators.extend(self._convert_spot_lamp_animation(bo.name, data_fcurves, lamp))
            if isinstance(lamp, bpy.types.PointLamp):
                applicators.extend(self._convert_omni_lamp_animation(bo.name, data_fcurves, lamp))

        # Check to make sure we have some valid animation applicators before proceeding.
        if not any(applicators):
            return

        # There is a race condition in the client with animation loading. It expects for modifiers
        # to be listed on the SceneObject in a specific order. D'OH! So, always use these funcs.
        agmod, agmaster = self.get_anigraph_objects(bo, so)
        atcanim = self._mgr.find_create_object(plATCAnim, so=so)

        # Add the animation data to the ATC
        for i in applicators:
            if i is not None:
                atcanim.addApplicator(i)
        agmod.channelName = bo.name
        agmaster.addPrivateAnim(atcanim.key)

        # This was previously part of the Animation Modifier, however, there can be lots of animations
        # Therefore we move it here.
        def get_ranges(*args, **kwargs):
            index = kwargs.get("index", 0)
            for i in args:
                if i is not None:
                    yield i.frame_range[index]
        atcanim.name = "(Entire Animation)"
        atcanim.start = self._convert_frame_time(min(get_ranges(obj_action, data_action, index=0)))
        atcanim.end = self._convert_frame_time(max(get_ranges(obj_action, data_action, index=1)))

        # Marker points
        if obj_action is not None:
            for marker in obj_action.pose_markers:
                atcanim.setMarker(marker.name, self._convert_frame_time(marker.frame))

        # Fixme? Not sure if we really need to expose this...
        atcanim.easeInMin = 1.0
        atcanim.easeInMax = 1.0
        atcanim.easeInLength = 1.0
        atcanim.easeOutMin = 1.0
        atcanim.easeOutMax = 1.0
        atcanim.easeOutLength = 1.0

    def _convert_camera_animation(self, bo, so, obj_fcurves, data_fcurves):
        if data_fcurves:
            # The hard part about this crap is that FOV animations are not stored in ATC Animations
            # instead, FOV animation keyframes are held inside of the camera modifier. Cyan's solution
            # in PlasmaMAX appears to be for any xform keyframe, add two messages to the camera modifier
            # representing the FOV at that point. Makes more sense to me to use each FOV keyframe instead
            fov_fcurve = next((i for i in data_fcurves if i.data_path == "plasma_camera.settings.fov"), None)
            if fov_fcurve:
                # NOTE: this is another critically important key ordering in the SceneObject modifier
                #       list. CameraModifier calls into AGMasterMod code that assumes the AGModifier
                #       is already available. Should probably consider adding some code to libHSPlasma
                #       to order the SceneObject modifier key vector at some point.
                anim_key = self.get_animation_key(bo)
                camera = self._mgr.find_create_object(plCameraModifier, so=so)
                cam_key = camera.key
                aspect, fps = (3.0 / 4.0), self._bl_fps
                degrees = math.degrees
                fov_fcurve.update()

                # Seeing as how we're transforming the data entirely, we'll just use the fcurve itself
                # instead of our other animation helpers. But ugh does this mess look like sloppy C.
                keyframes = fov_fcurve.keyframe_points
                num_keyframes = len(keyframes)
                has_fov_anim = bool(num_keyframes)
                i = 0
                while i < num_keyframes:
                    this_keyframe = keyframes[i]
                    next_keyframe = keyframes[0] if i+1 == num_keyframes else keyframes[i+1]

                    # So remember, these are messages. When we hit a keyframe, we're dispatching a message
                    # representing the NEXT desired FOV.
                    this_frame_time = this_keyframe.co[0] / fps
                    next_frame_num, next_frame_value = next_keyframe.co
                    next_frame_time = next_frame_num / fps

                    # This message is held on the camera modifier and sent to the animation... It calls
                    # back when the animation reaches the keyframe time, causing the FOV message to be sent.
                    cb_msg = plEventCallbackMsg()
                    cb_msg.event = kTime
                    cb_msg.eventTime = this_frame_time
                    cb_msg.index = i
                    cb_msg.repeats = -1
                    cb_msg.addReceiver(cam_key)
                    anim_msg = plAnimCmdMsg()
                    anim_msg.animName = "(Entire Animation)"
                    anim_msg.time = this_frame_time
                    anim_msg.sender = anim_key
                    anim_msg.addReceiver(anim_key)
                    anim_msg.addCallback(cb_msg)
                    anim_msg.setCmd(plAnimCmdMsg.kAddCallbacks, True)
                    camera.addMessage(anim_msg, anim_key)

                    # This is the message actually changes the FOV. Interestingly, it is sent at
                    # export-time and while playing the game, the camera modifier just steals its
                    # parameters and passes them to the brain. Can't make this stuff up.
                    cam_msg = plCameraMsg()
                    cam_msg.addReceiver(cam_key)
                    cam_msg.setCmd(plCameraMsg.kAddFOVKeyFrame, True)
                    cam_config = cam_msg.config
                    cam_config.accel = next_frame_time # Yassss...
                    cam_config.fovW = degrees(next_frame_value)
                    cam_config.fovH = degrees(next_frame_value * aspect)
                    camera.addFOVInstruction(cam_msg)

                    i += 1
            else:
                has_fov_anim = False
        else:
            has_fov_anim = False

        # If we exported any FOV animation at all, then we need to ensure there is an applicator
        # returned from here... At bare minimum, we'll need the applicator with an empty
        # CompoundController. This should be sufficient to keep CWE from crashing...
        applicator = self._convert_transform_animation(bo.name, obj_fcurves, bo.matrix_basis, allow_empty=has_fov_anim)
        camera = locals().get("camera", self._mgr.find_create_object(plCameraModifier, so=so))
        camera.animated = applicator is not None
        return applicator

    def _convert_lamp_color_animation(self, name, fcurves, lamp):
        if not fcurves:
            return None

        energy_curve = next((i for i in fcurves if i.data_path == "energy" and i.keyframe_points), None)
        color_curves = sorted((i for i in fcurves if i.data_path == "color" and i.keyframe_points), key=lambda x: x.array_index)
        if energy_curve is None and color_curves is None:
            return None
        elif lamp.use_only_shadow:
            self._exporter().report.warn("Cannot animate Lamp color because this lamp only casts shadows", indent=3)
            return None
        elif not lamp.use_specular and not lamp.use_diffuse:
            self._exporter().report.warn("Cannot animate Lamp color because neither Diffuse nor Specular are enabled", indent=3)
            return None

        # OK Specular is easy. We just toss out the color as a point3.
        color_keyframes, color_bez = self._process_keyframes(color_curves, convert=lambda x: x * -1.0 if lamp.use_negative else None)
        if color_keyframes and lamp.use_specular:
            channel = plPointControllerChannel()
            channel.controller = self._make_point3_controller(color_curves, color_keyframes, color_bez, lamp.color)
            applicator = plLightSpecularApplicator()
            applicator.channelName = name
            applicator.channel = channel
            yield applicator

        # Hey, look, it's a third way to process FCurves. YAY!
        def convert_diffuse_animation(color, energy):
            if lamp.use_negative:
                return { key: (0.0 - value) * energy[0] for key, value in color.items() }
            else:
                return { key: value * energy[0] for key, value in color.items() }
        diffuse_defaults = { "color": lamp.color, "energy": lamp.energy }
        diffuse_fcurves = color_curves + [energy_curve,]
        diffuse_keyframes = self._process_fcurves(diffuse_fcurves, convert_diffuse_animation, diffuse_defaults)
        if not diffuse_keyframes:
            return None

        # Whew.
        channel = plPointControllerChannel()
        channel.controller = self._make_point3_controller([], diffuse_keyframes, False, [])
        applicator = plLightDiffuseApplicator()
        applicator.channelName = name
        applicator.channel = channel
        yield applicator

    def _convert_omni_lamp_animation(self, name, fcurves, lamp):
        if not fcurves:
            return None

        energy_fcurve = next((i for i in fcurves if i.data_path == "energy"), None)
        distance_fcurve = next((i for i in fcurves if i.data_path == "distance"), None)
        if energy_fcurve is None and distance_fcurve is None:
            return None
        light_converter = self._exporter().light
        intensity, atten_end = light_converter.convert_attenuation(lamp)

        # All types allow animating cutoff
        if distance_fcurve is not None:
            channel = plScalarControllerChannel()
            channel.controller = self.make_scalar_leaf_controller(distance_fcurve,
                                                                  lambda x: x if lamp.use_sphere else x * 2)
            applicator = plOmniCutoffApplicator()
            applicator.channelName = name
            applicator.channel = channel
            yield applicator

        falloff = lamp.falloff_type
        if falloff == "CONSTANT":
            if energy_fcurve is not None:
                self._exporter().report.warn("Constant attenuation cannot be animated in Plasma", ident=3)
        elif falloff == "INVERSE_LINEAR":
            def convert_linear_atten(distance, energy):
                intens = abs(energy[0])
                atten_end = distance[0] if lamp.use_sphere else distance[0] * 2
                return light_converter.convert_attenuation_linear(intens, atten_end)

            keyframes = self._process_fcurves([distance_fcurve, energy_fcurve], convert_linear_atten,
                                              {"distance": lamp.distance, "energy": lamp.energy})
            if keyframes:
                channel = plScalarControllerChannel()
                channel.controller = self._make_scalar_leaf_controller(keyframes, False)
                applicator = plOmniApplicator()
                applicator.channelName = name
                applicator.channel = channel
                yield applicator
        elif falloff == "INVERSE_SQUARE":
            if self._mgr.getVer() >= pvMoul:
                def convert_quadratic_atten(distance, energy):
                    intens = abs(energy[0])
                    atten_end = distance[0] if lamp.use_sphere else distance[0] * 2
                    return light_converter.convert_attenuation_quadratic(intens, atten_end)

                keyframes = self._process_fcurves([distance_fcurve, energy_fcurve], convert_quadratic_atten,
                                                  {"distance": lamp.distance, "energy": lamp.energy})
                if keyframes:
                    channel = plScalarControllerChannel()
                    channel.controller = self._make_scalar_leaf_controller(keyframes, False)
                    applicator = plOmniSqApplicator()
                    applicator.channelName = name
                    applicator.channel = channel
                    yield applicator
            else:
                self._exporter().report.port("Lamp Falloff '{}' animations only partially supported for this version of Plasma", falloff, indent=3)
        else:
            self._exporter().report.warn("Lamp Falloff '{}' animations are not supported".format(falloff), ident=3)

    def _convert_sound_volume_animation(self, name, fcurves, soundemit):
        if not fcurves:
            return None

        def convert_volume(value):
            if value == 0.0:
                return 0.0
            else:
                return math.log10(value) * 20.0

        for sound in soundemit.sounds:
            path = "{}.volume".format(sound.path_from_id())
            fcurve = next((i for i in fcurves if i.data_path == path and i.keyframe_points), None)
            if fcurve is None:
                continue

            for i in soundemit.get_sound_indices(sound=sound):
                applicator = plSoundVolumeApplicator()
                applicator.channelName = name
                applicator.index = i

                # libHSPlasma assumes a channel is not shared among applicators...
                # so yes, we must convert the same animation data again and again.
                channel = plScalarControllerChannel()
                channel.controller = self.make_scalar_leaf_controller(fcurve, convert=convert_volume)
                applicator.channel = channel
                yield applicator

    def _convert_spot_lamp_animation(self, name, fcurves, lamp):
        if not fcurves:
            return None

        blend_fcurve = next((i for i in fcurves if i.data_path == "spot_blend"), None)
        size_fcurve = next((i for i in fcurves if i.data_path == "spot_size"), None)
        if blend_fcurve is None and size_fcurve is None:
            return None

        # Spot Outer is just the size keyframes...
        if size_fcurve is not None:
            channel = plScalarControllerChannel()
            channel.controller = self.make_scalar_leaf_controller(size_fcurve, lambda x: math.degrees(x))
            applicator = plSpotOuterApplicator()
            applicator.channelName = name
            applicator.channel = channel
            yield applicator

        # Spot inner must be calculated...
        def convert_spot_inner(spot_blend, spot_size):
            blend = min(0.001, spot_blend[0])
            size = spot_size[0]
            value = size - (blend * size)
            return math.degrees(value)
        defaults = { "spot_blend": lamp.spot_blend, "spot_size": lamp.spot_size }
        keyframes = self._process_fcurves([blend_fcurve, size_fcurve], convert_spot_inner, defaults)

        if keyframes:
            channel = plScalarControllerChannel()
            channel.controller = self._make_scalar_leaf_controller(keyframes, False)
            applicator = plSpotInnerApplicator()
            applicator.channelName = name
            applicator.channel = channel
            yield applicator

    def _convert_transform_animation(self, name, fcurves, xform, allow_empty=False):
        tm = self.convert_transform_controller(fcurves, xform, allow_empty)
        if tm is None and not allow_empty:
            return None

        applicator = plMatrixChannelApplicator()
        applicator.enabled = True
        applicator.channelName = name
        channel = plMatrixControllerChannel()
        channel.controller = tm
        applicator.channel = channel
        channel.affine = utils.affine_parts(xform)

        return applicator

    def convert_transform_controller(self, fcurves, xform, allow_empty=False):
        if not fcurves and not allow_empty:
            return None

        pos = self.make_pos_controller(fcurves, xform)
        rot = self.make_rot_controller(fcurves, xform)
        scale = self.make_scale_controller(fcurves, xform)
        if pos is None and rot is None and scale is None:
            if not allow_empty:
                return None

        tm = plCompoundController()
        tm.X = pos
        tm.Y = rot
        tm.Z = scale
        return tm

    def get_anigraph_keys(self, bo=None, so=None):
        mod = self._mgr.find_create_key(plAGModifier, so=so, bl=bo)
        master = self._mgr.find_create_key(plAGMasterMod, so=so, bl=bo)
        return mod, master

    def get_anigraph_objects(self, bo=None, so=None):
        mod = self._mgr.find_create_object(plAGModifier, so=so, bl=bo)
        master = self._mgr.find_create_object(plAGMasterMod, so=so, bl=bo)
        return mod, master

    def get_animation_key(self, bo, so=None):
        # we might be controlling more than one animation. isn't that cute?
        # https://www.youtube.com/watch?v=hspNaoxzNbs
        # (but obviously this is not wrong...)
        group_mod = bo.plasma_modifiers.animation_group
        if group_mod.enabled:
            return self._mgr.find_create_key(plMsgForwarder, bl=bo, so=so, name=group_mod.key_name)
        else:
            return self.get_anigraph_keys(bo, so)[1]

    def make_matrix44_controller(self, fcurves, pos_path, scale_path, pos_default, scale_default):
        def convert_matrix_keyframe(**kwargs):
            pos = kwargs.get(pos_path)
            scale = kwargs.get(scale_path)

            # Since only some position curves may be supplied, construct dict with all positions
            allpos = dict(enumerate(pos_default))
            allscale = dict(enumerate(scale_default))
            allpos.update(pos)
            allscale.update(scale)

            matrix = hsMatrix44()
            # Note: scale and pos are dicts, so we can't unpack
            matrix.setTranslate(hsVector3(allpos[0], allpos[1], allpos[2]))
            matrix.setScale(hsVector3(allscale[0], allscale[1], allscale[2]))
            return matrix

        fcurves = [i for i in fcurves if i.data_path == pos_path or i.data_path == scale_path]
        if not fcurves:
            return None

        default_values = { pos_path: pos_default, scale_path: scale_default }
        keyframes = self._process_fcurves(fcurves, convert_matrix_keyframe, default_values)
        if not keyframes:
            return None

        # Now we make the controller
        return self._make_matrix44_controller(keyframes)

    def make_pos_controller(self, fcurves, default_xform, convert=None):
        pos_curves = [i for i in fcurves if i.data_path == "location" and i.keyframe_points]
        keyframes, bez_chans = self._process_keyframes(pos_curves, convert)
        if not keyframes:
            return None

        # At one point, I had some... insanity here to try to crush bezier channels and hand off to
        # blah blah blah... As it turns out, point3 keyframe's tangents are vector3s :)
        ctrl = self._make_point3_controller(pos_curves, keyframes, bez_chans, default_xform.to_translation())
        return ctrl

    def make_rot_controller(self, fcurves, default_xform, convert=None):
        # TODO: support rotation_quaternion
        rot_curves = [i for i in fcurves if i.data_path == "rotation_euler" and i.keyframe_points]
        keyframes, bez_chans = self._process_keyframes(rot_curves, convert=None)
        if not keyframes:
            return None

        # Ugh. Unfortunately, it appears Blender's default interpolation is bezier. So who knows if
        # many users will actually see the benefit here? Makes me sad.
        if bez_chans:
            ctrl = self._make_scalar_compound_controller(rot_curves, keyframes, bez_chans, default_xform.to_euler())
        else:
            ctrl = self._make_quat_controller(rot_curves, keyframes, default_xform.to_euler())
        return ctrl

    def make_scale_controller(self, fcurves, default_xform, convert=None):
        scale_curves = [i for i in fcurves if i.data_path == "scale" and i.keyframe_points]
        keyframes, bez_chans = self._process_keyframes(scale_curves, convert)
        if not keyframes:
            return None

        # There is no such thing as a compound scale controller... in Plasma, anyway.
        ctrl = self._make_scale_value_controller(scale_curves, keyframes, bez_chans, default_xform)
        return ctrl

    def make_scalar_leaf_controller(self, fcurve, convert=None):
        keyframes, bezier = self._process_fcurve(fcurve, convert)
        if not keyframes:
            return None

        ctrl = self._make_scalar_leaf_controller(keyframes, bezier)
        return ctrl

    def _make_matrix44_controller(self, keyframes):
        ctrl = plLeafController()
        keyframe_type = hsKeyFrame.kMatrix44KeyFrame
        exported_frames = []

        for keyframe in keyframes:
            exported = hsMatrix44Key()
            exported.frame = keyframe.frame_num
            exported.frameTime = keyframe.frame_time
            exported.type = keyframe_type
            exported.value = keyframe.value
            exported_frames.append(exported)
        ctrl.keys = (exported_frames, keyframe_type)
        return ctrl

    def _make_point3_controller(self, fcurves, keyframes, bezier, default_xform):
        ctrl = plLeafController()
        subctrls = ("X", "Y", "Z")
        keyframe_type = hsKeyFrame.kBezPoint3KeyFrame if bezier else hsKeyFrame.kPoint3KeyFrame
        exported_frames = []
        ctrl_fcurves = { i.array_index: i for i in fcurves }

        for keyframe in keyframes:
            exported = hsPoint3Key()
            exported.frame = keyframe.frame_num
            exported.frameTime = keyframe.frame_time
            exported.type = keyframe_type

            in_tan = hsVector3()
            out_tan = hsVector3()
            value = hsVector3()
            for i, subctrl in enumerate(subctrls):
                fval = keyframe.values.get(i, None)
                if fval is not None:
                    setattr(value, subctrl, fval)
                    setattr(in_tan, subctrl, keyframe.in_tans[i])
                    setattr(out_tan, subctrl, keyframe.out_tans[i])
                else:
                    try:
                        setattr(value, subctrl, ctrl_fcurves[i].evaluate(keyframe.frame_num_blender))
                    except KeyError:
                        setattr(value, subctrl, default_xform[i])
                    setattr(in_tan, subctrl, 0.0)
                    setattr(out_tan, subctrl, 0.0)
            exported.inTan = in_tan
            exported.outTan = out_tan
            exported.value = value
            exported_frames.append(exported)
        ctrl.keys = (exported_frames, keyframe_type)
        return ctrl

    def _make_quat_controller(self, fcurves, keyframes, default_xform):
        ctrl = plLeafController()
        keyframe_type = hsKeyFrame.kQuatKeyFrame
        exported_frames = []
        ctrl_fcurves = { i.array_index: i for i in fcurves }

        for keyframe in keyframes:
            exported = hsQuatKey()
            exported.frame = keyframe.frame_num
            exported.frameTime = keyframe.frame_time
            exported.type = keyframe_type
            # NOTE: quat keyframes don't do bezier nonsense

            value = mathutils.Euler()
            for i in range(3):
                fval = keyframe.values.get(i, None)
                if fval is not None:
                    value[i] = fval
                else:
                    try:
                        value[i] = ctrl_fcurves[i].evaluate(keyframe.frame_num_blender)
                    except KeyError:
                        value[i] = default_xform[i]
            quat = value.to_quaternion()
            exported.value = utils.quaternion(quat)
            exported_frames.append(exported)
        ctrl.keys = (exported_frames, keyframe_type)
        return ctrl

    def _make_scalar_compound_controller(self, fcurves, keyframes, bez_chans, default_xform):
        ctrl = plCompoundController()
        subctrls = ("X", "Y", "Z")
        for i in subctrls:
            setattr(ctrl, i, plLeafController())
        exported_frames = ([], [], [])
        ctrl_fcurves = { i.array_index: i for i in fcurves }

        for keyframe in keyframes:
            for i, subctrl in enumerate(subctrls):
                fval = keyframe.values.get(i, None)
                if fval is not None:
                    keyframe_type = hsKeyFrame.kBezScalarKeyFrame if i in bez_chans else hsKeyFrame.kScalarKeyFrame
                    exported = hsScalarKey()
                    exported.frame = keyframe.frame_num
                    exported.frameTime = keyframe.frame_time
                    exported.inTan = keyframe.in_tans[i]
                    exported.outTan = keyframe.out_tans[i]
                    exported.type = keyframe_type
                    exported.value = fval
                    exported_frames[i].append(exported)
        for i, subctrl in enumerate(subctrls):
            my_keyframes = exported_frames[i]

            # ensure this controller has at least ONE keyframe
            if not my_keyframes:
                hack_frame = hsScalarKey()
                hack_frame.frame = 0
                hack_frame.frameTime = 0.0
                hack_frame.type = hsKeyFrame.kScalarKeyFrame
                hack_frame.value = default_xform[i]
                my_keyframes.append(hack_frame)
            getattr(ctrl, subctrl).keys = (my_keyframes, my_keyframes[0].type)
        return ctrl

    def _make_scalar_leaf_controller(self, keyframes, bezier):
        ctrl = plLeafController()
        keyframe_type = hsKeyFrame.kBezScalarKeyFrame if bezier else hsKeyFrame.kScalarKeyFrame
        exported_frames = []

        for keyframe in keyframes:
            exported = hsScalarKey()
            exported.frame = keyframe.frame_num
            exported.frameTime = keyframe.frame_time
            exported.inTan = keyframe.in_tan
            exported.outTan = keyframe.out_tan
            exported.type = keyframe_type
            exported.value = keyframe.value
            exported_frames.append(exported)
        ctrl.keys = (exported_frames, keyframe_type)
        return ctrl

    def _make_scale_value_controller(self, fcurves, keyframes, bez_chans, default_xform):
        subctrls = ("X", "Y", "Z")
        keyframe_type = hsKeyFrame.kBezScaleKeyFrame if bez_chans else hsKeyFrame.kScaleKeyFrame
        exported_frames = []
        ctrl_fcurves = { i.array_index: i for i in fcurves }

        default_scale = default_xform.to_scale()
        unit_quat = default_xform.to_quaternion()
        unit_quat.normalize()
        unit_quat = utils.quaternion(unit_quat)

        for keyframe in keyframes:
            exported = hsScaleKey()
            exported.frame = keyframe.frame_num
            exported.frameTime = keyframe.frame_time
            exported.type = keyframe_type

            in_tan = hsVector3()
            out_tan = hsVector3()
            value = hsVector3()
            for i, subctrl in enumerate(subctrls):
                fval = keyframe.values.get(i, None)
                if fval is not None:
                    setattr(value, subctrl, fval)
                    setattr(in_tan, subctrl, keyframe.in_tans[i])
                    setattr(out_tan, subctrl, keyframe.out_tans[i])
                else:
                    try:
                        setattr(value, subctrl, ctrl_fcurves[i].evaluate(keyframe.frame_num_blender))
                    except KeyError:
                        setattr(value, subctrl, default_scale[i])
                    setattr(in_tan, subctrl, 0.0)
                    setattr(out_tan, subctrl, 0.0)
            exported.inTan = in_tan
            exported.outTan = out_tan
            exported.value = (value, unit_quat)
            exported_frames.append(exported)

        ctrl = plLeafController()
        ctrl.keys = (exported_frames, keyframe_type)
        return ctrl

    def _process_fcurve(self, fcurve, convert=None):
        """Like _process_keyframes, but for one fcurve"""
        keyframe_data = type("KeyFrameData", (), {})
        fps = self._bl_fps
        pi = math.pi

        keyframes = {}
        bezier = False
        fcurve.update()
        for fkey in fcurve.keyframe_points:
            keyframe = keyframe_data()
            frame_num, value = fkey.co
            if fps == 30.0:
                keyframe.frame_num = int(frame_num)
            else:
                keyframe.frame_num = int(frame_num * (30.0 / fps))
            keyframe.frame_time = frame_num / fps
            if fkey.interpolation == "BEZIER":
                keyframe.in_tan = -(value - fkey.handle_left[1])  / (frame_num - fkey.handle_left[0])  / fps / (2 * pi)
                keyframe.out_tan = (value - fkey.handle_right[1]) / (frame_num - fkey.handle_right[0]) / fps / (2 * pi)
                bezier = True
            else:
                keyframe.in_tan = 0.0
                keyframe.out_tan = 0.0
            keyframe.value = value if convert is None else convert(value)
            keyframes[frame_num] = keyframe
        final_keyframes = [keyframes[i] for i in sorted(keyframes)]
        return (final_keyframes, bezier)

    def _process_fcurves(self, fcurves, convert, defaults=None):
        """Processes FCurves of different data sets and converts them into a single list of keyframes.
           This should be used when multiple Blender fields map to a single Plasma option."""
        class KeyFrameData:
            def __init__(self):
                self.values = {}
        fps = self._bl_fps
        pi = math.pi

        # It is assumed therefore that any multichannel FCurves will have all channels represented.
        # This seems fairly safe with my experiments with Lamp colors...
        grouped_fcurves = {}
        for fcurve in fcurves:
            if fcurve is None:
                continue
            fcurve.update()
            if fcurve.data_path in grouped_fcurves:
                grouped_fcurves[fcurve.data_path][fcurve.array_index] = fcurve
            else:
                grouped_fcurves[fcurve.data_path] = { fcurve.array_index: fcurve }

        # Default values for channels that are not animated
        for key, value in defaults.items():
            if key not in grouped_fcurves:
                if hasattr(value, "__len__"):
                    grouped_fcurves[key] = value
                else:
                    grouped_fcurves[key] = [value,]

        # Assemble a dict { PlasmaFrameNum: { FCurveDataPath: KeyFrame } }
        keyframe_points = {}
        for fcurve in fcurves:
            if fcurve is None:
                continue
            for keyframe in fcurve.keyframe_points:
                frame_num_blender, value = keyframe.co
                frame_num = int(frame_num_blender * (30.0 / fps))

                # This is a temporary keyframe, so we're not going to worry about converting everything
                # Only the frame number to Plasma so we can go ahead and merge any rounded dupes
                entry, data = keyframe_points.get(frame_num), None
                if entry is None:
                    entry = {}
                    keyframe_points[frame_num] = entry
                else:
                    data = entry.get(fcurve.data_path)
                if data is None:
                    data = KeyFrameData()
                    data.frame_num = frame_num
                    data.frame_num_blender = frame_num_blender
                    entry[fcurve.data_path] = data
                data.values[fcurve.array_index] = value

        # Now, we loop through our assembled keyframes and interpolate any missing data using the FCurves
        fcurve_chans = { key: len(value) for key, value in grouped_fcurves.items() }
        expected_values = sum(fcurve_chans.values())
        all_chans = frozenset(grouped_fcurves.keys())

        # We will also do the final convert here as well...
        final_keyframes = []

        for frame_num in sorted(keyframe_points.copy().keys()):
            keyframes = keyframe_points[frame_num]
            frame_num_blender = next(iter(keyframes.values())).frame_num_blender

            # If any data_paths are missing, init a dummy
            missing_channels = all_chans - frozenset(keyframes.keys())
            for chan in missing_channels:
                dummy = KeyFrameData()
                dummy.frame_num = frame_num
                dummy.frame_num_blender = frame_num_blender
                keyframes[chan] = dummy

            # Ensure all values are filled out.
            num_values = sum(map(len, (i.values for i in keyframes.values())))
            if num_values != expected_values:
                for chan, sorted_fcurves in grouped_fcurves.items():
                    chan_keyframes = keyframes[chan]
                    chan_values = fcurve_chans[chan]
                    if len(chan_keyframes.values) == chan_values:
                        continue
                    for i in range(chan_values):
                        if i not in chan_keyframes.values:
                            try:
                                fcurve = grouped_fcurves[chan][i]
                            except:
                                chan_keyframes.values[i] = defaults[chan]
                            else:
                                if isinstance(fcurve, bpy.types.FCurve):
                                    chan_keyframes.values[i] = fcurve.evaluate(chan_keyframes.frame_num_blender)
                                else:
                                    # it's actually a default value!
                                    chan_keyframes.values[i] = fcurve

            # All values are calculated! Now we convert the disparate key data into a single keyframe.
            kwargs = { data_path: keyframe.values for data_path, keyframe in keyframes.items() }
            final_keyframe = KeyFrameData()
            final_keyframe.frame_num = frame_num
            final_keyframe.frame_num_blender = frame_num_blender
            final_keyframe.frame_time = frame_num / fps
            value = convert(**kwargs)
            if hasattr(value, "__len__"):
                final_keyframe.in_tans = [0.0] * len(value)
                final_keyframe.out_tans = [0.0] * len(value)
                final_keyframe.values = value
            else:
                final_keyframe.in_tan = 0.0
                final_keyframe.out_tan = 0.0
                final_keyframe.value = value
            final_keyframes.append(final_keyframe)
        return final_keyframes


    def _process_keyframes(self, fcurves, convert=None):
        """Groups all FCurves for the same frame together"""
        keyframe_data = type("KeyFrameData", (), {})
        fps = self._bl_fps
        pi = math.pi

        keyframes = {}
        bez_chans = set()
        for fcurve in fcurves:
            fcurve.update()
            for fkey in fcurve.keyframe_points:
                frame_num, value = fkey.co
                keyframe = keyframes.get(frame_num, None)
                if keyframe is None:
                    keyframe = keyframe_data()
                    if fps == 30.0:
                        # hope you don't have a frame 29.9 and frame 30.0...
                        keyframe.frame_num = int(frame_num)
                    else:
                        keyframe.frame_num = int(frame_num * (30.0 / fps))
                    keyframe.frame_num_blender = frame_num
                    keyframe.frame_time = frame_num / fps
                    keyframe.in_tans = {}
                    keyframe.out_tans = {}
                    keyframe.values = {}
                    keyframes[frame_num] = keyframe
                idx = fcurve.array_index
                keyframe.values[idx] = value if convert is None else convert(value)

                # Calculate the bezier interpolation nonsense
                if fkey.interpolation == "BEZIER":
                    keyframe.in_tans[idx] = -(value - fkey.handle_left[1])  / (frame_num - fkey.handle_left[0])  / fps / (2 * pi)
                    keyframe.out_tans[idx] = (value - fkey.handle_right[1]) / (frame_num - fkey.handle_right[0]) / fps / (2 * pi)
                    bez_chans.add(idx)
                else:
                    keyframe.in_tans[idx] = 0.0
                    keyframe.out_tans[idx] = 0.0

        # Return the keyframes in a sequence sorted by frame number
        final_keyframes = [keyframes[i] for i in sorted(keyframes)]
        return (final_keyframes, bez_chans)

    @property
    def _mgr(self):
        return self._exporter().mgr
