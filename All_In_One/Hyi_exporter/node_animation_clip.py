import array
import struct

class NodeAnimationClip:
    def __init__(self, name):
        NODE_ANIMATION_CLIP = 4
        self.buffer = bytearray(4)
        self.buffer[0] = NODE_ANIMATION_CLIP
        self.name = name
        self.tracks = []

    def addTrack(self, track):
        self.tracks.append(track)

    def serialize(self):
        namebuf = self.name.encode('utf-8')
        self.buffer.extend(struct.pack("<H", len(namebuf)))
        self.buffer.extend(namebuf)
        for track in self.tracks:
            self.buffer.extend(track.serialize())
        nodeLength = len(self.buffer)
        buf = struct.pack("<I",nodeLength)
        self.buffer[1] = buf[0]
        self.buffer[2] = buf[1]
        self.buffer[3] = buf[2]
        return self.buffer
