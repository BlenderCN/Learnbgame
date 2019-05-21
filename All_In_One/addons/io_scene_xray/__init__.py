import pkgutil

import sys

bl_info = {
    'name': 'XRay Engine Tools',
    'author': 'Vakhurin Sergey (igel), Pavel_Blend',
    'version': (0, 6, 0),
    'blender': (2, 80, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export',
    'description': 'Import/Export X-Ray objects',
    'wiki_url': 'https://github.com/PavelBlend/blender-xray',
    'tracker_url': 'https://github.com/PavelBlend/blender-xray/issues',
    'warning': 'Under construction!'
}

import bpy
from . import xray_inject, plugin

invalid_types = None
try:
    # TODO possibly it will be removed in release version of Blender 2.8
    import bpy_types as invalid_types
except:
    print("Replace bpy_types.<ClassName> with bpy.types.<ClassName>")


def find_bases(cls):
    res = set()
    res = res.union(set(cls.__bases__))

    for b in cls.__bases__:
        res = res.union(find_bases(b))

    return res


def get_blender_classes(modules):
    """
    Usage:
    import sys
    from .lib import py_utils, pathes
    module = sys.modules[__name__]
    reload(py_utils)
    classes = py_utils.get_bl_classes(module)
    lib.info(classes)
    """
    prefs = set()
    menus = set()
    operators = set()
    panels = set()
    ui_lists = set()
    prop_groups = set()

    for mod in modules:
        m_dict = mod.__dict__
        classes = [m_dict[c] for c in m_dict if isinstance(m_dict[c], type)]

        for cls in classes:
            for type_name, dest_set in [("AddonPreferences", prefs), ("PropertyGroup", prop_groups),
                                        ("Operator", operators), ("Menu", menus), ("Panel", panels),
                                        ("UIList", ui_lists)]:
                ctypes = []
                if hasattr(bpy.types, type_name):
                    ctype = getattr(bpy.types, type_name)
                    if ctype:
                        ctypes.append(ctype)

                if invalid_types and hasattr(invalid_types, type_name):
                    ctype = getattr(invalid_types, type_name)
                    if ctype:
                        ctypes.append(ctype)

                if ctypes:
                    bases = find_bases(cls)
                    if bases.intersection(ctypes):
                        dest_set.add(cls)

    return list(prefs), list(prop_groups), list(operators) + list(ui_lists) + list(menus) + list(panels)


def register_modules(modules):
    prefs, prop_groups, other = get_blender_classes(modules)
    for classes in prefs, prop_groups, other:
        classes.sort(key=lambda x: getattr(x, "reg_order") if hasattr(x, "reg_order") else 1000)
        for cls in classes:
            # print("-------------------------------------------")
            # print("register class: ", cls.__name__)
            bpy.utils.register_class(cls)
            # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def unregister_modules(modules):
    prefs, prop_groups, other = get_blender_classes(modules)
    for classes in other, prop_groups, prefs:
        classes.sort(reverse=True, key=lambda x: getattr(x, "reg_order") if hasattr(x, "reg_order") else 1000)
        for cls in classes:
            bpy.utils.unregister_class(cls)


def get_submodules(package=sys.modules[__name__]):
    modules = set()

    prefix = package.__name__ + "."

    modules.add(package)

    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        # cprint("Found submodule %s (is a package: %s)" % (modname, ispkg) )
        module = __import__(modname, fromlist="dummy")
        modules.add(module)

        if ispkg:
            submods = get_submodules(module)

            for m in submods:
                modules.add(m)

    return modules


def register():
    modules = get_submodules()
    register_modules(modules)

    for clas in xray_inject.__CLASSES__:
        # print("register MAIN PROP class: ", clas)
        b_type = clas.b_type

        if invalid_types:
            tname = clas.b_type.__name__.replace("bpy.types", "")
            if hasattr(invalid_types, tname):
                b_type = getattr(invalid_types, tname)

        # print(b_type)

        b_type.xray = bpy.props.PointerProperty(type=clas)

    # plugin register
    plugin.append_menu_func()
    plugin.overlay_view_3d.__handle = bpy.types.SpaceView3D.draw_handler_add(
        plugin.overlay_view_3d, (),
        'WINDOW', 'POST_VIEW'
    )
    bpy.app.handlers.load_post.append(plugin.load_post)
    bpy.app.handlers.depsgraph_update_post.append(plugin.scene_update_post)


def unregister():
    for clas in reversed(xray_inject.__CLASSES__):
        del clas.b_type.xray

    # plugin unregister
    bpy.app.handlers.depsgraph_update_post.remove(plugin.scene_update_post)
    bpy.app.handlers.load_post.remove(plugin.load_post)

    bpy.types.SpaceView3D.draw_handler_remove(plugin.overlay_view_3d.__handle, 'WINDOW')
    bpy.types.TOPBAR_MT_file_export.remove(plugin.menu_func_export_ogf)
    bpy.types.TOPBAR_MT_file_export.remove(plugin.menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(plugin.menu_func_import)
    bpy.types.TOPBAR_MT_file_import.remove(plugin.menu_func_xray_import)
    bpy.types.TOPBAR_MT_file_export.remove(plugin.menu_func_xray_export)

    # all classes unregister
    modules = get_submodules()
    unregister_modules(modules)
