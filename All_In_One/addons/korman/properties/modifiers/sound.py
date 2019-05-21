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
from bpy.app.handlers import persistent
import math
from pathlib import Path
from PyHSPlasma import *

from ... import korlib
from .base import PlasmaModifierProperties
from ...exporter import ExportError
from ... import idprops

class PlasmaSfxFade(bpy.types.PropertyGroup):
    fade_type = EnumProperty(name="Type",
                             description="Fade Type",
                             items=[("NONE", "[Disable]", "Don't fade"),
                                    ("kLinear", "Linear", "Linear fade"),
                                    ("kLogarithmic", "Logarithmic", "Log fade"),
                                    ("kExponential", "Exponential", "Exponential fade")],
                             options=set())
    length = FloatProperty(name="Length",
                           description="Seconds to spend fading",
                           default=1.0, min=0.0,
                           options=set(), subtype="TIME", unit="TIME")


class PlasmaSound(idprops.IDPropMixin, bpy.types.PropertyGroup):
    def _get_name_proxy(self):
        if self.sound is not None:
            return self.sound.name
        return ""

    def _set_name_proxy(self, value):
        self.sound = bpy.data.sounds.get(value, None)

        # This is the actual pointer update callback
        if not self.sound:
            self.name = "[Empty]"
            return

        try:
            header, size = self._get_sound_info()
        except Exception as e:
            self.is_valid = False
            # this might be perfectly acceptable... who knows?
            # user consumable error report to be handled by the UI code
            print("---Invalid SFX selection---\n{}\n------".format(str(e)))
        else:
            self.is_valid = True
            self.is_stereo = header.numChannels == 2
        self._update_name()

    def _update_name(self, context=None):
        if self.is_stereo and self.channel != {"L", "R"}:
            self.name = "{}:{}".format(self._sound_name, "L" if "L" in self.channel else "R")
        else:
            self.name = self._sound_name

    enabled = BoolProperty(name="Enabled", default=True, options=set())
    sound = PointerProperty(name="Sound",
                            description="Sound Datablock",
                            type=bpy.types.Sound)

    # This is needed because pointer properties do not seem to allow update CBs... Bug?
    sound_data_proxy = StringProperty(name="Sound",
                                      description="Name of sound datablock",
                                      get=_get_name_proxy,
                                      set=_set_name_proxy,
                                      options=set())

    is_stereo = BoolProperty(default=True, options={"HIDDEN"})
    is_valid = BoolProperty(default=False, options={"HIDDEN"})

    sfx_region = PointerProperty(name="Soft Volume",
                                 description="Soft region this sound can be heard in",
                                 type=bpy.types.Object,
                                 poll=idprops.poll_softvolume_objects)

    sfx_type = EnumProperty(name="Category",
                            description="Describes the purpose of this sound",
                            items=[("kSoundFX", "3D", "3D Positional SoundFX"),
                                   ("kAmbience", "Ambience", "Ambient Sounds"),
                                   ("kBackgroundMusic", "Music", "Background Music"),
                                   ("kGUISound", "GUI", "GUI Effect"),
                                   ("kNPCVoices", "NPC", "NPC Speech")],
                            options=set())
    channel = EnumProperty(name="Channel",
                           description="Which channel(s) to play",
                           items=[("L", "Left", "Left Channel"),
                                  ("R", "Right", "Right Channel")],
                           options={"ENUM_FLAG"},
                           default={"L", "R"},
                           update=_update_name)

    auto_start = BoolProperty(name="Auto Start",
                              description="Start playing when the age is loaded",
                              default=False,
                              options=set())
    incidental = BoolProperty(name="Incidental",
                              description="Sound is a low-priority incident and the engine may forgo playback",
                              default=False,
                              options=set())
    loop = BoolProperty(name="Loop",
                        description="Loop the sound",
                        default=False,
                        options=set())

    inner_cone = FloatProperty(name="Inner Angle",
                               description="Angle of the inner cone from the negative Z-axis",
                               min=0, max=math.radians(360), default=0, step=100,
                               options=set(),
                               subtype="ANGLE")
    outer_cone = FloatProperty(name="Outer Angle",
                               description="Angle of the outer cone from the negative Z-axis",
                               min=0, max=math.radians(360), default=math.radians(360), step=100,
                               options=set(),
                               subtype="ANGLE")
    outside_volume = IntProperty(name="Outside Volume",
                         description="Sound's volume when outside the outer cone",
                         min=0, max=100, default=100,
                         options=set(),
                         subtype="PERCENTAGE")

    min_falloff = IntProperty(name="Begin Falloff",
                              description="Distance where volume attenuation begins",
                              min=0, max=1000000000, default=1,
                              options=set(),
                              subtype="DISTANCE")
    max_falloff = IntProperty(name="End Falloff",
                              description="Distance where the sound is inaudible",
                              min=0, max=1000000000, default=1000,
                              options=set(),
                              subtype="DISTANCE")
    volume = IntProperty(name="Volume",
                         description="Volume to play the sound",
                         min=0, max=100, default=100,
                         options={"ANIMATABLE"},
                         subtype="PERCENTAGE")

    fade_in = PointerProperty(type=PlasmaSfxFade, options=set())
    fade_out = PointerProperty(type=PlasmaSfxFade, options=set())

    @property
    def channel_override(self):
        if self.is_stereo and len(self.channel) == 1:
            return min(self.channel)
        else:
            return None

    def convert_sound(self, exporter, so, audible):
        header, dataSize = self._get_sound_info()
        length = dataSize / header.avgBytesPerSec

        # HAX: Ensure that the sound file is copied to game, if applicable.
        exporter.output.add_sfx(self._sound)

        # There is some bug in the MOUL code that causes a crash if this does not match the expected
        # result. There's no sense in debugging that though--the user should never specify
        # streaming vs static. That's an implementation detail.
        pClass = plWin32StreamingSound if length > 4.0 else plWin32StaticSound

        # OK. Any Plasma engine that uses OpenAL (MOUL) is subject to this restriction.
        # 3D Positional audio MUST... and I mean MUST... have mono emitters.
        # That means if the user has specified 3D and a stereo sound AND both channels, we MUST
        # export two emitters from here. Otherwise, it's no biggie. Wheeeeeeeeeeeeeeeeeeeeeeeee
        if self.is_3d_stereo or (self.is_stereo and len(self.channel) == 1):
            header.avgBytesPerSec = int(header.avgBytesPerSec / 2)
            header.numChannels = int(header.numChannels / 2)
            header.blockAlign = int(header.blockAlign / 2)
            dataSize = int(dataSize / 2)
        if self.is_3d_stereo:
            audible.addSound(self._convert_sound(exporter, so, pClass, header, dataSize, channel="L"))
            audible.addSound(self._convert_sound(exporter, so, pClass, header, dataSize, channel="R"))
        else:
            audible.addSound(self._convert_sound(exporter, so, pClass, header, dataSize, channel=self.channel_override))

    def _convert_sound(self, exporter, so, pClass, wavHeader, dataSize, channel=None):
        if channel is None:
            name = "Sfx-{}_{}".format(so.key.name, self._sound_name)
        else:
            name = "Sfx-{}_{}:{}".format(so.key.name, self._sound_name, channel)
        exporter.report.msg("[{}] {}", pClass.__name__[2:], name, indent=1)
        sound = exporter.mgr.find_create_object(pClass, so=so, name=name)

        # If this object is a soft volume itself, we will use our own soft region.
        # Otherwise, check what they specified...
        sv_mod, sv_key = self.id_data.plasma_modifiers.softvolume, None
        if sv_mod.enabled:
            sv_key = sv_mod.get_key(exporter, so)
        elif self.sfx_region:
            sv_mod = self.sfx_region.plasma_modifiers.softvolume
            if not sv_mod.enabled:
                raise ExportError("'{}': SoundEmit '{}', '{}' is not a SoftVolume".format(self.id_data.name, self._sound_name, self.sfx_region.name))
            sv_key = sv_mod.get_key(exporter)
        if sv_key is not None:
            sv_key.object.listenState |= plSoftVolume.kListenCheck | plSoftVolume.kListenDirty | plSoftVolume.kListenRegistered
            sound.softRegion = sv_key

        # Sound
        sound.type = getattr(plSound, self.sfx_type)
        if sound.type == plSound.kSoundFX:
            sound.properties |= plSound.kPropIs3DSound
        if self.auto_start:
            sound.properties |= plSound.kPropAutoStart
        if self.loop:
            sound.properties |= plSound.kPropLooping
        if self.incidental:
            sound.properties |= plSound.kPropIncidental
        sound.dataBuffer = self._find_sound_buffer(exporter, so, wavHeader, dataSize, channel)

        # Cone effect
        # I have observed that Blender 2.77's UI doesn't show the appropriate unit (degrees) for
        # IntProperty angle subtypes. So, we're storing the angles as floats in Blender even though
        # Plasma only wants integers. Sigh.
        sound.innerCone = int(math.degrees(self.inner_cone))
        sound.outerCone = int(math.degrees(self.outer_cone))
        sound.outerVol = self.outside_volume

        # Falloff
        sound.desiredVolume = self.volume / 100.0
        sound.minFalloff = self.min_falloff
        sound.maxFalloff = self.max_falloff

        # Fade FX
        fade_in, fade_out = sound.fadeInParams, sound.fadeOutParams
        for blfade, plfade in ((self.fade_in, fade_in), (self.fade_out, fade_out)):
            if blfade.fade_type == "NONE":
                plfade.lengthInSecs = 0.0
            else:
                plfade.lengthInSecs = blfade.length
                plfade.type = getattr(plSound.plFadeParams, blfade.fade_type)
            plfade.currTime = -1.0

        # Some manual fiddling -- this is hidden deep inside the 3dsm exporter...
        # Kind of neat how it's all generic though :)
        fade_in.volStart = 0.0
        fade_in.volEnd = 1.0
        fade_out.volStart = 1.0
        fade_out.volEnd = 0.0
        fade_out.stopWhenDone = True

        # Some last minute buffer tweaking based on our props here...
        buffer = sound.dataBuffer.object
        if isinstance(sound, plWin32StreamingSound):
            buffer.flags |= plSoundBuffer.kStreamCompressed
        if sound.type == plSound.kBackgroundMusic:
            buffer.flags |= plSoundBuffer.kAlwaysExternal

        # Win32Sound
        if channel == "L":
            sound.channel = plWin32Sound.kLeftChannel
        else:
            sound.channel = plWin32Sound.kRightChannel

        # Whew, that was a lot of work!
        return sound.key

    def _get_sound_info(self):
        """Generates a tuple (plWAVHeader, PCMsize) from the current sound"""
        sound = self._sound
        if sound.packed_file is None:
            stream = hsFileStream()
            try:
                stream.open(sound.filepath, fmRead)
            except IOError:
                self._raise_error("failed to open file")
        else:
            stream = hsRAMStream()
            stream.buffer = sound.packed_file.data

        try:
            magic = stream.read(4)
            stream.rewind()

            header = plWAVHeader()
            if magic == b"RIFF":
                size = korlib.inspect_wavefile(stream, header)
                return (header, size)
            elif magic == b"OggS":
                size = korlib.inspect_vorbisfile(stream, header)
                return (header, size)
            else:
                raise NotSupportedError("unsupported audio format")
        except Exception as e:
            self._raise_error(str(e))
        finally:
            stream.close()

    def _find_sound_buffer(self, exporter, so, wavHeader, dataSize, channel):
        # First, cleanup the file path to not have directories
        filename = Path(self._sound.filepath).name
        if channel is None:
            key_name = filename
        else:
            key_name = "{}:{}".format(filename, channel)

        key = exporter.mgr.find_key(plSoundBuffer, so=so, name=key_name)
        if key is None:
            sound = exporter.mgr.add_object(plSoundBuffer, so=so, name=key_name)
            sound.header = wavHeader
            sound.fileName = filename
            sound.dataLength = dataSize
            # Maybe someday we will allow packed sounds? I'm in no hurry...
            sound.flags |= plSoundBuffer.kIsExternal
            if channel == "L":
                sound.flags |= plSoundBuffer.kOnlyLeftChannel
            elif channel == "R":
                sound.flags |= plSoundBuffer.kOnlyRightChannel
            key = sound.key
        return key

    @classmethod
    def _idprop_mapping(cls):
        return {"sound": "sound_data",
                "sfx_region": "soft_region"}

    def _idprop_sources(self):
        return {"sound_data": bpy.data.sounds,
                "soft_region": bpy.data.objects}

    @property
    def is_3d_stereo(self):
        return self.sfx_type == "kSoundFX" and self.channel == {"L", "R"} and self.is_stereo

    def _raise_error(self, msg):
        if self.sound:
            raise ExportError("SoundEmitter '{}': Sound '{}' {}".format(self.id_data.name, self.sound.name, msg))
        else:
            raise ExportError("SoundEmitter '{}': {}".format(self.id_data.name, msg))

    @property
    def _sound(self):
        if not self.sound:
            self._raise_error("has an invalid sound specified")
        return self.sound

    @property
    def _sound_name(self):
        if self.sound:
            return self.sound.name
        return ""


