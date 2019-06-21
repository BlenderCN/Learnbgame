import bpy
from .. icons import get_icon_id
from .. utils.addons import addon_exists
from .. preferences import pro_mode_enabled
from .. utils.objects import get_current_selected_status


class HOPS_MT_MainMenu(bpy.types.Menu):
    bl_idname = "HOPS_MT_MainMenu"
    bl_label = "Hard Ops 0098"

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        wm = context.window_manager

        if active_object is None:
            self.draw_without_active_object(layout)
            layout.separator()
            layout.menu("HOPS_MT_RenderSetSubmenu", text="RenderSets", icon_value=get_icon_id("StatusOveride"))
            layout.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("WireMode"))

        elif active_object.mode == "OBJECT":
            if active_object.hops.status == "BOOLSHAPE":
                self.draw_boolshape_menu(layout)
                #self.draw_always(layout)
            elif active_object.hops.status == "BOOLSHAPE2":
                self.draw_boolshape_menu(layout)
                #self.draw_always(layout)
            else:
                if active_object.type == "LATTICE":
                    self.draw_lattice_menu(layout)
                    self.draw_always(layout)
                elif active_object.type == "CURVE":
                    self.draw_curve_menu(layout)
                    self.draw_always(layout)
                elif active_object.type == "LIGHT":
                    self.draw_lamp_menu(layout)
                    self.draw_always(layout)
                elif active_object.type == "CAMERA":
                    self.draw_camera_menu(context, layout)
                    self.draw_always(layout)
                elif active_object.type == "EMPTY":
                    col = layout.column()
                    self.draw_only_with_active_object_is_empty(layout)
                    self.draw_always(layout)
                else:
                    self.draw_object_mode_menu(layout)
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_menu(layout, active_object)
        elif active_object.mode == "POSE":
            self.draw_rigging_menu(layout)
        elif active_object.mode == "SCULPT":
            self.draw_sculpt_menu(layout)
            layout.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("Viewport"))
        elif active_object.mode == "PAINT_GPENCIL":
            self.draw_pencil_menu(layout)

        if bpy.context.object.type == 'MESH':
            if addon_exists("kitops"):
                if len(bpy.context.selected_objects):
                    if hasattr(wm, 'kitops'):
                        layout.separator()
                        layout.operator("view3d.insertpopup", text = "KitOps", icon_value=get_icon_id("Insert"))
        layout.separator()
        layout.menu("SCREEN_MT_user_menu", text="Quick Favorites", icon_value=get_icon_id("Tris"))
        # self.draw_always(layout)

    # Without Selection
    ############################################################################

    def draw_without_active_object(self, layout):
        layout.menu('HOPS_MT_ViewportSubmenu', text="ViewPort", icon_value=get_icon_id("WireMode"))
