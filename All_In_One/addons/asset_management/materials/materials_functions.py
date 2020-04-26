'''
Copyright (C) 2015 Pistiwique, Pitiwazou
 
Created by Pistiwique, Pitiwazou
 
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
 
import bpy, subprocess, bmesh
from os import listdir
from os.path import join, isdir, isfile, basename
from ..function_utils.get_path import (get_addon_path,
                                       get_directory,
                                       get_library_path
                                       )
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------

def get_valid_materials():
    """ Return the list of valid materials """
    
    valid_materials = list()
    
    AM = bpy.context.window_manager.asset_m
  
    thumbnails_path = get_directory("icons")
    extention = (".jpeg", ".jpg", ".png")
    
    thumbnails = [thumb.rsplit(".", 1)[0] for thumb in listdir(join(thumbnails_path)) if thumb.endswith(extention)]
    
    if not AM.multi_materials:
        if bpy.context.active_object.active_material.name not in thumbnails:
            valid_materials.append(bpy.context.active_object.active_material.name)
    
    else:
        for mat in bpy.context.active_object.material_slots:
            if mat.name not in thumbnails:
                valid_materials.append(mat.name)
    
    return valid_materials

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def add_material_library(blendfile, materials, pack):
    """ Import the target material from the tmp_file into the .blend of the library """
    
    addon_path = get_addon_path()
    tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
    source_file = join(tmp_file, "am_backup.blend")
    script_importer = join(addon_path, "background_tools", 'mat_lib_importer.py')
    
    subprocess.Popen([bpy.app.binary_path, blendfile, '-b', '--python', script_importer, materials, source_file, blendfile, pack])

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def generate_thumbnail_material(category_path, materials):
    """ Generate the thumbnails of the materials """
    
    AM = bpy.context.window_manager.asset_m
    materials = (";").join(materials) if AM.multi_materials else materials
    
    tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
    source_file = join(tmp_file, "am_backup.blend")
    addon_path = get_addon_path()
    
    if AM.mat_thumb_type in ["AM_Sphere.blend", "AM_Cloth.blend"]:
        blend_thumbnailer = join(addon_path, "blend_tools", "material", AM.mat_thumb_type)
    else:
        library_path = get_library_path()
 
        scene_render_path = join(library_path, "materials", "Render Scenes")
 
        for cat in listdir(scene_render_path):
            for scn in listdir(join(scene_render_path, cat, "blends")):
                if scn == AM.mat_thumb_type:
                    blend_thumbnailer = join(scene_render_path, cat, "blends", scn)
                    break
 
    script_thumbnailer = join(addon_path, "background_tools", 'generate_materials_thumbnail.py')
    
    subprocess.Popen([bpy.app.binary_path, blend_thumbnailer, '-b', '--python', script_thumbnailer, source_file, materials, category_path, AM.thumb_ext])
    
#------------------------------------------------------------------
#
#------------------------------------------------------------------
     
def materials_clear_world():
    """ Cleans the blend of all the unnecessary objects and datas object """
 
    AM = bpy.context.window_manager.asset_m
 
    for i in range(20):
        bpy.context.scene.layers[i] = True
 
    for obj in bpy.context.scene.objects:
        obj.hide = False
        obj.hide_select = False
        obj.hide_render = False
 
    if AM.render_type == 'opengl':
        bpy.ops.object.select_all(action = 'INVERT')
        bpy.ops.object.delete()
        bpy.ops.object.select_all(action = 'SELECT')
 
    else:
        bpy.ops.object.select_all(action = 'SELECT')
        bpy.ops.object.delete()
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def apply_material(mat_name, assign_mat):
    ob = bpy.context.active_object
 
    if assign_mat:
        bpy.ops.object.material_slot_add()
 
    # Get material
    if bpy.data.materials.get(mat_name):
        mat = bpy.data.materials[mat_name]
    else:
        # create material
        mat = bpy.data.materials.new(name=mat_name)
 
    # Assign it to object
    if len(ob.data.materials):
        # assign to active material slot
        ob.active_material = mat
    else:
        # no slots
        ob.data.materials.append(mat)
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def import_material_from_asset_management():
    """ Import the selected material """
 
    AM = bpy.context.window_manager.asset_m
    mat_name = bpy.context.window_manager.AssetM_previews.rsplit(".", 1)[0]
    blendfile = join(get_directory("blends"), mat_name + ".blend")
    directory = join(blendfile, "Material")
    act_obj = bpy.context.active_object
    assign_mat = False
 
    if bpy.context.object.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(act_obj.data)
 
        selected_face = [f for f in bm.faces if f.select]
 
        if selected_face:
            assign_mat = True
 
        bpy.ops.object.mode_set(mode='OBJECT')
 
        if mat_name in bpy.data.materials and AM.existing_material:
            if assign_mat:
                apply_material(mat_name, assign_mat)
            else:
                bpy.context.active_object.active_material = bpy.data.materials[mat_name]
 
        else:
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                if data_from.materials:
                    if AM.import_choise == 'append':
                        bpy.ops.wm.append(filename=mat_name, directory=directory)
                    else:
                        bpy.ops.wm.link(filename=mat_name, directory=directory)                    
 
            mat_name = [m for m in [mat.name for mat in bpy.data.materials] if mat_name in m][-1]
            apply_material(mat_name, assign_mat)
 
        bpy.ops.object.mode_set(mode='EDIT')
        if assign_mat:
            bpy.ops.object.material_slot_assign()
 
    elif bpy.context.object.mode == 'OBJECT':
        assign_mat = False
 
        obj_list = [item for item in bpy.context.selected_objects]
 
        if mat_name in bpy.data.materials and AM.existing_material:
            bpy.context.active_object.active_material = bpy.data.materials[mat_name]
 
        else:
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                if data_from.materials:
                    if AM.import_choise == 'append':
                        bpy.ops.wm.append(filename=mat_name, directory=directory)
                    else:
                        bpy.ops.wm.link(filename=mat_name, directory=directory)
 
            mat_name = [m for m in [mat.name for mat in bpy.data.materials] if mat_name in m][-1]
 
        for obj in obj_list:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
 
            apply_material(mat_name, assign_mat)
 
        for obj in obj_list:
            obj.select = True
 
        bpy.context.scene.objects.active = act_obj
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def get_custom_material_render_scene():
    """ Return the list of custom material render scene """
 
    AM = bpy.context.window_manager.asset_m
    library_path = get_library_path()
    render_scenes = []
 
    if isdir(join(library_path, "materials", "Render Scenes")):
        scene_render_path = join(library_path, "materials", "Render Scenes")
        categories = [cat for cat in listdir(scene_render_path) if isdir(join(scene_render_path, cat))]
 
        for cat in categories:
            for scn in listdir(join(scene_render_path, cat, "blends")):
                if scn.endswith(".blend"):
                    render_scenes.append(scn)
 
    return render_scenes
 
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def update_render_material_library(self, context):
    """ Custom toggle between 'as_mat_scene' and 'libraries' properties """
 
    AM = context.window_manager.asset_m
    library_path = get_library_path()
    if isdir(join(library_path, AM.library_type, "Render Scenes")):
        if AM.as_mat_scene:
            if AM.libraries != 'Render Scenes':
                AM.previous_lib = AM.libraries
                AM.libraries = 'Render Scenes'
        else:
            AM.libraries = AM.previous_lib
