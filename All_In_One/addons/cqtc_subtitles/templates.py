import bpy.props
import cqtc_templates

template_filename = "plantillas_subtitulos"

def load_templates():
	return cqtc_templates.load_templates(template_filename)


class AddSubtitleTemplateOperator(cqtc_templates.AddCqtcTemplateOperator):
	bl_idname = "subtitle.add_template"
	bl_label = "Añadir Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.subtitle

	@property
	def template_filename(self):
		return template_filename


class LoadSubtitleTemplateOperator(cqtc_templates.LoadCqtcTemplateOperator):
	bl_idname = "subtitle.load_template"
	bl_label = "Cargar Plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.subtitle

	@property
	def template_filename(self):
		return template_filename


class SetSubtitleTemplateNameOperator(cqtc_templates.SetCqtcTemplateNameOperator):
	bl_idname = "subtitle.set_template_name"
	bl_label = "Poner nombre a la nueva plantilla"
	bl_options = {"REGISTER", "UNDO"}
	
	action = bpy.props.StringProperty()
	
	@property
	def action_parameter(self):
		return self.action

	def get_addon_properties(self, context):
		return context.scene.subtitle

	@property
	def template_filename(self):
		return template_filename


class RemoveSubtitleTemplateOperator(cqtc_templates.RemoveCqtcTemplateOperator):
	bl_idname = "subtitle.remove_template"
	bl_label = "¿Estás seguro de que quieres borrar la plantilla seleccionada?"
	bl_options = {"REGISTER", "UNDO"}
	
	def get_addon_properties(self, context):
		return context.scene.subtitle

	@property
	def template_filename(self):
		return template_filename
