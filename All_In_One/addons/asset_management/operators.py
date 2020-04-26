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

import bpy, shutil, subprocess, pickle
from bpy.types import Operator
from os import remove, rename, listdir, makedirs
from os.path import isfile, isdir, join, basename, split, exists, basename, dirname, abspath
from .function_utils.utils import (get_asset_name,
                                   get_blend,
                                   run_clean_world,
                                   run_clean_datas,
                                   save_tmp,
                                   )
from .function_utils.get_path import *
from .assets_scenes.assets_functions import (preview_add_to_selection,
                                             generate_thumbnail_asset,
                                             )
from .materials.materials_functions import (import_material_from_asset_management,
                                            generate_thumbnail_material,
                                            )
from .ibl.ibl_functions import (import_ibl_from_asset_management,
                                get_ibl_from_thumbnail,
                                generate_thumbnail_ibl,
                                )
from .preview.preview_utils import update_pcoll_preview


class DebugOperator(bpy.types.Operator):
    bl_idname = "my_operator.debug_operator"
    bl_label = "Debug Operator"

    def execute(self, context):
        #(addon_path, current_dir) = split(dirname(abspath(__file__)))
        
        WM = context.window_manager
        AM = WM.asset_m
        asset_name = WM.AssetM_previews.rsplit(".", 1)[0]
        with open(join(get_library_path(), AM.library_type, AM.libraries, AM.categories, "IBL", asset_name + "_settings"), "rb") as file:
            pkl_load = pickle.Unpickler(file)
            dict = pkl_load.load()
            
        print(dict)
        return {"FINISHED"}
          
# ------------------------------------------------------------------
#    GENERATE THUMBNAILS 
# ------------------------------------------------------------------

class CleanAssetBlend(Operator):
    """ Open and clean the asset.blend """
    bl_idname = "object.clean_asset_blend"
    bl_label = "Clean asset blend"
    bl_options = {'REGISTER'}
    
    def modal(self, context, event):
        AM = context.window_manager.asset_m
        if not isfile(join(self.directory_path, "cleaning_asset.txt")):
            if AM.render_type == 'opengl':
                if isfile(join(get_directory("icons"), "EMPTY.png")):
                    remove(join(get_directory("icons"), "EMPTY.png"))
                update_pcoll_preview()
                AM.asset_adding_enabled = False
                bpy.ops.object.cancel_panel_choise()
                run_clean_datas(self.blend_file)
                return {'FINISHED'}
                
            bpy.ops.object.run_generate_thumbnails('INVOKE_DEFAULT')
            AM.asset_adding_enabled = False
            return {'FINISHED'}
        
        else:
            return {'PASS_THROUGH'} 
            
 
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        self.directory_path = get_directory("blends")
        addon_prefs = get_addon_preferences()
        asset_name = get_asset_name()
        self.blend_file = join(self.directory_path, asset_name + ".blend")
        pack = "pack" if addon_prefs.pack_image == 'pack' else ""
        world_name = ""
        ibl_path = ""
        
        if AM.library_type in ['assets', 'scenes']:
            lib_type = AM.library_type
            material = ""
        elif AM.library_type == 'materials' and AM.as_mat_scene:
            lib_type = 'as_mat_scene'
            material = ""
        
        if AM.library_type == 'scenes' or AM.library_type == 'materials' and AM.as_mat_scene:
            for world in bpy.data.worlds:
                if world.node_tree:
                    for node in world.node_tree.nodes:
                        if node.type == 'TEX_ENVIRONMENT':
                            world_name = world.name
                            ibl_path = node.image.filepath
         
        # create a check file to force the release of the generate_thumbnail operator to wait the end of the clean asset
        with open(join(self.directory_path, "cleaning_asset.txt"), "w") as file:
            file.write("en cours")
        AM.asset_adding_enabled = True
            
        run_clean_world(bpy.context.scene.name, self.blend_file, pack, lib_type, material, join(self.directory_path, "cleaning_asset.txt"), world_name, ibl_path)
 
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    

# ------------------------------------------------------------------
#    GENERATE THUMBNAILS 
# ------------------------------------------------------------------
 
