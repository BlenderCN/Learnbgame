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

lampspectrum_tree = [
    ("Natural", [
        ("Natural Daylight", 1)
    ] ),
    ("Incandescent", [
        ("Paraffin Candle Flame", 2),
        ("Generic 7W Incandescent Lamp", 3),
        ("PHILIPS [Argenta] 200W Incandescent Lamp", 4),
        ("Welsbach Gas Mantle (modern, without Thorium)", 5),
        ("Incandescent Anti-Insect Lamp", 6)
    ] ),
    ("Fluorescent", [
        ("PHILIPS [TL-D 30W/55] Regular Daylight Fluorescent", 7),
        ("Sylvania [F4T5 4W] Regular Warm White Fluorescent", 8),
        ("OSRAM [DULUXSTAR 21W/827] Regular Compact Triphosphor Fluorescent", 9),
        ("Cold Cathode Warm White CFL Triphosphor Fluorescent.", 10),
        ("NARVA [COLOURLUX plus daylight 20W/860] Daylight CFL Triphosphor Fluorescent", 11),
        ("Sylvania [GroLux] Fluorescent Aquarium/Plant Lamp", 12),
        ("Laptop LCD Screen", 13),
        ("PHILIPS [ActiViva] \"Natural\" Triphosphor Fluorescent", 14),
        ("PHILIPS [ActiViva] \"Active\" Triphosphor Fluorescent", 16)
    ] ),
    ("High Pressure Mercury", [
        ("OSRAM [HQA 80W] Clear HPM Lamp", 17),
        ("PHILIPS [HPL 125W] HPM Lamp with improved color", 18),
        ("OSRAM [HQL 80W] HPM Lamp with improved warm deluxe color", 19),
        ("PHILIPS [ML 160W] Self-Ballasted HPM Vapor Lamp", 20),
        ("NARVA [160W] Self-ballasted HPM Vapor Lamp", 21)
    ] ),
    ("Sodium Discharge", [
        ("Regular High Pressure Sodium Lamp, warmup after 5-7 sec", 22),
        ("Regular High Pressure Sodium Lamp, warmup after 10-12 sec", 23),
        ("SOX Low Pressure Sodium Discharge Lamp", 24),
        ("Medium Pressure Sodium Discharge Lamp, warmup after ~35 sec", 25),
        ("GE [Lucalox 35W] High Pressure Sodium Lamp", 26),
        ("PHILIPS [SDW-T 100W] Super High Pressure White Sodium Lamp", 27)
    ] ),
    ("Metal Halide", [
        ("PHILIPS [HPI-T 400W] MH Lamp with Mercury, Sodium, Thallium and Indium iodides", 28),
        ("OSRAM [HQI-TS 75W/WDL] Metal Halide lamp with Mercury, sodium, thallium, indium and tin iodides, from ", 29),
        ("GE [MVR325IUWM 325 Watt I-Line Multi-Vapor Metal Halide - Clear Watt Miser] MH Lamp with Mercury, Sodium \
        and Scandium iodides", 30),
        ("OSRAM [HQI-T 400W/D] MH Lamp with Mercury, Thallium, Dysprosium, Holmium, Thulium and Caesium iodides", 31),
        ("PHILIPS Diazo MH Lamp with Mercury, iron and cobalt iodides", 32),
        ("Sylvania Diazo MH Lamp with Mercury, gallium and lead iodides", 33),
        ("OSRAM [HQI-T 400W/Blau] Blue colored MH Lamp with Mercury and indium iodides", 34),
        ("RADIUM [HRI-T 400W/Planta] Plant growing MH Lamp with Mercury, indium and sodium iodides", 35),
        ("OSRAM [HQI-T 400W/Grun] Green colored MH Lamp with Mercury and thallium iodides", 36)
    ] ),
    ("Diode", [
        ("Regular High Brightness Blue LED", 37),
        ("Monochromatic emission from a Red Laser diode", 38),
        ("Monochromatic emission from a Green Laser diode.", 39)
    ] ),
    ("Spectral", [
        ("PHILIPS Spectral Xenon Lamp - Continuous Xenon low pressure thermionic discharge", 40),
        ("PHILIPS spectral Rubidium Lamp - Continuous Rubidium low pressure thermionic discharge", 41),
        ("PHILIPS spectral Cadmium Lamp - Continuous Cadmium low pressure thermionic discharge", 42),
        ("PHILIPS spectral zinc Lamp - Continuous Zinc low pressure thermionic discharge", 43)
    ] ),
    ("Glow Discharge", [
        ("Neon glow discharge", 44),
        ("Neon and Krypton glow discharge and green phosphor (night-lights/indicators)", 45),
        ("Neon and Xenon glow discharge and green phosphor (night-lights/indicators)", 46),
        ("Neon and Xenon glow discharge and blue phosphor (night-lights/indicators)", 48),
        ("Argon glow discharge", 49),
        ("Self-ballasted High Pressure Mercury Vapor Lamp, with yttrium vanadate phosphate fluorescent phosphors, \
        in glow discharge mode", 50)
    ] ),
    ("Molecular", [
        ("Butane Gas Flame", 51),
        ("Alcohol Flame", 52)
    ] ),
    ("Fluorescence", [
        ("Print quality A4 Xerox paper wrapped around a blacklight Lamp", 53),
        ("Neon green dye, bombarded with black light", 54),
        ("Regular Modern Color TV CRT", 55)
    ] ),
    ("Various", [
        ("Stroboscopic flash. Xenon I, likely II and perhaps III", 56),
        ("Carbon Arc Spectrum", 57),
        ("OSRAM [XBO 75W/2] Short Arc Xenon Lamp", 58)
    ] ),
    ("Blacklight/UV", [
        ("Sylvania [G8T5 8W] Germicidal lamp", 59),
        ("Sylvania [F6T5/BLB 8W] Black light blue fluorescent", 60),
        # ("PHILIPS [HPW 125W] High Pressure Mercury Black Light", 61),
        ("Sylvania [Blacklite 350 F8W/BL350] Black Light fluorescent", 62)
    ] ),
    ("Mercury UV", [
        ("The near visible UVA emissions from a high pressure Mercury clear lamp", 63)
    ] ),
    ("Absorption/Mixed", [
        ("High Pressure Mercury Warm Deluxe light ([1.4.3]) absorbed through blue Cobalt glass", 64),
        ("Incandescent light ([1.2.3]) absorbed through blue Cobalt glass", 65),
        ("High Pressure Mercury Warm Deluxe light ([1.4.3]) absorbed through ciel dye #42053", 66),
        ("Incandescent light ([1.2.3]) absorbed through ciel dye #42053", 67),
        ("High Pressure Mercury Warm Deluxe light ([1.4.3]) absorbed through red glass", 68),
        ("Incandescent light ([1.2.3]) absorbed through red glass.m", 69),
        ("Incandescent light ([1.2.3]) absorbed through olive oil. ", 70)
    ] )
]

