import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.utils import register_class, unregister_class, previews
import os
from . system import get_new_directory_index
from .. keys import keys as keysdict
from .. classes import classes as classesdict


# GENERAL

def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_name():
    return os.path.basename(get_path())


def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences


def get_addon(addon, debug=False):
    """
    look for addon by name and find folder name and path
    Note, this will also find addons that aren't registered!
    """
    import addon_utils

    for mod in addon_utils.modules():
        name = mod.bl_info["name"]
        version = mod.bl_info.get("version", None)
        foldername = mod.__name__
        path = mod.__file__
        enabled = addon_utils.check(foldername)[1]

        if name == addon:
            if debug:
                print(name)
                print("  enabled:", enabled)
                print("  folder name:", foldername)
                print("  version:", version)
                print("  path:", path)
                print()

            return enabled, foldername, version, path
    return False, None, None, None


def get_addon_prefs(addon):
    _, foldername, _, _ = get_addon(addon)
    return bpy.context.preferences.addons.get(foldername)


# CLASS REGISTRATION

def register_classes(classlists, debug=False):
    classes = []

    for classlist in classlists:
        for fr, imps in classlist:
            impline = "from ..%s import %s" % (fr, ", ".join([i[0] for i in imps]))
            classline = "classes.extend([%s])" % (", ".join([i[0] for i in imps]))

            exec(impline)
            exec(classline)

    for c in classes:
        if debug:
            print("REGISTERING", c)

        register_class(c)

    return classes


def unregister_classes(classes, debug=False):
    for c in classes:
        if debug:
            print("UN-REGISTERING", c)

        unregister_class(c)


def get_classes(classlist):
    classes = []

    for fr, imps in classlist:
        if "operators" in fr:
            type = "OT"
        elif "pies" in fr or "menus" in fr:
            type = "MT"

        for imp in imps:
            idname = imp[1]
            rna_name = "MACHIN3_%s_%s" % (type, idname)

            c = getattr(bpy.types, rna_name, False)

            if c:
                classes.append(c)

    return classes


# KEYMAP REGISTRATION

def register_keymaps(keylists):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    # kc = wm.keyconfigs.user

    keymaps = []


    for keylist in keylists:
        for item in keylist:
            keymap = item.get("keymap")
            space_type = item.get("space_type", "EMPTY")

            if keymap:
                km = kc.keymaps.new(name=keymap, space_type=space_type)

                if km:
                    idname = item.get("idname")
                    type = item.get("type")
                    value = item.get("value")

                    shift = item.get("shift", False)
                    ctrl = item.get("ctrl", False)
                    alt = item.get("alt", False)

                    kmi = km.keymap_items.new(idname, type, value, shift=shift, ctrl=ctrl, alt=alt)

                    if kmi:
                        properties = item.get("properties")

                        if properties:
                            for name, value in properties:
                                setattr(kmi.properties, name, value)

                        keymaps.append((km, kmi))
    return keymaps


def unregister_keymaps(keymaps):
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)


# ICON REGISTRATION

def register_icons():
    path = os.path.join(get_prefs().path, "icons")
    icons = previews.new()

    for i in sorted(os.listdir(path)):
        if i.endswith(".png"):
            iconname = i[:-4]
            filepath = os.path.join(path, i)

            icons.load(iconname, filepath, 'IMAGE')

    return icons


def unregister_icons(icons):
    previews.remove(icons)


# RETRIEVE CLASSLISTS

def get_core():
    return [classesdict["CORE"]]


def get_menus():
    classlists = []
    keylists = []

    # DECALmachine Pie Menu

    classlists.append(classesdict["PIE_MENU"])
    keylists.append(keysdict["PIE_MENU"])


    # DECALmachine Panel

    classlists.append(classesdict["PANEL"])

    return classlists, keylists


