import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import getSettings

def straightenSkirt(context):
    ob = context.object
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted:
        offset = settings.offsetVerts['Skirt']
    else:
        offset = 0

    bpy.ops.object.mode_set(mode='OBJECT')
    skey = ob.data.shape_keys.key_blocks[-1]
    verts = skey.data

    for col in settings.XYSkirtColumns:
        xsum = 0.0
        ysum = 0.0
        for vn in col:
            xsum += verts[vn-offset].co[0]
            ysum += verts[vn-offset].co[1]
        x = xsum/len(col)
        y = ysum/len(col)
        for vn in col:
            verts[vn-offset].co[0] = x
            verts[vn-offset].co[1] = y

    for row in settings.ZSkirtRows:
        zsum = 0.0
        for vn in row:
            zsum += verts[vn-offset].co[2]
        z = zsum/len(row)
        for vn in row:
            verts[vn-offset].co[2] = z

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

class VIEW3D_OT_StraightenSkirtButton(bpy.types.Operator):
    bl_idname = "mh.straighten_skirt"
    bl_label = "Straighten Skirt"
    bl_description = "Make (the right side of) the skirt perfectly straight."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob.MhAffectOnly == 'Skirt' or not ob.MhIrrelevantDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            straightenSkirt(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}