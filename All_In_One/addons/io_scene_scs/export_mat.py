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

import bpy, os, shutil
from . import export_tobj, help_funcs
from ast import literal_eval

class MAT:
    def __init__(self, exportpath, originpath, bl_mat):
        self.err_msg = ""
        self.__exportpath = exportpath
        self.__originpath = originpath
        self.__bl_mat = bl_mat
        self.__name = bl_mat.name+'.mat'
        self.__shading = bl_mat.scs_shading
        self.__textures = []
        tex_slots = [tex_s for tex_s in bl_mat.texture_slots if tex_s != None]
        for tex_s in tex_slots:
            tex = tex_s.texture
            if "scs_tex_base" not in tex:
                self.err_msg = ("Texture '"+tex.name+
                                "'on material '"+bl_mat.name+
                                "' is missing 'scs_tex_base' custom property!")
                return
            self.__textures.append(tex.name)
                    
        self.__options = bl_mat["scs_mat_options"]
    def write(self, copy_textures):
        if self.err_msg != "":
            return self.err_msg
        
        mats_path = self.__exportpath+'/'+self.__originpath+'/materials/'
        tobj_origin = '/'+self.__originpath+'/textures/'
        if not os.path.exists(mats_path):
            os.makedirs(mats_path)
        if not os.path.exists(self.__exportpath+tobj_origin):
            os.makedirs(self.__exportpath+tobj_origin)
        
        with open(mats_path+self.__name, "w") as f:
            f.write('material : "'+self.__shading+'" {\n')
            i=0 #texture index
            tex_lib = {}
            for tex_name in self.__textures:
                curr_tex = bpy.data.textures[tex_name]
                img_fpath = bpy.path.abspath(curr_tex.image.filepath)
                tex_base = curr_tex["scs_tex_base"]
                tobj_path = tobj_origin+tex_name+'.tobj'
                dds_path = tobj_origin+bpy.path.basename(img_fpath) #write actual image name
                #if tobj file not yet created and tobj won't be overwriten
                #by existing tobj then create new
                if not tobj_path in tex_lib and "scs_extra_tex" not in curr_tex :
                    unk6, unk8, unk9 = self.__get_tobj_unks(curr_tex)
                    self.__write_tobj(self.__exportpath+tobj_path, dds_path, unk6, unk8, unk9)
                    if copy_textures:
                        try:
                            shutil.copyfile(img_fpath, self.__exportpath+dds_path)
                        except Exception as e:
                            exp_str = str(e)
                            if exp_str.find("are the same file") != -1:
                                help_funcs.PrintDeb("\nInfo: Texture \""+dds_path[dds_path.rfind("/")+1:]+"\" won't be copied as model is exporting to import path!")
                            else:
                                return exp_str


                    tex_lib[tobj_path] = True
                
                if "scs_extra_tex" in curr_tex:
                    tobj_path = curr_tex["scs_extra_tex"]
                f.write('\ttexture['+str(i)+'] : "'+tobj_path+'"\n')
                f.write('\ttexture_name['+str(i)+'] : "'+tex_base+'"\n')
                i+=1
            for option in self.__options.keys():
                op_val = literal_eval(self.__options[option])
                if type(op_val) == tuple:
                    value = '{ '
                    for single_val in op_val:
                        value += str(single_val)+' , '
                    value = value.rstrip(', ')
                    value += ' }'
                elif type(op_val) == int or type(op_val) == float:
                    value = str(op_val)
                else:
                    value = '"'+str(op_val)+'"'
                f.write('\t'+option+' : '+value+'\n')
            f.write('}\n')
        return None
    
    def __write_tobj(self, tobj_path, dds_path, unk6, unk8, unk9):
        tobj = export_tobj.TOBJ(1890650625, unk6, 50528258, 
                    unk8, unk9, 256, 
                    dds_path)
        with open(tobj_path, "wb")as f:
            f.write(tobj.to_scs_bytes())
    
    def __get_tobj_unks(self, curr_tex):
        unks = literal_eval(curr_tex.scs_map_type)
        return unks[0],unks[1],unks[2]

"""
export_path = "E:"
origin_path = "EXPORT/first"
bl_mat = bpy.data.materials['7414bac60dd9ae05999f5f4e98286c48677915']
a = MAT(export_path, origin_path, bl_mat)
ret_ob = a.write(False)
if ret_ob == None:
    print("Exporting MAT file succseful!")
"""