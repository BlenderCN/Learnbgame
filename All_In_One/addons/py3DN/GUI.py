# Author: Paulo de Castro Aguiar	
# Date: July 2012
# email: pauloaguiar@fc.up.pt

"""Create py3DN GUI in Blender"""

import bpy
from bpy.props import *

import time

from DataContainers import *
import InterpolateFun
import DrawingFun
import DrawingXtras
import NeuroLucidaXMLParser

import myconfig
from mytools import *



def initSceneMyDrawTools(scn):

    # prepare blender
    # initialize parameters

    bpy.types.Scene.MyDrawTools_ContoursDraw = BoolProperty( name = "", description = "draw contours?")
    scn['MyDrawTools_ContoursDraw'] = True
    bpy.types.Scene.MyDrawTools_TreesDraw = BoolProperty( name = "", description = "draw trees?" )
    scn['MyDrawTools_TreesDraw'] = True
    bpy.types.Scene.MyDrawTools_SpinesDraw = BoolProperty( name = "", description = "draw spines?" )
    scn['MyDrawTools_SpinesDraw'] = False
    bpy.types.Scene.MyDrawTools_VaricosDraw = BoolProperty( name = "", description = "draw varicosities?" )
    scn['MyDrawTools_VaricosDraw'] = False

    # set base layer (bl): cellbody bl, trees bl+1, spines bl+2, varicos bl+3, structs bl+4, math bl+5    
    bpy.types.Scene.MyDrawTools_BaseLayer = IntProperty( name = "base layer", description = "first layer to be used", default = 0, min = 0, max = 19  )
    scn['MyDrawTools_BaseLayer'] = 0

    bpy.types.Scene.MyDrawTools_Interpolation = IntProperty( name = "interpolation degree", description = "interpolation degree used in Bezier curves", default = 0, min = 0, max = 2  )
    scn['MyDrawTools_Interpolation'] = 0

    bpy.types.Scene.MyDrawTools_Status = StringProperty( name = "MyDrawTools_Status", description = "status" )
    scn['MyDrawTools_Status'] = 'choose minimal_d and load an xml file'

    bpy.types.Scene.MyDrawTools_LoadedNeurons = StringProperty( name = "MyDrawTools_LoadedNeurons", description = "number of loaded neurons" )
    scn['MyDrawTools_LoadedNeurons'] = 'loaded neurons: 0'
    bpy.types.Scene.MyDrawTools_SelectedNeuron = IntProperty( name = "select", description = "selected neuron where operations are applyed", default = -1, min = -1, max = -1 )
    scn['MyDrawTools_SelectedNeuron'] = -1

    bpy.types.Scene.MyDrawTools_ContoursDetail = IntProperty( name = "detail", description = "contours level of detail", default = 2, min = 1, max = 8 )
    scn['MyDrawTools_ContoursDetail'] = 2
    bpy.types.Scene.MyDrawTools_TreesDetail = IntProperty( name = "detail", description = "trees level of detail", default = 6, min = 4, max = 32 )
    scn['MyDrawTools_TreesDetail'] = 6
    bpy.types.Scene.MyDrawTools_SpinesDetail = IntProperty( name = "detail", description = "spines level of detail", default = 4, min = 4, max = 32 )
    scn['MyDrawTools_SpinesDetail'] = 4
    bpy.types.Scene.MyDrawTools_VaricosDetail = IntProperty( name = "detail", description = "varicosities level of detail", default = 4, min = 4, max = 32 )
    scn['MyDrawTools_VaricosDetail'] = 4

    bpy.types.Scene.MyDrawTools_MinimalD = FloatProperty( name = "minimal d [um]", description = "minimal diameter/distance [um]", default = 0.17, min = 0.0, max = 10.0 )
    scn['MyDrawTools_MinimalD'] = 0.17
    
    bpy.types.Scene.MyDrawTools_RemovePoints = BoolProperty( name = "apply point removal", description = "remove points which are closer than minimal d" )
    scn['MyDrawTools_RemovePoints'] = False

    bpy.types.Scene.MyDrawTools_TreeSomaAttach = BoolProperty( name = "tree-soma attach", description = "extend the dendrites to ensure cell body attachment" )
    scn['MyDrawTools_TreeSomaAttach'] = False

    bpy.types.Scene.MyDrawTools_SpinesDiam = FloatProperty( name = "force diam [um]", description = "force spines' minimal diameter [um]", default = 1.0, min = 0.0, max = 10.0 )
    scn['MyDrawTools_SpinesDiam'] = 1.0
    bpy.types.Scene.MyDrawTools_SpinesForceDiam = BoolProperty( name = "", description = "override spines diameter" )
    scn['MyDrawTools_SpinesForceDiam'] = False

    bpy.types.Scene.MyDrawTools_VaricosDiam = FloatProperty( name = "force diam [um]", description = "force varicosities minimal diameter [um]", default = 1.0, min = 0.0, max = 10.0 )
    scn['MyDrawTools_VaricosDiam'] = 1.0
    bpy.types.Scene.MyDrawTools_VaricosForceDiam = BoolProperty( name = "", description = "overridedraw varicosities" )
    scn['MyDrawTools_VaricosForceDiam'] = False

    bpy.types.Scene.MyDrawTools_ContoursVCost = StringProperty( name = "MyDrawTools_ContoursVCost", description = "contours vertices cost" )
    scn['MyDrawTools_ContoursVCost'] = 'vcost=0'
    bpy.types.Scene.MyDrawTools_TreesVCost = StringProperty( name = "MyDrawTools_TreesVCost", description = "trees vertices cost" )
    scn['MyDrawTools_TreesVCost'] = 'vcost=0'
    bpy.types.Scene.MyDrawTools_SpinesVCost = StringProperty( name = "MyDrawTools_SpinesVCost", description = "spines vertices cost" )
    scn['MyDrawTools_SpinesVCost'] = 'vcost=0'
    bpy.types.Scene.MyDrawTools_VaricosVCost = StringProperty( name = "MyDrawTools_VaricosVCost", description = "varicos vertices cost" )
    scn['MyDrawTools_VaricosVCost'] = 'vcost=0'


