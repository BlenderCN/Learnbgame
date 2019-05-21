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
    "name": "0rAngE View Selected",
    "author": "0rAngE",
    "blender": (2, 80, 0),
    "category": "Learnbgame"
}

import bpy

class ViewSelectedZoomOut(bpy.types.Operator):
    bl_idname = "view_selected.zoomout"
    bl_label = "ViewSelected and ZoomOut"
    
    zoom_delta = bpy.props.IntProperty(name="Zoom Out", description="Steps to zoom out", min=0, max=10, default=4)
    
    def execute(self, context):
        #View Selected
        bpy.ops.view3d.view_selected()
        #Zoom Out
        for i in range(self.zoom_delta):
            bpy.ops.view3d.dolly(delta=-1, mx=context.region.width/2, my=context.region.height/2)
        return {'FINISHED'}
    
# Register / Unregister Classes    
def register():
    bpy.utils.register_class(ViewSelectedZoomOut)


def unregister():
    # Poly Pie_void
    bpy.utils.unregister_class(ViewSelectedZoomOut)
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    # clear the list
    del addon_keymaps[:]

if __name__ == "__main__":
    register()