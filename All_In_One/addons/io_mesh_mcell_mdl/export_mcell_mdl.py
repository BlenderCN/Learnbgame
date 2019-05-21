# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
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

# Copyright (C) 2012: Tom Bartol, bartol@salk.edu
# Contributors: Tom Bartol, Bob Kuczewski


"""
This script exports MCell MDL files from Blender and is a component of
CellBlender.

"""

# python imports
import os
import re
import shutil

# blender imports
import bpy

# from cellblender import cellblender_operators  # Shouldn't need this anymore!!

from cellblender import object_surface_regions
from cellblender.utils import project_files_path

# This function was moved to MCellObjectPropertyGroup in object_surface_regions.py by Bob
# TODO: Delete this commented code ... eventually
#def get_regions(obj):
#    """ Return a dictionary with region names """
#
#    reg_dict = {}
#
#    obj_regs = obj.mcell.regions.region_list
#    for reg in obj_regs:
#        id = str(reg.id)
#        mesh = obj.data
#        #reg_faces = list(cellblender_operators.get_region_faces(mesh,id))
#        reg_faces = list(reg.get_region_faces(mesh))
#
#        reg_faces.sort()
#        reg_dict[reg.name] = reg_faces
#
#    return reg_dict


def save(context, filepath=""):
    """ Top level function for saving the current MCell model
        as MDL.

    """
    print("export_mcell_mdl.py/save()")
    with open(filepath, "w", encoding="utf8", newline="\n") as out_file:
        filedir = os.path.dirname(filepath)
        save_wrapper(context, out_file, filedir)


def dontrun_filter_ignore(unfiltered_item_list):
    """ Apply selected filter/ignore policy.
    
    This function helps reduce boilerplate code.
    """
    
    mcell = bpy.context.scene.mcell

    item_list = []
    error_list = []

    if unfiltered_item_list:
        # Only export and run if everything is valid
        if mcell.cellblender_preferences.invalid_policy == 'dont_run':
            # Populate the list of errors to be shown in the Run Sim panel
            error_list = [entry for entry in unfiltered_item_list if entry.status]
            for error in error_list:
                mcell.run_simulation.error_list.add()
                mcell.run_simulation.error_list[
                    mcell.run_simulation.active_err_index].name = error.status
                mcell.run_simulation.active_err_index += 1
            #item_list = unfiltered_item_list
            item_list = [entry for entry in unfiltered_item_list if not entry.status]
        # Filter out invalid/illegal entries.
        elif mcell.cellblender_preferences.invalid_policy == 'filter':
            item_list = [entry for entry in unfiltered_item_list if not entry.status]
        # The user thinks they know better than CellBlender. Let them try to
        # export and run.
        elif mcell.cellblender_preferences.invalid_policy == 'ignore':
            item_list = unfiltered_item_list

    return item_list, error_list


def save_modular_or_allinone(filedir, main_mdl_file, mdl_filename,
                             save_function, args):
    """ Save output (either in main mdl or included mdl).

    This function helps reduce boilerplate code.

    args should contain everything the function will need except for the actual
    file to be written to, which will be inserted in this function.
    """

    mcell = bpy.context.scene.mcell
    settings = mcell.project_settings

    # Save modular (e.g. Scene.molecules.mdl, Scene.reactions.mdl)
    if mcell.export_project.export_format == 'mcell_mdl_modular':
        main_mdl_file.write("INCLUDE_FILE = \"%s.%s.mdl\"\n\n" %
                       (settings.base_name, mdl_filename))
        filepath = ("%s/%s.%s.mdl" %
                    (filedir, settings.base_name, mdl_filename))
        with open(filepath, "w", encoding="utf8", newline="\n") as mdl_file:
            # Maybe find a cleaner way to handle args list. Looks kind of ugly.
            args.insert(1, mdl_file)
            save_function(*args)
    # Or save everything in main mdl (e.g. Scene.main.mdl)
    else:
        args.insert(1, main_mdl_file)
        save_function(*args)


def save_general(mdl_filename, save_function, save_state, unfiltered_item_list):
    """ Set the filter/ignore policy and write to mdl.
   
    This function helps reduce boilerplate code.
    """

    context = bpy.context    
    filedir = save_state['filedir']
    main_mdl_file = save_state['main_mdl_file']

    item_list, error_list = dontrun_filter_ignore(unfiltered_item_list)
    if item_list and not error_list:
        args = [context, item_list]

        # Add additional parameters here. Only save_reactions for now.
        if save_function.__name__ == 'save_reactions':
            args.append(filedir)

        save_modular_or_allinone(filedir, main_mdl_file, mdl_filename,
                                 save_function, args)

    return item_list


def save_partitions(context, out_file):
    """Export partitions"""

    mcell = context.scene.mcell

    if mcell.partitions.include:
        out_file.write("PARTITION_X = [[%.15g TO %.15g STEP %.15g]]\n" % (
            mcell.partitions.x_start, mcell.partitions.x_end,
            mcell.partitions.x_step))
        out_file.write("PARTITION_Y = [[%.15g TO %.15g STEP %.15g]]\n" % (
            mcell.partitions.y_start, mcell.partitions.y_end,
            mcell.partitions.y_step))
        out_file.write("PARTITION_Z = [[%.15g TO %.15g STEP %.15g]]\n\n" % (
            mcell.partitions.z_start, mcell.partitions.z_end,
            mcell.partitions.z_step))


