import bpy
import os
from bpy.types import (Panel,PropertyGroup,Operator)
from bl_ui.properties_object import ObjectButtonsPanel
from bpy.utils import previews
from bpy.props import (EnumProperty,PointerProperty)

icons_collection = {}

icons = previews.new()
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons_list = os.listdir(icons_dir)
for icon in os.listdir(icons_dir):
	name, ext = os.path.splitext(icon)
	icons.load(name, os.path.join(icons_dir, icon), 'IMAGE')
icons_collection["main"] = icons

class POQBDB_POQBDB(Panel):
	bl_label="poqbdb"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb")
		row.operator(POQBDB_POQBDB_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_POQBDB_ADD(Operator):
	bl_idname = "poqbdb_poqbdb.add"
	bl_label = "poqbdb_poqbdb+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		other = poqbdbs.poqbdb
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"/root/Blender/blender-280/2.80/scripts/addons/learnbgame/poqbdb/") + other + ".glb")
		obj = context.selected_objects
		obj[0].name = other
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_ORGAN(Panel,ObjectButtonsPanel):
	bl_label="organ"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_POQBDB"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_organ",icon_value=icons[poqbdbs.poqbdb_organ if poqbdbs.poqbdb_organ+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_ORGAN_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_ORGAN_ADD(Operator):
	bl_idname = "poqbdb_organ.add"
	bl_label = "poqbdb_organ+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_organ = poqbdbs.poqbdb_organ
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/organ")+os.path.sep + poqbdb_organ + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_organ
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES(Panel,ObjectButtonsPanel):
	bl_label="species"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_POQBDB"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species",icon_value=icons[poqbdbs.poqbdb_species if poqbdbs.poqbdb_species+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_SPECIES_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_ADD(Operator):
	bl_idname = "poqbdb_species.add"
	bl_label = "poqbdb_species+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species = poqbdbs.poqbdb_species
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species")+os.path.sep + poqbdb_species + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PLANETS(Panel,ObjectButtonsPanel):
	bl_label="planets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_POQBDB"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_planets",icon_value=icons[poqbdbs.poqbdb_planets if poqbdbs.poqbdb_planets+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_PLANETS_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_PLANETS_ADD(Operator):
	bl_idname = "poqbdb_planets.add"
	bl_label = "poqbdb_planets+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_planets = poqbdbs.poqbdb_planets
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/planets")+os.path.sep + poqbdb_planets + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_planets
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_ANIMAL(Panel,ObjectButtonsPanel):
	bl_label="animal"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_animal",icon_value=icons[poqbdbs.poqbdb_species_animal if poqbdbs.poqbdb_species_animal+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_SPECIES_ANIMAL_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_ANIMAL_ADD(Operator):
	bl_idname = "poqbdb_species_animal.add"
	bl_label = "poqbdb_species_animal+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_animal = poqbdbs.poqbdb_species_animal
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/animal")+os.path.sep + poqbdb_species_animal + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_animal
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_PLANT(Panel,ObjectButtonsPanel):
	bl_label="plant"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_plant",icon_value=icons[poqbdbs.poqbdb_species_plant if poqbdbs.poqbdb_species_plant+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_SPECIES_PLANT_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_PLANT_ADD(Operator):
	bl_idname = "poqbdb_species_plant.add"
	bl_label = "poqbdb_species_plant+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_plant = poqbdbs.poqbdb_species_plant
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/plant")+os.path.sep + poqbdb_species_plant + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_plant
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_MICRABE(Panel,ObjectButtonsPanel):
	bl_label="micrabe"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_micrabe",icon_value=icons[poqbdbs.poqbdb_species_micrabe if poqbdbs.poqbdb_species_micrabe+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_SPECIES_MICRABE_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_MICRABE_ADD(Operator):
	bl_idname = "poqbdb_species_micrabe.add"
	bl_label = "poqbdb_species_micrabe+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_micrabe = poqbdbs.poqbdb_species_micrabe
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/micrabe")+os.path.sep + poqbdb_species_micrabe + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_micrabe
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PLANETS_RIG(Panel,ObjectButtonsPanel):
	bl_label="rig"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_PLANETS"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_planets_rig",icon_value=icons[poqbdbs.poqbdb_planets_rig if poqbdbs.poqbdb_planets_rig+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_PLANETS_RIG_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_PLANETS_RIG_ADD(Operator):
	bl_idname = "poqbdb_planets_rig.add"
	bl_label = "poqbdb_planets_rig+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_planets_rig = poqbdbs.poqbdb_planets_rig
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/planets/rig")+os.path.sep + poqbdb_planets_rig + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_planets_rig
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PLANETS_TRAFFIC(Panel,ObjectButtonsPanel):
	bl_label="traffic"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_PLANETS"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_planets_traffic",icon_value=icons[poqbdbs.poqbdb_planets_traffic if poqbdbs.poqbdb_planets_traffic+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_PLANETS_TRAFFIC_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_PLANETS_TRAFFIC_ADD(Operator):
	bl_idname = "poqbdb_planets_traffic.add"
	bl_label = "poqbdb_planets_traffic+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_planets_traffic = poqbdbs.poqbdb_planets_traffic
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/planets/traffic")+os.path.sep + poqbdb_planets_traffic + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_planets_traffic
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PLANETS_WEAPON(Panel,ObjectButtonsPanel):
	bl_label="weapon"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_PLANETS"

	global icons_collection
	icons = icons_collection["main"]

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_planets_weapon",icon_value=icons[poqbdbs.poqbdb_planets_weapon if poqbdbs.poqbdb_planets_weapon+".png" in icons_list else "learnbgame"].icon_id)
		row.operator(POQBDB_PLANETS_WEAPON_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_PLANETS_WEAPON_ADD(Operator):
	bl_idname = "poqbdb_planets_weapon.add"
	bl_label = "poqbdb_planets_weapon+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_planets_weapon = poqbdbs.poqbdb_planets_weapon
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/planets/weapon")+os.path.sep + poqbdb_planets_weapon + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_planets_weapon
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PROPERTY(PropertyGroup):
	poqbdb : EnumProperty(
		name="poqbdb",
		items=[
			("learnioc","Learnioc","add learnioc"),
			]
	)

	poqbdb_organ : EnumProperty(
		name="organ",
		items=[
			("heart","Heart","add heart"),
			]
	)

	poqbdb_species : EnumProperty(
		name="species",
		items=[
			("learnioc","Learnioc","add learnioc"),
			]
	)

	poqbdb_species_animal : EnumProperty(
		name="animal",
		items=[
			("monkey","Monkey","add monkey"),
			("crocodile","Crocodile","add crocodile"),
			("goldfish","Goldfish","add goldfish"),
			("ostrich","Ostrich","add ostrich"),
			("frog","Frog","add frog"),
			("penguin","Penguin","add penguin"),
			("racoon","Racoon","add racoon"),
			("turtle","Turtle","add turtle"),
			("crow","Crow","add crow"),
			("duck","Duck","add duck"),
			("elk","Elk","add elk"),
			("cow","Cow","add cow"),
			("kangaroo","Kangaroo","add kangaroo"),
			("shrimp","Shrimp","add shrimp"),
			("walrus","Walrus","add walrus"),
			("crab","Crab","add crab"),
			("hawk","Hawk","add hawk"),
			("goat","Goat","add goat"),
			("pig","Pig","add pig"),
			("parrot","Parrot","add parrot"),
			("bear","Bear","add bear"),
			("swan","Swan","add swan"),
			("pheasant","Pheasant","add pheasant"),
			("deer","Deer","add deer"),
			("glowworm","Glowworm","add glowworm"),
			("muskrat","Muskrat","add muskrat"),
			("armadillo","Armadillo","add armadillo"),
			("rabbit","Rabbit","add rabbit"),
			("snake","Snake","add snake"),
			("dolphin","Dolphin","add dolphin"),
			("spider","Spider","add spider"),
			("sealion","Sealion","add sealion"),
			("seahorse","Seahorse","add seahorse"),
			("elephant","Elephant","add elephant"),
			("bison","Bison","add bison"),
			("fly","Fly","add fly"),
			("giraffe","Giraffe","add giraffe"),
			("dog","Dog","add dog"),
			("fish","Fish","add fish"),
			("horse","Horse","add horse"),
			]
	)

	poqbdb_species_plant : EnumProperty(
		name="plant",
		items=[
			("sunflower","Sunflower","add sunflower"),
			("tulip","Tulip","add tulip"),
			]
	)

	poqbdb_species_micrabe : EnumProperty(
		name="micrabe",
		items=[
			("phage","Phage","add phage"),
			("coli","Coli","add coli"),
			]
	)

	poqbdb_planets : EnumProperty(
		name="planets",
		items=[
			("jupiter","Jupiter","add jupiter"),
			("moon","Moon","add moon"),
			]
	)

	poqbdb_planets_rig : EnumProperty(
		name="rig",
		items=[
			("fire_drango","Fire_drango","add fire_drango"),
			]
	)

	poqbdb_planets_traffic : EnumProperty(
		name="traffic",
		items=[
			("cycle","Cycle","add cycle"),
			]
	)

	poqbdb_planets_weapon : EnumProperty(
		name="weapon",
		items=[
			("sword","Sword","add sword"),
			]
	)

	

def register():
	bpy.utils.register_class(POQBDB_POQBDB)
	
	bpy.utils.register_class(POQBDB_POQBDB_ADD)
	
	bpy.utils.register_class(POQBDB_PROPERTY)
	
	bpy.utils.register_class(POQBDB_ORGAN)
	
	bpy.utils.register_class(POQBDB_ORGAN_ADD)
	
	bpy.utils.register_class(POQBDB_SPECIES)
	
	bpy.utils.register_class(POQBDB_SPECIES_ADD)
	
	bpy.utils.register_class(POQBDB_PLANETS)
	
	bpy.utils.register_class(POQBDB_PLANETS_ADD)
	
	bpy.utils.register_class(POQBDB_SPECIES_ANIMAL)
	
	bpy.utils.register_class(POQBDB_SPECIES_ANIMAL_ADD)
	
	bpy.utils.register_class(POQBDB_SPECIES_PLANT)
	
	bpy.utils.register_class(POQBDB_SPECIES_PLANT_ADD)
	
	bpy.utils.register_class(POQBDB_SPECIES_MICRABE)
	
	bpy.utils.register_class(POQBDB_SPECIES_MICRABE_ADD)
	
	bpy.utils.register_class(POQBDB_PLANETS_RIG)
	
	bpy.utils.register_class(POQBDB_PLANETS_RIG_ADD)
	
	bpy.utils.register_class(POQBDB_PLANETS_TRAFFIC)
	
	bpy.utils.register_class(POQBDB_PLANETS_TRAFFIC_ADD)
	
	bpy.utils.register_class(POQBDB_PLANETS_WEAPON)
	
	bpy.utils.register_class(POQBDB_PLANETS_WEAPON_ADD)
	
	bpy.types.Scene.poqbdbs = PointerProperty(type=POQBDB_PROPERTY)

def unregister():
	bpy.utils.unregister_class(POQBDB_POQBDB)
	
	bpy.utils.unregister_class(POQBDB_POQBDB_ADD)
	
	bpy.utils.unregister_class(POQBDB_PROPERTY)
	
	bpy.utils.unregister_class(POQBDB_ORGAN)
	
	bpy.utils.unregister_class(POQBDB_ORGAN_ADD)
	
	bpy.utils.unregister_class(POQBDB_SPECIES)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_ADD)
	
	bpy.utils.unregister_class(POQBDB_PLANETS)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_ADD)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_ANIMAL)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_ANIMAL_ADD)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_PLANT)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_PLANT_ADD)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_MICRABE)
	
	bpy.utils.unregister_class(POQBDB_SPECIES_MICRABE_ADD)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_RIG)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_RIG_ADD)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_TRAFFIC)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_TRAFFIC_ADD)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_WEAPON)
	
	bpy.utils.unregister_class(POQBDB_PLANETS_WEAPON_ADD)
	
