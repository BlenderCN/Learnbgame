import bpy
import struct
import mathutils

def load_papa(filepath,context):
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    file = open(filepath, 'rb')

    #PapaFile
    PapaFile = struct.unpack('IHHHHHHHHHHHHHHqqqqqqqqq', file.read(104));

    NumberOfBones = PapaFile[3];
    NumberOfTextures = PapaFile[4];
    NumberOfVertexBuffers = PapaFile[5];
    NumberOfIndexBuffers = PapaFile[6];
    NumberOfMaterials = PapaFile[7];
    NumberOfMeshes = PapaFile[8];
    NumberOfSkeletons = PapaFile[9];
    NumberOfModels = PapaFile[10];
    OffsetBonesHeader = PapaFile[15];
    OffsetTextureInformation = PapaFile[16];
    OffsetVerticesHeader = PapaFile[17];
    OffsetIndicesHeader = PapaFile[18];
    OffsetMaterialHeader = PapaFile[19];
    OffsetInformationHeader = PapaFile[20];
    OffsetSkeletonHeader = PapaFile[21];
    OffsetModelInformation = PapaFile[22];
    OffsetAnimationInformation = PapaFile[23];

    #PapaModelInformation
    file.seek(OffsetModelInformation);
    PapaFramesHeader = struct.unpack('IIffffffffffffffffq', file.read(80));
    OffsetSubFramesHeader = PapaFramesHeader[18];

    #PapaSubFramesHeader
    file.seek(OffsetSubFramesHeader);
    PapaSubFramesHeader = struct.unpack('IIffffffffffffffffq', file.read(80));
    SkeletonSegments = PapaSubFramesHeader[1];
    OffsetFrame = PapaFramesHeader[18];

    #PapaFrame
    #Not needed at this time.

    #PapaInformationHeader
    file.seek(OffsetInformationHeader);
    PapaInformationHeader = struct.unpack('IIq', file.read(16));
    InformationFormat = PapaInformationHeader[1];
    OffsetInformation = PapaInformationHeader[2];
        
    #PapaInformation
    #Not Needed

    #PapaCoordinateHeader
    #Not Needed

    #PapaCoordinate1
    #Not Needed

    #PapaCoordinate2
    #Not Needed

    #PapaVerticesHeader
    file.seek(OffsetVerticesHeader);
    PapaVerticesHeader = struct.unpack('IIqq', file.read(24));
    VertexFormat = PapaVerticesHeader[0];
    NumberOfVertices = PapaVerticesHeader[1];
    OffsetVertices = PapaVerticesHeader[3];

    Vertex_PositionX = [];
    Vertex_PositionY = [];
    Vertex_PositionZ = [];
    Vertex_BoneSegment = [];
    Vertex_NormalX = [];
    Vertex_NormalY = [];
    Vertex_NormalZ = [];
    Vertex_U = [];
    Vertex_V = [];

    BoneVertices = [None] * SkeletonSegments
    for i in range(0, SkeletonSegments):
            BoneVertices[i] = [0, ]
    
    #PapaVertex
    file.seek(OffsetVertices);
    for i in range(0, NumberOfVertices):
        if (VertexFormat == 7):
            CurrentVertex = struct.unpack('ffffffIffff', file.read(44));
            Vertex_PositionX.append(CurrentVertex[0]);
            Vertex_PositionY.append(CurrentVertex[1]);
            Vertex_PositionZ.append(CurrentVertex[2]);
            Vertex_NormalX.append(CurrentVertex[3]);
            Vertex_NormalY.append(CurrentVertex[4]);
            Vertex_NormalZ.append(CurrentVertex[5]);
            Vertex_U.append(CurrentVertex[7]);
            Vertex_V.append(CurrentVertex[8]);
        if (VertexFormat == 8):
            CurrentVertex = struct.unpack('fffIIfffff', file.read(40));
            Vertex_PositionX.append(CurrentVertex[0]);
            Vertex_PositionY.append(CurrentVertex[1]);
            Vertex_PositionZ.append(CurrentVertex[2]);

            if (CurrentVertex[4] < SkeletonSegments):
                BoneVertices[CurrentVertex[4]].append(i);
            else:
               print("Invalid Skeleton Segment for Vertex[" + str(i) + "]: " + str(CurrentVertex[4]))
                
            Vertex_NormalX.append(CurrentVertex[5]);
            Vertex_NormalY.append(CurrentVertex[6]);
            Vertex_NormalZ.append(CurrentVertex[7]);
            Vertex_U.append(CurrentVertex[8]);
            Vertex_V.append(CurrentVertex[9]);
        if (VertexFormat == 10):
            CurrentVertex = struct.unpack('ffffffffffffffff', file.read(64));
            Vertex_PositionX.append(CurrentVertex[0]);
            Vertex_PositionY.append(CurrentVertex[1]);
            Vertex_PositionZ.append(CurrentVertex[2]);
            Vertex_NormalX.append(CurrentVertex[3]);
            Vertex_NormalY.append(CurrentVertex[4]);
            Vertex_NormalZ.append(CurrentVertex[5]);
            Vertex_U.append(CurrentVertex[12]);
            Vertex_V.append(CurrentVertex[13]);

    for i in range(0, SkeletonSegments):
            BoneVertices[i].pop(0)
    
    #PapaIndicesHeader
    file.seek(OffsetIndicesHeader);
    PapaIndicesHeader = struct.unpack('IIqq', file.read(24));
    NumberOfIndices = PapaIndicesHeader[1];
    OffsetIndices = PapaIndicesHeader[3];

    Triangle_VertexA = [];
    Triangle_VertexB = [];
    Triangle_VertexC = [];

    #PapaTriangle
    file.seek(OffsetIndices);
    NumberOfTriangles = int(NumberOfIndices / 3)
    for i in range(0, NumberOfTriangles):
        CurrentTriangle = struct.unpack('HHH', file.read(6));
        Triangle_VertexA.append(CurrentTriangle[0]);
        Triangle_VertexB.append(CurrentTriangle[1]);
        Triangle_VertexC.append(CurrentTriangle[2]);

    #PapaSkeletonHeader
    if (OffsetSkeletonHeader > 0):
        file.seek(OffsetSkeletonHeader);
        PapaSkeletonHeader = struct.unpack('IIq', file.read(16));
        SkeletonSegments = PapaSkeletonHeader[0];
        OffsetSkeletonSegment = PapaSkeletonHeader[2];

        BoneSegment_BoneID = [];
        BoneSegment_ParentSegment = [];
        BoneSegment_X = [];
        BoneSegment_Y = [];
        BoneSegment_Z = [];
        BoneSegment_OffsetX = [];
        BoneSegment_OffsetY = [];
        BoneSegment_OffsetZ = [];
        BoneSegment_Rotation = [];

        #PapaSkeletonSegment
        file.seek(OffsetSkeletonSegment);
        for i in range(0, SkeletonSegments):
            CurrentSegment = struct.unpack('hhffffffffffffffffffffffffffffffff', file.read(132))
            BoneSegment_BoneID.append(CurrentSegment[0]);
            BoneSegment_ParentSegment.append(CurrentSegment[1]);
            BoneSegment_X.append(CurrentSegment[2]);
            BoneSegment_Y.append(CurrentSegment[3]);
            BoneSegment_Z.append(CurrentSegment[4]);

            A =(CurrentSegment[18],CurrentSegment[19],CurrentSegment[20],CurrentSegment[21])
            B =(CurrentSegment[22],CurrentSegment[23],CurrentSegment[24],CurrentSegment[25])
            C =(CurrentSegment[26],CurrentSegment[27],CurrentSegment[28],CurrentSegment[29])
            D =(CurrentSegment[14],CurrentSegment[15],CurrentSegment[16],CurrentSegment[17])
            mat = (A,B,C,D)
            BoneSegment_Rotation.append(mat)
            print(mat)
            BoneSegment_OffsetX.append(CurrentSegment[30]);
            BoneSegment_OffsetY.append(CurrentSegment[31]);
            BoneSegment_OffsetZ.append(CurrentSegment[32]);

    Bone_NameLength = [];
    Bone_Name = [];

    #PapaBonesHeader
    if (OffsetBonesHeader > 0):
        file.seek(OffsetBonesHeader);
        for i in range(0, NumberOfBones):
            CurrentBone = struct.unpack('QQ', file.read(16));
            Bone_NameLength.append(CurrentBone[0]);
            OffsetBone = CurrentBone[1];
            
            Restore = file.tell();
            #PapaBoneName
            file.seek(OffsetBone);
            Bone_Name.append(file.read(Bone_NameLength[i]));

            file.seek(Restore);

    #Data Manipulation to make importing easier.
    coords = [];
    faces = [];

    for i in range(0, NumberOfVertices):
        coords.append((Vertex_PositionX[i],Vertex_PositionY[i],Vertex_PositionZ[i]));

    for i in range(0, NumberOfTriangles):
        faces.append((Triangle_VertexA[i],Triangle_VertexB[i],Triangle_VertexC[i]));

    #Setup of Blender objects
    

    mesh = createMeshFromData('Mesh', (0,0,0), coords, faces);
    
    uvtex = mesh.data.uv_textures.new(name = 'UVMap')
    uvl = mesh.data.uv_layers.active.data[:]
    for i in range(0, NumberOfTriangles):
        uvl[i*3].uv[0] = Vertex_U[Triangle_VertexA[i]]
        uvl[i*3].uv[1] = 1 - Vertex_V[Triangle_VertexA[i]]
        uvl[i*3 + 1].uv[0] = Vertex_U[Triangle_VertexB[i]]
        uvl[i*3 + 1].uv[1] = 1 - Vertex_V[Triangle_VertexB[i]]
        uvl[i*3 + 2].uv[0] = Vertex_U[Triangle_VertexC[i]]
        uvl[i*3 + 2].uv[1] = 1 - Vertex_V[Triangle_VertexC[i]]

    armature = createArmatureFromData('Armature', (0,0,0));

    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.scene.cursor_location = (0.0,0.0,0.0)  
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    bpy.ops.object.mode_set(mode='EDIT')

    print(NumberOfBones)
    if (NumberOfBones >=3):
        armature.edit_bones.new(Bone_Name[0].decode("utf-8"));
        armature.edit_bones[Bone_Name[0].decode("utf-8")].head = (0,0,0)
        armature.edit_bones[Bone_Name[0].decode("utf-8")].tail = (0,0,1)
        armature.edit_bones.new(Bone_Name[1].decode("utf-8"));
        armature.edit_bones[Bone_Name[1].decode("utf-8")].head = (0,0,0)
        armature.edit_bones[Bone_Name[1].decode("utf-8")].tail = (0,0,1)
        armature.edit_bones.new(Bone_Name[2].decode("utf-8"));
        armature.edit_bones[Bone_Name[2].decode("utf-8")].head = (0,0,0)
        armature.edit_bones[Bone_Name[2].decode("utf-8")].tail = (0,0,1)
        
    for i in range(0, SkeletonSegments):
        BoneID = BoneSegment_BoneID[i];
        BoneName = Bone_Name[BoneID].decode("utf-8");
        ParentSegmentID = BoneSegment_ParentSegment[i];
        if (ParentSegmentID >= 0):
            ParentBoneID = BoneSegment_BoneID[ParentSegmentID];  
        
        armature.edit_bones.new(BoneName);
        
        #armature.edit_bones[BoneName].use_inherit_scale = True
        
        if (ParentSegmentID >= 0):
            armature.edit_bones[BoneName].parent = armature.edit_bones[Bone_Name[ParentBoneID].decode("utf-8")];

            armature.edit_bones[BoneName].head = (-BoneSegment_OffsetX[i],-BoneSegment_OffsetY[i],-BoneSegment_OffsetZ[i]);
            armature.edit_bones[BoneName].tail = (-BoneSegment_OffsetX[i],-BoneSegment_OffsetY[i],-BoneSegment_OffsetZ[i]+1);
