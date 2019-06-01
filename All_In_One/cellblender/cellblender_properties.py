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


# ############
#
#  Property Groups
#   CellBlender consists primarily of Property Groups which are the
#   classes which are templates for objects.
#
#   Each Property Group must implement the following functions:
#
#     init_properties - Deletes old and Creates a new object including children
#     build_data_model_from_properties - Builds a Data Model Dictionary from the existing properties
#     @staticmethod upgrade_data_model - Produces a current data model from an older version
#     build_properties_from_data_model - Calls init_properties and builds properties from a data model
#     check_properties_after_building - Used to resolve dependencies
#     
#
# ############


# <pep8 compliant>


"""
This script contains the custom properties used in CellBlender.
"""
# blender imports
import bpy
from . import cellblender_operators
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, PointerProperty, StringProperty, BoolVectorProperty

from bpy.app.handlers import persistent

from . import cellblender_molecules
from . import parameter_system
from . import data_model

# python imports
import os
from multiprocessing import cpu_count

from cellblender.utils import project_files_path

# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#Custom Properties

class MCellStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec = bpy.props.FloatVectorProperty(name="Float Vector")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell Float Vector Property... no collections to remove. Is there anything special do to for Vectors?" )
        pass


class MCellReactionProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="The Reaction")
    rxn_name = StringProperty(
        name="Reaction Name",
        description="The name of the reaction. "
                    "Can be used in Reaction Output.",
        update=cellblender_operators.check_reaction)
    reactants = StringProperty(
        name="Reactants", 
        description="Specify 1-3 reactants separated by a + symbol. "
                    "Optional: end with @ surface class. Ex: a; + b; @ sc;",
        update=cellblender_operators.check_reaction)
    products = StringProperty(
        name="Products",
        description="Specify zero(NULL) or more products separated by a + "
                    "symbol.",
        update=cellblender_operators.check_reaction)
    type_enum = [
        ('irreversible', "->", ""),
        ('reversible', "<->", "")]
    type = EnumProperty(
        items=type_enum, name="Reaction Type",
        description="A unidirectional/irreversible(->) reaction or a "
                    "bidirectional/reversible(<->) reaction.",
        update=cellblender_operators.check_reaction)
    variable_rate_switch = BoolProperty(
        name="Enable Variable Rate Constant",
        description="If set, use a variable rate constant defined by a two "
                    "column file (col1=time, col2=rate).",
        default=False, update=cellblender_operators.check_reaction)
    variable_rate = StringProperty(
        name="Variable Rate", subtype='FILE_PATH', default="")
    variable_rate_valid = BoolProperty(name="Variable Rate Valid",
        default=False, update=cellblender_operators.check_reaction)


    fwd_rate = PointerProperty ( name="Forward Rate", type=parameter_system.Parameter_Reference )
    bkwd_rate = PointerProperty ( name="Backward Rate", type=parameter_system.Parameter_Reference )


    reactants_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rxn_type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    products_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    variable_rate_switch_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rxn_name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def init_properties ( self, parameter_system ):
        self.name = "The_Reaction"
        self.rxn_name = ""
        self.reactants = ""
        self.products = ""
        self.type = 'irreversible'
        self.variable_rate_switch = False
        self.variable_rate = ""
        self.variable_rate_valid = False
        
        helptext = "Forward Rate\n" + \
                   "The units for the reaction rate for uni- and bimolecular reactions is:\n" + \
                   "  [1/s] for unimolecular reactions,\n" + \
                   "  [1/(M * s)] for bimolecular reactions between either\n" + \
                   "      two volume molecules or a volume molecule and a surface molecule,\n" + \
                   "  [um^2 / (N * s)] for bimolecular reactions between two surface molecules."
        self.fwd_rate.init_ref   ( parameter_system, "FW_Rate_Type", user_name="Forward Rate",  user_expr="0", user_units="", user_descr=helptext )
       
        helptext = "Backward Rate\n" + \
                  "The units for the reaction rate for uni- and bimolecular reactions is:\n" + \
                  "  [1/s] for unimolecular reactions,\n" + \
                  "  [1/(M * s)] for bimolecular reactions between either\n" + \
                  "      two volume molecules or a volume molecule and a surface molecule,\n" + \
                  "  [um^2 / (N * s)] for bimolecular reactions between two surface molecules."
        self.bkwd_rate.init_ref  ( parameter_system, "BW_Rate_Type", user_name="Backward Rate", user_expr="",  user_units="s", user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Properties... no collections to remove." )

    status = StringProperty(name="Status")


    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2014_10_24_1638"
        r_dict['name'] = r.name
        r_dict['rxn_name'] = r.rxn_name
        r_dict['reactants'] = r.reactants
        r_dict['products'] = r.products
        r_dict['rxn_type'] = r.type
        r_dict['variable_rate_switch'] = r.variable_rate_switch
        r_dict['variable_rate'] = r.variable_rate
        r_dict['variable_rate_valid'] = r.variable_rate_valid
        r_dict['fwd_rate'] = r.fwd_rate.get_expr()
        r_dict['bkwd_rate'] = r.bkwd_rate.get_expr()
        variable_rate_text = ""
        if r.type == 'irreversible':
            # Check if a variable rate constant file is specified
            if r.variable_rate_switch and r.variable_rate_valid:
                variable_rate_text = bpy.data.texts[r.variable_rate].as_string()
        r_dict['variable_rate_text'] = variable_rate_text
        return r_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionProperty data model to current version." )
        self.name = dm_dict["name"]
        self.rxn_name = dm_dict["rxn_name"]
        self.reactants = dm_dict["reactants"]
        self.products = dm_dict["products"]
        self.type = dm_dict["rxn_type"]
        self.variable_rate_switch = dm_dict["variable_rate_switch"]
        self.variable_rate = dm_dict["variable_rate"]
        self.variable_rate_valid = dm_dict["variable_rate_valid"]
        self.fwd_rate.set_expr ( dm_dict["fwd_rate"] )
        self.bkwd_rate.set_expr ( dm_dict["bkwd_rate"] )
        # TODO: The following logic doesn't seem right ... we might want to check it!!
        if self.type == 'irreversible':
            # Check if a variable rate constant file is specified
            if self.variable_rate_switch and self.variable_rate_valid:
                variable_rate_text = bpy.data.texts[self.variable_rate].as_string()
                self.store_variable_rate_text ( context, self.variable_rate, dm_dict["variable_rate_text"] )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def store_variable_rate_text ( self, context, text_name, rate_string ):
        """ Create variable rate constant text object from text string.

        Create a text object from an existing text string that represents the
        variable rate constant. This ensures that the variable rate constant is
        actually stored in the blend. Although, ultimately, this text object will
        be exported as another text file in the project directory when the MDLs are
        exported so it can be used by MCell."""
        print ( "store_variable_rate_text ( " + text_name + ", " + rate_string + " )" )
        texts = bpy.data.texts
        # Overwrite existing text objects.
        # XXX: Add warning.
        if text_name in texts:
            texts.remove(texts[text_name])
            print ( "Found " + text_name + ", and removed from texts" )

        # Create the text object from the text string
        try:
            text_object = texts.new(text_name)
            # Should add in some simple error checking
            text_object.write(rate_string)
            self.variable_rate_valid = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            self.variable_rate_valid = False
        

    def load_variable_rate_file ( self, context, filepath ):
        # Create the text object from the text file
        self.variable_rate = os.path.basename(filepath)
        try:
            with open(filepath, "r") as rate_file:
                rate_string = rate_file.read()
                self.store_variable_rate_text ( context, self.variable_rate, rate_string )
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            self.variable_rate_valid = False


    def write_to_mdl_file ( self, context, out_file, filedir ):
        out_file.write("  %s " % (self.name))

        ps = context.scene.mcell.parameter_system

        if self.type == 'irreversible':
            # Use a variable rate constant file if specified
            if self.variable_rate_switch and self.variable_rate_valid:
                variable_rate_name = self.variable_rate
                out_file.write('["%s"]' % (variable_rate_name))
                variable_rate_text = bpy.data.texts[variable_rate_name]
                variable_out_filename = os.path.join(
                    filedir, variable_rate_name)
                with open(variable_out_filename, "w", encoding="utf8",
                          newline="\n") as variable_out_file:
                    variable_out_file.write(variable_rate_text.as_string())
            # Use a single-value rate constant
            else:
                out_file.write("[%s]" % (self.fwd_rate.get_as_string_or_value(
                               ps.panel_parameter_list,ps.export_as_expressions)))    
        else:
            out_file.write(
                "[>%s, <%s]" % (self.fwd_rate.get_as_string_or_value(
                ps.panel_parameter_list, ps.export_as_expressions),
                self.bkwd_rate.get_as_string_or_value(ps.panel_parameter_list,
                ps.export_as_expressions)))

        if self.rxn_name:
            out_file.write(" : %s\n" % (self.rxn_name))
        else:
            out_file.write("\n")


class MCellMoleculeReleaseProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Site Name", default="Release_Site",
        description="The name of the release site",
        update=cellblender_operators.check_release_site)
    molecule = StringProperty(
        name="Molecule",
        description="The molecule to release",
        update=cellblender_operators.check_release_site)
    shape_enum = [
        ('CUBIC', 'Cubic', ''),
        ('SPHERICAL', 'Spherical', ''),
        ('SPHERICAL_SHELL', 'Spherical Shell', ''),
        #('LIST', 'List', ''),
        ('OBJECT', 'Object/Region', '')]
    shape = EnumProperty(
        items=shape_enum, name="Release Shape",
        description="Release in the specified shape. Surface molecules can "
                    "only use Object/Region.",
                    update=cellblender_operators.check_release_site)
    orient_enum = [
        ('\'', "Top Front", ""),
        (',', "Top Back", ""),
        (';', "Mixed", "")]
    orient = bpy.props.EnumProperty(
        items=orient_enum, name="Initial Orientation",
        description="Release surface molecules with the specified initial "
                    "orientation.")
    object_expr = StringProperty(
        name="Object/Region",
        description="Release in/on the specified object/region.",
        update=cellblender_operators.check_release_site)
        
    #location = bpy.props.FloatVectorProperty(
    #    name="Location", precision=4,
    #    description="The center of the release site specified by XYZ "
    #                "coordinates")

    location_x = PointerProperty ( name="Relese Loc X", type=parameter_system.Parameter_Reference )
    location_y = PointerProperty ( name="Relese Loc Y", type=parameter_system.Parameter_Reference )
    location_z = PointerProperty ( name="Relese Loc Z", type=parameter_system.Parameter_Reference )

    diameter = PointerProperty ( name="Site Diameter", type=parameter_system.Parameter_Reference )
    probability = PointerProperty ( name="Release Probability", type=parameter_system.Parameter_Reference )

    quantity_type_enum = [
        ('NUMBER_TO_RELEASE', "Constant Number", ""),
        ('GAUSSIAN_RELEASE_NUMBER', "Gaussian Number", ""),
        ('DENSITY', "Concentration/Density", "")]
    quantity_type = EnumProperty(items=quantity_type_enum,
                                 name="Quantity Type")

    quantity = PointerProperty ( name="Quantity to Release", type=parameter_system.Parameter_Reference )
    stddev = PointerProperty ( name="Standard Deviation", type=parameter_system.Parameter_Reference )

    pattern = StringProperty(
        name="Release Pattern",
        description="Use the named release pattern. "
                    "If blank, release molecules at start of simulation.")
    status = StringProperty(name="Status")

    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    shape_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    object_expr_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    orient_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    quantity_type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    mol_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rel_pattern_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )



    def init_properties ( self, parameter_system ):
        self.name = "Release_Site"
        self.molecule = ""
        self.shape = 'CUBIC'
        self.orient = '\''
        self.object_expr = ""
       
        self.location_x.init_ref  ( parameter_system, "Rel_Loc_Type_X",  user_name="Release Location X",  user_expr="0", user_units="", user_descr="The center of the release site's X coordinate.\nOnly used for geometrical shapes." )
        self.location_y.init_ref  ( parameter_system, "Rel_Loc_Type_Y",  user_name="Release Location Y",  user_expr="0", user_units="", user_descr="The center of the release site's Y coordinate\nOnly used for geometrical shapes." )
        self.location_z.init_ref  ( parameter_system, "Rel_Loc_Type_Z",  user_name="Release Location Z",  user_expr="0", user_units="", user_descr="The center of the release site's Z coordinate\nOnly used for geometrical shapes." )
        self.diameter.init_ref    ( parameter_system, "Diam_Type",       user_name="Site Diameter",       user_expr="0", user_units="", user_descr="Release molecules uniformly within a diameter d.\nNot used for releases on regions." )
        self.probability.init_ref ( parameter_system, "Rel_Prob_Type",   user_name="Release Probability", user_expr="1", user_units="", user_descr="This release does not have to occur every time, but rather with probability p.\nEither the whole release occurs or none of it does;\nthe probability does not apply molecule-by-molecule.\np must be in the interval [0;1]." )

        helptext = "Quantity of Molecules to release at this site." + \
                "\n" + \
                "When Quantity Type is Constant Number:\n" + \
                "  Release n molecules. For releases on regions, n can be negative, and\n" + \
                "  the release will then remove molecules of that type from the region. To\n" + \
                "  remove all molecules of a type, just make n large and negative. It is\n" + \
                "  unwise to both add and remove molecules on the same timestep—the\n" + \
                "  order of addition and removal is not defined in that case. This directive\n" + \
                "  is not used for the LIST shape, as every molecule is specified.\n" + \
                "  Concentration units: molar. Density units: molecules per square micron\n" + \
                "\n" + \
                "When Quantity Type is Gaussian Number:\n" + \
                "  Defines the mean of the Quantity of molecules to be released.\n" + \
                "\n" + \
                "When Quantity Type is Concentration / Density:\n" + \
                "  Release molecules at concentration c molar for volumes and d\n" + \
                "  molecules per square micron for surfaces. Neither can be used\n" + \
                "  for the LIST shape; DENSITY is only valid for regions."
        self.quantity.init_ref    ( parameter_system, "Rel_Quant_Type",  user_name="Quantity to Release", user_expr="",  user_units="", user_descr=helptext )

        helptext = "Standard Deviation of number to release\nwhen Quantity Type is Gaussian Number"
        self.stddev.init_ref      ( parameter_system, "Rel_StdDev_Type", user_name="Standard Deviation",  user_expr="0", user_units="", user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Release Properties... no collections to remove." )

    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2014_10_24_1638"
        r_dict['name'] = r.name
        r_dict['molecule'] = r.molecule
        r_dict['shape'] = r.shape
        r_dict['orient'] = r.orient
        r_dict['object_expr'] = r.object_expr
        r_dict['location_x'] = r.location_x.get_expr()
        r_dict['location_y'] = r.location_y.get_expr()
        r_dict['location_z'] = r.location_z.get_expr()
        r_dict['site_diameter'] = r.diameter.get_expr()
        r_dict['release_probability'] = r.probability.get_expr()
        r_dict['quantity_type'] = str(r.quantity_type)
        r_dict['quantity'] = r.quantity.get_expr()
        r_dict['stddev'] = r.stddev.get_expr()
        r_dict['pattern'] = str(r.pattern)
        return r_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeReleaseProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleaseProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):

        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleaseProperty data model to current version." )

        self.name = dm_dict["name"]
        self.molecule = dm_dict["molecule"]
        self.shape = dm_dict["shape"]
        self.orient = dm_dict["orient"]
        self.object_expr = dm_dict["object_expr"]
        self.location_x.set_expr ( dm_dict["location_x"] )
        self.location_y.set_expr ( dm_dict["location_y"] )
        self.location_z.set_expr ( dm_dict["location_z"] )
        self.diameter.set_expr ( dm_dict["site_diameter"] )
        self.probability.set_expr ( dm_dict["release_probability"] )
        self.quantity_type = dm_dict["quantity_type"]
        self.quantity.set_expr ( dm_dict["quantity"] )
        self.stddev.set_expr ( dm_dict["stddev"] )
        self.pattern = dm_dict["pattern"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



class MCellReleasePatternProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Pattern Name", default="Release_Pattern",
        description="The name of the release site",
        update=cellblender_operators.check_release_pattern_name)

    delay            = PointerProperty ( name="Release Pattern Delay", type=parameter_system.Parameter_Reference )
    release_interval = PointerProperty ( name="Relese Interval",       type=parameter_system.Parameter_Reference )
    train_duration   = PointerProperty ( name="Train Duration",        type=parameter_system.Parameter_Reference )
    train_interval   = PointerProperty ( name="Train Interval",        type=parameter_system.Parameter_Reference )
    number_of_trains = PointerProperty ( name="Number of Trains",      type=parameter_system.Parameter_Reference )

    status = StringProperty(name="Status")

    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def init_properties ( self, parameter_system ):
        self.name = "Release_Pattern"
        helptext = ""
        self.delay.init_ref            ( parameter_system, "Rel_Delay_Type", user_name="Release Pattern Delay", user_expr="0",     user_units="s", user_descr="The time at which the release pattern will start.\nDefault is at time zero." )
        self.release_interval.init_ref ( parameter_system, "Rel_Int_Type",   user_name="Relese Interval",       user_expr="",      user_units="s", user_descr="During a train of releases, release molecules after every t seconds.\nDefault is release only once (t is infinite)." )
        self.train_duration.init_ref   ( parameter_system, "Tr_Dur_Type",    user_name="Train Duration",        user_expr="",      user_units="s", user_descr="The duration of the train before turning off.\nDefault is to never turn off." )
        self.train_interval.init_ref   ( parameter_system, "Tr_Int_Type",    user_name="Train Interval",        user_expr="",      user_units="s", user_descr="A new train happens every interval.\nDefault is no new trains.\nThe train interval must not be shorter than the train duration." )
        self.number_of_trains.init_ref ( parameter_system, "NTrains_Type",   user_name="Number of Trains",      user_expr="1",     user_units="",  user_descr="Repeat the release process for this number of trains of releases.\nDefault is one train.", user_int=True )

    def remove_properties ( self, context ):
        print ( "Removing all Release Pattern Properties... no collections to remove." )


    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2014_10_24_1638"
        r_dict['name'] = r.name
        r_dict['delay'] = r.delay.get_expr()
        r_dict['release_interval'] = r.release_interval.get_expr()
        r_dict['train_duration'] = r.train_duration.get_expr()
        r_dict['train_interval'] = r.train_interval.get_expr()
        r_dict['number_of_trains'] = r.number_of_trains.get_expr()
        return r_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReleasePatternProperty Data Model" )

        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):

        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternProperty data model to current version." )

        self.name = dm_dict["name"]
        self.delay.set_expr ( dm_dict["delay"] )
        self.release_interval.set_expr ( dm_dict["release_interval"] )
        self.train_duration.set_expr ( dm_dict["train_duration"] )
        self.train_interval.set_expr ( dm_dict["train_interval"] )
        self.number_of_trains.set_expr ( dm_dict["number_of_trains"] )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



class MCellSurfaceClassPropertiesProperty(bpy.types.PropertyGroup):

    """ This is where properties for a given surface class are stored.

    All of the properties here ultimately get converted into something like the
    following: ABSORPTIVE = Molecule' or REFLECTIVE = Molecule;
    Each instance is only one set of properties for a surface class that may
    have many sets of properties.

    """

    name = StringProperty(name="Molecule", default="Molecule")
    molecule = StringProperty(
        name="Molecule Name",
        description="The molecule that is affected by the surface class",
        update=cellblender_operators.check_surf_class_props)
    surf_class_orient_enum = [
        ('\'', "Top/Front", ""),
        (',', "Bottom/Back", ""),
        (';', "Ignore", "")]
    surf_class_orient = EnumProperty(
        items=surf_class_orient_enum, name="Orientation",
        description="Volume molecules affected at front or back of a surface. "
                    "Surface molecules affected by orientation at border.",
        update=cellblender_operators.check_surf_class_props)
    surf_class_type_enum = [
        ('ABSORPTIVE', "Absorptive", ""),
        ('TRANSPARENT', "Transparent", ""),
        ('REFLECTIVE', "Reflective", ""),
        ('CLAMP_CONCENTRATION', "Clamp Concentration", "")]
    surf_class_type = EnumProperty(
        items=surf_class_type_enum, name="Type",
        description="Molecules are destroyed by absorptive surfaces, pass "
                    "through transparent, and \"bounce\" off of reflective.",
        update=cellblender_operators.check_surf_class_props)
    clamp_value = FloatProperty(name="Value", precision=4, min=0.0)
    clamp_value_str = StringProperty(
        name="Value", description="Concentration Units: Molar",
        update=cellblender_operators.update_clamp_value)
    status = StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        sc = self
        sc_dict = {}
        sc_dict['data_model_version'] = "DM_2014_10_24_1638"
        sc_dict['name'] = sc.name
        sc_dict['molecule'] = sc.molecule
        sc_dict['surf_class_orient'] = str(sc.surf_class_orient)
        sc_dict['surf_class_type'] = str(sc.surf_class_type)
        sc_dict['clamp_value'] = str(sc.clamp_value_str)
        return sc_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassPropertiesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )

        self.name = dm["name"]
        self.molecule = dm["molecule"]
        self.surf_class_orient = dm["surf_class_orient"]
        self.surf_class_type = dm["surf_class_type"]
        self.clamp_value_str = dm["clamp_value"]
        self.clamp_value = float(self.clamp_value_str)

    def init_properties ( self, parameter_system ):
        self.name = "Molecule"
        self.molecule = ""
        self.surf_class_orient = '\''
        self.surf_class_type = 'REFLECTIVE'
        self.clamp_value_str = "0.0"
        self.clamp_value = float(self.clamp_value_str)

    def remove_properties ( self, context ):
        print ( "Removing all Surface Class Properties... no collections to remove." )


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )




class MCellSurfaceClassesProperty(bpy.types.PropertyGroup):
    """ Stores the surface class name and a list of its properties. """

    name = StringProperty(
        name="Surface Class Name", default="Surface_Class",
        description="This name can be selected in Assign Surface Classes.",
        update=cellblender_operators.check_surface_class)
    surf_class_props_list = CollectionProperty(
        type=MCellSurfaceClassPropertiesProperty, name="Surface Classes List")
    active_surf_class_props_index = IntProperty(
        name="Active Surface Class Index", default=0)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Surface Class Properties..." )
        for item in self.surf_class_props_list:
            item.remove_properties(context)
        self.surf_class_props_list.clear()
        self.active_surf_class_props_index = 0
        print ( "Done removing all Surface Class Properties." )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Classes building Data Model" )
        sc_dm = {}
        sc_dm['data_model_version'] = "DM_2014_10_24_1638"
        sc_dm['name'] = self.name
        sc_list = []
        for sc in self.surf_class_props_list:
            sc_list.append ( sc.build_data_model_from_properties(context) )
        sc_dm['surface_class_prop_list'] = sc_list
        return sc_dm



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesProperty data model to current version." )
            return None

        if "surface_class_prop_list" in dm:
            for item in dm["surface_class_prop_list"]:
                if MCellSurfaceClassPropertiesProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesProperty data model to current version." )

        self.name = dm["name"]
        while len(self.surf_class_props_list) > 0:
            self.surf_class_props_list.remove(0)
        if "surface_class_prop_list" in dm:
            for sc in dm["surface_class_prop_list"]:
                self.surf_class_props_list.add()
                self.active_surf_class_props_index = len(self.surf_class_props_list)-1
                scp = self.surf_class_props_list[self.active_surf_class_props_index]
                # scp.init_properties(context.scene.mcell.parameter_system)
                scp.build_properties_from_data_model ( context, sc )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )
        



class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
    """ Assign a surface class to a surface region. """

    name = StringProperty(name="Assign Surface Class")
    surf_class_name = StringProperty(
        name="Surface Class Name",
        description="This surface class will be assigned to the surface "
                    "region listed below.",
        update=cellblender_operators.check_active_mod_surf_regions)
    object_name = StringProperty(
        name="Object Name",
        description="A region on this object will have the above surface "
                    "class assigned to it.",
        update=cellblender_operators.check_active_mod_surf_regions)
    region_name = StringProperty(
        name="Region Name",
        description="This surface region will have the above surface class "
                    "assigned to it.",
        update=cellblender_operators.check_active_mod_surf_regions)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties... no collections to remove." )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Region building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2014_10_24_1638"
        sr_dm['name'] = self.name
        sr_dm['surf_class_name'] = self.surf_class_name
        sr_dm['object_name'] = self.object_name
        sr_dm['region_name'] = self.region_name
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsProperty data model to current version." )

        self.name = dm["name"]
        self.surf_class_name = dm["surf_class_name"]
        self.object_name = dm["object_name"]
        self.region_name = dm["region_name"]

    def check_properties_after_building ( self, context ):
        print ( "Implementing check_properties_after_building for " + str(self) )
        print ( "Calling check_mod_surf_regions on object named: " + self.object_name )
        cellblender_operators.check_mod_surf_regions(self, context)
        



# Callback Functions must be defined before being used:

def set_tab_autocomplete_callback ( self, context ):
    # print ( "Called with self.tab_autocomplete = " + str(self.tab_autocomplete) )
    if self.tab_autocomplete:
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.indent'].active = False
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.autocomplete'].type = 'TAB'
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.autocomplete'].ctrl = False
    else:
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.autocomplete'].type = 'SPACE'
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.autocomplete'].ctrl = True
        bpy.data.window_managers['WinMan'].keyconfigs['Blender'].keymaps['Console'].keymap_items['console.indent'].active = True


