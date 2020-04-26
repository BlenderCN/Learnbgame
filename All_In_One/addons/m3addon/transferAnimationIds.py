#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import m3
import sys
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make a model use the same animation ids like another model(works only for bones with the same name yet)')
    parser.add_argument('animIdFile', help="m3 with the wanted animation ids")
    parser.add_argument('modelToFix', help="m3 which has the wrong animation ids")
    parser.add_argument('outputFile', help="name of the new m3 file to create")
    args = parser.parse_args()


    animIdModel = m3.loadModel(args.animIdFile) 
    modelToFix = m3.loadModel(args.modelToFix)
    outputFile = args.outputFile

    boneNameToAnimIdBoneMap = {}
    for bone in animIdModel.bones:
        boneNameToAnimIdBoneMap[bone.name] = bone

    oldAnimIdToNewAnimIdMap = {}
    for boneToFix in modelToFix.bones:
        boneWithAnimId = boneNameToAnimIdBoneMap[boneToFix.name]
        oldAnimId = boneToFix.location.header.animId
        newAnimId = boneWithAnimId.location.header.animId
        boneToFix.location.header.animId = newAnimId
        oldAnimIdToNewAnimIdMap[oldAnimId] = newAnimId
        
        oldAnimId = boneToFix.rotation.header.animId
        newAnimId = boneWithAnimId.rotation.header.animId
        boneToFix.rotation.header.animId = newAnimId
        oldAnimIdToNewAnimIdMap[oldAnimId] = newAnimId
        
        oldAnimId = boneToFix.scale.header.animId
        newAnimId = boneWithAnimId.scale.header.animId
        boneToFix.scale.header.animId = newAnimId
        oldAnimIdToNewAnimIdMap[oldAnimId] = newAnimId
       
    def assertModelContainsOneDivisionAndMSec(model):
        if len(model.divisions) != 1 or len(model.divisions[0].msec) != 1:
            raise Exception("Model contains %d divisions and the first division has %d msec" %(en(model.divisions), len(model.divisions[0].msec)))
    
    assertModelContainsOneDivisionAndMSec(modelToFix)
    assertModelContainsOneDivisionAndMSec(animIdModel)
    msecToFix = modelToFix.divisions[0].msec[0]
    msecWithAnimId = animIdModel.divisions[0].msec[0]
    oldAnimId = msecToFix.boundingsAnimation.header.animId
    newAnimId = msecWithAnimId.boundingsAnimation.header.animId
    msecToFix.boundingsAnimation.header.animId = newAnimId
    oldAnimIdToNewAnimIdMap[oldAnimId] = newAnimId
        

    for stc in modelToFix.sequenceTransformationCollections:
        animIds = stc.animIds
        for i in range(len(animIds)):
            newAnimId = oldAnimIdToNewAnimIdMap.get(animIds[i])
            if newAnimId != None:
                animIds[i] = newAnimId
    
    for sts in modelToFix.sts:
        animIds = sts.animIds
        for i in range(len(animIds)):
            newAnimId = oldAnimIdToNewAnimIdMap.get(animIds[i])
            if newAnimId != None:
                animIds[i] = newAnimId
    
    m3.saveAndInvalidateModel(modelToFix, outputFile)

