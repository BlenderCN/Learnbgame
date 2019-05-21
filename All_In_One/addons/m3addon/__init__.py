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

bl_info = {
    "name": "Importer and exporter for Blizzard's Starcraft 2 model files (*.m3)",
    'author': 'Florian Köberle, netherh, chaos2night, Talv',
    "version": (0, 2, 0),
    "blender": (2, 70, 0),
    "location": "Properties Editor -> Scene -> M3 Panels",
    "description": "Allows to export (and import) simple Starcraft 2 models (.m3) with particle systems. Use on own risk!",
    "category": "Import-Export",
    "wiki_url": "https://github.com/Talv/m3addon/blob/master/README.md",
    "tracker_url": "https://github.com/Talv/m3addon/issues"
}

if "bpy" in locals():
    import imp
    if "m3import" in locals():
            imp.reload(m3import)
            
    if "m3export" in locals():
            imp.reload(m3export)
            
    if "shared" in locals():
        imp.reload(shared)

from . import shared
import bpy

from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
import mathutils
import math

def boneNameSet():
    boneNames = set()
    for armature in bpy.data.armatures:
        for bone in armature.bones:
            boneNames.add(bone.name)
        for bone in armature.edit_bones:
            boneNames.add(bone.name)
    return boneNames

def availableBones(self, context):
    sortedBoneNames = []
    sortedBoneNames.extend(boneNameSet())
    sortedBoneNames.sort()
    list = [("", "None", "Not assigned to a bone")]
    
    for boneName in sortedBoneNames:
        list.append((boneName,boneName,boneName))
    return list

def availableMaterials(self, context):
    list = [("", "None", "No Material")]
    for material in context.scene.m3_material_references:
        list.append((material.name, material.name, material.name))
    return list

def updateBoenShapesOfParticleSystemCopies(scene, particleSystem):
    for copy in particleSystem.copies:
        boneName = copy.boneName
        bone, armatureObject = shared.findBoneWithArmatureObject(scene, boneName)
        if bone != None:
            poseBone = armatureObject.pose.bones[boneName]
            shared.updateBoneShapeOfParticleSystem(particleSystem, bone, poseBone)

def handleAttachmentPointTypeOrBoneSuffixChange(self, context):
    attachmentPoint = self
    scene = context.scene
    typeName = "Unknown"
    if attachmentPoint.volumeType == "-1":
        typeName = "Point"
    else:
        typeName = "Volume"
        
    boneSuffix = attachmentPoint.boneSuffix
    attachmentPoint.name = "%s (%s)" % (boneSuffix, typeName)
    
    currentBoneName = attachmentPoint.boneName
    calculatedBoneName = shared.boneNameForAttachmentPoint(attachmentPoint)
    
    if currentBoneName != calculatedBoneName:
        bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
        if bone != None:
            bone.name = calculatedBoneName
            attachmentPoint.boneName = bone.name
        else:
            attachmentPoint.boneName = calculatedBoneName
    if attachmentPoint.updateBlenderBone:
        selectOrCreateBoneForAttachmentPoint(scene, attachmentPoint)
        
def handleGeometicShapeTypeOrBoneNameUpdate(self, context):
    shapeObject = self
    scene = context.scene
    typeName = "Unknown"
    for typeId, name, description in geometricShapeTypeList:
        if typeId == shapeObject.shape:
            typeName = name

    shapeObject.name = "%s (%s)" % (shapeObject.boneName, typeName)

    if shapeObject.updateBlenderBone:
        selectOrCreateBoneForShapeObject(scene, shapeObject)

def handleParticleSystemTypeOrNameChange(self, context):
    particleSystem = self
    scene = context.scene

    if particleSystem.updateBlenderBoneShapes:
        currentBoneName = particleSystem.boneName
        calculatedBoneName = shared.boneNameForPartileSystem(particleSystem)

        if currentBoneName!= calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                particleSystem.boneName = bone.name
            else:
                particleSystem.boneName = calculatedBoneName

        selectOrCreateBoneForPartileSystem(scene, particleSystem)
        updateBoenShapesOfParticleSystemCopies(scene, particleSystem)
        
def handleParticleSystemCopyRename(self, context):
    scene = context.scene
    particleSystemCopy = self
    
    currentBoneName = particleSystemCopy.boneName
    calculatedBoneName = shared.boneNameForPartileSystemCopy(particleSystemCopy)

    if currentBoneName != calculatedBoneName:
        bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
        if bone != None:
            bone.name = calculatedBoneName
            particleSystemCopy.boneName = bone.name
        else:
            particleSystemCopy.boneName = calculatedBoneName
  
  
def handleRibbonBoneSuffixChange(self, context):
    ribbon = self
    scene = context.scene
    
    # no type yet to combine in the name
    ribbon.name = ribbon.boneSuffix

    if ribbon.updateBlenderBoneShapes:
        currentBoneName = ribbon.boneName
        calculatedBoneName = shared.boneNameForRibbon(ribbon)

        if currentBoneName != calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                ribbon.boneName = bone.name
            else:
                ribbon.boneName = calculatedBoneName

            selectOrCreateBoneForRibbon(scene, ribbon)
            #TODO for sub ribbons:
            # updateBoenShapesOfSubRibbons(scene, ribbon)
  
  
def handleParticleSystemAreaSizeChange(self, context):
    particleSystem = self
    scene = context.scene
    if particleSystem.updateBlenderBoneShapes:
        selectOrCreateBoneForPartileSystem(scene, particleSystem)
        updateBoenShapesOfParticleSystemCopies(scene, particleSystem)


def handleForceTypeOrBoneSuffixChange(self, context):
    scene = context.scene
    force = self
    typeName = "Unknown"
    for typeId, name, description in forceTypeList:
        if typeId == force.type:
            typeName = name
    
    boneSuffix = force.boneSuffix
    self.name = "%s (%s)" % (boneSuffix, typeName)

    if force.updateBlenderBoneShape:
        currentBoneName = force.boneName
        calculatedBoneName = shared.boneNameForForce(force)

        if currentBoneName != calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                force.boneName = bone.name
            else:
                force.boneName = calculatedBoneName

        selectOrCreateBoneForForce(scene, force)

def handleForceRangeUpdate(self, context):
    scene = context.scene
    force = self
    if force.updateBlenderBoneShape:
        selectOrCreateBoneForForce(scene, force)


def handleLightTypeOrBoneSuffixChange(self, context):
    scene = context.scene
    light = self
    typeName = "Unknown"
    for typeId, name, description in lightTypeList:
        if typeId == light.lightType:
            typeName = name
    
    light.name = "%s (%s)" % (light.boneSuffix, typeName)
    
    currentBoneName = light.boneName
    calculatedBoneName = shared.boneNameForLight(light)

    if light.updateBlenderBone:
        if currentBoneName != calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                light.boneName = bone.name
            else:
                light.boneName = calculatedBoneName
        selectOrCreateBoneForLight(scene, light)


def handleProjectionSizeChange(self, context):
    projection = self
    scene = context.scene
    if projection.updateBlenderBone:
        selectOrCreateBoneForProjection(scene, projection)

def handleLightSizeChange(self, context):
    scene = context.scene
    light = self
    if light.updateBlenderBone:
        selectOrCreateBoneForLight(scene, light)

def handleWarpRadiusChange(self, context):
    scene = context.scene
    warp = self
    if warp.updateBlenderBone:
        selectOrCreateBoneForWarp(scene, warp)

def handleProjectionTypeOrBoneSuffixChange(self, context):
    scene = context.scene
    projection = self
    
    projection.name = projection.boneSuffix
    
    currentBoneName = projection.boneName
    calculatedBoneName = shared.boneNameForProjection(projection)

    if projection.updateBlenderBone:
        if currentBoneName != calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                projection.boneName = bone.name
            else:
                projection.boneName = calculatedBoneName
        selectOrCreateBoneForProjection(scene, projection)


def handleWarpBoneSuffixChange(self, context):
    scene = context.scene
    warp = self
    
    warp.name = warp.boneSuffix
    
    currentBoneName = warp.boneName
    calculatedBoneName = shared.boneNameForWarp(warp)

    if warp.updateBlenderBone:
        if currentBoneName != calculatedBoneName:
            bone, armatureObject = shared.findBoneWithArmatureObject(scene, currentBoneName)
            if bone != None:
                bone.name = calculatedBoneName
                warp.boneName = bone.name
            else:
                warp.boneName = calculatedBoneName
        selectOrCreateBoneForWarp(scene, warp)

def handleCameraNameChange(self, context):
    scene = context.scene
    if self.name != self.oldName:
        bone, armatureObject = shared.findBoneWithArmatureObject(scene, self.oldName)
        if bone != None:
            bone.name = self.name
    self.oldName = self.name

def handleDepthBlendFalloffChanged(self, context):
    material = self
    if material.depthBlendFalloff <= 0.0:
        if material.useDepthBlendFalloff:
            material.useDepthBlendFalloff = False
    else:
        if not material.useDepthBlendFalloff:
            material.useDepthBlendFalloff = True
    
def handleUseDepthBlendFalloffChanged(self, context):
    material = self
    if material.useDepthBlendFalloff:
        if material.depthBlendFalloff <= 0.0:
            material.depthBlendFalloff = shared.defaultDepthBlendFalloff
    else:
        if material.depthBlendFalloff != 0.0:
            material.depthBlendFalloff = 0.0
    


def handleMaterialNameChange(self, context):
    scene = context.scene
    materialName = self.name
    materialReferenceIndex = self.materialReferenceIndex
    if materialReferenceIndex != -1:
        materialReference = scene.m3_material_references[self.materialReferenceIndex]
        materialIndex = materialReference.materialIndex
        materialType = materialReference.materialType
        oldMaterialName = materialReference.name 
        materialReference.name = materialName
        
        for particle_system in scene.m3_particle_systems:
            if particle_system.materialName == oldMaterialName:
                particle_system.materialName = materialName
                
        for projection in scene.m3_projections:
            if projection.materialName == oldMaterialName:
                projection.materialName = materialName
                
        for meshObject in shared.findMeshObjects(scene):
            mesh = meshObject.data
            if mesh.m3_material_name == oldMaterialName:     
                mesh.m3_material_name = materialName


def handleMaterialLayerFieldNameChange(self, context):
    self.name = layerFieldNameToNameMap.get(fieldName, fieldName)
    
def handleAttachmentVolumeTypeChange(self, context):
    handleAttachmentPointTypeOrBoneSuffixChange(self, context)
    if self.volumeType in ["0", "1", "2"]:
       if self.volumeSize0 == 0.0:
            self.volumeSize0 = 1.0
    else:
        self.volumeSize0 = 0.0

    if self.volumeType in ["0", "2"]:
        if self.volumeSize1 == 0.0:
            self.volumeSize1 = 1.0
    else:
        self.volumeSize1 = 0.0

    if self.volumeType in ["0"]:
        if self.volumeSize2 == 0.0:
            self.volumeSize2 = 1.0
    else:
        self.volumeSize2 = 0.0
        
        
def handleAttachmentVolumeSizeChange(self, context):
    scene = context.scene
    attachmentPoint = self
    if attachmentPoint.updateBlenderBone:
        selectOrCreateBoneForAttachmentPoint(scene, attachmentPoint)

def handleGeometicShapeUpdate(self, context):
    shapeObject = self
    if shapeObject.updateBlenderBone:
        selectOrCreateBoneForShapeObject(context.scene, shapeObject)

def handleParticleSystemsVisiblityUpdate(self, context):
    scene = context.scene
    for particleSystem in scene.m3_particle_systems:
        boneName = particleSystem.boneName
        shared.setBoneVisibility(scene, boneName, self.showParticleSystems)
        
        for copy in particleSystem.copies:
            boneName = copy.boneName
            shared.setBoneVisibility(scene, boneName, self.showParticleSystems)

def handleRibbonsVisiblityUpdate(self, context):
    scene = context.scene
    for ribbon in scene.m3_ribbons:
        boneName = ribbon.boneName
        shared.setBoneVisibility(scene, boneName, self.showRibbons)
        
        # TODO for sub ribbons:
        #for subRibbon in ribbon.subRibbons:
        #    boneName = subRibbon.boneName
        #    shared.setBoneVisibility(scene, boneName, self.showRibbons)            


def handleFuzzyHitTestVisiblityUpdate(self, context):
    scene = context.scene
    for fuzzyHitTest in scene.m3_fuzzy_hit_tests:
        boneName = fuzzyHitTest.boneName
        shared.setBoneVisibility(scene, boneName, self.showFuzzyHitTests)
    
def handleTightHitTestVisiblityUpdate(self, context):
    scene = context.scene
    tightHitTest = scene.m3_tight_hit_test
    boneName = tightHitTest.boneName
    shared.setBoneVisibility(scene, boneName, self.showTightHitTest)

def handleAttachmentPointVisibilityUpdate(self, context):
    scene = context.scene
    for attachmentPoint in scene.m3_attachment_points:
        boneName = attachmentPoint.boneName
        shared.setBoneVisibility(scene, boneName, self.showAttachmentPoints)

def handleLightsVisiblityUpdate(self, context):
    scene = context.scene
    for light in scene.m3_lights:
        boneName = light.boneName
        shared.setBoneVisibility(scene, boneName, self.showLights)

def handleForcesVisiblityUpdate(self, context):
    scene = context.scene
    for force in scene.m3_forces:
        boneName = force.boneName
        shared.setBoneVisibility(scene, boneName, self.showForces)

def handleCamerasVisiblityUpdate(self, context):
    scene = context.scene
    for camera in scene.m3_cameras:
        boneName = camera.name
        shared.setBoneVisibility(scene, boneName, self.showCameras)

def handlePhysicsShapeVisibilityUpdate(self, context):
    scene = context.scene
    for rigidBody in scene.m3_rigid_bodies:
        boneName = rigidBody.boneName
        shared.setBoneVisibility(scene, boneName, self.showPhysicsShapes)

def handleProjectionVisibilityUpdate(self, context):
    scene = context.scene
    for projection in scene.m3_projections:
        boneName = projection.boneName
        shared.setBoneVisibility(scene, boneName, self.showProjections)

def handleWarpVisibilityUpdate(self, context):
    scene = context.scene
    for warp in scene.m3_warps:
        boneName = warp.boneName
        shared.setBoneVisibility(scene, boneName, self.showWarps)

def getTrackName(m3Animation):
    return m3Animation.name + "_full"

def getOrCreateStrip(m3Animation, animationData):
    trackName = getTrackName(m3Animation)
    track = shared.getOrCreateTrack(animationData, trackName)
    if len(track.strips) > 0:
        strip = track.strips[0]
    else:
        stripName = trackName
        strip = track.strips.new(name=stripName, start=0,action=animationData.action)
    return strip

def handleAnimationChange(targetObject, oldAnimation, newAnimation):
    animationData = targetObject.animation_data    
    oldAction = animationData.action
    if oldAction != None and oldAnimation != None:
        oldStrip = getOrCreateStrip(oldAnimation, animationData)
        oldStrip.action = animationData.action
    
    if newAnimation:   
        newTrackName = newAnimation.name + "_full"
        newTrack = animationData.nla_tracks.get(newTrackName)
        if newTrack != None and len(newTrack.strips) > 0:
            newStrip = newTrack.strips[0]
            newAction = newStrip.action
        else:
            newAction = None
    else:
        newAction = None
    prepareDefaultValuesForNewAction(targetObject, newAction)
    animationData.action = newAction


def handleAnimationSequenceIndexChange(self, context):
    scene = self
    newIndex = scene.m3_animation_index
    oldIndex = scene.m3_animation_old_index
    shared.setAnimationWithIndexToCurrentData(scene, oldIndex)
    if (newIndex >= 0) and (newIndex < len(scene.m3_animations)):
        newAnimation = scene.m3_animations[newIndex]
    else:
        newAnimation = None
    if oldIndex >= 0 and (oldIndex < len(scene.m3_animations)):
        oldAnimation = scene.m3_animations[oldIndex]
    else:
        oldAnimation = None
        
    if newAnimation != None:
        scene.frame_start = newAnimation.startFrame
        scene.frame_end = newAnimation.exlusiveEndFrame - 1
        
    for targetObject in scene.objects:
        animationData = targetObject.animation_data
        if animationData != None:
            handleAnimationChange(targetObject, oldAnimation, newAnimation)
    
    if scene.animation_data != None:
        handleAnimationChange(scene, oldAnimation, newAnimation)

    scene.m3_animation_old_index = newIndex


def prepareDefaultValuesForNewAction(objectWithAnimationData, newAction):
    oldAnimatedProperties = set()
    animationData = objectWithAnimationData.animation_data
    if animationData == None:
        raise Exception("Must have animation data")
    oldAction = animationData.action
    if oldAction != None:
        for curve in oldAction.fcurves:
            oldAnimatedProperties.add((curve.data_path, curve.array_index))
    newAnimatedProperties = set()
    if newAction != None:
        for curve in newAction.fcurves:
            newAnimatedProperties.add((curve.data_path, curve.array_index))    
    defaultAction = shared.getOrCreateDefaultActionFor(objectWithAnimationData)

    removedProperties = set()

    propertiesBecomingAnimated = newAnimatedProperties.difference(oldAnimatedProperties)
    for prop in propertiesBecomingAnimated:
        try:
            value = getAttribute(objectWithAnimationData, prop[0],prop[1])
            propertyExists = True
        except:
            propertyExists = False
        if propertyExists:
            shared.setDefaultValue(defaultAction,prop[0],prop[1], value)
        else:
            print ("Can't find prop %s" % prop[0], prop[1])
            removedProperties.add(prop)
    propertiesBecomingUnanimated = oldAnimatedProperties.difference(newAnimatedProperties)
    
    if len(removedProperties) > 0:
        print("Removing animations for %s since those properties do no longer exist" % removedProperties)
    
    removedCurves = list()
    if newAction != None:
        for curve in newAction.fcurves:
            if (curve.data_path, curve.array_index) in removedProperties:
                removedCurves.append(curve)
    for removedCurve in removedCurves:
        newAction.fcurves.remove(removedCurve)
    
    
    defaultsToRemove = set()
    
    for curve in defaultAction.fcurves:
        prop = (curve.data_path, curve.array_index)
        if prop in propertiesBecomingUnanimated:
            defaultValue = curve.evaluate(0)
            curvePath = curve.data_path
            curveIndex = curve.array_index
            
            try:
                resolvedObject = objectWithAnimationData.path_resolve(curvePath)
                propertyExists = True
            except:
                propertyExists = False
            if propertyExists:
                if type(resolvedObject) in [float, int, bool]:
                    dotIndex = curvePath.rfind(".")
                    attributeName = curvePath[dotIndex+1:]
                    resolvedObject = objectWithAnimationData.path_resolve(curvePath[:dotIndex])
                    setattr(resolvedObject, attributeName, defaultValue)
                else:
                    resolvedObject[curveIndex] = defaultValue
            else:
                defaultsToRemove.add(prop)
    removedDefaultCurves = list()
    for curve in defaultAction.fcurves:
        if (curve.data_path, curve.array_index) in removedProperties:
            removedDefaultCurves.append(curve)
    for removedDefaultCurve in removedDefaultCurves:
        defaultAction.fcurves.remove(removedDefaultCurve)   

def getAttribute(obj, curvePath, curveIndex):
    """Gets the value of an attribute via animation path and index"""
    obj = obj.path_resolve(curvePath)
    if type(obj) in [float, int, bool]:
        return obj
    else:
        return obj[curveIndex]

def findUnusedParticleSystemName(scene):
    usedNames = set()
    for particle_system in scene.m3_particle_systems:
        usedNames.add(particle_system.name)
        for copy in particle_system.copies:
            usedNames.add(copy.name)
    unusedName = None
    counter = 1
    while unusedName == None:
        suggestedName = "%02d" % counter
        if not suggestedName in usedNames:
            unusedName = suggestedName
        counter += 1
    return unusedName  

def handlePartileSystemIndexChanged(self, context):
    scene = context.scene
    if scene.m3_particle_system_index == -1:
        return
    particleSystem = scene.m3_particle_systems[scene.m3_particle_system_index]
    particleSystem.copyIndex = -1
    selectOrCreateBoneForPartileSystem(scene, particleSystem)

def handleRibbonIndexChanged(self, context):
    scene = context.scene
    if scene.m3_ribbon_index == -1:
        return
    ribbon = scene.m3_ribbons[scene.m3_ribbon_index]
    ribbon.endPointIndex = -1
    selectOrCreateBoneForRibbon(scene, ribbon)

def handleRibbonEndPointIndexChanged(self, context):
    scene = context.scene
    ribbon = self
    if ribbon.endPointIndex >= 0 and ribbon.endPointIndex < len(ribbon.endPoints):
        endPoint = ribbon.endPoints[ribbon.endPointIndex]
        selectBoneIfItExists(scene,endPoint.name)

def handleForceIndexChanged(self, context):
    scene = context.scene
    if scene.m3_force_index == -1:
        return
    force = scene.m3_forces[scene.m3_force_index]
    selectOrCreateBoneForForce(scene, force)

def handlePhysicsShapeUpdate(self, context):
    scene = context.scene
    
    if self.updateBlenderBoneShapes:
        if scene.m3_rigid_body_index != -1:
            rigidBody = scene.m3_rigid_bodies[scene.m3_rigid_body_index]
            shared.updateBoneShapeOfRigidBody(scene, rigidBody)
        
        selectCurrentRigidBodyBone(scene)
        scene.m3_bone_visiblity_options.showPhysicsShapes = True

def handleRigidBodyIndexChange(self, context):
    scene = context.scene
    scene.m3_bone_visiblity_options.showPhysicsShapes = True
    selectCurrentRigidBodyBone(scene)

def handleRigidBodyBoneChange(self, context):
    # TODO: remove custom bone shape for old bone, create custom bone shape for new bone.
    # need to save old bone name somehow?
    scene = context.scene
    selectCurrentRigidBodyBone(scene)

def selectCurrentRigidBodyBone(scene):
    if scene.m3_rigid_body_index != -1:
        rigidBody = scene.m3_rigid_bodies[scene.m3_rigid_body_index]
        selectBone(scene, rigidBody.boneName)

def handleLightIndexChanged(self, context):
    scene = context.scene
    if scene.m3_light_index == -1:
        return
    light = scene.m3_lights[scene.m3_light_index]
    selectOrCreateBoneForLight(scene, light)
    
def handleBillboardBehaviorIndexChanged(self, context):
    scene = context.scene
    if scene.m3_billboard_behavior_index == -1:
        return
    billboardBehavior = scene.m3_billboard_behaviors[scene.m3_billboard_behavior_index]
    selectBoneIfItExists(scene, billboardBehavior.name)
    
def handleProjectionIndexChanged(self, context):
    scene = context.scene
    if scene.m3_projection_index == -1:
        return
    projection = scene.m3_projections[scene.m3_projection_index]
    selectOrCreateBoneForProjection(scene, projection)
    
def handleWarpIndexChanged(self, context):
    scene = context.scene
    if scene.m3_warp_index == -1:
        return
    warp = scene.m3_warps[scene.m3_warp_index]
    selectOrCreateBoneForWarp(scene, warp)
   
def handleAttachmentPointIndexChanged(self, context):
    scene = context.scene
    if scene.m3_attachment_point_index == -1:
        return
    attachmentPoint = scene.m3_attachment_points[scene.m3_attachment_point_index]
    selectOrCreateBoneForAttachmentPoint(scene, attachmentPoint)

def handlePartileSystemCopyIndexChanged(self, context):
    scene = context.scene
    particleSystem = self
    if particleSystem.copyIndex >= 0 and particleSystem.copyIndex < len(particleSystem.copies):
        copy = particleSystem.copies[particleSystem.copyIndex]
        selectOrCreateBoneForPartileSystemCopy(scene, particleSystem, copy)

def handleCameraIndexChanged(self, context):
    scene = context.scene
    if scene.m3_camera_index == -1:
        return
    camera = scene.m3_cameras[scene.m3_camera_index]
    selectOrCreateBoneForCamera(scene, camera)

def handleFuzzyHitTestIndexChanged(self, context):
    scene = context.scene
    if scene.m3_fuzzy_hit_test_index == -1:
        return
    fuzzyHitTest = scene.m3_fuzzy_hit_tests[scene.m3_fuzzy_hit_test_index]
    selectOrCreateBoneForShapeObject(scene, fuzzyHitTest)

def selectOrCreateBoneForAttachmentPoint(scene, attachmentPoint):
    scene.m3_bone_visiblity_options.showAttachmentPoints = True
    boneName = attachmentPoint.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfAttachmentPoint(attachmentPoint, bone, poseBone)
    
