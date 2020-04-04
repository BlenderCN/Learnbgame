bl_info = {
    "name": "Write Arabic Text",
    "author": "ﻦﻳﺪﻟﺍ ﻲﺤﻣ ﺪﻴﺷﺭ",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3Dviewport, Text edit mode",
    "description": "ﺔﻴﺑﺮﻌﻟﺍ ﺔﻐﻠﻟﺎﺑ ﺺﻧ ﺔﺑﺎﺘﻛ",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

import bpy

#

text_buffer = []

current_char_index = 0


# Arabic letters list

arabic_chars = ['ا', 'أ', 'إ', 'آ', 'ء', 'ب', 'ت', 'ث', 'ج',
                'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص',
                'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل',
                'م', 'ن', 'ه', 'ة','و', 'ؤ', 'ي', 'ى', 'ئ', 'ـ']


# Arabic letters that need to be connected to the letter preceding them
                
right_connectable_chars = ['ا', 'أ', 'إ', 'آ', 'ب', 'ت', 'ث', 'ج', 'ح',
                           'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض',
                           'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م',
                           'ن', 'ه', 'ة','و', 'ؤ', 'ي', 'ى', 'ئ', 'ـ']


# Arabic letters that need to be connected to the letter next to them
                           
left_connectable_chars = ['ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'س', 'ش', 'ص',
                          'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل',
                          'م', 'ن', 'ه', 'ي', 'ى', 'ئ', 'ـ']


# Locations (unicode) of Arabic letters shapes (when they are connected to other letters)

#                          ا       أ       إ       آ       ء       ب       ت       ث       ج
chars_variants_bases = [0xFE8D, 0xFE83, 0xFE87, 0xFE81, 0xFE80, 0xFE8F, 0xFE95, 0xFE99, 0xFE9D,
#                          ح       خ       د       ذ       ر       ز       س       ش       ص 
                        0xFEA1, 0xFEA5, 0xFEA9, 0xFEAB, 0xFEAD, 0xFEAF, 0xFEB1, 0xFEB5, 0xFEB9, 
#                          ض       ط       ظ       ع       غ       ف       ق       ك       ل
                        0xFEBD, 0xFEC1, 0xFEC1, 0xFEC9, 0xFECD, 0xFED1, 0xFED5, 0xFED9, 0xFEDD,
#                          م       ن       ه       ة       و       ؤ       ي       ى       ئ
                        0xFEE1, 0xFEE5, 0xFEE9, 0xFE93, 0xFEED, 0xFE85, 0xFEF1, 0xFEEF, 0xFE89]


# Check if a letter should be connected to the letter preceding it

def is_right_connectable(c):
    
    if c in right_connectable_chars:
        
        return True
    
    return False


# Check if a letter should be connected to the letter next to it

def is_left_connectable(c):
    
    if c in left_connectable_chars:
        
        return True
    
    return False        


# Index of an Arabic letter in the list above

def get_char_index(c):

    if c not in arabic_chars: # not an arabic char
        
        return -1
    
    return arabic_chars.index(c)


# Get the location (unicode id) of an Arabic letter shapes (when connected)

def get_char_variants_base(c):
    
    char_index = get_char_index(c)
    
    if char_index == -1: # It's not an arabic char
        
        return -1
    
    return chars_variants_bases[char_index]


# Link Arabic letters

def link_text(unlinked_text):
    
    #
    
    linked_text = []
    
    previous_char = ""
    
    next_char = ""
    
    char_code = 0
    
    skip_char = False
    
    # When the letter "Alef" is connected to the letter "Lem" they become one letter
    # but the buffer still contains the two
    
    uncounted_chars = 0
    
    #
    
    for current_char in unlinked_text:
        
        #
        
        if skip_char:
            skip_char = False
            continue
        
        #
        
        previous_char = ""
        next_char = ""

        #
        
        chars_count = len(linked_text) + uncounted_chars
        
        if chars_count > 0:
            previous_char = unlinked_text[chars_count - 1]
            
        if chars_count < len(unlinked_text) - 1:
            next_char = unlinked_text[chars_count + 1]
        
        # Lem-Alef
        # Tehere are four forms of this letter
        
        if current_char == 'ل':
            
            if next_char == 'ا':
                
                char_code = 0xFEFB
                
            elif next_char == 'أ':
                
                char_code = 0xFEF7
                
            elif next_char == 'إ':
                
                char_code = 0xFEF9
                
            elif next_char == 'آ':
                
                char_code = 0xFEF5
                
            else:
                
                char_code = 0
            
            if char_code != 0:
                
                if is_left_connectable(previous_char):
                    
                    char_code += 1
                    
                linked_text.insert(0, chr(char_code))
                
                uncounted_chars += 1
                
                skip_char = True
                
                continue
        
        # Tamdeed
            
        if(current_char == 'ـ'): 
            
            linked_text.insert(0, 'ـ')
            
            continue

        # Space
        
        if(current_char == ' '):
            
            linked_text.insert(0, ' ')
            
            continue
        
        # Line break
        
        if(current_char == '\n'):
            
            linked_text.insert(0, '\n')
            
            continue
        
        # Other letters
        
        # FIXME: Reverse arabic chars only
        
        char_code = get_char_variants_base(current_char);
        
        if char_code == -1: # = Not an arabic character
            
            linked_text.insert(0, current_char)
            
            continue
        
        # Its an arabic char
        
        if is_left_connectable(previous_char) and is_right_connectable(current_char):
            
            if is_left_connectable(current_char) and is_right_connectable(next_char):
                
                char_code += 3
                
            else:
                
                char_code += 1
        else:
            
            if is_left_connectable(current_char) and is_right_connectable(next_char):
                
                char_code += 2
        
        linked_text.insert(0, chr(char_code)) # put chars in reverse order
        
    text =''.join(linked_text)
    
    return text


# swap lines

# When we reverse the order of our characters (to show arabic text correctly), we will get our lines of text swaped
# so we have to swap our text lines back to make it shown correctly

def swap_lines(linked_text):
    
    new_text = []
    
    current_line_start = 0
    
    char_counter = 0
    
    for c in reversed(linked_text):
        
        if(c == '\n'):
            
            new_text.append('\n')
            
            current_line_start = char_counter + 1
            
            char_counter += 1
            
            continue
        
        new_text.insert(current_line_start, c)
        
        char_counter += 1
    
    return ''.join(new_text)


# Unlink Arabic text (get the original text before it gets connected)

def unlink_text(linked_text):
    
    #
    
    unlinked_text = []
    
    #
    
    for c in linked_text:
        
        if ord(c) in {0xFE8D, 0xFE8E}:
            
            unlinked_text.insert(0, 'ا')
            
        elif ord(c) in {0xFE83, 0xFE84}:
            
            unlinked_text.insert(0, 'أ')

        elif ord(c) in {0xFE87, 0xFE88}:
            
            unlinked_text.insert(0, 'إ')

        elif ord(c) in {0xFE81, 0xFE82}:
            
            unlinked_text.insert(0, 'آ')

        elif ord(c) in {0xFE80}:
            
            unlinked_text.insert(0, 'ء')
            
        elif ord(c) in {0xFE8F, 0xFE90, 0xFE91, 0xFE92}:
            
            unlinked_text.insert(0, 'ب')

        elif ord(c) in {0xFE95, 0xFE96, 0xFE97, 0xFE98}:
            
            unlinked_text.insert(0, 'ت')

        elif ord(c) in {0xFE99, 0xFE9A, 0xFE9B, 0xFE9C}:
            
            unlinked_text.insert(0, 'ث')

        elif ord(c) in {0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0}:
            
            unlinked_text.insert(0, 'ج')

        elif ord(c) in {0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4}:
            
            unlinked_text.insert(0, 'ح')

        elif ord(c) in {0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8}:
            
            unlinked_text.insert(0, 'خ')

        elif ord(c) in {0xFEA9, 0xFEAA}:
            
            unlinked_text.insert(0, 'د')

        elif ord(c) in {0xFEAB, 0xFEAC}:
            
            unlinked_text.insert(0, 'ذ')

        elif ord(c) in {0xFEAD, 0xFEAE}:
            unlinked_text.insert(0, 'ر')

        elif ord(c) in {0xFEAF, 0xFEB0}:
            
            unlinked_text.insert(0, 'ز')

        elif ord(c) in {0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4}:
            
            unlinked_text.insert(0, 'س')

        elif ord(c) in {0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8}:
            
            unlinked_text.insert(0, 'ش')

        elif ord(c) in {0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC}:
            
            unlinked_text.insert(0, 'ص')
            
        elif ord(c) in {0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0}:
            
            unlinked_text.insert(0, 'ض')

        elif ord(c) in {0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4}:
            
            unlinked_text.insert(0, 'ط')

        elif ord(c) in {0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8}:
            
            unlinked_text.insert(0, 'ظ')

        elif ord(c) in {0xFEC9, 0xFECA, 0xFECB, 0xFECC}:
            
            unlinked_text.insert(0, 'ع')
            
        elif ord(c) in {0xFECD, 0xFECE, 0xFECF, 0xFED0}:
            
            unlinked_text.insert(0, 'غ')
            
        elif ord(c) in {0xFED1, 0xFED2, 0xFED3, 0xFED4}:
            
            unlinked_text.insert(0, 'ف')
            
        elif ord(c) in {0xFED5, 0xFED6, 0xFED7, 0xFED8}:
            
            unlinked_text.insert(0, 'ق')

        elif ord(c) in {0xFED9, 0xFEDA, 0xFEDB, 0xFEDC}:
            
            unlinked_text.insert(0, 'ك')
            
        elif ord(c) in {0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0}:
            
            unlinked_text.insert(0, 'ل')
            
        elif ord(c) in {0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4}:
            
            unlinked_text.insert(0, 'م')
            
        elif ord(c) in {0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8}:
            
            unlinked_text.insert(0, 'ن')

        elif ord(c) in {0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC}:
            
            unlinked_text.insert(0, 'ه')

        elif ord(c) in {0xFE93, 0xFE94}:
            
            unlinked_text.insert(0, 'ة')

        elif ord(c) in {0xFEED, 0xFEEE}:
            
            unlinked_text.insert(0, 'و')

        elif ord(c) in {0xFE85, 0xFE86}:
            
            unlinked_text.insert(0, 'ؤ')

        elif ord(c) in {0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4}:
            
            unlinked_text.insert(0, 'ي')
        
        elif ord(c) in {0xFEEF, 0xFEF0}:
            
            unlinked_text.insert(0, 'ى')

        elif ord(c) in {0xFE89, 0xFE8A, 0xFE8B, 0xFE8C}:
            
            unlinked_text.insert(0, 'ئ')

        elif ord(c) in {0xFEFB, 0xFEFC}:
            
            unlinked_text.insert(0, 'ا')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF7, 0xFEF8}:
            
            unlinked_text.insert(0, 'أ')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF9, 0xFEFA}:
            
            unlinked_text.insert(0, 'إ')
            unlinked_text.insert(0, 'ل')

        elif ord(c) in {0xFEF5, 0xFEF6}:
            
            unlinked_text.insert(0, 'آ')
            unlinked_text.insert(0, 'ل')
        
        # Other characters
        
        else:
            
             unlinked_text.insert(0, c)
        
    return unlinked_text


