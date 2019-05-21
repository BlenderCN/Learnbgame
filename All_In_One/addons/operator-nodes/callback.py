import bpy

from . utils.strings import get_random_string

callback_by_identifier = {}

def new_callback(function):
    identifier = get_random_string(10)
    callback_by_identifier[identifier] = function
    return identifier

def insert_callback(identifier, function):
    callback_by_identifier[identifier] = function

def new_parameterized_callback(identifier, *parameters):
    return "#" + repr((identifier, parameters))

def execute_callback(identifier, *args, **kwargs):
    if identifier.startswith("#"):
        real_identifier, parameters = eval(identifier[1:])
        callback = callback_by_identifier[real_identifier]
        callback(*parameters, args, kwargs)
    else:
        callback = callback_by_identifier[identifier]
        callable(*args, **kwargs)



# Node Callback Utils
################################################

node_callback_name = "execute_node_callback"

def get_node_callback(node, function_name):
    return new_parameterized_callback(node_callback_name, 
            function_name, node.id_data.name, node.name)

def execute_node_callback(function_name, tree_name, node_name, args, kwargs):
    node = bpy.data.node_groups[tree_name].nodes[node_name]
    getattr(node, function_name)(*args, **kwargs)

insert_callback(node_callback_name, execute_node_callback)