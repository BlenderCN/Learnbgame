from .OSOVariable import OSOVariable
import re


class Node():
    def __init__(self, nodeType):
        self.NodeType = nodeType
        self.Properties = {}
        self.Name = "Unknown"

    def nodeType(self):
        return self.Instruction

    def SetProperty(self, prop, value):
        self.Properties[prop] = value


class NodeGraphVariable():
    def __init__(self, node, output, property):
        self.Node = node
        self.Property = property
        self.Output = output

    def Node(self):
        return self.Node

    def Property(self):
        return self.Property

    def Output(self):
        return self.Output


class NodeLink():
    def __init__(self, TargetNode, TargetIndex, SourceNode, SourceIndex):
        self.TargetNode = TargetNode
        self.TargetIndex = TargetIndex
        self.SourceNode = SourceNode
        self.SourceIndex = SourceIndex


class NodeGraph():
    def __init__(self):
        self.NodeList = []
        self.LinkList = []
        self.Variables = {}
        self.ShaderName = "Untitlted"
        self.Nodeindex = 0

    def CreateNode(self, nodeType):
        node = Node(nodeType)
        self.NodeList.append(node)
        node.Name = "Node_" + str(self.Nodeindex)
        node.SetProperty('label', "'" + node.Name + "'")
        self.Nodeindex = self.Nodeindex + 1
        return node

    def AddNode(self, node):
        self.NodeList.append(node)

    def AddLink(self, targetNode, targetIndex, variable):
        link = NodeLink(targetNode, targetIndex,
                        self.Variables[variable.Name].Node,
                        self.Variables[variable.Name].Output)
        self.LinkList.append(link)

    def AddNodeLink(self, targetNode, targetIndex, sourceNode, SourceIndex):
        link = NodeLink(targetNode, targetIndex, sourceNode, SourceIndex)
        self.LinkList.append(link)

    def prune(self):
        return
        print("---------prune---------")
        while True:
            SourceNodes = []
            for el in self.LinkList:
                if el.SourceNode not in SourceNodes:
                    SourceNodes.append(el.SourceNode)

            DeadNodes = []
            for el in self.NodeList:
                if el not in SourceNodes:
                    if (el.Name != "OutputNode"):
                        DeadNodes.append(el)
            print("Dead Nodes : %s" % len(DeadNodes))
            for nod in DeadNodes:
                print("Dead node : %s " % nod.Name)
                TargetLinks = []
                for el in self.LinkList:
                    if el.TargetNode == nod:
                        TargetLinks.append(el)
                for el in TargetLinks:
                    self.LinkList.remove(el)
                self.NodeList.remove(nod)
            if (len(DeadNodes)==0):
                break

    def Nodes(self):
        return self.Nodes

    def Links(self):
        return self.Links

    def SetVar(self, Destination, sourceNode, index, prop='Output'):
        self.Variables[Destination.Name] = NodeGraphVariable(
            sourceNode, index, prop)

    def ASetVar(self, Destination, sourceNode, index, prop='Output'):
        self.Variables[Destination] = NodeGraphVariable(
            sourceNode, index, prop)

    def Assign(self, Destination, Source):
        if (Destination.Name != Source.Name):
            self.Variables[Destination.Name] = self.Variables[Source.Name]

    def AAssign(self, Destination, Source):
        self.Variables[Destination] = self.Variables[Source.Name]

    def ARef(self, Destination, Source):
        self.Variables[Destination.Name] = self.Variables[Source]

    def MakeConst(self, var):
        if var.dataType == 'int' or var.dataType == 'float':
            node = self.CreateNode('ShaderNodeValue')
            node.SetProperty('outputs[0].default_value', var.defaults[0])
            self.SetVar(var, node, 0)
        elif var.IsPointLike():
            node = self.CreateNode('ShaderNodeCombineRGB')
            node.SetProperty('inputs[0].default_value', var.defaults[0])
            node.SetProperty('inputs[1].default_value', var.defaults[1])
            node.SetProperty('inputs[2].default_value', var.defaults[2])
            self.SetVar(var, node, 0)
        elif var.dataType == 'string':
            node = self.CreateNode('ShaderNodeValue')
            self.SetVar(var, node, 0)
        else:
            print("Unsupported const type %s(%s)" % (var.Name, var.dataType))

    def MakeGlobal(self,var):
        if var.Name=="N":
            node = self.CreateNode('ShaderNodeNewGeometry')
            self.SetVar(var, node, 1)
        elif var.Name=="I":
            node = self.CreateNode('ShaderNodeNewGeometry')
            self.SetVar(var, node, 4)
        elif var.Name=="P":
            node = self.CreateNode('ShaderNodeNewGeometry')
            self.SetVar(var, node, 0)
        elif var.Name=="Ng":
            node = self.CreateNode('ShaderNodeNewGeometry')
            self.SetVar(var, node, 3)
        elif var.Name=="u":
            node = self.CreateNode('ShaderNodeTexCoord')
            Split = self.CreateNode('ShaderNodeSeparateXYZ')
            self.AddNodeLink(Split, 0, node, 0)
            self.SetVar(var, Split, 0)
        elif var.Name=="v":
            node = self.CreateNode('ShaderNodeTexCoord')
            Split = self.CreateNode('ShaderNodeSeparateXYZ')
            self.AddNodeLink(Split, 0, node, 0)
            self.SetVar(var, Split, 1)
        else:
            print("Unhandled global %s" % var.Name)
            

    def MakeArray(self, var, oso):
        if 'int' in var.dataType == 'int' or 'float' in var.dataType:
            node = self.CreateNode('ShaderNodeValue')
            node.SetProperty('outputs[0].default_value', '0')
            len = int(re.match(r"[^[]*\[([^]]*)\]", var.dataType).groups()[0])
            for idx in range(0, len):
                self.ASetVar(var.Name + "_" + str(idx), node, 0)
                line = "temp " + \
                    var.dataType.split("[")[0] + " " + \
                    var.Name + "_" + str(idx)
                tvar = OSOVariable(line)
                oso.Variables.append(tvar)
        elif ('point' in var.dataType or
              'vector' in var.dataType or
              'color' in var.dataType):
            node = self.CreateNode('ShaderNodeCombineRGB')
            len = int(re.match(r"[^[]*\[([^]]*)\]", var.dataType).groups()[0])
            for idx in range(0, len):
                self.ASetVar(var.Name + "_" + str(idx), node, 0)
                line = "temp " + \
                    var.dataType.split("[")[0] + " " + \
                    var.Name + "_" + str(idx)
                tvar = OSOVariable(line)
                oso.Variables.append(tvar)

        else:
            print("Unsupported array type %s(%s)" % (var.Name, var.dataType))
