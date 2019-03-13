# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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


import bpy, os
from bpy.props import *
from bpy.types import Panel, Operator, Menu
from bpy.utils import previews

# Add-on info
bl_info = {
    "name": "Easy HDRI",
    "author": "Monaime Zaim (CodeOfArt.com)",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Properties > Easy HDRI",
    "description": "Load and test your HDRIs easily.", 
    "wiki_url": "http://codeofart.com/easy-hdri/",
    "tracker_url": "http://codeofart.com/easy-hdri/",      
    "category": "3D View"}


# Preview collections
preview_collections = {}
# Addon path
addon_dir = os.path.dirname(__file__)

###########################################################################################
################################### Functions #############################################
###########################################################################################

# Load an empty list(First launch)
def env_previews(self, context):  
    pcoll = preview_collections.get("prev")
    if not pcoll:
        return []
    return pcoll.prev

# It works just like os.walk, but you can pass it a level parameter
# that indicates how deep the recursion will go.
# http://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
def get_hdris(dir, level = 1):    
    assert os.path.isdir(dir)
    num_sep = dir.count(os.path.sep)
    hdris = []
    for root, dirs, files in os.walk(dir):
        for fn in files:
            if fn.lower().endswith(".hdr") or fn.lower().endswith(".exr"):
                hdris.append(os.path.join(root, fn).replace(dir, ''))            
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
    return hdris       
   
# Update the previews list if the folder changes
def update_dir(self, context):
       
    scn = bpy.context.scene
    enum_items = []
    if not 'previews_dir' in scn:
        scn['previews_dir'] = ''
    if not 'previews_list' in scn:
        scn['previews_list'] = []
    if not 'sub_dirs' in scn:
        scn['sub_dirs'] = 0  
    if not 'recursive_search' in scn:
        scn['recursive_search'] = 0              
    scn['previews_list'] = []
    
    previews_list = []
    recursion_level = scn.sub_dirs
    recursion = scn.recursive_search        
    previews_folder = bpy.path.abspath(scn['previews_dir'])
    pcoll = preview_collections["prev"]
           
    if os.path.exists(bpy.path.abspath(previews_folder)):
        if recursion:
            image_paths = get_hdris(previews_folder, recursion_level)        
        else: image_paths = get_hdris(previews_folder, 0)    
        for i, name in enumerate(image_paths):            
            filepath = os.path.join(previews_folder, name)
            if not pcoll.get(filepath):
                thumb = pcoll.load(filepath, filepath, 'IMAGE')
            else: thumb = pcoll[filepath]   
            enum_items.append((name, name, name, thumb.icon_id, i))
            previews_list.append(name)
        scn['previews_list'] = previews_list    
    pcoll.prev = enum_items
    pcoll.previews_dir = previews_folder
    if len(previews_list) > 0:
        scn.prev = previews_list[0]       
    return None

# Update the envirement map
def update_hdr(self, context):
    scn = bpy.context.scene
    dynamic = scn.dynamic_load
    dynamic_cleanup = scn.dynamic_cleanup
    sub_path = scn.prev
    set_projection = scn.set_projection
    image = os.path.basename(sub_path)
    images = bpy.data.images
    scn['previews_dir']  =  bpy.path.abspath(scn.previews_dir)  
    path = bpy.path.abspath(scn.previews_dir)
       
    if scn.world:
        if 'EasyHDR' in bpy.data.worlds and dynamic:
            if scn.world.name == 'EasyHDR':
                nodes = scn.world.node_tree.nodes            
                if 'Environment' in nodes:
                    env = nodes['Environment']
                    if image in images:
                        env.image = images[image]
                        if dynamic_cleanup:
                            cleanup_images()
                        if set_projection:
                            x, y = images[image].size                            
                            if x == y:
                                env.projection = 'MIRROR_BALL'
                            else: env.projection = 'EQUIRECTANGULAR'

    
                    else:
                        if os.path.exists(path):
                            if os.access(os.path.join(path, sub_path), os.F_OK):
                                filepath = os.path.join(path, sub_path) 
                                images.load(filepath)                                                    
                                if image in images:
                                    env.image = images[image]
                                    if dynamic_cleanup:
                                        cleanup_images()
                                    if set_projection:
                                        x, y = images[image].size
                                        if x == y:
                                            env.projection = 'MIRROR_BALL'
                                        else: env.projection = 'EQUIRECTANGULAR'    
                                                
    return None 


