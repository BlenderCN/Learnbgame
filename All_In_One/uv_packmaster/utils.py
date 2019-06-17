
import os
import platform
import traceback
import sys

from .connection import *

import bpy
import bmesh


def get_packer_path():
    file_path = os.path.dirname(os.path.abspath(__file__))
    packer_dirname = 'packer'
    packer_basename = 'uvp'
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
    SELECT_SIMILAR = 5

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
    MAX_GROUP_COUNT_EXCEEDED = 6

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
    SIMILAR_SELECTION = 9
    DONE = 100

class UvTopoAnalysisLevel:
    DEFAULT = 0
    EXTENDED = 1
    PROCESS_SELF_INTERSECT = 2

class UvGroupingMethod:
    EXTERNAL = 0
    SIMILARITY = 1

class PackContext:
    b_context = None
    bm = None
    uv_layer = None

    def __init__(self, _context, _objs):

        self.objs = []

        for obj in _objs:

            if obj.type != 'MESH':
                continue

            already_added = False
            for obj2 in self.objs:
                if obj.data == obj2.data:
                    already_added = True
                    break

            if not already_added:
                self.objs.append(obj)

        self.bms = []
        self.uv_layers = []
        self.face_idx_offsets = []
        self.vert_idx_offsets = []

        self.context = _context
        self.island_bm_map = dict()

        self.uv_island_faces_list = []
        self.face_to_verts = dict()

        self.material_map = None
        self.inconsistent_islands = []

        next_face_idx_offset = 0
        next_vert_idx_offset = 0

        for obj in self.objs:
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            self.bms.append(bm)
            self.uv_layers.append(bm.loops.layers.uv.verify())

            self.face_idx_offsets.append(next_face_idx_offset)
            next_face_idx_offset += len(bm.faces)

            self.vert_idx_offsets.append(next_vert_idx_offset)
            next_vert_idx_offset += len(bm.verts)

    def gather_uv_data(self, send_unselected):
        selected_faces_array = []

        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            selected_faces = get_selected_faces(self, bm, uv_layer)
            selected_faces_array.append(selected_faces)

            uv_island_faces_list, face_to_verts = extract_islands_from_faces(bm, uv_layer, selected_faces,
                                                                             self.face_idx_offsets[bm_idx],
                                                                             self.vert_idx_offsets[bm_idx])

            for island_idx in range(len(self.uv_island_faces_list),
                                    len(self.uv_island_faces_list) + len(uv_island_faces_list)):
                self.island_bm_map[island_idx] = bm_idx;

            self.uv_island_faces_list += uv_island_faces_list
            self.face_to_verts.update(face_to_verts)

        self.selected_count = len(self.uv_island_faces_list)

        if send_unselected:
            def uv_face_hidden(face):
                if self.context.tool_settings.use_uv_select_sync:
                    return face.hide
                else:
                    if not face.select:
                        return True
                return False

            for bm_idx in range(len(self.bms)):
                bm = self.bms[bm_idx]
                uv_layer = self.uv_layers[bm_idx]

                unselected_faces = [face for face in self.bms[bm_idx].faces if
                                    face not in selected_faces_array[bm_idx] and not uv_face_hidden(face)]
                unselected_uv_island_faces_list, unselected_face_to_verts = extract_islands_from_faces(bm, uv_layer,
                                                                                                       unselected_faces,
                                                                                                       self.face_idx_offsets[
                                                                                                           bm_idx],
                                                                                                       self.vert_idx_offsets[
                                                                                                           bm_idx])
                for island_idx in range(len(self.uv_island_faces_list),
                                        len(self.uv_island_faces_list) + len(unselected_uv_island_faces_list)):
                    self.island_bm_map[island_idx] = bm_idx;

                self.uv_island_faces_list += unselected_uv_island_faces_list
                self.face_to_verts.update(unselected_face_to_verts)

    def get_island_material_index(self, bm_idx, island_faces):
        bm = self.bms[bm_idx]
        orig_face_id = next(iter(island_faces)) - self.face_idx_offsets[bm_idx]
        mat_id = bm.faces[orig_face_id].material_index
        for face_id in island_faces:
            orig_face_id = face_id - self.face_idx_offsets[bm_idx]
            face = bm.faces[orig_face_id]
            if face.material_index != mat_id:
                return False, 0

        return True, mat_id

    def prepare_material_map(self):
        self.material_map = dict()

        mat_name_map = dict()
        next_mat_exid = 0

        for idx, island_faces in enumerate(self.uv_island_faces_list):
            bm_idx = self.island_bm_map[idx]
            bm = self.bms[bm_idx]
            obj = self.objs[bm_idx]

            mat_found, mat_id = self.get_island_material_index(bm_idx, island_faces)
            if not mat_found or mat_id >= len(obj.material_slots) or obj.material_slots[mat_id].material is None:
                self.inconsistent_islands.append(idx)
                continue

            mat_name = obj.material_slots[mat_id].material.name

            if mat_name in mat_name_map:
                self.material_map[idx] = mat_name_map[mat_name]
            else:
                mat_name_map[mat_name] = next_mat_exid
                self.material_map[idx] = next_mat_exid
                next_mat_exid += 1

        return len(mat_name_map)


    def update_meshes(self):
        for obj in self.objs:
            bmesh.update_edit_mesh(obj.data)

    def select_face(self, face, select):
        for v in face.verts:
            v.select = select

        face.select = select

    def select_faces(self, island_faces, select):
        island_faces.sort()

        curr_bm_idx = 0
        curr_bm = self.bms[0]
        curr_uv_layer = self.uv_layers[0]
        curr_face_idx_offset = 0
        next_face_idx_offset = len(self.bms[0].faces)

        for face_idx in island_faces:
            while face_idx >= next_face_idx_offset:
                curr_bm_idx += 1
                next_face_idx_offset += len(self.bms[curr_bm_idx].faces)
                curr_bm = self.bms[curr_bm_idx]
                curr_uv_layer = self.uv_layers[curr_bm_idx]
                curr_face_idx_offset = self.face_idx_offsets[curr_bm_idx]

            orig_face_idx = face_idx - curr_face_idx_offset
            face = curr_bm.faces[orig_face_idx]

            if self.context.tool_settings.use_uv_select_sync:
                self.select_face(face, select)
            else:
                for loop in face.loops:
                    loop[curr_uv_layer].select = select

    def select_island_faces(self, island_idx, island_faces, select):
        bm_idx = self.island_bm_map[island_idx]
        bm = self.bms[bm_idx]
        uv_layer = self.uv_layers[bm_idx]
        face_idx_offset = self.face_idx_offsets[bm_idx]

        if self.context.tool_settings.use_uv_select_sync:
            for face_idx in island_faces:
                orig_face_idx = face_idx - face_idx_offset
                face = bm.faces[orig_face_idx]
                self.select_face(face, select)
        else:
            for face_idx in island_faces:
                orig_face_idx = face_idx - face_idx_offset
                face = bm.faces[orig_face_idx]

                for loop in face.loops:
                    loop[uv_layer].select = select

    def select_all_faces(self, select):
        for bm_idx in range(len(self.bms)):
            bm = self.bms[bm_idx]
            uv_layer = self.uv_layers[bm_idx]

            if self.context.tool_settings.use_uv_select_sync:
                for face in bm.faces:
                    self.select_face(face, select)
            else:
                for face in bm.faces:
                    for loop in face.loops:
                        loop[uv_layer].select = select

