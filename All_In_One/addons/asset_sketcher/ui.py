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
import os

from . functions import get_addon_prefs

class NewMergeObject(bpy.types.Operator):
    bl_idname = "asset_sketcher.new_merge_object"
    bl_label = "New Merge Object"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    name = bpy.props.StringProperty(name="Name",default="Merge Object")
    def create_new_merge_object(self,context,wm):
        ob_data = bpy.data.meshes.new(self.name)
        merge_object = bpy.data.objects.new(self.name,ob_data)
        context.scene.objects.link(merge_object)
        context.scene.asset_sketcher.merge_object = merge_object.name
        return merge_object
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        wm = context.window_manager
        self.create_new_merge_object(context,wm)
        return {"FINISHED"}

class MergeObjects(bpy.types.Operator):
    bl_idname = "asset_sketcher.merge_objects"
    bl_label = "Merge Objects"
    bl_description = "Merge Selected Objects into MergeObject"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True
    
    def create_new_merge_object(self,context,wm):
        ob_data = bpy.data.meshes.new(context.scene.asset_sketcher.merge_object)
        merge_object = bpy.data.objects.new(context.scene.asset_sketcher.merge_object,ob_data)
        context.scene.objects.link(merge_object)
        return merge_object
    
    def convert_group_instance(self,context,wm,assets):
        for obj in context.selected_objects:
            obj.select = False
        for obj in assets:
            obj.select = True
        bpy.ops.object.duplicates_make_real(use_base_parent=False,use_hierarchy=False)
        for obj in context.selected_objects:
            if obj.type == "EMPTY" and obj.dupli_type == "NONE":
                bpy.data.objects.remove(obj,do_unlink=True)
        return context.selected_objects        
    
    def merge_asset(self,context,wm,assets):
        if context.scene.asset_sketcher.merge_object != "":
            merge_obj = bpy.data.objects[context.scene.asset_sketcher.merge_object] if context.scene.asset_sketcher.merge_object in bpy.data.objects else self.create_new_merge_object(context,wm)
            if "as_asset" not in merge_obj:
                merge_obj["as_asset"] = True
            if "as_merge_object" not in merge_obj:
                merge_obj["as_merge_object"] = True
            if merge_obj != None:
                bpy.context.scene.objects.active = None
                for obj in context.scene.objects:
                    obj.select = False
                for asset in assets: 
                    asset.select = True
                merge_obj.select = True
                context.scene.objects.active = merge_obj
                bpy.ops.object.join()

    def execute(self, context):
        wm = context.window_manager
        if len(context.selected_objects) == 0:
            self.report({"INFO"},"You need to select at least one Object to merge it into the 'Merge Object'")
            return{'FINISHED'}
        
        if context.scene.asset_sketcher.merge_object == "":
            merge_object = self.create_new_merge_object(context,wm)
            merge_object.name = "Merge Object"
            context.scene.asset_sketcher.merge_object = merge_object.name
        assets = self.convert_group_instance(context,wm,context.selected_objects)
        self.merge_asset(context,wm,assets)
        
        return {"FINISHED"}
                

class AssetSketcherUI(bpy.types.Panel):
    bl_idname = "asset_sketcher_ui"
    bl_label = "Asset Sketcher 1.1"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_category = "AssetSketcher"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        asset_list = wm.asset_sketcher.asset_list
        asset_list_index = wm.asset_sketcher.asset_list_index
        
        addon_prefs = get_addon_prefs(context)
        
        ### AS Logo Icon
        #print(preview_collections)
        pcoll = preview_collections["main"]
        as_icon = pcoll["as_icon"]
        #print(as_icon.icon_id)
        ### Sketch Button
        col = layout.column()
        if wm.asset_sketcher.sketch_mode_active == False:
            col.operator('asset_sketcher.sketch_assets', icon_value=as_icon.icon_id , text = "Enable Sketching")
        else:
            col.prop(wm.asset_sketcher, 'sketch_mode_active', icon_value=as_icon.icon_id ,text="Disable Sketching")
        
        ### Brush & Operators Box
        box = layout.box()
        if wm.asset_sketcher.box_brush_settings:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_brush_settings",emboss=False,text="Brush Settings",icon="DOWNARROW_HLT")
            
            col.prop(wm.asset_sketcher,"sketch_mode",text="")
            
            if wm.asset_sketcher.sketch_mode in ["SCALE","PAINT"]:
                col = box.column()
                col.label(text="Brush Settings:",icon="BRUSH_DATA")

                #col = box.column()
                col = col.column(align=True)
                row = col.row(align = True)
                row.prop(wm.asset_sketcher, 'brush_size', text="Brush Size")
                row.row(align=True).prop(wm.asset_sketcher, 'use_brush_size_pressure', text="",icon="STYLUS_PRESSURE")

                col = col.column(align=True)
                row = col.row(align = True)
                row.prop(wm.asset_sketcher, 'brush_density', text="Brush Density")
                row.row(align=True).prop(wm.asset_sketcher, 'use_brush_density_pressure', text="",icon="STYLUS_PRESSURE")
                
                col = col.column(align=True)
                #row = col.row(align = True)
                #col.prop(wm.asset_sketcher,"canvas_all",text="Use everything as Canvas")
                col.prop(wm.asset_sketcher,'delete_only_selected',text="Delete only Selected Assets")
