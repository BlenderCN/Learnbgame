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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import time
import math
import mathutils
from mathutils import Vector, Matrix, Quaternion
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from .hm8 import *
from .error import *
from .utils import *

LowestVersion = 22
HighestVersion = 49

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def importMhx2File(filepath, cfg, context):
    filepath = os.path.expanduser(filepath)
    cfg.folder = os.path.dirname(filepath)
    struct, time1 = importMhx2Json(filepath)
    build(struct, cfg, context)
    time2 = time.clock()
    print("File %s loaded in %g s" % (filepath, time2-time1))


def importMhx2Json(filepath):
    from .load_json import loadJson

    if os.path.splitext(filepath)[1].lower() != ".mhx2":
        print("Error: Not a mhx2 file: %s" % filepath.encode('utf-8', 'strict'))
        return
    print( "Opening MHX2 file %s " % filepath.encode('utf-8', 'strict') )

    time1 = time.clock()
    struct = loadJson(filepath)

    try:
        vstring = struct["mhx2_version"]
    except KeyError:
        vstring = ""

    if vstring:
        high,low = vstring.split(".")
        fileVersion = 100*int(high) + int(low)
    else:
        fileVersion = 0

    if (fileVersion > HighestVersion or
        fileVersion < LowestVersion):
        raise MhxError(
            ("Incompatible MHX2 versions:\n" +
            "MHX2 file: %s\n" % vstring +
            "Must be between\n" +
            "0.%d and 0.%d" % (LowestVersion, HighestVersion))
            )

    return struct, time1


