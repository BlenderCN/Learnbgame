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
    'name': 'Align Tools',
    'author': 'chromoly',
    'version': (0, 1, 1),
    'blender': (2, 77, 0),
    'location': 'View3D > Toolshelf',
    'description': '',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/quadview_move',
    'tracker_url': '',
    'category': '3D View',
}


# TODO: オペレータでmode毎に値を保存

from collections import OrderedDict
import importlib
import itertools
import os
import math
import time

import bpy
import bpy.utils.previews
import bmesh
import bgl
import mathutils
from mathutils import Matrix, Vector

try:
    importlib.reload(utils)
    importlib.reload(localutils)
    importlib.reload(va)
    importlib.reload(enums)
    importlib.reload(funcs)
    importlib.reload(grouping)
    importlib.reload(memocoords)
    importlib.reload(tooldata)
except NameError:
    from . import utils
    from . import localutils
    from . import va
    from . import enums
    from . import funcs
    from . import grouping
    from . import memocoords
    from . import tooldata
from .localutils.checkargs import CheckArgs
from .va import vaoperator as vaop
from .va import vaarmature as vaarm
from .va import vamath as vam
from .va import convexhull
from .va import vagl
from .va import unitsystem
from .va import manipulatormatrix
from .va import vaview3d as vav
from .enums import *

from . import op_stubs
from . import op_plane
from . import op_align
from . import op_edge
from . import op_matrix
from . import op_shift
from . import custom_icons


tool_data = tooldata.tool_data
memoize = tool_data.memoize
checkargs = CheckArgs(True)

EPS = 1e-5

# preview_collections = {}


###############################################################################
# Preference
###############################################################################
class AlignToolsPreferences(
        utils.AddonKeyMapUtility,
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'use_pie_menu')

        super().draw(context, layout.column())

    def update_keymap_items(self, context=None):
        items = []
        for km_name, kmi_id in self.registered_keymap_items():
            km = self.get_keymap(km_name)
            for kmi in km.keymap_items:
                if kmi.id == kmi_id:
                    items.append(kmi)
        for kmi in items:
            if self.use_pie_menu:
                if kmi.idname == 'wm.call_menu':
                    if kmi.properties.name == MenuMain.bl_idname:
                        kmi.idname = 'wm.call_menu_pie'
                        kmi.properties.name = PieMenuMain.bl_idname
            else:
                if kmi.idname == 'wm.call_menu_pie':
                    if kmi.properties.name == PieMenuMain.bl_idname:
                        kmi.idname = 'wm.call_menu'
                        kmi.properties.name = MenuMain.bl_idname

    use_pie_menu = bpy.props.BoolProperty(
        name='Pie Menu',
        default=False,
        update=update_keymap_items)


###############################################################################
# Menu, Panel
###############################################################################
class MenuManipulator(bpy.types.Menu):
    bl_idname = 'LA_MT_manipulator'
    bl_label = 'Manipulator A to B'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator(op_matrix.OperatorManipulatorSetA.bl_idname,
                        text='Set A',
                        icon='MANIPUL')
        layout.operator(op_matrix.OperatorManipulatorSetB.bl_idname,
                        text='Set B',
                        icon='MANIPUL')

        layout.separator()
        op = layout.operator(op_matrix.OperatorManipulatorAtoB.bl_idname,
                             text='Translate',
                             icon='MAN_TRANS')
        op.transform_mode = 'TRANSLATE'
        op = layout.operator(op_matrix.OperatorManipulatorAtoB.bl_idname,
                             text='Rotate',
                             icon='MAN_ROT')
        op.transform_mode = 'ROTATE'
        op = layout.operator(op_matrix.OperatorManipulatorAtoB.bl_idname,
                             text='All',
                             icon='MANIPUL')
        op.transform_mode = 'ALL'

        layout.separator()
        op = layout.operator(op_matrix.OperatorManipulatorAlign.bl_idname)


