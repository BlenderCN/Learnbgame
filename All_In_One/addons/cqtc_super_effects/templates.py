import bpy.props
import cqtc_templates

template_filename = "plantillas_super_efectos"

def load_templates():
	return cqtc_templates.load_templates(template_filename)


class AddSuperEffectTemplateOperator(cqtc_templates.AddCqtcTemplateOperator):
	bl_idname = "super_effect.add_template"
	bl_label = "Añadir Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.super_effect

	@property
	def template_filename(self):
		return template_filename


class LoadSuperEffectTemplateOperator(cqtc_templates.LoadCqtcTemplateOperator):
	bl_idname = "super_effect.load_template"
	bl_label = "Cargar Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.super_effect

	@property
	def template_filename(self):
		return template_filename


class SetSuperEffectTemplateNameOperator(cqtc_templates.SetCqtcTemplateNameOperator):
	bl_idname = "super_effect.set_template_name"
	bl_label = "Poner nombre a la nueva plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	action = bpy.props.StringProperty()
	
	@property
	def action_parameter(self):
		return self.action

	def get_addon_properties(self, context):
		return context.scene.super_effect

	@property
	def template_filename(self):
		return template_filename


class RemoveSuperEffectTemplateOperator(cqtc_templates.RemoveCqtcTemplateOperator):
	bl_idname = "super_effect.remove_template"
	bl_label = "¿Estás seguro de que quieres borrar la plantilla seleccionada?"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.super_effect

	@property
	def template_filename(self):
		return template_filename
