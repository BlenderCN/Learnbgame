# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Amir Shehata
#  http://www.openmovie.com
#  amir.shehata@gmail.com

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import pathlib
import glob
import shutil
import subprocess
import sys
from gpu_extras.batch import batch_for_shader
import os
import fnmatch
import json
import random
from math import sin, cos, atan2, pi
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils, object_utils
from bpy.types import Panel, Operator, Menu, Macro, WindowManager
from bpy.utils import previews
from bpy.props import EnumProperty, StringProperty, BoolVectorProperty

bl_info = {
    "name": "YAAM",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > TOOLS > YAAM",
    "author": "Amir Shehata <amir.shehata@gmail.com>",
    "description": "Yet Another Asset Manager",
    "category": "Learnbgame",
}

# Preview collections
preview_collections = {}

OBJ_dir_name = 'Obj'
FBX_dir_name = 'Fbx'
TEXTURES_dir_name = 'Textures'
BLEND_dir_name = 'Blend'
M3DS_dir_name = '3ds'
TRASH_dir_name = 'Trash'

class YAAMAstMgrSettings(object):
    def __init__(self):
        self.version = (0, 1)
        self.astMgr_settings_fname = 'yaam.json'
        self.astMgr_addon_dir = os.path.dirname(__file__)
        self.settings_abs_file = os.path.join(self.astMgr_addon_dir,
                                              self.astMgr_settings_fname)

        # Add-on settings
        self.astMgr_settings = {
            'favs': [],
            'version': (0, 1),
            'cur_assets_dir': "",
            'previous_assets_directory': "",
            'cur_selected_asset_category': "",
            'cur_selected_asset_abs_path': "",
            'cur_assets_filter' : "",
            'cur_blend_import_op': "",
            'cur_selected_asset_mode' : "astmgrmode.browse_assets",
            'save_asset_dir': "",
            'save_asset_name': "",
            'org_src_dir': "",
            'org_dst_dir': "",
            'blender_bin_path': "",
        }

        self.supported_img_formats_match = ['*.jpg', '*.jpeg', '*.png', '*.svg', '*.bmp', '*.hdr']
        self.supported_img_formats = ['jpg', 'jpeg', 'png', 'svg', 'bmp', 'hdr']

        if os.path.exists(self.settings_abs_file):
            with open(self.settings_abs_file, 'r') as f:
                settings = json.load(f)
                if 'version' not in settings or tuple(settings['version']) != self.version:
                    with open(self.settings_abs_file, 'w') as f:
                        json.dump(self.astMgr_settings, f, ensure_ascii=False)
                else:
                    self.astMgr_settings = settings
        else:
            with open(self.settings_abs_file, 'w') as f:
                json.dump(self.astMgr_settings, f, ensure_ascii=False)

        if not self.get_cur_assets_dir():
            # try and find the default assets dir
            default_assets = os.path.join(os.path.dirname(__file__), "Assets")
            if os.path.isdir(default_assets):
                self.set_cur_assets_dir(default_assets)

    def get_supported_img_formats(self):
        return self.supported_img_formats

    def get_supported_img_formats_match(self):
        return self.supported_img_formats_match

    def get_addon_dir(self):
        return self.astMgr_addon_dir

    def get_favs(self):
        return self.astMgr_settings['favs']

    def set_favs(self, e):
        if e not in self.astMgr_settings['favs']:
            self.astMgr_settings['favs'].append(e)
            self.write_settings()

    def rm_favs(self, e):
        if e in self.astMgr_settings['favs']:
            self.astMgr_settings['favs'].remove(e)

    def get_cur_selected_asset_category(self):
        return self.astMgr_settings['cur_selected_asset_category']

    def set_cur_selected_asset_category(self, val):
        self.astMgr_settings['cur_selected_asset_category'] = val
        self.write_settings()

    def get_cur_selected_asset_mode(self):
        return self.astMgr_settings['cur_selected_asset_mode']

    def set_cur_selected_asset_mode(self, val):
        self.astMgr_settings['cur_selected_asset_mode'] = val
        self.write_settings()

    def get_cur_selected_asset_abs_path(self):
        return self.astMgr_settings['cur_selected_asset_abs_path']

    def set_cur_selected_asset_abs_path(self, val):
        self.astMgr_settings['cur_selected_asset_abs_path'] = val
        self.write_settings()

    def get_cur_assets_dir(self):
        return self.astMgr_settings['cur_assets_dir']

    def set_cur_assets_dir(self, val):
        self.astMgr_settings['cur_assets_dir'] = val
        self.write_settings()

    def get_previous_assets_directory(self):
        return self.astMgr_settings['previous_assets_directory']

    def set_previous_assets_directory(self, val):
        self.astMgr_settings['previous_assets_directory'] = val
        self.write_settings()

    def get_cur_assets_filter(self):
        return self.astMgr_settings['cur_assets_filter']

    def set_cur_assets_filter(self, val):
        self.astMgr_settings['cur_assets_filter'] = val
        self.write_settings()

    def get_cur_blend_import_op(self):
        return self.astMgr_settings['cur_blend_import_op']

    def set_cur_blend_import_op(self, val):
        self.astMgr_settings['cur_blend_import_op'] = val
        self.write_settings()

    def get_save_asset_name(self):
        return self.astMgr_settings['save_asset_name']

    def set_save_asset_name(self, val):
        self.astMgr_settings['save_asset_name'] = val
        self.write_settings()

    def get_save_asset_dir(self):
        return self.astMgr_settings['save_asset_dir']

    def set_save_asset_dir(self, val):
        self.astMgr_settings['save_asset_dir'] = val
        self.write_settings()

    def get_org_src_dir(self):
        return self.astMgr_settings['org_src_dir']
    def set_org_src_dir(self, val):
        self.astMgr_settings['org_src_dir'] = val
        self.write_settings()

    def get_org_dst_dir(self):
        return self.astMgr_settings['org_dst_dir']
    def set_org_dst_dir(self, val):
        self.astMgr_settings['org_dst_dir'] = val
        self.write_settings()

    def get_blender_bin_path(self):
        return self.astMgr_settings['blender_bin_path']
    def set_blender_bin_path(self, val):
        self.astMgr_settings['blender_bin_path'] = val
        self.write_settings()

    def write_settings(self):
        with open(self.settings_abs_file, 'w') as f:
            json.dump(self.astMgr_settings, f, ensure_ascii=False)

    def read_settings(self):
        return self.astMgr_settings

    def translate_category(self, cat):
        if cat == 'asset.all':
            return ''
        if cat == 'asset.fbx_file':
            return FBX_dir_name
        if cat == 'asset.3ds_file':
            return M3DS_dir_name
        if cat == 'asset.obj_file':
            return OBJ_dir_name
        if cat == 'asset.blend':
            return BLEND_dir_name
        if cat == 'asset.trash':
            return TRASH_dir_name
        return ''

    def get_or_create_asset_subdir(self, cat, create=False):
        category = self.translate_category(cat)
        if not category:
            return ''

        cur_dir = yaam.get_cur_assets_dir()
        if not cur_dir:
            return ''
        directory = os.path.join(yaam.get_cur_assets_dir(), category)
        if os.path.exists(directory) and not os.path.isdir(directory):
            return ''
        if not os.path.exists(directory):
            if create:
                os.makedirs(directory, exist_ok=True)
            else:
                return ''
        return directory


