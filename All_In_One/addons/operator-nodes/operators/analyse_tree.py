import bpy
from pprint import pprint
from .. contexts.driver import evaluate_drivers
from .. trees.data_flow_group import find_possible_external_values, find_dependencies, find_required_sockets

class AnalyseTreeOperator(bpy.types.Operator):
    bl_idname = "en.analyse_tree"
    bl_label = "Analyse Tree"

    def execute(self, context):
        tree = context.space_data.node_tree
        evaluate_drivers()
        return {"FINISHED"}

