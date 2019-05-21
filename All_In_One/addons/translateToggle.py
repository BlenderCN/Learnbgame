bl_info = {
    "name": "Interface Translation Toggle",
    "author": "stan",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "",
    "description": "Toggle interface's translation",
    "warning": "",
    "wiki_url": "stan.stz@gmail.com",
    "category": "Learnbgame"
}

import bpy

bpy.context.user_preferences.system.use_international_fonts = True

class Translation(bpy.types.Operator):
    """Toggle UI translation"""
    bl_idname = "screen.translation"
    bl_label = "Interface translation"

    def execute(self, context):
        bpy.context.user_preferences.system.use_translate_interface = not bpy.context.user_preferences.system.use_translate_interface
        bpy.context.user_preferences.system.use_translate_tooltips = not bpy.context.user_preferences.system.use_translate_tooltips
        bpy.context.user_preferences.system.use_translate_new_dataname = not bpy.context.user_preferences.system.use_translate_new_dataname
        return {'FINISHED'}

def addon_button(self, context):
     self.layout.operator(
          "screen.translation",
          text="Translation",)

def register():
    bpy.utils.register_class(Translation)
    bpy.types.INFO_HT_header.append(addon_button)

def unregister():
    bpy.utils.unregister_class(Translation)
    bpy.types.INFO_HT_header.remove(addon_button)

if __name__ == "__main__":
    register()
