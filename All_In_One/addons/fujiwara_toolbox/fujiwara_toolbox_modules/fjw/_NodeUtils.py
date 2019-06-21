import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
import random
from collections import OrderedDict
from mathutils import *

from .main import *



class NodeUtils():
    def __init__(self, node):
        self.node = node
        pass

    def get_socket_by_name(self, sockets, name):
        for socket in sockets:
            if name in socket.name:
                return socket
        return None

    def input(self, name):
        return self.get_socket_by_name(self.node.inputs, name)

    def output(self, name):
        return self.get_socket_by_name(self.node.outputs, name)

    pass

class NodetreeUtils():
    def __init__(self, treeholder):
        self.treeholder = treeholder
        self.tree = None
        self.nodes = None
        self.links = None

        self.posx = 0
        self.posy = 0
        pass

    def activate(self):
        self.treeholder.use_nodes = True
        self.tree = self.treeholder.node_tree
        self.nodes = self.treeholder.node_tree.nodes
        self.links = self.treeholder.node_tree.links

    def deactivate(self):
        self.treeholder.use_nodes = False

    def cleartree(self):
        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

    """
    bpy.context.space_data.tree_type = 'CompositorNodeTree'
    "CompositorNodeRLayers" 入力　レンダーレイヤー
    "CompositorNodeComposite"出力　コンポジット出力
    "CompositorNodeMixRGB"カラーミックス
    "CompositorNodeCurveRGB"トーンカーブ
    "CompositorNodeValToRGB"カラーランプ
    add時の名前はbl_idnameでみれる

    """


    def add(self,type,label):
        node = self.nodes.new(type)
        node.label = label

        node.location = self.posx,self.posy
        self.posx += 200

        return node

    def group_instance(self, group):
        node = None
        if type(self.treeholder) == bpy.types.Scene:
            node = self.add("CompositorNodeGroup","Group")
        else:
            node = self.add("ShaderNodeGroup","Group")

        node.node_tree = group
        return node

    def link(self, output, input):
        self.links.new(output, input)



class NodeBuilder():
    """新しいやつ。。"""
    def __init__(self, node_holder):
        self.node_holder = node_holder
        self.node_holder.use_nodes = True
        self.node_tree = node_holder.node_tree
        self.pos_y = 0
    
    def node(self, bl_idname, create=False):
        """指定したタイプのノードを返す。なければ作る。"""
        if create:
            return self.node_tree.nodes.new(bl_idname)
        
        for node in self.node_tree.nodes:
            if node.bl_idname == bl_idname:
                return node
        
        return self.node_tree.nodes.new(bl_idname)

    def link(self, from_socket, to_socket):
        return self.node_tree.links.new(from_socket, to_socket)
    

    def _has_any_connects(self, node, inputs=False, outputs=False):
        if inputs:
            sockets = node.inputs
        if outputs:
            sockets = node.outputs
        connected = False
        for socket in sockets:
            if len(socket.links) != 0:
                connected = True
                break
        return connected
    
    def _connected_nodes(self, node, inputs=False, outputs=False):
        if inputs:
            sockets = node.inputs
        if outputs:
            sockets = node.outputs
        connected_nodes = []
        for socket in sockets:
            for link in socket.links:
                if inputs:
                    connected_nodes.append(link.from_node)
                if outputs:
                    connected_nodes.append(link.to_node)
        return connected_nodes

    def _get_endnodes(self):
        end_nodes = []
        for node in self.node_tree.nodes:
            if not self._has_any_connects(node, outputs=True):
                end_nodes.append(node)
        return end_nodes

    def _pos_nodes(self, root_node):
        root_node.location.y = self.pos_y
        for input_node in self._connected_nodes(root_node, inputs=True):
            # input_node.location.x = root_node.location.x - root_node.width - 10
            input_node.location.x = root_node.location.x - root_node.width - 300
            input_node.location.y = self.pos_y
            self._pos_nodes(input_node)
            # self.pos_y += root_node.height + 10
            self.pos_y += 200

    def layout(self):
        end_nodes = self._get_endnodes()
        for end_node in end_nodes:
            end_node.location.x = 0
            self._pos_nodes(end_node)

    def clear(self):
        self.node_holder.node_tree.nodes.clear()
    


"""
リンクベースで考えると効率的かも

ノードはnode("タイプ")
    検索してあればそれ、なければ作成


link = ntree.link(from_node, socket, to_node, socket)
もしくは
link = ntree.link()
link.from(node, socket)
link.to(node, socket)


画像ノードはクラス用意してもいいかも？
ImageNode(filepath)
みたいの
クラス作っておいてタイプ別に関数用意するか
Node.image(filepath)
Node.principle()
Node.node(type) 汎用のやつ
みたいなかんじで

レイアウト
ルートから辿って順番に位置決定するみたいの組む？
fromはいっぱいある
toは必ず一つ
ただし一つのノードにいろいろ入力がある←これは一旦無視するか
末端を基準に組む？

Principleのinputs
<bpy_struct, NodeSocketColor("Base Color")>
<bpy_struct, NodeSocketFloatFactor("Subsurface")>
<bpy_struct, NodeSocketVector("Subsurface Radius")>
<bpy_struct, NodeSocketColor("Subsurface Color")>
<bpy_struct, NodeSocketFloatFactor("Metallic")>
<bpy_struct, NodeSocketFloatFactor("Specular")>
<bpy_struct, NodeSocketFloatFactor("Specular Tint")>
<bpy_struct, NodeSocketFloatFactor("Roughness")>
<bpy_struct, NodeSocketFloatFactor("Anisotropic")>
<bpy_struct, NodeSocketFloatFactor("Anisotropic Rotation")>
<bpy_struct, NodeSocketFloatFactor("Sheen")>
<bpy_struct, NodeSocketFloatFactor("Sheen Tint")>
<bpy_struct, NodeSocketFloatFactor("Clearcoat")>
<bpy_struct, NodeSocketFloatFactor("Clearcoat Roughness")>
<bpy_struct, NodeSocketFloat("IOR")>
<bpy_struct, NodeSocketFloatFactor("Transmission")>
<bpy_struct, NodeSocketFloatFactor("Transmission Roughness")>
<bpy_struct, NodeSocketVector("Normal")>
<bpy_struct, NodeSocketVector("Clearcoat Normal")>
<bpy_struct, NodeSocketVector("Tangent")>

"""