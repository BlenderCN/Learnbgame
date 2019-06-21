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
from os import listdir
from os.path import join, isdir, basename
from ..function_utils.get_path import (get_library_path,
                                       get_addon_path
                                       )
from ..materials.materials_functions import get_custom_material_render_scene
                                


def library_enum_items(self, context):
    """ Returns the list of the libraries in the Asset management folder """
    
    AM = bpy.context.window_manager.asset_m
    # In case the libraries are stored on a server,
    # we retrieves the list of libraries to store them in a
    # variable and avoid the risk of latency.
    # So, if they are not stored, we get them and store.
    if not AM.library_list:
        
        library_path = get_library_path()

        libraries = [(lib, lib, "") for lib in listdir(join(library_path, AM.library_type)) if isdir(join(library_path, AM.library_type, lib))]
        
        for lib in libraries:
            AM.library_list.append(lib[0])
        
        return libraries
    
    # If they are already stored, we just check the variable
    else:
        return [(lib, lib, "") for lib in AM.library_list]

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def category_enum_items(self, context):
    """ Returns the list of the categories in the library folder """
    
    AM = bpy.context.window_manager.asset_m
    if not AM.category_list:
        library_path = get_library_path()
        
        categories = [(cat, cat, "") for cat in listdir(join(library_path, AM.library_type, AM.libraries)) if isdir(join(library_path, AM.library_type, AM.libraries, cat))]
        
        for cat in categories:
            AM.category_list.append(cat[0])
        
        return categories
    
    else:
        return [(cat, cat, "") for cat in AM.category_list]

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
def popup_options_enum_items(self, context):
    """ Returns the different options for the popup options """
    
    AM = bpy.context.window_manager.asset_m
    options = [('tools', "Tools", ""), ('display', "Display", "")]
    
    if AM.library_type in ['assets', 'materials']:
        options.insert(1, ('import', "Import", ""))
    
    return options

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def render_type_enum_items(self, context):
    """ Returns the different type of rendering thumbnails """
    
    AM = bpy.context.window_manager.asset_m
    render_type = [('image', "Image", "")]
    
    if AM.library_type == 'assets':
        if len([obj for obj in context.scene.objects if obj.select and (obj.type == 'MESH' or (obj.type == 'EMPTY' and obj.dupli_group) or obj.type == 'CURVE' and (obj.data.extrude or obj.data.bevel_depth))]):
            render_type.insert(0, ('render', "Render", ""))
            render_type.insert(1, ('opengl', "OpenGL", ""))
    
    elif AM.library_type == 'materials':
        if not AM.as_mat_scene:
            render_type.insert(0, ('render', "Render", ""))
        else:
            render_type.insert(0, ('opengl', "OpenGL", ""))
    
    elif AM.library_type == 'scenes':
        render_type.insert(0, ('opengl', "OpenGL", ""))
        
 
    return render_type

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def thumbnailer_enum_items(self, context):
    """ Returns the list of the differents materials thumbnailer """
    
    addon_thumbnailers = ["AM_Sphere.blend", "AM_Cloth.blend"]
    custom_render_scene = get_custom_material_render_scene()
    render_scenes = custom_render_scene + addon_thumbnailers
 
    return [(scn, scn.split(".blend")[0], "") for scn in render_scenes]

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def move_to_library_enum_item(self, context):
    """ Returns the list of the libraries in the Asset management folder """
     
    AM = bpy.context.window_manager.asset_m
    library_path = get_library_path()
    
    libraries = [(lib, lib, "") for lib in listdir(join(library_path, AM.library_type)) if isdir(join(library_path, AM.library_type, lib))]
    
    return libraries
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
def move_to_category_enum_item(self, context):
    """ Returns the list of the categories from the new_lib property selection """
    
    AM = bpy.context.window_manager.asset_m
    library_path = get_library_path()
    
    categories = [(cat, cat, "") for cat in listdir(join(library_path, AM.library_type, AM.new_lib)) if isdir(join(library_path, AM.library_type, AM.new_lib, cat))]
    
    return categories

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
def datablock_enum_items(self, context):
    """ Returns the list of the libraries in the Asset management folder """
    
    WM = bpy.context.window_manager
    AM = WM.asset_m
    if AM.library_type != 'hdri':
        if not AM.datablock_list:
            library_path = get_library_path()
            blendfile = join(library_path, AM.library_type, AM.libraries, AM.categories, "blends", WM.AssetM_previews.rsplit(".", 1)[0] + ".blend")
            
            if AM.library_type == 'assets':
                sections = [('Group', 'groups'),
                            ('Image', 'images'),
                            ('Material', 'materials'),
                            ('NodeTree', 'node_groups'),
                            ('Object', 'objects'),
                            ]
            else:
                sections = [('Action', 'actions'),
                            ('Brush', 'brushes'),
                            ('FreestyleLineStyle', 'linestyles'),
                            ('GPencil', 'grease_pencil'),
                            ('Group', 'groups'),
                            ('Image', 'images'),
                            ('Ipo', 'ipos'),
                            ('Lamp', 'lamps'),
                            ('Lattice', 'lattices'),
                            ('Mask', 'masks'),
                            ('Material', 'materials'),
                            ('Mesh', 'meshes'),
                            ('Metaball', 'metaballs'),
                            ('MovieClip', 'movieclips'),
                            ('NodeTree', 'node_groups'),
                            ('Object', 'objects'),
                            ('ParticleSettings', 'particles'),
                            ('Scene', 'scenes'),
                            ('Sound', 'sounds'),
                            ('Speaker', 'speakers'),
                            ('Text', 'texts'),
                            ('Texture', 'textures'),
                            ('VFont', 'fonts'),
                            ('World', 'worlds'),
                            ]
            
            with bpy.data.libraries.load(blendfile) as (data_from, data_to):
                for attr in sections:
                    target_coll = eval("data_from." + attr[1])
                    if target_coll:
                        AM.datablock_list.append(attr[0])
            
            datablock = [(block, block, "") for block in AM.datablock_list]
     
            return datablock

        else:
            return [(block, block, "") for block in AM.datablock_list]