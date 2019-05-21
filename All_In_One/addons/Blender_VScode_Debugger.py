'''
Debugging Support for Visual Studio Code

Prerequest: PTVSD module should have been installed (using pip to install), also the 'Python' (by Don Jaymanne) plugin of VSCode.

After this add-on installed and activated, press [Spacebar] then search 'connect', select "Connect to Visual Studio Code Debugger" to start forwarding debugging information to VSCode.

In VSCode, configure the debugger to "Remote", then you can start debugging in VSCode.

Author: Zhang Bo-Ning
Inspired by https://github.com/sybrenstuvel/random-blender-addons/blob/master/remote_debugger.py
'''
bl_info = {
    'name': 'Debugger for Visual Code',
    'author': 'Zhang Bo-ning',
    'version': (0, 1),
    'blender': (2, 78, 0),
    'location': 'Press [Space], search for "debugger"',
    'category': 'Development',
}

import bpy
import sys
import os
from bpy.types import AddonPreferences
from bpy.props import StringProperty

class DebuggerAddonPreferences(AddonPreferences):
    bl_idname = __name__

    ptvsdPath = StringProperty(
        name='Path of PTVSD module',
        subtype='DIR_PATH',
        default='/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages'
    )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'ptvsdPath')
        layout.label(text='Path for PTVSD module. In macOS, path should be something like: "/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages"')


class Debug_Connect_To_Vscode(bpy.types.Operator): 
    bl_idname = 'debug.connect_debugger_vscode'
    bl_label = 'Connect to Visual Studio Code Debugger'
    bl_description = 'Connect to the remote visual studio debugger'
    
    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        
        ptvsdPath = os.path.abspath(addon_prefs.ptvsdPath)

        if not os.path.exists(ptvsdPath):
            self.report({'ERROR'}, 'Unable to find PTVSD module at %r. Configure the addon properties '
                                   'in the User Preferences menu.' % ptvsdPath)
            return {'CANCELLED'}
        
        if not any(ptvsdPath in p for p in sys.path):
            sys.path.append(ptvsdPath)

        import ptvsd
        ptvsd.enable_attach("my_secret", address = ('0.0.0.0', 3000))
        return {'FINISHED'}

        
def register():
    bpy.utils.register_class(Debug_Connect_To_Vscode)
    bpy.utils.register_class(DebuggerAddonPreferences)    
    
def unregister():
    bpy.utils.unregister_class(Debug_Connect_To_Vscode)
    bpy.utils.unregister_class(DebuggerAddonPreferences)

if __name__ == '__main__':
    register()
