import bpy
from bpy.types import Operator
import addon_utils
import sys
import os
import ast
import glob
import csv
import argparse
import bpy

class BPYPropInfo():
    def __init__(self, filename=None, lineno=None, function_name=None, keyword=None, text=None):
        self.filename = filename
        self.lineno = lineno
        self.function_name = function_name
        self.keyword = keyword
        self.text = text

    def __str__(self):
        return "{}({}):{}({}={})".format(self.filename, self.lineno,
                                        self.function_name, self.keyword, self.text)
    def __repr__(self):
        return self.__str__()

class BPYPropExtractor(ast.NodeVisitor):
    TARGET_LIST = {
        # prop
        "IntProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "FloatProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "StringProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "EnumProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "BoolProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "IntVectorProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "FloatVectorProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "BoolVectorProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "CollectionProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        "PointerProperty": [{"keyword": "name", "index": 0}, {"keyword": "description", "index": 1}],
        # layout
        "template_any_ID": {"keyword": "text", "index": 3},
        "template_path_builder": {"keyword": "text", "index": 3},
        "prop": {"keyword": "text", "index": 2},
        "prop_menu_enum": {"keyword": "text", "index": 2},
        "prop_enum": {"keyword": "text", "index": 3},
        "prop_search": {"keyword": "text", "index": 4},
        "operator": {"keyword": "text", "index": 1},
        "operator_menu_enum": {"keyword": "text", "index": 2},
        "label": {"keyword": "text", "index": 0},
        "menu": {"keyword": "text", "index": 1},
    }

    def __init__(self):
        super(BPYPropExtractor, self).__init__()
        self.prop_list = []
        self.prop_error_list = []

    def add_result(self, function_name, keyword, text, lineno):
        self.prop_list.append(BPYPropInfo(
            function_name=function_name, keyword=keyword, text=text,
            lineno=lineno))
    
    def add_error(self, function_name, keyword, dump, lineno):
        self.prop_error_list.append(BPYPropInfo(
            function_name=function_name, keyword=keyword, text=dump, lineno=lineno))

    def get_results(self):
        return self.prop_list, self.prop_error_list
    
    def visit_Call(self, node):
        func_name = None
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        if func_name and (func_name in BPYPropExtractor.TARGET_LIST):
            targets = self.TARGET_LIST[func_name]
            if isinstance(targets, dict):
                targets = [targets]
            for target in targets:
                if len(node.args) > target["index"]:
                    if isinstance(node.args[target["index"]], ast.Str):
                        self.add_result(func_name, target["keyword"], node.args[target["index"]].s, node.lineno)
                    else:
                        self.add_error(func_name, target["keyword"], ast.dump(node.args[target["index"]]), node.lineno)
                for keyword in node.keywords:
                    if keyword.arg == target["keyword"]:
                        if isinstance(keyword.value, ast.Str):
                            self.add_result(func_name, target["keyword"], keyword.value.s, node.lineno)
                        else:
                            self.add_error(func_name, target["keyword"], ast.dump(keyword.value), node.lineno)
        if func_name == "EnumProperty":
            # parse enum items
            items = None
            if len(node.args) > 0:
                items = node.args[0]
            else:
                for keyword in node.keywords:
                    if keyword.arg == "items":
                        items = keyword.value
                        break
            if items is not None:
                parse_succeeded = True
                if isinstance(items, ast.Tuple) or isinstance(items, ast.List):
                    for elt in items.elts:
                        if (isinstance(elt, ast.Tuple) or isinstance(elt, ast.List)) and len(elt.elts) > 1 and isinstance(elt.elts[1], ast.Str):
                            self.add_result(func_name, "items", elt.elts[1].s, node.lineno)
                        else:
                            parse_succeeded = False
                else:
                    parse_succeeded = False
                if not parse_succeeded:
                    self.add_error(func_name, "items", ast.dump(items), node.lineno)
        else:
            pass