# Prepare our text (3D text, text_buffer)

def init():
    
    if bpy.context.object == None or bpy.context.object.type != 'FONT' or bpy.context.object.mode != 'EDIT':
        
        return
    
    global text_buffer
    
    text_buffer = swap_lines(bpy.context.object.data.body)
    text_buffer = unlink_text(text_buffer)
    
    bpy.context.object.data.align_x = 'RIGHT'
    
    current_char_index = 0
    
    update_visual_cursor_position()


# 

def update_text():
    
    global text_buffer
    global current_char_index
    
    linked_text = link_text(text_buffer)
    linked_text = swap_lines(linked_text)
    
    bpy.ops.font.select_all()
    bpy.ops.font.delete()
    bpy.ops.font.text_insert(text = linked_text)
    
    update_visual_cursor_position()
    

# Add a new character

def insert_text(char):
    
    global text_buffer
    global current_char_index
    
    text_buffer.insert(current_char_index, char)
    
    current_char_index += 1
    
    update_text()
    

# Move the cursor (well, our pointer) to the previous char/position

def move_previous():
    
    global current_char_index
    
    if current_char_index > 0:

        current_char_index -= 1
    
        #update_text()
    
    update_visual_cursor_position()


# Move the cursor/pointer to the next char/position

def move_next():
    
    global text_buffer    
    global current_char_index
    
    if current_char_index < len(text_buffer):
        
        current_char_index += 1
        
        #update_text()
        
    update_visual_cursor_position()


