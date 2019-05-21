#add 'ik.' before 'L' or 'R'
for pb in bpy.context.selected_pose_bones:
    # test the regex
    r = re.search(r'(.*)([LR])$', pb.name)
    for i, g in enumerate(r.groups()):
        print('grp',i,':', g)
    print()

    # pb.name = re.sub(r'(.*)([LR])$', r'\1ik.\2', pb.name)#
    #>>> 'arm.L' >> 'arm.ik.L' # unchanged if not finished by L or R