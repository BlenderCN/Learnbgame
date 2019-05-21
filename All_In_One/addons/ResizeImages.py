bl_info = {
        'name': 'ResizeImages',
        'author': 'code of art, updated to 2.80 by bay raitt',
        'version': (0, 1),
        'blender': (2, 80, 0),
        'category': 'View',
        'location': 'Image Editor > Image > Resize',
        'wiki_url': ''}


import bpy, os
from bpy.types import WindowManager as wm
from bpy.types import Panel, Operator
from bpy.props import *

# Resize then save (main function)
def resize_then_save(prefix, width, save, output, overwrite, all, cleanup):
    images = []
    if all == 'All images':
        images = bpy.data.images[:]
    else:
        if bpy.context.area.spaces.active.image:
            images.append(bpy.context.area.spaces.active.image)
    if len(images) > 0:
        for img in images:            
            x, y = img.size
            if x > 0:
                height = width * y / x
                if height > 0 and width > 0:
                    if not overwrite:
                        new_img = img.copy()
                        new_img.name = get_img_name(prefix + img.name)
                    else: new_img = img
                    if new_img:
                        new_img.scale(width, height)
                        if save:
                            new_img.save_render(os.path.join(output, new_img.name))
                            if cleanup and not overwrite:
                                bpy.data.images.remove(new_img, True) 
                                
# Get image name (Better than .00x)
def get_img_name(name):
    if not bpy.data.images.get(name):
        return name
    i = 1
    while bpy.data.images.get(str(i) + name):
        i += 1
    return str(i) + name                             
 
# Check if everything is OK                            
def ready():
    ready = True
    w_man = bpy.context.window_manager    
    width = w_man.ris_width    
    image = bpy.context.area.spaces.active.image
    
    if w_man.ris_all_images == 'Active image':    
        if image:
            x, y = image.size
            height = width * y / x            
            if width < 1 or height < 1:                
                ready = False
        else: ready = False
    else:
        if len(bpy.data.images[:]) < 1:
            ready = False    
    if w_man.ris_save :
        if not os.path.exists(w_man.ris_output):
            ready = False  
            
    return ready         
                                
            
# Resize then Save
class BR_OT_ResizeThenSave(Operator):
    """Resize Images"""
    bl_idname = "resize_images.resize_then_save"
    bl_label = "Resize"
    bl_description = "Resize the image(s), then save (Optional)."
 
    def execute(self, context):
        w_man = context.window_manager
        prefix = w_man.ris_prefix
        width = w_man.ris_width
        save = w_man.ris_save
        output = w_man.ris_output
        overwrite = w_man.ris_overwrite
        all = w_man.ris_all_images
        cleanup = w_man.ris_cleanup
         
        resize_then_save(prefix, width, save, output, overwrite, all, cleanup)
        return {'FINISHED'}    
     
# The UI
class BR_OT_ResizeImages(Panel):
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"   
    bl_label = "Resize"
             
    def draw(self, context):
        w_man = context.window_manager
        width = w_man.ris_width        
        active_img = context.area.spaces.active.image          
        layout = self.layout
        col = layout.column()
        col.operator("resize_images.resize_then_save", icon = 'UV_SYNC_SELECT')

        col.prop(w_man, 'ris_all_images', text = '')
        col.prop(w_man, 'ris_width')
        if  w_man.ris_all_images == 'Active image':
            if active_img:
                x, y = active_img.size            
                height = width * y / x
                col.label(text = 'Height: ' + str(int(height)), icon = 'INFO')
            else: col.label(text = 'No active image!', icon = 'ERROR')
        else: 
            if len(bpy.data.images[:]) == 0:
                col.label(text = 'Please, load  some images.', icon = 'ERROR')        
        col.prop(w_man, 'ris_overwrite', icon = 'LIBRARY_DATA_OVERRIDE')
        if not w_man.ris_overwrite:
            col.prop(w_man, 'ris_prefix')
            col.prop(w_man, 'ris_save', icon  = 'EXPORT')
            if w_man.ris_save:
                col.prop(w_man, 'ris_output')
                if not os.path.exists(w_man.ris_output):
                    col.label(text = 'Please, select a valid output', icon = 'ERROR')               
                if not w_man.ris_overwrite:
                    col.prop(w_man, 'ris_cleanup')
        col = layout.column()
        col.enabled = ready()


classes = (
    BR_OT_ResizeThenSave,
    BR_OT_ResizeImages,
)



def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    wm.ris_prefix = StringProperty(name = 'Prefix', description = 'Prefix.')
    wm.ris_output = StringProperty(name = 'Output', description = 'Output folder.', subtype='DIR_PATH')
    wm.ris_width = IntProperty(name = 'Width', default = 512, min = 1, max = 20000, description = 'Width of the image.')
    wm.ris_save = BoolProperty(name = 'Save', default = False, description = 'Save the resized image(s) to the output folder.')
    wm.ris_overwrite = BoolProperty(name = 'Overwrite', default = False, description = 'Overwrite the original image by the resized image.')
    wm.ris_cleanup = BoolProperty(name = 'Cleanup', default = False, description = 'Remove the resized image after saving it.')
    wm.ris_all_images = EnumProperty(name = 'All images',
        items = (('Active image','Active image','Resize the active image.'),('All images','All images','Resize all the images')),
        description = 'Resize the active image or all the images.')


                

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del wm.ris_prefix   
    del wm.ris_output 
    del wm.ris_width   
    del wm.ris_save
    del wm.ris_overwrite
    del wm.ris_cleanup
    del wm.ris_all_images
              
if __name__ == "__main__":
    register()    