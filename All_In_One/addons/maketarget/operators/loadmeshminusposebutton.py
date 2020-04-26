import bpy
from ..utils import *
from ..error import *
from bpy.props import *

from ..maketarget import getMeshes, applyArmature, createNewMeshShape, checkRotationMatrix
from mathutils import Vector, Quaternion, Matrix

def loadStatueMinusPose(context):
    ob,statue,scn = getMeshes(context)
    ob,rig,posed = applyArmature(context)
    posed.name = "Temporary"

    nVerts = len(ob.data.vertices)

    relMats = {}
    for vg in ob.vertex_groups:
        try:
            pb = rig.pose.bones[vg.name]
        except KeyError:
            pb = None
        if pb:
            relMats[vg.index] = pb.matrix * pb.bone.matrix_local.inverted()
        else:
            print(("Skipping vertexgroup %s" % vg.name))
            relMats[vg.index] = Matrix().identity()

    svs = statue.data.vertices
    pvs = posed.data.vertices
    ovs = ob.data.vertices

    skey = createNewMeshShape(ob, statue.name, scn)
    relmat = Matrix()
    y = Vector((0,0,0,1))
    for v in ob.data.vertices:
        vn = v.index
        diff = svs[vn].co - pvs[vn].co
        if diff.length > 1e-4:
            relmat.zero()
            wsum = 0.0
            for g in v.groups:
                w = g.weight
                relmat += w * relMats[g.group]
                wsum += w
            factor = 1.0/wsum
            relmat *= factor

            y[:3] = svs[vn].co
            x = relmat.inverted() * y
            skey.data[vn].co = Vector(x[:3])

            z = relmat * x

            xdiff = skey.data[vn].co - ovs[vn].co

            if False and vn in [8059]:
                print(("\nVert", vn, diff.length, xdiff.length))
                print(("det", relmat.determinant()))
                print(("d (%.4f %.4f %.4f)" % tuple(diff)))
                print(("xd (%.4f %.4f %.4f)" % tuple(xdiff)))
                checkRotationMatrix(relmat)
                print(("Rel", relmat))
                print(("Inv", relmat.inverted()))

                s = pvs[vn].co
                print(("s ( %.4f  %.4f  %.4f)" % (s[0],s[1],s[2])))
                print(("x ( %.4f  %.4f  %.4f)" % (x[0],x[1],x[2])))
                print(("y ( %.4f  %.4f  %.4f)" % (y[0],y[1],y[2])))
                print(("z ( %.4f  %.4f  %.4f)" % (z[0],z[1],z[2])))
                o = ovs[vn].co
                print(("o (%.4f %.4f %.4f)" % (o[0],o[1],o[2])))
                print(("r (%.4f %.4f %.4f)" % tuple(skey.data[vn].co)))

                for g in v.groups:
                    print(("\nGrp %d %f %f" % (g.group, g.weight, relMats[g.group].determinant())))
                    print(("Rel", relMats[g.group]))

    #scn.objects.unlink(statue)
    scn.objects.unlink(posed)

class VIEW3D_OT_LoadMeshMinusPoseButton(bpy.types.Operator):
    bl_idname = "mh.load_statue_minus_pose"
    bl_label = "Load Statue Minus Pose"
    bl_description = "Make selected mesh a shapekey of active mesh, and subtract the current pose."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object
        #return (context.object and not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        setObjectMode(context)
        try:
            loadStatueMinusPose(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}