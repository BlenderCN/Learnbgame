'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import gpu
import bgl
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader
import blf


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


def get_scale_mat(vec_scale):
    mat_scale = Matrix.Identity(4)
    mat_scale[0][0] = vec_scale.x
    mat_scale[1][1] = vec_scale.y
    mat_scale[2][2] = vec_scale.z
    return mat_scale


LEFT = ('l', 'L','left','Left','LEFT')
RIGHT = ('r', 'R','right','Right','RIGHT')

def is_name_r_l(name):
    return name.endswith(LEFT) or name.endswith(RIGHT)

def get_mirrored_name(name):
    for i, l_suffx in enumerate(LEFT):
        if name.endswith('.'+l_suffx) or name.endswith('_'+l_suffx):
            return name[:-1*len(l_suffx)] + RIGHT[i]
    for i, r_suffx in enumerate(RIGHT):
        if name.endswith('.'+r_suffx) or name.endswith('_'+r_suffx):
            return name[:-1*len(r_suffx)] + LEFT[i]
    return ''

LEFT_MARGIN = 80
TOP_POSITION = 250
BOX_WIDTH = 395

def draw_text_line(lines):
    line_height_h1 = 35
    line_height_p = 28
    font_id = 0
    current_line_pos = TOP_POSITION
    for line in lines:
        text, line_type = line
        font_size = 24 if line_type == 'H1' else 20
        blf.size(font_id, font_size, 60)
        blf.position(font_id, LEFT_MARGIN, current_line_pos, 0)
        blf.draw(font_id, text)
        if line_type == 'H1':
            current_line_pos -= line_height_h1
        else:
            current_line_pos -= line_height_p
    draw_background_box(width=BOX_WIDTH, height=TOP_POSITION +
                        line_height_h1, x0=LEFT_MARGIN-20, y0=current_line_pos)


shader2d = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
def draw_background_box(width, height, x0, y0):
    # draw box
    x1 = width
    y1 = height
    positions = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]

    vertices = (
        (x0, y0), (width, y0),
        (x0, height), (width, height))
    indices = ( (0, 1, 2), (2, 1, 3))
    bgl.glEnable(bgl.GL_BLEND)
    batch = batch_for_shader(shader2d, 'TRIS', {"pos": vertices}, indices=indices)

    shader2d.bind()
    shader2d.uniform_float("color", (0., 0., 0., 0.3))
    batch.draw(shader2d)
    bgl.glDisable(bgl.GL_BLEND)


def get_addon_name():
    return __package__.split(".")[0]


def addon_name_lowercase():
    return get_addon_name().lower()


def get_addon_preferences():
    return bpy.context.preferences.addons[get_addon_name()].preferences

def get_mat_world_obj(obj):
    obj.matrix_basis == (Matrix.Translation(obj.location) @ obj.rotation_quaternion.to_matrix().to_4x4() @ get_scale_mat(obj.scale))
    # replace rotation_quaternion with rotation_euler if you are using Euler mode
    matrix_local = obj.matrix_parent_inverse @ obj.matrix_basis
    matrix_world = matrix_local if obj.parent is None else obj.parent.matrix_word @ matrix_local
    return matrix_world


def get_new_mat_parent_inv(old_parent_m_w, new_parent_m_w, old_obj_m_p_inv):
    ''' cos: old_m_w == new_m_w'''
    ''' so:  old_parent_m_w @ obj.m_p_inv1 @ obj.m_basis  ==  new_parent_m_w @ obj.m_p_inv2 @ obj.m_basis'''
    ''' so:  old_parent_m_w @ obj.m_p_inv1 @ new_parent_m_w.inv()   ==   obj.m_p_inv2'''
    return old_parent_m_w @ old_obj_m_p_inv @ new_parent_m_w.inverted()

def clear_parent(obj):
    parent = obj.parent
    if parent:
        obj.matrix_basis = parent.matrix_world @ obj.matrix_parent_inverse @ obj.matrix_basis
        obj.parent = None