class RunGenerateThumbnails(Operator):
    ''' Generate the thumbnail and update the preview when added it '''
    bl_idname = "object.run_generate_thumbnails"
    bl_label = "Run generate thumbnails" 
 
    def is_thumbnail_updated(self):
        AM = bpy.context.window_manager.asset_m
        extentions = (".jpg", ".jpeg", ".png")
        self.thumbnails_list = [f for f in listdir(self.icon_path) if f.endswith(extentions)]
        
        if self.library_type == 'hdri':
            return isfile(join(self.icon_path, AM.ibl_to_thumb[-1].rsplit(".", 1)[0] + AM.thumb_ext))
        
        elif self.library_type == 'materials' and AM.render_type == 'render':
            return isfile(join(self.icon_path, AM.material_rendering[-1] + AM.thumb_ext))
        
        else:
            return self.thumbnails_list != self.thumbnails_directory_list
    
 
    def modal(self, context, event):
        AM = bpy.context.window_manager.asset_m
        extentions = (".jpg", ".jpeg", ".png")
        
        if AM.multi_materials and len(AM.material_rendering) >= 2:
            for mat in AM.material_rendering:
                if isfile(join(self.icon_path, mat + AM.thumb_ext)):
                    AM.material_rendering.remove(mat)
                else:
                    return {'PASS_THROUGH'}
        
        if self.is_thumbnail_updated():
 
            if isfile(join(self.icon_path, "EMPTY.png")):
                remove(join(self.icon_path, "EMPTY.png"))
 
            update_pcoll_preview()
 
            AM.render_running = False
            
            bpy.ops.object.cancel_panel_choise()
            
            if AM.library_type in ['assets', 'scenes'] or AM.library_type == 'materials' and AM.as_mat_scene:
                run_clean_datas(self.blend_file)
            
            del(AM.ibl_to_thumb[:])
            del(AM.material_rendering[:])
            if AM.library_type == 'assets' and AM.import_choise == 'link':
                del(AM.groups_list[:])
                del(AM.script_list[:])
            
            return {'FINISHED'}
 
        else:
            return {'PASS_THROUGH'}
 
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        self.icon_path = get_directory("icons")
        self.addon_prefs = get_addon_preferences()
        library_path = get_library_path()

        if AM.library_type != 'hdri':
            self.asset_name = get_asset_name()
            if not (AM.library_type == 'materials' and not AM.as_mat_scene):
                self.blend_file = join(get_directory("blends"), self.asset_name + '.blend')
        extentions = (".jpg", ".jpeg", ".png")
        self.thumbnails_directory_list = [f for f in listdir(self.icon_path) if f.endswith(extentions)]
        self.library_type = AM.library_type # need if library_type changed during the render
        
        if self.library_type == 'hdri':
            generate_thumbnail_ibl(self.icon_path)
            AM.render_running = True
        
        else:
            if AM.render_type == 'render':
                if AM.library_type == 'materials':
                    
                    generate_thumbnail_material(join(library_path, AM.library_type, AM.libraries, AM.categories), self.asset_name)
                else:
                    generate_thumbnail_asset(self.asset_name)
                AM.render_running = True
     
            elif AM.render_type == 'image':
                if AM.image_type == 'disk':
                    thumbnail = bpy.path.abspath(AM.custom_thumbnail_path)
                    shutil.copy(thumbnail, join(self.icon_path, self.asset_name + AM.thumb_ext))
                else:
                    bpy.data.images[AM.render_name].save_render(filepath=join(self.icon_path, self.asset_name + AM.thumb_ext))
                    
        context.window_manager.modal_handler_add(self)
 
        return {'RUNNING_MODAL'}

# ------------------------------------------------------------------
#    REMOVE ASSET
# ------------------------------------------------------------------

class RemoveAssetFromLibrary(Operator):
    ''' Remove the asset from your library '''
    bl_idname = "object.remove_asset_from_lib"
    bl_label = "Remove Asset"
 
    @classmethod
    def poll(cls, context):
        return not bpy.context.window_manager.asset_m.render_running
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        addon_path = get_addon_path()
        source_file = join(addon_path, "icons", "EMPTY.png")
        icons_path = get_directory("icons")
        if AM.library_type != 'hdri':
            file_dir = get_directory("blends")
        else:
            file_dir = get_directory("IBL")
        favorites_path = get_directory("Favorites")
        tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
        AM.is_deleted = False
        extentions = (".jpg", ".jpeg", ".png")
        
        if AM.library_type != 'hdri' and AM.replace_rename == 'replace':
            base_asset = get_asset_name()
            
            # recovered the thumbnail to the corresponding asset
            asset = [thumb for thumb in [f for f in listdir(icons_path) if f.endswith(extentions)] if thumb.rsplit(".", 1)[0] == base_asset][0]

        else:
            asset = context.window_manager.AssetM_previews
        
        if AM.library_type != 'hdri':
            file_to_delete = asset.rsplit(".", 1)[0] + ".blend"
        else:
            file_to_delete = get_ibl_from_thumbnail(asset, file_dir)

        favorites_files = [f for f in listdir(favorites_path) if f.endswith(extentions)]
        
        if asset in favorites_files:
            remove(join(favorites_path, asset))
            if len(favorites_files) == 1:
                AM.favorites_enabled = False
        
        if AM.library_type != 'hdri':
            for lib in bpy.data.libraries:
                if asset.rsplit(".", 1)[0] + ".blend" == basename(lib.filepath):
                    lib.filepath = ""

            if isfile(join(tmp_file, "am_remove_backup.blend")):
                remove(join(tmp_file, "am_remove_backup.blend"))
            if isfile(join(file_dir, file_to_delete)):
                shutil.copy(join(file_dir, file_to_delete), join(tmp_file, "am_remove_backup.blend"))
                remove(join(file_dir, file_to_delete))
        
        else:
            if isfile(join(file_dir, file_to_delete)):
                remove(join(file_dir, file_to_delete))
            
            if isfile(join(file_dir, asset.rsplit(".", 1)[0] + "_settings")):
                remove(join(file_dir, asset.rsplit(".", 1)[0] + "_settings"))
            
        if isfile(join(icons_path, asset)):
            remove(join(icons_path, asset))
 
        thumbnails_list = [f for f in listdir(icons_path) if f.endswith(extentions)]
 
        if not thumbnails_list:       
            shutil.copy(source_file, join(icons_path, "EMPTY.png"))
 
        if AM.library_type == 'assets' and AM.import_choise == 'link':
            del(AM.groups_list[:])
            del(AM.script_list[:])
        
        AM.is_deleted = True
 
        if AM.replace_rename == 'replace':
            return {'FINISHED'}
 
        else:
            update_pcoll_preview()
            return {'FINISHED'}
 
    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value*4, height=100)
 
    def draw(self, context):
        layout = self.layout
        asset = context.window_manager.AssetM_previews.rsplit(".", 1)[0]
 
        col = layout.column()
        col.label("Remove \" {} \"".format(asset), icon='ERROR')
        col.label("    It will not longer exist in Asset management")

