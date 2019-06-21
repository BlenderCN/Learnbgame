'''
Created on 10/05/2013

@author: forestmedina
@contributor: cesarpachon
'''

import bpy;
import struct;
import mathutils;
import math;
from bpy_extras.io_utils import ExportHelper

from bpy.utils import (
        register_class,
        unregister_class,
        )

def register():
    register_class(Exporter)
    register_class(FileHeader)
    register_class(FileBody)


def unregister():
    unregister_class(Exporter)
    unregister_class(FileHeader)
    unregister_class(FileBody)
    delete_properties()



class Reference:
    reference ="";#
    tipo =0   #
    offset =0   #
    position =0
    def __init__(self):
        self.tipo=ReferenceType.NODE;
        return;

    def writeReference(self,f):
        f.write(struct.pack("<I",len(self.reference)));#mesh
        if len(self.reference)>0:
            f.write(bytearray(self.reference,"ascii"));
        f.write(struct.pack("<I",self.tipo)),
        self.position=f.tell();
        f.write(struct.pack("<I",self.offset));
        return ;

    def writeExtra(self,f):    
        return;
        
    def writeNode(self,f):
        return;
        
    def updateOffset(self,f):
        f.seek(self.position);
        f.write(struct.pack("<I",self.offset));
        return;        

class Node(Reference):
    tipoNodo =0   #enum NodeType
    transforms =[]   #float[16]
    parent_id  =""   #string
    childrens   =[]  #Node[]
    camera     =None    #Camera
    light      =None   #Light
    model      =None   #Model
    
    def __init__(self):
        self.tipo=ReferenceType.NODE;
        self.tipoNodo=1;
        self.transforms=[0]*16;
        self.camera=None;
        self.light=None;
        self.model=None;
        self.childrens=[];
        self.parent_id=None;
        return;

    def writeReference(self,f):
        Reference.writeReference(self,f);
        for c in self.childrens:
            c.writeReference(f);
        if not self.camera is None:
            self.camera.writeReference(f);
        if not self.model is None:
            self.model.writeReference(f);
        
        
    def updateOffset(self,f):
        Reference.updateOffset(self,f);
        for c in self.childrens:
            c.updateOffset(f);
        if not self.camera is None:
            self.camera.updateOffset(f);
        if not self.model is None:
            self.model.updateOffset(f);
       
    def writeNode(self,f):
        self.writeData(f);
        return;
    
    def writeExtra(self,f):   
        if not self.model is None:
            self.model.writeExtra(f);
        for c in self.childrens:
            c.writeExtra(f);
        return;
    
    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("<I",self.tipoNodo));
        for t in self.transforms:
            f.write(struct.pack("<f",t));
        if not self.parent_id is None:
            f.write(struct.pack("<I",len(self.parent_id)+1));#mesh
            f.write(bytearray('#',"ascii"));
            if len(self.parent_id)>0:
                f.write(bytearray(self.parent_id,"ascii"));
        else:
            f.write(struct.pack("<I",0));
        f.write(struct.pack("<I",len(self.childrens))),#hijos longitud de cadena 0
        if len(self.childrens)>0:
            for c in self.childrens:
                c.writeData(f);
        if not self.camera is None:
            self.camera.writeData(f);
        else:
            f.write(struct.pack("B",0));            
        if not self.light is None:
            self.light.writeData(f);
        else:
            f.write(struct.pack("B",0));#luz longitud de cadena 0
        if not self.model is None:
            self.model.writeData(f);
        else:
            f.write(struct.pack("<I",1));#mesh
            f.write(bytearray('#',"ascii"));
        return ;
    
    #
    # set the transform attribute changing blender to gameplay coordinates
    #method based on: 
    #http://gamedev.stackexchange.com/questions/44058/exporting-bind-and-keyframe-bone-poses-from-blender-to-use-in-opengl
    def setTransform(self, bobject):
        matrix = bobject.matrix_world
        # World transform: Blender -> OpenGL
        #--
        #method 1: post multiply for a new transformation matrix
        # this will add a mirror effect 
        #worldTransform = mathutils.Matrix().Identity(4)
        #worldTransform *= mathutils.Matrix.Rotation(math.radians(90), 4, "X")
        #worldTransform *= mathutils.Matrix.Scale(-1, 4, (0,0,1))
        # Mesh (local) transform matrix
        #matrix_world = matrix.copy()
        #matrix_world = worldTransform * matrix_world
        #--
        #method 2: build the matrix from scratch (no mult by matrix_world)
        matrix_world = mathutils.Matrix().Identity(4)
        loc = bobject.location.copy()
        val = loc.y
        loc.y = loc.z
        loc.z = -val
        matrix_world*= mathutils.Matrix.Translation(loc)       
        rot = bobject.rotation_euler
        matrix_world *= mathutils.Matrix.Rotation(-rot.y, 4, "Z")
        matrix_world *= mathutils.Matrix.Rotation(rot.z, 4, "Y")
        matrix_world *= mathutils.Matrix.Rotation(rot.x, 4, "X")
        matrix_world *= mathutils.Matrix.Scale(bobject.scale.y, 4, (0, 0, 1))
        matrix_world *= mathutils.Matrix.Scale(bobject.scale.z, 4, (0, 1, 0))
        matrix_world *= mathutils.Matrix.Scale(bobject.scale.x, 4, (1, 0, 0))
        self.transforms[0]=matrix_world[0][0];
        self.transforms[1]=matrix_world[1][0];
        self.transforms[2]=matrix_world[2][0];
        self.transforms[3]=matrix_world[3][0];
        self.transforms[4]=matrix_world[0][1];
        self.transforms[5]=matrix_world[1][1];
        self.transforms[6]=matrix_world[2][1];
        self.transforms[7]=matrix_world[3][1];
        self.transforms[8]=matrix_world[0][2];
        self.transforms[9]=matrix_world[1][2];
        self.transforms[10]=matrix_world[2][2];
        self.transforms[11]=matrix_world[3][2];
        self.transforms[12]=matrix_world[0][3];
        #if you want to manually change coords, it is like this:
        #self.transforms[14]=-matrix_world[1][3];
        #self.transforms[13]=matrix_world[2][3];
        self.transforms[13]=matrix_world[1][3];
        self.transforms[14]=matrix_world[2][3];
        self.transforms[15]=matrix_world[3][3];
        return ;


