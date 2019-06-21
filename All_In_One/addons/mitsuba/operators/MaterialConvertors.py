# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

RoughnessMode = {'GGX' : 'ggx', 'SHARP' : 'beckmann' , 'BECKMANN' : 'beckmann'}


def color_cycle(color, input):
    color.r = input.default_value[0]
    color.g = input.default_value[1]
    color.b = input.default_value[2]

def IOR_transform(mts_mat, currentNode):
    if currentNode.inputs['IOR'].is_linked :
        pass    # it is inpossible in mitsuba 
    else :
        mts_mat.thin = False
        value = currentNode.inputs['IOR'].default_value
        if value == 1.0 :
            mts_mat.intIOR = 1.0
            mts_mat.thin = True
        elif value < 1.0 :
            mts_mat.intIOR = 1.0
            mts_mat.extIOR = 1.0/value
        else :
            mts_mat.intIOR = value
        
def convert_texture_node(imageNode, postFix, bl_mat):
    if imageNode.type == "TEX_IMAGE" :
        newName = bl_mat.name + postFix
        tex = None
        if newName in bpy.data.textures :
            tex = bpy.data.textures[newName]
        else :                
            tex = bpy.data.textures.new(newName, type = 'IMAGE')        
        index = bl_mat.texture_slots.find(newName)
        bl_tex = None
        if index == -1 :                
            bl_tex = bl_mat.texture_slots.add()                    
        else :
            bl_tex = bl_mat.texture_slots[index]
        bl_tex.texture = tex        
        tex.image = imageNode.image
        tex.mitsuba_texture.mitsuba_tex_bitmap.filename = imageNode.image.filepath
        return bl_tex
    else:        
        return None
        
