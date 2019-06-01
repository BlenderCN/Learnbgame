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


"""
>>> import ctypes
>>> blend_cdll = ctypes.CDLL('')
>>> # call function
>>> EDBM_vert_find_nearest_ex = blend_cdll.EDBM_vert_find_nearest_ex
>>> EDBM_vert_find_nearest_ex.restype = POINTER(BMVert)
>>> eve = EDBM_vert_find_nearest_ex(ctypes.byref(vc), ctypes.byref(dist), \
                                    ctypes.c_bool(1), use_cycle)
>>> # address -> function
>>> addr = ctypes.cast(EDBM_vert_find_nearest_ex, ctypes.c_void_p).value
>>> functype = ctypes.CFUNCTYPE(POINTER(BMVert), POINTER(ViewContext),
                   POINTER(ctypes.c_float), ctypes.c_bool, ctypes.c_bool)
>>> func = functype(addr)
>>> eve = func(ctypes.byref(vc), ctypes.byref(dist), ctypes.c_bool(1), \
               use_cycle)
"""


import ctypes
from ctypes import CDLL, Structure, Union, POINTER, addressof, cast, \
    c_char, c_char_p, c_double, c_float, c_short, c_int, c_void_p, \
    py_object, c_ssize_t, c_uint, c_int8, c_uint8, CFUNCTYPE, byref
import numpy as np
import platform
import re

import bpy


version = bpy.app.version


class c_void:
    pass


def fields(*field_items):
    """:rtype: list"""
    r_fields = []

    type = None
    for item in field_items:
        if isinstance(item, str):
            if type is None:
                raise ValueError('最初の要素は型でないといけない')
            m = re.match('(\**)(\w+)([\[\d\]]+)?$', item)  # 括弧は未対応
            if not m:
                raise ValueError('メンバ指定文字が間違ってる: {}'.format(item))
            ptr, name, num = m.groups()
            t = type
            if t is c_void:
                if ptr:
                    t = c_void_p
                    ptr = ptr[1:]
                else:
                    raise ValueError('c_voidを使う場合はポインタ表記必須')
            if ptr:
                for _ in range(len(ptr)):
                    t = POINTER(t)
            if num:
                # cとctypesでは逆になる
                for n in reversed(re.findall('\[(\d+)\]', num)):
                    t *= int(n)
            r_fields.append((name, t))
        else:
            type = item

    return r_fields


def set_fields(cls, *field_items):
    """'_fields_'のスペルミス多発の為"""
    cls._fields_ = fields(*field_items)


###############################################################################
# blenkernel / makesdna / windowmanager/ editors
###############################################################################
class Link(Structure):
    """source/blender/makesdna/DNA_listBase.h: 47"""

Link._fields_ = fields(
    Link, '*next', '*prev',
)


class ListBase(Structure):
    """source/blender/makesdna/DNA_listBase.h: 59"""
    _fields_ = fields(
        c_void_p, 'first', 'last',
    )

    def remove(self, vlink):
        """
        void BLI_remlink(ListBase *listbase, void *vlink)
        {
            Link *link = vlink;

            if (link == NULL) return;

            if (link->next) link->next->prev = link->prev;
            if (link->prev) link->prev->next = link->next;

            if (listbase->last == link) listbase->last = link->prev;
            if (listbase->first == link) listbase->first = link->next;
        }
        """
        link = vlink
        if not vlink:
            return

        if link.next:
            link.next.contents.prev = link.prev
        if link.prev:
            link.prev.contents.next = link.next

        if self.last == addressof(link):
            self.last = cast(link.prev, c_void_p)
        if self.first == addressof(link):
            self.first = cast(link.next, c_void_p)

    def find(self, number):
        """
        void *BLI_findlink(const ListBase *listbase, int number)
        {
            Link *link = NULL;

            if (number >= 0) {
                link = listbase->first;
                while (link != NULL && number != 0) {
                    number--;
                    link = link->next;
                }
            }

            return link;
        }
        """
        link_p = None
        if number >= 0:
            link_p = cast(c_void_p(self.first), POINTER(Link))
            while link_p and number != 0:
                number -= 1
                link_p = link_p.contents.next
        return link_p.contents if link_p else None

    def insert_after(self, vprevlink, vnewlink):
        """
        void BLI_insertlinkafter(ListBase *listbase, void *vprevlink, void *vnewlink)
        {
            Link *prevlink = vprevlink;
            Link *newlink = vnewlink;

            /* newlink before nextlink */
            if (newlink == NULL) return;

            /* empty list */
            if (listbase->first == NULL) {
                listbase->first = newlink;
                listbase->last = newlink;
                return;
            }

            /* insert at head of list */
            if (prevlink == NULL) {
                newlink->prev = NULL;
                newlink->next = listbase->first;
                newlink->next->prev = newlink;
                listbase->first = newlink;
                return;
            }

            /* at end of list */
            if (listbase->last == prevlink) {
                listbase->last = newlink;
            }

            newlink->next = prevlink->next;
            newlink->prev = prevlink;
            prevlink->next = newlink;
            if (newlink->next) {
                newlink->next->prev = newlink;
            }
        }
        """
        prevlink = vprevlink
        newlink = vnewlink

        if not newlink:
            return

        def gen_ptr(link):
            if isinstance(link, (int, type(None))):
                return cast(c_void_p(link), POINTER(Link))
            else:
                return ctypes.pointer(link)

        if not self.first:
            self.first = self.last = addressof(newlink)
            return

        if not prevlink:
            newlink.prev = None
            newlink.next = gen_ptr(self.first)
            newlink.next.contents.prev = gen_ptr(newlink)
            self.first = addressof(newlink)
            return

        if self.last == addressof(prevlink):
            self.last = addressof(newlink)

        newlink.next = prevlink.next
        newlink.prev = gen_ptr(prevlink)
        prevlink.next = gen_ptr(newlink)
        if newlink.next:
            newlink.next.prev = gen_ptr(newlink)

    def insert(self, i, vlink):
        self.insert_after(self.find(i - 1), vlink)

    def test(self):
        link1 = Link()
        link2 = Link()
        self.insert_after(None, link1)
        # self.insert_after(link1, link2)
        self.insert(1, link2)
        def eq(a, b):
            return addressof(a) == addressof(b)
        assert (self.first == addressof(link1))
        assert (self.last == addressof(link2))
        assert (eq(link1.next.contents, link2))
        assert (eq(link2.prev.contents, link1))
        assert (eq(link1.next.contents.prev.contents, link1))
        assert (eq(link2.prev.contents.next.contents, link2))

        self.remove(link2)
        assert(self.last == addressof(link1))
        assert(not link1.next)


class rcti(Structure):
    """DNA_vec_types.h: 86
    NOTE: region.width == ar.winrct.xmax - ar.winrct.xmin + 1
    """
    _fields_ = fields(
        c_int, 'xmin', 'xmax',
        c_int, 'ymin', 'ymax',
    )


class rctf(Structure):
    """DNA_vec_types.h: 92"""
    _fields_ = fields(
        c_float, 'xmin', 'xmax',
        c_float, 'ymin', 'ymax',
    )


class View2D(Structure):
    """DNA_view2d_types.h: 40"""

View2D._fields_ = fields(
    rctf, 'tot', 'cur',  # tot - area that data can be drawn in cur - region of tot that is visible in viewport
    rcti, 'vert', 'hor',  # vert - vertical scrollbar region hor - horizontal scrollbar region
    rcti, 'mask',  # region (in screenspace) within which 'cur' can be viewed

    c_float, 'min[2]', 'max[2]',  # min/max sizes of 'cur' rect (only when keepzoom not set)
    c_float, 'minzoom', 'maxzoom',  # allowable zoom factor range (only when (keepzoom & V2D_LIMITZOOM)) is set

    c_short, 'scroll',  # scroll - scrollbars to display (bitflag)
    c_short, 'scroll_ui',  # scroll_ui - temp settings used for UI drawing of scrollers

    c_short, 'keeptot',  # keeptot - 'cur' rect cannot move outside the 'tot' rect?
    c_short, 'keepzoom',  # keepzoom - axes that zooming cannot occur on, and also clamp within zoom-limits
    c_short, 'keepofs',  # keepofs - axes that translation is not allowed to occur on

    c_short, 'flag',  # settings
    c_short, 'align',  # alignment of content in totrect

    c_short, 'winx', 'winy',  # storage of current winx/winy values, set in UI_view2d_size_update
    c_short, 'oldwinx', 'oldwiny',  # storage of previous winx/winy values encountered by UI_view2d_curRect_validate(), for keepaspect

    c_short, 'around',  # pivot point for transforms (rotate and scale)

    c_float, '*tab_offset',  # different offset per tab, for buttons
    c_int, 'tab_num',  # number of tabs stored
    c_int, 'tab_cur',  # current tab

    # animated smooth view
    c_void_p, 'sms',  # struct SmoothView2DStore
    c_void_p, 'smooth_timer',  # struct wmTimer
)


class ARegionType(Structure):
    """BKE_screen.h: 116"""

ARegionType._fields_ = fields(
    ARegionType, '*next', '*prev',

    c_int, 'regionid',  # unique identifier within this space, defines RGN_TYPE_xxxx

    # add handlers, stuff you only do once or on area/region type/size changes
    c_void_p, 'init',
    # exit is called when the region is hidden or removed
    c_void_p, 'exit',
    # draw entirely, view changes should be handled here
    c_void_p, 'draw',
    # contextual changes should be handled here
    c_void_p, 'listener',

    c_void_p, 'free',

    # split region, copy data optionally
    c_void_p, 'duplicate',

    # register operator types on startup
    c_void_p, 'operatortypes',
    # add own items to keymap
    c_void_p, 'keymap',
    # allows default cursor per region
    c_void_p, 'cursor',

    # return context data
    c_void_p, 'context',

    # custom drawing callbacks
    ListBase, 'drawcalls',

    # panels type definitions
    ListBase, 'paneltypes',

    # header type definitions
    ListBase, 'headertypes',

    # hardcoded constraints, smaller than these values region is not visible
    c_int, 'minsizex', 'minsizey',
    # when new region opens (region prefsizex/y are zero then
    c_int, 'prefsizex', 'prefsizey',
    # default keymaps to add
    c_int, 'keymapflag',
    # return without drawing. lock is set by region definition, and copied to do_lock by render. can become flag
    c_short, 'do_lock', 'lock',
    # call cursor function on each move event
    c_short, 'event_cursor',
)


