#!BPY
# coding: utf-8
""" 
Name: 'Metasequoia(.mqo)...'
Blender: 245
Group: 'Import'
Tooltip: 'Import from Metasequoia file format (.mqo)'
"""
__author__=['ousttrue']
__url__ = ["http://gunload.web.fc2.com/blender/"]
__bpydoc__= '''\

MQO Importer

This script imports a mqo into Blender for editing.

20080123: update.
20091125: modify for linux.
20100310: rewrite.
20100311: create armature from mikoto bone.
20100505: C extension.
20100606: integrate 2.4 and 2.5.
20100619: fix multibyte object name.
20100626: refactoring.
20100724: update for Blender2.53.
20100731: add full python module.
20101005: update for Blender2.54.
20101228: update for Blender2.55.
20110429: update for Blender2.57b.
20110918: update for Blender2.59.
20111002: update for pymeshio-2.1.0
'''

bl_addon_info = {
        "category": "Learnbgame",
        'name': 'Import: Metasequioa Model Format (.mqo)',
        'author': 'ousttrue',
        'version': (2, 0),
        'blender': (2, 5, 3),
        'location': 'File > Import',
        'description': 'Import from the Metasequioa Model Format (.mqo)',
        'warning': '', # used for warning icon and text in addons panel
        'wiki_url': 'http://sourceforge.jp/projects/meshio/wiki/FrontPage',
        'tracker_url': 'http://sourceforge.jp/ticket/newticket.php?group_id=5081',
        }

import os
import sys
from pymeshio.mqo import reader

# for 2.5
import bpy

# wrapper
from . import bl

def createMqoMaterial(m):
    material = bpy.data.materials.new(m.name.decode("cp932"))
    # shader
    if m.shader==1:
        material.diffuse_shader='FRESNEL'
    else:
        material.diffuse_shader='LAMBERT'
    # diffuse
    material.diffuse_color=[m.color.r, m.color.g, m.color.b]
    material.diffuse_intensity=m.diffuse
    material.alpha=m.color.a
    # other
    material.ambient = m.ambient
    #material.specular = m.specular
    material.emit=m.emit
    material.use_shadeless=True
    return material


def has_mikoto(mqo):
    return False


def __createMaterials(mqo, directory):
    """
    create blender materials and renturn material list.
    """
    materials = []
    textureMap={}
    imageMap={}
    if len(mqo.materials)>0:
        for material_index, m in enumerate(mqo.materials):
            # material
            material=createMqoMaterial(m)
            materials.append(material)
            # texture
            texture_name=m.tex.decode("cp932")
            if texture_name!=b'':
                if texture_name in textureMap:
                    texture=textureMap[texture_name]
                else:
                    # load texture image
                    if os.path.isabs(texture_name):
                        # absolute
                        path = texture_name
                    else:
                        # relative
                        path = os.path.join(directory, texture_name)
                    # texture
                    path=path.replace("\\", "/")
                    if os.path.exists(path):
                        print("create texture:", path)
                        texture, image=bl.texture.create(path)
                        textureMap[texture_name]=texture
                        imageMap[material_index]=image
                    else:
                        print("%s not exits" % path)
                        continue
                bl.material.addTexture(material, texture)
    else:
        # default material
        pass
    return materials, imageMap


def __createObjects(mqo, root, materials, imageMap, scale):
    """
    create blender mesh objects.
    """
    # tree stack
    stack=[root]    
    objects=[]
    for o in mqo.objects:
        mesh, mesh_object=bl.mesh.create(o.name.decode("cp932"))

        # add hierarchy
        stack_depth=len(stack)-1
        #print(o.depth, stack_depth)
        if o.depth<stack_depth:
            for i in range(stack_depth-o.depth):
                stack.pop()
        bl.object.makeParent(stack[-1], mesh_object)
        stack.append(mesh_object)

        obj_name=o.name.decode("cp932")
        if obj_name.startswith('sdef'):
            objects.append(mesh_object)
        elif obj_name.startswith('anchor'):
            bl.object.setLayerMask(mesh_object, [0, 1])
        elif obj_name.startswith('bone'):
            bl.object.setLayerMask(mesh_object, [0, 1])

        # geometry
        vertices=[(v.x * scale, -v.z * scale, v.y * scale) for v in o.vertices]
        faces=[]
        materialMap={}
        for f in o.faces:
            face_indices=[]
            # flip face
            for i in reversed(range(f.index_count)):
                face_indices.append(f.getIndex(i))
            faces.append(face_indices)
            materialMap[f.material_index]=True
        bl.mesh.addGeometry(mesh, vertices, faces)

        # add materials
        for i, material_index in enumerate(materialMap.keys()):
            bl.mesh.addMaterial(mesh, materials[material_index])
            materialMap[material_index]=i
 
        # set face params
        assert(len(o.faces)==len(mesh.tessfaces))

        bl.mesh.addUV(mesh)

        for i, (f, face) in enumerate(zip(o.faces, mesh.tessfaces)):
            uv_array=[]
            # ToDo FIX
            # flip face
            for j in reversed(range(f.index_count)):
                uv_array.append((f.getUV(j).x, 1.0-f.getUV(j).y))
            bl.mesh.setFaceUV(mesh, i, face, uv_array, 
                    imageMap.get(f.material_index, None))
            if f.material_index in materialMap:
                bl.face.setMaterial(face, materialMap[f.material_index])
            bl.face.setSmooth(face, True)

        # fix mesh
        mesh.update()

        # mirror modifier
        if o.mirror:
            bl.modifier.addMirror(mesh_object)

        # set smoothing
        bl.mesh.setSmooth(mesh, o.smoothing)

        # calc normal
        bl.mesh.recalcNormals(mesh_object)

    return objects


