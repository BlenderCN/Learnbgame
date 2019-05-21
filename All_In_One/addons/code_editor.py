# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Code Editor",
    "location": "Text Editor > Righ Click Menu",
    "version": (0,1,0),
    "blender": (2,7,2),
    "description": "Better editor for coding",
    "author": "",
    "category": "Text Editor",
}

import bpy
import bgl
import blf
import time
import string
import threading

# =====================================================
#                      CODE EDITTING
# =====================================================

def custom_home(line, cursor_loc):
    """Returns position of first character in line"""
    for id, ch in enumerate(line):
        if ch != ' ' or id >= cursor_loc-1 :
            return id
    return 0

def smart_complete(input_string):
    """
    Based on input:
     - Evaluates numeric expression
     - Puts quotes("") around
     - Makes a list from selection
    """
    def handle_letters(input_text):
        if all([ch in string.ascii_letters + string.digits + '_' for ch in input_text]):
            return '"' + input_string + '"'
        if any([ch in '!#$%&\()*+,-/:;<=>?@[\\]^`{|}~' for ch in input_text]):
            return input_text
        else:
            input_text.split(" ")
            return '[' + ', '.join([ch for ch in input_text.split(" ") if ch!='']) + ']'
    
    # try numbers
    if not input_string:
        return ""
    elif not any([ch in string.digits for ch in input_string]):
        return handle_letters(input_string)
    else:
        try:
            e = 2.71828     # euler number
            phi = 1.61803   # golden ratio
            pi = 3.141592   # really?
            g = 9.80665     # gravitation accel
            answer = eval(input_string)
            return str(round(answer, 5))
        except:
            return handle_letters(input_string)

# =====================================================
#                     MINIMAP SYNTAX
# =====================================================