def set_double_sided_callback ( self, context ):
    for mesh in bpy.data.meshes:
        mesh.show_double_sided = self.double_sided

def set_backface_culling_callback ( self, context ):
    # bpy.data.window_managers[0].windows[0].screen.areas[4].spaces[0].show_backface_culling = True        
    for wm in bpy.data.window_managers:
        for w in wm.windows:
            for a in w.screen.areas:
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.show_backface_culling = self.backface_culling


from . import cellblender_panels

def set_old_scene_panels_callback(self, context):
    """ Show or hide the old scene panels based on the show_old_scene_panels boolean property. """
    print ( "Toggling the old scene panels" )
    mcell = context.scene.mcell
    prefs = mcell.cellblender_preferences
    if (prefs.show_scene_panel or prefs.show_tool_panel):
        # One of the other panels is showing, so it's OK to toggle
        show_old_scene_panels ( prefs.show_old_scene_panels )
    else:
        # No other panels are showing so DON'T ALLOW THIS ONE TO GO AWAY!
        prefs.show_old_scene_panels = True
        show_old_scene_panels ( True )


def set_scene_panel_callback(self, context):
    """ Show or hide the scene panel based on the show_scene_panel boolean property. """
    print ( "Toggling the scene panel" )
    mcell = context.scene.mcell
    prefs = mcell.cellblender_preferences
    if (prefs.show_old_scene_panels or prefs.show_tool_panel):
        # One of the other panels is showing, so it's OK to toggle
        show_hide_scene_panel ( prefs.show_scene_panel )
    else:
        # No other panels are showing so DON'T ALLOW THIS ONE TO GO AWAY!
        prefs.show_scene_panel = True
        show_hide_scene_panel ( True )


def set_tool_panel_callback(self, context):
    """ Show or hide the tool panel based on the show_tool_panel boolean property. """
    print ( "Toggling the tool panels" )
    mcell = context.scene.mcell
    prefs = mcell.cellblender_preferences
    if (prefs.show_old_scene_panels or prefs.show_scene_panel):
        # One of the other panels is showing, so it's OK to toggle
        show_hide_tool_panel ( prefs.show_tool_panel )
    else:
        # No other panels are showing so DON'T ALLOW THIS ONE TO GO AWAY!
        prefs.show_tool_panel = True
        show_hide_tool_panel ( True )

    



class CellBlenderPreferencesPropertyGroup(bpy.types.PropertyGroup):

    mcell_binary = StringProperty(name="MCell Binary",
        update=cellblender_operators.check_mcell_binary)
    mcell_binary_valid = BoolProperty(name="MCell Binary Valid",
        default=False)
    python_binary = StringProperty(name="Python Binary",
        update=cellblender_operators.check_python_binary)
    python_binary_valid = BoolProperty(name="Python Binary Valid",
        default=False)
    bionetgen_location = StringProperty(name="BioNetGen Location",
        update=cellblender_operators.check_bionetgen_location)
    bionetgen_location_valid = BoolProperty(name="BioNetGen Location Valid",
        default=False)

    invalid_policy_enum = [
        ('dont_run', "Do not run with errors", ""),
        ('filter', "Filter errors and run", ""),
        ('ignore', "Ignore errors and attempt run", "")]
    invalid_policy = EnumProperty(
        items=invalid_policy_enum,
        name="Invalid Policy",
        default='dont_run',
        update=cellblender_operators.save_preferences)
    decouple_export_run = BoolProperty(
        name="Decouple Export and Run", default=False,
        description="Allow the project to be exported without also running"
                    " the simulation.",
        update=cellblender_operators.save_preferences)
    debug_level = IntProperty(
        name="Debug", default=0, min=0, max=100,
        description="Amount of debug information to print: 0 to 100")
    
    use_long_menus = BoolProperty(
        name="Show Long Menu Buttons", default=True,
        description="Show Menu Buttons with Text Labels")

    use_stock_icons = BoolProperty (
        name="Use only internal Blender Icons", default=True,
        description="Use only internal Blender Icons")


    show_extra_options = BoolProperty (
        name="Show Extra Options", default=False,
        description="Show Additional Options (mostly for debugging)" )

    show_button_num = BoolVectorProperty ( size=15, default=[True for i in range(15)] )


    show_old_scene_panels = BoolProperty(
        name="Old CellBlender in Scene Tab", default=True,
        description="Show Old CellBlender Panels in Scene Tab", update=set_old_scene_panels_callback)

    show_scene_panel = BoolProperty(
        name="CellBlender in Scene Tab", default=True,
        description="Show CellBlender Panel in Scene Tab", update=set_scene_panel_callback)

    show_tool_panel = BoolProperty(
        name="CellBlender in Tool Tab", default=True,
        description="Show CellBlender Panel in Tool Tab", update=set_tool_panel_callback)

    show_sim_runner_options = BoolProperty(name="Show Alternate Simulation Runners", default=False)

    tab_autocomplete = BoolProperty(name="Use tab for console autocomplete", default=False, update=set_tab_autocomplete_callback)
    double_sided = BoolProperty(name="Show Double Sided Mesh Objects", default=False, update=set_double_sided_callback)
    backface_culling = BoolProperty(name="Backface Culling", default=False, update=set_backface_culling_callback)



    def remove_properties ( self, context ):
        print ( "Removing all Preferences Properties... no collections to remove." )


    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row(align=True)
            row.operator("mcell.preferences_reset")
            layout.separator()

            row = layout.row()
            row.operator("mcell.set_mcell_binary",
                         text="Set Path to MCell Binary", icon='FILESEL')
            row = layout.row()
            mcell_binary = self.mcell_binary
            if not mcell_binary:
                row.label("MCell Binary not set", icon='UNPINNED')
            elif not self.mcell_binary_valid:
                row.label("MCell File/Permissions Error: " +
                    self.mcell_binary, icon='ERROR')
            else:
                row.label(
                    text="MCell Binary: "+self.mcell_binary,
                    icon='FILE_TICK')

            row = layout.row()
            row.operator("mcell.set_bionetgen_location",
                         text="Set Path to BioNetGen File", icon='FILESEL')
            row = layout.row()
            bionetgen_location = self.bionetgen_location
            if not bionetgen_location:
                row.label("BioNetGen location not set", icon='UNPINNED')
            elif not self.bionetgen_location_valid:
                row.label("BioNetGen File/Permissions Error: " +
                    self.bionetgen_location, icon='ERROR')
            else:
                row.label(
                    text="BioNetGen Location: " + self.bionetgen_location,
                    icon='FILE_TICK')

            row = layout.row()
            row.operator("mcell.set_python_binary",
                         text="Set Path to Python Binary", icon='FILESEL')
            row = layout.row()
            python_path = self.python_binary
            if not python_path:
                row.label("Python Binary not set", icon='UNPINNED')
            elif not self.python_binary_valid:
                row.label("Python File/Permissions Error: " +
                    self.python_binary, icon='ERROR')
            else:
                row.label(
                    text="Python Binary: " + self.python_binary,
                    icon='FILE_TICK')

            row = layout.row()
            row.prop(mcell.cellblender_preferences, "decouple_export_run")
            row = layout.row()
            row.prop(mcell.cellblender_preferences, "invalid_policy")

            layout.separator()

            row = layout.row()
            row.prop ( context.user_preferences.inputs, "view_rotate_method" )
            
            row = layout.row()
            row.prop(mcell.cellblender_preferences, "use_long_menus")

            row = layout.row()
            row.prop(mcell.cellblender_preferences, "use_stock_icons")

            row = layout.row()
            row.prop ( context.user_preferences.system, "use_vertex_buffer_objects", text="Enable Vertex Buffer Objects" )
            
            row = layout.row()
            row.prop ( mcell.cellblender_preferences, "backface_culling", text="Enable Backface Culling" )

            row = layout.row()
            row.prop ( mcell.cellblender_preferences, "double_sided" )

            box = layout.box()

            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.show_extra_options:
                row.prop(self, "show_extra_options", icon='TRIA_DOWN', emboss=False)

                row = box.row()
                row.prop(mcell.cellblender_preferences, "tab_autocomplete")
                row = box.row()
                row.prop(mcell.cellblender_preferences, "show_tool_panel")
                row = box.row()
                row.prop(mcell.cellblender_preferences, "show_scene_panel")
                row = box.row()
                row.prop(mcell.cellblender_preferences, "show_old_scene_panels")

                row = box.row()
                row.prop(mcell.cellblender_preferences, "show_sim_runner_options")


                row = box.row()
                row.label ( "Enable/Disable individual short menu buttons:" )
                row = box.row()
                row.prop(mcell.cellblender_preferences, "show_button_num", text="")


            else:
                row.prop(self, "show_extra_options", icon='TRIA_RIGHT', emboss=False)
                

            


            #row.operator ( "mcell.reregister_panels", text="Show CB Panels",icon='ZOOMIN')
            #row.operator ( "mcell.unregister_panels", text="Hide CB Panels",icon='ZOOMOUT')
            

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


#class MCellScratchPropertyGroup(bpy.types.PropertyGroup):
#    show_all_icons = BoolProperty(
#        name="Show All Icons",
#        description="Show all Blender icons and their names",
#        default=False)
#    print_all_icons = BoolProperty(
#        name="Print All Icon Names",
#        description="Print all Blender icon names (helpful for searching)",
#        default=False)


class MCellProjectPropertyGroup(bpy.types.PropertyGroup):
    base_name = StringProperty(
        name="Project Base Name", default="cellblender_project")

    status = StringProperty(name="Status")

    def draw_layout (self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            split = row.split(0.96)
            col = split.column()
            col.label(text="CellBlender ID: "+cellblender.cellblender_info['cellblender_source_sha1'])
            col = split.column()
            col.prop ( mcell, "refresh_source_id", icon='FILE_REFRESH', text="" )
            if 'cellblender_source_id_from_file' in cellblender.cellblender_info:
                # This means that the source ID didn't match the refreshed version
                # Draw a second line showing the original file ID as an error
                row = layout.row()
                row.label("File ID: " + cellblender.cellblender_info['cellblender_source_id_from_file'], icon='ERROR')

            # if not mcell.versions_match:
            if not cellblender.cellblender_info['versions_match']:
                # Version in Blend file does not match Addon, so give user a button to upgrade if desired
                row = layout.row()
                row.label ( "Blend File version doesn't match CellBlender version", icon='ERROR' )

                row = layout.row()
                row.operator ( "mcell.upgrade", text="Upgrade Blend File to Current Version", icon='RADIO' )
                #row = layout.row()
                #row.operator ( "mcell.delete", text="Delete CellBlender Collection Properties", icon='RADIO' )

                row = layout.row()
                row.label ( "Note: Saving this file will FORCE an upgrade!!!", icon='ERROR' )

            row = layout.row()
            if not bpy.data.filepath:
                row.label(
                    text="No Project Directory: Use File/Save or File/SaveAs",
                    icon='UNPINNED')
            else:
                row.label(
                    text="Project Directory: " + os.path.dirname(bpy.data.filepath),
                    icon='FILE_TICK')

            row = layout.row()
            layout.prop(context.scene, "name", text="Project Base Name")

    def remove_properties ( self, context ):
        print ( "Removing all Preferences Properties... no collections to remove." )

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


class MCellExportProjectPropertyGroup(bpy.types.PropertyGroup):
    export_format_enum = [
        ('mcell_mdl_unified', "Single Unified MCell MDL File", ""),
        ('mcell_mdl_modular', "Modular MCell MDL Files", "")]
    export_format = EnumProperty(items=export_format_enum,
                                 name="Export Format",
                                 default='mcell_mdl_modular')

    def remove_properties ( self, context ):
        print ( "Removing all Export Project Properties... no collections to remove." )


class MCellRunSimulationProcessesProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Simulation Runner Process")
    #pid = IntProperty(name="PID")

    def remove_properties ( self, context ):
        print ( "Removing all Run Simulation Process Properties for " + self.name + "... no collections to remove." )

    def build_data_model_from_properties ( self, context ):
        print ( "MCellRunSimulationProcesses building Data Model" )
        dm = {}
        dm['data_model_version'] = "DM_2015_04_23_1753"
        dm['name'] = self.name
        return dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellRunSimulationProcessesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_23_1753
            dm['data_model_version'] = "DM_2015_04_23_1753"

        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationProcessesProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationProcessesProperty data model to current version." )
        self.name = dm["name"]


def sim_runner_changed_callback ( self, context ):
    """ The run lists are somewhat incompatible between sim runners, so just clear them when switching. """
    # print ( "Sim Runner has been changed!!" )
    # mcell = context.scene.mcell
    bpy.ops.mcell.clear_run_list()
    bpy.ops.mcell.clear_simulation_queue()
    

class MCellRunSimulationPropertyGroup(bpy.types.PropertyGroup):
    start_seed = IntProperty(
        name="Start Seed", default=1, min=1,
        description="The starting value of the random number generator seed",
        update=cellblender_operators.check_start_seed)
    end_seed = IntProperty(
        name="End Seed", default=1, min=1,
        description="The ending value of the random number generator seed",
        update=cellblender_operators.check_end_seed)
    mcell_processes = IntProperty(
        name="Number of Processes",
        default=cpu_count(),
        min=1,
        max=cpu_count(),
        description="Number of simultaneous MCell processes")
    log_file_enum = [
        ('none', "Do not Generate", ""),
        ('file', "Send to File", ""),
        ('console', "Send to Console", "")]
    log_file = EnumProperty(
        items=log_file_enum, name="Output Log", default='console',
        description="Where to send MCell log output")
    error_file_enum = [
        ('none', "Do not Generate", ""),
        ('file', "Send to File", ""),
        ('console', "Send to Console", "")]
    error_file = EnumProperty(
        items=error_file_enum, name="Error Log", default='console',
        description="Where to send MCell error output")
    remove_append_enum = [
        ('remove', "Remove Previous Data", ""),
        ('append', "Append to Previous Data", "")]
    remove_append = EnumProperty(
        items=remove_append_enum, name="Previous Simulation Data",
        default='remove',
        description="Remove or append to existing rxn/viz data from previous"
                    " simulations before running new simulations.")
    processes_list = CollectionProperty(
        type=MCellRunSimulationProcessesProperty,
        name="Simulation Runner Processes")
    active_process_index = IntProperty(
        name="Active Simulation Runner Process Index", default=0)
    status = StringProperty(name="Status")
    error_list = CollectionProperty(
        type=MCellStringProperty,
        name="Error List")
    active_err_index = IntProperty(
        name="Active Error Index", default=0)


    show_output_options = BoolProperty ( name='Output Options', default=False )


    simulation_run_control_enum = [
        ('COMMAND', "Command Line", ""),
        ('JAVA', "Java Control", ""),
        ('OPENGL', "OpenGL Control", ""),
        ('QUEUE', "Queue Control", "")]
    simulation_run_control = EnumProperty(
        items=simulation_run_control_enum, name="",
        description="Mechanism for running and controlling the simulation",
        default='QUEUE', update=sim_runner_changed_callback)


    def remove_properties ( self, context ):
        print ( "Removing all Run Simulation Properties..." )
        for item in self.processes_list:
            item.remove_properties(context)
        self.processes_list.clear()
        self.active_process_index = 0
        for item in self.error_list:
            item.remove_properties(context)
        self.error_list.clear()
        self.active_err_index = 0
        print ( "Done removing all Run Simulation Properties." )

    def build_data_model_from_properties ( self, context ):
        print ( "MCellRunSimulationPropertyGroup building Data Model" )
        dm = {}
        dm['data_model_version'] = "DM_2015_04_23_1753"
        dm['name'] = self.name
        p_list = []
        for p in self.processes_list:
            p_list.append ( p.build_data_model_from_properties(context) )
        dm['processes_list'] = p_list
        return dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellRunSimulationPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_23_1753
            dm['data_model_version'] = "DM_2015_04_23_1753"

        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )
            return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )

        self.name = dm["name"]
        self.processes_list.clear()
        for p in dm['processes_list']:
            self.processes_list.add()
            self.active_process_index = len(self.processes_list) - 1
            self.processes_list[self.active_process_index].build_properties_from_data_model(context, p)



    def draw_layout_queue(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            #mcell.project_settings.base_name = scene_name

            main_mdl = project_files_path()
            main_mdl = os.path.join(main_mdl, scene_name + ".main.mdl")

            row = layout.row()

            # Only allow the simulation to be run if both an MCell binary and a
            # project dir have been selected. There also needs to be a main mdl
            # file present.
            if not mcell.cellblender_preferences.mcell_binary:
                row.label(text="Set an MCell binary in CellBlender - Preferences Panel", icon='ERROR')
            elif not os.path.dirname(bpy.data.filepath):
                row.label(
                    text="Open or save a .blend file to set the project directory",
                    icon='ERROR')
            elif (not os.path.isfile(main_mdl) and
                    mcell.cellblender_preferences.decouple_export_run):
                row.label(text="Export the project", icon='ERROR')
                row = layout.row()
                row.operator(
                    "mcell.export_project",
                    text="Export CellBlender Project", icon='EXPORT')
            else:

                row = layout.row(align=True)
                if mcell.cellblender_preferences.decouple_export_run:
                    row.operator(
                        "mcell.export_project", text="Export CellBlender Project",
                        icon='EXPORT')
                row.operator("mcell.run_simulation", text="Run",
                             icon='COLOR_RED')
                
                if self.simulation_run_control != "QUEUE":
                    if self.processes_list and (len(self.processes_list) > 0):
                        row = layout.row()
                        row.template_list("MCELL_UL_run_simulation", "run_simulation",
                                          self, "processes_list",
                                          self, "active_process_index",
                                          rows=2)
                        row = layout.row()
                        row.operator("mcell.clear_run_list")

                else:

                    if (self.processes_list and
                            cellblender.simulation_queue.task_dict):
                        row = layout.row()
                        row.label(text="MCell Processes:",
                                  icon='FORCE_LENNARDJONES')
                        row = layout.row()
                        row.template_list("MCELL_UL_run_simulation_queue", "run_simulation_queue",
                                          self, "processes_list",
                                          self, "active_process_index",
                                          rows=2)
                        row = layout.row()
                        row.operator("mcell.clear_simulation_queue")
                        row = layout.row()
                        row.operator("mcell.kill_simulation")
                        row.operator("mcell.kill_all_simulations")


                box = layout.box()

                if self.show_output_options:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    row.prop(self, "show_output_options", icon='TRIA_DOWN',
                             text="Output / Control Options", emboss=False)

                    row = box.row(align=True)
                    row.prop(self, "start_seed")
                    row.prop(self, "end_seed")
                    row = box.row()
                    row.prop(self, "mcell_processes")
                    #row = box.row()
                    #row.prop(self, "log_file")
                    #row = box.row()
                    #row.prop(self, "error_file")
                    row = box.row()
                    row.prop(mcell.export_project, "export_format")

                    row = box.row()
                    row.prop(self, "remove_append", expand=True)
                    row = box.row()
                    col = row.column()
                    col.prop(mcell.cellblender_preferences, "decouple_export_run")

# Disable selector for simulation_run_control options
#  Queue control is the default
#  Queue control is currently the only option which properly disables the
#  run_simulation operator while simulations are currenlty running or queued
                    if mcell.cellblender_preferences.show_sim_runner_options:
                        col = row.column()
                        col.prop(self, "simulation_run_control")

                else:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    row.prop(self, "show_output_options", icon='TRIA_RIGHT',
                             text="Output / Control Options", emboss=False)

                
            if self.status:
                row = layout.row()
                row.label(text=self.status, icon='ERROR')
            
            if self.error_list: 
                row = layout.row() 
                row.label(text="Errors:", icon='ERROR')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_error_list", "run_simulation_queue",
                                  self, "error_list",
                                  self, "active_err_index", rows=2)


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout_queue ( context, layout )



class MCellMolVizPropertyGroup(bpy.types.PropertyGroup):
    """ Property group for for molecule visualization.

      This is the "Visualize Simulation Results Panel".

    """

    mol_viz_seed_list = CollectionProperty(
        type=MCellStringProperty, name="Visualization Seed List")
    active_mol_viz_seed_index = IntProperty(
        name="Current Visualization Seed Index", default=0,
        update=cellblender_operators.read_viz_data_callback)
        #update= bpy.ops.mcell.read_viz_data)
    mol_file_dir = StringProperty(
        name="Molecule File Dir", subtype='NONE')
    mol_file_list = CollectionProperty(
        type=MCellStringProperty, name="Molecule File Name List")
    mol_file_num = IntProperty(
        name="Number of Molecule Files", default=0)
    mol_file_name = StringProperty(
        name="Current Molecule File Name", subtype='NONE')
    mol_file_index = IntProperty(name="Current Molecule File Index", default=0)
    mol_file_start_index = IntProperty(
        name="Molecule File Start Index", default=0)
    mol_file_stop_index = IntProperty(
        name="Molecule File Stop Index", default=0)
    mol_file_step_index = IntProperty(
        name="Molecule File Step Index", default=1)
    mol_viz_list = CollectionProperty(
        type=MCellStringProperty, name="Molecule Viz Name List")
    render_and_save = BoolProperty(name="Render & Save Images")
    mol_viz_enable = BoolProperty(
        name="Enable Molecule Vizualization",
        description="Disable for faster animation preview",
        default=True, update=cellblender_operators.mol_viz_update)
    color_list = CollectionProperty(
        type=MCellFloatVectorProperty, name="Molecule Color List")
    color_index = IntProperty(name="Color Index", default=0)
    manual_select_viz_dir = BoolProperty(
        name="Manually Select Viz Directory", default=False,
        description="Toggle the option to manually load viz data.",
        update=cellblender_operators.mol_viz_toggle_manual_select)


    def build_data_model_from_properties ( self, context ):
        print ( "Building Mol Viz data model from properties" )
        mv_dm = {}
        mv_dm['data_model_version'] = "DM_2015_04_13_1700"

        mv_seed_list = []
        for s in self.mol_viz_seed_list:
            mv_seed_list.append ( str(s.name) )
        mv_dm['seed_list'] = mv_seed_list

        mv_dm['active_seed_index'] = self.active_mol_viz_seed_index
        mv_dm['file_dir'] = self.mol_file_dir

        # mv_file_list = []
        # for s in self.mol_file_list:
        #     mv_file_list.append ( str(s.name) )
        # mv_dm['file_list'] = mv_file_list

        mv_dm['file_num'] = self.mol_file_num
        mv_dm['file_name'] = self.mol_file_name
        mv_dm['file_index'] = self.mol_file_index
        mv_dm['file_start_index'] = self.mol_file_start_index
        mv_dm['file_stop_index'] = self.mol_file_stop_index
        mv_dm['file_step_index'] = self.mol_file_step_index

        mv_viz_list = []
        for s in self.mol_viz_list:
            mv_viz_list.append ( str(s.name) )
        mv_dm['viz_list'] = mv_viz_list

        mv_dm['render_and_save'] = self.render_and_save
        mv_dm['viz_enable'] = self.mol_viz_enable

        mv_color_list = []
        for c in self.color_list:
            mv_color = []
            for i in c.vec:
                mv_color.append ( i )
            mv_color_list.append ( mv_color )
        mv_dm['color_list'] = mv_color_list

        mv_dm['color_index'] = self.color_index
        mv_dm['manual_select_viz_dir'] = self.manual_select_viz_dir

        return mv_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMolVizPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_13_1700
            dm['data_model_version'] = "DM_2015_04_13_1700"

        if dm['data_model_version'] == "DM_2015_04_13_1700":
            # Change on June 22nd, 2015: The molecule file list will no longer be stored in the data model
            if 'file_list' in dm:
                dm.pop ( 'file_list' )
            dm['data_model_version'] = "DM_2015_06_22_1430"

        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )

        # Remove the old properties (includes emptying collections)
        self.remove_properties ( context )

        # Build the new properties
        
        for s in dm["seed_list"]:
            new_item = self.mol_viz_seed_list.add()
            new_item.name = s
            
        self.active_mol_viz_seed_index = dm['active_seed_index']

        self.mol_file_dir = dm['file_dir']

        #for s in dm["file_list"]:
        #    new_item = self.mol_file_list.add()
        #    new_item.name = s

        self.mol_file_num = dm['file_num']
        self.mol_file_name = dm['file_name']
        self.mol_file_index = dm['file_index']
        self.mol_file_start_index = dm['file_start_index']
        self.mol_file_stop_index = dm['file_stop_index']
        self.mol_file_step_index = dm['file_step_index']
            
        for s in dm["viz_list"]:
            new_item = self.mol_viz_list.add()
            new_item.name = s
            
        self.render_and_save = dm['render_and_save']
        self.mol_viz_enable = dm['viz_enable']

        for c in dm["color_list"]:
            new_item = self.color_list.add()
            new_item.vec = c
            
        if 'color_index' in dm:
            self.color_index = dm['color_index']
        else:
            self.color_index = 0

        self.manual_select_viz_dir = dm['manual_select_viz_dir']


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Visualization Properties..." )

        """
        while len(self.mol_viz_seed_list) > 0:
            self.mol_viz_seed_list.remove(0)

        while len(self.mol_file_list) > 0:
            self.mol_file_list.remove(0)

        while len(self.mol_viz_list) > 0:
            self.mol_viz_list.remove(0)

        while len(self.color_list) > 0:
            # It's not clear if anything needs to be done to remove individual color components first
            self.color_list.remove(0)
        """

        for item in self.mol_viz_seed_list:
            item.remove_properties(context)
        self.mol_viz_seed_list.clear()
        self.active_mol_viz_seed_index = 0
        for item in self.mol_file_list:
            item.remove_properties(context)
        self.mol_file_list.clear()
        self.mol_file_index = 0
        self.mol_file_start_index = 0
        self.mol_file_stop_index = 0
        self.mol_file_step_index = 1
        for item in self.mol_viz_list:
            item.remove_properties(context)
        self.mol_viz_list.clear()
        for item in self.color_list:
            item.remove_properties(context)
        self.color_list.clear()
        self.color_index = 0
        print ( "Done removing all Molecule Visualization Properties." )





    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            row.prop(mcell.mol_viz, "manual_select_viz_dir")
            row = layout.row()
            if self.manual_select_viz_dir:
                row.operator("mcell.select_viz_data", icon='IMPORT')
            else:
                row.operator("mcell.read_viz_data", icon='IMPORT')
            row = layout.row()
            row.label(text="Molecule Viz Directory: " + self.mol_file_dir,
                      icon='FILE_FOLDER')
            row = layout.row()
            if not self.manual_select_viz_dir:
                row.template_list("UI_UL_list", "viz_seed", mcell.mol_viz,
                                "mol_viz_seed_list", mcell.mol_viz,
                                "active_mol_viz_seed_index", rows=2)
            row = layout.row()

            row = layout.row()
            row.label(text="Current Molecule File: "+self.mol_file_name,
                      icon='FILE')