def selectOrCreateBoneForPartileSystemCopy(scene, particleSystem, copy):
    scene.m3_bone_visiblity_options.showParticleSystems = True
    boneName = copy.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfParticleSystem(particleSystem, bone, poseBone)
    
def selectOrCreateBoneForForce(scene, force):
    scene.m3_bone_visiblity_options.showForces = True
    boneName = force.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfForce(force, bone, poseBone)
    return (bone, poseBone)
    
def selectOrCreateBoneForLight(scene, light):
    scene.m3_bone_visiblity_options.showLights = True
    boneName = light.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfLight(light, bone, poseBone)

def selectOrCreateBoneForProjection(scene, projection):
    scene.m3_bone_visiblity_options.showProjections = True
    boneName = projection.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfProjection(projection, bone, poseBone)

def selectOrCreateBoneForWarp(scene, projection):
    scene.m3_bone_visiblity_options.showWarps = True
    boneName = projection.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfWarp(projection, bone, poseBone)

def selectOrCreateBoneForCamera(scene, camera):
    scene.m3_bone_visiblity_options.showCameras = True
    selectOrCreateBone(scene, camera.name)

def selectOrCreateBoneForPartileSystem(scene, particle_system):
    scene.m3_bone_visiblity_options.showParticleSystems = True
    boneName = particle_system.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfParticleSystem(particle_system, bone, poseBone)
    
def selectOrCreateBoneForRibbon(scene, ribbon):
    scene.m3_bone_visiblity_options.showRibbons = True
    boneName = ribbon.boneName
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfRibbon(ribbon, bone, poseBone)

def selectOrCreateBoneForShapeObject(scene, shapeObject):
    boneName = shapeObject.boneName
    if boneName == shared.tightHitTestBoneName:
        scene.m3_bone_visiblity_options.showTightHitTest = True
    else:
        scene.m3_bone_visiblity_options.showFuzzyHitTests = True
    bone, poseBone = selectOrCreateBone(scene, boneName)
    shared.updateBoneShapeOfShapeObject(shapeObject, bone, poseBone)

def selectBone(scene, boneName):
    bone, armature = shared.findBoneWithArmatureObject(scene, boneName)
    if bone == None or armature == None:
        return
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')
    
    armature.select = True
    scene.objects.active = armature
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='POSE')
    
    for b in armature.data.bones:
        b.select = False
    
    bone.select = True
    
def removeBone(scene, boneName):
    "removes the given bone if it exists"
    bone, armatureObject = shared.findBoneWithArmatureObject(scene, boneName)
    if bone == None or armatureObject == None:
        return
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')
    
    armatureObject.select = True
    scene.objects.active = armatureObject
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
    
    armature = armatureObject.data
    edit_bone = armature.edit_bones[boneName]
    armature.edit_bones.remove(edit_bone)
    
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='POSE')
    

def selectOrCreateBone(scene, boneName):
    "Returns the bone and it's pose variant"
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')
    bone, armatureObject = shared.findBoneWithArmatureObject(scene, boneName)
    boneExists = bone != None
    if boneExists:
        armature = armatureObject.data
        armatureObject.select = True
        scene.objects.active = armatureObject
    else:
        armatureObject = shared.findArmatureObjectForNewBone(scene)
        if armatureObject == None:
            armature = bpy.data.armatures.new(name="Armature")
            armatureObject = bpy.data.objects.new("Armature", armature)
            scene.objects.link(armatureObject)
        else:
            armature = armatureObject.data
        armatureObject.select = True
        scene.objects.active = armatureObject
        bpy.ops.object.mode_set(mode='EDIT')
        editBone = armature.edit_bones.new(boneName)
        editBone.head = (0, 0, 0)
        editBone.tail = (1, 0, 0)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='POSE')
        
    for boneOfArmature in armature.bones:
        isBoneToSelect = boneOfArmature.name == boneName
        boneOfArmature.select_head = isBoneToSelect
        boneOfArmature.select_tail = isBoneToSelect
        boneOfArmature.select = isBoneToSelect
    armature.bones.active = bone
        
    scene.objects.active = armatureObject
    armatureObject.select = True
    for currentBone in armature.bones:
        currentBone.select = currentBone.name == boneName
    poseBone = armatureObject.pose.bones[boneName]
    bone = armatureObject.data.bones[boneName]
    return (bone, poseBone)

def selectBoneIfItExists(scene, boneName):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')
    bone, armatureObject = shared.findBoneWithArmatureObject(scene, boneName)
    armature = armatureObject.data
    armatureObject.select = True
    scene.objects.active = armatureObject
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='POSE')
    scene.objects.active = armatureObject
    armatureObject.select = True
    for currentBone in armature.bones:
        currentBone.select = currentBone.name == boneName
    
def determineLayerNames(defaultSetting):
    from . import m3
    settingToStructureNameMap = {
        defaultSettingMesh: "MAT_", 
        defaultSettingParticle: "MAT_", 
        defaultSettingCreep: "CREP",
        defaultSettingDisplacement: "DIS_",
        defaultSettingComposite: "CMP_",
        defaultSettingVolume: "VOL_",
        defaultSettingVolumeNoise: "VON_",
        defaultSettingTerrain: "TER_",
        defaultSettingSplatTerrainBake: "STBM",
        defaultSettingLensFlare: "LFLR"
    }
    structureName = settingToStructureNameMap[defaultSetting]
    structureDescription = m3.structures[structureName].getNewestVersion()
    for field in structureDescription.fields:
        if hasattr(field, "referenceStructureDescription"):
            if field.historyOfReferencedStructures.name == "LAYR":
                yield shared.getLayerNameFromFieldName(field.name)


def finUnusedMaterialName(scene):
    usedNames = set()
    for materialReferenceIndex in range(0, len(scene.m3_material_references)):
        materialReference = scene.m3_material_references[materialReferenceIndex]
        material = shared.getMaterial(scene, materialReference.materialType, materialReference.materialIndex)
        if material != None:
            usedNames.add(material.name)
    unusedName = None
    counter = 1
    while unusedName == None:
        suggestedName = "%02d" % counter
        if not suggestedName in usedNames:
            unusedName = suggestedName
        counter += 1
    return unusedName

def createMaterial(scene, materialName, defaultSetting):
    layerNames = determineLayerNames(defaultSetting)
                    
    if defaultSetting in [defaultSettingMesh, defaultSettingParticle]:
        materialType = shared.standardMaterialTypeIndex
        materialIndex = len(scene.m3_standard_materials)
        material = scene.m3_standard_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
            if layerName == "Diffuse":
                if defaultSetting != defaultSettingParticle:
                    layer.colorChannelSetting = shared.colorChannelSettingRGBA
        
        if defaultSetting == defaultSettingParticle:
            material.unfogged = True
            material.blendMode = "2"
            material.layerBlendType = "2"
            material.emisBlendType = "2"
            material.noShadowsCast = True
            material.noHitTest = True
            material.noShadowsReceived = True
            material.forParticles = True
            material.useDepthBlendFalloff = True
            material.depthBlendFalloff = shared.defaultDepthBlendFalloff
            material.unknownFlag0x2 = True
            material.unknownFlag0x8 = True
    elif defaultSetting == defaultSettingDisplacement:
        materialType = shared.displacementMaterialTypeIndex
        materialIndex = len(scene.m3_displacement_materials)
        material = scene.m3_displacement_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingComposite:
        materialType = shared.compositeMaterialTypeIndex
        materialIndex = len(scene.m3_composite_materials)
        material = scene.m3_composite_materials.add()
        # has no layers
    elif defaultSetting == defaultSettingTerrain:
        materialType = shared.terrainMaterialTypeIndex
        materialIndex = len(scene.m3_terrain_materials)
        material = scene.m3_terrain_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingVolume:
        materialType = shared.volumeMaterialTypeIndex
        materialIndex = len(scene.m3_volume_materials)
        material = scene.m3_volume_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingVolumeNoise:
        materialType = shared.volumeNoiseMaterialTypeIndex
        materialIndex = len(scene.m3_volume_noise_materials)
        material = scene.m3_volume_noise_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingCreep:
        materialType = shared.creepMaterialTypeIndex
        materialIndex = len(scene.m3_creep_materials)
        material = scene.m3_creep_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingSplatTerrainBake:
        materialType = shared.stbMaterialTypeIndex
        materialIndex = len(scene.m3_stb_materials)
        material = scene.m3_stb_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
    elif defaultSetting == defaultSettingLensFlare:
        materialType = shared.lensFlareMaterialTypeIndex
        materialIndex = len(scene.m3_lens_flare_materials)
        material = scene.m3_lens_flare_materials.add()
        for layerName in layerNames:
            layer = material.layers.add()
            layer.name = layerName
            
    materialReferenceIndex = len(scene.m3_material_references)
    materialReference = scene.m3_material_references.add()
    materialReference.materialIndex = materialIndex
    materialReference.materialType = materialType
    material.materialReferenceIndex = materialReferenceIndex
    material.name = materialName # will also set materialReference name


    scene.m3_material_reference_index = len(scene.m3_material_references)-1


emissionAreaTypesWithRadius = [shared.emissionAreaTypeSphere, shared.emissionAreaTypeCylinder]
emissionAreaTypesWithWidth = [shared.emissionAreaTypePlane, shared.emissionAreaTypeCuboid]
emissionAreaTypesWithLength = [shared.emissionAreaTypePlane, shared.emissionAreaTypeCuboid]
emissionAreaTypesWithHeight = [shared.emissionAreaTypeCuboid, shared.emissionAreaTypeCylinder]
emissionAreaTypeList =  [(shared.emissionAreaTypePoint, "Point", "Particles spawn at a certain point"), 
                        (shared.emissionAreaTypePlane, 'Plane', "Particles spawn in a rectangle"), 
                        (shared.emissionAreaTypeSphere, 'Sphere', 'Particles spawn in a sphere'),
                        (shared.emissionAreaTypeCuboid, 'Cuboid', 'Particles spawn in a cuboid'),
                        (shared.emissionAreaTypeCylinder, 'Cylinder', 'Particles spawn in a cylinder'),
                        (shared.emissionAreaTypeDisc, 'Disc', 'Particles spawn in a cylinder of height 0'),
                        (shared.emissionAreaTypeMesh, 'Spline', 'Spawn location are the vertices of a mesh'),
                        ("7", 'Mesh', 'If Vertex Color is applied and exported by the material on the mesh, then the Red channel of vertex color regulates the probability that a face will be used for particle emission')
                        ]

particleTypeList = [("0", "Square Billbords", "Quads always rotated towards camera (id 0)"), 
                    ("1", "Speed Scaled and Rotated Billbords", "Particles are rectangles scaled which get scaled by speed by a configurable amounth"),
                    ("2", "Square Billbords 2?", "Unknown 2"),
                    ("3", "Square Billbords 3?", "Unknown 3"),
                    ("4", "Square Billbords 4?", "Unknown 4"),
                    ("5", "Square Billbords 5?", "Unknown 5"),
                    ("6", "Rectangular Billbords", "Rectangles which can have a length != witdh which are rotated towards the camera"),
                    ("7", "Quads with speed as normal", "Particles are quads which have their normals aligned to the speed vector of the particle"),
                    ("8", "Unknown (Id 8)", "Code 8 with unknown meaning"),
                    ("9", "Ray from Spawn Location", "A billboard that reaches from the spawn location to the current position"),
                    ("10", "Unknown (Id 10)", "Code 10 with unknown meaning")
                    ]

ribbonTypeList = [("0", "Planar Billboarded", "Planar Billboarded"), 
                  ("1", "Planar", "Planar"),
                  ("2", "Cylinder", "Cylinder"),
                  ("3", "Star Shaped", "Star Shaped")
                 ]
                 
projectionTypeList = [(shared.projectionTypeOrthonormal, "Orthonormal", "makes the Projector behave like a box. It will be the same width no matter how close the projector is to the target surface."), 
                  (shared.projectionTypePerspective, "Perspective", "makes the Projector behave like a camera. The closer the projector is to the surface, the smaller the effect will be.")
                 ]


forceTypeList = [("0", "Directional", "The particles get accelerated into one direction"), 
                    ("1", "Radial", "Particles get accelerated ayway from the force source"),
                    ("2", "Dampening", "This is a drag operation that resists the movement of particles"),
                    ("3", "Vortex", "This is a special rotation field that brings particles into a orbit. Does not work with Box Shape applied.")
                   ]

forceShapeList = [("0", "Sphere", "The particles get accelerated into one direction"), 
                    ("1", "Cylinder", "A cylinder with Radius and Height"),
                    ("2", "Box", "A box shape with Width, Height, and Length."),
                    ("3", "Hemisphere", "Half sphere shape defined with Radius."),
                    ("4", "ConeDome", "Special cone shape with length defined as Radius and cone width defined as Angle.")
                   ]
                   
physicsShapeTypeList = [("0", "Box", "Box shape with the given width, length and height"),
                        ("1", "Sphere", "Sphere shape with the given radius"),
                        ("2", "Capsule", "Capsule shape with the given radius and length"),
                        ("3", "Cylinder", "Cylinder with the given radius and length"),
                        ("4", "Convex Hull", "Convex hull created from the attached mesh"),
                        ("5", "Mesh", "Mesh shape created from the attached mesh"),
                        ]

uvSourceList = [("0", "Default", "First UV layer of mesh or generated whole image UVs for particles"),
                 ("1", "UV Layer 2", "Second UV layer which can be used for decals"),
                 ("2", "Ref Cubic Env", "For Env. Layer: Reflective Cubic Environment"),
                 ("3", "Ref Spherical Env", "For Env. Layer: Reflective Spherical Environemnt"),
                 ("4", "Planar Local z", "Planar Local z"),
                 ("5", "Planar World z", "Planar World z"),
                 ("6", "Animated Particle UV", "The flip book of the particle system is used to determine the UVs"),
                 ("7", "Cubic Environment", "For Env. Layer: Cubic Environment"),
                 ("8", "Spherical Environment", "For Env. Layer: Spherical Environment"),
                 ("9", "UV Layer 3", "UV Layer 3"),
                 ("10", "UV Layer 4", "UV Layer 4"),
                 ("11", "Planar Local X", "Planar Local X"),
                 ("12", "Planar Local Y", "Planar Local Y"),
                 ("13", "Planar World X", "Planar World X"),
                 ("14", "Planar World Y", "Planar World Y"),
                 ("15", "Screen space", "Screen space"),
                 ("16", "Tri Planar World", "Tri Planar World"),
                 ("17", "Tri Planar World Local", "Tri Planar Local"),
                 ("18", "Tri Planar World Local Z", "Tri Planar World Local Z")
                 ] 

particleEmissionTypeList = [("0", "Constant", "Emitted particles fly towards a configureable direction with a configurable spread"), 
                        ("1", 'Radial', "Particles move into all kinds of directions"), 
                        ("2", 'Z Axis', 'Picks randomly to move in the direction of the positive or negative local Z-Axis for the emitter.e'),
                        ("3", 'Random', 'Picks an entirely arbitrary orientation.'),
                        ("4", 'Mesh Normal', 'when using a Mesh Emitter Shape, uses the normal of the face being emitted from as the direction vector.')]


particleAnimationSmoothTypeList = [
    ("0", "Linear", "Linear transitions without usage of hold time"),
    ("1", "Smooth", "Smooth transitions without usage of hold time"),
    ("2", "Bezier", "Bezier transitions without usage of hold time"),
    ("3", "Linear Hold", "Linear transitions with usage of hold time"),
    ("4", "Bezier Hold", "Bezier transitions with usage of hold time")
    ]


attachmentVolumeTypeList = [(shared.attachmentVolumeNone, "None", "No Volume, it's a simple attachment point"), 
                            (shared.attachmentVolumeCuboid, 'Cuboid', "Volume with the shape of a cuboid with the given width, length and height"),
                            (shared.attachmentVolumeSphere, 'Sphere', "Volume with the shape of a sphere with the given radius"), 
                            (shared.attachmentVolumeCapsule, 'Capsule', 'Volume with the shape of a cylinder with the given radius and height'),
                            ("3", 'Unknown 3', 'Unknown Volume with id 3'),
                            ("4", 'Unknown 4', 'Unknown Volume with id 4')
                           ]
                           
geometricShapeTypeList = [("0", 'Cuboid', "A cuboid with the given width, length and height"),
                         ("1", 'Sphere', "A sphere with the given radius"),
                         ("2", 'Capsule', 'A capsue which is based on a cylinder with the given radius and height'),
                        ]
                        
defaultSettingMesh = "MESH"
defaultSettingParticle = "PARTICLE"
defaultSettingDisplacement = "DISPLACEMENT"
defaultSettingComposite = "COMPOSITE"
defaultSettingTerrain = "TERRAIN"
defaultSettingVolume = "VOLUME"
defaultSettingVolumeNoise = "VOLUME_NOISE"
defaultSettingCreep = "CREEP"
defaultSettingSplatTerrainBake="STB"
defaultSettingLensFlare = "LENS_FLARE"
matDefaultSettingsList = [(defaultSettingMesh, "Mesh Standard Material", "A material for meshes"), 
                        (defaultSettingParticle, 'Particle Standard Material', "Material for particle systems"),
                        (defaultSettingDisplacement, "Displacement Material", "Moves the colors of the background to other locations"),
                        (defaultSettingComposite, "Composite Material", "A combination of multiple materials"),
                        (defaultSettingTerrain, "Terrain Material", "Makes the object look like the ground below it"),
                        (defaultSettingVolume, "Volume Material", "A fog like material"),
                        (defaultSettingVolumeNoise, "Volume Noise Material", "A fog like material"),
                        (defaultSettingCreep, "Creep Material", "Looks like creep if there is creep below the model and is invisible otherwise"),
                        (defaultSettingSplatTerrainBake, "STB Material", "Splat Terrain Bake Material"),
                        (defaultSettingLensFlare, "Lens Flare Material", "Lens flare material which can not be exported yet"),
                        ]


billboardBehaviorTypeList = [("0", "Local X", "Bone gets oriented around X towards camera but rotates then with the model"),
                             ("1", "Local Z", "Bone gets oriented around Z towards camera but rotates then with the model"),
                             ("2", "Local Y", "Bone gets oriented around Y towards camera but rotates then with the model"),
                             ("3", "World X", "Bone gets oriented around X towards camera, independent of model rotation"),
                             ("4", "World X", "Bone gets oriented around X towards camera, independent of model rotation"),
                             ("5", "World X", "Bone gets oriented around X towards camera, independent of model rotation"),
                             ("6", "World All", "Bone orients itself always towards camera and rotates around all axes to do so")
                            ]
                             
                     

matBlendModeList = [("0", "Opaque", "no description yet"), 
                        ("1", 'Alpha Blend', "no description yet"), 
                        ("2", 'Add', 'no description yet'),
                        ("3", 'Alpha Add', 'no description yet'),
                        ("4", 'Mod', 'no description yet'),
                        ("5", 'Mod 2x', 'no description yet')
                        ]

matLayerAndEmisBlendModeList = [("0", "Mod", "no description yet"), 
                        ("1", 'Mod 2x', "no description yet"), 
                        ("2", 'Add', 'no description yet'),
                        ("3", 'Blend', 'no description yet'),
                        ("4", 'Team Color Emissive Add', 'no description yet'),
                        ("5", 'Team Color Diffuse Add', 'no description yet')
                        ]

colorChannelSettingList = [
    (shared.colorChannelSettingRGB, "RGB", "Use red, green and blue color channel"),
    (shared.colorChannelSettingRGBA, "RGBA", "Use red, green, blue and alpha channel"),
    (shared.colorChannelSettingA, "Alpha Only", "Use alpha channel only"),
    (shared.colorChannelSettingR, "Red Only", "Use red color channel only"),
    (shared.colorChannelSettingG, "Green Only", "Use green color channel only"),
    (shared.colorChannelSettingB, "Blue Only", "Use blue color channel only")
    ]


matSpecularTypeList = [("0", "RGB", "no description yet"), 
                        ("1", 'Alpha Only', "no description yet")
                        ]
                        
rttChannelList = [("-1", "None", "None"),
                  ("0", "Layer 1", "Render To Texture Layer 1"),
                  ("1", "Layer 2", "Render To Texture Layer 2"),
                  ("2", "Layer 3", "Render To Texture Layer 3"),
                  ("3", "Layer 4", "Render To Texture Layer 4"),
                  ("4", "Layer 5", "Render To Texture Layer 5"),
                  ("5", "Layer 6", "Render To Texture Layer 6"),
                  ("6", "Layer 7", "Render To Texture Layer 7"),
]

fresnelTypeList = [("0", "Disabled", "Fresnel is disabled"),
                  ("1", "Enabled", "Strength of layer is based on fresnel formula"),
                  ("2", "Enabled; Inverted", "Strenth of layer is based on inverted fresnel formula")
]

videoModeList = [("0", "Loop", "Loop"),
                 ("1", "Hold", "Hold")
                ]

contentToImportList = [("EVERYTHING", "Everything", "Import everything included in the m3 file"),
                       ("MESH_WITH_MATERIALS_ONLY", "Mesh with materials only", "Import the mesh with its m3 materials only")
                       ]

lightTypeList = [# directional light isn't supported yet: ("0", "Directional", ""),
                 (shared.lightTypePoint, "Point", "Light are generated around a point"),
                 (shared.lightTypeSpot, "Spot", "")
                 ]


animationExportAmount = [(shared.exportAmountAllAnimations, "All animations", "All animations will be exported"), 
                    (shared.exportAmountCurrentAnimation, "Current animation", "Only the current animation will be exported")
                    # Possible future additions: CURRENT_FRAME or FIRST_FRAME
                   ]


class M3AnimIdData(bpy.types.PropertyGroup):
    # animId is actually an unsigned integer but blender can store only signed ones
    # thats why the number range needs to be moved into the negative for storage
    animIdMinus2147483648 = bpy.props.IntProperty(name="animId", options=set())
    longAnimId = bpy.props.StringProperty(name="longAnimId", options=set())

class M3AnimatedPropertyReference(bpy.types.PropertyGroup):
    longAnimId = bpy.props.StringProperty(name="longAnimId", options=set())
    
class AssignedActionOfM3Animation(bpy.types.PropertyGroup):
    targetName = bpy.props.StringProperty(name="targetName", options=set())
    actionName = bpy.props.StringProperty(name="actionName", options=set())

class M3TransformationCollection(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="all", options=set())
    animatedProperties = bpy.props.CollectionProperty(type=M3AnimatedPropertyReference, options=set())
    runsConcurrent = bpy.props.BoolProperty(default=True, options=set())
    priority = bpy.props.IntProperty(subtype="UNSIGNED",options=set())

    
