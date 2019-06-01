import bpy
import random
import math
from .util import optional, optionalKey, clip, linkAndSelect, isIterable
from bpy.props import *


class Evolvable:
    """
    Base class for objects with evolvable properties. The properties need to be specified as bpy.props .
    Generalised methods for loading, storing, mutation and combination of evolvables objects are provided.
    Blender operators for using these methods are provided, too.
    See example.py for more info on usage.
    """

    def __init__(self, **kwargs):
        """
        Initialises all properties of the object with their default.
        Different values can be set through the kwargs. These will be clamped to the property's range (if applicable).
        """
        props = properties(self.__class__)
        for name, params in props.items():
            setattr(self, name, params["default"])
            
        for kw in kwargs:
            setattr(self, kw, propClamp(kwargs[kw], props[kw]))
    
    def store(self, obj):
        """Store all properties of self into the given object. If obj is a dict, the properties are stored as key/value, otherwise as attributes."""
        for name in properties(self.__class__).keys():
            if type(obj) is dict:
                obj[name] = getattr(self, name)
            else:
                setattr(obj, name, getattr(self, name))

    @classmethod
    def load(cls, obj):
        """Construct a new object from the values stored in a dict(via keys) or a general object(via attributes)."""
        return cls(**dict( filter(lambda p: p[1] is not None, 
            map(lambda n: (n, optionalKey(obj, n)), properties(cls).keys())) ))

    def toMeshObject(self, *args, **kwargs):
        """
        Create a Blender bpy.data.objects instance from the result of the toMesh method.
        The mesh name is also used for the object. This Evolvable is stored in the object.
        Any parameters to this method are passed on to toMesh.
        """
        newMesh = self.toMesh(*args, **kwargs)
        obj = bpy.data.objects.new(newMesh.name, newMesh)
        self.store(getattr(obj, self.__class__.identifier))
        return obj

    def mutate(self, radiation):
        """mutate a new object from this one. parameter radiation must be positive and should not be larger than 100"""
        assert(radiation >= 0)
        
        props = properties(self.__class__)
        nprops = len(props)
        
        nmutations = clip(round(random.gauss(nprops*radiation/200, math.sqrt(nprops))), 1, nprops)
        mutatingProps = random.sample(props.items(), nmutations)
        radiation /= math.sqrt(nmutations) # the more aspects change, the less each of them changes
        
        descendant = self.__class__.load(self)
        for name, params in mutatingProps:
            current = getattr(descendant, name)
            if params["type"] in (FloatVectorProperty, IntVectorProperty, BoolVectorProperty):
                idx = random.randrange(params["size"]) # evolve only one entry of a vector
            
            if params["type"] is BoolProperty:
                newVal = (not current) if radiation/100 < random.random() else current
            elif params["type"] is BoolVectorProperty:
                newVal = current.copy()
                newVal[idx] = (not current[idx]) if radiation/100 < random.random() else current[idx]
                
            elif params["type"] in (FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty):
                dtype = float if params["type"] in (FloatProperty, FloatVectorProperty) else int
                span = optionalKey(params, "soft_max", optionalKey(params, "max")) - optionalKey(params, "soft_min", optionalKey(params, "min"))
                span *= radiation/100 # percent to factor
                
                def fuzzyClamp(val, curr): # clamp that allows flowing over soft min/max with some probability
                    val = propClamp(val, params)
                    # if val exceeds the soft bounds, chances decrease to go further away
                    if optionalKey(params, "soft_min") is not None and val < params["soft_min"] and val < curr:
                        if random.random() < span/(span + params["soft_min"] - val):
                            return val
                        return curr if curr < params["soft_min"] else params["soft_min"]
                    if optionalKey(params, "soft_max") is not None and val > params["soft_max"] and val > curr:
                        if random.random() < span/(span + val - params["soft_max"]):
                            return val
                        return curr if curr > params["soft_max"] else params["soft_max"]
                    return val

                if params["type"] in (FloatProperty, IntProperty):
                    newVal = fuzzyClamp(random.gauss(current, span), current)
                elif params["type"] in (FloatVectorProperty, IntVectorProperty):
                    newVal = current.copy()
                    newVal[idx] = fuzzyClamp(random.gauss(current[idx], span), current[idx])
            else:
                raise Exception("Property type "+str(prop["type"])+" not supported.")
            
            setattr(descendant, name, newVal)
        
        return descendant

    @classmethod
    def procreate(cls, *geneSeeds):
        """
        Creates a new object from given examples. Specify at least 2 examples.
        Each property of the result will either be taken from an example or averaged over all examples.
        """
        assert len(geneSeeds) > 1, "Specify at least 2 seeds"
        # None gene leads to averaging; it occurs less often with many seeds to keep diversity
        genePool = geneSeeds + (None,)
        child = cls()
        for name, prop in properties(cls).items():
            gene = random.choice(genePool)
            if gene is None:
                if prop["type"] in (FloatProperty, FloatVectorProperty):
                    dtype = float
                elif prop["type"] in (IntProperty, IntVectorProperty):
                    dtype = int
                elif prop["type"] in (BoolProperty, BoolVectorProperty):
                    # flip a coin if equally distributed, else take majority
                    dtype = lambda x: random.random() > .5 if x == .5 else x > .5
                
                if prop["type"] in (FloatVectorProperty, IntVectorProperty, BoolVectorProperty):
                    val = [0]*prop['size']
                    for i in range(prop['size']):
                        val[i] = dtype( sum(optionalKey(p, name, prop['default'])[i] for p in geneSeeds) / len(genePool) )
                    setattr(child, name, val)
                elif prop["type"] in (FloatProperty, IntProperty, BoolProperty):
                    val = dtype( sum(optionalKey(p, name, prop['default']) for p in geneSeeds) / len(genePool) )
                    setattr(child, name, val)
                else:
                    raise Exception("Property type "+str(prop["type"])+" not supported.")
            else:
                setattr(child, name, optionalKey(gene, name, prop['default']))
        return child
    
    @classmethod
    def registerOperators(cls):
        assert cls.label and type(cls.label) is str, "a string label for the UI is required"
        assert cls.identifier and type(cls.identifier) is str, "a string identifier for the Blender IDs"
        
        # check for None to allow setting custom generators and to avoid constructing them twice
        if optionalKey(cls, "_generateOperator") is None:
            cls._generateOperator = generateOperator(cls, cls.label, cls.identifier)
        if optionalKey(cls, "_mutationOperator") is None:
            cls._mutationOperator = mutationOperator(cls, cls.label, cls.identifier)
        if optionalKey(cls, "_editOperator") is None:
            cls._editOperator = editOperator(cls, cls.label, cls.identifier)
        if optionalKey(cls, "_combineOperator") is None:
            cls._combineOperator = combineOperator(cls,cls.label, cls.identifier)
        class EvPropGroup(bpy.types.PropertyGroup, cls):
            pass
        
        bpy.utils.register_class(EvPropGroup)
        setattr(bpy.types.Object, cls.identifier, PointerProperty(type=EvPropGroup))
        bpy.utils.register_class(cls._generateOperator)
        bpy.utils.register_class(cls._mutationOperator)
        bpy.utils.register_class(cls._editOperator)
        bpy.utils.register_class(cls._combineOperator)
    
    @classmethod
    def unregisterOperators(cls):
        delattr(bpy.types.Object, cls.identifier)
        bpy.utils.unregister_class(EvPropGroup)
        bpy.utils.unregister_class(cls._generateOperator)
        bpy.utils.unregister_class(cls._mutationOperator)
        bpy.utils.unregister_class(cls._editOperator)
        bpy.utils.unregister_class(cls._combineOperator)

