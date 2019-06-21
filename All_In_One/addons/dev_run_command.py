
bl_info = {
    'name': 'Prompt and Run Command ',
    "category": "Learnbgame",
    'description': 'Execute expressions in command prompt'
}


import bpy


class RunCommandOperator(bpy.types.Operator):
    bl_idname = 'debug.run_command'
    bl_label = 'Debug Run Command'
    bl_options = {'INTERNAL', 'REGISTER'}

    def draw(self, context):
        layout = self.layout
        
        import builtins

        try:
            input = context.window_manager.prompt.strip()
            
            if input.startswith('context.'):
                data_path = eval(input)
            elif input in context.rna_type.properties:
                data_path = getattr(context, input)
            else:
                data_path = context.path_resolve(input)
            message = str(data_path)
        except builtins.Exception as e:
            message = '{}'.format(e.__class__.__name__) + ': '
            message += str(e).replace('\n', ': ')
            try:
                data_path = eval(input)
                message = data_path
            except builtins.Exception as e:
                message = '{}'.format(e.__class__.__name__) + ': '
                message += str(e).replace('\n', ': ')
   
        layout.label(">>> {}".format(input if input else "<empty command>"))
        layout.label("{}".format(message))

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=640, height=480)

    def execute(self, context):
        return {'FINISHED'}


def debug_run_command_prompt_draw(self, context):
    layout = self.layout
    col = layout.column()
    col.alert = True
    col.scale_x = 2.5
    col.prop(context.window_manager, 'prompt', text='', icon='CONSOLE')


def execute_run_command_prompt(self, context):
    bpy.ops.debug.run_command('INVOKE_DEFAULT')


def register():
    bpy.utils.register_class(RunCommandOperator)
    bpy.types.WindowManager.prompt = bpy.props.StringProperty(name='prompt', default='', update=execute_run_command_prompt)
    bpy.types.TEXT_HT_header.append(debug_run_command_prompt_draw)


def unregister():
    bpy.utils.unregister_class(RunCommandOperator)
    bpy.types.TEXT_HT_header.remove(debug_run_command_prompt_draw)
    del bpy.types.WindowManager.prompt


if __name__ == '__main__':
    register()
    #bpy.ops.debug.area_run_command('INVOKE_DEFAULT')

