# Info
bl_info = {
    "name": "PBR Materials",
    "description": "PBR Materials and procedural textures",
    "version": (3, 4),
    "blender": (2, 80, 0),
    "author": "Wolf & Nathan Craddock",
    "location": "Material Properties and Shader Editor",
	"wiki_url": "https://3d-wolf.com/products/materials.html",
    "tracker_url": "https://3d-wolf.com/products/materials.html",
    "support": "COMMUNITY",
    "category": "Material"
}


# Libraries
import bpy
import os
from bpy.props import *
from bpy.types import PropertyGroup, Panel, Operator
from bpy.utils import previews
from . import addon_updater_ops


# Materials panel
class PBRMATERIAL_PT_Panel(Panel):
	bl_label = "PBR Materials"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "material"

	def draw_header(self, context):
		settings = context.scene.pbr_material_settings
		layout = self.layout
		layout.prop(settings, 'enabled', text='')

	@classmethod
	def poll(cls, context):
		return context.active_object.material_slots.data.active_material

	def draw(self, context):
		settings = context.scene.pbr_material_settings
		layout = self.layout
		# Updater
		addon_updater_ops.check_for_update_background()
		scn = bpy.context.scene
		layout.enabled = settings.enabled
		# Category
		col = layout.column(align=True)
		row = col.row()
		row.prop(settings, 'category', text="Category", expand=True)
		if settings.category == 'd':
			# Dielectrics
			material_name = scn.thumbs_mats_dielectrics
			thumbs = "thumbs_mats_dielectrics"   
		else:
			# Metals
			material_name = scn.thumbs_mats_metals
			thumbs = "thumbs_mats_metals"
		# Previews
		row = col.row()
		row.template_icon_view(scn, thumbs, show_labels=True)
		# Material Name
		row = col.row(align=True)
		row.alignment = 'CENTER'
		row.label(text=material_name)

		# Updater
		addon_updater_ops.update_notice_box_ui(self, context)


# Material Nodes panel
class PBRMATERIAL_PT_PanelNode(Panel):
	bl_label = "PBR Material Nodes"
	bl_category = "PBR Materials"
	bl_space_type = 'NODE_EDITOR'
	bl_region_type = 'UI'

	@classmethod
	def poll(cls, context):
		if bpy.context.object.active_material:
			return bpy.context.object.active_material.use_nodes

	def draw(self, context):
		settings = context.scene.pbr_material_settings
		layout = self.layout
		col = layout.column(align=True)
		row = col.row()
		row.prop(settings, 'category_node', text="Category", expand=True)
		row = col.row()
		if settings.category_node == 'm':
			row.template_icon_view(context.scene, "thumbs_mats_metals_node", show_labels=True)
			material_name = context.scene.thumbs_mats_metals_node
		else:
			row.template_icon_view(context.scene, "thumbs_mats_dielectrics_node", show_labels=True)
			material_name = context.scene.thumbs_mats_dielectrics_node
		row = col.row(align=True)
		row.alignment = 'CENTER'
		row.label(text=material_name)

		# Textures
		col.label(text="")
		col = layout.column(align=True)
		# Previews
		row = col.row()
		row.template_icon_view(context.scene, "thumbs_tex", show_labels=True)
		# Texture Name
		texture_name = context.scene.thumbs_tex
		row = col.row(align=True)
		row.alignment = 'CENTER'
		row.label(text=texture_name)