yaam = YAAMAstMgrSettings()


def get_favs_enum(self, context):
    favs = yaam.get_favs()
    if favs:
        return [(f, f, '') for f in favs]
    return [('Empty', 'Nothing to list', '')]


def handle_favs_update(self, context):
    scn = context.scene
    favs = scn.list_favorites
    if favs not in ['Empyt', '']:
        scn.assets_dir = favs
    return None


def update_dir(self, context):
    yaam.set_cur_assets_dir(context.scene.assets_dir)
    return None


def update_filter(self, context):
    yaam.set_cur_assets_filter(context.scene.assets_filter.decode("utf-8"))
    # force an update by setting the previous assets directory to ''
    # This way when we check it while building, we'll continue to build
    # there by the filter taking effect
    yaam.set_previous_assets_directory("")
    return None

def update_blender_bin_path(self, context):
    yaam.set_blender_bin_path(context.scene.yaam_blender_bin_path)
    return None

def update_save_asset_name(self, context):
    yaam.set_save_asset_name(context.scene.save_asset_name)
    return None


def update_save_asset_dir(self, context):
    yaam.set_save_asset_dir(context.scene.save_asset_dir)
    return None

class YAAM_OT_AddToFav(Operator):
    bl_idname = "yaam.add_to_fav"
    bl_label = "Add to favorites"
    bl_description = "Add the current folder to the favorites"

    def execute(self, context):
        scn = context.scene
        yaam.set_favs(scn.assets_dir)
        return {'FINISHED'}

class YAAM_OT_RmFromFav(Operator):
    bl_idname = "yaam.remove_from_fav"
    bl_label = "Remove from favorites"
    bl_description = "Remove the current folder from the favorites"

    def execute(self, context):
        scn = context.scene
        yaam.rm_favs(scn.assets_dir)
        return {'FINISHED'}


# When the append button is hit, display a subset of the items we
# can append/link. And then when you select that, we display yet again
# a list of other items available under the particular category.
# For example, say we have multiple collections, the first menu will look
# like:
#   collections
#   Objects
#   Meshes
#   Materials
#
# Then we select Collections. A second menu will pop up:
#   Collection 1
#   Collection 2
#   Collection 3
#
# The one selected will be appended to the scene and moved to the
# imported_assets collection.
#
# The Append or Link buttons will be menus.
# They drop down the list of options in the first menu above
# Each entry will have its own property class, which will
# attempt to import the selected item from the blend file
#

class YAAM_MT_blend_append_menu(Menu):
    #bl_idname = "yaam.blend_MT_append"
    bl_label = "Append"
    bl_description = "Append from a blend library"

    def draw(self, context):
        layout = self.layout
        yaam.set_cur_blend_import_op("append")
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("astblend.append_collections")
        layout.operator("astBlend.append_materials")
        layout.operator("astBlend.append_objects")
        layout.operator("astBlend.append_textures")
        layout.operator("astBlend.append_scenes")

class YAAM_MT_blend_link_menu(Menu):
    bl_label = "Link"
    bl_description = "Link from a blend library"

    def draw(self, context):
        yaam.set_cur_blend_import_op("link")
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("astblend.append_collections")
        layout.operator("astBlend.append_materials")
        layout.operator("astBlend.append_objects")
        layout.operator("astBlend.append_textures")
        layout.operator("astBlend.append_scenes")


def setActiveCollection(layer_collection, name):
    if not layer_collection.children:
        return
    for c in layer_collection.children:
        if c.name == name:
            bpy.context.view_layer.active_layer_collection = c
            return
        setActiveCollection(c, name)


def createAndSetImportCollection():
    if bpy.context.view_layer.layer_collection.children:
        main = bpy.context.view_layer.layer_collection.children[0]
        bpy.context.view_layer.active_layer_collection = main
    collection_name = "imported_assets"
    c = bpy.data.collections.get(collection_name)
    scene = bpy.context.scene
    if c is None:
        c = bpy.data.collections.new(collection_name)
        scene.collection.children.link(c)
    setActiveCollection(bpy.context.view_layer.layer_collection,
                        collection_name)


def blendAppendLinkElement(abs_path, elem_type, name, link=False):
    filepath = abs_path + "\\" + elem_type + "\\" + name
    directory = abs_path + "\\" + elem_type + "\\"
    action = bpy.ops.wm.link if link else bpy.ops.wm.append
    action(filepath=filepath, filename=name, directory=directory)


@classmethod
def poll_general(cls, context):
    if not yaam.get_cur_selected_asset_abs_path():
        return False
    elif os.path.isdir(yaam.get_cur_selected_asset_abs_path()):
        return False
    return True


def invoke_general(self, context, event):
    wm = context.window_manager
    wm.invoke_props_dialog(self)
    return {'RUNNING_MODAL'}