def get_panels(getall=False):
    classlists = []

    # when registering DM, scene is not available, hence why getall is checked first below
    if not getall:
        dm = bpy.context.scene.DM

    # optional panels

    if getall or dm.register_panel_creation:
        classlists.append(classesdict["PANEL_CREATE"])

    if getall or dm.register_panel_update_legacy:
        classlists.append(classesdict["PANEL_UPDATE_LEGACY"])

    if getall or dm.register_panel_debug:
        classlists.append(classesdict["PANEL_DEBUG"])

    if getall or dm.register_panel_help:
        classlists.append(classesdict["PANEL_HELP"])

    return classlists


def get_tools():
    classlists = []
    keylists = []

    classlists.append(classesdict["INSERTREMOVE"])
    classlists.append(classesdict["VALIDATE"])
    classlists.append(classesdict["ADJUST"])
    classlists.append(classesdict["REAPPLY"])
    classlists.append(classesdict["PROJECT"])
    classlists.append(classesdict["SLICE"])
    classlists.append(classesdict["GETBACKUP"])
    classlists.append(classesdict["UNWRAP"])
    classlists.append(classesdict["MATCH"])
    classlists.append(classesdict["SELECT"])

    classlists.append(classesdict["CREATE"])

    classlists.append(classesdict["ADDON"])

    classlists.append(classesdict["DEBUG"])

    keylists.append(keysdict["QUICK_INSERT"])
    keylists.append(keysdict["SELECT"])

    return classlists, keylists


# PANEL REGISTRATION

def register_panels(getall=False):
    panel_classes = get_panels(getall)

    # register panels based on their scene prop settings
    register_classes(panel_classes)


def unregister_panels():
    panel_classes = get_panels(getall=True)

    # unregister all the panels if any is registered
    for classlist in panel_classes:
        for fr, imps in classlist:
            for _, idname in imps:
                panel = getattr(bpy.types, "MACHIN3_PT_%s" % (idname), None)

                if panel:
                    unregister_class(panel)


def reload_panels():
    unregister_panels()
    register_panels()


# DECAL REGISTRATION

decals = {}


