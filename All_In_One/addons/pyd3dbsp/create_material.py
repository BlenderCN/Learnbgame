# material creation code goes here

import bpy

import read_material
import read_texture

def create_material(name, material_fpath, texture_fpath):
    material_file = read_material.MTL()
    material_file.load_material(material_fpath + '\\' + name)
    
    material = bpy.data.materials.new(material_file.materialname)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # delete all nodes except output node
    for node in [node for node in nodes if node.type != 'OUTPUT_MATERIAL']:
        nodes.remove(node)

    # get output node
    material_output_node = None
    try:
        material_output_node = [node for node in nodes if node.type == 'OUTPUT_MATERIAL'][0]
    except:
        material_output_node = nodes.new('ShaderNodeOutputMaterial')
    material_output_node.location = (100,0)

    # create principled bsdf node and link it to the material output
    principled_bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    principled_bsdf_node.location = (-200,0)
    principled_bsdf_node.width = 200
    links.new(principled_bsdf_node.outputs['BSDF'], material_output_node.inputs['Surface'])

    # create texture input nodes and link them to the correct place
    counter = 0
    for maptype, mapname in material_file.mapinfo.items():
        texture_image = None
        try:
            texture_image = bpy.data.images.load(texture_fpath + '\\' + mapname + '.dds')
        except:
            print("Couldn't find " + mapname + ".dds. Trying to load from " + mapname + ".iwi")

        if(texture_image == None):
            texture = read_texture.Texture()
            if(texture.load_texture(texture_fpath + '\\' + mapname + '.iwi')):
                texture_image = bpy.data.images.new(mapname, texture.width, texture.height)
                pixels = [x / 255 for x in texture.texture_data]
                texture_image.pixels = pixels
            else:
                print("Couldn't load " + mapname + ".dds. Image texture will not be created.")

        if(texture_image != None):
            # creating texture input node
            texture_node = nodes.new('ShaderNodeTexImage')
            texture_node.label = maptype
            texture_node.location = (-700, 0 - 250 * counter)
            texture_node.image = texture_image

            # linking texture input node
            if(maptype == read_material.MTLMapTypes['colorMap']):
                links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])
            elif(maptype == read_material.MTLMapTypes['specularMap']):
                links.new(texture_node.outputs['Color'], principled_bsdf_node.inputs['Specular'])
            elif(maptype == read_material.MTLMapTypes['normalMap']):
                # create normalmap node
                normal_node = nodes.new('ShaderNodeNormalMap')
                normal_node.location = (-450, -500)

                links.new(texture_node.outputs['Color'], normal_node.inputs['Color'])
                links.new(normal_node.outputs['Normal'], principled_bsdf_node.inputs['Normal'])
            elif(maptype == read_material.MTLMapTypes['detailMap']):
                pass

            counter += 1

    # create texture coordinate node
    textcoord_node = nodes.new('ShaderNodeTexCoord')
    textcoord_node.location = (-1000, -150)
    for node in [node for node in nodes if node.type == 'TEX_IMAGE']:
        links.new(textcoord_node.outputs['UV'], node.inputs['Vector'])
