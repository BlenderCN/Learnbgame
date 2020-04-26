import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line


##b = bone, rb = ref_bone
def find_ref_roll(metarig,b) :


    distance = {}
    for bone_name,rb in metarig.items() :

        tail_distance = min((rb['tail']-b['tail']).length,(rb['tail']-b['head']).length)
        head_distance = min((rb['head']-b['tail']).length,(rb['head']-b['head']).length)



        distance[tail_distance+head_distance] = bone_name

    #print(tail_distance,head_distance)

    minimum = min(distance.keys())

    #print(distance[minimum])
    return(distance[minimum])


def inside(point,bone) :
    a = (point-bone['tail']).length
    b = (point-bone['head']).length

    #print(a+b-bone.length)

    if not a+b - bone['length'] <0.001 and  b<a:
        return False
    else :
        return True

# check if point is closer to bone_1 or to bone_2
def check_distance(bone_1,bone_2,point) :
    if bone_2 :

        distance = {}

        distance[(point-bone_1['tail']).length] = True
        distance[(point-bone_1['head']).length] = True

        distance[(point-bone_2['tail']).length]  = False
        distance[(point-bone_2['head']).length]  = False

        minimum = min(distance.keys())

        return(distance[minimum])

    else :
        return True


def round_vector(vector) :
    x = round(vector[0],5)
    y = round(vector[1],5)
    z = round(vector[2],5)

    return Vector((x,y,z))

'''
def intersect(pt,ref_bone) :
    intersection = intersect_point_line(pt,ref_bone['tail'],ref_bone['head'])


    distance =  (intersection[0]-pt).length


    if distance < 0.001 :
        return True
    else :
        return False
'''

def intersect(pt,bone) :
    intersection = intersect_point_line(pt,bone['head'],bone['tail'])

    point_on_line = (pt-intersection[0]).length < 0.001

    #print('point_on_line',point_on_line)
    #distance = True
    is_in_range = False
    if intersection[1]<=0.5 :
        distance = (pt-bone['head']).length
        #print(distance)
        if intersection[1]>=0 :
            is_in_range = True
        else :
            is_in_range = distance > -1.5

    elif intersection[1]>0.5 :
        distance = (pt-bone['tail']).length

        #print(distance)
        if intersection[1]<=1 :
            is_in_range = True
        else :
            is_in_range = distance < 2.5

    #print('is_in_range',is_in_range)
    #print(bone)
    #print('intersection',intersection)
    #print('point_on_line',point_on_line)

    #print('is_in_range',is_in_range)


    if point_on_line and is_in_range:
        return intersection[1]



def armature_info(rig) :
    #print('rig')
    if hasattr(rig,'type') :
        rig = rig.data

    scene = bpy.context.scene
    info = {}

    active_object = bpy.context.scene.objects.active
    mode = active_object.mode

    ob = bpy.data.objects.new('metarig',rig)
    scene.objects.link(ob)
    ob.select = True
    scene.objects.active = ob

    bpy.ops.object.mode_set(mode= 'OBJECT')
    bpy.context.scene.objects.active = ob

    bpy.ops.object.mode_set(mode= 'EDIT')

    for edit_bone in ob.data.edit_bones :
        info[edit_bone.name] ={}

        roll = round(edit_bone.roll,5)
        head = round_vector(edit_bone.head)
        tail = round_vector(edit_bone.tail)

        info[edit_bone.name]['roll'] = roll
        info[edit_bone.name]['head'] = head
        info[edit_bone.name]['tail'] = tail
        info[edit_bone.name]['vector'] = tail-head
        info[edit_bone.name]['length'] = edit_bone.length

    #restore active object
    bpy.ops.object.mode_set(mode= 'OBJECT')
    bpy.data.objects.remove(ob,True)

    bpy.context.scene.objects.active = active_object
    bpy.ops.object.mode_set(mode= mode)

    return info
