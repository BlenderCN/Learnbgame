#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 Jakub Uhlík
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import sys
import traceback
import argparse
import textwrap
import os
import json
import shutil


quiet = False
LOG_FILE_PATH = None


def log(msg, indent=0):
    if(quiet):
        return
    m = "{0}> {1}".format("    " * indent, msg)
    print(m)
    if(LOG_FILE_PATH is not None):
        with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
            f.write("{}{}".format(m, "\n"))


def texture(t):
    if(t is None):
        return None
    if(t.isEmpty()):
        return None
    
    d = {'path': t.getPath(),
         'use_global_map': t.useGlobalMap,
         'channel': t.uvwChannelID,
         'brightness': t.brightness * 100,
         'contrast': t.contrast * 100,
         'saturation': t.saturation * 100,
         'hue': t.hue * 180,
         'rotation': t.rotation,
         'invert': t.invert,
         'interpolation': t.typeInterpolation,
         'use_alpha': t.useAlpha,
         'repeat': [t.scale.x(), t.scale.y()],
         'mirror': [t.uIsMirrored, t.vIsMirrored],
         'offset': [t.offset.x(), t.offset.y()],
         'clamp': [int(t.clampMin * 255), int(t.clampMax * 255)],
         'tiling_units': t.useAbsoluteUnits,
         'tiling_method': [t.uIsTiled, t.vIsTiled],
         'normal_mapping_flip_red': t.normalMappingFlipRed,
         'normal_mapping_flip_green': t.normalMappingFlipGreen,
         'normal_mapping_full_range_blue': t.normalMappingFullRangeBlue, }
    
    # t.cosA
    # t.doGammaCorrection
    # t.sinA
    # t.theTextureExtensions
    
    d['procedural'] = []
    if(t.hasProceduralTextures()):
        n = t.getProceduralTexturesCount()
        for i in range(n):
            pd = extension(None, None, t, i)
            d['procedural'].append(pd)
    
    return d