# Move the cursor/pointer to the start of the current line

def move_line_start():
    
    global text_buffer    
    global current_char_index
    
    while current_char_index > 0:
        
        current_char_index -= 1
        
        if text_buffer[current_char_index] == '\n':
            
            current_char_index += 1

            break
        
    update_visual_cursor_position()


# Move the cursor/pointer to the end of the current line

def move_line_end():
    
    global text_buffer    
    global current_char_index
    
    while current_char_index < len(text_buffer):
        
        if text_buffer[current_char_index] == '\n':
            
            break
        
        current_char_index += 1
        
    update_visual_cursor_position()


# Move the cursor/pointer to the previous line

def move_up():
    
    global text_buffer    
    global current_char_index
    
    
    line_start = get_line_start()
    line_offset = current_char_index - line_start
    
    previous_line_end = line_start - 2
    
    previous_line_start = get_line_start(previous_line_end)
    
    previous_line_size = previous_line_end - previous_line_start
    
    new_index = previous_line_start + min(line_offset, previous_line_size + 1)
    
    if is_valid_char_index(new_index):
        
        current_char_index = new_index
        update_visual_cursor_position()


# Move the cursor/pointer to the next line

def move_down():
    
    global text_buffer    
    global current_char_index
    
    
    new_line_size = 0
    
    line_start = get_line_start()
    line_offset = current_char_index - line_start
    
    new_index = get_next_line_start()
    
    if new_index == -1:
    
        return
    
    
    for i in range(line_offset):
        
        if not is_valid_char_index(new_index):
        
            break
        
        if text_buffer[new_index] == '\n':
        
            break
        
        new_index +=1
        
    if is_valid_char_index(new_index) or new_index == len(text_buffer):
        
        current_char_index = new_index
        update_visual_cursor_position()


