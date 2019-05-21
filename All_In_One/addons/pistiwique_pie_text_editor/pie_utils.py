import bpy
from bpy.types import Operator
import os
from os.path import join, dirname
from . pie import *

custom_class_list = []
custom_fonction_list = []
custom_module_list = []

class InitPieTextPlus(Operator):
    bl_idname = "text.init_pie_text_plus"
    bl_label = "Pie text plus"
    
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name='pie.text_plus')
        
        return {'FINISHED'}
    
    
class InitPieTextEditor(Operator): 
    bl_idname = "text.init_pie_text_editor"
    bl_label = "Pie text editor"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name='pie.text_editor')
        
        return {'FINISHED'}


class InitChooseModule(Operator):
    bl_idname = "text.init_choose_module"
    bl_label = "Init choose module" 
    
    def execute(self, context):
        del(custom_module_list[:])
        txt = bpy.context.space_data.text.name
        file = bpy.data.texts[txt]
        directory_list = os.listdir(join(os.path.dirname(file.filepath)))
        for files in directory_list:
            if files.endswith('.py'):
                custom_module_list.append(files)
                
        bpy.ops.wm.call_menu(name="text.choose_module_menu")             
                                       
        return {'FINISHED'}
        
        
class ChooseModule(Operator):
    bl_idname = "text.choose_module"
    bl_label = "Choose_module"
    
    module = bpy.props.StringProperty(default="")
    
    def execute(self, context):
        txt = bpy.context.space_data.text.name
        file = bpy.data.texts[txt]
        directory = os.path.dirname(file.filepath)
        text = None
        for text_block in bpy.data.texts:
            if text_block.filepath == join(directory, self.module):
                text = text_block
                break
        if not text:
            text = bpy.data.texts.load(join(directory, self.module), internal=False)
        
        context.space_data.text = text
        
        return {'FINISHED'}
    
    
class ChooseModulePanel(bpy.types.Menu):
    bl_idname = "text.choose_module_menu"
    bl_label = "Choose module menu"
    
    def draw(self, context):
        layout = self.layout
        for item in custom_module_list:
            op = layout.operator("text.choose_module", text=item)
            op.module = item
            
                   
class InitJumpToClass(Operator):
    bl_idname = "text.init_jump_to_class"
    bl_label = "Init jump to class"
    
    def execute(self, context):
        del(custom_class_list[:])
        txt = bpy.context.space_data.text.name
        text = bpy.data.texts[txt]
        current_line = bpy.context.space_data.text.current_line_index
        for i in range(len(text.lines)):
            bpy.context.space_data.text.current_line_index = i
            base = bpy.context.space_data.text.current_line.body
            if "class " == base[:6]:
                custom_class_list.append((base.split("(")[0], bpy.context.space_data.text.current_line_index))

        bpy.context.space_data.text.current_line_index = current_line

        bpy.ops.wm.call_menu(name="text.jump_class_menu")
        
        return {'FINISHED'}


class JumpToClass(Operator):
    bl_idname = "text.jump_to_class"
    bl_label = "Jump to class"
    
    class_index = bpy.props.StringProperty(default="") 
    
    def execute(self, context):
        bpy.ops.text.jump(line=int(self.class_index)+1)
        
        return {'FINISHED'}
    
                
class JumpClassMenu(bpy.types.Menu):
    bl_idname = "text.jump_class_menu"
    bl_label = "Jump to class"    

    def draw(self, context):
        layout = self.layout  
        if not len(custom_class_list):
            layout.label('No class in " ' + str(bpy.context.space_data.text.name) + ' "')          
        for item in custom_class_list:
            op = layout.operator("text.jump_to_class", text=item[0])
            op.class_index = str(item[1])
            

class InitJumpToFonction(Operator):
    bl_idname = "text.init_jump_to_fonction"
    bl_label = "Init jump to fonction"
    
    def execute(self, context):  
        del(custom_fonction_list[:])      
        txt = bpy.context.space_data.text.name  
        text = bpy.data.texts[txt] 
        current_line = bpy.context.space_data.text.current_line_index
        for i in range(len(text.lines)):    
            bpy.context.space_data.text.current_line_index = i
            base = bpy.context.space_data.text.current_line.body
            if "def " == base[:4]:
                custom_fonction_list.append((base.split("(")[0], bpy.context.space_data.text.current_line_index))

        bpy.context.space_data.text.current_line_index = current_line
                    
        bpy.ops.wm.call_menu(name="text.jump_fonction_menu")
        
        return {'FINISHED'}


class JumpToFonction(Operator):
    bl_idname = "text.jump_to_fonction"
    bl_label = "Jump to fontion"
    
    fonction_index = bpy.props.StringProperty(default="") 
    
    def execute(self, context):
        bpy.ops.text.jump(line=int(self.fonction_index)+1)
        
        return {'FINISHED'}
    
                
class JumpFonctionMenu(bpy.types.Menu):
    bl_idname = "text.jump_fonction_menu"
    bl_label = "Jump to fonction"    

    def draw(self, context):
        layout = self.layout 
        if not len(custom_fonction_list):
            layout.label('No fonction in " ' + str(bpy.context.space_data.text.name) + ' "') 
        for item in custom_fonction_list:
            op = layout.operator("text.jump_to_fonction", text=item[0])
            op.fonction_index = str(item[1])

class InitCommentUncomment(bpy.types.Operator):
    bl_idname = "text.init_comment_uncomment"
    bl_label = "Comment Uncomment"
 
    def execute(self, context):
        if "#" in context.space_data.text.current_line.body:
            bpy.ops.text.custom_uncomment()
        else:
            bpy.ops.text.custom_comment()
        
        return {"FINISHED"}      