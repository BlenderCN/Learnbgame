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


from functools import wraps as _wraps
import pickle as _pickle
import shelve as _shelve
import inspect as _inspect
import logging as _logging

import bpy as _bpy


_logger = _logging.getLogger(__name__)
# logger.setLevel(_logging.ERROR)
_logger.setLevel(_logging.INFO)
_handler = _logging.StreamHandler()
_handler.setLevel(_logging.NOTSET)
_formatter = _logging.Formatter(
    '[%(levelname)s: %(name)s.%(funcName)s()]: %(message)s')
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)


INT_MIN = -2 ** (4 * 8 - 1)  # -2147483648
INT_MAX = 2 ** (4 * 8 - 1) - 1  # 2147483647
FLT_MIN = 1.175494e-38
FLT_MAX = 3.402823e+38
# DBL_MIN = 2.225074e-308
# DBL_MAX = 1.797693e+308


###############################################################################
# Wrapped Property
###############################################################################
def _convert_arguments(function):
    """bpy.props用のデコレータ
    可変長引数は name, description に展開する。
        limits, min, max は以下の様に展開する。
        limits: (min, soft_min, soft_max, max)
                 or (min(=soft_min), max(=soft_max))
        min: min or (min, soft_min) or (min(=soft_min), )
        max: max or (soft_max, max) or (max(=soft_max), )
    BVP, IVP, FVP で default, size の一方が欠けていた場合に補完する。

    rna_define.cのRNA_def_property()関数を参照
    """

    @_wraps(function)
    def _prop(*args, **kwargs):
        if 'limits' in kwargs:
            limits = kwargs.pop('limits')
        else:
            limits = None

        sig = _inspect.signature(function)
        bind = sig.bind(*args, **kwargs)
        kwargs = dict(bind.arguments)

        if limits:
            if len(limits) == 2:
                if limits[0] is not None:
                    kwargs['min'] = kwargs['soft_min'] = limits[0]
                if limits[1] is not None:
                    kwargs['max'] = kwargs['soft_max'] = limits[1]
            else:
                keys = ('min', 'soft_min', 'soft_max', 'max')
                for key, value in zip(keys, limits):
                    if value is not None:
                        kwargs[key] = value

        if 'min' in kwargs:
            value = kwargs['min']
            if isinstance(value, (list, tuple)):
                if len(value) == 1:
                    kwargs['min'] = kwargs['soft_min'] = value[0]
                else:
                    if value[0] is not None:
                        kwargs['min'] = value[0]
                    else:
                        del kwargs['min']
                    if value[1] is not None:
                        kwargs['soft_min'] = value[1]
        if 'max' in kwargs:
            value = kwargs['max']
            if isinstance(value, (list, tuple)):
                if len(value) == 1:
                    kwargs['soft_max'] = kwargs['max'] = value[0]
                else:
                    if value[0] is not None:
                        kwargs['soft_max'] = value[0]
                    if value[1] is not None:
                        kwargs['max'] = value[1]
                    else:
                        del kwargs['max']

        # Array Size and Default
        if function.__name__ in ('BVP', 'IVP', 'FVP'):
            if 'default' in kwargs and 'size' not in kwargs:
                kwargs['size'] = len(kwargs['default'])
            elif 'default' not in kwargs and 'size' in kwargs:
                if function.__name__ == 'BVP':
                    value = False
                elif function.__name__ == 'IVP':
                    value = 0
                elif function.__name__ == 'FVP':
                    value = 0.0
                kwargs['default'] = (value, ) * kwargs['size']

        # min, max, soft_min, soft_max
        # Cのint型、float型で表せない数値だと問題が起こるのでそれにも対処する
        if function.__name__ in ('IP', 'IVP', 'FP', 'FVP'):
            default_kwargs = {
                name: p.default for name, p in sig.parameters.items()
                if p.default != p.empty and
                name in ('min', 'max', 'soft_min', 'soft_max', 'subtype')}
            default_kwargs.update(kwargs)
            kwargs = default_kwargs
            subtype = kwargs['subtype']
            if function.__name__ in ('IP', 'IVP'):
                default_min = 0 if subtype == 'UNSIGNED' else INT_MIN
                default_max = INT_MAX
                default_soft_min = 0 if subtype == 'UNSIGNED' else -10000
                default_soft_max = 10000
            else:
                default_min = 0.0 if subtype == 'UNSIGNED' else -FLT_MAX
                default_max = FLT_MAX
                if subtype in ('COLOR', 'COLOR_GAMMA'):
                    default_soft_min = 0.0
                    default_soft_max = 1.0
                elif subtype == 'FACTOR':
                    default_soft_min = default_min = 0.0
                    default_soft_max = default_max = 1.0
                else:
                    default_soft_min = 0 if subtype == 'UNSIGNED' else -10000
                    default_soft_max = 10000

            hard_min = max(kwargs['min'], default_min)
            hard_max = min(kwargs['max'], default_max)

            soft_min = kwargs['soft_min']
            if soft_min is None:
                soft_min = default_soft_min
            soft_min = max(hard_min, soft_min)

            soft_max = kwargs['soft_max']
            if soft_max is None:
                soft_max = default_soft_max
            soft_max = min(hard_max, soft_max)

            kwargs['min'] = hard_min
            kwargs['max'] = hard_max
            kwargs['soft_min'] = soft_min
            kwargs['soft_max'] = soft_max

        return function(**kwargs)

    return _prop


