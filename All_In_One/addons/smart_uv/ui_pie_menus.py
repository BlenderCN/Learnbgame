import bpy
from .addon import prefs
from .ui_utils import operator


class SUV_MT_small_pie(bpy.types.Menu):
    bl_label = "Small UV Pie"

    def draw(self, context):
        layout = self.layout.menu_pie()
        operator(
            layout, "suv.exec", "Vertex", 'UV_VERTEXSEL',
            cmd="C.scene.tool_settings.uv_select_mode = 'VERTEX'")
        operator(
            layout, "suv.exec", "Edge", 'UV_EDGESEL',
            cmd="C.scene.tool_settings.uv_select_mode = 'EDGE'")
        operator(
            layout, "suv.exec", "Face", 'UV_FACESEL',
            cmd="C.scene.tool_settings.uv_select_mode = 'FACE'")
        operator(
            layout, "suv.exec", "Island", 'UV_ISLANDSEL',
            cmd="C.scene.tool_settings.uv_select_mode = 'ISLAND'")
        operator(
            layout, "uv.align", "Align", 'COLLAPSEMENU', axis='ALIGN_AUTO')

        col = layout.column(True)
        row = col.row()
        row.scale_y = 1.25
        operator(row, "image.view_selected", "Zoom Selected", 'VIEWZOOM')
        col.separator()
        row = col.row()
        row.scale_y = 1.25
        operator(
            row, "suv.exec", "Flip X", 'ARROW_LEFTRIGHT',
            cmd="O.transform.mirror(constraint_axis=(True, False, False))")
        operator(
            row, "suv.exec", "Flip Y", 'FULLSCREEN_ENTER',
            cmd="O.transform.mirror(constraint_axis=(False, True, False))")

        operator(
            layout, "suv.exec", "Rip", 'UV_ISLANDSEL',
            cmd="O.uv.select_split(); O.transform.translate('INVOKE_DEFAULT')")
        operator(layout, "suv.uv_reunwrap", "UV Re-Unwrap", 'MOD_MESHDEFORM')


class SUV_MT_big_pie(bpy.types.Menu):
    bl_label = "Big UV Pie"

    def draw(self, context):
        layout = self.layout.menu_pie()
        operator(
            layout, "uv.average_islands_scale",
            "Average Island Scale", 'MANIPUL')

        p = operator(
            layout, "suv.macro2", "Scale Islands", 'ROTATECOLLECTION')
        p.SUV_OT_exec1.cmd = (
            "pp = C.space_data.pivot_point; "
            "C.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'; "
            "O.transform.resize('INVOKE_DEFAULT')"
            )
        p.SUV_OT_exec2.cmd="C.space_data.pivot_point = pp"

        layout.prop(
            context.scene.tool_settings, "proportional_edit", "")
        # layout.prop_menu_enum(
        #     context.scene.tool_settings, "proportional_edit", "")

        row = layout.row()
        sub = row.row()
        sub.scale_x = 1.5
        sub.scale_y = 1.25
        operator(sub, "screen.redo_last", "", 'SCRIPTWIN')
        sub = row.row()
        sub.scale_y = 1.25
        operator(sub, "ed.undo", "Undo", 'LOOP_BACK')
        operator(sub, "ed.redo", "Redo", 'LOOP_FORWARDS')

        operator(
            layout, "screen.screen_full_area",
            "Toggle Maximize Are", 'SCREEN_BACK')
        operator(layout, "uv.pack_islands", "Pack Islands", 'ROTATE')
        operator(layout, "wm.pme_none", "7", 'NONE')
        operator(layout, "wm.pme_none", "Toggle UV", 'MOD_TRIANGULATE')