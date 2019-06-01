
import bpy


# object

class TowerEngineAttribute(bpy.types.PropertyGroup):
	""" Group of properties representing an item in the list """

	name = bpy.props.StringProperty(
		name="Name",
		description="The name of the attribute",
		default="attribute")

	value = bpy.props.StringProperty(
		name="Value",
		description="The value of the attribute",
		default="")


class TowerEngineObjectPropertyGroup(bpy.types.PropertyGroup):
	tag = bpy.props.StringProperty(name="Tag")
	
	attributes = bpy.props.CollectionProperty(name="attributes", type=TowerEngineAttribute)
	attribute_index = bpy.props.IntProperty(name="attribute_index", default=0)

	disable_mesh = bpy.props.BoolProperty(name="Do not export as Mesh Object")
	compound_shape = bpy.props.BoolProperty(name="Compound shape from children", default=False)

	object_type = bpy.props.EnumProperty(items=[("DEFAULT", "Default", "Default type from Blender object", 0),
												("REFLECTION_PROBE", "Reflection Probe", "Reflection Probe for TowerEngine", 1)],
										 name="Object Type",
										 default="DEFAULT")

# mesh texture slot

class TowerEngineMaterialTextureSlotPropertyGroup(bpy.types.PropertyGroup):
	use_map_metal_rough_reflect = bpy.props.BoolProperty(name="Metallic/Roughness/Reflectance", default=False)



# material

MaterialTypeItems = [
	("DEFAULT", "Default", "", 1),
	("SIMPLE_FORWARD", "SimpleForward", "", 2),
	("REFRACTION", "Refraction", "", 3),
]

MaterialBlendModeItems = [
	("ALPHA", "Alpha", "", 1),
	("ADD", "Add", "", 2),
	("MULTIPLY", "Multiply", "", 3),
]

class TowerEngineMaterialPropertyGroup(bpy.types.PropertyGroup):
	mat_type = bpy.props.EnumProperty(name="Type", items=MaterialTypeItems, default="DEFAULT")
	metallic = bpy.props.FloatProperty(name="Metallic", min=0.0, max=1.0, default=0.2)
	roughness = bpy.props.FloatProperty(name="Roughness", min=0.0, max=1.0, default=0.6)
	reflectance = bpy.props.FloatProperty(name="Reflectance", min=0.0, max=1.0, default=0.0)
	emission_color = bpy.props.FloatVectorProperty(name="Emission", subtype="COLOR", default=(0.0, 0.0, 0.0), min=-100.0, max=100.0, soft_min=0.0, soft_max=1.0)
	refraction_edge_color = bpy.props.FloatVectorProperty(name="Edge", subtype="COLOR", size=4, default=(0.0, 0.0, 0.0, 0.0), min=0.0, max=1.0)
	blend_mode = bpy.props.EnumProperty(name="BlendMode", items=MaterialBlendModeItems, default="ALPHA")



# mesh

class TowerEngineMeshPropertyGroup(bpy.types.PropertyGroup):
	vertices_only = bpy.props.BoolProperty(name="Vertices only", default=False)







reg_classes = [TowerEngineAttribute,
			   TowerEngineObjectPropertyGroup,
			   TowerEngineMaterialTextureSlotPropertyGroup,
			   TowerEngineMaterialPropertyGroup,
			   TowerEngineMeshPropertyGroup]

def register():
	for c in reg_classes:
		bpy.utils.register_class(c)

	bpy.types.Object.towerengine = bpy.props.PointerProperty(type=TowerEngineObjectPropertyGroup)
	bpy.types.Material.towerengine = bpy.props.PointerProperty(type=TowerEngineMaterialPropertyGroup)
	bpy.types.Material.towerengine_texture_slots = bpy.props.CollectionProperty(type=TowerEngineMaterialTextureSlotPropertyGroup)
	bpy.types.Mesh.towerengine = bpy.props.PointerProperty(type=TowerEngineMeshPropertyGroup)


def unregister():
	for c in reg_classes:
		bpy.utils.unregister_class(c)