#                if addon_prefs.enable_asset_preview:
#                    col.prop(wm.asset_sketcher,'asset_preview',text="Asset Preview")
            elif wm.asset_sketcher.sketch_mode == "GRID":
                col = box.column()
                col.label(text="Grid Settings:",icon="GRID")
                
                col = col.column(align=True)
                col.prop(wm.asset_sketcher, 'sketch_grid_size', text="Grid Size")
                col.prop(wm.asset_sketcher, 'sketch_layer', text="Grid Layer")
                col.prop(wm.asset_sketcher, 'sketch_plane_axis', text="")

                col = col.column(align=True)
                col.prop(wm.asset_sketcher,'delete_only_selected',text="Delete only Selected Assets")
                col.prop(wm.asset_sketcher,'asset_preview',text="Asset Preview")  
                
            
            wm.asset_sketcher.visible_objects ### updates enum property
            subrow = col.row(align=True)
            #subrow.prop_search(wm.asset_sketcher,"merge_object",context.scene,"objects",text="Merge Object")
            subrow.prop_search(context.scene.asset_sketcher,"merge_object",wm.asset_sketcher,"visible_objects_collection",text="Merge Object",icon="OBJECT_DATAMODE")
            if context.scene.asset_sketcher.merge_object == "":
                subrow.operator("asset_sketcher.new_merge_object",text="",icon="ZOOMIN")
            subrow.operator("asset_sketcher.merge_objects",text="",icon="AUTOMERGE_ON")
        else:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_brush_settings",emboss=False,text="Brush Settings",icon="RIGHTARROW")
                
        
        ### Asset List Box
        box = layout.box()
        if wm.asset_sketcher.box_asset_settings:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_asset_settings",emboss=False,text="Asset Library",icon="DOWNARROW_HLT")
            
            #col = box.column()
            row = col.row(align=True)
            row.prop(wm.asset_sketcher,"categories_enum", text="")
            row.operator("asset_sketcher.add_asset_category", text="",icon="ZOOMIN")
            row.operator("asset_sketcher.remove_asset_category", text="",icon="ZOOMOUT")
            
            ### Asset Thumbnail
            subcol= col.row(align=True)
            subcol.scale_y = .5
            subcol.template_icon_view(wm,"asset_preview_icon")
            
            subcol = subcol.column(align=True)
            if addon_prefs.enable_asset_preview:
                subcol.scale_y = 1.5
                if wm.asset_sketcher.asset_preview:
                    subcol.prop(wm.asset_sketcher,'asset_preview',text="",icon="RESTRICT_VIEW_OFF")
                else:
                    subcol.prop(wm.asset_sketcher,'asset_preview',text="",icon="RESTRICT_VIEW_ON")
            else:
                subcol.scale_y = 3
            subcol.operator("asset_sketcher.generate_asset_preview", text="",icon="FILE_REFRESH")
            ### Operator for adding new items to asset list
            icon = "OBJECT_DATAMODE"
            text = "Create new Asset Item Object"
            if len(context.selected_objects) > 1:
                icon = "GROUP"
                text = "Create new Asset Item Group"
            elif len(context.selected_objects) == 1 and context.active_object != None and context.active_object.type == "EMPTY":
                icon = "EMPTY_DATA"
                text = "Create new Asset Item Instance"
                
            col.operator("asset_sketcher.add_asset_item", text=text,icon=icon)
            
            col.operator("asset_sketcher.import_asset_lib", text="Import Asset Library",icon="IMPORT")
            
            
            col.template_list("UIListAssetItem","dummy",wm.asset_sketcher, "display_asset_list", wm.asset_sketcher, "display_asset_list_index", rows=5)
            
            #col.template_list("UIListAssetItem","dummy",wm.asset_sketcher, "asset_list", wm.asset_sketcher, "asset_list_index", rows=5)
            ### Asset template list
            if len(asset_list) > 0:
                asset_item = asset_list[asset_list_index]
                
                col = box.column()
                col.label(text="Asset Settings:",icon="OBJECT_DATAMODE")
                
                col = col.column(align=True)
                if asset_item.type == "GROUP":
                    subrow = col.row()
                    subrow.prop(asset_item,"group_mode",text="Pick Mode",expand=True)
                col.prop(asset_item,"make_single_user",text="Single User Object")
                #col.prop(asset_item,"canvas",text="Canvas Object")
                if asset_sketcher.sketch_mode in ["SCALE"]:
                    col.prop(asset_item,"use_no_scale", text="Use no Scale")
                    col.prop(asset_item,"use_no_rotation", text="Use no Rotation")
                if asset_sketcher.sketch_mode in ["PAINT","SCALE"]:
                    
                    row = col.row(align=True)
                    row.prop(asset_item,"asset_distance",text="Asset Distance")
                    row.prop(asset_item,"distance_constraint",text="",icon="CONSTRAINT")
                    col.prop(asset_item,"z_offset", text="Z-Offset")
                    col.prop(asset_item, "slope_threshold", text="Slope Threshold")
                    col.prop(asset_item,"surface_orient", text="Surface Orientation")
                
                if asset_sketcher.sketch_mode in ["GRID"]:
                    col.separator()
                    col = col.column(align=True)
                    col.prop(asset_item,"offset_x",text="Offset X")
                    col.prop(asset_item,"offset_y",text="Offset Y")
                    col.prop(asset_item,"offset_z",text="Offset Z")
                
                col.separator()
                col = col.column(align=True)
                col.prop(asset_item,"rot_x",text="Rotation X")
                col.prop(asset_item,"rot_y",text="Rotation Y")
                col.prop(asset_item,"rot_z",text="Rotation Z")
                
                col.separator()
                col = col.column(align=True)
                col.prop(asset_item,"rand_rot_x",text="Random Rotation X")
                col.prop(asset_item,"rand_rot_y",text="Random Rotation Y")
                col.prop(asset_item,"rand_rot_z",text="Random Rotation Z")
                col.prop(asset_item,"stroke_orient",text="Sketch in Stroke Direction",toggle=True,icon="CURVE_PATH")
                
                col.separator()
                col = col.column(align=True)
                row = col.row(align=True)
                row.prop(asset_item,"scale",text="Asset Scale")
                row.prop(asset_item,"scale_pressure",text="",icon="STYLUS_PRESSURE")
                if asset_item.constraint_rand_scale:
                    col = col.column(align=True)
                    row = col.row(align=True)
                    row.prop(asset_item,"rand_scale_x",text="Random Scale")
                    row.prop(asset_item,"constraint_rand_scale",text="",icon="CONSTRAINT")
                else:    
                    row = col.row(align=True)
                    col1 = row.column(align=True)
                    col1.prop(asset_item,"rand_scale_x",text="Random X Scale")
                    col1.prop(asset_item,"rand_scale_y",text="Random Y Scale")
                    col1.prop(asset_item,"rand_scale_z",text="Random Z Scale")
                    col2 = row.column(align=True)
                    col2.scale_y = 3
                
                    col2.prop(asset_item,"constraint_rand_scale",text="",icon="CONSTRAINT")
                
                col.separator()
                col.operator("asset_sketcher.add_asset_to_category", text="Add to Category",icon="GROUP")    
                col.operator("asset_sketcher.remove_asset_to_category", text="Remove from active Category",icon="GROUP")    
            
        else:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_asset_settings",emboss=False,text="Asset Library",icon="RIGHTARROW")
            
        
        ### Canvas Objects List Box
        box = layout.box()
        if wm.asset_sketcher.box_canvas_objects:
            col = box.column()
            row = col.row()
            row.prop(wm.asset_sketcher,"box_canvas_objects",emboss=False,text="Canvas Objects",icon="DOWNARROW_HLT")
            row.prop(wm.asset_sketcher,"use_canvas_objects",text="")
            
            col.prop(wm.asset_sketcher,"use_canvas_objects",text="Use Below Objects as Canvas")
            col.prop(wm.asset_sketcher,"canvas_all",text="Use everything as Canvas")
            col.operator("asset_sketcher.add_canvas_item",text="Add Canvas Objects",icon="OUTLINER_OB_SURFACE")
            col.template_list("UIListCanvasItem","dummy",wm.asset_sketcher, "canvas_list", wm.asset_sketcher, "canvas_list_index", rows=5)
        else:
            col = box.column()
            row = col.row()
            row.prop(wm.asset_sketcher,"box_canvas_objects",emboss=False,text="Canvas Objects",icon="RIGHTARROW")
            row.prop(wm.asset_sketcher,"use_canvas_objects",text="")
            
        
        ### Physics Box
        box = layout.box()
        if wm.asset_sketcher.box_physics:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_physics",emboss=False,text="Physics",icon="DOWNARROW_HLT")
            
            row = box.column(align=True)
            row.label(text="Physics Settings:",icon="MOD_PHYSICS")
            row.prop(wm.asset_sketcher,'physics_friction', text="Friction",slider=True)
            row.prop(wm.asset_sketcher,'physics_time_scale', text="Time Scale")
            row = box.row()
            if not wm.asset_sketcher.running_physics_calculation:
                op = row.operator('asset_sketcher.calc_physics',text = "Calc Physics",icon="MESH_ICOSPHERE")
            else:
                row.prop(wm.asset_sketcher,'running_physics_calculation', text="Cancel Calculation",icon="X")
            
        else:
            col = box.column()
            col.prop(wm.asset_sketcher,"box_physics",emboss=False,text="Physics",icon="RIGHTARROW")