def material(s, m):
    data = {}
    if(m.isNull()):
        return data
    
    # defaults
    bsdfd = {'visible': True, 'weight': 100.0, 'weight_map_enabled': False, 'weight_map': None, 'ior': 0, 'complex_ior': "",
             'reflectance_0': (0.6, 0.6, 0.6, ), 'reflectance_0_map_enabled': False, 'reflectance_0_map': None,
             'reflectance_90': (1.0, 1.0, 1.0, ), 'reflectance_90_map_enabled': False, 'reflectance_90_map': None,
             'transmittance': (0.0, 0.0, 0.0), 'transmittance_map_enabled': False, 'transmittance_map': None,
             'attenuation': 1.0, 'attenuation_units': 0, 'nd': 3.0, 'force_fresnel': False, 'k': 0.0, 'abbe': 1.0,
             'r2_enabled': False, 'r2_falloff_angle': 75.0, 'r2_influence': 0.0,
             'roughness': 100.0, 'roughness_map_enabled': False, 'roughness_map': None,
             'bump': 30.0, 'bump_map_enabled': False, 'bump_map': None, 'bump_map_use_normal': False, 'bump_normal': 100.0,
             'anisotropy': 0.0, 'anisotropy_map_enabled': False, 'anisotropy_map': None,
             'anisotropy_angle': 0.0, 'anisotropy_angle_map_enabled': False, 'anisotropy_angle_map': None,
             'scattering': (0.5, 0.5, 0.5, ), 'coef': 0.0, 'asymmetry': 0.0,
             'single_sided': False, 'single_sided_value': 1.0, 'single_sided_map_enabled': False, 'single_sided_map': None, 'single_sided_min': 0.001, 'single_sided_max': 10.0, }
    coatingd = {'enabled': False,
                'thickness': 500.0, 'thickness_map_enabled': False, 'thickness_map': None, 'thickness_map_min': 100.0, 'thickness_map_max': 1000.0,
                'ior': 0, 'complex_ior': "",
                'reflectance_0': (0.6, 0.6, 0.6, ), 'reflectance_0_map_enabled': False, 'reflectance_0_map': None,
                'reflectance_90': (1.0, 1.0, 1.0, ), 'reflectance_90_map_enabled': False, 'reflectance_90_map': None,
                'nd': 3.0, 'force_fresnel': False, 'k': 0.0, 'r2_enabled': False, 'r2_falloff_angle': 75.0, }
    displacementd = {'enabled': False, 'map': None, 'type': 1, 'subdivision': 5, 'adaptive': False, 'subdivision_method': 0,
                     'offset': 0.5, 'smoothing': True, 'uv_interpolation': 2, 'height': 2.0, 'height_units': 0,
                     'v3d_preset': 0, 'v3d_transform': 0, 'v3d_rgb_mapping': 0, 'v3d_scale': (1.0, 1.0, 1.0), }
    emitterd = {'enabled': False, 'type': 0, 'ies_data': "", 'ies_intensity': 1.0,
                'spot_map_enabled': False, 'spot_map': "", 'spot_cone_angle': 45.0, 'spot_falloff_angle': 10.0, 'spot_falloff_type': 0, 'spot_blur': 1.0,
                'emission': 0, 'color': (1.0, 1.0, 1.0, ), 'color_black_body_enabled': False, 'color_black_body': 6500.0,
                'luminance': 0, 'luminance_power': 40.0, 'luminance_efficacy': 17.6, 'luminance_output': 100.0, 'temperature_value': 6500.0,
                'hdr_map': None, 'hdr_intensity': 1.0, }
    layerd = {'visible': True, 'opacity': 100.0, 'opacity_map_enabled': False, 'opacity_map': None, 'blending': 0, }
    globald = {'override_map': None, 'bump': 30.0, 'bump_map_enabled': False, 'bump_map': None, 'bump_map_use_normal': False, 'bump_normal': 100.0,
               'dispersion': False, 'shadow': False, 'matte': False, 'priority': 0, 'id': (0.0, 0.0, 0.0), 'active_display_map': None, }
    
    # structure
    structure = []
    nl, _ = m.getNumLayers()
    for i in range(nl):
        l = m.getLayer(i)
        ln, _ = l.getName()
        nb, _ = l.getNumBSDFs()
        bs = []
        for j in range(nb):
            b = l.getBSDF(j)
            bn = b.getName()
            bs.append([bn, b])
        ls = [ln, l, bs]
        structure.append(ls)
    
    # default data
    data['global_props'] = globald.copy()
    data['displacement'] = displacementd.copy()
    data['layers'] = []
    for i, sl in enumerate(structure):
        bsdfs = []
        for j, sb in enumerate(sl[2]):
            bsdfs.append({'name': sb[0],
                          'bsdf_props': bsdfd.copy(),
                          'coating': coatingd.copy(), })
        layer = {'name': sl[0],
                 'layer_props': layerd.copy(),
                 'bsdfs': bsdfs,
                 'emitter': emitterd.copy(), }
        data['layers'].append(layer)
    
    # custom data
    def global_props(m, d):
        t, _ = m.getGlobalMap()
        d['override_map'] = texture(t)
        
        a, _ = m.getAttribute('bump')
        if(a.activeType == MAP_TYPE_BITMAP):
            d['bump_map_enabled'] = True
            d['bump_map'] = texture(a.textureMap)
            d['bump_map_use_normal'] = m.getNormalMapState()[0]
            if(d['bump_map_use_normal']):
                d['bump_normal'] = a.value
            else:
                d['bump'] = a.value
        else:
            d['bump_map_enabled'] = False
            d['bump_map'] = None
            d['bump_map_use_normal'] = m.getNormalMapState()[0]
            if(d['bump_map_use_normal']):
                d['bump_normal'] = a.value
            else:
                d['bump'] = a.value
        
        d['dispersion'] = m.getDispersion()[0]
        d['shadow'] = m.getMatteShadow()[0]
        d['matte'] = m.getMatte()[0]
        d['priority'] = m.getNestedPriority()[0]
        
        c, _ = m.getColorID()
        d['id'] = [c.r(), c.g(), c.b()]
        return d
    
    data['global_props'] = global_props(m, data['global_props'])
    
    def displacement(m, d):
        if(not m.isDisplacementEnabled()[0]):
            return d
        d['enabled'] = True
        t, _ = m.getDisplacementMap()
        d['map'] = texture(t)
        
        displacementType, subdivisionLevel, smoothness, offset, subdivisionType, interpolationUvType, minLOD, maxLOD, _ = m.getDisplacementCommonParameters()
        height, absoluteHeight, adaptive, _ = m.getHeightMapDisplacementParameters()
        scale, transformType, mapping, preset, _ = m.getVectorDisplacementParameters()
        
        d['type'] = displacementType
        d['subdivision'] = subdivisionLevel
        d['adaptive'] = adaptive
        d['subdivision_method'] = subdivisionType
        d['offset'] = offset
        d['smoothing'] = bool(smoothness)
        d['uv_interpolation'] = interpolationUvType
        d['height'] = height
        d['height_units'] = absoluteHeight
        d['v3d_preset'] = preset
        d['v3d_transform'] = transformType
        d['v3d_rgb_mapping'] = mapping
        d['v3d_scale'] = (scale.x(), scale.y(), scale.z(), )
        
        return d
    
    data['displacement'] = displacement(m, data['displacement'])
    
    def cattribute_rgb(a):
        if(a.activeType == MAP_TYPE_BITMAP):
            c = (a.rgb.r(), a.rgb.g(), a.rgb.b())
            e = True
            m = texture(a.textureMap)
        else:
            c = (a.rgb.r(), a.rgb.g(), a.rgb.b())
            e = False
            m = None
        return c, e, m
    
    def cattribute_value(a):
        if(a.activeType == MAP_TYPE_BITMAP):
            v = a.value
            e = True
            m = texture(a.textureMap)
        else:
            v = a.value
            e = False
            m = None
        return v, e, m
    
    def layer_props(l, d):
        d['visible'] = l.getEnabled()[0]
        d['blending'] = l.getStackedBlendingMode()[0]
        a, _ = l.getAttribute('weight')
        if(a.activeType == MAP_TYPE_BITMAP):
            d['opacity'] = a.value
            d['opacity_map_enabled'] = True
            d['opacity_map'] = texture(a.textureMap)
        else:
            d['opacity'] = a.value
            d['opacity_map_enabled'] = False
            d['opacity_map'] = None
        return d
    
    def emitter(l, d):
        e = l.getEmitter()
        if(e.isNull()):
            d['enabled'] = False
            return d
        
        d['enabled'] = True
        d['type'] = e.getLobeType()[0]
        
        d['ies_data'] = e.getLobeIES()
        d['ies_intensity'] = e.getIESLobeIntensity()[0]
        
        t, _ = e.getLobeImageProjectedMap()
        d['spot_map_enabled'] = (not t.isEmpty())
        
        d['spot_map'] = texture(t)
        d['spot_cone_angle'] = e.getSpotConeAngle()[0]
        d['spot_falloff_angle'] = e.getSpotFallOffAngle()[0]
        d['spot_falloff_type'] = e.getSpotFallOffType()[0]
        d['spot_blur'] = e.getSpotBlur()[0]
        
        d['emission'] = e.getActiveEmissionType()[0]
        ep, _ = e.getPair()
        colorType, units, _ = e.getActivePair()
        
        d['color'] = (ep.rgb.r(), ep.rgb.g(), ep.rgb.b(), )
        d['color_black_body'] = ep.temperature
        
        d['luminance'] = units
        if(units == EMISSION_UNITS_WATTS_AND_LUMINOUS_EFFICACY):
            d['luminance_power'] = ep.watts
            d['luminance_efficacy'] = ep.luminousEfficacy
        elif(units == EMISSION_UNITS_LUMINOUS_POWER):
            d['luminance_output'] = ep.luminousPower
        elif(units == EMISSION_UNITS_ILLUMINANCE):
            d['luminance_output'] = ep.illuminance
        elif(units == EMISSION_UNITS_LUMINOUS_INTENSITY):
            d['luminance_output'] = ep.luminousIntensity
        elif(units == EMISSION_UNITS_LUMINANCE):
            d['luminance_output'] = ep.luminance
        if(colorType == EMISSION_COLOR_TEMPERATURE):
            d['color_black_body_enabled'] = True
        
        d['temperature_value'] = e.getTemperature()[0]
        a, _ = e.getMXI()
        if(a.activeType == MAP_TYPE_BITMAP):
            d['hdr_map'] = texture(a.textureMap)
            d['hdr_intensity'] = a.value
        else:
            d['hdr_map'] = None
            d['hdr_intensity'] = a.value
        
        return d
    
    def bsdf_props(b, d):
        d['visible'] = b.getState()[0]
        
        a, _ = b.getWeight()
        if(a.activeType == MAP_TYPE_BITMAP):
            d['weight_map_enabled'] = True
            d['weight'] = a.value
            d['weight_map'] = texture(a.textureMap)
        else:
            d['weight_map_enabled'] = False
            d['weight'] = a.value
            d['weight_map'] = None
        
        r = b.getReflectance()
        d['ior'] = r.getActiveIorMode()[0]
        d['complex_ior'] = r.getComplexIor()
        
        d['reflectance_0'], d['reflectance_0_map_enabled'], d['reflectance_0_map'] = cattribute_rgb(r.getAttribute('color')[0])
        d['reflectance_90'], d['reflectance_90_map_enabled'], d['reflectance_90_map'] = cattribute_rgb(r.getAttribute('color.tangential')[0])
        d['transmittance'], d['transmittance_map_enabled'], d['transmittance_map'] = cattribute_rgb(r.getAttribute('transmittance.color')[0])
        d['attenuation_units'], d['attenuation'] = r.getAbsorptionDistance()
        d['nd'], d['abbe'], _ = r.getIOR()
        d['force_fresnel'], _ = r.getForceFresnel()
        d['k'], _ = r.getConductor()
        d['r2_falloff_angle'], d['r2_influence'], d['r2_enabled'], _ = r.getFresnelCustom()
        
        d['roughness'], d['roughness_map_enabled'], d['roughness_map'] = cattribute_value(b.getAttribute('roughness')[0])
        d['bump_map_use_normal'] = b.getNormalMapState()[0]
        if(d['bump_map_use_normal']):
            d['bump_normal'], d['bump_map_enabled'], d['bump_map'] = cattribute_value(b.getAttribute('bump')[0])
        else:
            d['bump'], d['bump_map_enabled'], d['bump_map'] = cattribute_value(b.getAttribute('bump')[0])
        d['anisotropy'], d['anisotropy_map_enabled'], d['anisotropy_map'] = cattribute_value(b.getAttribute('anisotropy')[0])
        d['anisotropy_angle'], d['anisotropy_angle_map_enabled'], d['anisotropy_angle_map'] = cattribute_value(b.getAttribute('angle')[0])
        
        a, _ = r.getAttribute('scattering')
        d['scattering'] = (a.rgb.r(), a.rgb.g(), a.rgb.b(), )
        d['coef'], d['asymmetry'], d['single_sided'], _ = r.getScatteringParameters()
        d['single_sided_value'], d['single_sided_map_enabled'], d['single_sided_map'] = cattribute_value(r.getScatteringThickness()[0])
        d['single_sided_min'], d['single_sided_max'], _ = r.getScatteringThicknessRange()
        
        return d
    
    def coating(b, d):
        nc, _ = b.getNumCoatings()
        if(nc > 0):
            c = b.getCoating(0)
        else:
            d['enabled'] = False
            return d
        
        d['enabled'] = True
        d['thickness'], d['thickness_map_enabled'], d['thickness_map'] = cattribute_value(c.getThickness()[0])
        d['thickness_map_min'], d['thickness_map_max'], _ = c.getThicknessRange()
        
        r = c.getReflectance()
        d['ior'] = r.getActiveIorMode()[0]
        d['complex_ior'] = r.getComplexIor()
        
        d['reflectance_0'], d['reflectance_0_map_enabled'], d['reflectance_0_map'] = cattribute_rgb(r.getAttribute('color')[0])
        d['reflectance_90'], d['reflectance_90_map_enabled'], d['reflectance_90_map'] = cattribute_rgb(r.getAttribute('color.tangential')[0])
        
        d['nd'], _, _ = r.getIOR()
        d['force_fresnel'], _ = r.getForceFresnel()
        d['k'], _ = r.getConductor()
        d['r2_falloff_angle'], _, d['r2_enabled'], _ = r.getFresnelCustom()
        
        return d
    
    for i, sl in enumerate(structure):
        l = sl[1]
        data['layers'][i]['layer_props'] = layer_props(l, data['layers'][i]['layer_props'])
        data['layers'][i]['emitter'] = emitter(l, data['layers'][i]['emitter'])
        for j, bs in enumerate(sl[2]):
            b = bs[1]
            data['layers'][i]['bsdfs'][j]['bsdf_props'] = bsdf_props(b, data['layers'][i]['bsdfs'][j]['bsdf_props'])
            data['layers'][i]['bsdfs'][j]['coating'] = coating(b, data['layers'][i]['bsdfs'][j]['coating'])
    
    return data


