
from . import m2_format
from .m2_format import *

#from . import BSP_Tree
#from .BSP_Tree import *

#from . import Collision
#from .Collision import *

import bpy
import math
from math import *
import bmesh
from mathutils import Vector
import os

class M2File:
    def __init__(self):
        self.header = M2Header()

    def read(self, f):        
        self.header.read(f) 
    
    def loadMaterials(self, name):
        self.materials = {}

        images = []
        imageNames = []

        # Add ghost material
        mat = bpy.data.materials.get("WowMaterial_ghost")
        if not mat:
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
            mat.WowMaterial.BlendingMode = str(self.momt.Materials[i].BlendMode)
            mat.WowMaterial.Texture1 = self.motx.GetString(self.momt.Materials[i].Texture1Ofs)
            mat.WowMaterial.Color1 = [x / 255 for x in self.momt.Materials[i].Color1[0:3]]
            mat.WowMaterial.Flags1 = '1' if self.momt.Materials[i].TextureFlags1 & 0x80 else '0'
            mat.WowMaterial.Texture2 = self.motx.GetString(self.momt.Materials[i].Texture2Ofs)
            mat.WowMaterial.Color2 = [x / 255 for x in self.momt.Materials[i].Color2[0:3]]
            mat.WowMaterial.TerrainType = str(self.momt.Materials[i].TerrainType)
            mat.WowMaterial.Texture3 = self.motx.GetString(self.momt.Materials[i].Texture3Ofs)
            mat.WowMaterial.Color3 = [x / 255 for x in self.momt.Materials[i].Color3[0:3]]
            mat.WowMaterial.Flags3 = '0' #1' if momt.Materials[i].TextureFlags1 & 0x80 else '0'

            if self.momt.Materials[i].Flags1 & 0x4:
                mat.WowMaterial.TwoSided = True
            if self.momt.Materials[i].Flags1 & 0x8:
                mat.WowMaterial.Darkened = True
            if self.momt.Materials[i].Flags1 & 0x10:
                mat.WowMaterial.NightGlow = True

            # set texture slot and load texture
            
            if mat.WowMaterial.Texture1:
                tex1_slot = mat.texture_slots.create(2)
                tex1_slot.uv_layer = "UVMap"
                tex1_slot.texture_coords = 'UV'

                tex1_name = material_name + "_Tex_01"
                tex1 = bpy.data.textures.new(tex1_name, 'IMAGE')
                tex1_slot.texture = tex1

                try:
                    tex1_img_filename = os.path.splitext( mat.WowMaterial.Texture1 )[0] + file_format

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
                    tex2_img_filename = os.path.splitext( mat.WowMaterial.Texture2 )[0] + file_format
                    
                    img2_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex2_img_filename):
                            tex2.image = images[iImg]
                            img2_loaded = True
                            break

                    # if image is not loaded, do it
                    if img2_loaded == False:
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
                    tex3_img_filename = os.path.splitext( mat.WowMaterial.Texture2 )[0] + file_format
                    
                    img3_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if imageNames[iImg] == tex3_img_filename:
                            tex3.image = images[iImg]
                            img3_loaded = True
                            break

                    # if image is not loaded, do it
                    if img3_loaded == False:
                        tex3_img = bpy.data.images.load(texturePath + tex3_img_filename)
                        tex3.image = tex3_img
                        images.append(tex3_img)
                        imageNames.append(tex3_img_filename)
                except:
                    pass
    
    def save(self, obj):
        bpy.context.scene.objects.active = obj
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.objects.active = new_obj
        
        mesh = new_obj.data
        original_mesh = obj.data
class M2SkinFile:
    def __init__(self):
        self.skin = M2SkinProfile()

    def read(self, f):        
        self.skin.read(f)

    def draw_submesh(self, m2_file):
        # Create the blender armature and object
        mesh_name = "model"
        armature = bpy.data.armatures.new('%s_Armature' % mesh_name)
        rig = bpy.data.objects.new(mesh_name, armature)
        rig.location = (0, 0, 0)
        #rig.show_x_ray = self.enable_armature_xray
        #armature.show_names = self.display_bone_names

        # Link the object to the scene
        scene = bpy.context.scene
        scene.objects.link(rig)
        scene.objects.active = rig
        scene.update()
        
        bpy.ops.object.mode_set(mode='OBJECT')
        for submesh_index, submesh in enumerate(self.skin.submeshes):
            #print("  Creation of the submesh '%s'..." % submesh.name)

            # Create the blender mesh and object                    
            
            mesh = bpy.data.meshes.new('Mesh_' + str(submesh_index))
            obj = bpy.data.objects.new(str(submesh_index), mesh)
            obj.location = (0, 0, 0)

            # Link the object to the scene
            scene.objects.link(obj)
            scene.objects.active = obj
            scene.update()

            # Retrieve the triangles of the submesh
            print("    - %s triangles, from %d" % (submesh.nTriangles, submesh.StartTriangle))
            submesh_triangles = self.skin.triangles[submesh.StartTriangle:submesh.StartTriangle+submesh.nTriangles]

            # Retrieve the indices of the submesh
            print("    - %s indices, from %d" % (submesh.nVertices, submesh.StartVertex))
            submesh_indices = self.skin.indices[submesh.StartVertex:submesh.StartVertex+submesh.nVertices]

            # Retrieve the list of vertex coordinates
            submesh_vertices = [ m2_file.header.vertices[index] for index in submesh_indices ]
            verts = [ vertex.pos.to_tuple() for vertex in submesh_vertices ]

            # Retrieve the list of faces
            faces = list(map(lambda x: x.to_tuple(offset=submesh.StartVertex), submesh_triangles))

            # Create the mesh
            mesh.from_pydata(verts, [], faces)

            # Update the mesh with the new data
            mesh.update(calc_edges=True)

            # Normals
            for n, vertex in enumerate(mesh.vertices):
                vertex.normal = submesh_vertices[n].normal
            
            uv1 = mesh.uv_textures.new("UVMap")
            uv_layer1 = mesh.uv_layers[0]
            for i in range(len(uv_layer1.data)):
                uv = submesh_vertices[mesh.loops[i].vertex_index].tex_coords
                uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
            uv1.active = True
            
            bones = []
            bone_groups = {}
            submesh_bone_table = m2_file.header.bone_lookup_table[submesh.StartBones:submesh.StartBones+submesh.nBones]
            for bone_index in submesh_bone_table:
                bones.insert(bone_index, m2_file.header.bones[bone_index])
                bone_groups[bone_index] = []
                        
            for vertex_index, vertex in enumerate(submesh_vertices):
                for n, bone_index in enumerate(vertex.bone_indices):
                    if bone_index > 0:
                        bone_groups[bone_index].append((vertex_index, vertex.bone_weights[n] / 255))

            for bone_index in bone_groups.keys():
                grp = obj.vertex_groups.new(str(bone_index))
                for (v, w) in bone_groups[bone_index]:
                    grp.add([v], w, 'REPLACE')                    