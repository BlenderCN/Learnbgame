import bpy
import math
from . import material_types
#from material_types import solid_material
#from material_types import transparent_material

soild_ior = 1.55
trans_ior = 1.45

# Done :)
solid_materials = {0: material_types.solid_material(0, "Black", "1B2A34"),
				   1: material_types.solid_material(1, "Bright Blue", "1E5AA8"),
				   2: material_types.solid_material(2, "Dark Green", "00852B"),
				   3: material_types.solid_material(3, "Bright Bluish Green", "069D9F"),
				   4: material_types.solid_material(4, "Bright Red", "B40000"),
				   5: material_types.solid_material(5, "Bright Purple", "D3359D"),
				   6: material_types.solid_material(6, "Medium Reddish Violet", "D05098"),
				   7: material_types.solid_material(7, "Grey", "8A928D"),
				   8: material_types.solid_material(8, "Dark Grey", "545955"),
				   9: material_types.solid_material(9, "Light Blue", "97CBD9"),
				   10: material_types.solid_material(10, "Bright Green", "58AB41"),
				   11: material_types.solid_material(11, "Medium Bluish Green", "00AAA4"),
				   12: material_types.solid_material(12, "Medium Red", "F06D61"),
				   13: material_types.solid_material(13, "Light Reddish Violet", "F6A9BB"),
				   14: material_types.solid_material(14, "Bright Yellow", "FAC80A"),
				   15: material_types.solid_material(15, "White", "F4F4F4"),
				   17: material_types.solid_material(17, "Light Green", "ADD9A8"),
				   18: material_types.solid_material(18, "Light Yellow", "FFD67F"),
				   19: material_types.solid_material(19, "Brick Yellow", "B0A06F"),
				   20: material_types.solid_material(20, "Light Bluish Violet", "AFBED6"),
				   22: material_types.solid_material(22, "Bright Violet", "671FA1"),
				   23: material_types.solid_material(23, "Dark Royal Blue", "0E3E9A"),
				   25: material_types.solid_material(25, "Bright Orange", "D67923"),
				   26: material_types.solid_material(26, "Bright Reddish Violet", "901F76"),
				   27: material_types.solid_material(27, "Bright Yellowish Green", "A5CA18"),
				   28: material_types.solid_material(28, "Sand Yellow", "897D62"),
				   30: material_types.solid_material(30, "Medium Lavender", "A06EB9"),
				   31: material_types.solid_material(31, "Lavender", "CDA4DE"),
				   68: material_types.solid_material(68, "Light Yellowish Orange", "FDC383"),
				   69: material_types.solid_material(69, "Bright Reddish Lilac", "8A12A8"),
				   70: material_types.solid_material(70, "Reddish Brown", "5F3109"),
				   71: material_types.solid_material(72, "Medium Stone Grey", "969696"),
				   72: material_types.solid_material(72, "Dark Stone Grey", "646464"),
				   73: material_types.solid_material(73, "Medium Blue", "7396C8"),
				   74: material_types.solid_material(74, "Medium Green", "7FC475"),
				   77: material_types.solid_material(77, "Light Pink", "F17880"),
				   78: material_types.solid_material(78, "Light Nougat", "FFC995"),
				   84: material_types.solid_material(84, "Medium Nougat", "AA7D55"),
				   85: material_types.solid_material(85, "Medium Lilac", "441A91"),
				   86: material_types.solid_material(86, "Brown", "7B5D41"),
				   89: material_types.solid_material(89, "Royal Blue", "1C58A7"),
				   92: material_types.solid_material(92, "Nougat", "BB805A"),
				   100: material_types.solid_material(100, "Light Red", "F9B7A5"),
				   110: material_types.solid_material(110, "Bright Bluish Violet", "26469A"),
				   112: material_types.solid_material(112, "Medium Bluish Violet", "4861AC"),
				   115: material_types.solid_material(115, "Medium Yellowish Green", "B7D425"),
				   118: material_types.solid_material(118, "Light Bluish Green", "9CD6CC"),
				   120: material_types.solid_material(120, "Light Yellowish Green", "DEEA92"),
				   125: material_types.solid_material(125, "Light Orange", "F9A777"),
				   128: material_types.solid_material(128, "Dark Nougat", "AD6140"),
				   151: material_types.solid_material(151, "Light Stone Grey", "C8C8C8"),
				   191: material_types.solid_material(191, "Flame Yellowish Orange", "FCAC00"),
				   212: material_types.solid_material(212, "Light Royal Blue", "9DC3F7"),
				   216: material_types.solid_material(216, "Rust", "872B17"),
				   218: material_types.solid_material(218, "Reddish Lilac", "8E5597"),
				   219: material_types.solid_material(219, "Lilac", "564E9D"),
				   226: material_types.solid_material(226, "Cool Yellow", "FFEC6C"),
				   232: material_types.solid_material(232, "Dove Blue", "77C9D8"),
				   272: material_types.solid_material(272, "Earth Blue", "19325A"),
				   288: material_types.solid_material(288, "Earth Green", "00451A"),
				   295: material_types.solid_material(295, "Flamingo Pink", "FF94C2"),
				   308: material_types.solid_material(308, "Dark Brown", "372100"),
				   313: material_types.solid_material(313, "Pastel Blue", "ABD9FF"),
				   320: material_types.solid_material(320, "Dark Red", "720012"),
				   321: material_types.solid_material(321, "Dark Azur", "469BC3"),
				   322: material_types.solid_material(322, "Medium Azur", "68C3E2"),
				   323: material_types.solid_material(323, "Aqua", "D3F2EA"),
				   326: material_types.solid_material(326, "Spring Yellowish Green", "E2F99A"),
				   330: material_types.solid_material(330, "Olive Green", "77774E"),
				   335: material_types.solid_material(335, "Sand Red", "88605E"),
				   351: material_types.solid_material(351, "Pink", "FF879C"),
				   366: material_types.solid_material(366, "Light Orange Brown", "D86D2C"),
				   373: material_types.solid_material(373, "Sand Violet", "75657D"),
				   378: material_types.solid_material(378, "Sand Green", "708E7C"),
				   379: material_types.solid_material(379, "Sand Blue", "70819A"),
				   450: material_types.solid_material(450, "Brick Red", "F2705E"),
				   462: material_types.solid_material(462, "Bright Yellowish Orange", "F58624"),
				   484: material_types.solid_material(484, "Dark Orange", "91501C"),
				   503: material_types.solid_material(503, "Light Grey", "BCB4A5")}

