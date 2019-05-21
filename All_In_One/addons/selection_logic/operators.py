import bpy
import bmesh
import numpy
from . parser import evaluate
from . conditions import getVariables
from bpy.props import IntProperty, StringProperty

def selectVertices(context):
    object = context.active_object
    mesh = bmesh.from_edit_mesh(object.data)
    variables = getVariables(object, mesh)
    try:
        result = evaluate(object.selection_expression, variables)
        object.invalid_expression = False
    except:
        object.invalid_expression = True
        return
    for face in mesh.faces:
        if all(result[vert.index] for vert in face.verts):
            face.select = True
        else:
            face.select = False
    for v, state in zip(mesh.verts, result):
        v.select = state
    bmesh.update_edit_mesh(object.data)

class AddSelectionConditionOperator(bpy.types.Operator):
    bl_idname = "mesh.add_selection_condition"
    bl_label = "Add Selection Condition"

    def execute(self, context):
        variables = "abcdefghijklmnopqrstuvwxyz"
        selectionCondition = context.active_object.selection_conditions.add()
        selectionCondition.identifier = str(hash(selectionCondition))
        usedNames = [condition.name for condition in context.active_object.selection_conditions]
        for var in variables:
            if var not in usedNames:
                selectionCondition.name = var
                break
        return {'FINISHED'}

class RemoveSelectionConditionOperator(bpy.types.Operator):
    bl_idname = "mesh.remove_selection_condition"
    bl_label = "Remove Selection Condition"
    index = IntProperty()

    def execute(self, context):
        object = context.active_object
        if object.selection_conditions[self.index].identifier in object.data:
            del object.data[object.selection_conditions[self.index].identifier]
        context.active_object.selection_conditions.remove(self.index)
        return {'FINISHED'}

class CollapsSelectionConditionOperator(bpy.types.Operator):
    bl_idname = "mesh.collapse_selection_condition"
    bl_label = "Remove Selection Condition"
    index = IntProperty()

    def execute(self, context):
        condition = context.active_object.selection_conditions[self.index]
        condition.expanded = False if condition.expanded else True
        return {'FINISHED'}

class UpdateSelectionMask(bpy.types.Operator):
    bl_idname = "mesh.update_selection_mask"
    bl_label = "Update Mask"
    index = IntProperty()

    def execute(self, context):
        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)
        mask = numpy.fromiter((vert.select for vert in bm.verts), numpy.int32)
        mesh[context.active_object.selection_conditions[self.index].identifier] = mask
        if context.active_object.auto_update:
            selectVertices(context)
        return {'FINISHED'}

classes = [AddSelectionConditionOperator, UpdateSelectionMask,
           RemoveSelectionConditionOperator, CollapsSelectionConditionOperator]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