class MenuMain(bpy.types.Menu):
    bl_idname = 'AT_MT_main'
    bl_label = 'Align Tools'

    # @classmethod
    # def poll(cls, context):
    #     if context.active_object:
    #         return context.active_object.mode == 'EDIT'
    #     else:
    #         return False

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        pcol = custom_icons.preview_collections['icon32']

        # Set Plane / Axis
        layout.operator(op_plane.OperatorSetPlane.bl_idname,
                        icon_value=pcol['set_plane'].icon_id)
        layout.operator(op_plane.OperatorSetAxis.bl_idname,
                        icon_value=pcol['set_axis'].icon_id)

        # Align
        layout.separator()
        layout.operator(op_align.OperatorAlign.bl_idname,
                        icon_value=pcol['align'].icon_id)
        layout.operator(op_align.OperatorAlignToPlane.bl_idname,
                        icon_value=pcol['align_to_plane'].icon_id)
        layout.operator(op_align.OperatorDistribute.bl_idname,
                        icon_value=pcol['distribute'].icon_id)

        # Manipulator
        layout.separator()
        layout.menu(MenuManipulator.bl_idname, icon='MANIPUL')

        # Edge
        layout.separator()
        layout.operator(op_edge.OperatorEdgeAlignToPlane.bl_idname,
                        icon_value=pcol['edge_align_to_plane'].icon_id)
        layout.operator(op_edge.OperatorEdgeIntersect.bl_idname,
                        icon_value=pcol['edge_intersect'].icon_id)
        layout.operator(op_edge.OperatorEdgeUnbend.bl_idname,
                        icon_value=pcol['edge_unbend'].icon_id)

        # Shift
        layout.separator()
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Tangent',
                             icon_value=pcol['shift_tangent'].icon_id)
        op.mode = 'tangent'
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Normal',
                             icon_value=pcol['shift_normal'].icon_id)
        op.mode = 'normal'


class PieMenuAlignVerts(bpy.types.Menu):
    bl_idname = 'AT_PIE_align_verts'
    bl_label = 'Align Verts'

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator_context = 'INVOKE_DEFAULT'

        def add(space, axis, text):
            op = pie.operator(op_align.OperatorAlignToPlane.bl_idname,
                              text=text)
            op.space = space
            op.axis = axis
            op.use_event = True

        add('GLOBAL', 'Z', 'Z')
        add('AXIS', 'Z', 'Axis')
        add('GLOBAL', 'X', 'X')
        add('VIEW', 'Y', 'View Y')
        add('VIEW', 'X', 'View X')
        add('PLANE', 'Z', 'Plane Z')
        add('GLOBAL', 'Y', 'Y')


# class PieMenuAlignEdges(bpy.types.Menu):
#     bl_idname = 'AT_PIE_align_edges'
#     bl_label = 'Align Edges'


class PieMenuMain(bpy.types.Menu):
    bl_idname = 'AT_PIE_main'
    bl_label = 'Align Tools'

    def draw(self, context):
        pcol = custom_icons.preview_collections['icon32']
        pie = self.layout.menu_pie()
        pie.operator_context = 'INVOKE_DEFAULT'

        # pie menu item order
        # 5 4 6
        # 1   2
        # 7 3 8

        pie.operator(op_align.OperatorAlign.bl_idname,
                     icon_value=pcol['align'].icon_id)

        layout = pie.column()
        layout.menu(MenuManipulator.bl_idname, text='Manipulator',
                    icon='MANIPUL')
        layout.separator()
        layout.operator(op_edge.OperatorEdgeAlignToPlane.bl_idname,
                        icon_value=pcol['edge_align_to_plane'].icon_id)
        layout.operator(op_edge.OperatorEdgeIntersect.bl_idname,
                        icon_value=pcol['edge_intersect'].icon_id)
        layout.operator(op_edge.OperatorEdgeUnbend.bl_idname,
                        icon_value=pcol['edge_unbend'].icon_id)
        layout.separator()
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Tangent',
                             icon_value=pcol['shift_tangent'].icon_id)
        op.mode = 'tangent'
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Normal',
                             icon_value=pcol['shift_normal'].icon_id)
        op.mode = 'normal'

        if 1:
            pie.operator(op_align.OperatorAlignToPlane.bl_idname,
                         icon_value=pcol['align_to_plane'].icon_id)
        else:
            op = pie.operator('wm.call_menu_pie', text='Align Verts',
                              icon_value=pcol['align_to_plane'].icon_id)
            op.name = PieMenuAlignVerts.bl_idname

        pie.operator(op_plane.OperatorSetPlane.bl_idname,
                     icon_value=pcol['set_plane'].icon_id)

        pie.operator(op_plane.OperatorSetAxis.bl_idname,
                     icon_value=pcol['set_axis'].icon_id)

        pie.separator()

        pie.operator(op_align.OperatorDistribute.bl_idname,
                     icon_value=pcol['distribute'].icon_id)
        pie.separator()


