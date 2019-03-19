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
##########################Import Module############################

import os
import random
import sys
import time
import datetime
sys.path.append("/root/Software/anaconda3/lib/python3.7/site-packages")
import openbabel
import pybel

import json

from math import sqrt,pi,radians, sin, cos, tan, asin, degrees

import bgl,blf

import bpy

from math import acos

from mathutils import Vector,Matrix

from . import poqbdb
from . import spaceship_generator
from . import hdri
from . import spacestation
from .book import Book
from .shelf import Shelf
from .ch_trees import gui
from .grove import Grove_Operator, Grove_Preferences

from . import grove

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
    IntProperty,
    FloatProperty,
    )
from bpy.utils import (
    previews,
    register_class,
    unregister_class
    )

##########################Import Module############################

##########################Variable################################

icons_collection = {}
    
icons = previews.new()
icons_dir = os.path.join(os.path.dirname(__file__), "icons")
for icon in os.listdir(icons_dir):
    name, ext = os.path.splitext(icon)
    icons.load(name, os.path.join(icons_dir, icon), 'IMAGE')
icons_collection["main"] = icons

atoms_dir = os.path.join(os.path.dirname(__file__), "atoms")
atoms_file = open(os.path.join(atoms_dir,"atoms.json"))
atoms_list = json.load(atoms_file)
electron_dict = dict()
for atom in atoms_list:
    electron_dict[atom["symbol"]]=atom["electrons"] 

molecules_dir = os.path.join(os.path.dirname(__file__), "molecules")
with open(os.path.join(molecules_dir, 'atoms.json')) as in_file:
    atom_data = json.load(in_file)


animals_dir = os.path.join(os.path.dirname(__file__), "species/animal")
animals_list = [os.path.splitext(anl)[0] for anl in os.listdir(animals_dir)]


plants_dir = os.path.join(os.path.dirname(__file__), "species/plant")
plants_list = [os.path.splitext(plt)[0] for plt in os.listdir(plants_dir)]

micrabes_dir = os.path.join(os.path.dirname(__file__), "species/micrabe")
micrabes_list = [os.path.splitext(mib)[0] for mib in os.listdir(micrabes_dir)]

planets_dir = os.path.join(os.path.dirname(__file__), "planets")
planets_list = [os.path.splitext(plet)[0] for plet in os.listdir(planets_dir)]

icons_dir = os.path.join(os.path.dirname(__file__), "icons")
icons_list = os.listdir(icons_dir)

poqbdb_dir = os.path.join(os.path.dirname(__file__),"poqbdb")

##########################Variable################################

########################UI##################################



class LEARNBGAME_ATOM(Panel):
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
    bl_label = "Molecule"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"


    global icons_collection
    icons = icons_collection["main"]

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        molecule = scene.molecule
        row = layout.row()
        row.prop(
            molecule,
            "smile_format",
            icon_value=icons['molecule'].icon_id
            )
        row.operator(MOLECULE_ADD.bl_idname,text="add",icon="ADD")



class LEARNBGAME_SPECIES(Panel):
    bl_label = "Species"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame"

    def draw(self,context):
        pass



class LEARNBGAME_SPECIES_ANIMAL(Panel):
    bl_label = "Animals"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame" 
    bl_parent_id = "LEARNBGAME_SPECIES"

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

class LEARNBGAME_SPECIES_PLANT(Panel):
    bl_label = "Plants"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame" 
    bl_parent_id = "LEARNBGAME_SPECIES"

    global icons_collection
    icons = icons_collection["main"]

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        plants = scene.plants
        row = layout.row()
        row.prop(
            plants,
            "plant",
            icon_value=icons[plants.plant if plants.plant+".png" in icons_list else "learnbgame"].icon_id
            )
        row.operator(PLANT_ADD.bl_idname,text="add",icon="ADD")
        row1 = layout.row()
        row1.operator(Grove_Operator.TheGrove6.bl_idname, text="The Grove ",icon="PARTICLE_TIP")
        row2 = layout.row()
        row2.prop(plants,"twigs_folder")
        row2.prop(plants,"textures_folder")

class LEARNBGAME_SPECIES_MICRABE(Panel):
    bl_label = "Macrabes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Learnbgame" 
    bl_parent_id = "LEARNBGAME_SPECIES"

    global icons_collection
    icons = icons_collection["main"]

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        micrabes = scene.micrabes
        row = layout.row()
        row.prop(
            micrabes,
            "micrabe",
            icon_value=icons[micrabes.micrabe if micrabes.micrabe+".png" in icons_list else "learnbgame"].icon_id)
        row.operator(MICRABE_ADD.bl_idname,text="add",icon="ADD")

class LEARNBGAME_PLANET(Panel):
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
        row1 = layout.row()
        row1.operator(GenerateSpaceship.bl_idname,text="Spaceship",icon="AUTO")
        row2 = layout.row()
        row2.operator(GenerateSpacestation.bl_idname,text="Spacestation",icon="AUTO")
        row3 = layout.row()
        row3.operator(bookGen.bl_idname,text="Book",icon="ASSET_MANAGER")        
        row4 = layout.row()
        row4.operator(CLOCK_ADD.bl_idname,text="Clock",icon="TIME")


##########################UI#####################################

#########################Property###################################

