
import bpy

def SplitText(text, maxWidth):

    result_text = []
    lineWidth = 0
    lastSpace = -1
    i = 0
    while i < len(text):
        if(lineWidth >= maxWidth):
            if(lastSpace != -1):
                result_text.append(text[i - lineWidth:lastSpace])
                i = lastSpace + 1
                lastSpace = -1
            else:
                result_text.append(text[i - lineWidth:i])
            lineWidth = 0
        if(text[i] == ' '):
            lastSpace = i
        lineWidth += 1
        i += 1
    if(lineWidth > 0):
        result_text.append(text[i-lineWidth-1:i-1])
    return result_text

class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    #type = StringProperty()
    message = bpy.props.StringProperty()
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
    def invoke(self, context, event):
        self.report({'INFO'}, self.message)
        print(self.message)
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)
    def draw(self, context):
        text = SplitText(self.message, 70)
        self.layout.label(text[0], icon='ERROR')
        for iLine in range(1, len(text)):
            self.layout.label(text[iLine])