# Done-ish Material 47 needs a special case (Clear Transparent)
trans_materials = {33: material_types.transparent_material(33, "Transparent Blue", "A4FFFF", "4BA4FF"),
				   34: material_types.transparent_material(34, "Transparent Green", "000400", "23C923"),
				   35: material_types.transparent_material(35, "Transparent Bright Yellowish Green", "55FFC7", "D4FF91"),
				   36: material_types.transparent_material(36, "Transparent Red", "0D0000", "FF3737"),
				   37: material_types.transparent_material(37, "Transparent Medium Reddish Violet", "FF00DE", "FFCCF8"),
				   38: material_types.transparent_material(38, "Transparent Fluorescent Reddish Orange", "FF0700", "FF8352"),
				   39: material_types.transparent_material(39, "Transparent Light Bluish Green", "4CFFFF", "E6FCFF"),
				   40: material_types.transparent_material(40, "Transparent Brown", "000000", "919191"),
				   41: material_types.transparent_material(41, "Transparent Fluorescent Blue", "0072FF", "E6F1FF"),
				   42: material_types.transparent_material(42, "Transparent Fluorescent Green", "ADFF00", "FFF289"),
				   43: material_types.transparent_material(43, "Transparent Light Blue", "00C2FF", "99FAFF"),
				   44: material_types.transparent_material(44, "Transparent Reddish Lilac", "DD00FF", "FCE6FF"),
				   45: material_types.transparent_material(45, "Transparent Bright Purple", "FF0077", "FFCCE4"),
				   46: material_types.transparent_material(46, "Transparent Yellow", "FFDC00", "FFF8A2"),
				   47: material_types.transparent_material(47, "Transparent", "FFFFFF", "FFFFFF"),
				   52: material_types.transparent_material(52, "Transparent Bright Bluish Violet", "3900FF", "D7CCFF"),
				   54: material_types.transparent_material(54, "Transparent Fluorescent Yellow", "B36F00", "FFE796"),
				   57: material_types.transparent_material(57, "Transparent Bright Orange", "1FFFFF", "FFA842"),
				   231: material_types.transparent_material(231, "Transparent Flame Yellowish Orange", "FF9C00", "FFEBCC"),
				   285: material_types.transparent_material(285, "Transparent Light Green", "00FFC5", "CCFFE4"),
				   293: material_types.transparent_material(293, "Transparent Light Royal Blue", "0099FF", "CCEBFF")}

