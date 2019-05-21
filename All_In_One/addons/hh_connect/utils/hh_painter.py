#Xolotl Studio
#Created by Ymmanuel Flores on 2018
#Copyright 2018 Crowdorchestra SAPI de CV. All rights reserved.
#hhconnect v 1.0.0.4

import bpy
import os
import string

def addMaterial(path,mat_names,ext,packed,normal):
    path = ''.join(filter(lambda c: c in string.printable, path))
    ext = ''.join(filter(lambda c: c in string.printable, ext))
    mat_names = ''.join(filter(lambda c: c in string.printable, mat_names))
    materials = mat_names.split('|')

    print("Substance Painter Live Link: Add Material Started")

    for mat in materials:
        exists = 0
        for m in bpy.data.materials:
            if 'HH_'+mat == m.name:
                exists = 1
        if exists == 1:
            print("Substance Painter Live Link: Material exists, Live Link will only refresh the textures",mat)
            refreshPrincipled()
        else:
            if int(packed) == 1:
                print("Substance Painter Live Link: Create Packed Material Started",mat)
                createPrincipledPacked(mat,path,ext,int(normal))
            else:
                print("Substance Painter Live Link: Create Material Started",mat)
                createPrincipled(mat,path,ext,int(normal))

    print("Substance Painter Live Link: All materials created successfully")

