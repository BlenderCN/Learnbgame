"""
.. module:: thea_render_main
   :platform: OS X, Windows, Linux
   :synopsis: Functions to prepare environment, export frames and implements TheaRender class

.. moduleauthor:: Grzegorz Rakoczy <grzegorz.rakoczy@solidiris.com>


"""

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
import re
import bpy
import bgl
import blf
import subprocess
import os
import runpy
import socket
import sys
import time
import datetime
import struct
import pickle
import string
import tempfile
from random import random
import platform
import mathutils
from math import *
from TheaForBlender.thea_exporter import *
import configparser
#from sys import platform
#from builtins import True
if os.name == "nt":
    try:
        import winreg
    except:
        thea_globals.log.warning("Can't access windows registry")


global sdkProcess

def sendSocketMsg(host, port, message, waitForResponse=True):
    '''Sends the message to Thea Server

        :param host: Host address.
        :type host: str
        :param port: Port number.
        :type port: str
        :param message: message to send.
        :type message: str
        :param waitForResponse: wait for response from the server.
        :type waitForResponse: bool
        :return: The return code::

            "**Response** from the server" -- if it's waiting for the response.
            "OK" -- if it's not waiting for the response but sending went fine.
            "ERROR" -- Error.
        :rtype: str

    '''
    thea_globals.log.debug("message: %s" % message)
    try:
        #print("timeS1: ", time.time())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        #print("timeS2: ", time.time())
        msg = struct.pack('<l',len(message))+struct.pack('<l',0)+message
        #print(msg)
        s.sendall(msg)
        #print("timeS3: ", time.time())
        if waitForResponse:
            data = s.recv(1024)
        else:
#            print("waitForResponse: ", waitForResponse)
            data = "OK"
#        print("timeS4: ", time.time())
        s.close()
#        print("timeS5: ", time.time())
        thea_globals.log.debug("data.decode(utf-8): %s" % data.decode("utf-8"))
        return data.decode("utf-8")
    except:
        return 'ERROR'



# class to generate bmp file from mat.thea file
class Preview:
    '''Class to generate bmp file from mat.thea file

    :Example:

        >>> prevImageOb = Preview()
        >>> tempDir = tempfile.gettempdir()
        >>> outputImage = os.path.join(tempDir, "matPreview.bmp")
        >>> prevImageOb.outFile = outputImage
        >>> prevImageOb.read(extMatFile)

    '''
    def __init__(self):
        self.image = []
        self.lines = 0
        self.pixels = 0
        self.outFile = None
        self.centerColor = (0,0,0)

    def bmp_write(self, d,the_bytes):
        '''Write self.outfile bmp file

            :param d: dictionary of header values
            :type d: dict
            :param the_bytes: bytes to write
            :type the_bytes: binary array

        '''
        mn1 = struct.pack('<B',d['mn1'])
        mn2 = struct.pack('<B',d['mn2'])
        filesize = struct.pack('<L',d['filesize'])
        undef1 = struct.pack('<H',d['undef1'])
        undef2 = struct.pack('<H',d['undef2'])
        offset = struct.pack('<L',d['offset'])
        headerlength = struct.pack('<L',d['headerlength'])
        width = struct.pack('<L',d['width'])
        height = struct.pack('<L',d['height'])
        colorplanes = struct.pack('<H',d['colorplanes'])
        colordepth = struct.pack('<H',d['colordepth'])
        compression = struct.pack('<L',d['compression'])
        imagesize = struct.pack('<L',d['imagesize'])
        res_hor = struct.pack('<L',d['res_hor'])
        res_vert = struct.pack('<L',d['res_vert'])
        palette = struct.pack('<L',d['palette'])
        importantcolors = struct.pack('<L',d['importantcolors'])
        #create the outfile
        outfile = open(self.outFile,'wb')

        #write the header + the_bytes
        outfile.write(mn1+mn2+filesize+undef1+undef2+offset+headerlength+width+height+\
                      colorplanes+colordepth+compression+imagesize+res_hor+res_vert+\
                      palette+importantcolors+the_bytes)
        outfile.close()

    def read(self,filename):
        '''Read the mat.thea file, prepare bmp data and save bmp to self.outfile

            :param filename: filename of the mat.thea file
        '''

        matFile = open(filename, "rb")
        matFile.seek(0)
        matData = matFile.read()
        i = 0
        value = matData[i]+matData[i+1]+matData[i+2]+matData[i+3]

#        mylist = []
#        with open(filename, "rb") as f:
#            for i in range (0, len(matData)):
#                s = bytearray(matData)
##                s = struct.unpack('=BH', f.read(3))
##                mylist.append(s[0])
#            thea_globals.log.debug("Sky data: %s" % s)

#        byte_string = ''
#        char = matData
#        byte = ord(char)
#        # print byte
#        byte_string += chr(byte)
#        while char != "":
#            char = infile.read(1)
#            if char != "":
#                byte = ord(char)
#                # print byte
#                byte_string += chr(byte)
#                thea_globals.log.debug("Sky data: %s" % byte_string)
#        thea_globals.log.debug("Sky data: %s" % matData)
#        for k in matData:
#            if matData.find(\x05) >=0:
#    #            k = next(it)
#                illMap = matData.split(" ")
#                thea_globals.log.debug("Sky data: %s" % illMap )
#        text = data.decode('utf-8')
#        thea_globals.log.debug("Sky data: %s" % data[40:2000])
#        height ,width, = struct.unpack(">LL",  matData[0:8])
#        thea_globals.log.debug("Sky data: %s - %s" % (height, width))
#        thea_globals.log.debug("Sky data: %s" % matData)
#        thea_globals.log.debug("Sky data: %s" % len(matData))
#        for k in matData:
#            thea_globals.log.debug("Sky data: %s" % reflection)
        if value == 3:
            i += 4
            value = matData[i]+matData[i+1]+matData[i+2]+matData[i+3]
            if value == 0:
                i += 6*4
                #pixels = matData[i]+matData[i+1]+matData[i+2]+matData[i+3]
                pixels = (matData[i+3] << 24) + (matData[i+2] << 16) + (matData[i+1] << 8) + matData[i]
                i += 4
                #lines = matData[i]+matData[i+1]+matData[i+2]+matData[i+3]
                lines = (matData[i+3] << 24) + (matData[i+2] << 16) + (matData[i+1] << 8) + matData[i]
                self.lines = lines
                self.pixels = pixels
                thea_globals.log.debug("lines: %s, pixels: %s" % (self.lines, self.pixels))
#                dataDing = struct.unpack('11B',matData[0:16])
#                thea_globals.log.debug("Sky data: %s" % dataDing)
#                thea_globals.log.debug("Sky data len: %s" % len(matData))
                d = {
                'mn1':66,
                'mn2':77,
                'filesize':0,
                'undef1':0,
                'undef2':0,
                'offset':54,
                'headerlength':40,
                'width':lines,
                'height':pixels,
                'colorplanes':0,
                'colordepth':24,
                'compression':0,
                'imagesize':0,
                'res_hor':0,
                'res_vert':0,
                'palette':0,
                'importantcolors':0
                }

                i += 4

                pixelVals = []
                for l in range(0,self.lines):
                    line = []
                    for p in range(0,self.pixels):
                        r = matData[i]
                        i += 1
                        g = matData[i]
                        i += 1
                        b = matData[i]
                        i += 1
                        line.append((r,g,b))
                    pixelVals.append(line)
                #flip render.image_settings.color_mode in y
                flippedVals = []
                for l in pixelVals[::-1]:
                    flippedVals.append(l)

                pixs = []
                pixs.append(pixelVals[int(self.lines/2)-1][int(self.pixels/2)])
                pixs.append(pixelVals[int(self.lines/2)-1][int(self.pixels/2)-1])
                pixs.append(pixelVals[int(self.lines/2)][int(self.pixels/2)-1])
                pixs.append(pixelVals[int(self.lines/2)][int(self.pixels/2)])
                ravg = (pixs[0][0]+pixs[1][0]+pixs[2][0]+pixs[3][0])/3/255
                gavg = (pixs[0][1]+pixs[1][1]+pixs[2][1]+pixs[3][1])/3/255
                bavg = (pixs[0][2]+pixs[1][2]+pixs[2][2]+pixs[3][2])/3/255
                self.centerColor = (ravg, gavg, bavg)


                the_bytes = b''
                len(pixelVals)-1
                pi = 0
                pixelVals = flippedVals
                for row in range(lines):# (BMPs are L to R from the bottom L row)
                    j = 0
                    for column in range(pixels):
                        r = pixelVals[pi][j][0]
                        g = pixelVals[pi][j][1]
                        b = pixelVals[pi][j][2]
                        j += 1
                        pixel = struct.pack('<BBB',b,g,r)
                        the_bytes = the_bytes + pixel
                    pi += 1
                    row_mod = (lines*d['colordepth']/8) % 4
                    if row_mod == 0:
                        padding = 0
                    else:
                        padding = (4 - row_mod)
                    padbytes = b''
                    for ip in range(int(padding)):
                        x = struct.pack('<B',0)
                        padbytes = padbytes + x
                    the_bytes = the_bytes + padbytes


                #call the bmp_write function with the
                #dictionary of header values and the
                #bytes created above.
                self.bmp_write(d,the_bytes)



        matFile.close()

    def getPixels(self):
        return self.pixels
    def getLines(self):
        return self.lines
    def getData(self):
        return self.image


FloatProperty= bpy.types.FloatProperty
IntProperty= bpy.types.IntProperty
BoolProperty= bpy.types.BoolProperty
EnumProperty= bpy.types.EnumProperty
CollectionProperty= bpy.types.CollectionProperty
StringProperty= bpy.types.StringProperty



def setPaths(scene, verbose=False):
    """Recognize required Thea and export paths

    :param scene: Blender scene
    :type scene: bpy_types.Scene
    :param verbose: enable to see verbose output in the stdout.
    :type verbose: bool

    :return: Tuple with (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile):
    :rtype: (str, str, str, str, str, str)
    """
    from . import thea_globals

    if(scene!=None):
        currentBlendFile = bpy.data.filepath
        currentBlendDir = os.path.dirname(currentBlendFile)
        thea_globals.currentBlendDir = currentBlendDir
        thea_globals.currentBlendFile = currentBlendFile
        if os.path.isdir(scene.render.filepath):
#             thea_globals.log.debug('****is dir: %s' % scene.render.filepath)
            exportPath = bpy.path.abspath(scene.render.filepath)
        else:
            exportPath = bpy.path.abspath(currentBlendDir)

        thea_globals.exportPath = exportPath

    else:
        currentBlendFile = ""
        currentBlendDir = ""
        exportPath = ""


    if thea_globals.theaPath is not None and len(thea_globals.currentBlendFile) > 2:
#         thea_globals.log.debug("output path: %s %s " % (thea_globals.exportPath, os.path.abspath(thea_globals.exportPath)))
#         thea_globals.log.debug('exportPath: %s' % thea_globals.exportPath)
#         thea_globals.log.debug('theaPath: %s'% thea_globals.theaPath)
#         thea_globals.log.debug('theaDir: %s' % thea_globals.theaDir)
#         thea_globals.log.debug('currentBlendDir: %s' % thea_globals.currentBlendDir)
#         thea_globals.log.debug('currentBlendFile: %s' % thea_globals.currentBlendFile)
#         thea_globals.log.debug('useLut: %s' % thea_globals.getUseLUT())
        return(thea_globals.exportPath, thea_globals.theaPath, thea_globals.theaDir, thea_globals.dataPath, thea_globals.currentBlendDir, thea_globals.currentBlendFile)



    theaPath = False
    dataPath = ""
    isMac = False

    theaDir = ""
    for path in bpy.utils.script_paths():
        thFileName = os.path.join(path,"addons","TheaForBlender","TheaConfig.txt")
        if verbose:
            thea_globals.log.debug('th config file: %s' % thFileName)
        if os.path.exists(thFileName):
            thFile = open(thFileName, "r")
            for line in thFile:
                ls = line.split("=")
                if ls[0] == "Application\ Path":
                    theaDir = os.path.dirname(ls[1].strip())
                    theaPath = ls[1].strip()
                if ls[0] == "Data\ Path":
                    dataPath = ls[1].strip()
            thFile.close()

    if theaDir == "":
        config = configparser.SafeConfigParser()
        configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini")
        config.read(configPath)
        if config.has_section("PATHS"):
            theaDir = os.path.dirname(config["PATHS"].get("thea_applicationpath", ""))
            theaPath = config["PATHS"].get("thea_applicationpath", "")
            dataPath = config["PATHS"].get("thea_datapath", "")


    if theaDir == "":
        if os.name == "nt":
            theaPath = False
            theaDir = ""
            try:
                regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\Solid Iris\Thea Render')
                theaDir = winreg.QueryValueEx(regKey, 'Application Path')[0]
            except:
                theaDir = ""
            if theaDir == "":
                try:
                    regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Solid Iris\Thea Render')
                    theaDir = winreg.QueryValueEx(regKey, 'Application Path')[0]
                except:
                    theaDir = ""

            dataPath = ""
            try:
                regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\Solid Iris\Thea Render')
                dataPath = winreg.QueryValueEx(regKey, 'Data Path')[0]
            except:
                dataPath = ""
            if dataPath == "":
                try:
                    regKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Solid Iris\Thea Render')
                    #theaDir = winreg.QueryValueEx(regKey, 'Application Path')[0]
                    dataPath = winreg.QueryValueEx(regKey, 'Data Path')[0]
                except:
                    dataPath = None
            theaPath = os.path.join(theaDir,"thea.exe")
        if os.name == "posix":
            isMac = False
            homeDir = os.environ['HOME']
            thFileName = os.path.join(homeDir,".Thea Render")
            if os.path.exists(thFileName):
                thFile = open(thFileName, "r")
                for line in thFile:
                    ls = line.split("=")
                    if ls[0] == "Data\ Path":
                        dataPath = ls[1][:-1]
                    if ls[0] == "Application\ Path":
                        theaDir = ls[1][:-1]
                        if platform.architecture()[0] == '64bit':
                            theaPath = os.path.join(theaDir,"thea-x64")
                        else:
                            theaPath = os.path.join(theaDir,"thea")
                thFile.close()
            else:
                thFileName = os.path.join(homeDir,"Library/Preferences/Thea Render Preferences")
                if os.path.exists(thFileName):
                    isMac = True
                    thFile = open(thFileName, "r")
                    for line in thFile:
                        ls = line.split("=")
                        if ls[0] == "Data\ Path":
                            dataPath = ls[1][:-1]
                        if ls[0] == "Application\ Path":
                            theaDir = ls[1][:-1]
                            theaPath = os.path.join(theaDir,"thea")
                    thFile.close()
                else:
                    theaDir = ""

        if os.name == "mac":
            homeDir = os.environ['HOME']
            thFileName = os.path.join(homeDir,"Library/Preferences/Thea Render Preferences")
            if os.path.exists(thFileName):
                thFile = open(thFileName, "r")
                for line in thFile:
                    ls = line.split("=")
                    if ls[0] == "Data\ Path":
                        dataPath = ls[1][:-1]
                    if ls[0] == "Application\ Path":
                        theaDir = ls[1][:-1]
                        theaPath = os.path.join(theaDir,"thea")
                thFile.close()
            else:
                theaDir = ""
                dataPath = ""

    curtime = time.strftime( "%Y-%m-%d" ).split("-")






    firstFrame = True

    from . import thea_globals
    thea_globals.getConfig()


    thea_globals.log.debug("********output path: %s %s " % (exportPath, os.path.abspath(exportPath)))

    if verbose:
        thea_globals.log.debug("output path: %s %s " % (exportPath, os.path.abspath(exportPath)))
        thea_globals.log.debug('exportPath: %s' % exportPath)
        thea_globals.log.debug('theaPath: %s'% theaPath)
        thea_globals.log.debug('theaDir: %s' % theaDir)
        thea_globals.log.debug('currentBlendDir: %s' % currentBlendDir)
        thea_globals.log.debug('currentBlendFile: %s' % currentBlendFile)
        thea_globals.log.debug('useLut: %s' % thea_globals.getUseLUT())
    thea_globals.exportPath = os.path.abspath(exportPath)
    thea_globals.theaPath = theaPath
    thea_globals.theaDir = theaDir
    thea_globals.dataPath = dataPath
    thea_globals.currentBlendDir = currentBlendDir
    thea_globals.currentBlendFile = currentBlendFile
    return(os.path.abspath(exportPath), theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile)


def editMaterial(scene,material,exporter=None): #call Thea material editor to edit selected material
    '''Call Thea material editor to edit selected material

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param material: Blender material
        :type material: bpy_types.Material
        :param exporter: XMLExporter instance
        :type exporter: thea_exporter.XMLExporter
        :return: True
        :rtype: bool
    '''

    scn = scene
    currentBlendFile = bpy.data.filepath


    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)

    matFile = False
    try:
        if os.path.exists(os.path.abspath(bpy.path.abspath(material['thea_extMat']))):
            matFile = True
        else:
            matFile = False

    except: pass



    if matFile:
        fileName = os.path.abspath(bpy.path.abspath(material['thea_extMat']))
        args = []
        args.append(str(theaPath))
        args.append("-matlab")
        args.append("-acceptreject")
        args.append("-nosplash")
        args.append("-loadmat")
        args.append(fileName)
        args.append("-savemat")
        args.append(fileName)

    else:
        ma = ThMaterial()
        ma.setName(material.name)
        ma.blenderMat = material
        thMat = exporter.generateMaterialNew(ma)
        xmlFilename = currentBlendFile.replace('.blend', '_mat_'+ma.name+'.xml')
        try:
            tempDir = os.path.join(exportPath,"~thexport")
            if not os.path.isdir(tempDir):
                os.mkdir(tempDir)
            matDir = os.path.join(tempDir,"materials")
            if not os.path.isdir(matDir):
                os.mkdir(matDir)
            fileName = os.path.join(matDir,os.path.basename(xmlFilename))
            #print("fileName: ", fileName)
            matFile = open(fileName,"w")
            thMat.write(matFile)
            matFile.close()
        except:
            return False
        if os.name == "nt":
            command = "\"" +str(theaPath) + "\" -matlab -nosplash -loadmat " + fileName + " -savemat " + fileName + ".mat.thea"
        else:
            command = str(theaPath) + " -matlab -nosplash -loadmat " + fileName + " -savemat " + fileName + ".mat.thea" + " &"
        args = []
        args.append(str(theaPath))
        args.append("-matlab")
        args.append("-acceptreject")
        args.append("-threads")
        args.append("0")
        args.append("-nosplash")
        args.append("-loadmat")
        args.append(fileName)
        args.append("-savemat")
        args.append(fileName + ".mat.thea")
        #material['thea_extMat'] = bpy.path.relpath(fileName+".mat.thea")
        material['thea_extMat'] = fileName+".mat.thea"

    p = subprocess.Popen(args)
    p.wait()
    material['thea_extMat'] = material['thea_extMat']
    material.diffuse_color = material.diffuse_color
    return True

def isMaterialLinkLocal(filename):
    '''Check if material filename is located in the export path

        :param filename: file name of the material
        :type filename: string
        :return: True if it's in export path
        :rtype: bool
    '''

    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)

    tempDir = os.path.join(exportPath,"~thexport")
    matDir = os.path.abspath(os.path.join(tempDir,"materials"))
    if matDir == os.path.dirname(os.path.abspath(bpy.path.abspath(filename))):
        return True
    else:
        return False


def alreadyExported(meshName, mesh_objects):
    '''check if object is already in mesh_objects list

        :param meshName: name of the mesh
        :type: meshName: str
        :param mesh_objects: list of the objects
        :type mesh_objects: list
        :return: True if found
        :rtype: bool
    '''
    for oB in mesh_objects:
        if oB.meshName == meshName:
            return True

def exportCameras(scene,frame, anim=False, exporter=None, area=None, obList=None):
    '''Export visible cameras and add them to exporter cameraList

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param area: current 3d view area
        :type area: bpy_types.Area
        :param obList: list of objects to export (not used by now)
        :type obList: list

    '''

    renderData = scene.render

    resX=int(renderData.resolution_x*renderData.resolution_percentage*0.01)
    resY=int(renderData.resolution_y*renderData.resolution_percentage*0.01)

#   CHANGED > added 'dist' variable for dof object check later in the script
    global camOb, cam, camData, dist, zDist
    # export cameras
    for camOb in bpy.data.objects:
        if camOb.type == 'CAMERA':
            camData = camOb.data
            if camOb.is_visible(scene):
                cam = ThCamera()
                cam.name = camOb.name
#               CHANGED > Added pinhole + added DOFpercentage
                cam.pinhole = camOb.thea_pinhole
                cam.enableDOFpercentage = camOb.thea_enableDOFpercentage
                cam.pixels = resX
                cam.lines = resY

                if resX > resY:
                    fac = float(resX) / float(resY)
                else:
                    fac = 1

#               CHANGED > this checks if in object mode and measure distance between camera and dof object>returns dist as value
                mode = bpy.context.mode
                if mode == 'OBJECT':
                    cam.name = camOb.name
#                    obj2 = camData.dof_object
#                    print(obj2)
                    if camData.dof_object:
                        obj1 = cam.name
                        obj2 = camData.dof_object.name
                        obj1_loc = bpy.data.objects[obj1].location
                        obj2_loc = bpy.data.objects[obj2].location
                        dist = (obj1_loc - obj2_loc).length
                        zDist = dist
                        camData.dof_distance = dist # SET distance from object
                    else:
                        dist = camData.dof_distance

#                        print("***DOF Distance mode: ", dist)



                if camData.type == "PERSP":
                    cam.focalLength = camData.lens

#                   CHANGED > New check for distance/distance_object and check if pinhole is active
#                   CHANGED > to try, was getting error when nothing was changed from startup file
                    try:
                        aperture = camOb["aperture"]
                        DOFpercentage = camOb["thea_DOFpercentage"]
                    except: pass
#                    added this line to check none distance
                    if camData.dof_distance == 0 and camData.dof_object:
                    #                    cam.focusDistance = camData.dof_distance
                        cam.focusDistance = dist
#                        print("**DISTANCE:", dist)
#                        print("***PINHOLE CHECK: ", cam.pinhole)
#                        aperture = camOb["aperture"]
#                        print("***PINHOLE CHECK: ", camOb["aperture"])
                        try:
                            if cam.pinhole == 0:
#                                print("***PINHOLE CHECK A: ", cam.pinhole)
                                cam.fNumber = aperture
                            else:
                                cam.fNumber = "Pinhole"
                        except: pass
                        try:
                            if cam.enableDOFpercentage == 1:
                                #print("***PINHOLE CHECK: ", cam.pinhole)
                                cam.DOFpercentage = DOFpercentage
                            else:
                                cam.DOFpercentage = 0
                        except: pass
                    else:
                            cam.fNumber = 0
#                            print("APERTURE A - ALL 0:", aperture)

#                    cam.projection = getattr(camOb, 'thea_projection', 'Perspective')
                    cam.projection = getattr(camOb, "thea_projection")
#                    #    CHANGED > Added region render options
#                    cam.regionRender = scn.thea_regionRender
#                    cam.regionsettings = scn.thea_regionSettings

                    #   CHANGED > added diaphgrama and blades
                    cam.diaphragm = camOb.thea_diaphragma
                    cam.blades = camOb.thea_diapBlades
#                    print("***diap: ", camOb.thea_diaphragma)
#                    print("***Blades: ", cam.blades)
                    #cam.filmHeight = 32 / fac
#                     cam.filmHeight = camData.sensor_width / fac
                    if camData.sensor_fit == 'VERTICAL':
                        sensor_height =  camData.sensor_height
                        sensor_width = sensor_height * fac
                        cam.shiftLensX = sensor_height * camData.shift_x
                        cam.shiftLensY = sensor_height * camData.shift_y * -1
                    else:
                        sensor_width = camData.sensor_width
                        sensor_height = sensor_width / fac
                        cam.shiftLensX = sensor_width * camData.shift_x
                        cam.shiftLensY = sensor_width * camData.shift_y * -1
                    thea_globals.log.debug("width: %s, height: %s" % (sensor_width, sensor_height))
#                     cam.filmHeight = camData.sensor_height
#                     cam.shiftLensX = camData.sensor_width * camData.shift_x
#                     cam.shiftLensY = camData.sensor_height * camData.shift_y * -1
                    cam.filmHeight = sensor_height

                elif camData.type == "ORTHO":
                    cam.projection = "Parallel"
#                  CHANGED > Added different calculation
#                     cam.filmHeight = camData.ortho_scale * 563.333333 #* 750
#                     cam.focalLength = camData.ortho_scale * 563.333333 #* 750
#                    cam.filmHeight = 80 / camData.lens * 1000
                    if camData.sensor_fit == 'VERTICAL':
                        cam.filmHeight = camData.ortho_scale * 1000
                        thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.ortho_scale, camData.sensor_fit,fac))
                    elif camData.sensor_fit == 'HORIZONTAL' or 'AUTO':
                        cam.filmHeight = (camData.ortho_scale * 1000) / fac
                        thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.ortho_scale, camData.sensor_fit,fac))
                    cam.focalLength = camData.lens
#               CHANGED > New check for distance/distance_object and check if pinhole is active
                if camData.dof_distance >= 0:
#                    cam.focusDistance = camData.dof_distance
                    cam.focusDistance = dist
                    try:
                        if cam.pinhole == 0:
                            cam.fNumber = aperture
                        else:
                            cam.fNumber = "Pinhole"
                        #print("***PINHOLE CHECK: B", cam.pinhole)
                    except: pass
                    try:
                        if cam.enableDOFpercentage == 1:
                            #print("***PINHOLE CHECK: ", cam.pinhole)
                            cam.DOFpercentage = DOFpercentage
                        else:
                            cam.DOFpercentage = 0
                    except: pass
                else:
                    cam.fNumber = aperture
                    #print("***PINHOLE CHECK: C", cam.pinhole)
                cam.autofocus = camOb.autofocus
                cam.shutterSpeed = camOb.shutter_speed
                #      CHANGED > Z-Clip from DOF
                if (getattr(camOb, "thea_ZclipDOF")== True):
                    camData.clip_start = zDist
                    cam.zClippingNear = setattr(camOb, "thea_zClippingNear", True)
                    cam.zClippingFar = setattr(camOb, "thea_zClippingFar", True)
#                    thea_globals.log.debug("*** ZdepthDOF Dist: %s" % zDist)
                    camData.clip_end = camOb.thea_ZclipDOFmargin