class YAAM_OT_AppendCollections(Operator):
    bl_idname = "astblend.append_collections"
    bl_label = "Collections"
    bl_description = "Append collections from a blend library"

    selection: BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    poll = poll_general
    invoke = invoke_general

    def __init__(self):
        self.collections_list = []

    def openBlendFileAndRead(self):
        self.collections_list = []
        asset_path = yaam.get_cur_selected_asset_abs_path()

        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            for name in data_from.collections:
                self.collections_list.append(name)

    def draw(self, conext):
        # open the blend file and read the collections
        # Make a list of all the collections in the file
        # Display them in the menu
        self.openBlendFileAndRead()
        layout = self.layout
        for idx, const in enumerate(self.collections_list):
            layout.prop(self, "selection", index=idx, text=const, toggle=False)

    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
        for index, flag in enumerate(self.selection):
            if flag:
                createAndSetImportCollection()
                link = False
                if yaam.get_cur_blend_import_op() == 'link':
                    link = True
                try:
                    blendAppendLinkElement(
                        yaam.get_cur_selected_asset_abs_path(),
                        "Collection",
                        self.collections_list[index],
                        link=link)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class YAAM_OT_AppendMaterials(Operator):
    bl_idname = "astblend.append_materials"
    bl_label = "Materials"
    bl_description = "Append materials from a blend library"

    selection: BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    poll = poll_general
    invoke = invoke_general

    def __init__(self):
        self.materials_list = []

    def openBlendFileAndRead(self):
        self.materials_list = []
        asset_path = yaam.get_cur_selected_asset_abs_path()

        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            for name in data_from.materials:
                self.materials_list.append(name)

    def draw(self, conext):
        # open the blend file and read the materials
        # Make a list of all the materials in the file
        # Display them in the menu
        self.openBlendFileAndRead()
        layout = self.layout
        for idx, const in enumerate(self.materials_list):
            layout.prop(self, "selection", index=idx, text=const, toggle=False)

    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
        for index, flag in enumerate(self.selection):
            if flag:
                createAndSetImportCollection()
                link = False
                if yaam.get_cur_blend_import_op() == 'link':
                    link = True

                try:
                    blendAppendLinkElement(
                        yaam.get_cur_selected_asset_abs_path(),
                        "Material",
                        self.materials_list[index],
                        link=link)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class YAAM_OT_AppendObjects(Operator):
    bl_idname = "astblend.append_objects"
    bl_label = "Objects"
    bl_description = "Append objects from a blend library"

    selection: BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    poll = poll_general
    invoke = invoke_general

    def __init__(self):
        self.objects_list = []

    def openBlendFileAndRead(self):
        self.objects_list = []
        asset_path = yaam.get_cur_selected_asset_abs_path()

        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            for name in data_from.objects:
                self.objects_list.append(name)

    def draw(self, conext):
        # open the blend file and read the objects
        # Make a list of all the objects in the file
        # Display them in the menu
        # TODO: don't open and read the file every draw cycle. do it only
        # once. Maybe have a flag and check if it has been set
        self.openBlendFileAndRead()
        layout = self.layout
        for idx, const in enumerate(self.objects_list):
            layout.prop(self, "selection", index=idx, text=const, toggle=False)

    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
        for index, flag in enumerate(self.selection):
            if flag:
                createAndSetImportCollection()
                link = False
                if yaam.get_cur_blend_import_op() == 'link':
                    link = True

                try:
                    blendAppendLinkElement(
                        yaam.get_cur_selected_asset_abs_path(),
                        "Object",
                        self.objects_list[index],
                        link=link)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class YAAM_OT_AppendTextures(Operator):
    bl_idname = "astblend.append_textures"
    bl_label = "Textures"
    bl_description = "Append textures from a blend library"

    selection: BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    poll = poll_general
    invoke = invoke_general

    def __init__(self):
        self.textures_list = []

    def openBlendFileAndRead(self):
        self.textures_list = []
        asset_path = yaam.get_cur_selected_asset_abs_path()

        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            for name in data_from.textures:
                self.textures_list.append(name)

    def draw(self, conext):
        # open the blend file and read the textures
        # Make a list of all the textures in the file
        # Display them in the menu
        self.openBlendFileAndRead()
        layout = self.layout
        for idx, const in enumerate(self.textures_list):
            layout.prop(self, "selection", index=idx, text=const, toggle=False)

    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
        for index, flag in enumerate(self.selection):
            if flag:
                createAndSetImportCollection()
                link = False
                if yaam.get_cur_blend_import_op() == 'link':
                    link = True

                try:
                    blendAppendLinkElement(
                        yaam.get_cur_selected_asset_abs_path(),
                        TEXTURES_dir_name,
                        self.textures_list[index],
                        link=link)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class YAAM_OT_AppendScenes(Operator):
    bl_idname = "astblend.append_scenes"
    bl_label = "Scenes"
    bl_description = "Append a collection from a blend library"

    selection: BoolVectorProperty(size=32, options={'SKIP_SAVE'})

    poll = poll_general
    invoke = invoke_general

    def __init__(self):
        self.scenes_list = []

    def openBlendFileAndRead(self):
        self.scenes_list = []
        asset_path = yaam.get_cur_selected_asset_abs_path()

        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            for name in data_from.scenes:
                self.scenes_list.append(name)

    def draw(self, conext):
        # open the blend file and read the scenes
        # Make a list of all the scenes in the file
        # Display them in the menu
        self.openBlendFileAndRead()
        layout = self.layout
        for idx, const in enumerate(self.scenes_list):
            layout.prop(self, "selection", index=idx, text=const, toggle=False)

    def execute(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
        for index, flag in enumerate(self.selection):
            if flag:
                createAndSetImportCollection()
                link = False
                if yaam.get_cur_blend_import_op() == 'link':
                    link = True

                try:
                    blendAppendLinkElement(
                        yaam.get_cur_selected_asset_abs_path(),
                        "Scene",
                        self.scenes_list[index],
                        link=link)
                except RuntimeError as e:
                    self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class YAAM_OT_import_ext(Operator):
    bl_idname = "yaam.import_ext"
    bl_label = "Import"
    bl_description = "Import external format"

    def import_scene(self, cb):
        if not yaam.get_cur_selected_asset_abs_path():
            return {'FINISHED'}
        if os.path.isdir(yaam.get_cur_selected_asset_abs_path()):
            self.report({'ERROR'}, "Can not import a folder")
            return {'FINISHED'}
        try:
            cb(filepath=yaam.get_cur_selected_asset_abs_path())
        except:
            self.report({'ERROR'}, "Failed to import file: ")
            return {'FINISHED'}
        bpy.ops.view3d.snap_selected_to_cursor()
        collection_name = "imported_assets"
        c = bpy.data.collections.get(collection_name)
        scene = bpy.context.scene
        if c is not None:
            c.objects.link(bpy.context.selected_objects[0])
        else:
            c = bpy.data.collections.new(collection_name)
            scene.collection.children.link(c)
            c.objects.link(bpy.context.selected_objects[0])
        return {'FINISHED'}

    def import_obj(self):
        return self.import_scene(bpy.ops.import_scene.obj)

    def import_blend(self):
        self.report({'ERROR'}, "Please explicitly select blend from category")
        return {'FINISHED'}

    def import_3ds(self):
        self.report({'ERROR'}, "File type currently unsupported")
        return {'FINISHED'}

    def import_fbx(self):
        return self.import_scene(bpy.ops.import_scene.fbx)

    def import_texture(self):
        img_path = yaam.get_cur_selected_asset_abs_path()
        if not img_path:
            self.report({'ERROR'}, "No image selected")
            return {'CANCELLED'}
        fname = pathlib.Path(img_path).parts[-1]
        if fname in bpy.data.images:
            self.report({'ERROR'}, "Asset is already imported")
            return {'CANCELLED'}
        bpy.data.images.load(img_path)
        bpy.data.images[fname].use_fake_user = True
        self.report({'INFO'}, "Successfully imported imaged and set fake user")
        return {'FINISHED'}

    def execute(self, context):
        if yaam.get_cur_selected_asset_category() == 'asset.all':
            cur_abs_path = yaam.get_cur_selected_asset_abs_path()
            if not cur_abs_path:
                self.report({'ERROR'}, "no asset selected to import")
                return {'CANCELLED'}
            fname = pathlib.Path(cur_abs_path).parts[-1]
            if fname.lower().endswith(tuple(yaam.get_supported_img_formats())):
                self.import_texture()
            elif fname.lower().endswith(('.blend')):
                self.import_blend()
            elif fname.lower().endswith(('.obj')):
                self.import_obj()
            elif fname.lower().endswith(('.3ds')):
                self.import_3ds()
            elif fname.lower().endswith(('.fbx')):
                self.import_fbx()
            else:
                self.report({'ERROR'}, "Unsupported File Format")
        elif yaam.get_cur_selected_asset_category() == 'asset.texture':
            self.import_texture()
        elif yaam.get_cur_selected_asset_category() == 'asset.3ds_file':
            self.import_3ds()
        elif yaam.get_cur_selected_asset_category() == 'asset.fbx_file':
            self.import_fbx()
        elif yaam.get_cur_selected_asset_category() == 'asset.obj_file':
            self.import_obj()
        elif yaam.get_cur_selected_asset_category() == 'asset.blend':
            self.import_blend()
        else:
            self.report({'ERROR'}, "Unsupported File Format")
        return {'FINISHED'}

class YAAM_OT_add_asset(Operator):
    bl_idname = "yaam.add_asset"
    bl_label = "Add"
    bl_description = "Add asset to selected Category"

    def save_asset(self, base_path, cat):
        if cat == 'asset.all':
            self.report({'ERROR'}, "Must specify category to save in")
        elif cat == 'asset.fbx_file':
            filename = base_path + ".fbx"
            bpy.ops.export_scene.fbx(filepath=filename)
        elif cat == 'asset.3ds_file':
            self.report({'ERROR'}, "3DS files are currently unsupported")
        elif cat == 'asset.obj_file':
            filename = base_path + ".obj"
            bpy.ops.export_scene.obj(filepath=filename)
        elif cat == 'asset.blend':
            filename = base_path + ".blend"
            bpy.ops.wm.save_as_mainfile(filepath=filename)

    def execute(self, context):
        # make sure the structure we need is there
        directory = yaam.get_or_create_asset_subdir(
            yaam.get_cur_selected_asset_category())
        if not directory:
            self.report({'ERROR'}, "Couldn't create asset directory")
            return ({'CANCELLED'})
        save_name = yaam.get_save_asset_name()
        if not save_name:
            self.report({'ERROR'}, "Must specify an asset name")
            return ({'CANCELLED'})
        if os.path.sep in save_name:
            self.report({'ERROR'}, "File name can not contain slashes")
            return ({'CANCELLED'})
        if '.' in save_name:
            self.report({'ERROR'}, "File name can not contain '.'")
            return ({'CANCELLED'})

        asset_save_dir = yaam.get_save_asset_dir()
        if asset_save_dir and directory not in asset_save_dir:
            self.report({'ERROR'},
                        "Specified save dir does not match category selected")
            return ({'CANCELLED'})

        abs_save_base_name = os.path.join(asset_save_dir, save_name)

        # get the active camera
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                camera = obj
        if camera is None:
            self.report({'ERROR'}, "No Camera in Scene")
            return ({'CANCELLED'})

        # store original values
        res_x = bpy.context.scene.render.resolution_x
        res_y = bpy.context.scene.render.resolution_y
        percentage = bpy.context.scene.render.resolution_percentage
        engine = bpy.context.scene.render.engine
        output = bpy.context.scene.render.filepath

        # set to EEVEE
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        # change the output to 128x128 100% resolution
        bpy.context.scene.render.resolution_x = 128
        bpy.context.scene.render.resolution_y = 128
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.render.filepath = abs_save_base_name + ".png"
        # Save the image and the file in the blend asset directory
        bpy.ops.render.render(write_still=True)
        # save according to category
        self.save_asset(abs_save_base_name,
                        yaam.get_cur_selected_asset_category())

        # restore original values
        bpy.context.scene.render.resolution_x = res_x
        bpy.context.scene.render.resolution_y = res_y
        bpy.context.scene.render.resolution_percentage = percentage
        bpy.context.scene.render.engine = engine
        bpy.context.scene.render.filepath = output

        self.report({'INFO'}, "Added asset successfully")
        # force an update
        yaam.set_previous_assets_directory("")
        return {'FINISHED'}

class YAAM_OT_rm_asset(Operator):
    bl_idname = "yaam.rm_asset"
    bl_label = "Remove"
    bl_description = "Remove asset from selected Category"

    def execute(self, context):
        # get or create the Trash directory
        asset_trash = yaam.get_or_create_asset_subdir(
            'asset.trash', create=True)
        if asset_trash is None:
            self.report({'ERROR'}, "Couldn't create trash directory")

        rm = False
        base_path_no_ext = os.path.splitext(
            yaam.get_cur_selected_asset_abs_path())[0]
        wildcard = base_path_no_ext + '.*'
        for file in glob.glob(wildcard):
            # move the asset and the png
            new_path = os.path.join(asset_trash, pathlib.Path(file).parts[-1])
            os.rename(file, new_path)
            rm = True

        if rm:
            self.report({'INFO'}, "Asset moved to trash successfully")
            # force an update
            yaam.set_previous_assets_directory("")
        else:
            self.report({'INFO'}, "Failed to remove Asset")
        return {'FINISHED'}

class YAAM_OT_refresh_asset(Operator):
    bl_idname = "yaam.refresh_asset"
    bl_label = "Refresh"
    bl_description = "Refresh assets"

    def execute(self, context):
        # force an update by setting the previous assets directory to ''
        # This way when we check it while building, we'll continue to build
        # there by the filter taking effect
        yaam.set_previous_assets_directory("")
        return {'FINISHED'}

class YAAM_OT_snap_image(Operator):
    bl_idname = "yaam.snap_picture"
    bl_label = "snap image"
    bl_description = "snap an image of the current asset"

    def execute(self, context):
        abs_path = yaam.get_cur_selected_asset_abs_path()
        if not abs_path:
            self.report({'ERROR'}, "no asset selected.")
            return ({'FINISHED'})

        for f in yaam.get_supported_img_formats_match():
            if fnmatch.fnmatch(abs_path, f):
                self.report({'ERROR'}, "Operation not allowed for images")
                return ({'FINISHED'})

        png_path = os.path.splitext(abs_path)[0]

        # store original values
        res_x = bpy.context.scene.render.resolution_x
        res_y = bpy.context.scene.render.resolution_y
        percentage = bpy.context.scene.render.resolution_percentage
        engine = bpy.context.scene.render.engine
        output = bpy.context.scene.render.filepath

        # set to EEVEE
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        # change the output to 128x128 100% resolution
        bpy.context.scene.render.resolution_x = 128
        bpy.context.scene.render.resolution_y = 128
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.render.filepath = png_path+".png"
        # Save the image and the file in the blend asset directory
        bpy.ops.render.render(write_still=True)

        # restore original values
        bpy.context.scene.render.resolution_x = res_x
        bpy.context.scene.render.resolution_y = res_y
        bpy.context.scene.render.resolution_percentage = percentage
        bpy.context.scene.render.engine = engine
        bpy.context.scene.render.filepath = output

        self.report({'INFO'}, "Image snapped successfully")
        # force an update by setting the previous assets directory to ''
        # This way when we check it while building, we'll continue to build
        # there by the filter taking effect
        yaam.set_previous_assets_directory("")
        return {'FINISHED'}

def asset_type_handler(self, context):
    yaam.set_cur_selected_asset_category(self.asset_type_dropdown)
    # force an update by setting the previous assets directory to ''
    # This way when we check it while building, we'll continue to build
    # there by the filter taking effect
    yaam.set_previous_assets_directory("")


def asset_mode_handler(self, context):
    yaam.set_cur_selected_asset_mode(self.asset_mode_expand)


# Asset Manager Mode
# Can be in browse or manage mode.
# In browse mode, you can browse and import
# In add mode, you can add assets to the library
class AstMgrMode(bpy.types.PropertyGroup):
    mode = [
        ("astmgrmode.browse_assets", "Browse", "Browse assets", '', 0),
        ("astmgrmode.mng_assets", "Manage", "Manage assets", '', 1),
    ]

    if yaam.get_cur_selected_asset_mode() == "":
        yaam.set_cur_selected_asset_mode("astmgrmode.browse_assets")

    asset_mode_expand: EnumProperty(
        items=mode,
        description="Asset Manager Mode",
        name="Asset Manager Mode",
        default=yaam.get_cur_selected_asset_mode(),
        update=asset_mode_handler,
        options={'HIDDEN'})


# Asset type drop down list
class AssetTypes(bpy.types.PropertyGroup):
    # The last entry int he array is displayed first
    asset_types = [
        ("asset.all", "all 3D assets", "all 3D assets", '', 5),
        ("asset.texture", "textures", "import textures", '', 4),
        ("asset.3ds_file", "3ds", "import 3ds into scene", '', 3),
        ("asset.fbx_file", "fbx", "import fbx into scene", '', 2),
        ("asset.obj_file", "obj", "import obj into scene", '', 1),
        ("asset.blend", "blend", "link or append blends", '', 0),
    ]

    if yaam.get_cur_selected_asset_category() == "":
        yaam.set_cur_selected_asset_category("asset.all")

    asset_type_dropdown: EnumProperty(
        items=asset_types,
        description="select asset type to import",
        name="Category",
        default=yaam.get_cur_selected_asset_category(),
        update=asset_type_handler)


class YAAM_OT_organize(Operator):
    bl_idname = "yaam_gen.organize"
    bl_label = "Organize"
    bl_description = "Organize assets"

    def __init__(self):
        self.src = ''
        self.dst = ''

    def get_fnames(self, dirName, fname, file_type):
        subdir = dirName.replace(self.src, '')
        old_fname = os.path.join(dirName, fname)
        new_fname = ''
        if subdir:
            new_subdir = os.path.join(self.dst, file_type, subdir)
            try:
                os.makedirs(new_subdir, exist_ok=True)
            except:
                e = sys.exc_info()[0]
                self.report({'ERROR'}, str(e))
                return '', ''
            new_fname = os.path.join(new_subdir, fname)
        else:
            new_fname = os.path.join(self.dst, file_type, fname)

        return old_fname, new_fname

    def do_import_export(self, file_type, obj_path, png_render_path):
        helperPyPath = os.path.join(yaam.get_addon_dir(), "import_export.py")
        b3d = yaam.get_blender_bin_path()
        if not b3d:
            b3d = "blender"
        try:
            cmd = [b3d, "-b", "-P", helperPyPath, "--", obj_path, file_type,
                   png_render_path]
            subprocess.call(cmd)
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))


    def handle_blend(self, dirName, fname):
        old_fname, new_fname = self.get_fnames(dirName, fname, BLEND_dir_name)
        helperPyPath = os.path.join(yaam.get_addon_dir(), "blend_organize.py")
        png_path = os.path.splitext(new_fname)[0]+".png"
        b3d = yaam.get_blender_bin_path()
        if not b3d:
            b3d = "blender"
        try:
            cmd = [b3d, old_fname, "-b", "-P", helperPyPath, "--", old_fname,
                   png_path]
            subprocess.call(cmd)
        except FileNotFoundError as e:
            self.report({'ERROR'}, str(e))
            return
        shutil.copy2(old_fname, new_fname)

    def handle_common(self, dirName, fname, file_type):
        old_fname, new_fname = self.get_fnames(dirName, fname, file_type)
        if not old_fname or not new_fname:
            self.report({'ERROR'}, "Failed to copy "+file_type+" file")
            return ({'CANCELLED'})
        png_path = os.path.splitext(new_fname)[0]+".png"
        self.do_import_export(file_type, old_fname, png_path)
        shutil.copy2(old_fname, new_fname)

    def handle_obj(self, dirName, fname):
        self.handle_common(dirName, fname, OBJ_dir_name)

    def handle_fbx(self, dirName, fname):
        self.handle_common(dirName, fname, FBX_dir_name)

    def handle_img(self, dirName, fname):
        # Texture files can just be copied over
        old_fname, new_fname = self.get_fnames(dirName, fname, TEXTURES_dir_name)
        shutil.copy2(old_fname, new_fname)
        return ({'FINISHED'})

    def organize(self):
        src = self.src
        dst = self.dst

        # first some sanity checks
        if not os.path.isdir(src):
            self.report({'ERROR'}, "src path is not valid")
            return ({'CANCELLED'})

        if not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)
        elif not os.path.isdir(dst):
            self.report({'ERROR'}, "dst path is not valid")
            return ({'CANCELLED'})

        # walk each file in the src dir
        for dirName, subdirList, fileList in os.walk(src):
            # examine the file extension
            for fname in fileList:
                if fname.lower().endswith("blend"):
                    self.handle_blend(dirName, fname)
                elif fname.lower().endswith("obj"):
                    self.handle_obj(dirName, fname)
                elif fname.lower().endswith("fbx"):
                    self.handle_fbx(dirName, fname)
                elif fname.lower().endswith(tuple(yaam.get_supported_img_formats())):
                    self.handle_img(dirName, fname)
        return ({'FINISHED'})

    def execute(self, context):
        scn = context.scene
        self.src = scn.yaam_gen_source_dir
        if not self.src.endswith(os.path.sep):
            self.src = self.src+os.path.sep
        yaam.set_org_src_dir(self.src)
        self.dst = scn.yaam_gen_dest_dir
        if not self.dst.endswith(os.path.sep):
            self.dst = self.dst+os.path.sep
        yaam.set_org_dst_dir(self.dst)

        self.organize()

        # force an update by setting the previous assets directory to ''
        # This way when we check it while building, we'll continue to build
        # there by the filter taking effect
        if self.dst == yaam.get_cur_assets_dir():
            yaam.set_previous_assets_directory("")
        return {'FINISHED'}

