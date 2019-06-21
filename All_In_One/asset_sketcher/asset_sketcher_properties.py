'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

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
import bpy.utils.previews
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty, PointerProperty
import math
from . functions import *
import os


class ItemObjects(bpy.types.PropertyGroup):
    name : StringProperty(default="")
    
class AssetCategories(bpy.types.PropertyGroup):
    name : StringProperty(default="")    


def lock_assets(self,context):
    if self != context.window_manager.asset_sketcher.asset_list[self.name]:
        context.window_manager.asset_sketcher.asset_list[self.name].hide_select = self.hide_select
        for obj in context.scene.objects:
            if "as_asset_name" in obj:
                if obj["as_asset_name"] == self.name:
                    obj.hide_select = self.hide_select
                    if self.hide_select:
                        obj.select = False
                        if context.scene.objects.active == obj:
                            context.scene.objects.active = None

def hide_assets(self,context):
    if self != context.window_manager.asset_sketcher.asset_list[self.name]:
        context.window_manager.asset_sketcher.asset_list[self.name].hide = self.hide
        for obj in context.scene.objects:
            if "as_asset_name" in obj:
                if obj["as_asset_name"] == self.name:
                    obj.hide = self.hide             

def update_previews(self,context):
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    pcoll = bpy.utils.previews.new()
    pcoll.asset_previews_dir = ""
    pcoll.asset_previews = ()
    preview_collections["asset_previews"] = pcoll
    bpy.context.window_manager.asset_previews_loaded = False
    return pcoll

def id_from_string(my_string):
    id = int(hash(my_string)/1000000000000)
    return id
        
def get_icon_previews(self,context):
    enum_items = []
    
    wm = context.window_manager
    pcoll = preview_collections["asset_previews"]
    filename = os.path.basename(bpy.data.filepath.split(".blend")[0])+".thumbs"
    preview_path = os.path.join(os.path.dirname(bpy.data.filepath),filename)
    if os.path.isdir(preview_path) and len(wm.asset_sketcher.display_asset_list) > 0:
        
        if wm.asset_previews_loaded:
            return pcoll.asset_previews
        
        pcoll = update_previews(self,context)
        
        image_paths = []
        for fn in os.listdir(preview_path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)
                
        for i,name in enumerate(image_paths):
            filepath = os.path.join(preview_path,name)
            if name.split(".png")[0] in wm.asset_sketcher.display_asset_list and filepath not in pcoll:
                thumb = pcoll.load(filepath,filepath,'IMAGE')
                name = name.split(".png")[0]
                enum_items.append((name,name,"",thumb.icon_id, id_from_string(name)))
            
        pcoll.asset_previews = enum_items    
        wm.asset_previews_loaded = True
        return pcoll.asset_previews
    else:
        return [("","","")]

class CanvasList(bpy.types.PropertyGroup):
    name : StringProperty(default="")
    canvas_item : PointerProperty(type=bpy.types.Object)


