import bpy
from .addon import ADDON_ID, temp_prefs, prefs, ic
from .utils.collection_utils import sort_collection
from .ops.context_browser import CB_OT_browser


class BookmarkItem(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty()


class CB_Preferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID

    bookmarks = bpy.props.CollectionProperty(type=BookmarkItem)

    def update_lists(self, context):
        tpr = temp_prefs()
        tpr.cd.update_lists(tpr.path, False)

    show_bool_props = bpy.props.BoolProperty(
        name="Show Bool Properties", description="Show bool properties",
        default=True, update=update_lists)
    show_int_props = bpy.props.BoolProperty(
        name="Show Int Properties", description="Show int properties",
        default=True, update=update_lists)
    show_float_props = bpy.props.BoolProperty(
        name="Show Float Properties", description="Show float properties",
        default=True, update=update_lists)
    show_str_props = bpy.props.BoolProperty(
        name="Show String Properties", description="Show string properties",
        default=True, update=update_lists)
    show_enum_props = bpy.props.BoolProperty(
        name="Show Enum Properties", description="Show enum properties",
        default=True, update=update_lists)
    show_vector_props = bpy.props.BoolProperty(
        name="Show Vector Properties", description="Show vector properties",
        default=True, update=update_lists)
    group_none = bpy.props.BoolProperty(
        name="Group None Objects",
        description="Group None objects",
        default=False, update=update_lists)
    show_prop_ids = bpy.props.BoolProperty(
        name="Show Property Identifiers",
        description="Show property identifiers",
        default=True)

    def show_header_btn_update(self, context):
        prefs().register_header_btn(self.show_header_btn)

    show_header_btn = bpy.props.BoolProperty(
        name="Show Header Button",
        description="Show header button",
        update=show_header_btn_update,
        default=True)
    obj_list_width = bpy.props.IntProperty(
        name="Width", description="Width of the list",
        subtype='PERCENTAGE',
        default=40, min=20, max=80)
    list_height = bpy.props.IntProperty(
        name="Number of Rows", description="Number of rows in lists",
        default=10, min=5, max=100)
    popup_width = bpy.props.IntProperty(
        name="Width", description="Popup width",
        subtype='PIXEL',
        default=640, min=300, max=3000)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator(CB_OT_browser.bl_idname)

        row = layout.split()

        col = row.column(align=True)
        col.label(text="Popup:")
        col.prop(self, "popup_width")
        col.prop(self, "list_height")

        col = row.column(align=True)
        col.label(text="Header:")
        col.prop(self, "show_header_btn")

    def add_bookmark(self, bookmark, name=None):
        if bookmark in self.bookmarks:
            return

        item = self.bookmarks.add()
        item.name = name or bookmark
        item.path = bookmark

        sort_collection(self.bookmarks, key=lambda item: item.name)

    def remove_bookmark(self, bookmark):
        for i, b in enumerate(self.bookmarks):
            if b.path == bookmark:
                self.bookmarks.remove(i)
                break

    def rename_bookmark(self, bookmark, name):
        for b in self.bookmarks:
            if b.path == bookmark:
                b.name = name
                break

        sort_collection(self.bookmarks, key=lambda item: item.name)

    def register_header_btn(self, value):
        for tp_name in (
                'CLIP_HT_header', 'CONSOLE_HT_header',
                'DOPESHEET_HT_header', 'FILEBROWSER_HT_header',
                'GRAPH_HT_header', 'IMAGE_HT_header',
                'INFO_HT_header', 'LOGIC_HT_header',
                'NLA_HT_header', 'NODE_HT_header',
                'OUTLINER_HT_header', 'PROPERTIES_HT_header',
                'SEQUENCER_HT_header', 'TEXT_HT_header',
                'TIME_HT_header', 'USERPREF_HT_header',
                'VIEW3D_HT_header'):
            tp = getattr(bpy.types, tp_name, None)
            if not tp:
                continue

            if value:
                tp.prepend(self.header_menu)
            else:
                tp.remove(self.header_menu)

    @staticmethod
    def context_menu(menu, context):
        layout = menu.layout
        layout.operator("cb.browser", icon=ic('BLENDER'))

    @staticmethod
    def header_menu(menu, context):
        layout = menu.layout
        layout.operator("cb.browser", text="", icon=ic('BLENDER'), emboss=False)


def register():
    pr = prefs()
    if pr.show_header_btn:
        pr.register_header_btn(True)


def unregister():
    pr = prefs()
    if pr.show_header_btn:
        pr.register_header_btn(False)
