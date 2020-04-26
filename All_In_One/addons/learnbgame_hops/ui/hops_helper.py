import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty
from .. utils.blender_ui import get_dpi_factor
from bl_ui.properties_data_modifier import DATA_PT_modifiers
from .. preferences import get_preferences


class HopsHelperOptions(PropertyGroup):

    operators_options: BoolProperty(
        name="Operators options",
        description="Display Hardops operator settings",
        default=False
    )

    sharp_options: BoolProperty(
        name="Sharp options",
        description="Display pre-sharp options",
        default=True
    )

    mesh_options: BoolProperty(
        name="Mesh options",
        description="General Mesh configuration settings",
        default=False
    )

    status: BoolProperty(
        name="Status",
        description="General sstatus behavioral options",
        default=False
    )

    surface: BoolProperty(
        name="Surface",
        description="Display surface settings",
        default=False
    )

    settings: BoolProperty(
        name="Settings",
        description="Display additional settings",
        default=False
    )

    cutting_material: BoolProperty(
        name="Cutting Material",
        description="Display cutting material settings",
        default=True
    )

    meshclean_options: BoolProperty(
        name="Mesh clean Material",
        description="Display meshclean settings",
        default=False
    )

    mirror_options: BoolProperty(
        name="Mirror options",
        description="Display mirroring settings",
        default=True
    )


def find_node(material, nodetype):
    if material and material.node_tree:
        ntree = material.node_tree

        active_output_node = None
        for node in ntree.nodes:
            if getattr(node, "type", None) == nodetype:
                if getattr(node, "is_active_output", True):
                    return node
                if not active_output_node:
                    active_output_node = node
        return active_output_node

    return None


def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

    return None


def panel_node_draw(layout, id_data, output_type, input_name):
    if not id_data.use_nodes:
        layout.operator("cycles.use_shading_nodes", icon='NODETREE')
        return False

    ntree = id_data.node_tree

    node = find_node(id_data, output_type)
    if not node:
        layout.label(text ="No output node")
    else:
        input = find_node_input(node, input_name)
        layout.template_node_view(ntree, node, input)

    return True

helper_tabs_items = [
    ("MODIFIERS", "Modifiers", ""),
    ("MATERIALS", "Materials", ""),
    ("MISC", "Misc", "")]

hops_status = [
    ("UNDEFINED", "Undefined", ""),
    ("CSHARP", "Csharp", ""),
    ("CSTEP", "Cstep", ""),
    ("BOOLSHAPE", "Boolshape", ""),
    ("BOOLSHAPE2", "Boolshape2", "")]