def set_parent(obj, new_parent):
    if obj.parent: #if there is old parent
        old_parent_m_w = obj.parent.matrix_world
        new_m_p_inv = old_parent_m_w @ obj.matrix_parent_inverse @ new_parent.matrix_world.inverted()
        obj.matrix_parent_inverse = new_m_p_inv
    else:
        obj.matrix_parent_inverse = new_parent.matrix_world.inverted()
    obj.parent = new_parent

def link_to_collection_sibling(source_obj, clone):
    ''' Link clone to collection where source_obj is located '''
    if len(source_obj.users_collection)>0:
        if clone.name not in source_obj.users_collection[0].objects.keys():
            source_obj.users_collection[0].objects.link(clone)
        else:
            return
    else:
        if clone.name not in bpy.context.scene.collection.objects.keys():
            bpy.context.scene.collection.objects.link(clone)
        else:
            return

def find_create_collection(parent_col, searched_col_name):
    ''' Try to find searched collection name in parent childrens. If not found create it and link it to master'''
    def find_coll(p_coll, search_col):
        if search_col == p_coll.name:
            return True
        if search_col in p_coll.children.keys():
            return True
        else: 
            for child_col in p_coll.children:
                if find_coll(child_col,search_col):
                    return True
        return False

    if find_coll(parent_col, searched_col_name):
        collection = bpy.data.collections[searched_col_name]
    else:
        if searched_col_name in bpy.data.collections.keys():
            collection = bpy.data.collections[searched_col_name]
        else:
            collection = bpy.data.collections.new(searched_col_name)
        parent_col.children.link(collection)
    return collection


def remap_sewing(context, sewing_obj, old_new_map_id, new_sewing_obj=None):
    instances = [sewing_obj.name for obj in bpy.data.objects if obj.data == sewing_obj.data]  # for finding patterns that were using splited pattern geo
    garment_using_sel_obj = set()
    if new_sewing_obj is not None:
        old_new_map_id2 = {new: old for new, old in old_new_map_id.items() if new != old}
    else:
        old_new_map_id2 = old_new_map_id

    for i, garment in enumerate(context.scene.cloth_garment_data):
        for idx, sewing in enumerate(garment.garment_sewings):
            if sewing.source_obj.name in instances:
                if sewing.segment_id_from in old_new_map_id2.keys():
                    if new_sewing_obj is not None:
                        sewing.source_obj = new_sewing_obj
                    sewing.segment_id_from = old_new_map_id2[sewing.segment_id_from]
                    garment_using_sel_obj.add(i)
            if sewing.target_obj.name in instances:
                if sewing.segment_id_to in old_new_map_id2.keys():
                    if new_sewing_obj is not None:
                        sewing.target_obj = new_sewing_obj  # map old pattern to clone
                    sewing.segment_id_to = old_new_map_id2[sewing.segment_id_to]
                    garment_using_sel_obj.add(i)

    for g_id in garment_using_sel_obj:  # find if new sewing obj patter, is in garment patterns list (sewing_patterns)
        garment = context.scene.cloth_garment_data[g_id]
        pattern_found = False
        for pattern in garment.sewing_patterns:
            if pattern.pattern_obj == sewing_obj:
                pattern_found = True
        if not pattern_found:  # if not then add new pattern
            new_pattern = garment.sewing_patterns.add()
            new_pattern.pattern_obj = sewing_obj if new_sewing_obj is None else new_sewing_obj

    return list(garment_using_sel_obj)


