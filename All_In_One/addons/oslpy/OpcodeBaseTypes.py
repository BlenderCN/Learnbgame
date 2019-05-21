class Opcode():
    def __init__(self, OSO, index):
        self.OSO = OSO
        self.InstructionIndex = index
        self.Instuction = self.OSO.Instructions[index]
        self.Tag = self.OSO.Instructions[index].Tag

    def Instruction(self):
        return self.Instruction

    def InstructionIndex(self):
        return self.InstructionIndex

    def NextIndex(self):
        return self.InstructionIndex + 1

    def Tag(self):
        return self.Tag

    def Generate(self, nodeGraph):
        print("Generate not implemented for %s" % self.Instuction.Opcode)


# Destination Source
class Opcode_DS(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Source = OSO.GetVariable(self.Instuction.Parameters[1])

    def Destination(self):
        return self.Destination

    def Source(self):
        return self.Source

class Opcode_D(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        
    def Destination(self):
        return self.Destination

# Destination Source1 Source2


class Opcode_DSS(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Source1 = OSO.GetVariable(self.Instuction.Parameters[1])
        self.Source2 = OSO.GetVariable(self.Instuction.Parameters[2])

    def Destination(self):
        return self.Destination

    def Source1(self):
        return self.Source1

    def Source2(self):
        return self.Source2


class Opcode_SDD(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Source = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Destination1 = OSO.GetVariable(self.Instuction.Parameters[1])
        self.Destination2 = OSO.GetVariable(self.Instuction.Parameters[2])

    def Destination1(self):
        return self.Destination1

    def Destination2(self):
        return self.Destination2

    def Source(self):
        return self.Source


# Destination Source1 Source2
class Opcode_DSSS(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Source1 = OSO.GetVariable(self.Instuction.Parameters[1])
        self.Source2 = OSO.GetVariable(self.Instuction.Parameters[2])
        self.Source3 = OSO.GetVariable(self.Instuction.Parameters[3])

    def Destination(self):
        return self.Destination

    def Source1(self):
        return self.Source1

    def Source2(self):
        return self.Source2

    def Source3(self):
        return self.Source3

# Destination Source1 index


class Opcode_DSI(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Source = OSO.GetVariable(self.Instuction.Parameters[1])
        self.Index = OSO.GetVariable(self.Instuction.Parameters[2])

    def Destination(self):
        return self.Destination

    def Source(self):
        return self.Source1

    def Index(self):
        return self.Index


class Opcode_DIS(Opcode):
    def __init__(self, OSO, index):
        Opcode.__init__(self, OSO, index)
        self.Destination = OSO.GetVariable(self.Instuction.Parameters[0])
        self.Index = OSO.GetVariable(self.Instuction.Parameters[1])
        self.Source = OSO.GetVariable(self.Instuction.Parameters[2])

    def Destination(self):
        return self.Destination

    def Source(self):
        return self.Source

    def Index(self):
        return self.Index


class Opcode_basicMath(Opcode_DSS):
    def __init__(self, OSO, index, operation):
        Opcode_DSS.__init__(self, OSO, index)
        self.Operation = operation

    def GenerateFloatFloat(self, nodeGraph):
        node = nodeGraph.CreateNode("ShaderNodeMath")
        node.SetProperty("operation", self.Operation)
        nodeGraph.AddLink(node, 0, self.Source1)
        nodeGraph.AddLink(node, 1, self.Source2)
        nodeGraph.SetVar(self.Destination, node, 0)

    def GeneratePointPoint(self, nodeGraph):
        node = nodeGraph.CreateNode("ShaderNodeVectorMath")
        if self.Operation in ['ADD', 'SUBTRACT']:
            node.SetProperty("operation", self.Operation)
            nodeGraph.AddLink(node, 0, self.Source1)
            nodeGraph.AddLink(node, 1, self.Source2)
            nodeGraph.SetVar(self.Destination, node, 0)
        elif self.Operation in ["MULTIPLY" ,"DIVIDE","MODULO"]:
            node1 = nodeGraph.CreateNode('ShaderNodeSeparateXYZ')
            nodeGraph.AddLink(node1, 0, self.Source1)
            node2 = nodeGraph.CreateNode('ShaderNodeSeparateXYZ')
            nodeGraph.AddLink(node2, 0, self.Source2)

            nodex = nodeGraph.CreateNode("ShaderNodeMath")
            nodex.SetProperty("operation", self.Operation)
            nodeGraph.AddNodeLink(nodex, 0, node1, 0)
            nodeGraph.AddNodeLink(nodex, 1, node2, 0)

            nodey = nodeGraph.CreateNode("ShaderNodeMath")
            nodey.SetProperty("operation", self.Operation)
            nodeGraph.AddNodeLink(nodey, 0, node1, 1)
            nodeGraph.AddNodeLink(nodey, 1, node2, 1)

            nodez = nodeGraph.CreateNode("ShaderNodeMath")
            nodez.SetProperty("operation", self.Operation)
            nodeGraph.AddNodeLink(nodez, 0, node1, 2)
            nodeGraph.AddNodeLink(nodez, 1, node2, 2)

            nodeOut = nodeGraph.CreateNode('ShaderNodeCombineXYZ')
            nodeGraph.AddNodeLink(nodeOut, 0, nodex, 0)
            nodeGraph.AddNodeLink(nodeOut, 1, nodey, 0)
            nodeGraph.AddNodeLink(nodeOut, 2, nodez, 0)
            nodeGraph.SetVar(self.Destination, nodeOut, 0)

        else:
            raise ValueError(str('Unsupported math operation %s %s %s' % (
                self.Source1.dataType, self.Operation, self.Source2.dataType)))

    def GeneratePointFloat(self, nodeGraph, vec, flt):
        node = nodeGraph.CreateNode('ShaderNodeSeparateXYZ')
        nodeGraph.AddLink(node, 0, vec)

        nodex = nodeGraph.CreateNode("ShaderNodeMath")
        nodex.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodex, 0, node, 0)
        nodeGraph.AddLink(nodex, 1, flt)

        nodey = nodeGraph.CreateNode("ShaderNodeMath")
        nodey.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodey, 0, node, 1)
        nodeGraph.AddLink(nodey, 1, flt)

        nodez = nodeGraph.CreateNode("ShaderNodeMath")
        nodez.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodez, 0, node, 2)
        nodeGraph.AddLink(nodez, 1, flt)

        nodeOut = nodeGraph.CreateNode('ShaderNodeCombineXYZ')
        nodeGraph.AddNodeLink(nodeOut, 0, nodex, 0)
        nodeGraph.AddNodeLink(nodeOut, 1, nodey, 0)
        nodeGraph.AddNodeLink(nodeOut, 2, nodez, 0)
        nodeGraph.SetVar(self.Destination, nodeOut, 0)

    def GenerateFloatPoint(self, nodeGraph):
        node = nodeGraph.CreateNode('ShaderNodeSeparateXYZ')
        nodeGraph.AddLink(node, 0, self.Source2)

        nodex = nodeGraph.CreateNode("ShaderNodeMath")
        nodex.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodex, 1, node, 0)
        nodeGraph.AddLink(nodex, 0, self.Source1)

        nodey = nodeGraph.CreateNode("ShaderNodeMath")
        nodey.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodey, 1, node, 1)
        nodeGraph.AddLink(nodey, 0, self.Source1)

        nodez = nodeGraph.CreateNode("ShaderNodeMath")
        nodez.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodez, 1, node, 2)
        nodeGraph.AddLink(nodez, 0, self.Source1)

        nodeOut = nodeGraph.CreateNode('ShaderNodeCombineXYZ')
        nodeGraph.AddNodeLink(nodeOut, 0, nodex, 0)
        nodeGraph.AddNodeLink(nodeOut, 1, nodey, 0)
        nodeGraph.AddNodeLink(nodeOut, 2, nodez, 0)
        nodeGraph.SetVar(self.Destination, nodeOut, 0)


    def Generate(self, nodeGraph):
        if self.Source1.IsNumeric() and self.Source2.IsNumeric():
            self.GenerateFloatFloat(nodeGraph)
        elif self.Source1.IsNumeric() and self.Source2.IsPointLike():
            self.GenerateFloatPoint(nodeGraph)
        elif self.Source1.IsPointLike() and self.Source2.IsNumeric():
            self.GeneratePointFloat(nodeGraph, self.Source1, self.Source2)
        elif self.Source1.IsPointLike() and self.Source2.IsPointLike():
            self.GeneratePointPoint(nodeGraph)
        else:
            raise ValueError(str('Unsupported math operation %s %s %s' % (
                self.Source1.dataType, self.Operation, self.Source2.dataType)))


