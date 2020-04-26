import bpy
import os
import shutil
import platform
from bpy.props import CollectionProperty, IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty
from zipfile import ZipFile
from . properties import DecalLibsCollection
from . utils.registration import get_path, get_name, reload_decal_libraries, get_addon
from . utils.ui import get_icon, popup_message, draw_keymap_items
from . utils.system import makedir, abspath, get_PIL_image_module_path, validate_zip_library
from . utils.library import get_lib
from . items import prefs_tab_items, prefs_newlibmode_items, prefs_decalmode_items


class DECALmachinePreferences(bpy.types.AddonPreferences):
    path = get_path()
    bl_idname = get_name()


    # DECAL LIBRARIES

    def update_assetspath(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        newpath = makedir(abspath(self.assetspath))
        oldpath = abspath(self.oldpath)

        if newpath != oldpath:
            print(" » Copying Decal Libraries from %s to %s" % (oldpath, newpath))

            libs = sorted([f for f in os.listdir(oldpath) if os.path.isdir(os.path.join(oldpath, f))])

            for lib in libs:
                src = os.path.join(oldpath, lib)
                dest = os.path.join(newpath, lib)

                if not os.path.exists(dest):
                    print("  » %s" % (lib))
                    shutil.copytree(src, dest)

            # set the new oldpath
            self.oldpath = newpath

            # make sure the chose assetspath is absolute
            self.avoid_update = True
            self.assetspath = newpath

            # reload assets
            reload_decal_libraries()

    def update_importdecallibpath(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        if self.importdecallibpath.strip():
            path = abspath(self.importdecallibpath)

            msg = ""

            if path and os.path.exists(path):
                if os.path.isdir(path) and os.path.exists(os.path.join(path, ".is280")):
                    lib = os.path.basename(path)
                    # print("%s is a 280 decal library (folder)" % (lib))
                    dst = os.path.join(self.assetspath, lib)

                    if os.path.exists(dst):
                        msg = "A Decal Library called '%s' exists already." % (lib)

                    else:
                        # print("importing library %s to %s" % (lib, dst))
                        shutil.copytree(path, dst)

                        reload_decal_libraries()

                elif not os.path.isdir(path) and os.path.splitext(path)[1].lower() == ".zip":
                    with ZipFile(path, mode="r") as z:
                        lib = validate_zip_library(z.namelist())

                        if lib:
                            # print("%s is a 280 decal library (zipped)" % (os.path.basename(path)))
                            dst = os.path.join(self.assetspath, lib)

                            if os.path.exists(dst):
                                msg = "A Decal Library called '%s' exists already." % (lib)

                            else:
                                # print("importing library %s to %s" % (lib, dst))
                                z.extractall(path=self.assetspath)

                                reload_decal_libraries()

                        else:
                            msg = "%s is not a valid zipped Decal Library!" % (os.path.basename(path))
                else:
                    msg = "%s is not a valid Decal Library!" % (os.path.basename(path))

            else:
                msg = "Path '%s' does not exist." % (os.path.basename(path))

            if msg:
                popup_message(msg, title="Decal Library could not be imported")


        self.avoid_update = True
        self.importdecallibpath = ""

    def update_newdecallibraryname(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        assetspath = self.assetspath
        name = self.newdecallibraryname.strip()

        if name:
            if os.path.exists(os.path.join(assetspath, name)):
                popup_message("This library exists already, choose another name!", title="Failed to add library", icon="ERROR")
            else:
                libpath = makedir(os.path.join(assetspath, name))

                print(" » Created decal library folder '%s'" % (libpath))

                with open(os.path.join(libpath, ".is280"), "w") as f:
                    f.write("")


                self.avoid_update = True
                self.newdecallibraryname = ""

                reload_decal_libraries()

    assetspath: StringProperty(name="Decal Libraries", subtype='DIR_PATH', default=os.path.join(path, "assets", "Decals"), update=update_assetspath)
    oldpath: StringProperty(name="Old Path", subtype='DIR_PATH', default=os.path.join(path, "assets", "Decals"))

    decallibsCOL: CollectionProperty(type=DecalLibsCollection)
    decallibsIDX: IntProperty()

    newlibmode: EnumProperty(name="New Library Mode", items=prefs_newlibmode_items, description="Choose whether to Import or create a new Empty Library", default="IMPORT")
    importdecallibpath: StringProperty(name="Import Decal Library", description="Choose a Folder or .zip File to load a Decal Library from", subtype='FILE_PATH', default="", update=update_importdecallibpath)
    newdecallibraryname: StringProperty(name="New Library Name", description="Enter a name to create a new empty Decal Library", update=update_newdecallibraryname)

    reversedecalsorting: BoolProperty(name="Reverse Decal Sorting (requires library reload or Blender restart)", default=False)
    libraryrows: IntProperty(name="Rows of libraries in the Pie Menu", default=2, min=1)
    libraryoffset: IntProperty(name="Offset libraries to the right or left side of the Pie Menu", default=0)
    libraryscale: IntProperty(name="Size of Decal Library Icons", default=4, min=1, max=20)
    decalsinlibraryscale: IntProperty(name="Size of Icons in Decal Libraries", default=4, min=1, max=20)

    showdecalcount: BoolProperty(name="Show Decal Count next to Library Name", default=False)
    showdecalnames: BoolProperty(name="Show Decal Names in Decal Libraries", default=False)
    showdecalbuttonname: BoolProperty(name="Show Decal Name on Insert Button", default=False)

    decalcreator: StringProperty(name="Decal Creator", default="MACHIN3 - machin3.io, @machin3io")


    # MODAL UI

    modal_hud_scale: FloatProperty(name="HUD Scale", default=1, min=0.5, max=10)
    modal_hud_color: FloatVectorProperty(name="HUD Font Color", subtype='COLOR', default=[1, 1, 1], size=3, min=0, max=1)
    modal_hud_hints: BoolProperty(name="Show Hints", default=True)


    # hidden

    def update_tabs(self, context):
        if self.tabs == "ABOUT":
            self.addons_MESHmachine = get_addon('MESHmachine')[0]
            self.addons_MACHIN3tools = get_addon('MACHIN3tools')[0]
            self.addons_GrouPro = get_addon('Group Pro')[0]
            self.addons_BatchOps = get_addon('Batch Operations™')[0]
            self.addons_HardOps = get_addon('Hard Ops 9')[0]
            self.addons_BoxCutter = get_addon('BoxCutter')[0]

    tabs: EnumProperty(name="Tabs", items=prefs_tab_items, default="GENERAL", update=update_tabs)

    def update_decalmode(self, context):
        if self.decalremovemode is True:
            self.decalmode = "REMOVE"
        else:
            self.decalmode = "INSERT"

    decalmode: EnumProperty(name="Decal Mode", items=prefs_decalmode_items, default="INSERT")
    decalremovemode: BoolProperty(name="Remove Decals", default=False, update=update_decalmode, description="Enable Decal Removal Mode. This Permanently Deletes Decals from the Hard Drive.")

    pil: BoolProperty(name="PIL", default=False)
    pilrestart: BoolProperty(name="PIL restart", default=False)
    showpildetails: BoolProperty(name="Show PIL details", default=False)

    check_for_updates: BoolProperty(name="Check for Updates", default=True)
    update_available: BoolProperty(name="Update is available", default=False)

    addons_MESHmachine: BoolProperty(default=False)
    addons_MACHIN3tools: BoolProperty(default=False)
    addons_GrouPro: BoolProperty(default=False)
    addons_BatchOps: BoolProperty(default=False)
    addons_HardOps: BoolProperty(default=False)
    addons_BoxCutter: BoolProperty(default=False)

    avoid_update: BoolProperty(default=False)


    def draw(self, context):
        layout=self.layout

        column = layout.column()
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = column.box()

        if self.tabs == "GENERAL":
            self.draw_general_tab(box)

        elif self.tabs == "CREATE":
            self.draw_create_tab(box)

        elif self.tabs == "ABOUT":
            self.draw_about_tab(box)


    # TABS

    def draw_general_tab(self, box):
        split = box.split()

        # LEFT

        b = split.box()
        b.label(text="Decal Libraries")

        self.draw_assets_path(b)

        self.draw_decal_libraries(b)


        # RIGHT

        b = split.box()
        b.label(text="Settings")

        self.draw_keymaps(b)

        self.draw_asset_loaders(b)

        self.draw_HUD(b)

        self.draw_updates(b)

    def draw_create_tab(self, box):
        split = box.split()

        # LEFT
        b = split.box()
        b.label(text="PIL - Python Imaging Library")

        self.draw_pil(b)


        # RIGHT
        b = split.box()
        b.label(text="Decal Creation Settings")

        self.draw_decal_creation(b)

    def draw_about_tab(self, box):
        split = box.split()

        # LEFT
        b = split.box()
        b.label(text="MACHIN3")

        self.draw_machin3(b)


        # RIGHT
        b = split.box()
        b.label(text="Recommended")
        self.draw_recommended(b)


    # GENERAL

    def draw_assets_path(self, layout):
        box = layout.box()
        column = box.column()

        row = column.row(align=True)
        row.prop(self, "assetspath", text="Location")
        row.operator("machin3.reset_decals_location", text="", icon="LOOP_BACK")

    def draw_decal_libraries(self, layout):
        box = layout.box()
        box.label(text="Libraries")

        column = box.column()

        row = column.row()

        col = row.column(align=True)
        col.template_list("MACHIN3_UL_decal_libs", "", self, "decallibsCOL", self, "decallibsIDX", rows=max(len(self.decallibsCOL), 6))

        col = row.column(align=True)
        col.operator("machin3.move_decal_library", text="", icon="TRIA_UP").direction = "UP"
        col.operator("machin3.move_decal_library", text="", icon="TRIA_DOWN").direction = "DOWN"
        col.separator()
        col.operator("machin3.rename_decal_library", text="", icon="OUTLINER_DATA_FONT")
        col.separator()
        col.operator("machin3.clear_decal_libraries", text="", icon="LOOP_BACK")
        col.operator("machin3.reload_decal_libraries", text="", icon_value=get_icon("refresh"))
        col.separator()

        _, _, active = get_lib()
        icon = "cancel" if active and not active.islocked else "cancel_grey"
        col.operator("machin3.remove_decal_library", text="", icon_value=get_icon(icon))

        row = column.split(factor=0.3)
        r = row.row()
        r.prop(self, "newlibmode", expand=True)

        if self.newlibmode == 'IMPORT':
            r = row.split(factor=0.25)
            r.label(text="Folder or .zip")
            r.prop(self, "importdecallibpath", text="")
        else:
            r = row.split(factor=0.25)
            r.label(text="Name")
            r.prop(self, "newdecallibraryname", text="")

    def draw_keymaps(self, layout):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        from . keys import keys as keysdict

        box = layout.box()
        box.label(text="Keymaps")

        column = box.column()

        for name, keylist in keysdict.items():
            draw_keymap_items(kc, name, keylist, column)

    def draw_asset_loaders(self, layout):
        box = layout.box()
        box.label(text="Asset Loaders")

        column = box.column()

        row = column.split(factor=0.1)
        row.prop(self, "libraryrows", text="")
        row.label(text="Rows of Libraries in the Pie Menu")

        row = column.split(factor=0.1)
        row.prop(self, "libraryoffset", text="")
        row.label(text="Offset Libraries to right or left side in the Pie Menu")

        row = column.split(factor=0.1)
        row.prop(self, "libraryscale", text="")
        row.label(text="Size of Decal Library Icons")

        row = column.split(factor=0.1)
        row.prop(self, "decalsinlibraryscale", text="")
        row.label(text="Size of Icons in Decal Libraries")

        row = column.split(factor=0.1)
        row.prop(self, "reversedecalsorting", text="True" if self.reversedecalsorting else "False", toggle=True)
        r = row.split(factor=0.3)
        r.label(text="Reverse Decal Sorting")
        r.label(text="reqiures library reload or Blender restart", icon='INFO')

        row = column.split(factor=0.1)
        row.prop(self, "showdecalcount", text="True" if self.showdecalcount else "False", toggle=True)
        row.label(text="Show Decal Count next to Library Name")

        row = column.split(factor=0.1)
        row.prop(self, "showdecalnames", text="True" if self.showdecalnames else "False", toggle=True)
        row.label(text="Show Decal Names in Decal Libraries")

        row = column.split(factor=0.1)
        row.prop(self, "showdecalbuttonname", text="True" if self.showdecalbuttonname else "False", toggle=True)
        row.label(text="Show Decal Name on Insert Buttons")

    def draw_HUD(self, layout):
        box = layout.box()
        box.label(text="HUD")

        column = box.column()

        row = column.row()

        rs = row.split(factor=0.35)
        rs.prop(self, "modal_hud_hints", text="True" if self.modal_hud_hints else "False", toggle=True)
        rs.label(text="Show Hints")

        rs = row.split(factor=0.35)
        rs.prop(self, "modal_hud_scale", text="")
        rs.label(text="HUD Scale")

        rs = row.split(factor=0.35)
        rs.prop(self, "modal_hud_color", text="")
        rs.label(text="HUD Color")

    def draw_updates(self, layout):
        box = layout.box()
        box.label(text="Update Checks")

        column = box.column()

        row = column.split(factor=0.1)
        row.prop(self, "check_for_updates", text="True" if self.check_for_updates else "False", toggle=True)

        r = row.split(factor=0.4)
        r.label(text="Check if an Update has been released.")
        r.label(text="Once a day, requires internet connection", icon='INFO')


    # DECAL CREATION

    def draw_pil(self, layout):
        box = layout.box()
        column = box.column()
        column.scale_y = 1.2

        if self.pil:
            row = column.row()
            row.label(text="PIL is installed.", icon_value=get_icon("save"))

            icon = 'TRIA_DOWN' if self.showpildetails else 'TRIA_LEFT'
            row.prop(self, "showpildetails", text="", icon=icon)

            if self.showpildetails:
                path = get_PIL_image_module_path()
                if path:
                    column.label(text=path, icon='MONKEY')

                row = column.row()
                row.operator("machin3.purge_pil", text="Purge PIL", icon_value=get_icon('cancel'))


        elif self.pilrestart:
            column.label(text="PIL has been installed. Please restart Blender now.", icon="INFO")

        else:
            row = column.split(factor=0.2)
            row.operator("machin3.install_pil", text="Install PIL", icon="PREFERENCES")
            row.label(text="PIL is needed for Decal Creation and Export. Internet connection required.")

            column.separator()

            box = column.box()
            box.label(text="Alternative Installation Methods")

            col = box.column(align=True)
            col.label(text="If you've used the Install button above, but are not seeing a green checkmark,")
            col.label(text="even after a Blender restart, you can try the following alternative installation methods.")

            if platform.system() == "Windows":
                b = col.box()
                r = b.row()
                r.label(text="Windows users, purge PIL now.")
                r.operator("machin3.purge_pil", text="Purge PIL", icon_value=get_icon('cancel'))

            elif platform.system() == "Darwin" and "AppTranslocation" in bpy.app.binary_path:
                b = col.box()
                b.label(text="Warning", icon_value=get_icon("error"))
                c = b.column()

                c.label(text="Blender is not properly installed, AppTranslocation is enabled.")
                c.label(text="Please refer to Blender's 'Installing on macOS' instructions.")
                c.label(text="Note that, for dragging of files and folders, you need to hold down the command key.")

                r = c.row()
                r.operator("wm.url_open", text="Installing on macOS").url = "https://docs.blender.org/manual/en/dev/getting_started/installing/macos.html"
                r.operator("wm.url_open", text="additional Information").url = "https://machin3.io/DECALmachine/docs/installation/#macos"

            col.label(text="Make sure to either run Blender as Administrator or at least have write access to the Blender folder.")
            col.label(text="Restart Blender, if the green checkmark doesn't show, after pressing either button.")

            row = col.row()
            row.operator("machin3.install_pil_admin", text="Install PIL (Admin)", icon="PREFERENCES")
            row.operator("machin3.easy_install_pil_admin", text="Easy Install PIL (Admin)", icon="PREFERENCES")

    def draw_decal_creation(self, layout):
        box = layout.box()
        column = box.column()

        row = column.split(factor=0.3)
        row.label(text="Decal Creator")
        row.prop(self, "decalcreator", text="")

        row = column.split(factor=0.3)
        row.label()
        row.label(text="Change this, so Decals created by you, are tagged with your info!", icon="INFO")


    # ABOUT

    def draw_machin3(self, layout):
        installed = get_icon('save')
        missing = get_icon('cancel_grey')

        box = layout.box()
        box.label(text="Blender Addons")
        column = box.column()

        row = column.split(factor=0.3)
        row.scale_y = 1.2
        row.label(text="DECALmachine", icon_value=installed)
        r = row.split(factor=0.2)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://decal.machin3.io"
        r.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/DECALmachine"
        r.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/DECALmachine"


        row = column.split(factor=0.3)
        row.scale_y = 1.2
        row.label(text="MESHmachine", icon_value=installed if self.addons_MESHmachine else missing)
        r = row.split(factor=0.2)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://mesh.machin3.io"
        r.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/MESHmachine"
        r.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/MESHmachine"


        row = column.split(factor=0.3)
        row.scale_y = 1.2
        row.label(text="MACHIN3tools", icon_value=installed if self.addons_MACHIN3tools else missing)
        r = row.split(factor=0.2)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://machin3.io/MACHIN3tools"
        r.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/MACHIN3tools"
        r.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/MACHIN3tools"


        box = layout.box()
        box.label(text="DECALmachine Documentation")

        column = box.column()
        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Docs", icon='INFO').url = "https://machin3.io/DECALmachine/docs"
        row.operator("wm.url_open", text="Youtube", icon='FILE_MOVIE').url = "https://www.youtube.com/playlist?list=PLcEiZ9GDvSdWiU2BPQp99HglGGg1OGiHs"
        row.operator("wm.url_open", text="FAQ", icon='QUESTION').url = "https://machin3.io/DECALmachine/docs/faq"
        row.operator("machin3.get_decalmachine_support", text="Get Support", icon='GREASEPENCIL')


        box = layout.box()
        box.label(text="DECALmachine Discussion")

        column = box.column()
        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Blender Artists", icon="COMMUNITY").url = "https://blenderartists.org/t/decalmachine/688181"
        row.operator("wm.url_open", text="polycount", icon="COMMUNITY").url = "https://polycount.com/discussion/210294/blender-decalmachine-surface-detailing-using-mesh-decals"

        box = layout.box()
        box.label(text="Follow my work")

        column = box.column()
        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Web").url = "https://machin3.io"
        row.operator("wm.url_open", text="Twitter @machin3io").url = "https://twitter.com/machin3io"
        row.operator("wm.url_open", text="Twitter #DECALmachine").url = "https://twitter.com/search?q=%23DECALmachine"
        row.operator("wm.url_open", text="Artstation").url = "https://artstation.com/machin3"

    def draw_recommended(self, layout):
        installed = get_icon('save')
        missing = get_icon('cancel_grey')

        box = layout.box()
        box.label(text="Bartosz Styperek")
        column = box.column()

        row = column.split(factor=0.2)
        row.scale_y = 1.2
        row.label(text="Group Pro", icon_value=installed if self.addons_GrouPro else missing)
        rs = row.split(factor=0.3)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://bartoszstyperek.wordpress.com/"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/JoseConseco3"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/GroupPro"


        box = layout.box()
        box.label(text="moth3r & dairin0d")
        column = box.column()

        row = column.split(factor=0.2)
        row.scale_y = 1.2
        row.label(text="Batch Operations™", icon_value=installed if self.addons_BatchOps else missing)
        rs = row.split(factor=0.3)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://batchops.moth3r.com"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/moth3r"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/batchops"
        rs.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/batchops"


        box = layout.box()
        box.label(text="masterxeon1001 & TeamC")
        column = box.column()

        row = column.split(factor=0.2)
        row.scale_y = 1.2
        row.label(text="Hard Ops 9", icon_value=installed if self.addons_HardOps else missing)
        rs = row.split(factor=0.3)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://masterxeon1001.com"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/mxeon1001"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/hardops"
        rs.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/hardopsofficial"

        row = column.split(factor=0.2)
        row.scale_y = 1.2
        row.label(text="BoxCutter", icon_value=installed if self.addons_BoxCutter else missing)
        rs = row.split(factor=0.3)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://masterxeon1001.com"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/mxeon1001"
        c = rs.column()
        c.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/BoxCutter/congrats_DM_release"
        c.label(text="Limited Promo Link!", icon='INFO')
        rs.operator("wm.url_open", text="Blender Market", icon='URL').url = "https://blendermarket.com/products/boxcutter"


        box = layout.box()
        box.label(text="Decal Resources")
        column = box.column()

        row = column.split(factor=0.4)
        row.scale_y = 1.2
        row.label(text="Paweł Łyczkowski: Stencil Kit - Industrial")
        rs = row.split(factor=0.45)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "http://plyczkowski.com"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/PLyczkowski"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/dVVp"

        row = column.split(factor=0.4)
        row.scale_y = 1.2
        row.label(text="Antoine Collignon: 40 Sci-Fi Decals 2017")
        rs = row.split(factor=0.45)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Web", icon='URL').url = "https://www.antoinecollignon.com/"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/omegear"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/SciFiDecals"

        row = column.split(factor=0.4)
        row.scale_y = 1.2
        row.label(text="Maciej Sobolewski: 70+ Sci-Fi Decals Atlas")
        rs = row.split(factor=0.45)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Instagram", icon='URL').url = "https://www.instagram.com/sobolevsky/"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/msobolewskiart"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/xNYG"

        row = column.split(factor=0.4)
        row.scale_y = 1.2
        row.label(text="Piotr Jedziński: 200+ Decals")
        rs = row.split(factor=0.45)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Artstation", icon='URL').url = "https://radi0n.artstation.com"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/radi0n"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/iqcqW"

        row = column.split(factor=0.4)
        row.scale_y = 1.2
        row.label(text="Tony Leonard: TL-MX Set 01")
        rs = row.split(factor=0.45)
        r = rs.row(align=True)
        r.operator("wm.url_open", text="Instagram", icon='URL').url = "https://www.instagram.com/tonikoro/"
        r.operator("wm.url_open", text="Twitter", icon='URL').url = "https://twitter.com/tonikorostudios"
        rs.operator("wm.url_open", text="Gumroad", icon='URL').url = "https://gumroad.com/l/TLMXset01"
