'''
    Copyright (C) 2017 MACHIN3, machin3.io, decal@machin3.io

    DECALmachine Program created by MACHIN3, AR, MX

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

    DECALmachine Assets, such as Decal textures and Sample Scenes created by MACHIN3

        Decal Assets may not be distributed or sub-licensed to third partys
        unless permission is specifically granted.

    Parallax Nodetree originally by zelouille, ported by Vsevolod Ochinskiy and used with permission:
    https://blenderartists.org/forum/showthread.php?314083-Cycles-parallax-step-mapping-with-nodes

    The core of the Atlas Class - Atlas.create_atlas() in operators/atlas.py is based on the Atlas
    implementation of the Kivy project. See https://github.com/kivy/kivy/blob/master/kivy/export.py

    Copyright and Permission notice:

        Copyright (c) 2010-2017 Kivy Team and other contributors

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in
        all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
        THE SOFTWARE.

    In the Kivy code, there's also this attribution:

        Thanks to
        omnisaurusgames.com/2011/06/texture-atlas-generation-using-python/
        for its initial implementation.

    The js packing algorithm in Atlas.js_pack() in operators/export.py is based on work by Jim Scott.
    See http://blackpawn.com/texts/lightmaps/default.html
'''

bl_info = {
    "name": "DECALmachine",
    "author": "MACHIN3, AR, MX",
    "version": (1, 4, "2a"),
    "blender": (2, 80, 0),
    "location": "Pie Menus: D, CTRL + ALT + SHIFT + D and CTRL + ALT + SHIFT + E",
    "description": "A complete mesh-based decal pipeline. Project decals, cut decal panel strips, create your own decals, export decals to a number of engines or bake them down.",
    "warning": "",
    "wiki_url": "https://decal.machin3.io",
    "tracker_url": "https://machin3.io/DECALmachine/docs/faq/#reporting-errors-or-problems",
    "category": "Learnbgame",
    }

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, IntProperty, EnumProperty
from . assets.previews_decals01 import register_and_load_decals01, unregister_and_unload_decals01
from . assets.previews_decals02 import register_and_load_decals02, unregister_and_unload_decals02
from . assets.previews_info01 import register_and_load_info01, unregister_and_unload_info01
from . assets.previews_paneling01 import register_and_load_paneling01, unregister_and_unload_paneling01
from . import developer_utils as du
from . import M3utils as m3
from . utils.operators import load_json

modules = du.setup_addon_modules(__path__, __name__, "bpy" in locals())


def get_paneling():
    DMpath = __path__[0]
    panelingpath = os.path.join(DMpath, "operators", "paneling.json")

    try:
        panelinglist = load_json(panelingpath)

        tuplelist = []
        for p in panelinglist:
            tuplelist.append((p[0], p[1], ""))
    except:
        tuplelist = [("paneling01_01", "paneling01_01", ""),
                     ("paneling01_02", "paneling01_02", ""),
                     ("paneling01_03", "paneling01_03", ""),
                     ("paneling01_04", "paneling01_04", ""),
                     ("paneling01_05", "paneling01_05", ""),
                     ("paneling01_06", "paneling01_06", ""),
                     ("paneling01_07", "paneling01_07", ""),
                     ("paneling01_08", "paneling01_08", "")]

    return sorted(tuplelist, reverse=True)


def get_exporttypes():
    tuplelist = [("DECALBakeDown", "DECALBakeDown", ""),
                 ("unity3d_bac9_packed_advanced", "Unity3D (Bac9 Packed Advanced)", ""),
                 ("unity3d_machin3", "Unity3D (MACHIN3)", ""),
                 ("unpacked", "Unpacked", ""),
                 ("unreal_engine_4", "Unreal Engine 4", ""),
                 ("sketchfab", "Sketchfab", ""),
                 ("substance_painter", "Substance Painter", "")]

    return sorted(tuplelist, reverse=True)

