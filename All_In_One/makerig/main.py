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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165
#
#
# Abstract: 
# Bone weighting utility
#

import bpy, os, mathutils
import math
from mathutils import *
from bpy.props import *


BodyVert = 3000
SkirtVert = 16000
TightsVert = 18000

#
#   getRigAndMesh(context):
#

def getRigAndMesh(context):
    rig = None
    me = None
    for ob in bpy.context.scene.objects:
        if ob.select:
            if ob.type == 'ARMATURE':
                if rig:
                    raise NameError("Two armatures selected")
                rig = ob
            elif ob.type == 'MESH':
                if me:
                    raise NameError("Two meshes selected")
                me = ob
    if rig and me:
        print("Using rig %s and mesh %s" % (rig, me))
    else:
        raise NameError("Must select one mesh and one armature")
    return (rig, me)
    

#
#   findJoint(jName, x, joints):
#   writeJoint(fp, jName, loc, joints, me):
#

def findJoint(jName, x, joints):
    try:
        found = joints[jName]
        return found
    except:
        pass
    if x == None:
        raise NameError("Cannot find joint "+jName)
    for (jy, y) in joints.values():
        if (x-y).length < 1e-3:
            return (jy, y)
    return None

def writeJoint(fp, jName, loc, joints, me):
    found = findJoint(jName, loc, joints)
    if found:
        joints[jName] = found
    else:
        joints[jName] = (jName, loc)
        v = closestVert(loc, me)
        offs = loc - v.co
        fp.write("  %s voffset %d %.4g %.4g %.4g\n" % (jName, v.index, offs[0], offs[2], -offs[1]))
    return
    
def closestVert(loc, me):
    mindist = 1e6
    for v in me.vertices:
        offs = loc - v.co
        if offs.length < mindist:
            best = v
            mindist = offs.length
    return best


def addKnee(fp, thigh, shin, ebones, joints):        
    hfound = findJoint(thigh+"_head", None, joints)
    tfound = findJoint(shin+"_tail", None, joints)
    mfound = findJoint(thigh+"_tailRaw", None, joints)
    (hname,hx) = hfound
    (tname,tx) = tfound
    (mname,mx) = mfound
    ttail = thigh+"_tail"
    fp.write("  %s front %s %s %s [0,0,0.1]\n" % (ttail, mname, hname, tname))
    joints[ttail] = (ttail, None)
    joints[shin+"_head"] = joints[ttail]
    

#
#   writeBones(fp, rig, me, scn):
#

def writeBones(fp, rig, me, scn):
    bpy.context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    
    # List symbolic joint locations
    joints = {}
    fp.write("\n# locations\n")
    ebones = rig.data.edit_bones
    if scn.MRLegIK:
        for eb in ebones:
            ebName = eb.name.replace(" ","_")
            if eb.parent and eb.parent.name == scn.MRThigh_L:
                writeJoint(fp, ebName+"_headRaw", eb.head, joints, me)
                shin_L = ebName
            elif eb.parent and eb.parent.name == scn.MRThigh_R:
                writeJoint(fp, ebName+"_headRaw", eb.head, joints, me)
                shin_R = ebName
            else:
                writeJoint(fp, ebName+"_head", eb.head, joints, me)
            if ebName in [scn.MRThigh_L, scn.MRThigh_R]:
                writeJoint(fp, ebName+"_tailRaw", eb.tail, joints, me)
            else:
                writeJoint(fp, ebName+"_tail", eb.tail, joints, me)
        fp.write("\n")
        addKnee(fp, scn.MRThigh_L, shin_L, ebones, joints)
        addKnee(fp, scn.MRThigh_R, shin_R, ebones, joints)
    else:
        for eb in ebones:
            ebName = eb.name.replace(" ","_")
            writeJoint(fp, ebName+"_head", eb.head, joints, me)
            writeJoint(fp, ebName+"_tail", eb.tail, joints, me)
    fp.write("\n")
        
    # List symbolic names for heads and tails
    fp.write("# bones\n")
    for eb in rig.data.edit_bones:
        #print("Bone", eb.name, eb.head, eb.tail)
        ebName = eb.name.replace(" ","_")
        hfound = findJoint(ebName+"_head", None, joints)
        tfound = findJoint(ebName+"_tail", None, joints)
        if hfound == None or tfound == None:
            fp.write("  %s %s %s" % ( ebName, eb.head, eb.tail))
            fp.close()
            raise NameError("ht", hfound, tfound)
        (hname,hx) = hfound
        (tname,tx) = tfound
        fp.write(" %s %s %s " % (ebName, hname, tname))
        if eb.roll < 0.02 and eb.roll > -0.02:
            fp.write("0 ")
        else:
            fp.write("%.3f " % eb.roll)
        if eb.parent:
            fp.write("%s " % eb.parent.name.replace(' ','_'))
        else:
            fp.write("- ")

        if not eb.use_deform:
            fp.write("-nd ")
        if not eb.use_connect:
            fp.write("-nc ")

        pb = rig.pose.bones[eb.name]
        for cns in pb.constraints:
            if cns.type == 'IK':
                fp.write("-ik %s %d %.3f " % (cns.subtarget, cns.chain_count, cns.influence))
                if cns.pole_target:
                    fp.write("-pt %s %.3f " % (cns.pole_subtarget, cns.pole_angle))
                break
        fp.write("\n")

