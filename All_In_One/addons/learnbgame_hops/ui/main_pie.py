import bpy
from .. icons import get_icon_id, icons
from .. utils.addons import addon_exists
from .. preferences import pie_F6_enabled, pie_bool_options_enabled
from .. utils.objects import get_current_selected_status


class HOPS_PT_MainPie(bpy.types.Menu):
    bl_idname = "hops_main_pie"
    bl_label = "Hard Ops 0097"

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
        col.menu("hops.render_set_submenu", text="RenderSets")  # , icon_value=get_icon_id("Gui"))
        col.menu("hops.vieport_submenu", text="ViewPort")  # , icon_value=get_icon_id("Viewport"))
        # col.menu("hops.settings_submenu", text="Settings")  # , icon_value=get_icon_id("Gui"))

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
        pie.separator()
        pie.operator("hops.copy_merge", text="Copy Merge")  # , icon_value=get_icon_id("Merge"))
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.remove_merge", text="coming soon")  # , icon_value=get_icon_id("Merge"))
        pie.operator("hops.mirror_gizmo", text="Mirror")  # , icon_value=get_icon_id("AdjustBevel"))

    def drawpie_only_with_active_object(self, layout, object):
        pie = self.layout.menu_pie()
        object = bpy.context.active_object
        if object.hops.is_pending_boolean:
            pie.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("ReBool"))
        else:
            pie.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))
        pie.separator()
        pie.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
        pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        pie.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("AdjustBevel"))

    def draw_boolshape_menu(self, layout):
        pie = self.layout.menu_pie()

        pie.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("ReBool"))
        pie.separator()
        pie.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("CSharpen"))
        pie.separator()
        pie.separator()
        self.drawpie_options(layout)
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

            pie.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("ReBool"))
            pie.separator()
            pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            pie.separator()
            pie.separator()
            self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            pie.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("AdjustBevel"))
        else:
            pie.operator("hops.step", text="Step", icon_value=get_icon_id("Cstep"))
            pie.separator()
            pie.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            pie.separator()
            pie.separator()
            self.drawpie_options(layout)
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            pie.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("AdjustBevel"))

    def drawpie_with_active_object_and_other_mesh(self, layout, active_object):
        pie = self.layout.menu_pie()

        pie.operator("hops.bool_difference", text="Difference", icon_value=get_icon_id("AdjustBevel"))
        pie.separator()
        pie.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Ssharpen"))
        pie.separator()
        self.drawpie_bool_options(layout)
        self.drawpie_options(layout)

        object = bpy.context.active_object
        if object.hops.status in ("CSHARP", "CSTEP"):
            pie.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        else:
            pie.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        pie.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("AdjustBevel"))

    def drawpie_options(self, layout):
        pie = self.layout.menu_pie()
        split = pie.box().split(align=True)
        col = split.column(align=True)
        col.menu("hops.object_operators_submenu", text="Operations")
        col.menu("hops.object_tools_submenu", text="MeshTools")
        col.menu("hops.settings_submenu", text="Settings")

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
        pie = self.layout.menu_pie()
        pie.separator()
        pie.separator()
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
        pie.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("AdjustBevel"))

    def draw_sculpt_menu(self, layout, context):
        pie = self.layout.menu_pie()
        pie.prop(context.tool_settings.sculpt, "use_smooth_shading")

        if context.sculpt_object.use_dynamic_topology_sculpting:
            pie.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
        else:
            pie.operator("sculpt.dynamic_topology_toggle", icon='SCULPT_DYNTOPO', text="Enable Dyntopo")

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

    # Edit Mode
    ############################################################################

    def draw_edit_mode_pie(self, layout, object):
        pie = self.layout.menu_pie()
        # left
        pie.operator("hops.star_connect", text="Star Connect")
        # right
        pie.separator()
        # bot
        pie.operator("hops.set_edit_sharpen", text="Set Sharp")
        # top
        pie.operator("hops.analysis", text="Analysis")
        # top L
        pie.separator()
        # top R
        split = pie.box().split(align=True)
        col = split.column()
        col.menu("hops.mesh_operators_submenu", text="Operations")
        if addon_exists("mira_tools"):
            col.menu("hops.mira_submenu", text="Mira (T)")
        col.menu("hops.reset_axis_submenu", text="Reset Axis")
        col.menu("hops.insert_objects_submenu", text="Insert")
        # bot L
        pie.operator("hops.bevel_weight", text="(B)Weight")
        # bot R
        pie.operator("hops.mirror_gizmo", text="Mirror")
