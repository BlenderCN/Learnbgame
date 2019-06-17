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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import mathutils
from mathutils import Vector, Matrix
from collections import OrderedDict
from copy import deepcopy
from .utils.helper_functions import *


class GTOOL_OT_CurveSymmetrize(bpy.types.Operator):
    bl_label = "Symmetrize"
    bl_idname = "curve.curve_symmetrize"
    bl_description = "Symmetrize curve. Select two points on curve, which will define symmetry axis.\
        \nIf no points are selected, symmetry will be defined by two points closest to x=0 axis."
    bl_options = {"REGISTER", "UNDO"}

    positive_x: bpy.props.BoolProperty(name='Use Positive X', default=True)

    def copy_bezier_point_flip(self, source_point, receiver_point, flip=False):
        ''' Copy point with form right to left, or just ordinary copy (no flip)'''
        receiver_point.co = source_point.co
        if flip:
            receiver_point.co.x *= -1

            receiver_point.handle_left_type = source_point.handle_right_type
            receiver_point.handle_left = source_point.handle_right
            receiver_point.handle_left.x *= -1

            receiver_point.handle_right_type = source_point.handle_left_type
            receiver_point.handle_right = source_point.handle_left
            receiver_point.handle_right.x *= -1

        else:
            receiver_point.handle_left = source_point.handle_left
            receiver_point.handle_left_type = source_point.handle_left_type

            receiver_point.handle_right = source_point.handle_right
            receiver_point.handle_right_type = source_point.handle_right_type

    def copy_bezier_point_sym(self, source_point, receiver_point, flip=False):
        ''' Copy point with symmetrical left and right handle'''
        receiver_point.co = source_point.co
        if flip:
            receiver_point.handle_left_type = source_point.handle_left_type
            receiver_point.handle_left = source_point.handle_left

            receiver_point.handle_right_type = source_point.handle_left_type
            receiver_point.handle_right = source_point.handle_left
            receiver_point.handle_right.x *= -1

        else:
            receiver_point.handle_left_type = source_point.handle_right_type
            receiver_point.handle_left = source_point.handle_right
            receiver_point.handle_left.x *= -1

            receiver_point.handle_right_type = source_point.handle_left_type
            receiver_point.handle_right = source_point.handle_right
            
        if receiver_point.handle_left_type in {'ALIGNED', 'AUTO'}:
            receiver_point.handle_left.y = receiver_point.co.y
        if receiver_point.handle_right_type in {'ALIGNED', 'AUTO'}:
                receiver_point.handle_right.y = receiver_point.co.y


    def find_two_center_points(self, active_spline):
        kd = mathutils.kdtree.KDTree(len(active_spline.bezier_points))  # for marging adding
        for i, point in enumerate(active_spline.bezier_points):
            kd.insert(Vector((point.co.x, 0, 0)), i)
            point.select_control_point = False
        kd.balance()
        for (co, index, dist) in kd.find_n(Vector((0, 0, 0)), 2):
            if dist < 0.2:
                active_spline.bezier_points[index].select_control_point = True
        sel_points_idx = [i for (i, b_point) in enumerate(active_spline.bezier_points) if b_point.select_control_point]
        return len(sel_points_idx) == 2


    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE')

    def execute(self, context):
        for obj in context.selected_objects:
            selObj = obj
            if selObj.type != 'CURVE':
                self.report({'INFO'}, 'Select curve type of object! Skipping')
                continue
            orig_spline = selObj.data.splines[0]

            if not self.find_two_center_points(orig_spline):
                self.report({'INFO'}, 'Cant find points for mirroring axis. Move 2 points close to center of X axis. Skipping')
                continue

            # get two selected points (point_id, point)
            sel_points_idx = [i for (i, b_point) in enumerate(orig_spline.bezier_points) if b_point.select_control_point]
            orig_spline_len = len(orig_spline.bezier_points)

            # so get distance a <-> b, and b-len(x)  <-> 0-a
            points_a_b = OrderedDict()  # get  points from <a+1 , b-1>  spline loop
            i = sel_points_idx[0]+1
            while (i % orig_spline_len != sel_points_idx[1]):
                points_a_b[i % orig_spline_len] = orig_spline.bezier_points[i % orig_spline_len].co
                i += 1

            points_b_a = OrderedDict()  # get  points from <b+1 ,a-1 > to  spline loop
            i = sel_points_idx[1]+1
            while (i % orig_spline_len != sel_points_idx[0]):
                points_b_a[i % orig_spline_len] = orig_spline.bezier_points[i % orig_spline_len].co
                i += 1

            orig_spline.bezier_points[sel_points_idx[0]].co.x = 0
            orig_spline.bezier_points[sel_points_idx[1]].co.x = 0

            flip = 1 if self.positive_x else -1
            if not points_a_b:  # there are no points between <a, b> selection, so no need to delete
                remove_points_ids = set() #no need to remove anything
                first_loop_point = sel_points_idx[1] if sel_points_idx[1]>sel_points_idx[0] and sel_points_idx[1]!=orig_spline_len-1 else sel_points_idx[0]
                backup_removed_points_ids = []
            elif all([flip*point_co.x < 0 for point_co in points_a_b.values()]):  # delete all points from <a,b> if they are all on left
                remove_points_ids = set(points_a_b.keys())
                first_loop_point = sel_points_idx[1] #use B for <a,b>
                backup_removed_points_ids = list(points_a_b.keys()) #from OrderedDict
            elif all([flip*point_co.x < 0 for point_co in points_b_a.values()]):  # else delete all points from <b,a> if they are all on left
                remove_points_ids = set(points_b_a.keys())
                first_loop_point = sel_points_idx[0]  #use A for <b,a>
                backup_removed_points_ids = list(points_b_a.keys())#from OrderedDict
            else:
                self.report({'INFO'}, 'No two points are not defining symmetry axis! Skipping')
                continue
            old_spline_cleared_li = [i for i in range(orig_spline_len) if i not in remove_points_ids]

            new_spline = selObj.data.splines.data.splines.new("BEZIER")
            mirrored_spline_len = 2*len(old_spline_cleared_li) - 2  # new polyline len is: old_spline_cleared_li + old_spline_cleared_li - 2
            new_spline.bezier_points.add(count=mirrored_spline_len - 1)  # (-1 co this how blender rolls)

            i = old_spline_cleared_li.index(first_loop_point) #get idx of old spline point from cleaned_spline_point_list
            receiver_idx = 0
            cleared_point_count = len(old_spline_cleared_li)
            old_new_sewing_map = {}
            while receiver_idx < cleared_point_count: #copy points that are left on right side. Start by first_loop_point
                src_pt_idx = old_spline_cleared_li[i] #get original point idx from cleaned_spline_point_list
                if receiver_idx != src_pt_idx:
                    old_new_sewing_map[src_pt_idx] = receiver_idx
                if receiver_idx == 0 or receiver_idx == cleared_point_count-1:
                    self.copy_bezier_point_sym(source_point=orig_spline.bezier_points[src_pt_idx], receiver_point=new_spline.bezier_points[receiver_idx])
                else:
                    self.copy_bezier_point_flip(source_point=orig_spline.bezier_points[src_pt_idx], receiver_point=new_spline.bezier_points[receiver_idx])
                receiver_idx +=1
                i = (i+1)%len(old_spline_cleared_li)
            
            i -=2 #go back to first_loop_pointn-1 point for source for point on left.
            i_backup = 0
            while receiver_idx < 2*cleared_point_count - 2: #copy point on left
                src_pt_idx = old_spline_cleared_li[i]
                if i_backup < len(backup_removed_points_ids):
                    if receiver_idx != src_pt_idx:
                        # backup_removed_points_ids[i_backup] - get sewing idx from list of removed points <A,b) or (a,B>
                        old_new_sewing_map[backup_removed_points_ids[i_backup]] = receiver_idx
                self.copy_bezier_point_flip(source_point=orig_spline.bezier_points[src_pt_idx], receiver_point=new_spline.bezier_points[receiver_idx], flip=True)
                i = (i-1)%len(old_spline_cleared_li)
                receiver_idx +=1
                i_backup += 1

            remap_sewing(context, selObj, old_new_sewing_map)
            #TODO: remove sewing from old_spline for points_id > mirrored_spline_len: maybe map them old: -1 ?
                
            new_spline.use_cyclic_u = True
            selObj.data.splines.data.splines.remove(orig_spline)
        return {'FINISHED'}