class M3Animation(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Stand", options=set())
    startFrame = bpy.props.IntProperty(subtype="UNSIGNED", options=set())
    useSimulateFrame = bpy.props.BoolProperty(default=False, options=set())
    simulateFrame = bpy.props.IntProperty(subtype="UNSIGNED", default=0, options=set())
    exlusiveEndFrame = bpy.props.IntProperty(subtype="UNSIGNED", options=set())
    assignedActions = bpy.props.CollectionProperty(type=AssignedActionOfM3Animation, options=set())
    transformationCollections = bpy.props.CollectionProperty(type=M3TransformationCollection, options=set())
    transformationCollectionIndex = bpy.props.IntProperty(default=0, options=set())
    movementSpeed = bpy.props.FloatProperty(name="mov. speed", options=set())
    frequency = bpy.props.IntProperty(subtype="UNSIGNED",options=set())
    notLooping = bpy.props.BoolProperty(options=set())
    alwaysGlobal = bpy.props.BoolProperty(options=set())
    globalInPreviewer = bpy.props.BoolProperty(options=set())

class M3MaterialLayer(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="Material Layer")
    imagePath = bpy.props.StringProperty(name="image path", default="", options=set())
    unknownbd3f7b5d = bpy.props.IntProperty(name="unknownbd3f7b5d", default=-1, options=set())
    color = bpy.props.FloatVectorProperty(name="color", default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=4, subtype="COLOR", options={"ANIMATABLE"})
    textureWrapX = bpy.props.BoolProperty(options=set(), default=True)
    textureWrapY = bpy.props.BoolProperty(options=set(), default=True)
    invertColor = bpy.props.BoolProperty(options=set(), default=False)
    clampColor = bpy.props.BoolProperty(options=set(), default=False)
    colorEnabled = bpy.props.BoolProperty(options=set(), default=False)
    uvSource = bpy.props.EnumProperty(items=uvSourceList, options=set(), default="0")
    brightMult = bpy.props.FloatProperty(name="bright. mult.",options={"ANIMATABLE"}, default=1.0)
    uvOffset = bpy.props.FloatVectorProperty(name="uv offset", default=(0.0, 0.0), size=2, subtype="XYZ", options={"ANIMATABLE"})
    uvAngle = bpy.props.FloatVectorProperty(name="uv offset", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    uvTiling = bpy.props.FloatVectorProperty(name="uv tiling", default=(1.0, 1.0), size=2, subtype="XYZ", options={"ANIMATABLE"})
    triPlanarOffset = bpy.props.FloatVectorProperty(name="tri planer offset", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    triPlanarScale = bpy.props.FloatVectorProperty(name="tri planer scale", default=(1.0, 1.0, 1.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    flipBookRows = bpy.props.IntProperty(name="flipBookRows", default=0, options=set())
    flipBookColumns = bpy.props.IntProperty(name="flipBookColumns", default=0, options=set())
    flipBookFrame = bpy.props.IntProperty(name="flipBookFrame", default=0, options={"ANIMATABLE"})
    midtoneOffset = bpy.props.FloatProperty(name="midtone offset", options={"ANIMATABLE"}, description="Can be used to make dark areas even darker so that only the bright regions remain")
    brightness = bpy.props.FloatProperty(name="brightness", options={"ANIMATABLE"}, default=1.0)
    rttChannel = bpy.props.EnumProperty(items=rttChannelList, options=set(), default="-1")
    colorChannelSetting = bpy.props.EnumProperty(items=colorChannelSettingList, options=set(), default=shared.colorChannelSettingRGB)
    fresnelType =  bpy.props.EnumProperty(items=fresnelTypeList, options=set(), default="0")
    invertedFresnel = bpy.props.BoolProperty(options=set())
    fresnelExponent = bpy.props.FloatProperty(default=4.0, options=set())
    fresnelMin = bpy.props.FloatProperty(default=0.0, options=set())
    fresnelMax = bpy.props.FloatProperty(default=1.0, options=set())
    fresnelMaskX = bpy.props.FloatProperty(options=set(), min=0.0, max=1.0)
    fresnelMaskY = bpy.props.FloatProperty(options=set(), min=0.0, max=1.0)
    fresnelMaskZ = bpy.props.FloatProperty(options=set(), min=0.0, max=1.0)
    fresnelRotationYaw = bpy.props.FloatProperty(subtype="ANGLE", options=set())
    fresnelRotationPitch = bpy.props.FloatProperty(subtype="ANGLE", options=set())
    fresnelLocalTransform = bpy.props.BoolProperty(options=set(), default=False)
    fresnelDoNotMirror = bpy.props.BoolProperty(options=set(), default=False)
    videoFrameRate = bpy.props.IntProperty(options=set(), default=24)
    videoStartFrame = bpy.props.IntProperty(options=set(), default=0)
    videoEndFrame = bpy.props.IntProperty(options=set(), default=-1)
    videoMode = bpy.props.EnumProperty(items=videoModeList, options=set(), default="0")
    videoSyncTiming = bpy.props.BoolProperty(options=set())
    videoPlay = bpy.props.BoolProperty(name="videoPlay", options={"ANIMATABLE"}, default=True)
    videoRestart = bpy.props.BoolProperty(name="videoRestart", options={"ANIMATABLE"}, default=True)

class M3Material(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", options=set())
    materialType = bpy.props.IntProperty(options=set())
    materialIndex = bpy.props.IntProperty(options=set())
    
class M3StandardMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())
    blendMode = bpy.props.EnumProperty(items=matBlendModeList, options=set(), default="0")
    priority = bpy.props.IntProperty(options=set())
    specularity = bpy.props.FloatProperty(name="specularity", options=set())
    cutoutThresh = bpy.props.IntProperty(name="cutoutThresh", min=0, max=255, default=0, options=set())
    specMult = bpy.props.FloatProperty(name="spec. mult.", options=set(), default=1.0)
    emisMult = bpy.props.FloatProperty(name="emis. mult.", options=set(), default=1.0)
    layerBlendType = bpy.props.EnumProperty(items=matLayerAndEmisBlendModeList, options=set(), default="2")
    emisBlendType = bpy.props.EnumProperty(items=matLayerAndEmisBlendModeList, options=set(), default="3")
    specType = bpy.props.EnumProperty(items=matSpecularTypeList, options=set(), default="0")
    unfogged = bpy.props.BoolProperty(options=set(), default=True)
    twoSided = bpy.props.BoolProperty(options=set(), default=False)
    unshaded = bpy.props.BoolProperty(options=set(), default=False)
    noShadowsCast = bpy.props.BoolProperty(options=set(), default=False)
    noHitTest = bpy.props.BoolProperty(options=set(), default=False)
    noShadowsReceived = bpy.props.BoolProperty(options=set(), default=False)
    depthPrepass = bpy.props.BoolProperty(options=set(), default=False)
    useTerrainHDR = bpy.props.BoolProperty(options=set(), default=False)
    splatUVfix = bpy.props.BoolProperty(options=set(), default=False)
    softBlending = bpy.props.BoolProperty(options=set(), default=False)
    forParticles = bpy.props.BoolProperty(options=set(), default=False)
    transparency = bpy.props.BoolProperty(options=set(), default=False)
    disableSoft = bpy.props.BoolProperty(options=set(), default=False)
    darkNormalMapping = bpy.props.BoolProperty(options=set(), default=False)
    decalRequiredOnLowEnd = bpy.props.BoolProperty(options=set(), default=False)
    acceptSplats = bpy.props.BoolProperty(options=set(), default=False)
    acceptSplatsOnly = bpy.props.BoolProperty(options=set(), default=False)
    emissiveRequiredOnLowEnd = bpy.props.BoolProperty(options=set(), default=False)
    backgroundObject = bpy.props.BoolProperty(options=set(), default=False)
    zpFillRequiredOnLowEnd = bpy.props.BoolProperty(options=set(), default=False)
    excludeFromHighlighting = bpy.props.BoolProperty(options=set(), default=False)
    clampOutput = bpy.props.BoolProperty(options=set(), default=False)
    geometryVisible = bpy.props.BoolProperty(options=set(), default=True)
    
    depthBlendFalloff = bpy.props.FloatProperty(name="depth blend falloff", options=set(), update=handleDepthBlendFalloffChanged, default=0.0)
    useDepthBlendFalloff = bpy.props.BoolProperty(options=set(), update=handleUseDepthBlendFalloffChanged, description="Should be true for particle system materials", default=False)
    useVertexColor = bpy.props.BoolProperty(options=set(), description="The vertex color layer named color will be used to tint the model", default=False)
    useVertexAlpha = bpy.props.BoolProperty(options=set(), description="The vertex color layer named alpha, will be used to determine the alpha of the model", default=False)
    unknownFlag0x200 = bpy.props.BoolProperty(options=set())

class M3DisplacementMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    strengthFactor = bpy.props.FloatProperty(name="strength factor",options={"ANIMATABLE"}, default=1.0, description="Factor that gets multiplicated with the strength values")
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())
    priority = bpy.props.IntProperty(options=set())
    
class M3CompositeMaterialSection(bpy.types.PropertyGroup):
    # The material name is getting called "name" so that blender names it properly in the list view
    name = bpy.props.StringProperty(options=set()) 
    alphaFactor = bpy.props.FloatProperty(name="alphaFactor", options={"ANIMATABLE"}, min=0.0, max=1.0, default=1.0, description="Defines the factor with which the alpha channel gets multiplicated")

class M3CompositeMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())
    sections = bpy.props.CollectionProperty(type=M3CompositeMaterialSection, options=set())
    sectionIndex = bpy.props.IntProperty(options=set(), default=0)
    
class M3TerrainMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())

class M3VolumeMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    volumeDensity = bpy.props.FloatProperty(name="volume density",options={"ANIMATABLE"}, default=0.3, description="Factor that gets multiplicated with the strength values")
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())

class M3VolumeNoiseMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    volumeDensity = bpy.props.FloatProperty(name="volume density",options={"ANIMATABLE"}, default=0.3, description="Factor that gets multiplicated with the strength values")
    nearPlane = bpy.props.FloatProperty(name="near plane",options={"ANIMATABLE"}, default=0.0)
    falloff = bpy.props.FloatProperty(name="falloff",options={"ANIMATABLE"}, default=0.9)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())
    scrollRate = bpy.props.FloatVectorProperty(name="scroll rate", default=(0.0, 0.0, 0.8), size=3, subtype="XYZ", options={"ANIMATABLE"})
    translation = bpy.props.FloatVectorProperty(name="translation", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    scale = bpy.props.FloatVectorProperty(name="scale", default=(2.0, 2.0, 1.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    rotation = bpy.props.FloatVectorProperty(name="rotation", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    alphaTreshhold = bpy.props.IntProperty(options=set(), default=0)
    drawAfterTransparency = bpy.props.BoolProperty(options=set(), default=False)

class M3CreepMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())

class M3STBMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())

class M3LensFlareMaterial(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Material", update=handleMaterialNameChange, options=set())
    # the following field gets used to update the name of the material reference:
    materialReferenceIndex = bpy.props.IntProperty(options=set(), default=-1)
    layers = bpy.props.CollectionProperty(type=M3MaterialLayer, options=set())

class M3Camera(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="Camera", update=handleCameraNameChange, options=set())
    oldName = bpy.props.StringProperty(name="oldName", options=set())
    fieldOfView = bpy.props.FloatProperty(name="fieldOfView", options={"ANIMATABLE"}, default=0.5)
    farClip = bpy.props.FloatProperty(name="farClip", options={"ANIMATABLE"}, default=10.0)
    nearClip = bpy.props.FloatProperty(name="nearClip", options={"ANIMATABLE"}, default=10.0)
    clip2 = bpy.props.FloatProperty(name="clip2", options={"ANIMATABLE"}, default=10.0)
    focalDepth = bpy.props.FloatProperty(name="focalDepth", options={"ANIMATABLE"}, default=2)
    falloffStart = bpy.props.FloatProperty(name="falloffStart", options={"ANIMATABLE"}, default=1.0)
    falloffEnd = bpy.props.FloatProperty(name="falloffEnd", options={"ANIMATABLE"}, default=2.0)
    depthOfField = bpy.props.FloatProperty(name="depthOfField", options={"ANIMATABLE"}, default=0.5)

class M3Boundings(bpy.types.PropertyGroup):
    radius = bpy.props.FloatProperty(name="radius", options=set(), default=2.0)
    center = bpy.props.FloatVectorProperty(name="center", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options=set())
    size = bpy.props.FloatVectorProperty(name="size", default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", options=set())


class M3ParticleSpawnPoint(bpy.types.PropertyGroup):
    location = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), name="location", size=3, subtype="XYZ", options={"ANIMATABLE"}, description="The first two values are the initial and final size of particles")


class M3ParticleSystemCopy(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(options=set(), update=handleParticleSystemCopyRename)
    boneName = bpy.props.StringProperty(options=set())
    emissionRate = bpy.props.FloatProperty(default=10.0, name="emiss. rate", options={"ANIMATABLE"})
    partEmit = bpy.props.IntProperty(default=0, subtype="UNSIGNED", options={"ANIMATABLE"})


class M3ParticleSystem(bpy.types.PropertyGroup):

    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(options=set(), update=handleParticleSystemTypeOrNameChange)
    boneName = bpy.props.StringProperty(options=set())
    updateBlenderBoneShapes = bpy.props.BoolProperty(default=True, options=set())
    materialName = bpy.props.StringProperty(options=set())
    maxParticles = bpy.props.IntProperty(default=20, subtype="UNSIGNED",options=set())
    emissionSpeed1 = bpy.props.FloatProperty(name="emis. speed 1",options={"ANIMATABLE"}, default=0.0, description="The initial speed of the particles at emission")
    emissionSpeed2 = bpy.props.FloatProperty(default=1.0, name="emiss. speed 2",options={"ANIMATABLE"}, description="If emission speed randomization is enabled this value specfies the other end of the range of random speeds")
    randomizeWithEmissionSpeed2 = bpy.props.BoolProperty(options=set(),default=False, description="Specifies if the second emission speed value should be used to generate random emission speeds")
    emissionAngleX = bpy.props.FloatProperty(default=0.0, name="emis. angle X", subtype="ANGLE", options={"ANIMATABLE"}, description="Specifies the X rotation of the emission vector")
    emissionAngleY = bpy.props.FloatProperty(default=0.0, name="emis. angle Y", subtype="ANGLE", options={"ANIMATABLE"}, description="Specifies the Y rotation of the emission vector")
    emissionSpreadX = bpy.props.FloatProperty(default=0.0, name="emissionSpreadX", options={"ANIMATABLE"}, description="Specifies in radian by how much the emission vector can be randomly rotated around the X axis")
    emissionSpreadY = bpy.props.FloatProperty(default=0.0, name="emissionSpreadY", options={"ANIMATABLE"}, description="Specifies in radian by how much the emission vector can be randomly rotated around the Y axis")
    lifespan1 = bpy.props.FloatProperty(default=0.5, name="lifespan1", options={"ANIMATABLE"},  description="Specfies how long it takes before the particles start to decay")
    lifespan2 = bpy.props.FloatProperty(default=5.0, name="lifespan2", options={"ANIMATABLE"}, description="If random lifespans are enabled this specifies the other end of the range for random lifespan values")
    randomizeWithLifespan2 = bpy.props.BoolProperty(default=True, name="randomizeWithLifespan2", options=set(), description="Specifies if particles should have random lifespans")
    zAcceleration = bpy.props.FloatProperty(default=0.0, name="z acceleration",options=set(), description="Negative gravity which does not get influenced by the emission vector")
    sizeAnimationMiddle = bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0, subtype="FACTOR", name="sizeAnimationMiddle", options=set(), description="Percentage of lifetime when the scale animation reaches reaches its middle value")
    colorAnimationMiddle = bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0, subtype="FACTOR", name="colorAnimationMiddle", options=set(), description="Percentage of lifetime when the color animation (without alpha) reaches reaches its middle value")
    alphaAnimationMiddle = bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0, subtype="FACTOR", name="alphaAnimationMiddle", options=set(), description="Percentage of lifetime when the alpha animation reaches reaches its middle value")
    rotationAnimationMiddle = bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0, subtype="FACTOR", name="rotationAnimationMiddle", options=set(), description="Percentage of lifetime when the scale animation reaches reaches its middle value")
    sizeHoldTime = bpy.props.FloatProperty(default=0.3, min=0.0, max=1.0, name="sizeHoldTime", options=set(), description="Factor of particle liftime to hold the middle size value")
    colorHoldTime = bpy.props.FloatProperty(default=0.3, min=0.0, max=1.0, name="colorHoldTime", options=set(), description="Factor of particle lifetime to hold the middle color and alpha value")
    alphaHoldTime = bpy.props.FloatProperty(default=0.3, min=0.0, max=1.0, name="alphaHoldTime", options=set(), description="Factor of particle lifetime to hold the middle rotation value")    
    rotationHoldTime = bpy.props.FloatProperty(default=0.3, min=0.0, max=1.0, name="rotationHoldTime", options=set(), description="Factor of particle lifetime to hold the middle rotation value")    
    sizeSmoothingType = bpy.props.EnumProperty(default="0", items=particleAnimationSmoothTypeList, options=set(), description="Determines the shape of the size curve based on the intial, middle , final and hold time value")    
    colorSmoothingType = bpy.props.EnumProperty(default="0", items=particleAnimationSmoothTypeList, options=set(), description="Determines the shape of the color curve based on the intial, middle , final and hold time value")    
    rotationSmoothingType = bpy.props.EnumProperty(default="0", items=particleAnimationSmoothTypeList, options=set(), description="Determines the shape of the rotation curve based on the intial, middle , final and hold time value")    
    particleSizes1 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), name="particle sizes 1", size=3, subtype="XYZ", options={"ANIMATABLE"}, description="The first two values are the initial and final size of particles")
    rotationValues1 = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), name="rotation values 1", size=3, subtype="XYZ", options={"ANIMATABLE"}, description="The first value is the inital rotation and the second value is the rotation speed")
    initialColor1 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, name="initial color 1", size=4, subtype="COLOR", options={"ANIMATABLE"}, description="Color of the particle when it gets emitted")
    middleColor1 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, name="unknown color 1", size=4, subtype="COLOR", options={"ANIMATABLE"})
    finalColor1 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 0.5), min = 0.0, max = 1.0, name="final color 1", size=4, subtype="COLOR", options={"ANIMATABLE"}, description="The color the particle will have when it vanishes")
    slowdown = bpy.props.FloatProperty(default=1.0, min=0.0, name="slowdown" ,options=set(), description="The amounth of speed reduction in the particles lifetime")
    mass = bpy.props.FloatProperty(default=0.001, name="mass",options=set())
    mass2 = bpy.props.FloatProperty(default=1.0, name="mass2",options=set())
    randomizeWithMass2 = bpy.props.BoolProperty(options=set(),default=True, description="Specifies if the second mass value should be used to generate random mass values")
    unknownFloat2c = bpy.props.FloatProperty(default=2.0, name="unknownFloat2c",options=set())
    trailingEnabled = bpy.props.BoolProperty(default=True, options=set(), description="If trailing is enabled then particles don't follow the particle emitter")
    emissionRate = bpy.props.FloatProperty(default=10.0, name="emiss. rate", options={"ANIMATABLE"})
    emissionAreaType = bpy.props.EnumProperty(default="2", items=emissionAreaTypeList, update=handleParticleSystemTypeOrNameChange, options=set())
    cutoutEmissionArea = bpy.props.BoolProperty(options=set())
    emissionAreaSize = bpy.props.FloatVectorProperty(default=(0.1, 0.1, 0.1), name="emis. area size", update=handleParticleSystemAreaSizeChange, size=3, subtype="XYZ", options={"ANIMATABLE"})
    emissionAreaCutoutSize = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), name="tail unk.", size=3, subtype="XYZ", options={"ANIMATABLE"})
    emissionAreaRadius = bpy.props.FloatProperty(default=2.0, name="emis. area radius", update=handleParticleSystemAreaSizeChange, options={"ANIMATABLE"})
    emissionAreaCutoutRadius = bpy.props.FloatProperty(default=0.0, name="spread unk.", options={"ANIMATABLE"})
    spawnPoints = bpy.props.CollectionProperty(type=M3ParticleSpawnPoint)
    emissionType = bpy.props.EnumProperty(default="0", items=particleEmissionTypeList, options=set())
    randomizeWithParticleSizes2 = bpy.props.BoolProperty(default=False, options=set(), description="Specifies if particles have random sizes")
    particleSizes2 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), name="particle sizes 2", size=3, subtype="XYZ", options={"ANIMATABLE"}, description="The first two values are used to determine a random initial and final size for a particle")
    randomizeWithRotationValues2 = bpy.props.BoolProperty(default=False, options=set())
    rotationValues2 = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), name="rotation values 2", size=3, subtype="XYZ", options={"ANIMATABLE"})
    randomizeWithColor2 = bpy.props.BoolProperty(default=False, options=set())
    initialColor2 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, name="initial color 2", size=4, subtype="COLOR", options={"ANIMATABLE"})
    middleColor2 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, name="unknown color 2", size=4, subtype="COLOR", options={"ANIMATABLE"})
    finalColor2 = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0, 0.0), min = 0.0, max = 1.0, name="final color 2", size=4, subtype="COLOR", options={"ANIMATABLE"})
    partEmit = bpy.props.IntProperty(default=0, subtype="UNSIGNED", options={"ANIMATABLE"})
    phase1StartImageIndex = bpy.props.IntProperty(default=0, min=0, max=255, subtype="UNSIGNED", options=set(), description="Specifies the cell index shown at start of phase 1 when the image got divided into rows and collumns")
    phase1EndImageIndex = bpy.props.IntProperty(default=0, min=0, max=255, subtype="UNSIGNED", options=set(), description="Specifies the cell index shown at end of phase 1 when the image got divided into rows and collumns")
    phase2StartImageIndex = bpy.props.IntProperty(default=0, min=0, max=255, subtype="UNSIGNED", options=set(), description="Specifies the cell index shown at start of phase 2 when the image got divided into rows and collumns")
    phase2EndImageIndex = bpy.props.IntProperty(default=0, min=0, max=255, subtype="UNSIGNED", options=set(), description="Specifies the cell index shown at end of phase 2 when the image got divided into rows and collumns")
    relativePhase1Length = bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0, subtype="FACTOR", name="relative phase 1 length", options=set(), description="A value of 0.4 means that 40% of the lifetime of the particle the phase 1 image animation will play")
    numberOfColumns = bpy.props.IntProperty(default=0, min=0, subtype="UNSIGNED", name="columns", options=set(), description="Specifies in how many columns the image gets divided")
    numberOfRows = bpy.props.IntProperty(default=0, min=0, subtype="UNSIGNED", name="rows", options=set(), description="Specifies in how many rows the image gets divided")
    columnWidth = bpy.props.FloatProperty(default=float("inf"), min=0.0, max=1.0, name="columnWidth", options=set(), description="Specifies the width of one column, relative to an image with width 1")
    rowHeight = bpy.props.FloatProperty(default=float("inf"), min=0.0, max=1.0, name="rowHeight", options=set(), description="Specifies the height of one row, relative to an image with height 1")
    unknownFloat4 = bpy.props.FloatProperty(default=0.0, name="unknownFloat4",options=set())
    unknownFloat5 = bpy.props.FloatProperty(default=1.0, name="unknownFloat5",options=set())
    unknownFloat6 = bpy.props.FloatProperty(default=1.0, name="unknownFloat6",options=set())
    unknownFloat7 = bpy.props.FloatProperty(default=1.0, name="unknownFloat7",options=set())
    particleType = bpy.props.EnumProperty(default="0", items=particleTypeList, options=set())
    lengthWidthRatio = bpy.props.FloatProperty(default=1.0, name="lengthWidthRatio",options=set())
    localForceChannels = bpy.props.BoolVectorProperty(default=tuple(16*[False]), size=16, subtype="LAYER", options=set(), description="If a model internal force shares a local force channel with a particle system then it affects it")
    worldForceChannels = bpy.props.BoolVectorProperty(default=tuple(16*[False]), size=16, subtype="LAYER", options=set(), description="If a force shares a force channel with a particle system then it affects it")
    copies = bpy.props.CollectionProperty(type=M3ParticleSystemCopy)
    copyIndex = bpy.props.IntProperty(options=set(), update=handlePartileSystemCopyIndexChanged)
    trailingParticlesName = bpy.props.StringProperty(options=set())
    trailingParticlesChance = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0, subtype="FACTOR", name="trailingParticlesChance",options=set())
    trailingParticlesRate = bpy.props.FloatProperty(default=10.0, name="trail. emiss. rate", options={"ANIMATABLE"})
    noiseAmplitude = bpy.props.FloatProperty(default=0.0, name="noiseAmplitude",options=set())
    noiseFrequency = bpy.props.FloatProperty(default=0.0, name="noiseFrequency",options=set())
    noiseCohesion = bpy.props.FloatProperty(default=0.0, name="noiseCohesion",options=set(), description="Prevents the particles from spreading to far from noise")
    noiseEdge = bpy.props.FloatProperty(default=0.0, min=0.0, max=0.5, subtype="FACTOR", name="noiseEdge", options=set(), description="The closer the value is to 0.5 the less noise will be at the start of particles life time")
    sort = bpy.props.BoolProperty(options=set())
    collideTerrain = bpy.props.BoolProperty(options=set())
    collideObjects = bpy.props.BoolProperty(options=set())
    spawnOnBounce = bpy.props.BoolProperty(options=set())
    inheritEmissionParams = bpy.props.BoolProperty(options=set())
    inheritParentVel = bpy.props.BoolProperty(options=set())
    sortByZHeight = bpy.props.BoolProperty(options=set())
    reverseIteration = bpy.props.BoolProperty(options=set())
    litParts = bpy.props.BoolProperty(options=set())
    randFlipBookStart = bpy.props.BoolProperty(options=set())
    multiplyByGravity = bpy.props.BoolProperty(options=set())
    clampTailParts = bpy.props.BoolProperty(options=set())
    spawnTrailingParts = bpy.props.BoolProperty(options=set())
    fixLengthTailParts = bpy.props.BoolProperty(options=set())
    useVertexAlpha = bpy.props.BoolProperty(options=set())
    modelParts = bpy.props.BoolProperty(options=set())
    swapYZonModelParts = bpy.props.BoolProperty(options=set())
    scaleTimeByParent = bpy.props.BoolProperty(options=set())
    useLocalTime = bpy.props.BoolProperty(options=set())
    simulateOnInit = bpy.props.BoolProperty(options=set())
    copy = bpy.props.BoolProperty(options=set())

class M3RibbonEndPoint(bpy.types.PropertyGroup):
    # nane is also bone name
    name = bpy.props.StringProperty(options=set())
    

