# -*- coding: utf-8 -*-
import bpy
from .. import gtls
from g_tools.gtls import defac,defac2,set_mode,set_ac
from g_tools.nbf import *

#########################################################シェーダースクリプト用定数
shader_node_types_dict = {
"NodeGroupInput":"GROUP_INPUT",
"NodeGroupOutput":"GROUP_OUTPUT",
"ShaderNodeAddShader":"ADD_SHADER",
"ShaderNodeAmbientOcclusion":"AMBIENT_OCCLUSION",
"ShaderNodeAttribute":"ATTRIBUTE",
"ShaderNodeBackground":"BACKGROUND",
"ShaderNodeBlackbody":"BLACKBODY",
"ShaderNodeBrightContrast":"BRIGHTCONTRAST",
"ShaderNodeBsdfAnisotropic":"BSDF_ANISOTROPIC",
"ShaderNodeBsdfDiffuse":"BSDF_DIFFUSE",
"ShaderNodeBsdfGlass":"BSDF_GLASS",
"ShaderNodeBsdfGlossy":"BSDF_GLOSSY",
"ShaderNodeBsdfHair":"BSDF_HAIR",
"ShaderNodeBsdfPrincipled":"BSDF_PRINCIPLED",
"ShaderNodeBsdfRefraction":"BSDF_REFRACTION",
"ShaderNodeBsdfToon":"BSDF_TOON",
"ShaderNodeBsdfTranslucent":"BSDF_TRANSLUCENT",
"ShaderNodeBsdfTransparent":"BSDF_TRANSPARENT",
"ShaderNodeBsdfVelvet":"BSDF_VELVET",
"ShaderNodeBump":"BUMP",
"ShaderNodeCameraData":"CAMERA",
"ShaderNodeCombineHSV":"COMBHSV",
"ShaderNodeCombineRGB":"COMBRGB",
"ShaderNodeCombineXYZ":"COMBXYZ",
"ShaderNodeEmission":"EMISSION",
"ShaderNodeExtendedMaterial":"MATERIAL_EXT",
"ShaderNodeFresnel":"FRESNEL",
"ShaderNodeGamma":"GAMMA",
"ShaderNodeGeometry":"GEOMETRY",
"ShaderNodeGroup":"GROUP",
"ShaderNodeHairInfo":"HAIR_INFO",
"ShaderNodeHoldout":"HOLDOUT",
"ShaderNodeHueSaturation":"HUE_SAT",
"ShaderNodeInvert":"INVERT",
"ShaderNodeLampData":"LAMP",
"ShaderNodeLayerWeight":"LAYER_WEIGHT",
"ShaderNodeLightFalloff":"LIGHT_FALLOFF",
"ShaderNodeLightPath":"LIGHT_PATH",
"ShaderNodeMapping":"MAPPING",
"ShaderNodeMaterial":"MATERIAL",
"ShaderNodeMath":"MATH",
"ShaderNodeMixRGB":"MIX_RGB",
"ShaderNodeMixShader":"MIX_SHADER",
"ShaderNodeNewGeometry":"NEW_GEOMETRY",
"ShaderNodeNormal":"NORMAL",
"ShaderNodeNormalMap":"NORMAL_MAP",
"ShaderNodeObjectInfo":"OBJECT_INFO",
"ShaderNodeOutput":"OUTPUT",
"ShaderNodeOutputLamp":"OUTPUT_LAMP",
"ShaderNodeOutputLineStyle":"OUTPUT_LINESTYLE",
"ShaderNodeOutputMaterial":"OUTPUT_MATERIAL",
"ShaderNodeOutputWorld":"OUTPUT_WORLD",
"ShaderNodeParticleInfo":"PARTICLE_INFO",
"ShaderNodeRGB":"RGB",
"ShaderNodeRGBCurve":"CURVE_RGB",
"ShaderNodeRGBToBW":"RGBTOBW",
"ShaderNodeScript":"SCRIPT",
"ShaderNodeSeparateHSV":"SEPHSV",
"ShaderNodeSeparateRGB":"SEPRGB",
"ShaderNodeSeparateXYZ":"SEPXYZ",
"ShaderNodeSqueeze":"SQUEEZE",
"ShaderNodeSubsurfaceScattering":"SUBSURFACE_SCATTERING",
"ShaderNodeTangent":"TANGENT",
"ShaderNodeTexBrick":"TEX_BRICK",
"ShaderNodeTexChecker":"TEX_CHECKER",
"ShaderNodeTexCoord":"TEX_COORD",
"ShaderNodeTexEnvironment":"TEX_ENVIRONMENT",
"ShaderNodeTexGradient":"TEX_GRADIENT",
"ShaderNodeTexImage":"TEX_IMAGE",
"ShaderNodeTexMagic":"TEX_MAGIC",
"ShaderNodeTexMusgrave":"TEX_MUSGRAVE",
"ShaderNodeTexNoise":"TEX_NOISE",
"ShaderNodeTexPointDensity":"TEX_POINTDENSITY",
"ShaderNodeTexSky":"TEX_SKY",
"ShaderNodeTexVoronoi":"TEX_VORONOI",
"ShaderNodeTexWave":"TEX_WAVE",
"ShaderNodeTexture":"TEXTURE",
"ShaderNodeUVAlongStroke":"UVALONGSTROKE",
"ShaderNodeUVMap":"UVMAP",
"ShaderNodeValToRGB":"VALTORGB",
"ShaderNodeValue":"VALUE",
"ShaderNodeVectorCurve":"CURVE_VEC",
"ShaderNodeVectorMath":"VECT_MATH",
"ShaderNodeVectorTransform":"VECT_TRANSFORM",
"ShaderNodeVolumeAbsorption":"VOLUME_ABSORPTION",
"ShaderNodeVolumeScatter":"VOLUME_SCATTER",
"ShaderNodeWavelength":"WAVELENGTH",
"ShaderNodeWireframe":"WIREFRAME",
}

