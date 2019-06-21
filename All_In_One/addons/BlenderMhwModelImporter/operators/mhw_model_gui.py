import mathutils 
import base64
import zlib 
import bmesh
import os
import math

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from bpy.types import Operator
from mathutils import Vector, Matrix
from ..config import writeConfig,  setInstallPath, setChunkPath
from ..vertexbuffers import mhw as mod3
from ..dbg import dbg
from ..common import fileOperations as fileOp
from ..common import constants as cons
from . import mhw_model as Mod
from ..config import initConfig

(config,CHUNK_PATH,PATH) = initConfig()

def CollectTris(fl,bendiannes,num,modf=1):
    dbg("CollectBETris %d" % num)
    res = []
    readOp = fileOp.ReadBEShort if bendiannes else fileOp.ReadShort
    for i in range(0 ,num):
        res.append([x+modf for x in [readOp(fl) , readOp(fl) ,readOp(fl)]])
    return res

def reserveVerticesAndFaces(export,headerref,parts,p,newVertexCount,newFaceCount):
    p.modifyVertexCount(parts,newVertexCount)
    p.modifyFaceCount(parts,newFaceCount)

def isClone(name):
    if(len(name) > len(cons.CLONE_SUFFIX)):
        dbg("isClone %s" % name[len(name)-len(cons.CLONE_SUFFIX):])
        return (name[len(name)-len(cons.CLONE_SUFFIX):] == cons.CLONE_SUFFIX)
    else:
        return False

def getCloneParent(name):
    cloneFMT = cons.CLONE_SUFFIX_FMT % 0
    if(len(name) > len(cloneFMT)):
        cloneParent = name[:len(name)-len(cloneFMT)-1]
        dbg("Clone parent of %s is %s" % (name,cloneParent))
        return cloneParent
    else:
        return ""

def checkForMeshClones(export,i,cloneMappings):
    for o in bpy.data.objects:
        name = o.name
        fl,parts = (i.fl,i.parts)
        if isClone(name):
            cloneParent = getCloneParent(name)
            dbg("clone %s detected" % name)
            for p in parts:
                if p.getName() == cloneParent:
                    newPart = p.createEmptyClone(parts)
                    cloneMappings[newPart.getName()] = name
                    parts.append(newPart)
                    export.modifyMeshCount(fl,i.headerref.MeshCount+1)
                    export.modifyVertexOffset(fl,i.headerref.VertexOffset + cons.MESH_PART_SIZE)
                    i.headerref.VertexOffset += cons.MESH_PART_SIZE
                    export.modifyFaceOffset(fl,i.headerref.FaceOffset + cons.MESH_PART_SIZE)
                    i.headerref.FaceOffset += cons.MESH_PART_SIZE
                    if(i.headerref.UnkOffset != 0):
                        export.modifyUnknOffset(fl,i.headerref.UnkOffset + cons.MESH_PART_SIZE)
                        i.headerref.UnkOffset += cons.MESH_PART_SIZE
                    break
    dbg("reloading by stream")
    #Reload everything
    fileOp.Seek(i.fl,0)
    i.init_main()
    i.readHeader()
    i.materials = i.readMaterials()
    i.readMeshParts()
    
def identifyDifference(export,parts, cloneMappings):
    for p in parts:
        headerref = p.headerref
        n = p.getName()
        if not n in bpy.data.objects and n in cloneMappings:
                dbg("%s is a clone" % n)
                n = cloneMappings[n]
                dbg("using clone name %s" % n)
                p.setName(n)
        if not n in bpy.data.objects:
            dbg("Mesh %s not found!" % n)
            continue
        obj = bpy.data.objects[n]
        bm = obj.data
        if not 'id' in bm.vertex_layers_int:
            my_id = bm.vertex_layers_int.new('id')
        else:
            my_id = bm.vertex_layers_int['id']
            vids = []
            duplicateVids = False
            for v in my_id.data:
                if v != None:
                    if v.value in vids:
                        duplicateVids = True
                        break
                    vids.append(v.value)
            if duplicateVids:
                for j, v in enumerate(my_id.data):
                    v.value = j
                dbg("Mesh %s had duplicate id's in vertex layer, rebuilding")
        dbg("Mesh %s has file vertice-count: %d and current vertice-count: %d" % (n,p.VertexCount,len(bm.vertices)))
        
        faceCount = 0
        for po in bm.polygons:
            faceCount += len(po.vertices)-2
        
        if((p.VertexCount != len(bm.vertices))or(p.FaceCount != faceCount)):
            dbg("need to modify structure because mesh %s has modified verticeCount" % n)
            reserveVerticesAndFaces(export,headerref,parts,p,len(bm.vertices),faceCount)
            return True
    return False

def updateDifferences(export, i, fl, cloneMappings, oldVertexRegionEnd, oldTotalFaceCount):
    orgFaceOffset = i.headerref.FaceOffset
    newVertexRegionEnd = 0
    newTotalFaceCount = 0
    newTotalVertexCount = 0
    newTotalFaceCount = 0
    newVertexBufferSize = 0
    for p2 in i.parts:
        newTotalVertexCount += p2.VertexCount
        newTotalFaceCount += p2.FaceCount
        newVertexBufferSize += p2.calcVertexBufferSize()
        newVertexRegionEnd = max(newVertexRegionEnd,p2.getVertexRegionEnd())
    VertexSizeDiff = newVertexRegionEnd-oldVertexRegionEnd
    FacesSizeDiff = (newTotalFaceCount-oldTotalFaceCount)*2
    export.modifyVertexCount(fl,newTotalVertexCount)
    export.modifyFaceOffset(fl,orgFaceOffset+VertexSizeDiff)
    export.modifyFaceCount(fl,newTotalFaceCount)
    export.modifyVertexBufferSize(fl,newVertexBufferSize)
    if(i.headerref.UnkOffset != 0):
        export.modifyUnknOffset(fl,i.headerref.UnkOffset + VertexSizeDiff + FacesSizeDiff)
    dbg("reloading by stream")
    #Reload everything
    fileOp.Seek(i.fl,0)
    i.init_main()
    i.readHeader()
    i.materials = i.readMaterials()
    i.readMeshParts()
    for p in i.parts:
        n = p.getName()
        if not n in bpy.data.objects:
            if n in cloneMappings:
                dbg("%s is a clone" % n)
                n = cloneMappings[n]
                dbg("using clone name %s" % n)
                p.setName(n)
  
def checkMeshesForModifications(export,i,cloneMappings):
    fl,parts = (i.fl,i.parts)
    modified = False
    oldVertexRegionEnd = max((p.getVertexRegionEnd() for p in parts))
    oldTotalFaceCount = sum((p.FaceCount for p in parts))
    dbg("checkMeshesForModifications found %d parts" % len(parts))
    modified = identifyDifference(export, parts, cloneMappings)
    if modified:
        updateDifferences(export, i, fl, cloneMappings, oldVertexRegionEnd, oldTotalFaceCount)


