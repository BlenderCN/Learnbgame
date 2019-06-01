"""
PAN {
    long    number_nodes
    long    start_node
    float   total_dist

    Nodes[number_nodes]
}


Node {
    Vector  position
    float   distance

    long[4] previous_node_ids
    long[4] next_node_ids
}

"""
# import struct

# file = open("garden1.pan", "rb")


# print("Total Nodes", num_nodes)
# print("Total distance", total_dist)

# # read all nodes
# for n in range(num_nodes):
#   print("NODE", n)

#   # read position
#   vec = struct.unpack("<3f", file.read(12))
#   print("   Position", vec)

#   # read distance to finish line
#   dist = struct.unpack("<f", file.read(4))[0]
#   print("   Distance", dist)

#   # read previews connections
#   for x in range(4):
#       print("   Link:", x)
#       prv = struct.unpack("<l", file.read(4))[0]
#       print("      Prev", prv)

#   # read upcoming connections
#   for x in range(4):
#       print("   Link:", x)
#       nxt = struct.unpack("<l", file.read(4))[0]
#       print("      Next", nxt)

# file.close()


# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy, struct, bmesh, re, os, glob
import time, struct
from mathutils import Vector, Color
 
from . import const, parameters

export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_pos_file(file, matrix):
    scn = bpy.context.scene
    # read header
    num_nodes = struct.unpack("<l", file.read(4))[0]
    start_node = struct.unpack("<l", file.read(4))[0]
    total_dist = struct.unpack("<f", file.read(4))[0]



    for n in range(num_nodes):
        print("NODE", n)

        # read position
        vec = Vector(struct.unpack("<3f", file.read(12)))
        nodeob = bpy.data.objects.new("posnode{}".format(n), None)
        bpy.context.scene.objects.link(nodeob)
        nodeob.location = vec*matrix
        print("   Position", vec)

        # read distance to finish line
        dist = struct.unpack("<f", file.read(4))[0]
        print("   Distance", dist)

        # read previews connections
        for x in range(4):
            print("   Link:", x)
            prv = struct.unpack("<l", file.read(4))[0]
            print("      Prev", prv)

        # read upcoming connections
        for x in range(4):
            print("   Link:", x)
            nxt = struct.unpack("<l", file.read(4))[0]
            print("      Next", nxt)
    

      

######################################################
# IMPORT
######################################################
def load_pos(filepath, context, matrix):

    print("importing pos: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading the pos file
    load_pos_file(file, matrix)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator, filepath, context, matrix):

    global export_filename
    export_filename = filepath

    load_pos(filepath, context, matrix)

    return {'FINISHED'}
