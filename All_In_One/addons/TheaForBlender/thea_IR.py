"""
.. module:: thea_IR
   :platform: OS X, Windows, Linux
   :synopsis: Functions and classes handling Interactive Rendering

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

import copy
from math import *
import os
import platform
from random import random
import struct
import subprocess
import sys
import time
import string

from TheaForBlender.thea_render_main import *
import bpy

from . import thea_globals



class RENDER_PT_thea_startSDK(bpy.types.Operator):
    '''Operator class to start Remote Darkroom
    '''

    bl_idname = "thea.start_sdk"
    bl_label = "Start SDK"
    _handle = None

    def modal(self, context, event):
        return {'PASS_THROUGH'}

    def cancel(self, context):
            #print("Killing process with pid %s " % context.scene['thea_sdkProcess'])
            os.kill(context.scene['thea_sdkProcess'],1)
            return {'CANCELLED'}

    def invoke(self, context, event):
        if context.scene.thea_sdkIsRunning == False:
            try:
                if context.scene.get('thea_SDKPort'):
                    port = context.scene.get('thea_SDKPort')
                else:
                    port = 30000
            except:
                port = 30000

            (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(context.scene)
            pArgs = []
            #pArgs.append(os.path.join(theaPath))
            pArgs.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "TheaRemoteDarkroom.exe"))
            pArgs.append('-remoteserver')
            pArgs.append(str(port))
            pArgs.append('-hidden')
            pArgs.append('-nosplash')
            #print(pArgs)
            # start SDK project on preview port
            sdkProcess = subprocess.Popen(pArgs)
            context.scene['thea_sdkProcess'] = sdkProcess.pid
            #print("Started process with pid %s " % sdkProcess.pid)
            self.region = context.region
            context.scene.thea_sdkIsRunning = True
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(draw_gl_content, (self, context, self.region, area), 'POST_PIXEL')

            #print("Starting SDK on port: ", port)
            #print("Started SDK")
            return {'RUNNING_MODAL'}
        else:
            # operator is called again, stop displaying
            try:
                os.kill(context.scene['thea_sdkProcess'],1)
            except:
                pass
            #print("Killing process with pid %s " % context.scene['thea_sdkProcess'])
            context.scene.thea_sdkIsRunning = False
            return {'FINISHED'}

class RENDER_PT_thea_stopSDK(bpy.types.Operator):
    '''Operator class to start Remote Darkroom
    '''
    bl_idname = "thea.stop_sdk"
    bl_label = "Start SDK"

    def invoke(self, context, event):
        if bpy.context.scene.sdkProcess.poll() is None:
            #print("Killing process with pid %s " % sdkProcess.pid)
            try:
                bpy.context.scene.sdkProcess.kill()
            except:
                pass
        return {'FINISHED'}


def register():
    return

#def exportIRCamera(scene, area, exportPath):
#    '''Export current 3d view camera to xml file so it can be merged into current IR session
#
#        :param scene: current scene
#        :type scene: bpy_types.Scene
#        :param area: GUI area
#        :type area: bpy_types.Area
#        :param exportPath: path to save xml file
#        :type exportPath: string
#    '''
#    #print("exportIRCamera")
#    resolutionDivider = 1
#
#    cam = ThCamera()
#    camData = area.spaces.active
#    if scene.get('thea_IRResolution'):
#        if scene.get('thea_IRResolution') == 0:
#            resolutionDivider = 1
#        if scene.get('thea_IRResolution') == 1:
#            resolutionDivider = 2
#        if scene.get('thea_IRResolution') == 2:
#            resolutionDivider = 4
#
#    thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)
#    if thea_globals.frame_px:
#        camOb = scene.camera
#        cam.name=camOb.name
#        camM = scene.camera.matrix_world
#        renderData = scene.render
#        x1 = thea_globals.frame_px[3][0]
#        y2 = thea_globals.frame_px[3][1]
#        x2 = thea_globals.frame_px[0][0]
#        y1 = thea_globals.frame_px[1][1]
#        resX = int(x2-x1)
#        resY = int(y2-y1)
#        #resX=int(renderData.resolution_x*renderData.resolution_percentage*0.01)
#        #resY=int(renderData.resolution_y*renderData.resolution_percentage*0.01)
#        camData = camOb.data
#        cam.pixels = resX
#        cam.lines = resY
#
#        if resX > resY:
#            fac = float(resX) / float(resY)
#        else:
#            fac = 1
#
#        if camData.type == "PERSP":
#            cam.projection = "perspective"
#            cam.focalLength = camData.lens
#            cam.focusDistance = 1
#            cam.filmHeight = 32 / fac
#            cam.shiftLensX = camData.shift_x
#            cam.shiftLensY = camData.shift_y
##           CHANGED > added diaphgrama and blades here
#            cam.diaphragm = camOb.thea_diaphragma
#            cam.blades = camOb.thea_diapBlades
#        elif camData.type == "ORTHO":
#            cam.projection = "Parallel"
##           CHANGED > Added different calculation
##             cam.filmHeight = camData.ortho_scale * 563.333333 #* 750
##             cam.focalLength = camData.ortho_scale * 563.333333 #* 750
##            cam.filmHeight = (camOb.scale*1000)/fac
#            cam.filmHeight = camData.ortho_scale
#            cam.focalLength = camData.lens
#        if camData.dof_distance > 0:
#            cam.focusDistance = camData.dof_distance
#            if camData.thea_pinhole == True:
#                try:
#                    aperture = camOb["aperture"]
#                    cam.fNumber = aperture
#                except: pass
#            elif camData.thea_enableDOFpercentage == True:
#                try:
#                    DOFpercentage = camOb["DOFpercentage"]
#                    cam.DOFpercentage = DOFpercentage
#                except:pass
#        else:
#            cam.fNumber = 0
##       CHANGED > Added zClipping options here for camera IR render mode
##        cam.zClippingNear = True
##        cam.zClippingNearDistance =  camData.clip_start
##        cam.zClippingFar = True
##        cam.zClippingFarDistance =  camData.clip_end
#
#
#
#    else:
#        cam.name="IR view"
#        camM = area.spaces.active.region_3d.view_matrix.inverted()
#    #camM = area.spaces.active.region_3d.view_matrix.inverted()
#        for region in area.regions:
#            if region.type == 'WINDOW':
#                viewWidth = region.width
#                viewHeight = region.height
#                break
#        cam.pixels = int(viewWidth/resolutionDivider)
#        cam.lines = int(viewHeight/resolutionDivider)
#
#        if viewWidth > viewHeight:
#            fac = float(viewWidth) / float(viewHeight)
#        else:
#         fac = 1
#
#        offset = area.spaces.active.region_3d.view_camera_offset
#
#
#        cam.focalLength = camData.lens / 2
#        cam.shiftLensX =  0
#        cam.shiftLensY =  0
#        if (area.spaces.active.region_3d.view_perspective == 'CAMERA'):
#            zoom = area.spaces.active.region_3d.view_camera_zoom;
#            zoom = (1.41421 + zoom/50.0)
#            zoom *= zoom
#            zoom = 2.0/zoom
#            ##print("zoom: ",zoom, round(zoom, 5), " offset: ",offset[0],offset[1])
#            cam.focalLength = camData.lens / zoom /2
#            cam.shiftLensX =  32 * offset[0] / zoom
#            cam.shiftLensY =  (32 * offset[1] * -1) / fac / zoom
#
#        #print("cam.focalLength: ", cam.focalLength, camData.lens,area.spaces.active.region_3d.view_camera_zoom, fac, " offset: ",cam.shiftLensX, cam.shiftLensY)
#        cam.focusDistance = 0
#        cam.filmHeight = 32 / fac
#        cam.fNumber = 0
#        #                ('1' if getattr(bpy.context.scene, 'thea_DispSharpness') else '0')
#        cam.zClippingNear = ('1' if getattr(camOb, "thea_zClippingNear") else '0')
#        print("ClipCheck: ", cam.zClippingNear)
#        cam.zClippingNearDistance =  camData.clip_start
#        cam.zClippingFar = ('1' if getattr(camOb, "thea_zClippingFar") else '0')
#        cam.zClippingFarDistance =  camData.clip_end
#
#
#    cam.frame = Transform(\
#                camM[0][0], -camM[0][1], -camM[0][2],
#                camM[1][0], -camM[1][1], -camM[1][2],
#                camM[2][0], -camM[2][1], -camM[2][2],
#                camM[0][3],  camM[1][3],  camM[2][3])
#    irFile = open(os.path.join(exportPath, 'ir.xml'), "w")
#    irFile.write('<Root Label=\"Kernel\" Name=\"\" Type=\"Kernel\">\n')
#    irFile.write('<Object Identifier=\"./Scenes/%s\" Label=\"Default Scene\" Name=\"%s\" Type=\"Scene\">\n' % ("Blender Scene","Blender Scene"))
#    cam.write(irFile)
#    display = DisplayOptions()
#    display.iso = scene.thea_DispISO
#    display.gamma = scene.thea_DispGamma
#    display.brightness = scene.thea_DispBrightness
#    display.shutter = scene.thea_DispShutter
#    display.fNumber = scene.thea_DispFNumber
##    CHANGED > Added sharpness - burn, new sharpness check
#    display.sharpness = scene.thea_DispSharpness
#    display.sharpnessWeight = scene.thea_DispSharpnessWeight / 100
#    display.burn = scene.thea_DispsBurn / 100
#    display.burnWeight = scene.thea_DispBurnWeight
#    display.bloom = scene.thea_DispBloom
##   CHANGED > added new bloom/glare menu
#    display.bloomItems = scene.thea_DispBloomItems
#    display.bloomWeight = scene.thea_DispBloomWeight / 100
#    display.glareRadius = scene.thea_DispGlareRadius / 100
#    display.vignetting = scene.thea_DispVignetting / 100
#    display.vignettingWeight = scene.thea_DispVignettingWeight / 100
#    display.minZ = scene.thea_DispMinZ
#    display.maxZ = scene.thea_DispMaxZ
#    display.write(irFile)
#    irFile.write("<Parameter Name=\"./Cameras/Active\" Type=\"String\" Value=\"%s\"/></Object>" % cam.name)
#    irFile.write("<Parameter Name=\"./Scenes/Active\" Type=\"String\" Value=\"Blender Scene\"/>")
#    irFile.write('</Root>\n')
#    irFile.close()
#    del(cam)
#    del(display)

def getRes(area):
    '''Get current area resolution

        :param area: current area
        :type area: bpy_types.Area
        :return: Tuple (resX, resY)
        :rtype: int, int
    '''


    if getattr(bpy.context.scene, 'thea_IRResolution'):
        if getattr(bpy.context.scene, 'thea_IRResolution') == "Quarter size":
            thea_globals.resolutionDivider = 4
        elif getattr(bpy.context.scene, 'thea_IRResolution') == "Half size":
            thea_globals.resolutionDivider = 2
        else:
            thea_globals.resolutionDivider = 1

    if thea_globals.frame_px:
        camM = bpy.context.scene.camera.matrix_world
        x1 = thea_globals.frame_px[3][0]
        y2 = thea_globals.frame_px[3][1]
        x2 = thea_globals.frame_px[0][0]
        y1 = thea_globals.frame_px[1][1]
        resX = int((x2-x1)/thea_globals.resolutionDivider // 4) * 4
        resY = int((y2-y1)/thea_globals.resolutionDivider // 4) * 4
    else:
        camM = area.spaces.active.region_3d.view_matrix.inverted()
        resX = int((bpy.context.region.width /thea_globals.resolutionDivider) // 4) * 4
        resY = int((bpy.context.region.height /thea_globals.resolutionDivider) // 4) * 4


    #print("-------------resX, rexY: ", resX, resY)
    thea_globals.resX = resX
    thea_globals.resY = resY

    return resX, resY

class RENDER_PT_thea_startIR(bpy.types.Operator):
    '''Start IR: FULL export of the scene
    '''
    bl_idname = "thea.start_ir"
    bl_label = "Start IR"
#     bl_options = {'REGISTER', 'UNDO'}
    START_DELAY = 0.3
    DELAY = 0.1
    _handle = None
    _timer = None
    region = None
    area = None
    camMatrix = None
    view3dZoom = None
    exportPath = None
    theaPath = None
    theaDir = None
    dataPath = None
    currentBlendDir = None
    currentBlendFile = None
    lastPreview = None
    previewAlpha = 1
    img = None
    _updating = False
    resolutionDivider = 1
    IRStartTime = 0
    countSinceUpdate = 0
    prevResX = 0
    prevResY = 0
    renderSizeUpdated = False

    reuseProp = bpy.props.BoolProperty(default= False)



    @staticmethod
    def handle_add(self, context):
        '''Add timer handler
        '''
        RENDER_PT_thea_startIR._handle = bpy.types.SpaceView3D.draw_handler_add(draw_gl_content, (self, context, self.region, context.area), 'WINDOW', 'POST_PIXEL')
        RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(self.DELAY, context.window)
#         RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(self.START_DELAY, context.window)

    @staticmethod
    def handle_remove(context):
        '''Remove timer handler
        '''
        if RENDER_PT_thea_startIR._handle is not None:
            context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
            bpy.types.SpaceView3D.draw_handler_remove(RENDER_PT_thea_startIR._handle, 'WINDOW')
        RENDER_PT_thea_startIR._handle = None
        RENDER_PT_thea_startIR._timer = None

    @classmethod
    def poll(cls, context):
        area_types = {'VIEW_3D'}
        return (context.area.type in area_types) and \
               (context.region.type == "WINDOW")

    def updateCamera(self, context):
        '''Update camera transform and lens data
        '''

        port = context.scene.thea_SDKPort
        data = sendSocketMsg('localhost', port, b'version')

        self.countSinceUpdate = 0

        if data.find('v'):
            area = context.area
            region = context.region
            scn = context.scene
            offset = area.spaces.active.region_3d.view_camera_offset

            self.camMatrix = context.area.spaces.active.region_3d.view_matrix.inverted()
            self.view3dZoom = copy.deepcopy(area.spaces.active.region_3d.view_camera_zoom)
            self.view3dOffset[0] = area.spaces.active.region_3d.view_camera_offset[0]
            self.view3dOffset[1] = area.spaces.active.region_3d.view_camera_offset[1]

            thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)
            resX, resY = getRes(area)
            if thea_globals.frame_px:
                camM = scn.camera.matrix_world
                message = 'set "./UI/Viewport/Camera/Active" = "%s"' % (bpy.context.scene.camera.name)
            else:
                camM = area.spaces.active.region_3d.view_matrix.inverted()
                message = 'set "./UI/Viewport/Camera/Active" = "%s"' % ("IR view")
#            thea_globals.log.debug("CAMERA TYPE: %s" % bpy.data.cameras["Camera.001"].type)
            data = sendSocketMsg('localhost', port, message.encode())
            #print("message: ",message, data)
            thea_globals.log.debug("message: %s -\n data: %s" % (message, data))

#             #print("message: ",message, data)

            message1 = 'set "./UI/Viewport/Camera/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (camM[0][0], -camM[0][1], -camM[0][2], camM[0][3],
                                                                                                     camM[1][0], -camM[1][1], -camM[1][2], camM[1][3],
                                                                                                     camM[2][0], -camM[2][1], -camM[2][2], camM[2][3])
            message2 = 'message "./UI/Viewport/Theme/RW_CMFR"'

            data = sendSocketMsg('localhost', port, message1.encode())
            ##print("message: ", message1, data)

#             data = sendSocketMsg('localhost', port, message2.encode(), waitForResponse=True)
            ##print("message: ", message2, data)

            if getattr(context.scene, "thea_IRShowTheaWindow", False) == False:
                message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (resX, resY)
#                message = ('%s\n%s\n%s' % (message1, message3, message2)).encode()
                data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)

                camData = area.spaces.active
                if resX > resY:
                    fac = float(resX) / float(resY)
                else:
                 fac = 1
                if view3d_camera_border(bpy.context.scene, area):
                    if bpy.context.scene.camera.data.sensor_fit == 'VERTICAL':
                        sensor_height =  bpy.context.scene.camera.data.sensor_height
                        sensor_width = bpy.context.scene.camera.data.sensor_height * fac
                        shiftLensX = sensor_height * bpy.context.scene.camera.data.shift_x
                        shiftLensY = sensor_height * bpy.context.scene.camera.data.shift_y * -1

                    else:
                        sensor_width = bpy.context.scene.camera.data.sensor_width
                        sensor_height = sensor_width / fac
                        shiftLensX = sensor_width * bpy.context.scene.camera.data.shift_x
                        shiftLensY = sensor_width * bpy.context.scene.camera.data.shift_y * -1
                    f = bpy.context.scene.camera.data.lens
#                     h = bpy.context.scene.camera.data.sensor_height
                    h = sensor_height
#                   CHANGED > Added correct check for if zclip is enabled
                    clip_start_enable = ('1' if getattr(bpy.context.scene.camera, "thea_zClippingNear") else '0')
                    clip_end_enable = ('1' if getattr(bpy.context.scene.camera, "thea_zClippingFar") else '0')
                    message = 'set "./UI/Viewport/Camera/Z-Clipping Near" = %s' % clip_start_enable
                    data = sendSocketMsg('localhost', port, message.encode())
                    message = 'set "./UI/Viewport/Camera/Z-Clipping Far" = %s' % clip_end_enable
                    data = sendSocketMsg('localhost', port, message.encode())
                    clip_start = bpy.context.scene.camera.data.clip_start
                    clip_end = bpy.context.scene.camera.data.clip_end
                else:
                    f = camData.lens /2
                    h = 32 / fac
                    thea_globals.log.debug("camData.lens: %s" % camData.lens)
                    clip_start = area.spaces.active.clip_start
                    clip_end = area.spaces.active.clip_end


                clip_start_enable = ('1' if getattr(bpy.context.scene.camera, "thea_zClippingNear") else '0')
                clip_end_enable = ('1' if getattr(bpy.context.scene.camera, "thea_zClippingFar") else '0')
                message = 'set "./UI/Viewport/Camera/Z-Clipping Near" = %s' % clip_start_enable
                data = sendSocketMsg('localhost', port, message.encode())
                message = 'set "./UI/Viewport/Camera/Z-Clipping Far" = %s' % clip_end_enable
                data = sendSocketMsg('localhost', port, message.encode())

#                message = 'set "./UI/Viewport/Camera/Projection" = %s' % ("Parallel")
                message = 'set "./UI/Viewport/Camera/Z-Clipping Near Distance" = %s' % clip_start
                data = sendSocketMsg('localhost', port, message.encode())
                message = 'set "./UI/Viewport/Camera/Z-Clipping Far Distance" = %s' % clip_end
                data = sendSocketMsg('localhost', port, message.encode())
                message = 'set "./UI/Viewport/Camera/Focal Length (mm)" = "%s"' % f
                data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)

                message = 'set "./UI/Viewport/Camera/Film Height (mm)" = "%s"' % h
                data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)

                if (area.spaces.active.region_3d.view_perspective == 'ORTHO'):
                    message = 'set "./Scenes/Active/Cameras/IR view/Projection" = "Parallel"'
#                    message = 'message "./UI/Viewport/Theme/ST_VPAR"'
                    data = sendSocketMsg('localhost', port, message.encode())
                    thea_globals.log.debug("message: %s -\n data: %s" % (message, data))

                    if bpy.context.scene.camera.data.sensor_fit == 'VERTICAL':
                        sensor_height = bpy.context.scene.camera.data.ortho_scale * 1000

                    elif bpy.context.scene.camera.data.sensor_fit == 'HORIZONTAL' or 'AUTO':
                        sensor_height = (bpy.context.scene.camera.data.ortho_scale * 1000) / fac

                    message = 'set "./UI/Viewport/Camera/Film Height (mm)" = "%s"' % (sensor_height)
                    data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)
                if bpy.context.scene.camera.data.type == 'ORTHO':
                    message = 'set "./Scenes/Active/Cameras/%s/Projection" = "Parallel"' % (bpy.context.scene.camera.name)
#                    message = 'set "./UI/Viewport/Theme/ST_VPAR"'
                    data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)
                    if bpy.context.scene.camera.data.sensor_fit == 'VERTICAL':
                        sensor_height = bpy.context.scene.camera.data.ortho_scale * 1000

                    elif bpy.context.scene.camera.data.sensor_fit == 'HORIZONTAL' or 'AUTO':
                        sensor_height = (bpy.context.scene.camera.data.ortho_scale * 1000) / fac

                    message = 'set "./UI/Viewport/Camera/Film Height (mm)" = "%s"' % (sensor_height)
                    data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=True)




    def updateObjectTransform(self, context):

        self.countSinceUpdate = 0
        port = context.scene.thea_SDKPort
        data = sendSocketMsg('localhost', port, b'version')

        if data.find('v'):

            message = b'message "./UI/Viewport/Theme/RW_PROG"'
            data = sendSocketMsg('localhost', port, message)

            area = context.area
            region = context.region
            scn = context.scene
            object = scn.objects.active
            if len(getattr(object, 'children')) == 0:
                obM = object.matrix_world
                if object.type == "MESH":
                    message = 'set "./Scenes/Active/Models/%s/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (object.name, obM[0][0], obM[0][1], obM[0][2], obM[0][3],
                                                                                                                          obM[1][0], obM[1][1], obM[1][2], obM[1][3],
                                                                                                                          obM[2][0], obM[2][1], obM[2][2], obM[2][3])
                elif object.type == "LAMP":
                    if object.name == 'Sun':
                            message = 'set "./Scenes/Active/Global Settings/Sun Direction" = "%s %s %s"' % (obM[0][2], obM[1][2], obM[2][2])
                            data = sendSocketMsg('localhost', port, message.encode())
                    message = 'set "./Scenes/Active/Lights/%s/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (object.name, obM[0][0], obM[0][1], -obM[0][2], obM[0][3],
                                                                                                                          obM[1][0], obM[1][1], -obM[1][2], obM[1][3],
                                                                                                                          obM[2][0], obM[2][1], -obM[2][2], obM[2][3])
                else:
                    return
                data = sendSocketMsg('localhost', port, message.encode())
                #print("message: ",message)
                #print("data: ", data)
            else:
                for object in getattr(object, 'children'):
                    obM = object.matrix_world
                    if object.type == "MESH":
                        message = 'set "./Scenes/Active/Models/%s/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (object.name, obM[0][0], obM[0][1], obM[0][2], obM[0][3],
                                                                                                                              obM[1][0], obM[1][1], obM[1][2], obM[1][3],
                                                                                                                              obM[2][0], obM[2][1], obM[2][2], obM[2][3])
                        data = sendSocketMsg('localhost', port, message.encode())
                    elif object.type == "LAMP":
                        if object.name == 'Sun':
                            message = 'set "./Scenes/Active/Global Settings/Sun Direction" = "%s %s %s"' % (obM[0][2], obM[1][2], obM[2][2])
                            data = sendSocketMsg('localhost', port, message.encode())
                        message = 'set "./Scenes/Active/Lights/%s/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (object.name, obM[0][0], obM[0][1], -obM[0][2], obM[0][3],
                                                                                                                              obM[1][0], obM[1][1], -obM[1][2], obM[1][3],
                                                                                                                              obM[2][0], obM[2][1], -obM[2][2], obM[2][3])
                        data = sendSocketMsg('localhost', port, message.encode())


            message = 'message "./UI/Viewport/Tweak Position"'
            data = sendSocketMsg('localhost', port, message.encode(), waitForResponse=False)

            if not thea_globals.IrIsPaused:
                message = b'message "./UI/Viewport/Theme/RW_EARF"'
                data = sendSocketMsg('localhost', port, message, waitForResponse=False)

    def updateEnvironment(self, context):
        thea_globals.log.debug("###############update Environment#################")
        self.countSinceUpdate = 0
        port = context.scene.thea_SDKPort
        scn = context.scene
        exporter=initExporter()
        (self.exportPath, self.theaPath, self.theaDir, self.dataPath, self.currentBlendDir, self.currentBlendFile) = setPaths(context.scene)
        xmlFile = os.path.join(self.exportPath, 'env.xml')
        args = exportFrame(context.scene,context.scene.frame_current,exporter=exporter, exportMode = 'Environment', xmlFile=xmlFile)


        if not thea_globals.IrIsPaused:
            message = b'message "./UI/Viewport/Theme/RW_PROG"'
            data = sendSocketMsg('localhost', port, message)
#         if data.find('Ok'):
        message = ('message \"Merge \'%s\' 0 0 0 1 1 0 0\"' % os.path.join(self.exportPath, 'env.xml')).encode()
        data = sendSocketMsg('localhost', port, message)
        #print("message: ", message)
        #print("data: ", data)
        if data.find('Ok'):
            #print("Scene merged")
#             message = b'message "./UI/Viewport/Tweak EnvironmentLight"'
#             #print("message: ",message)
#             data = sendSocketMsg('localhost', port, message)
            if not thea_globals.IrIsPaused:
                message = b'message "./UI/Viewport/Theme/RW_EARF"'
                data = sendSocketMsg('localhost', port, message)
                if data.find('Ok'):
                    thea_globals.log.info("\n\n***Interactive render started!****\n\n")

    def updateLamp(self, context):
        thea_globals.log.debug("###############updateLamp#################")
        self.countSinceUpdate = 0
        port = context.scene.thea_SDKPort
        scn = context.scene



#         import tempfile
#         tempDir = tempfile.gettempdir()
#         lampFilename = os.path.join(tempDir,'lamp.xml')
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
        xmlFilename = currentBlendFile.replace('.blend', '.xml')

        exporter=initExporter()
        #os.chdir(context.scene.render.filepath)
        #os.chdir(exportPath)
        region = bpy.context.region
        area = bpy.context.area
#                         bpy.context.scene['thea_Reuse'] = True
        currExportAnimation = getattr(bpy.context.scene, 'thea_ExportAnimation')
        currExportSelected = getattr(bpy.context.scene, 'thea_Selected')

        bpy.context.scene.thea_Selected = True
        bpy.context.scene.thea_ExportAnimation = False

        args = exportFrame(bpy.context.scene,bpy.context.scene.frame_current,exporter=exporter, area=area)

        bpy.context.scene.thea_Selected = currExportSelected
        bpy.context.scene.thea_ExportAnimation = currExportAnimation


        message = b'message "./UI/Viewport/Theme/RW_PROG"'
        data = sendSocketMsg('localhost', port, message)
        #print("message: ", message)
        #print("data: ", data)
        if data.find('Ok'):
            message = ('message "Merge \'%s\' 0 4 0 0 0 0"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
            data = sendSocketMsg('localhost', port, message)
            #print("message: ", message)
            #print("data: ", data)
            if data.find('Ok'):
                #print("Scene merged")
                if not thea_globals.IrIsPaused:
                    message = b'message "./UI/Viewport/Theme/RW_EARF"'
                    data = sendSocketMsg('localhost', port, message)
                    if data.find('Ok'):
                        thea_globals.log.info("\n\n***Interactive render started!****\n\n")




    def updateMaterial(self, context):
        self.countSinceUpdate = 0
        #print("******************* update material ***************")
        port = context.scene.thea_SDKPort
        area = context.area
        region = context.region
        scn = context.scene
        offset = area.spaces.active.region_3d.view_camera_offset

        material = scn.objects.active.active_material
        import tempfile
        tempDir = tempfile.gettempdir()

        matFilename = os.path.join(tempDir,'material_preview.xml')
        matFile = open(matFilename,"w")

        ##print("material: , ", material)

        ma = ThMaterial()
        ma.setName(material.name)
        ma.blenderMat = material
        if material:
            exporter = XMLExporter()
            thMat = exporter.generateMaterialNew(ma)
            ma.write(matFile, preview=True)

        message = "message \"LoadObject './Scenes/Active/Proxies/Appearance/%s' '%s'\"" % (material.name, matFilename)
        #print("message: ",message)
        data = sendSocketMsg('localhost', port, message)
        #print("data: ", data)
        message = b'message "./UI/Viewport/Tweak Material"'
        #print("message: ",message)
        data = sendSocketMsg('localhost', port, message)
        return





    def modal(self, context, event):

        port = context.scene.thea_SDKPort
        if context.area:
            context.area.tag_redraw()


        if event.type == 'TIMER':
            area = context.area
            region = context.region

            data = sendSocketMsg('localhost', port, b'version')
            thea_globals.log.debug("timer: %s" % time.time())

            if data.find('ERROR') >= 0:
                context.scene.thea_ir_running = False
                thea_globals.IrIsRunning = False
                self.report({'ERROR'}, "Connection with RemoteDarkroom has been lost, exiting IR!")
                return {'FINISHED'}
            ##print("materialUpdatesNumber: ", thea_globals.materialUpdatesNumber)
            if thea_globals.materialUpdatesNumber > 2:
                thea_globals.materialUpdatesNumber -= 1

            if (len(thea_globals.objectsUpdated) > 0):
                thea_globals.log.debug("Object updated *****************************")
                if getattr(context.scene, "thea_IRFullUpdate", False):
                    refreshIR()
                else:
                    for ob in thea_globals.objectsUpdated:
                        if ob.type == 'LAMP':
                            self.updateLamp(context)
                        if ob.type == 'CAMERA':
                            self.updateCamera(context)
                    self.updateObjectTransform(context)
                thea_globals.objectsUpdated = []
                if(getattr(context.scene, "thea_IRBlendAlpha", False)):
                    thea_globals.preview3DAlpha = 0.0
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)
#                 if(getattr(context.scene, "theaIRsyncDisplay")):
# #                   message = "RW_DTRB"
#                    message = b'message "./UI/Viewport/Theme/RW_DTRB"'
#                    data = sendSocketMsg('localhost', port, message)

            if thea_globals.materialUpdated:
                thea_updateIR(context)
                thea_globals.log.debug("\n\n\n\n************** material updated *********************\n\n\n\n: %s" % context.scene.objects.active.active_material)
                thea_globals.materialUpdated = False
                #time.sleep(0.2)
                context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
                RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)
            try:
                if (self.camMatrix != area.spaces.active.region_3d.view_matrix.inverted()) or (self.view3dZoom != area.spaces.active.region_3d.view_camera_zoom) or (self.view3dOffset[0] != area.spaces.active.region_3d.view_camera_offset[0]) and not self._updating:
                    camFrameChanged = True
                else:
                    camFrameChanged = False
            except:
                camFrameChanged = False
            if camFrameChanged or self.renderSizeUpdated:
                self.camMatrix = context.area.spaces.active.region_3d.view_matrix.inverted()
                self.view3dZoom = copy.deepcopy(area.spaces.active.region_3d.view_camera_zoom)
                #self.view3dOffset = copy.deepcopy(area.spaces.active.region_3d.view_camera_offset)
                self.view3dOffset[0] = area.spaces.active.region_3d.view_camera_offset[0]
                self.view3dOffset[1] = area.spaces.active.region_3d.view_camera_offset[1]
                self._updating = True
                self.updateCamera(context)
                if(getattr(context.scene, "thea_IRBlendAlpha", False)):
                    thea_globals.preview3DAlpha = 0.0
                self._updating = False
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)


            if thea_globals.engineUpdated:
                self.countSinceUpdate = 0
                thea_globals.log.debug("thea_globals.engineUpdated: %s" % thea_globals.engineUpdated)
                message = b'message "./UI/Viewport/Theme/RW_PROG"'
                data = sendSocketMsg('localhost', port, message)
                #print("message: ", message)
                #print("data: ", data)
                if data.find('Ok'):
                    message = ('set "./Scenes/Active/Render/Interactive/Engine Core" = "%s"' % getattr(context.scene, 'thea_IRRenderEngineMenu')).encode()
                    data = sendSocketMsg('localhost', port, message)
                    #print("message: ", message)
                    #print("data: ", data)
                    if data.find('Ok'):
                        #print("Scene merged")
                        if not thea_globals.IrIsPaused:
                            message = b'message "./UI/Viewport/Theme/RW_EARF"'
                            data = sendSocketMsg('localhost', port, message)
                            #print("message: ", message)
                            #print("data: ", data)
                            if data.find('Ok'):
                                thea_globals.log.info("\n\n***Interactive render started!****\n\n")
                thea_globals.engineUpdated = False
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)

            if thea_globals.displayUpdated:
                self.countSinceUpdate = 0
                thea_globals.log.debug("thea_globals.displayUpdated: %s" % thea_globals.displayUpdated)
                from TheaForBlender.thea_render_main import updateDisplaySettings
                updateDisplaySettings(port)

                thea_globals.displayUpdated = False
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)

            if thea_globals.lampUpdated:
                thea_globals.log.debug("Lamp updated")
                self.updateLamp(context)
                thea_globals.lampUpdated = False
                self.updateEnvironment(context)
                thea_globals.worldUpdated = False
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)

            if thea_globals.worldUpdated:
                thea_globals.log.debug("world updated")
                self.updateEnvironment(context)
#                CHANGED > Added lamp update so sun also gets update with IR
                self.updateLamp(context)
                thea_globals.lampUpdated = False
                thea_globals.worldUpdated = False
#                 context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                 RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)

            t1 = time.time()
            currentBlendDir = os.path.dirname(bpy.data.filepath)
            if getattr(area, 'type', 'None') == 'VIEW_3D' and not thea_globals.IrIsPaused:
#                thea_globals.log.debug("*** IR RENDER: %s" % (getattr(area, 'type', 'NONE')))
                if self.prevResX != getRes(area)[0] or self.prevResY != getRes(area)[1]:
                    self.renderSizeUpdated = True
                    self.prevResX, self.prevResY = getRes(area)
                else:
                    self.renderSizeUpdated = False


                message = b'status'
                data = sendSocketMsg('localhost', port, message)
                thea_globals.drawText = ''.join(filter(lambda x:x in string.printable, data))
                #print("thea_globals.drawText: ", thea_globals.drawText)


                thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)
                thea_globals.resX, thea_globals.resY = getRes(area)
                if thea_globals.frame_px:
                    camM = context.scene.camera.matrix_world

                    message = 'set "./UI/Viewport/Camera/Active" = "%s"' % (bpy.context.scene.camera.name)
#                    thea_globals.log.debug("*** IR RENDER: %s" % message)
                else:
                    camM = area.spaces.active.region_3d.view_matrix.inverted()
                if self.countSinceUpdate < 5:
                    thea_globals.IRScale = 4
                elif self.countSinceUpdate < 10:
                    thea_globals.IRScale = 2
                else:
                    thea_globals.IRScale = 1



                #print("self.countSinceUpdate: ", self.countSinceUpdate, self.countSinceUpdate % 10)
#                 if self.countSinceUpdate > 10: # after 10 updates change time to 1s
#                     context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
#                     RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(1, context.window)
                if thea_globals.IRScale > 1 or self.countSinceUpdate % 10 == 0: # update view if image is scaled or every tenth time
                    if (getattr(context.scene,"thea_SavePreviewtoImage") or getattr(context.scene,"thea_DrawPreviewto3dView")) and not getattr(context.scene,"thea_IRShowTheaWindow") :
                        if thea_globals.drawText.find("Ray Tracing") >=0:
                            #message = 'message "./UI/Viewport/SaveScaledImage %s %s"' % (thea_globals.IRScale, os.path.join(self.exportPath, thea_globals.IrPreviewFileName))
                            message = 'message "./UI/Viewport/SaveScaledImage %s %s"' % (thea_globals.IRScale, os.path.join(currentBlendDir, thea_globals.IrPreviewFileName))
                            data = sendSocketMsg('localhost', port, message.encode())
                    t2 = time.time()
                    thea_globals.log.debug("t2-t1: %s" % str(t2-t1))

                self.countSinceUpdate += 1
#
            if not thea_globals.IrIsPaused:
                try:
                    img = bpy.data.images[thea_globals.IrPreviewFileName]
                except:
                    try:
                        #img = bpy.data.images.load(os.path.join(exportPath, thea_globals.IrPreviewFileName))
                        img = bpy.data.images.load(os.path.join(currentBlendDir, thea_globals.IrPreviewFileName))
                    except:
                        img = None
                        return {'PASS_THROUGH'}

                t3 = time.time()
    #             if os.path.exists(os.path.join(self.exportPath, thea_globals.IrPreviewFileName)):
    #                 fileSize = os.path.getsize(os.path.join(self.exportPath, thea_globals.IrPreviewFileName))
    #             else:
    #                 fileSize = 0
    #             minSize = ((img.size[0]*img.size[1])/50)+thea_globals.minIRpreviewSize
                #print("fileSize, minSize: ", fileSize, minSize)
    #             if (fileSize>((img.size[0]*img.size[1])/50)+thea_globals.minIRpreviewSize): #if file is very small, it's probably empty
                img.reload()
                try:
                    img.scale(int(thea_globals.resX)*thea_globals.resolutionDivider, int(thea_globals.resY)*thea_globals.resolutionDivider)
                except:
                    pass
                t4 = time.time()

    #             thea_globals.log.debug("t4-t1: %s" % str(t4-t1))
    #             thea_globals.log.debug("t4-t3: %s" % str(t4-t3))


                for area in bpy.context.screen.areas:
                    if area.type == "IMAGE_EDITOR":
                        area.tag_redraw()

                thea_globals.preview3DAlpha += 0.1
                self.lastPreview = os.times()[4]

#

            return {'PASS_THROUGH'}



        if not context.scene.thea_ir_running:
            port = context.scene.thea_SDKPort

            data = sendSocketMsg('localhost', port, b'version')

            if data.find('v'):
                message = b'message "./UI/Viewport/Theme/RW_PROG"'
                data = sendSocketMsg('localhost', port, message)
                message = b'message "exit"'
                data = sendSocketMsg('localhost', port, message)
            #context.window_manager.event_timer_remove(self._timer)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):


        self.START_DELAY = getattr(bpy.context.scene, 'thea_RefreshDelay')
        self.view3dOffset = [0,0]
        thea_globals.preview3DAlpha = 0.0
        thea_globals.materialUpdated = False
        IrIsRunning = False
        thea_globals.objectsUpdated = []
        thea_globals.pixels = None

        context.window.cursor_set('WAIT')

        alpha = bpy.context.scene.get('thea_IRAlpha')
        if (bpy.context.scene.get('thea_IRAlpha') == None):
            bpy.context.scene['thea_IRAlpha'] = 1.0
        (self.exportPath, self.theaPath, self.theaDir, self.dataPath, self.currentBlendDir, self.currentBlendFile) = setPaths(context.scene)

        try:
            if bpy.context.active_object.mode != 'OBJECT':
                self.report({'ERROR'}, "Please change to object mode before rendering!")
                return {'FINISHED'}
        except:
            pass

        if len(self.currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        from TheaForBlender.thea_render_main import checkTheaMaterials
        if(checkTheaMaterials()==False):
            self.report({'ERROR'}, "Please set materials and lights to get proper render")
            return {'FINISHED'}

        from TheaForBlender.thea_render_main import checkTheaExtMat
        checkTheaExtMat()
        valuesExt = checkTheaExtMat()
        if (valuesExt[0]==False):
#            self.report({'ERROR'}, "Please link Material: %s > Object: %s" % (valuesExt[1], valuesExt[2]))
            missing_Mat = ""
            for mat in valuesExt[3]:
                missing_Mat = missing_Mat+"\n"+mat
#                layout = self.layout
#                box = layout.box()
#                col = box.column(align=True)
#                row = col.row(align=True)
#                row.alignment = "LEFT"
#                row.label(
#                            text=missing_Mat,
#                            icon="IMAGE_DATA")
            self.report({'ERROR'}, "Please link Material:%s" % missing_Mat)
#            thea_globals.log.debug("*** CheckMaterials = %s ***" % valuesExt[1])
            return {'FINISHED'}
        if not os.path.isdir(self.exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
        if bpy.context.scene.render.use_border:
            self.report({'ERROR'}, "Please disable Render Border")
            return {'FINISHED'}
        if context.area.type == 'VIEW_3D':

#             #print("############ area.spaces.active.local_view: ",context.area.spaces.active.local_view)
            if context.scene.thea_ir_running == False:
                try:
                    if context.scene.get('thea_SDKPort'):
                        port = context.scene.get('thea_SDKPort')
                    else:
                        port = 30000
                    #if context.scene.get('thea_RefreshDelay'):
                    #    self.DELAY = context.scene.get('thea_RefreshDelay')
                except:
                    port = 30000
                #self.DELAY = self.START_DELAY
#                 self.DELAY = getattr(context.scene, 'thea_RefreshDelay')
                socketServerIsRunning = False
                data = sendSocketMsg('localhost', port, b'version')
                #print("data: ",data)
                if data.find('v')>0:
                    socketServerIsRunning = True
                else:
                    p = startTheaRemoteDarkroom(port, show=getattr(context.scene, "thea_IRShowTheaWindow", False), idletimeout=getattr(context.scene, 'thea_IRIdleTimeout', 120))
                    ##print("process: ",p)
                    #time.sleep(bpy.context.scene.thea_StartTheaDelay)
                    message = b'version'
                    data = sendSocketMsg('localhost', port, message)
                    ##print("data: ",data)
                    if data.find('v')>0:
                        socketServerIsRunning = True

                #print("socketServerIsRunning: ",socketServerIsRunning)
                if socketServerIsRunning:
                    frame = context.scene.frame_current
                    frameS= "0000" + str(frame)
                    xmlFilename = self.currentBlendFile.replace('.blend', '.xml')
#                     os.chdir(os.path.dirname(self.theaPath))
                    exporter=initExporter()
                    context.scene.thea_IRMessage = "Exporting data..."

                    #os.chdir(context.scene.render.filepath)
                    os.chdir(self.exportPath)
                    self.region = context.region
                    context.scene.thea_ir_running = True
                    area = context.area
                    thea_globals.currentRegion = self.region

                    currExportAnimation = getattr(bpy.context.scene, 'thea_ExportAnimation')
                    if getattr(bpy.context.scene, 'thea_IRExportAnimation', False):
                        bpy.context.scene.thea_ExportAnimation = True
                    else:
                        bpy.context.scene.thea_ExportAnimation = False

                    currReuse = getattr(bpy.context.scene, 'thea_Reuse')
                    if self.reuseProp:
                        bpy.context.scene.thea_Reuse = True

                    if self.reuseProp == False and getattr(bpy.context.scene, 'thea_IRAdvancedIR', False):
                        bpy.context.scene.thea_Reuse = False
#                         thea_globals.forceExportGeometry=True

                    args = exportFrame(context.scene,context.scene.frame_current,exporter=exporter, area=area)

#                     thea_globals.forceExportGeometry=False
                    bpy.context.scene.thea_Reuse = currReuse
                    bpy.context.scene.thea_ExportAnimation = currExportAnimation
                    context.scene.thea_IRMessage = ""
                    self.camMatrix = context.area.spaces.active.region_3d.view_matrix.inverted()
                    self.view3dZoom = area.spaces.active.region_3d.view_camera_zoom
                    self.view3dOffset[0] = area.spaces.active.region_3d.view_camera_offset[0]
                    self.view3dOffset[1] = area.spaces.active.region_3d.view_camera_offset[1]
                    draw_IR_string("Starting IR", 10, 20, getattr(context.scene, 'thea_IRFontSize', 12)*1.8, (1.0, 1.0, 1.0, 1.0))
                    thea_globals.IrIsRunning = True

                      #load another scene and then merge exported one
                    if getattr(bpy.context.scene, "thea_showMerge"):
                        if os.path.exists(getattr(bpy.context.scene, 'thea_mergeFilePath')):
                            mergeString = (" %s %s %s %s %s %s" % (bpy.context.scene.thea_SceneMerModels, bpy.context.scene.thea_SceneMerLights, bpy.context.scene.thea_SceneMerCameras, bpy.context.scene.thea_SceneMerRender, bpy.context.scene.thea_SceneMerEnv, bpy.context.scene.thea_SceneMerMaterials))
                            if getattr(bpy.context.scene, 'thea_SceneMerReverseOrder'):
                                message = ('message "Load %s"' % getattr(bpy.context.scene, 'thea_mergeFilePath')).encode()
                                data = sendSocketMsg('localhost', port, message)
                                message = ('message "Merge %s %s' % (os.path.join(self.exportPath, os.path.basename(xmlFilename)), mergeString)).encode()
                                data = sendSocketMsg('localhost', port, message)
                            else:
                                message = ('message "Load %s"' % os.path.join(self.exportPath, os.path.basename(xmlFilename))).encode()
                                data = sendSocketMsg('localhost', port, message)
                                message = ('message "Merge %s %s' % (getattr(bpy.context.scene, 'thea_mergeFilePath'), mergeString)).encode()
                                data = sendSocketMsg('localhost', port, message)
                                #print("data: ", data)
                    else:
                        message = ('message "Load %s"' % os.path.join(self.exportPath, os.path.basename(xmlFilename))).encode()
                        data = sendSocketMsg('localhost', port, message)

                    currSelected = getattr(bpy.context.scene, 'thea_Selected')
                    currReuse = getattr(bpy.context.scene, 'thea_Reuse')
#                     thea_globals.log.debug("reuseProp: %s" % self.reuseProp)
#                     if getattr(bpy.context.scene, "thea_IRFullExportSelected") and currReuse:
                    if self.reuseProp and getattr(bpy.context.scene, "thea_IRFullExportSelected"):
                        if getattr(bpy.context.scene, "thea_IRFullExportSelected"):
                            bpy.context.scene.thea_Selected = True
                            thea_globals.forceExportGeometry=True
                        else:
                            bpy.context.scene.thea_Selected = False
                            thea_globals.forceExportGeometry=False
                        bpy.context.scene.thea_Reuse = True

                        args = exportFrame(bpy.context.scene,bpy.context.scene.frame_current,exporter=exporter, area=area)
                        thea_globals.forceExportGeometry=False
                        message = ('message \"Merge \'%s\' 4 0 0 0 0 1 1\"' % os.path.join(self.exportPath, os.path.basename(xmlFilename))).encode()
                        data = sendSocketMsg('localhost', port, message)

                    bpy.context.scene.thea_ExportAnimation = currExportAnimation
                    bpy.context.scene.thea_Selected = currSelected
                    bpy.context.scene.thea_Reuse = currReuse
                        #print("data: ", data)

#                     message = ('message "Load %s"' % os.path.join(self.exportPath, os.path.basename(xmlFilename))).encode()
#                     #print("message: ", message)
#                     data = sendSocketMsg('localhost', port, message)
#                     #print("data: ", data)
                    if data.find('Ok'):
                        #print("Scene loaded")
                        self.updateCamera(context)

                        #switch to camera frame
                        message = b'message "./UI/Viewport/Theme/RW_CMFR"'
                        data = sendSocketMsg('localhost', port, message)
                        #print("message: ",message)
                        ##print("out: ", data)
                        #set resolution
                        thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)
                        resX, resY = getRes(area)
                        self.prevResX, self.prevResY = getRes(area)
                        if thea_globals.frame_px:
                            camM = bpy.context.scene.camera.matrix_world

                        else:
                            camM = area.spaces.active.region_3d.view_matrix.inverted()
                        message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (resX, resY)
                        #print("message res: ",message, message.encode())
                        data = sendSocketMsg('localhost', port, message.encode())
                        #print("out: ", data)
                        #start auto refresh IR
                        message = b'message "./UI/Viewport/Theme/RW_EARF"'
                        #print("message: ",message)
                        data = sendSocketMsg('localhost', port, message)
                        thea_globals.IrIsPaused = False
                        if data.find('Ok'):
                            thea_globals.log.info("\n\n***Interactive render started!****\n\n")
                            self.report({'INFO'}, "Interactive render started")
                            thea_globals.IRScale = 4

#                             time.sleep(self.START_DELAY)
                            self.IRStartTime = os.times()[4]
#                             try:
#                                 img = bpy.data.images['IR Result']
#                             except:
#                                 img = False
#                             thea_globals.log.debug("img: %s" % img)
#                             if not img:
#                                 img = bpy.data.images.new('IR Result', width=int(resX/thea_globals.IRScale), height=int(resY/thea_globals.IRScale))
#                                 thea_globals.log.debug("creating new img: %s" % img)
#                                 img.filepath_raw = "/tmp/irresult.png"
#                                 img.file_format = 'PNG'
#                                 img.save()
#                                 img.reload()
                            #print("self.IRStartTime: ", self.IRStartTime)
                            currentBlendDir = os.path.dirname(bpy.data.filepath)
                            #message = 'message "./UI/Viewport/SaveImage %s"' % os.path.join(self.exportPath, thea_globals.IrPreviewFileName)
                            message = 'message "./UI/Viewport/SaveImage %s"' % os.path.join(currentBlendDir, thea_globals.IrPreviewFileName)
                            data = sendSocketMsg('localhost', port, message.encode())
                            #print("data: ", data)
                            try:
                                img = bpy.data.images[thea_globals.IrPreviewFileName]
                                #img.filepath = os.path.join(self.exportPath, thea_globals.IrPreviewFileName)
                                img.filepath = os.path.join(currentBlendDir, thea_globals.IrPreviewFileName)
                                img.reload()
                            except:
                                try:
                                    #img = bpy.data.images.load(os.path.join(self.exportPath, thea_globals.IrPreviewFileName))
                                    img = bpy.data.images.load(os.path.join(currentBlendDir, thea_globals.IrPreviewFileName))
                                except:
                                    pass
                            self.cursor_on_handle = 'None'
                            context.window_manager.modal_handler_add(self)
                            self.lastPreview = os.times()[4]
                            self.previewAlpha = 0
                            RENDER_PT_thea_startIR.handle_add(self, context)
                            bpy.context.scene.thea_ir_update = False
                            bpy.context.scene.thea_lastIRUpdate = os.times()[4]
                            bpy.app.handlers.scene_update_post.append(thea_collectUpdatedObjects)
#                             bpy.app.handlers.scene_update_post.append(thea_sceneUpdated)

                            message = b'version'
                            data = sendSocketMsg('localhost', port, message)
                            ##print("data: ",data)
#                             if data.find('v1.3')>0:
#                                 exportIRCamera(context.scene, area, self.exportPath)
#
#                                 message = ('message "Merge %s 0 0 1 0 0"' % os.path.join(self.exportPath, 'ir.xml')).encode()
#                                 #message = ('message "Merge %s 0 0 1 1 0"' % os.path.join(self.exportPath, 'ir.xml')).encode()
#                                 data = sendSocketMsg('localhost', port, message)
#                                 #print("message: ",message)
#                                 if data.find('Ok'):
#                                     message = 'set "./Cameras/Active" = "%s"' % ("Camera")
#                                     #switch to camera frame
#                                     message = b'message "./UI/Viewport/Theme/RW_CMFR"'
#                                     data = sendSocketMsg('localhost', port, message)
#                                     #print("message: ",message)
#                                     message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (resX, resY)
#                                     #print("message: ",message)
#                                     data = sendSocketMsg('localhost', port, message.encode())
#                                     bpy.context.scene.thea_ir_update = True
#                                     #draw_IR_preview(self, context, self.region, self.previewAlpha, self.img, area)
#                                     #time.sleep(0.2) #small delay to give thea time to render anything after merge
#                                     thea_globals.IrIsRunning = True
                                    #print("data: ", data)


#                             img = bpy.data.images['IR Result']
#                             thea_globals.log.debug("img2: %s" % img)
                            context.window.cursor_set('DEFAULT')

                            return {'RUNNING_MODAL'}
                elif data == b'ERROR':
                    self.report({'WARNING'}, "Thea socket server is not running, can't run operator")
                    thea_globals.IrIsRunning = False
                    context.window.cursor_set('DEFAULT')
                    return {'CANCELLED'}
            else:
                # operator is called again, stop displaying
                context.scene.thea_ir_running = False
                thea_globals.IrIsRunning = False
                RENDER_PT_thea_startIR.handle_remove(context)
                context.window.cursor_set('DEFAULT')
                return {'CANCELLED'}

        else:
            self.report({'WARNING'}, "View3D not found, can't run operator")
            context.window.cursor_set('DEFAULT')
            return {'CANCELLED'}



def draw_IR_string(text, x, y, size, color):

    dpi, font = 72, 0
    bgl.glEnable(bgl.GL_BLEND)
    blf.enable(0, blf.SHADOW)
    blf.shadow_offset(0, 2, -2)
    blf.shadow(0, 5, 0.0, 0.0, 0.0, 0.8)
    bgl.glColor4f(0.0, 0.0, 0.0, 0.8)
    bgl.glLineWidth(2)
    bgl.glColor4f(*color)
    blf.position(font, x, y, 0)
    blf.size(font, int(size), dpi)
    blf.draw(font, text)
    blf.disable(0, blf.SHADOW)



def find_3d_view(area):

    if area.type == 'VIEW_3D':
        v3d = area.spaces[0]
        rv3d = v3d.region_3d
        for region in area.regions:
            if region.type == 'WINDOW':
                viewM = area.spaces.active.region_3d.view_matrix.to_euler().to_matrix() #use only rotation data
                camM = bpy.context.scene.camera.matrix_world.inverted().to_euler().to_matrix()
                sum = 0
                for v in (viewM-camM):
                    for i in v:
                        sum += abs(i)
                ##print("sum: ", sum)
                if sum<1e-5:
                    return region, rv3d
    return None, None

def view3d_camera_border(scene, area):
    try:
        obj = scene.camera
        cam = obj.data

        frame = cam.view_frame(scene)

        # move into object space
        frame = [obj.matrix_world * v for v in frame]

        # move into pixelspace
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        region, rv3d = find_3d_view(area)
        if region:
            frame_px = [location_3d_to_region_2d(region, rv3d, v) for v in frame]
            return frame_px
        else:
            return False
    except:
        return False

# def draw_IR_preview(self, context, region, previewAlpha, img, area):
def draw_IR_preview(self, context, region, previewAlpha, area):

    if region.type == 'WINDOW':

        viewWidth = region.width
        viewHeight = region.height

        img = bpy.data.images[thea_globals.IrPreviewFileName]
#         img = getattr(bpy.data.images, 'IR Result', False)
#         img = bpy.data.images['IR Result']
        #print("****img size: ", img.size[0], img.size[1])
        if not img:
            return
        elif img.size[0]>0:
            thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)

            if img.size[0]>0:
                if thea_globals.frame_px:
                    x1 = thea_globals.frame_px[3][0]
                    y2 = thea_globals.frame_px[3][1]
                    x2 = thea_globals.frame_px[0][0]
                    y1 = thea_globals.frame_px[1][1]
                else:
                    x1 = 0
                    y1 = 0
#
                    if getattr(bpy.context.scene, "thea_Fit3dView"):
                        x2 = viewWidth
                        y2 = viewHeight
                    else:
                        x2 = thea_globals.resX
                        y2 = thea_globals.resY
                color=[1,1,1,1]
                img.gl_free()
                img.gl_load(bgl.GL_NEAREST, bgl.GL_NEAREST)
                if hasattr(img.bindcode, "__len__"): #fix for change in 2.77
                    bindcode = img.bindcode[0]
                else:
                    bindcode = img.bindcode
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, bindcode)
                bgl.glEnable(bgl.GL_TEXTURE_2D)
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glColor4f(1,1,1,max(min(thea_globals.preview3DAlpha, 1), 0))
                #bgl.glColor4f(1,1,1,0.5)
                bgl.glBegin(bgl.GL_QUADS)
                bgl.glTexCoord2f(0,0)
                bgl.glVertex2f(x1,y1)
                bgl.glTexCoord2f(0,1)
                bgl.glVertex2f(x1,y2)
                bgl.glTexCoord2f(1,1)
                bgl.glVertex2f(x2,y2)
                bgl.glTexCoord2f(1,0)
                bgl.glVertex2f(x2,y1)
                bgl.glEnd()



def draw_IR_bitmap(self, context, region, previewAlpha, area):


    if region.type == 'WINDOW':

        viewWidth = region.width
        viewHeight = region.height

        img = 0
#         img = bpy.data.images[thea_globals.IrPreviewFileName]
        img = getattr(bpy.data.images, 'IR Result', False)
        #print("******************img: ", img)
        #print("len(thea_globals.pixels): ", len(thea_globals.pixels))
        #print("img.size[0], img.size[1], thea_globals.resolutionDivider,  thea_globals.IRScale", img.size[0], img.size[1], thea_globals.resolutionDivider, thea_globals.IRScale)
        #print("(img.size[0] / thea_globals.resolutionDivider) * (img.size[1]*4 /  thea_globals.resolutionDivider)  / thea_globals.IRScale)", (img.size[0] / thea_globals.resolutionDivider) * (img.size[1]*4 /  thea_globals.resolutionDivider)  / thea_globals.IRScale)
        if img and thea_globals.pixels:
            if (len(thea_globals.pixels) == (img.size[0] / thea_globals.resolutionDivider) * (img.size[1]*4 /  thea_globals.resolutionDivider)  / thea_globals.IRScale):
                thea_globals.frame_px = view3d_camera_border(bpy.context.scene, area)
#                 #print("img.size: ", img.size[0], img.size[1])
                if img.size[0]>0:
                    if thea_globals.frame_px:
                        x1 = int(thea_globals.frame_px[3][0])
                        y2 = int(thea_globals.frame_px[3][1])
                        x2 = int(thea_globals.frame_px[0][0])
                        y1 = int(thea_globals.frame_px[1][1])
                    else:
                        x1 = 0
                        y1 = 0
                        x2 = int(viewWidth)
                        y2 = int(viewHeight)
                    #print("x1, y1, x2, y2", x1, y1, x2, y2)
#                     #print("***1***")
                    t1 = time.time()
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA);
                    bgl.glDisable(bgl.GL_DEPTH_TEST)
#                     bgl.glColor4f(1,1,1,max(min(thea_globals.preview3DAlpha, 1), 0))
                    t2 = time.time()
                    #print("thea_globals.preview3DAlpha: ", thea_globals.preview3DAlpha)
#                     #print("t2-t1", t2-t1)
#                     #print("thea_globals.pixels: ", thea_globals.pixels)
                    bitmap = bgl.Buffer(bgl.GL_FLOAT, len(thea_globals.pixels), thea_globals.pixels)
                    t3 = time.time()
#                     #print("t3-t2", t3-t2)
                    if getattr(bpy.context.scene, 'thea_Fit3dView'):
                        xFactor = (x2-x1)/img.size[0]
                        yFactor = (y2-y1)/img.size[1]
                        bgl.glPixelZoom(thea_globals.IRScale*thea_globals.resolutionDivider*xFactor, thea_globals.IRScale*thea_globals.resolutionDivider*yFactor)
                    else:
                        bgl.glPixelZoom(thea_globals.IRScale, thea_globals.IRScale)
                    t4 = time.time()
#                     #print("t4-t3", t4-t3)
                    bgl.glRasterPos2i(x1,y1)
                    t5 = time.time()
#                     #print("t5-t4", t5-t4)
#                     #print("scale %s, len(thea_globals.pixels) %s " %(thea_globals.IRScale, len(thea_globals.pixels)))
                    bgl.glDrawPixels(int((img.size[0] / thea_globals.resolutionDivider)/thea_globals.IRScale), int((img.size[1] / thea_globals.resolutionDivider)/thea_globals.IRScale),
                             bgl.GL_RGBA, bgl.GL_FLOAT,
                             bitmap
                             )
                    t6 = time.time()

#                     #print("t6-t5", t6-t5)
#                     #print("t6-t1", t6-t1)

def draw_gl_content(self, context, region, area):

    if getattr(context.scene, 'thea_DrawPreviewto3dView') and getattr(context.scene, 'thea_ir_running'):
        #print("-----------------------------region.as_pointer(), thea_globals.currentRegion: ", region.as_pointer(), thea_globals.currentRegion.as_pointer())
        if bpy.context.region.as_pointer() == thea_globals.currentRegion.as_pointer() and not getattr(context.scene,"thea_IRShowTheaWindow") :
            if thea_globals.drawText.find("Ray Tracing") >=0:
                draw_IR_preview(self, context, self.region,thea_globals.preview3DAlpha,area)
            if thea_globals.IrIsPaused:
                draw_IR_string(thea_globals.drawText, 60, 25, getattr(context.scene, 'thea_IRFontSize', 12)*1.3, (1.0, 0.0, 0.0, 1))
            else:
                draw_IR_string(thea_globals.drawText, 60, 25, getattr(context.scene, 'thea_IRFontSize', 12), (1.0, 1.0, 1.0, 1))
    return


def refreshIR(update=False):

    region = None
    resolutionDivider = 1

    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)

    #global preview3DAlpha
    thea_globals.preview3DAlpha = 0.0

    if bpy.context.area.type == 'VIEW_3D':
        bpy.context.window.cursor_set('WAIT')
        if bpy.context.scene.thea_ir_running == True:
            try:
                if bpy.context.scene.get('thea_SDKPort'):
                    port = context.scene.get('thea_SDKPort')
                else:
                    port = 30000
                #if context.scene.get('thea_RefreshDelay'):
                #    self.DELAY = context.scene.get('thea_RefreshDelay')
            except:
                port = 30000

            data = sendSocketMsg('localhost', port, b'version')

            if data.find('v'):

                message = b'message "./UI/Viewport/Theme/RW_PROG"'
                data = sendSocketMsg('localhost', port, message)
                #print("\n\n***Interactive render stopped!****\n\n")
                frame = bpy.context.scene.frame_current
                frameS= "0000" + str(frame)
                xmlFilename = currentBlendFile.replace('.blend', '.xml')
                os.chdir(os.path.dirname(theaPath))
                exporter=initExporter()
                #os.chdir(context.scene.render.filepath)
                os.chdir(exportPath)
                region = bpy.context.region
                area = bpy.context.area
#                         bpy.context.scene['thea_Reuse'] = True
                currExportAnimation = getattr(bpy.context.scene, 'thea_ExportAnimation')
                currSelected = getattr(bpy.context.scene, 'thea_Selected')
                currReuse = getattr(bpy.context.scene, 'thea_Reuse')
                if getattr(bpy.context.scene, 'thea_IRExportAnimation', False):
                    bpy.context.scene.thea_ExportAnimation = True
                else:
                    bpy.context.scene.thea_ExportAnimation = False


#                         bpy.context.scene['thea_Reuse'] = False
#                         message = ('message "Merge %s 4 1 2 1 1 4"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
                if update:
                    bpy.context.scene.thea_Selected = True
                    bpy.context.scene.thea_Reuse = False
                    args = exportFrame(bpy.context.scene,bpy.context.scene.frame_current,exporter=exporter, area=area)
                    thea_globals.log.debug("args: %s" % args)
                    message = ('message \"Merge \'%s\' 4 0 0 0 0 1 1\"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
#                         message = ('message \"Merge %s 4 0 0 0 0 \"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()

                else:
                    message = b'message "Reset"'
                    data = sendSocketMsg('localhost', port, message)
                    args = exportFrame(bpy.context.scene,bpy.context.scene.frame_current,exporter=exporter, area=area)
                    message = ('message "Load %s"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()

                bpy.context.scene.thea_ExportAnimation = currExportAnimation
                bpy.context.scene.thea_Selected = currSelected
                bpy.context.scene.thea_Reuse = currReuse
#                         message = ('message "Load %s"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
                #print("message: ", message)
                data = sendSocketMsg('localhost', port, message)
                #print("data: ", data)
                if data.find('Ok') and not update:
                    #print("Scene merged")
#                         if bpy.context.scene.get('thea_IRResolution'):
#                             if bpy.context.scene.get('thea_IRResolution') == 0:
#                                 resolutionDivider = 1
#                             if bpy.context.scene.get('thea_IRResolution') == 1:
#                                 resolutionDivider = 2
#                             if bpy.context.scene.get('thea_IRResolution') == 2:
#                                 resolutionDivider = 4
                    resX, resY = getRes(area)
                    if thea_globals.frame_px:
                        camM = bpy.context.scene.camera.matrix_world
#                             x1 = thea_globals.frame_px[3][0]
#                             y2 = thea_globals.frame_px[3][1]
#                             x2 = thea_globals.frame_px[0][0]
#                             y1 = thea_globals.frame_px[1][1]
#                             resX = int((x2-x1)/resolutionDivider)
#                             resY = int((y2-y1)/resolutionDivider)
                        message = 'set "./UI/Viewport/Camera/Active" = "%s"' % (bpy.context.scene.camera.name)
                    else:
                        camM = area.spaces.active.region_3d.view_matrix.inverted()
#                             resX = int(bpy.context.region.width/resolutionDivider)
#                             resY = int(bpy.context.region.height/resolutionDivider)
                        #message = 'set "./Cameras/Active" = "%s"' % ("3D View")
                        message = 'set "./UI/Viewport/Camera/Active" = "%s"' % ("IR view")
                    data = sendSocketMsg('localhost', port, message.encode())
                    #print("message: ",message, data)

                    #switch to camera frame
                    message = b'message "./UI/Viewport/Theme/RW_CMFR"'
                    data = sendSocketMsg('localhost', port, message)
                    #print("message: %s, data: %s|" % (message, data))


                    message1 = 'set "./UI/Viewport/Camera/Frame" = "%s %s %s %s %s %s %s %s %s %s %s %s"' % (camM[0][0], -camM[0][1], -camM[0][2], camM[0][3],
                                                                                                             camM[1][0], -camM[1][1], -camM[1][2], camM[1][3],
                                                                                                             camM[2][0], -camM[2][1], -camM[2][2], camM[2][3])
                    data = sendSocketMsg('localhost', port, message1.encode())
                    #set resolution
                    if getattr(bpy.context.scene, "thea_IRShowTheaWindow", False) == False:
#                             message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (int(bpy.context.region.width/resolutionDivider),int(bpy.context.region.height/resolutionDivider))
                        message = 'set "./UI/Viewport/Camera/Resolution" = "%sx%s"' % (resX, resY)
                        #print("message: ",message)
                        data = sendSocketMsg('localhost', port, message.encode())
                        #print("out: ", data)
                if not thea_globals.IrIsPaused:
                    message = b'message "./UI/Viewport/Theme/RW_EARF"'
                    data = sendSocketMsg('localhost', port, message)
                    thea_globals.IrIsPaused = False
                if data.find('Ok'):
                    bpy.context.window.cursor_set('DEFAULT')
                    #print("\n\n***Interactive render started!****\n\n")
                    return {'FINISHED'}
            elif data == b'ERROR':
                bpy.context.window.cursor_set('DEFAULT')
#                         self.report({'WARNING'}, "Thea socket server is not running, can't run operator")
                return {'CANCELLED'}
#                 else:
# #                     self.report({'WARNING'}, "IR is not currently running")
#                     return {'CANCELLED'}
    else:
#                 self.report({'WARNING'}, "View3D not found, can't run operator")
        return {'CANCELLED'}


class RENDER_PT_thea_refreshIR(bpy.types.Operator):
    bl_idname = "thea.refresh_ir"
    bl_label = "Refresh IR preview"
    #DELAY = 2
    _handle = None
    _timer = None


    def invoke(self, context, event):
        return refreshIR()

class RENDER_PT_thea_updateIR(bpy.types.Operator):
    '''Export and update selected objects'''
    bl_idname = "thea.update_ir"
    bl_label = "Update selected objects"
    #DELAY = 2
    _handle = None
    _timer = None


    def invoke(self, context, event):
        return refreshIR(update=True)


class RENDER_PT_thea_pauseIR(bpy.types.Operator):
    bl_idname = "thea.pause_ir"
    bl_label = "Update selected objects"
    #DELAY = 2
    _handle = None
    _timer = None


    def invoke(self, context, event):
        try:
            if bpy.context.scene.get('thea_SDKPort'):
                port = context.scene.get('thea_SDKPort')
            else:
                port = 30000
            #if context.scene.get('thea_RefreshDelay'):
            #    self.DELAY = context.scene.get('thea_RefreshDelay')
        except:
            port = 30000

        data = sendSocketMsg('localhost', port, b'version')

        if data.find('v'):

            if thea_globals.IrIsPaused:
                message = b'message "./UI/Viewport/Theme/RW_EARF"'
                thea_globals.IrIsPaused = False
                context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
                RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(RENDER_PT_thea_startIR.START_DELAY, context.window)
            else:
                message = b'message "./UI/Viewport/Theme/RW_PROG"'
                thea_globals.IrIsPaused = True
                thea_globals.log.debug("******Pausing IR %s %s %s" % (RENDER_PT_thea_startIR._timer.time_delta, RENDER_PT_thea_startIR._timer.time_duration, RENDER_PT_thea_startIR._timer.time_step))
                context.window_manager.event_timer_remove(RENDER_PT_thea_startIR._timer)
                RENDER_PT_thea_startIR._timer = context.window_manager.event_timer_add(1, context.window)
                thea_globals.log.debug("***********************Pausing IR %s %s %s" % (RENDER_PT_thea_startIR._timer.time_delta, RENDER_PT_thea_startIR._timer.time_duration, RENDER_PT_thea_startIR._timer.time_step))
                thea_globals.drawText = "IR: paused"
            data = sendSocketMsg('localhost', port, message)




        return {'FINISHED'}

class RENDER_PT_thea_startIRSelected(bpy.types.Operator):
    bl_idname = "thea.start_ir_selected"
    bl_label = "Start IR: export only selected meshes"
    #DELAY = 2
    _handle = None
    _timer = None


    def invoke(self, context, event):
        bpy.ops.thea.start_ir
        return {'FINISHED'}

class RENDER_PT_thea_startIRReuse(bpy.types.Operator):
    '''Start IR: Fast export, reuse already exported mesh data'''
    bl_idname = "thea.start_ir_reuse"
    bl_label = "Start IR: reuse mesh data"

    def invoke(self, context, event):
        bpy.ops.thea.start_ir('INVOKE_DEFAULT', reuseProp=True)
        return {'FINISHED'}

class RENDER_PT_thea_startIRSmart(bpy.types.Operator):
    '''Start/Pause IR: Try to be smart and figure out if it's time to do full export, start, resume or pause'''
    bl_idname = "thea.smart_start_ir"
    bl_label = "Start/Pause IR: smart way"


    def __init__(self):
        self.started = False
        self.step = 0

    @staticmethod
    def handle_add(self, context):
        RENDER_PT_thea_startIRSmart._timer = context.window_manager.event_timer_add(0.1, context.window)

    @staticmethod
    def handle_remove(context):
        if RENDER_PT_thea_startIRSmart._handle is not None:
            context.window_manager.event_timer_remove(RENDER_PT_thea_startIRSmart._timer)
        RENDER_PT_thea_startIRSmart._handle = None
        RENDER_PT_thea_startIRSmart._timer = None

    @classmethod
    def poll(cls, context):
        area_types = {'VIEW_3D',}
        return (context.area.type in area_types) and \
               (context.region.type == "WINDOW")


    def modal(self, context, event):


        thea_globals.log.debug("Smart IR: modal, step: %s" % self.step)
#         if event.type == 'TIMER' and not self.started and self.step == 0:
        if not self.started and self.step == 0:
            thea_globals.log.debug("Starting IR")
            self.report({'INFO'}, "Starting IR")
            self.step = 1
            return {'PASS_THROUGH'}

#         if event.type == 'TIMER' and not self.started and self.step > 0:
        if not self.started and self.step > 0:
            self.started = True
            if thea_globals.IrIsRunning:
                thea_globals.log.debug("Smart IR: pause")
                bpy.ops.thea.pause_ir('INVOKE_DEFAULT')
                if thea_globals.IrIsPaused:
                    self.report({'INFO'}, "IR paused")
                else:
                    self.report({'INFO'}, "IR resumed")
                self.started = True
                return {'FINISHED'}
            else:
                if getattr(context.scene, 'thea_WasExported'):
                    thea_globals.log.debug("Smart IR: reuse")
                    bpy.ops.thea.start_ir('INVOKE_DEFAULT', reuseProp=True)
                    self.report({'INFO'}, "IR Started : Fast")
                    return {'FINISHED'}
                else:
                    thea_globals.log.debug("Smart IR: full")
                    bpy.ops.thea.start_ir('INVOKE_DEFAULT')
                    self.report({'INFO'}, "IR Started : Full")
                    return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):

        thea_globals.log.debug("Smart IR: ivoke")
        #RENDER_PT_thea_startIRSmart.handle_add(self, context)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}




def thea_sceneUpdated(context):
    from . import thea_globals

    #print("scene updated")

def thea_collectUpdatedObjects(context):
    from . import thea_globals


    thea_globals.sceneUpdated = True

    for ob in bpy.data.objects:
        if ob.is_updated or ob.is_updated_data:
#             thea_globals.log.debug("---------------object updated: %s" % ob.name)
            if ob not in thea_globals.objectsUpdated:
                thea_globals.objectsUpdated.append(ob)

def thea_updateIR(con):
     from . import thea_globals



     if not thea_globals.IrIsRunning:
         return

     obList = thea_globals.objectsUpdated
#      for ob in bpy.data.objects:
#          if ob.is_updated:
#              obList.append(ob)

     port = bpy.context.scene.thea_SDKPort
     if (len(obList)>0 or thea_globals.materialUpdated):# and os.times()[4]-bpy.context.scene.thea_lastIRUpdate > 5: #don't refresh too often
         #print("One or more objects were updated!")
         bpy.context.scene.thea_lastIRUpdate = os.times()[4]
         if thea_globals.materialUpdated:
             exportMode = "Material"
             thea_globals.materialUpdated = False
         else:
             exportMode = "Full"


         #thea_globals.preview3DAlpha = 0
         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
         data = sendSocketMsg('localhost', port, b'version')


         if data.find('v'):
             message = b'message "./UI/Viewport/Theme/RW_PROG"'
             data = sendSocketMsg('localhost', port, message)
             if data.find('Ok'):
                 ##print("\n\n***Interactive render started!****\n\n")
                 frame = bpy.context.scene.frame_current
                 frameS= "0000" + str(frame)
                 xmlFilename = currentBlendFile.replace('.blend', '.xml')
                 os.chdir(os.path.dirname(theaPath))
                 exporter=initExporter()
                 #os.chdir(bpy.context.scene.render.filepath)
                 os.chdir(exportPath)
                 area = bpy.context.area
                 bpy.context.scene.thea_Reuse = True
                 currExportAnimation = getattr(bpy.context.scene, 'thea_ExportAnimation')
                 if getattr(bpy.context.scene, 'thea_IRExportAnimation', False):
                    bpy.context.scene.thea_ExportAnimation = True
                 else:
                    bpy.context.scene.thea_ExportAnimation = False
                 args = exportFrame(bpy.context.scene,bpy.context.scene.frame_current,exporter=exporter, area=None, obList=obList, exportMode=exportMode)
                 bpy.context.scene.thea_ExportAnimation = currExportAnimation

                 thea_globals.objectsUpdated = []
                 bpy.context.scene.thea_Reuse = False
#                  message = ('message "Merge %s 4 1 0 1 1 4"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
                 message = ('message "Merge \'%s\' 0 0 0 0 0 4"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
#                  message = ('message "Merge %s 0 0 0 0 0 2"' % os.path.join(exportPath, os.path.basename(xmlFilename))).encode()
                 #print("message: ", message)
                 #return
                 data = sendSocketMsg('localhost', port, message)
                 #print("data: ", data)
                 if data.find('Ok'):
                     #print("Scene merged")
                     if not thea_globals.IrIsPaused:
                         message = b'message "./UI/Viewport/Theme/RW_EARF"'
                         data = sendSocketMsg('localhost', port, message)
                         if data.find('Ok'):
                             #print("\n\n***Interactive render started!****\n\n")
                             return
         else:
             return