# ------------------------------------------------------------------
#    CANCEL PANEL CHOISE
# ------------------------------------------------------------------

class CancelPanelChoise(Operator):
    """ Cancel the panel choise """
    bl_idname = "object.cancel_panel_choise"
    bl_label = "Cancel"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        AM.replace_rename = 'rename'
        AM.adding_options = False
        AM.group_name = ""
        AM.render_name = ""
        AM.new_name = ""
        AM.scene_name = ""
        AM.custom_thumbnail_path = ""
        AM.ibl_type = '.hdr'
        AM.as_mat_scene = False
        if "AM_OGL_Camera" in context.scene.objects:
            bpy.ops.object.remove_ogl_render()
        return {'FINISHED'}

# ------------------------------------------------------------------
#    SETUP / REMOVE OPENGL RENDER   
# ------------------------------------------------------------------

class SetupOpenGlRender(Operator):
    """ Setup the scene for an opengl render """
    bl_idname = "object.setup_ogl_render"
    bl_label = "Setup OGL render"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        rendered_shade = False
        AM = context.window_manager.asset_m
        #Add object in the list
        obj_list = [obj for obj in bpy.context.scene.objects if obj.select]
        list_only_render = [obj for obj in context.scene.objects if obj.select and (obj.type == 'MESH' or obj.type == 'CURVE' and (obj.data.extrude or obj.data.bevel_depth))]
        active_obj = context.active_object

        #Add camera and remane it
        if not "AM_OGL_Camera" in [obj.name for obj in bpy.context.scene.objects]:
            AM.cam_reso_X = bpy.context.scene.render.resolution_x
            AM.cam_reso_Y = bpy.context.scene.render.resolution_y
            
            if context.space_data.viewport_shade == 'RENDERED':
                bpy.context.space_data.viewport_shade = 'SOLID'
                rendered_shade = True
                
            bpy.ops.object.camera_add()
            bpy.context.active_object.name = "AM_OGL_Camera"
            bpy.ops.view3d.object_as_camera()
            bpy.context.space_data.lock_camera=True
            bpy.context.object.data.clip_end = 10000
            bpy.context.object.data.lens = 85
            if len(list_only_render):
                bpy.context.space_data.show_only_render = True
            else:
                bpy.context.space_data.show_only_render = False
                
            bpy.ops.view3d.camera_to_view()

            #Setup the render settings
            bpy.context.scene.render.resolution_x = 256
            bpy.context.scene.render.resolution_y = 256
            bpy.context.scene.render.resolution_percentage = 100
 
            #Deselect All
            bpy.ops.object.select_all(action='DESELECT')
            
            #Select the objects in the list
            for obj in obj_list:
                obj.select=True
                
            bpy.context.scene.objects.active = active_obj
            
            bpy.ops.view3d.view_selected() 
            
            if rendered_shade:
                bpy.context.space_data.viewport_shade = 'RENDERED'
            
        else:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects['AM_OGL_Camera'].select=True
            bpy.context.scene.objects.active = bpy.data.objects['AM_OGL_Camera']
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.viewnumpad(type="CAMERA")
            bpy.context.space_data.lock_camera=True
            bpy.data.objects['AM_OGL_Camera'].select=False
            for obj in obj_list:
                obj.select=True
            bpy.context.scene.objects.active = active_obj
        return {"FINISHED"}


class RemoveOpenGlRenderSetup(Operator):
    """ Remove the OpenGl Render Setup """
    bl_idname = "object.remove_ogl_render"
    bl_label = "Remove OGL Setup"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        if "AM_OGL_Camera" in context.scene.objects:
            objects = [obj for obj in bpy.context.selected_objects]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects["AM_OGL_Camera"].select=True
            bpy.ops.object.delete()

            for obj in objects:
                obj.select=True
        bpy.context.space_data.show_only_render=False
        bpy.context.space_data.use_matcap = False
        bpy.context.space_data.fx_settings.use_ssao = False
        bpy.context.space_data.lock_camera = False

        if AM.cam_reso_X:
            bpy.context.scene.render.resolution_x = AM.cam_reso_X
            bpy.context.scene.render.resolution_y = AM.cam_reso_Y
        AM.cam_reso_X = 0
        AM.cam_reso_Y = 0   
        return {"FINISHED"}

