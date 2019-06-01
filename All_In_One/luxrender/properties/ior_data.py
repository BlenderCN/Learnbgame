# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from .. import LuxRenderAddon

ior_tree = [
    ("Liquids", [
        ("Acetone", 1),
        ("Alcohol, Ethyl (grain)", 2),
        ("Alcohol, Methyl (wood)", 3),
        ("Beer", 4),
        ("Benzene", 5),
        ("Carbon tetrachloride", 6),
        ("Carbon disulfide", 7),
        ("Carbonated Beverages", 8),
        ("Chlorine (liq)", 9),
        ("Cranberry Juice (25%)", 10),
        ("Glycerin", 11),
        ("Honey, 13% water content", 12),
        ("Honey, 17% water content", 13),
        ("Honey, 21% water content", 14),
        ("Ice", 15),
        ("Milk", 16),
        ("Oil, Clove", 17),
        ("Oil, Lemon", 18),
        ("Oil, Neroli", 19),
        ("Oil, Orange", 20),
        ("Oil, Safflower", 21),
        ("Oil, vegetable (50 C)", 22),
        ("Oil of Wintergreen", 23),
        ("Rum, White", 24),
        ("Shampoo", 25),
        ("Sugar Solution 30%", 26),
        ("Sugar Solution 80%", 27),
        ("Turpentine", 28),
        ("Vodka", 29),
        ("Water (0 C)", 30),
        ("Water (100 C)", 31),
        ("Water (20 C)", 32),
        ("Whisky", 33)
    ]),

    ("Gases", [
        ("Vacuum", 101),
        ("Air @ STP", 102),
        ("Air", 103), ("Helium", 104),
        ("Hydrogen", 105),
        ("Carbon dioxide", 106)
    ]),

    ("Transparent", [
        ("Eye, Aqueous humor", 201),
        ("Eye, Cornea", 202),
        ("Eye, Lens", 203),
        ("Eye, Vitreous humor", 204),
        ("Glass, Arsenic Trisulfide", 205),
        ("Glass, Crown (common)", 206),
        ("Glass, Flint, 29% lead", 207),
        ("Glass, Flint, 55% lead", 208),
        ("Glass, Flint, 71% lead", 209),
        ("Glass, Fused Silica", 210),
        ("Glass, Pyrex", 211),
        ("Lucite", 212),
        ("Nylon", 213),
        ("Obsidian", 214),
        ("Plastic", 215),
        ("Plexiglas", 216),
        ("Salt", 217)
    ]),

    ("Gemstones", [
        ("Agate", 301),
        ("Alexandrite", 302),
        ("Almandine", 303),
        ("Amber", 304),
        ("Amethyst", 305),
        ("Ammolite", 306),
        ("Andalusite", 307),
        ("Apatite", 308),
        ("Aquamarine", 309),
        ("Axenite", 310),
        ("Beryl", 311),
        ("Beryl, Red", 312),
        ("Chalcedony", 313),
        ("Chrome Tourmaline", 314),
        ("Citrine", 315),
        ("Clinohumite", 316),
        ("Coral", 317),
        ("Crystal", 318),
        ("Crysoberyl, Catseye", 319),
        ("Danburite", 320),
        ("Diamond", 321),
        ("Emerald", 322),
        ("Emerald Catseye", 323),
        ("Flourite", 324),
        ("Garnet, Grossular", 325),
        ("Garnet, Andradite", 326),
        ("Garnet, Demantiod", 327),
        ("Garnet, Mandarin", 328),
        ("Garnet, Pyrope", 329),
        ("Garnet, Rhodolite", 330),
        ("Garnet, Tsavorite", 331),
        ("Garnet, Uvarovite", 332),
        ("Hauyn", 333),
        ("Iolite", 334),
        ("Jade, Jadeite", 335),
        ("Jade, Nephrite", 336),
        ("Jet", 337),
        ("Kunzite", 338),
        ("Labradorite", 339),
        ("Lapis Lazuli", 340),
        ("Moonstone", 341),
        ("Morganite", 342),
        ("Obsidian", 343),
        ("Opal, Black", 344),
        ("Opal, Fire", 345),
        ("Opal, White", 346),
        ("Oregon Sunstone", 347),
        ("Padparadja", 348),
        ("Pearl", 349),
        ("Peridot", 350),
        ("Quartz", 351),
        ("Ruby", 352),
        ("Sapphire", 353),
        ("Sapphire, Star", 354),
        ("Spessarite", 355),
        ("Spinel", 356),
        ("Spinel, Blue", 357),
        ("Spinel, Red", 358),
        ("Star Ruby", 359),
        ("Tanzanite", 360),
        ("Topaz", 361),
        ("Topaz, Imperial", 362),
        ("Tourmaline", 363),
        ("Tourmaline, Blue", 364),
        ("Tourmaline, Catseye", 365),
        ("Tourmaline, Green", 366),
        ("Tourmaline, Paraiba", 367),
        ("Tourmaline, Red", 368),
        ("Zircon", 369),
        ("Zirconia, Cubic", 370)
    ]),

    ("Other ", [
        ("Pyrex (Borosilicate glass)", 401),
        ("Ruby", 402),
        ("Water ice", 403),
        ("Cryolite", 404),
        ("Acetone", 405),
        ("Ethanol", 406),
        ("Teflon", 407),
        ("Glycerol", 408),
        ("Acrylic glass", 409),
        ("Rock salt", 410),
        ("Crown glass (pure)", 411),
        ("Salt (NaCl)", 412),
        ("Polycarbonate", 413),
        ("PMMA", 414),
        ("PETg", 415),
        ("PET", 416),
        ("Flint glass (pure)", 417),
        ("Crown glass (impure)", 418),
        ("Fused Quartz", 419),
        ("Bromine", 420),
        ("Flint glass (impure)", 421),
        ("Cubic zirconia", 422),
        ("Moissanite", 423),
        ("Cinnabar (Mercury sulfide)", 424),
        ("Gallium(III) prosphide", 425),
        ("Gallium(III) arsenide", 426),
        ("Silicon", 427)
    ])
]

