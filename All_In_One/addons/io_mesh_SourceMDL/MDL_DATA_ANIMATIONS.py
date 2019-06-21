from enum import Enum
from pprint import pprint
from typing import List

import struct

import math

try:
    from .MDLIO_ByteIO import ByteIO
    from .GLOBALS import SourceFloat16bits, SourceVector
    from .MDL_DATA import *
except:
    from MDLIO_ByteIO import ByteIO
    from GLOBALS import SourceFloat16bits, SourceVector
    from MDL_DATA import *


class SourceMdlAnimationValuePointer:
    """"FROM: SourceEngine2006_source\public\studio.h
    struct mstudioanim_valueptr_t
    {
       short	offset[3];
       inline mstudioanimvalue_t *pAnimvalue( int i ) const { if (offset[i] > 0) return
         (mstudioanimvalue_t *)(((byte *)this) + offset[i]); else return NULL; };
    };"""

    def __init__(self):
        self.animXValueOffset = 0
        self.animYValueOffset = 0
        self.animZValueOffset = 0

        self.theAnimXValues = []
        self.theAnimYValues = []
        self.theAnimZValues = []

    def read(self, reader: ByteIO):
        self.animXValueOffset = reader.read_int16()
        self.animYValueOffset = reader.read_int16()
        self.animZValueOffset = reader.read_int16()

    def read_values(self, entry, frames, reader):
        with reader.save_current_pos():
            if self.animXValueOffset > 0:
                self.read_value(entry, frames, self.theAnimXValues, self.animXValueOffset, reader)
            if self.animYValueOffset > 0:
                self.read_value(entry, frames, self.theAnimYValues, self.animYValueOffset, reader)
            if self.animZValueOffset > 0:
                self.read_value(entry, frames, self.theAnimZValues, self.animZValueOffset, reader)
                # print(self)

    def read_value(self, entry, frames, holder, offset, reader):
        reader.seek(entry + offset)
        frameCountRemainingToBeChecked = frames
        accumulatedTotal = 0
        while frameCountRemainingToBeChecked > 0:
            value = SourceMdlAnimationValue()
            value.value = reader.read_int16()
            currentTotal = value.total
            accumulatedTotal += currentTotal
            if currentTotal == 0:
                print('BAD IF THIS REACHED')
                break
            frameCountRemainingToBeChecked -= currentTotal
            holder.append(value)
            validCount = value.valid
            for i in range(validCount):
                value = SourceMdlAnimationValue()
                value.value = reader.read_int16()
                holder.append(value)

    def __repr__(self):  # X:{0.theAnimXValues} Y:{0.theAnimYValues} Z:{0.theAnimZValues}
        return "<AnimationValuePointer X off:{0.animXValueOffset} Y off:{0.animYValueOffset} Z off:{0.animZValueOffset}>".format(
            self)


class SourceQuaternion48bits:
    def __init__(self):
        self.theXInput = SourceFloat16bits()
        self.theYInput = SourceFloat16bits()
        self.theZWInput = SourceFloat16bits()

    def read(self, reader: ByteIO):
        self.theXInput.read(reader)
        self.theYInput.read(reader)
        self.theZWInput.read(reader)

    def __repr__(self):
        return '<Quaternion X: {} Y: {} Z: {}>'.format(self.theXInput.float_value, self.theYInput.float_value,
                                                       self.theZWInput.float_value)