class M3Ribbon(bpy.types.PropertyGroup):
    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(options=set())
    boneSuffix = bpy.props.StringProperty(options=set(), update=handleRibbonBoneSuffixChange, default="Particle System")
    boneName = bpy.props.StringProperty(options=set())
    updateBlenderBoneShapes = bpy.props.BoolProperty(default=True, options=set())
    materialName = bpy.props.StringProperty(options=set())
    waveLength = bpy.props.FloatProperty(default=1.0, name="waveLength", options={"ANIMATABLE"})
    tipOffsetZ = bpy.props.FloatProperty(default=0.0, name="tipOffsetZ", options=set())
    centerBias = bpy.props.FloatProperty(default=0.5, name="centerBias", options=set())
    radiusScale =  bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), size=3, subtype="XYZ", options={"ANIMATABLE"})
    twist = bpy.props.FloatProperty(default=0.0, name="twist", options=set())
    baseColoring = bpy.props.FloatVectorProperty(name="color", default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=4, subtype="COLOR", options={"ANIMATABLE"})
    centerColoring = bpy.props.FloatVectorProperty(name="color", default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=4, subtype="COLOR", options={"ANIMATABLE"})
    tipColoring = bpy.props.FloatVectorProperty(name="color", default=(1.0, 1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=4, subtype="COLOR", options={"ANIMATABLE"})
    stretchAmount = bpy.props.FloatProperty(default=1.0, name="stretchAmount", options=set())
    stretchLimit = bpy.props.FloatProperty(default=1.0, name="stretchLimit", options=set())
    surfaceNoiseAmplitude = bpy.props.FloatProperty(default=0.0, name="surfaceNoiseAmplitude", options=set())
    surfaceNoiseNumberOfWaves = bpy.props.FloatProperty(default=0.0, name="surfaceNoiseNumberOfWaves", options=set())
    surfaceNoiseFrequency = bpy.props.FloatProperty(default=0.0, name="surfaceNoiseFrequency", options=set())
    surfaceNoiseScale = bpy.props.FloatProperty(default=0.2, name="surfaceNoiseScale", options=set())
    ribbonType = bpy.props.EnumProperty(default="0", items=ribbonTypeList, options=set())
    ribbonDivisions = bpy.props.FloatProperty(default=20.0, name="ribbonDivisions", options=set())
    ribbonSides = bpy.props.IntProperty(default=5, subtype="UNSIGNED",options=set())
    ribbonLength = bpy.props.FloatProperty(default=1.0, name="ribbonLength", options={"ANIMATABLE"})
    directionVariationBool = bpy.props.BoolProperty(default=False, options=set())
    directionVariationAmount = bpy.props.FloatProperty(default=0.0, name="directionVariationAmount", options={"ANIMATABLE"})
    directionVariationFrequency = bpy.props.FloatProperty(default=0.0, name="directionVariationFrequency", options={"ANIMATABLE"})
    amplitudeVariationBool = bpy.props.BoolProperty(default=False, options=set())
    amplitudeVariationAmount = bpy.props.FloatProperty(default=0.0, name="amplitudeVariationAmount", options={"ANIMATABLE"})
    amplitudeVariationFrequency = bpy.props.FloatProperty(default=0.0, name="amplitudeVariationFrequency", options={"ANIMATABLE"})
    lengthVariationBool = bpy.props.BoolProperty(default=False, options=set())
    lengthVariationAmount = bpy.props.FloatProperty(default=0.0, name="lengthVariationAmount", options={"ANIMATABLE"})
    lengthVariationFrequency = bpy.props.FloatProperty(default=0.0, name="lengthVariationFrequency", options={"ANIMATABLE"})
    radiusVariationBool = bpy.props.BoolProperty(default=False, options=set())
    radiusVariationAmount = bpy.props.FloatProperty(default=0.0, name="radiusVariationAmount", options={"ANIMATABLE"})
    radiusVariationFrequency = bpy.props.FloatProperty(default=0.0, name="radiusVariationFrequency", options={"ANIMATABLE"})
    collideWithTerrain = bpy.props.BoolProperty(default=False, options=set())
    collideWithObjects = bpy.props.BoolProperty(default=False, options=set())
    edgeFalloff = bpy.props.BoolProperty(default=False, options=set())
    inheritParentVelocity = bpy.props.BoolProperty(default=False, options=set())
    smoothSize = bpy.props.BoolProperty(default=False, options=set())
    bezierSmoothSize = bpy.props.BoolProperty(default=False, options=set())
    useVertexAlpha = bpy.props.BoolProperty(default=False, options=set())
    scaleTimeByParent = bpy.props.BoolProperty(default=False, options=set())
    forceLegacy = bpy.props.BoolProperty(default=False, options=set())
    useLocaleTime = bpy.props.BoolProperty(default=False, options=set())
    simulateOnInitialization = bpy.props.BoolProperty(default=False, options=set())
    useLengthAndTime = bpy.props.BoolProperty(default=False, options=set())
    endPoints = bpy.props.CollectionProperty(type=M3RibbonEndPoint)
    endPointIndex = bpy.props.IntProperty(default=-1, options=set(), update=handleRibbonEndPointIndexChanged)


class M3Force(bpy.types.PropertyGroup):
    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(options=set())
    updateBlenderBoneShape = bpy.props.BoolProperty(default=True, options=set())
    boneSuffix = bpy.props.StringProperty(options=set(), update=handleForceTypeOrBoneSuffixChange, default="Particle System")
    boneName = bpy.props.StringProperty(options=set())
    type = bpy.props.EnumProperty(default="0", items=forceTypeList, update=handleForceTypeOrBoneSuffixChange, options=set())
    shape = bpy.props.EnumProperty(default="0", items=forceShapeList, update=handleForceTypeOrBoneSuffixChange, options=set())
    channels = bpy.props.BoolVectorProperty(default=tuple(32*[False]), size=32, subtype="LAYER", options=set(), description="If a force shares a force channel with a particle system then it affects it")
    strength = bpy.props.FloatProperty(default=1.0, name="Strength", options={"ANIMATABLE"})
    width = bpy.props.FloatProperty(default=1.0, name="Radius/Width", update=handleForceRangeUpdate, options={"ANIMATABLE"})
    height = bpy.props.FloatProperty(default=0.05, name="Height/Angle", options={"ANIMATABLE"})
    length = bpy.props.FloatProperty(default=0.05, name="Length", options={"ANIMATABLE"})
    useFalloff = bpy.props.BoolProperty(options=set())
    useHeightGradient = bpy.props.BoolProperty(options=set())
    unbounded = bpy.props.BoolProperty(options=set())

class M3PhysicsShape(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(options=set())
    updateBlenderBoneShapes = bpy.props.BoolProperty(default=True, options=set())
    offset = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", update=handlePhysicsShapeUpdate)
    rotationEuler = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype="EULER", unit="ROTATION", update=handlePhysicsShapeUpdate)
    scale = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), size=3, subtype="XYZ", update=handlePhysicsShapeUpdate)
    shape = bpy.props.EnumProperty(default="0", items=physicsShapeTypeList, update=handlePhysicsShapeUpdate, options=set())
    meshObjectName = bpy.props.StringProperty(name="meshName", options=set())
    # TODO: convex hull properties...
    size0 = bpy.props.FloatProperty(default=1.0, name="size0", update=handlePhysicsShapeUpdate, options=set())
    size1 = bpy.props.FloatProperty(default=1.0, name="size1", update=handlePhysicsShapeUpdate, options=set())
    size2 = bpy.props.FloatProperty(default=1.0, name="size2", update=handlePhysicsShapeUpdate, options=set())

class M3RigidBody(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(options=set())
    boneName = bpy.props.StringProperty(name="boneName", update=handleRigidBodyBoneChange, options=set())
    unknownAt0 = bpy.props.FloatProperty(default=5.0, name="unknownAt0", options=set())
    unknownAt4 = bpy.props.FloatProperty(default=4.0, name="unknownAt4", options=set())
    unknownAt8 = bpy.props.FloatProperty(default=0.8, name="unknownAt8", options=set())
    # skip other unknown values for now
    physicsShapes = bpy.props.CollectionProperty(type=M3PhysicsShape)
    physicsShapeIndex = bpy.props.IntProperty(options=set())
    collidable = bpy.props.BoolProperty(default=True, options=set())
    walkable = bpy.props.BoolProperty(default=False, options=set())
    stackable = bpy.props.BoolProperty(default=False, options=set())
    simulateOnCollision = bpy.props.BoolProperty(default=False, options=set())
    ignoreLocalBodies = bpy.props.BoolProperty(default=False, options=set())
    alwaysExists = bpy.props.BoolProperty(default=False, options=set())
    doNotSimulate = bpy.props.BoolProperty(default=False, options=set())
    localForces = bpy.props.BoolVectorProperty(default=tuple(16*[False]), size=16, subtype="LAYER", options=set())
    wind = bpy.props.BoolProperty(default=False, options=set())
    explosion = bpy.props.BoolProperty(default=False, options=set())
    energy = bpy.props.BoolProperty(default=False, options=set())
    blood = bpy.props.BoolProperty(default=False, options=set())
    magnetic = bpy.props.BoolProperty(default=False, options=set())
    grass = bpy.props.BoolProperty(default=False, options=set())
    brush = bpy.props.BoolProperty(default=False, options=set())
    trees = bpy.props.BoolProperty(default=False, options=set())
    priority = bpy.props.IntProperty(default=0, options=set())

class M3AttachmentPoint(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", options=set())
    updateBlenderBone = bpy.props.BoolProperty(default=True, options=set())
    boneSuffix = bpy.props.StringProperty(name="boneSuffix", update=handleAttachmentPointTypeOrBoneSuffixChange)
    boneName = bpy.props.StringProperty(name="boneName", options=set())
    volumeType = bpy.props.EnumProperty(default="-1",update=handleAttachmentVolumeTypeChange, items=attachmentVolumeTypeList, options=set())
    volumeSize0 = bpy.props.FloatProperty(default=1.0, options=set(), update=handleAttachmentVolumeSizeChange)
    volumeSize1 = bpy.props.FloatProperty(default=0.0, options=set(), update=handleAttachmentVolumeSizeChange)
    volumeSize2 = bpy.props.FloatProperty(default=0.0, options=set(), update=handleAttachmentVolumeSizeChange)

class M3SimpleGeometricShape(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name", default="", options=set())
    updateBlenderBone = bpy.props.BoolProperty(default=True, options=set())
    boneName = bpy.props.StringProperty(name="boneName", update=handleGeometicShapeTypeOrBoneNameUpdate, options=set())
    shape = bpy.props.EnumProperty(default="1", items=geometricShapeTypeList, update=handleGeometicShapeTypeOrBoneNameUpdate, options=set())
    size0 = bpy.props.FloatProperty(default=1.0, update=handleGeometicShapeUpdate, options=set())
    size1 = bpy.props.FloatProperty(default=0.0, update=handleGeometicShapeUpdate, options=set())
    size2 = bpy.props.FloatProperty(default=0.0, update=handleGeometicShapeUpdate, options=set())
    offset = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype="XYZ", update=handleGeometicShapeUpdate,options=set())
    rotationEuler = bpy.props.FloatVectorProperty(default=(0.0, 0.0, 0.0), size=3, subtype="EULER", unit="ROTATION", update=handleGeometicShapeUpdate, options=set())
    scale = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), size=3, subtype="XYZ", update=handleGeometicShapeUpdate, options=set())

class M3BoneVisiblityOptions(bpy.types.PropertyGroup):
    showFuzzyHitTests = bpy.props.BoolProperty(default=True, options=set(), update=handleFuzzyHitTestVisiblityUpdate)
    showTightHitTest = bpy.props.BoolProperty(default=True, options=set(), update=handleTightHitTestVisiblityUpdate)
    showAttachmentPoints = bpy.props.BoolProperty(default=True, options=set(), update=handleAttachmentPointVisibilityUpdate)
    showParticleSystems = bpy.props.BoolProperty(default=True, options=set(), update=handleParticleSystemsVisiblityUpdate)
    showRibbons = bpy.props.BoolProperty(default=True, options=set(), update=handleRibbonsVisiblityUpdate)
    showLights = bpy.props.BoolProperty(default=True, options=set(), update=handleLightsVisiblityUpdate)
    showForces = bpy.props.BoolProperty(default=True, options=set(), update=handleForcesVisiblityUpdate)
    showCameras = bpy.props.BoolProperty(default=True, options=set(), update=handleCamerasVisiblityUpdate)
    showPhysicsShapes = bpy.props.BoolProperty(default=True, options=set(), update=handlePhysicsShapeVisibilityUpdate)
    showProjections = bpy.props.BoolProperty(default=True, options=set(), update=handleProjectionVisibilityUpdate)
    showWarps = bpy.props.BoolProperty(default=True, options=set(), update=handleWarpVisibilityUpdate)

class M3ExportOptions(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(name="path", default="ExportedModel.m3", options=set())
    testPatch20Format = bpy.props.BoolProperty(default=False, options=set())
    animationExportAmount = bpy.props.EnumProperty(default=shared.exportAmountAllAnimations, items=animationExportAmount, options=set())

class M3ImportOptions(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(name="path", default="", options=set())
    rootDirectory = bpy.props.StringProperty(name="rootDirectory", default="", options=set())
    generateBlenderMaterials = bpy.props.BoolProperty(default=True, options=set())
    applySmoothShading = bpy.props.BoolProperty(default=True, options=set())
    markSharpEdges = bpy.props.BoolProperty(default=True, options=set())
    recalculateRestPositionBones = bpy.props.BoolProperty(default=False, options=set())
    teamColor = bpy.props.FloatVectorProperty(default=(1.0, 0.0, 0.0), min = 0.0, max = 1.0, name="team color", size=3, subtype="COLOR", options=set(), description="Team color place holder used for generated blender materials")
    contentToImport = bpy.props.EnumProperty(default="EVERYTHING", items=contentToImportList, options=set())


class M3Projection(bpy.types.PropertyGroup):
    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(options=set())
    updateBlenderBone = bpy.props.BoolProperty(default=True, options=set())
    boneSuffix = bpy.props.StringProperty(options=set(), update=handleProjectionTypeOrBoneSuffixChange, default="Projection")
    boneName = bpy.props.StringProperty(options=set())
    materialName = bpy.props.StringProperty(options=set())
    projectionType = bpy.props.EnumProperty(default=shared.projectionTypeOrthonormal, items=projectionTypeList, options=set(), update=handleProjectionTypeOrBoneSuffixChange)
    fieldOfView = bpy.props.FloatProperty(default=45.0, name="FOV", options={"ANIMATABLE"}, description="represents the angle (in degrees) that defines the vertical bounds of the projector")
    aspectRatio = bpy.props.FloatProperty(default=1.0, name="Aspect Ratio", options={"ANIMATABLE"})
    near = bpy.props.FloatProperty(default=0.5, name="Near", options={"ANIMATABLE"})
    far = bpy.props.FloatProperty(default=10.0, name="Far", options={"ANIMATABLE"})
    depth = bpy.props.FloatProperty(default=10.0, name="Depth", options=set(), update=handleProjectionSizeChange)
    width = bpy.props.FloatProperty(default=10.0, name="Width", options=set(), update=handleProjectionSizeChange)
    height = bpy.props.FloatProperty(default=10.0, name="Height", options=set(), update=handleProjectionSizeChange)
    alphaOverTimeStart = bpy.props.FloatProperty(default=0.0, name="Alpha over time start", options=set() )
    alphaOverTimeMid = bpy.props.FloatProperty(default=1.0, name="Alpha over time mid", options=set() )
    alphaOverTimeEnd = bpy.props.FloatProperty(default=0.0, name="Alpha over time end", options=set() )
    


class M3Warp(bpy.types.PropertyGroup):
    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(options=set())
    updateBlenderBone = bpy.props.BoolProperty(default=True, options=set())
    boneSuffix = bpy.props.StringProperty(options=set(), update=handleWarpBoneSuffixChange, default="01")
    boneName = bpy.props.StringProperty(options=set())
    materialName = bpy.props.StringProperty(options=set())

    radius = bpy.props.FloatProperty(default=1.0, min=0.0, name="radius", update=handleWarpRadiusChange, options={"ANIMATABLE"})
    unknown9306aac0 = bpy.props.FloatProperty(default=10.0, name="unknown9306aac0", options={"ANIMATABLE"})
    compressionStrength = bpy.props.FloatProperty(default=1.0, name="compressionStrength", options={"ANIMATABLE"})
    unknown50c7f2b4 = bpy.props.FloatProperty(default=1.0, name="unknown50c7f2b4", options={"ANIMATABLE"})
    unknown8d9c977c = bpy.props.FloatProperty(default=1.0, name="unknown8d9c977c", options={"ANIMATABLE"})
    unknownca6025a2 = bpy.props.FloatProperty(default=1.0, name="unknownca6025a2", options={"ANIMATABLE"})


class M3Light(bpy.types.PropertyGroup):
    # name attribute seems to be needed for template_list but is not actually in the m3 file
    # The name gets calculated like this: name = boneSuffix (type)
    name = bpy.props.StringProperty(name="name", default="", options=set())
    updateBlenderBone = bpy.props.BoolProperty(default=True, options=set())
    lightType = bpy.props.EnumProperty(default="1", items=lightTypeList, options=set(), update=handleLightTypeOrBoneSuffixChange)
    boneSuffix = bpy.props.StringProperty(options=set(), update=handleLightTypeOrBoneSuffixChange, default="Particle System")
    boneName = bpy.props.StringProperty(options=set())
    lightColor = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=3, subtype="COLOR", options={"ANIMATABLE"})
    lightIntensity = bpy.props.FloatProperty(default=1.0, name="Light Intensity", options={"ANIMATABLE"})
    specColor =  bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), min = 0.0, max = 1.0, size=3, subtype="COLOR", options={"ANIMATABLE"})
    specIntensity = bpy.props.FloatProperty(default=0.0, name="Specular Intensity", options={"ANIMATABLE"})
    attenuationNear = bpy.props.FloatProperty(default=2.5, name="attenuationNear", options={"ANIMATABLE"})
    unknownAt148 = bpy.props.FloatProperty(default=2.5, name="unknownAt148", options=set())
    attenuationFar = bpy.props.FloatProperty(default=3.0, name="attenuationFar", update=handleLightSizeChange, options={"ANIMATABLE"})
    hotSpot = bpy.props.FloatProperty(default=1.0, name="Hot Spot", options={"ANIMATABLE"})
    falloff = bpy.props.FloatProperty(default=1.0, name="Fall Off", update=handleLightSizeChange, options={"ANIMATABLE"})
    unknownAt12 = bpy.props.IntProperty(default=-1, name="unknownAt12", options=set())
    unknownAt8 = bpy.props.BoolProperty(default=False,options=set())
    shadowCast = bpy.props.BoolProperty(options=set())
    specular = bpy.props.BoolProperty(options=set())
    unknownFlag0x04 = bpy.props.BoolProperty(options=set())
    turnOn = bpy.props.BoolProperty(default=True,options=set())
    
class M3BillboardBehavior(bpy.types.PropertyGroup):
    # name is also bone name
    name = bpy.props.StringProperty(name="name", default="", options=set())
    billboardType = bpy.props.EnumProperty(default="6", items=billboardBehaviorTypeList, options=set())
                                          
class ImportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_quickImport"
    bl_label = "M3 Import"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene.m3_import_options, "path", text="M3 File")
        layout.prop(scene.m3_import_options, "contentToImport", text="Import ")
        layout.operator("m3.quick_import", text="Import M3")
        layout.prop(scene.m3_import_options, "rootDirectory", text="Root Directory")
        layout.prop(scene.m3_import_options, "generateBlenderMaterials", text="Generate Blender Materials At Import")
        layout.operator("m3.generate_blender_materials", text="Generate Blender Materials")
        layout.prop(scene.m3_import_options, "applySmoothShading", text="Apply Smooth Shading")
        layout.prop(scene.m3_import_options, "markSharpEdges", text="Mark sharp edges")
        layout.prop(scene.m3_import_options, "teamColor", text="Team Color")


class ExportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_quickExport"
    bl_label = "M3 Quick Export"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene.m3_export_options, "path", text="")
        layout.operator("m3.quick_export", text="Export As M3")
        layout.prop(scene.m3_export_options, "testPatch20Format", text="Use new experimental format")
        layout.prop(scene.m3_export_options, "animationExportAmount", text="Export")



class BoneVisibilityPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_bone_visibility"
    bl_label = "M3 Bone Visibility"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene.m3_bone_visiblity_options, "showFuzzyHitTests", text="Fuzzy Hit Tests")
        layout.prop(scene.m3_bone_visiblity_options, "showTightHitTest", text="Tight Hit Test")
        layout.prop(scene.m3_bone_visiblity_options, "showAttachmentPoints", text="Attachment Points")
        layout.prop(scene.m3_bone_visiblity_options, "showParticleSystems", text="Particle Systems")
        layout.prop(scene.m3_bone_visiblity_options, "showRibbons", text="Ribbons")
        layout.prop(scene.m3_bone_visiblity_options, "showLights", text="Lights")
        layout.prop(scene.m3_bone_visiblity_options, "showForces", text="Forces")
        layout.prop(scene.m3_bone_visiblity_options, "showCameras", text="Cameras")
        layout.prop(scene.m3_bone_visiblity_options, "showPhysicsShapes", text="Physics Shapes")
        layout.prop(scene.m3_bone_visiblity_options, "showProjections", text="Projections")
        layout.prop(scene.m3_bone_visiblity_options, "showWarps", text="Warps")

class BasicMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_M3_animations_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.operator("m3.animations_duplicate", text="Duplicate")

class AnimationSequencesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_animations"
    bl_label = "M3 Animation Sequences"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_animations", scene, "m3_animations", scene, "m3_animation_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.animations_add", icon='ZOOMIN', text="")
        col.operator("m3.animations_remove", icon='ZOOMOUT', text="")
        col.menu("OBJECT_MT_M3_animations_menu", icon='DOWNARROW_HLT', text="")
        animationIndex = scene.m3_animation_index
        if animationIndex >= 0 and animationIndex < len(scene.m3_animations):
            animation = scene.m3_animations[animationIndex]
            layout.operator("m3.animations_deselect", text="Edit Default Values")
            layout.separator()
            layout.prop(animation, 'name', text="Name")
            layout.prop(animation, 'movementSpeed', text="Mov. Speed")
            layout.prop(animation, 'frequency', text="Frequency")
            layout.prop(animation, 'notLooping', text="Doesn't Loop")
            layout.prop(animation, 'alwaysGlobal', text="Always Global")
            layout.prop(animation, 'globalInPreviewer', text="Global In Previewer")
        
            if not len(scene.m3_rigid_bodies) > 0:
                return
            
            layout.separator()
            layout.prop(animation, 'useSimulateFrame', text="Use physics")
            if animation.useSimulateFrame:
                layout.prop(animation, 'simulateFrame', text="Simulate after frame")
            
class AnimationSequenceTransformationCollectionsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_STCs"
    bl_label = "M3 Sub Animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        animationIndex = scene.m3_animation_index
        if animationIndex >= 0 and animationIndex < len(scene.m3_animations):
            animation = scene.m3_animations[animationIndex]

            col.template_list("UI_UL_list", "m3_stcs", animation, "transformationCollections", animation, "transformationCollectionIndex", rows=2)
            
            col = row.column(align=True)
            col.operator("m3.stc_add", icon='ZOOMIN', text="")
            col.operator("m3.stc_remove", icon='ZOOMOUT', text="")
            index = animation.transformationCollectionIndex
            if index >= 0 and index < len(animation.transformationCollections):
                transformationCollection = animation.transformationCollections[index]
                layout.separator()
                layout.prop(transformationCollection, 'name', text="Name")
                layout.prop(transformationCollection, 'runsConcurrent', text="Runs Concurrent")
                layout.prop(transformationCollection, 'priority', text="Priority")
                row = layout.row()
                col = row.column()
                col.operator("m3.stc_select", text="Select FCurves")
                col = row.column()
                col.operator("m3.stc_assign", text="Assign FCurves")
     
class MaterialReferencesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_material_references"
    bl_label = "M3 Materials"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_material_references", scene, "m3_material_references", scene, "m3_material_reference_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.materials_add", icon='ZOOMIN', text="")
        col.operator("m3.materials_remove", icon='ZOOMOUT', text="")




class MaterialSelectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_material_selection"
    bl_label = "M3 Material Selection"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
 
    @classmethod
    def poll(cls, context):
        o = context.object
        return o and (o.data != None) and (o.type == 'MESH')
 
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        meshObject = context.object
        mesh = meshObject.data
        row = layout.row()

        row.prop_search(mesh, 'm3_material_name', scene, 'm3_material_references', text="M3 Material", icon='NONE')
        row.operator("m3.create_material_for_mesh", icon='ZOOMIN', text="")