#def convert_ldd_ldr(ldd_id):
	# Code:

def convert_ior_specular(ior):
	return math.pow((ior - 1.00) / (ior + 1.0), 2) / 0.08

def get_material(material, material_id):
	print("In material creation function")
	# Remove Diffuse BSDF
	material.node_tree.nodes.remove(material.node_tree.nodes.get('Diffuse BSDF'))
	# Grab the output node:
	output_note = material.node_tree.nodes.get('Material Output')
	if material_id in solid_materials:
		# Solid Material
		print("Solid Material")
		principled_node = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
		principled_node.inputs['Base Color'].default_value = solid_materials[material_id].color
		principled_node.distribution = 'GGX'
		principled_node.inputs['Roughness'].default_value = 0.300
		principled_node.inputs['Specular'].default_value = convert_ior_specular(soild_ior)
		material.node_tree.links.new(output_note.inputs[0], principled_node.outputs[0])
	elif material_id in trans_materials:
		print("Transparent Material")
		current_node_groups = bpy.data.node_groups
		#light_absorbtion = material.node_tree.nodes.new(bpy.data.node_groups['Light_Absorbtion'])
		if bpy.data.node_groups.find("Light Absorbtion") == -1:
			# Create Light Absorbtion Node Group
			light_absorbtion = bpy.data.node_groups.new('Light Absorbtion', 'ShaderNodeTree')
			light_absorbtion_inputs = light_absorbtion.nodes.new('NodeGroupInput') # Group Inputs
			light_absorbtion.inputs.new('NodeSocketFloat', 'Value')
			light_absorbtion_outputs = light_absorbtion.nodes.new('NodeGroupOutput') # Group Outputs
			light_absorbtion.outputs.new('NodeSocketFloat', 'Value')

			light_path = light_absorbtion.nodes.new('ShaderNodeLightPath')
			geometry = light_absorbtion.nodes.new('ShaderNodeNewGeometry')
			multiplyA = light_absorbtion.nodes.new('ShaderNodeMath') # To combime Light Path & Geometry
			multiplyA.operation = 'MULTIPLY'
			light_absorbtion.links.new(multiplyA.inputs[0], light_path.outputs['Ray Length']) # Link Light Paths to Multiply Node
			light_absorbtion.links.new(multiplyA.inputs[1], geometry.outputs['Backfacing'])   # Link Geometry to Multiply Node

			multiplyB = light_absorbtion.nodes.new('ShaderNodeMath') # To combime group input value and previous multiply (MultiplyA)
			multiplyB.operation = 'MULTIPLY'
			light_absorbtion.links.new(multiplyB.inputs[0], light_absorbtion_inputs.outputs[0]) # Link Group Input to Multiply Node
			light_absorbtion.links.new(multiplyB.inputs[1], multiplyA.outputs[0]) # Link MultiplyA Output to Multiply Node

			multiplyC = light_absorbtion.nodes.new('ShaderNodeMath') # TO multiply the previous multiply node with -1
			multiplyC.operation = 'MULTIPLY'
			multiplyC.inputs[0].default_value = -1.000
			light_absorbtion.links.new(multiplyC.inputs[1], multiplyB.outputs[0])

			power = light_absorbtion.nodes.new('ShaderNodeMath')
			power.operation = 'POWER'
			power.inputs[0].default_value = 2.710
			light_absorbtion.links.new(power.inputs[1], multiplyC.outputs[0])
			light_absorbtion.links.new(light_absorbtion_outputs.inputs[0], power.outputs[0]) # Link Power node to Group Output

		light_absorbtion = material.node_tree.nodes.new("ShaderNodeGroup")
		light_absorbtion.node_tree = bpy.data.node_groups.get("Light Absorbtion")
		light_absorbtion.inputs[0].default_value = 1.000
		mixRGB = material.node_tree.nodes.new("ShaderNodeMixRGB")
		mixRGB.blend_type = "MIX"
		mixRGB.inputs["Color1"].default_value = trans_materials[material_id].main_color
		mixRGB.inputs["Color2"].default_value = trans_materials[material_id].secondary_color
		material.node_tree.links.new(light_absorbtion.outputs[0], mixRGB.inputs[0])

		principled_node = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
		#principled_node.inputs['Base Color'].default_value = solid_materials[material_id]
		principled_node.distribution = 'MULTI_GGX'
		principled_node.inputs['Roughness'].default_value = 0.000
		principled_node.inputs[15].default_value = 1.000
		principled_node.inputs['Specular'].default_value = convert_ior_specular(trans_ior)
		material.node_tree.links.new(mixRGB.outputs[0], principled_node.inputs[0])

		HSV_node = material.node_tree.nodes.new("ShaderNodeHueSaturation")
		HSV_node.inputs[0].default_value = 0.500
		HSV_node.inputs[1].default_value = 1.000
		HSV_node.inputs[2].default_value = 0.125
		HSV_node.inputs[3].default_value = 1.000
		material.node_tree.links.new(mixRGB.outputs[0], HSV_node.inputs[4])

		Trans_node = material.node_tree.nodes.new("ShaderNodeBsdfTransparent")
		material.node_tree.links.new(HSV_node.outputs[0], Trans_node.inputs[0])

		Add_Shader = material.node_tree.nodes.new("ShaderNodeAddShader")
		material.node_tree.links.new(principled_node.outputs[0], Add_Shader.inputs[0])
		material.node_tree.links.new(Trans_node.outputs[0], Add_Shader.inputs[1])

		material.node_tree.links.new(Add_Shader.outputs[0], output_note.inputs[0])
	return material

