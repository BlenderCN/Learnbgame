"""
This module supports parameters and evaluation of expressions.
"""

import bpy
from bpy.props import *

from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys

import cellblender



# For timing code:
import time
import io

####################### Start of Profiling Code #######################

# From: http://wiki.blender.org/index.php/User:Z0r/PyDevAndProfiling

prof = {}

# Defines a dictionary associating a call name with a list of 3 (now 4) entries:
#  0: Name
#  1: Duration
#  2: Count
#  3: Start Time (for non-decorated version)

class profile:
    ''' Function decorator for code profiling.'''
    
    def __init__(self,name):
        self.name = name
    
    def __call__(self,fun):
        def profile_fun(*args, **kwargs):
            start = time.clock()
            try:
                return fun(*args, **kwargs)
            finally:
                duration = time.clock() - start
                if fun in prof:
                    prof[fun][1] += duration
                    prof[fun][2] += 1
                else:
                    prof[fun] = [self.name, duration, 1, 0]
        return profile_fun

# Builds on the previous profiling code with non-decorated versions (needed by some Blender functions):
#  0: Name
#  1: Duration
#  2: Count
#  3: Start Time (for non-decorated version)

def start_timer(fun):
    start = time.clock()
    if fun in prof:
        prof[fun][2] += 1
        prof[fun][3] = start
    else:
        prof[fun] = [fun, 0, 1, start]

def stop_timer(fun):
    stop = time.clock()
    if fun in prof:
        prof[fun][1] += stop - prof[fun][3]   # Stop - Start
        # prof[fun][2] += 1
    else:
        print ( "Timing Error: stop called without start!!" )
        pass


def print_statistics(app):
    '''Prints profiling results to the console,
       appends to plot files,
       and generates plotting and deleting scripts.'''
    
    print ( "=== Execution Statistics with " + str(len(app.parameter_system.general_parameter_list)) + " general parameters and " + str(len(app.parameter_system.panel_parameter_list)) + " panel parameters ===" )

    def timekey(stat):
        return stat[1] / float(stat[2])

    stats = sorted(prof.values(), key=timekey, reverse=True)

    print ( '{:<55} {:>7} {:>7} {:>8}'.format('FUNCTION', 'CALLS', 'SUM(ms)', 'AV(ms)'))
    for stat in stats:
        print ( '{:<55} {:>7} {:>7.0f} {:>8.2f}'.format(stat[0],stat[2],stat[1]*1000,(stat[1]/float(stat[2]))*1000))
        f = io.open(stat[0]+"_plot.txt",'a')
        #f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str((stat[1]/float(stat[2]))*1000) + "\n" )
        f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str(float(stat[1])*1000) + "\n" )
        f.flush()
        f.close()

    f = io.open("plot_command.bat",'w')
    f.write ( "java -jar data_plotters/java_plot/PlotData.jar" )
    for stat in stats:
        f.write ( " fxy=" + stat[0]+"_plot.txt" )
    f.flush()
    f.close()

    f = io.open("delete_command.bat",'w')
    for stat in stats:
        f.write ( "rm -f " + stat[0]+"_plot.txt\n" )
    f.flush()
    f.close()


