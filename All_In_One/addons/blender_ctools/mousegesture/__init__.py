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
    'name': 'Mouse Gesture',
    'author': 'chromoly',
    'version': (0, 7),
    'blender': (2, 77, 0),
    'location': 'UserPreferences > Add-ons > Mouse Gesture',
    'description': '',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/blender_mouse_gesture',
    'category': 'User Interface',
}


from contextlib import contextmanager
import fnmatch
import importlib
import math

import bpy
import bgl
import blf
from mathutils import Vector

try:
    importlib.reload(utils)
except NameError:
    from . import utils


PIXEL_SIZE = 1.0

_RELEASE = False


###############################################################################
# Settings
###############################################################################
def reset_groups(context):
    prefs = MouseGesturePreferences.get_instance()
    groups = prefs.gesture_groups
    groups.clear()

    def set_arg(item, name, value):
        key = (item.operator + '.' + name).replace('.', '__')
        arg = item.operator_args[key]
        setattr(arg, key, value)

    # View --------------------------------------------------------------------
    group = groups.add()
    group.name = 'View'

    for gesture, name, view_type in (
            ('D', 'View Front', 'FRONT'),
            ('DU', 'View Back', 'BACK'),
            ('RL', 'View Left', 'LEFT'),
            ('R', 'View Right', 'RIGHT'),
            ('U', 'View Top', 'TOP'),
            ('UD', 'View Bottom', 'BOTTOM'),
            ('RU, UR', 'View Camera', 'CAMERA')):
        item = group.gesture_items.add()
        item.name = name
        item.gesture = gesture
        item.operator = 'view3d.viewnumpad'
        set_arg(item, 'type', view_type)

    item = group.gesture_items.add()
    item.name = 'View Persp/Ortho'
    item.gesture = 'LD'
    item.operator = 'view3d.view_persportho'

    item = group.gesture_items.add()
    item.name = 'Local View'
    item.gesture = 'DR'
    item.operator = 'view3d.localview'

    if 'use_local_grid' in bpy.types.SpaceView3D.bl_rna.properties:
        item = group.gesture_items.add()
        item.name = 'Local Grid'
        item.gesture = 'DL'
        item.operator = 'view3d.localgrid'

    item = group.gesture_items.add()
    item.name = 'View All'
    item.gesture = 'LU'
    item.operator = 'view3d.view_all'

    item = group.gesture_items.add()
    item.name = 'View to Cursor'
    item.gesture = 'LDR'
    item.operator = 'view3d.view_center_cursor'

    item = group.gesture_items.add()
    item.name = 'View Selected'
    item.gesture = 'LR'
    item.operator = 'view3d.view_selected'

    item = group.gesture_items.add()
    item.name = 'View Selected (no zoom)'
    item.gesture = 'L'
    item.type = 'STRING'
    item.exec_string = '\n'.join(
        ['scn = context.scene',
         'cursor_bak = scn.cursor_location[:]',
         'bpy.ops.view3d.snap_cursor_to_selected(False)',
         'bpy.ops.view3d.view_center_cursor(False)',
         'scn.cursor_location = cursor_bak',
         ])

    # Transform ---------------------------------------------------------------
    group = groups.add()
    group.name = 'Transform'
    group.use_relative = True

    item = group.gesture_items.add()
    item.name = 'Grab/Move'
    item.gesture = 'U'
    item.operator = 'transform.translate'

    item = group.gesture_items.add()
    item.name = 'Rotate'
    item.gesture = 'UR*, UL*'
    item.operator = 'transform.rotate'

    item = group.gesture_items.add()
    item.name = 'Scale'
    item.gesture = 'UD'
    item.operator = 'transform.resize'

    # Scale -------------------------------------------------------------------
    group = groups.add()
    group.name = 'Transform: Scale'
    for gesture, name, value, pivot in (
            ('R', 'Scale Cursor: 0.0 along View X', (0, 1, 1), 'CURSOR'),
            ('U', 'Scale Cursor: 0.0 along View Y', (1, 0, 1), 'CURSOR'),
            ('D', 'Scale Cursor: 0.0 along View Z', (1, 1, 0), 'CURSOR'),

            ('RL', 'Scale Cursor: -1.0 along View X', (-1, 1, 1), 'CURSOR'),
            ('UD', 'Scale Cursor: -1.0 along View Y', (1, -1, 1), 'CURSOR'),
            ('DU', 'Scale Cursor: -1.0 along View Z', (1, 1, -1), 'CURSOR'),

            ('RU, RD', 'Scale Active: 0.0 along View X', (0, 1, 1),
             'ACTIVE_ELEMENT'),
            ('UL, UR', 'Scale Active: 0.0 along View Y', (1, 0, 1),
             'ACTIVE_ELEMENT'),
            ('DL, DR', 'Scale Active: 0.0 along View Z', (1, 1, 0),
             'ACTIVE_ELEMENT'),

            ('RLR, RLU, RLD', 'Scale Active: -1.0 along View X', (-1, 1, 1),
             'ACTIVE_ELEMENT'),
            ('UDU, UDL, UDR', 'Scale Active: -1.0 along View Y', (1, -1, 1),
             'ACTIVE_ELEMENT'),
            ('DUD, DUL, DUR', 'Scale Active: -1.0 along View Z', (1, 1, -1),
             'ACTIVE_ELEMENT')):
        item = group.gesture_items.add()
        item.name = name
        item.gesture = gesture
        item.type = 'STRING'
        item.exec_string = '\n'.join(
            ['v3d = context.space_data',
             'bak = (v3d.pivot_point, v3d.use_pivot_point_align)',
             "v3d.pivot_point = '{}'".format(pivot),
             'v3d.use_pivot_point_align = True',
             'bpy.ops.transform.resize(True, value={}, '
             'constraint_axis=(True, True, True), '
             "constraint_orientation='VIEW')".format(value),
             'v3d.pivot_point, v3d.use_pivot_point_align = bak'
             ]
        )

    # Edit --------------------------------------------------------------------
    # Mesh Selection Mode
    group = groups.add()
    group.name = 'Mesh Select Mode'

    item = group.gesture_items.add()
    item.name = 'Vertex'
    item.gesture = 'D'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.mesh_select_mode')
    set_arg(item, 'value', '[True, False, False]')

    item = group.gesture_items.add()
    item.name = '+/- Vertex'
    item.gesture = 'DU'
    item.type = 'STRING'
    item.exec_string = 'context.tool_settings.mesh_select_mode[0] ^= True'

    item = group.gesture_items.add()
    item.name = 'Edge'
    item.gesture = 'L'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.mesh_select_mode')
    set_arg(item, 'value', '[False, True, False]')

    item = group.gesture_items.add()
    item.name = '+/- Edge'
    item.gesture = 'LR'
    item.type = 'STRING'
    item.exec_string = 'context.tool_settings.mesh_select_mode[1] ^= True'

    item = group.gesture_items.add()
    item.name = 'Face'
    item.gesture = 'U'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.mesh_select_mode')
    set_arg(item, 'value', '[False, False, True]')

    item = group.gesture_items.add()
    item.name = '+/- Face'
    item.gesture = 'UD'
    item.type = 'STRING'
    item.exec_string = 'context.tool_settings.mesh_select_mode[2] ^= True'

    item = group.gesture_items.add()
    item.name = 'Toggle Occlude Geometry'
    item.gesture = 'R'
    item.operator = 'wm.context_toggle'
    set_arg(item, 'data_path', 'space_data.use_occlude_geometry')

    # Snap Element
    item = group.gesture_items.add()
    item.name = 'Snap Element: Increment'
    item.gesture = 'RD'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.snap_element')
    set_arg(item, 'value', "'INCREMENT'")

    item = group.gesture_items.add()
    item.name = 'Snap Element: Vertex'
    item.gesture = 'RL'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.snap_element')
    set_arg(item, 'value', "'VERTEX'")

    item = group.gesture_items.add()
    item.name = 'Snap Element: Edge'
    item.gesture = 'RU'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.snap_element')
    set_arg(item, 'value', "'EDGE'")

    item = group.gesture_items.add()
    item.name = 'Snap Element: Face'
    item.gesture = 'RU*'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'tool_settings.snap_element')
    set_arg(item, 'value', "'FACE'")

    # Pivot Point
    item = group.gesture_items.add()
    item.name = 'Pivot Point: Bounding Box Center'
    item.gesture = 'LD'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'space_data.pivot_point')
    set_arg(item, 'value', "'BOUNDING_BOX_CENTER'")

    item = group.gesture_items.add()
    item.name = 'Pivot Point: 3D Cursor'
    item.gesture = 'LU'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'space_data.pivot_point')
    set_arg(item, 'value', "'CURSOR'")

    item = group.gesture_items.add()
    item.name = 'Pivot Point: Median Point'
    item.gesture = 'UL'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'space_data.pivot_point')
    set_arg(item, 'value', "'MEDIAN_POINT'")

    item = group.gesture_items.add()
    item.name = 'Pivot Point: Individual Origins'
    item.gesture = 'ULR'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'space_data.pivot_point')
    set_arg(item, 'value', "'INDIVIDUAL_ORIGINS'")

    item = group.gesture_items.add()
    item.name = 'Pivot Point: Active Element'
    item.gesture = 'UR'
    item.operator = 'wm.context_set_value'
    set_arg(item, 'data_path', 'space_data.pivot_point')
    set_arg(item, 'value', "'ACTIVE_ELEMENT'")


