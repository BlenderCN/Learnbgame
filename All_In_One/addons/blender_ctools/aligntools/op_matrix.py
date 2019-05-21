# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import itertools

import bpy
import bpy.utils.previews

from mathutils import Matrix, Quaternion, Vector

from . import funcs
from . import memocoords
from . import tooldata
from .va import manipulatormatrix
from .op_template import *
from .enums import *
from .va import vaobject as vaob
from .va import vaarmature as vaarm


tool_data = tooldata.tool_data
memoize = tool_data.memoize


class OperatorManipulatorSetA(OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.manipulator_set_a'
    bl_label = 'Set Manipulator A'
    bl_description = 'Set manipulator A'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return manipulatormatrix.ManipulatorMatrix.poll(context)

    def execute(self, context):
        mmat = memocoords.manipulator_matrix(context)
        mmat.update(context, view_only=True, cursor_only=True)
        tool_data.matrix_a = Matrix(mmat)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class OperatorManipulatorSetB(OperatorTemplate, bpy.types.Operator):
    bl_idname = 'at.manipulator_set_b'
    bl_label = 'Set Manipulator B'
    bl_description = 'Set manipulator B'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return manipulatormatrix.ManipulatorMatrix.poll(context)

    def execute(self, context):
        mmat = memocoords.manipulator_matrix(context)
        mmat.update(context, view_only=True, cursor_only=True)
        tool_data.matrix_b = Matrix(mmat)
        return {'FINISHED'}


class OperatorManipulatorAtoB(OperatorTemplateModeSave,
                              OperatorTemplateGroup, bpy.types.Operator):
    bl_idname = 'at.manipulator_a_to_b'
    bl_label = 'Manipulator A to B'
    bl_description = 'Apply manipulator difference'
    bl_options = {'REGISTER', 'UNDO'}

    space = bpy.props.EnumProperty(
        name='Space',
        items=orientation_enum_items(),
        default='GLOBAL')
    mode = bpy.props.EnumProperty(
        name='Mode',
        items=(('A_TO_B', 'A to B', ''),
               ('TO_A', 'to A', 'Align to Manipulator A'),
               ('TO_B', 'to B', 'Align to Manipulator B')),
        default='A_TO_B')
    transform_mode = bpy.props.EnumProperty(
        name='Transform',
        items=(('TRANSLATE', 'Translate', ''),
               ('ROTATE', 'Rotate', ''),
               # ('ROTATE_RESIZE', 'Rotate & Resize', 'Apply matrix 3x3'),
               ('ALL', 'All', 'Apply translation and rotation')),
        default='TRANSLATE')
    use_relative_transform = bpy.props.BoolProperty(
        name='Relative',
        description='if disabled, base orientation is Manipulator A',
    )

    influence = bpy.props.FloatProperty(
        name='Influence',
        default=1.0,
        step=1,
        precision=3,
        soft_min=0.0,
        soft_max=1.0,
        subtype='NONE'
    )

    # show_expand_transform = bpy.props.BoolProperty()
    # show_expand_others = bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE'}

    def execute(self, context):
        bpy.ops.at.fix()
        memocoords.cache_init(context)
        groups = self.groups = self.make_groups(context)
        if not groups:
            return {'FINISHED'}

        a = tool_data.matrix_a
        b = tool_data.matrix_b

        if self.mode == 'A_TO_B':
            a_loc = a.to_translation()
            b_loc = b.to_translation()
            a_ = a.to_3x3().to_4x4()
            b_ = b.to_3x3().to_4x4()
            if self.use_relative_transform:
                # aの座標系における相対的な行列を求める。 (inv_a * b) = m * (inv_a * a)
                m = a.inverted() * b
            else:
                # b = m * a; b * inv_a = m
                tmat = Matrix.Translation(b_loc - a_loc)
                m = tmat * b_ * a_.inverted()
            if self.transform_mode == 'TRANSLATE':
                matrix = Matrix.Translation(m.to_translation())
            elif self.transform_mode == 'ROTATE':
                matrix = m.normalized().to_quaternion().to_matrix().to_4x4()
            # elif self.transform_mode == 'ROTATE_RESIZE':
            #     matrix = m.copy()
            #     matrix.col[3][:] = [0, 0, 0, 1]
            else:
                # matrix = m.copy()
                matrix = m.normalized().to_quaternion().to_matrix().to_4x4()
                matrix.col[3][:3] = m.col[3][:3]
        else:
            # groupの4x4逆行列を掛けた後でこの行列を適用する
            m = a if self.mode == 'TO_A' else b
            if self.transform_mode == 'TRANSLATE':
                matrix = Matrix.Translation(m.to_translation())
            elif self.transform_mode == 'ROTATE':
                matrix = m.normalized().to_quaternion().to_matrix().to_4x4()
            # elif self.transform_mode == 'ROTATE_RESIZE':
            #     matrix = m.copy()
            #     matrix.col[3][:] = [0, 0, 0, 1]
            else:
                matrix = m.normalized().to_quaternion().to_matrix().to_4x4()
                matrix.col[3][:3] = m.col[3][:3]

        def applied_influence(matrix, group_matrix=None):
            q = matrix.to_3x3().to_quaternion()
            loc = matrix.to_translation()
            if self.mode == 'A_TO_B':
                q0 = Quaternion([1, 0, 0, 0])
                loc0 = Vector()
            else:
                q0 = group_matrix.to_quaternion()
                if self.transform_mode == 'TRANSLATE':
                    q = q0.copy()
                if self.transform_mode in {'ALL', 'TRANSLATE'}:
                    loc0 = group_matrix.to_translation()
                else:
                    loc0 = Vector()
            q = q * self.influence + q0 * (1.0 - self.influence)
            loc = loc * self.influence + loc0 * (1.0 - self.influence)
            mat = q.to_matrix().to_4x4()
            mat.col[3][:3] = loc
            return mat

        matrices = {}
        for group in groups:
            if self.mode == 'A_TO_B':
                space = Space.get(self.space)
            else:
                space = Space.NORMAL
            omat = group.get_orientation(context, space)
            if not omat:
                matrices[group] = Matrix.Identity(4)
                continue

            if self.mode == 'A_TO_B':
                m1 = Matrix.Translation(-group.pivot)
                m2 = Matrix.Translation(group.pivot)
                omat = omat.to_4x4()
                oimat = omat.inverted()
                mat = applied_influence(matrix)
                matrices[group] = m2 * omat * mat * oimat * m1
            else:
                group_mat = Matrix.Translation(group.pivot) * omat.to_4x4()
                mat = applied_influence(matrix, group_mat)
                m = mat * group_mat.inverted()
                if self.transform_mode in {'ROTATE', 'ROTATE_RESIZE'}:
                    m = Matrix.Translation(group.pivot) * m
                matrices[group] = m

        groups.transform(context, matrices,
                         reverse=self.individual_orientation)

        if context.mode == 'OBJECT':
            objects = [bpy.data.objects[name]
                       for name in itertools.chain.from_iterable(groups)]
        else:
            objects = [context.active_object]
        funcs.update_tag(context, objects)

        return {'FINISHED'}

    def draw(self, context):
        # Transform
        box = self.draw_box(self.layout, 'Transform', '')
        column = box.column()
        self.draw_property('mode', column)
        self.draw_property('transform_mode', column)
        if self.mode == 'A_TO_B':
            self.draw_property('use_relative_transform', column)
            self.draw_property('space', column)

        column = box.column()
        if self.mode == 'A_TO_B':
            space = self.space
        else:
            space = 'NORMAL'
        column.active = self.groups and self.is_valid_individual_orientation(
            space, self.groups.Group)
        self.draw_property('individual_orientation', column)

        # Groups
        self.draw_group_boxes(context, self.layout)

        # Others
        # box = self.draw_box(self.layout, 'Others', 'show_expand_others')
        box = self.draw_box(self.layout, 'Others', '')
        column = box.column()
        self.draw_property('influence', column)


def transform_edit_bone(bone, matrix, scale=True, roll=True):
    """
    Transform the the bones head, tail, roll and envelope
    (when the matrix has a scale component).

    :type bone: bpy.types.EditBone
    :arg matrix: 3x3 or 4x4 transformation matrix.
       3x3を渡すとheadを原点として回転・拡大縮小を行う
    :type matrix: :class:`mathutils.Matrix`
    :arg scale: Scale the bone envelope by the matrix.
    :type scale: bool
    :arg roll:

       Correct the roll to point in the same relative
       direction to the head and tail.

    :type roll: bool
    """
    from mathutils import Vector
    z_vec = bone.matrix.to_3x3() * Vector((0.0, 0.0, 1.0))
    if len(matrix) == 4:
        bone.tail = matrix * bone.tail
        bone.head = matrix * bone.head
    else:
        bone.tail = matrix * (bone.tail - bone.head) + bone.head

    if scale:
        scalar = matrix.median_scale
        bone.head_radius *= scalar
        bone.tail_radius *= scalar

    if roll:
        bone.align_roll(matrix.to_3x3() * z_vec)


class OperatorManipulatorAlign(OperatorTemplateModeSave, bpy.types.Operator):
    # space_view3d_copy_attributes.pyを参考にした

    bl_idname = 'at.manipulator_align'
    bl_label = 'Align to'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO'}

    target = bpy.props.EnumProperty(
        name='Target',
        items=[('ACTIVE', 'Active', ''),
               ('MANIPUL', 'Manipulator', ''),
               ('MANIPUL_A', 'Manipulator A', ''),
               ('MANIPUL_B', 'Manipulator B', '')],
        default='ACTIVE',
    )
    location = bpy.props.BoolProperty(
        name='Location',
        default=True,
    )
    rotation = bpy.props.BoolProperty(
        name='Rotation',
        default=True,
    )
    scale = bpy.props.BoolProperty(
        name='Scale',
        default=True,
    )

    inherit_location = bpy.props.BoolProperty(
        name='Inherit Location',
        description='Inherit translation from parent',
        default=True,
    )
    inherit_rotation = bpy.props.BoolProperty(
        name='Inherit Rotation',
        description='Inherit rotation from parent',
        default=True,
    )

    @classmethod
    def poll(self, context):
        return context.mode in {'OBJECT', 'POSE', 'EDIT_ARMATURE'}

    def to_basis_matrix(self, ob):
        if ob.parent:
            m = ob.parent.matrix_world
            return ob.matrix_basis * ob.matrix_local.inverted() * m.inverted()
        else:
            return Matrix.Identity(4)

    def to_pose_bone_matrix(self, pbone, ignoreparent):
        """Helper function for visual transform copy,
           gets the active transform in bone space
        """
        ob = pbone.id_data
        obmat = ob.matrix_world
        bone = pbone.bone
        bone_mat = bone.matrix_local
        if bone.parent and not ignoreparent:
            parent_pbone_mat = pbone.parent.matrix
            parent_bone_mat = bone.parent.matrix_local
            mat = parent_bone_mat.inverted() * bone_mat
            new_mat = (mat.inverted() * parent_pbone_mat.inverted() *
                       obmat.inverted())
        else:
            new_mat = bone_mat.inverted() * obmat.inverted()
        return new_mat

    def copy_rotation(self, target, matrix):
        mat = matrix.to_3x3()
        if target.rotation_mode == 'QUATERNION':
            target.rotation_quaternion = mat.to_quaternion()
        elif target.rotation_mode == 'AXIS_ANGLE':
            rot = mat.to_quaternion().to_axis_angle()
            axis_angle = rot[1], rot[0][0], rot[0][1], rot[0][2]
            target.rotation_axis_angle = axis_angle
        else:
            target.rotation_euler = mat.to_euler(target.rotation_mode)

    def execute(self, context):
        bpy.ops.at.fix()
        memocoords.cache_init(context)

        if self.target == 'MANIPUL':
            manipul = memocoords.manipulator_matrix(context)
            tar_mat = Matrix(manipul)
        elif self.target == 'MANIPUL_A':
            tar_mat = tool_data.matrix_a
        elif self.target == 'MANIPUL_B':
            tar_mat = tool_data.matrix_b
        else:
            tar_mat = Matrix.Identity(4)

        actob = context.active_object
        if context.mode == 'OBJECT':
            if self.target == 'ACTIVE':
                if not actob or actob not in context.selected_objects:
                    return {'FINISHED'}
                tar_mat = actob.matrix_world

            for ob in vaob.sorted_dependency(context.selected_objects):
                if self.target == 'ACTIVE' and ob == actob:
                    continue
                mat = self.to_basis_matrix(ob) * tar_mat
                if self.location:
                    ob.location = mat.to_translation()
                if self.rotation:
                    self.copy_rotation(ob, mat)
                if self.scale:
                    ob.scale = mat.to_scale()

        elif context.mode == 'POSE':
            act_pbone = context.active_pose_bone
            if self.target == 'ACTIVE':
                if (not act_pbone or
                        act_pbone not in context.selected_pose_bones):
                    return {'FINISHED'}
                tar_mat = actob.matrix_world * act_pbone.matrix

            for pbone in vaob.sorted_dependency(context.selected_pose_bones):
                """:type: bpy.types.PoseBone"""
                if self.target == 'ACTIVE' and pbone == act_pbone:
                    continue
                if self.location:
                    ignore_parent = False
                    mat = self.to_pose_bone_matrix(pbone, ignore_parent)
                    mat = mat * tar_mat
                    pbone.location = mat.to_translation()
                if self.rotation:
                    ignore_parent = not pbone.bone.use_inherit_rotation
                    mat = self.to_pose_bone_matrix(pbone, ignore_parent)
                    mat = mat * tar_mat
                    self.copy_rotation(pbone, mat)
                if self.scale:
                    ignore_parent = not pbone.bone.use_inherit_scale
                    mat = self.to_pose_bone_matrix(pbone, ignore_parent)
                    mat = mat * tar_mat
                    pbone.scale = mat.to_scale()

        elif context.mode == 'EDIT_ARMATURE':
            act_bone = context.active_bone
            """:type: bpy.types.EditBone"""

            if self.target == 'ACTIVE':
                if not act_bone or act_bone not in context.selected_bones:
                    return {'FINISHED'}
                tar_mat_local = act_bone.matrix
            else:
                tar_mat_local = actob.matrix_world.inverted() * tar_mat

            def apply_recurcive(bone, offset, rot_mat, disconnected=False):
                for b in bone.children:
                    inherit_location = self.inherit_location
                    if connected[b]:
                        inherit_location = True
                    inherit_rotation = self.inherit_rotation

                    m1 = Matrix.Translation(b.head)
                    m2 = Matrix.Translation(offset)

                    tmat = Matrix.Identity(4)
                    if inherit_rotation:
                        tmat = m1 * rot_mat.to_4x4() * m1.inverted()
                    if inherit_location:
                        tmat = m2 * tmat

                    ofs = tmat * b.tail - b.tail
                    transform_edit_bone(b, tmat)
                    apply_recurcive(b, ofs, rot_mat,
                                    disconnected or not connected[b])

            connected = {b: b.use_connect for b in actob.data.edit_bones}
            for b in actob.data.edit_bones:
                b.use_connect = False

            for bone in vaob.sorted_dependency(context.selected_bones):
                """:type: bpy.types.EditBone"""
                if self.target == 'ACTIVE' and bone == act_bone:
                    continue
                mat = bone.matrix
                tmat = Matrix.Identity(4)
                rot_mat = Matrix.Identity(3)
                m1 = Matrix.Translation(mat.to_translation())
                m2 = Matrix.Translation(tar_mat_local.to_translation())
                if self.rotation:
                    rot_mat = tar_mat_local.to_3x3() * mat.to_3x3().inverted()
                    tmat = m1 * rot_mat.to_4x4() * m1.inverted()
                if self.location:
                    if not (bone.parent and connected[bone]):
                        tmat = m2 * m1.inverted() * tmat

                offset = tmat * bone.tail - bone.tail
                transform_edit_bone(bone, tmat)
                apply_recurcive(bone, offset, rot_mat)

            for b, connected in connected.items():
                b.use_connect = connected

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout.column()
        self.draw_property('target', layout)
        self.draw_property('location', layout)
        self.draw_property('rotation', layout)
        if context.mode != 'EDIT_ARMATURE':
            self.draw_property('scale', layout)
        if context.mode == 'EDIT_ARMATURE':
            self.draw_property('inherit_location', layout)
            self.draw_property('inherit_rotation', layout)


classes = [
    OperatorManipulatorSetA,
    OperatorManipulatorSetB,
    OperatorManipulatorAtoB,
    OperatorManipulatorAlign,
]
