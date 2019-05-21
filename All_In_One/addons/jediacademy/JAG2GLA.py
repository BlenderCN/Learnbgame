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

if 'JAStringhelper' in locals():
    imp.reload( JAStringhelper )
else:
    from . import JAStringhelper
if 'JAG2Constants' in locals():
    imp.reload( JAG2Constants )
else:
    from . import JAG2Constants
if 'JAG2Math' in locals():
    imp.reload( JAG2Math )
else:
    from . import JAG2Math
if 'MrwProfiler' in locals():
    imp.reload( MrwProfiler )
else:
    from . import MrwProfiler

import struct, bpy, mathutils

PROFILE = False
PROGRESS_UPDATE_INTERVAL = 30 # show progress & remaining time every 30 seconds.

def readString(file):
    return JAStringhelper.decode(struct.unpack("64s", file.read(JAG2Constants.MAX_QPATH))[0])

class MdxaHeader:
    
    def __init__(self):
        self.name = ""
        self.scale = 1 # does not seem to be used by Jedi Academy anyway - or is it? I need it in import!
        self.numFrames = -1
        self.ofsFrames = -1
        self.numBones = -1
        self.ofsCompBonePool = -1
        self.ofsSkel = -1 # this is also MdxaSkelOffsets.baseOffset + MdxaSkelOffsets.boneOffsets[0] - probably a historic leftover
        self.ofsEnd = -1
    
    def loadFromFile(self, file):
        # check ident
        ident, = struct.unpack("4s", file.read(4))
        if ident != JAG2Constants.GLA_IDENT:
            print("File does not start with ", JAG2Constants.GLA_IDENT, " but ", ident, " - no GLA!")
            return False, "Is no GLA file!"
        version, = struct.unpack("i", file.read(4))
        if version != JAG2Constants.GLA_VERSION:
            return False, "Wrong gla file version! ("+str(version)+" should be "+str(JAG2Constants.GLA_VERSION)+")"
        self.name = readString(file)
        self.scale, self.numFrames, self.ofsFrames, self.numBones, self.ofsCompBonePool, self.ofsSkel, self.ofsEnd = struct.unpack("f6i", file.read(7*4))
        print("Scale: {:.3f}".format(self.scale))
        return True, ""
    
    def saveToFile(self, file):
        file.write(struct.pack("4si64sf6i", JAG2Constants.GLA_IDENT, JAG2Constants.GLA_VERSION, self.name.encode(), self.scale, self.numFrames, self.ofsFrames, self.numBones, self.ofsCompBonePool, self.ofsSkel, self.ofsEnd))

class MdxaBoneOffsets:
    
    def __init__(self):
        self.baseOffset = 2*4 + 64 + 4*7 #sizeof header
        self.boneOffsets = []
    
    # fail-safe (except for exceptions)
    def loadFromFile(self, file, numBones):
        assert(self.baseOffset == file.tell())
        for i in range(numBones):
            self.boneOffsets.append(struct.unpack("i", file.read(4))[0])
    
    def saveToFile(self, file):
        assert(file.tell() == self.baseOffset) #must be after header
        for offset in self.boneOffsets:
            file.write(struct.pack("i", offset))

