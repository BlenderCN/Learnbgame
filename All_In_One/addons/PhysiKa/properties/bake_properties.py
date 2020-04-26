import bpy,os
from bpy.props import(
    BoolProperty,
    StringProperty,
    PointerProperty,
    IntProperty
    
)

class PyhsikaBakeProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        
        cls.is_bake_finished = BoolProperty(default = False)
        cls.frame_start = IntProperty(default = -1)
        cls.frame_end = IntProperty(default = -1)
        # cls.num_frames = cls.frame_end - cls.frame_start + 1
        
    @classmethod    
    def unregister(cls):
        pass


def register():
    bpy.utils.register_class(PyhsikaBakeProperties)

def unregister():
    bpy.utils.unregister_class(PyhsikaBakeProperties)

