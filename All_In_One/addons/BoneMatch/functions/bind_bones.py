import bpy
from .utils import *
from mathutils.geometry import intersect_point_line
from mathutils import Vector

### a simplififer à mort!!!!!!!!!
def bind_bones(rig,metarig):
    metarig_values = armature_info(metarig)
    rig_values = armature_info(rig)



    for bone_name,bone in rig_values.items() :
        match = {}

        for ref_bone_name,ref_bone in metarig_values.items() :

            head_intersection = intersect(bone['head'],ref_bone)
            tail_intersection = intersect(bone['tail'],ref_bone)

            if head_intersection is not None :
                if not 'head' in match or 'head' in match and abs(head_intersection) < abs(match['head']) :
                    match['ref_head'] = ref_bone_name
                    match['head'] = head_intersection

            if tail_intersection is not None :
                if not 'tail' in match or 'tail' in match and abs(tail_intersection) < abs(match['tail']) :
                    match['ref_tail'] = ref_bone_name
                    match['tail'] = tail_intersection


        if "tail" in match and "head" in match:
            if match['ref_tail'] == match['ref_head'] :
                roll_bone_name = match['ref_tail']

            else :
                roll_bone_name = find_ref_roll(metarig_values,bone)

            ref_roll_bone = metarig_values[roll_bone_name]

            roll = ref_roll_bone['roll']- bone['roll']

            match['roll'] =  roll
            match['ref_roll'] = roll_bone_name

        rig.data.bones[bone_name]['match'] = match

    """
        for ref_bone_name,ref_bone in metarig_values.items() :
            if intersect(bone["head"],ref_bone):
                better_match = False
                if match.get("ref_tail") :
                    if match.get("ref_head") and match["ref_tail"]==match["ref_head"] :
                        pass
                    elif ref_bone_name==match["ref_tail"] :
                        match['ref_head'] = ref_bone_name
                        head_vector = (bone['head']-ref_bone['head'])

                        if inside(bone['head'],ref_bone)  :
                            match['head'] = head_vector.length/ref_bone['length']
                        else :
                            match['head'] = -head_vector.length/ref_bone['length']

                        tmp_head = ref_bone
                    else :
                        better_match=True
                else :
                    better_match=True

                if better_match :

                    if check_distance(ref_bone,tmp_head,bone['head']) :
                        match['ref_head'] = ref_bone_name
                        head_vector = (bone['head']-ref_bone['head'])

                        if inside(bone['head'],ref_bone)  :
                            match['head'] = head_vector.length/ref_bone['length']
                        else :
                            match['head'] = -head_vector.length/ref_bone['length']

                        tmp_head = ref_bone

            if intersect(bone["tail"],ref_bone):
                better_match = False
                if match.get("ref_head") :
                    if match.get("ref_tail")and  match["ref_tail"]==match["ref_head"] :
                        pass

                    elif ref_bone_name==match["ref_head"] :
                        match['ref_tail'] = ref_bone_name
                        tail_vector = (bone['tail']-ref_bone["head"])

                        if inside(bone["tail"],ref_bone) :
                            match['tail'] = tail_vector.length/ref_bone["length"]
                        else :
                            match['tail'] = -tail_vector.length/ref_bone["length"]

                        tmp_tail = ref_bone

                    else :
                        better_match = True

                else :
                    better_match = True

                if better_match :
                    if check_distance(ref_bone,tmp_tail,bone['tail']) :

                        match['ref_tail'] = ref_bone_name
                        tail_vector = (bone['tail']-ref_bone["head"])

                        if inside(bone["tail"],ref_bone) :
                            match['tail'] = tail_vector.length/ref_bone["length"]
                        else :
                            match['tail'] = -tail_vector.length/ref_bone["length"]

                        tmp_tail = ref_bone






        if "tail" in match and "head" in match:
            if match['ref_tail'] == match['ref_head'] :
                roll_bone_name = match['ref_tail']

            else :
                roll_bone_name = find_ref_roll(metarig_values,bone)

            ref_roll_bone = metarig_values[roll_bone_name]


            roll = ref_roll_bone['roll']- bone['roll']

            match['roll'] =  roll
            match['ref_roll'] = roll_bone_name

        rig.data.bones[bone_name]['match'] = match
    """