class ATOM_PROPERTY(PropertyGroup):
    
    atom_items = [(atom['symbol'],atom['name'],"add " + atom['name']) for atom in atoms_list]
    atom_items.insert(0,("ptable","PeriodicTable","add Periodic Table of chemistry element"))
    atom : EnumProperty(
        name = "Atoms",
        items= atom_items
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

    twigs_folder : StringProperty(
        name = "Twigs Folder",
        description = "Twigs Folder",
        subtype='DIR_PATH'
        )
    
    textures_folder : StringProperty(
        name = "Textures Folder",
        description = "Textures Folder",
        subtype = 'DIR_PATH'
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
        bpy.ops.import_scene.gltf(filepath=animals_dir+"/"+animal_name+".glb")
        obj = context.selected_objects
        obj[0].name = animal_name
        obj[0].location = context.scene.cursor.location
        return {'FINISHED'}

class PLANT_ADD(Operator):
    bl_idname = "species.plant"
    bl_label = "Plant+"

    def execute(self,context):

        plants = context.scene.plants
        plant_name = plants.plant
        bpy.ops.import_scene.gltf(filepath=plants_dir+"/" + plant_name +".glb")
        obj = bpy.context.selected_objects
        obj[0].name = plant_name
        obj[0].location = bpy.context.scene.cursor.location
        return {'FINISHED'}

class MICRABE_ADD(Operator):
    bl_idname = "species.micrabe"
    bl_label = "Micrabe+"

    def execute(self,context):

        micrabes = context.scene.micrabes
        micrabe_name = micrabes.micrabe
        bpy.ops.import_scene.gltf(filepath=micrabes_dir+"/" + micrabe_name +".glb")
        obj = bpy.context.selected_objects
        obj[0].name = micrabe_name
        obj[0].location = bpy.context.scene.cursor.location
        return {'FINISHED'}

#########################Species Execute#######################

#########################Planet Execute###################################
class PLANET_ADD(Operator):
    bl_idname = "planet.add"
    bl_label = "Planet+"

    def execute(self,context):

        planets = context.scene.planets
        planet_name = planets.planet
        bpy.ops.import_scene.gltf(filepath=planets_dir+"/" + planet_name +".glb")
        obj = bpy.context.selected_objects
        obj[0].name = planet_name
        obj[0].location = bpy.context.scene.cursor.location
        return {'FINISHED'}

###########################Planet Execute########################################        

###########################Molecule Execute####################################
class MOLECULE_ADD(Operator):
    bl_idname = "molecule.add"
    bl_label = "Molecule+"

    def execute(self,context):
        self.draw_molecule(context,center=(0, 0, 0), show_bonds=True, join=True)

        return {'FINISHED'}

    def draw_molecule(self,context,center=(0, 0, 0), show_bonds=True, join=True):

        smile_text = context.scene.molecule.smile_format
        molecule = pybel.readstring("smi", smile_text)
        molecule.make3D()

        shapes = []

        bpy.ops.mesh.primitive_uv_sphere_add()
        sphere = bpy.context.object

        # Initialize bond material if it's going to be used.
        if show_bonds:
            bond_material = bpy.data.materials.new(name='bond')
            bond_material.use_nodes = True
            bond_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = atom_data['bond']['color']
            bond_material.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 1
            bond_material.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0
            bpy.ops.mesh.primitive_cylinder_add()
            cylinder = bpy.context.object
            cylinder.data.materials.append(bond_material)



        for atom in molecule.atoms:
            element = atom.type
            if element not in atom_data:
                element = 'undefined'

            if element not in bpy.data.materials:
                key = element
                atom_material = bpy.data.materials.new(name=key)
                atom_material.use_nodes = True
                atom_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = atom_data[key]['color']
                atom_material.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 1
                atom_material.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0

            atom_sphere = sphere.copy()
            atom_sphere.data = sphere.data.copy()
            atom_sphere.location = [l + c for l, c in
                                    zip(atom.coords, center)]
            scale = 1 if show_bonds else 2.5
            atom_sphere.dimensions = [atom_data[element]['radius'] *scale * 2] * 3
            atom_sphere.data.materials.append(atom_material)
            bpy.context.scene.collection.objects.link(atom_sphere)
            shapes.append(atom_sphere)

        for bond in (openbabel.OBMolBondIter(molecule.OBMol) if show_bonds else []):
            start = molecule.atoms[bond.GetBeginAtom().GetIndex()].coords
            end = molecule.atoms[bond.GetEndAtom().GetIndex()].coords
            diff = [c2 - c1 for c2, c1 in zip(start, end)]
            cent = [(c2 + c1) / 2 for c2, c1 in zip(start, end)]
            mag = sum([(c2 - c1) ** 2 for c1, c2 in zip(start, end)]) ** 0.5

            v_axis = Vector(diff).normalized()
            v_obj = Vector((0, 0, 1))
            v_rot = v_obj.cross(v_axis)

            # This check prevents gimbal lock (ie. weird behavior when v_axis is
            # close to (0, 0, 1))
            if v_rot.length > 0.01:
                v_rot = v_rot.normalized()
                axis_angle = [acos(v_obj.dot(v_axis))] + list(v_rot)
            else:
                v_rot = Vector((1, 0, 0))
                axis_angle = [0] * 4
            order = bond.GetBondOrder()
            if order not in range(1, 4):
                sys.stderr.write("Improper number of bonds! Defaulting to 1.\n")
                bond.GetBondOrder = 1

            if order == 1:
                trans = [[0] * 3]
            elif order == 2:
                trans = [[1.4 * atom_data['bond']['radius'] * x for x in v_rot],
                         [-1.4 * atom_data['bond']['radius'] * x for x in v_rot]]
            elif order == 3:
                trans = [[0] * 3,
                         [2.2 * atom_data['bond']['radius'] * x for x in v_rot],
                         [-2.2 * atom_data['bond']['radius'] * x for x in v_rot]]

            for i in range(order):
                bond_cylinder = cylinder.copy()
                bond_cylinder.data = cylinder.data.copy()
                bond_cylinder.dimensions = [atom_data['bond']['radius'] * scale *2] * 2 + [mag]
                bond_cylinder.location = [c + scale * v for c,v in zip(cent, trans[i])]
                bond_cylinder.rotation_mode = 'AXIS_ANGLE'
                bond_cylinder.rotation_axis_angle = axis_angle
                bpy.context.scene.collection.objects.link(bond_cylinder)
                shapes.append(bond_cylinder)

        sphere.select_set(True)
        if show_bonds:
            cylinder.select_set(True)
        bpy.ops.object.delete()

        for shape in shapes:
            shape.select_set(True)
        bpy.context.view_layer.objects.active = shapes[0]
        bpy.ops.object.shade_smooth()
        if join:
            bpy.ops.object.join()

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.context.scene.update()
        obj = bpy.context.selected_objects
        obj[0].name = smile_text
        obj[0].location = bpy.context.scene.cursor.location

        return {'FINISHED'}


#############################Molecule Execute################################

############################Atom Execute###################################

class ATOM_ADD(Operator):
    bl_idname = "atom.add"
    bl_label = "atom+"

    def execute(self,context):
        if context.scene.atoms.atom == "ptable":
            self.ptable(context)
        else:
            electronic_arrangement = electron_dict[context.scene.atoms.atom]
            self.draw_nucleus_electron(context,electronic_arrangement)

        return {'FINISHED'}

    def ptable(self,context):
        
        names = [ele['name'] for ele in atoms_list]
        alias = [ele['symbol'] for ele in atoms_list]

        keylist = bpy.data.objects.keys()

        num = 0


        for y in range(9,-11,-2):
            for x in range(-17,19,2):
                if y == 9 and x <= 15 and x >=-15:
                    pass
                elif (y == 7 and x >=-13 and x <= 5) or (y==5 and x >=-13 and x <= 5):
                    pass

                elif (y == -1 and x ==-13) or (y == -3 and x == -13):
                    pass

                elif y == -5 and x >= -17 and x <= 17:
                    pass

                elif (y == -7 and x >=-17 and x <=-13) or (y == -9 and x >=-17 and x <=-13) :
                    pass
                else:
                    bpy.ops.mesh.primitive_cube_add(
                        size=2,
                        view_align=False,
                        enter_editmode=False,
                        location=(x, y, 0))
                    obj = bpy.context.selected_objects
                    obj[0].name = names[num]            
                    element_material = bpy.data.materials.new(name=names[num])
                    element_material.use_nodes = True
                    element_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0, 0, 0, 1)
                    element_material.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 1
                    element_material.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0
                    obj[0].data.materials.append(element_material)

                    bpy.ops.object.text_add(
                        view_align=False,
                        enter_editmode=True,
                        location=(x,y,1))
                    bpy.context.object.name = alias[num]

                    bpy.ops.font.delete(type='PREVIOUS_WORD') 
                    bpy.ops.font.text_insert(text=alias[num])
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
                    obj = bpy.context.selected_objects
                    obj[0].location = (x,y,1)
                    
                    obj[0].name = names[num]                    
                    text_material = bpy.data.materials.new(name=alias[num])
                    text_material.use_nodes = True
                    text_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (1, 0, 0, 1)
                    text_material.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 1
                    text_material.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0
                    obj[0].data.materials.append(text_material)
                    bpy.ops.object.convert()
                    bpy.data.objects[names[num]].select_set(True)
                    bpy.context.view_layer.objects.active=bpy.data.objects[names[num]]
                    bpy.ops.object.join()


                    num += 1

    def draw_nucleus_electron(self,context,electronic_arrangement=[1,]):

        #electron_material = bpy.data.materials.new('electron')
        #electron_material.use_nodes = True
        #electron_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.045,0.945,0.945,1)
        #electron_material.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1
        #electron_material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0

################################fire material############
        electron_material = bpy.data.materials.new(name='electron')
        electron_material.use_nodes = True
        electron_material.node_tree.nodes.clear()

        output_material = electron_material.node_tree.nodes.new(type="ShaderNodeOutputMaterial") 
        emission1 = electron_material.node_tree.nodes.new(type="ShaderNodeEmission")   
        mix_rgb = electron_material.node_tree.nodes.new(type="ShaderNodeMixRGB")  
        mix_shader = electron_material.node_tree.nodes.new(type="ShaderNodeMixShader")   
        emission2 = electron_material.node_tree.nodes.new(type="ShaderNodeEmission")  
        transparent_bsdf = electron_material.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
        color_ramp1 = electron_material.node_tree.nodes.new(type="ShaderNodeValToRGB")
        color_ramp2 = electron_material.node_tree.nodes.new(type="ShaderNodeValToRGB")
        color_ramp3 = electron_material.node_tree.nodes.new(type="ShaderNodeValToRGB")
        normal = electron_material.node_tree.nodes.new(type="ShaderNodeNormal")
        voronoi_texture = electron_material.node_tree.nodes.new(type="ShaderNodeTexVoronoi")
        geometry = electron_material.node_tree.nodes.new(type="ShaderNodeNewGeometry")
        mapping = electron_material.node_tree.nodes.new(type="ShaderNodeMapping")
        texture_coordinate = electron_material.node_tree.nodes.new(type="ShaderNodeTexCoord")    

               
            # Change the parameters
        mix_rgb.blend_type = "MULTIPLY"
        mix_rgb.use_clamp = True
        mix_rgb.inputs['Fac'].default_value = 1
        mix_shader.name = ''
        emission2.inputs['Strength'].default_value = 3.2  

        color_ramp1.color_ramp.elements.new(0.478)
        color_ramp1.color_ramp.elements[0].color = (1,0,0,1)
        color_ramp1.color_ramp.elements[1].color = (1, 0.309396, 0, 1)
        color_ramp1.color_ramp.elements[2].color = (1, 0.732476, 0.427407, 1)

        color_ramp2.color_ramp.elements[0].position = 0.4495
        color_ramp2.color_ramp.elements[0].color = (0,0,0,1)
        color_ramp2.color_ramp.elements[1].position = 1
        color_ramp2.color_ramp.elements[1].color = (1,1,1,1)

        color_ramp3.color_ramp.elements[0].position = 0.268
        color_ramp3.color_ramp.elements[0].color = (1,1,1,1)
        color_ramp3.color_ramp.elements[1].position = 0.523
        color_ramp3.color_ramp.elements[1].color = (0,0,0,1)

        normal.outputs[0].default_value = (0.172571, -0.977901, -0.118026)
        voronoi_texture.inputs['Scale'].default_value=-2.7
        mapping.scale[0] = 0.9
        mapping.scale[1] = 2.0
        mapping.scale[2] = 0.0
                
        # Links
        electron_material.node_tree.links.new(texture_coordinate.outputs['Generated'], mapping.inputs[0])
        electron_material.node_tree.links.new(mapping.outputs[0], voronoi_texture.inputs[0])
        electron_material.node_tree.links.new(voronoi_texture.outputs[0], color_ramp3.inputs[0])
        electron_material.node_tree.links.new(color_ramp3.outputs[0], mix_rgb.inputs[1])
        electron_material.node_tree.links.new(mix_rgb.outputs[0], emission1.inputs[1])
        electron_material.node_tree.links.new(geometry.outputs['Normal'], normal.inputs[0])
        electron_material.node_tree.links.new(normal.outputs[1], color_ramp2.inputs[0])
        electron_material.node_tree.links.new(color_ramp2.outputs[0], mix_rgb.inputs[1])
        electron_material.node_tree.links.new(color_ramp2.outputs[0], mix_shader.inputs[0])
        electron_material.node_tree.links.new(color_ramp2.outputs[0], color_ramp1.inputs[0])
        electron_material.node_tree.links.new(color_ramp1.outputs[0], emission2.inputs[0])
        electron_material.node_tree.links.new(emission2.outputs[0], mix_shader.inputs[2])
        electron_material.node_tree.links.new(transparent_bsdf.outputs[0], mix_shader.inputs[1])
        electron_material.node_tree.links.new(mix_shader.outputs[0], output_material.inputs[0])

################################fire material############

        nucleus_material = bpy.data.materials.new('nucleus')
        nucleus_material.use_nodes = True
        nucleus_material.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0, 0, 0, 1)
        nucleus_material.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0
        nucleus_material.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0



        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,0))

        bpy.ops.object.shade_smooth()

        obj = bpy.context.selected_objects

        obj[0].name = "nucleus"
        obj[0].data.materials.append(nucleus_material)
        radius=2

        e_num = 1
        for electron_num in electronic_arrangement:
            electrons_status = [
                {"loc":(radius,0,0),"rot":(0,pi*2,0)},
                {"loc":(radius,0,0),"rot":(0,0,pi*2)},
                {"loc":(0,radius,0),"rot":(pi*2,0,0)},
                {"loc":(0,radius,0),"rot":(0,0,pi*2)},
                {"loc":(0,0,radius),"rot":(pi*2,0,0)},
                {"loc":(0,0,radius),"rot":(0,pi*2,0)},
                {"loc":(-radius,0,0),"rot":(0,pi*2,0)},
                {"loc":(-radius,0,0),"rot":(0,0,pi*2)},
                {"loc":(0,-radius,0),"rot":(pi*2,0,0)},
                {"loc":(0,-radius,0),"rot":(0,0,pi*2)},
                {"loc":(0,0,-radius),"rot":(pi*2,0,0)},
                {"loc":(0,0,-radius),"rot":(0,pi*2,0)},
                {"loc":(sqrt(radius**2/2),sqrt(radius**2/2),0),"rot":(0,0,pi*2)},
                {"loc":(sqrt(radius**2/2),0,sqrt(radius**2/2)),"rot":(0,pi*2,0)},
                {"loc":(0,sqrt(radius**2/2),sqrt(radius**2/2)),"rot":(pi*2,0,0)},
                {"loc":(-sqrt(radius**2/2),-sqrt(radius**2/2),0),"rot":(0,0,pi*2)},
                {"loc":(-sqrt(radius**2/2),0,-sqrt(radius**2/2)),"rot":(0,pi*2,0)},
                {"loc":(0,-sqrt(radius**2/2),-sqrt(radius**2/2)),"rot":(pi*2,0,0)},
                {"loc":(sqrt(radius**2/2),-sqrt(radius**2/2),0),"rot":(0,0,pi*2)},
                {"loc":(sqrt(radius**2/2),0,-sqrt(radius**2/2)),"rot":(0,pi*2,0)},
                {"loc":(-sqrt(radius**2/2),sqrt(radius**2/2),0),"rot":(0,0,pi*2)},
                {"loc":(0,sqrt(radius**2/2),-sqrt(radius**2/2)),"rot":(pi*2,0,0)},
                {"loc":(-sqrt(radius**2/2),0,sqrt(radius**2/2)),"rot":(0,pi*2,0)},
                {"loc":(0,-sqrt(radius**2/2),sqrt(radius**2/2)),"rot":(pi*2,0,0)},
                {"loc":(radius,0,0),"rot":(0,-pi*2,0)},
                {"loc":(radius,0,0),"rot":(0,0,-pi*2)},
                {"loc":(0,radius,0),"rot":(-pi*2,0,0)},
                {"loc":(0,radius,0),"rot":(0,0,-pi*2)},
                {"loc":(0,0,radius),"rot":(-pi*2,0,0)},
                {"loc":(0,0,radius),"rot":(0,-pi*2,0)},
                {"loc":(-radius,0,0),"rot":(0,-pi*2,0)},
                {"loc":(-radius,0,0),"rot":(0,0,-pi*2)},
                {"loc":(0,-radius,0),"rot":(-pi*2,0,0)},
                {"loc":(0,-radius,0),"rot":(0,0,-pi*2)},
                {"loc":(0,0,-radius),"rot":(-pi*2,0,0)},
                {"loc":(0,0,-radius),"rot":(0,-pi*2,0)},
                {"loc":(sqrt(radius**2/2),sqrt(radius**2/2),0),"rot":(0,0,-pi*2)},
                {"loc":(sqrt(radius**2/2),0,sqrt(radius**2/2)),"rot":(0,-pi*2,0)},
                {"loc":(0,sqrt(radius**2/2),sqrt(radius**2/2)),"rot":(-pi*2,0,0)},
                {"loc":(-sqrt(radius**2/2),-sqrt(radius**2/2),0),"rot":(0,0,-pi*2)},
                {"loc":(-sqrt(radius**2/2),0,-sqrt(radius**2/2)),"rot":(0,-pi*2,0)},
                {"loc":(0,-sqrt(radius**2/2),-sqrt(radius**2/2)),"rot":(-pi*2,0,0)},
                {"loc":(sqrt(radius**2/2),-sqrt(radius**2/2),0),"rot":(0,0,-pi*2)},
                {"loc":(sqrt(radius**2/2),0,-sqrt(radius**2/2)),"rot":(0,-pi*2,0)},
                {"loc":(-sqrt(radius**2/2),sqrt(radius**2/2),0),"rot":(0,0,-pi*2)},
                {"loc":(0,sqrt(radius**2/2),-sqrt(radius**2/2)),"rot":(-pi*2,0,0)},
                {"loc":(-sqrt(radius**2/2),0,sqrt(radius**2/2)),"rot":(0,-pi*2,0)},
                {"loc":(0,-sqrt(radius**2/2),sqrt(radius**2/2)),"rot":(-pi*2,0,0)},
                ]

            for status in random.sample(electrons_status,electron_num):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=status['loc'])
                bpy.ops.object.particle_system_add()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                obj = bpy.context.selected_objects
                bpy.ops.object.shade_smooth()
                
                electron_name = "electron"+ str(e_num)
                
                obj[0].name =electron_name

                obj[0].data.materials.append(electron_material)
                obj[0].particle_systems[-1].settings.count=100
                obj[0].particle_systems[-1].settings.mass=0.01
                obj[0].particle_systems[-1].settings.effector_weights.gravity=0
                obj[0].particle_systems[-1].settings.display_size = 0.05




                bpy.context.object.parent = bpy.data.objects["nucleus"]
                
                bpy.context.object.rotation_mode = 'XYZ'
                
                electron = bpy.data.objects[electron_name]


                electron.rotation_euler = (0,0,0)

                start_frame = bpy.context.scene.frame_start

                electron.keyframe_insert(data_path="rotation_euler",frame=start_frame)


                electron.rotation_euler = status['rot']

                end_frame = bpy.context.scene.frame_end = 45

                electron.keyframe_insert(data_path='rotation_euler',frame=end_frame + 1)
                e_num +=1

                bpy.context.area.type = 'GRAPH_EDITOR'             
                bpy.ops.graph.interpolation_type(type='LINEAR')     
                bpy.context.area.type = 'VIEW_3D'
            radius+=1
        bpy.ops.object.select_all(action='DESELECT')
        nucleus_obj = bpy.data.objects["nucleus"]
        nucleus_obj.select_set(True)
        bpy.context.view_layer.objects.active = nucleus_obj

        bpy.ops.screen.animation_play()


