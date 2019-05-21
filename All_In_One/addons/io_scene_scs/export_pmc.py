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


class PMCHeader:
    def __init__(self, ver, no_looks, no_variants, no_mats, no_col_models):
        """
        ver - version of pmc file
        no_looks - number of looks
        no_variants - number of variants
        no_mats - number of different materials in whole pmg model
        no_col_models - number of geometry model in pmc
        """
        self.__ver = ver
        self.__no_looks = no_looks
        self.__no_variants = no_variants
        self.__no_mats = no_mats
        self.__no_col_models = no_col_models
        self.look_names_off = 0
        self.variant_names_off = 0
        self.looks_off = 0
        self.col_models_off = 0
        self.variant_col_off = 0
        
    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__ver)
        bytes += help_funcs.UInt32ToByts(self.__no_looks)
        bytes += help_funcs.UInt32ToByts(self.__no_variants)
        bytes += help_funcs.UInt32ToByts(self.__no_mats)
        bytes += help_funcs.UInt32ToByts(self.__no_col_models)
        bytes += help_funcs.UInt32ToByts(self.look_names_off)
        bytes += help_funcs.UInt32ToByts(self.variant_names_off)
        bytes += help_funcs.UInt32ToByts(self.looks_off)
        bytes += help_funcs.UInt32ToByts(self.col_models_off)
        bytes += help_funcs.UInt32ToByts(self.variant_col_off)
        return bytes
        
        
class PMCLook:
    def __init__(self, name):
        self.__name = name
    def to_scs_bytes(self):
        return help_funcs.UInt64ToByts(self.__name)
        
        
class PMCVariant:
    def __init__(self, name):
        self.__name = name
    def to_scs_bytes(self):
        return help_funcs.UInt64ToByts(self.__name)
    
class PMCModel:
    """
    Class for storing geometry collision model
    no_faces - number of faces in model
    no_verts - number of vertices in model
    verts - list of float vector tuples [(x,y,z),(x,y,z),...]
    faces - list of int vector tuples [(v1,v2,v3),(v4,v5,v6),...]
    """
    def __init__(self, name, no_faces, no_verts, verts, faces):
        self.name = name
        self.__no_faces = no_faces*3
        self.__no_verts = no_verts
        self.verts_off = 0
        self.faces_off = 0
        self.verts = verts
        self.faces = faces
    
    
    def to_scs_bytes(self, type):
        """
        type - 0 > return definitions bytes
               1 > return vertex bytes
               2 > return faces bytes
        """
        bytes = b""
        if type == 0:
            bytes += help_funcs.UInt32ToByts(self.__no_faces)
            bytes += help_funcs.UInt32ToByts(self.__no_verts)
            bytes += help_funcs.UInt32ToByts(self.verts_off)
            bytes += help_funcs.UInt32ToByts(self.faces_off)
        elif type == 1:
            for vertex in self.verts:
                bytes += help_funcs.FloatVecToByts(vertex)
        elif type == 2:
            for face in self.faces:
                bytes += help_funcs.UInt16VecToByts(face)
        return bytes
    
class PMCCenter:
    """
    Class for storing collision center data
    center - center of collision object (0,0,0)
    rot - rotation of collision object in quaternions (0,0,0,0)
    """
    def __init__(self, center, rot):
        self.__co = center
        self.__rot = rot
    
    def to_scs_bytes(self):
        bytes = help_funcs.FloatVecToByts(self.__co)
        bytes += help_funcs.FloatQuatToByts(self.__rot)
        return bytes


class PMCCollision:
    """
    Class for storing one collision definition
    unk3 -  1 for box, 3 for cylinder, 8 for geometry
    type - 64 for box, 60 for cylinder, 56 for geometry
    name - name of collision object (max. length 12)
    center - PMCCenter object which tells where is center of model
    coll_data - for box (sizex, sizey, sizez), for cylinder (radius, height),
                for geometry (model_index)
    """
    def __init__(self, unk3, type, name, center, coll_data):
        self.__unk3 = unk3
        self.__type = type
        self.__unk1 = 0 #should be 0
        self.__unk2 = 1.0 #should be 1. -> 00 00 80 3F
        self.__name = help_funcs.EncodeNameCRC(name.lower())
        self.__center = center
        self.__coll_data = coll_data
    
    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__unk3)
        bytes += help_funcs.UInt32ToByts(self.__type)
        bytes += help_funcs.UInt32ToByts(self.__unk1)
        bytes += help_funcs.FloatToByts(self.__unk2)
        bytes += help_funcs.UInt64ToByts(self.__name)
        bytes += self.__center.to_scs_bytes()
        data_len = len(self.__coll_data)
        if data_len == 1: #geometry
            bytes += help_funcs.UInt32ToByts(self.__coll_data[0])
        elif data_len == 2 or data_len == 3: #box, cylinder
            for param in self.__coll_data:
                bytes += help_funcs.FloatToByts(param)
        return bytes
    
        
        

