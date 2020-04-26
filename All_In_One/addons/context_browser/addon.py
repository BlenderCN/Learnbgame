import bpy
import importlib
import os
import pkgutil
import sys
import inspect
import re

BACKGROUND = False
VERSION = (0, 0, 0)
BL_VERSION = (0, 0, 0)
ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
ADDON_ID = os.path.basename(ADDON_PATH)
TEMP_PREFS_ID = "addon_" + ADDON_ID
ADDON_PREFIX = "".join([s[0] for s in re.split(r"[_-]", ADDON_ID)]).upper()
ADDON_PREFIX_PY = ADDON_PREFIX.lower()
MODULE_NAMES = []
MODULE_MASK = None
ICON_ENUM_ITEMS = bpy.types.UILayout.bl_rna.functions[
    "prop"].parameters["icon"].enum_items


def uprefs():
    return getattr(bpy.context, "user_preferences", None) or \
        getattr(bpy.context, "preferences", None)


def uprefs_id():
    return "user_preferences" if hasattr(bpy.context, "user_preferences") \
        else "preferences"


def uprefs_eid():
    return "USER_PREFERENCES" if hasattr(bpy.context, "user_preferences") \
        else "PREFERENCES"


def prefs():
    return uprefs().addons[ADDON_ID].preferences


def temp_prefs():
    return getattr(bpy.context.window_manager, TEMP_PREFS_ID, None)


def init_addon(
        module_mask, use_reload=False, background=False,
        prefix=None, prefix_py=None):
    global VERSION, BL_VERSION, MODULE_MASK, BACKGROUND, \
        ADDON_PREFIX, ADDON_PREFIX_PY
    module = sys.modules[ADDON_ID]
    VERSION = module.bl_info.get("version", VERSION)
    BL_VERSION = module.bl_info.get("blender", BL_VERSION)

    if prefix:
        ADDON_PREFIX = prefix
    if prefix_py:
        ADDON_PREFIX_PY = prefix_py

    MODULE_MASK = module_mask
    for i, mask in enumerate(MODULE_MASK):
        MODULE_MASK[i] = "%s.%s" % (ADDON_ID, mask)

    BACKGROUND = background
    if not BACKGROUND and bpy.app.background:
        return

    def get_module_names(path=ADDON_PATH, package=ADDON_ID):
        module_names = []
        for _, module_name, is_package in pkgutil.iter_modules([path]):
            if module_name == "addon" or module_name.startswith("_"):
                continue

            if is_package:
                for m in get_module_names(
                        os.path.join(path, module_name),
                        "%s.%s" % (package, module_name)):
                    yield m
            else:
                module_names.append("%s.%s" % (package, module_name))

        for module_name in module_names:
            yield module_name

    module_names = []
    for module_name in get_module_names():
        module_names.append(module_name)

    sorted_module_names = []
    for mask in MODULE_MASK:
        rest_module_names = []
        for module_name in module_names:
            if not mask or module_name.startswith(mask):
                sorted_module_names.append(module_name)
            else:
                rest_module_names.append(module_name)
        module_names = rest_module_names

    MODULE_NAMES.clear()
    MODULE_NAMES.extend(sorted_module_names)
    for module_name in MODULE_NAMES:
        if use_reload:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)