def register_decals(library="ALL", default=None, reloading=False):
    assetspath = get_prefs().assetspath

    # remove any libs from the collection that were saved to prefs, but no longer exist on disk or are no longer .280 libs
    savedlibs = [lib.name for lib in get_prefs().decallibsCOL]

    for lib in savedlibs:
        if os.path.exists(os.path.join(assetspath, lib)):
            if not os.path.exists(os.path.join(assetspath, lib, ".is280")):
                index = get_prefs().decallibsCOL.keys().index(lib)
                get_prefs().decallibsCOL.remove(index)

                print(" ! WARNNING: decal library '%s' has not been updated for DECALmachine 1.8/Blender 2.80!" % lib)

        else:
            # the index needs to be retrieved every time, because it changes with each removal
            index = get_prefs().decallibsCOL.keys().index(lib)
            get_prefs().decallibsCOL.remove(index)
            print(" ! WARNNING: decal library '%s' can no longer be found! Save your preferences!" % lib)
            # TODO: just run  bpy.ops.wm.save_userpref() automatically?


    # create list containing all registered decallibs, or only a specific one, depending on the libtary argument
    decallibs = []


    # REGISTER ALL

    if library == "ALL":
        for f in sorted(os.listdir(assetspath)):
            if os.path.isdir(os.path.join(assetspath, f)):

                if os.path.exists(os.path.join(assetspath, f, ".is280")):

                    decallibs.append(f)

                    # populate decalllibs collection with new(previously unsaved) libs
                    if f not in get_prefs().decallibsCOL:
                        item = get_prefs().decallibsCOL.add()
                        item.name = f

                        # hide library, but only the first time it is seen
                        if os.path.exists(os.path.join(assetspath, f, ".ishidden")):
                            get_prefs().decallibsCOL[f].isvisible = False

                    # set slice prop
                    if os.path.exists(os.path.join(assetspath, f, ".ispanel")):
                        get_prefs().decallibsCOL[f].avoid_update = True
                        get_prefs().decallibsCOL[f].ispanel = True

                    # lock library
                    if os.path.exists(os.path.join(assetspath, f, ".islocked")):
                        get_prefs().decallibsCOL[f].avoid_update = True
                        get_prefs().decallibsCOL[f].islocked = True

        get_prefs().decallibsIDX = 0

        # create scene enum, used for decal creation, TODO: try putting it into the window manager?
        unlockedlibs = sorted([(lib.name, lib.name, "") for lib in get_prefs().decallibsCOL if not lib.islocked], reverse=False)
        enum = EnumProperty(name="User Decal Library", items=unlockedlibs, update=set_new_decal_index, default=unlockedlibs[-1][0] if unlockedlibs else None)
        setattr(bpy.types.Scene, "userdecallibs", enum)
        setattr(bpy.types.WindowManager, "newdecalidx", StringProperty(name="User Decal Library Index"))


    # REGISTER ONE

    else:
        decallibs = [library]


    # CREATE PREVIEW COLLECTIONS to store decal thumbnails from decallibs list

    # store preview collection in dictionary, using library/folder names as keys, to be returned at the end
    global decals

    # also collect uuids you encouter and the decalnames and libraries they are found in.
    uuids = {} if not reloading else bpy.types.WindowManager.decaluuids


    # for each folder create a preview collection and populate it
    for libname in decallibs:
        col = previews.new()
        items = populate_preview_collection(col, assetspath, libname, uuids)

        # store the collection in the decals dict
        decals[libname] = col

        # create window manager enum, used for the displaying the libraries in the UI
        enum = EnumProperty(items=items, update=insert_or_remove_decal(libname), default=default)
        setattr(bpy.types.WindowManager, "decallib_" + libname, enum)

        if reloading:
            if libname in savedlibs:
                print(" » reloaded decal library: %s" % (libname))
            else:
                print(" » loaded new decal library: %s" % (libname))

    # store the uuids
    setattr(bpy.types.WindowManager, "decaluuids", uuids)


    # create window manager enum for panel decals(not panel libs!), used by the slice tools
    # NOTE: putting this into Scene causes issues when used as operator prop in slice tools, perhaps somehow because ot the redo panel? its value seems to resist changing too in that case
    items = get_panel_decal_items()
    setattr(bpy.types.WindowManager, "paneldecals", EnumProperty(name='Panel Types', items=items, default=items[0][0]))

    return decals


def unregister_decals(library="ALL"):
    global decals

    if library == "ALL":
        decallibs = list(decals.items())

    else:
        decallibs = [(library, decals[library])]


    for libname, col in decallibs:
        # remove decallib enum
        delattr(bpy.types.WindowManager, "decallib_" + libname)

        # remove library preview collection
        previews.remove(col)

        # delete library dicationary entry
        del decals[libname]

        # remove uuids
        for uuid, decallist in list(bpy.types.WindowManager.decaluuids.items()):
            for decal, lib in decallist:
                if lib == libname:
                    # remove decalname, libname tuple decallist
                    decallist.remove((decal, lib))

            # remove empty uuid entry
            if not decallist:
                del bpy.types.WindowManager.decaluuids[uuid]

        print(" » unloaded decal library: %s" % (libname))


def get_panel_decal_items():
    panellibs = [lib.name for lib in get_prefs().decallibsCOL if lib.ispanel]

    tuplelist = []

    if panellibs:
        assetspath = get_prefs().assetspath

        for lib in panellibs:
            libpath = os.path.join(assetspath, lib)
            panellist = getattr(bpy.types.WindowManager, "decallib_" + lib)[1]['items']

            for name, _, _, _, _ in panellist:

                uuid = None

                with open(os.path.join(libpath, name, "uuid"), "r") as f:
                    uuid = f.read()

                if uuid:
                    # uuid first to ensure unique items across different libraries
                    tuplelist.append((uuid, name, lib))

    # sort them library first, name second
    return sorted(tuplelist, key=lambda x: (x[2], x[1]))


