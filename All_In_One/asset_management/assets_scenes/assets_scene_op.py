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
 
import bpy
import shutil
from math import ceil
from mathutils import Vector
from bpy.types import Operator
from os import remove, listdir, rename
from os.path import join, isfile, isdir, abspath, realpath
from ..function_utils.get_path import (get_addon_preferences,
                                       get_directory,
                                       get_library_path,
                                       )
from ..function_utils.utils import (run_opengl_render, 
                                    opengl_rendering,
                                    get_asset_name,
                                    save_tmp
                                    )
from ..properties import CustomBrowserProperty
 

                    #-----------------------------#
                    #      ASSETS OPERATORS       #
                    #-----------------------------#
                    
                     
class AddAssetInLibrary(Operator):
    """ Add the active object in the asset library """
    bl_idname = "object.add_asset_in_library"
    bl_label = "Add asset in library"
    bl_options = {'REGISTER'}
 
    def modal(self, context, event): 
        AM = context.window_manager.asset_m 
 
        if AM.is_deleted:
 
            save_tmp()  #for more security , creating a backup of the scene in case the addition goes wrong
 
            if AM.render_type == 'opengl':
                run_opengl_render(self.icon_path, self.asset_name)
                bpy.ops.scene.delete()
                bpy.ops.object.remove_ogl_render()
                bpy.ops.object.clean_unused_data()
 
            blend_file = join(self.directory_path, self.asset_name + ".blend")
            
 
            bpy.ops.wm.save_as_mainfile(
                filepath = blend_file,
                relative_remap = True,
                copy=True
                )
 
            if isfile(blend_file):
 
                if self.fake_user:
                    for mat in self.fake_user:
                        mat.use_fake_user = True
 
                AM.adding_options = False
 
                bpy.ops.object.clean_asset_blend('INVOKE_DEFAULT')
 
                if AM.import_choise == 'link':
                    del(AM.groups_list[:])
                    del(AM.script_list[:])
                return {'FINISHED'}
            else:
                return {'PASS_THROUGH'} 
        else:
            return {'PASS_THROUGH'}   
 
 
    def invoke(self, context, event):
        AM = context.window_manager.asset_m
        self.addon_prefs = get_addon_preferences()
        self.asset_name = get_asset_name()
        self.directory_path = get_directory("blends")
        self.icon_path = get_directory("icons")
 
        bpy.ops.object.clean_unused_data()
 
        self.fake_user = [mat for mat in bpy.data.materials if mat.use_fake_user]
        if self.fake_user:
            for mat in bpy.data.materials:
                mat.use_fake_user = False
 
        if AM.replace_rename == 'replace':
            bpy.ops.object.remove_asset_from_lib()
 
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class CleanGroups(Operator):
    bl_idname = "object.clean_groups"
    bl_label = "Clean Groups"
    bl_options = {'REGISTER', 'UNDO'}
 
    def execute(self, context):
 
        for obj in context.selected_objects:
            bpy.context.scene.objects.active = obj
            for group in obj.users_group:
                self.fixup_groups(group)
 
        for obj in context.selected_objects:
            bpy.context.scene.objects.active = obj
            for group in obj.users_group:
                if '.' in group.name:
                    bpy.ops.group.objects_remove(group=group.name)
 
        for group in bpy.data.groups:
            if len(group.objects) == 0:
                bpy.data.groups.remove(group, do_unlink = True)
 
        return {"FINISHED"}
 
 
    def split_name(self, group):
        name = group.name
        if not '.' in name:
            return name, None
 
        base, suffix = name.rsplit('.', 1)
        if not suffix.isdigit():
            return name, None
 
        return base, suffix
 
    def fixup_groups(self, group):
 
        base, suffix = self.split_name(group)
        if suffix is None:
            return
 
        try:
            base_group = bpy.data.groups[base]
        except KeyError:
            print('Base group % not found' % base)
            return
 
        bpy.ops.object.group_link(group=base)
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class ImportScript(bpy.types.Operator):
    """ Import the script and run it if option enabled """
    bl_idname = "text.import_script"
    bl_label = "Import Script"
 
    script = bpy.props.StringProperty(default="")
 
    def execute(self, context):
        AM = context.window_manager.asset_m
        asset = context.window_manager.AssetM_previews.rsplit(".", 1)[0]
        blendfile = join(get_directory("blends"), asset + ".blend")
        text = None
 
        for text_block in bpy.data.texts:
            if text_block.name == self.script:
                text = text_block
                break
 
        if not text:
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                directory = join(blendfile, "Text")
                bpy.ops.wm.append(filename = self.script, directory = directory)
            text = self.script
 
        if AM.run_script:
            bpy.context.area.type = 'TEXT_EDITOR'
            bpy.context.space_data.text = bpy.data.texts[self.script]
            bpy.ops.text.run_script()
            bpy.context.area.type = 'VIEW_3D'
 
        return {"FINISHED"}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class AssetLink(Operator):
    bl_idname = "object.asset_m_link"
    bl_label = "Link"
    bl_options = {"REGISTER"}
 
    def execute(self, context):
        bpy.ops.object.make_links_data(type='OBDATA')
        bpy.ops.object.make_links_data(type='MODIFIERS')
 
        return {"FINISHED"}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class AssetUnlink(Operator):
    bl_idname = "object.asset_m_unlink"
    bl_label = "Unlink"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
 
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
        return {"FINISHED"}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class ObjectAddToSelection(Operator):
    ''' Add the selected object to selected faces '''
    bl_idname = "object.asset_m_add_to_selection"
    bl_label = "To selected faces"
 
    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) == 2
 
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj_main = context.active_object
        obj_list = list()
 
        obj1, obj2 = context.selected_objects
        OBJ2 = obj1 if obj2 == obj_main else obj2
 
        OBJ2.select=False
 
        bpy.ops.object.duplicate()
        bpy.context.active_object.name = "Dummy"
        obj = context.active_object
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
 
        mat_world = obj.matrix_world
        up = Vector((0, 0, 1))
        mesh = obj.data
 
        for face in mesh.polygons:
            if face.select:
                loc = mat_world * Vector(face.center)
                quat = face.normal.to_track_quat('Z', 'Y')
                quat.rotate(mat_world)
 
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = OBJ2
                OBJ2.select=True
                bpy.ops.object.duplicate()
 
                bpy.context.active_object.matrix_world *= quat.to_matrix().to_4x4()
 
                bpy.context.object.location = loc
 
                obj_list.append(bpy.context.active_object)
 
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["Dummy"].select=True
        bpy.ops.object.delete()
 
        bpy.context.scene.objects.active = OBJ2
        OBJ2.select = True
 
        for obj in obj_list:
            obj.select=True
            bpy.ops.object.asset_m_link()
            obj.select=False
 
        del(obj_list[:])
 
        bpy.context.space_data.transform_orientation = 'LOCAL'
 
        return {'FINISHED'}


                    #-----------------------------#
                    #      SCENES OPERATORS       #
                    #-----------------------------#
 
 
