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

import struct
import sys
import m3
import xml.dom.minidom
from xml.dom.minidom import Node
import argparse
import os
import time

def forElementsIn(xmlNode):
    for child in xmlNode.childNodes:
        if type(child) == xml.dom.minidom.Text:
            if not child.wholeText.isspace():
                raise Exception("Unexpected content \"%s\" within element %s" % (child.wholeText, xmlNode.nodeName))
        else:
            yield child

def createSingleStructureElement(xmlNode, structureDescription):
    createdObject = structureDescription.createInstance()
    fieldIndex = 0
    for child in forElementsIn(xmlNode):
        fieldName = child.nodeName
        if fieldIndex >= len(structureDescription.fields):
            raise Exception("XML file is incompatible: too many fields")
        field = structureDescription.fields[fieldIndex]
        if field.name != fieldName:
            raise Exception("XML file is incompatible: Expected field %s but found field %s" % (field.name, fieldName) )
        
        fieldContent = createFieldContent(child,field)
        setattr(createdObject, field.name, fieldContent)
        fieldIndex += 1
    
    missingFields = len(structureDescription.fields) - fieldIndex
    if missingFields > 0:
        raise Exception("XML file is incompatible: %d fields are missing in %s" % (missingFields, structureDescription.structureName))
        
    return createdObject
                
intTypeStrings = set(["int32","int16","int8","uint32", "uint16", "uint8"])     
def createFieldContent(xmlNode, field):
    if isinstance(field, m3.ReferenceField):
        if field.historyOfReferencedStructures == None:
            return [] # TODO check if that's correct
        else:
            referencedStructureName = field.historyOfReferencedStructures.name
            if referencedStructureName == "CHAR":
                if len(xmlNode.childNodes) == 0:
                    return None
                return stringContentOf(xmlNode)
            elif referencedStructureName == "U8__":
                return bytearray(hexToBytes(stringContentOf(xmlNode), xmlNode))
            else:
                if field.historyOfReferencedStructures != None:
                    return createElementList(xmlNode, field.name, field.historyOfReferencedStructures)
                else:
                    return createElementList(xmlNode, field.name, None)

    elif isinstance(field, m3.UnknownBytesField):
        return hexToBytes(stringContentOf(xmlNode),xmlNode)
    elif isinstance(field, m3.PrimitiveField):
        if field.typeString == "float":
            return float(stringContentOf(xmlNode))
        elif field.typeString in intTypeStrings:
            return int(stringContentOf(xmlNode), 0)
        else:
            raise Exception("Unsupported primtive: %s" % field.typeString)
    elif isinstance(field, m3.EmbeddedStructureField):
        return createSingleStructureElement(xmlNode, field.structureDescription)
    else: # TagField
        raise Exception("Unsupported field type %s" % type(field))

def removeWhitespace(s):
    return s.translate({ord(" "):None,ord("\t"):None,ord("\r"):None,ord("\n"):None})

def hexToBytes(hexString, xmlNode):
    hexString = removeWhitespace(hexString)
    if hexString == "":
        return bytearray(0)
    if not hexString.startswith("0x"):
        raise Exception('hex string "%s" of node %s does not start with 0x' % (hexString,xmlNode.nodeName) )
    hexString = hexString[2:]
    return bytes([int(hexString[x:x+2], 16) for x in range(0, len(hexString),2)])

def stringContentOf(xmlNode):
    content = ""
    for child in xmlNode.childNodes:
        if child.nodeType == Node.TEXT_NODE:
            content += child.data
        else:
            raise Exception("Element %s contained childs of xml node type %s." % (xmlNode.nodeName,type(xmlNode)))
    return content

def createListElement(xmlNode, structureDescription):
    if structureDescription.structureName in ["I32_","I16_", "I8__", "U32_", "U16_", "U8__", "FLAG"]:
        return int(stringContentOf(xmlNode), 0)
    elif structureDescription.structureName in ["REAL"]:
        return float(stringContentOf(xmlNode))
    else:
        return createSingleStructureElement(xmlNode, structureDescription)
      
      
