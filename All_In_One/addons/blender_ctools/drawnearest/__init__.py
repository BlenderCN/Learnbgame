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
    'name': 'Edit Mesh Draw Nearest',
    'author': 'chromoly',
    'version': (0, 4),
    'blender': (2, 77, 0),
    'location': 'View3D > Properties Panel > Mesh Display',
    'wiki_url': 'https://github.com/chromoly/blender-EditMeshDrawNearest',
    'category': '3D View',
}


"""
MeshのEditModeに於いて、右クリックで選択される頂点/辺/面を強調表示する。
"""


import collections
import contextlib
from ctypes import addressof, sizeof, byref, c_bool, pointer
import enum
import functools
import importlib
import inspect
import numpy as np
import math

import bpy
import bmesh
import mathutils
from mathutils import Matrix, Vector
import bgl
import blf
# from bpy_extras.view3d_utils import location_3d_to_region_2d as project

try:
    importlib.reload(structures)
    importlib.reload(utils)
except NameError:
    pass
from .structures import *
from .utils import AddonPreferences, SpaceProperty, operator_call


# glVertexへ渡すZ値。
OVERLAY_MASK_Z = 100.0 - 1e-5
OVERLAY_DRAW_Z = OVERLAY_MASK_Z - 1e-5

# solid表示で辺を描画する際にED_view3d_polygon_offsetへ渡す値
POLYGON_OFFSET_EDGE = 1.05


def test_platform():
    return (platform.platform().split('-')[0].lower()
            not in {'darwin', 'windows'})


###############################################################################
# Addon Preferences
###############################################################################
class DrawNearestPreferences(
        AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    draw_set_vert = bpy.props.EnumProperty(
        name='Draw Vertex',
        items=(('VERT', 'Vert', ''),),
        default={'VERT'},
        options={'ENUM_FLAG'}
    )
    draw_set_edge = bpy.props.EnumProperty(
        name='Draw Edge',
        items=(('VERT', 'Vert', ''),
               ('EDGE', 'Edge', '')),
        default={'VERT', 'EDGE'},
        options={'ENUM_FLAG'}
    )
    draw_set_face = bpy.props.EnumProperty(
        name='Draw Face',
        items=(('VERT', 'Vert', ''),
               ('EDGE', 'Edge', ''),
               ('FACE', 'Face', '')),
        default={'VERT', 'EDGE', 'FACE'},
        options={'ENUM_FLAG'}
    )

    use_overlay = bpy.props.BoolProperty(
        name='Overlay',
    )

    select_color = bpy.props.FloatVectorProperty(
        name='Select Color',
        default=(0.0, 0.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR_GAMMA',
        size=4
    )
    vertex_size = bpy.props.IntProperty(
        name='Vertex Size',
        default=15,
        min=1,
        max=30,
    )
    vertex_line_width = bpy.props.IntProperty(
        name='Vertex Line Width',
        default=2,
        min=1,
        max=5,
    )
    edge_line_width = bpy.props.IntProperty(
        name='Edge Line Width',
        default=2,
        min=1,
        max=10,
    )
    edge_line_stipple = bpy.props.IntProperty(
        name='Line Stipple',
        default=5,
        min=0,
        max=20,
    )
    face_emphasis = bpy.props.EnumProperty(
        name='Face Emphasis',
        items=(('FILL', 'Fill', ''),
               ('CENTER', 'Center', '')),
        default='FILL',
    )
    face_stipple = bpy.props.IntProperty(
        name='Face Fill Stipple',
        description='Fill pattern size',
        default=2,
        min=1,
        max=4,
    )
    face_center_size = bpy.props.IntProperty(
        name='Face Center Size',
        default=12,
        min=0,
        max=30,
    )
    face_center_line_width = bpy.props.IntProperty(
        name='Face Center Line Width',
        default=1,
        min=0,
        max=10,
    )

    use_loop_select = bpy.props.BoolProperty(
        name='Loop Select',
        default=True,
    )
    loop_select_color = bpy.props.FloatVectorProperty(
        name='Loop Select Color',
        default=(0.0, 0.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR_GAMMA',
        size=4
    )
    loop_select_line_width = bpy.props.IntProperty(
        name='Loop Select Line Width',
        default=3,
        min=0,
        max=10,
    )
    loop_select_line_stipple = bpy.props.IntProperty(
        name='Loop Select Line Stipple',
        default=4,
        min=0,
        max=20,
    )
    loop_select_face_stipple = bpy.props.IntProperty(
        name='Loop Select Face Stipple',
        description='Dot pattern size',
        default=2,
        min=1,
        max=4,
    )

    redraw_all = bpy.props.BoolProperty(
        name='Redraw All 3D View',
    )
    mask = bpy.props.EnumProperty(
        name='Mask',
        items=(('DEPTH', 'DEPTH_TEST', ''),
               ('STENCIL', 'STENCIL_TEST', ''),
               ('NONE', 'None', '')),
        default='NONE',
    )
    use_internal = bpy.props.BoolProperty(
        name='Internal Functions',
        description='Faster (linux only)',
        default=False,
    )
    use_derived_mesh = bpy.props.BoolProperty(
        name='DerivedMesh',
        description='Use mesh->edit_btmesh->derivedCage',
        default=False,
    )

    def draw(self, context):
        split = self.layout.split()

        column = split.column()
        col = column.column()
        col.label('Draw:')
        col.label('Vertex:')
        row = col.row()
        sp = row.split(1.0 / 3)
        sp.row().prop(self, 'draw_set_vert')
        col.label('Edge:')
        row = col.row()
        sp = row.split(1.0 / 3 * 2)
        sp.row().prop(self, 'draw_set_edge')
        col.label('Face:')
        row = col.row()
        sp = row.split()
        sp.row().prop(self, 'draw_set_face')

        column = split.column()

        column.prop(self, 'select_color')
        column.prop(self, 'vertex_size')
        column.prop(self, 'vertex_line_width')
        column.prop(self, 'edge_line_width')
        column.prop(self, 'edge_line_stipple')
        column.prop(self, 'face_emphasis')
        if self.face_emphasis == 'FILL':
            column.prop(self, 'face_stipple')
        else:
            column.prop(self, 'face_center_size')
            column.prop(self, 'face_center_line_width')

        column = split.column()
        column.prop(self, 'use_loop_select')
        sub = column.column()
        sub.active = self.use_loop_select
        sub.prop(self, 'loop_select_color')
        sub.prop(self, 'loop_select_line_width')
        sub.prop(self, 'loop_select_line_stipple')
        sub.prop(self, 'loop_select_face_stipple')

        column = split.column()
        column.prop(self, 'use_overlay')
        column.prop(self, 'redraw_all')
        column.prop(self, 'mask')

        col = column.column()
        col.separator()
        col.label('ctypes:')
        col.prop(self, 'use_derived_mesh')
        sub = col.column()
        sub.active = test_platform()
        sub.prop(self, 'use_internal')


###############################################################################
# Space Property
###############################################################################
class VIEW3D_PG_DrawNearest(bpy.types.PropertyGroup):
    def update(self, context):
        arg = 'ENABLE' if self.enable else 'DISABLE'
        bpy.ops.view3d.draw_nearest_element('INVOKE_DEFAULT', type=arg)

    enable = bpy.props.BoolProperty(
        name='Enable', update=update)


space_prop = SpaceProperty(
    [bpy.types.SpaceView3D, 'drawnearest',
     VIEW3D_PG_DrawNearest])


###############################################################################
# GLSettings
###############################################################################
class Buffer:
    def __new__(self, type, dimensions=0, template=None):
        """
        :param type: GL_BYTE('bool','byte'), GL_SHORT('short'),
            GL_INT('int'), GL_FLOAT('float') or GL_DOUBLE('double')
        :type type: int | str
        :param dimensions: array size.
            e.g. 3:      [0, 0, 0]
                 [4, 2]: [(0, 0), (0, 0), (0, 0), (0, 0)]
        :type dimensions: int | list | tuple
        :param template: Used to initialize the Buffer
            e.g. list: [1, 2, 3], int: bgl.GL_BLEND
        :type template: None | sequence | int
        :return:
        :rtype:
        """
        if isinstance(type, str):
            type = type.lower()
            if type in ('bool', 'byte'):
                type = bgl.GL_BYTE
            elif type == 'short':
                type = bgl.GL_SHORT
            elif type == 'int':
                type = bgl.GL_INT
            elif type == 'float':
                type = bgl.GL_FLOAT
            elif type == 'double':
                type = bgl.GL_DOUBLE
            else:
                type = None

        return_int = isinstance(dimensions, int) and dimensions < 1
        if return_int:
            dim = 1
        else:
            dim = dimensions
        if template is None:
            buf = bgl.Buffer(type, dim)
        elif isinstance(template, int):
            if type == bgl.GL_BYTE:
                glGet = bgl.glGetBooleanv
            elif type == bgl.GL_SHORT:
                glGet = bgl.glGetIntegerv
            elif type == bgl.GL_INT:
                glGet = bgl.glGetIntegerv
            elif type == bgl.GL_FLOAT:
                glGet = bgl.glGetFloatv
            elif type == bgl.GL_DOUBLE:
                glGet = bgl.glGetDoublev
            else:
                msg = "invalid first argument type, should be one of " \
                      "GL_BYTE('bool','byte'), GL_SHORT('short'), " \
                      "GL_INT('int'), GL_FLOAT('float') or GL_DOUBLE('double')"
                raise AttributeError(msg)
            buf = bgl.Buffer(type, dim)
            glGet(template, buf)
        else:
            buf = bgl.Buffer(type, dim, template)

        if return_int:
            return buf[0]
        else:
            return buf


def glSwitch(attr, value):
    if value:
        bgl.glEnable(attr)
    else:
        bgl.glDisable(attr)


class GCM(contextlib._GeneratorContextManager):
    @classmethod
    def contextmanager(cls, func):
        sig = inspect.signature(cls.__init__)
        if '*' in str(sig.parameters['args']):
            @functools.wraps(func)
            def _func(*args, **kwargs):
                return cls(func, *args, **kwargs)
        else:
            @functools.wraps(func)
            def _func(*args, **kwargs):
                return cls(func, args, kwargs)
        return _func

    def enter(self, result=False):
        """
        :type result: bool
        :rtype: GCM | (GCM, T)
        """
        r = self.__enter__()
        if result:
            return self, r
        else:
            return self

    def exit(self):
        self.__exit__(None, None, None)


class GLSettings:
    def __init__(self, context, view_matrix=None, perspective_matrix=None):
        rv3d = context.region_data
        if view_matrix is None:
            if rv3d:
                view_matrix = rv3d.view_matrix
            else:
                view_matrix = Matrix.Identity(4)
        if perspective_matrix is None:
            if rv3d:
                perspective_matrix = rv3d.perspective_matrix
            else:
                perspective_matrix = Matrix.Identity(4)
        window_matrix = perspective_matrix * view_matrix.inverted()

        # type: <mathutils.Matrix>
        self.view_matrix = view_matrix
        self.window_matrix = window_matrix
        self.perspective_matrix = perspective_matrix

        # type: <bgl.Buffer>
        self.modelview_matrix = Buffer(
            'double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        self.projection_matrix = Buffer(
            'double', (4, 4), bgl.GL_PROJECTION_MATRIX)

        self._modelview_stack = []  # used in pop(), push()
        self._projection_stack = []  # used in pop(), push()

        region = context.region
        self.region_size = region.width, region.height
        window = context.window
        self.window_size = window.width, window.height

        # staticmethod
        self.Buffer = Buffer
        self.glSwitch = glSwitch

    # @staticmethod
    # def Buffer(type, dimensions=0, template=None):
    #     return Buffer(type, dimensions, template)

    # @staticmethod
    # def glSwitch(attr, value):
    #     glSwitch(attr, value)

    @staticmethod
    def mul_4x4_matrixd(m1, m2):
        """double型で大きさが16のBuffer同士の積"""
        matrix_mode = Buffer('int', 0, bgl.GL_MATRIX_MODE)
        bgl.glMatrixMode(bgl.GL_MODELVIEW)  # GL_MAX_MODELVIEW_STACK_DEPTH: 32
        bgl.glPushMatrix()
        bgl.glLoadMatrixd(m1)
        bgl.glMultMatrixd(m2)
        mat = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        bgl.glPopMatrix()
        bgl.glMatrixMode(matrix_mode)
        return mat

    @classmethod
    def get_matrix(cls, matrix_type, buffer=False):
        """GL_MODELVIEW_MATRIX, GL_PROJECTION_MATRIX を元にしたMatrixを返す。
        self.modelview_matrix等のインスタンス属性は使用しない。
        Spaceのコールバック関数の中でこのメソッドを呼んだ場合、
        PRE_VIEW / POST_VIEW と POST_PIXEL で違いがあるので十分注意すること。
        :param buffer: TrueだとBufferオブジェクトを返す。
        :rtype: Matrix | Buffer
        """
        if isinstance(matrix_type, int):
            if matrix_type == bgl.GL_MODELVIEW_MATRIX:
                matrix_type = 'modelview'
            elif matrix_type == bgl.GL_PROJECTION_MATRIX:
                matrix_type = 'projection'
            else:
                return None
        elif isinstance(matrix_type, str):
            matrix_type = matrix_type.lower()
        else:
            return None

        modelview = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        vmat = Matrix(modelview).transposed()
        if matrix_type.startswith(('model', 'view')):
            if buffer:
                return modelview
            else:
                return vmat
        else:
            projection = Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX)
            wmat = Matrix(projection).transposed()
            if matrix_type.startswith(('proj', 'win')):
                if buffer:
                    return projection
                else:
                    return wmat
            elif matrix_type.startswith('pers'):
                if buffer:
                    return cls.mul_4x4_matrixd(projection, modelview)
                else:
                    return wmat * vmat

    @staticmethod
    def font_size(id=0, size=11, dpi=None):
        if dpi is None:
            dpi = bpy.context.user_preferences.system.dpi
        blf.size(id, size, dpi)

    @classmethod
    def _load_matrix(cls, modelview=None, projection=None):
        matrix_mode = Buffer('int', 0, bgl.GL_MATRIX_MODE)
        if modelview:
            bgl.glMatrixMode(bgl.GL_MODELVIEW)
            bgl.glLoadIdentity()  # glLoadMatrix()にも必須
            if isinstance(modelview, bgl.Buffer):
                bgl.glLoadMatrixd(modelview)
        if projection:
            bgl.glMatrixMode(bgl.GL_PROJECTION)
            bgl.glLoadIdentity()  # glLoadMatrix()にも必須
            if isinstance(projection, bgl.Buffer):
                bgl.glLoadMatrixd(projection)
        bgl.glMatrixMode(matrix_mode)

    def push(self, mask=bgl.GL_ALL_ATTRIB_BITS):
        """glPushAttrib()で状態変数を保存しておく。
        glPushMatrix(), glPopMatrix() は GL_MAX_MODELVIEW_STACK_DEPTH が 32
        なのに対し、GL_MAX_PROJECTION_STACK_DEPTH が 4 しか無い為、使用しない。
        """
        bgl.glPushAttrib(mask)
        self._modelview_stack.append(
            Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX))
        self._projection_stack.append(
            Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX))

    def pop(self):
        """push()時の状態に戻す。"""
        self._load_matrix(self._modelview_stack.pop(),
                          self._projection_stack.pop())
        bgl.glPopAttrib()

    @classmethod
    @GCM.contextmanager
    def push_attrib(cls, mask=bgl.GL_ALL_ATTRIB_BITS, matrix=True):
        """with文で使用する。
        with GLSettings.push_attrib():
            ...
        :rtype: GCM
        """

        bgl.glPushAttrib(mask)
        modelview = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        projection = Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX)
        yield
        if matrix:
            cls._load_matrix(modelview, projection)
        bgl.glPopAttrib()

    @GCM.contextmanager
    def region_view3d_space(self):
        """with文、又はデコレータとして使用
        :rtype: GCM
        """
        modelview_mat = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        projection_mat = Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX)
        view_mat = Buffer('double', (4, 4), self.view_matrix.transposed())
        win_mat = Buffer('double', (4, 4), self.window_matrix.transposed())
        self._load_matrix(view_mat, win_mat)

        try:
            yield
        finally:
            self._load_matrix(modelview_mat, projection_mat)

    @GCM.contextmanager
    def region_pixel_space(self):
        """with文、又はデコレータとして使用

        NOTE: Z値の範囲: near 〜 far
        perspective_matrix * vec4d / w: -1.0 〜 +1.0
        gluProject: 0.0 〜 +1.0
        POST_PIXEL: +100 〜 -100
        Z-Buffer: 0.0 〜 +1.0
        :rtype: GCM
        """

        modelview_mat = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        projection_mat = Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX)
        matrix_mode = Buffer('int', 1, bgl.GL_MATRIX_MODE)

        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glLoadIdentity()  # 必須
        w, h = self.region_size
        # wmOrtho2_region_pixelspace(), wmOrtho2() 参照
        ofs = -0.01
        bgl.glOrtho(ofs, w + ofs, ofs, h + ofs, -100, 100)

        bgl.glMatrixMode(bgl.GL_MODELVIEW)
        bgl.glLoadIdentity()

        bgl.glMatrixMode(matrix_mode[0])

        try:
            yield
        finally:
            self._load_matrix(modelview_mat, projection_mat)

    @GCM.contextmanager
    def window_pixel_space(self):
        """with文、又はデコレータとして使用
        :rtype: GCM
        """

        win_width, win_height = self.window_size

        modelview_mat = Buffer('double', (4, 4), bgl.GL_MODELVIEW_MATRIX)
        projection_mat = Buffer('double', (4, 4), bgl.GL_PROJECTION_MATRIX)
        matrix_mode = Buffer('int', 1, bgl.GL_MATRIX_MODE)
        viewport = Buffer('int', 4, bgl.GL_VIEWPORT)

        bgl.glViewport(0, 0, win_width, win_height)
        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glLoadIdentity()
        ofs = -0.01
        bgl.glOrtho(ofs, win_width + ofs, ofs, win_height + ofs, -100, 100)
        bgl.glMatrixMode(bgl.GL_MODELVIEW)
        bgl.glLoadIdentity()
        bgl.glMatrixMode(matrix_mode[0])

        try:
            yield
        finally:
            bgl.glViewport(*viewport)
            self._load_matrix(modelview_mat, projection_mat)

        # NOTE:
        # PyOpenGLの場合
        # modelview_mat = (ctypes.c_double * 16)()
        # glGetDoublev(GL_MODELVIEW_MATRIX, ctypes.byref(modelview_mat))
        #
        # glMatrixMode()等でパラメーターにGLenumが要求される場合は
        # c_uintでなければならない
        # matrix_mode = ctypes.c_uint()
        # glGetIntegerv(GL_MATRIX_MODE, ctypes.byref(matrix_mode))
        # glMatrixMode(matrix_mode)


