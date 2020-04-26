# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
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

import bpy

from subprocess import Popen
from os import system, path, makedirs, sep

def ds_sp_get_export_path():

    _export_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_export_folder + sep

    if not path.exists(_export_path):
        makedirs(_export_path)

    return _export_path

def ds_sp_get_textures_path():

    _textures_path = bpy.path.abspath('//') + bpy.context.preferences.addons[__package__].preferences.option_textures_folder + sep

    if not path.exists(_textures_path):
        makedirs(_textures_path)

    return _textures_path

def ds_sp_get_object_name():
       
    return bpy.context.active_object.name

def ds_sp_get_file_name():
       
    return bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')

def ds_sp_get_texture_file(texture_path,mesh_name,mat_name,texture_name,texture_ext):

    if path.exists(texture_path+mesh_name+'_'+mat_name+'_'+texture_name+'.'+texture_ext):
        if bpy.context.preferences.addons[__package__].preferences.option_relative:
            texture_path=bpy.path.relpath(texture_path)+sep
        return texture_path+mesh_name+'_'+mat_name+'_'+texture_name+'.'+texture_ext
    elif path.exists(texture_path+mat_name+'_'+texture_name+'.'+texture_ext):
        if bpy.context.preferences.addons[__package__].preferences.option_relative:
            texture_path=bpy.path.relpath(texture_path)+sep
        return texture_path+mat_name+'_'+texture_name+'.'+texture_ext
    else:
        return ""