class ThreadedSyntaxHighlighter(threading.Thread):
    """Breaks text into segments based on syntax for highlighting"""
    def __init__(self, text, output_list):
        threading.Thread.__init__(self)
        self.daemon = True
        self.output = output_list
        self.text = text
        self._restart = threading.Event()
        self._paused = threading.Event()
        self._state = threading.Condition()
    
    def restart(self, text):
        with self._state:
            self.text = text
            self._restart.set()
            self._paused.clear()
            self._state.notify()  # unblock self if in paused mode
    
    def run(self):
        while True:
            with self._state:
                if self._paused.is_set():
                    self._state.wait() # wait until notify() - the thread is paused
            
            self._restart.clear()
            # do stuff
            self.highlight()
    
    def highlight(self):
        # approximate syntax higlighter, accuracy is traded for speed
        
        # start empty
        n_lines = len(self.text.lines) if self.text else 0
        data = {}
        data['plain'] = [[] for i in range(n_lines)]
        data['strings'] = [[] for i in range(n_lines)]
        data['comments'] = [[] for i in range(n_lines)]
        data['numbers'] = [[] for i in range(n_lines)]
        data["special"] = [[] for i in range(n_lines)]
        special_temp = []
        data["builtin"] = [[] for i in range(n_lines)]
        data["prepro"] = [[] for i in range(n_lines)]
        data['tabs'] = [[] for i in range(n_lines)]
        
        # syntax element structure
        element = [0,   # line id
                   0,   # element start position
                   0,   # element end position
                   0]   # special block end line
        
        # this is used a lot for ending plain text segment
        def close_plain(element, w):
            """Ends non-highlighted text segment"""
            if element[1] < w:
                element[2] = w - 1
                data['plain'][element[0]].append([element[1], element[2]])
            element[1] = w
            return
        
        # this ends collapsible code block
        def close_block(h, indent):
            for entry in list(special_temp):
                if entry[0] < h and entry[1] >= indent:
                    data['special'][entry[0]].append([entry[1], entry[2], h-empty_lines])
                    special_temp.remove(entry)
            return
        
        # recognized tags definitions, only the most used
        builtin = ['return','break','continue','yield','with','while','for ', 'import ', 'from ',
                   'if ','elif ',' else','None','True','False','and ','not ','in ','is ']
        special = ['def ','class ']
        
        # flags of syntax state machine
        state = None
        empty_lines = 0
        timer = -1      # timer to skip characters and close segment at t=0
        
        # process the text if there is one
        for h, line in enumerate(self.text.lines if self.text else []):
            
            # new line new element, carry string flag
            element[0] = h
            element[1] = 0
            if state not in ['Q_STRING', 'A_STRING']: state = None
            indent = 0
            block_close = any([char not in string.whitespace for char in line.body])
            
            # process each line and break into syntax elements
            for w, ch in enumerate(line.body):
                
                # end if restarted
                if self._restart.is_set():
                    return
                
                if timer > 0:
                    timer -= 1
                    
                elif timer < 0:
                    # tabs
                    if not state and line.body.startswith('    ', w):
                        close_plain(element, w)
                        state = 'TAB'
                        timer = 3
                        indent += 4
                    elif state in ['Q_STRING', 'A_STRING'] and line.body.startswith('    ', w):
                        element[1] = w + 4
                        indent += 4
                    
                    # bilt-in
                    if not state and ch in "rbcywfieNTFan":
                        results = [line.body.startswith(x, w) for x in builtin]
                        if any(results):
                            close_plain(element, w)
                            state = 'BUILTIN'
                            timer = len(builtin[results.index(True)]) - 1
                    
                    # special
                    if not state and ch in "dc":
                        results = [line.body.startswith(x, w) for x in special]
                        if any(results):
                            close_plain(element, w)
                            state = 'SPECIAL'
                            timer = len(special[results.index(True)]) - 1
                    
                    # numbers
                    if not state and ch in ['0','1','2','3','4','5','6','7','8','9']:
                        close_plain(element, w)
                        state = 'NUMBER'
                    elif state == 'NUMBER' and ch not in ['0','1','2','3','4','5','6','7','8','9','.']:
                        element[2] = w
                        data['numbers'][element[0]].append([element[1], element[2]])
                        element[1] = w
                        state = None
                    
                    # "" string
                    if not state and ch == '"':
                        close_plain(element, w)
                        state = 'Q_STRING'
                    elif state == 'Q_STRING' and ch == '"':
                        if w > 1 and line.body[w-1]=='\\' and line.body[w-2]=='\\':
                            timer = 0
                        elif w > 0 and line.body[w-1]=='\\':
                            pass
                        else:
                            timer = 0
                    
                    # '' string
                    elif not state and ch == "'":
                        close_plain(element, w)
                        state = 'A_STRING'
                    elif state == 'A_STRING' and ch == "'":
                        if w > 1 and line.body[w-1]=='\\' and line.body[w-2]=='\\':
                            timer = 0
                        elif w > 0 and line.body[w-1]=='\\':
                            pass
                        else:
                            timer = 0
                    
                    # comment
                    elif not state and ch == '#':
                        close_plain(element, w)
                        state = 'COMMENT'
                        # close code blocks
                        if block_close:
                            for i, j in enumerate(line.body):
                                if i > 0 and j != " ":
                                    close_block(h, 4*int(i/4))
                        break
                    
                    # preprocessor
                    elif not state and ch == '@':
                        close_plain(element, w)
                        state = 'PREPRO'
                        # close code blocks
                        if block_close:
                            close_block(h, indent)
                        break
                    
                # close special blocks
                if state != 'TAB' and block_close:
                    block_close = False
                    close_block(h, indent)
                
                # write element when timer 0
                if timer == 0:
                    element[2] = w
                    if state == 'TAB':
                        data['tabs'][element[0]].append([element[1], element[2]])
                        element[1] = w + 1
                    elif state in ['Q_STRING', 'A_STRING']:
                        data['strings'][element[0]].append([element[1], element[2]])
                        element[1] = w + 1
                    elif state == 'BUILTIN':
                        data['builtin'][element[0]].append([element[1], element[2]])
                        element[1] = w + 1
                    elif state == 'SPECIAL':
                        special_temp.append(element.copy())
                        element[1] = w + 1
                    state = None
                    timer = -1
            
            # count empty lines
            empty_lines = 0 if any([ch not in string.whitespace for ch in line.body]) else empty_lines + 1
            
            # handle line ends
            if not state:
                element[2] = len(line.body)
                data['plain'][element[0]].append([element[1], element[2]])
            elif state == 'COMMENT':
                element[2] = len(line.body)
                data['comments'][element[0]].append([element[1], element[2]])
            elif state == 'PREPRO':
                element[2] = len(line.body)
                data['prepro'][element[0]].append([element[1], element[2]])
            elif state in ['Q_STRING', 'A_STRING']:
                element[2] = len(line.body)
                data['strings'][element[0]].append([element[1], element[2]])
            elif state == 'NUMBER':
                element[2] = len(line.body)
                data['numbers'][element[0]].append([element[1], element[2]])
        
        # close all remaining blocks
        for entry in special_temp:
            data['special'][entry[0]].append([entry[1], entry[2], h+1-empty_lines])
        
        # done
        self.output[0]['elements'] = data['plain']
        self.output[1]['elements'] = data['strings']
        self.output[2]['elements'] = data['comments']
        self.output[3]['elements'] = data['numbers']
        self.output[4]['elements'] = data["builtin"]
        self.output[5]['elements'] = data['prepro']
        self.output[6]['elements'] = data["special"]
        self.output[7]['elements'] = data['tabs']
        
        # enter sleep
        with self._state:
            self._paused.set()  # enter sleep mode
        return

