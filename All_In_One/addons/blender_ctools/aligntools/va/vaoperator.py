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


import bpy

from . import vaprops as vap


WM_OT_exec_func = None


###############################################################################
# Template
###############################################################################
class Registerable:
    @classmethod
    def register_class(cls, rename=False):
        import re
        if issubclass(cls, bpy.types.Operator):
            mod, func = cls.bl_idname.split('.')
            class_name = mod.upper() + '_OT_' + func
        elif issubclass(cls, bpy.types.Menu):
            class_name = cls.bl_idname
        else:
            class_name = cls.__name__
        if rename:
            if cls._users == 0 or not hasattr(bpy.types, class_name):
                while hasattr(bpy.types, class_name):
                    base, num = re.match('([a-zA-Z_]+)(\d*)$', func).groups()
                    if num == '':
                        func = base + '0'
                    else:
                        func = base + str(int(num) + 1)
                    class_name = mod.upper() + '_OT_' + func
                cls.bl_idname = mod + '.' + func
                bpy.utils.register_class(cls)
                cls._users = 1
            else:
                print('{} already registered'.format(cls))
        else:
            if hasattr(bpy.types, class_name):
                getattr(bpy.types, class_name)._users += 1
            else:
                bpy.utils.register_class(cls)
                cls._users = 1

    @classmethod
    def unregister_class(cls, force=False):
        if issubclass(cls, bpy.types.Operator):
            mod, func = cls.bl_idname.split('.')
            class_name = mod.upper() + '_OT_' + func
        elif issubclass(cls, bpy.types.Menu):
            class_name = cls.bl_idname
        else:
            class_name = cls.__name__
        if hasattr(bpy.types, class_name):
            other_cls = getattr(bpy.types, class_name)
            if other_cls._users > 0:
                other_cls._users -= 1
            if force:
                other_cls._users = 0
            if other_cls._users == 0:
                bpy.utils.unregister_class(other_cls)
        else:
            bpy.utils.unregister_class(cls)  # 例外を出させるため