###############################################################################
# Find - ctypes
###############################################################################
class BMWSelect(enum.IntEnum):  # 名前は適当
    """bmesh/intern/bmesh_walkers.h: 115"""
    BMW_VERT_SHELL = 0
    BMW_LOOP_SHELL = 1
    BMW_LOOP_SHELL_WIRE = 2
    BMW_FACE_SHELL = 3
    BMW_EDGELOOP = 4
    BMW_FACELOOP = 5
    BMW_EDGERING = 6
    BMW_EDGEBOUNDARY = 7
    # BMW_RING
    BMW_LOOPDATA_ISLAND = 8
    BMW_ISLANDBOUND = 9
    BMW_ISLAND = 10
    BMW_CONNECTED_VERTEX = 11
    # end of array index enum vals

    # do not intitialze function pointers and struct size in BMW_init
    BMW_CUSTOM = 12
    BMW_MAXWALKERS = 13


# Find nearest ------------------------------------------------------
mval_prev = [-1, -1]


def unified_findnearest(context, bm, mval):
    """Mesh編集モードに於いて、次の右クリックで選択される要素を返す。
    Linux限定。
    NOTE: bmeshは外部から持ってこないと関数を抜ける際に開放されて
          返り値のBMVert等がdead扱いになってしまう。
    :type context: bpy.types.Context
    :param mval: mouse region coordinates. [x, y]
    :type mval: list[int] | tuple[int]
    :rtype: (bool,
             (bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace))
    """

    if not test_platform():
        raise OSError('Linux only')

    if context.mode != 'EDIT_MESH':
        return None, (None, None, None)

    # Load functions ------------------------------------------------
    blend_cdll = ctypes.CDLL('')

    view3d_operator_needs_opengl = blend_cdll.view3d_operator_needs_opengl

    em_setup_viewcontext = blend_cdll.em_setup_viewcontext
    ED_view3d_backbuf_validate = blend_cdll.ED_view3d_backbuf_validate
    ED_view3d_select_dist_px = blend_cdll.ED_view3d_select_dist_px
    ED_view3d_select_dist_px.restype = c_float

    EDBM_face_find_nearest_ex = blend_cdll.EDBM_face_find_nearest_ex
    EDBM_face_find_nearest_ex.restype = POINTER(BMFace)
    EDBM_edge_find_nearest_ex = blend_cdll.EDBM_edge_find_nearest_ex
    EDBM_edge_find_nearest_ex.restype = POINTER(BMEdge)
    EDBM_vert_find_nearest_ex = blend_cdll.EDBM_vert_find_nearest_ex
    EDBM_vert_find_nearest_ex.restype = POINTER(BMVert)

    BPy_BMVert_CreatePyObject = blend_cdll.BPy_BMVert_CreatePyObject
    BPy_BMVert_CreatePyObject.restype = py_object
    BPy_BMEdge_CreatePyObject = blend_cdll.BPy_BMEdge_CreatePyObject
    BPy_BMEdge_CreatePyObject.restype = py_object
    BPy_BMFace_CreatePyObject = blend_cdll.BPy_BMFace_CreatePyObject
    BPy_BMFace_CreatePyObject.restype = py_object

    # view3d_select_exec() ------------------------------------------
    # __class__rを使うのは警告対策: PyContext 'as_pointer' not found
    addr = context.__class__.as_pointer(context)
    C = cast(c_void_p(addr), POINTER(bContext))
    view3d_operator_needs_opengl(C)

    # EDBM_select_pick() --------------------------------------------

    vc_obj = ViewContext()
    vc = POINTER(ViewContext)(vc_obj)  # same as pointer(vc_obj)

    # setup view context for argument to callbacks
    em_setup_viewcontext(C, vc)
    vc_obj.mval[0] = mval[0]
    vc_obj.mval[1] = mval[1]

    # unified_findnearest() -----------------------------------------

    # only cycle while the mouse remains still
    use_cycle = c_bool(mval_prev[0] == vc_obj.mval[0] and
                       mval_prev[1] == vc_obj.mval[1])
    dist_init = ED_view3d_select_dist_px()  # float
    # since edges select lines, we give dots advantage of ~20 pix
    dist_margin = c_float(dist_init / 2)
    dist = c_float(dist_init)
    efa_zbuf = POINTER(BMFace)()
    eed_zbuf = POINTER(BMEdge)()

    eve = POINTER(BMVert)()
    eed = POINTER(BMEdge)()
    efa = POINTER(BMFace)()

    # no afterqueue (yet), so we check it now,
    # otherwise the em_xxxofs indices are bad
    ED_view3d_backbuf_validate(vc)

    if dist.value > 0.0 and bm.select_mode & {'FACE'}:
        dist_center = c_float(0.0)
        if bm.select_mode & {'EDGE', 'VERT'}:
            dist_center_p = POINTER(c_float)(dist_center)
        else:
            dist_center_p = POINTER(c_float)()  # 引数無しでNULLポインタになる
        efa = EDBM_face_find_nearest_ex(vc, byref(dist), dist_center_p,
                                        c_bool(1), use_cycle, byref(efa_zbuf))
        if efa and dist_center_p:
            dist.value = min(dist_margin.value, dist_center.value)

    if dist.value > 0.0 and bm.select_mode & {'EDGE'}:
        dist_center = c_float(0.0)
        if bm.select_mode & {'VERT'}:
            dist_center_p = POINTER(c_float)(dist_center)
        else:
            dist_center_p = POINTER(c_float)()
        eed = EDBM_edge_find_nearest_ex(vc, byref(dist), dist_center_p,
                                        c_bool(1), use_cycle, byref(eed_zbuf))
        if eed and dist_center_p:
            dist.value = min(dist_margin.value, dist_center.value)

    if dist.value > 0.0 and bm.select_mode & {'VERT'}:
        eve = EDBM_vert_find_nearest_ex(vc, byref(dist), c_bool(1), use_cycle)

    if eve:
        efa = POINTER(BMFace)()
        eed = POINTER(BMEdge)()
    elif eed:
        efa = POINTER(BMFace)()

    if not (eve or eed or efa):
        if eed_zbuf:
            eed = eed_zbuf
        elif efa_zbuf:
            efa = efa_zbuf

    mval_prev[0] = vc_obj.mval[0]
    mval_prev[1] = vc_obj.mval[1]

    bm_p = c_void_p(vc_obj.em.contents.bm)
    v = BPy_BMVert_CreatePyObject(bm_p, eve) if eve else None
    e = BPy_BMEdge_CreatePyObject(bm_p, eed) if eed else None
    f = BPy_BMFace_CreatePyObject(bm_p, efa) if efa else None

    r = bool(eve or eed or efa), (v, e, f)

    return r