class SpaceType(Structure):
    """BKE_screen.h: 66"""

SpaceType._fields_ = fields(
    # struct SpaceType *next, *prev
    #
    # char name[BKE_ST_MAXNAME]                  # for menus
    # int spaceid                                # unique space identifier
    # int iconid                                 # icon lookup for menus
    #
    # # initial allocation, after this WM will call init() too
    # struct SpaceLink    *(*new)(const struct bContext *C)
    # # not free spacelink itself
    # void (*free)(struct SpaceLink *)
    #
    # # init is to cope with file load, screen (size) changes, check handlers
    # void (*init)(struct wmWindowManager *, struct ScrArea *)
    # # exit is called when the area is hidden or removed
    # void (*exit)(struct wmWindowManager *, struct ScrArea *)
    # # Listeners can react to bContext changes
    # void (*listener)(struct bScreen *sc, struct ScrArea *, struct wmNotifier *)
    #
    # # refresh context, called after filereads, ED_area_tag_refresh()
    # void (*refresh)(const struct bContext *, struct ScrArea *)
    #
    # # after a spacedata copy, an init should result in exact same situation
    # struct SpaceLink    *(*duplicate)(struct SpaceLink *)
    #
    # # register operator types on startup
    # void (*operatortypes)(void)
    # # add default items to WM keymap
    # void (*keymap)(struct wmKeyConfig *)
    # # on startup, define dropboxes for spacetype+regions
    # void (*dropboxes)(void)
    #
    # # return context data
    # int (*context)(const struct bContext *, const char *, struct bContextDataResult *)
    #
    # # region type definitions
    # ListBase regiontypes
    #
    # # tool shelf definitions
    # ListBase toolshelf
    #
    # # read and write...
    #
    # # default keymaps to add
    # int keymapflag
)


class ScrArea(Structure):
    """DNA_screen_types.h: 202"""

ScrArea._fields_ = fields(
    ScrArea, '*next', '*prev',

    c_void_p, 'v1', 'v2', 'v3', 'v4',  # ordered (bl, tl, tr, br)

    c_void_p, 'full',  # <bScreen> if area==full, this is the parent

    rcti, 'totrct',  # rect bound by v1 v2 v3 v4

    c_char, 'spacetype', 'butspacetype',  # SPACE_..., butspacetype is button arg
    c_short, 'winx', 'winy',  # size

    c_short, 'headertype',  # OLD! 0=no header, 1= down, 2= up
    c_short, 'do_refresh',  # private, for spacetype refresh callback
    c_short, 'flag',
    c_short, 'region_active_win',  # index of last used region of 'RGN_TYPE_WINDOW'
                                   # runtime variable, updated by executing operators
    c_char, 'temp', 'pad',

    SpaceType, '*type',  # callbacks for this space type

    ListBase, 'spacedata',  # SpaceLink
    ListBase, 'regionbase',  # ARegion
    ListBase, 'handlers',  # wmEventHandler

    ListBase, 'actionzones',  # AZone
)


class ARegion(Structure):
    """DNA_screen_types.h: 229"""

ARegion._fields_ = fields(
    ARegion, '*next', '*prev',

    View2D, 'v2d',  # 2D-View scrolling/zoom info (most regions are 2d anyways)
    rcti, 'winrct',  # coordinates of region
    rcti, 'drawrct',  # runtime for partial redraw, same or smaller than winrct
    c_short, 'winx', 'winy',  # size

    c_short, 'swinid',
    c_short, 'regiontype',  # window, header, etc. identifier for drawing
    c_short, 'alignment',  # how it should split
    c_short, 'flag',  # hide, ...

    c_float, 'fsize',  # current split size in float (unused)
    c_short, 'sizex', 'sizey',  # current split size in pixels (if zero it uses regiontype)

    c_short, 'do_draw',  # private, cached notifier events
    c_short, 'do_draw_overlay',  # private, cached notifier events
    c_short, 'swap',  # private, indicator to survive swap-exchange
    c_short, 'overlap',  # private, set for indicate drawing overlapped
    c_short, 'flagfullscreen',  # temporary copy of flag settings for clean fullscreen
    c_short, 'pad',

    ARegionType, '*type',  # callbacks for this region type

    ListBase, 'uiblocks',  # uiBlock
    ListBase, 'panels',  # Panel
    ListBase, 'panels_category_active',  # Stack of panel categories
    ListBase, 'ui_lists',  # uiList
    ListBase, 'ui_previews',  # uiPreview
    ListBase, 'handlers',  # wmEventHandler
    ListBase, 'panels_category',  # Panel categories runtime

    c_void_p, 'regiontimer',  # <struct wmTimer>  # blend in/out

    c_char_p, 'headerstr',  # use this string to draw info
    c_void_p, 'regiondata',  # XXX 2.50, need spacedata equivalent?
)


class RegionView3D(Structure):
    """DNA_view3d_types.h: 86"""

RegionView3D._fields_ = fields(
    c_float, 'winmat[4][4]',  # GL_PROJECTION matrix
    c_float, 'viewmat[4][4]',  # GL_MODELVIEW matrix
    c_float, 'viewinv[4][4]',  # inverse of viewmat
    c_float, 'persmat[4][4]',  # viewmat*winmat
    c_float, 'persinv[4][4]',  # inverse of persmat
    c_float, 'viewcamtexcofac[4]',  # offset/scale for camera glsl texcoords

    # viewmat/persmat multiplied with object matrix, while drawing and selection
    c_float, 'viewmatob[4][4]',
    c_float, 'persmatob[4][4]',

    # user defined clipping planes
    c_float, 'clip[6][4]',
    c_float, 'clip_local[6][4]',  # clip in object space, means we can test for clipping in editmode without first going into worldspace
    c_void_p, 'clipbb',  # struct BoundBox

    RegionView3D, '*localvd',  # allocated backup of its self while in localview
    c_void_p, 'render_engine',  # struct RenderEngine
    c_void_p, 'depths',  # struct ViewDepths
    c_void_p, 'gpuoffscreen',

    # animated smooth view
    c_void_p, 'sms',  # struct SmoothView3DStore
    c_void_p, 'smooth_timer',  # struct wmTimer

    # transform widget matrix
    c_float, 'twmat[4][4]',

    c_float, 'viewquat[4]',  # view rotation, must be kept normalized
    c_float, 'dist',  # distance from 'ofs' along -viewinv[2] vector, where result is negative as is 'ofs'
    c_float, 'camdx', 'camdy',  # camera view offsets, 1.0 = viewplane moves entire width/height
    c_float, 'pixsize',  # runtime only
    c_float, 'ofs[3]',  # view center & orbit pivot, negative of worldspace location, also matches -viewinv[3][0:3] in ortho mode. 
    c_float, 'camzoom',  # viewport zoom on the camera frame, see BKE_screen_view3d_zoom_to_fac
    c_char, 'is_persp',   # check if persp/ortho view, since 'persp' cant be used for this since
                            # it can have cameras assigned as well. (only set in view3d_winmatrix_set)
    c_char, 'persp',
    c_char, 'view',
    c_char, 'viewlock',
    c_char, 'viewlock_quad',  # options for quadview (store while out of quad view)
    c_char, 'pad[3]',
    c_float, 'ofs_lock[2]',  # normalized offset for locked view: (-1, -1) bottom left, (1, 1) upper right

    c_short, 'twdrawflag',
    c_short, 'rflag',

    # last view (use when switching out of camera view)
    c_float, 'lviewquat[4]',
    c_short, 'lpersp', 'lview',  # lpersp can never be set to 'RV3D_CAMOB'

    c_float, 'gridview',
    c_float, 'tw_idot[3]',  # manipulator runtime: (1 - dot) product with view vector (used to check view alignment)

    # active rotation from NDOF or elsewhere
    c_float, 'rot_angle',
    c_float, 'rot_axis[3]',

    c_void_p, 'compositor',  # struct GPUFX
)


class GPUFXSettings(Structure):
    """DNA_gpu_types.h"""
    _fields_ = fields(
        c_void_p, 'dof',  # GPUDOFSettings
        c_void_p, 'ssao',  # GPUSSAOSettings
        c_char, 'fx_flag',  # eGPUFXFlags
        c_char, 'pad[7]',
        )


class View3D(Structure):
    """DNA_view3d_types.h: 153"""

