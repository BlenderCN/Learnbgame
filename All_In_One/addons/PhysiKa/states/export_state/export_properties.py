import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty
        )

class physika_export_properties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        cls.export_path = StringProperty(
            name = '',
            subtype='FILE_PATH'
        )
        
    @classmethod
    def unregister(cls):
        pass


    


def register():
    bpy.utils.register_class(physika_export_properties)
    bpy.types.Scene.physika_export = PointerProperty(type=physika_export_properties)
def unregister():
    bpy.utils.unregister_class(physika_export_properties)
    del bpy.types.Scene.physika_export
