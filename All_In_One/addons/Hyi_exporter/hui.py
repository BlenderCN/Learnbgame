
from .node_geometry import NodeGeometry
from .node_mesh import NodeMesh
from .node_skeleton import NodeSkeleton
from .node_animation_clip import NodeAnimationClip
from .keyframe_track import KeyframeTrack

class Hui:
    def __init__(self, operator):
        self.operator = operator
        self.huiNodes = []
        self.data = {}
    def log(self, s):
        self.operator.report({'INFO'}, str(s))

    def getBlenderData(self, data):
        skeletonNodes = {}
        self.data = data
        for mesh in data.meshes:
            nodeMesh = NodeMesh()
            nodeGeometry = NodeGeometry(len(self.huiNodes))
            for vert in mesh.vertices:
                nodeGeometry.pushVertex(vert.undeformed_co[0], vert.undeformed_co[1], vert.undeformed_co[2])
            mesh.calc_loop_triangles()
            for loopTriangle in mesh.loop_triangles:
                nodeGeometry.pushFace(loopTriangle.vertices[0], loopTriangle.vertices[1], loopTriangle.vertices[2])
            self.huiNodes.append(nodeGeometry)
            nodeMesh.setGeometryId(nodeGeometry.id)
            #skeleton
            object = self.findObjectOf(mesh)
            if object and object.parent and hasattr(object.parent.data,"bones"):
                skeletonName = object.parent.data.name
                if skeletonName in skeletonNodes:
                    skeleton = skeletonNodes[skeletonName]
                else:
                    skeleton = NodeSkeleton(len(self.huiNodes))
                    self.huiNodes.append(skeleton)
                    skeletonNodes[skeletonName] = skeleton
                    skeleton.loadArmature(object.parent.data)
                nodeMesh.setSkeletonId(skeleton.id)
                self.setupSkinning(mesh, skeleton, nodeGeometry)
            self.huiNodes.append(nodeMesh)
        self.setupAnimations()
            #parse geometry
        self.operator.report({'INFO'}, "getBlenderData:")

    def writeDataToFile(self, fileName):
        f = open(fileName, 'wb')
        for node in self.huiNodes:
            f.write(node.serialize())
        f.close()
        self.operator.report({'INFO'}, "writeDataToFile:" + fileName)

    def findObjectOf(self, entity):
        for object in self.data.objects:
            if object.data.name == entity.name:
                return object
        return False

    def setupSkinning(self, mesh, skeletonNode, geometryNode):
        vertex_groups = self.findObjectOf(mesh).vertex_groups
        if len(vertex_groups) == 0:
            return
        for vertex in mesh.vertices:
            weights = []
            boneIds = []
            for group in vertex.groups:
                weights.append(group.weight)
                groupNumber = group.group
                groupName =  vertex_groups[groupNumber].name
                boneNumber = skeletonNode.getBoneNumber(groupName)
                if boneNumber < 0:
                    self.operator.report({'ERROR'}, "Can not find a bone:" + groupName)
                    boneNumber = 255
                boneIds.append(boneNumber)
            for i in range(len(weights), 4):
                weights.append(0)
                boneIds.append(0)
            sortedZip = sorted(zip(weights,boneIds),reverse=True)
            geometryNode.pushSkinIndices(sortedZip[0][1], sortedZip[1][1], sortedZip[2][1], sortedZip[3][1])
            geometryNode.pushSkinWeights(sortedZip[0][0], sortedZip[1][0], sortedZip[2][0], sortedZip[3][0])

    def setupAnimations(self):
        #this method works only with skeleton
        boneMatrices = {}
        skeleton = False
        for o in self.data.objects:
            if hasattr(o.data,"bones"):
                skeleton = o
                break
        if not skeleton:
            return
        for bone in skeleton.pose.bones:
            boneMatrices[bone.name] = [row[:] for row in bone.matrix]
        frameDuration = 1.0 / self.data.scenes[0].render.fps
        helpSkeletonNode = NodeSkeleton(0)
        helpSkeletonNode.loadArmature(skeleton.data)
        for action in self.data.actions:
            skeleton.animation_data.action = action
            #find bones and track Types
            boneTracks = []
            keyFrameTracks = []
            for fc in action.fcurves:
                boneName, trackType = parseFcDataPath(fc.data_path)
                if boneName is None:
                    continue
                if not (boneName, trackType) in boneTracks:
                    boneTracks.append((boneName, trackType))
                    boneNumber = helpSkeletonNode.getBoneNumber(boneName)
                    keyFrameTracks.append (KeyframeTrack(boneNumber, trackType, boneName, boneMatrices[boneName]))

            startFrame, endFrame = action.frame_range
            for frame in range(int(startFrame), int(endFrame) + 1):
                frameTimePoint = (frame-startFrame) * frameDuration
                self.data.scenes[0].frame_set(frame)
                for track in keyFrameTracks:
                    track.parseKeyframeData(frameTimePoint, skeleton.pose)
            animClipNode = NodeAnimationClip(action.name)
            for track in keyFrameTracks:
                animClipNode.addTrack(track)
            self.huiNodes.append(animClipNode)


def parseFcDataPath(path):
    isBone = path.find('.bones["')
    boneNameEnd =  path.find('"].')
    if isBone and boneNameEnd>0:
        boneName = path[12:boneNameEnd]
        type =  path[boneNameEnd+3:]
        return (boneName, type)
    return (None, None)
