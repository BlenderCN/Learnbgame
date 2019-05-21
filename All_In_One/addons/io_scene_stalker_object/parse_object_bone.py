
from . import xray_io
from . import object_format


def read_friction(pr):
    friction = pr.getf('<f')[0]


def read_break_params(pr):
    breakForce, breakTorque = pr.getf('<ff')


def read_ik_flags(pr):
    ik_flags = pr.getf('<I')[0]


def read_mass_params(pr):
    mass = pr.getf('<f')[0]
    centerOfMass = pr.getf('<3f')


def read_ik_joint(pr):
    jointType = pr.getf('<I')[0]
    for _ in range(3):
        limitRange = pr.getf('<ff')
        limitSpringFactor = pr.getf('<f')[0]
        limitDampingFactor = pr.getf('<f')[0]
    springFactor = pr.getf('<f')[0]
    dampingFactor = pr.getf('<f')[0]


def read_shape(pr):
    shapeTypeNames = {0: 'undefined', 1: 'box', 2: 'sphere', 3: 'cylinder' }
    shapeType = pr.getf('<H')[0]
    shapeTypeName = shapeTypeNames.get(shapeType)
    boneShapeFlags = pr.getf('<H')[0]
    boxRotate = pr.getf('<9f')
    boxTranslate = pr.getf('<3f')
    boxHalfsize = pr.getf('<3f')
    sphereCenter = pr.getf('<3f')
    sphereRadius = pr.getf('<f')[0]
    cylinderCenter = pr.getf('<3f')
    cylinderDirection = pr.getf('<3f')
    cylinderHeight = pr.getf('<f')[0]
    cylinderRadius = pr.getf('<f')[0]


def read_bone_material(pr):
    boneMaterial = pr.gets()


def read_bind_pose(pr, so):
    bindPosition = pr.getf('<3f')
    bindRotation = pr.getf('<3f')
    bindLength = pr.getf('<f')
    so.skelet.bones[-1].position = bindPosition[0], bindPosition[2], bindPosition[1]
    so.skelet.bones[-1].rotation = bindRotation[0], bindRotation[2], bindRotation[1]


def read_def_b(pr):
    boneName = pr.gets()


def read_def_a(pr, so):
    boneName = pr.gets()
    parentName = pr.gets()
    so.skelet.bones[-1].name = boneName.lower()
    so.skelet.bones[-1].parent = parentName.lower()
    vMapName = pr.gets()


def read_bone_version(pr):
    boneVersion = pr.getf('<H')[0]
    return boneVersion


def read_bone(data, so):
    cr = xray_io.ChunkedReader(data)
    defType = 0
    chunks = object_format.Chunks.Bone
    for chunkID, chunkData in cr:
        pr = xray_io.PackedReader(chunkData)
        if chunkID == chunks.VERSION:
            boneVersion = read_bone_version(pr)
            if boneVersion != object_format.CURRENT_BONE_VERSION:
                so.context.operator.report({'ERROR'}, 'unsupported BONE format version {}'.format(boneVersion))
                break
            else:
                so.skelet.bones.create()
        elif chunkID == chunks.DEF:
            if defType == 0:
                read_def_a(pr, so)
                defType = 1
            else:
                read_def_b(pr)
        elif chunkID == chunks.BIND_POSE:
            read_bind_pose(pr, so)
        elif chunkID == chunks.MATERIAL:
            read_bone_material(pr)
        elif chunkID == chunks.SHAPE:
            read_shape(pr)
        elif chunkID == chunks.IK_JOINT:
            read_ik_joint(pr)
        elif chunkID == chunks.MASS_PARAMS:
            read_mass_params(pr)
        elif chunkID == chunks.IK_FLAGS:
            read_ik_flags(pr)
        elif chunkID == chunks.BREAK_PARAMS:
            read_break_params(pr)
        elif chunkID == chunks.FRICTION:
            read_friction(pr)
