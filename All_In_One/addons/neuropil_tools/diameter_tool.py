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
import subprocess
import os

# blender imports
import bpy
# IMPORT SWIG MODULE(s)
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

# Get spine neck of interest


class NEUROPIL_OT_select_spn(bpy.types.Operator):
    bl_idname = "diameter_tool.select_spn"
    bl_label = "Select spine"
    bl_description = "Select Spine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.diameter.select_spn(context)
        return {'FINISHED'}

# The operator calls the calculate_diameter function with the press of a button


class NEUROPIL_OT_calculate_diameter(bpy.types.Operator):
    bl_idname = "diameter_tool.calculate_diameter"
    bl_label = "Calculate diameter"
    bl_description = "Calculate diameter of spine head"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.diameter.calculate_diameter(context)
        return{'FINISHED'}

# Diameter Tool Panel:


class DIAMETER_UL_psd_draw_item(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        self.filter_name = "*spn*"
        active_obj = context.active_object
        layout.label(item.name)

# Draw panel


class DIAMETER_PT_DiameterTool(bpy.types.Panel):
    bl_label = "Calculate diameter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if context.object is not None:
            context.object.diameter.draw_panel(context, panel=self)

# Set property class to call neck region on each object


class DiameterToolNeckProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Spine Neck", default="")
    diameter_neck = FloatProperty(name="Diameter of Neck", default=0.0)

    def init_spn(self, context, name):
        obj_name = context.active_object.name
        dend_filter = 'd[0-9]{3}$'
        axon_filter = 'a[0-9]{3}$'
        if re.match(dend_filter, obj_name) is not None:
            self.char_postsynaptic = True
        elif re.match(axon_filter, obj_name) is not None:
            self.char_postsynaptic = False
        self.name = name
        self.diameter_neck = 0.0

    def select_spn(self, context):
        # For this spine head, select faces of this PSD:
        obj = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        reg = obj.mcell.regions.region_list[self.name]
        reg.select_region_faces(context)

    def calculate_diameter(self, context, spine):
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

        metrics = [line.split() for line in open(diam_fn)][1:]
        max_diameter = -1
        for metric in metrics:
            max_diameter = max(max_diameter, float(metric[0]))

        return max_diameter


# Object property
class DiameterToolObjectProperty(bpy.types.PropertyGroup):
    spn_list = CollectionProperty(
        type=DiameterToolNeckProperty, name="Spine List")
    active_spn_region_index = IntProperty(name="Active SPN Index", default=0)
    n_components = IntProperty(name="Number of Components in Mesh", default=0)
    #head_name = StringProperty(name="Spine Head Name", default="")
    diameter_neck = FloatProperty(name="Diameter of Neck",default=0.0)
    #diameter_head = FloatProperty(name="Diameter of Head",default=0.0)

    # def init_psd(self,context,name):
        #obj_name = context.active_object.name
        #self.name = name
        #self.head_name = ""
        #self.spine_name = ""
        #self.diameter_neck = 0.0
        #self.diameter_head = 0.0

    def get_active_spn(self, context):
        active_obj = context.active_object
        reg_list = active_obj.mcell.regions.region_list
        spn_list = [reg.name for reg in reg_list if reg.name.rfind('spn') > -1]
        spn = None
        spn_region_name = None
        if len(spn_list) > 0:
            spn_region_name = reg_list[self.active_spn_region_index].name
            spn = self.spn_list.get(spn_region_name)
        return(spn, spn_region_name)

    def add_spn(self, context, name):
        """ Add a new PSD to psd_list """
        new_spn = self.spn_list.add()
        new_spn.init_spn(context, name)
        return(new_spn)

    def select_spn(self, context):
        if self.n_components == 0:
#          print("Computing n components on %s" % (context.active_object.name))
            self.set_n_components(context)

        spn, spn_region_name = self.get_active_spn(context)
        if spn_region_name is not None:
            if spn is None:
                spn = self.add_spn(context, spn_region_name)
            spn.select_spn(context)

    def set_n_components(self, context):
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
            vl1 = [v.index for v in mesh.vertices if v.select]
            # make list of indices of remaining component(s)
            vl2 = [v.index for v in mesh.vertices if v.select == False]
            # Grow selection with vertices contiguous with first vertex of
            # remainder
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

    def calculate_diameter(self, context):
        spn, spn_region_name = self.get_active_spn(context)

        print("spine", spn, spn_region_name, dir(spn))
        print("index", self.active_spn_region_index)

        # reg_list = context.active_object.mcell.regions.region_list
        # spine = reg_list[self.active_spn_region_index]
        # spine_faces = spine.get_region_faces(context.selected_objects[0].data)

        # print(spine_faces)
        # print(len(spine_faces))
        #
        if spn and spn_region_name:
            self.diameter_neck = spn.calculate_diameter(context, spn)
        else:
            self.diameter_neck = 0.0


# Draw panel
    def draw_panel(self, context, panel):
        layout = panel.layout
        active_obj = context.active_object

        if (active_obj is not None) and (active_obj.type == 'MESH'):
            row = layout.row()
            row.label(text="Spine Neck List:", icon='MESH_ICOSPHERE')
            row = layout.row()
            row.template_list("DIAMETER_UL_psd_draw_item", "spn_list",
                              active_obj.mcell.regions, "region_list",
                              self, "active_spn_region_index",
                              rows=2)
            #spn, spn_region_name = self.get_active_psd(context)
            # if spn_region_name != None:
            row = layout.row()
            row.operator("diameter_tool.select_spn", text="Select Spine Neck")
            row = layout.row()
            row.operator(
                "diameter_tool.calculate_diameter",
                text="Calculate Diameter")
            row = layout.row()
            row.label(text="Max Diameter: %.5f" % (self.diameter_neck))

    # def get_active_psd(self,context):
        #active_obj = context.active_object
        #reg_list = active_obj.mcell.regions.region_list