#                if (getattr(camOb, "thea_ZclipDOF")== True):
#                    cam.zClippingNearDistance = camData.thea_ZclipDOF
#                    cam.zClippingFarDistance =  camData.thea_ZclipDOFmargin
                else:
                    cam.zClippingNear = getattr(camOb, "thea_zClippingNear")
                    cam.zClippingNearDistance =  camData.clip_start
                    cam.zClippingFar = getattr(camOb, "thea_zClippingFar")
                    cam.zClippingFarDistance =  camData.clip_end

                camM = camOb.matrix_world
                cam.frame = Transform(\
                camM[0][0], -camM[0][1], -camM[0][2],
                camM[1][0], -camM[1][1], -camM[1][2],
                camM[2][0], -camM[2][1], -camM[2][2],
                camM[0][3],  camM[1][3],  camM[2][3])

                startObMatrixAssigned = mathutils.Matrix((\
                (camM[0][0], -camM[0][1], -camM[0][2], camM[0][3]),
                (camM[1][0], -camM[1][1], -camM[1][2], camM[1][3]),
                (camM[2][0], -camM[2][1], -camM[2][2], camM[2][3]),
                (0.0, 0.0, 0.0, 1.0)))

                i = 0
                for layer in camOb.layers:
                   if layer:
                       if i>9:
                           cam.layer = i-9
                       else:
                           cam.layer = i
                   i += 1

                #print("camera: ", cam.name)

                #export animation data
                if scene.thea_ExportAnimation == True and (camOb.thExportAnimation == True or is_Animated(camOb)):
                    currFrame = scene.frame_current
                    startFrame=scene.frame_start
                    endFrame=scene.frame_end
                    #startFrame=currFrame-5
                    #endFrame=currFrame+5
                    im = InterpolatedMotion()
                    im.identifier = "Position Modifier"
                    im.enabled = True
                    im.duration = endFrame+1-startFrame
                    startCamM = camM
                    for frame in range(startFrame, endFrame+1, 1):
                        #print ("\n\nExporting animation frame: ",frame)
                        scene.frame_set(frame)
                        camM = camOb.matrix_world
                        ob_matrix_world_Assigned = mathutils.Matrix((\
                        (camM[0][0], -camM[0][1], -camM[0][2], camM[0][3]),
                        (camM[1][0], -camM[1][1], -camM[1][2], camM[1][3]),
                        (camM[2][0], -camM[2][1], -camM[2][2], camM[2][3]),
                        (0.0, 0.0, 0.0, 1.0)))

                        camMat = startObMatrixAssigned.inverted() * ob_matrix_world_Assigned
                        #camMat = startCamM * camOb.matrix_world.inverted()

                        frame = Transform(\
                        camMat[0][0], camMat[0][1], camMat[0][2],
                        camMat[1][0], camMat[1][1], camMat[1][2],
                        camMat[2][0], camMat[2][1], camMat[2][2],
                        camMat[0][3], camMat[1][3], camMat[2][3])
                        im.addNode(scn.frame_current, frame)

                    scene.frame_set(currFrame)
                    cam.interpolatedMotion = im
                if scene.render.use_border:
                    cam.renderRegion = True
#                     cam.region = "(%s,%s) - (%s,%s)" % (resX*scene.render.border_min_x, resY*scene.render.border_min_y, resX*scene.render.border_max_x, resY*scene.render.border_max_y)
                    cam.region = "(%s,%s)-(%s,%s)" % (int(resX*scene.render.border_min_x), int(cam.lines-resY*scene.render.border_max_y), int(resX*scene.render.border_max_x), int(cam.lines-resY*scene.render.border_min_y))
                exporter.addCamera(cam)

    # export current view
    if area:
        camM = area.spaces.active.region_3d.view_matrix.inverted()
        #camM = area.spaces.active.region_3d.perspective_matrix.inverted()
#         #print("camM: ",camM)
        for region in area.regions:
            if region.type == 'WINDOW':
                viewWidth = region.width
                viewHeight = region.height
                break
        camData = area.spaces.active


        offset = area.spaces.active.region_3d.view_camera_offset
        cam = ThCamera()
        cam.name="IR view"
        cam.pixels = viewWidth
        cam.lines = viewHeight

        if viewWidth > viewHeight:
            fac = float(viewWidth) / float(viewHeight)
        else:
         fac = 1

#                     cam.focalLength = (camData.lens+area.spaces.active.region_3d.view_camera_zoom) /2

        cam.shiftLensX =  0
        cam.shiftLensY =  0

        cam.zClippingNear = True
        cam.zClippingNearDistance =  camData.clip_start
        cam.zClippingFar = True
        cam.zClippingFarDistance =  camData.clip_end

#         if (area.spaces.active.region_3d.view_perspective == 'CAMERA'):
#             zoom = area.spaces.active.region_3d.view_camera_zoom;
#             zoom = (1.41421 + zoom/50.0)
#             zoom *= zoom
#             zoom = 2.0/zoom
#             cam.focalLength = camData.lens / zoom /2
#             cam.shiftLensX =  32 * offset[0] / zoom
#             cam.shiftLensY =  (32 * offset[1] * -1) / fac / zoom
#
        ##print("cam.focalLength: ", cam.focalLength, camData.lens,area.spaces.active.region_3d.view_camera_zoom, fac, " offset: ",cam.shiftLensX, cam.shiftLensY)
#   CHANGED > added new distance check for object or distance
#        if dist == 'None':
#            dist = 1
        try:
            cam.focusDistance = dist
        except:
            pass
        thea_globals.log.debug("camData.camera: %s" % camData.camera)
        thea_globals.log.debug("area.spaces.active.region_3d.view_perspective: %s" % area.spaces.active.region_3d.view_perspective)
        if camData.camera.data.type != 'ORTHO':
            cam.filmHeight = camData.camera.data.ortho_scale * 1000
        else:
            cam.filmHeight = 32 / fac
        cam.focalLength = camData.lens / 2
#         cam.filmHeight = camData.camera.sensor_height
        if (area.spaces.active.region_3d.view_perspective == 'CAMERA'):
            cam.pixels = resX
            cam.lines = resY
            cam.focalLength = camData.camera.data.lens
            cam.filmHeight = camData.camera.data.sensor_height
            cam.shiftLensX = camData.camera.data.sensor_width * camData.camera.data.shift_x
            cam.shiftLensY = camData.camera.data.sensor_width * camData.camera.data.shift_y * -1
#             cam.filmHeight = (32 * (32 / camData.camera.data.sensor_width)) / fac
#             cam.filmHeight = 32 / fac
#             cam.focalLength = camData.camera.data.lens
        else:
            cam.filmHeight = 32 / fac
            cam.focalLength = camData.lens / 2
#         thea_globals.log.debug("camData.camera.data.sensor_height: %s" % camData.camera.data.sensor_height)
#         cam.filmHeight = camData.camera.data.sensor_height / 2
        cam.fNumber = 0
#        if camData.camera.type != 'ORTHO':
#            cam.projection = "Parallel"
#            if camData.camera.data.sensor_fit == 'VERTICAL':
#                cam.filmHeight = camData.camera.data.ortho_scale * 1000
#                thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.camera.data.ortho_scale, camData.camera.data.sensor_fit,fac))
#            elif camData.camera.data.sensor_fit == 'HORIZONTAL' or 'AUTO':
#                cam.filmHeight = (camData.camera.data.ortho_scale * 1000) / fac
#                thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.camera.data.ortho_scale, camData.camera.data.sensor_fit,fac))
#            cam.focalLength = camData.camera.data.lens



        cam.frame = Transform(\
                    camM[0][0], -camM[0][1], -camM[0][2],
                    camM[1][0], -camM[1][1], -camM[1][2],
                    camM[2][0], -camM[2][1], -camM[2][2],
                    camM[0][3],  camM[1][3],  camM[2][3])

        exporter.addCamera(cam)
    else:
        try:
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    break
            camM = area.spaces.active.region_3d.view_matrix.inverted()
            #camM = area.spaces.active.region_3d.perspective_matrix.inverted()
            #print("camM: ",camM)
            for region in area.regions:
                if region.type == 'WINDOW':
                    viewWidth = region.width
                    viewHeight = region.height
                    break
            camData = area.spaces.active

            cam = ThCamera()
            cam.name="3D view"
            cam.pixels = viewWidth
            cam.lines = viewHeight

            cam.zClippingNear = True
            cam.zClippingNearDistance =  camData.clip_start
            cam.zClippingFar = True
            cam.zClippingFarDistance =  camData.clip_end

            if viewWidth > viewHeight:
                fac = float(viewWidth) / float(viewHeight)
            else:
             fac = 1

            cam.focalLength = camData.lens /2
#             cam.focalLength = (camData.lens+area.spaces.active.region_3d.view_camera_zoom) /2
            #print("cam.focalLength: ", cam.focalLength, camData.lens,area.spaces.active.region_3d.view_camera_zoom)
            cam.focusDistance = dist
#             cam.filmHeight = 32 / fac
            cam.filmHeight = camData.sensor_height
#   CHANGED > so it also checks correct diaphgrama
            cam.fNumber = aperture
            cam.diaphragm = camData.thea_diaphragma
            cam.blades = camData.thea_diapBlades


            cam.frame = Transform(
                        camM[0][0], -camM[0][1], -camM[0][2],
                        camM[1][0], -camM[1][1], -camM[1][2],
                        camM[2][0], -camM[2][1], -camM[2][2],
                        camM[0][3],  camM[1][3],  camM[2][3])

            exporter.addCamera(cam)
        except:
            pass

def exportLights(scene,frame, anim=False, exporter=None, obList=None):
    '''Export visible light and add them to exporter lightList

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param obList: list of objects to export
        :type obList: list

    '''

    light_objects = []

    if bpy.context.scene.thea_ir_running:
        obList = scn.objects


    for ob in obList:
        exportOb = False
        renderObject = True
        if ob.is_visible(scn):
              if ob.type == 'LAMP':
                  light_objects.append(ob)


    for lightOb in light_objects:
        lightData = lightOb.data
        omni=PointLight()
        omni.name=lightOb.name
        lM = lightOb.matrix_world
        ##print("lM: ", lM)
        omni.frame = Transform(\
        lM[0][0], -lM[0][1], -lM[0][2],
        lM[1][0], -lM[1][1], -lM[1][2],
        lM[2][0], -lM[2][1], -lM[2][2],
        lM[0][3],  lM[1][3],  lM[2][3])


        startObMatrixAssigned = mathutils.Matrix((\
        (lM[0][0], -lM[0][1], -lM[0][2], lM[0][3]),
        (lM[1][0], -lM[1][1], -lM[1][2], lM[1][3]),
        (lM[2][0], -lM[2][1], -lM[2][2], lM[2][3]),
        (0.0, 0.0, 0.0, 1.0)))


        if scene.thea_ExportAnimation == True and (lightOb.thExportAnimation == True or is_Animated(lightOb)):
            lightMInverted = lM.inverted()
            currFrame = scene.frame_current
            startFrame=scene.frame_start
            endFrame=scene.frame_end
            #startFrame=currFrame-5
            #endFrame=currFrame+5
            im = InterpolatedMotion()
            #im.identifier = "Position Modifier"
            im.enabled = True
            im.duration = endFrame+1-startFrame
            for frame in range(startFrame, endFrame+1, 1):
                #print ("\n\nExporting animation frame for lightsource: ",frame)
                scene.frame_set(frame)
                lM = lightOb.matrix_world
                #lightM = lightOb.matrix_world*lightMInverted
                #lightM = lightMInverted * lightOb.matrix_world
                ob_matrix_world_Assigned = mathutils.Matrix((\
                (lM[0][0], -lM[0][1], -lM[0][2], lM[0][3]),
                (lM[1][0], -lM[1][1], -lM[1][2], lM[1][3]),
                (lM[2][0], -lM[2][1], -lM[2][2], lM[2][3]),
                (0.0, 0.0, 0.0, 1.0)))

                lightM = startObMatrixAssigned.inverted() * ob_matrix_world_Assigned

                frame = Transform(\
                lightM[0][0], lightM[0][1], lightM[0][2],
                lightM[1][0], lightM[1][1], lightM[1][2],
                lightM[2][0], lightM[2][1], lightM[2][2],
                lightM[0][3],  lightM[1][3],  lightM[2][3])
                im.addNode(scn.frame_current, frame)

            scene.frame_set(currFrame)
            omni.interpolatedMotion = im

        bRgb = tuple([c for c in lightData.color])
        omni.emitter=RgbTexture(lightData.color[0], lightData.color[1], lightData.color[2])
#        changed > to emittancePower like in studio and added efficacy
        omni.multiplier=lightData.thea_EmittancePower#*10
        omni.efficacy = lightData.thea_EmittanceEfficacy
#        changed > to Attenuation checker like in studio
        thea_globals.log.debug("*** Light Name: %s - Type: %s" % (lightData.name, lightData.type))
        if lightData.type == 'SUN':
            att = lightData.thea_SunAttenuation
        else:
#            lightData.type != 'SPOT' and lightData.type != 'AREA' and lightData.type != 'HEMI':
            att = lightData.thea_EmittanceAttenuation
            if att == 'Inverse Square':
                omni.attenuation = 'Inverse Square'
            if att == 'Inverse':
                omni.attenuation = 'Inverse'
            if att == 'None':
                omni.attenuation = 'None'



        if lightData.type == 'SPOT' or lightData.type == 'AREA':
            ltextures = lightData.texture_slots
    #        changed > to emittancePower like in studio
            omni.multiplier=lightData.thea_EmittancePower#*10
            if len(ltextures) > 0:
                omni.type = "Spot"
                for ltex in ltextures:
                    try:
                        texType = ltex.texture.type
                    except:
                        texType = None
                    if (texType == 'IMAGE'):
                        (shortname, extension) = os.path.splitext(ltex.texture.image.filepath)
                        if extension == ".ies":
                            omni.type = "IES"
                            omni.iesfile = ltex.texture.image.filepath
                    #        changed > to emittancePower like in studio
                            omni.multiplier=lightData.thea_IESMultiplier#*10
#                        CHANGED > Added check for projector, lights can also have texture
                        if lightData.thea_enableProjector:
                            omni.type = "Projector"
                            omni.emitter = BitmapTexture(ltex.texture.image.filepath)
                            omni.emitter.scaleX = ltex.scale[0]
                            omni.emitter.scaleY = ltex.scale[1]
#                           CHANGED > Added wifth and height values for input
                            omni.width = lightData.thea_ProjectorWidth
                            omni.height = lightData.thea_ProjectorHeight
#                       CHANGED > Added texture for spotlights
                        if lightData.thea_TextureFilename != 'None':
                            omni.type = "Spot"
                            omni.emitter = BitmapTexture(ltex.texture.image.filepath)
                            omni.emitter.scaleX = ltex.scale[0]
                            omni.emitter.scaleY = ltex.scale[1]
#                           CHANGED > Added wifth and height values for input
                            omni.width = lightData.thea_ProjectorWidth
                            omni.height = lightData.thea_ProjectorHeight
                        if lightData.type == 'AREA':
                            omni.type = "Omni"
                            omni.emitter = BitmapTexture(ltex.texture.image.filepath)
                            omni.emitter.scaleX = ltex.scale[0]
                            omni.emitter.scaleY = ltex.scale[1]
#                           CHANGED > Added wifth and height values for input
                            omni.width = lightData.thea_ProjectorWidth
                            omni.height = lightData.thea_ProjectorHeight
#                        else:
#                            omni.type = "Projector"
#                            omni.emitter = BitmapTexture(ltex.texture.image.filepath)
#                            omni.emitter.scaleX = ltex.scale[0]
#                            omni.emitter.scaleY = ltex.scale[1]
##                           CHANGED > Added wifth and height values for input
#                            omni.width = lightData.thea_ProjectorWidth
#                            omni.height = lightData.thea_ProjectorHeight
#                            omni.width = (lightData.spot_size * 57.3) / 48.5
#                            omni.height = ((lightData.spot_size * (1 - lightData.spot_blend)) * 57.3) / 48.5

#                       CHANGED > Added Tone settings for lamp texture these where missing
                        omni.emitter.invert = bpy.data.textures[ltex.name].thea_TexInvert
                        omni.emitter.gamma = bpy.data.textures[ltex.name].thea_TexGamma
                        omni.emitter.red = bpy.data.textures[ltex.name].thea_TexRed
                        omni.emitter.green = bpy.data.textures[ltex.name].thea_TexGreen
                        omni.emitter.blue = bpy.data.textures[ltex.name].thea_TexBlue
                        omni.emitter.brightness = bpy.data.textures[ltex.name].thea_TexBrightness
                        omni.emitter.contrast = bpy.data.textures[ltex.name].thea_TexContrast
                        omni.emitter.saturation = bpy.data.textures[ltex.name].thea_TexSaturation
                        omni.emitter.clampMax = bpy.data.textures[ltex.name].thea_TexClampMax
                        omni.emitter.clampMin = bpy.data.textures[ltex.name].thea_TexClampMin

            if lightData.thea_enableProjector:
                omni.type = "Projector"
#                           CHANGED > Added wifth and height values for input
                omni.width = lightData.thea_ProjectorWidth
                omni.height = lightData.thea_ProjectorHeight
            else:
                omni.type = "Spot"
#                CHANGED > Added IES check here, light would still render as ies if IES was off
            if getattr(lightData, "thea_IESFilename") and lightData.thea_enableIES:
                omni.type = "IES"
                omni.iesfile = os.path.abspath(bpy.path.abspath(getattr(lightData, "thea_IESFilename")))
        #        changed > to emittancePower like in studio
                omni.multiplier=lightData.thea_IESMultiplier#*10
            if lightData.type != 'AREA':
                omni.falloff = lightData.spot_size * 57.295779 #57.3
                omni.hotspot = (lightData.spot_size * (1 - lightData.spot_blend)) * 57.295779 #57.3
            #print("energy: ", lightData.energy)

        if lightData.type == 'AREA':
#            ltextures = lightData.texture_slots
#            if len(ltextures) > 0:
#                omni.type = "Omni"
#                for ltex in ltextures:
#                    try:
#                        texType = ltex.texture.type
#                    except:
#                        texType = None
#                    if (texType == 'IMAGE'):
#                        (shortname, extension) = os.path.splitext(ltex.texture.image.filepath)
#                        omni.type = "Omni"
#                        omni.emitter = BitmapTexture(ltex.texture.image.filepath)
#                        omni.emitter.scaleX = ltex.scale[0]
#                        omni.emitter.scaleY = ltex.scale[1]
##                           CHANGED > Added wifth and height values for input
#                        omni.width = lightData.thea_ProjectorWidth
#                        omni.height = lightData.thea_ProjectorHeight
            omni.type = "Omni"
            omni.multiplier = lightData.thea_EmittancePower#*10
            omni.sun = False
            omni.softshadow = True
            omni.softradius = lightData.size
        elif (getattr(lightData, 'shadow_method', 'False') == "RAY_SHADOW") and (getattr(lightData, 'shadow_ray_samples') > 1):
            omni.softshadow = True
            omni.softradius = lightData.shadow_soft_size


        omni.unit = getattr(lightData, "thea_EmittanceUnit")
#        and omni.name.lower() == "sun"
        if lightData.type == 'POINT':
            ltextures = lightData.texture_slots
            omni.type = "Omni"
            omni.multiplier = lightData.thea_EmittancePower#*10
            omni.sun = False
            if len(ltextures) > 0:
                for ltex in ltextures:
                    try:
                        texType = ltex.texture.type
                    except:
                        texType = None
                    if (texType == 'IMAGE'):
                        (shortname, extension) = os.path.splitext(ltex.texture.image.filepath)
                        if lightData.thea_TextureFilename != 'None':
                            omni.emitter = BitmapTexture(ltex.texture.image.filepath)
                            omni.emitter.scaleX = ltex.scale[0]
                            omni.emitter.scaleY = ltex.scale[1]
#                           CHANGED > Added wifth and height values for input
                            omni.width = lightData.thea_ProjectorWidth
                            omni.height = lightData.thea_ProjectorHeight

#                       CHANGED > Added Tone settings for lamp texture these where missing
                        omni.emitter.invert = bpy.data.textures[ltex.name].thea_TexInvert
                        omni.emitter.gamma = bpy.data.textures[ltex.name].thea_TexGamma
                        omni.emitter.red = bpy.data.textures[ltex.name].thea_TexRed
                        omni.emitter.green = bpy.data.textures[ltex.name].thea_TexGreen
                        omni.emitter.blue = bpy.data.textures[ltex.name].thea_TexBlue
                        omni.emitter.brightness = bpy.data.textures[ltex.name].thea_TexBrightness
                        omni.emitter.contrast = bpy.data.textures[ltex.name].thea_TexContrast
                        omni.emitter.saturation = bpy.data.textures[ltex.name].thea_TexSaturation
                        omni.emitter.clampMax = bpy.data.textures[ltex.name].thea_TexClampMax
                        omni.emitter.clampMin = bpy.data.textures[ltex.name].thea_TexClampMin
        if lightData.type == 'SUN':
    #        changed > to emittancePower like in studio
            omni.multiplier=lightData.thea_EmittancePower#*10
            omni.radiusMultiplier=getattr(lightData, "thea_radiusMultiplier")
            omni.unit = getattr(lightData, "thea_SunEmittanceUnit","W/nm/sr")
#            CHANGED > Get sun Attenuation
            omni.attenuation = lightData.thea_SunAttenuation
            omni.efficacy = lightData.thea_EmittanceEfficacy
            omni.sun = True
            if lightData.thea_enableLamp == True:
                exporter.environmentOptions.overrideSun = True
            else:
                exporter.environmentOptions.overrideSun = False
            exporter.environmentOptions.sunDirectionX = lM[0][2]
            exporter.environmentOptions.sunDirectionY = lM[1][2]
            exporter.environmentOptions.sunDirectionZ = lM[2][2]

        i = 0
        for layer in lightOb.layers:
           if layer:
               if i>9:
                   omni.layer = i-9
               else:
                   omni.layer = i
           i += 1
#       CHANGED > Set manualSun here
        omni.enableLamp = getattr(lightData, "thea_enableLamp")
#        thea_globals.log.debug("Sun is enabled: %s" % omni.enableLamp)
        omni.manualSun = getattr(lightData, "thea_manualSun")
        thea_globals.log.debug("Sun is manual: %s" % omni.manualSun)
        omni.shadow = getattr(lightData, "thea_enableShadow")
        omni.softshadow = getattr(lightData, "thea_enableSoftShadow")
        omni.softradius = getattr(lightData, "thea_softRadius")
        omni.globalPhotons = getattr(lightData, "thea_globalPhotons")
        omni.causticPhotons = getattr(lightData, "thea_causticPhotons")
        omni.minRays = getattr(lightData, "thea_minRays")
        omni.maxRays = getattr(lightData, "thea_maxRays")
        omni.bufferIndex = getattr(lightData, "thea_bufferIndex")

#         #print("isinstance(omni.emitter, BitmapTexture): ", isinstance(omni.emitter, BitmapTexture))
#         #print("thea_TextureFilename: ", os.path.abspath(bpy.path.abspath(getattr(lightData, "thea_TextureFilename"))))
#         if isinstance(omni.emitter, BitmapTexture) == False:
#             if os.path.exists(os.path.abspath(bpy.path.abspath(getattr(lightData, "thea_TextureFilename")))):
#                 omni.emitter = BitmapTexture(os.path.abspath(bpy.path.abspath(getattr(lightData, "thea_TextureFilename"))))

        #export animation data

        exporter.addPointLight(omni)



def exportLibraries(scene,frame, anim=False, exporter=None, obList=None):
    '''Export libraries and add them to exporter objects lists

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param obList: list of objects to export
        :type obList: list

    '''


    prevOb = None
    firstOb = True
    for ob in obList:
        exportOb = False
        renderObject = True
        if ob.is_visible(scn):
                exportOb = True
        if exportOb:
              obType = ob.type
              if obType == 'EMPTY' and ob.dupli_group and ob.dupli_type=="GROUP":
                if not prevOb:
                    prevOb = ob
                try:
                    ob.dupli_list_create(scene)
                except:
                    pass

                if (prevOb.dupli_group.name == ob.dupli_group.name) and not firstOb: #if dupli grup is the same then add package
                    package = Package()
                    package.name = ob.name
                    package.alias = "%s:%s" % (ob.dupli_group.name, os.path.basename(ob.dupli_group.library.filepath).replace('.blend','') if ob.dupli_group.library else "local")
                    obD_mat = ob.matrix_world
                    frame = [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                             obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                             obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                    package.addFrame(frame)
                    #print("Adding package: ", package.name)
                    exporter.addPackage(package)
                else: # if it's first object of the grup then export proxy and add package
                    #print("group change from %s to %s" % (prevOb.dupli_group.name, ob.dupli_group.name))
                    #print("ob.name: ", ob.name)
                    #print("lenob.dupli_list: ", len(ob.dupli_list))
                    mainExpObject = exportObject()
                    mainExpObject.name = "%s:%s" % (ob.dupli_group.name, os.path.basename(ob.dupli_group.library.filepath).replace('.blend','') if ob.dupli_group.library else "local")
                    mainExpObject.meshName = mainExpObject.name
                    mainExpObject.matrix = ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                                     (0.0, 1.0, 0.0, 0.0),
                                     (0.0, 0.0, 1.0, 0.0),
                                     (0.0, 0.0, 0.0, 1.0))
                    dupobs = [(dob.object, dob.matrix, dob.object.matrix_basis) for dob in ob.dupli_list]
                    for obG, dupob_mat, dupob_mat_orig in dupobs:
                        obGType = obG.type
#                         #print("obG: ", obGType)
                        if obGType in ('MESH', 'CURVE', 'FONT'):
                           name = "%s:%s:%s" %(ob.name,ob.dupli_group.name,obG.name)
                           if obG.library:
                                meshName = "%s:%s:%s" % (ob.name,obG.library.filepath.replace('.blend',''),obG.data.name)
                           else:
                                meshName = obG.data.name
                           obName = name
                           emptyMatrix = ob.matrix_world
                           obGMatrix = obG.matrix_world
                           multMatrix = emptyMatrix * obGMatrix
                           mat = dupob_mat
                           mat = emptyMatrix.inverted() * dupob_mat
                           expOb = exportObject()
                           expOb.blenderObject = obG
                           expOb.matrix = mat
                           expOb.name = obName
                           expOb.meshName = meshName
                           #expOb.meshName = obName
                           #expOb.name = "obName"
                           #expOb.meshName = "meshName"
                           expOb.isProxy = True
#                            #print("expOb: ", expOb, expOb.blenderObject, expOb.name, expOb.meshName)
                           mainExpObject.subobjects.append(expOb)
