import bpy
from .addon import prefs
from .ui_utils import operator


class SUV_PT_tools(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_label = "Smart UV"
    bl_category = "Tools"

    def header(self, text, icon, spacer=True):
        if spacer:
            self.layout.separator()
        row = self.layout.row(True)
        row.alignment = 'CENTER'
        row.label(text, icon=icon)

    def draw_align(self):
        self.header("ALIGN TOOLS", 'MOD_LATTICE', False)
        pr = prefs()

        # row.prop(pr, "use_uv_bounds", "", icon='CURVE_NCIRCLE', toggle=True)

        row = self.layout.row()

        col = row.column(True)
        sub = col.row(True)
        sub.scale_x = 1.5
        sub.scale_y = 1.5
        sub.alignment = 'CENTER'
        operator(
            sub, "suv.island_align", "", 'TRIA_LEFT',
            mode='TL', use_uv_bounds=pr.use_uv_bounds)
        operator(
            sub, "suv.island_align", "", 'TRIA_UP',
            mode='T', use_uv_bounds=pr.use_uv_bounds)
        operator(
            sub, "suv.island_align", "", 'TRIA_RIGHT',
            mode='TR', use_uv_bounds=pr.use_uv_bounds)

        sub = col.row(True)
        sub.scale_x = 1.5
        sub.scale_y = 1.5
        sub.alignment = 'CENTER'
        operator(
            sub, "suv.island_align", "", 'TRIA_LEFT',
            mode='L', use_uv_bounds=pr.use_uv_bounds)
        # operator(
        #     sub, "suv.island_align", "", 'MESH_PLANE',
        #     mode='C', use_uv_bounds=pr.use_uv_bounds)
        sub.prop(pr, "use_uv_bounds", "", icon='MESH_GRID', toggle=True)
        operator(
            sub, "suv.island_align", "", 'TRIA_RIGHT',
            mode='R', use_uv_bounds=pr.use_uv_bounds)

        sub = col.row(True)
        sub.scale_x = 1.5
        sub.scale_y = 1.5
        sub.alignment = 'CENTER'
        operator(
            sub, "suv.island_align", "", 'TRIA_LEFT',
            mode='BL', use_uv_bounds=pr.use_uv_bounds)
        operator(
            sub, "suv.island_align", "", 'TRIA_DOWN',
            mode='B', use_uv_bounds=pr.use_uv_bounds)
        operator(
            sub, "suv.island_align", "", 'TRIA_RIGHT',
            mode='BR', use_uv_bounds=pr.use_uv_bounds)

        # col = row.column(True)
        # sub = col.row(True)
        # sub.scale_x = 1.5
        # sub.scale_y = 1.5
        # sub.prop(pr, "use_uv_bounds", "", icon='CURVE_NCIRCLE', toggle=True)

        col = self.layout
        row = col.row()
        operator(
            row, "suv.island_distribute", "Gap", 'ARROW_LEFTRIGHT',
            mode='HORIZONTAL')
        operator(
            row, "suv.island_distribute", "Gap", 'FULLSCREEN_ENTER',
            mode='VERTICAL')
        operator(col, "wm.pme_none", "Copy Rotation", 'FILE_REFRESH')
        operator(col, "uv.align", "Straighten", 'IPO_LINEAR', axis='ALIGN_S')
        operator(
            col, "suv.uv_align_by_edge",
            "Align Island by Edge", 'STYLUS_PRESSURE')


    def draw_standard(self):
        self.header("STANDARD TOOLS", 'MOD_DISPLACE')
        col = self.layout
        row = col.row()
        operator(row, "uv.mark_seam", "Mark Seam", 'IPO_CIRC', clear=False)
        operator(row, "uv.mark_seam", "Clear Seam", 'X', clear=True)
        operator(
            col, "uv.seams_from_islands", "Seams from Islands", 'MOD_ARRAY')
        operator(
            col, "suv.exec", "Rip", 'UV_ISLANDSEL',
            cmd="O.uv.select_split(); O.transform.translate('INVOKE_DEFAULT')")
        operator(col, "suv.uv_reunwrap", "Re-Unwrap", 'OUTLINER_OB_LATTICE')
        row = col.row()
        operator(row, "uv.pin", "Pin", 'REC', clear=False)
        operator(row, "uv.pin", "Unpin", 'RADIOBUT_OFF', clear=True)


    def draw_visual(self):
        self.header("VISUAL TOOLS", 'TEXTURE_SHADED')
        col = self.layout
        col.prop(bpy.context.space_data.uv_editor, "show_faces")
        col.prop(bpy.context.space_data.uv_editor, "show_stretch")
        col.prop(
            bpy.context.space_data.uv_editor, "draw_stretch_type", expand=True)
        operator(col, "wm.pme_none", "Toggle UV", 'MOD_TRIANGULATE')
        operator(
            col, "screen.screen_full_area", "Maximize Area", 'SCREEN_BACK')

    def draw_select(self):
        self.header("SELECT TOOLS", 'HAND')
        col = self.layout
        row = col.row()
        operator(row, "uv.circle_select", "Circle", 'BORDER_LASSO')
        operator(
            row, "uv.select_border", "Border", 'BORDER_RECT', pinned=False)
        operator(
            col, "uv.select_all", "Invert", 'IMAGE_ALPHA', action='INVERT')
        operator(col, "uv.select_pinned", "Pinned", 'REC')

    def draw(self, context):
        self.draw_align()
        self.draw_standard()
        self.draw_visual()
        self.draw_select()


