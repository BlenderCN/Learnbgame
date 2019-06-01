def mute_contraints(ob, mute=True):
    print(ob.name)
    cct = 0
    uct = 0
    for b in ob.pose.bones:
        for cs in b.constraints:
            if cs.mute == mute:
                print('  ',b.name, '-', cs.name, '-: Untouched')
                uct += 1
            else:
                print('  ',b.name, '-', cs.name, '-: Switch')
                cs.mute = mute
                cct +=1
    #report
    if cct or uct:
        if cct:
            print(' ',cct, 'switched')
        if uct:
            print(' ',uct, 'untouched')
    else:
        print('no constraints')
    return



for ob in [o for o in C.selected_objects if o.type == 'ARMATURE']:
    mute_contraints(ob, True)
    #unmute
    #mute_contraints(ob, False)