# originally called MdxaSkel_t, but I find that name misleading
class MdxaBone:
    def __init__(self):
        self.name = ""
        self.flags = 0
        self.parent = -1
        self.basePoseMat = JAG2Math.Matrix()
        self.basePoseMatInv = JAG2Math.Matrix()
        self.numChildren = 0
        self.children = []
        self.index = -1 # not saved, filled by loadBonesFromFile() and when loaded from blender
    
    def getSize(self):
        return struct.calcsize("64sIi12f12fi{}i".format(self.numChildren))
    
    def loadFromFile(self, file):
        self.name = readString(file)
        self.flags, self.parent = struct.unpack("Ii", file.read(2*4))
        self.basePoseMat.loadFromFile(file)
        self.basePoseMatInv.loadFromFile(file)
        self.numChildren, = struct.unpack("i", file.read(4))
        for i in range(self.numChildren):
            self.children.append(struct.unpack("i", file.read(4))[0])
    
    def saveToFile(self, file):
        file.write(struct.pack("64sIi", self.name.encode(), self.flags, self.parent))
        self.basePoseMat.saveToFile(file)
        self.basePoseMatInv.saveToFile(file)
        file.write(struct.pack("i", self.numChildren))
        assert(len(self.children) == self.numChildren)
        for child in self.children:
            file.write(struct.pack("i", child))
    
    def loadFromBlender(self, editbone, boneIndicesByName, bones, objLocalMat):
        # set name
        self.name = editbone.name
        
        # add index to dictionary
        boneIndicesByName[self.name] = self.index
        
        # parent is -1 by default - change if there is one.
        if editbone.parent != None:
            self.parent = boneIndicesByName[editbone.parent.name]
            parent = bones[self.parent]
            parent.numChildren += 1
            parent.children.append(self.index)
        
        # save (inverted) base pose matrix
        mat = objLocalMat * editbone.matrix
        JAG2Math.BlenderBoneRotToGLA(mat) # must not be used for blender-internal calculations anymore!
        matInv = mat.inverted()
        self.basePoseMat.fromBlender(mat)
        self.basePoseMatInv.fromBlender(matInv)
    
    #blenderBonesSoFar is a dictionary of boneIndex -> BlenderBone
    #allBones is the list of all MdxaBones
    #use it to set up hierarchy and add yourself once done.
    def saveToBlender(self, armature, blenderBonesSoFar, allBones, skeletonFixes):
        # create bone 
        bone = armature.edit_bones.new(self.name)
        
        # set position
        mat = self.basePoseMat.toBlender()
        pos = mathutils.Vector(mat.translation)
        bone.head = pos
        # head is offset a bit.
        x_axis = mathutils.Vector(mat.col[0][0:3]) # X points towards next bone.
        bone.tail = pos + x_axis*JAG2Constants.BONELENGTH
        # set roll
        y_axis = -mathutils.Vector(mat.col[1][0:3])
        bone.align_roll(y_axis)
        
        # set parent, if any, keeping in mind it might be overwritten
        parentIndex = self.parent
        parentChanges = JAG2Constants.PARENT_CHANGES[skeletonFixes]
        if self.index in parentChanges:
            parentIndex = parentChanges[self.index]
        if parentIndex != -1:
            blenderParent = blenderBonesSoFar[parentIndex]
            bone.parent = blenderParent
            
            #how many children does the parent have?
            numParentChildren = allBones[parentIndex].numChildren
            # we actually need to take into account the hierarchy changes.
            # so for any bone that used to have this parent but does not anymore, remove one
            for mdxaBone in allBones:
                # if a bone gets its parent changed, and it used to be "my" parent, my parent has one child less.
                if mdxaBone.parent == parentIndex and mdxaBone.index in parentChanges:
                    numParentChildren -= 1
            assert(numParentChildren >= 0)
            # and for any bone that got this as the parent, add one child.
            for _, newParentIndex in parentChanges.items():
                if newParentIndex == parentIndex:
                    numParentChildren += 1
            assert(numParentChildren > 0) #at least this bone is child.
            
            # if this is the only child of its parent or has priority: Connect the parent to this.
            if numParentChildren == 1 or self.name in JAG2Constants.PRIORITY_BONES[skeletonFixes]:
                # but only if that doesn't rotate the bone (much)
                # so calculate the directions...
                oldDir = blenderParent.tail - blenderParent.head
                newDir = pos - blenderParent.head
                oldDir.normalize()
                newDir.normalize()
                dotProduct = oldDir.dot(newDir)
                # ... and compare them using the dot product, which is the cosine of the angle between two unit vectors
                if dotProduct > JAG2Constants.BONE_ANGLE_ERROR_MARGIN:
                    blenderParent.tail = pos
                    bone.use_connect = True
        
        # save to created bones
        blenderBonesSoFar[self.index] = bone