class YAAM_PT_astGen(Panel):
    bl_label = "YAAM Organize"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'YAAM Manager'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        wm = context.window_manager
        col = layout.column(align=True)

        col.label(text="Blender 3D binary path:")
        col.prop(scn, "yaam_blender_bin_path", text='')
        col.label(text="Select source folder")
        col.prop(scn, "yaam_gen_source_dir", text="")
        col.label(text="Select destination folder")
        col.prop(scn, "yaam_gen_dest_dir", text="")
        col = layout.column(align=True)
        col.operator('yaam_gen.organize', icon = 'ASSET_MANAGER')

# N Panels
class YAAM_PT_astMgr(Panel):
    bl_label = "YAAM"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'YAAM Manager'

    def add_preview(self, wm, row):
        if yaam.get_cur_selected_asset_category() == 'asset.all':
            row.template_icon_view(wm, "yaam_category_all",
                                   show_labels=True, scale=5)
        elif yaam.get_cur_selected_asset_category() == 'asset.blend':
            row.template_icon_view(wm, "yaam_category_blend",
                                   show_labels=True, scale=5)
        elif yaam.get_cur_selected_asset_category() == 'asset.texture':
            row.template_icon_view(wm, "yaam_category_texture",
                                   show_labels=True, scale=5)
        elif yaam.get_cur_selected_asset_category() == 'asset.3ds_file':
            row.template_icon_view(wm, "yaam_category_3ds",
                                   show_labels=True, scale=5)
        elif yaam.get_cur_selected_asset_category() == 'asset.fbx_file':
            row.template_icon_view(wm, "yaam_category_fbx",
                                   show_labels=True, scale=5)
        elif yaam.get_cur_selected_asset_category() == 'asset.obj_file':
            row.template_icon_view(wm, "yaam_category_obj",
                                   show_labels=True, scale=5)

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        wm = context.window_manager
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(scn.asset_mode_list, "asset_mode_expand", expand=True)
        col = layout.column(align=True)
        row = col.row(align=True)
        directory = bpy.path.abspath(scn.assets_dir)
        if os.path.exists(directory):
            if not directory in yaam.get_favs():
                row.operator("yaam.add_to_fav", text='', icon='SOLO_ON')
            else:
                row.operator("yaam.remove_from_fav", text='', icon='X')
        row.prop(scn, "assets_dir", text = '')
        col.label(text="Select Asset type:")
        col.prop(scn.asset_type_list, "asset_type_dropdown")
        col.label(text="Assets Filter:")
        col.prop(scn, "assets_filter", text='')
        row = layout.row()
        self.add_preview(wm, row)
        col = row.column(align=True)
        if yaam.get_cur_selected_asset_mode() == 'astmgrmode.mng_assets':
                col.operator('yaam.add_asset', text='', icon='ADD')
                col.operator('yaam.rm_asset', text='', icon='REMOVE')
        else:
                col.operator('yaam.refresh_asset', text='', icon='FILE_REFRESH')
        col.prop(scn, 'list_favorites', text='', icon='SOLO_OFF', icon_only=True)

        col = layout.column(align=True)
        row = col.row(align=False)
        if (yaam.get_cur_selected_asset_category() == 'asset.blend') and \
           (yaam.get_cur_selected_asset_mode() == 'astmgrmode.browse_assets'):
            row.menu('YAAM_MT_blend_link_menu', icon = 'LINKED')
            row.menu('YAAM_MT_blend_append_menu', icon = 'APPEND_BLEND')
        elif (yaam.get_cur_selected_asset_category() != 'asset.blend') and \
             (yaam.get_cur_selected_asset_mode() == 'astmgrmode.browse_assets'):
            row.operator('yaam.import_ext', icon = 'IMPORT')

        if yaam.get_cur_selected_asset_mode() == 'astmgrmode.mng_assets':
            col.row(align=True)
            col.label(text="Save asset folder:")
            col.prop(scn, "save_asset_dir", text='')
            col.label(text="Save asset name:")
            col.prop(scn, "save_asset_name", text='')
            col = layout.column(align=True)
            col.operator('yaam.snap_picture', icon='IMAGE')


