
from . import xray_io
from . import object_format


def read_uv_maps(pr, mesh):
    vMaps = []
    for _ in range(pr.getf('<I')[0]):    # vMaps Count
        vMapName = pr.gets()
        vMapEntryDimension, hasDiscontigUVMap, vMapType, uvsCount = pr.getf('<3BI')
        if vMapType == 0:
            mesh.uv_map_name = vMapName
            currentUV = []
            prep_ff = pr.prep('ff')
            for __ in range(uvsCount):
                U, V = pr.getp(prep_ff)
                currentUV.append((U, 1 - V))
            vMaps.append(currentUV)
            pr.skip(uvsCount * 4)    # Vertices Not Used
            # vertices = pr.getf('<{0}I'.format(uvsCount))
            if hasDiscontigUVMap:
                pr.skip(uvsCount * 4)    # Triangles Not Used
                # triangles = pr.getf('<{0}I'.format(uvsCount))
        elif vMapType == 1:
            vMaps.append('WEIGHT')
            mesh.vertex_groups_names.append(vMapName)
            mesh.weights.append(pr.getf('<{0}f'.format(uvsCount)))
            mesh.weight_vertices.append(pr.getf('<{0}I'.format(uvsCount)))
            if hasDiscontigUVMap:
                pr.skip(uvsCount * 4)    # Triangles Not Used
                # triangles = pr.getf('<{0}I'.format(uvsCount))
    return vMaps


def read_vmap_references(pr):
    vMapIndices = []
    uvIndices = []
    prep_II = pr.prep('II')
    for _ in range(pr.getf('<I')[0]):    # vMap Reference Count
        vMapIndicesSet = []
        uvIndicesSet = []
        for __ in range(pr.getf('<B')[0]):    # Set Count
            vMapIndex, UVIndex = pr.getp(prep_II)
            vMapIndicesSet.append(vMapIndex)    # vMap Index
            uvIndicesSet.append(UVIndex)    # UV Index
        vMapIndices.append(vMapIndicesSet)
        uvIndices.append(uvIndicesSet)
    return vMapIndices, uvIndices


def read_triangles(pr, mesh):
    trianglesUV = []
    prep_6I = pr.prep('6I')
    trianglesCount = pr.getf('<I')[0]
    for _ in range(trianglesCount):
        vertex1, vMap1, vertex2, vMap2, vertex3, vMap3 = pr.getp(prep_6I)
        mesh.triangles.append((vertex1, vertex3, vertex2))
        trianglesUV.extend((vMap1, vMap3, vMap2))
    return trianglesCount, trianglesUV


def read_mesh(data, so):
    mesh = so.meshes[-1]
    cr = xray_io.ChunkedReader(data)
    chunks = object_format.Chunks.Mesh
    for chunkID, chunkData in cr:
        pr = xray_io.PackedReader(chunkData)
        if chunkID == chunks.VERSION:
            mesh.version = pr.getf('<H')[0]
            if mesh.version != object_format.CURRENT_MESH_VERSION:
                so.context.operator.report(
                    {'ERROR'},
                    'unsupported MESH format version {}'.format(mesh.version)
                    )
                break
        elif chunkID == chunks.MESH_NAME:
            mesh.name = pr.gets()
        elif chunkID == chunks.FLAGS:
            mesh.set_flags(pr.getf('<B')[0])
        elif chunkID == chunks.BOUNDING_BOX:
            pass    # Bounding Box Not Used
        elif chunkID == chunks.VERTICES:
            prep_3f = pr.prep('3f')
            for _ in range(pr.getf('<I')[0]):    # Vertices Count
                locationX, locationY, locationZ = pr.getp(prep_3f)
                mesh.vertices.append((locationX, locationZ, locationY))
        elif chunkID == chunks.TRIANGLES:
            trianglesCount, trianglesUV = read_triangles(pr, mesh)
        elif chunkID == chunks.VMAP_REFERENCES:
            vMapIndices, uvIndices = read_vmap_references(pr)
        elif chunkID == chunks.MATERIALS:
            for _ in range(pr.getf('<H')[0]):    # Materials Count
                materialName = pr.gets()
                # materials: trianglesIndices,       format: Triangles Count
                mesh.materials[materialName] = pr.getf('<{0}I'.format(pr.getf('<I')[0]))
        elif chunkID == chunks.OPTIONS:
            pass    # Mesh Option Not Used
        elif chunkID == chunks.UV_MAPS:
            vMaps = read_uv_maps(pr, mesh)
        elif chunkID == chunks.SMOOTH_GROUPS:
            prep_I = pr.prep('I')
            for _ in range(trianglesCount):
                mesh.smoothing_groups.append(pr.getp(prep_I)[0])    # Triangle Smoothing Group
    for triangleIndex in trianglesUV:
        if vMaps[vMapIndices[triangleIndex][0]] != 'WEIGHT':
            mesh.uvs.append(vMaps[vMapIndices[triangleIndex][0]][uvIndices[triangleIndex][0]])