class OperatorTemplate(Registerable):
    bl_idname = ''
    bl_label = ''
    bl_description = ''
    bl_options = {'REGISTER'}  # {'REGISTER', 'UNDO'}

    _users = 0

    @classmethod
    def call(cls, *args, **kwargs):
        mod, func = cls.bl_idname.split('.')
        op = getattr(getattr(bpy.ops, mod), func)
        return op(*args, **kwargs)

    def get_property(self, attr):
        """rna_typeを参照し、プロパティを返す
        :type attr: str
        :return: T
        """
        # NOTE:
        # Operatorのインスタンスの場合
        #     properties = self.properties.bl_rna.properties
        #     properties == self.rna_type.properties
        # Object等のインスタンスの場合
        #     properties = self.bl_rna.properties
        #     properties == self.rna_type.properties

        properties = self.rna_type.properties
        # return properties[attr] if attr in properties else None
        # ↑コメントアウト。キーが無ければ例外を発生させる
        return properties[attr]

    def draw_property(self, attr, layout, text=None, skip_hidden=True,
                      row=False, **kwargs):
        """オペレータ実行時のプロパティ表示を再現する。

        クラスからこのメソッドを実行する際に別オブジェクトのインスタンスを
        第一引数に渡す事でそのプロパティを描画するという使い方も可。

        :type attr: str
        :type layout: bpy.types.UILayout
        :type text: str
        :type skip_hidden: bool
        :type row: bool
        :rtype: bpy.types.UILayout
        """
        if attr == 'rna_type':
            return None

        # prop = self.get_property(attr)
        properties = self.rna_type.properties
        prop = properties[attr] if attr in properties else None

        if skip_hidden and prop.is_hidden:
            return None

        col = layout.column(align=True)
        sub = col.row()
        name = prop.name if text is None else text
        if prop.type == 'BOOLEAN' and prop.array_length == 0:
            sub.prop(self, attr, text=name, **kwargs)
        else:
            if name:
                sub.label(name + ':')
            sub = col.row() if row else col.column()
            if prop.type == 'ENUM' and \
                    (prop.is_enum_flag or 'expand' in kwargs):
                sub.prop(self, attr, **kwargs)  # text='' だとボタン名が消える為
            else:
                sub.prop(self, attr, text='', **kwargs)

        return col

    def draw_all(self, context, layout=None):
        """Draw all properties
        :rtype: dict[str, bpy.types.UILayout]
        """
        columns = {}
        if layout is None:
            layout = self.layout
        for attr in self.properties.rna_type.properties.keys():
            columns[attr] = self.draw_property(attr, layout)
        return columns

    def as_keywords(self, ignore=(), skip_hidden=False, use_list=False):
        """Return a copy of the properties as a dictionary.

        Use collections.OrderedDict instead of dict.
        (original: blender/release/scripts/modules/bpy_types.py:600)

        :type ignore: abc.Iterable
        :type skip_hidden: bool
        :param use_list: Vector, Matrix 等をlistへ変換する
        :type use_list: True
        :rtype: OrderedDict
        """
        from collections import OrderedDict
        import itertools
        from mathutils import Color, Euler, Matrix, Quaternion, Vector
        ignore = tuple(ignore) + ('rna_type',)
        r_dict = OrderedDict()
        for attr, prop in self.properties.rna_type.properties.items():
            if attr not in ignore and not (skip_hidden and prop.is_hidden):
                value = getattr(self, attr)
                if use_list:
                    if isinstance(value, (Color, Euler, Quaternion, Vector)):
                        value = list(value)
                    elif isinstance(value, Matrix):
                        value = list(itertools.chain.from_iterable(value.col))
                r_dict[attr] = value
        return r_dict

    def as_keywords_default(self, ignore=(), skip_hidden=False):
        """as_keywordsメソッドの亜種。現在の値の代わりにデフォルト値を返す。
        :type ignore: abc.Iterable
        :type skip_hidden: bool
        :rtype: OrderedDict
        """
        import collections.abc
        default_values = collections.OrderedDict()
        ignore = tuple(ignore) + ('rna_type',)
        for name, prop in self.properties.rna_type.properties.items():
            if name in ignore or skip_hidden and prop.is_hidden:
                continue
            default = None
            if prop.type == 'POINTER':
                pass
            elif prop.type == 'COLLECTION':
                pass
            elif prop.type == 'ENUM':
                py_prop = getattr(self.__class__, name)
                func, kwargs = py_prop
                if isinstance(kwargs['items'], collections.abc.Callable):
                    if prop.is_enum_flag:
                        default = set()
                    else:
                        items = list(kwargs['items'](self, bpy.context))
                        if items:
                            if len(items[0]) == 5:
                                items.sort(key=lambda x: x[-1])
                            default = items[0][0]
                else:
                    if prop.is_enum_flag:
                        default = set(prop.default_flag)
                    else:
                        default = prop.default
            elif prop.type in {'BOOLEAN', 'FLOAT', 'INT'}:
                if prop.is_array:
                    default = list(prop.default_array)
                else:
                    default = prop.default
            elif prop.type == 'STRING':
                default = prop.default
            default_values[name] = default
        return default_values


# NOTE:
# execute()中でのself.propertiesはプロパティのget,set,update関数の引数の
# selfと等しい <bpy_struct>


###############################################################################
# Execute String
###############################################################################
class WM_OT_exec_string(bpy.types.Operator):
    """文字列でexec()を実行する"""
    bl_description = 'exec(str)'
    bl_idname = 'wm.exec_string'
    bl_label = 'Exec String'
    bl_options = {'REGISTER', 'UNDO'}

    def prop_string(name='Exec String', description=''):
        return vap.SP(name, description, options={'HIDDEN'})
    string = prop_string()
    shiftstring = prop_string()
    ctrlstring = prop_string()
    altstring = prop_string()
    redraw = vap.BP('Redraw', default=False, options={'HIDDEN'})
    del prop_string

    def __init__(self):
        self.current_string = None

    def execute(self, context):
        def func(context, event):
            exec(self.string, globals(), locals())

        if self.current_string:
            exec_func(func, use_event=True)
            if self.redraw:
                context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.shift and self.shiftstring:
            self.current_string = self.shiftstring
        elif event.ctrl and self.ctrlstring:
            self.current_string = self.ctrlstring
        elif event.alt and self.altstring:
            self.current_string = self.altstring
        else:
            self.current_string = self.string
        return self.execute(context)