class AddSceneInLibrary(Operator):
    """ Add the active scene in the asset library """
    bl_idname = "object.add_scene_in_library"
    bl_label = "Add scene in library"
    bl_options = {'REGISTER'}
 
    def modal(self, context, event): 
        AM = context.window_manager.asset_m  
 
        if AM.is_deleted:
 
            save_tmp()  #for more security , creating a backup of the scene in case the addition goes wrong
 
            if AM.render_type == 'opengl':
                opengl_rendering(self.icon_path, self.asset_name)
                bpy.ops.object.remove_ogl_render()
 
            blend_file = join(self.directory_path, self.asset_name + ".blend")
            
            bpy.ops.wm.save_as_mainfile(
                filepath=blend_file,
                relative_remap = True,
                copy=True
                )
 
            if isfile(blend_file):
 
                AM.adding_options = False
 
                bpy.ops.object.clean_asset_blend('INVOKE_DEFAULT')
 
                return {'FINISHED'}
            else:
                return {'PASS_THROUGH'} 
        else:
            return {'PASS_THROUGH'}   
 
 
    def invoke(self, context, event): 
        AM = context.window_manager.asset_m
        self.addon_prefs = get_addon_preferences()
        self.asset_name = get_asset_name()
        self.directory_path = get_directory("blends")
        self.icon_path = get_directory("icons")
 
        if AM.replace_rename == 'replace':
            bpy.ops.object.remove_asset_from_lib()
 
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
 
# ------------------------------------------------------------------
#
# ------------------------------------------------------------------
 
class OpenActivePreview(bpy.types.Operator):
    """ Open the blenb of the active preview """
    bl_idname = "wm.open_active_preview"
    bl_label = "Open Active Preview"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return bpy.context.window_manager.AssetM_previews != "EMPTY.png"
    
    def execute(self, context):
        AM = context.window_manager.asset_m
        library_path = get_library_path()
#        load_ui = context.user_preferences.filepaths.use_load_ui
#        bpy.context.user_preferences.filepaths.use_load_ui = False

        blend_name = context.window_manager.AssetM_previews.rsplit(".", 1)[0] + ".blend"
 
        filepath = join(library_path, AM.library_type, AM.libraries, AM.categories, "blends", blend_name)
 
        bpy.ops.wm.open_mainfile(filepath = filepath)
 
#        bpy.context.user_preferences.filepaths.use_load_ui = load_ui
        return {"FINISHED"}
    

