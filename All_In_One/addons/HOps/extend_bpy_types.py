import bpy
from bpy.props import EnumProperty, PointerProperty, IntProperty, BoolProperty, FloatProperty
from . utils.objects import get_modifier_with_type


def register():
    bpy.types.Object.hops = PointerProperty(name="HardOps Properties", type=HOpsObjectProperties)


def unregister():
    del bpy.types.Object.hops


status_items = [
    ("UNDEFINED", "Undefined", "", "NONE", 0),
    ("CSHARP", "CSharp", "", "NONE", 1),
    ("CSTEP", "CStep", "", "NONE", 2),
    ("BOOLSHAPE", "BoolShape", "", "NONE", 3),
    ("BOOLSHAPE2", "BoolShape2", "", "NONE", 4)]


class HOpsObjectProperties(bpy.types.PropertyGroup):

    status: EnumProperty(name="Status", default="UNDEFINED", items=status_items)
    adaptivesegments: IntProperty("Adaptive Segments", default=3, min=-10, max=25)

    def get_is_pending_boolean(self):
        return get_modifier_with_type(self.id_data, "BOOLEAN") is not None

    is_pending_boolean: BoolProperty(name="Is Pending Boolean", get=get_is_pending_boolean)
    is_global: BoolProperty(name="Is Global", default=True)

    array_x: FloatProperty(name="Array gizmo x", description="Array gizmo x", default=0)
    array_y: FloatProperty(name="Array gizmo y", description="Array gizmo y", default=0)
    array_z: FloatProperty(name="Array gizmo z", description="Array gizmo z", default=0)