# Add material
def add_material(self, context):
	settings = context.scene.pbr_material_settings
	path = os.path.join(os.path.dirname(__file__), "blends/dielectrics.blend")
	if settings.category == 'd':
		node_name = context.scene.thumbs_mats_dielectrics
		if node_name in ("Atmosphere", "Blood", "Cloud", "Curtain", "Grass", "Leaf", "Ocean", "Paper", "Particles", "Transparent"):
			with bpy.data.libraries.load(path, False) as (data_from, data_to):
				data_to.node_groups = [node_name]
	else:
		node_name = context.scene.thumbs_mats_metals
	active_mat = bpy.context.active_object.active_material
	# Output
	active_mat.use_nodes = True
	active_mat.node_tree.nodes.clear()    
	preview_type = active_mat.preview_render_type
	output = active_mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
	output.location = (300, 0)

	# Dielectrics
	if node_name=="Dielectric":
		princi = principled(node_name, active_mat, output)
		princi.inputs[7].default_value = (0)
	elif node_name=="Acrylic Paint Black":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
		princi.inputs[5].default_value = (0.488)
		princi.inputs[7].default_value = (0)
	elif node_name=="Acrylic Paint White":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
		princi.inputs[5].default_value = (0.488)
		princi.inputs[7].default_value = (0)
	elif node_name=="Asphalt New":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.55)
	elif node_name=="Asphalt Old":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.12, 0.12, 0.12, 1)
		princi.inputs[5].default_value = (0.25)
		princi.inputs[7].default_value = (0.55)
	elif node_name=="Bark":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.168, 0.136, 0.105, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.6)
	elif node_name=="Brick":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.227, 0.147, 0.109, 1)
		princi.inputs[5].default_value = (0.588)
		princi.inputs[7].default_value = (0.78)
	elif node_name=="Car Paint":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0, 0.083, 0.457, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.25)
		princi.inputs[12].default_value = (1)
	elif node_name=="Carbon":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.015, 0.015, 0.015, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.4)
		princi.inputs[12].default_value = (1)
	elif node_name=="Ceramic":
		princi = principled(node_name, active_mat, output)
		color = rgb(princi, active_mat)
		color.outputs[0].default_value = (1, 0.898, 0.716, 1)
		princi.inputs[0].default_value = (0.6, 0.6, 0.6, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.6, 0.6, 0.6, 1)
		princi.inputs[5].default_value = (0.525)
		princi.inputs[7].default_value = (0)
	elif node_name=="Chalk":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.179, 0.7, 0.39, 1)
		princi.inputs[5].default_value = (0.563)
		princi.inputs[7].default_value = (0.65)
	elif node_name=="Cloth":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.065, 0.08, 0.254, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.8)
		princi.inputs[10].default_value = (1)
		princi.inputs[11].default_value = (0)
	elif node_name=="Coal":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.04, 0.04, 0.04, 1)
		princi.inputs[5].default_value = (0.425)
		princi.inputs[7].default_value = (0.66)
	elif node_name=="Concrete":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.231, 0.231, 0.202, 1)
		princi.inputs[5].default_value = (1.2)
		princi.inputs[7].default_value = (0.74)
	elif node_name=="Dirt":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.258, 0.162, 0.109, 1)
		princi.inputs[5].default_value = (0.75)
		princi.inputs[7].default_value = (0.78)
	elif node_name=="Light":
		emission = active_mat.node_tree.nodes.new("ShaderNodeEmission")
		blackbody = active_mat.node_tree.nodes.new("ShaderNodeBlackbody")
		blackbody.location = (-200, 0)
		blackbody.inputs[0].default_value = (3000)
		active_mat.node_tree.links.new(blackbody.outputs[0], emission.inputs[0])
		active_mat.node_tree.links.new(emission.outputs[0], output.inputs[0])
	elif node_name=="Mud":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.342, 0.246, 0.165, 1)
		princi.inputs[5].default_value = (2.225)
		princi.inputs[7].default_value = (0.62)
	elif node_name=="Plaster":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.275, 0.262, 0.235, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.86)
	elif node_name=="Plastic":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.448, 0.013, 0.007, 1)
		princi.inputs[5].default_value = (0.375)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Rock":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.328, 0.287, 0.227, 1)
		princi.inputs[5].default_value = (0.625)
		princi.inputs[7].default_value = (0.81)
	elif node_name=="Rubber":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.022, 0.022, 0.022, 1)
		princi.inputs[5].default_value = (0.425)
		princi.inputs[7].default_value = (0.79)
	elif node_name=="Rust":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.184, 0.032, 0.007, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.82)
	elif node_name=="Sand":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.44, 0.386, 0.231, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.8)
		princi.inputs[10].default_value = (1)
		princi.inputs[11].default_value = (0)
	elif node_name=="Skin":
		princi = principled(node_name, active_mat, output)
		color = rgb(princi, active_mat)
		color.outputs[0].default_value = (1, 0, 0, 1)
		princi.inputs[0].default_value = (0.523, 0.251, 0.19, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.523, 0.251, 0.19, 1)
		princi.inputs[5].default_value = (0.413)
		princi.inputs[7].default_value = (0.5)
	elif node_name=="Snow":
		princi = principled(node_name, active_mat, output)
		color = rgb(princi, active_mat)
		color.outputs[0].default_value = (1, 0.97, 0.95, 1)
		princi.inputs[0].default_value = (0.9, 0.9, 0.9, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.9, 0.9, 0.9, 1)
		princi.inputs[5].default_value = (1.25)
		princi.inputs[7].default_value = (0.5)
	elif node_name=="Wax":
		princi = principled(node_name, active_mat, output)
		color = rgb(princi, active_mat)
		color.outputs[0].default_value = (1, 0.397, 0.16, 1)
		princi.inputs[0].default_value = (0.263, 0.084, 0.222, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.263, 0.084, 0.222, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.3)
	elif node_name=="Wood":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.402, 0.319, 0.231, 1)
		princi.inputs[5].default_value = (1)
		princi.inputs[7].default_value = (0.68)

	# Translucent and Volume
	if node_name in ("Curtain", "Grass", "Leaf", "Paper", "Transparent"):
		groupnode(node_name, active_mat, output)
	elif node_name in ("Atmosphere", "Cloud", "Particles"):
		group = active_mat.node_tree.nodes.new("ShaderNodeGroup")
		group.node_tree = bpy.data.node_groups[node_name]
		active_mat.node_tree.links.new(group.outputs[0], output.inputs[1])
	elif node_name in ("Blood", "Ocean"):
		group = active_mat.node_tree.nodes.new("ShaderNodeGroup")
		group.node_tree = bpy.data.node_groups[node_name]
		active_mat.node_tree.links.new(group.outputs[0], output.inputs[0])
		active_mat.node_tree.links.new(group.outputs[1], output.inputs[1])

	# Metals
	if node_name=="Aluminium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.815, 0.831, 0.839, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Brass":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.956, 0.791, 0.305, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Bronze":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.973, 0.429, 0.15, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Chromium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.262, 0.258, 0.283, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Cobalt":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.392, 0.386, 0.361, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Copper":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.973, 0.356, 0.246, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Gallium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.479, 0.604, 0.578, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Gold":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.973, 0.539, 0.109, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Iron":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.552, 0.571, 0.571, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Lead":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.591, 0.591, 0.591, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Mercury":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.584, 0.571, 0.571, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0)
	elif node_name=="Molybdenum":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.429, 0.445, 0.361, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Nickel":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.392, 0.323, 0.235, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Pewter":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.515, 0.456, 0.392, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Platinum":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.429, 0.381, 0.314, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Pot":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.815, 0.831, 0.839, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.3)
		princi.inputs[8].default_value = (1)
		princi.inputs[9].default_value = (0.25)
	elif node_name=="Rhodium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.468, 0.381, 0.392, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Silver":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.93, 0.913, 0.831, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Tin":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.776, 0.776, 0.776, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Titanium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.262, 0.209, 0.165, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Tungsten":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.319, 0.319, 0.309, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Vanadium":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.407, 0.451, 0.429, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Zinc":
		princi = principled(node_name, active_mat, output)
		princi.inputs[0].default_value = (0.591, 0.546, 0.462, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)


