import bpy
import os
import sys
import io
import subprocess
import json
import sys
import cellblender
from cellblender import cellblender_properties, cellblender_operators
from collections import defaultdict
#from . import net

# We use per module class registration/unregistration
filePath = ''
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

def accessFile(filePath,parentOperator):
    if not hasattr(accessFile, 'info'):
        try:
            filePointer = open(filePath + '.json','r')
            accessFile.info = json.load(filePointer)
        except FileNotFoundError:
            if filePath.endswith('xml'):
                parentOperator.report({'ERROR_INVALID_INPUT'},'The file you selected could not be imported. Check if libsbml is correctly installed and whether you selected a valid SBML file')
            else:
                parentOperator.report({'ERROR_INVALID_INPUT'},'The file you selected could not be imported.')
            accessFile.info=defaultdict(list)
    return accessFile.info


class EXTERNAL_OT_parameter_add(bpy.types.Operator):
    bl_idname = "external.parameter_add"
    bl_label = "Add Parameter"
    bl_description = "Add imported parameters to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        #filePointer= open(filePath + '.json','r')
        #jfile = json.load(filePointer) 
        jfile = accessFile(filePath,self)       
        par_list = jfile['par_list']
        index = -1
        for key in par_list:
            index += 1

            par_name = str(key['name'])
            par_value = str(key['value'])
            par_unit = str(key['unit'])
            par_type = str(key['type'])

            mcell.parameter_system.add_general_parameter_with_values( par_name, par_value, par_unit, par_type )
            #print ( "Adding parameter \"" + str(par_name) + "\"  =  \"" + str(par_value) + "\"  (" + str(par_unit) + ")" )
 
        return {'FINISHED'}


class EXTERNAL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "external.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add imported molecules from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        #filePointer= open(filePath + '.json','r')
        #json.load(filePointer)        

        jfile = accessFile(filePath,self)
        mol_list = jfile['mol_list']
        index = -1
        for key in mol_list:
            index += 1
            mcell.molecules.molecule_list.add()
            mcell.molecules.active_mol_index = index
            molecule = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]
            #molecule.set_defaults()
            molecule.init_properties(ps)

            molecule.name = str(key['name'])
            molecule.type = str(key['type'])
            #molecule.diffusion_constant.expression = str(key['dif'])
            #molecule.diffusion_constant.param_data.label = "Diffusion Constant"
            molecule.diffusion_constant.set_expr ( key['dif'], ps.panel_parameter_list )
            
            #print ( "Adding molecule " + str(molecule.name) )

        return {'FINISHED'}


class EXTERNAL_OT_reaction_add(bpy.types.Operator):
    bl_idname = "external.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add imported reactions from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell

        #filePointer= open(filePath + '.json','r')
        #jfile = json.load(filePointer) 
        ps = mcell.parameter_system
        jfile = accessFile(filePath,self)       
        rxn_list = jfile['rxn_list']        
        index = -1
        for key in rxn_list:
            index += 1
            mcell.reactions.reaction_list.add()
            mcell.reactions.active_rxn_index = index
            reaction = mcell.reactions.reaction_list[
                mcell.reactions.active_rxn_index]
            #reaction.set_defaults()
            reaction.init_properties(ps)

            reaction.reactants = str(key['reactants'])
            reaction.products = str(key['products'])
            #reaction.fwd_rate.expression = str(key['fwd_rate'])
            if 'rxn_name' in key:
                reaction.rxn_name = str(key['rxn_name'])                
            #reaction.fwd_rate.param_data.label = "Forward Rate"
            reaction.fwd_rate.set_expr ( key['fwd_rate'], ps.panel_parameter_list )

            #print ( "Adding reaction  " + str(reaction.reactants) + "  ->  " + str(reaction.products))

        return {'FINISHED'}


class EXTERNAL_OT_release_site_add(bpy.types.Operator):
    bl_idname = "external.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add imported release sites from BNG-generated networxn_list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        #filePointer= open(filePath + '.json','r')
        #jfile = json.load(filePointer) 
        jfile = accessFile(filePath,self)        
        ps = mcell.parameter_system
        rel_list = jfile['rel_list']     
        index = -1
        for key in rel_list:
            index += 1
            mcell.release_sites.mol_release_list.add()
            mcell.release_sites.active_release_index = index
            release_site = mcell.release_sites.mol_release_list[
                mcell.release_sites.active_release_index]
            #release_site.set_defaults()
            release_site.init_properties(ps)
            
            release_site.name = str(key['name'])
            release_site.molecule = str(key['molecule'])
            release_site.shape = str(key['shape'])
            release_site.orient = str(key['orient'])
            release_site.object_expr = str(key['object_expr'])
            release_site.quantity_type = str(key['quantity_type'])
            release_site.quantity.set_expr ( str(key['quantity_expr']), ps.panel_parameter_list )

            #release_site.quantity.expression = str(key['quantity_expr'])
            if 'release_pattern' in key:
                release_site.pattern = str(key['release_pattern'])
            # Is this check even needed?
            #cellblender_operators.check_release_molecule(context)
            #print ( "Adding release site " + str(release_site.name) )

        return {'FINISHED'}


class EXTERNAL_OT_reaction_output_add(bpy.types.Operator):
    bl_idname = "external.reaction_output_add"
    bl_label = "Add Reaction Output"
    bl_description = "Add MCell observables based on assigmnent rule information"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        #filePointer= open(filePath + '.json','r')
        #jfile = json.load(filePointer) 
        jfile = accessFile(filePath,self)     
        ps = mcell.parameter_system
        obs_list = jfile['obs_list']     
        index = -1
        import copy
        for index,key in enumerate(obs_list):
            strBuffer = []
            #mcell.rxn_output.complex_rxn_output_list.append({'name':key['name'],'value':key['value']})
            
            for element in key['value']:
                if element == ['0']:
                    continue
                tmp = copy.copy(element)
                tmp[-1] = 'COUNT[{0},WORLD]'.format(element[-1])
                strBuffer.append(' * '.join(tmp))


            mcell.rxn_output.complex_rxn_output_list.add()
            mcell.rxn_output.temp_index = index
            rxn_output_instance = mcell.rxn_output.complex_rxn_output_list[
                mcell.rxn_output.temp_index]
            rxn_output_instance.molecule_name = '+'.join(strBuffer)
            rxn_output_instance.name = key['name']

            '''    
            index += 1
            mcell.rxn_output.rxn_output_list.add()
            mcell.rxn_output.active_rxn_output_index = index
            rxn_output = mcell.rxn_output.rxn_output_list[
                mcell.rxn_output.active_rxn_output_index]
            #release_site.set_defaults()
            rxn_output.init_properties(ps)
            '''

            #print ( "Adding reaction output " + str(key['name']))

        return {'FINISHED'}
