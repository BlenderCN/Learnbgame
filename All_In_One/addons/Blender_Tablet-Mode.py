### BEGIN GPL LICENSE BLOCK #####
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
    "name": "Tablet Mode",
    "author": "Matthias Ellerbeck",
    "version": (0, 0, 3),
    "blender": (2, 76, 0),
    "location": "None",
    "description": "Enables better tablet integration for Blender",
    "warning": "Early development state!",
    "wiki_url": "",
    "category": "User Interface",
    }
    
import bpy

#operator for mouse functions
class WM_OT_MouseClickModalOperator(bpy.types.Operator):
    bl_idname = "wm.tabletmode"
    bl_label = "Tablet Mode: Activate"

    def modal(self, context, event):
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            bpy.ops.tabletmode.contextmenu()
            return{'RUNNING_MODAL'}
        return{'PASS_THROUGH'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return{'RUNNING_MODAL'}
        #return wm.invoke_popup(self)
        
#implementing a context-menu
class WM_OT_ContextMenuTabletMode(bpy.types.Operator):
    bl_idname = "tabletmode.contextmenu"
    bl_label = "Tablet Mode: Context Menu"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        print(context.area.type)
        return{'FINISHED'}
        
    def invoke(self, context, event):
        #wm = context.window_manager
        self.operator("node.delete", icon="X", text="Delete")
        self.operator("node.mute_toggle", icon="RESTRICT_RENDER_OFF", text="")
        return wm.invoke_popup(self)
        
    #def draw(self, context):
        #layout = self.layout
        #col = layout.column()
        #col.operator("node.delete", icon="X", text="Delete")
        #col.operator("node.mute_toggle", icon="RESTRICT_RENDER_OFF", text="")
        #col.operator("node.hide_socket_toggle", icon="RESTRICT_VIEW_OFF", text="")

#adding buttons for common used functions
def NodeEditorPanel(self, context):
    layout = self.layout
    col = layout.column()
    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.operator("node.delete", icon="X", text="Delete")
    row.operator("node.mute_toggle", icon="RESTRICT_RENDER_OFF", text="")
    row.operator("node.hide_socket_toggle", icon="RESTRICT_VIEW_OFF", text="")
    row.operator("node.group_edit", icon="ZOOM_ALL", text="")

#registration
def register():
    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(MouseClickModalOperator)
    bpy.types.NODE_HT_header.append(NodeEditorPanel)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(MouseClickModalOperator)
    bpy.types.NODE_HT_header.remove(NodeEditorPanel)

if __name__ == "__main__":
    register()
    
    bpy.ops.wm.tabletmode()