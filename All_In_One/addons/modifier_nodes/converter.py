### BEGIN GPL LICENSE BLOCK #####
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

from math import *
from mathutils import *
from modgrammar import ParseError

import grammar
from modifier_nodes.symbol import *
from typedesc import *
from blender_data import *


# Helper class that stores a string and format variables
# and can converts into a true string with str()
class Expression():
    def __init__(self, expr, *variables):
        self.expr = expr
        self.variables = variables

    def __str__(self):
        #return "(%r %% (%s))" % ("(%s)" % self.expr, ", ".join("%s_%d" % (var.name, var.scope.uuid) for var in self.variables))
        return self.expr % tuple("%s_%d" % (var.name, var.scope.uuid) for var in self.variables)

    def __repr__(self):
        return str(self)


class FunctionDesc():
    """ Function signature descriptor """

    def __init__(self, name, impl, return_typedesc=TypeVoid, formal_params=None):
        self.name = name
        self.impl = impl
        self.params = [FunctionOutputDesc(return_typedesc),]
        if formal_params:
            self.params += formal_params
        self.use_object = False

    def input_param(self, typedesc):
        self.params.append((False, typedesc))

    def output_param(self, typedesc):
        self.params.append((True, typedesc))

    def return_param(self, typedesc):
        self.params[0] = (True, typedesc)

    @property
    def input_params(self):
        return [typedesc for is_output, typedesc in self.params if not is_output]

    @property
    def output_params(self):
        return [typedesc for is_output, typedesc in self.params if is_output]

def FunctionInputDesc(typedesc):
    return (False, typedesc)

def FunctionOutputDesc(typedesc):
    return (True, typedesc)

