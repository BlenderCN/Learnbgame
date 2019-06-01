##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

import bpy, re, os
from . import help_funcs, import_tobj

class MAT:
    def __init__(self, material_base_path, filepath):
        self.mat_base_path = material_base_path
        self.path = filepath[:filepath.rfind("/")+1]
        self.filename = filepath[filepath.rfind("/")+1:]
        f = open(self.mat_base_path+self.path+self.filename, "r")
        self.text = f.read()
        f.close()
        self.shading = ""
        self.entries = {}
        
    def parse(self):
        #with regex parse whole material as key : value
        p = re.compile(r"(\S+)\s*:\s*(\{\s*\S+\s*,\s*\S+\s*,\s*\S+[^\S\n]*\}|\{\s*\S+\s*,\s*\S+[^\S\n]*\}|\S+)")
        entrs = p.findall(self.text)
        for entry in entrs:
            #print("Trying to parse entry:", entry)
            if entry[0] == "material":
                self.shading = entry[1]
            else:
                nums3_m = re.match(r"\{\s*(\S+)\s*,\s*(\S+)\s*,\s*(\S+)\s*\}", entry[1])
                nums2_m = re.match(r"\{\s*(\S+)\s*,\s*(\S+)\s*\}", entry[1])
                #check if current entry has { x,x,x } pattern
                if not nums3_m is None:
                    self.entries[entry[0]] = (float(nums3_m.groups(0)[0]), 
                            float(nums3_m.groups(0)[1]),
                            float(nums3_m.groups(0)[2]))
                elif not nums2_m is None:
                    self.entries[entry[0]] = (float(nums2_m.groups(0)[0]), 
                            float(nums2_m.groups(0)[1]))
                else:
                    self.entries[entry[0]] = entry[1]
        
    #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
    #def create_mat(self, scs_base, basepath, look_indx, tobj_dic):
    def create_mat(self, scs_base, basepath, tobj_dic):
        path = self.mat_base_path+self.path+self.filename
        new_mat_name = path[path.rfind('/')+1:path.rfind('.')]
        self.name = new_mat_name
        if new_mat_name in bpy.data.materials:
            #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
            #mat = bpy.data.materials[new_mat_name]
            #set material avaliable to all looks (look_idx == -1)
            #mat.scs_look_idx = -1
            return
        
        mat = bpy.data.materials.new(new_mat_name)
        mat.use_vertex_color_paint = True
        mat.use_raytrace = False
        mat.scs_shading = self.shading.strip('"')
        if mat.scs_shading.count("over"):
            mat.use_transparency = True
        #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
        #mat.scs_look_idx = look_indx
        mat["scs_mat_options"] = { }
        keys = sorted(self.entries.keys())
        for option in keys:
            """
            if option == "diffuse":
                mat.diffuse_color = Color(self.entries["diffuse"])
            elif option == "specular":
                mat.specular_color = Color(self.entries["specular"])
            elif option == "shininess":
                mat.specular_hardness = int(self.entries["shininess"])
            el"""
            if (option == "texture[0]" or option == "texture[1]" or 
                option == "texture[2]" or option == "texture[3]" or
                option == "texture"):
                if option.count('0') == 1:
                    tex_idx = 0
                elif option.count('1') == 1:
                    tex_idx = 1
                elif option.count('2') == 1:
                    tex_idx = 2
                elif option.count('3') == 1:
                    tex_idx = 3
                else:
                    tex_idx = -1
                
                #if there is no array like assignment
                if tex_idx == -1:
                    opt_str = ''
                    tex_idx = 0
                else:
                    opt_str = '['+str(tex_idx)+']'

                mat_tex_type_key = 'texture_name'+opt_str
                mat_tex_type = "texture_base"
                #if texture_name exist overwrite default type value
                if mat_tex_type_key in self.entries:
                    mat_tex_type = self.entries[mat_tex_type_key]

                tobj_path = self.entries['texture'+opt_str].replace("\"", "") #absolute path to tobj
                tex = self.__read_TOBJ(scs_base, basepath, tobj_path, tobj_dic, False, mat_tex_type.strip('"'))
                
                #overrride tobj path if texture comes from "/material/evironment" folder
                if (self.entries['texture'+opt_str].count("material/environment") == 1 or
                    self.entries['texture'+opt_str].count("/vehicle/truck/share/") == 1 or
                    self.entries['texture'+opt_str].count("/system/special/") == 1):
                    tex["scs_extra_tex"] = self.entries['texture'+opt_str].strip('"')
                    
                mat.texture_slots.add()
                mat.texture_slots[tex_idx].texture = tex

                self.__set_tex_props(mat.texture_slots[tex_idx],
                                     mat_tex_type,
                                     mat)
            elif option.count("texture_name") == 1:
                #pass entry named "texture_name" cuz it's already used by texture
                pass
            else: #write option to custom properties
                mat["scs_mat_options"][option] = str(self.entries[option])
        return 0
                     
    def __set_tex_props(self, tex_s, type, mat):
        tex_s.texture.extension = 'CLIP'
        type = type.strip('"')
        tex_s.texture["scs_tex_base"] = type
        if mat.use_transparency:
            tex_s.texture.image.use_alpha = True
            tex_s.texture.use_alpha = True
            tex_s.use_map_alpha = True
        if type == "texture_base":
            #tex_s.texture.image.use_alpha = False
            tex_s.blend_type = 'MULTIPLY'
            tex_s.texture_coords = 'UV'
            tex_s.uv_layer = 'UVMap'
            tex_s.texture.image.use_clamp_y=True
            tex_s.texture.image.use_clamp_x=True
        elif type == "texture_mask":
            tex_s.use_map_alpha = True
            tex_s.diffuse_color_factor = 0.3
            tex_s.texture_coords = 'UV'
            tex_s.uv_layer = 'UVMap.001'
        elif type == "texture_reflection":
            tex_s.diffuse_color_factor = 0.5
            tex_s.blend_type = 'MULTIPLY'
            tex_s.texture_coords = 'REFLECTION'
        elif type == "texture_paintjob":
            tex_s.use_map_alpha = True
            tex_s.diffuse_color_factor = 0.65
            tex_s.texture_coords = 'UV'
            tex_s.uv_layer = 'UVMap.001'
        elif type == "texture_mult":
            tex_s.blend_type = 'MULTIPLY'
            tex_s.texture_coords = 'UV'
            tex_s.uv_layer = 'UVMap.001'
            tex_s.texture.image.use_clamp_y=True
            tex_s.texture.image.use_clamp_x=True
        elif type == "texture_over":
            tex_s.blend_type = 'OVERLAY'
            tex_s.texture_coords = 'UV'
            tex_s.uv_layer = 'UVMap.001'
        elif type == "texture_nmap":
            tex_s.texture_coords = 'UV'
            if (mat.scs_shading.count("mapuv") > 0 and 
                mat.scs_shading.count("truckpaint") == 0):
                tex_s.uv_layer = 'UVMap.001'
            else:
                tex_s.uv_layer = 'UVMap'
            tex_s.use_map_normal = True
            tex_s.use_map_color_diffuse = False
            tex_s.bump_objectspace = 'BUMP_TEXTURESPACE'
            

    def __find_path(self, scs_base, basepath, filepath):
        """
        Search for all possible matches of path. If none is found scs_base+filepath is returned
        even if doesn't exist
        Path checker order:
        1. mat_base_path
        2. basepath
        3. scs_base
        @param scs_base: path to scs base
        @param basepath: additional base path
        @param filepath: file which should be found
        @return: string
        """
        if os.path.exists(self.mat_base_path+self.path+filepath):
            real_path = self.mat_base_path+self.path+filepath
        elif os.path.exists(self.mat_base_path+filepath):
            real_path = self.mat_base_path+filepath
        elif os.path.exists(basepath+self.path+filepath):
            real_path = basepath+self.path+filepath
        elif os.path.exists(basepath+filepath):
            real_path = basepath+filepath
        elif os.path.exists(scs_base+self.path+filepath):
            real_path = scs_base+self.path+filepath
        else:
            real_path = scs_base+filepath
        return real_path

    def __read_TOBJ(self, scs_base, basepath, filepath, tobj_dic, use_alpha=True, texture_type=None):
        # print("Reading TOBJ...")
        # print("Mat Base:", self.mat_base_path, "\n")
        # print("Tobj path:", filepath, "\n")

        real_tobj_path = self.__find_path(scs_base, basepath, filepath)

        if os.path.exists(real_tobj_path):
            abs_tobj_path = bpy.path.abspath(real_tobj_path)
            tobj = import_tobj.TOBJ(abs_tobj_path)

            #check if tobj already exists
            if abs_tobj_path in tobj_dic:
                tex = tobj_dic[abs_tobj_path]
                # check if this is the same texture with different type
                # then duplicate texture becuse scs_tex_base property can sadly
                # be only one per texture so same texture with different scs_tex_type
                # needs to be duplicated
                if texture_type is not None and texture_type != tex["scs_tex_base"]:
                    new_tobj_abs_path = abs_tobj_path + "_" + texture_type
                    if new_tobj_abs_path in tobj_dic:
                        tex = tobj_dic[new_tobj_abs_path]
                    else:
                        tex = tex.copy()
                        tex.name = tobj.tobj_name + "_" + texture_type
                        tobj_dic[new_tobj_abs_path] = tex
            else:
                real_dds_path = self.__find_path(scs_base, basepath, tobj.tex_path)

                abs_dds_path = bpy.path.abspath(real_dds_path)

                #check if any loaded tobj with same name
                same_bl_tex_names = [tex for tex in bpy.data.textures
                                    if tobj.tobj_name == tex.name]
                if len(same_bl_tex_names) > 0:
                    tobj.tobj_name += str(len(same_bl_tex_names))
                tex = bpy.data.textures.new(tobj.tobj_name, 'IMAGE')
                tex.use_alpha = use_alpha

                #check if any loaded images with same filepath
                same_bl_img = [img for img in bpy.data.images
                                    if abs_dds_path == img.filepath]
                if len(same_bl_img) > 0:
                    img = same_bl_img[0]
                else:
                    #check if any loaded images with same name
                    same_bl_img_names = [img for img in bpy.data.images
                                            if tobj.tex_name == img.name]
                    if len(same_bl_img_names) > 0:
                        tobj.tex_name += str(len(same_bl_img_names))
                    img = bpy.data.images.load(abs_dds_path)
                    img.name = tobj.tex_name
                tex.image = img

                #check if item in mapping enum
                map_type = str(tuple((tobj.un6, tobj.un8, tobj.un9)))
                items =  [item for item in bpy.types.Texture.scs_map_type[1]['items']
                            if item[0] == map_type]
                if len(items) == 0:
                    help_funcs.PrintDeb("\n\nWarning: Texture mapping: ", map_type , "not found in library, setting to default\n")
                    map_type = '(0, 0, 0)' #default mapping
                tex.scs_map_type = map_type

                tobj_dic[abs_tobj_path] = tex
        else:
            dummy_name = "notfound_"+filepath[filepath.rfind('/')+1:filepath.rfind('.')]
            if not dummy_name in bpy.data.textures.keys():
                tex = bpy.data.textures.new(dummy_name, 'IMAGE')
                bpy.ops.image.new(name=dummy_name)
                tex.image = bpy.data.images[dummy_name]
                help_funcs.PrintDeb("\n\nWarning: Can't find tobj file:'"+filepath+"'. Texture file won't be loaded!\n")
                
                tex.scs_map_type = str(tuple((1, 33685507, 256)))
            else:
                tex = bpy.data.textures[dummy_name]
        return tex
        
        
    def print_self(self, additional=None):
        print("Path: ", self.path)
        print("\nShading: ", self.shading)
        for entry in self.entries.keys():
            print("Key:", entry, "Val: ", self.entries[entry])
        if not additional is None:
            print("Additional: ", additional)
        