def BP(name='', description='', default=False, options={'ANIMATABLE'},
       subtype='NONE', update=None, get=None, set=None):
    """Returns a new boolean property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR',
        'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
    :type subtype: string
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.BoolProperty(**locals())


@_convert_arguments
def BVP(name='', description='', default=(False, False, False),
        options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None,
        set=None):
    """Returns a new vector boolean property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg default: sequence of booleans the length of *size*.
    :type default: sequence
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION',
        'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION',
        'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'LAYER_MEMBER', 'NONE'].
    :type subtype: string
    :arg size: Vector dimensions in [1, 32].
    :type size: int
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.BoolVectorProperty(**locals())


@_convert_arguments
def IP(name='', description='', default=0, min=INT_MIN, max=INT_MAX,
       soft_min: -10000=None, soft_max: 10000=None, step=1,
       options={'ANIMATABLE'}, subtype='NONE',
       update=None, get=None, set=None):
    """Returns a new int property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg min: Hard minimum, trying to assign a value below will silently assign
        this minimum instead.
    :type min: int
    :arg max: Hard maximum, trying to assign a value above will silently assign
        this maximum instead.
    :type max: int
    :arg soft_max: Soft maximum (<= *max*), user won't be able to drag the
        widget above this value in the UI.
    :type soft_min: int
    :arg soft_min: Soft minimum (>= *min*), user won't be able to drag the
        widget below this value in the UI.
    :type soft_max: int
    :arg step: Step of increment/decrement in UI, in [1, 100], defaults to 1
        (WARNING: unused currently!).
    :type step: int
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR',
        'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
    :type subtype: string
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.IntProperty(**locals())


@_convert_arguments
def IVP(name='', description='', default=(0, 0, 0), min=INT_MIN, max=INT_MAX,
        soft_min: -10000=None, soft_max: 10000=None, step=1,
        options={'ANIMATABLE'}, subtype='NONE', size=3,
        update=None, get=None, set=None):
    """Returns a new vector int property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg default: sequence of ints the length of *size*.
    :type default: sequence
    :arg min: Hard minimum, trying to assign a value below will silently assign
        this minimum instead.
    :type min: int
    :arg max: Hard maximum, trying to assign a value above will silently assign
        this maximum instead.
    :type max: int
    :arg soft_min: Soft minimum (>= *min*), user won't be able to drag the
        widget below this value in the UI.
    :type soft_min: int
    :arg soft_max: Soft maximum (<= *max*), user won't be able to drag the
        widget above this value in the UI.
    :type soft_max: int
    :arg step: Step of increment/decrement in UI, in [1, 100], defaults to 1
        (WARNING: unused currently!).
    :type step: int
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION',
        'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION',
        'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'LAYER_MEMBER', 'NONE'].
    :type subtype: string
    :arg size: Vector dimensions in [1, 32].
    :type size: int
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: function
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: function
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: function
    """
    return _bpy.props.IntVectorProperty(**locals())


@_convert_arguments
def FP(name='', description='', default=0.0, min=-FLT_MAX, max=FLT_MAX,
       soft_min: -10000=None, soft_max: 10000=None, step=10, precision=3,
       options={'ANIMATABLE'}, subtype='NONE', unit='NONE',
       update=None, get=None, set=None):
    """Returns a new float property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg min: Hard minimum, trying to assign a value below will silently assign
        this minimum instead.
    :type min: float
    :arg max: Hard maximum, trying to assign a value above will silently assign
        this maximum instead.
    :type max: float
    :arg soft_min: Soft minimum (>= *min*), user won't be able to drag the
        widget below this value in the UI.
    :type soft_min: float
    :arg soft_max: Soft maximum (<= *max*), user won't be able to drag the
        widget above this value in the UI.
    :type soft_max: float
    :arg step: Step of increment/decrement in UI, in [1, 100], defaults to 3
        (WARNING: actual value is /100).
    :type step: float
    :arg precision: Maximum number of decimal digits to display, in [0, 6].
    :type precision: int
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['PIXEL', 'UNSIGNED', 'PERCENTAGE', 'FACTOR',
        'ANGLE', 'TIME', 'DISTANCE', 'NONE'].
    :type subtype: string
    :arg unit: Enumerator in ['NONE', 'LENGTH', 'AREA', 'VOLUME', 'ROTATION',
        'TIME', 'VELOCITY', 'ACCELERATION'].
    :type unit: string
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.FloatProperty(**locals())


