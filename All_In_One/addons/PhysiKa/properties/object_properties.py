if "bpy" in locals():
    import importlib
    reloadable_modules = [
        'bake_properties'
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])

import bpy
from bpy.props import(
    BoolProperty,
    EnumProperty,
    PointerProperty,
    StringProperty
)
from . import(
    bake_properties,
    state_properties
)


from .. import types
class PhysiKaObjectProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.physika = PointerProperty(
            name="PhysiKa Object Properties",
            description="",
            type=cls
        )
        

        cls.is_active = BoolProperty(default=False)
        cls.bake = PointerProperty(
            name = 'Physika Bake Properties',
            description = '',
            type = bake_properties.PyhsikaBakeProperties   
        )
        

        cls.state = StringProperty(default = 'obstacle')
        cls.enable_constraint = BoolProperty(default = False)

        cls.obstacles = None
        
    @classmethod    
    def unregister(cls):
        del bpy.types.Object.physika


        
def register():
    bake_properties.register()
    bpy.utils.register_class(PhysiKaObjectProperties)
    

def unregister():
    bake_properties.unregister()
    bpy.utils.unregister_class(PhysiKaObjectProperties)
