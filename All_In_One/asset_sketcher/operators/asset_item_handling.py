import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty, PointerProperty
from .. functions import *

def get_categories2(self,context):
    wm = context.window_manager
    asset_sketcher = wm.asset_sketcher
    categories = asset_sketcher.categories
    
    list = []
    for i,category in enumerate(categories):
        item = (category.name.upper(),category.name,category.name,"FILE_FOLDER",i)
        list.append(item)
    return list   

class AddCanvasItem(bpy.types.Operator):
    bl_idname = "asset_sketcher.add_canvas_item"
    bl_label = "Add Canvas Item"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        for obj in context.selected_objects:
            if obj.name not in wm.asset_sketcher.canvas_list and obj.type == "MESH":
                item = wm.asset_sketcher.canvas_list.add()
                item.name = obj.name
                item.canvas_item = obj
        return {"FINISHED"}
    
class RemoveCanvasItem(bpy.types.Operator):
    bl_idname = "asset_sketcher.remove_canvas_item"
    bl_label = "Remove Canvas Item"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    index = IntProperty()
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        wm.asset_sketcher.canvas_list.remove(self.index)
        return {"FINISHED"}
    
    
        

class AddAssetToCategory(bpy.types.Operator):
    bl_idname = "asset_sketcher.add_asset_to_category"
    bl_label = "Add Asset To Category"
    bl_description = ""
    bl_options = {"REGISTER"}

    invoke = BoolProperty(default=True)
    categories = EnumProperty(name="Available Categories",items=get_categories2)
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    
    def execute(self, context):
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        cat_name = self.categories
        asset_item = asset_sketcher.asset_list[asset_sketcher.asset_list_index]
        
        if cat_name not in asset_item.categories:
            cat_item = asset_item.categories.add()
            cat_item.name = self.categories
        else:
            text = 'Asset is already in "' + str(self.categories.title()) + '" Category.'
            self.report({'INFO'},text)
            
        
        
        wm.asset_sketcher.categories_enum = wm.asset_sketcher.categories_enum
        
        return {"FINISHED"}

class RemoveAssetToCategory(bpy.types.Operator):
    bl_idname = "asset_sketcher.remove_asset_to_category"
    bl_label = "Remove Asset To Category"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        cat_name = asset_sketcher.categories_enum
        
        asset_item = asset_sketcher.asset_list[asset_sketcher.asset_list_index]
        
        for i,cat_item in enumerate(asset_item.categories):
            if cat_item.name == cat_name:
                asset_item.categories.remove(i)
        
        wm.asset_sketcher.categories_enum = wm.asset_sketcher.categories_enum        
                
        return {"FINISHED"}        

class AddAssetCategory(bpy.types.Operator):
    bl_idname = "asset_sketcher.add_asset_category"
    bl_label = "Add Asset Category"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    cat_name = StringProperty(name="Category Name")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        self.cat_name = ""
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        
        if self.cat_name == "":
            self.report({'WARNING'},'Please enter a proper Category Name')
            return {"FINISHED"}
        
        cat_found = False
        self.cat_name = self.cat_name.title()
        for item in asset_sketcher.categories:
            if item.name == self.cat_name:
                self.report({'WARNING'},'Category exists already. Choose a different Name.')
                return {"FINISHED"}
        
        cat = asset_sketcher.categories.add()
        cat.name = self.cat_name
        asset_sketcher.categories_enum = cat.name.upper()
        return {"FINISHED"}
    
class RemoveAssetCategory(bpy.types.Operator):
    bl_idname = "asset_sketcher.remove_asset_category"
    bl_label = "Remove Asset Category"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
#    def invoke(self,context,event):
#        wm = context.window_manager
#        return wm.invoke_confirm(self,event)
    
    def execute(self, context):
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        
        for i,cat in enumerate(asset_sketcher.categories):
            if cat.name.upper() == asset_sketcher.categories_enum and cat.name.upper() != "DEFAULT":
                asset_sketcher.categories.remove(i)
                break
        
        if asset_sketcher.categories_enum == "DEFAULT":
            self.report({'INFO'},'You cannot delete the Default Category')
        if asset_sketcher.categories_enum == "DEFAULT":
            asset_sketcher.categories_enum = "DEFAULT"
        
        return {"FINISHED"}    
        

