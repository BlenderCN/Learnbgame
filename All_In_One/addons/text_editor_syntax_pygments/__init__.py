"""
BEGIN GPL LICENSE BLOCK

(c) Dealga McArdle 2012 / blenderscripting.blogspot / digitalaphasia.com

This program is free software; you may redistribute it, and/or
modify it, under the terms of the GNU General Public License
as published by the Free Software Foundation - either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, write to:

  the Free Software Foundation Inc.
  51 Franklin Street, Fifth Floor
  Boston, MA 02110-1301, USA

or go online at: http://www.gnu.org/licenses/ to view license options.

END GPL LICENCE BLOCK
"""

bl_info = {
    "name": "Text Syntax To 2d Text Objects",
    "author": "zeffii",
    "version": (0, 8, 0),
    "blender": (2, 6, 4),
    "location": "Text Editor",
    "description": "Converts to 2d Text with syntax highlighting.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


# revision, restore point. 012
# - handled: doc string.
# - handled: multi line tripple quote.
# - handled: whitespace objects.
# - added: convenience settings for linux and windows.

import bpy

SugarConstants = lambda: None
SugarConstants.line_height = 0.95
SugarConstants.DOC_TYPE = 'Literal.String.Doc'
SugarConstants.DEBUG = True
SugarConstants.CHAR_WIDTH = .471
SugarConstants.ESCAPE_STRING = 'Literal.String.Escape'
SugarConstants.LITERAL_STRING = 'Literal.String'
SugarConstants.OS = None

try:
    import pygments

except:
    # warning to the user, you might want to hardcode this.
    import sys
    platform = bpy.app.build_platform.decode()

    if 'Linux' in platform:
        sys.path.append('/usr/local/lib/python3.2/site-packages/')
        SugarConstants.OS = 'Linux'
    elif ('Windows' in platform) or ('NT' in platform):
        win_path = 'C:/Python32/Lib/site-packages/'
        sys.path.append(win_path)
        SugarConstants.OS = 'Windows'
    else:
        SugarConstants.OS = 'Darwin'
        print('for OS X support contact me at irc.freenode #blenderpython')


from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import RawTokenFormatter
import re
import os

# ----------------- helpers


def print_time_stamp():
    from time import asctime
    print(asctime().center(60, '-'))


def get_unique_sequential_name():
    # if you need more, increase this value it is arbitrary at the moment
    for i in range(10000):
        yield(str(i).zfill(6))


# ----------------- setup fonts and set spacing values


def add_fonts():
    font_locations = {
        'Windows': 'C:/Users/dealga/Downloads/SourceCodePro_FontsOnly-1.009/',
        'Linux': '/home/zeffii/Desktop/typeFACE/SourceCodePro_FontsOnly-1.009/'
    }

    ext = '.ttf'
    source_dir = font_locations[SugarConstants.OS]
    for font_name in ["SourceCodePro-Bold", "SourceCodePro-Regular"]:
        full_path = source_dir + font_name + ext
        bpy.data.fonts.load(full_path)


def get_string_width(syntax):
    # i can't get real information about the length including whitespace
    # so i measure once the distance between two capital B corners.
    return SugarConstants.CHAR_WIDTH * len(syntax.value)


def create_syntax_block(caret, syntax, seq_yielder):
    # material and syntax element share the same name,
    # this makes it possible to push other fonts weights on element changes.
    material, content = syntax.name, syntax.value

    bpy.ops.object.text_add(location=(caret.x, caret.y, 0.0))
    f_obj = bpy.context.active_object
    f_obj.name = next(seq_yielder)

    # ['Name.Function', 'Keyword', 'Keyword.Namespace']
    # seems the ttf parser/extractor is a little relaxed on charwidth.
    # not safe to switch between family weights, yet.
    f_obj.data.font = bpy.data.fonts['SourceCodePro-Bold']
    f_obj.data.body = content
    f_obj.data.materials.append(bpy.data.materials[material])

    return get_string_width(syntax)


# ----------------- materials set up


def make_material(syntax_name, float3):
    pymat = bpy.data.materials
    col = pymat.new(syntax_name)
    col.use_nodes = True
    Diffuse_BSDF = col.node_tree.nodes['Diffuse BSDF']
    Diffuse_BSDF.inputs[0].default_value = float3


def make_materials():
    material_library = {
        'Comment': (0.1523, 0.1523, 0.1523, 1.0),
        'Keyword': (0.0, 0.4458, 0.8, 1.0),
        'Keyword.Namespace': (0.4, 0.6, 0.97, 1.0),
        'Literal.Number.Float': (0.0, 0.7611, 0.9, 1.0),
        'Literal.Number.Integer': (0.9, 0.5, 0.5, 1.0),
        'Literal.String': (0.8, 0.3081, 0.2161, 1.0),
        'Literal.String.Doc': (0.98, 0.6, 0.6, 1.0),
        'Literal.String.Escape': (0.9, 0.2, 0.7, 1.0),
        'Name': (0.5488, 0.495, 0.2742, 1.0),
        'Name.Builtin': (0.2, 0.9, 0.94, 1.0),
        'Name.Builtin.Pseudo': (0.0, 0.0, 0.946, 1.0),
        'Name.Class': (0.0, 0.0, 0.7939, 1.0),
        'Name.Function': (0.9, 0.1657, 0.3041, 1.0),
        'Name.Namespace': (0.4, 0.4, 0.9, 1.0),
        'Operator': (0.4, 0.8, 0.0, 1.0),
        'Operator.Word': (0.9, 0.3, 0.8, 1.0),
        'Punctuation': (0.8, 0.8, 0.8, 1.0),
        'Text': (0.0, 0.0, 0.0, 1.0)
    }

    for k, v in material_library.items():
        if k not in bpy.data.materials:
            make_material(k, v)


def make_random_material(syntax_name):
    from random import random
    random_rgb_float = (0.0, 0.0, round(random(), 4), 1.0)
    make_material(syntax_name, random_rgb_float)


def make_caret():
    caret = lambda: None
    caret.x = 0.0
    caret.y = 0.0
    return caret


def make_syntax_unit(token_type, token_value):
    syntax = lambda: None
    syntax.name = token_type
    syntax.value = token_value
    return syntax


def get_syntax(udix):
    udix = [j for j in udix if len(j) > 0]
    return make_syntax_unit(udix[1], udix[2][1:-1])


def print_token(syntax):
    print('Token: {0.name}: |{0.value}|'.format(syntax))


def print_debug_item(multi_line):
    print('-- debug --')
    for t in multi_line:
        print(repr(t))
    print('-- /debug --')


def generate_doc_string(caret, syntax, seq_yielder):
    DOC_TYPE = SugarConstants.DOC_TYPE
    line_height = SugarConstants.line_height

    multi_line = re.split(r'\\n', syntax.value)

    if SugarConstants.DEBUG:
        print_debug_item(multi_line)

    # iterate over the resulting multiline
    for line in multi_line:
        line = line.replace(r'\\', '\\')

        print('|' + line + '|')
        syntax = make_syntax_unit(DOC_TYPE, line)
        syntax_params = caret, syntax, seq_yielder
        syntax_width = create_syntax_block(*syntax_params)
        caret.x = 0.0
        caret.y -= line_height

    return caret


def generate_escaped_special(caret, syntax, seq_yielder):
    ESCAPE_STRING = SugarConstants.ESCAPE_STRING
    line_height = SugarConstants.line_height

    literal_bytes = bytes(syntax.value, "utf-8")
    literal_string = literal_bytes.decode("unicode_escape")

    for character in literal_string:
        print('---extra---')
        print('|' + character + '|   <--- ' + repr(character))
        print('---extra---')

        if character == '\n':
            caret.x = 0.0
            caret.y -= line_height
        else:
            syntax = make_syntax_unit(ESCAPE_STRING, character)
            syntax_params = caret, syntax, seq_yielder
            caret.x += create_syntax_block(*syntax_params)

    return caret


# ----------------- main worker functions


def work_on_element(caret, udix, seq_yielder):
    DOC_TYPE = SugarConstants.DOC_TYPE
    ESCAPE_STRING = SugarConstants.ESCAPE_STRING
    LS = LITERAL_STRING = SugarConstants.LITERAL_STRING

    syntax = get_syntax(udix)
    print_token(syntax)

    # add material if not present
    if not syntax.name in bpy.data.materials:
        make_random_material(syntax.name)

    syntax_params = caret, syntax, seq_yielder

    if syntax.name == DOC_TYPE:
        caret = generate_doc_string(*syntax_params)

    elif syntax.name == ESCAPE_STRING:
        caret = generate_escaped_special(*syntax_params)

    else:
        # skip whitespace strings, move caret over distance
        if syntax.name == 'Text' and syntax.value.isspace():
            caret.x += get_string_width(syntax)
            return caret

        # two slashes should be included in lit.str.esc, but isn't
        elif syntax.name == LS and syntax.value == r'\\':
            ex_syntax = make_syntax_unit(LS, '\\')
            syntax_params = caret, ex_syntax, seq_yielder

        caret.x += create_syntax_block(*syntax_params)

    return caret


def write_lines(post_split_lines, seq_yielder):
    """ Some of this is very manual, i realize that """

    caret = make_caret()

    # line_counter = 0

    TOKEN_RE = """(Token\.(.*?)\t(\'(.*?)\')|Token\.(.*?)\t(\"(.*?)\"))"""
    pattern = re.compile(TOKEN_RE)

    for i in post_split_lines:
        if '\t' in i:
            results = pattern.findall(i)

            for udix in results:
                caret = work_on_element(caret, udix, seq_yielder)

        caret.x = 0.0

        # line_counter += 1
        #if line_counter > 80:
        #    break

        print('----newline')
        caret.y -= SugarConstants.line_height


# ----------------- main director function


def generate_syntax_objects(code):

    print_time_stamp()
    make_materials()
    add_fonts()

    seq_yielder = get_unique_sequential_name()

    # process data
    code_as_raw = highlight(code, Python3Lexer(), RawTokenFormatter())
    pre_split_lines = code_as_raw.decode('utf-8')

    # there is a hidden tab inside the regex here.
    post_split_lines = pre_split_lines.split(r"""Token.Text	'\n'""")

    # write to objects
    write_lines(post_split_lines, seq_yielder)


# ------------------ blender UI stuff


class GenerateSyntaxOperator(bpy.types.Operator):
    """Defines a button"""
    bl_idname = "scene.generate_sugar"
    bl_label = "Uses currently loaded text to make text objects with syntax"

    def execute(self, context):
        file_name = context.edit_text.name
        code = bpy.data.texts[file_name].as_string()
        generate_syntax_objects(code)
        return{'FINISHED'}


class GenerateSyntaxPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Syntax Objects"
    bl_idname = "OBJECT_PT_convertsyntax"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.operator("scene.generate_sugar", text='Make Text Objects')


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
