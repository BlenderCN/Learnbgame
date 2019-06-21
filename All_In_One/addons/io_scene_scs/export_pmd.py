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

import time
from . import help_funcs, export_mat


###############################################
#
# Base classe for saving definitions of pmd
#
###############################################
class PMDHeader:
    def __init__(self, ver, no_mats, no_looks, no_parts, no_vars,
                 no_visi_defs):
        """
        ver - version of pmd file
        no_mats - number of materials in model
        no_looks - number of looks in model
        no_parts - number of models in model
        no_vars - number of variants in model
        no_visi_defs - number of visibility definitions (number of sections)
        """
        self.__ver = ver
        self.no_mats = no_mats
        self.no_looks = no_looks
        self.no_parts = no_parts
        self.no_varians = no_vars
        self.__no_visi_links = no_visi_defs
        self.__no_visi_defs = no_visi_defs
        self.__no_varians_visi = no_visi_defs * 4
        self.mats_block_size = 0
        self.looks_off = 0
        self.varians_off = 0
        self.visi_links_off = 0
        self.varians_visi_off = 0
        self.visi_defs_off = 0
        self.mats_defs_off = 0
        self.mats_block_off = 0

    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__ver)
        bytes += help_funcs.UInt32ToByts(self.no_mats)
        bytes += help_funcs.UInt32ToByts(self.no_looks)
        bytes += help_funcs.UInt32ToByts(self.no_parts)
        bytes += help_funcs.UInt32ToByts(self.no_varians)
        bytes += help_funcs.UInt32ToByts(self.__no_visi_links)
        bytes += help_funcs.UInt32ToByts(self.__no_visi_defs)
        bytes += help_funcs.UInt32ToByts(self.__no_varians_visi)

        bytes += help_funcs.UInt32ToByts(self.mats_block_size)

        bytes += help_funcs.UInt32ToByts(self.looks_off)
        bytes += help_funcs.UInt32ToByts(self.varians_off)
        bytes += help_funcs.UInt32ToByts(self.visi_links_off)
        bytes += help_funcs.UInt32ToByts(self.varians_visi_off)
        bytes += help_funcs.UInt32ToByts(self.visi_defs_off)
        bytes += help_funcs.UInt32ToByts(self.mats_defs_off)
        bytes += help_funcs.UInt32ToByts(self.mats_block_off)
        return bytes


class PMDLook:
    def __init__(self, name):
        """
        name - name of look used for sii files (max length 12)
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())

    def to_scs_bytes(self):
        return help_funcs.UInt64ToByts(self.__name)


class PMDVariant:
    def __init__(self, name):
        """
        name - name of variant used for sii files (max length 12)
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())

    def to_scs_bytes(self):
        return help_funcs.UInt64ToByts(self.__name)


class PMDVisiLink:
    def __init__(self, from_l, to_l):
        """
        from_l - number of link
        to_l - number of next link
        """
        self.__from_l = from_l
        self.__to_l = to_l

    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__from_l)
        bytes += help_funcs.UInt32ToByts(self.__to_l)
        return bytes


class PMDVisiDef:
    def __init__(self, name, num1, num2):
        """
        name - name of visibility (usually "VISIBLE")
        num1 - always zero
        num2 - for every visibility definition it's increased for 4
        """
        self.__name = help_funcs.EncodeNameCRC(name.lower())
        self.__num1 = num1
        self.__num2 = num2

    def to_scs_bytes(self):
        bytes = help_funcs.UInt64ToByts(self.__name)
        bytes += help_funcs.UInt32ToByts(self.__num1)
        bytes += help_funcs.UInt32ToByts(self.__num2)
        return bytes


class PMDVarianVisib:
    def __init__(self, sec_visi_li):
        """
        sec_visi_li - list of sections visibilities for variant
                given in array of ints eg: (1,1,0,1,0)
        """
        self.__section_li = sec_visi_li

    def set_variant_visib(self, variant_indx, value):
        self.__section_li[variant_indx] = value

    def to_scs_bytes(self):
        bytes = b''
        for i in self.__section_li:
            bytes += help_funcs.UInt32ToByts(i)
        return bytes