class AddAssetItem(bpy.types.Operator):
    bl_idname = "asset_sketcher.add_asset_item"
    bl_label = "Add Asset Item"
    bl_description = ""
    bl_options = {"REGISTER"}

    asset_name = StringProperty(default="")    
    
    @classmethod
    def poll(cls, context):
        return True
        
    def draw(self,context):
        row = self.layout.row()
        row.label(text="Asset Name:")
        row.prop(self,"asset_name",text="")
    
    
    def invoke(self,context,event):
        self.asset_name = ""
        if len(context.selected_objects) > 1:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)
        
    def execute(self, context):
        obj = bpy.context.scene.objects.active
        wm = context.window_manager
        
        asset_list = wm.asset_sketcher.asset_list
        asset_list_index = wm.asset_sketcher.asset_list_index
        
        selected_objects = []
        for obj in context.selected_objects:
            if obj.parent == None:
                selected_objects.append(obj)
        
        if len(selected_objects) > 1 and self.asset_name == "":
            self.report({'WARNING'},'Enter an Asset Name.')
            return{'FINISHED'}
        
        if self.asset_name in asset_list or (obj.name in asset_list and len(context.selected_objects) == 1):
            self.report({'WARNING'},'Asset is already in List.')
            return{'FINISHED'}
            
        if obj != None:
            if obj.type in ["MESH","EMPTY"]:
                item = asset_list.add()
                if len(selected_objects) > 1:
                    item.name = self.asset_name
                else:    
                    item.name = obj.name
                
                if obj.type == "MESH" and len(selected_objects) == 1:
                    item.distance = obj.dimensions[0]
                    item.type = 'OBJECT'
                elif obj.type == "EMPTY" and len(selected_objects) == 1:
                    if obj.dupli_group != None:
                        for obj2 in obj.dupli_group.objects:
                            obj2["as_asset"] = True
                            obj2["as_dupli_group"] = obj.name
                    item.type = "EMPTY"    
                
                elif obj.type == "EMPTY" or obj.type == "MESH" and len(selected_objects) > 1:
                    item.type = "GROUP"
                    for obj2 in selected_objects:
                        group_obj = item.group_objects.add()
                        group_obj.name = obj2.name
                        
                        
                        if obj2 .type == "EMPTY" and obj2.dupli_group != None:
                            for obj3 in obj2.dupli_group.objects:
                                obj3["as_asset"] = True
                                obj3["as_dupli_group"] = obj2.name
                        

                wm.asset_sketcher.asset_list_index = len(asset_list)-1
            else:
                self.report({'WARNING'},'Please select a proper Object.')
                return{'FINISHED'}
        else:
            self.report({'WARNING'},'Please select an Asset before adding it to the list.')
        
        wm.asset_sketcher.categories_enum = wm.asset_sketcher.categories_enum
        if wm.asset_sketcher.categories_enum != "DEFAULT":
            bpy.ops.asset_sketcher.add_asset_to_category(categories=wm.asset_sketcher.categories_enum)
        
        return{'FINISHED'}

class RemoveAssetItem(bpy.types.Operator):
    bl_idname = "asset_sketcher.remove_asset_item"
    bl_label = "Remove Object from Assetlist"
    bl_description = "Remove asset or group from the asset list."
    bl_options = {"REGISTER"}
    
    idx = IntProperty()
    
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager 
        return wm.invoke_confirm(self,event)
    
    def execute(self, context):
        wm = context.window_manager
        display_asset = wm.asset_sketcher.display_asset_list[self.idx]
        display_asset_name = display_asset.name
        
        asset_list = wm.asset_sketcher.asset_list
        asset = wm.asset_sketcher.asset_list[display_asset_name]
        idx = 0
        for i,item in enumerate(asset_list):
            if item.name == asset.name:
                idx = i
                break
        
        wm.asset_sketcher.asset_list.remove(i)    
        
        
        
        wm.asset_sketcher.categories_enum = wm.asset_sketcher.categories_enum
        
        return{'FINISHED'}  
    
    
    
class SelectObjects(bpy.types.Operator):
    bl_idname = "asset_sketcher.select_objects" 
    bl_label = "Select all Objects of an Asset"
    bl_description = "Selects all Objects from the selected Asset in the Asset List"
    
    idx = IntProperty()
    mode = EnumProperty(items=(("select","select","select"),("lock","lock","lock"),("unlock","unlock","unlock")))
    
    def invoke(self,context,event):
    
        wm = context.window_manager
        display_asset = wm.asset_sketcher.display_asset_list[self.idx]
        display_asset_name = display_asset.name
        
        asset = wm.asset_sketcher.asset_list[display_asset_name]
        
        if (not event.shift and not event.ctrl):
            for obj in context.scene.objects:
                obj.select = False
            context.scene.objects.active = None    
        
        if asset.type in ["OBJECT","EMPTY","GROUP"]:
            for obj in context.visible_objects:
                if "as_asset_name" in obj:
                    if obj["as_asset_name"] == asset.name:
                        if event.ctrl:
                            obj.select = False
                        else:
                            obj.select = True    
        text = '"'+display_asset_name+'"'+ ' Assets have been selected.'
        self.report({'INFO'}, text)
        return{'FINISHED'}

    
    
      
          