class ds_sp_pbr_nodes(bpy.types.Operator):

    bl_idname = "ds_sp.pbr_nodes"
    bl_label = "Import Textures"
    bl_context = "material"
    bl_description = "Import from Substance Painter"

    import_setting : bpy.props.StringProperty(
        name="import_setting",
        default = 'scene'
    )

    def execute(self, context):

        if self.import_setting == 'scene':

            _objects = bpy.context.scene.objects

        elif bpy.context.active_object:

            _objects = {bpy.context.active_object}
        
        _textures_path = ds_sp_get_textures_path()
           
        _texture_ext=bpy.context.preferences.addons[__package__].preferences.option_import_ext

        for _obj in _objects:

            if _obj.type=='MESH':

                _obj_name = _obj.name

                _materials = _obj.data.materials

                for _material in _materials:

                    _material_name = _material.name            
                    
                    _file_Base_Color = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Base_Color',_texture_ext)
                    _file_Diffuse = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Diffuse',_texture_ext)
                    _file_Ambient_occlusion = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Ambient_occlusion',_texture_ext)
                    _file_Metallic = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Metallic',_texture_ext)
                    _file_Specular = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Specular',_texture_ext)
                    _file_Glossiness = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Glossiness',_texture_ext)
                    _file_Roughness = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Roughness',_texture_ext)

                    _file_Normal = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Normal_OpenGL',_texture_ext)

                    if _file_Normal=="":
                        _file_Normal = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Normal',_texture_ext)

                    _file_Emissive = ds_sp_get_texture_file(_textures_path,_obj_name,_material_name,'Emissive',_texture_ext)

                    if _file_Base_Color or _file_Diffuse:
                        
                        if _material:
                            
                            _material.use_nodes = True

                        # Clear Nodes

                        if _material and _material.node_tree:

                            _nodes = _material.node_tree.nodes

                            for node in _nodes:
                                _nodes.remove(node)

                        _material_links = _material.node_tree.links
                        
                        _nodes = _material.node_tree.nodes

                        # Output Material

                        _material_output = _nodes.new('ShaderNodeOutputMaterial')

                        if not _file_Emissive:
                            _material_output.location = 600,0
                        else:
                            _material_output.location = 1200,0

                        _material_output.name='ds_pbr_output'

                        if _file_Emissive:

                            # Add Shader

                            _node_add_shader=_nodes.new('ShaderNodeAddShader')
                            _node_add_shader.location = 1000,0
                            _node_add_shader.name = 'ds_pbr_add_shader'
                            _material_links.new(_node_add_shader.outputs['Shader'], _material_output.inputs['Surface'])
                            
                            # Shader Emission
                            
                            _node_emission=_nodes.new('ShaderNodeEmission')
                            _node_emission.location = 800,-100
                            _node_emission.name = 'ds_pbr_emission'
                            _material_links.new(_node_emission.outputs['Emission'], _node_add_shader.inputs[1])

                            # Emissive
                            
                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 600,-100
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_emissive'
                            _material_links.new(node.outputs['Color'], _node_emission.inputs['Color'])
                            node.image = bpy.data.images.load(_file_Emissive)

                        # Shader

                        node_shader = _nodes.new('ShaderNodeBsdfPrincipled')
                        node_shader.location = 400,0
                        node_shader.name='ds_pbr_shader'

                        if not _file_Emissive:
                            _material_links.new(node_shader.outputs['BSDF'], _material_output.inputs['Surface'])
                        else:
                            _material_links.new(node_shader.outputs['BSDF'], _node_add_shader.inputs[0])

                        if _file_Ambient_occlusion:

                            # Mix RGB

                            node_mix=_nodes.new('ShaderNodeMixRGB')
                            node_mix.location = 200,100
                            node_mix.blend_type = 'MULTIPLY'
                            node_mix.name='ds_pbr_mix_rgb'
                            _material_links.new(node_mix.outputs['Color'], node_shader.inputs['Base Color'])

                            # Base Color

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,250
                            node.name='ds_pbr_texture_base_color'
                            _material_links.new(node.outputs['Color'], node_mix.inputs['Color1'])
                            
                            if _file_Base_Color:
                                node.image = bpy.data.images.load(_file_Base_Color)
                            elif _file_Diffuse:
                                node.image = bpy.data.images.load(_file_Diffuse)

                            # Ambient Occlusion
                            
                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,0
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_ao'
                            _material_links.new(node.outputs['Color'], node_mix.inputs['Color2'])
                            node.image = bpy.data.images.load(_file_Ambient_occlusion)
                        
                        else:

                            # Base Color

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,250
                            node.name='ds_pbr_texture_base_color'
                            _material_links.new(node.outputs['Color'], node_shader.inputs['Base Color'])

                            if _file_Base_Color:
                                node.image = bpy.data.images.load(_file_Base_Color)
                            elif _file_Diffuse:
                                node.image = bpy.data.images.load(_file_Diffuse)

                        # Metallic

                        if _file_Metallic:

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,-250
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_metallic'
                            _material_links.new(node.outputs['Color'], node_shader.inputs['Metallic'])   
                            node.image = bpy.data.images.load(_file_Metallic)

                        # Specular

                        if _file_Specular:

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,-250
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_Specular'
                            _material_links.new(node.outputs['Color'], node_shader.inputs['Specular'])   
                            node.image = bpy.data.images.load(_file_Specular)

                        if _file_Glossiness:

                            # Roughness Invert

                            node_invert=_nodes.new('ShaderNodeInvert')
                            node_invert.location = 200,-450
                            node_invert.name='ds_pbr_invert'
                            _material_links.new(node_invert.outputs['Color'], node_shader.inputs['Roughness'])
                            
                            # Roughness

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,-500
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_roughness'
                            _material_links.new(node.outputs['Color'], node_invert.inputs['Color'])   
                            node.image = bpy.data.images.load(_file_Glossiness)

                        else:

                            # Roughness

                            node=_nodes.new('ShaderNodeTexImage')
                            node.location = 0,-500
                            node.color_space = 'NONE'
                            node.name='ds_pbr_texture_roughness'
                            _material_links.new(node.outputs['Color'], node_shader.inputs['Roughness'])   
                            node.image = bpy.data.images.load(_file_Roughness)

                        # Normal

                        node_map=_nodes.new('ShaderNodeNormalMap')
                        node_map.location = 200,-700
                        node_map.name='ds_pbr_normal_map'
                        _material_links.new(node_map.outputs['Normal'], node_shader.inputs['Normal'])
                        
                        node=_nodes.new('ShaderNodeTexImage')
                        node.location = 0,-750
                        node.color_space = 'NONE'
                        node.name='ds_pbr_texture_normal'
                        _material_links.new(node.outputs['Color'], node_map.inputs['Color'])
                        node.image = bpy.data.images.load(_file_Normal)

        return {'FINISHED'}