############################Atom Execute###################################

############################Spaceship Execute#############################

class GenerateSpaceship(Operator):
    """Procedurally generate 3D spaceships from a random seed."""
    bl_idname = "spaceship.add"
    bl_label = "Spaceship"
    bl_options = {'REGISTER', 'UNDO'}

    random_seed                : StringProperty(default='', name='Seed')
    num_hull_segments_min      : IntProperty (default=3, min=0, soft_max=16, name='Min. Hull Segments')
    num_hull_segments_max      : IntProperty (default=6, min=0, soft_max=16, name='Max. Hull Segments')
    create_asymmetry_segments  : BoolProperty(default=True, name='Create Asymmetry Segments')
    num_asymmetry_segments_min : IntProperty (default=1, min=1, soft_max=16, name='Min. Asymmetry Segments')
    num_asymmetry_segments_max : IntProperty (default=5, min=1, soft_max=16, name='Max. Asymmetry Segments')
    create_face_detail         : BoolProperty(default=True,  name='Create Face Detail')
    allow_horizontal_symmetry  : BoolProperty(default=True,  name='Allow Horizontal Symmetry')
    allow_vertical_symmetry    : BoolProperty(default=False, name='Allow Vertical Symmetry')
    apply_bevel_modifier       : BoolProperty(default=True,  name='Apply Bevel Modifier')
    assign_materials           : BoolProperty(default=True,  name='Assign Materials')

    def execute(self, context):
        spaceship_generator.generate_spaceship(
            self.random_seed,
            self.num_hull_segments_min,
            self.num_hull_segments_max,
            self.create_asymmetry_segments,
            self.num_asymmetry_segments_min,
            self.num_asymmetry_segments_max,
            self.create_face_detail,
            self.allow_horizontal_symmetry,
            self.allow_vertical_symmetry,
            self.apply_bevel_modifier,
            self.assign_materials)
        return {'FINISHED'}