#
#    writeVertexGroups(filePath)
#

def writeVertexGroups(fp, ob):
    for vg in ob.vertex_groups:
        index = vg.index
        weights = []
        for v in ob.data.vertices:
            for grp in v.groups:
                if grp.group == index and grp.weight > 0.005:
                    weights.append((v.index, grp.weight))    
        exportList(fp, weights, vg.name, 0)
    return
    
def exportList(fp, weights, name, offset):
    if len(weights) == 0:
        return
    if len(weights) > 0:
        fp.write("\n# weights %s\n" % name)
        for (vn,w) in weights:
            if w > 0.005:
                fp.write("  %d %.3g\n" % (vn+offset, w))
    

#
#   checkObjectOK(ob, context):
#

def checkObjectOK(ob, context):
    old = context.object
    context.scene.objects.active = ob
    word = None
    error = False
    epsilon = 1e-4
    if ob.location.length > epsilon:
        word = "object translation"
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    eu = ob.rotation_euler
    if abs(eu.x) + abs(eu.y) + abs(eu.z) > epsilon:
        word = "object rotation"
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    vec = ob.scale - Vector((1,1,1))
    if vec.length > epsilon:
        word = "object scaling"
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if ob.constraints:
        word = "constraints"
        error = True
    if ob.parent:
        word = "parent"
        ob.parent = None
    if word:
        msg = "Object %s can not be used for rig creation because it has %s.\n" % (ob.name, word)
        if error:
            msg +=  "Apply or delete before continuing.\n"
            print(msg)
            raise NameError(msg)
        else:
            print(msg)
            print("Fixed automatically")
    context.scene.objects.active = old
    return    

#
#   exportRigFile(context):
#

def exportRigFile(context):
    (rig,ob) = getRigAndMesh(context)
    checkObjectOK(rig, context)
    checkObjectOK(ob, context)
    (rigpath, rigfile) = getFileName(rig, context, "rig")
    print("Open", rigfile)
    fp = open(rigfile, mode="w", encoding="utf-8")
    scn = context.scene
    fp.write(
        "# author %s\n" % scn.MRAuthor +
        "# license %s\n" % scn.MRLicense +
        "# homepage %s\n" % scn.MRHomePage)
    writeBones(fp, rig, ob.data, scn)
    writeVertexGroups(fp, ob)
    fp.close()
    print("Rig file %s created" % rigfile)
    return
    
#
#   autoWeightBody(context)
#

