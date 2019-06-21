# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 - 2017 Pixar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# ##### END MIT LICENSE BLOCK #####

from .ply import lex as lex
from .ply import yacc as yacc
import random

# vstruct tokens
#
tokens = ('NUMBER',
          'LPAR',
          'RPAR',
          'OP_EQ',
          'OP_NOTEQ',
          'OP_GT',
          'OP_LT',
          'OP_GTEQ',
          'OP_LTEQ',
          'OP_IS',
          'OP_ISNOT',
          'OP_AND',
          'OP_OR',
          'KW_IF',
          'KW_ELSE',
          'KW_CONNECTED',
          'KW_CONNECT',
          'KW_IGNORE',
          'KW_COPY',
          'KW_SET',
          'PARAM',
          'STRING',
          )

# regex for simple tokens
#
# Regular expression rules for simple tokens
t_LPAR = r'\('
t_RPAR = r'\)'
t_OP_EQ = r'=='
t_OP_NOTEQ = r'!='
t_OP_GT = r'>'
t_OP_LT = r'<'
t_OP_GTEQ = r'>='
t_OP_LTEQ = r'<='
t_OP_ISNOT = r'is\wnot'
t_KW_ELSE = r'else'
t_KW_CONNECTED = r'connected'
t_KW_CONNECT = r'connect'
t_KW_IGNORE = r'ignore'
t_KW_COPY = r'copy'
t_STRING = r'"\w+"'
t_PARAM = r'\w+'


# regex rule with action code
#
def t_NUMBER(t):
    r'\d+[0-9\.]*'
    t.value = float(t.value)
    return t


def t_OP_IS(t):
    r'is'
    return t


def t_OP_OR(t):
    r'or'
    return t


def t_OP_AND(t):
    r'and'
    return t


def t_KW_IF(t):
    r'if'
    return t


def t_KW_SET(t):
    r'set'
    return t


# track line numbers
#
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()


def test_lex():
    global lexer
    print('test_lex')
    r = ["connect if underMaterial_singlescatterK > 0 " +
         "or (enableSinglescatter == 1 and (singlescatterK > 0" +
         "or singlescatterK is connected or singlescatterDirectGain > 0 " +
         "or singlescatterDirectGain is connected)) ",
         "connect if ((rrReflectionK is connected or rrReflectionK > 0) " +
         "and enableRR == 1) or underMaterial_walterReflectionK is connected" +
         " else set 0",
         "connect if enableClearcoat == 1 "]
    for s in r:
        print('-' * 80)
        print(s)
        lexer.input(s)
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            print(tok)


# This is the BNF extracted from VirtualStructConditionalGrammar.yy
#
#
# %start statement
# %token <string> NUMBER
# %token <string> STRING
# %token <string> PARAM
# %token LPAR RPAR
# %token OP_EQ OP_NOTEQ
# %token OP_GT OP_LT OP_GTEQ OP_LTEQ
# %token OP_IS OP_ISNOT
# %token OP_AND OP_OR
# %token KW_IF KW_ELSE KW_CONNECTED KW_CONNECT KW_IGNORE KW_COPY KW_SET
# %token UNRECOGNIZED_TOKEN
#
# %left OP_OR
# %left OP_AND
#
# %%
#
# value : STRING
#       | NUMBER
#
# op : OP_EQ
#    | OP_NOTEQ
#    | OP_GT
#    | OP_LT
#    | OP_GTEQ
#    | OP_LTEQ
#
# expr: PARAM op value
#     | OP_AND op value
#     | OP_OR op value
#     | OP_IS op value
#     | KW_IF op value
#     | KW_ELSE op value
#     | KW_CONNECTED op value
#     | KW_CONNECT op value
#     | KW_IGNORE op value
#     | KW_COPY op value
#     | KW_SET op value
#     | PARAM OP_IS KW_CONNECTED
#     | PARAM OP_ISNOT KW_CONNECTED
#     | PARAM OP_IS KW_SET
#     | PARAM OP_ISNOT KW_SET
#     | LPAR expr RPAR
#     | expr OP_AND expr
#     | expr OP_OR expr
#
# action : KW_COPY PARAM
#        | KW_CONNECT
#        | KW_IGNORE
#        | KW_SET STRING
#        | KW_SET NUMBER
#
# statement : action KW_IF expr KW_ELSE action
#           | action KW_IF expr
#           | KW_IF expr KW_ELSE action
#           | action
#           | expr
#

start = 'statement'


def p_value_string(p):
    'value : STRING'
    p[0] = p[1]


def p_value_number(p):
    'value : NUMBER'
    p[0] = p[1]


# op --------------------------------------------------------------------------


def p_op_eq(p):
    'op : OP_EQ'
    p[0] = '=='


def p_op_noteq(p):
    'op : OP_NOTEQ'
    p[0] = '!='


def p_op_gt(p):
    'op : OP_GT'
    p[0] = '>'


def p_op_lt(p):
    'op : OP_LT'
    p[0] = '<'