###############################Spaceship Execute##########################

##############################Spacestation Execute#######################

class GenerateSpacestation(Operator):
    bl_idname = "mesh.generate_spacestation"
    bl_label  = "Spacestation"
    #bl_options = {'REGISTER', 'UNDO'}

    use_seed : BoolProperty(default=False, name="Use Seed")
    seed : IntProperty(default=5, name="Seed (Requires 'Use Seed')")
    parts_min : IntProperty(default=3, min=0, name="Min. Parts")
    parts_max : IntProperty(default=8, min=3, name="Max. Parts")
    torus_major_min : FloatProperty(default=2.0, min=0.1, name="Min. Torus radius")
    torus_major_max : FloatProperty(default=5.0, min=0.1, name="Max. Torus radius")
    torus_minor_min : FloatProperty(default=0.1, min=0.1, name="Min. Torus thickness")
    torus_minor_max : FloatProperty(default=0.5, min=0.1, name="Max. Torus thickness")
    bevelbox_min : FloatProperty(default=0.2, min=0.1, name="Min. Bevelbox scale")
    bevelbox_max : FloatProperty(default=0.5, min=0.1, name="Max. Bevelbox scale")
    cylinder_min : FloatProperty(default=0.5, min=0.1, name="Min. Cylinder radius")
    cylinder_max : FloatProperty(default=3.0, min=0.1, name="Max. Cylinder radius")
    cylinder_h_min : FloatProperty(default=0.3, min=0.1, name="Min. Cylinder height")
    cylinder_h_max : FloatProperty(default=1.0, min=0.1, name="Max. Cylinder height")
    storage_min : FloatProperty(default=0.5, min=0.1, name="Min. Storage height")
    storage_max : FloatProperty(default=1.0, min=0.1, name="Max. Storage height")

    def execute(self, context):
        if not self.use_seed:
            seed = random.randint(0, 100000)
        else:
            seed = self.seed
        config = {
            "min_parts":      self.parts_min,
            "max_parts":      self.parts_max,
            "torus_major_min":self.torus_major_min,
            "torus_major_max":self.torus_major_max,
            "torus_minor_min":self.torus_minor_min,
            "torus_minor_max":self.torus_minor_max,
            "bevelbox_min":   self.bevelbox_min,
            "bevelbox_max":   self.bevelbox_max,
            "cylinder_min":   self.cylinder_min,
            "cylinder_max":   self.cylinder_max,
            "cylinder_h_min": self.cylinder_h_min,
            "cylinder_h_max": self.cylinder_h_max,
            "storage_min":    self.storage_min,
            "storage_max":    self.storage_max
        }
        spacestation.generate_station(seed, config)
        return {'FINISHED'}

