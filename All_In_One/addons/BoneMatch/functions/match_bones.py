import bpy
from .utils import *

def match_bones(rig,metarig):
    metarig_values = armature_info(metarig)
    rig_values = armature_info(rig)

    ##### EDIT BONES
    active_object = bpy.context.scene.objects.active
    mode = active_object.mode
    bpy.ops.object.mode_set(mode= 'OBJECT')
    bpy.context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode= 'EDIT')
    #####

    for bone in rig.data.edit_bones :

        if bone.get('match') :

            match = bone["match"]

            ref_tail = metarig_values.get(match['ref_tail']) if match.get('ref_tail') else None
            ref_head = metarig_values.get(match['ref_head']) if match.get('ref_head') else None
            ref_roll = metarig_values.get(match['ref_roll']) if match.get('ref_roll') else None


            if ref_tail and ref_head :

                #bpy.context.scene.cursor_location = ref_tail.head_local
                #bone.tail = ref_tail.vector * match["tail"]+ref_tail.head_local
                #bone.head = ref_head.vector* match["head"]+ref_head.head_local
                bone.head = ref_head["head"] + ref_head["vector"]*match["head"]
                bone.tail = ref_tail["head"] + ref_tail["vector"]*match["tail"]


            elif ref_tail and not ref_head :


                bone.head = ref_tail["vector"] * match["tail"]+ref_tail['head'] - bone.vector

                bone.tail = ref_tail["vector"]  * match["tail"]+ref_tail['head']
                #bone.head = ref_tail.vector * match["tail"]+bone.head


            elif ref_head and not ref_tail:

                bone.tail = ref_head["vector"] * match["head"]+ref_head["head"] + bone.vector
                bone.head = ref_head["head"]+ ref_head["vector"]*match["head"]



            if ref_roll :
                bone.roll = ref_roll['roll'] - match["roll"]

    bpy.ops.object.mode_set(mode= 'OBJECT')
    bpy.context.scene.objects.active = active_object
    bpy.ops.object.mode_set(mode= mode)

    #bpy.ops.object.mode_set(mode= 'OBJECT')
    #bpy.context.scene.objects.active = ob

    # reset stretch_to constraints
    for bone in rig.pose.bones :
        for c in bone.constraints :
            if c.type == "STRETCH_TO" :
                c.rest_length = bone.bone.length

            if c.type == "CHILD_OF" :
                bone = c.target.pose.bones.get(c.subtarget)
                c.inverse_matrix = bone.matrix.inverted()