#                  CHANGED > Added better time notation
                    t1 = datetime.datetime.now()
#                    exporter.writeModelBinary(scn, mainExpObject, frame, anim)
                    # CHANGED > Still used old code
                    exporter.writeModelBinaryNew(scn, mainExpObject, frame, anim)
                    t2 = datetime.datetime.now()
                    totalTime = t2-t1
                    minutes = totalTime.seconds/60
                    seconds = totalTime.seconds%60
                    microseconds = totalTime.microseconds%1000000
                    result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
                    thea_globals.log.debug("Exporting object Library: %s > %s sec" % (ob.name, result))
                    package = Package()
                    package.name = ob.name
                    package.alias = "%s:%s" % (ob.dupli_group.name, os.path.basename(ob.dupli_group.library.filepath).replace('.blend','') if ob.dupli_group.library else "local")
                    obD_mat = ob.matrix_world
                    frame = [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                             obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                             obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                    package.addFrame(frame)
                    exporter.addPackage(package)
                    del(mainExpObject)
                ob.dupli_list_clear()
                prevOb = ob
                firstOb = False


def exportDupliObjects(scene,frame, anim=False, exporter=None, obList=None):
    '''Export dupli objects and add them to exporter objects lists

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param obList: list of objects to export
        :type obList: list

    '''


    mesh_objects = []
    prevOb = None
    firstOb = True
    for ob in obList:
        exportOb = False
        renderObject = True
        if ob.is_visible(scn):
                exportOb = True
        if exportOb:
              obType = ob.type
              if obType == 'MESH' and (ob.dupli_type in ('VERTS', 'FACES')):
                try:
                    ob.dupli_list_create(scene)
                except:
                    pass
                # export proxy objects for children
                for obj in ob.children:
                    name = obj.name
                    meshName = obj.data.name
                    obName = name
                    obD_mat = obj.matrix_world
                    expOb = exportObject()
                    expOb.blenderObject = obj
                    expOb.matrix = obD_mat
                    expOb.name = obName
                    expOb.meshName = meshName
                    expOb.isProxy = True
                    mesh_objects.append(expOb)
                    del(expOb)
                    #add packages with dupli objects
                    package = Package()
                    package.name = obj.name
                    package.alias = obj.name
                    for dupOb in ob.dupli_list:
                        if dupOb.object == obj:
                            obD_mat = dupOb.matrix
                            frame =   [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                                       obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                                       obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                            package.addFrame(frame)
                    exporter.addPackage(package)

                ob.dupli_list_clear()


    for ob in mesh_objects:
#       CHANGED > Added better time notation
        t1 = datetime.datetime.now()
        exporter.writeModelBinaryNew(scn, ob, frame, anim)
        t2 = datetime.datetime.now()
        totalTime = t2-t1
        minutes = totalTime.seconds/60
        seconds = totalTime.seconds%60
        microseconds = totalTime.microseconds%1000000
        result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
        thea_globals.log.debug("Exporting object DupliObject: %s > %s sec" % (ob.name, result))



def exportParticles(scene,frame, anim=False, exporter=None, obList=None):
    '''Export particle systems and add them to exporter objects lists

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param obList: list of objects to export
        :type obList: list
    '''

    particle_objects = []
    mesh_objects = []

    for ob in obList:
        exportOb = False
        renderObject = True

        if ob.is_visible(scn):
                exportOb = True
                for mod in ob.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
                        psys = mod.particle_system
#                         if psys.settings.type == 'EMITTER':
                        thea_globals.log.debug("psys.settings.render_type: %s" % psys.settings.render_type)
                        if psys.settings.render_type=='OBJECT' and psys.settings.dupli_object:
                              obj = psys.settings.dupli_object
                              thea_globals.log.debug("psys.settings.dupli_object: %s" % psys.settings.dupli_object)
                              name = obj.name
                              meshName = obj.data.name
                              obName = name
                              obD_mat = obj.matrix_world
                              obD_mat = ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                                           (0.0, 1.0, 0.0, 0.0),
                                           (0.0, 0.0, 1.0, 0.0),
                                           (0.0, 0.0, 0.0, 1.0))
                              expOb = exportObject()
                              expOb.blenderObject = obj
                              expOb.matrix = obD_mat
                              expOb.name = obName
                              #expOb.meshName = meshName
                              expOb.meshName = obName
                              expOb.isProxy = True
                              mesh_objects.append(expOb)
                              del(expOb)
                        if psys.settings.render_type=='GROUP' and psys.settings.dupli_group:
                            mainExpObject = exportObject()
                            mainExpObject.name = "%s:%s" % (psys.settings.dupli_group.name, ob.name)
                            mainExpObject.meshName = mainExpObject.name
                            mainExpObject.matrix = ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                                             (0.0, 1.0, 0.0, 0.0),
                                             (0.0, 0.0, 1.0, 0.0),
                                             (0.0, 0.0, 0.0, 1.0))
#                                 dupobs = [(dob.object, dob.matrix, dob.object.matrix_basis) for dob in psys.settings.dupli_group.objects]
                            dupobs = psys.settings.dupli_group.objects
#                                 for obG, dupob_mat, dupob_mat_orig in dupobs:
                            for obG in dupobs:
                                obGType = obG.type
                                #print("obG: ", obG.name, obGType)
                                if obGType in ('MESH', 'CURVE', 'FONT'):
                                   name = "%s:%s:%s" %(ob.name,psys.settings.dupli_group.name,obG.name)
                                   meshName = obG.data.name
                                   obName = name
                                   emptyMatrix = ob.matrix_world
                                   obGMatrix = obG.matrix_world
                                   multMatrix = emptyMatrix * obGMatrix
                                   mat = emptyMatrix.inverted() * obG.matrix_local
#                                    mat = obG.matrix_local
                                   expOb = exportObject()
                                   expOb.blenderObject = obG
                                   expOb.matrix = mat
                                   expOb.name = obName
                                   expOb.meshName = meshName
                                   #expOb.meshName = obName
                                   #expOb.name = "obName"
                                   #expOb.meshName = "meshName"
                                   expOb.isProxy = True
        #                            #print("expOb: ", expOb, expOb.blenderObject, expOb.name, expOb.meshName)
#                                   thea_globals.log.debug("*** mainExpObject: %s" % mainExpObject.name)
                                   mainExpObject.subobjects.append(expOb)
#                               CHANGED > Added time notation
                                t1 = datetime.datetime.now()
                                exporter.writeModelBinaryNew(scn, mainExpObject, frame, anim)
                                t2 = datetime.datetime.now()
                                totalTime = t2-t1
                                minutes = totalTime.seconds/60
                                seconds = totalTime.seconds%60
                                microseconds = totalTime.microseconds%1000000
                                result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
                                thea_globals.log.debug("exporting Particle: %s > %s sec" % (ob.name, result))
#                                 package = Package()
#                                 package.name = "%s:%s" % (psys.settings.dupli_group.name, ob.name)#psys.settings.dupli_group.name
#                                 package.alias = "%s:%s" % (psys.settings.dupli_group.name, ob.name)#psys.settings.dupli_group.name, psys.settings.name)
#                                 obD_mat = ob.matrix_world
#                                 frame = [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
#                                          obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
#                                          obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
#                                 package.addFrame(frame)
#                                 exporter.addPackage(package)
                                del(mainExpObject)

                for mod in ob.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
                        psys = mod.particle_system
                        thea_globals.log.debug("packages: psys.settings.render_type: %s" % psys.settings.render_type)
                        #print("psys.name: %s " % psys.name)
                        if psys.settings.type == 'HAIR' and psys.settings.render_type not in ('OBJECT', 'GROUP'):
                            render = False
                            modifierName = None
                            for mod in ob.modifiers:
                                try:
                                    if mod.particle_system.name == psys.name and  mod.show_render == True:
                                          render = True
                                          modifierName = mod.name
                                except:
                                    pass
                            if render:
                                name = ob.name+"_"+psys.name
                                meshName = ob.data.name
                                obName = name
                                obD_mat = ob.matrix_world
                                if ob.parent:
                                    ob_parent_mat = ob.parent.matrix_world
                                    mesh = (ob,obD_mat,ob_parent_mat,obName,meshName,psys, modifierName)
                                else:
                                    mesh = (ob,obD_mat,None,obName,meshName,psys, modifierName)
                                particle_objects.append(mesh)

#                         if psys.settings.type == 'EMITTER':
#                             if psys.settings.dupli_object:
                        if psys.settings.render_type=='OBJECT' and psys.settings.dupli_object:
                          name = psys.settings.dupli_object.name
                          package = Package()
                          package.name = name
                          package.alias = name
                          i = 0
                          for p in psys.particles:
                            if (psys.settings.type == 'EMITTER' and p.alive_state=="ALIVE"):
                                pm = p.rotation.to_matrix()*p.size
                                frame =          [pm[0][0],pm[0][1],pm[0][2],p.location[0],
                                                  pm[1][0],pm[1][1],pm[1][2],p.location[1],
                                                  pm[2][0],pm[2][1],pm[2][2],p.location[2]
                                                  ]
                                package.addFrame(frame)
                            if psys.settings.type == 'HAIR':
                                p_scale_mat = mathutils.Matrix.Scale(p.size*psys.settings.hair_length, 4)
                                p_loc_mat = mathutils.Matrix.Translation(p.hair_keys[0].co_object(ob, mod, p))
                                ob_loc, ob_rot, ob_sc_mat = ob.matrix_world.decompose()
                                ob_loc_mat = mathutils.Matrix.Translation(ob_loc)
                                ob_rot_mat = ob_rot.to_matrix().to_4x4()
                                p_loc_rot_mat = (ob_rot.inverted() * p.rotation).to_matrix().to_4x4()
                                obD_mat = ob_loc_mat *ob_rot_mat * p_loc_mat * p_loc_rot_mat * p_scale_mat
                                frame =   [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                                       obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                                       obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                                package.addFrame(frame)
                          exporter.addPackage(package)
#                             elif psys.settings.dupli_group:
                        elif psys.settings.render_type=='GROUP' and psys.settings.dupli_group:
                          name = psys.settings.dupli_group.name
                          package = Package()
                          package.name = "%s:%s" % (psys.settings.dupli_group.name, ob.name)#name
                          package.alias = "%s:%s" % (psys.settings.dupli_group.name, ob.name)#"%s:%s" % (psys.settings.dupli_group.name, psys.settings.name)
                          #print("2object: %s, package.name: %s, package.alias: %s" %(ob.name, package.name, package.alias))
                          for p in psys.particles:
                            if (psys.settings.type == 'EMITTER' and p.alive_state=="ALIVE"):
#                                 pm = p.rotation.to_matrix()*p.size
                                pm = (p.rotation.to_matrix()*p.size)*ob.rotation_euler.to_matrix()
                                frame =          [pm[0][0],pm[0][1],pm[0][2],p.location[0],
                                                  pm[1][0],pm[1][1],pm[1][2],p.location[1],
                                                  pm[2][0],pm[2][1],pm[2][2],p.location[2]
                                                  ]
                                package.addFrame(frame)
                            if psys.settings.type == 'HAIR':
                                p_scale_mat = mathutils.Matrix.Scale(p.size*psys.settings.hair_length, 4)
                                p_loc_mat = mathutils.Matrix.Translation(p.hair_keys[0].co_object(ob, mod, p))
                                ob_loc, ob_rot, ob_sc_mat = ob.matrix_world.decompose()
                                ob_loc_mat = mathutils.Matrix.Translation(ob_loc)
                                ob_rot_mat = ob_rot.to_matrix().to_4x4()
                                p_loc_rot_mat = (ob_rot.inverted() * p.rotation).to_matrix().to_4x4()
                                obD_mat = ob_loc_mat *ob_rot_mat * p_loc_mat * p_loc_rot_mat * p_scale_mat
                                frame =   [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                                       obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                                       obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                                package.addFrame(frame)
                          package.addFrame(frame)
                          exporter.addPackage(package)



    for ob in mesh_objects:
#        CHANGED > Added time notation
        t1 = datetime.datetime.now()
        exporter.writeModelBinaryNew(scn, ob, frame, anim)
        t2 = datetime.datetime.now()
        totalTime = t2-t1
        minutes = totalTime.seconds/60
        seconds = totalTime.seconds%60
        microseconds = totalTime.microseconds%1000000
        result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
        thea_globals.log.debug("exporting Particle: %s > %s sec" % (ob.name, result))

    for mesh in particle_objects:
        exportModel = Model()
        ob = mesh[0]
        exportModel.name = mesh[3]
        thea_globals.log.debug("exporting Particle: %s " % (exportModel.name))

        partSystem = mesh[5]
        partSettings = partSystem.settings
        partMatIdx = partSettings.material
        partMat = ob.material_slots[partMatIdx-1].material
        modifierName = mesh[6]
        fastExport=False
        #if partMat.get('thea_FastHairExport') == True or partMat.get('thea_FastHairExport') == None:
        if getattr(partMat, 'thea_FastHairExport'):
            fastExport = True
        thea_globals.log.debug("fastExport: %s partMat: %s" % (fastExport, partMat.name))
        if fastExport:
            t1 = datetime.datetime.now()
            selected = bpy.context.selected_objects
            active = bpy.context.active_object
            # select active object
            ob.select = True
            bpy.context.scene.objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_convert(modifier=modifierName)
            bpy.ops.object.mode_set(mode='OBJECT')
            for v in bpy.context.active_object.data.vertices:
                    v.select = True
            tempObject = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')

            if partMat.get('thea_StrandRoot'):
                rootSize = partMat.get('thea_StrandRoot')
            else:
                rootSize = 0.001
            bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={"value":(0, rootSize, 0), "constraint_orientation":'NORMAL'})
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()
            bpy.context.active_object.data.materials.append(partMat)
            t2 = datetime.datetime.now()
            thea_globals.log.debug("exporting Particle t2-t1: %s " % (t2-t1))
            name = ob.name+"_"+partSystem.name
            meshName = ob.data.name+"_"+partSystem.name
            obName = name
            obD_mat = ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                     (0.0, 1.0, 0.0, 0.0),
                     (0.0, 0.0, 1.0, 0.0),
                     (0.0, 0.0, 0.0, 1.0))
            isProxy = False
            expOb = exportObject()
            expOb.blenderObject = bpy.context.active_object
            expOb.matrix = obD_mat
            expOb.name = obName
            expOb.meshName = meshName
            expOb.isProxy = isProxy
            partMesh = (bpy.context.active_object,obD_mat,None,obName,meshName, isProxy)
            #exporter.writeModelBinary(scn, partMesh, frame, anim)
            exporter.writeModelBinaryNew(scn, expOb, frame, anim)
            t3 = datetime.datetime.now()
            thea_globals.log.debug("exporting Particle t3-t2: %s " % (t3-t2))
            bpy.context.scene.objects.active = tempObject

            #delete object when it's done
            bpy.ops.object.delete()
            #select back objects
#             for selOb in bpy.context.scene.objects:
#                 selOb.select = False
            for selOb in selected:
                selOb.select = True
            bpy.context.scene.objects.active = active
        else:
            # something is wrong when exporting particles, but entering edit mode and leaving it fixes the problem
            bpy.context.scene.objects.active = ob
            # Temp turned this off, caused errors in production renders with certain setups
#            bpy.ops.object.mode_set(mode='EDIT')
#            bpy.ops.object.mode_set(mode='OBJECT')
            exporter.writeHairParticlesBinaryNew(scn, mesh, exportModel, frame, anim)

def exportMeshObjects(scene,frame, anim=False, exporter=None, obList=None):
    '''Export mesh objects and add them to exporter objects lists

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param obList: list of objects to export
        :type obList: list

    '''

    # list of objects.
    mesh_objects = []

    for ob in obList:
        exportOb = False
        renderObject = True
        if ob.is_visible(scn):
            exportOb = True

        if exportOb:

              obType = ob.type

              for psys in ob.particle_systems:
                #if psys.settings.type == 'EMITTER':
                renderObject = psys.settings.use_render_emitter

              #don't export if object is dupliverted or duplifaced
              try:
                  if ob.parent.dupli_type != "NONE":
                      renderObject = False
              except:
                  pass

              if obType in ('MESH', 'CURVE', 'FONT') and renderObject: #don't export objects having particle systems and render emitter disabled
                  if obType == 'CURVE':
                      obName = "C"+ob.name
                      meshName = "C"+ob.data.name
                  else:
                      obName = ob.name
                      meshName = ob.data.name
                  obD_mat = ob.matrix_world

                  isProxy = False
                  hasArray = False
                  # check if mesh is already added to export mesh, if yes then add package
                  expOb = alreadyExported(ob.data.name, mesh_objects)
                  # but in case it uses Array modifier don't do proxy
                  #print("meshName: ", meshName, ob.data.name)
                  for mod in ob.modifiers:
                      #print("     obName: ", obName)
                      #print("     meshName: ", meshName)
                      if mod.type == 'ARRAY':
                          hasArray = True
                          meshName = obName
                  #print("ob: %s, expOb: %s, meshName: %s" % (obName, expOb, meshName))
                  if expOb and (not hasArray):
                      package = Package()
                      if obType == 'CURVE':
                          package.name = "C"+ob.name+" - "
                          package.alias = "C"+ob.data.name
                      elif obType == 'FONT':
                          package.name = "T"+ob.name+" - "
                          package.alias = "T"+ob.data.name
                      else:
                          package.name = ob.name+" - "
                          package.alias = ob.data.name
                      frame = [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                               obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                               obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                      package.addFrame(frame)
                      exporter.addPackage(package)
                      #print ("package: ",ob.name, ob.data.name)
                  else:
                      if (ob.data.users > 1) and (not hasArray): # if there are many users for the same mesh (clones)
                          isProxy = True   #then add package for first object too
                          package = Package()
                          if obType == 'CURVE':
                              obName = "C"+meshName
                              package.name = "C"+ob.name+" - "
                              package.alias = "C"+ob.data.name
                          elif obType == 'FONT':
                              obName = "T"+meshName
                              package.name = "T"+ob.name+" - "
                              package.alias = "T"+ob.data.name
                          else:
                              obName = meshName
                              package.name = ob.name+" - "
                              package.alias = ob.data.name
                          frame = [obD_mat[0][0], obD_mat[0][1], obD_mat[0][2], obD_mat[0][3],
                                   obD_mat[1][0], obD_mat[1][1], obD_mat[1][2], obD_mat[1][3],
                                   obD_mat[2][0], obD_mat[2][1], obD_mat[2][2], obD_mat[2][3]]
                          package.addFrame(frame)
                          exporter.addPackage(package)
                          #print ("package: ",ob.name, ob.data.name)
                          obD_mat = ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                                     (0.0, 1.0, 0.0, 0.0),
                                     (0.0, 0.0, 1.0, 0.0),
                                     (0.0, 0.0, 0.0, 1.0))


                      expOb = exportObject()
                      expOb.blenderObject = ob
                      expOb.matrix = obD_mat
                      #expOb.name = ob.data.name
#                      CHANGED> Deleted "C" and "T" for curve and FONT>Object Settings are not applied cause of no name match due to extra letters
                      if obType == 'CURVE':
                          expOb.name = ob.name
                          expOb.meshName = ob.data.name
                      elif obType == 'FONT':
                          expOb.name = ob.name
                          expOb.meshName = ob.data.name
                      else:
                          expOb.name = ob.name
                          expOb.meshName = ob.data.name
                      expOb.isProxy = isProxy
                      mesh_objects.append(expOb)
                      #print ("object: ",expOb.name, expOb.meshName)
                      del(expOb)



    for ob in mesh_objects:
#       CHANGED > Added better time notation
        t1 = datetime.datetime.now()
        exporter.writeModelBinaryNew(scn, ob, frame, anim)
        t2 = datetime.datetime.now()
        totalTime = t2-t1
        minutes = totalTime.seconds/60
        seconds = totalTime.seconds%60
        microseconds = totalTime.microseconds%1000000
        result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
#        thea_globals.log.debug("exporting object: %s time: %s" % (ob.name, time.strftime("%H:%M:%S",time.gmtime(t))))
        thea_globals.log.debug("Exporting object MeshObject: %s > %s sec" % (ob.name, result))
#        thea_globals.log.debug("exporting object: %s time: %s" % (ob.name, t2-t1))


def regionRenderThea(scene):

    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)

    xmlFilename = currentBlendFile.replace('.blend', '.xml')
    os.chdir(os.path.dirname(theaPath))
#    exportFrame(scene,frame,exporter=exporter)

    fileFormat = ".png"
    if scn.render.image_settings.file_format == "JPEG":
        fileFormat = ".jpg"
    if scn.render.image_settings.file_format == "PNG":
        fileFormat = ".png"
    if scn.render.image_settings.file_format == "BMP":
        fileFormat = ".bmp"
    if scn.render.image_settings.file_format == "HDR":
        fileFormat = ".hdr"
    if scn.render.image_settings.file_format == "OPEN_EXR":
        fileFormat = ".exr"
    if scn.render.image_settings.file_format == "TIFF":
        fileFormat = ".tif"

    args = []
#    global scriptFile
    scriptFilename = os.path.join(exportPath, os.path.basename(currentBlendFile.replace('.blend', '_regionRender.ipt.thea')))
    scriptFile = open(scriptFilename, "w")

    if getattr(bpy.context.scene, "thea_showMerge"):
        if scn.thea_SceneMerReverseOrder:
            #load another scene and then merge exported one
            if os.path.exists(scn.thea_mergeFilePath):
                mergeString = (" %s %s %s %s %s %s" % (scn.thea_SceneMerModels, scn.thea_SceneMerLights, scn.thea_SceneMerCameras, scn.thea_SceneMerRender, scn.thea_SceneMerEnv, scn.thea_SceneMerMaterials))
                scriptFile.write('message \"Load ' +  scn.thea_mergeFilePath + '\"\n')
                scriptFile.write('message \"Merge ' + os.path.join(exportPath, os.path.basename(xmlFilename) + mergeString + '\"\n'))
            else:
                scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))
        else:
            scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))

            #merge another scene after load
            if os.path.exists(scn.thea_mergeFilePath):
                mergeString = (" %s %s %s %s %s %s" % (scn.thea_SceneMerModels, scn.thea_SceneMerLights, scn.thea_SceneMerCameras, scn.thea_SceneMerRender, scn.thea_SceneMerEnv, scn.thea_SceneMerMaterials))
                scriptFile.write('message \"Merge ' +  scn.thea_mergeFilePath + mergeString + '\"\n')
    else:
        scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))

    args.append(scriptFilename)
#    if scn.thea_regionRender !=True:
#        scriptFile.write('message \"Render\"\n')
#    else:
    if scn.thea_regionRender == True:
        ## REGIONS  2x2 || 3x3 || 4x4 || 5x5 || 6x6 || 7x7 || 8x8
        # NIGEC SHORT CODE VERSION altered
        iREnd = ""
        iCEnd = ""
        iSelindex = ""
        tilesize = ""
        C = ""
        R = ""
        iSelindex = scn.thea_regionSettings
        iREnd = (int(iSelindex) + 2)
        iCEnd = (int(iSelindex) + 2)
        tilesize = str(iREnd) + "," + str(iCEnd)
        regionData=""
#            R = 1
#            C = 1

        for C in range(1, int(iCEnd+1)):
            for R in range(1, int(iREnd+1)):
                regionData += 'set \"./Scenes/Active/Cameras/'+scn.camera.name+'/Region\" = \"Part ('+str(C)+","+str(R)+'):('+tilesize+')"\n'\
                              'message "Render"\n'\
                              'message \"SaveImage %s\"\n' % (os.path.join(exportPath, os.path.basename(xmlFilename[:-4].strip())+"_C"+str(C)+"_R" +str(R)+fileFormat))
                R += 1
            C += 1

        thea_globals.log.debug("*** REGION DATA: %s - R:%s - C:%s" % (iSelindex, iREnd, iCEnd))
        scriptFile.write('set "./Scenes/Active/Cameras/'+scn.camera.name+'/Render Region"' +' = "1"'+"\n"+regionData+"\n")

    scriptFile.close()
    return args

def exportFrame(scene,frame, anim=False, exporter=None, area=None, obList=None, exportMode="Full", xmlFile=None):
    '''Export whole scene for the given frame

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: frame number to be exported
        :type frame: int
        :param anim: export animation data (not used by now, export animation is checked in different way)
        :type anim: bool
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
        :param area: current 3d view area
        :type area: bpy_types.Area
        :param obList: list of objects to export
        :type obList: list
        :param exportMode: export mode "Full" if whole scene should be exported, "Material" if only active material should be exported
        :type exportMode: str
        :param xmlFile: filename of the xml file to be saved
        :type xmlFile: str

    '''

    global globalTimeToWait
    global guiSets, theaPath, selectedObjects
    global scn, exportPath, firstFrame, firstRun
#   CHANGED > added new globals for checking channels if on or off and added save img.thea file option
    global imgThea, checkChannels

    scn = scene

    #print("area: ",area)

    if not obList:
        if scn.thea_Selected == 1:
            try:
                if selectedObjects:
                    obList = selectedObjects
                else:
                    obList = bpy.context.selected_objects
            except:
                obList = bpy.context.selected_objects
        else:
            obList = scn.objects


    #print("obList: ",obList)
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn, verbose=True)

    firstRun = False

    tempDir = bpy.path.abspath(os.path.join(exportPath, "~thexport"))

    try:
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)
    except:
        return False

    #print ("Exporting frame in mode: ", exportMode)


    frameS= "0000" + str(frame)
    time1 = time.time()

    #print("Preparing temporary objects for export")
    tempObjects = []
    for object in obList:
        for mod in object.modifiers:
            if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
                psys = mod.particle_system
                if psys.settings.render_type == 'GROUP' and psys.settings.thea_ApplyModifier:
                    bpy.ops.object.select_all(action = 'DESELECT')
                    object.select = True
                    bpy.ops.object.duplicate()
                    bpy.ops.object.duplicates_make_real()
                    for ob in bpy.context.selected_objects:
                        tempObjects.append(ob)

    if exportMode=="Full":
        thea_globals.log.info("Exporting cameras")
        exportCameras(scene,frame, anim=anim, exporter=exporter, area=area, obList=obList)

        thea_globals.log.info("Exporting lights")
        exportLights(scene,frame, anim=anim, exporter=exporter, obList=obList)

        thea_globals.log.info("Exporting libraries")
        exportLibraries(scene,frame, anim=anim, exporter=exporter, obList=obList)

        thea_globals.log.info("Exporting dupli objects")
        exportDupliObjects(scene,frame, anim=anim, exporter=exporter, obList=obList)

        thea_globals.log.info("Exporting particles")
        exportParticles(scene,frame, anim=anim, exporter=exporter, obList=obList)

        thea_globals.log.info("Exporting mesh objects")
        exportMeshObjects(scene,frame, anim=anim, exporter=exporter, obList=obList)

        thea_globals.log.info("Export materials")
        for mat in exporter.materialList:
            exporter.generateMaterialNew(mat)

    if exportMode=="Material" and bpy.context.active_object is not None:
        thea_globals.log.debug("export single material only!")
        mat = bpy.context.active_object.active_material
        matName = mat.name
        madeLink = False
        ##print("#thea_globals.getUseLUT(): ", thea_globals.getUseLUT())
        if thea_globals.getUseLUT():#getattr(scn, 'thea_useLUT'):
            matTransTable = getMatTransTable()
            lut = getLUTarray()
            for trMat in matTransTable:
#                 try:
                if thea_globals.getNameBasedLUT():
                    if trMat[0] == matName and (exporter.findMaterialLink(matName) < 0):
                        matLink = Link()
                        matLink.setName(trMat[0])
                        matLink.setFilename(trMat[1])
                        exporter.addMaterialLink(matLink)
                        madeLink = True
                else:
                    if int(getattr(mat, 'thea_LUT', 0)) > 0:
                        if trMat[0] == lut[int(getattr(mat, 'thea_LUT', 0))] and (exporter.findMaterialLink(matName) < 0):
                            ##print("trMat[0]: ", trMat[0])
                            matLink = Link()
                            #matLink.setName(trMat[0])
                            matLink.setName(matName)
                            matLink.setFilename(trMat[1])
                            exporter.addMaterialLink(matLink)
                            madeLink = True
#                 except:
#                     emptyMat = True
#         if getattr(scene, 'thea_useLUT'):
#             matTransTable = getMatTransTable()
#             for trMat in matTransTable:
#                 try:
#                     if trMat[0] == matName and (exporter.findMaterialLink(matName) < 0):
#                         matLink = Link()
#                         matLink.setName(trMat[0])
#                         matLink.setFilename(trMat[1])
#                         exporter.addMaterialLink(matLink)
#                         madeLink = True
#                 except:
#                     emptyMat = True
        try:

            if os.path.exists(os.path.abspath(bpy.path.abspath(mat['thea_extMat']))) and (exporter.findMaterialLink(matName) < 0):
                matLink = Link()
                matLink.setName(matName)
                matLink.setFilename(os.path.abspath(bpy.path.abspath(mat['thea_extMat'])))
                exporter.addMaterialLink(matLink)
                madeLink = True
        except: pass

        if mat and (exporter.findMaterial(matName) < 0):
            ma = ThMaterial()
            ma.setName(matName)
            if madeLink:
                ma.link = True
            exporter.addMaterial(ma)
            exporter.materialList[exporter.findMaterial(matName)].blenderMat = mat

        for mat in exporter.materialList:
            #print("************ mat: ", mat.name)
            if not madeLink:
                exporter.generateMaterialNew(mat)


    exporter.getRenderOptions().animationOptions.currentFrame = scn.frame_current
    exporter.getRenderOptions().animationOptions.endFrame = scn.frame_end
    exporter.getRenderOptions().animationOptions.frameRate = int(scn.render.fps / scn.render.fps_base)

    if area:
        exporter.getRenderOptions().activeCamera = scn.camera.name #'## Current View ##'
    else:
        if scn.camera:
            exporter.getRenderOptions().activeCamera = scn.camera.name

#     if(area):
#         exporter.getRenderOptions().engine = scn.thea_IRRenderEngineMenu
#     else:
#         exporter.getRenderOptions().engine = scn.thea_RenderEngineMenu
    exporter.getRenderOptions().engine = scn.thea_RenderEngineMenu
    exporter.getRenderOptions().interactiveEngine = scn.thea_IRRenderEngineMenu
    exporter.getRenderOptions().maxRenderTime = scn.thea_RenderTime
    exporter.getRenderOptions().maxPasses = scn.thea_RenderMaxPasses
    exporter.getRenderOptions().maxSamples = scn.thea_RenderMaxSamples
    exporter.getRenderOptions().motionBlur = scn.thea_RenderMBlur
    exporter.getRenderOptions().volumetricScattering = scn.thea_RenderVolS
    exporter.getRenderOptions().lightBlending = scn.thea_RenderLightBl
    exporter.getRenderOptions().ImgTheaFile = scn.thea_ImgTheaFile
#    CHANGED > Added clay render options
    exporter.getRenderOptions().clayrender = scn.thea_clayRender
    exporter.getRenderOptions().clayrenderreflectance = scn.thea_clayRenderReflectance
#   CHANGED > Added Markernaming output + custom output
    exporter.getRenderOptions().markerName = scn.thea_markerName
    exporter.getRenderOptions().customOutput = scn.thea_customOutputName
    exporter.getRenderOptions().customName = scn.thea_customName

    exporter.getRenderOptions().checkChannels = True #scn.thea_showChannels

    if scene.thea_DistTh == '0':
        exporter.getRenderOptions().threads = "Max"
    if scene.thea_DistTh == '1':
        exporter.getRenderOptions().threads = "1"
    if scene.thea_DistTh == '2':
        exporter.getRenderOptions().threads = "2"
    if scene.thea_DistTh == '3':
        exporter.getRenderOptions().threads = "4"
    if scene.thea_DistTh == '4':
        exporter.getRenderOptions().threads = "8"

    exporter.getRenderOptions().bucketRendering = getattr(scn, "thea_BucketRendering")
    exporter.getRenderOptions().extendedTracing = getattr(scn, "thea_ExtendedTracing")
    exporter.getRenderOptions().transparencyDepth = getattr(scn, "thea_TransparencyDepth")
    exporter.getRenderOptions().internalReflectionDepth = getattr(scn, "thea_InternalReflectionDepth")
    exporter.getRenderOptions().SSSDepth = getattr(scn, "thea_SSSDepth")
    exporter.getRenderOptions().ClampLevelEnable = getattr(scn, "thea_ClampLevelEnable")
    exporter.getRenderOptions().ClampLevel = getattr(scn, "thea_ClampLevel")
    exporter.getRenderOptions().priority = scn.thea_DistPri
    if scn.thea_DistNet == '0':
        exporter.getRenderOptions().network = "None"
    if scn.thea_DistNet == '1':
        exporter.getRenderOptions().network = "Client"
    if scn.thea_DistNet == '2':
        exporter.getRenderOptions().network = "Server"
    if scn.thea_DistNet == '3':
        exporter.getRenderOptions().network = "Pure Server"
    exporter.getRenderOptions().serverport = scn.thea_DistPort
    exporter.getRenderOptions().serveraddress = scn.thea_DistAddr
    if scn.thea_AASamp == '0':
        exporter.getRenderOptions().supersampling = "DefaultSS"
    if scn.thea_AASamp == '1':
        exporter.getRenderOptions().supersampling = "NoneSS"
    if scn.thea_AASamp == '2':
        exporter.getRenderOptions().supersampling = "NormalSS"
    if scn.thea_AASamp == '3':
        exporter.getRenderOptions().supersampling = "HighSS"
#   CHANGED> Added adaptive bias +displacement
    exporter.getRenderOptions().adaptiveBias = scn.thea_adaptiveBias / 100
    exporter.getRenderOptions().displacemScene = scn.thea_displacemScene
    exporter.getRenderOptions().rayTracingDepth = scn.thea_RTTracingDepth
    exporter.getRenderOptions().rayDiffuseDepth = scn.thea_RTDiffuseDepth
    exporter.getRenderOptions().rayGlossyDepth = scn.thea_RTGlossyDepth
    exporter.getRenderOptions().rayTraceDispersion = scn.thea_RTTraceDispersion
    exporter.getRenderOptions().rayTraceReflections = scn.thea_RTTraceReflections
    exporter.getRenderOptions().rayTraceRefractions = scn.thea_RTTraceRefractions
    exporter.getRenderOptions().rayTraceTransparencies = scn.thea_RTTraceTransparencies
    exporter.getRenderOptions().maxContrast = scn.thea_AACont
    exporter.getRenderOptions().minAASubdivs = scn.thea_AAMinSub
    exporter.getRenderOptions().maxAASubdivs = scn.thea_AAMaxSub
    exporter.getRenderOptions().directLighting = scn.thea_DLEnable
    exporter.getRenderOptions().perceptualBased = scn.thea_DLPerceptualBased
    exporter.getRenderOptions().maxDirectError = scn.thea_DLMaxError / 100
    exporter.getRenderOptions().FMEnable = scn.thea_FMEnable
    exporter.getRenderOptions().FMFieldDensity = scn.thea_FMFieldDensity
    exporter.getRenderOptions().FMCellSize = scn.thea_FMCellSize
    exporter.getRenderOptions().photonMapping = scn.thea_GIEnable
    exporter.getRenderOptions().caustics = scn.thea_GICaustics
    exporter.getRenderOptions().leakCompensation = scn.thea_GILeakComp
    exporter.getRenderOptions().causticSharpening = scn.thea_GICausticSharp
    exporter.getRenderOptions().subsurfaceScattering = scn.thea_GIEnableSS
    exporter.getRenderOptions().globalPhotonsCaptured = scn.thea_GITotPh
    exporter.getRenderOptions().causticPhotonsCaptured = scn.thea_GICausticCaptured
    exporter.getRenderOptions().globalEstimationPhotons = scn.thea_GIGlobPh
    exporter.getRenderOptions().causticEstimationPhotons = scn.thea_GICausPh
    exporter.getRenderOptions().globalEstimationRadius = scn.thea_GIGlobalRadius
    exporter.getRenderOptions().causticEstimationRadius = scn.thea_GICausticRadius
    exporter.getRenderOptions().finalGathering = scn.thea_FGEnable
    exporter.getRenderOptions().secondaryGather = scn.thea_FGEnableSecondary
    exporter.getRenderOptions().distanceThreshold = scn.thea_FGDistanceThreshold
    exporter.getRenderOptions().gatherAdaptiveSteps = scn.thea_FGAdaptiveSteps
    exporter.getRenderOptions().gatherTracingDepth = scn.thea_GITracingDepth
    exporter.getRenderOptions().gatherDiffuseDepth = scn.thea_FGDiffuseDepth
    exporter.getRenderOptions().gatherGlossyDepth = scn.thea_FGGlossyDepth
    exporter.getRenderOptions().gatherGlossyEvaluation = scn.thea_FGGlossyEvaluation
    exporter.getRenderOptions().gatherCausticEvaluation = scn.thea_FGCausticEvaluation
    exporter.getRenderOptions().gatherTraceTransparencies = scn.thea_GITraceTransparencies
    exporter.getRenderOptions().gatherTraceReflections = scn.thea_GITraceReflections
    exporter.getRenderOptions().gatherTraceRefractions = scn.thea_GITraceRefractions
    exporter.getRenderOptions().gatherRays = scn.thea_GIRays
    exporter.getRenderOptions().maxGatherError = scn.thea_GIError/100
    exporter.getRenderOptions().blurredReflections = scn.thea_BREnable
    exporter.getRenderOptions().minBlurredSubdivs = scn.thea_BRMinSub
    exporter.getRenderOptions().maxBlurredSubdivs = scn.thea_BRMaxSub
    exporter.getRenderOptions().ICEnable = scn.thea_ICEnable
    exporter.getRenderOptions().ICForceInterpolation = scn.thea_ICForceInterpolation
    exporter.getRenderOptions().ICAccuracy = scn.thea_ICAccuracy * 0.01
    exporter.getRenderOptions().ICPrepassBoost = scn.thea_ICPrepassBoost
    exporter.getRenderOptions().ICMinDistance = scn.thea_ICMinDistance * 0.01
    exporter.getRenderOptions().ICMaxDistance = scn.thea_ICMaxDistance * 0.01
    if scn.thea_ICPrepass == '0':
        exporter.getRenderOptions().ICPrepass = "None"
    if scn.thea_ICPrepass == '1':
        exporter.getRenderOptions().ICPrepass = "1/1"
    if scn.thea_ICPrepass == '2':
        exporter.getRenderOptions().ICPrepass = "1/2"
    if scn.thea_ICPrepass == '3':
        exporter.getRenderOptions().ICPrepass = "1/4"
    if scn.thea_ICPrepass == '4':
        exporter.getRenderOptions().ICPrepass = "1/8"


    exporter.getDisplayOptions().iso = scn.thea_DispISO
    exporter.getDisplayOptions().shutter = scn.thea_DispShutter
    exporter.getDisplayOptions().fNumber = scn.thea_DispFNumber
    exporter.getDisplayOptions().gamma = scn.thea_DispGamma
    exporter.getDisplayOptions().brightness = scn.thea_DispBrightness
    exporter.getDisplayOptions().sharpness = scn.thea_DispSharpness
    exporter.getDisplayOptions().sharpnessWeight = scn.thea_DispSharpnessWeight / 100
    exporter.getDisplayOptions().burn = scn.thea_DispBurn
    exporter.getDisplayOptions().burnWeight = scn.thea_DispBurnWeight / 100
    exporter.getDisplayOptions().vignetting = scn.thea_DispVignetting / 100
    exporter.getDisplayOptions().vignettingWeight = scn.thea_DispVignettingWeight / 100
    exporter.getDisplayOptions().chroma = scn.thea_DispChroma
    exporter.getDisplayOptions().chromaWeight = scn.thea_DispChromaWeight / 100
    exporter.getDisplayOptions().contrast = scn.thea_DispContrast
    exporter.getDisplayOptions().contrastWeight = scn.thea_DispContrastWeight / 100
    exporter.getDisplayOptions().balance = scn.thea_DispTemperature
    exporter.getDisplayOptions().temperature = scn.thea_DispTemperatureWeight

    exporter.getDisplayOptions().bloom = scn.thea_DispBloom
    exporter.getDisplayOptions().glare = scn.thea_DispBloomItems
    exporter.getDisplayOptions().bloomItems = scn.thea_DispBloomItems
    exporter.getDisplayOptions().bloomWeight = scn.thea_DispBloomWeight / 100
    exporter.getDisplayOptions().glareRadius = scn.thea_DispGlareRadius / 100

    if scn.thea_ZdepthClip == True :
        scn.thea_DispMinZ = camData.clip_start
        scn.thea_DispMaxZ = camData.clip_end
    if scn.thea_ZdepthDOF == True :
        scn.thea_DispMinZ = zDist
        thea_globals.log.debug("*** ZdepthDOF Dist: %s" % zDist)
        scn.thea_DispMaxZ = scn.thea_ZdepthDOFmargin
    exporter.getDisplayOptions().minZ = scn.thea_DispMinZ
    exporter.getDisplayOptions().maxZ = scn.thea_DispMaxZ
    exporter.getDisplayOptions().analysisMenu = scn.thea_analysisMenu
    if scn.thea_analysisMenu == "Photometric" :
        exporter.getDisplayOptions().minIlLum = scn.thea_minIlLum
        exporter.getDisplayOptions().maxIlLum = scn.thea_maxIlLum

    imgThea = exporter.getRenderOptions().ImgTheaFile
    checkChannels = exporter.getRenderOptions().checkChannels

    #print ("Engine: ", exporter.getRenderOptions().engine)

    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().normalChannel = getattr(scn,"thea_channelNormal")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().positionChannel = getattr(scn,"thea_channelPosition")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().uvChannel = getattr(scn,"thea_channelUV")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().depthChannel = getattr(scn,"thea_channelDepth")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().alphaChannel = getattr(scn,"thea_channelAlpha")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().objectIdChannel = getattr(scn,"thea_channelObject_Id")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().materialIdChannel = getattr(scn,"thea_channelMaterial_Id")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().maskChannel = getattr(scn,"thea_channelMask")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().shadowChannel = getattr(scn,"thea_channelShadow")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().rawDiffuseColorChannel = getattr(scn,"thea_channelRaw_Diffuse_Color")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().rawDiffuseLightingChannel = getattr(scn,"thea_channelRaw_Diffuse_Lighting")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().rawDiffuseGIChannel = getattr(scn,"thea_channelRaw_Diffuse_GI")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().directChannel = getattr(scn,"thea_channelDirect")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)")):
        exporter.getRenderOptions().AOChannel = getattr(scn,"thea_channelAO")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().giChannel = getattr(scn,"thea_channelGI")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().selfIlluminationChannel = getattr(scn,"thea_channelSelf_Illumination")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (MC)")):
        exporter.getRenderOptions().sssChannel = getattr(scn,"thea_channelSSS")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().reflectionChannel = getattr(scn,"thea_channelReflection")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().refractionChannel = getattr(scn,"thea_channelRefraction")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Presto (AO)")):
        exporter.getRenderOptions().transparentChannel = getattr(scn,"thea_channelTransparent")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)")):
        exporter.getRenderOptions().irradianceChannel = getattr(scn,"thea_channelIrradiance")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Presto (AO)","Presto (MC)")):
        exporter.getRenderOptions().separatePassesPerLightChannel = getattr(scn,"thea_channelSeparate_Passes_Per_Light")
    if (getattr(scene, 'thea_RenderEngineMenu') in ("Adaptive (BSD)","Unbiased (TR1)","Unbiased (TR2)","Presto (AO)","Presto (MC)","Adaptive (AMC)")):
        exporter.getRenderOptions().invertMaskChannel = getattr(scn,"thea_channelInvert_Mask")


#     exporter.getRenderOptions().normalChannel = scn.get('thea_channelNormal')
#     exporter.getRenderOptions().depthChannel = scn.get('thea_channelDepth')
#     exporter.getRenderOptions().objectIdChannel = scn.get('thea_channelObjectId')
#     exporter.getRenderOptions().materialIdChannel = scn.get('thea_channelMaterialId')
#     exporter.getRenderOptions().directChannel = scn.get('thea_channelDirect')
#     exporter.getRenderOptions().AOChannel = scn.get('thea_channelAO')
#     exporter.getRenderOptions().giChannel = scn.get('thea_channelGI')
#     exporter.getRenderOptions().sssChannel = scn.get('thea_channelSSS')
#     exporter.getRenderOptions().reflectionChannel = scn.get('thea_channelReflection')
#     exporter.getRenderOptions().refractionChannel = scn.get('thea_channelRefraction')
#     exporter.getRenderOptions().transparentChannel = scn.get('thea_channelTransparent')

    color_mode = scn.render.image_settings.color_mode
    if scn.render.image_settings.file_format == "JPEG":
        color_mode = "RGB"
    if scn.render.image_settings.file_format == "BMP":
        color_mode = "RGB"

    if color_mode == "RGBA":
        exporter.getRenderOptions().alphaChannel = True
    else:
        exporter.getRenderOptions().alphaChannel = scn.get('thea_channelAlpha')

    exporter.getRenderOptions().deviceMask = scn.thea_IRDevice
#    exporter.getRenderOptions().cpuDevice = scn.thea_cpuDevice
#    exporter.getRenderOptions().cpuThreadsEnable = scn.thea_cpuThreadsEnable
#    exporter.getRenderOptions().cpuThreads = scn.thea_cpuThreads

    exporter.renderOptions.AOEnable = scn.thea_AOEnable
    exporter.renderOptions.AOMultiply = scn.thea_AOMultiply
    exporter.renderOptions.AOClamp = scn.thea_AOClamp
    exporter.renderOptions.AOSamples = scn.thea_AOSamples
    exporter.renderOptions.AODistance = scn.thea_AODistance
    exporter.renderOptions.AOIntensity = scn.thea_AOIntensity
    exporter.renderOptions.AOLowColor = scn.thea_AOLowColor
    exporter.renderOptions.AOHighColor = scn.thea_AOHighColor

    def getTexture(component="thea_IBLFilename"):
            wtextures = scn.world.texture_slots

            if len(wtextures) > 0:
                for mtex in wtextures:
                    found = False
                    texType = False
                    #texture = bpy.data.textures[mtex.name]
#                     if texture:
                    if mtex is not None:
                        if mtex.name=="IBL_"+component:
                            found = True
                            texType = bpy.data.textures[mtex.name].type

                        ##print("mtex.name, found, texType: ", mtex.name, found, texType, "IBL_"+component)
                        if (texType == 'IMAGE') and (found):
                            fileName = os.path.abspath(bpy.path.abspath(getattr(scn, component)))
                            ##print("tex name: ", mtex.name, component, fileName)
                            ##print("fileName: ", fileName)
                            tex = BitmapTexture(fileName)
                            tex.offsetX = mtex.offset[0]
                            tex.offsetY = mtex.offset[1]
                            tex.scaleX = mtex.scale[0]
                            tex.scaleY = mtex.scale[1]
                            tex.invert = bpy.data.textures[mtex.name].thea_TexInvert
                            tex.gamma = bpy.data.textures[mtex.name].thea_TexGamma
                            tex.red = bpy.data.textures[mtex.name].thea_TexRed
                            tex.green = bpy.data.textures[mtex.name].thea_TexGreen
                            tex.blue = bpy.data.textures[mtex.name].thea_TexBlue
                            tex.brightness = bpy.data.textures[mtex.name].thea_TexBrightness
                            tex.contrast = bpy.data.textures[mtex.name].thea_TexContrast
                            tex.saturation = bpy.data.textures[mtex.name].thea_TexSaturation
                            tex.clampMax = bpy.data.textures[mtex.name].thea_TexClampMax
                            tex.clampMin = bpy.data.textures[mtex.name].thea_TexClampMin
                            return tex
                    else:
                        return False
    if scn.world:
        if scn.thea_EnvPSEnable:
            exporter.getEnvironmentOptions().illumination="PhysicalSky"

        IBL = scn.thea_IBLEnable
        thea_globals.log.debug("**IBL  ** %s" % IBL)
        backgroundMapping = scn.thea_BackgroundMappingEnable
        reflectionMapping = scn.thea_ReflectionMappingEnable
        refractionMapping = scn.thea_RefractionMappingEnable
        AO = scn.world.light_settings.use_ambient_occlusion
        if (AO): # if sky AO is on
            #print("AO")
            wtextures = scn.world.texture_slots
            wTextures = False
            if len(wtextures) > 0:
                for wtex in wtextures:
                    try:
                        texType = wtex.texture.type
                    except:
                        texType = None
                    if (texType == 'IMAGE'):
                        wTextures = True
                        iblMap = EnvironmentOptions.IBLMap()
                        iblMap.bitmapTexture = BitmapTexture(bpy.path.abspath(bpy.data.textures[wtex.name].image.filepath))
                        if (wtex.texture_coords == "ANGMAP"):
                            iblMap.wrapping = "AngularProbe"
                        if (wtex.texture_coords == "SPHERE"):
                            iblMap.wrapping = "Spherical"
                        iblMap.enabledParameter = True
                        iblMap.intensity = wtex.horizon_factor
                        iblMap.rotation = bpy.data.textures[wtex.name].thea_TexRotation
                        exporter.getEnvironmentOptions().illuminationMap=iblMap
                        exporter.getEnvironmentOptions().illumination="IBL"
            if not wTextures:
                HorColor = scn.world.horizon_color
                exporter.getEnvironmentOptions().backgroundColor = RgbTexture(HorColor[0], HorColor[1], HorColor[2])
                exporter.getEnvironmentOptions().illumination="Dome"
        elif (IBL): # if IBL is on
            #print("*IBL*")
            #iblMap.bitmapTexture = BitmapTexture(bpy.path.abspath(scn.thea_IBLFilename))
            tex = getTexture(component="thea_IBLFilename")
#            thea_globals.log.debug("tex: %s" % tex)
            if tex:
                iblMap = EnvironmentOptions.IBLMap()
                iblMap.bitmapTexture = tex
                iblMap.iblType = scn.thea_IBLTypeMenu
                iblMap.wrapping = scn.thea_IBLWrappingMenu
                iblMap.enabledParameter = True
                iblMap.intensity = scn.thea_IBLIntensity
                iblMap.rotation = scn.thea_IBLRotation
                exporter.getEnvironmentOptions().illuminationMap=iblMap
                exporter.getEnvironmentOptions().illumination="IBL"
#        if scn.thea_IBLTypeMenu == "IBL Only":
#            omni.enableLamp = False
#         else:
#             exporter.getEnvironmentOptions().illumination="None"

        if (backgroundMapping):
            tex = getTexture(component="thea_BackgroundMappingFilename")
            if tex:
                iblMap = EnvironmentOptions.IBLMap()
                iblMap.bitmapTexture = tex
                iblMap.iblType = scn.thea_BackgroundMappingTypeMenu
                iblMap.wrapping = scn.thea_BackgroundMappingWrappingMenu
                iblMap.enabledParameter = True
                iblMap.intensity = scn.thea_BackgroundMappingIntensity
                iblMap.rotation = scn.thea_BackgroundMappingRotation
                exporter.getEnvironmentOptions().backgroundMap=iblMap

        if (reflectionMapping):
            tex = getTexture(component="thea_ReflectionMappingFilename")
            if tex:
                iblMap = EnvironmentOptions.IBLMap()
                iblMap.bitmapTexture = tex
                iblMap.iblType = scn.thea_ReflectionMappingTypeMenu
                iblMap.wrapping = scn.thea_ReflectionMappingWrappingMenu
                iblMap.enabledParameter = True
                iblMap.intensity = scn.thea_ReflectionMappingIntensity
                iblMap.rotation = scn.thea_ReflectionMappingRotation
                exporter.getEnvironmentOptions().reflectionMap=iblMap

        if (refractionMapping):
            tex = getTexture(component="thea_RefractionMappingFilename")
            if tex:
                iblMap = EnvironmentOptions.IBLMap()
                iblMap.bitmapTexture = tex
                iblMap.iblType = scn.thea_RefractionMappingTypeMenu
                iblMap.wrapping = scn.thea_RefractionMappingWrappingMenu
                iblMap.enabledParameter = True
                iblMap.intensity = scn.thea_RefractionMappingIntensity
                iblMap.rotation = scn.thea_RefractionMappingRotation
                exporter.getEnvironmentOptions().refractionMap=iblMap


    #CHANGED> Added locations menu info environment update for IR
#    exporter.getEnvironmentOptions().skyType=scn.thea_IBLTypeMenu


    exporter.environmentOptions.skyType=scn.thea_SkyTypeMenu
    exporter.environmentOptions.turbidity = scn.thea_EnvPSTurb
    exporter.environmentOptions.waterVapor = scn.thea_EnvPSWatVap
    exporter.environmentOptions.turbidityCoefficient = scn.thea_EnvPSTurbCo
    exporter.environmentOptions.wavelengthExponent = scn.thea_EnvPSWaveExp