# Disabled to explore UI slowdown behavior of Plot Panel and run options subpanel when mol_file_list is large
#            row = layout.row()
#            row.template_list("UI_UL_list", "viz_results", mcell.mol_viz,
#                              "mol_file_list", mcell.mol_viz, "mol_file_index",
#                              rows=2)
            row = layout.row()
            layout.prop(mcell.mol_viz, "mol_viz_enable")


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



# from . import parameter_system


class MCellInitializationPropertyGroup(bpy.types.PropertyGroup):

    def __init__(self):
        print ( "\n\nMCellInitializationPropertyGroup.__init__() called\n\n" )

    iterations = PointerProperty ( name="iterations", type=parameter_system.Parameter_Reference )
    time_step =  PointerProperty ( name="Time Step", type=parameter_system.Parameter_Reference )

    status = StringProperty(name="Status")
    advanced = bpy.props.BoolProperty(default=False)
    warnings = bpy.props.BoolProperty(default=False)
    notifications = bpy.props.BoolProperty(default=False)

    # Advanced/Optional Commands

    time_step_max = PointerProperty ( name="Time Step Max", type=parameter_system.Parameter_Reference )
    space_step = PointerProperty ( name="Space Step", type=parameter_system.Parameter_Reference )
    interaction_radius = PointerProperty ( name="Interaction Radius", type=parameter_system.Parameter_Reference )
    radial_directions = PointerProperty ( name="Radial Directions", type=parameter_system.Parameter_Reference )
    radial_subdivisions = PointerProperty ( name="Radial Subdivisions", type=parameter_system.Parameter_Reference )
    vacancy_search_distance = PointerProperty ( name="Radial Subdivisions", type=parameter_system.Parameter_Reference )
    surface_grid_density = PointerProperty ( name="Surface Grid Density", type=parameter_system.Parameter_Reference )

    def init_properties ( self, parameter_system ):
        helptext = "Number of iterations to run"
        self.iterations.init_ref    ( parameter_system, "Iteration_Type", 
                                      user_name="Iterations", 
                                      user_expr="1000",    
                                      user_units="",  
                                      user_descr=helptext,  
                                      user_int=True )

        helptext = "Simulation Time Step\n1e-6 is a common value."
        self.time_step.init_ref     ( parameter_system, "Time_Step_Type", 
                                      user_name="Time Step",  
                                      user_expr="1e-6", 
                                      user_units="seconds", 
                                      user_descr=helptext )
       
        helptext = "The longest possible time step.\n" + \
                   "MCell3 will move longer than the specified simulation time step\n" + \
                   "if it seems safe. This command makes sure that the longest possible\n" + \
                   "time step is no longer than this value (in seconds), even if MCell3\n" + \
                   "thinks a longer step would be safe. The default is no limit."
        self.time_step_max.init_ref ( parameter_system, "Time_Step_Max_Type", 
                                      user_name="Maximum Time Step", 
                                      user_expr="", 
                                      user_units="seconds", 
                                      user_descr=helptext )
       
        helptext = "Have molecules take the same mean diffusion distance.\n" + \
                   "Have all diffusing molecules take time steps of different duration,\n" + \
                   "chosen so that the mean diffusion distance is N microns for each\n" + \
                   "molecule. By default, all molecules move the same time step."
        self.space_step.init_ref    ( parameter_system, "Space_Step_Type",    
                                      user_name="Space Step",    
                                      user_expr="", 
                                      user_units="microns", 
                                      user_descr=helptext )
       
        helptext = "Diffusing Volume Molecules will interact when they get within\n" + \
                   "N microns of each other.\n" + \
                   "The default is:  1 / sqrt(Pi * SurfaceGridDensity)"
        self.interaction_radius.init_ref ( parameter_system, "Int_Rad_Type", 
                                           user_name="Interaction Radius", 
                                           user_expr="", user_units="microns", 
                                           user_descr=helptext )
       
        helptext = "Specifies how many different directions to put in the lookup table." + \
                   "The default is sensible. Don’t use this unless you know what you’re doing." + \
                   "Instead of a number, you can specify FULLY_RANDOM in MDL to generate the" + \
                   "directions directly from double precision numbers (but this is slower)."
        self.radial_directions.init_ref   ( parameter_system, "Rad_Dir_Type", 
                                            user_name="Radial Directions",   
                                            user_expr="", user_units="microns", 
                                            user_descr=helptext )
       
        helptext = "Specifies how many distances to put in the diffusion look-up table.\n" + \
                   "The default is sensible. FULLY_RANDOM is not implemented."
        self.radial_subdivisions.init_ref ( parameter_system, "Rad_Sub_Type", 
                                            user_name="Radial Subdivisions", 
                                            user_expr="", 
                                            user_descr=helptext )
       
        helptext = "Surface molecule products can be created at r distance.\n" + \
                   "Normally, a reaction will not proceed on a surface unless there\n" + \
                   "is room to place all products on the single grid element where\n" + \
                   "the reaction is initiated. By increasing r from its default value\n" + \
                   "of 0, one can specify how far from the reaction’s location, in microns,\n" + \
                   "the reaction can place its products. To be useful, r must\n" + \
                   "be larger than the longest axis of the grid element on the triangle\n" + \
                   "in question. The reaction will then proceed if there is room to\n" + \
                   "place its products within a radius r, and will place those products\n" + \
                   "as close as possible to the place where the reaction occurs\n" + \
                   "(deterministically, so small- scale directional bias is possible)."
        self.vacancy_search_distance.init_ref ( parameter_system, "Vac_SD_Type", 
                                                user_name="Vacancy Search Distance", 
                                                user_expr="", 
                                                user_units="microns", 
                                                user_descr=helptext )
       
        helptext = "Number of molecules that can be stored per square micron.\n" + \
                   "Tile all surfaces so that they can hold molecules at N different\n" + \
                   "positions per square micron. The default is 10000. For backwards\n" + \
                   "compatibility, EFFECTOR_GRID_DENSITY works also in MCell MDL."
        self.surface_grid_density.init_ref ( parameter_system, "Int_Rad_Type", 
                                             user_name="Surface Grid Density", 
                                             user_expr="10000", 
                                             user_units="count / sq micron", 
                                             user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Initialization Properties... no collections to remove." )


    def build_data_model_from_properties ( self, context ):
        dm_dict = {}

        dm_dict['data_model_version'] = "DM_2014_10_24_1638"

        dm_dict['iterations'] = self.iterations.get_expr()
        dm_dict['time_step'] = self.time_step.get_expr()
        dm_dict['time_step_max'] = self.time_step_max.get_expr()
        dm_dict['space_step'] = self.space_step.get_expr()
        dm_dict['interaction_radius'] = self.interaction_radius.get_expr()
        dm_dict['radial_directions'] = self.radial_directions.get_expr()
        dm_dict['radial_subdivisions'] = self.radial_subdivisions.get_expr()
        dm_dict['vacancy_search_distance'] = self.vacancy_search_distance.get_expr()
        dm_dict['surface_grid_density'] = self.surface_grid_density.get_expr()
        dm_dict['microscopic_reversibility'] = str(self.microscopic_reversibility)
        dm_dict['accurate_3d_reactions'] = self.accurate_3d_reactions==True
        dm_dict['center_molecules_on_grid'] = self.center_molecules_grid==True

        notify_dict = {}
        notify_dict['all_notifications'] = str(self.all_notifications)
        notify_dict['diffusion_constant_report'] = str(self.diffusion_constant_report)
        notify_dict['file_output_report'] = self.file_output_report==True
        notify_dict['final_summary'] = self.final_summary==True
        notify_dict['iteration_report'] = self.iteration_report==True
        notify_dict['partition_location_report'] = self.partition_location_report==True
        notify_dict['probability_report'] = str(self.probability_report)
        notify_dict['probability_report_threshold'] = str(self.probability_report_threshold)
        notify_dict['varying_probability_report'] = self.varying_probability_report==True
        notify_dict['progress_report'] = self.progress_report==True
        notify_dict['release_event_report'] = self.release_event_report==True
        notify_dict['molecule_collision_report'] = self.molecule_collision_report==True
        notify_dict['box_triangulation_report'] = False
        dm_dict['notifications'] = notify_dict
        
        warn_dict = {}
        warn_dict['all_warnings'] = str(self.all_warnings)
        warn_dict['degenerate_polygons'] = str(self.degenerate_polygons)
        warn_dict['high_reaction_probability'] = str(self.high_reaction_probability)
        warn_dict['high_probability_threshold'] = str(self.high_probability_threshold)
        warn_dict['lifetime_too_short'] = str(self.lifetime_too_short)
        warn_dict['lifetime_threshold'] = str(self.lifetime_threshold)
        warn_dict['missed_reactions'] = str(self.missed_reactions)
        warn_dict['missed_reaction_threshold'] = str(self.missed_reaction_threshold)
        warn_dict['negative_diffusion_constant'] = str(self.negative_diffusion_constant)
        warn_dict['missing_surface_orientation'] = str(self.missing_surface_orientation)
        warn_dict['negative_reaction_rate'] = str(self.negative_reaction_rate)
        warn_dict['useless_volume_orientation'] = str(self.useless_volume_orientation)
        dm_dict['warnings'] = warn_dict

        return dm_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellInitializationPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellInitializationPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):

        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellInitializationPropertyGroup data model to current version." )

        self.iterations.set_expr ( dm_dict["iterations"] )
        self.time_step.set_expr ( dm_dict["time_step"] )
        self.time_step_max.set_expr ( dm_dict["time_step_max"] )
        self.space_step.set_expr ( dm_dict["space_step"] )
        self.interaction_radius.set_expr ( dm_dict["interaction_radius"] )
        self.radial_directions.set_expr ( dm_dict["radial_directions"] )
        self.radial_subdivisions.set_expr ( dm_dict["radial_subdivisions"] )
        self.vacancy_search_distance.set_expr ( dm_dict["vacancy_search_distance"] )
        self.surface_grid_density.set_expr ( dm_dict["surface_grid_density"] )
        self.microscopic_reversibility = dm_dict["microscopic_reversibility"]
        self.accurate_3d_reactions = dm_dict["accurate_3d_reactions"]
        self.center_molecules_grid = dm_dict["center_molecules_on_grid"]

        self.all_notifications = dm_dict['notifications']['all_notifications']
        self.diffusion_constant_report = dm_dict['notifications']['diffusion_constant_report']
        self.file_output_report = dm_dict['notifications']['file_output_report']
        self.final_summary = dm_dict['notifications']['final_summary']
        self.iteration_report = dm_dict['notifications']['iteration_report']
        self.partition_location_report = dm_dict['notifications']['partition_location_report']
        self.probability_report = dm_dict['notifications']['probability_report']
        self.probability_report_threshold = float(dm_dict['notifications']['probability_report_threshold'])
        self.varying_probability_report = dm_dict['notifications']['varying_probability_report']
        self.progress_report = dm_dict['notifications']['progress_report']
        self.release_event_report = dm_dict['notifications']['release_event_report']
        self.molecule_collision_report = dm_dict['notifications']['molecule_collision_report']

        ##notify_dict[box_triangulation_report'] = False

        self.all_warnings = dm_dict['warnings']['all_warnings']
        self.degenerate_polygons = dm_dict['warnings']['degenerate_polygons']
        self.high_reaction_probability = dm_dict['warnings']['high_reaction_probability']
        self.high_probability_threshold = float(dm_dict['warnings']['high_probability_threshold'])
        self.lifetime_too_short = dm_dict['warnings']['lifetime_too_short']
        self.lifetime_threshold = float(dm_dict['warnings']['lifetime_threshold'])
        self.missed_reactions = dm_dict['warnings']['missed_reactions']
        self.missed_reaction_threshold = float(dm_dict['warnings']['missed_reaction_threshold'])
        self.negative_diffusion_constant = dm_dict['warnings']['negative_diffusion_constant']
        self.missing_surface_orientation = dm_dict['warnings']['missing_surface_orientation']
        self.negative_reaction_rate = dm_dict['warnings']['negative_reaction_rate']
        self.useless_volume_orientation = dm_dict['warnings']['useless_volume_orientation']

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    accurate_3d_reactions = BoolProperty(
        name="Accurate 3D Reaction",
        description="If selected, molecules will look through partitions to "
                    "react.",
        default=True)
    center_molecules_grid = BoolProperty(
        name="Center Molecules on Grid",
        description="If selected, surface molecules will be centered on the "
                    "grid.",
        default=False)


    microscopic_reversibility_enum = [
        ('ON', "On", ""),
        ('OFF', "Off", ""),
        ('SURFACE_ONLY', "Surface Only", ""),
        ('VOLUME_ONLY', "Volume Only", "")]
    microscopic_reversibility = EnumProperty(
        items=microscopic_reversibility_enum, name="Microscopic Reversibility",
        description="If false, more efficient but less accurate reactions",
        default='OFF')


    # Notifications
    all_notifications_enum = [
        ('INDIVIDUAL', "Set Individually", ""),
        ('ON', "On", ""),
        ('OFF', "Off", "")]
    all_notifications = EnumProperty(
        items=all_notifications_enum, name="All Notifications",
        description="If on/off, all notifications will be set to on/off "
                    "respectively.",
        default='INDIVIDUAL')
    diffusion_constant_report_enum = [
        ('BRIEF', "Brief", ""),
        ('ON', "On", ""),
        ('OFF', "Off", "")]
    diffusion_constant_report = EnumProperty(
        items=diffusion_constant_report_enum, name="Diffusion Constant Report",
        description="If brief, Mcell will report average diffusion distance "
                    "per step for each molecule.")
    file_output_report = BoolProperty(
        name="File Output Report",
        description="If selected, MCell will report every time that reaction "
                    "data is written.",
        default=False)
    final_summary = BoolProperty(
        name="Final Summary",
        description="If selected, MCell will report about the CPU time used",
        default=True)
    iteration_report = BoolProperty(
        name="Iteration Report",
        description="If selected, MCell will report how many iterations have "
                    "completed based on total.",
        default=True)
    partition_location_report = BoolProperty(
        name="Partition Location Report",
        description="If selected, the partition locations will be printed.",
        default=False)
    probability_report_enum = [
        ('ON', "On", ""),
        ('OFF', "Off", ""),
        ('THRESHOLD', "Threshold", "")]
    probability_report = EnumProperty(
        items=probability_report_enum, name="Probability Report", default='ON',
        description="If on, MCell will report reaction probabilites for each "
                    "reaction.")
    probability_report_threshold = bpy.props.FloatProperty(
        name="Threshold", min=0.0, max=1.0, precision=2)
    varying_probability_report = BoolProperty(
        name="Varying Probability Report",
        description="If selected, MCell will print out the reaction "
                    "probabilites for time-varying reaction.",
        default=True)
    progress_report = BoolProperty(
        name="Progress Report",
        description="If selected, MCell will print out messages indicating "
                    "which part of the simulation is underway.",
        default=True)
    release_event_report = BoolProperty(
        name="Release Event Report",
        description="If selected, MCell will print a message every time "
                    "molecules are released through a release site.",
        default=True)
    molecule_collision_report = BoolProperty(
        name="Molecule Collision Report",
        description="If selected, MCell will print the number of "
                    "bi/trimolecular collisions that occured.",
        default=False)


    # Warnings
    all_warnings_enum = [
        ('INDIVIDUAL', "Set Individually", ""),
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    all_warnings = EnumProperty(
        items=all_warnings_enum, name="All Warnings",
        description="If not \"Set Individually\", all warnings will be set "
                    "the same.",
        default='INDIVIDUAL')
    degenerate_polygons_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    degenerate_polygons = EnumProperty(
        items=degenerate_polygons_enum, name="Degenerate Polygons",
        description="Degenerate polygons have zero area and must be removed.",
        default='WARNING')
    high_reaction_probability_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    high_reaction_probability = EnumProperty(
        items=high_reaction_probability_enum, name="High Reaction Probability",
        description="Generate warnings or errors if probability reaches a "
                    "specified threshold.",
        default='IGNORED')
    high_probability_threshold = bpy.props.FloatProperty(
        name="High Probability Threshold", min=0.0, max=1.0, default=1.0,
        precision=2)
    lifetime_too_short_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", "")]
    lifetime_too_short = EnumProperty(
        items=lifetime_too_short_enum, name="Lifetime Too Short",
        description="Generate warning if molecules have short lifetimes.",
        default='WARNING')
    lifetime_threshold = IntProperty(
        name="Threshold", min=0, default=50)
    missed_reactions_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", "")]
    missed_reactions = EnumProperty(
        items=missed_reactions_enum, name="Missed Reactions",
        description="Generate warning if there are missed reactions.",
        default='WARNING')
    missed_reaction_threshold = bpy.props.FloatProperty(
        name="Threshold", min=0.0, max=1.0, default=0.001,
        precision=4)
    negative_diffusion_constant_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    negative_diffusion_constant = EnumProperty(
        items=negative_diffusion_constant_enum,
        description="Diffusion constants cannot be negative and will be set "
                    "to zero.",
        name="Negative Diffusion Constant", default='WARNING')
    missing_surface_orientation_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    missing_surface_orientation = EnumProperty(
        items=missing_surface_orientation_enum,
        description="Generate errors/warnings if molecules are placed on "
                    "surfaces or reactions occur at surfaces without "
                    "specified orientation.",
        name="Missing Surface Orientation",
        default='ERROR')
    negative_reaction_rate_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    negative_reaction_rate = EnumProperty(
        items=negative_reaction_rate_enum, name="Negative Reaction Rate",
        description="Reaction rates cannot be negative and will be set "
                    "to zero.",
        default='WARNING')
    useless_volume_orientation_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    useless_volume_orientation = EnumProperty(
        items=useless_volume_orientation_enum,
        description="Generate errors/warnings if molecules are released in a "
                    "volume or reactions occur in a volume with specified "
                    "orientation.",
        name="Useless Volume Orientation", default='WARNING')


    acc3D_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    center_on_grid_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    micro_rev_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            self.iterations.draw(layout,ps)
            self.time_step.draw(layout,ps)


            # Note that the run_simulation panel is effectively being drawn in the middle of this model_initialization panel!!!
            mcell.run_simulation.draw_layout_queue(context,layout)


            # Advanced Options
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.advanced:
                row.prop(mcell.initialization, "advanced", icon='TRIA_DOWN',
                         text="Advanced Options", emboss=False)

                self.time_step_max.draw(box,ps)
                self.space_step.draw(box,ps)
                self.interaction_radius.draw(box,ps)
                self.radial_directions.draw(box,ps)
                self.radial_subdivisions.draw(box,ps)
                self.vacancy_search_distance.draw(box,ps)
                self.surface_grid_density.draw(box,ps)

                #row = box.row()
                # row.prop(mcell.initialization, "accurate_3d_reactions")
                helptext = "Accurate 3D Reactions\n" + \
                           "Specifies which method to use for computing 3D molecule-molecule\n" + \
                           "interactions. If value is TRUE, then molecules will look\n" + \
                           "through partition boundaries for potential interacting\n" + \
                           "partners – this is slower but more accurate. If boolean is\n" + \
                           "FALSE, then molecule interaction disks will be clipped at partition\n" + \
                           "boundaries and probabilities adjusted to get the correct rate – \n" + \
                           "this is faster but can be less accurate. The default is TRUE."
                ps.draw_prop_with_help ( box, "Accurate 3D Reactions", mcell.initialization, "accurate_3d_reactions", "acc3D_show_help", self.acc3D_show_help, helptext )
                
                #row = box.row()
                #row.prop(mcell.initialization, "center_molecules_grid")
                helptext = "Center Molecules on Grid\n" + \
                           "If boolean is set to TRUE, then all molecules on a surface will be\n" + \
                           "located exactly at the center of their grid element. If FALSE, the\n" + \
                           "molecules will be randomly located when placed, and reactions\n" + \
                           "will take place at the location of the target (or the site of impact\n" + \
                           "in the case of 3D molecule/surface reactions). The default is FALSE."
                ps.draw_prop_with_help ( box, "Center Molecules on Grid", mcell.initialization, "center_molecules_grid", "center_on_grid_show_help", self.center_on_grid_show_help, helptext )

                #row = box.row()
                #row.prop(mcell.initialization, "microscopic_reversibility")
                helptext = "Microscopic Reversibility\n" + \
                           "If value is set to OFF, then binding- unbinding reactions between\n" + \
                           "molecules will be somewhat more efficient but may not be accurate\n" + \
                           "if the probability of binding is high (close to 1).\n" + \
                           "If ON, a more computationally demanding routine will be used to\n" + \
                           "make sure binding- unbinding is more similar in both directions.\n" + \
                           "If value is set to SURFACE_ONLY or VOLUME_ONLY, the more\n" + \
                           "accurate routines will be used only for reactions at surfaces\n" + \
                           "or only for those in the volume. OFF is the default."
                ps.draw_prop_with_help ( box, "Microscopic Reversibility", mcell.initialization, "microscopic_reversibility", "micro_rev_show_help", self.micro_rev_show_help, helptext )

            else:
                row.prop(mcell.initialization, "advanced", icon='TRIA_RIGHT',
                         text="Advanced Options", emboss=False)

            # Notifications
            #box = layout.box(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.notifications:
                row.prop(mcell.initialization, "notifications", icon='TRIA_DOWN',
                         text="Notifications", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_notifications")
                if self.all_notifications == 'INDIVIDUAL':
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "probability_report")
                    if self.probability_report == 'THRESHOLD':
                        row.prop(
                            mcell.initialization, "probability_report_threshold",
                            slider=True)
                    row = box.row()
                    row.prop(mcell.initialization, "diffusion_constant_report")
                    row = box.row()
                    row.prop(mcell.initialization, "file_output_report")
                    row = box.row()
                    row.prop(mcell.initialization, "final_summary")
                    row = box.row()
                    row.prop(mcell.initialization, "iteration_report")
                    row = box.row()
                    row.prop(mcell.initialization, "partition_location_report")
                    row = box.row()
                    row.prop(mcell.initialization, "varying_probability_report")
                    row = box.row()
                    row.prop(mcell.initialization, "progress_report")
                    row = box.row()
                    row.prop(mcell.initialization, "release_event_report")
                    row = box.row()
                    row.prop(mcell.initialization, "molecule_collision_report")
            else:
                row.prop(mcell.initialization, "notifications", icon='TRIA_RIGHT',
                         text="Notifications", emboss=False)

            # Warnings
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.warnings:
                row.prop(mcell.initialization, "warnings", icon='TRIA_DOWN',
                         text="Warnings", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_warnings")
                if self.all_warnings == 'INDIVIDUAL':
                    row = box.row()
                    row.prop(mcell.initialization, "degenerate_polygons")
                    row = box.row()
                    row.prop(mcell.initialization, "missing_surface_orientation")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_diffusion_constant")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_reaction_rate")
                    row = box.row()
                    row.prop(mcell.initialization, "useless_volume_orientation")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "high_reaction_probability")
                    if self.high_reaction_probability != 'IGNORED':
                        row.prop(mcell.initialization,
                                 "high_probability_threshold", slider=True)
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "lifetime_too_short")
                    if self.lifetime_too_short == 'WARNING':
                        row.prop(mcell.initialization, "lifetime_threshold")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "missed_reactions")
                    if self.missed_reactions == 'WARNING':
                        row.prop(mcell.initialization, "missed_reaction_threshold")
            else:
                row.prop(mcell.initialization, "warnings", icon='TRIA_RIGHT',
                         text="Warnings", emboss=False)

            if (self.status != ""):
                row = layout.row()
                row.label(text=self.status, icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


class MCellPartitionsPropertyGroup(bpy.types.PropertyGroup):
    include = BoolProperty(
        name="Include Partitions",
        description="Partitions are a way of speeding up a simulation if used "
                    "properly.",
        default=False)
    recursion_flag = BoolProperty(
        name="Recursion Flag",
        description="Flag to prevent infinite recursion",
        default=False)
    x_start = bpy.props.FloatProperty(
        name="X Start", default=-1, precision=3,
        description="The start of the partitions on the x-axis",
        update=cellblender_operators.transform_x_partition_boundary)
    x_end = bpy.props.FloatProperty(
        name="X End", default=1, precision=3,
        description="The end of the partitions on the x-axis",
        update=cellblender_operators.transform_x_partition_boundary)
    x_step = bpy.props.FloatProperty(
        name="X Step", default=0.02, precision=3,
        description="The distance between partitions on the x-axis",
        update=cellblender_operators.check_x_partition_step)
    y_start = bpy.props.FloatProperty(
        name="Y Start", default=-1, precision=3,
        description="The start of the partitions on the y-axis",
        update=cellblender_operators.transform_y_partition_boundary)
    y_end = bpy.props.FloatProperty(
        name="Y End", default=1, precision=3,
        description="The end of the partitions on the y-axis",
        update=cellblender_operators.transform_y_partition_boundary)
    y_step = bpy.props.FloatProperty(
        name="Y Step", default=0.02, precision=3,
        description="The distance between partitions on the y-axis",
        update=cellblender_operators.check_y_partition_step)
    z_start = bpy.props.FloatProperty(
        name="Z Start", default=-1, precision=3,
        description="The start of the partitions on the z-axis",
        update=cellblender_operators.transform_z_partition_boundary)
    z_end = bpy.props.FloatProperty(
        name="Z End", default=1, precision=3,
        description="The end of the partitions on the z-axis",
        update=cellblender_operators.transform_z_partition_boundary)
    z_step = bpy.props.FloatProperty(
        name="Z Step", default=0.02, precision=3,
        description="The distance between partitions on the z-axis",
        update=cellblender_operators.check_z_partition_step)

    def build_data_model_from_properties ( self, context ):
        print ( "Partitions building Data Model" )
        dm_dict = {}
        dm_dict['data_model_version'] = "DM_2014_10_24_1638"
        dm_dict['include'] = self.include==True
        dm_dict['recursion_flag'] = self.recursion_flag==True
        dm_dict['x_start'] = str(self.x_start)
        dm_dict['x_end'] =   str(self.x_end)
        dm_dict['x_step'] =  str(self.x_step)
        dm_dict['y_start'] = str(self.y_start)
        dm_dict['y_end'] =   str(self.y_end)
        dm_dict['y_step'] =  str(self.y_step)
        dm_dict['x_start'] = str(self.z_start)
        dm_dict['z_end'] =   str(self.z_end)
        dm_dict['z_step'] =  str(self.z_step)
        return dm_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellPartitionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellPartitionsPropertyGroup data model to current version." )
            return None

        return dm





    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellPartitionsPropertyGroup data model to current version." )

        self.include = dm["include"]
        self.recursion_flag = dm["recursion_flag"]
        self.x_start = float(dm["x_start"])
        self.x_end = float(dm["x_end"])
        self.x_step = float(dm["x_step"])
        self.y_start = float(dm["y_start"])
        self.y_end = float(dm["y_end"])
        self.y_step = float(dm["y_step"])
        self.z_start = float(dm["x_start"])
        self.z_end = float(dm["z_end"])
        self.z_step = float(dm["z_step"])

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Partition Properties... no collections to remove." )



    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            layout.prop(self, "include")
            if self.include:
                row = layout.row(align=True)
                row.prop(self, "x_start")
                row.prop(self, "x_end")
                row.prop(self, "x_step")

                row = layout.row(align=True)
                row.prop(self, "y_start")
                row.prop(self, "y_end")
                row.prop(self, "y_step")

                row = layout.row(align=True)
                row.prop(self, "z_start")
                row.prop(self, "z_end")
                row.prop(self, "z_step")

                if mcell.model_objects.object_list:
                    layout.operator("mcell.auto_generate_boundaries",
                                    icon='OUTLINER_OB_LATTICE')
                if not "partitions" in bpy.data.objects:
                    layout.operator("mcell.create_partitions_object",
                                    icon='OUTLINER_OB_LATTICE')
                else:
                    layout.operator("mcell.remove_partitions_object",
                                    icon='OUTLINER_OB_LATTICE')

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



class MCellReactionsPropertyGroup(bpy.types.PropertyGroup):
    reaction_list = CollectionProperty(
        type=MCellReactionProperty, name="Reaction List")
    active_rxn_index = IntProperty(name="Active Reaction Index", default=0)
    reaction_name_list = CollectionProperty(
        type=MCellStringProperty, name="Reaction Name List")
    # plot_command = StringProperty(name="", default="")      # TODO: This may not be needed ... check on it

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction List building Data Model" )
        react_dm = {}
        react_dm['data_model_version'] = "DM_2014_10_24_1638"
        react_list = []
        for r in self.reaction_list:
            react_list.append ( r.build_data_model_from_properties(context) )
        react_dm['reaction_list'] = react_list
        return react_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionsPropertyGroup data model to current version." )
            return None

        if "reaction_list" in dm:
            for item in dm["reaction_list"]:
                if MCellReactionProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionsPropertyGroup data model to current version." )
        while len(self.reaction_list) > 0:
            self.reaction_list.remove(0)
        if "reaction_list" in dm:
            for r in dm["reaction_list"]:
                self.reaction_list.add()
                self.active_rxn_index = len(self.reaction_list)-1
                rxn = self.reaction_list[self.active_rxn_index]
                rxn.init_properties(context.scene.mcell.parameter_system)
                rxn.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Properties..." )
        for item in self.reaction_list:
            item.remove_properties(context)
        self.reaction_list.clear()
        for item in self.reaction_name_list:
            item.remove_properties(context)
        self.reaction_name_list.clear()
        self.active_rxn_index = 0
        print ( "Done removing all Reaction Properties." )


    def draw_layout(self, context, layout):
        # layout = self.layout
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            if mcell.molecules.molecule_list:
                col = row.column()
                col.template_list("MCELL_UL_check_reaction", "define_reactions",
                                  self, "reaction_list",
                                  self, "active_rxn_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.reaction_add", icon='ZOOMIN', text="")
                col.operator("mcell.reaction_remove", icon='ZOOMOUT', text="")
                if len(self.reaction_list) > 0:
                    rxn = self.reaction_list[
                        self.active_rxn_index]

                    helptext = "Reactants\nThe reactants may contain one, two, or three molecule names\n" + \
                               "separated with the plus ('+') sign. Molecules in the reactants\n" + \
                               "list may also contain orientation marks (' or , or ;) as needed."
                    ps.draw_prop_with_help ( layout, "Reactants:", rxn, "reactants", "reactants_show_help", rxn.reactants_show_help, helptext )

                    helptext = "Reaction Type\n  ->   Unidirectional/Irreversible Reaction\n" + \
                               "  <->  Bidirectional/Reversible Reaction"
                    ps.draw_prop_with_help ( layout, "Reaction Type:", rxn, "type", "rxn_type_show_help", rxn.rxn_type_show_help, helptext )

                    helptext = "Products\nThe products list may contain an arbitrary number of\n" + \
                               "molecule names separated with the plus ('+') sign.\n" + \
                               "Molecules may also use NULL to specify no products.\n" + \
                               "Molecules in the products list may also contain orientation\n" + \
                               "marks  (' or , or ;) as needed."
                    ps.draw_prop_with_help ( layout, "Products:", rxn, "products", "products_show_help", rxn.products_show_help, helptext )

                    helptext = "Variable Rate Flag\n" + \
                               "When enabled, the reaction rate is given as a function of time\n" + \
                               "in the form of a 2 column table contained in a text file.\n" + \
                               "The first column in the file specifies the time (in seconds),\n" + \
                               "and the second column contains the rate at that time.\n" + \
                               " \n" + \
                               "When enabled, the normal rate constants will be replaced with\n" + \
                               "a file selection control that will allow you to navigate to the\n" + \
                               "file containing the two columns."
                    ps.draw_prop_with_help ( layout, "Enable Variable Rate", rxn, "variable_rate_switch", "variable_rate_switch_show_help", rxn.variable_rate_switch_show_help, helptext )

                    if rxn.variable_rate_switch:
                        layout.operator("mcell.variable_rate_add", icon='FILESEL')
                        # Do we need these messages in addition to the status
                        # message that appears in the list? I'll leave it for now.
                        if not rxn.variable_rate:
                            layout.label("Rate file not set", icon='UNPINNED')
                        elif not rxn.variable_rate_valid:
                            layout.label("File/Permissions Error: " +
                                rxn.variable_rate, icon='ERROR')
                        else:
                            layout.label(
                                text="Rate File: " + rxn.variable_rate,
                                icon='FILE_TICK')
                    else:
                        #rxn.fwd_rate.draw_in_new_row(layout)
                        rxn.fwd_rate.draw(layout,ps)
                        if rxn.type == "reversible":
                            #rxn.bkwd_rate.draw_in_new_row(layout)
                            rxn.bkwd_rate.draw(layout,ps)

                    helptext = "Reaction Name\nReactions may be named to be referred to by\n" + \
                               "count statements or reaction driven molecule release / placement."
                    ps.draw_prop_with_help ( layout, "Reaction Name:", rxn, "rxn_name", "rxn_name_show_help", rxn.rxn_name_show_help, helptext )

            else:
                row.label(text="Define at least one molecule", icon='ERROR')

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


class MCellSurfaceClassesPropertyGroup(bpy.types.PropertyGroup):
    surf_class_list = CollectionProperty(
        type=MCellSurfaceClassesProperty, name="Surface Classes List")
    active_surf_class_index = IntProperty(
        name="Active Surface Class Index", default=0)
    #surf_class_props_status = StringProperty(name="Status")

    # surf_class_help_title = StringProperty(name="SCT", default="Help on Surface Classes", description="Toggle Showing of Help for Surface Classes." )
    surf_class_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Classes Panel building Data Model" )
        sc_dm = {}
        sc_dm['data_model_version'] = "DM_2014_10_24_1638"
        sc_list = []
        for sc in self.surf_class_list:
            sc_list.append ( sc.build_data_model_from_properties(context) )
        sc_dm['surface_class_list'] = sc_list
        return sc_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassesPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesPropertyGroup data model to current version." )
            return None

        if "surface_class_list" in dm:
            for item in dm["surface_class_list"]:
                if MCellSurfaceClassesProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesPropertyGroup data model to current version." )

        while len(self.surf_class_list) > 0:
            self.surf_class_list.remove(0)
        if "surface_class_list" in dm:
            for s in dm["surface_class_list"]:
                self.surf_class_list.add()
                self.active_surf_class_index = len(self.surf_class_list)-1
                sc = self.surf_class_list[self.active_surf_class_index]
                # sc.init_properties(context.scene.mcell.parameter_system)
                sc.build_properties_from_data_model ( context, s )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Surface Classes Properties..." )
        for item in self.surf_class_list:
            item.remove_properties(context)
        self.surf_class_list.clear()
        self.active_surf_class_index = 0
        print ( "Done removing all Surface Classes Properties." )



    def draw_layout(self, context, layout):
        # layout = self.layout
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            # surf_class = mcell.surface_classes
            ps = mcell.parameter_system

            helptext = "Surface Classes\n" + \
                       " \n" + \
                       "MCell3 allows the user to specify properties of the surfaces\n" + \
                       "of objects. For example, one may wish to specify that a surface\n" + \
                       "does not block the diffusion of molecules. Each type of surface\n" + \
                       "is defined by name, and each surface name must be unique in the\n" + \
                       "simulation and should not match any molecule names.\n" + \
                       " \n" + \
                       "Each Surface Class can associate a number of properties with different molecules:\n" + \
                       " \n" + \
                       "     -  REFLECTIVE = name\n" + \
                       "           If name refers to a volume molecule it is reflected by any surface with\n" + \
                       "           this surface class. This is the default behavior for volume molecules.\n" + \
                       "           If name refers to a surface molecule it is reflected by the border of the\n" + \
                       "           surface with this surface class. Tick marks on the name allow selective\n" + \
                       "           reflection of volume molecules from only the front or back of a surface\n" + \
                       "           or selective reflection of surface molecules with only a certain orientation\n" + \
                       "           from the surface’s border. Using the keyword ALL_MOLECULES\n" + \
                       "           for name has the effect that all volume molecules are reflected by surfaces\n" + \
                       "           with this surface class and all surface molecules are reflected by\n" + \
                       "           the border of the surfaces with this surface class. Using the keyword\n" + \
                       "           ALL_VOLUME_MOLECULES for the name has the effect that all volume\n" + \
                       "           molecules are reflected by surfaces with this surface class. Using\n" + \
                       "           the keyword ALL_SURFACE_MOLECULES has the effect that all\n" + \
                       "           surface molecules are reflected by the border of the surface with this\n" + \
                       "           surface class\n" + \
                       " \n" + \
                       "     -  TRANSPARENT = name\n" + \
                       "           If name refers to a volume molecule it passes through all surfaces with\n" + \
                       "           this surface class. If name refers to a surface molecule it passes through\n" + \
                       "           the border of the surface with this surface class. This is the default\n" + \
                       "           behavior for surface molecules. Tick marks onname allow the creation\n" + \
                       "           of one-way transparent surfaces for volume molecules or oneway\n" + \
                       "           transparent surface borders for surface molecules. To make a\n" + \
                       "           surface with this surface class transparent to all volume molecules,\n" + \
                       "           use ALL_VOLUME_MOLECULES for name. To make a border of the\n" + \
                       "           surface with this surface class transparent to all surface molecules,\n" + \
                       "           use ALL_SURFACE_MOLECULES for name. Using the keyword\n" + \
                       "           ALL_MOLECULES for name has the effect that surfaces with this surface\n" + \
                       "           class are transparent to all volume molecules and borders of the\n" + \
                       "           surfaces with this surface class are transparent to all surface molecules.\n" + \
                       " \n" + \
                       "     -  ABSORPTIVE = name\n" + \
                       "           If name refers to a volume molecule it is destroyed if it touches surfaces\n" + \
                       "           with this surface class. If name refers to a surface molecule it\n" + \
                       "           is destroyed if it touches the border of the surface with this surface\n" + \
                       "           class. Tick marks on name allow destruction from only one side of\n" + \
                       "           the surface for volume molecules or selective destruction for surface\n" + \
                       "           molecules on the surfaces’s border based on their orientation. To make\n" + \
                       "           a surface with this surface class absorptive to all volume molecules,\n" + \
                       "           ALL_VOLUME_MOLECULES can be used for name. To make a border\n" + \
                       "           of the surface with this surface class absorptive to all surface molecules,\n" + \
                       "           ALL_SURFACE_MOLECULES can be used for name. Using the keyword\n" + \
                       "           ALL_MOLECULES has the effect that surfaces with this surface\n" + \
                       "           class are absorptive for all volume molecules and borders of the surfaces\n" + \
                       "           with this surface class are absorptive for all surface molecules.\n" + \
                       " \n" + \
                       "     -  CLAMP_CONCENTRATION = name = value\n" + \
                       "           The molecule called name is destroyed if it touches the surface (as if it\n" + \
                       "           had passed through), and new molecules are created at the surface, as\n" + \
                       "           if molecules had passed through from the other side at a concentration\n" + \
                       "           value (units = M). Orientation marks may be used; in this case, the other\n" + \
                       "           side of the surface is reflective. Note that this command is only used to\n" + \
                       "           set the effective concentration of a volume molecule at a surface; it is not\n" + \
                       "           valid to specify a surface molecule. This command can be abbreviated\n" + \
                       "           as CLAMP_CONC."
            ps.draw_label_with_help ( layout, "Surface Class Help", self, "surf_class_show_help", self.surf_class_show_help, helptext )


            row = layout.row()
            col = row.column()
            # The template_list for the surface classes themselves
            col.template_list("MCELL_UL_check_surface_class", "define_surf_class",
                              self, "surf_class_list", self,
                              "active_surf_class_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.surface_class_add", icon='ZOOMIN', text="")
            col.operator("mcell.surface_class_remove", icon='ZOOMOUT', text="")
            row = layout.row()
            # Show the surface class properties template_list if there is at least
            # a single surface class.
            if self.surf_class_list:
                active_surf_class = self.surf_class_list[
                    self.active_surf_class_index]
                row = layout.row()
                row.prop(active_surf_class, "name")
                row = layout.row()
                row.label(text="%s Properties:" % active_surf_class.name,
                          icon='FACESEL_HLT')
                row = layout.row()
                col = row.column()
                # The template_list for the properties of a surface class.
                # Properties include molecule, orientation, and type of surf class.
                # There can be multiple properties for a single surface class
                col.template_list("MCELL_UL_check_surface_class_props",
                                  "define_surf_class_props", active_surf_class,
                                  "surf_class_props_list", active_surf_class,
                                  "active_surf_class_props_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.surf_class_props_add", icon='ZOOMIN', text="")
                col.operator("mcell.surf_class_props_remove", icon='ZOOMOUT',
                             text="")
                # Show the surface class property fields (molecule, orientation,
                # type) if there is at least a single surface class property.
                if active_surf_class.surf_class_props_list:
                    surf_class_props = active_surf_class.surf_class_props_list[
                        active_surf_class.active_surf_class_props_index]
                    layout.prop_search(surf_class_props, "molecule",
                                       mcell.molecules, "molecule_list",
                                       icon='FORCE_LENNARDJONES')
                    layout.prop(surf_class_props, "surf_class_orient")
                    layout.prop(surf_class_props, "surf_class_type")
                    if (surf_class_props.surf_class_type == 'CLAMP_CONCENTRATION'):
                        layout.prop(surf_class_props, "clamp_value_str")


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



class MCellModSurfRegionsPropertyGroup(bpy.types.PropertyGroup):
    mod_surf_regions_list = CollectionProperty(
        type=MCellModSurfRegionsProperty, name="Assign Surface Class List")
    active_mod_surf_regions_index = IntProperty(
        name="Active Assign Surface Class Index", default=0)

    def build_data_model_from_properties ( self, context ):
        print ( "Assign Surface Class List building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2014_10_24_1638"
        sr_list = []
        for sr in self.mod_surf_regions_list:
            sr_list.append ( sr.build_data_model_from_properties(context) )
        sr_dm['modify_surface_regions_list'] = sr_list
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsPropertyGroup data model to current version." )
            return None

        if "modify_surface_regions_list" in dm:
            for item in dm["modify_surface_regions_list"]:
                if MCellModSurfRegionsProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsPropertyGroup data model to current version." )

        while len(self.mod_surf_regions_list) > 0:
            self.mod_surf_regions_list.remove(0)
        if "modify_surface_regions_list" in dm:
            for s in dm["modify_surface_regions_list"]:
                self.mod_surf_regions_list.add()
                self.active_mod_surf_regions_index = len(self.mod_surf_regions_list)-1
                sr = self.mod_surf_regions_list[self.active_mod_surf_regions_index]
                # sr.init_properties(context.scene.mcell.parameter_system)
                sr.build_properties_from_data_model ( context, s )


    def check_properties_after_building ( self, context ):
        print ( "Implementing check_properties_after_building for " + str(self) )
        for sr in self.mod_surf_regions_list:
            sr.check_properties_after_building(context)

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties ..." )
        for item in self.mod_surf_regions_list:
            item.remove_properties(context)
        self.mod_surf_regions_list.clear()
        self.active_mod_surf_regions_index = 0
        print ( "Done removing all Surface Regions Properties." )


    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            # mod_surf_regions = context.scene.mcell.mod_surf_regions

            row = layout.row()
            if not mcell.surface_classes.surf_class_list:
                row.label(text="Define at least one surface class", icon='ERROR')
            elif not mcell.model_objects.object_list:
                row.label(text="Add a mesh to the Model Objects list",
                          icon='ERROR')
            else:
                col = row.column()
                col.template_list("MCELL_UL_check_mod_surface_regions",
                                  "mod_surf_regions", self,
                                  "mod_surf_regions_list", self,
                                  "active_mod_surf_regions_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.mod_surf_regions_add", icon='ZOOMIN', text="")
                col.operator("mcell.mod_surf_regions_remove", icon='ZOOMOUT',
                             text="")
                if self.mod_surf_regions_list:
                    active_mod_surf_regions = \
                        self.mod_surf_regions_list[
                            self.active_mod_surf_regions_index]
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "surf_class_name",
                                    mcell.surface_classes, "surf_class_list",
                                    icon='FACESEL_HLT')
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "object_name",
                                    mcell.model_objects, "object_list",
                                    icon='MESH_ICOSPHERE')
                    if active_mod_surf_regions.object_name:
                        try:
                            regions = bpy.data.objects[
                                active_mod_surf_regions.object_name].mcell.regions
                            layout.prop_search(active_mod_surf_regions,
                                               "region_name", regions,
                                               "region_list", icon='FACESEL_HLT')
                        except KeyError:
                            pass


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellReleasePatternPropertyGroup(bpy.types.PropertyGroup):
    release_pattern_list = CollectionProperty(
        type=MCellReleasePatternProperty, name="Release Pattern List")
    # Contains release patterns AND reaction names. Used in "Release Placement"
    release_pattern_rxn_name_list = CollectionProperty(
        type=MCellStringProperty,
        name="Release Pattern and Reaction Name List")
    active_release_pattern_index = IntProperty(
        name="Active Release Pattern Index", default=0)

    def build_data_model_from_properties ( self, context ):
        print ( "Release Pattern List building Data Model" )
        rel_pat_dm = {}
        rel_pat_dm['data_model_version'] = "DM_2014_10_24_1638"
        rel_pat_list = []
        for r in self.release_pattern_list:
            rel_pat_list.append ( r.build_data_model_from_properties(context) )
        rel_pat_dm['release_pattern_list'] = rel_pat_list
        return rel_pat_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReleasePatternPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternPropertyGroup data model to current version." )
            return None

        group_name = "release_pattern_list"
        if group_name in dm:
            l = dm[group_name]
            for ri in range(len(l)):
                l[ri] = MCellReleasePatternProperty.upgrade_data_model ( l[ri] )
                if l[ri] == None:
                  return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternPropertyGroup data model to current version." )

        while len(self.release_pattern_list) > 0:
            self.release_pattern_list.remove(0)
        if "release_pattern_list" in dm:
            for r in dm["release_pattern_list"]:
                self.release_pattern_list.add()
                self.active_release_pattern_index = len(self.release_pattern_list)-1
                rp = self.release_pattern_list[self.active_release_pattern_index]
                rp.init_properties(context.scene.mcell.parameter_system)
                rp.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Release Pattern Properties..." )
        for item in self.release_pattern_list:
            item.remove_properties(context)
        self.release_pattern_list.clear()
        for item in self.release_pattern_rxn_name_list:
            item.remove_properties(context)
        self.release_pattern_rxn_name_list.clear()
        self.active_release_pattern_index = 0
        print ( "Done removing all Release Pattern Properties." )


    def draw_layout ( self, context, layout ):
        """ Draw the release "panel" within the layout """
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
          ps = mcell.parameter_system

          row = layout.row()
          col = row.column()
          col.template_list("MCELL_UL_check_release_pattern",
                              "release_pattern", mcell.release_patterns,
                              "release_pattern_list", mcell.release_patterns,
                              "active_release_pattern_index", rows=2)
          col = row.column(align=True)
          col.operator("mcell.release_pattern_add", icon='ZOOMIN', text="")
          col.operator("mcell.release_pattern_remove", icon='ZOOMOUT', text="")
          if mcell.release_patterns.release_pattern_list:
              rel_pattern = mcell.release_patterns.release_pattern_list[
                  mcell.release_patterns.active_release_pattern_index]


              helptext = "This field specifies the name for this release pattern\n" + \
                         " \n" + \
                         "A Release Pattern is a timing pattern (not a spatial pattern).\n" + \
                         " \n" + \
                         "A Release Pattern is generated from these parameters:\n" + \
                         "     -  Release Pattern Delay\n" + \
                         "     -  Release Interval\n" + \
                         "     -  Train Duration\n" + \
                         "     -  Train Interval\n" + \
                         "     -  Number of Trains"
              ps.draw_prop_with_help ( layout, "Pattern Name:", rel_pattern, "name", "name_show_help", rel_pattern.name_show_help, helptext )
              #layout.prop(rel_pattern, "name")


              rel_pattern.delay.draw(layout,ps)
              rel_pattern.release_interval.draw(layout,ps)
              rel_pattern.train_duration.draw(layout,ps)
              rel_pattern.train_interval.draw(layout,ps)
              rel_pattern.number_of_trains.draw(layout,ps)


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



