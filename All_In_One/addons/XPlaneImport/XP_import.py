#---------------------------------------------------------------------------
#
#  Import an X-Plane .obj file into Blender 2.78
#
# Dave Prue <dave.prue@lahar.net>
#
# MIT License
#
# Copyright (c) 2017 David C. Prue
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#---------------------------------------------------------------------------	

import bpy
import bmesh
import mathutils
from mathutils import Vector
import itertools
import os

class XPlaneImport(bpy.types.Operator):
    bl_label = "Import X-Plane OBJ"
    bl_idname = "import.xplane_obj"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        print("execute %s" % self.filepath)
        self.run((0,0,0))
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def createMeshFromData(self, name, origin, verts, faces, material, vert_uvs, vert_normals):
        # Create mesh and object
        me = bpy.data.meshes.new(name+'Mesh')
        ob = bpy.data.objects.new(name, me)
        ob.location = origin
        ob.show_name = False

        # Link object to scene and make active
        scn = bpy.context.scene
        scn.objects.link(ob)
        scn.objects.active = ob
        ob.select = True
        
        # Create mesh from given verts, faces.
        me.from_pydata(verts, [], faces)

        # Assign the Material to the object
        me.materials.append(material)

        # Assign the UV coordinates to each vertex
        me.uv_textures.new(name="UVMap")
        me.uv_layers[-1].data.foreach_set("uv", [uv for pair in [vert_uvs[l.vertex_index] for l in me.loops] for uv in pair])

        # Assign the normals for each vertex
        vindex = 0
        for vertex in me.vertices:
            vertex.normal = vert_normals[vindex]
            vindex += 1

        # Update mesh with new data
        me.calc_normals()
        me.update(calc_edges=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        ob.select = False

        return ob
        
        
    def run(self, origo):
        # parse file
        f = open(self.filepath, 'r')
        lines = f.readlines()
        f.close()
        
        verts = []
        uv = []
        faces = []
        normals = []
        removed_faces_regions = []
        origin_temp = Vector( ( 0, 0, 0 ) )
        anim_nesting = 0
        a_trans = [ origin_temp ]
        trans_available = False;
        objects = []
        for lineStr in lines:
            line = lineStr.split()
            if (len(line) == 0):
                continue
            
            if(line[0] == 'TEXTURE'):
                texfilename = line[1]

                # Create and add a material
                material = bpy.data.materials.new('Material')

                # Create texture
                tex = bpy.data.textures.new('Texture', type = 'IMAGE')
                tex.image = bpy.data.images.load("%s\\%s" % (os.path.dirname(self.filepath), texfilename))
                tex.use_alpha = True

                # Add Texture to the Material
                mtex = material.texture_slots.add()
                mtex.texture = tex
                mtex.texture_coords = 'UV'


            if(line[0] == 'VT'):
                vx = float(line[1])
                vy = float(line[3]) * -1
                vz = float(line[2])
                verts.append((vx, vy, vz))
            
                vnx = float(line[4])
                vny = float(line[6]) * -1
                vnz = float(line[5])
                normals.append((vnx, vny, vnz))

                uvx = float(line[7])
                uvy = float(line[8])
                uv.append((uvx, uvy))

            if(line[0] == 'IDX10' or line[0] == 'IDX'):
                faces.extend(map(int, line[1:]))
                
            if(line[0] == 'ANIM_begin'):
                anim_nesting += 1
                a_trans.append(Vector((0,0,0)))
                
            if(line[0] == 'ANIM_trans'):
                trans_x = float(line[1])
                trans_y = (float(line[3]) * -1)
                trans_z = float(line[2])
                o_t = Vector( (trans_x, trans_y, trans_z) )
                a_trans[anim_nesting] = o_t
                origin_temp = origin_temp + o_t
                trans_available = True
            
            if(line[0] == 'ANIM_end'):
                anim_nesting -= 1
                origin_temp = origin_temp - a_trans.pop()
                if(anim_nesting == 0):
                    trans_available = False
                
            if(line[0] == 'TRIS'):
                obj_origin = Vector( origo )
                tris_offset, tris_count = int(line[1]), int(line[2])
                obj_lst = faces[tris_offset:tris_offset+tris_count]
                if(trans_available):
                    obj_origin = origin_temp
                objects.append( (obj_origin, obj_lst) )
        
        counter = 0
        for orig, obj in objects:
            obj_tmp = tuple( zip(*[iter(obj)]*3) )
            self.createMeshFromData('OBJ%d' % counter, orig, verts, obj_tmp, material, uv, normals)
            counter+=1
        
        return
        