##############################Spacestation Execute#######################

##############################BookGen Execute#################################

class bookGen(bpy.types.Operator):
    bl_idname = "object.book_gen"
    bl_label = "BookGen"
    bl_options = {'REGISTER', 'UNDO'}

    def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8

    width : FloatProperty(name="width", default=1, min=0)
    scale : FloatProperty(name="scale", default=1, min=0)
    seed : IntProperty(name="seed", default=0)

    axis : EnumProperty(name="axis",
                                  items=(("0", "x", "distribute along the x-axis"),
                                         ("1", "y", "distribute along the y-axis"),
                                         ("2", "custom", "distribute along a custom axis")))

    angle : FloatProperty(name="angle", unit='ROTATION')

    alignment : EnumProperty(name="alignment", items=(("0", "spline", "align books at the spline (usually front in a shelf)"), ("1", "fore egde", "align books along there fore edge (usually back in a shelf)"), ("2", "center", "align along center")))

    lean_amount : FloatProperty(name="lean amount", subtype="FACTOR", min=.0, soft_max=1.0)

    lean_direction : FloatProperty(name="lean direction", subtype="FACTOR", min=-1, max=1, default=0)

    lean_angle : FloatProperty(name="lean angle", unit='ROTATION', min=.0, max=pi / 2.0, default=radians(30))
    rndm_lean_angle_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    book_height : FloatProperty(name="height", default=3.0, min=.0, unit="LENGTH")
    rndm_book_height_factor : FloatProperty(name=" random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    book_width : FloatProperty(name="width", default=0.5, min=.01, unit="LENGTH")
    rndm_book_width_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    book_depth : FloatProperty(name="depth", default=3.0, min=.0, unit="LENGTH")
    rndm_book_depth_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    cover_thickness : FloatProperty(name="cover thickness", default=0.05, min=.0, step=.02, unit="LENGTH", update=hinge_inset_guard)
    rndm_cover_thickness_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    textblock_offset : FloatProperty(name="textblock offset", default=0.1, min=.0, unit="LENGTH")
    rndm_textblock_offset_factor : FloatProperty(name="randon", default=1, min=.0, soft_max=1, subtype="FACTOR")

    spline_curl : FloatProperty(name="spline curl", default=0.01, step=.02, min=.0, unit="LENGTH")
    rndm_spline_curl_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    hinge_inset : FloatProperty(name="hinge inset", default=0.03, min=.0, step=.01, unit="LENGTH", update=hinge_inset_guard)
    rndm_hinge_inset_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    hinge_width : FloatProperty(name="hinge width", default=0.08, min=.0, step=.05, unit="LENGTH")
    rndm_hinge_width_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    spacing : FloatProperty(name="spacing", default=0.05, min=.0, unit="LENGTH")
    rndm_spacing_factor : FloatProperty(name="random", default=1, min=.0, soft_max=1, subtype="FACTOR")

    subsurf : BoolProperty(name="Add Subsurf-Modifier", default=False)
    smooth : BoolProperty(name="shade smooth", default=False)
    unwrap : BoolProperty(name="unwrap", default=True)

    cur_width = 0

    cur_offset = 0

    def check(self, context):
        self.run()

    def invoke(self, context, event):
        self.run()
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def run(self):
        time_start = time.time()

        if(self.axis == "0"):
            angle = radians(0)
        elif(self.axis == "1"):
            angle = radians(90)
        elif(self.axis == "2"):
            angle = self.angle

        parameters = {
            "scale": self.scale,
            "seed": self.seed,
            "alignment": self.alignment,
            "lean_amount": self.lean_amount,
            "lean_direction": self.lean_direction,
            "lean_angle": self.lean_angle,
            "rndm_lean_angle_factor": self.rndm_lean_angle_factor,
            "book_height": self.book_height,
            "rndm_book_height_factor": self.rndm_book_height_factor,
            "book_width": self.book_width,
            "rndm_book_width_factor": self.rndm_book_width_factor,
            "book_depth": self.book_depth,
            "rndm_book_depth_factor": self.rndm_book_depth_factor,
            "cover_thickness": self.cover_thickness,
            "rndm_cover_thickness_factor": self.rndm_cover_thickness_factor,
            "textblock_offset": self.textblock_offset,
            "rndm_textblock_offset_factor": self.rndm_textblock_offset_factor,
            "spline_curl": self.spline_curl,
            "rndm_spline_curl_factor": self.rndm_spline_curl_factor,
            "hinge_inset": self.hinge_inset,
            "rndm_hinge_inset_factor": self.rndm_hinge_inset_factor,
            "hinge_width": self.hinge_width,
            "rndm_hinge_width_factor": self.rndm_hinge_width_factor,
            "spacing": self.spacing,
            "rndm_spacing_factor": self.rndm_spacing_factor,
            "subsurf": self.subsurf,
            "smooth": self.smooth,
            "unwrap": self.unwrap
        }

        shelf = Shelf(bpy.context.scene.cursor.location, angle, self.width, parameters)
        shelf.fill()

        print("Finished: %.4f sec" % (time.time() - time_start))

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "width")
        layout.prop(self, "scale")
        layout.prop(self, "seed")

        row = layout.row(align=True)
        row.prop(self, "spacing")
        row.prop(self, "rndm_spacing_factor")

        layout.separator()
        layout.label(text = "axis")
        layout.prop(self, "axis", expand=True)
        sub = layout.column()
        sub.active = self.axis == "2"
        sub.prop(self, "angle")

        layout.separator()

        layout.label(text = "alignment")
        layout.prop(self, "alignment", expand=True)

        """layout.separator()

        leaning = layout.box()
        leaning.label(text = "leaning")
        leaning.prop(self, "lean_amount")
        leaning.prop(self, "lean_direction")
        row = leaning.row(align=True)
        row.prop(self, "lean_angle")
        row.prop(self, "rndm_lean_angle_factor")"""

        layout.separator()

        proportions = layout.box()
        proportions.label(text = "Proportions:")

        row = proportions.row(align=True)
        row.prop(self, "book_height")
        row.prop(self, "rndm_book_height_factor")

        row = proportions.row(align=True)
        row.prop(self, "book_depth")
        row.prop(self, "rndm_book_depth_factor")

        row = proportions.row(align=True)
        row.prop(self, "book_width")
        row.prop(self, "rndm_book_width_factor")

        layout.separator()

        details_box = layout.box()
        details_box.label(text = "Details:")

        row = details_box.row(align=True)
        row.prop(self, "textblock_offset")
        row.prop(self, "rndm_textblock_offset_factor")

        row = details_box.row(align=True)
        row.prop(self, "cover_thickness")
        row.prop(self, "rndm_cover_thickness_factor")

        row = details_box.row(align=True)
        row.prop(self, "spline_curl")
        row.prop(self, "rndm_spline_curl_factor")

        row = details_box.row(align=True)
        row.prop(self, "hinge_inset")
        row.prop(self, "rndm_hinge_inset_factor")

        row = details_box.row(align=True)
        row.prop(self, "hinge_width")
        row.prop(self, "rndm_hinge_width_factor")

        layout.separator()

        layout.prop(self, "subsurf")
        layout.prop(self, "smooth")
        layout.prop(self, "unwrap")