###############################################################################
# for mqo mikoto bone.
###############################################################################
class MikotoBone(object):
    __slots__=[
            'name',
            'iHead', 'iTail', 'iUp',
            'vHead', 'vTail', 'vUp',
            'parent', 'isFloating',
            'children',
            ]
    def __init__(self, face=None, vertices=None, materials=None):
        self.parent=None
        self.isFloating=False
        self.children=[]
        if not face:
            self.name='root'
            return

        self.name=materials[face.material_index].name.encode('utf-8')

        i0=face.getIndex(0)
        i1=face.getIndex(1)
        i2=face.getIndex(2)
        v0=vertices[i0]
        v1=vertices[i1]
        v2=vertices[i2]
        e01=v1-v0
        e12=v2-v1
        e20=v0-v2
        sqNorm0=e01.getSqNorm()
        sqNorm1=e12.getSqNorm()
        sqNorm2=e20.getSqNorm()
        if sqNorm0>sqNorm1:
            if sqNorm1>sqNorm2:
                # e01 > e12 > e20
                self.iHead=i2
                self.iTail=i1
                self.iUp=i0
            else:
                if sqNorm0>sqNorm2:
                    # e01 > e20 > e12
                    self.iHead=i2
                    self.iTail=i0
                    self.iUp=i1
                else:
                    # e20 > e01 > e12
                    self.iHead=i1
                    self.iTail=i0
                    self.iUp=i2
        else:
            # 0 < 1
            if sqNorm1<sqNorm2:
                # e20 > e12 > e01
                self.iHead=i1
                self.iTail=i2
                self.iUp=i0
            else:
                if sqNorm0<sqNorm2:
                    # e12 > e20 > e01
                    self.iHead=i0
                    self.iTail=i2
                    self.iUp=i1
                else:
                    # e12 > e01 > e20
                    self.iHead=i0
                    self.iTail=i1
                    self.iUp=i2
        self.vHead=vertices[self.iHead]
        self.vTail=vertices[self.iTail]
        self.vUp=vertices[self.iUp]

        if self.name.endswith('[]'):
            basename=self.name[0:-2]
            # expand LR name
            if self.vTail.x>0:
                self.name="%s_L" % basename
            else:
                self.name="%s_R" % basename


    def setParent(self, parent, floating=False):
        if floating:
            self.isFloating=True
        self.parent=parent
        parent.children.append(self)

    def printTree(self, indent=''):
        print("%s%s" % (indent, self.name))
        for child in self.children:
            child.printTree(indent+'  ')


def build_armature(armature, mikotoBone, parent=None):
    """
    create a armature bone.
    """
    bone = Armature.Editbone()
    bone.name = mikotoBone.name.encode('utf-8')
    armature.bones[bone.name] = bone

    bone.head = Mathutils.Vector(*mikotoBone.vHead.to_a())
    bone.tail = Mathutils.Vector(*mikotoBone.vTail.to_a())
    if parent:
        bone.parent=parent
        if mikotoBone.isFloating:
            pass
        else:
            bone.options=[Armature.CONNECTED]

    for child in mikotoBone.children:
        build_armature(armature, child, bone)


