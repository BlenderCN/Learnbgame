import bpy


def CreateNodeGroup(graph, vars):
    print("Building nodegroup %s" % graph.ShaderName)
    osl_group = bpy.data.node_groups.new(graph.ShaderName, 'ShaderNodeTree')
    for node in graph.NodeList:
        print("Creating node %s type = %s" % (node.Name , node.NodeType))
        bpyNode = osl_group.nodes.new(node.NodeType)
        bpyNode.name = node.Name

    for node in graph.NodeList:
        for prop in node.Properties:
            print("Setting %s of %s to %s" %
                  (prop, node.Name, node.Properties[prop]))
            if prop == "operation":
                exec("bpy.data.node_groups['%s'].nodes['%s'].%s = '%s'" % (
                    osl_group.name, node.Name, prop, node.Properties[prop]))
            else:
                exec("bpy.data.node_groups['%s'].nodes['%s'].%s = %s" % (
                    osl_group.name, node.Name, prop, node.Properties[prop]))

    for var in vars:
        if var.varType == 'param' or var.varType == 'oparam':
            if var.varType == 'oparam':
                flt = osl_group.outputs.new(var.GetNodeType(), var.Name)
            else:
                flt = osl_group.inputs.new(var.GetNodeType(), var.Name)

            if var.IsNumeric():
                flt.default_value = float(var.defaults[0])
            if var.IsPointLike():
                for i in range(0, len(var.defaults)):
                    flt.default_value[i] = float(var.defaults[i])

    # osl_group.links.begin_update()
    linkSize = len(graph.LinkList)
    counter =0
    for link in graph.LinkList:
        counter = counter + 1
        if (counter % 100 == 0):
            print("Adding link %s of %s" % (counter, linkSize))
        TargetNode = osl_group.nodes[link.TargetNode.Name]
        SourceNode = osl_group.nodes[link.SourceNode.Name]
        osl_group.links.new(TargetNode.inputs[link.TargetIndex],
                            SourceNode.outputs[link.SourceIndex], False)
    # osl_group.links.end_update()
    return osl_group
