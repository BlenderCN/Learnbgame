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

import bpy
from . import help_funcs
from mathutils import Vector, Quaternion


class PMCHeader:
    def __init__(self):
        self.pmc_id = 0
        self.no_looks = 0
        self.no_variants = 0
        self.no_materials = 0
        self.no_models = 0
        self.look_names_offset = 0
        self.variant_names_offset = 0
        self.materials_offset = 0
        self.model_defs_offset = 0
        self.variant_defs_offset = 0
    
    def read_header(self, f):
        self.pmc_id = help_funcs.ReadUInt32(f)
        self.no_looks = help_funcs.ReadUInt32(f)
        self.no_variants = help_funcs.ReadUInt32(f)
        self.no_materials = help_funcs.ReadUInt32(f)
        self.no_models = help_funcs.ReadUInt32(f)
        self.look_names_offset = help_funcs.ReadUInt32(f)
        self.variant_names_offset = help_funcs.ReadUInt32(f)
        self.materials_offset = help_funcs.ReadUInt32(f)
        self.model_defs_offset = help_funcs.ReadUInt32(f)
        self.variant_defs_offset = help_funcs.ReadUInt32(f)


class PMCLook:
    def __init__(self):
        self.name = 0
    def read(self,f):
        self.name = help_funcs.ReadUInt64(f)
        
        
class PMCVariant:
    def __init__(self):
        self.name = 0
    def read(self, f):
        self.name = help_funcs.ReadUInt64(f)



class PMCModel:
    """
    Class for storing geometry collision model
    """
    def __init__(self):
        self.no_faces = 0
        self.no_verts = 0
        self.verts_offset = 0
        self.faces_offset = 0
        self.verts = []
        self.faces = []
                
    def read_header(self, f):
        self.no_faces = help_funcs.ReadUInt32(f)/3
        self.no_verts = help_funcs.ReadUInt32(f)
        self.verts_offset = help_funcs.ReadUInt32(f)
        self.faces_offset = help_funcs.ReadUInt32(f)
    
    def read_verts(self, f):
        f.seek(self.verts_offset)
        i=0
        while i<self.no_verts:
            self.verts.append(help_funcs.ReadFloatVector(f))      
            i+=1
        
    def read_faces(self, f):
        f.seek(self.faces_offset)
        i=0
        while i<self.no_faces:
            self.faces.append(help_funcs.ReadUInt16Vector(f))
            i+=1


class PMCCenter:
    """
    Class for storing collision center data
    """
    def __init__(self, center=(0.0,0.0,0.0), direct=(0.0, 0.0, 0.0, 0.0)):
        self.co = center
        self.direct = direct


class PMCCollision:
    """
    Class for storing one collision definition
    Types:
        Box, Cylinder, Geometry
    """
    def __init__(self, unk3, type):
        self.unk3 = unk3
        self.type = type
        self.unk1 = 0
        self.unk2 = 0.0
        self.name = 0
        self.center = None
    
    def read_col(self, f):
        self.unk1 = help_funcs.ReadUInt32(f)
        self.unk2 = help_funcs.ReadFloat(f)
        self.name = help_funcs.ReadUInt64(f)
        self.center = PMCCenter(help_funcs.ReadFloatVector(f), help_funcs.ReadFloatQuaternion(f))
        if self.type == 56: #geometry
            self.model_no = help_funcs.ReadUInt32(f)
        elif self.type == 60: #cylinder
            self.radius = help_funcs.ReadFloat(f)
            self.depth = help_funcs.ReadFloat(f)
        elif self.type == 64: #box
            self.scale = help_funcs.ReadFloatVector(f)
        

class PMCVariCollision:
    """
    Class for storing variant collision definitions
    """
    def __init__(self):
        self.offset = 0
        self.collisions = []
        
    def read_header(self, f):
        self.offset = help_funcs.ReadUInt32(f)
        
    def read_collisions_def(self, f):
        f.seek(self.offset)
        unk3 = help_funcs.ReadInt32(f)
        type = help_funcs.ReadInt32(f)
        self.collisions.clear()
        while unk3 != 6 and type != -1:
            col = PMCCollision(unk3, type)
            col.read_col(f)
            self.collisions.append(col)
            unk3 = help_funcs.ReadInt32(f)
            type = help_funcs.ReadInt32(f)
        
        