class MCellMoleculeReleasePropertyGroup(bpy.types.PropertyGroup):
    mol_release_list = CollectionProperty(
        type=MCellMoleculeReleaseProperty, name="Molecule Release List")
    active_release_index = IntProperty(name="Active Release Index", default=0)

    def build_data_model_from_properties ( self, context ):
        print ( "Release Site List building Data Model" )
        rel_site_dm = {}
        rel_site_dm['data_model_version'] = "DM_2014_10_24_1638"
        rel_site_list = []
        for r in self.mol_release_list:
            rel_site_list.append ( r.build_data_model_from_properties(context) )
        rel_site_dm['release_site_list'] = rel_site_list
        return rel_site_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeReleasePropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleasePropertyGroup data model to current version." )
            return None

        if "release_site_list" in dm:
            for item in dm["release_site_list"]:
                if MCellMoleculeReleaseProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleasePropertyGroup data model to current version." )

        while len(self.mol_release_list) > 0:
            self.mol_release_list.remove(0)
        if "release_site_list" in dm:
            for r in dm["release_site_list"]:
                self.mol_release_list.add()
                self.active_release_index = len(self.mol_release_list)-1
                rs = self.mol_release_list[self.active_release_index]
                rs.init_properties(context.scene.mcell.parameter_system)
                rs.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Release Properties..." )
        for item in self.mol_release_list:
            item.remove_properties(context)
        self.mol_release_list.clear()
        self.active_release_index = 0
        print ( "Done removing all Molecule Release Properties." )



    def draw_layout ( self, context, layout ):
        """ Draw the release "panel" within the layout """
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            if not mcell.molecules.molecule_list:
                row.label(text="Define at least one molecule", icon='ERROR')
            else:
                row.label(text="Release/Placement Sites:",
                          icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_molecule_release",
                                  "molecule_release", self,
                                  "mol_release_list", self,
                                  "active_release_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.release_site_add", icon='ZOOMIN', text="")
                col.operator("mcell.release_site_remove", icon='ZOOMOUT', text="")

                if len(self.mol_release_list) > 0:
                    rel = self.mol_release_list[self.active_release_index]

                    helptext = "This field specifies the name for this release site\n" + \
                               " \n" + \
                               "A Release Site specifies:\n" + \
                               "     -  A molecule species to be released\n" + \
                               "     -  The location/orientation of the release\n" + \
                               "     -  The probability of the release\n" + \
                               "     -  The quantity to be released\n" + \
                               "     -  The timing of the release\n" + \
                               " \n" + \
                               "Location/Orientation of Release:\n" + \
                               "    Location is controlled by the Release Shape field.\n" + \
                               "    When the shape is a geometric shape, the location is explicit.\n" + \
                               "    When the shape is an Object or Region, the location is implicit.\n" + \
                               "    Initial Orientation is available for Surface Molecules only.\n" + \
                               " \n" + \
                               "Probability of Release:\n" + \
                               "    Probability controls the likelihood that the release will actually happen.\n" + \
                               " \n" + \
                               "Quantity to Release:\n" + \
                               "    The quantity to be released can be:\n" + \
                               "     -  A constant number to be released\n" + \
                               "     -  A random number chosen from a Gaussian distribution\n" + \
                               "     -  A concentration / density\n" + \
                               " \n" + \
                               "Timing of Release:\n" + \
                               "    The timing of releases is controlled by the Release Pattern.\n" + \
                               "    The release pattern field allows selection of:\n" + \
                               "           -  Explicitly defined timing patterns (Release Patterns Panel)\n" + \
                               "           -  Named reactions (Reactions Panel)"
                    ps.draw_prop_with_help ( layout, "Site Name:", rel, "name", "name_show_help", rel.name_show_help, helptext )
                    #layout.prop(rel, "name")

                    helptext = "Molecule to Release\n" + \
                               "Selects the molecule to be released at this site."
                    #layout.prop_search ( rel, "molecule", mcell.molecules, "molecule_list", text="Molecule", icon='FORCE_LENNARDJONES')
                    ps.draw_prop_search_with_help ( layout, "Molecule:", rel, "molecule", mcell.molecules, "molecule_list", "mol_show_help", rel.mol_show_help, helptext )

                    if rel.molecule in mcell.molecules.molecule_list:
                        if mcell.molecules.molecule_list[rel.molecule].type == '2D':
                            #layout.prop(rel, "orient")
                            ps.draw_prop_with_help ( layout, "Initial Orientation:", rel, "orient", "orient_show_help", rel.orient_show_help,
                                "Initial Orientation\n" + \
                                "Determines how surface molecules are orginally placed in the surface:\n" + \
                                "  Top Front\n" + \
                                "  Top Back\n" + \
                                "  Mixed\n" )

                    helptext = "Release Site Shape\n" + \
                               "Defines the shape of the release site. A shape may be:\n" + \
                               "  A geometric cubic region.\n" + \
                               "  A geometric spherical region.\n" + \
                               "  A geometric spherical shell region.\n" + \
                               "  A CellBlender/MCell Object or Region\n" + \
                               " \n" + \
                               "When the release site shape is one of the predefined geometric\n" + \
                               "shapes, CellBlender will provide fields for its location and size.\n" + \
                               " \n" + \
                               "When the release site shape is \"Object/Region\", CellBlender will expect\n" + \
                               "an MCell specification for one of the Objects or Regions defined in\n" + \
                               "your current model (via the \"Model Objects\" panel). For example, if\n" + \
                               "you have an object named \"Cube\", you would enter that name in the\n" + \
                               "Object/Region field. If you've defined a surface region named \"top\"\n" + \
                               "on your Cube, then you would specify that surface as \"Cube[top]\"."
                    ps.draw_prop_with_help ( layout, "Release Shape:", rel, "shape", "shape_show_help", rel.shape_show_help, helptext )

                    if ((rel.shape == 'CUBIC') | (rel.shape == 'SPHERICAL') |
                            (rel.shape == 'SPHERICAL_SHELL')):
                        #layout.prop(rel, "location")
                        rel.location_x.draw(layout,ps)
                        rel.location_y.draw(layout,ps)
                        rel.location_z.draw(layout,ps)
                        rel.diameter.draw(layout,ps)

                    if rel.shape == 'OBJECT':
                        helptext = "Release Site Object/Region\n" + \
                                   "This field requires an MCell-compatible object expression or region\n" + \
                                   "expression for one of the objects or regions defined in your current\n" + \
                                   "CellBlender model (via the \"Model Objects\" panel). For example, if\n" + \
                                   "you have an object named \"Cube\", you would enter that name in the\n" + \
                                   "Object/Region field. If you've defined a surface region named \"top\"\n" + \
                                   "on your Cube, then you would specify that surface as \"Cube[top]\"."
                        ps.draw_prop_with_help ( layout, "Object/Region:", rel, "object_expr", "object_expr_show_help", rel.object_expr_show_help, helptext )

                    rel.probability.draw(layout,ps)
            
                    helptext = "Quantity Type\n" + \
                               "Defines the meaning of the Quantity:\n" + \
                               "  Constant Number\n" + \
                               "  Gaussian Number\n" + \
                               "  Concentration / Density\n" + \
                               " \n" + \
                               "The value of this field determines the interpretation of the\n" + \
                               "Quantity to Release field below."
                    ps.draw_prop_with_help ( layout, "Quantity Type:", rel, "quantity_type", "quantity_type_show_help", rel.quantity_type_show_help, helptext )

                    rel.quantity.draw(layout,ps)

                    if rel.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                        rel.stddev.draw(layout,ps)

                    # We use release_pattern_rxn_name_list instead of
                    # release_pattern_list here, because we want to be able to
                    # assign either reaction names or release patterns to this
                    # field. This parallels exactly how it works in MCell.
                    #
                    #layout.prop_search(rel, "pattern", mcell.release_patterns,  # mcell.release_patterns is of type MCellReleasePatternPropertyGroup
                    #                   "release_pattern_rxn_name_list",  
                    #                   icon='FORCE_LENNARDJONES')

                    helptext = "Release Pattern\n" + \
                               "Selects a release pattern to follow or a named reaction to trigger releases.\n" + \
                               " \n" + \
                               "The Release Pattern generally controls the timing of release events.\n" + \
                               "This is either done with explicit timing parameters defined in the\n" + \
                               "Release Patterns panel or implicit timing by specifying reactions that\n" + \
                               "trigger releases. When reactions are used, the release generally happens\n" + \
                               "at a location relative to the reaction itself."
                    #layout.prop_search ( rel, "molecule", mcell.molecules, "molecule_list", text="Molecule", icon='FORCE_LENNARDJONES')
                    ps.draw_prop_search_with_help ( layout, "Release Pattern:", rel, "pattern", mcell.release_patterns, "release_pattern_rxn_name_list", "rel_pattern_show_help", rel.rel_pattern_show_help, helptext, 'TIME' )




    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


class MCellModelObjectsProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Object Name", update=cellblender_operators.check_model_object)
    status = StringProperty(name="Status")
    """
    def build_data_model_from_properties ( self, context ):
        print ( "Model Object building Data Model" )
        mo_dm = {}
        mo_dm['data_model_version'] = "DM_2014_10_24_1638"
        mo_dm['name'] = self.name
        return mo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModelObjectsProperty Data Model" )
        print ( "-------------->>>>>>>>>>>>>>>>>>>>> NOT IMPLEMENTED YET!!!" )
        return dm



    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsProperty data model to current version." )

        print ( "Assigning Model Object " + dm['name'] )
        self.name = dm["name"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    """

    def remove_properties ( self, context ):
        print ( "Removing all Model Objects Properties... no collections to remove." )



import mathutils

class MCellModelObjectsPropertyGroup(bpy.types.PropertyGroup):
    object_list = CollectionProperty(
        type=MCellModelObjectsProperty, name="Object List")
    active_obj_index = IntProperty(name="Active Object Index", default=0)
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def remove_properties ( self, context ):
        print ( "Removing all Model Object List Properties..." )
        for item in self.object_list:
            item.remove_properties(context)
        self.object_list.clear()
        self.active_obj_index = 0
        print ( "Done removing all Model Object List Properties." )


    def draw_layout ( self, context, layout ):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            if context.active_object != None:
                row = layout.row()
                row.prop ( context.active_object, "name", text="Active:" )

            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_model_objects", "model_objects",
                              self, "object_list",
                              self, "active_obj_index", rows=2)
            col = row.column(align=True)
#           col.active = (len(context.selected_objects) == 1)
            col.operator("mcell.model_objects_add", icon='ZOOMIN', text="")
            col.operator("mcell.model_objects_remove", icon='ZOOMOUT', text="")
            
            if len(self.object_list) > 0:
                box = layout.box()
                row = box.row()
                if not self.show_display:
                    row.prop(self, "show_display", icon='TRIA_RIGHT',
                             text=str(self.object_list[self.active_obj_index].name)+" Display Options", emboss=False)
                else:
                    row.prop(self, "show_display", icon='TRIA_DOWN',
                             text=str(self.object_list[self.active_obj_index].name)+" Display Options", emboss=False)

                    row = box.row()
                    row.prop ( context.scene.objects[self.object_list[self.active_obj_index].name], "draw_type" )
                    row = box.row()
                    row.prop ( context.scene.objects[self.object_list[self.active_obj_index].name], "show_transparent" )

#           row = layout.row()
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_include", text="Include")
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_select", text="Select")
#           sub.operator("mcell.model_objects_deselect", text="Deselect")

            """
            row = layout.row()
            row.label(text="Object Color:", icon='COLOR')
            
            active = None
            for o in self.object_list.keys():
                # print ( "Object: " + o )
                row = layout.row()
                if bpy.context.scene.objects[o] == bpy.context.scene.objects.active:
                    active = bpy.context.scene.objects[o]
                    row.label(text=o, icon='TRIA_RIGHT')
                else:
                    row.label(text=o, icon='DOT')

            if active == None:
                row = layout.row()
                row.label(text="No CellBlender object is active", icon='DOT')
            else:
                row = layout.row()
                row.label ( icon='DOT', text="  Object " + active.name + " is active and has " +
                    str(len(active.material_slots)) + " material slots" )
            """


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


    def build_data_model_from_properties ( self, context ):
    
        print ( "Model Objects List building Data Model" )
        mo_dm = {}
        mo_dm['data_model_version'] = "DM_2014_10_24_1638"
        mo_list = []
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                if scene_object.mcell.include:
                    print ( "MCell object: " + scene_object.name )
                    mo_list.append ( { "name": scene_object.name } )
        mo_dm['model_object_list'] = mo_list
        return mo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModelObjectsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Note that model object list is represented in two places:
        #   context.scene.mcell.model_objects.object_list[] - stores the name
        #   context.scene.objects[].mcell.include - boolean is true for model objects
        # This code updates both locations based on the data model

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsPropertyGroup data model to current version." )
        
        # Remove all model objects in the list
        while len(self.object_list) > 0:
            self.object_list.remove(0)
            
        # Create a list of model object names from the Data Model
        mo_list = []
        if "model_object_list" in dm:
          for m in dm["model_object_list"]:
              print ( "Data model contains " + m["name"] )
              self.object_list.add()
              self.active_obj_index = len(self.object_list)-1
              mo = self.object_list[self.active_obj_index]
              #mo.init_properties(context.scene.mcell.parameter_system)
              #mo.build_properties_from_data_model ( context, m )
              mo.name = m['name']
              mo_list.append ( m["name"] )

        # Use the list of Data Model names to set flags of all objects
        for k,o in context.scene.objects.items():
            if k in mo_list:
                o.mcell.include = True
            else:
                o.mcell.include = False

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



    def build_data_model_materials_from_materials ( self, context ):
        print ( "Model Objects List building Materials for Data Model" )
        mat_dm = {}
        mat_dict = {}

        # First build the list of materials from all objects
        for data_object in context.scene.objects:
            if data_object.type == 'MESH':
                if data_object.mcell.include:
                    print ( "Saving Materials for: " + data_object.name )
                    for mat_slot in data_object.material_slots:
                        if not mat_slot.name in mat_dict:
                            # This is a new material, so add it
                            mat = bpy.data.materials[mat_slot.name]
                            print ( "  Adding " + mat_slot.name )
                            mat_obj = {}
                            mat_obj['diffuse_color'] = {
                                'r': mat.diffuse_color.r,
                                'g': mat.diffuse_color.g,
                                'b': mat.diffuse_color.b,
                                'a': mat.alpha }
                            # Need to set:
                            #  mat.use_transparency
                            #  obj.show_transparent
                            mat_dict[mat_slot.name] = mat_obj;
        mat_dm['material_dict'] = mat_dict
        return mat_dm


    def build_materials_from_data_model_materials ( self, context, dm ):

        # Delete any materials with conflicting names and then rebuild all

        # Start by creating a list of named materials in the data model
        mat_names = dm['material_dict'].keys()
        print ( "Material names = " + str(mat_names) )
        
        # Delete all materials with identical names
        for mat_name in mat_names:
            if mat_name in bpy.data.materials:
                bpy.data.materials.remove ( bpy.data.materials[mat_name] )
        
        # Now add all the new materials
        
        for mat_name in mat_names:
            new_mat = bpy.data.materials.new(mat_name)
            c = dm['material_dict'][mat_name]['diffuse_color']
            new_mat.diffuse_color = ( c['r'], c['g'], c['b'] )
            new_mat.alpha = c['a']
            if new_mat.alpha < 1.0:
                new_mat.use_transparency = True


    def build_data_model_geometry_from_mesh ( self, context ):
        print ( "Model Objects List building Geometry for Data Model" )
        g_dm = {}
        g_list = []

        for data_object in context.scene.objects:
            if data_object.type == 'MESH':
                if data_object.mcell.include:
                    print ( "MCell object: " + data_object.name )

                    g_obj = {}
                    
                    saved_hide_status = data_object.hide
                    data_object.hide = False

                    context.scene.objects.active = data_object
                    bpy.ops.object.mode_set(mode='OBJECT')

                    g_obj['name'] = data_object.name
                    
                    loc_x = data_object.location.x
                    loc_y = data_object.location.y
                    loc_z = data_object.location.z

                    g_obj['location'] = [loc_x, loc_y, loc_z]
                    
                    if len(data_object.data.materials) > 0:
                        g_obj['material_names'] = []
                        for mat in data_object.data.materials:
                            g_obj['material_names'].append ( mat.name )
                            # g_obj['material_name'] = data_object.data.materials[0].name
                    
                    v_list = []
                    mesh = data_object.data
                    matrix = data_object.matrix_world
                    vertices = mesh.vertices
                    for v in vertices:
                        t_vec = matrix * v.co
                        v_list.append ( [t_vec.x-loc_x, t_vec.y-loc_y, t_vec.z-loc_z] )
                    g_obj['vertex_list'] = v_list

                    f_list = []
                    faces = mesh.polygons
                    for f in faces:
                        f_list.append ( [f.vertices[0], f.vertices[1], f.vertices[2]] )
                    g_obj['element_connections'] = f_list
                    
                    if len(data_object.data.materials) > 1:
                        # This object has multiple materials, so store the material index for each face
                        mi_list = []
                        for f in faces:
                            mi_list.append ( f.material_index )
                        g_obj['element_material_indices'] = mi_list

                    regions = data_object.mcell.get_regions_dictionary(data_object)
                    if regions:
                        r_list = []

                        region_names = [k for k in regions.keys()]
                        region_names.sort()
                        for region_name in region_names:
                            rgn = {}
                            rgn['name'] = region_name
                            rgn['include_elements'] = regions[region_name]
                            r_list.append ( rgn )
                        g_obj['define_surface_regions'] = r_list

                    # restore proper object visibility state
                    data_object.hide = saved_hide_status

                    g_list.append ( g_obj )

        g_dm['object_list'] = g_list
        return g_dm


    def delete_all_mesh_objects ( self, context ):
        bpy.ops.object.select_all(action='DESELECT')
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                print ( "Deleting Mesh object: " + scene_object.name )
                scene_object.hide = False
                scene_object.select = True
                bpy.ops.object.delete()
                # TODO Need to delete the mesh for this object as well!!!


    def build_mesh_from_data_model_geometry ( self, context, dm ):
            
        # Delete any objects with conflicting names and then rebuild all

        print ( "Model Objects List building Mesh Objects from Data Model Geometry" )
        
        # Start by creating a list of named objects in the data model
        model_names = [ o['name'] for o in dm['object_list'] ]
        print ( "Model names = " + str(model_names) )

        # Delete all objects with identical names to model objects in the data model
        bpy.ops.object.select_all(action='DESELECT')
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                print ( "Mesh object: " + scene_object.name )
                if scene_object.name in model_names:
                    print ( "  will be recreated from the data model ... deleting." )
                    # TODO preserve hidden/shown status
                    scene_object.hide = False
                    scene_object.select = True
                    bpy.ops.object.delete()
                    # TODO Need to delete the mesh for this object as well!!!

        # Now create all the object meshes from the data model
        for model_object in dm['object_list']:

            vertices = []
            for vertex in model_object['vertex_list']:
                vertices.append ( mathutils.Vector((vertex[0],vertex[1],vertex[2])) )
            faces = []
            for face_element in model_object['element_connections']:
                faces.append ( face_element )
            new_mesh = bpy.data.meshes.new ( model_object['name'] )
            new_mesh.from_pydata ( vertices, [], faces )
            new_mesh.update()
            new_obj = bpy.data.objects.new ( model_object['name'], new_mesh )
            if 'location' in model_object:
                new_obj.location = mathutils.Vector((model_object['location'][0],model_object['location'][1],model_object['location'][2]))

            # Add the materials to the object
            if 'material_names' in model_object:
                print ( "Object " + model_object['name'] + " has material names" )
                for mat_name in model_object['material_names']:
                    new_obj.data.materials.append ( bpy.data.materials[mat_name] )
                    if bpy.data.materials[mat_name].alpha < 1:
                        new_obj.show_transparent = True
                if 'element_material_indices' in model_object:
                    print ( "Object " + model_object['name'] + " has material indices" )
                    faces = new_obj.data.polygons
                    dm_count = len(model_object['element_material_indices'])
                    index = 0
                    for f in faces:
                        f.material_index = model_object['element_material_indices'][index % dm_count]
                        index += 1

            context.scene.objects.link ( new_obj )
            bpy.ops.object.select_all ( action = "DESELECT" )
            new_obj.select = True
            context.scene.objects.active = new_obj
            

            # Add the surface regions to new_obj.mcell
            
            if model_object.get('define_surface_regions'):
                for rgn in model_object['define_surface_regions']:
                    print ( "  Building region[" + rgn['name'] + "]" )
                    new_obj.mcell.regions.add_region_by_name ( context, rgn['name'] )
                    reg = new_obj.mcell.regions.region_list[rgn['name']]
                    reg.set_region_faces ( new_mesh, set(rgn['include_elements']) )



