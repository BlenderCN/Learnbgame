import bpy
from . tree_info import tag_update
from . execution import TreeExecutionData

execution_data_by_hash = dict()

class ComputeNodeTree(bpy.types.NodeTree):
    bl_idname = "cn_ComputeNodeTree"
    bl_label = "Compute"
    bl_icon = "SCRIPTPLUGINS"

    def update(self):
        tag_update(self)
        self.remove_execution_data()

    def remove_execution_data(self):
        execution_data_by_hash.pop(hash(self), None)

    def ensure_execution_data(self):
        if hash(self) not in execution_data_by_hash:
            execution_data_by_hash[hash(self)] = TreeExecutionData(self)

    def get_function(self):
        self.ensure_execution_data()
        return execution_data_by_hash[hash(self)].get_function()

    def print_modules(self):
        self.ensure_execution_data()
        execution_data_by_hash[hash(self)].print_modules()

    def print_assembly(self):
        self.ensure_execution_data()
        execution_data_by_hash[hash(self)].print_module_assembly()
