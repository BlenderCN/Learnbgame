import bpy
from . actions_tree import ActionsTree
from . data_flow_group import DataFlowGroupTree
from . particle_system import ParticleSystemTree
from . operators_tree import OperatorsTree

tree_types = [
    ActionsTree,
    DataFlowGroupTree,
    ParticleSystemTree,
    OperatorsTree
]

def register():
    for cls in tree_types:
        bpy.utils.register_class(cls)

def unregister():
    for cls in tree_types:
        bpy.utils.unregister_class(cls)