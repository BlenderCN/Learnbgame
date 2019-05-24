import bpy

# set soft value to array modifier's merge limit .
def softenArrayModMergeLimit():
    SOFT_MERGE_THRESHOLD = .0340
    meshObjects = []
    for o in bpy.data.objects:
        if o.type =="MESH":
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
    "name": "Soften Array Modifier Merge Limit ",
    "category": "Learnbgame",
}

import bpy


class SoftenArrayModMergeLimit(bpy.types.Operator):
    """soften array modifier merge limit"""
    bl_idname = "soften_mergelimit.comic"
    bl_label = "soften array merge limit"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        softenArrayModMergeLimit()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SoftenArrayModMergeLimit)


def unregister():
    bpy.utils.unregister_class(SoftenArrayModMergeLimit)


if __name__ == "__main__":
    register()