# Append material nodes
def append_material_node(self, context):
	settings = context.scene.pbr_material_settings
	path = os.path.join(os.path.dirname(__file__), "blends/dielectrics.blend")
	if settings.category_node == 'd':
		node_name = context.scene.thumbs_mats_dielectrics_node
		if node_name in ("Atmosphere", "Blood", "Cloud", "Curtain", "Grass", "Leaf", "Ocean", "Paper", "Particles", "Transparent"):
			with bpy.data.libraries.load(path, False) as (data_from, data_to):
				if not node_name in bpy.data.node_groups:
					data_to.node_groups = [node_name]
	else:
		node_name = context.scene.thumbs_mats_metals_node
	bpy.ops.node.select_all(action='DESELECT')
	active_mat = bpy.context.active_object.active_material

	# Dielectrics
	if node_name=="Dielectric":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[7].default_value = (0)
	elif node_name=="Acrylic Paint Black":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
		princi.inputs[5].default_value = (0.488)
		princi.inputs[7].default_value = (0)
	elif node_name=="Acrylic Paint White":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
		princi.inputs[5].default_value = (0.488)
		princi.inputs[7].default_value = (0)
	elif node_name=="Asphalt New":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.55)
	elif node_name=="Asphalt Old":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.12, 0.12, 0.12, 1)
		princi.inputs[5].default_value = (0.25)
		princi.inputs[7].default_value = (0.55)
	elif node_name=="Bark":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.168, 0.136, 0.105, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.6)
	elif node_name=="Brick":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.227, 0.147, 0.109, 1)
		princi.inputs[5].default_value = (0.588)
		princi.inputs[7].default_value = (0.78)
	elif node_name=="Car Paint":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0, 0.083, 0.457, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.25)
		princi.inputs[12].default_value = (1)
	elif node_name=="Carbon":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.015, 0.015, 0.015, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.4)
		princi.inputs[12].default_value = (1)
	elif node_name=="Ceramic":
		princi = principled_nodes(node_name, active_mat)
		color = rgb_nodes(princi, active_mat)
		color.outputs[0].default_value = (1, 0.898, 0.716, 1)
		princi.inputs[0].default_value = (0.6, 0.6, 0.6, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.6, 0.6, 0.6, 1)
		princi.inputs[5].default_value = (0.525)
		princi.inputs[7].default_value = (0)
	elif node_name=="Chalk":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.179, 0.7, 0.39, 1)
		princi.inputs[5].default_value = (0.563)
		princi.inputs[7].default_value = (0.65)
	elif node_name=="Cloth":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.065, 0.08, 0.254, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.8)
		princi.inputs[10].default_value = (1)
		princi.inputs[11].default_value = (0)
	elif node_name=="Coal":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.04, 0.04, 0.04, 1)
		princi.inputs[5].default_value = (0.425)
		princi.inputs[7].default_value = (0.66)
	elif node_name=="Concrete":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.231, 0.231, 0.202, 1)
		princi.inputs[5].default_value = (1.2)
		princi.inputs[7].default_value = (0.74)
	elif node_name=="Dirt":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.258, 0.162, 0.109, 1)
		princi.inputs[5].default_value = (0.75)
		princi.inputs[7].default_value = (0.78)
	elif node_name=="Light":
		emission = active_mat.node_tree.nodes.new("ShaderNodeEmission")
		blackbody = active_mat.node_tree.nodes.new("ShaderNodeBlackbody")
		blackbody.location = (-200, 0)
		blackbody.inputs[0].default_value = (3000)
		active_mat.node_tree.links.new(blackbody.outputs[0], emission.inputs[0])
		active_mat.node_tree.links.new(emission.outputs[0].inputs[0])
	elif node_name=="Mud":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.342, 0.246, 0.165, 1)
		princi.inputs[5].default_value = (2.225)
		princi.inputs[7].default_value = (0.62)
	elif node_name=="Plaster":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.275, 0.262, 0.235, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.86)
	elif node_name=="Plastic":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.448, 0.013, 0.007, 1)
		princi.inputs[5].default_value = (0.375)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Rock":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.328, 0.287, 0.227, 1)
		princi.inputs[5].default_value = (0.625)
		princi.inputs[7].default_value = (0.81)
	elif node_name=="Rubber":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.022, 0.022, 0.022, 1)
		princi.inputs[5].default_value = (0.425)
		princi.inputs[7].default_value = (0.79)
	elif node_name=="Rust":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.184, 0.032, 0.007, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.82)
	elif node_name=="Sand":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.44, 0.386, 0.231, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.8)
		princi.inputs[10].default_value = (1)
		princi.inputs[11].default_value = (0)
	elif node_name=="Skin":
		princi = principled_nodes(node_name, active_mat)
		color = rgb_nodes(princi, active_mat)
		color.outputs[0].default_value = (1, 0, 0, 1)
		princi.inputs[0].default_value = (0.523, 0.251, 0.19, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.523, 0.251, 0.19, 1)
		princi.inputs[5].default_value = (0.413)
		princi.inputs[7].default_value = (0.5)
	elif node_name=="Snow":
		princi = principled_nodes(node_name, active_mat)
		color = rgb_nodes(princi, active_mat)
		color.outputs[0].default_value = (1, 0.97, 0.95, 1)
		princi.inputs[0].default_value = (0.9, 0.9, 0.9, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.9, 0.9, 0.9, 1)
		princi.inputs[5].default_value = (1.25)
		princi.inputs[7].default_value = (0.5)
	elif node_name=="Wax":
		princi = principled_nodes(node_name, active_mat)
		color = rgb_nodes(princi, active_mat)
		color.outputs[0].default_value = (1, 0.397, 0.16, 1)
		princi.inputs[0].default_value = (0.263, 0.084, 0.222, 1)
		princi.inputs[1].default_value = (1)
		princi.inputs[3].default_value = (0.263, 0.084, 0.222, 1)
		princi.inputs[5].default_value = (0.5)
		princi.inputs[7].default_value = (0.3)
	elif node_name=="Wood":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.402, 0.319, 0.231, 1)
		princi.inputs[5].default_value = (1)
		princi.inputs[7].default_value = (0.68)

	# Translucent and Volume
	if node_name in ("Atmosphere", "Blood", "Cloud", "Curtain", "Grass", "Leaf", "Ocean", "Paper", "Particles", "Transparent"):
		group = bpy.data.materials[active_mat.name].node_tree.nodes.new("ShaderNodeGroup")
		group.node_tree = bpy.data.node_groups[node_name]
		group.location = bpy.context.space_data.edit_tree.view_center

	# Metals
	if node_name=="Aluminium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.815, 0.831, 0.839, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Brass":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.956, 0.791, 0.305, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Bronze":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.973, 0.429, 0.15, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Chromium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.262, 0.258, 0.283, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Cobalt":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.392, 0.386, 0.361, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Copper":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.973, 0.356, 0.246, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Gallium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.479, 0.604, 0.578, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Gold":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.973, 0.539, 0.109, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Iron":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.552, 0.571, 0.571, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Lead":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.591, 0.591, 0.591, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Mercury":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.584, 0.571, 0.571, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0)
	elif node_name=="Molybdenum":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.429, 0.445, 0.361, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Nickel":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.392, 0.323, 0.235, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Pewter":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.515, 0.456, 0.392, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Platinum":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.429, 0.381, 0.314, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Pot":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.815, 0.831, 0.839, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.3)
		princi.inputs[8].default_value = (1)
		princi.inputs[9].default_value = (0.25)
	elif node_name=="Rhodium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.468, 0.381, 0.392, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Silver":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.93, 0.913, 0.831, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Tin":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.776, 0.776, 0.776, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Titanium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.262, 0.209, 0.165, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Tungsten":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.319, 0.319, 0.309, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Vanadium":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.407, 0.451, 0.429, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)
	elif node_name=="Zinc":
		princi = principled_nodes(node_name, active_mat)
		princi.inputs[0].default_value = (0.591, 0.546, 0.462, 1)
		princi.inputs[4].default_value = (1)
		princi.inputs[7].default_value = (0.1)