View3D._fields_ = fields(
    c_void_p, 'next', 'prev',  # struct SpaceLink *next, *prev
    ListBase, 'regionbase',  # storage of regions for inactive spaces
    c_int, 'spacetype',
    c_float, 'blockscale',
    c_short, 'blockhandler[8]',

    c_float, 'viewquat[4]',  # DNA_DEPRECATED
    c_float, 'dist',  # DNA_DEPRECATED

    c_float, 'bundle_size',  # size of bundles in reconstructed data
    c_char, 'bundle_drawtype',  # display style for bundle
    c_char, 'pad[3]',

    c_uint, 'lay_prev',  # for active layer toggle
    c_uint, 'lay_used',  # used while drawing

    c_short, 'persp',  # DNA_DEPRECATED
    c_short, 'view',  # DNA_DEPRECATED

    c_void_p, 'camera', 'ob_centre',  # struct Object
    rctf, 'render_border',

    ListBase, 'bgpicbase',
    c_void_p, 'bgpic',  # <struct BGpic> DNA_DEPRECATED # deprecated, use bgpicbase, only kept for do_versions(...)

    View3D, '*localvd',  # allocated backup of its self while in localview

    c_char, 'ob_centre_bone[64]',  # optional string for armature bone to define center, MAXBONENAME

    c_uint, 'lay',
    c_int, 'layact',

    #  * The drawing mode for the 3d display. Set to OB_BOUNDBOX, OB_WIRE, OB_SOLID,
    #  * OB_TEXTURE, OB_MATERIAL or OB_RENDER
    c_short, 'drawtype',
    c_short, 'ob_centre_cursor',        # optional bool for 3d cursor to define center
    c_short, 'scenelock', 'around',
    c_short, 'flag', 'flag2',

    c_float, 'lens', 'grid',
    c_float, 'near', 'far',
    c_float, 'ofs[3]',  #  DNA_DEPRECATED  # XXX deprecated
    c_float, 'cursor[3]',

    c_short, 'matcap_icon',  # icon id

    c_short, 'gridlines',
    c_short, 'gridsubdiv',  # Number of subdivisions in the grid between each highlighted grid line
    c_char, 'gridflag',

    # transform widget info
    c_char, 'twtype', 'twmode', 'twflag',

    c_short, 'flag3',

    # afterdraw, for xray & transparent
    ListBase, 'afterdraw_transp',
    ListBase, 'afterdraw_xray',
    ListBase, 'afterdraw_xraytransp',

    # drawflags, denoting state
    c_char, 'zbuf', 'transp', 'xray',

    c_char, 'multiview_eye',  # multiview current eye - for internal use

    # built-in shader effects (eGPUFXFlags)
    c_char, 'pad3[4]',

    # note, 'fx_settings.dof' is currently _not_ allocated,
    # instead set (temporarily) from camera
    GPUFXSettings, 'fx_settings',

    c_void_p, 'properties_storage',  # Nkey panel stores stuff here (runtime only!)
    c_void_p, 'defmaterial',    # <struct Material> used by matcap now

    # # XXX deprecated?
    # struct bGPdata *gpd  DNA_DEPRECATED        # Grease-Pencil Data (annotation layers)
    # 
    # short usewcol, dummy3[3]
    # 
    #  # multiview - stereo 3d
    # short stereo3d_flag
    # char stereo3d_camera
    # char pad4
    # float stereo3d_convergence_factor
    # float stereo3d_volume_alpha
    # float stereo3d_convergence_alpha
    # 
    # # local grid
    # char localgrid, cursor_snap_grid, dummy[2]
    # float lg_loc[3], dummy2[2] // orign(x,y,z)
    # float lg_quat[4] // rotation(x,y,z)
)


class wmSubWindow(Structure):
    """windowmanager/intern/wm_subwindow.c: 67"""

wmSubWindow._fields_ = fields(
    wmSubWindow, '*next', '*prev',
    rcti, 'winrct',
    c_int, 'swinid',
)


class wmEvent(Structure):
    """windowmanager/WM_types.h: 431"""

wmEvent._fields_ = fields(
    wmEvent, '*next', '*prev',

    c_short, 'type',
    c_short, 'val',
    c_int, 'x', 'y',
    c_int, 'mval[2]',
    c_char, 'utf8_buf[6]',

    c_char, 'ascii',
    c_char, 'pad',

    c_short, 'prevtype',
    c_short, 'prevval',
    c_int, 'prevx', 'prevy',
    c_double, 'prevclick_time',
    c_int, 'prevclickx', 'prevclicky',

    c_short, 'shift', 'ctrl', 'alt', 'oskey',
    c_short, 'keymodifier',

    c_short, 'check_click',

    c_char_p, 'keymap_idname',  # const char

    c_void_p, 'tablet_data',  # const struct wmTabletData

    c_short, 'custom',
    c_short, 'customdatafree',
    c_int, 'pad2',
    c_void_p, 'customdata',
)


# wmOperatorType.flag
OPTYPE_REGISTER = (1 << 0)  # register operators in stack after finishing
OPTYPE_UNDO = (1 << 1)  # do undo push after after
OPTYPE_BLOCKING = (1 << 2)  # let blender grab all input from the WM (X11)
OPTYPE_MACRO = (1 << 3)
OPTYPE_GRAB_CURSOR = (1 << 4)  # grabs the cursor and optionally enables
                               # continuous cursor wrapping
OPTYPE_PRESET = (1 << 5)  # show preset menu

# some operators are mainly for internal use
# and don't make sense to be accessed from the
# search menu, even if poll() returns true.
# currently only used for the search toolbox */
OPTYPE_INTERNAL = (1 << 6)

OPTYPE_LOCK_BYPASS = (1 << 7)  # Allow operator to run when interface is locked


class ExtensionRNA(Structure):
    _fields_ = fields(
        c_void, '*data',
        c_void, '*srna',  # <StructRNA>
        c_void_p,'call',  # <StructCallbackFunc>
        c_void_p,'free'  # <StructFreeFunc>
    )


class wmOperatorType(Structure):
    """source/blender/windowmanager/WM_types.h: 518"""
    _fields_ = fields(
        c_char_p, 'name',
        c_char_p, 'idname',
        c_char_p, 'translation_context',
        c_char_p, 'description',

        c_void_p, 'exec',
        c_void_p, 'check',
        c_void_p, 'invoke',
        c_void_p, 'cancel',
        c_void_p, 'modal',

        c_void_p, 'poll',

        c_void_p, 'ui',

        c_void_p, 'srna',  # <StructRNA>

        c_void_p, 'last_properties',  # <IDProperty>

        c_void_p, 'prop',  # <PropertyRNA>

        ListBase, 'macro',

        c_void_p, 'modalkeymap',  # <wmKeyMap>

        c_void_p, 'pyop_poll',

        ExtensionRNA, 'ext',

        c_short, 'flag',
    )


class wmOperator(Structure):
    """source/blender/makesdna/DNA_windowmanager_types.h: 344

    pythonインスタンスからの取得方法:
    # python/intern/bpy_operator.c: 423: pyop_getinstance()
    pyop = bpy.ops.wm.splash
    opinst = pyop.get_instance()
    pyrna = ct.cast(ct.c_void_p(id(opinst)),
                     ct.POINTER(structures.BPy_StructRNA)).contents
    # wmOperator
    op = ct.cast(ct.c_void_p(pyrna.ptr.data),
                 ct.POINTER(structures.wmOperator)).contents
    # wmOperatorType
    ot = op.type.contents
    """

wmOperator._fields_ = fields(
    wmOperator, '*next', '*prev',

    c_char, 'idname[64]',
    c_void_p, 'properties',  # IDProperty

    wmOperatorType, '*type',
    c_void_p, 'customdata',
    py_object, 'py_instance',  # python stores the class instance here

    c_void_p, 'ptr',  # PointerRNA
    c_void_p, 'reports',  # ReportList

    ListBase, 'macro',
    wmOperator, '*opm',
    c_void_p, 'layout',  # uiLayout
    c_short, 'flag', c_short * 3, 'pad',
)


class wmEventHandler(Structure):
    """source/blender/windowmanager/wm_event_system.h: 45"""

wmEventHandler._fields_ = fields(
    wmEventHandler, '*next', '*prev',

    c_char, 'type',  # WM_HANDLER_DEFAULT, ...
    c_char, 'flag',  # WM_HANDLER_BLOCKING, ...

    # keymap handler
    c_void_p, 'keymap',  # <wmKeyMap> pointer to builtin/custom keymaps
    c_void_p, 'bblocal', 'bbwin',  # <const rcti> optional local and windowspace bb

    # modal operator handler
    wmOperator, '*op',  # for derived/modal handlers
    ScrArea, '*op_area',  # for derived/modal handlers
    ARegion, '*op_region',  # for derived/modal handlers
    c_short, 'op_region_type',  # for derived/modal handlers

    # ui handler
    c_void_p, 'ui_handle',  # <function: wmUIHandlerFunc> callback receiving events
    c_void_p, 'ui_remove',  # <function: wmUIHandlerRemoveFunc> callback when handler is removed
    c_void_p, 'ui_userdata',  # user data pointer
    ScrArea, '*ui_area',  # for derived/modal handlers
    ARegion, '*ui_region',  # for derived/modal handlers
    ARegion, '*ui_menu',  # for derived/modal handlers

    # drop box handler
    ListBase, '*dropboxes',
)

# wmEventHandler.flag
WM_HANDLER_DO_FREE = 1 << 7


class wmWindow(Structure):
    """source/blender/makesdna/DNA_windowmanager_types.h: 175"""

_fields = fields(
    wmWindow, '*next', '*prev',

    c_void_p, 'ghostwin',

    c_void_p, 'screen',  # struct bScreen
    c_void_p, 'newscreen',  # struct bScreen
    c_char, 'screenname[64]',

    c_short, 'posx', 'posy', 'sizex', 'sizey',
    c_short, 'windowstate',
    c_short, 'monitor',
    c_short, 'active',
    c_short, 'cursor',
    c_short, 'lastcursor',
    c_short, 'modalcursor',
    c_short, 'grabcursor',  # GHOST_TGrabCursorMode
    c_short, 'addmousemove',
    c_short, 'multisamples',
    c_short, 'pad[3]',

    c_int, 'winid',

    # internal, lock pie creation from this event until released
    c_short, 'lock_pie_event',
    # exception to the above rule for nested pies, store last pie event for operators
    # that spawn a new pie right after destruction of last pie
    c_short, 'last_pie_event',

    wmEvent, '*eventstate',

    wmSubWindow, '*curswin',

    c_void_p, 'tweak',  # struct wmGesture

    c_void_p, 'ime_data',  # struct wmIMEData

    c_int, 'drawmethod', 'drawfail',
    ListBase, 'drawdata',

    ListBase, 'queue',
    ListBase, 'handlers',
    ListBase, 'modalhandlers',  # wmEventHandler

    ListBase, 'subwindows',
    ListBase, 'gesture',

    c_void_p, 'stereo3d_format',  # struct Stereo3dFormat
)
wmWindow._fields_ = _fields


class SpaceText(Structure):
    """source/blender/makesdna/DNA_space_types.h: 981"""

SpaceText._fields_ = fields(
    SpaceText, '*next', '*prev',
    ListBase, 'regionbase',  # storage of regions for inactive spaces
    c_int, 'spacetype',
    c_float, 'blockscale',  # DNA_DEPRECATED
    c_short, 'blockhandler[8]',  # DNA_DEPRECATED

    c_void_p, 'text',  # struct Text

    c_int, 'top', 'viewlines',
    c_short, 'flags', 'menunr',

    c_short, 'lheight',  # user preference, is font_size!
    c_char, 'cwidth', 'linenrs_tot',  # runtime computed, character width and the number of chars to use when showing line numbers
    c_int, 'left',
    c_int, 'showlinenrs',
    c_int, 'tabnumber',

    c_short, 'showsyntax',
    c_short, 'line_hlight',
    c_short, 'overwrite',
    c_short, 'live_edit',  # run python while editing, evil
    c_float, 'pix_per_line',

    rcti, 'txtscroll', 'txtbar',

    c_int, 'wordwrap', 'doplugins',

    c_char, 'findstr[256]',  # ST_MAX_FIND_STR
    c_char, 'replacestr[256]',  # ST_MAX_FIND_STR

    c_short, 'margin_column',  # column number to show right margin at
    c_short, 'lheight_dpi',  # actual lineheight, dpi controlled
    c_char, 'pad[4]',

    c_void_p, 'drawcache',  # cache for faster drawing

    c_float, 'scroll_accum[2]',  # runtime, for scroll increments smaller than a line
)