class GTOOL_OT_PatternFlip(bpy.types.Operator):
    bl_idname = "curve.pattern_flip"
    bl_label = "Flip Pattern"
    bl_description = "Mirrors selected curve pattern around x axis.\
        \nIf you used this operation for second time, the mirroed copy will have its posiiton updated.\
        \nUse F6 to access additional options"
    bl_options = {"REGISTER", 'UNDO'}

    use_3dCursor: bpy.props.BoolProperty(name="Use 3d Cursor", default=False)
    clone: bpy.props.BoolProperty(name="Create duplicate", default=True)
    flip_axis: bpy.props.EnumProperty(name="Flip Axis", description="", default="X",
                                       items=(("X", "X", ""),
                                              ("Y", "Y", ""),
                                              ("Z", "Z", "")
                                              ))

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def execute(self, context):
        for obj in context.selected_objects:
            clone = None
            if self.clone:
                if is_name_r_l(obj.name):
                    mirrored_name = get_mirrored_name(obj.name)
                    if mirrored_name in context.scene.objects.keys():
                        clone = bpy.data.objects[mirrored_name]
                    else:
                        clone = obj.copy()
                        link_to_collection_sibling(obj, clone)
                        clone.name = mirrored_name
                else:
                    obj.name = obj.name + '.r'
                    clone = obj.copy()
                    link_to_collection_sibling(obj, clone)
                    clone.name = obj.name[:-2] + '.l'
                    
            matForFlip = Matrix.Identity(4)
            objMat = deepcopy(obj.matrix_world)
            i = 0
            if self.flip_axis == 'X':
                i = 0
            if self.flip_axis == 'Y':
                i = 1
            if self.flip_axis == 'Z':
                i = 2
            matForFlip[i][i] = -matForFlip[i][i]  # flix scale in x -1 to get mirror (local space)

            if self.use_3dCursor:
                cursorLoc = context.scene.cursor.location
                matForFlip[i][3] = cursorLoc[i]  # flip loc
                objMat[i][3] = objMat[i][3] - cursorLoc[i]  # if 3d cursor flip
            if clone is not None:
                clone.matrix_world = matForFlip@objMat  # mirror in local space @ to obj space
                clone.select_set(False)
            else:
                obj.matrix_world = matForFlip@objMat  # mirror in local space @ to obj space
        return {"FINISHED"}


