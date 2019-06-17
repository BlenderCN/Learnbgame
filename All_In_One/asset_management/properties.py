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
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty
                       )
from bpy.types import OperatorFileListElement
from .library.utils import *
from .function_utils.update import *
from .assets_scenes.assets_functions import active_snap
from .materials.materials_functions import update_render_material_library
from .ibl.ibl_functions import update_projection


class CustomBrowserProperty(bpy.types.PropertyGroup):
    
    name = StringProperty()
        
    active = BoolProperty(
        default = False,
        )
    
    
class AssetManagementCollectionGroup(bpy.types.PropertyGroup):
    
    favourites_list = list()
    groups_list = list()
    group_settings = dict()
    visibility_settings = dict()
    script_list = list()
    ibl_to_thumb = list()
    material_rendering = list()
    
    previous_lib = StringProperty()
    
    library_type = EnumProperty(
            items = (('assets', "Assets", ""),
                     ('scenes', "Scenes", ""),
                     ('materials', "Materials", ""),
                     ('hdri', "HDRI", "")),
                     default = 'assets',
                     update = library_type_updater,
                     )

# -----------------------------------------------------------------------------
#   LIBRARY PROPERTIES
# -----------------------------------------------------------------------------
    
    library_list = list()

    lib_name = StringProperty(
        default = "",
        )
        
    libraries = EnumProperty(
        items = library_enum_items,
        update = category_updater,
        )
    
    show_prefs_lib = BoolProperty(
        default = False,
        description = "Display the options of the library",
        )
    
    delete_library_choise = EnumProperty(
        items = (('yes', "Yes", ""),
                 ('no', "No", "")),
                 default = 'no',
                 )
     
    rename_library = BoolProperty(
        default = False,
        )
    
    change_library_name = StringProperty(
        name = "Rename",
        default = "",
        )

# -----------------------------------------------------------------------------
#   CATEGORY PROPERTIES
# -----------------------------------------------------------------------------

    category_list = list()
    
    cat_name = StringProperty(
        default = "",
        )
        
    categories = EnumProperty(
        items = category_enum_items,
        update = category_updater,
        )
    
    show_prefs_cat = BoolProperty(
        default = False,
        description = "Display the options of the category",
        )
    
    delete_category_choise = EnumProperty(
        items = (('yes', "Yes", ""),
                 ('no', "No", "")),
                 default = 'no',
                 )
     
    rename_category = BoolProperty(
        default = False,
        )
     
    change_category_name = StringProperty(
        name = "Rename",
        default = ""
        )

# -----------------------------------------------------------------------------
#   ADDING OPTIONS PROPERTIES
# -----------------------------------------------------------------------------
   
    adding_options = BoolProperty(
        default = False,
        description = "Display adding options of the asset",
        update = update_render_material_library,
        )
        
    render_type = EnumProperty(
        items = render_type_enum_items
        )
    
    mat_thumb_type = EnumProperty(
        items = thumbnailer_enum_items
        )
    
    replace_rename = EnumProperty(
        items = (('replace', "Replace", "Replace the object in your by the active object"),
                 ('rename', "Rename", "Change the name of the object to add in your library")),
                 default = 'rename',
                 )
                 
    group_name = StringProperty(
        default = "",
        )
    
    ibl_type = EnumProperty(
        items = (('.hdr', "HDR", ".hdr importer"),
                 ('.exr', "EXR", ".exr importer")),
                 default = '.hdr',
                 )
    
    thumb_ext = EnumProperty(
        items = (('.jpeg', ".jpeg", ""),
                 ('.png', ".png", "")),
                 default = '.jpeg',
                 )
    
    existing_thumb = BoolProperty(
        default = True,
        description = "Uses existing thumbnails in the folder",
        )
    
    as_mat_scene = BoolProperty(
        default = False,
        description = "Save the scene as a material render scene",
        update = update_render_material_library,
        )
    
    multi_materials = BoolProperty(
        default = False,
        description = "Add all the materials of the active object in the library",
        )
                     
    # ---------------- #          
    #   RENDER MODE    #
    # ---------------- #
    
    add_subsurf = BoolProperty(
        default = False,
        description = "Thumbnail render with subsurf"
        )   
     
    add_smooth = BoolProperty(
        default = False,
        description = "Thumbnail render with smooth",
        )
    
    material_render = BoolProperty(
        default = True,
        description = "Disable to render with the objet materials",
        )
    
    # ---------------- #          
    #   OPENGL MODE    #
    # ---------------- #
    
    background_alpha = EnumProperty(
        items = (('SKY', "SKY", ''),
                 ('TRANSPARENT', "TRANSPARENT", '')),
                 default = 'SKY',
                 update = background_alpha,
                 )
    
    matcap_options = BoolProperty(
        default = True,
        description = "Matcap Options",
        )
    
    ao_options = BoolProperty(
        default = False,
        description = "Ambiant Occlusion Options",
        )    
    
    # ---------------- #          
    #   IMAGES MODE    #
    # ---------------- #
    
    image_type = EnumProperty(
        items = (('disk', "On disk", ''),
                 ('rendered', "Rendered", '')),
                 default = 'disk',
                 )

    custom_thumbnail_path = StringProperty(
        default = "",
        subtype = 'FILE_PATH',
        )
    
    custom_thumbnail = BoolProperty(
        default = False,
        description = "Choose your custom thumbnail",
        )
     
    render_name = StringProperty(
        default = "",
        )
        