lampspectrum_names = {
    1: "Daylight", 2: "Candle", 3: "Incandescent1", 4: "Incandescent2",
    5: "Welsbach", 6: "AntiInsect", 7: "FLD2", 8: "FL37K",
    9: "CFL27K", 10: "CFL4K", 11: "CFL6K", 12: "GroLux",
    13: "LCDS", 14: "FLAV8K", 16: "FLAV17K",
    17: "HPM2", 18: "HPMFL1", 19: "HPMFL2", 20: "HPMSB",
    21: "HPMSBFL", 22: "SS1", 23: "SS2", 24: "LPS",
    25: "MPS", 26: "HPS", 27: "SHPS", 28: "MHN",
    29: "MHWWD", 30: "MHSc", 31: "MHD", 32: "FeCo",
    33: "GaPb", 34: "BLAU", 35: "PLANTA", 36: "GRUN",
    37: "LEDB", 38: "RedLaser", 39: "GreenLaser", 40: "XeI",
    41: "Rb", 42: "Cd", 43: "Zn", 44: "Ne",
    45: "NeKrFL", 46: "NeXeFL1", 48: "NeXeFL2",
    49: "Ar", 50: "HPMFL2Glow", 51: "Butane", 52: "Alcohol",
    53: "BLP", 54: "BLNG", 55: "TV", 56: "Xe",
    57: "CarbonArc", 58: "HPX", 59: "LPM2", 60: "FLBLB",
    # 61:"HPMBL",
    62: "FLBL", 63: "UVA", 64: "HPMFLCobaltGlass",
    65: "CobaltGlass", 66: "HPMFLCL42053", 67: "CL42053", 68: "HPMFLRedGlass",
    69: "RedGlass", 70: "OliveOil"
}


@LuxRenderAddon.addon_register_class
class TEXTURE_OT_set_lampspectrum_preset(bpy.types.Operator):
    bl_idname = 'texture.set_lampspectrum_preset'
    bl_label = 'Apply lampspectrum preset'

    index = bpy.props.IntProperty()
    l_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.texture and \
               context.texture.luxrender_texture and \
               context.texture.luxrender_texture.luxrender_tex_lampspectrum

    def execute(self, context):
        context.texture.luxrender_texture.luxrender_tex_lampspectrum.preset = lampspectrum_names[self.properties.index]
        context.texture.luxrender_texture.luxrender_tex_lampspectrum.label = self.properties.l_name
        return {'FINISHED'}


def draw_generator(operator, m_names):
    def draw(self, context):
        sl = self.layout
        for m_name, m_index in m_names:
            op = sl.operator(operator, text=m_name)
            op.index = m_index
            op.l_name = m_name

    return draw


@LuxRenderAddon.addon_register_class
class TEXTURE_MT_lampspectrum_presets(bpy.types.Menu):
    bl_label = 'Lampspectrum presets'
    submenus = []

    def draw(self, context):
        sl = self.layout

        for sm in self.submenus:
            sl.menu(sm.bl_idname)

    for label, spectra in lampspectrum_tree:
        submenu_idname = 'TEXTURE_MT_lampspectrum_cat%d' % len(submenus)
        submenus.append(
            LuxRenderAddon.addon_register_class(type(
                submenu_idname,
                (bpy.types.Menu,),
                {
                    'bl_idname': submenu_idname,
                    'bl_label': label,
                    'draw': draw_generator('TEXTURE_OT_set_lampspectrum_preset', spectra)
                }
            ))
        )