class GTOOL_OT_SplitPattern(bpy.types.Operator):
    bl_label = "Split"
    bl_idname = "curve.curve_split_gm"
    bl_description = "Split curve pattern into two objects, by two selected points"
    bl_options = {"REGISTER", "UNDO"}

    instance: bpy.props.BoolProperty(name='Mirror instance', default=False)
    flip: bpy.props.BoolProperty(name='Flip', default=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, 'instance')
        if self.instance:
            row.prop(self, 'flip')
        else:
            self.flip = False

    @staticmethod
    def spline_remove_point(obj, points_ids):
        ''' remov points froom obj while mantaining selection state'''
        spline = obj.data.splines[0]
        backup_mode = obj.mode
        bpy.context.view_layer.objects.active = obj

        # remove points from points_ids by selecting them and dissolve
        for p in spline.bezier_points:
            p.select_control_point = False
            p.select_left_handle = False
            p.select_right_handle = False
        for point_id in points_ids:
            spline.bezier_points[point_id].select_control_point = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.delete(type='VERT')
        bpy.ops.object.mode_set(mode=backup_mode)  # we loose spline after going in and out of edit mode

        spline.bezier_points.update()
        spline = obj.data.splines[0]
        # restore  selection from backup


    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE')

    def execute(self, context):
        selObj = context.active_object
        if selObj.type != 'CURVE':
            self.report({'INFO'}, 'Select curve type of object! Cancelling')
            return {'CANCELLED'}

        if not len([p for p in selObj.data.splines[0].bezier_points if p.select_control_point]) == 2:
            self.report({'INFO'}, 'Select two points to split curve pattern! Cancelling')
            return {'CANCELLED'}
        bpy.ops.object.editmode_toggle() #to kindow update spline form edit mode
        bpy.ops.object.editmode_toggle()

        clone = selObj.copy() #copy object 
        clone.data = selObj.data.copy() #and its data
        clone.matrix_world = selObj.matrix_world
        link_to_collection_sibling(selObj, clone)
        if self.instance:
            clone.name = selObj.name+'.l'
            selObj.name = selObj.name+'.r'

        # get two selected points (point_id, point)
        active_spline = selObj.data.splines[0]
        orig_spline_len = len(active_spline.bezier_points)
        sel_points_idx = [i for (i, b_point) in enumerate(active_spline.bezier_points) if b_point.select_control_point]
        if self.instance and self.flip:
            sel_points_idx = list(reversed(sel_points_idx))
        spline_len = len(active_spline.bezier_points)

        # so get distance a <-> b, and b-len(x)  <-> 0-a
        points_a_b = []  # get  points from <a+1 , b-1>  spline loop
        i = sel_points_idx[0]+1
        while (i % spline_len != sel_points_idx[1]):
            points_a_b.append(i % spline_len)
            i += 1

        points_b_a = []  # get  points from <b+1 ,a-1 > to  spline loop
        i = sel_points_idx[0]-1
        while (i % spline_len != sel_points_idx[1]):
            points_b_a.append(i % spline_len)
            i -= 1
        if not points_a_b or not points_b_a:  # there are no points between <a, b>  or <b,a> selection
            self.report({'INFO'}, 'No points between selected verts. Cancelling' )
            return {'CANCELLED'}

        clone.data.splines[0].bezier_points[sel_points_idx[0]].handle_left_type = 'VECTOR'
        clone.data.splines[0].bezier_points[sel_points_idx[0]].handle_right_type = 'VECTOR'
        selObj.data.splines[0].bezier_points[sel_points_idx[0]].handle_right_type = 'VECTOR'
        selObj.data.splines[0].bezier_points[sel_points_idx[0]].handle_left_type = 'VECTOR'
        clone.data.splines[0].bezier_points[sel_points_idx[1]].handle_left_type = 'VECTOR'
        clone.data.splines[0].bezier_points[sel_points_idx[1]].handle_right_type = 'VECTOR'
        selObj.data.splines[0].bezier_points[sel_points_idx[1]].handle_right_type = 'VECTOR'
        selObj.data.splines[0].bezier_points[sel_points_idx[1]].handle_left_type = 'VECTOR'

        bpy.ops.object.mode_set(mode='OBJECT')
        instances = [selObj.name for obj in bpy.data.objects if obj.data == selObj.data] #for finding patterns that were using splited pattern geo


        self.spline_remove_point(selObj, points_a_b)
        orig_spline_ids = {i for i in range(orig_spline_len)}
        old_spline_cleared = orig_spline_ids - set(points_a_b)  # map new ids to old ids by removing <a,b)
        old_new_map_id_b_a = {old: i for i, old in enumerate(old_spline_cleared) if old != sel_points_idx[0]}  # old vert_id : new_ver_id
        #calc split (middle) segment id for new sewing
        split_segment_id = {old: i for i, old in enumerate(old_spline_cleared) if old == sel_points_idx[0]}

        self.spline_remove_point(clone, points_b_a)
        old_spline_cleared2 = orig_spline_ids - set(points_b_a)  # map new ids to old ids by removing (b,a>
        old_new_map_id_a_b = {old: i for i, old in enumerate(old_spline_cleared2) if old != sel_points_idx[1]}  # old vert_id : new_ver_id
        #calc split segment id for new sewing
        split_segment_id2 = {old: i for i, old in enumerate(old_spline_cleared2) if old == sel_points_idx[1]}  # old vert_id : new_ver_id
 
        def remap_sewings(old_new_map_id_b_a, old_new_map_id_a_b):
            garment_using_sel_obj = -1
            for i,garment in enumerate(context.scene.cloth_garment_data):  # remap sewing that are assigned to the left segment of revemoved points
                for idx, sewing in enumerate(garment.garment_sewings):
                    #check for firs segment
                    if sewing.source_obj.name in instances:
                        if sewing.segment_id_from in old_new_map_id_b_a.keys():
                            sewing.segment_id_from = old_new_map_id_b_a[sewing.segment_id_from]
                            garment_using_sel_obj = i
                        #check for second segment
                        elif sewing.segment_id_from in old_new_map_id_a_b.keys():
                            sewing.source_obj = clone #map old pattern to clone
                            sewing.segment_id_from = old_new_map_id_a_b[sewing.segment_id_from]
                            garment_using_sel_obj = i
                            if self.instance:
                                sewing.flip = not sewing.flip
                    if sewing.target_obj.name in instances:
                        if sewing.segment_id_to in old_new_map_id_b_a.keys():
                            sewing.segment_id_to = old_new_map_id_b_a[sewing.segment_id_to]
                            garment_using_sel_obj = i
                        #check for second segment
                        elif sewing.segment_id_to in old_new_map_id_a_b.keys():
                            sewing.target_obj = clone  # map old pattern to clone
                            sewing.segment_id_to = old_new_map_id_a_b[sewing.segment_id_to]
                            garment_using_sel_obj = i
                            if self.instance:
                                sewing.flip = not sewing.flip

                #DONE: connect sewing sel_points_idx[0] from sel_obj and sel_points_idx[1] from clone FIX it
                if garment_using_sel_obj >- 1:
                    garment = context.scene.cloth_garment_data[garment_using_sel_obj]
                    garment.sewing_patterns.add()
                    garment.sewing_patterns[-1].pattern_obj = clone
                    garment.garment_sewings.add()
                    garment.garment_sewings[-1].source_obj = selObj
                    garment.garment_sewings[-1].segment_id_from = split_segment_id[sel_points_idx[0]]
                    garment.garment_sewings[-1].target_obj = clone
                    if self.instance:
                        garment.garment_sewings[-1].segment_id_to = split_segment_id[sel_points_idx[0]]
                    else:
                        garment.garment_sewings[-1].segment_id_to = split_segment_id2[sel_points_idx[1]]
                        garment.garment_sewings[-1].flip = True

        
        # set patterns(middle) for second splited part
        if not self.instance:
            remap_sewings(old_new_map_id_b_a, old_new_map_id_a_b)
        else: #make it work like flip?? So instance data, flip matrix, and remap sewing - assuming left and right split, have same ids (instaced)
            clone.data = selObj.data #and its data
            matForFlip = Matrix.Identity(4)
            objMat = deepcopy(selObj.matrix_world)
            i = 0
            matForFlip[i][i] = -matForFlip[i][i]  # flix scale in x -1 to get mirror (local space)
            clone.matrix_world = matForFlip @ selObj.matrix_world
            old_ids_1 = list(old_spline_cleared)  # old_ids_1 - contains ids, from instance source (right slice)
            old_ids_2 = list(old_spline_cleared2) # old_ids_2 - contains ids, from left (removed) slice (replaced by mirror instance)
            start_idx1 = old_ids_1.index(sel_points_idx[0])
            start_idx2 = old_ids_2.index(sel_points_idx[0])  

            i = start_idx2
            map_old_left_to_instance = {}
            #DONE: what if left if longer than right or viceversa
            #DONE: remove 4-9 - sewing point from remap on instance left
            ONE = 0 if self.instance and self.flip else 1  #when flipping instance,  cos reasons
            for count in range(max(len(old_ids_2), len(old_ids_1))-1): # -1 to skip split sewing
                left_old2_idx = old_ids_2[i % len(old_ids_2)]
                instance_idx = old_ids_1[(start_idx1 - i - ONE) % len(old_ids_1)] 
                map_old_left_to_instance[left_old2_idx] = instance_idx  # remap  old left to new instance idx
                i += 1
            #right now map_old_left_to_instance values (new_ids), are mapped to original spline. Remap it to right split half (ids <= len(right_half))
            for old_left_id, new_id in map_old_left_to_instance.items(): #remap right ids, to new_right ids (so eg. it wont go above half orig_spline_len)
                if new_id in old_new_map_id_b_a.keys():
                    map_old_left_to_instance[old_left_id] = old_new_map_id_b_a[new_id]

            remap_sewings(old_new_map_id_b_a, map_old_left_to_instance)
        
        return {'FINISHED'}