class GTOOL_OT_GarmentCleanup(bpy.types.Operator):
    bl_idname = "garment.cleanup"
    bl_label = "Cleanup garments"
    bl_description = 'Remove unused sewings/garment meshes that are no longer on scene. Resets broken sewings ids to 0'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        # remove garment pattern objs, that are not in vieport
        #check view layer, cos obj might have been removed, but is it sitll in blend file, cos of pattern_obj pointer
        meshes_to_remove = [idx for idx, garment_mesh in enumerate(
            garment.sewing_patterns) if garment_mesh.pattern_obj is None or garment_mesh.pattern_obj.name not in context.scene.objects.keys() or garment_mesh.pattern_obj.data.dimensions != '2D']
        for idx in reversed(meshes_to_remove):
            self.report({'INFO'}, 'Removed empty pattern: ')
            garment.sewing_patterns.remove(idx)

        #get list of garment pattern objs
        pattern_objs = [obj.pattern_obj.name for obj in garment.sewing_patterns]

        #remove sewing that are not attached to pattern objs
        sewing_to_remove = []
        for idx, sewing in enumerate(garment.garment_sewings):
            if sewing.source_obj is None or sewing.source_obj.name not in pattern_objs or sewing.source_obj.type != 'CURVE' or sewing.segment_id_from >= len(sewing.source_obj.data.splines[0].bezier_points):
                sewing_to_remove.append(idx)
                continue
            if sewing.target_obj is None or sewing.target_obj.name not in pattern_objs or sewing.target_obj.type != 'CURVE' or sewing.segment_id_to >= len(sewing.target_obj.data.splines[0].bezier_points):
                sewing_to_remove.append(idx)
                continue
            seg_count_source_obj = len(sewing.source_obj.data.splines[0].bezier_points)
            seg_count_target_obj = len(sewing.target_obj.data.splines[0].bezier_points)
            if sewing.segment_id_from >= seg_count_source_obj:
                sewing.segment_id_from = seg_count_source_obj - 1
            if sewing.segment_id_to >= seg_count_target_obj:
                sewing.segment_id_to = seg_count_target_obj - 1
        for idx in reversed(sewing_to_remove):
            self.report({'INFO'}, 'Removed broken sewing: ' + str(idx))
            garment.garment_sewings.remove(idx)
        sewing_to_remove.clear()

        #DONE: remove duplicate sewing
        sewing_count = len(garment.garment_sewings)
        for idx, sewing in enumerate(garment.garment_sewings):
            for idx2 in range(idx+1, sewing_count):
                if sewing.source_obj == garment.garment_sewings[idx2].source_obj and sewing.target_obj == garment.garment_sewings[idx2].target_obj  \
                        and sewing.segment_id_from == garment.garment_sewings[idx2].segment_id_from and sewing.segment_id_to == garment.garment_sewings[idx2].segment_id_to:
                        sewing_to_remove.append(idx)
                        continue
                if sewing.source_obj == garment.garment_sewings[idx2].target_obj and sewing.target_obj == garment.garment_sewings[idx2].source_obj  \
                        and sewing.segment_id_from == garment.garment_sewings[idx2].segment_id_to and sewing.segment_id_to == garment.garment_sewings[idx2].segment_id_from:
                        sewing_to_remove.append(idx)
                        continue
        for idx in reversed(sewing_to_remove):
            self.report({'INFO'}, 'Removed duplicated sewing: ' + str(idx))
            garment.garment_sewings.remove(idx)

        #fix unused pockets. - pocketObj is empty, or not in scene, target_pattern is empty, or not in scene, or not in PatternsList
        pockets_ids_to_remove = [idx for idx, pocket in enumerate(
            garment.pockets) if not pocket.pocketObj or pocket.pocketObj.name not in context.scene.objects.keys() or not pocket.target_pattern or pocket.target_pattern.name not in pattern_objs]
        for p_id in reversed(pockets_ids_to_remove):
            garment.pockets.remove(p_id)

        #Remove broken pins
        pins_to_remove = [idx for idx, pin in enumerate(
            garment.pins) if pin.source_obj is None or pin.source_obj.name not in pattern_objs or
            pin.target_obj is None or pin.target_obj.name not in pattern_objs]
        for idx in reversed(pins_to_remove):
            garment.pins.remove(idx)
        return {'FINISHED'}
