def reset_stretch():
    for b in C.object.pose.bones:
        for cs in b.constraints:
            #print(cs.type)
            if cs.type == 'STRETCH_TO':
                print ('reseting', b.name)
                cs.rest_length = 0
                ##select one by one
                #C.object.data.bones.active = C.object.data.bones[b.name]
                #return


reset_stretch()