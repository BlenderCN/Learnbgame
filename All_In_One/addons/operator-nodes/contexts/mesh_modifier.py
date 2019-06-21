import bpy
import bmesh
from bpy.props import *
from . driver import DependencyChecker
from .. trees import DataFlowGroupTree
from .. utils.objects import get_objects_in_scene

modifier_type_items = [
    ("SINGLE_POINT", "Single Point", ""),
    ("OFFSET", "Offset", "")
]

class NodeMeshModifier(DependencyChecker, bpy.types.PropertyGroup):
    type: EnumProperty(name = "Modifier Type", default = "SINGLE_POINT",
        items = modifier_type_items)
    source_object: PointerProperty(type = bpy.types.Object, poll = lambda _, object: object.type == "MESH")

    enabled: BoolProperty(name = "Enabled", default = False)
    data_flow_group: PointerProperty(type = DataFlowGroupTree)

    def get_dependencies(self):
        return self.data_flow_group.get_dependencies({})

def evaluate_modifiers():
    for object in get_objects_in_scene(bpy.context.scene):
        if object.type == "MESH" and object.data.node_modifier.enabled:
            evaluate_modifier_on_mesh(object.data)

def evaluate_modifier_on_mesh(mesh):
    modifier = mesh.node_modifier
    if not modifier.dependencies_changed_since_last_check:
        return

    group = modifier.data_flow_group
    if group is None:
        return
    if not group.is_valid_function:
        return

    signature = group.signature


    if modifier.type == "SINGLE_POINT":
        evaluate_modifier__single_point(mesh, modifier)
    elif modifier.type == "OFFSET":
        evaluate_modifier__offset(mesh, modifier)

def evaluate_modifier__single_point(mesh, modifier):
    clear_mesh(mesh)
    group = modifier.data_flow_group
    signature = group.signature

    if not signature.match_output(["Vector"]):
        raise Exception("output type should be a single vector")

    if signature.match_input([]):
        value = group.function()
        mesh.from_pydata([value], [], [])
    else:
        raise Exception("should have no input")

def evaluate_modifier__offset(mesh, modifier):
    group = modifier.data_flow_group
    signature = group.signature

    if not signature.match_output(["Vector"]):
        raise Exception("output type should be a single vector")
    if not signature.match_input(["Vector"]):
        raise Exception("input type should be a single vector")
    if modifier.source_object is None:
        return

    function = group.function
    bm = bmesh.new()
    bm.from_mesh(modifier.source_object.data)

    for vertex in bm.verts:
        vertex.co = function(vertex.co)

    bm.to_mesh(mesh)
    bm.free()

def clear_mesh(mesh):
    bmesh.new().to_mesh(mesh)


property_groups = [
    NodeMeshModifier
]

def register():
    for cls in property_groups:
        bpy.utils.register_class(cls)
    bpy.types.Mesh.node_modifier = PointerProperty(type = NodeMeshModifier)

def unregister():
    del bpy.types.Mesh.node_modifier
    for cls in property_groups:
        bpy.utils.unregister_class(cls)