#        wm = bpy.context.window_manager
#        layout.template_icon_view(wm, "Hard_Ops_previews")
#        layout.template_icon_view(wm, "sup_preview")
#        if addon_exists("MESHmachine"):
#            # layout.template_icon_view(wm, "pluglib_")
#            layout.separator()
#            layout.menu("machin3.mesh_machine_plug_libraries", text="Machin3")
#            layout.menu("machin3.mesh_machine_plug_utils_menu", text="Plug Utils")

    # Always
    ############################################################################

    def draw_always(self, layout):
        layout.separator()
        layout.menu("HOPS_MT_RenderSetSubmenu", text="RenderSets", icon_value=get_icon_id("StatusOveride"))
        layout.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("WireMode"))

    # Object Mode
    ############################################################################

    def draw_object_mode_menu(self, layout):
        active_object, other_objects, other_object = get_current_selected_status()
        only_meshes_selected = all(object.type == "MESH" for object in bpy.context.selected_objects)

        object = bpy.context.active_object

        if len(bpy.context.selected_objects) == 1:
            if object.hops.status in ("CSHARP", "CSTEP"):
                if active_object is not None and other_object is None and only_meshes_selected:
                        self.draw_only_with_active_object_is_csharpen(layout, active_object)
            if object.hops.status == "UNDEFINED":
                if active_object is not None and other_object is None and only_meshes_selected:
                    if active_object.name.startswith("AP_"):
                        self.draw_only_with_AP_as_active_object(layout, active_object)
                    #Thin Objects Addition for 2d Bevel
                    elif active_object.dimensions[2] == 0 or active_object.dimensions[1] == 0 or active_object.dimensions[0] == 0:
                        self.draw_thin_object(layout)
                    else:
                        self.draw_only_with_active_object(layout, active_object)
            self.draw_options(layout)

        elif len(bpy.context.selected_objects) >= 2:
            self.draw_with_active_object_and_other_mesh(layout, active_object, other_object)
            self.draw_options(layout)

        else:
            self.draw_without_active_object(layout)
            layout.separator()
            layout.menu("HOPS_MT_SettingsSubmenu", text="Settings", icon_value=get_icon_id("StatusOveride"))

    def draw_only_with_AP_as_active_object(self, layout, object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.copy_merge", text="Copy Merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text="coming soon", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text="Remove Merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Array"))

    def draw_only_with_active_object(self, layout, object):
        object = bpy.context.active_object

        # DM Insertion
        if "decal" in object.name or "info" in object.name or "panel" in object.name:
            self.draw_decalA_menu(layout)
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

        else:
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            if object.hops.is_pending_boolean:
                layout.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("ReBool"))
                #bpy.ops.hops.adjust_bevel()
                #layout.menu("HOPS_MT_ModSubmenu", text="Add Modifier", icon_value=get_icon_id("Diagonal"))
            else:
                #layout.menu("HOPS_MT_ModSubmenu", text="Add Modifier", icon_value=get_icon_id("Diagonal"))
                layout.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Array"))

    def draw_only_with_active_object_is_csharpen(self, layout, object):
        object = bpy.context.active_object
        layout.operator_context = "INVOKE_DEFAULT"
        if object.hops.is_pending_boolean:
            layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
            layout.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            layout.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))
        else:
            layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            layout.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
            layout.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Array"))

    def draw_with_active_object_and_other_mesh(self, layout, active_object, other_object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Csplit"))
        object = bpy.context.active_object
        if object.hops.status in ("CSHARP", "CSTEP"):
            layout.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        else:
            layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.bool_difference", text="Difference", icon_value=get_icon_id("Booleans"))
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Array"))
        layout.separator()
        layout.menu("HOPS_MT_BoolSumbenu", text="Booleans", icon="MOD_BOOLEAN")
        # layout.separator()

    def draw_with_active_object_and_other_mesh_for_merge(self, layout, active_object, other_object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge", text="(C) merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.simple_parent_merge", text="(S) merge", icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text="Remove Merge", icon_value=get_icon_id("Merge"))

    def draw_with_active_object_and_other_mesh_for_softmerge(self, layout, active_object, other_object):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge_soft", text="(C) merge(soft)", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Csplit"))
        layout.operator("hops.remove_merge", text="Remove Merge", icon_value=get_icon_id("CSharpen"))

    def draw_options(self, layout):
        layout.separator()
        layout.menu("HOPS_MT_ObjectsOperatorsSubmenu", text="Operations", icon_value=get_icon_id("Diagonal"))
        layout.separator()
        layout.menu("HOPS_MT_ModSubmenu", text="Add Modifier", icon_value=get_icon_id("Diagonal"))
        layout.separator()
        layout.menu("HOPS_MT_ObjectToolsSubmenu", text="MeshTools", icon_value=get_icon_id("WireMode"))
        layout.menu("HOPS_MT_SettingsSubmenu", text="Settings", icon_value=get_icon_id("StatusOveride"))

    # Edit Mode
    ############################################################################

    def draw_edit_mode_menu(self, layout, object):
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.set_edit_sharpen", text="Set SSharp", icon_value=get_icon_id("MakeSharpE"))
        layout.operator("hops.bevel_weight", text="Bweight", icon_value=get_icon_id("AdjustBevel"))
        layout.menu("HOPS_MT_ModSubmenu", text = 'Add Modifier',  icon_value=get_icon_id("Tris"))
        #layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Array"))
        layout.separator()
        if pro_mode_enabled():
            layout.operator("clean1.objects", text="Demote", icon_value=get_icon_id("Demote")).clearsharps = False
            layout.menu("HOPS_MT_BoolSumbenu", text="Booleans", icon_value=get_icon_id("Booleans"))
        else:
            layout.operator("clean1.objects", text="Clean SSharps", icon_value=get_icon_id("CleansharpsE")).clearsharps = False
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.separator()
        layout.menu("HOPS_MT_MeshOperatorsSubmenu", text="Operations", icon_value=get_icon_id("StatusOveride"))

        if pro_mode_enabled():
            if addon_exists("MESHmachine"):
                layout.separator()
                layout.menu("machin3.mesh_machine_menu", text="MESHmachine", icon_value=get_icon_id("Machine"))
                layout.separator()