#    changed> Added missing Albedo + ozone
    exporter.environmentOptions.ozone = scn.thea_EnvPSOzone
    exporter.environmentOptions.albedo = scn.thea_EnvPSalbedo
    exporter.environmentOptions.locEnable = scn.thea_locationEnable
    locCit = getLocMenu()[int(getattr(bpy.context.scene, "thea_EnvLocationsMenu"))][1]
#    locCap = getLocMenu()[int(getattr(bpy.context.scene, "thea_EnvLocationsMenu"))][2]
#    exporter.environmentOptions.location = locCap+" - "+locCit
    exporter.environmentOptions.location = locCit
    exporter.environmentOptions.latitude = scn.thea_EnvLat
    exporter.environmentOptions.longitude = scn.thea_EnvLong
    exporter.environmentOptions.timezone = ("GT+"+scn.thea_EnvTZ if int(scn.thea_EnvTZ)>0 else "GT"+scn.thea_EnvTZ)
    exporter.environmentOptions.localtime = scn.thea_EnvTime
#    exporter.environmentOptions.polarAngle = scn.thea_polarAngle
#    exporter.environmentOptions.azimuthAngle = scn.thea_azimuthAngle
    exporter.environmentOptions.date = scn.thea_EnvDate

#    CHANGED > Added Global Medium Options
    exporter.environmentOptions.GlobalMediumEnable = scn.thea_GlobalMediumEnable
    exporter.environmentOptions.GlobalMediumIOR = scn.thea_GlobalMediumIOR
    colorMedS = RgbTexture(getattr(scn, "thea_MediumScatterCol")[0],getattr(scn, "thea_MediumScatterCol")[1],getattr(scn, "thea_MediumScatterCol")[2])
    colorMed = RgbTexture(scn.thea_MediumScatterCol[0],scn.thea_MediumScatterCol[1],scn.thea_MediumScatterCol[2])
#    thea_globals.log.debug("GLobal Med Color: %s" % colorMedS)
    exporter.environmentOptions.scatteringColor = colorMedS
    exporter.environmentOptions.scatteringDensity = scn.thea_MediumScatterDensity
    exporter.environmentOptions.scatteringDensityTexture = scn.thea_MediumScatterDensityFilename
    exporter.environmentOptions.absorptionColor = scn.thea_MediumAbsorptionCol
    exporter.environmentOptions.absorptionDensity = scn.thea_MediumAbsorptionDensity
    exporter.environmentOptions.absorptionDensityTexture = scn.thea_MediumAbsorptionDensityFilename
    exporter.environmentOptions.MediumCoefficentEnable = scn.thea_MediumCoefficient
    exporter.environmentOptions.coefficientFilename = getTheaMediumMenuItems()[int(getattr(scn, "thea_MediumMenu"))-1][1]+".med"
    exporter.environmentOptions.phaseFunction = scn.thea_MediumPhaseFunction
    exporter.environmentOptions.asymetry = scn.thea_Asymetry



    fileFormat = ".png"
    if scn.render.image_settings.file_format == "JPEG":
        fileFormat = ".jpg"
    if scn.render.image_settings.file_format == "PNG":
        fileFormat = ".png"
    if scn.render.image_settings.file_format == "BMP":
        fileFormat = ".bmp"
    if scn.render.image_settings.file_format == "HDR":
        fileFormat = ".hdr"
    if scn.render.image_settings.file_format == "OPEN_EXR":
        fileFormat = ".exr"
    if scn.render.image_settings.file_format == "TIFF":
        fileFormat = ".tif"




    if anim:
        xmlFilename = currentBlendFile.replace('.blend', '_'+scn.camera.name+'_f'+frameS[-4:]+'.xml')
        imgFilename = currentBlendFile.replace('.blend', '_'+scn.camera.name+'_f'+frameS[-4:]+fileFormat)
        tempDir = os.path.join(exportPath,"~thexport")
        framesDir = os.path.join(exportPath,"~thexport","frames")
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)
        if not os.path.isdir(framesDir):
            os.mkdir(framesDir)
        if xmlFile == None:
            fileName = os.path.join(framesDir,os.path.basename(xmlFilename))
        else:
            fileName = xmlFile
        exporter.write(fileName, "Blender Scene")
        if scn.thea_UseZip:
            #print ("Compressing xml file")
            exporter.zipFile(fileName)
            fileName = os.path.join(framesDir,os.path.basename(xmlFilename).replace(".xml",".tzx"))
        mergeString = (" %s %s %s %s %s %s %s" % (scn.thea_MerModels, scn.thea_MerLights, scn.thea_MerCameras, scn.thea_MerEnv, scn.thea_MerRender, scn.thea_MerMaterials, scn.thea_MerSurfaces))
        message = 'message "Merge '+fileName+mergeString+'"\n'
        scriptFile.write(message)
        message = 'message "Render"\n'
        scriptFile.write(message)
        if scn.frame_start == frame:
           if scn.thea_ICLock:
               scriptFile.write('message "Lock Irradiance Cache"\n')
           if scn.thea_CausticLock:
               scriptFile.write('message "Lock Caustic Map"\n')
        message = 'message "SaveImage '+os.path.join(framesDir,os.path.basename(imgFilename))+'"\n'
        scriptFile.write(message)
        firstFrame = False
    else:
        if xmlFile == None:
            xmlFilename = currentBlendFile.replace('.blend', '.xml')
            imgFilename = currentBlendFile.replace('.blend', fileFormat)
            fileName = os.path.join(exportPath,os.path.basename(xmlFilename))
        else:
            fileName = xmlFile
        #print(fileName)
        exporter.write(fileName, "Blender Scene")
        if scn.thea_UseZip:
            #print ("Compressing xml file")
            exporter.zipFile(fileName)

    #print("Cleaning temporary objects")
    try:
        object.select_all(action = 'DESELECT')
        for object in tempObjects:
            object.select = True

        # remove all selected.
        bpy.ops.object.delete()
    except:
        pass

    scn.thea_WasExported = True

    thea_globals.log.info('Frame export time: %.4fs'% (time.time() - time1)   )
    args = []
    if scn.get('thea_startTheaAfterExport'):
        args.append(str(theaPath))
        if scene.thea_regionRender:
            if scene.thea_regionDarkroom:
                args.append("-darkroom")
        args.append(" -license")
        args.append("blender")

        args.append("-load")
        scriptFilename = os.path.join(exportPath, os.path.basename(currentBlendFile.replace('.blend', '_exportFrame.ipt.thea')))
        scriptFile = open(scriptFilename, "w")
        scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(fileName) + '\"\n'))
#        fileName = fil
        args.append(scriptFilename)
#        args.append(fileName)
        if scene.thea_regionRender:
            regionRenderThea(scene)
            thea_globals.log.debug("ARGS:" % args)
            fileName = currentBlendFile.replace('.blend', '_regionRender.ipt.thea')
            iptFileName = os.path.join(exportPath,os.path.basename(fileName))
            args.append(iptFileName)
        return args
    else:
        return True




def exportAnim(scene, exporter=None):
    '''Export animation as set of single frames and ipt.thea script to render them

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
    '''
    global scn
    global scriptFile, exportPath, firstFrame

    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
    firstFrame = True

    startFrame=scn.frame_start
    endFrame=scn.frame_end
    currFrame = scn.frame_current

    tempDir = os.path.join(exportPath, "~thexport")
    framesDir = os.path.join(exportPath,"~thexport","frames")
    if not os.path.isdir(tempDir):
        os.mkdir(tempDir)
    if not os.path.isdir(framesDir):
        os.mkdir(framesDir)

    scriptFilename = currentBlendFile.replace('.blend', '_'+scn.camera.name+'.ipt.thea')
    scriptFile = open(os.path.join(exportPath,os.path.basename(scriptFilename)), "w")

    for frame in range(startFrame, endFrame+1, 1):
        #print ("\n\nExporting frame: ",frame)
        scn.frame_set(frame)
        exportFrame(scene,frame, anim=True, exporter=initExporter())


    scn.frame_set(currFrame)
    scriptFile.close()



def exportStillCameras(scene, exporter=None): #this will export ipt.thea script will all visible cameras to render them in single animaiton
    '''Export ipt.thea script will all visible cameras to render them in single animation

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param exporter: exporter instance
        :type exporter: thea_exporter.XMLExporter
    '''

    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)

    time1 = os.times()[4]

    renderData = scn.render

    resX=int(renderData.resolution_x*renderData.resolution_percentage*0.01)
    resY=int(renderData.resolution_y*renderData.resolution_percentage*0.01)

    scriptFilename = currentBlendFile.replace('.blend', '_cameras.ipt.thea')
    scriptFile = open(os.path.join(exportPath,os.path.basename(scriptFilename)), "w")

    # export cameras
    for camOb in bpy.data.objects:
        if camOb.type == 'CAMERA':
            camData = camOb.data
            firstFrame = True
            if camOb.is_visible(scn):
                exporter.getRenderOptions().activeCamera = camOb.name
                cam = ThCamera()
                cam.name=camOb.name
                cam.pixels = resX
                cam.lines = resY

                if resX > resY:
                    fac = float(resX) / float(resY)
                else:
                    fac = 1

                if camData.type == "PERSP":
                    cam.focalLength = camData.lens
                    cam.pinhole = camOb.thea_pinhole
                    cam.enableDOFpercentage = camOb.thea_enableDOFpercentage
#                    cam.focusDistance = 1
#                   CHANGED > to try, was getting error when nothing was changed from startup file
                    try:
                        aperture = camOb["aperture"]
                        DOFpercentage = camOb["thea_DOFpercentage"]
                    except: pass
                    #                    added this line to check none distance
                    if camData.dof_distance == 0 and camData.dof_object:
                        #                    cam.focusDistance = camData.dof_distance
                        obj1 = cam.name
                        obj2 = camData.dof_object.name
                        #                    obj1_loc = bpy.data.objects[obj1].matrix_world.to_translation()
                        #                    obj2_loc = bpy.data.objects[obj2].matrix_world.to_translation()
                        obj1_loc = bpy.data.objects[obj1].location
                        obj2_loc = bpy.data.objects[obj2].location
                        dist = (obj1_loc - obj2_loc).length
                        cam.focusDistance = dist
                        #print("dof_distance: ", cam.focusDistance)
                        try:
                            if cam.pinhole == 0:
                                #print("***PINHOLE CHECK: ", cam.pinhole)
                                cam.fNumber = aperture
                            else:
                                cam.fNumber = "Pinhole"
                        except: pass
                        try:
                            if cam.enableDOFpercentage == 1:
                                #print("***PINHOLE CHECK: ", cam.pinhole)
                                cam.DOFpercentage = DOFpercentage
                            else:
                                cam.DOFpercentage = 0
                        except: pass
                    else:
                        cam.fNumber = 0
                        #print("APERTURE B - ALL 0:", aperture)
                    cam.filmHeight = 32 / fac
                    cam.shiftLensX = camData.shift_x
                    cam.shiftLensY = camData.shift_y
                    cam.projection = getattr(camOb, 'thea_projection', 'Perspective')
                    if (getattr(camOb, 'thea_diaphragma') in ("Polygonal")):
                        cam.diaphragma = camOb.thea_diaphragma
                        cam.blades = camOb.thea_diapBlades
                elif camData.type == "ORTHO":
                    cam.projection = "Parallel"
#                    cam.filmHeight = (camOb.scale*1000)/fac
                    if camData.sensor_fit == 'VERTICAL':
                        cam.filmHeight = camData.ortho_scale * 1000
                        thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.ortho_scale, camData.sensor_fit,fac))
                    elif camData.sensor_fit == 'HORIZONTAL' or 'AUTO':
                        cam.filmHeight = (camData.ortho_scale * 1000) / fac
                        thea_globals.log.debug("LENS scale: %s - Sensor: %s - Fac: %s" % (camData.ortho_scale, camData.sensor_fit,fac))
                    cam.focalLength = camData.lens
                if camData.dof_distance > 0:
                    cam.focusDistance = camData.dof_distance
                    try:
                        aperture = camOb["aperture"]
                        DOFpercentage = camOb["thea_DOFpercentage"]
                        if cam.pinhole == 0:
                            cam.fNumber = aperture
                        else:
                            cam.fNumber = "Pinhole"
                    except: pass
                    try:
                        if cam.enableDOFpercentage == 1:
                            #print("***PINHOLE CHECK: ", cam.pinhole)
                            cam.DOFpercentage = DOFpercentage
                        else:
                            cam.DOFpercentage = 0
                    except: pass
                else:
                    cam.fNumber = 0

                camM = camOb.matrix_world
#                CHANGED> removed forwardslash below, think was mistype orso
                cam.frame = Transform(
                camM[0][0], -camM[0][1], -camM[0][2],
                camM[1][0], -camM[1][1], -camM[1][2],
                camM[2][0], -camM[2][1], -camM[2][2],
                camM[0][3],  camM[1][3],  camM[2][3])

                fileFormat = ".png"
                if scn.render.image_settings.file_format == "JPEG":
                    fileFormat = ".jpg"
                if scn.render.image_settings.file_format == "PNG":
                    fileFormat = ".png"
                if scn.render.image_settings.file_format == "BMP":
                    fileFormat = ".bmp"
                if scn.render.image_settings.file_format == "HDR":
                    fileFormat = ".hdr"
                if scn.render.image_settings.file_format == "OPEN_EXR":
                    fileFormat = ".exr"
                if scn.render.image_settings.file_format == "TIFF":
                    fileFormat = ".tif"
                exporter.addCamera(cam)
                xmlFilename = currentBlendFile.replace('.blend', '_cam'+cam.name+'.xml')
                imgFilename = currentBlendFile.replace('.blend', '_f'+cam.name)
                tempDir = os.path.join(exportPath,"~thexport")
                framesDir = os.path.join(exportPath,"~thexport","frames")
                if not os.path.isdir(tempDir):
                    os.mkdir(tempDir)
                if not os.path.isdir(framesDir):
                    os.mkdir(framesDir)
                fileName = os.path.join(framesDir,os.path.basename(xmlFilename))
                exporter.write(fileName, "Blender Scene")
                mergeString = (" 0 0 1 0 0")
                if platform.system() == "Darwin":
                    message = 'message "Merge \''+fileName+'\''+mergeString+'"\n'
                else:
                    message = 'message "Merge '+fileName+mergeString+'"\n'
                scriptFile.write(message)
                message = 'message "Render"\n'
                scriptFile.write(message)
#                CHNAGED> Added fileformat here for better reuse variable imFilename
                message = 'message "SaveImage '+os.path.join(framesDir,os.path.basename(imgFilename[:-4].strip())+fileFormat)+'"\n'
                scriptFile.write(message)
                #    CHANGED> Added channels for still camera's'
#                outputImage = os.path.join(framesDir, os.path.basename(imgFilename) + fileFormat)
                outputIMG = os.path.join(framesDir, os.path.basename(imgFilename[:-4].strip()) +".img.thea")
                outputChannelImage = os.path.join(framesDir, os.path.basename(imgFilename[:-4].strip()))
                exporter.getRenderOptions().checkChannels = scn.thea_showChannels
                checkChannels = exporter.getRenderOptions().checkChannels
                try:
                    alphaMode = scn.get('thea_channelAlpha')
                except:
                    alphaMode = False
                if scn.thea_ImgTheaFile:
                   scriptFile.write('message \"SaveImage %s\"\n' % outputIMG)
                if checkChannels == True:
                   try:
                       if scn.thea_channelNormal:
                           scriptFile.write('message \"SaveChannel \'Normal\' %s\"\n' % os.path.join(framesDir,"normal",outputChannelImage+"_normal"+fileFormat ))
                       if scn.thea_channelPosition:
                           scriptFile.write('message \"SaveChannel \'Position\' %s\"\n' % os.path.join(framesDir,"position",outputChannelImage+"_position"+ fileFormat))
                       if scn.thea_channelUV:
                           scriptFile.write('message \"SaveChannel \'UV\' %s\"\n' % os.path.join(framesDir,"uv",outputChannelImage+"_uv"+fileFormat))
                       if scn.thea_channelDepth:
                           scriptFile.write('message \"SaveChannel \'Depth\' %s\"\n' % os.path.join(framesDir, "depth", outputChannelImage+"_depth"+fileFormat))
                       if alphaMode:
                           scriptFile.write('message \"SaveChannel \'Alpha\' %s\"\n' % os.path.join(framesDir, "alpha", outputChannelImage+"_aLpha"+fileFormat))
                       if scn.thea_channelObject_Id:
                           scriptFile.write('message \"SaveChannel \'Object Id\' %s\"\n' % os.path.join(framesDir, "object_id", outputChannelImage+"_object_ID"+fileFormat))
                       if scn.thea_channelMaterial_Id:
                           scriptFile.write('message \"SaveChannel \'Material Id\' %s\"\n' % os.path.join(framesDir, "material_id", outputChannelImage+"_material_ID"+fileFormat))
                       if scn.thea_channelShadow:
                           scriptFile.write('message \"SaveChannel \'Shadow\' %s\"\n' % os.path.join(framesDir,"shadow",outputChannelImage+"_shadow"+fileFormat))
            #            CHANGED> Added mask back in CHECK numbering system
                       if scn.thea_channelMask:
                           maskIndexList = []
                           for obName in scn.objects:
                               ob = obName
                               if ob.thMaskID == True:
                                   maskIndex = ob.thMaskIDindex
                                   if not maskIndex in maskIndexList:
                                       scriptFile.write('message \"SaveChannel \'Mask #%s\' %s\"\n' % (maskIndex, os.path.join(framesDir,"mask",outputChannelImage + "_mask" + str(maskIndex) + fileFormat)))
                                       maskIndexList.append(maskIndex)
                       if scn.thea_channelRaw_Diffuse_Color:
                           scriptFile.write('message \"SaveChannel \'Raw Diffuse Color\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_color",outputChannelImage+"_raw-diffuse-color"+fileFormat))
                       if scn.thea_channelRaw_Diffuse_Lighting:
                           scriptFile.write('message \"SaveChannel \'Raw Diffuse Lighting\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_lighting",outputChannelImage+"_raw-diffuse-light"+fileFormat))
                       if scn.thea_channelRaw_Diffuse_GI:
                           scriptFile.write('message \"SaveChannel \'Raw Diffuse GI\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_gi",outputChannelImage+"_raw-diffuse-gi"+fileFormat))
                       if scn.thea_channelSelf_Illumination:
                           scriptFile.write('message \"SaveChannel \'Self Illumination\' %s\"\n' % os.path.join(framesDir,"self_illumination",outputChannelImage+"_self-illumunitation"+fileFormat))
                       if scn.thea_channelDirect:
                           scriptFile.write('message \"SaveChannel \'Direct\' %s\"\n' % os.path.join(framesDir, "direct", outputChannelImage+"_direct"+fileFormat))
                       if scn.thea_channelAO:
                           scriptFile.write('message \"SaveChannel \'AO\' %s\"\n' % os.path.join(framesDir, "ao", outputChannelImage+"_ao"+fileFormat))
                       if scn.thea_channelGI:
                            scriptFile.write('message \"SaveChannel \'GI\' %s\"\n' % os.path.join(framesDir, "gi", outputChannelImage+"_gi"+fileFormat))
                       if scn.thea_channelSSS:
                            scriptFile.write('message \"SaveChannel \'SSS\' %s\"\n' % os.path.join(framesDir, "sss", outputChannelImage+"_sss"+fileFormat))
                       if scn.thea_channelSeparate_Passes_Per_Light:
                            scriptFile.write('message \"SaveChannel Separate Passes Per Light %s\"\n' % os.path.join(framesDir, "PassesPerLight", outputChannelImage+"_passes-per-light+"+fileFormat))
                       if scn.thea_channelReflection:
                           scriptFile.write('message \"SaveChannel \'Reflection\' %s\"\n' % os.path.join(framesDir, "reflection", outputChannelImage+"_reflection"+fileFormat))
                       if scn.thea_channelRefraction:
                           scriptFile.write('message \"SaveChannel \'Refraction\' %s\"\n' % os.path.join(framesDir, "refraction", outputChannelImage+"_tefraction"+fileFormat))
                       if scn.thea_channelTransparent:
                           scriptFile.write('message \"SaveChannel \'Transparent\' %s\"\n' % os.path.join(framesDir, "transparent", outputChannelImage+"_transparent"+fileFormat))
                       if scn.thea_channelIrradiance:
                           scriptFile.write('message \"SaveChannel \'Irradiance\' %s\"\n' % os.path.join(framesDir,"irradiance",outputChannelImage+"_irradiance"+fileFormat))
                   except: pass
                firstFrame = False



def renderFrame(scene,frame,anim=True):
    ''' Export current frame and prepare ipt.thea script to load, merge render and save render results

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :param frame: Frame number to render
        :type frame: int
        :return: list with arguments to start Thea process
        :rtype: list
    '''
    thea_globals.log.debug("*** Render Animation: %s" % anim)
    t1 = datetime.datetime.now()
    global guiSets
    global scn, exportPath, command, tmpTheaRenderFile, outputImage
    maskIndex = []
    maskIndexList = []
    exporter=initExporter()
    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
    frameS= "0000" + str(frame)
    xmlFilename = currentBlendFile.replace('.blend', '.xml')
    os.chdir(os.path.dirname(theaPath))
    exportFrame(scene,frame,exporter=exporter)
    if scn.thea_ExitAfterRender or anim:
        exitCom = "-exit"
    else:
        exitCom = ""

    fileFormat = ".png"
    color_mode = scene.render.image_settings.color_mode


    if scn.render.image_settings.file_format == "JPEG":
        fileFormat = ".jpg"
    if scn.render.image_settings.file_format == "PNG":
        fileFormat = ".png"
    if scn.render.image_settings.file_format == "BMP":
        fileFormat = ".bmp"
    if scn.render.image_settings.file_format == "HDR":
        fileFormat = ".hdr"
    if scn.render.image_settings.file_format == "OPEN_EXR" or scn.render.image_settings.file_format == "OPEN_EXR_MULTILAYER":
        fileFormat = ".exr"
    if scn.render.image_settings.file_format == "TIFF":
        fileFormat = ".tif"

    try:
        alphaMode = scn.get('thea_channelAlpha')
    except:
        alphaMode = False


    channels = ('normal','position','uv','depth','alpha','object_id','material_id','shadow','mask','raw_diffuse_color','raw_diffuse_lighting','raw_diffuse_gi','self_illumination','direct','ao','gi','sss','passes per light','reflection','refraction','transparent','irradiance')
    if anim:
        framesDir = os.path.join(exportPath,"~thexport","frames")
        if not os.path.isdir(framesDir):
            os.mkdir(framesDir)
        if os.path.isdir(framesDir):
            for ch in channels:
                channelDir = os.path.join(framesDir,ch)
                if not os.path.isdir(channelDir):
                    os.mkdir(channelDir)
        outputImage = os.path.join(framesDir, os.path.basename(xmlFilename[:-4].strip()) +"_"+scn.camera.name +"_"+frameS[-4:] + fileFormat)
#       CHANGED > added img.thea file for animation, though this is tricky, will take away a lot of time cause it saves out img file 2 times
        outputIMG = os.path.join(framesDir, os.path.basename(xmlFilename[:-4].strip()) +"_"+scn.camera.name +"_"+frameS[-4:] + ".img.thea")
        outputChannelImage = os.path.basename(xmlFilename[:-4].strip())+"_"+scn.camera.name +"_"+frameS[-4:]
    else:
        outputImage = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].strip()) +"_"+scn.camera.name +"_"+frameS[-4:] + fileFormat)
#       CHANGED > added img.thea file for animation, though this is tricky, will take away a lot of time cause it saves out img file 2 times
        outputIMG = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].strip()) +"_"+scn.camera.name +"_"+frameS[-4:] + ".img.thea")
        outputChannelImage = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].strip()) +"_"+scn.camera.name +"_"+frameS[-4:])




    args = []

    scriptFilename = os.path.join(exportPath, os.path.basename(currentBlendFile.replace('.blend', '_render.ipt.thea')))
    scriptFile = open(scriptFilename, "w")

    saveScriptFilename = os.path.join(exportPath, os.path.basename(currentBlendFile.replace('.blend', '_save.ipt.thea')))
    saveScriptFile = open(saveScriptFilename, "w")

    if getattr(bpy.context.scene, "thea_showMerge"):
        if scn.thea_SceneMerReverseOrder:
            #load another scene and then merge exported one
            if os.path.exists(scn.thea_mergeFilePath):
                mergeString = (" %s %s %s %s %s %s" % (scn.thea_SceneMerModels, scn.thea_SceneMerLights, scn.thea_SceneMerCameras, scn.thea_SceneMerRender, scn.thea_SceneMerEnv, scn.thea_SceneMerMaterials))
                scriptFile.write('message \"Load ' +  scn.thea_mergeFilePath + '\"\n')
                scriptFile.write('message \"Merge ' + os.path.join(exportPath, os.path.basename(xmlFilename) + mergeString + '\"\n'))
            else:
                scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))
        else:
            scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))

            #merge another scene after load
            if os.path.exists(scn.thea_mergeFilePath):
                mergeString = (" %s %s %s %s %s %s" % (scn.thea_SceneMerModels, scn.thea_SceneMerLights, scn.thea_SceneMerCameras, scn.thea_SceneMerRender, scn.thea_SceneMerEnv, scn.thea_SceneMerMaterials))
                scriptFile.write('message \"Merge ' +  scn.thea_mergeFilePath + mergeString + '\"\n')
    else:
        scriptFile.write('message \"Load ' + os.path.join(exportPath, os.path.basename(xmlFilename) + '\"\n'))


    #     if os.name == "nt":
    #         theaPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "WIN", "TheaRemoteDarkroom.exe")
    #     if os.name == "posix":
    #         import stat
    #         darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OSX", "TheaRemoteDarkroom.app/Contents/MacOS/TheaRemoteDarkroom")
    #         os.chmod(darkroomfile, stat.S_IEXEC)
    #         theaPath = darkroomfile
         #       CHANGED > ADDED MARKER NAMING AND CUSTOM NAMING
    if anim and exporter.getRenderOptions().customOutput:
        prefix = exporter.getRenderOptions().customName
        prefix = prefix + "_"
        xmlFilename = prefix
        outputImage = os.path.join(framesDir, os.path.basename(xmlFilename) +"_"+scn.camera.name +"_"+frameS[-4:] + fileFormat)
#       CHANGED > added img.thea file for animation, though this is tricky, will take away a lot of time cause it saves out img file 2 times
        outputIMG = os.path.join(framesDir, os.path.basename(xmlFilename) +"_"+scn.camera.name +"_"+frameS[-4:] + ".img.thea")
        outputChannelImage = os.path.basename(xmlFilename)+"_"+scn.camera.name +"_"+frameS[-4:]

    else:
        prefix = ""
    if anim and exporter.getRenderOptions().markerName:
        frame_current = scn.frame_current
        markers = scn.timeline_markers
        for m in markers:
            if m.frame == frame_current:
#                for k,v in scn.timeline_markers.items():
#                    frame = v.frame
                name = m.name
                outputImage = os.path.join(framesDir, prefix + os.path.basename(name) +"_"+scn.camera.name + fileFormat)
                outputIMG = os.path.join(framesDir, prefix + os.path.basename(name) +"_"+scn.camera.name + ".img.thea")
                outputChannelImage = os.path.join(framesDir, prefix + os.path.basename(name) +"_"+scn.camera.name )
                thea_globals.log.debug("Save Markername as Filename: %s" % exporter.getRenderOptions().markerName)
                thea_globals.log.debug("Prefix: %s Marker name: %s Frame: %s" % (prefix, name, frame))

    args.append(scriptFilename)
    args.append(saveScriptFilename)
#         args.append(str(theaPath))
    if scn.get('thea_HideThea') != False:
        args.append("-hidden")
    args.append(exitCom)
#    if scn.thea_regionRender !=True:
    scriptFile.write('message \"Render\"\n')

    thea_globals.log.debug("*** Save 2 Export only: %s" % getattr(scn,"thea_save2Export", False))
    if anim and (getattr(scn,"thea_save2Export")!=True):

#         args.append("-darkroom")
#         args.append("-nosplash")
        if scn.frame_start == frame:
#             args.append("-load")
#             args.append(scriptFilename)

            if color_mode == "RGBA":
                saveScriptFile.write('message \"SaveChannel +Alpha %s\"\n' % outputImage)
                exporter.getRenderOptions().alphaChannel = True
            else:
                if scn.render.image_settings.file_format == "OPEN_EXR_MULTILAYER":
                    saveScriptFile.write('message \"SaveLayeredImage %s\"\n' % outputImage)
                else:
                    saveScriptFile.write('message \"SaveImage %s\"\n' % outputImage)
            if scn.thea_ICLock:
               saveScriptFile.write('message \"Save Irradiance Cache ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.irc.thea\"\n'))
            if scn.thea_CausticLock:
                saveScriptFile.write('message \"Save Caustic Map ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.cpm.thea\"\n'))
        else:
#             args.append("-load")
#             args.append(scriptFilename)
            if scn.thea_ICLock:
               saveScriptFile.write('message \"Load Irradiance Cache ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.irc.thea\"\n'))
            if scn.thea_CausticLock:
                saveScriptFile.write('message \"Load Caustic Map ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.cpm.thea\"\n'))
#            scriptFile.write('message \"Render\"\n')
            if scn.thea_ICLock:
               saveScriptFile.write('message \"Save Irradiance Cache ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.irc.thea\"\n'))
            if scn.thea_CausticLock:
                saveScriptFile.write('message \"Save Caustic Map ' + os.path.join(exportPath,os.path.basename(xmlFilename) + '.cpm.thea\"\n'))
            if color_mode == "RGBA":
                saveScriptFile.write('message \"SaveChannel +Alpha %s\"\n' % outputImage)
                exporter.getRenderOptions().alphaChannel = True
            else:
                if scn.render.image_settings.file_format == "OPEN_EXR_MULTILAYER":
                    saveScriptFile.write('message \"SaveLayeredImage %s\"\n' % outputImage)
                else:
                    saveScriptFile.write('message \"SaveImage %s\"\n' % outputImage)
#       CHANGED > added option to save img.thea file
        if exporter.getRenderOptions().ImgTheaFile:
            saveScriptFile.write('message \"SaveImage %s\"\n' % outputIMG)
        if checkChannels == True:
            #                                    CHANGED > added single quote ' before and after each channel, else it wont save on mac. WIndows is different i ebeleive
            if exporter.getRenderOptions().normalChannel:
                saveScriptFile.write('message \"SaveChannel \'Normal\' %s\"\n' % os.path.join(framesDir,"normal",outputChannelImage + "_normal"+ fileFormat))
            if exporter.getRenderOptions().positionChannel:
                saveScriptFile.write('message \"SaveChannel \'Position\' %s\"\n' % os.path.join(framesDir,"position",outputChannelImage + "_position"+ fileFormat))
            if exporter.getRenderOptions().uvChannel:
                saveScriptFile.write('message \"SaveChannel \'UV\' %s\"\n' % os.path.join(framesDir,"uv",outputChannelImage + "_uv"+ fileFormat))
            if exporter.getRenderOptions().depthChannel:
                saveScriptFile.write('message \"SaveChannel \'Depth\' %s\"\n' % os.path.join(framesDir, "depth", outputChannelImage + "_depth"+ fileFormat))
            if alphaMode:
                saveScriptFile.write('message \"SaveChannel \'Alpha\' %s\"\n' % os.path.join(framesDir, "alpha", outputChannelImage + "_alpha"+ fileFormat))
            if exporter.getRenderOptions().objectIdChannel:
                saveScriptFile.write('message \"SaveChannel \'Object Id\' %s\"\n' % os.path.join(framesDir, "object_id", outputChannelImage + "_objectID"+ fileFormat))
            if exporter.getRenderOptions().materialIdChannel:
                saveScriptFile.write('message \"SaveChannel \'Material Id\' %s\"\n' % os.path.join(framesDir, "material_id", outputChannelImage + "_materialID"+ fileFormat))
            if exporter.getRenderOptions().shadowChannel:
                saveScriptFile.write('message \"SaveChannel \'Shadow\' %s\"\n' % os.path.join(framesDir,"shadow",outputChannelImage + "_Shadow"+ fileFormat))
#            CHANGED> Added mask back in CHECK numbering system
            if exporter.getRenderOptions().maskChannel:
                maskIndexList = []
                for obName in scn.objects:
                    ob = obName
                    if ob.thMaskID == True:
                        maskIndex = ob.thMaskIDindex
                        if not maskIndex in maskIndexList:
                            saveScriptFile.write('message \"SaveChannel \'Mask #%s\' %s\"\n' % (maskIndex, os.path.join(framesDir,"mask",outputChannelImage + "_mask" + str(maskIndex) + fileFormat)))
                            maskIndexList.append(maskIndex)
    #                    thea_globals.log.debug("Mask Index Number: %s" % maskIndex)
#            if exporter.getRenderOptions().invertMaskChannel:
#                scriptFile.write('message \"SaveChannel Mask %s\"\n' % os.path.join(framesDir,"mask",outputChannelImage + fileFormat))
            if exporter.getRenderOptions().rawDiffuseColorChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse Color\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_color",outputChannelImage + "_raw-diffuse-color" + fileFormat))
            if exporter.getRenderOptions().rawDiffuseLightingChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse Lighting\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_lighting",outputChannelImage + "_raw-diffuse-lighting" + fileFormat))
            if exporter.getRenderOptions().rawDiffuseGIChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse GI\' %s\"\n' % os.path.join(framesDir,"raw_diffuse_gi",outputChannelImage  + "_raw-diffuse-gi"+ fileFormat))
            if exporter.getRenderOptions().selfIlluminationChannel:
                saveScriptFile.write('message \"SaveChannel \'Self Illumination\' %s\"\n' % os.path.join(framesDir,"self_illumination",outputChannelImage + "_self-illumination" + fileFormat))
            if exporter.getRenderOptions().directChannel:
                saveScriptFile.write('message \"SaveChannel \'Direct\' %s\"\n' % os.path.join(framesDir, "direct", outputChannelImage + "_direct" + fileFormat))
            if exporter.getRenderOptions().AOChannel:
                saveScriptFile.write('message \"SaveChannel \'AO\' %s\"\n' % os.path.join(framesDir, "ao", outputChannelImage + "_ao" + fileFormat))
            if exporter.getRenderOptions().giChannel:
                saveScriptFile.write('message \"SaveChannel \'GI\' %s\"\n' % os.path.join(framesDir, "gi", outputChannelImage + "_gi" + fileFormat))
#            CHANGED> Turned this backon + light passes
            if exporter.getRenderOptions().sssChannel:
                scriptFile.write('message \"SaveChannel SSS %s\"\n' % os.path.join(framesDir, "sss", outputChannelImage  + "_sss"+ fileFormat))
            if exporter.getRenderOptions().separatePassesPerLightChannel:
                scriptFile.write('message \"SaveChannel Passes Per Light %s\"\n' % os.path.join(framesDir, "passes per light", outputChannelImage + "_passes-per-light" + fileFormat))
            if exporter.getRenderOptions().reflectionChannel:
                saveScriptFile.write('message \"SaveChannel \'Reflection\' %s\"\n' % os.path.join(framesDir, "reflection", outputChannelImage + "_reflection" + fileFormat))
            if exporter.getRenderOptions().refractionChannel:
                saveScriptFile.write('message \"SaveChannel \'Refraction\' %s\"\n' % os.path.join(framesDir, "refraction", outputChannelImage + "_refraction" + fileFormat))
            if exporter.getRenderOptions().transparentChannel:
                saveScriptFile.write('message \"SaveChannel \'Transparent\' %s\"\n' % os.path.join(framesDir, "transparent", outputChannelImage + "_transparent" + fileFormat))
            if exporter.getRenderOptions().irradianceChannel:
                saveScriptFile.write('message \"SaveChannel \'Irradiance\' %s\"\n' % os.path.join(framesDir,"irradiance",outputChannelImage + "_irradiance" + fileFormat))

#         args.append("-exit")



    else:
        #save rendered image also in exportPath dir
        outputImage = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].rstrip()) +"_"+scn.camera.name + fileFormat)
        outputIMG = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].rstrip()) +"_"+scn.camera.name + ".img.thea")
        outputChannelImage = os.path.join(exportPath, os.path.basename(xmlFilename[:-4].rstrip()) +"_"+scn.camera.name )
    if getattr(scn,"thea_save2Export")!=False:
        if exporter.getRenderOptions().customOutput:
            prefix = exporter.getRenderOptions().customName
            prefix = prefix + "_"
            xmlFilename = prefix
        else:
            prefix = ""
        if exporter.getRenderOptions().markerName:
            frame_current = scn.frame_current
            markers = scn.timeline_markers
            for m in markers:
                if m.frame == frame_current:
    #                for k,v in scn.timeline_markers.items():
    #                    frame = v.frame
                    name = m.name
                    outputImage = os.path.join(exportPath, prefix + os.path.basename(name) +"_"+scn.camera.name + fileFormat)
                    outputIMG = os.path.join(exportPath, prefix + os.path.basename(name) +"_"+scn.camera.name + ".img.thea")
                    outputChannelImage = os.path.join(exportPath, prefix + os.path.basename(name) +"_"+scn.camera.name )
                    thea_globals.log.debug("Save Markername as Filename: %s" % exporter.getRenderOptions().markerName)
                    thea_globals.log.debug("Prefix: %s Marker name: %s Frame: %s" % (prefix, name, frame))
        if color_mode == "RGBA":
            saveScriptFile.write('message \"SaveChannel +Alpha %s\"\n' % outputImage)
            exporter.getRenderOptions().alphaChannel = True
        else:
            if scn.render.image_settings.file_format == "OPEN_EXR_MULTILAYER":
                saveScriptFile.write('message \"SaveLayeredImage %s\"\n' % outputImage)
            else:
                saveScriptFile.write('message \"SaveImage %s\"\n' % outputImage)
        thea_globals.log.debug("Save2Export: %s - Filename: %s" % (getattr(scn,"thea_save2Export"), outputImage))
        if checkChannels == True:
            if exporter.getRenderOptions().ImgTheaFile:
                saveScriptFile.write('message \"SaveImage %s\"\n' % outputIMG)
            if exporter.getRenderOptions().normalChannel:
                saveScriptFile.write('message \"SaveChannel \'Normal\' %s\"\n' % (outputChannelImage + "_normal" + fileFormat))
            if exporter.getRenderOptions().positionChannel:
                saveScriptFile.write('message \"SaveChannel \'Position\' %s\"\n' % (outputChannelImage + "_position" + fileFormat))
            if exporter.getRenderOptions().uvChannel:
                saveScriptFile.write('message \"SaveChannel \'UV\' %s\"\n' % (outputChannelImage + "_uv" + fileFormat))
            if exporter.getRenderOptions().depthChannel:
                saveScriptFile.write('message \"SaveChannel \'Depth\' %s\"\n' % (outputChannelImage + "_depth" + fileFormat))
            if alphaMode:
                saveScriptFile.write('message \"SaveChannel \'Alpha\' %s\"\n' % (outputChannelImage + "_alpha" + fileFormat))
            if exporter.getRenderOptions().objectIdChannel:
                saveScriptFile.write('message \"SaveChannel \'Object Id\' %s\"\n' % (outputChannelImage + "_object_id" + fileFormat))
            if exporter.getRenderOptions().materialIdChannel:
                saveScriptFile.write('message \"SaveChannel \'Material Id\' %s\"\n' % (outputChannelImage + "_material_id" + fileFormat))
            if exporter.getRenderOptions().shadowChannel:
                saveScriptFile.write('message \"SaveChannel \'Shadow\' %s\"\n' % (outputChannelImage + "_shadow" + fileFormat))
    #            CHANGED> Added mask back in CHECK numbering system
            if exporter.getRenderOptions().maskChannel:
                maskIndexList = []
                for obName in scn.objects:
                    ob = obName
                    if ob.thMaskID == True:
                        maskIndex = ob.thMaskIDindex
                        if not maskIndex in maskIndexList:
                            saveScriptFile.write('message \"SaveChannel \'Mask #%s\' %s\"\n' % (maskIndex, outputChannelImage + "_Mask" + str(maskIndex) + fileFormat))
                            maskIndexList.append(maskIndex)
                        thea_globals.log.debug("Mask Index Number: %s" % maskIndexList)
    #            if exporter.getRenderOptions().maskChannel:
    #                saveScriptFile.write('message \"SaveChannel \'Mask %s\' %s\"\n' % ("#3", outputChannelImage + "_mask" + fileFormat))
            if exporter.getRenderOptions().rawDiffuseColorChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse Color\' %s\"\n' % (outputChannelImage + "_raw_diffuse_color" + fileFormat))
            if exporter.getRenderOptions().rawDiffuseLightingChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse Lighting\' %s\"\n' % (outputChannelImage + "_raw_diffuse_lighting" + fileFormat))
            if exporter.getRenderOptions().rawDiffuseGIChannel:
                saveScriptFile.write('message \"SaveChannel \'Raw Diffuse GI\' %s\"\n' % (outputChannelImage + "_raw_diffuse_gi" + fileFormat))
            if exporter.getRenderOptions().selfIlluminationChannel:
                saveScriptFile.write('message \"SaveChannel \'Self Illumination\' %s\"\n' % (outputChannelImage + "_self_illumination" + fileFormat))
            if exporter.getRenderOptions().directChannel:
                saveScriptFile.write('message \"SaveChannel \'Direct\' %s\"\n' % (outputChannelImage + "_direct" + fileFormat))
            if exporter.getRenderOptions().AOChannel:
                saveScriptFile.write('message \"SaveChannel \'AO\' %s\"\n' % (outputChannelImage + "_ao" + fileFormat))
            if exporter.getRenderOptions().giChannel:
                saveScriptFile.write('message \"SaveChannel \'GI\' %s\"\n' % (outputChannelImage + "_gi" + fileFormat))
            #CHANGED> turned back on + added passes per light
            if exporter.getRenderOptions().sssChannel:
                scriptFile.write('message \"SaveChannel SSS %s\"\n' % (outputChannelImage + "_sss" + fileFormat))
            if exporter.getRenderOptions().separatePassesPerLightChannel:
                scriptFile.write('message \"SaveChannel Passes Per Light %s\"\n' % (outputChannelImage + "_PassesLight" + fileFormat))
            if exporter.getRenderOptions().reflectionChannel:
                saveScriptFile.write('message \"SaveChannel \'Reflection\' %s\"\n' % (outputChannelImage + "_reflection" + fileFormat))
            if exporter.getRenderOptions().refractionChannel:
                saveScriptFile.write('message \"SaveChannel \'Refraction\' %s\"\n' % (outputChannelImage + "_refraction" + fileFormat))
            if exporter.getRenderOptions().transparentChannel:
                saveScriptFile.write('message \"SaveChannel \'Transparent\' %s\"\n' % (outputChannelImage + "_transparent" + fileFormat))
            if exporter.getRenderOptions().irradianceChannel:
                saveScriptFile.write('message \"SaveChannel \'Irradiance\' %s\"\n' % (outputChannelImage + "_irradiance"+ fileFormat))

    #         if exporter.getRenderOptions().depthChannel:
    #             saveScriptFile.write('message \"SaveChannel Depth %s\"\n' % (outputChannelImage + "_depth" + fileFormat))
    #         if alphaMode:
    #             saveScriptFile.write('message \"SaveChannel Alpha %s\"\n' % (outputChannelImage + "_alpha" + fileFormat))






    theaSessionDir = os.path.join(dataPath, "Temp")
#     args.append("-session")
#     args.append(theaSessionDir)
    if scn.get('thea_stopOnErrors') == False:
        args.append("-nostop")

#     args.append('-remoteserver')
#     args.append(str(scn.thea_SDKPort))


    scriptFile.close()
    saveScriptFile.close()
    thea_globals.log.debug(args)

    t2 = datetime.datetime.now()
    totalTime = t2-t1
    minutes = totalTime.seconds/60
    seconds = totalTime.seconds%60
    microseconds = totalTime.microseconds%1000000
    result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
    thea_globals.log.debug("Total export time: %s > %s sec" % (currentBlendFile, result))
    return args




def renderPreview(scene,):
    ''' Export material preview prepare ipt.thea script to load and render material preview

        :param scene: Blender scene
        :type scene: bpy_types.Scene
        :return: list with arguments to start Thea process
        :rtype: list
    '''
    global guiSets
    global scn, exportPath, command, tmpTheaRenderFile, outputImage, dataPath, theaPath

    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
    r = scene.render

    x= int(r.resolution_x*r.resolution_percentage*0.01)
    y= int(r.resolution_y*r.resolution_percentage*0.01)

    #print("+++++x,y: %s %s" % (x,y))


#     os.chdir(os.path.dirname(theaPath))
    import tempfile
    tempDir = tempfile.gettempdir()

    try:
        del exporter
    except:
        pass

    exporter = XMLExporter()

    theaPreviewFilename = False
    material = scene.objects['preview'].active_material

    outputImage = os.path.join(tempDir, "matPreview.bmp")


    matFilename = os.path.join(tempDir,'material_preview.xml')
    matFile = open(matFilename,"w")


    ma = ThMaterial()
    ma.setName("@Material@")
    ma.blenderMat = material
    previewScene = getTheaPreviewScenesMenuItems()[int(getattr(material, "thea_PreviewScenesMenu"))][1]+".scn.thea"
    if material:
        #print("thea_globals.previewScene: ", thea_globals.previewScene)
        #print("thea_PreviewScenesMenu: ", getattr(material, "thea_PreviewScenesMenu"), previewScene)
        if previewScene.startswith("Addon"):
        #if thea_globals.previewScene.startswith("Addon"):
            for path in bpy.utils.script_paths():
                scriptsDir = os.path.join(path,"addons","TheaForBlender")

                if material.preview_render_type == "FLAT":
                    pf = os.path.join(scriptsDir, "thea_preview_flat.scn.thea")
                if material.preview_render_type == "SPHERE":
                    pf = os.path.join(scriptsDir, "thea_preview_sphere.scn.thea")
                if material.preview_render_type == "CUBE":
                    pf = os.path.join(scriptsDir, "thea_preview_cube.scn.thea")
                if material.preview_render_type == "MONKEY":
                    pf = os.path.join(scriptsDir, "thea_preview_monkey.scn.thea")
                if os.path.exists(pf):
                    theaPreviewFilename = pf
        else:
            #theaPreviewFilename = thea_globals.previewScene
            theaPreviewFilename = getTheaPreviewScenesMenuItems()[int(getattr(material, "thea_PreviewScenesMenu"))][2]#+".scn.thea"


#         thea_globals.log.debug("theaPreviewFilename: %s" % theaPreviewFilename)

        if not theaPreviewFilename:
            return


        thMat = exporter.generateMaterialNew(ma)
        ma.write(matFile, preview=True)
    else:
        texFilename = scene.objects['texture'].active_material.active_texture.image.filepath
        mtexIndex = scene.objects['texture'].active_material.active_texture_index
        mtex = scene.objects['texture'].active_material.texture_slots[mtexIndex]

        ##print("texFilename: ",texFilename)


        tex = BitmapTexture(texFilename)
        if mtex.texture_coords == 'UV':
            tex.projection = "UV"
        if mtex.texture_coords == 'ORCO':
            if mtex.mapping == 'CUBE':
                tex.projection = "Cubic"
            if mtex.mapping == 'TUBE':
                tex.projection = "Cylindrical"
            if mtex.mapping == 'SPHERE':
                tex.projection = "Spherical"
            tex.offsetX = mtex.offset[0]
            tex.offsetY = mtex.offset[1]
            tex.scaleX = mtex.scale[0]
            tex.scaleY = mtex.scale[1]
            tex.brightness = bpy.data.textures[mtex.name].intensity
            tex.contrast = bpy.data.textures[mtex.name].contrast
            tex.saturation = bpy.data.textures[mtex.name].saturation
        bsdf = BasicBSDF()
        bsdf.setDiffuseTexture(BitmapTexture(texFilename))
        bsdf.setReflectanceTexture(RgbTexture(1,1,1))
        bsdf.setAbsorptionColor(RgbTexture(0,0,0))
        bsdf.setIndexOfRefraction(1.0)
        bsdf.setExtinctionCoefficient(0.0)
        bsdf.setRoughness(100.0)
        bsdf.setTraceReflections(False)

        thMat = ma.setBSDF(bsdf)
        ma.write(matFile)
        for path in bpy.utils.script_paths():
            scriptsDir = os.path.join(path,"addons","render_thea")
            pf = os.path.join(scriptsDir, "thea_preview_flat.scn.thea")
            if os.path.exists(pf):
                theaPreviewFilename = pf




    matFile.close()


    args = []
    camFilename = os.path.join(tempDir,'mat_preview_cam.xml')
    camFile = open(camFilename, "w")
    camFile.write('<Root Label="Kernel" Name="" Type="Kernel">\n\
                    <Object Identifier="./Scenes/direct" Label="Scene" Name="direct" Type="Scene">\n\
                    <Object Identifier="./Cameras/Camera" Label="Standard Camera" Name="Camera" Type="Camera">\n\
                    <Parameter Name="Focal Length (mm)" Type="Real" Value="85"/>\n\
                    <Parameter Name="Film Height (mm)" Type="Real" Value="32"/>\n\
                    <Parameter Name="Shift X (mm)" Type="Real" Value="0"/>\n\
                    <Parameter Name="Shift Y (mm)" Type="Real" Value="-0"/>\n\
                    <Parameter Name="Resolution" Type="String" Value="%sx%s"/>\n\
                    <Parameter Name="Frame" Type="Transform" Value="1 -2.6783e-09 7.39087e-09 0.0226645 -7.81677e-09 -0.238969 0.971027 -3.96692 -8.34513e-10 -0.971027 -0.238969 1.376 "/>\n\
                    <Parameter Name="Focus Distance" Type="Real" Value="1"/>\n\
                    <Parameter Name="Shutter Speed" Type="Real" Value="500"/>\n\
                    <Parameter Name="f-number" Type="String" Value="Pinhole"/>\n\
                    <Parameter Name="Depth of Field" Type="Real" Value="0.2"/>\n\
                    <Parameter Name="Blades" Type="Integer" Value="6"/>\n\
                    <Parameter Name="Diaphragm" Type="String" Value="Circular"/>\n\
                    <Parameter Name="Projection" Type="String" Value="Perspective"/>\n\
                    <Parameter Name="Auto-Focus" Type="Boolean" Value="0"/>\n\
                    <Parameter Name="DOF Lock" Type="Boolean" Value="0"/>\n\
                    <Parameter Name="Current View" Type="Boolean" Value="0"/>\n\
                    <Parameter Name="Roll Lock" Type="Boolean" Value="0"/>\n\
                    <Parameter Name="Upwards" Type="String" Value="0 0 1"/>\n\
                    <Parameter Name="Region" Type="String" Value=""/>\n\
                    <Parameter Name="Render Region" Type="Boolean" Value="0"/>\n\
                    </Object>\n\
                    </Object>\n\
                    </Root>' % (x,y))
    scriptFilename = os.path.join(tempDir,'mat_preview.ipt.thea')
    scriptFile = open(scriptFilename, "w")
    scriptFile.write('message \"Load ' + theaPreviewFilename + '\"\n')
    #if thea_globals.previewScene.startswith("Addon"):
    if previewScene.startswith("Addon"):
#        CHANGED Added add command for merge
        scriptFile.write('message \"Merge %s 0 0 2 0 0 \"\n' % camFilename )
    else:
        scriptFile.write('set \"./Scenes/Active/Cameras/Active/Resolution\" = \"%sx%s\"\n' % (x,y))
#    CHANGED > Added make active for better preview
#    scriptFile.write('message "./Scenes/Active/Cameras/Camera/Make Active\"\n')
    scriptFile.write('set "./Scenes/Active/Render/Interactive/Engine Core" = "Presto (MC)"\n')
    scriptFile.write('message \"LoadObject \'./Scenes/Active/Proxies/Appearance/@Material@\' \'%s\'\" \n' % matFilename)
    scriptFile.write('message "./UI/Viewport/Tweak Material"\n')
    if getattr(material, "thea_EnableUnbiasedPreview"):
    #if thea_globals.unbiasedPreview:
        scriptFile.write('message "Render"\n')

    args.append(str(theaPath))
    args.append(scriptFilename)
    args.append(outputImage)
#    thea_globals.log.debug("Arg outputImge mat preview: %s" % args)
    scriptFile.close()
    ##print (args)
    return args



def renderAnimation(scene):
    '''Render animation as sequence of single frame renders

        :param scene: Blender scene
        :type scene: bpy_types.Scene
    '''
    global scn
    global scriptFile, exportPath, firstFrame
    global exporter

    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
    firstFrame = True

    startFrame=scn.frame_start
    endFrame=scn.frame_end
    currFrame = scn.frame_current

    for frame in range(startFrame, endFrame+1, 1):
        #print ("\n\nRendering frame: ",frame)
        scn.frame_set(frame)
        args = renderFrame(scene,frame, anim=True)
        #print("\n\nStarting Thea....")
        p = subprocess.Popen(args)
        #print("Thea started. Frame rendering in progess...\n\n")
        p.wait()
    #print ("\n\nAnimation rendered")

    scn.frame_set(currFrame)