class WM_OT_exec(OperatorTemplate, bpy.types.Operator):
    """execute string.

    # register instead of 'bpy.utils.register_class(WM_OT_exec)'
    >>> WM_OT_exec.register_class()

    # execute
    >>> bpy.ops.wm.exec(code='print("hoge")')
    hoge

    >>> WM_OT_exec.call(code='print("hoge")')
    hoge

    # execute function
    >>> bpy.ops.wm.exec(
            code="def func(vec):\n"
                 "    print(Vector([4, 0, 0]) + vec)\n"
                 "    return {'FINISHED'}",
            func_name='func',
            func_args='Vector([1, 2, 3])',
            setup='from mathutils import Vector',
            )
    <Vector (5.0000, 2.0000, 3.0000)>

    # unregister instead of 'bpy.utils.unregister_class(WM_OT_exec)'
    >>> WM_OT_exec.unregister_class()
    """

    # 他のファイルで定義されたクラスとbl_idnameが衝突した場合に変更する
    # 'wm.exec' -> 'wm.exec0' -> 'wm.exec1' -> ...
    RENAME = False

    # func_argsに丸括弧を含めるか否か。 True:'(arg1, arg2)', False:'arg1, arg2'
    WITH_PARENTHESES = False

    bl_idname = 'wm.exec'
    bl_label = 'Execute String'
    bl_description = 'exec()'

    # exec()に渡す文字列
    code = bpy.props.StringProperty(options={'SKIP_SAVE'})

    # 文字列の先頭に挿入してimportやglobal変数を設定する。
    # codeを実行する時とfunc_argsで引数を取得する時に使用する。
    setup = bpy.props.StringProperty(options={'SKIP_SAVE'})

    # 指定したモジュール、クラス等をvars()に渡し、その返り値で
    # global変数を上書きする
    namespace = bpy.props.StringProperty(options={'SKIP_SAVE'})

    # 関数名、引数を指定する
    func_name = bpy.props.StringProperty(options={'SKIP_SAVE'})
    func_args = bpy.props.StringProperty(
        description="with '(' and ')'" if WITH_PARENTHESES else '',
        options={'SKIP_SAVE'})

    @classmethod
    def call(cls, *args, **kwargs):
        mod, func = cls.bl_idname.split('.')
        op = getattr(getattr(bpy.ops, mod), func)
        return op(*args, **kwargs)

    def _make_globals(self):
        import importlib

        namespace = {
            'bpy': bpy,
            'context': bpy.context,
            'C': bpy.context,
            'D': bpy.data,
        }

        if self.namespace:
            # try:
            #     mod = importlib.import_module(self.namespace)
            #     namespace.update(vars(mod))
            # except ImportError:
            #     if '.' in self.namespace:
            #         ls = self.namespace.split('.')
            #         mod = importlib.import_module('.'.join(ls[:-1]))
            #         obj = getattr(mod, ls[-1])
            #         namespace.update(vars(obj))
            #     else:
            #         raise
            mod = importlib.import_module(self.namespace)
            namespace.update(vars(mod))

        return namespace

    def _get_args(self):
        if not self.func_args:
            return (), {}
        code = '\n'.join(
            ['def __func(*args, **kwargs):',
             '    return args, kwargs',
             '__result = __func{}',
             ])
        args = self.func_args
        if not self.WITH_PARENTHESES:
            args = '(' + args + ')'
        code = code.format(args)
        if self.setup:
            code = self.setup.rstrip() + '\n' + code
        global_dict = self._make_globals()
        try:
            exec(code, global_dict)
        except:
            print('Arguments:')
            print(self.func_args + '\n')
            raise
        return global_dict['__result']

    def execute(self, context):
        global_dict = self._make_globals()
        code = self.code.rstrip() + '\n'
        if self.setup:
            code = self.setup.rstrip() + '\n' + code
        try:
            exec(code, global_dict)
        except:
            print('Code:')
            print(code)
            raise

        if (self.properties.is_property_set('func_name') and
                self.func_name):
            func = global_dict.get(self.func_name)
            if not func:
                msg = "function '{}' not found".format(self.func_name)
                raise ValueError(msg)

            args, kwargs = self._get_args()

            try:
                r = func(*args, **kwargs)
                if r is None:
                    r = {'FINISHED'}
                return r
            except:
                print('Code:')
                print(code)
                if self.func_args:
                    args = self.func_args
                    if not self.WITH_PARENTHESES:
                        args = '(' + args + ')'
                    print('Call:')
                    print(self.func_name + args + '\n')
                raise

        return {'FINISHED'}


###############################################################################
# Execute Function
###############################################################################
def generate_operator(name='WM_OT_mod_function', bases=(), namespace=None):
    base_name = name
    mod, func = base_name.split('_OT_')
    bl_idname = bl_idname_base = mod.lower() + '.' + func
    i = 1
    while hasattr(bpy.types, name):
        name = base_name + str(i)
        bl_idname = bl_idname_base + str(i)
        i += 1
    namespace_dict = {
        'bl_idname': bl_idname,
    }
    if namespace:
        namespace_dict.update(namespace)
    return type(name, bases, namespace_dict)


