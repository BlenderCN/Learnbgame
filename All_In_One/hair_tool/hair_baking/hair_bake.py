# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
from hair_tool.helper_functions import assign_material
from os import path
from random import randint

# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb
def assign_curve_id(curve ):
    '''Add material to curve. If clear_material is True - reomve all slots exept first.'''
    curve.data.materials.clear()
    for i in range(6):  #make sure first slot is assigned
        material_name = 'ID_CURVE_0'+ str(i)
        if material_name in  bpy.data.materials.keys():
            curve.data.materials.append(bpy.data.materials[material_name])
    for polyline in curve.data.splines:  # for strand point
        polyline.material_index =  randint(0,5)


def setup_pass(pass_name):
    background = None
    if 'Background' in bpy.data.objects.keys():
        background = bpy.data.objects['Background']
    render_objs = [obj for obj in bpy.data.objects if obj.type in {"MESH","CURVE"}]
    for obj in render_objs:
        if obj.type == 'CURVE' and pass_name in {'TANGENT','ROOT','ID','OPACITY','DIFFUSE'}:
            obj.data.use_uv_as_generated = True
            if pass_name == 'ID': #different workflow - randomly assign 6 materials
                assign_curve_id(obj)
            else:
                assign_material(obj, pass_name +"_CURVE")
        else:
            assign_material(obj, pass_name)
    background.hide_render = background.hide_viewport = True if pass_name in {
        'DIFFUSE', 'ID'} and background is not None else False  # hide background for these passes
    if pass_name == 'TANGENT' and background is not None:
        assign_material(background,'FLAT_TANGENT')


def compose_channels(context,bake_pass_list):
    bake_settings = context.scene.hair_bake_settings
    suffix = 'png' if bake_settings.output_format == 'PNG' else 'tga'
    if 'ChannelMixing' not in  bpy.data.node_groups.keys():
        bpy.ops.node.new_node_tree(type='TextureChannelMixing', name='ChannelMixing')
    node_tree = bpy.data.node_groups['ChannelMixing']
    for i,pass_name in enumerate(bake_pass_list):
        img_pass_name =  bake_settings.hair_bake_file_name + '_' + pass_name  + "." + suffix
        impPath = bpy.path.abspath(bake_settings.hair_bake_path + img_pass_name )
        if path.isfile(impPath): 
            if img_pass_name in bpy.data.images.keys():
                bpy.data.images[img_pass_name].reload()
            else:
                img = bpy.data.images.load(filepath=impPath)
            img_node = None
            for node in node_tree.nodes:
                if node.bl_idname == 'InputTexture' and  node.img == img_pass_name:
                    img_node = node
            if img_node is None:
                img_node = node_tree.nodes.new('InputTexture')
            img_node.img = img_pass_name # also refreshes img... 
            img_node.location[1] = i * 200
            img_node.width = 220

            # bpy.data.images.remove(img)
    # outputImg.filepath_raw = bpy.path.abspath(bake_settings.hair_bake_path + "Hair_compo." + suffix)


class HT_OT_BakeHair(bpy.types.Operator):
    bl_idname = "object.bake_hair"
    bl_label = "Bake Hair"
    bl_description = "Bake Hair"
    bl_options = {"REGISTER", "UNDO"}

    @staticmethod
    def unify_render_preview_settings ( context):
        for obj in bpy.context.scene.objects:
            obj.hide_render = obj.hide_viewport
        particle_objs = [obj for obj in bpy.data.objects if obj.type=='MESH' and len(obj.particle_systems)]
        for particle_obj in particle_objs:
            for particle_system in particle_obj.particle_systems:
                particle_system.settings.rendered_child_count =  particle_system.settings.child_nbr
                # particle_system.settings.display_step = 3

    def execute(self, context):
        bake_settings = context.scene.hair_bake_settings
        addon_prefs = bpy.context.preferences.addons['hair_tool'].preferences
        bpy.context.scene.render.image_settings.file_format = bake_settings.output_format
        # if save_path:
        #     bpy.ops.wm.save_as_mainfile(filepath=save_path)
        render_path = bake_settings.hair_bake_path
        render_file_name = bake_settings.hair_bake_file_name
        render_quality = bake_settings.render_quality
        render_size = int(bake_settings.bakeResolution)
        bpy.context.scene.render.resolution_x = render_size
        bpy.context.scene.render.resolution_y = render_size
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.image_settings.file_format = bake_settings.output_format

        self.unify_render_preview_settings(context)

        if len(render_path)>0:
            passes = list(bake_settings.render_passes)
            for pass_name in passes:
                setup_pass(pass_name)
                render = context.scene.render
                render.use_file_extension = True
                if pass_name=="AO":
                    bpy.context.scene.cycles.samples = 128*int(render_quality)
                else:
                    bpy.context.scene.cycles.samples = 16*int(render_quality)
                render.filepath = render_path + render_file_name + "_" + pass_name
                bpy.ops.render.render(write_still=True) #we cant acess render reuslt
            if bake_settings.hair_bake_composite:
                compose_channels(context, passes)
        return {"FINISHED"}


class HT_OT_OpenHairFile(bpy.types.Operator):
    bl_idname = "object.open_hair_bake"
    bl_label = "Open Baking scene"
    bl_description = "Open Baking scene"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        bpy.ops.wm.open_mainfile(filepath=path.dirname(__file__)+"\hair_bake.blend")
        return {"FINISHED"}
