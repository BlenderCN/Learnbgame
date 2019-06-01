# Copyright (c) 2017 The Khronos Group Inc.
# Modifications Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#
# Imports
#

import bpy
import json
import struct
import os

from .gltf2_debug import *
from .gltf2_filter import *
from .gltf2_generate import *

#
# Globals
#

#
# Functions
#

def prepare(export_settings):
    """
    Stores current state of Blender and prepares for export, depending on the current export settings.
    """
    if bpy.context.active_object is not None and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    filter_apply(export_settings)

    export_settings['gltf_original_frame'] = bpy.context.scene.frame_current

    export_settings['gltf_use_no_color'] = []

    export_settings['gltf_joint_cache'] = {}

    if export_settings['gltf_animations']:
        bpy.context.scene.frame_set(0)


def finish(export_settings):
    """
    Brings back Blender into its original state before export and cleans up temporary objects.
    """
    if export_settings['temporary_meshes'] is not None:
        for temporary_mesh in export_settings['temporary_meshes']:
            bpy.data.meshes.remove(temporary_mesh)

    if export_settings['temporary_materials'] is not None:
        for temporary_mat in export_settings['temporary_materials']:
            bpy.data.materials.remove(temporary_mat)

    bpy.context.scene.frame_set(export_settings['gltf_original_frame'])

def compressLZMA(path, settings):

    if settings['gltf_format'] == 'FB' or settings['gltf_sneak_peek']:
        return

    if not settings['gltf_lzma_enabled']:
        return

    # improves console readability
    path = os.path.normpath(path)

    printLog('INFO', 'Compressing file: ' + path)

    import http.client

    with open(path, 'rb') as fin:
        conn = http.client.HTTPConnection(settings['gltf_app_manager_host'])
        headers = {'Content-type': 'application/octet-stream'}
        conn.request('POST', '/storage/lzma/', body=fin, headers=headers)
        response = conn.getresponse()

        if response.status != 200:
            printLog('ERROR', 'LZMA compression error: ' + response.reason)

        with open(path + '.xz', 'wb') as fout:
            fout.write(response.read())


def save(operator, context, export_settings):
    """
    Starts the glTF 2.0 export and saves to content either to a .gltf or .glb file.
    """

    printLog('INFO', 'Starting glTF 2.0 export')
    bpy.context.window_manager.progress_begin(0, 100)
    bpy.context.window_manager.progress_update(0)

    #

    prepare(export_settings)

    #

    glTF = {}

    generateGLTF(operator, context, export_settings, glTF)

    cleanupDataKeys(glTF)

    indent = None
    separators = separators=(',', ':')

    if export_settings['gltf_format'] == 'ASCII' and not export_settings['gltf_strip']:
        indent = 4
        separators = separators=(', ', ' : ')

    glTF_encoded = json.dumps(glTF, indent=indent, separators=separators,
            sort_keys=True, ensure_ascii=False)

    #

    if export_settings['gltf_format'] == 'ASCII':
        file = open(export_settings['gltf_filepath'], "w", encoding="utf8", newline="\n")
        file.write(glTF_encoded)
        file.write("\n")
        file.close()

        binary = export_settings['gltf_binary']
        if len(binary) > 0 and not export_settings['gltf_embed_buffers']:
            file = open(export_settings['gltf_filedirectory'] + export_settings['gltf_binaryfilename'], "wb")
            file.write(binary)
            file.close()

        compressLZMA(export_settings['gltf_filepath'], export_settings)
        compressLZMA(export_settings['gltf_filedirectory'] + export_settings['gltf_binaryfilename'], export_settings)

    else:
        file = open(export_settings['gltf_filepath'], "wb")

        glTF_data = glTF_encoded.encode()
        binary = export_settings['gltf_binary']

        length_gtlf = len(glTF_data)
        spaces_gltf = (4 - (length_gtlf & 3)) & 3
        length_gtlf += spaces_gltf

        length_bin = len(binary)
        zeros_bin = (4 - (length_bin & 3)) & 3
        length_bin += zeros_bin

        length = 12 + 8 + length_gtlf
        if length_bin > 0:
            length += 8 + length_bin

        # Header (Version 2)
        file.write('glTF'.encode())
        file.write(struct.pack("I", 2))
        file.write(struct.pack("I", length))

        # Chunk 0 (JSON)
        file.write(struct.pack("I", length_gtlf))
        file.write('JSON'.encode())
        file.write(glTF_data)
        for i in range(0, spaces_gltf):
            file.write(' '.encode())

        # Chunk 1 (BIN)
        if length_bin > 0:
            file.write(struct.pack("I", length_bin))
            file.write('BIN\0'.encode())
            file.write(binary)
            for i in range(0, zeros_bin):
                file.write('\0'.encode())

        file.close()

        compressLZMA(export_settings['gltf_filepath'], export_settings)

    #

    finish(export_settings)

    #

    printLog('INFO', 'Finished glTF 2.0 export')
    bpy.context.window_manager.progress_end()
    print_newline()

    return {'FINISHED'}

def cleanupDataKeys(glTF):
    """
    Remove "id" keys used in the exporter to assign entity indices
    """
    for key, val in glTF.items():
        if type(val) == list:
            for entity in val:
                if 'id' in entity:
                    del entity['id']