class SourceQuaternion64bits:
    def __init__(self):
        self.theBytes = [0,0,0,0,0,0,0,0]  # type: List[int]

    def read(self, reader: ByteIO):
        self.theBytes.clear()
        self.theBytes = [reader.read_uint8() for _ in range(8)]
        print(self.theBytes)

    @property
    def x(self):
        byte0 = (self.theBytes[0] & 0xFF)
        byte1 = (self.theBytes[1] & 0xFF) << 8
        byte2 = (self.theBytes[2] & 0x1F) << 16

        bitsResult = IntegerAndSingleUnion(byte2|byte1|byte0)
        return (bitsResult.i - 1048576) * (1 / 1048576.5)

    @property
    def y(self):
        byte2 = (self.theBytes[2] & 0xE0) >> 5
        byte3 = (self.theBytes[3] & 0xFF) << 3
        byte4 = (self.theBytes[4] & 0xFF) << 11
        byte5 = (self.theBytes[5] & 0x3) >> 19
        bitsResult = IntegerAndSingleUnion(byte5|byte4|byte3|byte2)
        return (bitsResult.i -1048576) * (1 / 1048576.5)

    @property
    def z(self):
        byte5 = (self.theBytes[5] & 0xFC) >> 2
        byte6 = (self.theBytes[6] & 0xFF) << 6
        byte7 = (self.theBytes[7] & 0x7F) << 14

        bitsResult = IntegerAndSingleUnion(byte7|byte6|byte5)
        return (bitsResult.i -1048576) * (1 / 1048576.5)

    @property
    def wneg(self):
        return -1 if self.theBytes[7]&0x80 > 0 else 1

    @property
    def w(self):
        print(1-self.x**2-self.y**2-self.z**2)
        print(self.x**2,self.y**2,self.z**2)
        # print('w',math.sqrt(1+(self.x*self.x-self.y*self.y-self.z*self.z))*self.wneg)
        return math.sqrt(1-self.x**2-self.y**2-self.z**2)*self.wneg

    @property
    def as_4D_vec(self):
        return [self.x,self.y,self.z,self.w]

    def r2d(self,val):
        cos_a = self.w
        print(cos_a)
        angle = math.acos(cos_a)*2
        sin_a = math.sqrt(1-(cos_a**2))
        if math.fabs(sin_a)<0.000005:sin_a = 1
        return val/sin_a

    @property
    def xd(self):
        return self.r2d(self.x)
    @property
    def yd(self):
        return self.r2d(self.y)
    @property
    def zd(self):
        return self.r2d(self.z)

    @property
    def as_3D_vec(self):
        return [self.xd,self.yd,self.zd]

    def __repr__(self):
        # return "<Quaternion64 X:{0.x} Y:{0.y} Z:{0.z}>".format(self)
        return "<Quaternion64 X:{0.xd} Y:{0.yd} Z:{0.zd}>".format(self)

class IntegerAndSingleUnion:

    def __init__(self,i):
        self.i = i

    @property
    def s(self):
        return struct.unpack('f',struct.pack('i',self.i))

class SourceVector48bits:
    def __init__(self):
        self.theXInput = SourceFloat16bits()
        self.theYInput = SourceFloat16bits()
        self.theZInput = SourceFloat16bits()

    def read(self, reader: ByteIO):
        self.theXInput.read(reader)
        self.theYInput.read(reader)
        self.theZInput.read(reader)

    def __repr__(self):
        return '<Vector X: {} Y: {} Z: {}>'.format(self.theXInput.float_value, self.theYInput.float_value,
                                                   self.theZInput.float_value)