def get_prefs():
    return bpy.context.preferences.addons['uv_packmaster'].preferences


def platform_check_op():
    prefs = get_prefs()
    if not prefs.platform_supported:
        raise RuntimeError(prefs.not_supported_message)

    if not os.path.isfile(get_packer_path()):
        raise RuntimeError('Packer executable not found. Addon installation is corrupted')


def get_selected_faces(p_context, bm, uv_layer):
    if p_context.context.tool_settings.use_uv_select_sync:
        return [f for f in bm.faces if f.select]
    else:
        face_list = []
        for face in bm.faces:
            if not face.select:
                continue

            face_selected = False

            for loop in face.loops:
                if loop[uv_layer].select:
                    face_selected = True
                    break

            if face_selected:
                face_list.append(face)

        return face_list


def extract_islands_from_faces(bm, uv_layer, faces, face_idx_offset, vert_idx_offset):
    def get_uv_id_from_loop(uv_layer, l):
        return (l[uv_layer].uv.to_tuple(5), l.vert.index + vert_idx_offset)

    face_to_verts = defaultdict(list)
    vert_to_faces = defaultdict(set)

    for f in faces:
        for l_idx, l in enumerate(f.loops):
            id = get_uv_id_from_loop(uv_layer, l)

            face_idx = face_idx_offset + f.index
            face_to_verts[face_idx].append(id)
            vert_to_faces[id].add(face_idx)


    def extract_island(bm, face_idx, faces_left, island_faces):
        faces_left.remove(face_idx)
        faces_to_process = [face_idx]

        while len(faces_to_process) > 0:
            new_face_idx = faces_to_process.pop(0)
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
        uv_island_faces_list = []
        faces_left = set(face_to_verts.keys())
        while len(faces_left) > 0:
            current_island_faces = set()
            face_idx = list(faces_left)[0]
            extract_island(bm, face_idx, faces_left, current_island_faces)
            uv_island_faces_list.append(current_island_faces)
        return uv_island_faces_list

    uv_island_faces_list = extract_islands(bm)


    return uv_island_faces_list, face_to_verts

def handle_invalid_islands(p_context, invalid_islands):
    p_context.select_all_faces(False)

    for idx, island_faces in enumerate(p_context.uv_island_faces_list):
        if idx in invalid_islands:
            p_context.select_island_faces(idx, island_faces, True)

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
                p_context.select_island_faces(idx, island_faces, False)
            else:
                p_context.select_island_faces(idx, island_faces, True)

    return overlap_detected


def get_active_image_ratio(context):
    img = None
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            img = area.spaces.active.image

    if img is None:
        raise RuntimeError('No active texture found, open a texture in the UV editor')

    return float(img.size[0]) / float(img.size[1])
