
from . import wmo_format
from .wmo_format import *

from . import BSP_Tree
from .BSP_Tree import *

from . import Collision
from .Collision import *

import math
from math import *

#from . import Utility
#from .Utility import *

class WMO_group_file:
    def __init__(self):
        pass

    def Read(self, f):
        self.filename = f.name

        # read version header
        self.mver = MVER_chunk()
        self.mver.Read(f)

        # read file header
        self.mogp = MOGP_chunk()
        self.mogp.Read(f)
    
        # read materials
        self.mopy = MOPY_chunk()
        self.mopy.Read(f)

        # read indices
        self.movi = MOVI_chunk()
        self.movi.Read(f)

        # read vertices
        self.movt = MOVT_chunk()
        self.movt.Read(f)

        # read normals
        self.monr = MONR_chunk()
        self.monr.Read(f)

        # read texcoords
        self.motv = MOTV_chunk()
        self.motv.Read(f)

        # read batches
        self.moba = MOBA_chunk()
        self.moba.Read(f)
    
        # read lights
        if(self.mogp.Flags & MOGP_FLAG.HasLight):
            self.molr = MOLR_chunk()
            self.molr.Read(f)
    
        # read doodads
        if(self.mogp.Flags & MOGP_FLAG.HasDoodads):
            self.modr = MODR_chunk()
            self.modr.Read(f)
    
        # read collision faces
        if(self.mogp.Flags & MOGP_FLAG.HasCollision):
            self.mobn = MOBN_chunk()
            self.mobn.Read(f)
            self.mobr = MOBR_chunk()
            self.mobr.Read(f)
    
        # read vertex colors
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            self.mocv = MOCV_chunk()
            self.mocv.Read(f)

        # read liquids
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            self.mliq = MLIQ_chunk()
            self.mliq.Read(f)

    def CreateMeshFromBatch(self, meshName, batch, materials):
        # create mesh vertices / faces
        vertices = self.movt.Vertices[batch.StartVertex : batch.LastVertex + 1]
        indices = []
        
        # triangles are indices actually trueNTriangle = nTriangle // 3
        for i in range(batch.StartTriangle, batch.StartTriangle + batch.nTriangle):
            indices.append(self.movi.Indices[i] - batch.StartVertex)
          
        faces = []
        for i in range(0, len(indices), 3):
            faces.append(indices[i : i + 3])

        mesh = bpy.data.meshes.new(meshName)
        mesh.from_pydata(vertices, [], faces)
        
        # set vertex normals
        for i in range(len(mesh.vertices)):
            mesh.vertices[i].normal = self.monr.Normals[i + batch.StartVertex]
            
        # set vertex color
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            vertColor_layer1 = mesh.vertex_colors.new("vertCol_layer1")
            for i in range(len(mesh.loops)):
                vertColor_layer1.data[i].color = self.mocv.Colors[mesh.loops[i].vertex_index + batch.StartVertex][:3]
                
        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            uv = self.motv.TexCoords[mesh.loops[i].vertex_index + batch.StartVertex]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
        # set material
        mesh.materials.append(materials[batch.MaterialID])

        # set displayed texture
        uv1.active = True

        return mesh

    def GetMaterialViewportImage(self, material):
        for i in range(3):
            try:
                img = material.texture_slots[3 - i].texture.image
                return img
            except:
                pass
        return None
    
    # return array of vertice and array of faces in a tuple
    def LoadLiquids(self):
        # load vertices
        vertices = []
        for y in range(self.mliq.yVerts):
            y_pos = self.mliq.Position[1] + y * 4.1666625
            for x in range(self.mliq.xVerts):
                x_pos = self.mliq.Position[0] + x * 4.1666625
                vertices.append((x_pos, y_pos, self.mliq.HeightMap[y * self.mliq.xVerts + x][0] + self.mliq.Position[2]))
                # second float seems to be VERY low (e.g -3.271161e+35), or NAN or whatever when vertice is shown (or maybe it indicate a volume?)
                #vertices.append((x_pos, y_pos, self.mliq.HeightMap[y * self.mliq.xVerts + x][1] + self.mliq.Position[2]))
        # calculate faces
        indices = []
        for y in range(self.mliq.yTiles):
            for x in range(self.mliq.xTiles):
                indices.append(y * self.mliq.xVerts + x)
                indices.append(y * self.mliq.xVerts + x + 1)
                indices.append((y + 1) * self.mliq.xVerts + x)
                indices.append((y + 1) * self.mliq.xVerts + x)
                indices.append(y * self.mliq.xVerts + x + 1)
                indices.append((y + 1) * self.mliq.xVerts + x + 1)

        return (vertices, indices)
    
    # Return faces indices
    def GetBSPNodeIndices(self, iNode, nodes, faces, indices):
        # last node in branch
        nodeIndices = []
        if(nodes[iNode].PlaneType & BSP_PLANE_TYPE.Leaf):
            for i in range(nodes[iNode].FirstFace, nodes[iNode].FirstFace + nodes[iNode].NumFaces):
                nodeIndices.append(faces[i])

        if(nodes[iNode].Childrens[0] != -1):
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[0], nodes, faces, indices))

        if(nodes[iNode].Childrens[1] != -1):
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[1], nodes, faces, indices))

        return nodeIndices

    def GetCollisionIndices(self):
        nodeIndices = self.GetBSPNodeIndices(0, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
        indices = []
        for i in nodeIndices:
            if(not (self.mopy.TriangleMaterials[i].Flags & 0x04)):
                indices.append(self.movi.Indices[i * 3])
                indices.append(self.movi.Indices[i * 3 + 1])
                indices.append(self.movi.Indices[i * 3 + 2])

        return indices

    # Create mesh from file data
    def LoadObject(self, objName, materials, doodads, mogn):

        vertices = []
        normals = []
        faces = []

        vertColors = []
        texCoords = []
        
        vertices = self.movt.Vertices
        normals = self.monr.Normals
        texCoords = self.motv.TexCoords


        #for i in range(0, len(self.mobr.Faces)):
        #    faces.append((self.movi.Indices[self.mobr.Faces[i] * 3], self.movi.Indices[self.mobr.Faces[i] * 3 + 1], self.movi.Indices[self.mobr.Faces[i] * 3 + 2]))

        for i in range(0, len(self.movi.Indices), 3):
            faces.append(self.movi.Indices[i:i+3])
            
        """for i in range(len(self.moba.Batches)):

            batch = self.moba.Batches[i]

            # add vertices BAAAAAD 
            startVert = len(vertices)
            vertices.extend(self.movt.Vertices[batch.StartVertex : batch.LastVertex + 1])
            
            # add faces
            for iFace in range(batch.StartTriangle, batch.StartTriangle + batch.nTriangle, 3):
                faces.append((self.movi.Indices[iFace] - batch.StartVertex + startVert, \
                    self.movi.Indices[iFace + 1] - batch.StartVertex + startVert, \
                    self.movi.Indices[iFace + 2] - batch.StartVertex + startVert))

            # add vertex normals
            normals.extend(self.monr.Normals[batch.StartVertex : batch.LastVertex + 1])

            
            # add vertex color
            if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
                vertColors.extend(self.mocv.Colors[batch.StartVertex : batch.LastVertex + 1])

            # add uv coords
            texCoords.extend(self.motv.TexCoords[batch.StartVertex : batch.LastVertex + 1])

            # add material
            objMats.append(materials[batch.MaterialID])

        
        geometryVerticesCount = len(vertices)

        # load liquids
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            liquids_data = self.LoadLiquids()
            liquidVerticesCount = len(liquids_data[0])

            startVert = len(vertices)
            vertices.extend(liquids_data[0])

            for i in range(0, len(liquids_data[1]), 3):
                faces.append((liquids_data[1][i] + startVert, liquids_data[1][i + 1] + startVert, liquids_data[1][i + 2] + startVert))"""

        # create mesh
        mesh = bpy.data.meshes.new(objName)
        mesh.from_pydata(vertices, [], faces)

        # set normals
        for i in range(len(normals)):
            mesh.vertices[i].normal = normals[i]
            
        # set vertex color
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            vertColor_layer1 = mesh.vertex_colors.new("Col")
            # loops and vertex_color are in the same order, so we use it to find vertex index
            for i in range(len(mesh.loops)):
                #if(mesh.loops[i].vertex_index < geometryVerticesCount):
                vertColor_layer1.data[i].color = (self.mocv.Colors[mesh.loops[i].vertex_index][2] / 255, \
                        self.mocv.Colors[mesh.loops[i].vertex_index][1] / 255, \
                        self.mocv.Colors[mesh.loops[i].vertex_index][0] / 255)
                
        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            #if(mesh.loops[i].vertex_index < geometryVerticesCount):
            uv = texCoords[mesh.loops[i].vertex_index]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
        # set material
        """for i in range(len(objMats)):
            mesh.materials.append(objMats[i])

        # I guess mesh.polygons and faces are in the same order
        iFace = 0
        for i in range(len(self.moba.Batches)):
            img = self.GetMaterialViewportImage(objMats[i])
            iEndFace = iFace + (self.moba.Batches[i].nTriangle // 3)
            for iFace in range(iFace, iEndFace):
                mesh.polygons[iFace].material_index = i
                mesh.polygons[iFace].use_smooth = True
                if(img != None):
                    uv1.data[iFace].image = img
            iFace += 1"""
            
        # map root material ID to index in mesh materials
        material_indices = {}
        material_viewport_textures = {}

        # add materials
        for i in range(len(self.moba.Batches)):
            mesh.materials.append(materials[self.moba.Batches[i].MaterialID])
            material_viewport_textures[i] = self.GetMaterialViewportImage(mesh.materials[i])
            material_indices[self.moba.Batches[i].MaterialID] = i
            
        # add ghost material
        for i in self.mopy.TriangleMaterials:
            if(i.MaterialID == 0xFF):
                mat_ghost_ID = len(mesh.materials)
                mesh.materials.append(materials[0xFF])
                material_viewport_textures[mat_ghost_ID] = None
                material_indices[0xFF] = mat_ghost_ID
                break

        # set faces material
        for i in range(len(mesh.polygons)):
            matID = self.mopy.TriangleMaterials[i].MaterialID

            mesh.polygons[i].material_index = material_indices[matID]
            mesh.polygons[i].use_smooth = True
            # set texture displayed in viewport
            img = material_viewport_textures[material_indices[matID]]
            if(img != None):
                uv1.data[i].image = img

        # set textured solid in all 3D views
        for area in bpy.context.screen.areas:
            if(area.type == 'VIEW_3D'):
                area.spaces[0].show_textured_solid = True

        scn = bpy.context.scene
                    
        for o in scn.objects:
            o.select = False

        mesh.update()
        mesh.validate()

        nobj = bpy.data.objects.new(objName, mesh)

        # set liquid properties
        """if(self.mogp.Flags & MOGP_FLAG.HasWater):
            liquidGroup = nobj.vertex_groups.new("liquidGroup")

            liquidGroupIndices = []
            for i in range(liquidVerticesCount):
                liquidGroupIndices.append(i + geometryVerticesCount)
            
            liquidGroup.add(liquidGroupIndices, 1.0, 'ADD')
            nobj.WowLiquidEnabled = True
            nobj.WowLiquidVertGroup = "liquidGroup"
            nobj.WowLiquidType = str(self.mogp.LiquidType)"""
        
        #####DEBUG BSP
        """for iNode in range(len(self.mobn.Nodes)):
            bsp_node_indices = self.GetBSPNodeIndices(iNode, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
            bsp_node_vg = nobj.vertex_groups.new("debug_bsp")

            #for i in bsp_n1_indices:
            #    bsp_n1_GroupIndices.append(i)
            
            bsp_node_vg.add(bsp_node_indices, 1.0, 'ADD')"""
        #####DEBUG BSP

        # add collision vertex group
        collision_indices = self.GetCollisionIndices()

        if(collision_indices):
            collision_vg = nobj.vertex_groups.new("collision")    
            collision_vg.add(collision_indices, 1.0, 'ADD')
            nobj.WowCollision.Enabled = True
            nobj.WowCollision.VertexGroup = collision_vg.name

        # add WMO group properties
        nobj.WowWMOGroup.Enabled = True
        nobj.WowWMOGroup.GroupName = mogn.GetString(self.mogp.GroupNameOfs)
        nobj.WowWMOGroup.GroupDesc = mogn.GetString(self.mogp.DescGroupNameOfs)
        if(self.mogp.Flags & 0x2000):
            nobj.WowWMOGroup.PlaceType = str(0x2000)
        else:
            nobj.WowWMOGroup.PlaceType = str(0x8)

        scn.objects.link(nobj)

        nobj.select = True
        #nobj.show_transparent = True

        if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
            scn.objects.active = nobj

    def Save(self, f, obj, root):#, material_indices, group_name_ofs, group_desc_ofs):

        # check Wow WMO panel enabled
        if(not obj.WowWMOGroup.Enabled):
            #bpy.ops.error.message(message="Error: Trying to export " + obj.name + " but Wow WMO Group properties not enabled")
            raise Exception("Error: Trying to export " + obj.name + " but Wow WMO Group properties not enabled")
            return

        mesh = obj.data

        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        mver = MVER_chunk()
        mver.Version = 17
        mver.Write(f)

        mogp = MOGP_chunk()

        # order faces by material
        old_texCoords = []
        for i in range(len(mesh.vertices)):
            old_texCoords.append((0, 0))

        if len(mesh.uv_layers) > 0:
            uv_layer = mesh.uv_layers.active
            for i in range(len(uv_layer.data)):
                uv = (uv_layer.data[i].uv[0], 1 - uv_layer.data[i].uv[1])
                old_texCoords[mesh.loops[i].vertex_index] = uv

        batch_indices = []
        batch_vertices = []
        batch_normals = []
        batch_texCoords = []
        batch_collide = [] # for each vertice, True if collide, False otherwise
        batch_material_index = []

        batch_indice_range = []
        batch_vertex_range = []

        collision_vg_index = None

        if(obj.WowCollision.Enabled):
            collision_vg = obj.vertex_groups.get(obj.WowCollision.VertexGroup)
            if(collision_vg != None):
                collision_vg_index = collision_vg.index

        for i in range(len(mesh.materials)):
            indices = []
            for poly in mesh.polygons:
                if(poly.material_index == i):
                    indices.append(poly.vertices[0])
                    indices.append(poly.vertices[1])
                    indices.append(poly.vertices[2])
            batch_indices.append(indices)
            batch_material_index.append(root.AddMaterial(mesh.materials[i]))

        # create batch vertices and reorder indices
        startIndex = 0
        startVertex = 0
        for iBatch in range(len(batch_indices)):
            batch = batch_indices[iBatch]

            new_vertices = []
            new_indices = []
            new_normals = []
            new_texCoords = []
            new_collide = []

            # resize new_indices
            for i in range(len(batch)):
                new_indices.append(0)

            indices_map = {}
            for iIndex in range(len(batch)):
                # if vertex is already referenced, use that reference
                if batch[iIndex] in indices_map:
                    new_indices[iIndex] = indices_map[batch[iIndex]]
                # else add vertex in vertex list, and add reference
                else:
                    v = mesh.vertices[batch[iIndex]]
                    new_vertices.append(v.co)
                    new_normals.append(v.normal)
                    new_texCoords.append(old_texCoords[batch[iIndex]])
                    indices_map[batch[iIndex]] = len(new_vertices) - 1 + startVertex
                    new_indices[iIndex] = indices_map[batch[iIndex]]
                    # add index to collision list
                    if(collision_vg_index != None):
                        for groupElem in v.groups:
                            if(groupElem.group == collision_vg_index):
                                if(groupElem.weight > 0):
                                    new_collide.append(True)
                                    break
                                else:
                                    new_collide.append(False)
                                    break
                        else:
                            new_collide.append(False)
                    else:
                        new_collide.append(False)
            
            batch_collide.append(new_collide)
            batch_vertices.append(new_vertices)
            batch_normals.append(new_normals)
            batch_texCoords.append(new_texCoords)
            batch_indices[iBatch] = new_indices

            batch_indice_range.append((startIndex, len(new_indices)))
            batch_vertex_range.append((startVertex, len(new_vertices)))

            startIndex += len(new_indices)
            startVertex += len(new_vertices)

        del startIndex
        del startVertex

        # write triange materials
        mopy = MOPY_chunk()
        mopy.TriangleMaterials = []

        for iBatch in range(len(batch_indices)):
            for i in range(0, len(batch_indices[iBatch]), 3):
                triMat = TriangleMaterial()
                triMat.MaterialID = batch_material_index[iBatch]#material_indices[mesh.materials[iBatch]]

                # check if face is rendered
                if(triMat.MaterialID == 0xFF):
                    triMat.Flags = 0
                else:
                    triMat.Flags = 0x20 # F_RENDER

                # check if colliding face
                if(batch_collide[iBatch][batch_indices[iBatch][i] - batch_vertex_range[iBatch][0]] == True and
                   batch_collide[iBatch][batch_indices[iBatch][i + 1] - batch_vertex_range[iBatch][0]] == True and
                   batch_collide[iBatch][batch_indices[iBatch][i + 2] - batch_vertex_range[iBatch][0]] == True):
                    triMat.Flags = triMat.Flags | 0x48 # F_COLLIDE_HIT & F_HINT
                else:
                    triMat.Flags = triMat.Flags | 0x04 # F_NO_COLLISION


                mopy.TriangleMaterials.append(triMat)

        # write indices
        movi = MOVI_chunk()
        movi.Indices = []
        for batch in batch_indices:
            movi.Indices.extend(batch)

        # write vertices
        movt = MOVT_chunk()
        movt.Vertices = []
        for batch in batch_vertices:
            movt.Vertices.extend(batch)

        # write normals
        monr = MONR_chunk()
        monr.Normals = []
        for batch in batch_normals:
            monr.Normals.extend(batch)

        # write UV
        motv = MOTV_chunk()
        motv.TexCoords = []

        for batch in batch_texCoords:
            motv.TexCoords.extend(batch)

        # write batches
        moba = MOBA_chunk()
        moba.Batches = []

        for i in range(len(batch_vertices)):
            # pass if no vertices or material is ghost(0xFF)
            if(len(batch_vertices[i]) == 0 or batch_material_index[i] == 0xFF):#material_indices[mesh.materials[i]] == 0xFF):
                continue

            batch = Batch()

            bb = CalculateBoundingBox(batch_vertices[i])
            batch.BoundingBox = (floor(bb[0][0]), floor(bb[0][1]), floor(bb[0][2]), ceil(bb[1][0]), ceil(bb[1][1]), ceil(bb[1][2]))
            batch.StartTriangle = batch_indice_range[i][0]
            batch.nTriangle = batch_indice_range[i][1]
            batch.StartVertex = batch_vertex_range[i][0]
            batch.LastVertex = batch_vertex_range[i][0] + batch_vertex_range[i][1] - 1
            batch.Unknown = 0
            batch.MaterialID = batch_material_index[i]#material_indices[mesh.materials[i]]

            moba.Batches.append(batch)

        # write BSP nodes
        mobn = MOBN_chunk()

        # write BSP faces
        mobr = MOBR_chunk()

        # write header
        bb = CalculateBoundingBox(movt.Vertices)

        mogp.Flags = MOGP_FLAG.HasCollision # /!\ MUST HAVE 0x1 FLAG ELSE THE GAME CRASH !

        mogp.Flags = mogp.Flags | int(obj.WowWMOGroup.PlaceType)

        mogp.BoundingBoxCorner1 = bb[0]
        mogp.BoundingBoxCorner2 = bb[1]
        mogp.PortalStart = 0
        mogp.PortalCount = 0
        mogp.nBatchesA = 0
        mogp.nBatchesB = 0
        mogp.nBatchesC = len(moba.Batches)
        mogp.nBatchesD = 0
        mogp.FogIndices = (0, 0, 0, 0)
        mogp.LiquidType = 0
        mogp.GroupID = 0#23822
        mogp.Unknown1 = 0
        mogp.Unknown2 = 0
        
        groupInfo = root.AddGroupInfo(mogp.Flags, bb, obj.WowWMOGroup.GroupName, obj.WowWMOGroup.GroupDesc)
        mogp.GroupNameOfs = groupInfo[0]
        mogp.DescGroupNameOfs = groupInfo[1]
        
        f.seek(0x58)
        mopy.Write(f)
        movi.Write(f)
        movt.Write(f)
        monr.Write(f)
        motv.Write(f)
        moba.Write(f)
        
        bsp_tree = BSP_Tree()
        bsp_tree.GenerateBSP(movt.Vertices, movi.Indices, obj.WowCollision.NodeSize)

        mobn.Nodes = bsp_tree.Nodes
        mobr.Faces = bsp_tree.Faces

        mobn.Write(f)
        mobr.Write(f)

        # get file size
        f.seek(0, 2)
        mogp.Header.Size = f.tell() - 20

        # write header
        f.seek(0xC)
        mogp.Write(f)

        return None