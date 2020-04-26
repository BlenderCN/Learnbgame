# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from itertools import chain
from pynodes_framework import idref
from converter import Converter
from util import strhash16
import driver, typedesc

import builtin_functions as bf
import modifier_functions as mf
from inspect import getmembers, isfunction


def print_source(source):
    print("*" * 80)
    split_source = source.split('\n')
    for i, line in enumerate(split_source):
        lineno = i + 1
        print(str(lineno).rjust(4, '0') + "  " + line)
    print("*" * 80)


_modifiers = {}

def cache_directory():
    import os
    directory = os.path.dirname(__file__)
    return os.path.join(directory, "__nodecache__")

def modifier_filename(source):
    import hashlib
    source_bytes = source.encode('utf-8')
    return "%s.py" % hashlib.md5(source_bytes).hexdigest()

def load_modifier(source, loaded_files=None):
    import os, pickle
    
    cache_dir = cache_directory()
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    filename = os.path.join(cache_dir, modifier_filename(source))
    if os.path.exists(filename):
        f = open(filename, 'rb')
        mod = pickle.load(f)
        f.close()
    else:
        conv = Converter()
        try:
            mod = conv.generate(source)
        except:
            print_source(source)
            raise

        if mod:
            # Cache the modifier using pickle
            # NB: The OSL library uses a bytecode format (".oso") for the purpose of caching
            # precompiled shaders which can be parsed very quickly.
            # Since we are using python here home-made bytecode would be more difficult,
            # but pickle does essentially the same.
            f = open(filename, 'wb')
            pickle.dump(mod, f)
            f.close()

    if loaded_files is not None:
        loaded_files.add(filename)

    if mod:
        _modifiers[mod.name] = mod

        if mod.metadata.get("widget", "") == "node":
            mod.node_cls = create_auto_node(mod)
            bpy.utils.register_class(mod.node_cls)

    return mod

def unload_modifier(name):
    if name in _modifiers:
        mod = _modifiers[name]

        # unregister automated node classes
        node_cls = getattr(mod, "node_cls", None)
        if node_cls is not None:
            bpy.utils.unregister_class(node_cls)

        del _modifiers[name]

def modifier_node_name(mod):
    return "ModifierNode_%s" % mod.name

def create_auto_node(mod):
    from mod_node import ModifierNode, mod_node_item
    from typedesc import update_socket_value

    name = modifier_node_name(mod)
    label = mod.metadata.get("label", mod.name)
    node_cls = type(name, (bpy.types.Node, ModifierNode),
                    { "bl_idname" : name,
                      "bl_label" : label,
                      "modifier" : mod.name
                    })

    # apply decorator function for adding to node categories
    cat = mod.metadata.get("category", None)
    if cat:
        node_cls = mod_node_item(cat)(node_cls)

    return node_cls

# automatically generate a 'pass' modifier for a given type
def gen_modifiers_pass():
    for typename in typedesc._basetypes:
        if typename in typedesc._basetypes_default:
            default = typedesc._basetypes_default[typename]
            if default:
                yield "modifier pass_%s (%s in=%s, output %s out=%s) { out = in; }\n" % (typename, typename, default, typename, default)
            else:
                yield "modifier pass_%s (%s in, output %s out) { out = in; }\n" % (typename, typename, typename)

