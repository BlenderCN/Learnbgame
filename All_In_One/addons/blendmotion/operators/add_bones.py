import bpy

from blendmotion.core.rigging import add_bones
from blendmotion.error import OperatorError, error_and_log

class SelectAndAddBonesOperator(bpy.types.Operator):
    bl_idname = 'bm.select_and_add_bones'
    bl_label = 'Select base object'

    def list_objects(self, context):
        return [(name, name, name) for name, o in context.scene.objects.items() if o.type == 'ARMATURE']

    base_object_name = bpy.props.EnumProperty(name='Object', description=bl_label, items=list_objects)

    def execute(self, context):
        if self.base_object_name not in bpy.data.objects:
            return error_and_log(self, 'object "{}" not found'.format(self.base_object_name))

        obj = bpy.data.objects[self.base_object_name]
        try:
            add_bones(obj)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class AddBonesOperator(bpy.types.Operator):
    bl_idname = "mesh.addbmbones"
    bl_label  = "Kinematic Bones on Phobos model"
    bl_description = "Add kinematic bones on phobos model from selected mesh"
    bl_options = {'REGISTER', 'UNDO'}

    with_ik = bpy.props.BoolProperty(name="Enable IK", default=True)

    def execute(self, context):
        if len(context.selected_objects) == 0:
            return bpy.ops.bm.select_and_add_bones('INVOKE_DEFAULT')

        if len(context.selected_objects) != 1:
            return error_and_log(self, 'Single object must be selected')

        obj = context.selected_objects[0]
        try:
            add_bones(obj, with_ik=self.with_ik)
        except OperatorError as e:
            e.report(self)
            e.log()
            return {'CANCELLED'}

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.separator()
    o1 = self.layout.operator(AddBonesOperator.bl_idname, icon='GROUP_BONE', text=AddBonesOperator.bl_label)
    o1.with_ik = False
    o2 = self.layout.operator(AddBonesOperator.bl_idname, icon='CONSTRAINT_BONE', text=AddBonesOperator.bl_label + " (with IK)")
    o2.with_ik = True

def register():
    bpy.types.INFO_MT_armature_add.append(menu_func)
    bpy.utils.register_class(SelectAndAddBonesOperator)
    bpy.utils.register_class(AddBonesOperator)

def unregister():
    bpy.types.INFO_MT_armature_add.remove(menu_func)
    bpy.utils.unregister_class(SelectAndAddBonesOperator)
    bpy.utils.unregister_class(AddBonesOperator)
