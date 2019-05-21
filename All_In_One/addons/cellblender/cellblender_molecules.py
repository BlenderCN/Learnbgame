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
This file contains the classes for CellBlender's Molecules.

"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent
import math
import mathutils

# python imports
import re

import cellblender
# from . import cellblender_parameters
from . import parameter_system
from . import cellblender_operators


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)



# Generic helper functions that should go somewhere else!!!

def get_path_to_parent(self_object):
    # Return the Blender class path to the parent object with regard to the Blender Property Tree System
    path_to_self = "bpy.context.scene." + self_object.path_from_id()
    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
    return path_to_parent

def get_parent(self_object):
    # Return the parent Blender object with regard to the Blender Property Tree System
    path_to_parent = get_path_to_parent(self_object)
    parent = eval(path_to_parent)
    return parent



# Molecule Operators:

class MCELL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "mcell.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.add_molecule(context)
        return {'FINISHED'}

class MCELL_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "mcell.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.remove_active_molecule(context)
        self.report({'INFO'}, "Deleted Molecule")
        return {'FINISHED'}




# Callbacks for all Property updates appear to require global (non-member) functions.
# This is circumvented by simply calling the associated member function passed as self:

def check_callback(self, context):
    self.check_callback(context)
    return


def display_callback(self, context):
    self.display_callback(context)
    return

import os



class MCellMoleculeProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    name = StringProperty(
        name="Molecule Name", default="Molecule",
        description="The molecule species name",
        update=check_callback)
    id = IntProperty(name="Molecule ID", default=0)
    type_enum = [
        ('2D', "Surface Molecule", ""),
        ('3D', "Volume Molecule", "")]
    type = EnumProperty(
        items=type_enum, name="Molecule Type",
        default='3D',
        description="Surface molecules are constrained to surfaces/meshes. "
                    "Volume molecules exist in space.")
    diffusion_constant = PointerProperty ( name="Molecule Diffusion Constant", type=parameter_system.Parameter_Reference )
    lr_bar_trigger = BoolProperty("lr_bar_trigger", default=False)
    target_only = BoolProperty(
        name="Target Only",
        description="If selected, molecule will not initiate reactions when "
                    "it runs into other molecules. Can speed up simulations.")

    custom_time_step =   PointerProperty ( name="Molecule Custom Time Step",   type=parameter_system.Parameter_Reference )
    custom_space_step =  PointerProperty ( name="Molecule Custom Space Step",  type=parameter_system.Parameter_Reference )
    # TODO: Add after data model release:  maximum_step_length =  PointerProperty ( name="Maximum Step Length",  type=parameter_system.Parameter_Reference )

    usecolor = BoolProperty ( name="Use this Color", default=True, description='Use Molecule Color instead of Material Color', update=display_callback )
    color = FloatVectorProperty ( name="", min=0.0, max=1.0, default=(0.5,0.5,0.5), subtype='COLOR', description='Molecule Color', update=display_callback )
    alpha = FloatProperty ( name="Alpha", min=0.0, max=1.0, default=1.0, description="Alpha (inverse of transparency)", update=display_callback )
    emit = FloatProperty ( name="Emit", min=0.0, default=1.0, description="Emits Light (brightness)", update=display_callback )
    scale = FloatProperty ( name="Scale", min=0.0001, default=1.0, description="Relative size (scale) for this molecule", update=display_callback )
    previous_scale = FloatProperty ( name="Previous_Scale", min=0.0, default=1.0, description="Previous Scale" )
    #cumulative_scale = FloatProperty ( name="Cumulative_Scale", min=0.0, default=1.0, description="Cumulative Scale" )

    glyph_lib = os.path.join(os.path.dirname(__file__), "glyph_library.blend/Mesh/")
    glyph_enum = [
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere_1', "Sphere_1", ""),
        ('Sphere_2', "Sphere_2", ""),
        ('Torus', "Torus", "")]
    glyph = EnumProperty ( items=glyph_enum, name="", update=display_callback )


    export_viz = bpy.props.BoolProperty(
        default=False, description="If selected, the molecule will be "
                                   "included in the visualization data.")
    status = StringProperty(name="Status")


    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    target_only_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )


    def init_properties ( self, parameter_system ):
        self.name = "Molecule_"+str(self.id)

        helptext = "Molecule Diffusion Constant\n" + \
                   "This molecule diffuses in space with 3D diffusion constant for volume molecules.\n" + \
                   "This molecule diffuses on a surface with 2D diffusion constant for surface molecules.\n" + \
                   "The Diffusion Constant can be zero, in which case the molecule doesn’t move."
        self.diffusion_constant.init_ref   ( parameter_system, "Mol_Diff_Const_Type", user_name="Diffusion Constant",   user_expr="0", user_units="cm^2/sec", user_descr=helptext )

        helptext = "Molecule Custom Time Step\n" + \
                   "This molecule should take timesteps of this length (in seconds).\n" + \
                   "Use either this or CUSTOM_SPACE_STEP, not both."
        self.custom_time_step.init_ref     ( parameter_system, "Mol_Time_Step_Type",  user_name="Custom Time Step",     user_expr="",  user_units="seconds",  user_descr=helptext )

        helptext = "Molecule Custom Space Step\n" + \
                   "This molecule should take steps of this average length (in microns).\n" + \
                   "If you use this directive, do not set CUSTOM_TIME_STEP.\n" + \
                   "Providing a CUSTOM_SPACE_STEP for a molecule overrides a potentially\n" + \
                   "present global SPACE_STEP for this particular molecule."
        self.custom_space_step.init_ref    ( parameter_system, "Mol_Space_Step_Type", user_name="Custom Space Step",    user_expr="",  user_units="microns",  user_descr=helptext )
        # TODO: Add after data model release:  self.maximum_step_length.init_ref  ( parameter_system, "Max_Step_Len_Type",   user_name="Maximum Step Length",  user_expr="",  user_units="microns",  user_descr="Molecule should never step farther than this length during a single timestep. Use with caution (see documentation)." )

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Properties ... not implemented yet!" )


    def build_data_model_from_properties ( self ):
        m = self

        m_dict = {}
        m_dict['data_model_version'] = "DM_2014_10_24_1638"
        m_dict['mol_name'] = m.name
        m_dict['mol_type'] = str(m.type)
        m_dict['diffusion_constant'] = m.diffusion_constant.get_expr()
        m_dict['target_only'] = m.target_only
        m_dict['custom_time_step'] = m.custom_time_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        # TODO: Add after data model release:   m_dict['maximum_step_length'] = m.maximum_step_length.get_expr()
        m_dict['maximum_step_length'] = ""  # TODO: Remove this line after data model release
        m_dict['export_viz'] = m.export_viz

        return m_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )
        # Now convert the updated Data Model into CellBlender Properties
        self.name = dm_dict["mol_name"]
        self.type = dm_dict["mol_type"]
        self.diffusion_constant.set_expr ( dm_dict["diffusion_constant"] )
        self.target_only = dm_dict["target_only"]
        self.custom_time_step.set_expr ( dm_dict["custom_time_step"] )
        self.custom_space_step.set_expr ( dm_dict["custom_space_step"] )
        # TODO: Add after data model release:   self.maximum_step_length.set_expr ( dm_dict["maximum_step_length"] )
        self.export_viz = dm_dict["export_viz"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    # Exporting to an MDL file could be done just like this
    def print_details( self ):
        print ( "Name = " + self.name )

    def draw_props ( self, layout, molecules, parameter_system ):

        helptext = "Molecule Name\nThis is the name used in Reactions and Display"
        parameter_system.draw_prop_with_help ( layout, "Name", self, "name", "name_show_help", self.name_show_help, helptext )

        helptext = "Molecule Type: Either Volume or Surface\n" + \
                   "Volume molecules are placed in and diffuse in 3D spaces." + \
                   "Surface molecules are placed on and diffuse on 2D surfaces."
        parameter_system.draw_prop_with_help ( layout, "Molecule Type", self, "type", "type_show_help", self.type_show_help, helptext )

        self.diffusion_constant.draw(layout,parameter_system)
        #self.lr_bar_trigger = False
        
        lr_bar_display = 0
        if len(self.custom_space_step.get_expr().strip()) > 0:
            # Set lr_bar_display directly
            lr_bar_display = self.custom_space_step.get_value()
        else:
            # Calculate lr_bar_display from diffusion constant and time step
            dc = self.diffusion_constant.get_value()
            ts = bpy.context.scene.mcell.initialization.time_step.get_value()
            if len(self.custom_time_step.get_expr().strip()) > 0:
                ts = self.custom_time_step.get_value()
            lr_bar_display = 2 * math.sqrt ( 4 * dc * ts / math.pi )

        row = layout.row()
        row.label(text="lr_bar: %g"%(lr_bar_display), icon='BLANK1')  # BLANK1 RIGHTARROW_THIN SMALL_TRI_RIGHT_VEC DISCLOSURE_TRI_RIGHT_VEC DRIVER DOT FORWARD LINKED
        #layout.prop ( self, "lr_bar_trigger", icon='NONE', text="lr_bar: " + str(lr_bar_display) )

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_display:
            row.prop(molecules, "show_display", icon='TRIA_RIGHT',
                     text="Display Options", emboss=False)
        else:
            row.prop(molecules, "show_display", icon='TRIA_DOWN',
                     text="Display Options", emboss=False)
            row = box.row()
            row.label ( "Molecule Display Settings" )
            row = box.row()
            col = row.column()
            col.prop ( self, "glyph" )
            col = row.column()
            col.prop ( self, "scale" )
            row = box.row()
            col = row.column()
            mol_mat_name = 'mol_' + self.name + '_mat'
            if False and mol_mat_name in bpy.data.materials.keys():
                # This would control the actual Blender material property directly
                col.prop ( bpy.data.materials[mol_mat_name], "diffuse_color" )
                col = row.column()
                col.prop ( bpy.data.materials[mol_mat_name], "emit" )
            else:
                # This controls the molecule property which changes the Blender property via callback
                # But changing the color via the Materials interface doesn't change these values
                col.prop ( self, "color" )
                col = row.column()
                col.prop ( self, "emit" )
            #col = row.column()
            #col.prop ( self, "usecolor" )
        
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_advanced:
            row.prop(molecules, "show_advanced", icon='TRIA_RIGHT',
                     text="Advanced Options", emboss=False)
        else:
            row.prop(molecules, "show_advanced", icon='TRIA_DOWN',
                     text="Advanced Options", emboss=False)
            # row = box.row()
            # row.prop(self, "target_only")
            parameter_system.draw_prop_with_help ( box, "Target Only", self, "target_only", "target_only_show_help", self.target_only_show_help, 
                "Target Only - This molecule will not initiate reactions when\n" +
                "it runs into other molecules. This setting can speed up simulations\n" +
                "when applied to a molecule at high concentrations that reacts with\n" +
                "a molecule at low concentrations (it is more efficient for the\n" +
                "low-concentration molecule to trigger the reactions). This directive\n" +
                "does not affect unimolecular reactions." )
            self.custom_time_step.draw(box,parameter_system)
            self.custom_space_step.draw(box,parameter_system)


    def check_callback(self, context):
        """Allow the parent molecule list (MCellMoleculesListProperty) to do the checking"""
        get_parent(self).check(context)
        return


    def display_callback(self, context):
        """One of the display items has changed for this molecule"""
        print ( "Display for molecule \"" + self.name + "\" changed to: " + str(self.glyph) + ", color=" + str(self.color) + ", emit=" + str(self.emit) + ", scale=" + str(self.scale) )
        mol_name = 'mol_' + self.name
        mol_shape_name = mol_name + '_shape'
        if mol_shape_name in bpy.data.objects:
            if self.scale != self.previous_scale:
                # Scale by the ratio of current scale to previous scale
                bpy.data.objects[mol_shape_name].scale *= (self.scale / self.previous_scale)
                self.previous_scale = self.scale
                
            

        mol_mat_name = 'mol_' + self.name + '_mat'
        if mol_mat_name in bpy.data.materials.keys():
            if bpy.data.materials[mol_mat_name].diffuse_color != self.color:
                bpy.data.materials[mol_mat_name].diffuse_color = self.color
            if bpy.data.materials[mol_mat_name].emit != self.emit:
                bpy.data.materials[mol_mat_name].emit = self.emit


        # Refresh the scene
        self.set_mol_glyph ( context )
        cellblender_operators.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class.
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return



    def set_mol_glyph (self, context):
        # Use exact code from MCELL_OT_set_molecule_glyph(bpy.types.Operator).execute
        # Except added a test to see if the molecule exists first!!
        
        mol_name = 'mol_' + self.name
        if mol_name in bpy.data.objects:

            # First set up the selected and active molecules

            mol_obj = bpy.data.objects['mol_' + self.name]     # Is this used before being resest below?
            mol_shape_name = 'mol_' + self.name + '_shape'

            bpy.ops.object.select_all(action='DESELECT')
            context.scene.objects[mol_shape_name].hide_select = False
            context.scene.objects[mol_shape_name].select = True
            context.scene.objects.active = bpy.data.objects[mol_shape_name]


            # Exact code starts here (allow it to duplicate some previous code for now):

            mcell = context.scene.mcell
            meshes = bpy.data.meshes
            mcell.molecule_glyphs.status = ""
            select_objs = context.selected_objects
            if (len(select_objs) != 1):
                mcell.molecule_glyphs.status = "Select One Molecule"
                return
            if (select_objs[0].type != 'MESH'):
                mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
                return

            mol_obj = select_objs[0]
            mol_shape_name = mol_obj.name

            # glyph_name = mcell.molecule_glyphs.glyph
            glyph_name = str(self.glyph)

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
            mol_obj.hide_select = True
            meshes.remove(meshes[mol_shape_name])

            new_mol_mesh.name = mol_shape_name
            new_mol_mesh.materials.append(mol_mat)

        return




    def testing_set_mol_glyph (self, context):

        ###########################################
        ###########################################
        # return
        ###########################################
        ###########################################
        
        mcell = context.scene.mcell
        meshes = bpy.data.meshes
        mcell.molecule_glyphs.status = ""
        #select_objs = context.selected_objects
        #if len(select_objs) == -123:
        #    if (len(select_objs) != 1):
        #        mcell.molecule_glyphs.status = "Select One Molecule"
        #        return {'FINISHED'}
        #    if (select_objs[0].type != 'MESH'):
        #        mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
        #        return {'FINISHED'}

        #mol_obj = select_objs[0]
        #mol_shape_name = mol_obj.name

        # Try to deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        mol_obj = bpy.data.objects['mol_' + self.name]
        mol_shape_name = 'mol_' + self.name + '_shape'
        print ( "Try to select " + mol_shape_name + " from bpy.data.objects["+self.name+"]" )
        context.scene.objects.active = bpy.data.objects[mol_shape_name]

        glyph_name = str(self.glyph)

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

        print ( "New Glyph Name = " + new_glyph_name )

        if (bpy.app.version[0] > 2) or ( (bpy.app.version[0]==2) and (bpy.app.version[1] > 71) ):
          bpy.ops.wm.link(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)
        else:
          bpy.ops.wm.link_append(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)

        mol_mat = None
        if len(mol_obj.material_slots) > 0:
          mol_mat = mol_obj.material_slots[0].material

        new_mol_mesh = meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        ### causes a problem?  meshes.remove(meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        if mol_mat != None:
            new_mol_mesh.materials.append(mol_mat)
        print ( "Done setting molecule glyph" )






class MCell_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "CellBlender - Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function for the instance being drawn in this panel
        context.scene.mcell.molecules.draw_panel ( context, self )


class MCellMoleculesListProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    molecule_list = CollectionProperty(type=MCellMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def init_properties ( self, parameter_system ):
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.init_properties(parameter_system)

    def remove_properties ( self, context ):
        print ( "Removing all Molecule List Properties..." )
        for item in self.molecule_list:
            item.remove_properties(context)
        self.molecule_list.clear()
        self.active_mol_index = 0
        self.next_id = 1
        print ( "Done removing all Molecule List Properties." )
        
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.id = self.allocate_available_id()
        new_mol.init_properties(context.scene.mcell.parameter_system)
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        self.molecule_list.remove ( self.active_mol_index )
        self.active_mol_index -= 1
        if self.active_mol_index < 0:
            self.active_mol_index = 0
        if self.molecule_list:
            self.check(context)

    def build_data_model_from_properties ( self, context ):
        print ( "Molecule List building Data Model" )
        mol_dm = {}
        mol_dm['data_model_version'] = "DM_2014_10_24_1638"
        mol_list = []
        for m in self.molecule_list:
            mol_list.append ( m.build_data_model_from_properties() )
        mol_dm['molecule_list'] = mol_list
        return mol_dm

    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculesListProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculesListProperty data model to current version." )
            return None

        if "molecule_list" in dm:
            for item in dm["molecule_list"]:
                if MCellMoleculeProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculesListProperty data model to current version." )

        # Now convert the Data Model into CellBlender Properties

        # Start by removing all molecules from the list
        while len(self.molecule_list) > 0:
            self.remove_active_molecule ( context )

        # Add molecules from the data model
        if "molecule_list" in dm:
            for m in dm["molecule_list"]:
                self.add_molecule(context)
                self.molecule_list[self.active_mol_index].build_properties_from_data_model(context,m)

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def check ( self, context ):
        """Checks for duplicate or illegal molecule name"""
        # Note: Some of the list-oriented functionality is appropriate here (since this
        #        is a list), but some of the molecule-specific checks (like name legality)
        #        could be handled by the the molecules themselves. They're left here for now.

        mol = self.molecule_list[self.active_mol_index]

        status = ""

        # Check for duplicate molecule name
        mol_keys = self.molecule_list.keys()
        if mol_keys.count(mol.name) > 1:
            status = "Duplicate molecule: %s" % (mol.name)

        # Check for illegal names (Starts with a letter. No special characters.)
        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(mol_filter, mol.name)
        if m is None:
            status = "Molecule name error: %s" % (mol.name)

        mol.status = status

        return


    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 1 when there are no more molecules
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def draw_layout ( self, context, layout ):
        """ Draw the molecule "panel" within the layout """
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            col = row.column()
            col.template_list("MCell_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=2)
            col = row.column(align=True)
            col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
            col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                # The self is needed to pass the "advanced" flag to the molecule
                mol.draw_props ( layout, self, mcell.parameter_system )


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

