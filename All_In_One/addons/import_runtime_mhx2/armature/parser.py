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

import os
import math
from mathutils import Vector

from collections import OrderedDict

from .flags import *
from ..utils import *
from .utils import *
from ..hm8 import *
from ..load_json import loadJsonRelative

from . import rig_joints
from . import rig_spine
from . import rig_arm
from . import rig_leg
from . import rig_hand
#from . import rig_bones
from . import rig_face
from . import rig_control
from . import rig_merge
from . import rig_panel
from . import rig_rigify
from . import rerig

#-------------------------------------------------------------------------------
#   Parser base class.
#-------------------------------------------------------------------------------

class Parser:

    def __init__(self, mhHuman, mhSkel, cfg):
        self.config = cfg

        self.defineJointLocations(mhHuman, cfg)

        self.bones = OrderedDict()
        self.locations = {}
        self.terminals = {}
        self.origin = Vector([0,0,0])
        self.normals = {}
        self.headsTails = {}
        self.parents = {}
        self.ikChains = {}
        self.loadedShapes = {}
        self.customShapes = {}
        self.gizmos = {}
        self.constraints = {}
        self.locationLimits = {}
        self.rotationLimits = {}
        self.locks = {}
        self.drivers = []
        self.propDrivers = []
        self.lrPropDrivers = []
        self.boneDrivers = {}

        self.vertexGroupFiles = []
        self.vertexGroups = OrderedDict()

        if cfg.useMhx:
            layers = L_MAIN|L_SPINE|L_LARMFK|L_RARMFK|L_LLEGFK|L_RLEGFK|L_HEAD
            if cfg.useFingers:
                layers |= L_LHANDIK|L_RHANDIK
            else:
                layers |= L_LHANDFK|L_RHANDFK|L_LPALM|L_RPALM|L_TWEAK
            if cfg.useFacePanel:
                layers |= L_PANEL
        elif cfg.useRigify:
            layers = L_MAIN|L_HEAD|L_TWEAK
        else:
            layers = L_MAIN
        self.visibleLayers = layers

        self.objectProps = [("MhxRig", cfg.rigType)]
        self.customProps = []
        self.bbones = {}
        self.poseInfo = {}
        self.master = None
        self.headName = 'head'
        self.root = "hips"

        if cfg.useMhx:
            self.boneGroups = [
                ('Spine', 'THEME01', L_SPINE),
                ('ArmFK.L', 'THEME02', L_LARMFK),
                ('ArmFK.R', 'THEME03', L_RARMFK),
                ('ArmIK.L', 'THEME04', L_LARMIK),
                ('ArmIK.R', 'THEME05', L_RARMIK),
                ('LegFK.L', 'THEME06', L_LLEGFK),
                ('LegFK.R', 'THEME07', L_RLEGFK),
                ('LegIK.L', 'THEME14', L_LLEGIK),
                ('LegIK.R', 'THEME09', L_RLEGIK),
            ]
        else:
            self.boneGroups = []

        self.deformPrefix = ""
        if cfg.useDeformBones or cfg.useDeformNames:
            self.deformPrefix = "DEF-"

        if mhSkel is None:
            self.vertexGroupFiles += ["head", "body", "hand", "joints"]
            self.vertexGroupFiles += ["tights", "skirt", "genitalia", "hair"]

            self.joints = (
                rig_joints.Joints +
                rig_spine.Joints +
                rig_arm.Joints +
                rig_leg.Joints1 +
                rig_leg.Joints2 +
                rig_hand.Joints +
                rig_face.Joints
                )

            self.deformArmature = mergeDicts([
                rig_spine.Armature,
                rig_arm.Armature,
                rig_leg.Armature,
                rig_hand.Armature,
                rig_face.Armature,
            ])
        else:
            amt = mergeDicts([
                rig_spine.Armature,
                rig_arm.Armature,
                rig_leg.Armature,
                rig_hand.Armature,
                rig_face.Armature,
                ])
            self.joints, self.headsTails, self.armature, self.deformArmature = rerig.getJoints(mhSkel, amt)
            self.joints += (
                rig_leg.Joints2 +
                rig_hand.Joints +
                rig_face.Joints
                )

        if cfg.usePenisRig:
            self.joints += rig_spine.PenisJoints
        if cfg.useMhx:
            self.joints += rig_control.Joints
        if cfg.useFacePanel:
            self.joints += rig_panel.Joints

        self.planes = mergeDicts([
            rig_spine.Planes,
            rig_arm.Planes,
            rig_leg.Planes,
            rig_hand.Planes,
            rig_face.Planes,
        ])

        if cfg.useMhx:
            self.planeJoints = rig_control.PlaneJoints
        else:
            self.planeJoints = []

        if mhSkel is None:
            self.headsTails = mergeDicts([
                rig_spine.HeadsTails,
                rig_arm.HeadsTails,
                rig_leg.HeadsTails,
                rig_hand.HeadsTails,
                rig_face.HeadsTails,
            ])
        if cfg.usePenisRig:
            addDict(rig_spine.PenisHeadsTails, self.headsTails)
        if cfg.useMhx:
            addDict(rig_control.HeadsTails, self.headsTails)
            addDict(rig_control.RevFootHeadsTails, self.headsTails)

        if cfg.useFacePanel:
            addDict(rig_panel.HeadsTails, self.headsTails)

        for bname in cfg.terminals.keys():
            parent,offset = cfg.terminals[bname]
            _head,tail = self.headsTails[parent]
            self.headsTails[bname] = (tail, (tail,offset))

        self.headsTailsOrig = dict(self.headsTails)

        if cfg.useConstraints:
            if mhSkel is None:
                self.setConstraints(rig_spine.Constraints)
                self.setConstraints(rig_arm.Constraints)
                self.setConstraints(rig_leg.Constraints)
                self.setConstraints(rig_hand.Constraints)
                self.setConstraints(rig_face.Constraints)
            else:
                self.setConstraints(rerig.Constraints)
                self.setConstraints(rig_face.Constraints)

        if cfg.useRotationLimits:
            addDict(rig_spine.RotationLimits, self.rotationLimits)
            addDict(rig_arm.RotationLimits, self.rotationLimits)
            addDict(rig_hand.RotationLimits, self.rotationLimits)
            addDict(rig_leg.RotationLimits, self.rotationLimits)
            addDict(rig_face.RotationLimits, self.rotationLimits)
            addDict(rig_face.LocationLimits, self.locationLimits)
            addDict(rig_control.RotationLimits, self.rotationLimits)

        if cfg.useLocks:
            addDict(rig_spine.Locks, self.locks)
            addDict(rig_arm.Locks, self.locks)
            addDict(rig_hand.Locks, self.locks)
            addDict(rig_leg.Locks, self.locks)
            addDict(rig_face.Locks, self.locks)
            addDict(rig_control.Locks, self.locks)

        if cfg.useFacePanel:
            addDict(rig_panel.Locks, self.locks)
            addDict(rig_panel.LocationLimits, self.locationLimits)

        if cfg.useCustomShapes:
            addDict(rig_face.CustomShapes, self.customShapes)
            if cfg.useCustomShapes == 'ALL':
                addDict(rig_spine.CustomShapes, self.customShapes)
                addDict(rig_arm.CustomShapes, self.customShapes)
                addDict(rig_leg.CustomShapes, self.customShapes)
                addDict(rig_hand.CustomShapes, self.customShapes)
                addDict(rig_control.CustomShapes, self.customShapes)
        if cfg.useFacePanel:
            addDict(rig_panel.CustomShapes, self.customShapes)

        if cfg.useFingers and cfg.useConstraints:
            self.setConstraints(rig_hand.Constraints)
            self.lrPropDrivers += rig_hand.PropLRDrivers

        if cfg.useMhx:
            # npieces,target,numAfter,followNext
            self.splitBones = {
                "forearm" :     (3, "hand", False, True),
                "shin" :        (3, "foot", False, False),
            }
        elif cfg.useRigify:
            self.joints += rig_rigify.Joints
            addDict(rig_rigify.HeadsTails, self.headsTails)

            self.splitBones = {
                "upper_arm" :   (2, "forearm", False, True),
                "forearm" :     (2, "hand", False, True),
                "thigh" :       (2, "shin", False, True),
                "shin" :        (2, "foot", False, True),

                "thumb.01" :    (2, "thumb.02", True, True),
                "f_index.01" :  (2, "f_index.02", True, True),
                "f_middle.01" : (2, "f_middle.02", True, True),
                "f_ring.01" :   (2, "f_ring.02", True, True),
                "f_pinky.01" :  (2, "f_pinky.02", True, True),
            }
        else:
            self.splitBones = {}


    def createBones(self, mhHuman, mhSkel):
        cfg = self.config

        if mhSkel is None:
            self.addBones(rig_spine.Armature)
            self.addBones(rig_arm.Armature)
            self.addBones(rig_leg.Armature)
            self.addBones(rig_hand.Armature)
            self.addBones(rig_face.Armature)
        else:
            self.addBones(self.armature)
        if cfg.useTerminators:
            self.addBones(rig_spine.TerminatorArmature)
        if cfg.usePenisRig:
            self.addBones(rig_spine.PenisArmature)

        for bname in cfg.terminals.keys():
            pname,_offset = cfg.terminals[bname]
            parent = self.bones[pname]
            self.addBones({bname: (0, pname, 0, parent.layers)})

        if cfg.useMasterBone:
            self.master = 'master'
            self.addBones(rig_control.MasterArmature)

        if cfg.useReverseHip:
            hiphead, hiptail = self.headsTails["hips"]
            self.headsTails["root"] = (hiptail, (hiptail,(0,0,-2)))
            self.headsTails["hips"] = (hiptail, hiphead)
            self.customShapes["hips"] = "GZM_CircleHips"
            self.root = "root"
            root = self.bones["root"] = Bone(self, "root")
            root.type = "Null"
            root.fromInfo((0, None, F_WIR, L_MAIN))
            hips = self.bones["hips"]
            hips.parent = "root"
            hips.conn = False
            hips.lockLocation = (1,1,1)
            spine = self.bones["spine"]
            spine.parent = "root"
            spine.conn = False

        if cfg.useFacePanel:
            self.addBones(rig_panel.Armature)
            addDict(rig_panel.BoneDrivers, self.boneDrivers)

        if cfg.useRigify:
            self.addBones(rig_rigify.Armature)

        if cfg.useHeadControl:
            self.addBones(rig_control.HeadArmature)
            if cfg.useConstraints:
                self.setConstraints(rig_control.HeadConstraints)
                self.propDrivers += rig_control.HeadPropDrivers

        if cfg.useSockets and cfg.useConstraints:
            self.changeParents(rig_control.SocketParents)
            self.addBones(rig_control.SocketArmature)
            self.setConstraints(rig_control.SocketConstraints)
            self.lrPropDrivers += rig_control.SocketPropLRDrivers

        if cfg.useIkLegs and cfg.useConstraints:
            self.addBones(rig_control.RevFootArmature)
            self.setConstraints(rig_control.RevFootConstraints)
            self.addBones(rig_control.MarkerArmature)
            self.lrPropDrivers += rig_control.IkLegPropLRDrivers
            self.addIkChains(rig_leg.Armature, rig_control.IkLegChains)
            self.reparentMarkers(rig_control.LegMarkers)

        if cfg.useIkArms and cfg.useConstraints:
            self.addBones(rig_control.IkArmArmature)
            self.setConstraints(rig_control.IkArmConstraints)
            self.lrPropDrivers += rig_control.IkArmPropLRDrivers
            self.addIkChains(rig_arm.Armature, rig_control.IkArmChains)

        if cfg.useFingers and cfg.useConstraints:
            self.addBones(rig_control.FingerArmature)

        if cfg.useLocks:
            for bname,lock in self.locks.items():
                try:
                    bone = self.bones[bname]
                except KeyError:
                    continue
                bone.lockRotation = lock

        if cfg.useConstraints and cfg.useRotationLimits:
            for bname,limits in self.rotationLimits.items():
                try:
                    bone = self.bones[bname]
                except KeyError:
                    continue
                if bone.lockRotation != (1,1,1):
                    minX,maxX, minY,maxY, minZ,maxZ = limits
                    cns = ("LimitRot", C_LOCAL, 0.8, ["LimitRot", limits, (1,1,1)])
                    self.addConstraint(bname, cns)
                    self.propDrivers.append((bname, "LimitRot", ["RotationLimits"], "x1"))

            for bname,limits in self.locationLimits.items():
                try:
                    bone = self.bones[bname]
                except KeyError:
                    continue
                minX,maxX, minY,maxY, minZ,maxZ = limits
                cns = ("LimitLoc", C_LOCAL, 1, ["LimitLoc", limits, (1,1,1,1,1,1)])
                self.addConstraint(bname, cns)

        if cfg.addConnectingBones:
            extras = []
            for bone in self.bones:
                if bone.parent:
                    head,_ = self.headsTails[bone.name]
                    _,ptail = self.headsTails[bone.parent]
                    if head != ptail:
                        connector = Bone(self, "_"+bone.name)
                        connector.layers = L_HELP
                        connector.parent = bone.parent
                        bone.parent = connector.name
                        extras.append(connector)
                        self.headsTails[connector.name] = (ptail, head)
            for bone in extras:
                self.bones[bone.name] = bone

        if cfg.useCustomShapes:
            addDict(loadJsonRelative("armature/data/mhx/gizmos-face.json"), self.gizmos)
            if cfg.useCustomShapes == 'ALL':
                addDict(loadJsonRelative("armature/data/mhx/gizmos.json"), self.gizmos)
        if cfg.useFacePanel:
            addDict(loadJsonRelative("armature/data/mhx/gizmos-panel.json"), self.gizmos)

        if not AutoWeight:
            if mhSkel is None:
                vgroups = self.readVertexGroupFiles(self.vertexGroupFiles)
            else:
                vgroups = rerig.getVertexGroups(mhHuman, mhSkel)
            addDict(vgroups, self.vertexGroups)


        if cfg.mergeShoulders:
            for bname in ["DEF-deltoid.L", "DEF-deltoid.R"]:
                vgroup = self.vertexGroups[bname]
                self.splitVertexGroup(bname, vgroup)
                del self.vertexGroups[bname]
                del self.bones[bname]

        for flag,mergers in [
            (cfg.mergeShoulders, rig_merge.ShoulderMergers),
            (cfg.mergeHips, rig_merge.HipMergers),
            (cfg.mergeSpine, rig_merge.SpineMergers),
            (cfg.mergeChest, rig_merge.ChestMergers),
            (cfg.mergeNeck, rig_merge.NeckMergers),
            (cfg.mergePalms, rig_merge.PalmMergers),
            (cfg.mergeFingers, rig_merge.FingerMergers),
            (cfg.mergeHead, rig_merge.HeadMergers),
            (cfg.mergeFeet, rig_merge.FeetMergers),
            #(cfg.mergeToes, rig_merge.ToesMergers),
            (cfg.mergePenis, rig_merge.PenisMergers),
            ]:
            if flag:
                self.mergeBones(mergers)

        if not cfg.useConstraints:
            self.mergeBones(rig_merge.ConstraintMergers)

        if cfg.useDeformNames or cfg.useDeformBones:
            if cfg.usePenisRig:
                addDict(rig_spine.PenisArmature, self.deformArmature)
            if cfg.useDeformBones:
                self.addDeformBones()
                #self.renameDeformBones(rig_muscle.Armature)
                #if cfg.useConstraints:
                #    self.renameConstraints(rig_muscle.Constraints)
            self.addDeformVertexGroups(vgroups)

        if cfg.useSplitBones or cfg.useSplitNames:
            if cfg.useSplitBones:
                self.addSplitBones()
            self.addSplitVertexGroups(vgroups)


    def changeParents(self, newParents):
        for bname, parent in newParents.items():
            self.bones[bname].parent = parent


    def getRealBoneName(self, bname, raiseError=True):
        try:
            self.bones[bname]
            return bname
        except KeyError:
            pass

        altname = bname
        if bname[0:4] == "DEF-":
            altname = bname[4:]
        else:
            altname = "DEF-"+bname

        print("Missing bone %s. Trying %s" % (bname, altname))
        try:
            self.bones[altname]
            return altname
        except KeyError:
            pass

        if raiseError:
            print(str(self.bones.keys()))
            raise NameError("Missing %s and %s" % (bname, altname))
        else:
            return bname


    def setup(self, mhHuman, mhSkel):
        cfg = self.config

        self.setupJoints()
        self.setupNormals()
        self.setupPlaneJoints()
        self.createBones(mhHuman, mhSkel)

        for bone in self.bones.values():
            headTail = self.headsTails[bone.name]
            if isinstance(headTail, tuple):
                hname,tname = headTail
                head = self.findLocation(hname)
                tail = self.findLocation(tname)
            elif isinstance(headTail, str):
                xbone = self.bones[headTail]
                head = xbone.head
                tail = xbone.tail
            bone.setBone(head, tail)

        for bone in self.bones.values():
            if isinstance(bone.roll, str):
                if bone.roll[0:5] != "Plane":
                    bone.roll = self.bones[bone.roll].roll
            elif isinstance(bone.roll, Bone):
                bone.roll = bone.roll.roll
            elif isinstance(bone.roll, tuple):
                bname,angle = bone.roll
                bone.roll = self.bones[bname].roll + angle

        if cfg.useCorrectives:
            self.setupRotationBones(rig_control.RotationBones)

        # Rename vertex groups now.
        # Wait with bones until everything is built.

        for bname,nname in cfg.bones.items():
            vgroups = self.vertexGroups
            if bname in vgroups.keys():
                vgroups[nname] = vgroups[bname]
                del vgroups[bname]
            else:
                if self.isDeformName(bname):
                    defbname = bname
                    defnname = nname
                else:
                    defbname = self.deformPrefix + bname
                    defnname = self.deformPrefix + nname
                if (defbname in vgroups.keys() and
                    defbname != defnname):
                    vgroups[defnname] = vgroups[defbname]
                    del vgroups[defbname]


    def isDeformName(self, bname):
        return (bname[0:4] == self.deformPrefix)


    def setupNormals(self):
        self.normals["PlaneYPos"] = Vector((0,0,1))
        self.normals["PlaneYNeg"] = Vector((0,0,-1))
        for plane,joints in self.planes.items():
            j1,j2,j3 = joints
            p1 = self.locations[j1]
            p2 = self.locations[j2]
            p3 = self.locations[j3]
            pvec = getUnitVector(p2-p1)
            yvec = getUnitVector(p3-p2)
            if pvec is None or yvec is None:
                self.normals[plane] = None
            else:
                self.normals[plane] = getUnitVector(yvec.cross(pvec))


    def defineJointLocations(self, mhHuman, cfg):
        self.scale = mhHuman["scale"]
        if cfg.useOffset:
            self.offset = Vector(mhHuman["offset"])
        else:
            self.offset = Vector((0,0,0))

        self.coord = dict(
            [(vn,self.scale*Vector(co) + self.offset)
                for vn,co in enumerate(mhHuman["seed_mesh"]["vertices"])
            ])

        self.jointLocs = {}
        vn0 = FirstJointVert
        for name in JointNames:
            self.jointLocs[name] = self.calcBox(vn0)
            vn0 += 8
        self.jointLocs["ground"] = self.calcBox(NTotalVerts-8)


    def calcBox(self, vn0):
        vsum = Vector((0,0,0))
        for n in range(8):
            vsum += self.coord[vn0+n]
        return vsum/8


    def setupJoints (self):
        """
        Evaluate symbolic expressions for joint locations and store them in self.locations.
        Joint locations are specified symbolically in the *Joints list in the beginning of the
        rig_*.py files (e.g. ArmJoints in rig_arm.py).
        """

        cfg = self.config
        for (key, type, data) in self.joints:
            if type == 'j':
                loc = self.jointLocs[data]
                self.locations[key] = loc
                self.locations[data] = loc
            elif type == 'a':
                vec = Vector((float(data[0]),float(data[1]),float(data[2])))
                self.locations[key] = vec + self.offset
            elif type == 'v':
                v = int(data)
                self.locations[key] = self.coord[v]
            elif type == 'x':
                self.locations[key] = Vector((float(data[0]), float(data[2]), -float(data[1])))
            elif type == 'vo':
                v = int(data[0])
                offset = Vector((float(data[1]), float(data[3]), -float(data[2])))
                self.locations[key] = (self.coord[v] + self.scale*offset)
            elif type == 'vl':
                ((k1, v1), (k2, v2)) = data
                loc1 = self.coord[int(v1)]
                loc2 = self.coord[int(v2)]
                self.locations[key] = (k1*loc1 + k2*loc2)
            elif type == 'f':
                (raw, head, tail, offs) = data
                rloc = self.locations[raw]
                hloc = self.locations[head]
                tloc = self.locations[tail]
                vec = tloc - hloc
                vraw = rloc - hloc
                x = vec.dot(vraw)/vec.dot(vec)
                self.locations[key] = hloc + x*vec + Vector(offs)
            elif type == 'n':
                (raw, j1, j2, j3) = data
                rloc = self.locations[raw]
                loc1 = self.locations[j1]
                loc2 = self.locations[j2]
                loc3 = self.locations[j3]
                e12 = loc2 - loc1
                e13 = loc3 - loc1
                n = e12.cross(e13).normalized()
                e1r = rloc - loc1
                self.locations[key] = rloc - n*e1r.dot(n)
            elif type == 'b':
                self.locations[key] = self.jointLocs[key] = self.locations[data]
            elif type == 'p':
                x = self.locations[data[0]]
                y = self.locations[data[1]]
                z = self.locations[data[2]]
                self.locations[key] = Vector((x[0],y[1],z[2]))
            elif type == 'vz':
                v = int(data[0])
                z = self.coord[v][2]
                loc = self.locations[data[1]]
                self.locations[key] = Vector((loc[0],loc[1],z))
            elif type == 'X':
                r = self.locations[data[0]]
                (x,y,z) = data[1]
                r1 = Vector([float(x), float(y), float(z)])
                self.locations[key] = r.cross(r1)
            elif type == 'l':
                ((k1, joint1), (k2, joint2)) = data
                self.locations[key] = k1*self.locations[joint1] + k2*self.locations[joint2]
            elif type == 'o':
                (joint, offsSym) = data
                if isinstance(offsSym, str):
                    offs = self.locations[offsSym]
                else:
                    offs = self.scale * Vector(offsSym)
                self.locations[key] = self.locations[joint] + offs
            else:
                raise NameError("Unknown %s" % type)
        return


    def setupPlaneJoints (self):
        cfg = self.config
        for key,data in self.planeJoints:
            p0,plane,dist = data
            x0 = self.locations[p0]
            p1,p2,p3 = self.planes[plane]
            vec = getUnitVector(self.locations[p3] - self.locations[p1])
            n = self.normals[plane]
            t = n.cross(vec)
            self.locations[key] = x0 + self.scale*dist*t


    def findLocation(self, joint):
        if isinstance(joint, str):
            return self.locations[joint]
        else:
            (first, second) = joint
            if isinstance(first, str):
                return self.locations[first] + self.scale*Vector(second)
            else:
                w1,j1 = first
                w2,j2 = second
                return w1*self.locations[j1] + w2*self.locations[j2]


    def distance(self, joint1, joint2):
        vec = self.locations[joint2] - self.locations[joint1]
        return math.sqrt(vec.dot(vec))


    def getBoneScale(self, bname):
        try:
            head,tail = self.headsTails[bname]
            head0,tail0 = self.headsTailsOrig[bname]
        except KeyError:
            return None
        if (not ((head == head0 and tail == tail0) or
                 (head == tail0 and tail == head0))):
            vec = self.locations[tail] - self.locations[head]
            vec0 = self.locations[tail0] - self.locations[head0]
            return vec0.length/vec.length
        else:
            return None


    def prefixWeights(self, weights, prefix):
        pweights = {}
        for name in weights.keys():
            if name in self.heads:
                pweights[name] = weights[name]
            else:
                pweights[prefix+name] = weights[name]
        return pweights


    def sortBones(self, bone, hier):
        self.bones[bone.name] = bone
        subhier = []
        hier.append([bone, subhier])
        for child in bone.children:
            self.sortBones(child, subhier)


    def addBones(self, dict):
        for bname,info in dict.items():
            bone = self.bones[bname] = Bone(self, bname)
            bone.fromInfo(info)


    def getParent(self, bone):
        return bone.parent


    def reparentMarkers(self, markers):
        for suffix in [".L", ".R"]:
            for bname in markers:
                bone = self.bones[bname + ".marker" + suffix]
                words = bone.parent.rsplit(".", 1)
                bone.parent = words[0] + ".fk" + suffix


    def addIkChains(self, generic, ikChains):
        """
        Adds FK and IK versions of the bones in the chain, and add CopyTransform
        constraints to the original bone, which is moved to the L_HELP layer. E.g.
        shin.L => shin.fk.L, shin.ik.L, shin.L
        """

        cfg = self.config

        for bname in generic.keys():
            if bname not in self.bones.keys():
                continue
            bone = self.bones[bname]
            headTail = self.headsTails[bname]
            base,ext = splitBoneName(bname)
            #bone.parent = self.getParent(bone)

            if base in ikChains.keys():
                pbase,pext = splitBoneName(bone.parent)
                value = ikChains[base]
                type = value[0]
                iklayer = L_HELP
                if type == "DownStream":
                    _,layer,cnsname = value
                    fkParent = getFkName(pbase,pext)
                elif type == "Upstream":
                    _,layer,cnsname = value
                    fkParent = ikParent = bone.parent
                elif type == "Leaf":
                    _, layer, iklayer, count, cnsname, target, pole, lang, rang = value
                    fkParent = getFkName(pbase,pext)
                    ikParent = getIkName(pbase,pext)
                else:
                    raise NameError("Unknown IKChain type %s" % type)

                if ext == ".R":
                    layer <<= 16

                fkName = getFkName(base,ext)
                self.headsTails[fkName] = headTail
                fkBone = self.bones[fkName] = Bone(self, fkName)
                fkBone.fromInfo((bname, fkParent, F_WIR, layer<<1, bone.poseFlags))

                if cfg.useCustomShapes:
                    customShape = self.customShapes[bone.name]
                    self.customShapes[fkName] = customShape
                    self.customShapes[bone.name] = None
                bone.layers = L_HELP

                if bname in self.locks.keys():
                    self.locks[fkName] = self.locks[bname]
                if cfg.useRotationLimits:
                    if bname in self.rotationLimits.keys():
                        self.rotationLimits[fkName] = self.rotationLimits[bname]
                        del self.rotationLimits[bname]

                if type == "DownStream":
                    continue

                self.addConstraint(bname, copyTransform(fkName, cnsname+"FK"))

                ikName = getIkName(base,ext)
                self.headsTails[ikName] = headTail
                ikBone = self.bones[ikName] = Bone(self, ikName)
                ikBone.fromInfo((bname, ikParent, F_WIR, L_HELP, bone.poseFlags))

                if cfg.useCustomShapes:
                    self.customShapes[ikName] = customShape
                self.addConstraint(bname, copyTransform(ikName, cnsname+"IK", 0))

                if type == "Leaf":
                    words = bone.parent.rsplit(".", 1)
                    pbase = words[0]
                    if len(words) == 1:
                        pext = ""
                    else:
                        pext = "." + words[1]
                    fkBone.parent = pbase + ".fk" + pext
                    ikBone.parent = pbase + ".ik" + pext
                    ikBone.layers = iklayer
                    if iklayer == L_TWEAK:
                        ikBone.lockRotation = (0,0,1)
                        ikBone.layers = layer
                    bone.norot = True

                    ikTarget = target + ".ik" + ext
                    poleTarget = pole + ".ik" + ext
                    if ext == ".L":
                        poleAngle = lang
                    else:
                        poleAngle = rang

                    cns = ('IK', 0, 1, ['IK', ikTarget, count, (poleAngle, poleTarget), (True, False,False)])
                    self.addConstraint(ikName, cns)


    def addDeformBones(self):
        """
        Add deform bones with CopyTransform constraints to the original bone.
        Deform bones start with self.deformPrefix, as in Rigify.
        Don't add deform bones for split forearms, becaues that is done elsewhere.
        """

        cfg = self.config

        for bname in self.deformArmature.keys():
            try:
                bone = self.bones[bname]
            except KeyError:
                print("Warning: deform bone %s does not exist" % bname)
                continue
            if (self.isDeformName(bname) or not bone.deform):
                continue

            base,ext = splitBoneName(bname)
            if not (cfg.useSplitBones and
                    base in self.splitBones.keys()):
                headTail = self.headsTails[bname]
                bone.deform = False
                defParent = self.getDeformParent(bname)
                defname = self.deformPrefix + bname
                self.headsTails[defname] = headTail
                defBone = self.bones[defname] = Bone(self, defname)
                defBone.fromInfo((bone, defParent, F_DEF, L_DEF))
                self.addConstraint(defname, copyTransform(bone.name, bone.name))


    def getDeformParent(self, bname):
        cfg = self.config
        bone = self.bones[bname]
        bone.parent = self.getParent(bone)
        if (bone.parent and cfg.useDeformBones):
            pbase, pext = splitBoneName(bone.parent)
            if pbase in self.splitBones.keys():
                npieces = self.splitBones[pbase][0]
                return self.deformPrefix + pbase + ".0" + str(npieces) + pext
            else:
                parbone = self.bones[bone.parent]
                if (parbone.deform and
                    not self.isDeformName(bone.parent)):
                    return self.deformPrefix + bone.parent
                else:
                    return bone.parent
        else:
            return bone.parent


    def addSplitBones(self):
        """
            Split selected bones into two or three parts for better deformation,
            and constrain them to copy the partially.
            E.g. forearm.L => DEF-forearm.01.L, DEF-forearm.02.L, DEF-forearm.03.L
        """
        cfg = self.config

        for base in self.splitBones.keys():
            for ext in [".L", ".R"]:
                npieces,target,numAfter,followNext = self.splitBones[base]
                defName1,defName2,defName3 = splitBonesNames(base, ext, self.deformPrefix, numAfter)
                bname = base + ext
                head,tail = self.headsTails[bname]
                defParent = self.getDeformParent(bname)
                bone = self.bones[bname]
                rotMode = bone.poseFlags & P_ROTMODE
                rotMode = P_YZX

                if npieces == 2:
                    self.headsTails[defName1] = (head, ((0.5,head),(0.5,tail)))
                    self.headsTails[defName2] = (((0.5,head),(0.5,tail)), tail)

                    defBone1 = self.bones[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bname, defParent, F_DEF+F_CON, L_DEF, rotMode))
                    self.addConstraint(defName1, ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)]))

                    defBone2 = self.bones[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bname, defBone1, F_DEF, L_DEF, rotMode))
                    self.addConstraint(defName2, ('CopyRot', C_LOCAL, 1, [target, target+ext, (0,1,0), (0,0,0), True]))

                elif npieces == 3:
                    self.headsTails[defName1] = (head, ((0.667,head),(0.333,tail)))
                    self.headsTails[defName2] = (((0.667,head),(0.333,tail)), ((0.333,head),(0.667,tail)))
                    self.headsTails[defName3] = (((0.333,head),(0.667,tail)), tail)

                    defBone1 = self.bones[defName1] = Bone(self, defName1)
                    defBone1.fromInfo((bname, defParent, F_DEF+F_CON, L_DEF, rotMode))
                    defBone2 = self.bones[defName2] = Bone(self, defName2)
                    defBone2.fromInfo((bname, defName1, F_DEF+F_CON, L_DEF, rotMode))
                    defBone3 = self.bones[defName3] = Bone(self, defName3)
                    defBone3.fromInfo((bname, defName2, F_DEF+F_CON, L_DEF, rotMode))

                    self.addConstraint(defName1, ('IK', 0, 1, ['IK', target+ext, 1, None, (True, False,True)]))
                    if followNext:
                        self.addConstraint(defName2, ('CopyRot', C_LOCAL, 0.5, [target, target+ext, (0,1,0), (0,0,0), True]))
                        self.addConstraint(defName3, ('CopyRot', C_LOCAL, 0.5, [target, target+ext, (0,1,0), (0,0,0), True]))
                    else:
                        self.addConstraint(defName2, ('CopyRot', 0, 0.5, [bname, bname, (1,1,1), (0,0,0), False]))
                        self.addConstraint(defName3, ('CopyRot', 0, 1.0, [bname, bname, (1,1,1), (0,0,0), False]))

                defname = self.deformPrefix + base + ext
                for bone in self.bones.values():
                    if bone.parent == defname:
                        bone.parent = defName1


    def addDeformVertexGroups(self, vgroups):
        cfg = self.config
        useSplit = (cfg.useSplitBones or cfg.useSplitNames)
        for bname,vgroup in vgroups.items():
            base = splitBoneName(bname)[0]
            if useSplit and base in self.splitBones.keys():
                pass
            elif bname[0:4] == "hair":
                pass
            elif not self.isDeformName(bname):
                defname = self.deformPrefix+bname
                self.vertexGroups[defname] = vgroup
                try:
                    del self.vertexGroups[bname]
                except:
                    pass


    def readVertexGroupFiles(self, files):
        vgroups = OrderedDict()
        for file in files:
            try:
                folder,fname = file
            except:
                folder = "armature/data/vertexgroups/hm8"
                fname = file
            filepath = os.path.join(folder, "vgrp_"+fname+".json")
            print("Loading %s" % filepath)
            vglist = loadJsonRelative(filepath)
            for key,data in vglist:
                try:
                    vgroups[key] += data
                except KeyError:
                    vgroups[key] = data
            #readVertexGroups(filepath, vgroups, vgroups)
        return vgroups


    def addSplitVertexGroups(self, vgroups):
        for bname,vgroup in vgroups.items():
            base = splitBoneName(bname)[0]
            if base in self.splitBones.keys():
                self.splitVertexGroup(bname, vgroup)
                try:
                    del self.vertexGroups[bname]
                except KeyError:
                    print("No VG %s" % bname)


    def splitVertexGroup(self, bname, vgroup):
        """
        Splits a vertex group into two or three, with weights distributed
        linearly along the bone.
        """

        base,ext = splitBoneName(bname)
        if base in self.splitBones.keys():
            npieces,_target,numAfter,_followNext = self.splitBones[base]
            defName1,defName2,defName3 = splitBonesNames(base, ext, self.deformPrefix, numAfter)
        else:
            npieces = 2
            defName1 = base + "-1" + ext
            defName2 = base + "-2" + ext

        head,tail = self.headsTails[bname]
        vec = self.locations[tail] - self.locations[head]
        vec /= vec.dot(vec)
        orig = self.locations[head] + self.origin

        vgroup1 = []
        vgroup2 = []
        vgroup3 = []

        #print(bname,vgroup)

        if npieces == 2:
            for vn,w in vgroup:
                y = self.coord[vn] - orig
                x = vec.dot(y)
                if x < 0:
                    vgroup1.append([vn,w])
                elif x < 1:
                    vgroup1.append([vn, (1-x)*w])
                    vgroup2.append([vn, x*w])
                else:
                    vgroup2.append([vn,w])
            self.vertexGroups[defName1] = vgroup1
            self.vertexGroups[defName2] = vgroup2
        elif npieces == 3:
            for vn,w in vgroup:
                y = self.coord[vn] - orig
                x = vec.dot(y)
                if x < 0:
                    vgroup1.append([vn,w])
                elif x < 0.5:
                    vgroup1.append([vn, (1-2*x)*w])
                    vgroup2.append([vn, (2*x)*w])
                elif x < 1:
                    vgroup2.append([vn, (2-2*x)*w])
                    vgroup3.append([vn, (2*x-1)*w])
                else:
                    vgroup3.append([vn,w])
            self.vertexGroups[defName1] = vgroup1
            self.vertexGroups[defName2] = vgroup2
            self.vertexGroups[defName3] = vgroup3


    def mergeBones(self, mergers):
        for bname, data in mergers.items():
            tname, merged = data
            head,_ = self.headsTails[bname]
            _,tail = self.headsTails[tname]
            self.headsTails[bname] = head,tail

            if bname in self.vertexGroups.keys():
                vgroup = self.vertexGroups[bname]
            else:
                vgroup = []
                bone = self.bones[bname]
                bone.deform = True

            for mbone in merged:
                if mbone != bname:
                    if mbone in self.vertexGroups.keys():
                        vgroup += self.vertexGroups[mbone]
                        del self.vertexGroups[mbone]
                    if mbone in self.bones.keys():
                        del self.bones[mbone]
                    for child in self.bones.values():
                        if child.parent == mbone:
                            child.parent = bname
                            chead = self.headsTails[child.name]
                            if chead != tail:
                                child.conn = False

            self.vertexGroups[bname] = mergeWeights(vgroup)


    def setupRotationBones(self, rotBones):
        for bname,data in rotBones.items():
            cname,plane,length,axis,angle = data
            cbone = self.bones[cname]
            cvec = cbone.tail - cbone.head
            t = cvec/cvec.length
            n = self.normals[plane]
            if axis == 'X':
                rvec = n
            elif axis == 'Y':
                rvec = t
            elif axis == 'Z':
                rvec = t.cross(n)
            rot = Matrix.Rotation(-angle*D, 3, rvec)
            bvec = rot * t * length * self.scale

            bone = self.bones[bname] = Bone(self, bname)
            bone.parent = cbone.parent
            bone.roll = plane
            head = cbone.head
            bone.setBone(head, head + bvec)
            bone.layers = L_CSYS


    def addConstraint(self, bname, cns):
        from . import constraints
        try:
            cnslist = self.constraints[bname]
        except KeyError:
            cnslist = self.constraints[bname] = []
        cnslist.append(constraints.addConstraint(cns))


    def setConstraints(self, constraints):
        for bname,clist in constraints.items():
            for cns in clist:
                self.addConstraint(bname, cns)


