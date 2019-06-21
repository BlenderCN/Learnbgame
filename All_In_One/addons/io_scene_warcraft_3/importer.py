
import bpy
import mathutils
from . import constants


def load_warcraft_3_model(model, importProperties):
    bpyObjects = create_mesh_objects(model, importProperties.set_team_color)
    armatureObject = create_armature_object(model, bpyObjects, importProperties.bone_size)
    create_armature_actions(armatureObject, model, importProperties.frame_time)
    create_object_actions(model, bpyObjects, importProperties.frame_time)


def create_mesh_objects(model, setTeamColor):
    preferences = bpy.context.user_preferences.addons['io_scene_warcraft_3'].preferences
    resourceFolder = preferences.resourceFolder
    alternativeResourceFolder = preferences.alternativeResourceFolder
    textureExc = preferences.textureExtension
    if textureExc[0] != '.':
        textureExc = '.' + textureExc
    model.normalize_meshes_names()
    bpyImages = []
    for texture in model.textures:
        if texture.replaceable_id == 1:    # Team Color
            imageFile = constants.TEAM_COLOR_IMAGES[setTeamColor]
        elif texture.replaceable_id == 2:    # Team Glow
            imageFile = constants.TEAM_GLOW_IMAGES[setTeamColor]
        else:
            imageFile = texture.image_file_name
        bpyImage = bpy.data.images.new(imageFile.split('\\')[-1].split('.')[0], 0, 0)
        bpyImage.source = 'FILE'
        imageFileExt = imageFile.split('\\')[-1].split('.')[-1]
        if imageFileExt == 'blp':
            bpyImage.filepath = alternativeResourceFolder + imageFile.split('.')[0] + textureExc
        else:
            bpyImage.filepath = resourceFolder + imageFile
        bpyImages.append(bpyImage)
    bpyMaterials = []
    for material in model.materials:
        bpyImagesOfLayer = []
        for layer in material.layers:
            bpyImagesOfLayer.append(bpyImages[layer.texture_id])
        materialName = bpyImagesOfLayer[-1].filepath.split('\\')[-1].split('.')[0]
        bpyMaterial = bpy.data.materials.new(name=materialName)
        bpyMaterial.use_shadeless = True
        bpyMaterial.use_object_color = True
        bpyMaterial.diffuse_color = (1.0, 1.0, 1.0)
        textureSlotIndex = 0
        for bpyImage in bpyImagesOfLayer:
            bpyMaterial.texture_slots.add()
            bpyTexture = bpy.data.textures.new(name=materialName, type='IMAGE')
            bpyMaterial.texture_slots[textureSlotIndex].texture = bpyTexture
            textureSlotIndex += 1
            bpyTexture.image = bpyImage
        bpyMaterials.append(bpyMaterial)
    bpyObjects = []
    for warCraft3Mesh in model.meshes:
        bpyMesh = bpy.data.meshes.new(warCraft3Mesh.name)
        bpyObject = bpy.data.objects.new(warCraft3Mesh.name, bpyMesh)
        bpy.context.scene.objects.link(bpyObject)
        bpyMesh.from_pydata(warCraft3Mesh.vertices, (), warCraft3Mesh.triangles)
        bpyMesh.uv_textures.new()
        uvLayer = bpyMesh.uv_layers.active.data
        for tris in bpyMesh.polygons:
            for loopIndex in range(tris.loop_start, tris.loop_start + tris.loop_total):
                vertexIndex = bpyMesh.loops[loopIndex].vertex_index
                uvLayer[loopIndex].uv = (warCraft3Mesh.uvs[vertexIndex])
        bpyMaterial = bpyMaterials[warCraft3Mesh.material_id]
        bpyMesh.materials.append(bpyMaterial)
        bpyImage = None
        for textureSlot in bpyMaterial.texture_slots:
            if textureSlot:
                bpyImage = textureSlot.texture.image
        if bpyImage:
            for triangleID in range(len(bpyObject.data.polygons)):
                bpyObject.data.uv_textures[0].data[triangleID].image = bpyImage
        for vertexGroupId in warCraft3Mesh.vertex_groups_ids:
            bpyObject.vertex_groups.new(str(vertexGroupId))
        for vertexIndex, vertexGroupIds in enumerate(warCraft3Mesh.vertex_groups):
            for vertexGroupId in vertexGroupIds:
                bpyObject.vertex_groups[str(vertexGroupId)].add([vertexIndex, ], 1.0, 'REPLACE')
        bpyObjects.append(bpyObject)
    return bpyObjects


