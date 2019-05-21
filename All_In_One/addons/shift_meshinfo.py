#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### HEADER
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Mesh Info",
    "author"            : "Andrej Szontagh",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Mesh Info"}

import bpy

class MeshInfoPanel (bpy.types.Panel):
    
    bl_label        = "SHIFT - Mesh Info"
    bl_context      = "objectmode"

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):
        
        layout = self.layout

        obj = context.object

        try:
        
            mesh = bpy.data.meshes [obj.data.name];
            
            row = layout.row ()        
            row.label (text = "Count of polygons : %i" % len (mesh.faces))
                
            row = layout.row ()        
            row.label (text = "Count of vertices : %i" % len (mesh.vertices))
            
            row = layout.row ()
            row.label (text = "Count of edges : %i" % len (mesh.edges))
            
        except: pass
        
def register ():

    bpy.utils.register_module (__name__)

def unregister ():

    bpy.utils.unregister_module (__name__)
            
if __name__ == "__main__":
    
    register ()
    
