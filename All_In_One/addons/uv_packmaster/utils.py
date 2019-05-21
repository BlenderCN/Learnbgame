
import os
import platform
import traceback
import sys

from .connection import *

import bpy


def get_packer_path():
    file_path = os.path.dirname(os.path.abspath(__file__))
    packer_dirname = 'packer'
    packer_basename = 'uvPack'
    return os.path.join(file_path, packer_dirname, os_packer_dirname(), packer_basename + os_exec_extension())


from collections import defaultdict

if platform.system() == 'Linux':
    from .os_linux import *
elif platform.system() == 'Windows':
    from .os_windows import *
elif platform.system() == 'Darwin':
    from .os_mac import *


def in_debug_mode():
    return bpy.app.debug_value != 0


def print_backtrace(ex):
    _, _, trback = sys.exc_info()
    traceback.print_tb(trback)
    trbackDump = traceback.extract_tb(trback)
    filename, line, func, msg = trbackDump[-1]

    print('Line: {} Message: {}'.format(line, msg))
    print(str(ex))


class UvPackerOpcode:
    REPORT_VERSION = 0
    PACK = 1
    OVERLAP_CHECK = 2
    MEASURE_AREA = 3
    VALIDATE_UVS = 4

class UvPackerIslandFlags:
    OVERLAPS = 1

class UvPackerFeatureCode:
    DEMO = 0
    ISLAND_ROTATION = 1
    OVERLAP_CHECK = 2
    PACKING_DEPTH = 3
    HEURISTIC_SEARCH = 4
    PACK_RATIO = 5
    PACK_TO_OTHERS = 6
    GROUPED_PACK = 7
    LOCK_OVERLAPPING = 8
    ADVANCED_HEURISTIC = 9
    SELF_INTERSECT_PROCESSING = 10
    VALIDATION = 11

class UvPackerErrorCode:
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_TOPOLOGY = 2
    NO_SPACE = 3
    NO_VALID_STATIC_ISLAND = 4
    UNEXPECTED_INVALID_TOPOLOGY = 5

class UvPackingPhaseCode:
    INITIALIZATION = 0
    TOPOLOGY_ANALYSIS = 1
    PACKING_INITIALIZATION = 2
    PACKING = 3
    AREA_MEASUREMENT = 4
    OVERLAP_CHECK = 5
    RENDER_PRESENTATION = 6
    TOPOLOGY_VALIDATION = 7
    VALIDATION = 8
    DONE = 100

class UvTopoAnalysisLevel:
    DEFAULT = 0
    EXTENDED = 1
    PROCESS_SELF_INTERSECT = 2

class PackContext:
    b_context = None
    bm = None
    uv_layer = None

    def __init__(self, _context, _bm, _uv_layer):
        self.context = _context
        self.bm = _bm
        self.uv_layer = _uv_layer


def get_prefs():
    return bpy.context.user_preferences.addons['uv_packmaster'].preferences


def platform_check_op():
    prefs = get_prefs()
    if not prefs.platform_supported:
        raise RuntimeError(prefs.not_supported_message)

    if not os.path.isfile(get_packer_path()):
        raise RuntimeError('Packer executable not found. Addon installation is corrupted')


def get_selected_faces(p_context):
    if p_context.context.tool_settings.use_uv_select_sync:
        return [f for f in p_context.bm.faces if f.select]
    else:
        face_list = []
        for face in p_context.bm.faces:
            if not face.select:
                continue

            face_selected = False

            for loop in face.loops:
                if loop[p_context.uv_layer].select:
                    face_selected = True
                    break

            if face_selected:
                face_list.append(face)

        return face_list