class SourceMdlAnimation:
    class STUDIO_ANIM:
        RAWPOS = 1
        RAWROT = 2
        ANIMPOS = 4
        ANIMROT = 8
        DELTA = 16
        RAWROT2 = 32

        @classmethod
        def get_flags(cls, flag):
            flags = []
            for name, val in vars(cls).items():
                if name.isupper():
                    if (flag & val) > 0:
                        flags.append(name)
            return flags

    def __init__(self):
        self.boneIndex = 0
        self.flags = 0
        self.nextSourceMdlAnimationOffset = 0
        self.theRotV = SourceMdlAnimationValuePointer()
        self.thePosV = SourceMdlAnimationValuePointer()
        self.theRot48bits = SourceQuaternion48bits()
        self.theRot64bits = SourceQuaternion64bits()
        self.thePos = SourceVector48bits()

    def read(self, frame_count, anim_section, mdl: SourceMdlFileData, reader: ByteIO):
        anim_entry = reader.tell()
        self.boneIndex = reader.read_uint8()
        print('BoneIndex:',self.boneIndex)
        try:
            self.bone_name = mdl.bones[self.boneIndex].name
        except:
            self.bone_name = "ERROR"
        print('BoneName:',self.bone_name)
        if self.boneIndex == 255:
            reader.skip(3)
            return self, 0
        if self.boneIndex >= mdl.bone_count:
            print('Bone index out of range {} - {}'.format(self.boneIndex, mdl.bone_count))
            return self, 0
        self.flags = reader.read_uint8()
        self.sflags = self.STUDIO_ANIM.get_flags(self.flags)
        self.nextSourceMdlAnimationOffset = reader.read_int16()
        pdata = reader.tell()
        print('Seq flag',self.flags,self.sflags)
        if (self.flags & self.STUDIO_ANIM.RAWROT2) > 0:
            with reader.save_current_pos():
                reader.seek(pdata)
                self.theRot64bits.read(reader)
                print('Rot 64',self.theRot64bits)

        if (self.flags & self.STUDIO_ANIM.RAWROT) > 0:
            with reader.save_current_pos():
                reader.seek(pdata)
                self.theRot48bits.read(reader)
                print('Rot 48', self.theRot48bits)

        if (self.flags & self.STUDIO_ANIM.RAWPOS) > 0:
            with reader.save_current_pos():
                reader.seek(pdata+(((self.flags & self.STUDIO_ANIM.RAWROT) != 0)*6) + ((self.flags & self.STUDIO_ANIM.RAWROT2) != 0)*8)
                self.thePos.read(reader)
                print('Pos', self.thePos)

        if (self.flags & self.STUDIO_ANIM.ANIMROT) > 0:
            with reader.save_current_pos():
                rotV_entry = reader.tell()
                reader.seek(pdata)
                self.theRotV.read(reader)
                self.theRotV.read_values(rotV_entry, frame_count, reader)
                print('Rot V', self.theRotV)

        if (self.flags & self.STUDIO_ANIM.ANIMPOS) > 0:
            with reader.save_current_pos():
                reader.seek(((self.flags & self.STUDIO_ANIM.ANIMPOS)!=0) + pdata)
                posV_entry = reader.tell()
                self.thePosV.read(reader)
                self.thePosV.read_values(posV_entry, frame_count, reader)
                print('Pos V', self.thePosV)
        print('\n')
        pprint(self.__dict__)
        print('\n')
        if self.nextSourceMdlAnimationOffset == 0:
            print('DONE WITH ANIMATIONS')
            reader.seek(pdata)
            return self, -1
        else:
            nextAnimationInputFileStreamPosition = anim_entry + self.nextSourceMdlAnimationOffset
            if nextAnimationInputFileStreamPosition < reader.tell():
                print('PROBLEM! Should not be going backwards in file.')
                # raise BufferError('PROBLEM! Should not be going backwards in file.')
            reader.seek(nextAnimationInputFileStreamPosition)

        anim_section.append(self)

        return self, 1

    def __repr__(self):
        return "<Animation bone name:{0.bone_name} index:{0.boneIndex} flags:{0.sflags} thePosV:{0.thePosV} theRotV:{0.theRotV} >".format(
            self)


class BoneConstantInfo:
    def __init__(self):
        self.theConstantRawPos = SourceVector48bits()
        self.theConstantRawRot = SourceQuaternion48bits()

    def read(self, reader: ByteIO):
        self.theConstantRawPos.read(reader)
        self.theConstantRawRot.read(reader)

    def __repr__(self):
        return "<BoneConstantInfo constant pos:{} constant rot:{}>".format(self.theConstantRawPos,
                                                                           self.theConstantRawRot)