class MdxaSkel:
    def __init__(self):
        self.bones = []
        self.armature = None
        self.armatureObject = None
    
    def loadFromFile(self, file, offsets):
        for i, offset in enumerate(offsets.boneOffsets):
            file.seek(offsets.baseOffset + offset)
            bone = MdxaBone()
            bone.loadFromFile(file)
            bone.index = i
            self.bones.append(bone)
    
    def saveToFile(self, file, header):
        assert(file.tell() == header.ofsSkel)
        for bone in self.bones:
            bone.saveToFile(file)
    
    def fitsArmature(self, armature):
        for bone in self.bones:
            if not bone.name in armature.bones:
                return False, "Bone "+bone.name+" not found in existing skeleton_root armature!"
            return True, ""
    
    def saveToBlender(self, scene_root, skeletonFixes):
        #  Creation
        #create armature
        self.armature = bpy.data.armatures.new("skeleton_root")
        #create object
        self.armature_object = bpy.data.objects.new("skeleton_root", self.armature)
        #set parent
        self.armature_object.parent = scene_root
        #link object to scene
        bpy.context.scene.objects.link(self.armature_object)
        
        #  Set the armature as active and go to edit mode to add bones
        bpy.context.scene.objects.active = self.armature_object
        bpy.ops.object.mode_set(mode='EDIT')
        # list of indices of already created bones - only those bones with this as parent will be added
        createdBonesIndices = [-1]
        # bones yet to be created
        uncreatedBones = []
        uncreatedBones.extend(self.bones)
        parentChanges = JAG2Constants.PARENT_CHANGES[skeletonFixes]
        # Blender EditBones so far by index
        blenderEditBones = {}
        while len(uncreatedBones) > 0:
            # whether a new bone was created this time - if not, there's a hierarchy problem
            createdBone = False
            newUncreatedBones = []
            for bone in uncreatedBones:
                # only create those bones whose parent has already been created.
                if bone.index in parentChanges:
                    parent = parentChanges[bone.index]
                else:
                    parent = bone.parent
                if parent in createdBonesIndices:
                    bone.saveToBlender(self.armature, blenderEditBones, self.bones, skeletonFixes)
                    createdBonesIndices.append(bone.index)
                    createdBone = True
                else:
                    newUncreatedBones.append(bone)
            uncreatedBones = newUncreatedBones
            if not createdBone:
                bpy.ops.object.mode_set(mode='OBJECT')
                return False, "gla has hierarchy problems!"
        # leave armature edit mode
        bpy.ops.object.mode_set(mode='OBJECT')
        return True, ""

class MdxaFrame:
    def __init__(self):
        self.boneIndices = []
    
    # returns the highest referenced index - not nice from a design standpoint but saves space, which is probably good.
    def loadFromFile(self, file, numBones):
        maxIndex = 0
        for i in range(numBones):
            # bone indices are only 3 bytes long - with 20k+ frames 25% less is quite a bit, reportedly.
            index, = struct.unpack("I", file.read(3)+b"\0")
            maxIndex = max(maxIndex, index)
            self.boneIndices.append(index)
        return maxIndex
    
    def saveToFile(self, file):
        for index in self.boneIndices:
            # only write the first 3 bytes of the packed number
            file.write(struct.pack("I", index)[:3])

class MdxaBonePool:
    def __init__(self):
        # during import, this is a list of CompBone objects
        # during exports, it's a list of 14-byte-objects (compressed bones)
        self.bones = []
    
    def loadFromFile(self, file, numCompBones):
        for i in range(numCompBones):
            compBone = JAG2Math.CompBone()
            compBone.loadFromFile(file)
            self.bones.append(compBone)
    
    def saveToFile(self, file):
        for bone in self.bones:
            file.write(bone)

