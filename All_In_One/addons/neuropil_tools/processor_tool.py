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
This file contains the classes for Diameter Tool.

"""

# stuff to call Volrover individual executables
import sys
import subprocess
import os
import difflib
import re
import itertools
#import numpy

# blender imports
import bpy
# IMPORT SWIG MODULE(s)
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, \
    IntVectorProperty, PointerProperty, StringProperty
import mathutils

from bpy_extras.io_utils import ImportHelper


# python imports

import re
from  re import compile
import numpy as np
import neuropil_tools
import cellblender
import gamer

# register and unregister are required for Blender Addons
# We use per module class registration/unregistration


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

#Define operators

#spine_trace_filter_name = ""

#PSD_trace_filter_name= ""

trace_filter_name = ""

class NEUROPIL_OT_impser(bpy.types.Operator, ImportHelper):
    """Import from RECONSTRUCT Series file format (.ser)"""
    bl_idname = "processor_tool.impser"
    bl_label = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_description = 'Import from RECONSTRUCT Series File Format (.ser)'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}            

    filename_ext = ".ser"
    filter_glob = StringProperty(default="*.ser", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):  
        context.scene.test_tool.generate_contour_list(context,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}       


class NEUROPIL_OT_spine_namestruct(bpy.types.Operator):
    bl_idname = "processor_tool.spine_namestruct"
    bl_label = "Define Naming Pattern for Main Object"    
    bl_description = "Define Naming Pattern for Main Object"    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'} 

    spine_namestruct_name = StringProperty(name = "Name: ", description = "Assign Spine Name", default = "")
  
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        context.scene.test_tool.spine_namestruct(context, self.spine_namestruct_name)
        return {'FINISHED'}   


class NEUROPIL_OT_psd_namestruct(bpy.types.Operator):
    bl_idname = "processor_tool.psd_namestruct"
    bl_label = "Define Naming Pattern for Meta Object"    
    bl_description = "Define Naming Pattern for Meta Object"    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'} 

    PSD_namestruct_name = StringProperty(name = "Name: ", description = "Assign PSD Name", default = "")
  
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
   
    def execute(self, context):
        context.scene.test_tool.PSD_namestruct(context, self.PSD_namestruct_name)
        return {'FINISHED'}   

class NEUROPIL_OT_central_namestruct(bpy.types.Operator):
    bl_idname = "processor_tool.central_namestruct"
    bl_label = "Define Name for Central (shaft) Object"    
    bl_description = "Define Name for Central (shaft) Object"    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'} 

    central_namestruct_name = StringProperty(name = "Name: ", description = "Assign Central Object Name", default = "")
  
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
   
    def execute(self, context):
        context.scene.test_tool.central_namestruct(context, self.central_namestruct_name)

        return {'FINISHED'}   




class NEUROPIL_OT_include_contour(bpy.types.Operator):
    bl_idname = "processor_tool.include_contour"
    bl_label = "Add Selected Contour to Include List"    
    bl_description = "Add Selected Contour to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.include_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_include_filter_contour(bpy.types.Operator):
    bl_idname = "processor_tool.include_filter_contour"
    bl_label = "Add All Filtered Contours to Include List"    
    bl_description = "Add All Filtered Contours to Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.include_filter_contour(context)
        return {'FINISHED'}


class NEUROPIL_OT_remove_contour(bpy.types.Operator):
    bl_idname = "processor_tool.remove_contour"
    bl_label = "Remove Selected Contour and Mesh from Include List"
    bl_description = "Remove Selected Contour and Mesh from Include List"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_contour(context)
        return {'FINISHED'}

class NEUROPIL_OT_remove_contour_all(bpy.types.Operator):
    bl_idname = "processor_tool.remove_contour_all"
    bl_label = "Clear All Contours from Trace List"
    bl_description = "Clear All Contours from Trace List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_contour_all(context)
        return {'FINISHED'}

class NEUROPIL_OT_remove_comp(bpy.types.Operator):
    bl_idname = "processor_tool.remove_components"
    bl_label = "Remove Multiple Components tag"    
    bl_description = "Remove Multiple Components tag"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.remove_components(context)
        return {'FINISHED'}   


class NEUROPIL_OT_tile_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.generate_mesh_object"
    bl_label = "Interpolate and Generate Meshes from All Included Contours"    
    bl_description = "Interpolate and Generate Meshes from All Included Contours"    
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        context.scene.test_tool.generate_mesh_object(context)
        context.scene.test_tool.fix_mesh(context,"double")
        return {'FINISHED'}


class NEUROPIL_OT_tile_one_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.generate_mesh_object_single"
    bl_label = "Interpolate and Generate Meshes from Selected Contour"    
    bl_description = "Interpolate and Generate Meshes from Selected Contour"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.scene.test_tool.generate_mesh_object_single(context)
        context.scene.test_tool.fix_mesh(context,"single")
        return {'FINISHED'}


class NEUROPIL_OT_fix_mesh(bpy.types.Operator):
    bl_idname = "processor_tool.fix_mesh"
    bl_label = "Fix Mesh Object"
    bl_description = "Fix Mesh Object"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.fix_mesh(context,"single")
        return {'FINISHED'}   


class NEUROPIL_OT_select_obje(bpy.types.Operator):
    bl_idname = "processor_tool.select_obje"
    bl_label = "Select Faces of OBJ"
    bl_description = "Select Faces of OBJ"    
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obje(context,'spine')
        return {'FINISHED'}


#class NEUROPIL_OT_ImportMultipleObjs(bpy.types.Operator, ImportHelper):
#    """This appears in the tooltip of the operator and in the generated docs"""
#    bl_idname = "import_scene.multiple_objs"
#    bl_label = "Import multiple OBJ's"
#    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
#    filename_ext = ".obj"

#    filter_glob = StringProperty(
#            default="*.obj",
#            options={'HIDDEN'},
#            )

    #def execute(self, context):
    #    context.object.processor.multiple_objs(context)
    #    return {'FINISHED'}


class NEUROPIL_OT_smooth(bpy.types.Operator):
    bl_idname = "processor_tool.smooth"
    bl_label = "Smooth Object"
    bl_description = "Smooth Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.select_obje(context,'spine')
        context.active_object.processor.smooth(context)
        return {'FINISHED'}


class NEUROPIL_OT_smooth_all(bpy.types.Operator):
    bl_idname = "processor_tool.smooth_all"
    bl_label = "Smooth All"
    bl_description = "Smooth All"
    bl_options = {'REGISTER', 'UNDO'}
  
    spine_namestruct_name = StringProperty(name = "Name: ", description = "Assign Spine Name", default = "")

    def execute(self, context):
        context.scene.test_tool.smooth_all(context)
        return {'FINISHED'}


class NEUROPIL_OT_tag_psds(bpy.types.Operator):
    bl_idname = "processor_tool.tag_psds"
    bl_label = "Assign PSD Region"
    bl_description = "Assign PSD Region"
    bl_options = {'REGISTER', 'UNDO'}

    spine_namestruct_name = StringProperty(name = "Name: ", description = "Assign Spine Name", default = "")

    def execute(self, context):
        context.scene.test_tool.tag_psds(context,"double")
        return {'FINISHED'}


class NEUROPIL_OT_merge_objs(bpy.types.Operator):
    bl_idname = "processor_tool.merge_objs"
    bl_label = "Merge Objects"
    bl_description = "Merge Objects"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        context.scene.test_tool.merge_objs(context)
        return {'FINISHED'}



class NEUROPIL_OT_tag_psd_single(bpy.types.Operator):
    bl_idname = "processor_tool.tag_psd_single"
    bl_label = "Define Meta Region ('tag')"
    bl_description = "Define Region ('tag')"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.test_tool.tag_psds(context,"single")
        return {'FINISHED'}


class GAMER_OT_coarse_dense(bpy.types.Operator):
    bl_idname = "gamer.coarse_dense"
    bl_label = "Coarse Dense"
    bl_description = "Decimate selected dense areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_dense(context)
        return {'FINISHED'}


class GAMER_OT_coarse_flat(bpy.types.Operator):
    bl_idname = "gamer.coarse_flat"
    bl_label = "Coarse Flat"
    bl_description = "Decimate selected flat areas of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.coarse_flat(context)
        return {'FINISHED'}


class GAMER_OT_smooth(bpy.types.Operator):
    bl_idname = "gamer.smooth"
    bl_label = "Smooth"
    bl_description = "Smooth selected vertices of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.smooth(context)
        return {'FINISHED'}

 
class GAMER_OT_normal_smooth(bpy.types.Operator):
    bl_idname = "gamer.normal_smooth"
    bl_label = "Normal Smooth"
    bl_description = "Smooth faces normals of selected faces of the mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.gamer.mesh_improve_panel.normal_smooth(context)
        return {'FINISHED'}


#layout object lists
class Trace_UL_draw_item(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        global trace_filter_name
       
        #self.filter_name = bpy.context.scene.test_tool.include_list.filter_name
        #spine_trace_filter_name = self.spine_filter_name
        trace_filter_name = self.filter_name
        self.use_filter_sort_alpha = True
        layout.label(item.name)



class Include_UL_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = bpy.context.scene
        self.use_filter_sort_alpha = True    
        if item.non_manifold == True:
            layout.label(item.name, icon='ERROR')
        elif item.multi_component == True:
            layout.label(item.name, icon='NLA')
        elif item.generated == True:
#scn.objects[scn.test_tool.include_list[str(item)] != None:
            layout.label(item.name, icon='MESH_ICOSPHERE')
        else:
            layout.label(item.name)



class SCN_UL_obj_draw_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = bpy.context.scene
        filt = scn.test_tool.spine_namestruct_name.replace('#','[0-9]')
        self.filter_name = filt
        self.use_filter_sort_alpha = True
        if item.processor.newton == True:
            layout.label(item.name, icon='FILE_TICK')
        elif item.processor.smoothed == True:
            layout.label(item.name, icon='MOD_SMOOTH')
        else:
            layout.label(item.name)


class SCN_TestTool(bpy.types.Panel):
    bl_label = "Processor Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.scene != None:
            context.scene.test_tool.draw_panel(context, panel=self)

class SCN_TextEntry(bpy.types.Panel):
    bl_label = "Test"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        box1 = layout.box()
        row = box1.row()
        col = row.column(align = True)
        col.operator("processor_tool.psd_namestruct"   , icon = "RESTRICT_SELECT_OFF", text = "")


class ContourNameSceneProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Contour name", default ="")
    
    def init_contour(self,context,name):
        self.name = name


class IncludeNameSceneProperty(bpy.types.PropertyGroup):
    name = StringProperty(name= "Include name", default ="")
    generated = BoolProperty(name = "Mesh Object Generated", default = False)
    multi_component = BoolProperty(name = "Multiple Components in Mesh", default = False)
    non_manifold = BoolProperty(name = "Non-manifold Mesh", default = False)       
    filter_name = StringProperty(name="Read manually filtered names for Include", default= "")
    spine_filter_name = StringProperty(name="Read manually filtered names for Include", default= "")
    PSD_filter_name = StringProperty(name="Read manually filtered names for Include", default= "")
    problem = BoolProperty(name = "Problem Tagging", default = False)
    
    def init_include(self,context,name):
        self.name = name



class ProcessorToolObjectProperty(bpy.types.PropertyGroup):
    #obj_list = CollectionProperty(
    #    type=ProcessorToolObProperty, name="psd_trace_list")
    active_obj_region_index = IntProperty(name="Active OBJ Index", default=0)
    n_components = IntProperty(name="Number of Components in Mesh", default=0)
    smoothed = BoolProperty(name="Smoothed Object", default=False)
    newton = BoolProperty(name = "New Object", default=False)
    fix_all_fail = BoolProperty(name = "Failed to Fix Obj", default = False)
    

    #def init_obje(self,context,name):
    #    self.name = name



    def select_obje(self, context, obje):
        if context.active_object is not None:
          bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obje.select = True
        bpy.context.scene.objects.active = obje
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

#        obs = context.scene.objects
#        obje = context.active_object
#        obje_name = obje.name  
#        for obje in obs:
#            obje = returnObjectByName(obje_name)
##context.scene.objects[dend]
#            if obje != None:
#                print(obje)
#                obje.select = True  
#        #obje_list = bpy.data.objects.name[obje_name]
#                bpy.ops.object.mode_set(mode='EDIT')
#                bpy.ops.mesh.reveal()
#                bpy.ops.mesh.select_all(action='DESELECT')
#                bpy.ops.object.mode_set(mode = 'OBJECT')
#        return(obje)


    #def select_obje(self,context):
        # For this spine head, select faces of this PSD:
        
        #reg = obj.mcell.regions.region_list[self.name]
        #reg.select_region_faces(context)

    def set_n_components(self,context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.active_object
        mesh = obj.data

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Count total vertices and number of vertices contiguous with vertex 0
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh.vertices[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()
        n_v_tot = len(mesh.vertices)
        n_v_sel = mesh.total_vert_sel
        bpy.ops.object.mode_set(mode='OBJECT')

        # Loop over disjoint components
        n_components = 1
        while (n_v_sel < n_v_tot):
            n_components += 1
            # make list of selected indices
            vl1 = [v.index for v in mesh.vertices if v.select == True]
            # make list of indices of remaining component(s)
            vl2 = [v.index for v in mesh.vertices if v.select == False]
            # Grow selection with vertices contiguous with first vertex of remainder
            mesh.vertices[vl2[0]].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()

            # Count number of vertices now selected and loop again if necessary
            n_v_sel = mesh.total_vert_sel
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        self.n_components = n_components




    def smooth(self, context):
        """ Smooth using GAMer """
        print('Smoothing: %s' % (context.active_object.name))
        gamer_mip = context.scene.gamer.mesh_improve_panel
        gamer_mip.dense_rate = 2.5
        gamer_mip.dense_iter = 1
        gamer_mip.max_min_angle = 20.0
        gamer_mip.smooth_iter = 10
        gamer_mip.preserve_ridges = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')      
        bpy.ops.gamer.coarse_dense('INVOKE_DEFAULT')
        bpy.ops.gamer.smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
        bpy.ops.gamer.normal_smooth('INVOKE_DEFAULT')
#        bpy.ops.mesh.select_all(action='DESELECT')
#        bpy.ops.object.mode_set(mode='OBJECT')
        self.smoothed = True

        # ADD OBJ2MCELL
        return('FINISHED')



class ProcessorToolSceneProperty(bpy.types.PropertyGroup):
    active_sp_index = IntProperty(name="Active Spine Object Index", default=0)
    active_c_index = IntProperty(name="Active Contact Object Index", default=0)
    contour_list = CollectionProperty(
        type = ContourNameSceneProperty, name = "Contour List")
    active_contour_index = IntProperty(name="Active Trace Index", default=0)
    include_list = CollectionProperty(
        type = IncludeNameSceneProperty, name = "Include List")
    active_include_index = IntProperty(name="Active Include Index", default=0)
    new = BoolProperty(name = "Imported MDL Object", default = False)
    filepath = StringProperty(name = "Remember Active Filepath", default= "")
    spine_namestruct_name = StringProperty("Set object name structure", default = "d##sp##")          
    PSD_namestruct_name = StringProperty("Set metadata name structure", default = "d##c##")
    central_namestruct_name = StringProperty("Set central object name structure", default = "d##")
    spine = StringProperty(name = "Differentiates Spine", default = "")
    psd = StringProperty(name = "Differentiates PSD",default = "")
    min_section = StringProperty(name="Minimum Reconstruct Section File", default= "")
    max_section = StringProperty(name="Maximum Reconstruct Section File", default= "")
    section_thickness = StringProperty(name="Maximum Reconstruct Section File", default= "0.05")
    #c_obj_name_list = CollectionProperty(name = "

    #contour_name = StringProperty(name="Contour Name", default = "")
    
    def spine_namestruct(self, context, spine_namestruct_name):
        self.spine_namestruct_name = spine_namestruct_name

    def PSD_namestruct(self, context, PSD_namestruct_name):
        self.PSD_namestruct_name = PSD_namestruct_name
        

    def central_namestruct(self, context, central_namestruct_name):
        self.central_namestruct_name = central_namestruct_name
       
       #for i in self.spine_namestruct:
        #   if i == 'X':
        #       i.= '[0-9]'

       # print(self.spine_namestruct_name)
       # print(spine_name)
        #print(type(self.spine_namestruct_name))
    
    
    def add_contour(self,context,contour_name,mode):
        """ Add a new PSD to psd_list """
        if mode == 'contour':
            new_contour=self.contour_list.add()
            new_contour.init_contour(context,contour_name)
        else:
            new_contour=self.include_list.add()
            new_contour.init_include(context,contour_name)
        return(new_contour)


    def generate_contour_list(self, context, filepath):
        self.filepath = filepath
        ser_prefix = self.filepath

        first_re = compile('first3Dsection="(\d*)"')
        last_re = compile('last3Dsection="(\d*)"')
        default_thick_re = compile('defaultThickness="(.*)"')

        ser_data = open(ser_prefix[:-4] + ".ser", "r").read()
        self.min_section = first_re.search(ser_data).group(1)
        self.min_section = str(int(self.min_section) +1)
        self.max_section = last_re.search(ser_data).group(1)
        self.max_section = str(int(self.max_section)- 1)
        self.section_thickness = default_thick_re.search(ser_data).group(1)
    


        contour_re = compile('Contour\ name=\"(.*?)\"')

        all_names = []
        for i in range(int(self.min_section), int(self.max_section)):
            print(i)
            all_names += contour_re.findall(open(ser_prefix[:-3] + str(i)).read())
         # Now you would put each item in this python list into a Blender collection property
        contour_names = sorted(list(set(all_names))) 
       
        for name in contour_names:
            self.add_contour(context, name,"contour")
        for item in self.contour_list:
            print(item)
        return(self.contour_list)
    
    
    #def get_active_contour(self, context,mode):
    #    scn = bpy.context.scene
    #    if mode == 'contour':
    #        contour = scn.test_tool[self.active_contour_index]
    #    else:
    #        contour = 

    def include_filter_contour(self,context):
        for item in self.contour_list:
            if ((re.search(trace_filter_name, item.name)) or (re.search(trace_filter_name, item.name)))  and item.name not in self.include_list:
                self.add_contour(context, item.name, "include")
        return(self.include_list)



    def include_contour(self, context):
        name = self.contour_list[self.active_contour_index].name
        if name not in self.include_list:
            self.add_contour(context, name, "include")
        return(self.include_list)

    def remove_contour(self, context):
        #for name in self.contour_list:
        if (len(self.include_list) > 0):
            name = self.include_list[self.active_include_index].name
            ser_dir = os.path.split(self.filepath)[0]
            ser_file = os.path.split(self.filepath)[-1]

            ser_prefix = os.path.splitext(ser_file)[0]
            out_file = ser_dir + '/' + ser_prefix + "_output"


            #for item in self.include_list:
            #objs = bpy.context.scene.objects
            #for obj in objs:
            if bpy.data.objects.get(name) is not None:
                bpy.ops.object.select_all(action='DESELECT')
                obj = bpy.context.scene.objects[self.include_list[self.active_include_index].name]
                obj.select = True
                context.scene.objects.active = obj
                m = obj.data
                context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)
                if os.path.exists(out_file + '/'+ name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ name + '_tiles.rawc')
                if os. path.exists(out_file + '/'+ name + '.obj'):
                    os.remove(out_file + '/'+ name + '.obj')
            self.include_list.remove(self.active_include_index)
               
        return(self.include_list)

    def remove_contour_all(self, context):
        #for name in self.contour_list:
        #name = self.include_list[self.active_include_index].name
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]

        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"

        self.contour_list.clear()
               
        return(self.contour_list)

    def remove_components(self,context):
        scn = bpy.context.scene
        contour = self.include_list[self.active_include_index]
        contour_name = contour.name
        self.include_list[contour_name].multi_component == False



    #def generate_mesh_object(self, context)
    #     for item in self.include_list:
    #         self.contourcontour.generate_mesh_object(context,trace) 

    def generate_mesh_object(self, context):
        #set variables
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]

        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"
        if os.path.exists(out_file) == False:
            os.mkdir(out_file)
        interp_file = ser_prefix + "_interp" 
        
        #interpolate traces
        contour_name = " "
        for i in self.include_list: 
            contour = "-I " + str(i.name) + " "  
            contour_name += contour        
        interpolate_cmd = "reconstruct_interpolate -i %s -f %s -o %s --min_section=%s --max_section=%s --curvature_gain=1E2 --proximity_gain=3 --min_point_per_contour=4 --deviation_threshold=0.005 %s -w %s" % (ser_dir, ser_prefix, out_file, self.min_section, self.max_section, contour_name, interp_file)
        print('\nInterpolating series: \n%s\n' % (interpolate_cmd))
        subprocess.check_output([interpolate_cmd],shell=True)

        #tile traces
        for i in self.include_list:
            contour_name = str(i.name)
            print('\nGenerating Mesh for: %s\n' % (contour_name))
            if bpy.data.objects.get(contour_name) is None:
                tile_cmd = "ContourTilerBin -f ser -n %s -d %s -c %s -s  %s %s -z %s -C 0.01 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, self.section_thickness, interp_file)
                subprocess.check_output([tile_cmd],shell=True)
            #make obj
                raw2obj_cmd = "rawc2obj.py %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
                subprocess.check_output([raw2obj_cmd],shell=True)
            #import obj
                bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
                self.include_list[str(contour_name)].generated = True
        #obj = bpy.context.scene.objects[contour_name]
         #   obj != None:
                if i.multi_component == True:
                    print("Multiple Components: %s" % (str(self.include_list[contour_name])))

  
    def generate_mesh_object_single(self,context): 
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]
        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"

        if os.path.exists(out_file) == False:
            os.mkdir(out_file)
        interp_file = ser_prefix + "_interp" 
       
        contour = self.include_list[self.active_include_index]
        contour_name  = contour.name
        print(contour_name)
        obj = None
        interpolate_cmd = "reconstruct_interpolate -i %s -f %s -o %s --min_section=%s --max_section=%s --curvature_gain=1E2 --proximity_gain=3 --min_point_per_contour=4 --deviation_threshold=0.005 -I %s -w %s" % (ser_dir, ser_prefix, out_file, self.min_section, self.max_section, contour_name, interp_file)
        subprocess.check_output([interpolate_cmd],shell=True)

        if bpy.data.objects.get(contour_name) is None:
            tile_cmd = "ContourTilerBin -f ser -n %s -d %s -c %s -s  %s %s -z %s -C 0.01 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, self.section_thickness, interp_file)
            subprocess.check_output([tile_cmd],shell=True)
            #make obj
            raw2obj_cmd = "rawc2obj.py %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
            subprocess.check_output([raw2obj_cmd],shell=True)
            #import obj
            bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
            obj = bpy.data.objects.get(contour_name)
            if obj != None:
                self.include_list[str(contour_name)].generated = True
                obj.select = True
                context.scene.objects.active = obj
        '''
        else:
            obj = bpy.data.objects.get(contour_name)
            name = obj.name
            m = obj.data
            context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(m)
            if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                os.remove(out_file + '/'+ name + '_fix.rawc')
            if os.path.isfile(out_file + '/'+ name + '.obj'):
                os.remove(out_file + '/'+ name + '.obj')
            tile_cmd = "ContourTilerBin -f ser -n %s -d %s -c %s -s  %s %s -z .05 -C 0.01 -e 1e-15 -o raw -r %s" % (out_file, out_file, contour_name, self.min_section, self.max_section, interp_file)
            subprocess.check_output([tile_cmd],shell=True)
            #make obj
            raw2obj_cmd = "rawc2obj.py %s > %s" % (out_file + '/'+ contour_name + '_tiles.rawc', out_file + '/'+  contour_name + ".obj")
            subprocess.check_output([raw2obj_cmd],shell=True)
            #import obj
            bpy.ops.import_scene.obj(filepath=out_file + '/' + contour_name  + ".obj", axis_forward='Y', axis_up="Z")
        #obj = bpy.context.scene.objects[contour_name]
         #   obj != None:
            self.include_list[contour_name].generated = True
        '''

        if self.include_list[contour_name].multi_component == True:
            print("Multiple Components: %s" % (str(self.include_list[contour_name])))
        return (obj)


    def fix_mesh(self, context, mode):
        scn = bpy.context.scene         
        ser_dir = os.path.split(self.filepath)[0]
        ser_file = os.path.split(self.filepath)[-1]
        ser_prefix = os.path.splitext(ser_file)[0]
        out_file = ser_dir + '/' + ser_prefix + "_output"
        print("Fix Mesh Out_file:", out_file)

        if os.path.exists(out_file) == False:
            os.mkdir(out_file)

        #for i in self.include_list:
        #    #print(include_name)
        #    contour_name = str(i.name)
        #    bpy.ops.object.select_all(action='DESELECT')
        #    #obj = scn.objects.get(str(i.name))
        #    obj= bpy.context.scene.objects[contour_name] 
        #    obj.select = True

        if mode == "single":
            contour = self.include_list[self.active_include_index]
            contour_name  = contour.name
            bpy.ops.object.select_all(action='DESELECT')
            obj = scn.objects[contour_name]
            obj.select = True
            bpy.context.scene.objects.active = obj 
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.mcell.meshalyzer()
            mesh_props = bpy.context.scene.mcell.meshalyzer
            name = obj.name
            if mesh_props.components >1:           
                print('\nFound Multi-component Mesh: %s\n' % (obj.name))
                self.include_list[name].multi_component = True
            if ((mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals') and mesh_props.components == 1): 
                print('\nFixing Single Flawed Mesh: %s\n' % (contour_name))
                name = obj.name
                m = obj.data
                context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(m)  

                #fix mesh
                fix_all_cmd = "volFixAll %s %s" % (out_file + '/' + name + "_tiles.rawc", out_file + '/'+ name + "_fix.rawc")  
                subprocess.check_output([fix_all_cmd], shell=True)

                #make obj
                raw2obj_cmd = "rawc2obj.py %s > %s" % (out_file + '/'+ name + '_fix.rawc', out_file + '/'+  name + ".obj")
                subprocess.check_output([raw2obj_cmd],shell=True)

                #import obj
                bpy.ops.import_scene.obj(filepath=out_file + '/' + name  + ".obj", axis_forward='Y', axis_up="Z") 
                self.include_list[name].generated = True
                bpy.ops.object.select_all(action='DESELECT')
                obj = scn.objects[contour_name]
                obj.select = True
                bpy.context.scene.objects.active = obj 
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.mcell.meshalyzer()
                mesh_props = bpy.context.scene.mcell.meshalyzer
                if (mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals'):
                    print('\nMesh Still Flawed: %s\n' % (contour_name))
                    self.include_list[name].non_manifold = True
                else:
                    print('\nMesh Successfully Fixed: %s\n' % (contour_name))
                    self.include_list[name].non_manifold = False

            if os.path.isfile(out_file + '/'+ name + '_tiles.rawc'):
                os.remove(out_file + '/'+ name + '_tiles.rawc')
            if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                os.remove(out_file + '/'+ name + '_fix.rawc')
            if os.path.isfile(out_file + '/'+ name + '.obj'):
                os.remove(out_file + '/'+ name + '.obj')
                      
        else: 
            for obj in scn.objects:
                #obj= bpy.context.scene.objects[contour_name] 
                #print(obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                bpy.context.scene.objects.active = obj 
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.mcell.meshalyzer()
                mesh_props = bpy.context.scene.mcell.meshalyzer
                name = obj.name
                if mesh_props.components >1:
                    print('\nFound Multi-component Mesh: %s\n' % (obj.name))
                    self.include_list[name].multi_component = True
                if ((mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals') and mesh_props.components == 1): 
                    print('\nFound Flawed Mesh: %s\n' % (obj.name))
                    m = obj.data
                    context.scene.objects.unlink(obj)
                    bpy.data.objects.remove(obj)
                    bpy.data.meshes.remove(m)  

                    #fix mesh
                    fix_all_cmd = "volFixAll %s %s" % (out_file + '/' + name + "_tiles.rawc", out_file + '/'+ name + "_fix.rawc")  
                    subprocess.check_output([fix_all_cmd], shell=True)

                    #make obj
                    raw2obj_cmd = "rawc2obj.py %s > %s" % (out_file + '/'+ name + '_fix.rawc', out_file + '/'+  name + ".obj")
                    subprocess.check_output([raw2obj_cmd],shell=True)

                    #import obj
                    bpy.ops.import_scene.obj(filepath=out_file + '/' + name  + ".obj", axis_forward='Y', axis_up="Z") 
                    self.include_list[name].generated = True
                    bpy.ops.object.select_all(action='DESELECT')
                    obj = scn.objects[name]
                    obj.select = True
                    bpy.context.scene.objects.active = obj 
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.mcell.meshalyzer()
                    mesh_props = bpy.context.scene.mcell.meshalyzer
                    if (mesh_props.manifold == False) or (mesh_props.watertight == False) or (mesh_props.normal_status == 'Inconsistent Normals'):
                        print('\nMesh Still Flawed: %s\n' % (name))
                        self.include_list[name].non_manifold = True
                    else:
                        print('\nMesh Successfully Fixed: %s\n' % (name))
                        self.include_list[name].non_manifold = False

                #do some clean up
                if os.path.isfile(out_file + '/'+ name + '_tiles.rawc'):
                    os.remove(out_file + '/'+ name + '_tiles.rawc')
                if os.path.isfile(out_file + '/'+ name + '_fix.rawc'):
                    os.remove(out_file + '/'+ name + '_fix.rawc')
                if os.path.isfile(out_file + '/'+ name + '.obj'):
                    os.remove(out_file + '/'+ name + '.obj')

        print("\nMulti-component meshes:\n")
        for item in self.include_list:
            if item.multi_component == True:
                print(item.name) 

        #for i in range(int(self.min_section), int(self.max_section)+1):
        #    if os.path.isfile(out_file + '/'+ ser_prefix + '_interp.' + str(i)):
        #        os.remove(out_file + '/'+ ser_prefix + '_interp.' + str(i))
        #os.remove(out_file + '/_tiles.rawc')
        #os.remove(out_file + '/convert.sh')
        #os.remove(out_file + '/mesh.sh')
        #os.remove(out_file + '/mesh_and_convert.sh')
        #os.remove(out_file + '/'+ ser_prefix + '_interp.ser')
        #os.rmdir(out_file)


    def get_active_obje(self, context, mode):
        scn = bpy.context.scene

        if mode == 'spine':
            obje = scn.objects[self.active_sp_index]
            print(obje.name)
        else: 
            obje = scn.objects[self.active_c_index]
            print(obje.name)
           
        return(obje)


    def select_obje(self,context, mode):
        obje = self.get_active_obje(context, mode)
        obje.processor.select_obje(context, obje)


    def tag_psds(self, context,mode):
        """ Assign PSD metadata from intersection of cfa and sp traces """
        # 1 - select cfa and do obj2mcell
        # 2 - regular expression match for names, assign to variables
        # 3 - mesh tag region
        # 4 - add option for one spine versus whole branch
        #obj = context.active_object
        cwd = bpy.path.abspath(os.path.dirname(__file__))
        print('tag_psds cwd: %s' % (cwd))
        #tmp_obj = cwd + "/tmp.obj"
        #exe = bpy.path.abspath(cwd + "/obj2mesh")
  

        # given a list of selected cfa's find all the unique sp's they match

        # for each sp associated with a group of cfa's
        
        # 5. for each cfa object:


        scn = bpy.context.scene

        obj1 = self.spine_namestruct_name
        obj2 = self.PSD_namestruct_name


        diff = difflib.ndiff(obj1, obj2)
        d = list(diff)
        #print(d)
        predicate = '-'
        filtered = list(itertools.filterfalse(lambda x: x[0] == predicate, d))
 
        c_obj_name_list = []
        c_obj_name = ''
        for i in filtered:
            #print(i[2])
            #print(type(i))
            c_obj_name_list.append(i[2])
            c_obj_name += str(i[2])
        #print('c obj_name:',c_obj_name)
        #print('c_obj_name_list:', c_obj_name_list)

        obj1 = self.spine_namestruct_name.replace('#','[0-9]')
        obj2= self.PSD_namestruct_name.replace('#','[0-9]')
        #print('obj:',obj2)

        obje_list = [obje.name for obje in self.include_list if re.search(obj1, obje.name) != None]
        print("obje_list:", obje_list)
        contact_list = [contact.name for contact in self.include_list if re.search(obj2, contact.name) != None]
        #print('spine_struct:', self.spine_namestruct_name)
        #print(len(obje_list))
    
        
        
        if mode == "single":
            contour = scn.objects[self.active_sp_index]
            print(contour)
            contour_name  = contour.name
            sp_obj = scn.objects.get(contour_name)
            sp_obj_name = sp_obj.name

            digits = difflib.ndiff(sp_obj_name, obj1.replace('[0-9]', '#'))
            d = list(digits)
            #print(d)
            predicate = '-'
            filter_digits = list(itertools.filterfalse(lambda x: x[0] != predicate, d))
            #print("filter:", filter_digits)

            replace = []
            for i in filter_digits:
                replace.append(str(i[2]))
            print('replace:', replace) 

            location = []
            for i in c_obj_name:
                location.append(i)
            index = []
            for position,char in enumerate(location):
                if char == '#':
                    index.append(position)
            print('index:',index)  
            

            count = 0
            for i in index:
                c_obj_name_list[i] = replace[count]
                count+=1
            #print(c_obj_name_list)

            c_obj_name = ''
            for item in c_obj_name_list:
                c_obj_name += item
                
  
            
            print('test:', len(c_obj_name))

            print(sp_obj_name, c_obj_name)
            print(type(sp_obj_name), type(c_obj_name))
            if (sp_obj != None) and (sp_obj.processor.smoothed == True) and (sp_obj.processor.newton == False) and (self.include_list[sp_obj.name].non_manifold == False):
            #INDENT THE FOLLOWING:    
                sp_obj_file_name = cwd + '/' + sp_obj_name + ".obj"
                sp_mdl_file_name = cwd + '/' + sp_obj_name + ".mdl"
                #sp_mdl_file_name_2 = cwd + '/' + sp_obj_name + "_2.mdl"
                sp_mdl_with_tags_file_name = cwd + '/' + sp_obj_name + "_tagged.mdl"
                sp_mdl_with_tags_file_name_2 = cwd + '/' + sp_obj_name + "_tagged_2.mdl"
                sp_mdl_with_tags_file_name_3 = cwd + '/' + sp_obj_name + "_tagged_3.mdl"
                sp_mdl_with_tags_file_name_4 = cwd + '/' + sp_obj_name + "_tagged_4.mdl"
                sp_mdl_with_tags_file_obj = cwd + '/' + sp_obj_name + "_tagged.obj"
                sp_mdl_with_tags_file_obj_2 = cwd + '/' + sp_obj_name + "_tagged_2.obj"
                sp_mdl_with_tags_file_obj_3 = cwd + '/' + sp_obj_name + "_tagged_3.obj"
                c_obj_file_name = cwd + '/' + c_obj_name + ".obj"
                c_obj_file_name_2 = cwd + '/' + c_obj_name + "_2.obj"
                c_obj_file_name_3 = cwd + '/' + c_obj_name + "_3.obj"
                c_obj_file_name_4 = cwd + '/' + c_obj_name + "_4.obj"
                c_mdl_tag_file_name= cwd + '/' + c_obj_name + "_regions.mdl"
                c_mdl_tag_file_name_2 = cwd + '/' + c_obj_name + "_regions_2.mdl"
                c_mdl_tag_file_name_3 = cwd + '/' + c_obj_name + "_regions_3.mdl"
                c_mdl_tag_file_name_4 = cwd + '/' + c_obj_name + "_regions_4.mdl"
                
            # export smoothed blender object as an obj file to file name sp_obj_file_name
            # unselect all objects 
                bpy.ops.object.select_all(action='DESELECT')
            # now select and export the "sp" object:
                bpy.context.scene.objects.active = sp_obj
                sp_obj.select = True
                bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
            # export sp_obj as an MDL file
                bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)
            # export "c" object as an obj file to file name c_obj_file_name
            # unselect all objects 
                bpy.ops.object.select_all(action='DESELECT')
                #c_obj_name = obje.replace('sp', 'c')
                c_obj = scn.objects.get(c_obj_name)
                print("found c object: " + c_obj.name) 
                if c_obj != None:
                    # now select and export the "c" object:
                    bpy.context.scene.objects.active = c_obj
                    c_obj.select = True
                    bpy.ops.export_scene.obj(filepath=c_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
                    tag_cmd = "obj_tag_region %s %s > %s" % (sp_obj_file_name, c_obj_file_name, c_mdl_tag_file_name)
                    subprocess.check_output([tag_cmd],shell=True)
                    concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_mdl_file_name, c_mdl_tag_file_name, sp_mdl_with_tags_file_name)
                    subprocess.check_output([concat_cmd],shell=True)
                    bpy.ops.object.select_all(action='DESELECT')
                    sp_obj.select = True
                    bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_with_tags_file_name)
                    obje = scn.objects[sp_obj_name]
                    obje.processor.smoothed = True
                    obje.processor.newton = True


                else: 
                    obje = scn.objects[sp_obj_name]
                    self.include_list[obje.name].problem = True


        else:
            for obje in obje_list:
                print('obje: ' + obje)
                sp_obj = scn.objects[obje]
            
                #c_obj_list = []
                sp_obj_name = sp_obj.name
                print(sp_obj_name)
                            
                digits = difflib.ndiff(sp_obj_name, obj1.replace('[0-9]', '#'))
                d = list(digits)
                #print(d)
                predicate = '-'
                filter_digits = list(itertools.filterfalse(lambda x: x[0] != predicate, d))
                #print("filter:", filter_digits)

                replace = []
                for i in filter_digits:
                    replace.append(str(i[2]))
                print('replace:',replace) 

                c_obj_name_list = []
                c_obj_name = ''
                for i in filtered:
                    c_obj_name_list.append(i[2])
                    c_obj_name += str(i[2])
                #print('c obj_name:',c_obj_name)
                #print('c_obj_name_list:', c_obj_name_list)

                location = []
                #print('c_obj_name_list before loop', c_obj_name_list)
                for i in c_obj_name:
                    location.append(i)
                index = []
                for position,char in enumerate(location):
                    if char == '#':
                        index.append(position)
                print('index:',index)  
            

                count = 0
                for i in index:
                    c_obj_name_list[i] = replace[count]
                    count+=1
                #print(c_obj_name_list)

                c_obj_name = ''
                for item in c_obj_name_list:
                    c_obj_name += item
            
                print('test:', c_obj_name)

                print(sp_obj_name, c_obj_name)


                
                if sp_obj != None and sp_obj.processor.smoothed == True and sp_obj.processor.newton == False and self.include_list[sp_obj.name].non_manifold == False:
                    sp_obj_file_name = cwd + '/' + sp_obj_name + ".obj"
                    sp_mdl_file_name = cwd + '/' + sp_obj_name + ".mdl"
                    #sp_mdl_file_name_2 = cwd + '/' + sp_obj_name + "_2.mdl"
                    sp_mdl_with_tags_file_name = cwd + '/' + sp_obj_name + "_tagged.mdl"
                    sp_mdl_with_tags_file_name_2 = cwd + '/' + sp_obj_name + "_tagged_2.mdl"
                    sp_mdl_with_tags_file_name_3 = cwd + '/' + sp_obj_name + "_tagged_3.mdl"
                    sp_mdl_with_tags_file_name_4 = cwd + '/' + sp_obj_name + "_tagged_4.mdl"
                    sp_mdl_with_tags_file_obj = cwd + '/' + sp_obj_name + "_tagged.obj"
                    sp_mdl_with_tags_file_obj_2 = cwd + '/' + sp_obj_name + "_tagged_2.obj"
                    sp_mdl_with_tags_file_obj_3 = cwd + '/' + sp_obj_name + "_tagged_3.obj"
                    c_obj_file_name = cwd + '/' + c_obj_name + ".obj"
                    c_obj_file_name_2 = cwd + '/' + c_obj_name + "_2.obj"
                    c_obj_file_name_3 = cwd + '/' + c_obj_name + "_3.obj"
                    c_obj_file_name_4 = cwd + '/' + c_obj_name + "_4.obj"
                    c_mdl_tag_file_name= cwd + '/' + c_obj_name + "_regions.mdl"
                    c_mdl_tag_file_name_2 = cwd + '/' + c_obj_name + "_regions_2.mdl"
                    c_mdl_tag_file_name_3 = cwd + '/' + c_obj_name + "_regions_3.mdl"
                    c_mdl_tag_file_name_4 = cwd + '/' + c_obj_name + "_regions_4.mdl"
                
            # export smoothed blender object as an obj file to file name sp_obj_file_name
            # unselect all objects 
                    bpy.ops.object.select_all(action='DESELECT')
            # now select and export the "sp" object:
                    bpy.context.scene.objects.active = sp_obj
                    sp_obj.select = True
    
                    bpy.ops.export_scene.obj(filepath=sp_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 

            # export sp_obj as an MDL file
                    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_file_name)

            # export "c" object as an obj file to file name c_obj_file_name
            # unselect all objects 
                    bpy.ops.object.select_all(action='DESELECT')
                    #c_obj_name = obje.replace('sp', 'c')
                    c_obj = scn.objects.get(c_obj_name)
                    if c_obj != None:
                    # now select and export the "c" object:
                        bpy.context.scene.objects.active = c_obj
                        c_obj.select = True
                        bpy.ops.export_scene.obj(filepath=c_obj_file_name, axis_forward='Y', axis_up="Z", use_selection=True, use_edges=False, use_normals=False, use_uvs=False, use_materials=False, use_blen_objects=False) 
                    
                        tag_cmd = "obj_tag_region %s %s > %s" % (sp_obj_file_name, c_obj_file_name, c_mdl_tag_file_name)
                        subprocess.check_output([tag_cmd],shell=True)
                        concat_cmd = "( head -n -2 %s ; cat %s ; echo '}' ) > %s" % (sp_mdl_file_name, c_mdl_tag_file_name, sp_mdl_with_tags_file_name)
                        subprocess.check_output([concat_cmd],shell=True)
                        bpy.ops.object.select_all(action='DESELECT')
                        sp_obj.select = True
                        bpy.ops.import_mdl_mesh.mdl('EXEC_DEFAULT', filepath=sp_mdl_with_tags_file_name)
                        obje = scn.objects[sp_obj_name]
                        obje.processor.smoothed = True
                        obje.processor.newton = True

                   
                    else: 
                        obje = scn.objects[sp_obj_name]
                        self.include_list[obje.name].problem = True
                    
                    #os.remove(sp_obj_file_name)
                    #os.remove(c_obj_file_name)
                    #os.remove(sp_mdl_file_name)
                    #os.remove(c_mdl_tag_file_name_2)
  
                    
                    #os.remove(sp_obj_file_name)
                    #os.remove(c_obj_file_name)
                    #os.remove(sp_mdl_file_name)
                    #os.remove(c_mdl_tag_file_name)

            # import the concatenated tagged mdl and replace the blender object

                #sp_obj_list.append(sp_obj)
                #os.remove(sp_mdl_with_tags_file_name) 
                #os.remove(sp_mdl_with_tags_file_name_2)


            #os.remove(sp_mdl_with_tags_file_name) 
            #if os.path.exists(sp_mdl_with_tags_file_name_2) and os.path.getsize(sp_mdl_with_tags_file_name_2) > 0:
            #    os.path.remove(sp_mdl_with_tags_file_name_2)


    def smooth_all(self,context):
        spine_name = self.spine_namestruct_name.replace('#','[0-9]')
        scn = bpy.context.scene
        the_list = [obje for obje in scn.objects if re.search(spine_name, obje.name)!= None]
        for obje in the_list:
            if (self.include_list[obje.name].multi_component == False) and (self.include_list[obje.name].non_manifold == False) and(obje.processor.smoothed == False):
                obje.processor.select_obje(context, obje)
                obje.processor.smooth(context)




    #Draw panel
    def draw_panel(self, context, panel):
        layout = panel.layout
        row = layout.row()
        row.operator("processor_tool.impser", text="Import .ser file")  
        #row.operator("processor_tool.spine_namestruct", text = "Set Spine Name")
        row = layout.row()
        row.label(text="Trace List:", icon='CURVE_DATA')
        row.label(text="Include List:", icon='MESH_ICOSPHERE')
        row = layout.row()
        row.template_list("Trace_UL_draw_item","contours_in_ser_file",
                          bpy.context.scene.test_tool, "contour_list",
                          self, "active_contour_index",
                          rows=2)
       # row.template_list("PSD_Trace_UL_draw_item","contours_in_ser_file",
         #                 bpy.context.scene.test_tool, "contour_list",
         #                 self, "active_contour_index",
        #                  rows=2)
       # row = layout.row() 
        row.template_list("Include_UL_draw_item","included_in_ser_file",
                          bpy.context.scene.test_tool, "include_list",
                          self, "active_include_index",
                          rows=2)
        row = layout.row()
        row.operator("processor_tool.include_contour", text="Include Contour") 
        row.operator("processor_tool.remove_contour", text="Remove Contour")

        row = layout.row()
        row.operator("processor_tool.include_filter_contour", text = "Include Current Filtered Contours") 
        row.operator("processor_tool.generate_mesh_object_single", text="Generate Single Mesh Object")

        row = layout.row()
        row.operator("processor_tool.remove_contour_all", text = "Clear Contour List") 
        row.operator("processor_tool.generate_mesh_object", text="Generate Mesh Objects")

        row = layout.row()
        row.operator("processor_tool.fix_mesh", text = "Fix Mesh Objects")
        row = layout.row()
        row.label(text="Define Region Names for Tagging (use '#' to signify an integer)")  
        row = layout.row()     
        box1 = layout.box()
        row = box1.row()
        col = row.column(align = True)
        col.operator("processor_tool.spine_namestruct", icon = "RESTRICT_SELECT_OFF", text = "Set Main Object Name")          
        #row.label(text= 'processor_tool.spine_namestruct')  
        row.label(text= "Current: " + bpy.context.scene.test_tool.spine_namestruct_name)
        box1 = layout.box()
        row = box1.row()
        col = row.column(align = True)
        col.operator("processor_tool.psd_namestruct"   , icon = "RESTRICT_SELECT_OFF", text = "Set Meta Object Name")
        row.label(text= "Current: " +  bpy.context.scene.test_tool.PSD_namestruct_name) 
        row = layout.row()
        row.label(text="Object List:", icon='MESH_ICOSPHERE')
        row = layout.row()
        row.template_list("SCN_UL_obj_draw_item","sp_objects_in_scene",
                          bpy.context.scene, "objects",
                          self, "active_sp_index",
                          rows=2) 
        #row = layout.row()
        row.operator("processor_tool.remove_components", text="Allow Smooth")
        row = layout.row()
        row.operator("processor_tool.smooth", text="Smooth Selected Object (any!)")
        #row = layout.row()
        row.operator("processor_tool.tag_psd_single", text="Define Meta Region ('tag')")
        row = layout.row()
        row.operator("processor_tool.smooth_all", text="Smooth All Objects in List")
        #row = layout.row()
        row.operator("processor_tool.tag_psds", text="Define Meta Region for All Objects in List")
        #row = layout.row()
        #box1 = layout.box()
        #row = box1.row()
        #col = row.column(align = True)
        #col.operator("processor_tool.central_namestruct"   , icon = "RESTRICT_SELECT_OFF", text = "Set Central Object Name")
        #row.label(text="Default: dXX (use XX for integer value)")
        #row = layout.row()
        #row.operator("processor_tool.merge_objs", text="Merge Objects")