shader_node_iolen_dict = {
"NodeGroupInput":(0,1),
"NodeGroupOutput":(1,0),
"ShaderNodeAddShader":(2,1),
"ShaderNodeAmbientOcclusion":(1,1),
"ShaderNodeAttribute":(0,3),
"ShaderNodeBackground":(2,1),
"ShaderNodeBlackbody":(1,1),
"ShaderNodeBrightContrast":(3,1),
"ShaderNodeBsdfAnisotropic":(6,1),
"ShaderNodeBsdfDiffuse":(3,1),
"ShaderNodeBsdfGlass":(4,1),
"ShaderNodeBsdfGlossy":(3,1),
"ShaderNodeBsdfHair":(5,1),
"ShaderNodeBsdfPrincipled":(20,1),
"ShaderNodeBsdfRefraction":(4,1),
"ShaderNodeBsdfToon":(4,1),
"ShaderNodeBsdfTranslucent":(2,1),
"ShaderNodeBsdfTransparent":(1,1),
"ShaderNodeBsdfVelvet":(3,1),
"ShaderNodeBump":(4,1),
"ShaderNodeCameraData":(0,3),
"ShaderNodeCombineHSV":(3,1),
"ShaderNodeCombineRGB":(3,1),
"ShaderNodeCombineXYZ":(3,1),
"ShaderNodeEmission":(2,1),
"ShaderNodeExtendedMaterial":(11,6),
"ShaderNodeFresnel":(2,1),
"ShaderNodeGamma":(2,1),
"ShaderNodeGeometry":(0,9),
"ShaderNodeGroup":(0,0),
"ShaderNodeHairInfo":(0,4),
"ShaderNodeHoldout":(0,1),
"ShaderNodeHueSaturation":(5,1),
"ShaderNodeInvert":(2,1),
"ShaderNodeLampData":(0,5),
"ShaderNodeLayerWeight":(2,2),
"ShaderNodeLightFalloff":(2,3),
"ShaderNodeLightPath":(0,13),
"ShaderNodeMapping":(1,1),
"ShaderNodeMaterial":(4,3),
"ShaderNodeMath":(2,1),
"ShaderNodeMixRGB":(3,1),
"ShaderNodeMixShader":(3,1),
"ShaderNodeNewGeometry":(0,8),
"ShaderNodeNormal":(1,2),
"ShaderNodeNormalMap":(2,1),
"ShaderNodeObjectInfo":(0,4),
"ShaderNodeOutput":(2,0),
"ShaderNodeOutputLamp":(1,0),
"ShaderNodeOutputLineStyle":(4,0),
"ShaderNodeOutputMaterial":(3,0),
"ShaderNodeOutputWorld":(2,0),
"ShaderNodeParticleInfo":(0,7),
"ShaderNodeRGB":(0,1),
"ShaderNodeRGBCurve":(2,1),
"ShaderNodeRGBToBW":(1,1),
"ShaderNodeScript":(0,0),
"ShaderNodeSeparateHSV":(1,3),
"ShaderNodeSeparateRGB":(1,3),
"ShaderNodeSeparateXYZ":(1,3),
"ShaderNodeSqueeze":(3,1),
"ShaderNodeSubsurfaceScattering":(6,1),
"ShaderNodeTangent":(0,1),
"ShaderNodeTexBrick":(10,2),
"ShaderNodeTexChecker":(4,2),
"ShaderNodeTexCoord":(0,7),
"ShaderNodeTexEnvironment":(1,1),
"ShaderNodeTexGradient":(1,2),
"ShaderNodeTexImage":(1,2),
"ShaderNodeTexMagic":(3,2),
"ShaderNodeTexMusgrave":(7,2),
"ShaderNodeTexNoise":(4,2),
"ShaderNodeTexPointDensity":(1,2),
"ShaderNodeTexSky":(1,1),
"ShaderNodeTexVoronoi":(2,2),
"ShaderNodeTexWave":(5,2),
"ShaderNodeTexture":(1,3),
"ShaderNodeUVAlongStroke":(0,1),
"ShaderNodeUVMap":(0,1),
"ShaderNodeValToRGB":(1,2),
"ShaderNodeValue":(0,1),
"ShaderNodeVectorCurve":(2,1),
"ShaderNodeVectorMath":(2,2),
"ShaderNodeVectorTransform":(1,1),
"ShaderNodeVolumeAbsorption":(2,1),
"ShaderNodeVolumeScatter":(3,1),
"ShaderNodeWavelength":(1,1),
"ShaderNodeWireframe":(1,1),
}


