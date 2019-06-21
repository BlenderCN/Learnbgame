'''
Copyright (C) 2017 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from bpy.props import StringProperty, EnumProperty

class report_message(bpy.types.Operator):
    bl_idname = "b_painter.report_message"
    bl_label = "Info Message"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}
    
    message = StringProperty(default="")
    type = EnumProperty(default="INFO",items=(("INFO","INFO","INFO"),("WARNING","WARNING","WARNING")))
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        ico="NONE"
        if self.type == "WARNING":
            ico="ERROR"
        elif self.type == "INFO":
            ico="QUESTION"    
        row.label(text="",icon=ico)
        row.label(text=self.message)
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        