def initExporter():
    '''Use this function to init exporter instance
        :return: XMLExporter instance
        :rtype: thea_exporter.XMLExporter
    '''

    global guiSets


    isExporterInit = False
    exporter = XMLExporter()
    exporter.displayOptions=DisplayOptions()
    ro = RenderOptions()
    exporter.renderOptions = ro
    exporter.getRenderOptions().engine="Unbiased (TR1)"
    exporter.getRenderOptions().threads=4
    exporter.environmentOptions=EnvironmentOptions()
    exporter.environmentOptions.globalFrame=Transform()

    return exporter


def setExportPath(path):
    global exportPath
    scn.properties['TheaExportPath'] = path
    exportPath = path

def setTheaPath(path):
    global theaPath
    theaPath = path
    scn.properties['TheaBinaryPath'] = path
    getLocations()

def getMatTransTable():
    '''Get materials list from the materials LUT file

        :return: list of tuples with materials names and filepaths
        :rtype: [(str, str)]
    '''

    if len(thea_globals.matTransTable) > 0:
        return thea_globals.matTransTable
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass

    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    matTransTable = []
    try:
        ##print("bpy.context.scene.get('thea_materialsPath'): ", bpy.context.scene.get('thea_materialsPath'), os.path.dirname(bpy.context.scene.get('thea_materialsPath')))
        if bpy.context.scene.get('thea_materialsPath'):
            matTransFileName = os.path.join(os.path.dirname(bpy.context.scene.get('thea_materialsPath')), "BlenderTransTable.txt")
        else:
            matTransFileName = os.path.join(dataPath, "Materials", "BlenderTransTable.txt")
    except:
        matTransFileName = os.path.join(dataPath, "Materials", "BlenderTransTable.txt")

    ##print("matTransFileName: ", matTransFileName)


    if not matTransFileName:
        matTransFileName = os.path.join(dataPath, "Materials", "BlenderTransTable.txt")
    if os.path.exists(matTransFileName):
        trFile = open(matTransFileName, "r")
        i = 0
        for line in trFile:
            if i>1:
                ls = line.split(";")
                alreadyIn = False
                for matName,matPath in matTransTable:
                    if matName == ls[0]:
                        alreadyIn = True
                if not alreadyIn:
                    matTransTable.append((ls[0],ls[1].rstrip()))
            i+=1
        trFile.close()
    thea_globals.matTransTable = matTransTable
    return matTransTable


def getLocations(maxLines=1200):
    '''Get locations names and coordinates from locations.txt file

        :return: tuple with menu entries and list with locations.txt content required for mapping
        :rtype: ([(str,str,str)], [str])
    '''

    EnvLocationsMenuItems = []
    EnvLocationsArr = []

#     sceneLoaded = False
#     try:
#         if bpy.context.scene:
#             sceneLoaded = True
#     except:
#         pass
#
#     if sceneLoaded:
#         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene, verbose=True)
#     else:
#         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None, verbose=True)
#
#     if dataPath == "":
#         #print("---Can't find Thea data path!----")
    EnvLocationsMenuItems.append(("0","",""))
    EnvLocationsArr.append("")
#     else:
#         #print("dataPath: %s" % dataPath)
    #locPath = os.path.join(dataPath,"Locations","locations.txt")

    locPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locations.txt")
    try:
        file = open(locPath)
    except:
        file = False
    #print("locations file: ",locPath)
    if file:
        #print("locations found")
        l = 0
        for line in file:
            if l>0 and l<maxLines:
                EnvLocationsMenuItems.append((str(l-1),line[:34].strip(),""))
                EnvLocationsArr.append(line)
#                thea_globals.log.debug("Locations // Menuitems: %s - EnvLocArr: %s" % (EnvLocationsMenuItems, EnvLocationsArr))
            l+=1
    return (EnvLocationsMenuItems, EnvLocationsArr)

def getLocations2(maxLines=1250):
    '''Get locations names and coordinates from locations.txt file

        :return: tuple with menu entries and list with locations.txt content required for mapping
        :rtype: ([(str,str,str)], [str])
    '''

    EnvLocationsMenuItems = []
    EnvLocationsArr = []

    EnvLocationsMenuItems.append(("0","",""))
    EnvLocationsArr.append("")

    locPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locations.txt")
    try:
        file = open(locPath)
    except:
        file = False
    #print("locations file: ",locPath)
    if file:
        #print("locations found")
        l = 0
        it = iter(file)
        country = ["%UNITED STATES\n", "%CANADA\n"]
        for line in it:
            if line.isupper() and l>0:
                EnvLocCapitals = line.strip(" ").strip('\n')
                locCap = len(EnvLocCapitals)
                k = 0
                continue


            if line.isupper() ==0 and (line != "\n") and (line != country[1])>=0:
#                i+=1
                EnvLocationsArr.append(line)
#                thea_globals.log.debug("Locations: %s" % line)
#                EnvLocationsMenuItems.append((str(i),EnvLocCity, EnvLocCapitals))
                if line.isupper() and l>1:
                    continue
            l+=1

        file.close()
#        for line in file:
#            if l>0 and l<maxLines:
#                EnvLocationsMenuItems.append((str(l-1),line[:34].strip(),""))
#                EnvLocationsArr.append(line)
#            l+=1
    return EnvLocationsArr

def getLocMenu():
    '''Get locations names and coordinates from locations.txt file

        :return: tuple with menu entries and list with locations.txt content required for mapping
        :rtype: ([(str,str,str)], [str])
    '''

    EnvLocationsMenuItems = []
    EnvLocCapitals = []
    EnvLocCity = []
    country = []
    EnvLocationsMenuItems.append(("0","",""))

    locPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locations.txt")
    try:
        file = open(locPath)
    except:
        file = False

    i=0
    l = 0
    k = 0
    locCap = ""
    locCit = ""
    pattern='[a-z]'
    it = iter(file)
    for line in it:
        country = ["%UNITED STATES\n", "%CANADA\n"]
        if line.isupper() and (line != country[0]) and (line != country[1]):
#            EnvLocCapitals.append(line.strip(" "))
            EnvLocCapitals = line.strip(" ").strip('\n')
            locCap = len(EnvLocCapitals)
#            thea_globals.log.debug("Locations Capitals: %s" % EnvLocCapitals)
            k = 0
            continue
        l+=1

        if line.isupper() ==0 and (line != "\n") and (line != country[1])>=1:
            i+=1
            if line == "\n":
                i+=1
#                thea_globals.log.debug("Locations Extra: %s" % i)
#            EnvLocCity.append(line[:34].strip(" "))
            EnvLocCity = line[:34].strip(" ")
            locCit = line.strip(" ")
            EnvLocationsMenuItems.append((str(i),EnvLocCapitals +" - "+EnvLocCity, EnvLocCapitals))
#            thea_globals.log.debug("Locations Cities: %s + %s - %s" % (i,EnvLocCity, EnvLocCapitals ))
#            thea_globals.log.debug("Locations Cities: %s" % locCit)
#            thea_globals.log.debug("*** Cities: %s" % k)
#            thea_globals.log.debug("Locations: %s" % EnvLocationsMenuItems)
            if line.isupper() and l>0:
                continue
#                thea_globals.log.debug("Locations Cities: %s" % k)
        k+=1
    file.close()
    return EnvLocationsMenuItems

def defTheaGuiProperties():

    return 0

def getTheaPresets():
    '''Get menu entries with Thea render presets from Presets directory

        :return: list of tuples with menu entries
        :rtype: [(str, str, str)]
    '''

    presetsMenuItems = []
    presetsMenuItems.append(("0","None",""))

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass

    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    presets = []
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"Presets"))):
            presets.append((entry,os.path.join(dataPath,"Presets",entry)))
            presetsMenuItems.append((str(i),entry[:-4],""))
            i+=1
    if len(presetsMenuItems) == 1:
        presetsMenuItems.append(("1","Please install Thea Studio to use Render presets",""))
    return presetsMenuItems

def getPresets():
    '''Get Thea render presets from Presets directory

        :return: list of tuples with preset name and path
        :rtype: [(str, str)]
    '''

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass

    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    presets = []
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"Presets"))):
            presets.append((entry,os.path.join(dataPath,"Presets",entry)))
            i+=1
    return presets

lutMenuItems_store = []
def getLUT():
    '''Get menu entries with material from LUT file

        :return: list of tuples with menu entries
        :rtype: [(str, str, str)]
    '''
    thea_globals.log.debug("getLUT")

    lutMenuItems = []
    lutMenuItems.append(("0","None",""))
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    #print("sceneLoaded: ", sceneLoaded)
    matTransTable = getMatTransTable()

    i = 1
    maxid = 1
    id = 1
    found = False
    for tr in matTransTable:
        for idrec in lutMenuItems_store:
            id = idrec[0]
            if id > maxid:
                maxid = id
            if idrec[1] == str(i):
                found = True
                break
        if not found:
            lutMenuItems_store.append((maxid+1, str(i)))
#            items.append((mat.name, mat.name, mat.name))
#        items.append( (mat.name, mat.name, "", id) )
        lutMenuItems.append((str(i),tr[0],"",id))
        i+=1

    return lutMenuItems

def getLUTarray():
    '''get list with content of the LUT file

        :return: list with LUT file content
        :rtype: [str]
    '''

    lut = []
    lut.append((0,'None'))
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
    matTransTable = getMatTransTable()
    i = 1
    for tr in matTransTable:
        lut.append(tr[0])
        i+=1

#    thea_globals.log.debug("*** List LUT materials: %s" % lut)
    return lut



def getTheaCRF():
    '''get list with content of the CRF directory

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    crf = []
    crf.append((0,'None'))
    crfMenuItems = []
    crfMenuItems.append(("0","None",""))
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"crf"))):
            crf.append((entry,os.path.join(dataPath,"crf",entry)))
            crfMenuItems.append((str(i),entry[:-4],""))
            i+=1

    return crf

def getTheaCRFMenuItems():
    '''get list with menu items of the CRF directory

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    crfMenuItems = []
    crfMenuItems.append(("0","None",""))
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
    crf = []
    crf.append((0,'None'))
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"crf"))):
            crf.append((entry,os.path.join(dataPath,"crf",entry)))
            crfMenuItems.append((os.path.join(dataPath,"crf",entry),entry[:-4],""))
            i+=1
    else:
        crfMenuItems.append(("1","Please install Thea Studio to use CRF option",""))

    return crfMenuItems

def getTheaDisplayMenuItems():
    '''get list with menu items of the Display Presets directory

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    displayMenuItems = []
    displayMenuItems.append(("0","None",""))
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
    display = []
    display.append((0,'None'))
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"Displays"))):
            if entry.endswith('.xml') and not entry.startswith('.'):
                display.append((entry,os.path.join(dataPath,"Displays",entry)))
                displayMenuItems.append((os.path.join(dataPath,"Displays",entry),entry[:-4],""))
                i+=1
#        for entry in sorted(os.listdir(os.path.join(dataPath,"Displays"))):
#            display.append((entry,os.path.join(dataPath,"Displays",entry)))
#            displayMenuItems.append((os.path.join(dataPath,"Displays",entry),entry[:-4],""))
#            i+=1
    else:
        displayMenuItems.append(("1","Please install Thea Studio to use Display presets",""))

    return displayMenuItems


def getTheaIORMenuItems():
    '''get list with menu items of the IOR directory

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    iorMenuItems = []
    iorMenuItems.append(("0","None",""))
    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
    ior = []
    if len(dataPath ) > 5:
        i = 2
        for entry in sorted(os.listdir(os.path.join(dataPath,"ior"))):
            ior.append((entry,os.path.join(dataPath,"ior",entry)))
            iorMenuItems.append((str(i),entry[:-4],""))
            i+=1

    return iorMenuItems

def getTheaMediumMenuItems():
    '''get list with menu items of the medium directory

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    mediumMenuItems = []

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
    medium = []
    if len(dataPath ) > 5:
        i = 1
        for entry in sorted(os.listdir(os.path.join(dataPath,"med"))):
            medium.append((entry,os.path.join(dataPath,"med",entry)))
            mediumMenuItems.append((str(i),entry[:-4],""))
            i+=1
    else:
        mediumMenuItems.append(("0", "Please install Thea Studio to use medium files", ""))

    return mediumMenuItems

def getTheaPreviewScenesMenuItems():
    '''get list with menu items of the preview scenes

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''

    scenesMenuItems = []

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    searchPath = os.path.join(dataPath,"Scenes","MaterialEditor")
    scenes = []
    allfiles = []
    subfiles = []
    scenesMenuItems.append(("0", "Addon", "Addon"))
    for root, dirs, files in os.walk(searchPath):
        for f in files:
            if f.endswith('.scn.thea'):
                allfiles.append(os.path.join(root, f))
                if root != searchPath: # I'm in a subdirectory
                    subfiles.append(os.path.join(root, f))

    if len(subfiles) > 0:
        i = 1
        for entry in subfiles:
            scenes.append((entry,entry))
#            thea_globals.log.debug("entry: %s %s" % (entry, entry[:-9]))
            scenesMenuItems.append((str(i),os.path.basename(entry)[:-9],entry))
            i+=1
    else:
        scenesMenuItems.append(("1", "Please install Thea Studio to use Thea Studio preview scenes", ""))

#    thea_globals.log.debug("scenesMenuItems: %s" % scenesMenuItems)
    return scenesMenuItems


def getLocation(menuLine,EnvLocationsArr,scene):
    '''get lat, long and time zone for given location

        :param menuLine: Locations menu line number
        :type menuLine: int
        :param EnvLocationsArr: list with locations.txt file content
        :type EvnLocationsArr: [str]
        :param scene: Blender scene
        :type: bpy_types.Scene
        :return: tuple with loc, long and time zone
        :rtype: (str, str, str)
    '''
    if len(EnvLocationsArr) > 10:
        line = EnvLocationsArr[int(menuLine)] #CHANGED took out +1
        loc = line[34:]
        lat = loc[0:8].split("'")
        lat[1] = lat[1].strip(" ")
        latS = False
        longE = False
        long = []
        try:
           if lat[1] == "S":
              latS = True
           lat = lat[0].lstrip()
           lat = lat.replace(" ", ".")
           if latS:
               lat = eval(lat) * -1.0
           else:
               lat = eval(lat) * 1.0
           long = loc[12:21].split("'")
           long[1] = long[1].strip(" ")
#           thea_globals.log.debug("Long: %s" % long[1])
           if long[1] == "E":
               longE = True
           long = long[0].lstrip()
           long = long.replace(" ", ".")
           if longE:
               long = eval(long) * 1.0
           else:
               long = eval(long) * -1.0
        except:
           lat = 0
           long = 0

        try:
           TZ = str(eval(loc.split("'")[2][2:6]))
        except:
           TZ = 0
    else:
       lat = ""
       long = ""
       TZ = ""

    return (str(lat),str(long),str(TZ))



def startTheaRemoteServer(port, show=False):
    '''Start Thea Remote Server

        :param port: port to listen
        :type port: int
        :param show: show window with the Darkroom
        :type show: bool
        :return: process
    '''

    #print("os.getpid(): ", os.getpid())

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    sys.path.append(theaDir)
    ##print(sys.path)

    pArgs = []
    if os.name != "nt":
        pArgs.append("nohup")
    pArgs.append(theaPath)
    pArgs.append('-remoteserver')
    pArgs.append(str(port))
    if not show:
        pArgs.append('-hidden')
    pArgs.append('-nosplash')
    #print(pArgs)
    p = subprocess.Popen(pArgs)
    #print("Starting SDK on port: ", port)
    #time.sleep(1) #wait 1s to start process and then try to connect
    i = 0
    remoteServerReady = False
    while (not remoteServerReady) and (i<20):
        time.sleep(0.2)
        message = b'version'
        data = sendSocketMsg('localhost', port, message)
        #print("data: ",data)
        if data.find('v')>0:
            remoteServerReady = True
            i=20
        i+=1
    if remoteServerReady:
        #print("Started Thea remote server")
        return p
    else:
        #print("Thea remote server not started!")
        p.kill()
        return 0


def startTheaRemoteDarkroom(port, show=False, idletimeout=120):
    '''Start Thea Remote Dakroom

        :param port: port to listen
        :type port: int
        :param show: show window with the Darkroom
        :type show: bool
        :param idletimeout: timeout after process should exit when no new messages are sent
        :type idletimeout: int
        :return: process
    '''

    print("os.getpid(): ", os.getpid())

    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    sys.path.append(theaDir)
    #print(sys.path)

    pArgs = []
#     if os.name != "nt":
#         pArgs.append("nohup")
    #pArgs.append(theaPath)
    import platform
    if os.name == "nt":
        pArgs.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "WIN", "TheaRemoteDarkroom.exe"))
    if platform.system() == "Darwin":
        import stat
        darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OSX", "TheaRemoteDarkroom.app/Contents/MacOS/TheaRemoteDarkroom")
        os.chmod(darkroomfile, 0o755)
        pArgs.append(darkroomfile)
    if platform.system() == "Linux":
        import stat
        darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "LINUX", "TheaRemoteDarkroom")
        os.chmod(darkroomfile, 0o755)
        pArgs.append(darkroomfile)
#     pArgs.append("-load")
#     pArgs.append(" ")
#     pArgs.append("-exit")
    if not show:
        pArgs.append('-hidden')
    pArgs.append('-idletimeout')
    pArgs.append('-logging')
    pArgs.append(str(idletimeout))
    pArgs.append('-remoteserver')
    pArgs.append(str(port))

#     if not show:
#         pArgs.append('-hidden')
#     pArgs.append('-nosplash')
    print(pArgs)
    p = subprocess.Popen(pArgs)
    print("Starting SDK on port: ", port)
    #time.sleep(1) #wait 1s to start process and then try to connect
    i = 0
    remoteServerReady = False
    while (not remoteServerReady) and (i<20):
        time.sleep(0.1)
        message = b'version'
        data = sendSocketMsg('localhost', port, message)
        print("data: ",data)
        if data.find('v')>0:
            remoteServerReady = True
            i=20
        i+=1
    if remoteServerReady:
        print("Started Thea remote server")
        return p
    else:
        print("Thea remote server not started!")
        p.kill()
        return 0

def startTheaRemoteDarkroomNew(port, show=False, idletimeout=120):
    '''Start Thea Remote Dakroom - python version

        :param port: port to listen
        :type port: int
        :param show: show window with the Darkroom
        :type show: bool
        :param idletimeout: timeout after process should exit when no new messages are sent
        :type idletimeout: int
        :return: process
    '''

    #print("os.getpid(): ", os.getpid())


    sceneLoaded = False
    try:
        if bpy.context.scene:
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
    else:
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)

    sys.path.append(theaDir)
    ##print(sys.path)

    pArgs = []
#     if os.name != "nt":
#         pArgs.append("nohup")
    #pArgs.append(theaPath)


    #script = bpy.data.texts["/home/grzybu/blender/Thea/RemoteDarkroom/remotedarkroom/remotedarkroom.py"]
#     remoteDarkroomDir = "/home/grzybu/blender/Thea/RemoteDarkroom/remotedarkroom/"

    if platform.system() == "Linux":
        #script = os.path.join(remoteDarkroomDir, "remotedakroom.cpython-35.pyc")
        import stat
        darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "LINUX", "remotedarkroom")
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "LINUX"))
#         os.chmod(darkroomfile, stat.S_IEXEC)
        pArgs.append(darkroomfile)
        remoteDarkroomDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "LINUX")
        sys.path.append(remoteDarkroomDir)
        thea_globals.log.debug("path: %s" % sys.path)
    if platform.system() == "Darwin":
        #script = os.path.join(remoteDarkroomDir, "remotedakroom.cpython-34.pyc")
        import stat
        darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OSX", "TheaRemoteDarkroom.app/Contents/MacOS/TheaRemoteDarkroom")
        os.chmod(darkroomfile, stat.S_IEXEC)
        pArgs.append(darkroomfile)
    if platform.system() == "Windows":
        #script = os.path.join(remoteDarkroomDir, "remotedakroom.cpython-35.pyc")
        pArgs.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "WIN", "TheaRemoteDarkroom.exe"))

#     exec(script.as_string())
#     sys.argv = ['', '-remoteserver', str(port), '-d']
#     runpy.run_path(script, run_name='__main__')
#     return
#     import platform
#     if os.name == "nt":
#         pArgs.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "WIN", "TheaRemoteDarkroom.exe"))
#
#     if platform.system() == "Darwin":
#         import stat
#         darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "OSX", "TheaRemoteDarkroom.app/Contents/MacOS/TheaRemoteDarkroom")
#         os.chmod(darkroomfile, stat.S_IEXEC)
#         pArgs.append(darkroomfile)
#     if platform.system() == "Linux":
#         import stat
# #         darkroomfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "LINUX", "TheaRemoteDarkroom")
#     if platform.system() == "Darwin":
#         python_exec = "python3"
#     else:
#         python_exec = bpy.app.binary_path_python
# #         os.chmod(darkroomfile, stat.S_IEXEC)
#     pArgs.append(python_exec)
#     pArgs.append(script)
#     pArgs.append("-load")
#     pArgs.append(" ")
#     pArgs.append("-exit")
#     if not show:
    pArgs.append('-hidden')
    pArgs.append('-idletimeout')
    pArgs.append(str(idletimeout))
    pArgs.append('-remoteserver')
    pArgs.append(str(port))
    pArgs.append('-i')
#     pArgs.append('-v')
    logfile = os.path.join(tempfile.tempdir, 'remotedarkroom.log')
    #print("logfile: ", logfile)
    pArgs.append('-o')
    pArgs.append(logfile)

#     if not show:
#         pArgs.append('-hidden')
#     pArgs.append('-nosplash')
    #print(pArgs)
    thea_globals.log.debug("pArgs: %s" % pArgs)
    p = subprocess.Popen(pArgs)
    thea_globals.log.debug("p: %s", p)
    #print("Starting SDK on port: ", port)
    #time.sleep(1) #wait 1s to start process and then try to connect
    i = 0
    remoteServerReady = False
    while (not remoteServerReady) and (i<20):
        time.sleep(0.1)
        message = b'version'
        data = sendSocketMsg('localhost', port, message)
        #print("data: ",data)
        if data.find('v')>0:
            remoteServerReady = True
            i=20
        i+=1
    if remoteServerReady:
        #print("Started Thea remote server")
        return p
    else:
        #print("Thea remote server not started!")
        p.kill()
        return 0

def updateDisplaySettings(port):
    '''Send set of messages to remotedakroom to refresh display settings

        :param port: port
        :type port: int
    '''
    message = 'set "./Scenes/Active/Display/ISO" = "%s"' % getattr(bpy.context.scene, 'thea_DispISO')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Shutter Speed" = "%s"' % getattr(bpy.context.scene, 'thea_DispShutter')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/f-number" = "%s"' % getattr(bpy.context.scene, 'thea_DispFNumber')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Gamma" = "%s"' % getattr(bpy.context.scene, 'thea_DispGamma')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Brightness" = "%s"' % getattr(bpy.context.scene, 'thea_DispBrightness')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Filter" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispSharpness') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Sharpness Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispSharpnessWeight', 50) / 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Burn" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispBurn') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Burn Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispBurnWeight', 10) / 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Vignetting" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispVignetting') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Vignetting Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispVignettingWeight', 20) / 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Chroma" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispChroma') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Chroma Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispChromaWeight', 0) / 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Contrast" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispContrast') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Contrast Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispContrastWeight', 0) / 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Balance" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispTemperature') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Temperature" = "%s"' % getattr(bpy.context.scene, 'thea_DispTemperatureWeight')
    data = sendSocketMsg('localhost', port, message.encode())
#   CHANGED > added dropdownlist Glare / Bloom effect
    message = 'set "./Scenes/Active/Display/Bloom" = "%s"' % ('1' if getattr(bpy.context.scene, 'thea_DispBloom') else '0')
    data = sendSocketMsg('localhost', port, message.encode())
    if getattr(bpy.context.scene, 'thea_DispBloomItems') != "0":
        message = 'set "./Scenes/Active/Display/Glare" = "1"'
        data = sendSocketMsg('localhost', port, message.encode())
        message = 'set "./Scenes/Active/Display/Glare Blades" = "%s"' % getattr(bpy.context.scene, 'thea_DispBloomItems')
        data = sendSocketMsg('localhost', port, message.encode())
    else:
        message = 'set "./Scenes/Active/Display/Glare" = "0"'
        data = sendSocketMsg('localhost', port, message.encode())

    message = 'set "./Scenes/Active/Display/Bloom Weight" = "%s"' % (getattr(bpy.context.scene, 'thea_DispBloomWeight', 20)/ 100)
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Bloom Radius" = "%s"' % getattr(bpy.context.scene, 'thea_DispGlareRadius')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Min Z (m)" = "%s"' % getattr(bpy.context.scene, 'thea_DispMinZ')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Max Z (m)" = "%s"' % getattr(bpy.context.scene, 'thea_DispMaxZ')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/False Color" = "%s"' % getattr(bpy.context.scene, 'thea_analysisMenu')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Min Il-Lum" = "%s"' % getattr(bpy.context.scene, 'thea_minIlLum')
    data = sendSocketMsg('localhost', port, message.encode())
    message = 'set "./Scenes/Active/Display/Max Il-Lum" = "%s"' % getattr(bpy.context.scene, 'thea_maxIlLum')
    data = sendSocketMsg('localhost', port, message.encode())
    crf = getTheaCRF()
    #print("getattr(bpy.context.scene, 'thea_DispCRFMenu'): ", getattr(bpy.context.scene, 'thea_DispCRFMenu'))
    if getattr(bpy.context.scene, 'thea_DispCRFMenu') != "0":
        message = 'set "./Scenes/Active/Display/Enable CRF" = "1"'
        data = sendSocketMsg('localhost', port, message.encode())
        message = 'set "./Scenes/Active/Display/CRF File" = "%s"' % getattr(bpy.context.scene, 'thea_DispCRFMenu')
        data = sendSocketMsg('localhost', port, message.encode())
    else:
        message = 'set "./Scenes/Active/Display/Enable CRF" = "0"'
        data = sendSocketMsg('localhost', port, message.encode())

    time.sleep(0.1)

def checkTheaMaterials(): #check if any Thea material was modified by the user
    '''check if any Thea material was modified by the user

        :return: True if modified
        :rtype: bool
    '''
    modified = False
    for mat in bpy.data.materials:
        for key in mat.keys():
            if key.startswith("thea_"):
                modified = True
                return modified
    return modified