# ------------------------------------------------------------------
#    IMPORT ACTIVE PREVIEW
# ------------------------------------------------------------------
 
class ImportActivePreview(Operator):
    """ Import the asset from active preview """
    bl_idname = "object.import_active_preview"
    bl_label = "import Active Preview"
    bl_description = ""
    bl_options = {"REGISTER"}
 
    group_name = bpy.props.StringProperty()
 
    @classmethod
    def poll(cls, context):
        WM = context.window_manager
        AM = WM.asset_m
        return WM.AssetM_previews != "EMPTY.png"
 
    def get_last_parent(self):
        last_parent = []
 
        def get_parent(obj):
            if obj.parent:
                if not obj.parent in last_parent:
                    get_parent(obj.parent)
 
            else:
                if obj.children:
                    last_parent.append(obj)
 
        for obj in bpy.context.selected_objects:
            get_parent(obj)
 
        return last_parent     
 
    def get_children_list(self):
        children_list = []
 
        def add_children(obj):
            for child in obj.children:
                children_list.append(child)
                add_children(child)
 
        for child in self.get_last_parent():
            add_children(child)
 
        return children_list
 
 
    def execute(self, context):
        AM = context.window_manager.asset_m
 
        if AM.library_type == 'assets' or (AM.library_type == 'materials' and AM.libraries == 'Render Scenes'):
            obj_list = []
            if AM.replace_asset:
                simple_obj = [obj for obj in context.selected_objects if not obj.parent and not obj.children]
                parents = self.get_last_parent()
                childrens = self.get_children_list()
 
                if AM.replace_multi:
                    bpy.ops.object.select_all(action='DESELECT')
 
                    for obj in simple_obj + parents:
                        bpy.context.scene.objects.active = obj
                        obj.select=True
                        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
                        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
 
                        ob_matrix = obj.matrix_world.copy()
                        if AM.import_choise == 'link':
                            bpy.ops.object.import_am_link(group_name = self.group_name)
                        else:
                            preview_add_to_selection()
                        obj_list.append(context.active_object)
                        bpy.context.active_object.matrix_world = ob_matrix
 
 
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in simple_obj + parents + childrens:
                        obj.select = True
                        
                    bpy.ops.object.delete()
 
                    for obj in obj_list:
                        obj.select=True
                    bpy.context.scene.objects.active = obj_list[0]
                    del(obj_list[:])  
 
                else:
                    if len(context.selected_objects) >= 2:
                        for obj in simple_obj + parents:
                            obj.select=True
                        bpy.ops.view3d.snap_cursor_to_selected()
                        if childrens:
                            for obj in childrens:
                                obj.select=True
                        bpy.ops.object.delete()
                        if AM.import_choise == 'link':
                            bpy.ops.object.import_am_link(group_name = self.group_name)
                        else:
                            preview_add_to_selection()
 
                    else:
                        if parents:
                            ob_matrix = parents[0].matrix_world.copy()
 
                        else:
                            ob_matrix = bpy.context.object.matrix_world.copy()
                        
                        if AM.import_choise == 'link':
                            bpy.ops.object.import_am_link(group_name = self.group_name)
                        else:
                            preview_add_to_selection()
 
                        obj_list.append(context.active_object)
                        
                        bpy.context.active_object.matrix_world = ob_matrix
                        
                        bpy.ops.object.select_all(action = 'DESELECT')
                        for obj in simple_obj + parents + childrens:
                            obj.select = True
                            
                        bpy.ops.object.delete()
                        
                        for obj in obj_list:
                            obj.select=True
                        bpy.context.scene.objects.active = obj_list[0]
                        del(obj_list[:])  
                
                for obj in bpy.data.objects:
                    if obj.users == 0:
                        bpy.data.objects.remove(obj)
                 
                for mesh in bpy.data.meshes:
                    if mesh.users == 0:
                        bpy.data.meshes.remove(mesh)
                
            else:
                if AM.import_choise == 'link':
                    bpy.ops.object.import_am_link(group_name = self.group_name)
                else:
                    preview_add_to_selection()
 
        elif AM.library_type == 'materials':
            import_material_from_asset_management()
            
        elif AM.library_type == 'hdri':
            if context.object is not None:
                bpy.ops.object.mode_set(mode = 'OBJECT')
            import_ibl_from_asset_management()
 
        return {"FINISHED"} 


#class AppendActivePreview(Operator):
#    """ Append the asset from active preview """
#    bl_idname = "object.append_active_preview"
#    bl_label = "import Active Preview"
#    bl_description = ""
#    bl_options = {"REGISTER"}
# 
#    @classmethod
#    def poll(cls, context):
#        WM = context.window_manager
#        AM = WM.asset_m
#        return WM.AssetM_previews != "EMPTY.png" and (not AM.without_import and (AM.library_type in ['materials', 'hdri'] or AM.import_choise == 'append'))
#    
#    def execute(self, context):
#        bpy.ops.object.import_active_preview()
#        
#        return {'FINISHED'}