classes = [
    YAAM_PT_astMgr,
    YAAM_PT_astGen,
    YAAM_OT_organize,
    YAAM_MT_blend_link_menu,
    YAAM_MT_blend_append_menu,
    YAAM_OT_AppendCollections,
    YAAM_OT_AppendMaterials,
    YAAM_OT_AppendObjects,
    YAAM_OT_AppendTextures,
    YAAM_OT_AppendScenes,
    YAAM_OT_import_ext,
    YAAM_OT_add_asset,
    YAAM_OT_snap_image,
    YAAM_OT_rm_asset,
    YAAM_OT_refresh_asset,
    YAAM_OT_AddToFav,
    YAAM_OT_RmFromFav,
    AstMgrMode,
    AssetTypes,
]


# append_to_previews
#   If this is a directory then load the default directory icon
#   If this is a file, then try and find an image file with the same name
#   If no image file found load the default icon
#   Append to previews
def append_to_previews(pcoll, rootDir, abs_path, previews_list, idx):
    thumb = None

    if os.path.isdir(abs_path):
        #load icon
        default_icon_path = os.path.join(os.path.join(yaam.get_addon_dir(), "DefIcons"), "folder.png")
        if default_icon_path in pcoll:
            thumb = pcoll[default_icon_path]
        else:
            thumb = pcoll.load(default_icon_path, default_icon_path, 'IMAGE')
        display_name = pathlib.Path(abs_path).parts[-1]
        previews_list.append((abs_path, display_name, abs_path, thumb.icon_id,
                              idx))
    else:
        # find image
        name_no_ext = os.path.splitext(abs_path)[0]
        display_name = pathlib.Path(name_no_ext).parts[-1]
        name_pattern = name_no_ext + '.*'
        file_list = glob.glob(name_pattern)
        found = False
        for fname in file_list:
            if fname.lower().endswith(tuple(yaam.get_supported_img_formats())):
                #load image
                found = True
                if fname in pcoll:
                    pcoll[fname].reload()
                    thumb = pcoll[fname]
                else:
                    thumb = pcoll.load(
                        fname, fname, 'IMAGE', force_reload=True)
                previews_list.append((abs_path, display_name, abs_path,
                                     thumb.icon_id, idx))
                break
        if not found:
            default_icon_path = os.path.join(os.path.join(yaam.get_addon_dir(), "DefIcons"), "nothumbnail.png")
            if default_icon_path in pcoll:
                thumb = pcoll[default_icon_path]
            else:
                thumb = pcoll.load(default_icon_path, default_icon_path,
                                   'IMAGE')
            previews_list.append((abs_path, display_name, abs_path,
                                  thumb.icon_id, idx))


