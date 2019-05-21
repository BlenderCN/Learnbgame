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
    "name": "Oscurart Copy Vertex Location",
    "author": "Oscurart",
    "version": (1,0),
    "blender": (2, 5, 9),
    "api": 4000,
    "location": "Object > Transform > Copy Vertex Location",
    "description": "Transfer vertex location",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame"
}



import bpy


        

def printea (self, SELECT):   
    if  SELECT is False:
        ## AVERIGUO OBJETO SECUNDARIO
        for objeto in bpy.context.selected_objects:
            if objeto != bpy.context.active_object:
                secondary=objeto
        ## SETEO VERTICES EN SU LUGAR
        for vertice in bpy.context.active_object.data.vertices:
            vertice.co=secondary.data.vertices[vertice.index].co
    else:
        ## AVERIGUO OBJETO SECUNDARIO
        for objeto in bpy.context.selected_objects:
            if objeto != bpy.context.active_object:
                secondary=objeto
        ## SETEO VERTICES EN SU LUGAR
        for vertice in bpy.context.active_object.data.vertices:
            if vertice.select == True:
                vertice.co=secondary.data.vertices[vertice.index].co            


class OscCopyVertexLocation (bpy.types.Operator):
    bl_idname = "mesh.copy_vertex_location"
    bl_label = "Copy Vertex Location" 
    bl_options =  {"REGISTER","UNDO"}  
    
    SELECTVERT = bpy.props.BoolProperty(default=False, name="Selected Vertices")
      
    def execute (self, context):
        printea(self, self.SELECTVERT)        
        return {'FINISHED'}
    
    
def menu_oscCopyVertex(self, context):
    self.layout.operator("mesh.copy_vertex_location", 
        text="Copy Vertex Location", 
        icon='PLUGIN')
        



def register():
    bpy.utils.register_class(OscCopyVertexLocation)
    bpy.types.VIEW3D_MT_transform.append(menu_oscCopyVertex)

def unregister():
    bpy.utils.register_class(OscCopyVertexLocation)
    bpy.types.VIEW3D_MT_transform.append(menu_oscCopyVertex)

if __name__ == "__main__":
    register()
