import bpy

 
class SearchCustomProperties(bpy.types.Operator):
    bl_idname = "cpe.search_custom_properties"
    bl_label = "Search Custom Properties"
    bl_description = "Search for custom properties on selected objects"
    bl_options = {"REGISTER"}

    def execute(self, context):
        settings = context.scene.custom_props_edit
        settings.property_edit_settings.clear()
        
        property_names = set()
        for object in context.selected_objects:
            property_names.update(object.keys())
            
        for name in property_names:
            item = settings.property_edit_settings.add()
            item.property_name = name
        
        context.area.tag_redraw()
        return {"FINISHED"}
        
        
class RemoveSelectedProperties(bpy.types.Operator):
    bl_idname = "cpe.remove_selected_properties"
    bl_label = "Remove Selected Properties"
    bl_description = "Remove selected custom properties on selected objects (maybe some properties cannot be removed)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        settings = context.scene.custom_props_edit
        targets = context.selected_objects
        
        
        for i, item in enumerate(settings.property_edit_settings):
            if item.remove:
                self.remove_property(item.property_name, targets)
            
        bpy.ops.cpe.search_custom_properties()
        context.area.tag_redraw()
        return {"FINISHED"}
                
    def remove_property(self, name, objects):
        for object in objects:
            if name in object: del object[name]