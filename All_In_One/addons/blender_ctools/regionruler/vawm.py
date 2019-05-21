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


import ctypes

import bpy


def mouse_area_region(mco, screen=None, find_reverse=False):
    """マウスカーソルが内側に有るAreaとRegionを返す。
    :param mco: window座標 [event.mouse_x, event.mouse_y]
    :type mco: Vector | list | tuple
    :param screen: screenを指定する。初期値はbpy.context.screen
    :type screen: bpy.types.Screen
    :param find_reverse: region_overlapの事も考え、通常は 'TOOLS', 'PROPERTIES'
        等を最初に確認するが、これを真にすると 'WINDOW' を最初に確認する。
    :type find_reverse: bool
    :rtype: (bpy.types.Area, bpy.types.Region)
    """
    if not screen:
        screen = bpy.context.screen
    for area in screen.areas:
        regions = list(area.regions)
        ls = regions[:]
        regions.sort(key=lambda r: (int(r.type == 'WINDOW'), ls.index(r)),
                     reverse=find_reverse)
        for region in regions:
            if region.id != 0:  # 非表示のものはidが0になる
                if region.x <= mco[0] < region.x + region.width:
                    if region.y <= mco[1] < region.y + region.height:
                        return area, region
    return None, None


def region_from_id(region_id, screen=None):
    """idが一致するRegionを返す
    :type region_id: int
    :rtype: Region
    """
    if region_id == 0:
        return None
    if not screen:
        screen = bpy.context.screen
    for area in screen.areas:
        for region in area.regions:
            if region.id == region_id:
                return region


def get_area_from_data(data):
    """Region若しくはSpaceが所属するAreaを返す
    :type data: Region | Space
    :return:
    """
    if isinstance(data, bpy.types.Region):
        for sa in data.id_data.areas:  # data.id_data == Screen
            for ar in sa.regions:
                if ar == data:
                    return sa
    elif isinstance(data, bpy.types.Space):
        for sa in data.id_data.areas:
            for sl in sa.spaces:
                if sl == data:
                    return sa


def operator_call(op, *args, _scene_update=True, **kw):
    import bpy
    from _bpy import ops as ops_module

    BPyOpsSubModOp = op.__class__
    op_call = ops_module.call
    context = bpy.context

    # Get the operator from blender
    wm = context.window_manager

    # run to account for any rna values the user changes.
    if _scene_update:
        BPyOpsSubModOp._scene_update(context)

    if args:
        C_dict, C_exec, C_undo = BPyOpsSubModOp._parse_args(args)
        ret = op_call(op.idname_py(), C_dict, kw, C_exec, C_undo)
    else:
        ret = op_call(op.idname_py(), None, kw)

    if 'FINISHED' in ret and context.window_manager == wm:
        if _scene_update:
            BPyOpsSubModOp._scene_update(context)

    return ret


class wmWindow(ctypes.Structure):
    _fields_ = [
        ('next', ctypes.c_void_p),  # struct wmWindow
        ('prev', ctypes.c_void_p),  # struct wmWindow
        ('ghostwin', ctypes.c_void_p),

        ('screen', ctypes.c_void_p),  # struct bScreen
        ('newscreen', ctypes.c_void_p),  # struct bScreen
        ('screenname', ctypes.c_char * 64),

        ('posx', ctypes.c_short),
        ('posy', ctypes.c_short),
        ('sizex', ctypes.c_short),
        ('sizey', ctypes.c_short),
        ('windowstate', ctypes.c_short),
        ('monitor', ctypes.c_short),
        ('active', ctypes.c_short),
    ]


def active_window(context):
    for window in context.window_manager.windows:
        p = ctypes.c_void_p(window.as_pointer())
        win = ctypes.cast(p, ctypes.POINTER(wmWindow)).contents
        if win.active:
            return window
