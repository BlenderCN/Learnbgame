import bpy
from bpy.props import (PointerProperty,
                       StringProperty,
                       FloatVectorProperty)

class PathProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        
        bpy.types.Scene.vertexcolor = PointerProperty(
                name="Nif Vertex Color",
                description="Setting to import, edit, export vertex color",
                type=cls,
                )
                                                    
        #---operator parameters
        cls.fileinput = StringProperty(name='Input',
                                       subtype='FILE_PATH', 
                                       default="")   
        #TODO - add update=updatepath
              
        cls.fileoutput = StringProperty(name='Output', 
                                        subtype='FILE_PATH', 
                                        default="")
        
        cls.hexwidget = FloatVectorProperty(name='Hex Value', 
                                            subtype='COLOR', 
                                            default=[0.0,0.0,0.0])
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.vertexcolor

def register():
    bpy.utils.register_class(PathProperties)
    
def unregister():
    bpy.utils.unregister_class(PathProperties)