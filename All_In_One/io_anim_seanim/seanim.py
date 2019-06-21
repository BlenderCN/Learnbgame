import time
import struct

# <pep8 compliant>

LOG_READ_TIME = False
LOG_WRITE_TIME = False

LOG_ANIM_HEADER = False
LOG_ANIM_BONES = False
LOG_ANIM_BONE_MODIFIERS = False
LOG_ANIM_BONES_KEYS = False
LOG_ANIM_NOTES = False


def enum(**enums):
    return type('Enum', (), enums)


SEANIM_TYPE = enum(
    SEANIM_TYPE_ABSOLUTE=0,
    SEANIM_TYPE_ADDITIVE=1,
    SEANIM_TYPE_RELATIVE=2,
    SEANIM_TYPE_DELTA=3)

SEANIM_PRESENCE_FLAGS = enum(
    # These describe what type of keyframe data is present for the bones
    SEANIM_BONE_LOC=1 << 0,
    SEANIM_BONE_ROT=1 << 1,
    SEANIM_BONE_SCALE=1 << 2,
    # If any of the above flags are set, then bone keyframe data is present,
    # thus this comparing against this mask will return true
    SEANIM_PRESENCE_BONE=1 << 0 | 1 << 1 | 1 << 2,
    SEANIM_PRESENCE_NOTE=1 << 6,  # The file contains notetrack data
    SEANIM_PRESENCE_CUSTOM=1 << 7,  # The file contains a custom data block
)


SEANIM_PROPERTY_FLAGS = enum(
    SEANIM_PRECISION_HIGH=1 << 0)

SEANIM_FLAGS = enum(
    SEANIM_LOOPED=1 << 0)


class Info(object):
    __slots__ = ('version', 'magic')

    def __init__(self, file=None):
        self.version = 1
        self.magic = b'SEAnim'
        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = file.read(8)
        data = struct.unpack('6ch', bytes)

        magic = b''
        for i in range(6):
            magic += data[i]

        version = data[6]

        assert magic == self.magic
        assert version == self.version

    def save(self, file):
        bytes = self.magic
        bytes += struct.pack('h', self.version)
        file.write(bytes)


class Header(object):
    __slots__ = (
        'animType', 'animFlags',
        'dataPresenceFlags', 'dataPropertyFlags',
        'framerate', 'frameCount',
        'boneCount', 'boneAnimModifierCount',
        'noteCount'
    )

    def __init__(self, file=None):
        self.animType = SEANIM_TYPE.SEANIM_TYPE_RELATIVE  # Relative is default
        self.animFlags = 0x0

        self.dataPresenceFlags = 0x0
        self.dataPropertyFlags = 0x0

        self.framerate = 0
        self.frameCount = 0

        self.boneCount = 0
        self.boneAnimModifierCount = 0

        self.noteCount = 0

        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = file.read(2)
        data = struct.unpack('h', bytes)

        headerSize = data[0]
        bytes = file.read(headerSize - 2)
        # = prefix tell is to ignore C struct packing rules
        data = struct.unpack('=6BfII4BI', bytes)

        self.animType = data[0]
        self.animFlags = data[1]
        self.dataPresenceFlags = data[2]
        self.dataPropertyFlags = data[3]
        # reserved = data[4]
        # reserved = data[5]
        self.framerate = data[6]
        self.frameCount = data[7]
        self.boneCount = data[8]
        self.boneAnimModifierCount = data[9]
        # reserved = data[10]
        # reserved = data[11]
        # reserved = data[12]
        self.noteCount = data[13]

    def save(self, file):
        bytes = struct.pack('=6BfII4BI',
                            self.animType, self.animFlags,
                            self.dataPresenceFlags, self.dataPropertyFlags,
                            0, 0,
                            self.framerate,
                            self.frameCount, self.boneCount,
                            self.boneAnimModifierCount, 0, 0, 0,
                            self.noteCount)

        size = struct.pack('h', len(bytes) + 2)
        file.write(size)
        file.write(bytes)


class Frame_t(object):
    """
    The Frame_t class is only ever used to get the size
    and format character used by frame indices in a given seanim file
    """
    __slots__ = ('size', 'char')

    def __init__(self, header):
        if header.frameCount <= 0xFF:
            self.size = 1
            self.char = 'B'
        elif header.frameCount <= 0xFFFF:
            self.size = 2
            self.char = 'H'
        else:  # if header.frameCount <= 0xFFFFFFFF:
            self.size = 4
            self.char = 'I'