def build(struct, cfg, context):
    from .armature.build import buildRig
    from .armature.rigify import checkRigifyEnabled
    from .materials import buildMaterial
    from .geometries import buildGeometry, getScaleOffset
    from .proxy import setMhHuman

    scn = context.scene

    if (cfg.useOverride and
        cfg.rigType == 'RIGIFY' and
        cfg.finalizeRigify and
        not checkRigifyEnabled(context)):
        pass
        #raise MhxError("The Rigify add-on is not enabled. It is found under rigging.")

    mats = {}
    for mhMaterial in struct["materials"]:
        mname,mat = buildMaterial(mhMaterial, scn, cfg)
        mats[mname] = mat

    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhHuman)
            scn.MhxDesignHuman = getMhHuman()["name"]

    parser = None
    rig = None
    if cfg.useOverride:
        if cfg.useRig:
            if cfg.rigType == 'EXPORTED':
                if "skeleton" in struct.keys():
                    mhSkel = struct["skeleton"]
                    rig = buildSkeleton(mhSkel, scn, cfg)
            elif cfg.rigType in ['EXPORTED_MHX', 'EXPORTED_RIGIFY']:
                from .armature.rerig import isDefaultRig
                if "skeleton" in struct.keys():
                    mhSkel = struct["skeleton"]
                    if isDefaultRig(mhSkel):
                        rig,parser = buildRig(mhHuman, mhSkel, cfg, context)
                    else:
                        print("Can only build %s rig if the Default rig (with or without toes) was exported from MakeHuman." % cfg.rigType)
                        rig = buildSkeleton(mhSkel, scn, cfg)
            else:
                rig,parser = buildRig(mhHuman, None, cfg, context)
    elif "skeleton" in struct.keys():
        mhSkel = struct["skeleton"]
        rig = buildSkeleton(mhSkel, scn, cfg)

    if rig:
        rig.MhxScale = mhHuman["scale"]
        rig.MhxOffset = str(list(zup(mhHuman["offset"])))
        if "levator02.L" in rig.data.bones.keys():
            rig.MhxFaceRig = True
    mhHuman["parser"] = parser

    human = None
    proxies = []
    proxy = None
    for mhGeo in struct["geometries"]:
        if "proxy" in mhGeo.keys():
            mhProxy = mhGeo["proxy"]
            if mhGeo["human"]:
                if cfg.useHelpers:
                    if cfg.useHumanType != 'BASE':
                        proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "proxy_seed_mesh")
                        proxy.MhxHuman = True
                    if cfg.useHumanType != 'PROXY':
                        human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "seed_mesh")
                        human.MhxHuman = True
                else:
                    proxy = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, "mesh")
                    proxy.MhxHuman = True
                if proxy:
                    proxies.append((mhGeo, proxy))
            elif mhProxy["type"] == "Hair" and cfg.hairType != 'NONE':
                pass
            elif mhProxy["type"] == "Genitals" and cfg.genitalia != 'NONE':
                pass
            else:
                ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
                proxies.append((mhGeo, ob))
        elif mhGeo["human"]:
            human = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
            human.MhxHuman = True

    if proxy:
        proxy.MhxUuid = mhHuman["uuid"]

    groupName = mhHuman["name"].split(":",1)[0]

    if cfg.useOverride and cfg.genitalia != "NONE":
        genitalia = addMeshProxy("genitalia", cfg.genitalia, mhHuman, mats, rig, parser, scn, cfg)
        proxies.append(genitalia)

    if cfg.useOverride and cfg.useDeflector:
        from .hair import makeDeflector
        deflHead = addMeshProxy("deflector", "deflector_head", mhHuman, mats, None, None, scn, cfg)
        makeDeflector(deflHead, rig, ["head"], cfg)
        proxies.append(deflHead)
        deflTorso = addMeshProxy("deflector", "deflector_torso", mhHuman, mats, None, None, scn, cfg)
        makeDeflector(deflTorso, rig, ["chest-1","chest"], cfg)
        proxies.append(deflTorso)

    if cfg.useOverride and cfg.useRigify and cfg.finalizeRigify and rig:
        from .armature.rigify import fixRigifyMeshes
        fixRigifyMeshes(rig.children)

    if cfg.useOverride and cfg.hairType != "NONE":
        from .proxy import getProxyCoordinates
        folder = os.path.dirname(__file__)
        filepath = os.path.join(folder, "data/hm8/hair", cfg.hairType)
        hair,hcoords,_scales = getProxyCoordinates(mhHuman, filepath)

    if cfg.useOverride and cfg.useFaceShapes:
        from .shapekeys import addShapeKeys
        path = "data/hm8/faceshapes/faceshapes.mxa"
        proxyTypes = ["Proxymeshes", "Eyebrows", "Eyelashes", "Teeth", "Tongue"]
        addShapeKeys(human, path, mhHuman=mhHuman, proxies=proxies, proxyTypes=proxyTypes)

        if cfg.useFaceShapeDrivers:
            from .shapekeys import addShapeKeyDriversToAll
            meshes = [human] + [ob for (_,ob) in proxies]
            addShapeKeyDriversToAll(rig, meshes, "Mhf")
        elif parser and parser.boneDrivers:
            from .drivers import addBoneShapeDrivers
            addBoneShapeDrivers(rig, human, parser.boneDrivers, proxies=proxies, proxyTypes=proxyTypes)

    deselectAll(human, proxies, scn)

    if cfg.useOverride and cfg.useHelpers:
        from .masks import addMasks, selectAllMaskVGroups
        proxyTypes = ["Proxymeshes", "Genitals"]
        if cfg.useMasks == 'MODIFIER':
            addMasks(mhHuman, human, proxies, proxyTypes, cfg.useConservativeMasks)
        elif cfg.useMasks == 'APPLY':
            addMasks(mhHuman, human, proxies, proxyTypes, cfg.useConservativeMasks)
            selectAllMaskVGroups(human, proxies)
        elif cfg.useMasks == 'IGNORE':
            pass

    if (cfg.useOverride and cfg.useRig and cfg.useFaceRigDrivers and 
        cfg.rigType in ['EXPORTED_MHX', 'EXPORTED_RIGIFY']):
        from .armature.rerig import makeBonesPosable
        scn.objects.active = rig
        makeBonesPosable(rig, cfg.useMhx)

    if cfg.deleteHelpers:
        selectHelpers(human)

    if cfg.useOverride:
        deleteAllSelected(human, proxies, scn)

    grp = bpy.data.groups.new(groupName)
    if rig:
        grp.objects.link(rig)
    if human:
        grp.objects.link(human)
    for _,ob in proxies:
        grp.objects.link(ob)

    if cfg.useOverride and cfg.mergeBodyParts:
        from .merge import mergeBodyParts
        proxyTypes = ["Eyes", "Eyebrows", "Eyelashes", "Teeth", "Tongue", "Genitals"]
        if cfg.mergeMaxType == 'HAIR':
            proxyTypes += ['Hair']
        if cfg.mergeMaxType == 'CLOTHES':
            proxyTypes += ['Hair', 'Clothes']
        ob = getEffectiveHuman(human, proxy, cfg.mergeToProxy)
        if ob:
            mergeBodyParts(ob, proxies, scn, proxyTypes=proxyTypes)

    if cfg.useOverride and cfg.hairType != "NONE":
        from .hair import addHair
        ob = getEffectiveHuman(human, proxy, cfg.useHairOnProxy)
        if ob:
            reallySelect(ob, scn)
            addHair(ob, hair, hcoords, scn, cfg)

    if rig:
        reallySelect(rig, scn)
        bpy.ops.object.mode_set(mode='POSE')
    elif human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='OBJECT')
    elif proxy:
        reallySelect(proxy, scn)
        bpy.ops.object.mode_set(mode='OBJECT')