ior_dict = {
    1: 1.36,
    2: 1.36,
    3: 1.329,
    4: 1.345,
    5: 1.501,
    6: 1.000132,
    7: 1.00045,
    8: 1.34,
    9: 1.385,
    10: 1.351,
    11: 1.473,
    12: 1.504,
    13: 1.494,
    14: 1.484,
    15: 1.309,
    16: 1.35,
    17: 1.535,
    18: 1.481,
    19: 1.482,
    20: 1.473,
    21: 1.466,
    22: 1.47,
    23: 1.536,
    24: 1.361,
    25: 1.362,
    26: 1.38,
    27: 1.49,
    28: 1.472,
    29: 1.363,
    30: 1.33346,
    31: 1.31766,
    32: 1.33283,
    33: 1.356,
    101: 1.0,
    102: 1.0002926,
    103: 1.000293,
    104: 1.000036,
    105: 1.000132,
    106: 1.00045,
    201: 1.33,
    202: 1.38,
    203: 1.41,
    204: 1.34,
    205: 2.04,
    206: 1.52,
    207: 1.569,
    208: 1.669,
    209: 1.805,
    210: 1.459,
    211: 1.474,
    212: 1.495,
    213: 1.53,
    214: 1.50,
    215: 1.460,
    216: 1.488,
    217: 1.516,
    301: 1.544,
    302: 1.746,
    303: 1.75,
    304: 1.539,
    305: 1.532,
    306: 1.52,
    307: 1.629,
    308: 1.632,
    309: 1.567,
    310: 1.674,
    311: 1.57,
    312: 1.570,
    313: 1.544,
    314: 1.61,
    315: 1.532,
    316: 1.625,
    317: 1.486,
    318: 2.000,
    319: 1.746,
    320: 1.627,
    321: 2.417,
    322: 1.560,
    323: 1.560,
    324: 1.434,
    325: 1.72,
    326: 1.88,
    327: 1.880,
    328: 1.790,
    329: 1.73,
    330: 1.740,
    331: 1.739,
    332: 1.74,
    333: 1.490,
    334: 1.522,
    335: 1.64,
    336: 1.600,
    337: 1.660,
    338: 1.660,
    339: 1.560,
    340: 1.50,
    341: 1.518,
    342: 1.585,
    343: 1.50,
    344: 1.440,
    345: 1.430,
    346: 1.440,
    347: 1.560,
    348: 1.760,
    349: 1.53,
    350: 1.635,
    351: 1.544,
    352: 1.757,
    353: 1.757,
    354: 1.760,
    355: 1.79,
    356: 1.712,
    357: 1.712,
    358: 1.708,
    359: 1.76,
    360: 1.690,
    361: 1.607,
    362: 1.605,
    363: 1.603,
    364: 1.61,
    365: 1.61,
    366: 1.61,
    367: 1.61,
    368: 1.61,
    369: 1.777,
    370: 2.173,
    401: 1.47,
    402: 1.76,
    403: 1.31,
    404: 1.388,
    405: 1.36,
    406: 1.36,
    407: 1.35,
    408: 1.4729,
    409: 1.49,
    410: 1.516,
    411: 1.5,
    412: 1.544,
    413: 1.584,
    414: 1.4893,
    415: 1.57,
    416: 1.575,
    417: 1.6,
    418: 1.485,
    419: 1.46,
    420: 1.661,
    421: 1.523,
    422: 2.15,
    423: 2.419,
    424: 2.65,
    425: 3.02,
    426: 3.5,
    427: 3.927
}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_set_old_ior_preset(bpy.types.Operator):
    bl_idname = 'luxrender.set_old_ior_preset'
    bl_label = 'Apply IOR preset'

    index = bpy.props.IntProperty()
    l_name = bpy.props.StringProperty()

    def execute(self, context):
        ior = ior_dict[self.properties.index]
        name = self.properties.l_name

        # Detect either node or material or volume or texture context
        if 'node' in dir(context):
            # print("--->", context.node.__class__.__name__); # need it for further implementation tests
            lm = context.node
            ctx = context.node.__class__.__name__
            # print("--------", ctx)

            for mat_type in (
                    'glass', 'roughglass', 'glossy', 'glossycoating', 'glossy_lossy', 'glossytranslucent', 'node_glass',
                    'node_roughglass', 'node_glossy', 'node_glossycoating', 'node_glossytranslucent'):
                if ctx.endswith(mat_type):
                    lm.inputs['IOR'].index = ior
                    lm.inputs['IOR'].index_presetvalue = ior
                    lm.inputs['IOR'].index_presetstring = name

            for mat_type in ('mirror', 'shinymetal', 'node_mirror'):
                if ctx.endswith(mat_type):
                    lm.inputs['Film IOR'].filmindex = ior
                    lm.inputs['Film IOR'].filmindex_presetvalue = ior
                    lm.inputs['Film IOR'].filmindex_presetstring = name

            for mat_type in ('node_clear', 'node_homogeneous', 'node_heterogeneous', 'node_metal2'):
                if ctx.endswith(mat_type):
                    lm.inputs['IOR'].fresnel = ior
                    lm.inputs['IOR'].fresnel_presetvalue = ior
                    lm.inputs['IOR'].fresnel_presetstring = name

            for mat_type in ('cauchy', 'node_cauchy'):
                if ctx.endswith(mat_type):
                    lm.cauchy_n = ior
                    lm.cauchy_n_presetvalue = ior
                    lm.cauchy_n_presetstring = name

        else:
            if context.material and context.material.luxrender_material and not context.texture:
                lm = context.material.luxrender_material
                for mat_type in ('glass', 'roughglass', 'glossy', 'glossycoating', 'glossy_lossy', 'glossytranslucent'):
                    if lm.type == mat_type:
                        getattr(lm, 'luxrender_mat_%s' % mat_type).index_floatvalue = ior
                        getattr(lm, 'luxrender_mat_%s' % mat_type).index_presetvalue = ior
                        getattr(lm, 'luxrender_mat_%s' % mat_type).index_presetstring = name
                for mat_type in ('mirror', 'shinymetal'):
                    if lm.type == mat_type:
                        getattr(lm, 'luxrender_mat_%s' % mat_type).filmindex_floatvalue = ior
                        getattr(lm, 'luxrender_mat_%s' % mat_type).filmindex_presetvalue = ior
                        getattr(lm, 'luxrender_mat_%s' % mat_type).filmindex_presetstring = name
            elif context.texture.luxrender_texture.luxrender_tex_cauchy:
                context.texture.luxrender_texture.luxrender_tex_cauchy.ior = ior
                context.texture.luxrender_texture.luxrender_tex_cauchy.ior_presetvalue = ior
                context.texture.luxrender_texture.luxrender_tex_cauchy.ior_presetstring = name
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_set_volume_ior_preset(bpy.types.Operator):
    bl_idname = 'luxrender.set_volume_ior_preset'
    bl_label = 'Apply Volume IOR preset'

    index = bpy.props.IntProperty()
    l_name = bpy.props.StringProperty()

    def execute(self, context):
        ior = ior_dict[self.properties.index]
        name = self.properties.l_name

        if context.scene and context.scene.luxrender_volumes and not context.texture:
            vi = context.scene.luxrender_volumes.volumes_index
            lv = context.scene.luxrender_volumes.volumes[vi]
            lv.fresnel_fresnelvalue = ior
            lv.fresnel_presetvalue = ior
            lv.fresnel_presetstring = name

        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_set_coating_ior_preset(bpy.types.Operator):
    bl_idname = 'luxrender.set_coating_ior_preset'
    bl_label = 'Apply IOR preset'

    index = bpy.props.IntProperty()
    l_name = bpy.props.StringProperty()

    def execute(self, context):
        ior = ior_dict[self.properties.index]
        name = self.properties.l_name

        if context.material and context.material.luxrender_coating:
            lc = context.material.luxrender_coating
            lc.index_floatvalue = ior
            lc.index_presetvalue = ior
            lc.index_presetstring = name

        return {'FINISHED'}