# Delete the previous character

def delete_previous():
    
    global current_char_index
    
    if current_char_index > 0:
        
        text_buffer.pop(current_char_index - 1)
        
        current_char_index -= 1
        
        update_text ()


# Delete the next character

def delete_next():
    
    global text_buffer
    global current_char_index
    
    if is_valid_char_index(current_char_index):
        
        del(text_buffer[current_char_index])
        
        update_text ()


# 

def get_line_start(index = -1):
    
    global text_buffer    
    global current_char_index
    
    line_start = current_char_index if index == - 1 else index
    
    while line_start > 0:
        
        line_start -= 1
        
        if text_buffer[line_start] == '\n':

            line_start += 1
            
            break
        
    return line_start


#

def get_next_line_start():
    
    global text_buffer    
    global current_char_index
    
    next_line_start = current_char_index
    
    while next_line_start < len(text_buffer):
        
        if text_buffer[next_line_start] == '\n':

            next_line_start += 1
            
            break
        
        next_line_start += 1
        
        if next_line_start == len(text_buffer):
        
            return -1
        
    return next_line_start
      
#

def is_valid_char_index(index):
    
    if len(text_buffer) > 0 and index >= 0 and index < len(text_buffer):
    
        return True
    
    return False


# Make the visual cursor follow our pointer