class PMCVariCollDef:
    """
    Class for storing variant collision offset
    """
    def __init__(self, offset):
        self.offset = offset
    
    def to_scs_bytes(self):
        return help_funcs.UInt32ToByts(self.offset)
    
            
class PMCSave:
    def __init__(self, col_root, pmd, ver):
        col_models = [ob for ob in col_root.children if ob.scs_coll_type == 'geometry']
        self.header = PMCHeader(ver, pmd.header.no_looks, pmd.header.no_varians,
                                pmd.header.no_mats, len(col_models))
        self.looks_names = pmd.looks_li
        self.var_names = pmd.var_li
        #block of zeros
        self.looks_block = [0]*pmd.header.no_looks*pmd.header.no_mats
        #read collision models
        self.col_models = []
        for col_ob in col_models:
            m_verts = {}
            m_faces = []
            for p in col_ob.data.polygons:
                vert_li = [] #used for faces connections
                for idx in p.loop_indices:
                    v = col_ob.data.loops[idx].vertex_index
                    if not v in m_verts:
                        vert_co = col_ob.data.vertices[v].co
                        m_verts[v] = (vert_co[0], vert_co[1], -vert_co[2])
                    vert_li.append(v)
                m_faces.append(vert_li[::-1])
            verts_li = []
            for vert_k in sorted(m_verts.keys()):
                verts_li.append(m_verts[vert_k])
            self.col_models.append(PMCModel(col_ob.name, len(m_faces),
                                            len(verts_li), verts_li, m_faces))
        self.var_col_defs = []
        for var in self.var_names:
            self.var_col_defs.append(PMCVariCollDef(0))
        
    def write(self, f, col_root):
        #write header
        f.write(self.header.to_scs_bytes())
        #write looks names
        self.header.look_names_off = f.tell()
        for look in self.looks_names:
            f.write(look.to_scs_bytes())
        #write variants names
        self.header.variant_names_off = f.tell()
        for var in self.var_names:
            f.write(var.to_scs_bytes())
        #write 0 looks block
        self.header.looks_off = f.tell()
        for look in self.looks_block:
            f.write(help_funcs.UInt32ToByts(look))
        #write collision geometry models definitions
        self.header.col_models_off = f.tell()
        for col_m in self.col_models:
            f.write(col_m.to_scs_bytes(0))
        #write offsets to variant collision definitions
        self.header.variant_col_off = f.tell()
        for var in self.var_col_defs:
            f.write(var.to_scs_bytes())
        #write actual models geometries vertices and faces
        for col_m in self.col_models:
            col_m.verts_off = f.tell()
            f.write(col_m.to_scs_bytes(1))
            col_m.faces_off = f.tell()
            f.write(col_m.to_scs_bytes(2))
        #write actual collision definition data block
        i=0
        while i<len(self.var_col_defs):
            self.var_col_defs[i].offset = f.tell()
            var_ch = chr(ord('A')+i)
            #get all objects for current variant and write it's definitions
            var_objs = [ob for ob in col_root.children if "scs_variant_visib" in ob and ob["scs_variant_visib"].count(var_ch) == 1]
            for var_ob in var_objs:
                if var_ob.scs_coll_type == 'box':
                    unk3 = 1
                    type = 64
                    coll_data = tuple(var_ob.scale)
                elif var_ob.scs_coll_type == 'cylinder':
                    unk3 = 3
                    type = 60
                    coll_data = ((var_ob.scale.x+var_ob.scale.y)/2,
                                 var_ob.scale.z)
                elif var_ob.scs_coll_type == 'geometry':
                    unk3 = 8
                    type = 56
                    indx = 0
                    #get index of writen collision model
                    for col_model in self.col_models:
                        if col_model.name == var_ob.name:
                            break
                        indx+=1 
                    coll_data = (indx,)
                #to convert blender coordinate system to scs
                cent_loc = (var_ob.location[0], var_ob.location[1], -var_ob.location[2])
                center = PMCCenter(cent_loc, tuple(var_ob.rotation_quaternion))
                curr_col = PMCCollision(unk3, type, var_ob.name, center, coll_data)
                f.write(curr_col.to_scs_bytes())
            f.write(help_funcs.UInt32ToByts(6))
            f.write(help_funcs.Int32ToByts(-1))
            i+=1
            
        #rewrite header, collision models definitions, variant collisions definitions
        f.seek(0)
        f.write(self.header.to_scs_bytes())
        
        f.seek(self.header.col_models_off)
        for col_m in self.col_models:
            f.write(col_m.to_scs_bytes(0))
        
        f.seek(self.header.variant_col_off)
        for var in self.var_col_defs:
            f.write(var.to_scs_bytes())
            
def save(filename, col_root, pmd):
    with open(filename, "wb") as f:
        pmc = PMCSave(col_root, pmd, 6)
        pmc.write(f, col_root)