##            armature.edit_bones[BoneName].head = (BoneSegment_X[i]-BoneSegment_OffsetX[ParentSegmentID],BoneSegment_Y[i]-BoneSegment_OffsetY[ParentSegmentID],BoneSegment_Z[i]-BoneSegment_OffsetZ[ParentSegmentID]);
##            armature.edit_bones[BoneName].tail = (BoneSegment_X[i]-BoneSegment_OffsetX[ParentSegmentID],BoneSegment_Y[i]-BoneSegment_OffsetY[ParentSegmentID],BoneSegment_Z[i]-BoneSegment_OffsetZ[ParentSegmentID]+1);
        else:
            armature.edit_bones[BoneName].head = (0,0,0);
            armature.edit_bones[BoneName].tail = (0,0,1);

        armature.edit_bones[BoneName].use_inherit_rotation = False
        armature.edit_bones[BoneName].use_local_location = False
        rotation = mathutils.Matrix(BoneSegment_Rotation[i])
                
        armature.edit_bones[BoneName].transform(rotation, True, True)

        vg = mesh.vertex_groups.new(BoneName)
        vg.add(BoneVertices[i], 1.0, "ADD")
        
    bpy.ops.object.mode_set(mode='OBJECT')
    return

def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
 
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
 
    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update(calc_tessface=True)
    return ob

def createArmatureFromData(name, origin):
    # Create armature and object
    #amt = bpy.data.armatures.new(name+'Amt')
    bpy.ops.object.add(type='ARMATURE', location=origin)
    ob = bpy.context.object
    ob.name = name
    amt = ob.data
    amt.name = name+'Amt'
    ob.show_name = True
 
    # Link object to scene and make active
    #scn = bpy.context.scene
    #scn.objects.active = ob
    ob.select = True
 
    return amt

def load(operator,context,filepath=""):
    load_papa(filepath,context)
    
    return {'FINISHED'}