class MouseGestureOpArg(bpy.types.PropertyGroup):
    attrs = []

    def draw(self, context, layout):
        """
        :type context: bpy.types.Context
        :type layout: bpy.types.UILayout
        """
        # prop = getattr(self, self.name)
        layout.prop(self, self.name)


def enum_items_mod(self, context):
    return tuple([(mod, mod, '') for mod in bpy.ops])


def enum_items_op(self, context):
    if hasattr(bpy.ops, self.mod):
        return tuple([(op, op, '') for op in dir(getattr(bpy.ops, self.mod))])
    else:
        return ()


def prop_from_struct(prop):
    if prop.type not in ('BOOLEAN', 'ENUM', 'INT', 'FLOAT', 'STRING'):
        return None

    attrs = {'name': prop.name,
             'description': prop.description}

    if prop.type in ('BOOLEAN', 'INT', 'FLOAT') and prop.array_length > 0:
        attrs['default'] = tuple(prop.default_array)
        attrs['size'] = prop.array_length
    else:
        attrs['default'] = prop.default
    if prop.type in ('BOOLEAN', 'INT', 'FLOAT', 'STRING'):
        if prop.subtype == 'LAYER_MEMBER':  # 未対応
            attrs['subtype'] = 'LAYER'
        else:
            attrs['subtype'] = prop.subtype
    if prop.type == 'STRING':
        attrs['maxlen'] = prop.length_max
    if prop.type in ('INT', 'FLOAT'):
        attrs['min'] = prop.hard_min
        attrs['max'] = prop.hard_max
        attrs['soft_min'] = prop.soft_min
        attrs['soft_max'] = prop.soft_max
        attrs['step'] = prop.step
        if prop.type == 'FLOAT':
            attrs['precision'] = prop.precision
            attrs['unit'] = prop.unit
    if prop.type == 'ENUM':
        attrs['items'] = tuple(
            [(p.identifier, p.name, p.description, p.icon, p.value)
             for p in prop.enum_items])

    attrs['options'] = set()
    if prop.is_hidden:
        attrs['options'].add('HIDDEN')
    if prop.is_enum_flag:
        attrs['options'].add('ENUM_FLAG')

    if prop.type == 'BOOLEAN':
        if prop.array_length > 0:
            return bpy.props.BoolVectorProperty(**attrs)
        else:
            return bpy.props.BoolProperty(**attrs)
    elif prop.type == 'ENUM':
        if len(attrs['items']) == 0:
            # get関数があるものと仮定する
            d = {k: attrs[k] for k in ('name', 'description', 'default')}
            d['options'] = attrs['options'] & {'HIDDEN'}
            return bpy.props.StringProperty(**d)
        else:
            return bpy.props.EnumProperty(**attrs)
    elif prop.type == 'FLOAT':
        if prop.array_length > 0:
            return bpy.props.FloatVectorProperty(**attrs)
        else:
            return bpy.props.FloatProperty(**attrs)
    elif prop.type == 'INT':
        if prop.array_length > 0:
            return bpy.props.IntVectorProperty(**attrs)
        else:
            return bpy.props.IntProperty(**attrs)
    elif prop.type == 'STRING':
        return bpy.props.StringProperty(**attrs)