# Update the preview directory when the favorites change
def update_favs(self, context):
    scn = context.scene 
    favs = scn.favs
    if not favs in ['Empty', '']:
        scn.previews_dir = favs
    return None

# World nodes setup
def create_world_nodes():
    
    scn = bpy.context.scene
    worlds = bpy.data.worlds
    # Make sure the render engine is Cycles or Eevee
    if not scn.render.engine in ['CYCLES', 'BLENDER_EEVEE']:
        scn.render.engine = 'BLENDER_EEVEE'
    # Add a new world "EasyHDR", or reset the existing one
    if not 'EasyHDR' in worlds:
        world = bpy.data.worlds.new("EasyHDR")        
    else:
        world = worlds['EasyHDR']
    scn.world = world       
    # Enable Use nodes
    world.use_nodes= True
    # Delete all the nodes (Start from scratch)
    world.node_tree.nodes.clear()
    
    #Adding new nodes
    tex_coord = world.node_tree.nodes.new(type="ShaderNodeTexCoord")    
    mapping = world.node_tree.nodes.new(type="ShaderNodeMapping")   
    env = world.node_tree.nodes.new(type="ShaderNodeTexEnvironment")  
    background = world.node_tree.nodes.new(type="ShaderNodeBackground")
    gamma = world.node_tree.nodes.new(type="ShaderNodeGamma")
    saturation = world.node_tree.nodes.new(type="ShaderNodeHueSaturation")
    color = world.node_tree.nodes.new(type="ShaderNodeMixRGB")
    math_multiply = world.node_tree.nodes.new(type="ShaderNodeMath")
    math_divide = world.node_tree.nodes.new(type="ShaderNodeMath")
    math_add = world.node_tree.nodes.new(type="ShaderNodeMath")    
    output = world.node_tree.nodes.new(type="ShaderNodeOutputWorld") 
       
    # Change the parameters
    env.name = 'Environment'
    background.name = 'Background'
    mapping.name = 'Mapping'
    saturation.name = 'Saturation'
    math_multiply.name = 'Math_multiply'
    math_multiply.operation = 'MULTIPLY'
    math_multiply.inputs[1].default_value = 0.0
    math_divide.name = 'Math_divide'
    math_divide.operation = 'DIVIDE'
    math_divide.inputs[1].default_value = 100.0
    math_add.name = 'Math_add'   
    math_add.operation = 'ADD'   
    math_add.inputs[1].default_value = 1.0
    color.blend_type = 'MULTIPLY'  
    color.inputs[0].default_value = 0.0
        
    # Links
    world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs[0])
    world.node_tree.links.new(mapping.outputs[0], env.inputs[0])
    world.node_tree.links.new(env.outputs[0], gamma.inputs[0])
    world.node_tree.links.new(gamma.outputs[0], saturation.inputs[4])
    world.node_tree.links.new(saturation.outputs[0], color.inputs[1])
    world.node_tree.links.new(env.outputs[0], math_multiply.inputs[0])
    world.node_tree.links.new(math_multiply.outputs[0], math_divide.inputs[0])
    world.node_tree.links.new(math_divide.outputs[0], math_add.inputs[0])
    world.node_tree.links.new(math_add.outputs[0], background.inputs[1])
    world.node_tree.links.new(color.outputs[0], background.inputs[0])
    world.node_tree.links.new(background.outputs[0], output.inputs[0])    
    
    # Nodes location    
    tex_coord.location = (130, 252)
    mapping.location = (310, 252)
    env.location = (680, 252)
    gamma.location = (960, 350)
    saturation.location = (1120, 350)
    color.location = (1290, 350)
    math_multiply.location = (960, 100)
    math_divide.location = (1120, 100)
    math_add.location = (1290, 100)
    background.location = (1500, 252)
    output.location = (1660, 252)
    
    # Load
    if 'prev' in scn:
        scn.previews_dir = scn.previews_dir # hacky way to force the update
        if scn.prev != '' and scn.prev in bpy.data.images:
            env.image = bpy.data.images[scn.prev]
            
    

# Remove unused images 
def cleanup_images():
    images = bpy.data.images
    for image in images:
        if image.users == 0:
            images.remove(image)
            