def autoWeightBody(context):
    (rig,ob) = getRigAndMesh(context)
    scn = context.scene
    scn.objects.active = ob

    # Clean up original mesh
    for mod in ob.modifiers:
        if mod.type == 'ARMATURE':
            ob.modifiers.remove(mod)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.vertex_group_remove(all=True)
    
    # Copy mesh and autoweight duplicate
    rig.select = False
    ob.select = True
    bpy.ops.object.duplicate()
    dupliob = scn.objects.active
    for vn in [BodyVert]:
        dupliob.data.vertices[vn].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_linked(limit=False)
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.select = True
    scn.objects.active = rig
    print("Parent", ob, "to", rig)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    # Copy vertex weights back from duplicate
    vgroups = {}
    for dgrp in dupliob.vertex_groups:
        vgrp = ob.vertex_groups.new(dgrp.name)
        vgroups[dgrp.index] = vgrp
    vn = -1
    for dv in dupliob.data.vertices:
        dist = 1000
        while dist > 0.001:
            vn += 1
            v = ob.data.vertices[vn]
            vec = v.co - dv.co
            dist = vec.length
        for dg in dv.groups:
            vgroups[dg.group].add([vn], dg.weight, 'REPLACE')
            
    ob.parent = rig
    mod = ob.modifiers.new("Armature", 'ARMATURE')
    mod.object = rig
    mod.use_vertex_groups = True
    mod.use_bone_envelopes = False
    scn.objects.unlink(dupliob)    
    return
    
#
#   copyWeights(context):
#

def copyWeights(context):
    src = context.object
    trg = None
    scn = context.scene
    for ob in scn.objects:
        if ob.select and ob.type == 'MESH' and ob != src:
            trg = ob
            break
    if not trg:
        raise NameError("Two meshes must be selected")
    if len(trg.data.vertices) < len(src.data.vertices):
        ob = src
        src = trg
        trg = ob
        
    scn.objects.active = trg
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.vertex_group_remove(all=True)
        
    groupMap = {}
    for sgrp in src.vertex_groups:
        groupMap[sgrp.index] = trg.vertex_groups.new(sgrp.name)
    for n,vs in enumerate(src.data.vertices):
        vt = trg.data.vertices[n]
        for g in vs.groups:
            tgrp = groupMap[g.group]
            tgrp.add([vt.index], g.weight, 'REPLACE')


#
#   autoWeightSkirt(context):
#

def autoWeightSkirt(context):
    ob = context.object
    xmin = 1000
    xmax = -1000
    verts = {}
    for v in ob.data.vertices:
        if v.select:
            if v.co[0] > xmax:
                xmax = v.co[0]
            if v.co[0] < xmin:
                xmin = v.co[0]
            verts[v.index] = []
    if xmin >= xmax:
        raise NameError("Selection does not contain vertices at different x")
    print("xmin = %.3f xmax = %.3f" % (xmin, xmax))
                        
    (pairs, symm, symmIndex) = symmetricGroups(ob)    
    for (left, leftIndex, right, rightIndex) in pairs:
        print(leftIndex.items())
        for v in ob.data.vertices:
            if v.select:
                for g in v.groups:
                    try:
                        gname = leftIndex[g.group]
                    except:
                        gname = None
                    if not gname:
                        try:
                            gname = rightIndex[g.group]
                        except:
                            gname = None
                    if gname and g.weight > Epsilon:
                        verts[v.index].append( (left[gname], right[gname], v.co[0], g.weight) )
                        
    for (vn, value) in verts.items():
        for (lgrp, rgrp, x, w) in value:
            wl = w*(x-xmin)/(xmax-xmin)
            wr = w-wl
            lgrp.add([vn], wl, 'REPLACE')
            rgrp.add([vn], wr, 'REPLACE')

    return
     
#
#    class CProxy
#