# =====================================================
#                    OPENGL DRAWCALS
# =====================================================

def draw_callback_px(self, context):
    """Draws Code Editors Minimap and indentation marks"""
    
    def draw_line(origin, length, thickness, vertical = False):
        """Drawing lines with polys, its faster"""
        x = (origin[0] + thickness) if vertical else (origin[0] + length)
        y = (origin[1] + length) if vertical else (origin[1] + thickness)
        bgl.glBegin(bgl.GL_QUADS)
        for v1, v2 in [origin, (x, origin[1]), (x, y), (origin[0], y)]:
            bgl.glVertex2i(v1, v2)
        bgl.glEnd()
        return
    
    # abort if another text editor
    if self.area == context.area and self.window == context.window:
        bgl.glEnable(bgl.GL_BLEND)
    else:
        return
    
    start = time.clock()
    
    # init params
    font_id = 0
    self.width = next(region.width for region in context.area.regions if region.type=='WINDOW')
    self.height = next(region.height for region in context.area.regions if region.type=='WINDOW')
    dpi_r = context.user_preferences.system.dpi / 72.0
    self.left_edge = self.width - round(dpi_r*(self.width+5*self.minimap_width)/10.0)
    self.right_edge = self.width - round(dpi_r*15)
    self.opacity = min(max(0,(self.width-self.min_width) / 100.0),1)
    
    # compute character dimensions
    mcw = dpi_r * self.minimap_symbol_width         # minimap char width
    mlh = round(dpi_r * self.minimap_line_height)   # minimap line height
    fs = context.space_data.font_size
    cw = round(dpi_r * round(2 + 0.6 * (fs - 4)))                    # char width
    ch = round(dpi_r * round(2 + 1.3 * (fs - 2) + ((fs % 10) == 0))) # char height
    
    # panel background box
    self.tab_width = round(dpi_r * 25) if (self.tabs and len(bpy.data.texts) > 1) else 0
    bgl.glColor4f(self.background.r, self.background.g, self.background.b, (1-self.bg_opacity)*self.opacity)
    bgl.glBegin(bgl.GL_QUADS)
    for x, y in [(self.left_edge-self.tab_width, self.height),
                 (self.right_edge, self.height),
                 (self.right_edge, 0),
                 (self.left_edge-self.tab_width, 0)]:
        bgl.glVertex2i(x, y)
    bgl.glEnd()
    
    # line numbers background
    space = context.space_data
    if space.text:
        lines = len(space.text.lines)
        lines_digits = len(str(lines)) if space.show_line_numbers else 0
        self.line_bar_width = int(dpi_r*5)+cw*(lines_digits)
        bgl.glColor4f(self.background.r, self.background.g, self.background.b, 1)
        bgl.glBegin(bgl.GL_QUADS)
        for x, y in [(0, self.height), (self.line_bar_width, self.height), (self.line_bar_width, 0), (0, 0)]:
            bgl.glVertex2i(x, y)
        bgl.glEnd()
        # shadow
        bgl.glLineWidth(1.0 * dpi_r)
        for id, intensity in enumerate([0.2,0.1,0.07,0.05,0.03,0.02,0.01]):
            bgl.glColor4f(0.0, 0.0, 0.0, intensity)
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for x, y in [(self.line_bar_width+id, 0),
                         (self.line_bar_width+id, self.height)]:
                bgl.glVertex2i(x, y)
            bgl.glEnd()
    
    # minimap shadow
    for id, intensity in enumerate([0.2,0.1,0.07,0.05,0.03,0.02,0.01]):
        bgl.glColor4f(0.0, 0.0, 0.0, intensity*self.opacity)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x, y in [(self.left_edge-id-self.tab_width, 0),
                     (self.left_edge-id-self.tab_width, self.height)]:
            bgl.glVertex2i(x, y)
        bgl.glEnd()
        
    # divider
    if self.tab_width:
        bgl.glColor4f(0.0, 0.0, 0.0, 0.2*self.opacity)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x, y in [(self.left_edge, 0),
                     (self.left_edge, self.height)]:
            bgl.glVertex2i(x, y)
        bgl.glEnd()
    
    # if there is text in window
    if space.text and self.opacity:
        
        # minimap horizontal sliding based on text block length
        max_slide = max(0, mlh*(lines+self.height/ch) - self.height)
        self.slide = int(max_slide * space.top / lines)
        minimap_top_line = int(self.slide/mlh)
        minimap_bot_line = int((self.height+self.slide)/mlh)
        
        # draw minimap visible box
        if self.in_minimap:
            bgl.glColor4f(1.0, 1.0, 1.0, 0.1*self.opacity)
        else:
            bgl.glColor4f(1.0, 1.0, 1.0, 0.07*self.opacity)
        bgl.glBegin(bgl.GL_QUADS)
        for x, y in [(self.left_edge, self.height-mlh*space.top + self.slide),
                     (self.right_edge, self.height-mlh*space.top + self.slide),
                     (self.right_edge, self.height-mlh*(space.top+space.visible_lines) + self.slide),
                     (self.left_edge, self.height-mlh*(space.top+space.visible_lines) + self.slide)]:
            bgl.glVertex2i(x, y)
        bgl.glEnd()
        
        # draw minimap code
        for segment in self.segments[:-1]:
            bgl.glColor4f(segment['col'][0], segment['col'][1], segment['col'][2], 0.4*self.opacity)
            for id, element in enumerate(segment['elements'][minimap_top_line:minimap_bot_line]):
                loc_y = mlh*(id+minimap_top_line+3) - self.slide
                for sub_element in element:
                    draw_line((self.left_edge+int(mcw*(sub_element[0]+4)), self.height-loc_y),
                               int(mcw*(sub_element[1]-sub_element[0])),
                               int(0.5 * mlh))
        
        # minimap code marks
        bgl.glColor4f(self.segments[-2]['col'][0],
                      self.segments[-2]['col'][1],
                      self.segments[-2]['col'][2],
                      0.3*self.block_trans*self.opacity)
        for id, element in enumerate(self.segments[-2]['elements']):
            for sub_element in element:
                if sub_element[2] >= space.top or id < space.top+space.visible_lines:
                    draw_line((self.left_edge+int(mcw*(sub_element[0]+4)), self.height-mlh*(id+3)+self.slide),
                               -int(mlh*(sub_element[2]-id-1)),
                               int(0.5 * mlh),
                               True)
    
    # draw dotted indentation marks
    bgl.glLineWidth(1.0 * dpi_r)
    if space.text:
        bgl.glColor4f(self.segments[0]['col'][0],
                      self.segments[0]['col'][1],
                      self.segments[0]['col'][2],
                      self.indent_trans)
        for id, element in enumerate(self.segments[-1]['elements'][space.top:space.top+space.visible_lines]):
            loc_y = id
            for sub_element in element:
                draw_line((int(dpi_r*10)+cw*(lines_digits+sub_element[0]+4), self.height-ch*(loc_y)),
                           -ch,
                           int(1 * dpi_r),
                           True)
        
        # draw code block marks
        bgl.glColor4f(self.segments[-2]['col'][0],
                      self.segments[-2]['col'][1],
                      self.segments[-2]['col'][2],
                      self.block_trans)
        for id, element in enumerate(self.segments[-2]['elements']):
            for sub_element in element:
                if sub_element[2] >= space.top or id < space.top+space.visible_lines:
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    bgl.glVertex2i(int(dpi_r*10+cw*(lines_digits+sub_element[0])),
                                   self.height-ch*(id+1-space.top))
                    bgl.glVertex2i(int(dpi_r*10+cw*(lines_digits+sub_element[0])),
                                   self.height-int(ch*(sub_element[2]-space.top)))
                    bgl.glVertex2i(int(dpi_r*10+cw*(lines_digits+sub_element[0]+1)),
                                   self.height-int(ch*(sub_element[2]-space.top)))
                    bgl.glEnd()
    
    # tab dividers
    if self.tab_width and self.opacity:
        self.tab_height = min(200, int(self.height/len(bpy.data.texts)))
        y_loc = self.height-5
        for text in bpy.data.texts:
            # tab selection
            if text.name == self.in_tab:
                bgl.glColor4f(1.0, 1.0, 1.0, 0.05*self.opacity)
                bgl.glBegin(bgl.GL_QUADS)
                for x, y in [(self.left_edge-self.tab_width, y_loc),
                             (self.left_edge, y_loc),
                             (self.left_edge, y_loc-self.tab_height),
                             (self.left_edge-self.tab_width, y_loc-self.tab_height)]:
                    bgl.glVertex2i(x, y)
                bgl.glEnd()
            # tab active
            if context.space_data.text and text.name == context.space_data.text.name:
                bgl.glColor4f(1.0, 1.0, 1.0, 0.05*self.opacity)
                bgl.glBegin(bgl.GL_QUADS)
                for x, y in [(self.left_edge-self.tab_width, y_loc),
                             (self.left_edge, y_loc),
                             (self.left_edge, y_loc-self.tab_height),
                             (self.left_edge-self.tab_width, y_loc-self.tab_height)]:
                    bgl.glVertex2i(x, y)
                bgl.glEnd()
            bgl.glColor4f(0.0, 0.0, 0.0, 0.2*self.opacity)
            y_loc -= self.tab_height
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for x, y in [(self.left_edge-self.tab_width, y_loc),
                         (self.left_edge, y_loc)]:
                bgl.glVertex2i(x, y)
            bgl.glEnd()
    
    # draw fps