# -----------------------------------------------------------------------------
#   PANEL OPTIONS PROPERTIES
# -----------------------------------------------------------------------------

    import_choise = EnumProperty(
        items = (('append', "Append", ""),
                 ('link', "Link", "")),
                 default = 'append',
                 update = import_choise_updater,
                 )
    
    save_current_scn = EnumProperty(
        items = (('yes', 'Yes', ""),
                 ('no', 'No', "")),
                 default = 'yes',
                 )
    
    save_type = EnumProperty(
        items = (('over', 'Replace', "Save over the existing save"),
                 ('increment', 'Increment', "Increment the save with .001, .002 ect...")),
                 default = 'increment'
                 )
                              
    favourites_enabled = BoolProperty(
        default = False,
        )
    
    custom_data_import = BoolProperty(
        default = False,
        description = "Activate the custom data import",
        )
        
    new_name = StringProperty(
        default = "",
        )
    
    rename_mat = StringProperty(
        default = "",
        update = update_material_name,
        )
        
    scene_name = StringProperty(
        default = "",
        )
    
    without_import = BoolProperty(
        default = False,
        description = "Do not import the Asset into the scene",
        )
    
    display_tools = BoolProperty(
        default = False,
        description = "Display AM Tools",
        )
        
    datablock_list = list()
    
    datablock = EnumProperty(
        items = datablock_enum_items,
        name = "Section",
        )
        
# -----------------------------------------------------------------------------
#   POPUP MENU PROPERTIES
# -----------------------------------------------------------------------------
    
    option_choise = EnumProperty(
        items = popup_options_enum_items)

    active_layer = BoolProperty(
        default = True,
        description = "Import the asset in active layer",
        )
    
    existing_material = BoolProperty(
        default = True,
        description = "Use the existing materials if they ever in the datas",
        )
    
    existing_group = BoolProperty(
        default = False,
        description = "Use the existing groups if they ever in the datas",
        )
    
    run_script = BoolProperty(
        default = False,
        description = "Run automatically the script when imported",
        )
    
    snap_enabled = BoolProperty(
        default = False,
        update = active_snap,
        description = "setup automaticaly snap to face",
        )
    
    snap_mod = StringProperty()
    
    tools_options = EnumProperty(
        items = (('assets', "Assets", "", 'MESH_MONKEY', 1),
                 ('debug', "Debug", "", 'CONSOLE', 2)),
                 default = 'assets',
                 )
    
    new_lib = EnumProperty(
        items = move_to_library_enum_item,
        description = "Display the destination library",
        )
    
    new_cat = EnumProperty(
        items = move_to_category_enum_item,
        description = "Display the destination category",
        )
                    
# -----------------------------------------------------------------------------
#   OPERATORS PROPERTIES
# -----------------------------------------------------------------------------

    asset_adding_enabled = BoolProperty(
        default = False,
        )
        
    render_running = BoolProperty(
        default = False,
        )

    cam_reso_X = IntProperty(
        default = 0,
        )
        
    cam_reso_Y = IntProperty(
        default = 0,
        )
    
    replace_asset = BoolProperty(
        default = False,
        )
    
    replace_multi = BoolProperty(
        default = False,
        )
    
    is_deleted = BoolProperty(
        default = True,
        )
        
    projection = EnumProperty(
        items = (('EQUIRECTANGULAR', 'Equirectangular', "Equirectangular or latitude-longitude projection"),
                 ('MIRROR_BALL', 'Mirror Ball', "Projection from an orthographic photo of a mirror ball")),
                 default = 'EQUIRECTANGULAR', 
                 name = "Projection",
                 update = update_projection,
                 )