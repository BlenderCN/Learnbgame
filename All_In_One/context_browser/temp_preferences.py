import bpy
import types
from traceback import print_exc
from inspect import isfunction, ismethod
from .addon import TEMP_PREFS_ID, prefs, temp_prefs
from .constants import (
    ICON_UNKNOWN, ICON_FOLDER, ICON_FUNC, ICON_PROP, ICON_NONE,
    TOOLTIP_LEN,
    get_icon)
from .utils.collection_utils import sort_collection


def islist(data):
    return isinstance(
        data, (
            list,
            tuple,
            bpy.types.bpy_func,
            bpy.types.bpy_prop_collection
        )
    )


def isfunc(obj):
    return isinstance(obj, types.BuiltinFunctionType) or \
        isinstance(obj, types.BuiltinMethodType) or \
        isfunction(obj) or ismethod(obj)


class ContextData:
    def __init__(self):
        self.path = "C"
        self.data = None
        self.properties = []
        self.functions = []

    def eval_path(self, path, globals=None, locals=None):
        if globals:
            self.eval_globals = globals
        if locals:
            self.eval_locals = locals

        return eval(path, self.eval_globals, self.eval_locals)

        return None

    def add_col_item(self, col, item_type, name=None, data=None):
        item = col.add()
        item.type = item_type
        if name is not None:
            item.name = name
        if data is not None:
            item.data = data

    def add_info_item(self, item_type, name=None, data=None):
        self.add_col_item(self.tpr.info_list, item_type, name, data)

    def add_obj_item(self, item_type, name=None, data=None):
        self.add_col_item(self.tpr.obj_list, item_type, name, data)

    def add_header_item(self, label, icon='NONE'):
        if self.header and getattr(self, self.header, None) and \
                len(self.tpr.info_list):
            self.add_info_item('SPACER')

        self.header = label
        self.add_info_item('GROUP', label, icon)

        if not hasattr(TempPreferences, label):
            setattr(
                TempPreferences, label,
                bpy.props.BoolProperty(
                    default=True, update=TempPreferences.update_header))

    def add_properties(self):
        tpr = temp_prefs()
        self.add_header_item("Properties", ICON_PROP)
        if not getattr(tpr, "Properties"):
            return

        for name in self.properties:
            if not hasattr(self.data, name):
                continue

            self.add_info_item('PROP', name)

    def add_functions(self):
        tpr = temp_prefs()
        self.add_header_item("Functions", ICON_FUNC)
        if not getattr(tpr, "Functions"):
            return

        for name in self.functions:
            func = getattr(self.data, name, None)
            l = name
            r = "(...)"
            doc = getattr(func, "__doc__", None)
            if doc:
                sig, _, _ = doc.partition("\n")
                i = sig.find(":: ")
                if i != -1:
                    sig = sig[i + 3:]
                else:
                    _, _, sig = sig.partition(".")

                l, _, r = sig.partition("(")
                r = "(" + r

            self.add_info_item('FUNC', l, r)

    def parse_list(self):
        groups = dict(FOLDER=[], OTHER=[])

        if hasattr(self.data, "rna_type"):
            self.parse_obj()

        for i, v in enumerate(self.data):
            stri = "[%d]" % i
            label = stri
            item_path = self.path + stri
            label += "|" + v.__class__.__name__

            groups['FOLDER'].append((label, item_path, 'GROUP'))

        for key in ('FOLDER', 'OTHER'):
            group = groups[key]
            for name, path, item_type in group:
                self.add_obj_item(item_type, name, path)

    def parse_alist(self):
        groups = dict(FOLDER=[], OTHER=[])

        if hasattr(self.data, "rna_type"):
            self.parse_obj()

        for i, (k, v) in enumerate(self.data.items()):
            stri = "[%d]" % i
            strk = "['%s']" % k
            k_is_int = isinstance(k, int)
            if k_is_int:
                label = stri
                item_path = self.path + stri
            else:
                label = "%s %s" % (stri, k)
                item_path = self.path + strk

            label += "|" + v.__class__.__name__

            groups['FOLDER'].append((label, item_path, 'GROUP'))

        for key in ('FOLDER', 'OTHER'):
            group = groups[key]
            for name, path, item_type in group:
                self.add_obj_item(item_type, name, path)

    def parse_obj(self):
        pr = prefs()
        tpr = temp_prefs()
        rna_type = getattr(self.data, "rna_type", None)
        if rna_type is None:
            return

        folder_types = {'POINTER', 'COLLECTION'}
        skip_prop_types = set()
        if not pr.show_bool_props:
            skip_prop_types.add('BOOLEAN')
        if not pr.show_int_props:
            skip_prop_types.add('INT')
        if not pr.show_float_props:
            skip_prop_types.add('FLOAT')
        if not pr.show_str_props:
            skip_prop_types.add('STRING')
        if not pr.show_enum_props:
            skip_prop_types.add('ENUM')

        items = dir(self.data)
        for item in items:
            if item.startswith("_"):
                continue

            if hasattr(rna_type, "functions") and item in rna_type.functions:
                self.functions.append(item)
                continue

            if hasattr(rna_type, "properties") and item in rna_type.properties:
                prop = rna_type.properties[item]
                if prop.type not in folder_types:
                    if prop.type not in skip_prop_types:
                        if not pr.show_vector_props and getattr(
                                prop, "is_array", False):
                            continue
                        self.properties.append(item)
                    continue

            item_path = self.path + "." + item
            obj = self.eval_path(item_path)

            if isfunc(obj):
                self.functions.append(item)
                continue

            if obj is None:
                item_name = item + "|None"
                item_type = 'ITEM'
            else:
                item_name = item + "|" + type(obj).__name__
                item_type = 'GROUP'

            self.add_obj_item(item_type, item_name, item_path)

        if pr.group_none:
            sort_collection(tpr.obj_list, lambda item: item.type == 'ITEM')

    def update_lists(self, path, update_breadcrumbs=True):
        self.tpr = tpr = temp_prefs()
        tpr.obj_list.clear()
        tpr.info_list.clear()
        self.functions.clear()
        self.properties.clear()

        C = bpy.context
        while True:
            try:
                self.data = self.eval_path(path, globals(), locals())
                break
            except:
                path = ".".join(path.split(".")[:-1])

        self.path = path

        if self.path != "C":
            par_path, _, part = path.rpartition(".")
            i = part.find("[")
            if i != -1:
                par_path = "%s.%s" % (par_path, part[:i])

            self.add_obj_item('GROUP', "[..]", par_path)

        if update_breadcrumbs:
            tpr.last_path = path
            tpr.update_breadcrumbs(self.path)

        if self.data is None:
            return

        if islist(self.data):
            if hasattr(self.data, "items"):
                self.parse_alist()
            else:
                self.parse_list()

        else:
            self.parse_obj()

        self.update_info_list()

    def update_info_list(self):
        tpr = temp_prefs()
        tpr.info_list.clear()
        self.header = None

        self.add_properties()
        self.add_functions()


