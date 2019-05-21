# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, neo2068
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
# System Libs
from __future__ import division
from ctypes import cdll, c_uint, c_float, cast, POINTER, byref, sizeof
import os, struct, sys

# Blender Libs
import bpy
from ..extensions_framework import util as efutil

# LuxRender libs
from . import ParamSet, matrix_to_list, LuxManager
from ..outputs import LuxLog
from ..outputs.file_api import Files


class library_loader():
    load_lzo_attempted = False
    load_lzma_attempted = False

    # imported compression libraries
    has_lzo = False
    lzodll = None

    has_lzma = False
    lzmadll = None

    ver_str = '%d.%d' % bpy.app.version[0:2]

    platform_search = {
        'lzo': {
            'darwin': [
                bpy.utils.user_resource('SCRIPTS', 'addons/luxrender/liblzo2.2.dylib'),
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzo2.2.dylib'
            ],
            'win32': [
                'lzo.dll',
                bpy.utils.user_resource('SCRIPTS', 'addons/luxrender/lzo.dll'),
                bpy.app.binary_path[:-11] + ver_str + '/scripts/addons/luxrender/lzo.dll'
            ],
            'linux': [
                '/usr/lib/liblzo2.so',
                '/usr/lib/liblzo2.so.2',
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzo2.so'
            ],
            'linux2': [
                '/usr/lib/liblzo2.so',
                '/usr/lib/liblzo2.so.2',
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzo2.so'
            ]
        },
        'lzma': {
            'darwin': [
                bpy.utils.user_resource('SCRIPTS', 'addons/luxrender/liblzmadec.dylib'),
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzmadec.dylib'
            ],
            'win32': [
                'lzma.dll',
                bpy.utils.user_resource('SCRIPTS', 'addons/luxrender/lzma.dll'),
                bpy.app.binary_path[:-11] + ver_str + '/scripts/addons/luxrender/lzma.dll'
            ],
            'linux': [
                '/usr/lib/liblzma.so',
                '/usr/lib/liblzma.so.2',
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzma.so'
            ],
            'linux2': [
                '/usr/lib/liblzma.so',
                '/usr/lib/liblzma.so.2',
                bpy.app.binary_path[:-7] + ver_str + '/scripts/addons/luxrender/liblzma.so'
            ]
        }
    }

    @classmethod
    def load_lzo(cls):
        # Only attempt load once per session
        if not cls.load_lzo_attempted:

            for sp in cls.platform_search['lzo'][sys.platform]:
                try:
                    cls.lzodll = cdll.LoadLibrary(sp)
                    cls.has_lzo = True
                    break
                except Exception:
                    continue

            if cls.has_lzo:
                LuxLog('Volumes: LZO Library found')
            else:
                LuxLog('Volumes: LZO Library not found')

            cls.load_lzo_attempted = True

        return cls.has_lzo, cls.lzodll

    @classmethod
    def load_lzma(cls):
        # Only attempt load once per session
        if not cls.load_lzma_attempted:

            for sp in cls.platform_search['lzma'][sys.platform]:
                try:
                    cls.lzmadll = cdll.LoadLibrary(sp)
                    cls.has_lzma = True
                    break
                except Exception:
                    continue

            if cls.has_lzma:
                LuxLog('Volumes: LZMA Library found')
            else:
                LuxLog('Volumes: LZMA Library not found')

            cls.load_lzma_attempted = True

        return cls.has_lzma, cls.lzmadll