def extension(s, m, pt=None, pi=None, ):
    def texture(t):
        if(t is None):
            return None
        if(t.isEmpty()):
            return None
        d = {'path': t.getPath(),
             'use_global_map': t.useGlobalMap,
             'channel': t.uvwChannelID,
             'brightness': t.brightness * 100,
             'contrast': t.contrast * 100,
             'saturation': t.saturation * 100,
             'hue': t.hue * 180,
             'rotation': t.rotation,
             'invert': t.invert,
             'interpolation': t.typeInterpolation,
             'use_alpha': t.useAlpha,
             'repeat': [t.scale.x(), t.scale.y()],
             'mirror': [t.uIsMirrored, t.vIsMirrored],
             'offset': [t.offset.x(), t.offset.y()],
             'clamp': [int(t.clampMin * 255), int(t.clampMax * 255)],
             'tiling_units': t.useAbsoluteUnits,
             'tiling_method': [t.uIsTiled, t.vIsTiled],
             'normal_mapping_flip_red': t.normalMappingFlipRed,
             'normal_mapping_flip_green': t.normalMappingFlipGreen,
             'normal_mapping_full_range_blue': t.normalMappingFullRangeBlue, }
        return d
    
    def mxparamlistarray(v):
        return None
    
    def rgb(v):
        return (v.r(), v.g(), v.b())
    
    if(pt is not None and pi is not None):
        params = pt.getProceduralTexture(pi)
    else:
        params, _ = m.getMaterialModifierExtensionParams()
    types = [(0, 'UCHAR', params.getByte, ),
             (1, 'UINT', params.getUInt, ),
             (2, 'INT', params.getInt, ),
             (3, 'FLOAT', params.getFloat, ),
             (4, 'DOUBLE', params.getDouble, ),
             (5, 'STRING', params.getString, ),
             (6, 'FLOATARRAY', params.getFloatArray, ),
             (7, 'DOUBLEARRAY', params.getDoubleArray, ),
             (8, 'BYTEARRAY', params.getByteArray, ),
             (9, 'INTARRAY', params.getIntArray, ),
             (10, 'MXPARAMLIST', params.getTextureMap, ),
             (11, 'MXPARAMLISTARRAY', mxparamlistarray, ),
             (12, 'RGB', params.getRgb, ), ]
    
    d = {}
    for i in range(params.getNumItems()):
        name, data, _, _, data_type, _, data_count, _ = params.getByIndex(i)
        _, _, f = types[data_type]
        k = name
        if(data_type not in [10, 11, 12]):
            v, _ = f(name)
        else:
            if(data_type == 10):
                v = texture(f(name)[0])
            elif(data_type == 11):
                pass
            elif(data_type == 12):
                v = rgb(f(name)[0])
        d[k] = v
    return d


