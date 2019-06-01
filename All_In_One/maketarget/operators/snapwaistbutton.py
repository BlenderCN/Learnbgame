import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import getSettings

def snapWaist(context):
    ob = context.object
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted:
        offset = settings.offsetVerts['Skirt']
    else:
        offset = 0

    nVerts = len(settings.skirtWaist)
    if len(settings.tightsWaist) != nVerts:
        raise RuntimeError("snapWaist: %d %d" % (len(settings.tightsWaist), nVerts))
    bpy.ops.object.mode_set(mode='OBJECT')
    skey = ob.data.shape_keys.key_blocks[-1]
    verts = skey.data
    for n in range(nVerts):
        verts[settings.skirtWaist[n]-offset].co = verts[settings.tightsWaist[n]-offset].co

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

class VIEW3D_OT_SnapWaistButton(bpy.types.Operator):
    bl_idname = "mh.snap_waist"
    bl_label = "Snap Skirt Waist"
    bl_description = "Snap the top row of skirt verts to the corresponding tight verts"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob.MhAffectOnly == 'Skirt' or not ob.MhIrrelevantDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            snapWaist(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}