class CProxy:
    def __init__(self):
        self.refVerts = []
        self.firstVert = 0
        return
        
    def setWeights(self, verts, grp):
        rlen = len(self.refVerts)
        mlen = len(verts)
        first = self.firstVert
        if (first+rlen) != mlen:
            raise NameError( "Bug: %d refVerts != %d meshVerts" % (first+rlen, mlen) )
        gn = grp.index
        for n in range(rlen):
            vert = verts[n+first]
            refVert = self.refVerts[n]
            if type(refVert) == tuple:
                (rv0, rv1, rv2, w0, w1, w2, d0, d1, d2) = refVert
                vw0 = CProxy.getWeight(verts[rv0], gn)
                vw1 = CProxy.getWeight(verts[rv1], gn)
                vw2 = CProxy.getWeight(verts[rv2], gn)
                vw = w0*vw0 + w1*vw1 + w2*vw2
            else:
                vw = getWeight(verts[refVert], gn)
            grp.add([vert.index], vw, 'REPLACE')
        return
   
    def getWeight(vert, gn):
        for grp in vert.groups:
            if grp.group == gn:
                return grp.weight
        return 0             
        
    def read(self, filepath):
        realpath = os.path.realpath(os.path.expanduser(filepath))
        folder = os.path.dirname(realpath)
        try:
            tmpl = open(filepath, "rU")
        except:
            tmpl = None
        if tmpl == None:
            print("*** Cannot open %s" % realpath)
            return None

        status = 0
        doVerts = 1
        vn = 0
        for line in tmpl:
            words= line.split()
            if len(words) == 0:
                pass
            elif words[0] == '#':
                status = 0
                if len(words) == 1:
                    pass
                elif words[1] == 'verts':
                    if len(words) > 2:
                        self.firstVert = int(words[2])                    
                    status = doVerts
                else:
                    pass
            elif status == doVerts:
                if len(words) == 1:
                    v = int(words[0])
                    self.refVerts.append(v)
                else:                
                    v0 = int(words[0])
                    v1 = int(words[1])
                    v2 = int(words[2])
                    w0 = float(words[3])
                    w1 = float(words[4])
                    w2 = float(words[5])            
                    d0 = float(words[6])
                    d1 = float(words[7])
                    d2 = float(words[8])
                    self.refVerts.append( (v0,v1,v2,w0,w1,w2,d0,d1,d2) )
        return
        
        
def autoWeightHelpers(context):
    ob = context.object
    proxy = CProxy()
    scn = context.scene
    path = os.path.join(scn.MRMakeHumanDir, "data/3dobjs/base.mhclo")
    proxy.read(path)
    for grp in ob.vertex_groups:
        print(grp.name)
        proxy.setWeights(ob.data.vertices, grp)
    print("Weights projected from proxy")
    return     
    
#
#    unVertexDiamonds(context):
#

def getFaces(me):
    try:
        return me.faces
    except:
        return me.polygons
        
        