def gen_modifiers_modifier():
    for name, mt in mf.modifier_types():
        if name in mf._skip_modifier:
            continue

        args = []
        args.append("mesh_in")
        prop_decl = []
        prop_decl.append("mesh mesh_in [[string label=\"Mesh\"]]"),
        prop_decl.append("output mesh mesh_out [[string label=\"Mesh\"]]"),
        for prop in mf.modifier_properties(name, mt):
            td, is_struct, is_flag = mf.typedesc_from_rna(prop)
            if td is None:
                continue

            metadata = []
            if (name, prop.identifier) in mf._skip_property:
                metadata.append("string display=\"none\"")
            else:
                metadata.append("string label=\"%s\"" % prop.name)

                if prop.type == 'ENUM':
                    # show enums as node option buttons (not sockets)
                    metadata.append("string display=\"button\"")

                    metadata.append("string widget=\"mapper\"")
                    options = ["%s:%s" % (item.name, item.identifier) for item in prop.enum_items]
                    metadata.append("string options=\"%s\"" % "|".join(item for item in options))

                    if is_flag:
                        metadata.append("int is_flag=1")
                elif prop.type == 'POINTER' and issubclass(type(prop.fixed_type), bpy.types.ID):
                    metadata.append("string widget=\"idref\"")
                    metadata.append("string idtype=\"%s\"" % idref.id_type_identifier(type(prop.fixed_type)))
            metadata = "  [[%s]]" % ", ".join(m for m in metadata) if metadata else ""

            if prop.is_enum_flag:
                value = prop.default_flag
            elif getattr(prop, "array_length", 0) > 0:
                value = prop.default_array
            else:
                value = getattr(prop, "default", None)
            default = typedesc.value_from_rna(td, prop, value)

            prop_decl.append("%s %s%s%s" % (td, prop.identifier, "=%s" % default if default else "", metadata))

            args.append(prop.identifier)

        metadata = []
        metadata.append("string label=\"%s\"" % mt.bl_rna.name)
        metadata.append("string help=\"%s\"" % mt.bl_rna.description)
        if name not in mf._skip_node:
            metadata.append("string widget=\"node\"")
            metadata.append("string category=\"Modifiers\"")
        metadata = "  [[%s]]" % ", ".join(m for m in metadata) if metadata else ""

        source = "modifier %s%s(" % (name.lower(), metadata)

        source += ", ".join("\n    %s" % s for s in prop_decl)

        source += ")\n"
        source += "{\n"
        source += "    mesh_out = mod_%s(%s);\n" % (name.lower(), ", ".join(arg for arg in args))
        source += "}\n"

        yield source

def load_all_modifiers(blang_path):
    for source in gen_modifiers_pass():
        mod = load_modifier(source)

    for source in gen_modifiers_modifier():
        #print("****** MODIFIER *******")
        #print(source)
        #print("***********************")
        mod = load_modifier(source)

    import os

    # XXX TODO automatically clean the cache folder by deleting unused files
    #cache_dir = cache_directory()

    for filename in os.listdir(blang_path):
        f = open(os.path.join(blang_path, filename), 'r')
        source = f.read()
        f.close()
        load_modifier(source)

def unload_all_modifiers():
    mods = [name for name in _modifiers.keys()]
    for name in mods:
        unload_modifier(name)


# builtin symbols, independent of node tree or object
dict_builtin = {}
dict_builtin['DerivedMesh'] = mf.DerivedMesh
for name, func in getmembers(bf, isfunction):
    dict_builtin[name] = func
for name, func in mf.mod_funcs.items():
    dict_builtin[name] = func

"""
def sorted_nodes(node_tree):
    nodes = []
    visited = set()
    def sort_node(node):
        if node in visited:
            return
        visited.add(node)
        for link in node_tree.links:
            if link.to_node == node:
                sort_node(link.from_node)
        nodes.append(node)
    for node in node_tree.nodes:
        sort_node(node)
    return nodes
"""

class NodeTreeCompiler():
    def __init__(self):
        self.mod_map = None
        self.socket_map = None
        self.interface_map = None
        self.scope_id = strhash16("")

    def compile(self, node_tree):
        self.modifiers = []
        self.node_tree(node_tree, {})
        self.sort_modifiers()
        return self.codegen()

    def node_tree(self, node_tree, interface_map):
        prev_mod_map = self.mod_map
        prev_socket_map = self.socket_map
        prev_interface_map = self.interface_map
        self.mod_map = {}
        self.socket_map = {}
        self.interface_map = interface_map