class GTOOL_OT_DeletePoint(bpy.types.Operator):
    bl_label = "Delete Vert GT"
    bl_idname = "curve.curve_del_vert_gt"
    bl_description = "Delete Vert from GT - prevents moving sewings after removing curve points"
    bl_options = {"REGISTER", "UNDO"}
    ''' delete sewing left to selected points, substract segment_idx for each removed point for sewing right to it '''

    #Running this from F3 always works cos init properly reads the garment sewing
    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE')

    def execute(self, context):
        selObj = context.active_object
        active_spline = selObj.data.splines[0]
        spline_len = len(active_spline.bezier_points)
        
        sel_points_idx = [i for (i, b_point) in enumerate(active_spline.bezier_points) if b_point.select_control_point]
        removed_segments = [(i-1) % spline_len for (i, point) in enumerate(active_spline.bezier_points) if i in sel_points_idx]
        remap_segments = {}  # old_seg_idx : new_seg_idx  for sewing that need to be remapped

        output_seg_count = spline_len - len(sel_points_idx)
        k = 0 # output segment indx
        for i in range(spline_len):
            if active_spline.bezier_points[i].select_control_point:
                remap_segments[i] = (k-1) % output_seg_count  # assign sewingt to the new segment made form 2segments (left and right to vert)
            else:
                remap_segments[i] = k  #assign sewingt to the new segment made form 2segments (left and right to vert)
                k +=1
        
        bpy.ops.curve.delete(type='VERT')
        instances = [obj.name for obj in bpy.data.objects if obj.data == selObj.data]

        garments = context.scene.cloth_garment_data
        sewing_to_remove = [] #per garment
        for garment in garments: #remove sewing that are assigned to the left segment of revemoved points
            sewing_to_remove.clear()
            for idx, sewing in enumerate(garment.garment_sewings):
                if (sewing.source_obj.name in instances and sewing.segment_id_from in removed_segments) or (sewing.target_obj.name in instances and sewing.segment_id_to in removed_segments):
                    sewing_to_remove.append(idx)
            
            for idx in reversed(sewing_to_remove):
                self.report({'INFO'}, 'Remove sewing with no segment assigned: ' + str(idx))
                garment.garment_sewings.remove(idx)
        
        for garment in garments:  # remap sewing that are assigned to the left segment of revemoved points
            for idx, sewing in enumerate(garment.garment_sewings):
                if sewing.source_obj.name in instances:
                    sewing.segment_id_from = remap_segments[sewing.segment_id_from]
                if sewing.target_obj.name in instances:
                    sewing.segment_id_to = remap_segments[sewing.segment_id_to]

        return {'FINISHED'}