# Find loop / ring --------------------------------------------------
"""bmesh/intern/bmesh_walkers.h: 75"""
BMW_MASK_NOP = 0
"""bmesh/intern/bmesh_walkers.h: 137"""
BMW_NIL_LAY = 0


class BMWFlag(enum.IntEnum):
    """bmesh/intern/bmesh_walkers.h: 39"""
    BMW_FLAG_NOP = 0
    BMW_FLAG_TEST_HIDDEN = 1 << 0


class BMHeaderFlag(enum.IntEnum):  # 名前は適当
    """bmesh/bmesh_class.h: 291
    BMHeader->hflag (char)
    """
    BM_ELEM_SELECT = 1 << 0


def walker_select_count(em, walkercode, start, select, select_mix):
    tot = [0, 0]

    blend_cdll = ctypes.CDLL('')
    BMW_init = blend_cdll.BMW_init
    BMW_begin = blend_cdll.BMW_begin
    BMW_begin.restype = POINTER(BMElem)
    BMW_step = blend_cdll.BMW_step
    BMW_step.restype = POINTER(BMElem)
    BMW_end = blend_cdll.BMW_end

    def BM_elem_flag_test_bool(ele, flag):
        return ele.contents.head.hflag & flag != 0

    bm = c_void_p(em.contents.bm)
    walker = BMWalker()
    BMW_init(byref(walker), bm, walkercode,
             BMW_MASK_NOP, BMW_MASK_NOP, BMW_MASK_NOP,
             BMWFlag.BMW_FLAG_TEST_HIDDEN,
             BMW_NIL_LAY)
    ele = BMW_begin(byref(walker), start)
    while ele:
        i = BM_elem_flag_test_bool(ele, BMHeaderFlag.BM_ELEM_SELECT) != select
        tot[i] += 1
        ele = BMW_step(byref(walker))
    BMW_end(byref(walker))

    return tot


def walker_select(em, walkercode, start, select):
    """mesh/editmesh_select.c: 1402
    選択ではなく要素を返すように変更
    """
    r_elems = []

    blend_cdll = ctypes.CDLL('')
    BMW_init = blend_cdll.BMW_init
    BMW_begin = blend_cdll.BMW_begin
    BMW_begin.restype = POINTER(BMElem)
    BMW_step = blend_cdll.BMW_step
    BMW_step.restype = POINTER(BMElem)
    BMW_end = blend_cdll.BMW_end

    bm = c_void_p(em.contents.bm)
    walker = BMWalker()
    BMW_init(byref(walker), bm, walkercode,
             BMW_MASK_NOP, BMW_MASK_NOP, BMW_MASK_NOP,
             BMWFlag.BMW_FLAG_TEST_HIDDEN,
             BMW_NIL_LAY)
    ele = BMW_begin(byref(walker), start)
    while ele:
        r_elems.append(ele)
        ele = BMW_step(byref(walker))
    BMW_end(byref(walker))

    return r_elems


def mouse_mesh_loop_face(em, eed, select, select_clear):
    return walker_select(em, BMWSelect.BMW_FACELOOP, eed, select)


def mouse_mesh_loop_edge_ring(em, eed, select, select_clear):
    return walker_select(em, BMWSelect.BMW_EDGERING, eed, select)


def mouse_mesh_loop_edge(em, eed, select, select_clear, select_cycle):
    def BM_edge_is_boundary(e):
        l = e.contents.l
        return (l and addressof(l.contents.radial_next.contents) ==
                addressof(l.contents))

    edge_boundary = False

    if select_cycle and BM_edge_is_boundary(eed):
        tot = walker_select_count(em, BMWSelect.BMW_EDGELOOP, eed,
                                  select, False)
        if tot[int(select)] == 0:
            edge_boundary = True
            tot = walker_select_count(em, BMWSelect.BMW_EDGEBOUNDARY, eed,
                                      select, False)
            if tot[int(select)] == 0:
                edge_boundary = False

    if edge_boundary:
        return walker_select(em, BMWSelect.BMW_EDGEBOUNDARY, eed, select)
    else:
        return walker_select(em, BMWSelect.BMW_EDGELOOP, eed, select)


def mouse_mesh_loop(context, bm, mval, extend, deselect, toggle, ring):
    """Mesh編集モードに於いて、次の右クリックで選択される要素を返す。
    Linux限定。
    NOTE: bmeshは外部から持ってこないと関数を抜ける際に開放されて
          返り値のBMVert等がdead扱いになってしまう。
    :type context: bpy.types.Context
    :param mval: mouse region coordinates. [x, y]
    :type mval: list[int] | tuple[int]
    :rtype: (bool,
             (bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace))
    """

    if not test_platform():
        raise OSError('Linux only')

    if context.mode != 'EDIT_MESH':
        return None, []

    # Load functions ------------------------------------------------
    blend_cdll = ctypes.CDLL('')

    view3d_operator_needs_opengl = blend_cdll.view3d_operator_needs_opengl

    em_setup_viewcontext = blend_cdll.em_setup_viewcontext
    ED_view3d_backbuf_validate = blend_cdll.ED_view3d_backbuf_validate
    ED_view3d_select_dist_px = blend_cdll.ED_view3d_select_dist_px
    ED_view3d_select_dist_px.restype = c_float

    EDBM_edge_find_nearest_ex = blend_cdll.EDBM_edge_find_nearest_ex
    EDBM_edge_find_nearest_ex.restype = POINTER(BMEdge)

    BPy_BMEdge_CreatePyObject = blend_cdll.BPy_BMEdge_CreatePyObject
    BPy_BMEdge_CreatePyObject.restype = py_object
    BPy_BMElem_CreatePyObject = blend_cdll.BPy_BMElem_CreatePyObject
    BPy_BMElem_CreatePyObject.restype = py_object

    # edbm_select_loop_invoke() -------------------------------------
    # __class__を使うのは警告対策: PyContext 'as_pointer' not found
    addr = context.__class__.as_pointer(context)
    C = cast(c_void_p(addr), POINTER(bContext))
    view3d_operator_needs_opengl(C)

    # mouse_mesh_loop() ---------------------------------------------
    vc_obj = ViewContext()
    vc = POINTER(ViewContext)(vc_obj)  # same as pointer(vc_obj)
    dist = c_float(ED_view3d_select_dist_px() * 0.6666)
    em_setup_viewcontext(C, vc)
    vc_obj.mval[0] = mval[0]
    vc_obj.mval[1] = mval[1]

    ED_view3d_backbuf_validate(vc)

    eed = EDBM_edge_find_nearest_ex(vc, byref(dist), None, True, True, None)
    if not eed:
        return None, []

    bm_p = c_void_p(vc_obj.em.contents.bm)
    active_edge = BPy_BMEdge_CreatePyObject(bm_p, eed)

    select = True
    select_clear = False
    select_cycle = True
    if not extend and not deselect and not toggle:
        select_clear = True
    if extend:
        select = True
    elif deselect:
        select = False
    elif select_clear or not active_edge.select:
        select = True
    elif toggle:
        select = False
        select_cycle = False

    em = vc_obj.em
    if bm.select_mode & {'FACE'}:
        c_elems = mouse_mesh_loop_face(em, eed, select, select_clear)
    else:
        if ring:
            c_elems = mouse_mesh_loop_edge_ring(em, eed, select, select_clear)
        else:
            c_elems = mouse_mesh_loop_edge(em, eed, select, select_clear,
                                           select_cycle)

    elems = [BPy_BMElem_CreatePyObject(bm_p, elem) for elem in c_elems]

    return active_edge, elems