preferences_tabs = [("general", "General", ""),
                    ("keymaps", "Keymaps", ""),
                    ("create", "Create", ""),
                    ("export", "Export", ""),
                    ("about", "About", "")]


links = [("Buy DECALmachine @ Gumroad", "https://gumroad.com/l/DECALmachine", "NONE"),
         ("Buy DECALmachine @ Blender Market", "https://www.blendermarket.com/products/DECALmachine", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("Documentation", "https://machin3.io/DECALmachine/docs/", "INFO"),
         ("MACHINƎ.io", "https://machin3.io", "WORLD"),
         ("Report Errors or Problems", "https://machin3.io/DECALmachine/docs/faq/#reporting-errors-or-problems", "ERROR"),
         ("FAQ", "https://machin3.io/DECALmachine/docs/faq/", "QUESTION"),
         ("Youtube", "https://www.youtube.com/channel/UC4yaFzFDILd2yAqOWRuLOvA", "NONE"),
         ("Twitter", "https://twitter.com/machin3io", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("DECALmachine @ BlenderArtists", "https://blenderartists.org/forum/showthread.php?420355-Addon-DECALmachine", "NONE"),
         ("DECALmachine @ Polycount", "http://polycount.com/discussion/186089/blender-decal-machine-a-quick-way-to-create-decals-for-hard-surface", "NONE"),
         ("", "", ""),
         ("", "", ""),
         ("Get MACHIN3tools @ GitHub", "https://github.com/machin3io/MACHIN3tools", "NONE"),
         ("MACHINƎ @ Artstation", "https://www.artstation.com/artist/machin3", "NONE"),
         ]


class DecalSettings(bpy.types.PropertyGroup):
    debugmode = BoolProperty(name="Debug Mode", default=False)
    removemode = BoolProperty(name="Remove Decal Mode", default=False)
    extraoptions = BoolProperty(name="Extra Options", default=False)
    globalparallax = BoolProperty(name="Global Parallax", default=True)
    globalglossy = BoolProperty(name="Global Glossy", default=True)
    defaultpaneling = bpy.props.EnumProperty(name='Slice/Knife default material', items=get_paneling(), default="paneling01_01")

    # glossy shader defaults
    templatecolor = FloatVectorProperty(name="", subtype='COLOR', default=[0.35, 0.35, 0.35])
    templaterough = FloatProperty(name="Roughness", min=0, max=1, default=0.2)

    # decal creation defaults
    createheightcontrast = FloatProperty(name="Height Contrast", min=0.1, max=2, default=1)
    createparallaxvalue = FloatProperty(name="Parallax Value", min=-0.2, max=-0.01, default=-0.1)
    createreplacelast = BoolProperty(name="Repl. Last", default=False)
    createaosamples = IntProperty(name="AO Samples", default=7)

    # atlas creation defaults
    atlasdownsample = BoolProperty(name="Downsample Atlas", default=False)
    atlaspadding = IntProperty(name="Padding", default=-1, min=0, max=10)  # we initiate it at -1 so it can be fetched from prefs
    atlastype = StringProperty(name="Atlas Type", default="")
    maptype = StringProperty(name="Map Type", default="")

    # atlasing and export defaults
    autoopenfolderforexistingatlas = BoolProperty(name="Open Atlas Folder for Existing Atlas Solution", default=True)
    autoinitiateafterreset = BoolProperty(name="Initiate new Atlas when Resetting", default=False)
    autoopenfolderafterexport = BoolProperty(name="Open Export Folder after Exporting", default=True)

    exporttype = EnumProperty(name='Export to Target Platform', items=get_exporttypes(), default="unity3d_machin3")
    quickexport = BoolProperty(name="Quick Export", default=True)
    exportname = StringProperty(name="", default="Untitled")

    simpleexportgroup = BoolProperty(name="Simple Export Group", default=False)
    createnondecalsgroup = BoolProperty(name="Create 'DM_non-decals' Group", default=True)
    removedisplace = BoolProperty(name="Ignore Decal Heights", default=False)

    extradisplace = BoolProperty(name="Extra Displ.", default=True)
    extradisplaceamnt = FloatProperty(name="Amount", default=2, min=0, max=10)
    createarchive = BoolProperty(name=" » Create Archive", default=True)

    extrasbsatlas = BoolProperty(name="Extra Substance Atlas", default=False)
    parenttoroot = BoolProperty(name="Parent Objects to Root", default=True)
    unityrotfix = BoolProperty(name=" » Unity Rotation Fix (experimental)", default=True)
    triangulize = BoolProperty(name="Triangulize", default=True)
    normalflipgreen = BoolProperty(name="Flip Green Normal", default=False)
    assignuniquematerials = BoolProperty(name="Assign Unique Materials", default=False)
    treatfreestyleasseam = BoolProperty(name=" » Treat Freestyle edges as Seams", default=False)

    # DECALBakeDown
    bakedownexportfbx = BoolProperty(name="Export FBX", default=True)
    bakedownresolution = IntProperty(name="Resolution", default=1024, min=64, max=8192)
    bakedowndistance = FloatProperty(name="Distance", default=0.01, min=0, max=10)
    bakedownbias = FloatProperty(name="Bias", default=0.01, min=0, max=10)
    bakedowntransfersharps = BoolProperty(name="Transfer Sharps", default=False)
    bakedowncombine = BoolProperty(name="Combine Bakes (per Material)", default=True)
    bakedowncombineall = BoolProperty(name=" » Combine all-to-one", default=False)

    bakedownmapao = BoolProperty(name="Ambient Occlusion", default=True)
    bakedownmapcurvature = BoolProperty(name="Curvature", default=True)
    bakedownmapheight = BoolProperty(name="Height", default=True)
    bakedownmapnormal = BoolProperty(name="Normal", default=True)
    bakedownmapsubset = BoolProperty(name="Subset Mask", default=True)
    bakedownmapcolor = BoolProperty(name="Color", default=True)
    bakedownsbsnaming = BoolProperty(name="Substance Naming", default=True)

    # wstep
    wstepremovesharps = BoolProperty(name="(W)Step - Remove Sharps", default=True)


class DECALmachinePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    tabs = bpy.props.EnumProperty(name="Tabs", items=preferences_tabs, default="general")

    useAMpath = BoolProperty(name="Use Asset Management Assets path", default=False)
    useDMassetloader = BoolProperty(name="Use built-in Asset Loader (highly recommended)", default=True)

    DMpath = __path__[0]

    DMassetpath = StringProperty(name="Decal Library", subtype='DIR_PATH', default=os.path.join(DMpath, "assets", "Decals"))
    DMcustomassetpath = StringProperty(name="Custom Decal Library", subtype='DIR_PATH', default=os.path.join(DMpath, "assets", "CustomDecals"))
    DMexportpath = StringProperty(name="Export Path", subtype='DIR_PATH', default=os.path.join(DMpath, "assets", "export"))

    # Asset Management check to see if it's installed first and then to see if it's activated before DM(otherwise its asset path can't be accessed)
    AMfirst = False
    if m3.AM_check():
        try:  # if the path can be retrieved, all is good
            AMpath = m3.get_AM_library_path()
            AMfirst = True
        except:  # if it can't then AM has been activated after DM, in which case the AM path can't be used at the time of registration
            AMfirst = False

    if AMfirst:
        path = os.path.join(AMpath, "assets", "Decals")
        custompath = os.path.join(AMpath, "assets", "CustomDecals")
        if os.path.exists(path):
            AMassetpath = StringProperty(name="Asset Management Decal Assets Path", subtype='DIR_PATH', default=path)
            AMcustomassetpath = StringProperty(name="Asset Management Custom Decal Assets Path", subtype='DIR_PATH', default=custompath)
        else:
            AMassetpath = AMcustomassetpath = "No 'Decals' and 'CustomDecals' libraries found in Asset Manager assets path."

    assetpath = DMassetpath
    customassetpath = DMcustomassetpath

    autocycles = BoolProperty(name="Ensure Cycles is the Renderer, when inserting Decals", default=True)
    automaterialshading = BoolProperty(name="Automatically switch to Material Shading, when inserting Decals", default=True)

    consistantscale = BoolProperty(name="Force Consistent Scale", default=False)

    # GROUPPRO SUPPORT
    groupproconnection = BoolProperty(name="GroupPro Connection", default=True)

    # BASE MATERIAL
    autobasematerial = BoolProperty(name="Adjust Decal materials to base material, when inserting Decals into scene", default=True)

    if bpy.app.version < (2, 79, 0):
        distribution_items = reversed([("MULTI_GGX", "Multiscatter GGX", ""),
                                       ("ASHIKHMIN_SHIRLEY", "Ashikhmin-Shirley", ""),
                                       ("GGX", "GGX", ""),
                                       ("BECKMANN", "Beckmann", ""),
                                       ("SHARP", "Sharp", "")])
        base_distribution = EnumProperty(name="Distribution", items=distribution_items, default="GGX")
        base_color = FloatVectorProperty(name="Color", subtype='COLOR', default=[0.35, 0.35, 0.35], size=3, min=0, max=1)
        base_roughness = FloatProperty(name="Roughness", default=0.2)
    else:
        distribution_items = reversed([("MULTI_GGX", "Multiscatter GGX", ""),
                                       ("GGX", "GGX", "")])
        base_distribution = EnumProperty(name="Distribution", items=distribution_items, default="GGX")
        base_color = FloatVectorProperty(name="Color", subtype='COLOR', default=[0.35, 0.35, 0.35], size=3, min=0, max=1)
        base_metallic = FloatProperty(name="Metallic", default=1, min=0, max=1)
        base_specular = FloatProperty(name="Specular", default=0.5, min=0, max=1)
        base_speculartint = FloatProperty(name="Specular Tint", default=0, min=0, max=1)
        base_roughness = FloatProperty(name="Roughness", default=0.5, min=0, max=1)
        base_anisotropic = FloatProperty(name="Anisotropic", default=0, min=0, max=1)
        base_anisotropicrotation = FloatProperty(name="Anisotropic Rotation", default=0, min=0, max=1)
        base_sheen = FloatProperty(name="Sheen", default=0, min=0, max=1)
        base_sheentint = FloatProperty(name="Sheen", default=0.5, min=0, max=1)
        base_clearcoat = FloatProperty(name="Clearcoat", default=0, min=0, max=1)
        base_clearcoatroughness = FloatProperty(name="Clearcoat Roughness", default=0.03, min=0, max=1)
        base_ior = FloatProperty(name="IOR", default=1.450, min=0, max=1)
        base_transmission = FloatProperty(name="Transmission", default=0, min=0, max=1)

    # EXPORT PREFS

    # sketchfab
    sf_defaultdiffuse = FloatVectorProperty(name="Default Diffuse", subtype='COLOR', default=[0.5, 0.5, 0.5], size=3, min=0, max=1)
    sf_defaultmetalness = IntProperty(name="Default Metalness", min=0, max=100, default=100)
    sf_defaultglossiness = IntProperty(name="Default Glossiness", min=0, max=100, default=55)

    sf_bakeaointodiffuse = BoolProperty(name="Diffuse", default=True)
    sf_bakeaointometalness = BoolProperty(name="Metalness", default=True)
    sf_bakeaointoglossiness = BoolProperty(name="Glossiness", default=True)

    # CREATE PREFS
    usecustomdecalslib = BoolProperty(name="Use 'CustomDecals' library for Decal Creation", default=True)
    normalalphatolerance = IntProperty(name="Normal Alpha Tolerance", min=0, default=1)
    batchsuppressnaming = BoolProperty(name="Suppress Decal Names in Batch Decal Creation", default=False)

    atlaspadding = IntProperty(name="Default Padding", default=3, min=0, max=10)

    def draw(self, context):
        layout=self.layout

        column = layout.column(align=True)
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = column.box()

        if self.tabs == "general":
            self.draw_general_tab(box)
        elif self.tabs == "keymaps":
            self.draw_keymaps_tab(box)
        elif self.tabs == "create":
            self.draw_create_tab(box)
        elif self.tabs == "export":
            self.draw_export_tab(box)
        elif self.tabs == "about":
            self.draw_about_tab(box)

    def draw_general_tab(self, box):
        if self.AMfirst:
            if self.useAMpath is True:
                self.assetpath = self.AMassetpath
                self.customassetpath = self.AMcustomassetpath
            else:
                if self.assetpath == "No 'Decals' and 'CustomDecals' libraries found in Asset Manager assets path.":
                    self.assetpath = self.DMassetpath
                if self.customassetpath == "No 'Decals' and 'CustomDecals' libraries found in Asset Manager assets path.":
                    self.customassetpath = self.DMcustomassetpath

            column = box.column()

            column.prop(self, "assetpath")
            column.prop(self, "customassetpath")

            column = box.column()
            row = column.split(percentage=0.4)
            row.prop(self, "useAMpath")
            row.label("NOTE: Save user prefs and re-start Blender, when path is changed.")

            column.separator()

            column = box.column()
            row = column.row()
            row.prop(self, "useDMassetloader")
        else:
            column = box.column()
            column.prop(self, "assetpath")
            column.prop(self, "customassetpath")

        column = box.column()
        row = column.row()
        row.prop(self, "autocycles")

        column = box.column()
        row = column.row()
        row.prop(self, "automaterialshading")

        column = box.column()
        row = column.row()
        row.prop(self, "consistantscale")

        # HOps Fix

        if m3.HOps_check():
            column.separator()
            row = column.row()
            row.operator("hops.decalmachine_fix", text="HardOps Fix").option = True
            row.operator("hops.decalmachine_fix", text="Undo HardOps Fix").option = False

        # Group Pro

        if m3.GP_check():
            column.separator()
            row = column.row()
            row.prop(self, "groupproconnection")

        # Base Material

        row = column.split(percentage=0.45)
        row.label("")
        row.label("Base Material")

        column.prop(self, "autobasematerial")

        if bpy.app.version < (2, 79, 0):
            self.draw_base_material_old(column)
        else:
            self.draw_base_material(column)

    def draw_keymaps_tab(self, box):
        column = box.column()
        wm = bpy.context.window_manager

        kc = wm.keyconfigs.user

        column.separator()
        row = column.split(percentage=0.4)
        row.label("")
        row.label("Object Mode")

        row = column.split(percentage=0.25)
        row.label("DECALmachine")
        du.show_keymap(True, kc, "Object Mode", "wm.call_menu_pie", row, "name", "machin3.decal_pie")

        row = column.split(percentage=0.25)
        row.label("DECALcreate")
        du.show_keymap(True, kc, "Object Mode", "wm.call_menu_pie", row, "name", "machin3.decal_create_pie")

        row = column.split(percentage=0.25)
        row.label("DECALexport")
        du.show_keymap(True, kc, "Object Mode", "wm.call_menu_pie", row, "name", "machin3.decal_export_pie")

        column.separator()
        row = column.split(percentage=0.4)
        row.label("")
        row.label("Edit Mode")

        row = column.split(percentage=0.25)
        row.label("DECALmachine")
        du.show_keymap(True, kc, "Mesh", "wm.call_menu_pie", row, "name", "machin3.decal_pie")

        column.separator()
        row = column.split(percentage=0.4)
        row.label("")
        row.label("3D View")

        row = column.split(percentage=0.25)
        row.label("Rotate Decal CW")
        du.show_keymap(True, kc, "3D View", "machin3.decal_rotate", row, "angle", 45)

        row = column.split(percentage=0.25)
        row.label("Rotate Decal CCW")
        du.show_keymap(True, kc, "3D View", "machin3.decal_rotate", row, "angle", -45)

        column.separator()
        row = column.split(percentage=0.4)
        row.label("")
        row.label("Image Editor")

        row = column.split(percentage=0.25)
        row.label("Rotate UVs CW")
        du.show_keymap(True, kc, "Image", "machin3.decal_rotate", row, "angle", 45)

        row = column.split(percentage=0.25)
        row.label("Rotate UVs CCW")
        du.show_keymap(True, kc, "Image", "machin3.decal_rotate", row, "angle", -45)

        column.separator()
        row = column.split(percentage=0.4)
        row.label("")
        row.label("Grease Pencil")

        row = column.split(percentage=0.25)
        row.label("GPencil Pie")
        du.show_keymap(True, kc, "Object Mode", "wm.call_menu_pie", row, "name", "GPENCIL_PIE_tool_palette")

    def draw_create_tab(self, box):
        column = box.column()
        row = column.split(percentage=0.45)
        row.prop(self, "usecustomdecalslib")
        row.label("(Keep this checked or risk loosing Decals w/ updates)")

        row = column.split(percentage=0.45)
        row.prop(self, "normalalphatolerance")

        row = column.split(percentage=0.45)
        row.prop(self, "batchsuppressnaming")

    def draw_export_tab(self, box):
        column = box.column()

        column.separator()
        row = column.split(percentage=0.45)
        row.label("")
        row.label("Atlas")

        row = column.split(percentage=0.45)
        row.prop(self, "atlaspadding")

        column.separator()
        row = column.split(percentage=0.45)
        row.label("")
        row.label("Path")

        column.prop(self, "DMexportpath")

        column.separator()
        row = column.split(percentage=0.45)
        row.label("")
        row.label("Sketchfab")

        column = box.column()
        row = column.row()
        row.label("Sketchfab Diffuse")
        row.prop(self, "sf_defaultdiffuse", text="")

        row = column.row()
        row.label("Sketchfab Metalness")
        row.prop(self, "sf_defaultmetalness", text="")

        row = column.row()
        row.label("Sketchfab Glossiness")
        row.prop(self, "sf_defaultglossiness", text="")

        column = box.column()
        row = column.row()
        row.label("Sketchfab Bake AO into")
        row.prop(self, "sf_bakeaointodiffuse", toggle=True)
        row.prop(self, "sf_bakeaointometalness", toggle=True)
        row.prop(self, "sf_bakeaointoglossiness", toggle=True)

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

    def draw_base_material(self, column):
        row = column.row()
        row.label("Base Distribution")
        row.prop(self, "base_distribution", text="")

        row = column.row()
        row.label("Base Color")
        row.prop(self, "base_color", text="")

        row = column.row()
        row.label("Base Metallic")
        row.prop(self, "base_metallic", text="")

        row = column.row()
        row.label("Base Specilar")
        row.prop(self, "base_specular", text="")

        row = column.row()
        row.label("Base Specular Tint")
        row.prop(self, "base_speculartint", text="")

        row = column.row()
        row.label("Base Roughness")
        row.prop(self, "base_roughness", text="")

        row = column.row()
        row.label("Base Anisotropic")
        row.prop(self, "base_anisotropic", text="")

        row = column.row()
        row.label("Base Anisotropic Rotation")
        row.prop(self, "base_anisotropicrotation", text="")

        row = column.row()
        row.label("Base Sheen")
        row.prop(self, "base_sheen", text="")

        row = column.row()
        row.label("Base Sheen Tint")
        row.prop(self, "base_sheentint", text="")

        row = column.row()
        row.label("Base Clearcoat")
        row.prop(self, "base_clearcoat", text="")

        row = column.row()
        row.label("Base Clearcoat Roughness")
        row.prop(self, "base_clearcoatroughness", text="")

        row = column.row()
        row.label("Base IOR")
        row.prop(self, "base_ior", text="")

        row = column.row()
        row.label("Base Transmission")
        row.prop(self, "base_transmission", text="")

    def draw_base_material_old(self, column):
        row = column.row()
        row.label("Base Distribution")
        row.prop(self, "base_distribution", text="")

        row = column.row()
        row.label("Base Color")
        row.prop(self, "base_color", text="")

        row = column.row()
        row.label("Base Roughness")
        row.prop(self, "base_roughness", text="")


DECALmachine_keymaps = []


def register():
    bpy.utils.register_module(__name__)
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

    register_and_load_decals01()
    register_and_load_decals02()
    register_and_load_info01()
    register_and_load_paneling01()

    bpy.types.Scene.decals = bpy.props.PointerProperty(type=DecalSettings)

    wm = bpy.context.window_manager

    # DECALmachine pie - object mode
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', "D", "PRESS")
    kmi.properties.name = "machin3.decal_pie"
    DECALmachine_keymaps.append((km, kmi))

    # DECALmachine pie - edit mode
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', "D", "PRESS")
    kmi.properties.name = "machin3.decal_pie"
    DECALmachine_keymaps.append((km, kmi))

    # DECALcreate pie
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', "D", "PRESS", ctrl=True, shift=True, alt=True)
    kmi.properties.name = "machin3.decal_create_pie"
    DECALmachine_keymaps.append((km, kmi))

    # DECALexport pie
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', "E", "PRESS", ctrl=True, shift=True, alt=True)
    kmi.properties.name = "machin3.decal_export_pie"
    DECALmachine_keymaps.append((km, kmi))

    # Rotate Decal tool - 3D View
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("machin3.decal_rotate", "WHEELDOWNMOUSE", "PRESS", ctrl=True, alt=True, shift=True)
    setattr(kmi.properties, 'angle', 45)
    DECALmachine_keymaps.append((km, kmi))
    # kmi = km.keymap_items.new("machin3.decal_rotate_ccw", "WHEELUPMOUSE", "PRESS", ctrl=True, alt=True, shift=True)
    kmi = km.keymap_items.new("machin3.decal_rotate", "WHEELUPMOUSE", "PRESS", ctrl=True, alt=True, shift=True)
    setattr(kmi.properties, 'angle', -45)
    DECALmachine_keymaps.append((km, kmi))

    # Rotate Decal tool - Image editor
    km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
    kmi = km.keymap_items.new("machin3.decal_rotate", "WHEELDOWNMOUSE", "PRESS", ctrl=True, alt=True, shift=True)
    setattr(kmi.properties, 'angle', 45)
    DECALmachine_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("machin3.decal_rotate", "WHEELUPMOUSE", "PRESS", ctrl=True, alt=True, shift=True)
    setattr(kmi.properties, 'angle', -45)
    DECALmachine_keymaps.append((km, kmi))

    # Grease Pencil Pie (this ia a new mapping, looks like you can't edit the default one at startup)
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', "D", "PRESS", ctrl=True)
    kmi.properties.name = "GPENCIL_PIE_tool_palette"
    DECALmachine_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_module(__name__)
    print("Unregistered {}".format(bl_info["name"]))

    unregister_and_unload_decals01()
    unregister_and_unload_decals02()
    unregister_and_unload_info01()
    unregister_and_unload_paneling01()

    for km, kmi in DECALmachine_keymaps:
        km.keymap_items.remove(kmi)

    DECALmachine_keymaps.clear()