class Model (Reference):
    mesh     =""   #Mesh
    meshSkin =""    #MeshSkin
    materials=[]     #Material[]
    def __init__(self):
        self.tipo=ReferenceType.MODEL;
        self.meshSkin=None;
        return;

    def writeReference(self,f):
        self.mesh.writeReference(f);
        return;
        
    def updateOffset(self,f):
        self.mesh.updateOffset(f);
        return;
        
    def writeNode(self,f):
        return;
    
    def writeExtra(self,f):  
        self.mesh.writeData(f);
        return;
    
    def writeData(self,f):
        f.write(struct.pack("<I",len(self.mesh.reference)+1));#mesh
        f.write(bytearray('#',"ascii"));
        if len(self.mesh.reference)>0:
            f.write(bytearray(self.mesh.reference,"ascii"));
        if self.meshSkin is None:
            f.write(struct.pack("B",0));#hasMeshSkin no
        else:
            f.write(struct.pack("B",1));#hasMeshSkin yes
            self.meshSkin.writeData(f);
        f.write(struct.pack("<I",0));#material longitud de arreglo 0
        return ;

class Mesh(Reference):
    vertexFormat ="";
    vertices    =[];
    boundingBox ="";
    boundingSphere="";
    parts="";
    useVertexWeights=False
    uvLayers=None
    useUVLayers=False
    numVertexUsages = 2
    vertexFormatFloatLen=3+3
    def __init__(self):
        self.tipo=ReferenceType.MESH;
        return;
    
    #
    # writes a single vertex info to the stream.
    # notice that each vertex may be written many times,
    # because different polygons share the same vertices 
    # with different uv coordinates.
    #
    def writeVertex(self, vertexfaceid, face, f):
        id = face.vertices[vertexfaceid]
        v = self.vertices[id]
        f.write(struct.pack("<f",v.co[0]));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",v.co[2]));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",-v.co[1]));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",v.normal[0]));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",v.normal[2]));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",-v.normal[1]));#VextexSize 3 (x,y,z)
        if self.useVertexWeights:
            ngroups=0;
            for g in v.groups:
                f.write(struct.pack("<f",g.group));
                ngroups+=1;
                if ngroups>=4:
                    break;
            while ngroups<4:
                f.write(struct.pack("<f",0));#VextexSize 3 (x,y,z)
                ngroups+=1;
            ngroups=0;
            for g in v.groups:
                f.write(struct.pack("<f",g.weight));
                ngroups+=1;
                if ngroups>=4:
                    break;
            while ngroups<4:
                f.write(struct.pack("<f",0));#VextexSize 3 (x,y,z)
                ngroups+=1;
        #now export as many uvs as uvlayers in the mesh..
        if self.useUVLayers:
            for uvlayer in self.uvLayers:
                #uvloop = uvlayer.data[id];
                uvloop = uvlayer.data[face.loop_indices[vertexfaceid]]
                f.write(struct.pack("<f",uvloop.uv[0]));
                f.write(struct.pack("<f",uvloop.uv[1]));
        return;

    def writeData(self,f):
        self.offset=f.tell();
        self.numVertexUsages =2
        self.vertexFormatFloatLen=3+3#three floats from POSITION, three floats from NORMAL
        if self.useVertexWeights:
            self.numVertexUsages +=2
            self.vertexFormatFloatLen +=8#four floats for BLENDINDICES, four for BLENDWEIGHTS 
        if self.useUVLayers:
            #num of usages depends of number of uvlayers..
            self.numVertexUsages += len(self.uvLayers)
            self.vertexFormatFloatLen += 2*len(self.uvLayers) #two floats for each uvlayer
        f.write(struct.pack("<I",self.numVertexUsages));#Cantidad de vertexUsage
        #print("usage POSITION*3")
        f.write(struct.pack("<I",1));#VextexUsage 1-POSITION
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        #print("usage NORMAL*2")
        f.write(struct.pack("<I",2));#VextexUsage 2-NORMAL
        f.write(struct.pack("<I",3));#VextexSize 3 (x,y,z)
        if self.useVertexWeights:
            #print("usage BLENDINDICES*4")
            f.write(struct.pack("<I",7));#VextexUsage 7-BLENDINDICES
            f.write(struct.pack("<I",4));#VextexSize 4 max joints
            #print("usage BLENDWEIGHTS*4")
            f.write(struct.pack("<I",6));#VextexUsage 6-BLENDWEIGTHS
            f.write(struct.pack("<I",4));#VextexSize 4 max joints
        if self.useUVLayers:
            textcoordid = 7
            for layer in self.uvLayers:
                textcoordid+=1
                #print("usage TEXTCOORDID%d*2"%textcoordid)
                f.write(struct.pack("<I", textcoordid));
                f.write(struct.pack("<I", 2));#two floats for U,V
        #size in bytes that will require each vertex element 
        f.write(struct.pack("<I",3*len(self.parts)*(self.vertexFormatFloatLen)*4));
        #iterate over polygons and writes each vertex
        for face in self.parts:
            #for vertexid in face.vertices:
            self.writeVertex(0, face, f);
            self.writeVertex(1, face, f);
            self.writeVertex(2, face, f);
        #Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box
        f.write(struct.pack("<f",0));#Omit bounding box


        #Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        f.write(struct.pack("<f",0));#Omit bounding sphere
        
        #mesh parts (faces index array)
        f.write(struct.pack("<I",1));#MeshPart Array of only 1 part
        f.write(struct.pack("<I",4));#GL_TRIANGLES
        f.write(struct.pack("<I",5125));#Unsigned int Index format
        f.write(struct.pack("<I",len(self.parts)*3*4));#Unsigned int Index format
        i = 0
        for face in self.parts:
            for vertexid in face.vertices:
                f.write(struct.pack("<I",i));#
                i=i+1;
        return ;
        
