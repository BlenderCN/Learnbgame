

# <pep8 compliant>

# ----------------------------------------------------------
# Author: Fofight
# ----------------------------------------------------------


bl_info = {
    'name': 'Learnbgame',
    'description': 'Learn by game',
    'author': 'Fofight',
    'license': 'GPL',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'location': 'View3D > Tools > Learnbgame',
    'warning': '',
    'wiki_url': 'https://github.com/BlenderCN/Learnbgame/wiki',
    'tracker_url': 'https://github.com/BlenderCN/Learnbgame/issues',
    'link': 'https://github.com/BlenderCN/Learnbgame',
    'support': 'COMMUNITY',
    'category': 'Add Mesh'
    }


import os

import bgl,blf

# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
from bpy.types import (
    Panel, 
    Operator,
    Menu,
    PropertyGroup,
    SpaceView3D,
    WindowManager,
    )

from bpy.props import (
    EnumProperty,
    PointerProperty,
    StringProperty,
    BoolProperty,
    )
from bpy.utils import previews

icons_collection = {}
    
icons = previews.new()
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
for icon in os.listdir(icons_dir):
    name, ext = os.path.splitext(icon)
    icons.load(name, os.path.join(icons_dir, icon), 'IMAGE')
icons_collection["main"] = icons

atoms_dir = os.path.join(os.path.dirname(__file__), "atoms")
atoms_list = os.listdir(atoms_dir)

animals_dir = os.path.join(os.path.dirname(__file__), "species/animal")
animals_list = os.listdir(animals_dir)

plants_dir = os.path.join(os.path.dirname(__file__), "species/plant")
plants_list = os.listdir(plants_dir)

micrabes_dir = os.path.join(os.path.dirname(__file__), "species/micrabe")
micrabes_list = os.listdir(micrabes_dir)

planets_dir = os.path.join(os.path.dirname(__file__), "planets")
planets_list = os.listdir(planets_dir)

icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons_list = os.listdir(icons_dir)

########################UI##################################
class LEARNBGAME_ATOM(Panel):
    bl_idname = "learnbgame.atom"
    bl_label = "Atom"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    def draw(self,context):
        layout = self.layout
        scene = context.scene
        atoms = scene.atoms
        row = layout.row()
        row.prop(atoms,"atom",icon="PHYSICS")
        row.operator(ATOM_ADD.bl_idname,text="add",icon="ADD")

class LEARNBGAME_BRAND(Panel):
    bl_idname = "learnbgame.brand"
    bl_label = "Learnbgame"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        brand = scene.brand
        row = layout.row()
        row.prop(brand,"brand_text",icon="SMALL_CAPS")
        if context.window_manager.brand_run_opengl is False:
            icn = "PLAT",
            txt = "show"
        else:
            icon="PAUSE"
            txt = "hide"
        row.operator(BRAND_DISPLAY.bl_idname,text="show",icon="PLAY")


class LEARNBGAME_MOLECULE(Panel):
    bl_idname = "learnbgame.molecule"
    bl_label = "Molecule"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        molecule = scene.molecule
        row = layout.row()
        row.prop(molecule,"smile_format",icon="PIVOT_INDIVIDUAL")
        row.operator(MOLECULE_ADD.bl_idname,text="add",icon="ADD")



class LEARNBGAME_SPECIES(Panel):
    bl_idname = "learnbgame.species"
    bl_label = "Species"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    global icons_collection
    icons = icons_collection["main"]

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        animals = scene.animals
        row = layout.row(align=True)
        row.prop(
            animals,
            "animal",
            icon_value=icons[animals.animal if animals.animal+".png" in icons_list else "learnbgame"].icon_id
            )
        row.operator(ANIMAL_ADD.bl_idname,text="add",icon="ADD")

        plants = scene.plants
        row = layout.row()
        row.prop(
            plants,
            "plant",
            icon_value=icons[plants.plant if plants.plant+".png" in icons_list else "learnbgame"].icon_id
            )
        row.operator(PLANT_ADD.bl_idname,text="add",icon="ADD")

        micrabes = scene.micrabes
        row = layout.row()
        row.prop(
            micrabes,
            "micrabe",
            icon_value=icons[micrabes.micrabe if micrabes.micrabe+".png" in icons_list else "learnbgame"].icon_id)
        row.operator(MICRABE_ADD.bl_idname,text="add",icon="ADD")


class LEARNBGAME_PLANET(Panel):
    bl_idname = "learnbgame.planet"
    bl_label = "Planet"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    def draw(self,context):
        layout = self.layout
        scene = context.scene
        planets = scene.planets
        row = layout.row()
        row.prop(planets,"planet",icon="SHADING_WIRE")
        row.operator(PLANET_ADD.bl_idname,text="add",icon="ADD")