def create_armature(mqo):
    """
    create armature
    """
    boneObject=None
    for o in mqo.objects:
        if o.name.startswith('bone'):
            boneObject=o
            break
    if not boneObject:
        return

    tailMap={}
    for f in boneObject.faces:
        if f.index_count!=3:
            print("invalid index_count: %d" % f.index_count)
            continue
        b=MikotoBone(f, boneObject.vertices, mqo.materials)
        tailMap[b.iTail]=b

    #################### 
    # build mikoto bone tree
    #################### 
    mikotoRoot=MikotoBone()

    for b in tailMap.values():
        # each bone has unique parent or is root bone.
        if b.iHead in tailMap:
            b.setParent(tailMap[b.iHead])
        else: 
            isFloating=False
            for e in boneObject.edges:
                if  b.iHead==e.indices[0]:
                    # floating bone
                    if e.indices[1] in tailMap:
                        b.setParent(tailMap[e.indices[1]], True)
                        isFloating=True
                        break
                elif b.iHead==e.indices[1]:
                    # floating bone
                    if e.indices[0] in tailMap:
                        b.setParent(tailMap[e.indices[0]], True)
                        isFloating=True
                        break
            if isFloating:
                continue

            # no parent bone
            b.setParent(mikotoRoot, True)

    if len(mikotoRoot.children)==0:
        print("no root bone")
        return

    if len(mikotoRoot.children)==1:
        # single root
        mikotoRoot=mikotoRoot.children[0]
        mikotoRoot.parent=None
    else:
        mikotoRoot.vHead=Vector3(0, 10, 0)
        mikotoRoot.vTail=Vector3(0, 0, 0)

    #################### 
    # create armature
    #################### 
    armature = Armature.New()
    # link to object
    armature_object = scene.objects.new(armature)
    # create action
    act = Armature.NLA.NewAction()
    act.setActive(armature_object)
    # set XRAY
    armature_object.drawMode |= Object.DrawModes.XRAY
    # armature settings
    armature.drawType = Armature.OCTAHEDRON
    armature.envelopes = False
    armature.vertexGroups = True
    armature.mirrorEdit = True
    armature.drawNames=True

    # edit bones
    armature.makeEditable()
    build_armature(armature, mikotoRoot)
    armature.update()

    return armature_object
        

class TrianglePlane(object):
    """
    mikoto方式ボーンのアンカーウェイト計算用。
    (不完全)
    """
    __slots__=['normal', 
            'v0', 'v1', 'v2',
            ]
    def __init__(self, v0, v1, v2):
        self.v0=v0
        self.v1=v1
        self.v2=v2

    def isInsideXY(self, p):
        v0=Vector2(self.v0.x, self.v0.y)
        v1=Vector2(self.v1.x, self.v1.y)
        v2=Vector2(self.v2.x, self.v2.y)
        e01=v1-v0
        e12=v2-v1
        e20=v0-v2
        c0=Vector2.cross(e01, p-v0)
        c1=Vector2.cross(e12, p-v1)
        c2=Vector2.cross(e20, p-v2)
        if c0>=0 and c1>=0 and c2>=0:
            return True
        if c0<=0 and c1<=0 and c2<=0:
            return True

    def isInsideYZ(self, p):
        v0=Vector2(self.v0.y, self.v0.z)
        v1=Vector2(self.v1.y, self.v1.z)
        v2=Vector2(self.v2.y, self.v2.z)
        e01=v1-v0
        e12=v2-v1
        e20=v0-v2
        c0=Vector2.cross(e01, p-v0)
        c1=Vector2.cross(e12, p-v1)
        c2=Vector2.cross(e20, p-v2)
        if c0>=0 and c1>=0 and c2>=0:
            return True
        if c0<=0 and c1<=0 and c2<=0:
            return True

    def isInsideZX(self, p):
        v0=Vector2(self.v0.z, self.v0.x)
        v1=Vector2(self.v1.z, self.v1.x)
        v2=Vector2(self.v2.z, self.v2.x)
        e01=v1-v0
        e12=v2-v1
        e20=v0-v2
        c0=Vector2.cross(e01, p-v0)
        c1=Vector2.cross(e12, p-v1)
        c2=Vector2.cross(e20, p-v2)
        if c0>=0 and c1>=0 and c2>=0:
            return True
        if c0<=0 and c1<=0 and c2<=0:
            return True


