import bpy
from bpy.props import *
from .. trees import DataFlowGroupTree
from .. utils.objects import get_objects_in_scene

class DependencyChecker:
    last_dependency_state: StringProperty()

    @property
    def dependencies_changed_since_last_check(self):
        current_state = self.get_dependency_state()
        if current_state != self.last_dependency_state:
            self.last_dependency_state = current_state
            return True
        return False

    def get_dependency_state(self):
        data = list()
        for dependency in self.get_dependencies():
            data.append(hash(dependency))
            data.append(dependency.evaluate())
        return str(hash(str(data)))

    def get_dependencies(self):
        raise NotImplementedError()

class NodeDriver(DependencyChecker, bpy.types.PropertyGroup):
    path: StringProperty()
    data_flow_group: PointerProperty(type = DataFlowGroupTree)

    def get_dependencies(self):
        signature = self.data_flow_group.signature
        if signature.match_input(["Object"]):
            return self.data_flow_group.get_dependencies({signature.inputs[0] : self.id_data})
        else:
            return self.data_flow_group.get_dependencies({})



def evaluate_drivers():
    for object in get_objects_in_scene(bpy.context.scene):
        evaluate_drivers_on_object(object)

def evaluate_drivers_on_object(object):
    for driver in object.node_drivers:
        group = driver.data_flow_group
        if group is None:
            continue
        if not group.is_valid_function:
            continue
        if not driver.dependencies_changed_since_last_check:
            continue

        signature = group.signature
        if not signature.match_output([get_data_type(driver.path)]):
            raise Exception("output type of function does not match the property")
        if signature.match_input([]):
            value = group.function()
        elif signature.match_input(["Object"]):
            value = group.function(object)
        exec(f"object.{driver.path} = value", {"object" : object, "value" : value})

def get_data_type(path):
    if path in {"location", "scale"}:
        return "Vector"
    elif path in {"location.x", "location.y", "location.z"}:
        return "Float"
    else:
        raise Exception(f"type of property '{path}' is unknown")



property_groups = [
    NodeDriver
]

def register():
    for cls in property_groups:
        bpy.utils.register_class(cls)
    bpy.types.Object.node_drivers = CollectionProperty(type = NodeDriver)

def unregister():
    del bpy.types.Object.node_drivers
    for cls in reversed(property_groups):
        bpy.utils.unregister_class(cls)