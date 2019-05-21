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

from modgrammar import *
from typedesc import *
import re

grammar_whitespace_mode = 'optional'
# extended whitespace, including C/C++ style comments
grammar_whitespace = re.compile(r'(\s+(//.*?((\r\n?)|\n)|/\*.*?\*/)?)+', re.S)

def print_grammar(grammar):
    def elements_str(g, depth=0):
        if g is None:
            return ""
        s = "  " * depth + repr(g)
        if g.elements:
            s += "[\n" + ",\n".join(elements_str(e, depth+1) for e in g.elements) + "\n" + "  " * depth + "]"
        return s
    print(elements_str(grammar))

class Digits(Grammar):
    grammar = (WORD('0-9', fullmatch=True))
    grammar_collapse = True

class Sign(Grammar):
    grammar = (OPTIONAL(L('+') | L('-')))
    grammar_collapse = True

class Exponent(Grammar):
    grammar = (L('e'), Sign, Digits)
    grammar_collapse = True
    grammar_whitespace_mode = 'explicit'

class Integer(Grammar):
    grammar = (Sign, Digits)

    def grammar_elem_init(self, sessiondata):
        self.value = int(self.string)

    def codegen(self, conv):
        return conv.define_int(self.value)

class FloatingPointDecimals(Grammar):
    grammar = (L('.'), Digits, OPTIONAL(Exponent))
    grammar_collapse = True
    grammar_whitespace_mode = 'explicit'

class FloatingPointFull(Grammar):
    grammar = (Digits, L('.'), Digits, OPTIONAL(Exponent))
    grammar_collapse = True
    grammar_whitespace_mode = 'explicit'

class FloatingPoint(Grammar):
    grammar = (OR((Sign, FloatingPointFull), FloatingPointDecimals))

    def grammar_elem_init(self, sessiondata):
        self.value = float(self.string)

    def codegen(self, conv):
        return conv.define_float(self.value)

class Number(Grammar):
    grammar = (Integer | FloatingPoint)

    def codegen(self, conv):
        return self[0].codegen(conv)

    def evaluate(self):
        return self[0].value

class StringLiteral(Grammar):
    grammar = (L('"'), OPTIONAL(WORD('^"', fullmatch=True)), L('"'))
    # XXX how can nested strings/escaping be made to work?
    #grammar = (OR((L('"'), WORD('^"'), L('"')), (L('\''), WORD('^\''), L('\''))))
    #grammar = (EXCEPT(L('"'), L('\\"')), WORD('^"'), EXCEPT(L('"'), L('\\"')))

    def grammar_elem_init(self, sessiondata):
        self.value = self[1].string if self[1] else ""

    def codegen(self, conv):
        return conv.define_string(self.value)

    def evaluate(self):
        return self.value

class Boolean(Grammar):
    grammar = (L('true') | L('false'))

    def grammar_elem_init(self, sessiondata):
        self.value = True if self[0].string == 'true' else False

    def codegen(self, conv):
        return conv.define_bool(self.value)

    def evaluate(self):
        return self.value


class Identifier(Grammar):
    grammar = (WORD('_a-zA-Z', '_a-zA-Z0-9', fullmatch=True))
    grammar_collapse = True

class OutputSpec(Grammar):
    grammar = (OPTIONAL(L('output')))
    grammar_collapse = True

# types that require value initializer
class SimpleTypeNameInit(Grammar):
    grammar = (L('float') | L('int') | L('bool') | L('color') | L('vector') | L('point') | L('normal') | L('matrix') | L('string'))
    grammar_collapse = True

# symbolic types that don't require value
class SimpleTypeNameNoInit(Grammar):
    grammar = (L('void') | L('mesh') | L('any'))
    grammar_collapse = True

class SimpleTypeName(Grammar):
    grammar = (SimpleTypeNameInit | SimpleTypeNameNoInit)
    grammar_collapse = True

# XXX todo add struct support for TypeSpec
class TypeSpecInit(Grammar):
    grammar = (SimpleTypeNameInit)

    def grammar_elem_init(self, sessiondata):
        self.typedesc = TypeDesc(self[0].string)

class TypeSpecNoInit(Grammar):
    grammar = (SimpleTypeNameNoInit)

    def grammar_elem_init(self, sessiondata):
        self.typedesc = TypeDesc(self[0].string)