class PMC:
    """
    Class for storing whole PMC data
    """
    def __init__(self, f):
        self.header = PMCHeader()
        self.header.read_header(f)
        self.looks = self.__read_looks(f)
        self.variants = self.__read_variants(f)
        self.material_looks = self.__read_mat_looks(f)
        self.models = self.__read_models(f)
        self.variant_cols = self.__read_variant_cols(f)
        
    def __read_looks(self, f):
        help_funcs.PrintDeb("Loading looks...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_looks:
            curr_l = PMCLook()
            curr_l.read(f)
            ret.append(curr_l)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/",
                self.header.look_names_offset+self.header.no_looks*8);
        return ret
            
    def __read_variants(self, f):
        help_funcs.PrintDeb("Loading variants...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_variants:
            curr_v = PMCVariant()
            curr_v.read(f)
            ret.append(curr_v)
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/",
                self.header.variant_names_offset+self.header.no_variants*8);
        return ret
        
    def __read_mat_looks(self, f):
        help_funcs.PrintDeb("Loading material looks...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_looks*self.header.no_materials:
            ret.append(help_funcs.ReadUInt32(f))
            i+=1
            
        help_funcs.PrintDeb("Done!\nFile pos:", f.tell(), "/",
                self.header.materials_offset+self.header.no_materials*self.header.no_looks*4);
        return ret
    
    def __read_models(self, f):
        help_funcs.PrintDeb("Loading models...", end=" -> ");
        i=0
        ret = []
        while i < self.header.no_models:
            curr_m = PMCModel()
            curr_m.read_header(f)
            ret.append(curr_m)
            i+=1
            
        i=0
        while i< self.header.no_models:
            ret[i].read_verts(f)
            ret[i].read_faces(f)
            i+=1
            
        help_funcs.PrintDeb("Done!");
        return ret
        
    def __read_variant_cols(self, f):
        help_funcs.PrintDeb("Loading varaint collisions...", end=" -> ");
        f.seek(self.header.variant_defs_offset)
        i=0
        ret = []
        while i < self.header.no_variants:
            curr_v = PMCVariCollision()
            curr_v.read_header(f)
            ret.append(curr_v)
            i+=1
            
        i=0
        while i < self.header.no_variants:
            ret[i].read_collisions_def(f)
            i+=1    
        
        help_funcs.PrintDeb("Done!");
        return ret
    
    def draw_collisions(self, parent_ob):
        bpy.ops.object.empty_add(type='CUBE',location=Vector())
        pmc_ob = bpy.context.active_object
        pmc_ob.name = 'collisions'
        pmc_ob.parent = parent_ob
        pmc_ob.empty_draw_size = 0.1
        
        ob_col_vars = {}
        var_no="A"
        i=0
        while i < self.header.no_variants:
            for col in self.variant_cols[i].collisions:
                #converts verts coordinates and rotation 
                #to blender coordinate system
                cc = col.center
                loc = Vector((-cc.co[0], cc.co[1], -cc.co[2]))
                rot = Quaternion((cc.direct[0], -cc.direct[1], cc.direct[2], -cc.direct[3]))
                name = help_funcs.DecodeNameCRC(col.name)
                #collision object not yet created
                if not name in bpy.data.objects:
                    ob_col_vars[name] = ""
                    if col.type == 60: #cylinder
                        ob = draw_cylinder(loc, rot, col.depth,
                                col.radius, name, pmc_ob)
                    elif col.type == 64: #box
                        ob = draw_box(loc, rot, col.scale, 
                                name, pmc_ob)
                    elif col.type == 56: #geometry
                        verts = self.models[col.model_no].verts
                        j=0
                        while j<len(verts):
                            #converts verts coordinates to blender coordinate system
                            verts[j] = (-verts[j][0], verts[j][1], -verts[j][2])
                            j+=1
                        faces = self.models[col.model_no].faces
                        ob = draw_geometry(loc, rot, verts, faces,
                                name, pmc_ob)
                else:
                    ob = bpy.data.objects[name]
                #add variant name
                ob_col_vars[name] += var_no
                
            i+=1    
            var_no=chr(ord(var_no)+1)
            
        for ob in pmc_ob.children:
            ob["scs_variant_visib"] = ob_col_vars[ob.name]
       
        
def draw_cylinder(loc, rot, depth, radius, name, parent_ob):
    bpy.ops.mesh.primitive_cylinder_add(vertices=26,
            location=loc, radius=1, depth=1)
    ob = bpy.context.active_object
    ob.parent = parent_ob
    ob.name = name
    ob.scale.x=radius
    ob.scale.y=radius
    ob.scale.z=depth
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = rot
    ob.draw_type = 'WIRE'
    ob["scs_variant_visib"] = ""
    ob["scs_coll_init"] = True
    ob.scs_coll_type="cylinder"
    return ob
    
def draw_box(loc, rot, scale, name, parent_ob):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    ob = bpy.context.active_object
    ob.scale = Vector((0.5,0.5,0.5))
    bpy.ops.object.transform_apply(scale=True)
    ob.parent = parent_ob
    ob.name = name
    ob.scale = scale
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = rot
    ob.draw_type = 'WIRE'
    ob["scs_variant_visib"] = ""
    ob["scs_coll_init"] = True
    ob.scs_coll_type="box"
    return ob
    
def draw_geometry(loc, rot, verts, faces, name, parent_ob):
    me = bpy.data.meshes.new("Mesh"+name)
    ob = bpy.data.objects.new(name, me)     
    bpy.context.scene.objects.link(ob)
    ob.location = loc
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = rot
    ob.parent = parent_ob
    me.from_pydata(verts, [], faces[::-1])
    me.update()
    ob.draw_type = 'WIRE'
    ob["scs_variant_visib"] = ""
    ob["scs_coll_init"] = True
    ob.scs_coll_type="geometry"
    return ob
        
def load(filepath):
    help_funcs.PrintDeb("\nImporting PMC -----------------\n")
    with open(filepath, 'rb') as f:
        if help_funcs.ReadUInt32(f) != 6:
            return None
        f.seek(0)
        pmc = PMC(f)
    return pmc