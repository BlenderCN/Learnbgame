import bpy
from bpy.types import Operator
 

class CustomComment(Operator):
    bl_idname = "text.custom_comment"
    bl_label = "Custom comment"

    def execute(self, context):

        start_selection = bpy.context.space_data.text.current_character
        end_selection = bpy.context.space_data.text.select_end_character
        txt_name = bpy.context.space_data.text.name
        txt = bpy.data.texts[txt_name]
        line_begin = txt.current_line_index

        for line_end, line_obj in enumerate(txt.lines):
            if line_obj == txt.select_end_line:
                break

        selection = [i for i in range(line_begin+1, line_end+2)]
                       
        if line_begin != line_end:
            bpy.ops.text.comment()
            bpy.ops.text.move(type='NEXT_CHARACTER')           

        elif start_selection != end_selection:                    
            bpy.ops.text.cut()
            bpy.ops.text.insert(text="#")
            bpy.ops.text.paste()
            bpy.ops.text.move(type='NEXT_CHARACTER')            
            

        else:
            bpy.ops.text.select_line()
            bpy.ops.text.comment()
            bpy.ops.text.move(type='NEXT_CHARACTER')

        return {'FINISHED'}           
    


class CustomUncomment(Operator):
    bl_idname = "text.custom_uncomment"
    bl_label = "Custom uncomment"

    def execute(self, context):
        txt_name = bpy.context.space_data.text.name
        txt = bpy.data.texts[txt_name]
        line_begin = txt.current_line_index
        start_selection = bpy.context.space_data.text.current_character
        end_selection = bpy.context.space_data.text.select_end_character
        base = context.space_data.text.current_line.body

        for line_end, line_obj in enumerate(txt.lines):
            if line_obj == txt.select_end_line:
                break

        selection = [i for i in range(line_begin+1, line_end+2)]

        if line_begin != line_end:
            bpy.ops.text.uncomment()

        else:
            uncommented_line = bpy.context.space_data.text.current_line.body.split("#")
            bpy.ops.text.select_line()
            bpy.ops.text.delete()
            bpy.ops.text.insert(text=''.join(uncommented_line))
                          
        return {'FINISHED'}


class CustomCopy(Operator):
    bl_idname = "text.custom_copy"
    bl_label = "Custom copy"
    
    clipboard_list = []
    
    def execute(self, context):
        select_loc = bpy.context.space_data.text.select_end_character
        cursor_loc = bpy.context.space_data.text.current_character
        txt_name = bpy.context.space_data.text.name
        txt = bpy.data.texts[txt_name]
        line_begin = txt.current_line_index        
        
        context.window_manager.multi_line_enabled = False
        context.window_manager.clipboard = ""
        
        for line_end, line_obj in enumerate(txt.lines):
            if line_obj == txt.select_end_line:
                break

        if line_begin < line_end:
            selection = [i for i in range(line_begin, line_end+1)] 
        else:
            selection = [i for i in range(line_end,line_begin+1)] 

        if line_begin != line_end:
                                  
            line_to_copy_tmp = []  
            indent_list = []          
           
            for index in selection:                
                context.space_data.text.current_line_index = index
                base = context.space_data.text.current_line.body 
                if base.count(" ") == len(base):
                    line_to_copy_tmp.append(" ")
                    indent_list.append(50)
                             
                else:                   
                    if base.startswith("    "):
                        bpy.ops.text.move(type='LINE_BEGIN')
                        bpy.ops.text.move(type='NEXT_WORD')
                    start_copy = context.space_data.text.current_character
                    line_to_copy_tmp.append(base[start_copy:])
                    indent_list.append(int(start_copy/4))                   
            
            for indent in indent_list:
                if indent == 50:
                    indent_list[indent_list.index(indent)] = min([indent for indent in indent_list])
          
            index = 0
            for line in line_to_copy_tmp:
                self.clipboard_list.append("    "*(indent_list[index]-min([indent for indent in indent_list])) + line + "\n")
                index +=1
           
            context.window_manager.clipboard = ''.join(self.clipboard_list)

            del(line_to_copy_tmp[:])
            del(indent_list[:])
            del(self.clipboard_list[:])
            
            context.window_manager.multi_line_enabled = True
            
            bpy.ops.text.move(type='LINE_END')                
                                 
        elif cursor_loc != select_loc:            
            bpy.ops.text.copy()
            bpy.ops.text.move(type='NEXT_CHARACTER')
            
        else:
            base = context.space_data.text.current_line.body
            end_copy = context.space_data.text.current_character
            if base.startswith("    "):
                bpy.ops.text.move(type='LINE_BEGIN')
                bpy.ops.text.move(type='NEXT_WORD')
                current_character = context.space_data.text.current_character
                bpy.context.window_manager.clipboard = base[current_character:end_copy]
                for character in base[current_character:end_copy]:
                    bpy.ops.text.move(type='NEXT_CHARACTER')
                
            else:
                bpy.context.window_manager.clipboard = base[:end_copy]
         
        return {'FINISHED'}

    