def get_operator(name):
    split = name.split('.')
    op = None
    if len(split) == 2:
        m, o = split
        if m in dir(bpy.ops):  # hasattr(bpy.ops, m)は無意味
            mod = getattr(bpy.ops, m)
            if o in dir(mod):  # hasattr(mod, o)は無意味
                op = getattr(mod, o)
    return op


def ensure_operator_args(item, clear=False):
    bl_rna = None
    op = get_operator(item.operator)
    if op:
        bl_rna = op.get_rna().bl_rna
    if not bl_rna:
        return

    props = [p for p in bl_rna.properties if p.identifier != 'rna_type']
    if clear:
        item.operator_args.clear()
        for i in range(len(props)):
            item.operator_args.add()
    else:
        n = len(item.operator_args) - len(props)
        if n > 0:
            for i in range(n):
                item.operator_args.remove(len(item.operator_args) - 1)
        elif n < 0:
            for i in range(-n):
                item.operator_args.add()
    for arg, prop in zip(item.operator_args, props):
        attr = item.operator + '.' + prop.identifier  # eg. mesh.delete.type
        attr = attr.replace('.', '__')
        arg.name = attr
        setattr(MouseGestureOpArg, attr, prop_from_struct(prop))
        MouseGestureOpArg.attrs.append(attr)


def prop_operator_update(self, context):
    ensure_operator_args(self, True)


def prop_operator_search_items(self, context):
    if hasattr(prop_operator_search_items, 'items'):
        return prop_operator_search_items.items
    items = []
    for mod in dir(bpy.ops):
        for op in dir(getattr(bpy.ops, mod)):
            name = mod + '.' + op
            items.append((name, name, ''))
    prop_operator_search_items.items = items
    return items


def prop_operator_search_set(self, value):
    items = prop_operator_search_items(bpy.context)
    name = items[value][0]
    self.operator = name


class MouseGestureItem(bpy.types.PropertyGroup):
    show_expanded = bpy.props.BoolProperty(
        name='Show Details', default=False)
    gesture = bpy.props.StringProperty(
        name='Gesture',
        description='U, D, L, R, and wildcard characters')
    type = bpy.props.EnumProperty(
        name='type',
        items=(('OPERATOR', 'Operator', ''),
               ('STRING', 'String', '')),
        default='OPERATOR',
    )
    operator = bpy.props.StringProperty(
        name='Operator',
        update=prop_operator_update)
    operator_args = bpy.props.CollectionProperty(
        name='Arguments', type=MouseGestureOpArg
    )
    operator_execution_context = bpy.props.EnumProperty(
        name='Execution Context',
        items=[(s, s, '') for s in
               ['INVOKE_DEFAULT', 'INVOKE_REGION_WIN',
                'INVOKE_REGION_CHANNELS', 'INVOKE_REGION_PREVIEW',
                'INVOKE_AREA', 'INVOKE_SCREEN', 'EXEC_DEFAULT',
                'EXEC_REGION_WIN', 'EXEC_REGION_CHANNELS',
                'EXEC_REGION_PREVIEW', 'EXEC_AREA', 'EXEC_SCREEN']],
        default='INVOKE_DEFAULT'
    )
    operator_undo = bpy.props.BoolProperty(name='Undo', default=True)
    operator_search = bpy.props.EnumProperty(
        name='Operator',
        items=prop_operator_search_items,
        set=prop_operator_search_set,
    )
    exec_string = bpy.props.StringProperty(
        name='Exec String',
    )

    def draw_details(self, context, layout):
        split = layout.row().split(0.05)
        _ = split.column()
        column = split.column()

        box = column.box()
        if self.type == 'OPERATOR':
            row = box.row()
            sub = row.row(align=True)
            sub.prop(self, 'operator', text='')
            op = sub.operator('wm.mouse_gesture_search_operator',
                              text='', icon='VIEWZOOM')
            WM_OT_mouse_gesture_search_operator.data[id(self)] = self
            op.target = str(id(self))
            sub = row.row()
            sub.prop(self, 'operator_execution_context', text='')
            sub = row.row()
            sub.prop(self, 'operator_undo')
            sub.active = self.is_property_set('operator_undo')

            if self.operator_args:
                flow = box.column_flow(2)
                for arg in self.operator_args:
                    sub_box = flow.box()
                    row = sub_box.row()
                    sub = row.row()
                    sub.prop(arg, arg.name)
                    if arg.is_property_set(arg.name):
                        sub = row.row()
                        sub.alignment = 'RIGHT'
                        sub.context_pointer_set('mg_arg', arg)
                        op = sub.operator('wm.mouse_gesture_stubs',
                                          text='', icon='PANEL_CLOSE')
                        op.function = 'arg_unset'
                    else:
                        sub_box.active = False
        else:
            row = box.row()
            sp = row.split(0.8)
            sub = sp.row()
            sub.prop(self, 'exec_string', text='')
            sub = sp.row()
            sub.operator_menu_enum('wm.mouse_gesture_from_text',
                                   'text', text='Paste Text', icon='PASTEDOWN')

    def draw(self, context, layout):
        """
        :type context: bpy.types.Context
        :type layout: bpy.types.UILayout
        """

        column = layout.column()
        column.context_pointer_set('mg_item', self)
        title_row = column.row()

        # 詳細表示切り替え
        row = title_row.row()
        row.alignment = 'LEFT'
        icon = 'TRIA_DOWN' if self.show_expanded else 'TRIA_RIGHT'
        op = row.operator('wm.context_toggle', text='', icon=icon,
                          emboss=False)
        op.data_path = 'mg_item.show_expanded'

        # ジェスチャー
        sub = title_row.row()
        sub.prop(self, 'gesture', text='')

        # Operator / Exec String
        title_row.prop(self, 'type', text='')

        # 名前
        title_row.prop(self, 'name', text='Name')

        # 削除
        row = title_row.row()
        row.alignment = 'RIGHT'
        op = row.operator('wm.mouse_gesture_stubs',
                          text='', icon='PANEL_CLOSE')
        op.function = 'item_remove'

        # 詳細
        if self.show_expanded:
            self.draw_details(context, column)


