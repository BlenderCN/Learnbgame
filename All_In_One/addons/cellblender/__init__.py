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

import os
import atexit

bl_info = {
    "name": "CellBlender",
    "author": "Tom Bartol, Dipak Barua, Jacob Czech, Markus Dittrich, "
        "James Faeder, Bob Kuczewski, Devin Sullivan, Jose Juan Tapia",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "api": 55057,
    "location": "View3D -> ToolShelf -> CellBlender",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "https://github.com/mcellteam/cellblender/issues",
    "category": "Learnbgame",
}

from cellblender import cellblender_source_info
# cellblender_info was moved from __init__.py to cellblender_source_info.py
# This assignment fixes any broken references ... for now:
cellblender_info = cellblender_source_info.cellblender_info


simulation_popen_list = []


# To support reload properly, try to access a package var.
# If it's there, reload everything
if "bpy" in locals():
    print("Reloading CellBlender")
    import imp
    imp.reload(data_model)
    imp.reload(cellblender_properties)
    imp.reload(cellblender_panels)
    imp.reload(cellblender_operators)
    imp.reload(parameter_system)
    imp.reload(cellblender_molecules)
    imp.reload(object_surface_regions)
    imp.reload(io_mesh_mcell_mdl)
    imp.reload(sim_runner_queue)
    imp.reload(mdl)         # BK: Added for MDL
    imp.reload(bng)         # DB: Adde for BNG
    #    imp.reload(sbml)        #JJT: Added for SBML

    # Use "try" for optional modules
    try:
        imp.reload(data_plotters)
    except:
        print("cellblender.data_plotters was not reloaded")
else:
    print("Importing CellBlender")
    from . import data_model
    from . import cellblender_properties
    from . import cellblender_panels
    from . import cellblender_operators
    from . import parameter_system
    from . import cellblender_molecules
    from . import object_surface_regions
    from . import io_mesh_mcell_mdl
    from . import sim_runner_queue
    from . import mdl  # BK: Added for MDL
    from . import bng  # DB: Added for BNG
    #    from . import sbml #JJT: Added for SBML

    # Use "try" for optional modules
    try:
        from . import data_plotters
    except:
        print("cellblender.data_plotters was not imported")

simulation_queue = sim_runner_queue.SimQueue()

import bpy
import sys


#cellblender_added_handlers = []

def add_handler ( handler_list, handler_function ):
    """ Only add a handler if it's not already in the list """
    if not (handler_function in handler_list):
        handler_list.append ( handler_function )
        
        #cellblender_added_handlers


def remove_handler ( handler_list, handler_function ):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove ( handler_function )


# We use per module class registration/unregistration
def register():
    print ( "Registering CellBlender with Blender version = " + str(bpy.app.version) )
    bpy.utils.register_module(__name__)

    # Unregister and re-register panels to display them in order
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_cellblender_preferences)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_project_settings)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_run_simulation)         # Need to unregister because it's registered automatically
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_run_simulation_queue)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_viz_results)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_model_objects)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_partitions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_initialization)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_parameters)
    bpy.utils.unregister_class(parameter_system.MCELL_PT_parameter_system)
    bpy.utils.unregister_class(cellblender_molecules.MCELL_PT_define_molecules)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_reactions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_surface_classes)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_mod_surface_regions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_release_pattern)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_molecule_release)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_reaction_output_settings)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_visualization_output_settings)


    # Don't normally re-register individual panels here with new panel system, but do it for now to test slowdown problem
    # TMB: Don't re-register here to disable all individual panels in old panel system