class bContext(Structure):
    """source/blender/blenkernel/intern/context.c:61"""
    class bContext_wm(Structure):
        _fields_ = fields(
            c_void_p, 'manager',  # struct wmWindowManager
            wmWindow, '*window',
            c_void_p, 'screen',  # struct bScreen
            ScrArea, '*area',
            ARegion, '*region',
            ARegion, '*menu',
            c_void_p, 'store',  # struct bContextStore
            c_char_p, 'operator_poll_msg',  # reason for poll failing
        )

    class bContext_data(Structure):
        _fields_ = fields(
            c_void_p, 'main',  # struct Main
            c_void_p, 'scene',  # struct Scene

            c_int, 'recursion',
            c_int, 'py_init',  # true if python is initialized
            c_void_p, 'py_context',
        )

    _fields_ = fields(
        c_int, 'thread',

        # windowmanager context
        bContext_wm, 'wm',

        # data context
        bContext_data, 'data',
    )


class ID(Structure):
    """DNA_ID.h"""

ID._fields_ = fields(
    c_void_p, 'next', 'prev',
    ID, '*newid',
    c_void_p, 'lib',  # <struct Library>
    c_char, 'name[66]',  # MAX_ID_NAME
    c_short, 'flag',
    c_int, 'us',
    c_int, 'icon_id', 'pad2',
    c_void_p, 'properties',  # <IDProperty>
)


class Text(Structure):
    """makesdna/DNA_text_types.h: 50"""
    _fields_ = fields(
        ID, 'id',

        c_char_p, 'name',

        c_int, 'flags', 'nlines',

        ListBase, 'lines',
        c_void_p, 'curl', 'sell',  # <TextLine>
        c_int, 'curc', 'selc',

        c_char_p, 'undo_buf',
        c_int, 'undo_pos', 'undo_len',

        c_void_p, 'compiled',
        c_double, 'mtime',
    )


# 未使用
'''
class Material(Structure):
    """DNA_material_types.h"""

Material._fields_ = fields(
    ID, 'id',
)
'''


class DerivedMesh(Structure):
    """blenkernel/BKE_DerivedMesh.h: 177"""


class BMEditMesh(Structure):
    """blenkernel/BKE_editmesh.h: 53"""


# tessellation face, see MLoop/MPoly for the real face data
class MFace(Structure):
    """DNA_meshdata_types.h: 41"""
    _fields_ = fields(
        c_uint, 'v1', 'v2', 'v3', 'v4',
        c_short, 'mat_nr',
        c_char, 'edcode', 'flag',  # we keep edcode, for conversion to edges draw flags in old files
    )


class MEdge(Structure):
    """DNA_meshdata_types.h: 47"""
    _fields_ = fields(
        c_uint, 'v1', 'v2',
        c_char, 'crease', 'bweight',
        c_short, 'flag',
    )


class MDeformWeight(Structure):
    """DNA_meshdata_types.h: 53"""
    _fields_ = fields(
        c_int, 'def_nr',
        c_float, 'weight',
    )


class MDeformVert(Structure):
    """DNA_meshdata_types.h: 58"""
    _fields_ = fields(
        c_void, '*dw',  # struct MDeformWeight
        c_int, 'totweight',
        c_int, 'flag',  # flag only in use for weightpaint now
    )


class MVert(Structure):
    """DNA_meshdata_types.h: 64"""
    _fields_ = fields(
        c_float, 'co[3]',
        c_short, 'no[3]',
        c_char, 'flag', 'bweight',
    )


# * tessellation vertex color data.
# * at the moment alpha is abused for vertex painting and not used for transparency, note that red and blue are swapped
class MCol(Structure):
    _fields_ = fields(
        c_uint8, 'a', 'r', 'g', 'b'  # unsigned char
    )


# new face structure, replaces MFace, which is now only used for storing tessellations.
class MPoly(Structure):
    _fields_ = fields(
        # offset into loop array and number of loops in the face 
        c_int, 'loopstart',
        c_int, 'totloop',  # keep signed since we need to subtract when getting the previous loop 
        c_short, 'mat_nr',
        c_char, 'flag', 'pad',
    )

# the e here is because we want to move away from relying on edge hashes.
class MLoop(Structure):
    _fields_ = fields(
        c_uint, 'v',  # vertex index
        c_uint, 'e',  # edge index
    )


class MLoopTri(Structure):
    _fields_ = fields(
        c_uint, 'tri[3]',
        c_uint, 'poly',
    )


class Mesh(Structure):
    """DNA_mesh.types.h: 55"""
    _fields_ = fields(
        ID, 'id',
        c_void, '*adt',  # struct AnimData  # animation data (must be immediately after id for utilities to use it)

        c_void, '*bb',  # struct BoundBox

        c_void, '*ipo',  # struct Ipo  # DNA_DEPRECATED  # old animation system, deprecated for 2.5
        c_void, '*key',  # struct Key
        c_void, '**mat',  # struct Material
        c_void, '*mselect',  # struct MSelect

        # BMESH ONLY
        #new face structures
        c_void, '*mpoly',  # struct MPoly
        c_void, '*mtpoly',  # struct MTexPoly
        c_void, '*mloop',  # struct MLoop
        c_void, '*mloopuv',  # struct MLoopUV
        c_void, '*mloopcol',  # struct MLoopCol
        # END BMESH ONLY

        # mface stores the tessellation (triangulation) of the mesh,
        # real faces are now stored in nface. 
        c_void, '*mface',  # struct MFace  # array of mesh object mode faces for tessellation
        c_void, '*mtface',  # struct MTFace  # store tessellation face UV's and texture here
        c_void, '*tface',  # struct TFace  # DNA_DEPRECATED   # deprecated, use mtface
        c_void, '*mvert',  # struct MVert  # array of verts
        c_void, '*medge',  # struct MEdge  # array of edges
        c_void, '*dvert',  # struct MDeformVert  # deformgroup vertices

        # array of colors for the tessellated faces, must be number of tessellated
        # faces * 4 in length
        c_void, '*mcol',  # struct MCol
        c_void, '*texcomesh',  # struct Mesh

        # When the object is available, the preferred access method is: BKE_editmesh_from_object(ob)
        BMEditMesh, '*edit_btmesh',  # not saved in file!

        # 以下略
    )


BMEditMesh._fields_ = fields(
    c_void_p, 'bm',  # BMesh
    # this is for undoing failed operations
    BMEditMesh, '*emcopy',
    c_int, 'emcopyusers',

    # we store tessellations as triplets of three loops,
    # which each define a triangle.
    c_void_p, 'looptris',  # struct BMLoop *(*looptris)[3]
    c_int, 'tottri',

    # derivedmesh stuff
    DerivedMesh, '*derivedFinal', '*derivedCage',

    # 以下略
)


class CustomDataLayer(Structure):
    _fields_ = fields(
        c_int, 'type',       # type of data in layer
        c_int, 'offset',     # in editmode, offset of layer in block
        c_int, 'flag',       # general purpose flag
        c_int, 'active',     # number of the active layer of this type
        c_int, 'active_rnd', # number of the layer to render
        c_int, 'active_clone', # number of the layer to render
        c_int, 'active_mask', # number of the layer to render
        c_int, 'uid',        # shape keyblock unique id reference
        c_char, 'name[64]',  # layer name, MAX_CUSTOMDATA_LAYER_NAME
        c_void, '*data',     # layer data
    )


class CustomData(Structure):
    _fields_ = fields(
        CustomDataLayer, '*layers',  # CustomDataLayers, ordered by type
        c_int, 'typemap[42]',  # runtime only! - maps types to indices of first layer of that type,
                               # MUST be >= CD_NUMTYPES, but we cant use a define here.
                               # Correct size is ensured in CustomData_update_typemap assert()
        c_int, 'pad_i1',
        c_int, 'totlayer', 'maxlayer',        # number of layers, size of layers array
        c_int, 'totsize',                   # in editmode, total size of all data layers
        c_void, '*pool',  # struct BLI_mempool  # (BMesh Only): Memory pool for allocation of blocks
        c_void, '*external',  # CustomDataExternal  # external file storing customdata layers
    )


class _DerivedMesh_looptris(Structure):
    _fields_ = fields(
        c_void, '*array',  # struct MLoopTri
        c_int, 'num',
        c_int, 'num_alloc',
    )