def insert_or_remove_decal(libraryname='', instant=False):
    def function_template(self, context):
        # this is done to set a new decal after another one was removed and prevent warnings about decal '' not found in library, it may also be used in the future when replacing exsisting decals
        if get_prefs().decalmode == "NONE":
            return

        # insert or remove decal
        else:
            if get_prefs().decalmode == "INSERT":
                if instant:
                    bpy.ops.machin3.insert_decal(library="INSTANT", decal=getattr(bpy.context.window_manager, "instantdecallib"), instant=True, force_cursor_align=True)
                else:
                    bpy.ops.machin3.insert_decal(library=libraryname, decal=getattr(bpy.context.window_manager, "decallib_" + libraryname), instant=False, force_cursor_align=False)

            elif get_prefs().decalmode == "REMOVE":
                if instant:
                    bpy.ops.machin3.remove_decal('INVOKE_DEFAULT', library="INSTANT", decal=getattr(bpy.context.window_manager, "instantdecallib"), instant=True)
                else:
                    bpy.ops.machin3.remove_decal('INVOKE_DEFAULT', library=libraryname, decal=getattr(bpy.context.window_manager, "decallib_" + libraryname), instant=False)

    return function_template


def set_new_decal_index(self, context):
    assetspath = get_prefs().assetspath
    library = context.scene.userdecallibs
    decalpath = os.path.join(assetspath, library)

    context.window_manager.newdecalidx = get_new_directory_index(decalpath)


def populate_preview_collection(col, assetspath, library, uuids):
    libpath = os.path.join(assetspath, library)

    items = []

    folders = sorted([(f, os.path.join(libpath, f)) for f in os.listdir(libpath) if os.path.isdir(os.path.join(libpath, f))], key=lambda x: x[0], reverse=get_prefs().reversedecalsorting)

    for decalname, decalpath in folders:
        files = os.listdir(decalpath)

        if all([f in files for f in ["decal.blend", "decal.png", "uuid"]]):
            iconpath = os.path.join(decalpath, "decal.png")
            preview = col.load(decalname, iconpath, 'IMAGE')

            items.append((decalname, decalname, "%s %s" % (library, decalname), preview.icon_id, preview.icon_id))

            with open(os.path.join(decalpath, "uuid"), "r") as f:
                uuid = f.read().replace("\n", "")

            if uuid not in uuids:
                uuids[uuid] = []

            uuids[uuid].append((decalname, library))

    return items


def reload_decal_libraries(library="ALL", default=None):
    lib = bpy.context.scene.userdecallibs

    if library == "ALL":
        unregister_decals()
        register_decals(reloading=True)
    else:
        unregister_decals(library=library)
        register_decals(library=library, default=default, reloading=True)

        if default:
            mode = get_prefs().decalmode
            get_prefs().decalmode = "NONE"
            setattr(bpy.context.window_manager, "decallib_" + library, default)
            get_prefs().decalmode = mode

    # reset user decal libs, if the pre-library reload lib no longer exists
    if lib not in [lib[0] for lib in bpy.types.Scene.userdecallibs[1]['items']]:
        firstlib = bpy.types.Scene.userdecallibs[1]['items'][0][0]
        setattr(bpy.context.scene, "userdecallibs", firstlib)


# LOCKED PLACEHOLDER REGISTRATION

locked = None


def register_lockedlib():
    global locked

    locked = previews.new()

    lockedpath = os.path.join(get_path(), "resources", 'locked.png')
    preview = locked.load("LOCKED", lockedpath, 'IMAGE')
    items = [("LOCKED", "LOCKED", "LIBRARY is LOCKED", preview.icon_id, preview.icon_id)]

    enum = EnumProperty(items=items)
    setattr(bpy.types.WindowManager, "lockeddecallib", enum)


def unregister_lockedlib():
    global locked

    delattr(bpy.types.WindowManager, "lockeddecallib")
    previews.remove(locked)


# INSTANT DECAL

instantdecals = None