def displayMaterialPropertiesUI(scene, layout, materialReference):
        materialType = materialReference.materialType
        materialIndex = materialReference.materialIndex
        
        if materialType == shared.standardMaterialTypeIndex:
            material = scene.m3_standard_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
            layout.prop(material, 'blendMode', text="Blend Mode")
            layout.prop(material, 'priority', text="Priority")
            layout.prop(material, 'specularity', text="Specularity")
            layout.prop(material, 'cutoutThresh', text="Cutout Thresh.", slider=True)
            layout.prop(material, 'specMult', text="Spec. Mult.")
            layout.prop(material, 'emisMult', text="Emis. Mult.")
            layout.prop(material, 'layerBlendType', text="Layer Blend Type")
            layout.prop(material, 'emisBlendType', text="Emis. Blend Type")
            layout.prop(material, 'specType', text="Spec. Type")
           
            split = layout.split(percentage=0.7)
            split.prop(material, 'useDepthBlendFalloff', text="Depth Blend Falloff:")
            row = split.row()
            row.active = material.useDepthBlendFalloff
            row.prop(material, 'depthBlendFalloff', text="")
            
            layout.prop(material, 'useVertexColor', text="Use Vertex Color")
            layout.prop(material, 'useVertexAlpha', text="Use Vertex Alpha")
            layout.prop(material, 'unknownFlag0x200', text="unknownFlag0x200")
            layout.prop(material, 'unfogged', text="Unfogged")
            layout.prop(material, 'twoSided', text="Two Sided")
            layout.prop(material, 'unshaded', text="Unshaded")
            layout.prop(material, 'noShadowsCast', text="No Shadows Cast")
            layout.prop(material, 'noHitTest', text="No Hit Test")
            layout.prop(material, 'noShadowsReceived', text="No Shadows Received")
            layout.prop(material, 'depthPrepass', text="Depth Prepass")
            layout.prop(material, 'useTerrainHDR', text="Use Terrain HDR")
            layout.prop(material, 'splatUVfix', text="Splat UV Fix")
            layout.prop(material, 'softBlending', text="Soft Blending")
            layout.prop(material, 'forParticles', text="For Particles (?)")
            layout.prop(material, 'transparency', text="Transparency")
            layout.prop(material, 'disableSoft', text="Disable Soft")
            layout.prop(material, 'darkNormalMapping', text="Dark Normal Mapping")
            split = layout.split(percentage=0.6)
            split.prop(material, 'acceptSplats', text="Accept Splats:")
            row = split.row()
            row.active = material.acceptSplats
            row.prop(material, 'acceptSplatsOnly', text="Only")
            layout.prop(material, 'backgroundObject', text="Background Object")
            layout.prop(material, 'excludeFromHighlighting', text="No Highlighting")
            layout.prop(material, 'clampOutput', text="Clamp Output")
            layout.prop(material, 'geometryVisible', text="Geometry Visible")


            split = layout.split(align=True)
            split.label("Required On Low End:")

            box = layout.box()
            col = box.column_flow()
            col.prop(material, 'decalRequiredOnLowEnd', text="Decal")
            col.prop(material, 'emissiveRequiredOnLowEnd', text="Emissive")
            col.prop(material, 'zpFillRequiredOnLowEnd', text="ZP Fill")
            
        elif materialType == shared.displacementMaterialTypeIndex:
            material = scene.m3_displacement_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
            layout.prop(material, 'strengthFactor', text="Strength Factor")
            layout.prop(material, 'priority', text="Priority")
        elif materialType == shared.compositeMaterialTypeIndex:
            material = scene.m3_composite_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
            layout.label("Sections:")
            row = layout.row()
            col = row.column()
            col.template_list("UI_UL_list", "m3_material_sections", material, "sections", material, "sectionIndex", rows=2)
            
            col = row.column(align=True)
            col.operator("m3.composite_material_add_section", icon='ZOOMIN', text="")
            col.operator("m3.composite_material_remove_section", icon='ZOOMOUT', text="")
            sectionIndex = material.sectionIndex
            if (sectionIndex >= 0) and (sectionIndex < len(material.sections)):
                section = material.sections[sectionIndex]
                layout.prop_search(section, 'name', scene, 'm3_material_references', text="Material", icon='NONE')
                layout.prop(section, "alphaFactor", text="Alpha Factor")
            
        elif materialType == shared.terrainMaterialTypeIndex:
            material = scene.m3_terrain_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
        elif materialType == shared.volumeMaterialTypeIndex:
            material = scene.m3_volume_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
            layout.prop(material, 'volumeDensity', text="Volume Density")
        elif materialType == shared.volumeNoiseMaterialTypeIndex:
            material = scene.m3_volume_noise_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
            layout.prop(material, 'volumeDensity', text="Volume Density")
            layout.prop(material, 'nearPlane', text="Near Plane")
            layout.prop(material, 'falloff', text="Falloff")
            layout.prop(material, 'scrollRate', text="Scroll Rate")
            layout.prop(material, 'translation', text="Translation")
            layout.prop(material, 'scale', text="Scale")
            layout.prop(material, 'rotation', text="Rotation")
            layout.prop(material, 'alphaTreshhold', text="Alpha Treshhold")
            layout.prop(material, 'drawAfterTransparency', text="Draw after transparency")
        elif materialType == shared.creepMaterialTypeIndex:
            material = scene.m3_creep_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
        elif materialType == shared.stbMaterialTypeIndex:
            material = scene.m3_stb_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
        elif materialType == shared.lensFlareMaterialTypeIndex:
            material = scene.m3_lens_flare_materials[materialIndex]
            layout.prop(material, 'name', text="Name")
        else:
            layout.label(text=("Unsupported material type %d" % materialType))

class MaterialPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_material_properties"
    bl_label = "M3 Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        materialReferenceIndex = scene.m3_material_reference_index

        if materialReferenceIndex >= 0 and materialReferenceIndex < len(scene.m3_material_references):
            materialReference = scene.m3_material_references[materialReferenceIndex]
            displayMaterialPropertiesUI(scene, layout, materialReference)


class ObjectMaterialPropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_object_material_properties"
    bl_label = "M3 Material Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        meshObject = context.object
        mesh = meshObject.data
        materialName = mesh.m3_material_name
        materialReference = scene.m3_material_references.get(materialName)
        if materialReference != None:
            displayMaterialPropertiesUI(scene, layout, materialReference)
        
def displayMaterialLayersUI(scene, layout, materialReference):
    materialType = materialReference.materialType
    materialIndex = materialReference.materialIndex
    row = layout.row()
    col = row.column()
    material = shared.getMaterial(scene, materialType, materialIndex)
    if material != None:
        col.template_list("UI_UL_list", "m3_material_layers", material, "layers", scene, "m3_material_layer_index", rows=2)
        layerIndex = scene.m3_material_layer_index
        if layerIndex >= 0 and layerIndex < len(material.layers):
            layer = material.layers[layerIndex]
            layout.prop(layer, 'imagePath', text="Image Path")
            layout.prop(layer, 'unknownbd3f7b5d', text="Unknown (id: bd3f7b5d)")
            
            layout.prop(layer, 'uvSource', text="UV Source")
            isTriPlanarUVSource = layer.uvSource in ["16","17","18"]

            row = layout.row(align=True)
            row.active = not isTriPlanarUVSource
            row.prop(layer, 'textureWrapX', text="Tex. Wrap X")
            row.prop(layer, 'textureWrapY', text="Tex. Wrap Y")
            
            row = layout.row(align=True)
            row.prop(layer, 'invertColor', text="Invert Color")
            row.prop(layer, 'clampColor', text="Clamp Color")
            
            layout.prop(layer, 'colorChannelSetting', text="Color Channels")

            split = layout.split()
            row = split.row()
            row.prop(layer, 'colorEnabled', text="Color:")
            sub = row.column(align=True)
            sub.active = layer.colorEnabled
            sub.prop(layer, 'color', text="")
            
            
            col = layout.column_flow(columns=2)
            sub = col.column(align=True)
            sub.active = not isTriPlanarUVSource
            sub.label(text="UV Offset:")
            sub.prop(layer, "uvOffset", text="X", index=0)
            sub.prop(layer, "uvOffset", text="Y", index=1)


            sub = col.column(align=True)
            sub.active = not isTriPlanarUVSource
            sub.label(text="UV Tiling:")
            sub.prop(layer, "uvTiling", text="X", index=0)
            sub.prop(layer, "uvTiling", text="Y", index=1)
           

            sub = col.column(align=True)
            sub.active = not isTriPlanarUVSource
            sub.label(text="UV Angle:")
            sub.prop(layer, "uvAngle", text="X", index=0)
            sub.prop(layer, "uvAngle", text="Y", index=1)
            sub.prop(layer, "uvAngle", text="Z", index=2)

            row = layout.row()
            row.active = isTriPlanarUVSource
            sub = row.column(align=True)
            sub.label(text="Tri Planar Offset:")
            sub.prop(layer, "triPlanarOffset", index=0, text="X")
            sub.prop(layer, "triPlanarOffset", index=1, text="Y")
            sub.prop(layer, "triPlanarOffset", index=2, text="Z")
            sub = row.column(align=True)
            sub.label(text="Tri Planar Scale:")
            sub.prop(layer, "triPlanarScale", index=0, text="X")
            sub.prop(layer, "triPlanarScale", index=1, text="Y")
            sub.prop(layer, "triPlanarScale", index=2, text="Z")
            
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Flipbook:")
            sub.prop(layer, "flipBookRows", text="Rows")
            sub.prop(layer, "flipBookColumns", text="Columns")
            sub.prop(layer, "flipBookFrame", text="Frame")
            
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Brightness:")
            sub.prop(layer, "brightness", text="")
            sub.prop(layer, "brightMult", text="Multiplier")
            sub.prop(layer, "midtoneOffset", text="Midtone Offset")
            
            col = layout.column(align=True)
            col.prop(layer, 'fresnelType', text="Fresnel")
            box = col.box()
            box.active = (layer.fresnelType != "0")
            sub = box.column()
            sub = box.column(align=True)
            sub.prop(layer, 'fresnelExponent', text="Exponent")
            sub.prop(layer, 'fresnelMin', text="Min")
            sub.prop(layer, 'fresnelMax', text="Max")
            sub = box.column(align=True)
            sub.label("Mask")
            sub.prop(layer, 'fresnelMaskX', text="X", slider=True)
            sub.prop(layer, 'fresnelMaskY', text="Y", slider=True)
            sub.prop(layer, 'fresnelMaskZ', text="Z", slider=True)
            sub = box.column(align=True)
            sub.label("Rotation")
            sub.prop(layer, 'fresnelRotationYaw', text="Yaw")
            sub.prop(layer, 'fresnelRotationPitch', text="Pitch")
            sub = box.column(align=True)
            sub.prop(layer, 'fresnelLocalTransform', text="Local Transform")
            sub.prop(layer, 'fresnelDoNotMirror', text="Do Not Mirror")
            
            layout.prop(layer, "rttChannel", text="RTT Channel")
            
            col = layout.column(align=True)
            col.label(text="Video:")
            col.active = shared.isVideoFilePath(layer.imagePath)
            box = col.box()
            sub = box.column()
            sub.prop(layer, "videoFrameRate", text="Frame Rate")
            sub.prop(layer, "videoStartFrame", text="Start Frame")
            sub.prop(layer, "videoEndFrame", text="End Frame")
            sub.prop(layer, "videoMode", text="Mode")
            sub.prop(layer, "videoSyncTiming", text="Sync Timing")
            sub.prop(layer, "videoPlay", text="Play")
            sub.prop(layer, "videoRestart", text="Restart")

class MatrialLayersPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_material_layers"
    bl_label = "M3 Material Layers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        materialIndex = scene.m3_material_reference_index
        if materialIndex >= 0 and materialIndex < len(scene.m3_material_references):
            materialReference = scene.m3_material_references[materialIndex]
            displayMaterialLayersUI(scene, layout, materialReference)
        else:
            layout.label(text="No properties to display")


class ObjectMatrialLayersPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_object_material_layers"
    bl_label = "M3 Material Layers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        meshObject = context.object
        if meshObject == None:
            return
        mesh = meshObject.data
        materialName = mesh.m3_material_name
        materialReference = scene.m3_material_references.get(materialName)
        if materialReference != None:
            displayMaterialLayersUI(scene, layout, materialReference)
        else:
            layout.label(text="No properties to display")

class CameraPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_cameras"
    bl_label = "M3 Cameras"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_cameras", scene, "m3_cameras", scene, "m3_camera_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.cameras_add", icon='ZOOMIN', text="")
        col.operator("m3.cameras_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_camera_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_cameras):
            camera = scene.m3_cameras[currentIndex]
            layout.separator()
            layout.prop(camera, 'name',text="Name")
            layout.prop(camera, 'fieldOfView',text="Field Of View")
            layout.prop(camera, 'farClip',text="Far Clip")
            layout.prop(camera, 'nearClip',text="Near Clip")
            layout.prop(camera, 'clip2',text="Clip 2")
            layout.prop(camera, 'focalDepth',text="Focal Depth")
            layout.prop(camera, 'falloffStart',text="Falloff Start")
            layout.prop(camera, 'falloffEnd',text="Falloff End")
            layout.prop(camera, 'depthOfField',text="Depth Of Field")

            
class ParticleSystemsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_particles"
    bl_label = "M3 Particle Systems"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_particle_systems", scene, "m3_particle_systems", scene, "m3_particle_system_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.particle_systems_add", icon='ZOOMIN', text="")
        col.operator("m3.particle_systems_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_particle_system_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_particle_systems):
            particle_system = scene.m3_particle_systems[currentIndex]
            layout.separator()
            layout.prop(particle_system, 'name',text="Name")
            layout.prop_search(particle_system, 'materialName', scene, 'm3_material_references', text="Material", icon='NONE')
            split = layout.split()
            col = split.column()
            col.row().label("Emis. Area:")
            subcol = col.row().column(align=True)
            subcol.prop(particle_system, 'emissionAreaType', text="")
            sub = subcol.row()
            sub.active = particle_system.emissionAreaType in emissionAreaTypesWithLength
            sub.prop(particle_system, 'emissionAreaSize', index=0, text="Length")
            sub =  subcol.row()
            sub.active = particle_system.emissionAreaType in emissionAreaTypesWithWidth
            sub.prop(particle_system, 'emissionAreaSize', index=1, text="Width")
            sub = subcol.row()
            sub.active = particle_system.emissionAreaType in emissionAreaTypesWithHeight
            sub.prop(particle_system, 'emissionAreaSize', index=2, text="Height")
            sub = subcol.row()
            sub.active = particle_system.emissionAreaType in emissionAreaTypesWithRadius
            sub.prop(particle_system, 'emissionAreaRadius',text="Radius")
            col.row().prop(particle_system, 'cutoutEmissionArea', text="Cutout Emission Area:")
            subcol = col.row().column(align=True)
            sub = subcol.row()
            sub.active = particle_system.cutoutEmissionArea and particle_system.emissionAreaType in emissionAreaTypesWithLength
            sub.prop(particle_system, 'emissionAreaCutoutSize', index=0, text="Length")
            sub =  subcol.row()
            sub.active = particle_system.cutoutEmissionArea and particle_system.emissionAreaType in emissionAreaTypesWithWidth
            sub.prop(particle_system, 'emissionAreaCutoutSize', index=1, text="Width")
            sub = subcol.row()
            sub.active = particle_system.cutoutEmissionArea and particle_system.emissionAreaType == shared.emissionAreaTypeCuboid
            # property has no effect on cylinder cutout
            sub.prop(particle_system, 'emissionAreaCutoutSize', index=2, text="Height")
            sub = subcol.row()
            sub.active = particle_system.cutoutEmissionArea and particle_system.emissionAreaType in emissionAreaTypesWithRadius
            sub.prop(particle_system, 'emissionAreaCutoutRadius',text="Radius")
            subcol = col.row().column(align=True)
            subcol.active = particle_system.emissionAreaType == shared.emissionAreaTypeMesh
            # FIXME Add button to set mesh
            #subcol.prop_search(particle_system, 'spawnPointsMesh', bpy.data, 'objects' ,text="Spawn Points Mesh", icon='NONE')
            col.operator("m3.create_spawn_points_from_mesh", text="Spawn Points From Mesh")

            
            
            split = layout.split()
            col = split.column()
            col.prop(particle_system, 'emissionRate', text="Particles Per Second")
            col.prop(particle_system, 'maxParticles', text="Particle Maximum")
            
            layout.prop(particle_system, 'trailingEnabled', text="Trailing")

            split = layout.split()
            col = split.column()
            col.label(text="Emis. Speed.:")
            sub = col.column(align=True)
            sub.prop(particle_system, "emissionSpeed1", text="")
            col = split.column()
            col.prop(particle_system, "randomizeWithEmissionSpeed2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithEmissionSpeed2
            sub.prop(particle_system, "emissionSpeed2", text="")

            layout.prop(particle_system, 'emissionType', text="Emission Type")
            split = layout.split()
            split.active = particle_system.emissionType != "1"
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Angle:")
            sub.prop(particle_system, "emissionAngleX", text="X")
            sub.prop(particle_system, "emissionAngleY", text="Y")
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Spread:")
            sub.prop(particle_system, "emissionSpreadX", text="X")
            sub.prop(particle_system, "emissionSpreadY", text="Y")
            
            split = layout.split()
            col = split.column()
            col.label(text="Lifespan:")
            sub = col.column(align=True)
            sub.prop(particle_system, "lifespan1", text="")
            col = split.column()
            col.prop(particle_system, "randomizeWithLifespan2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithLifespan2
            sub.prop(particle_system, "lifespan2", text="")
            
            
            layout.prop(particle_system, 'zAcceleration', text="Z-Acceleration")
            
            split = layout.split()
            col = split.column()
            col.label(text="Color:")
            sub = col.column(align=True)
            sub.prop(particle_system, "initialColor1", text="Initial")
            sub.prop(particle_system, "middleColor1", text="Middle")
            sub.prop(particle_system, "finalColor1", text="Final")
            col = split.column()
            col.prop(particle_system, "randomizeWithColor2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithColor2
            sub.prop(particle_system, "initialColor2", text="Initial")
            sub.prop(particle_system, "middleColor2", text="Middle")
            sub.prop(particle_system, "finalColor2", text="Final")
            layout.prop(particle_system, "colorAnimationMiddle", text="Color Middle")
            layout.prop(particle_system, "alphaAnimationMiddle", text="Alpha Middle")
            split = layout.split()
            col = split.column()
            col.label(text="Color & Alpha Smooth Type:")
            col.prop(particle_system, "colorSmoothingType", text="")
            sub = col.column(align=True)
            sub.active = particle_system.colorSmoothingType in ["3", "4"]
            sub.prop(particle_system, "colorHoldTime", text="Color Hold Time")
            sub.prop(particle_system, "alphaHoldTime", text="Alpha Hold Time")

            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Size (Particle):")
            sub.prop(particle_system, 'particleSizes1', index=0, text="Initial")
            sub.prop(particle_system, 'particleSizes1', index=1, text="Middle")
            sub.prop(particle_system, 'particleSizes1', index=2, text="Final")
            col = split.column()
            col.prop(particle_system, "randomizeWithParticleSizes2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithParticleSizes2
            sub.prop(particle_system, 'particleSizes2', index=0, text="Initial")
            sub.prop(particle_system, 'particleSizes2', index=1, text="Middle")
            sub.prop(particle_system, 'particleSizes2', index=2, text="Final")
            layout.prop(particle_system, 'sizeAnimationMiddle', text="Size Middle")
            split = layout.split()
            col = split.column()
            col.label(text="Size Smooth Type:")
            col.prop(particle_system, "sizeSmoothingType", text="")
            sub = col.column(align=True)
            sub.active = particle_system.sizeSmoothingType in ["3", "4"]
            sub.prop(particle_system, "sizeHoldTime", text="Hold Time")

            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Rotation (Particle):")
            sub.prop(particle_system, 'rotationValues1', index=0, text="Initial")
            sub.prop(particle_system, 'rotationValues1', index=1, text="Middle")
            sub.prop(particle_system, 'rotationValues1', index=2, text="Final")
            col = split.column()
            col.prop(particle_system, "randomizeWithRotationValues2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithRotationValues2
            sub.prop(particle_system, 'rotationValues2', index=0, text="Initial")
            sub.prop(particle_system, 'rotationValues2', index=1, text="Middle")
            sub.prop(particle_system, 'rotationValues2', index=2, text="Final")
            layout.prop(particle_system, "rotationAnimationMiddle", text="Rotation Middle")
            split = layout.split()
            col = split.column()
            col.label(text="Rotation Smooth Type:")
            col.prop(particle_system, "rotationSmoothingType", text="")
            sub = col.column(align=True)
            sub.active = particle_system.rotationSmoothingType in ["3", "4"]
            sub.prop(particle_system, "rotationHoldTime", text="Hold Time")

            split = layout.split()
            row = split.row()
            sub = row.column(align=True)
            sub.label(text="Column:")
            sub.prop(particle_system, 'numberOfColumns', text="Count")
            sub.prop(particle_system, 'columnWidth', text="Width")
            row = split.row()
            sub = row.column(align=True)
            sub.label(text="Row:")
            sub.prop(particle_system, 'numberOfRows', text="Count")
            sub.prop(particle_system, 'rowHeight', text="Height")
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Phase 1 Image Index:")
            sub.prop(particle_system, 'phase1StartImageIndex', text="Inital")
            sub.prop(particle_system, 'phase1EndImageIndex', text="Final")
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Phase 2 Image Index:")
            sub.prop(particle_system, 'phase2StartImageIndex', text="Inital")
            sub.prop(particle_system, 'phase2EndImageIndex', text="Final")
            layout.prop(particle_system, 'relativePhase1Length', text="Relative Phase 1 Length")

            layout.prop(particle_system, 'slowdown', text="Slowdown")

            split = layout.split()
            col = split.column()
            col.label(text="Mass:")
            sub = col.column(align=True)
            sub.prop(particle_system, "mass", text="")
            col = split.column()
            col.prop(particle_system, "randomizeWithMass2", text="Randomize With:")
            sub = col.column(align=True)
            sub.active = particle_system.randomizeWithMass2
            sub.prop(particle_system, "mass2", text="")
            

            split = layout.split()
            col = split.column()
            col.label("Noise:")
            sub = col.column(align=True)
            sub.prop(particle_system, "noiseAmplitude", text="Amplitude")
            sub.prop(particle_system, "noiseFrequency", text="Frequency")
            sub.prop(particle_system, "noiseCohesion", text="Cohesion")
            sub.prop(particle_system, "noiseEdge", text="Edge")

            layout.prop(particle_system, "unknownFloat2c", text="Unknown f2c")
                        
            layout.prop(particle_system, 'partEmit', text="Part. Emit.")


            split = layout.split()
            col = split.column()
            col.prop(particle_system, 'particleType', text="Particle Type")
            sub = col.column(align=True)
            sub.active = particle_system.particleType in ["1", "6"]
            sub.prop(particle_system, 'lengthWidthRatio', text="Length/Width Ratio")
            
            layout.prop(particle_system, 'localForceChannels', text="Local Force Channels")
            layout.prop(particle_system, 'worldForceChannels', text="World Force Channels")

            split = layout.split()
            col = split.column()
            col.prop_search(particle_system, 'trailingParticlesName', scene, 'm3_particle_systems', text="Trailing Particles", icon='NONE')
            sub = col.column(align=True)
            sub.active = particle_system.trailingParticlesName != ""
            sub.prop(particle_system, "trailingParticlesChance", text="Chance to trail")
            sub.prop(particle_system, "trailingParticlesRate", text="Tailing  Rate")

            layout.prop(particle_system, "unknownFloat4", text="Unknown Float 4")
            layout.prop(particle_system, "unknownFloat5", text="Unknown Float 5")
            layout.prop(particle_system, "unknownFloat6", text="Unknown Float 6")
            layout.prop(particle_system, "unknownFloat7", text="Unknown Float 7")
            layout.prop(particle_system, 'sort', text="Sort")
            layout.prop(particle_system, 'collideTerrain', text="Collide Terrain")
            layout.prop(particle_system, 'collideObjects', text="Collide Objects")
            layout.prop(particle_system, 'spawnOnBounce', text="Spawn On Bounce")
            layout.prop(particle_system, 'inheritEmissionParams', text="Inherit Emission Params")
            layout.prop(particle_system, 'inheritParentVel', text="Inherit Parent Vel")
            layout.prop(particle_system, 'sortByZHeight', text="Sort By Z Height")
            layout.prop(particle_system, 'reverseIteration', text="Reverse Iteration")
            layout.prop(particle_system, 'litParts', text="Lit Parts")
            layout.prop(particle_system, 'randFlipBookStart', text="Rand Flip Book Start")
            layout.prop(particle_system, 'multiplyByGravity', text="Multiply By Gravity")
            layout.prop(particle_system, 'clampTailParts', text="Clamp Tail Parts")
            layout.prop(particle_system, 'spawnTrailingParts', text="Spawn Trailing Parts")
            layout.prop(particle_system, 'fixLengthTailParts', text="Fix Length Tail Parts")
            layout.prop(particle_system, 'useVertexAlpha', text="Use Vertex Alpha")
            layout.prop(particle_system, 'modelParts', text="Model Parts")
            layout.prop(particle_system, 'swapYZonModelParts', text="Swap Y Z On Model Parts")
            layout.prop(particle_system, 'scaleTimeByParent', text="Scale Time By Parent")
            layout.prop(particle_system, 'useLocalTime', text="Use Local Time")
            layout.prop(particle_system, 'simulateOnInit', text="Simulate On Init")
            layout.prop(particle_system, 'copy', text="Copy")






class RibbonsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_ribbons"
    bl_label = "M3 Ribbons"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_ribbons", scene, "m3_ribbons", scene, "m3_ribbon_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.ribbons_add", icon='ZOOMIN', text="")
        col.operator("m3.ribbons_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_ribbon_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_ribbons):
            ribbon = scene.m3_ribbons[currentIndex]
            layout.separator()
            layout.prop(ribbon, 'boneSuffix',text="Name")
            layout.prop_search(ribbon, 'materialName', scene, 'm3_material_references', text="Material", icon='NONE')
            layout.prop(ribbon, 'ribbonType',text="Type")
            layout.prop(ribbon, 'ribbonDivisions',text="Divisions")
            layout.prop(ribbon, 'ribbonSides',text="Sides")
            layout.prop(ribbon, 'ribbonLength',text="Length")
            layout.prop(ribbon, 'waveLength',text="Wave Length")
            layout.prop(ribbon, 'tipOffsetZ',text="Tip Offset Z")
            layout.prop(ribbon, 'centerBias',text="Center Bias")
            
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Radius Scale")
            sub.prop(ribbon, 'radiusScale', index=0, text="Start")
            sub.prop(ribbon, 'radiusScale', index=1, text="Middle")
            sub.prop(ribbon, 'radiusScale', index=2, text="End")
            
            layout.prop(ribbon, 'twist',text="Twist")
            layout.prop(ribbon, 'baseColoring',text="Base Coloring")
            layout.prop(ribbon, 'centerColoring',text="Center Coloring")
            layout.prop(ribbon, 'tipColoring',text="Tip Coloring")
            layout.prop(ribbon, 'stretchAmount',text="Stretch Amount")
            layout.prop(ribbon, 'stretchLimit',text="Stretch Limit")
            
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Surface Noice")
            sub.prop(ribbon, 'surfaceNoiseAmplitude',text="Amplitude")
            sub.prop(ribbon, 'surfaceNoiseNumberOfWaves',text="Number Of Waves")
            sub.prop(ribbon, 'surfaceNoiseFrequency',text="Frequency")
            sub.prop(ribbon, 'surfaceNoiseScale',text="Scale")

            split = layout.split()
            col = split.column()
            col.prop(ribbon, "directionVariationBool", text="Direction Variation:")
            sub = col.column(align=True)
            sub.active = ribbon.directionVariationBool
            sub.prop(ribbon, "directionVariationAmount", text="Amount")
            sub.prop(ribbon, "directionVariationFrequency", text="Frequency")

            split = layout.split()
            col = split.column()
            col.prop(ribbon, "amplitudeVariationBool", text="Amplitude Variation:")
            sub = col.column(align=True)
            sub.active = ribbon.amplitudeVariationBool
            sub.prop(ribbon, "amplitudeVariationAmount", text="Amount")
            sub.prop(ribbon, "amplitudeVariationFrequency", text="Frequency")

            split = layout.split()
            col = split.column()
            col.prop(ribbon, "lengthVariationBool", text="Length Variation:")
            sub = col.column(align=True)
            sub.active = ribbon.lengthVariationBool
            sub.prop(ribbon, "lengthVariationAmount", text="Amount")
            sub.prop(ribbon, "lengthVariationAmount", text="Frequency")

            split = layout.split()
            col = split.column()
            col.prop(ribbon, "radiusVariationBool", text="Radius Variation:")
            sub = col.column(align=True)
            sub.active = ribbon.radiusVariationBool
            sub.prop(ribbon, "radiusVariationAmount", text="Amount")
            sub.prop(ribbon, "radiusVariationFrequency", text="Frequency")
      
            layout.prop(ribbon, 'collideWithTerrain', text="Collide With Terrain")
            layout.prop(ribbon, 'collideWithObjects', text="Collide With Objects")
            layout.prop(ribbon, 'edgeFalloff', text="Edge Falloff")
            layout.prop(ribbon, 'inheritParentVelocity', text="Inherit Parent Velocity")
            layout.prop(ribbon, 'smoothSize', text="Smooth Size")
            layout.prop(ribbon, 'bezierSmoothSize', text="Bezier Smooth Size")
            layout.prop(ribbon, 'useVertexAlpha', text="Use Vertex Alpha")
            layout.prop(ribbon, 'scaleTimeByParent', text="Scale Time By Parent")
            layout.prop(ribbon, 'forceLegacy', text="Force Legacy")
            layout.prop(ribbon, 'useLocaleTime', text="Use Locale Time")
            layout.prop(ribbon, 'simulateOnInitialization', text="Simulate On Initialization")
            layout.prop(ribbon, 'useLengthAndTime' ,text="Use Length And Time")




class RibbonEndPointsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_ribbon_end_points"
    bl_label = "M3 Ribbon End Point"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        ribbonIndex = scene.m3_ribbon_index
        if ribbonIndex < 0 or ribbonIndex >= len(scene.m3_ribbons):
            return
        
        ribbon = scene.m3_ribbons[ribbonIndex]
        
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_ribbon_end_points", ribbon, "endPoints", ribbon, "endPointIndex", rows=2)

        col = row.column(align=True)
        col.operator("m3.ribbon_end_points_add", icon='ZOOMIN', text="")
        col.operator("m3.ribbon_end_points_remove", icon='ZOOMOUT', text="")
        
        endPointIndex = ribbon.endPointIndex
        if endPointIndex < 0 or endPointIndex >= len(ribbon.endPoints):
            return
        endPoint = ribbon.endPoints[endPointIndex]
        layout.prop(endPoint, 'name', text="Bone Name")

        

class ForcePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_forces"
    bl_label = "M3 Forces"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_forces", scene, "m3_forces", scene, "m3_force_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.forces_add", icon='ZOOMIN', text="")
        col.operator("m3.forces_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_force_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_forces):
            force = scene.m3_forces[currentIndex]
            layout.separator()
            layout.prop(force, 'boneSuffix', text="Name")
            layout.prop(force, "type", text="Type")
            layout.prop(force, "shape", text="Shape")
            layout.prop(force, "channels", text="Channels")
            layout.prop(force, "strength", text="Strength")
            layout.prop(force, "width", text="Width/Radius")
            layout.prop(force, "height", text="Height/Angle")
            layout.prop(force, "length", text="Length")
            layout.prop(force, "useFalloff", text="Use Fall Off")
            layout.prop(force, "useHeightGradient", text="Use Height Gradient")
            layout.prop(force, "unbounded", text="Unbounded")

class RigidBodyPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_rigid_bodies"
    bl_label = "M3 Rigid Bodies"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_rigid_bodies", scene, "m3_rigid_bodies", scene, "m3_rigid_body_index", rows=2)
        
        col = row.column(align=True)
        col.operator("m3.rigid_bodies_add", icon='ZOOMIN', text="")
        col.operator("m3.rigid_bodies_remove", icon='ZOOMOUT', text="")
        
        currentIndex = scene.m3_rigid_body_index
        if not 0 <= currentIndex < len(scene.m3_rigid_bodies):
            return
        rigid_body = scene.m3_rigid_bodies[currentIndex]
        
        layout.separator()
        layout.prop(rigid_body, 'name', text="Name")
        layout.prop(rigid_body, 'boneName', text="Bone")
        
        # TODO: Bone selection from list would be ideal.
        # This is almost correct, but bpy.data contains deleted items too. :(
        #if bpy.data.armatures:
        #    sub.prop_search(rigid_body, 'armatureName', bpy.data, "armatures", text="Armature")    
        #    if rigid_body.armatureName and bpy.data.armatures[rigid_body.armatureName]:
        #        sub.prop_search(rigid_body, 'boneName', bpy.data.armatures[rigid_body.armatureName], "bones", text="Bone")
        
        layout.prop(rigid_body, "unknownAt0")
        layout.prop(rigid_body, "unknownAt4")
        layout.prop(rigid_body, "unknownAt8")
        
        split = layout.split()
        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Collision Flags:")
        sub.prop(rigid_body, 'collidable', text="Collidable")
        sub.prop(rigid_body, 'walkable', text="Walkable")
        sub.prop(rigid_body, 'stackable', text="Stackable")
        sub.prop(rigid_body, 'simulateOnCollision', text="Simulate On Collision")
        sub.prop(rigid_body, 'ignoreLocalBodies', text="Ignore Local Bodies")
        sub.prop(rigid_body, 'alwaysExists', text="Always Exists")
        sub.prop(rigid_body, 'doNotSimulate', text="Do Not Simulate")
        
        layout.prop(rigid_body, 'localForces', text="Local Forces")
        
        split = layout.split()
        col = split.column()
        sub = col.column(align=True)
        sub.label(text="World Forces:")
        sub.prop(rigid_body, 'wind', text="Wind")
        sub.prop(rigid_body, 'explosion', text="Explosion")
        sub.prop(rigid_body, 'energy', text="Energy")
        sub.prop(rigid_body, 'blood', text="Blood")
        sub.prop(rigid_body, 'magnetic', text="Magnetic")
        sub.prop(rigid_body, 'grass', text="Grass")
        sub.prop(rigid_body, 'brush', text="Brush")
        sub.prop(rigid_body, 'trees', text="Trees")
        
        layout.prop(rigid_body, 'priority', text="Priority")

class PhyscisShapePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_physics_shapes"
    bl_label = "M3 Physics Shapes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        
        currentIndex = scene.m3_rigid_body_index
        if not 0 <= currentIndex < len(scene.m3_rigid_bodies):
            layout.label("No rigid body has been selected")
            return
        rigid_body = scene.m3_rigid_bodies[currentIndex]
        
        col.template_list("UI_UL_list", "m3_physics_sahpes", rigid_body, "physicsShapes", rigid_body, "physicsShapeIndex", rows=2)
        col = row.column(align=True)
        col.operator("m3.physics_shapes_add", icon='ZOOMIN', text="")
        col.operator("m3.physics_shapes_remove", icon='ZOOMOUT', text="")
        
        currentIndex = rigid_body.physicsShapeIndex
        if not 0 <= currentIndex < len(rigid_body.physicsShapes):
            return
        physics_shape = rigid_body.physicsShapes[currentIndex]
        
        layout.separator()
        layout.prop(physics_shape, 'name', text="Name")
        
        addUIForShapeProperties(layout, physics_shape)

class PhysicsMeshPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_physics_mesh"
    bl_label = "M3 Physics Mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        o = context.object
        return o and (o.data != None) and (o.type == 'MESH')
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        mesh = context.object.data
        layout.prop(mesh, "m3_physics_mesh", text="Physics Mesh Only")



class VisbilityTestPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_visibility_test"
    bl_label = "M3 Visibility Test"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        layout.prop(scene.m3_visibility_test, 'radius', text="Radius")
        layout.prop(scene.m3_visibility_test, 'center', text="Center")
        layout.prop(scene.m3_visibility_test, 'size', text="Size")

class LightPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_lights"
    bl_label = "M3 Lights"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_lights", scene, "m3_lights", scene, "m3_light_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.lights_add", icon='ZOOMIN', text="")
        col.operator("m3.lights_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_light_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_lights):
            light = scene.m3_lights[currentIndex]
            layout.separator()
            layout.prop(light, 'boneSuffix', text="Name")
            layout.prop(light, "lightType", text="Light Type")
            layout.prop(light, "lightColor", text="Light Color")
            layout.prop(light, "lightIntensity", text="Light Intensity")
            
            split = layout.split()
            col = split.column()
            col.prop(light, "specular", text="Use Specular")
            sub = col.column(align=True)
            sub.active = light.specular
            sub.prop(light, "specColor", text="")
            sub.prop(light, "specIntensity", text="Specular Intensity")
            
            split = layout.split()
            col = split.column()
            col.label(text="Attenuation:");
            sub = col.row(align=True)
            sub.prop(light, "attenuationNear", text="Near")
            sub.prop(light, "attenuationFar", text="Far")
            layout.prop(light, "unknownAt148", text="unknownAt148")
            layout.prop(light, "hotSpot", text="Hot Spot")
            layout.prop(light, "falloff", text="Fall Off")
            layout.prop(light, "unknownAt12", text="unknownAt12")
            layout.prop(light, "shadowCast", text="Shadow Cast")
            layout.prop(light, "unknownFlag0x04", text="Unknown Flag 0x04")
            layout.prop(light, "turnOn", text="Turn On")
            layout.prop(light, "unknownAt8", text="unknownAt8")

class BillboardBehaviorPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_billboard_behavior"
    bl_label = "M3 Billboard Behaviors"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_billboard_behaviors", scene, "m3_billboard_behaviors", scene, "m3_billboard_behavior_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.billboard_behaviors_add", icon='ZOOMIN', text="")
        col.operator("m3.billboard_behaviors_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_billboard_behavior_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_billboard_behaviors):
            billboardBehavior = scene.m3_billboard_behaviors[currentIndex]
            layout.separator()
            layout.prop(billboardBehavior, 'name', text="Bone Name")
            layout.prop(billboardBehavior, "billboardType", text="Billboard Type")

class ProjectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_projections"
    bl_label = "M3 Projections"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_projections", scene, "m3_projections", scene, "m3_projection_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.projections_add", icon='ZOOMIN', text="")
        col.operator("m3.projections_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_projection_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_projections):
            projection = scene.m3_projections[currentIndex]
            layout.separator()
            layout.prop(projection, 'boneSuffix', text="Name")
            layout.prop(projection, "projectionType", text="Type")
            layout.prop_search(projection, 'materialName', scene, 'm3_material_references', text="Material", icon='NONE')
            split = layout.split()
            col = split.column()
            col.label("Orthonormal")
            col.prop(projection, 'depth', text="Depth")
            col.prop(projection, 'width', text="Width")
            col.prop(projection, 'height', text="Height")
            col.active = (projection.projectionType == shared.projectionTypeOrthonormal)
            split = layout.split()
            col = split.column()
            col.label("Perspective")
            col.prop(projection, 'fieldOfView', text="FOV")
            col.prop(projection, 'aspectRatio', text="Aspect Ratio")
            col.prop(projection, 'near', text="Near")
            col.prop(projection, 'far', text="Far")
            col.active = (projection.projectionType == shared.projectionTypePerspective)
            split = layout.split()
            col = split.column()
            col.label(text="Alpha Over Time:")
            split = layout.split()
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Start:")
            sub.prop(projection, 'alphaOverTimeStart', text="Start")
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="Middle:")
            sub.prop(projection, 'alphaOverTimeMid', text="Middle")
            col = split.column()
            sub = col.column(align=True)
            sub.label(text="End:")
            sub.prop(projection, 'alphaOverTimeEnd', text="End")
            split = layout.split()
            col = split.column()
    

class WarpPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_warps"
    bl_label = "M3 Warp Fields"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_warps", scene, "m3_warps", scene, "m3_warp_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.warps_add", icon='ZOOMIN', text="")
        col.operator("m3.warps_remove", icon='ZOOMOUT', text="")
        currentIndex = scene.m3_warp_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_warps):
            warp = scene.m3_warps[currentIndex]
            layout.separator()
            layout.prop(warp, 'boneSuffix', text="Name")
            layout.prop(warp, 'radius', text="Radius")
            layout.prop(warp, 'unknown9306aac0', text="Unk. 9306aac0")
            layout.prop(warp, 'compressionStrength', text="Compression Strength")
            layout.prop(warp, 'unknown50c7f2b4', text="Unk. 50c7f2b4")
            layout.prop(warp, 'unknown8d9c977c', text="Unk. 8d9c977c")
            layout.prop(warp, 'unknownca6025a2', text="Unk. ca6025a2'")
    
class ParticleSystemCopiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_particle_copies"
    bl_label = "M3 Particle Systems Copies"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        
        particleSystemIndex = scene.m3_particle_system_index
        if not(particleSystemIndex >= 0 and particleSystemIndex < len(scene.m3_particle_systems)):
            layout.label("No particle system has been selected")
            return
        particle_system = scene.m3_particle_systems[particleSystemIndex]
        copyIndex = particle_system.copyIndex            
        col.template_list("UI_UL_list", "m3_particle_system_copies", particle_system, "copies", particle_system, "copyIndex", rows=2)

        col = row.column(align=True)
        col.operator("m3.particle_system_copies_add", icon='ZOOMIN', text="")
        col.operator("m3.particle_system_copies_remove", icon='ZOOMOUT', text="")
        if copyIndex >= 0 and copyIndex < len(particle_system.copies):
            copy = particle_system.copies[copyIndex]
            layout.separator()
            layout.prop(copy, 'name',text="Name")
            layout.prop(copy, 'emissionRate', text="Particles Per Second")
            layout.prop(copy, 'partEmit', text="Part. Emit.")


class AttachmentPointsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_attachments"
    bl_label = "M3 Attachment Points"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_attachment_points", scene, "m3_attachment_points", scene, "m3_attachment_point_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.attachment_points_add", icon='ZOOMIN', text="")
        col.operator("m3.attachment_points_remove", icon='ZOOMOUT', text="")

        currentIndex = scene.m3_attachment_point_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_attachment_points):
            attachment_point = scene.m3_attachment_points[currentIndex]
            layout.separator()
            layout.prop(attachment_point, 'boneSuffix', text="Name")
            layout.prop(attachment_point, 'volumeType', text="Volume: ")
            if attachment_point.volumeType in ["1", "2"]: 
                layout.prop(attachment_point, 'volumeSize0', text="Volume Radius")
            elif attachment_point.volumeType in  ["0"]:
                layout.prop(attachment_point, 'volumeSize0', text="Volume Width")
            if attachment_point.volumeType in ["0"]:
                layout.prop(attachment_point, 'volumeSize1', text="Volume Length")
            elif attachment_point.volumeType in ["2"]:
                layout.prop(attachment_point, 'volumeSize1', text="Volume Height")
            if attachment_point.volumeType in ["0"]:
                layout.prop(attachment_point, 'volumeSize2', text="Volume Height")


def addUIForShapeProperties(layout, shapeObject):
    layout.prop(shapeObject, 'shape', text="Shape: ")
    
    if shapeObject.shape in ["0", "1", "2", "3"]:
        split = layout.split()
        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Dimensions")
        if shapeObject.shape in ["0"]: #cuboid
            sub.prop(shapeObject, "size0", text="Width")
            sub.prop(shapeObject, "size1", text="Length")
            sub.prop(shapeObject, "size2", text="Height")
        elif shapeObject.shape in ["1"]: #sphere
            sub.prop(shapeObject, "size0", text="Radius")
        elif shapeObject.shape in ["2"]: #capsule
            sub.prop(shapeObject, "size0", text="Radius")
            sub.prop(shapeObject, "size1", text="Height")
        elif shapeObject.shape in ["3"]: #cylinder
            sub.prop(shapeObject, "size0", text="Radius")
            sub.prop(shapeObject, "size1", text="Height")
    elif shapeObject.shape in ["4", "5"]:
        layout.prop(shapeObject, "meshObjectName", text="Mesh Name")
    
    split = layout.split()
    col = split.column()
    sub = col.column(align=True)
    
    sub.label(text="Offset")
    sub.prop(shapeObject, 'offset', index=0, text="X")
    sub.prop(shapeObject, 'offset', index=1, text="Y")
    sub.prop(shapeObject, 'offset', index=2, text="Z")
    
    sub.label(text="Rotation (Euler)")
    sub.prop(shapeObject, 'rotationEuler', index=0, text="X")
    sub.prop(shapeObject, 'rotationEuler', index=1, text="Y")
    sub.prop(shapeObject, 'rotationEuler', index=2, text="Z")
    
    sub.label(text="Scale")
    sub.prop(shapeObject, 'scale', index=0, text="X")
    sub.prop(shapeObject, 'scale', index=1, text="Y")
    sub.prop(shapeObject, 'scale', index=2, text="Z")

class FuzzyHitTestPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_fuzzyhittests"
    bl_label = "M3 Fuzzy Hit Tests"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "m3_fuzzy_hit_tests", scene, "m3_fuzzy_hit_tests", scene, "m3_fuzzy_hit_test_index", rows=2)

        col = row.column(align=True)
        col.operator("m3.fuzzy_hit_tests_add", icon='ZOOMIN', text="")
        col.operator("m3.fuzzy_hit_tests_remove", icon='ZOOMOUT', text="")

        currentIndex = scene.m3_fuzzy_hit_test_index
        if currentIndex >= 0 and currentIndex < len(scene.m3_fuzzy_hit_tests):
            fuzzy_hit_test = scene.m3_fuzzy_hit_tests[currentIndex]
            layout.separator()
            addUIForShapeProperties(layout, fuzzy_hit_test)

class TightHitTestPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_tighthittest"
    bl_label = "M3 Tight Hit Test"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if scene.m3_tight_hit_test.name == "":
            layout.operator("m3.tight_hit_test_select_or_create_bone", text="Create Bone")
        else:
            layout.operator("m3.tight_hit_test_select_or_create_bone", text="Select Bone")
            layout.operator("m3.tight_hit_test_remove", text="Remove Tight Hit Test");
        split = layout.split()
        row = split.row()
        sub = row.column(align=False)
        sub.active = scene.m3_tight_hit_test.name != ""
        addUIForShapeProperties(sub, scene.m3_tight_hit_test)


class ExtraBonePropertiesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_M3_bone_properties"
    bl_label = "M3 Bone Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    
    @classmethod
    def poll(cls, context):
        return context.bone != None

    def draw(self, context):
        layout = self.layout
        bone = context.bone
        row = layout.row()
        col = row.column()
        layout.prop(bone, 'm3_bind_scale', text="Bind Scale")



class M3_MATERIALS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.materials_add'
    bl_label       = "Add M3 Material"
    bl_description = "Adds an material for the export to Starcraft 2"

    defaultSetting = bpy.props.EnumProperty(items=matDefaultSettingsList, options=set(), default="MESH")
    materialName = bpy.props.StringProperty(name="materialName", default="01", options=set())
    
    def invoke(self, context, event):
        scene = context.scene
        self.materialName = finUnusedMaterialName(scene)
        context.window_manager.invoke_props_dialog(self, width=250)
        return {'RUNNING_MODAL'}  
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "defaultSetting", text="Default Settings") 
        layout.prop(self, "materialName", text="Name") 

  
    def execute(self, context):
        scene = context.scene
        createMaterial(scene, self.materialName, self.defaultSetting)
        return {'FINISHED'}
    
class M3_MATERIALS_OT_createForMesh(bpy.types.Operator):
    bl_idname      = 'm3.create_material_for_mesh'
    bl_label       = "Creates a M3 Material for the current mesh"
    bl_description = "Creates an m3 material for the current mesh"

    defaultSetting = bpy.props.EnumProperty(items=matDefaultSettingsList, options=set(), default="MESH")
    materialName = bpy.props.StringProperty(name="materialName", default="01", options=set())
    
    def invoke(self, context, event):
        scene = context.scene
        self.materialName = finUnusedMaterialName(scene)
        context.window_manager.invoke_props_dialog(self, width=250)
        return {'RUNNING_MODAL'}  
        
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "defaultSetting", text="Default Settings") 
        layout.prop(self, "materialName", text="Name") 
  

  
    def execute(self, context):
        scene = context.scene
        meshObject = context.object
        mesh = meshObject.data
        createMaterial(scene, self.materialName, self.defaultSetting)
        mesh.m3_material_name = self.materialName

        return {'FINISHED'}
    
    
class M3_MATERIALS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.materials_remove'
    bl_label       = "Remove M3 Material"
    bl_description = "Removes the active M3 Material"
    
    def invoke(self, context, event):
        scene = context.scene
        referenceIndex = scene.m3_material_reference_index
        if referenceIndex>= 0:
            materialReference = scene.m3_material_references[referenceIndex]
            materialName = materialReference.name
            # Check if material is in use, and abort:
            for particle_system in scene.m3_particle_systems:
                if particle_system.materialName == materialName:
                    self.report({"ERROR"}, "Can't delete: The particle system '%s' is using this material" % particle_system.name)
                    return {"CANCELLED"}
            for ribbon in scene.m3_ribbons:
                if ribbon.materialName == materialName:
                    self.report({"ERROR"}, "Can't delete: The ribbon '%s' is using this material" % ribbon.name)
                    return {"CANCELLED"}
            for projection in scene.m3_projections:
                if projection.materialName == materialName:
                    self.report({"ERROR"}, "Can't delete: The projection '%s' is using this material" % projection.name)
                    return {"CANCELLED"}
            for meshObject in shared.findMeshObjects(scene):
                mesh = meshObject.data
                if mesh.m3_material_name == materialName:
                    self.report({"ERROR"}, "Can't delete: The object '%s' (mesh '%s') is using this material." % (meshObject.name, mesh.name))
                    return {"CANCELLED"}
            
            for higherReferenceIndex in range(referenceIndex+1,len(scene.m3_material_references)):
                higherReference = scene.m3_material_references[higherReferenceIndex]
                material = shared.getMaterial(scene, higherReference.materialType, higherReference.materialIndex)
                if material != None:
                    material.materialReferenceIndex -= 1
                    
            materialReference = scene.m3_material_references[referenceIndex]
            materialIndex = materialReference.materialIndex
            materialType = materialReference.materialType
            
            for otherReference in scene.m3_material_references:
                if otherReference.materialType == materialType and otherReference.materialIndex > materialIndex:
                    otherReference.materialIndex -= 1
                
            blenderMaterialsFieldName = shared.blenderMaterialsFieldNames[materialType]
            blenderMaterialsField = getattr(scene, blenderMaterialsFieldName)
            blenderMaterialsField.remove(materialIndex)
           
            
            scene.m3_material_references.remove(scene.m3_material_reference_index)
            scene.m3_material_reference_index -= 1
        return{'FINISHED'}

class M3_COMPOSITE_MATERIAL_OT_add_section(bpy.types.Operator):
    bl_idname      = 'm3.composite_material_add_section'
    bl_label       = "Add a section/layer to the composite material"
    bl_description = "Adds a section/layer to the composite material"

    def invoke(self, context, event):
        scene = context.scene
        materialIndex = scene.m3_material_reference_index
        if materialIndex >= 0 and materialIndex < len(scene.m3_material_references):
            materialReference = scene.m3_material_references[materialIndex]
            materialType = materialReference.materialType
            materialIndex = materialReference.materialIndex
            if materialType == shared.compositeMaterialTypeIndex:
                material = shared.getMaterial(scene, materialType, materialIndex)
                section = material.sections.add()
                if len(scene.m3_material_references) >= 1:
                    section.name = scene.m3_material_references[0].name
                material.sectionIndex = len(material.sections)-1                
        return{'FINISHED'}

class M3_COMPOSITE_MATERIAL_OT_remove_section(bpy.types.Operator):
    bl_idname      = 'm3.composite_material_remove_section'
    bl_label       = "Removes the selected section/layer from the composite material"
    bl_description = "Removes the selected section/layer from the composite material"

    def invoke(self, context, event):
        scene = context.scene
        materialIndex = scene.m3_material_reference_index
        if materialIndex >= 0 and materialIndex < len(scene.m3_material_references):
            materialReference = scene.m3_material_references[materialIndex]
            materialType = materialReference.materialType
            materialIndex = materialReference.materialIndex
            if materialType == shared.compositeMaterialTypeIndex:
                material = shared.getMaterial(scene, materialType, materialIndex)
                sectionIndex = material.sectionIndex
                if (sectionIndex >= 0) and (sectionIndex < len(material.sections)):
                    material.sections.remove(sectionIndex)
                    material.sectionIndex = material.sectionIndex-1                
        return{'FINISHED'}

class M3_ANIMATIONS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.animations_add'
    bl_label       = "Add Animation Sequence"
    bl_description = "Adds an animation sequence for the export to Starcraft 2"

    def invoke(self, context, event):
        scene = context.scene
        animation = scene.m3_animations.add()
        name = self.findUnusedName(scene)
        animation.name = name
        animation.startFrame = 0
        animation.exlusiveEndFrame = 60
        animation.frequency = 1
        animation.movementSpeed = 0.0
        scene.m3_animation_index = len(scene.m3_animations)-1
        return{'FINISHED'}
        
    def findUnusedName(self, scene):
        usedNames = set()
        for animation in scene.m3_animations:
            usedNames.add(animation.name)
        suggestedNames = ["Birth", "Stand", "Death", "Walk", "Attack"]
        unusedName = None
        for suggestedName in suggestedNames:
            if not suggestedName in usedNames:
                unusedName = suggestedName
                break
        counter = 1
        while unusedName == None:
            suggestedName = "Stand %02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName

def removeTrackFor(objectWithAnimationData, animation):
    animationData = objectWithAnimationData.animation_data
    if animationData != None:
        trackName = getTrackName(animation)
        track = animationData.nla_tracks.get(trackName)
        if track != None:
            animationData.nla_tracks.remove(track)
       
class M3_ANIMATIONS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.animations_remove'
    bl_label       = "Remove Animation Sequence"
    bl_description = "Removes the active M3 animation sequence"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_animation_index >= 0:
            animation = scene.m3_animations[scene.m3_animation_index]

            for targetObject in scene.objects:
                removeTrackFor(targetObject, animation)
            
            if scene.animation_data != None:
                removeTrackFor(scene, animation)
            
            scene.m3_animations.remove(scene.m3_animation_index)
            scene.m3_animation_old_index = -1
            scene.m3_animation_index -= 1
        return{'FINISHED'}
    
def copyCurrentActionOfObjectToM3Animation(objectWithAnimationData, targetAnimation):
    animationData = objectWithAnimationData.animation_data
    if animationData == None:
        return
    
    sourceAction = animationData.action
    if sourceAction == None:
        return
    
    targetStrip = getOrCreateStrip(targetAnimation, animationData)
    
    newAction = bpy.data.actions.new(objectWithAnimationData.name + targetAnimation.name)
    
    for sourceCurve in sourceAction.fcurves:
        path = sourceCurve.data_path
        arrayIndex = sourceCurve.array_index
        if sourceCurve.group != None:
            groupName = sourceCurve.group.name
            targetCurve = newAction.fcurves.new(path, arrayIndex, groupName)
        else:
            targetCurve = newAction.fcurves.new(path, arrayIndex)
        targetCurve.extrapolation = sourceCurve.extrapolation
        targetCurve.color_mode = sourceCurve.color_mode
        targetCurve.color = sourceCurve.color
        for sourceKeyFrame in sourceCurve.keyframe_points:
            frame = sourceKeyFrame.co.x
            value = sourceKeyFrame.co.y
            targetKeyFrame = targetCurve.keyframe_points.insert(frame, value)
            targetKeyFrame.handle_left_type = sourceKeyFrame.handle_left_type
            targetKeyFrame.handle_right_type = sourceKeyFrame.handle_right_type
            targetKeyFrame.interpolation = sourceKeyFrame.interpolation
            targetKeyFrame.type = sourceKeyFrame.type
            targetKeyFrame.handle_left.x = sourceKeyFrame.handle_left.x
            targetKeyFrame.handle_left.y = sourceKeyFrame.handle_left.y
            targetKeyFrame.handle_right.x = sourceKeyFrame.handle_right.x
            targetKeyFrame.handle_right.y = sourceKeyFrame.handle_right.y

    targetStrip.action = newAction


class M3_ANIMATIONS_OT_duplicate(bpy.types.Operator):
    bl_idname      = 'm3.animations_duplicate'
    bl_label       = "Create identical copy of the animation"
    bl_description = "Create identical copy of the animation"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_animation_index < 0:
            return{'FINISHED'}
        oldAnimation = scene.m3_animations[scene.m3_animation_index]
        
        uniqueNameFinder = shared.UniqueNameFinder()
        uniqueNameFinder.markNamesOfCollectionAsUsed(scene.m3_animations)
        
        newAnimation = scene.m3_animations.add()
        newAnimation.name = uniqueNameFinder.findNameAndMarkAsUsedLike(oldAnimation.name)
        newAnimation.startFrame = oldAnimation.startFrame
        newAnimation.exlusiveEndFrame = oldAnimation.exlusiveEndFrame
        newAnimation.frequency = oldAnimation.frequency
        newAnimation.movementSpeed = oldAnimation.movementSpeed
        
                
        for targetObject in scene.objects:
            copyCurrentActionOfObjectToM3Animation(targetObject, newAnimation)
        
        if scene.animation_data != None:
            copyCurrentActionOfObjectToM3Animation(scene, newAnimation)

        scene.m3_animation_index = len(scene.m3_animations)-1
   
        return{'FINISHED'}


class M3_ANIMATIONS_OT_deselect(bpy.types.Operator):
    bl_idname      = 'm3.animations_deselect'
    bl_label       = "Edit Default Values"
    bl_description = "Deselects the active M3 animation sequence so that the user can edit the default values"
    
    def invoke(self, context, event):
        scene = context.scene
        scene.m3_animation_index = -1
        return{'FINISHED'}

class M3_ANIMATIONS_OT_STC_add(bpy.types.Operator):
    bl_idname      = 'm3.stc_add'
    bl_label       = "Add sub animation"
    bl_description = "Add sub animation to the active animation sequence"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_animation_index >= 0:
            animation = scene.m3_animations[scene.m3_animation_index]
            stcIndex = len(animation.transformationCollections)
            stc = animation.transformationCollections.add()
            stc.name = self.findUnusedName(animation.transformationCollections)
            animation.transformationCollectionIndex = stcIndex

        return{'FINISHED'}
        
    def findUnusedName(self, existingSTCs):
        usedNames = set()
        for stc in existingSTCs:
            usedNames.add(stc.name)
        suggestedNames = ["full"]
        unusedName = None
        for suggestedName in suggestedNames:
            if not suggestedName in usedNames:
                unusedName = suggestedName
                break
        counter = 2
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName
        
class M3_ANIMATIONS_OT_STC_remove(bpy.types.Operator):
    bl_idname      = 'm3.stc_remove'
    bl_label       = "Remove sub animation from animation"
    bl_description = "Removes the active sub animation from animation sequence"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_animation_index >= 0:
            animation = scene.m3_animations[scene.m3_animation_index]
            stcIndex = animation.transformationCollectionIndex
            if stcIndex >= 0 and stcIndex < len(animation.transformationCollections):
                animation.transformationCollections.remove(stcIndex)
                animation.transformationCollectionIndex -= 1

        return{'FINISHED'}

class M3_ANIMATIONS_OT_STC_select(bpy.types.Operator):
    bl_idname      = 'm3.stc_select'
    bl_label       = "Select all FCurves of the active sub animation"
    bl_description = "Selects all FCURVES of the active sub animation"
    
    def invoke(self, context, event):
        scene = context.scene        
        longAnimIds = set()
        
        stc = None
        if scene.m3_animation_index >= 0:
            animation = scene.m3_animations[scene.m3_animation_index]
            stcIndex = animation.transformationCollectionIndex
            if stcIndex >= 0 and stcIndex < len(animation.transformationCollections):
                stc = animation.transformationCollections[stcIndex]
        if stc != None:
            for animatedProperty in stc.animatedProperties:
                longAnimId = animatedProperty.longAnimId
                longAnimIds.add(longAnimId)
                        
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                armature = obj.data
                selectObject = False
                for bone in armature.bones:
                    animPathPrefix = 'pose.bones["' + bone.name + '"].'
                    objectId = shared.animObjectIdArmature
                    boneLongAnimIds = set()
                    rotLongAnimId = shared.getLongAnimIdOf(objectId, animPathPrefix + "rotation_quaternion")
                    locLongAnimId = shared.getLongAnimIdOf(objectId, animPathPrefix + "location")
                    scaleLongAnimId = shared.getLongAnimIdOf(objectId, animPathPrefix + "scale")
                    if (rotLongAnimId in longAnimIds) or (locLongAnimId in longAnimIds) or (scaleLongAnimId in longAnimIds):
                        bone.select = True
                        selectObject = True
                    else:
                        bone.select = False
                # Select object at the end, otherwise Blender 2.63a
                # does not notice bone selection even if object is already selected
                obj.select = selectObject
                if obj.animation_data != None:
                    action = obj.animation_data.action
                    if action != None:
                        for fcurve in action.fcurves:
                            animPath = fcurve.data_path
                            objectId = shared.animObjectIdArmature
                            longAnimId = shared.getLongAnimIdOf(objectId, animPath)
                            fcurve.select = longAnimId in longAnimIds
                        
        if scene.animation_data != None:
            action = scene.animation_data.action
            if action != None:
                for fcurve in action.fcurves:
                    animPath = fcurve.data_path
                    objectId = shared.animObjectIdScene
                    longAnimId = shared.getLongAnimIdOf(objectId, animPath)
                    fcurve.select = longAnimId in longAnimIds
                        
                    
        return{'FINISHED'}


    
class M3_ANIMATIONS_OT_STC_assign(bpy.types.Operator):
    bl_idname      = 'm3.stc_assign'
    bl_label       = "Assign FCurves to sub animation"
    bl_description = "Assigns all selected FCurves to the active sub animation"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_animation_index < 0:
            return {'FINISHED'}
        
        selectedLongAnimIds = set(self.getSelectedLongAnimIdsOfCurrentActions(scene))

        animation = scene.m3_animations[scene.m3_animation_index]
        selectedSTCIndex = animation.transformationCollectionIndex
        
        for stcIndex, stc in enumerate(animation.transformationCollections):
            if stcIndex == selectedSTCIndex:
                stc.animatedProperties.clear()
                for longAnimId in selectedLongAnimIds:
                    animatedProperty = stc.animatedProperties.add()
                    animatedProperty.longAnimId = longAnimId
            else:
                #Remove selected properties from the other STCs:
                longAnimIds = set()
                for animatedProperty in stc.animatedProperties:
                    longAnimIds.add(animatedProperty.longAnimId)
                longAnimIds = longAnimIds - selectedLongAnimIds
                stc.animatedProperties.clear()
                for longAnimId in longAnimIds:
                    animatedProperty = stc.animatedProperties.add()
                    animatedProperty.longAnimId = longAnimId

        return{'FINISHED'}
           
                
    def getSelectedAnimationPaths(self, objectWithAnimData):
        if objectWithAnimData.animation_data != None:
            action = objectWithAnimData.animation_data.action
            if action != None:
                for fcurve in action.fcurves:
                    if fcurve.select:
                        animPath = fcurve.data_path
                        yield animPath

    def getSelectedLongAnimIdsOfCurrentActions(self, scene):
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                for animPath in self.getSelectedAnimationPaths(obj):
                    yield shared.getLongAnimIdOf(shared.animObjectIdArmature, animPath)
        for animPath in self.getSelectedAnimationPaths(scene):          
            yield shared.getLongAnimIdOf(shared.animObjectIdScene, animPath)
            
class M3_CAMERAS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.cameras_add'
    bl_label       = "Add M3 Camera"
    bl_description = "Adds a camera description for the export as m3"

    def invoke(self, context, event):
        scene = context.scene
        camera = scene.m3_cameras.add()
        camera.name = self.findUnusedName(scene)

        # The following selection causes a new bone to be created:
        scene.m3_camera_index = len(scene.m3_cameras)-1
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for camera in scene.m3_cameras:
            usedNames.add(camera.name)
        
        suggestedNames = ["CameraPortrait", "CameraAvatar"]
        unusedName = None
        for suggestedName in suggestedNames:
            if not suggestedName in usedNames:
                unusedName = suggestedName
                break
        counter = 1
        while unusedName == None:
            suggestedName = "Camera %02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName


class M3_CAMERAS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.cameras_remove'
    bl_label       = "Remove Camera"
    bl_description = "Removes the active M3 camera"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_camera_index >= 0:
            camera = scene.m3_cameras[scene.m3_camera_index]
            removeBone(scene, camera.name)
            scene.m3_cameras.remove(scene.m3_camera_index)
            scene.m3_camera_index-= 1
        return{'FINISHED'}

class M3_PARTICLE_SYSTEMS_OT_create_spawn_points_from_mesh(bpy.types.Operator):
    bl_idname      = 'm3.create_spawn_points_from_mesh'
    bl_label       = "Create Spawn Points From Mesh"
    bl_description = "Uses the vertices of the current mesh as spawn points for particles"

    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_particle_system_index >= 0:
            particleSystem = scene.m3_particle_systems[scene.m3_particle_system_index]
            particleSystem.spawnPoints.clear()
            activeObject = context.active_object 
            if activeObject != None and activeObject.type == 'MESH':
                mesh = activeObject.data
                mesh.update(calc_tessface=True)
                particleSystem.spawnPoints.clear()
                for vertex in mesh.vertices:
                    spawnPoint = particleSystem.spawnPoints.add()
                    spawnPoint.location = vertex.co.copy()
                selectOrCreateBoneForPartileSystem(scene, particleSystem)
                updateBoenShapesOfParticleSystemCopies(scene, particleSystem)
                return{'FINISHED'}
            else:
                raise Exception("No mesh selected")

        
class M3_PARTICLE_SYSTEMS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.particle_systems_add'
    bl_label       = "Add Particle System"
    bl_description = "Adds a particle system for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        particle_system = scene.m3_particle_systems.add()
        particle_system.name = findUnusedParticleSystemName(scene)
        if len(scene.m3_material_references) >= 1:
            particle_system.materialName = scene.m3_material_references[0].name

        handleParticleSystemTypeOrNameChange(particle_system, context)
        
        # The following selection causes a new bone to be created:
        scene.m3_particle_system_index = len(scene.m3_particle_systems)-1
        return{'FINISHED'}



class M3_PARTICLE_SYSTEMS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.particle_systems_remove'
    bl_label       = "Remove Particle System"
    bl_description = "Removes the active M3 particle system"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_particle_system_index >= 0:
            particleSystem = scene.m3_particle_systems[scene.m3_particle_system_index]
            removeBone(scene, particleSystem.boneName)
            for copy in particleSystem.copies:
                removeBone(scene, copy.boneName)
            scene.m3_particle_systems.remove(scene.m3_particle_system_index)
            scene.m3_particle_system_index-= 1
            
        return{'FINISHED'}
        
        

class M3_PARTICLE_SYSTEM_COPIES_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.particle_system_copies_add'
    bl_label       = "Add Particle System Copy"
    bl_description = "Adds a particle system copy for the export to the m3 model format"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        particleSystemIndex = scene.m3_particle_system_index
        return (particleSystemIndex >= 0 and particleSystemIndex < len(scene.m3_particle_systems))


    def invoke(self, context, event):
        scene = context.scene
        particle_system = scene.m3_particle_systems[scene.m3_particle_system_index]
        copy = particle_system.copies.add()
        copy.name = findUnusedParticleSystemName(scene)
        if len(scene.m3_material_references) >= 1:
            particle_system.materialName = scene.m3_material_references[0].name

        handleParticleSystemCopyRename(copy,context)
        particle_system.copyIndex = len(particle_system.copies)-1
        
        selectOrCreateBoneForPartileSystemCopy(scene, particle_system, copy)
        return{'FINISHED'}


class M3_PARTICLE_SYSTEMS_COPIES_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.particle_system_copies_remove'
    bl_label       = "Remove Particle System Copy"
    bl_description = "Removes the active copy from the M3 particle system"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        particleSystemIndex = scene.m3_particle_system_index
        if not (particleSystemIndex >= 0 and particleSystemIndex < len(scene.m3_particle_systems)):
            return False
        particleSystem = scene.m3_particle_systems[particleSystemIndex]
        copyIndex = particleSystem.copyIndex
        return (copyIndex >= 0 and copyIndex < len(particleSystem.copies))

    def invoke(self, context, event):
        scene = context.scene
        particleSystemIndex = scene.m3_particle_system_index
        particleSystem = scene.m3_particle_systems[particleSystemIndex]
        copyIndex = particleSystem.copyIndex
        copy = particleSystem.copies[copyIndex]
        removeBone(scene, copy.boneName)
        particleSystem.copies.remove(particleSystem.copyIndex)
        particleSystem.copyIndex -= 1

        
        return{'FINISHED'}



class M3_RIBBONS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.ribbons_add'
    bl_label       = "Add Ribbon"
    bl_description = "Adds a ribbon for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        ribbon = scene.m3_ribbons.add()
        ribbon.boneSuffix = self.findUnusedName(scene)
        if len(scene.m3_material_references) >= 1:
            ribbon.materialName = scene.m3_material_references[0].name

        handleRibbonBoneSuffixChange(ribbon, context)
        
        # The following selection causes a new bone to be created:
        scene.m3_ribbon_index = len(scene.m3_ribbons)-1
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for ribbon in scene.m3_ribbons:
            usedNames.add(ribbon.boneSuffix)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 


class M3_RIBBONS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.ribbons_remove'
    bl_label       = "Remove Ribbon"
    bl_description = "Removes the active M3 ribbon"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_ribbon_index >= 0:
            ribbon = scene.m3_ribbons[scene.m3_particle_system_index]
            removeBone(scene, ribbon.boneName)
            # endPoint do now own the bone, thus we must not delete it:
            #for endPoint in ribbon.endPoints:
            #    removeBone(scene, endPoint.name)
            scene.m3_ribbons.remove(scene.m3_ribbon_index)
            scene.m3_ribbon_index-= 1
            
        return{'FINISHED'}


class M3_RIBBON_END_POINTS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.ribbon_end_points_add'
    bl_label       = "Add Ribbon End Point"
    bl_description = "Adds an end point to the current ribbon"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        ribbonIndex = scene.m3_ribbon_index
        if ribbonIndex < 0 or ribbonIndex > len(scene.m3_ribbons):
            return False
        ribbon = scene.m3_ribbons[ribbonIndex]
        if len(ribbon.endPoints) >= 1:
            return False # No known model has more then 1 end point
        
        return True

    def invoke(self, context, event):
        scene = context.scene
        ribbonIndex = scene.m3_ribbon_index
        if ribbonIndex < 0 or ribbonIndex > len(scene.m3_ribbons):
            return
        
        ribbon = scene.m3_ribbons[ribbonIndex]
        
        endPoint = ribbon.endPoints.add()
        
        # The following selection causes a new bone to be created:
        ribbon.endPointIndex = len(ribbon.endPoints)-1
        return{'FINISHED'}
    


class M3_RIBBON_END_POINTS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.ribbon_end_points_remove'
    bl_label       = "Remove RibbonEnd Point"
    bl_description = "Removes the active ribbon end point"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        ribbonIndex = scene.m3_ribbon_index
        if ribbonIndex < 0 or ribbonIndex > len(scene.m3_ribbons):
            return False
        
        ribbon = scene.m3_ribbons[ribbonIndex]

        endPointIndex = ribbon.endPointIndex
        
        if endPointIndex < 0 or endPointIndex > len(ribbon.endPoints):
            return False
        
        return True
    
    def invoke(self, context, event):
        scene = context.scene
        ribbonIndex = scene.m3_ribbon_index
        if ribbonIndex < 0 or ribbonIndex > len(scene.m3_ribbons):
            return {'FINISHED'} # nothing to remove
        
        ribbon = scene.m3_ribbons[ribbonIndex]
        
        endPointIndex = ribbon.endPointIndex
       
        if endPointIndex < 0 or endPointIndex > len(ribbon.endPoints):
            return {'FINISHED'} # nothing to remove

        endPoint = ribbon.endPoints[endPointIndex]
        # end points don't own bones yet:
        # removeBone(scene, endPoint.name)
        ribbon.endPoints.remove(endPointIndex)
        ribbon.endPointIndex -= 1
        return{'FINISHED'}


class M3_FORCES_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.forces_add'
    bl_label       = "Add Force"
    bl_description = "Adds a particle system force for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        force = scene.m3_forces.add()
        force.updateBlenderBoneShape = False
        force.boneSuffix = self.findUnusedName(scene)
        handleForceTypeOrBoneSuffixChange(force, context)
        force.boneName = shared.boneNameForForce(force)
        force.updateBlenderBoneShape = True

        # The following selection causes a new bone to be created:
        scene.m3_force_index = len(scene.m3_forces)-1
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for force in scene.m3_forces:
            usedNames.add(force.boneSuffix)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 

class M3_FORCES_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.forces_remove'
    bl_label       = "Remove M3 Force"
    bl_description = "Removes the active M3 particle system force"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_force_index >= 0:
            force = scene.m3_forces[scene.m3_force_index]
            removeBone(scene, force.boneName)
            scene.m3_forces.remove(scene.m3_force_index)
            scene.m3_force_index-= 1
        return{'FINISHED'}

class M3_RIGID_BODIES_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.rigid_bodies_add'
    bl_label       = "Add Rigid Body"
    bl_description = "Adds a rigid body for export to the m3 model format"
    
    def invoke(self, context, event):
        scene = context.scene
        rigid_body = scene.m3_rigid_bodies.add()
        
        rigid_body.name = self.findUnusedName(scene)
        rigid_body.boneName = ""
        
        scene.m3_rigid_body_index = len(scene.m3_rigid_bodies) - 1
        return {'FINISHED'}
    
    def findUnusedName(self, scene):
        usedNames = set()
        for rigid_body in scene.m3_rigid_bodies:
            usedNames.add(rigid_body.name)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName

class M3_RIGID_BODIES_OT_remove(bpy.types.Operator):
    bl_idname = 'm3.rigid_bodies_remove'
    bl_label = "Remove M3 Rigid Body"
    bl_description = "Removes the active M3 rigid body (and the M3 Physics Shapes it contains)"
    
    def invoke(self, context, event):
        scene = context.scene
        
        currentIndex = scene.m3_rigid_body_index
        if not 0 <= currentIndex < len(scene.m3_rigid_bodies):
            return {'CANCELLED'}
        
        shared.removeRigidBodyBoneShape(scene, scene.m3_rigid_bodies[currentIndex])
        
        scene.m3_rigid_bodies.remove(currentIndex)
        scene.m3_rigid_body_index -= 1
        
        return {'FINISHED'}

class M3_PHYSICS_SHAPES_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.physics_shapes_add'
    bl_label       = "Add Physics Shape"
    bl_description = "Adds an M3 physics shape to the active M3 rigid body"
    
    def invoke(self, context, event):
        scene = context.scene
        
        currentIndex = scene.m3_rigid_body_index
        if not 0 <= currentIndex < len(scene.m3_rigid_bodies):
            return {'CANCELLED'}
        rigid_body = scene.m3_rigid_bodies[currentIndex]
        
        physics_shape = rigid_body.physicsShapes.add()
        physics_shape.name = self.findUnusedName(rigid_body)
        
        rigid_body.physicsShapeIndex = len(rigid_body.physicsShapes) - 1
        shared.updateBoneShapeOfRigidBody(scene, rigid_body)
        
        return {'FINISHED'}
    
    def findUnusedName(self, rigid_body):
        usedNames = set()
        for physics_shape in rigid_body.physicsShapes:
            usedNames.add(physics_shape.name)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName

class M3_PHYSICS_SHAPES_OT_remove(bpy.types.Operator):
    bl_idname = 'm3.physics_shapes_remove'
    bl_label = "Remove M3 Physics Shape"
    bl_description = "Removes the active M3 physics shape"
    
    def invoke(self, context, event):
        scene = context.scene
        
        currentIndex = scene.m3_rigid_body_index
        if not 0 <= currentIndex < len(scene.m3_rigid_bodies):
            return {'CANCELLED'}
        rigid_body = scene.m3_rigid_bodies[currentIndex]
        
        currentIndex = rigid_body.physicsShapeIndex
        if not 0 <= currentIndex < len(rigid_body.physicsShapes):
            return {'CANCELLED'}
        
        rigid_body.physicsShapes.remove(currentIndex)
        rigid_body.physicsShapeIndex -= 1
        shared.updateBoneShapeOfRigidBody(scene, rigid_body)
        
        return {'FINISHED'}




class M3_LIGHTS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.lights_add'
    bl_label       = "Add Light"
    bl_description = "Adds a particle system light for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        light = scene.m3_lights.add()
        light.updateBlenderBone = False
        light.boneSuffix = self.findUnusedName(scene)
        light.boneName = shared.boneNameForLight(light)
        handleLightTypeOrBoneSuffixChange(light, context)
        light.updateBlenderBone = True
        
        # The following selection causes a new bone to be created:
        scene.m3_light_index = len(scene.m3_lights)-1
        
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for light in scene.m3_lights:
            usedNames.add(light.boneSuffix)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 

class M3_LIGHTS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.lights_remove'
    bl_label       = "Remove M3 Light"
    bl_description = "Removes the active M3 particle system light"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_light_index >= 0:
            light = scene.m3_lights[scene.m3_light_index]
            removeBone(scene, light.boneName)
            scene.m3_lights.remove(scene.m3_light_index)
            scene.m3_light_index-= 1
        return{'FINISHED'}
    
class M3_BILLBOARD_BEHAVIORS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.billboard_behaviors_add'
    bl_label       = "Add Billboard Behavior"
    bl_description = "Adds a billboard behavior"

    def invoke(self, context, event):
        scene = context.scene
        behavior = scene.m3_billboard_behaviors.add()
        
        selectedBoneName = None
        if context.active_bone != None:
            selectedBoneName = context.active_bone.name
        if selectedBoneName == None or selectedBoneName in scene.m3_billboard_behaviors:
            unusedName = self.findUnusedName(scene)
            behavior.name = unusedName        
        else:
            behavior.name = selectedBoneName        

        # The following selection causes a new bone to be created:
        scene.m3_billboard_behavior_index = len(scene.m3_billboard_behaviors)-1
        
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for behavior in scene.m3_billboard_behaviors:
            usedNames.add(behavior.name)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "Billboard Behavior %02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 
    
class M3_BILLBOARD_BEHAVIORS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.billboard_behaviors_remove'
    bl_label       = "Remove M3 Billboard Behavior"
    bl_description = "Removes the active M3 billboard behavior"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_billboard_behavior_index >= 0:
            behavior = scene.m3_billboard_behaviors[scene.m3_billboard_behavior_index]
            scene.m3_billboard_behaviors.remove(scene.m3_billboard_behavior_index)
            scene.m3_billboard_behavior_index -= 1
        return{'FINISHED'}

class M3_PROJECTIONS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.projections_add'
    bl_label       = "Add Projection"
    bl_description = "Adds a projection for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        projection = scene.m3_projections.add()
        projection.updateBlenderBone = False
        projection.boneSuffix = self.findUnusedName(scene)
        projection.boneName = shared.boneNameForProjection(projection)
        handleProjectionTypeOrBoneSuffixChange(projection, context)
        projection.updateBlenderBone = True
        
        # The following selection causes a new bone to be created:
        scene.m3_projection_index = len(scene.m3_projections)-1
        
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for projection in scene.m3_projections:
            usedNames.add(projection.boneSuffix)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 
        
class M3_PROJECTIONS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.projections_remove'
    bl_label       = "Remove M3 Projection"
    bl_description = "Removes the active M3 projection"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_projection_index >= 0:
            projection = scene.m3_projections[scene.m3_projection_index]
            removeBone(scene, projection.boneName)
            scene.m3_projections.remove(scene.m3_projection_index)
            scene.m3_projection_index-= 1
        return{'FINISHED'}
        
        
class M3_WARPS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.warps_add'
    bl_label       = "Add Warp Field"
    bl_description = "Adds a warp field for the export to the m3 model format"

    def invoke(self, context, event):
        scene = context.scene
        warp = scene.m3_warps.add()
        warp.updateBlenderBone = False
        warp.boneSuffix = self.findUnusedName(scene)
        warp.boneName = shared.boneNameForWarp(warp)
        handleWarpBoneSuffixChange(warp, context)
        warp.updateBlenderBone = True
        
        # The following selection causes a new bone to be created:
        scene.m3_warp_index = len(scene.m3_warps)-1
        
        return{'FINISHED'}

    def findUnusedName(self, scene):
        usedNames = set()
        for warp in scene.m3_warps:
            usedNames.add(warp.boneSuffix)
        unusedName = None
        counter = 1
        while unusedName == None:
            suggestedName = "%02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName 
        
class M3_WARPS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.warps_remove'
    bl_label       = "Remove M3 Warp Field"
    bl_description = "Removes the active M3 warp field"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_warp_index >= 0:
            warp = scene.m3_warps[scene.m3_warp_index]
            removeBone(scene, warp.boneName)
            scene.m3_warps.remove(scene.m3_warp_index)
            scene.m3_warp_index-= 1
        return{'FINISHED'}
        

class M3_ATTACHMENT_POINTS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.attachment_points_add'
    bl_label       = "Add Attachment Point"
    bl_description = "Adds an attachment point for the export to Starcraft 2"

    def invoke(self, context, event):
        scene = context.scene
        attachmentPoint = scene.m3_attachment_points.add()
        name = self.findUnusedName(scene)
        attachmentPoint.updateBlenderBone = False
        attachmentPoint.boneSuffix = name
        attachmentPoint.boneName = shared.boneNameForAttachmentPoint(attachmentPoint)
        attachmentPoint.updateBlenderBone = True

        # The following selection causes a new bone to be created:
        scene.m3_attachment_point_index = len(scene.m3_attachment_points)-1
        return{'FINISHED'}
        
    def findUnusedName(self, scene):
        usedNames = set()
        for attachmentPoint in scene.m3_attachment_points:
            usedNames.add(attachmentPoint.boneSuffix)
        suggestedNames = {"Center", "Origin", "Overhead", "Target"}

        unusedName = None
        for suggestedName in suggestedNames:
            if not suggestedName in usedNames:
                unusedName = suggestedName
                break
        counter = 1
        while unusedName == None:
            suggestedName = "Target %02d" % counter
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName


class M3_TIGHT_HIT_TESTS_OT_selectorcreatebone(bpy.types.Operator):
    bl_idname      = 'm3.tight_hit_test_select_or_create_bone'
    bl_label       = "Select or create the HitTestFuzzy bone"
    bl_description = "Adds a shape for the fuzzy hit test"

    def invoke(self, context, event):
        scene = context.scene
        tightHitTest = scene.m3_tight_hit_test
        tightHitTest.boneName = shared.tightHitTestBoneName
        selectOrCreateBoneForShapeObject(scene, tightHitTest)
        return{'FINISHED'}


class M3_TIGHT_HIT_TESTS_OT_hittestremove(bpy.types.Operator):
    bl_idname      = 'm3.tight_hit_test_remove'
    bl_label       = "Select or create the HitTestFuzzy bone"
    bl_description = "Adds a shape for the fuzzy hit test"

    def invoke(self, context, event):
        scene = context.scene
        tightHitTest = scene.m3_tight_hit_test
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')
        removeBone(scene, tightHitTest.boneName)
        tightHitTest.name = ""

        return{'FINISHED'}


class M3_FUZZY_HIT_TESTS_OT_add(bpy.types.Operator):
    bl_idname      = 'm3.fuzzy_hit_tests_add'
    bl_label       = "Add Fuzzy Hit Test Shape"
    bl_description = "Adds a shape for the fuzzy hit test"

    def invoke(self, context, event):
        scene = context.scene
        m3_fuzzy_hit_test = scene.m3_fuzzy_hit_tests.add()
        m3_fuzzy_hit_test.boneName = self.findUnusedBoneName(scene)

        # The following selection causes a new bone to be created:
        scene.m3_fuzzy_hit_test_index = len(scene.m3_fuzzy_hit_tests)-1
        return{'FINISHED'}
        
    def findUnusedBoneName(self, scene):
        usedNames = set()
        for m3_fuzzy_hit_test in scene.m3_fuzzy_hit_tests:
            usedNames.add(m3_fuzzy_hit_test.boneName)
        unusedName = None
        bestName = "HitTestFuzzy"
        if not bestName in usedNames:
            unusedName = bestName
        counter = 1
        while unusedName == None:
            suggestedName = bestName + ("%02d" % counter)
            if not suggestedName in usedNames:
                unusedName = suggestedName
            counter += 1
        return unusedName

class M3_FUZZY_HIT_TESTS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.fuzzy_hit_tests_remove'
    bl_label       = "Remove Fuzzy Hit Test Shape"
    bl_description = "Removes a fuzzy hit test shape"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_fuzzy_hit_test_index >= 0:
            hitTest = scene.m3_fuzzy_hit_tests[scene.m3_fuzzy_hit_test_index]
            removeBone(scene, hitTest.boneName)
            scene.m3_fuzzy_hit_tests.remove(scene.m3_fuzzy_hit_test_index)
            scene.m3_fuzzy_hit_test_index-= 1
        return{'FINISHED'}
        

class M3_ATTACHMENT_POINTS_OT_remove(bpy.types.Operator):
    bl_idname      = 'm3.attachment_points_remove'
    bl_label       = "Remove Attachment Point"
    bl_description = "Removes the active M3 attachment point"
    
    def invoke(self, context, event):
        scene = context.scene
        if scene.m3_attachment_point_index >= 0:
            attackmentPoint = scene.m3_attachment_points[scene.m3_attachment_point_index]
            removeBone(scene, attackmentPoint.boneName)
            scene.m3_attachment_points.remove(scene.m3_attachment_point_index)
            scene.m3_attachment_point_index-= 1
        return{'FINISHED'}
        
class M3_OT_quickExport(bpy.types.Operator):
    bl_idname      = 'm3.quick_export'
    bl_label       = "Quick Export"
    bl_description = "Exports the model to the specified m3 path without asking further questions"
    
    def invoke(self, context, event):
        scene = context.scene
        fileName = scene.m3_export_options.path
        if not "m3export" in locals():
            from . import m3export
        m3export.export(scene, fileName)
        return{'FINISHED'}
        
class M3_OT_quickImport(bpy.types.Operator):
    bl_idname      = 'm3.quick_import'
    bl_label       = "Quick Import"
    bl_description = "Imports the model to the specified m3 path without asking further questions"
    
    def invoke(self, context, event):
        scene = context.scene
        if not "m3import" in locals():
            from . import m3import
        
        m3import.importM3BasedOnM3ImportOptions(scene)
        return{'FINISHED'}
        
class M3_OT_generateBlenderMaterails(bpy.types.Operator):
    bl_idname      = 'm3.generate_blender_materials'
    bl_label       = "M3 -> blender materials"
    bl_description = "Generates blender materials based on the specified m3 materials and imports textures as necessary from the specified path"
    
    def invoke(self, context, event):
        scene = context.scene
        
        shared.createBlenderMaterialsFromM3Materials(scene)
        return{'FINISHED'}

class M3_OT_export(bpy.types.Operator, ExportHelper):
    '''Export a M3 file'''
    bl_idname = "m3.export"
    bl_label = "Export M3 Model"
    bl_options = {'UNDO'}

    filename_ext = ".m3"
    filter_glob = StringProperty(default="*.m3", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="Path of the file that should be created", 
        maxlen= 1024, default= "")

    def execute(self, context):
        print("Export", self.properties.filepath)
        scene = context.scene
        if not "m3export" in locals():
            from . import m3export

        scene.m3_export_options.path = self.properties.filepath
        m3export.export(scene, self.properties.filepath)
        return {'FINISHED'}
            
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class M3_OT_import(bpy.types.Operator, ImportHelper):
    '''Load a M3 file'''
    bl_idname = "m3.import"
    bl_label = "Import M3"
    bl_options = {'UNDO'}

    filename_ext = ".m3"
    filter_glob = StringProperty(default="*.m3;*.m3a", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for importing the simple M3 file", 
        maxlen= 1024, default= "")

    def execute(self, context):
        print("Import", self.properties.filepath)
        scene = context.scene
        if not "m3import" in locals():
            from . import m3import
        scene.m3_import_options.path = self.properties.filepath
        m3import.importM3BasedOnM3ImportOptions(scene)
        return {'FINISHED'}
            
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class M3_OT_conertBlenderToM3NormalMap(bpy.types.Operator):
    '''Convert a blender normal map to a M3 one'''
    bl_idname = "m3.convert_blender_to_m3_normal_map"
    bl_label = "Converts a classic normal map to a normal map usable in the m3 format"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if not hasattr(context, "edit_image"):
            return False
        return context.edit_image is not None
            
    def invoke(self, context, event):
        currentImage = context.edit_image
        values = list(currentImage.pixels)

        def getNewValue(absoluteIndex):
            colorIndex = absoluteIndex % 4
            # Blender: R = (left/right), G = (up/down) , B = (height), A = (unused)
            # M3:      R = (unused)    , G = (down/up?),  B = (unused), A = (left/right)

            if colorIndex == 0: # red color slot:
                # unused
                return 1.0
            elif colorIndex == 1: # green color slot
                #m3.G = blender.G
                return 1.0 -  values[absoluteIndex]
            elif colorIndex == 2: # blue color slot
                # unused ?
                return 0.0
            if colorIndex == 3: # change alpha
                # m3.A = blender.R 
                # to get from index pixelOffset+0 to pixelOffset+3: add 3
                return values[absoluteIndex-3]
            
                
        currentImage.pixels = [getNewValue(i) for i in range(len(values))]
        currentImage.update()
        return{'FINISHED'}
        
class M3_OT_conertM3ToBlenderNormalMap(bpy.types.Operator):
    '''Convert a m3 normal map to a blender one'''
    bl_idname = "m3.convert_m3_to_blender_normal_map"
    bl_label = "Converts a m3 normal map to a classic normal map"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        if not hasattr(context, "edit_image"):
            return False
        return context.edit_image is not None
            
    def invoke(self, context, event):
        currentImage = context.edit_image
        values = list(currentImage.pixels)

        def getNewValue(absoluteIndex):
            colorIndex = absoluteIndex % 4
            # Blender: R = (left/right), G = (up/down) , B = (height), A = (unused)
            # M3:      R = (unused)    , G = (down/up?),  B = (unused), A = (left/right)

            if colorIndex == 0: # red color slot:
                #blender.R = m3.A
                return values[absoluteIndex+3] # old alpha
            elif colorIndex == 1: # green color slot
                #blender.G = 1.0 - m3.G
                return 1.0 -  values[absoluteIndex]
            elif colorIndex == 2: # blue color slot
                newRed = values[absoluteIndex+1] # (newRed = old alpha)
                newGreen = 1.0 - values[absoluteIndex-1] # 1.0 - old green
                leftRight = 2*(newRed -0.5) 
                upDown = 2*(newGreen -0.5) 
                # since sqrt(lowHigh^2 + leftRight^2 + upDown^2) = 1.0 is
                # newBlue = math.sqrt(1.0 - newRed*newRed - newGreen*newGreen)
                return math.sqrt(max(0.0, 1.0 - leftRight*leftRight - upDown*upDown))
            if colorIndex == 3: # change alpha
                # unused
                return 1.0
            
                
        currentImage.pixels = [getNewValue(i) for i in range(len(values))]
        currentImage.update()
        return{'FINISHED'}
        


def menu_func_convertNormalMaps(self, context):
    self.layout.operator(M3_OT_conertBlenderToM3NormalMap.bl_idname, text="Convert Blender to M3 Normal Map")
    self.layout.operator(M3_OT_conertM3ToBlenderNormalMap.bl_idname, text="Convert M3 to Blender Normal Map")


def menu_func_import(self, context):
    self.layout.operator(M3_OT_import.bl_idname, text="Starcraft 2 Model (.m3)...")
    
def menu_func_export(self, context):
    self.layout.operator(M3_OT_export.bl_idname, text="Starcraft 2 Model (.m3)...")
 
def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.m3_animation_index = bpy.props.IntProperty(update=handleAnimationSequenceIndexChange, options=set())
    bpy.types.Scene.m3_animation_old_index = bpy.props.IntProperty(options=set())
    bpy.types.Scene.m3_animations = bpy.props.CollectionProperty(type=M3Animation)
    bpy.types.Scene.m3_material_layer_index = bpy.props.IntProperty(options=set())
    bpy.types.Scene.m3_material_references = bpy.props.CollectionProperty(type=M3Material)
    bpy.types.Scene.m3_standard_materials = bpy.props.CollectionProperty(type=M3StandardMaterial)
    bpy.types.Scene.m3_displacement_materials = bpy.props.CollectionProperty(type=M3DisplacementMaterial)
    bpy.types.Scene.m3_composite_materials = bpy.props.CollectionProperty(type=M3CompositeMaterial)
    bpy.types.Scene.m3_terrain_materials = bpy.props.CollectionProperty(type=M3TerrainMaterial)
    bpy.types.Scene.m3_volume_materials = bpy.props.CollectionProperty(type=M3VolumeMaterial)
    bpy.types.Scene.m3_volume_noise_materials = bpy.props.CollectionProperty(type=M3VolumeNoiseMaterial)
    bpy.types.Scene.m3_creep_materials = bpy.props.CollectionProperty(type=M3CreepMaterial)
    bpy.types.Scene.m3_stb_materials = bpy.props.CollectionProperty(type=M3STBMaterial)
    bpy.types.Scene.m3_lens_flare_materials = bpy.props.CollectionProperty(type=M3LensFlareMaterial)
    bpy.types.Scene.m3_material_reference_index = bpy.props.IntProperty(options=set())
    bpy.types.Scene.m3_cameras = bpy.props.CollectionProperty(type=M3Camera)
    bpy.types.Scene.m3_camera_index = bpy.props.IntProperty(options=set(), update=handleCameraIndexChanged)
    bpy.types.Scene.m3_particle_systems = bpy.props.CollectionProperty(type=M3ParticleSystem)
    bpy.types.Scene.m3_particle_system_index = bpy.props.IntProperty(options=set(), update=handlePartileSystemIndexChanged)
    bpy.types.Scene.m3_ribbons = bpy.props.CollectionProperty(type=M3Ribbon)
    bpy.types.Scene.m3_ribbon_index = bpy.props.IntProperty(options=set(), update=handleRibbonIndexChanged)
    bpy.types.Scene.m3_forces = bpy.props.CollectionProperty(type=M3Force)
    bpy.types.Scene.m3_force_index = bpy.props.IntProperty(options=set(), update=handleForceIndexChanged)
    bpy.types.Scene.m3_rigid_bodies = bpy.props.CollectionProperty(type=M3RigidBody)
    bpy.types.Scene.m3_rigid_body_index = bpy.props.IntProperty(options=set(), update=handleRigidBodyIndexChange)
    bpy.types.Scene.m3_lights = bpy.props.CollectionProperty(type=M3Light)
    bpy.types.Scene.m3_light_index = bpy.props.IntProperty(options=set(), update=handleLightIndexChanged)
    bpy.types.Scene.m3_billboard_behaviors = bpy.props.CollectionProperty(type=M3BillboardBehavior)
    bpy.types.Scene.m3_billboard_behavior_index = bpy.props.IntProperty(options=set(), update=handleBillboardBehaviorIndexChanged)
    bpy.types.Scene.m3_projections = bpy.props.CollectionProperty(type=M3Projection)
    bpy.types.Scene.m3_projection_index = bpy.props.IntProperty(options=set(), update=handleProjectionIndexChanged)
    bpy.types.Scene.m3_warps = bpy.props.CollectionProperty(type=M3Warp)
    bpy.types.Scene.m3_warp_index = bpy.props.IntProperty(options=set(), update=handleWarpIndexChanged)
    bpy.types.Scene.m3_attachment_points = bpy.props.CollectionProperty(type=M3AttachmentPoint)
    bpy.types.Scene.m3_attachment_point_index = bpy.props.IntProperty(options=set(), update=handleAttachmentPointIndexChanged)
    bpy.types.Scene.m3_export_options = bpy.props.PointerProperty(type=M3ExportOptions)
    bpy.types.Scene.m3_import_options = bpy.props.PointerProperty(type=M3ImportOptions)
    bpy.types.Scene.m3_bone_visiblity_options = bpy.props.PointerProperty(type=M3BoneVisiblityOptions)
    bpy.types.Scene.m3_visibility_test = bpy.props.PointerProperty(type=M3Boundings)
    bpy.types.Scene.m3_animation_ids = bpy.props.CollectionProperty(type=M3AnimIdData)
    bpy.types.Scene.m3_fuzzy_hit_tests = bpy.props.CollectionProperty(type=M3SimpleGeometricShape)
    bpy.types.Scene.m3_fuzzy_hit_test_index = bpy.props.IntProperty(options=set(), update=handleFuzzyHitTestIndexChanged)
    bpy.types.Scene.m3_tight_hit_test = bpy.props.PointerProperty(type=M3SimpleGeometricShape)
    bpy.types.Mesh.m3_material_name = bpy.props.StringProperty(options=set())
    bpy.types.Mesh.m3_physics_mesh = bpy.props.BoolProperty(default=False, options=set(), description="Mark mesh to be used for physics shape only (not exported).")
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.IMAGE_MT_image.append(menu_func_convertNormalMaps)
    bpy.types.Bone.m3_bind_scale = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), size=3, options=set()) 
    bpy.types.EditBone.m3_bind_scale = bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), size=3, options=set()) 
    bpy.types.Scene.m3_default_value_action_assignments = bpy.props.CollectionProperty(type=AssignedActionOfM3Animation, options=set())


 
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.IMAGE_MT_image.remove(menu_func_convertNormalMaps)
 
if __name__ == "__main__":
    register()