class BoneFrameDataInfo:
    def __init__(self):
        self.theAnimPosition = SourceVector48bits()
        self.theAnimRotation = SourceQuaternion48bits()
        self.theFullAnimPosition = SourceVector()
        self.theFullAnimUnknown01 = 0
        self.theFullAnimUnknown02 = SourceQuaternion64bits()

    def __repr__(self):
        return "<BoneFrameDataInfo anim position:{} anim rotation:{} Full Anim Position:{}>".format(
            self.theAnimPosition, self.theAnimRotation, self.theFullAnimPosition)


class SourceAniFrameAnim:
    STUDIO_FRAME_RAWPOS = 1
    STUDIO_FRAME_RAWROT = 2
    STUDIO_FRAME_ANIMPOS = 4
    STUDIO_FRAME_ANIMROT = 8
    STUDIO_FRAME_FULLANIMPOS = 16
    STUDIO_FRAME_UNKNOWN01 = 64
    STUDIO_FRAME_UNKNOWN02 = 128

    def __init__(self):
        self.constantsOffset = 0
        self.frameOffset = 0
        self.unused = []
        self.theBoneFlags = []
        self.theBoneConstantInfos = []  # type: List[BoneConstantInfo]
        self.theBoneFrameDataInfos = []  # type: List[BoneFrameDataInfo]

    def __repr__(self):
        return "<AniFrameAnim frame offset:{} constant offset:{}>".format(self.frameOffset, self.constantsOffset)


class SourceMdlMovement:
    def __init__(self):
        self.endframeIndex = 0
        self.motionFlags = 0
        self.v0 = 0.0
        self.v1 = 0.0
        self.angle = 0.0
        self.vector = SourceVector()
        self.position = SourceVector()

    def read(self, reader: ByteIO):
        self.endframeIndex = reader.read_uint32()
        self.motionFlags = reader.read_uint32()
        self.v0 = reader.read_float()
        self.v1 = reader.read_float()
        self.angle = reader.read_float()
        self.vector.read(reader)
        self.position.read(reader)
        return self

    def __repr__(self):
        return "<Movement angle:{} vector:{} position:{}>".format(self.angle, self.vector, self.position)


class SourceMdlAnimationValue:
    """"FROM: SourceEngine2006_source\public\studio.h
    // animation frames
    union mstudioanimvalue_t
    {
        struct
        {
          byte	valid;
          byte	total;
        } num;
        short		value;
    };"""

    def __init__(self, value=0):
        self._valid = 0
        self._total = 1

        self.value = value

    @property
    def valid(self):
        a = struct.pack('h', self.value)
        _, ret = struct.unpack('BB', a)
        return ret

    @property
    def total(self):
        a = struct.pack('h', self.value)
        ret, _ = struct.unpack('BB', a)
        return ret

    def __repr__(self):
        return "<AnimationValue value:{} valid:{} total:{}>".format(self.value, self.valid, self.total)


class SourceMdlCompressedIkError:
    def __init__(self):
        self.scale = []  # len 6
        self.offset = []  # len 6
        self.theAnimValues = []  # type: List[SourceMdlAnimationValue]

    def read(self, reader: ByteIO):
        entry = reader.tell()
        self.scale = [reader.read_uint32() for _ in range(6)]
        self.offset = [reader.read_uint32() for _ in range(6)]
        for offset in self.offset:
            with reader.save_current_pos():
                reader.seek(entry + offset)
                self.theAnimValues.append(SourceMdlAnimationValue(reader.read_uint16()))
        return self

    def __repr__(self):
        return "<CompressedIkError scale:{} anim values:{}>".format(self.scale, self.theAnimValues)


