# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

"""
This script stores the operators for CellBlender. As such, it is responsible
for what the buttons do when pressed (amongst other things).

"""

# blender imports
import bpy
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
import mathutils

# python imports
import array
import glob
import os
import random
import re
import subprocess
import time
import shutil
import datetime

import cellblender
from . import data_model
# import cellblender.data_model
# import cellblender_source_info
from cellblender.utils import project_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl

# from . import ParameterSpace


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#CellBlender Operators:

global_mol_file_list = []



class MCELL_OT_upgrade(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgrade"
    bl_label = "Upgrade Blend File"
    bl_description = "Upgrade the data from a previous version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade Operator called" )
        data_model.upgrade_properties_from_data_model ( context )
        return {'FINISHED'}


class MCELL_OT_upgradeRC3(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgraderc3"
    bl_label = "Upgrade RC3/4 Blend File"
    bl_description = "Upgrade the data from an RC3/4 version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade RC3 Operator called" )
        data_model.upgrade_RC3_properties_from_data_model ( context )
        return {'FINISHED'}



class MCELL_OT_delete(bpy.types.Operator):
    """This is the Delete operator called when the user presses the "Delete Properties" button"""
    bl_idname = "mcell.delete"
    bl_label = "Delete CellBlender Collection Properties"
    bl_description = "Delete CellBlender Collection Properties"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Deleting CellBlender Collection Properties" )
        mcell = context.scene.mcell
        mcell.remove_properties(context)
        print ( "Finished Deleting CellBlender Collection Properties" )
        return {'FINISHED'}


class MCELL_OT_create_partitions_object(bpy.types.Operator):
    bl_idname = "mcell.create_partitions_object"
    bl_label = "Show Partition Boundaries"
    bl_description = "Create a representation of the partition boundaries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene_objs = scene.objects
        objs = bpy.data.objects
        meshes = bpy.data.meshes
        if not "partitions" in objs:
            old_active_object = bpy.context.active_object
            # Add a box that represents the partitions' boundaries
            bpy.ops.mesh.primitive_cube_add()
            partition_object = bpy.context.active_object
            # Prevent user from manipulating the box, because I don't yet have
            # a good way of updating the partitions when the box object is
            # moved/scaled in the 3D view window
            scene.objects.active = old_active_object
            partition_object.select = False
            partition_object.hide_select = True
            # Set draw_type to wireframe so the user can see what's inside
            partition_object.draw_type = 'WIRE'
            partition_object.name = "partitions"
            partition_mesh = partition_object.data
            partition_mesh.name = "partitions"
            transform_x_partition_boundary(self, context)
            transform_y_partition_boundary(self, context)
            transform_z_partition_boundary(self, context)

        return {'FINISHED'}


class MCELL_OT_remove_partitions_object(bpy.types.Operator):
    bl_idname = "mcell.remove_partitions_object"
    bl_label = "Hide Partition Boundaries"
    bl_description = "Remove a representation of the partition boundaries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene_objects = scene.objects
        objects = bpy.data.objects
        meshes = bpy.data.meshes
        if "partitions" in scene_objects:
            partition_object = scene_objects["partitions"]
            partition_mesh = partition_object.data
            scene_objects.unlink(partition_object)
            objects.remove(partition_object)
            meshes.remove(partition_mesh)

        return {'FINISHED'}


class MCELL_OT_auto_generate_boundaries(bpy.types.Operator):
    bl_idname = "mcell.auto_generate_boundaries"
    bl_label = "Automatically Generate Boundaries"
    bl_description = ("Automatically generate partition boundaries based off "
                      "of Model Objects list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        partitions = mcell.partitions
        object_list = mcell.model_objects.object_list
        first_time = True
        for obj in object_list:
            try:
                obj = bpy.data.objects[obj.name]
                obj_matrix = obj.matrix_world
                vertices = obj.data.vertices
                for vert in vertices:
                    # Transform local coordinates to global coordinates
                    (x, y, z) = obj_matrix * vert.co
                    if first_time:
                        x_min = x_max = x
                        y_min = y_max = y
                        z_min = z_max = z
                        first_time = False
                    else:
                        # Check for x max and min
                        if x > x_max:
                            x_max = x
                        elif x < x_min:
                            x_min = x
                        # Check for y max and min
                        if y > y_max:
                            y_max = y
                        elif y < y_min:
                            y_min = y
                        # Check for z max and min
                        if z > z_max:
                            z_max = z
                        elif z < z_min:
                            z_min = z
            # In case object was deleted, but still in model objects list
            except KeyError:
                pass

        # If we don't iterate through object_list, then we don't have values
        # for x_min, x_max, etc, therefore we need to skip over setting bounds
        if not first_time:
            partitions.x_start = x_min
            partitions.x_end = x_max
            partitions.y_start = y_min
            partitions.y_end = y_max
            partitions.z_start = z_min
            partitions.z_end = z_max

        return {'FINISHED'}


def transform_x_partition_boundary(self, context):
    """ Transform the partition object along the x-axis. """

    partitions = context.scene.mcell.partitions
    x_start = partitions.x_start
    x_end = partitions.x_end
    x_step = partitions.x_step
    partitions.x_step = check_partition_step(
        self, context, x_start, x_end, x_step)
    transform_partition_boundary(self, context, x_start, x_end, 0)


def transform_y_partition_boundary(self, context):
    """ Transform the partition object along the y-axis. """

    partitions = context.scene.mcell.partitions
    y_start = partitions.y_start
    y_end = partitions.y_end
    y_step = partitions.y_step
    partitions.y_step = check_partition_step(
        self, context, y_start, y_end, y_step)
    transform_partition_boundary(self, context, y_start, y_end, 1)


def transform_z_partition_boundary(self, context):
    """ Transform the partition object along the z-axis. """

    partitions = context.scene.mcell.partitions
    z_start = partitions.z_start
    z_end = partitions.z_end
    z_step = partitions.z_step
    partitions.z_step = check_partition_step(
        self, context, z_start, z_end, z_step)
    transform_partition_boundary(self, context, z_start, z_end, 2)


def transform_partition_boundary(self, context, start, end, xyz_index):
    """ Transform the partition object along the provided axis.

    Change the scaling and location of the cube that represents partition
    boundaries. Also, make sure the step lengths are valid.

    """

    difference = end-start
    # Scale works this way, because default Cube is 2x2x2
    half_difference = scale = difference/2
    # The object center of the partition boundaries (i.e. the box)
    location = start + half_difference
    # Move the partition boundary object if it exists
    if "partitions" in bpy.data.objects:
        partition_object = bpy.data.objects["partitions"]
        partition_object.location[xyz_index] = location
        partition_object.scale[xyz_index] = scale


def check_x_partition_step(self, context):
    """ Make sure the partition's step along the x-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        x_start = partitions.x_start
        x_end = partitions.x_end
        x_step = partitions.x_step
        partitions.x_step = check_partition_step(
            self, context, x_start, x_end, x_step)
        partitions.recursion_flag = False


def check_y_partition_step(self, context):
    """ Make sure the partition's step along the y-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        y_start = partitions.y_start
        y_end = partitions.y_end
        y_step = partitions.y_step
        partitions.y_step = check_partition_step(
            self, context, y_start, y_end, y_step)
        partitions.recursion_flag = False


def check_z_partition_step(self, context):
    """ Make sure the partition's step along the z-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        z_start = partitions.z_start
        z_end = partitions.z_end
        z_step = partitions.z_step
        partitions.z_step = check_partition_step(
            self, context, z_start, z_end, z_step)
        partitions.recursion_flag = False


def check_partition_step(self, context, start, end, step):
    """ Make sure the partition's step along the provided axis is valid. """

    difference = end-start
    # Scale works this way, because default Cube is 2x2x2
    half_difference = scale = difference/2
    # The object center of the partition boundaries (i.e. the box)
    location = start + half_difference
    # Ensure step length isn't larger than partition range
    if abs(step) > abs(difference):
        step = difference
    # Make sure partition range and step length are compatible
    # Good:
    # "PARTITION_X = [[-1.0 TO 1.0 STEP 0.2]]" or
    # "PARTITION_X = [[1.0 TO -1.0 STEP -0.2]]"
    # Bad:
    # "PARTITION_X = [[-1.0 TO 1.0 STEP -0.2]]" or
    # "PARTITION_X = [[1.0 TO -1.0 STEP 0.2]]"
    # x_scale < 0 means that x_start > x_end (e.g "1.0 TO -1.0")
    if ((scale < 0 and step > 0) or (scale > 0 and step < 0)):
        step *= -1
    return step

############### DB: The following two classes are included to create a parameter input panel: only relevant for BNG, SBML or other model import #################
class MCELL_OT_parameter_add(bpy.types.Operator):
    bl_idname = "mcell.parameter_add"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.parameters.parameter_list.add()
        mcell.parameters.active_par_index = len(mcell.parameters.parameter_list)-1
        mcell.parameters.parameter_list[
            mcell.parameters.active_par_index].name = "Parameter"
        return {'FINISHED'}
	
class MCELL_OT_parameter_remove(bpy.types.Operator):
    bl_idname = "mcell.parameter_remove"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.parameters.parameter_list.remove(mcell.parameters.active_par_index)
        mcell.parameters.active_par_index = mcell.parameters.active_par_index-1
        if (mcell.parameters.active_par_index < 0):
            mcell.parameters.active_par_index = 0

        return {'FINISHED'}	
	
#########################################################################################################################################


class MCELL_OT_reaction_add(bpy.types.Operator):
    bl_idname = "mcell.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add a new reaction to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.add()
        mcell.reactions.active_rxn_index = len(mcell.reactions.reaction_list)-1
        rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
        rxn.init_properties(mcell.parameter_system)
        check_reaction(self, context)
        return {'FINISHED'}


class MCELL_OT_reaction_remove(bpy.types.Operator):
    bl_idname = "mcell.reaction_remove"
    bl_label = "Remove Reaction"
    bl_description = "Remove selected reaction from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.remove(mcell.reactions.active_rxn_index)
        mcell.reactions.active_rxn_index = mcell.reactions.active_rxn_index-1
        if (mcell.reactions.active_rxn_index < 0):
            mcell.reactions.active_rxn_index = 0

        if mcell.reactions.reaction_list:
            check_reaction(self, context)
        else:
            update_release_pattern_rxn_name_list()

        return {'FINISHED'}


class MCELL_OT_add_variable_rate_constant(bpy.types.Operator):
    """ Create variable rate constant text object from a file.

    Create a text object from an existing text file that represents the
    variable rate constant. This ensures that the variable rate constant is
    actually stored in the blend. Although, ultimately, this text object will
    be exported as another text file in the project directory when the MDLs are
    exported so it can be used by MCell.
    """

    bl_idname = "mcell.variable_rate_add"
    bl_label = "Add Variable Rate Constant"
    bl_description = "Add a variable rate constant to a reaction."
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        rxn = mcell.reactions.reaction_list[
            mcell.reactions.active_rxn_index]
        
        rxn.load_variable_rate_file ( context, self.filepath )
        
        """
        # Moved to cellblender_properties.py / MCellReactionProperty
        rxn.variable_rate = os.path.basename(self.filepath)
        texts = bpy.data.texts

        # Overwrite existing text objects.
        # XXX: Add warning.
        if rxn.variable_rate in texts:
            texts.remove(texts[rxn.variable_rate])

        # Create the text object from the text file
        try:
            with open(self.filepath, "r") as rate_file:
                rate_string = rate_file.read()
            text_object = texts.new(rxn.variable_rate)
            # Should add in some simple error checking
            text_object.write(rate_string)
            rxn.variable_rate_valid = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            rxn.variable_rate_valid = False
        """

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def check_reaction(self, context):
    """Checks for duplicate or illegal reaction. Cleans up formatting."""

    mcell = context.scene.mcell

    #Retrieve reaction
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    for item in rxn.type_enum:
        if rxn.type == item[0]:
            rxtype = item[1]

    status = ""

    # Clean up rxn.reactants only if necessary to avoid infinite recursion.
    reactants = rxn.reactants.replace(" ", "")
    reactants = reactants.replace("+", " + ")
    reactants = reactants.replace("@", " @ ")
    if reactants != rxn.reactants:
        rxn.reactants = reactants

    # Clean up rxn.products only if necessary to avoid infinite recursion.
    products = rxn.products.replace(" ", "")
    products = products.replace("+", " + ")
    if products != rxn.products:
        rxn.products = products

    # Check for duplicate reaction
    rxn.name = ("%s %s %s") % (rxn.reactants, rxtype, rxn.products)
    rxn_keys = mcell.reactions.reaction_list.keys()
    if rxn_keys.count(rxn.name) > 1:
        status = "Duplicate reaction: %s" % (rxn.name)

    # Does the reaction need reaction directionality (i.e. there is at least
    # one surface molecule or a surface class)
    need_rxn_direction = False
    # Are there ever any reactants, products, or surface classes that don't
    # specify reaction directionality?
    ever_no_direction = False
    # Conversely, are there ever any reactants/products/SCs which do?
    ever_direction = False

    # Check syntax of reactant specification
    mol_list = mcell.molecules.molecule_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mol_surf_class_filter = \
        r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
    # Check the syntax of the surface class if one exists
    if rxn.reactants.count(" @ ") == 1:
        need_rxn_direction = True
        reactants_no_surf_class, surf_class = rxn.reactants.split(" @ ")
        match = re.match(mol_surf_class_filter, surf_class)
        if match is None:
            status = "Illegal surface class name: %s" % (surf_class)
        else:
            surf_class_name = match.group(1)
            surf_class_direction = match.group(2)
            if not surf_class_name in surf_class_list:
                status = "Undefined surface class: %s" % (surf_class_name)
            if not surf_class_direction:
                status = ("No directionality specified for surface class: "
                          "%s" % (surf_class_name))
    else:
        reactants_no_surf_class = rxn.reactants
        surf_class = None

    reactants = reactants_no_surf_class.split(" + ")
    for reactant in reactants:
        match = re.match(mol_surf_class_filter, reactant)
        if match is None:
            status = "Illegal reactant name: %s" % (reactant)
            break
        else:
            mol_name = match.group(1)
            mol_direction = match.group(2)
            if not mol_name in mol_list:
                status = "Undefined molecule: %s" % (mol_name)
            else:
                if mol_list[mol_name].type == '2D':
                    need_rxn_direction = True
                if not mol_direction:
                    ever_no_direction = True
                else:
                    ever_direction = True

    # Check syntax of product specification
    if rxn.products == "NULL":
        if rxn.type == 'reversible':
            rxn.type = 'irreversible'
    else:
        products = rxn.products.split(" + ")
        for product in products:
            match = re.match(mol_surf_class_filter, product)
            if match is None:
                status = "Illegal product name: %s" % (product)
                break
            else:
                mol_name = match.group(1)
                mol_direction = match.group(2)
                if not mol_name in mol_list:
                    status = "Undefined molecule: %s" % (mol_name)
                else:
                    if mol_list[mol_name].type == '2D':
                        need_rxn_direction = True
                    if not mol_direction:
                        ever_no_direction = True
                    else:
                        ever_direction = True

    # Is directionality required (i.e. any surface molecules or surface class)?
    # If so, is it missing anywhere in the rxn?
    if need_rxn_direction and ever_no_direction:
        status = "Reaction directionality required (e.g. semicolon after name)"
    # Is reaction directionality specified despite there only being vol. mols?
    if not surf_class and not need_rxn_direction and ever_direction:
        status = "Unneeded reaction directionality"

    # Check for a variable rate constant
    if rxn.variable_rate_switch:
        # Make sure that the file has not been deleted
        if rxn.variable_rate not in bpy.data.texts:
            rxn.variable_rate_valid = False

        # Check if file doesn't exist, isn't UTF8, is a directory, etc
        if not rxn.variable_rate_valid:
            status = ("Variable rate constant is not valid: "
                      "%s" % rxn.variable_rate)
        # Variable rate constants only support irreversible reactions
        elif rxn.variable_rate_valid and rxn.type == 'reversible':
            rxn.type = 'irreversible'

    rxn_name_status = check_reaction_name()
    if rxn_name_status:
        status = rxn_name_status

    rxn.status = status
    update_release_pattern_rxn_name_list()


def check_reaction_name():
    """ Make sure the reaction name is legal.

    Also make sure that it is available for counting and as a release pattern.

    """

    mcell = bpy.context.scene.mcell
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    rxn_name = rxn.rxn_name
    status = ""

    # Check for illegal names
    # (Starts with a letter. No special characters. Can be blank.)
    reaction_name_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)|(^$)"
    m = re.match(reaction_name_filter, rxn_name)
    if m is None:
        status = "Reaction name error: %s" % (rxn_name)

    return status