#    bgl.glColor4f(1, 1, 1, 0.2)
#    blf.size(font_id, fs, int(dpi_r*72))
#    blf.position(font_id, self.left_edge-50, 5, 0)
#    blf.draw(font_id, str(round(1/(time.clock() - start),3)))
    
    # draw line numbers
    if space.text:
        bgl.glColor4f(self.segments[0]['col'][0],
                      self.segments[0]['col'][1],
                      self.segments[0]['col'][2],
                      0.5)
        for id in range(space.top, min(space.top+space.visible_lines+1, lines+1)):
            if self.in_line_bar and self.segments[-2]['elements'][id-1]:
                bgl.glColor4f(self.segments[-2]['col'][0],
                              self.segments[-2]['col'][1],
                              self.segments[-2]['col'][2],
                              1)
                blf.position(font_id, 2+int(0.5*cw*(len(str(lines))-1)), self.height-ch*(id-space.top)+3, 0)
                #blf.draw(font_id, '→')
                blf.draw(font_id, '↓')
                bgl.glColor4f(self.segments[0]['col'][0],
                      self.segments[0]['col'][1],
                      self.segments[0]['col'][2],
                      0.5)
            else:
                blf.position(font_id, 2+int(0.5*cw*(len(str(lines))-len(str(id)))), self.height-ch*(id-space.top)+3, 0)
                blf.draw(font_id, str(id))
    
    # draw file names
    if self.tab_width:
        blf.enable(font_id, blf.ROTATION)
        blf.rotation(font_id, 1.570796)
        y_loc = self.height
        for text in bpy.data.texts:
            text_max_length = max(2,int((self.tab_height - 40)/cw))
            name = text.name[:text_max_length]
            if text_max_length < len(text.name):
                name += '...'
            bgl.glColor4f(self.segments[0]['col'][0],
                          self.segments[0]['col'][1],
                          self.segments[0]['col'][2],
                          (0.7 if text.name == self.in_tab else 0.4)*self.opacity)
            blf.position(font_id,
                         self.left_edge-round((self.tab_width-ch)/2.0)-5,
                         round(y_loc-(self.tab_height/2)-cw*len(name)/2),
                         0)
            blf.draw(font_id, name)
            y_loc -= self.tab_height
    
    # restore opengl defaults
    bgl.glColor4f(0, 0, 0, 1)
    bgl.glLineWidth(1.0)
    bgl.glDisable(bgl.GL_BLEND)
    blf.disable(font_id, blf.ROTATION)
    return

