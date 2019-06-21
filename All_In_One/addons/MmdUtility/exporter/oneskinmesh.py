# coding: utf-8
import bpy
from . import vertexarray
from .. import bl
from ..pymeshio import englishmap


def duplicate(scene, o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select=True
    scene.objects.active=o
    bpy.ops.object.duplicate()
    dumy=scene.objects.active
    #bpy.ops.object.rotation_apply()
    #bpy.ops.object.scale_apply()
    #bpy.ops.object.location_apply()
    dumy.data.update(calc_tessface=True)
    return dumy.data, dumy

def getVertexGroup(o, name):
    indices=[]
    for i, v in enumerate(o.data.vertices):
        for g in v.groups:
            if o.vertex_groups[g.group].name==name:
                indices.append(i)
    return indices

def getFaceUV(mesh, i, faces, count=3):
    active_uv_texture=None
    for t in mesh.tessface_uv_textures:
        if t.active:
            active_uv_texture=t
            break
    if active_uv_texture and active_uv_texture.data[i]:
        uvFace=active_uv_texture.data[i]
        if count==3:
            return (uvFace.uv1, uvFace.uv2, uvFace.uv3)
        elif count==4:
            return (uvFace.uv1, uvFace.uv2, uvFace.uv3, uvFace.uv4)
        else:
            print(count)
            assert(False)
    else:
        return ((0, 0), (0, 0), (0, 0), (0, 0))


class Morph(object):
    __slots__=['name', 'type', 'offsets']
    def __init__(self, name, type):
        self.name=name
        self.type=type
        self.offsets=[]

    def add(self, index, offset):
        self.offsets.append((index, offset))

    def sort(self):
        self.offsets.sort(key=lambda e: e[0])

    def __str__(self):
        return "<Morph %s>" % self.name


class SSS(object):
    def __init__(self):
        self.use=1


class DefaultMaterial(dict):
    def __init__(self):
        self.name='default'
        # diffuse
        self.diffuse_color=[1, 1, 1]
        self.alpha=1
        # specular
        self.specular_toon_size=0
        self.specular_hardness=5
        self.specular_color=[1, 1, 1]
        # ambient
        self.mirror_color=[0, 0, 0]
        # flag
        self.subsurface_scattering=SSS()
        # texture
        self.texture_slots=[]


class OneSkinMesh(object):
    __slots__=['vertexArray', 'morphList', 'rigidbodies', 'constraints', 'armatureObj']
    def __init__(self):
        self.vertexArray=vertexarray.VertexArray()
        self.morphList=[]
        self.rigidbodies=[]
        self.constraints=[]
        self.armatureObj=None

    def __str__(self):
        return "<OneSkinMesh %s, morph:%d>" % (
                self.vertexArray,
                len(self.morphList))

    def build(self, scene, node):
        ############################################################
        # search armature modifier
        ############################################################
        for m in node.o.modifiers:
            if m.type=='ARMATURE':
                armatureObj=m.object
                if not self.armatureObj:
                    self.armatureObj=armatureObj
                elif self.armatureObj!=armatureObj:
                    print("warning! found multiple armature. ignored.", 
                            armatureObj.name)

        if node.o.type.upper()=='MESH':
            self.addMesh(scene, node.o)

        for child in node.children:
            self.build(scene, child)

    def addMesh(self, scene, obj):
        if obj.hide:
            return
        self.__mesh(scene, obj)
        self.__rigidbody(obj)
        self.__constraint(obj)

    def __getWeightMap(self, obj, mesh):
        # bone weight
        weightMap={}
        secondWeightMap={}
        def setWeight(i, name, w):
            if w>0:
                if i in weightMap:
                    if i in secondWeightMap:
                        # 上位２つのweightを採用する
                        if w<secondWeightMap[i][1]:
                            pass
                        elif w<weightMap[i][1]:
                            # ２つ目を入れ替え
                            secondWeightMap[i]=(name, w)
                        else:
                            # １つ目を入れ替え
                            weightMap[i]=(name, w)
                    else:
                        if w>weightMap[i][1]:
                            # 多い方をweightMapに
                            secondWeightMap[i]=weightMap[i]
                            weightMap[i]=(name, w)
                        else:
                            secondWeightMap[i]=(name, w)
                else:
                    weightMap[i]=(name, w)

        # ToDo bone weightと関係ないvertex groupを除外する
        for i, v in enumerate(mesh.vertices):
            if len(v.groups)>0:
                for g in v.groups:
                    setWeight(i, obj.vertex_groups[g.group].name, g.weight)
            else:
                try:
                    setWeight(i, obj.vertex_groups[0].name, 1)
                except:
                    # no vertex_groups
                    pass

        # 合計値が1になるようにする
        for i in range(len(mesh.vertices)):
            if i in secondWeightMap:
                secondWeightMap[i]=(secondWeightMap[i][0], 1.0-weightMap[i][1])
            elif i in weightMap:
                weightMap[i]=(weightMap[i][0], 1.0)
                secondWeightMap[i]=("", 0)
            else:
                print("no weight vertex")
                weightMap[i]=("", 0)
                secondWeightMap[i]=("", 0)

        return weightMap, secondWeightMap

    def __processFaces(self, obj_name, mesh, weightMap, secondWeightMap):
        default_material=DefaultMaterial()
        # 各面の処理
        for i, face in enumerate(mesh.tessfaces):
            faceVertexCount=len(face.vertices)
            try:
                material=mesh.materials[face.material_index]
            except IndexError as e:
                material=default_material
            v=[mesh.vertices[index] for index in face.vertices]
            uv=getFaceUV(
                    mesh, i, face, len(face.vertices))

            if face.use_smooth:
                if faceVertexCount==3:
                    self.__addFaceTriangleSmooth(
                            obj_name, material, v, uv, 
                            weightMap, secondWeightMap
                            )
                elif faceVertexCount==4:
                    self.__addFaceQuadrangleSmooth(
                            obj_name, material, v, uv,
                            weightMap, secondWeightMap
                            )
            else:
                if faceVertexCount==3:
                    self.__addFaceTriangleSolid(
                            obj_name, material, v, uv, 
                            face.normal,
                            weightMap, secondWeightMap
                            )
                elif faceVertexCount==4:
                    self.__addFaceQuadrangleSolid(
                            obj_name, material, v, uv, 
                            face.normal,
                            weightMap, secondWeightMap
                            )

    def __addFaceTriangleSmooth(self, obj_name, material, v, uv,
            weightMap, secondWeightMap):
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[0].index, 
                v[1].index, 
                v[2].index,
                v[0].co, 
                v[1].co, 
                v[2].co,
                v[0].normal, 
                v[1].normal, 
                v[2].normal,
                uv[0], 
                uv[1], 
                uv[2],
                weightMap[v[0].index][0],
                weightMap[v[1].index][0],
                weightMap[v[2].index][0],
                secondWeightMap[v[0].index][0],
                secondWeightMap[v[1].index][0],
                secondWeightMap[v[2].index][0],
                weightMap[v[0].index][1],
                weightMap[v[1].index][1],
                weightMap[v[2].index][1]
                )

    def __addFaceQuadrangleSmooth(self, obj_name, material, v, uv,
            weightMap, secondWeightMap):
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[0].index, 
                v[1].index, 
                v[2].index,
                v[0].co, 
                v[1].co, 
                v[2].co,
                v[0].normal, 
                v[1].normal, 
                v[2].normal, 
                uv[0], 
                uv[1], 
                uv[2],
                weightMap[v[0].index][0],
                weightMap[v[1].index][0],
                weightMap[v[2].index][0],
                secondWeightMap[v[0].index][0],
                secondWeightMap[v[1].index][0],
                secondWeightMap[v[2].index][0],
                weightMap[v[0].index][1],
                weightMap[v[1].index][1],
                weightMap[v[2].index][1]
                )
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[2].index, 
                v[3].index, 
                v[0].index,
                v[2].co, 
                v[3].co, 
                v[0].co,
                v[2].normal, 
                v[3].normal, 
                v[0].normal, 
                uv[2], 
                uv[3], 
                uv[0],
                weightMap[v[2].index][0],
                weightMap[v[3].index][0],
                weightMap[v[0].index][0],
                secondWeightMap[v[2].index][0],
                secondWeightMap[v[3].index][0],
                secondWeightMap[v[0].index][0],
                weightMap[v[2].index][1],
                weightMap[v[3].index][1],
                weightMap[v[0].index][1]
                )

    def __addFaceTriangleSolid(self, obj_name, material, v, uv, normal,
            weightMap, secondWeightMap):
        # flip triangle
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[0].index, 
                v[1].index, 
                v[2].index,
                v[0].co, 
                v[1].co, 
                v[2].co,
                normal, 
                normal, 
                normal,
                uv[0], 
                uv[1], 
                uv[2],
                weightMap[v[0].index][0],
                weightMap[v[1].index][0],
                weightMap[v[2].index][0],
                secondWeightMap[v[0].index][0],
                secondWeightMap[v[1].index][0],
                secondWeightMap[v[2].index][0],
                weightMap[v[0].index][1],
                weightMap[v[1].index][1],
                weightMap[v[2].index][1]
                )

    def __addFaceQuadrangleSolid(self, obj_name, material, v, uv, normal,
            weightMap, secondWeightMap):
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[0].index, 
                v[1].index, 
                v[2].index,
                v[0].co, 
                v[1].co, 
                v[2].co,
                normal,
                normal,
                normal,
                uv[0], 
                uv[1], 
                uv[2],
                weightMap[v[0].index][0],
                weightMap[v[1].index][0],
                weightMap[v[2].index][0],
                secondWeightMap[v[0].index][0],
                secondWeightMap[v[1].index][0],
                secondWeightMap[v[2].index][0],
                weightMap[v[0].index][1],
                weightMap[v[1].index][1],
                weightMap[v[2].index][1]
                )
        self.vertexArray.addTriangle(
                obj_name, material.name,
                v[2].index, 
                v[3].index, 
                v[0].index,
                v[2].co, 
                v[3].co, 
                v[0].co,
                normal, 
                normal, 
                normal, 
                uv[2], 
                uv[3], 
                uv[0],
                weightMap[v[2].index][0],
                weightMap[v[3].index][0],
                weightMap[v[0].index][0],
                secondWeightMap[v[2].index][0],
                secondWeightMap[v[3].index][0],
                secondWeightMap[v[0].index][0],
                weightMap[v[2].index][1],
                weightMap[v[3].index][1],
                weightMap[v[0].index][1]
                )

    def __mesh(self, scene, obj):
        if bl.RIGID_SHAPE_TYPE in obj:
            return
        if bl.CONSTRAINT_A in obj:
            return

        #bl.message("export: %s" % obj.name)

        # メッシュのコピーを生成してオブジェクトの行列を適用する
        copyMesh, copyObj=duplicate(scene, obj)
        copyObj.name="tmp_object"
        if len(copyMesh.vertices)>0:
            # apply transform
            copyMesh.transform(obj.matrix_world)
            if copyObj.data.shape_keys:
                matrix=obj.matrix_world
                for key in copyMesh.shape_keys.key_blocks:
                    for point in key.data:
                        point.co=matrix*point.co
            copyMesh.calc_normals()

            # apply modifier
            for m in [m for m in copyObj.modifiers]:
                if m.type=='SOLIDFY':
                    continue
                elif m.type=='ARMATURE':
                    continue
                elif m.type=='MIRROR':
                    bpy.ops.object.modifier_apply(modifier=m.name)
                else:
                    print(m.type)

            # fix empty tessfaces(from blender2.66?)
            copyMesh.update(calc_tessface=True)

            weightMap, secondWeightMap=self.__getWeightMap(copyObj, copyMesh)
            self.__processFaces(obj.name, copyMesh, weightMap, secondWeightMap)
            self.__weights(copyObj, copyMesh, obj.name)
            self.__skin(copyObj, obj.name)
        scene.objects.unlink(copyObj)

    def createEmptyBasicSkin(self):
        self.__getOrCreateMorph('base', 0)

    def __skin(self, obj, obj_name):
        if not obj.data.shape_keys:
            return

        indexRelativeMap={}
        blenderMesh=obj.data
        baseMorph=None

        # shape keys
        vg=getVertexGroup(obj, bl.MMD_SHAPE_GROUP_NAME)
        if len(vg)==0:
            vg=list(range(len(blenderMesh.vertices)))

        # base
        used=set()
        for b in obj.data.shape_keys.key_blocks:
            if b.name==bl.BASE_SHAPE_NAME:
                baseMorph=self.__getOrCreateMorph('base', 0)
                basis=b

                relativeIndex=len(baseMorph.offsets)
                for index in vg:
                    v=b.data[index].co

                    pos=[v[0], v[1], v[2]]

                    indices=self.vertexArray.getMappedIndex(obj_name, index)
                    for attribute, i in indices.items():
                        if i in used:
                            continue
                        used.add(i)

                        baseMorph.add(i, pos)
                        indexRelativeMap[i]=relativeIndex
                        relativeIndex+=1

                break
        assert(basis)
        #print(basis.name, len(baseMorph.offsets))

        if len(baseMorph.offsets)==0:
            return

        # shape keys
        for b in obj.data.shape_keys.key_blocks:
            if b.name==bl.BASE_SHAPE_NAME:
                continue

            morph=self.__getOrCreateMorph(b.name, 4)
            used=set()
            for index, src, dst in zip(
                    range(len(blenderMesh.vertices)),
                    (k.co for k in basis.data),
                    (k.co for k in b.data),
                    ):
                offset=[dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]]
                if offset[0]==0 and offset[1]==0 and offset[2]==0:
                    continue
                if index in vg:
                    indices=self.vertexArray.getMappedIndex(obj_name, index)
                    for attribute, i in indices.items():
                        if i in used:
                            continue
                        used.add(i) 
                        morph.add(indexRelativeMap[i], offset)
            assert(len(morph.offsets)<=len(baseMorph.offsets))

        # sort skinmap
        original=self.morphList[:]
        def getIndex(morph):
            for i, v in enumerate(englishmap.skinMap):
                if v[0]==morph.name:
                    return i
            #print(morph)
            return len(englishmap.skinMap)
        self.morphList.sort(key=getIndex)

    def __rigidbody(self, obj):
        if not bl.RIGID_SHAPE_TYPE in obj:
            return
        self.rigidbodies.append(obj)

    def __constraint(self, obj):
        if not bl.CONSTRAINT_A in obj:
            return
        self.constraints.append(obj)

    def __getOrCreateMorph(self, name, type):
        for m in self.morphList:
            if m.name==name:
                return m
        m=Morph(name, type)
        self.morphList.append(m)
        return m

    def getVertexCount(self):
        return len(self.vertexArray.positions)

    def __weights(self, obj, mesh, obj_name):
        for v in mesh.vertices:
            for i in self.vertexArray.getMappedIndex2(obj_name, v.index):
                ext_w=self.vertexArray.ext_weight[i]
                ext_w.entries.extend( filter( lambda ent: not ent[0].startswith("_"), \
                    ((obj.vertex_groups[vg.group].name, vg.weight) for vg in v.groups) ) )