class MouseGestureItemGroup(bpy.types.PropertyGroup):
    show_expanded = bpy.props.BoolProperty(
        name='Show Details', default=False)
    use_relative = bpy.props.BoolProperty(
        name='Relative', default=False)
    gesture_items = bpy.props.CollectionProperty(
        name='Items', type=MouseGestureItem)

    def draw(self, context, layout):
        """
        :type context: bpy.types.Context
        :type layout: bpy.types.UILayout
        """
        column = layout.column()

        column.context_pointer_set('mg_group', self)
        title_row = column.row()

        # 詳細表示切り替え
        row = title_row.row()
        row.alignment = 'LEFT'
        icon = 'TRIA_DOWN' if self.show_expanded else 'TRIA_RIGHT'
        op = row.operator('wm.context_toggle', text='', icon=icon,
                          emboss=False)
        op.data_path = 'mg_group.show_expanded'

        # 名前
        row = title_row.row()
        row.prop(self, 'name', text='Name')

        # 相対 / 絶対
        row = title_row.row()
        row.prop(self, 'use_relative')

        # 削除
        row = title_row.row()
        row.alignment = 'RIGHT'
        op = row.operator('wm.mouse_gesture_stubs',
                          text='', icon='PANEL_CLOSE')
        op.function = 'group_remove'

        # 詳細
        if self.show_expanded:
            row = column.row()
            split = row.split(0.05)
            _col = split.column()
            col = split.column()
            for item in self.gesture_items:
                item.draw(context, col)

            # 追加
            row = col.row()
            row.alignment = 'LEFT'
            op = row.operator('wm.mouse_gesture_stubs', text='Add New',
                              icon='ZOOMIN')
            op.function = 'item_add'


class WM_OT_mouse_gesture_stubs(bpy.types.Operator):
    bl_idname = 'wm.mouse_gesture_stubs'
    bl_label = 'Execute Function'
    bl_description = ''
    bl_options = set()

    function = bpy.props.StringProperty()

    def group_add(self, context):
        prefs = MouseGesturePreferences.get_instance()
        prefs.gesture_groups.add()

    def group_remove(self, context):
        prefs = MouseGesturePreferences.get_instance()
        i = list(prefs.gesture_groups).index(context.mg_group)
        prefs.gesture_groups.remove(i)

    def item_add(self, context):
        context.mg_group.gesture_items.add()

    def item_remove(self, context):
        i = list(context.mg_group.gesture_items).index(context.mg_item)
        context.mg_group.gesture_items.remove(i)

    def arg_unset(self, context):
        context.mg_arg.property_unset(context.mg_arg.name)

    @classmethod
    def groups_unset(cls, context):
        prefs = MouseGesturePreferences.get_instance()
        prefs.property_unset('gesture_groups')

    @classmethod
    def groups_reset(cls, context):
        reset_groups(context)

    def execute(self, context):
        getattr(self, self.function)(context)
        return {'FINISHED'}


class WM_OT_mouse_gesture_search_operator(bpy.types.Operator):
    bl_idname = 'wm.mouse_gesture_search_operator'
    bl_label = ''
    bl_description = ''
    bl_options = {'INTERNAL'}
    bl_property = 'operator'

    data = {}

    operator = bpy.props.EnumProperty(
        name='Operator',
        items=prop_operator_search_items,
    )
    target = bpy.props.StringProperty()

    def execute(self, context):
        prop = self.data[int(self.target)]
        prop.operator = self.operator
        return {'FINISHED'}

    def invoke(self, context, event):
        if hasattr(prop_operator_search_items, 'items'):
            del prop_operator_search_items.items
        context.window_manager.invoke_search_popup(self)
        return {'INTERFACE'}


def prop_from_text_enum(self, context):
    items = []
    for text in bpy.data.texts:
        items.append((text.name, text.name, ''))
    items = tuple(items)
    prop_from_text_enum.items = items
    return items


class WM_OT_mouse_gesture_from_text(bpy.types.Operator):
    bl_idname = 'wm.mouse_gesture_from_text'
    bl_label = 'Paste Text'
    bl_description = ''
    bl_options = {'INTERNAL'}

    text = bpy.props.EnumProperty(
        name='Text',
        items=prop_from_text_enum
    )

    def execute(self, context):
        if self.text in bpy.data.texts:
            context.mg_item.exec_string = '\n'.join(
                [line.body for line in bpy.data.texts[self.text].lines])
        return {'FINISHED'}