'''
	   (2, 'Grey', 0),
	   (3, 'Light Yellow', 0),
	   (4, 'Brick Red', 0),
	   (5, 'Brick Yellow', 0),
	   (6, 'Light Green', 0),
	   (7, 'Orange', 0),
	   (8, 'Cobalt Blue', 0),
	   (9, 'Light Reddish Violet', 0),
	   (11, 'Pastel Blue', 0),
	   (12, 'Light Orange Brown', 0),
	   (13, 'Red Orange', 0),
	   (14, 'Pastel Green', 0),
	   (15, 'Lemon', 0),
	   (16, 'Pink', 0),
	   (17, 'Rose', 0),
	   (18, 'Nougat', 0),
	   (19, 'Light Brown', 0),
	   (21, 'Bright Red', 0),
	   (22, 'Medium Reddish Violet', 0),
	   (23, 'Bright Blue', 0),
	   (24, 'Bright Yellow', 0),
	   (25, 'Earth Orange', 0),
	   (26, 'Black', 0),
	   (27, 'Dark Grey', 0),
	   (28, 'Dark Green', 0),
	   (29, 'Medium Green', 0),
	   (36, 'Light Yellowish Orange', 0),
	   (37, 'Bright Green', 0),
	   (38, 'Dark Orange', 0),
	   (39, 'Light Bluish Violet', 0),
	   (45, 'Light Blue', 0),
	   (100, 'Light Red', 0),
	   (101, 'Medium Red', 0),
	   (102, 'Medium Blue', 0),
	   (103, 'Light Grey', 0),
	   (104, 'Bright Violet', 0),
	   (105, 'Bright Yellowish Orange', 0),
	   (106, 'Bright Orange', 0),
	   (107, 'Bright Bluish Green', 0),
	   (108, 'Earth Yellow', 0),
	   (110, 'Bright Bluish Violet', 0),
	   (112, 'Medium Bluish Violet', 0),
	   (115, 'Medium Yellowish Green', 0),
	   (116, 'Medium Bluish Green', 0),
	   (118, 'Light Bluish Green', 0),
	   (119, 'Bright Yellowish Green', 0),
	   (120, 'Light Yellowish Green', 0),
	   (121, 'Medium Yelowish Orange', 0),
	   (123, 'Bright Reddish Orange', 0),
	   (124, 'Bright Reddish Violet', 0),
	   (125, 'Light Orange', 0),
	   (128, 'Dark Nougat', 0),
	   (133, 'Neon Orange', 0),
	   (134, 'Neon Green', 0),
	   (135, 'Sand Blue', 0),
	   (136, 'Sand Violet', 0),
	   (137, 'Medium Orange', 0),
	   (138, 'Sand Yellow', 0),
	   (140, 'Earth Blue', 0),
	   (141, 'Earth Green', 0),
	   (144, 'Dark Army Green', 0),
	   (151, 'Sand Green', 0),
	   (153, 'Sand Red', 0),
	   (154, 'New Dark Red', 0),
	   (163, 'Dull Sand Red*', 0),
	   (180, 'Curry', 0),
	   (188, 'Tiny Blue', 0),
	   (190, 'Fire Yellow', 0),
	   (191, 'Flame Yellowish Orange', 0),
	   (192, 'Reddish Brown', 0),
	   (193, 'Flame Reddish Orange', 0),
	   (194, 'Medium Stone Grey', 0),
	   (195, 'Royal Blue', 0),
	   (196, 'Dark Royal Blue', 0),
	   (197, 'Bright Lilac', 0),
	   (198, 'Bright Reddish Lilac', 0),
	   (199, 'Dark Stone Grey', 0),
	   (208, 'Light Stone Grey', 0),
	   (209, 'Dark Curry', 0),
	   (210, 'Faded Green', 0),
	   (211, 'Turquoise', 0),
	   (212, 'Light Royal Blue', 0),
	   (213, 'Medium Royal Blue', 0),
	   (216, 'Rust', 0),
	   (217, 'Brown', 0),
	   (218, 'Reddish Lilac', 0),
	   (219, 'Lilac', 0),
	   (220, 'Light Lilac', 0),
	   (221, 'Bright Purple', 0),
	   (222, 'Light Purple', 0),
	   (223, 'Light Pink', 0),
	   (224, 'Light Brick Yellow', 0),
	   (225, 'Warm Yellowish Orange', 0),
	   (226, 'Cool Yellow', 0),
	   (232, 'Dove Blue', 0),
	   (233, 'Light Faded Green', 0),
	   (268, 'Medium Lilac', 0),
	   (269, 'Tiny-Medium Blue', 0),
	   (283, 'Light Nougat', 0),
	   (295, 'Flamingo Pink', 0),
	   (308, 'Dark Brown', 0),
	   (312, 'Medium Nougat', 0),
	   (321, 'Dark Azur', 0),
	   (322, 'Medium Azur', 0),
	   (323, 'Aqua', 0),
	   (324, 'Medium Lavender', 0),
	   (325, 'Lavender', 0),
	   (326, 'Spring Yellowish Green', 0),
	   (330, 'Olive Green', 0);
'''
