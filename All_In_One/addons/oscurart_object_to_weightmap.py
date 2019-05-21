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
    "name": "Object to weightMap",
    "author": "Eugenio Pignataro",
    "version": (1,1),
    "blender": (2, 5, 6),
    "location": "View3D > Tools > ObjectToWeightmap",
    "description": "Setea los valores de mapa de peso segun la distancia a un objeto",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy, math

## FUNCION QUE EJECUTA EL TRANSPASO
def oscOtwExecute(context,CWFACTOR,CWOFFSET,EMISORLOCATION):
    ## MARCO LAS VARIABLES DE SELECCION 
    CWFACTOR=CWFACTOR
    CWOFFSET=CWOFFSET
    CWSELECTION = bpy.context.selected_objects
    CWOBJRECEPTOR = bpy.context.active_object

    
    ## SETEO EL OBJETO EMISOR POR DESCARTE
    for SEL in CWSELECTION:
        if SEL.name != CWOBJRECEPTOR.name:
            print(SEL)
            CWOBJEMISOR=SEL 

   
    ## SETEO LA LOCATION DEL EMISOR
    LOCEMISOR=CWOBJEMISOR.location
    CWOBJEMISOR.location=(LOCEMISOR[0]+EMISORLOCATION[0],
        LOCEMISOR[1]+EMISORLOCATION[1],
        LOCEMISOR[2]+EMISORLOCATION[2])   

                 
    ## DECLARO FUNCION
    def DISTANCIAENTRE(ob1,ob2):
        VECTOR = ob1.co-ob2.location
        POW = pow(VECTOR[0],2)+pow(VECTOR[1],2)+pow(VECTOR[2],2)
        print("LA DISTANCIA ENTRE OBJETOS ES DE: "+str(math.sqrt(POW)))
        return((math.sqrt(POW)/CWFACTOR)+(CWOFFSET)) 
    
    ## SETEO EL VG ACTIVE INDEX
    CGACTINDEX=CWOBJRECEPTOR.vertex_groups.active_index
        
    ## SETEA VALORES A LOS VERTICES        
    for VERTICES in CWOBJRECEPTOR.data.vertices:
        VERTICES.groups[CGACTINDEX].weight = DISTANCIAENTRE(VERTICES,CWOBJEMISOR)

# IMPORTA LIBRERIA DE PROPIEDADES        
from bpy.props import *

# CREA PANEL TEMPORAL DINAMICO
class MESH_OT_oscOTW(bpy.types.Operator):
    bl_idname = "mesh.oscotwm"
    bl_label = "Apply!"
    bl_options = {'REGISTER', 'UNDO'}
    factor = FloatProperty(name="Factor", default=1.0) 
    offset = FloatProperty(name="Offset", default=1.0) 
    emisorPosition = FloatVectorProperty(name="Emisor Location")               
    def execute(self, context):
        oscOtwExecute(context, 
            self.factor,self.offset,self.emisorPosition)

        return {'FINISHED'}            

# CREA PANEL DE ADD    
def menu_oscotwm(self, context):
    self.layout.operator("mesh.oscotwm", 
        text="Oscurart Object To WeightMap", 
        icon='PLUGIN')


 
def register():
   bpy.utils.register_module(__name__)
   bpy.types.VIEW3D_MT_paint_weight.append(menu_oscotwm)
 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_oscotwm)
 
if __name__ == "__main__":
    register()    