# Check the World's node tree
def check_world_nodes():
    nodes_list = ['Texture Coordinate', 'Mapping', 'Background',
                  'World Output', 'Environment', 'Math_multiply',
                  'Math_divide', 'Math_add', 'Mix', 'Saturation',
                  'Gamma']
    all_found = True              
    scn = bpy.context.scene
    worlds = bpy.data.worlds
    if not scn.world:
        return 'Fix'        
    if not 'EasyHDR' in worlds:
        return 'Create'
    else:
        world = worlds['EasyHDR']
        nodes = world.node_tree.nodes
        if len(nodes) > 0:
            for n in nodes_list:
                if not n in nodes:
                    all_found = False
            if not all_found:
                return 'Fix'
        else:
            return 'Fix'
    if not scn.world.name == 'EasyHDR':
        return 'Fix'
    
# Get the list of favorites (enum)
def get_favs_enum(self, context):
    dirs = get_favs()
    if len(dirs) > 0:
        return [(i, i, '') for i in dirs]
    else: return [('Empty', '__Empty__', '')]

# return the list of favorites
def get_favs():
    dirs = []
    fav_file = os.path.join(addon_dir, "Favorites.fav")
    if os.path.exists(fav_file):    
        with open(fav_file, 'r') as ff:
            lines = ff.read()
            fav_dirs = lines.splitlines()
            dirs = [i for i in fav_dirs if i.strip() != '']
    return dirs       
        
    
        

###########################################################################################
################################### Operators #############################################
###########################################################################################

# Add to favorites
class EASYHDRI_OT_add_to_fav(Operator):
    bl_idname = "easyhdr.add_to_fav"
    bl_label = "Add to fav"
    bl_description = "Add the current folder to the favorites"

    def execute(self, context):
        scn = context.scene
        new_fav = bpy.path.abspath(scn.previews_dir)
        fav_file = os.path.join(addon_dir, "Favorites.fav")
        if os.path.exists(new_fav):
            if not os.path.exists(fav_file):
                with open(fav_file, 'w') as ff:
                    ff.write('')            
            dirs = get_favs()
            if not new_fav in dirs:
                dirs.append(new_fav)
                with open(fav_file, 'w') as ff:
                    for d in dirs:
                        if d : ff.write(d + '\n')
        else: self.report({'WARNING'}, 'Directory not found !')                       
                
        return {'FINISHED'}
    
# Remove from favorites
class EASYHDRI_OT_remove_from_fav(Operator):
    bl_idname = "easyhdr.remove_from_fav"
    bl_label = "Remove"
    bl_description = "Remove the current folder from the favorites"

    def execute(self, context):
        scn = context.scene
        dir = bpy.path.abspath(scn.previews_dir)
        fav_file = os.path.join(addon_dir, "Favorites.fav")                    
        dirs = get_favs()
        dirs.remove(dir)
        with open(fav_file, 'w') as ff:
            for d in dirs:
                if d : ff.write(d + '\n')                            
        return {'FINISHED'}          
    
# Reload previews
class EASYHDRI_OT_reload_previews(Operator):
    bl_idname = "easyhdr.reload_previews"
    bl_label = "Reload previews"
    bl_description = "Reload previews"

    def execute(self, context):
        scn = context.scene
        if 'previews_dir' in scn:
            if scn.previews_dir:
                scn.previews_dir = scn.previews_dir
        
        return {'FINISHED'}     

# Create world nodes    
class EASYHDRI_OT_create_world(Operator):
    bl_idname = "easyhdr.create_world"
    bl_label = "Create world nodes"
    bl_description = "Create world nodes for EasyHDR"

    def execute(self, context):
        create_world_nodes()        
        return {'FINISHED'}
    
# Load image    
class EASYHDRI_OT_load_image(Operator):
    bl_idname = "easyhdr.load_image"
    bl_label = "Load image"
    bl_description = "Load image"
    
    @classmethod
    def poll(cls, context):
        return not context.scene.dynamic_load

    def execute(self, context):
        scn = bpy.context.scene
        dynamic = scn.dynamic_load
        dynamic_cleanup = scn.dynamic_cleanup
        set_projection = scn.set_projection
        image = scn.prev
        images = bpy.data.images
        path = bpy.path.abspath(scn.previews_dir)        
        
        if 'EasyHDR' in bpy.data.worlds:
            if scn.world.name == 'EasyHDR':
                nodes = scn.world.node_tree.nodes            
                if 'Environment' in nodes:
                    env = nodes['Environment']
                    if image in images:
                        env.image = images[image]
                        if dynamic_cleanup:
                            cleanup_images()
                        if set_projection:
                            x, y = images[image].size
                            if x == y:
                                env.projection = 'MIRROR_BALL'
                            else: env.projection = 'EQUIRECTANGULAR'    
                    else:
                        if os.path.exists(path):
                            if os.access(os.path.join(path, image), os.F_OK):
                                filepath = os.path.join(path, image) 
                                images.load(filepath)                        
                                if image in images:
                                    env.image = images[image]   
                                    if dynamic_cleanup:
                                        cleanup_images()
                                    if set_projection:
                                        x, y = images[image].size
                                        if x == y:
                                            env.projection = 'MIRROR_BALL'
                                        else: env.projection = 'EQUIRECTANGULAR'            
              
        return {'FINISHED'} 
    
