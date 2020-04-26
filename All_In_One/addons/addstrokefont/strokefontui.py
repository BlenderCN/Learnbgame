#
#
# UI classes and registration, unregistration functions for Blender Stroke Font add-on.
#
# Copyright (C) 2019  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/blenderstrokefont/blob/master/LICENSE)
#
# Not yet pep8 compliant 

import bpy
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, PointerProperty
from bpy.types import PropertyGroup, Object, Operator, Panel
from mathutils import Vector

from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d
from gpu_extras.batch import batch_for_shader
import bgl, bpy, gpu, gpu_extras

from . strokefontmain import main, getfontNameList

class AddStrokeFontTextParams(PropertyGroup):

    text : StringProperty(name="Text", default = 'Text',
            description='Text to add')

    fontName : EnumProperty(name = "Font", description='Text Font', items = getfontNameList)
    
    fontSize : FloatProperty(name = "Font Size", description='Text Font Size', default = 0.25)

    charSpacing : FloatProperty(name = "Char Spacing", 
        description='Spacing between characters', default = 1)

    lineSpacing : FloatProperty(name = "Line Spacing", 
        description='Spacing between lines', default = 1)

    margin : FloatProperty(name = "Margin", 
        description='Margin from edges of confined area', default = 0.5)

    width : FloatProperty(name = "Area Width", 
        description='Width of confined area', default = 5)

    height : FloatProperty(name = "Area Height", 
        description='Height of confined area', default = 7)

    hAlignment : EnumProperty(name = "Horizontal Alignment", \
        description='Horizontal text aligment in confined area', \
        items = (('left','Left','Left alignment'),\
        ('right','Right','Left alignment'),\
        ('center','Center','Center alignment'),\
        ('justified','Justified','Justified text')), default = 'justified')
    
    vAlignment : EnumProperty(name = "Vertical Alignment", \
        description='Vertical text aligment in confined area', \
        items = (('none','None','No Alignment'),\
        ('top','Top','Align to top of area'),\
        ('center','Center','Align to center of area'),\
        ('bottom','Bottom','Align to bottom of area')), default = 'center')

    action : EnumProperty(name = "Action", description='Text Source', \
        items = [('addInputText', 'Add Input Text', 'Add text from input text box'), \
        ('addFromFile','Add Text From File','Add text from file (choose the file below)'), \
        ('addGlyphTable','Add Glyph Table','Add all glyphs of selected font')])

    filePath : StringProperty(name = 'File Path', subtype='FILE_PATH')

    copyPropertiesCurve : PointerProperty(
            name = 'Properties of', 
            description = "Copy Properties (Material, Bevel Depth etc.) of curve on to the text",
            type = Object)

    cloneGlyphs : BoolProperty(name="Clone Glyphs", default = True, \
        description='Common data for the same glyphs')

    confined : BoolProperty(name="Confine Area", default = False, \
        description='Render text in confined 2d area')

    expandDir : EnumProperty(name = "Expand Direction", \
        description='Expand direction after confine area is full', \
        items = (('x', 'X', 'Expand in X direction'),\
        ('y', 'Y', 'Expand in Y direction'),\
        ('z', 'Z', 'Expand in Z direction'), \
        ('none', 'None', "Don't create expanded areas")), 
        default = 'z' )
        
    expandDist : FloatProperty(name = "Expand Offset", 
        description='Offset between text areas', default = -0.1)

    addPlane : BoolProperty(name="Add Plane", default = False, \
        description='Add a plane object under the text')

class AddStrokeFontOp(Operator):
    bl_idname = "object.add_stroke_font_text"
    bl_label = "Add Stroke Font Text"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):            
        main(context)
        return {'FINISHED'}

class AddStrokeFontTextPanel(Panel):    
    bl_label = "Stroke Font Text"
    bl_idname = "CURVE_PT_strokefonttext"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.objectmode'

    def draw(self, context):
        params = context.window_manager.AddStrokeFontTextParams
        layout = self.layout
        layout.use_property_split = True

        obj = context.object
        col = layout.column()

        col.prop(params, "action")
        
        if(params.action == 'addFromFile'):
            col.prop(params, 'filePath')
        elif(params.action == 'addInputText'):
            col.prop(params, 'text')

        col.prop(params, "fontName")
        col.prop(params, "fontSize")
        col.prop(params, "charSpacing")
        col.prop(params, "lineSpacing")
        
        #TODO: Get rid of this workaround
        try:
            if(params.copyPropertiesCurve != None):
                params.copyPropertiesCurve.data
        except:
            params.copyPropertiesCurve = None
            
        col.prop(params, "copyPropertiesCurve")        
        
        if(params.action != 'addGlyphTable'):
            col.prop(params, "cloneGlyphs")
            col.prop(params, "confined")
        
            if(params.confined):            
                col.prop(params, "width")
                col.prop(params, "height")
                col.prop(params, "margin")            
                col.prop(params, "hAlignment")
                col.prop(params, "vAlignment")
                col.prop(params, "expandDir")
                if(params.expandDir != 'none'):
                    col.prop(params, "expandDist")
                col.prop(params, "addPlane")
            
        col.operator("object.add_stroke_font_text")

