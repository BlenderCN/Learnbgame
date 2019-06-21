# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons BY-NC-SA:
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2016
#
# ##### END LICENSE BLOCK #####

import bpy, struct, mathutils

########
# READ #
########
def read_angel_string(file):
    str_len = struct.unpack('B', file.read(1))[0]
    if str_len == 0:
        return ''
    else:
        return_string = file.read(str_len - 1).decode("utf-8")
        file.seek(1, 1)
        return return_string

def read_float(file):
    return struct.unpack('f', file.read(4))[0]


def read_float3(file):
    return struct.unpack('fff', file.read(12))


def read_cfloat3(file):
    btc = struct.unpack('BBB', file.read(3))
    return (btc[0]-128)/128, (btc[1]-128)/128, (btc[2]-128)/128


def read_cfloat2(file):
    stc = struct.unpack('HH', file.read(4))
    return (stc[0]/128) - 128, (stc[1]/128) - 128


def read_float2(file):
    return struct.unpack('ff', file.read(8))


def read_color4f(file):
    return struct.unpack('ffff', file.read(16))


def read_color4d(file):
    c4d = struct.unpack('BBBB', file.read(4))
    return [c4d[0]/255, c4d[1]/255, c4d[2]/255, c4d[3]/255]
    
def read_matrix3x4(file):
    row1r = list(struct.unpack('fff', file.read(12)))
    row2r = list(struct.unpack('fff', file.read(12)))
    row3r = list(struct.unpack('fff', file.read(12)))
    translation = struct.unpack('fff', file.read(12))
    
    # rotate the matrix
    row1 = [row1r[0], row2r[0], row3r[0]]
    row2 = [row1r[1], row2r[1], row3r[1]]
    row3 = [row1r[2], row2r[2], row3r[2]]
    
    # create matrix, and rotate axes
    mtx = mathutils.Matrix((row1, row2, row3))
    
    
    eul_angles = mtx.to_euler('XYZ')
    new_rot = [eul_angles.x, eul_angles.z, eul_angles.y]
    
    # zero out rotation
    eul_angles.x *= -1
    eul_angles.y *= -1
    eul_angles.z *= -1
    mtx.rotate(eul_angles)
    
    
    # insert correct rotation
    eul_angles.x = new_rot[0]
    eul_angles.y = new_rot[1]
    eul_angles.z = new_rot[2]
    mtx.rotate(eul_angles)
    
    # create 4x4 and return
    mtx4x4 = mtx.to_4x4()
    mtx4x4.translation = ((translation[0], translation[2] * -1, translation[1]))
    return mtx4x4

def write_matrix3x4(file, matrix):
    # convert to 3x3 and grab pos/rot
    mtx = matrix.to_3x3()
    
    eul_angles = mtx.to_euler('XYZ')
    translation = matrix.to_translation()
    new_rot = [eul_angles.x, eul_angles.z, eul_angles.y]
    
    # zero out rotation
    eul_angles.x *= -1
    eul_angles.y *= -1
    eul_angles.z *= -1
    mtx.rotate(eul_angles)
    
    # insert correct rotation
    eul_angles.x = new_rot[0]
    eul_angles.y = new_rot[1]
    eul_angles.z = new_rot[2]
    mtx.rotate(eul_angles)
    
    #write 3x3
    file.write(struct.pack('fff', mtx[0][0], mtx[1][0], mtx[2][0]))
    file.write(struct.pack('fff', mtx[0][1], mtx[1][1], mtx[2][1]))
    file.write(struct.pack('fff', mtx[0][2], mtx[1][2], mtx[2][2]))
    file.write(struct.pack('fff', translation[0], translation[2], translation[1] * -1))

#########
# WRITE #
#########
def write_angel_string(file, strng):
    str_len = len(strng)
    if str_len > 0:
        file.write(struct.pack('B', str_len+1))
        file.write(bytes(strng, 'UTF-8'))
        file.write(bytes('\x00', 'UTF-8'))
    else:
        file.write(struct.pack('B', 0))

def write_float2(file, data):
    file.write(struct.pack('ff', data[0], data[1]))
    
def write_float3(file, data):
    file.write(struct.pack('fff', data[0], data[1], data[2]))
    
def write_color4d(file, color, alpha=1):
    file.write(struct.pack('BBBB', int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(alpha * 255)))
    
def write_color4f(file, color, alpha=1):
    file.write(struct.pack('ffff', color[0], color[1], color[2], alpha))


def write_file_header(file, name, length=0):
    file.write(bytes('FILE', 'utf-8'))
    write_angel_string(file, name)
    file.write(struct.pack('L', length))