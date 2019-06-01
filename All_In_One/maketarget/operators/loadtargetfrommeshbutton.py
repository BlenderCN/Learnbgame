import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import getMeshes, createNewMeshShape

def loadTargetFromMesh(context):
    ob,trg,scn = getMeshes(context)
    scn.objects.active = trg
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    skey = createNewMeshShape(ob, trg.name, scn)
    nVerts = len(ob.data.vertices)
    for v in trg.data.vertices[0:nVerts]:
        skey.data[v.index].co = v.co
    scn.objects.unlink(trg)

class VIEW3D_OT_LoadTargetFromMeshButton(bpy.types.Operator):
    bl_idname = "mh.load_target_from_mesh"
    bl_label = "Load Target From Mesh"
    bl_description = "Make selected mesh a shapekey of active mesh."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object
        #return (context.object and not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        setObjectMode(context)
        try:
            loadTargetFromMesh(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}