def get_classes():
    ret = set()
    bpy_struct = bpy.types.bpy_struct
    mems = set()
    mem_data = []
    for mod in MODULE_NAMES:
        # mod = sys.modules["%s.%s" % (ADDON_ID, mod)]
        mod = sys.modules[mod]
        for name, mem in inspect.getmembers(mod):
            if inspect.isclass(mem) and issubclass(mem, bpy_struct) and \
                    mem not in mems:

                mems.add(mem)
                classes = []

                cprop = bpy.props.CollectionProperty
                pprop = bpy.props.PointerProperty
                for pname, pvalue in vars(mem).items():
                    if not isinstance(pvalue, tuple):
                        continue

                    ptype = pvalue[0]
                    if ptype is cprop or ptype is pprop:
                        classes.append(pvalue[1]["type"])

                if not classes:
                    ret.add(mem)
                else:
                    mem_data.append(
                        dict(
                            mem=mem,
                            classes=classes
                        )
                    )

    mems.clear()

    ret_post = []
    if mem_data:
        mem_data_len = -1
        while len(mem_data):
            if len(mem_data) == mem_data_len:
                for data in mem_data:
                    ret_post.append(data["mem"])
                break

            new_mem_data = []
            for data in mem_data:
                add = True
                for cls in data["classes"]:
                    if cls not in ret and cls not in ret_post:
                        add = False
                        break

                if add:
                    ret_post.append(data["mem"])
                else:
                    new_mem_data.append(data)

            mem_data_len = len(mem_data)
            mem_data.clear()
            mem_data = new_mem_data

    ret = list(ret)
    ret.extend(ret_post)
    return ret


def register_modules():
    if not BACKGROUND and bpy.app.background:
        return

    if not is_28():
        bpy.utils.register_class(TimeoutOperator)

    if hasattr(bpy.utils, "register_module"):
        bpy.utils.register_module(ADDON_ID)
    else:
        for cls in get_classes():
            bpy.utils.register_class(cls)

    for mod in MODULE_NAMES:
        # m = sys.modules["%s.%s" % (ADDON_ID, mod)]
        m = sys.modules[mod]
        if hasattr(m, "register"):
            m.register()


def unregister_modules():
    if not BACKGROUND and bpy.app.background:
        return

    try:
        if not is_28():
            bpy.utils.unregister_class(TimeoutOperator)
    except:
        pass

    for mod in reversed(MODULE_NAMES):
        # m = sys.modules["%s.%s" % (ADDON_ID, mod)]
        m = sys.modules[mod]
        if hasattr(m, "unregister"):
            m.unregister()

    if hasattr(bpy.utils, "unregister_module"):
        bpy.utils.unregister_module(ADDON_ID)
    else:
        for cls in get_classes():
            bpy.utils.unregister_class(cls)


class Timeout:
    bl_idname = "%s.timeout" % ADDON_PREFIX_PY
    bl_label = ""
    bl_options = {'INTERNAL'}
    data = dict()

    idx = bpy.props.IntProperty(
        name="Index", options={'SKIP_SAVE', 'HIDDEN'})
    delay = bpy.props.FloatProperty(
        name="Delay (s)", description="Delay in seconds",
        default=0.0001, options={'SKIP_SAVE', 'HIDDEN'})

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self.finished:
                context.window_manager.event_timer_remove(self.timer)
                self.timer = None
                del self.data[self.idx]
                return {'FINISHED'}

            if self.timer.time_duration >= self.delay:
                self.finished = True

                try:
                    func, params = self.data[self.idx]
                    func(*params)
                except:
                    pass

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.finished = False

        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(
            self.delay, window=context.window)
        return {'RUNNING_MODAL'}


TimeoutOperator = type(
    "%s_OT_timeout" % ADDON_PREFIX, (Timeout, bpy.types.Operator), {})


def timeout(func, *params):
    if is_28():
        from functools import partial
        bpy.app.timers.register(partial(func, *params), first_interval=0.1)
    else:
        idx = len(Timeout.data)
        while idx in Timeout.data:
            idx += 1

        Timeout.data[idx] = (func, params)
        mod = getattr(bpy.ops, ADDON_PREFIX_PY)
        mod.timeout(idx=idx)


def is_28():
    return bpy.app.version >= (2, 80, 0)


def ic(icon):
    if not icon:
        return icon

    if icon in ICON_ENUM_ITEMS:
        return icon

    bl28_icons = dict(
        ZOOMIN="ADD",
        ZOOMOUT="REMOVE",
        GHOST="DUPLICATE",
    )

    if icon in bl28_icons and bl28_icons[icon] in ICON_ENUM_ITEMS:
        return bl28_icons[icon]

    return 'BLENDER'
