import bpy


class ScreenPieMenu(bpy.types.Menu):
    bl_label = 'Screen Pie Menu'
    bl_idname = 'ui.screen_pie_menu'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        for i, scr in enumerate(bpy.data.screens):
            if i >= 7:
                break
            pie.operator(ScreenPieChange.bl_idname,
                         text=scr.name).scr_name = scr.name

class ScreenPieChange(bpy.types.Operator):
    bl_idname = 'pie.screen_pie_menu_change_screen'
    bl_label = 'Change Screen Function for ScreenPieMenu'
    bl_options = {'INTERNAL'}

    scr_name = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.window.screen = bpy.data.screens[self.scr_name]
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