# -----------------------------------------------------------------------------
#   ADD / REMOVE FAVOURITES
# -----------------------------------------------------------------------------

class AddToFavourites(Operator):
    ''' Add the asset to your favourites '''
    bl_idname = "object.add_to_favourites"
    bl_label = "Add to Favourites" 
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        thumbnails_path = get_directory("icons")
        favourites_path = get_directory("Favorites")
        target = context.window_manager.AssetM_previews
        
        if not exists(favourites_path):
            makedirs(favourites_path)
        
        source_file = join(thumbnails_path, target)
        destination = join(favourites_path, target)
        shutil.copy(source_file, destination)
        
        return {'FINISHED'}



class RemoveFromFavorites(Operator):
    ''' Remove the asset from your favourites '''
    bl_idname = "object.remove_from_favourites"
    bl_label = "Remove from favourites"
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        favourites_path = get_directory("Favorites")
        target = context.window_manager.AssetM_previews
        
        remove(join(favourites_path, target))
        
        extentions = (".jpg", ".jpeg", ".png")
        favourites_files = [f for f in listdir(favourites_path) if f.endswith(extentions)] 

        update_pcoll_preview()
        
        if not favourites_files:
            AM.favourites_enabled = False
      
        return {'FINISHED'}

# -----------------------------------------------------------------------------
#   SWITCH ASSET PREVIEW
# -----------------------------------------------------------------------------

class NextAsset(Operator):
    """ Display the next asset """
    bl_idname = "object.next_asset"
    bl_label = "Next Asset"
    bl_options = {"REGISTER"}
    
    selection = bpy.props.IntProperty(
        default = 0
        )
    
    @classmethod
    def poll(cls, context):
        WM = context.window_manager
        AM = WM.asset_m
        return WM.AssetM_previews != "EMPTY.png"
    
    def get_next_asset(self, selection):
        """ Return the next asset to draw in the preview """
     
        AM = bpy.context.window_manager.asset_m
        if AM.favourites_enabled:
            thumbnails_path = get_directory("Favorites")
        else:
            thumbnails_path = get_directory("icons")
        current_asset = bpy.context.window_manager.AssetM_previews
        extention = (".jpg", ".jpeg", ".png")
        asset_list = [f for f in listdir(thumbnails_path) if f.endswith(extention)]
     
        current_index = asset_list.index(current_asset)
        max_index = len(asset_list)-1
        asset = asset_list[current_index + selection] if current_index + selection <= max_index else asset_list[0]
     
        return asset
    
    def execute(self, context):
        AM = bpy.context.window_manager.asset_m
        
        without_import = AM.without_import
        
        AM.without_import = True
        bpy.context.window_manager.AssetM_previews = self.get_next_asset(self.selection)
        AM.without_import = without_import

        
        if not AM.without_import:
            if AM.library_type == 'assets':
                if AM.replace_asset and AM.import_choise == 'append':
                    bpy.ops.object.import_active_preview()
            elif AM.library_type == 'hdri' and not AM.without_import:
                import_ibl_from_asset_management()
            
            if AM.library_type == 'assets' and AM.import_choise == 'link':
                del(AM.groups_list[:])
                del(AM.script_list[:])
        
        return {"FINISHED"}
    
# ------------------------------------------------------------------
#    IMPORT LINK
# ------------------------------------------------------------------
 
class ImportAMLink(Operator):
    """ Import the asset or the material by linking """
    bl_idname = "object.import_am_link"
    bl_label = "Import Am Link"
 
    group_name = bpy.props.StringProperty(default="")
 
    def execute(self, context):
        AM = context.window_manager.asset_m
 
        bpy.ops.object.select_all(action='DESELECT')
 
        asset = context.window_manager.AssetM_previews.rsplit(".", 1)[0]
        blendfile = join(get_directory("blends"), asset + ".blend")
        if self.group_name:
            directory = join(blendfile, 'Group')
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                bpy.ops.wm.link(filename = self.group_name, directory = directory)
        else:
            directory = join(blendfile, 'Object')
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                bpy.ops.wm.link(filename = asset, directory = directory)
 
        return {"FINISHED"}

# ------------------------------------------------------------------
#    CHANGE NAME ASSET
# ------------------------------------------------------------------