class MCellVizOutputPropertyGroup(bpy.types.PropertyGroup):
    active_mol_viz_index = IntProperty(
        name="Active Molecule Viz Index", default=0)
    all_iterations = bpy.props.BoolProperty(
        name="All Iterations",
        description="Include all iterations for visualization.", default=True)
    start = bpy.props.IntProperty(
        name="Start", description="Starting iteration", default=0, min=0)
    end = bpy.props.IntProperty(
        name="End", description="Ending iteration", default=1, min=1)
    step = bpy.props.IntProperty(
        name="Step", description="Output viz data every n iterations.",
        default=1, min=1)
    export_all = BoolProperty(
        name="Export All",
        description="Visualize all molecules",
        default=True)

    def build_data_model_from_properties ( self, context ):
        print ( "Viz Output building Data Model" )
        vo_dm = {}
        vo_dm['data_model_version'] = "DM_2014_10_24_1638"
        vo_dm['all_iterations'] = self.all_iterations
        vo_dm['start'] = str(self.start)
        vo_dm['end'] = str(self.end)
        vo_dm['step'] = str(self.step)
        vo_dm['export_all'] = self.export_all
        return vo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellVizOutputPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
        
        self.all_iterations = dm["all_iterations"]
        self.start = int(dm["start"])
        self.end = int(dm["end"])
        self.step = int(dm["step"])
        self.export_all = dm["export_all"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Visualization Output Properties... no collections to remove." )


    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            if mcell.molecules.molecule_list:
                row.label(text="Molecules To Visualize:",
                          icon='FORCE_LENNARDJONES')
                row.prop(self, "export_all")
                layout.template_list("MCELL_UL_visualization_export_list",
                                     "viz_export", mcell.molecules,
                                     "molecule_list", self,
                                     "active_mol_viz_index", rows=2)
                layout.prop(self, "all_iterations")
                if self.all_iterations is False:
                    row = layout.row(align=True)
                    row.prop(self, "start")
                    row.prop(self, "end")
                    row.prop(self, "step")
            else:
                row.label(text="Define at least one molecule", icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellReactionOutputProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Reaction Output", update=cellblender_operators.check_rxn_output)
    molecule_name = StringProperty(
        name="Molecule",
        description="Count the selected molecule.",
        update=cellblender_operators.check_rxn_output)
    reaction_name = StringProperty(
        name="Reaction",
        description="Count the selected reaction.",
        update=cellblender_operators.check_rxn_output)
    object_name = StringProperty(
        name="Object", update=cellblender_operators.check_rxn_output)
    region_name = StringProperty(
        name="Region", update=cellblender_operators.check_rxn_output)
    count_location_enum = [
        ('World', "World", ""),
        ('Object', "Object", ""),
        ('Region', "Region", "")]
    count_location = bpy.props.EnumProperty(
        items=count_location_enum, name="Count Location",
        description="Count all molecules in the selected location.",
        update=cellblender_operators.check_rxn_output)
    rxn_or_mol_enum = [
        ('Reaction', "Reaction", ""),
        ('Molecule', "Molecule", "")]
    rxn_or_mol = bpy.props.EnumProperty(
        items=rxn_or_mol_enum, name="Count Reaction or Molecule",
        default='Molecule',
        description="Select between counting a reaction or molecule.",
        update=cellblender_operators.check_rxn_output)
    # plot_command = StringProperty(name="Command")  # , update=cellblender_operators.check_rxn_output)
    status = StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2014_10_24_1638"
        ro_dm['name'] = self.name
        ro_dm['molecule_name'] = self.molecule_name
        ro_dm['reaction_name'] = self.reaction_name
        ro_dm['object_name'] = self.object_name
        ro_dm['region_name'] = self.region_name
        ro_dm['count_location'] = self.count_location
        ro_dm['rxn_or_mol'] = self.rxn_or_mol
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
        self.name = dm["name"]
        self.molecule_name = dm["molecule_name"]
        self.reaction_name = dm["reaction_name"]
        self.object_name = dm["object_name"]
        self.region_name = dm["region_name"]
        self.count_location = dm["count_location"]
        self.rxn_or_mol = dm["rxn_or_mol"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Output Properties... no collections to remove." )




import cellblender

#JJT:temporary class
class MCellReactionOutputPropertyTemp(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Reaction Output")
    molecule_name = StringProperty(
        name="Molecule",
        description="Count the selected molecules.")


class MCellReactionOutputPropertyGroup(bpy.types.PropertyGroup):
    #JJT: temporary list made to hold complex expressions from imported files
    temp_index = IntProperty(
        name="Temp Output Index", default=0)
    complex_rxn_output_list = CollectionProperty(
        type=MCellReactionOutputPropertyTemp,name="Temporary output list")
    
    rxn_step = PointerProperty ( name="Step",
        type=parameter_system.Parameter_Reference )
    active_rxn_output_index = IntProperty(
        name="Active Reaction Output Index", default=0)
    rxn_output_list = CollectionProperty(
        type=MCellReactionOutputProperty, name="Reaction Output List")
    plot_layout_enum = [
        (' page ', "Separate Page for each Plot", ""),
        (' plot ', "One Page, Multiple Plots", ""),
        (' ',      "One Page, One Plot", "")]
    plot_layout = bpy.props.EnumProperty ( 
        items=plot_layout_enum, name="", 
        description="Select the Page and Plot Layout",
        default=' plot ' )
    plot_legend_enum = [
        ('x', "No Legend", ""),
        ('0', "Legend with Automatic Placement", ""),
        ('1', "Legend in Upper Right", ""),
        ('2', "Legend in Upper Left", ""),
        ('3', "Legend in Lower Left", ""),
        ('4', "Legend in Lower Right", ""),
        # ('5', "Legend on Right", ""), # This appears to duplicate option 7
        ('6', "Legend in Center Left", ""),
        ('7', "Legend in Center Right", ""),
        ('8', "Legend in Lower Center", ""),
        ('9', "Legend in Upper Center", ""),
        ('10', "Legend in Center", "")]
    plot_legend = bpy.props.EnumProperty ( 
        items=plot_legend_enum, name="", 
        description="Select the Legend Display and Placement",
        default='0' )
    combine_seeds = BoolProperty(
        name="Combine Seeds",
        description="Combine all seeds onto the same plot.",
        default=True)
    mol_colors = BoolProperty(
        name="Molecule Colors",
        description="Use Molecule Colors for line colors.",
        default=False)

    def init_properties ( self, parameter_system ):
        self.rxn_step.init_ref (
            parameter_system, "Rxn_Output_Step", user_name="Step", 
            user_expr="", user_units="", user_descr="Step\n"
            "Output reaction data every t seconds.") 

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output Panel building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2014_10_24_1638"
        ro_dm['rxn_step'] = self.rxn_step.get_expr()
        ro_dm['plot_layout'] = self.plot_layout
        ro_dm['plot_legend'] = self.plot_legend
        ro_dm['combine_seeds'] = self.combine_seeds
        ro_dm['mol_colors'] = self.mol_colors
        ro_list = []
        for ro in self.rxn_output_list:
            ro_list.append ( ro.build_data_model_from_properties(context) )
        ro_dm['reaction_output_list'] = ro_list
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputPropertyGroup Data Model" )
        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['rxn_step'] = ""
            dm['data_model_version'] = "DM_2015_05_15_1214"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_05_15_1214":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
            return None

        if "reaction_output_list" in dm:
            for item in dm["reaction_output_list"]:
                if MCellReactionOutputProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_05_15_1214":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
        self.init_properties(context.scene.mcell.parameter_system)
        self.plot_layout = dm["plot_layout"]
        self.plot_legend = dm["plot_legend"]
        self.rxn_step.set_expr ( dm["rxn_step"] )
        self.combine_seeds = dm["combine_seeds"]
        self.mol_colors = dm["mol_colors"]
        while len(self.rxn_output_list) > 0:
            self.rxn_output_list.remove(0)
        if "reaction_output_list" in dm:
            for r in dm["reaction_output_list"]:
                self.rxn_output_list.add()
                self.active_rxn_output_index = len(self.rxn_output_list)-1
                ro = self.rxn_output_list[self.active_rxn_output_index]
                # ro.init_properties(context.scene.mcell.parameter_system)
                ro.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Output Properties..." )
        for item in self.complex_rxn_output_list:
            item.remove_properties(context)
        self.complex_rxn_output_list.clear()
        self.active_rxn_output_index = 0
        for item in self.rxn_output_list:
            item.remove_properties(context)
        self.rxn_output_list.clear()
        print ( "Done removing all Reaction Output Properties." )



    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell
        ps = mcell.parameter_system

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            self.rxn_step.draw(layout,ps)
            row = layout.row()
            if mcell.molecules.molecule_list:
                col = row.column()
                col.template_list("MCELL_UL_check_reaction_output_settings",
                                  "reaction_output", self,
                                  "rxn_output_list", self,
                                  "active_rxn_output_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.rxn_output_add", icon='ZOOMIN', text="")
                col.operator("mcell.rxn_output_remove", icon='ZOOMOUT', text="")
                # Show molecule, object, and region options only if there is at
                # least one count statement.
                if self.rxn_output_list:
                    rxn_output = self.rxn_output_list[
                        self.active_rxn_output_index]
                    layout.prop(rxn_output, "rxn_or_mol", expand=True)
                    if rxn_output.rxn_or_mol == 'Molecule':
                        layout.prop_search(
                            rxn_output, "molecule_name", mcell.molecules,
                            "molecule_list", icon='FORCE_LENNARDJONES')
                    else:
                        layout.prop_search(
                            rxn_output, "reaction_name", mcell.reactions,
                            "reaction_name_list", icon='FORCE_LENNARDJONES')
                    layout.prop(rxn_output, "count_location", expand=True)
                    # Show the object selector if Object or Region is selected
                    if rxn_output.count_location != "World":
                        layout.prop_search(
                            rxn_output, "object_name", mcell.model_objects,
                            "object_list", icon='MESH_ICOSPHERE')
                        if (rxn_output.object_name and
                                (rxn_output.count_location == "Region")):
                            try:
                                regions = bpy.data.objects[
                                    rxn_output.object_name].mcell.regions
                                layout.prop_search(rxn_output, "region_name",
                                                   regions, "region_list",
                                                   icon='FACESEL_HLT')
                            except KeyError:
                                pass

                    layout.separator()
                    layout.separator()

                    row = layout.row()
                    row.label(text="Plot Reaction Data:",
                              icon='FORCE_LENNARDJONES')

                    row = layout.row()

                    col = row.column()
                    col.prop(self, "plot_layout")

                    col = row.column()
                    col.prop(self, "combine_seeds")

                    row = layout.row()

                    col = row.column()
                    col.prop(self, "plot_legend")

                    col = row.column()
                    col.prop(self, "mol_colors")


                    row = layout.row()
                    button_num = 0
                    num_columns = len(cellblender.cellblender_info[
                        'cellblender_plotting_modules'])
                    if num_columns > 3:
                        num_columns = 2
                    for plot_module in cellblender.cellblender_info[
                            'cellblender_plotting_modules']:
                        mod_name = plot_module.get_name()
                        if (button_num % num_columns) == 0:
                            button_num = 0
                            row = layout.row()
                        col = row.column()
                        col.operator("mcell.plot_rxn_output_generic",
                                     text=mod_name).plotter_button_label = mod_name
                        button_num = button_num + 1

            else:
                row.label(text="Define at least one molecule", icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellMoleculeGlyphsPropertyGroup(bpy.types.PropertyGroup):
    glyph_lib = os.path.join(
        os.path.dirname(__file__), "glyph_library.blend/Mesh/")
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
    glyph = EnumProperty(items=glyph_enum, name="Molecule Shapes")
    show_glyph = BoolProperty(name="Show Glyphs",description="Show Glyphs ... can cause slowness!!",default=True)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Glyph Properties... no collections to remove." )



class MCellMeshalyzerPropertyGroup(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name")
    vertices = IntProperty(name="Vertices", default=0)
    edges = IntProperty(name="Edges", default=0)
    faces = IntProperty(name="Faces", default=0)
    watertight = StringProperty(name="Watertight")
    manifold = StringProperty(name="Manifold")
    normal_status = StringProperty(name="Surface Normals")
    area = FloatProperty(name="Area", default=0)
    volume = FloatProperty(name="Volume", default=0)
    sav_ratio = FloatProperty(name="SA/V Ratio", default=0)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Meshalyzer Properties... no collections to remove." )



class MCellObjectSelectorPropertyGroup(bpy.types.PropertyGroup):
    filter = StringProperty(
        name="Object Name Filter",
        description="Enter a regular expression for object names.")

    def remove_properties ( self, context ):
        print ( "Removing all Object Selector Properties... no collections to remove." )




class PP_OT_init_mcell(bpy.types.Operator):
    bl_idname = "mcell.init_cellblender"
    bl_label = "Init CellBlender"
    bl_description = "Initialize CellBlender"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print ( "Initializing CellBlender" )
        mcell = context.scene.mcell
        mcell.init_properties()
        mcell.rxn_output.init_properties(mcell.parameter_system)
        print ( "CellBlender has been initialized" )
        return {'FINISHED'}




def show_old_scene_panels ( show=False ):
    if show:
        print ( "Showing the Old CellBlender panels in the Scene tab" )
        try:
            bpy.utils.register_class(cellblender_panels.MCELL_PT_cellblender_preferences)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_project_settings)
            # bpy.utils.register_class(cellblender_panels.MCELL_PT_run_simulation)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_run_simulation_queue)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_viz_results)
            bpy.utils.register_class(parameter_system.MCELL_PT_parameter_system)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_model_objects)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_partitions)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_initialization)
            bpy.utils.register_class(cellblender_molecules.MCELL_PT_define_molecules)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_define_reactions)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_define_surface_classes)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_mod_surface_regions)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_release_pattern)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_molecule_release)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_reaction_output_settings)
            bpy.utils.register_class(cellblender_panels.MCELL_PT_visualization_output_settings)
        except:
            pass
    else:
        print ( "Hiding the Old CellBlender panels in the Scene tab" )
        try:
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_cellblender_preferences)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_project_settings)
            # bpy.utils.unregister_class(cellblender_panels.MCELL_PT_run_simulation)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_run_simulation_queue)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_viz_results)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_model_objects)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_partitions)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_initialization)
            bpy.utils.unregister_class(parameter_system.MCELL_PT_parameter_system)
            bpy.utils.unregister_class(cellblender_molecules.MCELL_PT_define_molecules)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_reactions)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_surface_classes)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_mod_surface_regions)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_release_pattern)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_molecule_release)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_reaction_output_settings)
            bpy.utils.unregister_class(cellblender_panels.MCELL_PT_visualization_output_settings)
        except:
            pass



def show_hide_tool_panel ( show=True ):
    if show:
        print ( "Showing CellBlender panel in the Tool tab" )
        try:
            bpy.utils.register_class(MCELL_PT_main_panel)
        except:
            pass
    else:
        print ( "Hiding the CellBlender panel in the Tool tab" )
        try:
            bpy.utils.unregister_class(MCELL_PT_main_panel)
        except:
            pass


def show_hide_scene_panel ( show=True ):
    if show:
        print ( "Showing the CellBlender panel in the Scene tab" )
        try:
            bpy.utils.register_class(MCELL_PT_main_scene_panel)
        except:
            pass
    else:
        print ( "Hiding the CellBlender panel in the Scene tab" )
        try:
            bpy.utils.unregister_class(MCELL_PT_main_scene_panel)
        except:
            pass






    

# My panel class (which happens to augment 'Scene' properties)
class MCELL_PT_main_panel(bpy.types.Panel):
    # bl_idname = "SCENE_PT_CB_MU_APP"
    bl_label = "  CellBlender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "CellBlender"
    
    @classmethod
    def poll(cls, context):
        return (context.scene is not None)


    def draw_header(self, context):
        # LOOK HERE!! This is where the icon is actually included in the panel layout!
        # The icon() method takes the image data-block in and returns an integer that
        # gets passed to the 'icon_value' argument of your label/prop constructor or 
        # within a UIList subclass
        img = bpy.data.images.get('cellblender_icon')
        #could load multiple images and animate the icon too.
        #icons = [img for img in bpy.data.images if hasattr(img, "icon")]
        if img is not None:
            icon = self.layout.icon(img)
            self.layout.label(text="", icon_value=icon)

    def draw(self, context):
        context.scene.mcell.cellblender_main_panel.draw_self(context,self.layout)

'''
class MCELL_PT_main_scene_panel(bpy.types.Panel):
    bl_label = "CellBlender Scene"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        # LOOK HERE!! This is where the icon is actually included in the panel layout!
        # The icon() method takes the image data-block in and returns an integer that
        # gets passed to the 'icon_value' argument of your label/prop constructor or 
        # within a UIList subclass
        img = bpy.data.images.get('cellblender_icon')
        #could load multiple images and animate the icon too.
        #icons = [img for img in bpy.data.images if hasattr(img, "icon")]
        if img is not None:
            icon = self.layout.icon(img)
            self.layout.label(text="", icon_value=icon)

    def draw(self, context):
        context.scene.mcell.cellblender_main_panel.draw_self(context,self.layout)
'''


# load_pre callback
@persistent
def report_load_pre(dummy):
    # Note that load_pre may not be called when the startup file is loaded for earlier versions of Blender (somewhere before 2.73)
    print ( "===================================================================================" )
    print ( "================================= Load Pre called =================================" )
    print ( "===================================================================================" )


# Load scene callback
@persistent
def scene_loaded(dummy):
    # Icon
    #print("ADDON_ICON")
    icon_files = { 'cellblender_icon': 'cellblender_icon.png', 'mol_u': 'mol_unsel.png', 'mol_s': 'mol_sel.png', 'reaction_u': 'reactions_unsel.png', 'reaction_s': 'reactions_sel.png' }
    for icon_name in icon_files:
        fname = icon_files[icon_name]
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname,'icons')
        icon = bpy.data.images.get(icon_name)
        if icon is None:
            img = bpy.data.images.load(os.path.join(dirname, fname))
            img.name = icon_name
            img.use_alpha = True
            img.user_clear() # Won't get saved into .blend files
        # remove scene_update handler
        elif "icon" not in icon.keys():
            icon["icon"] = True
            for f in bpy.app.handlers.scene_update_pre:
                if f.__name__ == "scene_loaded":
                    print("Removing scene_loaded handler now that icons are loaded")
                    bpy.app.handlers.scene_update_pre.remove(f)




class CBM_OT_refresh_operator(bpy.types.Operator):
    bl_idname = "cbm.refresh_operator"
    bl_label = "Refresh"
    bl_description = ("Refresh Molecules from Simulation")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Refreshing/Reloading the Molecules..." )
        bpy.ops.mcell.read_viz_data()
        return {'FINISHED'}



def select_callback ( self, context ):
    self.select_callback(context)


class CellBlenderMainPanelPropertyGroup(bpy.types.PropertyGroup):

    preferences_select = BoolProperty ( name="pref_sel", description="Preferences", default=False, subtype='NONE', update=select_callback)
    settings_select = BoolProperty ( name="set_sel", description="Project Settings", default=False, subtype='NONE', update=select_callback)
    parameters_select = BoolProperty ( name="par_sel", description="Model Parameters", default=False, subtype='NONE', update=select_callback)
    reaction_select = BoolProperty ( name="react_sel", description="Reactions", default=False, subtype='NONE', update=select_callback)
    molecule_select = BoolProperty ( name="mol_sel", description="Molecules", default=False, subtype='NONE', update=select_callback)
    placement_select = BoolProperty ( name="place_sel", description="Molecule Placement", default=False, subtype='NONE', update=select_callback)
    objects_select = BoolProperty ( name="obj_sel", description="Model Objects", default=False, subtype='NONE', update=select_callback)
    surf_classes_select = BoolProperty ( name="surfc_sel", description="Surface Classes", default=False, subtype='NONE', update=select_callback)
    surf_regions_select = BoolProperty ( name="surfr_sel", description="Assign Surface Classes", default=False, subtype='NONE', update=select_callback)
    rel_patterns_select = BoolProperty ( name="relpat_sel", description="Release Patterns", default=False, subtype='NONE', update=select_callback)
    partitions_select = BoolProperty ( name="part_sel", description="Partitions", default=False, subtype='NONE', update=select_callback)
    init_select = BoolProperty ( name="init_sel", description="Run Simulation", default=False, subtype='NONE', update=select_callback)
    # run_select = BoolProperty ( name="run_sel", description="Old Run Simulation", default=False, subtype='NONE', update=select_callback)
    graph_select = BoolProperty ( name="graph_sel", description="Plot Output Settings", default=False, subtype='NONE', update=select_callback)
    mol_viz_select = BoolProperty ( name="mviz_sel", description="Visual Output Settings", default=False, subtype='NONE', update=select_callback)
    viz_select = BoolProperty ( name="viz_sel", description="Visual Output Settings", default=False, subtype='NONE', update=select_callback)
    reload_viz = BoolProperty ( name="reload", description="Reload Simulation Data", default=False, subtype='NONE', update=select_callback)
    
    select_multiple = BoolProperty ( name="multiple", description="Show Multiple Panels", default=False, subtype='NONE', update=select_callback)
    
    last_state = BoolVectorProperty ( size=22 ) # Keeps track of previous button state to detect transitions
    
    dummy_bool = BoolProperty( name="DummyBool", default=True )
    dummy_string = StringProperty( name="DummyString", default=" " )
    dummy_float = FloatProperty ( name="DummyFloat", default=12.34 )

    def remove_properties ( self, context ):
        print ( "Removing all CellBlender Main Panel Properties... no collections to remove." )

    
    def select_callback ( self, context ):
        """
        Desired Logic:
          pin_state 0->1 with no others selected:
            Show All
          pin_state 0->1 with just 1 selected:
            No Change (continue showing the currently selected, and allow more)
          pin_state 0->1 with more than 1 selected ... should NOT happen because only one panel should show when pin_state is 0
            Illegal state
          pin_state 1->0 :
            Hide all panels ... always
            
        """
        prop_keys = [ 'preferences_select', 'settings_select', 'parameters_select', 'reaction_select', 'molecule_select', 'placement_select', 'objects_select', 'surf_classes_select', 'surf_regions_select', 'rel_patterns_select', 'partitions_select', 'init_select', 'graph_select', 'viz_select', 'select_multiple' ]
        
        pin_state = False
        
        """
        try:
            pin_state = (self['select_multiple'] != 0)
        except:
            pass
        old_pin_state = (self.last_state[prop_keys.index('select_multiple')] != 0)
        """

        if self.get('select_multiple'):
            pin_state = (self['select_multiple'] != 0)
        old_pin_state = (self.last_state[prop_keys.index('select_multiple')] != 0)
        
        print ( "Select Called without try/except with pin state:" + str(pin_state) + ", and old pin state = " + str(old_pin_state) )

        if (old_pin_state and (not pin_state)):
            # Pin has been removed, so hide all panels ... always
            # print ("Hiding all")
            for k in prop_keys:
                self.last_state[prop_keys.index(k)] = False
                self[k] = 0
                """
                try:
                    self.last_state[prop_keys.index(k)] = False
                    self[k] = 0
                except:
                    pass
                """
            self.last_state[prop_keys.index('select_multiple')] = False
            
        elif ((not old_pin_state) and pin_state):
            # Pin has been pushed
            # Find out how many panels are currently shown
            num_panels_shown = 0
            for k in prop_keys:
                if k != 'select_multiple':
                    if self.get(k):
                        if self[k] != 0:
                            num_panels_shown += 1
                    """
                    try:
                        if self[k] != 0:
                            num_panels_shown += 1
                    except:
                        pass
                    """
            # Check for case where no panels are showing
            if num_panels_shown == 0:
                # print ("Showing all")
                # Show all panels
                for k in prop_keys:
                    if self.get(k):
                        self[k] = 1
                        self.last_state[prop_keys.index(k)] = False
                    """
                    try:
                        self[k] = 1
                        self.last_state[prop_keys.index(k)] = False
                    except:
                        pass
                    """
        
            self.last_state[prop_keys.index('select_multiple')] = True
        
        else:
            # Pin state has not changed, so assume some other button has been toggled

            # Go through and find which one has changed to positive, setting all others to 0 if not pin_state
            for k in prop_keys:
                if self.get(k):
                    # print ( "Key " + k + " is " + str(self[k]) + ", Last state = " + str(self.last_state[index]) )
                    if (self[k] != 0) and (self.last_state[prop_keys.index(k)] == False):
                        self.last_state[prop_keys.index(k)] = True
                    else:
                        if not pin_state:
                            self.last_state[prop_keys.index(k)] = False
                            self[k] = 0
                """
                try:
                    if (self[k] != 0) and (self.last_state[prop_keys.index(k)] == False):
                        self.last_state[prop_keys.index(k)] = True
                    else:
                        if not pin_state:
                            self.last_state[prop_keys.index(k)] = False
                            self[k] = 0
                except:
                    pass
                """


    def draw_self (self, context, layout):
        # print ( "Top of CellBlenderMainPanelPropertyGroup.draw_self" )

        #######################################################################################
        """
        #######################################################################################
        def draw_panel_code_worked_out_with_Tom_on_Feb_18_2015:
            if not scn.mcell.get('CB_ID'):
                # This .blend file has no CellBlender data or was created with CellBlender RC3
                if not scn.mcell['initialized']:
                    # This .blend file has no CellBlender data (never saved with CellBlender enabled)
                    display "Initialize"
                else:
                    # This is a CellBlender RC3 or RC4 file
                    display "Update"
            else:
                # This is a CellBlender .blend file >= 1.0
                CB_ID = scn.mcell['CB_ID']
                if CB_ID != cb.cellblender_source_info['cb_src_sha1']
                    display "Update"
                else:
                    display normal panel
        #######################################################################################
        """
        #######################################################################################

        mcell = context.scene.mcell
        
        if not mcell.get ( 'saved_by_source_id' ):
            # This .blend file has no CellBlender data at all or was created with CellBlender RC3 / RC4
            if not mcell.initialized:  # if not mcell['initialized']:
                # This .blend file has no CellBlender data (never saved with CellBlender enabled)
                mcell.draw_uninitialized ( layout )
            else:
                # This is a CellBlender RC3 or RC4 file so draw the RC3/4 upgrade button
                row = layout.row()
                row.label ( "Blend File version (RC3/4) doesn't match CellBlender version", icon='ERROR' )
                row = layout.row()
                row.operator ( "mcell.upgraderc3", text="Upgrade RC3/4 Blend File to Current Version", icon='RADIO' )
        else:
            CB_ID = mcell['saved_by_source_id']
            source_id = cellblender.cellblender_info['cellblender_source_sha1']

            if CB_ID != source_id:
                # This is a CellBlender file >= 1.0, so draw the normal upgrade button
                row = layout.row()
                row.label ( "Blend File version doesn't match CellBlender version", icon='ERROR' )
                row = layout.row()
                row.operator ( "mcell.upgrade", text="Upgrade Blend File to Current Version", icon='RADIO' )

            else:
                # The versions matched, so draw the normal panels

                if not mcell.cellblender_preferences.use_long_menus:

                    # Draw all the selection buttons in a single row

                    real_row = layout.row()
                    split = real_row.split(0.9)
                    col = split.column()

                    #row = layout.row(align=True)
                    row = col.row(align=True)

                    if mcell.cellblender_preferences.show_button_num[0]: row.prop ( self, "preferences_select", icon='PREFERENCES' )
                    if mcell.cellblender_preferences.show_button_num[1]: row.prop ( self, "settings_select", icon='SETTINGS' )
                    if mcell.cellblender_preferences.show_button_num[2]: row.prop ( self, "parameters_select", icon='SEQ_SEQUENCER' )

                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons to check on drawing speed problem
                        if mcell.cellblender_preferences.show_button_num[3]: row.prop ( self, "molecule_select", icon='FORCE_LENNARDJONES' )
                        if mcell.cellblender_preferences.show_button_num[4]: row.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT' )
                    else:
                        if self.molecule_select:
                            if mcell.cellblender_preferences.show_button_num[3]: molecule_img_sel = bpy.data.images.get('mol_s')
                            if mcell.cellblender_preferences.show_button_num[3]: mol_s = layout.icon(molecule_img_sel)
                            if mcell.cellblender_preferences.show_button_num[3]: row.prop ( self, "molecule_select", icon_value=mol_s )
                        else:
                            if mcell.cellblender_preferences.show_button_num[3]: molecule_img_unsel = bpy.data.images.get('mol_u')
                            if mcell.cellblender_preferences.show_button_num[3]: mol_u = layout.icon(molecule_img_unsel)
                            if mcell.cellblender_preferences.show_button_num[3]: row.prop ( self, "molecule_select", icon_value=mol_u )

                        if self.reaction_select:
                            if mcell.cellblender_preferences.show_button_num[4]: react_img_sel = bpy.data.images.get('reaction_s')
                            if mcell.cellblender_preferences.show_button_num[4]: reaction_s = layout.icon(react_img_sel)
                            if mcell.cellblender_preferences.show_button_num[4]: row.prop ( self, "reaction_select", icon_value=reaction_s )
                        else:
                            if mcell.cellblender_preferences.show_button_num[4]: react_img_unsel = bpy.data.images.get('reaction_u')
                            if mcell.cellblender_preferences.show_button_num[4]: reaction_u = layout.icon(react_img_unsel)
                            if mcell.cellblender_preferences.show_button_num[4]: row.prop ( self, "reaction_select", icon_value=reaction_u )

                    if mcell.cellblender_preferences.show_button_num[5]: row.prop ( self, "placement_select", icon='GROUP_VERTEX' )
                    if mcell.cellblender_preferences.show_button_num[6]: row.prop ( self, "rel_patterns_select", icon='TIME' )
                    if mcell.cellblender_preferences.show_button_num[7]: row.prop ( self, "objects_select", icon='MESH_ICOSPHERE' )  # Or 'MESH_CUBE'
                    if mcell.cellblender_preferences.show_button_num[8]: row.prop ( self, "surf_classes_select", icon='FACESEL_HLT' )
                    if mcell.cellblender_preferences.show_button_num[9]: row.prop ( self, "surf_regions_select", icon='SNAP_FACE' )
                    if mcell.cellblender_preferences.show_button_num[10]: row.prop ( self, "partitions_select", icon='GRID' )
                    if mcell.cellblender_preferences.show_button_num[11]: row.prop ( self, "graph_select", icon='FCURVE' )
                    if mcell.cellblender_preferences.show_button_num[12]: row.prop ( self, "viz_select", icon='SEQUENCE' )
                    if mcell.cellblender_preferences.show_button_num[13]: row.prop ( self, "init_select", icon='COLOR_RED' )

                    col = split.column()
                    row = col.row()

                    if self.select_multiple:
                        if mcell.cellblender_preferences.show_button_num[0]: row.prop ( self, "select_multiple", icon='PINNED' )
                    else:
                        if mcell.cellblender_preferences.show_button_num[0]: row.prop ( self, "select_multiple", icon='UNPINNED' )

                    # Use an operator rather than a property to make it an action button
                    # row.prop ( self, "reload_viz", icon='FILE_REFRESH' )
                    if mcell.cellblender_preferences.show_button_num[0]: row.operator ( "cbm.refresh_operator",text="",icon='FILE_REFRESH')
                        
                else:


                    current_marker = "Before drawing any buttons"

                    # Draw all the selection buttons with labels in 2 columns:

                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "preferences_select", icon='PREFERENCES', text="Preferences" )
                    bcol = brow.column()
                    bcol.prop ( self, "settings_select", icon='SETTINGS', text="Settings" )

                    current_marker = "After drawing preferences_select"

                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "parameters_select", icon='SEQ_SEQUENCER', text="Parameters" )
                    bcol = brow.column()
                    
                    current_marker = "After drawing parameters_select"


                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons to check on drawing speed problem
                        bcol.prop ( self, "molecule_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                        brow = layout.row()
                        bcol = brow.column()
                        bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                    else:
                        # Use custom icons for some buttons
                        if self.molecule_select:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                            else:
                                molecule_img_sel = bpy.data.images.get('mol_s')
                                mol_s = layout.icon(molecule_img_sel)
                                bcol.prop ( self, "molecule_select", icon_value=mol_s, text="Molecules" )
                        else:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                            else:
                                molecule_img_unsel = bpy.data.images.get('mol_u')
                                mol_u = layout.icon(molecule_img_unsel)
                                bcol.prop ( self, "molecule_select", icon_value=mol_u, text="Molecules" )

                        brow = layout.row()
                        bcol = brow.column()
                        if self.reaction_select:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                            else:
                                react_img_sel = bpy.data.images.get('reaction_s')
                                reaction_s = layout.icon(react_img_sel)
                                bcol.prop ( self, "reaction_select", icon_value=reaction_s, text="Reactions" )
                        else:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                            else:
                                react_img_unsel = bpy.data.images.get('reaction_u')
                                reaction_u = layout.icon(react_img_unsel)
                                bcol.prop ( self, "reaction_select", icon_value=reaction_u, text="Reactions" )


                    current_marker = "After drawing molecules and reactions"


                    ## Drawing is fast when exiting here

                    bcol = brow.column()
                    bcol.prop ( self, "placement_select", icon='GROUP_VERTEX', text=" Molecule Placement" )

                    current_marker = "After drawing placement_select"
                    ## Drawing is a little slower when exiting here


                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "rel_patterns_select", icon='TIME', text="Release Patterns" )
                    bcol = brow.column()
                    bcol.prop ( self, "objects_select", icon='MESH_ICOSPHERE', text="Model Objects" )

                    current_marker = "After drawing release patterns"

                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "surf_classes_select", icon='FACESEL_HLT', text="Surface Classes" )
                    bcol = brow.column()
                    bcol.prop ( self, "surf_regions_select", icon='SNAP_FACE', text="Assign Surface Classes" )
                    

                    current_marker = "After drawing surface selections"


                    ## Drawing is slower when exiting here


                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "partitions_select", icon='GRID', text="Partitions" )
                    bcol = brow.column()
                    bcol.prop ( self, "graph_select", icon='FCURVE', text="Plot Output Settings" )


                    current_marker = "After drawing partition and graph buttons"


                    brow = layout.row()
                    bcol = brow.column()
                    bcol.prop ( self, "viz_select", icon='SEQUENCE', text="Visualization Settings" )
                    bcol = brow.column()
                    bcol.prop ( self, "init_select", icon='COLOR_RED', text="Run Simulation" )


                    current_marker = "After drawing the viz and run buttons buttons"




                    ############################################
                    ############################################
                    #print ( "Exiting ... " + current_marker )
                    #return
                    ############################################
                    ############################################



                    brow = layout.row()
                    bcol = brow.column()
                    if self.select_multiple:
                        bcol.prop ( self, "select_multiple", icon='PINNED', text="Show All / Multiple" )
                    else:
                        bcol.prop ( self, "select_multiple", icon='UNPINNED', text="Show All / Multiple" )
                    bcol = brow.column()
                    bcol.operator ( "cbm.refresh_operator",icon='FILE_REFRESH', text="Reload Visualization Data")



                current_marker = "After drawing all buttons"



                # Draw each panel only if it is selected

                if self.preferences_select:
                    layout.box() # Use as a separator
                    layout.label ( "Preferences", icon='PREFERENCES' )
                    context.scene.mcell.cellblender_preferences.draw_layout ( context, layout )

                if self.settings_select:
                    layout.box() # Use as a separator
                    layout.label ( "Project Settings", icon='SETTINGS' )
                    context.scene.mcell.project_settings.draw_layout ( context, layout )

                if self.parameters_select:
                    layout.box() # Use as a separator
                    layout.label ( "Model Parameters", icon='SEQ_SEQUENCER' )
                    context.scene.mcell.parameter_system.draw_layout ( context, layout )

                if self.molecule_select:
                    layout.box() # Use as a separator
                    layout.label(text="Defined Molecules", icon='FORCE_LENNARDJONES')
                    context.scene.mcell.molecules.draw_layout ( context, layout )

                if self.reaction_select:
                    layout.box() # Use as a separator
                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons to check on drawing speed problem
                        layout.label ( "Defined Reactions", icon='ARROW_LEFTRIGHT' )
                    else:
                        react_img_sel = bpy.data.images.get('reaction_s')
                        reaction_s = layout.icon(react_img_sel)
                        layout.label ( "Defined Reactions", icon_value=reaction_s )
                    context.scene.mcell.reactions.draw_layout ( context, layout )

                if self.placement_select:
                    layout.box() # Use as a separator
                    layout.label ( "Molecule Release/Placement", icon='GROUP_VERTEX' )
                    context.scene.mcell.release_sites.draw_layout ( context, layout )

                if self.rel_patterns_select:
                    layout.box() # Use as a separator
                    layout.label ( "Release Patterns", icon='TIME' )
                    context.scene.mcell.release_patterns.draw_layout ( context, layout )

                if self.objects_select:
                    layout.box() # Use as a separator
                    layout.label ( "Model Objects", icon='MESH_ICOSPHERE' )  # Or 'MESH_CUBE'
                    context.scene.mcell.model_objects.draw_layout ( context, layout )
                    # layout.box() # Use as a separator
                    if context.object != None:
                        context.object.mcell.regions.draw_layout(context, layout)

                if self.surf_classes_select:
                    layout.box() # Use as a separator
                    layout.label ( "Defined Surface Classes", icon='FACESEL_HLT' )
                    context.scene.mcell.surface_classes.draw_layout ( context, layout )

                if self.surf_regions_select:
                    layout.box() # Use as a separator
                    layout.label ( "Assigned Surface Classes", icon='SNAP_FACE' )
                    context.scene.mcell.mod_surf_regions.draw_layout ( context, layout )

                if self.partitions_select:
                    layout.box() # Use as a separator
                    layout.label ( "Partitions", icon='GRID' )
                    context.scene.mcell.partitions.draw_layout ( context, layout )

                if self.graph_select:
                    layout.box() # Use as a separator
                    layout.label ( "Reaction Data Output", icon='FCURVE' )
                    context.scene.mcell.rxn_output.draw_layout ( context, layout )

                #if self.mol_viz_select:
                #    layout.box()
                #    layout.label ( "Visualization Output Settings", icon='SEQUENCE' )
                #    context.scene.mcell.mol_viz.draw_layout ( context, layout )
                    
                if self.viz_select:
                    layout.box()
                    layout.label ( "Visualization", icon='SEQUENCE' )
                    context.scene.mcell.viz_output.draw_layout ( context, layout )
                    context.scene.mcell.mol_viz.draw_layout ( context, layout )
                    
                if self.init_select:
                    layout.box() # Use as a separator
                    layout.label ( "Run Simulation", icon='COLOR_RED' )
                    context.scene.mcell.initialization.draw_layout ( context, layout )
                    
                #if self.run_select:
                #    layout.box() # Use as a separator
                #    layout.label ( "Run Simulation", icon='COLOR_RED' )
                #    context.scene.mcell.run_simulation.draw_layout ( context, layout )
                    
                # The reload_viz button refreshes rather than brings up a panel
                #if self.reload_viz:
                #    layout.box()
                #    layout.label ( "Reload Simulation Data", icon='FILE_REFRESH' )
        # print ( "Bottom of CellBlenderMainPanelPropertyGroup.draw_self" )