class TypeSpec(Grammar):
    grammar = (SimpleTypeName)

    def grammar_elem_init(self, sessiondata):
        self.typedesc = TypeDesc(self[0].string)

class SimpleTypeSpec(Grammar):
    grammar = (SimpleTypeName)

    def grammar_elem_init(self, sessiondata):
        self.typedesc = TypeDesc(self[0].string)

class TypeConstructor(Grammar):
    grammar = (TypeSpec, L('('), LIST_OF(REF('Expr'), sep=','), L(')'))

    def codegen(self, conv):
        args = tuple(expr.codegen(conv) for expr in self[2].find_all(Expr))
        sym = conv.type_constructor(self[0].typedesc, args[0] if len(args) == 1 else args)
        return sym

    def evaluate(self):
        values = tuple(expr.evaluate() for expr in self[2].find_all(Expr))
        return values

class Initializer(Grammar):
    grammar = (L('='), REF('Expr'))

    def codegen(self, conv):
        return self[1].codegen(conv)

    def evaluate(self):
        return self[1].evaluate()

# XXX not implemented yet
"""
class ArraySpec(Grammar):
    grammar = (L('['), OPTIONAL(Integer), L(']'))

    def grammar_elem_init(self, sessiondata):
        self.array_index = 0 if self[1] is None else self[1].value
"""

class DefExpr(Grammar):
    grammar = (Identifier, OPTIONAL(Initializer))

    def grammar_elem_init(self, sessiondata):
        self.identifier = self[0].string
        self.initializer = self[1]


class ArrayDeref(Grammar):
    grammar = (L('['), REF('Expr'), L(']'))

    def codegen(self, conv):
        return self[1].codegen(conv)

    def evaluate(self):
        return self[1].evaluate()

class VariableLValue(Grammar):
    # XXX this causes infinite recursion ...
#    grammar = (OR((Identifier, OPTIONAL(ArrayDeref)), (REF('VariableLValue'), ArrayDeref)))
    grammar = (Identifier, OPTIONAL(ArrayDeref))

    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string

    def codegen(self, conv):
        self.array_index_sym = self[1].codegen(conv) if self[1] else None

class ParenExpr(Grammar):
    grammar = (L('('), REF('Expr'), L(')'))

    def codegen(self, conv):
        return self[1].codegen(conv)

    def evaluate(self):
        return self[1].evaluate()

class VariableRef(Grammar):
    grammar = (Identifier, OPTIONAL(ArrayDeref))

    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string

    def codegen(self, conv):
        self.array_index_sym = self[1].codegen(conv) if self[1] else None
        return conv.variable_ref(self.name, self.array_index_sym)

    def lvalue(self, conv):
        return self.name, self.array_index_sym

class FunctionCall(Grammar):
    grammar = (Identifier, L('('), LIST_OF(REF('Expr'), sep=',', min=0), L(')'))

    def grammar_elem_init(self, sessiondata):
        self.func_name = self[0].string
        self.func_args = self[2].find_all(Expr)

    def codegen(self, conv):
        arg_syms = tuple((expr.codegen(conv), expr.lvalue(conv)) for expr in self.func_args)
        return conv.function_call(self.func_name, *arg_syms)


### RNA Path ###

class CollectionKey(Grammar):
    grammar = (L('['), Integer | StringLiteral, L(']'))

    def grammar_elem_init(self, sessiondata):
        self.value = self[1].value

class StructField(Grammar):
    grammar = (Identifier, ZERO_OR_MORE(CollectionKey))

    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string
        self.keys = [key.value for key in self[1].find_all(CollectionKey)]

class ArrayIndex(Grammar):
    grammar = (L('['), Integer, L(']'))

    def grammar_elem_init(self, sessiondata):
        self.value = self[1].value

class Property(Grammar):
    grammar = (Identifier, OPTIONAL(ArrayIndex))

    def grammar_elem_init(self, sessiondata):
        self.prop = self[0].string
        self.index = self[1].value if self[1] else None

class RNAPathBase(Grammar):
    grammar = (L('bdata') | L('object'))
    grammar_collapse = True

