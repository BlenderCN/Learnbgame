import bpy
from bpy.props import (
    PointerProperty,
    CollectionProperty,
    IntProperty,
    BoolProperty,
    StringProperty
)
from ...properties.object_properties import PhysiKaObjectProperties





class physika_obj_ptr(bpy.types.PropertyGroup):
    obj_ptr = PointerProperty(
        name = "Obj_Pointer",
        type = bpy.types.Object
    )


class physika_obstacles(bpy.types.PropertyGroup):
    def scene_chosenobject_poll(self, object):
        physika_obj = bpy.context.scene.objects.active
        physika_obj_name = physika_obj.name
        return object.type == 'MESH' and object.name != physika_obj_name and eval("object.physika." + physika_obj_name.replace('.','_') +  "_obstacle == False")

    @classmethod
    def register(cls):
        PhysiKaObjectProperties.obstacles = PointerProperty(
            name="PhysiKa Obstacles",
            type= cls
        )



    objs = CollectionProperty(
            type = physika_obj_ptr
        )
    index = IntProperty(default = -1)

    chosen_obj = PointerProperty(
        name = "choose obstacle",
        type = bpy.types.Object,
        poll = scene_chosenobject_poll
    )

def register():

    bpy.utils.register_class(physika_obj_ptr)
    bpy.utils.register_class(physika_obstacles)
    # setattr(bpy.types.Object.physika, 'obstacles', PointerProperty(
    #     name="PhysiKa Obstacles",
    #     type = physika_obstacles
    # ))

def unregister():
    bpy.utils.unregister_class(physika_obj_ptr)
    bpy.utils.unregister_class(physika_obstacles)