class SourceMdlLocalHierarchy:
    def __init__(self):
        self.boneIndex = 0
        self.boneNewParentIndex = 0
        self.startInfluence = 0.0
        self.peakInfluence = 0.0
        self.tailInfluence = 0.0
        self.endInfluence = 0.0
        self.startFrameIndex = 0
        self.localAnimOffset = 0
        self.unused = []  # len 4
        self.theLocalAnims = SourceMdlCompressedIkError()

    def read(self, reader: ByteIO):
        entry = reader.tell()
        self.boneIndex = reader.read_uint32()
        self.boneNewParentIndex = reader.read_uint32()
        self.startInfluence = reader.read_float()
        self.peakInfluence = reader.read_float()
        self.tailInfluence = reader.read_float()
        self.endInfluence = reader.read_float()
        self.startFrameIndex = reader.read_uint32()
        self.localAnimOffset = reader.read_uint32()

        if self.localAnimOffset != 0:
            with reader.save_current_pos():
                reader.seek(entry + self.localAnimOffset)
                self.theLocalAnims.read(reader)

        self.unused = [reader.read_uint32() for _ in range(4)]
        return self

    def __repr__(self):
        return "<LocalHierarchy bone index:{}>".format(self.boneIndex)


class SourceMdlAnimationSection:
    def __init__(self):
        self.animBlock = 0
        self.animOffset = 0

    def read(self, reader: ByteIO):
        self.animBlock = reader.read_uint32()
        self.animOffset = reader.read_uint32()
        return self

    def __repr__(self):
        return "<AnimationSection anim Block:{} anim offset:{}>".format(self.animBlock, self.animOffset)


class SourceMdlAnimationDescBase:
    def __init__(self):
        self.theName = ''

    def __repr__(self):
        return "<AnimationDesc name:{}>".format(self.theName)


class SourceMdlIkRule:
    pass