def read_cache(smokecache, is_high_res, amplifier, flowtype):
    scene = LuxManager.CurrentScene

    # NOTE - dynamic libraries are not loaded until needed, further down
    # the script...

    # ##################################################################################################
    # Read cache
    # Pointcache file format v1.04:
    # name								   size of uncompressed data
    #--------------------------------------------------------------------------------------------------
    #	header								( 20 Bytes)
    #	data_segment for shadow values		( cell_count * sizeof(float) Bytes)
    #	data_segment for density values		( cell_count * sizeof(float) Bytes)
    #	data_segment for heat values		( cell_count * sizeof(float) Bytes)
    #	data_segment for heat, old values	( cell_count * sizeof(float) Bytes)
    #	data_segment for vx values		( cell_count * sizeof(float) Bytes)
    #	data_segment for vy values		( cell_count * sizeof(float) Bytes)
    #	data_segment for vz values		( cell_count * sizeof(float) Bytes)
    #	data_segment for obstacles values	( cell_count * sizeof(char) Bytes)
    # if simulation is high resolution additionally:
    #	data_segment for density values		( big_cell_count * sizeof(float) Bytes)
    #	data_segment for tcu values		( cell_count * sizeof(u_int) Bytes)
    #	data_segment for tcv values		( cell_count * sizeof(u_int) Bytes)
    #	data_segment for tcw values		( cell_count * sizeof(u_int) Bytes)
    #
    # header format:
    #	BPHYSICS		(Tag-String, 8 Bytes)
    #	data type		(u_int, 4 Bytes)		=> 3 - PTCACHE_TYPE_SMOKE_DOMAIN
    #	cell count		(u_int, 4 Bytes)		Resolution of the smoke simulation
    #	user data type	(u_int int, 4 Bytes)                    not used by smoke simulation
    #
    # data segment format:
    #	compressed flag	(u_char, 1 Byte)			=> 0 - uncompressed data,
    #								   1 - LZO compressed data,
    #								   2 - LZMA compressed data
    #	stream size		(u_int, 4 Bytes)		size of data stream
    #	data stream		(u_char, (stream_size) Bytes)	data stream
    # if lzma-compressed additionally:
    #	props size		(u_int, 4 Bytes)		size of props ( has to be 5 Bytes)
    #	props			(u_char, (props_size) Bytes)	props data for lzma decompressor
    #
    ###################################################################################################
    density = []
    fire = []
    cell_count = 0
    res_x = 0
    res_y = 0
    res_z = 0
    cachefilepath = []
    cachefilename = []

    if not smokecache.is_baked:
        LuxLog('Volumes: Smoke data has to be baked for export')
    else:
        cachefilepath = os.path.join(
            os.path.splitext(os.path.dirname(bpy.data.filepath))[0],
            "blendcache_" + os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        )
        cachefilename = smokecache.name + "_{0:06d}_{1:02d}.bphys".format(scene.frame_current, smokecache.index)
        fullpath = os.path.join(cachefilepath, cachefilename)

        if not os.path.exists(fullpath):
            LuxLog('Volumes: Cachefile doesn''t exist: %s' % fullpath)
        else:
            cachefile = open(fullpath, "rb")
            buffer = cachefile.read(8)
            temp = ""
            stream_size = c_uint()
            props_size = c_uint()
            outlen = c_uint()
            compressed = 0

            for i in range(len(buffer)):
                temp = temp + chr(buffer[i])

            SZ_FLOAT = sizeof(c_float)
            SZ_UINT = sizeof(c_uint)

            if temp == "BPHYSICS":  #valid cache file
                data_type = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                #print("Data type: {0:1d}".format(data_type))

                if data_type == 3 or data_type == 4:
                    cell_count = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                    #print("Cell count: {0:1d}".format(cell_count))
                    struct.unpack("1I", cachefile.read(SZ_UINT))[0]

                    last_pos = cachefile.tell()
                    buffer = cachefile.read(4)
                    temp = ""
                    for i in range(len(buffer)):
                        temp += chr(buffer[i])

                    new_cache = False

                    if temp[0] >= '1' and temp[1] == '.':
                        new_cache = True
                    else:
                        cachefile.seek(last_pos)

                    # Try to read new header
                    if new_cache:
                        # number of fluid fields in the cache file
                        fluid_fields = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        active_fields = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        res_x = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        res_y = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        res_z = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        dx = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        cell_count = res_x * res_y * res_z

                    # Shadow values
                    compressed = struct.unpack("1B", cachefile.read(1))[0]

                    if not compressed:
                        cachefile.read(SZ_FLOAT * cell_count)
                    else:
                        stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        cachefile.read(stream_size)

                        if compressed == 2:
                            props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(props_size)

                    # Density values
                    density_compressed = struct.unpack("1B", cachefile.read(1))[0]

                    if not density_compressed:
                        cachefile.read(SZ_FLOAT * cell_count)
                    else:
                        density_stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        density_stream = cachefile.read(density_stream_size)

                        if density_compressed == 2:
                            props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            props = cachefile.read(props_size)

                    if not new_cache:
                        # Densitiy, old values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                    # Heat values
                    compressed = struct.unpack("1B", cachefile.read(1))[0]

                    if not compressed:
                        cachefile.read(SZ_FLOAT * cell_count)
                    else:
                        stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        cachefile.read(stream_size)

                        if compressed == 2:
                            props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(props_size)

                    # Heat, old values
                    compressed = struct.unpack("1B", cachefile.read(1))[0]

                    if not compressed:
                        cachefile.read(SZ_FLOAT * cell_count)
                    else:
                        stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                        cachefile.read(stream_size)

                        if compressed == 2:
                            props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(props_size)

                    # Fire values
                    if new_cache and flowtype >= 1:
                        # Fire values
                        fire_compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not fire_compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            fire_stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            fire_stream = cachefile.read(fire_stream_size)

                            if fire_compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)
                                # Fuel values

                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                        # React values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                                #						if new_cache and flowtype >= 1:
                                #                           #active colors
                                #    						# r values
                                #							compressed = struct.unpack("1B", cachefile.read(1))[0]
                                #							if not compressed:
                                #								cachefile.read(SZ_FLOAT*cell_count)
                                #							else:
                                #								stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #								cachefile.read(stream_size)
                                #								if compressed == 2:
                                #									props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #									cachefile.read(props_size)
                                #    						# g values
                                #							compressed = struct.unpack("1B", cachefile.read(1))[0]
                                #							if not compressed:
                                #								cachefile.read(SZ_FLOAT*cell_count)
                                #							else:
                                #								stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #								cachefile.read(stream_size)
                                #								if compressed == 2:
                                #									props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #									cachefile.read(props_size)
                                #    						# b values
                                #							compressed = struct.unpack("1B", cachefile.read(1))[0]
                                #							if not compressed:
                                #								cachefile.read(SZ_FLOAT*cell_count)
                                #							else:
                                #								stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #								cachefile.read(stream_size)
                                #								if compressed == 2:
                                #									props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                #									cachefile.read(props_size)

                    if is_high_res:
                        # vx values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                        # vy values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                        # vz values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                        if not new_cache:
                            # vx, old values
                            compressed = struct.unpack("1B", cachefile.read(1))[0]

                            if not compressed:
                                cachefile.read(SZ_FLOAT * cell_count)
                            else:
                                stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(stream_size)

                                if compressed == 2:
                                    props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    cachefile.read(props_size)

                            #vy,old values
                            compressed = struct.unpack("1B", cachefile.read(1))[0]

                            if not compressed:
                                cachefile.read(SZ_FLOAT * cell_count)
                            else:
                                stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(stream_size)

                                if compressed == 2:
                                    props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    cachefile.read(props_size)

                            # vz,old values
                            compressed = struct.unpack("1B", cachefile.read(1))[0]
                            if not compressed:
                                cachefile.read(SZ_FLOAT * cell_count)
                            else:
                                stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(stream_size)

                                if compressed == 2:
                                    props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    cachefile.read(props_size)

                        # Obstacle values
                        compressed = struct.unpack("1B", cachefile.read(1))[0]
                        if not compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            cachefile.read(stream_size)

                            if compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                cachefile.read(props_size)

                        # dt value
                        cachefile.read(SZ_FLOAT)
                        # dx value
                        cachefile.read(SZ_FLOAT)

                        if new_cache:
                            #p0
                            cachefile.read(3 * SZ_FLOAT)
                            #p1
                            cachefile.read(3 * SZ_FLOAT)
                            #dp0
                            cachefile.read(3 * SZ_FLOAT)
                            #shift
                            cachefile.read(3 * SZ_UINT)
                            #obj_shift_f
                            cachefile.read(3 * SZ_FLOAT)
                            #obmat
                            cachefile.read(16 * SZ_FLOAT)
                            #base_res
                            cachefile.read(3 * SZ_UINT)
                            #res min
                            cachefile.read(3 * SZ_UINT)
                            #res max
                            cachefile.read(3 * SZ_UINT)
                            #active color
                            cachefile.read(3 * SZ_FLOAT)

                        # High resolution
                        cell_count = cell_count * amplifier * amplifier * amplifier

                        # Density values
                        density_compressed = struct.unpack("1B", cachefile.read(1))[0]

                        if not density_compressed:
                            cachefile.read(SZ_FLOAT * cell_count)
                        else:
                            density_stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                            density_stream = cachefile.read(density_stream_size)

                            if density_compressed == 2:
                                props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                props = cachefile.read(props_size)

                        # Fire values
                        if new_cache and flowtype >= 1:
                            fire_compressed = struct.unpack("1B", cachefile.read(1))[0]

                            if not fire_compressed:
                                cachefile.read(SZ_FLOAT * cell_count)
                            else:
                                fire_stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                fire_stream = cachefile.read(fire_stream_size)

                                if fire_compressed == 2:
                                    props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    cachefile.read(props_size)
                                    #    						# Fuel values
                                    #							compressed = struct.unpack("1B", cachefile.read(1))[0]
                                    #							if not compressed:
                                    #								cachefile.read(SZ_FLOAT*cell_count)
                                    #							else:
                                    #								stream_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    #								cachefile.read(stream_size)
                                    #								if compressed == 2:
                                    #									props_size = struct.unpack("1I", cachefile.read(SZ_UINT))[0]
                                    #									cachefile.read(props_size)

                    if density_compressed == 1:
                        has_lzo, lzodll = library_loader.load_lzo()
                        if has_lzo:
                            LuxLog('Volumes: De-compressing LZO stream of length {0:0d} bytes...'.format(
                                density_stream_size))
                            #print("Cell count: %d"%cell_count)
                            uncomp_stream = (c_float * cell_count * SZ_FLOAT)()
                            p_dens = cast(uncomp_stream, POINTER(c_float))

                            #call lzo decompressor
                            lzodll.lzo1x_decompress(density_stream, density_stream_size, p_dens, byref(outlen), None)

                            for i in range(cell_count):
                                density.append(p_dens[i])
                        else:
                            LuxLog('Volumes: Cannot read compressed LZO stream; no library loaded')

                    elif density_compressed == 2:
                        has_lzma, lzmadll = library_loader.load_lzma()

                        if has_lzma:
                            LuxLog('Volumes: De-compressing LZMA stream of length {0:0d} bytes...'.format(
                                density_stream_size))
                            #print("Cell count: %d"%cell_count)
                            uncomp_stream = (c_float * cell_count * SZ_FLOAT)()
                            p_dens = cast(uncomp_stream, POINTER(c_float))
                            outlen = c_uint(cell_count * SZ_FLOAT)

                            #call lzma decompressor
                            lzmadll.LzmaUncompress(p_dens, byref(outlen), density_stream,
                                                   byref(c_uint(density_stream_size)), props, props_size)

                            for i in range(cell_count):
                                density.append(p_dens[i])
                        else:
                            LuxLog('Volumes: Cannot read compressed LZMA stream; no library loaded')

                    if new_cache and flowtype >= 1:
                        if fire_compressed == 1:
                            has_lzo, lzodll = library_loader.load_lzo()

                            if has_lzo:
                                fire_stream_size = len(fire_stream)
                                LuxLog('Volumes: De-compressing LZO stream of length {0:0d} bytes...'.format(
                                    fire_stream_size))
                                uncomp_stream = (c_float * cell_count * SZ_FLOAT)()
                                p_fire = cast(uncomp_stream, POINTER(c_float))

                                #call lzo decompressor
                                lzodll.lzo1x_decompress(fire_stream, fire_stream_size, p_fire, byref(outlen), None)

                                for i in range(cell_count):
                                    fire.append(p_fire[i])
                            else:
                                LuxLog('Volumes: Cannot read compressed LZO stream; no library loaded')

                        elif fire_compressed == 2:
                            has_lzma, lzmadll = library_loader.load_lzma()

                            if has_lzma:
                                fire_stream_size = len(stream)
                                LuxLog('Volumes: De-compressing LZMA stream of length {0:0d} bytes...'.format(
                                    fire_stream_size))
                                uncomp_stream = (c_float * cell_count * SZ_FLOAT)()
                                p_fire = cast(uncomp_stream, POINTER(c_float))
                                outlen = c_uint(cell_count * SZ_FLOAT)

                                #call lzma decompressor
                                lzmadll.LzmaUncompress(p_fire, byref(outlen), fire_stream,
                                                       byref(c_uint(fire_stream_size)), props, props_size)

                                for i in range(cell_count):
                                    fire.append(p_fire[i])
                            else:
                                LuxLog('Volumes: Cannot read compressed LZMA stream; no library loaded')

            cachefile.close()
            #endif cachefile exists
            return res_x, res_y, res_z, density, fire

    return 0, 0, 0, [], []


