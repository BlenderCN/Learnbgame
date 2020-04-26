import bpy
from .. icons import get_icon_id, icons
from .. utils.addons import addon_exists
from .. preferences import pie_F6_enabled, pie_bool_options_enabled, get_preferences
from .. utils.objects import get_current_selected_status


class HOPS_MT_MainPie(bpy.types.Menu):
    bl_idname = "HOPS_MT_MainPie"
    bl_label = "Hard Ops 0098"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object

        if active_object is None:
            self.draw_without_active_object_pie(layout)
        elif active_object.mode == "OBJECT":
            if active_object.hops.status == "BOOLSHAPE":
                self.draw_boolshape_menu(layout)
            elif active_object.hops.status == "BOOLSHAPE2":
                self.draw_boolshape_menu(layout)
            else:
                if active_object.type == "LATTICE":
                    self.draw_lattice_menu(layout)
                elif active_object.type == "CURVE":
                    self.draw_curve_menu(layout)
                elif active_object.type == "LIGHT":
                    self.draw_lamp_menu(layout)
                elif active_object.type == "CAMERA":
                    self.draw_camera_menu(layout, context)
                elif active_object.type == "EMPTY":
                    self.draw_empty_menu(layout, context)
                else:
                    self.draw_object_mode_pie(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_pie(layout, active_object)
        elif active_object.mode == 'POSE':
            self.draw_rigging_menu(layout)
        elif active_object.mode == "SCULPT":
            self.draw_sculpt_menu(layout, context)
        elif active_object.mode == "PAINT_GPENCIL":
            self.draw_pencil_menu(layout, context)


    # Without Selection
    ############################################################################

    def draw_without_active_object_pie(self, layout):
        wm = bpy.context.window_manager
        pie = self.layout.menu_pie()
        pie.separator()

        # top
        pie.separator()
        pie.separator()

        box = pie.box()
        col = box.column()
        col.menu("HOPS_MT_RenderSetSubmenu", text="RenderSets")  # , icon_value=get_icon_id("Gui"))
        col.menu("HOPS_MT_ViewportSubmenu", text="ViewPort")  # , icon_value=get_icon_id("Viewport"))
        # col.menu("HOPS_MT_SettingsSubmenu", text="Settings")  # , icon_value=get_icon_id("Gui"))

        pie.separator()
        pie.separator()

    # Always
    ############################################################################

    # Object Mode
    ############################################################################

    def draw_object_mode_pie(self, layout):
        active_object, other_objects, other_object = get_current_selected_status()
        only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)
        object = bpy.context.active_object

        if len(bpy.context.selected_objects) == 1:

            if object.hops.status in ("CSHARP", "CSTEP"):
                if active_object is not None and other_object is None and only_meshes_selected:
                        self.drawpie_only_with_active_object_is_csharpen(layout, active_object)

            if object.hops.status == "UNDEFINED":
                if active_object is not None and other_object is None and only_meshes_selected:
                    if active_object.name.startswith("AP_"):
                        self.drawpie_only_with_AP_as_active_object(layout, active_object)
                    else:
                        self.drawpie_only_with_active_object(layout, active_object)

        elif len(bpy.context.selected_objects) >= 2:
            self.drawpie_with_active_object_and_other_mesh(layout, active_object)

        else:
            self.draw_without_active_object_pie(layout)

    def drawpie_only_with_AP_as_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        pie.operator("hops.remove_merge", text="Remove Merge")  # , icon_value=get_icon_id("Merge"))
        self.mod_options(layout)
        pie.operator("hops.copy_merge", text="Copy Merge")  # , icon_value=get_icon_id("Merge"))
        self.drawpie_options(layout)
        pie.separator()
        pie.separator()
        pie.operator("hops.remove_merge", text="coming soon", icon_value=get_icon_id("Merge"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def drawpie_only_with_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:
            pie.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("ReBool"))
        else:
            pie.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))
        self.mod_options(layout)
        pie.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
        self.drawpie_options(layout)
        pie.separator()
        pie.separator()
        pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def draw_boolshape_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("ReBool"))
        self.mod_options(layout)
        pie.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("Qarray"))
        self.drawpie_options(layout)
        pie.separator()
        pie.separator()
        pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        col = pie.column(align=True)
        colrow = col.row(align=True)
        colrow.operator("hops.boolshape_status_swap", text="Red").red = True
        colrow.operator("hops.boolshape_status_swap", text="Green").red = False
        colrow.operator("clean.sharps", text="Clean")

    def drawpie_only_with_active_object_is_csharpen(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:

            pie.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))
            self.mod_options(layout)
            pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            self.drawpie_options(layout)
            # pie.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Qarray"))
            pie.separator()
            pie.separator()
            # self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")
        else:
            pie.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))
            self.mod_options(layout)
            pie.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            self.drawpie_options(layout)
            # pie.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Qarray"))
            pie.separator()
            pie.separator()
            # self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def drawpie_with_active_object_and_other_mesh(self, layout, active_object):
        pie = self.layout.menu_pie()

        pie.operator("hops.bool_difference", text="Difference", icon_value=get_icon_id("AdjustBevel"))
        self.mod_options(layout)
        pie.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Ssharpen"))
        self.drawpie_options(layout)
        pie.separator()
        pie.separator()

        object = bpy.context.active_object
        if object.hops.status in ("CSHARP", "CSTEP"):
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        else:
            pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    def mod_edit_options(self, layout):
        pie = self.layout.menu_pie()
        maincol = pie.column()
        split = maincol.box().row(align=True)
        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        if get_preferences().pie_mod_expand:

            col.operator("hops.adjust_bevel", text="", icon="MOD_BEVEL")
            col.operator("hops.mod_lattice", text="", icon="MOD_LATTICE")
            col.operator("hops.mod_hook", text="", icon="HOOK")
            col.operator("hops.mod_mask", text="", icon="MOD_MASK")

            split.separator()
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

        col.operator("hops.edit_bool_difference", text="", icon_value=get_icon_id("red"))
        col.operator("hops.edit_bool_union", text="", icon_value=get_icon_id("green"))
        col.operator("hops.edit_bool_intersect", text="", icon_value=get_icon_id("yellow"))
        if get_preferences().pie_mod_expand:
            col.prop(get_preferences(), "pie_mod_expand", text="", icon="TRIA_LEFT")
        else:
            col.prop(get_preferences(), "pie_mod_expand", text="", icon="TRIA_RIGHT")

        maincol.separator()
        maincol.separator()
        maincol.separator()

    def mod_options(self, layout):
        pie = self.layout.menu_pie()
        maincol = pie.column()
        split = maincol.box().row(align=True)
        row = split.row(align=True)
        col = row.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3

        if get_preferences().pie_mod_expand:

            col.operator("hops.adjust_tthick", text="", icon="MOD_SOLIDIFY")
            col.operator("hops.mod_screw", text="", icon="MOD_SCREW")
            col.operator("hops.mod_simple_deform", text="", icon="MOD_SIMPLEDEFORM")
            col.operator("hops.mod_shrinkwrap", text="", icon="MOD_SHRINKWRAP")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.array_gizmo", text="", icon="MOD_ARRAY")
            col.operator("hops.mod_triangulate", text="", icon="MOD_TRIANGULATE")
            col.operator("hops.mod_wireframe", text="", icon="MOD_WIREFRAME")
            col.operator("hops.mod_cast", text="", icon="MOD_CAST")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.mod_lattice", text="", icon="MOD_LATTICE")
            col.operator("hops.mod_weighted_normal", text="", icon="MOD_NORMALEDIT")
            col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
            col.operator("hops.mod_decimate", text="", icon="MOD_DECIM")
            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

            col.operator("hops.adjust_bevel", text="", icon="MOD_BEVEL")
            col.operator("hops.mod_subdivision", text="", icon="MOD_SUBSURF")
            # col.operator("hops.mod_displace", text="", icon="MOD_DISPLACE")
            col.operator("hops.mod_skin", text="", icon="MOD_SKIN")
            col.operator("hops.mod_apply", text="", icon="REC")
            split.separator()

            row = split.row(align=True)
            col = row.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.3

        col.operator("hops.bool_difference", text="", icon_value=get_icon_id("red"))
        col.operator("hops.bool_union", text="", icon_value=get_icon_id("green"))
        col.operator("hops.bool_intersect", text="", icon_value=get_icon_id("yellow"))
        if get_preferences().pie_mod_expand:
            col.prop(get_preferences(), "pie_mod_expand", text="", icon="TRIA_LEFT")
        else:
            col.prop(get_preferences(), "pie_mod_expand", text="", icon="TRIA_RIGHT")

        maincol.separator()
        maincol.separator()
        maincol.separator()

    def drawpie_options(self, layout):
        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        row = col.row(align=True)

        # col.popover(panel='HOPS_MT_ObjectsOperatorsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='HOPS_MT_ObjectToolsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='HOPS_MT_SettingsSubmenu', text='', icon="MOD_MIRROR")
        # col.popover(panel='SCREEN_MT_user_menu', text='', icon="MOD_MIRROR")

        if addon_exists("kitops"):
            if hasattr(bpy.context.window_manager, 'kitops'):
                row.operator('view3d.insertpopup', text = '', icon_value=get_icon_id("Insert"))
                row.separator()
        row.menu("HOPS_MT_ObjectsOperatorsSubmenu", text="", icon="SNAP_FACE")
        row.separator()
        row.menu("HOPS_MT_ObjectToolsSubmenu", text="", icon="OBJECT_DATAMODE")
        row.separator()
        row.menu("HOPS_MT_SettingsSubmenu", text="", icon="PREFERENCES")
        row.separator()
        row.menu("SCREEN_MT_user_menu", text="", icon="WINDOW")

    def drawpie_bool_options(self, layout):
        pie = self.layout.menu_pie()
        if pie_bool_options_enabled():
            row = pie.row()
            row.operator("hops.bool_intersect", text="Intersection")
            row.operator("hops.bool_union", text="Union")
            row.operator("hops.bool_difference", text="Difference")
        else:
            pie.separator()

    def draw_f6_option(self, layout):
        pie = self.layout.menu_pie()
        if pie_F6_enabled():
            pie.operator("screen.redo_last", text="F6") # icon='SCRIPTWIN')
        else:
            pie.separator()

    def draw_lattice_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.row().prop(bpy.context.object.data, "points_u", text="X")
        pie.operator("hops.simplify_lattice", text="Simplify")
        pie.row().prop(bpy.context.object.data, "points_v", text="Y")
        pie.separator()
        pie.separator()
        pie.prop(bpy.context.object.data, "use_outside")
        pie.row().prop(bpy.context.object.data, "points_w", text="Z")
        pie.separator()

    def draw_curve_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.operator("hops.curve_bevel", text="Curve bevel")
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.adjust_curve", text="Adjust Curve")
        pie.separator()

    def draw_rigging_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("object.create_driver_constraint", text="Driver Constraint")
        pie.separator()

    def draw_lamp_menu(self, layout):
        pie = self.layout.menu_pie()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.separator()
        pie.label(text="No Lamp Options Yet")
        pie.separator()

    def draw_camera_menu(self, layout, context):
        # cam = context.camera

        pie = self.layout.menu_pie()
        pie.separator()
        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.object.data, "sensor_fit", text="sensor fit")
        if context.object.data.sensor_fit == 'AUTO':
            col.prop(context.object.data, "sensor_width", text="Width")
        else:
            col.prop(context.object.data, "sensor_width", text="Width")
            col.prop(context.object.data, "sensor_height", text="Height")

        pie.separator()

        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.object.data, "lens", text="Lens")
        col.prop(context.object.data, "passepartout_alpha", text="PP")
        col.prop(context.object.data, "dof_object", text="")
        col.prop(context.object.data.cycles, "aperture_size", text="DOF Size")

        pie.separator()
        pie.separator()
        pie.operator("hops.set_camera", text="Set Active Cam")
        pie.separator()

    def draw_empty_menu(self, layout, context):
        pie = self.layout.menu_pie()

        pie.separator()
        pie.operator("hops.set_empty_image", text="Set Image")
        pie.separator()
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.separator()
        pie.operator("hops.mirror_gizmo", text="", icon_value=get_icon_id("AdjustBevel"))

    def draw_sculpt_menu(self, layout, context):
        pie = self.layout.menu_pie()
        pie.prop(context.tool_settings.sculpt, "use_smooth_shading")

        if context.sculpt_object.use_dynamic_topology_sculpting:
            pie.operator("sculpt.dynamic_topology_toggle", text="Disable Dyntopo")
        else:
            pie.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo")

        pie.operator("sculpt.symmetrize")

        split = pie.box().split(align=True)
        col = split.column()
        col.prop(context.tool_settings.sculpt, "detail_refine_method", text="")
        col.prop(context.tool_settings.sculpt, "detail_type_method", text="")
        col.prop(context.tool_settings.sculpt, "symmetrize_direction", text="")
        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            col.prop(context.tool_settings.sculpt, "constant_detail")
            col.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        elif (context.tool_settings.sculpt.detail_type_method == 'BRUSH'):
            col.prop(context.tool_settings.sculpt, "detail_percent")
        else:
            col.prop(context.tool_settings.sculpt, "detail_size")

        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            pie.operator("sculpt.detail_flood_fill")
        else:
            pie.separator()

        pie.operator("hops.shrinkwrap_refresh", text="Shrinkwrap Refresh").sculpt = True
        pie.operator("sculpt.optimize")
        pie.separator()

    def draw_pencil_menu(self, layout, context):
        pie = self.layout.menu_pie()

        pie.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("dots"))
        pie.separator()
        pie.operator("hops.copy_move", text="Copy / Move", icon_value=get_icon_id("dots"))
        self.drawpie_options(layout)
        pie.separator()
        pie.separator()
        pie.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("dots"))
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")

    # Edit Mode
    ############################################################################

    def draw_edit_mode_pie(self, layout, object):
        pie = self.layout.menu_pie()
        # left
        pie.operator("hops.star_connect", text="Star Connect")
        # right
        self.mod_edit_options(layout)
        # bot
        pie.operator("hops.set_edit_sharpen", text="Set Sharp")
        # top

        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.3
        row = col.row(align=True)

        row.menu("HOPS_MT_MeshOperatorsSubmenu", text="", icon="SNAP_FACE")
        row.separator()
        row.operator("hops.reset_axis_modal", text="", icon_value=get_icon_id("Xslap"))
        if bpy.context.object and bpy.context.object.type == 'MESH':
            row.separator()
            row.menu("HOPS_MT_MaterialListMenu", text="", icon_value=get_icon_id("StatusOveride"))
        row.separator()
        row.menu("SCREEN_MT_user_menu", text="", icon="WINDOW")

        # top L
        pie.separator()
        # top R
        pie.separator()
        # pie.operator("hops.analysis", text="Analysis")
        # bot L
        pie.operator("hops.bevel_weight", text="(B)Weight", icon_value=get_icon_id("AdjustBevel"))
        # bot R
        pie.operator("hops.mirror_gizmo", text="", icon="MOD_MIRROR")
