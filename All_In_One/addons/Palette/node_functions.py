import bpy

def CreateNodeGroupFromPalette(palette):
    try:
        ngroup=bpy.data.node_groups[palette.name]
    except KeyError:
        newgroup=bpy.data.node_groups.new(palette.name, 'ShaderNodeTree')
        for c in palette.colors:
            newgroup.outputs.new("NodeSocketColor", c.name)
        output_node = newgroup.nodes.new("NodeGroupOutput")
        output_node.location = (200, 0)
        
        for c in palette.colors:
            col=newgroup.nodes.new('ShaderNodeRGB')
            col.name=col.label=c.name
            r,v,b=c.color_value
            col.outputs[0].default_value = [r,v,b,1.0]
            newgroup.links.new(col.outputs['Color'], output_node.inputs[c.name])
    return {'FINISHED'}

def RemoveNodeGroupFromPalette(palette):
    for n in bpy.data.node_groups:
        if n.name==palette.name:
            bpy.data.node_groups.remove(n, do_unlink=True)
    return {'FINISHED'}

def UpdateNodeGroupColor(palette):
    for n in bpy.data.node_groups:
        if palette.name==n.name:
            for c in palette.colors:
                for node in n.nodes:
                    if node.name==c.name:
                        r,v,b=c.color_value
                        node.outputs[0].default_value = [r,v,b,1.0]
    return {'FINISHED'}

def UpdateAddNodeGroupColor(palette):
    newcol=palette.colors[len(palette.colors)-1]
    nodegroup=bpy.data.node_groups[palette.name]
    nodegroup.outputs.new("NodeSocketColor", newcol.name)
    col=nodegroup.nodes.new('ShaderNodeRGB')
    col.name=col.label=newcol.name
    r,v,b=newcol.color_value
    col.outputs[0].default_value = [r,v,b,1.0]
    nodegroup.links.new(col.outputs['Color'], nodegroup.nodes['Group Output'].inputs[newcol.name])
    return {'FINISHED'}

def UpdateRemoveNodeGroupColor(palette):
    nodegroup=bpy.data.node_groups[palette.name]
    #delete node
    for node in nodegroup.nodes:
        if node.type=='RGB':
            try:
                palette.colors[node.name]
            except KeyError:
                nodegroup.nodes.remove(node)
    #delete output
    for o in nodegroup.outputs:
        try:
            palette.colors[o.name]
        except KeyError:
            nodegroup.outputs.remove(o)
    return {'FINISHED'}

def UpdateNodeGroupColorNames(palette):
    nodegroup=bpy.data.node_groups[palette.name]
    #rename nodes
    for node in nodegroup.nodes:
        if node.type=='RGB':
            try:
                palette.colors[node.name]
            except KeyError:
                nodetorename=node
    for o in nodegroup.outputs:
        try:
            palette.colors[o.name]
        except KeyError:
            outputtorename=o
    for c in palette.colors:
        try:
            nodegroup.nodes[c.name]
        except KeyError:
            nodetorename.name=c.name
            nodetorename.label=c.name
            outputtorename.name=c.name
    return {'FINISHED'}

def CreateNodeGroupPaletteGeneral():
    try :
        newgroup=bpy.data.node_groups['___palette_group___']
    except KeyError:
        newgroup=bpy.data.node_groups.new('___palette_group___', 'ShaderNodeTree')
        output_node = newgroup.nodes.new("NodeGroupOutput")
        output_node.location = (200, 0)
    return {'FINISHED'}

def PaletteListCallback(scene, context):
    items=[]
    prop=bpy.data.window_managers['WinMan'].palette[0]
    for p in prop.palettes:
        items.append((p.name,p.name,''))
    return items

def PaletteNodeUpdate(self, context):
    prop=bpy.data.window_managers['WinMan'].palette[0]
    palette=prop.palettes[prop.palette_list]
    nodegroup=bpy.data.node_groups['___palette_group___']
    grouptoget=bpy.data.node_groups[prop.palette_list]
    #Group
    for n in nodegroup.nodes:
        if n.type=='GROUP':
            nodegroup.nodes.remove(n)
    group=nodegroup.nodes.new('ShaderNodeGroup')
    group.node_tree=grouptoget
    #outputs
    for o in nodegroup.outputs:
        nodegroup.outputs.remove(o)
    for i in group.outputs:
        nodegroup.outputs.new("NodeSocketColor", i.name)
        nodegroup.links.new(group.outputs[i.name], nodegroup.nodes['Group Output'].inputs[i.name])