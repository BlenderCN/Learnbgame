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
 
# <pep8 compliant> 
 
bl_info = { 
    "name": "br_remove_vertex_alone", 
    "author": "bruno dindoun sanchiz", 
    "version": (2, 1, 0), 
    "blender": (2, 6, 9), 
    "api": "ee", 
    "location": "View3D > Properties > br_remove_vertex_alone", 
    "description": "remove vertex alone in a mesh", 
    "warning": "don t work when number of vertices is different of len(ob.data.vertices)) on one version of blender; perrhaps 2.65", 
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/" \ 
    "Scripts/3D_interaction/Sun_Position", 
    "tracker_url": "https://projects.blender.org/tracker/" \ 
    "index.php?", 
    "category": "Learnbgame",
} 
 
import bpy,bmesh  
from mathutils import * 
import math 
import bgl 
 
 
# --------------------------------------------------------------------------- 
 
 
class br_remove_vertex_alone(bpy.types.Operator): 
    bl_idname = "mesh.br_remove_vertex_alone" #bpy.ops.vcv.br_remove_vertex_alone 
    bl_label = "br_remove_vertex_alone" 
    bl_description = "remove vertex alone in a mesh" 
    bl_context = "mesh_edit" 
    bl_register = True 
 
    def modal(self, context, event): 
        return {'PASS_THROUGH'} 
 
    def invoke(self, context, event): 
        #print("context.area.type",context.area.type)         
        scene = context.scene 
        objetactif=scene.objects.active 
        for obj in bpy.context.selected_objects: 
            if obj.type== 'MESH': 
                #print('work  '+obj.name) 
                scene.objects.active=obj 
                bm=bmesh.from_edit_mesh(obj.data) 
                v=bm.verts 
                E=bm.edges 
                tmpv=[True for i in range(len(v))]#numeros des verts a detruire 
                for i in E: 
                    tmpv[i.verts[0].index]=False#verts pas a detruire 
                    tmpv[i.verts[1].index]=False#verts pas a detruire 
                adetruire=[]#liste des numeros des verts a detruire 
                for i in range(len(tmpv)): 
                    if tmpv[i]==True: 
                        #print(" a detruire : ",v[i],v[i].co) 
                        adetruire+=[i] 
                adetruire.sort() 
                adetruire.reverse()#liste des numeros des verts a detruire rangee dans le sens inverse 
                for i in adetruire: 
                    bm.verts.remove(v[i]) 
                bpy.ops.object.editmode_toggle() 
                bpy.ops.object.editmode_toggle() 
        scene.objects.active=objetactif 
        return{'FINISHED'} 
 
 
 
############################################################################ 
 
 
 
 
 
def register(): 
    bpy.utils.register_class(br_remove_vertex_alone) 
     
def unregister(): 
    bpy.utils.unregister_class(br_remove_vertex_alone) 
      
if __name__ == "__main__": 
    register()

