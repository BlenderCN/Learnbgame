#
#    Copyright (c) 2015 Shane Ambler
#
#    All rights reserved.
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    1.  Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#    2.  Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
#    OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#    LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# based on response to --
# http://blender.stackexchange.com/a/26722/935
# by Chebhou
#
# My version splits into two operators to work without a dialog
# this allows use of buttons without a dialog
# in my opinion this is a better user experience.

bl_info = {
    "name": "Text conversion",
    "author": "sambler",
    "version": (1,1),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Convert text object",
    "description": "Create a text file from the contents of a text object, or set the object contents from a file.",
    "warning": "",
    "wiki_url": "https://github.com/sambler/addonsByMe/blob/master/textToFile.py",
    "tracker_url": "https://github.com/sambler/addonsByMe/issues",
    "category": "Learnbgame",
}

import bpy

class textToFile(bpy.types.Operator):
    """text file to text object"""
    bl_idname = "object.text_to_file"
    bl_label = "Convert text object to file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.type == 'FONT':
            if None == bpy.data.texts.get(obj.name):
                bpy.data.texts.new(name = obj.name)

            text_file = bpy.data.texts[obj.name]
            text_file.clear()
            text = obj.data.body
            text_file.write(text)
        return {'FINISHED'}

class fileToText(bpy.types.Operator):
    """text object from text file"""
    bl_idname = "object.file_to_text"
    bl_label = "Convert text file to object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.type == 'FONT':
            if None == bpy.data.texts.get(obj.name):
                bpy.data.texts.new(name = obj.name)

            text_file = bpy.data.texts[obj.name]
            obj.data.body = text_file.as_string()
        return {'FINISHED'}

class textConversion(bpy.types.Panel):
    """Panel for quick text conversion"""
    bl_label = "Convert Text"
    bl_idname = "SCENE_PT_conversion"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'FONT')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("object.text_to_file")
        row = layout.row()
        row.operator("object.file_to_text")

class textSubMenu(bpy.types.Menu):
    bl_label = "Convert text"
    bl_idname = "OBJECT_MT_convert_text"

    def draw(self, context):
        self.layout.operator(textToFile.bl_idname)
        self.layout.operator(fileToText.bl_idname)

def convertMenu(self, context):
    self.layout.menu(textSubMenu.bl_idname, icon = 'OUTLINER_DATA_FONT')

def register():
    bpy.utils.register_class(textToFile)
    bpy.utils.register_class(fileToText)
    bpy.utils.register_class(textConversion)
    bpy.utils.register_class(textSubMenu)
    bpy.types.VIEW3D_MT_object.append(convertMenu)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(convertMenu)
    bpy.utils.unregister_class(textToFile)
    bpy.utils.unregister_class(fileToText)
    bpy.utils.unregister_class(textConversion)
    bpy.utils.unregister_class(textSubMenu)

if __name__ == "__main__":
    register()

