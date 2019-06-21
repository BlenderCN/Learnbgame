def selection():
    C =  bpy.context
    m = C.mode

    if m == 'POSE':
        return C.selected_pose_bones
    elif m == 'EDIT_ARMATURE':
        return C.selected_bones
    else:
        return C.selected_objects