import bpy
from bpy.props import StringProperty, IntProperty, PointerProperty, BoolProperty, CollectionProperty, FloatVectorProperty
import mathutils
from . utils.support import flatten_matrix


class MMStash(bpy.types.PropertyGroup):
    name = StringProperty()
    index = IntProperty()
    obj = PointerProperty(name="Stash Object", type=bpy.types.Object)

    flipped = BoolProperty(name="Flipped Normals", default=False)

    mark_delete = BoolProperty(default=False)


class MMObjectProperties(bpy.types.PropertyGroup):
    stashes = CollectionProperty(type=MMStash)
    active_stash_idx = IntProperty()

    isstashobj = BoolProperty(name="is stash object", default=False)
    stashmx = FloatVectorProperty(name="Stash Matrix", subtype="MATRIX", size=16, default=flatten_matrix(mathutils.Matrix()))
    stashtargetmx = FloatVectorProperty(name="Target Matrix", subtype="MATRIX", size=16, default=flatten_matrix(mathutils.Matrix()))

    uuid = StringProperty(name="plug uuid")
    isplug = BoolProperty(name="is plug", default=False)
    isplughandle = BoolProperty(name="is plug handle", default=False)
    isplugdeformer = BoolProperty(name="is plug deformer", default=False)
    isplugsubset = BoolProperty(name="is plug subset", default=False)
    isplugoccluder = BoolProperty(name="is plug occluder", default=False)

    hasfillet = BoolProperty(name="has fillet", default=False)
    deformerprecision = IntProperty(name="Deformer Precision", default=4)
    usedeformer = BoolProperty(name="Use Deformer", default=False)

    forcesubsetdeform = BoolProperty(name="Force Subset Deform", default=False)

    plugcreator = StringProperty(name="Plug Creator")


class MMPlugEmpties(bpy.types.PropertyGroup):
    name = StringProperty()
    index = IntProperty()
    location = FloatVectorProperty(name="Location")


class MMPlugScales(bpy.types.PropertyGroup):
    name = StringProperty()
    index = IntProperty()
    scale = FloatVectorProperty(name="Scale")
    empties = CollectionProperty(type=MMPlugEmpties)


class MMSceneProperties(bpy.types.PropertyGroup):
    plugscales = CollectionProperty(type=MMPlugScales)