def childElementsOf(parentName, xmlNode):
    expectedChildNames = parentName + "-element"
    for child in xmlNode.childNodes:
        if type(child) == xml.dom.minidom.Text:
            if not child.data.isspace():
                raise Exception("Unexpected content \"%s\" within element %s" % (child.wholeText, xmlNode.nodeName))
        else:
            if (child.nodeName != expectedChildNames):
                raise Exception("Unexpected child \"%s\" within element %s", (child.nodeName, xmlNode.nodeName))
            yield child

def createElementList(xmlNode, parentName, historyOfReferencedStructure):
    xmlElements = list(childElementsOf(parentName, xmlNode))
    if historyOfReferencedStructure.name in ["CHAR", "I32_","I16_", "I8__", "U32_", "U16_", "U8__", "REAL", "FLAG"]:
        structVersion = 0
    else:
        if len(xmlElements) == 0:
            return []
        
        child = xmlNode.firstChild
        structVersion = int(xmlNode.getAttribute("structureVersion"))
        structName = xmlNode.getAttribute("structureName")
        if structName == "" or structVersion == "":
            raise Exception("Incompatible format: Require now a strutureName and structureVerson attribute for the list %s" % parentName)
        if structName != historyOfReferencedStructure.name:
            raise Exception("Expected a %s to have the structure name %s instead of %s" % (parentName,  historyOfReferencedStructure.name, structName))
    structureDescription = historyOfReferencedStructure.getVersion(structVersion)
    createdList = []
    for child in xmlElements:
        o = createListElement(child, structureDescription)
        createdList.append(o)
        
    return createdList
        


def convertFile(inputFilePath, outputDirectory):
    if outputDirectory != None:
        fileName = os.path.basename(inputFilePath)
        outputFilePath = os.path.join(outputDirectory, fileName[:-4])
    else:
        outputFilePath = inputFilePath[:-4]
    print("Converting %s -> %s" % (inputFilePath, outputFilePath))
    doc = xml.dom.minidom.parse(inputFilePath)
    modelElement = doc.firstChild
    structVersion = int(modelElement.getAttribute("structureVersion"))
    structName = modelElement.getAttribute("structureName")
    modelDescription = m3.structures[structName].getVersion(structVersion)
    model = createSingleStructureElement(modelElement, modelDescription)
    m3.saveAndInvalidateModel(model, outputFilePath)

 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='+', help="Either a *.m3.xml file or a directory with *.m3.xml files generated with m3ToXml.py")
    parser.add_argument('--output-directory', '-o', help='Directory in which m3 files will be placed')
    parser.add_argument('--watch', action='store_const', const=True, default=False)
    args = parser.parse_args()
    outputDirectory = args.output_directory
    if outputDirectory != None and not os.path.isdir(outputDirectory):
        sys.stderr.write("%s is not a directory" % outputDirectory)
        sys.exit(2)
    for filePath in args.path:
        if not (filePath.endswith(".m3.xml") or os.path.isdir(filePath)):
            sys.stderr.write("%s neither a directory nor does it end with '.m3.xml'\n" % filePath)
            sys.exit(2)
            
            
    if args.watch:
        if ((len(args.path) == 0) or os.path.isdir(filePath)):
            sys.stderr.write("Watch option is only supported for a single file")
            sys.exit(2)
        
        previousModelModiticationTime = os.path.getmtime(filePath)
        convertFile(filePath, outputDirectory)
        print("Converted %s to an m3 file. Will convert it again if it changes" % filePath)
        while True:
            currentModelModificationTime = os.path.getmtime(filePath)
            if currentModelModificationTime > previousModelModiticationTime:
                print("File modified at %s, converting again" % time.ctime(currentModelModificationTime))
                convertFile(filePath, outputDirectory)
                print("converted file")
                previousModelModiticationTime = currentModelModificationTime
            time.sleep(0.1)
    else:
        counter = 0
        for filePath in args.path:
            if os.path.isdir(filePath):
                for fileName in os.listdir(filePath):
                    inputFilePath = os.path.join(filePath, fileName)
                    if fileName.endswith(".m3.xml"):
                        convertFile(inputFilePath, outputDirectory)
                        counter += 1
            else:
                convertFile(filePath, outputDirectory)
                counter += 1
        if counter == 1:
            print("Converted %d file from .m3.xml to .m3" % counter)
        else:
            print("Converted %d files from .m3.xml to .m3" % counter)