DerivedMesh._fields_ = fields(
    # * Private DerivedMesh data, only for internal DerivedMesh use
    CustomData, 'vertData', 'edgeData', 'faceData', 'loopData', 'polyData',
    c_int, 'numVertData', 'numEdgeData', 'numTessFaceData', 'numLoopData', 'numPolyData',
    c_int, 'needsFree',  # checked on ->release, is set to 0 for cached results
    c_int, 'deformedOnly',  # set by modifier stack if only deformed from original
    c_void, '*bvhCache',  # typedef struct LinkNode *BVHCache
    c_void, '*drawObject',  # struct GPUDrawObject
    c_int, 'type',  # DerivedMeshType
    c_float, 'auto_bump_scale',
    c_int, 'dirty',  # DMDirtyFlag
    c_int, 'totmat',  # total materials. Will be valid only before object drawing.
    c_void, '**mat',  # struct Material  # material array. Will be valid only before object drawing

    # warning Typical access is done via #getLoopTriArray, #getNumLoopTri.
    _DerivedMesh_looptris, 'looptris',

    # use for converting to BMesh which doesn't store bevel weight and edge crease by default
    c_char, 'cd_flag',

    #* Calculate vert and face normals
    c_void, '*calcNormals',  # void (*calcNormals)(DerivedMesh * dm)

    #* Calculate loop (split) normals
    c_void, '*calcLoopNormals',  # void (*calcLoopNormals)(DerivedMesh * dm, const bool use_split_normals, const float split_angle)

    #* Calculate loop (split) normals, and returns split loop normal spacearr.
    c_void, '*calcLoopNormalsSpaceArray',  # void (*calcLoopNormalsSpaceArray)(DerivedMesh * dm, const bool use_split_normals, const float split_angle,
                                           #       struct MLoopNorSpaceArray *r_lnors_spacearr)

    c_void, '*calcLoopTangents',  # void (*calcLoopTangents)(DerivedMesh * dm)

    # * Recalculates mesh tessellation
    c_void, '*recalcTessellation',  # void (*recalcTessellation)(DerivedMesh * dm)

    # * Loop tessellation cache
    CFUNCTYPE(c_int, POINTER(DerivedMesh)),  '*recalcLoopTri',  # void (*recalcLoopTri)(DerivedMesh * dm)
    # * accessor functions
    CFUNCTYPE(POINTER(MLoopTri), POINTER(DerivedMesh)), '*getLoopTriArray',  #const struct MLoopTri *(*getLoopTriArray)(DerivedMesh * dm)
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), '*getNumLoopTri',  # int (*getNumLoopTri)(DerivedMesh *dm)

    # Misc. Queries

    # Also called in Editmode
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), 'getNumVerts',  # int (*getNumVerts)(DerivedMesh *dm)
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), 'getNumEdges',  # int (*getNumEdges)(DerivedMesh *dm)
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), 'getNumTessFaces',  # int (*getNumTessFaces)(DerivedMesh *dm)
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), 'getNumLoops',  # int (*getNumLoops)(DerivedMesh *dm)
    CFUNCTYPE(c_int, POINTER(DerivedMesh)), 'getNumPolys',  # int (*getNumPolys)(DerivedMesh *dm)

    # * Copy a single vert/edge/tessellated face from the derived mesh into
    # * ``*r_{vert/edge/face}``. note that the current implementation
    # * of this function can be quite slow, iterating over all
    # * elements (editmesh)

    c_void, '*getVert',  # void (*getVert)(DerivedMesh * dm, int index, struct MVert * r_vert)
    c_void, '*getEdge',  # void (*getEdge)(DerivedMesh * dm, int index, struct MEdge * r_edge)
    c_void, '*getTessFace',  # void (*getTessFace)(DerivedMesh * dm, int index, struct MFace * r_face)

    # * Return a pointer to the entire array of verts/edges/face from the
    # * derived mesh. if such an array does not exist yet, it will be created,
    # * and freed on the next ->release(). consider using getVert/Edge/Face if
    # * you are only interested in a few verts/edges/faces.

    CFUNCTYPE(POINTER(MVert), POINTER(DerivedMesh)), 'getVertArray',  # struct MVert *(*getVertArray)(DerivedMesh * dm)
    CFUNCTYPE(POINTER(MEdge), POINTER(DerivedMesh)), 'getEdgeArray',  # struct MEdge *(*getEdgeArray)(DerivedMesh * dm)
    CFUNCTYPE(POINTER(MFace), POINTER(DerivedMesh)), 'getTessFaceArray',  # struct MFace *(*getTessFaceArray)(DerivedMesh * dm)
    CFUNCTYPE(POINTER(MLoop), POINTER(DerivedMesh)), 'getLoopArray',  # struct MLoop *(*getLoopArray)(DerivedMesh * dm)
    CFUNCTYPE(POINTER(MPoly), POINTER(DerivedMesh)), 'getPolyArray',  # struct MPoly *(*getPolyArray)(DerivedMesh * dm)

    # * Copy all verts/edges/faces from the derived mesh into
    # * *{vert/edge/face}_r (must point to a buffer large enough)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), POINTER(MVert)), 'copyVertArray',  # void (*copyVertArray)(DerivedMesh *dm, struct MVert *r_vert);
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), POINTER(MEdge)), 'copyEdgeArray',  # void (*copyEdgeArray)(DerivedMesh *dm, struct MEdge *r_edge);
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), POINTER(MFace)), 'copyTessFaceArray',  # void (*copyTessFaceArray)(DerivedMesh *dm, struct MFace *r_face);
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), POINTER(MLoop)), 'copyLoopArray',  # void (*copyLoopArray)(DerivedMesh *dm, struct MLoop *r_loop);
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), POINTER(MPoly)), 'copyPolyArray',  # void (*copyPolyArray)(DerivedMesh *dm, struct MPoly *r_poly);

    # * Return a copy of all verts/edges/faces from the derived mesh
    # * it is the caller's responsibility to free the returned pointer
    c_void, '*dupVertArray',  # struct MVert *(*dupVertArray)(DerivedMesh * dm);
    c_void, '*dupEdgeArray',  # struct MEdge *(*dupEdgeArray)(DerivedMesh * dm);
    c_void, '*dupTessFaceArray',  # struct MFace *(*dupTessFaceArray)(DerivedMesh * dm);
    c_void, '*dupLoopArray',  # struct MLoop *(*dupLoopArray)(DerivedMesh * dm);
    c_void, '*dupPolyArray',  # struct MPoly *(*dupPolyArray)(DerivedMesh * dm);

    # * Return a pointer to a single element of vert/edge/face custom data
    # * from the derived mesh (this gives a pointer to the actual data, not
    # * a copy)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int, c_int), 'getVertData',  # void *(*getVertData)(DerivedMesh *dm, int index, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int, c_int), 'getEdgeData',  # void *(*getEdgeData)(DerivedMesh *dm, int index, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int, c_int), 'getTessFaceData',  # void *(*getTessFaceData)(DerivedMesh *dm, int index, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int, c_int), 'getPolyData',  # void *(*getPolyData)(DerivedMesh *dm, int index, int type)

    # * Return a pointer to the entire array of vert/edge/face custom data
    # * from the derived mesh (this gives a pointer to the actual data, not
    # * a copy)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int), 'getVertDataArray',  # void *(*getVertDataArray)(DerivedMesh *dm, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int), 'getEdgeDataArray',  # void *(*getEdgeDataArray)(DerivedMesh *dm, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int), 'getTessFaceDataArray',  # void *(*getTessFaceDataArray)(DerivedMesh *dm, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int), 'getLoopDataArray',  # void *(*getLoopDataArray)(DerivedMesh *dm, int type)
    CFUNCTYPE(c_void_p, POINTER(DerivedMesh), c_int), 'getPolyDataArray',  # void *(*getPolyDataArray)(DerivedMesh *dm, int type)

    # /** Retrieves the base CustomData structures for
    #  * verts/edges/tessfaces/loops/facdes*/
    # CustomData *(*getVertDataLayout)(DerivedMesh * dm);
    # CustomData *(*getEdgeDataLayout)(DerivedMesh * dm);
    # CustomData *(*getTessFaceDataLayout)(DerivedMesh * dm);
    # CustomData *(*getLoopDataLayout)(DerivedMesh * dm);
    # CustomData *(*getPolyDataLayout)(DerivedMesh * dm);
    c_void_p, 'getVertDataLayout',
    c_void_p, 'getEdgeDataLayout',
    c_void_p, 'getTessFaceDataLayout',
    c_void_p, 'getLoopDataLayout',
    c_void_p, 'getPolyDataLayout',

    # /** Copies all customdata for an element source into dst at index dest */
    # void (*copyFromVertCData)(DerivedMesh *dm, int source, CustomData *dst, int dest);
    # void (*copyFromEdgeCData)(DerivedMesh *dm, int source, CustomData *dst, int dest);
    # void (*copyFromFaceCData)(DerivedMesh *dm, int source, CustomData *dst, int dest);
    c_void_p, 'copyFromVertCData',
    c_void_p, 'copyFromEdgeCData',
    c_void_p, 'copyFromFaceCData',

    # /** Optional grid access for subsurf */
    # int (*getNumGrids)(DerivedMesh *dm);
    # int (*getGridSize)(DerivedMesh *dm);
    # struct CCGElem **(*getGridData)(DerivedMesh * dm);
    # int *(*getGridOffset)(DerivedMesh * dm);
    # void (*getGridKey)(DerivedMesh *dm, struct CCGKey *key);
    # DMFlagMat *(*getGridFlagMats)(DerivedMesh * dm);
    # unsigned int **(*getGridHidden)(DerivedMesh * dm);
    c_void_p, 'getNumGrids',
    c_void_p, 'getGridSize',
    c_void_p, 'getGridData',
    c_void_p, 'getGridOffset',
    c_void_p, 'getGridKey',
    c_void_p, 'getGridFlagMats',
    c_void_p, 'getGridHidden',

    # /** Iterate over each mapped vertex in the derived mesh, calling the
    #  * given function with the original vert and the mapped vert's new
    #  * coordinate and normal. For historical reasons the normal can be
    #  * passed as a float or short array, only one should be non-NULL.
    #  */
    # void (*foreachMappedVert)(DerivedMesh *dm,
    #                           void (*func)(void *userData, int index, const float co[3],
    #                                        const float no_f[3], const short no_s[3]),
    #                           void *userData,
    #                           DMForeachFlag flag);
    c_void_p, 'foreachMappedVert',

    # /** Iterate over each mapped edge in the derived mesh, calling the
    #  * given function with the original edge and the mapped edge's new
    #  * coordinates.
    #  */
    # void (*foreachMappedEdge)(DerivedMesh *dm,
    #                           void (*func)(void *userData, int index,
    #                                        const float v0co[3], const float v1co[3]),
    #                           void *userData);
    c_void_p, 'foreachMappedEdge',

    # /** Iterate over each mapped loop in the derived mesh, calling the given function
    #  * with the original loop index and the mapped loops's new coordinate and normal.
    #  */
    # void (*foreachMappedLoop)(DerivedMesh *dm,
    #                           void (*func)(void *userData, int vertex_index, int face_index,
    #                                        const float co[3], const float no[3]),
    #                           void *userData,
    #                           DMForeachFlag flag);
    c_void_p, 'foreachMappedLoop',

    # /** Iterate over each mapped face in the derived mesh, calling the
    #  * given function with the original face and the mapped face's (or
    #  * faces') center and normal.
    #  */
    # void (*foreachMappedFaceCenter)(DerivedMesh *dm,
    #                                 void (*func)(void *userData, int index,
    #                                              const float cent[3], const float no[3]),
    #                                 void *userData,
    #                                 DMForeachFlag flag);
    CFUNCTYPE(c_int,
              POINTER(DerivedMesh),
              CFUNCTYPE(c_int, c_void_p, c_int, c_void_p, c_void_p),
              c_void_p,
              c_int),
    'foreachMappedFaceCenter',

    # * Iterate over all vertex points, calling DO_MINMAX with given args.
    # *
    # * Also called in Editmode
    # void (*getMinMax)(DerivedMesh *dm, float r_min[3], float r_max[3]);
    c_void_p, 'getMinMax',

    # * Direct Access Operations
    #  * - Can be undefined
    # * - Must be defined for modifiers that only deform however

    # * Get vertex location, undefined if index is not valid
    # void (*getVertCo)(DerivedMesh *dm, int index, float r_co[3]);
    CFUNCTYPE(c_int, POINTER(DerivedMesh), c_int, c_void_p), 'getVertCo',

    # * Fill the array (of length .getNumVerts()) with all vertex locations
    # void (*getVertCos)(DerivedMesh *dm, float (*r_cos)[3]);
    CFUNCTYPE(c_int, POINTER(DerivedMesh), c_void_p), 'getVertCos',

    # # * Get smooth vertex normal, undefined if index is not valid
    # void (*getVertNo)(DerivedMesh *dm, int index, float r_no[3]);
    # void (*getPolyNo)(DerivedMesh *dm, int index, float r_no[3]);

    # 以下略

)


