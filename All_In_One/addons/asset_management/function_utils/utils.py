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
 
import bpy, subprocess, atexit
from os import remove, listdir
from os.path import isfile, join, abspath, isdir, split, dirname, abspath
from bpy.app.handlers import persistent
from .get_path import (get_addon_path,
                       get_directory,
                       get_library_path,
                       )
from ..assets_scenes.assets_functions import preview_add_to_selection
from ..materials.materials_functions import import_material_from_asset_management
from ..ibl.ibl_functions import import_ibl_from_asset_management

library_setup = {}
new_file_library = {}

@persistent
def load_handler_before(dummy):
    if bpy.context.user_preferences.filepaths.use_load_ui:
        new_file_library.clear()
        WM = bpy.context.window_manager
        AM = WM.asset_m
        new_file_library[AM.library_type] = (AM.libraries, AM.categories, WM.AssetM_previews)
 
 
@persistent
def load_handler_after(dummy):
    if new_file_library:
        WM = bpy.context.window_manager
        AM = WM.asset_m
        for k in new_file_library.keys():
            AM.library_type = k
            AM.libraries = new_file_library[k][0]
            AM.categories = new_file_library[k][1]
 
bpy.app.handlers.load_pre.append(load_handler_before)
bpy.app.handlers.load_post.append(load_handler_after)


def save_tmp():
    """ Save the current blend in the blender tmp file """
 
    tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
    if isfile(join(tmp_file, "am_backup.blend")):
        remove(join(tmp_file, "am_backup.blend"))
 
    bpy.ops.wm.save_as_mainfile(
        filepath = join(tmp_file, "am_backup.blend"),
        copy = True
        )


#------------------------------------------------------------------
#
#------------------------------------------------------------------

def assets_clear_world():
    """ Retaining only the selected object and the active scene before adding in the library """
 
    AM = bpy.context.window_manager.asset_m
    scene = bpy.context.scene
 
    # recovering the selected objects list and their children
    objs = set()
 
    def add_obj(obj):
        objs.add(obj)
 
        for child in obj.children:
            add_obj(child)
 
    for obj in scene.objects:
        if obj.select:
            add_obj(obj)
 
    # one activates all the layers
    for i in range(20):
        scene.layers[i] = True
 
    # before cleaning the objects are prepared
    for obj in scene.objects:
        obj.hide_select = False
        obj.hide = False
        if obj in objs:
            obj.select = True
 
    bpy.ops.object.select_all(action = 'INVERT')
 
    bpy.ops.group.objects_remove_all()
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action = 'SELECT')

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def run_opengl_render(icon_path, asset_name):
    bpy.ops.scene.new(type='LINK_OBJECT_DATA')
    layers = [i for i in range(20) if bpy.context.scene.layers[i]]
    AM_cam = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA' and "AM_OGL_Camera" in obj.name]
    if AM_cam:
        AM_cam[0].select=True
        
    assets_clear_world()
    opengl_rendering(icon_path, asset_name)
    
    if AM_cam:
        bpy.context.scene.objects.unlink(AM_cam[0])
 
#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def opengl_rendering(icon_path, asset_name):
    """ Run the opengl rendering """
    
    AM = bpy.context.window_manager.asset_m
    bpy.context.scene.render.use_antialiasing = True
    bpy.context.scene.render.antialiasing_samples = '16'
    bpy.ops.render.opengl()
    bpy.data.images['Render Result'].save_render(filepath=join(icon_path, asset_name + AM.thumb_ext))
    bpy.data.images['Render Result'].user_clear()

#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def get_asset_name():
    """ Return the name of the asset """
 
    AM = bpy.context.window_manager.asset_m
 
    if AM.library_type == 'assets':
        asset_name = AM.group_name if AM.group_name and len([obj for obj in bpy.context.scene.objects if obj.select]) >= 2 else bpy.context.active_object.name
    
    elif AM.library_type == 'materials':
        if AM.as_mat_scene:
            asset_name = AM.scene_name
        else:
            asset_name = AM.material_rendering[0] if len(AM.material_rendering) == 1 else AM.material_rendering
    
    elif AM.library_type == 'scenes':
        asset_name = AM.scene_name
 
    return asset_name

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def get_blend(asset, dir):
    """ Return the .blend from the asset in the preview """
    return ''.join([b for b in listdir(dir) if b.endswith(".blend") and b.rsplit(".", 1)[0] == asset.rsplit(".", 1)[0]])

#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def run_preview_add_to_selection(self, context):
    """  """
    
    WM = context.window_manager
    AM = WM.asset_m
    
    if WM.AssetM_previews != "EMPTY.png":
        if AM.library_type != 'hdri':
            del(AM.datablock_list[:])
            
        if AM.library_type == 'assets' and AM.import_choise == 'link':
            del(AM.groups_list[:])
            del(AM.script_list[:])
        
        store_library_setup()
        
        if not AM.without_import:
            if AM.library_type == 'assets':
#                if AM.import_choise == 'append':
#                if AM.replace_asset:
                bpy.ops.object.import_active_preview()
#                else:
#                    preview_add_to_selection()
            
            elif AM.library_type == 'materials' and context.object is not None:
                import_material_from_asset_management()
            
            elif AM.library_type == 'hdri':
                import_ibl_from_asset_management()
        
        save_library_setup()
    
#------------------------------------------------------------------
#
#------------------------------------------------------------------

def run_clean_world(scene, blendfile, pack, lib_type, material, text_file, world_name, ibl_path):
    addon_path = get_addon_path()
    Asset_M_clean_world = join(addon_path, "background_tools", 'clean_world.py')
    
    sub = subprocess.Popen([bpy.app.binary_path, blendfile, '-b', '--python', Asset_M_clean_world, scene, blendfile, pack, lib_type, material, text_file, world_name, ibl_path])

#------------------------------------------------------------------
#
#------------------------------------------------------------------
 
def run_clean_datas(blendfile):
    addon_path = get_addon_path()
    Asset_M_clean_data = join(addon_path, "background_tools", 'clean_datas.py')
 
    sub = subprocess.Popen([bpy.app.binary_path, blendfile, '-b', '--python', Asset_M_clean_data, blendfile])
    
#------------------------------------------------------------------
#
#------------------------------------------------------------------

def store_library_setup():
    AM = bpy.context.window_manager.asset_m
    library_setup["backup"] = "{};{};{};{}".format(AM.library_type,AM.libraries,AM.categories,bpy.context.window_manager.AssetM_previews)

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def load_library_setup():
    
    AM = bpy.context.window_manager.asset_m
    addon_path = get_addon_path()
    if isfile(join(addon_path, "library", "library_setup.txt")):
        AM.without_import = True
        try:
            with open(join(addon_path, "library", "library_setup.txt"), "r") as lib:
                lib_setup = lib.read()
            
            AM.library_type, AM.libraries, AM.categories, bpy.context.window_manager.AssetM_previews = lib_setup.split(";")
            AM.without_import = False
        except:
            print("#"*50)
            print("Cannot load the library setup")
            AM.without_import = False

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def save_library_setup():
    if "backup" in library_setup:
        (addon_path, current_dir) = split(dirname(abspath(__file__)))
        lib_type, lib, cat, asset = library_setup["backup"].split(";")
        
        with open(join(addon_path, "library", "library_setup.txt"), "w") as lib_setup:
            lib_setup.write("{};{};{};{}".format(lib_type, lib, cat, asset))
 
atexit.register(save_library_setup)