@_convert_arguments
def FVP(name='', description='', default=(0, 0, 0), min=-FLT_MAX, max=FLT_MAX,
        soft_min: -10000=None, soft_max: 10000=None, step=10,
        precision=3, options={'ANIMATABLE'}, subtype='NONE', unit='NONE',
        size=3,
        update=None, get=None, set=None):
    """Returns a new vector float property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg default: sequence of floats the length of *size*.
    :type default: sequence
    :arg min: Hard minimum, trying to assign a value below will silently assign
        this minimum instead.
    :type min: float
    :arg max: Hard maximum, trying to assign a value above will silently assign
        this maximum instead.
    :type max: float
    :arg soft_min: Soft minimum (>= *min*), user won't be able to drag the
        widget below this value in the UI.
    :type soft_min: float
    :arg soft_max: Soft maximum (<= *max*), user won't be able to drag the
        widget above this value in the UI.
    :type soft_max: float
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg step: Step of increment/decrement in UI, in [1, 100], defaults to 3
        (WARNING: actual value is /100).
    :type step: float
    :arg precision: Maximum number of decimal digits to display, in [0, 6].
    :type precision: int
    :arg subtype: Enumerator in ['COLOR', 'TRANSLATION', 'DIRECTION',
        'VELOCITY', 'ACCELERATION', 'MATRIX', 'EULER', 'QUATERNION',
        'AXISANGLE', 'XYZ', 'COLOR_GAMMA', 'LAYER', 'LAYER_MEMBER', 'NONE'].
    :type subtype: string
    :arg unit: Enumerator in ['NONE', 'LENGTH', 'AREA', 'VOLUME', 'ROTATION',
        'TIME', 'VELOCITY', 'ACCELERATION'].
    :type unit: string
    :arg size: Vector dimensions in [1, 32].
    :type size: int
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.FloatVectorProperty(**locals())


def SP(name='', description='', default='', maxlen=0, options={'ANIMATABLE'},
       subtype='NONE', update=None, get=None, set=None):
    """Returns a new string property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg default: initializer string.
    :type default: string
    :arg maxlen: maximum length of the string.
    :type maxlen: int
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg subtype: Enumerator in ['FILE_PATH', 'DIR_PATH', 'FILE_NAME',
        'BYTE_STRING', 'PASSWORD', 'NONE'].
    :type subtype: string
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    return _bpy.props.StringProperty(**locals())