def create_armature_object(model, bpyObjects, boneSize):
    nodes = model.nodes
    pivotPoints = model.pivot_points
    bpyArmature = bpy.data.armatures.new(model.name + ' Nodes')
    bpyArmature.draw_type = 'STICK'
    bpyObject = bpy.data.objects.new(model.name + ' Nodes', bpyArmature)
    bpyObject.show_x_ray = True
    bpy.context.scene.objects.link(bpyObject)
    bpy.context.scene.objects.active = bpyObject
    bpy.ops.object.mode_set(mode='EDIT')
    nodeTypes = set()
    boneTypes = {}
    for indexNode, node in enumerate(nodes):
        nodePosition = pivotPoints[indexNode]
        boneName = node.node.name
        nodeTypes.add(node.type)
        bone = bpyArmature.edit_bones.new(boneName)
        bone.head = nodePosition
        bone.tail = nodePosition
        bone.tail[1] += boneSize
        boneTypes[boneName] = node.type
    nodeTypes = list(nodeTypes)
    nodeTypes.sort()
    for indexNode, node in enumerate(nodes):
        bone = bpyObject.data.edit_bones[indexNode]
        if node.node.parent:
            parent = bpyObject.data.edit_bones[node.node.parent]
            bone.parent = parent
    for mesh in bpyObjects:
        mesh.modifiers.new(name='Armature', type='ARMATURE')
        mesh.modifiers['Armature'].object = bpyObject
        for vertexGroup in mesh.vertex_groups:
            vertexGroupIndex = int(vertexGroup.name)
            boneName = bpyObject.data.edit_bones[vertexGroupIndex].name
            vertexGroup.name = boneName
    bpy.ops.object.mode_set(mode='POSE')
    boneGroups = {}
    for nodeType in nodeTypes:
        bpy.ops.pose.group_add()
        boneGroup = bpyObject.pose.bone_groups.active
        boneGroup.name = nodeType + 's'
        boneGroups[nodeType] = boneGroup
        if nodeType == 'bone':
            boneGroup.color_set = 'THEME04'
        elif nodeType == 'attachment':
            boneGroup.color_set = 'THEME09'
        elif nodeType == 'collision_shape':
            boneGroup.color_set = 'THEME02'
        elif nodeType == 'event':
            boneGroup.color_set = 'THEME03'
        elif nodeType == 'helper':
            boneGroup.color_set = 'THEME01'
    for bone in bpyObject.pose.bones:
        bone.rotation_mode = 'XYZ'
        bone.bone_group = boneGroups[boneTypes[bone.name]]
    for bone in bpyObject.data.bones:
        bone.warcraft_3.nodeType = boneTypes[bone.name].upper()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = None
    return bpyObject


def add_sequence_to_armature(sequenceName, armatureObject):
    warcraft3data = armatureObject.data.warcraft_3
    sequence = warcraft3data.sequencesList.add()
    sequence.name = sequenceName


