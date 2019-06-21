"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Project to proxy

"""

import bpy
import os

#

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
        #if (first+rlen) != mlen:
        #    raise NameError( "Bug: %d refVerts != %d meshVerts" % (first+rlen, mlen) )
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
                vw = CProxy.getWeight(verts[refVert], gn)
            grp.add([vert.index], vw, 'REPLACE')
        return

    def cornerWeights(self, vn):
        n = vn - self.firstVert
        refVert = self.refVerts[n]
        if type(refVert) == tuple:
            (rv0, rv1, rv2, w0, w1, w2, d0, d1, d2) = refVert
            return [(w0,rv0), (w1,rv1), (w2,rv2)]
        else:
            return [(1,refVert)]

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

#
#   class VIEW3D_OT_ProjectMaterialsButton(bpy.types.Operator):
#

from random import random

class VIEW3D_OT_ProjectMaterialsButton(bpy.types.Operator):
    bl_idname = "mhw.project_materials"
    bl_label = "Project materials from proxy"

    def execute(self, context):
        ob = context.object
        proxy = CProxy()
        proxy.read(os.path.join(the3dobjFolder, "base.mhclo"))
        grps = baseFileGroups()
        grpList = set(grps.values())
        grpIndices = {}
        grpNames = {}
        n = 0
        for grp in grpList:
            mat = bpy.data.materials.new(grp)
            ob.data.materials.append(mat)
            mat.diffuse_color = (random(), random(), random())
            grpIndices[grp] = n
            grpNames[n] = grp
            n += 1

        vertFaces = {}
        for v in ob.data.vertices:
            vertFaces[v.index] = []

        for f in ob.data.polygons:
            for vn in f.vertices:
                vertFaces[vn].append(f)
                if vn >= proxy.firstVert:
                    grp = None
                    continue
                grp = grps[f.index]
            if grp:
                f.material_index = grpIndices[grp]

        for f in ob.data.polygons:
            if f.vertices[0] >= proxy.firstVert:
                cwts = []
                for vn in f.vertices:
                    cwts += proxy.cornerWeights(vn)
                cwts.sort()
                cwts.reverse()
                (w,vn) = cwts[0]
                for f1 in vertFaces[vn]:
                    mn = f1.material_index
                    f.material_index = f1.material_index
                    continue

        print("Material projected from proxy")
        return{'FINISHED'}

#
#   class VIEW3D_OT_ProjectWeightsButton(bpy.types.Operator):
#

class VIEW3D_OT_ProjectWeightsButton(bpy.types.Operator):
    bl_idname = "mhw.project_weights"
    bl_label = "Project weights from proxy"

    def execute(self, context):
        ob = context.object
        proxy = CProxy()
        filepath = os.path.join(os.path.dirname(__file__), "../maketarget/data/a8_v69_clothes.mhclo")
        proxy.read(filepath)
        for grp in ob.vertex_groups:
            print(grp.name)
            proxy.setWeights(ob.data.vertices, grp)
        print("Weights projected from proxy")
        return{'FINISHED'}

#
#
#

SkirtFront = [
  [18115, 18116, 18117, 18119, 18126, 18133, 18134, 18135, 18136, 18138, 18145, ],
  [18151, 18152, 18153, 18155, 18162, 18169, 18170, 18171, 18172, 18174, 18181, ],
  [18187, 18188, 18189, 18191, 18198, 18205, 18206, 18207, 18208, 18210, 18217, ],
  [18223, 18224, 18225, 18227, 18234, 18241, 18242, 18243, 18244, 18246, 18253, ],
  [18259, 18260, 18261, 18263, 18270, 18277, 18278, 18279, 18280, 18282, 18289, ],
  [18295, 18296, 18297, 18299, 18306, 18313, 18314, 18315, 18316, 18318, 18325, ],
  [18331, 18332, 18333, 18335, 18342, 18349, 18350, 18351, 18352, 18354, 18361, ],
  [18367, 18368, 18369, 18371, 18378, 18385, 18386, 18387, 18388, 18390, 18397, ],
  [18403, 18404, 18405, 18407, 18414, 18421, 18422, 18423, 18424, 18426, 18433, ],
  [18439, 18440, 18441, 18443, 18450, 18457, 18458, 18459, 18460, 18462, 18469, ],
  [18475, 18476, 18477, 18479, 18486, 18493, 18494, 18495, 18496, 18498, 18505, ],
  [18511, 18512, 18513, 18515, 18522, 18529, 18530, 18531, 18532, 18534, 18541, ],
  [18547, 18548, 18549, 18551, 18558, 18565, 18566, 18567, 18568, 18570, 18577, ],
  [18583, 18584, 18585, 18587, 18594, 18601, 18602, 18603, 18604, 18606, 18613, ],
  [18619, 18620, 18621, 18623, 18630, 18637, 18638, 18639, 18640, 18642, 18649, ],
  [18655, 18656, 18657, 18659, 18666, 18673, 18674, 18675, 18676, 18678, 18685, ],
  [18691, 18692, 18693, 18695, 18702, 18709, 18710, 18711, 18712, 18714, 18721, ]
]

SkirtBack = [
  [18147, 18148, 18149, 18150, 18161, 18164, 18165, 18166, 18167, 18168, 18180, ],
  [18183, 18184, 18185, 18186, 18197, 18200, 18201, 18202, 18203, 18204, 18216, ],
  [18219, 18220, 18221, 18222, 18233, 18236, 18237, 18238, 18239, 18240, 18252, ],
  [18255, 18256, 18257, 18258, 18269, 18272, 18273, 18274, 18275, 18276, 18288, ],
  [18291, 18292, 18293, 18294, 18305, 18308, 18309, 18310, 18311, 18312, 18324, ],
  [18327, 18328, 18329, 18330, 18341, 18344, 18345, 18346, 18347, 18348, 18360, ],
  [18363, 18364, 18365, 18366, 18377, 18380, 18381, 18382, 18383, 18384, 18396, ],
  [18399, 18400, 18401, 18402, 18413, 18416, 18417, 18418, 18419, 18420, 18432, ],
  [18435, 18436, 18437, 18438, 18449, 18452, 18453, 18454, 18455, 18456, 18468, ],
  [18471, 18472, 18473, 18474, 18485, 18488, 18489, 18490, 18491, 18492, 18504, ],
  [18507, 18508, 18509, 18510, 18521, 18524, 18525, 18526, 18527, 18528, 18540, ],
  [18543, 18544, 18545, 18546, 18557, 18560, 18561, 18562, 18563, 18564, 18576, ],
  [18579, 18580, 18581, 18582, 18593, 18596, 18597, 18598, 18599, 18600, 18612, ],
  [18615, 18616, 18617, 18618, 18629, 18632, 18633, 18634, 18635, 18636, 18648, ],
  [18651, 18652, 18653, 18654, 18665, 18668, 18669, 18670, 18671, 18672, 18684, ],
  [18687, 18688, 18689, 18690, 18701, 18704, 18705, 18706, 18707, 18708, 18720, ]
]

def smoothenSkirt(ob):
    from .vgroup import setupVGroups
    vgroups = setupVGroups(ob)

    for row in SkirtFront + SkirtBack:
        verts = [ob.data.vertices[vn] for vn in row]
        orderedVerts = [(v.co[0], v) for v in verts]
        orderedVerts.sort()
        verts = [v for _,v in orderedVerts]
        verts = verts[1:-1]

        v0 = verts[0]
        rowGroups = {}
        for g in v0.groups:
            try:
                vg = vgroups[g.group]
            except KeyError:
                print(v0, g, g.group)
                print(list(v0.groups))
            if vg.name[-2:] == ".R":
                delta = g.weight/(len(verts)-1)
                rGroup = rowGroups[vg.name] = []
                lGroup = rowGroups[vg.name[:-2] + ".L"] = []
                for n in range(len(verts)):
                    rGroup.append((g.weight - n*delta))
                    lGroup.append((n*delta))
            else:
                group = rowGroups[vg.name] = []
                for n in range(len(verts)):
                    group.append(g.weight)

        for v in verts:
            for g in v.groups:
                try:
                    vg = vgroups[g.group]
                except KeyError:
                    print(v0, g, g.group)
                    print(list(v0.groups))
                vg.remove([v.index])

        for gname,weights in rowGroups.items():
            vg = ob.vertex_groups[gname]
            print(vg)
            for n,v in enumerate(verts):
                vg.add([v.index], weights[n], 'REPLACE')


class VIEW3D_OT_SmoothenSkirtButton(bpy.types.Operator):
    bl_idname = "mhw.smoothen_skirt"
    bl_label = "Smoothen skirt"

    def execute(self, context):
        smoothenSkirt(context.object)
        print("Skirt smoothened")
        return{'FINISHED'}




#
#   exportObjFile(context):
#   setupTexVerts(ob, scn):
#

def exportObjFile(context):
    fp = open(os.path.join(the3dobjFolder, "base3.obj"), "w")
    scn = context.scene
    me = context.object.data
    for v in me.vertices:
        fp.write("v %.4f %.4f %.4f\n" % (v.co[0], v.co[2], -v.co[1]))

    for v in me.vertices:
        fp.write("vn %.4f %.4f %.4f\n" % (v.normal[0], v.normal[2], -v.normal[1]))

    if me.uv_textures:
        (uvFaceVerts, texVerts, nTexVerts) = setupTexVerts(me, scn)
        for vtn in range(nTexVerts):
            vt = texVerts[vtn]
            fp.write("vt %.4f %.4f\n" % (vt[0], vt[1]))
        n = 1
        mn = -1
        for f in me.polygons:
            if f.material_index != mn:
                mn = f.material_index
                fp.write("g %s\n" % me.materials[mn].name)
            uvVerts = uvFaceVerts[f.index]
            fp.write("f ")
            for n,v in enumerate(f.vertices):
                (vt, uv) = uvVerts[n]
                fp.write("%d/%d " % (v+1, vt+1))
            fp.write("\n")
    else:
        for f in me.polygons:
            fp.write("f ")
            for vn in f.vertices:
                fp.write("%d " % (vn+1))
            fp.write("\n")

    fp.close()
    print("base3.obj written")
    return

def setupTexVerts(me, scn):
    vertEdges = {}
    vertFaces = {}
    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    for f in me.polygons:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in me.polygons:
        faceEdges[f.index] = []
    for f in me.polygons:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)

    faceNeighbors = {}
    uvFaceVerts = {}
    for f in me.polygons:
        faceNeighbors[f.index] = []
        uvFaceVerts[f.index] = []
    for f in me.polygons:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvtex = me.uv_textures[0]
    vtn = 0
    texVerts = {}
    for f in me.polygons:
        uvf = uvtex.data[f.index]
        vtn = findTexVert(uvf.uv1, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        vtn = findTexVert(uvf.uv2, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        vtn = findTexVert(uvf.uv3, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
        if len(f.vertices) > 3:
            vtn = findTexVert(uvf.uv4, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn)
    return (uvFaceVerts, texVerts, vtn)

def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, scn):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < scn.MhxEpsilon:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1

class VIEW3D_OT_ExportBaseObjButton(bpy.types.Operator):
    bl_idname = "mhw.export_base_obj"
    bl_label = "Export base3.obj"

    def execute(self, context):
        exportObjFile(context)
        return{'FINISHED'}