### This Class stores all asset settings for each entry
class AssetList(bpy.types.PropertyGroup):
    name : StringProperty(default="")
    make_single_user : BoolProperty(description="Objects gets added as single User Obejcts with its own Mesh Data.",default=False)
    canvas : BoolProperty(description="Added object functions also as Canvas and can be painted on.",default=False)
    
    
    
    group_mode : EnumProperty(description="Defines how Assets are picked from Group. Random or Cyclic.",items=(("RANDOM","Pick Random","Random"),("CYCLIC","Pick Cyclic","Cyclic")))

    
    asset_distance : FloatProperty(description="Set the asset distance for each Paint Stroke.",default = 1.0,min=0.0, max=30.0)
    distance_constraint : BoolProperty(description = "Constraint Distance to Brush Radius.",default=False)
    z_offset : FloatProperty(description="Set the Z offset the Assets gets placed from the underground.",default = 0.0,min=-30.0, max=30.0)
    slope_threshold : FloatProperty(description="Defines the threshold if assets can be placed on a slope.",default = 0.0,min=0.0, max=1.0,subtype="FACTOR")
    surface_orient : FloatProperty(description="Defines how much the asset is aligned to the surface normal.",default = 1.0,min=0.0, max=1.0,subtype="FACTOR")
    
    hide_select : BoolProperty(description = "Lock all Assets of that Type.",default=False,update=lock_assets)
    hide : BoolProperty(description = "Hide all Assets of that Type.",default=False,update=hide_assets)
    
    use_no_scale : BoolProperty(description="Will disable Scaling when placing assets.",default=False)
    use_no_rotation : BoolProperty(description="Will disable Rotation when placing assets.",default=False)
    
    rand_rot_x : FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    rand_rot_y : FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    rand_rot_z : FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    
    rand_scale_x : FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    rand_scale_y : FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    rand_scale_z : FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    
    offset_x : FloatProperty(description="Set offset values for grid mode.",default=0.0)
    offset_y : FloatProperty(description="Set offset values for grid mode.",default=0.0)
    offset_z : FloatProperty(description="Set offset values for grid mode.",default=0.0)
    
    stroke_orient : BoolProperty(description = "Asset is directing to the stroke direction.",default=False)
    
    rot_x : FloatProperty(description="Set the rotation of a placed asset.",default=0,subtype='ANGLE',min=math.radians(-180),max=math.radians(180))
    rot_y : FloatProperty(description="Set the rotation of a placed asset.",default=0,subtype='ANGLE',min=math.radians(-180),max=math.radians(180))
    rot_z : FloatProperty(description="Set the rotation of a placed asset.",default=0,subtype='ANGLE',min=math.radians(-180),max=math.radians(180))
    
    constraint_rand_scale : BoolProperty(description = "Constraints the random scale to all axis.",default=True)

    scale : FloatProperty(description="Set the scale of your asset",default=1.0,min=0.01)
    scale_pressure : BoolProperty(description="Constraint Asset Scale to pen pressure",default = False)
    type : EnumProperty(description="",default="OBJECT",items=(("OBJECT","Object","Object","",0),("GROUP","Group","Group","",1),("EMPTY","Empty","Empty","",2)))
    

ITEMS = []
def get_visible_objects(self,context):
    global ITEMS
    wm = context.window_manager
    collection_len = len(wm.asset_sketcher.visible_objects_collection)
    objs_len = 0
    for obj in context.visible_objects:
        if obj.type == "MESH":# and "as_merge_object" in obj:
            objs_len += 1
            
    ITEMS = []
    
    if collection_len != objs_len:
        for i in range(collection_len):
            wm.asset_sketcher.visible_objects_collection.remove(0)
    for obj in context.visible_objects:
        if obj.type == "MESH":# and "as_merge_object" in obj:
            ITEMS.append((obj.name,obj.name,obj.name))
            
            if collection_len != objs_len:
                item = wm.asset_sketcher.visible_objects_collection.add()
                item.name = obj.name
            
    return ITEMS        

def select_asset_preview(self,context):
    wm = context.window_manager
    for i,asset in enumerate(wm.asset_sketcher.display_asset_list):
        if wm.asset_preview_icon == asset.name:
            wm.asset_sketcher["display_asset_list_index"] = i
    for i,asset in enumerate(wm.asset_sketcher.asset_list):
        if wm.asset_preview_icon == asset.name:
            wm.asset_sketcher["asset_list_index"] = i

#class MergeObjectAvailableObjects(bpy.types.PropertyGroup):
    