class ChangeNameInAssetManagement(Operator):
    """ Rename the asset in your library """
    bl_idname = "object.change_name_asset"
    bl_label = "Change name"
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        addon_path = get_addon_path()
        target = bpy.context.window_manager.AssetM_previews
        new_name = AM.new_name
        icons_path = get_directory("icons")
        favorites_path = get_directory("Favorites")
        if AM.library_type != 'hdri':
            file_dir = get_directory("blends")
        else:
            file_dir = get_directory("IBL")
        
        if AM.library_type != 'hdri':
            Asset_M_library = join(file_dir, target.rsplit(".", 1)[0] + ".blend")
            
        Asset_M_change_name_script = join(addon_path, "background_tools", "change_asset_name.py")
        rename(join(icons_path, target), join(icons_path, '.'.join((new_name, target.rsplit(".", 1)[-1]))))
        
        extentions = (".jpg", ".jpeg", ".png")
        favorites_files = [f for f in listdir(favorites_path) if f.endswith(extentions)] 
 
        if target in favorites_files:
            rename(join(favorites_path, target), join(favorites_path, ".".join((new_name, target.rsplit(".", 1)[-1]))))
        
        if AM.library_type != 'hdri':
            simple = False
            if AM.library_type == 'assets':
                with bpy.data.libraries.load(Asset_M_library) as (data_from, data_to):
                    if len(data_from.objects) == 1:
                        simple = True
            else:
                simple = True
     
            if simple:
                sub = subprocess.Popen([bpy.app.binary_path, Asset_M_library, '-b', '--python', Asset_M_change_name_script, target.rsplit(".", 1)[0], new_name, Asset_M_library, AM.library_type])
                sub.wait()
 
            rename(join(file_dir, target.rsplit(".", 1)[0] + ".blend"), join(file_dir, new_name + ".blend"))
            if isfile(join(file_dir, target.rsplit(".", 1)[0] + ".blend1")):
                remove(join(file_dir, target.rsplit(".", 1)[0] + ".blend1"))
        
        else:
            ibl = get_ibl_from_thumbnail(target, file_dir)
            rename(join(file_dir, ibl), join(file_dir, '.'.join((new_name, ibl.rsplit(".", 1)[-1]))))
            
            
        AM.rename_asset = False
        AM.new_name = ""
        if AM.library_type == 'assets' and AM.import_choise == 'link':
            del(AM.groups_list[:])
            del(AM.script_list[:])
        
        update_pcoll_preview()
 
        return {'FINISHED'}

# ------------------------------------------------------------------
#    DATA CLEANER  
# ------------------------------------------------------------------

# The author name's of the "link_to_base_names" code is Sybren A. Stuvel
class MATERIAL_OT_link_to_base_names(Operator):
    """ Link materials to base name of the selected objects """
    bl_idname = "material.link_to_base_names"
    bl_label = "Link materials to base names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for ob in context.selected_objects:
            for slot in ob.material_slots:
                self.fixup_slot(slot)
 
        materials = bpy.data.materials
 
        for material in bpy.data.materials:
            if not material.users:
                materials.remove(material)
                
        return {'FINISHED'}
 
    def split_name(self, material):
        name = material.name
 
        if not '.' in name:
            return name, None
 
        base, suffix = name.rsplit('.', 1)
        if not suffix.isdigit():
            return name, None
 
        return base, suffix
 
    def fixup_slot(self, slot):
        if not slot.material:
            return
 
        base, suffix = self.split_name(slot.material)
        if suffix is None:
            return
 
        try:
            base_mat = bpy.data.materials[base]
        except KeyError:
            print('Base material %r not found' % base)
            return
 
        slot.material = base_mat

class CleanDatas(Operator):
    """ Clean all the unused datas """
    bl_idname = "object.clean_unused_data"
    bl_label = "Clean Datas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        
        persistent_datas = [obj for obj in bpy.data.objects if obj.name not in bpy.context.scene.objects]
        
        if persistent_datas:
            selection = [obj for obj in bpy.context.selected_objects]
            
            bpy.ops.object.select_all(action = 'DESELECT')
             
            for obj in persistent_datas:
                bpy.context.scene.objects.link(obj)
                obj.select = True
            
            bpy.ops.object.delete()
            
            for obj in selection:
                obj.select = True
    
        for images in bpy.data.images:
            if not images.use_fake_user:
                if images.name != 'Render Result':
                    if not images.packed_file:
                        if not isfile(bpy.path.abspath(images.filepath)):
                            images.user_clear()
                            bpy.data.images.remove(images)
         
        data_list = ['objects', 'curves',
                    'texts', 'metaballs',
                    'lamps', 'cameras',
                    'fonts', 'lattices',
                    'meshes', 'groups',
                    'armatures', 'materials',
                    'textures', 'images',
                    'node_groups', 'grease_pencil',
                    'actions', 'libraries',
                    'movieclips', 'sounds', 
                    'speakers'
                    ] 
         
        for data in data_list:
            target_coll = eval("bpy.data." + data)
            for item in target_coll:
                if item.name != 'Render Result':
                    if item and item.users == 0:
                            target_coll.remove(item)
        
        return {'FINISHED'}      

# ------------------------------------------------------------------
#    EDIT ASSET  
# ------------------------------------------------------------------

settings = {
    "original_file": "",
    "file_to_edit": "",
    "is_saved": "",
    }
    
