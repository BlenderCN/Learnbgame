def getRoll(bone):
    '''take a bone and return roll in radians'''
    #need: from math import atan, pi, degrees
    mat = bone.matrix_local.to_3x3()
    quat = mat.to_quaternion()
    if abs(quat.w) < 1e-4:
        roll = pi
    else:
        roll = 2*atan(quat.y/quat.w)

    ##return as radians
    return roll
    ##return as degrees
    # return degrees(roll)