# traverse_dir
#   Traverse directory and for each entry including
#   subdirectories call the cb_fn with pcoll and the filename/directory
#   which matches the filters provided
def traverse_dir(rootDir, assetDir, category_filter, asset_filter, pcoll,
                 cb_fn):
    i = 0
    previews_list = []
    for dirName, subdirList, fileList in os.walk(assetDir):
        matched_subdir = False
        p = pathlib.Path(dirName)
        subdir = p.parts[-1]
        if (subdir.lower() == 'deficons' or subdir.lower() == 'trash'):
            continue
        if (asset_filter and fnmatch.fnmatch(subdir, asset_filter)):
            matched_subdir = True
        subdiradded = False
        for fname in fileList:
            match_cat_filter = False
            for f in category_filter:
                if fnmatch.fnmatch(fname, f):
                    match_cat_filter = True
                    break
            if not match_cat_filter:
                continue
            if asset_filter and \
               not fnmatch.fnmatch(fname, asset_filter) and \
               not matched_subdir:
                continue
            # matched a subdirectory
            if not subdiradded:
                i = i + 1
                cb_fn(pcoll, rootDir, dirName, previews_list, i)
                subdiradded = True
            i = i + 1
            cb_fn(pcoll, rootDir, os.path.join(dirName, fname), previews_list,
                  i)
    return previews_list


