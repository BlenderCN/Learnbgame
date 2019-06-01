'''
Created on 10/05/2013

@author: forestmedina
'''

import bpy;
import struct;
import math;
import mathutils;
from bpy_extras.io_utils import ExportHelper

from bpy.utils import (
        register_class,
        unregister_class,
        )

def register():
    register_class(Exporter)
    register_class(PanelOpciones)
    register_class(FileHeader)
    register_class(FileBody)


def unregister():
    unregister_class(Exporter)
    unregister_class(PanelOpciones)
    unregister_class(FileHeader)
    unregister_class(FileBody)

class PanelOpciones(bpy.types.Panel):
    bl_label = "exportadorOpengl"
#    bl_idname = "OBJECT_exportadorOpengl"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = bpy.context.active_object
        self.layout.prop(obj, "colisionador","Colisionador");

class Vertice():
    def __init__(self):
        self.co=[0.0]*3;
        self.normal=[0.3]*3;
        self.color=[0.0]*3;
        return;

class Mesh():
    vertexFormat ="";
    vertices    =[];
    boundingBox ="";
    boundingSphere="";
    parts="";
    def __init__(self):
        return;

    def writeData(self,f):
        f.write(struct.pack("<I",len(self.vertices)));
        for v in self.vertices:
            f.write(struct.pack("<f",v.co[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.co[2]));#VextexSize 3 (x,y,z)
        for v in self.vertices:
            f.write(struct.pack("<f",v.normal[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.normal[2]));#VextexSize 3 (x,y,z)
        for v in self.vertices:
            f.write(struct.pack("<f",v.color[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.color[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",v.color[2]));#VextexSize 3 (x,y,z)
        for v in self.vertices:
            if len(v.groups)>0:
                f.write(struct.pack("f",v.groups[0].group));
            else:
                f.write(struct.pack("f",0));
        for v in self.vertices:
            if len(v.groups)>0:
                f.write(struct.pack("f",v.groups[0].weight));
            else:
                f.write(struct.pack("f",0));
        f.write(struct.pack("<I",len(self.caras)));
        for c in self.caras:
            f.write(struct.pack("<I",c.vertices[0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<I",c.vertices[1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<I",c.vertices[2]));#VextexSize 3 (x,y,z)
        print ("Importado")
        return ;
        
        
class Esqueleto():
    huesos =[];
    
    def __init__(self):
        self.huesos=[];
        return;

    def writeData(self,f):
        f.write(struct.pack("<I",len(self.huesos)));
        for h in self.huesos:
            if h.parent is None:
                f.write(struct.pack("<i",-1));
            else:
                f.write(struct.pack("<i",self.huesos.find(h.parent.name)));
            f.write(struct.pack("<f",h.head_local.x));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.head_local.y));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.head_local.z));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.tail_local.x));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.tail_local.y));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.tail_local.z));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[0][0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[1][0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[2][0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[3][0]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[0][1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[1][1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[2][1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[3][1]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[0][2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[1][2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[2][2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[3][2]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[0][3]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[1][3]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[2][3]));#VextexSize 3 (x,y,z)
            f.write(struct.pack("<f",h.matrix_local[3][3]));#VextexSize 3 (x,y,z)


class Exporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_opengl.gpb";
    bl_label        = "Exportador OPENGL personalizado";
    bl_options      = {'PRESET'};
    filename_ext    = ".mesh";
    objetos=[];
    
        
    def procesarMesh(self, bobject):
        for mod in bobject.modifiers:
            if mod.type=='ARMATURE':
                mod.show_viewport=False; 
        mesh = bobject.to_mesh(bpy.context.scene,True,'PREVIEW',True,False);
        for mod in bobject.modifiers:
            if mod.type=='ARMATURE':
                mod.show_viewport=True; 
        meshes_to_clear.append(mesh);
        omesh=Mesh();

        omesh.vertices=[0]*len(mesh.vertices)
        for i in range(0,len(mesh.vertices)):
            v=Vertice();
            v.co=mesh.vertices[i].co;
            v.normal=mesh.vertices[i].normal;
            v.groups=mesh.vertices[i].groups;
            omesh.vertices[i]=v;
        omesh.caras=mesh.polygons;
        colores=[0]*10;
        for p in mesh.polygons:
            for li in p.loop_indices:
                vi=mesh.loops[li].vertex_index;
                omesh.vertices[vi].color= mesh.vertex_colors[0].data[li].color; 
        omesh.colores=colores;
        return omesh;
        
    def procesarArmadura(self, bobject):
        arm = bobject.data;
        esq=Esqueleto();
        esq.huesos=arm.bones;
        return esq;

    def procesarAnimaciones(self, bobject,f):
        f.write(struct.pack("<I",len(bpy.data.actions))); 
        for a in bpy.data.actions:
            bobject.animation_data.action=a;
            inicio, fin = [int(x) for x in a.frame_range]
            fps=bpy.context.scene.render.fps;
            total=fin-inicio;
            print("acciones:"+str(len(bpy.data.actions)));
#            f.write(struct.pack("<I",len(a.name))); 
#            if len(a.name)>0:
            f.write(bytearray(a.name+"\00","ascii"));
            f.write(struct.pack("<I",total)); #Cantidad de frames
            i=0;
            for frame in range(inicio,fin):
                f.write(struct.pack("<f",float(frame)/float(fps)));
                bpy.context.scene.frame_set(frame);
                i=i+1;
                for h in bobject.pose.bones:
                    matfix =mathutils.Matrix.Rotation(math.radians(-90), 4, "X");
                    matorig =h.bone.matrix_local*matfix;
                    matpose=h.matrix*matfix;
                    mat=matpose*matorig.inverted();
                    q=mat.to_quaternion();
                    loc=h.matrix.translation-h.bone.matrix_local.translation;
#                    q=h.rotation_quaternion;
                    f.write(struct.pack("<f",loc.x));
                    f.write(struct.pack("<f",loc.y));
                    f.write(struct.pack("<f",loc.z));
                    f.write(struct.pack("<f",q.x));
                    f.write(struct.pack("<f",q.y));
                    f.write(struct.pack("<f",q.z));
                    f.write(struct.pack("<f",q.w));
            print("cuadros:"+str(i)); 


    def execute(self, context):
        global meshes_to_clear;
        global reference_count;
        reference_count=0;
        meshes_to_clear=[];
#        bpy.ops.object.mode_set(mode='OBJECT');
        result = {'FINISHED'};
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ob.is_visible(bpy.context.scene):
                file = open(self.filepath, 'bw');
                self.procesarMesh(ob).writeData(file);      
                file.close();
            if ob.type == 'ARMATURE':
                file = open(self.filepath+".esq", 'bw');
                self.procesarArmadura(ob).writeData(file);
                self.procesarAnimaciones(ob,file);
                file.close();

        for m in meshes_to_clear:
            bpy.data.meshes.remove(m);
        return result;