# =====================================================
#                       OPERATORS
# =====================================================

class CodeEditor(bpy.types.Operator):
    """Modal operator running Code Editor"""
    bl_idname = "code_editor.start"
    bl_label = "Code Editor"
    
    # minimap scrolling
    def scroll(self, context, event):
        if context.space_data.text:
            # dpi_ratio for ui scale
            dpi_r = context.user_preferences.system.dpi / 72.0
            mlh = round(dpi_r * self.minimap_line_height)   # minimap line height
            # box center in px
            box_center = self.height - mlh * (context.space_data.top + context.space_data.visible_lines/2)
            self.to_box_center = box_center + self.slide - event.mouse_region_y
            # scroll will scroll 3 lines thus * 0.333
            nlines = 0.333 * self.to_box_center / mlh
            bpy.ops.text.scroll(lines=round(nlines))
        return
    
    def modal(self, context, event):
        # function only if in area invoked in
        if (context.space_data and
            context.space_data.type == 'TEXT_EDITOR' and
            self.area == context.area and
            self.window == context.window):
                
            # does not work with word wrap
            context.space_data.show_line_numbers = True
            context.space_data.show_word_wrap = False
            context.space_data.show_syntax_highlight = True
            context.area.tag_redraw()
            
            # minimap scrolling and tab clicking
            if event.type == 'MOUSEMOVE':
                if ((0 < event.mouse_region_x < self.width) and
                    (0 < event.mouse_region_y < self.height)):
                    self.in_area = True
                else:
                    self.in_area = False
                
                if ((0 < event.mouse_region_x < self.line_bar_width) and
                    (0 < event.mouse_region_y < self.height)):
                    self.in_line_bar = True
                else:
                    self.in_line_bar = False
                
                if self.drag:
                    self.scroll(context, event)
                if ((self.left_edge < event.mouse_region_x < self.right_edge) and
                    (0 < event.mouse_region_y < self.height)):
                    self.in_minimap = True
                else:
                    self.in_minimap = False
                    
                if ((self.left_edge - self.tab_width < event.mouse_region_x < self.left_edge) and
                     (0 < event.mouse_region_y < self.height)):
                    tab_id = int((self.height-event.mouse_region_y) / self.tab_height)
                    if tab_id < len(bpy.data.texts):
                        self.in_tab = bpy.data.texts[tab_id].name
                    else:
                        self.in_tab = None
                else:
                    self.in_tab = None
                    
            if self.in_minimap and self.opacity and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self.drag = True
                self.scroll(context, event)
                return {'RUNNING_MODAL'}
            if self.in_line_bar and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                return {'RUNNING_MODAL'}
            if self.in_tab and self.opacity and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                context.space_data.text = bpy.data.texts[self.in_tab]
                return {'RUNNING_MODAL'}
            if self.opacity and event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self.thread.restart(context.space_data.text)
                self.drag = False
            
            # typing characters - update minimap when whitespace
            if self.opacity and (event.unicode == ' ' or event.type in {'RET', 'NUMPAD_ENTER', 'TAB'}):
                self.thread.restart(context.space_data.text)
            
            # custom home handling
            if self.in_area and event.type == 'HOME' and event.value == 'PRESS' and not event.ctrl:
                if event.alt:
                    bpy.ops.text.move(type='LINE_BEGIN')
                    return {'RUNNING_MODAL'}
                line = context.space_data.text.current_line.body
                cursor_loc = context.space_data.text.select_end_character
                new_loc = custom_home(line, cursor_loc)
                for x in range(cursor_loc - new_loc):
                    # this is awful but blender ops suck balls
                    if event.shift:
                        bpy.ops.text.move_select(type='PREVIOUS_CHARACTER')
                    else:
                        bpy.ops.text.move(type='PREVIOUS_CHARACTER')
                return {'RUNNING_MODAL'}
            
            # custom brackets etc. handling
            elif self.in_area and event.unicode in ['(', '"', "'", '[', '{'] and event.value == 'PRESS':
                select_loc = context.space_data.text.select_end_character
                cursor_loc = context.space_data.text.current_character
                line = context.space_data.text.current_line.body
                if cursor_loc == select_loc and cursor_loc < len(line) and line[cursor_loc] not in " \n\t\r)]},.+-*/":
                    return {'PASS_THROUGH'}
                if event.unicode == '(': bpy.ops.text.insert(text='()')
                if event.unicode == '"': bpy.ops.text.insert(text='""')
                if event.unicode == "'": bpy.ops.text.insert(text="''")
                if event.unicode == "[": bpy.ops.text.insert(text="[]")
                if event.unicode == "{": bpy.ops.text.insert(text="{}")
                bpy.ops.text.move(type='PREVIOUS_CHARACTER')
                return {'RUNNING_MODAL'}
            
            # smart complete ALT-C
            elif self.in_area and event.unicode == 'c' and event.value == 'PRESS' and event.alt:
                if context.space_data.text.select_end_character == context.space_data.text.current_character:
                    bpy.ops.text.select_word()
                bpy.ops.text.copy()
                clipboard = bpy.data.window_managers[0].clipboard
                context.window_manager.clipboard = smart_complete(clipboard)
                bpy.ops.text.paste()
                context.window_manager.clipboard = ""
                return {'RUNNING_MODAL'}
            
            # comment ALT-D
            elif self.in_area and event.unicode == 'd' and event.value == 'PRESS' and event.alt:
                if context.space_data.text.select_end_character == context.space_data.text.current_character:
                    bpy.ops.text.select_word()
                bpy.ops.text.comment()
                return {'RUNNING_MODAL'}
            
            # end by button and code editor cleanup
            if str(context.area) not in context.window_manager.code_editors:
                del self.thread
                bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}
        
        # end by F8 for reloading addons
        if event.type == 'F8':
            editors = context.window_manager.code_editors.split('&')
            editors.remove(str(context.area))
            context.window_manager.code_editors = '&'.join(editors)
            del self.thread
            bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        # Version with one 'invoke scene' operator handling multiple text editor areas has the same performance
        # as one operator for eatch area - version 2 is implemented for simplicity
        if context.area.type != 'TEXT_EDITOR':
            self.report({'WARNING'}, "Text Editor not found, cannot run operator")
            return {'CANCELLED'}
        
        # init handlers
        args = (self, context)
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        
        # register operator in winman prop
        if not context.window_manager.code_editors: 
            context.window_manager.code_editors = str(context.area)
        else:
            editors = context.window_manager.code_editors.split('&')
            editors.append(str(context.area))
            context.window_manager.code_editors = '&'.join(editors)
        
        # user controllable in addon preferneces
        addon_prefs = context.user_preferences.addons[__name__].preferences
        self.bg_opacity = addon_prefs.opacity
        self.tabs = addon_prefs.show_tabs
        self.minimap_width = addon_prefs.minimap_width
        self.min_width = addon_prefs.window_min_width
        self.minimap_symbol_width = addon_prefs.symbol_width
        self.minimap_line_height = addon_prefs.line_height
        context.space_data.show_margin = addon_prefs.show_margin
        context.space_data.margin_column = addon_prefs.margin_column
        self.block_trans = 1-addon_prefs.block_trans
        self.indent_trans = 1-addon_prefs.indent_trans
        
        # init operator params
        self.area = context.area
        self.window = context.window
        self.in_area = True
        self.opacity = 1.0
        self.text_name = None
        self.width = next(region.width for region in context.area.regions if region.type=='WINDOW')
        self.height = next(region.height for region in context.area.regions if region.type=='WINDOW')
        dpi_r = context.user_preferences.system.dpi / 72.0
        self.left_edge = self.width - round(dpi_r*(self.width+5*self.minimap_width)/10.0)
        self.right_edge = self.width - round(dpi_r*15)
        self.in_minimap = False
        self.in_tab = None
        self.tab_width = 0
        self.tab_height = 0
        self.drag = False
        self.to_box_center = 0
        self.slide = 0
        self.line_bar_width = 0
        self.in_line_bar = False
        
        # get theme colors
        current_theme = bpy.context.user_preferences.themes.items()[0][0]
        tex_ed = bpy.context.user_preferences.themes[current_theme].text_editor
        self.background = tex_ed.space.back
        
        # get dpi, font size
        self.dpi = bpy.context.user_preferences.system.dpi
        
        #temp folder for autosave - TODO
        #self.temp = bpy.context.user_preferences.filepaths.temporary_directory
        
        # list to hold text info
        self.segments = []
        self.segments.append({'elements': [], 'col': tex_ed.space.text})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_string})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_comment})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_numbers})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_builtin})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_preprocessor})
        self.segments.append({'elements': [], 'col': tex_ed.syntax_special})
        self.segments.append({'elements': [], 'col': (1,0,0)})  # Indentation marks
        
        # list to hold gui areas
        self.clickable = []
        
        # threaded syntax highlighter
        self.thread = ThreadedSyntaxHighlighter(context.space_data.text, self.segments)
        self.thread.start()
        
        return {'RUNNING_MODAL'}

