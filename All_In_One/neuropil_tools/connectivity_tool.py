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
This file contains the classes for Connectivity Tool
"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
import mathutils

# python imports

import re
import neuropil_tools
import cellblender

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Spine Head Analyzer Operators:

class CONNECTIVITY_OT_show_synaptic_partner(bpy.types.Operator):
    bl_idname = "connectivity_tool.show_synaptic_partner"
    bl_label = "Show Axon and Dendrite for Selected PSD or AZ"
    bl_description = "Show Axon and Dendrite for Selected PSD or AZ"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.object.connectivity.show_synaptic_partner(context)
        return {'FINISHED'}


class CONNECTIVITY_OT_output_pre_to_post(bpy.types.Operator):
    bl_idname = "connectivity_tool.output_pre_to_post"
    bl_label = "Output Connectivity Data"
    bl_description = "Output Connectivity Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        outFile = open('pre_to_post_connectivity.txt', 'wt')
#        outFile.write('# axon sy dendrite\n')

        axon_filter = 'a[0-9]{3}$'

        axons = [obj.name for obj in context.scene.objects if re.match(axon_filter,obj.name) != None]
        axons.sort()

        for axon in axons:
            obj = context.scene.objects[axon]
            obj.connectivity.output_pre_to_post(context,obj,outFile)

        outFile.close()
        return {'FINISHED'}


class CONNECTIVITY_OT_output_post_to_pre(bpy.types.Operator):
    bl_idname = "connectivity_tool.output_post_to_pre"
    bl_label = "Output Connectivity Data"
    bl_description = "Output Connectivity Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        outFile = open('post_to_pre_connectivity.txt', 'wt')
#        outFile.write('# dendrite sy axon\n')

        dend_filter = 'd[0-9]{3}$'

        dends = [obj.name for obj in context.scene.objects if re.match(dend_filter,obj.name) != None]
        dends.sort()

        for dend in dends:
            obj = context.scene.objects[dend]
            obj.connectivity.output_post_to_pre(context,obj,outFile)

        outFile.close()
        return {'FINISHED'}


# Connectivity Tool Panel:

class CONNECTIVITY_UL_psd_draw_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        self.filter_name = "*sy*"
        active_obj = context.active_object
        layout.label(item.name)


class CONNECTIVITY_PT_ConnectivityTool(bpy.types.Panel):
    bl_label = "Connectivity Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Neuropil Tools"

    def draw(self, context):
        if context.object != None:
            context.object.connectivity.draw_panel(context, panel=self)


# Connectivity Tool Properties:

class ConnectivityToolObjectProperty(bpy.types.PropertyGroup):
    active_psd_region_index = IntProperty(name="Active PSD Index", default=0)

    def get_active_psd(self,context):
        active_obj = context.active_object
        reg_list = active_obj.mcell.regions.region_list
        sy_list = [reg.name for reg in reg_list if reg.name.rfind('sy') > -1]
        psd_region_name = None
        if len(sy_list) > 0:
            psd_region_name = active_obj.mcell.regions.region_list[self.active_psd_region_index].name
        return(psd_region_name)


    def get_dendrite(self,context,psd_region_name):
        scn = context.scene
        dend_filter = 'd[0-9]{3}'
        m = re.match(dend_filter,psd_region_name)
        if m != None:
            dend_name = m.group(0)
            return (scn.objects[dend_name])


    def get_axon(self,context,psd_region_name):
        scn = context.scene
        axon_filter = 'a[0-9]{3}$'
        axon_objs = [obj for obj in scn.objects if re.match(axon_filter,obj.name) != None]
        for obj in axon_objs:
            reg_list = obj.mcell.regions.region_list
            if reg_list.get(psd_region_name) != None:
                return(obj)


    def show_synaptic_partner(self,context):
        psd_region_name = self.get_active_psd(context)
        if self.is_dendrite(context):
            self.show_axon(context,psd_region_name)
        else:
            self.show_dendrite(context,psd_region_name)
        

    def show_dendrite(self,context,psd_region_name):
        dend_obj = self.get_dendrite(context,psd_region_name)
        if (dend_obj != None):
            dend_obj.hide = False


    def show_axon(self,context,psd_region_name):
        axon_obj = self.get_axon(context,psd_region_name)
        if (axon_obj != None):
            axon_obj.hide = False


    def is_dendrite(self,context):
        active_obj = context.active_object
        dend_filter = 'd[0-9]{3}$'
        if re.match(dend_filter,active_obj.name) != None:
            return (True)
        else:
            return (False)


    def is_axon(self,context):
        active_obj = context.active_object
        axon_filter = 'a[0-9]{3}$'
        if re.match(axon_filter,active_obj.name) != None:
            return (True)
        else:
            return (False)


    def output_pre_to_post(self,context,axon_obj,file):
        reg_list = axon_obj.mcell.regions.region_list
        sy_list = [reg.name for reg in reg_list if reg.name.rfind('sy') > -1]
        for sy in sy_list:
            dend_obj = self.get_dendrite(context,sy)
            file.write('%s %s %s\n' % (axon_obj.name, sy, dend_obj.name))


    def output_post_to_pre(self,context,dend_obj,file):
        reg_list = dend_obj.mcell.regions.region_list
        sy_list = [reg.name for reg in reg_list if reg.name.rfind('sy') > -1]
        for sy in sy_list:
            axon_obj = self.get_axon(context,sy)
            file.write('%s %s %s\n' % (dend_obj.name, sy, axon_obj.name))


    def draw_panel(self, context, panel):
        layout = panel.layout

        active_obj = context.active_object

        if (active_obj != None) and (active_obj.type == 'MESH'):
            sy_text = 'Synaptic Regions:'
            if self.is_dendrite(context):
               sy_text = 'Synaptic PSD Regions:'
            elif self.is_axon(context):
               sy_text = 'Synaptic Active Zone Regions:'
            row = layout.row()
            row.label(text=sy_text, icon='MESH_ICOSPHERE')
            row = layout.row()

# Layout active_object.mcell.regions.region_list with filter "*sy*" and active_psd_region_index
            row.template_list("CONNECTIVITY_UL_psd_draw_item","spine_psd_list",
                          active_obj.mcell.regions, "region_list",
                          self, "active_psd_region_index",
                          rows=2)

            row = layout.row()
            row.operator("connectivity_tool.output_pre_to_post", text="Output Pre to Post")
            row = layout.row()
            row.operator("connectivity_tool.output_post_to_pre", text="Output Post to Pre")

            psd_region_name = self.get_active_psd(context)
            if psd_region_name != None:
                row = layout.row()
                row.operator("connectivity_tool.show_synaptic_partner", text="Show Synaptic Partner")
