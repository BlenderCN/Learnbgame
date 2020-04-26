import bpy
from ..addon import prefs, temp_prefs, is_28, ic
from ..utils.ui_utils import split
from ..constants import (
    ICON_NONE, ICON_FOLDER, ICON_COL,
    get_icon, get_bool_icon, LIST_ROW_SCALE_Y
)


class CB_UL_obj_list(bpy.types.UIList):

    def _draw_filter(self, context, layout):
        pr = prefs()
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.scale_x = 1.5
        sub.prop(
            pr, "group_none", text="", icon=ic('FILE_FOLDER'), toggle=True)
        row.prop(pr, "obj_list_width")

    def draw_filter27(self, context, layout):
        self._draw_filter(context, layout)

    def draw_filter28(self, context, layout, reverse=False):
        self._draw_filter(context, layout)

    draw_filter = draw_filter27
    # draw_filter = draw_filter28 if is_28() else draw_filter27

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_propname, index):
        self.use_filter_show = True

        is_group = item.type == 'GROUP'
        icon = ICON_FOLDER if is_group else ICON_NONE
        left, _, right = item.name.partition("|")
        if right:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            if not is_group:
                row.active = False
            row.label(text=left, icon=ic(icon))

            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            if not is_group:
                row.active = False
            row.label(text=right)

        else:
            layout.alignment = 'LEFT'
            if not is_group:
                layout.active = False
            layout.label(text=left, icon=ic(icon))


class CB_UL_info_list(bpy.types.UIList):

    def _draw_filter(self, context, layout):
        pr = prefs()
        row = split(layout, align=True)
        row.prop(pr, "show_prop_ids", text="", icon=ic('COPY_ID'))
        row.prop(pr, "show_bool_props", text="", icon=ic(get_icon("bool")))
        row.prop(pr, "show_int_props", text="", icon=ic(get_icon("int")))
        row.prop(pr, "show_float_props", text="", icon=ic(get_icon("float")))
        row.prop(pr, "show_str_props", text="", icon=ic(get_icon("string")))
        row.prop(pr, "show_enum_props", text="", icon=ic(get_icon("enum")))
        row.prop(pr, "show_vector_props", text="", icon=ic('GROUP'))

    def draw_filter27(self, context, layout):
        self._draw_filter(context, layout)

    def draw_filter28(self, context, layout, reverse=False):
        self._draw_filter(context, layout)

    draw_filter = draw_filter27
    # draw_filter = draw_filter28 if is_28() else draw_filter27

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_propname, index):
        self.use_filter_show = True

        if item.type == 'PROP':
            pr = prefs()
            row = layout.row(align=True)
            cd = temp_prefs().cd
            cd_data = cd.data
            icon = 'NONE'
            prop = cd_data.rna_type.properties[item.name]
            prop_type = type(prop)
            prop_type_name = prop_type.__name__
            prop_is_array = getattr(prop, "is_array", False)
            prop_icon = ICON_COL if prop_is_array else \
                get_icon(prop_type_name[:-8].lower())
            prop_name = prop.identifier \
                if pr.show_prop_ids or not prop.name else prop.name
            row.label(icon=ic(prop_icon))

            if prop_is_array and prop.subtype != 'COLOR' or \
                    prop.is_enum_flag:
                row.label(text=prop_name)
                sub = row.row(align=True)
                sub.alignment = 'RIGHT'
                p = sub.operator(
                    "cb.prop_popup", text="Edit...", emboss=False)
                p.data_path = cd.path
                p.prop = item.name

            else:
                row = split(row, 0.33, True)
                row.label(text=prop_name)
                row = row.row(align=True)

                if prop_type_name == "BoolProperty":
                    icon = get_bool_icon(getattr(cd_data, item.name))
                    row.alignment = 'LEFT'

                emboss = False
                if prop.subtype == 'COLOR':
                    emboss = True

                row.prop(
                    cd_data, item.name, text="", icon=ic(icon), icon_value=0,
                    emboss=emboss)

        elif item.type == 'GROUP':
            layout.scale_y = LIST_ROW_SCALE_Y
            layout.prop(
                temp_prefs(), item.name, icon=ic(item.data), toggle=True)

        elif item.type == 'FUNC':
            row = layout.row(align=True)
            row.label(icon=ic('FONT_DATA'))
            row = split(row, 0.33, True)
            row.label(text=item.name)

            sub = row.row(align=True)
            sub.alignment = 'RIGHT'
            sub.label(text=item.data)

        elif item.type == 'SPACER':
            pass