##########################UI#####################################

#########################Property###################################

class ATOM_PROPERTY(PropertyGroup):
    atom : EnumProperty(
        name = "Atom",
        items=(
            ('H',"Hydrogen","add H"),
            ("He","Heliem","add He")
            )
        )

class BRAND_PROPERTY(PropertyGroup):
    brand_text : StringProperty(
        name = "Text",
        description="brand text",
        default="Learnbgame"
        )
    WindowManager.brand_run_opengl = BoolProperty(default=False)


class MOLECULE_PROPERTY(PropertyGroup):
    smile_format : StringProperty(
        name = "Smile",
        description="smile format",
        default="CCO"
        )

class SPECIES_PROPERTY(PropertyGroup):


    animal : EnumProperty(
        name = "Animals",
        items=[
        (
            animal_name,
            animal_name.capitalize(),
            "add "+ animal_name,
            )for animal_name in animals_list
        ]
        )

    plant : EnumProperty(

        name = "Plants",
        items=[
        (
            plant_name,
            plant_name.capitalize(),
            "add "+ plant_name,
            )for plant_name in plants_list
        ]
        )

    micrabe : EnumProperty(
        name = "Micrabes",
        items =[
        (
            micrabe_name,
            micrabe_name.capitalize(),
            "add "+ micrabe_name,
            )for micrabe_name in micrabes_list
        ]
        )



class PLANET_PROPERTY(PropertyGroup):
    planet : EnumProperty(
        name = "Planet",
        items= [
        (
            planet_name,
            planet_name.capitalize(),
            "add "+ planet_name,
            )for planet_name in planets_list
        ]
        )
##########################Property####################################

######################Species Execute######################
class ANIMAL_ADD(Operator):
    bl_idname = "species.animal"
    bl_label = "Animal+"

    def execute(self,context):
        animals = context.scene.animals
        animal_name = animals.animal
        bpy.ops.import_scene.obj(filepath=animals_dir+"/"+animal_name+"/"+animal_name+".obj")
        obj = context.selected_objects
        context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = context.selected_objects
        obj[0].name = animal_name
        obj[0].location = context.scene.cursor_location
        return {'FINISHED'}

