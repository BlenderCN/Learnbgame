# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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

import math

from .flags import *

#
#   Master class
#


class CConstraint:
    def __init__(self, type, name, flags, inf):
        self.constraint = None
        self.name = name
        self.type = type
        self.influence = inf
        self.active = (flags & C_ACT == 0)
        self.expanded = (flags & C_EXP != 0)

        ow = flags & C_OW_MASK
        if ow == 0:
            self.ownsp = 'WORLD'
        elif ow == C_OW_LOCAL:
            self.ownsp = 'LOCAL'
        elif ow == C_OW_LOCPAR:
            self.ownsp = 'LOCAL_WITH_PARENT'
        elif ow == C_OW_POSE:
            self.ownsp = 'POSE'

        tg = flags & C_TG_MASK
        if tg == 0:
            self.targsp = 'WORLD'
        elif tg == C_TG_LOCAL:
            self.targsp = 'LOCAL'
        elif tg == C_TG_LOCPAR:
            self.targsp = 'LOCAL_WITH_PARENT'
        elif tg == C_TG_POSE:
            self.targsp = 'POSE'


    def update(self, parser, bone):
        return
        raise NameError("Unknown constraint: bone %s cns %s type %s" % (bone.name, self.name, self.type))


    def __repr__(self):
        return ("<CConstraint %s %s>" % (self.name, self.type))


    def build(self, pb, rig, parser):
        cns = self.constraint = pb.constraints.new(self.type)
        cns.name = self.name
        cns.influence = self.influence
        cns.active = self.active
        cns.show_expanded = self.expanded
        cns.target_space = self.targsp
        cns.owner_space = self.ownsp
        return cns

#
#   Constraint subclasses
#

class CIkConstraint(CConstraint):
    def __init__(self, flags, inf, data, lockLoc, lockRot):
        CConstraint.__init__(self, "IK", data[0], flags, inf)
        self.subtar = data[1]
        self.chainlen = data[2]
        self.pole = data[3]
        if self.pole:
            (self.angle, self.ptar) = self.pole
        else:
            (self.angle, self.ptar) = (0, None)
        (self.useLoc, self.useRot, self.useStretch) = data[4]
        if len(data) > 5:
            self.useTail = data[5]
        else:
            self.useTail = True
        self.lockLoc = lockLoc
        self.lockRot = lockRot
        (lockRotX, lockRotY, lockRotZ) = lockRot

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.subtarget = self.subtar
        cns.use_tail = self.useTail

        #self.pos_lock Array 1 1 1
        #self.rot_lock Array 1 1 1
        cns.reference_axis = 'BONE'
        cns.chain_count =  self.chainlen
        cns.ik_type = 'COPY_POSE'
        cns.iterations = 500
        cns.limit_mode = 'LIMITDIST_INSIDE'
        cns.orient_weight = 1

        if self.pole:
            cns.pole_angle = self.angle*D
            cns.pole_subtarget = self.ptar
            cns.pole_target = rig

        cns.use_location = self.useLoc
        cns.use_rotation = self.useRot
        cns.use_stretch = self.useStretch
        cns.weight = 1

    def update(self, parser, bone):
        if self.chainlen == 1:
            target = parser.bones[self.subtar]
            head = bone.getHead()
            goal = target.getHead()
            vec = goal - head
            dist = math.sqrt(vec.dot(vec))
            goal = head + vec*(bone.length/dist)
            bone.stretchTo(goal, False)

            if self.ptar:
                pole = parser.bones[self.ptar].getHead()
                bone.poleTargetCorrect(head, goal, pole, self.angle)
        else:
            raise NameError("IK chainlen %d %s" % (self.chainlen, bone.name))


class CActionConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "ACTION", data[0], flags, inf)
        self.action = data[1]
        self.subtar = data[2]
        self.channel = data[3]
        (self.sframe, self.eframe) = data[4]
        (self.amin, self.amax) = data[5]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        scale = parser.scale
        cns.target = rig
        cns.action = self.action
        cns.frame_start = self.sframe
        cns.frame_end = self.eframe
        if channel[0:3] == 'LOC':
            cns.maximum = self.amax*scale
            cns.minimum = self.amin*scale
        else:
            cns.maximum = self.amax
            cns.minimum = self.amin
        cns.subtarget = self.subtar
        cns.transform_channel = self.channel


class CCopyRotConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "COPY_ROTATION", data[0], flags, inf)
        self.subtar = data[1]
        self.use = data[2]
        self.invert = data[3]
        self.useOffs = data[4]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.use_x,cns.use_y,cns.use_z = self.use
        cns.invert_x,cns.invert_y,cns.invert_z = self.invert
        if isinstance(self.subtar, tuple):
            bname1,bname2 = self.subtar
            if bname1 in rig.data.bones.keys():
                cns.subtarget = bname1
            else:
                cns.subtarget = bname2
        else:
            cns.subtarget = self.subtar
        cns.use_offset = self.useOffs


class CCopyLocConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "COPY_LOCATION", data[0], flags, inf)
        self.subtar = data[1]
        self.use = data[2]
        self.invert = data[3]
        self.head_tail = data[4]
        self.useOffs = data[5]


    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.use_x,cns.use_y,cns.use_z = self.use
        cns.invert_x,cns.invert_y,cns.invert_z = self.invert
        cns.head_tail = self.head_tail
        cns.subtarget = self.subtar
        cns.use_offset = self.useOffs


class CCopyScaleConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "COPY_SCALE", data[0], flags, inf)
        self.subtar = data[1]
        self.use = data[2]
        self.useOffs = data[3]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.use_x,cns.use_y,cns.use_z = self.use
        cns.subtarget = self.subtar
        cns.use_offset = self.useOffs


class CCopyTransConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "COPY_TRANSFORMS", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.head_tail = self.head_tail
        cns.subtarget = self.subtar


class CLimitRotConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LIMIT_ROTATION", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.usex, self.usey, self.usez) = data[2]
        self.ltra = (flags & C_LTRA != 0)

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.use_transform_limit = self.ltra
        cns.max_x = self.xmax*D
        cns.max_y = self.ymax*D
        cns.max_z = self.zmax*D
        cns.min_x = self.xmin*D
        cns.min_y = self.ymin*D
        cns.min_z = self.zmin*D
        cns.use_limit_x = self.usex
        cns.use_limit_y = self.usey
        cns.use_limit_z = self.usez


class CLimitLocConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LIMIT_LOCATION", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.useminx, self.usemaxx, self.useminy, self.usemaxy, self.useminz, self.usemaxz) = data[2]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        scale = parser.scale

        cns.use_transform_limit = True
        cns.max_x = self.xmax*scale
        cns.max_y = self.ymax*scale
        cns.max_z = self.zmax*scale
        cns.min_x = self.xmin*scale
        cns.min_y = self.ymin*scale
        cns.min_z = self.zmin*scale
        cns.use_max_x = self.usemaxx
        cns.use_max_y = self.usemaxy
        cns.use_max_z = self.usemaxz
        cns.use_min_x = self.useminx
        cns.use_min_y = self.useminy
        cns.use_min_z = self.useminz


class CLimitScaleConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LIMIT_SCALE", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.usex, self.usey, self.usez) = data[2]


    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.max_x = self.xmax
        cns.max_y = self.ymax
        cns.max_z = self.zmax
        cns.min_x = self.xmin
        cns.min_y = self.ymin
        cns.min_z = self.zmin
        cns.use_max_x = self.usex
        cns.use_max_y = self.usey
        cns.use_max_z = self.usez
        cns.use_min_x = self.usex
        cns.use_min_y = self.usey
        cns.use_min_z = self.usez


class CTransformConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "TRANSFORM", data[0], flags, inf)
        self.subtar = data[1]
        self.map_from = data[2]
        self.from_min = data[3]
        self.from_max = data[4]
        self.map_to_from = data[5]
        self.map_to = data[6]
        self.to_min = data[7]
        self.to_max = data[8]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.subtarget = self.subtar
        cns.map_from = self.map_from
        cns.from_min_x = self.from_min[0]
        cns.from_min_y = self.from_min[1]
        cns.from_min_z = self.from_min[2]
        cns.from_max_x = self.from_max[0]
        cns.from_max_y = self.from_max[1]
        cns.from_max_z = self.from_max[2]
        cns.map_to = self.map_to
        cns.map_to_x_from = self.map_to_from[0]
        cns.map_to_y_from = self.map_to_from[1]
        cns.map_to_z_from = self.map_to_from[2]
        cns.to_min_x = self.to_min[0]
        cns.to_min_y = self.to_min[1]
        cns.to_min_z = self.to_min[2]
        cns.to_max_x = self.to_max[0]
        cns.to_max_y = self.to_max[1]
        cns.to_max_z = self.to_max[2]


class CDampedTrackConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "DAMPED_TRACK", data[0], flags, inf)
        self.subtar = data[1]
        self.track = data[2]
        self.headtail = data[3]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = parser.name
        cns.subtarget = self.subtar
        cns.head_tail = self.headtail
        cns.track_axis = self.track


class CLockedTrackConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LOCKED_TRACK", data[0], flags, inf)
        self.subtar = data[1]
        self.trackAxis = data[2]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.subtarget = self.subtar
        cns.track_axis = self.trackAxis


