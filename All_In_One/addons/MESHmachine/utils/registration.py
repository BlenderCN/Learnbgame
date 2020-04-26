import bpy
import bpy.utils.previews
import os
from bpy.props import EnumProperty, StringProperty
from . import MACHIN3 as m3

preview_collections = {}


def register_and_load_plugs(library="ALL", default=None, reloading=False):
    assetspath = m3.MM_prefs().assetspath

    # remove any libs from the collection that were saved to prefs, but no longer exist on disk
    savedlibs = [lib.name for lib in m3.MM_prefs().pluglibsCOL]
    for idx, lib in enumerate(savedlibs):
        if not os.path.exists(os.path.join(assetspath, lib)):
            m3.MM_prefs().pluglibsCOL.remove(idx)
            print(" ! WARNNING:  plug library '%s' can no longer be found! Save your preferences!" % lib)

    # create pluglibs enum and populate collection
    pluglibs = []
    if library == "ALL":
        for idx, f in enumerate(sorted(os.listdir(assetspath))):
            if os.path.isdir(os.path.join(assetspath, f)):
                pluglibs.append(f)

                # populate plugllibs collection with new(previously unsaved) libs
                if f not in m3.MM_prefs().pluglibsCOL:
                    item = m3.MM_prefs().pluglibsCOL.add()
                    item.name = f

                if os.path.exists(os.path.join(assetspath, f, ".islocked")):
                    m3.MM_prefs().pluglibsCOL[f].islocked = True

        m3.MM_prefs().pluglibsIDX = len(pluglibs) - 1

        # create scene enum, used for plug creation
        unlockedlibs = [(lib.name, lib.name, "") for lib in m3.MM_prefs().pluglibsCOL if not lib.islocked]
        setattr(bpy.types.Scene, "pluglibs", EnumProperty(name="User Plug Libraries", items=sorted(unlockedlibs, reverse=True), update=set_new_plug_index))
        setattr(bpy.types.Scene, "newplugidx", StringProperty(name="User Plug Library Index"))

    else:
        pluglibs = [library]

    # for each folder create a preview collection, all saved in a preview collections dict, used for unregistering
    global preview_collections

    for folder in pluglibs:
        preview_collections[folder] = bpy.utils.previews.new()
        load_library_preview_icons(preview_collections[folder], os.path.join(assetspath, folder, "icons"))
        items = get_library_preview_items(preview_collections[folder])

        # also create window manager enum, used for the asset loaders
        setattr(bpy.types.WindowManager, "pluglib_" + folder, EnumProperty(items=items, update=insert_or_remove_plug(folder), default=default))
        if reloading:
            if folder in savedlibs:
                print(" » reloaded plug library: %s" % (folder))
            else:
                print(" » loaded new plug library: %s" % (folder))
        else:
            print(" » plug library: %s" % (folder))

    print()


def unregister_and_unload_plugs(library="ALL"):
    if library == "ALL":
        pluglibs = [lib.name for lib in m3.MM_prefs().pluglibsCOL]

        delattr(bpy.types.Scene, "pluglibs")
        print(" » unregistered Scene.pluglibs property")

    else:
        pluglibs = [library]

    global preview_collections

    for folder in pluglibs:
        delattr(bpy.types.WindowManager, "pluglib_" + folder)
        bpy.utils.previews.remove(preview_collections[folder])

        print(" » unloaded plug library: %s" % (folder))

    if library == "ALL":
        preview_collections = {}


def insert_or_remove_plug(folderstring):
    def function_template(self, context):
        # if m3.MM_prefs().plugremovemode:
        if m3.MM_prefs().plugmode == "INSERT":
            bpy.ops.machin3.insert_plug(library=folderstring, plug=getattr(bpy.context.window_manager, "pluglib_" + folderstring))
        elif m3.MM_prefs().plugmode == "REMOVE":
            bpy.ops.machin3.remove_plug('INVOKE_DEFAULT', library=folderstring, plug=getattr(bpy.context.window_manager, "pluglib_" + folderstring))

    return function_template


def set_new_plug_index(self, context):
    assetspath = m3.MM_prefs().assetspath
    library = context.scene.pluglibs
    iconspath = os.path.join(assetspath, library, "icons")

    icons = sorted(os.listdir(iconspath))

    if icons:
        counters = [int(icon[:3]) for icon in icons]
        index = str(counters[-1] + 1).zfill(3)
    else:
        index = "001"

    context.scene.newplugidx = index


def load_library_preview_icons(preview_collection, dirpath):
    for f in sorted(os.listdir(dirpath)):
        if f.endswith(".png"):
            plugname = f[:-4]
            filepath = os.path.join(dirpath, f)
            preview_collection.load(plugname, filepath, 'IMAGE')


def get_library_preview_items(preview_collection):
    tuplelist = []
    for name, preview in sorted(preview_collection.items(), reverse=m3.MM_prefs().reverseplugsorting):
        tuplelist.append((name, name, "", preview.icon_id, preview.icon_id))
    return tuplelist


def reload_plug_libraries(library="ALL", defaultplug=None):
    if library == "ALL":
        unregister_and_unload_plugs()
        register_and_load_plugs(reloading=True)
    else:
        unregister_and_unload_plugs(library=library)
        register_and_load_plugs(library=library, default=defaultplug, reloading=True)