def getEffectiveHuman(human, proxy, useProxy):
    if proxy and (useProxy or not human):
        return proxy
    elif human and (not useProxy or not proxy):
        return human
    else:
        return None


def addMeshProxy(type, pname, mhHuman, mats, rig, parser, scn, cfg):
    from .proxy import addProxy
    from .geometries import buildGeometry

    filepath = os.path.join("data/hm8/%s" % type, pname.lower() + ".mxa")
    print("Adding %s:" % pname, filepath)
    mhGeo,scales = addProxy(filepath, mhHuman, mats, scn, cfg)
    ob = buildGeometry(mhGeo, mats, rig, parser, scn, cfg, cfg.getMeshType())
    ob.MhxScale = mhHuman["scale"]
    if "targets" in mhGeo.keys():
        from .shapekeys import addTargets
        addTargets(ob, mhGeo["targets"], scales)
    return mhGeo,ob


def buildSkeleton(mhSkel, scn, cfg):
    from .geometries import getScaleOffset
    from .bone_drivers import buildAnimation, buildExpressions

    rname = mhSkel["name"]
    amt = bpy.data.armatures.new(rname)
    rig = bpy.data.objects.new(rname, amt)
    amt.draw_type = 'STICK'
    rig.show_x_ray = True
    scn.objects.link(rig)
    reallySelect(rig, scn)

    scale,offset = getScaleOffset(mhSkel, cfg, True)
    bpy.ops.object.mode_set(mode='EDIT')
    for mhBone in mhSkel["bones"]:
        eb = amt.edit_bones.new(mhBone["name"])
        eb.head = zup(mhBone["head"])+offset
        eb.tail = zup(mhBone["tail"])+offset
        if "matrix" in mhBone.keys():
            mat = Matrix(mhBone["matrix"])
            nmat = Matrix((mat[0], -mat[2], mat[1])).to_3x3().to_4x4()
            nmat.col[3] = eb.matrix.col[3]
            eb.matrix = nmat
        else:
            eb.roll = mhBone["roll"]
        if "parent" in mhBone.keys():
            eb.parent = amt.edit_bones[mhBone["parent"]]

    bpy.ops.object.mode_set(mode='OBJECT')
    for mhBone in mhSkel["bones"]:
        pb = rig.pose.bones[mhBone["name"]]
        if pb.parent:
            pb.lock_location = [True,True,True]

    rig.MhxRig = "Exported"
    buildExpressions(mhSkel, rig, scn, cfg)
    buildAnimation(mhSkel, rig, scn, offset, cfg)
    return rig

#------------------------------------------------------------------------
#   Selecting and deleting verts
#------------------------------------------------------------------------

def deselectAll(human, proxies, scn):
    if human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
    for _,pxy in proxies:
        reallySelect(pxy, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')


def deleteAllSelected(human, proxies, scn):
    if human:
        reallySelect(human, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
    for _,pxy in proxies:
        reallySelect(pxy, scn)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')


def selectHelpers(human):
    if human is None:
        return
    for vn in range(NBodyVerts, NTotalVerts):
        human.data.vertices[vn].select = True

#------------------------------------------------------------------------
#   Design human
#------------------------------------------------------------------------

def setDesignHuman(filepath, context):
    filepath = os.path.expanduser(filepath)
    struct, _time1 = importMhx2Json(filepath)
    for mhGeo in struct["geometries"]:
        if mhGeo["human"]:
            mhHuman = mhGeo
            setMhHuman(mhGeo)
            context.scene.MhxDesignHuman = getMhHuman()["name"]
            return
    raise MhxError("Unable to set design human")


class VIEW3D_OT_SetDesignHumanButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx2.set_design_human"
    bl_label = "Set Design Human (.mhx2)"
    bl_description = "Load definition of human to be designed"
    bl_options = {'UNDO'}

    filename_ext = ".mhx2"
    filter_glob = StringProperty(default="*.mhx2", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to mhx2 file", maxlen=1024, default="")

    def execute(self, context):
        try:
            setDesignHuman(self.properties.filepath, context)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_ClearDesignHumanButton(bpy.types.Operator):
    bl_idname = "mhx2.clear_design_human"
    bl_label = "Clear Design Human"
    bl_description = "Clear definition of human to be designed"
    bl_options = {'UNDO'}

    def execute(self, context):
        mhHuman = None
        context.scene.MhxDesignHuman = "None"
        return{'FINISHED'}
