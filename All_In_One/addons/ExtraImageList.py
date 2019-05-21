#-------------------------------------------------------------------------------
#                      Extra Image List - Addon for Blender
# Version: 0.1
# Revised: 02.03.2017
# Author: Miki (Meshlogic)
#
# released under CC-By
# http://www.blendswap.com/blends/view/87714
#-------------------------------------------------------------------------------
bl_info = {
    "name": "Extra Image List",
    "author": "Meshlogic",
    "category": "UV",
    "description": "Alternative image browse list with tiles for UV/Image Editor.",
    "location": "UV/Image Editor > Tools > Extra Image List",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "wiki_url": "http://www.blendswap.com/blends/view/87714",
}

import bpy
from bpy.props import *
from bpy.types import Menu, Operator, Panel, UIList


#-------------------------------------------------------------------------------
# UI PANEL
#------------------------------------------------------------------------------- 
class ExtraImageList_PT(Panel):
    bl_label = "Extra Image List"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Extra Image List"

    def draw(self, context):
        layout = self.layout
        cs = context.scene
        cs_props = cs.extra_image_list

        #--- Get the current image in UV editor and list of all images
        img = context.space_data.image
        img_list = bpy.data.images
                
        #--- Num. of rows & cols for image browse list
        row = layout.row()
        split = row.split(percentage=0.6)
        
        col = split.column(True)
        col.prop(cs.extra_image_list, "rows")
        col.prop(cs.extra_image_list, "cols")
        
        #--- Navigation button PREV
        sub = split.column()
        sub.scale_y = 2
        sub.operator("extra_image_list.nav", text="", icon='BACK').dir = 'PREV'
        
        # Disable button for the first image or for no images
        sub.enabled = (img!=img_list[0] if (img!=None and len(img_list)>0) else False)
        
        #--- Navigation button NEXT
        sub = split.column()
        sub.scale_y = 2
        sub.operator("extra_image_list.nav", text="", icon='FORWARD').dir = 'NEXT'
        
        # Disable button for the last image or for no images
        sub.enabled = (img!=img_list[-1] if (img!=None and len(img_list)>0) else False)
        
        #--- Image browse list
        layout.template_ID_preview(context.space_data, "image",
            new="image.new", open="image.open",
            rows=cs_props.rows, cols=cs_props.cols)
        
        #--- Image Info
        if img != None:
            row = layout.row()
            row.label("Source:", icon='DISK_DRIVE')
            row = layout.row(True)
            
            if not img.packed_file:
                row.operator("image.pack", text="", icon='UGLYPACKAGE')
            else:
                row.operator("image.unpack", text="", icon='PACKAGE')
                
            row.prop(img, "filepath", text="")
            row.operator("image.reload", text="", icon='FILE_REFRESH')
            
            #--- Image size
            row = layout.row()
            row.alignment = 'LEFT'
            
            if img.has_data:
                row.label("Size:", icon='TEXTURE')
                row.label(str(img.size[0])+" x "+str(img.size[1])+" x "+str(img.depth)+"b")
            else:
                row.label("Can't load image file!", icon='ERROR')

            #--- Scan
            row = layout.row()
            row = layout.row()
            row.alignment = 'LEFT'
            row.operator("extra_image_list.clear", text="  Clear All Image Users  ", icon='RADIO')


#-------------------------------------------------------------------------------
# IMAGE NAVIGATION OPERATOR
#------------------------------------------------------------------------------- 
class ExtraImageList_PT_Nav(Operator):
    bl_idname = "extra_image_list.nav"
    bl_label = "Nav"
    bl_description = "Navigation button"
 
    dir = EnumProperty(
        name = "dir", default = 'NEXT',
        items = [
            ('NEXT', "PREV", "PREV"),
            ('PREV', "PREV", "PREV")
        ])
 
    def execute(self, context):
        # Get list of all images
        img_list = list(bpy.data.images)
        
        # Get index of current image in UV editor, return if there is none image
        img = context.space_data.image
        if img in img_list:
            id = img_list.index(img)
        else:
            return{'FINISHED'}
        
        # Navigate
        if self.dir == 'NEXT':
            if id+1 < len(img_list):
                context.space_data.image = img_list[id+1]

        if self.dir == 'PREV':
            if id > 0:
                context.space_data.image = img_list[id-1]
 
        return{'FINISHED'}
    
    
#-------------------------------------------------------------------------------
# CLEAR USERS OPERATOR
#------------------------------------------------------------------------------- 
class ExtraImageList_PT_Clear(Operator):
    bl_idname = "extra_image_list.clear"
    bl_label = "Clear Users"
    bl_description = """[Use with caution]
        Clear all users for this image datablock.
        So the image datablock can disappear after save and reload of this blend file."""

    def execute(self, context):
        img = context.space_data.image
        
        if img != None:
            img.user_clear()
            
        return{'FINISHED'}
    
        
#-------------------------------------------------------------------------------
# CUSTOM SCENE PROPS
#-------------------------------------------------------------------------------        
class ExtraImageList_Props(bpy.types.PropertyGroup):
    
    rows = IntProperty(
        name = "Rows",
        description = "Num. of rows in image browse list",
        default = 5, min = 1, max = 15)
        
    cols = IntProperty(
        name = "Cols",
        description = "Num. of columns in image browse list",
        default = 10, min = 1, max = 30)
        

#-------------------------------------------------------------------------------
# REGISTER/UNREGISTER ADDON CLASSES
#-------------------------------------------------------------------------------
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.extra_image_list = PointerProperty(type=ExtraImageList_Props)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.extra_image_list
    
if __name__ == "__main__":
    register()
    