class MCELL_OT_surf_class_props_add(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_add"
    bl_label = "Add Surface Class Properties"
    bl_description = "Add new surface class properties to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.add()
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
        check_surf_class_props(self, context)

        return {'FINISHED'}


class MCELL_OT_surf_class_props_remove(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_remove"
    bl_label = "Remove Surface Class Properties"
    bl_description = "Remove surface class properties from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.remove(
            active_surf_class.active_surf_class_props_index)
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
        if (active_surf_class.active_surf_class_props_index < 0):
            active_surf_class.active_surf_class_props_index = 0

        return {'FINISHED'}


class MCELL_OT_surface_class_add(bpy.types.Operator):
    bl_idname = "mcell.surface_class_add"
    bl_label = "Add Surface Class"
    bl_description = "Add a new surface class to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.add()
        surf_class.active_surf_class_index = len(
            surf_class.surf_class_list) - 1
        surf_class.surf_class_list[
            surf_class.active_surf_class_index].name = "Surface_Class"

        return {'FINISHED'}


class MCELL_OT_surface_class_remove(bpy.types.Operator):
    bl_idname = "mcell.surface_class_remove"
    bl_label = "Remove Surface Class"
    bl_description = "Remove selected surface class from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.remove(surf_class.active_surf_class_index)
        surf_class.active_surf_class_index -= 1
        if (surf_class.active_surf_class_index < 0):
            surf_class.active_surf_class_index = 0

        if surf_class.surf_class_list:
            check_surface_class(self, context)
        else:
            surf_class.surf_class_status = ""

        return {'FINISHED'}


def check_surface_class(self, context):
    """Checks for duplicate or illegal surface class name"""

    surf_class = context.scene.mcell.surface_classes
    active_surf_class = surf_class.surf_class_list[
        surf_class.active_surf_class_index]

    status = ""

    # Check for duplicate names
    surf_class_keys = surf_class.surf_class_list.keys()
    if surf_class_keys.count(active_surf_class.name) > 1:
        status = "Duplicate Surface Class: %s" % (active_surf_class.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    surf_class_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(surf_class_filter, active_surf_class.name)
    if m is None:
        status = "Surface Class name error: %s" % (active_surf_class.name)

    active_surf_class.status = status

    return


def convert_surf_class_str(surf_class_type):
    """Format MDL language (surf class type) for viewing in the UI"""

    if surf_class_type == "ABSORPTIVE":
        surf_class_type = "Absorptive"
    elif surf_class_type == "TRANSPARENT":
        surf_class_type = "Transparent"
    elif surf_class_type == "REFLECTIVE":
        surf_class_type = "Reflective"
    elif surf_class_type == "CLAMP_CONCENTRATION":
        surf_class_type = "Clamp Concentration"

    return(surf_class_type)


def convert_orient_str(orient):
    """Format MDL language (orientation) for viewing in the UI"""

    if orient == "'":
        orient = "Top/Front"
    elif orient == ",":
        orient = "Bottom/Back"
    elif orient == ";":
        orient = "Ignore"

    return(orient)


def check_surf_class_props(self, context):
    """Checks for illegal/undefined molecule names in surf class properties"""

    mcell = context.scene.mcell
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    mol_list = mcell.molecules.molecule_list
    molecule = surf_class_props.molecule
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
        molecule, orient, surf_class_type)

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    m = re.match(mol_filter, molecule)
    if m is None:
        status = "Molecule name error: %s" % (molecule)
    else:
        # Check for undefined names
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = "Undefined molecule: %s" % (mol_name)

    surf_class_props.status = status

    return


class MCELL_OT_mod_surf_regions_add(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_add"
    bl_label = "Assign Surface Class"
    bl_description = "Assign a surface class to a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.add()
        mod_surf_regions.active_mod_surf_regions_index = len(
            mod_surf_regions.mod_surf_regions_list) - 1
        check_active_mod_surf_regions(self, context)

        return {'FINISHED'}


class MCELL_OT_mod_surf_regions_remove(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_remove"
    bl_label = "Remove Surface Class Assignment"
    bl_description = "Remove a surface class assignment from a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.remove(
            mod_surf_regions.active_mod_surf_regions_index)
        mod_surf_regions.active_mod_surf_regions_index -= 1
        if (mod_surf_regions.active_mod_surf_regions_index < 0):
            mod_surf_regions.active_mod_surf_regions_index = 0

        return {'FINISHED'}


def check_mod_surf_regions(self, context):
    """Make sure the surface class name is valid and format the list entry"""
    print ( "  Checking the mod_surf_region for " + str(self) )

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = self
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    region_list = []

    # At some point during the building of properties the object name is "" which causes problems. So skip it for now.
    if len(object_name) > 0:
        try:
            region_list = bpy.data.objects[object_name].mcell.regions.region_list
        except KeyError as kerr:
            # The object name in mod_surf_regions isn't a blender object - print a stack trace ...
            print ( "Error: The object name (\"" + object_name + "\") isn't a blender object ... at this time?" )
            fail_error = sys.exc_info()
            print ( "    Error Type: " + str(fail_error[0]) )
            print ( "    Error Value: " + str(fail_error[1]) )
            tb = fail_error[2]
            # tb.print_stack()
            print ( "=== Traceback Start ===" )
            traceback.print_tb(tb)
            traceback.print_stack()
            print ( "=== Traceback End ===" )
            pass


    # Format the entry as it will appear in the Modify Surface Regions
    active_mod_surf_regions.name = ("Surface Class: %s   Object: %s   "
                                    "Region: %s" % (
                                        surf_class_name, object_name,
                                        region_name))

    status = ""

    # Make sure the user entered surf class is in Defined Surface Classes list
    if not surf_class_name in surf_class_list:
        status = "Undefined surface class: %s" % surf_class_name
    # Make sure the user entered object name is in the Model Objects list
    elif not active_mod_surf_regions.object_name in obj_list:
        status = "Undefined object: %s" % active_mod_surf_regions.object_name
    # Make sure the user entered object name is in the object's
    # Surface Region list
    elif not region_name in region_list:
        status = "Undefined region: %s" % region_name

    active_mod_surf_regions.status = status

    return


def check_active_mod_surf_regions(self, context):
    """This calls check_mod_surf_regions on the active mod_surf_regions"""

    mcell = context.scene.mcell
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    # This is a round-about way to call "check_mod_surf_regions" above
    # Maybe these functions belong in the MCellModSurfRegionsProperty class
    # Leave them here for now to not disturb too much code at once

    ######  commented out temporarily (causes names to not be built):
    active_mod_surf_regions.check_properties_after_building(context)
    # The previous line appears to cause the following problem:
    """
        Done removing all MCell Properties.
        Overwriting properites based on data in the data model dictionary
        Overwriting the parameter_system properties
        Parameter System building Properties from Data Model ...
        Overwriting the initialization properties
        Overwriting the define_molecules properties
        Overwriting the define_reactions properties
        Overwriting the release_sites properties
        Overwriting the define_release_patterns properties
        Overwriting the define_surface_classes properties
        Overwriting the modify_surface_regions properties
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
        Error: The object name ("") isn't a blender object
            Error Type: <class 'KeyError'>
            Error Value: 'bpy_prop_collection[key]: key "" not found'
        === Traceback Start ===
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 842, in check_mod_surf_regions
            region_list = bpy.data.objects[active_mod_surf_regions.object_name].mcell.regions.region_list
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 78, in execute
            data_model.upgrade_properties_from_data_model ( context )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/data_model.py", line 298, in upgrade_properties_from_data_model
            mcell.build_properties_from_data_model ( context, dm )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 4986, in build_properties_from_data_model
            self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 2755, in build_properties_from_data_model
            sr.build_properties_from_data_model ( context, s )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 774, in build_properties_from_data_model
            self.surf_class_name = dm["surf_class_name"]
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 892, in check_active_mod_surf_regions
            active_mod_surf_regions.check_properties_after_building(context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 780, in check_properties_after_building
            cellblender_operators.check_mod_surf_regions(self, context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 853, in check_mod_surf_regions
            traceback.print_stack()
        === Traceback End ===
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
        Overwriting the model_objects properties
        Data model contains Cube
        Overwriting the viz_output properties
        Overwriting the mol_viz properties
    """
    return


class MCELL_OT_release_pattern_add(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_add"
    bl_label = "Add Release Pattern"
    bl_description = "Add a new Release Pattern to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_patterns.release_pattern_list.add()
        mcell.release_patterns.active_release_pattern_index = len(
            mcell.release_patterns.release_pattern_list)-1
        rel_pattern = mcell.release_patterns.release_pattern_list[
            mcell.release_patterns.active_release_pattern_index]
        rel_pattern.name = "Release_Pattern"
        rel_pattern.init_properties(mcell.parameter_system)
        check_release_pattern_name(self, context)

        return {'FINISHED'}


class MCELL_OT_release_pattern_remove(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_remove"
    bl_label = "Remove Release Pattern"
    bl_description = "Remove selected Release Pattern from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_patterns.release_pattern_list.remove(
            mcell.release_patterns.active_release_pattern_index)
        mcell.release_patterns.active_release_pattern_index -= 1
        if (mcell.release_patterns.active_release_pattern_index < 0):
            mcell.release_patterns.active_release_pattern_index = 0

        if mcell.release_patterns.release_pattern_list:
            check_release_pattern_name(self, context)
        else:
            update_release_pattern_rxn_name_list()

        return {'FINISHED'}


def check_release_pattern_name(self, context):
    """Checks for duplicate or illegal release pattern name."""

    mcell = context.scene.mcell
    rel_pattern_list = mcell.release_patterns.release_pattern_list
    rel_pattern = rel_pattern_list[
        mcell.release_patterns.active_release_pattern_index]

    status = ""

    # Check for duplicate release pattern name
    rel_pattern_keys = rel_pattern_list.keys()
    if rel_pattern_keys.count(rel_pattern.name) > 1:
        status = "Duplicate release pattern: %s" % (rel_pattern.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_pattern_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_pattern_filter, rel_pattern.name)
    if m is None:
        status = "Release Pattern name error: %s" % (rel_pattern.name)

    rel_pattern.status = status
    update_release_pattern_rxn_name_list()


class MCELL_OT_release_site_add(bpy.types.Operator):
    bl_idname = "mcell.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add a new Molecule Release Site to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_sites.mol_release_list.add()
        mcell.release_sites.active_release_index = len(
            mcell.release_sites.mol_release_list)-1
        mcell.release_sites.mol_release_list[
            mcell.release_sites.active_release_index].name = "Release_Site"

        relsite = mcell.release_sites.mol_release_list[mcell.release_sites.active_release_index]

        relsite.init_properties(mcell.parameter_system)
            
        check_release_molecule(context)

        return {'FINISHED'}


class MCELL_OT_release_site_remove(bpy.types.Operator):
    bl_idname = "mcell.release_site_remove"
    bl_label = "Remove Release Site"
    bl_description = "Remove selected Molecule Release Site from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_sites.mol_release_list.remove(
            mcell.release_sites.active_release_index)
        mcell.release_sites.active_release_index -= 1
        if (mcell.release_sites.active_release_index < 0):
            mcell.release_sites.active_release_index = 0

        if mcell.release_sites.mol_release_list:
            check_release_site(self, context)

        return {'FINISHED'}


def check_release_site(self, context):
    """ Thin wrapper for check_release_site. """

    check_release_site_wrapped(context)


def check_release_site_wrapped(context):
    """ Make sure that the release site is valid. """

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]

    name_status = check_release_site_name(context)
    molecule_status = check_release_molecule(context)
    object_status = check_release_object_expr(context)

    if name_status:
        rel.status = name_status
    elif molecule_status:
        rel.status = molecule_status
    elif object_status and rel.shape == 'OBJECT':
        rel.status = object_status
    else:
        rel.status = ""

    return


def check_release_site_name(context):
    """Checks for duplicate or illegal release site name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]

    status = ""

    # Check for duplicate release site name
    rel_keys = rel_list.keys()
    if rel_keys.count(rel.name) > 1:
        status = "Duplicate release site: %s" % (rel.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_filter, rel.name)
    if m is None:
        status = "Release Site name error: %s" % (rel.name)

    return status


def check_release_molecule(context):
    """Checks for illegal release site molecule name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    mol = rel.molecule

    mol_list = mcell.molecules.molecule_list

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, mol)
    if m is None:
        status = "Molecule name error: %s" % (mol)
    else:
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = "Undefined molecule: %s" % (mol_name)
        # Only change if necessary to avoid infinite recursion
        elif (mol_list[mol_name].type == '2D') and (not rel.shape == 'OBJECT'):
            rel.shape = 'OBJECT'

    return status