# Append texture nodes
def append_texture_node_group(self, context):
	path = os.path.join(os.path.dirname(__file__), "blends/textures.blend")
	with bpy.data.libraries.load(path, False) as (data_from, data_to):
		node_group = context.scene.thumbs_tex
		if not node_group in bpy.data.node_groups:
			data_to.node_groups = [node_group]
	# Add the node
	active_material = bpy.context.object.active_material
	bpy.ops.node.select_all(action='DESELECT')
	group = bpy.data.materials[active_material.name].node_tree.nodes.new("ShaderNodeGroup")
	group.node_tree = bpy.data.node_groups[node_group]
	group.location = bpy.context.space_data.edit_tree.view_center


# Principled Materials
def principled(node_name, active_mat, output):
	principled = active_mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	principled.name = node_name
	principled.distribution = "MULTI_GGX"
	principled.subsurface_method = "RANDOM_WALK"
	active_mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
	return principled


# Principled Nodes
def principled_nodes(node_name, active_mat):
	principled = active_mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	principled.name = node_name
	principled.distribution = "MULTI_GGX"
	principled.subsurface_method = "RANDOM_WALK"
	principled.location = bpy.context.space_data.edit_tree.view_center
	return principled


# RGB Materials
def rgb(principled, active_mat):
	rgbnode = active_mat.node_tree.nodes.new("ShaderNodeRGB")
	rgbnode.location = (-200, 0)
	active_mat.node_tree.links.new(rgbnode.outputs[0], principled.inputs[2])
	return rgbnode


