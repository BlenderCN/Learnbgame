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


import functools

import bpy

import itertools

from .. import localutils
from ..localutils import utils


def sorted_objects(obs):
    """親から順に並べ替えたリストを返す。
    objectの他に、boneに対しても使用可。
    """
    # 階層の深さ順に並び替え
    def sort_key(ob, i=0):
        return i if not ob.parent else sort_key(ob.parent, i + 1)
    obs = sorted(obs, key=sort_key)

    # 親子関係で纏める。但し複数の子を持っている場合はそこで切る
    def group_key(a, b):
        return (len(b.children) == 1 and a.parent == b or
                len(a.children) == 1 and b.parent == a)
    groups = localutils.utils.groupwith(obs, group_key)

    return list(itertools.chain.from_iterable(groups))

    # if not ob_children:
    #     ob_parent = {ob: None for ob in obs}
    #     for ob in obs:
    #         if ob.parent in ob_parent:
    #             ob_parent[ob] = ob.parent
    #         else:
    #             # [parent] ob1 - ob9_not_obs - ob2 [child]
    #             tmp = ob.parent
    #             while tmp:
    #                 if tmp in ob_parent:
    #                     ob_parent[ob] = tmp
    #                     break
    #                 tmp = tmp.parent
    #
    #     ob_children = {ob: [] for ob in obs}
    #     for ob, parent in ob_parent.items():
    #         if parent:
    #             ob_children[parent].append(ob)
    #     obs = [ob for ob, parent in ob_parent.items() if not parent]
    #
    # for ob in obs:
    #     yield ob
    #
    #     for o in sorted_parent_and_child(ob_children[ob], ob_children):
    #         yield o


def object_children_recursive(ob, insert_none=False):
    """オブジェクトの全ての子をリストにして返す。
    :param ob: Object
    :param insert_none: if not object.children, return None
    """
    def object_children_re(ob, insert_none=False, _root=True):
        if not _root:
            yield ob
        for child in ob.children:
            for o in object_children_re(child, insert_none, False):
                yield o
        if not ob.children and insert_none:
            yield None
    return list(object_children_re(ob, insert_none))


###############################################################################
# Solve Dependence
###############################################################################
def _get_depend_on_parent(ob):
    """親Object(PoseBone/Bone/EditBone)を返す。
    PoseBoneの場合、親PoseBoneが無ければ所属するObjectを返す。
    Bone,EditBoneの場合は親Bone/EditBoneが無ければNoneを返す。
    :type ob: Object | PoseBone | Bone | EditBone
    :rtype: list
    """
    if ob.parent:
        if isinstance(ob, bpy.types.Object) and ob.parent_type == 'BONE':
            return ob.parent.pose.bones[ob.parent_bone]
        else:
            return ob.parent
    elif isinstance(ob, bpy.types.PoseBone):
        return ob.id_data  # bpy.types.Object
    else:
        return None


def _get_depend_on_constraints(ob):
    """
    :type ob: Object | PoseBone
    :rtype: list
    """
    targets = []

    for con in ob.constraints:
        if con.mute or not con.is_valid:
            continue

        t = con.type
        target1 = target2 = subtarget1 = subtarget2 = None
        # Motion Tracking
        if t == 'FOLLOW_TRACK':
            target1 = con.camera or bpy.context.scene.camera
            target2 = con.depth_object
        elif t == 'OBJECT_SOLVER':
            target1 = con.camera or bpy.context.scene.camera

        # Transform
        elif t in ('COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE',
                   'COPY_TRANSFORMS', 'LIMIT_DISTANCE', 'TRANSFORM'):
            target1 = con.target
            subtarget1 = con.subtarget

        # Tracking
        elif t == 'CLAMP_TO':
            target1 = con.target  # curves only
        elif t == ('DAMPED_TRACK', 'LOCKED_TRACK', 'STRETCH_TO',
                   'TRACK_TO'):
            target1 = con.target
        elif t == 'IK':  # PoseBone only
            target1 = con.target
            subtarget1 = con.subtarget
            target2 = con.pole_target
            subtarget2 = con.pole_subtarget
        elif t == 'SPLINE_IK':  # PoseBone only
            target1 = con.target  # curves only ?

        # Relationship
        elif t in ('ACTION', 'CHILD_OF', 'FLOOR', 'PIVOT'):
            target1 = con.target
            subtarget1 = con.subtarget
        elif t == 'FOLLOW_PATH':
            target1 = con.target  # curves only
        elif t == 'RIGID_BODY_JOINT':  # Object only
            target1 = con.target
            target2 = con.child
        elif t == 'SHRINKWRAP':
            target1 = con.target  # mesh only ?

        # append
        for tar, subtar in [[target1, subtarget1], [target2, subtarget2]]:
            if tar:
                if subtar:  # use PoseBone
                    if subtar in tar.pose.bones:
                        targets.append(tar.pose.bones[subtar])
                else:
                    targets.append(tar)

    return targets


