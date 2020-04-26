import re
from collections import OrderedDict
import numpy as np
from itertools import cycle

# Light version of webcolors
# http://stackoverflow.com/a/4382138/1060738
# Kelly's 22 colors of maximum contrast
kelly_colors = OrderedDict()
kelly_colors_dic = dict(vivid_yellow=(255, 179, 0),
                    strong_purple=(128, 62, 117),
                    vivid_orange=(255, 104, 0),
                    #very_light_blue=(166, 189, 215),
                    vivid_red=(193, 0, 32),
                    grayish_yellow=(206, 162, 98),
                    # medium_gray=(129, 112, 102),

                    # these aren't good for people with defective color vision:
                    vivid_green=(0, 125, 52),
                    strong_purplish_pink=(246, 118, 142),
                    strong_blue=(0, 83, 138),
                    strong_yellowish_pink=(255, 122, 92),
                    strong_violet=(83, 55, 122),
                    vivid_orange_yellow=(255, 142, 0),
                    strong_purplish_red=(179, 40, 81),
                    vivid_greenish_yellow=(244, 200, 0),
                    strong_reddish_brown=(127, 24, 13),
                    vivid_yellowish_green=(147, 170, 0),
                    deep_yellowish_brown=(89, 51, 21),
                    vivid_reddish_orange=(241, 58, 19),
                    dark_olive_green=(35, 44, 22))
for k in sorted(list(kelly_colors_dic.keys())):
    kelly_colors[k] = kelly_colors_dic[k]

# Boynton's list of 11 colors that are almost never confused.
boynton_colors = ["yellow", "green", "magenta", "blue", "red", "deepskyblue", "orange", "brown", 'darkblue', 'aquamarine', 'chocolate', 'indigo']#, "gray"]


def get_distinct_colors_hs(colors_num=0):
    Hs = np.linspace(0, 360, colors_num + 1)
    return Hs[:-1]


def get_distinct_colors(colors_num=0):
    # http://jsfiddle.net/tomfx/CKV65/
    if colors_num == 2:
        return cycle((np.array([kelly_colors_dic[col] for col in ['grayish_yellow', 'strong_violet']]) / 255.0).tolist())
    if colors_num <= len(boynton_colors) and colors_num != 0:
        return get_distinct_colors_boynton()
    else:
        return get_distinct_colors_kelly()


def get_distinct_colors_kelly():
    return cycle((np.array(list(kelly_colors.values())) / 255.0).tolist())


def get_distinct_colors_boynton():
    return cycle((np.array([name_to_rgb(c) for c in boynton_colors])).tolist())


def get_distinct_colors_names(colors_num=0):
    if colors_num <= len(boynton_colors) and colors_num != 0:
        return cycle(boynton_colors)
    else:
        return cycle(list(kelly_colors.keys()))


def get_distinct_colors_and_names(colors_num=0, boynton=False):
    if (colors_num <= len(boynton_colors) and colors_num != 0) or boynton:
        rgbs = (np.array([name_to_rgb(c) for c in boynton_colors])).tolist()
        names = boynton_colors
    else:
        rgbs = (np.array(list(kelly_colors.values())) / 255.0).tolist()
        names = list(kelly_colors.keys())
    return cycle(zip(rgbs, names))