def find_nearest_ctypes(context, context_dict, bm, mco_region):
    context_dict_bak = context_py_dict_set(context, context_dict)
    find, (eve, eed, efa) = unified_findnearest(context, bm, mco_region)
    context_py_dict_set(context, context_dict_bak)
    if find:
        elem = eve or eed or efa
    else:
        elem = None
    return elem


def find_loop_selection_ctypes(context, context_dict, bm, mco_region, ring,
                               toggle):
    """
    :type context: bpy.types.Context
    :type context_dict: dict
    :type bm: bpy.types.BMesh
    :param mco_region: マウスRegion座標
    :type mco_region: collections.Sequence
    :type ring: bool
    :type toggle: bool
    :return: active edge と 選択要素のタプル
    :rtype: T, list
    """
    context_dict_bak = context_py_dict_set(context, context_dict)
    edge, elems = mouse_mesh_loop(context, bm, mco_region, False, False,
                                  toggle, ring)
    context_py_dict_set(context, context_dict_bak)
    return edge, elems
    # edge_coords = []
    # face_coords = []
    # if edge and elems:
    #     if isinstance(elems[0], bmesh.types.BMEdge):
    #         edge_coords = [[v.co.copy() for v in e.verts] for e in elems]
    #     elif isinstance(elems[0], bmesh.types.BMFace):
    #         face_coords = [[v.co.copy() for v in f.verts] for f in elems]
    # return edge, edge_coords, face_coords


###############################################################################
# Find - python
###############################################################################
def get_selected(bm):
    selected_verts = {elem for elem in bm.verts if elem.select}
    selected_edges = {elem for elem in bm.edges if elem.select}
    selected_faces = {elem for elem in bm.faces if elem.select}
    return selected_verts, selected_edges, selected_faces


def find_nearest(context, context_dict, bm, mco_region):
    select_history = list(bm.select_history)
    active_face = bm.faces.active
    active_material_index = context.active_object.active_material_index

    selected_verts, selected_edges, selected_faces = get_selected(bm)

    def test_select(elem):
        if isinstance(elem, bmesh.types.BMVert):
            return elem in selected_verts
        elif isinstance(elem, bmesh.types.BMEdge):
            return elem in selected_edges
        else:
            return elem in selected_faces

    def set_select(elem):
        elem.select = test_select(elem)

    bm.select_history.clear()
    bpy.ops.view3d.select(context_dict, False, extend=True,
                          location=mco_region)

    active = bm.select_history.active

    if active:
        if isinstance(active, bmesh.types.BMFace):
            # faces
            set_select(active)
            for eve in active.verts:
                for efa in eve.link_faces:
                    set_select(efa)
            # edges
            for eed in active.edges:
                set_select(eed)
            for eve in active.verts:
                for efa in eve.link_faces:
                    for eed in efa.edges:
                        set_select(eed)
                for eed in eve.link_edges:
                    set_select(eed)
            # verts
            for eve in active.verts:
                set_select(eve)
            for eve in active.verts:
                for efa in eve.link_faces:
                    for v in efa.verts:
                        set_select(v)
                for eed in eve.link_edges:
                    for v in eed.verts:
                        set_select(v)

        elif isinstance(active, bmesh.types.BMEdge):
            # faces
            for eve in active.verts:
                for efa in eve.link_faces:
                    set_select(efa)
            # edges
            for eve in active.verts:
                for efa in eve.link_faces:
                    for eed in efa.edges:
                        set_select(eed)
                for eed in eve.link_edges:
                    set_select(eed)
            set_select(active)
            # verts
            for eve in active.verts:
                for efa in eve.link_faces:
                    for v in efa.verts:
                        set_select(v)
                for eed in eve.link_edges:
                    for v in eed.verts:
                        set_select(v)
                set_select(eve)

        else:
            # faces
            for efa in active.link_faces:
                set_select(efa)
            #edges
            for efa in active.link_faces:
                for eed in efa.edges:
                    set_select(eed)
            for eed in active.link_edges:
                set_select(eed)
            # verts
            for efa in active.link_faces:
                for eve in efa.verts:
                    set_select(eve)
            for eed in active.link_edges:
                for eve in eed.verts:
                    set_select(eve)
            set_select(active)

    # restore
    bm.select_history.clear()
    for elem in select_history:
        bm.select_history.add(elem)
    bm.faces.active = active_face
    context.active_object.active_material_index = active_material_index

    return active


def find_loop_selection(context, context_dict, bm, mco_region, ring, toggle):
    """
    :type context: bpy.types.Context
    :type context_dict: dict
    :type bm: bpy.types.BMesh
    :param mco_region: マウスRegion座標。未使用。
    :type mco_region: collections.Sequence
    :type ring: bool
    :type toggle: bool
    :return: active edge と 選択要素のタプル
    :rtype: T, list
    """
    ts = context.tool_settings
    mode = ts.mesh_select_mode[:]
    if mode[2]:
        ring = True

    select_history = list(bm.select_history)
    active_face = bm.faces.active
    active_material_index = context.active_object.active_material_index

    verts_pre, edges_pre, faces_pre = get_selected(bm)

    if ring:
        if mode[2]:
            ts.mesh_select_mode = [False, True, True]
        else:
            ts.mesh_select_mode = [False, True, False]
        r = bpy.ops.mesh.edgering_select(
                context_dict, 'INVOKE_DEFAULT', False,
                extend=False, deselect=False, toggle=False, ring=True)
    else:
        if toggle:
            bpy.ops.mesh.select_all(context_dict, False, action='DESELECT')
        ts.mesh_select_mode = [False, True, False]
        r = bpy.ops.mesh.loop_select(
                context_dict, 'INVOKE_DEFAULT', False,
                extend=False, deselect=False, toggle=False, ring=False)
    if r == {'CANCELLED'}:
        active_edge = None
        elems = []
    else:
        # bm.select_history.active: vert選択が有効ならBMVert型になり、
        # edgeが有効ならBMEdge、faceが有効ならBMFaceとなる。
        # 優先度はvert,edge,faceの順。
        active_edge = bm.select_history.active
        verts, edges, faces = get_selected(bm)
        if mode[2]:
            elems = faces
        else:
            elems = edges

    context.tool_settings.mesh_select_mode = mode
    if r != {'CANCELLED'} or not ring and toggle:
        bpy.ops.mesh.select_all(context_dict, False, action='DESELECT')
        if mode == [False, False, True]:
            for f in faces_pre:
                f.select = True
        elif not mode[0]:
            for f in faces_pre:
                f.select = True
            for e in edges_pre:
                e.select = True
        else:
            for f in faces_pre:
                f.select = True
            for e in edges_pre:
                e.select = True
            for v in verts_pre:
                v.select = True

        # restore
        bm.select_history.clear()
        for elem in select_history:
            bm.select_history.add(elem)
        bm.faces.active = active_face
        context.active_object.active_material_index = active_material_index

    return active_edge, elems


###############################################################################
# Derived Mesh
###############################################################################
class CustomDataType(enum.IntEnum):
    """DNA_customdata_types.h: 77"""
    CD_ORIGINDEX = 7


"""BKE_customdata.h: 63"""
ORIGINDEX_NONE = -1


class DerivedMeshType(enum.IntEnum):
    """BKE_DerivedMesh.h:122
    DerivedMesh->type (int)
    """
    # cdderivedmesh.c: generate系
    DM_TYPE_CDDM = 0
    # editderivedmesh.c: editmodeで、有効なmodifier無し/deform系
    DM_TYPE_EDITBMESH = 1
    # subsurf_ccg.c: subsurf
    DM_TYPE_CCGDM = 2


class DMForeachFlag(enum.IntEnum):
    """BKE_DerivedMesh.h:158"""
    DM_FOREACH_NOP = 0
    # foreachMappedVert, foreachMappedLoop, foreachMappedFaceCenter
    DM_FOREACH_USE_NORMAL = (1 << 0)


dm_cache = {}


def get_dm(mesh):
    mesh_addr = mesh.as_pointer()
    mesh_p = cast(c_void_p(mesh_addr), POINTER(Mesh))
    mesh_ = mesh_p.contents
    em_p = mesh_.edit_btmesh
    if em_p:
        em = em_p.contents
        dm_p = em.derivedCage
        if dm_p:
            return dm_p.contents
    return None