class MouseGesturePreferences(
        utils.AddonKeyMapUtility,
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    # 属性確認用
    # BOOL = bpy.props.BoolProperty()
    # BOOL_VECTOR = bpy.props.BoolVectorProperty()
    # INT = bpy.props.IntProperty()
    # INT_VECTOR = bpy.props.IntVectorProperty()
    # FLOAT = bpy.props.FloatProperty()
    # FLOAT_VECTOR = bpy.props.FloatVectorProperty()
    # STRING = bpy.props.StringProperty()
    # ENUM = bpy.props.EnumProperty(items=(('A', 'A', ''),))
    # ENUM_SET = bpy.props.EnumProperty(items=(('A', 'A', ''),),
    #                                   options={'ENUM_FLAG'})

    threshold = bpy.props.IntProperty(
        name='Threshold', default=5, min=1, max=50)

    gesture_groups = bpy.props.CollectionProperty(
        name='Items', type=MouseGestureItemGroup)

    def ensure_operator_args(self):
        for group in self.gesture_groups:
            for item in group.gesture_items:
                ensure_operator_args(item, False)

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""

        column = layout.column()

        row = column.row()
        row.alignment = 'LEFT'
        row.prop(self, 'threshold')

        # グループ
        column.separator()
        row = column.row()
        sub = row.row()
        sub.alignment = 'LEFT'
        sub.label('Groups:')

        # 初期化
        sub = row.row()
        sub.alignment = 'RIGHT'
        op = sub.operator('wm.mouse_gesture_stubs', text='Clear')
        op.function = 'groups_unset'
        op = sub.operator('wm.mouse_gesture_stubs',
                          text='Restore Defaults')
        op.function = 'groups_reset'

        # 一覧
        for group in self.gesture_groups:
            group.draw(context, column)

        # 追加
        row = column.row()
        sub = row.row()
        sub.alignment = 'LEFT'
        op = sub.operator('wm.mouse_gesture_stubs', text='Add New',
                          icon='ZOOMIN')
        op.function = 'group_add'

        super().draw(context, column.column())


###############################################################################
# Operator
###############################################################################
@contextmanager
def window_space(win):
    modelview_mat = bgl.Buffer(bgl.GL_DOUBLE, 16)
    projection_mat = bgl.Buffer(bgl.GL_DOUBLE, 16)
    bgl.glGetDoublev(bgl.GL_MODELVIEW_MATRIX, modelview_mat)
    bgl.glGetDoublev(bgl.GL_PROJECTION_MATRIX, projection_mat)

    matrix_mode = bgl.Buffer(bgl.GL_INT, 1)
    bgl.glGetIntegerv(bgl.GL_MATRIX_MODE, matrix_mode)

    viewport = bgl.Buffer(bgl.GL_INT, 4)
    bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)

    bgl.glViewport(0, 0, win.width, win.height)
    bgl.glMatrixMode(bgl.GL_PROJECTION)
    bgl.glLoadIdentity()
    ofs = -0.01
    bgl.glOrtho(ofs, win.width + ofs, ofs, win.height + ofs, -100, 100)
    bgl.glMatrixMode(bgl.GL_MODELVIEW)
    bgl.glLoadIdentity()
    bgl.glMatrixMode(matrix_mode[0])

    yield

    bgl.glViewport(*viewport)

    bgl.glMatrixMode(bgl.GL_PROJECTION)
    bgl.glLoadMatrixd(projection_mat)
    bgl.glMatrixMode(bgl.GL_MODELVIEW)
    bgl.glLoadMatrixd(modelview_mat)
    bgl.glMatrixMode(matrix_mode[0])

    # PyOpenGLの場合
    # modelview_mat = (ctypes.c_double * 16)()
    # glGetDoublev(GL_MODELVIEW_MATRIX, ctypes.byref(modelview_mat))
    #
    # glMatrixMode()等でパラメーターにGLenumが要求される場合は
    # c_uintでなければならない
    # matrix_mode = ctypes.c_uint()
    # glGetIntegerv(GL_MATRIX_MODE, ctypes.byref(matrix_mode))
    # glMatrixMode(matrix_mode)


def gen_texture():
    textures = bgl.Buffer(bgl.GL_INT, 1)
    bgl.glGenTextures(1, textures)
    tex = textures[0]
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, tex)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER,
                        bgl.GL_LINEAR)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER,
                        bgl.GL_LINEAR)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
    return tex


def gen_screenshot_texture(x, y, w, h, mode=None):
    scissor_is_enabled = bgl.Buffer(bgl.GL_BYTE, 1)
    bgl.glGetIntegerv(bgl.GL_SCISSOR_TEST, scissor_is_enabled)
    scissor_box = bgl.Buffer(bgl.GL_INT, 4)
    bgl.glGetIntegerv(bgl.GL_SCISSOR_BOX, scissor_box)
    bgl.glEnable(bgl.GL_SCISSOR_TEST)
    bgl.glScissor(x, y, w, h)

    mode_bak = bgl.Buffer(bgl.GL_INT, 1)
    bgl.glGetIntegerv(bgl.GL_READ_BUFFER, mode_bak)
    if mode is not None:
        bgl.glReadBuffer(mode)

    pixels = bgl.Buffer(bgl.GL_BYTE, 4 * w * h)
    # RGBAにしないと斜めになる
    # GL_UNSIGNED_BYTEでないと色が僅かにずれる
    bgl.glReadPixels(x, y, w, h, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, pixels)
    bgl.glFinish()

    if mode is not None:
        bgl.glReadBuffer(mode_bak[0])

    # 反転。確認用
    # for i in range(4 * w * h):
    #     if (i % 4) != 3:
    #         pixels[i] = 255 - pixels[i]

    tex = gen_texture()
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, tex)
    bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA, w, h, 0, bgl.GL_RGBA,
                     bgl.GL_UNSIGNED_BYTE, pixels)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

    if not scissor_is_enabled[0]:
        bgl.glDisable(bgl.GL_SCISSOR_TEST)
    bgl.glScissor(*scissor_box)

    return tex


def draw_texture(x, y, w, h, texture, mode=None):
    mode_bak = bgl.Buffer(bgl.GL_INT, 1)
    bgl.glGetIntegerv(bgl.GL_DRAW_BUFFER, mode_bak)
    if mode is not None:
        bgl.glDrawBuffer(mode)

    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture)

    bgl.glColor4d(1.0, 1.0, 1.0, 1.0)
    bgl.glBegin(bgl.GL_TRIANGLE_FAN)
    bgl.glTexCoord2d(0.0, 0.0)
    bgl.glVertex2i(x, y)
    bgl.glTexCoord2d(1.0, 0.0)
    bgl.glVertex2i(x + w, y)
    bgl.glTexCoord2d(1.0, 1.0)
    bgl.glVertex2i(x + w, y + h)
    bgl.glTexCoord2d(0.0, 1.0)
    bgl.glVertex2i(x, y + h)
    bgl.glEnd()

    bgl.glDisable(bgl.GL_TEXTURE_2D)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

    if mode is not None:
        bgl.glDrawBuffer(mode_bak[0])


