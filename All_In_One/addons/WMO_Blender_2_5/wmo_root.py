
import bpy
from . import wmo_format
from .wmo_format import *

import os

class WMO_root_file:
    def __init__(self):
        self.mver = MVER_chunk()
        self.mohd = MOHD_chunk()
        self.motx = MOTX_chunk()
        self.momt = MOMT_chunk()
        self.mogn = MOGN_chunk()
        self.mogi = MOGI_chunk()
        self.mosb = MOSB_chunk()
        self.mopv = MOPV_chunk()
        self.mopt = MOPT_chunk()
        self.mopr = MOPR_chunk()
        self.movv = MOVV_chunk()
        self.movb = MOVB_chunk()
        self.molt = MOLT_chunk()
        self.mods = MODS_chunk()
        self.modn = MODN_chunk()
        self.modd = MODD_chunk()
        self.mfog = MFOG_chunk()

        self.materialLookup = {}
        self.textureLookup = {}

    def Read(self, f):
        self.mver.Read(f)
        self.mohd.Read(f)
        self.motx.Read(f)
        self.momt.Read(f)
        self.mogn.Read(f)
        self.mogi.Read(f)
        self.mosb.Read(f)
        self.mopv.Read(f)
        self.mopt.Read(f)
        self.mopr.Read(f)
        self.movv.Read(f)
        self.movb.Read(f)
        self.molt.Read(f)
        self.mods.Read(f)
        self.modn.Read(f)
        self.modd.Read(f)
        self.mfog.Read(f)

    
    #def LoadDoodads(self):
        #for i in range(self.mods):

    # mat is a bpy.types.Material
    def AddMaterial(self, mat):
        """ Add material if not already added, then return index in root file """

        if mat in self.materialLookup:
            # if material already added, return index
            return self.materialLookup[mat]
        else:
            # else add it then return index
            if(not mat.WowMaterial.Enabled):
                self.materialLookup[mat] = 0xFF
                return 0xFF
            else:
                self.materialLookup[mat] = len(self.momt.Materials)

                WowMat = WMO_Material()
                WowMat.Flags1 = 0
                WowMat.Shader = int(mat.WowMaterial.Shader)
                WowMat.BlendMode = int(mat.WowMaterial.Transparent)

                if mat.WowMaterial.Texture1 in self.textureLookup:
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]
                else:
                    self.textureLookup[mat.WowMaterial.Texture1] = self.motx.AddString(mat.WowMaterial.Texture1)
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]

                WowMat.Color1 = (mat.WowMaterial.Color1[0], mat.WowMaterial.Color1[1], mat.WowMaterial.Color1[2], 1)
                WowMat.TextureFlags1 = 0

                if mat.WowMaterial.Texture2 in self.textureLookup:
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]
                else:
                    self.textureLookup[mat.WowMaterial.Texture2] = self.motx.AddString(mat.WowMaterial.Texture2)
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]

                WowMat.Color2 = (mat.WowMaterial.Color2[0], mat.WowMaterial.Color2[1], mat.WowMaterial.Color2[2], 1)
                WowMat.TextureFlags2 = 0

                if mat.WowMaterial.Texture3 in self.textureLookup:
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]
                else:
                    self.textureLookup[mat.WowMaterial.Texture3] = self.motx.AddString(mat.WowMaterial.Texture3)
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]

                WowMat.Color3 = (mat.WowMaterial.Color3[0], mat.WowMaterial.Color3[1], mat.WowMaterial.Color3[2], 1)

                WowMat.DiffColor = (0, 0, 0)
                WowMat.RunTimeData = (0, 0)

                self.momt.Materials.append(WowMat)

                return self.materialLookup[mat]

    def AddGroupInfo(self, flags, boundingBox, name, desc):
        """ Add group info, then return offset of name and desc in a tuple """
        group_info = GroupInfo()

        group_info.Flags = flags # 8
        group_info.BoundingBoxCorner1 = boundingBox[0].copy()
        group_info.BoundingBoxCorner2 = boundingBox[1].copy()
        group_info.NameOfs = self.mogn.AddString(name) #0xFFFFFFFF

        descOfs = self.mogn.AddString(desc)

        self.mogi.Infos.append(group_info)

        return (group_info.NameOfs, descOfs)

    def LoadMaterials(self, name, texturePath):
        self.materials = {}

        images = []
        imageNames = []

        # Add ghost material
        mat = bpy.data.materials.get("WowMaterial_ghost")
        if(not mat):
            mat = bpy.data.materials.new("WowMaterial_ghost")
            mat.diffuse_color = (0.2, 0.5, 1.0)
            mat.diffuse_intensity = 1.0
            mat.alpha = 0.15
            mat.transparency_method = 'Z_TRANSPARENCY'
            mat.use_transparency = True

        self.materials[0xFF] = mat

        for i in range(len(self.momt.Materials)):
            material_name = name + "_Mat_" + str(i).zfill(2)

            mat = bpy.data.materials.new(material_name)
            self.materials[i] = mat

            mat.WowMaterial.Enabled = True
            mat.WowMaterial.Shader = str(self.momt.Materials[i].Shader)
            mat.WowMaterial.Transparent = (self.momt.Materials[i].BlendMode == 1)
            mat.WowMaterial.Texture1 = self.motx.GetString(self.momt.Materials[i].Texture1Ofs)
            mat.WowMaterial.Color1 = [x / 255 for x in self.momt.Materials[i].Color1[0:3]]
            mat.WowMaterial.Flags1 = '1' if self.momt.Materials[i].TextureFlags1 & 0x80 else '0'
            mat.WowMaterial.Texture2 = self.motx.GetString(self.momt.Materials[i].Texture2Ofs)
            mat.WowMaterial.Color2 = [x / 255 for x in self.momt.Materials[i].Color2[0:3]]
            mat.WowMaterial.Flags2 = '1' if self.momt.Materials[i].TextureFlags2 & 0x80 else '0'
            mat.WowMaterial.Texture3 = self.motx.GetString(self.momt.Materials[i].Texture3Ofs)
            mat.WowMaterial.Color3 = [x / 255 for x in self.momt.Materials[i].Color3[0:3]]
            mat.WowMaterial.Flags3 = '0'#1' if momt.Materials[i].TextureFlags1 & 0x80 else '0'

            # set texture slot and load texture
            if mat.WowMaterial.Texture1:
                tex1_slot = mat.texture_slots.create(2)
                tex1_slot.uv_layer = "UVMap"
                tex1_slot.texture_coords = 'UV'

                tex1_name = material_name + "_Tex_01"
                tex1 = bpy.data.textures.new(tex1_name, 'IMAGE')
                tex1_slot.texture = tex1

                try:
                    tex1_img_filename = os.path.splitext(os.path.basename(mat.WowMaterial.Texture1))[0] + ".png"

                    img1_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex1_img_filename):
                            tex1.image = images[iImg]
                            img1_loaded = True
                            break

                    # if image is not loaded, do it
                    if(img1_loaded == False):
                        tex1_img = bpy.data.images.load(texturePath + tex1_img_filename)
                        tex1.image = tex1_img
                        images.append(tex1_img)
                        imageNames.append(tex1_img_filename)

                except:
                    pass


            # set texture slot and load texture
            if mat.WowMaterial.Texture2:
                tex2_slot = mat.texture_slots.create(1)
                tex2_slot.uv_layer = "UVMap"
                tex2_slot.texture_coords = 'UV'
                
                tex2_name = material_name + "_Tex_02"
                tex2 = bpy.data.textures.new(tex2_name, 'IMAGE')
                tex2_slot.texture = tex2

                try:
                    tex2_img_filename = os.path.splitext(os.path.basename(mat.WowMaterial.Texture2))[0] + ".png"
                    
                    img2_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex2_img_filename):
                            tex2.image = images[iImg]
                            img2_loaded = True
                            break

                    # if image is not loaded, do it
                    if(img2_loaded == False):
                        tex2_img = bpy.data.images.load(texturePath + tex2_img_filename)
                        tex2.image = tex2_img
                        images.append(tex2_img)
                        imageNames.append(tex2_img_filename)
                except:
                    pass

            # set texture slot and load texture
            if mat.WowMaterial.Texture3:
                tex3_slot = mat.texture_slots.create(0)
                tex3_slot.uv_layer = "UVMap"
                tex3_slot.texture_coords = 'UV'
                
                tex3_name = material_name + "_Tex_03"
                tex3 = bpy.data.textures.new(tex3_name, 'IMAGE')
                tex3_slot.texture = tex3

                try:
                    tex3_img_filename = os.path.splitext(os.path.basename(mat.WowMaterial.Texture3))[0] + ".png"
                    
                    img3_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex3_img_filename):
                            tex3.image = images[iImg]
                            img3_loaded = True
                            break

                    # if image is not loaded, do it
                    if(img3_loaded == False):
                        tex3_img = bpy.data.images.load(texturePath + tex3_img_filename)
                        tex3.image = tex3_img
                        images.append(tex3_img)
                        imageNames.append(tex3_img_filename)
                except:
                    pass

    def LoadLights(self, name):
        self.lights = []
        for i in range(len(self.molt.Lights)):
            light_name = name + "_Light_" + str(i).zfill(2)

            l = self.molt.Lights[i]

            
            if(l.LightType == 0): # omni
                l_type = 'POINT'
            elif(l.LightType == 1): # spot
                l_type = 'SPOT'
            elif(l.LightType == 2): # direct
                l_type = 'SUN'
            elif(l.LightType == 3): # ambiant
                l_type = 'POINT'    # use point with no attenuation
            else:
                raise Exception("Light type unknown :" + str(l.LightType) + "(light nbr : " + str(i) + ")")

            light_name = name + "_Light_" + str(i).zfill(2)
            light = bpy.data.lamps.new(light_name, l_type)
            light.color = (l.Color[2] / 255, l.Color[1] / 255, l.Color[0] / 255)
            light.energy = l.Intensity

            if(l.LightType == 0 or l.LightType == 1):
                light.falloff_type = 'INVERSE_LINEAR'
                light.distance = l.Unknown4 / 2
                light.use_sphere = True

            light.WowLight.Enabled = True
            light.WowLight.LightType = str(l.LightType)
            light.WowLight.UseAttenuation = bool(l.UseAttenuation)
            light.WowLight.Color = light.color
            light.WowLight.Intensity = l.Intensity
            light.WowLight.AttenuationStart = l.AttenuationStart
            light.WowLight.AttenuationEnd = l.AttenuationEnd

            obj = bpy.data.objects.new(light_name, light)
            obj.location = self.molt.Lights[i].Position

            bpy.context.scene.objects.link(obj)

    def GetObjectBoundingBox(self, obj):
        corner1 = [0, 0, 0]
        corner2 = [0, 0, 0]
        
        for v in obj.bound_box:
            if(v[0] < corner1[0]):
                corner1[0] = v[0]
            if(v[1] < corner1[1]):
                corner1[1] = v[1]
            if(v[2] < corner1[2]):
                corner1[2] = v[2]
                
            if(v[0] > corner2[0]):
                corner2[0] = v[0]
            if(v[1] > corner2[1]):
                corner2[1] = v[1]
            if(v[2] > corner2[2]):
                corner2[2] = v[2]

        return (corner1, corner2)

    def GetGlobalBoundingBox(self):
        corner1 = self.mogi.Infos[0].BoundingBoxCorner1
        corner2 = self.mogi.Infos[0].BoundingBoxCorner2
        
        for gi in self.mogi.Infos:
            v = gi.BoundingBoxCorner1
            if(v[0] < corner1[0]):
                corner1[0] = v[0]
            if(v[1] < corner1[1]):
                corner1[1] = v[1]
            if(v[2] < corner1[2]):
                corner1[2] = v[2]
                
            v = gi.BoundingBoxCorner2                
            if(v[0] > corner2[0]):
                corner2[0] = v[0]
            if(v[1] > corner2[1]):
                corner2[1] = v[1]
            if(v[2] > corner2[2]):
                corner2[2] = v[2]

        return (corner1, corner2)

    def Save(self, f):

        # set version header
        self.mver.Version = 17


        # set header
        bb = self.GetGlobalBoundingBox()

        self.mohd.nMaterials = len(self.momt.Materials)
        self.mohd.nGroups = len(self.mogi.Infos)
        self.mohd.nPortals = len(self.mopt.Infos)
        self.mohd.nLights = len(self.molt.Lights)
        self.mohd.nModels = 0
        self.mohd.nDoodads = len(self.modd.Definitions)
        self.mohd.nSets = len(self.mods.Sets)
        self.mohd.AmbientColor = (0, 0, 0, 1)
        self.mohd.ID = 0#4435
        self.mohd.BoundingBoxCorner1 = bb[0]
        self.mohd.BoundingBoxCorner2 = bb[1]
        self.mohd.LiquidType = 5 # 5 = no liquid? 0 = ocean?

        # write all chunks
        self.mver.Write(f)
        self.mohd.Write(f)
        self.motx.Write(f)
        self.momt.Write(f)
        self.mogn.Write(f)
        self.mogi.Write(f)
        self.mosb.Write(f)
        self.mopv.Write(f)
        self.mopt.Write(f)
        self.mopr.Write(f)
        self.movv.Write(f)
        self.movb.Write(f)
        self.molt.Write(f)
        self.mods.Write(f)
        self.modn.Write(f)
        self.modd.Write(f)
        self.mfog.Write(f)

        return
