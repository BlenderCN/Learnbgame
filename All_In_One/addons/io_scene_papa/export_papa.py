import bpy
import struct
import mathutils
import logging

log = logging.getLogger(__name__)

def pad(currentLength,file):
    if (currentLength % 8 != 0):
        paddedLength = 8 - (currentLength % 8)

        padString = ""
        for i in range(0, paddedLength):
            file.write(struct.pack('B',0))
    else:
        paddedLength = 0
    return paddedLength

def write_papa(filepath,context):

    Vertex_PositionX = [];
    Vertex_PositionY = [];
    Vertex_PositionZ = [];
    Vertex_BoneSegment = [];
    Vertex_NormalX = [];
    Vertex_NormalY = [];
    Vertex_NormalZ = [];
    Vertex_U = [];
    Vertex_V = [];
    
    Triangle_VertexA = [];
    Triangle_VertexB = [];
    Triangle_VertexC = [];

    BoneSegment_BoneID = [];
    BoneSegment_ParentSegment = [];
    BoneSegment_X = [];
    BoneSegment_Y = [];
    BoneSegment_Z = [];
    BoneSegment_OffsetX = [];
    BoneSegment_OffsetY = [];
    BoneSegment_OffsetZ = [];
    BoneSegment_Rotation = [];

    Bone_NameLength = [];
    Bone_NameOffset = [];
    Bone_Name = [];
  
    NumberOfVertices = 0
    NumberOfTriangles = 0
    NumberOfBones = 0;
    SkeletonSegments = 0

    _objects = bpy.context.scene.objects
    for _item in _objects:
        log.warning("Found object: {}".format(_item.type))

    for item in bpy.context.scene.objects:   
        if (item.type == 'MESH'):

            log.warning("Processing {} vertices".format(len(item.data.vertices)))
            
            for vertex in item.data.vertices:
                Vertex_PositionX.append(vertex.co.x)
                Vertex_PositionY.append(vertex.co.y)
                Vertex_PositionZ.append(vertex.co.z)
                
                if not len(vertex.groups):
                    log.error("Vertex {} does not belong to a group".format(vertex))
                    log.error("Ensure that all vertices are assigned to a vertex group")
                
                Vertex_BoneSegment.append(vertex.groups[0].group)
                Vertex_NormalX.append(vertex.normal.x)
                Vertex_NormalY.append(vertex.normal.y)
                Vertex_NormalZ.append(vertex.normal.z)
                Vertex_U.append(0) #TODO
                Vertex_V.append(0) #TODO
                NumberOfVertices= NumberOfVertices + 1

            log.warning("Processing {} faces".format(len(item.data.tessfaces)))

            item.data.update(calc_tessface=True);
            for face in item.data.tessfaces:
                
                Triangle_VertexA.append(face.vertices[0])
                Triangle_VertexB.append(face.vertices[1])
                Triangle_VertexC.append(face.vertices[2])
                #Vertex_U[face.vertices[0]] = face.uv1
                #print(face.uv1)
                NumberOfTriangles = NumberOfTriangles + 1