class CB_OT_copy_path(bpy.types.Operator):
    bl_idname = "cb.copy_path"
    bl_label = ""
    bl_description = "Copy Path"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tpr = temp_prefs()
        context.window_manager.clipboard = tpr.cd.path
        return {'FINISHED'}


class CB_OT_copy_path_area(bpy.types.Operator):
    bl_idname = "cb.copy_path_area"
    bl_label = ""
    bl_description = "Copy Area Path"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        path = repr(context.screen)

        for i, a in enumerate(context.screen.areas):
            if a == context.area:
                index = i
                break

        path += ".areas[%d]" % index
        context.window_manager.clipboard = path

        return {'FINISHED'}


class CB_OT_browser(bpy.types.Operator):
    bl_idname = "cb.browser"
    bl_label = "Context Browser"
    bl_description = "Context Browser"

    instance = None

    path = bpy.props.StringProperty(default="C")

    def draw(self, context):
        pr = prefs()
        tpr = temp_prefs()
        layout = self.layout

        col = layout.column(align=True)
        row = col.box().row()

        sub = row.row(align=True)
        sub.operator("cb.bookmark_menu", text="", icon=ic('BOOKMARKS'))

        sub = row.row(align=True)
        if len(tpr.breadcrumb_items) > 1:
            left = sub.row(align=True)
            left.alignment = 'LEFT'
            for id, name, _ in tpr.breadcrumb_items:
                if id == tpr.breadcrumb_items[-1][0]:
                    break
                left.prop_enum(tpr, "path", id)
        sub.prop_enum(tpr, "path", tpr.breadcrumb_items[-1][0])

        sub = row.row(align=True)
        sub.operator("cb.copy_path", text="", icon=ic('COPYDOWN'))

        row = split(col, 0.01 * pr.obj_list_width, True)
        row.template_list(
            "CB_UL_obj_list", "",
            tpr, "obj_list",
            tpr, "obj_list_idx", rows=pr.list_height)

        row.template_list(
            "CB_UL_info_list", "",
            tpr, "info_list",
            tpr, "info_list_idx", rows=pr.list_height)

        row = col.box().row()
        left = row.row()
        left.alignment = 'LEFT'
        left.label(
            text="%s Area | Area Type: %s | Area Index: %d | Spaces: %d" % (
                self.area_name, self.area_type, self.area_index,
                self.area_spaces
            ),
            icon_value=self.area_icon)

        row.row()

        right = row.row()
        right.operator("cb.copy_path_area", text="", icon=ic('COPYDOWN'))

    def check(self, context):
        return True

    def cancel(self, context):
        CB_OT_browser.instance = None
        temp_prefs().clear_lists()

    def execute(self, context):
        CB_OT_browser.instance = None
        temp_prefs().clear_lists()
        return {'FINISHED'}

    def invoke(self, context, event):
        CB_OT_browser.instance = self
        CB_OT_browser.focus = False
        tpr = temp_prefs()
        tpr.cd.update_lists(tpr.last_path)

        self.area_type = context.area.type
        self.area_name = bpy.types.UILayout.enum_item_name(
            context.area, "type", self.area_type)
        self.area_icon = bpy.types.UILayout.enum_item_icon(
            context.area, "type", self.area_type)
        self.area_spaces = len(context.area.spaces)

        for i, a in enumerate(context.screen.areas):
            if a == context.area:
                self.area_index = i
                break

        return context.window_manager.invoke_props_dialog(
            self, width=prefs().popup_width)
