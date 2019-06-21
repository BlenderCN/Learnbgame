import bpy
from bpy.props import StringProperty
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from ... utils.registration import get_prefs


class CallDecalPie(bpy.types.Operator):
    bl_idname = "machin3.call_decal_pie"
    bl_label = "MACHIN3: Call DECALmachine Pie"
    bl_options = {'REGISTER', 'UNDO'}

    idname: StringProperty()

    def invoke(self, context, event):
        # reset decalmode, if it's NONE (the AddDecalToLibrary tool, if aborted, leaves it in this state)
        if get_prefs().decalmode == "NONE":
            get_prefs().decalmode = "INSERT"
            get_prefs().decalremovemode = False

        current_tool = ToolSelectPanelHelper._tool_get_active(context, 'VIEW_3D', None)[0][0]

        if current_tool == 'BoxCutter':
            return {'PASS_THROUGH'}

        else:
            context.window_manager.decal_mousepos = (event.mouse_region_x, event.mouse_region_y)

            bpy.ops.wm.call_menu_pie(name='MACHIN3_MT_%s' % (self.idname))
            return {'FINISHED'}