class ViewContext(Structure):
    """editors/include/ED_view3d.h"""

if version[1] > 76 or version[1] == 76 and version[2] >= 11:
    ViewContext._fields_ = fields(
        c_void_p, 'scene',
        c_void_p, 'obact',
        c_void_p, 'obedit',
        c_void_p, 'ar',
        c_void_p, 'v3d',
        c_void_p, 'win',
        c_void_p, 'rv3d',
        BMEditMesh, '*em',
        c_int, 'mval[2]',
    )
else:
    ViewContext._fields_ = fields(
        c_void_p, 'scene',
        c_void_p, 'obact',
        c_void_p, 'obedit',
        c_void_p, 'ar',
        c_void_p, 'v3d',
        c_void_p, 'rv3d',
        BMEditMesh, '*em',
        c_int, 'mval[2]',
    )


###############################################################################
# BMesh
###############################################################################
# class c_int8_(c_int8):
#     """サブクラス化することでPython型へ透過的に変換しなくなる"""
#     pass


class BMHeader(Structure):
    _fields_ = fields(
        c_void_p, 'data',
        c_int, 'index',
        c_char, 'htype',
        # c_char, 'hflag',
        # c_int8_, 'hflag',
        c_int8, 'hflag',  # ビット演算の為int型にする
        c_char, 'api_flag',
    )


class BMElem(Structure):
    _fields_ = fields(
        BMHeader, 'head',
    )


class BMVert(Structure):
    pass


class BMEdge(Structure):
    pass


class BMFace(Structure):
    pass


class BMLoop(Structure):
    pass


class BMDiskLink(Structure):
    _fields_ = fields(
        BMEdge, '*next',
        BMEdge, '*prev',
    )


BMVert._fields_ = fields(
    BMHeader, 'head',
    c_void_p, 'oflags',  # BMFlagLayer
    c_float, 'co[3]',
    c_float, 'no[3]',
    BMEdge, '*e',
)

BMEdge._fields_ = fields(
    BMHeader, 'head',
    c_void_p, 'oflags',  # BMFlagLayer
    BMVert, '*v1',
    BMVert, '*v2',
    BMLoop, '*l',
    BMDiskLink, 'v1_disk_link',
    BMDiskLink, 'v2_disk_link',
)

BMLoop._fields_ = fields(
    BMHeader, 'head',

    BMVert, '*v',
    BMEdge, '*e',
    BMFace, '*f',

    BMLoop, '*radial_next',
    BMLoop, '*radial_prev',

    BMLoop, '*next',
    BMLoop, '*prev',
)


class BMFace(Structure):
    _fields_ = fields(
        BMHeader, 'head',
        c_void_p, 'oflags',  # BMFlagLayer
        c_void_p, 'l_first',  # BMLoop
        c_int, 'len',
        c_float, 'no[3]',
        c_short, 'mat_nr',
    )


class BMesh(Structure):
    _fields_ = fields(
        c_int, 'totvert', 'totedge', 'totloop', 'totface',
        c_int, 'totvertsel', 'totedgesel', 'totfacesel',

        c_char, 'elem_index_dirty',

        c_char, 'elem_table_dirty',

        c_void, '*vpool', '*epool', '*lpool', '*fpool',  # BLI_mempool

        BMVert, '**vtable',
        BMEdge, '**etable',
        BMFace, '**ftable',

        c_int, 'vtable_tot',
        c_int, 'etable_tot',
        c_int, 'ftable_tot',

        c_void, '*vtoolflagpool', '*etoolflagpool', '*ftoolflagpool',  # struct BLI_mempool

        c_int, 'toolflag_index',
        c_void, '*currentop',  # struct BMOperator

        CustomData, 'vdata', 'edata', 'ldata', 'pdata',
    )


class BMWalker(Structure):
    _fields_ = fields(
        c_char, 'begin_htype',  # only for validating input
        c_void_p, 'begin',  # void  (*begin) (struct BMWalker *walker, void *start)
        c_void_p, 'step',  # void *(*step)  (struct BMWalker *walker)
        c_void_p, 'yield',  # void *(*yield) (struct BMWalker *walker)
        c_int, 'structsize',
        c_int, 'order',  # enum BMWOrder
        c_int, 'valid_mask',

        # runtime
        c_int, 'layer',

        BMesh, '*bm',
        c_void_p, 'worklist',  # BLI_mempool
        ListBase, 'states',

        # these masks are to be tested against elements BMO_elem_flag_test(),
        # should never be accessed directly only through BMW_init() and bmw_mask_check_*() functions
        c_short, 'mask_vert',
        c_short, 'mask_edge',
        c_short, 'mask_face',

        c_int, 'flag',  # enum BMWFlag

        c_void_p, 'visit_set',  # struct GSet *visit_set
        c_void_p, 'visit_set_alt',  # struct GSet *visit_set_alt
        c_int, 'depth',

        c_int, 'dummy[4]',  # enumのサイズが不明な為
    )


###############################################################################
# Python Header
###############################################################################
class PyObject_HEAD(ctypes.Structure):
    _fields_ = [
        # py_object, '_ob_next', '_ob_prev';  # When Py_TRACE_REFS is defined
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.c_void_p),
    ]

class PyObject_VAR_HEAD(ctypes.Structure):
    _fields_ = [
        # py_object, '_ob_next', '_ob_prev';  # When Py_TRACE_REFS is defined
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.c_void_p),
        ('ob_size', ctypes.c_ssize_t),
    ]


###############################################################################
# PropertyRNA
###############################################################################
class _PointerRNA_id(Structure):
    """makesrna/RNA_types.h"""
    _fields_ = fields(
        c_void_p, 'data',
    )


class PointerRNA(Structure):
    """makesrna/RNA_types.h"""
    _fields_ = fields(
        _PointerRNA_id, 'id',
        c_void_p, 'type',  # <StructRNA> &RNA_Operator 等の値
        c_void_p, 'data',
    )


RNA_MAX_ARRAY_DIMENSION = 3  # rna_internal_types.h: 54


class PropertyRNA(Structure):
    """rna_internal_types.h: 155"""

PropertyRNA._fields_ = fields(
    PropertyRNA, '*next', '*prev',

    # magic bytes to distinguish with IDProperty
    c_int, 'magic',

    # unique identifier
    c_char, '*identifier',  # <const char>
    # various options
    c_int, 'flag',

    # user readable name
    c_char, '*name',  # <const char>
    # single line description, displayed in the tooltip for example
    c_char, '*description',  # <const char>
    # icon ID
    c_int, 'icon',
    # context for translation
    c_char, '*translation_context',  # <const char>

    # property type as it appears to the outside
    c_int, 'type',  # <enum: PropertyType>
    # subtype, 'interpretation' of the property
    c_int, 'subtype',  # <enum: PropertySubType>
    # if non-NULL, overrides arraylength. Must not return 0?
    c_void_p, 'getlength',  # <PropArrayLengthGetFunc>
    # dimension of array
    c_uint, 'arraydimension',  # <unsigned int>
    # array lengths lengths for all dimensions (when arraydimension > 0)
    c_uint, 'arraylength[3]',  # <unsigned int> arraylength[RNA_MAX_ARRAY_DIMENSION]
    c_uint, 'totarraylength',  # <unsigned int>

    # callback for updates on change
    c_void_p, 'update',  # <UpdateFunc>
    c_int, 'noteflag',

    # callback for testing if editable
    c_void_p, 'editable',  # <EditableFunc>
    # callback for testing if array-item editable (if applicable)
    c_void_p, 'itemeditable',  # <ItemEditableFunc>

    # raw access
    c_int, 'rawoffset',
    c_int, 'rawtype',  # <enum: RawPropertyType>

    # This is used for accessing props/functions of this property
    # any property can have this but should only be used for collections and arrays
    # since python will convert int/bool/pointer's
    c_void, '*srna',  # <StructRNA>  # attributes attached directly to this collection

    # python handle to hold all callbacks
    # * (in a pointer array at the moment, may later be a tuple)
    c_void, '*py_data',
    )


class FloatPropertyRNA(Structure):
    """rna_internal_types.h: 252"""


PropFloatGetFunc = CFUNCTYPE(c_float, POINTER(PointerRNA))
PropFloatSetFunc = CFUNCTYPE(c_int, POINTER(PointerRNA), c_float)
PropFloatArrayGetFunc = CFUNCTYPE(c_int, POINTER(PointerRNA), POINTER(c_float))
PropFloatArraySetFunc = CFUNCTYPE(c_int, POINTER(PointerRNA), POINTER(c_float))
PropFloatRangeFunc = CFUNCTYPE(c_int, POINTER(PointerRNA),
                               c_float, c_float, c_float, c_float)

