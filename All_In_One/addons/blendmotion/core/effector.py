import bpy
from blendmotion.error import OperatorError

EFFECTOR_TYPES = ('world', 'local', 'none')

def is_effector(obj):
    """
        obj: Object
    """

    if obj.type != 'MESH':
        return False

    if obj.data.bm_rotation_effector != 'none':
        return True

    if obj.data.bm_location_effector != 'none':
        return True

    return False


def mark_as_location_effector(mesh, effector_type, weight=1.0):
    """
        mesh: Mesh
        weight: float
    """

    mesh.bm_location_effector = effector_type
    mesh.bm_location_effector_weight = weight

def mark_as_rotation_effector(mesh, effector_type, weight=1.0):
    """
        mesh: Mesh
        weight: float
    """

    mesh.bm_rotation_effector = effector_type
    mesh.bm_rotation_effector_weight = weight

def unmark_as_effector(mesh):
    """
        mesh: Mesh
    """

    mesh.bm_rotation_effector = 'none'
    mesh.bm_location_effector = 'none'


def register():
    effector_types_enum = [(t, t, t) for t in EFFECTOR_TYPES]
    bpy.types.Mesh.bm_rotation_effector = bpy.props.EnumProperty(name='Rotation Effector', items=effector_types_enum, default='none')
    bpy.types.Mesh.bm_rotation_effector_weight = bpy.props.FloatProperty(name='Rotation Weight', min=0.0, max=1.0, default=1.0)
    bpy.types.Mesh.bm_location_effector = bpy.props.EnumProperty(name='Location Effector', items=effector_types_enum, default='none')
    bpy.types.Mesh.bm_location_effector_weight = bpy.props.FloatProperty(name='Location Weight', min=0.0, max=1.0, default=1.0)

def unregister():
    pass