class GTOOL_OT_SubdivideSegment(bpy.types.Operator):
    bl_label = "Subdivide Segments GT"
    bl_idname = "curve.curve_subdivide_gt"
    bl_description = "Subdivide segments while preserving garment sewing from moving"
    bl_options = {"REGISTER", "UNDO"}

    number_cuts : bpy.props.IntProperty(name='Number of cuts', default=1)

    #Running this from F3 always works cos init properly reads the garment sewing
    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE')

    def execute(self, context):
        selObj = context.active_object
        active_spline = selObj.data.splines[0]
        spline_len = len(active_spline.bezier_points)
        
        sel_segments = []
        prev_point_select = active_spline.bezier_points[-1].select_control_point
        for i,point in enumerate(active_spline.bezier_points):
            if point.select_control_point == prev_point_select and prev_point_select is True:
                sel_segments.append((i-1) % spline_len)  # add segment i-1 for points i - 1 and i
            prev_point_select = point.select_control_point
        
        remap_segments = {}  # old_seg_idx : new_seg_idx  for sewing that need to be remapped
        k = 0 # output segment indx
        for i in range(spline_len):
            remap_segments[i] = k   # assign sewingt to the new segment made form 2segments (left and right to vert)
            if i in sel_segments:
                #TODO: maybe (k+self.number_cuts+1 ) % len.segmetns??
                k += self.number_cuts+1 #adwance output segments by +1 + numb_of_cuts
            else:
                k += 1  # adwance output segments by +1
        
        bpy.ops.curve.subdivide('INVOKE_DEFAULT', number_cuts=self.number_cuts)

        instances = [obj.name for obj in bpy.data.objects if obj.data == selObj.data]
        garments = context.scene.cloth_garment_data
        for g_idx, garment in enumerate(garments):   # remap sewing that are assigned to the left segment of revemoved points
            for s_idx, sewing in enumerate(garment.garment_sewings):
                if sewing.source_obj and sewing.target_obj:
                    if sewing.source_obj.name in instances:
                        sewing.segment_id_from = remap_segments[sewing.segment_id_from]
                    if sewing.target_obj.name in instances:
                        sewing.segment_id_to = remap_segments[sewing.segment_id_to]
            
        return {'FINISHED'}