class PanelMain(bpy.types.Panel):
    bl_idname = 'LA_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    bl_label = 'Align Tools'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH', 'EDIT_ARMATURE', 'POSE'}

    def draw(self, context):
        main_layout = self.layout

        main_layout.operator_context = 'INVOKE_REGION_WIN'

        pcol = custom_icons.preview_collections['icon32']

        # Set Plane / Axis
        layout = main_layout.column(align=True)
        layout.operator(op_plane.OperatorSetPlane.bl_idname,
                        icon_value=pcol['set_plane'].icon_id)
        layout.operator(op_plane.OperatorSetAxis.bl_idname,
                        icon_value=pcol['set_axis'].icon_id)

        # Align
        layout = main_layout.column(align=True)
        layout.operator(op_align.OperatorAlign.bl_idname,
                        icon_value=pcol['align'].icon_id)
        layout.operator(op_align.OperatorAlignToPlane.bl_idname,
                        icon_value=pcol['align_to_plane'].icon_id)
        layout.operator(op_align.OperatorDistribute.bl_idname,
                        icon_value=pcol['distribute'].icon_id)

        # Edge
        layout = main_layout.column(align=True)
        layout.operator(op_edge.OperatorEdgeAlignToPlane.bl_idname,
                        icon_value=pcol['edge_align_to_plane'].icon_id)
        layout.operator(op_edge.OperatorEdgeIntersect.bl_idname,
                        icon_value=pcol['edge_intersect'].icon_id)
        layout.operator(op_edge.OperatorEdgeUnbend.bl_idname,
                        icon_value=pcol['edge_unbend'].icon_id)

        # Shift
        layout = main_layout.column(align=True)
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Tangent',
                             icon_value=pcol['shift_tangent'].icon_id)
        op.mode = 'tangent'
        op.cursor_to_center = True
        op = layout.operator(op_shift.OperatorShift.bl_idname,
                             text='Shift Normal',
                             icon_value=pcol['shift_normal'].icon_id)
        op.mode = 'normal'
        op.cursor_to_center = True


@bpy.app.handlers.persistent
def load_pre(dummy):
    """クラッシュ回避"""
    # 起動時のstartup.blendでは呼ばれない
    custom_icons.unload_icons()


@bpy.app.handlers.persistent
def load_post(dummy):
    """クラッシュ回避"""
    custom_icons.unload_icons()
    custom_icons.load_icons()


###############################################################################
# Register / Unregister
###############################################################################
classes = [
    AlignToolsPreferences,

    MenuManipulator,
    MenuMain,

    PieMenuAlignVerts,
    PieMenuMain,

    PanelMain,
]

classes.extend(op_stubs.classes)
classes.extend(op_plane.classes)
classes.extend(op_align.classes)
classes.extend(op_edge.classes)
classes.extend(op_matrix.classes)
classes.extend(op_shift.classes)


addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        addon_prefs = AlignToolsPreferences.get_instance()
        """:type: AlignToolsPreferences"""
        km = addon_prefs.get_keymap('3D View')
        kmi = km.keymap_items.new(
            'wm.call_menu', 'A', 'PRESS', shift=True, ctrl=True, alt=True,
            head=True)
        # kmi.active = False
        kmi.properties.name = MenuMain.bl_idname
        addon_keymaps.append((km, kmi))
        addon_prefs.register_keymap_items(addon_keymaps)

        addon_prefs.update_keymap_items()

    custom_icons.load_icons()
    bpy.app.handlers.load_pre.append(load_pre)
    bpy.app.handlers.load_post.append(load_post)


def unregister():
    addon_prefs = AlignToolsPreferences.get_instance()
    """:type: AlignToolsPreferences"""
    addon_prefs.unregister_keymap_items()

    custom_icons.unload_icons()
    bpy.app.handlers.load_pre.remove(load_pre)
    bpy.app.handlers.load_post.remove(load_post)

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
