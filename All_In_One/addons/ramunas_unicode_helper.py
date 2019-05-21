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
    'name': "Unicode Helper",
    'author': "ramunas@blender.lt",
    'version': (0, 1, 4),
    'blender': (2, 5, 9),
    'api': 40768,
    'location': "View3D > Toolbar",
    'warning': "",
    'description': "Operator to add special characters to Text object",
    'wiki_url': "",
    'tracker_url': "http://blender.lt/?page_id=417",
    'category': 'Object'}

import bpy

def translate_hex(self, context):
    try:
        context.window_manager.char_code = int(context.window_manager.char_hex_code, 16)
    except:
        pass
    return None

import datetime
def log(msg, obj):
    timestring = str(datetime.datetime.now())[11:]
    print(timestring+" "+str(msg)+" "+str(obj))
    

bpy.types.WindowManager.char_code = bpy.props.IntProperty(name="Code", description="Numeric (base10) Value Of The New Character", default=261, min=14, max=55295, subtype='UNSIGNED')
bpy.types.WindowManager.char_hex_code = bpy.props.StringProperty(name="", description="Hexadecimal Code Value", default="105", update=translate_hex)
bpy.types.WindowManager.text_replace = bpy.props.BoolProperty(name="Replace Existing Text", description="Replace Existing Content In Text Object", default=False)
bpy.types.WindowManager.char_prepend = bpy.props.BoolProperty(name="Insert On The Left", description="Insert Char On The Left Side Of The String", default=False)
bpy.types.WindowManager.char_map = bpy.props.BoolProperty(name="Character Map", description="Display Character Map", default=False)
#bpy.types.WindowManager.char_direction = bpy.props.EnumProperty(items=[('LTR', 'LTR', 'Left To Right'), ('RTL', 'RTL', 'Right To Left')], name="Text Direction", description="Left To Right or Right To Left", default='LTR')
bpy.types.WindowManager.charmap_page = bpy.props.IntProperty(name="Page", description="Character Map Page", default=5, min=0, max=1105)
bpy.types.WindowManager.charmap_rows = bpy.props.IntProperty(name="Rows", description="Character map rows", default=10, min=1, max=100)
bpy.types.WindowManager.charmap_cols = bpy.props.IntProperty(name="Cols", description="Character map columns", default=5, min=1, max=100)

class FONT_OT_append(bpy.types.Operator):
    ''' Insert special characters to the Text object'''
    bl_idname = "font.append_character"
    bl_label = "Append Special Character"
    bl_options = {'REGISTER', 'UNDO'}
    
    symbol_code = bpy.props.IntProperty(name="symbol code", default=0)
    add = bpy.props.BoolProperty(name="Clear added char", default=False)
    hex_update = False

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'FONT' and ob.mode == 'OBJECT')
        
    def execute(self, context):
        if (self.symbol_code > 0):
            context.window_manager.char_code = self.symbol_code
            self.symbol_code = 0
        
        char = chr(context.window_manager.char_code)
        self.put_char(context, char)
        return {'FINISHED'}
    
    def put_char(self, context, char):
        ob = context.active_object
        if (context.window_manager.char_prepend):
            ob.data.body = char + ob.data.body
        else:
            ob.data.body += char

    def pop_char(self, context):
        ob = context.active_object
        if (context.window_manager.char_prepend):
            ob.data.body = str(ob.data.body)[1:]
        else:
            ob.data.body = str(ob.data.body)[:-1]

    
    def draw(self, context):
        if (self.symbol_code != 0):
            context.window_manager.char_code = self.symbol_code
        if (context.window_manager.char_hex_code != str(hex(context.window_manager.char_code))[2:]):
            context.window_manager.char_hex_code = str(hex(context.window_manager.char_code))[2:]
        layout = self.layout
        split = layout.split(percentage=0.7)
        split.prop(context.window_manager, "char_code")
        split.prop(context.window_manager, "char_hex_code")
        row = layout.row()
        row.prop(context.window_manager, "char_prepend")
        row = layout.row()
        row.operator(FONT_OT_append.bl_idname, "Add Another").add = True

        
def draw_charmap(context, layout):
    if (context.window_manager.char_map):
        row = layout.row()
        row.prop(context.window_manager, "charmap_page")
        row = layout.row()
        rows = context.window_manager.charmap_rows
        cols = context.window_manager.charmap_cols
        j = 0
        page = context.window_manager.charmap_page
        amnt = rows * cols
        for i in range (page*amnt, page*amnt+amnt):
            if j % cols == 0:
                row = layout.row()
            row.operator(FONT_OT_append.bl_idname, chr(i)).symbol_code = i
            j += 1
    

class FONT_OT_file_importer(bpy.types.Operator): 
    ''' Select text file to import it's contents to the Text object '''
    bl_idname = "font.text_file_selector"
    bl_label = "Import Text File"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath = bpy.props.StringProperty(name="File Path", description="File path used for importing file", maxlen= 1024, default= "")
    filter_folder = bpy.props.BoolProperty(default=True)
    filter_text = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'FONT')
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        import os
        if os.path.exists(self.filepath):
            self.report({'INFO'}, 'Importing file: '+self.filepath)
            file_handler = open(self.filepath, "r")
            file_contents = file_handler.read()
            ob = context.active_object
            if context.window_manager.text_replace:
                ob.data.body = file_contents
            else:
                ob.data.body += file_contents
        else:
            self.report({'INFO'}, 'File does not exist')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.window_manager, "text_replace")


class FONT_PT_unicode_helper(bpy.types.Panel):
    ''' Unicode Helper panel in Tools menu '''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Unicode Helper'                                     

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'FONT')

    def draw(self, context):
        layout = self.layout
        layout.operator(FONT_OT_append.bl_idname, text = 'Add Character')
        layout.operator(FONT_OT_file_importer.bl_idname, text = 'Import From File')
        layout.prop(context.window_manager, "char_map")
        draw_charmap(context, layout)

def register():
    bpy.utils.register_module(__name__)
   
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
