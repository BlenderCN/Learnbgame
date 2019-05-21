bl_info = {    
    "name"        : "Armature parenting tree generator",
    "author"      : "Tamir Lousky",
    "version"     : (1, 0, 0),
    "blender"     : (2, 66, 0),
    "category"    : "Rigging",
    "wiki_url"    : "https://github.com/Tlousky/production_scripts/wiki/_new?wiki[name]=draw_parenting_tree.py",
    "download_url": "https://github.com/Tlousky/production_scripts/blob/master/draw_parenting_tree.py",
    "description" : "Creates a node tree representing the armature's bone parenting structure."
    }

import bpy

rig   = bpy.context.object
bones = rig.data.bones

# find root bone
root = ''
for bone in bones:
	if not bone.parent:
		root = bone.name

# create references to node tree and node links
tree  = bpy.context.scene.node_tree
links = tree.links

# clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)

# create first node's location
(row, x, y) = (0, 0, 0)

def create_node( bone, x, y, row ):
    """
    recursive function that creates a math node for each bone in the armature
    and draws connections between bones (math nodes) according to parenting
    """
    # create new nodes
    node = tree.nodes.new('MAP_RANGE')

    no_of_children = len(bone.children)
    
    # set up node location, label and name
    node.location = x,y
    node.label    = bone.name
    node.name     = bone.name
    node.hide     = True

    # if this isn't the (parentless) root bone, create a link to its parent
    if bone.parent:
        parent_name = bone.parent.name
        parent_node = tree.nodes[parent_name]
        links.new(parent_node.outputs[0],node.inputs[0])
    
    # iterate over all the current's bone's children and draw their nodes

    row += 1
   
    i = 1
    for child in bone.children:
        x = 200 * row
        y = 0
        create_node( child, x, y, row )
        i += 1

def set_node_height( linksnode, i, yp ):
    """ recurse all nodes and set their height
    according to the parenting structure """

    # Draw tree (from root bone)
create_node( bones[root], x, 0, row )

def set_node_height( node, i, yp ):
    """
    recurse all nodes and set their height
    according to the parenting structure
    """
    n = len(node.outputs[0].links) # count the number of children
    y = yp + (i + n) * -30         # set y value to depend on the: parent's y value,
                                   # no. of children and the position of current bone in children
    node.location.y = y
    
    j = 0
    for link in node.outputs[0].links: # iterate current node's links
        child = link.to_node           # reference output node
        j += 1
        set_node_height( child, j, y )

# iterate over all nodes and adjust their y value
i = 0
for node in tree.nodes:
    set_node_height( node, i, 0 )
    i += 1

# Draw constraints
bpy.ops.object.mode_set(mode ='OBJECT')
pb = bpy.context.object.pose.bones

bones = [ node.name for node in tree.nodes ]

for bone in bones:
    pbone = pb[bone]
    
    for const in pbone.constraints:
        ctype     = const.type
        
        subtarget = bone
        try:
            subtarget = const.subtarget
        except:
            pass

        print( bone, " --> ", ctype, " --> ", subtarget )
                
        cnode = tree.nodes.new('MATH')

        # set up node location, label, color and name
        cnode.label            = ctype
        cnode.name             = node.name + "_" + ctype
        cnode.color            = ( 0.5, 0, 0.5 )
        cnode.use_custom_color = True

        subtarget_node = tree.nodes[subtarget]
        node           = tree.nodes[bone]

        x = ( node.location[0] + subtarget_node.location[0] ) / 2
        
        if node.location[1] > subtarget_node.location[1]:
            y = node.location[1] + 200
        else:
            y = subtarget_node.location[1] + 200


        cnode.location = x,y        

        links.new(node.outputs[0],cnode.inputs[0])

        for i in range(len(subtarget_node.inputs)):
            if not subtarget_node.inputs[i].links:
                break

        links.new(cnode.outputs[0],subtarget_node.inputs[i])