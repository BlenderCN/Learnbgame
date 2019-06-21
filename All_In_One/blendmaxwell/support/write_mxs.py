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
import json
import struct
import shutil
import math
import datetime
import os


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


class MXSBinMeshReader():
    def __init__(self, path):
        def r(f, b, o):
            d = struct.unpack_from(f, b, o)
            o += struct.calcsize(f)
            return d, o
        
        def r0(f, b, o):
            d = struct.unpack_from(f, b, o)[0]
            o += struct.calcsize(f)
            return d, o
        
        offset = 0
        with open(path, "rb") as bf:
            buff = bf.read()
        # endianness?
        signature = 20357755437992258
        l, _ = r0("<q", buff, 0)
        b, _ = r0(">q", buff, 0)
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            order = ">"
        else:
            raise AssertionError("{}: not a MXSBinMesh file".format(self.__class__.__name__))
        o = order
        # magic
        magic, offset = r0(o + "7s", buff, offset)
        magic = magic.decode(encoding="utf-8")
        if(magic != 'BINMESH'):
            raise RuntimeError()
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # name
        name, offset = r0(o + "250s", buff, offset)
        name = name.decode(encoding="utf-8").replace('\x00', '')
        # number of steps
        num_positions, offset = r0(o + "i", buff, offset)
        # number of vertices
        lv, offset = r0(o + "i", buff, offset)
        # vertex positions
        vertices = []
        for i in range(num_positions):
            vs, offset = r(o + "{}d".format(lv * 3), buff, offset)
            vs3 = [vs[i:i + 3] for i in range(0, len(vs), 3)]
            vertices.append(vs3)
        # vertex normals
        normals = []
        for i in range(num_positions):
            ns, offset = r(o + "{}d".format(lv * 3), buff, offset)
            ns3 = [ns[i:i + 3] for i in range(0, len(ns), 3)]
            normals.append(ns3)
        # number of triangle normals
        ltn, offset = r0(o + "i", buff, offset)
        # triangle normals
        triangle_normals = []
        for i in range(num_positions):
            tns, offset = r(o + "{}d".format(ltn * 3), buff, offset)
            tns3 = [tns[i:i + 3] for i in range(0, len(tns), 3)]
            triangle_normals.append(tns3)
        # number of triangles
        lt, offset = r0(o + "i", buff, offset)
        # triangles
        ts, offset = r(o + "{}i".format(lt * 6), buff, offset)
        triangles = [ts[i:i + 6] for i in range(0, len(ts), 6)]
        # number uv channels
        num_channels, offset = r0(o + "i", buff, offset)
        # uv channels
        uv_channels = []
        for i in range(num_channels):
            uvc, offset = r(o + "{}d".format(lt * 9), buff, offset)
            uv9 = [uvc[i:i + 9] for i in range(0, len(uvc), 9)]
            uv_channels.append(uv9)
        # number of materials
        num_materials, offset = r0(o + "i", buff, offset)
        # triangle materials
        tms, offset = r(o + "{}i".format(2 * lt), buff, offset)
        triangle_materials = [tms[i:i + 2] for i in range(0, len(tms), 2)]
        # throwaway
        _, offset = r(o + "?", buff, offset)
        # and now.. eof
        if(offset != len(buff)):
            raise RuntimeError("expected EOF")
        # collect data
        self.data = {'name': name,
                     'num_positions': num_positions,
                     'vertices': vertices,
                     'normals': normals,
                     'triangles': triangles,
                     'triangle_normals': triangle_normals,
                     'uv_channels': uv_channels,
                     'num_materials': num_materials,
                     'triangle_materials': triangle_materials, }


class MXSBinHairReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 23161492825065794
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinHair file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINHAIR'):
            raise RuntimeError()
        _ = r(o + "?")
        # number floats
        self.num = r(o + "i")[0]
        self.data = r(o + "{}d".format(self.num))
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class MXSBinParticlesReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 23734338517354818
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinParticles file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINPART'):
            raise RuntimeError()
        _ = r(o + "?")
        # 'PARTICLE_POSITIONS'
        n = r(o + "i")[0]
        self.PARTICLE_POSITIONS = r(o + "{}d".format(n))
        # 'PARTICLE_SPEEDS'
        n = r(o + "i")[0]
        self.PARTICLE_SPEEDS = r(o + "{}d".format(n))
        # 'PARTICLE_RADII'
        n = r(o + "i")[0]
        self.PARTICLE_RADII = r(o + "{}d".format(n))
        # 'PARTICLE_NORMALS'
        n = r(o + "i")[0]
        self.PARTICLE_NORMALS = r(o + "{}d".format(n))
        # 'PARTICLE_IDS'
        n = r(o + "i")[0]
        self.PARTICLE_IDS = r(o + "{}i".format(n))
        # 'PARTICLE_UVW'
        n = r(o + "i")[0]
        self.PARTICLE_UVW = r(o + "{}d".format(n))
        # eof
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class MXSBinWireReader():
    def __init__(self, path):
        self.offset = 0
        with open(path, "rb") as bf:
            self.bindata = bf.read()
        
        def r(f):
            d = struct.unpack_from(f, self.bindata, self.offset)
            self.offset += struct.calcsize(f)
            return d
        
        # endianness?
        signature = 19512248343873858
        l = r("<q")[0]
        self.offset = 0
        b = r(">q")[0]
        self.offset = 0
        if(l == signature):
            if(sys.byteorder != "little"):
                raise RuntimeError()
            self.order = "<"
        elif(b == signature):
            if(sys.byteorder != "big"):
                raise RuntimeError()
            self.order = ">"
        else:
            raise AssertionError("{}: not a MXSBinWire file".format(self.__class__.__name__))
        o = self.order
        # magic
        self.magic = r(o + "7s")[0].decode(encoding="utf-8")
        if(self.magic != 'BINWIRE'):
            raise RuntimeError()
        _ = r(o + "?")
        # number floats
        self.num = r(o + "i")[0]
        _ = r(o + "?")
        self.data = []
        for i in range(self.num):
            w = r(o + "33d")
            base = w[0:12]
            base = [base[i * 3:(i + 1) * 3] for i in range(4)]
            pivot = w[12:24]
            pivot = [pivot[i * 3:(i + 1) * 3] for i in range(4)]
            loc = w[24:27]
            rot = w[27:30]
            sca = w[30:33]
            self.data.append((base, pivot, loc, rot, sca, ))
        e = r(o + "?")
        if(self.offset != len(self.bindata)):
            raise RuntimeError("expected EOF")


class PercentDone():
    def __init__(self, total, prefix="> ", indent=0):
        self.current = 0
        self.percent = -1
        self.last = -1
        self.total = total
        self.prefix = prefix
        self.indent = indent
        self.t = "    "
        self.r = "\r"
        self.n = "\n"
    
    def step(self, numdone=1):
        if(quiet):
            return
        self.current += numdone
        self.percent = int(self.current / (self.total / 100))
        if(self.percent > self.last):
            sys.stdout.write(self.r)
            sys.stdout.write("{0}{1}{2}%".format(self.t * self.indent, self.prefix, self.percent))
            self.last = self.percent
        if(self.percent >= 100 or self.total == self.current):
            sys.stdout.write(self.r)
            sys.stdout.write("{0}{1}{2}%{3}".format(self.t * self.indent, self.prefix, 100, self.n))
            if(LOG_FILE_PATH is not None):
                with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
                    f.write("{}".format("{0}{1}{2}%{3}".format(self.t * self.indent, self.prefix, 100, self.n)))


def material_placeholder(s, n=None, ):
    if(n is not None):
        pass
    else:
        n = 'MATERIAL_PLACEHOLDER'
    m = s.createMaterial(n)
    l = m.addLayer()
    b = l.addBSDF()
    r = b.getReflectance()
    a = Cattribute()
    a.activeType = MAP_TYPE_BITMAP
    t = CtextureMap()
    mgr = CextensionManager.instance()
    e = mgr.createDefaultTextureExtension('Checker')
    ch = e.getExtensionData()
    ch.setUInt('Number of elements U', 32)
    ch.setUInt('Number of elements V', 32)
    t.addProceduralTexture(ch)
    a.textureMap = t
    r.setAttribute('color', a)
    return m


def material_default(d, s, ):
    m = s.createMaterial(d['name'])
    l = m.addLayer()
    b = l.addBSDF()
    return m


def material_external(d, s, ):
    p = d['path']
    t = s.readMaterial(p)
    t.setName(d['name'])
    m = s.addMaterial(t)
    if(not d['embed']):
        m.setReference(1, p)
    return m