class Opcode_basicMath1(Opcode_DS):
    def __init__(self, OSO, index, operation):
        Opcode_DS.__init__(self, OSO, index)
        self.Operation = operation

    def GenerateFloat(self, nodeGraph):
        node = nodeGraph.CreateNode("ShaderNodeMath")
        node.SetProperty("operation", self.Operation)
        nodeGraph.AddLink(node, 0, self.Source)
        nodeGraph.SetVar(self.Destination, node, 0)

    def GeneratePoint(self, nodeGraph):
        node = nodeGraph.CreateNode('ShaderNodeSeparateXYZ')
        nodeGraph.AddLink(node, 0, self.Source)

        nodex = nodeGraph.CreateNode("ShaderNodeMath")
        nodex.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodex, 0, node, 0)

        nodey = nodeGraph.CreateNode("ShaderNodeMath")
        nodey.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodey, 0, node, 1)

        nodez = nodeGraph.CreateNode("ShaderNodeMath")
        nodez.SetProperty("operation", self.Operation)
        nodeGraph.AddNodeLink(nodez, 0, node, 2)

        nodeOut = nodeGraph.CreateNode('ShaderNodeCombineXYZ')
        nodeGraph.AddNodeLink(nodeOut, 0, nodex, 0)
        nodeGraph.AddNodeLink(nodeOut, 1, nodey, 0)
        nodeGraph.AddNodeLink(nodeOut, 2, nodez, 0)
        nodeGraph.SetVar(self.Destination, nodeOut, 0)


    def Generate(self, nodeGraph):
        if self.Source.IsNumeric():
            self.GenerateFloat(nodeGraph)
        elif self.Source.IsPointLike():
            self.GeneratePoint(nodeGraph)
        else:
            raise ValueError(str('Unsupported math operation %s %s' %
                                 (self.Source.dataType, self.Operation)))