#        nodes = node_tree.nodes
        # NB: sort by node name to ensure a somewhat stable order of nodes.
        # Otherwise simply selecting nodes might require full rebuild of the modifier stack
        nodes = sorted(node_tree.nodes, key=lambda node: node.name)
        for node in nodes:
            self.mod_inst = None

            prev_scope_id = self.scope_id
            self.scope_id = strhash16(node.name, self.scope_id)

            node.compile(self)

            self.scope_id = prev_scope_id

        for link in node_tree.links:
            from_mod, from_param = self.socket_map.get(link.from_socket, (None, None))
            to_mod, to_param = self.socket_map.get(link.to_socket, (None, None))
            if from_mod and to_mod:
                assert(to_param not in to_mod.param_value or not isinstance(to_mod.param_value[to_param], ModifierLink))
                to_mod.param_value[to_param] = ModifierLink(from_mod, from_param)

        self.mod_map = prev_mod_map
        self.socket_map = prev_socket_map
        self.interface_map = prev_interface_map

    def modifier(self, name, layer_name):
        mod = _modifiers[name]
        if layer_name in self.mod_map:
            raise KeyError("Modifier layer %r already exists" % layer_name)
        mod_inst = ModifierInstance(mod, layer_name, self.scope_id)
        self.mod_inst = mod_inst
        self.mod_map[layer_name] = self.mod_inst
        self.modifiers.append(self.mod_inst)
        return mod_inst

    def map_socket(self, mod_inst, param_name, socket):
        if mod_inst is None:
            assert(self.mod_inst is not None) # XXX may support pending parameters later
            mod_inst = self.mod_inst
        self.socket_map[socket] = (mod_inst, param_name)

    def sort_modifiers(self):
        modlist = []
        visited = set()
        def sort_mod(mod):
            if mod in visited:
                return
            visited.add(mod)
            for param in mod.modifier.parameters:
                if not param.is_output:
                    link = mod.param_value.get(param.name, None)
                    if isinstance(link, ModifierLink):
                        sort_mod(link.mod_inst)
            modlist.append(mod)
        for mod in self.modifiers:
            sort_mod(mod)
        self.modifiers = modlist

    def codegen(self):
        conv = Converter()
        conv.module()

        for mod in self.modifiers:
            conv.modinst(mod)

        conv.module_end()

        #print("NodeTree source:")
        #print_source(conv.result)
        code = compile(conv.result, '<string>', 'exec')

        class Generator():
            @staticmethod
            def evaluate(ob, **kwargs):
#                for obmod in ob.modifiers:
#                    # disable modifiers by default, modifier function calls enable them
#                    obmod.show_render = False
#                    obmod.show_viewport = False
#                    obmod.show_in_editmode = False

                driver.object_clear_driver(ob)

                dict_globals = dict_builtin.copy() # don't modify basic common globals
                dict_globals['__object__'] = ob
                dict_globals['__object_add_driver__'] = driver.object_add_driver
                dict_globals['__mesh_output___0'] = mf.DerivedMesh() # XXX can we get rid of the stupid suffix?
                dict_globals.update(kwargs)

                exec(code, dict_globals)

                result = dict_globals['__mesh_output___0']
                result.apply(ob)

        return Generator


class Parameter():
    def __init__(self, name, typedesc, is_output, default, metadata=None):
        self.name = name
        self.typedesc = typedesc
        self.is_output = is_output
        self.default = default
        self.metadata = metadata if metadata else {}


class Modifier():
    def __init__(self, name, metadata=None):
        self.name = name
        self.source = ""
        self.parameters = []
        self.metadata = metadata if metadata else {}

    def parameter(self, *args, **kw):
        self.parameters.append(Parameter(*args, **kw))


class ModifierLink():
    def __init__(self, mod_inst, param_name):
        self.mod_inst = mod_inst
        self.param_name = param_name


from bpy.types import ID
StructRNA = bpy.types.Struct.__bases__[0]

def _modinst_param_arg(typedesc, prop, value):
    b = typedesc.basetype
    if b in {'float', 'int', 'bool'}:
        return repr(value)
    elif b in {'vector', 'point', 'normal'}:
        return "Vector(%s)" % repr(value[:])
    elif b in {'color'}:
        return "Color(%s)" % repr(value[:])
    elif b in {'matrix'}:
        return "Matrix(%s)" % repr(value[:])
    elif b in {'string'}:
        if (prop and prop.type == 'POINTER') or isinstance(value, StructRNA):
            # convert struct objects into bpy path strings
            if isinstance(value, ID):
                return "%r" % idref.get_full_path(value)
            else:
                # XXX unsupported
                return "%r" % ""
        elif (prop and prop.is_enum_flag):
            return "%r" % "|".join(v for v in value)
        else:
            return "%r" % value
    else:
        raise Exception("Unhandled type %r for converting socket value to parameter default" % b)

class ModifierInstance():
    def __init__(self, modifier, name, scope_id):
        self.modifier = modifier
        key = strhash16(name, scope_id)
        self.name = "%s%d" % (modifier.name, key)
        self.param_value = {}

    def parameter(self, param_name, typedesc, prop, value):
        self.param_value[param_name] = _modinst_param_arg(typedesc, prop, value)