def EP(name='', description='', items=(), default='', options={'ANIMATABLE'},
       update=None, get=None, set=None):
    """Returns a new enumerator property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg items: sequence of enum items formatted:
        [(identifier, name, description, icon, number), ...] where the
        identifier is used for python access and other values are used for the
        interface.
        The three first elements of the tuples are mandatory.
        The forth one is either the (unique!) number id of the item or, if
        followed by a fith element (which must be the numid), an icon string
        identifier or integer icon value (e.g. returned by icon()...).
        Note the item is optional.
        For dynamic values a callback can be passed which returns a list in
        the same format as the static list.
        This function must take 2 arguments (self, context)
        WARNING: There is a known bug with using a callback,
        Python must keep a reference to the strings returned or Blender will
        crash.
    :type items: sequence of string tuples or a function
    :arg default: The default value for this enum, a string from the
        identifiers used in *items*.
        If the *ENUM_FLAG* option is used this must be a set of such string
        identifiers instead.
    :type default: string or set
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'ENUM_FLAG', 'LIBRARY_EDITABLE'].
    :type options: set
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: types.FunctionType
    :arg get: Function to be called when this value is 'read',
        This function must take 1 value (self) and return the value of the
        property.
    :type get: types.FunctionType
    :arg set: Function to be called when this value is 'written',
        This function must take 2 values (self, value) and return None.
    :type set: types.FunctionType
    """
    kwargs = dict(locals())
    if not default:
        del kwargs['default']
    return _bpy.props.EnumProperty(**kwargs)


def PP(name='', description='', type=None, options={'ANIMATABLE'},
       update=None):
    """Returns a new pointer property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg type: A subclass of :class:`bpy.types.PropertyGroup`.
    :type type: class
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    :arg update: Function to be called when this value is modified,
        This function must take 2 values (self, context) and return None.
        *Warning* there are no safety checks to avoid infinite recursion.
    :type update: function
    """
    return _bpy.props.PointerProperty(**locals())


def CP(name='', description='', type=None, options={'ANIMATABLE'}):
    """Returns a new collection property definition.
    :arg name: Name used in the user interface.
    :type name: string
    :arg description: Text used for the tooltip and api documentation.
    :type description: string
    :arg type: A subclass of :class:`bpy.types.PropertyGroup`.
    :type type: class
    :arg options: Enumerator in ['HIDDEN', 'SKIP_SAVE', 'ANIMATABLE',
        'LIBRARY_EDITABLE', 'PROPORTIONAL'].
    :type options: set
    """
    return _bpy.props.CollectionProperty(**locals())


def RP(cls, attr=''):
    """Removes a dynamically defined property.
    :param cls: The class containing the property (must be a positional
        argument).
    :type cls: class
    :param attr: Property name (must be passed as a keyword).
    :type attr: str

    NOTE: Typically this function doesn't need to be accessed directly.
        Instead use ``del cls.attr``
    """
    return _bpy.props.RemoveProperty(cls, attr=attr)


###############################################################################
# bpy_struct <-> dict
###############################################################################
ADDRESS = '_ADDRESS'
ID_PROPERTY = '_ID_PROPERTY'
NAMESPACE = '__dict__'

_converted_props = {}


# bpy_struct -> dict ----------------------------------------------------------
def _dump_namespace(obj, r_dict):
    """__dict__属性。pickle化可能な物のみ追加する"""
    if not hasattr(obj, '__dict__'):
        return

    r_dict[NAMESPACE] = dic = {}
    for k, v in obj.__dict__.items():
        try:
            _pickle.dumps(v)
        except _pickle.PicklingError as e:
            _logger.warning(str(e))
            continue
        dic[k] = v
    return dic


def _dump_id_property(obj, r_dict):
    """IDProperty
    Only bpy.types.ID, bpy.types.Bone and bpy.types.PoseBone classes support
    custom properties.
    ↑ PropertyGroup も
    """
    try:
        obj.keys()
    except TypeError:
        # 'bpy_struct.keys(): this type doesn't support IDProperties'
        return

    bl_rna = obj.bl_rna
    keys = list(bl_rna.properties.keys())
    r_dict[ID_PROPERTY] = dic = {}
    for key in obj.keys():
        if key not in keys:
            id_prop = obj[key]
            if not isinstance(id_prop, (int, float, str)):  # boolはint扱い
                cls_name = id_prop.__class__.__name__
                if cls_name == 'IDPropertyArray':
                    id_prop = id_prop.to_list()
                elif cls_name == 'IDPropertyGroup':
                    id_prop = id_prop.to_dict()
            dic[key] = id_prop
    return dic