class SourceMdlAnimationDesc49(SourceMdlAnimationDescBase):

    class STUDIO:
        LOOPING = 1
        SNAP = 2
        DELTA = 4
        AUTOPLAY = 8
        POST = 16
        ALLZEROS = 32
        FRAMEANIM = 64
        CYCLEPOSE = 128
        REALTIME = 256
        LOCAL = 512
        HIDDEN = 1024
        OVERRIDE = 2048
        ACTIVITY = 4096
        EVENT = 8192
        WORLD = 16384
        NOFORCELOOP = 32768
        EVENT_CLIENT = 65536

        def __init__(self,flag):
            self.flag = flag

        def __contains__(self, item):
            return (self.flag&item)>0
        @property
        def get_flags(self):
            flags = []
            for name, val in vars(self.__class__).items():
                if name.isupper():
                    if (self.flag & val) > 0:
                        flags.append(name)
            return flags

        def __repr__(self):
            return "<Flags value:{0.flag}  {0.get_flags}>".format(self)


    def __init__(self):
        super().__init__()
        self.baseHeaderOffset = 0
        self.nameOffset = 0
        self.fps = 0.0
        self.flags = self.STUDIO
        self.frameCount = 0
        self.movementCount = 0
        self.movementOffset = 0
        self.ikRuleZeroFrameOffset = 0
        self.unused1 = []  # 5 ints
        self.animBlock = 0
        self.animOffset = 0
        self.ikRuleCount = 0
        self.ikRuleOffset = 0
        self.animblockIkRuleOffset = 0
        self.localHierarchyCount = 0
        self.localHierarchyOffset = 0
        self.sectionOffset = 0
        self.sectionFrameCount = 0
        self.spanFrameCount = 0
        self.spanCount = 0
        self.spanOffset = 0
        self.spanStallTime = 0.0
        self.theSectionsOfAnimations = []  # type: List[List[SourceMdlAnimation]]
        self.theAniFrameAnim = SourceAniFrameAnim()
        self.theIkRules = SourceMdlIkRule()
        self.theSections = []  # type: List[SourceMdlAnimationSection]
        self.theMovements = []  # type: List[SourceMdlMovement]
        self.theLocalHierarchies = []  # type: List[SourceMdlLocalHierarchy]
        self.theAnimIsLinkedToSequence = False
        self.theLinkedSequences = False
        self.size = 100
        self.fileOffsetStart2 = -1
        self.fileOffsetEnd2 = -1
        self.entry = -1

    def read(self, reader: ByteIO, MDL: SourceMdlFileData):
        entry = reader.tell()
        self.entry = entry
        self.baseHeaderOffset = reader.read_int32()
        self.nameOffset = reader.read_int32()
        self.theName = reader.read_from_offset(entry + self.nameOffset, reader.read_ascii_string)
        self.fps = reader.read_float()
        self.flags = self.STUDIO(reader.read_uint32())
        self.frameCount = reader.read_uint32()
        self.movementCount = reader.read_uint32()
        self.movementOffset = reader.read_uint32()

        self.unused1 = [reader.read_uint32() for _ in range(6)]
        self.animBlock = reader.read_uint32()
        self.animOffset = reader.read_uint32()


        self.ikRuleCount = reader.read_uint32()
        self.ikRuleOffset = reader.read_uint32()
        self.animblockIkRuleOffset = reader.read_uint32()
        self.localHierarchyCount = reader.read_uint32()
        self.localHierarchyOffset = reader.read_uint32()


        self.sectionOffset = reader.read_uint32()
        self.sectionFrameCount = reader.read_uint32()

        self.spanFrameCount = reader.read_uint16()
        self.spanCount = reader.read_uint16()
        self.spanOffset = reader.read_uint32()
        self.spanStallTime = reader.read_float()
        self.fileOffsetStart2 = entry + self.spanOffset
        self.fileOffsetEnd2 = entry + self.spanOffset-1
        if self.spanFrameCount!=0 or self.spanCount!=0 or self.spanOffset!=0 or self.spanStallTime!=0:
            for bone_index in range(len(MDL.bones)):
                bone = MDL.bones[bone_index] #type: SourceMdlBone
                if bone.flags & SourceMdlBone.BONE_HAS_SAVEFRAME_POS:
                    self.fileOffsetEnd2 += self.spanCount * 6
                if bone.flags & SourceMdlBone.BONE_HAS_SAVEFRAME_ROT:
                    self.fileOffsetEnd2 += self.spanCount * 8




        return self

    def __repr__(self):
        return "<AnimationDesc49 name:{0.theName} fps:{0.fps} frames:{0.frameCount} sectionFrameCount count:{0.sectionFrameCount}>".format(
            self)