#############################################

class SimpleGenerator:
    """Generator for an Evolvable that just picks all parameters uniformly from their valid range."""
    
    def __init__(self, evolvable):
        self.evolvable = evolvable
    
    @staticmethod
    def randProp(prop):
        def pickUniform(prop):
            validRange = optionalKey(prop, "soft_max", optionalKey(prop, "max")), optionalKey(prop, "soft_min", optionalKey(prop, "min"))
            return random.uniform(*validRange)
        
        if prop["type"] is FloatProperty:
            return pickUniform(prop)
        elif prop["type"] is IntProperty:
            return int(pickUniform(prop))
        elif prop["type"] is BoolProperty:
            return random.random() > .5
        elif prop["type"] is FloatVectorProperty:
            return [ pickUniform(prop) for _ in range(prop["size"]) ]
        elif prop["type"] is IntVectorProperty:
            return [ int(pickUniform(prop)) for _ in range(prop["size"]) ]
        elif prop["type"] is BoolVectorProperty:
            return [ random.random() > .5 for _ in range(prop["size"]) ]
        raise Exception("Property type "+str(prop["type"])+" not supported.")
    
    def __call__(self):
        return self.evolvable( **{
            name : SimpleGenerator.randProp(prop) for name, prop in properties(self.evolvable).items()
            })

#############################################