def _dump_pointer(obj, attr, r_dict):
    bl_rna = obj.bl_rna
    prop = bl_rna.properties[attr]
    prop_obj = getattr(obj, attr)

    if prop_obj is None:
        r_dict[attr] = (prop.type, None, prop.fixed_type.identifier)
        return

    elif prop_obj in _converted_props:
        address = prop_obj.as_pointer()
        r_dict[attr] = _converted_props[address]
        return

    address = prop_obj.as_pointer()
    dic = {ADDRESS: address}
    prop_data = (prop.type, dic, prop.fixed_type.__class__.__name__)
    r_dict[attr] = _converted_props[address] = prop_data

    _dump(prop_obj, None, dic)

    return prop_data


def _dump_collection(obj, attr, r_dict):
    bl_rna = obj.bl_rna
    prop = bl_rna.properties[attr]

    ls = []
    prop_data = (prop.type, ls, prop.fixed_type.__class__.__name__)
    r_dict[attr] = prop_data

    for elem in getattr(obj, attr):
        if elem is None:
            ls.append(None)
        else:
            address = elem.as_pointer()
            if address in _converted_props:
                ls.append(_converted_props[address])
            else:
                dic = {ADDRESS: address}
                ls.append(dic)
                _converted_props[address] = dic
                _dump(elem, None, dic)

    return prop_data


def _dump(obj, attr=None, r_dict=None):
    # NOTE: bl_rna.name == bl_label
    #       bl_rna.identifier == bl_idname == bpy.typesでの属性名
    #
    #       bl_rna.__class__ == bpy.types.Hoge
    #       bl_rna == bpy.types.Hoge.bl_rna

    if r_dict is None:
        r_dict = {}
    # if not obj or not hasattr(obj, 'bl_rna'):
    #     return r_dict
    if not issubclass(obj.__class__, _bpy.types.ID.__base__):  # <bpy_struct>
        return r_dict

    bl_rna = obj.bl_rna

    if attr is None:
        _dump(obj, NAMESPACE, r_dict)
        _dump(obj, ID_PROPERTY, r_dict)
        for key in bl_rna.properties.keys():
            if key != 'rna_type':
                _dump(obj, key, r_dict)
        return r_dict

    elif attr == ID_PROPERTY:
        _dump_id_property(obj, r_dict)
        return r_dict

    elif attr == NAMESPACE:
        _dump_namespace(obj, r_dict)
        return r_dict

    # # bug: segmentation fault
    # if isinstance(obj, _bpy.types.ParticleEdit):
    #     if attr in ('is_editable', 'is_hair', 'object'):
    #         return r_dict

    prop = bl_rna.properties[attr]
    prop_obj = getattr(obj, attr)

    if prop.type == 'POINTER':
        _dump_pointer(obj, attr, r_dict)

    elif prop.type == 'COLLECTION':
        _dump_collection(obj, attr, r_dict)

    elif prop.type in ('BOOLEAN', 'ENUM', 'FLOAT', 'INT', 'STRING'):
        if hasattr(prop, 'array_length') and prop.array_length > 0:
            if prop.subtype == 'MATRIX':
                r_dict[attr] = (prop.type, [list(x) for x in prop_obj])
            else:
                r_dict[attr] = (prop.type, list(prop_obj))
        else:
            if isinstance(prop_obj, set):  # ENUM: options={'ENUM_FLAG', ...}
                r_dict[attr] = (prop.type, set(prop_obj))
            else:
                r_dict[attr] = (prop.type, prop_obj)

    return r_dict


def dump(obj, attr=None):
    """PropertyGroupを再帰的に辿って辞書に変換する。bpy_structに対しても可。
    ('BOOLEAN', True) or ('BOOLEAN', [True, False, ...])
    ('INT', 1) or ('INT', [0, 1, ...])
    ('FLOAT', 1.0) or ('FLOAT', [0.0, 1.0, ...])
    ('ENUM', 'A') or ('ENUM', {'A', 'B', ...})
    ('STRING', 'abc')
    ('POINTER', {}, type_identifier)
    ('COLLECTION', [{}, ...], type_identifier)
    :type obj: PropertyGroup | bpy_struct
    :param attr: 対象の属性。Noneで全ての属性を辿る。NAMESPACEで__dict__属性、
        ID_PROPERTYではIDPropertyを取得する。
    :type attr: list | tuple | str
    :rtype: dict
    """
    _converted_props.clear()
    if attr is None:
        return _dump(obj)
    elif not attr:
        return {}
    else:
        if isinstance(attr, str):
            return _dump(obj, attr)[attr]
        else:
            dic = {}
            for a in attr:
                _dump(obj, a, dic)
            return dic


