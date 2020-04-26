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
import argparse
import os.path
import os
import io
import time
import traceback
import re

def byteDataToHex(byteData):
    return '0x' + ''.join(["%02x" % x for x in byteData])


def indent(level):
    return "\t" * level

def openTag(name):
    return "<%s>" % name

def closeTag(name):
    return "</%s>\n" % name

def openCloseTag(name):
    return "<%s />\n" % name


def printXmlElement(out, level, name, value):
    out.write(indent(level) + openTag(name) + value + closeTag(name))

def printObject(out, level, name, value):
    valueType = type(value)
    if value == None:
        out.write(indent(level) + openCloseTag(name))
        return
    
    elif valueType == int:
        value = hex(value)
        printXmlElement(out, level, name, value)
        return
    
    elif valueType == bytearray or valueType == bytes:
        value = byteDataToHex(value)
        printXmlElement(out, level, name, value)
        return

    elif valueType == str:
        value = re.sub('[^\x20-\x7F]', '.', str(value))
        printXmlElement(out, level, name, value)
        return

    elif valueType == list:
        if len(value) == 0:
            out.write(indent(level) + openTag(name) + closeTag(name))
            return
        firstObject = value[0]
        if isinstance(firstObject, m3.M3Structure):
            structureName = firstObject.structureDescription.structureName
            structureVersion = firstObject.structureDescription.structureVersion
            out.write(('%s<%s structureName="%s" structureVersion="%s" >\n' % (indent(level), name, structureName, structureVersion)))
        else:
            out.write(indent(level) + openTag(name) + "\n")
        for entry in value:
            printObject(out, level + 1, name + "-element", entry)
        
        out.write(indent(level) + closeTag(name))
        return
    
    elif valueType == m3.M3Structure:
        out.write(indent(level) + openTag(name) + "\n")
        
        for field in value.structureDescription.fields:
            v = getattr(value, field.name)
            printObject(out, level + 1, field.name, v)
        
        out.write(indent(level) + closeTag(name))
        return
    
    else:
        printXmlElement(out, level, name, str(value))
        return

def printModel(model, outputFilePath):
    outputStream = io.StringIO()
    
    outputFile = open(outputFilePath, "w")
    modelDescription = model.structureDescription
    outputStream.write('<model structureName="%s" structureVersion="%s" >\n' % (modelDescription.structureName, modelDescription.structureVersion))

    for field in modelDescription.fields:
        value = getattr(model, field.name)
        printObject(outputStream, 0, field.name, value)

    outputStream.write(closeTag("model"))
    
    outputFile.write(outputStream.getvalue())
    outputFile.close()
    
    outputStream.close()


def convertFile(inputFilePath, outputFilePath, continueAtErrors):    
    model = None
    try:
        model = m3.loadModel(inputFilePath)
    except Exception as e:
        if continueAtErrors:
            sys.stderr.write("\nError: %s\n" % e)
            sys.stderr.write("\nFile: %s\n" % inputFilePath)
            sys.stderr.write("Trace: %s\n" % traceback.format_exc())
        else:
            raise e
        return False
    
    printModel(model, outputFilePath)
    return True

def processFile(inputPath, outputDirectory, inputFilePath, continueAtErrors):
    relativeInputPath = os.path.relpath(inputFilePath, inputPath)
    relativeOutputPath = relativeInputPath + ".xml"
   
    if outputDirectory:
        if outputDirectory and not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outputFilePath = os.path.join(outputDirectory, relativeOutputPath)
    else:
        outputFilePath = inputFilePath + ".xml"
    
    print("%s -> %s" % (inputFilePath, outputFilePath))

    return convertFile(inputFilePath, outputFilePath, continueAtErrors)

def processDirectory(inputPath, outputPath, recurse, continueAtErrors):
    
    count, succeeded, failed = 0, 0, 0
    
    for path, dirs, files in os.walk(inputPath):
        
        for file in files:
            if file.endswith(".m3"):
                
                inputFilePath = os.path.join(path, file)
                success = processFile(inputPath, outputPath, inputFilePath, continueAtErrors)
                
                succeeded += success
                failed += not success
                count += 1
        
        if not recurse:
            break
    
    return count, succeeded, failed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Starcraft II m3 models to xml format.')
    parser.add_argument('path', nargs='+', help="Either a *.m3 file or a directory with *.m3 files")
    parser.add_argument('--output-directory', 
        '-o', 
        help='Directory in which m3 files will be placed')
    parser.add_argument('-r', '--recurse',
        action='store_true', default=False,
        help='Recurse input directory and convert all m3 files found.')
    parser.add_argument('-c', '--continue-at-errors',
        action='store_true', default=False,
        help='Continue if there are errors in the files')
    args = parser.parse_args()
    
    outputDirectory = args.output_directory
    if outputDirectory != None and not os.path.isdir(outputDirectory):
        sys.stderr.write("%s is not a directory" % outputDirectory)
        sys.exit(2)
        
    for path in args.path:
        if not os.path.isdir(path) and not os.path.isfile(path):
            sys.stderr.write("Path %s is not a valid directory or file" % path)
            sys.exit(2)
    
    recurse = args.recurse
    
    continueAtErrors = args.continue_at_errors
    
    t0 = time.time()
    print("Converting files..")
    for path in args.path:
        total, succeeded, failed = (0, 0, 0)
        if os.path.isfile(path):
            inputFilePath = path
            path = os.path.dirname(path)
            success = processFile(path, outputDirectory, inputFilePath, continueAtErrors)
            totalDelta, succeededDelta, failedDelta = 1, success, not success
        else:
            totalDelta, succeededDelta, failedDelta = processDirectory(path, outputDirectory, recurse, continueAtErrors)
        total += totalDelta
        succeeded += succeededDelta
        failed += failedDelta
    
    t1 = time.time()
    print("%d files found, %d converted, %d failed in %.2f s" % (total, succeeded, failed, (t1 - t0)))
    if failed > 0:
        sys.exit(1)