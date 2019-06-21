###
##  Translate an RVMat to a new location, copying all required textures along
#
from subprocess import Popen,PIPE,call
import os.path as path
import tempfile
import shutil
import bpy


static_texture_translation = [
["ca\\data\\env_bathroom_co","a3\\data_f\\env_bathroom_co"],
["ca\\data\\data\\default_co","a3\\data_f\\default_co"],
["ca\\data\\env_land_co","a3\\data_f\\env_land_co"],
["ca\\data\\env_chrome_co","a3\\data_f\\env_chrome_co"],
["ca\\data\\env_co","a3\\data_f\\env_co"],
["ca\\data\\env_land_optic_co","a3\\data_f\\env_land_optic_co"],
["ca\\wheeled\\data\\bis_klan","a3\\data_f\\bis_klan"],
["ca\\weapons\\data\\bullettracer\\tracer_red","a3\\weapons_f\\data\\bullettracer\\tracer_red"],
["ca\\weapons\\data\\bullettracer\\tracer_yellow","a3\\weapons_f\\data\\bullettracer\\tracer_yellow"],
["ca\\weapons\\data\\bullettracer\\tracer_green","a3\\weapons_f\\data\\bullettracer\\tracer_green"],
["ca\\wheeled\\data\\clear_empty","a3\\data_f\\clear_empty"],
["ca\\ca_e\\data\\carflare_ca","a3\\data_f\\carflare_ca"],
["ca\\weapons\\data\\detailmaps\\metal_detail_dt","\\a3\\weapons_f\\data\\detailmaps\\metal_detail_dt"],
["ca\\weapons\\data\\detailmaps\\metal_rough_dt","\\a3\\weapons_f\\data\\detailmaps\\metal_rough_dt"],
["ca\\data\\env_land_plastic_co","a3\\data_f\\env_land_plastic_co"],
["ca\\data\\default_ti_ca", "a3\\data_f\\default_ti_ca"],
["ca\\ca_e\\data\\destruct_ti_ca", "a3\data_f\\destruct_ti_ca"], 
["ca\\data_baf\\env_land_baf_co", "a3\\data_f\\env_land_co"],
["ca\\weapons_e\\data\default_ti_ca", "a3\\data_f\\default_ti_ca"],
["ca\\data\\destruct\\metal_rough_half_dt", "CUP\\BaseConfigs\\CUP_BaseData\\Data\\metal_rough_half_dt"],
["ca\\data\\destruct\\metal_rough_full_dt", "CUP\\BaseConfigs\\CUP_BaseData\\Data\\metal_rough_full_dt"],
["ca\\data\\destruct\\destruct_plech_half_dt",  "a3\\data_f\\destruct\\destruct_plech_half_dt"],
["ca\\data\\destruct\\destruct_plech_half_mc",  "a3\\data_f\\destruct\\destruct_plech_half_mc"],
["ca\\data\\destruct\\destruct_plech_half_smdi",  "a3\\data_f\\destruct\\destruct_plech_half_smdi"],
["ca\\data\\destruct\\destruct_plech_full_dt",  "a3\\data_f\\destruct\\destruct_plech_full_dt"],
["ca\\data\\destruct\\destruct_plech_full_mc",  "a3\\data_f\\destruct\\destruct_plech_full_mc"],
["ca\\data\\destruct\\destruct_plech_full_smdi",  "a3\\data_f\\destruct\\destruct_plech_full_smdi"],
["ca\\data\\destruct\\destruct_rubber_half_dt",  "a3\\data_f\\destruct\\destr_rubber_half_dt"],
["ca\\data\\destruct\\damage_metal_basicarmor_dt", "a3\\data_f\\destruct\\damage_metal_basicarmor_dt"],
["ca\\data\\destruct\\destr_glass_plexi_full_nohq",  "a3\\data_f\\destruct\\destr_glass_plexi_full_nohq"],
["ca\\data\\destruct\\destr_glass_plexi_full_ca",  "a3\\data_f\\destruct\\destr_glass_plexi_full_ca"],
["ca\\data\\destruct\\destr_glass_plexi_full_smdi",  "a3\\data_f\\destruct\\destr_glass_plexi_full_smdi"],
["ca\\data\\destruct\\destr_glass_plexi_half_nohq",  "a3\\data_f\\destruct\\destr_glass_plexi_half_nohq"],
["ca\\data\\destruct\\destr_glass_plexi_half_ca",  "a3\\data_f\\destruct\\destr_glass_plexi_half_ca"],
["ca\\data\\destruct\\destr_glass_plexi_half_smdi",  "a3\\data_f\\destruct\\destr_glass_plexi_half_smdi"],
["ca\\structures\\Data\\DetailMaps\\Metal_Detail_DT", "\\a3\\weapons_f\\data\\detailmaps\\metal_detail_dt"],
["ca\\data\\destruct\\destr_glass_armour2_full_nohq",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_full_nohq"],
["ca\\data\\destruct\\destr_glass_armour2_full_ca",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_full_ca"],
["ca\\data\\destruct\\destr_glass_armour2_full_smdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_full_smdi"],
["ca\\data\\destruct\\destr_glass_armour2_half_nohq",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_half_nohq"],
["ca\\data\\destruct\\destr_glass_armour2_half_ca",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_half_ca"],
["ca\\data\\destruct\\destr_glass_armour2_half_smdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\destr_glass_armour2_half_smdi"],
["ca\\data\\destruct\\metal_01_broken_full_dt",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\metal_01_broken_full_dt"],
["ca\\data\\destruct\\metal_01_broken_full_dtsmdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\metal_01_broken_full_dtsmdi"],
["ca\\data\\destruct\\metal_01_broken_half_dt",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\metal_01_broken_half_dt"],
["ca\\data\\destruct\\metal_01_broken_half_dtsmdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Datadestruct\\\\metal_01_broken_half_dtsmdi"],
["ca\\data\\destruct\\vehicle_destr512_256_mc",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr512_256_mc"],
["ca\\data\\destruct\\vehicle_destr512_256_smdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr512_256_smdi"],
["ca\\data\\destruct\\vehicle_destr512_512_mc",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr512_512_mc"],
["ca\\data\\destruct\\vehicle_destr512_512_smdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr512_512_smdi"],
["ca\\data\\destruct\\vehicle_destr2048_1024_mc",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr2048_1024_mc"],
["ca\\data\\destruct\\vehicle_destr2048_2048_mc",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr2048_2048_mc"],
["ca\\data\\destruct\\vehicle_destr2048_2048_smdi",  "CUP\\BaseConfigs\\CUP_BaseData\\Data\\destruct\\vehicle_destr2048_2048_smdi"]

]


def rt_FindTextureNames(rvMatFile):
    
    textures = []
    
    with open(rvMatFile) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content] 
        f.close()
        
    for l in content:
        if "texture" in l.lower():
            t = l.split("=")
            if len(t) == 2:
                texture = t[1];
                if texture.rfind(";") >= 0:
                    texture = texture[:-1]
                texture = texture.strip("\"")
                texture = texture.strip("'")
                texture = texture.strip()

                if texture[0] != '#':
                    textures.append(texture)
                
    return textures

def rt_findTextureMatch(textureName):
    # Clean up the texture name
    # split the extension
    base,ext = path.splitext(textureName)
    
    # make it lower-case
    base = base.lower()
    
    # Remove leading \
    base = base.strip('\\')
    
    for pair in static_texture_translation:
        #print(pair[0], "==", base, "?")
        if pair[0] == base:
            return pair[1] + ".paa", True

    return base + ".paa", False

###
##  Read textures inside an rvMat file
#
def rt_readTextures(rvMatFile):
    
    textures = []
    
    with open(rvMatFile) as f:
        content = f.readlines()
        content = [x.strip() for x in content] 
        
    for l in content:
        if "texture" in l.lower():
            t = l.split("=")
            if len(t) == 2:
                texture = t[1];
                if texture.rfind(";") >= 0:
                    texture = texture[:-1]
                texture = texture.strip("\"")
                texture = texture.strip("'")
                texture = texture.strip()

                if texture[0] != '#':
                    textures.append(texture)
                
    return textures

###
##  Replace the texture names in an rvmat file
#   
def ft_replaceNames(rvmatName, repList):
    with open(rvmatName) as f:
        content = f.readlines()

    
    with open(rvmatName, "w") as f:
        for l in content:
            if "texture" in l.lower():
                out = l
                for rep in repList:
                    idx = l.lower().find(rep[0].lower())
                    if idx != -1:
                        out = l[:idx] + rep[1] + l[idx+len(rep[0]):]
                        print(out)
                        break
                f.write(out)
            else:
                f.write(l)

    

def rt_smartCopy(srcFile, dstFile):
    if path.exists(srcFile):
        shutil.copyfile(srcFile, dstFile)
        return
    
    srcFile = path.splitext(srcFile)[0] + ".paa"
    if path.exists(srcFile):
        shutil.copyfile(srcFile, dstFile)
        return
    
    srcFile = path.splitext(srcFile)[0] + ".tga"
    if path.exists(srcFile):
        shutil.copyfile(srcFile, dstFile)
        return
    
    raise FileNotFoundError

def rt_MoveRVMAT(rvmatName, prefixPath="P:\\"):
    # Construct the output name on the drive. This assumes the rvMat is on the P drive
    outputFolder = path.split(rvmatName)[0]
    
    # Construct the output name in Game terms. This assumes outputFolder is on the P drive
    gameOutputFolder = path.splitdrive(outputFolder)[1]
    gameOutputFolder = gameOutputFolder.strip("\\")

    # Get the textures for this
    textures = rt_readTextures(rvmatName)
    
    outputList = []
    
    for tex in textures:
        texture, replaced = rt_findTextureMatch(tex)
        if replaced is True:
            outputList.append([tex, texture])
        else:
            # Copy the texture
            srcFile = path.join(prefixPath, path.splitext(tex)[0] + ".paa")
            dstFile = path.join(outputFolder, path.basename(texture))
            print("Need to copy " + srcFile + " to " + dstFile)
            try:
                rt_smartCopy(srcFile, dstFile)
            except:
                pass
            
            # Add the replacement to the list
            texBase = path.split(texture)[1]
            outputList.append([tex, path.join(gameOutputFolder,texBase)])
    
    ft_replaceNames(rvmatName, outputList)
    

def rt_CopyRVMat(rvmatName, outputFolder, prefixPath="P:\\"):
    if path.splitext(outputFolder)[1] == '.rvmat':
        outputRV = outputFolder
    else:
        outputRV = path.join(outputFolder, path.basename(rvmatName))
    
    try:
        shutil.copy(rvmatName, outputRV)
    except:
        pass
        
    rt_MoveRVMAT(outputRV, prefixPath)
    
    
#
# Copy/Adapt(/Win?) textures from the model
#

def mt_stripAddonPath(apath):
    if apath == "" or apath == None: 
        return ""
    if path.isabs(apath):
        p = path.splitdrive(apath)
        return p[1][1:]
    elif apath[0] == '\\':
        return apath[1:]
    else:
        return apath

def mt_getMaterialInfo(material):
    textureName = ""
    texType = material.armaMatProps.texType;
    
    if texType == 'Texture':
        textureName = material.armaMatProps.texture;
        textureName = mt_stripAddonPath(textureName);
    elif texType == 'Custom':
        textureName = material.armaMatProps.colorString;
    elif texType == 'Color':
        textureName = "#(argb,8,8,3)color({0:.3f},{1:.3f},{2:.3f},1.0,{3})".format( 
            material.armaMatProps.colorValue.r, 
            material.armaMatProps.colorValue.g, 
            material.armaMatProps.colorValue.b, 
            material.armaMatProps.colorType)

    materialName = mt_stripAddonPath(material.armaMatProps.rvMat)
    
    return (materialName, textureName)

def rt_SmartCopy(texName, outputName):
    if path.exists(outputName):
        print ("output file exists")
        pass
    else:
        shutil.copy(texName, outputPath)

def rt_CopyTexture(texName, outputPath):
    print("rt_CopyTexture " + texName + "," + outputPath)
    if path.exists(texName):
        print("copying")
        rt_SmartCopy(texName, outputPath)
    else:
        # Try with a different extension
        p,e = path.splitext(texName)
        if e == ".paa":
            e = ".tga"
        else:
            e = ".paa"
        texName = p + e
        if path.exists(texName):
            p,e = path.splitext(outputPath)
            if e == ".paa":
                e = ".tga"
            else:
                e = ".paa"
            outputPath = p + e
            rt_SmartCopy(texName, outputPath)

def mt_RelocateMaterial(textureName, materialName, outputPath, copyRV, prefixPath):
    #print("mt_RelocateMaterial: textureName = ", textureName, " materialName = ", materialName, "\n")
    if len(materialName) > 0:
        baseMat = path.basename(materialName)
        # Construct real path
        if len(path.splitdrive(materialName)[0]) > 0:
            #print("Material has absolute path\n")
            rvmatName = materialName
        else:
            #print("material has relative path\n")
            rvmatName = path.join(prefixPath, materialName)
        
        outputName = path.join(outputPath, baseMat)
        
        if copyRV == True:
            rt_CopyRVMat(rvmatName, outputName, prefixPath)
        else:
            shutil.copy(rvmatName, outputName)
            
        for mat in bpy.data.materials:
            if mat.armaMatProps.rvMat == materialName:
                mat.armaMatProps.rvMat = outputName

    if len(textureName) > 0:
        baseTex = path.basename(textureName)
        if len(path.splitdrive(textureName)[0]) > 0:
            texName = textureName
        else:
            texName = path.join(prefixPath, textureName)

        outputName = path.join(outputPath, baseTex)
        print (texName, outputName)
        # TODO: might need to go through a replacement here...?
        rt_CopyTexture(texName, outputName)
        
        for mat in bpy.data.materials:
            if mat.armaMatProps.texType == 'Texture':
                if mat.armaMatProps.texture == textureName:
                    mat.armaMatProps.texture = outputName
