'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from lens_flare_utils import *

def newCyclesMaterial(name = "Material"):
	material = newMaterial()
	material.use_nodes = True
	return material
def newMaterial(name = "Material"):
	return bpy.data.materials.new(name = name)
def cleanMaterial(material):
	removeNodes(material.node_tree)
def removeNodes(nodeTree):
	nodes = nodeTree.nodes
	for node in nodes:
		nodes.remove(node)
		
def setMaterialOnObject(object, material):
	object.data.materials.append(material)
		
def newOutputNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeOutputMaterial")
def newEmissionNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeEmission")
def newImageTextureNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeTexImage")
def newTextureCoordinatesNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeTexCoord")
def newTransparentNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeBsdfTransparent")
def newMixShader(nodeTree):
	return nodeTree.nodes.new("ShaderNodeMixShader")
def newAddShader(nodeTree):
	return nodeTree.nodes.new("ShaderNodeAddShader")
def newColorMixNode(nodeTree, type = "MIX", factor = 0.5, default1 = [0.5, 0.5, 0.5, 1.0], default2 = [0.5, 0.5, 0.5, 1.0]):
	node = nodeTree.nodes.new("ShaderNodeMixRGB")
	node.blend_type = type
	node.inputs[0].default_value = factor
	node.inputs[1].default_value = default1
	node.inputs[2].default_value = default2
	return node
def newRgbToBwNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeRGBToBW")
def newMathNode(nodeTree, type = "MIX", default = 0.5):
	node = nodeTree.nodes.new("ShaderNodeMath")
	node.operation = type
	node.inputs[0].default_value = default
	node.inputs[1].default_value = default
	return node
def newRerouteNode(nodeTree):
	return nodeTree.nodes.new("NodeReroute")
def newColorRampNode(nodeTree):
	return nodeTree.nodes.new("ShaderNodeValToRGB")
	
def linkToMixShader(nodeTree, socket1, socket2, mixShader, factor = None):
	if factor is not None: newNodeLink(nodeTree, mixShader.inputs[0], factor)
	newNodeLink(nodeTree, socket1, mixShader.inputs[1])
	newNodeLink(nodeTree, socket2, mixShader.inputs[2])	
def linkToAddShader(nodeTree, socket1, socket2, addShader):
	newNodeLink(nodeTree, socket1, addShader.inputs[0])
	newNodeLink(nodeTree, socket2, addShader.inputs[1])	
def newNodeLink(nodeTree, fromSocket, toSocket):
	nodeTree.links.new(toSocket, fromSocket)
	
def makeOnlyVisibleToCamera(object):
	object.cycles_visibility.glossy = False
	object.cycles_visibility.diffuse = False
	object.cycles_visibility.shadow = False
	object.cycles_visibility.transmission = False
	
def getNodeWithNameInObject(object, name):
	for slot in object.material_slots:
		node = slot.material.node_tree.nodes.get(name)
		if node is not None: return node
	return None