import bpy
from bpy.types import (Panel)
from bpy.utils import register_class, unregister_class
from sound_drivers.sound_action import SoundActionMethods
from sound_drivers.utils import (getSpeaker, getAction, unique_name)

class SoundNLAPanel(SoundActionMethods, Panel):
    bl_label = "NLA Mixer Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)

        return (speaker
                and hasattr(speaker, "animation_data")
                and 'NLA' in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        layout.label("", icon='NLA')

    def draw(self, context):
        layout = self.layout
        from sound_drivers.sound_bake import BakeSoundPanel
        layout.enabled = not BakeSoundPanel.baking
        self.nla_tracks(context)

def register():
    register_class(SoundNLAPanel)
    pass

def unregister():
    unregister_class(SoundNLAPanel)
    pass