def createPrincipledPacked(name,path,ext,normal):
    mat = bpy.data.materials.new(name="HH_"+name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    if nodes.get('Diffuse BSDF') != None:
        nodes.remove(nodes.get('Diffuse BSDF'))

    material_output = nodes.get('Material Output')
    mainMixShader = nodes.new('ShaderNodeMixShader')
    mainMixShader.location = (0,300)
    mat.node_tree.links.new(material_output.inputs[0], mainMixShader.outputs[0])
    transparentBSDF = nodes.new('ShaderNodeBsdfTransparent')
    transparentBSDF.location = (-300,0)
    mat.node_tree.links.new(mainMixShader.inputs[2], transparentBSDF.outputs[0])


    secondaryMixShader = nodes.new('ShaderNodeMixShader')
    secondaryMixShader.location = (-300,300)
    mat.node_tree.links.new(mainMixShader.inputs[1], secondaryMixShader.outputs[0])
    emissionShader = nodes.new('ShaderNodeEmission')
    emissionShader.location = (-600,300)
    emissionShader.inputs[1].default_value = 10
    emissionShader.inputs[0].default_value = (0,0,0,1)
    mat.node_tree.links.new(secondaryMixShader.inputs[2], emissionShader.outputs[0])

    principaledBSDF = nodes.new('ShaderNodeBsdfPrincipled')
    principaledBSDF.location = (-600,900)
    principaledBSDF.distribution = 'GGX'
    mat.node_tree.links.new(secondaryMixShader.inputs[1], principaledBSDF.outputs[0])

    uv_map = nodes.new('ShaderNodeUVMap')
    uv_map.location = (-2400,300)
    uv_map.uv_map = "UVMap"


    txt_basecolor = nodes.new('ShaderNodeTexImage')
    txt_basecolor.location = (-900,1200)
    img_basecolor = bpy.data.images.load(filepath = path+"/"+name+"_basecolor."+ext)
    txt_basecolor.image = img_basecolor
    mat.node_tree.links.new(principaledBSDF.inputs[0], txt_basecolor.outputs[0])
    mat.node_tree.links.new(txt_basecolor.inputs[0], uv_map.outputs[0])


    separateRGB = nodes.new('ShaderNodeSeparateRGB')
    separateRGB.location = (-900,900)



    txt_aoroughmetal = nodes.new('ShaderNodeTexImage')
    txt_aoroughmetal.location = (-1200,900)
    img_aoroughmetal = bpy.data.images.load(filepath = path+"/"+name+"_aoroughmetal."+ext)
    txt_aoroughmetal.image = img_aoroughmetal
    txt_aoroughmetal.color_space = 'NONE'
    mat.node_tree.links.new(txt_aoroughmetal.inputs[0], uv_map.outputs[0])
    mat.node_tree.links.new(separateRGB.inputs[0], txt_aoroughmetal.outputs[0])
    mat.node_tree.links.new(principaledBSDF.inputs[7], separateRGB.outputs[1])
    mat.node_tree.links.new(principaledBSDF.inputs[4], separateRGB.outputs[2])



    txt_normal = nodes.new('ShaderNodeTexImage')
    txt_normal.location = (-2100,600)
    img_normal = bpy.data.images.load(filepath = path+"/"+name+"_normal."+ext)
    txt_normal.image = img_normal
    txt_normal.color_space = 'NONE'

    if normal == 0:
        separateRGBNormal = nodes.new('ShaderNodeSeparateRGB')
        separateRGBNormal.location = (-1800,600)
        mat.node_tree.links.new(separateRGBNormal.inputs[0], txt_normal.outputs[0])

        invertNormal = nodes.new('ShaderNodeInvert')
        invertNormal.location = (-1500,600)
        mat.node_tree.links.new(invertNormal.inputs[1], separateRGBNormal.outputs[1])


        combineRGBNormal = nodes.new('ShaderNodeCombineRGB')
        combineRGBNormal.location = (-1200,600)
        mat.node_tree.links.new(combineRGBNormal.inputs[0], separateRGBNormal.outputs[0])
        mat.node_tree.links.new(combineRGBNormal.inputs[1], invertNormal.outputs[0])
        mat.node_tree.links.new(combineRGBNormal.inputs[2], separateRGBNormal.outputs[2])

        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-900,600)
        mat.node_tree.links.new(normal_map.inputs[1], combineRGBNormal.outputs[0])

        mat.node_tree.links.new(principaledBSDF.inputs[17], normal_map.outputs[0])
        mat.node_tree.links.new(txt_normal.inputs[0], uv_map.outputs[0])
    else:
        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-900,600)
        mat.node_tree.links.new(normal_map.inputs[1], txt_normal.outputs[0])

        mat.node_tree.links.new(principaledBSDF.inputs[17], normal_map.outputs[0])
        mat.node_tree.links.new(txt_normal.inputs[0], uv_map.outputs[0])

    path_opacity = path+"/"+name+"_opacity."+ext
    if os.path.isfile(path_opacity):
        txt_opacity = nodes.new('ShaderNodeTexImage')
        txt_opacity.location = (-1200,0)
        img_opacity = bpy.data.images.load(filepath = path+"/"+name+"_opacity."+ext)
        txt_opacity.image = img_opacity
        txt_opacity.color_space = 'NONE'
        mat.node_tree.links.new(txt_opacity.inputs[0], uv_map.outputs[0])

        invertOpacity = nodes.new('ShaderNodeInvert')
        invertOpacity.location = (-900,0)
        mat.node_tree.links.new(invertOpacity.inputs[1], txt_opacity.outputs[0])
        mat.node_tree.links.new(mainMixShader.inputs[0], invertOpacity.outputs[0])
    else:
        mainMixShader.inputs[0].default_value = 0


    path_emissive = path+"/"+name+"_emissive."+ext
    if os.path.isfile(path_emissive):
        txt_emissive = nodes.new('ShaderNodeTexImage')
        txt_emissive.location = (-1200,300)
        img_emissive = bpy.data.images.load(filepath = path+"/"+name+"_emissive."+ext)
        txt_emissive.image = img_emissive
        txt_emissive.color_space = 'COLOR'
        mat.node_tree.links.new(txt_emissive.inputs[0], uv_map.outputs[0])
        mat.node_tree.links.new(emissionShader.inputs[0], txt_emissive.outputs[0])
        mat.node_tree.links.new(secondaryMixShader.inputs[0], txt_emissive.outputs[0])
    else:
        secondaryMixShader.inputs[0].default_value = 0