def check_release_object_expr(context):
    """Checks for illegal release object name."""

    scn = context.scene
    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    obj_list = mcell.model_objects.object_list
    obj_expr = rel.object_expr

    status = ""

    # Check for illegal names. (Starts with a letter. No special characters.)
    # May be only object name or object name and region (e.g. object[reg].)
    obj_reg_filter = (r"(?P<obj_reg>(?P<obj_name>^[A-Za-z]+[0-9A-Za-z_.]*)(\[)"
                      "(?P<reg_name>[A-Za-z]+[0-9A-Za-z_.]*)(\])$)|"
                      "(?P<obj_name_only>^([A-Za-z]+[0-9A-Za-z_.]*)$)")

    expr_filter = r"[\+\-\*\(\)]"

    expr_vars = re.sub(expr_filter, " ", obj_expr).split()
    
    #print ( "Checking Release Objects: " + str(expr_vars) + " in " + str([k for k in obj_list]) )

    if not obj_expr:
        status = "Object name error"

    for var in expr_vars:
        #print ( "Checking " + str(var) )
        m = re.match(obj_reg_filter, var)
        if m is None:
            #print ( "Match returned None" )
            status = "Object name error: %s" % (var)
            #print ( status )
            break
        else:
            #print ( "Match returned " + str(m) )
            if m.group("obj_reg") is not None:
                obj_name = m.group("obj_name")
                reg_name = m.group("reg_name")
                if not obj_name in obj_list or obj_list[obj_name].status:
                    status = "Undefined/illegal object: %s" % (obj_name)
                    #print ( status )
                    break
                obj = scn.objects[obj_name]
                if reg_name != "ALL":
                    if (not obj.mcell.regions.region_list or 
                            reg_name not in obj.mcell.regions.region_list):
                        status = "Undefined region: %s" % (reg_name)
                        #print ( status )
                        break
            else:
                obj_name = m.group("obj_name_only")
                if not obj_name in obj_list or obj_list[obj_name].status:
                    status = "Undefined/illegal object: %s" % (obj_name)
                    #print ( status )
                    break

    return status


def is_executable(binary_path):
    """Checks for nonexistant or non-executable binary file"""
    is_exec = False
    try:
        st = os.stat(binary_path)
        if os.path.isfile(binary_path):
            if os.access(binary_path, os.X_OK):
                is_exec = True
    except Exception as err:
        is_exec = False
    return is_exec




def check_python_binary(self, context):
    """Callback to check for python executable"""
    mcell = context.scene.mcell
    binary_path = mcell.cellblender_preferences.python_binary
    mcell.cellblender_preferences.python_binary_valid = is_executable(binary_path)
    bpy.ops.mcell.preferences_save(name='Cb')
    return None



class MCELL_OT_set_python_binary(bpy.types.Operator):
    bl_idname = "mcell.set_python_binary"
    bl_label = "Set Python Binary"
    bl_description = "Set Python Binary"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.cellblender_preferences.python_binary = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def check_bionetgen_location(self, context):
    """Callback to check for mcell executable"""
    mcell = context.scene.mcell
    application_path = mcell.cellblender_preferences.bionetgen_location
    mcell.cellblender_preferences.bionetgen_location_valid = is_executable(application_path)
    bpy.ops.mcell.preferences_save(name='Cb')
    return None


class MCELL_OT_set_check_bionetgen_location(bpy.types.Operator):
    bl_idname = "mcell.set_bionetgen_location"
    bl_label = "Set BioNetGen Location"
    bl_description = ("Set BioNetGen Location. If needed, download at "
                      "bionetgen.org")
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.cellblender_preferences.bionetgen_location = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def check_mcell_binary(self, context):
    """Callback to check for mcell executable"""
    mcell = context.scene.mcell
    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = is_executable(binary_path)
    bpy.ops.mcell.preferences_save(name='Cb')
    return None


class MCELL_OT_save_preferences(AddPresetBase, bpy.types.Operator):
    """Save CellBlender Preferences."""

    bl_idname = "mcell.preferences_save"
    bl_label = "Save Preferences"
    # This needs to be the same name as the preset menu class in
    # cellblender_panels
    preset_menu = "MCELL_MT_presets" 

    preset_defines = [
        "scene = bpy.context.scene"
    ]

    # These are the values which will be saved/loaded
    preset_values = [
        "scene.mcell.cellblender_preferences.mcell_binary",
        "scene.mcell.cellblender_preferences.bionetgen_location",
        "scene.mcell.cellblender_preferences.python_binary",
        "scene.mcell.cellblender_preferences.decouple_export_run",
        "scene.mcell.cellblender_preferences.invalid_policy",
    ]

    # This needs to be the same as what's in the menu class
    preset_subdir = "cellblender" 


# Operators can't be callbacks, so we need this function.
def save_preferences(self, context):
    bpy.ops.mcell.preferences_save(name='Cb')
    return None


class MCELL_OT_reset_preferences(bpy.types.Operator):
    """Reset CellBlender preferences"""

    bl_idname = "mcell.preferences_reset"
    bl_label = "Reset Preferences"
    bl_description = ("Reset preferences to their original values.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.cellblender_preferences.mcell_binary = ""
        mcell.cellblender_preferences.python_binary = ""
        mcell.cellblender_preferences.bionetgen_location = ""
        mcell.cellblender_preferences.invalid_policy = 'dont_run'
        mcell.cellblender_preferences.decouple_export_run = False

        return {'FINISHED'}


@persistent
def load_preferences(context):
    """ Load CB preferences using preset on startup. """
    print ( "load post handler: cellblender_operators.load_preferences() called" )

    #active_preset = bpy.types.MCELL_MT_presets.bl_label
    #bpy.ops.script.execute_preset(
    #    filepath=preset_path, menu_idname="MCELL_MT_presets")

    # Cant use execute_preset here because of incorrect context
    # Look for existing preset named "Cb" in "cellblender" preset subdir
    # Presets are named with leading capital, but modules are lowercase
    # Therefore the preset "Cb" corresponds to the file "cb.py"
    try:
        preset_path = bpy.utils.preset_find(
            "Cb", 'cellblender', display_name=True)
        with open(preset_path, 'r') as preset_file:
            preset_string = preset_file.read()
            exec(preset_string)
    except TypeError:
        print('No preset file found')


class MCELL_OT_set_mcell_binary(bpy.types.Operator):
    bl_idname = "mcell.set_mcell_binary"
    bl_label = "Set MCell Binary"
    bl_description = ("Set MCell Binary. If needed, download at "
                      "mcell.org/download.html")
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.cellblender_preferences.mcell_binary = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MCELL_OT_run_simulation(bpy.types.Operator):
    bl_idname = "mcell.run_simulation"
    bl_label = "Run MCell Simulation"
    bl_description = "Run MCell Simulation"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):

        mcell = context.scene.mcell
        if str(mcell.run_simulation.simulation_run_control) == 'QUEUE':
            processes_list = mcell.run_simulation.processes_list
            for pl_item in processes_list:
                pid = int(pl_item.name.split(',')[0].split(':')[1])
                q_item = cellblender.simulation_queue.task_dict[pid]
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    return False
        return True

    def execute(self, context):
        mcell = context.scene.mcell

        print ( "Need to run " + str(mcell.run_simulation.simulation_run_control) )
        if str(mcell.run_simulation.simulation_run_control) == 'JAVA':
            bpy.ops.mcell.run_simulation_control_java()
        elif str(mcell.run_simulation.simulation_run_control) == 'OPENGL':
            bpy.ops.mcell.run_simulation_control_opengl()
        elif str(mcell.run_simulation.simulation_run_control) == 'COMMAND':
            bpy.ops.mcell.run_simulation_normal()
        else:
            bpy.ops.mcell.run_simulation_control_queue()
        return {'FINISHED'}


