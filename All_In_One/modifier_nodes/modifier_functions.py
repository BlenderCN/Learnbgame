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

import bpy
from symbol import *
from converter import Expression
from typedesc import *

StructRNA = bpy.types.Struct.__bases__[0]


class DerivedMesh():
    def __init__(self):
        self.obgen = []

    def copy(self):
        dm = DerivedMesh()
        dm.obgen = self.obgen[:]
        return dm

    def modifier(self, func, typename):
        self.obgen.append((func, typename))

    def apply(self, ob):
        """
        def find_object_modifier(name):
            for mod in ob.modifiers:
                if mod.name == name
                    return mod
            return None
        """

        # sync modifier stack
        # XXX NB: Modifier stack API is very rigid atm (no move(from, to) function),
        # any reordering will usually require almost full rebuild.
        # Should not be a big issue in most cases, but at some point
        # a more flexible API may be necessary

        obindex = 0
        for func, typename in self.obgen:
            #name = "%s%d" % (layername, curindex)
            name = typename # just let uniquename handle actual modifier instance name for now

            #obmod = find_object_modifier(name) # XXX only useful once we have a reordering function
            obmod = ob.modifiers[obindex] if obindex < len(ob.modifiers) else None

            if obmod and obmod.type == typename:
                pass
            else:
                # remove all remaining modifiers, this is necessary
                # because we can only add new modifiers at the end ...
                for i in range(obindex, len(ob.modifiers)):
                    ob.modifiers.remove(ob.modifiers[obindex])
                obmod = ob.modifiers.new(name, typename)
            obindex += 1

            func(obmod)

        # remove leftover modifiers
        for i in range(obindex, len(ob.modifiers)):
            ob.modifiers.remove(ob.modifiers[obindex])

    def __repr__(self):
        obgenr = "\n%s" % ", ".join("\t%r\n" % (g,) for g in self.obgen) if self.obgen else ""
        return "DerivedMesh(%s)" % obgenr


class ModifierFunction():
    def __init__(self, typename, *argdesc):
        self.typename = typename
        self.fixed_values = { prop_name : value for (mod_name, prop_name), value in _fixed_value.items() if mod_name == typename }
        self.argtypes = [a[0] for a in argdesc]
        self.argnames = [a[1] for a in argdesc]
        self.is_struct = [a[2] for a in argdesc]
        self.is_flag = [a[3] for a in argdesc]

    def __call__(self, mesh, *args):
        def modifier_values():
            # generic settings
            yield "show_render", True
            yield "show_viewport", True
            yield "show_in_editmode", False # XXX yes? no?
            yield "show_expanded", False

            # fixed values
            for name, value in self.fixed_values.items():
                yield name, value

            # variable arguments
            for i, arg in enumerate(args):
                name = self.argnames[i]
                if self.is_struct[i]:
                    value = eval(arg) if arg else None
                elif self.is_flag[i]:
                    value = set(flag for flag in arg.split("|"))
                else:
                    value = arg
                yield name, value

        def func(obmod):
            # set properties on object modifier
            for key, value in modifier_values():
                cur_value = getattr(obmod, key)
                if cur_value != value:
                    setattr(obmod, key, value)

        mesh.modifier(func, self.typename)
        return mesh

def ismodifierfunction(o):
    return isinstance(o, ModifierFunction)

# maps identifiers to the RNA types
# this can not be retrieved directly from RNA info
_modifier_type_names = {
    'MESH_CACHE'             : 'MeshCacheModifier',
    'UV_PROJECT'             : 'UVProjectModifier',
    'UV_WARP'                : 'UVWarpModifier',
    'VERTEX_WEIGHT_EDIT'     : 'VertexWeightEditModifier',
    'VERTEX_WEIGHT_MIX'      : 'VertexWeightMixModifier',
    'VERTEX_WEIGHT_PROXIMITY' : 'VertexWeightProximityModifier',
    'ARRAY'                  : 'ArrayModifier',
    'BEVEL'                  : 'BevelModifier',
    'BOOLEAN'                : 'BooleanModifier',
    'BUILD'                  : 'BuildModifier',
    'DECIMATE'               : 'DecimateModifier',
    'EDGE_SPLIT'             : 'EdgeSplitModifier',
    'MASK'                   : 'MaskModifier',
    'MIRROR'                 : 'MirrorModifier',
    'MULTIRES'               : 'MultiresModifier',
    'REMESH'                 : 'RemeshModifier',
    'SCREW'                  : 'ScrewModifier',
    'SKIN'                   : 'SkinModifier',
    'SOLIDIFY'               : 'SolidifyModifier',
    'SUBSURF'                : 'SubsurfModifier',
    'TRIANGULATE'            : 'TriangulateModifier',
    'ARMATURE'               : 'ArmatureModifier',
    'CAST'                   : 'CastModifier',
    'CURVE'                  : 'CurveModifier',
    'DISPLACE'               : 'DisplaceModifier',
    'HOOK'                   : 'HookModifier',
    'LAPLACIANSMOOTH'        : 'LaplacianSmoothModifier',
    'LATTICE'                : 'LatticeModifier',
    'MESH_DEFORM'            : 'MeshDeformModifier',
    'SHRINKWRAP'             : 'ShrinkwrapModifier',
    'SIMPLE_DEFORM'          : 'SimpleDeformModifier',
    'SMOOTH'                 : 'SmoothModifier',
    'WARP'                   : 'WarpModifier',
    'WAVE'                   : 'WaveModifier',
    'CLOTH'                  : 'ClothModifier',
    'COLLISION'              : 'CollisionModifier',
    'DYNAMIC_PAINT'          : 'DynamicPaintModifier',
    'EXPLODE'                : 'ExplodeModifier',
    'FLUID_SIMULATION'       : 'FluidSimulationModifier',
    'OCEAN'                  : 'OceanModifier',
    'PARTICLE_INSTANCE'      : 'ParticleInstanceModifier',
    'PARTICLE_SYSTEM'        : 'ParticleSystemModifier',
    'SMOKE'                  : 'SmokeModifier',
    'SOFT_BODY'              : 'SoftBodyModifier',
    'SURFACE'                : 'SurfaceModifier',
}