def region_is_overlap(context, area, region):
    if context.user_preferences.system.use_region_overlap:
        if 'WM_is_draw_triple(context.window)':
            if area.type in {'VIEW_3D', 'SEQUENCE_EDITOR'}:
                if region.type in {'TOOLS', 'UI', 'TOOL_PROPS'}:
                    return True
            elif area.type == 'IMAGE_EDITOR':
                if region.type in {'TOOLS', 'UI', 'TOOL_PROPS', 'PREVIEW'}:
                    return True
    return False


def prop_group_enum_items(self, context):
    prefs = MouseGesturePreferences.get_instance()
    items = []
    for group in prefs.gesture_groups:
        if group.name:
            items.append((group.name, group.name, ''))
    prop_group_enum_items.items = items
    return items


class WM_OT_mouse_gesture(bpy.types.Operator):
    bl_description = 'Mouse Gesture'
    bl_idname = 'wm.mouse_gesture'
    bl_label = 'Mouse Gesture'
    bl_options = {'INTERNAL'}
    # bl_options = {'REGISTER', 'UNDO'}

    group = bpy.props.EnumProperty(
        name='Group',
        items=prop_group_enum_items,
    )

    @classmethod
    def poll(cls, context):
        return context.area

    def __init__(self):
        self.use_texture = False
        self.handle = None
        self.handle_area = None
        self.handle_region = None
        self.area = None
        self.region = None
        self.gesture_abs = ''
        self.gesture_rel = ''
        self.item = None
        self.op_running_modal = False
        self.mco = Vector((0, 0))
        self.coords = []
        self.invoke_event_type = ''
        self.texture_back = None

    def region_drawing_rectangle(self, context, area, region):
        """※ regionrulerからコピペ。
        'WINDOW'の描画範囲を表すregion座標を返す。
        RegionOverlapが有効な場合の範囲は 'WINDOW' から 'TOOLS'('TOOL_PROPS'),
        'UI' を除外したものになる。
        :return (xmin, ymin, xmax, ymax)
        :rtype (int, int, int, int)
        """

        ymin = 0
        ymax = region.height - 1

        # render info
        if context.area.type == 'IMAGE_EDITOR':
            image = context.area.spaces.active.image
            if image and image.type == 'RENDER_RESULT':
                dpi = context.user_preferences.system.dpi
                ymax -= int((PIXEL_SIZE * dpi * 20 + 36) / 72)  # # widget_unit

        if not context.user_preferences.system.use_region_overlap:
            return 0, ymin, region.width - 1, ymax

        # Regionが非表示ならidが0。
        # その際、通常はwidth若しくはheightが1になっている。
        # TOOLSが非表示なのにTOOL_PROPSのみ表示される事は無い
        window = tools = tool_props = ui = None
        for ar in area.regions:
            if ar.id != 0:
                if ar.type == 'WINDOW':
                    window = ar
                elif ar.type == 'TOOLS':
                    tools = ar
                elif ar.type == 'TOOL_PROPS':
                    tool_props = ar
                elif ar.type == 'UI':
                    ui = ar

        xmin = region.x
        xmax = xmin + window.width - 1
        left_width = right_width = 0
        if tools and ui:
            r1, r2 = sorted([tools, ui], key=lambda ar: ar.x)
            if r1.x == area.x:
                # 両方左
                if r2.x == r1.x + r1.width:
                    left_width = r1.width + r2.width
                # 片方ずつ
                else:
                    left_width = r1.width
                    right_width = r2.width
            # 両方右
            else:
                right_width = r1.width + r2.width
        elif tools:
            if tools.x == area.x:
                left_width = tools.width
            else:
                right_width = tools.width
        elif ui:
            if ui.x == area.x:
                left_width = ui.width
            else:
                right_width = ui.width

        xmin = max(xmin, area.x + left_width) - region.x
        xmax = min(xmax, area.x + area.width - right_width - 1) - region.x
        return xmin, ymin, xmax, ymax

    def draw_callback_px(self, context):
        use_texture = self.use_texture
        if not use_texture:
            if context.region != self.region:
                return

        U = context.user_preferences
        prefs = MouseGesturePreferences.get_instance()
        dpi = U.system.dpi
        widget_unit = int((PIXEL_SIZE * dpi * 20 + 36) / 72)

        font_id = 0
        theme_style = U.ui_styles[0]
        blf.size(font_id, theme_style.widget.points, dpi)
        bgl.glEnable(bgl.GL_BLEND)

        bgl.glColor3f(*U.themes['Default'].view_3d.space.text_hi)

        win = context.window
        w, h = win.width, win.height

        if use_texture:
            bgl.glDisable(bgl.GL_SCISSOR_TEST)

        with window_space(win):
            if use_texture:
                draw_texture(0, 0, w, h, self.texture_back)

            # draw origin
            coords = self.coords + [self.mco]
            bgl.glLineWidth(2)
            r1 = prefs.threshold
            r2 = r1 + 5
            x, y = coords[0]
            bgl.glBegin(bgl.GL_LINES)
            for i in range(4):
                a = math.pi / 2 * i + math.pi / 4
                bgl.glVertex2f(x + r1 * math.cos(a),
                               y + r1 * math.sin(a))
                bgl.glVertex2f(x + r2 * math.cos(a),
                               y + r2 * math.sin(a))
            bgl.glEnd()
            bgl.glLineWidth(1)

            # draw lines
            bgl.glEnable(bgl.GL_LINE_STIPPLE)
            bgl.glLineStipple(1, int(0b101010101010101))  # (factor, pattern)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for v in coords:
                bgl.glVertex2f(v[0], v[1])
            bgl.glEnd()
            bgl.glLineStipple(1, 1)
            bgl.glDisable(bgl.GL_LINE_STIPPLE)

        if use_texture:
            bgl.glEnable(bgl.GL_SCISSOR_TEST)

        # draw txt

        xmin, ymin, xmax, ymax = self.region_drawing_rectangle(
            context, self.area, self.region)
        xmin += self.region.x
        ymin += self.region.y
        xmax += self.region.x
        ymax += self.region.y

        if self.area.type == 'VIEW_3D':
            if U.view.show_mini_axis:
                # view3d_draw.c: 1019: draw_selected_name()
                posx = xmin + widget_unit + U.view.mini_axis_size * 2
            else:
                # view3d_draw.c: 928: draw_selected_name()
                posx = xmin + 1.5 * widget_unit
            posy = ymin + widget_unit * 1.5
        else:
            posx = xmin + widget_unit * 0.5
            posy = ymin + widget_unit * 0.5
        char_space = 5

        group = prefs.gesture_groups.get(self.group)
        use_relative = group and group.use_relative
        gesture = self.gesture_rel if use_relative else self.gesture_abs
        # 文字はregionに収まるように（はみ出すと見た目が悪いから）
        scissor_box = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_SCISSOR_BOX, scissor_box)
        bgl.glScissor(xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)
        with window_space(win):
            if gesture:
                x = posx
                for txt in gesture:
                    blf.position(font_id, x, posy, 0)
                    blf.draw(font_id, txt)
                    text_width, text_height = blf.dimensions(font_id, txt)
                    x += text_width + char_space
            if self.item:
                blf.position(font_id, posx, posy + widget_unit, 0)
                blf.draw(font_id, self.item.name)
        bgl.glScissor(*scissor_box)

        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def vecs_direction(self, vec1, vec2):
        # vec1はUp方向
        def vecs_angle(vec1, vec2):
            """反時計回りを正とした角度を返す。"""
            def cross2d(v1, v2):
                return v1[0] * v2[1] - v1[1] * v2[0]
            angle = vec1.angle(vec2)
            if cross2d(vec1, vec2) < 0:
                angle = -angle
            return angle
        angle = vecs_angle(vec1, vec2)
        angle = math.atan2(math.sin(angle), math.cos(angle))
        pi4 = math.pi / 4
        if -pi4 <= angle < pi4:
            return 'U'
        elif pi4 <= angle < pi4 * 3:
            return 'L'
        elif -pi4 * 3 <= angle < -pi4:
            return 'R'
        else:
            return 'D'

    def update_item(self, context):
        prefs = MouseGesturePreferences.get_instance()

        self.item = None
        group = prefs.gesture_groups.get(self.group)
        if group:
            if group.use_relative:
                current_gesture = self.gesture_rel
            else:
                current_gesture = self.gesture_abs
            for item in group.gesture_items:
                for gesture in item.gesture.split(','):
                    gesture = gesture.strip()
                    if fnmatch.fnmatch(current_gesture, gesture):
                        self.item = item
                        return

    def coords_append(self, event, mco=None):
        prefs = MouseGesturePreferences.get_instance()
        if mco is None:
            mco = Vector((event.mouse_x, event.mouse_y))
        mco_rel = mco - self.coords[-1]

        if mco_rel.length >= prefs.threshold:
            # relative (先頭の二つが基準)
            if len(self.coords) == 1:
                direction = 'U'
            else:
                vec0 = self.coords[1] - self.coords[0]
                direction = self.vecs_direction(vec0, mco_rel)
            if not self.gesture_rel or self.gesture_rel[-1] != direction:
                self.gesture_rel += direction

            # absolute
            direction = self.vecs_direction(Vector((0, 1)), mco_rel)
            if not self.gesture_abs or self.gesture_abs[-1] != direction:
                self.gesture_abs += direction

            self.coords.append(mco)
            return True
        else:
            return False

    def draw_handler_add(self, context):
        if self.use_texture:
            area = region = None
            if context.user_preferences.system.window_draw_method == 'FULL':
                for sa in context.screen.areas:
                    for ar in sa.regions:
                        if ar.id != 0:
                            area = sa
                            region = ar
            else:
                for sa in context.screen.areas:
                    for ar in sa.regions:
                        if ar.id != 0 and region_is_overlap(context, sa, ar):
                            area = sa
                            region = ar
                if not region:
                    area = context.area
                    ar_window = None
                    for ar in area.regions:
                        if ar.id != 0:
                            if ar.type == 'WINDOW':
                                ar_window = ar
                            else:
                                region = ar
                                break
                    else:
                        region = ar_window
        else:
            area = context.area
            region = context.region
        self.handle = area.spaces.active.draw_handler_add(
            self.draw_callback_px, (context,), region.type, 'POST_PIXEL')
        self.handle_area = area
        self.handle_region = region

    def draw_handler_remove(self):
        self.handle_area.spaces.active.draw_handler_remove(
            self.handle, self.handle_region.type)

    def redraw_all(self, context):
        for area in context.screen.areas:
            area.tag_redraw()

    def gen_textures(self, context):
        if self.use_texture:
            win = context.window
            w, h = win.width, win.height
            self.texture_back = gen_screenshot_texture(0, 0, w, h)

    def delete_textures(self):
        if self.use_texture:
            buf = bgl.Buffer(bgl.GL_INT, 1, [self.texture_back])
            bgl.glDeleteTextures(1, buf)

    def modal(self, context, event):
        U = context.user_preferences

        if (event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE') and
                event.mouse_x == event.mouse_prev_x and
                event.mouse_y == event.mouse_prev_y):
            return {'RUNNING_MODAL'}

        self.mco = Vector((event.mouse_x, event.mouse_y))

        if self.op_running_modal:
            # for 'Continuous Grab'
            return {'FINISHED'}

        if (event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE') and
                self.coords_append(event)):
            self.update_item(context)

        # Cancel
        elif (event.type == 'ESC' or event.type == 'RIGHTMOUSE' and
                event.value == 'PRESS' and
                self.invoke_event_type != 'RIGHTMOUSE'):
            self.draw_handler_remove()
            self.redraw_all(context)
            self.delete_textures()
            return {'CANCELLED'}

        # Execute
        elif ((event.type in ('RET', 'NUMPAD_ENTER', 'SPACE') or
               event.type == self.invoke_event_type) and
              event.value == 'RELEASE'):
            self.draw_handler_remove()
            self.redraw_all(context)
            self.delete_textures()

            if self.item:
                if self.item.type == 'STRING' and self.item.exec_string:
                    lines = ['def func(context):']
                    for line in self.item.exec_string.split('\n'):
                        lines.append('    ' + line)
                    d = {}
                    x = '\n'.join(lines)
                    exec(x, {'bpy': bpy}, d)
                    retval = d['func'](context)
                    if (isinstance(retval, set) and
                            'RUNNING_MODAL' in retval and
                            U.inputs.use_mouse_continuous):
                        self.op_running_modal = True
                        return {'RUNNING_MODAL'}
                elif self.item.type == 'OPERATOR':
                    operator = get_operator(self.item.operator)
                    args = [self.item.operator_execution_context]
                    # if self.item.is_property_set('operator_undo'):
                    args.append(self.item.operator_undo)
                    kwargs = {}
                    for arg in self.item.operator_args:
                        n = arg.name.split('__')[-1]
                        if arg.is_property_set(arg.name):
                            kwargs[n] = getattr(arg, arg.name)
                    retval = operator(*args, **kwargs)
                    if 'RUNNING_MODAL' in retval:
                        # {'FINISHED'}を返すとContinuousGrabが無効化される
                        self.op_running_modal = True
                        return retval
                return {'FINISHED'}
            else:
                return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            self.handle_region.tag_redraw()

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        U = context.user_preferences
        prefs = MouseGesturePreferences.get_instance()
        if not self.group or self.group not in prefs.gesture_groups:
            return {'CANCELLED'}

        # 'FULL'だと全regionを再描画する為、除外する
        self.use_texture = not context.screen.is_animation_playing
        if '.' in __name__:
            try:
                if context.space_data.drawnearest.enable:
                    # テクスチャが真っ黒になるので無効化
                    self.use_texture = False
            except:
                pass

        self.gen_textures(context)

        context.window_manager.modal_handler_add(self)
        self.draw_handler_add(context)
        self.area = context.area
        self.region = context.region
        self.mco = Vector((event.mouse_x, event.mouse_y))
        self.coords = [self.mco]

        if event.type.startswith('EVT_TWEAK_'):
            if event.type == 'EVT_TWEAK_L':
                self.invoke_event_type = 'LEFTMOUSE'
            elif event.type == 'EVT_TWEAK_M':
                self.invoke_event_type = 'MIDDLEMOUSE'
            elif event.type == 'EVT_TWEAK_R':
                self.invoke_event_type = 'RIGHTMOUSE'
            elif event.type == 'EVT_TWEAK_A':
                if U.inputs.select_mouse == 'RIGHT':
                    self.invoke_event_type = 'LEFTMOUSE'
                else:
                    self.invoke_event_type = 'RIGHTMOUSE'
            elif event.type == 'EVT_TWEAK_S':
                if U.inputs.select_mouse == 'RIGHT':
                    self.invoke_event_type = 'RIGHTMOUSE'
                else:
                    self.invoke_event_type = 'LEFTMOUSE'
        else:
            self.invoke_event_type = event.type

        # prefs.ensure_operator_args()

        self.handle_region.tag_redraw()

        return {'RUNNING_MODAL'}