class Bone_t(object):
    """
    The Bone_t class is only ever used to get the size
    and format character used by frame indices in a given seanim file
    """
    __slots__ = ('size', 'char')

    def __init__(self, header):
        if header.boneCount <= 0xFF:
            self.size = 1
            self.char = 'B'
        elif header.boneCount <= 0xFFFF:
            self.size = 2
            self.char = 'H'
        else:  # if header.boneCount <= 0xFFFFFFFF:
            self.size = 4
            self.char = 'I'


class Precision_t(object):
    """
    The Precision_t class is only ever used to get the size
    and format character used by vec3_t, quat_t, etc. in a given sanim file
    """
    __slots__ = ('size', 'char')

    def __init__(self, header):
        if (header.dataPropertyFlags &
                SEANIM_PROPERTY_FLAGS.SEANIM_PRECISION_HIGH):
            self.size = 8
            self.char = 'd'
        else:
            self.size = 4
            self.char = 'f'


class KeyFrame(object):
    """
    A small class used for holding keyframe data
    """
    __slots__ = ('frame', 'data')

    def __init__(self, frame, data):
        self.frame = frame
        self.data = data


class Bone(object):
    __slots__ = (
        'name', 'flags',
        'locKeyCount', 'rotKeyCount', 'scaleKeyCount',
        'posKeys', 'rotKeys', 'scaleKeys',
        'useModifier', 'modifier'
    )

    def __init__(self, file=None):
        self.name = ""

        self.flags = 0x0

        self.locKeyCount = 0
        self.rotKeyCount = 0
        self.scaleKeyCount = 0

        self.posKeys = []
        self.rotKeys = []
        self.scaleKeys = []

        self.useModifier = False
        self.modifier = 0

        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.name = bytes.decode("utf-8")

    def loadData(self, file, frame_t, precision_t,
                 useLoc=False, useRot=False, useScale=False):
        # Read the flags for the bone
        bytes = file.read(1)
        data = struct.unpack("B", bytes)
        self.flags = data[0]

        # Load the position keyframes if they are present
        if useLoc:
            bytes = file.read(frame_t.size)
            data = struct.unpack('%c' % frame_t.char, bytes)
            self.locKeyCount = data[0]

            for i in range(self.locKeyCount):
                bytes = file.read(frame_t.size + 3 * precision_t.size)
                data = struct.unpack('=%c3%c' %
                                     (frame_t.char, precision_t.char), bytes)

                frame = data[0]
                pos = (data[1], data[2], data[3])

                self.posKeys.append(KeyFrame(frame, pos))

        # Load the rotation keyframes if they are present
        if useRot:
            bytes = file.read(frame_t.size)
            data = struct.unpack('%c' % frame_t.char, bytes)
            self.rotKeyCount = data[0]

            for i in range(self.rotKeyCount):

                bytes = file.read(frame_t.size + 4 * precision_t.size)
                data = struct.unpack('=%c4%c' %
                                     (frame_t.char, precision_t.char), bytes)

                frame = data[0]
                # Load the quaternion as XYZW
                quat = (data[1], data[2], data[3], data[4])

                self.rotKeys.append(KeyFrame(frame, quat))

        # Load the Scale Keyrames
        if useScale:
            bytes = file.read(frame_t.size)
            data = struct.unpack('%c' % frame_t.char, bytes)
            self.scaleKeyCount = data[0]
            for i in range(self.scaleKeyCount):
                bytes = file.read(frame_t.size + 3 * precision_t.size)
                data = struct.unpack('=%c3%c' %
                                     (frame_t.char, precision_t.char), bytes)

                frame = data[0]
                scale = (data[1], data[2], data[3])

                self.scaleKeys.append(KeyFrame(frame, scale))

    def save(self, file, frame_t, bone_t, precision_t,
             useLoc=False, useRot=False, useScale=False):
        bytes = struct.pack("B", self.flags)
        file.write(bytes)

        if useLoc:
            bytes = struct.pack('%c' % frame_t.char, len(self.posKeys))
            file.write(bytes)

            for i, key in enumerate(self.posKeys):
                bytes = struct.pack('=%c3%c' %
                                    (frame_t.char, precision_t.char),
                                    key.frame,
                                    key.data[0], key.data[1], key.data[2])
                file.write(bytes)

        if useRot:
            bytes = struct.pack('%c' % frame_t.char, len(self.rotKeys))
            file.write(bytes)

            for i, key in enumerate(self.rotKeys):
                bytes = struct.pack('=%c4%c' %
                                    (frame_t.char, precision_t.char),
                                    key.frame,
                                    key.data[0], key.data[1],
                                    key.data[2], key.data[3])
                file.write(bytes)

        if useScale:
            bytes = struct.pack('%c' % frame_t.char, len(self.scaleKeys))
            file.write(bytes)

            for i, key in enumerate(self.scaleKeys):
                bytes = struct.pack('=%c3%c' %
                                    (frame_t.char, precision_t.char),
                                    key.frame,
                                    key.data[0], key.data[1], key.data[2])
                file.write(bytes)