FloatPropertyRNA._fields_ = fields(
    PropertyRNA, 'property',

    PropFloatGetFunc, 'get',
    PropFloatSetFunc, 'set',
    PropFloatArrayGetFunc, 'getarray',
    PropFloatArraySetFunc, 'setarray',
    PropFloatRangeFunc, 'range',

    # PropFloatGetFuncEx, 'get_ex',
    # PropFloatSetFuncEx, 'set_ex',
    # PropFloatArrayGetFuncEx, 'getarray_ex',
    # PropFloatArraySetFuncEx, 'setarray_ex',
    # PropFloatRangeFuncEx, 'range_ex',
    #
    # c_float, 'softmin', 'softmax',
    # c_float, 'hardmin', 'hardmax',
    # c_float, 'step',
    # c_int, 'precision',
    #
    # c_float, 'defaultvalue',
    # c_float, '*defaultarray',   # <cost float>
)


class BPy_StructRNA(Structure):
    """python/intern/bpy_rna.h"""
    _fields_ = fields(
        PyObject_HEAD, 'head',
        PointerRNA, 'ptr',
    )


class BPy_PropertyRNA(Structure):
    """python/intern/bpy_rna.h"""
    _fields_ = fields(
        PyObject_HEAD, 'head',
        PointerRNA, 'ptr',
        PropertyRNA, '*prop',
    )


class BPy_PropertyArrayRNA(Structure):
    """python/intern/bpy_rna.h"""
    _fields_ = fields(
        PyObject_HEAD, 'head',
        PointerRNA, 'ptr',
        PropertyRNA, '*prop',
        c_int, 'arraydim',
        c_int, 'arrayoffset',
    )


def RNA_property_float_get_array(ptr, prop, values):
    """
    :param ptr: PointerRNA *ptr
    :type ptr: POINTER(PointerRNA)
    :param prop: PropertyRNA *prop
    :type prop: POINTER(PropertyRNA)
    :param values: float *values
    :type values: POINTER(c_float)
    """
    fprop = cast(prop, POINTER(FloatPropertyRNA)).contents
    fprop.getarray(ptr, cast(values, POINTER(c_float)))


def RNA_property_float_set_array(ptr, prop, values):
    """
    :param ptr: PointerRNA *ptr
    :type ptr: POINTER(PointerRNA)
    :param prop: PropertyRNA *prop
    :type prop: POINTER(PropertyRNA)
    :param values: float *values
    :type values: POINTER(c_float)
    """
    fprop = cast(prop, POINTER(FloatPropertyRNA)).contents
    fprop.setarray(ptr, cast(values, POINTER(c_float)))


def image_pixels_get(image):
    """Image.pixelsをnumpy.ndarrayとして返す。
    :type image: bpy.types.Image
    :return: 要素の型はfloat32でshapeは(row, col)。
    :rtype: numpy.ndarray
    """

    if not isinstance(image, bpy.types.Image):
        raise TypeError()

    image_pixels = image.pixels  # インスタンスは終わるまで残しとかないと駄目
    addr = id(image_pixels)
    bpy_prop = cast(c_void_p(addr), POINTER(BPy_PropertyArrayRNA)).contents
    ptr = cast(c_void_p(ctypes.addressof(bpy_prop.ptr)), POINTER(PointerRNA))
    prop = bpy_prop.prop
    pixels = np.zeros(len(image.pixels), dtype=np.float32)
    RNA_property_float_get_array(ptr, prop, c_void_p(pixels.ctypes.data))
    return pixels


def image_pixels_set(image, pixels):
    """Image.pixelsをpixelsで上書きする。
    :type image: bpy.types.Image
    :param pixels: 要素の型はfloat32にしておく必要がある。それ以外だと変換される。
        要素数の確認は行わないので注意。
    :type pixels: numpy.ndarray
    """

    if not isinstance(image, bpy.types.Image):
        raise TypeError()
    if not isinstance(pixels, np.ndarray):
        raise TypeError()
    if pixels.dtype != np.float32:
        pixels = pixels.astype(np.float32)

    image_pixels = image.pixels
    addr = id(image_pixels)
    bpy_prop = cast(c_void_p(addr), POINTER(BPy_PropertyArrayRNA)).contents
    ptr = cast(c_void_p(ctypes.addressof(bpy_prop.ptr)), POINTER(PointerRNA))
    prop = bpy_prop.prop
    RNA_property_float_set_array(ptr, prop, c_void_p(pixels.ctypes.data))


###############################################################################
def context_py_dict_get(context):
    """CTX_py_dict_get
    :type context: bpy.types.Context
    """
    addr = c_void_p(context.__class__.as_pointer(context))
    C = cast(addr, POINTER(bContext)).contents
    if C.data.py_context is None:  # NULL
        return None
    else:
        return cast(C.data.py_context, py_object).value


def context_py_dict_set(context, py_dict):
    """CTX_py_dict_set
    :type context: bpy.types.Context
    :type py_dict: dict | None
    :rtype: dict
    """
    py_dict_bak = context_py_dict_get(context)

    addr = c_void_p(context.__class__.as_pointer(context))
    C = cast(addr, POINTER(bContext)).contents
    if isinstance(py_dict, dict):
        C.data.py_context = c_void_p(id(py_dict))
    else:
        C.data.py_context = None  # NULL
    return py_dict_bak


def test_platform():
    return (platform.platform().split('-')[0].lower()
            not in {'darwin', 'windows'})


def context_py_dict_get_linux(context):
    """ctypes.CDLLを用いる方法"""

    if not test_platform():
        raise OSError('Linux only')
    blend_cdll = CDLL('')
    CTX_py_dict_get = blend_cdll.CTX_py_dict_get
    CTX_py_dict_get.restype = c_void_p
    addr = context.__class__.as_pointer(context)  # 警告抑制の為
    C = cast(c_void_p(addr), POINTER(bContext))
    ptr = CTX_py_dict_get(C)
    if ptr is not None:  # int
        return cast(c_void_p(ptr), py_object).value
    else:
        return None


def context_py_dict_set_linux(context, py_dict):
    """ctypes.CDLLを用いる方法"""

    if not test_platform():
        raise OSError('Linux only')
    blend_cdll = CDLL('')
    CTX_py_dict_set = blend_cdll.CTX_py_dict_set
    addr = context.__class__.as_pointer(context)  # 警告抑制の為
    C = cast(c_void_p(addr), POINTER(bContext))
    context_dict_back = context_py_dict_get(context)
    if py_dict is not None:
        CTX_py_dict_set(C, py_object(py_dict))
    else:
        # CTX_py_dict_set(C, py_object())
        CTX_py_dict_set(C, None)
    return context_dict_back


###############################################################################
class _Buffer_buf(ctypes.Union):
    _fields_ = [
        ('asbyte', ctypes.POINTER(ctypes.c_char)),
        ('asshort', ctypes.POINTER(ctypes.c_short)),
        ('asint', ctypes.POINTER(ctypes.c_int)),
        ('asfloat', ctypes.POINTER(ctypes.c_float)),
        ('asdouble', ctypes.POINTER(ctypes.c_double)),

        ('asvoid', ctypes.c_void_p),
    ]


class Buffer(ctypes.Structure):
    _anonymous_ = ('_head',)
    _fields_ = [
        ('_head', PyObject_VAR_HEAD),
        ('parent', ctypes.py_object),

        ('type', ctypes.c_int),   # GL_BYTE, GL_SHORT, GL_INT, GL_FLOAT
        ('ndimensions', ctypes.c_int),
        ('dimensions', ctypes.POINTER(ctypes.c_int)),

        ('buf', _Buffer_buf),
    ]


def buffer_to_ctypes(buf):
    import ctypes as ct
    c_buf_p = ct.cast(ct.c_void_p(id(buf)), ct.POINTER(Buffer))
    c_buf = c_buf_p.contents
    types = {
        bgl.GL_BYTE: ct.c_byte,
        bgl.GL_SHORT: ct.c_short,
        bgl.GL_INT: ct.c_int,
        bgl.GL_FLOAT: ct.c_float,
        bgl.GL_DOUBLE: ct.c_double
    }
    t = types[c_buf.type]
    n = c_buf.ndimensions
    for i in range(n - 1, -1, -1):
        t *= c_buf.dimensions[i]
    ct_buf = ct.cast(c_buf.buf.asvoid, ct.POINTER(t)).contents
    return ct_buf


def buffer_to_ndarray(buf):
    import numpy as np
    return np.ctypeslib.as_array(buffer_to_ctypes(buf))


###############################################################################
# ポインタアドレスからpythonオブジェクトを生成する。
# bpy.context.active_object.as_pointer() -> int の逆の動作。

# class BlenderRNA(Structure):
#     _fields_ = [
#         ('structs', ListBase),
#     ]

# 未使用
def create_python_object(id_addr, type_name, addr):
    """アドレスからpythonオブジェクトを作成する。
    area = create_python_object(C.screen.as_pointer(), 'Area',
                                C.area.as_pointer())
    obj = create_python_object(C.active_object.as_pointer(), 'Object',
                               C.active_object.as_pointer())

    :param id_addr: id_dataのアドレス。自身がIDオブジェクトならそれを指定、
        そうでないなら所属するIDオブジェクトのアドレスを指定する。
        AreaならScreen、ObjectならObjectのアドレスとなる。無い場合はNone。
        正しく指定しないと予期しない動作を起こすので注意。
    :type id_addr: int | None
    :param type_name: 型名。'Area', 'Object' 等。
        SpaceView3D等のSpaceのサブクラスは'Space'でよい。
    :type type_name: str
    :param addr: オブジェクトのアドレス。
    :type addr: int
    :rtype object
    """

    class _PointerRNA_id(Structure):
        _fields_ = [
            ('data', c_void_p),
        ]

    class PointerRNA(Structure):
        _fields_ = [
            ('id', _PointerRNA_id),
            ('type', c_void_p),  # StructRNA
            ('data', c_void_p),
        ]

    if (not isinstance(id_addr, (int, type(None))) or
            not isinstance(type_name, str) or
            not isinstance(addr, int)):
        raise TypeError('引数の型が間違ってる。(int, str, int)')

    blend_cdll = CDLL('')
    RNA_pointer_create = blend_cdll.RNA_pointer_create
    RNA_pointer_create.restype = None
    pyrna_struct_CreatePyObject = blend_cdll.pyrna_struct_CreatePyObject
    pyrna_struct_CreatePyObject.restype = py_object
    try:
        RNA_type = getattr(blend_cdll, 'RNA_' + type_name)
    except AttributeError:
        raise ValueError("型名が間違ってる。'{}'".format(type_name))

    ptr = PointerRNA()
    RNA_pointer_create(c_void_p(id_addr), RNA_type, c_void_p(addr), byref(ptr))
    return pyrna_struct_CreatePyObject(byref(ptr))


