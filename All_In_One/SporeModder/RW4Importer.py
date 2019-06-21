__author__ = 'Eric'

from sporemodder.RW4Base import *
from sporemodder.materials import RWMaterialBuilder
from sporemodder import RWMaterialConfig
import sporemodder.materials.DirectXEnums
from bpy_extras.io_utils import unpack_list, unpack_face_list
from mathutils import Matrix, Quaternion, Vector
import math
import bpy


def vec_roll_to_mat3(vec, roll):
    target = Vector((0, 0.1, 0))
    nor = vec.normalized()
    axis = target.cross(nor)
    if axis.dot(axis) > 0.0000000001:  # this seems to be the problem for some bones, no idea how to fix
        axis.normalize()
        theta = target.angle(nor)
        bMatrix = Matrix.Rotation(theta, 3, axis)
    else:
        updown = 1 if target.dot(nor) > 0 else -1
        bMatrix = Matrix.Scale(updown, 3)

        # C code:
        # bMatrix[0][0]=updown; bMatrix[1][0]=0.0;    bMatrix[2][0]=0.0;
        # bMatrix[0][1]=0.0;    bMatrix[1][1]=updown; bMatrix[2][1]=0.0;
        # bMatrix[0][2]=0.0;    bMatrix[1][2]=0.0;    bMatrix[2][2]=1.0;
        bMatrix[2][2] = 1.0

    rMatrix = Matrix.Rotation(roll, 3, nor)
    mat = rMatrix * bMatrix
    return mat


def mat3_to_vec_roll(mat):
    vec = mat.col[1]
    vecmat = vec_roll_to_mat3(mat.col[1], 0)
    vecmatinv = vecmat.inverted()
    rollmat = vecmatinv * mat
    roll = math.atan2(rollmat[0][2], rollmat[2][2])
    return vec, roll


class RW4ImporterSettings:
    def __init__(self):
        self.importMaterials = True
        self.importSkeleton = True
        self.importMovements = True