#######################BookGen Execute########################

#######################CLOCK_ADD Execute###################

class CLOCK_ADD(Operator):
    bl_idname = "clock.add"
    bl_label = "add clock"

    def execute(self,context):
        
        now = datetime.datetime.now()                        #Get the current date/time

        hour = now.hour                                      #Get hours,
        min = now.minute                                     #minutes
        sec = now.second                                     #and seconds  


        #bpy.ops.object.select_all(action='TOGGLE')            #Deselects any objects which may be selected
        #bpy.ops.object.select_all(action='TOGGLE')            #Selects all objects
        #bpy.ops.object.delete()                               #Deletes all objects to allow for new clockface (will delete old one)


        #Clock hand creation


        bpy.ops.mesh.primitive_cube_add(location=(0,0,1))                                        
        bpy.context.active_object.name = "hour hand"
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.transform.resize(value=(0.2,0.2,2.5))

        bpy.context.active_object.rotation_euler = (-0.523599*hour)+(-min*0.008727),0,0          # 30 degrees*hour to get the correct placement on clock. But at
                                                                                                   # half past the hour the hour hand should be placed somewhere between
                                                                                                   # two hour numbers, hence the min*0.5 (*0.5 converts 60 minutes to 30 degrees)

        bpy.ops.mesh.primitive_cube_add(location=(0,0,1))
        bpy.context.active_object.name = "min hand"
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.transform.resize(value=(0.2,0.2,3)) 

        bpy.context.active_object.rotation_euler = (-0.104720*min)+(-sec*0.001745),0,0             # Same as the hour hand except using the seconds to offset the minutes



        bpy.ops.mesh.primitive_cube_add(location=(0,0,1))
        bpy.context.active_object.name = "sec hand"
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.transform.resize(value=(0.1,0.1,3.5)) 

        bpy.context.active_object.rotation_euler = -0.104720*sec,0,0

        #Clock rim creation

        for i in range(0,60):
            
            
            bpy.ops.mesh.primitive_cube_add(location=(0,0,8))              #add cube

            bpy.ops.transform.resize(value=(0.1,0.1,0.5))                  #resize it

            bpy.context.scene.cursor.location = 0,0,0                      #Set cursor to origin of scene
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                #Set objects origin to cursor

            bpy.context.active_object.rotation_euler = 0.104720*i,0,0      #rotate object with radians (6 degrees)
         

        #Clock numbers creation

        for i in range(1,13):

            bpy.ops.object.text_add(rotation=(1.570796,0,1.5707960))            #Create text object
            bpy.ops.object.editmode_toggle()                                    #Go to edit mode to allow text editing
            bpy.ops.font.delete(type='PREVIOUS_WORD')                                     #Delete text
            bpy.ops.font.text_insert(text=str(i), accent=False)                 #Make the text a number (i)
            bpy.ops.object.editmode_toggle()                                    #Back to object mode to allow object manipulation

            bpy.context.active_object.name = "Text" +str(i)                     #Give a name to text of 'Texti' so they can be accessed later

            bpy.context.active_object.location = 0,0,6.5                        #Move text up to clock face edge

            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                     #Set pivot point to origin of scene
            
            bpy.ops.object.convert(target='MESH', keep_original=False)          #Convert text to mesh so rotation can be applied
            
            bpy.ops.object.transform_apply(rotation=True)                                     #Apply rotation
            
            bpy.context.active_object.rotation_euler =-0.523599*i,0,0           #Rotate numbers around clock face
            
            bpy.ops.object.transform_apply(rotation=True)                                       #Apply rotation
            
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')                   #Set origins back to center or geometry (needed for correction, below)
            
            
        #Corrects rotation for numbers on bottom half of clockface
            
        for i in range(4,9):                                                    #Loop through numbers 4-9
            
            currentText = bpy.data.objects['Text'+str(i)]                       #Get the object
            
            bpy.context.view_layer.objects.active = currentText                      #Set the object to selected
         
            bpy.context.active_object.rotation_euler = 3.141593,0,0             #Rotate number to right way up (180 degrees)
          

        bpy.context.scene.frame_current = 1    

        #Insert keyframe 1

        currentObject = bpy.data.objects['hour hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)    #Inserts first keyframe for rotation

        currentObject = bpy.data.objects['min hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

        currentObject = bpy.data.objects['sec hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)
         
        bpy.context.scene.frame_current = bpy.context.scene.frame_end           #Go to the last frame in playback range 


        #Insert Keyframe 2

        currentObject = bpy.data.objects['hour hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.000006*-bpy.context.scene.frame_end) #adds new rotation of 0.00033333*number of frames to get correct position
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

        currentObject = bpy.data.objects['min hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.000070*-bpy.context.scene.frame_end) #Same as above except 0.004 degrees
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

        currentObject = bpy.data.objects['sec hand']
        bpy.context.view_layer.objects.active= currentObject
        bpy.context.view_layer.objects.active.select_set(True)
        bpy.context.active_object.rotation_euler.x = bpy.context.active_object.rotation_euler.x+(0.004189*-bpy.context.scene.frame_end) #Same as above except 0.24 degrees
        bpy.ops.anim.keyframe_insert(type='Rotation', confirm_success=False)

        bpy.context.area.type = 'GRAPH_EDITOR'              #Change screen to graph editor to do the next operation

        bpy.ops.graph.interpolation_type(type='LINEAR')     #Set keyframe type to linear to avoid acceleration of the hands animation

        bpy.context.area.type = 'VIEW_3D'               #Change back to text editor

        bpy.ops.screen.animation_play() 

        return {'FINISHED'}

#######################CLOCK_ADD Execute###################

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


CLASSES = (
    bookGen,
    CLOCK_ADD,
    GenerateSpacestation,
    GenerateSpaceship,
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
    LEARNBGAME_SPECIES_ANIMAL,
    LEARNBGAME_SPECIES_PLANT,
    LEARNBGAME_SPECIES_MICRABE,
    )

def register():
    poqbdb.register()
    hdri.register()
    Grove_Preferences.register()
    Grove_Operator.register()
    


    for cla in CLASSES:
        register_class(cla)
    bpy.types.Scene.plants = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.animals = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.micrabes = PointerProperty(type=SPECIES_PROPERTY)
    bpy.types.Scene.planets = PointerProperty(type=PLANET_PROPERTY)
    bpy.types.Scene.molecule = PointerProperty(type=MOLECULE_PROPERTY)
    bpy.types.Scene.atoms = PointerProperty(type=ATOM_PROPERTY)
    bpy.types.Scene.brand = PointerProperty(type=BRAND_PROPERTY)
    gui.register()



def unregister():

    gui.unregister()
    global icons_collection
    for cla in CLASSES:
        unregister_class(cla)
    for icons in icons_collection.values():
        previews.remove(icons)
    icons_collection.clear()
    poqbdb.unregister()
    hdri.unregister()
    Grove_Operator.unregister()
    Grove_Preferences.unregister()




if __name__ == "__main__":
    register()