class RNAPath(Grammar):
    grammar = (RNAPathBase, OPTIONAL(L('.'), LIST_OF(StructField, sep='.')), L('.'), Property)

    def grammar_elem_init(self, sessiondata):
        self.base = self[0].string
        self.struct_path = self[1][1].string if self[1] else ""
        self.prop = self[3].prop
        self.prop_index = self[3].index

    def codegen(self, conv):
        return conv.rna_path(self.base, self.struct_path, self.prop, self.prop_index)

# RNA path can be parsed as independent string too
rna_path_parser = RNAPath.parser()


### Multiplicative Operators ###

class P0Term(Grammar):
    grammar = (ParenExpr | Number | StringLiteral | Boolean | VariableRef | TypeConstructor | FunctionCall | RNAPath)
    grammar_collapse = True

class P0Expr(Grammar):
    grammar = (P0Term, ONE_OR_MORE(L('*') | L('/') | L('%'), P0Term))

    def codegen(self, conv):
        sym = self[0].codegen(conv)
        for expr in self[1]:
            op = expr[0].string
            op_sym = expr[1].codegen(conv)

            sym = conv.binary_op(op, sym, op_sym)
        return sym

    def evaluate(self):
        value = self[0].evaluate()
        for expr in self[1]:
            rvalue = expr[1].evaluate()
            op = expr[0].string
            value = eval("%s %s %s") % (value, op, rvalue)
        return value


### Additive Operators ###

class P1Term(Grammar):
    grammar = (P0Expr | P0Term)
    grammar_collapse = True

class P1Expr(Grammar):
    grammar = (P1Term, ONE_OR_MORE(L('+') | L('-'), P1Term))

    def codegen(self, conv):
        sym = self[0].codegen(conv)
        for expr in self[1]:
            op = expr[0].string
            op_sym = expr[1].codegen(conv)

            sym = conv.binary_op(op, sym, op_sym)
        return sym

    def evaluate(self):
        value = self[0].evaluate()
        for expr in self[1]:
            rvalue = expr[1].evaluate()
            op = expr[0].string
            value = eval("%s %s %s") % (value, op, rvalue)
        return value


### Relational Operators ###

class P2Term(Grammar):
    grammar = (P0Expr | P1Expr | P0Term)
    grammar_collapse = True

class P2Expr(Grammar):
    grammar = (P2Term, ONE_OR_MORE(L('==') | L('!=') | L('<') | L('<=') | L('>') | L('>='), P2Term))

    def codegen(self, conv):
        sym = self[0].codegen(conv)
        for expr in self[1]:
            op = expr[0].string
            op_sym = expr[1].codegen(conv)

            sym = conv.binary_op(op, sym, op_sym)
        return sym

    def evaluate(self):
        value = self[0].evaluate()
        for expr in self[1]:
            rvalue = expr[1].evaluate()
            op = expr[0].string
            value = eval("%s %s %s") % (value, op, rvalue)
        return value


### Assignment Operators ###

class P3Term(Grammar):
    grammar = (P0Expr | P1Expr | P2Expr | P0Term)
    grammar_collapse = True

class P3Expr(Grammar):
    grammar = (VariableLValue, L('=') | L('*=') | L('/=') | L('%=') | L('+=') | L('-='), P3Term | REF('P3Expr'))

    def codegen(self, conv):
        self[0].codegen(conv)
        name = self[0].name
        array_index_sym = self[0].array_index_sym
        rsym = self[2].codegen(conv)
        op = self[1].string
        if op == '=':
            pass
        else:
            sym = conv.variable_ref(name, array_index_sym)
            if op == '*=':
                rsym = conv.binary_op('*', sym, rsym)
            elif op == '/=':
                rsym = conv.binary_op('/', sym, rsym)
            elif op == '%=':
                rsym = conv.binary_op('%', sym, rsym)
            elif op == '+=':
                rsym = conv.binary_op('+', sym, rsym)
            elif op == '-=':
                rsym = conv.binary_op('-', sym, rsym)
        conv.assign(name, rsym, array_index_sym)
        return rsym

P3Expr.grammar[2].grammar_resolve_refs(recurse=False, follow=False)

class Expr(Grammar):
    grammar = (P3Expr | P2Expr | P1Expr | P0Expr | P0Term)

    def codegen(self, conv):
        return self[0].codegen(conv)

    def evaluate(self):
        return self[0].evaluate()

    def lvalue(self, conv):
        if hasattr(self[0], "lvalue"):
            return self[0].lvalue(conv)
        else:
            return None, None