def generateOperator(evolvable, label, identifier):
    class Generate(bpy.types.Operator):
        bl_idname = "mesh.random_"+identifier
        bl_label = "Random "+label
        bl_options = {"REGISTER", "UNDO"}

        count = IntProperty(
            name="Count",
            description="How many "+label+"s to generate",
            default=4, min=1
        )
        
        generator = SimpleGenerator(evolvable)
   
        def execute(self, context):
            for pos in range(-self.count//2, self.count//2):
                newEvObj = self.generator()
                blObj = newEvObj.toMeshObject()
                blObj.location = (pos, 0, 0)
                linkAndSelect(blObj, context)
            return {'FINISHED'}
    return Generate

#############################################

def mutationOperator(evolvable, label, identifier):
    class Mutate(bpy.types.Operator):
        bl_idname = "mesh.mutate_"+identifier
        bl_label = "Mutate "+label
        bl_options = {"REGISTER", "UNDO"}

        count = IntProperty(
            name="Variations",
            description="How many different objects to generate from this one",
            default=4, min=1
        )

        radiation = FloatProperty(
            name="Radiation",
            description="Strength of mutation",
            default=70, step=100,
            min=0, max=100
        )

        def execute(self, context):
            evObj = evolvable.load(getattr(context.object, identifier))
            for _ in range(self.count):
                newEvObj = evObj.mutate(self.radiation)
                blObj = newEvObj.toMeshObject()
                blObj.location = context.object.location
                blObj.location[1] += 1
                linkAndSelect(blObj, context)
            return {'FINISHED'}
    return Mutate

#############################################

def editOperator(evolvable, label, identifier):
    class Edit(bpy.types.Operator, evolvable):
        bl_idname = "mesh.edit_"+identifier
        bl_label = "Edit "+label
        bl_options = {"REGISTER", "UNDO"}
        
        def invoke(self, context, event):
            if context.object is not None:
                evolvable.load(getattr(context.object, identifier)).store(self)
            return self.execute(context)
        
        def execute(self, context):
            evObj = evolvable.load(self)
            blObj = evObj.toMeshObject()
            blObj.location = optional(context.object, blObj).location
            blObj.location[1] += 1
            linkAndSelect(blObj, context)
            return {'FINISHED'}
    return Edit

#############################################

def combineOperator(evolvable, label, identifier):
    class Combine(bpy.types.Operator):
        bl_idname = "mesh.combine_"+identifier
        bl_label = "Combine "+label+"s"
        bl_options = {"REGISTER", "UNDO"}
        
        count = IntProperty(
            name="Offspring",
            description="How many objects to generate",
            default=2, min=1
        )
        
        def execute(self, context):
            parents = [getattr(co, identifier) for co in context.selected_objects]
            for i in range(self.count):
                evObj = evolvable.procreate(*parents)
                blObj = evObj.toMeshObject()
                blObj.location = optional(context.object, blObj).location
                blObj.location[1] += 1
                linkAndSelect(blObj, context)
            return {'FINISHED'}
    return Combine

#############################################
# utils
#############################################

def mergeTypeInfo(propTuple):
    result = propTuple[1].copy()
    result["type"] = propTuple[0]
    return result

def properties(props):
    """extract a dictionary mapping names to Blender properties (which are represented as dictionaries)"""
    return dict(
        # pack name and config dict together
        map( lambda p: (p[0], mergeTypeInfo(p[1])),
            # pick those where the attribute value is a Blender Property tuple, i.e. has the form (property type, dict with config)
            # type(bpy.props.*) is the same for all properties
            filter( lambda v: type(v[1]) is tuple and len(v[1]) == 2 and type(v[1][0]) is type(FloatProperty),
                # get tuples (name, attribute value)
                ( (n, getattr(props, n)) for n in dir(props) )
    )))

def propClamp(value, prop, soft=False):
    ptype = prop["type"]
    
    if ptype in (FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty):
        dtype = float if ptype in (FloatProperty, FloatVectorProperty) else int
        
        # we might just clamp one entry of a vector property, so we need to check, whether an iterable was given
        if ptype in (FloatVectorProperty, IntVectorProperty) and isIterable(value):
            return [ propClamp(val, prop, soft) for val in value ]
        else:
            value = dtype(value)
            minv = optionalKey(prop, "soft_min" if soft else "min", value)
            maxv = optionalKey(prop, "soft_max" if soft else "max", value)
            return clip(value, minv, maxv)
    
    if ptype is BoolVectorProperty and isIterable(value):
        return [ bool(val) for val in value ]
    if ptype in (BoolProperty, BoolVectorProperty):
        return bool(value)
    
    if ptype is StringProperty:
        return str(value)[:optionalKey(prop, "maxlen", -1)]
    
    raise Exception("Property type "+str(ptype)+" not supported.")