def p_op_gteq(p):
    'op : OP_GTEQ'
    p[0] = '>='


def p_op_lteq(p):
    'op : OP_LTEQ'
    p[0] = '<='


# expr ------------------------------------------------------------------------


def p_expr_param_op_value(p):
    'expr : PARAM op value'
    global cc
    # debug(p_expr_param_op_value.__doc__, p)
    pval = cc.paramGetValue(p[1])
    p[0] = eval('%s %s %s' % (pval, p[2], p[3]))
    debug(p_expr_param_op_value.__doc__, p, '%s = %s' % (p[1], str(pval)))


def p_expr_and_op_value(p):
    'expr : OP_AND op value'
    # PARAM named 'and', special case
    # debug(p_expr_and_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_and_op_value.__doc__, p)


def p_expr_or_op_value(p):
    'expr : OP_OR op value'
    # PARAM named 'or', special case
    # debug(p_expr_or_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_or_op_value.__doc__, p)


def p_expr_is_op_value(p):
    'expr : OP_IS op value'
    # PARAM named 'is', special case
    # debug(p_expr_is_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_is_op_value.__doc__, p)


def p_expr_if_op_value(p):
    'expr : KW_IF op value'
    # PARAM named 'if', special case
    # debug(p_expr_if_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_if_op_value.__doc__, p)


def p_expr_else_op_value(p):
    'expr : KW_ELSE op value'
    # PARAM named 'else', special case
    # debug(p_expr_else_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_else_op_value.__doc__, p)


def p_expr_connected_op_value(p):
    'expr : KW_CONNECTED op value'
    # PARAM named 'connected', special case
    # debug(p_expr_connected_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_connected_op_value.__doc__, p)


def p_expr_connect_op_value(p):
    'expr : KW_CONNECT op value'
    # PARAM named 'connect', special case
    # debug(p_expr_connect_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_connect_op_value.__doc__, p)


def p_expr_ignore_op_value(p):
    'expr : KW_IGNORE op value'
    # PARAM named 'ignore', special case
    # debug(p_expr_ignore_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_ignore_op_value.__doc__, p)


def p_expr_copy_op_value(p):
    'expr : KW_COPY op value'
    # PARAM named 'copy', special case
    # debug(p_expr_copy_op_value.__doc__, p)
    p_expr_param_op_value(p)
    debug(p_expr_copy_op_value.__doc__, p)


# def p_expr_set_op_value(p):
#     'expr : KW_SET op value'
#     # PARAM named 'set', special case
#     debug(p_expr_set_op_value.__doc__, p)
#     p_expr_param_op_value(p)
#     debug(p_expr_set_op_value.__doc__, p)


def p_expr_param_is_connected(p):
    'expr : PARAM OP_IS KW_CONNECTED'
    global cc
    # debug(p_expr_param_is_connected.__doc__, p)
    p[0] = cc.paramIsConnected(p[1])
    debug(p_expr_param_is_connected.__doc__, p)


def p_expr_param_isnot_connected(p):
    'expr : PARAM OP_ISNOT KW_CONNECTED'
    # debug(p_expr_param_isnot_connected.__doc__, p)
    p[0] = not cc.paramIsConnected(p[1])
    debug(p_expr_param_isnot_connected.__doc__, p)


# def p_expr_param_is_set(p):
#     'expr : PARAM OP_IS KW_SET'
#     # diffuseColor is set ? IGNORED
#     debug(p_expr_param_is_set.__doc__, p)


# def p_expr_param_isnot_set(p):
#     'expr : PARAM OP_ISNOT KW_SET'
#     # diffuseColor is not set ? IGNORED
#     debug(p_expr_param_isnot_set.__doc__, p)


def p_expr_lpar_expr_rpar(p):
    'expr : LPAR expr RPAR'
    p[0] = p[2]
    debug(p_expr_lpar_expr_rpar.__doc__, p)


def p_expr_expr_and_expr(p):
    'expr : expr OP_AND expr'
    p[0] = eval('%s and %s' % (p[1], p[3]))
    debug(p_expr_expr_and_expr.__doc__, p)


def p_expr_expr_or_expr(p):
    'expr : expr OP_OR expr'
    p[0] = eval('%s or %s' % (p[1], p[3]))
    debug(p_expr_expr_or_expr.__doc__, p)


# action ----------------------------------------------------------------------


def p_action_copy_param(p):
    'action : KW_COPY PARAM'
    global cc
    cc.actionSet('copyParam', p[2])
    cc.valueSet(p[2])
    p[0] = 'copyParam'
    debug(p_action_copy_param.__doc__, p)


def p_action_connect(p):
    'action : KW_CONNECT'
    global cc
    cc.actionSet('connect')
    p[0] = 'connect'
    debug(p_action_connect.__doc__, p)


def p_action_ignore(p):
    'action : KW_IGNORE'
    global cc
    cc.actionSet('ignore')
    p[0] = 'ignore'
    debug(p_action_ignore.__doc__, p)