def _make_function_desc():
    _function_desc = []

    # shorthands
    I = FunctionInputDesc
    O = FunctionOutputDesc
    def F(*args, **kw):
        return _function_desc.append(FunctionDesc(*args, **kw))

    import builtin_functions as bf
    import modifier_functions as mf
    from inspect import getmembers

    F('radians',    bf.radians,             TypeFloat,      [I(TypeFloat)])
    F('degrees',    bf.degrees,             TypeFloat,      [I(TypeFloat)])

    F('sin',        bf.sin,                 TypeFloat,      [I(TypeFloat)])
    F('cos',        bf.cos,                 TypeFloat,      [I(TypeFloat)])
    F('tan',        bf.tan,                 TypeFloat,      [I(TypeFloat)])
    F('sincos',     bf.sincos,              TypeVoid,       [I(TypeFloat), O(TypeFloat), O(TypeFloat)])
    F('asin',       bf.asin,                TypeFloat,      [I(TypeFloat)])
    F('acos',       bf.acos,                TypeFloat,      [I(TypeFloat)])
    F('atan',       bf.atan,                TypeFloat,      [I(TypeFloat)])
    F('atan2',      bf.atan2,               TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('sinh',       bf.sinh,                TypeFloat,      [I(TypeFloat)])
    F('cosh',       bf.cosh,                TypeFloat,      [I(TypeFloat)])
    F('tanh',       bf.tanh,                TypeFloat,      [I(TypeFloat)])

    F('pow',        bf.pow,                 TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('exp',        bf.exp,                 TypeFloat,      [I(TypeFloat)])
    F('exp2',       bf.exp2,                TypeFloat,      [I(TypeFloat)])
    F('expm1',      bf.expm1,               TypeFloat,      [I(TypeFloat)])
    F('log',        bf.log,                 TypeFloat,      [I(TypeFloat)])
    F('log2',       bf.log2,                TypeFloat,      [I(TypeFloat)])
    F('log10',      bf.log10,               TypeFloat,      [I(TypeFloat)])
    F('log',        bf.log_var,             TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('logb',       bf.logb,                TypeFloat,      [I(TypeFloat)])

    F('floor',      bf.floor,               TypeFloat,      [I(TypeFloat)])
    F('ceil',       bf.ceil,                TypeFloat,      [I(TypeFloat)])
    F('round',      bf.round,               TypeFloat,      [I(TypeFloat)])
    F('trunc',      bf.trunc,               TypeFloat,      [I(TypeFloat)])

    F('sqrt',       bf.sqrt,                TypeFloat,      [I(TypeFloat)])
    F('inversesqrt', bf.inversesqrt,        TypeFloat,     [I(TypeFloat)])

    F('hypot',      bf.hypot2,              TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('hypot',      bf.hypot3,              TypeFloat,      [I(TypeFloat), I(TypeFloat), I(TypeFloat)])

    F('abs',        bf.abs,                 TypeFloat,      [I(TypeFloat)])
    F('fabs',       bf.abs,                 TypeFloat,      [I(TypeFloat)])
    F('sign',       bf.sign,                TypeInt,        [I(TypeFloat)])

    F('mod',        bf.mod,                 TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('fmod',       bf.mod,                 TypeFloat,      [I(TypeFloat), I(TypeFloat)])

    F('min',        bf.blang_min,           TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('max',        bf.blang_max,           TypeFloat,      [I(TypeFloat), I(TypeFloat)])
    F('clamp',      bf.clamp,               TypeFloat,      [I(TypeFloat), I(TypeFloat), I(TypeFloat)])
    F('mix',        bf.mix,                 TypeFloat,      [I(TypeFloat), I(TypeFloat), I(TypeFloat)])

    F('dot',        bf.dot,                 TypeFloat,      [I(TypeVector), I(TypeVector)])
    F('cross',      bf.cross,               TypeVector,     [I(TypeVector), I(TypeVector)])
    F('length',     bf.length,              TypeFloat,      [I(TypeVector)])
    F('distance',   bf.distance,            TypeFloat,      [I(TypeVector), I(TypeVector)])

    fdesc = FunctionDesc('bdata', bf.bdata, TypeAny,        [I(TypeString)])
    fdesc.use_object = True
    _function_desc.append(fdesc)

    # parameter types are defined in modifier_functions
    for name, func in mf.mod_funcs.items():
        F(name, func, TypeMesh, [I(TypeMesh)] + [I(a) for a in func.argtypes])

    return _function_desc


class Block():
    def __init__(self, uuid, hint, parent):
        self.uuid = uuid
        self.hint = hint
        self.parent = parent
        self.symbols = []
        if parent is None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        self.returned = False   # XXX needed?
        self.tempsym_next = 0
        self.empty = True       # if true, adds a pass statement

    def debug_print(self):
        print("BLOCK:")
        print("  Symbols:")
        for sym in self.symbols:
            print("    %r [%s] : %r" % (sym.name, "local" if sym.scope == self else "extern", sym.value))

    def _tempsym_gen(self):
        name = "temp%d" % self.tempsym_next
        self.tempsym_next += 1
        return name

    def _find_symbol(self, name):
        for sym in reversed(self.symbols):
            if sym.name == name:
                return sym
        if self.parent is not None:
            return self.parent._find_symbol(name)
        if name in _global_syms:
            return _global_syms[name]
        return None

    def get_assignments_map(self, depth):
        assignments = {}
        for sym in reversed(self.symbols):
            if sym.scope.depth > depth:
                continue
            if sym.name in assignments:
                continue
            assignments[sym.name] = sym
        return assignments

    def _find_symbol_decl(self, name):
        for sym in reversed(self.symbols):
            if sym.scope == self and sym.name == name:
                return sym
        return None

    def _find_symbol_extern(self, name):
        for sym in reversed(self.symbols):
            if sym.scope != self and sym.name == name:
                return sym
        return None

    def symbol(self, name):
        sym = self._find_symbol(name)
        if sym is None:
            raise Exception("Symbol %s undeclared" % name)
        return sym

    def assign(self, sym, value):
        nsym = sym.copy_assign(value)
        if not self.returned:
            self.symbols.append(nsym)
        return nsym

    def declare(self, name, typedesc, value=None):
        sym = self._find_symbol_decl(name)
        if sym:
            raise Exception("Symbol %s already declared" % name)
        sym = Symbol(name, self, typedesc, value)
        if not self.returned:
            self.symbols.append(sym)
        return sym

    def declare_temp(self, typedesc, value=None):
        return self.declare(self._tempsym_gen(), typedesc, value)


_function_desc = _make_function_desc()
_global_block = Block(0, 'GLOBAL', None)
_global_syms = {
    '__mesh_output__' : _global_block.declare('__mesh_output__', TypeMesh),
    }

class Converter():
    def __init__(self):
        self.funcname = None
        self.parameters = []
        self.mod = None
        self.mod_types = set()
        self.result = ""

        self.indent = 0
        self.scope_uuid_next = 1
        self.scopestack = []
        self.return_branches = []

    def scope_uuid_gen(self):
        uuid = self.scope_uuid_next
        self.scope_uuid_next += 1
        return uuid

    @property
    def scope(self):
        return self.scopestack[-1]

    def line(self, text):
        self.result += "    " * self.indent + text + "\n"
        self.scope.empty = False

    def symbol_string(self, sym):
        return "%s_%d" % (sym.name, sym.scope.uuid)

    def expression(self):
        return Expression()

    def generate(self, source):
        try:
#            result = grammar.modifier_parser.parse_text(source, reset=True, eof=True, matchtype='complete')
            result = grammar.modifier_parser.parse_text(source, reset=True, eof=True)
        except ParseError as err:
            print("Error: line %d: %s" % (err.line, err.message))
            split_buffer = err.buffer.split('\n')
            print(split_buffer[err.line])
            if err.col > 0:
                print("%s^" % (" " * (err.col-1) if err.col > 0 else "",))
            result = None

        if result:
            result.codegen(self)
        if self.mod is not None:
            self.mod.source = self.result

        return self.mod


    ### Module ###

    def module(self):
        self.scopestack.append(Block(self.scope_uuid_gen(), 'MODULE', None))

    def module_end(self):
        self.scopestack = []

        # insert header and modifier functions into result
        header = "import bpy\n" \
                 "from mathutils import *\n" \
                 "\n"
        self.result = header \
                      + "\n".join(mod_type.source for mod_type in self.mod_types) \
                      + self.result


    ### Modifier ###

    def modifier(self, name, metadata):
        # transform into dict, drop typespecs (not needed for python)
        metadata = {md[1] : md[2] for md in metadata} if metadata else {}

        from generator import Modifier
        self.mod = Modifier(name, metadata)

        self.function(name)

    def modifier_body(self):
        self.function_body()

    def modifier_return(self):
        self.function_return()

    def modifier_parameter(self, name, typedesc, is_output, default, metadata):
        # transform into dict, drop typespecs (not needed for python)
        metadata = {md[1] : md[2] for md in metadata} if metadata else {}

        self.mod.parameter(name, typedesc, is_output, default, metadata)
        self.function_parameter(name, typedesc, is_output, default)


    ### Modifier Instance ###

    def modinst(self, modinst):
        from generator import ModifierLink

        self.mod_types.add(modinst.modifier)

        input_args = []
        output_args = []
        for param in modinst.modifier.parameters:
            name = "%s_%s" % (modinst.name, param.name)
            if param.is_output:
                sym = self.declare(name, param.typedesc)
                output_args.append(self.symbol_string(sym))
            else:
                if param.name in modinst.param_value:
                    value = modinst.param_value[param.name]
                    if isinstance(value, ModifierLink):
                        rhs_name = "%s_%s" % (value.mod_inst.name, value.param_name)
                        rhs_sym = self.scope.symbol(rhs_name)
                        sym = self.type_convert(param.typedesc, rhs_sym)
                        arg = self.symbol_string(sym)
                    else:
                        arg = value
                    input_args.append("_%s=%s" % (param.name, arg))
        
        source = ""
        if output_args:
            source += "%s = " % ", ".join(arg for arg in output_args)
        source += "%s(%s)" % (modinst.modifier.name, ", ".join(arg for arg in input_args))

        self.line(source)


    ### Function ###

    def function(self, name):
        self.funcname = name

        # NB: scopestack[0] is the return scope,
        # the actual base scope is created in function_body
        self.scopestack.append(Block(self.scope_uuid_gen(), 'RETURN', None))

    def function_body(self):
        # NB: add '_' prefix to avoid python keywords
        self.line("def %s(%s):" % (self.funcname, ", ".join("_%s=%r" % (param.name, param.default) for param in self.parameters if not param.is_output)))
        # initialize parameter symbols
        for param in self.parameters:
            sym = self.scope.declare(param.name, param.typedesc, param.default)

        self.scope_begin()
        self.indent += 1

        self.line("global %s" % ", ".join(self.symbol_string(sym) for sym in _global_syms.values()))

        for param in self.parameters:
            if param.is_output:
                # initial output parameter value for valid return statement
                self.line("%s_%d = %r" % (param.name, self.scope.parent.uuid, param.default))
            else:
                # for name-based access to input symbols, make a copy with scope uuid appended
                self.line("%s_%d = _%s if _%s is not None else %r" % (param.name, self.scope.parent.uuid, param.name, param.name, self.default_value(param.typedesc)))

    def function_return(self):
        self.merge_returns()
        self.scope_end()

        # return output parameters values
        return_syms = [self.scope.symbol(param.name) for param in self.parameters if param.is_output]
        return_args = ["None" if sym is None else ("%s" % self.symbol_string(sym)) for sym in return_syms]
        self.line("return %s" % ", ".join(arg for arg in return_args))
        self.indent -= 1

        self.scopestack = []
        self.parameters = []

    def function_parameter(self, name, typedesc, is_output, default):
        from generator import Parameter
        self.parameters.append(Parameter(name, typedesc, is_output, default))


    ### Symbols ###

    def declare(self, name, typedesc, value=None):
        sym = self.scope.declare(name, typedesc, value)
        if value is not None:
            self.line("%s = %r" % (self.symbol_string(sym), value))
        return sym

    def declare_temp(self, typedesc, value=None):
        sym = self.scope.declare_temp(typedesc, value)
        if value is not None:
            self.line("%s = %r" % (self.symbol_string(sym), value))
        return sym

    def assign(self, name, rhs_sym, array_index_sym=None):
        scope = self.scope
        sym = scope.symbol(name)

        rhs_sym = self.type_convert(sym.typedesc, rhs_sym) # make sure we have a matching type
        sym = scope.assign(sym, rhs_sym.value)
        # copy semantics
        if rhs_sym.typedesc.basetype == 'mesh':
            copy_str = "%s.copy()" % self.symbol_string(rhs_sym)
        else:
            copy_str = self.symbol_string(rhs_sym)
        self.line("%s%s = %s" % (self.symbol_string(sym), "" if array_index_sym is None else "[%s]" % self.symbol_string(array_index_sym), copy_str))
        return sym

    def variable_ref(self, name, array_index_sym=None):
        scope = self.scope
        sym = scope.symbol(name)

        if array_index_sym is None:
            return sym
        else:
            deref_type = sym.typedesc.deref()
            lhs_sym = self.declare_temp(deref_type, None)
            self.line("%s = %s[%s]" % (self.symbol_string(lhs_sym), self.symbol_string(sym), self.symbol_string(array_index_sym)))
            return lhs_sym


    ### Scope ###

    def _scope_push(self, hint):
        block = Block(self.scope_uuid_gen(), hint, self.scope)
        self.scopestack.append(block)
        return block

    def _scope_pop(self):
        block = self.scopestack.pop()
        if not block.empty:
            self.scope.empty = False
        return block

    def merge_scope(self, branch):
        scope = self.scope
        if scope.returned:
            return

        if branch.returned:
            scope.returned = True
            return

    def merge_conditional(self, branch_if, branch_else):
        scope = self.scope
        if scope.returned:
            return

        if branch_if.returned and branch_else.returned:
            scope.returned = True
            return

    def merge_returns(self):
        scope = self.scope

    def scope_begin(self):
        self._scope_push('SCOPE')

    def scope_end(self):
        branch = self._scope_pop()
        self.merge_scope(branch)

    def conditional_if(self, condition):
        scope = self.scope
        self.line("if %s:" % self.symbol_string(condition))
        scope.branch_if = self._scope_push('IF')
        self.indent += 1

    def conditional_else(self, condition):
        if self.scope.empty:
            self.line("pass")

        self._scope_pop()
        self.indent -= 1

        scope = self.scope
        self.line("else:")
        scope.branch_else = self._scope_push('ELSE')
        self.indent += 1

    def conditional_end_if(self):
        if self.scope.empty:
            self.line("pass")

        self._scope_pop()
        self.indent -= 1

        branch_if = self.scope.branch_if
        branch_else = self.scope.branch_else
        self.merge_conditional(branch_if, branch_else)

    def set_return(self, sym):
        # return output parameters values
        output_params = [param for param in self.parameters if param.is_output]
        return_syms = [sym] + [self.scope.symbol(param.name) for param in output_params[1:]]
        return_args = ["None" if sym is None else ("%s" % self.symbol_string(sym)) for sym in return_syms]
        self.line("return %s" % ", ".join(arg for arg in return_args))

        self.scope.returned = True
        self.return_branches.append(self.scope)


    ### Types ###

    @classmethod
    def default_value(cls, typedesc):
        from modifier_functions import DerivedMesh
        b = typedesc.basetype
        if b in {'void', 'any'}:
            return None
        elif b == 'float':
            return 0.0
        elif b == 'int':
            return 0
        elif b == 'bool':
            return False
        elif b == 'color':
            return Color((0, 0, 0))
        elif b in {'vector', 'point'}:
            return Vector((0, 0, 0))
        elif b == 'normal':
            return Vector((0, 0, 1))
        elif b == 'matrix':
            return Matrix.Identity(4)
        elif b == 'string':
            return ""
        elif b == 'mesh':
            return DerivedMesh()
        else:
            raise Exception("Unhandled default value type %r" % b)

    def define_int(self, value, driven=False):
        return self.declare_temp(TypeInt, int(value))

    def define_float(self, value, driven=False):
        return self.declare_temp(TypeFloat, float(value))

    def define_bool(self, value, driven=False):
        return self.declare_temp(TypeBool, bool(value))

    def define_color(self, value, driven=False):
        return self.declare_temp(TypeColor, Color((float(value[0]), float(value[1]), float(value[2]))))

    def define_vector(self, value, basetype='vector', driven=False):
        return self.declare_temp(TypeDesc(basetype), Vector((float(value[0]), float(value[1]), float(value[2]))))

    def define_matrix(self, value, driven=False):
        return self.declare_temp(TypeMatrix, Matrix(tuple(value[0:16])))

    def define_string(self, value, driven=False):
        return self.declare_temp(TypeString, str(value))

    def define_mesh(self, value, driven=False):
        return self.declare_temp(TypeMesh, set())

    def type_constructor(self, typedesc, args):
        try:
            if typedesc.basetype == 'int':
                if isinstance(args, Symbol):
                    return self.to_int(args)
                else:
                    return self.define_int(args)
            elif typedesc.basetype == 'float':
                if isinstance(args, Symbol):
                    return self.to_float(args)
                else:
                    return self.define_float(args)
            elif typedesc.basetype == 'bool':
                if isinstance(args, Symbol):
                    return self.to_bool(args)
                else:
                    return self.define_bool(args)
            # for vector types first try to construct float arguments
            elif typedesc.basetype in {'color', 'vector', 'normal', 'point', 'matrix'}:
                try:
                    sym_args = [self.to_float(c) if isinstance(c, Symbol) else self.define_float(c) for c in args]
                    if typedesc.basetype in {'vector', 'normal', 'point'}:
                        return self.declare_temp(typedesc, Expression("Vector((%s, %s, %s))", sym_args[0], sym_args[1], sym_args[2]))
                    elif typedesc.basetype == 'color':
                        return self.declare_temp(typedesc, Expression("Color((%s, %s, %s))", sym_args[0], sym_args[1], sym_args[2]))
                    elif typedesc.basetype == 'matrix':
                        raise Exception("Not implemented yet")
                except:
                    if isinstance(args, Symbol):
                        if typedesc.basetype == 'color':
                            return self.to_color(args)
                        elif typedesc.basetype in {'vector', 'point', 'normal'}:
                            return self.to_vector(args)
                        elif typedesc.basetype == 'matrix':
                            return self.to_matrix(args)
                    else:
                        raise
            elif typedesc.basetype == 'string':
                if isinstance(args, Symbol):
                    return self.to_string(args)
                else:
                    return self.define_string(args)
            elif typedesc.basetype == 'mesh':
                if isinstance(args, Symbol):
                    return self.to_mesh(args)
                else:
                    return self.define_mesh(args)
            else:
                raise Exception("Unknown type %r" % typedesc.basetype)
        except:
            raise Exception("Cannot construct %s from %r" % (str(typedesc), args))

    def to_float(self, sym):
        t = sym.typedesc.basetype
        if t == 'float':
            return sym
        elif t in {'int', 'bool', 'any'}:
            return self.declare_temp(TypeFloat, Expression("float(%s)", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'float'))

    def to_int(self, sym):
        t = sym.typedesc.basetype
        if t == 'int':
            return sym
        elif t in {'float', 'bool', 'any'}:
            return self.declare_temp(TypeInt, Expression("int(%s)", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'int'))

    def to_bool(self, sym):
        t = sym.typedesc.basetype
        if t == 'bool':
            return sym
        elif t in {'float', 'int', 'any'}:
            return self.declare_temp(TypeBool, Expression("bool(%s)", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'bool'))

    def to_color(self, sym):
        t = sym.typedesc.basetype
        if t == 'color':
            return sym
        elif t in {'vector', 'point', 'normal', 'any'}:
            # use vector values as color
            return self.declare_temp(TypeColor, Expression("Color(%s[0:3])", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'color'))

    def to_vector(self, sym, typedesc=TypeVector):
        t = sym.typedesc.basetype
        if sym.typedesc == typedesc:
            return sym
        elif t in {'vector', 'point', 'normal', 'color', 'any'}:
            return self.declare_temp(typedesc, Expression("Vector(%s[0:3])", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, str(typedesc)))

    def to_matrix(self, sym):
        t = sym.typedesc.basetype
        if t == 'matrix':
            return sym
        elif t in {'any'}:
            return self.declare_temp(TypeMatrix, Expression("Matrix(%s[0:16])", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'matrix'))

    def to_string(self, sym):
        t = sym.typedesc.basetype
        if t == 'string':
            return sym
        elif t in {'any'}:
            return self.declare_temp(TypeString, Expression("str(%s)", sym))
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'string'))

    def to_mesh(self, sym):
        t = sym.typedesc.basetype
        if t == 'mesh':
            return sym
        else:
            raise Exception("Cannot convert %s to %s" % (t, 'mesh'))

    def to_any(self, sym):
        t = sym.typedesc.basetype
        if t == 'any':
            return sym
        else:
            return self.declare_temp(TypeAny, sym.value)

    def type_convert(self, typedesc, sym):
        if sym.typedesc.array_size != typedesc.array_size:
            raise Exception("Cannot convert array of size %r to size %r" % (sym.typedesc.array_size, typedesc.array_size))

        if typedesc.basetype == 'int':
            return self.to_int(sym)
        elif typedesc.basetype == 'float':
            return self.to_float(sym)
        elif typedesc.basetype == 'bool':
            return self.to_bool(sym)
        elif typedesc.basetype == 'color':
            return self.to_color(sym)
        elif typedesc.basetype in {'vector', 'point', 'normal'}:
            return self.to_vector(sym, typedesc)
        elif typedesc.basetype == 'matrix':
            return self.to_matrix(sym)
        elif typedesc.basetype == 'string':
            return self.to_string(sym)
        elif typedesc.basetype == 'mesh':
            return self.to_mesh(sym)
        elif typedesc.basetype == 'any':
            return self.to_any(sym)
        else:
            raise Exception("Unknown type %r" % typedesc.basetype)

    def bool_neg(self, sym):
        assert(sym.typedesc.basetype == 'bool')
        return self.declare_temp(TypeBool, Expression("not %s", sym))

    # NB: binary boolean ops gracefully accept None arguments for simplicity
    def bool_and(self, sym_a, sym_b):
        if sym_a is None:
            return sym_b
        elif sym_b is None:
            return sym_a
        else:
            assert(sym_a.typedesc.basetype == 'bool' and sym_b.typedesc.basetype == 'bool')
            return self.declare_temp(TypeBool, Expression("%s and %s", rsym_a, rsym_b))

    def bool_or(self, sym_a, sym_b):
        if sym_a is None:
            return sym_b
        elif sym_b is None:
            return sym_a
        else:
            assert(sym_a.typedesc.basetype == 'bool' and sym_b.typedesc.basetype == 'bool')
            return self.declare_temp(TypeBool, Expression("%s or %s", rsym_a, rsym_b))

    def bool_xor(self, sym_a, sym_b):
        if sym_a is None:
            return sym_b
        elif sym_b is None:
            return sym_a
        else:
            assert(sym_a.typedesc.basetype == 'bool' and sym_b.typedesc.basetype == 'bool')
            return self.declare_temp(TypeBool, Expression("%s != %s", rsym_a, rsym_b))

    def binary_op(self, op, sym_a, sym_b):
        type_a = sym_a.typedesc.basetype
        type_b = sym_b.typedesc.basetype
        
        # some shortcuts
        def scalar_math_op(result_type, operation):
            rsym_a = self.type_convert(result_type, sym_a)
            rsym_b = self.type_convert(result_type, sym_b)
            return self.declare_temp(result_type, Expression("%%s %s %%s" % operation, rsym_a, rsym_b))
        def scalar_compare_op(result_type, operation):
            rsym_a = self.type_convert(result_type, sym_a)
            rsym_b = self.type_convert(result_type, sym_b)
            return self.declare_temp(TypeBool, Expression("%%s %s %%s" % operation, rsym_a, rsym_b))
        def float3_result_type():
            type_a = sym_a.typedesc.basetype
            type_b = sym_b.typedesc.basetype
            if type_a == type_b:
                return sym_a.typedesc
            elif type_a == 'color' or type_b == 'color':
                return TypeColor
            else:
                # only exact matches of vector types (handled above)
                # can become anything other than generic vector type
                return TypeVector
        def float3_component_math_op(result_type, operation):
            rsym_a = self.type_convert(result_type, sym_a)
            rsym_b = self.type_convert(result_type, sym_b)
            return self.declare_temp(result_type, Expression("(%%s[0] %s %%s[0], %%s[1] %s %%s[1], %%s[2] %s %%s[2])"
                                                             % (operation, operation, operation),
                                                             rsym_a, rsym_b, rsym_a, rsym_b, rsym_a, rsym_b))
        def mul_v3_fl_op(vec, fac):
            # XXX RGB mix node does some clamping of the factor value to 0..1 range,
            # which makes it useless for generic multiplication ...
            # Instead construct a color from float and then multiply that
            fac = self.type_convert(TypeFloat, fac)
            return self.declare_temp(result_type, Expression("(%s[0] * %s, %s[1] * %s, %s[2] * %s)",
                                                             vec, fac, vec, fac, vec, fac))
        
        if op == '*':
            if type_a in int_types and type_b in int_types:
                result = scalar_math_op(TypeInt, '*')
            elif type_a in scalar_types and type_b in scalar_types:
                result = scalar_math_op(TypeFloat, '*')
            elif type_a in float3_types and type_b in float3_types:
                result = float3_component_math_op(float3_result_type(), '*')
            elif type_a in scalar_types and type_b in float3_types:
                result = mul_v3_fl_op(sym_b, sym_a)
            elif type_a in float3_types and type_b in scalar_types:
                result = mul_v3_fl_op(sym_a, sym_b)
            else:
                raise Exception("NOT IMPLEMENTED")
        elif op == '/':
            if type_a in int_types and type_b in int_types:
                result = scalar_math_op(TypeInt, '/')
            elif type_a in scalar_types and type_b in scalar_types:
                result = scalar_math_op(TypeFloat, '/')
            elif type_a in float3_types and type_b in float3_types:
                result = float3_component_math_op(float3_result_type(), '/')
            elif type_a in float3_types and type_b in scalar_types:
                result = mul_v3_fl_op(sym_a, self.one_over(sym_b))
            else:
                raise Exception("NOT IMPLEMENTED")
        elif op == '%':
            if type_a in int_types and type_b in int_types:
                result = scalar_math_op(TypeInt, '%')
            elif type_a in scalar_types and type_b in scalar_types:
                result = scalar_math_op(TypeFloat, '%')
            else:
                raise Exception("NOT IMPLEMENTED")
        elif op == '+':
            if type_a in int_types and type_b in int_types:
                result = scalar_math_op(TypeInt, '+')
            elif type_a in scalar_types and type_b in scalar_types:
                result = scalar_math_op(TypeFloat, '+')
            elif type_a in float3_types and type_b in float3_types:
                result = float3_component_math_op(float3_result_type(), '+')
            elif type_a in string_types and type_b in string_types:
                result = self.declare_temp(TypeString, Expression("%s + %s", sym_a, sym_b))
            else:
                raise Exception("NOT IMPLEMENTED")
        elif op == '-':
            if type_a in int_types and type_b in int_types:
                result = scalar_math_op(TypeInt, '-')
            elif type_a in scalar_types and type_b in scalar_types:
                result = scalar_math_op(TypeFloat, '-')
            elif type_a in float3_types and type_b in float3_types:
                result = float3_component_math_op(float3_result_type(), '-')
            else:
                raise Exception("NOT IMPLEMENTED")

        elif op == '==':
            result = self.declare_temp(TypeBool, Expression("%s == %s", sym_a, sym_b))
        elif op == '!=':
            result = self.declare_temp(TypeBool, Expression("%s != %s", sym_a, sym_b))
        elif op == '<':
            result = self.declare_temp(TypeBool, Expression("%s < %s", sym_a, sym_b))
        elif op == '<=':
            result = self.declare_temp(TypeBool, Expression("%s <= %s", sym_a, sym_b))
        elif op == '>':
            result = self.declare_temp(TypeBool, Expression("%s > %s", sym_a, sym_b))
        elif op == '>=':
            result = self.declare_temp(TypeBool, Expression("%s >= %s", sym_a, sym_b))

        return result


    ### Function Calls ###

    def function_type_check(self, name, *arg_syms):
        name_found = False
        for fdesc in _function_desc:
            if fdesc.name == name:
                name_found = True

                # XXX for now just checks number of arguments to disambiguate function names.
                # According to OSL spec the types should also be checked,
                # this will require some compatibility test function
                if len(fdesc.params) == len(*arg_syms) + 1: # +1 to account for return parameter
                    return fdesc

        if name_found:
            raise Exception("No matching parameter list for function %s" % name)
        else:
            raise Exception("Unknown function %s" % name)

    def function_call(self, name, *arg_syms):
        fdesc = self.function_type_check(name, arg_syms)

        # NB: first item in func_desc is the return value type, not specified in arg_syms
        input_syms = [rval for (rval, lval), (is_output, typedesc) in zip(arg_syms, fdesc.params[1:]) if not is_output]
        return_typedesc = fdesc.params[0][1]
        return_sym = self.declare_temp(return_typedesc) if return_typedesc.basetype != 'void' else None
        output_syms = ([return_sym] if return_sym else []) + [lval for (rval, lval), (is_output, typedesc) in zip(arg_syms, fdesc.params[1:]) if is_output]

        input_args = [self.symbol_string(sym) for sym in input_syms]
        if fdesc.use_object:
            input_args = ["__object__"] + input_args
        output_args = [self.symbol_string(sym) for sym in output_syms]
        fname = fdesc.impl.__name__ if hasattr(fdesc.impl, "__name__") else name
        self.line("%s%s(%s)" % ("%s = " % ", ".join(a for a in output_args) if output_args else "", fname, ", ".join(a for a in input_args)))

        if return_sym:
            return_sym.value = Expression(self.symbol_string(return_sym))

        return return_sym


    ### RNA paths ###

    def rna_path(self, base, struct_path, prop, prop_index):
        self.line("__object_add_driver__(%r, %r, %r, %r)" % (base, struct_path, prop, prop_index))

        path_value = rna_path_value(base, struct_path, prop, prop_index)
        return self.declare_temp(TypeAny, path_value)


    ### Comments ###

    def comment(self, text):
        split_text = text.split('\n')
        for line in split_text:
            self.line("# %s" % line)