# dict -> bpy_struct ----------------------------------------------------------
def _undump_namespace(prop_data, obj):
    try:
        obj.__dict__.clear()
        obj.__dict__.update(prop_data)
    except Exception as err:
        _logger.error(str(err))


def _undump_id_property(prop_data, obj):
    try:
        obj.keys()
    except TypeError as err:
        _logger.error(str(err))
        return

    for k in list(obj.keys()):
        del obj[k]
    for k, v in prop_data.items():
        try:
            obj[k] = v
        except Exception as err:
            _logger.error(str(err))


def _undump_pointer(prop_data, obj, attr):
    # prop_dataはgetattr(obj, attr)のもの
    prop = obj.bl_rna.properties.get(attr)

    if prop_data[0] != 'POINTER':
        _logger.error("'{}.{} is 'POINTER' property, not '{}'".format(
            str(type(obj)), attr, prop_data[0]))

    _type, dic, _class_name = prop_data

    if dic is None:
        try:
            setattr(obj, attr, None)
        except Exception as err:
            _logger.error(str(err))

    elif not dic:
        pass

    elif issubclass(prop.fixed_type.__class__, _bpy.types.PropertyGroup):
        prop_obj = getattr(obj, attr)
        _undump(dic, prop_obj)

    elif (dic.get(ADDRESS) not in _converted_props and
          str(id(dic)) not in _converted_props):
        if ADDRESS in dic:
            _converted_props[dic[ADDRESS]] = True
        else:
            msg = "'{}' not in {}.{} property data".format(
                ADDRESS, str(type(obj)), attr)
            _logger.warning(msg)
        _converted_props[str(id(dic))] = True

        if prop.is_readonly:
            _undump(dic, getattr(obj, attr))
        else:
            # bpy.dataの中から探す
            # NOTE: bpy.data: rna_type, filepath, is_dirty, is_saved,
            #       use_autopack, version 以外は全てIDのサブクラス
            for attr_, prop_ in _bpy.data.bl_rna.properties.items():
                if (prop_.type == 'POINTER' and
                        prop_.fixed_type == prop.fixed_type):
                    if 'name' in dic:
                        ob_name = dic['name']
                        prop_obj = getattr(_bpy.data, attr_)[ob_name]
                        try:
                            setattr(obj, attr, prop_obj)
                        except Exception as err:  # 例外はあり得るか？
                            _logger.error(str(err))
                    else:
                        msg = "'name' not in {}.{} property data".format(
                            str(type(obj)), attr)
                        _logger.warning(msg)
                        prop_obj = getattr(obj, attr)
                    _undump(dic, prop_obj)

                    break
            else:
                _undump(dic, getattr(obj, attr))


def _undump_collection(prop_data, obj, attr):
    if prop_data[0] != 'COLLECTION':
        _logger.error("'{}.{} is 'COLLECTION' property, not '{}'".format(
            str(type(obj)), attr, prop_data[0]))

    _type, ls, _class_name = prop_data

    prop = obj.bl_rna.properties.get(attr)
    # if hasattr(prop_obj, 'clear') and hasattr(prop_obj, 'add'):
    if issubclass(prop.fixed_type.__class__, _bpy.types.PropertyGroup):
        collection = getattr(obj, attr)
        collection.clear()
        for dic in ls:
            elem = collection.add()
            _undump(dic, elem)
    else:
        # TODO: Object.material_slots, Scene.objects等々
        pass


