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


from . import import_shared
#FIXME: namespace pollution. explicitly import what's needed
from .pyparsing import *


class objRegion:
    def __init__(self, name):
        self.name = name
        self.faces = []


class mdlObject:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.faces = []
        self.regions = {}
        self.cur_reg = None


my_objects = {}
cur_obj = None

bnf = None


def store_vertex(tokens):
    global cur_obj
    vertex = (float(tokens[0]), float(tokens[1]), float(tokens[2]))
    cur_obj.vertices.append(vertex)


def store_face(tokens):
    global cur_obj
    face = (int(tokens[0]), int(tokens[1]), int(tokens[2]))
    cur_obj.faces.append(face)


def store_region_elements(tokens):
    global cur_obj
    region = tokens[1]
    region = [int(i) for i in region]
    cur_obj.cur_reg.faces = region


def store_region_name(tokens):
    global cur_obj
    regname = tokens[0]
    if not regname in cur_obj.regions:
        cur_obj.regions[regname] = objRegion(regname)
    cur_obj.cur_reg = cur_obj.regions[regname]


def store_object_name(tokens):
    global my_objects
    global cur_obj
    objname = tokens[0]
    if not objname in my_objects:
        my_objects[objname] = mdlObject(objname)
    cur_obj = my_objects[objname]


def mdl_format_bnf():
    global bnf

    if not bnf:

        # punctuation
        lbrace = Suppress("{")
        rbrace = Suppress("}")
        lbracket = Suppress("[")
        rbracket = Suppress("]")
        equal = Suppress("=")
        comma = Suppress(",")
        point = Literal('.')
        e = CaselessLiteral('E')
        plusorminus = Literal('+') | Literal('-')

        # keywords
        object_ = Keyword("OBJECT")
        polygonlist_ = Keyword("POLYGON_LIST")
        vertexlist_ = Keyword("VERTEX_LIST")
        elementconns_ = Keyword("ELEMENT_CONNECTIONS")
        define_surface_regions_ = Keyword("DEFINE_SURFACE_REGIONS")
        elementlist_ = Keyword("ELEMENT_LIST")
        vizvalue_ = Keyword("VIZ_VALUE")

        number = Word(nums)
        integer = Combine(Optional(plusorminus) + number)
        real = Combine(integer +
                       Optional(point + Optional(number)) +
                       Optional(e + integer))
        numarg = (real | integer)

        identifier = Word(alphas, alphanums + "_" + ".")

        vertex_def = (lbracket + numarg + comma + numarg + comma + numarg +
                      rbracket).setParseAction(store_vertex)
        face_def = (lbracket + integer + comma + integer + comma + integer +
                    rbracket).setParseAction(store_face)

        vertex_list = (vertexlist_ + lbrace + OneOrMore(vertex_def) + rbrace)
        face_list = (elementconns_ + lbrace + OneOrMore(face_def) + rbrace)

        integer_array_elements = Group(integer + ZeroOrMore(comma + integer))
        integer_array = (lbracket + integer_array_elements + rbracket)
        element_list_def = (
            elementlist_ + equal + integer_array).setParseAction(
            store_region_elements)
        viz_value_def = (vizvalue_ + equal + integer)
        surface_region_def = ((identifier + lbrace).setParseAction(
            store_region_name) + element_list_def + Optional(viz_value_def) +
            rbrace)
        surface_regions_block = (define_surface_regions_ + lbrace +
                                 OneOrMore(surface_region_def) + rbrace)

        poly_obj = ((identifier + polygonlist_).setParseAction(
                    store_object_name) + lbrace + vertex_list + face_list +
                    ZeroOrMore(surface_regions_block) + rbrace)

        # Doesn't handle nested metaobjects right now. Also, there can be
        # naming issues when you import something like "meta.Cube" and "Cube"
        meta_obj = (identifier + object_ + lbrace + OneOrMore(poly_obj) +
                    rbrace)

        meta_or_poly = OneOrMore(poly_obj) | OneOrMore(meta_obj)

        bnf = OneOrMore(meta_or_poly)

        singleLineComment = "//" + restOfLine
        bnf.ignore(singleLineComment)
        bnf.ignore(cStyleComment)

    return bnf


def load(operator, context, filepath="", add_to_model_objects=True):
    global my_objects
    my_objects = {}

    obj_mat, reg_mat = import_shared.create_materials()

    with open(filepath, "r") as file:
        bnf = mdl_format_bnf()
        bnf.parseString(file.read())

    for _, mdlobj in my_objects.items():
        import_shared.import_obj(mdlobj, obj_mat, reg_mat, add_to_model_objects)

    return {'FINISHED'}
