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

from . import help_funcs

class PMDHeader:
    def __init__(self):
        self.id = 0
        self.no_materials = 0
        self.no_looks = 0
        self.no_parts = 0
        self.no_variants = 0
        self.no_visib_links = 0
        self.no_visib_defs = 0
        self.no_variants_visib = 0
        self.mat_block_size = 0
        self.looks_offset = 0
        self.variants_offset = 0
        self.visib_links_offset = 0
        self.variants_visib_offset = 0
        self.visib_defs_offset = 0
        self.mat_offs_offset = 0
        self.mat_block_offset = 0
        
    def read_header(self,f):
        self.id = help_funcs.ReadUInt32(f)
        self.no_materials = help_funcs.ReadUInt32(f)
        self.no_looks = help_funcs.ReadUInt32(f)
        self.no_parts = help_funcs.ReadUInt32(f)
        self.no_variants = help_funcs.ReadUInt32(f)
        self.no_visib_links = help_funcs.ReadUInt32(f)
        self.no_visib_defs = help_funcs.ReadUInt32(f)
        self.no_variants_visib = help_funcs.ReadUInt32(f)
        self.mat_block_size = help_funcs.ReadUInt32(f)
        self.looks_offset = help_funcs.ReadUInt32(f)
        self.variants_offset = help_funcs.ReadUInt32(f)
        self.visib_links_offset = help_funcs.ReadUInt32(f)
        self.variants_visib_offset = help_funcs.ReadUInt32(f)
        self.visib_defs_offset = help_funcs.ReadUInt32(f)
        self.mat_offs_offset = help_funcs.ReadUInt32(f)
        self.mat_block_offset = help_funcs.ReadUInt32(f)

class PMDLook:
    def __init__(self):
        self.name = 0
    def read(self,f):
        self.name = help_funcs.ReadUInt64(f)
        
class PMDVariant:
    def __init__(self):
        self.name = 0
    def read(self, f):
        self.name = help_funcs.ReadUInt64(f)

class PMDVisibLink:
    """
    Class for storing visibility definitions chain link
    """
    def __init__(self):
        self.from_link = 0   
        self.to_link = 0
    def read(self, f):
        self.from_link = help_funcs.ReadUInt32(f)
        self.to_link = help_funcs.ReadUInt32(f)

class PMDVisibDef:
    """
    Class for storing visibility definitin data
    """
    def __init__(self):
        self.name = 0
        self.num1 = 0
        self.num2 = 0
    def read(self, f):
        self.name = help_funcs.ReadUInt64(f)
        self.num1 = help_funcs.ReadUInt32(f)
        self.num2 = help_funcs.ReadUInt32(f)

class PMDVariantVisib:
    """
    Class for storing list of visible sections in current variant
    """
    def __init__(self):
        self.visib_list=[]
    def read(self, f, no_visib):
        self.visib_list.clear()
        i=0
        while i<no_visib:
            self.visib_list.append(help_funcs.ReadUInt32(f))
            i+=1

class PMDMaterials:
    """
    Class for storing offsets to materials and paths of materials
    """
    def __init__(self):
        self.offsets=[]
        self.mat_paths=[]
    def read_offsets(self, f, no_mats, no_looks):
        self.offsets.clear()
        i=0
        while i < no_mats*no_looks:
            self.offsets.append(help_funcs.ReadUInt32(f))
            i+=1
    def read_materials(self, f):
        if len(self.offsets) == 0:
            return
        self.mat_paths.clear()
        for offset in self.offsets:
            f.seek(offset)
            val=help_funcs.ReadChar(f)
            mat = ""
            while val!=0:
                mat += chr(val)
                val=help_funcs.ReadChar(f)
            self.mat_paths.append(mat)

    
class PMD:
    """
    Class for storing all pmd data
    """
    def __init__(self,f):
        self.header=PMDHeader()
        self.header.read_header(f)
        self.looks = self.__read_looks(f)
        self.variants = self.__read_variants(f)
        self.visib_links = self.__read_visib_links(f)
        self.visib_defs = self.__read_visib_defs(f)   
        self.visib_variants = self.__read_visib_variants(f)
        self.materials = self.__read_materials(f)
    
    def __read_looks(self, f):
        help_funcs.PrintDeb("Loading looks...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_looks:
            curr_l = PMDLook()
            curr_l.read(f)
            ret.append(curr_l)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.looks_offset+self.header.no_looks*8);
        return ret
            
    def __read_variants(self, f):
        help_funcs.PrintDeb("Loading variants...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_variants:
            curr_v = PMDVariant()
            curr_v.read(f)
            ret.append(curr_v)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.variants_offset+self.header.no_variants*8);
        return ret
    
    def __read_visib_links(self, f):
        help_funcs.PrintDeb("Loading visibility links...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_visib_links:
            curr_vl = PMDVisibLink()
            curr_vl.read(f)
            ret.append(curr_vl)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.visib_links_offset+self.header.no_visib_links*8);
        return ret
    
    def __read_visib_defs(self, f):
        help_funcs.PrintDeb("Loading visibility defs...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_visib_defs:
            curr_vd = PMDVisibDef()
            curr_vd.read(f)
            ret.append(curr_vd)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.visib_defs_offset+self.header.no_visib_defs*16);
        return ret
    
    def __read_visib_variants(self, f):
        help_funcs.PrintDeb("Loading variants visibility...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_variants:
            curr_vd = PMDVariantVisib()
            curr_vd.read(f, self.header.no_visib_defs)
            ret.append(curr_vd)
            i+=1
         
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.variants_visib_offset+self.header.no_variants*self.header.no_visib_defs*4);
        return ret
    def __read_materials(self, f):
        help_funcs.PrintDeb("Loading materials...", end=" -> ");
        mats = PMDMaterials()
        mats.read_offsets(f, self.header.no_materials, self.header.no_looks)
        mats.read_materials(f)
        
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/", self.header.mat_block_offset+self.header.mat_block_size);
        return mats
    
def load(filepath):
    help_funcs.PrintDeb("\nImporting PMD -----------------\n")
    with open(filepath, 'rb') as f:
        if help_funcs.ReadUInt32(f) != 4:
            return None
        f.seek(0)
        pmd = PMD(f)
    
    return pmd