class GTOOL_OT_DuplicateSewed(bpy.types.Operator):
    bl_label = "Duplicate Sewed"
    bl_idname = "curve.duplicate_sewed"
    bl_description = "Duplicate pattern and sew it to original pattern, if selection belongs to garment"
    bl_options = {"REGISTER", "UNDO"}

    instance: bpy.props.BoolProperty(name='Instance', description = 'Generate pattern instance vs copy', default=True)

    @classmethod
    def poll(cls, context):
        return (context.active_object and context.active_object.type == 'CURVE')
        
    def execute(self, context):
        selObj = context.active_object
        selObj.select_set(False)

        sel_obj_instance = selObj.copy()
        if not self.instance:
            sel_obj_instance.data = selObj.data.copy()
        link_to_collection_sibling(selObj, sel_obj_instance)
        sel_obj_instance.select_set(True)
        sel_obj_instance.matrix_world = sel_obj_instance.matrix_world

        active_spline = selObj.data.splines[0]
        spline_len = len(active_spline.bezier_points)

        garment_using_active_ob = None
        for garment in context.scene.cloth_garment_data:
            existing_patterns = [g_mesh.pattern_obj.name for g_mesh in garment.sewing_patterns if g_mesh.pattern_obj]
            if selObj.name in existing_patterns:  # find garments  that are using active_obj
                for i in range(spline_len):
                    garment.garment_sewings.add()
                    garment.garment_sewings[-1].source_obj = selObj
                    garment.garment_sewings[-1].target_obj = sel_obj_instance
                    garment.garment_sewings[-1].segment_id_from = i
                    garment.garment_sewings[-1].segment_id_to = i
                
                garment.sewing_patterns.add()
                garment.sewing_patterns[-1].pattern_obj = sel_obj_instance
                continue

        return {'FINISHED'}

