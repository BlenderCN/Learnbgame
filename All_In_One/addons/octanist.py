# ##### BEGIN GPL LICENSE BLOCK #####
#
#   Copyright (C) 2018 Landon Dou
#   itisltw@gmail.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENCE BLOCK #####

bl_info = {
    "name": "Octanist",
    "description": "A helper addon made for Octane render users",
    "author": "Landon Dou",
    "version": (2, 0, 0),
    "blender": (2, 79, 0),
    "category": "Object",
    "location": "View3D > Toolshelf > Octanist",
}

import bpy
from bpy.types import Panel, Operator
   
'''Functions That Handle Custom Properties'''    
def update_hdr_rot_x(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[0].default_value[0] = self.rot_x
    
def update_hdr_rot_y(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[0].default_value[1] = self.rot_y

def update_hdr_rot_z(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[0].default_value[2] = self.rot_z
    
def update_hdr_sca_x(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[1].default_value[0] = self.sca_x
    
def update_hdr_sca_y(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[1].default_value[1] = self.sca_y

def update_hdr_sca_z(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[1].default_value[2] = self.sca_z

def update_hdr_tra_x(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[2].default_value[0] = self.tra_x
    
def update_hdr_tra_y(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[2].default_value[1] = self.tra_y

def update_hdr_tra_z(self, context):
    self.node_tree.nodes["Octane 3D Transform"].inputs[2].default_value[2] = self.tra_z
    
def update_vis_env_color(self, context):
    self.node_tree.nodes["Octane RGBSpectrum Tex"].inputs[0].default_value = self.vis_env_color
    
'''Custom Properties Declaration'''  
#Rotation of HDR Texture Environment
bpy.types.Texture.rot_x = bpy.props.FloatProperty(
        name='Rotation X', 
        default=0, 
        min=-180.0, 
        max=180.0, 
        step=100, 
        precision=1,
        update=update_hdr_rot_x)
bpy.types.Texture.rot_y = bpy.props.FloatProperty(
        name='Rotation Y', 
        default=0,
        min=-180.0, 
        max=180.0, 
        step=100, 
        precision=1,
        update=update_hdr_rot_y)
bpy.types.Texture.rot_z = bpy.props.FloatProperty(
        name='Rotation Z', 
        default=0,
        min=-180.0, 
        max=180.0, 
        step=100, 
        precision=1,
        update=update_hdr_rot_z)
        
#Scale of HDR Texture Environment  
bpy.types.Texture.sca_x = bpy.props.FloatProperty(
        name='Scale X', 
        default=1.0, 
        step=10, 
        precision=2,
        update=update_hdr_sca_x)
bpy.types.Texture.sca_y = bpy.props.FloatProperty(
        name='Scale Y', 
        default=1.0,
        step=10, 
        precision=2,
        update=update_hdr_sca_y)
bpy.types.Texture.sca_z = bpy.props.FloatProperty(
        name='Scale Z', 
        default=1.0,
        step=10, 
        precision=2,
        update=update_hdr_sca_z)

#Translation of HDR Texture Environment        
bpy.types.Texture.tra_x = bpy.props.FloatProperty(
        name='Translation X', 
        default=0, 
        step=10, 
        precision=1,
        update=update_hdr_tra_x)
bpy.types.Texture.tra_y = bpy.props.FloatProperty(
        name='Translation Y', 
        default=0,
        step=10, 
        precision=1,
        update=update_hdr_tra_y)
bpy.types.Texture.tra_z = bpy.props.FloatProperty(
        name='Translation Z', 
        default=0,
        step=10, 
        precision=1,
        update=update_hdr_tra_z)
        
#Color of Solid Color Visible Environment
bpy.types.Texture.vis_env_color = bpy.props.FloatVectorProperty(
        name='Visible Environment Color',
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype='COLOR',
        update=update_vis_env_color)

'''Helper Functions'''
def link_nodes(mat, node1, n_out, node2, n_in):
    links = mat.node_tree.links
    #link index n_out on outputs of node1 to index n_in on inputs of node2
    links.new(node1.outputs[n_out], node2.inputs[n_in])

def create_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    return mat

def create_world_texture(name):
    tex = bpy.data.textures.new(name, type='IMAGE')
    tex.use_nodes = True
    nodes = tex.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    bpy.context.scene.world.active_texture = tex
    return tex

def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def add_node(mat, mattype, position):
    nodes = mat.node_tree.nodes
    new_node = nodes.new(type=mattype)
    new_node.location = position
    return new_node

'''ENVIRONMENT PANEL START'''
class OCTANIST_BTN_Setup_Texture_Environment(Operator):
    bl_idname = 'octanist.setup_tex_env'
    bl_label = 'Texture Environment'
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob = bpy.props.StringProperty(default="*.hdr;*.png;*.jpeg;*.jpg;*.exr", options={'HIDDEN'})
    
    def execute(self, context):
         if self.filepath != '':
             print('SELECTED : '+self.filepath)
             #CREATE WORLD TEXTURE
             tex = create_world_texture('OCEnv')
             #CREATE NODES
             node_image = add_node(tex, 'ShaderNodeOctImageTex', [-300,0])
             node_sph_projection = add_node(tex, 'ShaderNodeOctSphericalProjection', [-600,0])
             node_ro_transform = add_node(tex, 'ShaderNodeOct3DTransform', [-900,0])
             node_output = add_node(tex, 'TextureNodeOutput', [0,0])
             #MODIFY NODES PROPERTIES
             tex.use_fake_user = True
             node_image.image = bpy.data.images.load(self.filepath)
             node_image.image.use_fake_user = True
             node_image.inputs[0].default_value = 1.0
             #LINK NODES
             link_nodes(tex, node_ro_transform, 0, node_sph_projection, 0)
             link_nodes(tex, node_sph_projection, 0, node_image, 4)
             link_nodes(tex, node_image, 0, node_output, 0)
             #SET TEXTURE AS ENVIRONMENT TEXTURE
             bpy.context.scene.world.octane.env_type = '0'
             bpy.context.scene.world.octane.env_texture = tex.name
         return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OCTANIST_BTN_Setup_Visible_Texture_Environment(Operator):
    bl_idname = 'octanist.setup_tex_vis_env'
    bl_label = 'Texture Environment'
    
    def execute(self, context):
        #CREATE WORLD TEXTURE
        tex = create_world_texture('OCVisEnv')
        #CREATE NODES
        node_rgba = add_node(tex, 'ShaderNodeOctRGBSpectrumTex', [-300,0])
        node_output = add_node(tex, 'TextureNodeOutput', [0,0])
        #MODIFY NODES PROPERTIES
        tex.use_fake_user = True
        node_rgba.inputs[0].default_value = (1,1,1,1)
        #LINK NODES
        link_nodes(tex, node_rgba, 0, node_output, 0)
        #SET TEXTURE AS ENVIRONMENT TEXTURE
        bpy.context.scene.world.octane.use_vis_env = True
        bpy.context.scene.world.octane.env_vis_type = '0'
        bpy.context.scene.world.octane.env_vis_backplate = True
        bpy.context.scene.world.octane.env_vis_texture = tex.name
        return {'FINISHED'}

class OCTANIST_BTN_Reset_Texture_Environment(Operator):
    bl_idname = 'octanist.reset_tex_env'
    bl_label = 'Reset Texture Environment'

    def execute(self, context):
        env_tex_name = context.scene.world.octane.env_texture
        if env_tex_name:
            env_tex = bpy.data.textures[env_tex_name]
            env_tex.rot_x=0
            env_tex.rot_y=0
            env_tex.rot_z=0
            env_tex.sca_x=1
            env_tex.sca_y=1
            env_tex.sca_z=1
            env_tex.tra_x=0
            env_tex.tra_y=0
            env_tex.tra_z=0
            context.scene.world.octane.env_power = 1
        return {'FINISHED'}
    
class OCTANIST_BTN_Remove_Texture_Environment(Operator):
    bl_idname = 'octanist.remove_tex_env'
    bl_label = 'Remove Texture Environment'
    
    def execute(self, context):
        env_tex_name = context.scene.world.octane.env_texture
        if env_tex_name:
            context.scene.world.octane.env_texture = ""
            bpy.data.textures.remove(bpy.data.textures[env_tex_name])
            context.scene.world.octane.env_type = '1'
            context.scene.world.octane.env_power = 1
        return {'FINISHED'}
    
class OCTANIST_BTN_Reset_Texture_Visible_Environment(Operator):
    bl_idname = 'octanist.reset_tex_vis_env'
    bl_label = 'Reset Visible Texture Environment'
    
    def execute(self, context):
        vis_env_tex_name = context.scene.world.octane.env_vis_texture
        if vis_env_tex_name:
            vis_env_tex = bpy.data.textures[vis_env_tex_name]
            vis_env_tex.vis_env_color=(1,1,1,1)
            context.scene.world.octane.env_vis_power = 1
        return {'FINISHED'}
    
class OCTANIST_BTN_Remove_Texture_Visible_Environment(Operator):
    bl_idname = 'octanist.remove_tex_vis_env'
    bl_label = 'Remove Visible Texture Environment'
    
    def execute(self, context):
        vis_env_tex_name = context.scene.world.octane.env_vis_texture
        if vis_env_tex_name:
            context.scene.world.octane.env_vis_texture = ""
            bpy.data.textures.remove(bpy.data.textures[vis_env_tex_name])
            context.scene.world.octane.use_vis_env = False
            context.scene.world.octane.env_vis_type = '1'
            context.scene.world.octane.env_vis_power = 1
        return {'FINISHED'}

class OCTANIST_BTN_Add_Point_Light(Operator):
    bl_idname = 'octanist.add_pointlight'
    bl_label = 'Add A Point Light'
    
    rgb_emission_color = bpy.props.FloatVectorProperty(
        name='Color',
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    emission_power = bpy.props.FloatProperty(
        name='Power', 
        default=100, 
        min=0.0001,
        step=10, 
        precision=4)
    emission_surface_brightness = bpy.props.BoolProperty(
        name="Surface Brightness",
        default=False)
    
    def execute(self, context):
        #CREATE MATERIAL
        mat = create_material('OCEmission')
        #CREATE NODES
        node_diffuse = add_node(mat, 'ShaderNodeOctDiffuseMat', [-200,0])
        node_bb_emission = add_node(mat, 'ShaderNodeOctBlackBodyEmission', [-400,0])
        node_rgb_tex = add_node(mat, 'ShaderNodeOctRGBSpectrumTex', [-600,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #MODIFY NODES PROPERTIES | CALL PROPS DIALOG
        node_rgb_tex.inputs[0].default_value = self.rgb_emission_color
        node_bb_emission.inputs[1].default_value = self.emission_power
        node_bb_emission.inputs[2].default_value = self.emission_surface_brightness
        #LINK NODES
        link_nodes(mat, node_rgb_tex, 0, node_bb_emission, 0)
        link_nodes(mat, node_bb_emission, 0, node_diffuse, 6)
        link_nodes(mat, node_diffuse, 0, node_output, 0)
        #ASSIGN NODES
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.5)
        ob = bpy.context.active_object
        assign_material(ob, mat)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OCTANIST_BTN_Add_Default_Cam(Operator):
    bl_idname = 'octanist.add_def_cam'
    bl_label = 'Add A Default Camera'
    

    camera_imager = bpy.props.BoolProperty(name="Octane Camera Imager")
    
    def execute(self, context):
        bpy.ops.object.camera_add(view_align=True, rotation=(3.1415927410125732/2,0,0))
        
        context.scene.octane.hdr_tonemap_render_enable = self.camera_imager
        
        if self.camera_imager:
            context.scene.display_settings.display_device = 'None'
        else:
            context.scene.display_settings.display_device = 'sRGB'
        
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label('[Render Mode Only]')
        col.prop(self, 'camera_imager')
        col = layout.column()
        col.label('With Imager enabled, Display device will be set to None')
        col.label('instead of sRGB to get correct response')
    
    def invoke(self, context, event):
        self.camera_imager = context.scene.octane.hdr_tonemap_render_enable

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
class OCTANIST_BTN_Add_360_Cam(Operator):
    bl_idname = 'octanist.add_360_cam'
    bl_label = 'Add A 360 Degree Camera'
    
    res_x = bpy.props.IntProperty(
        name='Width(X)',
        min=4,
        step=1)
            
    res_y = bpy.props.IntProperty(
        name='Height(Y)',
        min=4,
        step=1)
            
    camera_imager = bpy.props.BoolProperty(
        name="Octane Camera Imager")
    
    def execute(self, context):
        context.scene.render.resolution_x = self.res_x
        context.scene.render.resolution_y = self.res_y
        
        bpy.ops.object.camera_add(view_align=True, rotation=(3.1415927410125732/2,0,0))
        cam = context.active_object
        cam.data.lens_unit = 'FOV'
        cam.data.angle = 1.5708
        cam.data.type = 'PANO'
        cam.data.cycles.panorama_type = 'EQUIRECTANGULAR'
        
        context.scene.octane.hdr_tonemap_render_enable = self.camera_imager
        
        if self.camera_imager:
            context.scene.display_settings.display_device = 'None'
        else:
            context.scene.display_settings.display_device = 'sRGB'
            
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label('[Render Mode Only]')
        col=layout.column(align=True)
        col.prop(self, 'res_x')
        col.prop(self, 'res_y')
        col = layout.column()
        col.label('360 Degree Camera requires 2:1 resolution ratio')
        col = layout.column()
        col.prop(self, 'camera_imager')
        col = layout.column()
        col.label('With Imager enabled, Display device will be set to None')
        col.label('instead of sRGB to get correct response')
        
    def invoke(self, context, event):
        self.res_x = context.scene.render.resolution_x
        self.res_y = context.scene.render.resolution_y
        self.camera_imager = context.scene.octane.hdr_tonemap_render_enable

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class OCTANIST_PANEL_Environment(Panel):
    bl_label = 'Octane Environment'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Octanist'
    bl_context = 'objectmode'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if scene.render.engine == 'octane':
            #Button | Scene
            col = layout.column(align=True)
            col.label('Octane Kernel')
            col.prop(scene.octane, 'kernel_type', text='')
            col = layout.column(align=True)
            col.label('Display Device')
            col.prop(scene.display_settings, 'display_device', text='')
            
            #Button | Setup Texture Environment & Reset Texture Environment
            layout.label('Environment')
            col = layout.column(align=True)
            col.operator('octanist.setup_tex_env', text='Texture Environment', icon='IMAGE_COL')
            env_tex_name = bpy.context.scene.world.octane.env_texture
            if env_tex_name:
                env_tex = bpy.data.textures[env_tex_name]
                col.prop(scene.world.octane, 'env_power')
                col.prop(env_tex, 'rot_x')
                col.prop(env_tex, 'rot_y')
                col.prop(env_tex, 'rot_z')
                col.prop(env_tex, 'sca_x')
                col.prop(env_tex, 'sca_y')
                col.prop(env_tex, 'sca_z')
                col.prop(env_tex, 'tra_x')
                col.prop(env_tex, 'tra_y')
                col.prop(env_tex, 'tra_z')
                row = col.row(align=True)
                row.operator('octanist.reset_tex_env', text='Reset', icon='FILE_REFRESH')
                row.operator('octanist.remove_tex_env', text='Remove', icon='PANEL_CLOSE')
            
            #Button | Setup Solid Color Visible Environment 
            col = layout.column(align=True)
            col.operator('octanist.setup_tex_vis_env', text='Solid Color VisEnvironment', icon='COLOR')
            vis_env_tex_name = scene.world.octane.env_vis_texture
            if scene.world.octane.use_vis_env == True:
                if vis_env_tex_name:
                    vis_env_tex = bpy.data.textures[vis_env_tex_name]
                    col.prop(vis_env_tex,'vis_env_color','')
                    col.prop(scene.world.octane, 'env_vis_power')
                    row = col.row(align=True)
                    row.operator('octanist.reset_tex_vis_env', text='Reset', icon='FILE_REFRESH')
                    row.operator('octanist.remove_tex_vis_env', text='Remove', icon='PANEL_CLOSE')
                    
            #Button | Lights
            layout.label('Lights')
            row = layout.row(align=True)
            row.operator('octanist.add_pointlight', text='Point Light', icon='LAMP_POINT')
            
            #Button | Cameras
            layout.label('Cameras')
            col = layout.column(align=True)
            col.operator('octanist.add_def_cam', text='Default Camera', icon='CAMERA_DATA')
            col.operator('octanist.add_360_cam', text='360 Degree Camera', icon='FORCE_VORTEX')
        else:
            layout.label(text="Octane Render Only")

'''ENVIRONMENT PANEL END'''

'''MATERIALS PANEL START'''
class OCTANIST_BTN_Assign_DifShader(Operator):
    bl_idname = 'octanist.diffuse_mat'
    bl_label = 'Add Octane Diffuse Shader to Selected'

    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCDiffuse')
        #CREATE NODES
        node_diffuse = add_node(mat, 'ShaderNodeOctDiffuseMat', [-200,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #LINK NODES
        link_nodes(mat, node_diffuse, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}

class OCTANIST_BTN_Assign_GloShader(Operator):
    bl_idname = 'octanist.glossy_mat'
    bl_label = 'Add Octane Glossy Shader to Selected'

    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCGlossy')
        #CREATE NODES
        node_glossy = add_node(mat, 'ShaderNodeOctGlossyMat', [-200,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #LINK NODES
        link_nodes(mat, node_glossy, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}

class OCTANIST_BTN_Assign_MetShader(Operator):
    bl_idname = 'octanist.metal_mat'
    bl_label = 'Add Octane Metal Shader to Selected'

    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCMetal')
        #CREATE NODES
        node_metal = add_node(mat, 'ShaderNodeOctMetalMat', [-200,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #LINK NODES
        link_nodes(mat, node_metal, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}

class OCTANIST_BTN_Assign_SpeShader(Operator):
    bl_idname = 'octanist.specular_mat'
    bl_label = 'Add Octane Specular Shader to Selected'

    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCSpecular')
        #CREATE NODES
        node_spec = add_node(mat, 'ShaderNodeOctSpecularMat', [-200,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #LINK NODES
        link_nodes(mat, node_spec, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}

class OCTANIST_BTN_Assign_TooShader(Operator):
    bl_idname = 'octanist.toon_mat'
    bl_label = 'Add Octane Toon Shader to Selected'

    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCToon')
        #CREATE NODES
        node_toon = add_node(mat, 'ShaderNodeOctToonMat', [-200,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #LINK NODES
        link_nodes(mat, node_toon, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}
    
class OCTANIST_BTN_Assign_RGBEmissionMat(Operator):
    bl_idname = 'octanist.rgb_emission_fmat'
    bl_label = 'Add RGB Emission Material to Selected'
    
    rgb_emission_color = bpy.props.FloatVectorProperty(
        name='Color',
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    emission_power = bpy.props.FloatProperty(
        name='Power', 
        default=100, 
        min=0.0001,
        step=10, 
        precision=4)
    emission_surface_brightness = bpy.props.BoolProperty(
        name="Surface Brightness",
        default=False)
    
    def execute(self,context):
        #CREATE MATERIAL
        mat = create_material('OCEmission')
        #CREATE NODES
        node_diffuse = add_node(mat, 'ShaderNodeOctDiffuseMat', [-200,0])
        node_bb_emission = add_node(mat, 'ShaderNodeOctBlackBodyEmission', [-400,0])
        node_rgb_tex = add_node(mat, 'ShaderNodeOctRGBSpectrumTex', [-600,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #MODIFY NODES PROPERTIES | CALL PROPS DIALOG
        node_rgb_tex.inputs[0].default_value = self.rgb_emission_color
        node_bb_emission.inputs[1].default_value = self.emission_power
        node_bb_emission.inputs[2].default_value = self.emission_surface_brightness
        #LINK NODES
        link_nodes(mat, node_rgb_tex, 0, node_bb_emission, 0)
        link_nodes(mat, node_bb_emission, 0, node_diffuse, 6)
        link_nodes(mat, node_diffuse, 0, node_output, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
class OCTANIST_BTN_Assign_FIREMat(Operator):
    bl_idname = 'octanist.fire_fmat'
    bl_label = 'Add Fire Material to Selected'
    
    emission_power = bpy.props.FloatProperty(
        name='Emission Power', 
        default=0.01, 
        min=0.0001,
        step=1, 
        precision=4)
    emission_color = bpy.props.FloatVectorProperty(
        name='Emission Color',
        size=4,
        default = (0.8, 0.3, 0, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    outer_cone_color = bpy.props.FloatVectorProperty(
        name='Outer Cone',
        size=4,
        default = (0.7, 0.08, 0, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    intermediate_cone_color = bpy.props.FloatVectorProperty(
        name='Intermediate Cone',
        size=4,
        default = (0.85, 0.8, 0.15, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    inner_cone_color = bpy.props.FloatVectorProperty(
        name='Inner Cone',
        size=4,
        default = (1, 1, 1, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
    smoke_color = bpy.props.FloatVectorProperty(
        name='Smoke Absorbtion',
        size=4,
        default = (0.02, 0.05, 0.2, 1),
        min = 0,
        max = 1,
        subtype='COLOR')
        
    def execute(self,context): 
        #CREATE MATERIAL
        mat = create_material('OCFire')
        #CREATE NODES
        node_volume_med = add_node(mat, 'ShaderNodeOctVolumeMedium', [-200,0])
        node_smoke_ramp = add_node(mat, 'ShaderNodeOctVolumeRampTex', [-400,0])
        node_fire_ramp = add_node(mat, 'ShaderNodeOctVolumeRampTex', [-400,-250])
        node_tex_emission = add_node(mat, 'ShaderNodeOctTextureEmission', [-600,0])
        node_emission_color = add_node(mat, 'ShaderNodeOctRGBSpectrumTex', [-800,0])
        node_output = add_node(mat, 'ShaderNodeOutputMaterial', [0,0])
        #MODIFY NODES PROPERTIES | CALL PROPS DIALOG
        node_volume_med.inputs[0].default_value = 70
        node_volume_med.inputs[1].default_value = 0.1
        node_volume_med.inputs[2].default_value = 0.1
        node_volume_med.inputs[5].default_value = 0.1
        node_volume_med.inputs[7].default_value = 0.6
        node_tex_emission.inputs[1].default_value = self.emission_power
        node_tex_emission.inputs[4].default_value = 1000
        node_emission_color.inputs[0].default_value = self.emission_color
        node_smoke_ramp.inputs[0].default_value = 1
        node_smoke_ramp.color_ramp.elements.new(0)
        node_smoke_ramp.color_ramp.elements[0].color=(0,0,0,1)
        node_smoke_ramp.color_ramp.elements[1].color=self.smoke_color
        node_smoke_ramp.color_ramp.elements[2].color=(1,1,1,1)
        node_smoke_ramp.color_ramp.elements[0].position=0
        node_smoke_ramp.color_ramp.elements[1].position=0.2
        node_smoke_ramp.color_ramp.elements[2].position=1
        node_fire_ramp.inputs[0].default_value = 1
        node_fire_ramp.color_ramp.elements.new(0)
        node_fire_ramp.color_ramp.elements[0].color=self.outer_cone_color
        node_fire_ramp.color_ramp.elements[1].color=self.intermediate_cone_color
        node_fire_ramp.color_ramp.elements[2].color=self.inner_cone_color
        node_fire_ramp.color_ramp.elements[0].position=0.35
        node_fire_ramp.color_ramp.elements[1].position=0.7
        node_fire_ramp.color_ramp.elements[2].position=1
        #LINK NODES
        link_nodes(mat, node_volume_med, 0, node_output, 1)
        link_nodes(mat, node_smoke_ramp, 0, node_volume_med, 3)
        link_nodes(mat, node_fire_ramp, 0, node_volume_med, 9)
        link_nodes(mat, node_tex_emission, 0, node_volume_med, 8)
        link_nodes(mat, node_emission_color, 0, node_tex_emission, 0)
        #ASSIGN NODES
        for ob in bpy.context.selected_objects:
            assign_material(ob, mat)
            
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
        
class OCTANIST_PANEL_Materials(Panel):
    bl_label = 'Octane Materials'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Octanist'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if scene.render.engine == 'octane':
            
            #Button | Basic Shaders
            layout.label('Basic Shaders')
            col = layout.column(align=True)
            col.operator('octanist.diffuse_mat', text='Diffuse Shader', icon='MATERIAL_DATA')
            col.operator('octanist.glossy_mat', text='Glossy Shader', icon='MATERIAL_DATA')
            col.operator('octanist.metal_mat', text='Metal Shader', icon='MATERIAL_DATA')
            col.operator('octanist.specular_mat', text='Specular Shader', icon='MATERIAL_DATA')
            col.operator('octanist.toon_mat', text='Toon Shader', icon='MATERIAL_DATA')
            
            #Button | Featured Materials
            layout.label('Featured Materials')
            col = layout.column(align=True)
            col.operator('octanist.rgb_emission_fmat', text='RGB Emission', icon='MATERIAL_DATA')
            col.operator('octanist.fire_fmat', text='Fire Material [Domain]', icon='MATERIAL_DATA')
            #col.operator('octanist.pbr_fmat', text='Metallic PBR Material', icon='MATERIAL_DATA')
        
        else:
            layout.label(text="Octane Render Only")
        
'''MATERIALS PANEL END'''

'''MAIN'''
def register():
    bpy.utils.register_class(OCTANIST_PANEL_Materials)
    bpy.utils.register_class(OCTANIST_BTN_Assign_DifShader)
    bpy.utils.register_class(OCTANIST_BTN_Assign_GloShader)
    bpy.utils.register_class(OCTANIST_BTN_Assign_MetShader)
    bpy.utils.register_class(OCTANIST_BTN_Assign_SpeShader)
    bpy.utils.register_class(OCTANIST_BTN_Assign_TooShader)
    bpy.utils.register_class(OCTANIST_BTN_Assign_RGBEmissionMat)
    bpy.utils.register_class(OCTANIST_BTN_Assign_FIREMat)
    
    bpy.utils.register_class(OCTANIST_PANEL_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Setup_Texture_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Reset_Texture_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Remove_Texture_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Setup_Visible_Texture_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Reset_Texture_Visible_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Remove_Texture_Visible_Environment)
    bpy.utils.register_class(OCTANIST_BTN_Add_Point_Light)
    bpy.utils.register_class(OCTANIST_BTN_Add_Default_Cam)
    bpy.utils.register_class(OCTANIST_BTN_Add_360_Cam)
    
def unregister():
    bpy.utils.unregister_class(OCTANIST_PANEL_Materials)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_DifShader)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_GloShader)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_MetShader)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_SpeShader)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_TooShader)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_RGBEmissionMat)
    bpy.utils.unregister_class(OCTANIST_BTN_Assign_FIREMat)
    
    bpy.utils.unregister_class(OCTANIST_PANEL_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Setup_Texture_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Reset_Texture_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Remove_Texture_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Setup_Visible_Texture_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Reset_Texture_Visible_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Remove_Texture_Visible_Environment)
    bpy.utils.unregister_class(OCTANIST_BTN_Add_Point_Light)
    bpy.utils.unregister_class(OCTANIST_BTN_Add_Default_Cam)
    bpy.utils.unregister_class(OCTANIST_BTN_Add_360_Cam)
    
if __name__ == "__main__":
    register()