NAMES_TO_HEX = {
    u'aliceblue': u'#f0f8ff',
    u'antiquewhite': u'#faebd7',
    u'aqua': u'#00ffff',
    u'aquamarine': u'#7fffd4',
    u'azure': u'#f0ffff',
    u'beige': u'#f5f5dc',
    u'bisque': u'#ffe4c4',
    u'black': u'#000000',
    u'blanchedalmond': u'#ffebcd',
    u'blue': u'#0000ff',
    u'blueviolet': u'#8a2be2',
    u'brown': u'#a52a2a',
    u'burlywood': u'#deb887',
    u'cadetblue': u'#5f9ea0',
    u'chartreuse': u'#7fff00',
    u'chocolate': u'#d2691e',
    u'coral': u'#ff7f50',
    u'cornflowerblue': u'#6495ed',
    u'cornsilk': u'#fff8dc',
    u'crimson': u'#dc143c',
    u'cyan': u'#00ffff',
    u'darkblue': u'#00008b',
    u'darkcyan': u'#008b8b',
    u'darkgoldenrod': u'#b8860b',
    u'darkgray': u'#a9a9a9',
    u'darkgrey': u'#a9a9a9',
    u'darkgreen': u'#006400',
    u'darkkhaki': u'#bdb76b',
    u'darkmagenta': u'#8b008b',
    u'darkolivegreen': u'#556b2f',
    u'darkorange': u'#ff8c00',
    u'darkorchid': u'#9932cc',
    u'darkred': u'#8b0000',
    u'darksalmon': u'#e9967a',
    u'darkseagreen': u'#8fbc8f',
    u'darkslateblue': u'#483d8b',
    u'darkslategray': u'#2f4f4f',
    u'darkslategrey': u'#2f4f4f',
    u'darkturquoise': u'#00ced1',
    u'darkviolet': u'#9400d3',
    u'deeppink': u'#ff1493',
    u'deepskyblue': u'#00bfff',
    u'dimgray': u'#696969',
    u'dimgrey': u'#696969',
    u'dodgerblue': u'#1e90ff',
    u'firebrick': u'#b22222',
    u'floralwhite': u'#fffaf0',
    u'forestgreen': u'#228b22',
    u'fuchsia': u'#ff00ff',
    u'gainsboro': u'#dcdcdc',
    u'ghostwhite': u'#f8f8ff',
    u'gold': u'#ffd700',
    u'goldenrod': u'#daa520',
    u'gray': u'#808080',
    u'grey': u'#808080',
    u'green': u'#008000',
    u'greenyellow': u'#adff2f',
    u'honeydew': u'#f0fff0',
    u'hotpink': u'#ff69b4',
    u'indianred': u'#cd5c5c',
    u'indigo': u'#4b0082',
    u'ivory': u'#fffff0',
    u'khaki': u'#f0e68c',
    u'lavender': u'#e6e6fa',
    u'lavenderblush': u'#fff0f5',
    u'lawngreen': u'#7cfc00',
    u'lemonchiffon': u'#fffacd',
    u'lightblue': u'#add8e6',
    u'lightcoral': u'#f08080',
    u'lightcyan': u'#e0ffff',
    u'lightgoldenrodyellow': u'#fafad2',
    u'lightgray': u'#d3d3d3',
    u'lightgrey': u'#d3d3d3',
    u'lightgreen': u'#90ee90',
    u'lightpink': u'#ffb6c1',
    u'lightsalmon': u'#ffa07a',
    u'lightseagreen': u'#20b2aa',
    u'lightskyblue': u'#87cefa',
    u'lightslategray': u'#778899',
    u'lightslategrey': u'#778899',
    u'lightsteelblue': u'#b0c4de',
    u'lightyellow': u'#ffffe0',
    u'lime': u'#00ff00',
    u'limegreen': u'#32cd32',
    u'linen': u'#faf0e6',
    u'magenta': u'#ff00ff',
    u'maroon': u'#800000',
    u'mediumaquamarine': u'#66cdaa',
    u'mediumblue': u'#0000cd',
    u'mediumorchid': u'#ba55d3',
    u'mediumpurple': u'#9370db',
    u'mediumseagreen': u'#3cb371',
    u'mediumslateblue': u'#7b68ee',
    u'mediumspringgreen': u'#00fa9a',
    u'mediumturquoise': u'#48d1cc',
    u'mediumvioletred': u'#c71585',
    u'midnightblue': u'#191970',
    u'mintcream': u'#f5fffa',
    u'mistyrose': u'#ffe4e1',
    u'moccasin': u'#ffe4b5',
    u'navajowhite': u'#ffdead',
    u'navy': u'#000080',
    u'oldlace': u'#fdf5e6',
    u'olive': u'#808000',
    u'olivedrab': u'#6b8e23',
    u'orange': u'#ffa500',
    u'orangered': u'#ff4500',
    u'orchid': u'#da70d6',
    u'palegoldenrod': u'#eee8aa',
    u'palegreen': u'#98fb98',
    u'paleturquoise': u'#afeeee',
    u'palevioletred': u'#db7093',
    u'papayawhip': u'#ffefd5',
    u'peachpuff': u'#ffdab9',
    u'peru': u'#cd853f',
    u'pink': u'#ffc0cb',
    u'plum': u'#dda0dd',
    u'powderblue': u'#b0e0e6',
    u'purple': u'#800080',
    u'red': u'#ff0000',
    u'rosybrown': u'#bc8f8f',
    u'royalblue': u'#4169e1',
    u'saddlebrown': u'#8b4513',
    u'salmon': u'#fa8072',
    u'sandybrown': u'#f4a460',
    u'seagreen': u'#2e8b57',
    u'seashell': u'#fff5ee',
    u'sienna': u'#a0522d',
    u'silver': u'#c0c0c0',
    u'skyblue': u'#87ceeb',
    u'slateblue': u'#6a5acd',
    u'slategray': u'#708090',
    u'slategrey': u'#708090',
    u'snow': u'#fffafa',
    u'springgreen': u'#00ff7f',
    u'steelblue': u'#4682b4',
    u'tan': u'#d2b48c',
    u'teal': u'#008080',
    u'thistle': u'#d8bfd8',
    u'tomato': u'#ff6347',
    u'turquoise': u'#40e0d0',
    u'violet': u'#ee82ee',
    u'wheat': u'#f5deb3',
    u'white': u'#ffffff',
    u'whitesmoke': u'#f5f5f5',
    u'yellow': u'#ffff00',
    u'yellowgreen': u'#9acd32',
}

HEX_COLOR_RE = re.compile(r'^#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$')


def name_to_rgb(name):
    """
    Convert a color name to a 3-tuple of integers suitable for use in
    an ``rgb()`` triplet specifying that color.

    """
    return np.array(hex_to_rgb(name_to_hex(name))) / 255.0


def name_to_hex(name):
    """
    Convert a color name to a normalized hexadecimal color value.
    When no color of that name exists in the given specification,
    ``ValueError`` is raised.

    """
    normalized = name.lower()
    hex_value = NAMES_TO_HEX.get(normalized)
    if hex_value is None:
        raise ValueError("Can't convert {} to hex!".format(name))
    return hex_value


def hex_to_rgb(hex_value):
    """
    Convert a hexadecimal color value to a 3-tuple of integers
    suitable for use in an ``rgb()`` triplet specifying that color.
    """
    hex_value = normalize_hex(hex_value)
    hex_value = int(hex_value[1:], 16)
    return (hex_value >> 16,
            hex_value >> 8 & 0xff,
            hex_value & 0xff)


def normalize_hex(hex_value):
    """
    Normalize a hexadecimal color value to 6 digits, lowercase.

    """
    match = HEX_COLOR_RE.match(hex_value)
    if match is None:
        raise ValueError('{} is not a valid hexadecimal color value'.format(hex_value))

    hex_digits = match.group(1)
    if len(hex_digits) == 3:
        hex_digits = u''.join(2 * s for s in hex_digits)
    return u'#{}'.format(hex_digits.lower())