def register_instant_decals(default=None, reloading=False):
    global instantdecals

    instantpath = os.path.join(get_path(), "assets", 'Create', 'instant')

    items = []
    instantdecals = previews.new()

    # also collect uuids you encouter and the decalnames and libraries they are found in.
    uuids = {} if not reloading else bpy.types.WindowManager.instantdecaluuids


    folders = sorted([(f, os.path.join(instantpath, f)) for f in os.listdir(instantpath) if os.path.isdir(os.path.join(instantpath, f))], key=lambda x: x[0], reverse=False)

    for decalname, decalpath in folders:
        files = os.listdir(decalpath)

        if all([f in files for f in ["decal.blend", "decal.png", "uuid"]]):

            iconpath = os.path.join(decalpath, "decal.png")
            preview = instantdecals.load(decalname, iconpath, 'IMAGE')

            items.append((decalname, decalname, "%s %s" % ("INSTANT", decalname), preview.icon_id, preview.icon_id))

            with open(os.path.join(decalpath, "uuid"), "r") as f:
                uuid = f.read().replace("\n", "")

            if uuid not in uuids:
                uuids[uuid] = []

            uuids[uuid].append(decalname)


    enum = EnumProperty(items=items, update=insert_or_remove_decal(instant=True), default=default)

    setattr(bpy.types.WindowManager, "instantdecallib", enum)

    # store the uuids
    setattr(bpy.types.WindowManager, "instantdecaluuids", uuids)


def unregister_instant_decals():
    global instantdecals

    delattr(bpy.types.WindowManager, "instantdecallib")
    previews.remove(instantdecals)

    # remove uuids
    for uuid, decallist in list(bpy.types.WindowManager.instantdecaluuids.items()):
        for decal in decallist:
            decallist.remove(decal)

        # remove empty uuid entry
        if not decallist:
            del bpy.types.WindowManager.instantdecaluuids[uuid]


def reload_instant_decals(default=None):
    unregister_instant_decals()
    register_instant_decals(default=default, reloading=True)

    if default:
        mode = get_prefs().decalmode
        get_prefs().decalmode = "NONE"
        bpy.context.window_manager.instantdecallib = default
        get_prefs().decalmode = mode


# INFO DECAL TEXTURE REGISTRATION

infotextures = None


def register_infotextures(default=None):
    global infotextures

    infotextures = previews.new()

    infopath = os.path.join(get_path(), "assets", 'Create', 'infotextures')

    images = [f for f in os.listdir(infopath) if f.endswith(".png") or f.endswith(".jpg")]

    items = []

    for img in sorted(images):
        imgpath = os.path.join(infopath, img)
        imgname = img

        preview = infotextures.load(imgname, imgpath, 'IMAGE')

        items.append((imgname, imgname, "", preview.icon_id, preview.icon_id))

    enum = EnumProperty(items=items, default=default)
    setattr(bpy.types.WindowManager, "infotextures", enum)


def unregister_infotextures():
    global infotextures

    delattr(bpy.types.WindowManager, "infotextures")
    previews.remove(infotextures)


def reload_infotextures(default=None):
    unregister_infotextures()
    register_infotextures(default=default)


# INFO DECAL FONT REGISTRATION

infofonts = None


def register_infofonts(default=None):
    global infofonts

    infofonts = previews.new()

    fontspath = os.path.join(get_path(), "assets", 'Create', 'infofonts')

    fontfiles = [f for f in os.listdir(fontspath) if f.endswith(".ttf") or f.endswith(".TTF")]

    items = []

    for font in sorted(fontfiles):
        fontpath = os.path.join(fontspath, font)
        fontname = font

        preview = infofonts.load(fontname, fontpath, 'FONT')

        items.append((fontname, fontname, "", preview.icon_id, preview.icon_id))

    enum = EnumProperty(items=items, default=default)
    setattr(bpy.types.WindowManager, "infofonts", enum)


def unregister_infofonts():
    global infofonts

    delattr(bpy.types.WindowManager, "infofonts")
    previews.remove(infofonts)


def reload_infofonts(default=None):
    unregister_infofonts()
    register_infofonts(default=default)