class PLANT_ADD(Operator):
    bl_idname = "species.plant"
    bl_label = "Plant+"

    def execute(self,context):

        plants = context.scene.plants
        plant_name = plants.plant
        bpy.ops.import_scene.obj(filepath=plants_dir+"/" + plant_name + "/" + plant_name +".obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = plant_name
        obj[0].location = bpy.context.scene.cursor_location
        return {'FINISHED'}
class MICRABE_ADD(Operator):
    bl_idname = "species.micrabe"
    bl_label = "Micrabe+"

    def execute(self,context):

        micrabes = context.scene.micrabes
        micrabe_name = micrabes.micrabe
        bpy.ops.import_scene.obj(filepath=micrabes_dir+"/" + micrabe_name + "/" + micrabe_name +".obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = micrabe_name
        obj[0].location = bpy.context.scene.cursor_location
        return {'FINISHED'}
#########################Species Execute#######################

#########################Planet Execute###################################
class PLANET_ADD(Operator):
    bl_idname = "planet.add"
    bl_label = "Planet+"

    def execute(self,context):

        planets = context.scene.planets
        planet_name = planets.planet
        bpy.ops.import_scene.obj(filepath=planets_dir+"/" + planet_name + "/" + planet_name +".obj")
        obj = bpy.context.selected_objects
        bpy.context.view_layer.objects.active=obj[0]
        bpy.ops.object.join()
        obj = bpy.context.selected_objects
        obj[0].name = planet_name
        obj[0].location = bpy.context.scene.cursor_location
        return {'FINISHED'}

###########################Planet Execute########################################        

###########################Molecule Execute####################################
class MOLECULE_ADD(Operator):
    bl_idname = "molecule.add"
    bl_label = "Molecule+"

    def execute(self,context):

        return {'FINISHED'}

#############################Molecule Execute################################

############################Atom Execute###################################

class ATOM_ADD(Operator):
    bl_idname = "atom.add"
    bl_label = "atom+"

    def execute(self,context):

        return {'FINISHED'}

############################Atom Execute###################################

############################Brand Execute###################################

class BRAND_DISPLAY(Operator):
    bl_idname = "brand.display"
    bl_label = "brand display"
    _handler = None

    def handle_add(self,context):
        if BRAND_DISPLAY._handler is None:
            BRAND_DISPLAY._handler = SpaceView3D.draw_handler_add(
                self.draw_callback,
                (context,),
                "WINDOW",
                "POST_PIXEL"
                )
            context.window_manager.brand_run_opengl = True

    def handle_remove(self,context):
        if BRAND_DISPLAY._handler is not None:
            SpaceView3D.draw_handler_remove(BRAND_DISPLAY._handler,"WINDOW")
        BRAND_DISPLAY._handler = None
        context.window_manager.brand_run_opengl = False
    def execute(self,context):
        if context.area.type == 'VIEW_3D':
            if context.window_manager.brand_run_opengl is False:
                self.handle_add(context)
            else:
                self.handle_remove(context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                 "View3D not found, cannot run operator")

        return {'CANCELLED'}

    def draw_callback(self, context):
        """Draw on the viewports"""
        # BLF drawing routine
        brand = context.scene.brand
        text = brand.brand_text
        font_id = 0
        blf.position(font_id, 25, 45, 0)
        blf.size(font_id, 50, 72)
        blf.draw(font_id, text)


        
############################Brand Execute###################################


"""
class BIOLOGY_ANIMAL_ADD(Menu):
    bl_idname = "biology.animal.add"
    bl_label = "Animal"

    def draw(self,context):
        global icons_collection
        icons = icons_collection["main"]
        layout = self.layout
        for animal in animals_list:
            layout.operator(
                "biology_animal."+animal,
                text=animal.capitalize(),
                icon_value=icons[animal if animal+".png" in icons_list else "learnbgame"].icon_id)


class BIOLOGY_PLANT_ADD(Menu):
    bl_idname = "biology.plant.add"
    bl_label = "Plant"

    def draw(self,context):
        global icons_collection
        icons = icons_collection["main"]
        layout = self.layout
        scene = context.scene
        plants_add = scene.plants_add
        row = layout.column()
        row.prop(plants_add,"plant_add",text="")
        #layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        plant_name = plants_add.plant_add
        bpy.ops.import_scene.obj(filepath=animals_dir+"/" + plant_name + "/" + plant_name +".obj")

class BIOLOGY_MICROBE_ADD(Menu):
    bl_idname = "biology.micrabe.add"
    bl_label = "Microbe"

    def draw(self,context):
        global icons_collection
        icons = icons_collection["main"]
        layout = self.layout
        
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)
        layout.operator("biology_animal.dog",text="Dog",icon_value=icons["dog"].icon_id)


class BIOLOGY_CREATURE_ADD(Menu):
    bl_idname = "biology.creature.add"
    bl_label = 'Biology'


    def draw(self, context):
        global icons_collection
        icons = icons_collection["main"]
        layout = self.layout
        layout.menu(BIOLOGY_ANIMAL_ADD.bl_idname,text="Animal",icon="RNA_ADD")
        layout.menu(BIOLOGY_PLANT_ADD.bl_idname,text="Plant",icon="RNA_ADD")
        layout.menu(BIOLOGY_MICROBE_ADD.bl_idname,text="Microbe",icon="RNA_ADD")




def biology_func(self, context):
    layout = self.layout
    global icons_collection
    icons = icons_collection["main"]
    layout.menu(BIOLOGY_CREATURE_ADD.bl_idname, text="Biology",icon="RNA")
"""
CLASSES = (
    SPECIES_PROPERTY,
    PLANT_ADD,
    LEARNBGAME_SPECIES,
    LEARNBGAME_ATOM,
    LEARNBGAME_MOLECULE,
    LEARNBGAME_PLANET,
    MOLECULE_PROPERTY,
    PLANET_PROPERTY,
    ANIMAL_ADD,
    PLANET_ADD,
    MICRABE_ADD,
    MOLECULE_ADD,
    ATOM_PROPERTY,
    ATOM_ADD,
    BRAND_PROPERTY,
    BRAND_DISPLAY,
    LEARNBGAME_BRAND,
    )

def register():

    for cla in CLASSES:
        bpy.utils.register_class(cla)
    bpy.types.Scene.plants = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.animals = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.micrabes = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.planets = PointerProperty(type=PLANET_PROPERTY)
    bpy.types.Scene.molecule = PointerProperty(type=MOLECULE_PROPERTY)
    bpy.types.Scene.atoms = PointerProperty(type=ATOM_PROPERTY)
    bpy.types.Scene.brand = PointerProperty(type=BRAND_PROPERTY)





def unregister():
    global icons_collection
    for cla in CLASSES:
        bpy.utils.unregister_class(cla)
    for icons in icons_collection.values():
        previews.remove(icons)
    icons_collection.clear()


if __name__ == "__main__":
    register()