def set_translation_item(item, prop, text_ctxt, input_dir, is_error):
    item.msgid = prop.text
    item.function = prop.function_name
    item.keyword = prop.keyword
    item.file_full_path = prop.filename
    item.lineno = prop.lineno
    if input_dir:
        item.file_rel_path = os.path.relpath(prop.filename, input_dir)
    else:
        item.file_rel_path = os.path.basename(prop.filename)
    if prop.function_name == "operator" or prop.function_name == "operator_menu_enum":
        item.ctx = "Operator"
    else:
        item.ctx = "*"

    if not is_error:
        if text_ctxt:
            msgstr = bpy.app.translations.pgettext(item.msgid, text_ctxt)
            if msgstr == item.msgid:
                msgstr = bpy.app.translations.pgettext(item.msgid, item.ctx)
        else:
            msgstr = bpy.app.translations.pgettext(item.msgid, item.ctx)
        if msgstr == item.msgid:
            item.msgstr = ""
        else:
            item.msgstr = msgstr

def build_tralsnation_items(mod, locale, bpy_text, text_ctxt):
    use_international_fonts_backup = bpy.context.user_preferences.system.use_international_fonts
    locale_backup = bpy.context.user_preferences.system.language
    try:
        bpy.context.user_preferences.system.use_international_fonts = True
        bpy.context.user_preferences.system.language = locale
        translation_prop = bpy_text.translation_tools
        translation_prop.items.clear()
        translation_prop.error_items.clear()

        basename = os.path.basename(mod.__file__)
        if basename == "__init__.py":
            input_dir = os.path.dirname(mod.__file__)
            scripts = glob.iglob(os.path.join(input_dir, "**", "*.py"), recursive=True)
        else:
            input_dir = None
            scripts = [mod.__file__]
        found = set()
        for filename in scripts:
            with open(filename, "r", encoding="utf_8_sig") as ifp:
                root = ast.parse(ifp.read())
                hook = BPYPropExtractor()
                hook.visit(root)
                props, errors = hook.get_results()
                for prop in props:
                    if (not prop.text) or (prop.text in found):
                        continue
                    found.add(prop.text)
                    prop.filename = filename
                    item = translation_prop.items.add()
                    set_translation_item(item, prop, text_ctxt, input_dir=input_dir, is_error=False)
                for err in errors:
                    prop.filename = filename                
                    item = translation_prop.error_items.add()
                    set_translation_item(item, prop, text_ctxt, input_dir=input_dir, is_error=True)
    finally:
        bpy.context.user_preferences.system.language = locale_backup
        bpy.context.user_preferences.system.use_international_fonts = use_international_fonts_backup

class TemplateGenerateOperator(Operator):
    bl_idname = "addon_translation_tools.generate_template"
    bl_label = "Parse addon and Generate translation items"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @staticmethod
    def __make_text_name(mod, locale):
        return "{}_translation_{}.py".format(mod.__name__, locale)

    @staticmethod
    def __find_module(addon_file):
        for mod in addon_utils.modules():
            if mod.__file__ == addon_file:
                return mod
        return None

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "TEXT_EDITOR"

    def execute(self, context):
        panel_props = context.scene.translation_tools
        if not (panel_props.addon and panel_props.locale):
            self.report({"ERROR"}, "addon or locale not selected")
            return {"CANCELLED"}
        mod = self.__find_module(panel_props.addon)
        if mod is None:
            self.report({"ERROR"}, "{} could not be found".format(panel_props.addon))
            return {"CANCELLED"}
        locale = panel_props.locale
        name = self.__make_text_name(mod, locale)
        if name in bpy.data.texts:
            text = bpy.data.texts[name]
        else:
            text = bpy.data.texts.new(name=name)
        try:
            panel_props.updatable = False
            text.use_fake_user = True
            props = text.translation_tools
            props.addon_path = panel_props.addon
            props.addon_name = mod.__name__
            props.locale = panel_props.locale
            props.bl_info_name = "translation: {} {}".format(props.addon_name, props.locale)
            props.bl_info_author = "your name <email>"

            text_ctxt = panel_props.text_ctxt if panel_props.use_text_ctxt else None
            build_tralsnation_items(mod, locale, text, text_ctxt)
            if text_ctxt:
                props.text_ctxt = text_ctxt
                props.use_text_ctxt = True
            else:
                props.text_ctxt = mod.__name__
                props.use_text_ctxt = False
            context.space_data.text = text
            
            if len(props.items) == 0:
                self.report({"ERROR"}, "No translation targets")
                bpy.ops.text.unlink()
                return {"CANCELLED"}
            
            bpy.ops.translation_tools.generate_module()
        finally:
            panel_props.updatable = True
        return {"FINISHED"}

