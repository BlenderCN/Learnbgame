bl_info = {
   "name": "Useful Menus Add-on",
   "author": "Alan North",
   "version": (0, 2),
   "blender": (2, 79, 0),
   "location": "None, see documentation to set shortcuts.",
   "description": "Lists sculpt brushes (sculpt.list_brushes).",
   "warning": "",
   "wiki_url": "https://github.com/AlansCodeLog/blender-useful-menus-addon",
   "tracker_url": "https://github.com/AlansCodeLog/blender-useful-menus-addon/issues",
   "category": "User Interface",
}

import bpy
import math
import ctypes #to send escape key
from pathlib import Path #to check custom icons are accessible

#PRIVATE METHODS
class BrushSet(bpy.types.Operator):
   bl_idname = "useful_menus.private_brush_set"
   bl_label = "Set scullpt brush"
   name = bpy.props.StringProperty() #needs to be passed to function
   
   def execute(self, context):
      if not self.name == '':
         bpy.context.tool_settings.sculpt.brush = bpy.data.brushes[self.name]
         ctypes.windll.user32.keybd_event(0x1B) #send escape key to exit dialog
      return {'FINISHED'}

#HELPER FUNCTIONS

#get list of brush names
def b_names(): 
   brushlist = []
   index = 0
   for items in bpy.data.brushes:
      if items.use_paint_sculpt:
         brushlist.append(items.name)
         index = index + 1
   return brushlist

#get list of brush types (for brushes that don't have a custom icon
def b_types():
   types = []
   for items in bpy.data.brushes:
      if items.use_paint_sculpt:
         types.append(items.sculpt_tool)
   return types

#CONSTANT VARIABLES
#TODO make configurable?

#the aspect ratio of the buttons (width to height)
scale = 6
#button width in pixels
button_width = 22 * scale

#PUBLIC METHODS
#popup (not a pie menu because with more than 20+ brushes it just got uncomfortable)
class MenuBrushList(bpy.types.Operator):
   bl_idname = "useful_menus.list_brushes" #set shortcut to this to acess
   bl_label = "Brush List"
   
#   DYNAMIC VARIABLES
#   set by invoke so they're dynamic and we don't get access restrict errors when trying to get bpy.data

#   brush_names
#   brush_types
#   ui_scale
#   col_num
#   row_num
   
   def execute(self, context):
      return {'FINISHED'}

   def invoke(self, context, event):
      #SETTING DYNAMIC VARIABLES
      #get our lists
      brush_names = self.brush_names = b_names()
      brush_types = self.brush_types = b_types()
      ui_scale = self.ui_scale = context.user_preferences.view.ui_scale
      #total number of columns and rows
      col_num = self.col_num = math.ceil(math.sqrt(len(brush_names)/scale)) #total number of brushes divided by scale (so real pixel width and height are the same), then sqrt these groups (that represent a 1:1 area) to keep popup relatively square
      row_num = self.row_num = math.ceil(len(brush_names)/col_num)
      
      wm = context.window_manager
      return wm.invoke_popup(self, width=col_num*button_width*ui_scale) 

   def draw(self, context):
      
      #VARIABLES
      layout = self.layout
      toolsettings = context.tool_settings
      brush_names = self.brush_names
      brush_types = self.brush_types
      col_num = self.col_num
      row_num = self.row_num
      
      #TODO different lists depending on context so shortcut can be set once for the general 3D View or different shortcuts for each context
      if context.mode == "SCULPT":
         split = layout.split()
         #for each column
         for col_index in range(col_num):
               #create column
               col = split.column(align=True)
               
               #break if the brushes only reach part of the column
               if col_index*row_num >= len(brush_names): 
                  break
               #for each row 
               for index in range(col_index*row_num, col_index*row_num + row_num):
                  
                  name = brush_names[index]
                  default_icon = "BRUSH_"+brush_types[index]
                  if default_icon == "BRUSH_DRAW": #why!!!
                           default_icon = "BRUSH_SCULPT_DRAW"
                           
                  custom_icon = bpy.data.brushes[name].preview.icon_id
                  #check if the file for the custom icon exists
                  custom_icon_path = Path(bpy.data.brushes[name].icon_filepath).is_file()
                  #does the brush have a custom icon otherwise use default
                  if bpy.data.brushes[name].use_custom_icon and custom_icon_path:
                     col.operator("useful_menus.private_brush_set", text = name, icon_value = custom_icon, emboss=False ).name = name
                  else:     
                     col.operator("useful_menus.private_brush_set", text = name, icon = default_icon, emboss=False).name = name
                  #break if we're at the end
                  if index >= len(brush_names) - 1: 
                     break

def register():
   bpy.utils.register_module(__name__)

def unregister():
   bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
   register()