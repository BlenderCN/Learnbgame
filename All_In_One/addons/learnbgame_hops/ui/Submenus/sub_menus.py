import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled, mira_handler_enabled


# Material


class HOPS_MT_MaterialListMenu(bpy.types.Menu):
    bl_idname = "hops.material_list_menu"
    bl_label = "Material list"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if len(bpy.data.materials):
            for mat in bpy.data.materials:
                name = mat.name
                try:
                    icon_val = layout.icon(mat)
                except:
                    icon_val = 1
                    print("WARNING [Mat Panel]: Could not get icon value for %s" % name)

                op = col.operator("object.apply_material", text=name, icon_value=icon_val)
                op.mat_to_assign = name
        else:
            layout.label(text="No data materials")


class HOPS_MT_SculptSubmenu(bpy.types.Menu):
    bl_label = 'Sculpt'
    bl_idname = 'hops.sculpt_submenu'

    def draw(self, context):
        layout = self.layout

        # sculpt = context.tool_settings.sculpt
        # settings = self.paint_settings(context)
        # brush = settings.brush

        if context.sculpt_object.use_dynamic_topology_sculpting:
            layout.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
        else:
            layout.operator("sculpt.dynamic_topology_toggle", icon='SCULPT_DYNTOPO', text="Enable Dyntopo")
        layout.separator()

        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.prop(context.tool_settings.sculpt, "constant_detail")
            layout.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        elif (context.tool_settings.sculpt.detail_type_method == 'BRUSH'):
            layout.prop(context.tool_settings.sculpt, "detail_percent")
        else:
            layout.prop(context.tool_settings.sculpt, "detail_size")
        layout.prop(context.tool_settings.sculpt, "detail_refine_method", text="")
        layout.prop(context.tool_settings.sculpt, "detail_type_method", text="")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "use_smooth_shading")
        layout.operator("sculpt.optimize")
        if (context.tool_settings.sculpt.detail_type_method == 'CONSTANT'):
            layout.operator("sculpt.detail_flood_fill")
        layout.separator()
        layout.prop(context.tool_settings.sculpt, "symmetrize_direction", text="")
        layout.operator("sculpt.symmetrize")


class HOPS_MT_MiraSubmenu(bpy.types.Menu):
    bl_label = 'Mira Panel'
    bl_idname = 'hops.mira_submenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout.column_flow(columns=2)

        if mira_handler_enabled():
            layout.operator("mesh.curve_stretch", text="CurveStretch", icon="RNA")
            layout.operator("mesh.curve_guide", text='CurveGuide', icon="RNA")

        else:
            layout.operator("mira.curve_stretch", text="CurveStretch", icon="RNA")
            layout.operator("mira.curve_guide", text="CurveGuide", icon="RNA")
            layout.prop(context.scene.mi_cur_stretch_settings, "points_number", text='')
            layout.prop(context.scene.mi_curguide_settings, "points_number", text='')


class HOPS_MT_BasicObjectOptionsSubmenu(bpy.types.Menu):
    bl_label = 'ObjectOptions'
    bl_idname = 'hops.basic_objects_options_submenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout.column_flow(columns=1)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.2

        obj = bpy.context.object

        layout.prop(obj, "name", text="")
        layout.separator()

        obj = bpy.context.object

        layout.prop(obj, "show_name", text="Show object's name"),


class HOPS_MT_FrameRangeSubmenu(bpy.types.Menu):
    bl_label = 'FrameRange'
    bl_idname = 'hops.frame_range_submenu'

    def draw(self, context):
        layout = self.layout

        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.operator("setframe.end", text="Frame Range", icon_value=get_icon_id("SetFrame"))

        if pro_mode_enabled():
            col.prop(scene, 'frame_start')

            col.prop(scene, 'frame_end')