import pickle

# Main MCell (CellBlender) Properties Class:
def refresh_source_id_callback ( self, context ):
    # This is a boolean which defaults to false. So clicking it should change it to true which triggers this callback:
    if self.refresh_source_id:
        print ("Updating ID")
        if not ('cellblender_source_id_from_file' in cellblender.cellblender_info):
            # Save the version that was read from the file
            cellblender.cellblender_info.update ( { "cellblender_source_id_from_file": cellblender.cellblender_info['cellblender_source_sha1'] } )
        # Compute the new version
        cellblender.cellblender_source_info.identify_source_version(os.path.dirname(__file__),verbose=True)
        # Check to see if they match
        if cellblender.cellblender_info['cellblender_source_sha1'] == cellblender.cellblender_info['cellblender_source_id_from_file']:
            # They still match, so remove the "from file" version from the info to let the panel know that there's no longer a mismatch:
            cellblender.cellblender_info.pop('cellblender_source_id_from_file')
        # Setting this to false will redraw the panel
        self.refresh_source_id = False



class MCellPropertyGroup(bpy.types.PropertyGroup):
    initialized = BoolProperty(name="Initialized", default=False)
    # versions_match = BoolProperty ( default=True )

    cellblender_version = StringProperty(name="CellBlender Version", default="0")
    cellblender_addon_id = StringProperty(name="CellBlender Addon ID", default="0")
    cellblender_data_model_version = StringProperty(name="CellBlender Data Model Version", default="0")
    refresh_source_id = BoolProperty ( default=False, description="Recompute the Source ID from actual files", update=refresh_source_id_callback )
    #cellblender_source_hash = StringProperty(
    #    name="CellBlender Source Hash", default="unknown")


    cellblender_main_panel = PointerProperty(
        type=CellBlenderMainPanelPropertyGroup,
        name="CellBlender Main Panel")


    cellblender_preferences = PointerProperty(
        type=CellBlenderPreferencesPropertyGroup,
        name="CellBlender Preferences")
    project_settings = PointerProperty(
        type=MCellProjectPropertyGroup, name="CellBlender Project Settings")
    export_project = PointerProperty(
        type=MCellExportProjectPropertyGroup, name="Export Simulation")
    run_simulation = PointerProperty(
        type=MCellRunSimulationPropertyGroup, name="Run Simulation")
    mol_viz = PointerProperty(
        type=MCellMolVizPropertyGroup, name="Mol Viz Settings")
    initialization = PointerProperty(
        type=MCellInitializationPropertyGroup, name="Model Initialization")
    partitions = bpy.props.PointerProperty(
        type=MCellPartitionsPropertyGroup, name="Partitions")
    ############# DB: added for parameter import from BNG, SBML models####
    #parameters = PointerProperty(
    #    type=MCellParametersPropertyGroup, name="Defined Parameters")
    parameter_system = PointerProperty(
        type=parameter_system.ParameterSystemPropertyGroup, name="Parameter System")
    molecules = PointerProperty(
        type=cellblender_molecules.MCellMoleculesListProperty, name="Defined Molecules")
    reactions = PointerProperty(
        type=MCellReactionsPropertyGroup, name="Defined Reactions")
    surface_classes = PointerProperty(
        type=MCellSurfaceClassesPropertyGroup, name="Defined Surface Classes")
    mod_surf_regions = PointerProperty(
        type=MCellModSurfRegionsPropertyGroup, name="Assign Surface Classes")
    release_patterns = PointerProperty(
        type=MCellReleasePatternPropertyGroup, name="Defined Release Patterns")
    release_sites = PointerProperty(
        type=MCellMoleculeReleasePropertyGroup, name="Defined Release Sites")
    model_objects = PointerProperty(
        type=MCellModelObjectsPropertyGroup, name="Instantiated Objects")
    viz_output = PointerProperty(
        type=MCellVizOutputPropertyGroup, name="Viz Output")
    rxn_output = PointerProperty(
        type=MCellReactionOutputPropertyGroup, name="Reaction Output")
    meshalyzer = PointerProperty(
        type=MCellMeshalyzerPropertyGroup, name="CellBlender Project Settings")
    object_selector = PointerProperty(
        type=MCellObjectSelectorPropertyGroup,
        name="CellBlender Project Settings")
    molecule_glyphs = PointerProperty(
        type=MCellMoleculeGlyphsPropertyGroup, name="Molecule Shapes")

    #scratch_settings = PointerProperty(
    #    type=MCellScratchPropertyGroup, name="CellBlender Scratch Settings")

    def init_properties ( self ):
        self.cellblender_version = "0.1.54"
        self.cellblender_addon_id = "0"
        self.cellblender_data_model_version = "0"
        self.parameter_system.init_properties()
        self.initialization.init_properties ( self.parameter_system )
        self.molecules.init_properties ( self.parameter_system )
        # Don't forget to update the "saved_by_source_id" to match the current version of the addon
        self['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
        self.initialized = True


    def remove_properties ( self, context ):
        print ( "Removing all MCell Properties..." )
        self.molecule_glyphs.remove_properties(context)
        self.object_selector.remove_properties(context)
        self.meshalyzer.remove_properties(context)
        self.rxn_output.remove_properties(context)
        self.viz_output.remove_properties(context)
        self.model_objects.remove_properties(context)
        self.release_sites.remove_properties(context)
        self.release_patterns.remove_properties(context)
        self.mod_surf_regions.remove_properties(context)
        self.surface_classes.remove_properties(context)
        self.reactions.remove_properties(context)
        self.molecules.remove_properties(context)
        self.partitions.remove_properties(context)
        self.initialization.remove_properties(context)
        self.mol_viz.remove_properties(context)
        self.run_simulation.remove_properties(context)
        self.export_project.remove_properties(context)
        self.project_settings.remove_properties(context)
        self.cellblender_preferences.remove_properties(context)
        self.cellblender_main_panel.remove_properties(context)
        self.parameter_system.remove_properties(context)
        print ( "Done removing all MCell Properties." )



    def build_data_model_from_properties ( self, context, geometry=False ):
        print ( "build_data_model_from_properties: Constructing a data_model dictionary from current properties" )
        dm = {}
        dm['data_model_version'] = "DM_2014_10_24_1638"
        dm['blender_version'] = [v for v in bpy.app.version]
        dm['cellblender_version'] = self.cellblender_version
        #dm['cellblender_source_hash'] = self.cellblender_source_hash
        dm['cellblender_source_sha1'] = cellblender.cellblender_info["cellblender_source_sha1"]
        if 'api_version' in self:
            dm['api_version'] = self['api_version']
        else:
            dm['api_version'] = 0
        dm['parameter_system'] = self.parameter_system.build_data_model_from_properties(context)
        dm['initialization'] = self.initialization.build_data_model_from_properties(context)
        dm['initialization']['partitions'] = self.partitions.build_data_model_from_properties(context)
        dm['define_molecules'] = self.molecules.build_data_model_from_properties(context)
        dm['define_reactions'] = self.reactions.build_data_model_from_properties(context)
        dm['release_sites'] = self.release_sites.build_data_model_from_properties(context)
        dm['define_release_patterns'] = self.release_patterns.build_data_model_from_properties(context)
        dm['define_surface_classes'] = self.surface_classes.build_data_model_from_properties(context)
        dm['modify_surface_regions'] = self.mod_surf_regions.build_data_model_from_properties(context)
        dm['model_objects'] = self.model_objects.build_data_model_from_properties(context)
        dm['viz_output'] = self.viz_output.build_data_model_from_properties(context)
        dm['simulation_control'] = self.run_simulation.build_data_model_from_properties(context)
        dm['mol_viz'] = self.mol_viz.build_data_model_from_properties(context)
        dm['reaction_data_output'] = self.rxn_output.build_data_model_from_properties(context)
        if geometry:
            print ( "Adding Geometry to Data Model" )
            dm['geometrical_objects'] = self.model_objects.build_data_model_geometry_from_mesh(context)
            dm['materials'] = self.model_objects.build_data_model_materials_from_materials(context)
        return dm



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellPropertyGroup Data Model" )
        # cellblender.data_model.dump_data_model ( "Dump of dm passed to MCellPropertyGroup.upgrade_data_model", dm )

        # Perform any upgrades to this top level data model

        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellPropertyGroup data model to current version." )
            return None

        # Perform any upgrades to all components within this top level data model

        group_name = "parameter_system"
        if group_name in dm:
            dm[group_name] = parameter_system.ParameterSystemPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "initialization"
        if group_name in dm:
            dm[group_name] = MCellInitializationPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

            subgroup_name = "partitions"
            if subgroup_name in dm[group_name]:
                dm[group_name][subgroup_name] = MCellPartitionsPropertyGroup.upgrade_data_model ( dm[group_name] )
                if dm[group_name][subgroup_name] == None:
                    return None

        group_name = "define_molecules"
        if group_name in dm:
            dm[group_name] = cellblender_molecules.MCellMoleculesListProperty.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_reactions"
        if group_name in dm:
            dm[group_name] = MCellReactionsPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "release_sites"
        if group_name in dm:
            dm[group_name] = MCellMoleculeReleasePropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_release_patterns"
        if group_name in dm:
            dm[group_name] = MCellReleasePatternPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_surface_classes"
        if group_name in dm:
            dm[group_name] = MCellSurfaceClassesPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "modify_surface_regions"
        if group_name in dm:
            dm[group_name] = MCellModSurfRegionsPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "model_objects"
        if group_name in dm:
            dm[group_name] = MCellModelObjectsPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "viz_output"
        if group_name in dm:
            dm[group_name] = MCellVizOutputPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "simulation_control"
        if group_name in dm:
            dm[group_name] = MCellRunSimulationPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "mol_viz"
        if group_name in dm:
            dm[group_name] = MCellMolVizPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "reaction_data_output"
        if group_name in dm:
            dm[group_name] = MCellReactionOutputPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        return dm



    def build_properties_from_data_model ( self, context, dm, geometry=False ):
        print ( "build_properties_from_data_model: Data Model Keys = " + str(dm.keys()) )

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellPropertyGroup data model to current version." )

        # Remove the existing MCell Property Tree
        self.remove_properties(context)

        # Now convert the updated Data Model into CellBlender Properties
        print ( "Overwriting properites based on data in the data model dictionary" )
        self.init_properties()
        if "parameter_system" in dm:
            print ( "Overwriting the parameter_system properties" )
            self.parameter_system.build_properties_from_data_model ( context, dm["parameter_system"] )
        
        if "initialization" in dm:
            print ( "Overwriting the initialization properties" )
            self.initialization.build_properties_from_data_model ( context, dm["initialization"] )
            if "partitions" in dm:
                print ( "Overwriting the partitions properties" )
                self.partitions.build_properties_from_data_model ( context, dm["initialization"]["partitions"] )
        if "define_molecules" in dm:
            print ( "Overwriting the define_molecules properties" )
            self.molecules.build_properties_from_data_model ( context, dm["define_molecules"] )
        if "define_reactions" in dm:
            print ( "Overwriting the define_reactions properties" )
            self.reactions.build_properties_from_data_model ( context, dm["define_reactions"] )
        if "release_sites" in dm:
            print ( "Overwriting the release_sites properties" )
            self.release_sites.build_properties_from_data_model ( context, dm["release_sites"] )
        if "define_release_patterns" in dm:
            print ( "Overwriting the define_release_patterns properties" )
            self.release_patterns.build_properties_from_data_model ( context, dm["define_release_patterns"] )
        if "define_surface_classes" in dm:
            print ( "Overwriting the define_surface_classes properties" )
            self.surface_classes.build_properties_from_data_model ( context, dm["define_surface_classes"] )
        # Move below model objects?
        #if "modify_surface_regions" in dm:
        #    print ( "Overwriting the modify_surface_regions properties" )
        #    self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
        if geometry:
            print ( "Deleting all mesh objects" )
            self.model_objects.delete_all_mesh_objects(context)
            if "materials" in dm:
                print ( "Overwriting the materials properties" )
                print ( "Building Materials from Data Model Materials" )
                self.model_objects.build_materials_from_data_model_materials ( context, dm['materials'] )
            if "geometrical_objects" in dm:
                print ( "Overwriting the geometrical_objects properties" )
                print ( "Building Mesh Geometry from Data Model Geometry" )
                self.model_objects.build_mesh_from_data_model_geometry ( context, dm["geometrical_objects"] )
            print ( "Not fully implemented yet!!!!" )
        if "model_objects" in dm:
            print ( "Overwriting the model_objects properties" )
            self.model_objects.build_properties_from_data_model ( context, dm["model_objects"] )
        if "modify_surface_regions" in dm:
            print ( "Overwriting the modify_surface_regions properties" )
            self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
        if "viz_output" in dm:
            print ( "Overwriting the viz_output properties" )
            self.viz_output.build_properties_from_data_model ( context, dm["viz_output"] )
        if "mol_viz" in dm:
            print ( "Overwriting the mol_viz properties" )
            self.mol_viz.build_properties_from_data_model ( context, dm["mol_viz"] )
        # This is commented out because it's not clear how it should work yet...
        #if "simulation_control" in dm:
        #    print ( "Overwriting the simulation_control properties" )
        #    self.run_simulation.build_properties_from_data_model ( context, dm["simulation_control"] )
        if "reaction_data_output" in dm:
            print ( "Overwriting the reaction_data_output properties" )
            self.rxn_output.build_properties_from_data_model ( context, dm["reaction_data_output"] )


        # Now call the various "check" routines to clean up any unresolved references
        print ( "Checking the initialization and partitions properties" )
        self.initialization.check_properties_after_building ( context )
        self.partitions.check_properties_after_building ( context )
        print ( "Checking the define_molecules properties" )
        self.molecules.check_properties_after_building ( context )
        print ( "Checking the define_reactions properties" )
        self.reactions.check_properties_after_building ( context )
        print ( "Checking the release_sites properties" )
        self.release_sites.check_properties_after_building ( context )
        print ( "Checking the define_release_patterns properties" )
        self.release_patterns.check_properties_after_building ( context )
        print ( "Checking the define_surface_classes properties" )
        self.surface_classes.check_properties_after_building ( context )
        print ( "Checking the modify_surface_regions properties" )
        self.mod_surf_regions.check_properties_after_building ( context )
        print ( "Checking all mesh objects" )
        self.model_objects.check_properties_after_building ( context )
        print ( "Checking the viz_output properties" )
        self.viz_output.check_properties_after_building ( context )
        print ( "Checking the mol_viz properties" )
        self.mol_viz.check_properties_after_building ( context )
        print ( "Checking the reaction_data_output properties" )
        self.rxn_output.check_properties_after_building ( context )
        print ( "Checking/Updating the model_objects properties" )
        cellblender_operators.model_objects_update(context)

        print ( "Done building properties from the data model." )
        


    def draw_uninitialized ( self, layout ):
        row = layout.row()
        row.operator("mcell.init_cellblender", text="Initialize CellBlender")




    def print_id_property_tree ( self, obj, name, depth ):
        """ Recursive routine that prints an ID Property Tree """
        depth = depth + 1
        indent = "".join([ '  ' for x in range(depth) ])
        print ( indent + "Depth="+str(depth) )
        print ( indent + "print_ID_property_tree() called with \"" + name + "\" of type " + str(type(obj)) )
        if "'IDPropertyGroup'" in str(type(obj)):
            print ( indent + "This is an ID property group: " + name )
            for k in obj.keys():
                self.print_id_property_tree ( obj[k], k, depth )
        elif "'list'" in str(type(obj)):
            print ( indent + "This is a list: " + name )
            i = 0
            for k in obj:
                self.print_id_property_tree ( k, name + '['+str(i)+']', depth )
                i += 1
        else:
            print ( indent + "This is NOT an ID property group: " + name + " = " + str(obj) )

        depth = depth - 1
        return




    #################### Special RC3 Code Below ####################

    def RC3_add_from_ID_panel_parameter ( self, dm_dict, dm_name, prop_dict, prop_name, panel_param_list ):
        dm_dict[dm_name] = [ x for x in panel_param_list if x['name'] == prop_dict[prop_name]['unique_static_name'] ] [0] ['expr']

    def RC3_add_from_ID_string ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_float ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_int ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_floatstr ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = str(prop_dict[prop_name])
        else:
          dm_dict[dm_name] = str(default_value)

    def RC3_add_from_ID_boolean ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = ( prop_dict[prop_name] != 0 )
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_enum ( self, dm_dict, dm_name, prop_dict, prop_name, default_value, enum_list ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = enum_list[int(prop_dict[prop_name])]
        else:
          dm_dict[dm_name] = default_value

    def build_data_model_from_RC3_ID_properties ( self, context, geometry=False ):
        # Build an unversioned data model from RC3 ID properties to match the pre-versioned data models that can be upgraded to versioned data models

        print ( "build_data_model_from_RC3_ID_properties: Constructing a data_model dictionary from RC3 ID properties" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!! THIS MAY NOT WORK YET !!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )

        dm = None

        # Remove the RNA properties overlaying the ID Property 'mcell'
        del bpy.types.Scene.mcell
        
        mcell = context.scene.get('mcell')
        if mcell != None:

          # There's an mcell in the scene
          dm = {}
          

          # Build the parameter system first
          par_sys = mcell.get('parameter_system')
          if par_sys != None:
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There's a parameter system" )
            # There's a parameter system
            dm['parameter_system'] = {}
            dm_ps = dm['parameter_system']
            gpl = par_sys.get('general_parameter_list')
            if gpl != None:
              dm_ps['model_parameters'] = []
              dm_mp = dm_ps['model_parameters']
              if len(gpl) > 0:
                for gp in gpl:
                  print ( "Par name = " + str(gp['par_name']) )
                  dm_p = {}
                  dm_p['par_name'] = str(gp['par_name'])
                  dm_p['par_expression'] = str(gp['expr'])
                  dm_p['par_description'] = str(gp['descr'])
                  dm_p['par_units'] = str(gp['units'])
                  extras = {}
                  extras['par_id_name'] = str(gp['name'])
                  extras['par_valid'] = gp['isvalid'] != 0
                  extras['par_value'] = gp['value']
                  dm_p['extras'] = extras
                  dm_mp.append ( dm_p )

            print ( "Done parameter system" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

          ppl = par_sys.get('panel_parameter_list')
          

          # Build the rest of the data model

          # Initialization

          init = mcell.get('initialization')
          if init != None:
            # dm['initialization'] = self.initialization.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is initialization" )

            # There is initialization
            dm['initialization'] = {}
            dm_init = dm['initialization']

            self.RC3_add_from_ID_panel_parameter ( dm_init, 'iterations',              init, 'iterations', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'time_step',               init, 'time_step',  ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'time_step_max',           init, 'time_step_max', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'space_step',              init, 'space_step', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'interaction_radius',      init, 'interaction_radius', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'radial_directions',       init, 'radial_directions', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'radial_subdivisions',     init, 'radial_subdivisions', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'vacancy_search_distance', init, 'vacancy_search_distance', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'surface_grid_density',    init, 'surface_grid_density', ppl )

            self.RC3_add_from_ID_boolean ( dm_init, 'accurate_3d_reactions',     init, 'accurate_3d_reactions', True )
            self.RC3_add_from_ID_boolean ( dm_init, 'center_molecules_on_grid',  init, 'center_molecules_grid', False )


            if init.get('microscopic_reversibility'):
              dm_init['microscopic_reversibility'] = init['microscopic_reversibility']
            else:
              dm_init['microscopic_reversibility'] = 'OFF'

            # Notifications

            dm_init['notifications'] = {}
            dm_note = dm_init['notifications']
            if init.get('all_notifications'):
              dm_note['all_notifications'] = init['all_notifications']
            else:
              dm_note['all_notifications'] = 'INDIVIDUAL'

            if init.get('diffusion_constant_report'):
              dm_note['diffusion_constant_report'] = init['diffusion_constant_report']
            else:
              dm_note['diffusion_constant_report'] = 'BRIEF'

            if init.get('file_output_report'):
              dm_note['file_output_report'] = init['file_output_report'] != 0
            else:
              dm_note['file_output_report'] = False

            if init.get('final_summary'):
              dm_note['final_summary'] = init['final_summary'] != 0
            else:
              dm_note['final_summary'] = True

            if init.get('iteration_report'):
              dm_note['iteration_report'] = init['iteration_report'] != 0
            else:
              dm_note['iteration_report'] = True

            if init.get('partition_location_report'):
              dm_note['partition_location_report'] = init['partition_location_report'] != 0
            else:
              dm_note['partition_location_report'] = False

            if init.get('probability_report'):
              dm_note['probability_report'] = init['probability_report']
            else:
              dm_note['probability_report'] = 'ON'

            if init.get('probability_report_threshold'):
              dm_note['probability_report_threshold'] = init['probability_report_threshold']
            else:
              dm_note['probability_report_threshold'] = 0.0


            if init.get('varying_probability_report'):
              dm_note['varying_probability_report'] = init['varying_probability_report'] != 0
            else:
              dm_note['varying_probability_report'] = True

            if init.get('progress_report'):
              dm_note['progress_report'] = init['progress_report'] != 0
            else:
              dm_note['progress_report'] = True

            if init.get('release_event_report'):
              dm_note['release_event_report'] = init['release_event_report'] != 0
            else:
              dm_note['release_event_report'] = True

            if init.get('molecule_collision_report'):
              dm_note['molecule_collision_report'] = init['molecule_collision_report'] != 0
            else:
              dm_note['molecule_collision_report'] = False


            # Warnings

            dm_init['warnings'] = {}
            dm_warn = dm_init['warnings']

            if init.get('all_warnings'):
              dm_warn['all_warnings'] = init['all_warnings']
            else:
              dm_warn['all_warnings'] = 'INDIVIDUAL'

            if init.get('degenerate_polygons'):
              dm_warn['degenerate_polygons'] = init['degenerate_polygons']
            else:
              dm_warn['degenerate_polygons'] = 'WARNING'

            if init.get('high_reaction_probability'):
              dm_warn['high_reaction_probability'] = init['high_reaction_probability']
            else:
              dm_warn['high_reaction_probability'] = 'IGNORED'

            if init.get('high_probability_threshold'):
              dm_warn['high_probability_threshold'] = init['high_probability_threshold']
            else:
              dm_warn['high_probability_threshold'] = 1.0

            if init.get('lifetime_too_short'):
              dm_warn['lifetime_too_short'] = init['lifetime_too_short']
            else:
              dm_warn['lifetime_too_short'] = 'WARNING'

            if init.get('lifetime_threshold'):
              dm_warn['lifetime_threshold'] = init['lifetime_threshold']
            else:
              dm_warn['lifetime_threshold'] = 50

            if init.get('missed_reactions'):
              dm_warn['missed_reactions'] = init['missed_reactions']
            else:
              dm_warn['missed_reactions'] = 'WARNING'

            if init.get('missed_reaction_threshold'):
              dm_warn['missed_reaction_threshold'] = init['missed_reaction_threshold']
            else:
              dm_warn['missed_reaction_threshold'] = 0.001

            if init.get('negative_diffusion_constant'):
              dm_warn['negative_diffusion_constant'] = init['negative_diffusion_constant']
            else:
              dm_warn['negative_diffusion_constant'] = 'WARNING'

            if init.get('missing_surface_orientation'):
              dm_warn['missing_surface_orientation'] = init['missing_surface_orientation']
            else:
              dm_warn['missing_surface_orientation'] = 'ERROR'

            if init.get('negative_reaction_rate'):
              dm_warn['negative_reaction_rate'] = init['negative_reaction_rate']
            else:
              dm_warn['negative_reaction_rate'] = 'WARNING'

            if init.get('useless_volume_orientation'):
              dm_warn['useless_volume_orientation'] = init['useless_volume_orientation']
            else:
              dm_warn['useless_volume_orientation'] = 'WARNING'

            print ( "Done initialization" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

          # Partitions

          parts = mcell.get('partitions')
          if parts != None:

            # dm['initialization']['partitions'] = self.partitions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are partitions" )
            # There are partitions
            
            # Ensure that there is an initialization section in the data model that's being built
            dm_init = dm.get('initialization')
            if dm_init == None:
              dm['initialization'] = {}
              dm_init = dm['initialization']
            
            dm['initialization']['partitions'] = {}
            dm_parts = dm['initialization']['partitions']

            if parts.get('include'):
              dm_parts['include'] = ( parts['include'] != 0 )
            else:
              dm_parts['include'] = False

            if parts.get('recursion_flag'):
              dm_parts['recursion_flag'] = ( parts['recursion_flag'] != 0 )
            else:
              dm_parts['recursion_flag'] = False

            if parts.get('x_start'):
              dm_parts['x_start'] = parts['x_start']
            else:
              dm_parts['x_start'] = -1

            if parts.get('x_end'):
              dm_parts['x_end'] = parts['x_end']
            else:
              dm_parts['x_end'] = 1

            if parts.get('x_step'):
              dm_parts['x_step'] = parts['x_step']
            else:
              dm_parts['x_step'] = 0.02

            if parts.get('y_start'):
              dm_parts['y_start'] = parts['y_start']
            else:
              dm_parts['y_start'] = -1

            if parts.get('y_end'):
              dm_parts['y_end'] = parts['y_end']
            else:
              dm_parts['y_end'] = 1

            if parts.get('y_step'):
              dm_parts['y_step'] = parts['y_step']
            else:
              dm_parts['y_step'] = 0.02

            if parts.get('z_start'):
              dm_parts['z_start'] = parts['z_start']
            else:
              dm_parts['z_start'] = -1

            if parts.get('z_end'):
              dm_parts['z_end'] = parts['z_end']
            else:
              dm_parts['z_end'] = 1

            if parts.get('z_step'):
              dm_parts['z_step'] = parts['z_step']
            else:
              dm_parts['z_step'] = 0.02

            print ( "Done partitions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Model Objects

          modobjs = mcell.get('model_objects')
          if modobjs != None:
            # dm['model_objects'] = self.model_objects.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are model objects" )
            # There are model objects
            dm['model_objects'] = {}
            dm_mo = dm['model_objects']
            mol = modobjs.get('object_list')
            if mol != None:
              print ( "There is a model_object_list" )
              dm_mo['model_object_list'] = []
              dm_ol = dm_mo['model_object_list']
              if len(mol) > 0:
                for o in mol:
                  print ( "Model Object name = " + str(o['name']) )
                  
                  dm_o = {}
                  
                  self.RC3_add_from_ID_string ( dm_o, 'name', o, 'name', "Object" )

                  dm_ol.append ( dm_o )

            print ( "Done model objects" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Molecules

          mols = mcell.get('molecules')
          if mols != None:
            # dm['define_molecules'] = self.molecules.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are molecules" )
            # There are molecules
            dm['define_molecules'] = {}
            dm_mols = dm['define_molecules']
            ml = mols.get('molecule_list')
            if ml != None:
              dm_mols['molecule_list'] = []
              dm_ml = dm_mols['molecule_list']
              if len(ml) > 0:
                for m in ml:
                  print ( "Mol name = " + str(m['name']) )

                  dm_m = {}

                  self.RC3_add_from_ID_string          ( dm_m, 'mol_name',           m, 'name',               "Molecule" )
                  self.RC3_add_from_ID_enum            ( dm_m, 'mol_type',           m, 'type',               "2D",      ["2D", "3D"] )
                  self.RC3_add_from_ID_boolean         ( dm_m, 'target_only',        m, 'target_only',        False )
                  self.RC3_add_from_ID_boolean         ( dm_m, 'export_viz',         m, 'export_viz',         False )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'diffusion_constant', m, 'diffusion_constant', ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'custom_space_step',  m, 'custom_space_step',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'custom_time_step',   m, 'custom_time_step',   ppl )
                  dm_m['maximum_step_length'] = ""

                  dm_ml.append ( dm_m )

            print ( "Done molecules" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Reactions

          reacts = mcell.get('reactions')
          if reacts != None:
            # dm['define_reactions'] = self.reactions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are reactions" )
            # There are reactions
            dm['define_reactions'] = {}
            dm_reacts = dm['define_reactions']
            rl = reacts.get('reaction_list')
            if rl != None:
              dm_reacts['reaction_list'] = []
              dm_rl = dm_reacts['reaction_list']
              if len(rl) > 0:
                for r in rl:
                  print ( "React name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',      r, 'name',      "The Reaction" )
                  self.RC3_add_from_ID_string  ( dm_r, 'rxn_name',  r, 'rxn_name',  "" )
                  self.RC3_add_from_ID_string  ( dm_r, 'reactants', r, 'reactants', "" )
                  self.RC3_add_from_ID_string  ( dm_r, 'products',  r, 'products',  "" )

                  self.RC3_add_from_ID_enum    ( dm_r, 'rxn_type',  r, 'type', "irreversible", ["irreversible", "reversible"] )

                  self.RC3_add_from_ID_boolean ( dm_r, 'variable_rate_switch', r, 'variable_rate_switch', False )
                  self.RC3_add_from_ID_string  ( dm_r, 'variable_rate',        r, 'variable_rate',        "" )
                  self.RC3_add_from_ID_boolean ( dm_r, 'variable_rate_valid',  r, 'variable_rate_valid',  False )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'fwd_rate',  r, 'fwd_rate',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'bkwd_rate', r, 'bkwd_rate', ppl )

                  dm_rl.append ( dm_r )

            print ( "Done reactions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Release Sites

          rels = mcell.get('release_sites')
          if rels != None:
            # dm['release_sites'] = self.release_sites.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are release sites" )
            # There are release sites
            dm['release_sites'] = {}
            dm_rel = dm['release_sites']
            rsl = rels.get('mol_release_list')
            if rsl != None:
              print ( "There is a mol_release_list" )
              dm_rel['release_site_list'] = []
              dm_rs = dm_rel['release_site_list']
              if len(rsl) > 0:
                for r in rsl:
                  print ( "Release Site name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',     r, 'name',     "Release_Site" )
                  self.RC3_add_from_ID_string  ( dm_r, 'molecule', r, 'molecule', "" )
                  self.RC3_add_from_ID_enum    ( dm_r, 'shape',    r, 'shape',    "CUBIC", ["CUBIC", "SPHERICAL", "SPHERICAL_SHELL", "OBJECT"] )
                  self.RC3_add_from_ID_enum    ( dm_r, 'orient',   r, 'orient',   "\'",    ["\'", ",", ";"] )
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'object_expr', r, 'object_expr', "" )
                  
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_x',  r, 'location_x',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_y',  r, 'location_y',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_z',  r, 'location_z',  ppl )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'site_diameter',        r, 'diameter',     ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'release_probability',  r, 'probability',  ppl )

                  self.RC3_add_from_ID_enum    ( dm_r, 'quantity_type', r, 'quantity_type', "NUMBER_TO_RELEASE", ["NUMBER_TO_RELEASE", "GAUSSIAN_RELEASE_NUMBER", "DENSITY"] )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'quantity', r, 'quantity',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'stddev',   r, 'stddev',  ppl )

                  self.RC3_add_from_ID_string  ( dm_r, 'pattern', r, 'pattern', "" )

                  dm_rs.append ( dm_r )

            print ( "Done release sites" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Release Patterns

          relps = mcell.get('release_patterns')
          if relps != None:
            # dm['define_release_patterns'] = self.release_patterns.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are release patterns" )
            # There are release patterns
            dm['define_release_patterns'] = {}
            dm_relps = dm['define_release_patterns']
            rpl = relps.get('release_pattern_list')
            if rpl != None:
              print ( "There is a release_pattern_list" )
              dm_relps['release_pattern_list'] = []
              dm_rpl = dm_relps['release_pattern_list']
              if len(rpl) > 0:
                for r in rpl:
                  print ( "Release Pattern name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',     r, 'name',     "Release_Pattern" )
                  
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'delay',            r, 'delay',            ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'release_interval', r, 'release_interval', ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'train_duration',   r, 'train_duration',   ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'train_interval',   r, 'train_interval',   ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'number_of_trains', r, 'number_of_trains', ppl )

                  dm_rpl.append ( dm_r )

            print ( "Done release patterns" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Surface Class Definitions

          surfcs = mcell.get('surface_classes')
          if surfcs != None:
            # dm['define_surface_classes'] = self.surface_classes.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are surface class definitions" )
            # There are surface classes
            print ( "surfcs.keys() = " + str(surfcs.keys()) )
            dm['define_surface_classes'] = {}
            dm_surfcs = dm['define_surface_classes']
            scl = surfcs.get('surf_class_list')
            if scl != None:
              print ( "There is a surf_class_list" )
              dm_surfcs['surface_class_list'] = []
              dm_scl = dm_surfcs['surface_class_list']
              print ( "The surf_class_list has " + str(len(scl)) + " surface classes" )
              if len(scl) > 0:
                for sc in scl:
                  print ( "  Surface Class Name = " + str(sc['name']) )
                  dm_sc = {}
                  if 'name' in sc:
                    dm_sc['name'] = sc['name']
                  dm_sc['surface_class_prop_list'] = []
                  dm_scpl = dm_sc['surface_class_prop_list']
                  if 'surf_class_props_list' in sc:
                    scpl = sc.get('surf_class_props_list')
                    for scp in scpl:
                      print ( "    Surface Class Property Name = " + str(scp['name']) )
                      dm_scp = {}
                      self.RC3_add_from_ID_string   ( dm_scp, 'name',     scp, 'name',     "Surf_Class_Property" )
                      self.RC3_add_from_ID_string   ( dm_scp, 'molecule', scp, 'molecule', "" )
                      
                      self.RC3_add_from_ID_enum     ( dm_scp, 'surf_class_orient', scp, 'surf_class_orient', "\'", ['\'', ',', ';'] )
                      self.RC3_add_from_ID_enum     ( dm_scp, 'surf_class_type',   scp, 'surf_class_type',   "ABSORPTIVE", ['ABSORPTIVE', 'TRANSPARENT', 'REFLECTIVE', 'CLAMP_CONCENTRATION'] )
                      
                      self.RC3_add_from_ID_floatstr ( dm_scp, 'clamp_value',       scp, 'clamp_value', "" )
                      
                      dm_scpl.append ( dm_scp )

                  dm_scl.append ( dm_sc )

            print ( "Done surface class definitions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Surface Region Definitions

          modsrs = mcell.get('mod_surf_regions')
          if modsrs != None:
            # dm['modify_surface_regions'] = self.mod_surf_regions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are surface regions" )
            # There are surface regions
            print ( "modsrs.keys() = " + str(modsrs.keys()) )
            dm['modify_surface_regions'] = {}
            dm_modsrs = dm['modify_surface_regions']
            msrl = modsrs.get('mod_surf_regions_list')
            if msrl != None:
              print ( "There is a mod_surf_regions_list" )
              dm_modsrs['modify_surface_regions_list'] = []
              dm_msrl = dm_modsrs['modify_surface_regions_list']
              if len(msrl) > 0:
                print ( "The mod_surf_regions_list has " + str(len(msrl)) + " regions" )
                for msr in msrl:
                  print ( " Modify Region Name = " + str(msr['name']) )
                  print ( "   Surf Class Name = " + str(msr['surf_class_name']) )
                  print ( "   Object Name = " + str(msr['object_name']) )
                  print ( "   Region Name = " + str(msr['region_name']) )
                  
                  dm_msr = {}

                  self.RC3_add_from_ID_string ( dm_msr, 'name',     msr, 'name',     "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'surf_class_name', msr, 'surf_class_name', "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'object_name', msr, 'object_name', "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'region_name', msr, 'region_name', "" )

                  dm_msrl.append ( dm_msr )

            print ( "Done surface regions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Visualization Output

          vizout = mcell.get('viz_output')
          if vizout != None:
            # dm['viz_output'] = self.viz_output.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is viz output" )
            # There is viz output
            dm['viz_output'] = {}
            dm_viz = dm['viz_output']
            self.RC3_add_from_ID_boolean ( dm_viz, 'all_iterations', vizout, 'all_iterations', True )
            self.RC3_add_from_ID_int     ( dm_viz, 'start',          vizout, 'start',          0 )
            self.RC3_add_from_ID_int     ( dm_viz, 'end',            vizout, 'end',            1 )
            self.RC3_add_from_ID_int     ( dm_viz, 'step',           vizout, 'step',           1 )
            self.RC3_add_from_ID_boolean ( dm_viz, 'export_all',     vizout, 'export_all',     False )
            print ( "Done viz output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Reaction Output

          rxnout = mcell.get('rxn_output')
          if rxnout != None:
            # dm['reaction_data_output'] = self.rxn_output.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is reaction output" )
            # There is reaction output
            dm['reaction_data_output'] = {}
            dm_rxnout = dm['reaction_data_output']

            self.RC3_add_from_ID_boolean ( dm_rxnout, 'combine_seeds', rxnout, 'combine_seeds', True )
            self.RC3_add_from_ID_boolean ( dm_rxnout, 'mol_colors',    rxnout, 'mol_colors',    False )
            self.RC3_add_from_ID_enum    ( dm_rxnout, 'plot_layout',   rxnout, 'plot_layout',   " plot ", [' page ', ' plot ', ' '] )
            self.RC3_add_from_ID_enum    ( dm_rxnout, 'plot_legend',   rxnout, 'plot_legend',   "0", ['x', '0', '1', '2', '3', '4', '6', '7', '8', '9', '10'] )


            print ( "rxnout.keys() = " + str(rxnout.keys()) )
            rxnl = rxnout.get('rxn_output_list')
            if rxnl != None:
              print ( "There is a rxn_output_list" )
              dm_rxnout['reaction_output_list'] = []
              dm_rxnl = dm_rxnout['reaction_output_list']
              if len(rxnl) > 0:
                print ( "The reaction_output_list has " + str(len(rxnl)) + " entries" )
                for rxn in rxnl:
                  dm_rxn = {}

                  self.RC3_add_from_ID_string ( dm_rxn, 'name',            rxn, 'name',            "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'molecule_name',   rxn, 'molecule_name',   "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'reaction_name',   rxn, 'reaction_name',   "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'object_name',     rxn, 'object_name',     "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'region_name',     rxn, 'region_name',     "" )
                  self.RC3_add_from_ID_enum   ( dm_rxn, 'count_location',  rxn, 'count_location',  "World",    ['World', 'Object', 'Region'] )
                  self.RC3_add_from_ID_enum   ( dm_rxn, 'rxn_or_mol',      rxn, 'rxn_or_mol',      "Molecule", ['Reaction', 'Molecule'] )

                  dm_rxnl.append ( dm_rxn )

            print ( "Done reaction output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Viz Data


            """ Use this as a template for mol_viz data

            def build_data_model_from_properties ( self, context ):
                print ( "Building Mol Viz data model from properties" )
                mv_dm = {}
                mv_dm['data_model_version'] = "DM_2015_04_13_1700"

                mv_seed_list = []
                for s in self.mol_viz_seed_list:
                    mv_seed_list.append ( str(s.name) )
                mv_dm['seed_list'] = mv_seed_list

                mv_dm['active_seed_index'] = self.active_mol_viz_seed_index
                mv_dm['file_dir'] = self.mol_file_dir

                mv_file_list = []
                for s in self.mol_file_list:
                    mv_file_list.append ( str(s.name) )
                mv_dm['file_list'] = mv_file_list

                mv_dm['file_num'] = self.mol_file_num
                mv_dm['file_name'] = self.mol_file_name
                mv_dm['file_index'] = self.mol_file_index
                mv_dm['file_start_index'] = self.mol_file_start_index
                mv_dm['file_stop_index'] = self.mol_file_stop_index
                mv_dm['file_step_index'] = self.mol_file_step_index

                mv_viz_list = []
                for s in self.mol_viz_list:
                    mv_viz_list.append ( str(s.name) )
                mv_dm['viz_list'] = mv_viz_list

                mv_dm['render_and_save'] = self.render_and_save
                mv_dm['viz_enable'] = self.mol_viz_enable

                mv_color_list = []
                for c in self.color_list:
                    mv_color = []
                    for i in c.vec:
                        mv_color.append ( i )
                    mv_color_list.append ( mv_color )
                mv_dm['color_list'] = mv_color_list

                mv_dm['color_index'] = self.color_index
                mv_dm['manual_select_viz_dir'] = self.manual_select_viz_dir

                return mv_dm
            """





          """
          geom = mcell.get('geometrical_objects')
          if geom != None:
            # dm['geometrical_objects'] = self.model_objects.build_data_model_geometry_from_mesh(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is viz output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            # There is viz output
          if geometry:
            print ( "Adding Geometry to Data Model" )
            
            dm['materials'] = self.model_objects.build_data_model_materials_from_materials(context)
          """

        print ( "Adding Geometry to Data Model" )
        dm['geometrical_objects'] = self.model_objects.build_data_model_geometry_from_mesh(context)
        dm['materials'] = self.model_objects.build_data_model_materials_from_materials(context)
        # cellblender.data_model.save_data_model_to_file ( dm, "Upgraded_Data_Model.txt" )
        print ( "Removing Geometry from Data Model" )
        dm.pop('geometrical_objects')
        dm.pop('materials')

        #self.print_id_property_tree ( context.scene['mcell'], 'mcell', 0 )

        # Restore the RNA properties overlaying the ID Property 'mcell'
        bpy.types.Scene.mcell = bpy.props.PointerProperty(type=MCellPropertyGroup)

        return dm