def createPrincipled(name,path,ext,normal):
    mat = bpy.data.materials.new(name="HH_"+name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes


    if nodes.get('Diffuse BSDF') != None:
        nodes.remove(nodes.get('Diffuse BSDF'))

    material_output = nodes.get('Material Output')
    mainMixShader = nodes.new('ShaderNodeMixShader')
    mainMixShader.location = (0,300)
    mat.node_tree.links.new(material_output.inputs[0], mainMixShader.outputs[0])
    transparentBSDF = nodes.new('ShaderNodeBsdfTransparent')
    transparentBSDF.location = (-300,0)
    mat.node_tree.links.new(mainMixShader.inputs[2], transparentBSDF.outputs[0])


    secondaryMixShader = nodes.new('ShaderNodeMixShader')
    secondaryMixShader.location = (-300,300)
    mat.node_tree.links.new(mainMixShader.inputs[1], secondaryMixShader.outputs[0])
    emissionShader = nodes.new('ShaderNodeEmission')
    emissionShader.location = (-600,300)
    emissionShader.inputs[1].default_value = 10
    emissionShader.inputs[0].default_value = (0,0,0,1)
    mat.node_tree.links.new(secondaryMixShader.inputs[2], emissionShader.outputs[0])

    principaledBSDF = nodes.new('ShaderNodeBsdfPrincipled')
    principaledBSDF.location = (-600,900)
    principaledBSDF.distribution = 'GGX'
    mat.node_tree.links.new(secondaryMixShader.inputs[1], principaledBSDF.outputs[0])

    uv_map = nodes.new('ShaderNodeUVMap')
    uv_map.location = (-2400,300)
    uv_map.uv_map = "UVMap"


    txt_basecolor = nodes.new('ShaderNodeTexImage')
    txt_basecolor.location = (-900,1200)
    img_basecolor = bpy.data.images.load(filepath = path+"/"+name+"_basecolor."+ext)
    txt_basecolor.image = img_basecolor
    mat.node_tree.links.new(principaledBSDF.inputs[0], txt_basecolor.outputs[0])
    mat.node_tree.links.new(txt_basecolor.inputs[0], uv_map.outputs[0])


    txt_rough = nodes.new('ShaderNodeTexImage')
    txt_rough.location = (-900,900)
    img_metal = bpy.data.images.load(filepath = path+"/"+name+"_roughness."+ext)
    txt_rough.image = img_metal
    txt_rough.color_space = 'NONE'
    mat.node_tree.links.new(principaledBSDF.inputs[7], txt_rough.outputs[0])
    mat.node_tree.links.new(txt_rough.inputs[0], uv_map.outputs[0])


    txt_metal = nodes.new('ShaderNodeTexImage')
    txt_metal.location = (-900,600)
    img_metal = bpy.data.images.load(filepath = path+"/"+name+"_metallic."+ext)
    txt_metal.image = img_metal
    txt_metal.color_space = 'NONE'
    mat.node_tree.links.new(principaledBSDF.inputs[4], txt_metal.outputs[0])
    mat.node_tree.links.new(txt_metal.inputs[0], uv_map.outputs[0])


    path_ao = path+"/"+name+"_ao."+ext
    if os.path.isfile(path_ao):
        txt_ao = nodes.new('ShaderNodeTexImage')
        txt_ao.location = (-1200,300)
        img_ao = bpy.data.images.load(filepath = path+"/"+name+"_ao."+ext)
        txt_ao.image = img_ao
        txt_ao.color_space = 'NONE'
        mat.node_tree.links.new(txt_ao.inputs[0], uv_map.outputs[0])



    txt_normal = nodes.new('ShaderNodeTexImage')
    txt_normal.location = (-2100,600)
    img_normal = bpy.data.images.load(filepath = path+"/"+name+"_normal."+ext)
    txt_normal.image = img_normal
    txt_normal.color_space = 'NONE'

    if normal == 0:
        separateRGBNormal = nodes.new('ShaderNodeSeparateRGB')
        separateRGBNormal.location = (-1800,600)
        mat.node_tree.links.new(separateRGBNormal.inputs[0], txt_normal.outputs[0])

        invertNormal = nodes.new('ShaderNodeInvert')
        invertNormal.location = (-1500,600)
        mat.node_tree.links.new(invertNormal.inputs[1], separateRGBNormal.outputs[1])


        combineRGBNormal = nodes.new('ShaderNodeCombineRGB')
        combineRGBNormal.location = (-1200,600)
        mat.node_tree.links.new(combineRGBNormal.inputs[0], separateRGBNormal.outputs[0])
        mat.node_tree.links.new(combineRGBNormal.inputs[1], invertNormal.outputs[0])
        mat.node_tree.links.new(combineRGBNormal.inputs[2], separateRGBNormal.outputs[2])

        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-900,300)
        mat.node_tree.links.new(normal_map.inputs[1], combineRGBNormal.outputs[0])

        mat.node_tree.links.new(principaledBSDF.inputs[17], normal_map.outputs[0])
        mat.node_tree.links.new(txt_normal.inputs[0], uv_map.outputs[0])
    else:
        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (-900,300)
        mat.node_tree.links.new(normal_map.inputs[1], txt_normal.outputs[0])

        mat.node_tree.links.new(principaledBSDF.inputs[17], normal_map.outputs[0])
        mat.node_tree.links.new(txt_normal.inputs[0], uv_map.outputs[0])

    path_opacity = path+"/"+name+"_opacity."+ext
    if os.path.isfile(path_opacity):
        txt_opacity = nodes.new('ShaderNodeTexImage')
        txt_opacity.location = (-1200,0)
        img_opacity = bpy.data.images.load(filepath = path+"/"+name+"_opacity."+ext)
        txt_opacity.image = img_opacity
        txt_opacity.color_space = 'NONE'
        mat.node_tree.links.new(txt_opacity.inputs[0], uv_map.outputs[0])

        invertOpacity = nodes.new('ShaderNodeInvert')
        invertOpacity.location = (-900,0)
        mat.node_tree.links.new(invertOpacity.inputs[1], txt_opacity.outputs[0])
        mat.node_tree.links.new(mainMixShader.inputs[0], invertOpacity.outputs[0])
    else:
        mainMixShader.inputs[0].default_value = 0


    path_emissive = path+"/"+name+"_emissive."+ext
    if os.path.isfile(path_emissive):
        txt_emissive = nodes.new('ShaderNodeTexImage')
        txt_emissive.location = (-1200,300)
        img_emissive = bpy.data.images.load(filepath = path+"/"+name+"_emissive."+ext)
        txt_emissive.image = img_emissive
        txt_emissive.color_space = 'COLOR'
        mat.node_tree.links.new(txt_emissive.inputs[0], uv_map.outputs[0])
        mat.node_tree.links.new(emissionShader.inputs[0], txt_emissive.outputs[0])
        mat.node_tree.links.new(secondaryMixShader.inputs[0], txt_emissive.outputs[0])
    else:
        secondaryMixShader.inputs[0].default_value = 0



def refreshPrincipled():
    for image in bpy.data.images:
        image.reload()

    for area in bpy.context.screen.areas:
        if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
            area.tag_redraw()

    if bpy.context.space_data.viewport_shade == 'RENDERED':
        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.context.space_data.viewport_shade = 'RENDERED'

'''
import bpy

for material in bpy.data.materials:
    if not material.users:
        bpy.data.materials.remove(material)

for image in bpy.data.images:
    if not image.users:
        bpy.data.images.remove(image)

addMaterial('C:/Users/argos/Desktop/test/SP Test','Default','tif','0','1')
'''
