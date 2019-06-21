import bpy
import struct
from console_python import add_scrollback, get_console


history_append = bpy.ops.console.history_append


def hex_to_rgb(rgb_str):
    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))
    return tuple([val / 255 for val in int_tuple])


def do_text_glam():

    def set_props(s):
        # s = context.space_data
        s.show_line_numbers = True
        s.show_word_wrap = True
        s.show_syntax_highlight = True
        s.show_margin = True

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:

            if not area.type == 'TEXT_EDITOR':
                continue

            for s in area.spaces:
                if s.type == 'TEXT_EDITOR':
                    set_props(s)


def do_text_synthax(theme):
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    texed = bpy.context.user_preferences.themes[current_theme].text_editor

    # here function to save your favourite theme for TEXT EDITOR
    # https://gist.github.com/zeffii/2ee84e47872ff04bec94 (See console)

    if theme == 'dk':
        texed.space.text = hex_to_rgb('ffffff')
        texed.space.back = hex_to_rgb('2a2a2a')
        texed.cursor = hex_to_rgb('FFAAAA')
        texed.syntax_builtin = hex_to_rgb('00EFFF')  # import, return, for, in..
        texed.syntax_comment = hex_to_rgb('33df05')
        texed.syntax_numbers = hex_to_rgb('0093c8')
        texed.syntax_special = hex_to_rgb('f8ff35')  # def, class..
        texed.syntax_string = hex_to_rgb('B2FFB0')
        texed.syntax_symbols = hex_to_rgb('FFC5DF')  # = ()[] . , > < == etc.
        texed.syntax_reserved = hex_to_rgb('45eae4')
        texed.syntax_preprocessor = hex_to_rgb('FFFFFF')
        texed.line_numbers_background = (0, 0, 0)
        texed.selected_text = (.4, .4, .4)
    if theme == 'lt':
        texed.syntax_builtin = (0.7882354, 0.2313726, 0.572549)
        texed.syntax_reserved = (0.7529413, 0.3137255, 0.0)
        texed.syntax_preprocessor = (0.2745098, 0.0, 0.7529413)
        texed.space.back = (0.9137256, 0.9137256, 0.9137256)
        texed.syntax_string = (0.5960785, 0.0, 0.0)
        texed.syntax_numbers = (0.0, 0.0, 0.8470589)
        texed.syntax_comment = (0.0, 0.6470588, 0.3137255)
        texed.syntax_symbols = (0.0, 0.6, 0.6980392)
        texed.selected_text = (0.7215686, 0.8156863, 0.9019608)
        texed.space.text = (0.0, 0.0, 0.0)
        texed.cursor = (0.3607843, 0.6431373, 0.8980393)
        texed.line_numbers_background = (0.8588236, 0.8588236, 0.8588236)
        texed.syntax_special = (0.654902, 0.5960785, 0.027451)


def do_console_rewriter(ctx, m):
    fail = 'null ops, check spelling or be less specific'
    msg = fail
    if (m == 'obj='):
        msg = 'obj = bpy.context.active_object'
    elif (m == 'obj=['):
        msg = 'obj = bpy.data.objects[\''
    elif (len(m) > 5) and (m[5:] in bpy.data.objects):
        msg = "obj = bpy.data.objects['{0}']".format(m[5:])
    elif (m == 'n='):
        msg = 'nodes = bpy.data.node_groups[\'NodeTree\'].nodes'
    elif m.startswith('-fem'):
        msg = 'bm = bmesh.from_edit_mesh(C.object.data)'
    elif (m == 'n=['):
        msg = "ng = bpy.data.node_groups[\'"

    add_scrollback(m + ' --> ' + msg, 'OUTPUT')
    history_append(text=m, remove_duplicates=True)
    if not (msg == fail):
        ctx.space_data.history[-1].body = msg

