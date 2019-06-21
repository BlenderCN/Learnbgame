### BEGIN GPL LICENSE BLOCK #####
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

# <pep8 compliant>

from bpy.types import ID

_basetypes = { 'void', 'any', 'int', 'float', 'bool', 'color', 'vector', 'normal', 'point', 'matrix', 'string', 'mesh' }
_basetypes_default = {
    'any'       : None,
    'int'       : '0',
    'float'     : '0.0',
    'bool'      : 'false',
    'color'     : 'color(0,0,0)',
    'vector'    : 'vector(0,0,0)',
    'normal'    : 'normal(0,0,1)',
    'point'     : 'point(0,0,0)',
    'matrix'    : 'matrix(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)',
    'string'    : 'string("")',
    'mesh'      : None,
    }

def value_from_rna(typedesc, prop, value):
    b = typedesc.basetype
    if b == 'any':
        return None # XXX what? any doesn't have a value, should be removed anyway ...
    elif b == 'int':
        return str(int(value))
    elif b == 'float':
        return str(float(value))
    elif b == 'bool':
        return "true" if value else "false"
    elif b == 'color':
        return "color(%s)" % ", ".join(str(float(v)) for v in value[0:4])
    elif b == 'vector':
        return "vector(%s)" % ", ".join(str(float(v)) for v in value[0:3])
    elif b == 'normal':
        return "normal(%s)" % ", ".join(str(float(v)) for v in value[0:3])
    elif b == 'point':
        return "point(%s)" % ", ".join(str(float(v)) for v in value[0:3])
    elif b == 'matrix':
        return "matrix(%s)" % ", ".join(str(float(v)) for v in value[0:16])
    elif b == 'string':
        if prop.type == 'POINTER':
            # convert struct objects into bpy path strings
            if isinstance(value, ID):
                return idref.get_full_path(value)
            else:
                # XXX unsupported
                return "\"\""
        elif prop.is_enum_flag:
            return "\"%s\"" % "|".join(v for v in value)
        else:
            return "\"%s\"" % value
    elif b == 'mesh':
        return None

int_types = {'int', 'bool'}
scalar_types = {'float', 'int', 'bool'}
vector_types = {'vector', 'point', 'normal'}
float3_types = vector_types | {'color'}
array_types = float3_types | {'matrix'}
string_types = {'string'}

class TypeDesc():
    def __init__(self, basetype, array_size=None):
        assert(basetype in _basetypes)
        self.basetype = basetype
        self.array_size = array_size

    # python trick: this allows using a predefined type descriptor
    # to be used both with and without array_size argument, like:
    #   single_float = TypeFloat
    #   array_float = TypeFloat(7)
    def __call__(self, array_size):
        return TypeDesc(self.basetype, array_size)

    def __str__(self):
        return self.basetype

    def __repr__(self):
        return "<TypeDesc at %s, basetype=%r, array_size=%r>" % (hex(id(self)), self.basetype, self.array_size)

    def __eq__(self, other):
        return self.basetype == other.basetype and self.array_size == other.array_size

    def __ne__(self, other):
        return self.basetype != other.basetype or self.array_size != other.array_size

    def simpletype(self):
        """ Returns the base type without array """
        return TypeDesc(self.basetype)

    def deref(self):
        if self.array_size is None:
            if self.basetype in {'vector', 'point', 'normal'}:
                return TypeDesc('float')
            if self.basetype in {'color'}:
                return TypeDesc('float')
            elif self.basetype in {'matrix'}:
                return TypeDesc('float', array_size=4)
            else:
                raise Exception("Cannot derefence type %r" % self)
        else:
            return TypeDesc(self.basetype)

# shorthands for avoiding repetitive strings
TypeVoid = TypeDesc('void')
TypeAny = TypeDesc('any')
TypeFloat = TypeDesc('float')
TypeInt = TypeDesc('int')
TypeBool = TypeDesc('bool')
TypeColor = TypeDesc('color')
TypeVector = TypeDesc('vector')
TypePoint = TypeDesc('point')
TypeNormal = TypeDesc('normal')
TypeMatrix = TypeDesc('matrix')
TypeString = TypeDesc('string')
TypeMesh = TypeDesc('mesh')


from bpy.props import *
from pynodes_framework.parameter import *
from pynodes_framework.idref import *
from pynodes_framework.group import NodeGroup
import database

# update callback used for socket input values
# triggers a modifier sync like nodetree.update()
def update_socket_value(node, context):
    ntree = node.id_data
    database.tag_update(ntree)

class ModifierNodeParamAny(NodeParamAny):
    value_update = update_socket_value

class ModifierNodeParamFloat(NodeParamFloat):
    value_update = update_socket_value
    
class ModifierNodeParamInt(NodeParamInt):
    value_update = update_socket_value

class ModifierNodeParamBool(NodeParamBool):
    value_update = update_socket_value

class ModifierNodeParamColor(NodeParamColor):
    value_update = update_socket_value

class ModifierNodeParamVector(NodeParamVector):
    value_update = update_socket_value

class ModifierNodeParamPoint(NodeParamPoint):
    value_update = update_socket_value

class ModifierNodeParamNormal(NodeParamNormal):
    value_update = update_socket_value

class ModifierNodeParamMatrix(NodeParamMatrix):
    value_update = update_socket_value

class ModifierNodeParamString(NodeParamString):
    value_update = update_socket_value

class ModifierNodeParamEnum(NodeParamEnum):
    value_update = update_socket_value

class ModifierNodeParamMesh(NodeParameter):
    """Modifier mesh data"""
    datatype_identifier = "MESH"
    datatype_name = "Mesh"
    color = (0.80, 0.30, 0.00, 1.0)

    def __init__(self, name, is_output=False, use_socket=True, **kw):
        NodeParameter.__init__(self, name, is_output, use_socket)