def checkTheaExtMat():
    '''check if Thea linked materials are live
        :return: False if missing link
        :rtype: bool
    '''
    missing_Materials = []
    matNameExt = ""
    matMesh = ""
    matExtLink = True
    for mat in bpy.data.materials:
        if getattr(mat, "thea_extMat"):
            extMat = os.path.exists(os.path.abspath(bpy.path.abspath(mat.get('thea_extMat'))))
            if extMat == False:
#                matMesh = bpy.context.active_object.name
                matExtLink = False
                matNameExt = mat.name
                MNAME = matNameExt
                obs = []
                for o in bpy.data.objects:
                    if isinstance(o.data, bpy.types.Mesh) and MNAME in o.data.materials:
#                        obs.append(o.name)
                        matMesh = o.name
                missing_Materials.append("%s > Mesh obj: %s" % (matNameExt, matMesh))
#                return [matExtLink, matNameExt, matMesh]
            else:
                pass
        missing_Materials = sorted(list(set(missing_Materials)))
#    thea_globals.log.debug("*** Missing Material list: %s" % missing_Materials)
    return [matExtLink, matNameExt, matMesh, missing_Materials]

def updateActiveMaterialColor():
    '''Update active material diffuse color using color values from center of the embeded material preview
    '''
    import tempfile
    material = bpy.context.scene.objects.active.active_material
    extMatFile = False
    extIBLFile = True
    scene = bpy.context.scene
    #print("material name: ", material.name)
    if material:
        try:
            materialName, foo = material.name.split(".") # very bad workaround because preview scene adds .00x to material names
        except:
            materialName = material.name

    #if getattr(scene, 'thea_useLUT'):
#             if thea_globals.getUseLUT():
#             if getattr(scene, "thea_useLUT"):
    if int(getattr(material, 'thea_LUT', 0)) > 0:
        matTransTable = getMatTransTable()
        lut = getLUTarray()
        i = 0
#                 #print("matTransTable: ", matTransTable)
        for trMat in matTransTable:
            i+=1
            try:
                trFileName = trMat[1].replace("$", ":")
                foo, trFileName = trFileName.split("::/")
                matIndex = i
                matName = trMat[0]
            except:
                trFileName = trMat[1]
                matIndex = i
                matName = trMat[0]

#            trFileName = os.path.join(dataPath, trFileName)
            trFileName = os.path.join(scene.thea_materialsPath, trFileName)
            try:
                if thea_globals.getNameBasedLUT():
                    if trMat[0] == materialName and (os.path.exists(trFileName)):
                        extMatFile = trFileName
                else:
                    if trMat[0] == lut[material.get('thea_LUT')] and (os.path.exists(trFileName)):
                        extMatFile = trFileName
                    ##print("trMat[0], matName: ", trMat[0], matName)
            except:
                pass
    if not extMatFile:
        try:
            extMatFile = os.path.abspath(bpy.path.abspath(material['thea_extMat']))
        except:
            extMatFile = False

#             #print("extMatFile: ", extMatFile)
    if extMatFile:
        prevImageOb = Preview()
        tempDir = tempfile.gettempdir()
        outputImage = os.path.join(tempDir, "matPreview.bmp")
        thea_globals.log.debug("TempDIr Preview: %s" % tempDir)
        prevImageOb.outFile = outputImage
        prevImageOb.read(extMatFile)
        setattr(material, 'diffuse_color', prevImageOb.centerColor)
#    if extIBLFile:
#        prevImageOb = Preview()
#        tempDir = tempfile.gettempdir()
#        outputImage = os.path.join(tempDir, "matIBLPreview.bmp")
#        thea_globals.log.debug("TempDIr Preview: %s" % tempDir)
#        prevImageOb.outFile = outputImage
#        prevImageOb.read("/Users/romboutversluijs/Library/Application Support/Thea Render/Skies/HDR Haven/Skies/Rustig Koppie_8k_0deg_Toned-v1.sky.thea")
#        setattr(material, 'diffuse_color', prevImageOb.centerColor)
    return


class TheaRender(bpy.types.RenderEngine):
    '''Main class for rendering scene or material preview
    '''
    bl_idname = 'THEA_RENDER'
    bl_label = "Thea Render"
    bl_use_preview = True
    DELAY = 1



    def _render(self):
       global theaPath, scn, selectedObjects

       #print("-- Starting Thea --")

    def render(self, scene):
        #                                    CHANGED > added variable ImgTheaRenderFile
        global exporter, tmpTheaRenderFile, imgTheaRenderFile, scn, outputImage, selectedObjects, dataPath, materialUpdated

        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)


        if scene.name != "preview":
            if len(currentBlendFile)<2:
                self.report({'ERROR'}, "Please save the scene before exporting!")
                return {'FINISHED'}
            if(checkTheaMaterials()==False):
                self.report({'ERROR'}, "Please set materials and lights to get proper render")
                #return {'FINISHED'}
            if (checkTheaExtMat()==False):
                self.report({'ERROR'}, "Please check linked materials")
#            thea_globals.log.debug("*** CheckMaterials = %s ***" % checkTheaExtMat())
                return {'FINISHED'}
            if not os.path.isdir(exportPath):
                self.report({'ERROR'}, "Please set proper output path before exporting!")
                return {'FINISHED'}
            checkTheaExtMat()
            valuesExt = checkTheaExtMat()
            if (valuesExt[0]==False):
    #            self.report({'ERROR'}, "Please link Material: %s > Object: %s" % (valuesExt[1], valuesExt[2]))
                missing_Mat = ""
                for mat in valuesExt[3]:
                    missing_Mat = missing_Mat+"\n"+mat
                self.report({'ERROR'}, "Please link Material:%s" % missing_Mat)
    #            thea_globals.log.debug("*** CheckMaterials = %s ***" % valuesExt[1])
                return {'FINISHED'}

        calculatePreview = True
        previewGeneratorPort = 30001
        renderInProgress = False

        r = scene.render
        material = False
        #return


        # compute resolution
        x= int(r.resolution_x*r.resolution_percentage*0.01)
        y= int(r.resolution_y*r.resolution_percentage*0.01)

#        # calculate region render image size NOT USED NO MORE
#        if scene.thea_regionRender:
#            if scene.thea_regionSettings == "1":
#                x = x/2
#                y = y/2
#            if scene.thea_regionSettings == "2":
#                x = x/3
#                y = y/3
#            if scene.thea_regionSettings == "3":
#                x = x/4
#                y = y/4
#            if scene.thea_regionSettings == "4":
#                x = x/8
#                y = y/8


        if (x<=80) or (y<=80):
            return

        def update_image(image, layer, sx, sy, x, y):
            thea_globals.log.debug("update image: %s, %s, %s, %s" %(sx, sy, x, y))
            #print("update image: ", sx, sy, x, y)
            result = self.begin_result(sx, sy, x, y)
            lay = result.layers[layer]
            #time.sleep(0.1)
            try:
                lay.load_from_file(image)
            except:
                pass
            self.end_result(result)



        scn = scene
        renderStartTime = os.times()[4]
        self.update_stats("", "THEA: Exporting data from Blender")
        thea_globals.materialUpdated = True
        if thea_globals.materialUpdatesNumber<10:
            thea_globals.materialUpdatesNumber += 4
        #print(scene, scene.frame_current)
        #print
        if scene.name == "preview":
            #print("\n\n**Material preview**\n\n")
            material = getattr(scene.objects['preview'], 'active_material', False)

            extMatFile = False
            ##print("material name: ", material.name)
            if material:
                try:
                    materialName, foo = material.name.split(".") # very bad workaround because preview scene adds .00x to material names
                except:
                    materialName = material.name

            #if getattr(scene, 'thea_useLUT'):
#            thea_globals.log.debug("thea_globals.useLUT: %s %s" % (thea_globals.useLUT, getattr(scene, "thea_useLUT")))
            #print("scenes: ", bpy.data.scenes)
#             if thea_globals.getUseLUT():
#             if getattr(scene, "thea_useLUT"):
            if int(getattr(material, 'thea_LUT', 0)) > 0:
                matTransTable = getMatTransTable()
                lut = getLUTarray()
#                 #print("matTransTable: ", matTransTable)
                for trMat in matTransTable:
                    try:
                        trFileName = trMat[1].replace("$", ":")
                        foo, trFileName = trFileName.split("::/")
                    except:
                        trFileName = trMat[1]

                    trFileName = os.path.join(dataPath, trFileName)
                    try:
                        if thea_globals.getNameBasedLUT():
                            if trMat[0] == materialName and (os.path.exists(trFileName)):
                                extMatFile = trFileName
                        else:
                            if trMat[0] == lut[material.get('thea_LUT')] and (os.path.exists(trFileName)):
                                extMatFile = trFileName
                            ##print("trMat[0], matName: ", trMat[0], matName)
                    except:
                        pass

            if not extMatFile:
                try:
                    extMatFile = os.path.abspath(bpy.path.abspath(material['thea_extMat']))
                except:
                    extMatFile = False

#             #print("extMatFile: ", extMatFile)
            if extMatFile:
                import tempfile
                prevImageOb = Preview()
                tempDir = tempfile.gettempdir()
                outputImage = os.path.join(tempDir, "matPreview.bmp")
                ##print("outputImage: ", outputImage)
                prevImageOb.outFile = outputImage
                #print()
                prevImageOb.read(extMatFile)
                px = prevImageOb.getLines()
                py = prevImageOb.getPixels()
                if x >= px:
                    sx = int((x-px)/2)
                else:
                    sx = 0
                if y >= py:
                    sy = int((y-py)/2)
                else:
                    sy = 0
                #print("sx, sy, px, py ", sx, sy, px, py, x, y)
                update_image(outputImage, 0, sx, sy, px, py)
                thea_globals.materialUpdated = True


            elif calculatePreview:

                if material:
                    args = renderPreview(scene)
                    ##print("args: ", args)
                    socketServerIsRunning = False
                    #from . import thea_globals

                    ##print("thea_globals.IrIsRunning: ", thea_globals.IrIsRunning)
                    if False:#thea_globals.IrIsRunning:
                        thea_globals.log.warning("Interactive rendering is running. Material preview rendering is disabled!")
                        self.report({'ERROR'}, "Interactive rendering is running. Material preview rendering is disabled!")
                    else:

                        message = b'version'
                        data = sendSocketMsg('localhost', previewGeneratorPort, message)
                        #print('SDK reply', repr(data))
                        if data.find('v')>0:
                            socketServerIsRunning = True
                        else:
                            startTheaRemoteDarkroom(previewGeneratorPort, show=False, idletimeout=25)
                            message = b'version'
                            data = sendSocketMsg('localhost', previewGeneratorPort, message)
                            if data.find('v')>0:
                                socketServerIsRunning = True


                        #print("socketServerIsRunning: ", socketServerIsRunning)

                        if socketServerIsRunning:
#                             message = b'message "Reset"'
#                             data = sendSocketMsg('localhost', previewGeneratorPort, message)
                            message = 'message "./UI/Viewport/Theme/RW_PROG"'
                            data = sendSocketMsg('localhost', previewGeneratorPort, message.encode())
                            fileName = args[1]
                            if os.path.exists(fileName):
                                trFile = open(fileName, "r")
                                i = 0
                                for line in trFile:
                                    ##print("message: ", line)
                                    message = bytes(line.rstrip('\n'), 'UTF-8')
                                    data = sendSocketMsg('localhost', previewGeneratorPort, message)
                                    ##print('SDK reply', repr(data))
                                outputImage = args[2]
                                ##print("outputImage: ", outputImage)
                                #if thea_globals.unbiasedPreview == False:
                                #Doesnt make sense to render from camera frame using Unbiased preview
                                if getattr(material, "thea_EnableUnbiasedPreview") == False:
                                    #switch to camera frame
                                    message = b'message "./UI/Viewport/Theme/RW_CMFR"'
                                else:
                                    message = b'message "Render"'
                                data = sendSocketMsg('localhost', previewGeneratorPort, message)
                                #print("message: ",message)
                                #print("out: ", data)
                                #set resolution
                                message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (x,y)
                                #print("message: ",message)
                                data = sendSocketMsg('localhost', previewGeneratorPort, message.encode())
                                #print("out: ", data)
                                if thea_globals.unbiasedPreview == False:
                                    #start auto refresh IR
                                    message = b'message "./UI/Viewport/Theme/RW_EARF"'
                                    data = sendSocketMsg('localhost', previewGeneratorPort, message)
                                    #print("message: ",message)
                                    #print("out: ", data, data.find('Ok'))
                                if data.find('Ok')>-1:
                                    #print("\n\n***Material preview render started!****\n\n")
                                    time.sleep(0.5)
                                    i=0
                                    while i<20:
                                        #if thea_globals.unbiasedPreview == False:
                                        if getattr(material, "thea_EnableUnbiasedPreview") == False:
                                            message = 'message "./UI/Viewport/SaveImage %s"' % outputImage
                                        else:
                                            message = 'message "SaveImage %s"' % outputImage
                                        data = sendSocketMsg('localhost', previewGeneratorPort, message.encode())
                                        #print("i: ",i," message: ",message)
                                        #print("img save data: ", data)
                                        #print("data.find('Ok'): ", data.find('Ok'))
                                        if data.find('Ok')>0:
                                            update_image(outputImage, 0, 0, 0, x, y);
                                        if self.test_break():
                                            ##print("message: ",message)
                                            message = 'message "./UI/Viewport/Theme/RW_PROG"'
                                            data = sendSocketMsg('localhost', previewGeneratorPort, message.encode())
                                            ##print("data: ", data)
                                            #break
                                            return
                                        i+=1
                                        time.sleep(0.2)
                                    message = 'message "./UI/Viewport/Theme/RW_PROG"'
                                    #print("message: ",message)
                                    data = sendSocketMsg('localhost', previewGeneratorPort, message.encode())
                                    thea_globals.materialUpdated = False
                                    ##print("message: ",message)
                                    ##print("data: ", data)
                                    #print("\n\n***Material preview render finished!****\n\n")
                                    #time.sleep(10)
                                    message = b'message "exit"'
                                    data = sendSocketMsg('localhost', previewGeneratorPort, message)
#                                     #print("message: ",message)
#                                     #print("data: ", data)
                else:
                    texFilename = scene.objects['texture'].active_material.active_texture.image.filepath
                    if os.path.exists(os.path.abspath(bpy.path.abspath(texFilename))):
                        x = scene.objects['texture'].active_material.active_texture.image.size[0]
                        y = scene.objects['texture'].active_material.active_texture.image.size[1]
                        #print("x, y: ", x, y)
                        update_image(os.path.abspath(bpy.path.abspath(texFilename)), 0, 0, 0, x, y);


        else:
            #bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
            if thea_globals.IrIsRunning:
                thea_globals.log.info("IR is running. Stopping it before production render")
                message = b'version'
                data = sendSocketMsg('localhost', scene.thea_SDKPort, message)
                #print("message, data", message, data)
                #print('SDK reply', repr(data))
                if data.find('v')>0:
                    socketServerIsRunning = True
                if data.find('v'):
                    message = b'message "./UI/Viewport/Theme/RW_PROG"'
                    data = sendSocketMsg('localhost', scene.thea_SDKPort, message)
                    #print("message, data", message, data)
                    message = b'message "exit"'
                    data = sendSocketMsg('localhost', scene.thea_SDKPort, message)
                    #print("message, data", message, data)
                    thea_globals.IrIsRunning = False
                    scene.thea_ir_running = False

            port = scene.thea_SDKPort+2
            args = renderFrame(scene, scene.frame_current)
            show = False if args[2] == '-hidden' else True
            #print("show: ", show)
            message = b'version'
            data = sendSocketMsg('localhost', port, message)
            #print('SDK reply', repr(data))
            if data.find('v')>0:
                socketServerIsRunning = True
            else:
                startTheaRemoteDarkroom(port, show=show, idletimeout=getattr(scene, 'thea_IRIdleTimeout', 120))
                time.sleep(1)
                message = b'version'
                data = sendSocketMsg('localhost', port, message)

                if data.find('v')>0:
                    socketServerIsRunning = True


            #print("socketServerIsRunning: ", socketServerIsRunning)
            #execute command from first ipt.thea file to prepare rendering
            if socketServerIsRunning:
#                 message = b'message "Reset"'
#                 data = sendSocketMsg('localhost', port, message)
                fileName = args[0]
                if os.path.exists(fileName):
                    trFile = open(fileName, "r")
                    i = 0
                    for line in trFile:
                        #print("message: ", line)
                        message = bytes(line.rstrip('\n'), 'UTF-8')
                        data = sendSocketMsg('localhost', port, message)


            message = b'Render'
            data = sendSocketMsg('localhost', port, message)
#            if (data=="Warning:"):
#             sys.path.append(theaDir)
            #sys.path.append(theaDir+"/Plugins/Presto")
            ##print(sys.path)
#             self.p = subprocess.Popen(args)
        #tmpTheaRenderFile = os.path.join(dataPath, "Temp", "temp.png")
        #tmpTheaRenderFile = os.path.join(os.path.dirname(bpy.data.filepath),"temp.png")
        #tmpTheaRenderFile = os.path.join(os.path.join(dataPath, "Temp"),"temp.png")
        tmpTheaRenderFile = os.path.join(os.path.join(exportPath, "~thexport"),"temp.png")
        tmpTheaRenderChannel = os.path.join(os.path.join(exportPath, "~thexport"),"temp_channel.png")
#       CHANGED > added save 'temp.img.thea' variable
        imgTheaRenderFile = os.path.join(os.path.join(exportPath, "~thexport"),"temp.img.thea")
        #tmpTheaRenderFile = os.path.join(dataPath, "temp.png")



        #print ("tmpTheaRenderFile: ",tmpTheaRenderFile)
        if os.path.exists(tmpTheaRenderFile):
            os.remove(tmpTheaRenderFile)
        if scene.name != "preview":
            self.update_stats("", "THEA: Rendering...")

        prev_size = -1
        lastTime = time.time()#os.times()[4]
        saveImageTime = 1
        i = 0
        if scene.name != "preview":
            while True:
               time.sleep(self.DELAY)
               if scene.name != "preview":
                   thea_globals.log.debug("Rendering ...")
                   ##print(saveImageTime, (os.times()[4]-lastTime))
                   ##print("scene.thea_RenderRefreshResult: ", scene.thea_RenderRefreshResult)
                   ##print("os.times()[4], lastTime: ", time.time(), os.times(), os.times()[4], lastTime, os.times()[4]-lastTime, saveImageTime)
                   if scene.thea_RenderRefreshResult:
                       message = b'status'
                       status = sendSocketMsg('localhost', port, message)
                       thea_globals.log.debug("status: %s %s" % (status, status.find('Idle')))
                       if status.find('ERROR')>=0:
                           self.report({'ERROR'}, "Something went wrong while rendering!")
                           self.update_stats("", "THEA: Something went wrong while rendering!")
                           thea_globals.log.critical('Something went wrong while rendering!')
                           break
                       #if rendering is finished execute command from second file with saveimage commands
                       if status.find('Idle')>=0:
                            self.update_stats(status, "THEA: Saving output images " )
                            fileName = args[1]
                            if os.path.exists(fileName):
                                trFile = open(fileName, "r", encoding='UTF-8')
                                i = 0
                                for line in trFile:
                                    message = bytes(line.rstrip('\n'), 'utf-8')
#                                   CHANGED > move data = sendSocket.... to top, channels and image where not loadded into Blender else
                                    data = sendSocketMsg('localhost', port, message)
                                    thea_globals.log.debug("save: %s" % message)
                                    # try to find messages saving channels and if found create or reload image with channel
                                    if (line.find("SaveChannel") > 0) and (line.find("~thexport")>0):
                                        channelName = ""
                                        channelFile = ""
                                        if line.find("'")>0:
                                            channelName = line.split("'")[1]
                                            channelFile = line.split("'")[2].lstrip(" ").replace("\"", "").rstrip()
                                        else:
                                            channelName = line.split(" ")[2]
                                            channelFile = line.split(" ")[3].replace("\"", "").rstrip()
#                                       CHANGED > Added saving output channel to to send to blender
                                        thea_globals.log.debug("Channel MaskList %s" % channelFile)
                                        self.update_stats(status, "Saving: " + channelName + " channel")
                                        img = None
                                        img = bpy.data.images.get("Channel %s" % channelName)
                                        if img == None:
                                            try:
                                                img = bpy.data.images.load(channelFile)
                                                img.name = "Channel %s" % channelName
                                            except:
                                                img = None
#                                        CHANGED> Added reload, new renders wont reload otherwise
                                        try:
                                            img = bpy.data.images["Channel %s" % channelName].reload()
                                        except:
                                            img = None

                                    if (line.find("SaveImage") > 0) or (line.find("SaveLayeredImage") > 0):
                                        message = 'message "SaveImage %s"' % tmpTheaRenderFile
                                        data = sendSocketMsg('localhost', port, message.encode())
                                        update_image(tmpTheaRenderFile, 0, 0, 0, x, y);
#                                       CHANGED > Redid stripping. scnes with spaces would get loaded otherwise
                                        imageFile = line.replace("message \"SaveImage ","").replace("\"", "").rstrip()
#                                        imageFile = line.split(" ")[2].replace("\"", "").rstrip()
                                        img = None
                                        img = bpy.data.images.get("TheaRenderResult")
                                        thea_globals.log.debug("ThearenderResult Imagea: %s" % imageFile)
                                        if img == None:
                                            try:
                                                img = bpy.data.images.load(imageFile)
                                                img.name = "TheaRenderResult"
                                                thea_globals.log.debug("ThearenderResult Imagea: %s" % imageFile)
                                            except:
                                                img = None
#                                       CHANGED> Added reload, new renders wont reload otherwise
                                        img = bpy.data.images["TheaRenderResult"].reload()

                                    data = sendSocketMsg('localhost', port, message)
#                             update_image(outputImage, 0, 0, 0, x, y);

                            data = sendSocketMsg('localhost', port, b'exit')
                            self.update_stats("", "THEA: Rendering finished")
                            thea_globals.log.critical('Rendering finished!')
#                             #print("final update")
#                             update_image("/tmp/text.exr", 0, 0, 0, x, y);
                            break
                       else:
                           message = b'status'
                           data = sendSocketMsg('localhost', port, message)
                           status = ''.join(filter(lambda x:x in string.printable, data))
                           thea_globals.log.debug("status: %s" % status)
                           self.update_stats(status, "THEA: Rendering " )
                           #print("thea_globals.displayUpdated: ", thea_globals.displayUpdated)
                           if thea_globals.displayUpdated:
                               updateDisplaySettings(port)
                               thea_globals.displayUpdated = False
                               time1 = time.time()#os.times()[4]
#                               message = 'message "SaveImage %s"' % tmpTheaRenderFile
                               thea_globals.log.debug("View Channel: %s" % getattr(scene, "thea_viewChannel", 0).replace("_"," "))
                               if getattr(scene, "thea_viewChannel", 0).replace("_"," ") == "Color":
                                   message = 'message "SaveImage %s"' % tmpTheaRenderFile
                                   data = sendSocketMsg('localhost', port, message.encode())
                               else:
                                   message = 'message "SaveChannel '+ "'" + getattr(scene, "thea_viewChannel", 0).replace("_"," ") + "'"+' %s"' % tmpTheaRenderFile
                                   data = sendSocketMsg('localhost', port, message.encode())
#                              CHANGED > Added update status temp render file
                               self.update_stats(status, "Updating temp file: " + tmpTheaRenderFile)
                               data = sendSocketMsg('localhost', port, message.encode())
                               time2 = time.time()
                               if (time2-time1)<1:
                                   saveImageTime = 1
                               else:
                                   saveImageTime = time2-time1
                               if data.find('Ok')>-1:
                                   update_image(tmpTheaRenderFile, 0, 0, 0, x, y);
                                   lastTime = time.time()#os.times()[4]
                           #print("saveImageTime", saveImageTime, (time.time()-lastTime))
                           if saveImageTime>0 and (time.time()-lastTime)>saveImageTime*5:
                               #self.DELAY = 10*saveImageTime
                               message = b'version'
                               data = sendSocketMsg('localhost', port, message)

                               if data.find('v')>0:
                                   time1 = time.time()#os.times()[4]
                                   if getattr(scene, "thea_viewChannel", 0).replace("_"," ")  == "Color":
                                       message = 'message "SaveImage %s"' % tmpTheaRenderFile
                                       data = sendSocketMsg('localhost', port, message.encode())
                                   else:
                                       message = 'message "SaveChannel '+ "'" + getattr(scene, "thea_viewChannel", 0).replace("_"," ") + "'"+' %s"' % tmpTheaRenderFile
                                       data = sendSocketMsg('localhost', port, message.encode())
                                   #print("message, data: ", message, data)
                                   time2 = time.time()#os.times()[4]
                                   if (time2-time1)<1:
                                       saveImageTime = 1
                                   else:
                                       saveImageTime = time2-time1
                                   if data.find('Ok')>-1:
                                       update_image(tmpTheaRenderFile, 0, 0, 0, x, y);
                                       lastTime = time.time()#os.times()[4]
                                   if data.find('Ok')>-1:
                                       update_image(tmpTheaRenderFile, 0, 0, 0, x, y);
                                       lastTime = time.time()#os.times()[4]

#                try:
# #                    if self.p.poll() != None:
#                    #print("Final output update")
#                    update_image(outputImage, 0, 0, 0, x, y);
#                    break
#                except:
#                    pass

               # user exit
               if self.test_break():
                   try:
                        message = b'exit'
                        data = sendSocketMsg('localhost', port, message)
                        self.p.terminate()
                   except:
                        pass
                   break

        #print("Rendering finished")




class mainExporter:
    '''Instance of this class is used to prepare logger on import
    '''

    def run(self):
        '''Prepare the loger in thea_globals
        '''

        import os
        import logging
        from logging import handlers
        import tempfile

        thea_globals.log = logging.getLogger('TheaForBlender')
        thea_globals.fh = logging.handlers.RotatingFileHandler(filename=os.path.join(tempfile.gettempdir(), 'TheaForBlender.log'), maxBytes=100000)
        thea_globals.fh.setLevel(logging.DEBUG)
        thea_globals.log.addHandler(thea_globals.fh)
        logging.basicConfig(level=logging.INFO)
        thea_globals.log.debug("logger configured")


        if(getattr(bpy.context, "scene", None)!=None):
            setPaths(bpy.context.scene, verbose=True)
        else:
            setPaths(None, verbose=True)

        thea_globals.log.info("Thea addon started")
        return 0



exp = mainExporter()
exp.run()


