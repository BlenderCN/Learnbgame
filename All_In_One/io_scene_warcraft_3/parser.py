
import bpy
from . import classes
from . import constants
from . import importer
from . import binary


def parse_model(data, model):
    r = binary.Reader(data)
    model.name = r.gets(80)
    animationFileName = r.gets(260)
    boundsRadius = r.getf('<f')[0]
    minimumExtent = r.getf('<3f')
    maximumExtent = r.getf('<3f')
    blendTime = r.getf('<I')[0]


def parse_material_alpha(r):
    alpha = classes.WarCraft3GeosetTransformation()
    alpha.tracks_count = r.getf('<I')[0]
    alpha.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(alpha.tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<f')[0]    # alpha value
        alpha.times.append(time)
        alpha.values.append(value)
        if alpha.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<f')[0]
            outTan = r.getf('<f')[0]
    return alpha


def parse_material_texture_id(r):
    textureId = classes.WarCraft3GeosetTransformation()
    textureId.tracks_count = r.getf('<I')[0]
    textureId.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(textureId.tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<f')[0]    # texture id value
        textureId.times.append(time)
        textureId.values.append(value)
        if textureId.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<f')[0]
            outTan = r.getf('<f')[0]


def parse_layers(data):
    r = binary.Reader(data)
    chunkId = r.getid(constants.CHUNK_LAYER)
    layersCount = r.getf('<I')[0]
    layers = []
    for _ in range(layersCount):
        layer = classes.WarCraft3Layer()
        inclusiveSize = r.offset + r.getf('<I')[0]
        filterMode = r.getf('<I')[0]
        shadingFlags = r.getf('<I')[0]
        layer.texture_id = r.getf('<I')[0]
        textureAnimationId = r.getf('<I')[0]
        coordId = r.getf('<I')[0]
        alpha = r.getf('<f')[0]
        while r.offset < inclusiveSize:
            chunkId = r.getid(constants.SUB_CHUNKS_LAYER)
            if chunkId == constants.CHUNK_MATERIAL_ALPHA:
                layer.material_alpha = parse_material_alpha(r)
            elif chunkId == constants.CHUNK_MATERIAL_TEXTURE_ID:
                layer.material_texture_id = parse_material_texture_id(r)
        layers.append(layer)
    return layers


def parse_materials(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    while r.offset < dataSize:
        material = classes.WarCraft3Material()
        inclusiveSize = r.getf('<I')[0]
        priorityPlane = r.getf('<I')[0]
        flags = r.getf('<I')[0]
        layerChunkDataSize = inclusiveSize - 12
        if layerChunkDataSize > 0:
            layerChunkData = data[r.offset : r.offset + layerChunkDataSize]
            r.skip(layerChunkDataSize)
            material.layers = parse_layers(layerChunkData)
        model.materials.append(material)


def parse_textures(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    if dataSize % 268 != 0:
        raise Exception('bad Texture data (size % 268 != 0)')
    texturesCount = dataSize // 268
    for _ in range(texturesCount):
        texture = classes.WarCraft3Texture()
        texture.replaceable_id = r.getf('<I')[0]
        texture.image_file_name = r.gets(260)
        flags = r.getf('<I')[0]
        model.textures.append(texture)


def parse_geoset_scaling(r):
    scaling = classes.WarCraft3GeosetTransformation()
    scaling.tracks_count = r.getf('<I')[0]
    scaling.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(scaling.tracks_count):
        time = r.getf('<I')[0]
        values = r.getf('<3f')    # scaling values
        scaling.times.append(time)
        scaling.values.append(values)
        if scaling.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<3f')
            outTan = r.getf('<3f')
    return scaling


def parse_geoset_rotation(r):
    rotation = classes.WarCraft3GeosetTransformation()
    rotation.tracks_count = r.getf('<I')[0]
    rotation.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(rotation.tracks_count):
        time = r.getf('<I')[0]
        rotX, rotY, rotZ, rotW = r.getf('<4f')
        if rotation.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<4f')
            outTan = r.getf('<4f')
        values = (rotW, rotX, rotY, rotZ)    # rotation values
        rotation.times.append(time)
        rotation.values.append(values)
    return rotation


def parse_geoset_translation(r):
    translation = classes.WarCraft3GeosetTransformation()
    translation.tracks_count = r.getf('<I')[0]
    translation.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(translation.tracks_count):
        time = r.getf('<I')[0]
        values = r.getf('<3f')    # translation values
        translation.times.append(time)
        translation.values.append(values)
        if translation.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<3f')
            outTan = r.getf('<3f')
    return translation


def parse_node(r):
    node = classes.WarCraft3Node()
    inclusiveSize = r.offset + r.getf('<I')[0]
    node.name = r.gets(80)
    node.id = r.getf('<I')[0]
    node.parent = r.getf('<I')[0]
    if node.parent == 0xffffffff:
        node.parent = None
    flags = r.getf('<I')[0]
    while r.offset < inclusiveSize:
        chunkId = r.getid(constants.SUB_CHUNKS_NODE)
        if chunkId == constants.CHUNK_GEOSET_TRANSLATION:
            node.translations = parse_geoset_translation(r)
        elif chunkId == constants.CHUNK_GEOSET_ROTATION:
            node.rotations = parse_geoset_rotation(r)
        elif chunkId == constants.CHUNK_GEOSET_SCALING:
            node.scalings = parse_geoset_scaling(r)
    return node


def parse_bones(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    while r.offset < dataSize:
        bone = classes.WarCraft3Bone()
        bone.node = parse_node(r)
        bone.geoset_id = r.getf('<I')[0]
        geosetAnimationId = r.getf('<I')[0]
        model.nodes.append(bone)


def get_vertex_groups(matrixGroups, matrixGroupsSizes, matrixIndices):
    i = 0
    matrix = []
    for matrixGroupSize in matrixGroupsSizes:
        matrix.append(matrixIndices[i : i + matrixGroupSize])
        i += matrixGroupSize
    vertexGroups = []
    vertexGroupsIds = set()
    for matrixGroup in matrixGroups:
        vertexGroup = matrix[matrixGroup]
        vertexGroups.append(vertexGroup)
        for vertexGroupId in vertexGroup:
            vertexGroupsIds.add(vertexGroupId)
    vertexGroupsIds = list(vertexGroupsIds)
    vertexGroupsIds.sort()
    return vertexGroups, vertexGroupsIds


def parse_geometry(data):
    r = binary.Reader(data)
    mesh = classes.WarCraft3Mesh()
    mesh.name = 'temp'
    ############################################################################
    chunkId = r.getid(constants.CHUNK_VERTEX_POSITION)
    vertexCount = r.getf('<I')[0]
    for _ in range(vertexCount):
        vertexPositionX, vertexPositionY, vertexPositionZ = r.getf('<3f')
        mesh.vertices.append((vertexPositionX, vertexPositionY, vertexPositionZ))
    ############################################################################
    ################################# NOT USED #################################
    ############################################################################
    chunkId = r.getid(constants.CHUNK_VERTEX_NORMAL)
    normalsCount = r.getf('<I')[0]
    for _ in range(normalsCount):
        normal = r.getf('<3f')
    ############################################################################
    ################################# NOT USED #################################
    ############################################################################
    chunkId = r.getid(constants.CHUNK_FACE_TYPE_GROUP)
    faceTypeGroupsCount = r.getf('<I')[0]
    for _ in range(faceTypeGroupsCount):
        faceType = r.getf('<I')[0]
    ############################################################################
    ################################# NOT USED #################################
    ############################################################################
    chunkId = r.getid(constants.CHUNK_FACE_GROUP)
    faceGroupCount = r.getf('<I')[0]
    for _ in range(faceGroupCount):
        indexesCount = r.getf('<I')[0]
    ############################################################################
    chunkId = r.getid(constants.CHUNK_FACE)
    indicesCount = r.getf('<I')[0]
    if indicesCount % 3 != 0:
        raise Exception('bad indices (indicesCount % 3 != 0)')
    for _ in range(indicesCount // 3):
        vertexIndex1, vertexIndex2, vertexIndex3 = r.getf('<3H')
        mesh.triangles.append((vertexIndex1, vertexIndex2, vertexIndex3))
    ############################################################################
    chunkId = r.getid(constants.CHUNK_VERTEX_GROUP)
    matrixGroupsCount = r.getf('<I')[0]
    matrixGroups = []
    for _ in range(matrixGroupsCount):
        matrixGroup = r.getf('<B')[0]
        matrixGroups.append(matrixGroup)
    ############################################################################
    chunkId = r.getid(constants.CHUNK_MATRIX_GROUP)
    matrixGroupsSizesCount = r.getf('<I')[0]
    matrixGroupsSizes = []
    for _ in range(matrixGroupsSizesCount):
        matrixGroupSize = r.getf('<I')[0]
        matrixGroupsSizes.append(matrixGroupSize)
    ############################################################################
    chunkId = r.getid(constants.CHUNK_MATRIX_INDEX)
    matrixIndicesCount = r.getf('<I')[0]
    matrixIndices = []
    for _ in range(matrixIndicesCount):
        matrixIndex = r.getf('<I')[0]
        matrixIndices.append(matrixIndex)
    ############################################################################
    vertexGroups, vertexGroupsIds = get_vertex_groups(matrixGroups, matrixGroupsSizes, matrixIndices)
    mesh.vertex_groups = vertexGroups
    mesh.vertex_groups_ids = vertexGroupsIds
    mesh.material_id = r.getf('<I')[0]
    selectionGroup = r.getf('<I')[0]
    selectionFlags = r.getf('<I')[0]
    boundsRadius = r.getf('<f')[0]
    minimumExtent = r.getf('<3f')
    maximumExtent = r.getf('<3f')
    extentsCount = r.getf('<I')[0]
    for _ in range(extentsCount):
        boundsRadius = r.getf('<f')[0]
        minimumExtent = r.getf('<3f')
        maximumExtent = r.getf('<3f')
    ############################################################################
    ################################# NOT USED #################################
    ############################################################################
    chunkId = r.getid(constants.CHUNK_TEXTURE_VERTEX_GROUP)
    textureVertexGroupCount = r.getf('<I')[0]
    ############################################################################
    chunkId = r.getid(constants.CHUNK_VERTEX_TEXTURE_POSITION)
    vertexTexturePositionCount = r.getf('<I')[0]
    for _ in range(vertexTexturePositionCount):
        u, v = r.getf('<2f')
        mesh.uvs.append((u, 1 - v))
    ############################################################################
    return mesh


def parse_geosets(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    while r.offset < dataSize:
        inclusiveSize = r.getf('<I')[0]
        geoDataSize = inclusiveSize - 4
        geoData = data[r.offset : r.offset + geoDataSize]
        r.skip(geoDataSize)
        mesh = parse_geometry(geoData)
        model.meshes.append(mesh)


def parse_attachment_visibility(r):
    chunkId = r.getid(constants.CHUNK_ATTACHMENT_VISIBILITY)
    visibility = classes.WarCraft3GeosetTransformation()
    visibility.tracks_count = r.getf('<I')[0]
    visibility.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(visibility.tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<f')[0]    # visibility value
        visibility.times.append(time)
        visibility.values.append(value)
        if visibility.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<f')[0]
            outTan = r.getf('<f')[0]


def parse_attachment(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    attachment = classes.WarCraft3Attachment()
    attachment.node = parse_node(r)
    path = r.gets(260)
    attachmentId = r.getf('<I')[0]
    if r.offset < dataSize:
        parse_attachment_visibility(r)
    model.nodes.append(attachment)


def parse_attachments(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    while r.offset < dataSize:
        inclusiveSize = r.getf('<I')[0]
        attachDataSize = inclusiveSize - 4
        attachData = data[r.offset : r.offset + attachDataSize]
        r.skip(attachDataSize)
        parse_attachment(attachData, model)


def parse_helpers(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    while r.offset < dataSize:
        helper = classes.WarCraft3Helper()
        helper.node = parse_node(r)
        model.nodes.append(helper)


def parse_pivot_points(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    if dataSize % 12 != 0:
        raise Exception('bad Pivot Point data (size % 12 != 0)')
    pivotPointsCount = dataSize // 12
    for _ in range(pivotPointsCount):
        model.pivot_points.append(r.getf('<3f'))


def parse_tracks(r):
    tracksCount = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(tracksCount):
        time = r.getf('<I')[0]


def parse_events(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    while r.offset < dataSize:
        event = classes.WarCraft3Event()
        event.node = parse_node(r)
        if r.offset < dataSize:
            chunkId = r.gets(4)
            if chunkId == constants.CHUNK_TRACKS:
                parse_tracks(r)
            else:
                r.offset -= 4
        model.nodes.append(event)


def parse_collision_shapes(data, model):
    dataSize = len(data)
    r = binary.Reader(data)
    while r.offset < dataSize:
        collisionShape = classes.WarCraft3CollisionShape()
        collisionShape.node = parse_node(r)
        type = r.getf('<I')[0]
        if type == 0:
            verticesCount = 2
        elif type == 2:
            verticesCount = 1
        else:
            raise Exception('UNSUPPORTED COLLISION SHAPE TYPE:', type)
        for _ in range(verticesCount):
            position = r.getf('<3f')
        if type == 2:
            boundsRadius = r.getf('<f')[0]
        model.nodes.append(collisionShape)


def parse_sequences(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    if dataSize % 132 != 0:
        raise Exception('bad sequence data (size % 132 != 0)')
    sequenceCount = dataSize // 132
    for _ in range(sequenceCount):
        sequence = classes.WarCraft3Sequence()
        sequence.name = r.gets(80)
        sequence.interval_start = r.getf('<I')[0]
        sequence.interval_end = r.getf('<I')[0]
        moveSpeed = r.getf('<f')[0]
        flags = r.getf('<I')[0]
        rarity = r.getf('<f')[0]
        syncPoint = r.getf('<I')[0]
        boundsRadius = r.getf('<f')[0]
        minimumExtent = r.getf('<3f')
        maximumExtent = r.getf('<3f')
        model.sequences.append(sequence)


def parse_geoset_color(r):
    color = classes.WarCraft3GeosetTransformation()
    color.tracks_count = r.getf('<I')[0]
    color.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(color.tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<3f')    # color value
        color.times.append(time)
        color.values.append(value)
        if color.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<3f')
            outTan = r.getf('<3f')
    return color


def parse_geoset_alpha(r):
    alpha = classes.WarCraft3GeosetTransformation()
    alpha.tracks_count = r.getf('<I')[0]
    alpha.interpolation_type = r.getf('<I')[0]
    globalSequenceId = r.getf('<I')[0]
    for _ in range(alpha.tracks_count):
        time = r.getf('<I')[0]
        value = r.getf('<f')[0]    # alpha value
        alpha.times.append(time)
        alpha.values.append(value)
        if alpha.interpolation_type > constants.INTERPOLATION_TYPE_LINEAR:
            inTan = r.getf('<f')[0]
            outTan = r.getf('<f')[0]
    return alpha


def parse_geoset_animations(data, model):
    r = binary.Reader(data)
    dataSize = len(data)
    while r.offset < dataSize:
        geosetAnimation = classes.WarCraft3GeosetAnimation()
        inclusiveSize = r.offset + r.getf('<I')[0]
        alpha = r.getf('<f')[0]
        flags = r.getf('<I')[0]
        color = r.getf('<3f')
        geosetAnimation.geoset_id = r.getf('<I')[0]
        while r.offset < inclusiveSize:
            chunkId = r.getid(constants.SUB_CHUNKS_GEOSET_ANIMATION)
            if chunkId == constants.CHUNK_GEOSET_COLOR:
                geosetAnimation.animation_color = parse_geoset_color(r)
            elif chunkId == constants.CHUNK_GEOSET_ALPHA:
                geosetAnimation.animation_alpha = parse_geoset_alpha(r)
        if not geosetAnimation.animation_color:
            geosetColor = classes.WarCraft3GeosetTransformation()
            geosetColor.tracks_count = 1
            geosetColor.interpolation_type = constants.INTERPOLATION_TYPE_NONE
            geosetColor.times = [0, ]
            geosetColor.values = [color, ]
            geosetAnimation.animation_color = geosetColor
        if not geosetAnimation.animation_alpha:
            geosetAlpha = classes.WarCraft3GeosetTransformation()
            geosetAlpha.tracks_count = 1
            geosetAlpha.interpolation_type = constants.INTERPOLATION_TYPE_NONE
            geosetAlpha.times = [0, ]
            geosetAlpha.values = [alpha, ]
            geosetAnimation.animation_alpha = geosetAlpha
        model.geoset_animations.append(geosetAnimation)


def parse_version(data):
    r = binary.Reader(data)
    version = r.getf('<I')[0]
    if version != constants.MDX_CURRENT_VERSION:
        raise Exception('unsupported MDX format version: {0}'.format(version))


def parse_mdx(data, importProperties):
    dataSize = len(data)
    r = binary.Reader(data)
    r.getid(constants.CHUNK_MDX_MODEL)
    model = classes.WarCraft3Model()
    while r.offset < dataSize:
        chunkId = r.getid(constants.SUB_CHUNKS_MDX_MODEL, debug=True)
        chunkSize = r.getf('<I')[0]
        chunkData = data[r.offset : r.offset + chunkSize]
        r.skip(chunkSize)
        if chunkId == constants.CHUNK_VERSION:
            parse_version(chunkData)
        elif chunkId == constants.CHUNK_GEOSET:
            parse_geosets(chunkData, model)
        elif chunkId == constants.CHUNK_TEXTURE:
            parse_textures(chunkData, model)
        elif chunkId == constants.CHUNK_MATERIAL:
            parse_materials(chunkData, model)
        elif chunkId == constants.CHUNK_MODEL:
            parse_model(chunkData, model)
        elif chunkId == constants.CHUNK_BONE:
            parse_bones(chunkData, model)
        elif chunkId == constants.CHUNK_PIVOT_POINT:
            parse_pivot_points(chunkData, model)
        elif chunkId == constants.CHUNK_HELPER:
            parse_helpers(chunkData, model)
        elif chunkId == constants.CHUNK_ATTACHMENT:
            parse_attachments(chunkData, model)
        elif chunkId == constants.CHUNK_EVENT_OBJECT:
            parse_events(chunkData, model)
        elif chunkId == constants.CHUNK_COLLISION_SHAPE:
            parse_collision_shapes(chunkData, model)
        elif chunkId == constants.CHUNK_SEQUENCE:
            parse_sequences(chunkData, model)
        elif chunkId == constants.CHUNK_GEOSET_ANIMATION:
            parse_geoset_animations(chunkData, model)
    importer.load_warcraft_3_model(model, importProperties)


def load_mdx(importProperties):
    mdxFile = open(importProperties.mdx_file_path, 'rb')
    mdxFileData = mdxFile.read()
    mdxFile.close()
    parse_mdx(mdxFileData, importProperties)
