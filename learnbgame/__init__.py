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
sys.path.append(sys.path.append("/root/Software/anaconda3/lib/python3.7/site-packages"))
import openbabel
import pybel

import json

from math import sqrt,pi

import bgl,blf

import bpy

from math import acos

from mathutils import Vector

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

##########################Variable################################

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
        obj[0].location = context.scene.cursor_location
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
        obj[0].location = bpy.context.scene.cursor_location
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
        bpy.ops.import_scene.gltf(filepath=planets_dir+"/" + planet_name +".glb")
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
        obj[0].location = bpy.context.scene.cursor_location

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
        register_class(cla)
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
        unregister_class(cla)
    for icons in icons_collection.values():
        previews.remove(icons)
    icons_collection.clear()


if __name__ == "__main__":
    register()
