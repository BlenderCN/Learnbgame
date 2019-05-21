# Vertex element semantics, used to identify the meaning of vertex buffer
# contents
VES_POSITION = 1
VES_BLEND_WEIGHTS = 2
VES_BLEND_INDICES = 3
VES_NORMAL = 4
VES_DIFFUSE = 5
VES_SPECULAR = 6
VES_TEXTURE_COORDINATES = 7
VES_BINORMAL = 8
VES_TANGENT = 9

# vertex buffer component types
VET_FLOAT1 = 0
VET_FLOAT2 = 1
VET_FLOAT3 = 2
VET_FLOAT4 = 3
# alias to more specific colour type - use the current rendersystem's colour packing
VET_COLOUR = 4
VET_SHORT1 = 5
VET_SHORT2 = 6
VET_SHORT3 = 7
VET_SHORT4 = 8
VET_UBYTE4 = 9
# D3D style compact colour
VET_COLOUR_ARGB = 10
# GL style compact colour
VET_COLOUR_ABGR = 11

type2size = {
        VET_FLOAT1 : 4,
        VET_FLOAT2 : 8,
        VET_FLOAT3 : 12,
        VET_FLOAT4 : 16,
        # alias to more specific colour type - use the current rendersystem's colour packing
        VET_COLOUR : 12, # ???
        VET_SHORT1 : 2,
        VET_SHORT2 : 4,
        VET_SHORT3 : 6,
        VET_SHORT4 : 8,
        VET_UBYTE4 : 4
        # D3D style compact colour
  #      VET_COLOUR_ARGB = 10,
        # GL style compact colour
  #      VET_COLOUR_ABGR = 11

}


class MeshChunkID(object):
        Header = 0x1000
        Mesh = 0x3000
        SubMesh = 0x4000
        SubMeshOperation = 0x4010
        SubMeshBoneAssignment = 0x4100
        Geometry = 0x5000
        GeometryVertexDeclaration = 0x5100
        GeometryNormals = 0x5100
        GeometryVertexElement = 0x5110
        GeometryVertexBuffer = 0x5200
        GeometryColors = 0x5200
        GeometryVertexBufferData = 0x5210
        GeometryTexCoords = 0x5300
        MeshSkeletonLink = 0x6000
        MeshBoneAssignment = 0x7000
        MeshLOD = 0x8000
        MeshLODUsage = 0x8100
        MeshLODManual = 0x8110
        MeshLODGenerated = 0x8120
        MeshBounds = 0x9000
        SubMeshNameTable = 0xA000
        SubMeshNameTableElement = 0xA100
        EdgeLists = 0xB000
        EdgeListLOD = 0xB100
        EdgeListGroup = 0xB110

MeshCids = [MeshChunkID.Geometry, MeshChunkID.SubMesh,
            MeshChunkID.MeshSkeletonLink, MeshChunkID.MeshBoneAssignment,
            MeshChunkID.MeshLOD, MeshChunkID.MeshBounds,
            MeshChunkID.SubMeshNameTable, MeshChunkID.EdgeLists]

GeomCids = [MeshChunkID.GeometryVertexDeclaration,
            MeshChunkID.GeometryVertexBuffer]

SubMeshCids = [MeshChunkID.MeshBoneAssignment, MeshChunkID.SubMeshOperation]
