import bpy
import mathutils


def regOp(reg, op):
    if reg:
        bpy.utils.register_class(op)
    else:
        bpy.utils.unregister_class(op)

def toMeshMode():
    bpy.ops.object.mode_set(mode = 'EDIT')

def toObjectMode():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def getSecondarySel():
    act = bpy.context.active_object
    for obj in bpy.data.objects:
        if not obj.type == 'MESH':
            continue
        if not obj == act:
            return obj
    raise Exception('Secondary mesh is not exist')

def getModifiedMesh(obj):
    apply_modifiers = True
    settings = 'PREVIEW'
    om = obj.to_mesh(bpy.context.scene, apply_modifiers, settings)
    return om

def getVertPosW(obj, v):
    return obj.matrix_world * v.co

def getVertPosWSP(obj, v):
    vw = mathutils.Vector((v.co[0], v.co[1], v.co[2], 1.0))
    return obj.matrix_world * vw
