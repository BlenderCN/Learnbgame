import bpy
import webbrowser

from bpy.types import Header, Menu
from bpy.types import NODE_HT_header as NODE_HT_header_old
from bpy.types import (
    NODE_PT_grease_pencil,
    NODE_PT_tools_grease_pencil_brush,
    NODE_PT_tools_grease_pencil_edit,
    NODE_PT_tools_grease_pencil_brushcurves,
    NODE_PT_grease_pencil_tools,
    NODE_PT_tools_grease_pencil_draw,
    NODE_PT_grease_pencil_palettecolor,
    NODE_PT_tools_grease_pencil_sculpt,
)


from auth import ocvl_auth
from auth import DEBUG
sv_tree_types = {'SverchCustomTreeType', 'SverchGroupTreeType'}


class NODE_HT_header(Header):
    bl_space_type = 'NODE_EDITOR'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        ob = context.object
        snode = context.space_data
        snode_id = snode.id
        id_from = snode.id_from
        toolsettings = context.tool_settings

        row = layout.row(align=True)
        row.label(icon='NODETREE')
        # row.template_header()

        if context.area.show_menus:
            row.menu("NODE_MT_view_new")
            row.menu("NODE_MT_select_new")
            row.menu("NODE_MT_add")
            row.menu("NODE_MT_node_new")

        layout.template_ID(snode, "node_tree", new="node.new_node_tree")

        # layout.prop(snode, "pin", text="")
        layout.operator("node.tree_path_parent", text="", icon='FILE_PARENT')

        layout.separator()

        # Auto-offset nodes (called "insert_offset" in code)
        layout.prop(snode, "use_insert_offset", text="")

        # Snap
        row = layout.row(align=True)
        row.prop(toolsettings, "use_snap", text="")
        row.prop(toolsettings, "snap_node_element", icon_only=True)
        if toolsettings.snap_node_element != 'GRID':
            row.prop(toolsettings, "snap_target", text="")

        row = layout.row(align=True)
        row.operator("node.clipboard_copy", text="", icon='COPYDOWN')
        row.operator("node.clipboard_paste", text="", icon='PASTEDOWN')

        layout.template_running_jobs()