class CStretchToConstraint(CConstraint):
    def __init__(self, flags, inf, data, parser=None):
        CConstraint.__init__(self, "STRETCH_TO", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]
        self.bulge = data[3]
        if (parser != None) and (len(data) > 4):
            if isinstance(data[4], tuple):
                start,end = data[4]
                self.rest_length = parser.parser.distance(start,end)
            else:
                self.rest_length = data[4]
        else:
            self.rest_length = None
        if flags & C_VOLXZ:
            self.volume = 'VOLUME_XZX'
        elif flags & C_VOLX:
            self.volume = 'VOLUME_X'
        elif flags & C_VOLZ:
            self.volume = 'VOLUME_Z'
        else:
            self.volume = 'NO_VOLUME'
        if flags & C_PLANEZ:
            self.axis = 'PLANE_Z'
        else:
            self.axis = 'PLANE_X'

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        scale = parser.scale
        cns.target = rig
        cns.bulge = self.bulge
        cns.head_tail = self.head_tail
        cns.keep_axis = self.axis
        cns.subtarget = self.subtar
        cns.volume = self.volume
        if self.rest_length != None:
            cns.rest_length = self.rest_length*scale

    def update(self, parser, bone):
        target = parser.bones[self.subtar]
        goal = (1-self.head_tail)*target.getHead() + self.head_tail*target.getTail()
        bone.stretchTo(goal, True)


class CTrackToConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "TRACK_TO", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]
        self.track_axis = data[3]
        self.up_axis = data[4]
        self.use_target_z = data[5]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.head_tail = self.head_tail
        cns.track_axis = self.track_axis
        cns.up_axis = self.up_axis
        cns.subtarget = self.subtar
        cns.use_target_z = self.use_target_z


class CLimitDistConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LIMIT_DISTANCE", data[0], flags, inf)
        self.subtar = data[1]
        self.limit_mode = data[2]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.limit_mode = self.limit_mode
        cns.subtarget = self.subtar


class CChildOfConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "CHILD_OF", data[0], flags, inf)
        self.subtar = data[1]
        (self.locx, self.locy, self.locz) = data[2]
        (self.rotx, self.roty, self.rotz) = data[3]
        (self.scalex, self.scaley, self.scalez) = data[4]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.subtarget = self.subtar
        cns.use_location_x = self.locx
        cns.use_location_y = self.locy
        cns.use_location_z = self.locz
        cns.use_rotation_x = self.rotx
        cns.use_rotation_y = self.roty
        cns.use_rotation_z = self.rotz
        cns.use_scale_x = self.scalex
        cns.use_scale_y = self.scaley
        cns.use_scale_z = self.scalez


class CSplineIkConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "SPLINE_IK", data[0], flags, inf)
        self.target = data[1]
        self.count = data[2]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.chain_count = self.count
        cns.use_chain_offset = False
        cns.use_curve_radius = True
        cns.use_even_divisions = False
        cns.use_y_stretch = True
        cns.xz_scale_mode = None


class CFloorConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "FLOOR", data[0], flags, inf)
        self.subtar = data[1]
        self.floor_location = data[2]
        self.offset = data[3]
        self.use_rotation = data[4]
        self.use_sticky = data[5]

    def build(self, pb, rig, parser):
        cns = CConstraint.build(self, pb, rig, parser)
        cns.target = rig
        cns.floor_location = self.floor_location
        cns.offset= self.offset
        cns.subtarget = self.subtar
        cns.use_rotation = self.use_rotation
        cns.use_sticky = self.use_sticky


def addConstraint(cdef, lockLoc=(False,False,False), lockRot=(False,False,False)):
    (type, flags, inf, data) = cdef
    if type == 'IK':
        return CIkConstraint(flags, inf, data, lockLoc, lockRot)
    elif type == 'Action':
        return CActionConstraint(flags, inf, data)
    elif type == 'CopyRot':
        return CCopyRotConstraint(flags, inf, data)
    elif type == 'CopyLoc':
        return CCopyLocConstraint(flags, inf, data)
    elif type == 'CopyScale':
        return CCopyScaleConstraint(flags, inf, data)
    elif type == 'CopyTrans':
        return CCopyTransConstraint(flags, inf, data)
    elif type == 'LimitRot':
        return CLimitRotConstraint(flags, inf, data)
    elif type == 'LimitLoc':
        return CLimitLocConstraint(flags, inf, data)
    elif type == 'LimitScale':
        return CLimitScaleConstraint(flags, inf, data)
    elif type == 'Transform':
        return CTransformConstraint(flags, inf, data)
    elif type == 'LockedTrack':
        return CLockedTrackConstraint(flags, inf, data)
    elif type == 'DampedTrack':
        return CDampedTrackConstraint(flags, inf, data)
    elif type == 'StretchTo':
        return CStretchToConstraint(flags, inf, data)
    elif type == 'TrackTo':
        return CTrackToConstraint(flags, inf, data)
    elif type == 'LimitDist':
        return CLimitDistConstraint(flags, inf, data)
    elif type == 'ChildOf':
        return CChildOfConstraint(flags, inf, data)
    elif type == 'SplineIK':
        return CSplineIkConstraint(flags, inf, data)
    elif type == 'Floor':
        return CFloorConstraint(flags, inf, data)
    else:
        raise RuntimeError("Unknown constraint type %s" % type)