def export_smoke(smoke_obj_name, channel):
    if LuxManager.CurrentScene.name == 'preview':
        return 1, 1, 1, 1.0
    else:
        flowtype = -1
        smoke_obj = bpy.data.objects[smoke_obj_name]
        domain = None

        # Search smoke domain target for smoke modifiers
        for mod in smoke_obj.modifiers:
            if mod.name == 'Smoke':
                if mod.smoke_type == 'FLOW':
                    if mod.flow_settings.smoke_flow_type == 'BOTH':
                        flowtype = 2
                    else:
                        if mod.flow_settings.smoke_flow_type == 'SMOKE':
                            flowtype = 0
                        else:
                            if mod.flow_settings.smoke_flow_type == 'FIRE':
                                flowtype = 1

                if mod.smoke_type == 'DOMAIN':
                    domain = smoke_obj
                    smoke_modifier = mod

        eps = 0.000001
        if domain is not None:
            if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 71:
                # Blender version 2.71 supports direct access to smoke data structure
                set = mod.domain_settings

                channeldata = []
                if channel == 'density':
                    for v in set.density_grid:
                        channeldata.append(v.real)

                if channel == 'fire':
                    for v in set.flame_grid:
                        channeldata.append(v.real)

                resolution = set.resolution_max
                big_res = []
                big_res.append(set.domain_resolution[0])
                big_res.append(set.domain_resolution[1])
                big_res.append(set.domain_resolution[2])

                if set.use_high_resolution:
                    big_res[0] = big_res[0] * (set.amplify + 1)
                    big_res[1] = big_res[1] * (set.amplify + 1)
                    big_res[2] = big_res[2] * (set.amplify + 1)
            else:
                p = []
                # gather smoke domain settings
                BBox = domain.bound_box
                p.append([BBox[0][0], BBox[0][1], BBox[0][2]])
                p.append([BBox[6][0], BBox[6][1], BBox[6][2]])
                set = mod.domain_settings
                resolution = set.resolution_max
                smokecache = set.point_cache
                ret = read_cache(smokecache, set.use_high_resolution, set.amplify + 1, flowtype)
                res_x = ret[0]
                res_y = ret[1]
                res_z = ret[2]
                density = ret[3]
                fire = ret[4]

                if res_x * res_y * res_z > 0:
                    # new cache format
                    big_res = []
                    big_res.append(res_x)
                    big_res.append(res_y)
                    big_res.append(res_z)
                else:
                    max = domain.dimensions[0]
                    if (max - domain.dimensions[1]) < -eps:
                        max = domain.dimensions[1]

                    if (max - domain.dimensions[2]) < -eps:
                        max = domain.dimensions[2]

                    big_res = [int(round(resolution * domain.dimensions[0] / max, 0)),
                               int(round(resolution * domain.dimensions[1] / max, 0)),
                               int(round(resolution * domain.dimensions[2] / max, 0))]

                if set.use_high_resolution:
                    big_res = [big_res[0] * (set.amplify + 1), big_res[1] * (set.amplify + 1),
                               big_res[2] * (set.amplify + 1)]

                if channel == 'density':
                    channeldata = density

                if channel == 'fire':
                    channeldata = fire

                    # sc_fr = '%s/%s/%s/%05d' % (efutil.export_path, efutil.scene_filename(), bpy.context.scene.name, bpy.context.scene.frame_current)
                    #		        if not os.path.exists( sc_fr ):
                    #			        os.makedirs(sc_fr)
                    #
                    #       		smoke_filename = '%s.smoke' % bpy.path.clean_name(domain.name)
                    #	        	smoke_path = '/'.join([sc_fr, smoke_filename])
                    #
                    #		        with open(smoke_path, 'wb') as smoke_file:
                    #			        # Binary densitygrid file format
                    #			        #
                    #			        # File header
                    #	        		smoke_file.write(b'SMOKE')        #magic number
                    #		        	smoke_file.write(struct.pack('<I', big_res[0]))
                    #			        smoke_file.write(struct.pack('<I', big_res[1]))
                    #       			smoke_file.write(struct.pack('<I', big_res[2]))
                    # Density data
                    #       			smoke_file.write(struct.pack('<%df'%len(channeldata), *channeldata))
                    #
                    #	        	LuxLog('Binary SMOKE file written: %s' % (smoke_path))

    return big_res[0], big_res[1], big_res[2], channeldata

# return (smoke_path)




