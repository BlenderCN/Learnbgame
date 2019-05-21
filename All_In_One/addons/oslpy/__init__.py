from .osl_py_addin import ShaderNodeOSLPY
import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import sys
import importlib


bl_info = {
    "name": "OSLPY",
    "author": (
        "LazyDodo, "
     ),
    "version": (0, 0, 1, 1),
    "blender": (2, 7, 8),
    "location": "Nodes > Add nodes",
    "description": "OSL PY",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}

modulesNames = ['NodeGroupBuilder', 'Nodes','OpcodeBaseTypes','Opcodes','osl_py_addin','OSOInstruction','OSOReader','OSOVariable','StringBuilder']
 
modulesFullNames = {}
for currentModuleName in modulesNames:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    
class ExtraNodesCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == 'ShaderNodeTree' and
                context.scene.render.use_shading_nodes)


node_categories = [
    ExtraNodesCategory("SH_OSL_PY", "OslPY", items=[
        NodeItem("ShaderNodeOSLPY"),
        ]),
    ]


def register():
    bpy.utils.register_class(ShaderNodeOSLPY)
    nodeitems_utils.register_node_categories("SH_OSL_PY", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("SH_OSL_PY")
    bpy.utils.unregister_class(ShaderNodeOSLPY)


if __name__ == "__main__":
    register()