Initializer.grammar_resolve_refs(recurse=False, follow=False)
ArrayDeref.grammar_resolve_refs(recurse=False, follow=False)
ParenExpr.grammar_resolve_refs(recurse=False, follow=False)
# NB: LIST_OF needs two resolves, there is a nested ref in grammar[1]
TypeConstructor.grammar[2].grammar_resolve_refs(recurse=False, follow=False)
TypeConstructor.grammar[2].grammar[1].grammar_resolve_refs(recurse=False, follow=False)
FunctionCall.grammar[2].grammar_resolve_refs(recurse=False, follow=False)
FunctionCall.grammar[2].grammar[1].grammar_resolve_refs(recurse=False, follow=False)

class ExprStatement(Grammar):
    grammar = (OPTIONAL(Expr), ';')

    def codegen(self, conv):
        if self[0] is not None:
            conv.comment(self.string)
            self[0].codegen(conv)

class CondStatement(Grammar):
    grammar = (L('if'), L('('), Expr, L(')'), REF('Statement'), OPTIONAL(L('else'), REF('Statement')))

    def codegen(self, conv):
        conv.comment("if (%s)" % self[2].string)
        cond_expr_sym = self[2].codegen(conv)
        
        conv.conditional_if(cond_expr_sym)
        self[4].codegen(conv)
        conv.conditional_else(cond_expr_sym)
        if self[5] is not None:
            conv.comment("else // %s" % self[2].string)
            self[5][1].codegen(conv)
        conv.conditional_end_if()

class ScopedStatements(Grammar):
    grammar = (L('{'), REF('StatementList'), L('}'))

    def codegen(self, conv):
        conv.comment("{")
        conv.scope_begin()
        self[1].codegen(conv)
        conv.comment("}")
        conv.scope_end()

class ReturnStatement(Grammar):
    grammar = (L('return'), OPTIONAL(Expr), L(';'))

    def codegen(self, conv):
        conv.comment(self.string)
        sym = self[1].codegen(conv) if self[1] else None
        conv.set_return(sym)

class VariableDeclaration(Grammar):
    grammar = (TypeSpec, LIST_OF(DefExpr, sep=','), L(';'))

    def codegen(self, conv):
        typedesc = self[0].typedesc
        for def_expr in self[1].find_all(DefExpr):
            value = def_expr.initializer.codegen(conv).value if def_expr.initializer else None
            conv.declare(def_expr.identifier, typedesc, value)

class LocalDeclaration(Grammar):
    grammar = (VariableDeclaration)

    def codegen(self, conv):
        conv.comment(self.string)
        self[0].codegen(conv)

class Statement(Grammar):
    grammar = (ReturnStatement | ExprStatement | ScopedStatements | LocalDeclaration | CondStatement)

    def codegen(self, conv):
        self[0].codegen(conv)

CondStatement.grammar_resolve_refs(recurse=False, follow=False)
CondStatement.grammar[5].grammar[0].grammar_resolve_refs(recurse=False, follow=False)

class StatementList(Grammar):
    grammar = (ZERO_OR_MORE(Statement))

    def codegen(self, conv):
        for s in self[0]:
            s.codegen(conv)

ScopedStatements.grammar_resolve_refs(recurse=False, follow=False)


### Meta Data ###

class MetaData(Grammar):
    grammar = (SimpleTypeSpec, Identifier, Initializer)

    def grammar_elem_init(self, sessiondata):
        self.typedesc = self[0].typedesc
        self.name = self[1].string
        self.value = self[2].evaluate()

class MetaDataBlock(Grammar):
    grammar = (L('[['), LIST_OF(MetaData, sep=','), L(']]'))

    def grammar_elem_init(self, sessiondata):
        self.metadata = [(md.typedesc, md.name, md.value) for md in self[1].find_all(MetaData)]


