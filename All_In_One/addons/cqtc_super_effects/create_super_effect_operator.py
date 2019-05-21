import bpy.props
from cqtc_operator import CqtcOperator
from .super_effect_creator import SuperEffectCreator

class CreateSuperEffectOperator(CqtcOperator):
	bl_idname = "super_effect.create"
	bl_label = "Crear Transición"
	operation_type =  bpy.props.StringProperty()
	add_color_to_transition = bpy.props.BoolProperty(name="Con color", default=True)
	super_effect_creator = SuperEffectCreator()

	def execute(self, context):
		error = self.super_effect_creator.create(context, self.operation_type, self.add_color_to_transition)
		if error:
			return self.return_error(error)
	
		return {"FINISHED"}
