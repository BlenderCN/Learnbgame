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


bl_info = {
    'name': 'QuadView Move',
    'author': 'chromoly',
    'version': (0, 2),
    'blender': (2, 77, 0),
    'location': 'View3D',
    'description': '',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/quadview_move',
    'tracker_url': '',
    'category': '3D View',
}


"""
QuadViewの境界中心をドラッグする事でその大きさを変更する。
"""


import importlib
import math

import bpy

try:
    importlib.reload(structures)
    importlib.reload(utils)
except NameError:
    pass
from .structures import *
from .utils import AddonPreferences, SpaceProperty, AddonKeyMapUtility


# regionの幅と高さの最小幅
MIN_SIZE = 5


class QuadViewMovePreferences(
        AddonKeyMapUtility,
        AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    # 反応する閾値
    threshold = bpy.props.IntProperty(
        name='Threshold', min=1, max=50, default=10)

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        column = split.column()
        row = column.row()
        row.prop(self, 'threshold')
        column = split.column()
        column = split.column()

        super().draw(context, layout.column())


def get_window_modal_handlers(window):
    """ctypesを使い、windowに登録されている modal handlerのリストを返す。
    idnameはUIなら 'UI'、認識できない物なら 'UNKNOWN' となる。
    :rtype: list[(Structures.wmEventHandler, str, int, int, int)]
    """
    if not window:
        return []

    addr = window.as_pointer()
    win = cast(c_void_p(addr), POINTER(wmWindow)).contents

    handlers = []

    ptr = cast(win.modalhandlers.first, POINTER(wmEventHandler))
    while ptr:
        # http://docs.python.jp/3/library/ctypes.html#surprises
        # この辺りの事には注意する事
        handler = ptr.contents
        area = handler.op_area  # NULLの場合はNone
        region = handler.op_region  # NULLの場合はNone
        idname = 'UNKNOWN'
        if handler.ui_handle:
            idname = 'UI'
        if handler.op:
            op = handler.op.contents
            ot = op.type.contents
            if ot.idname:
                idname = ot.idname.decode()
        handlers.append((handler, idname, area, region,
                         handler.op_region_type))
        ptr = handler.next

    return handlers


def swin_from_region(window, region):
    win = cast(c_void_p(window.as_pointer()), POINTER(wmWindow)).contents
    ar = cast(c_void_p(region.as_pointer()), POINTER(ARegion)).contents
    swinid = ar.swinid

    swin_ptr = cast(win.subwindows.first, POINTER(wmSubWindow))
    while swin_ptr:
        swin = swin_ptr.contents
        if swin.swinid == swinid:
            return swin
        swin_ptr = swin.next
    return None


def get_active_region_index(context, mx, my, regions, rv3d_list):
    # test smooth timer
    for i, rv3d in enumerate(rv3d_list[:3]):
        if rv3d.smooth_timer:
            return i

    # test modal handler
    handlers = get_window_modal_handlers(context.window)
    for h, idname, sa, ar, rt in handlers:
        if idname in ('VIEW3D_OT_zoom', 'VIEW3D_OT_move'):
            if ar is not None:
                for i, region in enumerate(regions[:3]):
                    if region.as_pointer() == cast(ar, c_void_p).value:
                        return i

    # test mouse position
    # ここでは 3 を返す事がある
    for i, region in enumerate(regions):
        if (region.x <= mx <= region.x + region.width and
                region.y <= my <= region.y + region.height):
            return i

    # test max size
    sizes = [(max(region.width, region.height), region)
             for region in regions[:3]]
    return regions.index(max(sizes, key=lambda x: x[0])[1])


class VIEW3D_PG_QuadViewAspect(bpy.types.PropertyGroup):
    enable = bpy.props.BoolProperty()
    center = bpy.props.FloatVectorProperty(size=2)


space_prop = SpaceProperty(
    [bpy.types.SpaceView3D, 'quadview_aspect',
     VIEW3D_PG_QuadViewAspect])


def sync_quad(context, area):
    """source/blender/editors/screen/area.c: region_rect_recursive()辺りを参考
    """
    v3d = area.spaces.active
    prop = space_prop.get(v3d)
    if not prop.enable:
        return
    fx, fy = prop.center

    addr = context.window.as_pointer()
    win = cast(c_void_p(addr), POINTER(wmWindow)).contents
    event = win.eventstate.contents

    regions = [region for region in area.regions if region.type == 'WINDOW']
    xmin = float(regions[0].x)
    xmax = float(regions[2].x + regions[2].width)
    ymin = float(regions[0].y)
    ymax = float(regions[1].y + regions[1].height)
    if xmax - xmin + 1 <= MIN_SIZE * 2:
        centx = xmin + MIN_SIZE
    else:
        centx = xmin + (xmax - xmin) * fx
        centx = min(max(xmin + MIN_SIZE, centx), xmax - MIN_SIZE)
    if ymax - ymin + 1 <= MIN_SIZE * 2:
        centy = ymin + MIN_SIZE
    else:
        centy = ymin + (ymax - ymin) * fy
        centy = min(max(ymin + MIN_SIZE, centy), ymax - MIN_SIZE)
    centx = round(centx)
    centy = round(centy)

    for i, region in enumerate(regions):
        addr = region.as_pointer()
        ar = cast(c_void_p(addr), POINTER(ARegion)).contents
        rct = ar.winrct
        rect = [rct.xmin, rct.ymin, rct.xmax, rct.ymax]
        rect_bak = rect[:]
        if i < 2:
            rect[2] = centx - 1
        else:
            rect[0] = centx
        if i in (0, 2):
            rect[3] = centy - 1
        else:
            rect[1] = centy

        if rect == rect_bak:
            continue

        rct.xmin, rct.ymin, rct.xmax, rct.ymax = rect
        ar.winx = rct.xmax - rct.xmin + 1
        ar.winy = rct.ymax - rct.ymin + 1
        U = context.user_preferences
        UI_DPI_FAC = U.system.pixel_size * U.system.dpi / 72.0
        ar.sizex = int((ar.winx + 0.5) / UI_DPI_FAC)
        ar.sizey = int((ar.winy + 0.5) / UI_DPI_FAC)

        swin = swin_from_region(bpy.context.window, region)
        if swin:
            swin.winrct.xmin = rct.xmin
            swin.winrct.xmax = rct.xmax
            swin.winrct.ymin = rct.ymin
            swin.winrct.ymax = rct.ymax

        region.tag_redraw()

    if area.spaces.active.region_quadviews[2].show_sync_view:
        rv3d_list = []
        for region_data in area.spaces.active.region_quadviews:
            addr = region_data.as_pointer()
            rv3d = cast(c_void_p(addr), POINTER(RegionView3D)).contents
            rv3d_list.append(rv3d)
        index = get_active_region_index(context, event.x, event.y, regions,
                                        rv3d_list)
        if index != 3:
            region = regions[index]
            rv3d = rv3d_list[index]

            fac = max(region.width, region.height) / rv3d.dist

            for i, (region, rv3d) in enumerate(zip(regions, rv3d_list)):
                prev_dist = rv3d.dist
                rv3d.dist = max(0.001, max(region.width, region.height) / fac)
                if prev_dist != rv3d.dist:
                    region.tag_redraw()
                if i == 2:
                    break


class VIEW3D_OT_quadview_move(bpy.types.Operator):
    bl_idname = 'view3d.quadview_move'
    bl_label = 'QuadView Move'
    bl_options = set()

    @classmethod
    def poll(cls, context):
        area = context.area
        if area and area.type == 'VIEW_3D':
            if area.spaces.active.region_quadviews:
                return True
        return False

    def modal(self, context, event):
        v3d = context.area.spaces.active
        prop = space_prop.get(v3d)

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            prop.center = (0.5, 0.5)
            sync_quad(context, context.area)
            prop.enable = False
            context.window.cursor_set('DEFAULT')
            return {'FINISHED'}

        mco = (event.mouse_x, event.mouse_y)

        regions = [r for r in context.area.regions if r.type == 'WINDOW']

        xmin = float(regions[0].x)
        xmax = float(regions[2].x + regions[2].width)
        ymin = float(regions[0].y)
        ymax = float(regions[1].y + regions[1].height)

        if xmax - xmin <= MIN_SIZE * 2:
            fx = 0.5
        else:
            dx = mco[0] - self.mco[0]
            centx = min(max(xmin + MIN_SIZE, self.center[0] + dx),
                        xmax - MIN_SIZE - 1)
            fx = (centx - xmin) / (xmax - xmin)
        if ymax - ymin <= 4:
            fy = 0.5
        else:
            dy = mco[1] - self.mco[1]
            centy = min(max(ymin + 2, self.center[1] + dy),
                        ymax - MIN_SIZE - 1)
            fy = (centy - ymin) / (ymax - ymin)

        prop.enable = True
        prop.center = (fx, fy)
        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        prefs = QuadViewMovePreferences.get_instance()

        mco = self.mco = (event.mouse_x, event.mouse_y)
        for region in context.area.regions:
            if region.type == 'WINDOW':
                break
        center = self.center = (float(region.x + region.width),
                                float(region.y + region.height))

        cancel = False
        d = math.sqrt((mco[0] - center[0]) ** 2 + (mco[1] - center[1]) ** 2)
        if d > prefs.threshold:
            cancel = True
        elif context.user_preferences.system.use_region_overlap:
            for region in context.area.regions:
                if region.id != 0:
                    if region.type in ('TOOLS', 'TOOL_PROPS', 'UI'):
                        # region.width == ar.winrct.xmax - ar.winrct.xmin + 1
                        if region.x <= mco[0] <= region.x + region.width - 1:
                            cancel = True
                            break
        if cancel:
            return {'CANCELLED', 'PASS_THROUGH'}

        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('SCROLL_XY')
        return {'RUNNING_MODAL'}


@bpy.app.handlers.persistent
def scene_update_func(scene):
    screen = bpy.context.screen
    if screen:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                if area.spaces.active.region_quadviews:
                    sync_quad(bpy.context, area)


classes = [
    VIEW3D_OT_quadview_move,
    QuadViewMovePreferences,
    VIEW3D_PG_QuadViewAspect,
]

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    space_prop.register()

    bpy.app.handlers.scene_update_post.append(scene_update_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        addon_prefs = QuadViewMovePreferences.get_instance()
        """:type: QuadViewMovePreferences"""
        km = addon_prefs.get_keymap('Screen Editing')
        kmi = km.keymap_items.new('view3d.quadview_move', 'LEFTMOUSE', 'PRESS',
                                  head=True)
        addon_keymaps.append((km, kmi))
        addon_prefs.register_keymap_items(addon_keymaps)


def unregister():
    addon_prefs = QuadViewMovePreferences.get_instance()
    """:type: QuadViewMovePreferences"""
    addon_prefs.unregister_keymap_items()

    bpy.app.handlers.scene_update_post.remove(scene_update_func)

    space_prop.unregister()

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