class ExportMOD3(Operator, ImportHelper):
    bl_idname = "custom_import.export_mhw"
    bl_label = "Export MHW MOD file (.mod3)"
    bl_options = {'PRESET'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".mod3"
 
    filter_glob = StringProperty(default="*.mod3", options={'HIDDEN'}, maxlen=255)
    
    do_write_bones = BoolProperty(
            name="Export bones and armature (experimental)",
            description="Exports bone information.",
            default=False)
    overwrite_lod = BoolProperty(name="Force LOD1",
                description="overwrite the level of detail of the other meshes (for example if you used 'Only import high LOD-parts').",
                default=True)
    export_normals = BoolProperty(name="Export normals (experimental)",
                description="Exports normals for every vertice.",
                default=True)
    apply_trans_rot = BoolProperty(name="Apply rotation/transformation changes",
                description="Automatically apply rotation/transformation of mesh to vertices (ctrl+a).",
                default=True)
    def execute(self, context):
        if not 'data' in bpy.data.texts:
            raise Exception("Make shure to import with \"Reference/Embed original data.\" first.")
        scene = bpy.context.scene
        bpy.ops.object.mode_set(mode='OBJECT')
        if self.apply_trans_rot:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type == 'MESH':
                scene.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')
                if len(obj.data.vertices)>0:
                    obj.data.calc_tangents()
        dataText = bpy.data.texts['data'].lines[0].body
        if dataText[0:5]=="path:":
            path = dataText[5:]
            dbg("path:%s" % path)
            with open(path, 'rb') as content_file:
                content = content_file.read()
                fl = fileOp.createContentStream(content)
        else:
            data = base64.b64decode(dataText)
            content = zlib.decompress(data)
            fl = fileOp.createContentStream(content)
        i = ImportMOD3(self)
        i.init_main()
        i.fl = fl
        fileOp.Seek(i.fl,0)
        i.readHeader()
        i.materials = i.readMaterials()
        i.readMeshParts()
        
        cloneMappings = {}
        
        checkForMeshClones(self,i,cloneMappings)
        checkMeshesForModifications(self,i,cloneMappings)
        
        for p in i.parts:
            p.writeVertexes(i.fl,self.do_write_bones,self.export_normals)
            p.writeCustomProperties(i.fl)
        
        if self.overwrite_lod:
            for p in i.parts:
                if (p.LOD == 1) or (p.LOD == 0xFFFF):
                    p.writeLOD(i.fl,0xFFFF)
                else:
                    p.writeLOD(i.fl,0)

        if self.do_write_bones:
            if cons.MAIN_ARMATURE in bpy.data.objects:
                self.writeBones(i,i.fl,cons.MAIN_ARMATURE)
            if cons.AMATRICES_ARMATURE in bpy.data.objects:
                self.writeBones(i,i.fl,cons.AMATRICES_ARMATURE)
        content = fileOp.getContentStreamValue(fl)
        with open(self.filepath, 'wb') as content_file:
            content_file.write(content)
        return {'FINISHED'}
    
    def modifyFaceOffset(self,fl,newFaceOffset):
        dbg("modifyFaceOffset %08x [%08x]" % (newFaceOffset,0x58))
        fileOp.Seek(fl,0x58)
        fileOp.WriteLongs(fl,[newFaceOffset])
    def modifyVertexOffset(self,fl,newVertexOffset):
        dbg("modifyVertexOffset %08x [%08x]" % (newVertexOffset,0x50))
        fileOp.Seek(fl,0x50)
        fileOp.WriteLongs(fl,[newVertexOffset])

    def modifyVertexCount(self,fl,totalVertexCount):
        dbg("modifyVertexCount %d [%08x]" % (totalVertexCount,0x0c))
        fileOp.Seek(fl,0x0c)
        fileOp.WriteLongs(fl,[totalVertexCount])

    def modifyVertexBufferSize(self,fl,vertexBufferSize):
        dbg("modifyVertexBufferSize %d [%08x]" % (vertexBufferSize,0x18))
        fileOp.Seek(fl,0x18)
        fileOp.WriteLongs(fl,[vertexBufferSize])
    def modifyMeshCount(self,fl,totalMeshCount):
        dbg("modifyMeshCount %08x [%08x]" % (totalMeshCount,0x10))
        fileOp.Seek(fl,0x08)
        fileOp.WriteShorts(fl,[totalMeshCount])
    def modifyFaceCount(self,fl,totalFaceCount):
        dbg("modifyFaceCount %08x [%08x]" % (totalFaceCount,0x10))
        fileOp.Seek(fl,0x10)
        fileOp.WriteLongs(fl,[totalFaceCount])
    def modifyUnknOffset(self,fl,unknOffset):
        dbg("modifyUnknOffset %08x [%08x]" % (unknOffset,0x60))
        fileOp.Seek(fl,0x60)
        fileOp.WriteLongs(fl,[unknOffset])

    def writeBones(self,headerref,fl,ArmatureName):
        dbg("writeBones %s" % ArmatureName)
        old_type = bpy.context.area.type
        try:
            bpy.context.area.type = 'VIEW_3D'
            bpy.ops.view3d.snap_cursor_to_center()
            scene = bpy.context.scene
            scene.objects.active = bpy.data.objects[ArmatureName]
            #bpy.ops.armature.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='EDIT')
            armature = bpy.data.objects[ArmatureName].data
            if (cons.FMT_BONE % 255) in armature.edit_bones:
                fileOp.Seek(fl,headerref.BonesOffset)
                
                if ArmatureName == cons.AMATRICES_ARMATURE:
                    fileOp.fseek(fl,headerref.BoneCount*24)
                else:
                    for i in range(0,headerref.BoneCount):
                        fileOp.fseek(fl,2) # skip unkn1
                        bone = armature.edit_bones[cons.FMT_BONE % i]
                        pb = bone.parent
                        parentId = 255
                        if(not (pb is None)):
                            pbName = pb.name
                            dbg("pbName: %s" % pb.name)
                            parentId = int(pbName[len(cons.FMT_BONE)-3:])
                            dbg("parentId: %d" % parentId)
                        dbg("write parentId,i %s at offset %08x" % ([parentId,i],fileOp.getPos(fl)))
                        fileOp.WriteBytes(fl,[parentId])
                        fileOp.fseek(fl,1) # skip child for now (does not seem to be an unique number)
                        fileOp.fseek(fl,4) # skip unkn2
                        
                        length = bone.length
                        if(bone.length <= cons.MIN_BONE_LENGTH):
                            dbg("zero length bone detected")
                            length = 0
                            t2 = mathutils.Matrix.Translation(Vector((0,0,0)))
                        else:
                            t2 = mathutils.Matrix.Translation(bone.tail)*mathutils.Matrix.Translation(bone.head).inverted()
                        t2t = t2.to_translation()
                        fileOp.WriteFloats(fl,[length,t2t.x,t2t.y,t2t.z])

                if ArmatureName == cons.AMATRICES_ARMATURE:
                    fileOp.fseek(fl,headerref.BoneCount*64)
                #store "lmatrices"
                for i in range(0,headerref.BoneCount):
                    bone = armature.edit_bones[cons.FMT_BONE % i]
                    if(bone.length <= cons.MIN_BONE_LENGTH):
                        dbg("zero length bone detected")
                        t2 = mathutils.Matrix.Translation(Vector((0,0,0)))
                    else:
                        t2 = mathutils.Matrix.Translation(bone.tail)*mathutils.Matrix.Translation(bone.head).inverted()
                    #t2 = bone.matrix*bone.parent.matrix.inverted()
                    #dbg("%s %s %s" % (bone.matrix,bone.parent.matrix,t2))
                    #t2 *= Matrix.Translation(Vector((0,0,-1,1)))
                    #t2 *= Matrix.Rotation(90*math.pi/2,4,Vector((0,0,1)))
                    dbg("write bone %d at offset %08x:\n%s" % (i,fileOp.getPos(fl),t2))
                    for r in t2.transposed().row:
                        dbg(r)
                        fileOp.WriteFloats(fl,(r[0],r[1],r[2],r[3]))
            bpy.ops.object.mode_set(mode='OBJECT')
        finally:
            bpy.context.area.type = old_type
        #bpy.ops.armature.select_all(action='DESELECT')


def chunk_path_update(self,context):
    dbg("chunk_path: %s" % (ImportMOD3.chunk_path,))
    ImportMOD3.chunk_path[1]["default"] = self.chunk_path
def install_path_update(self,context):
    dbg("install_path: %s" % (ImportMOD3.install_path,))
    ImportMOD3.install_path[1]["default"] = self.install_path
def use_layers_changed(self,context):
    dbg("use_layers: '%s'" % (self.use_layers))
    if self.use_layers == cons.LAYER_MODE_LOD:
        self.only_import_lod_1 = False
def only_import_lod_changed(self,context):
    if (self.only_import_lod != -1) and self.only_import_lod_1:
        self.only_import_lod_1 = False
def only_import_lod_1_changed(self,context):
    if self.only_import_lod_1 and (self.only_import_lod != -1):
        self.only_import_lod = -1
def read_amatrices_changed(self,context):
    if self.read_amatrices and not self.do_read_bones:
        self.do_read_bones = True
def do_read_bones(self,context):
    if self.read_amatrices and not self.do_read_bones:
        self.read_amatrices = False

#TODO: seperate header-info from import class
class ImportMOD3(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhw"
    bl_label = "Load MHW MOD file (.mod3)"
    bl_options = {'PRESET'}
 
    # ImportHelper mixin class uses this
    filename_ext = ".mod3"
 
    filter_glob = StringProperty(default="*.mod3", options={'HIDDEN'}, maxlen=255)
    
    
    clear_scene_before_import = BoolProperty(
            name = "Clear scene before import.",
            description = "Recommended, exporting multiple mod3-files is not supported.",
            default = True)
    chunk_path = StringProperty(
            name = "Chunk path",
            description = "Path to chunk folder (containing template.mrl3 for example)",
            default = CHUNK_PATH,
            update = chunk_path_update,
    )
    install_path = StringProperty(
            name = "Install path",
            description = "Path the contains the Scarlet directory.",
            default = PATH,
            update = install_path_update,
    )
    use_layers = EnumProperty(
            name = "Layer mode",
            description = "Chose what mesh should be put to what layer.",
            items = [cons.ENUM_LAYER_MODE_NONE,cons.ENUM_LAYER_MODE_PARTS,cons.ENUM_LAYER_MODE_LOD],
            default = cons.LAYER_MODE_PARTS,
            update = use_layers_changed,
    )
    import_textures = BoolProperty(
            name = "Import textures.",
            description = "Looks automatically for the *.mrl3 file and imports the *.tex files.",
            default = False,
    )
    only_import_lod_1 = BoolProperty(
            name = "Only import high LOD-parts.",
            description = "Skip meshparts with low level of detail.",
            default = True,
            update = only_import_lod_1_changed,
    )
    only_import_lod = IntProperty(
            name = "Only import LOD parts with level:",
            description = "If not -1 it imports only parts with a defined level of detail.",
            default = -1,
            update = only_import_lod_changed,
    )
    embed_mode = EnumProperty(
            name = "Embed mode",
            description = "Used for beeing able to export the object.",
            items = [cons.ENUM_EMBED_MODE_NONE,cons.ENUM_EMBED_MODE_REFERENCE,cons.ENUM_EMBED_MODE_DATA],
            default = cons.EMBED_MODE_REFERENCE
    )
    do_read_bones = BoolProperty(
            name = "Import bones and armature.",
            description = "Imports bones ... useful for testing poses.",
            default = True,
            update = do_read_bones
    )
    read_amatrices = BoolProperty(
            name = "Import amatrices.",
            description = "It's another bone structure.\nCurrently don't know what this is for.",
            default = False,
            update = read_amatrices_changed
    )

    def init_main(self):
        self.headerref = self
        self.parts = []

    
    def readHeader(self):
        dbg("readHeader")
        fl = self.fl
        self.bendian = False
        self.ID = fileOp.ReadLong(fl);
        if self.ID != 0x444f4d:
            raise Exception("Invalid Header")
        self.Version = fileOp.ReadByte(fl)
        self.Version2 = fileOp.ReadByte(fl) 
        self.BoneCount = fileOp.ReadShort(fl)
        self.MeshCount = fileOp.ReadShort(fl)
        self.MaterialCount = fileOp.ReadShort(fl)
        self.VertexCount = fileOp.ReadLong(fl)
        self.FaceCount = fileOp.ReadLong(fl)
        self.VertexIds = fileOp.ReadLong(fl)
        self.VertexBufferSize = fileOp.ReadLong(fl)
        self.SecondBufferSize = fileOp.ReadLong(fl)
        if self.Version < 190:
            self.TextureCount = fileOp.ReadLong(fl)
        self.GroupCount = fileOp.ReadPointer(fl,cons.x64)
        if self.Version < 190 or self.Version > 220: 
            self.BoneMapCount = fileOp.ReadPointer(fl,cons.x64)
        self.BonesOffset = fileOp.ReadPointer(fl,cons.x64)
        self.GroupOffset = fileOp.ReadPointer(fl,cons.x64)
        self.MaterialNamesOffset =fileOp. ReadPointer(fl,cons.x64)
        self.MeshOffset = fileOp.ReadPointer(fl,cons.x64)
        self.VertexOffset =fileOp.ReadPointer(fl,cons.x64)
        if self.Version < 190:
            self.Vertex2Offset = fileOp.ReadLong(fl)
        self.FaceOffset = fileOp.ReadPointer(fl,cons.x64)
        self.UnkOffset = fileOp.ReadPointer(fl,cons.x64)
        if self.Version < 190:
            self.unkOffset2 = fileOp.ReadLong(fl)
            self.bbsphereposition = fileOp.ReadVector3(fl)
            self.bbsphereradius = fileOp.ReadFloat(fl)
            self.bbmin = fileOp.ReadVector3(fl)
            fileOp.ReadLong(fl)
            self.bbmax = fileOp.ReadVector3(fl)
            fileOp.ReadLong(fl)
            for s  in range(1,4+1):
                self.vtbuffscale[s] = self.bbmax[s]-self.bbmin[s]

        if self.Version == 237:
            self.BoneMapCount = None
        dbg("pos:%d FaceOffset: %08x" % (fileOp.pos[fl],self.FaceOffset))
        
    
    
    def addArmature(self,name):
        bpy.ops.object.armature_add()
        ob = bpy.context.scene.objects.active
        ob.name = name
        ob.show_x_ray = True
        arm = ob.data
        arm.name = name
        return arm
    
    def addChildBones(self,a,parentBone,id,bones):
        dbg("addChildBones %d" % id)
        i = 0
        for b in bones:
            if ((id == b.parentid)and(b.id != id)):
                dbg("addChildBone %d with parent %d" % (b.id,id))
                bone2 = a.edit_bones.new(cons.FMT_BONE % b.id)
                bone2.parent = parentBone
                lm = self.lmatrices[b.id]
                c1 = lm.col1
                c2 = lm.col2
                c3 = lm.col3
                c4 = lm.col4
                t = Matrix((
                          (c1[0],c2[0],c3[0],c4[0]),
                          (c1[1],c2[1],c3[1],c4[1]),
                          (c1[2],c2[2],c3[2],c4[2]),
                          (c1[3],c2[3],c3[3],c4[3])
                          ))
                loc,rot,scal = t.decompose()
                bone2.head = parentBone.tail
                loc.rotate(rot)
                if loc.length <= cons.MIN_BONE_LENGTH:
                    dbg("Bone length cannot be 0, adjusting")
                    loc = Vector((0.0,0.0,cons.MIN_BONE_LENGTH))

                bone2.tail = bone2.head+loc
                #bone2.tail = bone2.head+Vector((0.0,0.0,1.0))
                #bone2.tail = bone2.head
                dbg("#1 bone: %d length:%f l: %s r: %s s: %s,t:\n%s" % (b.id,loc.length,loc,rot,scal,t))
                #bone2.transform(t)
                
                #t2 = bone2.matrix*bone2.parent.matrix.inverted()
                #t2 *= Matrix.Translation(Vector((0,0,-1,1)))
                ##t2 *= Matrix.Rotation(90*math.pi/2,4,Vector((0,0,1)))
                #loc,rot,scal = t2.decompose()
                #dbg("#2 bone: %d l: %s r: %s s: %s,t2:\n%s" % (b.id,loc,rot,scal,t2))

                self.addChildBones(a,bone2,b.id,bones)
                i += 1
    
    def readBones(self):
        headerref = self.headerref
        fl = self.fl
        fileOp.Seek(fl,self.BonesOffset)
        _MODBoneInfo = None
        if headerref.Version == 237:
            _MODBoneInfo = Mod.MODBoneInfo2
        else:
            raise Exception("not implemented!")
        self.bones = []
        self.lmatrices = []
        self.amatrices = []
        self.remaptable = []
        self.remaptablesize = 512 if headerref.Version == 137 else 256
        for b in range(0,headerref.BoneCount):
            self.bones.append(_MODBoneInfo(b,headerref.fl,headerref.bendian))
        for b in range(0,headerref.BoneCount):
            self.lmatrices.append(Mod.readmatrix44(headerref))
        for b in range(0,headerref.BoneCount):
            self.amatrices.append(Mod.readmatrix44(headerref))
        for b in range(0,self.remaptablesize):
            self.remaptable.append(fileOp.ReadByte(headerref.fl))
        if headerref.BoneMapCount != None:
            raise Exception("not implemented")

    def createBones(self,armatureName,matrices):
        a = self.addArmature(armatureName)
        a.draw_type = 'STICK'
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        a.edit_bones[0].select_tail = True
        dbg("bones: %d" % len(self.bones))
        i = 0
        k = 0
        parentBone = a.edit_bones[-1]
        parentBone.transform(Matrix(((1,0,0),(0,0,1),(0,-1,0))))
        parentBone.name = cons.FMT_BONE % 255
        parentBone.length = cons.MIN_BONE_LENGTH

        for b in self.bones:
            dbg("bone: %d has parent %d" % (b.id,b.parentid))
            if (b.parentid == b.id)or(b.parentid == 255):
                bone = a.edit_bones.new(cons.FMT_BONE % b.id)

                lm = matrices[i]
                c1 = lm.col1
                c2 = lm.col2
                c3 = lm.col3
                c4 = lm.col4
                t = Matrix((
                          (c1[0],c2[0],c3[0],c4[0]),
                          (c1[1],c2[1],c3[1],c4[1]),
                          (c1[2],c2[2],c3[2],c4[2]),
                          (c1[3],c2[3],c3[3],c4[3])
                          ))
                #loc,rot,scal = t.decompose()
                bone.parent = parentBone
                #bone.head = parentBone.tail+Vector(loc)
                #bone.tail = bone.head+Vector((0.0,0.0,1.0))

                _,rot,scal = t.decompose()
                loc = Vector((b.x,b.y,b.z))
                
                if loc.length <= cons.MIN_BONE_LENGTH:
                    dbg("Bone length cannot be 0, adjusting")
                    loc = Vector((0.0,0.0,cons.MIN_BONE_LENGTH))
                dbg("##1 bone: %d length: %f l: %s r: %s s: %s,t:\n%s" % (b.id,loc.length,loc,rot,scal,t))

                bone.head = parentBone.tail
                loc.rotate(rot)
                bone.tail = bone.head+loc
                if(b.length <= cons.MIN_BONE_LENGTH):
                    bone.length = cons.MIN_BONE_LENGTH
                else:
                    bone.length = b.length
                #bone.tail = bone.head+Vector((0.0,0.0,1.0))
                #bone.tail = bone.head
                #bone.transform(t)

                #t2 = bone.matrix*bone.parent.matrix.inverted()
                #t2 *= Matrix.Translation(Vector((0,0,-1,1)))
                ##t2 *= Matrix.Rotation(90*math.pi/2,4,Vector((0,0,1)))
                #loc,rot,scal = t2.decompose()
                #dbg("#2 bone: %d l: %s r: %s s: %s,t2:\n%s" % (b.id,loc,rot,scal,t2))
                k += 1


                self.addChildBones(a,bone,b.id,self.bones)
            i += 1
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for o in bpy.data.objects:
            if o.type == "MESH":
                bpy.context.scene.objects.active = o
                bpy.ops.object.modifier_add(type='ARMATURE')
                bpy.context.object.modifiers[-1].object = bpy.data.objects[armatureName]
    
    def writeFaces(self,meshPart,fl,faces):
        headerref = meshPart.headerref
        dbg("writeFaces % 08x" % (headerref.FaceOffset+meshPart.FaceOffset*2))
        fileOp.Seek(fl,headerref.FaceOffset+meshPart.FaceOffset*2)
        fileOp.WriteShorts(fl,faces)
    def writemeshdatav1(self,meshPart,fl,vertices,uvs,faces,weights,bones,normals,tangents):
        raise Exception("NotImplementedError")
    def writemeshdatav2(self,meshPart,fl,vertices,uvs,faces,weights,bones,normals,tangents):
        raise Exception("NotImplementedError")
    def writemeshdatav3(self,meshPart,fl,vertices,uvs,faces,weights,bones,normals,tangents):
        headerref = meshPart.headerref
        BOFF=meshPart.VertexSub+meshPart.VertexBase
        dbg("meshPart.VertexOffset %08x" % (headerref.VertexOffset+meshPart.VertexOffset+meshPart.BlockSize*BOFF))
        fileOp.Seek(fl, (headerref.VertexOffset+meshPart.VertexOffset+meshPart.BlockSize*BOFF))
        dbg("writemeshdatav3 %s meshPart.VertexCount: %d , vertices: %d weights: %d bones: %d" % (meshPart.getName(),meshPart.VertexCount,len(vertices),len(weights),len(bones)))
        
        if meshPart.VertexCount != len(vertices):
            raise Exception("different vertices counts are not (yet) permitted!")
            
        uvi = 0
        vi = 0
        for vi, v3 in enumerate(vertices):
            if(len(v3) != 3):
                raise Exception("verticesCount != 3")
            vStartPos = fileOp.getPos(fl)
            #dbg("vStartPos: %08x" % vStartPos)
            fileOp.WriteFloats(fl,v3)
            if (len(normals)>0) and (len(tangents)>0):
                if vi not in normals:
                    bpy.context.scene.cursor_location = (vertices[vi].x, vertices[vi].y, vertices[vi].z)
                    raise ValueError("No normals for %s %s: %f, %f, %f" % (meshPart.id, meshPart.uid, vertices[vi].x, vertices[vi].y, vertices[vi].z))
                nvec = normals[vi]
                dbg("normals for %d: %s" % (vi,nvec))
                floats = []
                floats.append(nvec.x)
                floats.append(nvec.y)
                floats.append(nvec.z)
                #dbg("normals as bytes for %d: %s" % (vi,bytes))
                fileOp.Write8s(fl,floats)
                fileOp.Write8s(fl,[0.0])
                floats = []
                if vi in tangents:
                    (tvec,tsign) = tangents[vi]
                    floats.append(tvec.x)
                    floats.append(tvec.y)
                    floats.append(tvec.z)
                    floats.append(tsign)
                else:
                    floats.append(0)
                    floats.append(0)
                    floats.append(0)
                    floats.append(0)
                #dbg("normals as bytes for %d: %s" % (vi,bytes))
                fileOp.Write8s(fl,floats)
            else:
                fileOp.fseek(fl,8)
            vertexBuffer = mod3.MODVertexBufferSelector(meshPart.BlockType)
            structSize = vertexBuffer.getStructSize()
            uvOFF = vertexBuffer.getUVOFFAfterTangents()
            fileOp.fseek(fl,uvOFF)
            if len(uvs)>0:
                if not (uvi in uvs):
                    dbg("uv: %s" % uvs)
                    dbg("uvi: %s" % uvi)
                    k = 0
                    mk = 0
                    for k,v in uvs.items():
                        mk = max(mk,k)
                    dbg("max k in uv: %d" % mk)
                    fileOp.fseek(fl,4)
                else:
                    fileOp.WriteHalfFloats(fl,[uvs[uvi].x,1-uvs[uvi].y])
                uvi += 1
            else:
                fileOp.fseek(fl,4)
            weightsOff = vertexBuffer.getWeightsOFFAfterUVOFF()
            bonesOff  = vertexBuffer.getBonesOFFAfterWeightsOFF()
            if (weightsOff != -1) and (bonesOff != -1) and (vi in weights) and (vi in bones):
                fileOp.fseek(fl,weightsOff)
                if(vertexBuffer.getBoneMode() == cons.WEIGHTS3_BONES4):
                    w1 = 0
                    w2 = 0
                    w3 = 0
                    lw = len(weights[vi])
                    if lw > 0:
                        w1 = weights[vi][0]
                    if lw > 1:
                        w2 = weights[vi][1]
                    if lw > 2:
                        w3 = weights[vi][2]
                    if lw > 3:
                        w4 = weights[vi][3]
                    try:
                        w1 = min(int(round(w1 / cons.WEIGHT_MULTIPLIER)), 1023)
                    except ValueError as e:
                        dbg("w1: %f weights: %s" % (w1,weights[vi]))
                        raise e
                    w2 = min(int(round(w2 / cons.WEIGHT_MULTIPLIER)), 1023) << 10
                    w3 = min(int(round(w3 / cons.WEIGHT_MULTIPLIER)), 1023) << 20
                    weightVal = w1 + w2 + w3
                    fileOp.WriteLongs(fl,[weightVal])
                    fileOp.fseek(fl,bonesOff)
                    
                    boneList = bones[vi]
                    while len(bones[vi]) < 4:
                        boneList.append(0)
                    fileOp.WriteBytes(fl,boneList[0:4])
                elif(vertexBuffer.getBoneMode() == cons.WEIGHTS7_BONES8):
                    w1 = 0
                    w2 = 0
                    w3 = 0

                    w4 = 0
                    w5 = 0
                    w6 = 0
                    w7 = 0


                    lw = len(weights[vi])
                    if lw > 0:
                        w1 = weights[vi][0]
                    if lw > 1:
                        w2 = weights[vi][1]
                    if lw > 2:
                        w3 = weights[vi][2]

                    if lw > 3:
                        w4 = weights[vi][3]
                    if lw > 4:
                        w5 = weights[vi][4]
                    if lw > 5:
                        w6 = weights[vi][5]
                    if lw > 6:
                        w7 = weights[vi][6]
                    try:
                        w1 = min(int(round(w1 / cons.WEIGHT_MULTIPLIER)), 1023)
                    except ValueError as e:
                        dbg("w1: %f weights: %s" % (w1,weights[vi]))
                        raise e
                    w2 = min(int(round(w2 / cons.WEIGHT_MULTIPLIER)), 1023) << 10
                    w3 = min(int(round(w3 / cons.WEIGHT_MULTIPLIER)), 1023) << 20
                    w4 = min(int(round(w4 / cons.WEIGHT_MULTIPLIER2)), 0xFF)
                    w5 = min(int(round(w5 / cons.WEIGHT_MULTIPLIER2)) , 0xFF)
                    w6 = min(int(round(w6 / cons.WEIGHT_MULTIPLIER2)) , 0xFF)
                    w7 = min(int(round(w7 / cons.WEIGHT_MULTIPLIER2)) , 0xFF)
                    weightVal = w1 + w2 + w3
                    #dbg("Write weights for vertex %08x : %s" % (fileOp.getPos(fl),[w1,w2,w3,w4,w5,w6,w7]))
                    fileOp.WriteLongs(fl,[weightVal])
                    fileOp.WriteBytes(fl,[w4,w5,w6,w7])
                    
                    fileOp.fseek(fl,bonesOff)
                    boneList = bones[vi]
                    while len(bones[vi]) < 8:
                        boneList.append(0)
                    #dbg("Write bone for vertex %08x : %s" % (fileOp.getPos(fl),boneList[0:8]))
                    try:
                        fileOp.WriteBytes(fl,boneList[0:8])
                    except:
                        raise Exception(str(boneList[0:8]))
                else:
                    dbg("wrong bone mode")
                    weightsOff = 0
                    bonesOff = 0
            else:
                dbg("#%d no bones to write %08x %08x" % (vi,weightsOff,bonesOff))
                weightsOff = 0
                bonesOff = 0
                
                
                
            #dbg("Next start pos: %08x (structSize: %d)" % (vStartPos+structSize,structSize))
            fileOp.Seek(fl,vStartPos+structSize) 
        self.writeFaces(meshPart,fl,faces)
        """
    def loadmeshdatav1(self,meshPart):
        f = mod3.MODVertexBufferSelector(meshPart.BlockType)
        headerref = meshPart.headerref
        if f != None:
            fileOp.Seek(headerref.fl,((headerref.VertexOffset+meshPart.VertexOffset)+(BlockSize*(meshPart.VertexSub+meshPart.VertexBase))))
            meshPart.meshdata = f(headerref,meshPart.VertexCount)
            fileOp.Seek(headerref.fl,(headerref.FaceOffset+FaceOffset*2))
            if headerref.bendian:
                meshPart.meshdata.facearray = CollectBEStrips(headerref.fl,meshPart.FaceCount,(0-meshPart.VertexSub))
            else:
                meshPart.meshdata.facearray = CollectStrips(headerref.fl,meshPart.FaceCount,(0-meshPart.VertexSub))
        else:
            raise Exception("Unknown block hash [%08x] for MTF v1 model format.\n" % meshPart.BlockType)
    def loadmeshdatav1(self):
        raise Exception("NotImplementedError")
        """

    def loadmeshdatav3(self,meshPart):
        f = mod3.MODVertexBufferSelector(meshPart.BlockType)
        headerref = meshPart.headerref
        if f != None:
            VOFF=headerref.VertexOffset+meshPart.VertexOffset
            BOFF=meshPart.VertexSub+meshPart.VertexBase
            fileOp.Seek(headerref.fl,(VOFF+meshPart.BlockSize*BOFF))
            meshPart.meshdata = f(headerref,meshPart.VertexCount)
            fileOp.Seek(headerref.fl,(headerref.FaceOffset+meshPart.FaceOffset*2))
            meshPart.FaceCount = int(meshPart.FaceCount/3)
            meshPart.meshdata.facearray = CollectTris(headerref.fl, headerref.bendian, meshPart.FaceCount,0-meshPart.VertexSub, )
        else:
            raise Exception("Unknown block hash [%08x] for MTF v1 model format.\n" % meshPart.BlockType)

    def readMeshPartv1(self,uid):
        MeshPartOffset = fileOp.getPos(self.fl)
        if self.bendian:
            fl = self.fl
            id = fileOp.ReadBEShort(fl)
            Material = fileOp.ReadBEShort(fl )
            fileOp.ReadByte(fl)
            LOD = fileOp.ReadByte(fl)
            fileOp.ReadShort(fl)
            BlockSize = fileOp.ReadByte(fl)
            BlockType = fileOp.ReadByte(fl)
            fileOp.fseek(fl,2)
            VertexCount = fileOp.ReadBEShort(fl) 
            fileOp.ReadShort(fl)
            VertexSub = fileOp.ReadBELong(fl)
            VertexOffset = fileOp.ReadBELong(fl) 
            fileOp.fseek(fl,4)
            FaceOffset = fileOp.ReadBELong(fl)
            FaceCount = fileOp.ReadBELong(fl)
            VertexBase = fileOp.ReadBELong(fl)
            fileOp.fseek(fl,6)
            boneremapid = fileOp.ReadByte(fl)+1
            fileOp.fseek(fl,5)
        else:
            fl = self.fl
            id = fileOp.ReadShort(fl)
            UnknS2Idx = fileOp.ReadByte(fl)
            Material = fileOp.ReadShort(fl)
            LOD = fileOp.ReadByte(fl)
            fileOp.ReadShort(fl)
            BlockSize = fileOp.ReadByte(fl)
            BlockType = fileOp.ReadByte(fl)
            fileOp.fseek(fl,2)
            VertexCount = fileOp.ReadShort(fl) 
            fileOp.ReadShort(fl)
            VertexSub = fileOp.ReadLong(fl)
            VertexOffset = fileOp.ReadLong(fl) 
            fileOp.fseek(fl,4)
            FaceOffset = fileOp.ReadLong(fl) 
            FaceCount = fileOp.ReadLong(fl)
            VertexBase = fileOp.ReadLong(fl) 
            fileOp.fseek(fl,6)
            boneremapid = fileOp.ReadByte(fl)+1
            fileOp.fseek(fl,5)
        return Mod.MeshPart(
            MeshPartOffset,
            uid,
            id,
            Material,
            UnknS2Idx,
            LOD,
            BlockSize,
            BlockType,
            VertexSub,
            VertexCount,
            VertexOffset,
            FaceOffset,
            FaceCount,
            VertexBase,
            None,
            boneremapid,
            self,
            self.loadmeshdatav1,
            self.writemeshdatav1)


    def readMeshPartv2(self,uid):
        raise Exception("readMeshPartv2 not implemented")
    def readMeshPartv3(self,uid):
        headerref = self.headerref
        MeshPartOffset = fileOp.getPos(headerref.fl)
        fileOp.ReadShort(headerref.fl)
        VertexCount = fileOp.ReadShort(headerref.fl)     
        id = fileOp.ReadShort(headerref.fl)
        Material = fileOp.ReadShort(headerref.fl)
        lod = fileOp.ReadLong(headerref.fl)
        fileOp.ReadShort(headerref.fl)
        BlockSize = fileOp.ReadByte(headerref.fl)
        fileOp.ReadByte(headerref.fl)
        VertexSub = fileOp.ReadLong(headerref.fl)
        VertexOffset = fileOp.ReadLong(headerref.fl)
        BlockType = fileOp.ReadLong(headerref.fl)
        FaceOffset = fileOp.ReadLong(headerref.fl)
        FaceCount = fileOp.ReadLong(headerref.fl)
        VertexBase = fileOp.ReadLong(headerref.fl)
        boneremapid = fileOp.ReadByte(headerref.fl)+1
        fileOp.fseek(headerref.fl,39)
        return Mod.MeshPart(
            MeshPartOffset,
            uid,
            id,
            Material,
            uid,
            lod,
            BlockSize,
            BlockType,
            VertexSub,
            VertexCount,
            VertexOffset,
            FaceOffset,
            FaceCount,
            VertexBase,
            None,
            boneremapid,
            self,
            self.loadmeshdatav3,
            self.writemeshdatav3)
    
    def readMaterials(self):
        dbg("readMaterials")
        headerref = self.headerref
        fileOp.Seek(self.fl,headerref.MaterialNamesOffset)
        materials = []
        for i in range(0,headerref.MaterialCount):
            s = fileOp.ReadString(headerref.fl,128)
            dbg(s)
            materials.append(s)
        return materials
    
    def readMeshParts(self):
        headerref = self.headerref
        dbg("readMeshParts, meshOffset: %08x" % headerref.MeshOffset)
        fileOp.Seek(self.fl,headerref.MeshOffset)
        if(self.Version == 237):
            readMeshPart = self.readMeshPartv3
        elif(self.Version < 190):
            readMeshPart = self.readMeshPartv1
        else:
            readMeshPart = self.readMeshPartv2
        for i in range(0,self.MeshCount):
           self.parts.append(readMeshPart(i))
        dbg("%d %d" % (len(self.parts),headerref.MeshCount))

    def readVertexes(self):
        headerref = self.headerref
        fileOp.Seek(self.fl,headerref.VertexOffset)
        for m in self.parts:
            m.loadmeshdata()

    def parseMrl3(self,filepath):
        global PATH,CHUNK_PATH

        from .mhw_texture import doImportTex

        
        if not os.path.isfile(filepath):
            dbg("%s not found" % filepath)
            return
        
        if not os.path.isdir(CHUNK_PATH):
            raise Exception("Chunkdirectory %s does not exist!" % CHUNK_PATH)
        
        with open(filepath, 'rb') as content_file:
            content = content_file.read()
            fl = fileOp.createContentStream(content)

        fileOp.Seek(fl,0)
        fileOp.ReadLong(fl)
        for u in range(0,12):
            fileOp.ReadByte(fl)
        materialCount = fileOp.ReadLong(fl)
        textureCount = fileOp.ReadLong(fl)
        #unknS2Count = fileOp.ReadLong(fl)
        for i in range(0,3):
            fileOp.ReadLong(fl)
        
        for i in range(0,textureCount):
            fileOp.ReadLong(fl)
            for i in range(0,12):
                fileOp.ReadByte(fl)
            tex = ""
            for j in range(0,256):
                b = fileOp.ReadByte(fl)
                if b != 0:
                    by = chr(b)
                    tex = "%s%s" % (tex,by)
            texname = "%s.tex" % tex
            texpath = "%s\\%s" % (os.path.dirname(filepath),os.path.basename(texname))
            dbg("testing local path %s" % texpath)
            if not os.path.isfile(texpath):
                texpath = "%s\\%s" % (CHUNK_PATH,texname)
                if not os.path.isfile(texpath):
                    chunk_folders = ["chunk0","chunk1","chunk2"]
                    for c in chunk_folders:
                        try:
                            if(CHUNK_PATH.index(c)>0):
                                for n in range(0,3):
                                    texpath = "%s\\%s.tex" % (CHUNK_PATH.replace(c,"chunk%d" % n),tex)
                                    if os.path.isfile(texpath):
                                        break
                        except ValueError as e:
                            pass

            dbg("importing texture: %s" % (texpath))
            doImportTex(texpath)
        
        materials = []
        unknS2A = []
        for mi in range(0,materialCount):
            m = Mod.Material(fl,mi)
            materials.append(m)
        ui = 0
        for m in materials:
            fileOp.Seek(fl,m.startAddr)
            unknS2 = Mod.UnknS2(fl,ui)
            m.unknS2 = unknS2
            unknS2A.append(unknS2)
            ui += 1
        return (materials,unknS2A)
    
    def execute(self, context):
        global CHUNK_PATH
        
        previous_context = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.view3d.snap_cursor_to_center()
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError as e:
            #ignore this error, it can happen when no object is visible!
            pass
        try:
            if self.clear_scene_before_import:
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.delete() 
                for i in bpy.data.images.keys():
                    bpy.data.images.remove(bpy.data.images[i])
            self.embed_data = True if self.embed_mode == cons.EMBED_MODE_DATA else False
            self.reference_data = True if self.embed_mode == cons.EMBED_MODE_REFERENCE else False
            self.init_main()
            CHUNK_PATH = self.chunk_path
            if CHUNK_PATH[len(CHUNK_PATH)-1] == '\\':
                CHUNK_PATH = CHUNK_PATH[0:len(CHUNK_PATH)-1]
            PATH = self.install_path
            if not os.path.isdir(PATH):
                raise Exception("Install path %s not found!" % PATH)
            dbg("CHUNK_PATH: %s" % CHUNK_PATH)
            dbg("PATH: %s" % PATH)
            dbg("self: %s" % self)
            dbg("context: %s" % context)
            dbg("typeof(chunk_path): %s " % type(self.chunk_path))
            setInstallPath(PATH)
            setChunkPath(CHUNK_PATH)
            writeConfig()
            if(self.import_textures):
                (self.materials,self.unknS2) = self.parseMrl3(self.filepath.replace(".mod3",".mrl3"))
            if(self.use_layers != cons.LAYER_MODE_NONE):
                dbg("using layers %s" % self.use_layers)
            with open(self.filepath, 'rb') as content_file:
                content = content_file.read()
                fl = fileOp.createContentStream(content)
                if self.reference_data:
                    if('data' in bpy.data.texts):
                        dataText = bpy.data.texts['data']
                        dataText.clear()
                    else:
                        dataText = bpy.data.texts.new('data')
                    dataText.from_string("path:%s" % self.filepath)
                else:
                    if self.embed_data:
                        cdata = zlib.compress(content)
                        dbg("len of compressed-data: %d" % len(cdata))
                        data = base64.b64encode(cdata).decode("utf-8")
                        dbg("len of b64-data: %d" % len(data))
                        if('data' in bpy.data.texts):
                            dataText = bpy.data.texts['data']
                            dataText.clear()
                        else:
                            dataText = bpy.data.texts.new('data')
                        dataText.from_string(data)
            self.startImport(fl)
            if(self.import_textures):
                bpy.context.area.type = previous_context
                area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
                space = next(space for space in area.spaces if space.type == 'VIEW_3D')
                space.viewport_shade = "TEXTURED"
            bpy.ops.object.select_all(action='DESELECT')
            return {'FINISHED'}
        finally:
            bpy.context.area.type = previous_context
            
    def startImport(self,fl):
        if not "shadeless" in bpy.data.materials:
            shadeless = bpy.data.materials.new("Shadeless")
        else:
            shadeless = bpy.data.materials["Shadeless"]
        shadeless.use_shadeless = True
        shadeless.use_face_texture = True

        self.fl = fl
        fileOp.Seek(fl,0)
            
        self.readHeader()
        self.materialsNames = self.readMaterials()
        if self.do_read_bones:
            self.readBones()
        self.readMeshParts()
        self.readVertexes()
        
        fi = 0
        pi = 0
        rpi = -1
        lodlayers = {}
        clod = 1
        if(self.use_layers == cons.LAYER_MODE_LOD):
            for m in self.parts:
                if not m.LOD in lodlayers:
                    lodlayers[m.LOD] = clod
                    clod += 1
        dbg("self.parts: %d" % len(self.parts))
        for m in self.parts:
            if ((self.only_import_lod < 0) and (self.only_import_lod_1)) and ((m.LOD != 1) and (m.LOD != 0xFFFF)):
                dbg("Skipped mesh %d because of lod level: %d, expected: 1" % (pi,m.LOD))
                pi += 1
                continue
            if (self.only_import_lod > -1) and (m.LOD != self.only_import_lod):
                dbg("Skipped mesh %d because of lod level: %d , expected: %d" % (pi,m.LOD,self.only_import_lod))
                pi += 1
                continue
            if m.meshdata != None:
                rpi += 1
                normals = m.meshdata.normalarray
                dbg("Import mesh %d, normals length: %d" % (pi,len(normals)))
                bm = bmesh.new()
                my_id = bm.verts.layers.int.new('id')
                bm.verts.ensure_lookup_table()
                mesh = bpy.data.meshes.new("mesh")  # add a new mesh
                s = m.getName()
                obj = bpy.data.objects.new(s, mesh)  # add a new object using the mesh
                dbg("%s %d     %d" % (s,m.VertexCount,len(m.meshdata.vertarray)))
                verts  = []
                verts2 = []
                faces = []
                face_vertex_index = {}
                bmfaces = []
                vi = 0
                for v in m.meshdata.vertarray:
                    #dbg(v)
                    verts2.append(v)
                    bmv = bm.verts.new(v)
                    if vi < len(normals):
                        fx = float(normals[vi][0])
                        fy = float(normals[vi][1])
                        fz = float(normals[vi][2])
                        nvl = math.sqrt(fx*fx + fy*fy + fz*fz)
                        if nvl == 0:
                            bmv.normal = [0,0,0]
                        else:
                            bmv.normal = [fx/nvl,fy/nvl,fz/nvl]
                        #dbg("normal for mespart %d and vertex %d: %s (%s)" % (pi,vi,bmv.normal,(fx,fy,fz)))
                    bmv[my_id] = vi
                    bmv.index = vi
                    verts.append(bmv)
                    vi += 1

                
                if(self.import_textures):
                    tex = bm.faces.layers.tex.new("main_uv_texture")
                uv = bm.loops.layers.uv.new("main_uv_layer")

                fi = 0
                for f in m.meshdata.facearray:
                    addFace=True
                    for x in f:
                        if x >= len(verts):
                            addFace = False
                            #dbg("%d not in verts [%d]" % (x,len(verts)))
                    if addFace:
                        #if fi<30:
                        vts  = [verts[x] for x in f]
                        #vts2 = [verts2[x] for x in f]
                        uvs  = [m.meshdata.uvs[x] for x in f]
                        #dbg(vts)
                        #dbg(vts2)
                        #dbg(f)
                        faces.append(vts)
                        fi+=1
                        uidx = m.UnknS2Idx
                        iidx = 0
                        imgi = 0
                        if self.import_textures and (uidx < len(self.materials)):
                            iidx = self.materials[uidx].unknS2.texIdx-1
                            if iidx > len(bpy.data.images):
                                dbg("something went wrong, using default iidx [%d is out of range, unknS2-offset: %08x]" % (iidx,self.unknS2[uidx].offset))
                                for img in bpy.data.images:
                                    if "_BML" in img.name:
                                        iidx = imgi
                                        break
                                    imgi += 1

                        #dbg("using image index %d for mesh: %d" % (iidx,pi))
                        try:
                            face = bm.faces.new(vts)
                            vindices = [x for x in f]
                            if(self.import_textures):
                                face[tex].image = bpy.data.images[iidx]
                            vi = 0
                            for loopi in range(0,len(face.loops)):
                                loop = face.loops[loopi]
                                loop[uv].uv = uvs[vi]
                                vi += 1
                            bmfaces.append(face)
                            face_vertex_index[face] = vindices
                        except Exception as e:
                            dbg(e)
                        #pass
                    else:
                        raise Exception("Problem with face:%s [vert len:%d,pos:%08x]" % (f,len(verts),fileOp.pos[fl]))

                scene = bpy.context.scene
                scene.objects.link(obj)  # put the object into the scene (link)
                if(self.use_layers == cons.LAYER_MODE_PARTS):
                    for i in range(19):
                        obj.layers[1+i] = (i == (rpi % 19)) # we only have 20 layers available ... sadly
                if(self.use_layers == cons.LAYER_MODE_LOD):
                    for i in range(19):
                        obj.layers[1+i] = (1+i == (lodlayers[m.LOD])) # we only have 20 layers available ... sadly
                    
                scene.objects.active = obj  # set as the active object in the scene
                obj.select = True  # select object

                # make the bmesh the object's mesh
                bm.to_mesh(mesh)

                bm2 = obj.data                
                for p in bm2.polygons:
                    for loop in p.loop_indices:
                        #dbg("setting loop normal for mespart %d and vertex %d: %s" % (pi,bm2.loops[loop].vertex_index,verts[bm2.loops[loop].vertex_index].normal))
                        bm2.loops[loop].normal = verts[bm2.loops[loop].vertex_index].normal

                
                
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.faces_shade_smooth()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                
                if len(verts)>0:
                    boneIds = []
                    for v in verts:
                        #v2 = verts2[v[my_id]]
                        if (len(m.meshdata.bones)>0) and len(m.meshdata.bones[v[my_id]])>0:
                            wi = 0
                            for bId in m.meshdata.bones[v[my_id]]:
                                if bId not in boneIds:
                                    boneIds.append(bId)
                                    vg = obj.vertex_groups.new(cons.FMT_BONE % bId)
                                else:
                                    vg = obj.vertex_groups[cons.FMT_BONE % bId]
                                #dbg("add %d to vg: Bone%d" % (v.index,bId))
                                vg.add([v.index],m.meshdata.weights[v[my_id]][wi],"ADD")
                                wi += 1

                mesh.materials.append(shadeless)
                mesh["LOD"] = m.LOD
                mesh["Material"] = self.materialsNames[m.Material]

                bm.free()  # always do this when finished
            else:
                dbg("Skipped mesh %d because of empty data" % pi)

            pi += 1

        if self.do_read_bones:
            self.createBones(cons.MAIN_ARMATURE,self.lmatrices)
            if self.read_amatrices:
                self.createBones(cons.AMATRICES_ARMATURE,self.amatrices)
        
# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportMOD3.bl_idname, text="MHW MOD (.mod3)")
def menu_func_export(self, context):
    self.layout.operator(ExportMOD3.bl_idname, text="MHW MOD (.mod3)")