#    bpy.utils.register_class(cellblender_panels.MCELL_PT_cellblender_preferences)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_project_settings)
##    bpy.utils.register_class(cellblender_panels.MCELL_PT_run_simulation)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_run_simulation_queue)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_viz_results)
#    bpy.utils.register_class(parameter_system.MCELL_PT_parameter_system)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_model_objects)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_partitions)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_initialization)
#    bpy.utils.register_class(cellblender_molecules.MCELL_PT_define_molecules)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_define_reactions)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_define_surface_classes)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_mod_surface_regions)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_release_pattern)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_molecule_release)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_reaction_output_settings)
#    bpy.utils.register_class(cellblender_panels.MCELL_PT_visualization_output_settings)


    bpy.types.INFO_MT_file_import.append(io_mesh_mcell_mdl.menu_func_import)
    bpy.types.INFO_MT_file_export.append(io_mesh_mcell_mdl.menu_func_export)


    # BK: Added for MDL import
    bpy.types.INFO_MT_file_import.append(mdl.menu_func_import)

    # DB: Added for BioNetGen import
    bpy.types.INFO_MT_file_import.append(bng.menu_func_import)

    #JJT: And SBML import
    #bpy.types.INFO_MT_file_import.append(sbml.menu_func_import)

    # BK: Added for Data Model import and export
    bpy.types.INFO_MT_file_import.append(data_model.menu_func_import)
    bpy.types.INFO_MT_file_export.append(data_model.menu_func_export)
    bpy.types.INFO_MT_file_import.append(data_model.menu_func_import_all)
    bpy.types.INFO_MT_file_export.append(data_model.menu_func_export_all)
    bpy.types.INFO_MT_file_export.append(data_model.menu_func_print)



    bpy.types.Scene.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellPropertyGroup)
    bpy.types.Object.mcell = bpy.props.PointerProperty(
        type=object_surface_regions.MCellObjectPropertyGroup)


    print("CellBlender registered")
    if (bpy.app.version not in cellblender_info['supported_version_list']):
        print("Warning, current Blender version", bpy.app.version,
              " is not in supported list:",
              cellblender_info['supported_version_list'])

    print("CellBlender Addon found: ", __file__)
    cellblender_info["cellblender_addon_path"] = os.path.dirname(__file__)
    print("CellBlender Addon Path is " + cellblender_info["cellblender_addon_path"])
    addon_path = os.path.dirname(__file__)

    # SELECT ONE OF THE FOLLOWING THREE:

    # To compute the ID on load, uncomment this choice and comment out the other two
    #cellblender_source_info.identify_source_version(addon_path,verbose=True)

    # To import the ID as python code, uncomment this choice and comment out the other two
    #from . import cellblender_id
    #cellblender_info['cellblender_source_sha1'] = cellblender_id.cellblender_id

    # To read the ID from the file as text, uncomment this choice and comment out the other two
    
    cs = open ( os.path.join(addon_path, 'cellblender_id.py') ).read()
    cellblender_info['cellblender_source_sha1'] = cs[1+cs.find("'"):cs.rfind("'")]


    print ( "CellBlender Source SHA1 = " + cellblender_info['cellblender_source_sha1'] )

    # Use "try" for optional modules
    try:
        # print ( "Reloading data_plottters" )
        cellblender_info['cellblender_plotting_modules'] = []
        plotters_list = data_plotters.find_plotting_options()
        # data_plotters.print_plotting_options()
        print("Begin installing the plotters")
        for plotter in plotters_list:
            #This assignment could be done all at once since plotters_list is
            # already a list.
            cellblender_info['cellblender_plotting_modules'] = \
                cellblender_info['cellblender_plotting_modules'] + [plotter]
            print("  System meets requirements for %s" % (plotter.get_name()))
    except:
        print("Error installing some plotting packages" + sys.exc_value)


    print ( "Adding handlers to bpy.app.handlers" )
    # Note that handlers appear to be called in the order listed here (first listed are called first)
    
    # Add the frame change pre handler
    add_handler ( bpy.app.handlers.frame_change_pre, cellblender_operators.frame_change_handler )

    # Add the load_pre handlers
    add_handler ( bpy.app.handlers.load_pre, cellblender_properties.report_load_pre )

    # Add the load_post handlers
    add_handler ( bpy.app.handlers.load_post, data_model.load_post )
    add_handler ( bpy.app.handlers.load_post, cellblender_operators.clear_run_list )
    add_handler ( bpy.app.handlers.load_post, cellblender_operators.model_objects_update )
    add_handler ( bpy.app.handlers.load_post, object_surface_regions.object_regions_format_update )
    add_handler ( bpy.app.handlers.load_post, cellblender_operators.mcell_valid_update )
    # add_handler ( bpy.app.handlers.load_post, cellblender_operators.set_defaults )
    
    
    ### add_handler ( bpy.app.handlers.load_post, cellblender_operators.init_properties )
    
    
    add_handler ( bpy.app.handlers.load_post, cellblender_operators.load_preferences )
    add_handler ( bpy.app.handlers.load_post, cellblender_properties.scene_loaded )
    add_handler ( bpy.app.handlers.load_post, cellblender_operators.read_viz_data_load_post )

    # Add the scene update pre handler
    add_handler ( bpy.app.handlers.scene_update_pre, cellblender_properties.scene_loaded )

    # Add the save_pre handlers
    add_handler ( bpy.app.handlers.save_pre, data_model.save_pre )
    add_handler ( bpy.app.handlers.save_pre, cellblender_operators.model_objects_update )

    # Register atexit function to shutdown simulation queue before quitting Blender
    atexit.register(simulation_queue.shutdown)

    print("CellBlender Registered")



def unregister():
    remove_handler ( bpy.app.handlers.frame_change_pre, cellblender_operators.frame_change_handler )
    remove_handler ( bpy.app.handlers.load_pre,         cellblender_properties.report_load_pre )
    remove_handler ( bpy.app.handlers.load_post, data_model.load_post )
    remove_handler ( bpy.app.handlers.load_post, cellblender_operators.clear_run_list )
    remove_handler ( bpy.app.handlers.load_post, cellblender_operators.model_objects_update )
    remove_handler ( bpy.app.handlers.load_post, object_surface_regions.object_regions_format_update )
    remove_handler ( bpy.app.handlers.load_post, cellblender_operators.mcell_valid_update )
    
    
    ### remove_handler ( bpy.app.handlers.load_post, cellblender_operators.init_properties )
    
    
    remove_handler ( bpy.app.handlers.load_post, cellblender_operators.load_preferences )
    remove_handler ( bpy.app.handlers.load_post, cellblender_properties.scene_loaded )
    remove_handler ( bpy.app.handlers.scene_update_pre, cellblender_properties.scene_loaded )
    remove_handler ( bpy.app.handlers.save_pre, data_model.save_pre )
    remove_handler ( bpy.app.handlers.save_pre, cellblender_operators.model_objects_update )

    bpy.utils.unregister_module(__name__)

    print("CellBlender unregistered")


# for testing
if __name__ == '__main__':
    register()
