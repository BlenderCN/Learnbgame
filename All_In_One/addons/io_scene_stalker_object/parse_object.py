
from . import xray_io
from . import object_format
from . import parse_object_mesh
from . import parse_object_bone


def read_lod_reference(data, so):
    pr = xray_io.PackedReader(data)
    so.lod_reference = pr.gets()


def read_motion_reference(data, so):
    pr = xray_io.PackedReader(data)
    so.motion_reference = pr.gets()


def read_bone_partitions(data):
    pr = xray_io.PackedReader(data)
    partitionsCount = pr.getf('<I')[0]
    for _ in range(partitionsCount):
        partitionName = pr.gets()
        bonesCount = pr.getf('<I')[0]
        for __ in range(bonesCount):
            boneName = pr.gets()


def read_authors(data, so):
    pr = xray_io.PackedReader(data)
    so.creator = pr.gets()
    so.create_time = pr.getf('<I')[0]
    so.editor = pr.gets()
    so.edit_time = pr.getf('<I')[0]


def read_bones(data, so):
    cr = xray_io.ChunkedReader(data)
    for boneID, boneData in cr:
        parse_object_bone.read_bone(boneData, so)


def read_actor_transforms(data, so):
    pr = xray_io.PackedReader(data)
    position = pr.getf('<3f')
    rotation = pr.getf('<3f')
    so.position = position[0], position[2], position[1]
    so.rotation = rotation[0], rotation[2], rotation[1]


def read_motions(data):
    pr = xray_io.PackedReader(data)
    motionsCount = pr.getf('<I')[0]
    for _ in range(motionsCount):
        motionName = pr.gets()
        frameStart, frameEnd = pr.getf('<II')
        FPS = pr.getf('f')[0]
        motionVersion = pr.getf('<H')[0]
        if motionVersion == object_format.CURRENT_MOTION_VERSION:
            motionFlags = pr.getf('B')[0]
            bonePartitionOrStartBone = pr.getf('<H')[0]
            speed = pr.getf('<f')[0]
            accrue = pr.getf('<f')[0]
            falloff = pr.getf('<f')[0]
            power = pr.getf('<f')[0]
            bonesCount = pr.getf('<H')[0]
            for __ in range(bonesCount):
                boneName = pr.gets()
                boneFlags = pr.getf('<B')[0]
                for ___ in range(6):
                    behaviours = pr.getf('<BB')
                    keysCount = pr.getf('<H')[0]
                    for ____ in range(keysCount):
                        value = pr.getf('<f')[0]
                        time = pr.getf('<f')[0] * FPS
                        shape = pr.getf('<B')[0]


def read_user_data(data, so):
    pr = xray_io.PackedReader(data)
    so.user_data = pr.gets()


def read_meshes(data, so):
    cr = xray_io.ChunkedReader(data)
    for meshID, meshData in cr:
        so.meshes.create()
        parse_object_mesh.read_mesh(meshData, so)


def read_materials(data, so):
    pr = xray_io.PackedReader(data)
    materialsCount = pr.getf('<I')[0]
    for _ in range(materialsCount):
        materialName = pr.gets()
        so.materials[materialName] = so.Material()
        so.materials[materialName].name = materialName
        so.materials[materialName].engine_shader = pr.gets()
        so.materials[materialName].compiler_shader = pr.gets()
        so.materials[materialName].game_material = pr.gets()
        so.materials[materialName].texture = pr.gets()
        vMapName = pr.gets()
        so.materials[materialName].two_sided = bool(pr.getf('<I')[0])
        fvf = pr.getf('<I')[0]
        tc = pr.getf('<I')[0]


def read_object_flags(data, so):
    pr = xray_io.PackedReader(data)
    objectFlags = pr.getf('<I')[0]
    so.object_type = object_format.OBJECT_TYPES.get(objectFlags)
    so.flags.dynamic = bool(objectFlags & 0x01)
    so.flags.progressive = bool(objectFlags & 0x02)
    so.flags.using_lod = bool(objectFlags & 0x04)
    so.flags.hom = bool(objectFlags & 0x08)
    so.flags.multiple_usage = bool(objectFlags & 0x10)
    so.flags.sound_occluder = bool(objectFlags & 0x20)
    if so.object_type == None:
        so.object_type = 'OTHER'


def read_object_version(data, so):
    pr = xray_io.PackedReader(data)
    so.version = pr.getf('<H')[0]


def read_body(data, so):
    cr = xray_io.ChunkedReader(data)
    chunks = object_format.Chunks.Object
    for chunkID, chunkData in cr:
        if chunkID == chunks.VERSION:
            read_object_version(chunkData, so)
            if so.version != object_format.CURRENT_OBJECT_VERSION:
                so.context.operator.report({'ERROR'}, 'unsupported OBJECT format version {}'.format(ObjectVersion))
                break
        elif chunkID == chunks.FLAGS:
            read_object_flags(chunkData, so)
        elif chunkID == chunks.MATERIALS:
            read_materials(chunkData, so)
        elif chunkID == chunks.MESHES:
            read_meshes(chunkData, so)
        elif chunkID == chunks.USER_DATA:
            read_user_data(chunkData, so)
        elif chunkID == chunks.MOTIONS:
            read_motions(chunkData)
        elif chunkID == chunks.ACTOR_TRANSFORM:
            read_actor_transforms(chunkData, so)
        elif chunkID == chunks.BONES:
            read_bones(chunkData, so)
        elif chunkID == chunks.AUTHORS:
            read_authors(chunkData, so)
        elif chunkID == chunks.BONE_PARTITIONS:
            read_bone_partitions(chunkData)
        elif chunkID == chunks.MOTION_REFERENCE:
            read_motion_reference(chunkData, so)
        elif chunkID == chunks.LOD_REFERENCE:
            read_lod_reference(chunkData, so)


def read_object(data, so):
    cr = xray_io.ChunkedReader(data)
    for chunkID, chunkData in cr:
        if chunkID == object_format.Chunks.File.BODY:
            read_body(chunkData, so)