def unVertexDiamonds(context):
    ob = context.object
    print("Unvertex diamonds in %s" % ob)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    me = ob.data
    faces = getFaces(me)
    for f in faces:        
        if len(f.vertices) < 4:
            for vn in f.vertices:
                me.vertices[vn].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.vertex_group_remove_from(all=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    return
    
    
def unVertexBelowThreshold(context):    
    ob = context.object
    threshold = context.scene.MRThreshold
    for vgrp in ob.vertex_groups:
        gn = vgrp.index
        for v in ob.data.vertices:
            for g in v.groups:
                if g.group == gn and g.weight < threshold:
                    vgrp.remove([v.index])
    return
    
#
#   goodName(name):    
#   getFileName(pob, context, ext):            
#

def goodName(name):    
    newName = name.replace('-','_').replace(' ','_')
    return newName.lower()
    
def getFileName(ob, context, ext):            
    name = goodName(ob.name)
    #outpath = '%s/%s' % (context.scene.MRDirectory, name)
    outpath = os.path.realpath(os.path.expanduser(context.scene.MRDirectory))
    if not os.path.exists(outpath):
        print("Creating directory %s" % outpath)
        os.mkdir(outpath)
    outfile = os.path.join(outpath, "%s.%s" % (name, ext))
    return (outpath, outfile)

#
#    symmetrizeWeights(context):
#    class VIEW3D_OT_SymmetrizeWeightsButton(bpy.types.Operator):
#

Epsilon = 1e-3
    
def symmetricGroups(ob):
    left = {}
    left01 = {}
    left02 = {}
    left03 = {}
    leftIndex = {}
    left01Index = {}
    left02Index = {}
    left03Index = {}
    right = {}
    right01 = {}
    right02 = {}
    right03 = {}
    rightIndex = {}
    right01Index = {}
    right02Index = {}    
    right03Index = {}
    symm = {}
    symmIndex = {}
    for vgrp in ob.vertex_groups:
        if vgrp.name[-2:] in ['_L', '.L', '_l', '.l']:
            nameStripped = vgrp.name[:-2]
            left[nameStripped] = vgrp
            leftIndex[vgrp.index] = nameStripped
        elif vgrp.name[-2:] in ['_R', '.R', '_r', '.r']:
            nameStripped = vgrp.name[:-2]
            right[nameStripped] = vgrp
            rightIndex[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.L.01', '.l.01']:
            nameStripped = vgrp.name[:-5]
            left01[nameStripped] = vgrp
            left01Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.R.01', '.r.01']:
            nameStripped = vgrp.name[:-5]
            right01[nameStripped] = vgrp
            right01Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.L.02', '.l.02']:
            nameStripped = vgrp.name[:-5]
            left02[nameStripped] = vgrp
            left02Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['.R.02', '.r.02']:
            nameStripped = vgrp.name[:-5]
            right02[nameStripped] = vgrp
            right02Index[vgrp.index] = nameStripped
        elif vgrp.name[-4:] in ['Left', 'left']:
            nameStripped = vgrp.name[:-4]
            left03[nameStripped] = vgrp
            left03Index[vgrp.index] = nameStripped
        elif vgrp.name[-5:] in ['Right', 'right']:
            nameStripped = vgrp.name[:-5]
            right03[nameStripped] = vgrp
            right03Index[vgrp.index] = nameStripped
        else:
            symm[vgrp.name] = vgrp
            symmIndex[vgrp.index] = vgrp.name

    printGroups('Left', left, leftIndex, ob.vertex_groups)
    printGroups('Right', right, rightIndex, ob.vertex_groups)
    printGroups('Left01', left01, left01Index, ob.vertex_groups)
    printGroups('Right01', right01, right01Index, ob.vertex_groups)
    printGroups('Left02', left02, left02Index, ob.vertex_groups)
    printGroups('Right02', right02, right02Index, ob.vertex_groups)
    printGroups('left03', left03, left03Index, ob.vertex_groups)
    printGroups('right03', right03, right03Index, ob.vertex_groups)
    printGroups('Symm', symm, symmIndex, ob.vertex_groups)
    
    pairs = [(left, leftIndex, right, rightIndex), 
             (left01, left01Index, right01, right01Index), 
             (left02, left02Index, right02, right02Index),
             (left03, left03Index, right03, right03Index)] 
    return (pairs, symm, symmIndex)


def symmetrizeWeights(context, left2right):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    
    (pairs, symm, symmIndex) = symmetricGroups(ob)    
    (left, leftIndex, right, rightIndex) = pairs[0]
    (lverts, rverts, mverts) = setupVertexPairs(context)
    groups = []
    if left2right:
        factor = 1
        fleft = left
        fright = right
        for (left0, left0Index, right0, right0Index) in pairs:
            groups += list(right0.values())
        cleanGroups(ob.data, groups)
    else:
        factor = -1
        fleft = right
        fright = left
        rverts = lverts
        for (left0, left0Index, right0, right0Index) in pairs:
            groups += list(left0.values())
        cleanGroups(ob.data, groups)

    for (vn, rvn) in rverts.items():
        v = ob.data.vertices[vn]
        rv = ob.data.vertices[rvn]
        #print(v.index, rv.index)
        for rgrp in rv.groups:
            rgrp.weight = 0
        for grp in v.groups:
            pairList = [(symm, symmIndex)]
            for (left, leftIndex, right, rightIndex) in pairs:
                pairList.append((right, leftIndex))
                pairList.append((left, rightIndex))
            rgrp = None
            for (groups, indices) in pairList:              
                try:
                    name = indices[grp.group]
                    rgrp = groups[name]
                except:
                    pass
            if rgrp:
                #print("  ", name, grp.group, rgrp.name, rgrp.index, v.index, rv.index, grp.weight)
                rgrp.add([rv.index], grp.weight, 'REPLACE')
            else:                
                gn = grp.group
                raise NameError("*** No rgrp for %s %s %s" % (grp, gn, ob.vertex_groups[gn]))
    return len(rverts)


def printGroups(name, groups, indices, vgroups):
    print(name)
    for (nameStripped, grp) in groups.items():
        print("  ", nameStripped, grp.name, indices[grp.index])
    return


def cleanGroups(me, groups):
    for grp in groups:
        print(grp)
        for v in me.vertices:
            grp.remove([v.index])
    return
    
#
#   zeroRolls(context):
#
    
def zeroRolls(context):
    ob = context.object
    if not (ob and ob.type == 'ARMATURE'):
        raise NameError("An armature must be selected")
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in ob.data.edit_bones:
        eb.roll = 0
    bpy.ops.object.mode_set(mode='OBJECT')

        
#----------------------------------------------------------
#   setupVertexPairs(ob):
#----------------------------------------------------------

def setupVertexPairs(context):
    ob = context.object
    verts = []
    for v in ob.data.vertices:
        x = v.co[0]
        y = v.co[1]
        z = v.co[2]
        verts.append((z,y,x,v.index))
    verts.sort()        
    lverts = {}
    rverts = {}
    mverts = {}
    nmax = len(verts)
    notfound = []
    for n,data in enumerate(verts):
        (z,y,x,vn) = data
        n1 = n - 20
        n2 = n + 20
        if n1 < 0: n1 = 0
        if n2 >= nmax: n2 = nmax
        vmir = findVert(verts[n1:n2], vn, -x, y, z, notfound)
        if vmir < 0:
            mverts[vn] = vn
        elif x > Epsilon:
            rverts[vn] = vmir
        elif x < -Epsilon:
            lverts[vn] = vmir
        else:
            mverts[vn] = vmir
    if notfound:            
        print("Did not find mirror image for vertices:")
        for msg in notfound:
            print(msg)
    print("Left-right-mid", len(lverts.keys()), len(rverts.keys()), len(mverts.keys()))
    return (lverts, rverts, mverts)
    
def findVert(verts, v, x, y, z, notfound):
    for (z1,y1,x1,v1) in verts:
        dx = x-x1
        dy = y-y1
        dz = z-z1
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < Epsilon:
            return v1
    if abs(x) > Epsilon:            
        notfound.append("  %d at (%.4f %.4f %.4f)" % (v, x, y, z))
    return -1                    

#
#   readDefaultSettings(context):
#   saveDefaultSettings(context):
#

def settingsFile():
    outdir = os.path.expanduser("~/makehuman/settings/")        
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return os.path.join(outdir, "make_rig.settings")

def readDefaultSettings(context):
    fname = settingsFile() 
    try:
        fp = open(fname, "rU")
    except:
        print("Did not find %s. Using default settings" % fname)
        return
    
    scn = context.scene
    for line in fp:
        words = line.split()
        prop = words[0]
        type = words[1]        
        if type == "int":
            scn[prop] = int(words[2])
        elif type == "float":
            scn[prop] = float(words[2])
        elif type == "str":
            string = words[2]
            for word in words[3:]:
                string += " " + word
            scn[prop] = string
    fp.close()
    return
    
def saveDefaultSettings(context):
    fname = settingsFile() 
    fp = open(fname, "w")
    scn = context.scene
    for (prop, value) in scn.items():
        if prop[0:2] == "MR":
            if type(value) == int:
                fp.write("%s int %s\n" % (prop, value))
            elif type(value) == float:
                fp.write("%s float %.4f\n" % (prop, value))
            elif type(value) == str:
                fp.write("%s str %s\n" % (prop, value))
    fp.close()
    return
    
#
#   initInterface():
#

def initInterface():
    bpy.types.Scene.MRDirectory = StringProperty(
        name="Directory", 
        description="Directory", 
        maxlen=1024,
        default="~")
        
    bpy.types.Scene.MRMakeHumanDir = StringProperty(
        name="MakeHuman Directory", 
        description="The directory where MakeHuman is installed", 
        maxlen=1024,
        default="/home/svn/makehuman")        
    
    bpy.types.Scene.MRVertNum = IntProperty(
        name="Vertex", 
        default = -1)

    bpy.types.Scene.MRThreshold = FloatProperty(
        name="Threshold", 
        default = 0.001,
        min=0.0, max=1.0)    
    
    bpy.types.Scene.MRAuthor = StringProperty(
        name="Author", 
        default="Unknown",
        maxlen=32)
    
    bpy.types.Scene.MRLicense = StringProperty(
        name="License", 
        default="AGPL3 (see also http://www.makehuman.org/node/320)",
        maxlen=256)
    
    bpy.types.Scene.MRHomePage = StringProperty(
        name="HomePage", 
        default="http://www.makehuman.org/",
        maxlen=256)
        
    bpy.types.Scene.MRLegIK = BoolProperty(
        name="Leg IK",
        default=False)

    bpy.types.Scene.MRThigh_L = StringProperty(
        name="Left Thigh Bone",
        default="UpLeg_L")
    
    bpy.types.Scene.MRThigh_R = StringProperty(
        name="Right Thigh Bone",
        default="UpLeg_R")
    

    return
   
