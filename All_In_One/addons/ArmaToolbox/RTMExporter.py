'''
Created on 23.12.2013

@author: hfrieden

-----------------------------
What do I know
Matrix is a transformation matrix, with the position in the last line
Rotation seems to be absolute, i.e. one bone rotates 90 degrees, all sub-bones rotate 90 degrees too
Position:
If not rotated individually, it's 0,0,0,1
If rotated individually, it is the offset from its original position

Question is whether I can always write a translation even if the thing didn't rotate individually

Idea: Have two backups of the original bone skeleton, deform one alone with the armature, and use the other for reference

I am pretty sure now that the rotations in the matrix in the RTM file are global rotations of the bones in X,Z, and Y (Blender)

In an example I have with the complete Right forearm rotated around 45 degrees on its local axis, the resulting matrix
is 

       0.816696 0.379291 0.434911 0.000000
       -0.540669 0.766365 0.346932 0.000000
       -0.201713 -0.518483 0.830957 0.000000
       0.096033 1.252794 0.079032 1.000000
       
The upper 3x3 matrix yields a rotation of -31, 11, -33 around X,Y and Z (or rather, X,Z and Y for Blender) which is the same for
all bones below the RightForearm. Replicating that rotation in Blender yields the same result, so I am quite sure the rotations are
global.

'''
import struct
import bpy
import bmesh
import os.path as path
import ArmaToolbox
import math
import mathutils

def writeSignature(filePtr, sig):
    filePtr.write(bytes(sig, "UTF-8"))

def writeULong(filePtr, value):
    filePtr.write(struct.pack("I", value))
    
def writeFloat(filePtr, value):
    filePtr.write(struct.pack("f", value))
    
def writeBone(filePtr, boneName):
    filePtr.write(struct.pack("32s", bytes(boneName, "UTF-8")))

def RTMFrameTime(frame, startFrame, endFrame):
    frameIdx = frame - startFrame
    return frameIdx / (endFrame - startFrame)
        
def writeRTMFrame(filePtr, boneNames, blendObject, keyframe, frameTime):
    writeFloat(filePtr, frameTime)
    for boneName in boneNames:
        writeBone(filePtr, boneName)
        
        poseBone = blendObject.pose.bones[boneName]
        mat = mathutils.Matrix(poseBone.matrix_channel)
        mat.transpose()

        # M00 M02 M01
        # M20 M22 M21
        # M10 M12 M11
        # M30 M32 M31

        writeFloat(filePtr, mat[0][0])
        writeFloat(filePtr, mat[0][2])
        writeFloat(filePtr, mat[0][1])

        writeFloat(filePtr, mat[2][0])
        writeFloat(filePtr, mat[2][2])
        writeFloat(filePtr, mat[2][1])

        writeFloat(filePtr, mat[1][0])
        writeFloat(filePtr, mat[1][2])
        writeFloat(filePtr, mat[1][1])
        
        writeFloat(filePtr, mat[3][0])
        writeFloat(filePtr, mat[3][2])
        writeFloat(filePtr, mat[3][1])


def getMotionVector(context, boneName, firstKf, lastKf):

    blendObject = context.object
    armature = blendObject.data
    scene = context.scene

    scene.frame_set(firstKf)
    bone = blendObject.pose.bones[boneName]
    matrix_final = blendObject.matrix_world * bone.matrix
    vec1 = matrix_final.to_translation()

    scene.frame_set(lastKf)
    bone = blendObject.pose.bones[boneName]
    matrix_final = blendObject.matrix_world * bone.matrix
    vec2 = matrix_final.to_translation()

    vector = vec2 - vec1
    
    # Swap Y and Z
    v = [vector[0], vector[2], vector[1]]
    return v

def exportRTM(context, keyframeList, filepath="", staticPose=False, clipFrames=True):
    filePtr = open(filepath, "wb")
    
    blendObject = context.object
    armature = blendObject.data
    scene = context.scene

    startFrame = scene.frame_start
    endFrame = scene.frame_end

    keyframeList.sort()
    keyframeList = list(set(keyframeList))
    
    if clipFrames:
        k = []
        for x in keyframeList:
            if x >= startFrame and x <= endFrame:
                k.append(x)
        keyframeList = k
    
    # Check if there are any keyframes, if not, enforce staticPose
    if blendObject.animation_data is None:
        staticPose = True
    
    # Find our bone names
    boneNames = []
    
    for bone in armature.bones:
        if len(bone.name)>0:
            if bone.name[0] != '@' and bone.name[-1] != '@':
                boneNames.append(bone.name)


    # At this point we're ready to start writing
    # Signature
    writeSignature(filePtr, "RTM_0101")
    
    # Movement vector
    if staticPose:
        # Static pose has no motion
        writeFloat(filePtr, 0)
        writeFloat(filePtr, 0)
        writeFloat(filePtr, 0)
    elif len(blendObject.armaObjProps.centerBone) == 0:
        # With no center bone selected, write the motion vector 
        vector = blendObject.armaObjProps.motionVector
        writeFloat(filePtr, vector[0])
        writeFloat(filePtr, vector[2])
        writeFloat(filePtr, vector[1])
    else:
        # With a bone selected, calculate the real motion vector
        boneName = blendObject.armaObjProps.centerBone
        vector = getMotionVector(context, boneName, keyframeList[0], keyframeList[-1])
        writeFloat(filePtr, vector[0])
        writeFloat(filePtr, vector[1])
        writeFloat(filePtr, vector[2])
    
    # number of frames and number of bones
    if staticPose:
        writeULong(filePtr, 2)
    else:
        writeULong(filePtr, len(keyframeList))
        
    writeULong(filePtr, len(boneNames))
    
    # Write out the bone names
    for boneName in boneNames:
        writeBone(filePtr, boneName)
    keyframeList = sorted(keyframeList)
    if not staticPose:    
        ############################
        # Start writing RTM Frames
        # for a non-static animation
        for keyframe in keyframeList:
            scene.frame_set(keyframe)
            writeRTMFrame(filePtr, boneNames, blendObject, keyframe, RTMFrameTime(keyframe, startFrame, endFrame)) 
    else:
        ############################
        # Wrtie out the current pose
        # as a static pose
        writeRTMFrame(filePtr, boneNames, blendObject, 0, 0)
        writeRTMFrame(filePtr, boneNames, blendObject, 1, 1)
    
    
    filePtr.close()