class Note(object):
    __slots__ = ('frame', 'name')

    def __init__(self, file=None, frame_t=None):
        self.frame = -1
        self.name = ""

        if file is not None:
            self.load(file, frame_t)

    def load(self, file, frame_t):
        bytes = file.read(frame_t.size)
        data = struct.unpack('%c' % frame_t.char, bytes)

        self.frame = data[0]

        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.name = bytes.decode("utf-8")

    def save(self, file, frame_t):
        bytes = struct.pack('%c' % frame_t.char, self.frame)
        file.write(bytes)

        bytes = struct.pack('%ds' % (len(self.name) + 1), self.name.encode())
        file.write(bytes)


class Anim(object):
    __slots__ = ('__info', 'info', 'header', 'bones',
                 'boneAnimModifiers', 'notes')

    def __init__(self, path=None):
        self.__info = Info()
        self.header = Header()

        self.bones = []
        self.boneAnimModifiers = []
        self.notes = []

        if path is not None:
            self.load(path)

    # Update the header flags based on the presence of certain keyframe /
    # notetrack data
    def update_metadata(self, high_precision=False, looping=False):
        anim_locKeyCount = 0
        anim_rotKeyCount = 0
        anim_scaleKeyCount = 0

        header = self.header
        header.boneCount = len(self.bones)

        dataPresenceFlags = header.dataPresenceFlags
        dataPropertyFlags = header.dataPropertyFlags

        max_frame_index = 0

        for bone in self.bones:
            bone.locKeyCount = len(bone.posKeys)
            bone.rotKeyCount = len(bone.rotKeys)
            bone.scaleKeyCount = len(bone.scaleKeys)

            anim_locKeyCount += bone.locKeyCount
            anim_rotKeyCount += bone.rotKeyCount
            anim_scaleKeyCount += bone.scaleKeyCount

            for key in bone.posKeys:
                max_frame_index = max(max_frame_index, key.frame)

            for key in bone.rotKeys:
                max_frame_index = max(max_frame_index, key.frame)

            for key in bone.scaleKeys:
                max_frame_index = max(max_frame_index, key.frame)

        if anim_locKeyCount:
            dataPresenceFlags |= SEANIM_PRESENCE_FLAGS.SEANIM_BONE_LOC
        if anim_rotKeyCount:
            dataPresenceFlags |= SEANIM_PRESENCE_FLAGS.SEANIM_BONE_ROT
        if anim_scaleKeyCount:
            dataPresenceFlags |= SEANIM_PRESENCE_FLAGS.SEANIM_BONE_SCALE

        for note in self.notes:
            max_frame_index = max(max_frame_index, note.frame)

        header.noteCount = len(self.notes)

        if header.noteCount:
            dataPresenceFlags |= SEANIM_PRESENCE_FLAGS.SEANIM_PRESENCE_NOTE

        if high_precision:
            dataPropertyFlags |= SEANIM_PROPERTY_FLAGS.SEANIM_PRECISION_HIGH

        if looping:
            header.animFlags |= SEANIM_FLAGS.SEANIM_LOOPED

        header.dataPresenceFlags = dataPresenceFlags
        header.dataPropertyFlags = dataPropertyFlags

        # FrameCount represents the length of the animation in frames
        # and since all animations start at frame 0 - we simply grab
        # the max frame number (from keys / notes / etc.) and add 1 to it
        header.frameCount = max_frame_index + 1

    def load(self, path):
        if LOG_READ_TIME:
            time_start = time.time()
            print("Loading: '%s'" % path)

        try:
            file = open(path, "rb")
        except IOError:
            print("Could not open file for reading:\n %s" % path)
            return

        self.info = Info(file)
        self.header = Header(file)
        self.boneAnimModifiers = []

        # Init the frame_t, bone_t and precision_t info
        frame_t = Frame_t(self.header)
        bone_t = Bone_t(self.header)
        precision_t = Precision_t(self.header)

        dataPresenceFlags = self.header.dataPresenceFlags

        if LOG_ANIM_HEADER:
            print("Magic: %s" % self.info.magic)
            print("Version: %d" % self.info.version)

            print("AnimType: %d" % self.header.animType)
            print("AnimFlags: %d" % self.header.animFlags)
            print("PresenceFlags: %d" % dataPresenceFlags)
            print("PropertyFlags: %d" % self.header.dataPropertyFlags)
            print("FrameRate: %f" % self.header.framerate)
            print("FrameCount: %d" % self.header.frameCount)
            print("BoneCount: %d" % self.header.boneCount)
            print("NoteCount: %d" % self.header.noteCount)
            print("BoneModifierCount: %d" % self.header.boneAnimModifierCount)

            print("Frame_t Size: %d" % frame_t.size)
            print("Frame_t Char: '%s'" % frame_t.char)

        self.bones = []
        if dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_PRESENCE_BONE:
            useLoc = dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_BONE_LOC
            useRot = dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_BONE_ROT
            useScale = (dataPresenceFlags &
                        SEANIM_PRESENCE_FLAGS.SEANIM_BONE_SCALE)

            for i in range(self.header.boneCount):
                if LOG_ANIM_BONES:
                    print("Loading Name for Bone[%d]" % i)
                self.bones.append(Bone(file))

            for i in range(self.header.boneAnimModifierCount):
                bytes = file.read(bone_t.size + 1)
                data = struct.unpack("%cB" % bone_t.char, bytes)
                index = data[0]
                self.bones[index].useModifier = True
                self.bones[index].modifier = data[1]

                self.boneAnimModifiers.append(self.bones[index])

                if LOG_ANIM_BONE_MODIFIERS:
                    print("Loaded Modifier %d for '%s" %
                          (index, self.bones[index].name))

            for i in range(self.header.boneCount):
                if LOG_ANIM_BONES:
                    print("Loading Data For Bone[%d] '%s'" % (
                        i, self.bones[i].name))
                self.bones[i].loadData(
                    file, frame_t, precision_t, useLoc, useRot, useScale)
                if LOG_ANIM_BONES_KEYS:
                    for key in self.bones[i].posKeys:
                        print("%s LOC %d %s" %
                              (self.bones[i].name, key.frame, key.data))
                    for key in self.bones[i].rotKeys:
                        print("%s ROT %d %s" %
                              (self.bones[i].name, key.frame, key.data))
                    for key in self.bones[i].scaleKeys:
                        print("%s SCALE %d %s" %
                              (self.bones[i].name, key.frame, key.data))

        self.notes = []
        if (self.header.dataPresenceFlags &
                SEANIM_PRESENCE_FLAGS.SEANIM_PRESENCE_NOTE):
            for i in range(self.header.noteCount):
                note = Note(file, frame_t)
                self.notes.append(note)
                if LOG_ANIM_NOTES:
                    print("Loaded Note[%d]:" % i)
                    print("  Frame %d: %s" % (note.frame, note.name))

        file.close()

        if LOG_READ_TIME:
            time_end = time.time()
            time_elapsed = time_end - time_start
            print("Done! - Completed in %ss" % time_elapsed)

    def save(self, filepath="", high_precision=False, looping=False):
        if LOG_WRITE_TIME:
            time_start = time.time()
            print("Saving: '%s'" % filepath)

        try:
            file = open(filepath, "wb")
        except IOError:
            print("Could not open file for writing:\n %s" % path)
            return

        # Update the header flags, based on the presence of different keyframe
        # types
        self.update_metadata(high_precision, looping)

        self.__info.save(file)
        self.header.save(file)
        for bone in self.bones:
            bytes = struct.pack(
                '%ds' % (len(bone.name) + 1), bone.name.encode())
            file.write(bytes)

        dataPresenceFlags = self.header.dataPresenceFlags

        useLoc = dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_BONE_LOC
        useRot = dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_BONE_ROT
        useScale = dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_BONE_SCALE

        frame_t = Frame_t(self.header)
        bone_t = Bone_t(self.header)
        precision_t = Precision_t(self.header)

        for index, bone in enumerate(self.bones):
            if bone.useModifier:
                bytes = struct.pack('%cB' % bone_t.char, index, bone.modifier)
                file.write(bytes)

        for bone in self.bones:
            bone.save(file, frame_t, bone_t, precision_t,
                      useLoc, useRot, useScale)

        if dataPresenceFlags & SEANIM_PRESENCE_FLAGS.SEANIM_PRESENCE_NOTE:
            for note in self.notes:
                note.save(file, frame_t)

        file.close()

        if LOG_WRITE_TIME:
            time_end = time.time()
            time_elapsed = time_end - time_start
            print("Done! - Completed in %ss" % time_elapsed)