#            if addon_exists("mira_tools"):
#                layout.menu("HOPS_MT_MiraSubmenu", text="Mira (T)", icon="PLUGIN")

        layout.operator("hops.reset_axis_modal", text="Flatten", icon_value=get_icon_id("Xslap"))
        if addon_exists('bezier_mesh_shaper'):
            layout.menu("HOPS_MT_edgeWizardSubmenu", text="Plugin", icon="PLUGIN")
        layout.separator()
        # layout.operator("ehalfslap.object", text="(X+) Symmetrize", icon_value = get_icon_id("Xslap"))

        """if object.data.show_edge_crease == False:
            layout.operator("object.showoverlays", text="Show Overlays", icon = "RESTRICT_VIEW_ON")
        else :
            layout.operator("object.hide_overlays", text="Hide Overlays", icon = "RESTRICT_VIEW_OFF")"""

        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("HOPS_MT_MaterialListMenu", text="Material", icon_value=get_icon_id("StatusOveride"))

        #layout.separator()
        #layout.menu("HOPS_MT_InsertsObjectsSubmenu", text="Insert", icon_value=get_icon_id("Noicon"))

    # Sculpt Menu
    ############################################################################
    def draw_sculpt_menu(self, layout):
        wm = bpy.context.window_manager
        layout.menu("HOPS_MT_SculptSubmenu", text="Sculpt")
        layout.template_icon_view(wm, "brush_previews", show_labels=True)
        layout.separator()
        layout.operator("sculpt.toggle_brush", text="Toggle Brush")
        layout.separator()
        layout.operator("sculpt.decimate_mesh", text="Decimate Mesh")

    # Lamp Menu
    ############################################################################

    def draw_lamp_menu(self, layout):
        c = bpy.context.scene
        if c.render.engine == 'BLENDER_EEVEE':
            layout.prop(bpy.context.object.data, "energy", text="Energy")
            layout.prop(bpy.context.object.data, "use_contact_shadow", text="Contact Shadow")
            layout.separator()
            layout.prop(bpy.context.scene.eevee,"use_soft_shadows", text = "SCN_Soft Shadows")
            layout.prop(bpy.context.scene.eevee, "use_gtao", text = "SCN_Global AO")
        else:
            layout.label(text="No Lamp Options Yet")

    # Camera Menu
    ############################################################################

    def draw_camera_menu(self, context, layout):
        # cam = bpy.context.space_data
        obj = bpy.context.object

        obj = bpy.context.object.data
        layout.prop(obj, "lens", text="Lens")
        layout.prop(obj, "passepartout_alpha", text="PP")
        layout.prop(obj, "dof_object", text="")

        obj = bpy.context.object.data.cycles
        layout.prop(obj, "aperture_size", text="DOF Size")

        layout.separator()

        layout.prop(context.object.data, "sensor_fit", text="")
        if context.object.data.sensor_fit == 'AUTO':
            layout.prop(context.object.data, "sensor_width")
        else:
            layout.prop(context.object.data, "sensor_width")
            layout.prop(context.object.data, "sensor_height")

        layout.separator()
        layout.operator("hops.set_camera", text="Set Active Cam", icon_value=get_icon_id("StarConnect"))

        layout.separator()
        layout.menu("HOPS_MT_SettingsSubmenu", text="Settings", icon_value=get_icon_id("StatusOveride"))

    # Lattice Mode
    ############################################################################

    def draw_lattice_menu(self, layout):
        layout.prop(bpy.context.object.data, "points_u", text="X")
        layout.prop(bpy.context.object.data, "points_v", text="Y")
        layout.prop(bpy.context.object.data, "points_w", text="Z")
        layout.prop(bpy.context.object.data, "use_outside")
        layout.operator("hops.simplify_lattice", text="Simplify", icon_value=get_icon_id("StarConnect"))

    # BoolShape Menu
    ############################################################################

    def draw_boolshape_menu(self, layout):
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))
        layout.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))
        layout.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("Qarray"))
        layout.separator()
        layout.operator("hops.boolshape_status_swap", text="Red", icon_value=get_icon_id("Red")).red = True
        layout.operator("hops.boolshape_status_swap", text="Green", icon_value=get_icon_id("Green")).red = False
        layout.operator("clean.sharps", text="Clean", icon_value=get_icon_id("CleansharpsE"))
        layout.separator()
        layout.menu("HOPS_MT_ObjectsOperatorsSubmenu", text="Operations", icon_value=get_icon_id("StatusOveride"))
        layout.menu("HOPS_MT_ObjectToolsSubmenu", text="MeshTools", icon_value=get_icon_id("WireMode"))
        layout.menu("HOPS_MT_SettingsSubmenu", text="Settings", icon_value=get_icon_id("StatusOveride"))

    def draw_curve_menu(self, layout):
        if len(bpy.context.selected_objects) == 1:
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator("hops.adjust_curve", text="Adjust Curve", icon_value=get_icon_id("Curve"))
        else:
            layout.operator("hops.curve_bevel", text="Curve Taper", icon_value=get_icon_id("Curve"))

    def draw_rigging_menu(self, layout):
        layout.operator("object.create_driver_constraint", text="Driver Constraint")

    # DECAL MENU
    ############################################################################

    def draw_decalA_menu(self, layout):
        # if "decal" not in activemat.name and "paneling" not in activemat.name and "info" not in activemat.name:
        if "decal" or "info" or "panel" in bpy.context.active_object.name:
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator("machin3.modal_decal_height", text="Adjust Decal Height")
            layout.operator("machin3.decal_source", text="Extract Source")
            # layout.separator()

    # Empty Menu
    ############################################################################

    def draw_only_with_active_object_is_empty(self, layout):

        obj = bpy.context.object
        wm = bpy.context.window_manager

        layout.template_icon_view(wm, "img_selection_previews")

        button = layout.operator("hops.set_empty_image", text="Set Image")
        # button.img = wm.img_selection_previews

        layout.operator("hops.center_empty", text="Center Image")
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.empty_transparency_modal", text="Change Transparency")
        layout.operator("hops.empty_position_modal", text="Change Offset")

    # Thin Object Test
    ############################################################################

    def draw_thin_object(self, layout):

        obj = bpy.context.object

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator('hops.2d_bevel', text = '2d Bevel', icon_value=get_icon_id("AdjustBevel"))
        layout.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))
        layout.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("Qarray"))

    # Grease Pencil Tiem
    ############################################################################

    def draw_pencil_menu(self, layout):

        obj = bpy.context.object

        layout.operator("hops.copy_move", text="Copy / Move", icon_value=get_icon_id("dots"))
        layout.operator("hops.surfaceoffset", text="Surface OffSet", icon_value=get_icon_id("dots"))
        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
