import bpy

import os

import blendmotion

class BlendMotionPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    log_file = bpy.props.StringProperty(name='log_file', subtype='FILE_PATH', default=os.path.join(blendmotion.__path__[0], "blendmotion.log"))
    log_level = bpy.props.EnumProperty(name='log_level', items=tuple((l,) * 3 for l in ('NONE', 'ERROR', 'WARNING', 'INFO', 'DEBUG')), default='ERROR')

    def draw(self, context):
        box = self.layout.box()
        box.label(text='Logging')
        box.prop(self, 'log_file', text='Log File Path')
        box.prop(self, 'log_level', text='Log Level')

def register():
    bpy.utils.register_class(BlendMotionPrefs)

def unregister():
    bpy.utils.unregister_class(BlendMotionPrefs)
