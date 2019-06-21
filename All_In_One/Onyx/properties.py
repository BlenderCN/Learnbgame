import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup
from .update import Update_ObjectOrigin, Update_ObjectVGOrigin

# Used to get the vertex groups of a selected object
def GetVertexGroups(scene, context):

    items = [
        ("1", "None",  "", 0),
    ]

    ob = bpy.context.active_object
    u = 1

    for i,x in enumerate(ob.vertex_groups):
        items.append((str(i+1), x.name, x.name))

    return items

# All properties relating to a specific object
class OX_Object(PropertyGroup):

    origin_point = EnumProperty(
        name="Set Object Origin",
        items=(
        ('1', 'Origin to Object Base', 'Sets the origin to the lowest point of the object, using the object Z axis.'),
        ('2', 'Origin to Lowest Point', 'Sets the origin to the lowest point of the object, using the scene Z axis'),
        ('3', 'Origin to Centre of Mass', 'Sets the origin using the objects centre of mass.'),
        ('4', 'Origin to Vertex Group', 'Sets the origin using a given vertex group'),
        ('5', 'Origin to 3D Cursor', 'Sets the origin using a given vertex group'),
        ),
        update = Update_ObjectOrigin
        )

    update_toggle = BoolProperty(
        name = "Update Toggle",
        description = "Prevents recursion loops in specific, multi-select operations",
        default = False
        )

    vertex_groups = EnumProperty(
        name="Select Vertex Group",
        items=GetVertexGroups,
        update=Update_ObjectVGOrigin
        )

class OX_Scene(PropertyGroup):

    update_toggle = BoolProperty(
        name = "Internal Update Toggle",
        description = "Used to prevent loop recursion when updating origins from the toolshelf menu.",
        default = False
        )
