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
    "name": "Restore Render Parts",
    "description": "Restores the old render option of defining tiles by amount rather than pixels",
    "author": "Ray Mairlot",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "Properties Editor > Performance",
    "category": "Learnbgame",
}
    
    
import bpy


def calculateTileX(self,context):
    
    render = context.scene.render
    
    resolution = (render.resolution_x * render.resolution_percentage) / 100
    
    render.tile_x  = resolution / context.scene.x_parts
    
    
    
def calculateTileY(self,context):
    
    render = context.scene.render
    
    resolution = (render.resolution_y * render.resolution_percentage) / 100
    
    render.tile_y  = resolution / context.scene.y_parts
   

    
bpy.types.Scene.x_parts = bpy.props.IntProperty(name="x_parts", description="Define the amount of parts the width of the image will be divided into", default=1, min=1, update=calculateTileX)
bpy.types.Scene.y_parts = bpy.props.IntProperty(name="y_parts", description="Define the amount of parts the height of the image will be divided into", default=1, min=1, update=calculateTileY)



def restoreRenderParts(self, context):

    row = self.layout.row(align=True)
    row.label(text="Render parts:")  
    row.prop(bpy.context.scene, "x_parts", text="X")
    row.prop(bpy.context.scene, "y_parts", text="Y") 



def register():
    bpy.types.CyclesRender_PT_performance.append(restoreRenderParts)
    bpy.types.RENDER_PT_performance.append(restoreRenderParts)



def unregister():
    bpy.types.CyclesRender_PT_performance.remove(restoreRenderParts)
    bpy.types.RENDER_PT_performance.remove(restoreRenderParts)


if __name__ == "__main__":
    register()