class MikotoAnchor(object):
    """
    mikoto方式スケルトンのアンカー。
    """
    __slots__=[
            "triangles", "bbox",
            ]
    def __init__(self):
        self.triangles=[]
        self.bbox=None

    def push(self, face, vertices):
        if face.index_count==3:
            self.triangles.append(TrianglePlane(
                vertices[face.indices[0]],
                vertices[face.indices[1]],
                vertices[face.indices[2]]
                ))
        elif face.index_count==4:
            self.triangles.append(TrianglePlane(
                vertices[face.indices[0]],
                vertices[face.indices[1]],
                vertices[face.indices[2]]
                ))
            self.triangles.append(TrianglePlane(
                vertices[face.indices[2]],
                vertices[face.indices[3]],
                vertices[face.indices[0]]
                ))
        # bounding box
        if not self.bbox:
            self.bbox=BoundingBox(vertices[face.indices[0]])
        for i in face.indices:
            self.bbox.expand(vertices[i])


    def calcWeight(self, v):
        if not self.bbox.isInside(v):
            return 0

        if self.anyXY(v.x, v.y) and self.anyYZ(v.y, v.z) and self.anyZX(v.z, v.x):
            return 1.0
        else:
            return 0
        
    def anyXY(self, x, y):
        for t in self.triangles:
            if t.isInsideXY(Vector2(x, y)):
                return True
        return False

    def anyYZ(self, y, z):
        for t in self.triangles:
            if t.isInsideYZ(Vector2(y, z)):
                return True
        return False

    def anyZX(self, z, x):
        for t in self.triangles:
            if t.isInsideZX(Vector2(z, x)):
                return True
        return False


def create_bone_weight(scene, mqo, armature_object, objects):
    """
    create mikoto bone weight.
    """
    anchorMap={}
    # setup mikoto anchors
    for o in mqo.objects:
        if o.name.startswith("anchor"):
            for f in o.faces:
                name=mqo.materials[f.material_index].name
                if name.endswith('[]'):
                    basename=name[0:-2]
                    v=o.vertices[f.indices[0]]
                    if(v.x>0):
                        # L
                        name_L=basename+'_L'
                        if not name_L in anchorMap:
                            anchorMap[name_L]=MikotoAnchor()
                        anchorMap[name_L].push(f, o.vertices)
                    elif(v.x<0):
                        # R
                        name_R=basename+'_R'
                        if not name_R in anchorMap:
                            anchorMap[name_R]=MikotoAnchor()
                        anchorMap[name_R].push(f, o.vertices)
                    else:
                        print("no side", v)
                else:
                    if not name in anchorMap:
                        anchorMap[name]=MikotoAnchor()
                    anchorMap[name].push(f, o.vertices)

    for o in objects:
        # add armature modifier
        mod=o.modifiers.append(Modifier.Types.ARMATURE)
        mod[Modifier.Settings.OBJECT] = armature_object
        mod[Modifier.Settings.ENVELOPES] = False
        o.makeDisplayList()
        # create vertex group
        mesh=o.getData(mesh=True)
        for name in anchorMap.keys():
            mesh.addVertGroup(name)
        mesh.update()
                 
    # assing vertices to vertex group
    for o in objects:
        mesh=o.getData(mesh=True)
        for i, mvert in enumerate(mesh.verts):
            hasWeight=False
            for name, anchor in anchorMap.items():
                weight=anchor.calcWeight(mvert.co)
                if weight>0:
                    mesh.assignVertsToGroup(
                            name, [i], weight, Mesh.AssignModes.ADD)
                    hasWeight=True
            if not hasWeight:
                # debug orphan vertex
                print('orphan', mvert)
        mesh.update()


def _execute(filepath='', scale=0.1):
    # read mqo model
    model=reader.read_from_file(filepath)
    if not model:
        bl.message("fail to load %s" % filepath)
        return

    # create materials
    materials, imageMap=__createMaterials(model, os.path.dirname(filepath))
    if len(materials)==0:
        materials.append(bl.material.create('default'))

    # create objects
    root=bl.object.createEmpty(os.path.basename(filepath))
    objects=__createObjects(model, root, materials, imageMap, scale)

    if has_mikoto(model):
        # create mikoto bone
        armature_object=create_armature(model)
        if armature_object:
            root.makeParent([armature_object])

            # create bone weight
            create_bone_weight(model, armature_object, objects)


import bpy_extras.io_utils # pylint: disable=E0401
class ImportMqo(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from MQO file format (.mqo)'''
    bl_idname = 'import_scene.metasequioa_mqo'
    bl_label = 'Import MQO'
    bl_options={'UNDO'}
    filename_ext = '.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.mqo', options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=0.1)

    def execute(self, context):
        bl.initialize('mqo_import', context.scene)
        _execute(**self.as_keywords(
            ignore=('filter_glob',)))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname,
                text="Metasequoia (.mqo)",
                icon='PLUGIN'
                )