def get_dm_attr(mesh, dm, attr):
    mesh_addr = mesh.as_pointer()
    if mesh_addr not in dm_cache:
        dm_cache[mesh_addr] = {}
    cache = dm_cache[mesh_addr]
    dm_p = pointer(dm)

    if attr in cache:
        return cache[attr]

    if attr == 'type':
        value = dm.type

    elif attr == 'num_verts':
        value = dm.getNumVerts(dm_p)
    elif attr == 'num_edges':
        value = dm.getNumEdges(dm_p)
    elif attr == 'num_faces':
        value = dm.getNumPolys(dm_p)
    elif attr == 'num_loops':
        value = dm.getNumLoops(dm_p)

    elif attr == 'vert_coords':
        value = (c_float * 3 * get_dm_attr(mesh, dm, 'num_verts'))()
        dm.getVertCos(dm_p, value)

    elif attr == 'vert_array':
        value = (MVert * get_dm_attr(mesh, dm, 'num_verts'))()
        dm.copyVertArray(dm_p, value)
    elif attr == 'edge_array':
        value = (MEdge * get_dm_attr(mesh, dm, 'num_edges'))()
        dm.copyEdgeArray(dm_p, value)
    elif attr == 'face_array':
        value = (MPoly * get_dm_attr(mesh, dm, 'num_faces'))()
        dm.copyPolyArray(dm_p, value)
    elif attr == 'loop_array':
        value = (MLoop * get_dm_attr(mesh, dm, 'num_loops'))()
        dm.copyLoopArray(dm_p, value)

    elif attr == 'vert_origindex_array':
        num_verts = get_dm_attr(mesh, dm, 'num_verts')
        if dm.type == DerivedMeshType.DM_TYPE_EDITBMESH:
            value = (c_int * num_verts)(*range(num_verts))
        else:
            arr = dm.getVertDataArray(dm_p, CustomDataType.CD_ORIGINDEX)
            if arr:
                value = (c_int * num_verts)()
                ctypes.memmove(value, arr, sizeof(value))
            else:
                value = None
    elif attr == 'edge_origindex_array':
        num_edges = get_dm_attr(mesh, dm, 'num_edges')
        if dm.type == DerivedMeshType.DM_TYPE_EDITBMESH:
            value = (c_int * num_edges)(*range(num_edges))
        else:
            arr = dm.getEdgeDataArray(dm_p, CustomDataType.CD_ORIGINDEX)
            if arr:
                value = (c_int * num_edges)()
                ctypes.memmove(value, arr, sizeof(value))
            else:
                value = None
    elif attr == 'face_origindex_array':
        num_faces = get_dm_attr(mesh, dm, 'num_faces')
        if dm.type == DerivedMeshType.DM_TYPE_EDITBMESH:
            value = (c_int * num_faces)(*range(num_faces))
        else:
            arr = dm.getPolyDataArray(dm_p, CustomDataType.CD_ORIGINDEX)
            if arr:
                value = (c_int * num_faces)()
                ctypes.memmove(value, arr, sizeof(value))
            else:
                value = None

    elif attr in {'face_center_origindex_np_array', 'face_center_np_array'}:
        # 1007616個の要素: 4.0s
        queue = collections.deque()
        P = POINTER(c_float)
        def callback(userData, index, cent, no):
            # この方法だと12.0s
            # queue = cast(c_void_p(userData), py_object).value
            # v = list(cast(c_void_p(cent), POINTER(c_float * 3)).contents)
            # queue.append((index, v))
            x = cast(cent, P)
            queue.append((index, (x[0], x[1], x[2])))
            return 0
        func = CFUNCTYPE(c_int, c_void_p, c_int, c_void_p, c_void_p)(callback)
        dm.foreachMappedFaceCenter(dm_p, func, id(queue),
                                   DMForeachFlag.DM_FOREACH_NOP)

        face_center_origindex_np_array = np.array(
                [i for i, v in queue], dtype=np.int)
        sort_order = np.argsort(face_center_origindex_np_array)
        face_center_origindex_np_array = \
            face_center_origindex_np_array[sort_order]
        cache['face_center_origindex_np_array'] = \
            face_center_origindex_np_array

        face_center_np_array = np.array([v for i, v in queue], dtype=np.float)
        face_center_np_array = face_center_np_array[sort_order]
        cache['face_center_np_array'] = face_center_np_array

        if attr == 'face_center_origindex_np_array':
            value = face_center_origindex_np_array
        else:
            value = face_center_np_array
    else:
        raise KeyError(attr)

    cache[attr] = value
    return value


def get_bmdm_elems(mesh, bm, elems, require_face_centers, use_derived=True):
    dm_vert_elems = {}
    dm_edge_elems = {}
    dm_face_elems = {}
    dm_face_center_elems = {}

    verts = set()
    edges = set()
    faces = set()
    for elem in elems:
        if isinstance(elem, bmesh.types.BMVert):
            verts.add(elem)
        elif isinstance(elem, bmesh.types.BMEdge):
            edges.add(elem)
            for v in elem.verts:
                verts.add(v)
        else:
            faces.add(elem)
            for v in elem.verts:
                verts.add(v)
            for e in elem.edges:
                edges.add(e)

    if use_derived:
        dm = get_dm(mesh)
    else:
        dm = None
    if dm:
        co = (c_float * 3)()
        for elem in verts:
            i = elem.index
            dm.getVertCo(dm, i, co)
            dm_vert_elems[i] = (Vector(co), i)
    else:
        for elem in verts:
            i = elem.index
            dm_vert_elems[i] = (elem.co.copy(), i)
    for elem in edges:
        i = elem.index
        dm_edge_elems[i] = ([v.index for v in elem.verts], i)
    for elem in faces:
        i = elem.index
        dm_face_elems[i] = ([v.index for v in elem.verts], i)
        if dm:
            coords = [dm_vert_elems[v.index][0] for v in elem.verts]
            center = sum(coords, Vector()) / len(coords)
        else:
            center = elem.calc_center_median()
        dm_face_center_elems[i] = (center, i)

    return dm_vert_elems, dm_edge_elems, dm_face_elems, dm_face_center_elems


def get_dm_elems(mesh, bm, elems, require_face_centers):
    dm = get_dm(mesh)
    if (not dm or get_dm_attr(mesh, dm, 'type') ==
            DerivedMeshType.DM_TYPE_EDITBMESH):
        return get_bmdm_elems(mesh, bm, elems, require_face_centers)

    elem_types = set((type(elem) for elem in elems))
    vert_coords = get_dm_attr(mesh, dm, 'vert_coords')
    vert_origindex_array = get_dm_attr(mesh, dm, 'vert_origindex_array')
    if bmesh.types.BMVert in elem_types:
        # vert_array = get_dm_attr(mesh, dm, 'vert_array')
        pass
    if bmesh.types.BMEdge in elem_types:
        edge_array = get_dm_attr(mesh, dm, 'edge_array')
        edge_origindex_array = get_dm_attr(mesh, dm, 'edge_origindex_array')
    if bmesh.types.BMFace in elem_types:
        edge_array = get_dm_attr(mesh, dm, 'edge_array')
        face_array = get_dm_attr(mesh, dm, 'face_array')
        loop_array = get_dm_attr(mesh, dm, 'loop_array')
        edge_origindex_array = get_dm_attr(mesh, dm, 'edge_origindex_array')
        face_origindex_array = get_dm_attr(mesh, dm, 'face_origindex_array')
        if require_face_centers:
            face_center_np_array = get_dm_attr(
                    mesh, dm, 'face_center_np_array')
            face_center_origindex_np_array = get_dm_attr(
                    mesh, dm, 'face_center_origindex_np_array')

    # 要素の二番目は派生元のelemのindex。無けれはNone
    dm_vert_elems = {}
    dm_edge_elems = {}
    dm_face_elems = {}
    dm_face_center_elems = {}

    for elem in elems:
        elem_index = elem.index

        if isinstance(elem, bmesh.types.BMVert):
            orig_index_array = vert_origindex_array
        elif isinstance(elem, bmesh.types.BMEdge):
            orig_index_array = edge_origindex_array
        else:
            orig_index_array = face_origindex_array

        derived_indices = {}
        arr = np.ctypeslib.as_array(orig_index_array)
        for i in np.nonzero(arr == elem_index)[0]:
            derived_indices[i] = elem_index

        if isinstance(elem, bmesh.types.BMVert):
            for i, orig_index in derived_indices.items():
                dm_vert_elems[i] = (Vector(vert_coords[i]), orig_index)

        elif isinstance(elem, bmesh.types.BMEdge):
            verts = set()
            for i, orig_index in derived_indices.items():
                me = edge_array[i]
                dm_edge_elems[i] = ((me.v1, me.v2), orig_index)
                verts.add(me.v1)
                verts.add(me.v2)
            for i in verts:
                orig_index = vert_origindex_array[i]
                dm_vert_elems[i] = (Vector(vert_coords[i]), orig_index)

        else:
            verts = []
            edges = []
            for i, orig_index in derived_indices.items():
                mp = face_array[i]
                ls = []
                for j in range(mp.loopstart, mp.loopstart + mp.totloop):
                    ml = loop_array[j]
                    ls.append(ml.v)
                    verts.append(ml.v)
                    edges.append(ml.e)
                dm_face_elems[i] = (ls, orig_index)

            for i in set(verts):
                orig_index = vert_origindex_array[i]
                dm_vert_elems[i] = (Vector(vert_coords[i]), orig_index)

            for i in set(edges):
                orig_index = edge_origindex_array[i]
                e = edge_array[i]
                dm_edge_elems[i] = ((e.v1, e.v2), orig_index)

            if require_face_centers:
                arr = face_center_origindex_np_array == elem.index
                for i in np.nonzero(arr)[0]:
                    vec = Vector(face_center_np_array[i])
                    dm_face_center_elems[i] = (vec, elem.index)

    return dm_vert_elems, dm_edge_elems, dm_face_elems, dm_face_center_elems


###############################################################################
# Draw Funcs
###############################################################################
def redraw_areas(context, force=False):
    actob = context.active_object
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces.active
            prop = space_prop.get(v3d)
            if force:
                area.tag_redraw()
            elif prop.enable and v3d.viewport_shade != 'RENDERED':
                if any([a & b for a, b in zip(actob.layers, v3d.layers)]):
                    area.tag_redraw()


def bglPolygonOffset(viewdist, dist):
    """screen/glutil.c: 954
    :type viewdist: float
    :type dist: float
    """
    bgl.glMatrixMode(bgl.GL_PROJECTION)
    if dist != 0.0:
        bgl.glGetFloatv(bgl.GL_PROJECTION_MATRIX, bglPolygonOffset.winmat)
        if bglPolygonOffset.winmat[15] > 0.5:
            offs = 0.00001 * dist * viewdist
        else:
            offs = 0.0005 * dist
        bglPolygonOffset.winmat[14] -= offs
        bglPolygonOffset.offset += offs
    else:
        bglPolygonOffset.winmat[14] += bglPolygonOffset.offset
        bglPolygonOffset.offset = 0.0
    bgl.glLoadMatrixf(bglPolygonOffset.winmat)
    bgl.glMatrixMode(bgl.GL_MODELVIEW)

bglPolygonOffset.winmat = bgl.Buffer(bgl.GL_FLOAT, 16)
bglPolygonOffset.offset = 0.0


def ED_view3d_polygon_offset(rv3d, dist):
    """space_view3d/view3d_view.c: 803
    :type rv3d: bpy.types.RegionView3D
    :type dist: float
    """
    # if rv3d->rflag & RV3D_ZOFFSET_DISABLED:
    #     return
    viewdist = rv3d.view_distance
    if dist != 0.0:
        if rv3d.view_perspective == 'CAMERA':
            if not rv3d.is_perspective:
                winmat = rv3d.window_matrix
                viewdist = 1.0 / max(abs(winmat[0][0]), abs(winmat[1][1]))
    bglPolygonOffset(viewdist, dist)


def polygon_offset_pers_mat(rv3d, dist):
    viewdist = rv3d.view_distance
    if dist != 0.0:
        if rv3d.view_perspective == 'CAMERA':
            if not rv3d.is_perspective:
                winmat = rv3d.window_matrix
                viewdist = 1.0 / max(abs(winmat[0][0]), abs(winmat[1][1]))

    winmat = rv3d.window_matrix.copy()
    if dist != 0.0:
        if winmat.col[3][3] > 0.5:
            offs = 0.00001 * dist * viewdist
        else:
            offs = 0.0005 * dist
        winmat.col[3][2] -= offs

    return winmat * rv3d.view_matrix


