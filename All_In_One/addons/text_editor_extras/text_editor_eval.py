import bpy


def strict_eval(input_string):
    '''
    Test the input, avoid evaluating strings that are probably not
    intended for execution.

    The only thing of which this script can be fairly certain is that
    the content of the clipboard is filled by the text.copy() operation.
    '''
    try:
        answer = str(eval(input_string))
        return answer
    except:
        print('addon not smart enough yet to read minds')
        
    return input_string



class TextEval(bpy.types.Operator):
    bl_label = ""
    bl_idname = "txt.eval_selected_text"
    
    def execute(self, context):
        bpy.ops.text.copy()
        copied_text = bpy.data.window_managers[0].clipboard
        answer = strict_eval(copied_text)
        bpy.data.window_managers[0].clipboard = answer
        bpy.ops.text.paste()
        return {'FINISHED'}

