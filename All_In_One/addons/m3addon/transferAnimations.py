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
    parser = argparse.ArgumentParser(description='Combines an m3 and m3a file')
    parser.add_argument('m3File', help="m3 file")
    parser.add_argument('m3aFile', help="m3a files with extra animations for the m3 file")
    parser.add_argument('outputFile', help="name of the new m3 file to create")
    args = parser.parse_args()


    m3Model = m3.loadModel(args.m3File) 
    m3aModel = m3.loadModel(args.m3aFile)
    outputFile = args.outputFile
    sameFormat = True

    if (len(m3Model.sequences) > 0 and len(m3aModel.sequences) > 0 ):
        if m3Model.sequences[0].structureDescription != m3aModel.sequences[0].structureDescription:
            sameFormat = False
    if (len(m3Model.sequenceTransformationCollections) > 0 and len(m3aModel.sequenceTransformationCollections) > 0 ):
        if m3Model.sequenceTransformationCollections[0].structureDescription != m3aModel.sequenceTransformationCollections[0].structureDescription:
            sameFormat = False
    if (len(m3Model.sequenceTransformationGroups) > 0 and len(m3aModel.sequenceTransformationGroups) > 0 ):
        if m3Model.sequenceTransformationGroups[0].structureDescription != m3aModel.sequenceTransformationGroups[0].structureDescription:
            sameFormat = False
    if (len(m3Model.sts) > 0 and len(m3aModel.sts) > 0 ):
        if m3Model.sts[0].structureDescription != m3aModel.sts[0].structureDescription:
            sameFormat = False

    if not sameFormat:
        sys.stderr.write("The animation data has been stored in differnt formats\n")
        sys.exit(1)
            
    if m3Model.uniqueUnknownNumber != m3aModel.uniqueUnknownNumber:
        sys.stderr.write("The animations / the m3a file has not been made for the m3 file\n")
        sys.exit(1)
    
    m3aAnimationNames = set()
    for seq in m3aModel.sequences:
        m3aAnimationNames.add(seq.name)
        
    m3AnimationNames = set()
    for seq in m3Model.sequences:
        m3AnimationNames.add(seq.name)

    animationNameConflicts = m3AnimationNames.intersection(m3aAnimationNames)
    if len(animationNameConflicts) > 0:
        sys.stderr.write("Animation name conflict detected: %s\n" % animationNameConflicts)
        sys.exit(1)

    numberOfSequences = len(m3aModel.sequences)
    if len(m3aModel.sequenceTransformationGroups) != numberOfSequences:
        raise Exception("Script or model incorrect: The model has not the same amounth of stg elements as it has sequences.")
    for sequenceIndex in range(numberOfSequences):
        sequence = m3aModel.sequences[sequenceIndex]
        stg = m3aModel.sequenceTransformationGroups[sequenceIndex]
        newSTCIndices = []
        for oldSTCIndex in stg.stcIndices:
            stc = m3aModel.sequenceTransformationCollections[oldSTCIndex]
            if stc.stsIndex != stc.stsIndexCopy:
                raise Exception("Script or model incorrect: stsIndex != stsIndexCopy.")
            sts = m3aModel.sts[stc.stsIndex]
            stc.stsIndex = len(m3Model.sts)
            stc.stsIndexCopy = stc.stsIndex
            m3Model.sts.append(sts)
            newSTCIndex = len(m3Model.sequenceTransformationCollections)
            m3Model.sequenceTransformationCollections.append(stc)
            newSTCIndices.append(newSTCIndex)
        stg.stcIndices = newSTCIndices
        m3Model.sequences.append(sequence)
        m3Model.sequenceTransformationGroups.append(stg)
    
    
    m3.saveAndInvalidateModel(m3Model, outputFile)