#########################################################decorators
def mat_ctx(f):
    def mat_ctxed(*args,obj = None,actmat = None,actnode = None,actnt = None,**kwargs):
        if obj == None:
            obj = gtls.get_active_obj()
        if actmat == None:
            actmat = get_active_mat(obj = obj)
        f(*args,obj = obj,actmat = actmat,actnode = actnode,actnt = actnt,**kwargs)

#########################################################マテリアルテクスチャーやテクスチャースロット関連
@defac
def get_mat_texs(obj = None):
    mats = obj.data.materials
    tslots = [[t for t in m.texture_slots] for m in mats]
    texs = []
    for ts in tslots:
        for t in ts:
            if t:
                texs.append(t)
    return texs

@defac
def get_mat_texslots(obj = None):
    mats = obj.data.materials
    tslots = [[t for t in m.texture_slots] for m in mats]
    return tslots

#########################################################scene関連
def assign_material_pass_indices():
    c=0
    for m in bpy.data.materials:
        m.pass_index = c
        c+=1

def node_resetterate(m):
    return anymap(lambda x: m.node_tree.nodes.remove(x),m.node_tree.nodes)

def node_reset(tar):
    dmats = bpy.data.materials
    anymap(node_resetterate,prop_filterate(tar,"node_tree"))

def invert_color_ramp(ramp_node):
    ramp = ramp_node.color_ramp
    # anymap(lambda x: setattr(ramp.elements[x],"position",(1-ramp.elements[x].position)),rlen(ramp.elements))
    anymap(lambda x: setattr(ramp.elements[x], "color",
                             (*(1 - ramp.elements[x].color[i] for i in range(3)), ramp.elements[x].color[3]))
           , rlen(ramp.elements))

def simple_node_search(nodes, type="ShaderNodeValToRGB"):
    return filter(lambda n: n.type == t, nodes)[0]



#########################################################node関連

def reset_matnodes_global():
    dmats = bpy.data.materials
    for m in dmats:
        m.use_nodes = not m.use_nodes
        m.use_nodes = not m.use_nodes


@defac
def copy_propagate_named_nodes(nodename="", mat=None, actmat=False, obj=None, source_node=None, prop_direcs=None):
    mats = obj.data.materials
    matslots = obj.material_slots
    actmat = get_active_mat(obj=obj)
    if mat == None:
        mat = actmat

    nt = mat.node_tree
    nodes = nt.nodes

    if source_node == None:
        source_node = get_active_mat(obj=obj).nt.nodes.active
    if nodename == "":
        nodename = source_node.name

    for mat in mats:
        copy_update_named_nodes(mat=mat, actmat=False, obj=obj, source_node=source_node, copy_props=prop_direcs)

#########################################################その他