# XXX stupid code for printing the dictionary above
"""
def _print_modifier_map():
    ids = [item.identifier for item in bpy.types.Modifier.bl_rna.properties['type'].enum_items]
    for mt in ids:
        ob = bpy.data.objects['Cube']
        mod = ob.modifiers.new(name="blah", type=mt)
        name = repr(mt).ljust(24)
        print("    %s : %r," % (name, mod.bl_rna.identifier))
        ob.modifiers.remove(mod)
"""

### Special Modifiers ###

# don't automatically generate a modifier script for these
_skip_modifier = {}

# don't automatically generate a node script for these
_skip_node = {
    'ARRAY',
}

# don't generate properties for these parameters
# (modifier, parameter)
_skip_property = {
    ('ARRAY', 'fit_type'),
}

# use a fixed value for these parameters
# (modifier, parameter) : value
_fixed_value = {
    ('ARRAY', 'use_constant_offset')    : True,
    ('ARRAY', 'use_relative_offset')    : True,
    ('ARRAY', 'use_object_offset')      : True,
}

#########################

def modifier_types():
    for key, typename in _modifier_type_names.items():
        btype = getattr(bpy.types, typename)
        assert(issubclass(btype, bpy.types.Modifier))
        yield key, btype

def typedesc_from_rna(prop):
    basetype = prop.type
    subtype = prop.subtype
    array_length = getattr(prop, "array_length", None)

    typedesc = None
    is_struct = False
    is_flag = prop.is_enum_flag
    if basetype == 'FLOAT':
        if array_length in { None, 0 }:
            typedesc = TypeFloat
        elif array_length == 3:
            if subtype == 'DIRECTION':
                typedesc = TypeNormal
            else:
                typedesc = TypeVector
        elif array_length == 4:
            typedesc = TypeColor
    elif basetype == 'INT':
        if array_length in { None, 0 }:
            typedesc = TypeInt
    elif basetype == 'BOOLEAN':
        if array_length in { None, 0 }:
            typedesc = TypeBool
    elif basetype == 'STRING':
        if array_length in { None, 0 }:
            typedesc = TypeString
    elif basetype == 'ENUM':
        if array_length in { None, 0 }:
            typedesc = TypeString
    elif basetype == 'POINTER':
        if array_length in { None, 0 }:
            typedesc = TypeString
            is_struct = True
    elif basetype == 'COLLECTION':
        # XXX ignore for now
        pass

#    if typedesc is None:
#        details = "type %r, subtype %r" % (basetype, subtype)
#        if array_length is not None:
#            details += ", array length %d" % array_length
#        raise Exception("Cannot convert RNA property %r (%s) into type descriptor" % (prop, details))

    return (typedesc, is_struct, is_flag)

def modifier_properties(mod_name, mod_type):
    _modifier_base_props = set(bpy.types.Modifier.bl_rna.properties.keys())
    # items() method does nice sorting in same order as RNA declaration
    for key, prop in mod_type.bl_rna.properties.items():
        if prop.is_readonly:
            continue
        # only use actual own properties
        if key in _modifier_base_props:
            continue
        if (mod_name, prop.identifier) in _fixed_value:
            # fixed value is set in the generator
            continue
        yield prop

def modifier_func_decls():
    for name, mt in modifier_types():
#        print("Modifier Type: %s (%r)" % (mt.bl_rna.identifier, name))
        props = []
        for prop in modifier_properties(name, mt):
            typedesc, is_struct, is_flag = typedesc_from_rna(prop)
#            print(typedesc, prop.identifier, is_struct)
            if typedesc is None:
                continue
            props.append((typedesc, prop.identifier, is_struct, is_flag))
        yield "mod_%s" % name.lower(), ModifierFunction(name, *props)

mod_funcs = { name : func for name, func in modifier_func_decls()}