def update_visual_cursor_position():
    
    global text_buffer    
    global current_char_index

    # Move visual cursor to the begining of the text
    
    for i in range(len(text_buffer)):
    
        bpy.ops.font.move(type='PREVIOUS_CHARACTER')
    
    #
    
    current_line_start = get_line_start()
    
    for i in range(current_line_start):

        if text_buffer[i] == '\n':
        
            bpy.ops.font.move(type='NEXT_LINE')
    
    # NOTE: we can do this in another way, without moving the cursor to the and of the line and then bring it back
    # we can just count the length of the current line and move the cursor forward:
    # (line_length - current_line_offset(= current_char_index - line_start)) times
    
    bpy.ops.font.move(type='LINE_END')
    
    for i in range(current_line_start, current_char_index):
        
        # Do not count "Lem-Alef" as two letters
        
        if text_buffer[i] in {'ا', 'أ', 'إ', 'آ'}:
            
            if i > 0 and text_buffer[i - 1] == 'ل':
                
                continue
            
        bpy.ops.font.move(type='PREVIOUS_CHARACTER')


# Keyboard Handler

class __OT_ArabicTextMode(bpy.types.Operator):

    bl_idname = "view3d.arabic_text_mode"
    bl_label = "Write Arabic Text"
    
    #
    
    def modal(self, context, event):
        
        global text_buffer
        
        global current_char_index
        
        
        # Use this handler only when a 3DText object is selected and being edited
        
        if bpy.context.object == None or bpy.context.object.type != 'FONT' or bpy.context.object.mode != 'EDIT':
        
            return {'PASS_THROUGH'}
        
        #
        
        if event.type == 'BACK_SPACE':

            if event.value=='PRESS':
            
                delete_previous()
            
            return {'RUNNING_MODAL'}
        
        
        elif event.type == 'DEL':
            
            if event.value=='PRESS':
            
                delete_next()
            
            return {'RUNNING_MODAL'}
        
        
        elif event.type == 'HOME':
            
            if event.value=='PRESS':
            
                move_line_start()
            
            return {'RUNNING_MODAL'}
        
        elif event.type == 'END':
            
            if event.value=='PRESS':
            
                move_line_end()
            
            return {'RUNNING_MODAL'}
        
        elif event.type == 'RIGHT_ARROW':
            
            if event.value=='PRESS':
            
                move_previous()
            
            return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFT_ARROW':
            
            if event.value=='PRESS':
            
                move_next()
            
            return {'RUNNING_MODAL'}
        
        elif event.type == 'UP_ARROW':

            if event.value=='PRESS':
            
                move_up()
            
            return {'RUNNING_MODAL'}

        elif event.type == 'DOWN_ARROW':

            if event.value=='PRESS':
            
                move_down()
            
            return {'RUNNING_MODAL'}

        elif event.type == 'RET':
            
            if event.value=='PRESS':
            
                insert_text('\n')
            
            return {'RUNNING_MODAL'}
                   
        elif event.type == 'TAB':
            
            if event.value=='RELEASE':
                
                if bpy.context.object.mode == 'EDIT':
                
                    init()
            
            return {'PASS_THROUGH'}
            
        elif event.unicode:
            
            if event.value=='PRESS':
                
                insert_text(event.unicode)
            
            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
     
    #
        
    def invoke(self, context, event):
        
        if context.area.type == 'VIEW_3D':
            
            self.key = ""
            
            context.window_manager.modal_handler_add(self)
            
            if bpy.context.object != None and bpy.context.object.type == 'FONT' and bpy.context.object.mode == 'EDIT':
                
                # update text data (i don't know a better way to do this)
                
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle() 
                
                init()
            
            return {'RUNNING_MODAL'}
        
        else:
            
            return {'CANCELLED'}


# ----------------------------------------------------------------------------------------------------------------

keymaps = []

def register():
    
    bpy.utils.register_class(__OT_ArabicTextMode)
	
    wm = bpy.context.window_manager
    
    kc = wm.keyconfigs.addon
    
    if kc:
        
        km = wm.keyconfigs.addon.keymaps.new(name="Window")
        kmi = km.keymap_items.new(__OT_ArabicTextMode.bl_idname, 'F1', 'PRESS', ctrl=True)
        keymaps.append((km, kmi))
    
#
    
def unregister():
    
    for km, kmi in keymaps:
    
        km.keymap_items.remove(kmi)
        
    keymaps.clear()
    
    bpy.utils.unregister_class(__OT_ArabicTextMode)
    
# ----------------------------------------------------------------------------------------------------------------

if(__name__ == "__main__"):
    
    register()

