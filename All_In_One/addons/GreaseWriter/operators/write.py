import bpy
import os
import copy
from .utils import draw_glyph

def get_char_name(char):
    character_dict = {
        "!": "exclamation",
        "#": "pound",
        "$": "dollar",
        "%": "percentage",
        "&": "ampersand",
        "'": "quotesingle",
        "(": "parenthesisleft",
        ")": "parenthesisright",
        "*": "asterisk",
        "+": "plus",
        ",": "comma",
        "-": "minus",
        ".": "period",
        "/": "slash",
        "№": "numero-sign",
        "0": "0",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        ":": "colon",
        ";": "semicolon",
        "<": "lessthan",
        "=": "equal",
        ">": "greaterthan",
        "?": "question",
        "@": "at",
        "A": "a-uppercase",
        "B": "b-uppercase",
        "C": "c-uppercase",
        "D": "d-uppercase",
        "E": "e-uppercase",
        "F": "f-uppercase",
        "G": "g-uppercase",
        "H": "h-uppercase",
        "I": "i-uppercase",
        "J": "j-uppercase",
        "K": "k-uppercase",
        "L": "l-uppercase",
        "M": "m-uppercase",
        "N": "n-uppercase",
        "O": "o-uppercase",
        "P": "p-uppercase",
        "Q": "q-uppercase",
        "R": "r-uppercase",
        "S": "s-uppercase",
        "T": "t-uppercase",
        "U": "u-uppercase",
        "V": "v-uppercase",
        "W": "w-uppercase",
        "X": "x-uppercase",
        "Y": "y-uppercase",
        "Z": "z-uppercase",
        "[": "bracketleft",
        "\\": "backslash",
        "]": "bracketright",
        "^": "caret",
        "_": "underscore",
        "`": "grave",
        "a": "a-lowercase",
        "b": "b-lowercase",
        "c": "c-lowercase",
        "d": "d-lowercase",
        "e": "e-lowercase",
        "f": "f-lowercase",
        "g": "g-lowercase",
        "h": "h-lowercase",
        "i": "i-lowercase",
        "j": "j-lowercase",
        "k": "k-lowercase",
        "l": "l-lowercase",
        "m": "m-lowercase",
        "n": "n-lowercase",
        "o": "o-lowercase",
        "p": "p-lowercase",
        "q": "q-lowercase",
        "r": "r-lowercase",
        "s": "s-lowercase",
        "t": "t-lowercase",
        "u": "u-lowercase",
        "v": "v-lowercase",
        "w": "w-lowercase",
        "x": "x-lowercase",
        "y": "y-lowercase",
        "z": "z-lowercase",
        "{": "curlyleft",
        "|": "verticalbar",
        "}": "curlyright",
        "~": "tilde",
        "Δ": "delta",
        "←": "arrowleft",
        "↑": "arrowup",
        "→": "arrowright",
        "↓": "arrowdown",
        "☐": "box",
        "♀": "female",
        "♂": "male",
        '"': "quotedouble",
        "°": "degree",

        # Russian Characters
        "а": "а-lowercase",
        "А": "а-uppercase",
        "б": "б-lowercase",
        "Б": "б-uppercase",
        "в": "в-lowercase",
        "В": "в-uppercase",
        "г": "г-lowercase",
        "Г": "г-uppercase",
        "д": "д-lowercase",
        "Д": "д-uppercase",
        "е": "е-lowercase",
        "Е": "е-uppercase",
        "ё": "ё-lowercase",
        "Ё": "ё-uppercase",
        "ж": "ж-lowercase",
        "Ж": "ж-uppercase",
        "з": "з-lowercase",
        "З": "з-uppercase",
        "и": "и-lowercase",
        "И": "и-uppercase",
        "й": "й-lowercase",
        "Й": "й-uppercase",
        "к": "к-lowercase",
        "К": "к-uppercase",
        "л": "л-lowercase",
        "Л": "л-uppercase",
        "м": "м-lowercase",
        "М": "м-uppercase",
        "н": "н-lowercase",
        "Н": "н-uppercase",
        "о": "о-lowercase",
        "О": "о-uppercase",
        "п": "п-lowercase",
        "П": "п-uppercase",
        "р": "р-lowercase",
        "Р": "р-uppercase",
        "с": "с-lowercase",
        "С": "с-uppercase",
        "т": "т-lowercase",
        "Т": "т-uppercase",
        "у": "у-lowercase",
        "У": "у-uppercase",
        "ф": "ф-lowercase",
        "Ф": "ф-uppercase",
        "х": "х-lowercase",
        "Х": "х-uppercase",
        "ц": "ц-lowercase",
        "Ц": "ц-uppercase",
        "ч": "ч-lowercase",
        "Ч": "ч-uppercase",
        "ш": "ш-lowercase",
        "Ш": "ш-uppercase",
        "щ": "щ-lowercase",
        "Щ": "щ-uppercase",
        "ъ": "ъ-lowercase",
        "Ъ": "ъ-uppercase",
        "ы": "ы-lowercase",
        "Ы": "ы-uppercase",
        "ь": "ь-lowercase",
        "Ь": "ь-uppercase",
        "э": "э-lowercase",
        "Э": "э-uppercase",
        "ю": "ю-lowercase",
        "Ю": "ю-uppercase",
        "я": "я-lowercase",
        "Я": "я-uppercase",

        # Tajik Characters
        "ғ": "ғ-lowercase",
        "Ғ": "ғ-uppercase",
        "ӣ": "ӣ-lowercase",
        "Ӣ": "ӣ-uppercase",
        "қ": "қ-lowercase",
        "Қ": "қ-uppercase",
        "ӯ": "ӯ-lowercase",
        "Ӯ": "ӯ-uppercase",
        "ҳ": "ҳ-lowercase",
        "Ҳ": "ҳ-uppercase",
        "ҷ": "ҷ-lowercase",
        "Ҷ": "ҷ-uppercase",

    }
    try:
        return character_dict[char]
    except KeyError:
        return character_dict['☐']