class EditAsset(bpy.types.Operator):
    """ Open the blend of the active preview """
    bl_idname = "object.edit_asset"
    bl_label = "Edit Asset"
    
    @classmethod
    def poll(cls, context):
        return settings["original_file"] == ""
    
    def check(self, context):
        return True
    
    def split_name(self, path):
        name = basename(path).split(".blend")[0]
     
        if not '.' in name:
            return name, None
     
        base, suffix = name.rsplit('.', 1)
        if not suffix.isdigit():
            return name, None
     
        return base, suffix
     
    def get_increment(self, path):
     
        base, suffix = self.split_name(path)
        if suffix is None:
            return base, "000"
        
        return base, suffix
    
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
        blend = context.window_manager.AssetM_previews.rsplit(".", 1)[0] + ".blend"
        filepath = join(library_path, AM.library_type, AM.libraries, AM.categories, "blends", blend)
        
        if AM.save_current_scn == 'yes':
            if bpy.data.filepath:
                if AM.save_type == 'over':
                    bpy.ops.wm.save_mainfile()
                else:
                    path = bpy.data.filepath.split(basename(bpy.data.filepath))[0]
                    base, suffix = self.get_increment(bpy.data.filepath)
                    filename = "%s.00%s.blend" % (base, int(suffix) + 1)
                    bpy.ops.wm.save_as_mainfile(filepath = join(path, filename))
            else:
                save_tmp()
         
            settings["is_saved"] = "True"
            
        if bpy.data.filepath:
            settings["original_file"] = bpy.data.filepath
            settings["is_saved"] = "True"
        else:
            tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
            settings["original_file"] = join(tmp_file, "am_backup.blend")
            
        settings["file_to_edit"] = bpy.path.abspath(filepath)

        bpy.ops.wm.open_mainfile(filepath = settings["file_to_edit"])
        
        print("Asset to edit opened !")
        
        return {"FINISHED"}
    
    def draw(self, context):
        AM = context.window_manager.asset_m
        layout = self.layout
        layout.label("Do you want to save your current scene ?")
        layout.prop(AM, "save_current_scn", text = " ", expand = True)
        if AM.save_current_scn == 'yes':
            if bpy.data.filepath:
                layout.prop(AM, "save_type", text = " ", expand = True)
            else:
                layout.label("No filepath. The scene will be save in the TMP folder", icon = 'ERROR')
     
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        AM.save_current_scn = 'yes'
        self.dpi_value = bpy.context.user_preferences.system.dpi
     
        return context.window_manager.invoke_props_dialog(self, width=self.dpi_value*5, height=100)
    
    

class BackToOriginal(bpy.types.Operator):
    """ Saving changes and return to the previous .blend """
    bl_idname = "wm.back_to_original"
    bl_label = "Save And Return To Original"

    @classmethod
    def poll(cls, context):
        return settings["original_file"] != ""

    def execute(self, context):
        
        filename = basename(settings["file_to_edit"])
        
        for obj in context.scene.objects:
            obj.select = True
        
        bpy.ops.wm.save_mainfile(filepath = settings["file_to_edit"])
        
        if settings["is_saved"] == "True":
            bpy.ops.wm.open_mainfile(filepath = settings["original_file"])
        
        if isfile(settings["file_to_edit"] + "1"):
            remove(settings["file_to_edit"] + "1")
        if isfile(settings["original_file"] + "1"):
            remove(settings["original_file"] + "1")
        
        settings["original_file"] = ""
        settings["file_to_edit"] = ""
        settings["is_saved"] = ""
        
        print("Back to original !")
        
        return {"FINISHED"}
    

class CancelChanges(bpy.types.Operator):
    """ Don't save the change and return to the previous .blend """
    bl_idname = "wm.cancel_changes"
    bl_label = "Just Return To Original"
 
    @classmethod
    def poll(cls, context):
        return settings["original_file"] != ""
    
    def execute(self, context):
        
        if settings["is_saved"] == "True":
            bpy.ops.wm.open_mainfile(filepath = settings["original_file"])
     
        if isfile(settings["file_to_edit"] + "1"):
            remove(settings["file_to_edit"] + "1")
        if isfile(settings["original_file"] + "1"):
            remove(settings["original_file"] + "1")
     
        settings["original_file"] = ""
        settings["file_to_edit"] = ""
        settings["is_saved"] = ""
        
        print("Cancel modifications !")
        
        return {"FINISHED"}

# ------------------------------------------------------------------
#    MOVE ASSET 
# ------------------------------------------------------------------