# build_enum_preview
#   Find the exact directory
#   If it doesn't exist then return empty preview
#   Otherwise Traverse the directory recursively
#   examine each file defined by the category
#   Check if the file matches the filter and if it doesn't ignore.
#   populate the preview
def build_enum_preview(pcoll, category, category_filter):
    if not yaam.get_cur_assets_dir():
        return [], False

    if yaam.get_previous_assets_directory() == yaam.get_cur_assets_dir():
        # nothing has changed no need to rebuild
        return pcoll, False

    # set the previous assets directory to avoid having to rebuild
    # for no reason
    yaam.set_previous_assets_directory(yaam.get_cur_assets_dir())

    directory = os.path.join(yaam.get_cur_assets_dir(), category)

    if directory and os.path.exists(directory):
        return traverse_dir(
            yaam.get_cur_assets_dir(), directory, category_filter,
            yaam.get_cur_assets_filter(), pcoll, append_to_previews), True

    return [], True

def set_default_view(new_list):
    default = ''
    selected = yaam.get_cur_selected_asset_abs_path()
    if len(new_list):
        default = new_list[0][0]
        if os.path.isdir(default):
            # find an actual asset
            for l in new_list:
                if not os.path.isdir(l[0]):
                    if not default or os.path.isdir(default):
                        default = l[0]
                    if l[0] == selected:
                        default = l[0]
                        break
    return default

def yaam_hndlr_enum_previews_category_all(self, context):
    pcoll = preview_collections["asset_category_all"]
    new_list, changed = build_enum_preview(
        pcoll, '', [".blend", "*.obj", "*.fbx", "*.3ds"])
    if (changed):
        pcoll.yaam_category_all = new_list
        if len(new_list):
            context.window_manager.yaam_category_all = set_default_view(new_list)
    return pcoll.yaam_category_all

def yaam_hndlr_enum_previews_category_blend(self, context):
    pcoll = preview_collections["asset_category_blend"]
    new_list, changed = build_enum_preview(pcoll, BLEND_dir_name, ["*.blend"])
    if (changed):
        pcoll.yaam_category_blend = new_list
        if len(new_list):
            context.window_manager.yaam_category_blend = set_default_view(new_list)
    return pcoll.yaam_category_blend

def yaam_hndlr_enum_previews_category_obj(self, context):
    pcoll = preview_collections["asset_category_obj"]
    new_list, changed = build_enum_preview(pcoll, OBJ_dir_name, ["*.obj"])
    if (changed):
        pcoll.yaam_category_obj = new_list
        if len(new_list):
            context.window_manager.yaam_category_obj = set_default_view(new_list)
    return pcoll.yaam_category_obj