def get_glyph_width(vert_collection):
    verts = []
    for group in vert_collection:
        verts.extend(group)
    return max(verts, key=lambda v: v[0])[0]

def get_connection_points(vert_collection, y_range):
    verts = []
    for group in vert_collection:
        for vert in group:
            if vert[1] >= y_range[0] and vert[1] <= y_range[1]:
                verts.append(vert)
    min_x = min(verts, key=lambda v: v[0])[0]
    max_x = max(verts, key=lambda v: v[0])[0]
    return min_x, max_x

def get_glyph_verts(char):
    scene = bpy.context.scene
    font = scene.gw_font
    letter_folder = os.path.join(os.path.dirname(__file__), 'fonts', font)

    glyph_name = get_char_name(char) + ".glyph"
    try:
        with open(os.path.join(letter_folder, glyph_name)) as f:
            char_text = f.read().strip()
    except FileNotFoundError:
        with open(os.path.join(letter_folder, 'box.glyph')) as f:
            char_text = f.read().strip()
    lines = char_text.split('\n')

    glyph_verts = []
    for line in lines:
        verts = eval(line)
        glyph_verts.append(verts)
    return glyph_verts


class GREASEPENCIL_OT_write(bpy.types.Operator):
    bl_label = "Write"
    bl_idname = "grease_writer.write"
    bl_description = "Create drawn-animated text"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.gw_source_text != '' or scene.gw_source_text_file != '':
            return True
        else:
            return False

    def execute(self, context):
        scene = context.scene

        # Adjust settings for each font so they look good by default
        font_props = {
            "consolas": {
                "word space": 0.425,
                "kerning": 0.425,
                "line height": 1.1,
                #"monospace": True
            },
            "hershey_script_simplex": {
                "word space": 0.5,
                "kerning": 0.26,
                "line height": 2.2,
                # The cursive letters should connect somewhere within this y range
                "y_range": [0.63, 1.4],
            },
            "hershey_roman_simplex": {
                "word space": 0.5,
                "kerning": 0.185,
                "line height": 1.25,
            },
            "shohrukh_russian": {
                "word space": 0.4,
                "kerning": 0.2,
                "line height": 1.1,
            },
            "shohrukh_tajik": {
                "word space": 0.4,
                "kerning": 0.2,
                "line height": 1.1,
            },
        }

        gpencil = bpy.data.grease_pencil.new('greasewriter')

        color = scene.gw_color
        new_mat = bpy.data.materials.new('writings')
        bpy.data.materials.create_gpencil_data(new_mat)
        new_mat.grease_pencil.color[0] = color[0]
        new_mat.grease_pencil.color[1] = color[1]
        new_mat.grease_pencil.color[2] = color[2]

        obj = bpy.data.objects.new('greasewritten', gpencil)
        obj.data.materials.append(new_mat)
        bpy.context.scene.collection.objects.link(obj)

        if scene.gw_source_text != '':
            text = scene.gw_source_text.rstrip()
        elif scene.gw_source_text_file != '':
            text = bpy.data.texts[scene.gw_source_text_file].as_string().rstrip()

        font = scene.gw_font

        scale = scene.gw_scale

        font = scene.gw_font
        kerning = font_props[font]['kerning'] * scene.gw_kerning
        word_space = font_props[font]['word space'] * scene.gw_word_space
        line_height = font_props[font]['line height'] * scene.gw_line_height

        current_x = 0
        current_y = 0

        glyph_strokes = []
        prev_char = None

        c = 0
        while c < len(text):
            char = text[c]
            if char == " ":
                current_x += word_space
            elif char == "\n":
                current_y -= line_height
                current_x = 0
            else:
                glyph_verts = get_glyph_verts(char)
                unchanged_verts = copy.deepcopy(glyph_verts)
                glyph_width = get_glyph_width(glyph_verts)
                for group in glyph_verts:
                    for vert in group:
                        vert[0] += current_x
                        if 'monospace' in font_props[font]:
                            vert[0] += (kerning / 2) - (glyph_width / 2)
                        vert[1] += current_y - line_height

                    glyph_strokes.append(group)

                if char.isalpha() and 'y_range' in font_props[font] and c < len(text) - 1 and text[c + 1].isalpha():
                    this_connect_points = get_connection_points(unchanged_verts, font_props[font]['y_range'])
                    next_glyph_verts = get_glyph_verts(text[c + 1])
                    next_connect_points = get_connection_points(next_glyph_verts, font_props[font]['y_range'])

                    current_x += this_connect_points[1] - next_connect_points[0]

                elif 'monospace' in font_props[font]:
                    current_x += kerning

                else:
                    current_x += glyph_width + kerning
            c += 1

        draw_glyph(obj, glyph_strokes)

        obj.scale[0] = scale
        obj.scale[1] = scale
        obj.scale[2] = scale

        obj.empty_display_size = 0.5

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {"FINISHED"}