class HOPS_MT_SelectViewSubmenu(bpy.types.Menu):
    bl_label = 'Selection'
    bl_idname = 'hops.selection_submenu'

    def draw(self, context):
        layout = self.layout

        m_check = context.window_manager.m_check

        if bpy.context.object and bpy.context.object.type == 'MESH':
            if m_check.meshcheck_enabled:
                layout.operator("object.remove_materials", text="Hidde Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))
            else:
                layout.operator("object.add_materials", text="Display Ngons/Tris", icon_value=get_icon_id("ShowNgonsTris"))

            layout.operator("data.facetype_select", text="Ngons Select", icon_value=get_icon_id("Ngons")).face_type = "5"
            layout.operator("data.facetype_select", text="Tris Select", icon_value=get_icon_id("Tris")).face_type = "3"

# Viewport


class HOPS_MT_ViewportSubmenu(bpy.types.Menu):
    bl_label = 'Viewport'
    bl_idname = 'hops.vieport_submenu'

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        c = bpy.context.scene
        
        if c.render.engine == 'BLENDER_EEVEE':
            #layout.operator("ui.reg", text="Normal", icon_value=get_icon_id("NGui"))
            #layout.operator("ui.clean", text="Minimal", icon_value=get_icon_id("QGui"))
            layout.prop(view.overlay, "show_overlays", text = 'Overlays')
            layout.separator()        
            layout.operator("render.setup", text="Eevee HQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Eevee LQ", icon="RESTRICT_RENDER_OFF")
        if c.render.engine == 'CYCLES':
            layout.operator("ui.reg", text="Normal", icon_value=get_icon_id("NGui"))
            layout.operator("ui.clean", text="Minimal", icon_value=get_icon_id("QGui"))
            layout.separator()        
            layout.operator("render.setup", text="Cycles RenderSet1 HQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Cycles RenderSet2 LQ", icon="RESTRICT_RENDER_OFF")
        else:
            pass

        if pro_mode_enabled():
            if addon_exists("Fidget"):
                layout.separator()
                row = layout.row()
                row.operator_context = 'INVOKE_DEFAULT'
                row.operator("fidget.viewport_buttons", text="Fidget")
        
        if c.render.engine == 'BLENDER_EEVEE':
            layout.separator()
            layout.prop(view.shading, "type", text = "")
            if view.shading.type != 'WIREFRAME':
                layout.separator()
            if view.shading.type == 'SOLID':
                layout.prop(view.shading, "light", text = "")
                layout.prop(view.shading, "color_type", text = "")
                layout.separator()
            if view.shading.type != 'WIREFRAME' and view.shading.type != 'RENDERED':
                if view.shading.light in ["STUDIO", "MATCAP"]:
                    layout.template_icon_view(view.shading, "studio_light", show_labels=True, scale=3)
                    layout.separator()
            if view.shading.type == 'MATERIAL' or view.shading.type == 'RENDERED':
                layout.prop(bpy.context.scene.eevee, "use_ssr", text = "Screen Space Reflections")
                if bpy.context.scene.eevee.use_ssr == True:
                    layout.prop(bpy.context.scene.eevee, "use_ssr_halfres", text = "Half Res")
                layout.prop(bpy.context.scene.eevee, "use_gtao", text = "AO")
                layout.prop(bpy.context.scene.eevee, "use_dof", text = "DOF")
                layout.prop(bpy.context.scene.eevee, "use_bloom", text = "Bloom")
                layout.prop(bpy.context.scene.eevee, "use_soft_shadows", text = "Soft Shadows")
                layout.prop(bpy.context.scene.eevee, "gi_diffuse_bounces", text = "Indirect Bounces")
                layout.prop(bpy.context.scene.eevee, "taa_samples", text = "Viewport Samples")
                layout.separator()
            if view.shading.type == 'MATERIAL':
                layout.prop(view.shading, 'use_scene_lights')
                layout.prop(view.overlay, 'show_look_dev')
            if view.shading.type == 'SOLID':
                if view.overlay.show_overlays == True:
                    layout.prop(view.overlay, 'show_wireframes')
                    layout.prop(view.overlay, 'wireframe_threshold')
                    layout.separator()
                layout.prop(bpy.context.scene.eevee, "use_gtao", text = "AO")
                layout.prop(bpy.context.scene.eevee, "use_soft_shadows", text = "Soft Shadows")
                layout.separator()
                layout.prop(view.shading, 'show_cavity')
                layout.prop(view.shading, 'show_shadows')
            layout.separator()
            layout.label(text = view.shading.type)
                
class HOPS_MT_RenderSetSubmenu(bpy.types.Menu):
    bl_label = 'RenderSet_submenu'
    bl_idname = 'hops.render_set_submenu'

    def draw(self, context):
        layout = self.layout
        
        c = bpy.context.scene
        if c.render.engine == 'CYCLES':
            layout.operator("render.setup", text="Render (1)", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Render (2)", icon="RESTRICT_RENDER_OFF")
        if c.render.engine == 'BLENDER_EEVEE':
            layout.operator("render.setup", text="Eevee HQ", icon="RESTRICT_RENDER_OFF")
            layout.operator("renderb.setup", text="Eevee LQ", icon="RESTRICT_RENDER_OFF")
        else:
            pass

        layout.separator()

        row = layout.row(align=False)
        col = row.column(align=True)

        view_settings = context.scene.view_settings
        col.prop(view_settings, "view_transform", text="")
        col.prop(view_settings, "look", text="")


class HOPS_MT_ResetAxiSubmenu(bpy.types.Menu):
    bl_idname = "hops.reset_axis_submenu"
    bl_label = "Reset Axis Submenu"

    def draw(self, context):
        layout = self.layout
        #layout = self.layout.column_flow(columns=2)
        #row = layout.row()
        #sub = row.row()
        #sub.scale_y = 1.0
        #sub.scale_x = 0.05

        layout.operator("hops.reset_axis", text=" X ", icon_value=get_icon_id("Xslap")).set_axis = "X"
        layout.operator("hops.reset_axis", text=" Y ", icon_value=get_icon_id("Yslap")).set_axis = "Y"
        layout.operator("hops.reset_axis", text=" Z ", icon_value=get_icon_id("Zslap")).set_axis = "Z"


class HOPS_MT_SymmetrySubmenu(bpy.types.Menu):
    bl_idname = "hops.symetry_submenu"
    bl_label = "Symmetry Submenu"

    def draw(self, context):
        layout = self.layout
        # box = layout.box()
        # row = box.row()

#        if pro_mode_enabled():
#            if any("AutoMirror" in s for s in bpy.context.preferences.addons.keys()):
#                layout.menu("automirror.submenu", text="Automirror", icon_value=get_icon_id("MHelper"))
#                layout.separator()

        # layout = self.layout.column_flow(columns=2)
        # row = layout.row()
#        sub = row.row()
#        sub.scale_y = 1.0
#        sub.scale_x = 0.05

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.mirror_gizmo", text="Mir2")
        # layout.operator("machin3.symmetrize", text="Machin3 Symmetrize")


class HOPS_MT_edgeWizardSubmenu(bpy.types.Menu):
    bl_label = 'EWizard Tools Submenu'
    bl_idname = 'hops.edge_wizzard_submenu'

    def draw(self, context):
        layout = self.layout

        if any("kk_QuickLatticeCreate" in s for s in bpy.context.preferences.addons.keys()):
            layout.operator("object.easy_lattice", text="Easy Lattice", icon_value=get_icon_id("Easylattice"))

        if any("mesh_snap" in s for s in bpy.context.preferences.addons.keys()):
            layout.operator("mesh.snap_utilities_line", text="Snap Line")
            layout.operator("mesh.snap_push_pull", text="Push Pull Faces")

        if any("mesh_edge_equalize" in s for s in bpy.context.preferences.addons.keys()):
            layout.operator("mo.edge_equalize_active", text="Edge Equalize")


class HOPS_MT_BoolSumbenu(bpy.types.Menu):
    bl_label = 'Bool Submenu'
    bl_idname = 'hops.bool_menu'

    def draw(self, context):
        layout = self.layout

        object = context.active_object

        if object.mode == "EDIT" and object.type == "MESH":
            layout.operator("hops.edit_bool_difference", text="Difference")#, icon="ROTACTIVE")
            layout.operator("hops.edit_bool_union", text="Union")#, icon="ROTATECOLLECTION")

        if object.mode == "OBJECT" and object.type == "MESH":
            layout.operator("hops.cut_in", text="Cut-in")#, icon_value=get_icon_id("Cutin"))
            layout.operator("hops.slash", text="(C) Slash")#, icon_value=get_icon_id("ReBool"))
            layout.separator()
            layout.operator("hops.bool_difference", text="Difference")#, icon="ROTACTIVE")
            layout.operator("hops.bool_intersect", text="Intersection")#, icon="ROTATECENTER")
            layout.operator("hops.bool_union", text="Union")#, icon="ROTATECOLLECTION")

            layout.separator()