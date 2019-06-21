import bpy

from bpy.props import (
    EnumProperty,
    PointerProperty,
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    )

from bpy.types import (
    Panel, 
    Operator,
    Menu,
    PropertyGroup,
    SpaceView3D,
    WindowManager,
    )

from bpy.utils import (
    previews,
    register_class,
    unregister_class
    )

class SimpleGenerator:
    """Generator for an Evolvable that just picks all parameters uniformly from their valid range."""
    
    #def __init__(self, evolvable):
        #self.evolvable = evolvable
    
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
    
    #def __call__(self):
        #return self.evolvable( **{
            #name : SimpleGenerator.randProp(prop) for name, prop in properties(self.evolvable).items()
            #})


class GENERATE_OT_FRUIT(Operator):
    bl_idname = "mesh.random_fruit"
    bl_label = "Random Fruit"
    bl_options = {"REGISTER", "UNDO"}

    count : IntProperty(
        name="Count",
        description="How many fruits to generate",
        default=4, min=1
    )
    generator = SimpleGenerator()
    def execute(self, context):
        for pos in range(-self.count//2, self.count//2):
            newEvObj = self.generator
            blObj = newEvObj.toMeshObject()
            blObj.location = (pos, 0, 0)
            linkAndSelect(blObj, context)
        return {'FINISHED'}


#############################################


class MUTATE_OT_FRUIT(Operator):
    bl_idname = "mesh.mutate_fruit"
    bl_label = "Mutate Fruit"
    bl_options = {"REGISTER", "UNDO"}

    count : IntProperty(
        name="Variations",
        description="How many different objects to generate from this one",
        default=4, min=1
    )

    radiation : FloatProperty(
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
    

#############################################


class EDIT_OT_FRUIT(Operator):
    bl_idname = "mesh.edit_fruit"
    bl_label = "Edit Fruit"
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
    

#############################################



class COMBINE_OT_FRUIT(Operator):
    bl_idname = "mesh.combine_fruit"
    bl_label = "Combine Fruits"
    bl_options = {"REGISTER", "UNDO"}
    
    count : IntProperty(
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

classes = (
    GENERATE_OT_FRUIT,
    MUTATE_OT_FRUIT,
    EDIT_OT_FRUIT,
    COMBINE_OT_FRUIT,
    )

def register():
    for cla in classes:
        register_class(cla)
def unregister():
    for cla in classes:
        unregister_class(cla)
