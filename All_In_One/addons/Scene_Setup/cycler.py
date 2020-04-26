import bpy

def link(mat, tex):

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    # Remove old links
    to_diffuse = nodes['diffuse'].inputs
    for l in to_diffuse['Color'].links:
        links.remove(l)
    # Add link to texture
    links.new(to_diffuse['Color'], tex.outputs['Color'])

def tex(mat, _name, _image):

    nodes = mat.node_tree.nodes
    # Make new texture with image
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(_image)
    texture.name = _name
    # Link texture to output
    link(mat, texture)

    # New named texture
    return texture

def mat():

    mat = bpy.data.materials.new('Material')

    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # clear
    while(nodes): nodes.remove(nodes[0])

    # As of 2.69.1
    # https://docs.blender.org/api/blender_python_api_2_69_1/bpy.types.Nodes.html
    output  = nodes.new("ShaderNodeOutputMaterial")
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.name = 'diffuse'
    output.name = 'output'

    links.new(output.inputs['Surface'], diffuse.outputs['BSDF'])

    # material
    return mat
