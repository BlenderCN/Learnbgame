import bpy
from bpy.types import Menu
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
from .ui import draw_color_panel, draw_brush_panel, draw_texture_panel, draw_stencil_panel, draw_layer_panel
preview_collections_pie = {}

class VIEW3D_PIE_coa_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "BPainter"
    bl_idname = "view3d.b_painter_pie_menu"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj != None and obj.mode == "TEXTURE_PAINT":
            return True
    
    def draw(self, context):
        wm = context.window_manager
        scene = context.scene
        layout = self.layout
        ob = context.active_object
        settings = context.scene.tool_settings.unified_paint_settings
        brush = context.scene.tool_settings.image_paint.brush
        ipaint = context.scene.tool_settings.image_paint
        col = None
        
        layout = self.layout
        pie = layout.menu_pie()
        
        #1 left
        op = pie.operator("b_painter.pie_docker_menu",text="Layer",icon="RENDERLAYERS")
        op.docker = "LAYER"
        #2 right
        op = pie.operator("b_painter.pie_docker_menu",text="Stencil",icon="IMAGE_RGB_ALPHA")
        op.docker = "STENCIL"
        #3 bottom
        pie.row()
        #4 top
        op = pie.operator("b_painter.pie_docker_menu",text="Brush",icon="BRUSH_DATA")
        op.docker = "BRUSH"
        #5 top left
        op = pie.operator("b_painter.pie_docker_menu",text="Color",icon="COLOR")
        op.docker = "COLOR"
        #6 top right
        op = pie.operator("b_painter.pie_docker_menu",text="Texture",icon="TPAINT_HLT")
        op.docker = "TEXTURE"
        #7 bottom left
        pie.row()
        #8 bottom right
        pie.row()
        
class PieColorOperator(bpy.types.Operator):
    bl_idname = "b_painter.pie_docker_menu"
    bl_label = "BPainter"
    bl_description = ""
    bl_options = {"INTERNAL"}
    
    docker = StringProperty(default="COLOR")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def check(self,context):
        return True 
    
    def draw(self, context):
        wm = context.window_manager
        scene = context.scene
        layout = self.layout
        ob = context.active_object
        settings = context.scene.tool_settings.unified_paint_settings
        brush = context.scene.tool_settings.image_paint.brush
        ipaint = context.scene.tool_settings.image_paint
        col = None
        
        if self.docker == "COLOR":
            layout.label(text="Color Docker")
            draw_color_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint,pie=True)
        elif self.docker == "BRUSH":
            layout.label(text="Brush Docker")
            draw_brush_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint,pie=True)
        elif self.docker == "TEXTURE":
            layout.label(text="Texture Docker")
            draw_texture_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint,pie=True)
        elif self.docker == "STENCIL":
            layout.label(text="Stencil Docker")
            draw_stencil_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint,pie=True)
        elif self.docker == "LAYER":
            layout.label(text="Layer Docker")
            draw_layer_panel(self,context,wm,scene,layout.column(),ob,settings,brush,ipaint,pie=True)
            
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        return {"FINISHED"}
 

                