# Frames & Compressed Bone Pool
class MdxaAnimation:
    def __init__(self):
        self.frames = []
        self.bonePool = MdxaBonePool()
    
    def loadFromFile(self, file, header, skeleton, startFrame, numFrames):
        # read frames
        if file.tell() != header.ofsFrames:
            print("Info: Frames in .gla not encountered when expected (at ", file.tell(), " instead of ", header.ofsFrames, "), seeking correct position. There could be a bug in the importer (bad) or the file could be unusual - but not necessarily wrong (no problem).", sep="")
            file.seek(header.ofsFrames)
        
        # prepare frame start/end settings
        if numFrames == -1:
            assert(startFrame == 0)
            numFrames = header.numFrames
        else:
            print("Reading {} frames, starting at {}".format(numFrames, startFrame))
        if startFrame >= header.numFrames:
            print("Warning: StartFrame beyond existing frames, using last one")
            startFrame = header.numFrames - 1
            numFrames = 1
        if startFrame + numFrames > header.numFrames:
            print("Warning: Trying to import more frames than there are, fixing")
            numFrames = header.numFrames - startFrame
        # skip first startFrame frames
        file.seek(startFrame * 3 * header.numBones, 1) #1 = from current position
        
        #read (remaining) frames
        maxIndex = -1
        for i in range(numFrames):
            frame = MdxaFrame()
            # loadFromFile returns highest read index
            maxIndex = max(maxIndex, frame.loadFromFile(file, header.numBones))
            self.frames.append(frame)
        
        # read compressed bone pool
        # see if we reached it yet
        curPos = file.tell()
        if curPos != header.ofsCompBonePool:
            # we're not yet there. If we're off by 0-3 bytes, it's because 32-bit-alignment is forced. Silently seek correct position. Otherwise: warn (and seek correct position, too)
            # if we're only importing some frames, we may or may not be there yet, of course, so don't warn.
            if curPos > header.ofsCompBonePool or (header.ofsCompBonePool > curPos + 3 and numFrames == header.numFrames):
                print("Info: Bone Pool in .gla not encountered when expected (at ", file.tell(), " instead of ", header.ofsCompBonePool, "), seeking correct position. There could be a bug in the importer (bad) or the file could be unusual - but not necessarily wrong (no problem).", sep="")
            file.seek(header.ofsCompBonePool)
        # there's one more object than the highest index since those start at 0
        self.bonePool.loadFromFile(file, maxIndex+1)
        
        #file should be over now, bone pool is usually the last thing. I'm not sure it has to be, but so far it has always been.
        if file.tell() != header.ofsEnd and numFrames == header.numFrames:
            print("Info: .gla Bone Pool read but file not over yet - this likely indicates a problem.")
        return True, ""
    
    def saveToFile(self, file, header):
        assert(file.tell() == header.ofsFrames)
        for frame in self.frames:
            frame.saveToFile(file)
        # add padding if not 32 bit aligned (due to 3-byte-indices)
        if file.tell() % 4 != 0:
            file.seek(4 - (file.tell() % 4), 1) # from_what = 1 -> from current position
        assert(file.tell() == header.ofsCompBonePool)
        self.bonePool.saveToFile(file)
    
    def saveToBlender(self, skeleton, armature, scale):
        import time
        startTime = time.time()
        #   Bone Position Set Order
        # bones have to be set in hierarchical order - their position depends on their parent's absolute position, after all.
        # so this is the order in which bones have to be processed.
        hierarchyOrder = []
        while len(hierarchyOrder) < len(skeleton.bones):
            # make sure we add something each frame (infinite loop otherwise)
            addedSomething = False
            # I could copy skeleton.bones for minor speed boost, imho not necessary.
            for bone in skeleton.bones:
                if bone.index in hierarchyOrder:
                    continue #we already have this one.
                if bone.parent  != -1 and bone.parent not in hierarchyOrder:
                    continue #we don't have the parent yet, so this cannot come yet.
                hierarchyOrder.append(bone.index)
                addedSomething = True
            assert(addedSomething)
        # for going leaf to root
        
        #   Blender PoseBones list
        bones = []
        for info in skeleton.bones: # is ordered by index
            bones.append(armature.pose.bones[info.name])
        
        basePoses = []
        for bone in skeleton.bones:
            basePoses.append(bone.basePoseMat.toBlender())
        
        #   Prepare animation
        scene = bpy.context.scene
        scene.frame_start = 0
        numFrames = len(self.frames)
        scene.frame_end = numFrames - 1
        
        if scale == 0:
        #if True:
            scale = 1
        else:
            scale = 1/scale
        scaleMatrix = mathutils.Matrix([
            [scale, 0, 0, 0],
            [0, scale, 0, 0],
            [0, 0, scale, 0],
            [0, 0, 0, 1]
            ])
        
        # show progress every 1000 steps, but at least 10 times)
        progressStep = min(1000, round(numFrames / 10))
        nextProgressDisplayTime = time.time() + PROGRESS_UPDATE_INTERVAL
        lastFrameNum = 0
        
        #   Export animation
        for frameNum, frame in enumerate(self.frames):
            # show progress bar / remaining time
            if time.time() >= nextProgressDisplayTime:
                numProcessedFrames = frameNum - lastFrameNum
                framesRemaining = numFrames - frameNum
                # only take the frames since the last update into account since the speed varies.
                # speed's roughly inversely proportional to the current frame number so I could use that to predict remaining time...
                timeRemaining = PROGRESS_UPDATE_INTERVAL * framesRemaining / numProcessedFrames
                
                print("Frame {}/{} - {:.2%} - remaining time: ca. {:.0f}m {:.0f}s".format(frameNum, numFrames, frameNum/numFrames, timeRemaining // 60, timeRemaining % 60))
                
                lastFrameNum = frameNum
                nextProgressDisplayTime = time.time() + PROGRESS_UPDATE_INTERVAL
            
            #set current frame
            scene.frame_set(frameNum)
            
            # absolute offset matrices by bone index
            offsets = {}
            for index in hierarchyOrder:
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                mdxaBone = skeleton.bones[index]
                assert(mdxaBone.index == index)
                bonePoolIndex = frame.boneIndices[index]
                # get offset transformation matrix, relative to parent
                offset = self.bonePool.bones[bonePoolIndex].matrix
                # turn into absolute offset matrix (already is if this is top level bone)
                if mdxaBone.parent != -1:
                    offset = offsets[mdxaBone.parent] * offset
                # save this absolute offset for use by children
                offsets[index] = offset
                # calculate the actual position
                transformation = offset * basePoses[index]
                # flip axes as required for blender bone
                JAG2Math.GLABoneRotToBlender(transformation)
                
                pose_bone = bones[index]
                #pose_bone.matrix = transformation * scaleMatrix
                pose_bone.matrix = transformation
                pose_bone.scale = [1, 1, 1] # in the _humanoid face, the scale gets changed. that messes the re-export up.
                pose_bone.keyframe_insert('location')
                pose_bone.keyframe_insert('rotation_quaternion')
                # hackish way to force the matrix to update
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        scene.frame_current = 1

class GLA:
    
    def __init__(self):
        #whether this is the automatic default skeleton
        self.isDefault = False
        self.header = MdxaHeader()
        self.boneOffsets = MdxaBoneOffsets()
        self.skeleton = MdxaSkel()
        self.boneIndexByName = {}
        # boneNameByIndex = {} #just use bones[index].name
        # the Blender Armature / Object
        self.skeleton_armature = None
        self.skeleton_object = None
        self.animation = MdxaAnimation()
    
    def loadFromFile(self, filepath_abs, loadAnimation, startFrame, numFrames):
        print("Loading {}...".format(filepath_abs))
        try:
            file = open(filepath_abs, mode="rb")
        except IOError:
            print("Could not open file: {}".format(filepath_abs))
            return False, "Could not open file!"
        profiler = MrwProfiler.SimpleProfiler(True)
        # load header
        profiler.start("reading header")
        success, message = self.header.loadFromFile(file)
        if not success:
            return False, message
        profiler.stop("reading header")
        # load offsets (directly after header, always)
        profiler.start("reading bone hierarchy")
        self.boneOffsets.loadFromFile(file, self.header.numBones)
        # load bones
        self.skeleton.loadFromFile(file, self.boneOffsets)
        # build lookup map
        for bone in self.skeleton.bones:
            self.boneIndexByName[bone.name] = bone.index
        profiler.stop("reading bone hierarchy")
        if loadAnimation != 'NONE':
            profiler.start("reading animations")
            if loadAnimation == 'ALL':
                success, message = self.animation.loadFromFile(file, self.header, self.skeleton, 0, -1)
            else:
                assert(loadAnimation == 'RANGE')
                success, message = self.animation.loadFromFile(file, self.header, self.skeleton, startFrame, numFrames)
            if not success:
                return False, message
            profiler.stop("reading animations")
        return True, ""
    
    def loadFromBlender(self, gla_filepath_rel, gla_reference_abs):
        # fill out header name
        self.header.name = gla_filepath_rel
        
        # find skeleton_root
        if not "skeleton_root" in bpy.data.objects:
            return False, "No skeleton_root object found!"
        self.skeleton_object = bpy.data.objects["skeleton_root"]
        if self.skeleton_object.type != 'ARMATURE':
            return False, "skeleton_root is no Armature!"
        self.skeleton_armature = self.skeleton_object.data
        self.header.scale = self.skeleton_object.g2_prop_scale / 100
        
        # make skeleton_root the active object
        bpy.context.scene.objects.active = self.skeleton_object
        self.skeleton_object.select = True
        self.skeleton_object.hide = False
        
        # in case of rescaled/moved skeleton object: get transformation (assuming we're a child of scene_root)
        localMat = self.skeleton_object.matrix_local
        
        # if there's a reference GLA (for bone indices), load that
        if gla_reference_abs != "":
            print("Using reference GLA skeleton - warning: there's no check beyond bone names (hierarchy, base pose etc.)")
            
            # load reference GLA
            referenceGLA = GLA()
            success, message = referenceGLA.loadFromFile(gla_reference_abs, 'NONE', 0, 0)
            if not success:
                return False, "Could not load reference GLA: {}".format(message)
            
            # copy relevant data from reference
            self.boneIndexByName = referenceGLA.boneIndexByName
            self.skeleton = referenceGLA.skeleton # will be changed, but reference is discarded later anyway
            self.boneOffsets = referenceGLA.boneOffsets
            self.header.ofsFrames = referenceGLA.header.ofsFrames
            self.header.ofsSkel = referenceGLA.header.ofsSkel
            self.header.numBones = referenceGLA.header.numBones
            
            # verify all bones exist
            success, message = self.skeleton.fitsArmature(self.skeleton_armature)
            if not success:
                return False, "Armature does not fit reference: {}".format(message)
        
        # or no reference GLA? build new skeleton then.
        else:
            
            # enter edit mode so we can access editbones
            bpy.ops.object.mode_set(mode='EDIT')
            
            # populate bone hierarchy
            bonesToAdd = [bone for bone in self.skeleton_armature.edit_bones]
            while len(bonesToAdd) > 0:
                addedSomething = False
                newBonesToAdd = []
                for bone in bonesToAdd:
                    # add bones whose parents have already been added
                    if bone.parent == None or bone.parent.name in self.boneIndexByName:
                        # create this bone
                        newBone = MdxaBone()
                        
                        # set its index (will be appended, hence the size)
                        newBone.index = len(self.skeleton.bones)
                        
                        # read the rest from the editbone
                        newBone.loadFromBlender(bone, self.boneIndexByName, self.skeleton.bones, localMat)
                        
                        # append bone
                        self.skeleton.bones.append(newBone)
                        addedSomething = True
                    else:
                        newBonesToAdd.append(bone)
                bonesToAdd = newBonesToAdd
                if addedSomething == False:
                    return False, "Hierarchy error (most likely a bug, actually)"
            
            # calculate bone file position offsets
            offset = 4 * len(self.skeleton.bones) # first bone starts after the bone offsets
            self.header.ofsSkel = offset + self.boneOffsets.baseOffset # save first bones position
            for bone in self.skeleton.bones:
                self.boneOffsets.boneOffsets.append(offset)
                offset += bone.getSize()
            
            self.header.ofsFrames = self.boneOffsets.baseOffset + offset # frames start after last bone
            self.header.numBones = len(self.skeleton.bones)
        
        
        #   retrieve animations
        
        print("Compressing animation...")
        
        # enter pose mode
        bpy.ops.object.mode_set(mode='POSE')
        
        # create a dictionary containing the indices of already added compressed bones - lookup should be faster than a linear search through the existing compressed bones (at the cost of more RAM usage - that's ok)
        compBoneIndices = {}
        
        # for each frame: 
        for curFrame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
            # progress bar-ish thing
            if curFrame % 10 == 0:
                print("Compressing frame {}...".format(curFrame))
            
            frame = MdxaFrame()
            bpy.context.scene.frame_set(curFrame)
            #bpy.context.scene.frame_current = curFrame
            
            # bone offsets need to be calculated in hierarchical order, but written in index order
            # so calculate first:
            relativeBoneOffsets = [None] * self.header.numBones # these get written to the GLA
            
            absoluteBoneOffsets = [None] * self.header.numBones # these are for calculating
            
            unprocessed = [i for i in range(self.header.numBones)]
            while len(unprocessed) > 0:
                # make sure we're not looping infinitely (shouldn't be possible)
                progressed = False
                
                newUnprocessed = []
                for index in unprocessed:
                    bone = self.skeleton.bones[index]
                    basebone = self.skeleton_armature.bones[bone.name]
                    posebone = self.skeleton_object.pose.bones[bone.name]
                    
                    basePoseMat = localMat * basebone.matrix_local
                    poseMat = localMat * posebone.matrix
                    
                    # change rotation axes from blender style to gla style
                    JAG2Math.BlenderBoneRotToGLA(basePoseMat)
                    JAG2Math.BlenderBoneRotToGLA(poseMat)
                    if bone.parent == -1:
                        relativeBoneOffsets[index] = absoluteBoneOffsets[index] = poseMat * basePoseMat.inverted()
                        
                        progressed = True
                        
                    elif bone.parent not in unprocessed:
                        assert(absoluteBoneOffsets[bone.parent]) #just what the if checks
                        assert(absoluteBoneOffsets[index] == None) # each offset should only be calculated once.
                        
                        relativeBoneOffsets[index] = absoluteBoneOffsets[bone.parent].inverted() * poseMat * basePoseMat.inverted()
                        absoluteBoneOffsets[index] =  absoluteBoneOffsets[bone.parent] * relativeBoneOffsets[index]
                        
                        progressed = True
                        
                    else:
                        newUnprocessed.append(index)
                unprocessed = newUnprocessed
                
                assert(progressed)
            
            # then write precalculated offsets:
            for offset in relativeBoneOffsets:
                
                # compress that offset
                compOffset = JAG2Math.CompBone.compress(offset)
                
                try:
                    # try to use existing compressed bone offset
                    index = compBoneIndices[compOffset]
                    frame.boneIndices.append(index)
                except KeyError:
                    # if this offset is not yet part of the pool, add it
                    index = len(self.animation.bonePool.bones)
                    self.animation.bonePool.bones.append(compOffset)
                    frame.boneIndices.append(index)
                    compBoneIndices[compOffset] = index
            
            self.animation.frames.append(frame)
        
        self.header.numFrames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
        # enforce 32 bit alignment after 3-byte-indices
        framesSize = 3 * self.header.numFrames * self.header.numBones
        if framesSize % 4 != 0:
            framesSize += 4 - (framesSize % 4)
        self.header.ofsCompBonePool = self.header.ofsFrames + framesSize
        self.header.ofsEnd = self.header.ofsCompBonePool + len(self.animation.bonePool.bones) * 14
        
        return True, ""
    
    def saveToFile(self, filepath_abs):
        try:
            file = open(filepath_abs, mode="wb")
        except IOError:
            print("Could not open file: ", filepath_abs, sep="")
            return False, "Could not open file!"
        self.header.saveToFile(file)
        self.boneOffsets.saveToFile(file)
        self.skeleton.saveToFile(file, self.header)
        self.animation.saveToFile(file, self.header)
        assert(file.tell() == self.header.ofsEnd)
        return True, ""
    
    def saveToBlender(self, scene_root, useAnimation, skeletonFixes):
        print("Applying skeleton/skeleton to Blender")
        profiler = MrwProfiler.SimpleProfiler(True)
        #default skeleton = no skeleton.
        if self.isDefault:
            return True, ""
        
        #  try using existing skeletons
        # first check if there's already an armature object called skeleton_root. Try using that.
        if "skeleton_root" in bpy.data.objects:
            print("Found a skeleton_root object, trying to use it.")
            self.skeleton_object = bpy.data.objects["skeleton_root"]
            if self.skeleton_object.type != 'ARMATURE':
                return False, "Existing skeleton_root object is no armature!"
            self.skeleton_armature = self.skeleton_object.data
            self.skeleton_object.g2_prop_scale = self.header.scale * 100
        # If there's no skeleton, there may yet still be an armature. Use that.
        elif "skeleton_root" in bpy.data.armatures:
            print("Found skeleton_root armature, trying to use it.")
            self.skeleton_armature = bpy.data.armatures["skeleton_root"]
        
        # for profiling, possibly
        global g_temp
        # if we found an existing armature, we need to make sure it's linked to an object and valid
        if self.skeleton_armature:
            # see if the armature fits
            success, message =  self.skeleton.fitsArmature(self.skeleton_armature)
            if not success:
                return False, message
            
            # this armature would work, add it to an object if necessary
            if not self.skeleton_object:
                self.skeleton_object = bpy.data.objects.new("skeleton_root", self.skeleton_armature)
                self.skeleton_object.g2_prop_scale = self.header.scale * 100
            
            # link the object to the current scene if necessary
            if not self.skeleton_object.name in bpy.context.scene.objects:
                bpy.context.scene.objects.link(self.skeleton_object)
            
            # set its parent to the scene_root (not strictly speaking necessary but keeps output consistent)
            self.skeleton_object.parent = scene_root
            
            # add animations, if any
            if useAnimation:
                profiler.start("applying animations")
                # go to object mode
                bpy.context.scene.objects.active = self.skeleton_object
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                if PROFILE:
                    import cProfile
                    print("=== Profile start ===")
                    cProfile.runctx("self.animation.saveToBlender(self.skeleton, self.skeleton_object, self.header.scale)", globals(), locals())
                    print("=== Profile stop ===")
                else:
                    self.animation.saveToBlender(self.skeleton, self.skeleton_object, self.header.scale)
                profiler.stop("applying animations")
            
            #that's all
            return True, ""
        
        
        # no existing Armature found, create a new one.
        
        #create armature
        profiler.start("creating armature")
        success, message = self.skeleton.saveToBlender(scene_root, skeletonFixes)
        if not success:
            return False, message
        self.skeleton_armature = self.skeleton.armature
        self.skeleton_object = self.skeleton.armature_object
        self.skeleton_object.g2_prop_scale = self.header.scale * 100
        profiler.stop("creating armature")
        
        #add animations, if any
        if useAnimation:
            profiler.start("applying animations")
            # go to object mode
            bpy.context.scene.objects.active = self.skeleton_object
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)            
            if PROFILE:
                import cProfile
                print("=== Profile start ===")
                cProfile.runctx("self.animation.saveToBlender(self.skeleton, self.skeleton_object, self.header.scale)", globals(), locals())
                print("=== Profile stop ===")
            else:
                self.animation.saveToBlender(self.skeleton, self.skeleton_object, self.header.scale)
            profiler.stop("applying animations")
        return True, ""