def main(args):
    log("mxm to dict:", 1)
    p = args.mxm_path
    s = Cmaxwell(mwcallback)
    log("reading mxm from: {0}".format(p), 2)
    m = s.readMaterial(p)
    data = material(s, m)
    if(m.hasMaterialModifier()):
        data['extension'] = extension(s, m)
    log("serializing..", 2)
    p = args.data_path
    with open("{0}.tmp".format(p), 'w', encoding='utf-8', ) as f:
        json.dump(data, f, skipkeys=False, ensure_ascii=False, indent=4, )
    if(os.path.exists(p)):
        os.remove(p)
    shutil.move("{0}.tmp".format(p), p)
    log("done.", 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''mxm to dict'''), epilog='',
                                     formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True, )
    parser.add_argument('pymaxwell_path', type=str, help='path to directory containing pymaxwell')
    parser.add_argument('log_file', type=str, help='path to log file')
    parser.add_argument('mxm_path', type=str, help='path to .mxm')
    parser.add_argument('data_path', type=str, help='path to serialized data')
    args = parser.parse_args()
    
    PYMAXWELL_PATH = args.pymaxwell_path
    
    try:
        from pymaxwell import *
    except ImportError:
        if(not os.path.exists(PYMAXWELL_PATH)):
            raise OSError("pymaxwell for python 3.5 does not exist ({})".format(PYMAXWELL_PATH))
        sys.path.insert(0, PYMAXWELL_PATH)
        from pymaxwell import *
    
    LOG_FILE_PATH = args.log_file
    
    try:
        main(args)
    except Exception as e:
        m = traceback.format_exc()
        log(m)
        sys.exit(1)
    sys.exit(0)