class MeshSkin(Reference):
    
    def __init__(self):
        self.tipo=ReferenceType.MESHSKIN;
        self.bindShape=[0]*16   ;
        self.joints=[];
        self.jointBindPoses=[];
        self.boundingBox=None;
        self.boundingSphere=None;
        return;

    def writeData(self,f):
        self.offset=f.tell();
        print("BindShape "+str(len(self.bindShape)));
        for b in self.bindShape:
            f.write(struct.pack("<f",b));
        f.write(struct.pack("<I",len(self.joints)));#joints
        for j in self.joints:
            f.write(struct.pack("<I",len(j.reference)+1));#mesh
            f.write(bytearray('#',"ascii"));
            f.write(bytearray(j.reference,"ascii"));

        f.write(struct.pack("<I",len(self.joints)*16));#joints
        for b in self.jointBindPoses:
            f.write(struct.pack("<f",b));
        #Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #f.write(struct.pack("<f",0));#Omit bounding box
        #Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        #f.write(struct.pack("<f",0));#Omit bounding sphere
        return ;   
        
        
class Light(Reference):
    lightType = None#byte, see LampType class
    color = []#float r b g 
    range = 0.0#float
    innerAngle=0.0#float
    outerAngle=0.0#float
    def __init__(self):
        self.tipo=ReferenceType.LIGHT;
        self.color = [1.0, 1.0, 1.0];
        return;
    
    def writeData(self, f):
        self.offset=f.tell();
        print("lamp writeData %d"%self.offset);
        f.write(struct.pack("B",self.lightType));
        f.write(struct.pack("<f",self.color[0]));
        f.write(struct.pack("<f",self.color[1]));
        f.write(struct.pack("<f",self.color[2]));
        if self.lightType == LampType.POINT or self.lightType == LampType.SPOT:
            f.write(struct.pack("<f",self.range));
        if self.lightType == LampType.SPOT:
            f.write(struct.pack("<f",self.innerAngle));
            f.write(struct.pack("<f",self.outerAngle));
        return;        

