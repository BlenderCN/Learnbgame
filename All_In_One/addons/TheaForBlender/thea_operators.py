"""
.. module:: thea_operators
   :platform: OS X, Windows, Linux
   :synopsis: Operators definitions

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
from bpy.types import Operator

import bpy
import subprocess
import os
import sys
import copy
import time
import struct
from random import random
import platform
from math import *
from . import thea_globals
from TheaForBlender.thea_render_main import *
if os.name == "nt":
    try:
        import winreg
    except:
        thea_globals.log.info("Can't access windows registry")


class THEA_OT_quitBlender(bpy.types.Operator):
    bl_idname = "thea.quit_blender"
    bl_label = "quit Blender"

    def invoke(self, context, event):
        thea_globals.log.info("quit blender")
        try:
            if context.scene.get('thea_SDKPort'):
                port = context.scene.get('thea_SDKPort')
            else:
                port = 30000
        except:
            port = 30000

        data = sendSocketMsg('localhost', port, b'version')
        if data.find('v'):
            message = b'message "exit"'
            data = sendSocketMsg('localhost', port, message)

        try:
            if context.scene.get('thea_PreviewSDKPort'):
                port = context.scene.get('thea_PreviewSDKPort')
            else:
                port = 30001
        except:
            port = 30001

        data = sendSocketMsg('localhost', port, b'version')
        if data.find('v'):
            message = b'message "exit"'
            data = sendSocketMsg('localhost', port, message)

        bpy.ops.wm.quit_blender()
        return {'FINISHED'}


class RENDER_PT_thea_materialsPath(bpy.types.Operator):
    bl_idname = "thea.materials_path"
    bl_label = "Materials Path"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")

    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        bpy.context.scene.thea_materialsPath = FilePath
        ##print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RENDER_PT_thea_makeLUT(bpy.types.Operator):
    bl_idname = "thea.make_lut"
    bl_label = "Generate LUT"

    def invoke(self, context, event):
        global dataPath

        scene = context.scene

        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
        exporter=initExporter()

        import os

        # set paths here
        try:
            searchPath = scene.get('thea_materialsPath')
        except:
            searchPath = os.path.join(dataPath, "Materials")
        if not searchPath:
            searchPath = os.path.join(dataPath, "Materials")

        lutFileName = os.path.join(searchPath, "BlenderTransTable.txt")
        ##print("lutFileName: ", lutFileName)
        try:
            allowOverwrite = scene.get('thea_overwriteLUT')
        except:
            allowOverwrite = False


        allfiles = []
        subfiles = []

        if getattr(scene, 'thea_LUTScanSubdirectories'):
            for root, dirs, files in os.walk(searchPath):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for f in files:
                    if f.endswith('.mat.thea') and not f.startswith('.'):
                        allfiles.append(os.path.join(root, f))
                        #if root != searchPath: # I'm in a subdirectory
                        subfiles.append(os.path.join(root, f))
        else:
             for f in os.listdir(searchPath):
                if f.endswith('.mat.thea') and not f.startswith('.'):
                    allfiles.append(os.path.join(searchPath, f))
                    #if root != searchPath: # I'm in a subdirectory
                    subfiles.append(os.path.join(searchPath, f))
        if len(subfiles) > 0:
            matList = []
            for matFile in sorted(subfiles):
                matList.append((os.path.basename(matFile).split(".mat.thea")[0], matFile))

            if os.path.exists(lutFileName) and not allowOverwrite:
                #print("\n!!\n!!!!!!!!!! File already exist !!!!!!!!\n!!")
                self.report({'ERROR'}, "!!!!!!!!!! File already exist !!!!!!!!\nPlease allow to overwrite the file")
                return {'FINISHED'}
            else:
                trFile = open(lutFileName, "w")
                #print("trFile: ", trFile)
                trFile.write("#Material translation table\n")
                trFile.write("#Blender_name;path/to/Thea/mat/file\n")
                for mat in matList:
                    trFile.write("%s;%s\n" % (mat[0][0:40], mat[1]))

        #print("LUT file generated! Press F8 to reaload LUT into GUI!")
        self.report({'INFO'}, "LUT file generated! Press F8 to reaload LUT into GUI!")
        scene['thea_lutMessage'] = "LUT file generated! Press F8 to reaload LUT into GUI!"

        return {'FINISHED'}


class RENDER_PT_thea_MoreLocations(bpy.types.Operator):
    bl_idname = "thea.morelocations"
    bl_label = "Display more locations"

    def invoke(self, context, event):
        scene = context.scene
        scene.thea_maxLines = int(scene.thea_maxLines)+200
        EnumProperty(   attr="thea_EnvLocationsMenu",
                items=getLocations(scene.thea_maxLines),
                name="Location",
                description="Location",
                default="3")
        return {'FINISHED'}


class RENDER_PT_thea_RenderFrame(bpy.types.Operator):
    bl_idname = "thea.render_frame"
    bl_label = "Render current frame"

    def invoke(self, context, event):
        scene = context.scene
        args = renderFrame(scene, scene.frame_current, anim=False)
        p = subprocess.Popen(args)
        return {'FINISHED'}


class RENDER_PT_thea_RenderAnimation(bpy.types.Operator):
    bl_idname = "thea.render_animation"
    bl_label = "Render animation"

    def invoke(self, context, event):
        scene = context.scene
        renderAnimation(scene)
        return {'FINISHED'}



class RENDER_PT_thea_ExportFrame(bpy.types.Operator):
    bl_idname = "thea.export_frame"
    bl_label = "Export current frame"
    #   CHANGED > Added better description
    bl_description="Save current frame to scn.thea file"

    def invoke(self, context, event):
        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)

        try:
            if bpy.context.active_object.mode != 'OBJECT':
                self.report({'ERROR'}, "Please change to object mode before rendering!")
                return {'FINISHED'}
        except:
            pass
        if len(currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        if not os.path.isdir(exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
#        from TheaForBlender.thea_render_main import checkTheaExtMat
#        if (checkTheaExtMat()==False):
#            self.report({'ERROR'}, "Please check linked materials")
##            thea_globals.log.debug("*** CheckMaterials = %s ***" % checkTheaExtMat())
#            return {'FINISHED'}
        from TheaForBlender.thea_render_main import checkTheaExtMat
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


        exporter=initExporter()
        #print("exporter: ", exporter)
        #print("scene.render.filepath: ",exportPath)
        #os.chdir(scene.render.filepath)
        os.chdir(exportPath)
        scene.thea_startTheaAfterExport = True
        args = exportFrame(scene,scene.frame_current,exporter=exporter)
        #print("args: ", args)
        if not args:
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
#         if scene.get('thea_startTheaAfterExport'):
        p = subprocess.Popen(args)
        del exporter
        return {'FINISHED'}

class RENDER_PT_thea_SaveFrame(bpy.types.Operator):
    '''Save current frame to file'''
    bl_idname = "thea.save_frame"
    bl_label = "Save current frame to file"
#   CHANGED > Added better description
    bl_description = "Save current frame to XML-file"
#    and bpy.context.selected_objects != None
    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
#         #set the string path fo the file here.
#         #this is a variable created from the top to start it
#         bpy.context.scene.thea_mergeFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path
        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)



        if bpy.context.active_object.mode != 'OBJECT':
            self.report({'ERROR'}, "Please change to object mode before exporting!")
            return {'FINISHED'}
        if len(currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        if not os.path.isdir(exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
        from TheaForBlender.thea_render_main import checkTheaExtMat
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


        exporter=initExporter()
        scene.thea_startTheaAfterExport = False
        #print("exporter: ", exporter)
#         #print("scene.render.filepath: ",exportPath)
        #os.chdir(scene.render.filepath)
#         os.chdir(exportPath)
        args = exportFrame(scene,scene.frame_current,exporter=exporter,xmlFile = self.filepath)
        if not args:
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
#         if scene.get('thea_startTheaAfterExport'):
#             p = subprocess.Popen(args)
        del exporter

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_PT_thea_SaveFrame2(bpy.types.Operator):
    bl_idname = "thea.save_frame2"
    bl_label = "Save current frame to file"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")

    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        #bpy.context.scene.thea_mergeFilePath = FilePath


        return {'FINISHED'}



    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)

        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)



        if bpy.context.active_object.mode != 'OBJECT':
            self.report({'ERROR'}, "Please change to object mode before exporting!")
            return {'FINISHED'}
        if len(currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        if not os.path.isdir(exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}


        #print("path: ",self.filepath)#display the file name and current path

        exporter=initExporter()
        #print("exporter: ", exporter)
        #print("scene.render.filepath: ",exportPath)
        #os.chdir(scene.render.filepath)
        os.chdir(exportPath)
        args = exportFrame(scene,scene.frame_current,exporter=exporter)
        if not args:
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
#         if scene.get('thea_startTheaAfterExport'):
#             p = subprocess.Popen(args)
        del exporter
        return {'FINISHED'}


class RENDER_PT_thea_ExportAnim(bpy.types.Operator):
    '''Export animation script'''
    bl_idname = "thea.export_anim"
    bl_label = "Export animation script"

    def invoke(self, context, event):
        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
        if len(currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        if not os.path.isdir(exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}

        exporter=initExporter()
        #print("exporter: ", exporter)
        exportAnim(scene, exporter=exporter)
        del exporter
        return {'FINISHED'}


class RENDER_PT_thea_ExportStillCameras(bpy.types.Operator):
    '''Export visible cameras as animation script'''
    bl_idname = "thea.export_still_cameras"
    bl_label = "Export visible cameras as animation"

    def invoke(self, context, event):

        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
        if len(currentBlendFile)<2:
            self.report({'ERROR'}, "Please save the scene before exporting!")
            return {'FINISHED'}
        if not os.path.isdir(exportPath):
            self.report({'ERROR'}, "Please set proper output path before exporting!")
            return {'FINISHED'}
        exporter=initExporter()
        exportStillCameras(scene, exporter=exporter)
        return {'FINISHED'}


class RENDER_PT_thea_EnableAnimated(bpy.types.Operator):
    '''Set selected objects as animated meshes'''
    bl_idname = "thea.enable_animated"
    bl_label = "Set selected objects as animated meshes"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object['thAnimated'] = True
        return {'FINISHED'}



class RENDER_PT_thea_DisableAnimated(bpy.types.Operator):
    '''Unset selected objects as animated meshes'''
    bl_idname = "thea.disable_animated"
    bl_label = "Unset selected objects as animated meshes"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object['thAnimated'] = False
        return {'FINISHED'}


class RENDER_PT_thea_CausticReceiver(bpy.types.Operator):
    '''Set selected object as caustic receiver'''
    bl_idname = "thea.caustic_receiver"
    bl_label = "Set selected object as caustic receiver"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
#         if object.get('thCausticReceiver') == 0:
#             object['thCausticReceiver'] = 1
#         else:
#             object['thCausticReceiver'] = 0
        object.thCausticReceiver = not object.thCausticReceiver
        return {'FINISHED'}

class RENDER_PT_thea_CausticTransmitter(bpy.types.Operator):
    bl_idname = "thea.caustic_transmitter"
    bl_label = "Set selected object as caustic transmitter"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
        if object.get('thCausticTransmitter') == 0:
            object['thCausticTransmitter'] = 1
        else:
            object['thCausticTransmitter'] = 0
        return {'FINISHED'}

class RENDER_PT_thea_Enabled(bpy.types.Operator):
    bl_idname = "thea.enabled"
    bl_label = "Enable selected object"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
        if object.get('thEnabled') == 0:
            object['thEnabled'] = 1
        else:
            object['thEnabled'] = 0
        return {'FINISHED'}

class RENDER_PT_thea_Hide(bpy.types.Operator):
    bl_idname = "thea.visible"
    bl_label = "Set selected object visible in Thea"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
        if object.get('thVisible') == 0:
            object['thVisible'] = 1
        else:
            object['thVisible'] = 0
        return {'FINISHED'}

class RENDER_PT_thea_ShadowCaster(bpy.types.Operator):
    bl_idname = "thea.shadow_caster"
    bl_label = "Set shadow casting for selected object"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
        if object.get('thShadowCaster') == 0:
            object['thShadowCaster'] = 1
        else:
            object['thShadowCaster'] = 0
        return {'FINISHED'}

class RENDER_PT_thea_ShadowReceiver(bpy.types.Operator):
    bl_idname = "thea.shadow_receiver"
    bl_label = "Set shadow receiving for selected object"

    def invoke(self, context, event):

        scene = context.scene
        object = bpy.context.selected_objects[0]
        if object.get('thShadowReceiver') == 0:
            object['thShadowReceiver'] = 1
        else:
            object['thShadowReceiver'] = 0
        return {'FINISHED'}


class RENDER_PT_thea_EnableCausticReceiver(bpy.types.Operator):
    bl_idname = "thea.enable_caustic_receiver"
    bl_label = "Set selected objects as caustic receiver"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object.thCausticsReceiver = True
        return {'FINISHED'}


class RENDER_OT_thea_DisableCausticReceiver(bpy.types.Operator):
    bl_idname = "thea.disable_caustic_receiver"
    bl_label = "Unset selected objects as caustic receiver"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object.thCausticsReceiver = False
        return {'FINISHED'}


class RENDER_PT_thea_EnableTraceReflections(bpy.types.Operator):
    bl_idname = "thea.enable_trace_reflections"
    bl_label = "Enable trace reflections selected objects materials"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            for obMat in object.material_slots:
                obMat.material.shadow_ray_bias = 0
        return {'FINISHED'}


class RENDER_PT_thea_DisableTraceReflections(bpy.types.Operator):
    bl_idname = "thea.disable_trace_reflections"
    bl_label = "Enable trace reflections selected objects materials"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            for obMat in object.material_slots:
                obMat.material.shadow_ray_bias = 1
        return {'FINISHED'}


class RENDER_PT_thea_EnableAnimationExport(bpy.types.Operator):
    '''Enable animation export for selected objects'''
    bl_idname = "thea.enable_animation_export"
    bl_label = "Enable animation export for selected objects"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object.thExportAnimation = True
        return {'FINISHED'}


class RENDER_PT_thea_DisableCausticReceiver(bpy.types.Operator):
    '''Disable animation export for selected objects'''
    bl_idname = "thea.disable_animation_export"
    bl_label = "Disable animation export for selected objects"

    def invoke(self, context, event):

        scene = context.scene
        for object in bpy.context.selected_objects:
            object.thExportAnimation = False
        return {'FINISHED'}

class MATERIAL_PT_thea_TheaMaterialEditor(bpy.types.Operator):
    '''Edit material in Thea Material Editor'''
    bl_idname = "thea.thea_material_editor"
    bl_label = "Edit material in Thea"

    def invoke(self, context, event):
        scene = context.scene
        exporter=initExporter()
        res = editMaterial(scene,bpy.context.active_object.active_material, exporter=exporter)
        if not res:
            self.report({'ERROR'}, "Please set proper output path before editing material!")
            return {'FINISHED'}
        thea_globals.materialUpdated = True
        return {'FINISHED'}


class MATERIAL_PT_thea_deleteMaterialLink(bpy.types.Operator):
    '''Delete material link'''
    bl_idname = "thea.delete_material_link"
    bl_label = "Delete material link"

    def invoke(self, context, event):
        scene = context.scene
        try:
            del(bpy.context.active_object.active_material['thea_extMat'])
        except:
            pass
        return {'FINISHED'}



# class RENDER_PT_thea_saveIR(bpy.types.Operator):
class MATERIAL_PT_thea_copyMaterialLocally(bpy.types.Operator):
    '''Copy material file to the selected directory'''
    bl_idname = "thea.copy_material_locally"
    bl_label = "Copy material file locally"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")

    def execute(self, context):
        matDir = os.path.dirname(self.filepath)
#         scene = context.scene
#         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
#
#         tempDir = os.path.join(exportPath,"~thexport")
#         if not os.path.isdir(tempDir):
#             os.mkdir(tempDir)
#         matDir = os.path.join(tempDir,"materials")
#         if not os.path.isdir(matDir):
#             os.mkdir(matDir)
        import shutil
        shutil.copy2(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material['thea_extMat'])), matDir)
        bpy.context.active_object.active_material['thea_extMat'] = bpy.path.abspath(os.path.join(matDir, os.path.basename(bpy.context.active_object.active_material['thea_extMat'])))

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
#
# class MATERIAL_PT_thea_copyMaterialLocally(bpy.types.Operator):
#     bl_idname = "thea.copy_material_locally"
#     bl_label = "Copy material file locally"
#
#     def invoke(self, context, event):
#         scene = context.scene
#         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
#
#         tempDir = os.path.join(exportPath,"~thexport")
#         if not os.path.isdir(tempDir):
#             os.mkdir(tempDir)
#         matDir = os.path.join(tempDir,"materials")
#         if not os.path.isdir(matDir):
#             os.mkdir(matDir)
#         import shutil
#         shutil.copy2(os.path.abspath(bpy.path.abspath(bpy.context.active_object.active_material['thea_extMat'])), matDir)
#         bpy.context.active_object.active_material['thea_extMat'] = bpy.path.relpath(os.path.join(matDir, os.path.basename(bpy.context.active_object.active_material['thea_extMat'])))
#         return {'FINISHED'}


class Material_PT_thea_SetLibraryMaterial(bpy.types.Operator):
    '''Set library material'''
    bl_idname = "thea.set_library_material"
    bl_label = "Set library material"

    def invoke(self, context, event):
       lut = getLUTarray()
       mat = context.material
       #print("mat.get('thea_LUT')", mat.get('thea_LUT'))

       if mat.get('thea_LUT') > 0:
           mat.name = lut[mat.get('thea_LUT')]
           mat.use_cubic = True

       return {'FINISHED'}



class MATERIAL_PT_thea_BasicSyncTheaToBlender(bpy.types.Operator):
    '''Sync Basic component to blender material'''
    bl_idname = "thea.sync_basic_to_blender"
    bl_label = "Sync Basic component to blender material"

    def invoke(self, context, event):
        mat = context.material
        mat.raytrace_mirror.use = False
        mat.use_transparency = False
        mat.diffuse_intensity = 0.8
        try:
            mat.specular_color = mat.get('thea_BasicReflectanceCol')
        except:
            mat.specular_color = (0,0,0)
        mat.specular_intensity = 1.0
        mat.specular_shader = "COOKTORR"
        try:
            mat.specular_ior = mat.get('thea_BasicIOR')
        except:
            mat.specular_ior = 1.5
        try:
            mat.specular_hardness = 511 - (mat.get('thea_BasicStructureRoughness') * 5.11)
        except:
            mat.specular_ior = 1.5
        try:
            if mat.get('thea_BasicTrace'):
                mat.shadow_ray_bias = 0.0
            else:
                mat.shadow_ray_bias = 0.2
        except:
            mat.shadow_ray_bias = 0.0
        return {'FINISHED'}

class VIEW3D_MT_RefreshBigPreview(Operator):
    bl_idname = "thea.refresh_big_preview"
    bl_label = "Refresh Big Preview"
    bl_context = "material"

    def execute(self, context):
        mat = context.object.active_material
        return mat

def refreshMatPreview():
    mat = bpy.context.object.active_material
    return mat

class VIEW3D_MT_BigPreview(Operator):
    bl_idname = "thea.big_preview"
    bl_label = "Big Preview"
    bl_context = "material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'PREVIEW'

    sceneLoaded = False
#    COMPAT_ENGINES = set(['THEA_RENDER'])

    heightRand = random()
    height = thea_globals.panelMatHeight

    def draw_header(self, context):
        layout = self.layout
        mat = context.material
        context.object.active_material.diffuse_color = mat.diffuse_color
        layout.label("Big Preview")

#    @classmethod
#    def poll( cls, context):
#        engine = context.scene.render.engine
#        return (engine in cls.COMPAT_ENGINES) and context.object is not None and context.object.active_material is not None and (thea_globals.panelMatPreview is True)
    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC', 'LEFTMOUSE'}:
            self.execute(context)
            return {'CANCELLED'}
        mat = bpy.context.active_object.active_material
        return {"RUNNING_MODAL"}

    def execute(self, context):
        print("Closing big preview")
        thea_globals.panelMatPreview = True
        return {'FINISHED'}

    def cancel(self, context):
        thea_globals.panelMatPreview = True
        self.execute(context)
        thea_globals.log.debug("Closing Big: %s")

    def check(self, context):
        return False


    def invoke(self, context, event):
        thea_globals.panelMatPreview = False
#        thea_globals.materialUpdated = True
        wm = context.window_manager
        print("Invoke big preview")
        return wm.invoke_props_dialog(self, width=800, height=800)

        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material
        col = layout.column()
        thea_globals.log.debug("Active object Big render: %s - Material:%s" % (bpy.context.scene.objects.active, mat))
#        layout.scale_y = 2
        layout.template_preview( refreshMatPreview(), show_buttons=False, preview_id = "thea.big_preview") #  ??? this make render stop and only reernder when
        layout.label(" ")





class RENDER_PT_thea_SyncBlenderToThea(bpy.types.Operator):
    '''Enable basic component for materials without Thea material. To be used with internal render engine materials'''
    bl_idname = "thea.sync_blender_to_thea"
    bl_label = "Enable basic component for materials without Thea material"

    def invoke(self, context, event):
        scene = context.scene
        for object in bpy.data.objects:
            for matSlot in object.material_slots:
                mat = bpy.data.materials[matSlot.name]
                #print("mat: ", mat)
                if mat.get('thea_Basic')!=True and mat.get('thea_Glossy')!=True:
                    #force material preview generation
                    mat.diffuse_color = mat.diffuse_color
                    mat['thea_BasicReflectanceCol'] = mat.specular_color
                    mat['thea_BasicIOR'] = 1.5
                    if mat.specular_hardness == 50:
                        mat['thea_BasicStructureRoughness'] = 25.0
                    else:
                        mat['thea_BasicStructureRoughness'] = (((511.0 - mat.specular_hardness) / 511.0) * 100) / 2
                    if mat.shadow_ray_bias > 0:
                        mat['thea_BasicTrace'] = False
                    else:
                        mat['thea_BasicTrace'] = True
                    #enable all testures to be used with Basic component
                    for tex in mat.texture_slots:
                        try:
                            tex.texture['thea_Basic'] = True
                            if getattr(tex, 'use_map_color_diffuse') and os.path.exists(os.path.abspath(bpy.path.abspath(tex.texture.image.filepath))):
                                mat.thea_BasicDiffuseFilename=tex.texture.image.filepath
                        except:
                            pass

        return {'FINISHED'}



class MATERIAL_PT_thea_BasicSyncBlenderToThea(bpy.types.Operator):
    '''Sync Basic component with blender material'''
    bl_idname = "thea.sync_blender_to_basic"
    bl_label = "Sync Basic component with blender material"

    def invoke(self, context, event):
        mat = context.material
        #force material preview generation
        mat.diffuse_color = mat.diffuse_color
        mat['thea_BasicReflectanceCol'] = mat.specular_color
        mat['thea_BasicIOR'] = mat.specular_ior
        mat['thea_BasicStructureRoughness'] = ((511.0 - mat.specular_hardness) / 511.0) * 100
        if mat.shadow_ray_bias > 0:
            mat['thea_BasicTrace'] = False
        else:
            mat['thea_BasicTrace'] = True
        #enable all testures to be used with Basic component
        for tex in mat.texture_slots:
            try:
                tex.texture['thea_Basic'] = True
                if getattr(tex, 'use_map_color_diffuse') and os.path.exists(os.path.abspath(bpy.path.abspath(tex.texture.image.filepath))):
                    mat.thea_BasicDiffuseFilename=tex.texture.image.filepath
            except:
                pass

        return {'FINISHED'}


def getBSDFDiffuseNode(node):
#     #print("Diffuse node.name: %s, node.type: %s", (node.name, node.type))
    if node.type == 'BSDF_DIFFUSE':
        #print("found: ", node.name)
        return node
    for input in node.inputs:
#         #print("node: %s, input: %s", (node.name, input.name))
        if input.is_linked:
            node = getBSDFDiffuseNode(input.links[0].from_node)
            if node:
                return node
#             if fromNode.type == 'BSDF_DIFFUSE':
#                 #print("found: ", fromNode.name)
#                 return fromNode
#             else:
#                 getBSDFDiffuseNode(fromNode)

def getBSDFGlossyNode(node):
#     #print("Glossy node.name: %s, node.type: %s", (node.name, node.type))
    if node.type == 'BSDF_GLOSSY':
#         #print("found: ", node.name)
        return node
    for input in node.inputs:
        if input.is_linked:
            node = getBSDFGlossyNode(input.links[0].from_node)
            if node:
                return node
#             if fromNode.type == 'BSDF_GLOSSY':
#                 #print("found: ", fromNode.name)
#                 return fromNode
#             else:
#                 getBSDFGlossyNode(fromNode)

def getBSDFGlassNode(node):
#     #print("Glass  node.name: %s, node.type: %s", (node.name, node.type))
    if node.type == 'BSDF_GLASS':
#         #print("found: ", node.name)
        return node
    for input in node.inputs:
        if input.is_linked:
            node = getBSDFGlassNode(input.links[0].from_node)
            if node:
                return node
#             if fromNode.type == 'BSDF_GLASS':
#                 #print("found: ", fromNode.name)
#                 return fromNode
#             else:
#                 getBSDFGlassNode(fromNode)

def getTextureNode(node):
#     #print("Texture  node.name: %s, node.type: %s", (node.name, node.type))
    if node.type == 'TEX_IMAGE':
#         #print("found1: ", node.name)
        return node
    for input in node.inputs:
#         #print("input: ", input)
        if input.is_linked:
            texNode = getTextureNode(input.links[0].from_node)
            if texNode:
                return texNode
#             if fromNode.type == 'TEX_IMAGE':
#                 #print("found2: ", fromNode.name)
#                 return fromNode
#             else:
#                 getTextureNode(fromNode)


class MATERIAL_PT_thea_SyncCyclesToThea(bpy.types.Operator):
    '''Convert cycles materials to Thea materials'''
    bl_idname = "thea.sync_cycles_to_thea"
    bl_label = "Sync material with cycles material"

    def enableTexture(self, mat, node, origin):
#         #print("mat, node, origin: ", mat, node, origin)
        imgName = getattr(mat, origin)
        texName = mat.name+"_"+origin
        exists = False
        try:
            if mat.texture_slots[texName]:
                exists = True
                slot = mat.texture_slots[texName]
                tex = slot.texture
        except:
            pass

        if exists:
            try:
                if imgName:
                    img = bpy.data.images.load(imgName)
                    tex.image = img
                else:
                    #print("removing texture: ", slot, tex)
                    mat.texture_slots[texName].texture = None
            except:
                pass
        else:
            img = bpy.data.images.load(imgName)
            tex = bpy.data.textures.new(name=texName, type='IMAGE')
            tex.image = img
            tex.name = texName
            slot = mat.texture_slots.add()
            slot.texture = tex
            slot.texture_coords='UV'
            if 'Diffuse' in tex.name:
                slot.use_map_color_diffuse=True
            if 'Reflectance' in tex.name:
                slot.use_map_color_spec=True
                slot.use_map_color_diffuse=False
            if 'Basic' in tex.name:
                slot.texture.thea_Basic=True
            if 'Glossy' in tex.name:
                slot.texture.thea_Glossy=True

    def invoke(self, context, event):
        for mat in bpy.data.materials:
#         for object in bpy.data.objects:
# #             object.select = True
# #             bpy.context.scene.objects.active = object
#             s = 0
#             for matSlot in object.material_slots:
#                 mat = bpy.data.materials[matSlot.name]
# #                 object.active_material_index = s
# #                 s += 1
            #print("material: ", mat.name)
#         mat = context.material
    #force material preview generation
            if mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == 'OUTPUT_MATERIAL':
                        outputNode = node
                        if outputNode.inputs['Surface'].is_linked:
                            diffuseNode = getBSDFDiffuseNode(outputNode.inputs['Surface'].links[0].from_node)
                            glossyNode = getBSDFGlossyNode(outputNode.inputs['Surface'].links[0].from_node)
                            glassNode = getBSDFGlassNode(outputNode.inputs['Surface'].links[0].from_node)
                            #print("diffuseNode: ", diffuseNode)
                            #print("glossyNode: ", glossyNode)
                            #print("glassNode: ", glassNode)
                            if diffuseNode:
                                mat.thea_Basic = True
                                #print("diffuseNode: ", diffuseNode.name)
                                texNode = getTextureNode(diffuseNode)
#                                 if diffuseNode.inputs['Color'].is_linked and diffuseNode.inputs['Color'].links[0].from_node.type == 'TEX_IMAGE':
                                if texNode:
                                    #print("texNode: ", texNode.name, texNode.type)
                                    #make texture
#                                     texNode = getDiffuseNode.inputs['Color'].links[0].from_node
                                    try:
                                        mat.thea_BasicDiffuseFilename = texNode.image.filepath
                                        self.enableTexture(mat, texNode, "thea_BasicDiffuseFilename")
                                    except:
                                        pass
                                else:
                                    diffuseColor = diffuseNode.inputs['Color'].default_value
                                    mat.diffuse_color = (diffuseColor[0], diffuseColor[1], diffuseColor[2])
                                if glossyNode:
                                    if glossyNode.inputs['Color'].is_linked and glossyNode.inputs['Color'].links[0].from_node.type == 'TEX_IMAGE':
                                        #make texture
                                        try:
                                            texNode = glossyNode.inputs['Color'].links[0].from_node
                                            mat.thea_BasicReflectanceFilename = texNode.image.filepath
                                        except:
                                            pass
                                    else:
                                        reflectanceColor = glossyNode.inputs['Color'].default_value
                                        mat.thea_BasicReflectanceCol = (reflectanceColor[0], reflectanceColor[1], reflectanceColor[2])
                                    mat.thea_BasicStructureRoughness = glossyNode.inputs['Roughness'].default_value*100
                                    mat.thea_BasicIOR = 1.5
                            else:
                                mat.thea_Basic = False

                            if glossyNode and not diffuseNode:
                                #print("glossyNode: ", glossyNode.name)
                                mat.thea_Glossy = True
                                if glossyNode.inputs['Color'].is_linked and glossyNode.inputs['Color'].links[0].from_node.type == 'TEX_IMAGE':
                                    #make texture
                                    texNode = glossyNode.inputs['Color'].links[0].from_node
                                    mat.thea_GlossyReflectanceFilename = texNode.image.filepath
                                else:
                                    reflectanceColor = glossyNode.inputs['Color'].default_value
                                    mat.thea_GlossyReflectanceCol = (reflectanceColor[0], reflectanceColor[1], reflectanceColor[2])
                                mat.thea_GlossyStructureRoughness = glossyNode.inputs['Roughness'].default_value*100
                                mat.thea_GlossyIOR = 1.5


                            if glassNode:
                                #print("glassNode: ", glassNode.name)
                                mat.thea_Glossy = True
                                if glassNode.inputs['Color'].is_linked and glassNode.inputs['Color'].links[0].from_node.type == 'TEX_IMAGE':
                                    #make texture
                                    texNode = glassNode.inputs['Color'].links[0].from_node
                                    mat.thea_GlossyTransmittanceFilename = texNode.image.filepath
                                else:
                                    transmittanceColor = glassNode.inputs['Color'].default_value
                                    mat.thea_GlossyTransmittanceCol = (transmittanceColor[0], transmittanceColor[1], transmittanceColor[2])
                                mat.thea_GlossyReflectanceCol = (1,1,1)
                                mat.thea_GlossyStructureRoughness = glassNode.inputs['Roughness'].default_value*100
                                mat.thea_GlossyIOR = glassNode.inputs['IOR'].default_value
#             object.select = False
#             bpy.context.scene.objects.active = None

#         mat.diffuse_color = mat.diffuse_color


        return {'FINISHED'}


class MATERIAL_PT_thea_Basic2SyncTheaToBlender(bpy.types.Operator):
    '''Sync second Basic component to blender material'''
    bl_idname = "thea.sync_basic2_to_blender"
    bl_label = "Sync second Basic component to blender material"

    def invoke(self, context, event):
        mat = context.material
        mat.raytrace_mirror.use = False
        mat.use_transparency = False
        mat.diffuse_intensity = 0.8
        mat.diffuse_color = mat.get('thea_Basic2DiffuseCol')
        try:
            mat.specular_color = mat.get('thea_Basic2ReflectanceCol')
        except:
            mat.specular_color = (0,0,0)
        mat.specular_intensity = 1.0
        mat.specular_shader = "COOKTORR"
        try:
            mat.specular_ior = mat.get('thea_Basic2IOR')
        except:
            mat.specular_ior = 1.5
        try:
            mat.specular_hardness = 511 - (mat.get('thea_Basic2StructureRoughness') * 5.11)
        except:
            mat.specular_ior = 1.5
        try:
            if mat.get('thea_Basic2Trace'):
                mat.shadow_ray_bias = 0.0
            else:
                mat.shadow_ray_bias = 0.2
        except:
            mat.shadow_ray_bias = 0.0
        return {'FINISHED'}

class MATERIAL_PT_thea_Basic2SyncBlenderToThea(bpy.types.Operator):
    '''Sync second Basic component with blender material'''
    bl_idname = "thea.sync_blender_to_basic2"
    bl_label = "Sync second Basic component with blender material"

    def invoke(self, context, event):
        mat = context.material
        #force material preview generation
        mat.diffuse_color = mat.diffuse_color
        mat['thea_Basic2DiffuseCol'] = mat.diffuse_color
        mat['thea_Basic2ReflectanceCol'] = mat.specular_color
        mat['thea_Basic2IOR'] = mat.specular_ior
        mat['thea_Basic2StructureRoughness'] = ((511.0 - mat.specular_hardness) / 511.0) * 100
        if mat.shadow_ray_bias > 0:
            mat['thea_Basic2Trace'] = False
        else:
            mat['thea_Basic2Trace'] = True
        return {'FINISHED'}

class MATERIAL_PT_thea_GlossySyncTheaToBlender(bpy.types.Operator):
    '''Sync Glossy component to blender material'''
    bl_idname = "thea.sync_glossy_to_blender"
    bl_label = "Sync Glossy component to blender material"

    def invoke(self, context, event):
        mat = context.material
        mat.specular_color = (0,0,0)
        mat.specular_intensity = 0.0
        mat.specular_shader = "COOKTORR"
        try:
            mat.raytrace_mirror.use = mat.get('thea_GlossyTraceReflections')
        except:
            mat.raytrace_mirror.use = True
        try:
            mat.use_transparency = mat.get('thea_GlossyTraceRefractions')
        except:
            mat.use_transparency = True
        mat.transparency_method = 'RAYTRACE'
        mat.raytrace_mirror.fresnel = 1.0
        mat.raytrace_mirror.reflect_factor = 1.0
        try:
            mat.diffuse_color = mat.get('thea_GlossyTransmittanceCol')
            mat.diffuse_intensity = 0.0
        except:
            mat.diffuse_color = (0,0,0)
        try:
            mat.raytrace_transparency.ior = mat.get('thea_GlossyIOR')
            raytrace_transparency.filter = 1.0
        except:
            mat.raytrace_transparency.ior = 1.5
            mat.raytrace_transparency.filter = 1.0
        try:
            if mat.get('thea_GlossyStructureRoughTrEn'):
                mat.raytrace_transparency.gloss_factor = 1-(mat.get('thea_GlossyStructureRoughnessTr')/100)
            else:
                mat.raytrace_transparency.gloss_factor = 1.0
        except:
            mat.raytrace_transparency.gloss_factor = 1.0
        try:
            mat.mirror_color = mat.get('thea_GlossyReflectanceCol')
        except:
            mat.mirror_color = (0,0,0)
        try:
            mat.raytrace_mirror.fresnel = mat.get('thea_GlossyIOR')
        except:
            mat.raytrace_mirror.fresnel = 1.5
        try:
            mat.raytrace_mirror.gloss_factor = 1-(mat.get('thea_GlossyStructureRoughness')/100)
        except:
            mat.raytrace_transparency.gloss_factor = 0.9

        try:
            if mat.get('thea_GlossyTraceReflections'):
                mat.shadow_ray_bias = 0.0
            else:
                mat.shadow_ray_bias = 0.2
        except:
            mat.shadow_ray_bias = 0.0
        return {'FINISHED'}

class MATERIAL_PT_thea_GlossySyncBlenderToThea(bpy.types.Operator):
    '''Sync Glossy component with blender material'''
    bl_idname = "thea.sync_blender_to_glossy"
    bl_label = "Sync Glossy component with blender material"

    def invoke(self, context, event):
        mat = context.material
        #force material preview generation
        mat.diffuse_color = mat.diffuse_color
        mat['thea_GlossyTransmittanceCol'] = mat.diffuse_color
        mat['thea_GlossyReflectanceCol'] = mat.mirror_color
        mat['thea_GlossyIOR'] = mat.raytrace_mirror.fresnel
        mat['thea_GlossyStructureRoughness'] = (1- mat.raytrace_mirror.gloss_factor) * 100
        mat['thea_GlossyStructureRoughnessTr'] = (1- mat.raytrace_transparency.gloss_factor) * 100
        if mat['thea_GlossyStructureRoughnessTr'] > 0:
            mat['thea_GlossyStructureRoughTrEn'] = True
        if mat.raytrace_mirror.use:
            mat['thea_GlossyTraceReflections'] = True
        else:
            mat['thea_GlossyTraceReflections'] = False
        if mat.use_transparency:
            mat['thea_GlossyTraceRefractions'] = True
        else:
            mat['thea_GlossyTraceRefractions'] = False
        return {'FINISHED'}

class RENDER_PT_thea_syncWithThea(bpy.types.Operator):
    '''Sync selected object transform wih saved Thea scene'''
    bl_idname = "thea.sync_with_thea"
    bl_label = "Sync with Thea for selected objects"

    def invoke(self, context, event):
        scene = context.scene
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
        xmlFilename = currentBlendFile.replace('.blend', '.xml')
        fileName = os.path.join(exportPath, os.path.basename(xmlFilename))
        checkFile = extMat = os.path.exists(fileName)
        if checkFile == False:
            self.report({'ERROR'}, "Please export scene to studio first")
            return {'FINISHED'}
        t1 = datetime.datetime.now()
        f = open(fileName)
        i = 0
        selectedOb = 0
        foundOb = False
#        check = ""
        it = iter(f)
        for obj in bpy.data.objects:
            if obj in bpy.context.selected_objects:
                thea_globals.log.debug("*** Selected Obj: %s" % obj)
                selectedOb +=1
        if selectedOb == 0:
            thea_globals.log.debug("*** Selected Objects Name: %s" % selectedOb)
            self.report({'ERROR'}, "Sync does need selection")
            return {'FINISHED'}
        for line in it:
            i+=1
            thea_globals.log.debug("*** Line: %s" % i)
            if line.find('<Object Identifier="./Models/') >= 0:
#                name = line.split(" ")[3].split('"')[1]
                name = line.split("Name=\"")[0].split('"')[1]
                name = name.replace(name[:9],'')
                ob = scene.objects.get(name)
                thea_globals.log.debug("Model to sync: %s" % name)
                if ob in bpy.context.selected_objects:
                    foundOb = True
            if foundOb and (line.find('<Parameter Name="Frame"') >= 0):
                if ob.type in ['MESH']:
                    thea_globals.log.debug("Model to sync: %s" % ob)
    #                        thea_globals.log.debug("Model to sync: %s" % name)
                    frame_str = line.split('"')[5]
                    frame_arr = frame_str.split(" ")
                    listItems = []
                    thea_globals.log.debug("Model to sync: %s" % frame_str)
                    ob.matrix_world = (float(frame_arr[0]), float(frame_arr[4]), float(frame_arr[8]), 0), (float(frame_arr[1]), float(frame_arr[5]), float(frame_arr[9]), 0), (float(frame_arr[2]), float(frame_arr[6]), float(frame_arr[10]), 0), (float(frame_arr[3]), float(frame_arr[7]), float(frame_arr[11]), 1)
                    foundOb = False
    #                        print (name, " synced")
    #                        synced = name
    #                        if foundOb:
                    self.report({'ERROR'}, "Synced:%s" % name)

            if line.find('<Object Identifier="./Lights/') >=0:
                name = line.split("Name=\"")[0].split('"')[1]
                name = name.replace(name[:9],'')
                ob = scene.objects.get(name)
                lampColor = []
                lampTexProj = ""
                lampTexFile = ""
                lampAtte = ""
                lampWidth = 0
                lampHeight = 0
                lampPower = 0
                lampEfficacy = 0
                lampUnit = 0
                iesFile = ""
                iesTexFile = ""
                iesColor = []
                iesTexProj = ""
                iesMultiplier = ""
                spotColor = []
                spotTexFile = ""
                spotTexProj = ""
                spotAtte = ""
                spotFallOff = ""
                spotHotSpot = ""
                spotPower = ""
                spotEfficacy = ""
                spotUnit = ""
                omniColor = []
                omniTexFile = ""
                omniTexProj = ""
                omniAtte = ""
                omniPower = ""
                omniEfficacy = ""
                omniUnit = ""
                ligthEnable = True
                ligthSun = False
                lightManualSun = False
                ligthShadow = True
                ligthSoftShadow = False
                ligthGlobalPhotons = False
                ligthCausticPhotons = False
                lightMinRays = ""
                lightMaxRays = ""
                ligthLayer = ""
                ligthBuff = ""
                ligthInterF = False
#                thea_globals.log.debug("*** Selected obj in Blender: %s - Name in Thea: %s" % (obj, ob))
                if ob in bpy.context.selected_objects:
                    thea_globals.log.debug("*** Selected Objects Type: %s" % ob.type)
                    line = next(it)
                    if line.find('<Object Identifier="Projector Light')>= 0:
                        line = next(it)
                        foundOb = True
                        ob.data.use_square = True
                        if line.find('<Object Identifier="./Color/Constant Texture')>=0:
                            line = next(it)
                            if line.find('Name="Color"') >=0:
                                lampColor = line.split('"')[5].split(" ")
                                ob.data.color = (float(lampColor[0]),float(lampColor[1]),float(lampColor[2]))
                                ob.data.thea_TextureFilename = ""
                                thea_globals.log.debug("%s Color: %s %s %s" % (ob,lampColor[0],lampColor[1],lampColor[2]))
                        if line.find('<Object Identifier="./Color/Bitmap Texture')>=0:
                            line = next(it)
                            if line.find('Name="Filename"') >=0:
                                lampTexFile = line.split('"')[5]
                                ob.data.thea_TextureFilename = lampTexFile
                                thea_globals.log.debug("%s TexFile: %s" % (name,lampTexFile))
                            line = next(it)
                            if line.find('Name="Projection"') >=0:
                                lampTexProj = line.split('"')[5]
#                                ob.data.thea_TextureFilename = lampTexProj
                                thea_globals.log.debug("%s Projection: %s" % (name,lampTexProj))
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                        line = next(it)
                        line = next(it)
                        if line.find('Name="Attenuation"'):
                            lampAtte = line.split('"')[5]
                            ob.data.thea_EmittanceAttenuation = lampAtte
                            thea_globals.log.debug("%s Attenuation: %s" % (name,lampAtte))
                        line = next(it)
                        if line.find('Name="Width"'):
                            lampWidth = float(line.split('"')[5])
                            ob.data.thea_ProjectorWidth = lampWidth
                            thea_globals.log.debug("Lamp Width: %s" % lampWidth)
                        line = next(it)
                        if line.find('Name="Height"'):
                            lampHeight = float(line.split('"')[5])
                            ob.data.thea_ProjectorHeight = lampHeight
                            thea_globals.log.debug("Lamp Height: %s" % lampHeight)
                        line = next(it)
                        line = next(it)
                        if line.find('Name="Power"'):
                            lampPower = float(line.split('"')[5])
                            ob.data.thea_EmittancePower = lampPower
                            thea_globals.log.debug("Lamp Power: %s" % lampPower)
                        line = next(it)
                        if line.find('Name="Efficacy"'):
                            lampEfficacy = float(line.split('"')[5])
                            ob.data.thea_EmittanceEfficacy = lampEfficacy
                            thea_globals.log.debug("Lamp Efficacy: %s" % lampEfficacy)
                        line = next(it)
                        if line.find('Name="Unit"'):
                            lampUnit = line.split('"')[5]
                            ob.data.thea_EmittanceUnit = lampUnit
                            thea_globals.log.debug("Lamp Power: %s" % lampUnit)

                    if line.find('<Object Identifier="IES Light')>= 0:
                        line = next(it)
                        foundOb = True
                        if line.find('<Object Identifier="./Color/Constant Texture')>=0:
                            line = next(it)
                            if line.find('Name="Color"') >=0:
                                iesColor = line.split('"')[5].split(" ")
                                ob.data.color = (float(iesColor[0]),float(iesColor[1]),float(iesColor[2]))
                                ob.data.thea_TextureFilename = ""
                                thea_globals.log.debug("%s Color: %s %s %s" % (ob,iesColor[0],iesColor[1],iesColor[2]))
                        if line.find('<Object Identifier="./Color/Bitmap Texture')>=0:
                            line = next(it)
                            if line.find('Name="Filename"') >=0:
                                iesTexFile = line.split('"')[5] #.split('"')[1]
                                ob.data.thea_TextureFilename = iesTexFile
                                thea_globals.log.debug("%s TexFile: %s" % (name,iesTexFile))
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                        line = next(it)
                        line = next(it)
                        if line.find('Name="IES File"')>=0:
                            iesFile = line.split('"')[5]
                            if iesFile == "0":
                                ob.data.thea_IESFilename = ""
                            else:
                                ob.data.thea_IESFilename = iesFile
                            thea_globals.log.debug("%s File: %s" % (name,iesFile))
                        line = next(it)
                        line = next(it)
                        if line.find('Name="Multiplier"')>=0:
                            iesMultiplier = float(line.split('"')[5])
                            ob.data.thea_IESMultiplier = iesMultiplier
                            thea_globals.log.debug("%s Multiplier: %s" % (name,iesMultiplier))
                    if line.find('<Object Identifier="Spot Light')>= 0:
                        line = next(it)
                        foundOb = True
                        if line.find('<Object Identifier="./Color/Constant Texture')>=0:
                            line = next(it)
                            if line.find('Name="Color"') >=0:
                                spotColor = line.split('"')[5].split(" ")
                                ob.data.color = (float(spotColor[0]),float(spotColor[1]),float(spotColor[2]))
                                ob.data.thea_TextureFilename = ""
                                thea_globals.log.debug("%s Color: %s %s %s" % (ob,spotColor[0],spotColor[1],spotColor[2]))
                        if line.find('<Object Identifier="./Color/Bitmap Texture')>=0:
                            line = next(it)
                            if line.find('Name="Filename"') >=0:
                                spotTexFile = line.split('"')[5]
                                ob.data.thea_TextureFilename = spotTexFile
                                thea_globals.log.debug("%s TexFile: %s" % (name,spotTexFile))
                            line = next(it)
                            if line.find('Name="Projection"') >=0:
                                spotTexProj = line.split('"')[5]
#                                ob.data.thea_TextureFilename = lampTexProj
                                thea_globals.log.debug("%s Projection: %s" % (name,spotTexProj))
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                        line = next(it)
                        line = next(it)
                        if line.find('Name="Attenuation"'):
                            spotAtte = line.split('"')[5]
                            ob.data.thea_EmittanceAttenuation = spotAtte
                            thea_globals.log.debug("%s Attenuation: %s" % (name,spotAtte))
                        line = next(it)
                        if line.find('Name="Fall Off"'):
                            spotFallOff = float(line.split('"')[5])
                            ob.data.spot_size = spotFallOff / 57.295779
                            thea_globals.log.debug("%s FallOff: %s" % (name, spotFallOff))
                        line = next(it)
                        if line.find('Name="Hot Spot"'):
                            spotHotSpot = float(line.split('"')[5])
                            ob.data.spot_blend = 1-((spotHotSpot/57.295779)/ob.data.spot_size)
                            thea_globals.log.debug("%s Hot Spot: %s" % (name, spotHotSpot))
                        line = next(it)
                        if line.find('Name="Power"'):
                            spotPower = float(line.split('"')[5])
                            ob.data.thea_EmittancePower = spotPower
                            thea_globals.log.debug("%s Power: %s" % (name,spotPower))
                        line = next(it)
                        if line.find('Name="Efficacy"'):
                            spotEfficacy = float(line.split('"')[5])
                            ob.data.thea_EmittanceEfficacy = spotEfficacy
                            thea_globals.log.debug("%s Efficacy: %s" % (name,spotEfficacy))
                        line = next(it)
                        if line.find('Name="Unit"'):
                            spotUnit = line.split('"')[5]
                            ob.data.thea_EmittanceUnit = spotUnit
                            thea_globals.log.debug("%s Unit: %s" % (name,spotUnit))
                    if line.find('<Object Identifier="Omni Light')>= 0:
                        line = next(it)
                        foundOb = True
                        if line.find('<Object Identifier="./Color/Constant Spectrum Texture"')>=0:
                            line = next(it)
                        if line.find('<Object Identifier="./Color/Constant Texture')>=0:
                            line = next(it)
                            if line.find('Name="Color"') >=0:
                                omniColor = line.split('"')[5].split(" ")
                                ob.data.color = (float(omniColor[0]),float(omniColor[1]),float(omniColor[2]))
                                ob.data.thea_TextureFilename = ""
                                thea_globals.log.debug("%s Color: %s %s %s" % (ob,omniColor[0],omniColor[1],omniColor[2]))
                        if line.find('<Object Identifier="./Color/Bitmap Texture')>=0:
                            line = next(it)
                            if line.find('Name="Filename"') >=0:
                                omniTexFile = line.split('"')[5]
                                ob.data.thea_TextureFilename = omniTexFile
                                thea_globals.log.debug("%s TexFile: %s" % (name,omniTexFile))
                            line = next(it)
                            if line.find('Name="Projection"') >=0:
                                omniTexProj = line.split('"')[5]
#                                ob.data.thea_TextureFilename = lampTexProj
                                thea_globals.log.debug("%s Projection: %s" % (name,omniTexProj))
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                            line = next(it)
                        line = next(it)
                        line = next(it)
                        if line.find('Name="Power"'):
#                            omniPower = float(line.split('"')[5])
                            omniPower = float(line.split('"')[5])
                            ob.data.thea_EmittancePower = omniPower
                            thea_globals.log.debug("%s Power: %s" % (name,omniPower))
                        line = next(it)
                        if line.find('Name="Efficacy"'):
                            omniEfficacy = float(line.split('"')[5])
                            ob.data.thea_EmittanceEfficacy = omniEfficacy
                            thea_globals.log.debug("%s Efficacy: %s" % (name,omniEfficacy))
                        line = next(it)
                        if line.find('Name="Unit"'):
#                            thea_globals.log.debug("OMNI type in blender: %s" % ob.data.type)
                            omniUnit = line.split('"')[5]
                            if ob.data.type in ('POINT'):
                                ob.data.thea_EmittanceUnit = omniUnit
                            if ob.data.type in ('AREA'):
                                ob.data.thea_EmittanceUnit = omniUnit
                            else:
                                ob.data.thea_SunEmittanceUnit = omniUnit
                            thea_globals.log.debug("%s Unit: %s" % (name,omniUnit))
                        line = next(it)
                        if line.find('Name="Attenuation"'):
                            omniAtte = line.split('"')[5]
                            if ob.data.type in ('POINT'):
                                ob.data.thea_EmittanceAttenuation = omniAtte
                            if ob.data.type in ('AREA'):
                                ob.data.thea_EmittanceAttenuation = omniAtte
                            else:
                                ob.data.thea_SunAttenuation = omniAtte
                            thea_globals.log.debug("%s Attenuation: %s" % (name,omniAtte))
                    line = next(it)
                    line = next(it)
                    if line.find('Name="Enabled"')>=0:
                        lightEnabled = line.split('"')[5]
                        if lightEnabled == "1":
                            ob.thEnabled = True
                            ob.data.thea_enableLamp = True
                        else:
                            ob.thEnabled = False
                            ob.data.thea_enableLamp = False
                        thea_globals.log.debug("%s Enables: %s" % (name,lightEnabled))
                    line = next(it)
#                    if line.find('Name="Sun"')>=0:
#                            lightSun = line.split('"')[5]
#                            if lightEnabled == "1":
#                                ob.thEnabled = True
#                            else:
#                                ob.thEnabled = False
#                            thea_globals.log.debug("%s File: %s" % (name,lightEnabled))
                    line = next(it)
                    if line.find('Name="Manual Sun"')>=0:
                        lightManualSun = line.split('"')[5]
                        if lightManualSun == "1":
                            ob.data.thea_manualSun = True
                        else:
                            ob.data.thea_manualSun = False
                        thea_globals.log.debug("%s Manual Sun: %s" % (name,lightManualSun))
                    line = next(it)
                    if line.find('Name="Shadow"')>=0:
                        lightShadow = line.split('"')[5]
                        if lightShadow == "1":
                            ob.data.thea_enableShadow = True
                        else:
                            ob.data.thea_enableShadow = False
                        thea_globals.log.debug("%s Shadow: %s" % (name,lightShadow))
                    line = next(it)
                    if line.find('Name="Soft Shadow"')>=0:
                        lightSoftShadow = line.split('"')[5]
                        if lightSoftShadow == "1":
                            ob.data.thea_enableSoftShadow = True
                        else:
                            ob.data.thea_enableSoftShadow = False
                        thea_globals.log.debug("%s Soft Shadow: %s" % (name,lightSoftShadow))
                    line = next(it)
                    if line.find('Name="Negative Light"')>=0:
                        lightNegativeLight = line.split('"')[5]
#                            if lightNegativeLight == "1":
##                                ob.data.thea_enableSoftShadow = True
#                            else:
##                                ob.data.thea_enableSoftShadow = False
                        thea_globals.log.debug("%s Negative Light: %s" % (name,lightNegativeLight))
                    line = next(it)
                    if line.find('Name="Global Photons"')>=0:
                        lightGlobalPhotons = line.split('"')[5]
                        if lightGlobalPhotons == "1":
                            ob.data.thea_globalPhotons = True
                        else:
                            ob.data.thea_globalPhotons = False
                        thea_globals.log.debug("%s Global Photons: %s" % (name,lightGlobalPhotons))
                    line = next(it)
                    if line.find('Name="Caustic Photons"')>=0:
                        lightCausticPhotons = line.split('"')[5]
                        if lightCausticPhotons == "1":
                            ob.data.thea_causticPhotons = True
                        else:
                            ob.data.thea_causticPhotons = False
                        thea_globals.log.debug("%s Caustics Photons: %s" % (name,lightCausticPhotons))
                    line = next(it)
                    if line.find('Name="Frame')>=0:
                        frame_str = line.split('"')[5]
                        frame_arr = frame_str.split(" ")
                        listItems = []
                        if ob.type in ('LAMP') and ob:
                            ob.matrix_world = (float(frame_arr[0]), float(frame_arr[4]), float(frame_arr[8]), 0), (float(frame_arr[1])*-1, float(frame_arr[5])*-1, float(frame_arr[9])*-1, 0), (float(frame_arr[2])*-1, float(frame_arr[6])*-1, float(frame_arr[10])*-1, 0), (float(frame_arr[3]), float(frame_arr[7]), float(frame_arr[11]), 1)
        #                    listItems.append(name)
#                            print (name, " synced")
                            self.report({'ERROR'}, "Synced:%s" % name)
                            foundOb = False

#                            synced = name
#                            foundOb = True
                    line = next(it) # SKIP FRAME already done
                    line = next(it) # SKIP Focal Frame not sure why this is???
                    if line.find('Name="Radius Multiplier')>=0:
                        lightRadiusMulitplier = float(line.split('"')[5])
                        ob.data.thea_radiusMultiplier = lightRadiusMulitplier
                        thea_globals.log.debug("%s Radius Multiplier: %s" % (name,lightRadiusMulitplier))
                    line = next(it)
                    if line.find('Name="Radius')>=0:
                        lightRadius = float(line.split('"')[5])
                        ob.data.thea_softRadius = lightRadius
                        thea_globals.log.debug("%s Radius: %s" % (name,lightRadius))
                    line = next(it)
                    if line.find('Name="Min')>=0:
                        lightMinRays = float(line.split('"')[5])
                        ob.data.thea_minRays = lightMinRays
                        thea_globals.log.debug("%s Min Rays: %s" % (name,lightMinRays))
                    line = next(it)
                    if line.find('Name="Max')>=0:
                        lightMaxRays = float(line.split('"')[5])
                        ob.data.thea_maxRays = lightMaxRays
                        thea_globals.log.debug("%s Max Rays: %s" % (name,lightMaxRays))
                    line = next(it)
                    if line.find('Name="Layer')>=0:
                        lightLayer = int(line.split('"')[5])
                        ob.layers[lightLayer] = True
                        for i in range(20):
                            ob.layers[i] = (i == lightLayer)
                        thea_globals.log.debug("%s Layer: %s" % (name,lightLayer))
                    line = next(it)
                    if line.find('Name="Light Buffer Index')>=0:
                        lightLightBuffer = float(line.split('"')[5])
                        ob.data.thea_bufferIndex = lightLightBuffer
                        thea_globals.log.debug("%s Light Buffer Index: %s" % (name,lightLightBuffer))
                    line = next(it)
                    if line.find('Name="Interface Appearance"')>=0:
                        lightInterference = line.split('"')[5]
#                        ob.thea_Container[lightInterference]
                        try:
                            setattr(ob,"thea_Container",lightInterference)
                        except:
                            pass
                        thea_globals.log.debug("%s Interference: %s" % (name,lightInterference))
#                    line = next(it)
            if line.find('<Object Identifier="./Cameras/') >= 0:
                name = line.split("Name=\"")[0].split('"')[1]
                name = name.replace(name[:10],'')
                ob = scene.objects.get(name)
                if ob in bpy.context.selected_objects:
                    foundOb = True
                    line = next(it)
                    if line.find('Focal Length'):
                        camFocalLength = float(line.split(" ")[5].split('"')[1])
        #                        camFocalLength = line.split(" ")[5].split('"')[1]
                        ob.data.lens = camFocalLength
                        line = next(it)
                    if line.find('Film Height') >= 0:
                        camFilmHeight = float(line.split(" ")[5].split('"')[1])
                        if ob.data.sensor_fit in {'VERTICAL'}:
                           ob.data.sensor_height = camFilmHeight
                        if ob.data.sensor_fit in {'HORIZONTAL' and 'AUTO'}:
                           ob.data.sensor_height = camFilmHeight

                    line = next(it)
                    if line.find('Shift X') >= 0:
                        camShiftX = float(line.split(" ")[5].split('"')[1])
        #                        ob.data.shift_x = camShiftX
                    line = next(it)
                    if line.find('Shift Y') >= 0:
                        camShiftY = float(line.split(" ")[5].split('"')[1])
        #                        ob.data.shift_y = camShiftY
                    line = next(it)
                    if line.find('Resolution'):
                        camResolution = (line.split(" ")[3].split('"')[1])
                        camRatio = camResolution.split("x")
                        if camRatio[0] > camRatio[1]:
                            fac = float(camRatio[0]) / float(camRatio[1])
                        else:
                            fac = 1
                        ob.data.sensor_width = camFilmHeight * fac
                        ob.data.shift_x  = float(camShiftX) / ob.data.sensor_width
                        ob.data.shift_y  = float(camShiftY) / ob.data.sensor_width  * -1
                    line = next(it)
                    if line.find('Frame'):
#                        camFrame = line.split('"')[5]
#                        foundOb = True
                        frame_str = line.split('"')[5]
                        frame_arr = frame_str.split(" ")
                        listItems = []
                        if ob.type in ('CAMERA') and ob:
                            ob.matrix_world = (float(frame_arr[0]), float(frame_arr[4]), float(frame_arr[8]), 0), (float(frame_arr[1])*-1, float(frame_arr[5])*-1, float(frame_arr[9])*-1, 0), (float(frame_arr[2])*-1, float(frame_arr[6])*-1, float(frame_arr[10])*-1, 0), (float(frame_arr[3]), float(frame_arr[7]), float(frame_arr[11]), 1)
                            self.report({'ERROR'}, "Synced:%s" % name)
                            foundOb = False
#                            synced = name
#                        thea_globals.log.debug("Frame found: %s" % camFrame)
                    line = next(it)
                    if line.find('Focus Distance') >= 0:
                        camFocusDistance = float(line.split(" ")[4].split('"')[1])
                        ob.data.dof_distance = camFocusDistance
                    line = next(it)
                    if line.find('Shutter Speed') >= 0:
                        camShutterSpeed = float(line.split(" ")[4].split('"')[1])
                        ob.shutter_speed = camShutterSpeed
                    line = next(it)
                    if line.find('f-number'):
                        camFNumber = line.split('"')[-2]
                        if camFNumber == 'Pinhole':
                            ob.thea_pinhole = True
                            thea_globals.log.debug("*** OB2: %s" % camFNumber)
                        else:
                            camFNumber = float(camFNumber)
                            thea_globals.log.debug("*** OB2: %s" % camFNumber)
                            ob.aperture = camFNumber
                            ob.thea_pinhole = False

                    line = next(it)
                    if line.find('Depth of Field') >= 0:
                        camDOF = float(line.split(" ")[5].split('"')[1])
                        ob.thea_DOFpercentage = camDOF
                    line = next(it)
                    if line.find('Blades'):
                        camBlades = float(line.split(" ")[3].split('"')[1])
                        ob.thea_diapBlades = camBlades
                    line = next(it)
                    if line.find('Diaphragm"'):
                        camDiaph = line.split(" ")[3].split('"')[1]
                        ob.thea_diaphragma = camDiaph
                    line = next(it)
                    if line.find('Projection"'):
                        camProjec = line.split(" ")[3].split('"')[1]
        #                        if camProjec == "Perspective":
                        ob.thea_projection = camProjec
                        ob.data.type = "PERSP"
                        if camProjec == "Parallel":
                            ob.data.type = "ORTHO"
#                                    ob.data.ortho_scale = camFocalLength * .0001 # OLD SCALE VALUE
#                            ob.data.ortho_scale = camFocalLength * .0001 # NEW CALCULATION - slight mismatch though
                            if ob.data.sensor_fit == 'VERTICAL':
                                ob.data.ortho_scale = camFilmHeight * .001 # NEW CALCULATION - slight mismatch though
                            if ob.data.sensor_fit == 'HORIZONTAL' or 'AUTO':
                                ob.data.ortho_scale = camfilmHeight * .001 * ratio #NEW horizontal and vertical differnce calculation
                            ob.data.shift_x = 0
                            ob.data.shift_y = 0
        #                        elif: camProjec == "Cylindrical"
        #                            ob.data.type =
                    line = next(it)
                    if line.find('Auto-Focus'):
                        camAutoFocus = line.split(" ")[3].split('"')[1]
                        if camAutoFocus == "1":
                            ob.autofocus = True
                        else:
                            ob.autofocus = False
                    line = next(it) # SKIP DOF LOCK
                    line = next(it) # SKIP CURRENT VIEW
                    line = next(it) # SKIP LOCK CAMERA TRANSFORM
                    line = next(it) # SKIP ROLL LOCK BOOL
                    line = next(it) # SKIP UPWARDS ???? BOOL
                    line = next(it) # SKIP REGION MATRIX
                    line = next(it) # SKIP REGION BOOL
                    line = next(it) # INTERFERENCE
                    line = next(it)
                    if line.find('Z-Clipping Near'):
                        zClipNear = line.split(" ")[4].split('"')[1]
                        if zClipNear == "1":
                            ob.thea_zClippingNear = True
                        else:
                            ob.thea_zClippingNear = False
                    line = next(it)
                    if line.find('Z-Clipping Far'):
                        zClipFar = line.split(" ")[4].split('"')[1]
                        if zClipFar == "1":
                            ob.thea_zClippingFar = True
                        else:
                            ob.thea_zClippingFar = False
                    line = next(it)
                    if line.find('Z-Clipping Near Distance'):
                        zClipNearDistance = float(line.split(" ")[5].split('"')[1])
                        ob.data.clip_start = zClipNearDistance
                    line = next(it)
                    if line.find('Z-Clipping Near Distance'):
                        zClipNearDistance = float(line.split(" ")[5].split('"')[1])
                        ob.data.clip_end = zClipNearDistance

                    obCam = bpy.data.objects[name].name
                    line = next(it)
##            thea_globals.log.debug("*** Selected Objects Name: %s" % selectedOb)
#            if foundOb and (line.find('Frame') >= 0):
#                frame_str = line.split('"')[5]
#                frame_arr = frame_str.split(" ")
#                listItems = []
#                ob.matrix_world = (float(frame_arr[0]), float(frame_arr[4]), float(frame_arr[8]), 0), (float(frame_arr[1]), float(frame_arr[5]), float(frame_arr[9]), 0), (float(frame_arr[2]), float(frame_arr[6]), float(frame_arr[10]), 0), (float(frame_arr[3]), float(frame_arr[7]), float(frame_arr[11]), 1)
#                print (name, " synced")
#                foundOb = False
#                selectedOb += 1


        f.close()
#        f.close()
        t2 = datetime.datetime.now()
        totalTime = t2-t1
        minutes = totalTime.seconds/60
        seconds = totalTime.seconds%60
        microseconds = totalTime.microseconds%1000000
        result = "%d:%d.%d" %(minutes, seconds,(microseconds/1000))
        thea_globals.log.debug("Sync time from Thea XML: %s > %s sec" % (name, result))
        return {'FINISHED'}



class RENDER_PT_thea_mergeFile(bpy.types.Operator):
    '''Select Thea scnene to merge'''
    bl_idname = "thea.merge_file"
    bl_label = "Merge Thea Scene"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        bpy.context.scene.thea_mergeFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_PT_thea_IBLFile(bpy.types.Operator):
    bl_idname = "thea.ibl_file"
    bl_label = "IBL filename"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
        bpy.context.scene.thea_IBLFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_PT_thea_BackgroundMappingFile(bpy.types.Operator):
    bl_idname = "thea.backgroundmapping_file"
    bl_label = "Background Mapping filename"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        bpy.context.scene.thea_BackgroundMappingFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_PT_thea_ReflectionMappingFile(bpy.types.Operator):
    bl_idname = "thea.reflectionmapping_file"
    bl_label = "Reflection Mapping filename"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        bpy.context.scene.thea_ReflectionMappingFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_PT_thea_RefractionMappingFile(bpy.types.Operator):
    bl_idname = "thea.refractionmapping_file"
    bl_label = "Refraction Mapping filename"

    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")



    def execute(self, context):
        FilePath = self.filepath
        #set the string path fo the file here.
        #this is a variable created from the top to start it
        bpy.context.scene.thea_RefractionMappingFilePath = FilePath
        #print("path: ",FilePath)#display the file name and current path

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

#class RENDER_PT_thea_updateLoc(bpy.types.Operator):
#    bl_idname = "thea.update_loc"
#    bl_label = "Update location"
#
#
#
#    def invoke(self, context, event):
#       scene = context.scene
#       loc = getLocation(scene.thea_EnvLocationsMenu, getLocations2(), scene)
#       if loc[0] != "":
#           scene.thea_EnvLat = loc[0]
#           scene.thea_EnvLong = loc[1]
#           scene.thea_EnvTZ = str(loc[2])
#       return {'FINISHED'}

class RENDER_PT_thea_RefreshRender(bpy.types.Operator):
    bl_idname = "thea.refresh_render"
    bl_label = "Refresh render result"

    def invoke(self, context, event):
        thea_globals.displayUpdated = True
        #print("refresh")
        return {'FINISHED'}

# class RENDER_PT_thea_StartInteractiveRender(bpy.types.Operator):
#     bl_idname = "thea.start_irender"
#     bl_label = "Refresh render result"
#
#     def invoke(self, context, event):
#         bpy.ops.thea.start_ir()
#         #print("refresh")
#         return {'FINISHED'}

class MATERIAL_PT_thea_checkTheaExtMat(bpy.types.Operator):
    '''check if Thea linked materials are live
        :return: False if missing link
        :rtype: bool
    '''
    bl_idname = "thea.check_thea_mat"
    bl_label = "Show missing linked materials list"

    def invoke(self, context, event):
        missing_Materials = []
        matNameExt = ""
        matMesh = ""
        missing_Mat = ""
#        matExtLink = True
        for mat in bpy.data.materials:
            if getattr(mat, "thea_extMat"):
                extMat = os.path.exists(os.path.abspath(bpy.path.abspath(mat.get('thea_extMat'))))
                if extMat == False:
                    matNameExt = mat.name
                    MNAME = matNameExt
                    obs = []
                    for o in bpy.data.objects:
                        if isinstance(o.data, bpy.types.Mesh) and MNAME in o.data.materials:
                            matMesh = o.name
                    missing_Materials.append("%s > Mesh obj: %s" % (matNameExt, matMesh))
#                    missing_Materials += matNameExt + "> Mesh obj:"+ matMesh+"\n"
#                    missing_Materials = matNameExt + "\n"
    #                return [matExtLink, matNameExt, matMesh]
                else:
                    pass
            missing_Materials = sorted(list(set(missing_Materials)))

        for mat in missing_Materials:
            missing_Mat = missing_Mat+"\n"+mat

        self.report({'ERROR'}, "Please link Material:%s" % missing_Mat)
        return {'FINISHED'}


class MATERIAL_PT_thea_listLinkedMaterials(bpy.types.Operator):
    '''List materials using the same Thea material file'''
    bl_idname = "thea.list_linked_materials"
    bl_label = "List materials using the same Thea material file"

    def invoke(self, context, event):
        mat = bpy.context.scene.objects.active.active_material
        materials = "Materials using the same Thea material file: \n"
        if len(getattr(mat, "thea_extMat"))>5:
            for m in bpy.data.materials:
                if getattr(mat, "thea_extMat") == getattr(m, "thea_extMat"):
                    materials+=m.name+"\n"

        #print("materials: ", materials)
        self.report({'ERROR'}, materials)
        return {'FINISHED'}


class RENDER_PT_thea_saveIR(bpy.types.Operator):
    '''Save IR result'''
    bl_idname = "thea.save_ir"
    bl_label = "Save IR result"
    filepath = bpy.props.StringProperty(name="file path", description="getting file path", maxlen= 1024, default= "")

    def execute(self, context):
        FilePath = self.filepath
#        CHANGED > Added string below, was missing and took from old part
        scn = context.scene
#       CHANGED > Strips .blend from file name when saving
        FilePath = FilePath[:-6]
        if FilePath[-4:] not in (".jpg", ".png", ".bmp", ".hdr", ".ext", ".tif"):
            fileFormat = ".png"
            color_mode = scn.render.image_settings.color_mode
            if context.scene.render.image_settings.file_format == "JPEG":
                fileFormat = ".jpg"
            if context.scene.render.image_settings.file_format == "PNG":
                fileFormat = ".png"
            if context.scene.render.image_settings.file_format == "BMP":
                fileFormat = ".bmp"
            if context.scene.render.image_settings.file_format == "HDR":
                fileFormat = ".hdr"
            if context.scene.render.image_settings.file_format == "OPEN_EXR":
                fileFormat = ".exr"
            if context.scene.render.image_settings.file_format == "TIFF":
                fileFormat = ".tif"
        else:
            fileFormat = ""

        if context.scene.thea_ir_running == True:
            try:
                if context.scene.get('thea_SDKPort'):
                    port = context.scene.get('thea_SDKPort')
                else:
                    port = 30000
                #if context.scene.get('thea_RefreshDelay'):
                #    self.DELAY = context.scene.get('thea_RefreshDelay')
            except:
                port = 30000

            data = sendSocketMsg('localhost', port, b'version')
            if data.find('v'):

#                 outputImage = os.path.join(exportPath, os.path.basename(FilePath) + fileFormat)
                outputImage = os.path.join(os.path.dirname(FilePath), os.path.basename(FilePath) + fileFormat)
                #print("outputImage: ", outputImage)
                message = 'message "./UI/Viewport/SaveImage %s"' % outputImage
                #print("message: ", message)
                data = sendSocketMsg('localhost', port, message.encode())
                #print("data: ", data, data.find('Ok'))
                if data.find('Ok')>0:
                    self.report({'INFO'}, "File %s saved" % outputImage)
                else:
                    self.report({'ERROR'}, "Error while saving file!")
            else:
                self.report({'ERROR'}, "Error while saving file!")

        #print("path: ",FilePath)#display the file name and current path
        thea_globals.log.debug("FilePath: %s" % FilePath)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


#     def invoke(self, context, event):
#
#         (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(context.scene)
#         scn = context.scene
#
#         fileFormat = ".png"
#         color_mode = scn.render.image_settings.color_mode
#
#
#         if scn.render.image_settings.file_format == "JPEG":
#             fileFormat = ".jpg"
#         if scn.render.image_settings.file_format == "PNG":
#             fileFormat = ".png"
#         if scn.render.image_settings.file_format == "BMP":
#             fileFormat = ".bmp"
#         if scn.render.image_settings.file_format == "HDR":
#             fileFormat = ".hdr"
#         if scn.render.image_settings.file_format == "OPEN_EXR":
#             fileFormat = ".exr"
#         if scn.render.image_settings.file_format == "TIFF":
#             fileFormat = ".tif"
#
#         if context.scene.thea_ir_running == True:
#             try:
#                 if context.scene.get('thea_SDKPort'):
#                     port = context.scene.get('thea_SDKPort')
#                 else:
#                     port = 30000
#                 #if context.scene.get('thea_RefreshDelay'):
#                 #    self.DELAY = context.scene.get('thea_RefreshDelay')
#             except:
#                 port = 30000
#
#             data = sendSocketMsg('localhost', port, b'version')
#             if data.find('v'):
#                 imageFilename = currentBlendFile.replace('.blend', '_ir_result')
#                 outputImage = os.path.join(exportPath, os.path.basename(imageFilename) + fileFormat)
#                 #print("outputImage: ", outputImage)
#                 message = 'message "./UI/Viewport/SaveImage %s"' % outputImage
#                 #print("message: ", message)
#                 data = sendSocketMsg('localhost', port, message.encode())
#                 #print("data: ", data, data.find('Ok'))
#                 if data.find('Ok')>0:
#                     self.report({'INFO'}, "File %s saved" % outputImage)
#                 else:
#                     self.report({'ERROR'}, "Error while saving file!")
#             else:
#                 self.report({'ERROR'}, "Error while saving file!")
#
#         return {'FINISHED'}

class RENDER_PT_thea_installTheaStudio(bpy.types.Operator):
    bl_idname = "thea.install_thea_studio"
    bl_label = "Install Thea Studio"

    def invoke(self, context, event):
        import webbrowser
        url = "http://thearender.com/studio"
        webbrowser.open(url)
        return {'FINISHED'}


class MATERIAL_PT_thea_refreshDiffuseColor(bpy.types.Operator):
    '''Refresh diffuse color from mat.thea file'''
    bl_idname = "thea.refresh_diffuse_color"
    bl_label = "Refresh diffuse color from mat.thea file"

    def invoke(self, context, event):
        updateActiveMaterialColor()
        return {'FINISHED'}


class LAMP_PT_thea_refreshLamp(bpy.types.Operator):
    bl_idname = "thea.refresh_lamp"
    bl_label = "Refresh lamp data"

    def invoke(self, context, event):
        thea_globals.lampUpdated = True
        return {'FINISHED'}

def item_iorMenu(self, context):
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
#            ior.append((entry,os.path.join(dataPath,"ior",entry)))
            iorMenuItems.append((str(i),entry[:-4],""))
            i+=1
#            thea_globals.log.debug("*** IORmenu Items: %s" % iorMenuItems)

    return iorMenuItems
#    return [(str(i), "Item %i" % i, "") for i in range(100)]


class glossyIORmenu(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "glossy.iormenu"
    bl_label = "IOR Menu 1"
    bl_property = "my_enum"
    bl_description = "Quick search for IOR files"
#    my_enum = bpy.props.EnumProperty(items=item_cb)
    my_enum = bpy.props.EnumProperty(items=item_iorMenu)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material


    def execute(self, context):
        mat = context.material
#        self.report({'INFO'}, "Selected: %s" % self.my_enum)
        item = self.my_enum
#        thea_globals.log.debug("*** IORmenu Items: %s" % item)
        try:
            bpy.data.materials[setattr(mat,"thea_GlossyIORMenu", item)]
        except:
            pass
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

class glossy2IORmenu(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "glossy2.iormenu"
    bl_label = "IOR Menu 2"
    bl_property = "my_enum"
    bl_description = "Quick search for IOR files"
#    my_enum = bpy.props.EnumProperty(items=item_cb)
    my_enum = bpy.props.EnumProperty(items=item_iorMenu)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material


    def execute(self, context):
        mat = context.material
#        self.report({'INFO'}, "Selected: %s" % self.my_enum)
        item = self.my_enum
#        thea_globals.log.debug("*** IORmenu Items: %s" % item)
        try:
            bpy.data.materials[setattr(mat,"thea_Glossy2IORMenu", item)]
        except:
            pass
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
#        invoke_props_dialog(self, 800, 550)
        return {'FINISHED'}

def item_lutMenu(self, context):
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


class theaLUTmenu(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "thea.lutmenu"
    bl_label = "LUT menu search"
    bl_property = "my_lut"
    bl_description = "Quick search in LUT library"
#    my_enum = bpy.props.EnumProperty(items=item_cb)
    my_lut = bpy.props.EnumProperty(items=item_lutMenu)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material


    def execute(self, context):
        mat = context.material
#        self.report({'INFO'}, "Selected: %s" % self.my_enum)
        item = self.my_lut
#        thea_globals.log.debug("*** IORmenu Items: %s" % item)
        try:
            bpy.data.materials[setattr(mat,"thea_LUT", item)]
        except:
            pass
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

#def item_locMenu(self, context):
#    '''Get locations names and coordinates from locations.txt file
#
#        :return: tuple with menu entries and list with locations.txt content required for mapping
#        :rtype: ([(str,str,str)], [str])
#    '''
#    maxLines = 1200
#    locationMenuItems = []
##    EnvLocationsArr = []
#
#    locationMenuItems.append(("0","",""))
##    EnvLocationsArr.append("")
##     else:
##         #print("dataPath: %s" % dataPath)
#    #locPath = os.path.join(dataPath,"Locations","locations.txt")
#
#    locPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locations.txt")
#    try:
#        file = open(locPath)
#    except:
#        file = False
#    #print("locations file: ",locPath)
#    if file:
#        #print("locations found")
#        l = 0
#        for line in file:
#            if l>0 and l<maxLines:
#                locationMenuItems.append((str(l-1),line[:34].strip(),""))
##                EnvLocationsArr.append(line)
#            l+=1
#
#    return locationMenuItems
from TheaForBlender.thea_render_main import getLocMenu

class thea_location_search(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "thea.location_search"
    bl_label = "Locations menu search"
    bl_property = "my_locations"
    bl_description = "Quick search in Locations Menu"
#    my_enum = bpy.props.EnumProperty(items=item_cb)
#    items = []
#    items.append(("0","",""))
    my_locations = bpy.props.EnumProperty(items=getLocMenu())

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mat = context.material


    def execute(self, context):
        mat = context.material
#        self.report({'INFO'}, "Selected: %s" % self.my_enum)
        item = self.my_locations
#        thea_globals.log.debug("*** IORmenu Items: %s" % item)
        try:
            setattr(bpy.data.scenes["Scene"],"thea_EnvLocationsMenu", item)
            setattr(bpy.data.scenes["Scene"],"thea_Envlocation", getLocMenu()[int(getattr(bpy.context.scene, "thea_EnvLocationsMenu"))][1])

#            bpy.data.scenes[setattr(scene,"thea_EnvLocationsMenu", item)]
#            bpy.data.scenes[setattr(scene,"thea_EnvLocationsMenu", item)]
        except:
            pass
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

#def item_displayMenu(self, context):
#    displayMenuItems = []
#    displayMenuItems.append(("0","None",""))
#    sceneLoaded = False
#    try:
#        if bpy.context.scene:
#            sceneLoaded = True
#    except:
#        pass
#    if sceneLoaded:
#        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)
#    else:
#        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene=None)
#    ior = []
#    if len(dataPath ) > 5:
#        i = 2
#        for entry in sorted(os.listdir(os.path.join(dataPath,"display"))):
##            ior.append((entry,os.path.join(dataPath,"ior",entry)))
#            displayMenuItems.append((str(i),entry[:-4],""))
#            i+=1
##            thea_globals.log.debug("*** IORmenu Items: %s" % iorMenuItems)
#
#    return displayMenuItems
##    return [(str(i), "Item %i" % i, "") for i in range(100)]
#
#
#class Displaymenu(bpy.types.Operator):
#    """Tooltip"""
#    bl_idname = "display.menu"
#    bl_label = "Display Menu"
#    bl_property = "my_enum"
#    bl_description = "Quick search for Display files"
##    my_enum = bpy.props.EnumProperty(items=item_cb)
#    my_enum = bpy.props.EnumProperty(items=Displaymenu)
#
#    def draw(self, context):
#        layout = self.layout
#        scene = context.scene
#        mat = context.material
#
#
#    def execute(self, context):
#        mat = context.material
##        self.report({'INFO'}, "Selected: %s" % self.my_enum)
#        item = self.my_enum
##        thea_globals.log.debug("*** IORmenu Items: %s" % item)
#        try:
#            bpy.data.materials[setattr(mat,"thea_DisplayMenu", item)]
#        except:
#            pass
#        return {'FINISHED'}
#
#    def invoke(self, context, event):
#        wm = context.window_manager
#        wm.invoke_search_popup(self)
#        return {'FINISHED'}


def saveDisplayPreset():
    scene = bpy.context.scene

    global DispISO, DispShutter, DispFNumber, DispFNumber, DispGamma, DispBrightness,\
       DispCRFMenu, DispSharpness, DispSharpnessWeight, DispBurn, DispBurnWeight,\
       DispVignetting, DispVignettingWeight, DispChroma, DispChromaWeight, DispContrast, \
       DispContrastWeight, DispTemperature, DispTemperatureWeight, DispBloom, DispBloomItems,\
       DispBloomWeight, DispGlareRadius, DispMinZ, DispMaxZ
    if thea_globals.displayReset == -2:
        DispISO = scene.thea_DispISO
        DispShutter = scene.thea_DispShutter
        DispFNumber = scene.thea_DispFNumber
        DispGamma = scene.thea_DispGamma
        DispBrightness = scene.thea_DispBrightness
        DispCRFMenu = scene.thea_DispCRFMenu
        DispSharpness = scene.thea_DispSharpness
        DispSharpnessWeight = scene.thea_DispSharpnessWeight
        DispBurn = scene.thea_DispBurn
        DispBurnWeight = scene.thea_DispBurnWeight
        DispVignetting = scene.thea_DispVignetting
        DispVignettingWeight = scene.thea_DispVignettingWeight
        DispChroma = scene.thea_DispChroma
        DispChromaWeight = scene.thea_DispChromaWeight
        DispContrast = scene.thea_DispContrast
        DispContrastWeight = scene.thea_DispContrastWeight
        DispTemperature = scene.thea_DispTemperature
        DispTemperatureWeight = scene.thea_DispTemperatureWeight
        DispBloom = scene.thea_DispBloom
        DispBloomItems = scene.thea_DispBloomItems
        DispBloomWeight = scene.thea_DispBloomWeight
        DispGlareRadius = scene.thea_DispGlareRadius
        DispMinZ = scene.thea_DispMinZ
        DispMaxZ = scene.thea_DispMaxZ

class IMAGE_PT_LoadDisplayPreset(bpy.types.Operator):
    bl_idname = "load.displaypreset"
    bl_label = "Load Display Preset"
    bl_description = "Load Display settings from studio"

    def invoke(self, context, event):
        scene = bpy.context.scene
        thea_globals.displayPreset = True
        saveDisplayPreset()
#        thea_globals.displayReset += 1
        if thea_globals.displayReset == -2:
            thea_globals.displayReset = thea_globals.displayReset + 1
        thea_globals.displaySet = scene.thea_DisplayMenu
        displayFile = scene.thea_DisplayMenu
        thea_globals.log.debug(displayFile)
        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scene)
    #    xmlFilename = currentBlendFile.replace('.blend', '.xml')
        fileName = os.path.join(dataPath,"Displays", os.path.basename(displayFile))
        checkFile = extMat = os.path.exists(fileName)
        if checkFile == False:
            self.report({'ERROR'}, "Please select a preset")
            return {'FINISHED'}
        f = open(fileName)
        i = 0
        it = iter(f)
        for line in it:
            i+=1
#            thea_globals.log.debug("*** Line: %s" % i)
            if line.find('<Root Label="Display"') >=0:
                line = next(it)
                if line.find('Filter') >=0:
                    Filter = line.split('"')[5]
                    if Filter == "1":
                        scene.thea_DispSharpness = True
                    else:
                        scene.thea_DispSharpness = False
                line = next(it)
                if line.find('Balance') >=0:
                    Balance = line.split('"')[5]
                    if Balance == "1":
                        scene.thea_DispTemperature = True
                    else:
                        scene.thea_DispTemperature = False
                line = next(it)
                if line.find('Burn') >=0:
                    Burn = line.split('"')[5]
                    if Burn == "1":
                        scene.thea_DispBurn = True
                    else:
                        scene.thea_DispBurn = False
                line = next(it)
                if line.find('Bloom') >=0:
                    Bloom = line.split('"')[5]
                    if Bloom == "1":
                        scene.thea_DispBloom = True
                    else:
                        scene.thea_DispBloom = False
                line = next(it)
                if line.find('Glare') >=0:
                    Glare = line.split('"')[5]
                    if Glare == "0":
                        scene.thea_DispBloomItems = Glare
                line = next(it)
                if line.find('Vignetting') >=0:
                    Vignetting = line.split('"')[5]
                    if Vignetting == "1":
                        scene.thea_DispVignetting = True
                    else:
                        scene.thea_DispVignetting = False
                line = next(it)
                if line.find('Chroma') >=0:
                    Chroma = line.split('"')[5]
                    if Chroma == "1":
                        scene.thea_DispChroma = True
                    else:
                        scene.thea_DispChroma = False
                line = next(it)
                if line.find('Contrast') >=0:
                    Contrast = line.split('"')[5]
                    if Contrast == "1":
                        scene.thea_DispContrast = True
                    else:
                        scene.thea_DispContrast = False
                line = next(it)
                line = next(it)
#                if line.find('Enable CRF') >=0:
#                    CRFenable = line.split('"')[5]
#                    if CRFenable == "1":
#                        scene.thea_DispCRFMenu = True
#                    else:
#                        scene.thea_DispCRFMenu = False
#                line = next(it)
                if line.find('Sharpness') >=0:
                    Sharpness = float(line.split('"')[5])
                    scene.thea_DispSharpnessWeight = Sharpness * 100
                    thea_globals.log.debug("Sharpness Weight: %s" % Sharpness)
                line = next(it)
                if line.find('Burn Weight') >=0:
                    BurnWeight = float(line.split('"')[5])
                    scene.thea_DispBurnWeight = BurnWeight * 100
#                    thea_globals.log.debug("Burnweigth Weight: %s" % BurnWeight)
                line = next(it)
                if line.find('Glare Blade') >=0:
                    GlareBlades = float(line.split('"')[5])
                    if GlareBlades == '0':
                        scene.thea_DispGlareRadius[0]
                    if GlareBlades == '5':
                        scene.thea_DispGlareRadius[1]
                    if GlareBlades == '6':
                        scene.thea_DispGlareRadius[2]
                    if GlareBlades == '8':
                        scene.thea_DispGlareRadius[3]
                    if GlareBlades == '12':
                        scene.thea_DispGlareRadius[4]
                    line = next(it)
                    if line.find('Bloom Weight') >=0:
                        BloomWeight = float(line.split('"')[5])
                        scene.thea_DispBloomWeight = BloomWeight * 100
                    line = next(it)
                    if line.find('Bloom Radius') >=0:
                        BloomRadius = float(line.split('"')[5])
                        scene.thea_DispGlareRadius = BloomRadius * 100
                    line = next(it)
                    if line.find('Vignetting Weight') >=0:
                        Vignetting = float(line.split('"')[5])
                        scene.thea_DispVignettingWeight = Vignetting * 100
                    line = next(it)
                    if line.find('Chroma Weight') >=0:
                        Chroma = float(line.split('"')[5])
                        scene.thea_DispChromaWeight = Chroma * 100
                    line = next(it)
                    if line.find('Contrast Weight') >=0:
                        Contrast = float(line.split('"')[5])
                        scene.thea_DispContrastWeight = Contrast * 100
                    line = next(it)
                    if line.find('Temperature') >=0:
                        Temperature = float(line.split('"')[5])
                        scene.thea_DispTemperatureWeight = Temperature
                    line = next(it)
                    if line.find('Gamma') >=0:
                        Gamma = float(line.split('"')[5])
                        scene.thea_DispGamma = Gamma
                    line = next(it)
                    if line.find('Brightness') >=0:
                        Brightness = float(line.split('"')[5])
                        scene.thea_DispBrightness = Brightness
                    line = next(it)
                    if line.find('ISO') >=0:
                        ISO = float(line.split('"')[5])
                        scene.thea_DispISO = ISO
                    line = next(it)
                    if line.find('Shutter Speed') >=0:
                        Shutter = float(line.split('"')[5])
                        scene.thea_DispShutter = Shutter
                    line = next(it)
                    if line.find('f-number') >=0:
                        fnumber = float(line.split('"')[5])
                        scene.thea_DispFNumber = fnumber
                    line = next(it)
#                    if line.find('Focus Distance') >=0:
#                        focusdist = float(line.split('"')[5])
#                        scene.thea_DispFNumber = focusdist
                    line = next(it)
                    if line.find('Min Z (m)') >=0:
                        MinZ = float(line.split('"')[5])
                        scene.thea_DispMinZ = MinZ
                    line = next(it)
                    if line.find('Max Z (m)') >=0:
                        MaxZ = float(line.split('"')[5])
                        scene.thea_DispMaxZ = MaxZ
        f.close()
        return {'FINISHED'}

class IMAGE_PT_UnloadDisplayPreset(bpy.types.Operator):
    bl_idname = "unload.displaypreset"
    bl_label = "Unload Display Preset"
    bl_description = "Reset display settings to prior settings"

    def execute(self, context):
        scene = context.scene
        thea_globals.displayPreset = False
        if thea_globals.displayReset == -1:
            thea_globals.displayReset = -2
            scene.thea_DispISO = DispISO
            scene.thea_DispShutter = DispShutter
            scene.thea_DispFNumber = DispFNumber
            scene.thea_DispGamma = DispGamma
            scene.thea_DispBrightness = DispBrightness
            scene.thea_DispCRFMenu = DispCRFMenu
            scene.thea_DispSharpness = DispSharpness
            scene.thea_DispSharpnessWeight = DispSharpnessWeight
            scene.thea_DispBurn = DispBurn
            scene.thea_DispBurnWeight = DispBurnWeight
            scene.thea_DispVignetting = DispVignetting
            scene.thea_DispVignettingWeight = DispVignettingWeight
            scene.thea_DispChroma = DispChroma
            scene.thea_DispChromaWeight = DispChromaWeight
            scene.thea_DispContrast = DispContrast
            scene.thea_DispContrastWeight = DispContrastWeight
            scene.thea_DispTemperature = DispTemperature
            scene.thea_DispTemperatureWeight = DispTemperatureWeight
            scene.thea_DispBloom = DispBloom
            scene.thea_DispBloomItems = DispBloomItems
            scene.thea_DispBloomWeight = DispBloomWeight
            scene.thea_DispGlareRadius = DispGlareRadius
            scene.thea_DispMinZ = DispMinZ
            scene.thea_DispMaxZ = DispMaxZ

        return{'FINISHED'}


class IMAGE_PT_EditExternally(bpy.types.Operator):
    bl_idname = "edit.externally"
    bl_label = "Edit Externally"
    bl_description = "Edit texture in external editor"
#
    text = bpy.props.StringProperty()
#    filepath = StringProperty(
#            subtype='FILE_PATH',
#            )
#
#    def execute (self, context):
##        path = base_dir + strip_elem.filename
#        tex = context.material
#        try:
#            bpy.ops.image.external_edit(filepath=path)
#        except:
#            self.report({'ERROR_INVALID_INPUT'},
#            'Please specify an Image Editor in Preferences > File')
#            return {'CANCELLED'}
#
#        return {'FINISHED'}
#    filepath = StringProperty(subtype='FILE_PATH')

    @staticmethod
    def _editor_guess(context):
        import sys

        image_editor = context.user_preferences.filepaths.image_editor

        # use image editor in the preferences when available.
        if not image_editor:
            if sys.platform[:3] == "win":
                image_editor = ["start"]  # not tested!
            elif sys.platform == "darwin":
                image_editor = ["open"]
            else:
                image_editor = ["gimp"]
        else:
            if sys.platform == "darwin":
                # blender file selector treats .app as a folder
                # and will include a trailing backslash, so we strip it.
                image_editor.rstrip('\\')
                image_editor = ["open", "-a", image_editor]
            else:
                image_editor = [image_editor]

        return image_editor

    def execute(self, context):
#        import os
#        import subprocess

        filepath = self.filepath

        if not filepath:
            self.report({'ERROR'}, "Image path not set")
            return {'CANCELLED'}

        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            self.report({'ERROR'},
                        "Image path %r not found, image may be packed or "
                        "unsaved" % filepath)
            return {'CANCELLED'}

        cmd = self._editor_guess(context) + [filepath]

        try:
            subprocess.Popen(cmd)
        except:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'},
                        "Image editor not found, "
                        "please specify in User Preferences > File")

            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        import os
        sd = context.space_data
        mat = bpy.context.material
        texEdit = mat.texture_slots[self.text].texture
#        imgName = bpy.context.object.active_material.active_texture.name #.context.material
        imgName = mat.texture_slots[self.text].name #.context.material
        texName = imgName
        exists = False
#        img = bpy.data.images.load(imgName)
        try:
            if mat.texture_slots[texName]:
                exists = True
                slot = mat.texture_slots[texName]
                tex = slot.texture
        except:
            pass

        if exists:
            try:
                if imgName:
                    img = bpy.data.images.load(imgName)
                    tex.image = img
                    tex = mat.texture_slots[text].texture
                else:
                    print("removing texture: ", slot, tex)
                    mat.texture_slots[texName].texture = None
            except:
                pass
        try:
            image = texEdit.image
        except AttributeError:
            self.report({'ERROR'}, "Context incorrect, image not found")
            return {'CANCELLED'}

        filepath = image.filepath
        filepath = bpy.path.abspath(filepath, library=image.library)

        self.filepath = os.path.normpath(filepath)
        self.execute(context)

        return {'FINISHED'}


class callToneMenu(bpy.types.Operator):
    bl_idname = "wm.call_tonemenu"
    bl_label = "Quick Edit Texture"
    bl_description = "Quick edit texture tone settings. IE Updating coordinates menu, close and reopen quick edit menu"

    origin = bpy.props.StringProperty()

    def invoke(self, context, event):
        mat = bpy.context.material
        text = mat.name+"_"+self.origin
        try:
            tex = mat.texture_slots[text].texture
        except:
            self.report({'ERROR'}, "No image loaded")
            return {'CANCELLED'}
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=800)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        mat = bpy.context.material
        text = mat.name+"_"+self.origin
        try:
            tex = mat.texture_slots[text].texture
            texMap = mat.texture_slots[0]
        except:
            self.report({'ERROR'}, "Image not found: %s" % text)
            return {'CANCELLED'}
#        tex = texName.texture
#        thea_globals.log.debug("Context Tex panel 3: %s" % texName)
#        thea_globals.log.debug("Context Tex origin: %s" % self.origin)
        layout.separator()
#        layout.prop(tex, "thea_mappingtoneMenu", expand=True)
        layout.label("Mapping")
#        if getattr(tex, "thea_mappingtoneMenu") in ("Mapping"):
        split = layout.split(percentage=0.3)
        split.label(text="Coordinates:")
        split.prop(tex, "thea_texture_coords")
        if getattr(tex,"thea_texture_coords") == 'UV':
            split = layout.split(percentage=0.3)
            split.label(text="UV Channel:")
            split.prop(tex, 'thea_TexUVChannel', text="")
        if getattr(tex, "thea_texture_coords") == 'Camera Map':
            split = layout.split(percentage=0.3)
            split.label(text="Camera:")
            split.prop(tex.texture, "thea_camMapName", text="")
        split = layout.split(percentage=0.3)
        split.label(text="Channel:")
        split.prop(tex, "thea_TexChannel", text="")
        row = layout.row()
        row.prop(tex,"thea_TexRepeat")
        if not getattr(tex, "thea_texture_coords") == 'UV':
            row = layout.row()
#           CHANGED> Added spatial
            row.label(text="Spatial:")
            row.prop(tex, "thea_TexSpatialXtex", text="X:")
            row.prop(tex, "thea_TexSpatialYtex", text="Y:")

        layout.separator()
        row = layout.row()
        row.column().prop(texMap, "offset")
        row.column().prop(texMap, "scale")
        row = layout.row()
        row.prop(tex,"thea_TexRotation")
#        if getattr(tex, "thea_mappingtoneMenu") in ("Tone"):
        layout.separator()
        split = layout.split()
        row = layout.row()
        colL = split.column()
        colL.label("Tone")
        colL.prop(tex,"thea_TexInvert")
        colL.prop(tex,"thea_TexGamma")
        colL.prop(tex,"thea_TexRed")
        colL.prop(tex,"thea_TexGreen")
        colL.prop(tex,"thea_TexBlue")
        colL.prop(tex,"thea_TexSaturation")
        colL.prop(tex,"thea_TexBrightness")
        colL.prop(tex,"thea_TexContrast")
        colL.prop(tex,"thea_TexClampMin")
        colL.prop(tex,"thea_TexClampMax")

        colL.separator()
        colL.operator("edit.externally", text="Edit externally").text = text


from TheaForBlender.thea_properties import updateCurveMaterial #updates Curve list for reflectance 90


class CURVELIST_PT_updateCurveList(bpy.types.Operator):
    bl_idname = "update.curve_list"
    bl_label = "Update Curve List"
    bl_description = "Update Reflectance 90 curve list"

    def execute(self, context):
        mat = context.material
#        mat.thea_BasicReflectionCurve = mat.thea_Basic2ReflectionCurve = mat.thea_GlossyReflectionCurve = mat.thea_Glossy2ReflectionCurve = True # update curve list
        updateCurveMaterial(self, context)
        return {'FINISHED'}
