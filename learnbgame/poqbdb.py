import bpy
from bpy.types import Panel

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
		row.prop(poqbdbs,"poqbdbs")

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
		row.prop(poqbdbs,"species")

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
		row.prop(poqbdbs,"planets")

class POQBDB_ANIMAL(Panel):
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
		row.prop(poqbdbs,"animal")

class POQBDB_PLANT(Panel):
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
		row.prop(poqbdbs,"plant")

class POQBDB_MICRABE(Panel):
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
		row.prop(poqbdbs,"micrabe")