class MCELL_OT_print_profiling(bpy.types.Operator):
    bl_idname = "mcell.print_profiling"
    bl_label = "Print Profiling"
    bl_description = ("Print Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.mcell
        print_statistics(app)
        return {'FINISHED'}

    def invoke(self, context, event):
        app = context.scene.mcell
        print_statistics(app)
        return {'RUNNING_MODAL'}


class MCELL_OT_clear_profiling(bpy.types.Operator):
    bl_idname = "mcell.clear_profiling"
    bl_label = "Clear Profiling"
    bl_description = ("Clear Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        prof.clear()
        return {'FINISHED'}

    def invoke(self, context, event):
        prof.clear()
        return {'RUNNING_MODAL'}



####################### End of Profiling Code #######################




##### vvvvvvvvv   General Parameter Code   vvvvvvvvv



#@profile('spaced_strings_from_list')
def spaced_strings_from_list ( list_of_strings ):
    space = " "
    return space.join(list_of_strings)


class MCELL_UL_draw_parameter(bpy.types.UIList):
    #@profile('MCELL_UL_draw_parameter.draw_item')
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        start_timer('MCELL_UL_draw_parameter.draw_item')
        mcell = context.scene.mcell
        parsys = mcell.parameter_system
        par = parsys.general_parameter_list[index]
        disp = str(par.par_name) + " = " + str(par.expr) + " = "
        if par.isvalid:
            disp = disp + str(parsys.param_display_format%par.value)
            icon = 'FILE_TICK'
        else:
            disp = disp + " ?"
            icon = 'ERROR'
        layout.label(disp, icon=icon)
        stop_timer('MCELL_UL_draw_parameter.draw_item')


class MCELL_PT_parameter_system(bpy.types.Panel):
    bl_label = "CellBlender - Model Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    #@profile('MCELL_PT_parameter_system.draw')

    def draw ( self, context ):
        # Call the draw function of the object itself
        start_timer('MCELL_PT_parameter_system.draw_panel')
        context.scene.mcell.parameter_system.draw_panel ( context, self )
        stop_timer('MCELL_PT_parameter_system.draw_panel')


class MCELL_OT_add_parameter(bpy.types.Operator):
    bl_idname = "mcell.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter"
    bl_options = {'REGISTER', 'UNDO'}

    #@profile('MCELL_OT_add_parameter.execute')
    def execute(self, context):
        start_timer('MCELL_OT_add_parameter.execute')
        context.scene.mcell.parameter_system.add_parameter(context)
        stop_timer('MCELL_OT_add_parameter.execute')
        return {'FINISHED'}

class MCELL_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "mcell.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter"
    bl_options = {'REGISTER', 'UNDO'}

    #@profile('MCELL_OT_remove_parameter.execute')
    def execute(self, context):
        start_timer('MCELL_OT_remove_parameter.execute')
        status = context.scene.mcell.parameter_system.remove_active_parameter(context)
        if status != "":
            # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
            self.report({'ERROR'}, status)
        stop_timer('MCELL_OT_remove_parameter.execute')
        return {'FINISHED'}

class MCELL_OT_print_parameter_details(bpy.types.Operator):
    bl_idname = "mcell.print_parameter_details"
    bl_label = "Print Details"
    bl_description = "Print the details to the console"
    bl_options = {'REGISTER', 'UNDO'}

    #@profile('MCELL_OT_print_parameter_details')
    def execute(self, context):
        start_timer('MCELL_OT_print_parameter_details.execute')
        print ( "self = " + str(self) )
        stop_timer('MCELL_OT_print_parameter_details.execute')
        return {'FINISHED'}



class Parameter_Reference ( bpy.types.PropertyGroup ):
    """ Simple class to reference a panel parameter - used throughout the application """
    # This is the ONLY property in this class ... all others are in the Parameter_Data that this references
    unique_static_name = StringProperty ( name="unique_name", default="" )

    #@profile('Parameter_Reference.set_unique_static_name')
    def set_unique_static_name ( self, new_name ):
        self.unique_static_name = new_name
    
    #@profile('Parameter_Reference.init_ref')
    def init_ref ( self, parameter_system, type_name, user_name=None, user_expr="0", user_descr="Panel Parameter", user_units="", user_int=False ):

        if user_name == None:
            user_name = "none"

        new_par = parameter_system.new_parameter ( new_name=user_name, pp=True, new_expr=user_expr )
        new_par.descr = user_descr
        new_par.units = user_units
        new_par.isint = user_int
    
        self.set_unique_static_name ( new_par.name )

    def remove_properties ( self, context ):
        print ( "Removing all Parameter Reference Properties ... not implemented yet!" )
        

    #@profile('Parameter_Reference.del_ref')
    def del_ref ( self, parameter_system ):
        parameter_system.del_panel_parameter ( self.unique_static_name )


    #@profile('Parameter_Reference.get_param')
    def get_param ( self, plist=None ):
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        return plist[self.unique_static_name]

    #@profile('Parameter_Reference.get_expr')
    def get_expr ( self, plist=None ):
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        return self.get_param(plist).expr

    #@profile('Parameter_Reference.set_expr')
    def set_expr ( self, expr, plist=None ):
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        p = self.get_param(plist)
        p.expr = expr

    #@profile('Parameter_Reference.get_value')
    def get_value ( self, plist=None ):
        '''Return the numeric value of this parameter'''
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        p = self.get_param(plist)
        if p.isint:
            return int(p.get_numeric_value())
        else:
            return p.get_numeric_value()

    #@profile('Parameter_Reference.get_as_string')
    def get_as_string ( self, plist=None, as_expr=False ):
        '''Return a string represeting the numeric value or the expression itself'''
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        p = self.get_param(plist)
        if as_expr:
            return p.expr
        else:
            if p.isint:
                return "%g"%(int(p.get_numeric_value()))
            else:
                return "%g"%(p.get_numeric_value())

    #@profile('Parameter_Reference.get_as_string_or_value')
    def get_as_string_or_value ( self, plist=None, as_expr=False ):
        '''Return a string represeting the numeric value or a non-blank expression'''
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        p = self.get_param(plist)
        if as_expr and (len(p.expr.strip()) > 0):
            return p.expr
        else:
            if p.isint:
                return "%g"%(int(p.get_numeric_value()))
            else:
                return "%g"%(p.get_numeric_value())


    #@profile('Parameter_Reference.get_label')
    def get_label ( self, plist=None ):
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        return self.get_param(plist).par_name


    #@profile('Parameter_Reference.draw')
    def draw ( self, layout, parameter_system ):
        plist = parameter_system.panel_parameter_list
        try:
            p = self.get_param(plist)
            if parameter_system.param_display_mode == 'two_line':
                # Create a box to put everything inside
                # Cheat by using the same name (layout) so subsequent code doesn't change
                layout = layout.box()
            row = layout.row()
            if p.isvalid:
                value = 0
                disp_val = " "
                if p.expr.strip() != "":
                    value = p.get_numeric_value()
                    disp_val = parameter_system.param_display_format%value
                if parameter_system.param_display_mode == 'one_line':
                    split = row.split(parameter_system.param_label_fraction)
                    col = split.column()
                    col.label ( text=p.par_name+" = "+disp_val )
                    col = split.column()
                    col.prop ( p, "expr", text="" )
                    col = row.column()
                    col.prop ( p, "show_help", icon='INFO', text="" )
                elif parameter_system.param_display_mode == 'two_line':
                    row.label ( icon='NONE', text=p.par_name+" = "+disp_val )
                    row = layout.row()
                    split = row.split(0.03)
                    col = split.column()
                    col = split.column()
                    col.prop ( p, "expr", text="" )
                    col = row.column()
                    col.prop ( p, "show_help", icon='INFO', text="" )
            else:
                value = 0
                if parameter_system.param_display_mode == 'one_line':
                    split = row.split(parameter_system.param_label_fraction)
                    col = split.column()
                    col.label ( text=p.par_name+" = ?", icon='ERROR' )
                    col = split.column()
                    col.prop ( p, "expr", text="", icon='ERROR' )
                    col = row.column()
                    col.prop ( p, "show_help", icon='INFO', text="" )
                elif parameter_system.param_display_mode == 'two_line':
                    row.label ( icon='ERROR', text=p.par_name+" = ?" )
                    row = layout.row()
                    split = row.split(0.03)
                    col = split.column()
                    col = split.column()
                    col.prop ( p, "expr", text="", icon='ERROR' )
                    col = row.column()
                    col.prop ( p, "show_help", icon='INFO', text="" )
                
            if p.show_help:
                # Draw the help information in a box inset from the left side
                row = layout.row()
                # Use a split with two columns to indent the box
                split = row.split(0.03)
                col = split.column()
                col = split.column()
                box = col.box()
                desc_list = p.descr.split("\n")
                for desc_line in desc_list:
                    box.label (text=desc_line)
                if len(p.units) > 0:
                    box.label(text="Units = " + p.units)
                if parameter_system.show_all_details:
                    box = box.box()
                    p.draw_details(box)
                    row = box.row()
                    split = row.split(1.0/3)
                    col = split.column()
                    col = split.column()
                    col = split.column()
                    col.prop(p,"print_info", text="Print to Console", icon='LONGDISPLAY' )
                    row = box.row()

        except Exception as ex:
            print ( "Parameter not found (or other error) for: \"" + self.unique_static_name + "\" (" + str(self) + "), exception = " + str(ex) )
            pass


class Expression_Handler:

    """
      String encoding of expression lists:
      
      Rules:
        The tilde character (~) separates all terms
        Any term that does not start with # is a string literal
        Any term that starts with #? is an undefined parameter name
        Any term that starts with # followed by an integer is a parameter ID

      Example:
        Parameter 'a' has an ID of 1
        Parameter 'b' has an ID of 2
        Parameter 'c' is undefined
        Original Expression:  a + 5 + b + c
          Expression as a List: [1, '+', '5', '+', 2, '+', None, 'c' ]
          Expression as string:  #1~+~5~+~#2~+~#?c
        Note that these ID numbers always reference General Parameters so the IDs
          used in this example (1 and 2) will reference "g1" and "g2" respectively.
          Panel Parameters cannot be referenced in expressions (they have no name).
    """
    
    #@profile('Expression_Handler.get_term_sep')
    def get_term_sep (self):
        return ( "~" )    # This is the string used to separate terms in an expression. It should be illegal in whatever syntax is being parsed.

    #@profile('Expression_Handler.UNDEFINED_NAME')
    def UNDEFINED_NAME(self):
        return ( "   (0*1111111*0)   " )   # This is a string that evaluates to zero, but is easy to spot in expressions
    
    #@profile('Expression_Handler.get_expression_keywords')
    def get_expression_keywords(self):
        return ( { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' } )

    #@profile('Expression_Handler.get_mdl_keywords')
    def get_mdl_keywords(self):
        # It's not clear how these will be handled, but they've been added here because they will be needed to avoid naming conflicts
        return ( [  "ABS",
                    "ABSORPTIVE",
                    "ACCURATE_3D_REACTIONS",
                    "ACOS",
                    "ALL_DATA",
                    "ALL_CROSSINGS",
                    "ALL_ELEMENTS",
                    "ALL_ENCLOSED",
                    "ALL_HITS",
                    "ALL_ITERATIONS",
                    "ALL_MESHES",
                    "ALL_MOLECULES",
                    "ALL_NOTIFICATIONS",
                    "ALL_TIMES",
                    "ALL_WARNINGS",
                    "ASCII",
                    "ASIN",
                    "ASPECT_RATIO",
                    "ATAN",
                    "BACK",
                    "BACK_CROSSINGS",
                    "BACK_HITS",
                    "BINARY",
                    "BOTTOM",
                    "BOX",
                    "BOX_TRIANGULATION_REPORT",
                    "BRIEF",
                    "CEIL",
                    "CELLBLENDER",
                    "CENTER_MOLECULES_ON_GRID",
                    "CHECKPOINT_INFILE",
                    "CHECKPOINT_OUTFILE",
                    "CHECKPOINT_ITERATIONS",
                    "CHECKPOINT_REALTIME",
                    "CHECKPOINT_REPORT",
                    "CLAMP",
                    "CLAMP_CONC",
                    "CLAMP_CONCENTRATION",
                    "CLOSE_PARTITION_SPACING",
                    "COMPLEX_PLACEMENT_ATTEMPTS",
                    "COMPLEX_PLACEMENT_FAILURE",
                    "COMPLEX_PLACEMENT_FAILURE_THRESHOLD",
                    "COMPLEX_RATE",
                    "CORNERS",
                    "COS",
                    "CONC",
                    "CONCENTRATION",
                    "COUNT",
                    "CUBIC",
                    "CUBIC_RELEASE_SITE",
                    "CUSTOM_SPACE_STEP",
                    "CUSTOM_RK",
                    "CUSTOM_TIME_STEP",
                    "D_3D",
                    "DIFFUSION_CONSTANT",
                    "DIFFUSION_CONSTANT_3D",
                    "D_2D",
                    "DIFFUSION_CONSTANT_2D",
                    "DEFAULT",
                    "DEFINE_COMPLEX_MOLECULE",
                    "DEFINE_MOLECULE",
                    "DEFINE_MOLECULES",
                    "DEFINE_REACTIONS",
                    "DEFINE_RELEASE_PATTERN",
                    "DEFINE_SURFACE_REGIONS",
                    "DEFINE_SURFACE_CLASS",
                    "DEFINE_SURFACE_CLASSES",
                    "DEGENERATE_POLYGONS",
                    "DELAY",
                    "DENSITY",
                    "DIFFUSION_CONSTANT_REPORT",
                    "DX",
                    "DREAMM_V3",
                    "DREAMM_V3_GROUPED",
                    "EFFECTOR_GRID_DENSITY",
                    "SURFACE_GRID_DENSITY",
                    "EFFECTOR_POSITIONS",
                    "EFFECTOR_STATES",
                    "ELEMENT_CONNECTIONS",
                    "ELEMENT_LIST",
                    "ELLIPTIC",
                    "ELLIPTIC_RELEASE_SITE",
                    "ERROR",
                    "ESTIMATE_CONC",
                    "ESTIMATE_CONCENTRATION",
                    "EXCLUDE_ELEMENTS",
                    "EXCLUDE_PATCH",
                    "EXCLUDE_REGION",
                    "EXIT",
                    "EXP",
                    "EXPRESSION",
                    "FALSE",
                    "FILENAME",
                    "FILENAME_PREFIX",
                    "FILE_OUTPUT_REPORT",
                    "FINAL_SUMMARY",
                    "FLOOR",
                    "FRONT",
                    "FRONT_CROSSINGS",
                    "FRONT_HITS",
                    "FULLY_RANDOM",
                    "GAUSSIAN_RELEASE_NUMBER",
                    "GEOMETRY",
                    "HEADER",
                    "HIGH_PROBABILITY_THRESHOLD",
                    "HIGH_REACTION_PROBABILITY",
                    "IGNORE",
                    "IGNORED",
                    "INCLUDE_ELEMENTS",
                    "INCLUDE_FILE",
                    "INCLUDE_PATCH",
                    "INCLUDE_REGION",
                    "INPUT_FILE",
                    "INSTANTIATE",
                    "INTERACTION_RADIUS",
                    "INVALID_OUTPUT_STEP_TIME",
                    "ITERATIONS",
                    "ITERATION_FRAME_DATA",
                    "ITERATION_LIST",
                    "ITERATION_NUMBERS",
                    "ITERATION_REPORT",
                    "LEFT",
                    "LIFETIME_TOO_SHORT",
                    "LIFETIME_THRESHOLD",
                    "LIST",
                    "LOCATION",
                    "LOG10",
                    "LOG",
                    "MAX",
                    "MAXIMUM_STEP_LENGTH",
                    "MEAN_DIAMETER",
                    "MEAN_NUMBER",
                    "MEMORY_PARTITION_X",
                    "MEMORY_PARTITION_Y",
                    "MEMORY_PARTITION_Z",
                    "MEMORY_PARTITION_POOL",
                    "MESHES",
                    "MICROSCOPIC_REVERSIBILITY",
                    "MIN",
                    "MISSED_REACTIONS",
                    "MISSED_REACTION_THRESHOLD",
                    "MISSING_SURFACE_ORIENTATION",
                    "MOD",
                    "MODE",
                    "MODIFY_SURFACE_REGIONS",
                    "MOLECULE_DENSITY",
                    "MOLECULE_NUMBER",
                    "MOLECULE",
                    "LIGAND",
                    "MOLECULES",
                    "MOLECULE_COLLISION_REPORT",
                    "MOLECULE_POSITIONS",
                    "LIGAND_POSITIONS",
                    "MOLECULE_STATES",
                    "LIGAND_STATES",
                    "MOLECULE_FILE_PREFIX",
                    "MOLECULE_PLACEMENT_FAILURE",
                    "NAME_LIST",
                    "NEGATIVE_DIFFUSION_CONSTANT",
                    "NEGATIVE_REACTION_RATE",
                    "NO",
                    "NOEXIT",
                    "NONE",
                    "NOTIFICATIONS",
                    "NULL",
                    "NUMBER_OF_SUBUNITS",
                    "NUMBER_OF_SLOTS",
                    "NUMBER_OF_TRAINS",
                    "NUMBER_TO_RELEASE",
                    "OBJECT",
                    "OBJECT_FILE_PREFIXES",
                    "OFF",
                    "ON",
                    "ORIENTATIONS",
                    "OUTPUT_BUFFER_SIZE",
                    "OVERWRITTEN_OUTPUT_FILE",
                    "PARTITION_LOCATION_REPORT",
                    "PARTITION_X",
                    "PARTITION_Y",
                    "PARTITION_Z",
                    "PI",
                    "POLYGON_LIST",
                    "POSITIONS",
                    "PROBABILITY_REPORT",
                    "PROBABILITY_REPORT_THRESHOLD",
                    "PROGRESS_REPORT",
                    "RADIAL_DIRECTIONS",
                    "RADIAL_SUBDIVISIONS",
                    "RAND_UNIFORM",
                    "RAND_GAUSSIAN",
                    "RATE_RULES",
                    "REACTION_DATA_OUTPUT",
                    "REACTION_OUTPUT_REPORT",
                    "REACTION_GROUP",
                    "RECTANGULAR",
                    "RECTANGULAR_RELEASE_SITE",
                    "REFERENCE_DIFFUSION_CONSTANT",
                    "REFLECTIVE",
                    "REGION_DATA",
                    "RELEASE_EVENT_REPORT",
                    "RELEASE_INTERVAL",
                    "RELEASE_PATTERN",
                    "RELEASE_PROBABILITY",
                    "RELEASE_SITE",
                    "REMOVE_ELEMENTS",
                    "RIGHT",
                    "ROTATE",
                    "ROUND_OFF",
                    "SCALE",
                    "SEED",
                    "SHAPE",
                    "SHOW_EXACT_TIME",
                    "SIN",
                    "SITE_DIAMETER",
                    "SITE_RADIUS",
                    "SPACE_STEP",
                    "SPHERICAL",
                    "SPHERICAL_RELEASE_SITE",
                    "SPHERICAL_SHELL",
                    "SPHERICAL_SHELL_SITE",
                    "SQRT",
                    "STANDARD_DEVIATION",
                    "STATE_VALUES",
                    "STEP",
                    "STRING_TO_NUM",
                    "SUBUNIT",
                    "SLOT",
                    "SUBUNIT_RELATIONSHIPS",
                    "SLOT_RELATIONSHIPS",
                    "SUM",
                    "SURFACE_CLASS",
                    "SURFACE_ONLY",
                    "SURFACE_POSITIONS",
                    "SURFACE_STATES",
                    "TAN",
                    "TARGET_ONLY",
                    "TET_ELEMENT_CONNECTIONS",
                    "THROUGHPUT_REPORT",
                    "TIME_LIST",
                    "TIME_POINTS",
                    "TIME_STEP",
                    "TIME_STEP_MAX",
                    "TO",
                    "TOP",
                    "TRAIN_DURATION",
                    "TRAIN_INTERVAL",
                    "TRANSLATE",
                    "TRANSPARENT",
                    "TRIGGER",
                    "TRUE",
                    "UNLIMITED",
                    "VACANCY_SEARCH_DISTANCE",
                    "VARYING_PROBABILITY_REPORT",
                    "USELESS_VOLUME_ORIENTATION",
                    "VERTEX_LIST",
                    "VIZ_DATA_OUTPUT",
                    "VIZ_MESH_FORMAT",
                    "VIZ_MOLECULE_FORMAT",
                    "VIZ_OUTPUT",
                    "VIZ_OUTPUT_REPORT",
                    "VIZ_VALUE",
                    "VOLUME_DATA_OUTPUT",
                    "VOLUME_OUTPUT_REPORT",
                    "VOLUME_DEPENDENT_RELEASE_NUMBER",
                    "VOLUME_ONLY",
                    "VOXEL_COUNT",
                    "VOXEL_LIST",
                    "VOXEL_SIZE",
                    "WARNING",
                    "WARNINGS",
                    "WORLD",
                    "YES",
                    "printf",
                    "fprintf",
                    "sprintf",
                    "print_time",
                    "fprint_time",
                    "fopen",
                    "fclose" ] )

    #@profile('encode_expr_list_to_str')
    def encode_expr_list_to_str ( self, expr_list ):
        """ Turns an expression list into a string that can be stored as a Blender StringProperty """
        term_sep = self.get_term_sep()
        expr_str = ""
        next_is_undefined = False
        for e in expr_list:
            if next_is_undefined:
                expr_str += term_sep + '#?' + e
                next_is_undefined = False
            else:
                if type(e) == type(None):
                    next_is_undefined = True
                elif type(e) == int:
                    expr_str += term_sep + "#" + str(e)
                elif type(e) == type("a"):
                    expr_str += term_sep + e
                else:
                    print ( "Unexepected type while encoding list: " + str(expr_list) )

        if len(expr_str) >= len(term_sep):
            # Remove the first term_sep string (easier here than checking above)
            expr_str = expr_str[len(term_sep):]
        return expr_str


    #@profile('Expression_Handler.decode_str_to_expr_list')
    def decode_str_to_expr_list ( self, expr_str ):
        """ Recovers an expression list from a string that has been stored as a Blender StringProperty """
        expr_list = []
        terms = expr_str.split(self.get_term_sep())
        for e in terms:
            if len(e) > 0:
                if e[0] == '#':
                    if (len(e) > 1) and (e[1] == '?'):
                        expr_list.append ( None )
                        expr_list.append ( e[2:] )
                    else:
                        expr_list.append ( int(e[1:]) )
                else:
                    expr_list.append ( e )
        return expr_list


    #@profile('Expression_Handler.build_mdl_expr')
    def build_mdl_expr ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into an MDL expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_mdl_expr did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it without translation
                    expr = expr + token
        return expr

    #@profile('Expression_Handler.build_py_expr_using_names')
    def build_py_expr_using_names ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into a python expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_py_expr_using_names did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it after translation as needed
                    if token in expression_keywords:
                        expr = expr + expression_keywords[token]
                    else:
                        expr = expr + token
        return expr

    #@profile('Expression_Handler.build_py_expr_using_ids')
    def build_py_expr_using_ids ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into a python expression using unique names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + token_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_py_expr_using_ids did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it after translation as needed
                    if token in expression_keywords:
                        expr = expr + expression_keywords[token]
                    else:
                        expr = expr + token
        return expr


    #@profile('Expression_Handler.parse_param_expr')
    def parse_param_expr ( self, param_expr, parameter_system ):
        """ Converts a string expression into a list expression with:
                 variable id's as integers,
                 None preceding undefined names
                 all others as strings
            Returns either a list (if successful) or None if there is an error

            Examples:

              Expression: "A * (B + C)" becomes something like: [ 3, "*", "(", 22, "+", 5, ")", "" ]
                 where 3, 22, and 5 are the ID numbers for parameters A, B, and C respectively

              Expression: "A * (B + C)" when B is undefined becomes: [ 3, "*", "(", None, "B", "+", 5, ")", "" ]

              Note that the parsing may produce empty strings in the list which should not cause any problem.
        """
        general_parameter_list = parameter_system.general_parameter_list

        lcl_name_ID_dict = parameter_system['gname_to_id_dict']

        param_expr = param_expr.strip()

        if len(param_expr) == 0:
            return []

        st = None
        pt = None
        try:
            st = parser.expr(param_expr)
            pt = st.totuple()
        except:
            print ( "==> Parsing Exception: " + str ( sys.exc_info() ) )

        parameterized_expr = None  # param_expr
        if pt != None:

            start_timer("All_Expression_Handler.recurse_tree_symbols" )
            parameterized_expr = self.recurse_tree_symbols ( lcl_name_ID_dict, pt, [] )
            stop_timer("All_Expression_Handler.recurse_tree_symbols" )
            
            if parameterized_expr != None:
            
                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]

        compressed_expr = parameterized_expr
        if False and (compressed_expr != None):
            # To speed things up, collapse adjacent strings within the expression
            #   So this:       [ 3, "*", "(", 22, "+", 5, ")" ]
            #   Becomes this:  [ 3, "*(", 22, "+", 5, ")" ]

            # Can't currently do this because the expression list is in MDL
            # Each token has to remain separate so the translation can be done
            
            compressed_expr = []
            next_str = None
            for token in parameterized_expr:
                if type(token) == int:
                    if next_str != None:
                        compressed_expr = compressed_expr + [next_str]
                        next_str = None
                    compressed_expr = compressed_expr + [token]
                else:
                    # This is a string so simply concatenate (no translation done here)
                    if next_str == None:
                        next_str = str(token)
                    else:
                        next_str = next_str + str(token)
            if next_str != None:
                # Append any remaining strings
                compressed_expr = compressed_expr + [next_str]
        return compressed_expr

    #@profile('Expression_Handler.count_stub')
    def count_stub ( self ):
        pass

    #@profile('Expression_Handler.recurse_tree_symbols')
    def recurse_tree_symbols ( self, local_name_ID_dict, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """
        self.count_stub()

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree

            terminal = False
            if len(pt) == 2:
                if type(pt[1]) == str:
                    terminal = True

            if terminal:
                # This is a 2-tuple with a type and value
                if pt[0] == token.NAME:
                    expression_keywords = self.get_expression_keywords()
                    if pt[1] in expression_keywords:
                        # This is a recognized name and not a user-defined symbol, so append the string itself
                        return current_expr + [ pt[1] ]
                    else:
                        # This must be a user-defined symbol, so check if it's in the dictionary
                        pt1_str = str(pt[1])
                        #if pt[1] in local_name_ID_dict:
                        if pt1_str in local_name_ID_dict:
                            # Append the integer ID to the list after stripping off the leading "g"
                            return current_expr + [ int(local_name_ID_dict[pt1_str][1:]) ]
                        else:
                            # Not in the dictionary, so append a None flag followed by the undefined name
                            return current_expr + [ None, pt[1] ]
                else:
                    # This is a non-name part of the expression
                    return current_expr + [ pt[1] ]
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( local_name_ID_dict, pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None


    #@profile('Expression_Handler.evaluate_parsed_expr_py')
    def evaluate_parsed_expr_py ( self, param_sys ):
        self.updating = True        # Set flag to check for self-references
        param_sys.recursion_depth += 1

        self.isvalid = False        # Mark as invalid and return None on any failure

        general_parameter_list = param_sys.general_parameter_list
        who_I_depend_on_list = self.who_I_depend_on.split()
        for I_depend_on in who_I_depend_on_list:
            if not general_parameter_list[I_depend_on].isvalid:
                print ( "Cannot evaluate " + self.name + " because " + general_parameter_list[I_depend_on].name + " is not valid." )
                self.isvalid = False
                self.pending_expr = self.expr
                param_sys.register_validity ( self.name, False )
                # Might want to propagate invalidity here as well ???
                param_sys.recursion_depth += -1
                self.updating = False
                print ( "Return from evaluate_parsed_expr_py with depth = " + str(param_sys.recursion_depth) )
                return None
            exec ( general_parameter_list[I_depend_on].name + " = " + str(general_parameter_list[I_depend_on].value) )
        #print ( "About to exec (" + self.name + " = " + self.parsed_expr_py + ")" )
        exec ( self.name + " = " + self.parsed_expr_py )
        self.isvalid = True
        self.pending_expr = ""
        param_sys.register_validity ( self.name, True )
        return ( eval ( self.name, locals() ) )


# Callbacks for Property updates appear to require global (non-member) functions
# This is circumvented by simply calling the associated member function passed as self

#@profile('update_parameter_name')
def update_parameter_name ( self, context ):
    start_timer('update_parameter_name')
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.par_name_changed ( context )
    stop_timer('update_parameter_name')

#@profile('update_parameter_expression')
def update_parameter_expression ( self, context ):
    start_timer('update_parameter_expression')
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.expression_changed ( context )
    stop_timer('update_parameter_expression')

#@profile('update_parameter_parsed_expression')
def update_parameter_parsed_expression ( self, context ):
    start_timer('update_parameter_parsed_expression')
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.parsed_expression_changed ( context )
    stop_timer('update_parameter_parsed_expression')

#@profile('update_parameter_value')
def update_parameter_value ( self, context ):
    start_timer('update_parameter_value')
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.value_changed ( context )
    stop_timer('update_parameter_value')

#@profile('print_parameter_details')
def print_parameter_details ( self, context ):
    start_timer('print_parameter_details')
    """ The "self" passed in is a Parameter_Data object. """
    if self.print_info:
        self.print_parameter()
        self.print_info = False
    stop_timer('print_parameter_details')


#@profile('dummy_update')
def dummy_update ( self, context ):
    start_timer('dummy_update')
    """ The "self" passed in is a Parameter_Data object. """
    stop_timer('dummy_update')
    pass


class Parameter_Data ( bpy.types.PropertyGroup, Expression_Handler ):
    """ Parameter - Contains the actual data for a parameter """
    name = StringProperty  ( name="ID Name", default="" )      # Unique Static Identifier used as the key to find this item in the collection
    expr = StringProperty  ( name="Expression", default="0", description="Expression to be evaluated for this parameter", update=update_parameter_expression )
    pending_expr = StringProperty ( default="" )     # Pending expression
    parsed_expr = StringProperty ( name="Parsed", default="", update=update_parameter_parsed_expression )
    parsed_expr_py = StringProperty ( name="Parsed_Python", default="" )
    value = FloatProperty ( name="Value", default=0.0, description="Current evaluated value for this parameter", update=update_parameter_value )
    isvalid = BoolProperty ( default=True )   # Boolean flag to signify that the value and float_value are accurate
    name_status = StringProperty ( name="Name Status", default="" )

    who_I_depend_on = StringProperty ( name="who_I_depend_on", default="" )
    who_depends_on_me = StringProperty ( name="who_depends_on_me", default="" )

    par_name = StringProperty ( name="Name", default="Unnamed", description="Name of this Parameter", update=update_parameter_name )  # User's name for this parameter - can be changed by the user
    old_par_name = StringProperty ( name="Name", default="", description="Old name of this Parameter" )  # Will generally be the same as the current name except during a name change
    units = StringProperty ( name="Units", default="none", description="Units for this Parameter" )
    descr = StringProperty ( name="Description", default="", description="Description of this Parameter" )

    show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    print_info = BoolProperty ( default=False, description="Print information about this parameter to the console", update=print_parameter_details ) # This was one way to attach an "operator" (button) to an actual property


    #panel_path may not be needed any more. It was used to find panel parameters, but they're now maintained as a centralized list
    #panel_path = StringProperty ( name="Panel Path", default="" )
    ispanel = BoolProperty ( default=False )  # Boolean flag to signify panel parameter
    isint = BoolProperty ( default=False )    # Boolean flag to signify an integer parameter
    initialized = BoolProperty(default=False) # Set to true by "init_par_properties"

    updating = BoolProperty(default=False)    # Set to true when changing a value to suppress infinite recursion
    disable_parse = BoolProperty ( default=True )   # Boolean flag to signify that this parameter should not be parsed at this time, start with True for speed!!
    

    def remove_properties ( self, context ):
        print ( "Removing all Parameter Data Properties ... not implemented yet!" )

    
    #@profile('Parameter_Data.__init__')
    def __init__ ( self ):
        print ( "The Parameter_Data.__init__ function has been called." )

    #@profile('Parameter_Data.init_par_properties')
    def init_par_properties ( self ):
        #print ( "Setting Defaults for a Parameter" )

        # TODO - C H E C K   F O R   D U P L I C A T E    N A M E S  !!!!!!!!

        self.pending_expr = ""
        self.parsed_expr_py = ""
        self.isvalid = True
        self.who_I_depend_on = ""
        self.who_depends_on_me = ""
        self.old_par_name = self.par_name
        self.units = ""
        self.descr = self.par_name + " Description"
        self.show_help = False
        #self.panel_path = ""
        self.name_status = ""
        self.ispanel = False
        self.isint = False
        self.initialized = True
        self.updating = False
        self.disable_parse = False

    #@profile('Parameter_Data.draw_details')
    def draw_details ( self, layout ):
        p = self
        layout.label("Internal Information:")
        layout.label(" Parameter Name = " + p.par_name)
        layout.label(" Parameter ID Name = " + p.name)
        layout.label(" Parameter Expression = " + p.expr)
        layout.label(" Parameter Pending Expression = " + p.pending_expr)
        layout.label(" Parameter Parsed Expression = " + p.parsed_expr)
        layout.label(" Parameter Parsed Python Expression = " + p.parsed_expr_py)
        layout.label(" Numeric Value = " + str(p.value))
        layout.label(" Description = " + p.descr )
        layout.label(" Is Valid Flag = " + str(p.isvalid))
        layout.label(" Name status = " + str(p.name_status))
        layout.label(" " + p.name + " depends on " + str(len(p.who_I_depend_on.split())) + " other parameters" )
        layout.label(" " + p.name + " depends on: " + p.who_I_depend_on)
        layout.label(" " + str(len(p.who_depends_on_me.split())) + " other parameters depend on " + p.name )
        layout.label(" Who depends on " + p.name + ": " + p.who_depends_on_me)
        layout.label(" Old Parameter Name = " + p.old_par_name)
        layout.label(" Is Panel = " + str(p.ispanel))
        layout.label(" Is Integer = " + str(p.isint))
        layout.label(" Initialized = " + str(p.initialized))
        # layout.label(" Panel Path = " + self.path_from_id())   # This really really slows down the interface!!

    #@profile('Parameter_Data.print_parameter')
    def print_parameter ( self ):
        p = self
        print ("Internal Information:")
        print (" Parameter Name = " + p.par_name)
        print (" Parameter ID Name = " + p.name)
        print (" Parameter Expression = " + p.expr)
        print (" Parameter Pending Expression = " + p.pending_expr)
        print (" Parameter Parsed Expression = " + p.parsed_expr)
        print (" Parameter Parsed Python Expression = " + p.parsed_expr_py)
        print (" Numeric Value = " + str(p.value))
        print (" Description = " + self.descr )
        print (" Is Valid Flag = " + str(p.isvalid))
        print (" Name status = " + str(p.name_status))
        print (" " + p.name + " depends on " + str(len(p.who_I_depend_on.split())) + " other parameters" )
        print (" " + p.name + " depends on: " + p.who_I_depend_on)
        print (" " + str(len(p.who_depends_on_me.split())) + " other parameters depend on " + p.name )
        print (" Who depends on " + p.name + ": " + p.who_depends_on_me)
        print (" Old Parameter Name = " + p.old_par_name)
        print (" Is Panel = " + str(p.ispanel))
        print (" Is Integer = " + str(p.isint))
        print (" Initialized = " + str(p.initialized))
        # print (" Panel Path = " + self.path_from_id())   # This really really slows down the interface!!


    #@profile('Parameter_Data.build_data_model_from_properties')
    def build_data_model_from_properties ( self ):
        p = self

        par_dict = {}
        par_dict['par_name'] = p.par_name
        par_dict['par_expression'] = p.expr
        par_dict['par_units'] = p.units
        par_dict['par_description'] = p.descr

        extras_dict = {}
        extras_dict['par_id_name'] = p.name
        extras_dict['par_value'] = p.value
        extras_dict['par_valid'] = p.isvalid

        par_dict['extras'] = extras_dict

        return par_dict


    #@profile('Parameter_Data.draw')
    def draw ( self, layout ):
        # This is generally not called, so show a banner if it is
        print ( "####################################################" )
        print ( "#######  ParameterData.draw was Called  ############" )
        print ( "####################################################" )


    #@profile('Parameter_Data.get_numeric_value')
    def get_numeric_value ( self ):
        return self.value


    #@profile('Parameter_Data.update_parsed_and_dependencies')
    def update_parsed_and_dependencies ( self, parameter_system ):
        general_parameter_list = parameter_system.general_parameter_list 
        old_who_I_depend_on_set = set(self.who_I_depend_on.split())
        
        expr_list = self.parse_param_expr ( self.expr, parameter_system )
        
        print ( "Expression List for " + str(self.expr) + " = " + str(expr_list) )

        if expr_list is None:
            self.parsed_expr = ""
            self.parsed_expr_py = ""
            self.who_I_depend_on = ""
            self.isvalid = False
            self.pending_expr = self.expr
            parameter_system.register_validity ( self.name, False )

        elif None in expr_list:
            self.isvalid = False
            self.pending_expr = self.expr
            parameter_system.register_validity ( self.name, False )
        else:
            self.parsed_expr = self.encode_expr_list_to_str ( expr_list )
            self.parsed_expr_py = self.build_py_expr_using_ids ( expr_list, general_parameter_list )
            who_I_depend_on_list = [ "g"+str(x) for x in expr_list if type(x) == int ]
            who_I_depend_on_list = [ p for p in set(who_I_depend_on_list) ]
            who_I_depend_on_str = spaced_strings_from_list ( who_I_depend_on_list )
            self.who_I_depend_on = who_I_depend_on_str
            
            new_who_I_depend_on_set = set(self.who_I_depend_on.split())
            remove_me_from_set = old_who_I_depend_on_set.difference(new_who_I_depend_on_set)
            add_me_to_set = new_who_I_depend_on_set.difference(old_who_I_depend_on_set)
            for remove_me_from in remove_me_from_set:
                p = general_parameter_list[remove_me_from]
                if self.name in p.who_depends_on_me:
                    # p.who_depends_on_me = spaced_strings_from_list ( [x for x in set(p.who_depends_on_me.split()).remove(self.name)] )
                    pset = set(p.who_depends_on_me.split())
                    pset.discard(self.name)
                    p.who_depends_on_me = spaced_strings_from_list ( [x for x in pset] )

            for add_me_to in add_me_to_set:
                p = general_parameter_list[add_me_to]
                if not self.name in p.who_depends_on_me:
                    p.who_depends_on_me = (p.who_depends_on_me + " " + self.name).strip()

            self.pending_expr = ""
            parameter_system.register_validity ( self.name, True )


    #@profile('Parameter_Data.par_name_changed')
    def par_name_changed ( self, context ):
        """
        This parameter's user name string has been changed.

        Update the entire parameter system based on a parameter's name being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the name is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend
        on this one so their expressions show the new name as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """

        if self.old_par_name == self.par_name:
            # Nothing to do
            self.name_status = ""
            return
        
        self.name_status = ""

        mcell = context.scene.mcell
        params = mcell.parameter_system
        general_param_list = params.general_parameter_list
        panel_param_list = params.panel_parameter_list

        #if params.suspend_evaluation:
        #    return


        # TODO - C H E C K   F O R   I L L E G A L   N A M E S   (currently using molecule name checking)  !!!!!!!!

        # Note that it would be good to call:
        #   self.report({'ERROR'}, status)
        # when name errors happen, but the report function is only associated with operators and not properties!!
        # The following logic somewhat works around it but requires the user to hit enter again to clear the error.

        name_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(name_filter, self.par_name)
        if m is None:
            # Don't allow the change, so change it back!!!
            bad_name = self.par_name
            self.par_name = self.old_par_name
            self.name_status = "Cannot change name from \"" + self.old_par_name + "\" to \"" + bad_name + "\" because \"" + bad_name + "\" is an illegal name."
            print ( self.name_status )
            return

        if self.name[0] == "g":
            # This is a general parameter which must also maintain unique user names
            if params.par_name_already_in_use ( self.par_name ):
                # Don't allow the change, so change it back!!!
                bad_name = self.par_name
                self.par_name = self.old_par_name
                self.name_status = "Cannot change name from \"" + self.old_par_name + "\" to \"" + bad_name + "\" because \"" + bad_name + "\" is already in use."
                print ( self.name_status )
                return
            params.update_name_ID_dictionary(self)

        self.name_status = ""
        self.old_par_name = self.par_name

        # Update any expressions that use this parameter (to change this name in their expressions)

        who_depends_on_me_list = self.who_depends_on_me.split()
        for pname in who_depends_on_me_list:
            p = None
            if pname[0] == "g":
                p = general_param_list[pname]
            else:
                p = panel_param_list[pname]
            p.regenerate_expr_from_parsed_expr ( general_param_list )

        # Check the parameters with errors in case this name change fixes any of them

        if len(params.param_error_list) > 0:
            # There are parameters with errors that this name change might fix
            param_error_names = params.param_error_list.split()
            for pname in param_error_names:
                # pname will be the name of a parameter that contains an error - possibly an invalid name!
                if pname != self.name:   # Some small attempt to avoid recursion?
                    p = None
                    if pname[0] == "g":
                        p = general_param_list[pname]
                    else:
                        p = panel_param_list[pname]
                    # "Touch" the parameter's expression to cause it to be re-evaluated
                    p.expr = p.expr


    #@profile('Parameter_Data.expression_changed')
    def expression_changed ( self, context ):
        """
        This parameter's expression string has been changed.

        Update the entire parameter system based on a parameter's expression being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the string expression is changed (either programatically or via the GUI).
        This function needs to update the parsed expression of this parameter based on the
        expression having changed.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        expr_list = self.parse_param_expr ( self.expr, params )
        if expr_list is None:
            print ( "ERROR ... expr_list = None!!!" )
            self.parsed_expr = ""
            self.parsed_expr_py = ""
            self.isvalid = False
            self.pending_expr = self.expr
            params.register_validity ( self.name, False )
        else:
            if None in expr_list:
                self.isvalid = False
                self.pending_expr = self.expr
                params.register_validity ( self.name, False )
            else:
                self.isvalid = True
                self.pending_expr = ""
                if (self.expr.strip() == "") and (self.parsed_expr != ""):
                    # When an expression is empty, it's value should be zero
                    self.parsed_expr = ""
                params.register_validity ( self.name, True )
            parsed_expr = self.encode_expr_list_to_str ( expr_list )
            if self.parsed_expr != parsed_expr:
                # Force an update by changing the property
                #print ( "Old expression of \"" + str(self.parsed_expr) + "\" != \"" + str(parsed_expr) + "\" making assignment..." )
                self.parsed_expr = parsed_expr



    #@profile('Parameter_Data.parsed_expression_changed')
    def parsed_expression_changed ( self, context ):
        """ 
        This parameter's parsed expression string has been changed.

        Update the parameter system based on a parameter's parsed expression being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the parsed expression is changed (either programatically or via the GUI).
        This function needs to evaluate the new parsed expression to produce an updated
        value for this expression.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        if self.parsed_expr == "":
            self.parsed_expr_py = ""
            self.who_I_depend_on = ""
            if self.value != 0:
                self.value = 0
        else:
            # self.update_parsed_and_dependencies(params)

            old_who_I_depend_on_set = set(self.who_I_depend_on.split())
            
            expr_list = self.decode_str_to_expr_list (self.parsed_expr )
            
            if expr_list is None:
                self.parsed_expr = ""
                self.parsed_expr_py = ""
                self.who_I_depend_on = ""
                self.isvalid = False
                self.pending_expr = self.expr
            elif None in expr_list:
                self.parsed_expr_py = ""
                self.who_I_depend_on = ""
                self.isvalid = False
                self.pending_expr = self.expr
            else:
                self.parsed_expr_py = self.build_py_expr_using_ids ( expr_list, gen_param_list )
                who_I_depend_on_list = [ "g"+str(x) for x in expr_list if type(x) == int ]
                who_I_depend_on_list = [ p for p in set(who_I_depend_on_list) ]
                who_I_depend_on_str = spaced_strings_from_list ( who_I_depend_on_list )
                self.who_I_depend_on = who_I_depend_on_str
                self.isvalid = True
                self.pending_expr = ""
            
            if self.isvalid:
                new_who_I_depend_on_set = set(self.who_I_depend_on.split())
                remove_me_from_set = old_who_I_depend_on_set.difference(new_who_I_depend_on_set)
                add_me_to_set = new_who_I_depend_on_set.difference(old_who_I_depend_on_set)
                for remove_me_from in remove_me_from_set:
                    p = gen_param_list[remove_me_from]
                    if self.name in p.who_depends_on_me:
                        # p.who_depends_on_me = spaced_strings_from_list ( [x for x in set(p.who_depends_on_me.split()).remove(self.name)] )
                        pset = set(p.who_depends_on_me.split())
                        pset.discard(self.name)
                        p.who_depends_on_me = spaced_strings_from_list ( [x for x in pset] )

                for add_me_to in add_me_to_set:
                    p = gen_param_list[add_me_to]
                    if not self.name in p.who_depends_on_me:
                        p.who_depends_on_me = (p.who_depends_on_me + " " + self.name).strip()

                count_down = 3
                done = False
                params.recursion_depth = 0
                while not done:
                    try:
                        params.recursion_depth = 0
                        value = self.evaluate_parsed_expr_py(params)
                        if value != None:
                            if self.value != value:
                                # Force an update by changing this parameters value
                                self.value = value
                            self.isvalid = True
                            self.pending_expr = ""
                        else:
                            self.isvalid = False
                            self.pending_expr = self.expr
                        done = True
                    except Exception as e:
                        print ( ">>>>>>>>>>>>>>>>\n\nGot an exception while evaluating ... try again\n\n>>>>>>>>>>>>>>>>" )
                        print ( "   Exception was " + str(e) )
                        count_down += -1
                        if count_down > 0:
                            done = False
                        else:
                            self.isvalid = False
                            self.pending_expr = self.expr
                            done = True
                params.recursion_depth = 0


    #@profile('Parameter_Data.value_changed')
    def value_changed ( self, context ):
        """ 
        Update the entire parameter system based on a parameter's value being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the value is changed (typically via an expression evaluation).
        This function needs to force the redraw of all values that depend on this one.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        # Force a redraw of the expression itself
        self.expr = self.expr

        # Propagate forward ...
        who_depends_on_me_list = []
        if (self.who_depends_on_me != None) and (self.who_depends_on_me != "") and (self.who_depends_on_me != "None"):
            who_depends_on_me_list = self.who_depends_on_me.split()
        for pname in who_depends_on_me_list:
            p = None
            if pname[0] == "g":
                p = gen_param_list[pname]
            else:
                p = params.panel_parameter_list[pname]
            if p != None:
                if p.updating:
                    # May or may not be an error? print ( "Warning: Circular reference detected when updating " + self.name + "(" + self.par_name + ")")
                    pass
                p.parsed_expr = p.parsed_expr




    #@profile('Parameter_Data.regenerate_expr_from_parsed_expr')
    def regenerate_expr_from_parsed_expr ( self, general_parameter_list ):
        expr_list = self.decode_str_to_expr_list ( self.parsed_expr )
        regen_expr = self.build_mdl_expr ( expr_list, general_parameter_list )
        if regen_expr != None:
            if self.expr != regen_expr:
                self.expr = regen_expr


    #@profile('Parameter_Data.build_mdl_expr')
    def build_mdl_expr ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into an MDL expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_mdl_expr did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it without translation
                    expr = expr + token
        return expr


class ParameterSystemPropertyGroup ( bpy.types.PropertyGroup ):
    """ Master list of all existing Parameters throughout the application """
    general_parameter_list = CollectionProperty ( type=Parameter_Data, name="GP List" )
    panel_parameter_list = CollectionProperty ( type=Parameter_Data, name="PP List" )
    
    # This might be needed to keep a mapping from user names to id names for parsing speed
    #general_name_to_id_list = CollectionProperty ( type=Name_ID_Data, name="Name ID" )
    
    active_par_index = IntProperty(name="Active Parameter", default=0)
    next_gid = IntProperty(name="Counter for Unique General Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    next_pid = IntProperty(name="Counter for Unique Panel Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    
    recursion_depth = IntProperty(default=0)  # Counts recursion depth

    param_display_mode_enum = [ ('one_line',  "One line per parameter", ""), ('two_line',  "Two lines per parameter", "") ]
    param_display_mode = bpy.props.EnumProperty ( items=param_display_mode_enum, default='one_line', name="Parameter Display Mode", description="Display layout for each parameter" )
    param_display_format = StringProperty ( default='%.6g', description="Formatting string for each parameter" )
    param_label_fraction = FloatProperty(precision=4, min=0.0, max=1.0, default=0.35, description="Width (0 to 1) of parameter's label")
    
    export_as_expressions = BoolProperty ( default=False, description="Export Parameters as Expressions rather than Numbers" )
    
    show_panel = BoolProperty(name="Show Panel", default=False)
    show_all_details = BoolProperty(name="Show All Details", default=False)
    print_panel = BoolProperty(name="Print Panel", default=True)
    param_error_list = StringProperty(name="Parameter Error List", default="")
    currently_updating = BoolProperty(name="Currently Updating", default=False)
    suspend_evaluation = BoolProperty(name="Suspend Evaluation", default=False)
    auto_update = BoolProperty ( name="Auto Update", default=True )

    #@profile('ParameterSystem.init_properties')
    def init_properties ( self ):
        if not ('gname_to_id_dict' in self):
            self['gname_to_id_dict'] = {}


    def remove_properties ( self, context ):
        print ( "Removing all Parameter System Properties ... not implemented yet!" )


    #@profile('ParameterSystem.allocate_available_gid')
    def allocate_available_gid ( self ):
        """ Return a unique parameter ID for a new parameter """
        if (len(self.general_parameter_list) <= 0) and (len(self.panel_parameter_list) <= 0):
            # Reset the ID to 1 when there are no more parameters
            self.next_gid = 1
        self.next_gid += 1
        return ( self.next_gid - 1 )


    #@profile('ParameterSystem.allocate_available_pid')
    def allocate_available_pid ( self ):
        """ Return a unique parameter ID for a new parameter """
        if (len(self.general_parameter_list) <= 0) and (len(self.panel_parameter_list) <= 0):
            # Reset the ID to 1 when there are no more parameters
            self.next_pid = 1
        self.next_pid += 1
        return ( self.next_pid - 1 )


    #@profile('ParameterSystem.get_parameter')
    def get_parameter ( self, unique_name, pp=False ):
        if pp:
            # Look for this name in the list of panel parameter references
            if unique_name in self.panel_parameter_list:
                return self.panel_parameter_list[unique_name]
            else:
                return None
        else:
            # Look for this name in the list of general parameter references
            if unique_name in self.general_parameter_list:
                return self.general_parameter_list[unique_name]
            else:
                return None


    #@profile('ParameterSystem.add_general_parameter_with_values')
    def add_general_parameter_with_values ( self, name, expression, units, description ):
        """ Add a new parameter to the list of parameters """
        p = self.new_parameter ( new_name=name, pp=False, new_expr=expression, new_units=units, new_desc=description )
        return p


    #@profile('ParameterSystem.new_parameter')
    def new_parameter ( self, new_name=None, pp=False, new_expr=None, new_units=None, new_desc=None ):
        """ Add a new parameter to the list of parameters """
        if new_name != None:
            if (not pp) and self.par_name_already_in_use(new_name):
                # Cannot use this name because it's already used by a general parameter
                # Could optionally return with an error,
                #   but for now, just set to None to pick an automated name
                new_name = None

        par_num = -1
        par_name = "undefinded"
        par_user_name = "undefined"
        if pp:
            # Set up a panel parameter
            par_num = self.allocate_available_pid()
            par_name = "p" + str(par_num)
            par_user_name = "PP" + str(par_num)
        else:
            # Set up a general parameter
            par_num = self.allocate_available_gid()
            par_name = "g" + str(par_num)
            par_user_name = "P" + str(par_num)

        if not (new_name is None):
            par_user_name = new_name

        if pp:
            # Create the parameter in the panel parameter list
            new_par = self.panel_parameter_list.add()
        else:
            # Create the parameter in the general parameter list
            new_par = self.general_parameter_list.add()

        new_par.disable_parse = True

        new_par.name = par_name
        new_par.par_name = par_user_name

        new_par.init_par_properties()

        if not (new_expr is None):
            new_par.expr = new_expr

        if not pp:
            self.update_name_ID_dictionary(new_par)

        if new_units != None:
            new_par.units = new_units
        if new_desc != None:
            new_par.descr = new_desc

        new_par.disable_parse = False

        return new_par


    #@profile('ParameterSystem.del_panel_parameter')
    def del_panel_parameter ( self, unique_name ):

        if unique_name[0] == 'p':
            p = self.panel_parameter_list[unique_name]

            # The parameters that I depend on have references to me that must be removed
            remove_me_from_set = set(p.who_I_depend_on.split())
            for remove_me_from in remove_me_from_set:
                rp = self.general_parameter_list[remove_me_from]
                if self.name in rp.who_depends_on_me:
                    rpset = set(rp.who_depends_on_me.split())
                    rpset.discard(p.name)
                    rp.who_depends_on_me = spaced_strings_from_list ( [x for x in rpset] )

            # Delete the parameter from the panel parameter list
            self.panel_parameter_list.remove(self.panel_parameter_list.find(unique_name))
        else:
            print ( "Warning: del_panel_parameter called on a non-panel parameter: " + unique_name )
            print ( "  Parameter " + unique_name + " was not deleted!!" )
            ## Delete the parameter from the general parameter list
            #self.general_parameter_list.remove(self.general_parameter_list.find(unique_name))
            ## Also delete it from the name to ID mapping (check first to avoid exception)
            #if unique_name in self['gname_to_id_dict'].keys():
            #    self['gname_to_id_dict'].pop(unique_name)


    #@profile('ParameterSystem.add_parameter')
    def add_parameter ( self, context ):
        """ Add a new parameter to the list of general parameters and set as the active parameter """
        p = self.new_parameter()
        self.active_par_index = len(self.general_parameter_list)-1
        return p

    #@profile('ParameterSystem.remove_active_parameter')
    def remove_active_parameter ( self, context ):
        """ Remove the active parameter from the list of parameters if not needed by others """
        status = ""
        if len(self.general_parameter_list) > 0:
            p = self.general_parameter_list[self.active_par_index]
            if p != None:
                ok_to_delete = True
                if p.who_depends_on_me != None:
                    who_depends_on_me = p.who_depends_on_me.strip()
                    if len(who_depends_on_me) > 0:
                        ok_to_delete = False
                        status = "Parameter " + p.par_name + " is used by: " + self.translated_param_name_list(who_depends_on_me)
                if ok_to_delete:
                    # The parameters that I depend on have references to me that must be removed
                    remove_me_from_set = set(p.who_I_depend_on.split())
                    for remove_me_from in remove_me_from_set:
                        rp = self.general_parameter_list[remove_me_from]
                        if self.name in rp.who_depends_on_me:
                            rpset = set(rp.who_depends_on_me.split())
                            rpset.discard(p.name)
                            rp.who_depends_on_me = spaced_strings_from_list ( [x for x in rpset] )

                    # Remove this name from the gname to id dictionary
                    # print ( "Testing if " + p.par_name + " is in " + str(self['gname_to_id_dict'].keys()) )
                    if p.par_name in self['gname_to_id_dict'].keys():
                        self['gname_to_id_dict'].pop(p.par_name)
                    
                    # Remove this parameter from the general parameter list and move the pointer
                    self.general_parameter_list.remove ( self.active_par_index )
                    self.active_par_index -= 1
                    if self.active_par_index < 0:
                        self.active_par_index = 0

        return ( status )



    #@profile('ParameterSystem.build_dependency_ordered_name_list')
    def build_dependency_ordered_name_list ( self ):
        print ( "Building Dependency Ordered Name List" )
        ol = []
        if len(self.general_parameter_list) > 0:
            gl = self.general_parameter_list;
            gs = set(gl.keys())
            print ( " general parameter set (gs) = " + str(gs) )
            while len(gs) > len(ol):
                defined_set = set(ol)
                print ( "  In while with already defined_set = " + str(defined_set) )
                for n in gs:
                    print ( n + " is " + gl[n].par_name + ", depends on (" + gl[n].who_I_depend_on + "), and depended on by (" + gl[n].who_depends_on_me + ")" )
                    print ( "   Checking for " + n + " in the defined set" )
                    if not ( n in defined_set):
                        print ( "     " + n + " is not defined yet, check if it can be" )
                        dep_set = set(gl[n].who_I_depend_on.split())
                        if dep_set.issubset(defined_set):
                            print ( "       " + n + " is now defined since all its dependencies are defined." )
                            ol.append ( n );
                            defined_set = set(ol)
        return ol



    #@profile('ParameterSystem.register_validity')
    def register_validity ( self, name, valid ):
        """ Register the global validity or invalidity of a parameter """
        if valid:
            # Check to see if it's in the list and remove it
            if name in self.param_error_list:
                param_error_names = self.param_error_list.split()    # Convert to a list
                while name in param_error_names:                 # Remove all references
                    param_error_names.remove(name)
                self.param_error_list = spaced_strings_from_list(param_error_names)  # Rebuild the string
        else:
            # Check to see if it's in the list and add it
            if not (name in self.param_error_list):
                self.param_error_list = self.param_error_list + " " + name

    #@profile('ParameterSystem.translated_param_name_list')
    def translated_param_name_list ( self, param_name_string ):
        param_list = param_name_string.split()
        name_list = ""
        for name in param_list:
            if len(name_list) > 0:
                name_list = name_list + " "
            if name[0] == 'g':
                name_list = name_list + self.general_parameter_list[name].par_name
            else:
                name_list = name_list + self.panel_parameter_list[name].par_name
        return name_list

    #@profile('ParameterSystem.draw')
    def draw ( self, layout ):
        pass

    #@profile('ParameterSystem.print_general_parameter_list')
    def print_general_parameter_list ( self ):
        print ( "General Parameters:" )
        for p in self.general_parameter_list:
            p.print_parameter()

    #@profile('ParameterSystem.print_panel_parameter_list')
    def print_panel_parameter_list ( self ):
        print ( "Panel Parameters:" )
        for p in self.panel_parameter_list:
            p.print_parameter()


    #@profile('ParameterSystem.build_data_model_from_properties')
    def build_data_model_from_properties ( self, context ):
        print ( "Parameter System building Data Model" )
        par_sys_dm = {}
        gen_par_list = []
        for p in self.general_parameter_list:
            gen_par_list.append ( p.build_data_model_from_properties() )
        par_sys_dm['model_parameters'] = gen_par_list
        return par_sys_dm



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading ParameterSystemPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade ParameterSystemPropertyGroup data model to current version." )
            return None

        return dm



    #@profile('ParameterSystem.build_data_model_from_properties')
    def build_properties_from_data_model ( self, context, par_sys_dm ):
        # Check that the data model version matches the version for this property group
        if par_sys_dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )

        print ( "Parameter System building Properties from Data Model ..." )
        while len(self.general_parameter_list) > 0:
            self.general_parameter_list.remove(0)
        self['gname_to_id_dict'] = {}
        self.next_gid = 1
        if 'model_parameters' in par_sys_dm:
            # Add all of the parameters - some will be invalid if they depend on other parameters that haven't been read yet
            for p in par_sys_dm['model_parameters']:
                print ( "Adding " + p['par_name'] + " = " + p['par_expression'] + " (" + p['par_units'] + ") ... " + p['par_description'] )
                self.add_general_parameter_with_values ( p['par_name'], p['par_expression'], p['par_units'], p['par_description'] )

            # Update the parameter expressions for any that were invalid after all have been added
            last_num_invalid = 0
            keep_checking = True
            while keep_checking:
                num_invalid = 0
                for p in self.general_parameter_list:
                    if not p.isvalid:
                        num_invalid +=1
                        # Assign it again to force an evaluation after all other parameters have been added
                        p.expr = p.expr
                if num_invalid == last_num_invalid:
                    # No parameters have been updated, so exit (even if there are some remaining invalid)
                    keep_checking = False



    #@profile('ParameterSystem.print_name_id_map')
    def print_name_id_map ( self ):
        gname_dict = self['gname_to_id_dict']
        print ( "Name to ID Map:" )
        for k,v in gname_dict.items():
            print ( "  gname: " + str(k) + " = " + str(v) )


    #@profile('ParameterSystem.par_name_already_in_use')
    def par_name_already_in_use ( self, par_name ):
        return par_name in self['gname_to_id_dict']


    #@profile('ParameterSystem.update_name_ID_dictionary')
    def update_name_ID_dictionary ( self, param ):
        gname_dict = self['gname_to_id_dict']

        if (len(param.old_par_name) > 0) and (param.old_par_name != param.par_name):
            # This is a name change, so remove the old name first
            while param.old_par_name in gname_dict:
                gname_dict.pop(param.old_par_name)

        # Perform the update
        gname_dict[param.par_name] = param.name

        # Remove all entries that match the new name (if any)
        #while param.par_name in gname_dict:
        #    gname_dict.pop(param.par_name)

        # Add the new entry
        #gname_dict[param.par_name] = param.name


    #@profile('MCELL_PT_parameter_system.draw_layout')
    def draw_layout (self, context, layout):
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            
            if ps.param_error_list != "":
                row = layout.row()
                row.label(text="Error with: " + ps.translated_param_name_list(ps.param_error_list), icon='ERROR')

            row = layout.row()

            col = row.column()
            col.template_list("MCELL_UL_draw_parameter", "parameter_system",
                              ps, "general_parameter_list",
                              ps, "active_par_index", rows=5)

            col = row.column(align=True)

            subcol = col.column(align=True)
            subcol.operator("mcell.add_parameter", icon='ZOOMIN', text="")
            subcol.operator("mcell.remove_parameter", icon='ZOOMOUT', text="")

            if len(ps.general_parameter_list) > 0:

                if str(ps.param_display_mode) != "none":
                    par = ps.general_parameter_list[ps.active_par_index]

                    row = layout.row()
                    if par.name_status == "":
                        layout.prop(par, "par_name")
                    else:
                        #layout.prop(par, "par_name", icon='ERROR')
                        layout.prop(par, "par_name")
                        row = layout.row()
                        row.label(text=str(par.name_status), icon='ERROR')
                    if len(par.pending_expr) > 0:
                        layout.prop(par, "expr")
                        row = layout.row()
                        row.label(text="Undefined Expression: " + str(par.pending_expr), icon='ERROR')
                    elif not par.isvalid:
                        layout.prop(par, "expr", icon='ERROR')
                        row = layout.row()
                        row.label(text="Invalid Expression: " + str(par.pending_expr), icon='ERROR')
                    else:
                        layout.prop(par, "expr")
                    layout.prop(par, "units")
                    layout.prop(par, "descr")


            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if not ps.show_panel:
                row.prop(ps, "show_panel", text="Parameter Options", icon='TRIA_RIGHT', emboss=False)
            else:
                col = row.column()
                col.alignment = 'LEFT'
                col.prop(ps, "show_panel", text="Parameter Options", icon='TRIA_DOWN', emboss=False)
                col = row.column()
                col.prop(ps, "show_all_details", text="Show Internal Details for All")

                if ps.show_all_details:
                    col = row.column()
                    #detail_box = None
                    if len(ps.general_parameter_list) > 0:
                        par = ps.general_parameter_list[ps.active_par_index]
                        col.prop(par,"print_info", text="Print to Console", icon='LONGDISPLAY' )
                        detail_box = box.box()
                        par.draw_details(detail_box)
                    else:
                        detail_box = box.box()
                        detail_box.label(text="No General Parameters Defined")
                    if len(ps.param_error_list) > 0:
                        error_names_box = box.box()
                        param_error_names = ps.param_error_list.split()
                        for name in param_error_names:
                            error_names_box.label(text="Parameter Error for: " + name, icon='ERROR')

                row = box.row()
                row.prop(ps, "param_display_mode", text="Parameter Display Mode")
                row = box.row()
                row.prop(ps, "param_display_format", text="Parameter Display Format")
                row = box.row()
                row.prop(ps, "param_label_fraction", text="Parameter Label Fraction")

                row = box.row()
                row.prop(ps, "export_as_expressions", text="Export Parameters as Expressions (experimental)")

                row = box.row()
                row.operator("mcell.print_profiling", text="Print Profiling")
                row.operator("mcell.clear_profiling", text="Clear Profiling")

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


    def draw_label_with_help ( self, layout, label, prop_group, show, show_help, help_string ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=label )
        col = split.column()
        col.label ( text="" )
        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
          row = layout.row()
          # Use a split with two columns to indent the box
          split = row.split(0.03)
          col = split.column()
          col = split.column()
          box = col.box()
          desc_list = help_string.split("\n")
          for desc_line in desc_list:
              box.label (text=desc_line)


    def draw_prop_with_help ( self, layout, prop_label, prop_group, prop, show, show_help, help_string ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=prop_label )
        col = split.column()
        col.prop ( prop_group, prop, text="" )
        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
          row = layout.row()
          # Use a split with two columns to indent the box
          split = row.split(0.03)
          col = split.column()
          col = split.column()
          box = col.box()
          desc_list = help_string.split("\n")
          for desc_line in desc_list:
              box.label (text=desc_line)


    def draw_prop_search_with_help ( self, layout, prop_label, prop_group, prop, prop_parent, prop_list_name, show, show_help, help_string, icon='FORCE_LENNARDJONES' ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=prop_label )
        col = split.column()
        #col.prop ( prop_group, prop, text="" )

        #layout.prop_search(rel, "molecule", mcell.molecules, "molecule_list", text="Molecule", icon='FORCE_LENNARDJONES')
        col.prop_search( prop_group, prop, prop_parent, prop_list_name, text="", icon=icon)

        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
          row = layout.row()
          # Use a split with two columns to indent the box
          split = row.split(0.03)
          col = split.column()
          col = split.column()
          box = col.box()
          desc_list = help_string.split("\n")
          for desc_line in desc_list:
              box.label (text=desc_line)



def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)

def unregister():
    print ("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