def _undump(prop_dict, obj):
    if obj is None:
        return

    for attr, prop_data in sorted(prop_dict.items(), key=lambda x: x[0]):
        if attr == ADDRESS:
            continue

        if attr == NAMESPACE:
            _undump_namespace(prop_data, obj)
            continue

        if attr == ID_PROPERTY:
            _undump_id_property(prop_data, obj)
            continue

        prop = obj.bl_rna.properties.get(attr)

        if not prop:
            _logger.error("{} has no property '{}'".format(obj, attr))
            continue

        if prop.type == 'POINTER':
            _undump_pointer(prop_data, obj, attr)

        elif prop.type == 'COLLECTION':
            _undump_collection(prop_data, obj, attr)

        elif not prop.is_readonly:
            # is_readonlyが偽でも実行時に
            # bpy_prop "***" is read-only と出る場合がある
            t, val = prop_data
            try:
                if hasattr(prop, 'array_length') and prop.array_length > 0:
                    # matrix_world等は、スライスを使わないと勝手に値を
                    # 修正してしまう
                    getattr(obj, attr)[:] = val
                else:
                    setattr(obj, attr, val)
            except Exception as err:
                _logger.error(str(err))


def undump(prop_dict, obj):
    """dump()で得た辞書でPropertyGroupを更新する。
    一応はbpy_structに対しても有効だが、COLLECTIONプロパティは非対応。
    適用する必要の無い不要なPOINTERプロパティは削除又は修正しておくこと。
    e.g.)
    Object.active_materialを変更したいが、そのMaterialの属性については変更を
    加えたくない場合は、ADDRESSと'name'を残して消す。
    ADDRESSは変更済みのオブジェクトを記録しておいて同オブジェクトに対して
    複数回変更を加えないようにする為のものなので必須ではない。
    {'active_material':
          ('POINTER',
           {ADDRESS: 140195969897480, 'name': 'Material.001'},
           'Material'),
     ...
    }
    :type prop_dict: dict
    :type obj: PropertyGroup | bpy_struct
    """
    _converted_props.clear()
    _undump(prop_dict, obj)


###############################################################################
# save / load
###############################################################################
def save(file_path, prop_obj, include=None, exclude=None, clear=True):
    """
    :type file_path: str
    :type prop_obj: dict | object
    :type include: dict
    :type exclude: list | tuple
    :type clear: bool
    """
    if isinstance(prop_obj, dict):
        d = prop_obj
    else:
        d = dump(prop_obj)
    if include:
        if isinstance(prop_obj, dict):
            d = dict(d)
        d.update(include)
    if exclude:
        for key in exclude:
            if key in d:
                del d[key]
    try:
        shelf = _shelve.open(file_path)
    except Exception as err:
        _logger.error(str(err))
        return False
    if clear:
        shelf.clear()
    shelf.update(d)
    shelf.close()
    _logger.info("saved to '{}'".format(file_path))
    return True


def load(file_path, prop_obj, include=None, exclude=None):
    """
    :type file_path: str
    :type prop_obj: dict | object
    :type include: dict
    :type exclude: list | tuple
    """
    try:
        shelf = _shelve.open(file_path)
    except Exception as err:
        _logger.error(str(err))
        return False
    d = dict(shelf)
    shelf.close()
    if include:
        d.update(include)
    if exclude:
        for key in exclude:
            if key in d:
                del d[key]
    if isinstance(prop_obj, dict):
        prop_obj.update(d)
    else:
        undump(d, prop_obj)
    _logger.info("loaded from '{}'".format(file_path))
    return True


"""
NOTE:

属性一覧:
PointerProperty:
    as_pointer(), bl_rna, driver_add(), driver_remove(), get(), id_data,
    is_property_hidden(), is_property_set(), items(), keyframe_delete(),
    keyframe_insert(), keys(), name, path_from_id(), path_resolve(),
    property_unset(), rna_type, type_recast(), values()
    dir: ['__dict__', '__doc__', '__module__', '__weakref__', 'bl_rna', 'name',
          'rna_type']
CollectionProperty:
    add(), as_bytes(), clear(), data, find(), foreach_get(), foreach_set(),
    get(), id_data, items(), keys(), move(), path_from_id(), remove(),
    rna_type(), values()
    dir: ['__doc__', 'add', 'clear', 'move', 'remove']


PyObject *obj;
if (BPy_StructRNA_Check(obj)) {  # bpy_rna.h
    BPy_StructRNA *py_srna = (BPy_StructRNA *)obj;
    PointerRNA *ptr = &py_srna->ptr;
    StructRNA *srna = ptr->data;
    if (RNA_struct_is_ID(ptr->type)) {
        ID *id = ptr->id.data;
    }
}
"""