class HOPS_OT_HelperPopup(bpy.types.Operator):
    """
    Displays modifers / material / hardops popup helper.

    """
    bl_idname = "view3d.hops_helper_popup"
    bl_label = "HOps Helper"

    tab: EnumProperty(name="Tab", default="MODIFIERS",
                      options={"SKIP_SAVE"}, items=helper_tabs_items)

    status: EnumProperty(name="Status", default="UNDEFINED",
                         options={"SKIP_SAVE"}, items=hops_status)

    # mesh_tools = BoolProperty(name = "Z Axis", description = "Z Axis", default = False)

    def execute(self, context):
        self.set_helper_default(context)
        self.set_hops_status(context)
        return {'FINISHED'}

    def cancel(self, context):
        self.set_helper_default(context)
        self.set_hops_status(context)

    def check(self, context):
        return True

    def invoke(self, context, event):
        object = bpy.context.active_object
        if object is not None:
            if object.type == "MESH":
                self.status = object.hops.status
        self.tab = get_preferences().helper_tab
        return context.window_manager.invoke_props_dialog(self, width=300 * get_dpi_factor())

    def set_helper_default(self, context):
        if self.tab == "MODIFIERS":
            get_preferences().helper_tab = "MODIFIERS"
        elif self.tab == "MATERIALS":
            get_preferences().helper_tab = "MATERIALS"
        elif self.tab == "MISC":
            get_preferences().helper_tab = "MISC"

    def set_hops_status(self, context):
        object = bpy.context.active_object
        if object is not None:
            if object.type == "MESH":
                if self.status == "UNDEFINED":
                    object.hops.status = "UNDEFINED"
                elif self.status == "CSHARP":
                    object.hops.status = "CSHARP"
                elif self.status == "CSTEP":
                    object.hops.status = "CSTEP"
                elif self.status == "BOOLSHAPE":
                    object.hops.status = "BOOLSHAPE"
                elif self.status == "BOOLSHAPE2":
                    object.hops.status = "BOOLSHAPE2"

    def draw(self, context):
        layout = self.layout
        self.draw_tab_bar(layout)

        if self.tab == "MODIFIERS":
            self.draw_modifier_tab(layout)
        elif self.tab == "MATERIALS":
            self.draw_material_tab(context, layout)
        elif self.tab == "MISC":
            self.draw_misc_tab(context, layout)

    def draw_tab_bar(self, layout):
        row = layout.row()
        row.prop(self, "tab", expand=True)
        layout.separator()

    def draw_modifier_tab(self, layout):

        col = layout.column(align=True)
        object = bpy.context.active_object
        if object is None:
            colrow = col.row(align=True)
            colrow.alignment = "CENTER"
            colrow.label(text="No active object", icon="INFO")
            return

        colrow = col.row(align=True)
        colrow.operator_menu_enum("object.modifier_add", "type")
        colrow.operator("object.make_links_data", text="Copy Modifiers").type = "MODIFIERS"
        colrow.operator("hops.open_modifiers", text="", icon="TRIA_DOWN")
        colrow.operator("hops.collapse_modifiers", text="", icon="TRIA_UP")

        modifiers_panel = DATA_PT_modifiers(bpy.context)
        for modifier in object.modifiers:
            box = layout.template_modifier(modifier)
            if box:
                getattr(modifiers_panel, modifier.type)(box, object, modifier)

    def draw_material_tab(self, context, layout):

        object = context.active_object
        option = context.window_manager.Hard_Ops_helper_options

        if object:
            is_sortable = len(object.material_slots) > 1
            rows = 2

            if (is_sortable):
                rows = 4
            row = layout.row()
            row.context_pointer_set('material', object.active_material)

            row.template_list("MATERIAL_UL_matslots", "", object, "material_slots", object, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()
                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if object.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        if object:
            split = layout.split(factor=0.65)
            slot = object.material_slots[object.active_material_index] if object.material_slots else None
            split.template_ID(object, "active_material", new="material.hops_new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")

            else:
                row.label(text="")

        column = layout.column(align=True)
        if object and object.material_slots and object.active_material:
            box = column.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            sub = row.row(align=True)
            # sub.scale_x = 0.5
            sub.prop(option, "surface", icon="TRIA_DOWN" if option.surface else "TRIA_RIGHT", text="", emboss=False)
            row.prop(option, "surface", text="Surface", toggle=True, emboss=False)
            sub = row.row(align=True)
            sub.prop(option, "surface", text=" ", toggle=True, emboss=False)

            if option.surface:
                box = column.box()

                if not panel_node_draw(box, object.active_material, 'OUTPUT_MATERIAL', 'Surface'):
                    row = layout.row()
                    row.prop(object.active_material, "diffuse_color")

            column.separator()
            box = column.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            sub = row.row(align=True)
            # sub.scale_x = 0.5
            sub.prop(option, "settings", icon="TRIA_DOWN" if option.settings else "TRIA_RIGHT", text="", emboss=False)
            row.prop(option, "settings", text="Settings", toggle=True, emboss=False)
            sub = row.row(align=True)
            sub.prop(option, "settings", text=" ", toggle=True, emboss=False)

            if option.settings:
                box = column.box()
                col = box.column()
                split = col.split()
                col = split.column(align=True)
                col.label(text="Viewport Color:")
                col.prop(object.active_material, "diffuse_color", text="")
                #col.prop(object.active_material, "specular_color", text="")
                #col.prop(object.active_material, "roughness")
                col.label(text="Transparency Type:")
                col.prop(object.active_material, "blend_method", text="")
                col.prop(object, "show_transparent", text="Transparency")
                col.label(text="Pass Index:")
                col.prop(object.active_material, "pass_index", text ='')
            column.separator()

        box = column.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        sub = row.row(align=True)
        sub.prop(option, "cutting_material", icon="TRIA_DOWN" if option.cutting_material else "TRIA_RIGHT", text="", emboss=False)
        row.prop(option, "cutting_material", text="Cutting Material", toggle=True, emboss=False)
        sub = row.row(align=True)
        sub.prop(option, "cutting_material", text=" ", toggle=True, emboss=False)

        if option.cutting_material:
            box = column.box()

            material_option = context.window_manager.Hard_Ops_material_options

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(material_option, "material_mode", expand=True)
            row = col.row(align=True)

            if material_option.material_mode == "ALL":
                row.prop_search(material_option, "active_material", bpy.data, "materials", text="")

            else:
                row.prop_search(material_option, "active_material", context.active_object, "material_slots", text="")

            row.prop(material_option, "force", text="", icon="FORCE_FORCE")

    def draw_misc_tab(self, context, layout):
        # layout.label(text="Coming To 008!", icon="INFO")

        ob = context.object
        active_object = context.active_object
        option = context.window_manager.Hard_Ops_helper_options

        layout = self.layout

        # box = layout.box().column(1)
        # row = box.row(1)

        col = layout.box().column(align=True)

        col.separator()
        colrow = col.row(align=True)
        colrow.prop(get_preferences(), "workflow", expand=True)
        colrow = col.row(align=True).split(factor=0.1, align=True)
        colrow.prop(get_preferences(), "add_weighten_normals_mod", toggle=True)
        colrow2 = colrow.row(align=True)
        colrow2.prop(get_preferences(), "workflow_mode", expand=True)
        col.separator()

        col = layout.box().column(align=True)
        col.prop(option, "sharp_options", icon="TRIA_DOWN" if option.sharp_options else "TRIA_RIGHT", text="Sharps", emboss=False)

        if option.sharp_options:
            col = layout.column(align=True)

            col.separator()
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "sharp_use_crease", text="Apply crease")
            colrow.prop(get_preferences(), "sharp_use_bweight", text="Apply bweight")

            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "sharp_use_seam", text="Apply seam")
            colrow.prop(get_preferences(), "sharp_use_sharp", text="Apply sharp")

            col.separator()
            colrow = col.row(align=True)
            colrow.operator("hops.set_sharpness_30", text="30")
            colrow.operator("hops.set_sharpness_45", text="45")
            colrow.operator("hops.set_sharpness_60", text="60")

            col.prop(get_preferences(), "sharpness", text="Sharpness")
            col = layout.box().column(align=True)

        col.prop(option, "mirror_options", icon="TRIA_DOWN" if option.mirror_options else "TRIA_RIGHT", text="Mirror Options", emboss=False)

        if option.mirror_options:
            col = layout.column(align=True)

            col.separator()
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "Hops_mirror_modes", text="aa", expand=True)
            if get_preferences().Hops_mirror_modes in {"BISECT", "SYMMETRY"}:
                colrow = col.row(align=True)
                colrow.prop(get_preferences(), "Hops_mirror_direction", text="vv", expand=True)

            col = layout.box().column(align=True)

        col.prop(option, "operators_options", icon="TRIA_DOWN" if option.operators_options else "TRIA_RIGHT", text="Operators Options", emboss=False)

        if option.operators_options:
            col = layout.column(align=True)

            col.separator()
            colrow = col.row(align=True)
            colrow.label(text='Modals :')

            col.separator()
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "Hops_modal_scale", text="Modal Scale")
            colrow.prop(get_preferences(), "adaptivewidth", text="Adapitve")

            col.separator()
            colrow = col.row(align=True)
            colrow.label(text='CSharpen :')
            col.separator()
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "bevel_loop_slide", text="use Loop slide")
            colrow.prop(get_preferences(), "auto_bweight", text="jump to (B)Width")

            col.separator()
            colrow = col.row(align=True)
            colrow.label(text='Mirror :')
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "Hops_mirror_modal_scale", text="Mirror Scale")
            colrow.prop(get_preferences(), "Hops_mirror_modal_sides_scale", text="Mirror Size")
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), "Hops_mirror_modal_Interface_scale", text="Mirror Interface Scale")
            colrow.prop(get_preferences(), "Hops_mirror_modal_revert", text="Revert")
            col.separator()

            col.separator()
            colrow = col.row(align=True)
            colrow.label(text='CutIn :')
            colrow.prop(get_preferences(), "keep_cutin_bevel", expand=True)
            col.separator()

            colrow = col.row(align=True)
            colrow.label(text='Array :')
            colrow.prop(get_preferences(), "force_array_reset_on_init", expand=True)
            colrow = col.row(align=True)
            colrow.label(text='')
            colrow.prop(get_preferences(), "force_array_apply_scale_on_init", expand=True)
            col.separator()

            col.separator()
            colrow = col.row(align=True)
            colrow.label(text='Thick :')
            colrow.prop(get_preferences(), "force_thick_reset_solidify_init", expand=True)
            col.separator()

            col = layout.box().column(align=True)

        col.prop(option, "status", icon="TRIA_DOWN" if option.status else "TRIA_RIGHT", text="Status", emboss=False)

        if option.status:
            col = layout.column(align=True)
            colrow = col.row(align=True)
            colrow.prop(self, "status", expand=True)
            col = layout.box().column(align=True)

        col.prop(option, "mesh_options", icon="TRIA_DOWN" if option.mesh_options else "TRIA_RIGHT", text="Mesh Options", emboss=False)

        if option.mesh_options:
            col = layout.column(align=True)
            if ob:
                if active_object.type == "MESH":

                    colrow = col.row(align=True)
                    obj = bpy.context.object
                    # colrow.label(text ="Name:")
                    colrow.prop(obj, "name", text="")

                    col.separator()

                    colrow = col.row(align=True)
                    colrow.operator("object.shade_smooth", text="Set Smooth")
                    colrow.operator("object.shade_flat", text="Shade Flat")

                    colrow = col.row(align=True)
                    asmooth = bpy.context.object.data
                    colrow.prop(asmooth, "auto_smooth_angle", text="Auto Smooth Angle")
                    colrow.prop(asmooth, "use_auto_smooth", text="Auto Smooth")

                    col.separator()

                    colrow = col.row(align=True)
                    swire = bpy.context.object
                    colrow.prop(swire, "show_wire", text="Show Wire")
                    colrow.prop(swire, "show_all_edges", text="Show All Edges")

                    col.separator()

                    colrow = col.row(align=True)
                    colrow.label(text ="Parent:")
                    colrow.prop(ob, "parent", text="")

                    col.separator()

                elif active_object.type == "CURVE":
                    layout.label(text="Curve Stuff Soon", icon="INFO")

                    # the idea is that curve stuff will be here for quick options for things the q menu cant do.
            else:
                col.label(text="add object first", icon="INFO")

        col.prop(option, "meshclean_options", icon="TRIA_DOWN" if option.meshclean_options else "TRIA_RIGHT", text="Mesh Clean Options", emboss=False)

        if option.meshclean_options:
            col = layout.column(align=True)

            col.separator()
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), 'meshclean_mode', expand=True)
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), 'meshclean_dissolve_angle', text="Limited Disolve Angle")
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), 'meshclean_remove_threshold', text="Remove Threshold")
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), 'meshclean_unhide_behavior', text="Unhide Mesh")
            colrow = col.row(align=True)
            colrow.prop(get_preferences(), 'meshclean_delete_interior', text="Delete Interior Faces")


        layout.separator()