def extract_islands_from_faces(bm, uv_layer, faces):
    def get_next_cyclic(len, idx):
        return (idx + 1) % len

    def get_prev_cyclic(len, idx):
        return (idx - 1) % len

    def get_uv_id_from_loop(uv_layer, l):
        return (l[uv_layer].uv.to_tuple(5), l.vert.index)

    face_to_verts = defaultdict(list)
    vert_to_faces = defaultdict(set)

    for f in faces:
        for l_idx, l in enumerate(f.loops):
            id = get_uv_id_from_loop(uv_layer, l)
            prev_id = get_uv_id_from_loop(uv_layer, f.loops[get_prev_cyclic(len(f.loops), l_idx)])
            next_id = get_uv_id_from_loop(uv_layer, f.loops[get_next_cyclic(len(f.loops), l_idx)])
            face_to_verts[f.index].append(id)
            vert_to_faces[id].add(f.index)


    def extract_island(bm, face_idx, faces_left, island, island_faces):
        faces_left.remove(face_idx)
        faces_to_process = [face_idx]

        while len(faces_to_process) > 0:
            new_face_idx = faces_to_process.pop(0)

            island |= set(face_to_verts[new_face_idx])
            island_faces.add(new_face_idx)

            # island.append(bm.faces[face_idx])
            for v in face_to_verts[new_face_idx]:
                connected_faces = vert_to_faces[v]
                if connected_faces:
                    for cf in connected_faces:
                        if cf in faces_left:
                            faces_left.remove(cf)
                            faces_to_process.append(cf)
                        # extract_island(bm, cf, faces_left, island, island_faces)

    def extract_islands(bm):
        uv_island_list = []
        uv_island_faces_list = []
        faces_left = set(face_to_verts.keys())
        while len(faces_left) > 0:
            current_island = set()
            current_island_faces = set()
            face_idx = list(faces_left)[0]
            extract_island(bm, face_idx, faces_left, current_island, current_island_faces)
            uv_island_list.append(current_island)
            uv_island_faces_list.append(current_island_faces)
        return uv_island_list, uv_island_faces_list

    uv_island_list, uv_island_faces_list = extract_islands(bm)


    return uv_island_faces_list, face_to_verts


def select_faces(p_context, island_faces, select):
    def select_face(face, select):
        for v in face.verts:
            v.select = select

        face.select = select

    if p_context.context.tool_settings.use_uv_select_sync:
        for face_idx in island_faces:
            face = p_context.bm.faces[face_idx]
            select_face(face, select)
    else:
        for face_idx in island_faces:
            face = p_context.bm.faces[face_idx]

            for loop in face.loops:
                loop[p_context.uv_layer].select = select



def handle_invalid_islands(p_context, uv_island_faces_list, invalid_islands):
    select_faces(p_context, range(len(p_context.bm.faces)), False)
    for idx, island_faces in enumerate(uv_island_faces_list):
        if idx in invalid_islands:
            select_faces(p_context, island_faces, True)


def invalid_islands_handler(err, p_context):
    handle_invalid_islands(p_context, err.uv_island_faces_list, err.island_indices)


def handle_island_flags(p_context, uv_island_faces_list, island_flags):
    overlap_indicies = []
    for i in range(len(island_flags)):
        overlaps = island_flags[i] & UvPackerIslandFlags.OVERLAPS
        if overlaps > 0:
            overlap_indicies.append(i)

    overlap_detected = len(overlap_indicies) > 0
    if overlap_detected:
        for idx, island_faces in enumerate(uv_island_faces_list):
            if idx not in overlap_indicies:
                select_faces(p_context, island_faces, False)
            else:
                select_faces(p_context, island_faces, True)

    return overlap_detected


def get_active_image_ratio(context):
    img = None
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            img = area.spaces.active.image

    if img is None:
        raise RuntimeError('No active texture found, open a texture in the UV editor')

    return float(img.size[0]) / float(img.size[1])


def get_island_material(p_context, island_faces):
    mat_id = p_context.bm.faces[next(iter(island_faces))].material_index
    for id in island_faces:
        face = p_context.bm.faces[id]
        if face.material_index != mat_id:
            return False, 0

    return True, mat_id