class Camera(Reference):
    cameraType =0#byte {perspective|orthographic}
    aspectRatio =0.0#float
    nearPlane =0.0#float
    farPlane =0.0#float
    fieldOfView =0.0 #[ cameraType : perspective
                #  fieldOfView float
                #]
                #[ cameraType : orthographic
                #  magnification float[2]
                #]
    def __init__(self):
        self.tipo=ReferenceType.CAMERA;
        return;

    def writeData(self,f):
        self.offset=f.tell();
        f.write(struct.pack("B",self.cameraType));#VextexUsage 2-POSITION
        f.write(struct.pack("<f",self.aspectRatio));#VextexSize 3 (x,y,z)
        f.write(struct.pack("<f",self.nearPlane));#VextexUsage 2-NORMAL
        f.write(struct.pack("<f",self.farPlane));#VextexUsage 2-NORMAL
        f.write(struct.pack("<f",self.fieldOfView));#VextexSize 3 (x,y,z)
        return ;        


class ReferenceType:
    SCENE=1;
    NODE=2;
    MODEL=11;
    MESH=34;
    MESHSKIN=36;
    CAMERA=32;
    LIGHT=33; 


class NodeType:
    NODE = 1,
    JOINT = 2
    
class LampType:
    DIRECTIONAL= 1;
    POINT =  2;
    SPOT= 3; 

    