# RGB Nodes
def rgb_nodes(principled, active_mat):
	rgbnode = active_mat.node_tree.nodes.new("ShaderNodeRGB")
	rgbnode.location.x = principled.location.x-200
	rgbnode.location.y = principled.location.y
	active_mat.node_tree.links.new(rgbnode.outputs[0], principled.inputs[2])
	return rgbnode


# Group
def groupnode(node_name, active_mat, output):
	group = active_mat.node_tree.nodes.new("ShaderNodeGroup")
	group.node_tree = bpy.data.node_groups[node_name]
	active_mat.node_tree.links.new(group.outputs[0], output.inputs[0])


# Previews of materials
def generate_previews(metals):
	if metals:
		previews = preview_collections["pbr_materials_metals"]
	else:
		previews = preview_collections["pbr_materials_dielectrics"]
	image_location = previews.images_location
	enum_items = []    
	# Generate the thumbnails
	for i, image in enumerate(os.listdir(image_location)):
		filepath = os.path.join(image_location, image)
		thumb = previews.load(filepath, filepath, 'IMAGE')
		enum_items.append((image, image, "", thumb.icon_id, i))
	enum_items.sort()
	return enum_items


# Previews of nodes
def generate_previews_nodes(metals):
	if metals:
		previews = preview_collections_nodes["pbr_materials_metals_node"]
	else:
		previews = preview_collections_nodes["pbr_materials_dielectrics_node"]
	image_location = previews.images_location
	enum_items = []
	# Generate the thumbnails
	for i, image in enumerate(os.listdir(image_location)):
		filepath = os.path.join(image_location, image)
		thumb = previews.load(filepath, filepath, 'IMAGE')
		enum_items.append((image, image, "", thumb.icon_id, i))
	enum_items.sort()
	return enum_items


