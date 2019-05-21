import bpy, os

from bpy.types import Panel, Operator

bl_info = {
         "name" : "Additional Texture Slots",
         "author" : "Andrew Merizalde <andrewmerizalde@hotmail.com>",
         "version" : (1, 0, 1),
         "blender" : (2, 7, 8),
         "location" : "View 3D > Texture Paint > Tool Shelf > Slots",
         "description" :
             "Add Paint Slots to a Material while in Texture Paint mode. You still have to hook them up in the Node Editor!",
         "warning" : "",
         "wiki_url" : "https://github.com/amerizalde/add_paint_slots",
         "tracker_url" : "",
         "category" : "Paint"}
    
# callback to add a texture to the active material and add a paint slot in Texture Paint mode
class SlotsOperator(Operator):
    bl_idname = "alm.paint_slots"
    bl_label = "Add Paint Slots"
    
    def execute(self, context):
        bpy.ops.paint.add_texture_paint_slot(type="DIFFUSE_COLOR")
        self.report({'INFO'}, "Texture Created!")
        
        return {"FINISHED"}
    
# callback to save the active paint slot's texture
class SaveOperator(Operator):
    bl_idname = "alm.save_image"
    bl_label = "SaveImage"
    
    # 'pointers' for the invoke method to populate
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def get_active_image(self, context):
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]
    
    def path_exists(self, image_path):
        ipath = bpy.path.abspath(image_path)
        if os.path.exists(ipath):
            return True
        
    def execute(self, context):
        slot_image = self.get_active_image(context)
        
        # swap area type
        area = bpy.context.area
        old_type, area.type = area.type, "IMAGE_EDITOR"
        context.space_data.image = slot_image
        
        # function
        if slot_image.filepath == '':
            bpy.ops.image.save_as(filepath=self.filepath)
            self.report({'INFO'}, "{} saved!".format(slot_image.filepath))
        else:
            bpy.ops.image.save_dirty()

        # replace area type
        area.type = old_type
        
        return {"FINISHED"}
    
    
    def invoke(self, context, event):
        slot_image = self.get_active_image(context)
        
        if slot_image.filepath == '' or not self.path_exists(slot_image.filepath):
            context.window_manager.fileselect_add(self)
        else:
            self.execute(context)
    
        return {'RUNNING_MODAL'}


# custom Toolshelf Panel
class View3DPanel(Panel):
    """"""
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Add Textures"
    bl_context = "imagepaint"
    bl_category = "Slots"
    
    def draw(self, context):
        
        layout = self.layout        
        row = layout.row()

        obj = context.object
        
        # Display a label
        str_add_slot = "Add another texture to " + obj.name
        row.label(text=str_add_slot)
        
        # Add a custom operator
        row = layout.row()
        row.operator("alm.paint_slots", text="Add Texture", icon="FACESEL_HLT")
        
        row = layout.row()
        row.operator("alm.save_image", text="Save Dirty", icon="IMAGE_DATA")
        
    
def register():
    bpy.utils.register_class(SlotsOperator)
    bpy.utils.register_class(SaveOperator)
    bpy.utils.register_class(View3DPanel)

    
def unregister():
    bpy.utils.unregister_class(View3DPanel)
    bpy.utils.unregister_class(SlotsOperator)
    bpy.utils.unregister_class(SaveOperator)


if __name__ == "__main__":
    register()