def setlinestyle(nr):
    """screen/glutil.c:270
    :type nr: int
    """
    if nr == 0:
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
    else:
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
        if False:  # if U.pixelsize > 1.0f
            bgl.glLineStipple(nr, 0xCCCC)
        else:
            bgl.glLineStipple(nr, 0xAAAA)


def face_stipple_pattern(size):
    stipple_quattone_base = np.array(
            [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]])

    def conv(arr):
        arr = [int(''.join([str(k) for k in arr[i][j*8:j*8+8]]), 2)
           for i in range(32) for j in range(4)]
        return bgl.Buffer(bgl.GL_BYTE, 128, arr)

    if size >= 8:
        buf = face_stipple_pattern.x8
        if not buf:
            buf = face_stipple_pattern.x8 = \
                conv(np.repeat(np.repeat(stipple_quattone_base, 8, axis=0), 8,
                               axis=1))
    elif size >= 4:
        buf = face_stipple_pattern.x4
        if not buf:
            buf = face_stipple_pattern.x4 = \
                conv(np.tile(np.repeat(np.repeat(
                        stipple_quattone_base, 4, axis=0), 4, axis=1), (2, 2)))
    elif size >= 2:
        buf = face_stipple_pattern.x2
        if not buf:
            buf = face_stipple_pattern.x2 = \
                conv(np.tile(np.repeat(np.repeat(
                        stipple_quattone_base, 2, axis=0), 2, axis=1), (4, 4)))
    else:
        # glutil.cのものと重ならないようにずらしたもの
        buf = face_stipple_pattern.x1
        if not buf:
            buf = face_stipple_pattern.x1 = \
                conv(np.tile(np.roll(stipple_quattone_base, 2, 1), (8, 8)))
    return buf

face_stipple_pattern.x1 = None
face_stipple_pattern.x2 = None
face_stipple_pattern.x4 = None
face_stipple_pattern.x8 = None


def setpolygontone(enable, size=1):
    """
    :type enable: bool
    :type size: int
    """
    if enable:
        bgl.glEnable(bgl.GL_POLYGON_STIPPLE)
        bgl.glPolygonStipple(face_stipple_pattern(size))
    else:
        bgl.glDisable(bgl.GL_POLYGON_STIPPLE)


def get_depth(x, y, fatten=0, buf=None):
    """スクリーン座標x,yのZ値を読む。fatten==0で1pixel,1で3x3の9pixelを返す"""
    size = fatten * 2 + 1
    if buf:
        # bufはBuffer(GL_FLOAT, (height, width))で作成してあるものとする
        ls = []
        h, w = buf.dimensions
        xmin = max(0, x - fatten)
        xmax = min(x + fatten, w - 1)
        ymin = max(0, y - fatten)
        ymax = min(y + fatten, h - 1)
        for row in range(ymin, ymax + 1):
            for col in range(xmin, xmax + 1):
                ls.append(buf[row][col])
        return ls
    else:
        buf = bgl.Buffer(bgl.GL_FLOAT, size ** 2)
        bgl.glReadPixels(x - fatten, y - fatten, size, size,
                         bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, buf)
        return list(buf)


def project(region, rv3d, vec):
    v = rv3d.perspective_matrix * vec.to_4d()
    if abs(v[3]) > 1e-5:
        v /= v[3]
    x = (1 + v[0]) * region.width * 0.5
    y = (1 + v[1]) * region.height * 0.5
    z = (1 + v[2]) * 0.5
    return Vector((x, y, z))


def project_v3(sx, sy, persmat, vec) -> "3D Vector":
    v = persmat * vec.to_4d()
    if abs(v[3]) > 1e-5:
        v /= v[3]
    x = (1 + v[0]) * sx * 0.5
    y = (1 + v[1]) * sy * 0.5
    z = (1 + v[2]) * 0.5
    return Vector((x, y, z))


def draw_circle(x, y, z, radius, subdivide, poly=False):
    r = 0.0
    dr = math.pi * 2 / subdivide
    if poly:
        subdivide += 1
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        bgl.glVertex3f(x, y, z)
    else:
        bgl.glBegin(bgl.GL_LINE_LOOP)
    for _ in range(subdivide):
        bgl.glVertex3f(x + radius * math.cos(r), y + radius * math.sin(r), z)
        r += dr
    bgl.glEnd()


def draw_box(xmin, ymin, w, h, z, poly=False):
    bgl.glBegin(bgl.GL_QUADS if poly else bgl.GL_LINE_LOOP)
    bgl.glVertex3f(xmin, ymin, z)
    bgl.glVertex3f(xmin + w, ymin, z)
    bgl.glVertex3f(xmin + w, ymin + h, z)
    bgl.glVertex3f(xmin, ymin + h, z)
    bgl.glEnd()


def make_paths(edges):
    """
    :param edges: [[v1, v2], ...]
    :type edges: list | tuple
    :return: [[v1, v2, v3, v1], [v4, v5]]
    :rtype: list
    """
    paths = []

    vert_verts = {}
    for v1, v2 in edges:
        if v1 not in vert_verts:
            vert_verts[v1] = [v2]
        else:
            vert_verts[v1].append(v2)
        if v2 not in vert_verts:
            vert_verts[v2] = [v1]
        else:
            vert_verts[v2].append(v1)

    end_flags = {v: len(others) != 2 for v, others in vert_verts.items()}
    for vert in vert_verts.keys():
        verts = vert_verts[vert]
        while verts:
            vprev = vert
            vnext = verts.pop()
            vert_verts[vnext].remove(vprev)
            path = [vprev, vnext]
            while True:
                if end_flags[vnext]:
                    if end_flags[path[0]]:  # 開始点、終了点が共に端
                        break
                    else:
                        path.reverse()  # 逆に回る
                        vprev = vert
                elif vnext == vert:  # 周状
                    break
                else:
                    vprev = vnext
                vnext = vert_verts[vprev].pop()
                vert_verts[vnext].remove(vprev)
                path.append(vnext)
            paths.append(path)

    return paths