class SnapObjects:
    """
    使用例:
    class Operator(bpy.types.Operator):
        def modal(self, context, event):
            mval = event.mouse_region_x, event.mouse_region_y
            r = self.snap_objects.snap(context, mval, 'VERTEX')
            if r:
                # keys: 'location', 'normal', 'index', 'object'
                # location,normalはworld座標
                ...

            # mesh等が更新されたらキャッシュ等を再生成
            self.snap_objects.update()

            # オペレーター終了時には開放を忘れない。
            __del__で開放するようにしているが、context.modeの変更で落ちる為
            手動で行う。
            self.snap_objects.free()
            return {'FINISHED'}

        def invoke(self, context, event):
            self.snap_objects = SnapObjects(context)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    このクラスを丸々コピペして動くようにcreate_python_object等を
    メソッドにしている

    """

    # enum SnapSelect
    SNAP_ALL = 0
    SNAP_NOT_SELECTED = 1
    SNAP_NOT_ACTIVE = 2

    SNAP_MIN_DISTANCE = 30

    SNAP_OBJECT_USE_CACHE = 1 << 0

    # tool_settings.snap_mode
    # SCE_SNAP_MODE_INCREMENT = 0
    SCE_SNAP_MODE_VERTEX = 1
    SCE_SNAP_MODE_EDGE = 2
    SCE_SNAP_MODE_FACE = 3
    # SCE_SNAP_MODE_VOLUME = 4
    # SCE_SNAP_MODE_NODE_X = 5
    # SCE_SNAP_MODE_NODE_Y = 6
    # SCE_SNAP_MODE_NODE_XY = 7
    # SCE_SNAP_MODE_GRID = 8

    BM_ELEM_SELECT = 1 << 0
    BM_ELEM_HIDDEN = 1 << 1

    def __init__(self, context=None):
        self.object_context = None
        if context:
            self.ensure(context)

    def __del__(self):
        self.free()

    def snap_object_context_create_view3d(self, context):
        import bpy
        import ctypes as ct
        cdll = ct.CDLL('')
        func = cdll.ED_transform_snap_object_context_create_view3d
        func.restype = ct.c_void_p

        # area = context.area
        # if not area:
        #     raise ValueError('context.areaがNone')
        # if area.type != 'VIEW_3D':
        #     raise ValueError("context.areaが3DViewではない")

        region = context.region
        if not region:
            raise ValueError('context.regionがNone')
        if region.type != 'WINDOW':
            raise ValueError("context.region.typeが'WINDOW'ではない")
        ar = ct.c_void_p(region.as_pointer())

        view3d = context.space_data
        if not isinstance(view3d, bpy.types.SpaceView3D):
            raise ValueError('context.space_dataがSpaceView3Dではない')
        v3d = ct.c_void_p(view3d.as_pointer())

        bl_main = ct.c_void_p(bpy.data.as_pointer())
        scn = ct.c_void_p(context.scene.as_pointer())
        object_context = func(bl_main, scn, self.SNAP_OBJECT_USE_CACHE, ar, v3d)
        return ct.c_void_p(object_context)

    def ensure(self, context):
        if not self.object_context:
            self.object_context = self.snap_object_context_create_view3d(
                context)

    def update(self, context):
        if self.object_context:
            self.free()
        self.object_context = self.snap_object_context_create_view3d(context)

    def free(self):
        # 開放前にcontext.modeを切り替えてはならない。落ちる。
        import ctypes as ct
        cdll = ct.CDLL('')
        if self.object_context:
            cdll.ED_transform_snap_object_context_destroy(self.object_context)
            self.object_context = None

    def set_editmesh_callbacks(self):
        # ED_transform_snap_object_context_set_editmesh_callbacks(
        #     object_context,
        #        (bool(*)(BMVert *, void *))
        # BM_elem_cb_check_hflag_disabled,
        # bm_edge_is_snap_target,
        # bm_face_is_snap_target,
        # SET_UINT_IN_POINTER((BM_ELEM_SELECT | BM_ELEM_HIDDEN)))

        import ctypes as ct
        cdll = ct.CDLL('')
        func = cdll.ED_transform_snap_object_context_set_editmesh_callbacks
        vfunc = ct.c_void_p(ct.addressof(cdll.BM_elem_cb_check_hflag_disabled))
        # FIXME: efunc,ffuncはstatucで参照出来ない為このコードは動かない
        efunc = ct.c_void_p(ct.addressof(cdll.bm_edge_is_snap_target))
        ffunc = ct.c_void_p(ct.addressof(cdll.bm_face_is_snap_target))

        user_data = ct.c_void_p(self.BM_ELEM_SELECT | self.BM_ELEM_HIDDEN)
        func(self.object_context, vfunc, efunc, ffunc, user_data)

    def create_python_object(self, id_addr, type_name, addr):
        """アドレスからpythonオブジェクトを作成する。
        area = create_python_object(C.screen.as_pointer(), 'Area',
                                    C.area.as_pointer())
        obj = create_python_object(C.active_object.as_pointer(), 'Object',
                                   C.active_object.as_pointer())

        :param id_addr: id_dataのアドレス。自身がIDオブジェクトならそれを指定、
            そうでないなら所属するIDオブジェクトのアドレスを指定する。
            AreaならScreen、ObjectならObjectのアドレスとなる。無い場合はNone。
            正しく指定しないと予期しない動作を起こすので注意。
        :type id_addr: int | None
        :param type_name: 型名。'Area', 'Object' 等。
            SpaceView3D等のSpaceのサブクラスは'Space'でよい。
        :type type_name: str
        :param addr: オブジェクトのアドレス。
        :type addr: int
        :rtype object
        """

        import ctypes as ct

        class _PointerRNA_id(ct.Structure):
            _fields_ = [
                ('data', ct.c_void_p),
            ]

        class PointerRNA(ct.Structure):
            _fields_ = [
                ('id', _PointerRNA_id),
                ('type', ct.c_void_p),  # StructRNA
                ('data', ct.c_void_p),
            ]

        if (not isinstance(id_addr, (int, type(None))) or
                not isinstance(type_name, str) or
                not isinstance(addr, int)):
            raise TypeError('引数の型が間違ってる。(int, str, int)')

        cdll = ct.CDLL('')
        RNA_pointer_create = cdll.RNA_pointer_create
        RNA_pointer_create.restype = None
        pyrna_struct_CreatePyObject = cdll.pyrna_struct_CreatePyObject
        pyrna_struct_CreatePyObject.restype = ct.py_object
        try:
            RNA_type = getattr(cdll, 'RNA_' + type_name)
        except AttributeError:
            raise ValueError("型名が間違ってる。'{}'".format(type_name))

        ptr = PointerRNA()
        RNA_pointer_create(ct.c_void_p(id_addr), RNA_type, ct.c_void_p(addr),
                           ct.byref(ptr))
        return pyrna_struct_CreatePyObject(ct.byref(ptr))

    def snap(self, context, mval, snap_element=None, snap_select='ALL',
             dist_px=SNAP_MIN_DISTANCE):
        import ctypes as ct
        from mathutils import Vector

        cdll = ct.CDLL('')

        if not self.object_context:
            self.ensure(context)

        mval = (ct.c_float * 2)(*mval)
        dist_px = ct.c_float(dist_px)
        r_loc = (ct.c_float * 3)()
        r_no = (ct.c_float * 3)()
        r_index = ct.c_int()
        r_ob = ct.c_void_p()
        actob = context.active_object

        class SnapObjectParams(ct.Structure):
            _fields_ = [
                ('snap_select', ct.c_char),
                ('use_object_edit_cage', ct.c_ubyte),  # unsigned int
            ]

        if snap_select not in {'ALL', 'NOT_SELECTED', 'NOT_ACTIVE'}:
            raise ValueError(
                "snap_select not in {'ALL', 'NOT_SELECTED', 'NOT_ACTIVE'}")
        d = {'ALL': self.SNAP_ALL,
             'NOT_SELECTED': self.SNAP_NOT_SELECTED,
             'SNAP_NOT_ACTIVE': self.SNAP_NOT_ACTIVE
             }
        snap_select = d[snap_select]
        params = SnapObjectParams(snap_select, actob and actob.mode == 'EDIT')

        # self.set_editmesh_callbacks()

        if snap_element:
            snap_mode = snap_element
        else:
            snap_mode = context.tool_settings.snap_element
        if snap_mode not in {'VERTEX', 'EDGE', 'FACE'}:
            if snap_element:
                raise ValueError(
                    "snap_element not in {'VERTEX', 'EDGE', 'FACE'}")
            else:
                return None
        d = {
            # 'INCREMENT': SCE_SNAP_MODE_INCREMENT,
            'VERTEX': self.SCE_SNAP_MODE_VERTEX,
            'EDGE': self.SCE_SNAP_MODE_EDGE,
            'FACE': self.SCE_SNAP_MODE_FACE,
            # 'VOLUME': SCE_SNAP_MODE_VOLUME,
        }
        snap_to = d[snap_mode]

        found = cdll.ED_transform_snap_object_project_view3d_ex(
            self.object_context, snap_to, ct.byref(params), mval,
            ct.byref(dist_px), None, r_loc, r_no, ct.byref(r_index),
            ct.byref(r_ob),
        )

        if found:
            ob = self.create_python_object(r_ob.value, 'Object', r_ob.value)
            return {'location': Vector(r_loc),
                    'normal': Vector(r_no),
                    'index': r_index.value,
                    'object': ob}
        else:
            return None