def material_custom(d, s, ):
    m = s.createMaterial(d['name'])
    d = d['data']
    
    def global_props(d, m):
        # global properties
        if(d['override_map']):
            t = texture(d['override_map'], s, )
            if(t is not None):
                m.setGlobalMap(t)
        
        if(d['bump_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(d['bump_map'], s, )
            if(t is not None):
                a.textureMap = t
            if(d['bump_map_use_normal']):
                a.value = d['bump_normal']
            else:
                a.value = d['bump']
            m.setAttribute('bump', a)
            m.setNormalMapState(d['bump_map_use_normal'])
        
        m.setDispersion(d['dispersion'])
        m.setMatteShadow(d['shadow'])
        m.setMatte(d['matte'])
        m.setNestedPriority(d['priority'])
        
        c = Crgb()
        c.assign(*d['id'])
        m.setColorID(c)
        
        if(d['active_display_map']):
            t = texture(d['active_display_map'], s, )
            m.setActiveDisplayMap(t)
    
    def displacement(d, m):
        if(not d['enabled']):
            return
        
        m.enableDisplacement(True)
        if(d['map'] is not None):
            t = texture(d['map'], s)
            m.setDisplacementMap(t)
        m.setDisplacementCommonParameters(d['type'], d['subdivision'], int(d['smoothing']), d['offset'], d['subdivision_method'], d['uv_interpolation'], )
        m.setHeightMapDisplacementParameters(d['height'], d['height_units'], d['adaptive'], )
        v = Cvector(*d['v3d_scale'])
        m.setVectorDisplacementParameters(v, d['v3d_transform'], d['v3d_rgb_mapping'], d['v3d_preset'], )
    
    def add_bsdf(d, l):
        b = l.addBSDF()
        b.setName(d['name'])
        
        bp = d['bsdf_props']
        # weight
        if(bp['weight_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(bp['weight_map'], s, )
            if(t is not None):
                a.textureMap = t
            a.value = bp['weight']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            a.value = bp['weight']
        b.setWeight(a)
        # enabled
        if(not bp['visible']):
            b.setState(False)
        # ior
        r = b.getReflectance()
        if(bp['ior'] == 1):
            # measured data
            r.setActiveIorMode(1)
            r.setComplexIor(bp['complex_ior'])
        else:
            if(bp['reflectance_0_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(bp['reflectance_0_map'], s, )
                if(t is not None):
                    a.textureMap = t
                a.rgb.assign(*bp['reflectance_0'])
            else:
                a = Cattribute()
                a.activeType = MAP_TYPE_RGB
                a.rgb.assign(*bp['reflectance_0'])
            r.setAttribute('color', a)
            
            if(bp['reflectance_90_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(bp['reflectance_90_map'], s, )
                if(t is not None):
                    a.textureMap = t
                a.rgb.assign(*bp['reflectance_90'])
            else:
                a = Cattribute()
                a.activeType = MAP_TYPE_RGB
                a.rgb.assign(*bp['reflectance_90'])
            r.setAttribute('color.tangential', a)
            
            if(bp['transmittance_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(bp['transmittance_map'], s, )
                if(t is not None):
                    a.textureMap = t
                a.rgb.assign(*bp['transmittance'])
            else:
                a = Cattribute()
                a.activeType = MAP_TYPE_RGB
                a.rgb.assign(*bp['transmittance'])
            r.setAttribute('transmittance.color', a)
            
            r.setAbsorptionDistance(bp['attenuation_units'], bp['attenuation'])
            r.setIOR(bp['nd'], bp['abbe'])
            if(bp['force_fresnel']):
                r.enableForceFresnel(True)
            r.setConductor(bp['k'])
            if(bp['r2_enabled']):
                r.setFresnelCustom(bp['r2_falloff_angle'], bp['r2_influence'], True, )
        # surface
        if(bp['roughness_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(bp['roughness_map'], s, )
            if(t is not None):
                a.textureMap = t
            a.value = bp['roughness']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            a.value = bp['roughness']
        b.setAttribute('roughness', a)
        
        if(bp['bump_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(bp['bump_map'], s, )
            if(t is not None):
                a.textureMap = t
            if(bp['bump_map_use_normal']):
                a.value = bp['bump_normal']
            else:
                a.value = bp['bump']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            if(bp['bump_map_use_normal']):
                a.value = bp['bump_normal']
            else:
                a.value = bp['bump']
        b.setAttribute('bump', a)
        b.setNormalMapState(bp['bump_map_use_normal'])
        
        if(bp['anisotropy_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(bp['anisotropy_map'], s, )
            if(t is not None):
                a.textureMap = t
            a.value = bp['anisotropy']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            a.value = bp['anisotropy']
        b.setAttribute('anisotropy', a)
        
        if(bp['anisotropy_angle_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(bp['anisotropy_angle_map'], s, )
            if(t is not None):
                a.textureMap = t
            a.value = bp['anisotropy_angle']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            a.value = bp['anisotropy_angle']
        b.setAttribute('angle', a)
        
        # subsurface
        a = Cattribute()
        a.activeType = MAP_TYPE_RGB
        a.rgb.assign(*bp['scattering'])
        r.setAttribute('scattering', a)
        r.setScatteringParameters(bp['coef'], bp['asymmetry'], bp['single_sided'])
        if(bp['single_sided']):
            if(bp['single_sided_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(bp['single_sided_map'], s, )
                if(t is not None):
                    a.textureMap = t
                a.value = bp['single_sided_value']
            else:
                a = Cattribute()
                a.activeType = MAP_TYPE_VALUE
                a.value = bp['single_sided_value']
            r.setScatteringThickness(a)
            r.setScatteringThicknessRange(bp['single_sided_min'], bp['single_sided_max'])
        
        # coating
        cp = d['coating']
        if(cp['enabled']):
            c = b.addCoating()
            
            if(cp['thickness_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(cp['thickness_map'], s, )
                if(t is not None):
                    a.textureMap = t
                a.value = cp['thickness']
            else:
                a = Cattribute()
                a.activeType = MAP_TYPE_VALUE
                a.value = cp['thickness']
            c.setThickness(a)
            c.setThicknessRange(cp['thickness_map_min'], cp['thickness_map_max'])
            
            r = c.getReflectance()
            if(cp['ior'] == 1):
                # measured data
                r.setActiveIorMode(1)
                r.setComplexIor(cp['complex_ior'])
            else:
                if(cp['reflectance_0_map_enabled']):
                    a = Cattribute()
                    a.activeType = MAP_TYPE_BITMAP
                    t = texture(cp['reflectance_0_map'], s, )
                    if(t is not None):
                        a.textureMap = t
                    a.rgb.assign(*cp['reflectance_0'])
                else:
                    a = Cattribute()
                    a.activeType = MAP_TYPE_RGB
                    a.rgb.assign(*cp['reflectance_0'])
                r.setAttribute('color', a)
                
                if(cp['reflectance_90_map_enabled']):
                    a = Cattribute()
                    a.activeType = MAP_TYPE_BITMAP
                    t = texture(cp['reflectance_90_map'], s, )
                    if(t is not None):
                        a.textureMap = t
                    a.rgb.assign(*cp['reflectance_90'])
                else:
                    a = Cattribute()
                    a.activeType = MAP_TYPE_RGB
                    a.rgb.assign(*cp['reflectance_90'])
                r.setAttribute('color.tangential', a)
                r.setIOR(cp['nd'], 1.0, )
                if(cp['force_fresnel']):
                    r.enableForceFresnel(True)
                r.setConductor(cp['k'])
                if(cp['r2_enabled']):
                    r.setFresnelCustom(cp['r2_falloff_angle'], 0.0, True, )
    
    def add_emitter(d, l):
        e = l.createEmitter()
        
        if(d['type'] == 0):
            e.setLobeType(EMISSION_LOBE_DEFAULT)
        elif(d['type'] == 1):
            e.setLobeType(EMISSION_LOBE_IES)
            e.setLobeIES(d['ies_data'])
            e.setIESLobeIntensity(d['ies_intensity'])
        elif(d['type'] == 2):
            e.setLobeType(EMISSION_LOBE_SPOTLIGHT)
            if(d['spot_map'] is not None):
                t = texture(d['spot_map'], s)
                if(t is not None):
                    e.setLobeImageProjectedMap(d['spot_map_enabled'], t)
            e.setSpotConeAngle(d['spot_cone_angle'])
            e.setSpotFallOffAngle(d['spot_falloff_angle'])
            e.setSpotFallOffType(d['spot_falloff_type'])
            e.setSpotBlur(d['spot_blur'])
        if(d['emission'] == 0):
            e.setActiveEmissionType(EMISSION_TYPE_PAIR)
            ep = CemitterPair()
            c = Crgb()
            c.assign(*d['color'])
            ep.rgb.assign(c)
            ep.temperature = d['color_black_body']
            ep.watts = d['luminance_power']
            ep.luminousEfficacy = d['luminance_efficacy']
            ep.luminousPower = d['luminance_output']
            ep.illuminance = d['luminance_output']
            ep.luminousIntensity = d['luminance_output']
            ep.luminance = d['luminance_output']
            e.setPair(ep)
            
            if(d['luminance'] == 0):
                u = EMISSION_UNITS_WATTS_AND_LUMINOUS_EFFICACY
            elif(d['luminance'] == 1):
                u = EMISSION_UNITS_LUMINOUS_POWER
            elif(d['luminance'] == 2):
                u = EMISSION_UNITS_ILLUMINANCE
            elif(d['luminance'] == 3):
                u = EMISSION_UNITS_LUMINOUS_INTENSITY
            elif(d['luminance'] == 4):
                u = EMISSION_UNITS_LUMINANCE
            if(d['color_black_body_enabled']):
                e.setActivePair(EMISSION_COLOR_TEMPERATURE, u)
            else:
                e.setActivePair(EMISSION_RGB, u)
        
        elif(d['emission'] == 1):
            e.setActiveEmissionType(EMISSION_TYPE_TEMPERATURE)
            e.setTemperature(d['temperature_value'])
        elif(d['emission'] == 2):
            e.setActiveEmissionType(EMISSION_TYPE_MXI)
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(d['hdr_map'], s)
            if(t is not None):
                a.textureMap = t
            a.value = d['hdr_intensity']
            e.setMXI(a)
        
        e.setState(True)
    
    def add_layer(d, m):
        l = m.addLayer()
        l.setName(d['name'])
        
        lpd = d['layer_props']
        if(not lpd['visible']):
            l.setEnabled(False)
        if(lpd['blending'] == 1):
            l.setStackedBlendingMode(1)
        if(lpd['opacity_map_enabled']):
            a = Cattribute()
            a.activeType = MAP_TYPE_BITMAP
            t = texture(lpd['opacity_map'], s, )
            if(t is not None):
                a.textureMap = t
            a.value = lpd['opacity']
        else:
            a = Cattribute()
            a.activeType = MAP_TYPE_VALUE
            a.value = lpd['opacity']
        l.setAttribute('weight', a)
        
        epd = d['emitter']
        if(epd['enabled']):
            add_emitter(epd, l)
        
        for b in d['bsdfs']:
            add_bsdf(b, l)
    
    global_props(d['global_props'], m)
    displacement(d['displacement'], m)
    for layer in d['layers']:
        add_layer(layer, m)
    
    return m


def material(d, s, ):
    """create material by type"""
    if(d['subtype'] == 'EXTERNAL'):
        if(d['path'] == ''):
            m = material_placeholder(s, d['name'])
        else:
            m = material_external(d, s)
            
            if(d['override']):
                # global properties
                if(d['override_map']):
                    t = texture(d['override_map'], s, )
                    if(t is not None):
                        m.setGlobalMap(t)
                
                if(d['bump_map_enabled']):
                    a = Cattribute()
                    a.activeType = MAP_TYPE_BITMAP
                    t = texture(d['bump_map'], s, )
                    if(t is not None):
                        a.textureMap = t
                    if(d['bump_map_use_normal']):
                        a.value = d['bump_normal']
                    else:
                        a.value = d['bump']
                    m.setAttribute('bump', a)
                    m.setNormalMapState(d['bump_map_use_normal'])
                
                m.setDispersion(d['dispersion'])
                m.setMatteShadow(d['shadow'])
                m.setMatte(d['matte'])
                m.setNestedPriority(d['priority'])
                
                c = Crgb()
                c.assign(*d['id'])
                m.setColorID(c)
        
    elif(d['subtype'] == 'EXTENSION'):
        if(d['use'] == 'EMITTER'):
            m = s.createMaterial(d['name'])
            l = m.addLayer()
            e = l.createEmitter()
            
            if(d['emitter_type'] == 0):
                e.setLobeType(EMISSION_LOBE_DEFAULT)
            elif(d['emitter_type'] == 1):
                e.setLobeType(EMISSION_LOBE_IES)
                e.setLobeIES(d['emitter_ies_data'])
                e.setIESLobeIntensity(d['emitter_ies_intensity'])
            elif(d['emitter_type'] == 2):
                e.setLobeType(EMISSION_LOBE_SPOTLIGHT)
                if(d['emitter_spot_map'] is not None):
                    t = texture(d['emitter_spot_map'], s)
                    if(t is not None):
                        e.setLobeImageProjectedMap(d['emitter_spot_map_enabled'], t)
                e.setSpotConeAngle(d['emitter_spot_cone_angle'])
                e.setSpotFallOffAngle(d['emitter_spot_falloff_angle'])
                e.setSpotFallOffType(d['emitter_spot_falloff_type'])
                e.setSpotBlur(d['emitter_spot_blur'])
            
            if(d['emitter_emission'] == 0):
                e.setActiveEmissionType(EMISSION_TYPE_PAIR)
                
                ep = CemitterPair()
                c = Crgb()
                c.assign(*d['emitter_color'])
                ep.rgb.assign(c)
                ep.temperature = d['emitter_color_black_body']
                ep.watts = d['emitter_luminance_power']
                ep.luminousEfficacy = d['emitter_luminance_efficacy']
                ep.luminousPower = d['emitter_luminance_output']
                ep.illuminance = d['emitter_luminance_output']
                ep.luminousIntensity = d['emitter_luminance_output']
                ep.luminance = d['emitter_luminance_output']
                e.setPair(ep)
                
                if(d['emitter_luminance'] == 0):
                    u = EMISSION_UNITS_WATTS_AND_LUMINOUS_EFFICACY
                elif(d['emitter_luminance'] == 1):
                    u = EMISSION_UNITS_LUMINOUS_POWER
                elif(d['emitter_luminance'] == 2):
                    u = EMISSION_UNITS_ILLUMINANCE
                elif(d['emitter_luminance'] == 3):
                    u = EMISSION_UNITS_LUMINOUS_INTENSITY
                elif(d['emitter_luminance'] == 4):
                    u = EMISSION_UNITS_LUMINANCE
                if(d['emitter_color_black_body_enabled']):
                    e.setActivePair(EMISSION_COLOR_TEMPERATURE, u)
                else:
                    e.setActivePair(EMISSION_RGB, u)
            
            elif(d['emitter_emission'] == 1):
                e.setActiveEmissionType(EMISSION_TYPE_TEMPERATURE)
                e.setTemperature(d['emitter_temperature_value'])
            elif(d['emitter_emission'] == 2):
                e.setActiveEmissionType(EMISSION_TYPE_MXI)
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(d['emitter_hdr_map'], s)
                if(t is not None):
                    a.textureMap = t
                a.value = d['emitter_hdr_intensity']
                e.setMXI(a)
            
            e.setState(True)
            
            def global_props(d, m):
                # global properties
                if(d['override_map']):
                    t = texture(d['override_map'], s, )
                    if(t is not None):
                        m.setGlobalMap(t)
                
                if(d['bump_map_enabled']):
                    a = Cattribute()
                    a.activeType = MAP_TYPE_BITMAP
                    t = texture(d['bump_map'], s, )
                    if(t is not None):
                        a.textureMap = t
                    if(d['bump_map_use_normal']):
                        a.value = d['bump_normal']
                    else:
                        a.value = d['bump']
                    m.setAttribute('bump', a)
                    m.setNormalMapState(d['bump_map_use_normal'])
                
                m.setDispersion(d['dispersion'])
                m.setMatteShadow(d['shadow'])
                m.setMatte(d['matte'])
                m.setNestedPriority(d['priority'])
                
                c = Crgb()
                c.assign(*d['id'])
                m.setColorID(c)
                
                if(d['active_display_map']):
                    t = texture(d['active_display_map'], s, )
                    m.setActiveDisplayMap(t)
            
            global_props(d, m)
            
        else:
            m = CextensionManager.instance()
            if(d['use'] == 'AGS'):
                e = m.createDefaultMaterialModifierExtension('AGS')
                p = e.getExtensionData()
            
                c = Crgb()
                c.assign(*d['ags_color'])
                p.setRgb('Color', c)
                p.setFloat('Reflection', d['ags_reflection'])
                p.setUInt('Type', d['ags_type'])
            
            elif(d['use'] == 'OPAQUE'):
                e = m.createDefaultMaterialModifierExtension('Opaque')
                p = e.getExtensionData()
            
                p.setByte('Color Type', d['opaque_color_type'])
                c = Crgb()
                c.assign(*d['opaque_color'])
                p.setRgb('Color', c)
                texture_data_to_mxparams(d['opaque_color_map'], p, 'Color Map', )
            
                p.setByte('Shininess Type', d['opaque_shininess_type'])
                p.setFloat('Shininess', d['opaque_shininess'])
                texture_data_to_mxparams(d['opaque_shininess_map'], p, 'Shininess Map', )
            
                p.setByte('Roughness Type', d['opaque_roughness_type'])
                p.setFloat('Roughness', d['opaque_roughness'])
                texture_data_to_mxparams(d['opaque_roughness_map'], p, 'Roughness Map', )
            
                p.setByte('Clearcoat', d['opaque_clearcoat'])
            
            elif(d['use'] == 'TRANSPARENT'):
                e = m.createDefaultMaterialModifierExtension('Transparent')
                p = e.getExtensionData()
            
                p.setByte('Color Type', d['transparent_color_type'])
                c = Crgb()
                c.assign(*d['transparent_color'])
                p.setRgb('Color', c)
                texture_data_to_mxparams(d['transparent_color_map'], p, 'Color Map', )
            
                p.setFloat('Ior', d['transparent_ior'])
                p.setFloat('Transparency', d['transparent_transparency'])
            
                p.setByte('Roughness Type', d['transparent_roughness_type'])
                p.setFloat('Roughness', d['transparent_roughness'])
                texture_data_to_mxparams(d['transparent_roughness_map'], p, 'Roughness Map', )
            
                p.setFloat('Specular Tint', d['transparent_specular_tint'])
                p.setFloat('Dispersion', d['transparent_dispersion'])
                p.setByte('Clearcoat', d['transparent_clearcoat'])
            
            elif(d['use'] == 'METAL'):
                e = m.createDefaultMaterialModifierExtension('Metal')
                p = e.getExtensionData()
            
                p.setUInt('IOR', d['metal_ior'])
            
                p.setFloat('Tint', d['metal_tint'])
            
                p.setByte('Color Type', d['metal_color_type'])
                c = Crgb()
                c.assign(*d['metal_color'])
                p.setRgb('Color', c)
                texture_data_to_mxparams(d['metal_color_map'], p, 'Color Map', )
            
                p.setByte('Roughness Type', d['metal_roughness_type'])
                p.setFloat('Roughness', d['metal_roughness'])
                texture_data_to_mxparams(d['metal_roughness_map'], p, 'Roughness Map', )
            
                p.setByte('Anisotropy Type', d['metal_anisotropy_type'])
                p.setFloat('Anisotropy', d['metal_anisotropy'])
                texture_data_to_mxparams(d['metal_anisotropy_map'], p, 'Anisotropy Map', )
            
                p.setByte('Angle Type', d['metal_angle_type'])
                p.setFloat('Angle', d['metal_angle'])
                texture_data_to_mxparams(d['metal_angle_map'], p, 'Angle Map', )
            
                p.setByte('Dust Type', d['metal_dust_type'])
                p.setFloat('Dust', d['metal_dust'])
                texture_data_to_mxparams(d['metal_dust_map'], p, 'Dust Map', )
            
                p.setByte('Perforation Enabled', d['metal_perforation_enabled'])
                texture_data_to_mxparams(d['metal_perforation_map'], p, 'Perforation Map', )
            
            elif(d['use'] == 'TRANSLUCENT'):
                e = m.createDefaultMaterialModifierExtension('Translucent')
                p = e.getExtensionData()
            
                p.setFloat('Scale', d['translucent_scale'])
                p.setFloat('Ior', d['translucent_ior'])
            
                p.setByte('Color Type', d['translucent_color_type'])
                c = Crgb()
                c.assign(*d['translucent_color'])
                p.setRgb('Color', c)
                texture_data_to_mxparams(d['translucent_color_map'], p, 'Color Map', )
            
                p.setFloat('Hue Shift', d['translucent_hue_shift'])
                p.setByte('Invert Hue', d['translucent_invert_hue'])
                p.setFloat('Vibrance', d['translucent_vibrance'])
                p.setFloat('Density', d['translucent_density'])
                p.setFloat('Opacity', d['translucent_opacity'])
            
                p.setByte('Roughness Type', d['translucent_roughness_type'])
                p.setFloat('Roughness', d['translucent_roughness'])
                texture_data_to_mxparams(d['translucent_roughness_map'], p, 'Roughness Map', )
            
                p.setFloat('Specular Tint', d['translucent_specular_tint'])
                p.setByte('Clearcoat', d['translucent_clearcoat'])
                p.setFloat('Clearcoat Ior', d['translucent_clearcoat_ior'])
            
            elif(d['use'] == 'CARPAINT'):
                e = m.createDefaultMaterialModifierExtension('Car Paint')
                p = e.getExtensionData()
            
                c = Crgb()
                c.assign(*d['carpaint_color'])
                p.setRgb('Color', c)
            
                p.setFloat('Metallic', d['carpaint_metallic'])
                p.setFloat('Topcoat', d['carpaint_topcoat'])
            
            elif(d['use'] == 'HAIR'):
                e = m.createDefaultMaterialModifierExtension('Hair')
                p = e.getExtensionData()
                
                p.setByte('Color Type', d['hair_color_type'])
                
                c = Crgb()
                c.assign(*d['hair_color'])
                p.setRgb('Color', c)
                texture_data_to_mxparams(d['hair_color_map'], p, 'Color Map', )
                
                texture_data_to_mxparams(d['hair_root_tip_map'], p, 'Root-Tip Map', )
                
                p.setByte('Root-Tip Weight Type', d['hair_root_tip_weight_type'])
                p.setFloat('Root-Tip Weight', d['hair_root_tip_weight'])
                texture_data_to_mxparams(d['hair_root_tip_weight_map'], p, 'Root-Tip Weight Map', )
                
                p.setFloat('Primary Highlight Strength', d['hair_primary_highlight_strength'])
                p.setFloat('Primary Highlight Spread', d['hair_primary_highlight_spread'])
                c = Crgb()
                c.assign(*d['hair_primary_highlight_tint'])
                p.setRgb('Primary Highlight Tint', c)
                
                p.setFloat('Secondary Highlight Strength', d['hair_secondary_highlight_strength'])
                p.setFloat('Secondary Highlight Spread', d['hair_secondary_highlight_spread'])
                c = Crgb()
                c.assign(*d['hair_secondary_highlight_tint'])
                p.setRgb('Secondary Highlight Tint', c)
            
            m = s.createMaterial(d['name'])
            m.applyMaterialModifierExtension(p)
            
            # global properties
            if(d['override_map']):
                t = texture(d['override_map'], s, )
                if(t is not None):
                    m.setGlobalMap(t)
            
            if(d['bump_map_enabled']):
                a = Cattribute()
                a.activeType = MAP_TYPE_BITMAP
                t = texture(d['bump_map'], s, )
                if(t is not None):
                    a.textureMap = t
                if(d['bump_map_use_normal']):
                    a.value = d['bump_normal']
                else:
                    a.value = d['bump']
                m.setAttribute('bump', a)
                m.setNormalMapState(d['bump_map_use_normal'])
            
            m.setDispersion(d['dispersion'])
            m.setMatteShadow(d['shadow'])
            m.setMatte(d['matte'])
            
            m.setNestedPriority(d['priority'])
            
            c = Crgb()
            c.assign(*d['id'])
            m.setColorID(c)
            
            if(d['active_display_map']):
                t = texture(d['active_display_map'], s, )
                m.setActiveDisplayMap(t)
            
            def displacement(d, m):
                if(not d['enabled']):
                    return
                
                m.enableDisplacement(True)
                if(d['map'] is not None):
                    t = texture(d['map'], s)
                    m.setDisplacementMap(t)
                m.setDisplacementCommonParameters(d['type'], d['subdivision'], int(d['smoothing']), d['offset'], d['subdivision_method'], d['uv_interpolation'], )
                m.setHeightMapDisplacementParameters(d['height'], d['height_units'], d['adaptive'], )
                v = Cvector(*d['v3d_scale'])
                m.setVectorDisplacementParameters(v, d['v3d_transform'], d['v3d_rgb_mapping'], d['v3d_preset'], )
            
            try:
                displacement(d['displacement'], m)
            except KeyError:
                pass
            
    elif(d['subtype'] == 'CUSTOM'):
        material_custom(d, s, )
    else:
        raise TypeError("Material '{}' {} is unknown type".format(d['name'], d['subtype']))


def get_material(n, s, ):
    """get material by name from scene, if material is missing, create and return placeholder"""
    def get_material_names(s):
        it = CmaxwellMaterialIterator()
        o = it.first(s)
        l = []
        while not o.isNull():
            name = o.getName()
            l.append(name)
            o = it.next()
        return l
    
    names = get_material_names(s)
    m = None
    if(n in names):
        m = s.getMaterial(n)
    if(m is None):
        # should not happen because i stopped changing material names.. but i leave it here
        m = material_placeholder(s)
    return m


def texture(d, s, ):
    if(d is None):
        return
    
    t = CtextureMap()
    t.setPath(d['path'])
    
    t.uvwChannelID = d['channel']
    
    t.brightness = d['brightness'] / 100
    t.contrast = d['contrast'] / 100
    t.saturation = d['saturation'] / 100
    t.hue = d['hue'] / 180
    
    t.useGlobalMap = d['use_global_map']
    t.useAbsoluteUnits = d['tile_method_units']
    
    t.uIsTiled = d['tile_method_type'][0]
    t.vIsTiled = d['tile_method_type'][1]
    
    t.uIsMirrored = d['mirror'][0]
    t.vIsMirrored = d['mirror'][1]
    
    vec = Cvector2D()
    vec.assign(d['offset'][0], d['offset'][1])
    t.offset = vec
    t.rotation = d['rotation']
    t.invert = d['invert']
    t.useAlpha = d['alpha_only']
    if(d['interpolation']):
        t.typeInterpolation = 1
    else:
        t.typeInterpolation = 0
    t.clampMin = d['rgb_clamp'][0] / 255
    t.clampMax = d['rgb_clamp'][1] / 255
    
    vec = Cvector2D()
    vec.assign(d['repeat'][0], d['repeat'][1])
    t.scale = vec
    
    t.normalMappingFlipRed = d['normal_mapping_flip_red']
    t.normalMappingFlipGreen = d['normal_mapping_flip_green']
    t.normalMappingFullRangeBlue = d['normal_mapping_full_range_blue']
    
    # t.cosA
    # t.doGammaCorrection
    # t.sinA
    # t.theTextureExtensions
    
    m = CextensionManager.instance()
    for i, pt in enumerate(d['procedural']):
        if(pt['use'] == 'BRICK'):
            e = m.createDefaultTextureExtension('Brick')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setFloat('Brick width', pt['brick_brick_width'])
            p.setFloat('Brick height', pt['brick_brick_height'])
            p.setInt('Brick offset', pt['brick_brick_offset'])
            p.setInt('Random offset', pt['brick_random_offset'])
            p.setByte('Double brick', pt['brick_double_brick'])
            p.setFloat('Small brick width', pt['brick_small_brick_width'])
            p.setByte('Round corners', pt['brick_round_corners'])
            p.setFloat('Boundary sharpness U', pt['brick_boundary_sharpness_u'])
            p.setFloat('Boundary sharpness V', pt['brick_boundary_sharpness_v'])
            p.setInt('Boundary noise detail', pt['brick_boundary_noise_detail'])
            p.setFloat('Boundary noise region U', pt['brick_boundary_noise_region_u'])
            p.setFloat('Boundary noise region V', pt['brick_boundary_noise_region_v'])
            p.setUInt('Seed', pt['brick_seed'])
            p.setByte('Random rotation', pt['brick_random_rotation'])
            p.setInt('Color variation', pt['brick_color_variation'])
            c = Crgb()
            c.assign(*pt['brick_brick_color_0'])
            p.setRgb('Brick color 0', c)
            texture_data_to_mxparams(pt['brick_brick_texture_0'], p, 'Brick texture 0', )
            p.setInt('Sampling factor 0', pt['brick_sampling_factor_0'])
            p.setInt('Weight 0', pt['brick_weight_0'])
            c = Crgb()
            c.assign(*pt['brick_brick_color_1'])
            p.setRgb('Brick color 1', c)
            texture_data_to_mxparams(pt['brick_brick_texture_1'], p, 'Brick texture 1', )
            p.setInt('Sampling factor 1', pt['brick_sampling_factor_1'])
            p.setInt('Weight 1', pt['brick_weight_1'])
            c = Crgb()
            c.assign(*pt['brick_brick_color_2'])
            p.setRgb('Brick color 2', c)
            texture_data_to_mxparams(pt['brick_brick_texture_2'], p, 'Brick texture 2', )
            p.setInt('Sampling factor 2', pt['brick_sampling_factor_2'])
            p.setInt('Weight 2', pt['brick_weight_2'])
            p.setFloat('Mortar thickness', pt['brick_mortar_thickness'])
            c = Crgb()
            c.assign(*pt['brick_mortar_color'])
            p.setRgb('Mortar color', c)
            texture_data_to_mxparams(pt['brick_mortar_texture'], p, 'Mortar texture', )
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'CHECKER'):
            e = m.createDefaultTextureExtension('Checker')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            c = Crgb()
            c.assign(*pt['checker_color_0'])
            p.setRgb('Color0', c)
            c = Crgb()
            c.assign(*pt['checker_color_1'])
            p.setRgb('Color1', c)
            p.setUInt('Number of elements U', pt['checker_number_of_elements_u'])
            p.setUInt('Number of elements V', pt['checker_number_of_elements_v'])
            p.setFloat('Transition sharpness', pt['checker_transition_sharpness'])
            p.setUInt('Fall-off', pt['checker_falloff'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'CIRCLE'):
            e = m.createDefaultTextureExtension('Circle')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            c = Crgb()
            c.assign(*pt['circle_background_color'])
            p.setRgb('Background color', c)
            c = Crgb()
            c.assign(*pt['circle_circle_color'])
            p.setRgb('Circle color', c)
            p.setFloat('RadiusU', pt['circle_radius_u'])
            p.setFloat('RadiusV', pt['circle_radius_v'])
            p.setFloat('Transition factor', pt['circle_transition_factor'])
            p.setUInt('Fall-off', pt['circle_falloff'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'GRADIENT3'):
            e = m.createDefaultTextureExtension('Gradient3')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setByte('Gradient U', pt['gradient3_gradient_u'])
            c = Crgb()
            c.assign(*pt['gradient3_color0_u'])
            p.setRgb('Color0 U', c)
            c = Crgb()
            c.assign(*pt['gradient3_color1_u'])
            p.setRgb('Color1 U', c)
            c = Crgb()
            c.assign(*pt['gradient3_color2_u'])
            p.setRgb('Color2 U', c)
            p.setUInt('Gradient type U', pt['gradient3_gradient_type_u'])
            p.setFloat('Color1 U position', pt['gradient3_color1_u_position'])
            p.setByte('Gradient V', pt['gradient3_gradient_v'])
            c = Crgb()
            c.assign(*pt['gradient3_color0_v'])
            p.setRgb('Color0 V', c)
            c = Crgb()
            c.assign(*pt['gradient3_color1_v'])
            p.setRgb('Color1 V', c)
            c = Crgb()
            c.assign(*pt['gradient3_color2_v'])
            p.setRgb('Color2 V', c)
            p.setUInt('Gradient type V', pt['gradient3_gradient_type_v'])
            p.setFloat('Color1 V position', pt['gradient3_color1_v_position'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'GRADIENT'):
            e = m.createDefaultTextureExtension('Gradient')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setByte('Gradient U', pt['gradient_gradient_u'])
            c = Crgb()
            c.assign(*pt['gradient_color0_u'])
            p.setRgb('Color0 U', c)
            c = Crgb()
            c.assign(*pt['gradient_color1_u'])
            p.setRgb('Color1 U', c)
            p.setUInt('Gradient type U', pt['gradient_gradient_type_u'])
            p.setFloat('Transition factor U', pt['gradient_transition_factor_u'])
            p.setByte('Gradient V', pt['gradient_gradient_v'])
            c = Crgb()
            c.assign(*pt['gradient_color0_v'])
            p.setRgb('Color0 V', c)
            c = Crgb()
            c.assign(*pt['gradient_color1_v'])
            p.setRgb('Color1 V', c)
            p.setUInt('Gradient type V', pt['gradient_gradient_type_v'])
            p.setFloat('Transition factor V', pt['gradient_transition_factor_v'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'GRID'):
            e = m.createDefaultTextureExtension('Grid')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            c = Crgb()
            c.assign(*pt['grid_boundary_color'])
            p.setRgb('Boundary color', c)
            c = Crgb()
            c.assign(*pt['grid_cell_color'])
            p.setRgb('Cell color', c)
            
            p.setFloat('Cell width', pt['grid_cell_width'])
            p.setFloat('Cell height', pt['grid_cell_height'])
            if(pt['grid_horizontal_lines']):
                p.setFloat('Boundary thickness U', pt['grid_boundary_thickness_u'])
            else:
                p.setFloat('Boundary thickness U', 0.0)
            if(pt['grid_vertical_lines']):
                p.setFloat('Boundary thickness V', pt['grid_boundary_thickness_v'])
            else:
                p.setFloat('Boundary thickness V', 0.0)
            p.setFloat('Transition sharpness', pt['grid_transition_sharpness'])
            p.setUInt('Fall-off', pt['grid_falloff'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'MARBLE'):
            e = m.createDefaultTextureExtension('Marble')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setUInt('Coordinates type', pt['marble_coordinates_type'])
            c = Crgb()
            c.assign(*pt['marble_color0'])
            p.setRgb('Color0', c)
            c = Crgb()
            c.assign(*pt['marble_color1'])
            p.setRgb('Color1', c)
            c = Crgb()
            c.assign(*pt['marble_color2'])
            p.setRgb('Color2', c)
            p.setFloat('Frequency', pt['marble_frequency'])
            p.setFloat('Detail', pt['marble_detail'])
            p.setInt('Octaves', pt['marble_octaves'])
            p.setUInt('Seed', pt['marble_seed'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'NOISE'):
            e = m.createDefaultTextureExtension('Noise')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setUInt('Coordinates type', pt['noise_coordinates_type'])
            c = Crgb()
            c.assign(*pt['noise_noise_color'])
            p.setRgb('Noise color', c)
            c = Crgb()
            c.assign(*pt['noise_background_color'])
            p.setRgb('Background color', c)
            p.setFloat('Detail', pt['noise_detail'])
            p.setFloat('Persistance', pt['noise_persistance'])
            p.setInt('Octaves', pt['noise_octaves'])
            p.setFloat('Low value', pt['noise_low_value'])
            p.setFloat('High value', pt['noise_high_value'])
            p.setUInt('Seed', pt['noise_seed'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'VORONOI'):
            e = m.createDefaultTextureExtension('Voronoi')
            p = e.getExtensionData()
            
            p.setFloat('Blend procedural', pt['blending_factor'])
            
            p.setUInt('Coordinates type', pt['voronoi_coordinates_type'])
            c = Crgb()
            c.assign(*pt['voronoi_color0'])
            p.setRgb('Color0', c)
            c = Crgb()
            c.assign(*pt['voronoi_color1'])
            p.setRgb('Color1', c)
            p.setInt('Detail', pt['voronoi_detail'])
            p.setUInt('Distance', pt['voronoi_distance'])
            p.setUInt('Combination', pt['voronoi_combination'])
            p.setFloat('Low value', pt['voronoi_low_value'])
            p.setFloat('High value', pt['voronoi_high_value'])
            p.setUInt('Seed', pt['voronoi_seed'])
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'TILED'):
            e = m.createDefaultTextureExtension('TiledTexture')
            p = e.getExtensionData()
            
            p.setFloat('Blend factor', pt['blending_factor'])
            
            c = Crgb()
            c.assign(*pt['tiled_base_color'])
            p.setRgb('Base Color', c)
            p.setByte('Use base color', pt['tiled_use_base_color'])
            p.setString('Filename_mask', pt['tiled_token_mask'])
            p.setString('Filename', pt['tiled_filename'])
            # 'Map U tile range' UCHAR
            # 'Map V tile range' UCHAR
            
            t.addProceduralTexture(p)
        elif(pt['use'] == 'WIREFRAME'):
            e = m.createDefaultTextureExtension('WireframeTexture')
            p = e.getExtensionData()
            
            c = Crgb()
            c.assign(*pt['wireframe_fill_color'])
            p.setRgb('Fill Color', c)
            c = Crgb()
            c.assign(*pt['wireframe_edge_color'])
            p.setRgb('Edge Color', c)
            c = Crgb()
            c.assign(*pt['wireframe_coplanar_edge_color'])
            p.setRgb('Coplanar Edge Color', c)
            p.setFloat('Edge Width', pt['wireframe_edge_width'])
            p.setFloat('Coplanar Edge Width', pt['wireframe_coplanar_edge_width'])
            p.setFloat('Coplanar Threshold', pt['wireframe_coplanar_threshold'])
            
            t.addProceduralTexture(p)
        else:
            raise TypeError("{0} is unknown procedural texture type".format(pt['use']))
    
    return t


def base_and_pivot(o, d, ):
    b = d['base']
    p = d['pivot']
    bb = Cbase()
    bb.origin = Cvector(*b[0])
    bb.xAxis = Cvector(*b[1])
    bb.yAxis = Cvector(*b[2])
    bb.zAxis = Cvector(*b[3])
    pp = Cbase()
    pp.origin = Cvector(*p[0])
    pp.xAxis = Cvector(*p[1])
    pp.yAxis = Cvector(*p[2])
    pp.zAxis = Cvector(*p[3])
    o.setBaseAndPivot(bb, pp)
    
    l = d['location']
    r = d['rotation']
    s = d['scale']
    o.setPivotPosition(Cvector(*l))
    o.setPivotRotation(Cvector(*r))
    o.setPosition(Cvector(*l))
    o.setRotation(Cvector(*r))
    o.setScale(Cvector(*s))
    
    for(t, _, b, p) in d['motion_blur']:
        bb = Cbase()
        bb.origin = Cvector(*b[0])
        bb.xAxis = Cvector(*b[1])
        bb.yAxis = Cvector(*b[2])
        bb.zAxis = Cvector(*b[3])
        pp = Cbase()
        pp.origin = Cvector(*p[0])
        pp.xAxis = Cvector(*p[1])
        pp.yAxis = Cvector(*p[2])
        pp.zAxis = Cvector(*p[3])
        o.setBaseAndPivot(bb, pp, t, )


def object_props(o, d, ):
    if(d['hidden_camera']):
        o.setHideToCamera(True)
    if(d['hidden_camera_in_shadow_channel']):
        o.setHideToCameraInShadowsPass(True)
    if(d['hidden_global_illumination']):
        o.setHideToGI(True)
    if(d['hidden_reflections_refractions']):
        o.setHideToReflectionsRefractions(True)
    if(d['hidden_zclip_planes']):
        o.excludeOfCutPlanes(True)
    if(d['opacity'] != 100.0):
        o.setOpacity(d['opacity'])
    if(d['hide']):
        o.setHide(d['hide'])
    c = Crgb()
    c.assign(*d['object_id'])
    o.setColorID(c)
    for n in d['blocked_emitters']:
        ok = o.addExcludedLight(n)


def camera(d, s, ):
    if(d['lens'] in [6, 7]):
        c = s.addCamera(d['name'], d['number_of_steps'], d['shutter'], d['film_width'], d['film_height'], d['iso'],
                        d['aperture'], d['diaphragm_angle'], d['diaphragm_blades'], d['frame_rate'],
                        d['resolution_x'], d['resolution_y'], d['pixel_aspect'], TYPE_EXTENSION_LENS, )
    else:
        c = s.addCamera(d['name'], d['number_of_steps'], d['shutter'], d['film_width'], d['film_height'], d['iso'],
                        d['aperture'], d['diaphragm_angle'], d['diaphragm_blades'], d['frame_rate'],
                        d['resolution_x'], d['resolution_y'], d['pixel_aspect'], d['lens'], )
    
    c.setCameraResponsePreset(d['response'])
    
    if(d['custom_bokeh']):
        c.setCustomBokeh(d['bokeh_ratio'], d['bokeh_angle'], True)
    
    for s in d['steps']:
        o = Cvector()
        o.assign(*s[1])
        f = Cvector()
        f.assign(*s[2])
        u = Cvector()
        u.assign(*s[3])
        c.setStep(s[0], o, f, u, s[4], s[5], s[6], s[7], )
    
    if(d['lens'] == 3):
        c.setFishLensProperties(d['fov'])
    if(d['lens'] == 4):
        c.setSphericalLensProperties(d['azimuth'])
    if(d['lens'] == 5):
        c.setCylindricalLensProperties(d['angle'])
    
    if(d['lens'] == 6):
        p = MXparamList()
        p.createString('EXTENSION_NAME', 'Lat-Long Stereo')
        p.createUInt('Type', d['lls_type'], 0, 2)
        p.createFloat('FOV Vertical', d['lls_fovv'], 180.0, 0.0)
        p.createFloat('FOV Horizontal', d['lls_fovh'], 360.0, 0.0)
        p.createByte('Flip Ray X', d['lls_flip_ray_x'], 0, 1)
        p.createByte('Flip Ray Y', d['lls_flip_ray_y'], 0, 1)
        p.createFloat('Parallax Distance', d['lls_parallax_distance'], 0.0, 360.0)
        p.createByte('Zenith Mode', d['lls_zenith_mode'], 0, 1)
        p.createFloat('Separation', d['lls_separation'], 0.0, 100000.0)
        p.createTextureMap('Separation Map', CtextureMap())
        texture_data_to_mxparams(d['lls_separation_map'], p, 'Separation Map')
        c.applyCameraLensExtension(p)
    
    if(d['lens'] == 7):
        p = MXparamList()
        p.createString('EXTENSION_NAME', 'Fish Stereo')
        p.createUInt('Type', d['fs_type'], 0, 2)
        p.createFloat('FOV', d['fs_fov'], 0.0, 360.0)
        p.createFloat('Separation', d['fs_separation'], 0.0, 1000000.0)
        p.createTextureMap('Separation Map', CtextureMap())
        texture_data_to_mxparams(d['fs_separation_map'], p, 'Separation Map')
        p.createByte('Dome Tilt Compensation', d['fs_dome_tilt_compensation'], 0, 1)
        p.createFloat('Dome Tilt', d['fs_dome_tilt'], 0.0, 90.0)
        p.createByte('Vertical Mode', d['fs_vertical_mode'], 0, 1)
        p.createFloat('Dome Radius', d['fs_dome_radius'], 1.0, 1000000.0)
        p.createTextureMap('Turn Map', CtextureMap())
        texture_data_to_mxparams(d['fs_head_turn_map'], p, 'Turn Map')
        p.createTextureMap('Tilt Map', CtextureMap())
        texture_data_to_mxparams(d['fs_head_tilt_map'], p, 'Tilt Map')
        c.applyCameraLensExtension(p)
    
    c.setCutPlanes(d['set_cut_planes'][0], d['set_cut_planes'][1], d['set_cut_planes'][2], )
    c.setShiftLens(d['set_shift_lens'][0], d['set_shift_lens'][1], )
    if(d['screen_region'] != 'NONE'):
        r = d['screen_region_xywh']
        if(r[2] == d['resolution_x']):
            r[2] -= 1
        if(r[3] == d['resolution_y']):
            r[3] -= 1
        c.setScreenRegion(r[0], r[1], r[2], r[3], d['screen_region'])
    if(d['active']):
        c.setActive()
    return c


def empty(d, s, ):
    o = s.createMesh(d['name'], 0, 0, 0, 0,)
    base_and_pivot(o, d)
    object_props(o, d)
    return o


def mesh(d, s, ):
    r = MXSBinMeshReader(d['mesh_data_path'])
    m = r.data
    o = s.createMesh(d['name'], d['num_vertexes'], d['num_normals'], d['num_triangles'], d['num_positions_per_vertex'], )
    
    for i in range(len(m['uv_channels'])):
        o.addChannelUVW(i)
    
    # an = 0
    for ip in range(m['num_positions']):
        # reset counter in each run, its value should be the same for each position anyway, it only used as offset for triangle normals
        an = 0
        verts = m['vertices'][ip]
        norms = m['normals'][ip]
        for i, loc in enumerate(verts):
            o.setVertex(i, ip, Cvector(*loc), )
            o.setNormal(i, ip, Cvector(*norms[i]), )
            an += 1
    
    for ip in range(m['num_positions']):
        trinorms = m['triangle_normals'][ip]
        for i, nor in enumerate(trinorms):
            o.setNormal(an + i, ip, Cvector(*nor), )
    for i, tri in enumerate(m['triangles']):
        o.setTriangle(i, *tri)
    for iuv, uv in enumerate(m['uv_channels']):
        for it, t in enumerate(uv):
            o.setTriangleUVW(it, iuv, *t)
    
    if(d['num_materials'] > 1):
        # multi material
        mats = []
        for i in range(d['num_materials']):
            try:
                n = d['materials'][i]
                mat = get_material(n, s, )
            except:
                mat = material_placeholder(s)
            mats.append(mat)
        
        for tid, mid in m['triangle_materials']:
            o.setTriangleMaterial(tid, mats[mid])
    else:
        # single material
        if(len(d['materials']) == 1):
            if(d['materials'][0] != ''):
                mat = get_material(d['materials'][0], s, )
                o.setMaterial(mat)
    
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)
    
    return o


def instance(d, s, ):
    bo = s.getObject(d['instanced'])
    o = s.createInstancement(d['name'], bo)
    
    if(d['num_materials'] > 1):
        # multi material instances inherits material from base object
        pass
    else:
        # single material, and i think (not sure) i can't make instance with different material than base in blender..
        if(len(d['materials']) == 1):
            if(d['materials'][0] != ''):
                mat = get_material(d['materials'][0], s, )
                o.setMaterial(mat)
    
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)
    return o


def scene(d, s, ):
    h, t = os.path.split(d["output_mxi"])
    n, e = os.path.splitext(t)
    base_path = os.path.join(h, n)
    
    def get_ext_depth(t, e=None):
        if(e is not None):
            t = "{}{}".format(e[1:].upper(), int(t[3:]))
        
        if(t == 'RGB8'):
            return ('.png', 8)
        elif(t == 'RGB16'):
            return ('.png', 16)
        elif(t == 'RGB32'):
            return ('.exr', 32)
        elif(t == 'PNG8'):
            return ('.png', 8)
        elif(t == 'PNG16'):
            return ('.png', 16)
        elif(t == 'TGA'):
            return ('.tga', 8)
        elif(t == 'TIF8'):
            return ('.tif', 8)
        elif(t == 'TIF16'):
            return ('.tif', 16)
        elif(t == 'TIF32'):
            return ('.tif', 32)
        elif(t == 'EXR16'):
            return ('.exr', 16)
        elif(t == 'EXR32'):
            return ('.exr', 32)
        elif(t == 'EXR_DEEP'):
            return ('.exr', 32)
        elif(t == 'JPG'):
            return ('.jpg', 8)
        elif(t == 'JP2'):
            return ('.jp2', 8)
        elif(t == 'HDR'):
            return ('.hdr', 32)
        elif(t == 'DTEX'):
            return ('.dtex', 32)
        elif(t == 'PSD8'):
            return ('.psd', 8)
        elif(t == 'PSD16'):
            return ('.psd', 16)
        elif(t == 'PSD32'):
            return ('.psd', 32)
        else:
            return ('.tif', 8)
    
    _, depth = get_ext_depth(d["output_depth"], os.path.splitext(os.path.split(d["output_image"])[1])[1])
    s.setPath('RENDER', d["output_image"], depth)
    
    e, depth = get_ext_depth(d["channels_alpha_file"])
    s.setPath('ALPHA', "{}_alpha{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_shadow_file"])
    s.setPath('SHADOW', "{}_shadow{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_object_id_file"])
    s.setPath('OBJECT', "{}_object_id{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_material_id_file"])
    s.setPath('MATERIAL', "{}_material_id{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_motion_vector_file"])
    s.setPath('MOTION', "{}_motion_vector{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_z_buffer_file"])
    s.setPath('Z', "{}_z_buffer{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_roughness_file"])
    s.setPath('ROUGHNESS', "{}_roughness{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_fresnel_file"])
    s.setPath('FRESNEL', "{}_fresnel{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_normals_file"])
    s.setPath('NORMALS', "{}_normals{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_position_file"])
    s.setPath('POSITION', "{}_position{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_deep_file"])
    s.setPath('DEEP', "{}_deep{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_uv_file"])
    s.setPath('UV', "{}_uv{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_custom_alpha_file"])
    s.setPath('ALPHA_CUSTOM', "{}_custom_alpha{}".format(base_path, e), depth)
    e, depth = get_ext_depth(d["channels_reflectance_file"])
    s.setPath('REFLECTANCE', "{}_reflectance{}".format(base_path, e), depth)
    
    s.setRenderParameter('ENGINE', d["scene_quality"])
    s.setRenderParameter('NUM THREADS', d["scene_cpu_threads"])
    s.setRenderParameter('STOP TIME', d["scene_time"] * 60)
    s.setRenderParameter('SAMPLING LEVEL', d["scene_sampling_level"])
    s.setRenderParameter('USE MULTILIGHT', d["scene_multilight"])
    s.setRenderParameter('SAVE LIGHTS IN SEPARATE FILES', d["scene_multilight_type"])
    
    s.setRenderParameter('MXI FULLNAME', d["output_mxi"])
    s.setRenderParameter('DO NOT SAVE MXI FILE', not d["output_mxi_enabled"])
    s.setRenderParameter('DO NOT SAVE IMAGE FILE', not d["output_image_enabled"])
    # s.setRenderParameter('RENAME AFTER SAVING', d[""])
    # s.setRenderParameter('COPY MXI AFTER RENDER', d["output_mxi"])
    # s.setRenderParameter('COPY IMAGE AFTER RENDER', d["output_image"])
    # s.setRenderParameter('REMOVE FILES AFTER COPY', d[""])
    s.setRenderParameter('DO MOTION BLUR', d["globals_motion_blur"])
    s.setRenderParameter('DO DISPLACEMENT', d["globals_diplacement"])
    s.setRenderParameter('DO DISPERSION', d["globals_dispersion"])
    
    # 'RENDER LAYERS': 0 = RENDER_LAYER_ALL (all layers)
    #                  1 = RENDER_LAYER_DIFFUSE (diffuse)
    #                  2 = RENDER_LAYER_REFLECTIONS (reflections)
    #                  3 = RENDER_LAYER_REFRACTIONS (refractions)
    #                  4 = RENDER_LAYER_DIFFUSE_AND_REFLECTIONS (diffuse and reflections)
    #                  5 = RENDER_LAYER_REFLECTIONS_AND_REFRACTIONS (reflections and refractions)
    s.setRenderParameter('RENDER LAYERS', d['channels_render_type'])
    
    # # 3.1
    # if(d['channels_render_type'] == 2):
    #     s.setRenderParameter('DO DIFFUSE LAYER', 0)
    #     s.setRenderParameter('DO REFLECTION LAYER', 1)
    # elif(d['channels_render_type'] == 1):
    #     s.setRenderParameter('DO DIFFUSE LAYER', 1)
    #     s.setRenderParameter('DO REFLECTION LAYER', 0)
    # else:
    #     s.setRenderParameter('DO DIFFUSE LAYER', 1)
    #     s.setRenderParameter('DO REFLECTION LAYER', 1)
    
    v = d['illum_caustics_illumination']
    if(v == 3):
        s.setRenderParameter('DO DIRECT LAYER', 0)
        s.setRenderParameter('DO INDIRECT LAYER', 0)
    elif(v == 2):
        s.setRenderParameter('DO DIRECT LAYER', 0)
        s.setRenderParameter('DO INDIRECT LAYER', 1)
    elif(v == 1):
        s.setRenderParameter('DO DIRECT LAYER', 1)
        s.setRenderParameter('DO INDIRECT LAYER', 0)
    else:
        s.setRenderParameter('DO DIRECT LAYER', 1)
        s.setRenderParameter('DO INDIRECT LAYER', 1)
    
    v = d['illum_caustics_refl_caustics']
    if(v == 3):
        s.setRenderParameter('DO DIRECT REFLECTION CAUSTIC LAYER', 0)
        s.setRenderParameter('DO INDIRECT REFLECTION CAUSTIC LAYER', 0)
    elif(v == 2):
        s.setRenderParameter('DO DIRECT REFLECTION CAUSTIC LAYER', 0)
        s.setRenderParameter('DO INDIRECT REFLECTION CAUSTIC LAYER', 1)
    elif(v == 1):
        s.setRenderParameter('DO DIRECT REFLECTION CAUSTIC LAYER', 1)
        s.setRenderParameter('DO INDIRECT REFLECTION CAUSTIC LAYER', 0)
    else:
        s.setRenderParameter('DO DIRECT REFLECTION CAUSTIC LAYER', 1)
        s.setRenderParameter('DO INDIRECT REFLECTION CAUSTIC LAYER', 1)
    
    v = d['illum_caustics_refr_caustics']
    if(v == 3):
        s.setRenderParameter('DO DIRECT REFRACTION CAUSTIC LAYER', 0)
        s.setRenderParameter('DO INDIRECT REFRACTION CAUSTIC LAYER', 0)
    elif(v == 2):
        s.setRenderParameter('DO DIRECT REFRACTION CAUSTIC LAYER', 0)
        s.setRenderParameter('DO INDIRECT REFRACTION CAUSTIC LAYER', 1)
    elif(v == 1):
        s.setRenderParameter('DO DIRECT REFRACTION CAUSTIC LAYER', 1)
        s.setRenderParameter('DO INDIRECT REFRACTION CAUSTIC LAYER', 0)
    else:
        s.setRenderParameter('DO DIRECT REFRACTION CAUSTIC LAYER', 1)
        s.setRenderParameter('DO INDIRECT REFRACTION CAUSTIC LAYER', 1)
    
    s.setRenderParameter('DO RENDER CHANNEL', int(d["channels_render"]))
    s.setRenderParameter('DO ALPHA CHANNEL', int(d["channels_alpha"]))
    s.setRenderParameter('OPAQUE ALPHA', int(d["channels_alpha_opaque"]))
    s.setRenderParameter('EMBED CHANNELS', d["channels_output_mode"])
    s.setRenderParameter('DO IDOBJECT CHANNEL', int(d["channels_object_id"]))
    s.setRenderParameter('DO IDMATERIAL CHANNEL', int(d["channels_material_id"]))
    s.setRenderParameter('DO SHADOW PASS CHANNEL', int(d["channels_shadow"]))
    s.setRenderParameter('DO MOTION CHANNEL', int(d["channels_motion_vector"]))
    s.setRenderParameter('DO ROUGHNESS CHANNEL', int(d["channels_roughness"]))
    s.setRenderParameter('DO FRESNEL CHANNEL', int(d["channels_fresnel"]))
    s.setRenderParameter('DO NORMALS CHANNEL', int(d["channels_normals"]))
    s.setRenderParameter('NORMALS CHANNEL SPACE', d["channels_normals_space"])
    s.setRenderParameter('POSITION CHANNEL SPACE', d["channels_position_space"])
    s.setRenderParameter('DO POSITION CHANNEL', int(d["channels_position"]))
    s.setRenderParameter('DO ZBUFFER CHANNEL', int(d["channels_z_buffer"]))
    s.setRenderParameter('ZBUFFER RANGE', (d["channels_z_buffer_near"], d["channels_z_buffer_far"]))
    s.setRenderParameter('DO DEEP CHANNEL', int(d["channels_deep"]))
    s.setRenderParameter('DEEP CHANNEL TYPE', d["channels_deep_type"])
    s.setRenderParameter('DEEP MIN DISTANCE', d["channels_deep_min_dist"])
    s.setRenderParameter('DEEP MAX SAMPLES', d["channels_deep_max_samples"])
    s.setRenderParameter('DO UV CHANNEL', int(d["channels_uv"]))
    # s.setRenderParameter('MOTION CHANNEL TYPE', ?)
    s.setRenderParameter('DO ALPHA CUSTOM CHANNEL', int(d["channels_custom_alpha"]))
    s.setRenderParameter('DO REFLECTANCE CHANNEL', int(d["channels_reflectance"]))
    
    s.setRenderParameter('DO DEVIGNETTING', d["simulens_devignetting"])
    s.setRenderParameter('DEVIGNETTING', d["simulens_devignetting_value"])
    s.setRenderParameter('DO SCATTERING_LENS', d["simulens_scattering"])
    s.setRenderParameter('SCATTERING_LENS', d["simulens_scattering_value"])
    
    s.setRenderParameter('DO SHARPNESS', d["tone_sharpness"])
    s.setRenderParameter('SHARPNESS', d["tone_sharpness_value"])
    s.setToneMapping(d["tone_gamma"], d["tone_burn"])
    
    if(d["materials_override"]):
        s.setOverrideMaterial(True)
    if(d["materials_override_path"] != ""):
        s.setOverrideMaterial(d["materials_override_path"])
    
    if(d["simulens_diffraction"]):
        s.enableDiffraction()
        s.setDiffraction(d["simulens_diffraction_value"], d["simulens_frequency"], d["simulens_aperture_map"], d["simulens_obstacle_map"])
    
    s.setColorSpace(d["tone_color_space"])
    s.setWhitePoint(d["tone_whitepoint"], d["tone_tint"])
    
    if(d["materials_search_path"] != ""):
        s.addSearchingPath(d["materials_search_path"])
    
    if(d["materials_default_material"] != ""):
        s.setDefaultMaterial(True)
        s.setDefaultMaterial(d["materials_default_material"])
    else:
        s.setDefaultMaterial(False)
    
    if(d['export_protect_mxs']):
        s.enableProtection(True)
    else:
        s.enableProtection(False)
    
    if(d['extra_sampling_enabled']):
        s.setRenderParameter('DO EXTRA SAMPLING', 1)
        s.setRenderParameter('EXTRA SAMPLING SL', d['extra_sampling_sl'])
        s.setRenderParameter('EXTRA SAMPLING MASK', d['extra_sampling_mask'])
        s.setRenderParameter('EXTRA SAMPLING CUSTOM ALPHA', d['extra_sampling_custom_alpha'])
        s.setRenderParameter('EXTRA SAMPLING USER BITMAP', d['extra_sampling_user_bitmap'])
        if(d['extra_sampling_invert']):
            s.setRenderParameter('EXTRA SAMPLING INVERT', 1)
    
    if(d['overlay_enabled']):
        o = CoverlayTextOptions()
        o.enabled_ = 1
        o.text_ = Cstring(d['overlay_text'])
        o.position_ = d['overlay_position']
        c = Crgb()
        c.assign(*d['overlay_color'])
        o.color_ = c.toRGB8()
        o.backgroundEnabled_ = d['overlay_background']
        c = Crgb()
        c.assign(*d['overlay_background_color'])
        o.backgroundColor_ = c.toRGB8()
        s.setOverlayTextOptions(o)
    
    if(d['plugin_id'] != ""):
        s.setPluginID(d['plugin_id'])


def environment(d, s, ):
    env = s.getEnvironment()
    if(d["env_type"] == 'PHYSICAL_SKY' or d["env_type"] == 'IMAGE_BASED'):
        env.setActiveSky(d["sky_type"])
        if(d["sky_type"] == 'PHYSICAL'):
            if(not d["sky_use_preset"]):
                env.setPhysicalSkyAtmosphere(d["sky_intensity"], d["sky_ozone"], d["sky_water"], d["sky_turbidity_coeff"], d["sky_wavelength_exp"], d["sky_reflectance"], d["sky_asymmetry"], d["sky_planet_refl"], )
            else:
                env.loadSkyFromPreset(d["sky_preset"])
        
        if(d["sky_type"] == 'CONSTANT'):
            hc = Crgb()
            hc.assign(*d['dome_horizon'])
            zc = Crgb()
            zc.assign(*d['dome_zenith'])
            env.setSkyConstant(d["dome_intensity"], hc, zc, d['dome_mid_point'])
        
        sc = Crgb()
        sc.assign(*d['sun_color'])
        if(d["sun_type"] == 'PHYSICAL'):
            env.setSunProperties(SUN_PHYSICAL, d["sun_temp"], d["sun_power"], d["sun_radius_factor"], sc)
        elif(d["sun_type"] == 'CUSTOM'):
            env.setSunProperties(SUN_CONSTANT, d["sun_temp"], d["sun_power"], d["sun_radius_factor"], sc)
        elif(d["sun_type"] == 'DISABLED'):
            env.setSunProperties(SUN_DISABLED, d["sun_temp"], d["sun_power"], d["sun_radius_factor"], sc)
        if(d["sun_location_type"] == 'LATLONG'):
            env.setSunPositionType(0)
            l = d["sun_date"].split(".")
            date = datetime.date(int(l[2]), int(l[1]), int(l[0]))
            day = int(date.timetuple().tm_yday)
            l = d["sun_time"].split(":")
            hour = int(l[0])
            minute = int(l[1])
            time = hour + (minute / 60)
            env.setSunLongitudeAndLatitude(d["sun_latlong_lon"], d["sun_latlong_lat"], d["sun_latlong_gmt"], day, time)
            env.setSunRotation(d["sun_latlong_ground_rotation"])
        elif(d["sun_location_type"] == 'ANGLES'):
            env.setSunPositionType(1)
            env.setSunAngles(d["sun_angles_zenith"], d["sun_angles_azimuth"])
        elif(d["sun_location_type"] == 'DIRECTION'):
            env.setSunPositionType(2)
            env.setSunDirection(Cvector(d["sun_dir_x"], d["sun_dir_y"], d["sun_dir_z"]))
        
        if(d["env_type"] == 'IMAGE_BASED'):
            env.enableEnvironment(True)
        
        def state(s):
            # channel state: 0 = Disabled;  1 = Enabled; 2 = Use active sky instead.
            if(s == 'HDR_IMAGE'):
                return 1
            if(s == 'ACTIVE_SKY'):
                return 2
            if(s == 'SAME_AS_BG'):
                # same as bg, set the same values as in bg layer
                return 3
            return 0
        
        env.setEnvironmentWeight(d["ibl_intensity"])
        s = state(d["ibl_bg_type"])
        env.setEnvironmentLayer(IBL_LAYER_BACKGROUND, d["ibl_bg_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_bg_intensity"], d["ibl_bg_scale_x"], d["ibl_bg_scale_y"], d["ibl_bg_offset_x"], d["ibl_bg_offset_y"], )
        s = state(d["ibl_refl_type"])
        if(s == 3):
            s = state(d["ibl_bg_type"])
            env.setEnvironmentLayer(IBL_LAYER_REFLECTION, d["ibl_bg_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_bg_intensity"], d["ibl_bg_scale_x"], d["ibl_bg_scale_y"], d["ibl_bg_offset_x"], d["ibl_bg_offset_y"], )
        else:
            env.setEnvironmentLayer(IBL_LAYER_REFLECTION, d["ibl_refl_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_refl_intensity"], d["ibl_refl_scale_x"], d["ibl_refl_scale_y"], d["ibl_refl_offset_x"], d["ibl_refl_offset_y"], )
        s = state(d["ibl_refr_type"])
        if(s == 3):
            s = state(d["ibl_bg_type"])
            env.setEnvironmentLayer(IBL_LAYER_REFRACTION, d["ibl_bg_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_bg_intensity"], d["ibl_bg_scale_x"], d["ibl_bg_scale_y"], d["ibl_bg_offset_x"], d["ibl_bg_offset_y"], )
        else:
            env.setEnvironmentLayer(IBL_LAYER_REFRACTION, d["ibl_refr_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_refr_intensity"], d["ibl_refr_scale_x"], d["ibl_refr_scale_y"], d["ibl_refr_offset_x"], d["ibl_refr_offset_y"], )
        s = state(d["ibl_illum_type"])
        if(s == 3):
            s = state(d["ibl_bg_type"])
            env.setEnvironmentLayer(IBL_LAYER_ILLUMINATION, d["ibl_bg_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_bg_intensity"], d["ibl_bg_scale_x"], d["ibl_bg_scale_y"], d["ibl_bg_offset_x"], d["ibl_bg_offset_y"], )
        else:
            env.setEnvironmentLayer(IBL_LAYER_ILLUMINATION, d["ibl_illum_map"], s, not d["ibl_screen_mapping"], not d["ibl_interpolation"], d["ibl_illum_intensity"], d["ibl_illum_scale_x"], d["ibl_illum_scale_y"], d["ibl_illum_offset_x"], d["ibl_illum_offset_y"], )
    else:
        env.setActiveSky('')


def custom_alphas(d, s, ):
    def get_material_names(s):
        it = CmaxwellMaterialIterator()
        o = it.first(s)
        l = []
        while not o.isNull():
            name = o.getName()
            l.append(name)
            o = it.next()
        return l
    
    def get_object_names(s):
        it = CmaxwellObjectIterator()
        o = it.first(s)
        l = []
        while not o.isNull():
            name, _ = o.getName()
            l.append(name)
            o = it.next()
        return l
    
    sobs = get_object_names(s)
    smats = get_material_names(s)
    
    ags = d['channels_custom_alpha_groups']
    for a in ags:
        s.createCustomAlphaChannel(a['name'], a['opaque'])
        for n in a['objects']:
            if(n in sobs):
                o = s.getObject(n)
                o.addToCustomAlpha(a['name'])
        for n in a['materials']:
            if(n in smats):
                m = s.getMaterial(n)
                m.addToCustomAlpha(a['name'])


def particles(d, s, ):
    mgr = CextensionManager.instance()
    ext = mgr.createDefaultGeometryProceduralExtension('MaxwellParticles')
    params = ext.getExtensionData()
    
    if(d['embed'] is True):
        bpp = d['pdata']
        r = MXSBinParticlesReader(bpp)
        
        c = Cbase()
        c.origin = Cvector(0.0, 0.0, 0.0)
        c.xAxis = Cvector(1.0, 0.0, 0.0)
        c.yAxis = Cvector(0.0, 1.0, 0.0)
        c.zAxis = Cvector(0.0, 0.0, 1.0)
        
        params.setFloatArray('PARTICLE_POSITIONS', list(r.PARTICLE_POSITIONS), c)
        params.setFloatArray('PARTICLE_SPEEDS', list(r.PARTICLE_SPEEDS), c)
        params.setFloatArray('PARTICLE_RADII', list(r.PARTICLE_RADII), c)
        params.setIntArray('PARTICLE_IDS', list(r.PARTICLE_IDS))
        params.setFloatArray('PARTICLE_NORMALS', list(r.PARTICLE_NORMALS), c)
        params.setFloatArray('PARTICLE_UVW', list(r.PARTICLE_UVW), c)
        
    else:
        params.setString('FileName', d['bin_filename'])
    
    params.setFloat('Radius Factor', d['bin_radius_multiplier'])
    params.setFloat('MB Factor', d['bin_motion_blur_multiplier'])
    params.setFloat('Shutter 1/', d['bin_shutter_speed'])
    params.setFloat('Load particles %', d['bin_load_particles'])
    params.setUInt('Axis', d['bin_axis_system'])
    params.setInt('Frame#', d['bin_frame_number'])
    params.setFloat('fps', d['bin_fps'])
    params.setUInt('Create N particles per particle', d['bin_extra_create_np_pp'])
    params.setFloat('Extra particles dispersion', d['bin_extra_dispersion'])
    params.setFloat('Extra particles deformation', d['bin_extra_deformation'])
    params.setByte('Load particle Force', d['bin_load_force'])
    params.setByte('Load particle Vorticity', d['bin_load_vorticity'])
    params.setByte('Load particle Normal', d['bin_load_normal'])
    params.setByte('Load particle neighbors no.', d['bin_load_neighbors_num'])
    params.setByte('Load particle UV', d['bin_load_uv'])
    params.setByte('Load particle Age', d['bin_load_age'])
    params.setByte('Load particle Isolation Time', d['bin_load_isolation_time'])
    params.setByte('Load particle Viscosity', d['bin_load_viscosity'])
    params.setByte('Load particle Density', d['bin_load_density'])
    params.setByte('Load particle Pressure', d['bin_load_pressure'])
    params.setByte('Load particle Mass', d['bin_load_mass'])
    params.setByte('Load particle Temperature', d['bin_load_temperature'])
    params.setByte('Load particle ID', d['bin_load_id'])
    params.setFloat('Min Force', d['bin_min_force'])
    params.setFloat('Max Force', d['bin_max_force'])
    params.setFloat('Min Vorticity', d['bin_min_vorticity'])
    params.setFloat('Max Vorticity', d['bin_max_vorticity'])
    params.setUInt('Min Nneighbors', d['bin_min_nneighbors'])
    params.setUInt('Max Nneighbors', d['bin_max_nneighbors'])
    params.setFloat('Min Age', d['bin_min_age'])
    params.setFloat('Max Age', d['bin_max_age'])
    params.setFloat('Min Isolation Time', d['bin_min_isolation_time'])
    params.setFloat('Max Isolation Time', d['bin_max_isolation_time'])
    params.setFloat('Min Viscosity', d['bin_min_viscosity'])
    params.setFloat('Max Viscosity', d['bin_max_viscosity'])
    params.setFloat('Min Density', d['bin_min_density'])
    params.setFloat('Max Density', d['bin_max_density'])
    params.setFloat('Min Pressure', d['bin_min_pressure'])
    params.setFloat('Max Pressure', d['bin_max_pressure'])
    params.setFloat('Min Mass', d['bin_min_mass'])
    params.setFloat('Max Mass', d['bin_max_mass'])
    params.setFloat('Min Temperature', d['bin_min_temperature'])
    params.setFloat('Max Temperature', d['bin_max_temperature'])
    params.setFloat('Min Velocity', d['bin_min_velocity'])
    params.setFloat('Max Velocity', d['bin_max_velocity'])
    
    o = s.createGeometryProceduralObject(d['name'], params)
    
    a, _ = o.addChannelUVW()
    o.generateCustomUVW(0, a)
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        o.setMaterial(mat)
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)


def cloner(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryModifierExtension('MaxwellCloner')
    p = e.getExtensionData()
    
    if(d['embed'] is True):
        bpp = d['pdata']
        
        r = MXSBinParticlesReader(bpp)
        
        c = Cbase()
        c.origin = Cvector(0.0, 0.0, 0.0)
        c.xAxis = Cvector(1.0, 0.0, 0.0)
        c.yAxis = Cvector(0.0, 1.0, 0.0)
        c.zAxis = Cvector(0.0, 0.0, 1.0)
        
        p.setFloatArray('PARTICLE_POSITIONS', list(r.PARTICLE_POSITIONS), c)
        p.setFloatArray('PARTICLE_SPEEDS', list(r.PARTICLE_SPEEDS), c)
        p.setFloatArray('PARTICLE_RADII', list(r.PARTICLE_RADII), c)
        p.setIntArray('PARTICLE_IDS', list(r.PARTICLE_IDS))
        
    else:
        p.setString('FileName', d['filename'])
    
    p.setFloat('Radius Factor', d['radius'])
    p.setFloat('MB Factor', d['mb_factor'])
    p.setFloat('Load particles %', d['load_percent'])
    p.setUInt('Start offset', d['start_offset'])
    p.setUInt('Create N particles per particle', d['extra_npp'])
    p.setFloat('Extra particles dispersion', d['extra_p_dispersion'])
    p.setFloat('Extra particles deformation', d['extra_p_deformation'])
    
    p.setByte('Use velocity', d['align_to_velocity'])
    p.setByte('Scale with particle radius', d['scale_with_radius'])
    p.setByte('Inherit ObjectID', d['inherit_obj_id'])
    
    p.setInt('Frame#', d['frame'])
    p.setFloat('fps', d['fps'])
    
    p.setUInt('Display Percent', d['display_percent'])
    p.setUInt('Display Max. Particles', d['display_max'])
    
    if(not d['render_emitter']):
        o = s.getObject(d['parent'])
        o.setHide(True)
    
    o = s.getObject(d['cloned_object'])
    o.applyGeometryModifierExtension(p)


def hair(d, s, ):
    m = CextensionManager.instance()
    if(d['extension'] == 'MaxwellHair'):
        e = m.createDefaultGeometryProceduralExtension('MaxwellHair')
    if(d['extension'] == 'MGrassP'):
        e = m.createDefaultGeometryProceduralExtension('MGrassP')
    
    p = e.getExtensionData()
    p.setByteArray('HAIR_MAJOR_VER', d['data']['HAIR_MAJOR_VER'])
    p.setByteArray('HAIR_MINOR_VER', d['data']['HAIR_MINOR_VER'])
    p.setByteArray('HAIR_FLAG_ROOT_UVS', d['data']['HAIR_FLAG_ROOT_UVS'])
    
    m = memoryview(struct.pack("I", d['data']['HAIR_GUIDES_COUNT'][0])).tolist()
    p.setByteArray('HAIR_GUIDES_COUNT', m)
    
    m = memoryview(struct.pack("I", d['data']['HAIR_GUIDES_POINT_COUNT'][0])).tolist()
    p.setByteArray('HAIR_GUIDES_POINT_COUNT', m)
    
    c = Cbase()
    c.origin = Cvector(0.0, 0.0, 0.0)
    c.xAxis = Cvector(1.0, 0.0, 0.0)
    c.yAxis = Cvector(0.0, 1.0, 0.0)
    c.zAxis = Cvector(0.0, 0.0, 1.0)
    
    bhp = d['hair_data_path']
    r = MXSBinHairReader(bhp)
    p.setFloatArray('HAIR_POINTS', list(r.data), c)
    
    p.setFloatArray('HAIR_NORMALS', d['data']['HAIR_NORMALS'], c)
    
    if(d['data']['HAIR_FLAG_ROOT_UVS'][0] == 1):
        p.setFloatArray('HAIR_ROOT_UVS', list(d['data']['HAIR_ROOT_UVS']), c)
    
    p.setUInt('Display Percent', d['display_percent'])
    if(d['extension'] == 'MaxwellHair'):
        p.setUInt('Display Max. Hairs', d['display_max_hairs'])
        p.setDouble('Root Radius', d['hair_root_radius'])
        p.setDouble('Tip Radius', d['hair_tip_radius'])
    if(d['extension'] == 'MGrassP'):
        p.setUInt('Display Max. Hairs', d['display_max_blades'])
        p.setDouble('Root Radius', d['grass_root_width'])
        p.setDouble('Tip Radius', d['grass_tip_width'])
    
    o = s.createGeometryProceduralObject(d['name'], p)
    
    if(d['extension'] == 'MaxwellHair'):
        a, _ = o.addChannelUVW()
        o.generateCustomUVW(0, a)
        b, _ = o.addChannelUVW()
        o.generateCustomUVW(1, b)
        c, _ = o.addChannelUVW()
        o.generateCustomUVW(2, c)
    if(d['extension'] == 'MGrassP'):
        a, _ = o.addChannelUVW()
        o.generateCustomUVW(0, a)
        b, _ = o.addChannelUVW()
        o.generateCustomUVW(1, b)
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        o.setMaterial(mat)
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)


def reference(d, s, ):
    o = s.createMesh(d['name'], 0, 0, 0, 0,)
    base_and_pivot(o, d)
    object_props(o, d)
    o.setReferencedScenePath(d['path'])
    if(d['flag_override_hide']):
        o.setReferencedOverrideFlags(FLAG_OVERRIDE_HIDE)
    if(d['flag_override_hide_to_camera']):
        o.setReferencedOverrideFlags(FLAG_OVERRIDE_HIDE_TO_CAMERA)
    if(d['flag_override_hide_to_refl_refr']):
        o.setReferencedOverrideFlags(FLAG_OVERRIDE_HIDE_TO_REFL_REFR)
    if(d['flag_override_hide_to_gi']):
        o.setReferencedOverrideFlags(FLAG_OVERRIDE_HIDE_TO_GI)
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        o.setMaterial(mat)
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    return o


def volumetrics(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryProceduralExtension('MaxwellVolumetric')
    p = e.getExtensionData()
    
    p.setByte('Create Constant Density', d['vtype'])
    p.setFloat('ConstantDensity', d['density'])
    p.setUInt('Seed', d['noise_seed'])
    p.setFloat('Low value', d['noise_low'])
    p.setFloat('High value', d['noise_high'])
    p.setFloat('Detail', d['noise_detail'])
    p.setInt('Octaves', d['noise_octaves'])
    p.setFloat('Persistance', d['noise_persistence'])
    
    o = s.createGeometryProceduralObject(d['name'], p)
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        o.setMaterial(mat)
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)
    return o


def subdivision(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryModifierExtension('SubdivisionModifier')
    p = e.getExtensionData()
    
    o = s.getObject(d['object'])
    
    p.setUInt('Subdivision Level', d['level'])
    p.setUInt('Subdivision Scheme', d['scheme'])
    
    if(d['scheme'] == 0 and d['quad_pairs'] is not None):
        for t, q in d['quad_pairs']:
            o.setTriangleQuadBuddy(t, q)
    
    p.setUInt('Interpolation', d['interpolation'])
    p.setFloat('Crease', d['crease'])
    p.setFloat('Smooth Angle', d['smooth'])
    o.applyGeometryModifierExtension(p)


def scatter(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryModifierExtension('MaxwellScatter')
    p = e.getExtensionData()
    
    o = s.getObject(d['object'])
    e = d
    
    p.setString('Object', e['scatter_object'])
    p.setByte('Inherit ObjectID', e['inherit_objectid'])
    p.setFloat('Density', e['density'])
    texture_data_to_mxparams(e['density_map'], p, 'Density Map', )
    p.setUInt('Seed', e['seed'])
    p.setFloat('Scale X', e['scale_x'])
    p.setFloat('Scale Y', e['scale_y'])
    p.setFloat('Scale Z', e['scale_z'])
    texture_data_to_mxparams(e['scale_map'], p, 'Scale Map', )
    p.setFloat('Scale X Variation', e['scale_variation_x'])
    p.setFloat('Scale Y Variation', e['scale_variation_y'])
    p.setFloat('Scale Z Variation', e['scale_variation_z'])
    p.setFloat('Rotation X', e['rotation_x'])
    p.setFloat('Rotation Y', e['rotation_y'])
    p.setFloat('Rotation Z', e['rotation_z'])
    texture_data_to_mxparams(e['rotation_map'], p, 'Rotation Map', )
    p.setFloat('Rotation X Variation', e['rotation_variation_x'])
    p.setFloat('Rotation Y Variation', e['rotation_variation_y'])
    p.setFloat('Rotation Z Variation', e['rotation_variation_z'])
    p.setUInt('Direction Type', e['rotation_direction'])
    p.setByte('Enable LOD', e['lod'])
    p.setFloat('LOD Min Distance', e['lod_min_distance'])
    p.setFloat('LOD Max Distance', e['lod_max_distance'])
    p.setFloat('LOD Max Distance Density', e['lod_max_distance_density'])
    p.setUInt('Display Percent', e['display_percent'])
    p.setUInt('Display Max. Blades', e['display_max_blades'])
    
    p.setByte('Remove Overlapped', e['remove_overlapped'])
    p.setFloat('Direction Type', e['direction_type'])
    p.setFloat('Initial Angle', e['initial_angle'])
    p.setFloat('Initial Angle Variation', e['initial_angle_variation'])
    texture_data_to_mxparams(e['initial_angle_map'], p, 'Initial Angle Map', )
    p.setByte('Uniform Scale', e['scale_uniform'])
    
    o.applyGeometryModifierExtension(p)


def grass(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryModifierExtension('MaxwellGrass')
    p = e.getExtensionData()
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        p.setString('Material', mat.getName())
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        p.setString('Double Sided Material', mat.getName())
    
    p.setUInt('Density', d['density'])
    texture_data_to_mxparams(d['density_map'], p, 'Density Map')
    
    p.setFloat('Length', d['length'])
    texture_data_to_mxparams(d['length_map'], p, 'Length Map')
    p.setFloat('Length Variation', d['length_variation'])
    
    p.setFloat('Root Width', d['root_width'])
    p.setFloat('Tip Width', d['tip_width'])
    
    p.setFloat('Direction Type', d['direction_type'])
    
    p.setFloat('Initial Angle', d['initial_angle'])
    p.setFloat('Initial Angle Variation', d['initial_angle_variation'])
    texture_data_to_mxparams(d['initial_angle_map'], p, 'Initial Angle Map')
    
    p.setFloat('Start Bend', d['start_bend'])
    p.setFloat('Start Bend Variation', d['start_bend_variation'])
    texture_data_to_mxparams(d['start_bend_map'], p, 'Start Bend Map')
    
    p.setFloat('Bend Radius', d['bend_radius'])
    p.setFloat('Bend Radius Variation', d['bend_radius_variation'])
    texture_data_to_mxparams(d['bend_radius_map'], p, 'Bend Radius Map')
    
    p.setFloat('Bend Angle', d['bend_angle'])
    p.setFloat('Bend Angle Variation', d['bend_angle_variation'])
    texture_data_to_mxparams(d['bend_angle_map'], p, 'Bend Angle Map')
    
    p.setFloat('Cut Off', d['cut_off'])
    p.setFloat('Cut Off Variation', d['cut_off_variation'])
    texture_data_to_mxparams(d['cut_off_map'], p, 'Cut Off Map')
    
    p.setUInt('Points per Blade', d['points_per_blade'])
    p.setUInt('Primitive Type', d['primitive_type'])
    
    p.setUInt('Seed', d['seed'])
    
    p.setByte('Enable LOD', d['lod'])
    p.setFloat('LOD Min Distance', d['lod_min_distance'])
    p.setFloat('LOD Max Distance', d['lod_max_distance'])
    p.setFloat('LOD Max Distance Density', d['lod_max_distance_density'])
    
    p.setUInt('Display Percent', d['display_percent'])
    p.setUInt('Display Max. Blades', d['display_max_blades'])
    
    o = s.getObject(d['object'])
    o.applyGeometryModifierExtension(p)


def sea(d, s, ):
    m = CextensionManager.instance()
    e = m.createDefaultGeometryLoaderExtension('MaxwellSea')
    
    p = e.getExtensionData()
    p.setUInt('Resolution', d['resolution'])
    p.setFloat('Reference Time', d['reference_time'])
    p.setFloat('Ocean Wind Mod.', d['ocean_wind_mod'])
    p.setFloat('Ocean Wind Dir.', d['ocean_wind_dir'])
    p.setFloat('Vertical Scale', d['vertical_scale'])
    p.setFloat('Damp Factor Against Wind', d['damp_factor_against_wind'])
    p.setFloat('Ocean Wind Alignment', d['ocean_wind_alignment'])
    p.setFloat('Ocean Min. Wave Length', d['ocean_min_wave_length'])
    p.setFloat('Ocean Dim', d['ocean_dim'])
    p.setFloat('Ocean Depth', d['ocean_depth'])
    p.setInt('Ocean Seed', d['ocean_seed'])
    p.setByte('Enable Choppyness', d['enable_choppyness'])
    p.setFloat('Choppy factor', d['choppy_factor'])
    p.setByte('Enable White Caps', d['enable_white_caps'])
    
    o = s.createGeometryLoaderObject(d['name'], p)
    
    if(d['material'] != ''):
        mat = get_material(d['material'], s, )
        o.setMaterial(mat)
    if(d['backface_material'] != ''):
        mat = get_material(d['backface_material'], s, )
        o.setBackfaceMaterial(mat)
    
    base_and_pivot(o, d)
    object_props(o, d)


def hierarchy(d, s, ):
    log("setting object hierarchy..", 2)
    a = ['CAMERA', 'EMPTY', 'MESH', 'MESH_INSTANCE', 'SCENE', 'ENVIRONMENT', 'PARTICLES', 'HAIR',
         'REFERENCE', 'VOLUMETRICS', 'SUBDIVISION', 'SCATTER', 'GRASS', 'CLONER', 'SEA', ]
    
    object_types = ['EMPTY', 'MESH', 'MESH_INSTANCE', 'PARTICLES', 'HAIR', 'REFERENCE', 'VOLUMETRICS', 'SEA', 'WIREFRAME_CONTAINER', 'WIREFRAME_BASE', ]
    for i in range(len(d)):
        if(d[i]['type'] in object_types):
            if(d[i]['parent'] is not None):
                ch = s.getObject(d[i]['name'])
                p = s.getObject(d[i]['parent'])
                ch.setParent(p)


def wireframe(d, s, ):
    r = []
    bo = s.getObject(d['instanced'])
    
    wr = MXSBinWireReader(d['wire_matrices'])
    wire_matrices = wr.data
    
    for i, m in enumerate(wire_matrices):
        o = s.createInstancement("{0}-{1}".format(d['name'], i), bo)
        bp = {'base': m[0],
              'pivot': m[1],
              'location': m[2],
              'rotation': m[3],
              'scale': m[4],
              # NOTE: wireframe quick fix, no real motion blur for wireframe..
              'motion_blur': [], }
        base_and_pivot(o, bp)
        object_props(o, d)
        r.append(o)
    return r


def texture_data_to_mxparams(d, mp, name, ):
    if(d is None):
        return
    
    t = CtextureMap()
    t.setPath(d['path'])
    v = Cvector2D()
    v.assign(*d['repeat'])
    t.scale = v
    v = Cvector2D()
    v.assign(*d['offset'])
    t.offset = v
    t.rotation = d['rotation']
    t.uvwChannelID = d['channel']
    t.uIsTiled = d['tile_method_type'][0]
    t.vIsTiled = d['tile_method_type'][1]
    t.uIsMirrored = d['mirror'][0]
    t.vIsMirrored = d['mirror'][1]
    t.invert = d['invert']
    # t.doGammaCorrection = 0
    t.useAbsoluteUnits = d['tile_method_units']
    
    t.normalMappingFlipRed = d['normal_mapping_flip_red']
    t.normalMappingFlipGreen = d['normal_mapping_flip_green']
    t.normalMappingFullRangeBlue = d['normal_mapping_full_range_blue']
    
    t.useAlpha = d['alpha_only']
    t.typeInterpolation = d['interpolation']
    
    t.brightness = d['brightness'] / 100
    t.contrast = d['contrast'] / 100
    t.hue = d['hue'] / 180
    t.saturation = d['saturation'] / 100
    
    t.clampMin = d['rgb_clamp'][0] / 255
    t.clampMax = d['rgb_clamp'][1] / 255
    
    t.useGlobalMap = d['use_global_map']
    # t.cosA = 1.000000
    # t.sinA = 0.000000
    ok = mp.setTextureMap(name, t)
    
    return mp


def main(args):
    log("loading data..", 2)
    with open(args.scene_data_path, 'r') as f:
        data = json.load(f)
    # create scene
    mxs = Cmaxwell(mwcallback)
    if(args.append is True):
        log("appending to existing scene..", 2)
        mxs.readMXS(args.result_path)
    else:
        log("creating new scene..", 2)
    # instance manager
    mgr = CextensionManager.instance()
    mgr.loadAllExtensions()
    # loop over scene data and create things by type
    
    use_wireframe = args.wireframe
    all_wire_instances = []
    wire_container = None
    wire_base = None
    
    log("creating objects:", 2)
    progress = PercentDone(len(data), indent=3, )
    for d in data:
        if(d['type'] == 'CAMERA'):
            camera(d, mxs)
        elif(d['type'] == 'EMPTY'):
            empty(d, mxs)
        elif(d['type'] == 'MESH'):
            mesh(d, mxs)
        elif(d['type'] == 'MESH_INSTANCE'):
            try:
                if(d['base']):
                    mesh(d, mxs)
            except KeyError:
                instance(d, mxs)
        elif(d['type'] == 'SCENE'):
            scene(d, mxs)
            custom_alphas(d, mxs)
        elif(d['type'] == 'ENVIRONMENT'):
            environment(d, mxs)
        elif(d['type'] == 'PARTICLES'):
            particles(d, mxs)
        elif(d['type'] == 'HAIR'):
            hair(d, mxs)
        elif(d['type'] == 'REFERENCE'):
            reference(d, mxs)
        elif(d['type'] == 'VOLUMETRICS'):
            volumetrics(d, mxs)
        elif(d['type'] == 'SUBDIVISION'):
            subdivision(d, mxs)
        elif(d['type'] == 'SCATTER'):
            scatter(d, mxs)
        elif(d['type'] == 'GRASS'):
            grass(d, mxs)
        elif(d['type'] == 'CLONER'):
            cloner(d, mxs)
        elif(d['type'] == 'SEA'):
            sea(d, mxs)
        elif(d['type'] == 'MATERIAL'):
            material(d, mxs)
        elif(d['type'] == 'WIREFRAME_CONTAINER'):
            wire_container = empty(d, mxs)
        elif(d['type'] == 'WIREFRAME_BASE'):
            wire_base = mesh(d, mxs)
        elif(d['type'] == 'WIREFRAME_INSTANCES'):
            wos = wireframe(d, mxs, )
            all_wire_instances.extend(wos)
        
        else:
            raise TypeError("{0} is unknown type".format(d['type']))
        progress.step()
    #
    hierarchy(data, mxs)
    
    if(use_wireframe):
        for wi in all_wire_instances:
            wi.setParent(wire_container)
        
        # zero scale wire_base to be practically invisible
        z = (0.0, 0.0, 0.0)
        b = Cbase()
        b.origin = Cvector(*z)
        b.xAxis = Cvector(*z)
        b.yAxis = Cvector(*z)
        b.zAxis = Cvector(*z)
        p = Cbase()
        p.origin = Cvector(*z)
        p.xAxis = Cvector(1.0, 0.0, 0.0)
        p.yAxis = Cvector(0.0, 1.0, 0.0)
        p.zAxis = Cvector(0.0, 0.0, 1.0)
        wire_base.setBaseAndPivot(b, p)
        wire_base.setScale(Cvector(0, 0, 0))
        
        # export_use_wireframe
        export_clay_override_object_material = False
        export_wire_wire_material = None
        export_wire_clay_material = None
        
        for d in data:
            if(d['type'] == 'SCENE'):
                export_clay_override_object_material = d['export_clay_override_object_material']
                export_wire_wire_material = d['export_wire_wire_material']
                export_wire_clay_material = d['export_wire_clay_material']
                break
        
        if(export_wire_clay_material is not None):
            wire = get_material(export_wire_wire_material, mxs, )
            for d in data:
                if(d['type'] == 'WIREFRAME_BASE'):
                    o = mxs.getObject(d['name'])
                    o.setMaterial(wire)
                    break
            for wi in all_wire_instances:
                wi.setMaterial(wire)
        
        if(export_wire_clay_material is not None and export_clay_override_object_material):
            clay = get_material(export_wire_clay_material, mxs, )
            clayable = ['MESH', 'MESH_INSTANCE', 'PARTICLES', 'HAIR', 'REFERENCE', 'VOLUMETRICS', 'SEA', ]
            for d in data:
                if(d['type'] in clayable):
                    o = mxs.getObject(d['name'])
                    o.setMaterial(clay)
    
    # set active camera, again.. for some reason it gets reset
    for d in data:
        if(d['type'] == 'CAMERA'):
            if(d['active']):
                c = mxs.getCamera(d['name'])
                c.setActive()
    # remove unused materials
    # FIXMENOT: disabled because it removes also backface materials if they are not used somewhere else as normal materials
    # mxs.eraseUnusedMaterials()
    for d in data:
        if(d['type'] == 'SCENE'):
            if(d['export_remove_unused_materials']):
                # optional, might also remove materials not supposed to be removed
                log("removing unused materials..", 2)
                mxs.eraseUnusedMaterials()
    # save mxs
    log("saving scene..", 2)
    ok = mxs.writeMXS(args.result_path)
    log("done.", 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''Make Maxwell scene from serialized data'''), epilog='',
                                     formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True, )
    parser.add_argument('-a', '--append', action='store_true', help='append to existing mxs (result_path)')
    parser.add_argument('-w', '--wireframe', action='store_true', help='scene data contains wireframe scene')
    # parser.add_argument('-i', '--instancer', action='store_true', help='scene data contains instancer (python only)')
    parser.add_argument('-q', '--quiet', action='store_true', help='no logging except errors')
    parser.add_argument('pymaxwell_path', type=str, help='path to directory containing pymaxwell')
    parser.add_argument('log_file', type=str, help='path to log file')
    parser.add_argument('scene_data_path', type=str, help='path to serialized scene data file')
    parser.add_argument('result_path', type=str, help='path to result .mxs')
    args = parser.parse_args()
    
    quiet = args.quiet
    
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
        
        # import cProfile, pstats, io
        # pr = cProfile.Profile()
        # pr.enable()
        
        main(args)
        
        # pr.disable()
        # s = io.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print(s.getvalue())
        
    except Exception as e:
        import traceback
        m = traceback.format_exc()
        log(m)
        
        sys.exit(1)
    sys.exit(0)