def create_armature_actions(armatureObject, model, frameTime):
    nodes = model.nodes
    sequences = model.sequences
    action = bpy.data.actions.new(name='#UNANIMATED')
    add_sequence_to_armature('#UNANIMATED', armatureObject)
    for node in nodes:
        boneName = node.node.name
        dataPath = 'pose.bones["' + boneName + '"]'
        locationFcurveX = action.fcurves.new(dataPath + '.location', 0, boneName)
        locationFcurveY = action.fcurves.new(dataPath + '.location', 1, boneName)
        locationFcurveZ = action.fcurves.new(dataPath + '.location', 2, boneName)
        locationFcurveX.keyframe_points.insert(0.0, 0.0)
        locationFcurveY.keyframe_points.insert(0.0, 0.0)
        locationFcurveZ.keyframe_points.insert(0.0, 0.0)
        rotationFcurveX = action.fcurves.new(dataPath + '.rotation_euler', 0, boneName)
        rotationFcurveY = action.fcurves.new(dataPath + '.rotation_euler', 1, boneName)
        rotationFcurveZ = action.fcurves.new(dataPath + '.rotation_euler', 2, boneName)
        rotationFcurveX.keyframe_points.insert(0.0, 0.0)
        rotationFcurveY.keyframe_points.insert(0.0, 0.0)
        rotationFcurveZ.keyframe_points.insert(0.0, 0.0)
        scaleFcurveX = action.fcurves.new(dataPath + '.scale', 0, boneName)
        scaleFcurveY = action.fcurves.new(dataPath + '.scale', 1, boneName)
        scaleFcurveZ = action.fcurves.new(dataPath + '.scale', 2, boneName)
        scaleFcurveX.keyframe_points.insert(0.0, 1.0)
        scaleFcurveY.keyframe_points.insert(0.0, 1.0)
        scaleFcurveZ.keyframe_points.insert(0.0, 1.0)
    for sequence in sequences:
        intervalStart = sequence.interval_start
        intervalEnd = sequence.interval_end
        action = bpy.data.actions.new(name=sequence.name)
        add_sequence_to_armature(sequence.name, armatureObject)
        for node in nodes:
            boneName = node.node.name
            dataPath = 'pose.bones["' + boneName + '"]'
            translations = node.node.translations
            rotations = node.node.rotations
            scalings = node.node.scalings
            if translations:
                locationFcurveX = None
                locationFcurveY = None
                locationFcurveZ = None
                interpolationType = constants.INTERPOLATION_TYPE_NAMES[translations.interpolation_type]
                for index in range(translations.tracks_count):
                    time = translations.times[index]
                    translation = translations.values[index]
                    if intervalStart <= time and time <= intervalEnd:
                        if not locationFcurveX:
                            locationFcurveX = action.fcurves.new(dataPath + '.location', 0, boneName)
                        if not locationFcurveY:
                            locationFcurveY = action.fcurves.new(dataPath + '.location', 1, boneName)
                        if not locationFcurveZ:
                            locationFcurveZ = action.fcurves.new(dataPath + '.location', 2, boneName)
                        realTime = round((time - intervalStart) / frameTime, 0)
                        locationXKeyframe = locationFcurveX.keyframe_points.insert(realTime, translation[0])
                        locationYKeyframe = locationFcurveY.keyframe_points.insert(realTime, translation[1])
                        locationZKeyframe = locationFcurveZ.keyframe_points.insert(realTime, translation[2])
                        locationXKeyframe.interpolation = interpolationType
                        locationYKeyframe.interpolation = interpolationType
                        locationZKeyframe.interpolation = interpolationType
                if not locationFcurveX:
                    locationFcurveX = action.fcurves.new(dataPath + '.location', 0, boneName)
                    locationFcurveX.keyframe_points.insert(0.0, 0.0)
                if not locationFcurveY:
                    locationFcurveY = action.fcurves.new(dataPath + '.location', 1, boneName)
                    locationFcurveY.keyframe_points.insert(0.0, 0.0)
                if not locationFcurveZ:
                    locationFcurveZ = action.fcurves.new(dataPath + '.location', 2, boneName)
                    locationFcurveZ.keyframe_points.insert(0.0, 0.0)
            if rotations:
                rotationFcurveX = None
                rotationFcurveY = None
                rotationFcurveZ = None
                interpolationType = constants.INTERPOLATION_TYPE_NAMES[rotations.interpolation_type]
                for index in range(rotations.tracks_count):
                    time = rotations.times[index]
                    rotation = rotations.values[index]
                    if intervalStart <= time and time <= intervalEnd:
                        if not rotationFcurveX:
                            rotationFcurveX = action.fcurves.new(dataPath + '.rotation_euler', 0, boneName)
                        if not rotationFcurveY:
                            rotationFcurveY = action.fcurves.new(dataPath + '.rotation_euler', 1, boneName)
                        if not rotationFcurveZ:
                            rotationFcurveZ = action.fcurves.new(dataPath + '.rotation_euler', 2, boneName)
                        realTime = round((time - intervalStart) / frameTime, 0)
                        euler = mathutils.Quaternion(mathutils.Vector(rotation)).to_euler('XYZ')
                        rotationXKeyframe = rotationFcurveX.keyframe_points.insert(realTime, euler[0])
                        rotationYKeyframe = rotationFcurveY.keyframe_points.insert(realTime, euler[1])
                        rotationZKeyframe = rotationFcurveZ.keyframe_points.insert(realTime, euler[2])
                        rotationXKeyframe.interpolation = interpolationType
                        rotationYKeyframe.interpolation = interpolationType
                        rotationZKeyframe.interpolation = interpolationType
                if not rotationFcurveX:
                    rotationFcurveX = action.fcurves.new(dataPath + '.rotation_euler', 0, boneName)
                    rotationFcurveX.keyframe_points.insert(0.0, 0.0)
                if not rotationFcurveY:
                    rotationFcurveY = action.fcurves.new(dataPath + '.rotation_euler', 1, boneName)
                    rotationFcurveY.keyframe_points.insert(0.0, 0.0)
                if not rotationFcurveZ:
                    rotationFcurveZ = action.fcurves.new(dataPath + '.rotation_euler', 2, boneName)
                    rotationFcurveZ.keyframe_points.insert(0.0, 0.0)
            if scalings:
                scaleFcurveX = None
                scaleFcurveY = None
                scaleFcurveZ = None
                interpolationType = constants.INTERPOLATION_TYPE_NAMES[scalings.interpolation_type]
                for index in range(scalings.tracks_count):
                    time = scalings.times[index]
                    scale = scalings.values[index]
                    if intervalStart <= time and time <= intervalEnd:
                        if not scaleFcurveX:
                            scaleFcurveX = action.fcurves.new(dataPath + '.scale', 0, boneName)
                        if not scaleFcurveY:
                            scaleFcurveY = action.fcurves.new(dataPath + '.scale', 1, boneName)
                        if not scaleFcurveZ:
                            scaleFcurveZ = action.fcurves.new(dataPath + '.scale', 2, boneName)
                        realTime = round((time - intervalStart) / frameTime, 0)
                        scaleXKeyframe = scaleFcurveX.keyframe_points.insert(realTime, scale[0])
                        scaleYKeyframe = scaleFcurveY.keyframe_points.insert(realTime, scale[1])
                        scaleZKeyframe = scaleFcurveZ.keyframe_points.insert(realTime, scale[2])
                        scaleXKeyframe.interpolation = interpolationType
                        scaleYKeyframe.interpolation = interpolationType
                        scaleZKeyframe.interpolation = interpolationType
                if not scaleFcurveX:
                    scaleFcurveX = action.fcurves.new(dataPath + '.scale', 0, boneName)
                    scaleFcurveX.keyframe_points.insert(0.0, 1.0)
                if not scaleFcurveY:
                    scaleFcurveY = action.fcurves.new(dataPath + '.scale', 1, boneName)
                    scaleFcurveY.keyframe_points.insert(0.0, 1.0)
                if not scaleFcurveZ:
                    scaleFcurveZ = action.fcurves.new(dataPath + '.scale', 2, boneName)
                    scaleFcurveZ.keyframe_points.insert(0.0, 1.0)