class ListItem(bpy.types.PropertyGroup):
    data = bpy.props.StringProperty()
    type = bpy.props.EnumProperty(
        items=(
            ('ITEM', "", ""),
            ('GROUP', "", ""),
            ('SPACER', "", ""),
            ('PROP', "", ""),
            ('FUNC', "", ""),
        ))


class TempPreferences(bpy.types.PropertyGroup):
    breadcrumb_items = []
    cd = ContextData()

    def get_path_items(self, context):
        return self.breadcrumb_items

    def update_path(self, context):
        self.cd.update_lists(self.path, False)

    def update_header(self, context):
        self.cd.update_info_list()

    def obj_list_idx_update(self, context):
        item = self.obj_list[self.obj_list_idx]
        self["obj_list_idx"] = -1
        self.cd.update_lists(item.data)

    obj_list = bpy.props.CollectionProperty(type=ListItem)
    obj_list_idx = bpy.props.IntProperty(update=obj_list_idx_update)
    info_list = bpy.props.CollectionProperty(type=ListItem)
    info_list_idx = bpy.props.IntProperty(get=lambda s: -1)
    last_path = bpy.props.StringProperty(default="C")
    path = bpy.props.EnumProperty(
        name="Path", description="Path",
        items=get_path_items,
        update=update_path)

    def clear_lists(self):
        self.obj_list.clear()
        self.info_list.clear()

    def update_breadcrumbs(self, path):
        self.breadcrumb_items.clear()
        items = path.split(".")
        path = ""
        item_idx = -1
        for item in items:
            idx = item.find("[")
            if idx >= 0:
                a = item[:idx]
                path += a
                self.breadcrumb_items.append((path, a, path))
                a = item[idx:]
                path += a
                self.breadcrumb_items.append((path, a, path))
                path += "."
                item_idx += 2

            else:
                item_idx += 1
                path += item
                self.breadcrumb_items.append((path, item, path))
                path += "."

        self["path"] = item_idx


def register():
    if not hasattr(bpy.types.WindowManager, TEMP_PREFS_ID):
        setattr(
            bpy.types.WindowManager, TEMP_PREFS_ID,
            bpy.props.PointerProperty(type=TempPreferences))


def unregister():
    if hasattr(bpy.types.WindowManager, TEMP_PREFS_ID):
        delattr(bpy.types.WindowManager, TEMP_PREFS_ID)
