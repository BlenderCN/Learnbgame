# wahooney_uv_helper.py Copyright (C) 2009-2010, Keith "Wahooney" Boshoff
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

'''

TODO:
 * Copy vertex colours
 * Check that face counts match properly and fix/report accordingly
 * Copy UVs from original back to UV Helper (2-way communication)
 * Ignore multiple instances of same mesh
 * Remove Selected/All UV Helpers function
 * Hide/show objects properly

History:

0.4:
 * Update for Blender 2.57
 
0.3:
 * Report when face counts have changed between original and UV Helper
 
0.2:
 * Remove reliance on vertex group names, use custom object properties on uv helper
 * Copy Edge Flags from and back to original (seams, sharp, etc.)
 * Operatorify & Addonify
 * Rename UVObject to UVHelper
 * Remove meshes
 * Copy image faces back to original objects
 * Copy image faces from original when making
 
0.1:
 * Basic functionality

'''

bl_info = {
    'name': 'UV Helper',
    'author': 'Keith (Wahooney) Boshoff',
    'version': (0, 3, 0),
    'blender': (2, 5, 7),
    'category': 'UV'
}

import bpy

def make_uv_helper(self, context):

    obj = context.active_object

    selection = context.selected_objects
    
    mesh = bpy.data.meshes.new("UVHelper")
	
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
    vertices = []
    faces = []
    edges = []
    
    groups = []
    uv_faces = []
    img_faces = []
    edge_flags = []
    
    offset = 0
    e_offset = 0
    
    for sel in selection:
    
        if sel.type != 'MESH':
            continue
            
        tm = sel.matrix_world
            
        num_faces = len(sel.data.faces)
        num_verts = len(sel.data.vertices)
        num_edges = len(sel.data.edges)
        
        groups.append({'name' : sel.data.name, 'edges' : num_edges, 'faces' : num_faces})
    
        # collect face data
        for f in sel.data.faces:
            face = []
            for v in f.vertices:
                face.append(v + offset)
                
            faces.append(face)
        
        # collect vertex data
        for v in sel.data.vertices:
            vertices.append(tm * v.co)
            
        # collect edge data
        for e in sel.data.edges:
        
            # edge vertex connections
            edge = []
            
            for v in e.vertices:
                edge.append(v+offset)
        
            edges.append(edge)
            
            # store edge flags
            flags = 0
            
            if e.use_seam:
                flags = flags | 1;
                
            if e.use_edge_sharp:
                flags = flags | 2;
            
            edge_flags.append(flags)
        
        # collect uv data
        uv = sel.data.uv_textures.active
        
        # add a uv channel if one doesn't exist
        if not uv:
            uv = sel.data.uv_textures.new()
        
        for f in uv.data:
            raw = []
            for v in f.uv_raw:
                raw.append(v)

            # collect the image data
            img_faces.append(f.image)

            uv_faces.append(raw)

        # increment index offsets
        offset += num_verts
        e_offset += num_verts

        # hide completed objects
        sel.hide = True            

    # create mesh from collected data
    mesh.from_pydata(vertices, edges, faces)
    
    mesh.update();
    
    # apply uv coordinates
    uv = mesh.uv_textures.new()
    for i, f in enumerate(uv_faces):
        uv.data[i].uv_raw = f
        uv.data[i].image = img_faces[i]
        
    # apply edge flags
    for i, e in enumerate(edge_flags):
        mesh.edges[i].use_seam = e & 1;
        mesh.edges[i].use_edge_sharp = e & 2;
        
    mesh.update();
    
    # instantiate and link object
    uv_obj = bpy.data.objects.new("UVHelper", mesh)
    context.scene.objects.link(uv_obj)
    
    # store meta data
    faces = []
    edges = []
    meshes = []
    
    for g in groups:
        meshes.append(g['name'])
        faces.append(g['faces'])
        edges.append(g['edges'])
    
    # add custom properties
    uv_obj['uvhelper_faces'] = faces
    uv_obj['uvhelper_meshes'] = meshes
    uv_obj['uvhelper_edges'] = edges
    
    # deselect all objects
    for obj in context.scene.objects:
        obj.select = False
        
    # select uv helper object
    uv_obj.select = True
    context.scene.objects.active = uv_obj
        
def apply_uv_helper(self, context):

    obj = context.active_object
    
    if obj.type != 'MESH' or not "uvhelper_faces" in obj or not "uvhelper_edges" in obj or not "uvhelper_meshes" in obj:
        self.report({'ERROR'}, "No valid UV Helpers selected")
        return

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    groups = obj['uvhelper_meshes']
    uv_faces = obj['uvhelper_faces']
    uv_edges = obj['uvhelper_edges']

    if not len(groups):
        return

    helper = obj.data.uv_textures.active
    
    if not helper:
        return
        
    helper_mesh = obj.data
    helper_uv = helper.data
    idx = 0
    ed_idx = 0
    
    for i, g in enumerate(groups):
        mesh = bpy.data.meshes[g]
        
        if len(mesh.faces) != uv_faces[i]:
            self.report({'ERROR'}, "%s's face count has changed (%d > %d), please make a new UV Helper" % (g, uv_faces[i], len(mesh.faces)))
            return

        if len(mesh.edges) != uv_edges[i]:
            self.report({'ERROR'}, "%s's edge count has changed (%d > %d), please make a new UV Helper" % (g, uv_edges[i], len(mesh.edges)))
            return
        
    for i, g in enumerate(groups):
        mesh = bpy.data.meshes[g]
        
        uv = mesh.uv_textures.active
        
        if not uv:
            uv = mesh.uv_textures.new()
            
        uvs = uv.data
            
        for j, f in enumerate(uvs):
            f.uv_raw = helper_uv[idx].uv_raw
            
            # copy image face across
            f.image = helper_uv[idx].image
            
            idx += 1
            
        for j, e in enumerate(mesh.edges):
            e.use_seam = helper_mesh.edges[ed_idx].use_seam
            e.use_edge_sharp = helper_mesh.edges[ed_idx].use_edge_sharp
            ed_idx += 1
            
        mesh.update()
        
    for obj in bpy.data.objects:
        obj.hide = False
    
    '''mesh = obj.data
    context.scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)
    
    if not mesh.users:
        bpy.data.meshes.remove(mesh)'''
        
class MakeUVHelper(bpy.types.Operator):
    ''''''
    bl_idname = "object.make_uv_helper"
    bl_label = "Make UV Helper"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1

    def execute(self, context):
        make_uv_helper(self, context)
        return {'FINISHED'}

class ApplyUVHelper(bpy.types.Operator):
    ''''''
    bl_idname = "object.apply_uv_helper"
    bl_label = "Apply UV Helper"

    @classmethod
    def poll(cls, context):
        return context.active_object != None and "uvhelper_meshes" in context.active_object

    def execute(self, context):
        apply_uv_helper(self, context)
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
