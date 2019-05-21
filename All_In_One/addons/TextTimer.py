bl_info = {
    "name": "TextTimer",
    "author": "Sondre Dalen (Eroyal)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Video Sequence Editor > Add > Effect Strip > TextTimer",
    "description": "Add a timer to your video",
    "wiki_url": "",
    "category": "Sequencer",
    }


import bpy
from bpy.types import Panel, Operator, TextSequence


class TextTimer(Panel):
    """Text Timer for use in video editing."""
    bl_label = "Text Timer"
    bl_idname = "SEQUENCE_TextTimer"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_categroy = "Strip"

    

    @classmethod
    def poll(cls, context):
        return isinstance(context.selected_sequences[0],TextSequence)

    def draw(self,context):
        text_seq = context.selected_sequences[0]
        layout = self.layout

        row = layout.row()
        row.prop(text_seq,"use_textTimer",toggle=True)
        if text_seq.use_textTimer:
            
            row = layout.row()
            row.prop(text_seq,"textTimer_format")

            row = layout.row()
            row.prop(text_seq,"textTimer_start_value")
            row.prop(text_seq,"textTimer_speed")
            
            row = layout.row(True)
            row.prop(text_seq,"textTimer_start_at")
            row.prop(text_seq,"textTimer_end_at")

    def text_update(self,context):
        handler_TextTimer(context.scene)
        return


def handler_TextTimer(scene):
    time = {'h':0 ,'H':0 ,'m':0 ,'M':0 ,'s':0 ,'S':0 ,'f':0 ,'F':0}
    fps = scene.render.fps

    text_seqs = [t for t in scene.sequence_editor.sequences_all if hasattr(t,'use_textTimer') and t.use_textTimer]
    for text_seq in text_seqs:
        if text_seq.textTimer_start_at < text_seq.frame_start: text_seq.textTimer_start_at = text_seq.frame_start
        if text_seq.textTimer_start_at > text_seq.frame_final_end: text_seq.textTimer_start_at = text_seq.frame_final_end
        if text_seq.textTimer_end_at < text_seq.frame_start: text_seq.textTimer_end_at = text_seq.frame_start
        if text_seq.textTimer_end_at > text_seq.frame_final_end: text_seq.textTimer_end_at = text_seq.frame_final_end
        frame_time = 0

        
        start = text_seq.textTimer_start_at
        end =  text_seq.textTimer_end_at

        start_value = fps*text_seq.textTimer_start_value

        if scene.frame_current <= start:
            frame_time = start_value

        elif scene.frame_current >= end:
            frame_time = int(start_value + ((end-start) * text_seq.textTimer_speed))

        else:
            frame_time = int(start_value + ((scene.frame_current - start) * text_seq.textTimer_speed))


        format = text_seq.textTimer_format

        format = format.replace("%h","{h:02d}")
        format = format.replace("%m","{m:02d}")
        format = format.replace("%s","{s:02d}")
        format = format.replace("%f","{f:02d}")
        format = format.replace("%H","{H:2d}")
        format = format.replace("%M","{M:2d}")
        format = format.replace("%S","{S:2d}")
        format = format.replace("%F","{F:2d}")



        this_time = time.copy()
        this_time['F'] = frame_time
        this_time['f'] = frame_time % fps
        this_time['S'] = frame_time / fps
        this_time['s'] = frame_time / fps % 60
        this_time['M'] = frame_time / fps / 60
        this_time['m'] = frame_time / fps / 60 % 60
        this_time['H'] = frame_time / fps / 60 / 60
        this_time['h'] = frame_time / fps / 60 / 60 % 24

        for x in this_time:
            this_time[x] = int(this_time[x])

        text_seq.text = format.format(**this_time)




def register():
    #Enable
    TextSequence.use_textTimer = bpy.props.BoolProperty(name="Use TextTimer",\
        description="Enable the TextTimer addon for this Text Strip.",\
        default=False)

    #formating
    TextSequence.textTimer_format = bpy.props.StringProperty(name="Text format",\
        description="Format of the text, use:\nHour: %h = [00-24], %H = [0-inf]\nMinute: %m = [0-60], %M = [0-inf]\nSecond: %s = [0-60], \nFrame: %f = [0-fps], %F = [0-inf]",\
        update=TextTimer.text_update,\
        default="%m:%s")

    #start value
    TextSequence.textTimer_start_value = bpy.props.FloatProperty(name="Start time (in seconds)",\
        description="Starting time. (in seconds), so staring at one hour is 3600.0",\
        update=TextTimer.text_update,\
        default=0.0)

    #speed
    TextSequence.textTimer_speed = bpy.props.FloatProperty(name="Speed multiplier",\
        description="Multiply the speed of time. (Mainly used when a speed effect is applied",\
        update=TextTimer.text_update,\
        default=1.0)

    #start at
    TextSequence.textTimer_start_at = bpy.props.IntProperty(name="Start at",\
        description="Start counting after frame",\
        update=TextTimer.text_update,\
        default=0)

    #end at
    TextSequence.textTimer_end_at = bpy.props.IntProperty(name="Stop at",\
        description="Stop counting at frame",\
        update=TextTimer.text_update,\
        default=0)

    bpy.utils.register_class(TextTimer)
    bpy.app.handlers.frame_change_pre.append(handler_TextTimer)
    bpy.app.handlers.render_pre.append(handler_TextTimer)


def unregister():
    bpy.utils.unregister_class(TextTimer)


if __name__ == "__main__":
    register()
