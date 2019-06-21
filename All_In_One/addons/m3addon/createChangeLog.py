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
import os.path
import argparse
import time

modelFileName = sys.argv[1]

class ChangeLogCreator:
    
    def __init__(self, modelFileName, logFileName):
        self.modelFileName = modelFileName
        self.logFileName = logFileName
    
    def createChangeLog(self):
        self.logFile = open(self.logFileName, "w")
        try:
            previousModelModiticationTime = os.path.getmtime(self.modelFileName)
            self.log("Log file started at %s" % time.ctime(previousModelModiticationTime))
            previousModel = m3.loadModel(self.modelFileName, checkExpectedValue=False)
            while True:
                currentModelModificationTime = os.path.getmtime(self.modelFileName)
                if currentModelModificationTime > previousModelModiticationTime:
                    self.log("")
                    self.log("File modified at %s" % time.ctime(currentModelModificationTime))
                    currentModel = m3.loadModel(self.modelFileName)
                    self.changedAnimationIds = 0
                    self.compareM3Structures(previousModel, currentModel, "model")
                    if self.changedAnimationIds > 0:
                        self.log("%d animation ids have changed!" % self.changedAnimationIds)
                    previousModelModiticationTime = currentModelModificationTime
                    previousModel = currentModel
                time.sleep(0.1)
        finally:
           self.logFile.close()
                
    def compareM3Structures(self, previous, current, structurePath):
        previousType = previous.structureDescription
        currentType = current.structureDescription
        if currentType.structureName != previousType.structureName:
            self.log("%s changed its structure type from %s to %s" % (structurePath, previousType.structureName, currentType.structureName))
            return
        
        if currentType.structureVersion != previousType.structureVersion:
            self.log("%s changed its structure version from %s to %s" % (structurePath, previousType.structureVersion, currentType.structureVersion))
            return
        
        for field in previousType.fields:
            fieldPath = structurePath + "." + field.name
            previousFieldContent = getattr(previous, field.name)
            currentFieldContent = getattr(current, field.name)
            if isinstance(field, m3.EmbeddedStructureField):
                self.compareM3Structures(previousFieldContent, currentFieldContent, fieldPath)
            elif isinstance(field, m3.StructureReferenceField):
                currentLength = len(currentFieldContent)
                previousLength = len(previousFieldContent)
                if len(currentFieldContent) != previousLength:
                    self.log("The length of %s changed from %d to %d" % (fieldPath, previousLength, currentLength ))
                else:
                    elementIndex = 0
                    for previousElement, currentElement in zip(previousFieldContent, currentFieldContent):
                        elementPath = "%s[%d]" % (fieldPath, elementIndex)
                        self.compareM3Structures(previousElement, currentElement, elementPath)
                        elementIndex += 1
            else:
                    
                if currentFieldContent != previousFieldContent:
                    if field.name != "animId" and field.name != "uniqueUnknownNumber" :
                        if isinstance(field, m3.IntField):
                            previousFieldContentStr = hex(previousFieldContent)
                            currentFieldContentStr = hex(currentFieldContent) 
                        else:
                            previousFieldContentStr = str(previousFieldContent)
                            currentFieldContentStr = str(currentFieldContent)
                        self.log("%s changed from %s to %s" % (fieldPath, previousFieldContentStr, currentFieldContentStr))
                    else:
                        self.changedAnimationIds += 1

            
    
    def log(self, message):
        self.logFile.write(str(message) + "\n")
        print(message) 
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('m3File', help="The m3 file for which a change log should be created")
    parser.add_argument('--log-file', '-l', help='Directory in which m3 files will be placed')
    args = parser.parse_args()
    modelFileName = args.m3File
    logFileName = args.log_file
    if logFileName == None:
        logFileName = modelFileName[:-3] + "-changelog.txt"
    changeLogCreator = ChangeLogCreator(modelFileName, logFileName)
    changeLogCreator.createChangeLog()