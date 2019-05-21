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
This file contains the classes for Spine Head Analyzer.

"""
# stuff to call Volrover individual executables
import subprocess
import os

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
import mathutils

# python imports

import re
import numpy as np
import neuropil_tools
import cellblender

# register and unregister are required for Blender Addons
# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Spine Head Analyzer Operators:

class NEUROPIL_OT_select_psd(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.select_psd"
    bl_label = "Select Faces of PSD"
    bl_description = "Select Faces of PSD"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.spine_head_ana.select_psd(context)
        return {'FINISHED'}


class NEUROPIL_OT_compute_volume(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.compute_volume"
    bl_label = "Label spine head and compute its volume"
    bl_description = "Label spine head and compute its volume"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.spine_head_ana.compute_volume(context,'head')
        return {'FINISHED'}


class NEUROPIL_OT_compute_volume_spine(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.compute_volume_spine"
    bl_label = "Label whole spine and compute its volume"
    bl_description = "Label whole spine and compute its volume"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.spine_head_ana.compute_volume(context,'spine')
        return {'FINISHED'}


class NEUROPIL_OT_calculate_diameter(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.calculate_diameter"
    bl_label = "Calculate diameter"
    bl_description = "Calculate diameter of spine neck"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.spine_head_ana.calculate_diameter(context)
        return{'FINISHED'}



class NEUROPIL_OT_recompute_volumes(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.recompute_volumes"
    bl_label = "Recompute volumes of all spines, heads, and necks on object"
    bl_description = "Recompute volumes of all spines, heads, and necks on object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        report_file = open('spine_data_report.txt','w')
        dend_filter = 'd[0-9]{2}$'
        dend_objs = [obj.name for obj in context.scene.objects if re.match(dend_filter,obj.name) != None]
        
        dend_objs.sort()
        orig_obj = context.active_object
        orig_obj.select = False
        orig_obj.hide = False
        context.scene.objects.active = None
        context.scene.update()
        for dend in dend_objs:
            obj = context.scene.objects[dend]
            obj.hide = False
            obj.select = True
            context.scene.objects.active = obj  
            context.scene.update()
            obj.spine_head_ana.recompute_volumes(context,report_file)
            obj.select = False
            obj.hide = True
            context.scene.objects.active = None
            context.scene.update()
         
        orig_obj.hide = False
        orig_obj.select = True
        context.scene.objects.active = orig_obj

#        context.object.spine_head_ana.recompute_volumes(context,context.active_object)
        report_file.close()

        return {'FINISHED'}


class NEUROPIL_OT_output(bpy.types.Operator):
    bl_idname = "spine_head_analyzer.output"
    bl_label = "Output Data"
    bl_description = "Output Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dend_outFile = open('spine_head_analysis_output.txt', 'wt')
        dend_outFile.write('# sy pre_post head_vol spine_vol neck_vol head_area psd_az_area\n')

        dend_filter = 'd[0-9][0-9]*sp[0-9]'
        dend_objs = [obj for obj in context.scene.objects if re.match(dend_filter,obj.name) != None]
        print(dend_objs)
        for obj in dend_objs:
            obj.spine_head_ana.output(context,dend_outFile)

        dend_outFile.close()

        #xon_outFile = open('spine_head_analysis_output.axons.txt', 'wt')
        #axon_outFile.write('# sy pre_post spine_vol head_vol neck_vol spine_area head_area neck_area psd_az_area psd_az_loc_x psd_az_loc_y psd_az_loc_z neck_base_loc_x neck_base_loc_y neck_base_loc_z mito h_hooked h_concave h_flatface h_bulbous h_skinny n_short n_long n_stubby n_thin n_tapered n_branched n_twotiered glia_spicule glia_ensheathed glia_adjacent glia_distant exclude\n')

        #axon_filter = 'a[0-9]{2}$'
        #axon_objs = [obj for obj in context.scene.objects if re.match(axon_filter,obj.name) != None]
        #for obj in axon_objs:
        #    obj.spine_head_ana.output(context,axon_outFile)

        #axon_outFile.close()

        return {'FINISHED'}



# Spine Head Analyzer Panel:

class NEUROPIL_UL_check_psd(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scn = context.scene
        self.filter_name = "*sy*"
        active_obj = context.active_object
        psd = active_obj.spine_head_ana.psd_list.get(item.name)
        if psd != None:
            if psd.char_postsynaptic:
                volume = active_obj.spine_head_ana.psd_list[item.name].volume
                volume_spine = active_obj.spine_head_ana.psd_list[item.name].volume_spine
                if (volume == 0.0) and (volume_spine == 0.0):
                    layout.label(item.name)
                else:
                    layout.label(item.name, icon='FILE_TICK')
            else:
                volume = active_obj.spine_head_ana.psd_list[item.name].volume
                if (volume == 0.0):
                    layout.label(item.name)
                else:
                    layout.label(item.name, icon='FILE_TICK')
        else:
            layout.label(item.name)


#class DIAMETER_UL_psd_draw_item(bpy.types.UIList):

    #def draw_item(self, context, layout, data, item, icon, active_data,
        #          active_propname, index):
        #self.filter_name = "*spn*"
        #active_obj = context.active_object
        #spn = active_obj.spine_head_ana.spn_list.get(item.name)
        #layout.label(item.name)


class NEUROPIL_PT_SpineHeadAnalyzer(bpy.types.Panel):
    bl_label = "Spine Head Analyzer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.object != None:
            context.object.spine_head_ana.draw_panel(context, panel=self)


# Spine Head Analyzer Properties:


# Properties of the PSDs:

class SpineHeadAnalyzerPSDProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Spine PSD or AZ Name", default="")
    char_postsynaptic = BoolProperty(name="Pre or Postsynaptic",default=True)
    head_name = StringProperty(name="Spine Head Name", default="")
    spine_name = StringProperty(name="Spine Name", default="")
    neck_name = StringProperty(name="Spine Neck Name", default="")
    volume = FloatProperty(name="Volume of Spine Head",default=0.0)
    volume_spine = FloatProperty(name="Volume of Spine",default=0.0)
    volume_neck = FloatProperty(name="Volume of Spine Neck",default=0.0)
    area_head = FloatProperty(name="Area of Spine Head",default=0.0)
    area_spine = FloatProperty(name="Area of Spine",default=0.0)
    area_neck = FloatProperty(name="Surface Area of Spine Neck",default=0.0)
    area_neck_cross_section_abt = FloatProperty(name="Area of Spine Neck cross section based on avg of top and base cross section area",default=0.0)
    area_neck_cross_section_lbt = FloatProperty(name="Area of Spine Neck cross section based on volume_neck/length_neck_lbt",default=0.0)
    area_psd_az = FloatProperty(name="Area of PSD or AZ",default=0.0)
    diameter_neck_max = FloatProperty(name="Diameter of Neck",default=0.0)
    diameter_neck_min = FloatProperty(name="Diameter of Neck",default=0.0)
    diameter_neck_lbt = FloatProperty(name="Diameter of Neck based on area_neck_cross_section_lbt",default=0.0)
    length_neck = FloatProperty(name="Length of Neck based on volume_neck/area_neck_cross_section",default=0.0)
    length_neck_lbt = FloatProperty(name="Length of Neck based on distance from base to top",default=0.0)
    psd_az_location = FloatVectorProperty(name="Location of PSD or AZ",default=(0.0,0.0,0.0))
    neck_top_location = FloatVectorProperty(name="Location of Top of Spine Neck",default=(0.0,0.0,0.0))
    neck_base_location = FloatVectorProperty(name="Location of Base of Spine Neck",default=(0.0,0.0,0.0))
    char_mito = BoolProperty(name="Mitochondrion in Bouton",default=False)
    exclude = BoolProperty(name="Exclude this spine?", default=False)
    ensheathment_enum = [
                          ('Distant','Distant',''),
                          ('Partial','Partial',''),
                          ('Full','Full','')
                        ]
    ensheathment = EnumProperty(items = ensheathment_enum, name="Glial Ensheathment", description='Degree of Glial Ensheathment')

    def init_psd(self,context,name):
        obj_name = context.active_object.name
        dend_filter = 'd[0-9]{2}$'
        axon_filter = 'a[0-9]{2}$'
        if re.match(dend_filter,obj_name) != None:
            self.char_postsynaptic = True
        elif re.match(axon_filter,obj_name) != None:
            self.char_postsynaptic = False
        self.name = name
        self.head_name = ""
        self.spine_name = ""
        self.neck_name = ""
        self.volume = 0.0
        self.volume_spine = 0.0
        self.volume_neck = 0.0
        self.area_head = 0.0
        self.area_spine = 0.0
        self.area_neck = 0.0
        self.area_neck_cross_section_abt = 0.0
        self.area_neck_cross_section_lbt = 0.0
        self.area_psd_az = self.compute_region_area(context,self.name)
        self.diameter_neck_max = 0.0
        self.diameter_neck_min = 0.0
        self.diameter_neck_lbt = 0.0
        self.length_neck = 0.0
        self.length_neck_lbt = 0.0
        self.compute_psd_az_location(context)
        self.neck_top_location = (0.0,0.0,0.0)
        self.neck_base_location = (0.0,0.0,0.0)
        self.char_mito = False
        self.exclude = False
        self.ensheathment = 'Distant'


    def select_psd(self,context):
        # For this spine head, select faces of this PSD:
        bpy.data.screens['Default'] 
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        reg = obj.mcell.regions.region_list[self.name]
        reg.select_region_faces(context)


    def get_region_index(self,context):
        active_obj = context.active_object
        reg_list = active_obj.mcell.regions.region_list
        reg_index = [i for i in range(len(reg_list)) if reg_list[i].name == self.name][0]
        return(reg_index)


    def compute_region_area(self,context,region_name):
        obj = context.active_object
        mesh = obj.data
        reg = obj.mcell.regions.region_list[region_name]
        reg_faces = list(reg.get_region_faces(mesh))
        t_mat = obj.matrix_world
        area = 0.0
        for face_index in reg_faces:
            face = mesh.polygons[face_index]
            tv0 = mesh.vertices[face.vertices[0]].co * t_mat
            tv1 = mesh.vertices[face.vertices[1]].co * t_mat
            tv2 = mesh.vertices[face.vertices[2]].co * t_mat
            area += mathutils.geometry.area_tri(tv0, tv1, tv2)

#        print("    Area of %s with %d faces is %g" % (region_name,len(reg_faces),area))
        return(area)


    def compute_areas(self,context):
        self.area_psd_az = self.compute_region_area(context,self.name)

        obj = context.active_object
        reg_list = obj.mcell.regions.region_list

        region_name = self.name.replace('sy','sph')
        if reg_list.get(region_name) != None:
            self.area_head = self.compute_region_area(context,region_name)

        region_name = self.name.replace('sy','sp')
        if reg_list.get(region_name) != None:
            self.area_spine = self.compute_region_area(context,region_name)

        region_name = self.name.replace('sy','spn')
        if reg_list.get(region_name) != None:
            self.area_neck = self.compute_region_area(context,region_name)

        region_name = self.name.replace('cs','axb')
        if reg_list.get(region_name) != None:
            self.area_head = self.compute_region_area(context,region_name)


    def compute_psd_az_location(self,context):
        obj = context.active_object
        mesh = obj.data
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        self.select_psd(context)
        bpy.ops.object.mode_set(mode='OBJECT')

        psd_az_verts = [v.co for v in mesh.vertices if v.select == True]
        av = [0,0,0]
        for v in psd_az_verts:
            av[0] += v[0]
            av[1] += v[1]
            av[2] += v[2]
        av[0] = av[0]/len(psd_az_verts)
        av[1] = av[1]/len(psd_az_verts)
        av[2] = av[2]/len(psd_az_verts)
        self.psd_az_location = av.copy()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')


    def select_spn(self, context):
        # For this spine head, select faces of this PSD:
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        reg = obj.mcell.regions.region_list[self.neck_name]
        reg.select_region_faces(context)
      

    def calculate_diameter(self, context):
        self.select_spn(context)
        mesh = context.active_object.data
        old_to_new_index = dict()
        selected_vertices = list()
        selected_faces = list()
        required_vertices = set()

        for face in mesh.polygons:
            if face.select:
                required_vertices.add(face.vertices[0])
                required_vertices.add(face.vertices[1])
                required_vertices.add(face.vertices[2])
        for i, vertex in enumerate(mesh.vertices):
            if i in required_vertices:
                old_to_new_index[i] = len(selected_vertices)
                selected_vertices.append(vertex)
        for face in mesh.polygons:
            if face.select:
                newa = old_to_new_index[face.vertices[0]] + 1
                newb = old_to_new_index[face.vertices[1]] + 1
                newc = old_to_new_index[face.vertices[2]] + 1
                selected_faces.append((newa, newb, newc))

        cwd = bpy.path.abspath(os.path.dirname(__file__))
        tmp_obj = cwd + "/tmp.obj"
        exe = bpy.path.abspath(cwd + "/calc_diameter")

        with open(tmp_obj, "w+") as of:
            for vertex in selected_vertices:
                of.write("v %f %f %f\n" % (vertex.co.x, vertex.co.y, vertex.co.z))
            for p1, p2, p3 in selected_faces:
                of.write("f %d %d %d\n" % (p1, p2, p3))

        subprocess.call([exe, tmp_obj, cwd + "/"])

        # [1:] means ignore the first row "# Segments: N"
        diam_fn = cwd + "/tmp_diameters.txt"

        #metrics = [line.split() for line in open(diam_fn)][1:]
        sort = []
        for line in open(diam_fn):
            metrics = line.strip()
            sort.append(metrics)

        sort = sort[1:]
        len_sort = len(sort)
        #val = (len_sort/2)-1
    
        sort.sort(reverse=True)
        max_diameter = sort[0]
        min_diameter = sort[-1]
        #middle_seg = sort[int(val)]
        #print(middle_seg)
        self.diameter_neck_max = float(max_diameter)
        self.diameter_neck_min = float(min_diameter)


    def compute_neck_stats(self, context):

      obj = context.active_object
      if self.volume_neck > 0.0:
        

        spine_name = self.name.replace('sy','sp')
        head_name = self.name.replace('sy','sph')
        
        # Estimate neck length and diameter from neck volume and neck cross section areas
        neck_top_loc, area_spine_neck_boundary = self.compute_neck_boundary_area(context,spine_name)
        neck_base_loc, area_head_neck_boundary  = self.compute_neck_boundary_area(context,head_name)
        self.neck_top_location = neck_top_loc
        self.neck_base_location = neck_base_loc
        self.area_neck_cross_section_abt = (area_spine_neck_boundary + area_head_neck_boundary)/2.0
        self.diameter_neck = 2*np.sqrt(self.area_neck_cross_section_abt/np.pi)
        self.length_neck = self.volume_neck/self.area_neck_cross_section_abt

        # Estimate neck diameter from neck volume and neck length from base to top
        neck_axis = np.array(self.neck_base_location)-np.array(self.neck_top_location)
        self.length_neck_lbt = np.linalg.norm(neck_axis)
        self.area_neck_cross_section_lbt = self.volume_neck/self.length_neck_lbt
        self.diameter_neck_lbt = 2*np.sqrt(self.area_neck_cross_section_lbt/np.pi)
        print('spine_neck area:',area_spine_neck_boundary)
        print('head_neck area:',area_head_neck_boundary)
        print('avg neck cross section area:',self.area_neck_cross_section_abt)
        print('neck diameter:',self.diameter_neck)
        print('neck length:',self.length_neck)
        print('len_bt neck cross section area:',self.area_neck_cross_section_lbt)
        print('len_bt neck diameter:',self.diameter_neck_lbt)
        print('neck length base to top:',self.length_neck_lbt)


    def compute_neck_boundary_area(self, context, reg_name):

      orig_obj = context.active_object
      reg = orig_obj.mcell.regions.region_list[reg_name]
      # Enter edit mode and unhide and deselect mesh
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.reveal()
      bpy.ops.mesh.select_all(action='DESELECT')
      # Select the region
      reg.select_region_faces(context)
      
      #duplicate region as new object
      bpy.ops.mesh.duplicate()
      #separate object from original
      bpy.ops.mesh.separate(type = 'SELECTED')
      # Unhide and deselect mesh and exit edit mode
      bpy.ops.mesh.reveal()
      bpy.ops.mesh.select_mode(type='EDGE')
      bpy.ops.mesh.select_all(action='DESELECT')
      bpy.ops.object.mode_set(mode='OBJECT')
      
      #deselect original object
      orig_obj.select = False
      #define and name duplicated object
      dup_obj = bpy.context.selected_objects[0]
      dup_obj.name = reg_name + '_tmp_boundary'
      dup_obj.data.name = dup_obj.name
      #make dup_obj active
      scn = bpy.context.scene
      scn.objects.active = dup_obj
      
      #extract non-manifold boundary of dup_obj
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.select_mode(type='EDGE')
      bpy.ops.mesh.select_all(action='DESELECT')
      bpy.ops.mesh.select_non_manifold()
      bpy.ops.mesh.select_all(action='INVERT')
      bpy.ops.mesh.delete(type='EDGE')
      bpy.ops.mesh.select_mode(type='VERT')
      bpy.ops.mesh.select_all(action='SELECT')
      bpy.ops.object.mode_set(mode='OBJECT')
      
      # Now project the boundary onto its principle plane
      
      # Get the mesh vertices
      mesh = dup_obj.data
      verts = mesh.vertices
      bnd_verts = np.array([v.co for v in verts])
      
      # Do PCA on the vertices
      covm = np.cov(bnd_verts,rowvar=0)
      eigval, eigvec = np.linalg.eig(covm)
      
      # Take the top to two principle component vectors
      r = np.sqrt(eigval)
      r = sorted(list(enumerate(r)),key=lambda l: l[1], reverse=True)
      pcv = []
      for i in range(len(r)-1):
        pcv.append(r[i][1]*eigvec[:,r[i][0]])
        
      # Define the normal vector of the principle plane as
      #   the cross product of the two principle vectors
      nvec = np.cross(pcv[0],pcv[1])
      nvec = nvec/np.linalg.norm(nvec)

      # Project the boundary vertices onto the principle plane
      bnd_centroid = bnd_verts.mean(axis=0)
      for i in range(len(bnd_verts)):
          p = bnd_verts[i]
          v = p - bnd_centroid
          p_proj = p - np.dot(v,nvec)*nvec
          verts[i].co.x = p_proj[0]
          verts[i].co.y = p_proj[1]
          verts[i].co.z = p_proj[2]
    #      verts.add(1)
    #      verts[-1].co = p_proj

      # Make planar polygon out of the projected boundary
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.edge_face_add()
      bpy.ops.object.mode_set(mode='OBJECT')
      
      # Extract the boundary vertices in polygonal order
      pverts = []
      poly = mesh.polygons[0]
      for vi in poly.vertices:
          pverts.append(verts[vi].co)
          
      # measure the area of the boundary cross section polygon
      area = abs(self.area_3D_polygon(pverts, nvec))
      
      # We're done so now delete boundary object and mesh  
      dup_obj.select = False
      scn.objects.unlink(dup_obj)
      bpy.data.objects.remove(dup_obj)
      bpy.data.meshes.remove(mesh)
      
      #reselect original object
      scn.objects.active = orig_obj
      orig_obj.select = True
      
      return(list(bnd_centroid), area)
      

    def compute_normal_from_boundary(self, context, reg_name=None):
      # Given a non-closed object of name of a non-closed surface region on
      # an object, compute the normal vector of the best principle plane
      # passing through the boundary of the region

      orig_obj = context.active_object

      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.reveal()
      bpy.ops.mesh.select_all(action='DESELECT')

      if reg_name:
        reg = orig_obj.mcell.regions.region_list[reg_name]
        # Enter edit mode and unhide and deselect mesh
        # Select the region
        reg.select_region_faces(context)
        tmp_obj_name = reg_name + '_tmp_boundary'
      else:
        bpy.ops.mesh.select_all(action='SELECT')
        tmp_obj_name = orig_obj.name + '_tmp_boundary'
      
      #duplicate region as new object
      bpy.ops.mesh.duplicate()
      #separate object from original
      bpy.ops.mesh.separate(type = 'SELECTED')
      # Unhide and deselect mesh and exit edit mode
      bpy.ops.mesh.reveal()
      bpy.ops.mesh.select_mode(type='EDGE')
      bpy.ops.mesh.select_all(action='DESELECT')
      bpy.ops.object.mode_set(mode='OBJECT')
      
      #deselect original object
      orig_obj.select = False
      #define and name duplicated object
      dup_obj = bpy.context.selected_objects[0]
      dup_obj.name = tmp_obj_name
      dup_obj.data.name = dup_obj.name
      #make dup_obj active
      scn = bpy.context.scene
      scn.objects.active = dup_obj

      # Compute centroid of object
      mesh = dup_obj.data
      verts = mesh.vertices
      v_array = np.array([v.co for v in verts])
      v_centroid = v_array.mean(axis=0)
      
      #extract non-manifold boundary of dup_obj
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.select_mode(type='EDGE')
      bpy.ops.mesh.select_all(action='DESELECT')
      bpy.ops.mesh.select_non_manifold()
      bpy.ops.mesh.select_all(action='INVERT')
      bpy.ops.mesh.delete(type='EDGE')
      bpy.ops.mesh.select_mode(type='VERT')
      bpy.ops.mesh.select_all(action='SELECT')
      bpy.ops.object.mode_set(mode='OBJECT')

      # Now find the principle plane of the boundary
      
      # Get the boundary vertices and compute centroid
      mesh = dup_obj.data
      verts = mesh.vertices
      bnd_verts = np.array([v.co for v in verts])
      bnd_centroid = bnd_verts.mean(axis=0)
      
      # Do PCA on the vertices
      covm = np.cov(bnd_verts,rowvar=0)
      eigval, eigvec = np.linalg.eig(covm)
      
      # Take the top to two principle component vectors
      r = np.sqrt(eigval)
      r = sorted(list(enumerate(r)),key=lambda l: l[1], reverse=True)
      pcv = []
      for i in range(len(r)-1):
        pcv.append(r[i][1]*eigvec[:,r[i][0]])

      # Define the normal vector of the principle plane as
      # the cross product of the two principle vectors
      # Orient the vector to point toward the centroid of the object
      nvec = np.cross(pcv[0],pcv[1])
      nvec = nvec/np.linalg.norm(nvec)
      objvec = v_centroid - bnd_centroid
      objvec = objvec/np.linalg.norm(objvec)
      nvec = np.sign(nvec.dot(objvec))*nvec

      # Convert nvec and bnd_centroid to list
      nvec = list(nvec)
      bnd_centroid = list(bnd_centroid)

      # We're done so now delete boundary object and mesh  
      dup_obj.select = False
      scn.objects.unlink(dup_obj)
      bpy.data.objects.remove(dup_obj)
      bpy.data.meshes.remove(mesh)
      
      #reselect original object
      scn.objects.active = orig_obj
      orig_obj.select = True
      
      return(bnd_centroid, nvec)

      
    def area_3D_polygon(self, verts, nvec):
        
        '''
        # make test triangle to validate area computation: area = 0.0074489
        print('verts: ', verts)
        verts = []
        verts.append([5.543,5.581,5.878])
        verts.append([5.559,5.576,5.753])
        verts.append([5.450,5.648,5.843])
        v1 = np.array(verts[1]) - np.array(verts[0])
        v2 = np.array(verts[2]) - np.array(verts[0])
        nvec = np.cross(v1,v2)
        nvec = nvec/np.linalg.norm(nvec)
        '''
        
        n = len(verts)
        verts = verts.copy()
        verts.append(verts[0])
        
        # select largest abs coordinate to ignore for projection
        ax = abs(nvec[0])   # abs x-coord
        ay = abs(nvec[1])   # abs y-coord
        az = abs(nvec[2])   # abs z-coord
            
        coord = 3          # ignore z-coord
        if (ax > ay):
            if (ax > az):
                coord = 1   # ignore x-coord
        elif (ay > az):
             coord = 2      # ignore y-coord

        # compute area of the 2D projection
        area = 0.0
        j=2
        k=0
        if coord == 1:
            for i in range(1,n):
                area += (verts[i][1] * (verts[j][2] - verts[k][2]))
                j+=1
                k+=1
        elif coord == 2:
            for i in range(1,n):
                area += (verts[i][2] * (verts[j][0] - verts[k][0]))
                j+=1
                k+=1
        elif coord == 3:
            for i in range(1,n):
                area += (verts[i][0] * (verts[j][1] - verts[k][1]))
                j+=1
                k+=1
                
        if coord == 1:   # wrap-around term
            area += (verts[n][1] * (verts[1][2] - verts[n-1][2]))
        elif coord == 2:
            area += (verts[n][2] * (verts[1][0] - verts[n-1][0]))
        elif coord == 3:
            area += (verts[n][0] * (verts[1][1] - verts[n-1][1]))

        # scale to get area before projection
        if coord == 1:
            area /= 2*nvec[0]
        elif coord == 2:
            area /= 2*nvec[1]
        elif coord == 3:
            area /= 2*nvec[2]
            
        return area



    def output(self,context,file):
#        if self.area_psd_az == 0.0:
#            self.compute_areas(context)
#        if (self.psd_az_location[0] == 0.0) and \
#            (self.psd_az_location[1] == 0.0) and \
#            (self.psd_az_location[2] == 0.0):
#              self.compute_psd_az_location(context)
        file.write('%s'  % (self.name))
        file.write(' %s' % (self.char_postsynaptic))
        file.write(' %g' % (self.volume))
        file.write(' %g' % (self.volume_spine))
        file.write(' %g' % (self.volume_neck))
        file.write(' %g' % (self.area_head))
        file.write(' %g' % (self.area_psd_az))
        file.write('\n')



    def compute_volume(self,context,mode,n_components,make_shell_opt=False,make_jaccard_opt=False):
        # Now make a new region for spine head and name it
          # Generate the name for the spine head
        orig_obj = context.active_object
#        print("Computing volume of %s on %s..." % (self.name, orig_obj.name))
        if mode == 'head':
            if self.char_postsynaptic:
                reg_name = self.name.replace('sy','sph')
                self.head_name = reg_name
            else:
                reg_name = self.name.replace('sy','axb')
                self.head_name = reg_name
        else: 
            reg_name = self.name.replace('sy','sp')
            self.spine_name = reg_name

        reg = orig_obj.mcell.regions.region_list.get(reg_name)
        if reg == None:
#            print("  Adding new region %s" % (reg_name))
            orig_obj.mcell.regions.add_region_by_name(context,reg_name)
            reg = orig_obj.mcell.regions.region_list[reg_name]
        else:
#            print("  Resetting region %s" % (reg_name))
            reg.reset_region(context)
#        print("  Assigning faces to region %s" % (reg_name))
        reg.assign_region_faces(context)
    
        # Compute area of region
#        print("  Computing area of %s" % (reg_name))
        if mode == 'head':
            self.area_head = self.compute_region_area(context,reg_name)
        else:
            self.area_spine = self.compute_region_area(context,reg_name)

        # DUPLICATE SELECTION AND SEPARATE
        #editmode
        bpy.ops.object.mode_set(mode='EDIT')
        #duplicate object
        bpy.ops.mesh.duplicate()
        #separate object from original
        bpy.ops.mesh.separate(type = 'SELECTED')
        # Unhide and deselect mesh and exit edit mode
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

       # DEFINE OBJECT 1 (original) AND 2 (hull to be) and SELECT O2
        #deselect original object
        orig_obj.select = False
        #define and name hull object
        hull = context.selected_objects[0]
        hull.name = orig_obj.name + '_tmp'
        #make hull active
        scn = context.scene
        scn.objects.active = hull

        # Compute location of top of neck:
        if mode == 'head':
            nloc, nvec = self.compute_normal_from_boundary(context)
            self.neck_top_location = nloc.copy()
            self.head_base_normal = nvec.copy()

            '''
            hull_mesh = hull.data
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.mode_set(mode='OBJECT')
            neck_top_verts = [v.co for v in hull_mesh.vertices if v.select == True]
            av = [0,0,0]
            for v in neck_top_verts:
                av[0] += v[0]
                av[1] += v[1]
                av[2] += v[2]
            av[0] = av[0]/len(neck_top_verts)
            av[1] = av[1]/len(neck_top_verts)
            av[2] = av[2]/len(neck_top_verts)
            self.neck_top_location = av.copy()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='FACE')
            '''

        # Compute location of base of neck:
        if mode == 'spine':
            hull_mesh = hull.data
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.mode_set(mode='OBJECT')
            neck_base_verts = [v.co for v in hull_mesh.vertices if v.select == True]
            av = [0,0,0]
            for v in neck_base_verts:
                av[0] += v[0]
                av[1] += v[1]
                av[2] += v[2]
            av[0] = av[0]/len(neck_base_verts)
            av[1] = av[1]/len(neck_base_verts)
            av[2] = av[2]/len(neck_base_verts)
            self.neck_base_location = av.copy()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type='FACE')

        # MAKE CONVEX HULL
        #editmode
        bpy.ops.object.mode_set(mode='EDIT')
        #select all vertices in vertex mode
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        #create convex hull
        bpy.ops.mesh.convex_hull()
        #exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

        orig_piece = None
        if (n_components > 1):
            #Original object contains disjoint pieces
            #The Boolean modifier does not work correctly with disjoint pieces
            #So we need to detect and handle this special case by
            #isolating the piece of dendrite containing the PSD we're working with
            hull.select = False
            orig_obj.select = True
            scn.objects.active = orig_obj

            # Count total vertices and number of vertices contiguous with PSD
            self.select_psd(context)
            bpy.ops.object.mode_set(mode='OBJECT')
            orig_mesh = orig_obj.data
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()
            n_v_tot = len(orig_mesh.vertices)
            n_v_sel = orig_mesh.total_vert_sel
            if (n_v_sel < n_v_tot):
                # Dendrite contains more than one component so duplicate
                # and separate the selected piece and use it for the boolean step
                bpy.ops.mesh.duplicate()
                #separate piece from original
                bpy.ops.mesh.separate(type = 'SELECTED')

                #deselect original object
                bpy.ops.object.mode_set(mode='OBJECT')
                orig_obj.select = False
                #define and name piece object
                orig_piece = context.selected_objects[0]
                orig_piece.name = orig_obj.name + '_piece_tmp'
                orig_piece.select = False

            #make hull active again
            bpy.ops.object.mode_set(mode='OBJECT')
            hull.select = True
            scn.objects.active = hull

        # Enlarge convex hull by 1 nm to make Boolean Intersection more robust
        #expand shape of shell by 0.001 nm
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        offset = -0.001
        bpy.ops.transform.shrink_fatten(value=offset)
        bpy.ops.object.mode_set(mode='OBJECT')

        # BOOLEAN INTERSECT
        #add Boolean modifier
        hull.modifiers.new("Boolean", 'BOOLEAN')
        #set Boolean modifier to intersect function (actually the default)
        hull.modifiers["Boolean"].operation = 'INTERSECT'
        #set object for Boolean to intersect with
        if (orig_piece != None):
          hull.modifiers["Boolean"].object = orig_piece
        else:
          hull.modifiers["Boolean"].object = orig_obj
        #apply modifier
        bpy.ops.object.modifier_apply(modifier="Boolean")
        #triangulate
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')

        #Delete dendrite piece if we made one
        if (orig_piece != None):
            hull.select = False
            orig_piece.select = True
            scn.objects.active = orig_piece
            bpy.ops.object.delete()
            hull.select = True
            scn.objects.active = hull

        # Make sure Boolean result contains one component
        #   Method 1:
        hull_mesh = hull.data
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Count total vertices and number of vertices contiguous with vertex 0
        bpy.ops.object.mode_set(mode='OBJECT')
        hull_mesh.vertices[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()

        n_v_tot = len(hull_mesh.vertices)
        n_v_sel = hull_mesh.total_vert_sel
        bpy.ops.object.mode_set(mode='OBJECT')

        # Loop until only one contiguous component remains
        while (n_v_sel < n_v_tot):
            # make list of indices of first component
            vl1 = [v.index for v in hull_mesh.vertices if v.select == True]
            # make list of indices of remaining component(s)
            vl2 = [v.index for v in hull_mesh.vertices if v.select == False]
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            # Select and delete vertices contiguous with first vertex of smaller piece
            if (len(vl2) < len(vl1)):
                hull_mesh.vertices[vl2[0]].select = True
            else:
                hull_mesh.vertices[vl1[0]].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.delete(type='VERT')

            # Count total vertices and number of vertices contiguous with vertex 0 of result and loop again if necessary
            bpy.ops.object.mode_set(mode='OBJECT')
            hull_mesh.vertices[0].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()
            n_v_tot = len(hull_mesh.vertices)
            n_v_sel = hull_mesh.total_vert_sel
            bpy.ops.object.mode_set(mode='OBJECT')
        '''
        '''

        '''
        # Method 2:
        # Also, delete all extraneous verts, faces, and edges.
        #   Necessary because boolean modifier is not totally robust.
        #   Order matters here.   
        hull_mesh = hull.data
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')


        # First, delete vertices not contiguous with PSD
        bpy.ops.object.mode_set(mode='OBJECT')
        hull_mesh.vertices[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_linked()
        bpy.ops.object.mode_set(mode='OBJECT')
        vl1 = [v.index for v in hull_mesh.vertices if v.select == True]
        vl2 = [v.index for v in hull_mesh.vertices if v.select == False]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        # Select and delete vertices contiguous with first vertex of smaller piece
        if (len(vl2) < len(vl1)):
                hull_mesh.vertices[vl2[0]].select = True
        else:
                hull_mesh.vertices[vl1[0]].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()
        bpy.ops.mesh.delete(type='VERT')

        n_v_tot = len(hull_mesh.vertices)
        n_v_sel = hull_mesh.total_vert_sel
        if (n_v_sel < n_v_tot):
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Second, delete faces not contiguous with PSD
        reg = obj.mcell.regions.region_list[self.name]
        reg.select_region_faces(context)
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_linked()
        n_f_tot = len(hull_mesh.polygons)
        n_f_sel = hull_mesh.total_face_sel
        if (n_f_sel < n_f_tot):
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Last, delete edges not contiguous with PSD
        reg = obj.mcell.regions.region_list[self.name]
        reg.select_region_faces(context)
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_linked()
        n_e_tot = len(hull_mesh.edges)
        n_e_sel = hull_mesh.total_edge_sel
        if (n_e_sel < n_e_tot):
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')
        '''

        # Make normals consistent
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False) 
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # CALCULATE VOLUME
        bpy.ops.mcell.meshalyzer()
#        print("%s meshalyzer status:  %s" % (hull.name, scn.mcell.meshalyzer.status))
#        print("%s meshalyzer volume:  %s" % (hull.name, scn.mcell.meshalyzer.volume))
        #check status
        if (scn.mcell.meshalyzer.status == ''):
            volume = scn.mcell.meshalyzer.volume
            # Shouldn't be necessary but maybe bug in Blender:
            if volume < 0:
                print("%s negative volume, flipping normals" % (hull.name))
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.flip_normals()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.mcell.meshalyzer()
                volume = scn.mcell.meshalyzer.volume
            if mode == 'head':
                self.volume = volume
            else:
                self.volume_spine = volume
        else:
            print("%s failed meshalyzer test:  %s" % (hull.name, scn.mcell.meshalyzer.status))

        # Make shell object from hull/head/spine
        if make_shell_opt:
            if mode == 'head': 
                if self.char_postsynaptic:
                    shell_name = self.name.replace('sy', 'sphs')
                    offset = -0.005
                else:
                    shell_name = self.name.replace('sy', 'axbs')
                    offset = -0.005
            else:
                shell_name = self.name.replace('sy', 'sps')
                offset = -0.010
#                offset = -0.050
            #remove regions from shell
            hull.mcell.regions.remove_all_regions(context)
            #expand shape of shell by 0.005 nm
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.shrink_fatten(value=offset)
            bpy.ops.object.mode_set(mode='OBJECT')
            #rename the shell
            shell_obj = scn.objects.get(shell_name)
            if shell_obj != None:
                hull.select = False
                shell_obj.hide = False
                shell_obj.select = True
                scn.objects.active = shell_obj
                bpy.ops.object.delete()
                hull.select = True
                scn.objects.active = hull
            hull.name = shell_name
            hull.select = False
            hull.hide = True
        elif make_jaccard_opt:
            shell_name = self.name.replace('sy', 'sph') + '_tmp_jaccard'
            #remove regions from shell
            hull.mcell.regions.remove_all_regions(context)
            #rename the shell
            shell_obj = scn.objects.get(shell_name)
            if shell_obj != None:
                hull.select = False
                shell_obj.hide = False
                shell_obj.select = True
                scn.objects.active = shell_obj
                bpy.ops.object.delete()
                hull.select = True
                scn.objects.active = hull
            hull.name = shell_name
            hull.select = False
            hull.hide = False
        else:
            bpy.ops.object.delete()


        # Make neck
        if (self.volume != 0.0) and (self.volume_spine != 0.0):
            #reselect original dendrite
            orig_obj.select = True
            scn.objects.active = orig_obj
            #unhide and unselect original mesh
            context.scene.update()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(type='FACE')
            bpy.ops.mesh.select_all(action='DESELECT')
	
            # Make Neck Region
            sp_name = self.name.replace('sy', 'sp')
            sph_name = self.name.replace('sy', 'sph')
            spn_name = self.name.replace('sy', 'spn')

            neck_reg = orig_obj.mcell.regions.region_list.get(spn_name)
            if neck_reg == None:
                orig_obj.mcell.regions.add_region_by_name(context,spn_name)
                neck_reg = orig_obj.mcell.regions.region_list[spn_name]
            else:
                neck_reg.reset_region(context)
            spine_reg = orig_obj.mcell.regions.region_list[sp_name]
            head_reg = orig_obj.mcell.regions.region_list[sph_name]

            spine_reg.select_region_faces(context)
            head_reg.deselect_region_faces(context)

            neck_reg.assign_region_faces(context)
            self.neck_name = spn_name
            self.area_neck = self.compute_region_area(context,spn_name)

            # Calculate Neck Volume
            self.volume_neck = self.volume_spine - self.volume
            bpy.ops.object.mode_set(mode='OBJECT')


        # RETURN TO ORIGINAL VIEW
        #reselect original dendrite
        orig_obj.select = True
        scn.objects.active = orig_obj	
        #re-enter editmode
        bpy.ops.object.mode_set(mode='EDIT')
        #unhide original
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='FACE')



class SpineHeadAnalyzerObjectProperty(bpy.types.PropertyGroup):
    psd_list = CollectionProperty(
        type=SpineHeadAnalyzerPSDProperty, name="Spine PSD List")
    sp_list = CollectionProperty(
        type=SpineHeadAnalyzerPSDProperty, name="contact list")
    active_spn_region_index = IntProperty(name="Active SPN Index", default=0)
    active_psd_region_index = IntProperty(name="Active PSD Index", default=0)
    n_components = IntProperty(name="Number of Components in Mesh", default=0)
    make_shell_head_opt = BoolProperty(name="Make Spine Head Shell?", default=True)
    make_shell_spine_opt = BoolProperty(name="Make Spine Shell?", default=True)
    set_head_mat_opt = BoolProperty(name="Set Spine Head Material?", default=False)
    diameter_neck = FloatProperty(name="Diameter of Neck",default=0.0)

    def get_active_psd(self,context):
        active_obj = context.active_object
        reg_list = active_obj.mcell.regions.region_list
        sy_list = [reg.name for reg in reg_list if reg.name.rfind('sy') > -1]
        psd = None
        psd_region_name = None
        if len(sy_list) > 0:
            psd_region_name = reg_list[self.active_psd_region_index].name
            psd = self.psd_list.get(psd_region_name)
        return(psd, psd_region_name)


    def add_psd(self,context,name):
        """ Add a new PSD to psd_list """
        new_psd=self.psd_list.add()
        new_psd.init_psd(context,name)
        return(new_psd)


    def select_psd(self,context):
        if self.n_components == 0:
#          print("Computing n components on %s" % (context.active_object.name))
          self.set_n_components(context)

        psd, psd_region_name = self.get_active_psd(context)
        if psd_region_name != None:
            if psd == None:
                psd = self.add_psd(context, psd_region_name)
            psd.select_psd(context)


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


    def recompute_volumes(self,context,report_file):
        if self.n_components == 0:
          self.set_n_components(context)

        obj = context.active_object
        bpy.ops.object.mode_set(mode='OBJECT')
        reg_list = obj.mcell.regions.region_list
        sy_list = [reg.name for reg in reg_list if reg.name.rfind('sy') > -1]
        psd = None
        psd_region_name = None
        for psd_region_name in sy_list:
            print("Checking %s..." % (psd_region_name))
            report_file.write("Checking %s...\n" % (psd_region_name))
            psd = self.psd_list.get(psd_region_name)
            if psd == None:
                print("  Automatically added and excluded PSD: %s" % (psd_region_name))
                report_file.write("  Automatically added and excluded PSD: %s\n" % (psd_region_name))
                psd = self.add_psd(context, psd_region_name)
                psd.exclude = True
            if (psd.exclude):
                print("  Skipping excluded PSD: %s" % (psd_region_name))
                report_file.write("  Skipping excluded PSD: %s\n" % (psd_region_name))
            else:
                if (psd.psd_az_location[0] == 0.0) and \
                    (psd.psd_az_location[1] == 0.0) and \
                    (psd.psd_az_location[2] == 0.0):
                        psd.compute_psd_az_location(context)
                        print("  Updated PSD location: <%g, %g, %g>" % (psd.psd_az_location[0],psd.psd_az_location[1],psd.psd_az_location[2]))
                        report_file.write("  Updated PSD location: <%g, %g, %g>\n" % (psd.psd_az_location[0],psd.psd_az_location[1],psd.psd_az_location[2]))
                if (psd.area_psd_az == 0.0):
                    psd.area_psd_az = psd.compute_region_area(context,psd_region_name)
                    print("  Updated PSD area: %g" % (psd.area_psd_az))
                    report_file.write("  Updated PSD area: %g\n" % (psd.area_psd_az))
                if ((psd.area_head == 0.0) or (psd.area_spine == 0.0)):
                    head_region_name = psd_region_name.replace('sy','sph')
                    spine_region_name = psd_region_name.replace('sy','sp')
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='FACE')
                    if psd.area_head == 0.0:
                        reg = reg_list.get(head_region_name)
                        if reg == None: 
                            print("  ***** Missing spine head for PSD %s" % (psd_region_name))
                            report_file.write("  ***** Missing spine head for PSD %s\n" % (psd_region_name))
#                            pass
                        else:
                            mode = 'head'
                            bpy.ops.mesh.select_all(action='DESELECT')
                            reg.select_region_faces(context)
                            psd.compute_volume(context,mode,self.n_components,self.make_shell_head_opt)
                            print('  Updated volume of %s  head: %g' % (head_region_name, psd.volume))
                            report_file.write('  Updated volume of %s  head: %g\n' % (head_region_name, psd.volume))

                    if psd.area_spine == 0.0:
                        reg = reg_list.get(spine_region_name)
                        if reg == None: 
                            print("  Missing whole spine for PSD %s" % (psd_region_name))
                            report_file.write("  Missing whole spine for PSD %s\n" % (psd_region_name))
#                            pass
                        else:
                            mode = 'spine'
                            bpy.ops.mesh.select_all(action='DESELECT')
                            reg.select_region_faces(context)
                            psd.compute_volume(context,mode,self.n_components,self.make_shell_spine_opt)
                            print('  Updated volume of %s  whole spine: %g  neck: %g' % (spine_region_name, psd.volume_spine, psd.volume_neck))
                            report_file.write('  Updated volume of %s  whole spine: %g  neck: %g\n' % (spine_region_name, psd.volume_spine, psd.volume_neck))
                if (psd.volume < 0.0):
                    report_file.write('  ***** Negative head volume for PSD %s %g\n' % (psd_region_name, psd.volume))
                if (psd.volume_spine < 0.0):
                    print('  ***** Negative whole spine volume for PSD %s %g' % (psd_region_name, psd.volume_spine))
                    report_file.write('  ***** Negative whole spine volume for PSD %s %g\n' % (psd_region_name, psd.volume_spine))
                if (psd.volume_neck < 0.0):
                    print('  ***** Negative neck volume for PSD %s %g' % (psd_region_name, psd.volume_neck))
                    report_file.write('  ***** Negative neck volume for PSD %s %g\n' % (psd_region_name, psd.volume_neck))
                if (psd.volume_neck > 0.0):
                    psd.compute_neck_stats(context)
                    neck_region_name = psd_region_name.replace('sy','spn')
                    report_file.write('  Updated diameter and length of neck %s  max diameter: %g  min diameter: %g  length: %g\n' % (neck_region_name, psd.diameter_neck_max, psd.diameter_neck_min, psd.length_neck))
                  
            bpy.ops.object.mode_set(mode='OBJECT')


    def compute_volume(self,context,mode):
        psd, psd_region_name = self.get_active_psd(context)
        if psd != None:
            if mode == 'head':
                psd.compute_volume(context,mode,self.n_components,self.make_shell_head_opt)
            else:
                psd.compute_volume(context,mode,self.n_components,self.make_shell_spine_opt)
            self.active_psd_region_index = psd.get_region_index(context)


    def calculate_diameter(self, context):
        psd, psd_region_name = self.get_active_psd(context)
        if psd != None:
            psd.calculate_diameter(context)


    def output(self,context,file):
        for psd in self.psd_list:
            psd.output(context,file)


    def draw_panel(self, context, panel):
        layout = panel.layout

        active_obj = context.active_object

        if (active_obj != None) and (active_obj.type == 'MESH'):
            row = layout.row()
            row.label(text="Select all faces of spine head associated with a PSD", icon='FORWARD')
            row = layout.row()
            row.label(text="Spine PSDs:", icon='MESH_ICOSPHERE')
            row = layout.row()

# Layout active_object.mcell.regions.region_list with filter "*sy*" and active_psd_region_index
#FIXME: add "*sy*" filter:
            row.template_list("NEUROPIL_UL_check_psd","spine_psd_list",
                          active_obj.mcell.regions, "region_list",
                          self, "active_psd_region_index",
                          rows=2)            
            psd, psd_region_name = self.get_active_psd(context)
            row = layout.row()
            row.prop(self,"make_shell_head_opt",text="Make Spine Head Shell")
            row = layout.row()
            row.prop(self,"make_shell_spine_opt",text="Make Spine Shell")
            row = layout.row()
            row.operator("spine_head_analyzer.output", text="Output")
            row = layout.row()
            row.operator("spine_head_analyzer.recompute_volumes", text="Recompute All Volumes")
            if psd_region_name != None:
                row = layout.row()
                row.operator("spine_head_analyzer.select_psd", text="Select PSD")
            if psd != None:
                if psd.char_postsynaptic:
                    row = layout.row()
                    row.prop(psd,"exclude",text="Exclude this spine")
                    mesh = active_obj.data
                    row = layout.row()
                    row.enabled = (mesh.total_face_sel > 0)
                    row = layout.row()
                    row.operator("spine_head_analyzer.compute_volume", text="Compute Spine Head Volume")
                    row.enabled = (mesh.total_face_sel > 0)
                    row.operator("spine_head_analyzer.compute_volume_spine", text="Compute Whole Spine Volume")
                    if (psd.volume != 0.0):
                        row = layout.row()
                        row.label(text="Spine Head Volume: %.4g um^3" % (psd.volume))
                    if (psd.volume_neck != 0.0):                    
                        row = layout.row()
                        row.label(text="Spine Neck Volume: %.4g um^3" % (psd.volume_neck))
                    if (psd.volume_spine != 0.0):                    
                        row = layout.row()
                        row.label(text="Whole Spine Volume: %.4g um^3" % (psd.volume_spine))
                    row = layout.row()
                    row.label(text="Spine Neck List:", icon='MESH_ICOSPHERE')          
                    if psd.neck_name != "": 
                        row = layout.row()
                        row.operator("spine_head_analyzer.calculate_diameter", text="Calculate Diameter")
                        row = layout.row()
                        row.label(text="Max Diameter: %.5f um" % (psd.diameter_neck_max))
                        row = layout.row()
                        row.label(text="Max Diameter: %.5f um" % (psd.diameter_neck_min))
                #else:
                #    row = layout.row()
                #    row.prop(psd,"exclude",text="Exclude this bouton")


                    #mesh = active_obj.data
                    #row = layout.row()
                    #row.enabled = (mesh.total_face_sel > 0)
                    #row.operator("spine_head_analyzer.compute_volume", text="Compute Bouton Volume")
                    #if (psd.volume != 0.0):
                    #    row = layout.row()
                    #    row.label(text="Bouton: %s Volume: %.4g" % (psd.head_name, psd.volume))
                    #row = layout.row()
                    #row.prop(psd,"char_mito",text="Mitochondrion in Bouton")
                #row = layout.row()
                #row.template_list("DIAMETER_UL_psd_draw_item", "spn_list",
                #              active_obj.mcell.regions, "region_list",
                #              self, "active_spn_region_index",
                #              rows=2)
                #row = layout.row()

#class SpineHeadAnalyzerSceneProperty(bpy.types.PropertyGroup):

    #def output(self,context,file):
    #    scn = context.scene
    #    for obj in scn:
    #        for psd in spine_head_ana.psd_list:
    #        psd.output(context,file)




