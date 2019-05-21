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
from .utils import *
from .hm8 import *

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def buildGeometry(mhGeo, mats, rig, parser, scn, cfg, meshType):
    from .proxy import proxifyVertexGroups

    mhMesh = mhGeo[meshType]

    if meshType == "proxy_seed_mesh" and mhGeo["human"]:
        gname = ("%s:Proxy" % mhGeo["name"].split(':',1)[0])
        ob = buildMesh(mhGeo, mhMesh, gname, scn, cfg, True)
        ob.MhxSeedMesh = True
    elif meshType == "seed_mesh" and mhGeo["human"]:
        gname = ("%s:Body" % mhGeo["name"].split(':',1)[0])
        ob = buildMesh(mhGeo, mhMesh, gname, scn, cfg, True)
        ob.MhxSeedMesh = True
    else:
        gname = mhGeo["name"]
        useSeedMesh = (meshType == "seed_mesh")
        ob = buildMesh(mhGeo, mhMesh, gname, scn, cfg, useSeedMesh)
        ob.MhxSeedMesh = useSeedMesh
        
    ob.MhxUuid = mhGeo["uuid"]
    if "license" in mhGeo.keys():
        mhLicense = mhGeo["license"]
        if isinstance(mhLicense, dict):
            ob.MhxAuthor = mhLicense["author"]
            ob.MhxLicense = mhLicense["license"]
            ob.MhxHomePage = mhLicense["homepage"]

    vgrps = None
    if cfg.useOverride:
        if cfg.useRig:
            if meshType == "proxy_seed_mesh":
                vgrps = proxifyVertexGroups(mhGeo["proxy"], getMhHuman(), parser)
            elif mhGeo["human"]:
                vgrps = meshVertexGroups(mhMesh, parser, cfg)
            else:
                vgrps = proxifyVertexGroups(mhGeo["proxy"], getMhHuman())

    elif "weights" in mhMesh.keys():
        vgrps = mhMesh["weights"]

    if vgrps:
        buildVertexGroups(vgrps, ob, rig)

    if rig:
        ob.parent = rig
        ob.lock_location = (True,True,True)
        ob.lock_rotation = (True,True,True)
        ob.lock_scale = (True,True,True)

    if cfg.useSubsurf:
        mod = ob.modifiers.new("Subsurf", 'SUBSURF')
        mod.levels = cfg.subsurfLevels
        mod.render_levels = cfg.subsurfRenderLevels
    elif "issubdivided" in mhGeo.keys() and mhGeo["issubdivided"]:
        mod = ob.modifiers.new("Subsurf", 'SUBSURF')
        mod.levels = 1
        mod.render_levels = 1              

    mat = mats[mhGeo["material"]]
    ob.data.materials.append(mat)
    return ob


def meshVertexGroups(mhMesh, parser, cfg):
    if parser:
        return parser.vertexGroups
    elif (cfg.rigType == 'EXPORTED' and
          "weights" in mhMesh.keys()):
        return mhMesh["weights"]
    else:
        return {}


def buildMesh(mhGeo, mhMesh, gname, scn, cfg, useSeedMesh):
    scale,offset = getScaleOffset(mhGeo, cfg, useSeedMesh)
    print("BUILD", mhGeo["name"], mhGeo["scale"], scale, offset)
    verts = [scale*zup(co)+offset for co in mhMesh["vertices"]]
    ob = addMeshToScene(verts, gname, mhMesh, scn)
    ob.MhxScale = mhGeo["scale"]
    ob.MhxOffset = str(list(zup(mhGeo["offset"])))
    return ob


def addMeshToScene(verts, gname, mhMesh, scn):
    me = bpy.data.meshes.new(gname)
    try:
        faces = mhMesh["faces"]
        edges = []
    except KeyError:
        edges = mhMesh["edges"]
        faces = []
    me.from_pydata(verts, edges, faces)

    for f in me.polygons:
        f.use_smooth = True

    uvtex = me.uv_textures.new()
    uvlayer = me.uv_layers.active
    uvcoords = mhMesh["uv_coordinates"]
    n = 0
    for f in mhMesh["uv_faces"]:
        for vn in f:
            uvlayer.data[n].uv = uvcoords[vn]
            n += 1

    ob = bpy.data.objects.new(gname, me)
    scn.objects.link(ob)
    return ob


def buildVertexGroups(vweights, ob, rig):
    mod = ob.modifiers.new('ARMATURE', 'ARMATURE')
    mod.use_vertex_groups = True
    mod.use_bone_envelopes = False
    mod.object = rig

    for vgname,data in vweights.items():
        vgrp = ob.vertex_groups.new(vgname)
        for vn,w in data:
            vgrp.add([vn], w, 'REPLACE')


def getVertexGroupsFromObject(ob):
    vgrps = dict([(vgrp.index, (vgrp.name, [])) for vgrp in ob.vertex_groups])
    for v in ob.data.vertices:
        for g in v.groups:
            vgrps[g.group][1].append((v.index, g.weight))
    return dict(vgrps.values())


def getScaleOffset(struct, cfg, useSeedMesh):
    if useSeedMesh:
        scale = struct["scale"]
    else:
        scale = 1
    if cfg.useOffset:
        offset = zup(struct["offset"])
    else:
        offset = Vector((0,0,0))
    return scale,offset