#class Exporter(bpy.types.Operator, ExportHelper):
class Exporter():
    bl_idname       = "export_gameplay.gpb";
    bl_label        = "Gameplay3d Exporter";
    bl_options      = {'PRESET'};
    filename_ext    = ".gpb";
    objetos=[];
    
    def procesarArmature(self,nodeMesh, mesh):
        bobject=mesh.parent;
        armature = bobject.data;
        nodeMesh.model.meshSkin=MeshSkin();
        node= Node();
        node.transforms[0]=bobject.matrix_world[0][0];
        node.transforms[1]=bobject.matrix_world[1][0];
        node.transforms[2]=bobject.matrix_world[2][0];
        node.transforms[3]=bobject.matrix_world[3][0];
        node.transforms[4]=bobject.matrix_world[0][1];
        node.transforms[5]=bobject.matrix_world[1][1];
        node.transforms[6]=bobject.matrix_world[2][1];
        node.transforms[7]=bobject.matrix_world[3][1];
        node.transforms[8]=bobject.matrix_world[0][2];
        node.transforms[9]=bobject.matrix_world[1][2];
        node.transforms[10]=bobject.matrix_world[2][2];
        node.transforms[11]=bobject.matrix_world[3][2];
        node.transforms[12]=bobject.matrix_world[0][3];
        node.transforms[13]=bobject.matrix_world[1][3];
        node.transforms[14]=bobject.matrix_world[2][3];
        node.transforms[15]=bobject.matrix_world[3][3];
        node.tipoNodo=NodeType.JOINT;
        node.reference=bobject.name;
        self.objetos.append(node);
        huesos={};
        nodeMesh.model.meshSkin.jointBindPoses=[0]*(len(armature.bones)*16);
        i=0;
        for b in armature.bones:
            bone= Node();
            bone.reference=b.name;
            nodeMesh.model.meshSkin.joints.append(bone);
            bone.transforms[0]=b.matrix_local[0][0];
            bone.transforms[1]=b.matrix_local[1][0];
            bone.transforms[2]=b.matrix_local[2][0];
            bone.transforms[3]=b.matrix_local[3][0];
            bone.transforms[4]=b.matrix_local[0][1];
            bone.transforms[5]=b.matrix_local[1][1];
            bone.transforms[6]=b.matrix_local[2][1];
            bone.transforms[7]=b.matrix_local[3][1];
            bone.transforms[8]=b.matrix_local[0][2];
            bone.transforms[9]=b.matrix_local[1][2];
            bone.transforms[10]=b.matrix_local[2][2];
            bone.transforms[11]=b.matrix_local[3][2];
            bone.transforms[12]=b.matrix_local[0][3];
            bone.transforms[13]=b.matrix_local[1][3];
            bone.transforms[14]=b.matrix_local[2][3];
            bone.transforms[15]=b.matrix_local[3][3];
            nodeMesh.model.meshSkin.jointBindPoses[0+i*16]=b.matrix_local[0][0];
            nodeMesh.model.meshSkin.jointBindPoses[1+i*16]=b.matrix_local[1][0];
            nodeMesh.model.meshSkin.jointBindPoses[2+i*16]=b.matrix_local[2][0];
            nodeMesh.model.meshSkin.jointBindPoses[3+i*16]=b.matrix_local[3][0];
            nodeMesh.model.meshSkin.jointBindPoses[4+i*16]=b.matrix_local[0][1];
            nodeMesh.model.meshSkin.jointBindPoses[5+i*16]=b.matrix_local[1][1];
            nodeMesh.model.meshSkin.jointBindPoses[6+i*16]=b.matrix_local[2][1];
            nodeMesh.model.meshSkin.jointBindPoses[7+i*16]=b.matrix_local[3][1];
            nodeMesh.model.meshSkin.jointBindPoses[8+i*16]=b.matrix_local[0][2];
            nodeMesh.model.meshSkin.jointBindPoses[9+i*16]=b.matrix_local[1][2];
            nodeMesh.model.meshSkin.jointBindPoses[10+i*16]=b.matrix_local[2][2];
            nodeMesh.model.meshSkin.jointBindPoses[11+i*16]=b.matrix_local[3][2];
            nodeMesh.model.meshSkin.jointBindPoses[12+i*16]=b.matrix_local[0][3];
            nodeMesh.model.meshSkin.jointBindPoses[13+i*16]=b.matrix_local[1][3];
            nodeMesh.model.meshSkin.jointBindPoses[14+i*16]=b.matrix_local[2][3];
            nodeMesh.model.meshSkin.jointBindPoses[15+i*16]=b.matrix_local[3][3];
            bone.tipoNodo=NodeType.JOINT;
            huesos[bone.reference]=bone;
            i+=1;
            if b.parent is None:
                node.childrens.append(bone);
          #      bone.parent_id=node.reference;
                print(bone.parent_id);
            else:
                huesos[b.parent].childrens.append(bone);

                bone.parent_id=huesos[b.parent].reference;
        return node;


    def procesarMesh(self, bobject):
        print("processing mesh %s"%bobject.name);
        mesh = bobject.to_mesh(bpy.context.scene,True,'PREVIEW');
        meshes_to_clear.append(mesh);
        node= Node();
        node.setTransform(bobject);
        node.model=Model();
        node.model.mesh=Mesh();
        node.reference=bobject.name;
        node.model.mesh.reference=bobject.name+"mesh";
        node.model.mesh.vertices=mesh.vertices;
        node.model.mesh.parts=mesh.polygons;
        self.objetos.append(node);
        if bobject.parent != None and bobject.parent.type == 'ARMATURE':
            node.model.mesh.useVertexWeights = True
            self.procesarArmature(node,bobject);
        if len(mesh.uv_layers)>0:
            node.model.mesh.useUVLayers = True
            node.model.mesh.uvLayers = mesh.uv_layers
        return node;
        
        
    def procesarCamera(self, cam):
        print("processing camera %s"%cam.name);
        bobject=bpy.data.objects[cam.name];
        node= Node();
        node.setTransform(bobject);
        node.camera=Camera();
        node.reference=cam.name;
        node.camera.reference=cam.name+"cam";
        node.camera.cameraType=1;
        node.camera.aspectRatio=1.700000;
        node.camera.nearPlane=cam.clip_start;
        node.camera.farPlane=cam.clip_end;
        node.camera.fieldOfView=math.degrees(cam.angle);
        return node;        
        
    def procesarLamp(self, lamp):
        print("processing lamp %s"%lamp.name);
        bobject=lamp;
        node= Node();
        node.transforms[0]=bobject.matrix_world[0][0];
        node.transforms[1]=bobject.matrix_world[1][0];
        node.transforms[2]=bobject.matrix_world[2][0];
        node.transforms[3]=bobject.matrix_world[3][0];
        node.transforms[4]=bobject.matrix_world[0][1];
        node.transforms[5]=bobject.matrix_world[1][1];
        node.transforms[6]=bobject.matrix_world[2][1];
        node.transforms[7]=bobject.matrix_world[3][1];
        node.transforms[8]=bobject.matrix_world[0][2];
        node.transforms[9]=bobject.matrix_world[1][2];
        node.transforms[10]=bobject.matrix_world[2][2];
        node.transforms[11]=bobject.matrix_world[3][2];
        node.transforms[12]=bobject.matrix_world[0][3];
        node.transforms[13]=bobject.matrix_world[1][3];
        node.transforms[14]=bobject.matrix_world[2][3];
        node.transforms[15]=bobject.matrix_world[3][3];
        node.light=Light();
        node.reference=lamp.name;
        node.light.reference=lamp.name+"light";
        lampdata = lamp.data;
        if lampdata.type == "POINT":
            node.light.lightType = LampType.POINT;
        elif lampdata.type == "SUN":
            node.light.lightType = LampType.DIRECTIONAL;
        elif lampdata.type == "SPOT":
            node.light.lightType = LampType.SPOT;
        else:
            print("ERROR: lamp type not supported");
            return;
        node.light.color[0] = lampdata.color[0];
        node.light.color[2] = lampdata.color[1];
        node.light.color[1] = lampdata.color[2];
        if lampdata.type == "SUN" or lampdata.type == "SPOT":
            node.light.range = lampdata.distance;
        if lampdata.type == "SPOT":
            #spot_size is in radians!
            node.light.innerAngle = lampdata.spot_size;    
            node.light.outerAngle = lampdata.spot_size;
        self.objetos.append(node);
        return node;
    
    def procesarEmpty(self, empty):
        print("processing empty %s"%empty.name);
        node= Node();
        node.setTransform(empty);
        node.reference = empty.name
        self.objetos.append(node);
        return node;
        
    def execute(self, context):
        global meshes_to_clear;
        meshes_to_clear=[];
        bpy.ops.object.mode_set(mode='OBJECT');
        # Set the default return state to FINISHED
        result = {'FINISHED'};
        # Check that the currently selected object contains mesh data for exporting
        numemptys = 0
        self.objetos=[];
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                self.procesarMesh(ob);
            elif ob.type == 'LAMP':
                self.procesarLamp(ob);
            elif ob.type == 'EMPTY':
                self.procesarEmpty(ob);
                numemptys = numemptys+1
        # Create a file header object with data stored in the body section   
        # Open the file for writing
        camera = self.procesarCamera(bpy.data.cameras[bpy.context.scene.camera.name]);
        self.objetos.append(camera);
        file = open(self.filepath, 'bw');
        file.write(b'\xABGPB\xBB\r\n\x1A\n');
        file.write(struct.pack("B",1));
        file.write(struct.pack("B",2));
        #+1 for scene reference , *2 for node+mesh reference and node+camera reference .. 
        # empties have not data associated
        numreferences = len(self.objetos)*2+1-numemptys;
        file.write(struct.pack("<I",numreferences));
        scene=Reference();
        scene.tipo=ReferenceType.SCENE;
        scene.reference="__SCENE__";
        scene.writeReference(file);
        for o in  self.objetos:
            o.writeReference(file);
        scene.offset=file.tell();
        file.write(struct.pack("<I",len(self.objetos)));
        for o in  self.objetos:
            o.writeNode(file);       
        #write data of scene
        file.write(struct.pack("<I",len(camera.reference)+1));#camara xref
        file.write(bytearray('#',"ascii"));
        if len(camera.reference)>0:
            file.write(bytearray(camera.reference,"ascii"));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        file.write(struct.pack("<f",1.0));
        for o in  self.objetos:
            o.writeExtra(file);
        for o in  self.objetos:
            o.updateOffset(file);
        scene.updateOffset(file);
        file.close();
        for m in meshes_to_clear:
            bpy.data.meshes.remove(m);
        return result;


# uncomment this block to use the exporter without register in blender ui (using ALT+P)
print("ejecutando exportador:");
print(bpy.data.objects);
_exporter = Exporter();
_exporter.filepath = "/home/cesar/gameplay/gpbexporter/res/cone.gpb";
_exporter.execute(None);
print("archivo ejecutado con exito!");