##            uvtex = item.data.tessface_uv_textures.active
##            if (uvtex):
##                for uv_index, uv_itself in enumerate(uvtex.data):
##                    uvs = uv_itself.uv1, uv_itself.uv2, uv_itself.uv3, uv_itself.uv4
##                    for vertex_index, vertex_itself in enumerate(item.data.tessfaces[uv_index].vertices):
##                        Vertex_U[vertex_index] = uv_itself[0] #fix
##                        Vertex_V[vertex_index] = uv_itself[1] #fix
                    
            uvl = item.data.uv_layers.active.data[:]
            for i in range(0, NumberOfTriangles):
                
                if i*3 >= len(uvl):
                    log.error("Found too many triangles")
                    log.error("Make sure to weld vertices and triangulate model")
                    
                Vertex_U[Triangle_VertexA[i]] = uvl[i*3].uv[0]
                Vertex_V[Triangle_VertexA[i]] = 1 - uvl[i*3].uv[1]
                Vertex_U[Triangle_VertexB[i]] = uvl[i*3+1].uv[0]
                Vertex_V[Triangle_VertexB[i]] = 1 - uvl[i*3+1].uv[1]
                Vertex_U[Triangle_VertexC[i]] = uvl[i*3+2].uv[0]
                Vertex_V[Triangle_VertexC[i]] = 1 - uvl[i*3+2].uv[1]
                
        if (item.type == 'ARMATURE'):
            parent_rotation = []

            _bones = item.data.bones
            for _bone in _bones:
                log.warning("Found bone {}".format(_bone.name))

            for bone in item.data.bones:
                Bone_Name.append(bone.name);
                Bone_NameLength.append(len(bone.name));
                NumberOfBones = NumberOfBones + 1
                if (NumberOfBones>3):
                    BoneSegment_BoneID.append(NumberOfBones-1)
                    BoneSegment_X.append(bone.head_local.x)
                    BoneSegment_Y.append(bone.head_local.y)
                    BoneSegment_Z.append(bone.head_local.z)
                    if (bone.parent):
                        _parent_index = Bone_Name.index(bone.parent.name)
                        
                        if not _parent_index in BoneSegment_BoneID:
                            log.error("Parent {} of bone {} not previously found".format(bone.parent.name, bone.name))
                            log.error("Check that all required bones are present in the correct order")
                        
                        parentSegmentID = BoneSegment_BoneID.index(Bone_Name.index(bone.parent.name))
                        SegmentID = SkeletonSegments
                        BoneSegment_ParentSegment.append(parentSegmentID)
                        BoneSegment_X[SegmentID]=bone.head_local.x-bone.parent.head_local.x
                        BoneSegment_Y[SegmentID]=bone.head_local.y-bone.parent.head_local.y
                        BoneSegment_Z[SegmentID]=bone.head_local.z-bone.parent.head_local.z
                        original = bone.matrix
                        rotation = parent_rotation * bone.matrix
                        parent_rotation = rotation
                        A = [rotation[0][0],-rotation[1][0],rotation[2][0],0]
                        B = [rotation[0][2],-rotation[1][2],rotation[2][2],0]
                        C = [rotation[0][1],-rotation[1][1],rotation[2][1],0]
                        D = [0,0,0,1]
                        BoneSegment_Rotation.append([D, A, B, C])
                        BoneSegment_OffsetX.append(BoneSegment_OffsetX[parentSegmentID] - BoneSegment_X[SegmentID])
                        BoneSegment_OffsetY.append(BoneSegment_OffsetY[parentSegmentID] - BoneSegment_Y[SegmentID])
                        BoneSegment_OffsetZ.append(BoneSegment_OffsetZ[parentSegmentID] - BoneSegment_Z[SegmentID])
                    else:
                        BoneSegment_ParentSegment.append(-1)
                        BoneSegment_OffsetX.append(0)
                        BoneSegment_OffsetY.append(0)
                        BoneSegment_OffsetZ.append(0)
                        BoneSegment_Rotation.append([[0,0,0,1],[1,0,0,0],[0,1,0,0],[0,0,1,0]])

                        
                    if (SkeletonSegments == 0):
                        parent_rotation = bone.matrix
                    SkeletonSegments = SkeletonSegments + 1

    file = open(filepath, 'wb')

    #PapaFile
    
    PapaFile = []


    OffsetUnknown1 = -1;
    OffsetFramesHeader = 104
    OffsetInformationHeader = OffsetFramesHeader + 80 + 80 + 2 * SkeletonSegments;
                            
    if (SkeletonSegments % 4 != 0):
        OffsetInformationHeader = OffsetInformationHeader + 8 - (OffsetInformationHeader % 8)  #Padding
                            
    OffsetCoordinateHeader = OffsetInformationHeader + 16 + 32;
    OffsetVerticesHeader = OffsetCoordinateHeader + 64 + 48;
    OffsetIndicesHeader = OffsetVerticesHeader + 24 + 40 * NumberOfVertices;
                            
    if (SkeletonSegments > 0):
        OffsetSkeletonHeader = OffsetIndicesHeader + 24 + 6 * NumberOfTriangles;
        if (6 * NumberOfTriangles % 8 != 0):
            OffsetSkeletonHeader = OffsetSkeletonHeader + 8 - (OffsetSkeletonHeader % 8)  #Padding
    else:
        OffsetSkeletonHeader = -1
    if (NumberOfBones > 0):
        OffsetBonesHeader = OffsetSkeletonHeader + 16 + SkeletonSegments * 132;
        if (SkeletonSegments * 132 % 8 != 0):
            OffsetBonesHeader = OffsetBonesHeader + 8 - (OffsetBonesHeader % 8)  #Padding
    else:
        OffsetBonesHeader = -1 

    OffsetUnknown2 = -1;
    
    PapaFile = PapaFile + [b'a',b'p',b'a',b'P']
    PapaFile = PapaFile + [0,0,2,0]
    PapaFile.append(NumberOfBones)
    PapaFile = PapaFile + [1,0,1,0,2,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0]
    PapaFile.append(OffsetBonesHeader)
    PapaFile.append(OffsetUnknown1)
    PapaFile.append(OffsetVerticesHeader)
    PapaFile.append(OffsetIndicesHeader)
    PapaFile.append(OffsetCoordinateHeader)
    PapaFile.append(OffsetInformationHeader)
    PapaFile.append(OffsetSkeletonHeader)
    PapaFile.append(OffsetFramesHeader)
    PapaFile.append(OffsetUnknown2)

    #PapaFramesHeader
    PapaFramesHeader = []

    OffsetSubFramesHeader = OffsetFramesHeader + 80

    PapaFramesHeader = PapaFramesHeader + [0,1,1]
    PapaFramesHeader = PapaFramesHeader + [0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    PapaFramesHeader.append(OffsetSubFramesHeader)

    #PapaSubFramesHeader
    PapaSubFramesHeader = []

    if (SkeletonSegments > 0):
        OffsetFrame = OffsetSubFramesHeader + 80
    else:
        OffsetFrame = -1
               
    PapaSubFramesHeader.append(0)
    PapaSubFramesHeader.append(SkeletonSegments)
    PapaSubFramesHeader.append(1)
    PapaSubFramesHeader =PapaSubFramesHeader + [0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    PapaSubFramesHeader.append(OffsetFrame)

    #PapaFrame
    PapaFrame = []
    
    for i in range(0, SkeletonSegments):
        PapaFrame.append(i)

    #PapaInformationHeader
    PapaInformationHeader = []

    OffsetInformation = OffsetInformationHeader + 16

    PapaInformationHeader = PapaInformationHeader + [0,2]
    PapaInformationHeader.append(OffsetInformation)

    #PapaInformation
    PapaInformation = []

    NumberOfIndices = NumberOfTriangles * 3

    PapaInformation = PapaInformation + [65535,0]
    PapaInformation.append(NumberOfTriangles)
    PapaInformation = PapaInformation + [2,131071]
    PapaInformation.append(NumberOfIndices)
    PapaInformation = PapaInformation + [0,2]


    #PapaCoordinateHeader
    PapaCoordinateHeader = []

    OffsetCoordinate1 = OffsetCoordinateHeader + 64
    OffsetCoordinate2 = OffsetCoordinate1 + 24

    PapaCoordinateHeader = PapaCoordinateHeader + [1,1,0]
    PapaCoordinateHeader.append(OffsetCoordinate1)
    PapaCoordinateHeader = PapaCoordinateHeader + [-1,-1,1,1,0]
    PapaCoordinateHeader.append(OffsetCoordinate2)           
    PapaCoordinateHeader = PapaCoordinateHeader + [-1,-1]

    #PapaCoordinate1
    PapaCoordinate1 = []

    PapaCoordinate1 = PapaCoordinate1 + [2, 0.4745098, 0.4745098, 0.4745098,0,0]

    #PapaCoordinate2
    PapaCoordinate2 = []

    PapaCoordinate2 = PapaCoordinate2 + [2, 0.588, 0.588, 0.588,0,0]

    #PapaVerticesHeader
    PapaVerticesHeader = []

    SizeOfVerticesBlock = NumberOfVertices * 40
    OffsetVertices = OffsetVerticesHeader + 24

    PapaVerticesHeader = PapaVerticesHeader + [8]
    PapaVerticesHeader.append(NumberOfVertices)
    PapaVerticesHeader.append(SizeOfVerticesBlock)
    PapaVerticesHeader.append(OffsetVertices)


    #PapaVertex
    PapaVertex = []
               
    for i in range(0, NumberOfVertices):
        PapaVertex.append(Vertex_PositionX[i])
        PapaVertex.append(Vertex_PositionY[i])
        PapaVertex.append(Vertex_PositionZ[i])
        PapaVertex.append(255)
        PapaVertex.append(0)
        PapaVertex.append(0)
        PapaVertex.append(0)
        PapaVertex.append(Vertex_BoneSegment[i])
        PapaVertex.append(Vertex_NormalX[i])
        PapaVertex.append(Vertex_NormalY[i])
        PapaVertex.append(Vertex_NormalZ[i])
        PapaVertex.append(Vertex_U[i])
        PapaVertex.append(Vertex_V[i])

    #PapaIndicesHeader
    PapaIndicesHeader = []

    SizeOfIndicesBlock = NumberOfTriangles * 6
    OffsetIndices = OffsetIndicesHeader + 24

    PapaIndicesHeader.append(0)
    PapaIndicesHeader.append(NumberOfIndices)
    PapaIndicesHeader.append(SizeOfIndicesBlock)
    PapaIndicesHeader.append(OffsetIndices)

    

    #PapaTriangle
    PapaTriangle = []
               
    for i in range(0, NumberOfTriangles):
        PapaTriangle.append(Triangle_VertexA[i]);
        PapaTriangle.append(Triangle_VertexB[i]);
        PapaTriangle.append(Triangle_VertexC[i]);

    

    #PapaSkeletonHeader
    PapaSkeletonHeader = []

    OffsetSkeletonSegment = OffsetSkeletonHeader + 16

    PapaSkeletonHeader.append(SkeletonSegments)
    PapaSkeletonHeader.append(0)
    PapaSkeletonHeader.append(OffsetSkeletonSegment)
    
    #PapaSkeletonSegment
    PapaSkeletonSegment = []
    
    for i in range(0, SkeletonSegments):
        PapaSkeletonSegment.append(BoneSegment_BoneID[i])
        PapaSkeletonSegment.append(BoneSegment_ParentSegment[i])
        PapaSkeletonSegment.append(BoneSegment_X[i])
        PapaSkeletonSegment.append(BoneSegment_Y[i])
        PapaSkeletonSegment.append(BoneSegment_Z[i])
        PapaSkeletonSegment = PapaSkeletonSegment + [0,0,0]
        PapaSkeletonSegment = PapaSkeletonSegment + [1,1,0]
        PapaSkeletonSegment = PapaSkeletonSegment + [0,0,1]
        PapaSkeletonSegment = PapaSkeletonSegment + [BoneSegment_Rotation[i][0][0],BoneSegment_Rotation[i][0][1],BoneSegment_Rotation[i][0][2],BoneSegment_Rotation[i][0][3]]
        PapaSkeletonSegment = PapaSkeletonSegment + [BoneSegment_Rotation[i][1][0],BoneSegment_Rotation[i][1][1],BoneSegment_Rotation[i][1][2],BoneSegment_Rotation[i][1][3]]
        PapaSkeletonSegment = PapaSkeletonSegment + [BoneSegment_Rotation[i][2][0],BoneSegment_Rotation[i][2][1],BoneSegment_Rotation[i][2][2],BoneSegment_Rotation[i][2][3]]
        PapaSkeletonSegment = PapaSkeletonSegment + [BoneSegment_Rotation[i][3][0],BoneSegment_Rotation[i][3][1],BoneSegment_Rotation[i][3][2],BoneSegment_Rotation[i][3][3]]
        PapaSkeletonSegment.append(BoneSegment_OffsetX[i])
        PapaSkeletonSegment.append(BoneSegment_OffsetY[i])
        PapaSkeletonSegment.append(BoneSegment_OffsetZ[i])
        PapaSkeletonSegment.append(1)

    #PapaBones
    PapaBones = []

    CumulativeBoneNameLength = 0
    
    for i in range(0, NumberOfBones):
        PapaBones.append(Bone_NameLength[i])
        OffsetBoneName = OffsetBonesHeader + NumberOfBones * 16 + CumulativeBoneNameLength
        PapaBones.append(OffsetBoneName)
        CumulativeBoneNameLength = CumulativeBoneNameLength + Bone_NameLength[i]
        if (CumulativeBoneNameLength % 8 != 0):
            CumulativeBoneNameLength = CumulativeBoneNameLength + 8 - (CumulativeBoneNameLength % 8)
    
    #PapaBoneNames
    PapaBoneNames = []

    TotalBoneNameLength = 0
    
    for i in range(0, NumberOfBones):
        TotalBoneNameLength = TotalBoneNameLength + Bone_NameLength[i]

        tempBoneName = Bone_Name[i]
        if (TotalBoneNameLength % 8 != 0):
            for i in range(0, int(8 - (TotalBoneNameLength %8))):
                tempBoneName = tempBoneName + '\0'
            TotalBoneNameLength = TotalBoneNameLength + 8 - (TotalBoneNameLength %8)
        PapaBoneNames.append(tempBoneName)
      
    file.write(struct.pack('ccccBBBBIBBBBBBBBBBBBBBBBBBBBqqqqqqqqq', *PapaFile))
    file.write(struct.pack('IIffffffffffffffffq', *PapaFramesHeader));
    file.write(struct.pack('IIffffffffffffffffq', *PapaSubFramesHeader));
    file.write(struct.pack('H'*SkeletonSegments, *PapaFrame));
    pad(2 * SkeletonSegments,file)
    file.write(struct.pack('IIq', *PapaInformationHeader));
    file.write(struct.pack('IIIIIIII', *PapaInformation));
    file.write(struct.pack('HHIqqqHHIqqq', *PapaCoordinateHeader));
    file.write(struct.pack('Ifffff', *PapaCoordinate1));
    file.write(struct.pack('Ifffff', *PapaCoordinate1));
    file.write(struct.pack('IIqq', *PapaVerticesHeader));
    file.write(struct.pack('fffBBBBIfffff'*NumberOfVertices, *PapaVertex));
    file.write(struct.pack('IIqq', *PapaIndicesHeader));
    file.write(struct.pack('HHH'*NumberOfTriangles, *PapaTriangle));
    pad(6 * NumberOfTriangles,file)
    file.write(struct.pack('IIq', *PapaSkeletonHeader));
    file.write(struct.pack('hhffffffffffffffffffffffffffffffff'*SkeletonSegments, *PapaSkeletonSegment));
    pad(132 * SkeletonSegments,file)
    file.write(struct.pack('qq'*NumberOfBones, *PapaBones));

    allNames = "".join(PapaBoneNames)
    file.write(struct.pack('B' * CumulativeBoneNameLength, *bytearray(allNames,'utf_8')));

    

    file.close();
    
    return

def write(operator,context,filepath=""):
    write_papa(filepath,context)
    
    return {'FINISHED'}