def draw_callback(cls, context):
    cls.remove_invalid_windows()

    if not cls.data:
        cls.remove_handler()
        return

    win = context.window
    data = cls.active(win)
    if not data:
        return

    prefs = DrawNearestPreferences.get_instance()
    event = data['event']
    area = context.area
    region = context.region
    rv3d = context.region_data
    v3d = context.space_data

    key = rv3d.as_pointer()
    if key in data['callback_count']:
        callback_count = data['callback_count'][key]
        data['callback_count'][key] = min(callback_count + 1, 100)  # 適当な上限
        if callback_count > 0:
            return
    else:
        # data['callback_count'][key] = -1
        return

    prop = space_prop.get(v3d)
    if (not prop.enable or context.mode != 'EDIT_MESH' or
            v3d.viewport_shade == 'RENDERED'):
        return

    mco = (event.mouse_x, event.mouse_y)
    target = data['target']  # [type, vert_coords, median]

    do_draw = True
    if not target:
        do_draw = False
    elif data['mco'] != mco:  # 別のOperatorがRUNNING_MODAL
        do_draw = False
    elif not prefs.redraw_all:
        # if not (region.x <= mco[0] <= region.x + region.width and
        #         region.y <= mco[1] <= region.y + region.height):
        if not (area.x <= mco[0] <= area.x + area.width and
                area.y <= mco[1] <= area.y + area.height):
            do_draw = False
    if not do_draw:
        return

    ob = context.active_object
    if not ob:
        return
    mat = ob.matrix_world

    glsettings = GLSettings(context)
    glsettings.push()
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(1)

    if v3d.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'}:
        solid_view3d = True
    else:
        solid_view3d = False
    if (solid_view3d and ob.draw_type not in {'BOUNDBOX', 'WIREFRAME'} and
            v3d.use_occlude_geometry):
        solid_object = True
    else:
        solid_object = False

    if prefs.use_overlay:
        use_depth = False
    elif solid_view3d and solid_object:
        use_depth = True
    else:
        use_depth = False

    mask = prefs.mask
    if mask == 'STENCIL':
        buf = Buffer('int', 0, bgl.GL_STENCIL_BITS)
        if buf == 0:
            mask = 'NONE'

    depth_buffer = bgl.Buffer(bgl.GL_FLOAT, (region.height, region.width))
    bgl.glReadPixels(region.x, region.y, region.width, region.height,
                     bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, depth_buffer)

    key, mode, dm_type, verts, edges, faces, face_centers = target
    vert_coords_local = {i: co for i, (co, orig) in verts.items()}
    vert_coords = {i: mat * co for i, co in vert_coords_local.items()}
    face_center_coords = {}
    for i, (vec, orig) in face_centers.items():
        face_center_coords[i] = mat * vec

    def draw_faces(emphasis):
        if emphasis == 'FILL':
            if use_depth:
                ED_view3d_polygon_offset(rv3d, 1.0)
            else:
                cm = glsettings.region_pixel_space().enter()
            bgl.glBegin(bgl.GL_TRIANGLES)
            for v_indices, orig in faces.values():
                if len(v_indices) == 3:
                    tris = [(0, 1, 2)]
                elif len(v_indices) == 4:
                    if dm_type == DerivedMeshType.DM_TYPE_CCGDM:
                        tris = [(0, 1, 3), (1, 2, 3)]
                    else:
                        tris = [(0, 1, 2), (0, 2, 3)]
                else:
                    tris = mathutils.geometry.tessellate_polygon(
                           [[vert_coords_local[i] for i in v_indices]])
                for tri in tris:
                    for i in tri:
                        j = v_indices[i]
                        if use_depth:
                            bgl.glVertex3f(*vert_coords[j])
                        else:
                            v = project(region, rv3d, vert_coords[j])
                            bgl.glVertex3f(v[0], v[1], OVERLAY_DRAW_Z)
            bgl.glEnd()
            if use_depth:
                ED_view3d_polygon_offset(rv3d, 0.0)
            else:
                cm.exit()
        else:
            with glsettings.region_pixel_space():
                for i, vec in face_center_coords.items():
                    if not use_depth or depth_test_result_madians[i]:
                        r2 = prefs.face_center_size / 2
                        v = project(region, rv3d, vec)
                        draw_box(v[0] - r2, v[1] - r2, r2 * 2, r2 * 2,
                                 OVERLAY_DRAW_Z)
                bgl.glLineWidth(1)

    def draw_edges():
        edge_paths = make_paths([v1v2 for v1v2, orig in edges.values()
                                 if orig != ORIGINDEX_NONE])
        if use_depth:
            if solid_object:
                # 辺が1.0で描画されている為（たぶん）、
                # すこしずらなさいと重なってしまう
                ED_view3d_polygon_offset(rv3d, POLYGON_OFFSET_EDGE)
            else:
                ED_view3d_polygon_offset(rv3d, 1.0)
            for path in edge_paths:
                bgl.glBegin(bgl.GL_LINE_STRIP)
                for i in path:
                    vec = vert_coords[i]
                    bgl.glVertex3f(*vec)
                bgl.glEnd()
            ED_view3d_polygon_offset(rv3d, 0.0)
        else:
            cm = glsettings.region_pixel_space().enter()
            for path in edge_paths:
                bgl.glBegin(bgl.GL_LINE_STRIP)
                for i in path:
                    vec = vert_coords[i]
                    v = project(region, rv3d, vec)
                    bgl.glVertex3f(v[0], v[1], OVERLAY_DRAW_Z)
                bgl.glEnd()
            cm.exit()

    if mode == 'select':
        bgl.glColor4f(*prefs.select_color)
        # target_type, target_index, verts, edges, faces, medians = target

        offs_pmat = polygon_offset_pers_mat(rv3d, 1)

        def depth_test(vec):
            """描画可なら1を返す"""
            v = project_v3(region.width, region.height,
                           offs_pmat, vec)
            depth3x3 = get_depth(int(v[0]), int(v[1]), 1, depth_buffer)
            if not (0.0 < v[2] < 1.0):
                return 0
            for f in depth3x3:
                if f == 0.0:  # オブジェクト中心マークが0.0
                    return -1
                if v[2] <= f:
                    return 1
            return 0

        # マスクを描画するから今の内に求めておく
        # depth_test_result_coords = {i: depth_test(v)
        #                             for i, v in vert_coords.items()}
        depth_test_result_coords = {}
        for i, v in vert_coords.items():
            orig = verts[i][1]
            if orig == ORIGINDEX_NONE:
                depth_test_result_coords[i] = 0
            else:
                depth_test_result_coords[i] = depth_test(v)

        depth_test_result_madians = {}
        for i, vec in face_center_coords.items():
            if prefs.face_emphasis == 'FILL':
                depth_test_result_madians[i] = 0
            else:
                depth_test_result_madians[i] = depth_test(vec)

        mesh_select_mode = context.tool_settings.mesh_select_mode
        if faces:
            draw_vert = 'VERT' in prefs.draw_set_face
            draw_edge = 'EDGE' in prefs.draw_set_face
            draw_face = 'FACE' in prefs.draw_set_face
        elif edges:
            draw_vert = 'VERT' in prefs.draw_set_edge
            draw_edge = 'EDGE' in prefs.draw_set_edge
            draw_face = False
        else:
            draw_vert = 'VERT' in prefs.draw_set_vert
            draw_edge = False
            draw_face = False

        bgl.glEnable(bgl.GL_DEPTH_TEST)
        if mask == 'STENCIL':
            bgl.glEnable(bgl.GL_STENCIL_TEST)
            bgl.glClearStencil(0)
            bgl.glClear(bgl.GL_STENCIL_BUFFER_BIT)
        else:
            bgl.glDisable(bgl.GL_STENCIL_TEST)

        # 頂点位置にマスクを描く
        # NOTE: 元の頂点は深度マスクを切って描かれている
        v_size = context.user_preferences.themes['Default'].view_3d.vertex_size
        if mesh_select_mode[0] and mask != 'NONE':
            with glsettings.push_attrib():
                if use_depth:
                    ED_view3d_polygon_offset(rv3d, 1.0)
                else:
                    cm = glsettings.region_pixel_space().enter()
                if mask == 'STENCIL':
                    bgl.glStencilMask(0xff)
                    bgl.glStencilFunc(bgl.GL_GREATER, 0b1, 0xff)
                    bgl.glStencilOp(bgl.GL_KEEP, bgl.GL_REPLACE,
                                    bgl.GL_REPLACE)
                    bgl.glDepthMask(0)
                else:
                    bgl.glDepthFunc(bgl.GL_ALWAYS)
                    bgl.glDepthMask(1)

                bgl.glColorMask(0, 0, 0, 0)
                bgl.glPointSize(v_size)
                bgl.glBegin(bgl.GL_POINTS)
                for i, vec in vert_coords.items():
                    if verts[i][1] is not None:
                        if not use_depth or depth_test_result_coords[i] == 1:
                            if use_depth:
                                bgl.glVertex3f(*vec)
                            else:
                                v = project(region, rv3d, vec)
                                bgl.glVertex3f(v[0], v[1], OVERLAY_MASK_Z)
                bgl.glEnd()
                if use_depth:
                    ED_view3d_polygon_offset(rv3d, 0.0)
                else:
                    cm.exit()

        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glDepthMask(0)
        bgl.glStencilMask(0)
        bgl.glStencilFunc(bgl.GL_EQUAL, 0, 0xff)
        bgl.glStencilOp(bgl.GL_KEEP, bgl.GL_KEEP, bgl.GL_KEEP)

        # 面描画
        if faces and draw_face:
            # パターンを使って塗りつぶし
            if prefs.face_emphasis == 'FILL':
                dot_size = 2 ** (prefs.face_stipple - 1)
                setpolygontone(True, dot_size)
                draw_faces('FILL')
                setpolygontone(False)
            # Medianの位置に四角を描く
            else:
                bgl.glLineWidth(prefs.face_center_line_width)
                draw_faces('CENTER')
                bgl.glLineWidth(1)

        # 辺描画
        if edges and draw_edge:
            bgl.glLineWidth(prefs.edge_line_width)
            bgl.glEnable(bgl.GL_LINE_SMOOTH)
            setlinestyle(prefs.edge_line_stipple)
            draw_edges()
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
            bgl.glLineWidth(1)
            setlinestyle(0)

        # 頂点描画。頂点の中心が隠れていると描画しない
        if verts and draw_vert:
            bgl.glDisable(bgl.GL_STENCIL_TEST)
            bgl.glLineWidth(prefs.vertex_line_width)
            bgl.glEnable(bgl.GL_LINE_SMOOTH)
            vert_size = prefs.vertex_size / 2
            vnum = 12
            if use_depth:
                pmat = offs_pmat
            else:
                pmat = rv3d.perspective_matrix
            with glsettings.region_pixel_space():
                for i, (_vec, orig) in verts.items():
                    if orig == ORIGINDEX_NONE:
                        continue
                    vec = vert_coords[i]
                    if not use_depth or depth_test_result_coords[i] != 0:
                        v = project_v3(region.width, region.height, pmat, vec)
                        if use_depth and depth_test_result_coords[i] == -1:
                            # オブジェクト中心のマークと重なっている場合
                            z = -(v[2] * 200 - 100)
                        else:
                            z = OVERLAY_DRAW_Z
                        draw_circle(v[0], v[1], z, vert_size, vnum, poly=False)
                        # bgl.glColor3f(1, 1, 1)
                        # draw_circle(v[0], v[1], z,
                        #             vert_size - prefs.vertex_line_width,
                        #             vnum, poly=False)
                        # bgl.glColor3f(0, 0, 0)
                        # draw_circle(v[0], v[1], z, vert_size, vnum,
                        #             poly=False)
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
            bgl.glLineWidth(1)

    else:
        if use_depth:
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glDepthMask(0)
        else:
            bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glColor4f(*prefs.loop_select_color)

        if faces:
            dot_size = 2 ** (prefs.loop_select_face_stipple - 1)
            setpolygontone(True, dot_size)
            draw_faces('FILL')
            setpolygontone(False)

        elif edges:
            bgl.glLineWidth(prefs.loop_select_line_width)
            setlinestyle(prefs.loop_select_line_stipple)
            draw_edges()
            setlinestyle(0)
            bgl.glLineWidth(1)

    glsettings.pop()
    glsettings.font_size()