# Previews of textures
def generate_previews_tex():
	previews = preview_collections_tex["pbr_textures"]
	image_location = previews.images_location
	enum_items = []
	# Generate the thumbnails
	for i, image in enumerate(os.listdir(image_location)):
		filepath = os.path.join(image_location, image)
		thumb = previews.load(filepath, filepath, 'IMAGE')
		enum_items.append((image, image, "", thumb.icon_id, i))
	enum_items.sort()
	return enum_items


# Enable
def addon_toggle(self, context):
	settings = context.scene.pbr_material_settings
	# If the Checkbox is OFF, add basic Principled
	if not settings.enabled:
		# Delete active material
		active_mat = context.active_object.active_material
		active_mat.use_nodes = True
		active_mat.node_tree.nodes.clear()
		preview_type = active_mat.preview_render_type
		# Create nodes
		output = active_mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
		principled = active_mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
		output.location = (200, 0)
		# Link nodes
		active_mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
		# Hack to refresh the preview
		active_mat.preview_render_type = preview_type
	else:
		# Select the Dielectric Preview
		bpy.context.scene.pbr_material_settings.category = 'd'
		bpy.context.scene.thumbs_mats_dielectrics = 'Dielectric'
		# Add material
		add_material(self, context)


# Settings
class PBRMaterialSettings(PropertyGroup):
	category : bpy.props.EnumProperty(
		items=[('d', 'Dielectric', 'Dielectric Materials'),
				('m', 'Metal', 'Metal Materials')],
		description="Type of Material",
		default='d'
		)
	category_node : bpy.props.EnumProperty(
		items=[('d', 'Dielectric', 'Show dielectric materials'),
				('m', 'Metal', 'Show metallic materials')],
		description="Choose the category for materials",
		default='d'
		)
	enabled : bpy.props.BoolProperty(
		name="Enabled",
		description="Use PBR Materials Addon",
		default=False,
		update=addon_toggle
		)