class UIListCanvasItem(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname,index):
        ob = data
        slot = item
        row = layout.row()
        #row.label(text=slot.name)
        if item.canvas_item != None:
            row.prop(item.canvas_item,"name",text="",icon="OUTLINER_OB_SURFACE",emboss=False)
        op = row.operator("asset_sketcher.remove_canvas_item",text="",icon="X",emboss=False)
        op.index = index
            
### UIList Class for Asset List Item            
class UIListAssetItem(bpy.types.UIList):
    def __init__(self):
        self.ico = ''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        row = layout.row(align=True)
        if item.type == 'OBJECT':
            self.ico = 'OBJECT_DATAMODE'
        elif item.type == 'GROUP':
            self.ico = 'GROUP'
        elif item.type == 'EMPTY':
            self.ico = 'OUTLINER_DATA_EMPTY'
        elif item.type == "CANVAS":
            self.ico = 'OUTLINER_OB_SURFACE'

        row.label(text=item.name,icon=self.ico)
        
        if item.hide_select:
            row.prop(item,"hide_select",text="",icon="LOCKED",emboss=False)
        else:
            row.prop(item,"hide_select",text="",icon="UNLOCKED",emboss=False)
            
        if item.hide:
            row.prop(item,"hide",text="",icon="VISIBLE_IPO_OFF",emboss=False)
        else:
            row.prop(item,"hide",text="",icon="VISIBLE_IPO_ON",emboss=False)
        
        op = row.operator('asset_sketcher.select_objects',text = "",icon="RESTRICT_SELECT_OFF",emboss=False)
        op.idx = int(index)
        op.mode = "select"
        
        op = row.operator("asset_sketcher.remove_asset_item", icon='X', text="", emboss=False)
        op.idx = int(index) 
        
preview_collections = {}        
def register_icons():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews = ()
    my_icons_dir = os.path.join(os.path.dirname(__file__),"icons")
    pcoll.load("as_icon", os.path.join(my_icons_dir,"as_logo.png"),'IMAGE')
    
    preview_collections["main"] = pcoll
    
def unregister_icons():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()    

classes = (
    NewMergeObject,
    MergeObjects,
    AssetSketcherUI,
    UIListCanvasItem,
    UIListAssetItem,   
    )

def register():
    for cla in classes:
        bpy.utils.register_class(cla)

def unregister():
    for cla in classes:
        bpy.utils.unregister_class(cla)