def yaam_hndlr_enum_previews_category_texture(self, context):
    pcoll = preview_collections["asset_category_texture"]
    new_list, changed = build_enum_preview(pcoll, TEXTURES_dir_name,
                            yaam.get_supported_img_formats_match())
    if (changed):
        pcoll.yaam_category_texture = new_list
        if len(new_list):
            context.window_manager.yaam_category_texture = set_default_view(new_list)
    return pcoll.yaam_category_texture

def yaam_hndlr_enum_previews_category_3ds(self, context):
    pcoll = preview_collections["asset_category_3ds"]
    new_list, changed = build_enum_preview(pcoll, '3ds', ["*.3ds"])
    if (changed):
        pcoll.yaam_category_3ds= new_list
        if len(new_list):
            context.window_manager.yaam_category_3ds = set_default_view(new_list)
    return pcoll.yaam_category_3ds

def yaam_hndlr_enum_previews_category_fbx(self, context):
    pcoll = preview_collections["asset_category_fbx"]
    new_list, changed = build_enum_preview(pcoll, FBX_dir_name, ["*.fbx"])
    if (changed):
        pcoll.yaam_category_fbx = new_list
        if len(new_list):
            context.window_manager.yaam_category_fbx = set_default_view(new_list)
    return pcoll.yaam_category_fbx


def astmgr_hndlr_selected_asset(self, context):
    if yaam.get_cur_selected_asset_category() == "asset.all":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_all'))
    elif yaam.get_cur_selected_asset_category() == "asset.texture":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_texture'))
    elif yaam.get_cur_selected_asset_category() == "asset.3ds_file":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_3ds'))
    elif yaam.get_cur_selected_asset_category() == "asset.fbx_file":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_fbx'))
    elif yaam.get_cur_selected_asset_category() == "asset.obj_file":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_obj'))
    elif yaam.get_cur_selected_asset_category() == "asset.blend":
        yaam.set_cur_selected_asset_abs_path(getattr(self, 'yaam_category_blend'))
    else:
        yaam.set_cur_selected_asset_abs_path("")
    return None


# TODO: Need to set the default icon (or something) in the preview on
# startup. For some reason, after loading the images nothing appears in
# the preview. I need to actually click and select. I should at least be
# able to see the first in the list
def setup_preview_collections(mgr):
    global preview_collections

    mgr.yaam_category_dir_all = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_all = EnumProperty(
        items=yaam_hndlr_enum_previews_category_all,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_all = ""
    pcoll.yaam_category_all = ()
    preview_collections["asset_category_all"] = pcoll

    mgr.yaam_category_dir_blend = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_blend = EnumProperty(
        items=yaam_hndlr_enum_previews_category_blend,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_blend = ""
    pcoll.yaam_category_blend = ()
    preview_collections["asset_category_blend"] = pcoll

    mgr.yaam_category_dir_obj = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_obj = EnumProperty(
        items=yaam_hndlr_enum_previews_category_obj,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_obj = ""
    pcoll.yaam_category_obj = ()
    preview_collections["asset_category_obj"] = pcoll

    mgr.yaam_category_dir_3ds = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_3ds = EnumProperty(
        items=yaam_hndlr_enum_previews_category_3ds,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_3ds = ""
    pcoll.yaam_category_3ds = ()
    preview_collections["asset_category_3ds"] = pcoll

    mgr.yaam_category_dir_fbx = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_fbx = EnumProperty(
        items=yaam_hndlr_enum_previews_category_fbx,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_fbx = ""
    pcoll.yaam_category_fbx = ()
    preview_collections["asset_category_fbx"] = pcoll

    mgr.yaam_category_dir_texture = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")
    mgr.yaam_category_texture = EnumProperty(
        items=yaam_hndlr_enum_previews_category_texture,
        update=astmgr_hndlr_selected_asset)
    pcoll = previews.new()
    pcoll.yaam_category_dir_texture = ""
    pcoll.yaam_category_texture = ()
    preview_collections["asset_category_texture"] = pcoll


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.assets_dir = StringProperty(
        name="Asset Folder",
        subtype='DIR_PATH',
        default=yaam.get_cur_assets_dir(),
        update=update_dir,
        description='Path to the folder containing assets.')

    yaam.set_previous_assets_directory("")

    bpy.types.Scene.assets_filter = StringProperty(
        name="Assets Filter",
        subtype='BYTE_STRING',
        default=yaam.get_cur_assets_filter(),
        update=update_filter,
        description='Filter the assets')

    bpy.types.Scene.save_asset_dir = StringProperty(
        name="Asset Directory",
        subtype='DIR_PATH',
        default=os.path.join(
            yaam.get_cur_assets_dir(),
            yaam.translate_category(yaam.get_cur_selected_asset_category())),
        update=update_save_asset_dir,
        description='Save Asset SubDir')

    bpy.types.Scene.save_asset_name = StringProperty(
        name="Asset Name",
        subtype='FILE_NAME',
        default="",
        update=update_save_asset_name,
        description='Save Asset SubDir')

    bpy.types.Scene.asset_type_list = bpy.props.PointerProperty(
        type=AssetTypes)
    bpy.types.Scene.asset_mode_list = bpy.props.PointerProperty(
        type=AstMgrMode)
    bpy.types.Scene.list_favorites = EnumProperty(
        name='Favorites', items=get_favs_enum, update=handle_favs_update)

    bpy.types.Scene.yaam_gen_source_dir = StringProperty(
        name="YAAM org source dir",
        subtype='DIR_PATH',
        default=yaam.get_org_src_dir(),
        description='Source directory to organize'
    )

    bpy.types.Scene.yaam_gen_dest_dir = StringProperty(
        name="YAAM org dest dir",
        subtype='DIR_PATH',
        default=yaam.get_org_dst_dir(),
        description='Destination directory to organize'
    )

    bpy.types.Scene.yaam_blender_bin_path = StringProperty(
        name="Path to blender binary",
        subtype='FILE_PATH',
        update=update_blender_bin_path,
        default=yaam.get_blender_bin_path(),
        description='Path to blender binary'
    )

    setup_preview_collections(WindowManager)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Scene.assets_dir
    del bpy.types.Scene.assets_filter
    del bpy.types.Scene.save_asset_dir
    del bpy.types.Scene.save_asset_name
    del bpy.types.Scene.asset_mode_list
    del bpy.types.Scene.asset_type_list
    del bpy.types.Scene.list_favorites
    del bpy.types.Scene.yaam_gen_source_dir
    del bpy.types.Scene.yaam_gen_dest_dir
    del bpy.types.Scene.yaam_blender_bin_path


if __name__ == "__main__":
    register()
