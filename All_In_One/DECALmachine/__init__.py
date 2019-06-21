'''
    Copyright (C) 2017-2019 MACHIN3, machin3.io, decal@machin3.io

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

    DECALmachine Assets, such as Example Decal textures and supplied blend files created by MACHIN3

        Decal Assets may not be distributed or sub-licensed to third partys
        unless permission is specifically granted.

    Parallax Nodetree originally by zelouille, ported by Vsevolod Ochinskiy and used with permission:
    https://blenderartists.org/forum/showthread.php?314083-Cycles-parallax-step-mapping-with-nodes

    The core of the Atlas Class - Atlas.create_atlas() in operators/atlas.py is based on the Atlas
    implementation of the Kivy project. See https://github.com/kivy/kivy/blob/master/kivy/atlas.py

    Copyright and Permission notice:

        Copyright (c) 2010-2019 Kivy Team and other contributors

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
    "version": (1, 8, 5),
    "blender": (2, 80, 0),
    "location": "Pie Menu: D key, MACHIN3 N Panel",
    "revision": "d81d453ac57c9697dd75cef89377cdc20236fd9a",
    "description": "A complete mesh-decal pipeline. Project decals, slice decal panel strips, create your own decals, export decals or bake them down.",
    "warning": "",
    "wiki_url": "https://decal.machin3.io",
    "tracker_url": "https://machin3.io/DECALmachine/docs/faq/#get-support",
    "category": "Mesh"}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty, CollectionProperty, IntVectorProperty
from . properties import DecalSceneProperties, DecalObjectProperties, DecalMaterialProperties, DecalImageProperties, DecalCollectionProperties, ExcludeCollection
from . utils.registration import get_core, get_menus, get_tools, get_prefs, register_classes, unregister_classes, register_keymaps, unregister_keymaps
from . utils.registration import register_decals, unregister_decals, register_instant_decals, unregister_instant_decals, register_lockedlib, unregister_lockedlib
from . utils.registration import register_icons, unregister_icons, register_infotextures, unregister_infotextures, register_infofonts, unregister_infofonts, register_panels, unregister_panels
from . utils.system import get_PIL_image_module_path
from . utils.update import update_check
from . handlers import update_panels, update_match_material_enum, update_infodecal_sources, update_userdecallibs_enum


def register():
    global classes, keymaps, icons

    # CORE

    core_classes = register_classes(get_core())


    # PROPERTIES

    bpy.types.Scene.DM = PointerProperty(type=DecalSceneProperties)
    bpy.types.Object.DM = PointerProperty(type=DecalObjectProperties)
    bpy.types.Material.DM = PointerProperty(type=DecalMaterialProperties)
    bpy.types.Image.DM = PointerProperty(type=DecalImageProperties)
    bpy.types.Collection.DM = PointerProperty(type=DecalCollectionProperties)

    bpy.types.WindowManager.matchmaterial = EnumProperty(name="Materials, that can be matched", items=[("None", "None", "", 0, 0)])

    bpy.types.WindowManager.collectinfotextures = BoolProperty()
    bpy.types.WindowManager.updateinfotextures = StringProperty()
    bpy.types.WindowManager.excludeimages = CollectionProperty(type=ExcludeCollection)

    bpy.types.WindowManager.collectinfofonts = BoolProperty()
    bpy.types.WindowManager.updateinfofonts = StringProperty()
    bpy.types.WindowManager.excludefonts = CollectionProperty(type=ExcludeCollection)

    bpy.types.WindowManager.decal_mousepos = IntVectorProperty(name="Mouse Position for Decal Insertion", size=2)


    # DECALS

    decals = register_decals()
    register_instant_decals()
    register_lockedlib()


    # INFO DECAL SOURCES

    register_infotextures()
    register_infofonts()


    # TOOLS, MENUS, KEYMAPS

    menu_classlists, menu_keylists = get_menus()
    tool_classlists, tool_keylists = get_tools()

    classes = register_classes(menu_classlists + tool_classlists) + core_classes
    keymaps = register_keymaps(menu_keylists + tool_keylists)

    register_panels(getall=True)


    # ICONS

    icons = register_icons()


    # HANDLERS

    bpy.app.handlers.load_post.append(update_panels)

    bpy.app.handlers.undo_post.append(update_match_material_enum)
    bpy.app.handlers.redo_post.append(update_match_material_enum)
    bpy.app.handlers.load_post.append(update_match_material_enum)

    bpy.app.handlers.load_post.append(update_userdecallibs_enum)

    bpy.app.handlers.depsgraph_update_post.append(update_infodecal_sources)


    # CHECK PIL and set preferences.pil prop accordingly

    try:
        import PIL
        from PIL import Image

        get_prefs().pil = True
        get_prefs().pilrestart = False
        path = get_PIL_image_module_path(Image)
    except:
        get_prefs().pil = False
        get_prefs().pilrestart = False
        path = ''


    # REGISTRATION TERMINAL OUTPUT

    print("Registered %s %s with %d decal libraries. %s" % (bl_info["name"], ".".join([str(i) for i in bl_info['version']]), len(decals), "PIL %s %s" % (PIL.__version__, "Image Module: %s" % path) if get_prefs().pil else "PIL is not installed."))

    for lib in decals:
        print(" » decal library: %s" % (lib))


    # INITIALIZE
    get_prefs().update_available = False


    # CHECK for new versions

    update_check()


def unregister():
    global classes, keymaps, icons

    # HANDLERS

    bpy.app.handlers.load_post.remove(update_panels)

    bpy.app.handlers.undo_post.remove(update_match_material_enum)
    bpy.app.handlers.redo_post.remove(update_match_material_enum)
    bpy.app.handlers.load_post.remove(update_match_material_enum)

    bpy.app.handlers.load_post.remove(update_userdecallibs_enum)

    bpy.app.handlers.depsgraph_update_post.remove(update_infodecal_sources)


    # DECALS

    unregister_decals()
    unregister_instant_decals()
    unregister_lockedlib()


    # INFO DECAL SOURCES

    unregister_infotextures()
    unregister_infofonts()


    # KEYMAPS

    unregister_keymaps(keymaps)


    # ICONS

    unregister_icons(icons)


    # PANELS

    unregister_panels()


    # PROPERTIES

    del bpy.types.Scene.DM
    del bpy.types.Object.DM
    del bpy.types.Material.DM
    del bpy.types.Image.DM
    del bpy.types.Collection.DM

    del bpy.types.WindowManager.matchmaterial

    del bpy.types.Scene.userdecallibs
    del bpy.types.WindowManager.newdecalidx
    del bpy.types.WindowManager.decaluuids
    del bpy.types.WindowManager.paneldecals
    del bpy.types.WindowManager.instantdecaluuids

    del bpy.types.WindowManager.collectinfotextures
    del bpy.types.WindowManager.updateinfotextures
    del bpy.types.WindowManager.excludeimages

    del bpy.types.WindowManager.collectinfofonts
    del bpy.types.WindowManager.updateinfofonts
    del bpy.types.WindowManager.excludefonts

    del bpy.types.WindowManager.decal_mousepos


    # TOOLS, MENUS, CORE

    unregister_classes(classes)

    print("Unregistered %s %s" % (bl_info["name"], ".".join([str(i) for i in bl_info['version']])))
