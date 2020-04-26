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

from .utils import *
from .hm8 import *

#------------------------------------------------------------------------
#   Masking
#------------------------------------------------------------------------

def addMasks(mhHuman, human, proxies, proxyTypes, useConservativeMasks):
    for mhGeo,ob in proxies:
        mhProxy = mhGeo["proxy"]
        if "delete_verts" not in mhProxy.keys():
            continue
        vnums = getDeleteVerts(mhHuman, mhProxy, useConservativeMasks)
        pname = getProxyName(ob)
        if human:
            addMask(human, vnums, pname)
        for mhGeo1,ob1 in proxies:
            if ob == ob1:
                continue
            mhProxy1 = mhGeo1["proxy"]
            if mhProxy1["type"] in proxyTypes:
                if "proxy_seed_mesh" in mhGeo1.keys():
                    mhMesh = mhGeo1["proxy_seed_mesh"]
                else:
                    mhMesh = mhGeo1["seed_mesh"]
                pvnums = proxifyMask(mhProxy1, mhMesh, vnums)
                if pvnums:
                    addMask(ob1, pvnums, pname)


def addMask(ob, vnums, pname):
    if vnums:
        mod = ob.modifiers.new("Mask:%s" % pname, 'MASK')
        vgrp = ob.vertex_groups.new("Delete:%s" % pname)
        mod.vertex_group = vgrp.name
        mod.invert_vertex_group = True
        for vn in vnums:
            vgrp.add([vn], 1, 'REPLACE')


def selectAllMaskVGroups(human, proxies):
    selectMaskVGroups(human)
    for _,pxy in proxies:
        selectMaskVGroups(pxy)


def selectMaskVGroups(ob):
    if not ob:
        return

    delMods = []
    for mod in ob.modifiers:
        if mod.type == 'MASK':
            delMods.append(mod)
            try:
                vgrp = ob.vertex_groups[mod.vertex_group]
            except KeyError:
                vgrp = None
                print("Did not find vertex group %s" % grpname)
            if vgrp:
                for v in ob.data.vertices:
                    for g in v.groups:
                        if g.group == vgrp.index:
                            v.select = True
                ob.vertex_groups.remove(vgrp)
    for mod in delMods:
        ob.modifiers.remove(mod)


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def getDeleteVerts(mhHuman, mhProxy, useConservativeMasks):
    vnums = [vn for vn,delete in enumerate(mhProxy["delete_verts"]) if delete]
    if not useConservativeMasks:
        return vnums
    if ("conservative" in mhProxy.keys() and
        not mhProxy["conservative"]):
        return vnums

    mhMesh = mhHuman["seed_mesh"]
    nVerts = len(mhMesh["vertices"])
    nFaces = len(mhMesh["faces"])
    vertsFaces = dict([(vn, []) for vn in range(nVerts)])
    facesVerts = {}
    for fn,f in enumerate(mhMesh["faces"]):
        facesVerts[fn] = f
        for vn in f:
            vertsFaces[vn].append(fn)

    nFaceVerts = dict([(fn,0) for fn in range(nFaces)])
    for vn in vnums:
        for fn in vertsFaces[vn]:
            nFaceVerts[fn] += 1

    delVerts = dict([(vn,True) for vn in range(nVerts)])
    for fn,ndel in nFaceVerts.items():
        if ndel <= 2:
            for vn in facesVerts[fn]:
                delVerts[vn] = False

    vnums = [vn for vn,delete in delVerts.items() if delete]
    return vnums

# ---------------------------------------------------------------------
#   Proxify masks
# ---------------------------------------------------------------------

def proxifyMask(mhProxy, mhMesh, vnums):
    from .proxy import proxifyVertexGroups

    vgrps = { "Mask" : [(vn,1.0) for vn in vnums] }
    mhHuman = {
        "seed_mesh" : {
            "weights" : vgrps
        }
    }
    ngrps = proxifyVertexGroups(mhProxy, mhHuman)

    if "Mask" in ngrps.keys():
        nverts = len(mhMesh["vertices"])
        vmask = dict([(vn,0) for vn in range(nverts)])
        for vn,w in ngrps["Mask"]:
            vmask[vn] = w
        vclear = dict([(vn,False) for vn in range(nverts)])
        for f in mhMesh["faces"]:
            if vmask[f[0]]*vmask[f[1]]*vmask[f[2]]*vmask[f[3]] < 0.5:
                vclear[f[0]] = vclear[f[1]] = vclear[f[2]] = vclear[f[3]] = True
        pvnums = [vn for vn,test in vclear.items() if not test]
        pvnums.sort()
    else:
        pvnums = []
    return pvnums