###############################################################################
# Modal Operator
###############################################################################
class VIEW3D_OT_draw_nearest_element(bpy.types.Operator):
    bl_label = 'Draw Nearest Element'
    bl_idname = 'view3d.draw_nearest_element'
    bl_options = {'INTERNAL'}

    data = {}
    """:type: dict[int, dict[str, T]]"""
    handle = None

    type = bpy.props.EnumProperty(
        items=(('ENABLE', 'Enable', ''),
               ('DISABLE', 'Disable', ''),
               ('TOGGLE', 'Toggle', ''),
               ('KILL', 'Kill', '')),
        default='TOGGLE',
    )

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'

    @classmethod
    def remove_handler(cls):
        if cls.handle:
            bpy.types.SpaceView3D.draw_handler_remove(cls.handle, 'WINDOW')
        cls.handle = None

    @classmethod
    def remove_invalid_windows(cls):
        """存在しないWindowを除去"""
        exist_windows = []
        for wm in bpy.data.window_managers:
            for win in wm.windows:
                exist_windows.append(win.as_pointer())

        for addr in list(cls.data.keys()):
            if addr not in exist_windows:
                del cls.data[addr]

    @classmethod
    def active(cls, window):
        cls.remove_invalid_windows()
        return cls.data.get(window.as_pointer())

    def modal(self, context, event):
        """
        :type context: bpy.types.Context
        :type event: bpy.types.Event
        """

        self.remove_invalid_windows()

        win = context.window
        # 終了
        if win.as_pointer() not in self.data:
            if not self.data:
                self.remove_handler()
            redraw_areas(context, True)
            return {'FINISHED', 'PASS_THROUGH'}

        if context.mode != 'EDIT_MESH':
            return {'PASS_THROUGH'}

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                p = space_prop.get(area.spaces.active)
                if p.enable:
                    break
        else:  # 現在のwindowに描画対象が無いならスキップ
            return {'PASS_THROUGH'}

        prefs = DrawNearestPreferences.get_instance()
        data = self.active(win)
        mco = (event.mouse_x, event.mouse_y)
        mco_prev = data.get('mco')
        data['mco'] = mco
        data['target'] = None

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'PASS_THROUGH'}
        elif event.type.startswith('TIMER'):
            return {'PASS_THROUGH'}
        elif event.type == 'MOUSEMOVE':
            if mco == mco_prev:
                # 一時期ボタンの上にマウスがあると'MOUSEMOVE'イベントが
                # 発生し続ける謎仕様だった。今は無い？
                return {'PASS_THROUGH'}

        # modal中はcontext.area等は更新されないので手動で求める
        area = region = v3d = rv3d = None
        for sa in context.window.screen.areas:
            if sa.type == 'VIEW_3D':
                if (sa.x <= mco[0] <= sa.x + sa.width and
                        sa.y <= mco[1] <= sa.y + sa.height):
                    area = sa
                    break
        if area:
            for ar in area.regions:
                i = 0
                if ar.type == 'WINDOW':
                    if (ar.x <= mco[0] <= ar.x + ar.width and
                            ar.y <= mco[1] <= ar.y + ar.height):
                        region = ar
                        v3d = area.spaces.active
                        if v3d.region_quadviews:
                            rv3d = v3d.region_quadviews[i]
                        else:
                            rv3d = v3d.region_3d
                        break
                    i += 1

        if not (area and region):
            return {'PASS_THROUGH'}

        if v3d.viewport_shade == 'RENDERED':  # TODO: 他のview用に求めるか？
            return {'PASS_THROUGH'}

        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        mesh_select_mode = context.tool_settings.mesh_select_mode
        # スクリプト等でtool_settings.mesh_select_modeとbm.select_modeが
        # 一致しない状態になる場合がある為、揃える
        bm_select_mode = set()
        for i, val in enumerate(mesh_select_mode):
            if val:
                bm_select_mode.add(['VERT', 'EDGE', 'FACE'][i])
        bm.select_mode = bm_select_mode

        context_dict = context.copy()
        context_dict.update({'area': area, 'region': region})
        mco_region = [mco[0] - region.x, mco[1] - region.y]

        # キーマップから、一致するオペレータを探す
        mode = 'select'
        ring = False
        toggle = False

        shift = event.shift
        ctrl = event.ctrl
        alt = event.alt
        oskey = event.oskey
        if event.type in {'LEFT_SHIFT', 'RIGHT_SHIFT'}:
            if event.value == 'PRESS':
                shift = True
            elif event.value == 'RELEASE':
                shift = False
        if event.type in {'LEFT_CTRL', 'RIGHT_CTRL'}:
            if event.value == 'PRESS':
                ctrl = True
            elif event.value == 'RELEASE':
                ctrl = False
        if event.type in {'LEFT_ALT', 'RIGHT_ALT'}:
            if event.value == 'PRESS':
                alt = True
            elif event.value == 'RELEASE':
                alt = False
        if event.type in {'OSKEY'}:
            if event.value == 'PRESS':
                oskey = True
            elif event.value == 'RELEASE':
                oskey = False

        if shift or ctrl or alt or oskey:
            kc = bpy.context.window_manager.keyconfigs.user
            km = kc.keymaps['Mesh']
            for kmi in km.keymap_items:
                if not kmi.active:
                    continue
                if kmi.idname in {'mesh.loop_select', 'mesh.edgering_select'}:
                    if kmi.type == 'SELECTMOUSE':
                        if (kmi.shift == shift and kmi.ctrl == ctrl and
                                kmi.alt == alt and kmi.oskey == oskey):
                            ring = kmi.properties.ring
                            if mesh_select_mode[2]:
                                ring = True
                            mode = 'ring' if ring else 'loop'
                            toggle = kmi.properties.toggle
                            break

        # オペレータ実行時にScene.update()が実行され
        # lockcoordsのまで呼び出されてしまうから無効化しておく
        scene_pre = list(bpy.app.handlers.scene_update_pre)
        bpy.app.handlers.scene_update_pre.clear()
        scene_post = list(bpy.app.handlers.scene_update_post)
        bpy.app.handlers.scene_update_post.clear()

        use_internal = test_platform() and prefs.use_internal
        if mode == 'select':
            if use_internal:
                elem = find_nearest_ctypes(
                        context, context_dict, bm, mco_region)
            else:
                elem = find_nearest(context, context_dict, bm, mco_region)
            elems = [elem] if elem else []
        elif prefs.use_loop_select:
            if use_internal:
                edge, elems = find_loop_selection_ctypes(
                        context, context_dict, bm, mco_region, ring, toggle)
            else:
                edge, elems = find_loop_selection(
                        context, context_dict, bm, mco_region, ring, toggle)
        else:
            elems = []

        bpy.app.handlers.scene_update_pre[:] = scene_pre
        bpy.app.handlers.scene_update_post[:] = scene_post

        updated_areas = set()
        for sa in context.window.screen.areas:
            if sa.type != 'VIEW_3D':
                continue
            space_data = sa.spaces.active
            """:type: bpy.types.SpaceView3D"""
            prop = space_prop.get(space_data)
            if (not prop.enable or
                    space_data.viewport_shade == 'RENDERED'):
                continue
            key = space_data.region_3d.as_pointer()
            count = data['callback_count'].get(key)
            if count is not None:
                if count > 1:
                    updated_areas.add(sa)
            data['callback_count'][key] = 0
            for rv3d_ in space_data.region_quadviews:
                key = rv3d_.as_pointer()
                count = data['callback_count'].get(key)
                if count is not None:
                    if count > 1:
                        updated_areas.add(sa)
                data['callback_count'][key] = 0

        do_dm_cache_updated = False
        if elems:
            if prefs.use_derived_mesh and data['do_dm_cache_update']:
                if mesh.as_pointer() in dm_cache:
                    del dm_cache[mesh.as_pointer()]
                data['do_dm_cache_update'] = False
                do_dm_cache_updated = True
            # index_update()はほぼ無視できる処理時間。10万ポリで1e-5以下
            bm.verts.index_update()
            bm.edges.index_update()
            bm.faces.index_update()

            require_face_centers = prefs.face_emphasis == 'CENTER'
            if prefs.use_derived_mesh:
                verts, edges, faces, centers = get_dm_elems(
                        mesh, bm, elems, require_face_centers)
            else:
                verts, edges, faces, centers = get_bmdm_elems(
                        mesh, bm, elems, require_face_centers, False)
            elems_key = []
            for ele in elems:
                if isinstance(ele, bmesh.types.BMVert):
                    elems_key.append((repr(ele), tuple(ele.co)))
                else:
                    elems_key.append(repr(ele))
            key = (mode, tuple(elems_key))
            dm = get_dm(mesh)
            if dm:
                dm_type = get_dm(mesh).type
                data['target'] = [key, mode, dm_type, verts, edges, faces,
                                  centers]

        data['object_is_updated'] = False

        # 再描画
        redraw = False
        if updated_areas:
            redraw = True
        elif (data['target'] and not data['target_prev'] or
                not data['target'] and data['target_prev']):
            redraw = True
        elif data['target']:
            if data['target_prev'][0] != data['target'][0]:
                redraw = True
            elif do_dm_cache_updated:
                redraw = True
        if redraw:
            if prefs.redraw_all:
                redraw_areas(context)
            else:
                area.tag_redraw()
        # Areaが切り替わったら前のAreaを再描画
        addr = data['area_prev']
        if addr and addr != area.as_pointer():
            for sa in context.screen.areas:
                if sa.as_pointer() == addr:
                    sa.tag_redraw()
                    break

        dm = get_dm(mesh)
        if dm:
            data['dm_address'] = addressof(dm) if dm else None
            data['dm_num_elems'] = [get_dm_attr(mesh, dm, 'num_verts'),
                                    get_dm_attr(mesh, dm, 'num_edges'),
                                    get_dm_attr(mesh, dm, 'num_faces'),
                                    get_dm_attr(mesh, dm, 'num_loops'),]
            data['target_prev'] = data['target']
            data['area_prev'] = area.as_pointer()

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if self.type == 'KILL':
            self.data.clear()
            redraw_areas(context, True)
            return {'FINISHED'}

        win = context.window
        v3d = context.space_data
        prop = space_prop.get(v3d)
        type = self.type
        if self.type == 'TOGGLE':
            if prop.enable:
                type = 'DISABLE'
            else:
                type = 'ENABLE'

        if type == 'DISABLE':
            # 同期に問題有り
            # if win.as_pointer() in self.data:
            #     del self.data[win.as_pointer()]
            context.area.tag_redraw()
            return {'FINISHED'}
        else:
            if win.as_pointer() in self.data:
                return {'FINISHED'}
            self.data[win.as_pointer()] = data = {}
            data['event'] = event
            data['target'] = None
            data['target_prev'] = None
            data['callback_count'] = {}  # 視点変更等で再描画されるとカウント
            data['object_is_updated'] = False
            data['do_dm_cache_update'] = True
            data['dm_address'] = None
            data['dm_num_elems'] = [-1, -1, -1, -1]
            data['area_prev'] = None
            if not self.handle:
                self.__class__.handle = bpy.types.SpaceView3D.draw_handler_add(
                    draw_callback, (self.__class__, context,), 'WINDOW',
                        'POST_VIEW')
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

    @classmethod
    def unregister(cls):
        cls.data.clear()
        try:
            cls.remove_handler()
        except:
            pass


###############################################################################
# Panel Draw Func / Callback / Register / Unregister
###############################################################################
def menu_func(self, context):
    prop = space_prop.get(context.space_data)
    self.layout.separator()
    col = self.layout.column(align=True)
    """:type: bpy.types.UILayout"""
    v3d = context.space_data
    if context.mode != 'EDIT_MESH' or v3d.viewport_shade == 'RENDERED':
        col.active = False
    col.prop(prop, 'enable', text='Draw Nearest')


@bpy.app.handlers.persistent
def scene_update_pre(scene):
    win = bpy.context.window
    if not win:  # アニメーションレンダリング時にて
        return
    if bpy.context.region:
        return

    cls = VIEW3D_OT_draw_nearest_element

    if bpy.context.mode == 'EDIT_MESH':
        data = cls.active(win)
        if data:
            ob = bpy.context.object
            dm_updated = False
            dm_address = None
            dm_num_elems = [-1, -1, -1, -1]
            prefs = DrawNearestPreferences.get_instance()
            if prefs.use_derived_mesh:
                dm = get_dm(ob.data)
                if dm:
                    dm_address = addressof(dm)
                    dm_p = pointer(dm)
                    dm_num_elems = [dm.getNumVerts(dm_p),
                                    dm.getNumEdges(dm_p),
                                    dm.getNumPolys(dm_p),
                                    dm.getNumLoops(dm_p)]
                dm_updated = not (dm and dm_address == data['dm_address'] and
                                  dm_num_elems == data['dm_num_elems'])
            if (ob.is_updated or ob.is_updated_data or
                    ob.data.is_updated or ob.data.is_updated_data or
                    dm_updated):
                data['object_is_updated'] = True
                data['do_dm_cache_update'] = True
                data['dm_address'] = dm_address
                data['dm_num_elems'] = dm_num_elems

    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces.active
            p = space_prop.get(v3d)
            if p.enable:
                if not cls.active(win):
                    c = bpy.context.copy()
                    c['area'] = area
                    c['region'] = area.regions[-1]
                    operator_call(
                        bpy.ops.view3d.draw_nearest_element,
                        c, 'INVOKE_DEFAULT', type='ENABLE',
                        _scene_update=False)
                break
    else:
        # disable ?
        pass


@bpy.app.handlers.persistent
def load_pre(dummy):
    # オブジェクトは開放しておかないとアドレスが再利用された場合に不具合になる
    VIEW3D_OT_draw_nearest_element.unregister()
    dm_cache.clear()


classes = [
    DrawNearestPreferences,
    VIEW3D_PG_DrawNearest,
    VIEW3D_OT_draw_nearest_element,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    space_prop.register()
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(menu_func)
    bpy.app.handlers.scene_update_pre.append(scene_update_pre)
    bpy.app.handlers.load_pre.append(load_pre)


def unregister():
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    bpy.app.handlers.load_pre.remove(load_pre)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(menu_func)
    space_prop.unregister()
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
