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
This file contains the classes defining and handling the CellBlender Data Model.
The CellBlender Data Model is intended to be a fairly stable representation of
a CellBlender project which should be compatible across CellBlender versions.
"""


"""
  CONVERSION NOTES:
    How do our CellBlender reaction fields/controls handle catalytic reactions?
    Would it be better to allow a full reaction expression rather than reactants/products?
    Should we have an option for using full reaction syntax?
    What is the MCellReactionsPanelProperty.reaction_name_list? Is it needed any more?
    
    MCellMoleculeReleaseProperty:
       Do we still need location, or is it handled by location_x,y,z?

    Release Patterns:

      Should "release pattern" be called "release timing" or "release train"?

      Why does MCellReleasePatternPanelProperty contain:
         release_pattern_rxn_name_list?
      JC: There is a "Release Pattern" field in the "Molecule Placement" panel.
      One can assign either a release pattern or a named reaction to it. 
       
"""


# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent

# python imports
import pickle
import os

from bpy_extras.io_utils import ExportHelper
import cellblender
# import cellblender/cellblender_id


def code_api_version():
    return 1


def flag_incompatible_data_model ( message ):
    print ( "#########################################################" )
    print ( "#########################################################" )
    print ( "Note: an Incompatible CellBlender Data Model was detected" )
    print ( message )
    print ( "#########################################################" )
    print ( "#########################################################" )

def handle_incompatible_data_model ( message ):
    print ( "###########################################################" )
    print ( "###########################################################" )
    print ( "Quitting Blender due to Incompatible CellBlender Data Model" )
    print ( message )
    print ( "###########################################################" )
    print ( "###########################################################" )
    bpy.ops.wm.quit_blender()


data_model_depth = 0
def dump_data_model ( name, dm ):
    global data_model_depth
    if type(dm) == type({'a':1}):  #dm is a dictionary
        print ( str(data_model_depth*"  ") + name + " {}" )
        data_model_depth += 1
        for k,v in sorted(dm.items()):
            dump_data_model ( k, v )
        data_model_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
        print ( str(data_model_depth*"  ") + name + " []" )
        data_model_depth += 1
        i = 0
        for v in dm:
            k = name + "["+str(i)+"]"
            dump_data_model ( k, v )
            i += 1
        data_model_depth += -1
#    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
    elif (type(dm) == type('a1')):  #dm is a string
        print ( str(data_model_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
        print ( str(data_model_depth*"  ") + name + " = " + str(dm) )


def pickle_data_model ( dm ):
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    return ( pickle.loads ( dmp.encode('latin1') ) )

def save_data_model_to_file ( mcell_dm, file_name ):
    print ( "Saving CellBlender model to file: " + file_name )
    dm = { 'mcell': mcell_dm }
    f = open ( file_name, 'w' )
    f.write ( pickle_data_model(dm) )
    f.close()
    print ( "Done saving CellBlender model." )



class PrintDataModel(bpy.types.Operator):
    '''Print the CellBlender data model to the console'''
    bl_idname = "cb.print_data_model" 
    bl_label = "Print Data Model"
    bl_description = "Print the CellBlender Data Model to the console"

    def execute(self, context):
        print ( "Printing CellBlender Data Model:" )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context )
        dump_data_model ( "Data Model", {"mcell": mcell_dm} )
        return {'FINISHED'}


class ExportDataModel(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model as a Python Pickle in a text file'''
    bl_idname = "cb.export_data_model" 
    bl_label = "Export Data Model"
    bl_description = "Export CellBlender Data Model to a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        #print ( "Saving CellBlender model to file: " + self.filepath )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=False )
        save_data_model_to_file ( mcell_dm, self.filepath )
        """
        dm = { 'mcell': mcell_dm }
        f = open ( self.filepath, 'w' )
        f.write ( pickle_data_model(dm) )
        f.close()
        """
        #print ( "Done saving CellBlender model." )
        return {'FINISHED'}


class ExportDataModelAll(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model including geometry as a Python Pickle in a text file'''
    bl_idname = "cb.export_data_model_all" 
    bl_label = "Export Data Model with Geometry"
    bl_description = "Export CellBlender Data Model and Geometry to a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        #print ( "Saving CellBlender model and geometry to file: " + self.filepath )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        save_data_model_to_file ( mcell_dm, self.filepath )
        """
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        dm = { 'mcell': mcell_dm }
        f = open ( self.filepath, 'w' )
        f.write ( pickle_data_model(dm) )
        f.close()
        print ( "Done saving CellBlender model." )
        """
        return {'FINISHED'}


class ImportDataModel(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model from a Python Pickle in a text file'''
    bl_idname = "cb.import_data_model" 
    bl_label = "Import Data Model"
    bl_description = "Import CellBlender Data Model from a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from file: " + self.filepath + " ..." )
        f = open ( self.filepath, 'r' )
        pickle_string = f.read()
        f.close()

        dm = unpickle_data_model ( pickle_string )
        dm['mcell'] = cellblender.cellblender_properties.MCellPropertyGroup.upgrade_data_model(dm['mcell'])
        context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'] )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}


class ImportDataModelAll(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model from a Python Pickle in a text file'''
    bl_idname = "cb.import_data_model_all" 
    bl_label = "Import Data Model with Geometry"
    bl_description = "Import CellBlender Data Model and Geometry from a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from file: " + self.filepath + " ..." )
        f = open ( self.filepath, 'r' )
        pickle_string = f.read()
        f.close()

        dm = unpickle_data_model ( pickle_string )
        dm['mcell'] = cellblender.cellblender_properties.MCellPropertyGroup.upgrade_data_model(dm['mcell'])
        context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'], geometry=True )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}

def save_mcell_preferences ( mcell ):
    mp = {}
    mp['mcell_binary'] = mcell.cellblender_preferences.mcell_binary
    mp['mcell_binary_valid'] = mcell.cellblender_preferences.mcell_binary_valid
    mp['python_binary'] = mcell.cellblender_preferences.python_binary
    mp['python_binary_valid'] = mcell.cellblender_preferences.python_binary_valid
    mp['bionetgen_location'] = mcell.cellblender_preferences.bionetgen_location
    mp['bionetgen_location_valid'] = mcell.cellblender_preferences.bionetgen_location_valid
    return mp

def restore_mcell_preferences ( mp, mcell ):
    mcell.cellblender_preferences.mcell_binary = mp['mcell_binary']
    mcell.cellblender_preferences.mcell_binary_valid = mp['mcell_binary_valid']
    mcell.cellblender_preferences.python_binary = mp['python_binary']
    mcell.cellblender_preferences.python_binary_valid = mp['python_binary_valid']
    mcell.cellblender_preferences.bionetgen_location = mp['bionetgen_location']
    mcell.cellblender_preferences.bionetgen_location_valid = mp['bionetgen_location_valid']

import traceback

def upgrade_properties_from_data_model ( context ):
    print ( "Upgrading Properties from Data Model" )
    mcell = context.scene.mcell

    if 'data_model' in mcell:

        print ( "Found a data model to upgrade." )
        dm = cellblender.data_model.unpickle_data_model ( mcell['data_model'] )

        # Save any preferences that are stored in properties but not in the Data Model
        mp = save_mcell_preferences ( mcell )

        print ( "Delete MCell RNA properties" )
        del bpy.types.Scene.mcell
        if context.scene.get ( 'mcell' ):
          del context.scene['mcell']

        # Something like the following code would be needed if the
        #  internal data model handled the regions. But at this time
        #  the regions are handled and upgraded separately in:
        #           object_surface_regions.py
        #
        #del bpy.types.Object.mcell
        #for obj in context.scene.objects:
        #  if obj.get ( 'mcell' ):
        #    del obj['mcell']
        #    if obj.type == 'MESH':
        #      m = obj.data
        #      if m.get ( 'mcell' ):
        #        del m['mcell']
        #bpy.types.Object.mcell = bpy.props.PointerProperty(type=cellblender.object_surface_regions.MCellObjectPropertyGroup)

        print ( "Reinstate MCell RNA properties" )

        bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_properties.MCellPropertyGroup)

        print ( "Reinstated MCell RNA properties" )

        # Restore the local variable mcell to be consistent with not taking this branch of the if.
        mcell = context.scene.mcell
        
        # Restore the current preferences that had been saved
        restore_mcell_preferences ( mp, mcell )

        # Do the actual updating of properties from data model right here
        dm = cellblender.cellblender_properties.MCellPropertyGroup.upgrade_data_model(dm)
        mcell.build_properties_from_data_model ( context, dm )
    else:
        print ( "Warning: This should never happen." )
        traceback.print_stack()
        print ( "No data model to upgrade ... building a data model and then recreating properties." )
        dm = mcell.build_data_model_from_properties ( context )
        dm = cellblender.cellblender_properties.MCellPropertyGroup.upgrade_data_model(dm)
        mcell.build_properties_from_data_model ( context, dm )

    # Update the source_id
    mcell['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
    #mcell.versions_match = True
    cellblender.cellblender_info['versions_match'] = True
    print ( "Finished Upgrading Properties from Data Model" )


def upgrade_RC3_properties_from_data_model ( context ):
      print ( "Upgrading Properties from an RC3 File Data Model" )
      mcell = context.scene.mcell

      dm = None
      if 'data_model' in mcell:
          # This must be an RC4 file?
          print ( "Found a data model to upgrade." )
          dm = cellblender.data_model.unpickle_data_model ( mcell['data_model'] )
      else:
          print ( "No data model in RC3 file ... building a data model and then recreating properties." )
          dm = mcell.build_data_model_from_RC3_ID_properties ( context )

      # Save any preferences that are stored in properties but not in the Data Model
      mp = save_mcell_preferences ( mcell )

      print ( "Delete MCell RNA properties" )
      del bpy.types.Scene.mcell
      if context.scene.get ( 'mcell' ):
        del context.scene['mcell']

      # Something like the following code would be needed if the
      #  internal data model handled the regions. But at this time
      #  the regions are handled and upgraded separately in:
      #           object_surface_regions.py
      #
      #del bpy.types.Object.mcell
      #for obj in context.scene.objects:
      #  if obj.get ( 'mcell' ):
      #    del obj['mcell']
      #    if obj.type == 'MESH':
      #      m = obj.data
      #      if m.get ( 'mcell' ):
      #        del m['mcell']
      #bpy.types.Object.mcell = bpy.props.PointerProperty(type=cellblender.object_surface_regions.MCellObjectPropertyGroup)

      print ( "Reinstate MCell RNA properties" )

      bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_properties.MCellPropertyGroup)

      print ( "Reinstated MCell RNA properties" )

      # Restore the local variable mcell
      mcell = context.scene.mcell

      # Restore the current preferences that had been saved
      restore_mcell_preferences ( mp, mcell )

      # Do the actual updating of properties from data model right here
      dm = cellblender.cellblender_properties.MCellPropertyGroup.upgrade_data_model(dm)
      mcell.build_properties_from_data_model ( context, dm )

      # Update the source_id
      mcell['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
      #mcell.versions_match = True
      cellblender.cellblender_info['versions_match'] = True
      print ( "Finished Upgrading Properties from RC3 Data Model" )



# Construct the data model property
@persistent
def save_pre(context):
    """Set the "saved_by_source_id" value and store a data model based on the current property settings in this application"""
    # The context appears to always be "None"
    print ( "========================================" )
    source_id = cellblender.cellblender_info['cellblender_source_sha1']
    print ( "save_pre() has been called ... source_id = " + source_id )
    if cellblender.cellblender_info['versions_match']:
        print ( "save_pre() called with versions matching ... save Data Model and Source ID" )
        if not context:
            # The context appears to always be "None", so use bpy.context
            context = bpy.context
        if hasattr ( context.scene, 'mcell' ):
            print ( "Updating source ID of mcell before saving" )
            mcell = context.scene.mcell
            mcell['saved_by_source_id'] = source_id
            dm = mcell.build_data_model_from_properties ( context )
            context.scene.mcell['data_model'] = pickle_data_model(dm)
    else:
        print ( "save_pre() called with versions not matching ... force an upgrade." )
        if not context:
            # The context appears to always be "None", so use bpy.context
            context = bpy.context
        if hasattr ( context.scene, 'mcell' ):
            mcell = context.scene.mcell
            # Only save the data model if mcell has been initialized
            if hasattr ( mcell, 'initialized' ):
                if mcell.initialized:
                    print ( "Upgrading blend file to current version before saving" )
                    mcell = context.scene.mcell
                    if not mcell.get ( 'saved_by_source_id' ):
                        # This .blend file was created with CellBlender RC3 / RC4
                        upgrade_RC3_properties_from_data_model ( context )
                    else:
                        upgrade_properties_from_data_model ( context )
                    mcell['saved_by_source_id'] = source_id
                    dm = mcell.build_data_model_from_properties ( context )
                    context.scene.mcell['data_model'] = pickle_data_model(dm)
    print ( "========================================" )


    """
    print ( "data_model.save_pre called" )

    if not context:
        context = bpy.context

    if 'mcell' in context.scene:
        dm = context.scene.mcell.build_data_model_from_properties ( context )
        context.scene.mcell['data_model'] = pickle_data_model(dm)

    return
    """


# Check for a data model in the properties
@persistent
def load_post(context):
    """Detect whether the loaded .blend file matches the current addon and set a flag to be used by other code"""

    print ( "load post handler: data_model.load_post() called" )

    # SELECT ONE OF THE FOLLOWING THREE:

    # To compute the ID on load, uncomment this choice and comment out the other three
    #cellblender_source_info.identify_source_version(addon_path,verbose=True)

    # To import the ID as python code, uncomment this choice and comment out the other three
    #from . import cellblender_id
    #cellblender.cellblender_info['cellblender_source_sha1'] = cellblender_id.cellblender_id

    # To read the ID from the file as text, uncomment this choice and comment out the other three
    #cs = open ( os.path.join(os.path.dirname(__file__), 'cellblender_id.py') ).read()
    #cellblender.cellblender_info['cellblender_source_sha1'] = cs[1+cs.find("'"):cs.rfind("'")]

    # To read the ID from the file as text via a shared call uncomment this choice and comment out the other three
    cellblender.cellblender_info['cellblender_source_sha1'] = cellblender.cellblender_source_info.identify_source_version_from_file()


    source_id = cellblender.cellblender_info['cellblender_source_sha1']
    print ( "cellblender source id = " + source_id )

    if not context:
        # The context appears to always be "None", so use bpy.context
        context = bpy.context

    api_version_in_blend_file = -1  # TODO May not be used

    #if 'mcell' in context.scene:
    if hasattr ( context.scene, 'mcell' ):
        mcell = context.scene.mcell

        # mcell.versions_match = False
        cellblender.cellblender_info['versions_match'] = False
        if 'saved_by_source_id' in mcell:
            saved_by_id = mcell['saved_by_source_id']
            print ( "load_post() opened a blend file with source_id = " + saved_by_id )
            if source_id == saved_by_id:
                #mcell.versions_match = True
                cellblender.cellblender_info['versions_match'] = True
            else:
                # Don't update the properties here. Just flag to display the "Upgrade" button for user to choose.
                #mcell.versions_match = False
                cellblender.cellblender_info['versions_match'] = False
    #print ( "End of load_post(): mcell.versions_match = " + str(mcell.versions_match) )
    print ( "End of load_post(): cellblender.cellblender_info['versions_match'] = " + str(cellblender.cellblender_info['versions_match']) )
    print ( "========================================" )


    """
    print ( "Delete MCell RNA properties" )
    del bpy.types.Scene.mcell
    if context.scene.get ( 'mcell' ):
      del context.scene['mcell']
    print ( "Reinstate MCell RNA properties" )
    bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_properties.MCellPropertyGroup)
    print ( "Reinstated MCell RNA properties" )
    """

    #print ( "Unregister, delete all ID properties, and Reregister" )
    # Unregister, delete all ID properties, and Reregister
    #bpy.utils.unregister_module('cellblender')
    #print ( "Unregistered" )

    #bpy.utils.register_module('cellblender')
    #mcell = context.scene.mcell
    #print ( "Reregistered" )


def menu_func_import(self, context):
    self.layout.operator("cb.import_data_model", text="CellBlender Model (text/pickle)")

def menu_func_export(self, context):
    self.layout.operator("cb.export_data_model", text="CellBlender Model (text/pickle)")

def menu_func_import_all(self, context):
    self.layout.operator("cb.import_data_model_all", text="CellBlender Model and Geometry (text/pickle)")

def menu_func_export_all(self, context):
    self.layout.operator("cb.export_data_model_all", text="CellBlender Model and Geometry (text/pickle)")

def menu_func_print(self, context):
    self.layout.operator("cb.print_data_model", text="Print CellBlender Model (text)")


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)
    #bpy.types.INFO_MT_file_export.append(menu_func_export_dm)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_import.remove(menu_func_export_dm)


if __name__ == "__main__": 
    register()