def _get_depend_on_modifiers(ob):
    """
    :type ob: Object
    :rtype: list
    """
    targets = []

    for mod in ob.modifiers:
        if not mod.show_viewport:  # TODO: show_in_editmode, show_render
            continue

        mod_targets = []
        t = mod.type

        # Modify
        if t == 'UV_PROJECT':
            mod_targets = [mod.object]
        elif t == 'UV_WARP':
            mod_targets = [[mod.object_from, mod.bone_from],
                       [mod.object_to, mod.bone_to]]
        elif t == 'VERTEX_WEIGHT_PROXIMITY':
            mod_targets = [mod.target]

        # Generate
        elif t == 'ARRAY':
            mod_targets = [mod.start_cap, mod.end_cap]
            if mod.use_object_offset:
                mod_targets.append(mod.offset_object)
        elif t == 'BOOLEAN':
            mod_targets = [mod.object]
        elif t == 'MIRROR':
            mod_targets = [mod.mirror_object]
        elif t == 'SCREW':
            mod_targets = [mod.object]

        # Deform
        elif t in ('ARMATURE', 'CAST', 'CURVE', 'LATTICE', 'MESH_DEFORM'):
            mod_targets = [mod.object]
        elif t == 'HOOK':
            mod_targets = [[mod.object, mod.subtarget]]
        elif t == 'SHRINKWRAP':
            mod_targets = [mod.target]
        elif t == 'SIMPLE_DEFORM':
            mod_targets = [mod.origin]
        elif t == 'WARP':
            mod_targets = [mod.object_from, mod.object_to]
        elif t == 'WAVE':
            mod_targets = [mod.start_position_object]

        # Simulate
        elif t == 'PARTICLE_INSTANCE':
            mod_targets = [mod.object]

        # append
        for target in mod_targets:
            if isinstance(target, (list, tuple)):
                target, subtarget = target
            else:
                subtarget = ''
            if target:
                if subtarget and subtarget in target.pose.bones:
                    targets.append(target.pose.bones[subtarget])
                else:
                    targets.append(target)

    return targets


def _get_depend_on(ob, parent=True, constraints=True, modifiers=True):
    """Object, PoseBone, EditBone, Boneで使用可"""
    targets = []
    if parent:
        parent_ob = _get_depend_on_parent(ob)
        if parent_ob:
            targets.append(parent_ob)
    if constraints:
        if isinstance(ob, (bpy.types.Object, bpy.types.PoseBone)):
            targets.extend(_get_depend_on_constraints(ob))
    if modifiers:
        if isinstance(ob, bpy.types.Object):
            targets.extend(_get_depend_on_modifiers(ob))
    # TODO: driver
    return targets


def sorted_dependency(objects, parent=True, constraints=True, modifiers=True,
                      all=False):
    """objectsを依存関係により並び替えたリストを返す。先頭がroot側。
    :param objects: Object, PoseBone, EditBone, Bone の何れかのリスト
    :type objects: abc.Iterable
    :type parent: bool
    :type constraints: bool
    :type modifiers: bool
    :param all: 依存関係にあるがelementsに含まれないものも返り値に含める。
    :type all: bool
    :rtype: list
    """
    func = functools.partial(_get_depend_on, parent=parent,
                             constraints=constraints, modifiers=modifiers)
    return localutils.utils.sorted_dependency(objects, func, all)
