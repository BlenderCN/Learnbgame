bl_info = {
    "name": "Speak English",
    "author": "stan",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "description": "Speak English",
    "category": "Learnbgame"
}

import bpy
import subprocess

def add_string(self, context):
    self.layout.prop(context.scene, "speak_string")

def speakText(self, context):
    path='/usr/bin/espeak'
    subprocess.run([path, '-s120', bpy.context.scene.speak_string])
    return{'FINISHED'}

'''
eval(a.replace('(', '').replace(')','')+'._func')
bpy.context.window_manager.clipboard
'''

def register():
    bpy.types.Scene.speak_string = bpy.props.StringProperty \
      (
        name = "",
        description = "type text here to speak",
        default = "Type text to speak",
        update = speakText
      )
    bpy.types.INFO_HT_header.append(add_string)

def unregister():
    bpy.types.INFO_HT_header.remove(add_string)
    del bpy.types.Scene.speak_string

if __name__ == "__main__":
    register()