class NODE_MT_view_new(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("node.properties", icon='MENU_PANEL')
        layout.operator("node.toolbar", icon='MENU_PANEL')

        layout.separator()

        layout.operator("view2d.zoom_in")
        layout.operator("view2d.zoom_out")

        layout.separator()

        layout.operator("node.view_selected")
        layout.operator("node.view_all")

        if context.space_data.show_backdrop:
            layout.separator()

            layout.operator("node.backimage_move", text="Backdrop Move")
            layout.operator("node.backimage_zoom", text="Backdrop Zoom In").factor = 1.2
            layout.operator("node.backimage_zoom", text="Backdrop Zoom Out").factor = 0.83333
            layout.operator("node.backimage_fit", text="Fit Backdrop to Available Space")

        layout.separator()

        layout.operator("screen.area_dupli")


class NODE_MT_select_new(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("node.select_border").tweak = False
        layout.operator("node.select_circle")

        layout.separator()
        layout.operator("node.select_all").action = 'TOGGLE'
        layout.operator("node.select_all", text="Inverse").action = 'INVERT'
        layout.operator("node.select_linked_from")
        layout.operator("node.select_linked_to")

        layout.separator()

        layout.operator("node.select_grouped").extend = False
        layout.operator("node.select_same_type_step", text="Activate Same Type Previous").prev = True
        layout.operator("node.select_same_type_step", text="Activate Same Type Next").prev = False

        layout.separator()

        layout.operator("node.find_node")


class NODE_MT_node_new(Menu):
    bl_label = "Node"

    def draw(self, context):
        layout = self.layout

        layout.operator("transform.translate")

        layout.separator()

        layout.operator("node.duplicate_move")
        layout.operator("node.delete")
        layout.operator("node.delete_reconnect")

        layout.separator()

        layout.operator("node.link_make").replace = False
        layout.operator("node.link_make", text="Make and Replace Links").replace = True
        layout.operator("node.links_cut")
        layout.operator("node.links_detach")

        layout.separator()

        layout.operator("node.group_edit").exit = False
        layout.operator("node.group_ungroup")
        layout.operator("node.group_make")
        layout.operator("node.group_insert")

        # layout.separator()
        #
        # layout.operator("node.hide_toggle")
        # layout.operator("node.mute_toggle")
        # layout.operator("node.preview_toggle")
        # layout.operator("node.hide_socket_toggle")
        # layout.operator("node.options_toggle")
        # layout.operator("node.collapse_hide_unused_toggle")


class SvViewHelpForNodeNew(bpy.types.Operator):
    from bpy.props import StringProperty
    bl_idname = "node.view_node_help"
    bl_label = "display a browser with compiled html"
    kind = StringProperty(default='online')

    def execute(self, context):
        active_node = context.active_node

        if self.kind == 'online':
            url = 'https://docs.opencv.org/3.0-last-rst/search.html?q={}&check_keywords=yes&area=default'.format(active_node.bl_label)
            webbrowser.open(url)
        elif self.kind == 'offline':
            self.report({'INFO'}, 'Documentation docstring - {}'.format(active_node.bl_label))
        elif self.kind == 'github':
            webbrowser.open("https://github.com/feler404/ocvl")

        return {'FINISHED'}


class SvViewSourceForNodeNew(bpy.types.Operator):
    from bpy.props import StringProperty
    bl_idname = "node.sv_view_node_source"
    bl_label = "display the source in your editor"
    kind = StringProperty(default='external')

    def execute(self, context):
        webbrowser.open("https://github.com/feler404/ocvl")
        return {'FINISHED'}


class NODEVIEW_MT_Dynamic_Menu_new(bpy.types.Menu):
    bl_label = "Sverchok Nodes"

    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        if tree_type in sv_tree_types:
            return True

    def draw(self, context):

        tree_type = context.space_data.tree_type
        if not tree_type in sv_tree_types:
            return

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        if self.bl_idname == 'NODEVIEW_MT_Dynamic_Menu_new':
            layout.operator("node.sv_extra_search", text="Search", icon='OUTLINER_DATA_FONT')


        layout.separator()
        layout.menu("NODE_MT_category_SVERCHOK_GROUPS", icon="RNA")



def valid_active_node(nodes):
    if nodes:
        # a previously active node can remain active even when no nodes are selected.
        if nodes.active and nodes.active.select:
            return nodes.active


def has_outputs(node):
    return node and len(node.outputs)


class SvNodeviewRClickMenu_new(bpy.types.Menu):
    bl_label = "Right click menu"
    bl_idname = "NODEVIEW_MT_sv_rclick_menu"

    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        return tree_type in sv_tree_types

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.edit_tree
        nodes = tree.nodes
        node = valid_active_node(nodes)

        if node:
            if has_outputs(node):
                layout.operator("node.sv_deligate_operator", text="Connect Viewer").fn = "Viewer"

            if hasattr(node, "rclick_menu"):
                node.rclick_menu(context, layout)

        else:
            layout.menu("NODEVIEW_MT_Dynamic_Menu_new", text='node menu')

        if node and len(node.outputs):
            layout.operator("node.sv_deligate_operator", text="Connect stethoscope").fn = "Stethoscope"


def add_connection_new(tree, bl_idname_new_node, offset):

    nodes = tree.nodes
    links = tree.links

    existing_node = nodes.active

    if isinstance(bl_idname_new_node, str):

        new_node = nodes.new(bl_idname_new_node)

        outputs = existing_node.outputs
        inputs = new_node.inputs

        links.new(outputs[0], inputs[0])


class SvGenericDeligationOperator_new(bpy.types.Operator):

    bl_idname = "node.sv_deligate_operator"
    bl_label = "Execute generic code"

    fn = bpy.props.StringProperty(default='')

    def execute(self, context):
        tree = context.space_data.edit_tree

        if self.fn == 'Viewer':
            add_connection_new(tree, bl_idname_new_node=ocvl_auth.viewer_name, offset=[220, 0])
        elif self.fn == 'Stethoscope':
            add_connection_new(tree, bl_idname_new_node="SvStethoscopeNodeMK2", offset=[220, 0])

        return {'FINISHED'}



classes_to_unregister = [
    NODE_PT_grease_pencil,
    NODE_PT_tools_grease_pencil_brush,
    NODE_PT_tools_grease_pencil_edit,
    NODE_PT_tools_grease_pencil_brushcurves,
    NODE_PT_grease_pencil_tools,
    NODE_PT_tools_grease_pencil_draw,
    NODE_PT_grease_pencil_palettecolor,
    NODE_PT_tools_grease_pencil_sculpt,

    NODE_HT_header_old,
    ]


SV_CLASSES = [
    NODEVIEW_MT_Dynamic_Menu_new,
    SvViewHelpForNodeNew,
    SvViewSourceForNodeNew,
    SvNodeviewRClickMenu_new,
    SvGenericDeligationOperator_new,
]



classes = [
    NODE_HT_header,
    NODE_MT_view_new,
    NODE_MT_select_new,
    NODE_MT_node_new,

]

if not DEBUG:
    classes += SV_CLASSES