#-------------------------------------------------------------------------------
#   Bone class
#-------------------------------------------------------------------------------

class Bone:

    def __init__(self, parser, name):
        self.name = name
        self.parser = parser
        self.origName = name
        self.head = None
        self.tail = None
        self.roll = 0
        self.parent = None
        self.setFlags(0)
        self.poseFlags = 0
        self.layers = L_MAIN
        self.length = 0
        self.customShape = None
        self.children = []

        self.location = (0,0,0)
        self.lockLocation = (0,0,0)
        self.lockRotation = (0,0,0)
        self.lockScale = (1,1,1)
        self.ikDof = (1,1,1)
        #self.lock_rotation_w = False
        #self.lock_rotations_4d = False

        self.constraints = []
        self.drivers = []


    def __repr__(self):
        return "<Bone %s %s %s>" % (self.name, self.parent, self.children)


    def fromInfo(self, info):
        if len(info) == 5:
            self.roll, self.parent, flags, self.layers, self.poseFlags = info
        else:
            self.roll, self.parent, flags, self.layers = info
            self.poseFlags = 0
        if self.parent and not flags & F_NOLOCK:
            self.lockLocation = (1,1,1)
        if flags & F_LOCKY:
            self.lockRotation = (0,1,0)
        if flags & F_LOCKROT:
            self.lockRotation = (1,1,1)
        if flags & F_SCALE:
            self.lockScale = (0,0,0)
        self.setFlags(flags)
        if self.roll == None:
            halt


    def setFlags(self, flags):
        self.flags = flags
        self.conn = (flags & F_CON != 0)
        self.deform = (flags & F_DEF != 0)
        self.restr = (flags & F_RES != 0)
        self.wire = (flags & F_WIR != 0)
        self.scale = (flags & F_SCALE != 0)


    def setBone(self, head, tail):
        self.head = head
        self.tail = tail
        vec = tail - head
        self.length = math.sqrt(vec.dot(vec))

        if isinstance(self.roll, str):
            if self.roll[0:5] == "Plane":
                normal = m2b(self.parser.normals[self.roll])
                self.roll = computeRoll(self.head, self.tail, normal, bone=self)