class RW4Importer:
    class BoneInfo:
        def __init__(self):
            self.abs_bind_pose = None
            self.inv_pose_translation = None
            self.inv_bind_pose = None
            self.pose_translation = None

    def __init__(self, renderWare, fileReader, settings):
        # for blender objects, we use the prefix b
        self.renderWare = renderWare
        self.fileReader = fileReader
        self.settings = settings

        self.meshesDict = {}  # vertexBuffer -> bObject
        self.bMeshObjects = []
        self.bMeshes = []

        self.bArmature = None
        self.bArmatureObject = None
        self.skinsInK = None

        self.bAnimationActions = []
        self.bonesInfo = []

    def process(self):
        self.processSkeleton()
        self.processMeshes()
        self.processAnimations()

    def processMeshes(self):
        meshLinks = self.renderWare.getObjects(MeshCompiledStateLink.type_code)

        materialIndex = 0

        for meshLink in meshLinks:
            vertexBuffer = meshLink.mesh.vertexBuffers[0]

            bObject = self.meshesDict.get(vertexBuffer)

            if bObject is None:
                objectName = "Model-%d" % (self.renderWare.getIndex(vertexBuffer))
                bMesh = bpy.data.meshes.new(objectName)
                bObject = bpy.data.objects.new(objectName, bMesh)
                bpy.context.scene.objects.link(bObject)

                self.bMeshes.append(bMesh)
                self.bMeshObjects.append(bObject)

                self.meshesDict[vertexBuffer] = bObject
                isNewMesh = True
            else:
                bMesh = bObject.data
                isNewMesh = False

            # add all vertices and triangles (only if we haven't added them before)

            if isNewMesh:
                vertices = meshLink.mesh.vertexBuffers[0].processData(self.fileReader)
                indices = meshLink.mesh.indexBuffer.processData(self.fileReader)

                if meshLink.mesh.indexBuffer.primitiveType != DirectXEnums.D3DPRIMITIVETYPE.D3DPT_TRIANGLELIST:
                    raise NameError("Unsupported primitive type: %d" % meshLink.mesh.indexBuffer.primitiveType)

                bMesh.vertices.add(meshLink.mesh.vertexBuffers[0].vertexCount)
                for i in range(meshLink.mesh.vertexBuffers[0].vertexCount):
                    pos = vertices.pos[i]
                    bMesh.vertices[i].co = (pos[0], pos[1], pos[2])

                triangleCount = meshLink.mesh.indexBuffer.primitiveCount // 3

                bMesh.tessfaces.add(triangleCount)

                for i in range(triangleCount):
                    for j in range(3):
                        bMesh.tessfaces[i].vertices_raw[j] = indices[i * 3 + j]
                        
                if vertices.uvs is not None:
                    uvtex = bMesh.tessface_uv_textures.new()
                    uvtex.name = 'DefaultUV'
        
                    for i, face in enumerate(bMesh.tessfaces):
                        uvtex.data[i].uv1 = (vertices.uvs[face.vertices_raw[0]][0], -vertices.uvs[face.vertices_raw[0]][1])
                        uvtex.data[i].uv2 = (vertices.uvs[face.vertices_raw[1]][0], -vertices.uvs[face.vertices_raw[1]][1])
                        uvtex.data[i].uv3 = (vertices.uvs[face.vertices_raw[2]][0], -vertices.uvs[face.vertices_raw[2]][1])
                        uvtex.data[i].uv4 = [0, 0]

                # configure skeleton if any
                if self.bArmature is not None:
                    for bBone in self.bArmature.bones:
                        bObject.vertex_groups.new(bBone.name)

                    for v in range(meshLink.mesh.vertexBuffers[0].vertexCount):
                        for i in range(4):
                            if vertices.boneWeights[v][i] != 0:
                                bObject.vertex_groups[vertices.boneIndices[v][i] // 3].add(
                                    [v], vertices.boneWeights[v][i], 'REPLACE')

                    bModifier = bObject.modifiers.new("Skeleton: " + self.bArmature.name, 'ARMATURE')
                    bModifier.object = self.bArmatureObject
                    bModifier.use_vertex_groups = True

            # Configure material for the mesh
            bMat = bpy.data.materials.new("Mesh-%d" % (self.renderWare.getIndex(meshLink)))
            bMesh.materials.append(bMat)

            if self.settings.importMaterials and len(meshLink.compiledStates) > 0:
                material_builder = RWMaterialBuilder.RWMaterialBuilder()
                material_builder.from_compiled_state(ArrayFileReader(meshLink.compiledStates[0].data))

                RWMaterialConfig.parse_material_builder(material_builder, bMat.renderWare4)

            for i in range(meshLink.mesh.firstIndex // 3, meshLink.mesh.firstIndex // 3 + meshLink.mesh.triangleCount):
                bMesh.tessfaces[i].material_index = materialIndex

            materialIndex += 1

        for bMesh in self.bMeshes:
            bMesh.update()

    def processSkeleton(self):

        if not self.settings.importSkeleton:
            return

        skinsInKs = self.renderWare.getObjects(SkinsInK.type_code)
        if len(skinsInKs) > 0:
            self.skinsInK = skinsInKs[0]

            self.bArmature = bpy.data.armatures.new(getString(self.skinsInK.skeleton.skeletonID))
            self.bArmatureObject = bpy.data.objects.new(self.bArmature.name, self.bArmature)

            bpy.context.scene.objects.link(self.bArmatureObject)
            bpy.context.scene.objects.active = self.bArmatureObject

            boneLength = 0.1

            bound_box = self.renderWare.getObjects(BBox.type_code)
            if len(bound_box) > 0:
                boneLength *= (bound_box[0].bound_box[1][1] - bound_box[0].bound_box[0][1])

            bpy.ops.object.mode_set(mode='EDIT')

            for i, bone in enumerate(self.skinsInK.skeleton.bones):

                name = getString(bone.name)
                bBone = self.bArmature.edit_bones.new(name)
                bBone.use_local_location = True

                bonePose = self.skinsInK.animationSkin.data[i]

                matrix = Matrix(bonePose.absBindPose.data)
                invBindPose = matrix.inverted().to_4x4()
                invBindPose[0][3] = bonePose.invPoseTranslation[0]
                invBindPose[1][3] = bonePose.invPoseTranslation[1]
                invBindPose[2][3] = bonePose.invPoseTranslation[2]

                absBindPose = invBindPose.inverted()
                head = absBindPose.to_translation()

                axis, roll = mat3_to_vec_roll(invBindPose.to_3x3())

                # we might not need to use rotations at all, so this is better
                axis = Vector((0, 1, 0))

                bBone.head = head
                bBone.tail = axis*boneLength + bBone.head
                bBone.roll = roll

                if bone.parent is not None:
                    bBone.parent = self.bArmature.edit_bones[self.skinsInK.skeleton.bones.index(bone.parent)]

                    # if bone.flags == 1:
                    #     bBone.parent.tail = bBone.head
                    #     bBone.use_connect = True

            bpy.ops.object.mode_set(mode='OBJECT')

    def setBoneInfo(self):
        if self.skinsInK is not None and self.skinsInK.animationSkin is not None:
            baseRot = Matrix.Identity(3)

            for i, bonePose in enumerate(self.skinsInK.animationSkin.data):

                boneInfo = RW4Importer.BoneInfo()
                
                boneInfo.abs_bind_pose = Matrix(bonePose.absBindPose.data)
                boneInfo.inv_bind_pose = (boneInfo.abs_bind_pose.inverted() * baseRot).to_quaternion()
                
                boneInfo.inv_pose_translation = Vector((bonePose.invPoseTranslation))
                
                self.bonesInfo.append(boneInfo)

                if self.skinsInK.skeleton.bones[i].flags == 0:
                    baseRot = boneInfo.abs_bind_pose

    def importAnimationRotation(self, bPoseBone, bAction, bActionGroup, channel, index):
        data_path = bPoseBone.path_from_id('rotation_quaternion')
        qr_w = bAction.fcurves.new(data_path, index=0)
        qr_x = bAction.fcurves.new(data_path, index=1)
        qr_y = bAction.fcurves.new(data_path, index=2)
        qr_z = bAction.fcurves.new(data_path, index=3)
        
        qr_w.group = bActionGroup
        qr_x.group = bActionGroup
        qr_y.group = bActionGroup
        qr_z.group = bActionGroup

        for kf in channel.keyframes:
            qr = Quaternion((kf.rot[3], kf.rot[0], kf.rot[1], kf.rot[2])) * self.bonesInfo[index].inv_bind_pose

            if bPoseBone.parent is not None:
                parent_qr = bPoseBone.parent.rotation_quaternion
                qr = qr * parent_qr.inverted()

            qr_w.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, qr[0])
            qr_x.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, qr[1])
            qr_y.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, qr[2])
            qr_z.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, qr[3])
            
    def importAnimationLocation(self, bPoseBone, bAction, bActionGroup, channel, index):
        data_path = bPoseBone.path_from_id('location')
        vt_x = bAction.fcurves.new(data_path, index=0)
        vt_y = bAction.fcurves.new(data_path, index=1)
        vt_z = bAction.fcurves.new(data_path, index=2)
        
        vt_x.group = bActionGroup
        vt_y.group = bActionGroup
        vt_z.group = bActionGroup

        for kf in channel.keyframes:
            vt = Vector((vt_x, vt_y, vt_z))
            
            if bPoseBone.parent is not None:
                vt = vt + self.bonesInfo[index].inv_pose_translation
                
            
            qr = Quaternion((kf.rot[3], kf.rot[0], kf.rot[1], kf.rot[2])) * self.bonesInfo[index].invBindPose

            if bPoseBone.parent is not None:
                parent_qr = bPoseBone.parent.rotation_quaternion
                qr = qr * parent_qr.inverted()

            vt_x.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, vt[0])
            vt_y.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, vt[1])
            vt_z.keyframe_points.insert(kf.time*KeyframeAnim.frames_per_second, vt[2])

    def getBoneIndex(self, name):
        if self.skinsInK is not None and self.skinsInK.skeleton is not None:
            for i in range(len(self.skinsInK.skeleton.bones)):
                if self.skinsInK.skeleton.bones[i].name == name:
                    return i
        return -1
    
    def processAnimation(self, animation, animID):
        """ Imports an animation and returns the Blender Action"""
        
        bAction = bpy.data.actions.new(getString(animID))
        self.bAnimationActions.append(bAction)

        self.bArmatureObject.animation_data.action = bAction

        for c, channel in enumerate(animation.channels):
            boneIndex = self.getBoneIndex(channel.channelID)
            
            bPoseBone = self.bArmatureObject.pose.bones[boneIndex]
            
            bActionGroup = bAction.groups.new(bPoseBone.name)

            if channel.keyframeClass == KeyframeAnim.Channel.LocRotScale or channel.keyframeClass == KeyframeAnim.Channel.LocRot:
                self.importAnimationRotation(
                    bPoseBone=bPoseBone,
                    bAction=bAction,
                    bActionGroup=bActionGroup,
                    channel=channel,
                    index=boneIndex
                    )
                
        return bAction

    def processAnimations(self):
        if not self.settings.importMovements:
            return
        if self.bArmatureObject is None:
            return

        animObjects = self.renderWare.getObjects(Animations.type_code)
        
        # Animations

        if len(animObjects) > 0:

            self.setBoneInfo()

            animations = animObjects[0].animations

            bpy.ops.object.mode_set(mode='POSE')
            self.bArmatureObject.animation_data_create()

            for animID in animations.keys():

                animation = animations[animID]

                self.processAnimation(animation, animID)

            bpy.ops.object.mode_set(mode='OBJECT')
            
        # Morph handles
        
        handleObjects = self.renderWare.getObjects(MorphHandle.type_code)
        
        if len(handleObjects) > 0:
            bpy.ops.object.mode_set(mode='POSE')
            
            # Check if we have created the animation data yet
            if len(animObjects) == 0:
                self.bArmatureObject.animation_data_create()
                self.setBoneInfo()
                
            for handle in handleObjects:
                bAction = self.processAnimation(handle.animation, handle.handleID)
                
                bAction.rw4.is_morph_handle = True
            
            bpy.ops.object.mode_set(mode='OBJECT')


def importRW4(file, settings):
    fileReader = FileReader(file)

    renderWare = RenderWare4()

    renderWare.read(fileReader)

    importer = RW4Importer(renderWare, fileReader, settings)
    importer.process()

    return {'FINISHED'}


if __name__ == "__main__":
    debugFile = open("C:\\Users\\Eric\\Desktop\\be_classic_01.rw4", "br")

    try:
        importRW4(debugFile, RW4ImporterSettings())
    finally:
        debugFile.close()