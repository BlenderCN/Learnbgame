# -*- coding: utf-8 -*-

bl_info = {
    "name": "Zen Mode for working peacefully",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "Operator Search Menu (type 'Zen')",
    "description": "(Un)Clear the area headers for the current screen",
    "warning": "",
    "category": "Learnbgame",
}

"""(Un)Clear the area headers for the current screen"""


import bpy


def screen_areas_zen(context, settings):
    for area in context.screen.areas:
        area.show_menus = settings['show_menus'] and not settings['enable']
        cb = area.header_text_set
        cb('') if settings['enable'] else cb()
        area.tag_redraw()


class ScreenModeZenOperator(bpy.types.Operator):
    """Zennify the Screen areas display"""
    bl_idname = "screen.mode_zen"
    bl_label = "Screen Mode Zen"
    bl_options = {'REGISTER', 'UNDO'}

    enable = bpy.props.BoolProperty(name='Enable', description="Enable/Disable Zen Mode", default=True)
    show_menus = bpy.props.BoolProperty(name='Show Menus?', description="Should the menus be shown", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.prop(self, 'enable')
        column.prop(self, 'show_menus')

    def invoke(self, context, event):
        screen_areas_zen(context, self.as_keywords())
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        screen_areas_zen(context, self.as_keywords())
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ScreenModeZenOperator)


def unregister():
    bpy.utils.unregister_class(ScreenModeZenOperator)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.screen.mode_zen(enable=False)
    #bpy.ops.screen.mode_zen('INVOKE_DEFAULT')