# Remove unused images
class EASYHDRI_OT_remove_unused_images(Operator):
    bl_idname = "easyhdr.remove_unused_images"
    bl_label = "Remove unused images"
    bl_description = "Remove 0 user images"
    
    def execute(self, context):
        cleanup_images()
        return {'FINISHED'}       
     
# Next next image
class EASYHDRI_OT_next_image(Operator):
    bl_idname = "easyhdr.next"
    bl_label = "Next"
    bl_description = "Next image"

    def execute(self, context):        
        scn = context.scene
        list = scn['previews_list']
        prev = scn.prev
        count = len(list)
        index = list.index(prev) + 1
        if index > count - 1:
            index = 0
        image = list[index]     
        if image != prev:
            scn.prev = image                      
        return {'FINISHED'}
    
# Preview previous image
class EASYHDRI_OT_previous_image(Operator):
    bl_idname = "easyhdr.previous"
    bl_label = "Previous"
    bl_description = "Previous image"

    def execute(self, context):
        scn = context.scene
        list = scn['previews_list']
        prev = scn.prev
        count = len(list)
        index = list.index(prev) - 1
        if index < 0:
            index = count-1
        image = list[index]     
        if image != prev:
            scn.prev = image                      
        return {'FINISHED'}      
        
    
###########################################################################################
##################################### The UI ##############################################
###########################################################################################          
    
# Easy HDRI Panel
class EASYHDRI_PT_main(Panel):          
    bl_label = "Easy HDRI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Easy HDRI'
    #bl_context = "objectmode"
    
    def draw(self, context):
        scn = context.scene
        favs = get_favs()
        dir = bpy.path.abspath(scn.previews_dir)
        recursion = scn.recursive_search
        layout = self.layout
        col = layout.column(align=True)
        active_hdr = ''
        prev_list = 0
        if 'previews_list' in scn:
            prev_list = len(scn['previews_list'])
        if len(preview_collections["prev"]) > 0 and prev_list > 0:
            active_hdr = scn.prev        
        if scn.render.engine in ['CYCLES', 'BLENDER_EEVEE']:
            row = col.row(align=True)
            if os.path.exists(dir):
                if not dir in favs:
                    row.operator("easyhdr.add_to_fav", text = '', icon = 'SOLO_ON')
                else: row.operator("easyhdr.remove_from_fav", text = '', icon = 'X')            
            row.prop(scn, "previews_dir", text = '')
            if recursion:
                col.prop(scn, "sub_dirs", text = 'Recursion level')
            if len(preview_collections["prev"]) > 0 and prev_list > 0:
                col.label(text = active_hdr, icon = 'IMAGE_DATA')                     
            row = layout.row()
            row.template_icon_view(scn, "prev", show_labels=True)
            col = row.column(align=True)
            col.operator("easyhdr.reload_previews", text = '',  icon = 'FILE_REFRESH')
            col.prop(scn, 'favs', text = '', icon = 'SOLO_OFF', icon_only=True)
            col.menu("easyhdr.settings", text = '', icon = 'TOOL_SETTINGS')
            if scn.render.engine == 'CYCLES':
                col.prop(scn.cycles, 'film_transparent', text = '', icon = 'FILE_IMAGE') 
            col = layout.column()                         
            col = layout.column()                
            if len(preview_collections["prev"]) > 0 and prev_list > 0:
                box = col.box() 
                box.scale_y = 1.0                             
                row = box.row(align = True)
                row.scale_y = 1.7
                row.operator("easyhdr.previous", text = '',  icon = 'TRIA_LEFT')
                #row1 = row.row() 
                #row1.scale_y = 1.7                
                row.operator("easyhdr.load_image", icon = 'IMAGE_DATA')                               
                row.operator("easyhdr.next", text = '', icon = 'TRIA_RIGHT')
            else:
                col.label(text = 'The list is empty', icon = 'ERROR')             
            if check_world_nodes() == 'Create':
                col.operator("easyhdr.create_world", icon = 'WORLD_DATA')
            elif check_world_nodes() == 'Fix':
                col.operator("easyhdr.create_world", text = 'Fix World nodes', icon = 'WORLD_DATA')                    
            else:                    
                col = layout.column()                
                nodes = scn.world.node_tree.nodes
                box = col.box()
                col = box.column()
                col.label(text = 'World Settings:', icon = 'WORLD_DATA')
                col = box.column()                
                if 'Math_multiply' in nodes:
                    col.prop(nodes['Math_multiply'].inputs[1], "default_value", text = 'Sun Strength')
                if 'Math_add' in nodes:
                    col.prop(nodes['Math_add'].inputs[1], "default_value", text = 'Sky Strength')    
                col = box.column()
                if 'Environment' in nodes:
                    col.prop(nodes['Environment'], "projection", text = '')                                            
                if 'Mapping' in nodes:
                    col = box.column()
                    col.prop(nodes['Mapping'], "rotation")                
                if 'Mix' in nodes:
                    col = box.column(align = True)
                    col.prop(nodes['Mix'].inputs[2], "default_value", text = "Tint")        
                    col.prop(nodes['Mix'].inputs[0], "default_value", text = "Factor")
                if 'Gamma' in nodes:
                    col = box.column()
                    col.prop(nodes['Gamma'].inputs[1], "default_value", text = "Gamma")
                if 'Saturation' in nodes:
                    col = box.column()
                    col.prop(nodes['Saturation'].inputs[1], "default_value", text = "Saturation")                
        else:
            col.label(text = 'Not compatible with this render engine', icon = 'INFO')
            col.prop(scn.render, 'engine')
                    