# XXX texture node group elements, ignore for now
"""
class TextureFormalParam(Grammar):
    grammar = (OutputSpec, TypeSpec, Identifier, Initializer)

    def grammar_elem_init(self, sessiondata):
        self.is_output = bool(self[0])
        self.typedesc = self[1].typedesc
        self.name = self[2].string
        self.initializer = self[3]

class TextureFormalParams(Grammar):
    grammar = (LIST_OF(TextureFormalParam, sep=',', min=0))
    grammar_collapse = True

class Texture(Grammar):
    grammar = (L('texture'), Identifier, '(', TextureFormalParams, ')', '{', StatementList, '}')

    def grammar_elem_init(self, sessiondata):
        self.name = self[1]
        self.params = self[3].find_all(TextureFormalParam)
        self.statements = self[6]

        #print_grammar(self)

    def codegen(self, conv):
        conv.function(self.name, self.params)
        ntree = conv.node_tree

        self.statements.codegen(conv)

        conv.function_return()

        return ntree

class TextureFile(Grammar):
    grammar = (Texture)

    def grammar_elem_init(self, sessiondata):
        self.texture = self[0]

    def codegen(self, prefix):
        conv = Converter(prefix)
        return self.texture.codegen(conv)
"""

class ModifierFormalParam(Grammar):
    grammar = (OutputSpec, OR((TypeSpecInit, Identifier, Initializer), (TypeSpecNoInit, Identifier)), OPTIONAL(MetaDataBlock))

    def grammar_elem_init(self, sessiondata):
        self.is_output = bool(self[0])
        self.typedesc = self[1][0].typedesc
        self.name = self[1][1].string
        self.initializer = self[1][2] if len(self[1].elements) > 2 else None
        self.metadata = self[2].metadata if self[2] else None

class ModifierFormalParams(Grammar):
    grammar = (LIST_OF(ModifierFormalParam, sep=',', min=0))
    grammar_collapse = True

class Modifier(Grammar):
    grammar = (L('modifier'), Identifier, OPTIONAL(MetaDataBlock), '(', ModifierFormalParams, ')', '{', StatementList, '}')

    def grammar_elem_init(self, sessiondata):
        self.name = self[1].string
        self.params = self[4].find_all(ModifierFormalParam)
        self.statements = self[7]
        self.metadata = self[2].metadata if self[2] else None

    def codegen(self, conv):
        conv.modifier(self.name, self.metadata)

        # return param
        # XXX not used in modifier functions, makes it easier to assign names etc.
        #conv.modifier_parameter(None, self.return_typespec.typedesc, True, None)
        # formal params
        for param in self.params:
            init_value = param.initializer.evaluate() if param.initializer else None
            conv.modifier_parameter(param.name, param.typedesc, param.is_output, init_value, param.metadata)

        conv.modifier_body()
        self.statements.codegen(conv)
        conv.modifier_return()

class ModifierFile(Grammar):
    grammar = (Modifier)

    def grammar_elem_init(self, sessiondata):
        self.modifier = self[0]

    def codegen(self, conv):
        self.modifier.codegen(conv)

# debugging code for finding unresolved refs
"""
def grammar_search_refs(g):
    refs = []
    visited = set()
    def add_ref_paths(g, path):
        if g in visited:
            return
        visited.add(g)
        for i, e in enumerate(g.grammar):
            if e.__name__ == '<REF>':
#                refs.append("%s - %s" % (path, e.string))
                refs.append("%s/%d" % (path, i))
            else:
                add_ref_paths(e, "%s/%d - %s" % (path, i, e.__name__))
    add_ref_paths(g, g.__name__)
    return refs
refs = grammar_search_refs(ModifierFile)
for r in refs:
    print(r)
"""

if False:
    ### GRAMMAR DEBUGGING ###
    import sys
    from modgrammar.debugging import *

    class ModifierGrammarDebugger(GrammarDebugger):
        def __init__(self):
            GrammarDebugger.__init__(self)
            self.type_constructor = False

        def match_success(self, grammar, pos, text, substack, matched):
            if self.in_terminal:
                return
            print("--- {0:>5} : {1}".format(pos, self.stack_summary([substack])))

        def error_left_recursion(self, stack):
            print("LEFT RECURSION!")

    #sys.stdout.writelines(generate_ebnf(ModifierFile))

    modifier_parser = ModifierFile.parser(debug=ModifierGrammarDebugger(), debug_flags=DEBUG_SUCCESSES)
    #########################
else:
    modifier_parser = ModifierFile.parser()