def p_action_set_string(p):
    'action : KW_SET STRING'
    global cc
    cc.actionSet('setString')
    cc.valueSet(p[2])
    p[0] = 'setString'
    debug(p_action_set_string.__doc__, p)


def p_action_set_number(p):
    'action : KW_SET NUMBER'
    global cc
    cc.actionSet('setNumber')
    cc.valueSet(p[2])
    p[0] = 'setNumber'
    debug(p_action_set_number.__doc__, p)


# statement -------------------------------------------------------------------


def p_statement_action_if_expr_else_action(p):
    'statement : action KW_IF expr KW_ELSE action'
    global cc
    if p[3]:
        cc.actionChoose('action')
    else:
        cc.actionChoose('fallback')
    p[0] = p[3]
    debug(p_statement_action_if_expr_else_action.__doc__, p)


def p_statement_action_if_expr(p):
    'statement : action KW_IF expr'
    global cc
    if not p[3]:
        cc.actionSet(None)
    p[0] = p[3]
    debug(p_statement_action_if_expr.__doc__, p)


def p_statement_if_expr_else_action(p):
    'statement : KW_IF expr KW_ELSE action'
    global cc
    if p[2]:
        cc.actionChoose('action')
    else:
        cc.actionChoose('fallback')
    p[0] = p[2]
    debug(p_statement_if_expr_else_action.__doc__, p)


def p_statement_action(p):
    'statement : action'
    global cc
    cc.actionSet(p[1])
    p[0] = p[1]
    debug(p_statement_action.__doc__, p)


def p_statement_expr(p):
    'statement : expr'
    p[0] = p[1]
    debug(p_statement_expr.__doc__, p)


precedence = (
    ('left', 'OP_OR'),
    ('left', 'OP_AND'),
)


# Error rule for syntax errors
#
def p_error(p):
    print("Syntax error in input! > '%s'" % p)

# Build the parser
#
parser = yacc.yacc(write_tables=False)


# test
#
def test_yacc():
    # global parser
    print('test_yacc')
    r = ["connect if underMaterial_singlescatterK > 0 " +
         "or (enableSinglescatter == 1 and (singlescatterK > 0 " +
         "or singlescatterK is connected or singlescatterDirectGain > 0 " +
         "or singlescatterDirectGain is connected)) ",
         "connect if ((rrReflectionK is connected or rrReflectionK > 0) " +
         "and enableRR == 1) or " +
         "underMaterial_walterReflectionK is connected " +
         "else set 0",
         "connect if enableClearcoat == 1 "]
    cobj = defaultClient()
    for s in r:
        print('-' * 80)
        print(s)
        evalExpr(s, cobj)
        print(getLastTrace())


class defaultClient:

    def __init__(self):
        self.action = None
        self.actionValue = None
        self.fallback = None
        self.fallbackValue = None

    def paramGetValue(self, param):
        # random decision for testing
        return random.random()

    def paramIsConnected(self, param):
        # random decision for testing
        return bool(2.0 * random.random() - 1.0)

    def actionSet(self, action):
        if self.action is None:
            self.action = action
        else:
            self.fallback = action
        vstruct.logTrace('Client actionSet :'.rjust(45) +
                         ' action = %s  fallback = %s'
                         % (self.action, self.fallback))

    def actionChoose(self, which):
        if which == 'action':
            self.fallback = None
        else:
            self.action = None

    def actionGet(self):
        if self.action is not None:
            return self.action
        else:
            return self.fallback

    def valueSet(self, value):
        if self.action is not None and self.actionValue is None:
            self.actionValue = value
        else:
            self.fallbackValue = value
        vstruct.logTrace('Client valueSet :'.rjust(45) +
                         ' actionValue = %s  fallbackValue = %s'
                         % (self.actionValue, self.fallbackValue))

    def valueGet(self):
        if self.action is not None:
            return self.actionValue
        else:
            return self.fallbackValue


cc = defaultClient()


def evalExpr(expr, clientObj):
    global cc
    lexer = lex.lex()
    parser = yacc.yacc()
    traceInit(expr)
    cc = clientObj
    result = parser.parse(expr, lexer=lexer)
    return result


def debug(msg, array, msg2=None):
    global lastTrace
    s = ''
    for i in range(len(array)):
        s += ' ' + repr(array[i])
    w = 45
    if msg2 is None:
        lastTrace += '%s  ->  %s\n' % (msg.rjust(w), s)
    else:
        lastTrace += '%s  ->  %s  ( %s )\n' % (msg.rjust(w), s, msg2)


def traceInit(expr):
    global lastTrace
    lastTrace = '-' * 80 + '\n'
    lastTrace += 'Expr: "%s"\n' % expr
    lastTrace += '-' * 80 + '\n'


def logTrace(msg):
    global lastTrace
    lastTrace += msg + '\n'


def getLastTrace():
    global lastTrace
    return lastTrace