def ds_sp_fbx_export_sel(self, context):

    _export_name = ds_sp_get_object_name()
    _export_path = ds_sp_get_export_path()
    _export_file = _export_path + _export_name + '.fbx'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    bpy.ops.export_scene.fbx(filepath=_export_file, use_selection=True, check_existing=False, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
    
    return _export_file

class ds_sp_fbx_export_sel_execute(bpy.types.Operator):

    bl_idname = "ds_sp.fbx_export_sel"
    bl_label = "Export FBX."

    def execute(self, context):

        _export_file = ds_sp_fbx_export_sel(self, context)

        return {'FINISHED'}

def ds_sp_fbx_export_scene(self, context):

    _export_name = ds_sp_get_file_name()
    _export_path = ds_sp_get_export_path()
    _export_file = _export_path + _export_name + '.fbx'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()

    bpy.ops.export_scene.fbx(filepath=_export_file, use_selection=False, check_existing=False, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
    
    return _export_file

class ds_sp_fbx_export_scene_execute(bpy.types.Operator):

    bl_idname = "ds_sp.fbx_export_scene"
    bl_label = "Export FBX."

    def execute(self, context):

        _export_file = ds_sp_fbx_export_scene(self, context)

        return {'FINISHED'}

def ds_sp_obj_export_sel(self, context):

    _export_name = ds_sp_get_object_name()
    _export_path = ds_sp_get_export_path()
    _export_file = _export_path + _export_name + '.obj'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()
    
    bpy.ops.export_scene.obj(filepath=_export_file, check_existing=False, use_selection=True, axis_forward='-Z', axis_up='Y', global_scale=1.0, keep_vertex_order=True)

    return _export_file

class ds_sp_obj_export_sel_execute(bpy.types.Operator):

    bl_idname = "ds_sp.obj_export_sel"
    bl_label = "Export OBJ."

    def execute(self, context):

        _export_file = ds_sp_obj_export_sel(self, context)

        return {'FINISHED'}

def ds_sp_obj_export_scene(self, context):

    _export_name = ds_sp_get_file_name()
    _export_path = ds_sp_get_export_path()
    _export_file = _export_path + _export_name + '.obj'

    if not bpy.context.preferences.addons[__package__].preferences.option_save_before_export:
        bpy.ops.wm.save_mainfile()
    
    bpy.ops.export_scene.obj(filepath=_export_file, check_existing=False, use_selection=False, axis_forward='-Z', axis_up='Y', global_scale=1.0, keep_vertex_order=True)

    return _export_file

class ds_sp_obj_export_scene_execute(bpy.types.Operator):

    bl_idname = "ds_sp.obj_export_scene"
    bl_label = "Export OBJ."

    def execute(self, context):

        _export_file = ds_sp_obj_export_scene(self, context)

        return {'FINISHED'}

class ds_sp_export_sel(bpy.types.Operator):

    bl_idname = "ds_sp.export_sel" 
    bl_label = "Substance Painter (Selected)"
    bl_description = "Export to Substance Painter (Selected)"

    def execute(self, context):

        _object_name = ds_sp_get_object_name()
        _export_path = bpy.path.abspath('//')
        _export_project = _export_path + _object_name + '.spp'
        _textures_path = ds_sp_get_textures_path()

        if bpy.context.preferences.addons[__package__].preferences.option_export_type=='obj':
            _export_file = ds_sp_obj_export_sel(self, context)
        elif bpy.context.preferences.addons[__package__].preferences.option_export_type=='fbx':
            _export_file = ds_sp_fbx_export_sel(self, context)

        if bpy.context.preferences.addons[__package__].preferences.option_no_new:

            if not path.exists(_export_project):
                Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path])
            else:
                Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path, _export_project])

        else:

            Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path, _export_project])

        return {'FINISHED'}

class ds_sp_export_scene(bpy.types.Operator):

    bl_idname = "ds_sp.export_scene" 
    bl_label = "Substance Painter (Scene)"
    bl_description = "Export to Substance Painter (Scene)"

    def execute(self, context):

        _export_name = ds_sp_get_file_name()
        _export_path = bpy.path.abspath('//')
        _export_project = _export_path + _export_name + '.spp'
        _textures_path = ds_sp_get_textures_path()

        if bpy.context.preferences.addons[__package__].preferences.option_export_type=='obj':
            _export_file = ds_sp_obj_export_scene(self, context)
        elif bpy.context.preferences.addons[__package__].preferences.option_export_type=='fbx':
            _export_file = ds_sp_fbx_export_scene(self, context)

        if bpy.context.preferences.addons[__package__].preferences.option_no_new:

            if not path.exists(_export_project):
                Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path])
            else:
                Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path, _export_project])

        else:
            
            Popen([bpy.context.preferences.addons[__package__].preferences.option_sp_exe, "--disable-version-checking", "--mesh", _export_file, "--export-path", _textures_path, _export_project])

        return {'FINISHED'}

