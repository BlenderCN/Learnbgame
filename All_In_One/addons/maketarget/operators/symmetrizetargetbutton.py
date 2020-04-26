import bpy
from ..utils import *
from ..error import *
from bpy.props import StringProperty
from ..maketarget import Mid2Mid, Left2Right
from .. import utils

def symmetrizeTarget(context, left2right, mirror):
    #pairing = CPairing().setup(context, False)

    ob = context.object
    scn = context.scene
    if not utils.isTarget(ob):
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = ob.active_shape_key.data
    nVerts = len(verts)

    for vn in list(Mid2Mid.keys()):
        if vn >= nVerts:
            break
        v = verts[vn]
        v.co[0] = 0

    for (lvn,rvn) in list(Left2Right.items()):
        if lvn >= nVerts or rvn >= nVerts:
            break
        lv = verts[lvn].co
        rv = verts[rvn].co
        if mirror:
            tv = rv.copy()
            verts[rvn].co = (-lv[0], lv[1], lv[2])
            verts[lvn].co = (-tv[0], tv[1], tv[2])
        elif left2right:
            rv[0] = -lv[0]
            rv[1] = lv[1]
            rv[2] = lv[2]
        else:
            lv[0] = -rv[0]
            lv[1] = rv[1]
            lv[2] = rv[2]

    bverts = ob.data.vertices
    selected = {}
    for v in bverts:
        selected[v.index] = v.select

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    for vn in list(Mid2Mid.keys()):
        if vn >= nVerts:
            break
        bverts[vn].select = selected[vn]

    for (lvn,rvn) in list(Left2Right.items()):
        if lvn >= nVerts or rvn >= nVerts:
            break
        if mirror:
            bverts[lvn].select = selected[rvn]
            bverts[rvn].select = selected[lvn]
        elif left2right:
            bverts[lvn].select = selected[lvn]
            bverts[rvn].select = selected[lvn]
        else:
            bverts[lvn].select = selected[rvn]
            bverts[rvn].select = selected[rvn]

    print("Target symmetrized")
    return

class VIEW3D_OT_SymmetrizeTargetButton(bpy.types.Operator):
    bl_idname = "mh.symmetrize_target"
    bl_label = "Symmetrize"
    bl_description = "Symmetrize or mirror active target"
    bl_options = {'UNDO'}
    action = StringProperty()

    def execute(self, context):
        try:
            setObjectMode(context)
            symmetrizeTarget(context, (self.action=="Right"), (self.action=="Mirror"))
        except MHError:
            handleMHError(context)
        return{'FINISHED'}