# ------------------------------------------------------------------
#    CUSTOM IMPORT 
# ------------------------------------------------------------------
    
        
class ASSETM_WM_custom_browser(Operator):
    """ Open a custom browser from the selected section of the active preview """
    bl_idname = "wm.assetm_custom_browser"
    bl_label = "Import / Link"
 
    propertyGroup = bpy.props.CollectionProperty(
        type = CustomBrowserProperty,
        )
    
    activeLayer = bpy.props.BoolProperty(
        default = False,
        )
        
    def invoke(self, context, event):
        self.propertyGroup.clear()
        WM = context.window_manager
        self.AM = WM.asset_m
        self.activeLayer = self.AM.active_layer
        library_path = get_library_path()
        self.blendfile = join(library_path, self.AM.library_type, self.AM.libraries, self.AM.categories, "blends", WM.AssetM_previews.rsplit(".", 1)[0] + ".blend")
        maxColumns = 6
        self.columns = 1
        self.start = 0
        self.steps = 0
        self.end = 0
 
        if self.AM.library_type == 'assets':
            self.libraries = {'Group':('groups', 'GROUP'),
                              'Image':('images', 'IMAGE_DATA'),
                              'Material':('materials', 'MATERIAL'),
                              'NodeTree':('node_groups', 'NODETREE'),
                              'Object':('objects', 'OBJECT_DATA'),
                              }
 
        else:
            self.libraries = {'Action':('actions', 'ACTION'),
                              'Brush':('brushes', 'BRUSH_DATA'),
                              'FreestyleLineStyle':('linestyles', 'LINE_DATA'),
                              'GPencil':('grease_pencil', 'GREASEPENCIL'),
                              'Group':('groups', 'GROUP'),
                              'Image':('images', 'IMAGE_DATA'),
                              'Ipo':('ipos', 'IPO'),
                              'Lamp':('lamps', 'LAMP'), 
                              'Lattice':('lattices', 'LATTICE_DATA'),
                              'Mask':('masks', 'BRUSH_TEXMASK'),
                              'Material':('materials', 'MATERIAL'),
                              'Mesh':('meshes', 'MESH_DATA'),
                              'Metaball':('metaballs', 'META_BALL'),
                              'MovieClip':('movieclips', 'FILE_MOVIE'),
                              'NodeTree':('node_groups', 'NODETREE'),
                              'Object':('objects', 'OBJECT_DATA'),
                              'ParticleSettings':('particles', 'PARTICLES'),
                              'Scene':('scenes', 'SCENE_DATA'),
                              'Sound':('sounds', 'SOUND'),
                              'Speaker':('speakers', 'SPEAKER'),
                              'Text':('texts', 'FILE_TEXT'),
                              'Texture':('textures', 'TEXTURE'),
                              'VFont':('fonts', 'FONT_DATA'),
                              'World':('worlds', 'WORLD'),
                              }
 
        with bpy.data.libraries.load(self.blendfile) as (data_from, data_to):
            target_coll = eval("data_from." + self.libraries[self.AM.datablock][0])
            for datas in target_coll:
                self.propertyGroup.add().name = datas
        
        self.dataCount = len(self.propertyGroup)
        
        # calcul du nombre de colonne en arrondissant a l'entier superieur (fonction ceil du module math)
        # pour une quantite de ligne maximum de 15 par colonne
        self.colCount = ceil(self.dataCount / 15)
        
        # si le nombre de colonne trouve est superieur au nombre maximum de colonne "autorise",
        # on limite le nombre de colonne au miximum de colonne autorise
        # repartition de la quantite de datas de facon homogene dans les colonnes
        # definition du premier stop pour changer de colonne
        if self.colCount > maxColumns:
            self.columns = maxColumns
            self.steps = ceil(self.dataCount / maxColumns)
            self.end = self.steps
        # sinon, le nombre de colonne sera le nombre trouve lors du calcul
        else:
            self.columns = self.colCount
            self.steps = ceil(self.dataCount / self.colCount)
            self.end = self.steps
              
        dpi_value = bpy.context.user_preferences.system.dpi
         
        return context.window_manager.invoke_props_dialog(self, width = dpi_value * 3 * self.columns, height = 100)
 
    def draw(self, context):
        layout = self.layout
        layout.label(self.AM.datablock, icon = self.libraries[self.AM.datablock][1])
        layout.prop(self, "activeLayer", text = "Active Layer")
        layout.separator()
        row = layout.row()
        for i in range(self.columns):
            col = row.column()
            box = col.box()
            for idx in range(self.start, self.end):
                box.prop(self.propertyGroup[idx], "active", text = self.propertyGroup[idx].name)
            
            self.start += self.steps
            if self.end + self.steps <= self.dataCount:
                self.end += self.steps
            else:
                self.end = self.dataCount
                
 
    def execute(self, context):
        
        dataToImport = [idx for idx in range(len(self.propertyGroup)) if self.propertyGroup[idx].active]
        
        if dataToImport:
            directory = join(self.blendfile, self.AM.datablock)

            files = list()
            
            for idx in range(len(self.propertyGroup)):
                if self.propertyGroup[idx].active:
                    files.append({"name":self.propertyGroup[idx].name})
                    files.append({"name":self.propertyGroup[idx].name + "Mesh"})
                    

            with bpy.data.libraries.load(self.blendfile) as (data_from, data_to):
                if self.AM.import_choise == 'append':
                    bpy.ops.wm.append(directory = directory, files = files, active_layer = self.activeLayer)
     
                else:
                    bpy.ops.wm.link(directory = directory, files = files, active_layer = self.activeLayer)
 
        return {"FINISHED"}

