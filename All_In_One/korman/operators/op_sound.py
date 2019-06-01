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

class SoundOperator:
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "PLASMA_GAME"


class PlasmaSoundOpenOperator(SoundOperator, bpy.types.Operator):
    bl_idname = "sound.plasma_open"
    bl_label = "Load Sound"
    bl_options = {"INTERNAL"}

    filter_glob = StringProperty(default="*.ogg;*.wav", options={"HIDDEN"})
    filepath = StringProperty(subtype="FILE_PATH")

    data_path = StringProperty(options={"HIDDEN"})
    sound_property = StringProperty(options={"HIDDEN"})

    def execute(self, context):
        # Check to see if the sound exists... Because the sneakily introduced bpy.data.sounds.load
        # check_existing doesn't tell us if it already exists... dammit...
        for i in bpy.data.sounds:
            if self.filepath == i.filepath:
                sound = i
                break
        else:
            sound = bpy.data.sounds.load(self.filepath)

        # Now do the stanky leg^H^H^H^H^H^H^H^H^H^H deed and put the sound on the mod
        # NOTE: must use the name so that the mod can receive update callbacks
        dest = eval(self.data_path)
        setattr(dest, self.sound_property, sound.name)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class PlasmaSoundPackOperator(SoundOperator, bpy.types.Operator):
    bl_idname = "sound.plasma_pack"
    bl_label = "Pack"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        soundemit = context.active_object.plasma_modifiers.soundemit
        soundemit.sounds[soundemit.active_sound_index].sound.pack()
        return {"FINISHED"}


class PlasmaSoundUnpackOperator(SoundOperator, bpy.types.Operator):
    bl_idname = "sound.plasma_unpack"
    bl_label = "Unpack"
    bl_options = {"INTERNAL"}

    method = EnumProperty(name="Method", description="How to unpack",
                          # See blender/makesrna/intern/rna_packedfile.c
                          items=[("USE_LOCAL", "Use local file", "", 5),
                                 ("WRITE_LOCAL", "Write Local File (overwrite existing)", "", 4),
                                 ("USE_ORIGINAL", "Use Original File", "", 6),
                                 ("WRITE_ORIGINAL", "Write Original File (overwrite existing)", "", 3)],
                          options=set())

    def execute(self, context):
        soundemit = context.active_object.plasma_modifiers.soundemit
        soundemit.sounds[soundemit.active_sound_index].sound.unpack(self.method)
        return {"FINISHED"}