class ModalCreateBoxOp(Operator):
    bl_description = "Create Text Boxes"
    bl_idname = "wm.create_text_boxes"
    bl_label = "Create Text Boxes"
    
    def cleanup(self, context):
        if(self.drawHandlerRef):
            bpy.types.SpaceView3D.draw_handler_remove(self.drawHandlerRef, "WINDOW")

    def modal (self, context, event):
        if(event.type == "ESC" or \
            (not hasattr(context.space_data, 'region_3d') and event.value == 'CLICK')):
            self.cleanup(context)
            return {'CANCELLED'}
        
        if context.area:
            context.area.tag_redraw()

        if(event.type == 'BACK_SPACE' and event.value == 'CLICK'):
            if(len(self.rectangles) > 0):
                self.rectangles.pop()
            self.createBatch()                
            return {'RUNNING_MODAL'}
                
        elif(event.type == "RET"):
            self.cleanup(context)
            ret = main(context, self.rectangles)
            if(ret == 'NO_GLYPHS'):
                self.report({'WARNING'}, "No glyphs in the font choosen")                
            return {'FINISHED'}            
            
        if (event.type == "LEFTMOUSE" and event.value == "CLICK"):
            self.capture = not self.capture
            if(self.capture):
                loc = self.getLoc(context, event)
                self.rectangles.append([None] * 2)
                self.rectangles[-1][0] = loc
            return {'RUNNING_MODAL'}

        if (event.type == "MOUSEMOVE" and self.capture):
            self.rectangles[-1][1] = self.getLoc(context, event)
            self.createBatch()
            return {'RUNNING_MODAL'}
            
        return {"PASS_THROUGH"}

    def rectCornerVects(rect):
        p0 = rect[0]            
        p1 = Vector((rect[1][0], rect[0][1], rect[0][2]))
        p2 = Vector((rect[1][0], rect[1][1], rect[0][2]))#Use z of first loc
        p3 = Vector((rect[0][0], rect[1][1], rect[0][2]))
        return [p0, p1, p2, p3]
        
    def createBatch(self):
        positions = []
        for r in self.rectangles:
            p0, p1, p2, p3 = ModalCreateBoxOp.rectCornerVects(r)
            positions += [p0, p1, p1, p2, p2, p3, p3, p0]
        self.batch = batch_for_shader(self.shader, "LINES", {"pos": positions})            
        
    def getLoc(self, context, event):
        coord = event.mouse_region_x, event.mouse_region_y
        region = context.region
        rv3d = context.space_data.region_3d
        vec = region_2d_to_vector_3d(region, rv3d, coord)
        return region_2d_to_location_3d(region, rv3d, coord, vec)        
        
    def drawHandler(self):
        if(not self.batch):
            return
        bgl.glLineWidth(5)
        self.batch.draw(self.shader)

    def execute(self, context):
        self.rectangles = []
        self.drawHandlerRef = bpy.types.SpaceView3D.draw_handler_add(self.drawHandler, \
            (), "WINDOW", "POST_VIEW")
        
        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")                
        self.shader.uniform_float("color", (1, 0.1, 0.1, 1.0))                
        self.shader.bind()        
        self.batch = None
        self.capture = False
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

keymap = None

def register():
    bpy.utils.register_class(AddStrokeFontTextPanel)
    bpy.utils.register_class(AddStrokeFontOp)
    
    bpy.utils.register_class(AddStrokeFontTextParams)
    bpy.types.WindowManager.AddStrokeFontTextParams = \
        bpy.props.PointerProperty(type = AddStrokeFontTextParams)
    bpy.utils.register_class(ModalCreateBoxOp)
    
    c = bpy.context.window_manager.keyconfigs.addon
    if(c):
        m = c.keymaps.new(name='3D View', space_type='VIEW_3D')   
        i = m.keymap_items.new("wm.create_text_boxes", 'Q', 'PRESS', \
            shift = True, ctrl = True)
        keymap = (m, i)

def unregister():
    bpy.utils.unregister_class(AddStrokeFontTextPanel)
    bpy.utils.unregister_class(AddStrokeFontOp)
    
    del bpy.types.WindowManager.AddStrokeFontTextParams
    bpy.utils.unregister_class(AddStrokeFontTextParams)
    
    if(keymap != None):
        keymap[0].keymap_items.remove(keymap[1])
    
    bpy.utils.unregister_class(ModalCreateBoxOp)
