import os

from math import sqrt, sin, cos, asin, acos, atan2, radians

from copy import deepcopy

from .ply import lex as lex
from .ply import yacc as yacc
from .ply.lex import TOKEN

from . import geometry
from .geometry import Vector, Point, Transform

from .global_env import GlobalEnv

from .scene import *
O_DRAWABLE = (Dots, Line, Curve, Polygon, Special, Sweep, Repeat, Compound)

from .symtable import SymbolTable

from .opts import Options

class SketchParser:
    keyword_tokens = [ 'LANGUAGE'  , 'PSTRICKS' , 'TIKZ'    , 'LaTeX'      , 'ConTeXt'     ,
                       'CURVE'     , 'CAMERA'   , 'DEF'     , 'DOTS'       , 'FRAME'       ,
                       'GLOBAL'    , 'LINE'     , 'POLYGON' , 'PUT'        , 'REPEAT'      ,
                       'SET'       , 'SWEEP'    , 'THEN'    , 'PICTUREBOX' , 'ASIN'        ,
                       'ACOS'      , 'ATAN2'    , 'COS'     , 'INVERSE'    , 'PERSPECTIVE' ,
                       'PROJECT'   , 'ROTATE'   , 'SCALE'   , 'SIN'        , 'SQRT'        ,
                       'TRANSLATE' , 'UNIT'     , 'VIEW'    ]

    reserved = { keyword.lower() : keyword for keyword in keyword_tokens }

    tokens = [ 'ID'       , 'BRACKET_ID'  , 'DBL_BRACKET_ID' , 'CURLY_ID' ,
               'ANGLE_ID' , 'NUM'         , 'OPTS_STR'       , 'SPECIAL'  ,
               'TICK'     , 'EMPTY_ANGLE' , 'PAREN_ID'       ] + keyword_tokens

    literals = r"-+*/^|.()\[\]{}=,"

    states = (('input', 'inclusive'),)

    Identifier = '[A-Za-z]([A-Za-z0-9_]*[A-Za-z0-9])?'
    WS         = '[ \t\r\n]'

    t_ignore = ' \t\r'

    def __init__(self, **kwargs):
        self.lexer = []
        self.filename = None

        self.debug = kwargs.get("debug", False)
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] \
                    + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        self.lexer.append(lex.lex(module=self, **kwargs))
        self.parser = yacc.yacc(module=self,
                                debugfile=self.debugfile,
                                tabmodule=self.tabmodule,
                                **kwargs)

        self.MAX_INPUT_DEPTH = 6

        self.sym_tab = SymbolTable()
        self.env     = GlobalEnv()
        self.objects = []

    def reset(self):
        del self.sym_tab
        del self.env
        del self.objects

        self.sym_tab = SymbolTable()
        self.env     = GlobalEnv()
        self.objects = []

    def run(self):
        while 1:
            try:
                s = input("sketch >")
            except EOFError:
                break
            if not s:
                continue
            self.parser.parse(s, lexer=self)

    def parse(self, string, **kwargs):
        self.parser.parse(string, *kwargs)
        return self.objects

    def t_comment(self, t):
        r'[%#].*'
        pass

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def t_OPTS_STR(self, t):
        r'\[[^\]=]+=[^\]]+\]'
        # [<stuff>=<stuff>]
        t.value = t.value[1:-1]
        return t

    @TOKEN(r"'" + WS + r"*[xyz]")
    def t_TICK(self, t):
        # set the index value
        t.value = "xyz".index(t.value[1])
        return t

    @TOKEN(r'(([0-9]+\.[0-9]*)|(\.[0-9]+)|([0-9]+))([eE][-+]?[0-9]+)?')
    def t_NUM(self, t):
        t.value = float(t.value)
        return t

    def _update_lineno(self, t):
        t.lineno += t.value.count('\n')

    @TOKEN(r'input' + WS + r'*')
    def t_input(self, t):
        self._update_lineno(t)
        t.lexer.begin("input")

    @TOKEN(r'special' + WS + r'*')
    def t_SPECIAL(self, t):
        # TODO(david): add a warning
        result = ""

        if len(self.lexer[-1].lexdata) <= self.lexer[-1].lexpos:
            # TODO(david): error for no special
            return result

        delim = self.lexer[-1].lexdata[self.lexer[-1].lexpos]

        ch = self.lexer[-1].lexpos + 1
        while self.lexer[-1].lexdata[ch] != delim \
                and len(self.lexer[-1].lexdata) > ch:
            if self.lexer[-1].lexdata[ch] == "\n":
                self._update_lineno(t)
            result += self.lexer[-1].lexdata[ch]
            ch += 1
        # if self.lexer[-1].lexdata[ch] != delim: TODO(david): error

        self.lexer[-1].lexpos = ch + 1
        self._update_lineno(t)
        t.value = result
        return t

    @TOKEN(Identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, 'ID')
        return t

    @TOKEN(r'<' + Identifier + r'>')
    def t_ANGLE_ID(self, t):
        # strip the brackets off
        t.value = t.value[1:-1]
        return t

    @TOKEN(r'<>')
    def t_EMPTY_ANGLE(self, t):
        return t

    @TOKEN(r'\(' + Identifier + r'\)')
    def t_PAREN_ID(self, t):
        t.value = t.value[1:-1]
        return t

    @TOKEN(r'\[' + Identifier + r'\]')
    def t_BRACKET_ID(self, t):
        t.value = t.value[1:-1]
        return t

    @TOKEN(r'\[\[' + Identifier + r'\]\]')
    def t_DBL_BRACKET_ID(self, t):
        t.value = t.value[2:-2]
        return t

    @TOKEN(r'\{' + Identifier + r'\}')
    def t_CURLY_ID(self, t):
        t.value = t.value[1:-1]
        return t

    # Input
    def t_input_FILENAME(self, t):
        r'''\{[^}]*\}'''
        buf = ""
        if self.filename:
            buf = os.path.split(self.filename)[0] + os.sep
        buf += t.value[1:-1] # cut off the braces

        if len(self.lexer) < self.MAX_INPUT_DEPTH:
            with open(buf, 'r') as f:
                # create a new lexer with the same build
                self.lexer.append(self.lexer[-1].clone())
                self.lexer[-1].input(f.read())
                self.lexer[-1].prev_filename = self.filename
                # holds onto the state from last lexer (input)
                self.lexer[-1].begin('INITIAL')
                # stops returning tokens if nothing comes out of this
                return self.lexer[-1].token()
        # ensure lexer is in the right state when popping back
        t.lexer.begin('INITIAL')

    def t_error(self, t):
        print("illegal character: '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_eof(self, t):
        if len(self.lexer) == 1:
            return None
        # remember that last file name and pop back out
        self.filename = self.lexer[-1].prev_filename
        self.lexer.pop()
        # return the next token to make sure we keep going
        return self.lexer[-1].token()

    def input(self, s):
        self.lexer[-1].input(s)

    def token(self):
        return self.lexer[-1].token()

    def __iter__(self):
        return self

    def next(self):
        t = self.token()
        if t is None:
            raise StopIteration
        return t

    __next__ = next

    # YACC ###################################################################

    precedence = (
            ('right', 'THEN'),
            ('left', '-', '+'),
            ('left', '*', '/', '.'),
            ('left', 'NEG'),
            ('right', '^'),
            ('left', 'TICK'),
    )

    def p_input(self, p):
        """input : defs_and_decls global_decl_block"""
        self.objects = p[1]

    def p_global_decl_block(self, p):
        """global_decl_block : GLOBAL '{' global_decls '}' 
                             |"""
        pass

    def p_global_decls(self, p):
        """global_decls : global_decls global_decl
                        | global_decl"""
        pass

        # GLOBAL #################################################################

    def p_global_set_opts(self, p):
        """global_decl : SET OPTS_STR"""
        self.env.set_opts(p[2], p.lineno(1))

    def p_global_pbox_scalar(self, p):
        """global_decl : PICTUREBOX '[' scalar_expr ']' """
        self.env.set_baseline(p[3], p.lineno(1))

    def p_global_pbox_baseline(self, p):
        """global_decl : PICTUREBOX opt_baseline point point"""
        self.env.set_baseline(p[2], p.lineno(1))
        self.env.set_extent(p[3], p[4], p.lineno(1))

    def p_global_camera(self, p):
        """global_decl : CAMERA transform_expr"""
        self.env.set_camera(p[2], p.lineno(1))

    def p_global_frame(self, p):
        """global_decl : FRAME"""
        self.env.set_frame(None, p.lineno(1))

    def p_global_frame_opts(self, p):
        """global_decl : FRAME OPTS_STR"""
        self.env.set_frame(p[2], p.lineno(1))

    def p_global_language(self, p):
        """global_decl : LANGUAGE output_language"""
        self.env.set_output_language(p[2], p.lineno(1))

    def p_global_def(self, p):
        """global_decl : def"""
        pass

        # LANGUAGES ##############################################################

    def p_output_language(self, p):
        """output_language : graphics_language comma_macro_package"""
        p[0] = p[1] | p[2]

    def p_graphics_language(self, p):
        """graphics_language : PSTRICKS
                             | TIKZ"""
        p[0] = 0 #GEOL_PSTRICKS if p[1] == "PSTRICKS" else GEOL_TIKZ

    def p_comma_macro(self, p):
        """comma_macro_package : ',' macro_package
                               |"""
        if len(p) > 1:
            p[0] = 0 #p[2]
        else:
            p[0] = 0 #GEOL_LATEX

    def p_macro(self, p):
        """macro_package : LaTeX
                         | ConTeXt"""
        if p[1] == 'LaTeX':
            p[0] = 0 #GEOL_LATEX
        else:
            p[0] = 0 #GEOL_CONTEXT

        # BASELINE ###############################################################

    def p_opt_baseline(self, p):
        """opt_baseline : '[' scalar_expr ']'
                        |"""
        if len(p) > 1:
            p[0] = p[2]
        else:
            p[0] = None

        # DEFINITIONS ############################################################

    def p_defs_and_decls(self, p):
        """defs_and_decls : rev_defs_and_decls"""
        p[0] = p[1][::-1] if p[1] else p[1]

    def p_rev_defs_and_decls_join(self, p):
        """rev_defs_and_decls : rev_defs_and_decls def_or_decl"""
        p[0] = p[2][::-1] + p[1] if p[2] else p[1]

    def p_rev_defs_and_decls(self, p):
        """rev_defs_and_decls : def_or_decl"""
        p[0] = p[1][::-1] if p[1] else p[1]

    def p_def_or_decl(self, p):
        """def_or_decl : def
                       | decl"""
        if p[1]:
            if type(p[1]) == list:
                p[0] = p[1]
            else:
                p[0] = [p[1]]
        else:
            p[0] = []

    def p_def(self, p):
        """def : DEF ID defable
               | tagged_defs EMPTY_ANGLE defable
               | DEF ID EMPTY_ANGLE"""

        name = p[1] if p[2] == '<>' else p[2]
        obj = Tag() if p[3] == '<>' else p[3]

        self.sym_tab.new_symbol(name, None, obj, p.lineno(1))
        p[0] = None

    def p_tagged_defs(self, p):
        """tagged_defs : DEF ID ANGLE_ID defable"""
        p[0] = "" if self.sym_tab.new_symbol(p[2], p[3], p[4], p.lineno(3)) else p[2]

    def p_tagged_defs_rec(self, p):
        """tagged_defs : tagged_defs ANGLE_ID defable"""
        p[0] = "" if self.sym_tab.new_symbol(p[1], p[2], p[3], p.lineno(2)) else p[1]

    def p_defable_expr(self, p):
        """defable : expr
                   | decl"""
        p[0] = p[1]

    def p_defable_opts_str(self, p):
        """defable : OPTS_STR"""
        p[0] = Options(p[1], p.lineno(1))

        # DECLARES ###############################################################

    def p_decl_dots(self, p):
        """decl : DOTS options points"""
        p[0] = Dots(p[2], p[3])

    def p_decl_line(self, p):
        """decl : LINE options points"""
        p[0] = Line(p[2], p[3])

    def p_decl_curve(self, p):
        """decl : CURVE options points"""
        p[0] = Curve(p[2], p[3])

    def p_decl_polygon(self, p):
        """decl : POLYGON options points"""
        p[0] = Polygon(p[2], p[3])

    def p_decl_sweep(self, p):
        """decl : SWEEP options '{' scalar_expr opt_star ',' transforms '}' point
                | SWEEP options '{' scalar_expr opt_star ',' transforms '}' decl"""
        point_obj = Point(p[9]) if type(p[9]) == Point else p[9]
        p[0] = Sweep(p[2], p[4], p[5], p[7], point_obj)

    def p_decl_repeat(self, p):
        """decl : REPEAT '{' scalar_expr ',' transforms '}' decl"""
        p[0] = Repeat(p[3], p[5], p[7])

    def p_decl_put(self, p):
        """decl : PUT '{' transform_expr '}' decl"""
        p[0] = Compound(p[3], p[5])

    def p_decl_special(self, p):
        """decl : SPECIAL special_args"""
        p[0] = Special(p[1], p[2], p.lineno(1))

    def p_decl_curly(self, p):
        """decl : CURLY_ID"""
        p[0] = self.sym_tab.lookup(p[1], O_DRAWABLE, p.lineno(1))

    def p_decl_scoped(self, p):
        """decl : '{' new_scope defs_and_decls '}' """
        # TODO(david): throw an error
        p[0] = deepcopy(p[3])
        self.sym_tab = self.sym_tab.pop()

    def p_new_scope(self, p):
        """new_scope :"""
        self.sym_tab = self.sym_tab.push()

        # OPTIONS ################################################################

    def p_opt_star(self, p):
        """opt_star : EMPTY_ANGLE
                    |"""
        p[0] = True if len(p) > 1 else False

    def p_option_id_list(self, p):
        """option_id_list : option_id_list ',' ID"""
        p[0] = p[1].update(self.sym_tab.lookup(p[3], (Options,), p.lineno(1)))

    def p_option_id_list_base(self, p):
        """option_id_list : ID"""
        p[0] = self.sym_tab.lookup(p[1], (Options,), p.lineno(1))

    def p_options_str(self, p):
        """options : OPTS_STR"""
        p[0] = Options(p[1], p.lineno(1))

    def p_options_brkt(self, p):
        """options : BRACKET_ID"""
        p[0] = self.sym_tab.lookup(p[1], (Options,), p.lineno(1))

    def p_options_ids(self, p):
        """options : '[' option_id_list ']' """
        p[0] = p[2]

    def p_options_empty(self, p):
        """options :"""
        p[0] = Options("=")

    # POINTS #################################################################

    def p_points(self, p):
        """points : rev_points"""
        p[0] = p[1][::-1]

    def p_rev_points_rec(self, p):
        """rev_points : rev_points point"""
        p[0] = [p[2]] + p[1]

    def p_rev_points_base(self, p):
        """rev_points : point"""
        p[0] = [p[1]]

    # SPECIAL ################################################################

    def p_special_args(self, p):
        """special_args : rev_special_args"""
        p[0] = p[1][::-1]

    def p_rev_special_args(self, p):
        """rev_special_args : rev_special_args special_arg"""
        p[0] = [p[2]] + p[1]

    def p_rev_special_args_empty(self, p):
        """rev_special_args :"""
        p[0] = []

    def p_special_arg_def(self, p):
        """special_arg : scalar
                       | point
                       | vector_literal
                       | OPTS_STR"""
        p[0] = [p[1]]

    def p_special_arg_lookup(self, p):
        """special_arg : BRACKET_ID"""
        p[0] = [self.sym_tab.lookup(p[1], (Vector, Options), p.lineno(1))]

    # TRANSFORMS #############################################################

    def p_transforms(self, p):
        """transforms : rev_transforms"""
        p[0] = p[1][::-1]

    def p_rev_transforms_rec(self, p):
        """rev_transforms : rev_transforms ',' transform_expr"""
        p[0] = [p[3]] + p[1]

    def p_rev_transforms_base(self, p):
        """rev_transforms : transform_expr"""
        p[0] = [p[1]]

        # EXPR ###################################################################

    def p_expr_set(self, p):
        """expr : scalar
                | point
                | vector
                | transform"""
        p[0] = deepcopy(p[1])

    def p_expr_bop(self, p):
        """expr : expr '+'  expr
                | expr '-'  expr
                | expr '*'  expr
                | expr '/'  expr
                | expr '.'  expr
                | expr THEN expr"""
        types = (type(p[1]), type(p[3]))
        if p[2] == '+' and types in ((float, float),
                                     (Vector, Vector),
                                     (Vector, Point),
                                     (Point, Vector)):
            # swap the addition to ensure a point is returned
            p[0] = p[1] + p[3] if types[0] == Point else p[3] + p[1]
        elif p[2] == '-' and types in ((float, float),
                                       (Point, Point),
                                       (Point, Vector),
                                       (Vector, Vector)):
            # ensure Vector when subtracting points
            p[0] = Vector(p[1] - p[3]) if type(p[2]) == Point else p[1] - p[3]
        elif (p[2] == '*' and types in ((float, float),
                                       (float, Vector),
                                       (Vector, float),
                                       (Transform, Transform),
                                       (Transform, Point),
                                       (Transform, Vector))) or \
             (p[2] == '.' and types in ((float, float),
                                       (Vector, float),
                                       (float, Vector),
                                       (Vector, Vector),
                                       (Transform, Transform),
                                       (Transform, Point),
                                       (Trasnform, Vector))):
            p[0] = p[1] * p[3]
        elif p[2] == '*' and types in ((Vector, Vector),):
            p[0] = p[1].cross(p[3])
        elif p[2] == '/' and types in ((float, float),
                                       (Vector, float),
                                       (float, Vector)):
            p[0] = p[1] / p[3]
        elif p[2].upper() == 'THEN' and types in ((Transform, Transform),
                                          (Point, Transform),
                                          (Vector, Transform)):
            # should just be flipped version of before
            p[0] = p[3] * p[1]
        else:
            p[0] = 0.0 #TODO(david): ERROR MESSAGE

    def p_expr_mag(self, p):
        """expr : '|' expr '|'"""
        if type(p[2]) == float:
            p[0] = p[2] if p[2] >= 0 else p[2]
        elif type(p[2]) == Vector:
            p[0] = p[2].length
        else:
            p[0] = p[2] # TODO(david): error message

    def p_expr_neg(self, p):
        """expr : '-' expr %prec NEG"""
        if type(p[2]) in (float, Vector):
            p[0] = -p[2]
        else:
            p[0] = p[2] # TODO(david): error message

    def p_expr_pow(self, p):
        """expr : expr '^' expr"""
        types = (type(p[1]), type(p[3]))
        if types in ((float, float),):
            p[0] = p[1] ** p[3]
        elif types in ((Transform, float),):
            p[0] = p[1] ** int(p[3])
        else:
            p[0] = 0.0 # TODO(david): error message

    def p_expr_paren(self, p):
        """expr : '(' expr ')'"""
        p[0] = p[2]

    def p_expr_unit(self, p):
        """expr : UNIT  '(' expr ')'"""
        if type(p[3]) == Vector:
            p[0] = p[3].normalized()
        else:
            p[0] = Vector((0.0, 0.0, 1.0))

    def p_expr_fun(self, p):
        """expr : SQRT  '(' expr ')'
                | SIN   '(' expr ')'
                | COS   '(' expr ')'
                | ASIN  '(' expr ')'
                | ACOS  '(' expr ')'
                | ATAN2 '(' expr ',' expr ')'"""
        if not type(p[3]) == float:
            p[0] = 0.0 #TODO(david): error message
            return
        if p[1] == 'SQRT':
            p[0] = sqrt(p[3])
        elif p[1] == 'SIN':
            p[0] = sin(p[3])
        elif p[1] == 'COS':
            p[0] = cos(p[3])
        elif p[1] == 'ASIN':
            p[0] = asin(p[3])
        elif p[1] == 'ACOS':
            p[0] = acos(p[3])
        elif p[1] == 'ATAN2' and type(p[5]) == float:
            p[0] = atan2(p[3], p[5])
        else:
            p[0] = 0.0 #TODO(david): error message

    def p_expr_tick(self, p):
        """expr : expr TICK"""
        if type(p[1]) in (Vector, Point):
            p[0] = p[1][p[2]]
        else:
            p[0] = 0.0 #TODO(david): error message

    def p_scalar_num(self, p):
        """scalar : NUM"""
        p[0] = p[1]

    def p_scalar_sym(self, p):
        """scalar : ID"""
        p[0] = self.sym_tab.lookup(p[1], (float,), p.lineno(1))

    def p_scalar_expr(self, p):
        """scalar_expr : expr"""
        if type(p[1]) == float:
            p[0] = p[1]
        else:
            p[0] = 0.0 #TODO(david): error message

    def p_point_3(self, p):
        """point : '(' scalar_expr ',' scalar_expr ',' scalar_expr ')'"""
        p[0] = Point(p[2::2])

    def p_point_2(self, p):
        """point : '(' scalar_expr ',' scalar_expr ')'"""
        p[0] = Point(p[2::2] + [0.0])

    def p_point_id(self, p):
        """point : PAREN_ID"""
        p[0] = self.sym_tab.lookup(p[1], (Point,), p.lineno(1))

    def p_point_expr(self, p):
        """point_expr : expr"""
        if type(p[1]) == Point:
            p[0] = Point(p[1])
        else:
            p[0] = Point((0.0, 0.0, 0.0)) #TODO(david): error message

    def p_vector_vector_literal(self, p):
        """vector : vector_literal"""
        p[0] = p[1]

    def p_vector_id(self, p):
        """vector : BRACKET_ID"""
        p[0] = self.sym_tab.lookup(p[1], (Vector,), p.lineno(1))

    def p_vector_literal_3(self, p):
        """vector_literal : '[' scalar_expr ',' scalar_expr ',' scalar_expr ']'"""
        p[0] = Vector(p[2::2])

    def p_vector_literal_2(self, p):
        """vector_literal : '[' scalar_expr ',' scalar_expr ']'"""
        p[0] = Vector(p[2::2] + [0.0])


    def p_vector_expr(self, p):
        """vector_expr : expr"""
        if type(p[1]) == Vector:
            p[0] = Vector(p[1])
        else:
            p[0] = Vector((0.0, 0.0, 0.0)) #TODO(david): error message

    def p_transform_mat(self, p):
        """transform : '['\
                       '[' scalar_expr ',' scalar_expr ',' scalar_expr ',' scalar_expr ']'\
                       '[' scalar_expr ',' scalar_expr ',' scalar_expr ',' scalar_expr ']'\
                       '[' scalar_expr ',' scalar_expr ',' scalar_expr ',' scalar_expr ']'\
                       '[' scalar_expr ',' scalar_expr ',' scalar_expr ',' scalar_expr ']'\
                       ']'"""
        p[0] = Transform([p[(i * 9) + 1:(i + 1) * 9:2] for i in range(4)])

    def p_transform_rotate(self, p):
        """transform : ROTATE '(' scalar_expr ')'
                     | ROTATE '(' scalar_expr ',' expr ')'
                     | ROTATE '(' scalar_expr ',' point_expr  ',' vector_expr ')'"""
        point = Point((0.0, 0.0, 0.0))
        vector = Vector((0.0, 0.0, 1.0))
        if len(p) > 5:
            if type(p[5]) == Point:
                point = p[5]
                if len(p) > 7:
                    vector = p[7]
            elif type(p[5]) == Vector:
                vector = p[5]
            # else: TODO(david): raise error
                
        rot = Transform.Rotation(radians(p[3]), 4, vector)
        tra = Transform.Translation(point)
        p[0] = tra * rot

    def p_transform_translate(self, p):
        """transform : TRANSLATE '(' vector_expr ')'"""
        p[0] = Transform.Translation(p[3])

    def p_transform_scale(self, p):
        """transform : SCALE '(' expr ')'"""
        scale_by = (0, 0, 0)
        if type(p[3]) == float:
            scale_by = tuple(p[3] for i in range(3))
        elif type(p[3]) == Vector:
            scale_by = tuple(p[3])
        # TODO(david): error if else
        p[0] = Transform.Scale(scale_by)

    def p_transform_project_parallel(self, p):
        """transform : PROJECT '(' ')'"""
        p[0] = Transform.Scale(Vector(1.0, 1.0, 0.0))

    def p_transform_project_perspective(self, p):
        """transform : PROJECT '(' scalar_expr ')'"""
        p[0] = Transform.Scale((p[3],)*3)
        p[0][3][3] = 0.0
        p[0][2][3] = -1.0

    def p_transform_perspective(self, p):
        """transform : PERSPECTIVE '(' scalar_expr ')'"""
        p[0] = Transform.Scale(Vector((p[3], p[3], 1.0)))
        p[0][3][2] = 1.0
        p[0][2][3] = -1.0
        p[0][3][3] = 0.0

    def p_transform_view(self, p):
        """transform : VIEW '(' point_expr ',' expr ',' vector_expr ')'
                     | VIEW '(' point_expr ',' expr ')'
                     | VIEW '(' point_expr ')'"""
        up = p[7] if len(p) > 7 else Vector((0.0, 1.0, 0.0))
        vd = Vector(-p[3])
        if len(p) > 5:
            if type(p[5]) == Vector:
                vd = p[5]
            elif type(p[5]) == Point:
                vd = p[5] - p[3]
            # TODO(david): else print error
        eye = p[3]
        p[0] = Transform.View(eye, vd, up)

    def p_transform_inverse(self, p):
        """transform : INVERSE '(' transform_expr ')'"""
        p[0] = p[1].inverted()

    def p_transform_id(self, p):
        """transform : DBL_BRACKET_ID"""
        p[0] = self.sym_tab.lookup(p[1], (Transform,), p.lineno(1))

    def p_transform_expr(self, p):
        """transform_expr : expr"""
        p[0] = deepcopy(p[1]) if type(p[1]) == Transform else Transform()

    def p_error(self, p):
        if p:
            print("Syntax error at token", p.type, p.lineno)
            # Just discard the token and tell the parser it's okay.
            self.parser.errok()
        else:
            print("Syntax error at EOF")

if __name__=="__main__":
    lexer = SketchParser(debug=True)
    with open("example/cone.sk", 'r') as f:
        print(lexer.parse(f.read()))

