import bpy
import os
from bpy.types import (Panel,PropertyGroup,Operator)
from bpy.props import (EnumProperty,PointerProperty)

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
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/") + other + ".glb")
		obj = context.selected_objects
		obj[0].name = other
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES(Panel):
	bl_label="species"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_POQBDB"

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species")
		row.operator(POQBDB_SPECIES_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_ADD(Operator):
	bl_idname = "poqbdb_species.add"
	bl_label = "poqbdb_species+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species = poqbdbs.poqbdb_species
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species")+"/" + poqbdb_species + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PLANETS(Panel):
	bl_label="planets"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_POQBDB"

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_planets")
		row.operator(POQBDB_PLANETS_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_PLANETS_ADD(Operator):
	bl_idname = "poqbdb_planets.add"
	bl_label = "poqbdb_planets+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_planets = poqbdbs.poqbdb_planets
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/planets")+"/" + poqbdb_planets + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_planets
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_ANIMAL(Panel):
	bl_label="animal"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_animal")
		row.operator(POQBDB_SPECIES_ANIMAL_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_ANIMAL_ADD(Operator):
	bl_idname = "poqbdb_species_animal.add"
	bl_label = "poqbdb_species_animal+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_animal = poqbdbs.poqbdb_species_animal
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/animal")+"/" + poqbdb_species_animal + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_animal
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_PLANT(Panel):
	bl_label="plant"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_plant")
		row.operator(POQBDB_SPECIES_PLANT_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_PLANT_ADD(Operator):
	bl_idname = "poqbdb_species_plant.add"
	bl_label = "poqbdb_species_plant+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_plant = poqbdbs.poqbdb_species_plant
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/plant")+"/" + poqbdb_species_plant + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_plant
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_SPECIES_MICRABE(Panel):
	bl_label="micrabe"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Learnbgame"
	bl_parent_id = "POQBDB_SPECIES"

	def draw(self,context):
		layout=self.layout
		scene = context.scene
		poqbdbs = scene.poqbdbs
		row = layout.row()
		row.prop(poqbdbs,"poqbdb_species_micrabe")
		row.operator(POQBDB_SPECIES_MICRABE_ADD.bl_idname,text="add",icon="ADD")

class POQBDB_SPECIES_MICRABE_ADD(Operator):
	bl_idname = "poqbdb_species_micrabe.add"
	bl_label = "poqbdb_species_micrabe+"

	def execute(self,context):
		poqbdbs = context.scene.poqbdbs
		poqbdb_species_micrabe = poqbdbs.poqbdb_species_micrabe
		bpy.ops.import_scene.gltf(filepath=os.path.join(os.path.dirname(__file__),"poqbdb/species/micrabe")+"/" + poqbdb_species_micrabe + ".glb")
		obj = context.selected_objects
		obj[0].name = poqbdb_species_micrabe
		obj[0].location = context.scene.cursor.location 
		return {'FINISHED'}

class POQBDB_PROPERTY(PropertyGroup):
	poqbdb : EnumProperty(
		name="poqbdb",
		items=[
			("learnioc","Learnioc","add learnioc"),
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
			("earth","Earth","add earth"),
			]
	)

	

def register():
	bpy.utils.register_class(POQBDB_POQBDB)
	
	bpy.utils.register_class(POQBDB_POQBDB_ADD)
	
	bpy.utils.register_class(POQBDB_PROPERTY)
	
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
	
	bpy.types.Scene.poqbdbs = PointerProperty(type=POQBDB_PROPERTY)
def unregister():
	bpy.utils.unregister_class(POQBDB_POQBDB)
	
	bpy.utils.unregister_class(POQBDB_POQBDB_ADD)
	
	bpy.utils.unregister_class(POQBDB_PROPERTY)
	
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
	