class _WM_OT_exec_func_base:
    bl_description = ''
    bl_idname = 'wm.exec_func_base'
    bl_label = 'Exec Function'
    bl_options = {'INTERNAL'}

    _function_data = {}
    _results = []

    def invoke(self, context, event):
        data = self.__class__._function_data
        if not data:
            return {'CANCELLED'}

        function = data['function']
        args = data['args']
        kwargs = data['kwargs']
        context_dict = data['context_dict']
        use_event = data['use_event']

        pre_args = [context]
        if use_event:
            pre_args.append(event)
        if context_dict is not None:
            pre_args.append(context_dict)

        result = function(*(pre_args + list(args)), **kwargs)
        self.__class__._results.append(result)
        return {'CANCELLED'}

    @classmethod
    def set_function(cls, function, args=None, kwargs=None,
                     context_dict=None, use_event=False):
        cls._function_data['function'] = function
        cls._function_data['args'] = args or ()
        cls._function_data['kwargs'] = kwargs or {}
        cls._function_data['context_dict'] = context_dict
        cls._function_data['use_event'] = use_event

    @classmethod
    def get_result(cls):
        return cls._results.pop()


def generate_WM_OT_exec_func():
    namespace = {
        '_function_data': {
            'function': None,
            'args': (),
            'kwargs': {},
            'use_event': False,
            'context_dict': None,
            },
        '_results': []
    }
    cls = generate_operator(
        'WM_OT_exec_func', (_WM_OT_exec_func_base, bpy.types.Operator),
        namespace)
    return cls


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


def exec_func(function, args=None, kwargs=None, override_context=None,
              use_event=False, use_context_dict=False, scene_update=True):
    """contextの属性を上書きした状態で関数を実行、
    function(context, *args, **kwargs)の結果を返す。
    :param function: 呼び出す関数
    :type function: types.FunctionType
    :param args: 関数に渡す可変長引数
    :type args: list | tuple
    :param kwargs: 関数に渡すキーワード引数
    :type kwargs: dict
    :param override_context: bpy.ops.***.***(override_context)
    :type override_context: dict
    :param use_event: 真ならfunction(context, event, ...) となる
    :type use_event: bool
    :param use_context_dict: 真ならfunction(context, context_dict, ...)、
        use_eventが真の場合はfunction(context, event, context_dict, ...)となる
    :type use_context_dict: bool
    :param scene_update: オペレータ実行前と後にはScene.update()が呼ばれるが
        偽を指定する事でこれを抑制する。scene_update_pre(post)_handlerの中で
        実行する場合に偽を指定する必要がある。
    :type _scene_update: bool
    """
    global WM_OT_exec_func
    if not WM_OT_exec_func:
        WM_OT_exec_func = generate_WM_OT_exec_func()
        bpy.utils.register_class(WM_OT_exec_func)

    cls = WM_OT_exec_func
    d = override_context if use_context_dict else None
    cls.set_function(function, args, kwargs, d, use_event)

    # invoke()
    mod, func = cls.bl_idname.split('.')
    op = getattr(getattr(bpy.ops, mod), func)
    if override_context:
        op_args = [override_context, 'INVOKE_DEFAULT']
    else:
        op_args = ['INVOKE_DEFAULT']
    operator_call(op, *op_args, _scene_update=scene_update)
    return cls.get_result()


###############################################################################
# Register
###############################################################################
def _get_registerd(cls):
    if cls:
        name = cls.__name__
        if hasattr(bpy.types, name):
            return getattr(bpy.types, name)


def register_exec_func():
    global WM_OT_exec_func
    if not WM_OT_exec_func:
        WM_OT_exec_func = generate_WM_OT_exec_func()
    cls = _get_registerd(WM_OT_exec_func)
    if not cls:
        bpy.utils.register_class(WM_OT_exec_func)
    elif cls != WM_OT_exec_func:
        raise TypeError('違う型が登録済み')


def unregister_exec_func():
    global WM_OT_exec_func
    cls = _get_registerd(WM_OT_exec_func)
    if cls != WM_OT_exec_func:
        raise TypeError('違う型が登録済み')
    else:
        bpy.utils.unregister_class(WM_OT_exec_func)
    WM_OT_exec_func = None


classes = [
    WM_OT_exec_string,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # register_exec_func()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # unregister_exec_func()


register()