class CustomCut(Operator):
    bl_idname = "text.custom_cut"
    bl_label = "Custom cut"
    
    clipboard_list = []
    
    def execute(self, context):
        select_loc = bpy.context.space_data.text.select_end_character
        cursor_loc = bpy.context.space_data.text.current_character
        txt_name = bpy.context.space_data.text.name
        txt = bpy.data.texts[txt_name]
        line_begin = txt.current_line_index                   
        
        context.window_manager.multi_line_enabled = False
        context.window_manager.clipboard = ""
        
        for line_end, line_obj in enumerate(txt.lines):
            if line_obj == txt.select_end_line:
                break
        
        if line_begin < line_end:
            selection = [i for i in range(line_begin, line_end+1)] 
        else:
            selection = [i for i in range(line_end,line_begin+1)] 
        
        if line_begin != line_end:
         
            line_to_cut_tmp = []  
            indent_list = []          
         
            for index in selection:                
                context.space_data.text.current_line_index = index
                base = context.space_data.text.current_line.body 
                if base.count(" ") == len(base):
                    line_to_cut_tmp.append(" ")         
                    indent_list.append(50)
                 
                else:                   
                    if base.startswith("    "):
                        bpy.ops.text.move(type='LINE_BEGIN')
                        bpy.ops.text.move(type='NEXT_WORD')
                    start_copy = context.space_data.text.current_character
                    line_to_cut_tmp.append(base[start_copy:])
                    indent_list.append(int(start_copy/4))
                    bpy.ops.text.select_line()
                    bpy.ops.text.delete()                 
             
            for indent in indent_list:
                if indent == 50:
                    indent_list[indent_list.index(indent)] = min([indent for indent in indent_list])

            index = 0
            for line in line_to_cut_tmp:
                self.clipboard_list.append("    "*(indent_list[index]-min([indent for indent in indent_list])) + line + "\n")
                index +=1
         
            context.window_manager.clipboard = ''.join(self.clipboard_list)
         
            del(line_to_cut_tmp[:])
            del(indent_list[:])
            del(self.clipboard_list[:])
         
            context.window_manager.multi_line_enabled = True
                              
        elif cursor_loc != select_loc:            
            bpy.ops.text.cut()
            
        else:
            base = context.space_data.text.current_line.body
            end_copy = context.space_data.text.current_character
            if base.startswith("    "):
                bpy.ops.text.move(type='LINE_BEGIN')
                bpy.ops.text.move(type='NEXT_WORD')
                current_character = context.space_data.text.current_character
                bpy.context.window_manager.clipboard = base[current_character:end_copy]
                for character in base[current_character:end_copy]:
                    bpy.ops.text.move_select(type='NEXT_CHARACTER')
                bpy.ops.text.delete()
                
            else:
                bpy.context.window_manager.clipboard = base[:end_copy]
                bpy.ops.text.move(type='LINE_BEGIN')
                for character in base[:end_copy]:
                    bpy.ops.text.move_select(type='NEXT_CHARACTER')
                bpy.ops.text.delete()                   
        
        return {'FINISHED'}
    

def custom_punctuation_function(punctuation):
    base = bpy.context.space_data.text.current_line.body
    select_loc = bpy.context.space_data.text.select_end_character
    cursor_loc = bpy.context.space_data.text.current_character
    txt_name = bpy.context.space_data.text.name
    txt = bpy.data.texts[txt_name]
    line_begin = txt.current_line_index

    for line_end, line_obj in enumerate(txt.lines):
        if line_obj == txt.select_end_line:
            break

    selection = [i for i in range(line_begin, line_end)] 
    
    if cursor_loc != select_loc or line_begin != line_end:
        bpy.ops.text.cut()
        bpy.ops.text.insert(text=punctuation)
        bpy.ops.text.move(type='PREVIOUS_CHARACTER')
        bpy.ops.text.paste()
        bpy.ops.text.move(type='NEXT_CHARACTER')                                
    else:
        if punctuation == '"'*2 and cursor_loc < len(base) and base[cursor_loc] == '"':
            bpy.ops.text.insert(text='"')
            
        elif punctuation == "'"*2 and cursor_loc < len(base) and base[cursor_loc] == "'":
            bpy.ops.text.insert(text="'")
            
        else:  
            bpy.ops.text.insert(text=punctuation)
            bpy.ops.text.move(type='PREVIOUS_CHARACTER')            

    
class CustomDoubleQuote(Operator):
    bl_idname = "text.custom_double_quote"
    bl_label = "Double quote"
    
    def execute(self, context):

        custom_punctuation_function('"'*2)
   
        return {'FINISHED'}


class CustomSimpleQuote(Operator):
    bl_idname = "text.custom_simple_quote"
    bl_label = "Simple quote"

    def execute(self, context):

        custom_punctuation_function("''")
        
        return {'FINISHED'}
    
    
class CustomBracket(Operator):
    bl_idname = "text.custom_bracket"
    bl_label = "Bracket"
    
    def execute(self, context):
        custom_punctuation_function("()")
        
        return {'FINISHED'}


class CustomSquareBracket(Operator):
    bl_idname = "text.custom_square_bracket"
    bl_label = "Square bracket"
    
    def execute(self, context):
        custom_punctuation_function("[]")
        
        return {'FINISHED'}


class CustomBrace(Operator):
    bl_idname = "text.custom_brace"
    bl_label = "Brace"
    
    def execute(self, context):
        custom_punctuation_function("{}")
    
        return {'FINISHED'}


class CustomPaste(Operator):
    bl_idname = "text.custom_paste"
    bl_label = "Paste"

    to_copy_tmp = []
    
    def execute(self, context):
        if context.window_manager.multi_line_enabled:
            self.to_copy_tmp.append(context.window_manager.clipboard)

            base_indent = int(context.space_data.text.current_character/4)
            
            # first line of the selection
            bpy.ops.text.insert(text=''.join(self.to_copy_tmp).split("\n")[0])

            for line in ''.join(self.to_copy_tmp).split("\n")[1:-1]:
                bpy.ops.text.insert(text="\n" + "    "*base_indent + line)
            bpy.ops.text.insert(text="\n" + "    "*base_indent + ''.join(self.to_copy_tmp).split("\n")[-1])           
                        
            del(self.to_copy_tmp[:])
            return {'FINISHED'}

        else: 
            bpy.ops.text.paste()
            
            return {'FINISHED'}