#---------------------------------------------------------------------------------------------------------------


class BlendingNeuronsUIPanel(bpy.types.Panel):
    bl_label = "Neuronal Morphometric Analysis"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):

        layout = self.layout
        scn = context.scene

        layout.label("Paulo Aguiar and Peter Szucs", icon='ARMATURE_DATA')
        layout.label("pauloaguiar@fc.up.pt", icon='WORLD')

        row = layout.row()
        
        layout.label( scn['MyDrawTools_Status'], icon='OUTLINER_OB_LAMP' )
        layout.operator( "mydrawtools.loadxml", icon='DISK_DRIVE' )
        row = layout.row(align = False)
        row.alignment = 'EXPAND'   
        row.label( scn['MyDrawTools_LoadedNeurons'], icon='PACKAGE' )
        row.prop( scn, 'MyDrawTools_SelectedNeuron' )

        # ------------------------------------------------------

        row = layout.row(align = True)        
        row.alignment = 'EXPAND'        
        row.label("Contours:", icon='MESH_ICOSPHERE')
        row.prop(scn, 'MyDrawTools_ContoursDraw' )
        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_ContoursDetail' )
        row.label( scn['MyDrawTools_ContoursVCost'], icon='ORTHO' )

        # ------------------------------------------------------

        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.label("Trees:", icon='MESH_ICOSPHERE')
        row.prop(scn, 'MyDrawTools_TreesDraw' )
        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_TreesDetail' )
        row.label( scn['MyDrawTools_TreesVCost'], icon='ORTHO' )        
        layout.prop(scn, 'MyDrawTools_MinimalD' )
        row = layout.row(align = True)        
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_RemovePoints', icon='PARTICLE_POINT' )
        row.prop(scn, 'MyDrawTools_TreeSomaAttach', icon='CONSTRAINT' )
        layout.prop(scn, 'MyDrawTools_Interpolation' )        
        
        # ------------------------------------------------------

        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.label("Spines:", icon='MESH_ICOSPHERE')
        row.prop(scn, 'MyDrawTools_SpinesDraw' )
        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_SpinesDetail' )
        row.label( scn['MyDrawTools_SpinesVCost'], icon='ORTHO' )
        row = layout.row(align = True)        
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_SpinesDiam' )
        row.prop(scn, 'MyDrawTools_SpinesForceDiam', icon='FORCE_FORCE' )

        # ------------------------------------------------------

        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.label("Varicosities:", icon='MESH_ICOSPHERE')
        row.prop(scn, 'MyDrawTools_VaricosDraw' )
        row = layout.row(align = True)
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_VaricosDetail' )
        row.label( scn['MyDrawTools_VaricosVCost'], icon='ORTHO' )
        row = layout.row(align = True)        
        row.alignment = 'EXPAND'
        row.prop(scn, 'MyDrawTools_VaricosDiam' )
        row.prop(scn, 'MyDrawTools_VaricosForceDiam', icon='FORCE_FORCE' )

        # ------------------------------------------------------

        row = layout.row(align = True)
        
        layout.operator("mydrawtools.interpolate", icon='ORTHO' )

        row = layout.row(align = True)        
        row.alignment = 'EXPAND'
        row.operator("mydrawtools.set3d", icon='GROUP')
        row.prop(scn, 'MyDrawTools_BaseLayer' )

        layout.operator("mydrawtools.drawall", icon='SCRIPT')


#---------------------------------------------------------------------------------------------------------------