MODULE_TEMPLATE = """# -*- coding: utf-8 -*-
# This code is generated by addon_translation_tools.
import bpy
{BL_INFO}
translation_dict = {TRANSLATION_DICT}

if __package__:
    translation_id = __package__
elif __name__ != "__main__":
    translation_id = __name__
else:
    translation_id = __file__

def register(name=None):
    name = name or translation_id
    try:
        bpy.app.translations.register(name, translation_dict)
    except ValueError:
        bpy.app.translations.unregister(name)
        bpy.app.translations.register(name, translation_dict)

def unregister(name=None):
    name = name or translation_id
    bpy.app.translations.unregister(name)

if __name__ == "__main__":
    unregister()
    register()
"""
BL_INFO="""
bl_info = {{
    "name": "{NAME}",
    "version": ({V0}, {V1}, {V2}),
    "author": "{AUTHOR}",
    "tracker_url": "{TRACKER_URL}",
    "category": "Learnbgame",
    "support": "COMMUNITY"
}}
"""

def escape_double_quote(s):
    return s.replace(r'"', r'\"')

class ModuleGenerateOperator(Operator):
    bl_idname = "translation_tools.generate_module"
    bl_label = "Generate the translation module from items"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == "TEXT_EDITOR" and
                    context.space_data.text and
                    len(context.space_data.text.translation_tools.items) > 0)
    def execute(self, context):
        bpy_text = context.space_data.text
        prop = bpy_text.translation_tools
        translation_dict = "{\n"
        translation_dict += r'    "{}": '.format(prop.locale) + "{\n"
        for item in prop.items:
            if not item.msgid or not item.msgstr:
                continue
            msgid = escape_double_quote(item.msgid)
            msgstr = escape_double_quote(item.msgstr)
            if prop.use_text_ctxt:
                ctx = prop.text_ctxt
            else:
                ctx = item.ctx
            if msgid and msgstr:
                translation_dict += r'        ("{}", "{}"): "{}",'.format(ctx, msgid, msgstr) + "\n"

        translation_dict += "    }\n"
        translation_dict += "}"
        
        bl_info = ""
        if prop.mode == "Standalone":
            name = prop.bl_info_name if prop.bl_info_name else "translation: {} {}".format(prop.addon_name, prop.locale)
            bl_info = BL_INFO.format_map({
                "NAME": escape_double_quote(name),
                "V0": prop.bl_info_version[0],
                "V1": prop.bl_info_version[1],
                "V2": prop.bl_info_version[2],
                "AUTHOR": escape_double_quote(prop.bl_info_author),
                "TRACKER_URL": escape_double_quote(prop.bl_info_tracker_url)
                })
        template = MODULE_TEMPLATE.format_map({"BL_INFO": bl_info, "TRANSLATION_DICT": translation_dict})
        bpy_text.clear()
        bpy_text.write(template)

        context.space_data.show_line_numbers = True
        context.space_data.show_syntax_highlight = True
        ret = bpy.ops.text.move(type='FILE_TOP')
        if "FINISHED" not in ret:
            return ret
        ret = bpy.ops.text.run_script()
        if "FINISHED" not in ret:
            return ret

        return {"FINISHED"}