###############################################################################
# Register
###############################################################################
classes = [
    MouseGestureOpArg,
    MouseGestureItem,
    MouseGestureItemGroup,
    MouseGesturePreferences,
    WM_OT_mouse_gesture_stubs,
    WM_OT_mouse_gesture_search_operator,
    WM_OT_mouse_gesture_from_text,
    WM_OT_mouse_gesture,
]


changed_key_map_items = []
addon_keymaps = []
blender_keymaps = []


@bpy.app.handlers.persistent
def scene_update_pre(scene):
    """起動後に一度だけ実行"""
    kc = bpy.context.window_manager.keyconfigs['Blender']
    if kc:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in km.keymap_items:
                if kmi.idname in ('view3d.cursor3d',
                                  'view3d.cursor3d_restrict'):
                    if kmi.type == 'ACTIONMOUSE' and kmi.value == 'PRESS':
                        kmi.value = 'CLICK'
                        blender_keymaps.append((km, kmi))
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)


@bpy.app.handlers.persistent
def load_handler(dummy):
    prefs = MouseGesturePreferences.get_instance()
    prefs.ensure_operator_args()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = MouseGesturePreferences.get_instance()
    if not prefs.is_property_set('gesture_groups'):
        reset_groups(bpy.context)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new('3D View', space_type='VIEW_3D',
                            region_type='WINDOW', modal=False)
        if _RELEASE:
            kmi = km.keymap_items.new('wm.mouse_gesture', 'EVT_TWEAK_A', 'ANY',
                                      head=True)
            kmi.properties.group = 'View'
            addon_keymaps.append((km, kmi))
        else:
            kmi = km.keymap_items.new('wm.mouse_gesture', 'EVT_TWEAK_A', 'ANY',
                                      shift=True, head=True)
            kmi.properties.group = 'Transform: Scale'
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new('wm.mouse_gesture', 'EVT_TWEAK_A', 'ANY',
                                      head=True)
            kmi.properties.group = 'Mesh Select Mode'
            addon_keymaps.append((km, kmi))

        addon_prefs = MouseGesturePreferences.get_instance()
        """:type: MouseGesturePreferences"""
        addon_prefs.register_keymap_items(addon_keymaps)

    bpy.app.handlers.scene_update_pre.append(scene_update_pre)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    addon_prefs = MouseGesturePreferences.get_instance()
    """:type: MouseGesturePreferences"""
    addon_prefs.unregister_keymap_items()

    for km, kmi in blender_keymaps:
        kmi.value = 'PRESS'
    blender_keymaps.clear()

    for km, kmi in changed_key_map_items:
        try:
            if kmi.type == 'ACTIONMOUSE' and kmi.value == 'RELEASE':
                kmi.vaule = 'PRESS'
        except:
            pass
    changed_key_map_items.clear()

    if scene_update_pre in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    bpy.app.handlers.load_post.remove(load_handler)

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
