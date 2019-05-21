import cqtc_panel

class CqtcToolsPanel(cqtc_panel.CqtcPanel):
	bl_label = "Herramientas"
	bl_idname = "SCENE_PT_cqtc_tools"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw_header(self, context):
		self.layout.label(" ", icon="PREFERENCES")
	
	def draw(self, context):
		layout = self.layout
		
		self.draw_selected_sequences_info(layout, context)

		col = layout.column(align=True)
		row = col.row(align=True)
		row.scale_y = 1.5
		move_channel_up_operator = row.operator("cqtc_tools.change_channel", text="Subir strips")
		move_channel_up_operator.up_or_down = True
		
		row = col.row(align=True)
		row.scale_y = 1.5
		move_channel_down_operator = row.operator("cqtc_tools.change_channel", text="Bajar strips")
		move_channel_down_operator.up_or_down = False
