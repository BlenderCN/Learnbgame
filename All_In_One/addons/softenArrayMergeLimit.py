import bpy

# set soft value to mirror modifier's merge limit .
def softenMirrorModMergeLimit():
    SOFT_MERGE_THRESHOLD = .0340
    meshObjects = []
    for o in bpy.data.objects:
        if o.type =="MESH" or o.type == "CURVE":
            meshObjects.append(o)

    # why? this cannot work.
    #meshObjects = [o for o in bpy.data.objects if o.tyoe == "MESH"]

    for ob in meshObjects:
        mirrors = [mod for mod in ob.modifiers if mod.type == "MIRROR"]
        for m in mirrors:
            m.merge_threshold = SOFT_MERGE_THRESHOLD
    return
################### add on setting section###########################
bl_info = {
    "name": "Soften Mirror Modifier Merge Limit ",
    "category": "Learnbgame",
}

import bpy


class SoftenMirrorModMergeLimit(bpy.types.Operator):
    """soften mirror modifier merge limit"""
    bl_idname = "soften_mergelimit.comic"
    bl_label = "soften mirror merge limit"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        softenMirrorModMergeLimit()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SoftenMirrorModMergeLimit)


def unregister():
    bpy.utils.unregister_class(SoftenMirrorModMergeLimit)


if __name__ == "__main__":
    register()