###############################################
#
# Main class for saving pmd file
#
###############################################
class PMDSave:
    def __init__(self, root_ob, ver):
        self.err_msg = ""
        #get sections from root object
        sec_list = [ob for ob in root_ob.children if "scs_variant_visib" in ob]

        #get looks        
        looks_li = []
        looks_dic = root_ob["scs_looks"]
        keys = sorted(looks_dic.keys(), key=lambda x: int(x))
        for look_k in keys:
            looks_li.append(PMDLook(looks_dic[look_k]))

        #get variants
        var_li = []
        var_visib_li = []
        var_dic = root_ob["scs_variants"]
        keys = sorted(var_dic.keys())
        i = 0
        for var_k in keys:
            var_li.append(PMDVariant(var_dic[var_k]))
            var_visib_li.append(PMDVarianVisib([0] * len(sec_list)))
            i += 1

        no_models = 0
        mat_dic = {}
        var_visib_links_li = []
        var_visib_defs_li = []
        i = 0
        for sec_ob in sec_list:

            var_visib_links_li.append(PMDVisiLink(i, i + 1))
            var_visib_defs_li.append(PMDVisiDef("visible", 0, i * 4))
            #go trough all models and save material name in dictionary as key
            #and object of used material as value
            mod_objs = [ob for ob in sec_ob.children if ob.type == 'MESH']
            no_models += len(mod_objs)
            for ob in mod_objs:
                if len(ob.material_slots) < len(looks_li):
                    self.err_msg = "Object '" + ob.name + "' doesn't have assigned enough materials!"
                    return
                curr_mod_mat_key = ""
                for look_indx in range(0, len(looks_li)):
                    if ob.material_slots[look_indx].material is None:
                        self.err_msg = "Object '" + ob.name + "' doesn't have assigned enough materials!"
                        return
                    curr_mod_mat_key += ob.material_slots[look_indx].material.name
                if not curr_mod_mat_key in mat_dic:
                    mat_dic[curr_mod_mat_key] = ob
                #for every variant add value in visibility array
            if not "scs_variant_visib" in sec_ob:
                self.err_msg = "Section '" + sec_ob.name + "' doesn't have defined variant visibilites!"
                return
            for var_ch in sec_ob["scs_variant_visib"]:
                curr_var_visib = var_visib_li[ord(var_ch) - ord('A')]
                curr_var_visib.set_variant_visib(i, 1)
            i += 1

        header = PMDHeader(ver, len(mat_dic), len(looks_li),
                           no_models, len(var_li), len(var_visib_defs_li))
        self.header = header
        self.__mat_dic = mat_dic
        self.looks_li = looks_li
        self.var_li = var_li
        self.__var_visib_li = var_visib_li
        self.__var_visib_defs_li = var_visib_defs_li
        self.__var_visib_links_li = var_visib_links_li
        self.mat_idx_lib = -1

    def write(self, f, exportpath, originpath, copy_tex):
        f.write(self.header.to_scs_bytes())

        self.header.looks_off = f.tell()
        for look in self.looks_li:
            f.write(look.to_scs_bytes())

        self.header.varians_off = f.tell()
        for var in self.var_li:
            f.write(var.to_scs_bytes())

        self.header.visi_links_off = f.tell()
        for visib_link in self.__var_visib_links_li:
            f.write(visib_link.to_scs_bytes())

        self.header.visi_defs_off = f.tell()
        for visib_def in self.__var_visib_defs_li:
            f.write(visib_def.to_scs_bytes())

        self.header.varians_visi_off = f.tell()
        for var_visib in self.__var_visib_li:
            f.write(var_visib.to_scs_bytes())

        i = 0
        mat_idx = 0 #material index
        mat_path = "/" + originpath + "/materials/"
        mat_block = "" #materials paths for writing to material data block
        mat_offs = [] #offsets for current look materials
        #define material library for defining mat index in pmg file
        mat_idx_lib = {}
        writen_mats = {}
        while i < len(self.looks_li):
            for m_key in self.__mat_dic.keys():
                curr_mat = self.__mat_dic[m_key].material_slots[i].material
                mat_offs.append(len(mat_block))
                mat_block += mat_path + curr_mat.name + ".mat|"
                #write material if it's not already writen
                if curr_mat.name not in writen_mats:
                    exp_mat = export_mat.MAT(exportpath, originpath, curr_mat)
                    ret_ob = exp_mat.write(copy_tex)
                    if ret_ob is not None:
                        self.err_msg = ret_ob
                        return
                    writen_mats[curr_mat.name] = True
                    #only set material indx lib for first look cuz indexes are same foo others
                if i == 0:
                    mat_idx_lib[m_key] = mat_idx
                    mat_idx += 1
            i += 1
        self.mat_idx_lib = mat_idx_lib

        self.header.mats_defs_off = f.tell()
        mat_start_off = f.tell() + len(mat_offs) * 4
        for mat_off in mat_offs:
            f.write(help_funcs.UInt32ToByts(mat_start_off + mat_off))

        self.header.mats_block_off = f.tell()
        self.header.mats_block_size = len(mat_block)

        for ch in mat_block:
            if ch == "|":
                f.write((0).to_bytes(1, 'little'))
            else:
                f.write(help_funcs.CharToByts(ord(ch)))

        f.seek(0)
        f.write(self.header.to_scs_bytes())


def save(exportpath, originpath, root_ob, copy_tex):
    with open(exportpath + '/' + originpath + '/' + root_ob.name + '.pmd', "wb") as f:
        if not "scs_looks" in root_ob or not "scs_variants" in root_ob:
            return -1, "Can't export PMD. Looks or variants are not defined!"
        t = time.clock()
        pmd = PMDSave(root_ob, 4)
        if len(pmd.err_msg) > 0:
            return -1, pmd.err_msg
        pmd.write(f, exportpath, originpath, copy_tex)
        if len(pmd.err_msg) > 0:
            return -1, pmd.err_msg

        help_funcs.PrintDeb("Exporting of PMD took:", str(time.clock() - t)[:4], "seconds")
    return 0, pmd


"""
import os
export_path = "E:"
origin_path = "EXPORT/first"
if not os.path.exists(export_path+'/'+origin_path):
    os.makedirs(export_path+'/'+origin_path)
save(export_path, origin_path, bpy.data.objects["universal"], True)
"""
