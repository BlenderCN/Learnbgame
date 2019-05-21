import bpy
from bpy.types import Panel, Operator
from bpy.props import StringProperty
from sound_drivers.sound_action import SoundActionMethods
from bpy.utils import register_class, unregister_class
from sound_drivers.utils import getAction, getSpeaker

class VisualiserOptions(Operator):
    """Visualiser Options"""
    bl_idname = "action.visualiser"
    bl_label = "Visualiser Options"
    action_name = StringProperty(default="", options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def execute(self, context):
        return {'FINISHED'}
        pass

    def draw(self, context):
        action = bpy.data.actions.get(self.action_name)
        layout = self.layout
        layout.label("Visualiser Settings", icon='SEQ_HISTOGRAM')
        col = layout.column()
        col.prop(action, "vismode", expand=True)
        row = layout.row(align=True)
        sub = row.row()
        sub.alignment = 'LEFT'
        sub.label("", icon='NLA')
        col = row.row()
        col.prop(action, '["row_height"]', text="h", slider=True)
        col = layout.row()
        col.prop(action, '["start"]', text="Start", slider=True)
        col.prop(action, '["end"]', text="  End", slider=True)

class SoundVisualiserPanel(SoundActionMethods, Panel):
    bl_label = "Visualiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    vismode = 'VISUAL'
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        speaker = getSpeaker(context)
        if speaker is None:
            return False

        if context.space_data.pin_id is not None:
            if context.space_data.pin_id == speaker:
                return cls.vismode in speaker.vismode

        return (context.object.data == speaker and cls.vismode
                in speaker.vismode)

    def draw_header(self, context):
        layout = self.layout
        speaker = getSpeaker(context)
        action = getAction(speaker)
        if not action:
            layout.label("", icon='SEQ_HISTOGRAM')
            return

        op = layout.operator("action.visualiser", icon='SEQ_HISTOGRAM',
                             emboss=False, text="")
        op.action_name = action.name

    def draw(self, context):
        layout = self.layout
        layout.enabled = not bpy.types.BakeSoundPanel.baking
        speaker = getSpeaker(context)
        action = getAction(speaker)

        #checks
        if speaker.sound is None:
            layout.label("Speaker has No Sound", icon='INFO')
            return
        if action is None:
            layout.label("No Action Baked", icon='INFO')
            return
        elif action is None:
            layout.label("No Action Baked", icon='INFO')
            return
        elif action['wavfile'] != speaker.sound.name:
            layout.label("No Action Baked", icon='INFO')
            layout.label("for %s" % speaker.sound.name)
            return
        '''
        layout.label(repr(action))
        if action:
            layout.label(action['wavfile'])

        '''
        if not bpy.types.BakeSoundPanel.baking:
            if action.vismode == 'SLIDER':
                self.Sliders(context)
            elif action.vismode == 'FCURVE':
                self.FCurveSliders(context)
            elif action.vismode == 'VERTICAL':
                self.EBT(context)
            elif action.vismode == 'TABSTER':
                self.EBT(context)

def register():
    register_class(SoundVisualiserPanel)
    register_class(VisualiserOptions)

def unregister():
    unregister_class(SoundVisualiserPanel)
    unregister_class(VisualiserOptions)