class SourceMdlSequenceDesc:
    def __init__(self):
        self.baseHeaderOffset = 0
        self.nameOffset = 0
        self.activityNameOffset = 0

        #    int                    flags;        // looping/non-looping flags
        self.flags = 0

        #    int                    activity;    // initialized at loadtime to game DLL values
        self.activity = 0
        #    int                    actweight;
        self.activityWeight = 0

        #    int                    numevents;
        self.eventCount = 0
        #    int                    eventindex;
        #    inline mstudioevent_t *pEvent( int i ) const { Assert( i >= 0 && i < numevents); return (mstudioevent_t *)(((byte *)this) + eventindex) + i; };
        self.eventOffset = 0

        #    Vector                bbmin;        // per sequence bounding box
        self.bbMin = SourceVector()
        #    Vector                bbmax;
        self.bbMax = SourceVector()

        #    int                    numblends;
        self.blendCount = 0

        #    // Index into array of shorts which is groupsize[0] x groupsize[1] in length
        #    int                    animindexindex;
        self.animIndexOffset = 0

        #    int                    movementindex;    // [blend] float array for blended movement
        self.movementIndex = 0
        #    int                    groupsize[2];
        self.groupSize = []
        #    int                    paramindex[2];    // X, Y, Z, XR, YR, ZR
        self.paramIndex = []
        #    float                paramstart[2];    // local (0..1) starting value
        self.paramStart = []
        #    float                paramend[2];    // local (0..1) ending value
        self.paramEnd = []
        #    int                    paramparent;
        self.paramParent = 0

        #    float                fadeintime;        // ideal cross fate in time (0.2 default)
        self.fadeInTime = 0.0
        #    float                fadeouttime;    // ideal cross fade out time (0.2 default)
        self.fadeOutTime = 0.0

        #    int                    localentrynode;        // transition node at entry
        self.localEntryNodeIndex = 0
        #    int                    localexitnode;        // transition node at exit
        self.localExitNodeIndex = 0
        #    int                    nodeflags;        // transition rules
        self.nodeFlags = 0

        #    float                entryphase;        // used to match entry gait
        self.entryPhase = 0.0
        #    float                exitphase;        // used to match exit gait
        self.exitPhase = 0.0

        #    float                lastframe;        // frame that should generation EndOfSequence
        self.lastFrame = 0.0

        #    int                    nextseq;        // auto advancing sequences
        self.nextSeq = 0
        #    int                    pose;            // index of delta animation between end and nextseq
        self.pose = 0

        #    int                    numikrules;
        self.ikRuleCount = 0

        #    int                    numautolayers;    //
        self.autoLayerCount = 0
        #    int                    autolayerindex;
        #    inline mstudioautolayer_t *pAutolayer( int i ) const { Assert( i >= 0 && i < numautolayers); return (mstudioautolayer_t *)(((byte *)this) + autolayerindex) + i; };
        self.autoLayerOffset = 0

        #    int                    weightlistindex;
        self.weightOffset = 0
        #    inline float        *pBoneweight( int i ) const { return ((float *)(((byte *)this) + weightlistindex) + i); };

        #    // FIXME: make this 2D instead of 2x1D arrays
        #    int                    posekeyindex;
        self.poseKeyOffset = 0
        #    float                *pPoseKey( int iParam, int iAnim ) const { return (float *)(((byte *)this) + posekeyindex) + iParam * groupsize[0] + iAnim; }

        #    int                    numiklocks;
        self.ikLockCount = 0
        #    int                    iklockindex;
        #    inline mstudioiklock_t *pIKLock( int i ) const { Assert( i >= 0 && i < numiklocks); return (mstudioiklock_t *)(((byte *)this) + iklockindex) + i; };
        self.ikLockOffset = 0

        #    // Key values
        #    int                    keyvalueindex;
        self.keyValueOffset = 0
        #    int                    keyvaluesize;
        #    inline const char * KeyValueText( void ) const { return keyvaluesize != 0 ? ((char *)this) + keyvalueindex : NULL; }
        self.keyValueSize = 0

        #    int                    cycleposeindex;        // index of pose parameter to use as cycle index
        self.cyclePoseIndex = 0

        #    int                    unused[7];        // remove/add as appropriate (grow back to 8 ints on version change!)
        #======
        #FROM: VERSION 49
        #    int                    activitymodifierindex;
        #    int                    numactivitymodifiers;
        #    inline mstudioactivitymodifier_t *pActivityModifier( int i ) const { Assert( i >= 0 && i < numactivitymodifiers); return activitymodifierindex != 0 ? (mstudioactivitymodifier_t *)(((byte *)this) + activitymodifierindex) + i : NULL; };
        #    int                    unused[5];        // remove/add as appropriate (grow back to 8 ints on version change!)
        self.activityModifierOffset = 0
        self.activityModifierCount = 0
        self.unused = []


        self.theName = ""
        self.theActivityName = ""
        self.thePoseKeys = []
        self.theEvents = []
        self.theAutoLayers = []
        self.theIkLocks = []
        #NOTE: In the file, a bone weight is a 32-bit float, i.e. a Single, but is stored as Double for better writing to file.
        self.theBoneWeights = []
        self.theWeightListIndex = 0
        self.theAnimDescIndexes = []
        self.theKeyValues = ""
        self.theActivityModifiers = []
        self.theBoneWeightsAreDefault = []

    def read(self,reader:ByteIO,mdl:SourceMdlFileData):
        entry = reader.tell()
        self.baseHeaderOffset = reader.read_int32()
        self.nameOffset = reader.read_uint32()
        self.theName = reader.read_from_offset(entry+self.nameOffset,reader.read_ascii_string)
        self.activityNameOffset = reader.read_uint32()
        self.theActivityName = reader.read_from_offset(entry+self.activityNameOffset,reader.read_ascii_string)
        self.flags = reader.read_uint32()
        self.activity = reader.read_int32()
        self.activityWeight = reader.read_uint32()
        self.eventCount = reader.read_uint32()
        self.eventOffset = reader.read_uint32()
        self.bbMin.read(reader)
        self.bbMax.read(reader)
        self.blendCount = reader.read_uint32()
        self.animIndexOffset = reader.read_uint32()
        self.movementIndex = reader.read_uint32()
        self.groupSize = [reader.read_uint32() for _ in range(2)]
        self.paramIndex = [reader.read_int32() for _ in range(2)]
        self.paramStart = [reader.read_uint32() for _ in range(2)]
        self.paramEnd = [reader.read_uint32() for _ in range(2)]
        self.paramParent = reader.read_uint32()
        self.fadeInTime = reader.read_float()
        self.fadeOutTime = reader.read_float()
        self.localEntryNodeIndex = reader.read_uint32()
        self.localExitNodeIndex = reader.read_uint32()
        self.nodeFlags = reader.read_uint32()
        self.entryPhase = reader.read_float()
        self.exitPhase = reader.read_float()
        self.lastFrame = reader.read_float()
        self.nextSeq = reader.read_uint32()
        self.pose = reader.read_uint32()

        self.ikRuleCount = reader.read_uint32()
        self.autoLayerCount = reader.read_uint32()
        self.autoLayerOffset = reader.read_uint32()
        self.weightOffset = reader.read_uint32()
        self.poseKeyOffset = reader.read_uint32()

        self.ikLockCount = reader.read_uint32()
        self.ikLockOffset = reader.read_uint32()
        self.keyValueOffset = reader.read_uint32()
        self.keyValueSize = reader.read_uint32()
        self.cyclePoseIndex = reader.read_uint32()
        if mdl.version == 49:
            self.activityModifierOffset = reader.read_int32()
            self.activityModifierCount = reader.read_uint32()
            self.unused = [reader.read_uint32() for _ in range(5)]
        else:
            self.unused = [reader.read_uint32() for _ in range(7)]

        if self.groupSize[0] > 1 and self.groupSize[1] > 1 and self.poseKeyOffset !=0:
            with reader.save_current_pos():
                reader.seek(entry+self.poseKeyOffset)
                for _ in range(self.groupSize[0]+self.groupSize[1]):
                    self.thePoseKeys.append(reader.read_float())
        if self.eventCount > 0 and self.eventOffset!=0:
            with reader.save_current_pos():
                reader.seek(entry+self.eventOffset)
                for _ in range(self.eventCount):
                    self.theEvents.append(SourceMdlEvent().read(reader))


        return self


class SourceMdlEvent:
    NEW_EVENT_STYLE = 1 << 10

    def __init__(self):
        self.cycle = 0
        self.eventIndex = 0
        self.eventType = 0
        self.options = [] #64
        self.nameOffset = 0
        self.theName = ''

    def read(self,reader:ByteIO):
        entry = reader.tell()
        self.cycle = reader.read_float()
        self.eventIndex = reader.read_uint32()
        self.eventType = reader.read_uint32()
        self.options = [reader.read_uint8() for _ in range(64)]
        self.nameOffset = reader.read_uint32()
        if self.nameOffset:
            self.theName = reader.read_from_offset(self.nameOffset+entry,reader.read_ascii_string)
        else:
            self.theName = str(self.eventIndex)
        return self