# Settings Menu
class EASYHDRI_MT_settings(Menu):
    bl_idname = "easyhdr.settings"
    bl_label = "Settings"
    bl_description = "Settings"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.label(text = 'Cleanup:')    
        layout.operator("easyhdr.remove_unused_images")
        layout.separator()
        layout.label(text = 'Loading images:')
        layout.prop(scn, 'dynamic_load', text = 'Load dynamically')
        layout.prop(scn, 'dynamic_cleanup', text = 'Cleanup dynamically')
        layout.prop(scn, 'set_projection', text = 'Set projection dynamically')
        layout.separator()
        layout.label(text = 'Recursive file search:')
        layout.prop(scn, 'recursive_search', text = 'Search in sub-folders')


# Register/Unregister

classes = (
    EASYHDRI_OT_add_to_fav,
    EASYHDRI_OT_remove_from_fav,
    EASYHDRI_OT_reload_previews,
    EASYHDRI_OT_create_world,
    EASYHDRI_OT_load_image,
    EASYHDRI_OT_remove_unused_images,
    EASYHDRI_OT_next_image,
    EASYHDRI_OT_previous_image,
    EASYHDRI_PT_main,
    EASYHDRI_MT_settings
    )
    
def register():
    
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    pcoll = previews.new()     
    preview_collections["prev"] = pcoll
    bpy.types.Scene.prev = EnumProperty(items = env_previews, update = update_hdr)
    bpy.types.Scene.favs = EnumProperty(name = 'Favorites', items = get_favs_enum, update = update_favs, description = 'List of the favorit folders')
    bpy.types.Scene.dynamic_load = BoolProperty(default = True, description = 'Load the images dynamically')        
    bpy.types.Scene.dynamic_cleanup = BoolProperty(default = False, description = 'Remove 0 user images dynamically')    
    bpy.types.Scene.recursive_search = BoolProperty(default = False, update = update_dir, description = 'Enable/Disable Recursive search')
    bpy.types.Scene.set_projection = BoolProperty(default = False, update = update_hdr, description = 'Set the projection dynamically')    
    bpy.types.Scene.previews_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default="",
            update = update_dir,
            description = 'Path to the folder containing the images'      
            )
    bpy.types.Scene.sub_dirs = IntProperty(
            default = 0,
            min = 0, max = 20,
            update = update_dir,
            description = 'Look for HDRIs in the sub folder(s), at this level, 0 = No recursion'
            )               

def unregister():
    
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)        
    
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()
    del bpy.types.Scene.prev
    del bpy.types.Scene.favs    
    del bpy.types.Scene.dynamic_load
    del bpy.types.Scene.dynamic_cleanup
    del bpy.types.Scene.recursive_search
    del bpy.types.Scene.set_projection
    del bpy.types.Scene.previews_dir   
    del bpy.types.Scene.sub_dirs


if __name__ == "__main__":
    register()