class ds_sp_toggle(bpy.types.Operator):

    bl_idname = "ds_sp.toggle"
    bl_label = "SP"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    def execute(self, context):

        if not bpy.context.preferences.addons[__package__].preferences.option_show_sp_toggle_state:
                bpy.context.preferences.addons[__package__].preferences.option_show_sp_toggle_state=True
        else:
                bpy.context.preferences.addons[__package__].preferences.option_show_sp_toggle_state=False
        return {'FINISHED'}

class ds_sp_menu(bpy.types.Menu):

    bl_label = " Substance Painter"
    bl_idname = "ds_sp.menu"

    def draw(self, context):
            
        layout = self.layout

        self.layout.operator(ds_sp_export_scene.bl_idname,icon="EXPORT")
        self.layout.operator(ds_sp_pbr_nodes.bl_idname, text='Substance Painter (Scene)', icon="IMPORT").import_setting = 'scene'

        self.layout.operator(ds_sp_export_sel.bl_idname,icon="EXPORT")
        self.layout.operator(ds_sp_pbr_nodes.bl_idname, text='Substance Painter (Selected)', icon="IMPORT").import_setting = 'selected'

def ds_sp_draw_menu(self, context):

    self.layout.menu(ds_sp_menu.bl_idname)

def ds_sp_menu_func_export_scene(self, context):

    self.layout.operator(ds_sp_export_scene.bl_idname)

def ds_sp_menu_func_export_sel(self, context):

    self.layout.operator(ds_sp_export_sel.bl_idname)

def ds_sp_menu_func_import_scene(self, context):

    self.layout.operator(ds_sp_pbr_nodes.bl_idname, text='Substance Painter (Scene)').import_setting = 'scene'

def ds_sp_menu_func_import_sel(self, context):

    self.layout.operator(ds_sp_pbr_nodes.bl_idname, text='Substance Painter (Selected)').import_setting = 'selected'

def ds_sp_draw_btns(self, context):
    
    if context.region.alignment != 'RIGHT':

        layout = self.layout
        row = layout.row(align=True)

        row.operator(ds_sp_export_scene.bl_idname,text="SP:Scene",icon="EXPORT")
        row.operator(ds_sp_pbr_nodes.bl_idname, text='SP:Scene',icon="IMPORT").import_setting = 'scene'

        row.operator(ds_sp_export_sel.bl_idname,text="SP:Sel",icon="EXPORT")
        row.operator(ds_sp_pbr_nodes.bl_idname, text='SP:Sel', icon="IMPORT").import_setting = 'selected'

classes = (
    ds_sp_fbx_export_sel_execute,
    ds_sp_fbx_export_scene_execute,
    ds_sp_obj_export_sel_execute,
    ds_sp_obj_export_scene_execute,
    ds_sp_export_scene,
    ds_sp_export_sel,
    ds_sp_toggle,
    ds_sp_pbr_nodes,
)

def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(ds_sp_menu_func_export_scene)
    bpy.types.TOPBAR_MT_file_import.append(ds_sp_menu_func_import_scene)
    bpy.types.TOPBAR_MT_file_export.append(ds_sp_menu_func_export_sel)
    bpy.types.TOPBAR_MT_file_import.append(ds_sp_menu_func_import_sel)

    if bpy.context.preferences.addons[__package__].preferences.option_display_type=='Buttons':

        bpy.types.TOPBAR_HT_upper_bar.append(ds_sp_draw_btns)

    elif bpy.context.preferences.addons[__package__].preferences.option_display_type=='Menu':

        register_class(ds_sp_menu)
        bpy.types.TOPBAR_MT_editor_menus.append(ds_sp_draw_menu)

def unregister():

    bpy.types.TOPBAR_MT_file_export.remove(ds_sp_menu_func_export_scene)
    bpy.types.TOPBAR_MT_file_import.remove(ds_sp_menu_func_import_scene)
    bpy.types.TOPBAR_MT_file_export.remove(ds_sp_menu_func_export_sel)
    bpy.types.TOPBAR_MT_file_import.remove(ds_sp_menu_func_import_sel)

    if bpy.context.preferences.addons[__package__].preferences.option_display_type=='Buttons':
        
        bpy.types.TOPBAR_HT_upper_bar.remove(ds_sp_draw_btns)

    elif bpy.context.preferences.addons[__package__].preferences.option_display_type=='Menu':

        register_class(ds_sp_menu)
        bpy.types.TOPBAR_MT_editor_menus.remove(ds_sp_draw_menu)

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
