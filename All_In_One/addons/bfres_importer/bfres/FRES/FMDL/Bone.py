import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryStruct.Flags import Flags
from bfres.BinaryStruct.Vector import Vec3f, Vec4f
from bfres.BinaryFile import BinaryFile
from bfres.FRES.FresObject import FresObject
from bfres.FRES.Dict import Dict
from .Attribute import Attribute, AttrStruct
from .Buffer    import Buffer
from .FVTX      import FVTX
from .LOD       import LOD
from .Vertex    import Vertex
import struct
import math
import mathutils # Blender


class BoneStruct(BinaryStruct):
    """The bone data in the file."""
    fields = (
        String('name'),
        ('5I', 'unk04'),
        ('H',  'bone_idx'),
        ('h',  'parent_idx'),
        ('h',  'smooth_mtx_idx'),
        ('h',  'rigid_mtx_idx'),
        ('h',  'billboard_idx'),
        ('H',  'udata_count'),
        Flags('flags', {
            'VISIBLE': 0x00000001,
            'EULER':   0x00001000, # use euler rotn, not quaternion
            'BB_CHILD':0x00010000, # child billboarding
            'BB_WORLD_VEC':0x00020000, # World View Vector.
                # The Z axis is parallel to the camera.
            'BB_WORLD_POINT':0x00030000, # World View Point.
                # The Z axis is equal to the direction the camera
                # is pointing to.
            'BB_SCREEN_VEC':0x00040000, # Screen View Vector.
                # The Z axis is parallel to the camera, the Y axis is
                # equal to the up vector of the camera.
            'BB_SCREEN_POINT':0x00050000, # Screen View Point.
                # The Z axis is equal to the direction the camera is
                # pointing to, the Y axis is equal to the up vector of
                # the camera.
            'BB_Y_VEC':0x00060000, # Y-Axis View Vector.
                # The Z axis has been made parallel to the camera view
                # by rotating the Y axis.
            'BB_Y_POINT':0x00070000, # Y-Axis View Point.
                # The Z axis has been made equal to the direction
                # the camera is pointing to by rotating the Y axis.
            'SEG_SCALE_COMPENSATE':0x00800000, # Segment scale
                # compensation. Set for bones scaled in Maya whose
                # scale is not applied to child bones.
            'UNIFORM_SCALE': 0x01000000, # Scale uniformly.
            'SCALE_VOL_1':   0x02000000, # Scale volume by 1.
            'NO_ROTATION':   0x04000000,
            'NO_TRANSLATION':0x08000000,
            # same as previous but for hierarchy of bones
            'GRP_UNIFORM_SCALE': 0x10000000,
            'GRP_SCALE_VOL_1':   0x20000000,
            'GRP_NO_ROTATION':   0x40000000,
            'GRP_NO_TRANSLATION':0x80000000,
        }),
        Vec3f('scale'),
        Vec4f('rot'),
        Vec3f('pos'),
    )
    size = 80


class Bone(FresObject):
    """A bone in an FSKL."""
    _struct = BoneStruct

    def __init__(self, fres):
        self.fres   = fres
        self.offset = None
        self.parent = None # to be set by FSKL on read


    def __str__(self):
        return "<Bone(@%s) at 0x%x>" %(
            '?' if self.offset is None else hex(self.offset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        flags = []
        for name in sorted(self.flags.keys()):
            if name != '_raw':
                val = self.flags[name]
                if val: flags.append(name)
        flags = ', '.join(flags)
        rotD  = ' (%3d, %3d, %3d, %3d°)' % tuple(map(math.degrees, self.rot))

        res  = []
        res.append("Bone #%3d '%s':" % (self.bone_idx, self.name))
        res.append("Position: %#5.2f, %#5.2f, %#5.2f" % tuple(self.pos))
        res.append("Rotation: %#5.2f, %#5.2f, %#5.2f, %#5.2f" % tuple(self.rot) + rotD)
        res.append("Scale:    %#5.2f, %#5.2f, %#5.2f" % tuple(self.scale))
        res.append("Unk04: 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X" %
            self.unk04)
        res.append("Parent     Idx: %3d" % self.parent_idx)
        res.append("Smooth Mtx Idx: %3d" % self.smooth_mtx_idx)
        res.append("Rigid  Mtx Idx: %3d" % self.rigid_mtx_idx)
        res.append("Billboard  Idx: %3d" % self.billboard_idx)
        res.append("Udata count:    %3d" % self.udata_count)
        res.append("Flags: %s" % flags)
        #res = ', '.join(res)
        return '\n'.join(res).replace('\n', '\n  ')
        #return res


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        #log.debug("Reading Bone from 0x%06X", offset)
        self.offset = offset
        data = self.fres.read(BoneStruct(), offset)

        self.name           = data['name']
        self.pos            = data['pos']
        self.rot            = data['rot']
        self.scale          = data['scale']
        self.unk04          = data['unk04']
        self.bone_idx       = data['bone_idx']
        self.parent_idx     = data['parent_idx']
        self.smooth_mtx_idx = data['smooth_mtx_idx']
        self.rigid_mtx_idx  = data['rigid_mtx_idx']
        self.billboard_idx  = data['billboard_idx']
        self.udata_count    = data['udata_count']
        self.flags          = data['flags']

        return self


    def computeTransform(self):
        """Compute final transformation matrix."""
        T = self.pos
        S = self.scale
        R = self.rot

        # why have these flags instead of just setting the
        # values to 0/1? WTF Nintendo.
        # they seem to only be set when the values already are
        # 0 (or 1, for scale) anyway.
        #if self.flags['NO_ROTATION']:    R = Vec4(0, 0, 0, 1)
        #if self.flags['NO_TRANSLATION']: T = Vec3(0, 0, 0)
        #if self.flags['SCALE_VOL_1']:    S = Vec3(1, 1, 1)
        if self.flags['SEG_SCALE_COMPENSATE']:
            # apply inverse of parent's scale
            if self.parent:
                S[0] *= 1 / self.parent.scale[0]
                S[1] *= 1 / self.parent.scale[1]
                S[2] *= 1 / self.parent.scale[2]
            else:
                log.warning("Bone '%s' has flag SEG_SCALE_COMPENSATE but no parent", self.name)
        # no idea what "scale uniformly" actually means.
        # XXX billboarding, rigid mtxs, if ever used.

        # Build matrices from these transformations.
        T = mathutils.Matrix.Translation(T).to_4x4().transposed()
        Sm = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()
        Sm[0][0] = S[0]
        Sm[1][1] = S[1]
        Sm[2][2] = S[2]
        S = Sm
        R = self._fromEulerAngles(R).to_matrix().to_4x4().transposed()
        if self.parent:
            P = self.parent.computeTransform()#.to_4x4()
        else:
            P = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()
        M = mathutils.Matrix.Translation((0, 0, 0)).to_4x4()

        # Apply transformations. (order is important!)
        M = M * S
        M = M * R
        M = M * T
        M = M * P

        #log.debug("Final bone transform %s: %s", self.name, M)
        return M


    def _fromAxisAngle(self, axis, angle):
        return mathutils.Quaternion((
            math.cos(angle / 2),
            axis[0] * math.sin(angle / 2),
            axis[1] * math.sin(angle / 2),
            axis[2] * math.sin(angle / 2),
        ))

    def _fromEulerAngles(self, rot):
        x = self._fromAxisAngle((1,0,0), rot[0])
        y = self._fromAxisAngle((0,1,0), rot[1])
        z = self._fromAxisAngle((0,0,1), rot[2])
        #q = x * y * z
        q = z * y * x
        if q.w < 0: q *= -1
        return q