def save_wrapper(context, out_file, filedir):
    """ This function saves the current model to MDL.

    It provides a wrapper assembling the final mdl piece by piece.

    """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    export_project = mcell.export_project
    project_settings = mcell.project_settings
    ps = mcell.parameter_system
    error_list = mcell.run_simulation.error_list
    error_list.clear()
    mcell.run_simulation.active_err_index = 0
    invalid_policy = mcell.cellblender_preferences.invalid_policy
    save_state = {'main_mdl_file': out_file, 'filedir': filedir}


    # Export parameters: 
    #par_list = mcell.parameters.parameter_list
    #if (len(par_list) > 0):
    #    if export_project.export_format == 'mcell_mdl_modular':
    #        out_file.write("INCLUDE_FILE = \"%s.parameters.mdl\"\n\n" %
    #                       (settings.base_name))
    #        filepath = ("%s/%s.parameters.mdl" %
    #                    (filedir, settings.base_name))
    #        with open(filepath, "w", encoding="utf8", newline="\n") as par_file:
    #            save_parameters(context, par_file, par_list)
    #    else:
    #        save_parameters(context, out_file, par_list)
    
    # Export parameters: 
    if ps and ps.general_parameter_list:
        args = [ps]
        save_modular_or_allinone(
            filedir, out_file, 'parameters', save_general_parameters, args)
        #if export_project.export_format == 'mcell_mdl_modular':
        #    out_file.write("INCLUDE_FILE = \"%s.parameters.mdl\"\n\n" %
        #                   (settings.base_name))
        #    filepath = ("%s/%s.parameters.mdl" %
        #                (filedir, settings.base_name))
        #    with open(filepath, "w", encoding="utf8", newline="\n") as par_file:
        #        save_general_parameters(ps, par_file)
        #else:
        #    save_general_parameters(ps, out_file)
    


    # Export model initialization:
    out_file.write("ITERATIONS = %s\n" % (mcell.initialization.iterations.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    
    out_file.write("TIME_STEP = %s\n" % (mcell.initialization.time_step.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

    if mcell.initialization.vacancy_search_distance.get_expr(ps.panel_parameter_list) != '':
        out_file.write("VACANCY_SEARCH_DISTANCE = %s\n" % (mcell.initialization.vacancy_search_distance.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    else:
        out_file.write("VACANCY_SEARCH_DISTANCE = 10\n\n") # DB: added to avoid error (I think it should have a default value to avoid error in most of the reaction networks)

    # Export optional initialization commands:
    args = [context]
    save_modular_or_allinone(filedir, out_file, 'initialization', save_initialization_commands, args)
    #if export_project.export_format == 'mcell_mdl_modular':
    #    out_file.write("INCLUDE_FILE = \"%s.initialization.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.initialization.mdl" %
    #                (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as init_file:
    #        save_initialization_commands(context, init_file)
    #else:
    #    save_initialization_commands(context, out_file)
    
    save_partitions(context, out_file)

    ## Export partitions:
    #if mcell.partitions.include:
    #    out_file.write("PARTITION_X = [[%.15g TO %.15g STEP %.15g]]\n" % (
    #        mcell.partitions.x_start, mcell.partitions.x_end,
    #        mcell.partitions.x_step))
    #    out_file.write("PARTITION_Y = [[%.15g TO %.15g STEP %.15g]]\n" % (
    #        mcell.partitions.y_start, mcell.partitions.y_end,
    #        mcell.partitions.y_step))
    #    out_file.write("PARTITION_Z = [[%.15g TO %.15g STEP %.15g]]\n\n" % (
    #        mcell.partitions.z_start, mcell.partitions.z_end,
    #        mcell.partitions.z_step))
	    
    # Export molecules:
    unfiltered_mol_list = mcell.molecules.molecule_list
    save_general('molecules', save_molecules, save_state, unfiltered_mol_list)
    #if mcell.cellblender_preferences.filter_invalid:
    #    mol_list = [mol for mol in unfiltered_mol_list if not mol.status]
    #else:
    #    mol_list = unfiltered_mol_list

    #if export_project.export_format == 'mcell_mdl_modular':
    #    out_file.write("INCLUDE_FILE = \"%s.molecules.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.molecules.mdl" %
    #                (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as mol_file:
    #        save_molecules(context, mol_file, mol_list)
    #else:
    #    save_molecules(context, out_file, mol_list)

    # Export surface classes:
    unfiltered_surf_class_list = mcell.surface_classes.surf_class_list
    surf_class_list = save_general(
        'surface_classes', save_surface_classes, save_state,
        unfiltered_surf_class_list)
    #if mcell.cellblender_preferences.filter_invalid:
    #    surf_class_list = [
    #        sc for sc in unfiltered_surf_class_list if not sc.status]
    #else:
    #    surf_class_list = unfiltered_surf_class_list

    #if surf_class_list and export_project.export_format == 'mcell_mdl_modular':
    #    out_file.write("INCLUDE_FILE = \"%s.surface_classes.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.surface_classes.mdl" %
    #                (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as sc_file:
    #        save_surface_classes(context, sc_file, surf_class_list)
    #else:
    #    save_surface_classes(context, out_file, surf_class_list)

    # Export reactions:
    unfiltered_rxn_list = mcell.reactions.reaction_list
    save_general('reactions', save_reactions, save_state, unfiltered_rxn_list)
    #if mcell.cellblender_preferences.filter_invalid:
    #    rxn_list = [rxn for rxn in unfiltered_rxn_list if not rxn.status]
    #else:
    #    rxn_list = unfiltered_rxn_list

    #if rxn_list and export_project.export_format == 'mcell_mdl_modular':
    #    out_file.write("INCLUDE_FILE = \"%s.reactions.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.reactions.mdl" %
    #               (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as react_file:
    #        save_reactions(context, react_file, rxn_list, filedir)
    #else:
    #    save_reactions(context, out_file, rxn_list, filedir)

    # Export model geometry:
    unfiltered_object_list = context.scene.mcell.model_objects.object_list
    object_list = save_general(
        'geometry', save_geometry, save_state, unfiltered_object_list)
    #if mcell.cellblender_preferences.filter_invalid:
    #    object_list = [obj for obj in unfiltered_object_list if not obj.status]
    #else:
    #    object_list = unfiltered_object_list

    #if object_list and export_project.export_format == 'mcell_mdl_modular':
    #    out_file.write("INCLUDE_FILE = \"%s.geometry.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.geometry.mdl" %
    #                (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as geom_file:
    #        save_geometry(context, geom_file, object_list)
    #else:
    #    save_geometry(context, out_file, object_list)

    # Export modify surface regions:
    if surf_class_list:
        unfiltered_msr_list = mcell.mod_surf_regions.mod_surf_regions_list
        save_general('mod_surf_regions', save_mod_surf_regions, save_state,
                     unfiltered_msr_list)
        #if mcell.cellblender_preferences.filter_invalid:
        #    mod_surf_regions_list = [
        #        msr for msr in unfiltered_msr_list if not msr.status]
        #else:
        #    mod_surf_regions_list = unfiltered_msr_list

        #if (mod_surf_regions_list and
        #        export_project.export_format == 'mcell_mdl_modular'):
        #    out_file.write("INCLUDE_FILE = \"%s.mod_surf_regions.mdl\"\n\n" %
        #                   (settings.base_name))
        #    filepath = ("%s/%s.mod_surf_regions.mdl" %
        #                (filedir, settings.base_name))
        #    with open(filepath, "w", encoding="utf8",
        #              newline="\n") as mod_sr_file:
        #        save_mod_surf_regions(
        #            context, mod_sr_file, mod_surf_regions_list)
        #else:
        #    save_mod_surf_regions(context, out_file, mod_surf_regions_list)

    # Export release patterns:
    unfiltered_rel_pattern_list = mcell.release_patterns.release_pattern_list
    save_general('release_patterns', save_rel_patterns, save_state,
                 unfiltered_rel_pattern_list)
    #if mcell.release_patterns.release_pattern_list:
    #    unfiltered_rel_pattern_list = mcell.release_patterns.release_pattern_list
    #    if mcell.cellblender_preferences.filter_invalid:
    #        rel_patterns_list = [
    #            rel_pattern for rel_pattern in unfiltered_rel_pattern_list if not rel_pattern.status]
    #    else:
    #        rel_patterns_list = unfiltered_rel_pattern_list

    #    if (rel_patterns_list and
    #            export_project.export_format == 'mcell_mdl_modular'):
    #        out_file.write("INCLUDE_FILE = \"%s.release_patterns.mdl\"\n\n" %
    #                       (settings.base_name))
    #        filepath = ("%s/%s.release_patterns.mdl" %
    #                    (filedir, settings.base_name))
    #        with open(filepath, "w", encoding="utf8",
    #                  newline="\n") as rel_pattern_file:
    #            save_rel_patterns(
    #                context, rel_pattern_file, rel_patterns_list)
    #    else:
    #        save_rel_patterns(context, out_file, rel_patterns_list)

    # Instantiate Model Geometry and Release sites:
    unfiltered_release_site_list = mcell.release_sites.mol_release_list
    release_site_list, _ = dontrun_filter_ignore(unfiltered_release_site_list)
    #if mcell.cellblender_preferences.filter_invalid:
    #    release_site_list = [
    #        rel for rel in unfiltered_release_site_list if not rel.status]
    #else:
    #    release_site_list = unfiltered_release_site_list

    if object_list or release_site_list:
        out_file.write("INSTANTIATE %s OBJECT\n" % (context.scene.name))
        out_file.write("{\n")

        if object_list:
            save_object_list(context, out_file, object_list)

        if release_site_list:
            save_release_site_list(context, out_file, release_site_list,
                                   mcell)

        out_file.write("}\n\n")

    out_file.write("sprintf(seed,\"%05g\",SEED)\n\n")

    # Export viz output:

    unfiltered_mol_list = mcell.molecules.molecule_list
    unfiltered_mol_viz_list = [
        mol for mol in unfiltered_mol_list if mol.export_viz]
    molecule_viz_list, _ = dontrun_filter_ignore(unfiltered_mol_viz_list)
    molecule_viz_str_list = [mol.name for mol in molecule_viz_list]

    export_all = mcell.viz_output.export_all
    if export_all or molecule_viz_list:
        args = [context, molecule_viz_str_list, export_all]
        save_modular_or_allinone(
            filedir, out_file, 'viz_output', save_viz_output_mdl, args)

    #if mcell.cellblender_preferences.filter_invalid:
    #    molecule_viz_list = [
    #        mol.name for mol in unfiltered_mol_list if mol.export_viz and not
    #        mol.status]
    #else:
    #    molecule_viz_list = [
    #        mol.name for mol in unfiltered_mol_list if mol.export_viz]

    #export_all = mcell.viz_output.export_all
    ##if (export_all or (molecule_viz_list and
    ##__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    #if ((molecule_viz_list or export_all) and export_project.export_format == 'mcell_mdl_modular'):
    #    out_file.write("INCLUDE_FILE = \"%s.viz_output.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.viz_output.mdl" % (filedir, settings.base_name))
    #    with open(filepath, "w", encoding="utf8", newline="\n") as viz_file:
    #        save_viz_output_mdl(context, viz_file, molecule_viz_list, export_all)
    #else:
    #    save_viz_output_mdl(context, out_file, molecule_viz_list, export_all)

    # Export reaction output:
    settings = mcell.project_settings
    unfiltered_rxn_output_list = mcell.rxn_output.rxn_output_list
    
        
    
    save_general('rxn_output', save_rxn_output_mdl, save_state,
                 unfiltered_rxn_output_list)
                 
    
    #JJT:temporary solution for complex output expressions
    complex_rxn_output_list = mcell.rxn_output.complex_rxn_output_list
    if len(complex_rxn_output_list) > 0:
        save_modular_or_allinone(filedir, out_file, 'rxn_output',
                                 save_rxn_output_temp_mdl,[context, complex_rxn_output_list])


    if error_list and invalid_policy == 'dont_run':
        # If anything is invalid, delete all the MDLs.
        project_dir = project_files_path()
        try:
            shutil.rmtree(project_dir)
        except:
            pass

    #if mcell.cellblender_preferences.filter_invalid:
    #    rxn_output_list = [
    #        rxn for rxn in unfiltered_rxn_output_list if not rxn.status]
    #else:
    #    rxn_output_list = unfiltered_rxn_output_list

    #if (rxn_output_list and export_project.export_format == 'mcell_mdl_modular'):
    #    out_file.write("INCLUDE_FILE = \"%s.rxn_output.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.rxn_output.mdl" % (filedir, settings.base_name))
    #    with open(
    #            filepath, "w", encoding="utf8", newline="\n") as mod_rxn_file:
    #        save_rxn_output_mdl(context, mod_rxn_file, rxn_output_list)
    #else:
    #    save_rxn_output_mdl(context, out_file, rxn_output_list)


def save_initialization_commands(context, out_file):
    """ Save the advanced/optional initialization commands.

        This also includes notifications and warnings.

    """

    mcell = context.scene.mcell
    init = mcell.initialization
    ps = mcell.parameter_system
    # Maximum Time Step
    if init.time_step_max.get_expr(ps.panel_parameter_list) != '':
        out_file.write("TIME_STEP_MAX = %s\n" % (init.time_step_max.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Space Step
    if init.space_step.get_expr(ps.panel_parameter_list) != '':
        out_file.write("SPACE_STEP = %s\n" % (init.space_step.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Interaction Radius
    if init.interaction_radius.get_expr(ps.panel_parameter_list) != '':
        out_file.write("INTERACTION_RADIUS = %s\n" % (init.interaction_radius.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Radial Directions
    if init.radial_directions.get_expr(ps.panel_parameter_list) != '':
        out_file.write("RADIAL_DIRECTIONS = %s\n" % (init.radial_directions.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Radial Subdivisions
    if init.radial_subdivisions.get_expr(ps.panel_parameter_list) != '':
        out_file.write("RADIAL_SUBDIVISIONS = %s\n" % (init.radial_subdivisions.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Vacancy Search Distance
    if init.vacancy_search_distance.get_expr(ps.panel_parameter_list) != '':
        out_file.write("VACANCY_SEARCH_DISTANCE = %s\n" % (init.vacancy_search_distance.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Surface Grid Density
    ##### TODO: If surface_grid_density is an integer (as it is) why output it as %.15g format?
    out_file.write("SURFACE_GRID_DENSITY = %s\n" % (init.surface_grid_density.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Accurate 3D Reactions
    if init.accurate_3d_reactions:
        out_file.write("ACCURATE_3D_REACTIONS = TRUE\n")
    else:
        out_file.write("ACCURATE_3D_REACTIONS = FALSE\n")
    # Center Molecules on Grid
    if init.center_molecules_grid:
        out_file.write("CENTER_MOLECULES_ON_GRID = TRUE\n")
    else:
        out_file.write("CENTER_MOLECULES_ON_GRID = FALSE\n")
    # Microscopic Reversibility
    out_file.write("MICROSCOPIC_REVERSIBILITY = %s\n\n" %
                   (init.microscopic_reversibility))

    # Notifications
    out_file.write("NOTIFICATIONS\n{\n")
    if init.all_notifications == 'INDIVIDUAL':

        # Probability Report
        if init.probability_report == 'THRESHOLD':
            out_file.write("   PROBABILITY_REPORT_THRESHOLD = %.15g\n" % (
                init.probability_report_threshold))
        else:
            out_file.write("   PROBABILITY_REPORT = %s\n" % (
                init.probability_report))
        # Diffusion Constant Report
        out_file.write("   DIFFUSION_CONSTANT_REPORT = %s\n" % (
            init.diffusion_constant_report))
        # File Output Report
        if init.file_output_report:
            out_file.write("   FILE_OUTPUT_REPORT = ON\n")
        else:
            out_file.write("   FILE_OUTPUT_REPORT = OFF\n")
        # Final Summary
        if init.final_summary:
            out_file.write("   FINAL_SUMMARY = ON\n")
        else:
            out_file.write("   FINAL_SUMMARY = OFF\n")
        # Iteration Report
        if init.iteration_report:
            out_file.write("   ITERATION_REPORT = ON\n")
        else:
            out_file.write("   ITERATION_REPORT = OFF\n")
        # Partition Location Report
        if init.partition_location_report:
            out_file.write("   PARTITION_LOCATION_REPORT = ON\n")
        else:
            out_file.write("   PARTITION_LOCATION_REPORT = OFF\n")
        # Varying Probability Report
        if init.varying_probability_report:
            out_file.write("   VARYING_PROBABILITY_REPORT = ON\n")
        else:
            out_file.write("   VARYING_PROBABILITY_REPORT = OFF\n")
        # Progress Report
        if init.progress_report:
            out_file.write("   PROGRESS_REPORT = ON\n")
        else:
            out_file.write("   PROGRESS_REPORT = OFF\n")
        # Release Event Report
        if init.release_event_report:
            out_file.write("   RELEASE_EVENT_REPORT = ON\n")
        else:
            out_file.write("   RELEASE_EVENT_REPORT = OFF\n")
        # Release Event Report
        if init.molecule_collision_report:
            out_file.write("   MOLECULE_COLLISION_REPORT = ON\n")
        else:
            out_file.write("   MOLECULE_COLLISION_REPORT = OFF\n")

    else:
        out_file.write(
            "   ALL_NOTIFICATIONS = %s\n" % (init.all_notifications))
    out_file.write('}\n\n')

    # Warnings
    out_file.write("WARNINGS\n{\n")
    if init.all_notifications == 'INDIVIDUAL':

        # Degenerate Polygons
        out_file.write(
            "   DEGENERATE_POLYGONS = %s\n" % init.degenerate_polygons)
        # Negative Diffusion Constant
        out_file.write("   NEGATIVE_DIFFUSION_CONSTANT = %s\n"
                       % init.negative_diffusion_constant)
        # Missing Surface Orientation
        out_file.write("   MISSING_SURFACE_ORIENTATION = %s\n"
                       % init.missing_surface_orientation)
        # Negative Reaction Rate
        out_file.write("   NEGATIVE_REACTION_RATE = %s\n"
                       % init.negative_reaction_rate)
        # Useless Volume Orientation
        out_file.write("   USELESS_VOLUME_ORIENTATION = %s\n"
                       % init.useless_volume_orientation)
        # High Reaction Probability
        out_file.write("   HIGH_REACTION_PROBABILITY = %s\n"
                       % init.high_reaction_probability)
        # Lifetime Too Short
        out_file.write("   LIFETIME_TOO_SHORT = %s\n"
                       % init.lifetime_too_short)
        if init.lifetime_too_short == 'WARNING':
            out_file.write("   LIFETIME_THRESHOLD = %s\n"
                           % init.lifetime_threshold)
        # Missed Reactions
        out_file.write("   MISSED_REACTIONS = %s\n" % init.missed_reactions)
        if init.missed_reactions == 'WARNING':
            out_file.write("   MISSED_REACTION_THRESHOLD = %.15g\n"
                           % init.missed_reaction_threshold)
    else:
        out_file.write(
            "   ALL_WARNINGS = %s\n" % (init.all_warnings))
    out_file.write('}\n\n')


def save_object_list(context, out_file, object_list):
    """ Save the list objects to mdl output file """

    for item in object_list:
        out_file.write("  %s OBJECT %s {}\n" % (item.name, item.name))


def save_release_site_list(context, out_file, release_site_list, mcell):
    """ Save the list of release site to mdl output file. """

    mol_list = mcell.molecules.molecule_list
    ps = mcell.parameter_system

    for release_site in release_site_list:
        out_file.write("  %s RELEASE_SITE\n" % (release_site.name))
        out_file.write("  {\n")


        print ( "release_site.shape = " + release_site.shape )
        
        # release sites with predefined shapes
        if ((release_site.shape == 'CUBIC') |
                (release_site.shape == 'SPHERICAL') |
                (release_site.shape == 'SPHERICAL_SHELL')):

            out_file.write("   SHAPE = %s\n" % (release_site.shape))
            out_file.write("   LOCATION = [%s, %s, %s]\n" %
                           (release_site.location_x.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions),
                            release_site.location_y.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions),
                            release_site.location_z.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
            out_file.write("   SITE_DIAMETER = %s\n" %
                           (release_site.diameter.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        # user defined shapes
        if (release_site.shape == 'OBJECT'):
            inst_obj_expr = instance_object_expr(context,
                                                 release_site.object_expr)
            out_file.write("   SHAPE = %s\n" % (inst_obj_expr))

        if release_site.molecule in mol_list:
            if mol_list[release_site.molecule].type == '2D':
                out_file.write("   MOLECULE = %s%s\n" % (release_site.molecule,
                                                         release_site.orient))
            else:
                out_file.write("   MOLECULE = %s\n" % (release_site.molecule))

        if release_site.quantity_type == 'NUMBER_TO_RELEASE':
            out_file.write("   NUMBER_TO_RELEASE = %s\n" %
                       (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        elif release_site.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
            out_file.write("   GAUSSIAN_RELEASE_NUMBER\n")
            out_file.write("   {\n")
            out_file.write("        MEAN_NUMBER = %s\n" %
                           (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
            out_file.write("        STANDARD_DEVIATION = %s\n" %
                           (release_site.stddev.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
            out_file.write("      }\n")

        elif release_site.quantity_type == 'DENSITY':
            if release_site.molecule in mol_list:
                if mol_list[release_site.molecule].type == '2D':
                    out_file.write("   DENSITY = %s\n" %
                               (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
                else:
                    out_file.write("   CONCENTRATION = %s\n" %
                               (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        out_file.write("   RELEASE_PROBABILITY = %s\n" %
                       (release_site.probability.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        if release_site.pattern:
            out_file.write("   RELEASE_PATTERN = %s\n" %
                           (release_site.pattern))

        out_file.write('  }\n')

# This function is not being used except in commented references within save_wrapper
#
#def save_parameters(context, out_file, par_list):
#    """ Saves parameter info to mdl output file. """
#
#    # Export Parameter:
#    if par_list:
#        out_file.write("/* DEFINE PARAMETERS */\n")
#
#        for par_item in par_list:
#            out_file.write("    %s = %s" % (par_item.name, par_item.value))
#
#            if ((par_item.unit != "") | (par_item.type != "")):
#                out_file.write("    /* ")
#
#                if par_item.unit != "":
#                    out_file.write("%s. " % (par_item.unit))
#
#                if par_item.type != "":
#                    out_file.write("%s. " % (par_item.type))
#
#                out_file.write("*/")
#                out_file.write("\n")
#        out_file.write("\n")


def write_parameter_as_mdl ( p, out_file, as_expr ):
    """ Writes a single parameter as MDL as either a value or an expression """

    # Export Parameter:
    if as_expr:
        # Note that some expressions are allowed to be blank which indicates use of the default VALUE
        if len(p.expr.strip()) <= 0:
            # The expression is blank, so use the value which should be the default
            out_file.write("%s = %.15g" % (p.par_name, p.value))
        else:
            # The expression is not blank, so use it
            out_file.write("%s = %s" % (p.par_name, p.expr))
    else:
        # Output the value rather than the expression
        out_file.write("%s = %.15g" % (p.par_name, p.value))

    if ((p.descr != "") | (p.units != "")):
        out_file.write("    /* ")

        if p.descr != "":
            out_file.write("%s " % (p.descr))

        if p.units != "":
            out_file.write("   units=%s" % (p.units))

        out_file.write(" */")
    out_file.write("\n")



def save_general_parameters(ps, out_file):
    """ Saves parameter info to mdl output file. """

    # Export Parameters:
    if ps and ps.general_parameter_list:
                
        if not ps.export_as_expressions:

            # Output as values ... order doesn't matter
            out_file.write("/* DEFINE PARAMETERS */\n")
            for p in ps.general_parameter_list:
                write_parameter_as_mdl ( p, out_file, ps.export_as_expressions )
            out_file.write("\n")

        else:

            ordered_names = ps.build_dependency_ordered_name_list()
            print ( "Ordered names = " + str(ordered_names) )
            # Output as expressions where order matters
            out_file.write("/* DEFINE PARAMETERS */\n")
            for pn in ordered_names:
                p = ps.general_parameter_list[pn]
                write_parameter_as_mdl ( p, out_file, ps.export_as_expressions )
            out_file.write("\n")


def save_molecules(context, out_file, mol_list):
    """ Saves molecule info to mdl output file. """

    # Export Molecules:
    out_file.write("DEFINE_MOLECULES\n")
    out_file.write("{\n")

    ps = context.scene.mcell.parameter_system

    for mol_item in mol_list:
        out_file.write("  %s\n" % (mol_item.name))
        out_file.write("  {\n")

        if mol_item.type == '2D':
            out_file.write("    DIFFUSION_CONSTANT_2D = %s\n" %
                           (mol_item.diffusion_constant.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))
        else:
            out_file.write("    DIFFUSION_CONSTANT_3D = %s\n" %
                           (mol_item.diffusion_constant.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))

        if mol_item.custom_time_step.get_value(ps.panel_parameter_list) > 0:
            out_file.write("    CUSTOM_TIME_STEP = %s\n" % 
                           (mol_item.custom_time_step.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))
        elif mol_item.custom_space_step.get_value(ps.panel_parameter_list) > 0:
            out_file.write("    CUSTOM_SPACE_STEP = %s\n" %
                           (mol_item.custom_space_step.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))

        if mol_item.target_only:
            out_file.write("    TARGET_ONLY\n")

        out_file.write("  }\n")
    out_file.write("}\n\n")


def save_surface_classes(context, out_file, surf_class_list):
    """ Saves surface class info to mdl output file. """

    mcell = context.scene.mcell

    out_file.write("DEFINE_SURFACE_CLASSES\n")
    out_file.write("{\n")
    for active_surf_class in surf_class_list:
        out_file.write("  %s\n" % (active_surf_class.name))
        out_file.write("  {\n")
        unfiltered_surf_class_props_list = \
            active_surf_class.surf_class_props_list
        surf_class_props_list, _ = dontrun_filter_ignore(
            unfiltered_surf_class_props_list)
        for surf_class_props in surf_class_props_list:
            molecule = surf_class_props.molecule
            orient = surf_class_props.surf_class_orient
            surf_class_type = surf_class_props.surf_class_type
            if surf_class_type == 'CLAMP_CONCENTRATION':
                clamp_value = surf_class_props.clamp_value
                out_file.write("    %s" % surf_class_type)
                out_file.write(   " %s%s = %.15g\n" % (molecule,
                                                    orient,
                                                    clamp_value))
            else:
                out_file.write("    %s = %s%s\n" % (surf_class_type,
                                                    molecule, orient))
        out_file.write("  }\n")
    out_file.write("}\n\n")


def save_rel_patterns(context, out_file, release_pattern_list):
    """ Saves release pattern info to mdl output file. """

    mcell = context.scene.mcell

    ps = mcell.parameter_system
    for active_release_pattern in release_pattern_list:
        out_file.write("DEFINE_RELEASE_PATTERN %s\n" %
                       (active_release_pattern.name))
        out_file.write("{\n")

        out_file.write(
            "  DELAY = %s\n" % active_release_pattern.delay.get_as_string_or_value(
            ps.panel_parameter_list, ps.export_as_expressions))

        if active_release_pattern.release_interval.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  RELEASE_INTERVAL = %s\n" %
                active_release_pattern.release_interval.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        if active_release_pattern.train_duration.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  TRAIN_DURATION = %s\n" %
                active_release_pattern.train_duration.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        if active_release_pattern.train_interval.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  TRAIN_INTERVAL = %s\n" %
                active_release_pattern.train_interval.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        out_file.write(
            "  NUMBER_OF_TRAINS = %s\n" %
            active_release_pattern.number_of_trains.get_as_string_or_value(
            ps.panel_parameter_list,ps.export_as_expressions))

        out_file.write("}\n\n")


def save_reactions(context, out_file, rxn_list, filedir):
    """ Saves reaction info to mdl output file. """

    out_file.write("DEFINE_REACTIONS\n")
    out_file.write("{\n")

    # ps = context.scene.mcell.parameter_system

    for rxn_item in rxn_list:
        rxn_item.write_to_mdl_file ( context, out_file, filedir )
        
        """
        # Moved to cellblender_properties.py / MCellReactionProperty
        out_file.write("  %s " % (rxn_item.name))

        if rxn_item.type == 'irreversible':
            # Use a variable rate constant file if specified
            if rxn_item.variable_rate_switch and rxn_item.variable_rate_valid:
                variable_rate_name = rxn_item.variable_rate
                out_file.write('["%s"]' % (variable_rate_name))
                variable_rate_text = bpy.data.texts[variable_rate_name]
                variable_out_filename = os.path.join(
                    filedir, variable_rate_name)
                with open(variable_out_filename, "w", encoding="utf8",
                          newline="\n") as variable_out_file:
                    variable_out_file.write(variable_rate_text.as_string())
            # Use a single-value rate constant
            else:
                out_file.write("[%s]" % (rxn_item.fwd_rate.get_as_string_or_value(
                               ps.panel_parameter_list,ps.export_as_expressions)))    
        else:
            out_file.write(
                "[>%s, <%s]" % (rxn_item.fwd_rate.get_as_string_or_value(
                ps.panel_parameter_list, ps.export_as_expressions),
                rxn_item.bkwd_rate.get_as_string_or_value(ps.panel_parameter_list,
                ps.export_as_expressions)))

        if rxn_item.rxn_name:
            out_file.write(" : %s\n" % (rxn_item.rxn_name))
        else:
            out_file.write("\n")
        """

    out_file.write("}\n\n")


def save_geometry(context, out_file, object_list):
    """ Saves geometry info to mdl output file. """

    # Export Model Geometry:
    for object_item in object_list:

        data_object = context.scene.objects[object_item.name]

        if data_object.type == 'MESH':

            # NOTE (Markus): I assume this is what is happening
            # here. We need to unhide objects (if hidden) during
            # writing and then restore the state in the end.
            saved_hide_status = data_object.hide
            data_object.hide = False

            context.scene.objects.active = data_object
            bpy.ops.object.mode_set(mode='OBJECT')

            out_file.write("%s POLYGON_LIST\n" % (data_object.name))
            out_file.write("{\n")

            # write vertex list
            out_file.write("  VERTEX_LIST\n")
            out_file.write("  {\n")
            mesh = data_object.data
            matrix = data_object.matrix_world
            vertices = mesh.vertices
            for v in vertices:
                t_vec = matrix * v.co
                out_file.write("    [ %.15g, %.15g, %.15g ]\n" %
                               (t_vec.x, t_vec.y, t_vec.z))

            # close VERTEX_LIST block
            out_file.write("  }\n")

            # write element connection
            out_file.write("  ELEMENT_CONNECTIONS\n")
            out_file.write("  {\n")

            faces = mesh.polygons
            for f in faces:
                out_file.write("    [ %d, %d, %d ]\n" %
                               (f.vertices[0], f.vertices[1],
                                f.vertices[2]))

            # close ELEMENT_CONNECTIONS block
            out_file.write("  }\n")

            # write regions
            # regions = get_regions(data_object)
            regions = data_object.mcell.get_regions_dictionary(data_object)
            if regions:
                out_file.write("  DEFINE_SURFACE_REGIONS\n")
                out_file.write("  {\n")

                region_names = [k for k in regions.keys()]
                region_names.sort()
                for region_name in region_names:
                    out_file.write("    %s\n" % (region_name))
                    out_file.write("    {\n")
                    out_file.write("      ELEMENT_LIST = " +
                                   str(regions[region_name])+'\n')
                    out_file.write("    }\n")

                out_file.write("  }\n")

            # close SURFACE_REGIONS block
            out_file.write("}\n\n")

            # restore proper object visibility state
            data_object.hide = saved_hide_status


def save_viz_output_mdl(context, out_file, molecule_viz_list, export_all):
    """ Saves visualizaton output info to mdl output file. """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    start = mcell.viz_output.start
    end = mcell.viz_output.end
    step = mcell.viz_output.step
    all_iterations = mcell.viz_output.all_iterations

    if molecule_viz_list or export_all:
        out_file.write("VIZ_OUTPUT\n{\n")
        out_file.write("  MODE = CELLBLENDER\n")
        out_file.write("  FILENAME = \"./viz_data/seed_\" & seed & \"/%s\"\n" % settings.base_name)
        out_file.write("  MOLECULES\n")
        out_file.write("  {\n")
        if export_all:
            out_file.write("    NAME_LIST {ALL_MOLECULES}\n")
        else:
            out_file.write("    NAME_LIST {%s}\n" % " ".join(molecule_viz_list))
        if all_iterations:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ ALL_ITERATIONS}\n")
        else:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ [[%s TO %s STEP %s]]}\n" %
                (start, end, step))
        out_file.write("  }\n")
        out_file.write("}\n\n")

def save_rxn_output_mdl(context, out_file, rxn_output_list):
    """ Saves reaction output info to mdl output file. """
    
    mcell = context.scene.mcell
    ps = mcell.parameter_system

    out_file.write("REACTION_DATA_OUTPUT\n{\n")
    rxn_step = mcell.rxn_output.rxn_step.get_as_string_or_value(
        ps.panel_parameter_list, ps.export_as_expressions)
    out_file.write("  STEP=%s\n" % rxn_step)

    for rxn_output in rxn_output_list:
        if rxn_output.rxn_or_mol == 'Reaction':
            count_name = rxn_output.reaction_name
        else:
            count_name = rxn_output.molecule_name
        object_name = rxn_output.object_name
        region_name = rxn_output.region_name
        if rxn_output.count_location == 'World':
            out_file.write(
                "  {COUNT[%s,WORLD]}=> \"./react_data/seed_\" & seed & "
                "\"/%s.World.dat\"\n" % (count_name, count_name,))
        elif rxn_output.count_location == 'Object':
            out_file.write(
                "  {COUNT[%s,%s.%s]}=> \"./react_data/seed_\" & seed & "
                "\"/%s.%s.dat\"\n" % (count_name, context.scene.name,
                object_name, count_name, object_name))
        elif rxn_output.count_location == 'Region':
            out_file.write(
                "  {COUNT[%s,%s.%s[%s]]}=> \"./react_data/seed_\" & seed & "
                "\"/%s.%s.%s.dat\"\n" % (count_name, context.scene.name,
                object_name, region_name, count_name, object_name, region_name))
                

    out_file.write("}\n\n")

def save_rxn_output_temp_mdl(context, out_file, rxn_output_list):
    #JJT:temporary code that outsputs imported rxn output expressions
    #remove when we figure out how to add this directly to the interface
    
    mcell = context.scene.mcell
    ps = mcell.parameter_system

    out_file.write("REACTION_DATA_OUTPUT\n{\n")
    rxn_step = mcell.rxn_output.rxn_step.get_as_string_or_value(
        ps.panel_parameter_list, ps.export_as_expressions)
    out_file.write("  STEP=%s\n" % rxn_step)

    
    for rxn_output in rxn_output_list:
        outputStr = rxn_output.molecule_name
        if outputStr not in ['',None]:
            outputStr = '{%s} =>  "./react_data/seed_" & seed & \"/%s.World.dat\"\n' % (outputStr,rxn_output.name)
            out_file.write(outputStr)
        else:
            print('Found invalid reaction output {0}'.format(outputStr))
    out_file.write("}\n\n")


def save_mod_surf_regions(context, out_file, mod_surf_regions_list):
    """ Saves modify surface region info to mdl output file. """

    out_file.write("MODIFY_SURFACE_REGIONS\n")
    out_file.write("{\n")
    for active_mod_surf_regions in mod_surf_regions_list:
        surf_class_name = active_mod_surf_regions.surf_class_name
        out_file.write("  %s[%s]\n" %
                       (active_mod_surf_regions.object_name,
                        active_mod_surf_regions.region_name))
        out_file.write("  {\n    SURFACE_CLASS = %s\n  }\n" %
                       (surf_class_name))
    out_file.write("}\n\n")


def instance_object_expr(context, expression):
    """ Converts an object expression into an instantiated MDL object

    This function converts an object specification coming from
    the GUI into a fully qualified (instantiated) MDL expression.
    E.g., if the instantiated object is named *Scene*

      - an object *Cube* will be converted to *Scene.Cube* and
      - an expression *Cube + Sphere* will be converted to
        "Scene.Cube + Scene.Sphere"

    NOTE (Markus): I am not sure if this function isn't a bit
    too complex for the task (i.e. regular expressions and all)
    but perhaps it's fine. Time will tell.

    """

    token_spec = [
        ("ID", r"[A-Za-z]+[0-9A-Za-z_.]*(\[[A-Za-z]+[0-9A-Za-z_.]*\])?"),
                              # Identifiers
        ("PAR", r"[\(\)]"),   # Parentheses
        ("OP", r"[\+\*\-]"),  # Boolean operators
        ("SKIP", r"[ \t]"),   # Skip over spaces and tabs
    ]
    token_regex = "|".join("(?P<%s>%s)" % pair for pair in token_spec)
    get_token = re.compile(token_regex).match

    instantiated_expression = ""
    pos = 0
    line_start = 0
    m = get_token(expression)
    while m:
        token_type = m.lastgroup
        if token_type != "SKIP":
            val = m.group(token_type)

            if token_type == "ID":
                val = context.scene.name + "." + val
            elif token_type == "OP":
                val = " " + val + " "

            instantiated_expression = instantiated_expression + val

        pos = m.end()
        m = get_token(expression, pos)

    if pos != len(expression):
        pass

    return instantiated_expression