# Preferences
@addon_updater_ops.make_annotations
class PBRMaterialsPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=True,
		)
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=1,
		min=0,
		max=31
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	def draw(self, context):
		layout = self.layout
		mainrow = layout.row()
		col = mainrow.column()
		addon_updater_ops.update_settings_ui(self, context)


preview_collections = {}
preview_collections_nodes = {}
preview_collections_tex = {}


###############################################################################################

classes = (
	PBRMATERIAL_PT_Panel,
	PBRMATERIAL_PT_PanelNode,
	PBRMaterialSettings,
	PBRMaterialsPreferences
	)

register, unregister = bpy.utils.register_classes_factory(classes)


# Register
def register():
	addon_updater_ops.register(bl_info)
	for cls in classes:
		# Updater
		addon_updater_ops.make_annotations(cls)
		bpy.utils.register_class(cls)
	bpy.types.Scene.pbr_material_settings = bpy.props.PointerProperty(type=PBRMaterialSettings)
	# Materials
	previews_mat_metals = bpy.utils.previews.new()
	previews_mat_dielectrics = bpy.utils.previews.new()
	previews_mat_metals_node = bpy.utils.previews.new()
	previews_mat_dielectrics_node = bpy.utils.previews.new()
	previews_tex = bpy.utils.previews.new()
	previews_mat_metals.images_location = os.path.join(os.path.dirname(__file__), "thumbs/m")
	previews_mat_dielectrics.images_location = os.path.join(os.path.dirname(__file__), "thumbs/d")
	previews_mat_metals_node.images_location = os.path.join(os.path.dirname(__file__), "thumbs/m")
	previews_mat_dielectrics_node.images_location = os.path.join(os.path.dirname(__file__), "thumbs/d")
	previews_tex.images_location = os.path.join(os.path.dirname(__file__), "thumbs/t")
	preview_collections['pbr_materials_metals'] = previews_mat_metals
	preview_collections['pbr_materials_dielectrics'] = previews_mat_dielectrics
	preview_collections_nodes['pbr_materials_metals_node'] = previews_mat_metals_node
	preview_collections_nodes['pbr_materials_dielectrics_node'] = previews_mat_dielectrics_node
	preview_collections_tex['pbr_textures'] = previews_tex

	# Previews Dielectrics and Metals
	bpy.types.Scene.thumbs_mats_metals = bpy.props.EnumProperty(
		items=generate_previews(True),
		description="Choose the material you want to use",
		update=add_material,
		default='Gold'
		)
	bpy.types.Scene.thumbs_mats_dielectrics = bpy.props.EnumProperty(
		items=generate_previews(False),
		description="Choose the material you want to use",
		update=add_material,
		default='Dielectric'
		)
	bpy.types.Scene.thumbs_mats_metals_node = bpy.props.EnumProperty(
		items=generate_previews_nodes(True),
		description="Choose the material you want to use",
		update=append_material_node,
		default='Gold'
		)
	bpy.types.Scene.thumbs_mats_dielectrics_node = bpy.props.EnumProperty(
		items=generate_previews_nodes(False),
		description="Choose the material you want to use",
		update=append_material_node,
		default='Dielectric'
		)
	bpy.types.Scene.thumbs_tex = bpy.props.EnumProperty(
		items=generate_previews_tex(),
		description="Choose the texture you want to use",
		default="Scratches Texture",
		update=append_texture_node_group
		)


def unregister():
	# Updater
	addon_updater_ops.unregister()
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.pbr_material_settings
	for preview in preview_collections.values():
		bpy.utils.previews.remove(preview)
	for preview in preview_collections_nodes.values():
		bpy.utils.previews.remove(preview)
	for preview in preview_collections_tex.values():
		bpy.utils.previews.remove(preview)
	del bpy.types.Scene.thumbs_mats_metals
	del bpy.types.Scene.thumbs_mats_dielectrics
	del bpy.types.Scene.thumbs_mats_metals_node
	del bpy.types.Scene.thumbs_mats_dielectrics_node
	del bpy.types.Scene.thumbs_tex
	preview_collections.clear()