class MCELL_OT_run_simulation_control_normal(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_normal"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = is_executable ( binary_path )

        start = mcell.run_simulation.start_seed
        end = mcell.run_simulation.end_seed
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = project_files_path()
        status = ""
        # If python path was set by user, use that one. Otherwise, try to
        # automatically find it. This will probably fail on Windows unless it's
        # set in the PATH.
        if mcell.cellblender_preferences.python_binary_valid:
            python_path = mcell.cellblender_preferences.python_binary
        else:
            python_path = shutil.which("python", mode=os.X_OK)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "react_data")
                if (os.path.exists(react_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "viz_data")
                if (os.path.exists(viz_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))
                script_file_path = os.path.join(
                    script_dir_path, "run_simulations.py")

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(
                    mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[
                    mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started MCell at: " + (str(time.ctime())) + "\n")

                # We have to create a new subprocess that in turn creates a
                # multiprocessing pool, instead of directly creating it here,
                # because the multiprocessing package requires that the __main__
                # module be importable by the children.
                sp = subprocess.Popen([
                    python_path, script_file_path, mcell_binary, str(start),
                    str(end + 1), project_dir, base_name, error_file_option,
                    log_file_option, mcell_processes_str], stdout=None,
                    stderr=None)
                self.report({'INFO'}, "Simulation Running")

                # This is a hackish workaround since we can't return arbitrary
                # objects from operators or store arbitrary objects in collection
                # properties, and we need to keep track of the progress of the
                # subprocess objects in cellblender_panels.
                cellblender.simulation_popen_list.append(sp)

                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_run_simulation_control_queue(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_queue"
    bl_label = "Run MCell Simulation Using Command Queue"
    bl_description = "Run MCell Simulation Using Command Queue"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = is_executable ( binary_path )

        start_seed = mcell.run_simulation.start_seed
        end_seed = mcell.run_simulation.end_seed
        mcell_processes = mcell.run_simulation.mcell_processes
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = project_files_path()
        status = ""
        # If python path was set by user, use that one. Otherwise, try to
        # automatically find it. This will probably fail on Windows unless it's
        # set in the PATH.
        if mcell.cellblender_preferences.python_binary_valid:
            python_path = mcell.cellblender_preferences.python_binary
        else:
            python_path = shutil.which("python", mode=os.X_OK)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "react_data")
                if (os.path.exists(react_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "viz_data")
                if (os.path.exists(viz_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                cellblender.simulation_queue.python_exec = python_path
                cellblender.simulation_queue.start(mcell_processes)
                cellblender.simulation_queue.notify = True

                processes_list = mcell.run_simulation.processes_list
                for seed in range(start_seed,end_seed + 1):
                  processes_list.add()
                  mcell.run_simulation.active_process_index = len(
                      mcell.run_simulation.processes_list) - 1
                  simulation_process = processes_list[
                      mcell.run_simulation.active_process_index]

                  print("Starting MCell ... create start_time.txt file:")
                  with open(os.path.join(os.path.dirname(bpy.data.filepath),
                            "start_time.txt"), "w") as start_time_file:
                      start_time_file.write(
                          "Started MCell at: " + (str(time.ctime())) + "\n")

                  # Log filename will be log.year-month-day_hour:minute_seed.txt
                  # (e.g. log.2013-03-12_11:45_1.txt)
                  time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

                  if error_file_option == 'file':
                      error_filename = "error.%s_%d.txt" % (time_now, seed)
                  elif error_file_option == 'none':
                      error_file = subprocess.DEVNULL
                  elif error_file_option == 'console':
                      error_file = None

                  if log_file_option == 'file':
                      log_filename = "log.%s_%d.txt" % (time_now, seed)
                  elif log_file_option == 'none':
                      log_file = subprocess.DEVNULL
                  elif log_file_option == 'console':
                      log_file = None

                  mdl_filename = '%s.main.mdl' % (base_name)
                  mcell_args = '-seed %d %s' % (seed, mdl_filename)
                  proc = cellblender.simulation_queue.add_task(mcell_binary, mcell_args, project_dir)

                  self.report({'INFO'}, "Simulation Running")

                  simulation_process.name = ("PID: %d, MDL: %s, " "Seed: %d" % (proc.pid, mdl_filename, seed))

        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_kill_simulation(bpy.types.Operator):
    bl_idname = "mcell.kill_simulation"
    bl_label = "Kill Selected Simulation"
    bl_description = ("Kill/Cancel Selected Running/Queued MCell Simulation. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}


    @classmethod
    def poll(self,context):
        mcell = context.scene.mcell
        processes_list = mcell.run_simulation.processes_list
        active_index = mcell.run_simulation.active_process_index
        ap = processes_list[active_index]
        pid = int(ap.name.split(',')[0].split(':')[1])
        q_item = cellblender.simulation_queue.task_dict.get(pid)
        if q_item:
            if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                return True

    def execute(self, context):

        mcell = context.scene.mcell

        processes_list = mcell.run_simulation.processes_list
        active_index = mcell.run_simulation.active_process_index
        ap = processes_list[active_index]
        pid = int(ap.name.split(',')[0].split(':')[1])
        q_item = cellblender.simulation_queue.task_dict.get(pid)
        if q_item:
            if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                # Simulation is running or waiting in queue, so let's kill it
                cellblender.simulation_queue.kill_task(pid)

        return {'FINISHED'}


class MCELL_OT_kill_all_simulations(bpy.types.Operator):
    bl_idname = "mcell.kill_all_simulations"
    bl_label = "Kill All Simulations"
    bl_description = ("Kill/Cancel All Running/Queued MCell Simulations. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        processes_list = mcell.run_simulation.processes_list

        for p_item in processes_list:
            pid = int(p_item.name.split(',')[0].split(':')[1])
            q_item = cellblender.simulation_queue.task_dict.get(pid)
            if q_item:
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    # Simulation is running or waiting in queue, so let's kill it
                    cellblender.simulation_queue.kill_task(pid)

        return {'FINISHED'}





class MCELL_OT_run_simulation_control_opengl(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_opengl"
    bl_label = "Run MCell Simulation Control"
    bl_description = "Run MCell Simulation Control"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = is_executable ( binary_path )

        start = mcell.run_simulation.start_seed
        end = mcell.run_simulation.end_seed
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = project_files_path()
        status = ""

        if not mcell.cellblender_preferences.decouple_export_run:
            bpy.ops.mcell.export_project()

        if (mcell.run_simulation.error_list and
                mcell.cellblender_preferences.invalid_policy == 'dont_run'):
            pass
        else:
            react_dir = os.path.join(project_dir, "react_data")
            if (os.path.exists(react_dir) and
                    mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            viz_dir = os.path.join(project_dir, "viz_data")
            if (os.path.exists(viz_dir) and
                    mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            base_name = mcell.project_settings.base_name

            error_file_option = mcell.run_simulation.error_file
            log_file_option = mcell.run_simulation.log_file
            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(
                script_dir_path, "SimControl")

            processes_list = mcell.run_simulation.processes_list
            processes_list.add()
            mcell.run_simulation.active_process_index = len(
                mcell.run_simulation.processes_list) - 1
            simulation_process = processes_list[
                mcell.run_simulation.active_process_index]

            print("Starting MCell ... create start_time.txt file:")
            with open(os.path.join(os.path.dirname(bpy.data.filepath),
                      "start_time.txt"), "w") as start_time_file:
                start_time_file.write(
                    "Started MCell at: " + (str(time.ctime())) + "\n")

            # Spawn a subprocess for each simulation

            window_num = 0

            for sim_seed in range(start,end+1):
                print ("Running with seed " + str(sim_seed) )

                command_list = [
                    script_file_path,
                    ("x=%d" % ((50*window_num)%500)),
                    ("y=%d" % ((40*window_num)%400)),
                    ":",
                    mcell_binary,
                    ("-seed %s" % str(sim_seed)),
                    os.path.join(project_dir, ("%s.main.mdl" % base_name))
                  ]
                
                command_string = "Command:";
                for s in command_list:
                  command_string += " " + s
                print ( command_string )
                
                sp = subprocess.Popen ( command_list, cwd=project_dir, stdout=None, stderr=None )

                self.report({'INFO'}, "Simulation Running")

                # This is a hackish workaround since we can't return arbitrary
                # objects from operators or store arbitrary objects in collection
                # properties, and we need to keep track of the progress of the
                # subprocess objects in cellblender_panels.
                cellblender.simulation_popen_list.append(sp)
                window_num += 1


            if ((end - start) == 0):
                simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                           "Seed: %d" % (sp.pid, base_name,
                                                         start))
            else:
                simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                           "Seeds: %d-%d" % (sp.pid, base_name,
                                                             start, end))

        mcell.run_simulation.status = status

        return {'FINISHED'}



class MCELL_OT_run_simulation_control_java(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_java"
    bl_label = "Run MCell Simulation Control"
    bl_description = "Run MCell Simulation Control"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = is_executable ( binary_path )

        start = mcell.run_simulation.start_seed
        end = mcell.run_simulation.end_seed
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = project_files_path()
        status = ""
        # If python path was set by user, use that one. Otherwise, try to
        # automatically find it. This will probably fail on Windows unless it's
        # set in the PATH.
        if mcell.cellblender_preferences.python_binary_valid:
            python_path = mcell.cellblender_preferences.python_binary
        else:
            python_path = shutil.which("python", mode=os.X_OK)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "react_data")
                if (os.path.exists(react_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "viz_data")
                if (os.path.exists(viz_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))
                script_file_path = os.path.join(
                    script_dir_path, "SimControl.jar")

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(
                    mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[
                    mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started MCell at: " + (str(time.ctime())) + "\n")

                # Create a subprocess for each simulation
                
                window_num = 0

                for sim_seed in range(start,end+1):
                    print ("Running with seed " + str(sim_seed) )
                    
                    command_list = [
                        'java',
                        '-jar',
                        script_file_path,
                        ("x=%d" % ((50*(1+window_num))%500)),
                        ("y=%d" % ((40*(1+window_num))%400)),
                        ":",
                        mcell_binary,
                        ("-seed %s" % str(sim_seed)),
                        os.path.join(project_dir, ("%s.main.mdl" % base_name))
                      ]
                    
                    command_string = "Command:";
                    for s in command_list:
                      command_string += " " + s
                    print ( command_string )
                    
                    sp = subprocess.Popen ( command_list, cwd=project_dir, stdout=None, stderr=None )
                    
                    self.report({'INFO'}, "Simulation Running")

                    # This is a hackish workaround since we can't return arbitrary
                    # objects from operators or store arbitrary objects in collection
                    # properties, and we need to keep track of the progress of the
                    # subprocess objects in cellblender_panels.
                    cellblender.simulation_popen_list.append(sp)
                    window_num += 1


                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_clear_run_list(bpy.types.Operator):
    bl_idname = "mcell.clear_run_list"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        # The collection property of subprocesses
        processes_list = mcell.run_simulation.processes_list
        # A list holding actual subprocess objects
        simulation_popen_list = cellblender.simulation_popen_list
        sim_list_length = len(simulation_popen_list)
        idx = 0
        ctr = 0

        while ctr < sim_list_length:
            ctr += 1
            sp = simulation_popen_list[idx]
            # Simulation set is still running. Leave it in the collection
            # property and list of subprocess objects.
            if sp.poll() is None:
                idx += 1
            # Simulation set has failed or finished. Remove it from
            # collection property and the list of subprocess objects.
            else:
                processes_list.remove(idx)
                simulation_popen_list.pop(idx)
                mcell.run_simulation.active_process_index -= 1
                if (mcell.run_simulation.active_process_index < 0):
                    mcell.run_simulation.active_process_index = 0

        return {'FINISHED'}


class MCELL_OT_clear_simulation_queue(bpy.types.Operator):
    bl_idname = "mcell.clear_simulation_queue"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        # The collection property of subprocesses
        processes_list = mcell.run_simulation.processes_list
        # Class holding actual subprocess objects
        simulation_queue = cellblender.simulation_queue
        proc_list_length = len(processes_list)
        idx = 0
        ctr = 0

        while ctr < proc_list_length:
            ctr += 1
            pid = int(processes_list[idx].name.split(',')[0].split(':')[1])
            q_item = simulation_queue.task_dict.get(pid)
            if q_item:
                proc = q_item['process']
                if (q_item['status'] == 'queued') or (q_item['status'] == 'running'):
                    # Simulation is still running. Leave it in the collection
                    # property and simulation queue
                    idx += 1
                    pass
                else:
                    # Simulation has failed or finished. Remove it from
                    # collection property and the simulation queue
                    simulation_queue.clear_task(pid)
                    processes_list.remove(idx)
                    if idx <= mcell.run_simulation.active_process_index:
                        mcell.run_simulation.active_process_index -= 1
                        if (mcell.run_simulation.active_process_index < 0):
                            mcell.run_simulation.active_process_index = 0
            else:
                # Process is missing from simulation queue
                # so remove it from collection property
                processes_list.remove(idx)
                if idx <= mcell.run_simulation.active_process_index:
                    mcell.run_simulation.active_process_index -= 1
                    if (mcell.run_simulation.active_process_index < 0):
                        mcell.run_simulation.active_process_index = 0

        return {'FINISHED'}


@persistent
def clear_run_list(context):
    """ Clear processes_list when loading a blend.

    Data in simulation_popen_list can not be saved with the blend, so we need
    to clear the processes_list upon reload so the two aren't out of sync.

    """
    print ( "load post handler: cellblender_operators.clear_run_list() called" )

    if not context:
        context = bpy.context

    processes_list = context.scene.mcell.run_simulation.processes_list

    if not cellblender.simulation_popen_list:
        processes_list.clear()

    if not cellblender.simulation_queue:
        processes_list.clear()



@persistent
def mcell_valid_update(context):
    """ Check whether the mcell executable in the .blend file is valid """
    print ( "load post handler: cellblender_operators.mcell_valid_update() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = is_executable ( binary_path )
    # print ( "mcell_binary_valid = ", mcell.cellblender_preferences.mcell_binary_valid )


@persistent
def init_properties(context):
    """ Initialize MCell properties if not already initialized """
    print ( "load post handler: cellblender_operators.init_properties() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    if not mcell.initialized:
        mcell.init_properties()
        mcell.initialized = True


def create_color_list():
    """ Create a list of colors to be assigned to the glyphs. """ 

    mcell = bpy.context.scene.mcell
    mcell.mol_viz.color_index = 0
    if not mcell.mol_viz.color_list:
        for i in range(8):
            mcell.mol_viz.color_list.add()
        mcell.mol_viz.color_list[0].vec = [0.8, 0.0, 0.0]
        mcell.mol_viz.color_list[1].vec = [0.0, 0.8, 0.0]
        mcell.mol_viz.color_list[2].vec = [0.0, 0.0, 0.8]
        mcell.mol_viz.color_list[3].vec = [0.0, 0.8, 0.8]
        mcell.mol_viz.color_list[4].vec = [0.8, 0.0, 0.8]
        mcell.mol_viz.color_list[5].vec = [0.8, 0.8, 0.0]
        mcell.mol_viz.color_list[6].vec = [1.0, 1.0, 1.0]
        mcell.mol_viz.color_list[7].vec = [0.0, 0.0, 0.0]


@persistent
def read_viz_data_load_post(context):
    print ( "load post handler: cellblender_operators.read_viz_data_load_post() called" )
    bpy.ops.mcell.read_viz_data()


# Operators can't be callbacks, so we need this function for now.  This is
# temporary until we make importing viz data automatic.
def read_viz_data_callback(self, context):
    bpy.ops.mcell.read_viz_data()


class MCELL_OT_read_viz_data(bpy.types.Operator):
    bl_idname = "mcell.read_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Load the molecule visualization data into Blender"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global global_mol_file_list

        # Called when the molecule files are actually to be read (when the
        # "Read Molecule Files" button is pushed or a seed value is selected
        # from the list)

        # print("MCELL_OT_read_viz_data.execute() called")
        # self.report({'INFO'}, "Reading Visualization Data")

        mcell = context.scene.mcell

        mol_file_dir = ''

        #  mol_file_dir comes from directory already chosen manually
        if mcell.mol_viz.manual_select_viz_dir:
            mol_file_dir = mcell.mol_viz.mol_file_dir
            print("manual mol_file_dir: %s" % (mol_file_dir))

        #  mol_file_dir comes from directory associated with saved .blend file
        else:
          # Force the top level mol_viz directory to be where the .blend file
          # lives plus "viz_data". The seed directories will live underneath it.
          mol_viz_top_level_dir = os.path.join(project_files_path(), "viz_data/")
          mol_viz_top_level_dir = os.path.relpath(mol_viz_top_level_dir)
          mol_viz_seed_list = glob.glob(os.path.join(mol_viz_top_level_dir, "*"))
          mol_viz_seed_list.sort()

          # Clear the list of seeds (e.g. seed_00001, seed_00002, etc) and the
          # list of files (e.g. my_project.cellbin.0001.dat,
          # my_project.cellbin.0002.dat)
          mcell.mol_viz.mol_viz_seed_list.clear()


          # Add all the seed directories to the mol_viz_seed_list collection
          # (seed_00001, seed_00002, etc)
          for mol_viz_seed in mol_viz_seed_list:
              new_item = mcell.mol_viz.mol_viz_seed_list.add()
              new_item.name = os.path.basename(mol_viz_seed)

          if mcell.mol_viz.mol_viz_seed_list:
              mol_file_dir = get_mol_file_dir()
              mcell.mol_viz.mol_file_dir = mol_file_dir
              print("auto mol_file_dir: %s" % (mol_file_dir))

#        mcell.mol_viz.mol_file_list.clear()

        global_mol_file_list = []
        mol_file_list = []

        if mol_file_dir != '':
          mol_file_list = glob.glob(os.path.join(mol_file_dir, "*"))
          mol_file_list.sort()

        if mol_file_list:
          # Add all the viz_data files to global_mol_file_list (e.g.
          # my_project.cellbin.0001.dat, my_project.cellbin.0001.dat, etc)
          for mol_file_name in mol_file_list:
#              new_item = mcell.mol_viz.mol_file_list.add()
#              new_item.name = os.path.basename(mol_file_name)
              global_mol_file_list.append(os.path.basename(mol_file_name))

          # If you previously had some viz data loaded, but reran the
          # simulation with less iterations, you can receive an index error.
          try:
#              mol_file = mcell.mol_viz.mol_file_list[
#                  mcell.mol_viz.mol_file_index]
              mol_file = global_mol_file_list[
                  mcell.mol_viz.mol_file_index]
          except IndexError:
              mcell.mol_viz.mol_file_index = 0

          create_color_list()
          set_viz_boundaries(context)

          try:
              mol_viz_clear(mcell, force_clear=True)
              mol_viz_update(self, context)
          except:
              print( "Unexpected Exception calling mol_viz_update: " + str(sys.exc_info()) )

        return {'FINISHED'}


class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("MCELL_OT_export_project.execute()")
        print(" Scene name =", context.scene.name)

        # Filter or replace problem characters (like space, ...)
        scene_name = context.scene.name.replace(" ", "_")

        # Change the actual scene name to the legal MCell Name
        context.scene.name = scene_name

        mcell = context.scene.mcell

        # Force the project directory to be where the .blend file lives
        model_objects_update(context)

        filepath = project_files_path()
        os.makedirs(filepath, exist_ok=True)

        # Set this for now to have it hopefully propagate until base_name can
        # be removed
        mcell.project_settings.base_name = scene_name

        #filepath = os.path.join(
        #   filepath, mcell.project_settings.base_name + ".main.mdl")
        filepath = os.path.join(filepath, scene_name + ".main.mdl")
#        bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
        export_mcell_mdl.save(context, filepath)

        # These two branches of the if statement seem identical ?

        #if mcell.export_project.export_format == 'mcell_mdl_unified':
        #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
        #                            (mcell.project_settings.base_name +
        #                            ".main.mdl"))
        #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
        #elif mcell.export_project.export_format == 'mcell_mdl_modular':
        #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
        #                            (mcell.project_settings.base_name +
        #                            ".main.mdl"))
        #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)

        self.report({'INFO'}, "Project Exported")

        return {'FINISHED'}

def set_viz_boundaries( context ):
        global global_mol_file_list

        mcell = context.scene.mcell

#        mcell.mol_viz.mol_file_num = len(mcell.mol_viz.mol_file_list)
        mcell.mol_viz.mol_file_num = len(global_mol_file_list)
        mcell.mol_viz.mol_file_stop_index = mcell.mol_viz.mol_file_num - 1

        #print("Setting frame_start to 0")
        #print("Setting frame_end to ", len(mcell.mol_viz.mol_file_list)-1)
        bpy.context.scene.frame_start = 0
#        bpy.context.scene.frame_end = len(mcell.mol_viz.mol_file_list)-1
        bpy.context.scene.frame_end = len(global_mol_file_list)-1

        if bpy.context.screen != None:
            for area in bpy.context.screen.areas:
                if area != None:
                    if area.type == 'TIMELINE':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                ctx = bpy.context.copy()
                                ctx['area'] = area
                                ctx['region'] = region
                                bpy.ops.time.view_all(ctx)
                                break  # It's not clear if this should break or continue ... breaking for now


class MCELL_OT_select_viz_data(bpy.types.Operator):
    bl_idname = "mcell.select_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Read MCell Molecule Files for Visualization"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def __init__(self):
        self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir

    def execute(self, context):
        global global_mol_file_list

        mcell = context.scene.mcell
        
        if (os.path.isdir(self.filepath)):
            mol_file_dir = self.filepath
        else:
            # Strip the file name off of the file path.
            mol_file_dir = os.path.dirname(self.filepath)

        mcell.mol_viz.mol_file_dir = mol_file_dir

        mol_file_list = glob.glob(os.path.join(mol_file_dir, "*"))
        mol_file_list.sort()

        # Reset mol_file_list and mol_viz_seed_list to empty
#        mcell.mol_viz.mol_file_list.clear()
        global_mol_file_list = []

        for mol_file_name in mol_file_list:
#            new_item = mcell.mol_viz.mol_file_list.add()
#            new_item.name = os.path.basename(mol_file_name)
            global_mol_file_list.append(os.path.basename(mol_file_name))

        create_color_list()
        set_viz_boundaries(context)
        mcell.mol_viz.mol_file_index = 0

        mol_viz_update(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        # Called when the file selection panel is requested
        # (when the "Set Molecule Viz Directory" button is pushed)
        print("MCELL_OT_select_viz_data.invoke() called")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

"""
def plot_rxns(plot_command):
    # Plot a file
    mcell = bpy.context.scene.mcell
    # Force the project directory to be where the .blend file lives
    project_dir = os.path.dirname(bpy.data.filepath)
    base_name = mcell.project_settings.base_name
    print("Plotting ", base_name, " with ", plot_command, " at ", project_dir)
    pid = subprocess.Popen(
        plot_command.split(), cwd=os.path.join(project_dir, "react_data"))


class MCELL_OT_plot_rxn_output_command(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_command"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using command line"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        print("Plotting with cmd=", mcell.reactions.plot_command)
        plot_rxns(mcell.reactions.plot_command)
        return {'FINISHED'}
"""

class MCELL_OT_plot_rxn_output_generic(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_generic"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using specified plotting package"
    bl_options = {'REGISTER', 'UNDO'}

    plotter_button_label = bpy.props.StringProperty()

    def execute(self, context):
        mcell = context.scene.mcell
        plot_sep = mcell.rxn_output.plot_layout
        plot_legend = mcell.rxn_output.plot_legend

        combine_seeds = mcell.rxn_output.combine_seeds
        mol_colors = mcell.rxn_output.mol_colors

        plot_button_label = self.plotter_button_label

        # Look up the plotting module by its name

        for plot_module in cellblender.cellblender_info[
                'cellblender_plotting_modules']:
            mod_name = plot_module.get_name()
            if mod_name == plot_button_label:
                break

        # Plot the data via this module
        # print("Preparing to call %s" % (mod_name))
        # The project_files_path is now where the MDL lives:
        data_path = project_files_path()
        data_path = os.path.join(data_path, "react_data")
        plot_spec_string = "xlabel=time(s) ylabel=count "
        if plot_legend != 'x':
            plot_spec_string = plot_spec_string + "legend=" + plot_legend

        for rxn_output in mcell.rxn_output.rxn_output_list:
            molecule_name = rxn_output.molecule_name
            object_name = rxn_output.object_name
            region_name = rxn_output.region_name
            file_name = None

            if rxn_output.rxn_or_mol == 'Molecule':
                if rxn_output.count_location == 'World':
                    file_name = "%s.World.dat" % (molecule_name)
                elif rxn_output.count_location == 'Object':
                    file_name = "%s.%s.dat" % (molecule_name, object_name)
                elif rxn_output.count_location == 'Region':
                    file_name = "%s.%s.%s.dat" % (molecule_name,
                                           object_name, region_name)
            else:
                rxn_name = rxn_output.reaction_name
                file_name = "%s.World.dat" % (rxn_name)

            if file_name:
                file_name = os.path.join("seed_*", file_name)
                candidate_file_list = glob.glob(
                    os.path.join(data_path, file_name))
                # Without sorting, the seeds may not be increasing
                candidate_file_list.sort()
                #print("Candidate file list for %s:" % (file_name))
                #print("  ", candidate_file_list)
                first_pass = True
                # Use the start_time.txt file to find files modified since
                # MCell was started
                start_time = os.stat(os.path.join(os.path.dirname(
                    bpy.data.filepath), "start_time.txt")).st_mtime
                # This file is both in the list and newer
                # than the run time for MCell
                candidate_file_list = [
                    ffn for ffn in candidate_file_list if os.stat(ffn).st_mtime >= start_time]
                for ffn in candidate_file_list:

                    # Create f as a relative path containing seed/file
                    split1 = os.path.split(ffn)
                    split2 = os.path.split(split1[0])
                    f = os.path.join(split2[1], split1[1])
                    
                    color_string = ""
                    if rxn_output.rxn_or_mol == 'Molecule' and mol_colors:
                        # Use molecule colors for graphs
                        # Should be standardized!!
                        mol_mat_name = "mol_%s_mat" % (molecule_name)
                        #print ("Molecule Material Name = ", mol_mat_name)
                        #Look up the material
                        mats = bpy.data.materials
                        mol_color = mats.get(mol_mat_name).diffuse_color
                        #print("Molecule color = ", mol_mat.diffuse_color)

                        mol_color_red = 255 * mol_color.r
                        mol_color_green = 255 * mol_color.g
                        mol_color_blue = 255 * mol_color.b
                        color_string = " color=#%2.2x%2.2x%2.2x " % (
                            mol_color_red, mol_color_green, mol_color_blue)

                    base_name = os.path.basename(f)

                    if combine_seeds:
                        title_string = " title=" + base_name
                    else:
                        title_string = " title=" + f
                    
                    if plot_sep == ' ':
                        # No title when all are on the same plot since only
                        # last will show
                        title_string = ""

                    if combine_seeds:
                        psep = " "
                        if first_pass:
                            psep = plot_sep
                            first_pass = False
                        plot_spec_string = (
                            plot_spec_string + psep + color_string +
                            title_string + " f=" + f)
                    else:
                        plot_spec_string = (
                            plot_spec_string + plot_sep + color_string +
                            title_string + " f=" + f)

        print("Plotting from", data_path)
        print("Plotting spec", plot_spec_string)
        plot_module.plot(data_path, plot_spec_string)

        return {'FINISHED'}


class MCELL_OT_mol_viz_set_index(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_set_index"
    bl_label = "Set Molecule File Index"
    bl_description = "Set MCell Molecule File Index for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global global_mol_file_list

        mcell = context.scene.mcell
#        if mcell.mol_viz.mol_file_list:
        if global_mol_file_list:
            i = mcell.mol_viz.mol_file_index
            if (i > mcell.mol_viz.mol_file_stop_index):
                i = mcell.mol_viz.mol_file_stop_index
            if (i < mcell.mol_viz.mol_file_start_index):
                i = mcell.mol_viz.mol_file_start_index
            mcell.mol_viz.mol_file_index = i
            # print ( "Set index calling update" )
            mol_viz_update(self, context)
        return{'FINISHED'}



#CellBlender operator helper functions:


@persistent
def frame_change_handler(scn):
    """ Update the viz data every time a frame is changed. """

    mcell = scn.mcell
    curr_frame = mcell.mol_viz.mol_file_index
    if (not curr_frame == scn.frame_current):
        mcell.mol_viz.mol_file_index = scn.frame_current
        bpy.ops.mcell.mol_viz_set_index()
        # Is the following code necessary?
        #if mcell.mol_viz.render_and_save:
        #    scn.render.filepath = "//stores_on/frames/frame_%05d.png" % (
        #        scn.frame_current)
        #    bpy.ops.render.render(write_still=True)


def mol_viz_toggle_manual_select(self, context):
    """ Toggle the option to manually load viz data. """
    global global_mol_file_list

    mcell = context.scene.mcell

    mcell.mol_viz.mol_file_dir = ""
    mcell.mol_viz.mol_file_name = ""
#    mcell.mol_viz.mol_file_list.clear()
    global_mol_file_list = []
    mcell.mol_viz.mol_viz_seed_list.clear()

    if not mcell.mol_viz.manual_select_viz_dir:
        bpy.ops.mcell.read_viz_data()

    mol_viz_clear(mcell)


def get_mol_file_dir():
    """ Get the viz dir """

    mcell = bpy.context.scene.mcell

    # If you previously had some viz data loaded, but reran the
    # simulation with less seeds, you can receive an index error.
    try:
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[
            mcell.mol_viz.active_mol_viz_seed_index]
    except IndexError:
        mcell.mol_viz.active_mol_viz_seed_index = 0
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[0]
    filepath = os.path.join(
        project_files_path(), "viz_data/%s" % active_mol_viz_seed.name)
    filepath = os.path.relpath(filepath)

    return filepath


def mol_viz_update(self, context):
    """ Clear the old viz data. Draw the new viz data. """
    global global_mol_file_list

    mcell = context.scene.mcell

#    if len(mcell.mol_viz.mol_file_list) > 0:
    if len(global_mol_file_list) > 0:
#        filename = mcell.mol_viz.mol_file_list[mcell.mol_viz.mol_file_index].name
        filename = global_mol_file_list[mcell.mol_viz.mol_file_index]
        mcell.mol_viz.mol_file_name = filename
        filepath = os.path.join(mcell.mol_viz.mol_file_dir, filename)

        # Save current global_undo setting. Turn undo off to save memory
        global_undo = bpy.context.user_preferences.edit.use_global_undo
        bpy.context.user_preferences.edit.use_global_undo = False

        mol_viz_clear(mcell)
        if mcell.mol_viz.mol_viz_enable:
            mol_viz_file_read(mcell, filepath)

        # Reset undo back to its original state
        bpy.context.user_preferences.edit.use_global_undo = global_undo
    return


def mol_viz_clear(mcell_prop, force_clear=False):
    """ Clear the viz data from the previous frame. """

    mcell = mcell_prop
    scn = bpy.context.scene
    scn_objs = scn.objects
    meshes = bpy.data.meshes
    objs = bpy.data.objects

    if force_clear:
      mol_viz_list = [obj for obj in scn_objs if (obj.name[:4] == 'mol_') and (obj.name[-6:] != '_shape')]
    else:
      mol_viz_list = mcell.mol_viz.mol_viz_list

    for mol_item in mol_viz_list:
        mol_name = mol_item.name
        mol_obj = scn_objs.get(mol_name)
        if mol_obj:
            hide = mol_obj.hide

            mol_pos_mesh = mol_obj.data
            mol_pos_mesh_name = mol_pos_mesh.name
            mol_shape_obj_name = "%s_shape" % (mol_name)
            mol_shape_obj = objs.get(mol_shape_obj_name)
            if mol_shape_obj:
                mol_shape_obj.parent = None

            scn_objs.unlink(mol_obj)
            objs.remove(mol_obj)
            meshes.remove(mol_pos_mesh)

            mol_pos_mesh = meshes.new(mol_pos_mesh_name)
            mol_obj = objs.new(mol_name, mol_pos_mesh)
            scn_objs.link(mol_obj)

            if mol_shape_obj:
                mol_shape_obj.parent = mol_obj

            mol_obj.dupli_type = 'VERTS'
            mol_obj.use_dupli_vertices_rotation = True
            mols_obj = objs.get("molecules")
            mol_obj.parent = mols_obj

            mol_obj.hide = hide

    # Reset mol_viz_list to empty
    for i in range(len(mcell.mol_viz.mol_viz_list)-1, -1, -1):
        mcell.mol_viz.mol_viz_list.remove(i)





def old_mol_viz_file_read(mcell_prop, filepath):
    """ Draw the viz data for the current frame. """
    mcell = mcell_prop
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ("Processing molecules from file:    %s" % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read Binary format molecule file:
            bin_data = 1
            while True:
                try:
                    # Variable names are a little hard to follow
                    # Here's what I assume they mean:
                    # ni = Initially, array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")
                    ni.fromfile(mol_file, 1)
                    ns = array.array("B")
                    ns.fromfile(mol_file, ni[0])
                    s = ns.tostring().decode()
                    mol_name = "mol_%s" % (s)
                    mt = array.array("B")
                    mt.fromfile(mol_file, 1)
                    ni = array.array("I")
                    ni.fromfile(mol_file, 1)
                    mol_pos = array.array("f")
                    mol_orient = array.array("f")
                    mol_pos.fromfile(mol_file, ni[0])
#                    tot += ni[0]/3
                    if mt[0] == 1:
                        mol_orient.fromfile(mol_file, ni[0])
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                except:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            bin_data = 0
            mol_file.close()
            # Create a list of molecule names, positions, and orientations
            # Each entry in the list is ordered like this (afaik):
            # [molec_name, [x_pos, y_pos, z_pos, x_orient, y_orient, z_orient]]
            # Orientations are zero in the case of volume molecules.
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[2:]]] for s in open(
                    filepath, "r").read().split("\n") if s != ""]

            for mol in mol_data:
                mol_name = "mol_%s" % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    # Check to see if it's a surface molecule
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array("f"), array.array("f")]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        # Get the parent object to all the molecule positions if it exists.
        # Otherwise, create it.
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = "molecules"

        #mol_viz_list

        if mol_dict:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            #ident_mat = mathutils.Matrix.Translation(
            #    mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = "%s_mat" % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

                # Look-up mesh shape (glyph) template and create if needed
                mol_shape_mesh_name = "%s_shape" % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)
                if not mol_shape_mesh:
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005, location=[0, 0, 0])
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    mol_shape_obj = objs.get(mol_shape_obj_name)

                # Look-up material, create if needed.
                # Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mcell.mol_viz.color_list[
                        mcell.mol_viz.color_index].vec
                    mcell.mol_viz.color_index = mcell.mol_viz.color_index + 1
                    if (mcell.mol_viz.color_index >
                            len(mcell.mol_viz.color_list)-1):
                        mcell.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

                # Create a "mesh" to hold instances of molecule positions
                mol_pos_mesh_name = "%s_pos" % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

                # Add and place vertices at positions of molecules
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

                # Create object to contain the mol_pos_mesh data
                mol_obj = objs.get(mol_name)
                if not mol_obj:
                    mol_obj = objs.new(mol_name, mol_pos_mesh)
                    scn_objs.link(mol_obj)
                    mol_shape_obj.parent = mol_obj
                    mol_obj.dupli_type = 'VERTS'
                    mol_obj.use_dupli_vertices_rotation = True
                    mol_obj.parent = mols_obj

#        scn.update()

#        utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#        print ("     Processed %d molecules in %g seconds\n" % (
#            len(mol_data), utime))

    except IOError:
        print(("\n***** File not found: %s\n") % (filepath))

    except ValueError:
        print(("\n***** Invalid data in file: %s\n") % (filepath))




import sys, traceback


def mol_viz_file_read(mcell_prop, filepath):
    """ Read and Draw the molecule viz data for the current frame. """

    mcell = mcell_prop
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ("Processing molecules from file:    %s" % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read MCell/CellBlender Binary Format molecule file, version 1:
            # print ("Reading binary file " + filepath )
            bin_data = 1
            while True:
                try:
                    # ni = Initially, byte array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")          # Create a binary byte ("B") array
                    ni.fromfile(mol_file, 1)       # Read one byte which is the number of characters in the molecule name
                    ns = array.array("B")          # Create another byte array to hold the molecule name
                    ns.fromfile(mol_file, ni[0])   # Read ni bytes from the file
                    s = ns.tostring().decode()     # Decode bytes as ASCII into a string (s)
                    mol_name = "mol_%s" % (s)      # Construct name of blender molecule viz object
                    mt = array.array("B")          # Create a byte array for the molecule type
                    mt.fromfile(mol_file, 1)       # Read one byte for the molecule type
                    ni = array.array("I")          # Re-use ni as an integer array to hold the number of molecules of this name in this frame
                    ni.fromfile(mol_file, 1)       # Read the 4 byte integer value which is 3 times the number of molecules
                    mol_pos = array.array("f")     # Create a floating point array to hold the positions
                    mol_orient = array.array("f")  # Create a floating point array to hold the orientations
                    mol_pos.fromfile(mol_file, ni[0])  # Read the positions which should be 3 floats per molecule
#                    tot += ni[0]/3  
                    if mt[0] == 1:                                        # If mt==1, it's a surface molecule
                        mol_orient.fromfile(mol_file, ni[0])              # Read the surface molecule orientations
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]     # Create a dictionary entry for this molecule containing a list of relevant data
                    new_item = mcell.mol_viz.mol_viz_list.add()           # Create a new collection item to hold the name for this molecule
                    new_item.name = mol_name                              # Assign the name to the new item
                except EOFError:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

                except:
                    print( "Unexpected Exception: " + str(sys.exc_info()) )
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            # print ("Reading ASCII file " + filepath )
            bin_data = 0
            mol_file.close()
            # Create a list of molecule names, positions, and orientations
            # Each entry in the list is ordered like this (afaik):
            # [molec_name, [x_pos, y_pos, z_pos, x_orient, y_orient, z_orient]]
            # Orientations are zero in the case of volume molecules.
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[2:]]] for s in open(
                    filepath, "r").read().split("\n") if s != ""]

            for mol in mol_data:
                mol_name = "mol_%s" % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    # Check to see if it's a surface molecule
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array("f"), array.array("f")]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        # Get the parent object to all the molecule positions if it exists.
        # Otherwise, create it.
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])      # Create an "Empty" object in the Blender scene
            ### Note, the following line seems to cause an exception in some contexts: 'Context' object has no attribute 'selected_objects'
            mols_obj = bpy.context.selected_objects[0]  # The newly added object will be selected
            mols_obj.name = "molecules"                 # Name this empty object "molecules" 
            mols_obj.hide_select = True
            mols_obj.hide = True

        if mol_dict:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            #ident_mat = mathutils.Matrix.Translation(
            #    mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = "%s_mat" % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # print ( "in mol_viz_file_read with mol_name = " + mol_name + ", mol_mat_name = " + mol_mat_name + ", file = " + filepath[filepath.rfind(os.sep)+1:] )

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

                # Look up the glyph, color, size, and other attributes from the molecules list
                
                #### If the molecule found in the viz file doesn't exist in the molecules list, create it as the interface for changing color, etc.

                mname = mol_name[4:]   # Trim off the "mol_" portion to use as an index into the molecules list
                mol = None
                if (len(mname) > 0) and (mname in mcell.molecules.molecule_list):
                    mol = mcell.molecules.molecule_list[mname]
                    # The color below doesn't seem to be used ... the color comes from a material
                    # print ( "Mol " + mname + " has color " + str(mol.color) )

                # Look-up mesh shape (glyph) template and create if needed
                
                # This may end up calling a member function of the molecule class to create a new default molecule (including glyph)
                if mol != None:
                    # print ( "Molecule  glyph: " + str (mol.glyph) )
                    pass
                mol_shape_mesh_name = "%s_shape" % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)  # This will return None if not found by that name
                # print ( "Getting or Making the glyph for " + mol_shape_obj_name )
                if not mol_shape_mesh:
                    # Make the glyph right here
                    # print ( "Making a " + str(mol.glyph) + " molecule glyph" )
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005, location=[0, 0, 0])
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_obj.hide_select = True
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    # print ( "Using a " + str(mol.glyph) + " molecule glyph" )
                    mol_shape_obj = objs.get(mol_shape_obj_name)

                # Look-up material, create if needed.
                # Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mcell.mol_viz.color_list[
                        mcell.mol_viz.color_index].vec
                    mcell.mol_viz.color_index = mcell.mol_viz.color_index + 1
                    if (mcell.mol_viz.color_index >
                            len(mcell.mol_viz.color_list)-1):
                        mcell.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

                #if (mol != None):
                #    # and (mol.usecolor):
                #    # Over-ride the default colors
                #    mol_mat.diffuse_color = mol.color
                #    mol_mat.emit = mol.emit

                # Look-up mesh to hold instances of molecule positions, create if needed
                mol_pos_mesh_name = "%s_pos" % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

                # Add and set values of vertices at positions of molecules
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

                # Save the molecule's visibility state, so it can be restored later
                mol_obj = objs.get(mol_name)
                if mol_obj:
                    hide = mol_obj.hide
                    scn_objs.unlink(mol_obj)
                    objs.remove(mol_obj)
                else:
                    hide = False

                # Create object to contain the mol_pos_mesh data
                mol_obj = objs.new(mol_name, mol_pos_mesh)
                scn_objs.link(mol_obj)
                mol_shape_obj.parent = mol_obj
                mol_obj.dupli_type = 'VERTS'
                mol_obj.use_dupli_vertices_rotation = True
                mol_obj.parent = mols_obj
                mol_obj.hide_select = True
            
                # Restore the visibility state
                mol_obj.hide = hide

#        utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#        print ("     Processed %d molecules in %g seconds\n" % (
#            len(mol_data), utime))

    except IOError:
        print(("\n***** IOError: File: %s\n") % (filepath))

    except ValueError:
        print(("\n***** ValueError: Invalid data in file: %s\n") % (filepath))

    except RuntimeError as rte:
        print(("\n***** RuntimeError reading file: %s\n") % (filepath))
        print("      str(error): \n" + str(rte) + "\n")
        fail_error = sys.exc_info()
        print ( "    Error Type: " + str(fail_error[0]) )
        print ( "    Error Value: " + str(fail_error[1]) )
        tb = fail_error[2]
        # tb.print_stack()
        print ( "=== Traceback Start ===" )
        traceback.print_tb(tb)
        print ( "=== Traceback End ===" )

    except Exception as uex:
        # Catch any exception
        print ( "\n***** Unexpected exception:" + str(uex) + "\n" )
        raise


# Meshalyzer
class MCELL_OT_meshalyzer(bpy.types.Operator):
    bl_idname = "mcell.meshalyzer"
    bl_label = "Analyze Geometric Properties of Mesh"
    bl_description = "Analyze Geometric Properties of Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        objs = context.selected_objects

        mcell.meshalyzer.object_name = ""
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.watertight = ""
        mcell.meshalyzer.manifold = ""
        mcell.meshalyzer.normal_status = ""
        mcell.meshalyzer.area = 0
        mcell.meshalyzer.volume = 0
        mcell.meshalyzer.sav_ratio = 0

        if (len(objs) != 1):
            mcell.meshalyzer.status = "Please Select One Mesh Object"
            return {'FINISHED'}

        obj = objs[0]

        mcell.meshalyzer.object_name = obj.name

        if not (obj.type == 'MESH'):
            mcell.meshalyzer.status = "Selected Object Not a Mesh"
            return {'FINISHED'}

        t_mat = obj.matrix_world
        mesh = obj.data

        mcell.meshalyzer.vertices = len(mesh.vertices)
        mcell.meshalyzer.edges = len(mesh.edges)
        mcell.meshalyzer.faces = len(mesh.polygons)

        area = 0
        for f in mesh.polygons:
            if not (len(f.vertices) == 3):
                mcell.meshalyzer.status = "***** Mesh Not Triangulated *****"
                mcell.meshalyzer.watertight = "Mesh Not Triangulated"
                return {'FINISHED'}

            tv0 = mesh.vertices[f.vertices[0]].co * t_mat
            tv1 = mesh.vertices[f.vertices[1]].co * t_mat
            tv2 = mesh.vertices[f.vertices[2]].co * t_mat
            area = area + mathutils.geometry.area_tri(tv0, tv1, tv2)

        mcell.meshalyzer.area = area

        (edge_faces, edge_face_count) = make_efdict(mesh)

        is_closed = check_closed(edge_face_count)
        is_manifold = check_manifold(edge_face_count)
        is_orientable = check_orientable(mesh, edge_faces, edge_face_count)

        if is_orientable:
            mcell.meshalyzer.normal_status = "Consistent Normals"
        else:
            mcell.meshalyzer.normal_status = "Inconsistent Normals"

        if is_closed:
            mcell.meshalyzer.watertight = "Watertight Mesh"
        else:
            mcell.meshalyzer.watertight = "Non-watertight Mesh"

        if is_manifold:
            mcell.meshalyzer.manifold = "Manifold Mesh"
        else:
            mcell.meshalyzer.manifold = "Non-manifold Mesh"

        volume = 0
        if is_orientable and is_manifold and is_closed:
            volume = mesh_vol(mesh, t_mat)
            if volume >= 0:
                mcell.meshalyzer.normal_status = "Outward Facing Normals"
            else:
                mcell.meshalyzer.normal_status = "Inward Facing Normals"

        mcell.meshalyzer.volume = volume
        if (not volume == 0.0):
            mcell.meshalyzer.sav_ratio = area/volume

        mcell.meshalyzer.status = ""
        return {'FINISHED'}


class MCELL_OT_gen_meshalyzer_report(bpy.types.Operator):
    bl_idname = "mcell.gen_meshalyzer_report"
    bl_label = "Analyze Geometric Properties of Multiple Meshes"
    bl_description = "Generate Analysis Report of Geometric Properties of Multiple Meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        mcell = context.scene.mcell
        objs = context.selected_objects

        mcell.meshalyzer.object_name = ''
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.watertight = ''
        mcell.meshalyzer.manifold = ''
        mcell.meshalyzer.normal_status = ''
        mcell.meshalyzer.area = 0
        mcell.meshalyzer.volume = 0
        mcell.meshalyzer.sav_ratio = 0

        if (len(objs) == 0):
            mcell.meshalyzer.status = 'Please Select One or More Mesh Objects'
            return {'FINISHED'}

        bpy.ops.text.new()
        report = bpy.data.texts['Text']
        report.name = 'mesh_analysis.txt'
        report.write("# Object  Surface Area  Volume\n")

        for obj in objs:

            mcell.meshalyzer.object_name = obj.name

            if not (obj.type == 'MESH'):
                mcell.meshalyzer.status = 'Selected Object Not a Mesh'
                return {'FINISHED'}

            t_mat = obj.matrix_world
            mesh=obj.data

            mcell.meshalyzer.vertices = len(mesh.vertices)
            mcell.meshalyzer.edges = len(mesh.edges)
            mcell.meshalyzer.faces = len(mesh.polygons)

            area = 0
            for f in mesh.polygons:
                if not (len(f.vertices) == 3):
                    mcell.meshalyzer.status = '***** Mesh Not Triangulated *****'
                    mcell.meshalyzer.watertight = 'Mesh Not Triangulated'
                    return {'FINISHED'}

                tv0 = mesh.vertices[f.vertices[0]].co * t_mat
                tv1 = mesh.vertices[f.vertices[1]].co * t_mat
                tv2 = mesh.vertices[f.vertices[2]].co * t_mat
                area = area + mathutils.geometry.area_tri(tv0,tv1,tv2)

            mcell.meshalyzer.area = area

            (edge_faces, edge_face_count) = make_efdict(mesh)

            is_closed = check_closed(edge_face_count)
            is_manifold = check_manifold(edge_face_count)
            is_orientable = check_orientable(mesh,edge_faces,edge_face_count)

            if is_orientable:
                mcell.meshalyzer.normal_status = 'Consistent Normals'
            else:
                mcell.meshalyzer.normal_status = 'Inconsistent Normals'

            if is_closed:
                mcell.meshalyzer.watertight = 'Watertight Mesh'
            else:
                mcell.meshalyzer.watertight = 'Non-watertight Mesh'

            if is_manifold:
                mcell.meshalyzer.manifold = 'Manifold Mesh'
            else:
                mcell.meshalyzer.manifold = 'Non-manifold Mesh'

            volume = 0
            if is_orientable and is_manifold and is_closed:
                volume = mesh_vol(mesh,t_mat)
                if volume >= 0:
                    mcell.meshalyzer.normal_status = 'Outward Facing Normals'
                else:
                    mcell.meshalyzer.normal_status = 'Inward Facing Normals'

            mcell.meshalyzer.volume = volume
            if (not volume == 0.0):
                mcell.meshalyzer.sav_ratio = area/volume

            report.write("%s %.9g %.9g\n" % (obj.name, mcell.meshalyzer.area, mcell.meshalyzer.volume))

        mcell.meshalyzer.status = ''
        return {'FINISHED'}


def mesh_vol(mesh, t_mat):
    """Compute volume of triangulated, orientable, watertight, manifold mesh

    volume > 0 means outward facing normals
    volume < 0 means inward facing normals

    """

    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co * t_mat
        tv1 = mesh.vertices[f.vertices[1]].co * t_mat
        tv2 = mesh.vertices[f.vertices[2]].co * t_mat
        x0 = tv0.x
        y0 = tv0.y
        z0 = tv0.z
        x1 = tv1.x
        y1 = tv1.y
        z1 = tv1.z
        x2 = tv2.x
        y2 = tv2.y
        z2 = tv2.z
        det = x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
        volume = volume + det

    volume = volume/6.0

    return(volume)


def make_efdict(mesh):

    edge_faces = {}
    edge_face_count = {}
    for f in mesh.polygons:
        for ek in f.edge_keys:
            if ek in edge_faces:
                edge_faces[ek] ^= f.index
                edge_face_count[ek] = edge_face_count[ek] + 1
            else:
                edge_faces[ek] = f.index
                edge_face_count[ek] = 1

    return(edge_faces, edge_face_count)


def check_manifold(edge_face_count):
    """ Make sure the object is manifold """

    for ek in edge_face_count.keys():
        if edge_face_count[ek] != 2:
            return (0)

    return(1)


def check_closed(edge_face_count):
    """ Make sure the object is closed (no leaks). """

    for ek in edge_face_count.keys():
        if not edge_face_count[ek] == 2:
            return (0)

    return(1)


def check_orientable(mesh, edge_faces, edge_face_count):

    ev_order = [[0, 1], [1, 2], [2, 0]]
    edge_checked = {}

    for f in mesh.polygons:
        for i in range(0, len(f.vertices)):
            ek = f.edge_keys[i]
            if not ek in edge_checked:
                edge_checked[ek] = 1
                if edge_face_count[ek] == 2:
                    nfi = f.index ^ edge_faces[ek]
                    nf = mesh.polygons[nfi]
                    for j in range(0, len(nf.vertices)):
                        if ek == nf.edge_keys[j]:
                            if f.vertices[ev_order[i][0]] != nf.vertices[
                                    ev_order[j][1]]:
                                return (0)
                            break

    return (1)


class MCELL_OT_select_filtered(bpy.types.Operator):
    bl_idname = "mcell.select_filtered"
    bl_label = "Select Filtered"
    bl_description = "Select objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = True

        return {'FINISHED'}


class MCELL_OT_deselect_filtered(bpy.types.Operator):
    bl_idname = "mcell.deselect_filtered"
    bl_label = "Deselect Filtered"
    bl_description = "Deselect objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = False

        return {'FINISHED'}


class MCELL_OT_toggle_visibility_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_visibility_filtered"
  bl_label = "Visibility Filtered"
  bl_description = "Toggle visibility of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide = not obj.hide

    return {'FINISHED'}


class MCELL_OT_toggle_renderability_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_renderability_filtered"
  bl_label = "Renderability Filtered"
  bl_description = "Toggle renderability of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide_render= not obj.hide_render

    return {'FINISHED'}


# Rebuild Model Objects List from Scratch
#   This is required to catch changes in names of objects.
#   Note: This function is also registered as a load_post and save_pre handler
@persistent
def model_objects_update(context):
    # print ( "cellblender_operators.model_objects_update() called" )
    if not context:
        context = bpy.context

    mcell = context.scene.mcell
    mobjs = mcell.model_objects
    sobjs = context.scene.objects

    model_obj_names = [obj.name for obj in sobjs if obj.mcell.include]

    # Note: This bit only needed to convert
    #       old model object list (pre 0.1 rev_55) to new style.
    #       Old style did not have obj.mcell.include Boolean Property.
    if ((len(model_obj_names) == 0) & (len(mobjs.object_list) > 0)):
        for i in range(len(mobjs.object_list)-1):
            obj = sobjs.get(mobjs.object_list[i].name)
            if obj:
                obj.mcell.include = True
        model_obj_names = [
            obj.name for obj in sobjs if obj.mcell.include]

    # Update the model object list from objects marked obj.mcell.include = True
    if (len(model_obj_names) > 0):
        model_obj_names.sort()

        for i in range(len(mobjs.object_list)-1, -1, -1):
            mobjs.object_list.remove(i)

        active_index = mobjs.active_obj_index
        for obj_name in model_obj_names:
            mobjs.object_list.add()
            mobjs.active_obj_index = len(mobjs.object_list)-1
            mobjs.object_list[mobjs.active_obj_index].name = obj_name
            scene_object = sobjs[obj_name]
            # Set an error status if object is not triangulated
            for face in scene_object.data.polygons:
                if not (len(face.vertices) == 3):
                    status = "Object is not triangulated: %s" % (obj_name)
                    mobjs.object_list[mobjs.active_obj_index].status = status
                    break

        mobjs.active_obj_index = active_index

        # We check release sites are valid here in case a user adds an object
        # referenced in a release site after adding the release site itself.
        # (e.g. Add Cube shaped release site. Then add Cube.)
        release_list = mcell.release_sites.mol_release_list
        save_release_idx = mcell.release_sites.active_release_index
        # check_release_site_wrapped acts on the active release site, so we
        # need to increment it and then check
        for rel_idx, _ in enumerate(release_list):
            mcell.release_sites.active_release_index = rel_idx
            check_release_site_wrapped(context)
        # Restore the active index
        mcell.release_sites.active_release_index = save_release_idx

    return


class MCELL_OT_model_objects_add(bpy.types.Operator):
    bl_idname = "mcell.model_objects_add"
    bl_label = "Model Objects Include"
    bl_description = ("Include objects selected in 3D View Window in Model "
                      "Objects export list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        # From the list of selected objects, only add MESH objects.
        objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objs:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY',
                                               ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.mcell.include = True

        model_objects_update(context)

#        for obj in objs:
#            # Prevent duplicate entries
#            if not obj.name in mcell.model_objects.object_list:
#                mcell.model_objects.object_list.add()
#                mcell.model_objects.active_obj_index = len(
#                    mcell.model_objects.object_list)-1
#                mcell.model_objects.object_list[
#                    mcell.model_objects.active_obj_index].name = obj.name


        return {'FINISHED'}


class MCELL_OT_model_objects_remove(bpy.types.Operator):
    bl_idname = "mcell.model_objects_remove"
    bl_label = "Model Objects Remove"
    bl_description = "Remove selected item from Model Objects export list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        mobjs = mcell.model_objects
        sobjs = context.scene.objects

        if (len(mobjs.object_list) > 0):
            obj = sobjs.get(mobjs.object_list[mobjs.active_obj_index].name)
            if obj:
                obj.mcell.include = False

                mobjs.object_list.remove(mobjs.active_obj_index)
                mobjs.active_obj_index -= 1
                if (mobjs.active_obj_index < 0):
                    mobjs.active_obj_index = 0
        
        model_objects_update(context)

        return {'FINISHED'}


def check_model_object(self, context):
    """Checks for illegal object name"""

    mcell = context.scene.mcell
    model_object_list = mcell.model_objects.object_list
    model_object = model_object_list[mcell.model_objects.active_obj_index]

    # print ("Checking name " + model_object.name )

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    model_object_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(model_object_filter, model_object.name)
    if m is None:
        status = "Object name error: %s" % (model_object.name)

    model_object.status = status

    return


class MCELL_OT_set_molecule_glyph(bpy.types.Operator):
    bl_idname = "mcell.set_molecule_glyph"
    bl_label = "Set Molecule Glyph"
    bl_description = "Set molecule glyph to desired shape in glyph library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        meshes = bpy.data.meshes
        mcell.molecule_glyphs.status = ""
        select_objs = context.selected_objects
        if (len(select_objs) != 1):
            mcell.molecule_glyphs.status = "Select One Molecule"
            return {'FINISHED'}
        if (select_objs[0].type != 'MESH'):
            mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
            return {'FINISHED'}

        mol_obj = select_objs[0]
        mol_shape_name = mol_obj.name

        glyph_name = mcell.molecule_glyphs.glyph

        # There may be objects in the scene with the same name as the glyphs in
        # the glyph library, so we need to deal with this possibility
        new_glyph_name = glyph_name
        if glyph_name in meshes:
            # pattern: glyph name, period, numbers. (example match: "Cube.001")
            pattern = re.compile(r'%s(\.\d+)' % glyph_name)
            competing_names = [m.name for m in meshes if pattern.match(m.name)]
            # example: given this: ["Cube.001", "Cube.3"], make this: [1, 3]
            trailing_nums = [int(n.split('.')[1]) for n in competing_names]
            # remove dups & sort... better way than list->set->list?
            trailing_nums = list(set(trailing_nums))
            trailing_nums.sort()
            i = 0
            gap = False
            for i in range(0, len(trailing_nums)):
                if trailing_nums[i] != i+1:
                    gap = True
                    break
            if not gap and trailing_nums:
                i+=1
            new_glyph_name = "%s.%03d" % (glyph_name, i + 1)

        if (bpy.app.version[0] > 2) or ( (bpy.app.version[0]==2) and (bpy.app.version[1] > 71) ):
          bpy.ops.wm.link(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)
        else:
          bpy.ops.wm.link_append(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)

        mol_mat = mol_obj.material_slots[0].material
        new_mol_mesh = meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        meshes.remove(meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        new_mol_mesh.materials.append(mol_mat)

        return {'FINISHED'}


class MCELL_OT_rxn_output_add(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_add"
    bl_label = "Add Reaction Data Output"
    bl_description = "Add new reaction data output to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.add()
        mcell.rxn_output.active_rxn_output_index = len(
            mcell.rxn_output.rxn_output_list)-1
        check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_rxn_output_remove(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_remove"
    bl_label = "Remove Reaction Data Output"
    bl_description = "Remove selected reaction data output from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.remove(
            mcell.rxn_output.active_rxn_output_index)
        mcell.rxn_output.active_rxn_output_index -= 1
        if (mcell.rxn_output.active_rxn_output_index < 0):
            mcell.rxn_output.active_rxn_output_index = 0

        if mcell.rxn_output.rxn_output_list:
            check_rxn_output(self, context)

        return {'FINISHED'}


def update_release_pattern_rxn_name_list():
    """ Update lists needed to count rxns and use rel patterns. """

    mcell = bpy.context.scene.mcell
    mcell.reactions.reaction_name_list.clear()
    mcell.release_patterns.release_pattern_rxn_name_list.clear()
    rxns = mcell.reactions.reaction_list
    rel_patterns_rxns = mcell.release_patterns.release_pattern_rxn_name_list
    # If a reaction has a reaction name, save it in reaction_name_list for
    # counting in "Reaction Output Settings." Also, save reaction names in
    # release_pattern_rxn_name_list for use as a release pattern, which is
    # assigned in "Molecule Release/Placement"
    for rxn in rxns:
        if rxn.rxn_name and not rxn.status:
            new_rxn_item = mcell.reactions.reaction_name_list.add()
            new_rxn_item.name = rxn.rxn_name
            new_rel_pattern_item = rel_patterns_rxns.add()
            new_rel_pattern_item.name = rxn.rxn_name

    rel_patterns = mcell.release_patterns.release_pattern_list
    for rp in rel_patterns:
        if not rp.status:
            new_rel_pattern_item = rel_patterns_rxns.add()
            new_rel_pattern_item.name = rp.name


def check_rxn_output(self, context):
    """ Format reaction data output. """

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[
        mcell.rxn_output.active_rxn_output_index]
    mol_list = mcell.molecules.molecule_list
    reaction_list = mcell.reactions.reaction_name_list
    molecule_name = rxn_output.molecule_name
    reaction_name = rxn_output.reaction_name
    obj_list = mcell.model_objects.object_list
    object_name = rxn_output.object_name
    region_name = rxn_output.region_name
    rxn_output_name = ""

    try:
        region_list = bpy.data.objects[object_name].mcell.regions.region_list
    except KeyError:
        # The object name isn't a blender object
        region_list = []

    status = ""

    if rxn_output.rxn_or_mol == 'Reaction':
        count_name = reaction_name
        name_list = reaction_list
    else:
        count_name = molecule_name
        name_list = mol_list

    # Check for illegal names (Starts with a letter. No special characters.)
    count_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    c = re.match(count_filter, count_name)
    if c is None:
        status = "Name error: %s" % (count_name)
    else:
        # Check for undefined molecule or reaction names
        c_name = c.group(1)
        if not c_name in name_list:
            status = "Undefined: %s" % (c_name)

    # Use different formatting depending on where we are counting
    if rxn_output.count_location == 'World':
        rxn_output_name = "Count %s in World" % (count_name)
    elif rxn_output.count_location == 'Object':
        if not object_name in obj_list:
            status = "Undefined object: %s" % object_name
        else:
            rxn_output_name = "Count %s in/on %s" % (
                count_name, object_name)
    elif rxn_output.count_location == 'Region':
        if not region_name in region_list:
            status = "Undefined region: %s" % region_name
        else:
            rxn_output_name = "Count %s in/on %s[%s]" % (
                count_name, object_name, region_name)

    # Only update reaction output if necessary to avoid infinite recursion
    if rxn_output.name != rxn_output_name:
        rxn_output.name = rxn_output_name

    # Check for duplicate reaction data
    rxn_output_keys = rxn_output_list.keys()
    if rxn_output_keys.count(rxn_output.name) > 1 and not status:
        status = "Duplicate reaction output: %s" % (rxn_output.name)

    rxn_output.status = status

    return


def check_val_str(val_str, min_val, max_val):
    """ Convert val_str to float if possible. Otherwise, generate error. """

    status = ""
    val = None

    try:
        val = float(val_str)
        if min_val is not None:
            if val < min_val:
                status = "Invalid value for %s: %s"
        if max_val is not None:
            if val > max_val:
                status = "Invalid value for %s: %s"
    except ValueError:
        status = "Invalid value for %s: %s"

    return (val, status)


def update_delay(self, context):
    """ Store the release pattern delay as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    delay_str = release_pattern.delay_str

    (delay, status) = check_val_str(delay_str, 0, None)

    if status == "":
        release_pattern.delay = delay
    else:
        release_pattern.delay_str = "%g" % (release_pattern.delay)


def update_release_interval(self, context):
    """ Store the release interval as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    release_interval_str = release_pattern.release_interval_str

    (release_interval, status) = check_val_str(
        release_interval_str, 1e-12, None)

    if status == "":
        release_pattern.release_interval = release_interval
    else:
        release_pattern.release_interval_str = "%g" % (
            release_pattern.release_interval)


def update_train_duration(self, context):
    """ Store the train duration as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    train_duration_str = release_pattern.train_duration_str

    (train_duration, status) = check_val_str(train_duration_str, 1e-12, None)

    if status == "":
        release_pattern.train_duration = train_duration
    else:
        release_pattern.train_duration_str = "%g" % (
            release_pattern.train_duration)


def update_train_interval(self, context):
    """ Store the train interval as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    train_interval_str = release_pattern.train_interval_str

    (train_interval, status) = check_val_str(train_interval_str, 1e-12, None)

    if status == "":
        release_pattern.train_interval = train_interval
    else:
        release_pattern.train_interval_str = "%g" % (
            release_pattern.train_interval)


def update_clamp_value(self, context):
    """ Store the clamp value as a float if it's legal or generate an error """

    mcell = context.scene.mcell
    surf_class = context.scene.mcell.surface_classes
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    #surf_class_type = surf_class_props.surf_class_type
    #orient = surf_class_props.surf_class_orient
    #molecule = surf_class_props.molecule
    clamp_value_str = surf_class_props.clamp_value_str

    (clamp_value, status) = check_val_str(clamp_value_str, 0, None)

    if status == "":
        surf_class_props.clamp_value = clamp_value
    else:
        #status = status % ("clamp_value", clamp_value_str)
        surf_class_props.clamp_value_str = "%g" % (
            surf_class_props.clamp_value)

    #surf_class_type = convert_surf_class_str(surf_class_type)
    #orient = convert_orient_str(orient)

    #if molecule:
    #    surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
    #        molecule, orient, surf_class_type)
    #else:
    #    surf_class_props.name = "Molec.: NA   Orient.: %s   Type: %s" % (
    #        orient, surf_class_type)

    #surf_class.surf_class_props_status = status

    return


def check_start_seed(self, context):
    """ Ensure start seed is always lte to end seed. """

    run_sim = context.scene.mcell.run_simulation
    start_seed = run_sim.start_seed
    end_seed = run_sim.end_seed

    if start_seed > end_seed:
        run_sim.start_seed = end_seed


def check_end_seed(self, context):
    """ Ensure end seed is always gte to start seed. """
    
    run_sim = context.scene.mcell.run_simulation
    start_seed = run_sim.start_seed
    end_seed = run_sim.end_seed

    if end_seed < start_seed:
        run_sim.end_seed = start_seed
