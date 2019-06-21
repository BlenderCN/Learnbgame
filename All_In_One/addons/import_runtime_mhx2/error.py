# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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

import bpy

theMessage = "No message"
theErrorLines = []

class ErrorOperator(bpy.types.Operator):
    bl_idname = "mhx2.error"
    bl_label = "MHX2 Error:"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        global theMessage, theErrorLines
        theErrorLines = theMessage.split('\n')
        maxlen = len(self.bl_label)
        for line in theErrorLines:
            if len(line) > maxlen:
                maxlen = len(line)
        width = 20+5*maxlen
        height = 20+5*len(theErrorLines)
        #self.report({'INFO'}, theMessage)
        wm = context.window_manager
        res = wm.invoke_props_dialog(self, width=width, height=height)
        return res

    def draw(self, context):
        global theErrorLines
        for line in theErrorLines:
            print(line)
            self.layout.label(line)


class MhxError(Exception):

    def __init__(self, value):
        global theMessage
        theMessage = value
        print("ERROR:", theMessage)
        bpy.ops.mhx2.error('INVOKE_DEFAULT')

    def __str__(self):
        return repr(self.value)


def handleMhxError(context):
    global theMessage
    print(theMessage)