class PlasmaSoundEmitter(PlasmaModifierProperties):
    pl_id = "soundemit"

    bl_category = "Logic"
    bl_label = "Sound Emitter"
    bl_description = "Point at which sound(s) are played"
    bl_icon = "SPEAKER"

    sounds = CollectionProperty(type=PlasmaSound)
    active_sound_index = IntProperty(options={"HIDDEN"})

    def export(self, exporter, bo, so):
        winaud = exporter.mgr.find_create_object(plWinAudible, so=so, name=self.key_name)
        winaud.sceneNode = exporter.mgr.get_scene_node(so.key.location)
        aiface = exporter.mgr.find_create_object(plAudioInterface, so=so, name=self.key_name)
        aiface.audible = winaud.key

        # Pass this off to each individual sound for conversion
        for i in self.sounds:
            if i.enabled:
                i.convert_sound(exporter, so, winaud)

    def get_sound_indices(self, name=None, sound=None):
        """Returns the index of the given sound in the plWin32Sound. This is needed because stereo
           3D sounds export as two mono sound objects -- wheeeeee"""
        assert name or sound
        idx = 0

        if name is None:
            for i in self.sounds:
                if i == sound:
                    yield idx
                    if i.is_3d_stereo:
                        yield idx + 1
                    break
                else:
                    idx += 2 if i.is_3d_stereo else 1
            else:
                raise LookupError(sound)

        if sound is None:
            for i in self.sounds:
                if i.name == name:
                    yield idx
                    if i.is_3d_stereo:
                        yield idx + 1
                    break
                else:
                    idx += 2 if i.is_3d_stereo else 1
            else:
                raise ValueError(name)

    @property
    def requires_actor(self):
        return True
