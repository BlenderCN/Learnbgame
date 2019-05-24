 ##### BEGIN GPL LICENSE BLOCK #####
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
    "name": "Highpass",
    "description": "Highpass Filter for Tracks. Intended for high quality stabilization.",
    "author": "Björn Sonnenschein",
    "version": (0, 1),
    "blender": (2, 71, 0),
    "location": "Clip Editor > Tools",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame",
}


import bpy

IntProperty = bpy.props.IntProperty
rangeprop = IntProperty( name="Range", description="With higher values, slower motions will be overtaken", default=5, min=1, max=100, step=1)
bpy.types.Scene.smooth_range = rangeprop

class HighpassPanel(bpy.types.Panel):    
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_label = "Highpass"

    def draw(self, context):
        scn = bpy.context.scene
        layout = self.layout
        
        row = layout.row()
        col = row.column()
        
        col.operator( "highpass.apply" ) 
        row.prop( bpy.context.scene, "smooth_range" )

class Apply_Highpass_Operator(bpy.types.Operator): 
     
    bl_idname = "highpass.apply"
    bl_label = "Apply"
            
    def invoke(self, context, event ):  

        for a in bpy.context.window.screen.areas:
            if a.type == 'CLIP_EDITOR':
                editor = a.spaces.active
                break

        track = editor.clip.tracking.tracks.active
        markers = track.markers

        smoothrange = bpy.context.scene.smooth_range
        smoothcoords = []
        startframe = bpy.context.scene.frame_start
        endframe = bpy.context.scene.frame_end
        counter = 0
        startcoords = markers.find_frame( startframe, exact = True).co


        for i in range(startframe, endframe + 1):
            
            temp = [0.0, 0.0]
            framecoords = markers.find_frame( i, exact = True).co
            
            for j in range(i - smoothrange, i + smoothrange + 1):
                
                if (j >= startframe and j <= endframe):
                    coords = markers.find_frame( j, exact = True).co
                else:
                    coords = markers.find_frame( i, exact = True).co
                    
                temp[0] = temp[0] + coords[0]
                temp[1] = temp[1] + coords[1]
                
            temp[0] = temp[0] / (2 * smoothrange + 1)
            temp[1] = temp[1] / (2 * smoothrange + 1)
            smoothcoords.append((framecoords[0] - temp[0] + startcoords[0], framecoords[1] - temp[1] + startcoords[1]))
        
        bpy.ops.clip.copy_tracks()
        bpy.ops.clip.paste_tracks()

        for i in range ( startframe, endframe + 1):
          
            editor.clip.tracking.tracks.active.markers.insert_frame(i, co=smoothcoords[counter])
            counter = counter + 1
            
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class( HighpassPanel ) 
    bpy.utils.register_class( Apply_Highpass_Operator ) 

def unregister():
    bpy.utils.register_class( HighpassPanel ) 
    bpy.utils.unregister_class( Apply_Highpass_Operator ) 

if __name__ == "__main__":
    register()