class MoveAsset(bpy.types.Operator):
    """ Move the asset in in the selected library and category """
    bl_idname = "object.move_asset"
    bl_label = "Move Asset"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        AM = bpy.context.window_manager.asset_m
        return AM.new_lib != AM.libraries or AM.new_cat != AM.categories
    
    def execute(self, context):
        WM = context.window_manager
        AM = WM.asset_m
        library_path = get_library_path()
        icon_path = get_directory("icons")
        favorites_path = get_directory("Favorites")
        asset = WM.AssetM_previews
        destination = join(library_path, AM.library_type, AM.new_lib, AM.new_cat)
        
        if AM.library_type != 'hdri':
            directory_path = get_directory("blends")
            file = get_blend(asset, directory_path)
            shutil.copy(join(directory_path, file), join(destination, "blends", file))
        else:
            directory_path = get_directory("IBL")
            file = get_ibl_from_thumbnail(asset, directory_path)
            shutil.copy(join(directory_path, file), join(destination, "IBL", file))
            
            if isfile(join(directory_path, asset.rsplit(".", 1)[0] + "_settings")):
                shutil.copy(join(directory_path, asset.rsplit(".", 1)[0] + "_settings"), join(destination, "IBL", asset.rsplit(".", 1)[0] + "_settings"))
            
        
        shutil.copy(join(icon_path, asset), join(destination, "icons", asset))
        
        if isdir(favorites_path) and isdir(join(destination, "Favorites")):
            if isfile(join(favorites_path, asset)):
                shutil.copy(join(favorites_path, asset), join(destination, "Favorites", asset))
        
        if isfile(join(destination, "icons", "EMPTY.png")):
            remove(join(destination, "icons", "EMPTY.png"))
            
        bpy.ops.object.remove_asset_from_lib()
        
        update_pcoll_preview()
        
        return {"FINISHED"}
        
# ------------------------------------------------------------------
#    PREPARE ASSET
# ------------------------------------------------------------------

class PrepareAsset(bpy.types.Operator):
    """ Parent the selection to a main object """
    bl_idname = "object.prepare_asset"
    bl_label = "Prepare Asset"
    bl_options = {"REGISTER"}
    
    type = bpy.props.EnumProperty(
        items = (('H_Ops', '', ''),
                 ('AM', '', '')),
                 default = 'H_Ops',
                 )

    @classmethod
    def poll(cls, context):
        return bpy.context.selected_objects

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        objs = [obj for obj in context.scene.objects if obj.select]
        
        if self.type == 'AM':
            bpy.ops.mesh.primitive_cube_add(radius = 4)
            bpy.context.active_object.name = "Main"
            
        else:
            bpy.context.active_object.name = "BB_" + bpy.context.active_object.name
            
        bpy.context.object.draw_type = 'WIRE'
        bpy.context.object.hide_render = True
        bpy.context.object.cycles_visibility.camera = False
        bpy.context.object.cycles_visibility.diffuse = False
        bpy.context.object.cycles_visibility.glossy = False
        bpy.context.object.cycles_visibility.transmission = False
        bpy.context.object.cycles_visibility.scatter = False
        bpy.context.object.cycles_visibility.shadow = False
        
        for obj in objs:
            obj.select = True
            if not obj.parent:
                bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = True)
        
        del(objs[:])
        
        return {"FINISHED"}
        
# ------------------------------------------------------------------
#    RENAME OBJECTS
# ------------------------------------------------------------------
        
class RenameObjects(bpy.types.Operator):
    """ Replace the "." by "_" in the object name for all selected objects """
    bl_idname = "object.rename_objects"
    bl_label = "Rename Objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        
        selection = [obj for obj in context.scene.objects if obj.select]
        
        for obj in selection:
            if "." in obj.name:
                obj.name = "_".join(obj.name.split("."))
            
        return {"FINISHED"}       

# ------------------------------------------------------------------
#    DEBUG 
# ------------------------------------------------------------------

class DebugPreview(Operator):
    """ Add a thumbnail if the render didn't go well, you can Delete or Update the Asset with better settings """
    bl_idname = "object.debug_preview"
    bl_label = "Debug"
    
    def execute(self, context):
        AM = bpy.context.window_manager.asset_m
        thumbnails_path = get_directory("icons")
        path_directory = get_directory("blends") if AM.library_type != 'hdri' else get_directory("IBL")
        addon_path = dirname(abspath(__file__))
        extention = (".jpg", ".jpeg", ".png")

        file_list = [blend.split(".blend")[0] for blend in listdir(path_directory) if blend.endswith(".blend")] if AM.library_type != 'hdri' else [ibl.rsplit(".", 1)[0] for ibl in listdir(path_directory)]
        
        tumbnail_list = [f.rsplit(".", 1)[0] for f in listdir(thumbnails_path) if f.endswith(extention)]
        
        source_file = join(addon_path, "icons", "error.png")
        
        for item in file_list:
            if item not in tumbnail_list:   
                shutil.copy(source_file, join(thumbnails_path, item + ".png"))
                
        if isfile(join(path_directory, "cleaning_asset.txt")):
            remove(join(path_directory, "cleaning_asset.txt"))

        else:
            for thumb in tumbnail_list:
                if thumb != "EMPTY":
                    if thumb not in file_list:
                        thumb_name = [f for f in listdir(thumbnails_path) if f.startswith(thumb)][0]
                        remove(join(thumbnails_path, thumb_name))

                        self.report({'INFO'}, "%s could not be added" % (thumb_name.rsplit(".", 1)[0]))
            
            update_pcoll_preview()
        AM.render_running = False
        AM.asset_adding_enabled = False
        AM.group_name = ""
        
        return {'FINISHED'} 