### All Addon Properties are stored in this Group
class AssetSketcherProperties(bpy.types.PropertyGroup):

    name : StringProperty(default="")

    asset_preview : BoolProperty(description="Preview Asset. Does not work well with Blenders undo system. May cause crashes. Turned off by default.",default=False)
    
    ### general addon operator
    sketch_mode_active : BoolProperty(description="Disable Sketching",default=False)
    
    ### brush and operator box
    box_brush_settings : BoolProperty(description="Show/Hide Brush Box", default=True)
    
    sketch_mode : EnumProperty(name="Asset Sketcher Mode",description="Asset Sketcher Painting Mode",default="PAINT",items=(("PAINT","Paint Mode","Paint mode","BRUSH_DATA",0),("SCALE","Scale Mode","Scale mode","MAN_SCALE",1),("GRID","Grid Mode","Grid mode","GRID",2)))
    sketch_plane_axis : EnumProperty(name="Sketch Plane Axis",description="The Plane the grid system is in.",default="XY",items=(("XY","XY Plane","XY Plane","",0),("XZ","XZ Plane","XZ Plane","",1),("YZ","YZ Plane","YZ Plane","",2)))
    sketch_grid_size : FloatProperty(default=2.0)
    sketch_layer : IntProperty()
    brush_size : FloatProperty(description="Brush Size", default=25.0,min=0.01)
    brush_density : IntProperty(description="Brush Density", default=1,min=1,max=100)
    
    use_brush_size_pressure : BoolProperty(description="Use Pen Pressure for brush size.")
    use_brush_density_pressure : BoolProperty(description="Use Pen Pressure for brush density.")
    pen_pressure : FloatProperty(default=1.0)
    
    delete_only_selected : BoolProperty(description="Delete only selected Objects.")
    
    visible_objects : EnumProperty(name="Visible Objects",items=get_visible_objects)

    merge_object : StringProperty(description="If a Name is set, all new Assets will be merged into one Object. Increases performance. Delete Brush does not work on single Assets anymore.",default="")
    
    ### asset library box
    box_asset_settings : BoolProperty(description="Show/Hide Asset Box", default=True)
    
    ### canvas list
    use_canvas_objects : BoolProperty(default=False)

    canvas_list_index : IntProperty(default=0)
    
    ### asset list
    
    asset_list_index : IntProperty(default=0)
    
    
    display_asset_list_index : IntProperty(default=0,update=update_asset_list_index)

    categories_enum : EnumProperty(name="Asset Categories",description="Create Asset Categories to better organize your Assets.",items=get_categories,update=update_category_display)
    categories_enum_prev : StringProperty()
    
    ### asset canvas box
    box_canvas_objects : BoolProperty(description="Show/Hide Canvas Objects Box", default=True)
    
    ### physics box
    box_physics : BoolProperty(description="Show/Hide Physics Box", default=True)
    
    canvas_all : BoolProperty(description="Use any object as Canvas",default=False)
    
    physics_friction : FloatProperty(description="Friction Value that is used for phyics calculation.",default=0.5,min=0.0,max=1.0)
    running_physics_calculation : BoolProperty(description="", default=False)
    physics_time_scale : FloatProperty(description="Time Scale that is used for calculation. Smaller Values are more accurate, but take longer to calculate.", default=5.0,min=0.0,max=20.0)


preview_collections = {}

classes = (
    AssetSketcherProperties,
    #MergeObjectAvailableObjects,
    ItemObjects,
    AssetCategories,
    CanvasList,
    AssetList,
    
    )
    
def register():
    for cla in classes:
        bpy.utils.register_class(cla)
    bpy.types.WindowManager.asset_sketcher : PointerProperty(type=AssetSketcherProperties)
    bpy.types.Scene.asset_sketcher : PointerProperty(type=AssetSketcherProperties)
    
    bpy.types.WindowManager.asset_preview_icon : EnumProperty(items=get_icon_previews,update=select_asset_preview)
    bpy.types.WindowManager.asset_previews_loaded : BoolProperty(default=False)
    bpy.types.WindowManager.asset_sketcher.canvas_list : CollectionProperty(type=CanvasList)
    bpy.types.WindowManager.asset_sketcher.asset_list : CollectionProperty(type=AssetList)
    bpy.types.WindowManager.asset_sketcher.group_objects : CollectionProperty(type=ItemObjects)
    bpy.types.WindowManager.asset_sketcher.categories : CollectionProperty(type=AssetCategories)
    bpy.types.WindowManager.asset_sketcher.display_asset_list : CollectionProperty(type=AssetList)
    bpy.types.WindowManager.asset_sketcher.visible_objects_collection : CollectionProperty(type=AssetSketcherProperties)
    bpy.types.WindowManager.asset_sketcher.categories : CollectionProperty(name="Asset Categories",type=AssetCategories)
    
    
    #preview_path = os.path.join(os.path.dirname(bpy.data.filepath),"asset_thumbs")
    pcoll = bpy.utils.previews.new()
    pcoll.asset_previews_dir = ""
    pcoll.asset_previews = ()
    preview_collections["asset_previews"] = pcoll
    #bpy.context.window_manager.asset_previews_loaded = False

    
def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    for cla in classes:
        bpy.utils.unregister_class(cla)