def draw_generator(operator, m_names):
    def draw(self, context):
        sl = self.layout.row()
        for i, (m_name, m_index) in enumerate(m_names):
            if i % 20 == 0:
                cl = sl.column()

            op = cl.operator(operator, text=m_name)
            op.index = m_index
            op.l_name = m_name

    return draw


def create_ior_menu(name, opname):
    submenus = []
    for label, iors in ior_tree:
        submenu_idname = 'LUXRENDER_MT_ior_%s_cat%d' % (name, len(submenus))
        submenus.append(
            LuxRenderAddon.addon_register_class(type(
                submenu_idname,
                (bpy.types.Menu,),
                {
                    'bl_idname': submenu_idname,
                    'bl_label': label,
                    'draw': draw_generator(opname, iors)
                }
            ))
        )

    return submenus


class LUXRENDER_MT_ior_presets_base(bpy.types.Menu):
    def draw(self, context):
        sl = self.layout

        for sm in self.submenus:
            sl.menu(sm.bl_idname)


@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_ior_presets(LUXRENDER_MT_ior_presets_base):
    bl_label = 'IOR Presets'

    submenus = create_ior_menu('old', 'LUXRENDER_OT_set_old_ior_preset')


@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_ior_presets_volumes(LUXRENDER_MT_ior_presets_base):
    bl_label = 'Volume IOR Presets'

    submenus = create_ior_menu('volume', 'LUXRENDER_OT_set_volume_ior_preset')


@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_coating_ior_presets(LUXRENDER_MT_ior_presets_base):
    bl_label = 'IOR Presets'

    submenus = create_ior_menu('coating', 'LUXRENDER_OT_set_coating_ior_preset')