def convert_diffuse_materials_cycles(bl_mat, currentNode):
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'diffuse'
    mitsuba_mat.mitsuba_bsdf_diffuse.reflectance_usetexture = False
    mitsuba_mat.mitsuba_bsdf_diffuse.alpha_usetexture = False
    mitsuba_mat.mitsuba_bsdf_diffuse.distribution = 'none'
    if currentNode.inputs['Color'].is_linked :
        imageNode = currentNode.inputs['Color'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Reff_tex",bl_mat)
        
        if(bl_tex):
            mitsuba_mat.mitsuba_bsdf_diffuse.reflectance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_diffuse.reflectance_texturename = bl_tex.texture.name
        else:
            pass        
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_diffuse.reflectance_color, currentNode.inputs['Color'])        

    if currentNode.inputs['Roughness'].is_linked :
        imageNode = currentNode.inputs['Roughness'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Rough_Tex",bl_mat)
        
        if(bl_tex):    
            mitsuba_mat.mitsuba_bsdf_diffuse.alpha_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_diffuse.alpha_texturename = bl_tex.texture.name
        else:
            pass    
    else :
        value = currentNode.inputs["Roughness"].default_value
        if value > 0 :
            mitsuba_mat.mitsuba_bsdf_diffuse.alpha = value 
            mitsuba_mat.mitsuba_bsdf_diffuse.distribution = 'beckmann'    
    return True
    
    
def convert_glossy_materials_cycles(bl_mat ,  currentNode ):    
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'conductor'
    mitsuba_mat.mitsuba_bsdf_conductor.specularReflectance_usetexture = False
    mitsuba_mat.mitsuba_bsdf_conductor.alpha_usetexture = False
    if currentNode.inputs['Color'].is_linked :        
        imageNode = currentNode.inputs['Color'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Reff_tex",bl_mat)
        
        if(bl_tex):            
            mitsuba_mat.mitsuba_bsdf_conductor.specularReflectance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_conductor.specularReflectance_texturename = bl_tex.texture.name
        else:
            pass            
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_conductor.specularReflectance_color, currentNode.inputs["Color"])
        
    mitsuba_mat.mitsuba_bsdf_conductor.distribution = RoughnessMode[currentNode.distribution]
    if currentNode.inputs['Roughness'].is_linked :    
        imageNode = currentNode.inputs['Roughness'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Rough_Tex",bl_mat)
         
        if(bl_tex):                
            mitsuba_mat.mitsuba_bsdf_conductor.alpha_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_conductor.alpha_texturename = bl_tex.texture.name
        else:
            pass            
    else :        
        mitsuba_mat.mitsuba_bsdf_conductor.alpha = currentNode.inputs["Roughness"].default_value
    return True
    
        
def convert_glass_materials_cycles(bl_mat ,  currentNode ):    
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'dielectric'
    mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = False
    mitsuba_mat.mitsuba_bsdf_dielectric.alpha_usetexture = False
    if currentNode.inputs['Color'].is_linked :                
        imageNode = currentNode.inputs['Color'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Reff_tex",bl_mat)
        
        if(bl_tex):            
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_texturename = bl_tex.texture.name
        else:
            pass                        
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_color, currentNode.inputs["Color"])
        
    mitsuba_mat.mitsuba_bsdf_dielectric.distribution = RoughnessMode[currentNode.distribution]    
    if currentNode.inputs['Roughness'].is_linked :
        imageNode = currentNode.inputs['Roughness'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Rough_Tex",bl_mat)            
        if(bl_tex):                
            mitsuba_mat.mitsuba_bsdf_dielectric.alpha_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_dielectric.alpha_texturename = bl_tex.texture.name
        else:
            pass    
    else :    
        mitsuba_mat.mitsuba_bsdf_dielectric.alpha = currentNode.inputs["Roughness"].default_value
            
    if currentNode.inputs['IOR'].is_linked :
        pass    # it is inpossible in mitsuba 
    else :
        IOR_transform(mitsuba_mat.mitsuba_bsdf_dielectric, currentNode)        
    return True

def convert_transparent_materials_cycles(bl_mat, currentNode):    
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'dielectric'
    mitsuba_mat.mitsuba_bsdf_dielectric.intIOR = 1.0
    mitsuba_mat.mitsuba_bsdf_dielectric.thin = True
    mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = False
    if currentNode.inputs['Color'].is_linked :                        
        imageNode = currentNode.inputs['Color'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Trans_tex",bl_mat)
        
        if(bl_tex):            
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_texturename = bl_tex.texture.name
        else:
            pass                        
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_color, currentNode.inputs["Color"])
    return True                        
    
def convert_refraction_materials_cycles(bl_mat ,  currentNode ):    
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'dielectric'
    mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = False
    mitsuba_mat.mitsuba_bsdf_dielectric.alpha_usetexture = False
    if currentNode.inputs['Color'].is_linked :                
        imageNode = currentNode.inputs['Color'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Reff_tex",bl_mat)
        
        if(bl_tex):            
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_usetexture = bl_tex.texture.name
        else:
            pass                        
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_dielectric.specularTransmittance_color, currentNode.inputs["Color"])
        
    mitsuba_mat.mitsuba_bsdf_dielectric.distribution = RoughnessMode[currentNode.distribution]        
    if currentNode.inputs['Roughness'].is_linked :
        imageNode = currentNode.inputs['Roughness'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Rough_Tex",bl_mat)
        
        if(bl_tex):                
            mitsuba_mat.mitsuba_bsdf_dielectric.alpha_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_dielectric.alpha_texturename = bl_tex.texture.name
        else:
            pass    
    else :
        mitsuba_mat.mitsuba_bsdf_dielectric.alpha = currentNode.inputs['Roughness'].default_value
            
    if currentNode.inputs['IOR'].is_linked :
        pass    # it is inpossible in mitsuba 
    else :
        IOR_transform(mitsuba_mat.mitsuba_bsdf_dielectric, currentNode)        
    return True
 
def convert_emitter_materials_cycles(bl_mat ,  currentNode , partial = False):    
    if not(partial) :
        bl_mat.mitsuba_mat_bsdf.use_bsdf = False
    mitsuba_emitter = bl_mat.mitsuba_mat_emitter    
    mitsuba_emitter.use_emitter = True    
    if currentNode.inputs['Color'].is_linked :
        pass    # it is not possible in mitsuba
    else:
        color_cycle(mitsuba_emitter.color, currentNode.inputs["Color"])
    
    if  currentNode.inputs["Strength"].is_linked:
        pass    #it is not possible in mitsuba
    else :
        mitsuba_emitter.intensity = currentNode.inputs["Strength"].default_value
    return True    
        
def convert_mix_materials_cycles(bl_mat, currentNode, obj = None, addShader = False):    
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'mixturebsdf'     
    
    if obj != None :
        bpy.context.scene.objects.active = obj
    else :
        obj = bpy.context.active_object

    name_I = bl_mat.name + '_I'
    name_II= bl_mat.name + "_II"    
    # in the case of AddShader 1-True = 0
    mat_I = currentNode.inputs[1-addShader].links[0].from_node
    mat_II= currentNode.inputs[2-addShader].links[0].from_node
    a, b = None, None
    #TODO:XOR would be better in case of two emission type material
    emitter = ((mat_I.type == 'EMISSION') or (mat_II.type == 'EMISSION'))    
    if emitter:        
        if (mat_I.type == 'EMISSION') :
            mat_I , mat_II = mat_II , mat_I                        
        a = material_selection_for_convertion_cycles(bl_mat, mat_I, obj)
        b = convert_emitter_materials_cycles(bl_mat ,mat_II , True)
        return a and b        
    else :
        # create first material
        if  (name_I in bpy.data.materials) :
            if (obj.material_slots.find(name_I) == -1): 
                obj.data.materials.append(bpy.data.materials[name_I])
            a = True                    
        else :
            mat = bpy.data.materials.new(name=name_I)
            obj.data.materials.append(mat)
            a = material_selection_for_convertion_cycles(mat, mat_I, obj)
        
        # create second materials    
        if  (name_II in bpy.data.materials) :
            if (obj.material_slots.find(name_II) == -1): 
                obj.data.materials.append(bpy.data.materials[name_II])
            b = True    
        else :
            mat = bpy.data.materials.new(name=name_II)
            obj.data.materials.append(mat)
            b = material_selection_for_convertion_cycles(mat, mat_II, obj)
        
        mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat1_name = name_I 
        mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat2_name = name_II
        if (addShader):
            mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat1_weight = 0.5
            mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat2_weight = 0.5
        else:
            mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat1_weight = max( 0.9999 - currentNode.inputs['Fac'].default_value,0.0)
            mitsuba_mat.mitsuba_bsdf_mixturebsdf.mat2_weight = max(currentNode.inputs['Fac'].default_value,0.0)             
        return a and b   

def convert_subsurface_scattering_cycles(bl_mat,currentNode):
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'plastic'
    mitsuba_mat.mitsuba_bsdf_plastic.reflectance_usetexture = False
    mitsuba_mat.mitsuba_bsdf_plastic.alpha_usetexture = False
    mitsuba_mat.mitsuba_bsdf_plastic.distribution = 'none'
    if currentNode.inputs['Radius'].is_linked :
        imageNode = currentNode.inputs['Radius'].links[0].from_node
        bl_tex = convert_texture_node(imageNode,"_Reff_tex",bl_mat)
        
        if(bl_tex):
            mitsuba_mat.mitsuba_bsdf_plastic.specularReflectance_usetexture = True    
            mitsuba_mat.mitsuba_bsdf_plastic.specularReflectance_texturename = bl_tex.texture.name
        else:
            pass        
    else :
        color_cycle(mitsuba_mat.mitsuba_bsdf_plastic.specularReflectance_color, currentNode.inputs['Radius'])        

    mitsuba_mat = bl_mat.mitsuba_mat_subsurface
    mitsuba_mat.use_subsurface = True
    mitsuba_mat.type = 'dipole'
    mitsuba_mat.mitsuba_sss_dipole.sigmaS_usetexture = False
    
    if currentNode.inputs['Scale'].is_linked:
        pass   
    else :
        mitsuba_mat.mitsuba_sss_dipole.scale = currentNode.inputs['Scale'].default_value
            
    if currentNode.inputs['Color'].is_linked:
        pass    # it dosen't seems to be funtional yet
    else :
        color_cycle(mitsuba_mat.mitsuba_sss_dipole.sigmaS_color, currentNode.inputs['Color'])     
    return True
    
            
def material_selection_for_convertion_cycles(blender_mat, currentNode , obj=None):            
    matDone = True
    #TODO: Add more support for other materials
    if(currentNode.type == "BSDF_DIFFUSE"):            
        matDone = convert_diffuse_materials_cycles(blender_mat, currentNode)        
    elif(currentNode.type == 'BSDF_GLOSSY'):            
        matDone = convert_glossy_materials_cycles(blender_mat, currentNode)        
    elif(currentNode.type == 'BSDF_GLASS'):            
        matDone = convert_glass_materials_cycles(blender_mat, currentNode)    
    elif(currentNode.type == 'EMISSION'):         
        matDone = convert_emitter_materials_cycles(blender_mat,currentNode)                    
    elif(currentNode.type == 'MIX_SHADER'):
        matDone = convert_mix_materials_cycles(blender_mat,currentNode, obj)
    elif(currentNode.type == 'BSDF_TRANSPARENT'):
        matDone = convert_transparent_materials_cycles(blender_mat,currentNode)
    elif(currentNode.type == 'BSDF_REFRACTION'):
        matDone = convert_refraction_materials_cycles(blender_mat,currentNode)        
    elif(currentNode.type == 'ADD_SHADER'):
        matDone = convert_mix_materials_cycles(blender_mat,currentNode, obj, True)
    elif(currentNode.type == 'SUBSURFACE_SCATTERING'):
        matDone = convert_subsurface_scattering_cycles(blender_mat,currentNode)
    else:
        matDone = False
    return matDone

def assigne_default_material(bl_mat):
    mitsuba_mat = bl_mat.mitsuba_mat_bsdf
    mitsuba_mat.type = 'diffuse'
    mitsuba_mat.mitsuba_bsdf_diffuse.reflectance_color = (0.8, 0.8, 0.8)