def create_object_actions(model, bpyObjects, frameTime):
    geosetAnimations = model.geoset_animations
    sequences = model.sequences
    dataPathColor = 'color'
    for geosetAnimation in geosetAnimations:
        geosetId = geosetAnimation.geoset_id
        action = bpy.data.actions.new(name='#UNANIMATED' + ' ' + bpyObjects[geosetId].name)
        colorR = action.fcurves.new(dataPathColor, 0)
        colorG = action.fcurves.new(dataPathColor, 1)
        colorB = action.fcurves.new(dataPathColor, 2)
        colorA = action.fcurves.new(dataPathColor, 3)
        colorR.keyframe_points.insert(0.0, 1.0)
        colorG.keyframe_points.insert(0.0, 1.0)
        colorB.keyframe_points.insert(0.0, 1.0)
        colorA.keyframe_points.insert(0.0, 1.0)
    for sequence in sequences:
        intervalStart = sequence.interval_start
        intervalEnd = sequence.interval_end
        for geosetAnimation in geosetAnimations:
            geosetId = geosetAnimation.geoset_id
            colorAnim = geosetAnimation.animation_color
            alphaAnim = geosetAnimation.animation_alpha
            action = bpy.data.actions.new(name=sequence.name + ' ' + bpyObjects[geosetId].name)
            colorR = None
            colorG = None
            colorB = None
            colorA = None
            interpolationType = constants.INTERPOLATION_TYPE_NAMES[colorAnim.interpolation_type]
            for index in range(colorAnim.tracks_count):
                time = colorAnim.times[index]
                color = colorAnim.values[index]
                if intervalStart <= time and time <= intervalEnd or time == 0:
                    if not colorR:
                        colorR = action.fcurves.new(dataPathColor, 0)
                    if not colorG:
                        colorG = action.fcurves.new(dataPathColor, 1)
                    if not colorB:
                        colorB = action.fcurves.new(dataPathColor, 2)
                    if time == 0:
                        realTime = 0.0
                    else:
                        realTime = round((time - intervalStart) / frameTime, 0)
                    colorRKeyframe = colorR.keyframe_points.insert(realTime, color[0])
                    colorGKeyframe = colorG.keyframe_points.insert(realTime, color[1])
                    colorBKeyframe = colorB.keyframe_points.insert(realTime, color[2])
                    colorRKeyframe.interpolation = interpolationType
                    colorGKeyframe.interpolation = interpolationType
                    colorBKeyframe.interpolation = interpolationType
            if not colorR:
                colorR = action.fcurves.new(dataPathColor, 0)
                colorR.keyframe_points.insert(0, 1.0)
            if not colorG:
                colorG = action.fcurves.new(dataPathColor, 1)
                colorG.keyframe_points.insert(0, 1.0)
            if not colorB:
                colorB = action.fcurves.new(dataPathColor, 2)
                colorB.keyframe_points.insert(0, 1.0)
            interpolationType = constants.INTERPOLATION_TYPE_NAMES[alphaAnim.interpolation_type]
            for index in range(alphaAnim.tracks_count):
                time = alphaAnim.times[index]
                alpha = alphaAnim.values[index]
                if intervalStart <= time and time <= intervalEnd or time == 0:
                    if not colorA:
                        colorA = action.fcurves.new(dataPathColor, 3)
                    if time == 0:
                        realTime = 0.0
                    else:
                        realTime = round((time - intervalStart) / frameTime, 0)
                    colorAKeyframe = colorA.keyframe_points.insert(realTime, alpha)
                    colorAKeyframe.interpolation = interpolationType
            if not colorA:
                colorA = action.fcurves.new(dataPathColor, 3)
                colorA.keyframe_points.insert(0, 1.0)