class OBJECT_OT_MyDrawTools_LoadXML(bpy.types.Operator):

    bl_idname = "mydrawtools.loadxml"
    bl_label  = "Load XML file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scn = bpy.context.scene
        scn['MyDrawTools_Status'] = 'parsing XML file - please wait...'
        # Update Info ( SelectedNeuron will be needed to the following functions )
        total_neurons = len( myconfig.neuron ) + 1
        scn['MyDrawTools_LoadedNeurons'] = 'loaded neurons: ' + str( total_neurons )
        bpy.types.Scene.MyDrawTools_SelectedNeuron = IntProperty( name = "select", description = "selected neuron where operations will applyed", default = total_neurons - 1, min = 0, max = total_neurons - 1 )
        scn['MyDrawTools_SelectedNeuron'] = total_neurons - 1
        # XML parsing
        NeuroLucidaXMLParser.Load_Neuron( self.filepath, bpy.context.scene['MyDrawTools_MinimalD'], bpy.context.scene['MyDrawTools_RemovePoints'] )
        scn['MyDrawTools_Status'] = 'XML file loaded!'
        # Interpolation
        bpy.ops.mydrawtools.interpolate()
        # ease typing
        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#---------------------------------------------------------------------------------------------------------------


class OBJECT_OT_MyDrawTools_Interpolate(bpy.types.Operator):
    bl_idname = "mydrawtools.interpolate"
    bl_label = "Interpolate and Update VCost"

    def execute(self, context):

        scn = bpy.context.scene

        selected_neuron = scn['MyDrawTools_SelectedNeuron']
        neuron          = myconfig.neuron[    selected_neuron]
        morphology      = myconfig.morphology[selected_neuron]

        InterpolateFun.Interpolate_Objects( neuron, morphology, scn['MyDrawTools_ContoursDetail'], scn['MyDrawTools_Interpolation'], scn['MyDrawTools_MinimalD'] )

        total_points  = 0
        total_spines  = 0
        total_varicos = 0
        total_contour_points = 0

        for s in range(0, morphology.total_structures):
            for c in range(0, morphology.structure[s].total_contours):
                total_contour_points += morphology.structure[s].rawcontour[c].total_points

        for i in range(0, neuron.total_trees):
            total_points  += neuron.tree[i].total_rawpoints
            total_spines  += neuron.tree[i].total_spines
            total_varicos += neuron.tree[i].total_varicosities


        scn['MyDrawTools_ContoursVCost'] = 'vcost=' + str( scn['MyDrawTools_ContoursDetail'] * total_contour_points )
        i = scn['MyDrawTools_Interpolation']
        scn['MyDrawTools_TreesVCost'] = 'vcost=' + str( scn['MyDrawTools_TreesDetail'] * total_points * ( i + 1 ) )
        scn['MyDrawTools_SpinesVCost'] = 'vcost=' + str( scn['MyDrawTools_SpinesDetail'] * total_spines * 2 )
        v = scn['MyDrawTools_VaricosDetail']
        scn['MyDrawTools_VaricosVCost'] = 'vcost=' + str( (v*v-(v-2)) * total_varicos )

        return{'FINISHED'}   


#---------------------------------------------------------------------------------------------------------------


class OBJECT_OT_MyDrawTools_DrawAll(bpy.types.Operator):
    bl_idname = "mydrawtools.drawall"
    bl_label = "Draw 3D Reconstruction"

    def execute(self, context):

        t0 = time.clock()

        selected_neuron = bpy.context.scene['MyDrawTools_SelectedNeuron']
        neuron          = myconfig.neuron[    selected_neuron]
        morphology      = myconfig.morphology[selected_neuron]

        DrawingFun.Draw_Objects( neuron, morphology )
        print( '\n\n{0:.2f} seconds total processing time'.format( time.clock() - t0 ) )    

        return{'FINISHED'}    
        

#---------------------------------------------------------------------------------------------------------------


class OBJECT_OT_MyDrawTools_Set3D(bpy.types.Operator):
    bl_idname = "mydrawtools.set3d"
    bl_label = "Set 3D View"

    def execute(self, context):
        
        # be sure that the visualization properties are adequate for the neuron dimensions
        bpy.context.scene.layers = [True]*20
        for area in bpy.context.screen.areas :
            if area.type == 'VIEW_3D':
                area.spaces.active.clip_start = 0.0
                area.spaces.active.clip_end   = 100000.0
                area.spaces.active.grid_lines = 32
                area.spaces.active.grid_scale = 500.0

        for obj in bpy.data.objects :
            if obj.name == 'Camera':
                #obj.data.draw_size = 1
                obj.scale = [500.0, 500.0, 500.0]
                obj.data.clip_start = 0.0
                obj.data.clip_end   = 100000.0
                obj.data.lens       = 30.0
            if obj.name == 'Lamp' :
                obj.data.distance   = 1000.0
                obj.scale = [500.0, 500.0, 500.0]


        return{'FINISHED'}    


#---------------------------------------------------------------------------------------------------------------


# Initialization
initSceneMyDrawTools( bpy.context.scene )
       
# Registration
bpy.utils.register_module(__name__)

