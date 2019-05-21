#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------

# section 1
# bl_info must be initialized in this file, as it gets parsed
bl_info = \
    {
        "name": "Console Scripts 2",
        "author" : "Walid Shouman <eng.walidshouman@gmail.com>",
        "version" : (1, 0, 0),
        "blender" : (2, 7, 9),
        "location" : "Python API, only through code",
        "description" :
            "Expose console_writer.console_write method to print on all open consoles instead of the terminal",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category": "Development",
    }
# end of section 1

import os
current_directory = os.path.dirname(os.path.abspath(__file__))

# section 2
# support addon reloading
reloadfile = os.path.join(current_directory, '__reload__.py')
exec(open(reloadfile).read())
# end of section 2

import bpy
from .utils import console_writer

class ConsoleWriterOperator(bpy.types.Operator):
    bl_idname = "console.console_write_operator"
    bl_label = "Console Write"

    myString = bpy.props.StringProperty(name="message string")

    def execute(self, context):
        console_writer.console_write(self.myString)
        return {'FINISHED'}

    def invoke(self, context, event):
        pass
        # wm = context.window_manager
        # return wm.invoke_props_dialog(self)

# section 3
# support addon registration
registrationfile = os.path.join(current_directory, '__register__.py')
exec(open(registrationfile).read())

if __name__ == "__main__":
    register()
# end of section 3
