
import time
import os

import bpy

from .. import ogf
from .. import types
from . import importer
from . import format_
from . import geom

try:
    from io_scene_xray import xray_io
except ImportError:
    pass


def _sector_root(data, sector):
    packed_reader = xray_io.PackedReader(data)
    root = packed_reader.getf('I')[0]
    sector.root = root


def _sector_portal(data, sector):
    packed_reader = xray_io.PackedReader(data)
    portal_count = len(data) // format_.SECTOR_PORTAL_SIZE
    sector.portal_count = portal_count

    for portal_index in range(portal_count):
        portal = packed_reader.getf('H')[0]


def _sector(data):
    chunked_reader = xray_io.ChunkedReader(data)
    sector = types.Sector()

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == format_.Chunks.Sector.PORTALS:
            _sector_portal(chunk_data, sector)
        elif chunk_id == format_.Chunks.Sector.ROOT:
            _sector_root(chunk_data, sector)
        else:
            print('UNKNOW LEVEL SECTOR CHUNK: {0:#x}'.format(chunk_id))

    return sector


def _sectors(data, level):
    chunked_reader = xray_io.ChunkedReader(data)

    for sector_id, sector_data in chunked_reader:
        sector = _sector(sector_data)
        level.sectors.append(sector)


def _glows(data):
    packed_reader = xray_io.PackedReader(data)
    glows_count = len(data) // format_.GLOW_SIZE

    for glow_index in range(glows_count):
        position = packed_reader.getf('3f')
        radius = packed_reader.getf('f')[0]
        shader_index = packed_reader.getf('H')[0]


def _light_dynamic(data):
    packed_reader = xray_io.PackedReader(data)
    light_count = len(data) // format_.LIGHT_DYNAMIC_SIZE

    for light_index in range(light_count):
        controller_id = packed_reader.getf('I')[0] # ???
        type = packed_reader.getf('I')[0] # ???
        diffuse = packed_reader.getf('4f')
        specular = packed_reader.getf('4f')
        ambient = packed_reader.getf('4f')
        position = packed_reader.getf('3f')
        direction = packed_reader.getf('3f')
        range_ = packed_reader.getf('f')[0]
        falloff = packed_reader.getf('f')[0]
        attenuation_0 = packed_reader.getf('f')[0]
        attenuation_1 = packed_reader.getf('f')[0]
        attenuation_2 = packed_reader.getf('f')[0]
        theta = packed_reader.getf('f')[0]
        phi = packed_reader.getf('f')[0]


def _portals(data):
    packed_reader = xray_io.PackedReader(data)
    portals_count = len(data) // format_.PORTAL_SIZE

    for portal_index in range(portals_count):
        sector_front = packed_reader.getf('H')[0]
        sector_back = packed_reader.getf('H')[0]

        for vertex_index in range(format_.PORTAL_VERTEX_COUNT):
            coord_x, coord_y, coord_z = packed_reader.getf('fff')

        used_vertices_count = packed_reader.getf('I')[0]


def _visuals(data, level):
    chunked_reader = xray_io.ChunkedReader(data)
    for visual_index, visual_data in chunked_reader:
        visual = ogf.read.main(visual_data)
        level.visuals.append(visual)


def _shaders_v13(data, level):
    packed_reader = xray_io.PackedReader(data)
    shaders_count = packed_reader.getf('I')[0]
    empty_shader = packed_reader.gets()

    for shader_index in range(shaders_count - 1):
        shader = packed_reader.gets()
        engine_shader, textures = shader.split('/')
        light_maps_count = textures.count(',')

        if not light_maps_count:
            texture = textures
            level.lmaps.append(None)
            level.lmaps_0.append(None)
            level.lmaps_1.append(None)

        elif light_maps_count == 1:
            texture, lmap = textures.split(',')
            level.lmaps.append(lmap)
            level.lmaps_0.append(None)
            level.lmaps_1.append(None)

        elif light_maps_count == 2:
            texture, lmap_0, lmap_1 = textures.split(',')
            level.lmaps.append(None)
            level.lmaps_0.append(lmap_0)
            level.lmaps_1.append(lmap_1)

        else:
            raise Exception('Shader has to many lmaps!')

        level.materials.append(texture)
        level.shaders.append(engine_shader)


class ShaderV8:
    def __init__(self):
        self.shader = None
        self.light_map = None


def _shaders_v8(data, level):
    packed_reader = xray_io.PackedReader(data)
    shaders_count = packed_reader.getf('I')[0]

    for shader_index in range(shaders_count):
        raw_string = packed_reader.gets()
        shader = ShaderV8()
        if ',' in raw_string:
            shader.shader, shader.light_map = raw_string.split(',')
        else:
            shader.shader = raw_string
        level.shaders.append(shader)


def header(data):
    packed_reader = xray_io.PackedReader(data)
    xrlc_version = packed_reader.getf('H')[0]
    xrlc_quality = packed_reader.getf('H')[0]
    if xrlc_version not in format_.XRLC_SUPPORT_VERSIONS:
        raise Exception('UNSUPPORTED FORMAT VERSION: {}'.format(xrlc_version))
    return xrlc_version


def _root(data, level):
    start_time = time.time()
    chunked_reader = xray_io.ChunkedReader(data)

    chunk_data = chunked_reader.next(format_.Chunks.HEADER)
    xrlc_version = header(chunk_data)
    level.format_version = xrlc_version
    chunks = format_.CHUNKS_TABLE[xrlc_version]

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == chunks.SHADERS:
            if level.format_version <= format_.XRLC_VERSION_11:
                _shaders_v8(chunk_data, level)
            else:
                _shaders_v13(chunk_data, level)

        elif chunk_id == chunks.VISUALS:
            visuals_chunk_data = chunk_data

        elif chunk_id == chunks.PORTALS:
            _portals(chunk_data)

        elif chunk_id == chunks.LIGHT_DYNAMIC:
            _light_dynamic(chunk_data)

        elif chunk_id == chunks.GLOWS:
            _glows(chunk_data)

        elif chunk_id == chunks.SECTORS:
            _sectors(chunk_data, level)

        elif chunk_id == chunks.VB:
            geom.read.vertex_buffers(chunk_data, level)

        elif chunk_id == chunks.IB:
            geom.read.indices_buffers(chunk_data, level)

        elif chunk_id == chunks.SWIS:
            geom.read.slide_windows_indices(chunk_data, level)

        else:
            print('UNKNOW LEVEL CHUNK: {0:#x}'.format(chunk_id))

    print('Load Level', time.time() - start_time)

    start_time = time.time()

    geom_path = level.file_path + '.geom'
    has_geom = False
    if os.path.exists(geom_path):
        has_geom = True
        geom.read.file(geom_path, level)

    geomx_path = level.file_path + '.geomx'
    has_geomx = False
    if os.path.exists(geomx_path):
        has_geomx = True
        geom.read.file(geomx_path, level, fastpath=True)

    level.has_geomx = has_geomx

    print('Load Geom:', time.time() - start_time)

    start_time = time.time()
    _visuals(visuals_chunk_data, level)
    print('Load Visuals', time.time() - start_time)
    start_time = time.time()
    importer.import_visuals(level)
    print('Imported Visuals', time.time() - start_time)


def file(file_path):
    level = types.Level()
    level.file_path = file_path

    with open(file_path, 'rb') as file_:
        data = file_.read()
        _root(data, level)