class CodeEditorPrefs(bpy.types.AddonPreferences):
    """Code Editors Preferences Panel"""
    bl_idname = __name__
    
    opacity = bpy.props.FloatProperty(
        name="Panel Background transparency",
        description="0 - fully opaque, 1 - fully transparent",
        min=0.0,
        max=1.0,
        default=0.2)
    
    show_tabs = bpy.props.BoolProperty(
        name="Show Tabs in Panel when multiple text blocks",
        description="Show opened textblock in tabs next to minimap",
        default=True)
    
    minimap_width = bpy.props.IntProperty(
        name="Minimap panel width",
        description="Minimap base width in px",
        min=25,
        max=400,
        default=100)
    
    window_min_width = bpy.props.IntProperty(
        name="Hide Panel when area width less than",
        description="Set 0 to deactivate side panel hiding, set huge to disable panel",
        min=0,
        max=4096,
        default=600)
    
    symbol_width = bpy.props.FloatProperty(
        name="Minimap character width",
        description="Minimap character width in px",
        min=1.0,
        max=10.0,
        default=1.0)
    
    line_height = bpy.props.IntProperty(
        name="Minimap line spacing",
        description="Minimap line spacign in px",
        min=2,
        max=10,
        default=2)
    
    block_trans = bpy.props.FloatProperty(
        name="Code block markings transparency",
        description="0 - fully opaque, 1 - fully transparent",
        min=0.0,
        max=1.0,
        default=0.6)
    
    indent_trans = bpy.props.FloatProperty(
        name="Indentation markings transparency",
        description="0 - fully opaque, 1 - fully transparent",
        min=0.0,
        max=1.0,
        default=0.9)
    
    show_margin = bpy.props.BoolProperty(
        name="Activate global Text Margin marker",
        default = True)
    
    margin_column = bpy.props.IntProperty(
        name="Margin Column",
        description="Column number to show marker at",
        min=0,
        max=1024,
        default=120)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        col.prop(self, "opacity")
        col.prop(self, "show_tabs", toggle=True)
        col.prop(self, "window_min_width")
        col = row.column(align=True)
        col.prop(self, "minimap_width")
        col.prop(self, "symbol_width")
        col.prop(self, "line_height")
        row = layout.row(align=True)
        row.prop(self, "show_margin", toggle=True)
        row.prop(self, "margin_column")
        row = layout.row(align=True)
        row.prop(self, "block_trans")
        row.prop(self, "indent_trans")

class CodeEditorEnd(bpy.types.Operator):
    """Removes reference of Code Editors Area ending its modal operator"""
    bl_idname = "code_editor.end"
    bl_label = ""
    
    def execute(self, context):
        if str(context.area) in context.window_manager.code_editors:
            editors = context.window_manager.code_editors.split('&')
            editors.remove(str(context.area))
            context.window_manager.code_editors = '&'.join(editors)
        return {'FINISHED'}

# =====================================================
#                        REGISTER
# =====================================================

def menu_entry(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    if str(context.area) in context.window_manager.code_editors:
        layout.operator("code_editor.end", text="Exit Code Editor", icon="GO_LEFT")
    else:
        layout.operator("code_editor.start", text="Start Code Editor", icon='FONTPREVIEW')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.code_editors = bpy.props.StringProperty(default="")
    bpy.types.TEXT_MT_toolbox.prepend(menu_entry)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.TEXT_MT_toolbox.remove(menu_entry)

if __name__ == "__main__":
    register()