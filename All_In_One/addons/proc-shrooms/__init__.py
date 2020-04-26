bl_info = {
    "name": "ShroomGen",
    "category": "Object",
    "author": "Rafael",
    "version": (1, 0),
    }

import bpy
from .util import optional, linkAndSelect
from .shroom import MushroomProps, Mushroom, MushroomPG, generatorEnums, generatorMap
from .spline import asEdgeObject

#############################################
    
class GrowShroom(bpy.types.Operator):
    bl_idname = "mesh.shroom_generate"
    bl_label = "Generate Mushroom(s)"
    bl_options = {"REGISTER", "UNDO"}
    
    func = bpy.props.EnumProperty(
        name="Function",
        description="The generation function to use",
        items=generatorEnums
    )
    
    LODr = bpy.props.IntProperty(
        name="LOD radius",
        description="Number of samples in radial direction",
        default=10, min=2
    )
    
    LODp = bpy.props.IntProperty(
        name="LOD phi",
        description="Number of samples in angular direction",
        default=16, min=3
    )
    
    count = bpy.props.IntProperty(
        name="Count",
        description="How many mushrooms to generate",
        default=4, min=1
    )
    
    noise = bpy.props.BoolProperty(
        name="Noise",
        description="Adds some irregularities to the mushroom",
        default=False)
    
    exportCrossSec = bpy.props.BoolProperty(
        name="Cross Section",
        description="Create an Object for the cross section",
        default=False)
    exportMesh = bpy.props.BoolProperty(
        name="Mesh",
        description="Create an Object for the mesh",
        default=True)
   
    def execute(self, context):
        for pos in range(-self.count//2, self.count//2):
            shroom = generatorMap[self.func]()
            
            if self.exportCrossSec:
                obj = asEdgeObject(shroom.upperHat(), shroom.lowerHat(), shroom.shaft(), LOD=self.LODr)
                obj.location = (pos, 0, 0)
                shroom.store(obj.mushroom)
                linkAndSelect(obj, context)
                obj = asEdgeObject(shroom.shaftRadiusSpline(), LOD=self.LODr)
                obj.location = (pos, 0, 0)
                linkAndSelect(obj, context)
            if self.exportMesh:
                obj = shroom.toMeshObject(self.LODr, self.LODp, self.noise)
                obj.location = (pos, 0, 0)
                linkAndSelect(obj, context)
        
        return {'FINISHED'}

#############################################

class EvolveShroom(bpy.types.Operator):
    bl_idname = "mesh.shroom_evolve"
    bl_label = "Mutate Mushroom"
    bl_options = {"REGISTER", "UNDO"}
    
    count = bpy.props.IntProperty(
        name="Variations",
        description="How many different mushrooms to generate from this one",
        default=4, min=1
    )
    
    radiation = bpy.props.FloatProperty(
        name="Radiation",
        description="Strength of mutation",
        default=70, step=100,
        min=0, max=100
    )
    
    def execute(self, context):
        shroom = Mushroom.load(context.object.mushroom)
        for _ in range(self.count):
            newShroom = shroom.mutate(self.radiation)
            obj = newShroom.toMeshObject(10, 16)
            obj.location = context.object.location
            obj.location[1] += 1
            linkAndSelect(obj, context)
        return {'FINISHED'}

#############################################

class EditShroom(bpy.types.Operator, MushroomProps):
    bl_idname = "mesh.shroom_edit"
    bl_label = "Edit Mushroom"
    bl_options = {"REGISTER", "UNDO"}
    
    LODr = GrowShroom.LODr
    LODp = GrowShroom.LODp
    noise = GrowShroom.noise
        
    def invoke(self, context, event):
        if context.object is not None:
            Mushroom.load(context.object.mushroom).store(self)
        return self.execute(context)
    
    def execute(self, context):
        shroom = Mushroom.load(self)
        obj = shroom.toMeshObject(self.LODr, self.LODp, self.noise)
        obj.location = optional(context.object, obj).location
        obj.location[1] += 1
        linkAndSelect(obj, context)
        return {'FINISHED'}

#############################################

class CombineShrooms(bpy.types.Operator):
    bl_idname = "mesh.shroom_combine"
    bl_label = "Combine Mushrooms"
    bl_options = {"REGISTER", "UNDO"}
    
    count = bpy.props.IntProperty(
        name="Offspring",
        description="How many mushrooms to generate",
        default=2, min=1
    )
    
    def execute(self, context):
        parents = [co.mushroom for co in context.selected_objects]
        for i in range(self.count):
            shroom = Mushroom.procreate(*parents)
            obj = shroom.toMeshObject(10, 16, False)
            obj.location = optional(context.object, obj).location
            obj.location[1] += 1
            linkAndSelect(obj, context)
        return {'FINISHED'}
    
#############################################
# un-/register formalities
#############################################

def register():
    bpy.utils.register_class(MushroomPG)
    bpy.utils.register_class(GrowShroom)
    bpy.utils.register_class(EditShroom)
    bpy.utils.register_class(EvolveShroom)
    bpy.utils.register_class(CombineShrooms)
    bpy.types.Object.mushroom = bpy.props.PointerProperty(type=MushroomPG)
    
def unregister():
    bpy.utils.unregister_class(GrowShroom)
    bpy.utils.unregister_class(EditShroom)
    bpy.utils.unregister_class(EvolveShroom)
    bpy.utils.unregister_class(CombineShrooms)
    bpy.utils.unregister_class(MushroomPG)
    del bpy.types.Object.mushroom

if __name__ == "__main__":
    register()
