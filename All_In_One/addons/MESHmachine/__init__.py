'''
    Copyright (C) 2018 MACHIN3, machin3.io, mesh@machin3.io

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

bl_info = {
    "name": "MESHmachine",
    "author": "MACHIN3",
    "version": (0, 6, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "The missing essentials.",
    # "warning": "This is a preview of the next stable realease, things may be more likely to break",
    "wiki_url": "https://mesh.machin3.io",
    "tracker_url": "https://machin3.io/MESHmachine/docs/faq/#reporting-errors-or-problems",
    "category": "Learnbgame",
    }


import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, FloatVectorProperty, StringProperty, PointerProperty, CollectionProperty
import os
from . properties import MMObjectProperties, MMSceneProperties
from . keymaps import register_keymaps
from . ui.MESHmachine import specials_menu
from . ui.stashesHUD import scene_update_handler
from . utils import developer as dev
from . utils.registration import register_and_load_plugs, unregister_and_unload_plugs
from . utils import MACHIN3 as m3

modules = dev.setup_addon_modules(__path__, __name__, "bpy" in locals())


preferences_tabs = [("GENERAL", "General", ""),
                    ("PLUGS", "Plugs", ""),
                    ("ABOUT", "About", "")]

keyboard_layout_items = [("QWERTY", "QWERTY", ""),
                         ("QWERTZ", "QWERTZ", "")]


links = [("Buy MESHmachine @ Gumroad", "https://gumroad.com/l/MESHmachine", "NONE"),
         ("Buy MESHmachine @ Blender Market", "https://www.blendermarket.com/products/MESHmachine", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("Documentation", "https://machin3.io/MESHmachine/docs/", "INFO"),
         ("MACHINƎ.io", "https://machin3.io", "WORLD"),
         ("Report Errors or Problems", "https://machin3.io/MESHmachine/docs/faq/#reporting-errors-or-problems", "ERROR"),
         ("FAQ", "https://machin3.io/MESHmachine/docs/faq/", "QUESTION"),
         ("Youtube", "https://www.youtube.com/channel/UC4yaFzFDILd2yAqOWRuLOvA", "NONE"),
         ("Twitter", "https://twitter.com/machin3io", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("MESHmachine @ BlenderArtists", "https://blenderartists.org/t/meshmachine/1102529", "NONE"),
         ("MESHmachine @ Polycount", "https://polycount.com/discussion/205933/blender-meshmachine-hard-surface-focused-mesh-modeling/", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("Get MACHIN3tools @ GitHub", "https://github.com/machin3io/MACHIN3tools", "NONE"),
         ("MACHINƎ @ Artstation", "https://www.artstation.com/artist/machin3", "NONE"),
         ]


op_context_items = [("EXEC_DEFAULT", "Simple", ""),
                    ("INVOKE_DEFAULT", "Modal", "")]


plugmodeitems = [("INSERT", "Insert", ""),
                 ("REMOVE", "Remove", ""),
                 ("NONE", "None", "")]


class PlugLibsUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        isvisibleicon = "RESTRICT_VIEW_OFF" if item.isvisible else "RESTRICT_VIEW_ON"
        islockedicon = "LOCKED" if item.islocked else "BLANK1"

        split = layout.split(0.7)

        row = split.row()
        row.label(text=item.name)
        row = split.row()
        row.prop(item, "isvisible", text="", icon=isvisibleicon, emboss=False)
        row.prop(item, "islocked", text="", icon=islockedicon, emboss=False)


class PlugLibsCollection(bpy.types.PropertyGroup):
    name = StringProperty()
    isvisible = BoolProperty(default=True, description="Show in MESHmachine Menu")
    islocked = BoolProperty(default=False, description="Prevent Plug Creation. Requires Library Reload")


class MESHmachinePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    MMpath = __path__[0]

    debug = BoolProperty(name="Debug MESHmachine", default=False)

    # LAYOUT
    tabs = bpy.props.EnumProperty(name="Tabs", items=preferences_tabs, default="GENERAL")

    # MENU

    show_in_specials_menu = BoolProperty(name="Show in Specials Menu", default=True)

    show_looptools_wrappers = BoolProperty(name="Show LoopTools Wrappers", default=True)

    show_mesh_split = BoolProperty(name="Show Mesh Split tool (QWERTZ keyboards)", default=True)
    show_delete = BoolProperty(name="Show Delete Menu (QWERTY keyboards)", default=True)

    show_documentation = BoolProperty(name="Show Documentation", default=True)

    # KEYMAP

    keyboard_layout = EnumProperty(name="Keyboard Layout", items=keyboard_layout_items, default="QWERTY")

    # BEHAVIOR

    modal_Fuse = EnumProperty(name="Fuse", items=op_context_items, default="INVOKE_DEFAULT")
    modal_ChangeWidth = EnumProperty(name="Change Width", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Flatten = EnumProperty(name="Flatten", items=op_context_items, default="INVOKE_DEFAULT")

    modal_Unfuck = EnumProperty(name="Unf*ck", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Unfuse = EnumProperty(name="Unfuse", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Refuse = EnumProperty(name="Refuse", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Unbevel = EnumProperty(name="Unbevel", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Unchamfer = EnumProperty(name="Unbevel", items=op_context_items, default="INVOKE_DEFAULT")

    modal_TurnCorner = EnumProperty(name="Unbevel", items=op_context_items, default="INVOKE_DEFAULT")
    modal_QuadCorner = EnumProperty(name="Quad Corner", items=op_context_items, default="INVOKE_DEFAULT")

    modal_NormalFlatten = EnumProperty(name="Normal Flatten", items=op_context_items, default="INVOKE_DEFAULT")

    modal_Chamfer = EnumProperty(name="Chamfer", items=op_context_items, default="INVOKE_DEFAULT")
    modal_Offset = EnumProperty(name="Offset", items=op_context_items, default="INVOKE_DEFAULT")

    # MODAL UI

    modal_hud_scale = FloatProperty(name="HUD Scale", default=1, min=0.5, max=10)
    modal_hud_color = FloatVectorProperty(name="HUD Font Color", subtype='COLOR', default=[1, 1, 1], size=3, min=0, max=1)
    modal_hud_hints = BoolProperty(name="Show Hints", default=True)

    # PLUGs
    assetspath = StringProperty(name="Plug Libraries", subtype='DIR_PATH', default=os.path.join(MMpath, "assets", "Plugs"))

    pluglibsCOL = CollectionProperty(type=PlugLibsCollection)
    pluglibsIDX = IntProperty()

    newpluglibraryname = StringProperty(name="New Library Name")

    reverseplugsorting = BoolProperty(name="Reverse Plug Sorting (requires library reload or Blender restart)", default=False)

    libraryscale = FloatProperty(name="Size of Plug Libary Icons", default=0.7, min=0.5, max=1)
    plugsinlibraryscale = IntProperty(name="Size of Icons in Plug Libaries", default=4, min=1, max=20)

    showplugcount = BoolProperty(name="Show Plug Count next to Library Name", default=True)
    showplugbutton = BoolProperty(name="Show Plug Buttons below Libraries", default=True)
    showplugbuttonname = BoolProperty(name="Show Plug Name on Insert Button", default=False)
    showplugnames = BoolProperty(name="Show Plug Names in Plug Libraries", default=True)

    plugxraypreview = BoolProperty(name="Auto-X-Ray the plug and its subsets, when inserting Plug into scene", default=True)
    plugfadingwire = BoolProperty(name="Fading wire frames (experimental)", default=False)

    plugcreator = StringProperty(name="Plug Creator")


    def update_plugmode(self, context):
        if self.plugremovemode is True:
            self.plugmode = "REMOVE"
        else:
            self.plugmode = "INSERT"

    # hidden
    plugmode = EnumProperty(name="Plug Mode", items=plugmodeitems, default="INSERT")
    plugremovemode = BoolProperty(name="Remove Plugs", default=False, update=update_plugmode)


    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = column.box()

        if self.tabs == "GENERAL":
            self.draw_general_tab(box)
        elif self.tabs == "PLUGS":
            self.draw_plugs_tab(box)
        elif self.tabs == "ABOUT":
            self.draw_about_tab(box)

    def draw_general_tab(self, box):
        split = box.split()

        column = split.column()

        # KEYMAP

        self.draw_keymap_box(column)


        # MENU

        self.draw_menu_box(column)


        # SPLIT ########################

        column = split.column()


        # BEHAVIOR

        self.draw_behavior_box(column)


        # HUD

        self.draw_HUD_box(column)

    def draw_menu_box(self, column):
        col = column.box().column()

        row = col.split(percentage=0.39)
        row.label("")
        row.label("MESHmachine Menu")
        col.separator()

        row = col.row()
        row.prop(self, "show_in_specials_menu")
        row.label("Changing this requires restart", icon="INFO")
        col.separator()

        if 'mesh_looptools' in bpy.context.user_preferences.addons:
            col.prop(self, "show_looptools_wrappers")

        if self.keyboard_layout == "QWERTY":
            col.prop(self, "show_delete")
        else:
            col.prop(self, "show_mesh_split")

        col.separator()

        col.prop(self, "show_documentation")

    def draw_behavior_box(self, column):
        col = column.box().column()

        row = col.split(percentage=0.44)
        row.label("")
        row.label("Behavior")
        col.separator()

        row = col.row()
        row.label("Fuse")
        row.prop(self, "modal_Fuse", expand=True)

        row = col.row()
        row.label("Change Widh")
        row.prop(self, "modal_ChangeWidth", expand=True)

        row = col.row()
        row.label("Flatten")
        row.prop(self, "modal_Flatten", expand=True)

        row = col.row()
        row.label("Unf*ck")
        row.prop(self, "modal_Unfuck", expand=True)

        row = col.row()
        row.label("Unfuse")
        row.prop(self, "modal_Unfuse", expand=True)

        row = col.row()
        row.label("Refuse")
        row.prop(self, "modal_Refuse", expand=True)

        row = col.row()
        row.label("Unbevel")
        row.prop(self, "modal_Unbevel", expand=True)

        row = col.row()
        row.label("Unchamfer")
        row.prop(self, "modal_Unchamfer", expand=True)

        row = col.row()
        row.label("Turn Corner")
        row.prop(self, "modal_TurnCorner", expand=True)

        row = col.row()
        row.label("Quad Corner")
        row.prop(self, "modal_QuadCorner", expand=True)

        row = col.row()
        row.label("Normal Flatten")
        row.prop(self, "modal_NormalFlatten", expand=True)

        row = col.row()
        row.label("Chamfer")
        row.prop(self, "modal_Chamfer", expand=True)

        row = col.row()
        row.label("Offset")
        row.prop(self, "modal_Offset", expand=True)

    def draw_HUD_box(self, column):
        if any([op == "INVOKE_DEFAULT" for op in [self.modal_Fuse, self.modal_ChangeWidth, self.modal_Flatten, self.modal_Unfuck, self.modal_Unfuse, self.modal_Refuse, self.modal_Unbevel, self.modal_Unchamfer, self.modal_TurnCorner, self.modal_QuadCorner]]):
            col = column.box().column()

            row = col.split(percentage=0.45)
            row.label("")
            row.label("HUD")
            col.separator()

            row = col.row()

            row = col.split(percentage=0.3)
            row.prop(self, "modal_hud_scale")
            r = row.split(percentage=0.45)
            r.prop(self, "modal_hud_hints")
            r.label("Text Color:")
            r.prop(self, "modal_hud_color", text="")

    def draw_keymap_box(self, column):
        col = column.box().column()

        row = col.split(percentage=0.44)
        row.label("")
        row.label("Keymap")
        col.separator()

        row = col.row()
        row.prop(self, "keyboard_layout", expand=True)
        b = col.box()
        b.label("If you change the keyboard layout above, save the prefs and restart Blender.", icon="INFO")
        b.label("     This will remap the MESHmachine menu below, after the restart! X for QWERTY, Y for QWERTZ")
        col.separator()

        b = col.box()
        b.label("MESHmachine menus")

        # EDIT mode

        row = b.split(percentage=0.2)
        row.label("Mesh")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        kmi = dev.get_keymap_item(km, 'wm.call_menu', ("name", "machin3.mesh_machine_menu"))
        dev.draw_keymap_item(km, kmi, kc, row)
        b.separator()

        # OBJECT mode

        row = b.split(percentage=0.2)
        row.label("Object Mode")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Object Mode']
        kmi = dev.get_keymap_item(km, 'wm.call_menu', ("name", "machin3.mesh_machine_menu"))
        dev.draw_keymap_item(km, kmi, kc, row)


        # Symmetrize
        b = col.box()
        b.label("Symmetrize")

        row = b.split(percentage=0.2)
        row.label("X Axis")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        kmi = dev.get_keymap_item(km, 'machin3.symmetrize', ("axis", "X"))
        dev.draw_keymap_item(km, kmi, kc, row)

        row = b.split(percentage=0.2)
        row.label("Y Axis")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        kmi = dev.get_keymap_item(km, 'machin3.symmetrize', ("axis", "Y"))
        dev.draw_keymap_item(km, kmi, kc, row)

        row = b.split(percentage=0.2)
        row.label("Z Axis")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Mesh']
        kmi = dev.get_keymap_item(km, 'machin3.symmetrize', ("axis", "Z"))
        dev.draw_keymap_item(km, kmi, kc, row)

    def draw_plugs_tab(self, box):
        split = box.split()

        column = split.column()

        # PLUG LIBRARY

        self.draw_plug_library_box(column)


        column = split.column()

        # PLUG SETTINGS

        self.draw_plug_settings_box(column)

    def draw_plug_library_box(self, column):
        col = column.box().column()

        row = col.split(percentage=0.42)
        row.label("")
        row.label("Plug Libraries")
        col.separator()

        col.prop(self, "assetspath", text="Location")
        column.separator()

        row = col.row()
        rows = len(self.pluglibsCOL) if len(self.pluglibsCOL) > 6 else 6
        row.template_list("PlugLibsUIList", "", self, "pluglibsCOL", self, "pluglibsIDX", rows=rows)

        c = row.column(align=True)
        c.operator("machin3.move_plug_library", text="", icon="TRIA_UP").direction = "UP"
        c.operator("machin3.move_plug_library", text="", icon="TRIA_DOWN").direction = "DOWN"
        c.separator()
        c.operator("machin3.clear_plug_libraries", text="", icon="LOOP_BACK")
        c.operator("machin3.reload_plug_libraries", text="", icon="FILE_REFRESH")
        c.separator()
        c.operator("machin3.open_plug_library", text="", icon="FILE_FOLDER")
        c.operator("machin3.rename_plug_library", text="", icon="OUTLINER_DATA_FONT")
        c.operator("machin3.remove_plug_library", text="", icon="CANCEL")

        row = col.row()
        row.prop(self, "newpluglibraryname")
        row.operator("machin3.add_plug_library", text="", icon="ZOOMIN")

    def draw_plug_settings_box(self, column):
        col = column.box().column()

        row = col.split(percentage=0.42)
        row.label("")
        row.label("Plug Settings")
        col.separator()

        col.prop(self, "reverseplugsorting")

        col.separator()

        row = col.row()
        row.prop(self, "libraryscale")
        row.prop(self, "plugsinlibraryscale")

        col.separator()

        col.prop(self, "showplugcount")
        row = col.row()
        # row.prop(self, "showplugbutton")
        if self.showplugbutton:
            row.prop(self, "showplugbuttonname")
        row.prop(self, "showplugnames")

        col.separator()

        col.prop(self, "plugxraypreview")
        col.prop(self, "plugfadingwire")

        col.separator()

        col.prop(self, "plugcreator")

    def draw_about_tab(self, box):
        column = box.column()

        for idx, (text, url, icon) in enumerate(links):
            if idx % 2 == 0:
                row = column.row()
                if text == "":
                    row.separator()
                else:
                    row.operator("wm.url_open", text=text, icon=icon).url = url
            else:
                if text == "":
                    row.separator()
                else:
                    row.operator("wm.url_open", text=text, icon=icon).url = url


MESHmachine_keys = []


def register():
    bpy.utils.register_module(__name__)
    print("Registered %s %s with %d modules" % (bl_info["name"], str(bl_info['version']).replace(", ", "."), len(modules)))

    register_and_load_plugs()

    # populate specials menus
    if m3.MM_prefs().show_in_specials_menu:
        bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(specials_menu)
        bpy.types.VIEW3D_MT_object_specials.prepend(specials_menu)

    global MESHmachine_keys
    MESHmachine_keys = register_keymaps()

    bpy.types.Object.MM = PointerProperty(type=MMObjectProperties)
    bpy.types.Scene.MM = PointerProperty(type=MMSceneProperties)

    # register callback
    bpy.app.handlers.scene_update_post.append(scene_update_handler)


def unregister():
    unregister_and_unload_plugs()

    # unregister callbacks
    bpy.app.handlers.scene_update_post.remove(scene_update_handler)

    global MESHmachine_keys
    for km, kmi in MESHmachine_keys:
        km.keymap_items.remove(kmi)

    MESHmachine_keys.clear()

    bpy.utils.unregister_module(__name__)
