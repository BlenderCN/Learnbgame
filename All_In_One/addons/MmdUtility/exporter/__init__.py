# coding: utf-8
"""
Blenderのメッシュをワンスキンメッシュ化する
"""
from .. import bl

if "bpy" in locals():
    import imp
    imp.reload(oneskinmesh)
    imp.reload(bonebuilder)
else:
    from . import oneskinmesh
    from . import bonebuilder
import bpy



class ObjectNode(object):
    '''
    Objectの木構造構築
    '''
    __slots__=['o', 'children']
    def __init__(self, o):
        self.o=o
        self.children=[]


class Exporter(object):
    '''
    Blenderから情報収集する
    '''
    __slots__=[
            'oneSkinMesh',
            'skeleton',
            'root',
            ]
    def setup(self, scene):
        # scene内のオブジェクトの木構造を構築する
        object_node_map={}
        for o in scene.objects:
            object_node_map[o]=ObjectNode(o)
        for o in scene.objects:
            node=object_node_map[o]
            if node.o.parent:
                object_node_map[node.o.parent].children.append(node)
        self.root=object_node_map[scene.objects.active]

        # ワンスキンメッシュを作る
        self.oneSkinMesh=oneskinmesh.OneSkinMesh()
        self.oneSkinMesh.build(scene, self.root)
        #bl.message(self.oneSkinMesh)
        if len(self.oneSkinMesh.morphList)==0:
            # create emtpy skin
            self.oneSkinMesh.createEmptyBasicSkin()

        # skeleton
        self.skeleton=bonebuilder.BoneBuilder()
        self.skeleton.build(self.oneSkinMesh.armatureObj)

