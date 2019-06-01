bl_info = { # TODO adapt to your project
    "name": "Example Addon",
    "category": "Add Mesh",
    "author": "Your Name",
    "version": (0, 0),
    }

import bpy
from .util import linkAndSelect
from .example import Example, generatorEnums, generatorMap

#############################################

# one way to generate your Evolvable
class GenerateExample(bpy.types.Operator):
    bl_idname = "mesh.generate_example"
    bl_label = "Generate Example"
    bl_options = {"REGISTER", "UNDO"}
    
    func = bpy.props.EnumProperty(
        name="Function",
        description="The generation function to use",
        items=generatorEnums
    )
    
    LOD = bpy.props.IntProperty(
        name="LOD",
        description="Level of Detail",
        default=16, min=3
    )
    
    count = bpy.props.IntProperty(
        name="Count",
        description="How many circles to generate",
        default=4, min=1
    )
   
    def execute(self, context):
        for pos in range(-self.count//2, self.count//2):
            exmpl = generatorMap[self.func]() # look up the generator and call it
            obj = exmpl.toMeshObject(self.LOD)
            obj.location = (pos, 0, 0)
            linkAndSelect(obj, context)
        return {'FINISHED'}

# you may wish to remove the default generator, by overwriting it
# if you do, your Operator will be registered by Example.registerOperators()
#Example._generateOperator = GenerateExample

#############################################
# un-/register formalities
#############################################

def register():
    Example.registerOperators()
    bpy.utils.register_class(GenerateExample)
    
def unregister():
    Example.unregisterOperators()
    bpy.utils.unregister_class(GenerateExample)

if __name__ == "__main__": # lets you run the script from a Blender text block; useful during development
    register()