class ModifierNodeParamIDRef(NodeParameter):
    """Reference to an ID datablock"""
    datatype_identifier = "IDREF"
    datatype_name = "IDRef"
    color = (0.80, 0.15, 0.30, 1.0)

    def __init__(self, name, is_output=False, use_socket=True, idtype='OBJECT', **kw):
        NodeParameter.__init__(self, name, is_output, use_socket,
                               prop=IDRefProperty(name, idtype=idtype, **kw))

    def draw_socket(self, layout, data, prop, text):
        draw_idref(layout, data, prop, text)

def define_node_params(cls, name, typedesc, is_output, default, metadata, *args, **kw):
    basetype = typedesc.basetype
    label = metadata.get("label", name)
    display = metadata.get("display", "socket")

    if display == "none":
        return None
    use_socket = (display == "socket")
    use_button = (display == "button" and not is_output)

    param = None

    if basetype in {'void'}:
        pass
    elif basetype == 'any':
        param = ModifierNodeParamAny(name=label, is_output=is_output, *args, **kw)
    elif basetype == 'float':
        param = ModifierNodeParamFloat(name=label, is_output=is_output, default=default, *args, **kw)
    elif basetype == 'int':
        param = ModifierNodeParamInt(name=label, is_output=is_output, default=default, *args, **kw)
    elif basetype == 'bool':
        param = ModifierNodeParamBool(name=label, is_output=is_output, default=default, *args, **kw)
    elif basetype == 'color':
        param = ModifierNodeParamColor(name=label, is_output=is_output, default=default[:], *args, **kw)
    elif basetype == 'vector':
        param = ModifierNodeParamVector(name=label, is_output=is_output, default=default[:], *args, **kw)
    elif basetype == 'point':
        param = ModifierNodeParamPoint(name=label, is_output=is_output, default=default[:], *args, **kw)
    elif basetype == 'normal':
        param = ModifierNodeParamNormal(name=label, is_output=is_output, default=default[:], *args, **kw)
    elif basetype == 'matrix':
        param = ModifierNodeParamMatrix(name=label, is_output=is_output, default=default[:], *args, **kw)
    elif basetype == 'string':
        widget = metadata.get("widget", "")
        options = metadata.get("options", "").split('|')
        if widget in {'popup', 'mapper'}:
            prop_options = {'ANIMATABLE'}
            if widget == 'popup':
                items = [(opt, opt, "") for opt in options]
            elif widget == 'mapper':
                items = []
                for opt in options:
                    opt_name, opt_id = opt.split(':')
                    try:
                        i = int(opt_id)
                    except:
                        i = None
                    if i is None:
                        items.append((opt_id, opt_name, ""))
                    else:
                        items.append((opt_id, opt_name, "", int(opt_id)))

                if int(metadata.get("is_flag", "0")):
                    prop_options.add('ENUM_FLAG')
                    default = set(flag for flag in default.split("|"))
            param = ModifierNodeParamEnum(name=label, is_output=is_output, default=default, items=items, options=prop_options, *args, **kw)
        elif widget in {'idref'}:
            idtype = metadata.get("idtype", "OBJECT")
            param = ModifierNodeParamIDRef(name=label, is_output=is_output, idtype=idtype, *args, **kw)
        else:
            param = ModifierNodeParamString(name=label, is_output=is_output, default=default, *args, **kw)
    elif basetype == 'mesh':
        param = ModifierNodeParamMesh(name=label, is_output=is_output, default=default, *args, **kw)
    else:
        raise Exception("Unknown typedesc base type %r, cannot create node parameter" % basetype)

    if param:
        if use_socket:
            param.identifier = name
            setattr(cls, name, param)

        if use_button:
            if param.prop:
                setattr(cls, name, param.prop)
                def draw_button(self, context, layout):
                    param.draw_socket(layout, self, name, label)
                cls.append(draw_button)


node_datatype_typedesc = {
    'ANY'       : TypeAny,
    'FLOAT'     : TypeFloat,
    'INT'       : TypeInt,
    'BOOL'      : TypeBool,
    'COLOR'     : TypeColor,
    'VECTOR'    : TypeVector,
    'POINT'     : TypePoint,
    'NORMAL'    : TypeNormal,
    'MATRIX'    : TypeMatrix,
    'STRING'    : TypeString,
    'MESH'      : TypeMesh,
    'IDREF'     : TypeString,
    }


#modifier_parameter_types = [ModifierNodeParamAny, ModifierNodeParamFloat, ModifierNodeParamInt, ModifierNodeParamBool, ModifierNodeParamColor,
#                            ModifierNodeParamVector, ModifierNodeParamPoint, ModifierNodeParamNormal, ModifierNodeParamMatrix,
#                            ModifierNodeParamString, ModifierNodeParamEnum, ModifierNodeParamMesh, ModifierNodeParamIDRef]

# XXX TODO ModifierNodeParamEnum needs registered item PropertyGroup
modifier_parameter_types = [ModifierNodeParamAny, ModifierNodeParamFloat, ModifierNodeParamInt, ModifierNodeParamBool, ModifierNodeParamColor,
                            ModifierNodeParamVector, ModifierNodeParamPoint, ModifierNodeParamNormal, ModifierNodeParamMatrix,
                            ModifierNodeParamString, ModifierNodeParamMesh, ModifierNodeParamIDRef]

def register():
    for pt in modifier_parameter_types:
        pt.register_template()

def unregister():
    for pt in modifier_parameter_types:
        pt.unregister_template()
