__author__ = 'Eric'

import bpy
from sporemodder import RW4Base
from sporemodder.materials import DirectXEnums
from sporemodder import RWMaterialConfig
from collections import namedtuple
from mathutils import Matrix, Quaternion, Vector
from random import choice


# noinspection PyUnusedLocal
def write_raw_buffer(fileWriter, data, owner):
    fileWriter.fileBuffer.write(data)


def write_index_buffer(fileWriter, data, owner):
    if owner.format == DirectXEnums.D3DFORMAT.D3DFMT_INDEX16:
        for x in data:
            fileWriter.writeUShort(x)

    elif owner.format == DirectXEnums.D3DFORMAT.D3DFMT_INDEX32:
        for x in data:
            fileWriter.writeUInt(x)


def write_vertex_buffer(fileWriter, data, owner):
    for vertexIndex in range(owner.vertexCount):
        for i in range(len(owner.vertexDescription.vertexElements)):
            owner.vertexDescription.vertexElements[i].writeData(fileWriter, data[i][vertexIndex])


def signed_float_to_ubyte(value):
    return int(round(value * 127.5 + 127.5) & 0xFF)


def unpack_ubyte_vec3(values):
    return Vector((
        (values[0] - 127.5) / 127.5,
        (values[1] - 127.5) / 127.5,
        (values[2] - 127.5) / 127.5
    ))


def pack_ubyte_vec3(values):
    return (
        int(round(values[0] * 127.5 + 127.5) & 0xFF),
        int(round(values[1] * 127.5 + 127.5) & 0xFF),
        int(round(values[2] * 127.5 + 127.5) & 0xFF),
        0
    )


def calculate_tangents(vertices, faces):
    vTangents = []
    vBitangents = []
    # calcTangents:
    for v in range(len(vertices.pos)):
        vTangents.append(Vector((0.0, 0.0, 0.0)))
        vBitangents.append(Vector((0.0, 0.0, 0.0)))

        # we need 4 values (we use ubyte4)
        vertices.tangents.append([0, 0, 0, 0])

    for f, face in enumerate(faces):
        v0_co = vertices.pos[face[0]]
        v1_co = vertices.pos[face[1]]
        v2_co = vertices.pos[face[2]]
        v0_uv = vertices.uvs[face[0]]
        v1_uv = vertices.uvs[face[1]]
        v2_uv = vertices.uvs[face[2]]

        dco1 = v1_co - v0_co
        dco2 = v2_co - v0_co
        duv1 = Vector((v1_uv[0], v1_uv[1])) - Vector((v0_uv[0], v0_uv[1]))
        duv2 = Vector((v2_uv[0], v2_uv[1])) - Vector((v0_uv[0], v0_uv[1]))
        tangent = dco2 * duv1.y - dco1 * duv2.y
        bitangent = dco2 * duv1.x - dco1 * duv2.x
        if dco2.cross(dco1).dot(bitangent.cross(tangent)) < 0:
            tangent.negate()
            bitangent.negate()
        vTangents[face[0]] += tangent
        vTangents[face[1]] += tangent
        vTangents[face[2]] += tangent
        vBitangents[face[0]] += bitangent
        vBitangents[face[1]] += bitangent
        vBitangents[face[2]] += bitangent

    for v in range(len(vertices.tangents)):
        normal = unpack_ubyte_vec3(vertices.normals[v])
        vTangents[v] = vTangents[v] - normal * vTangents[v].dot(normal)
        vTangents[v].normalize()
        # Spore normals and tangents are ubytes from 0 to 255
        vertices.tangents[v] = pack_ubyte_vec3(vTangents[v])


class RW4Exporter:
    class BaseBone:
        def __init__(self, absBindPose, invPoseTranslation):
            self.abs_bind_pose = absBindPose
            self.inv_pose_translation = invPoseTranslation
    
    def __init__(self):
        self.renderWare = RW4Base.RenderWare4()
        self.added_textures = {}

        self.bArmatureObject = None
        self.bMeshObjects = []
        
        self.bone_bases = {}

        self.renderWare.header.rwTypeCode = RW4Base.RWHeader.type_code_model
        
        self.bound_box = None
        
        # for TriangleKDTreeProcedural
        self.triangles = []
        self.vertices = []
        self.triangle_unknowns = []
        
    def get_bone_count(self):
        if self.bArmatureObject is None:
            return 0
        return len(self.bArmatureObject.data.bones)
    
    def get_skin_matrix_buffer_index(self):
        skinMatrixBuffers = self.renderWare.getObjects(RW4Base.SkinMatrixBuffer.type_code)

        if len(skinMatrixBuffers) > 0:
            return self.renderWare.getIndex(
                skinMatrixBuffers[0],
                sectionType=RW4Base.INDEX_SUB_REFERENCE)

        else:
            return self.renderWare.getIndex(None, sectionType=RW4Base.INDEX_NO_OBJECT)

    def add_texture(self, path):
        if path is not None and len(path) > 0 and path in self.added_textures:
            return self.added_textures[path]

        raster = RW4Base.Raster(self.renderWare)
        data_buffer = RW4Base.BaseResource(self.renderWare,
                                           write_method=write_raw_buffer)

        if path is None or len(path) == 0:
            # just create an empty texture
            raster.width = 64
            raster.height = 64
            raster.mipmapLevels = 7
            raster.textureFormat = DirectXEnums.D3DFORMAT.D3DFMT_DXT5

            data_buffer.data = bytearray(5488)  # ?

        else:
            file = open(bpy.path.abspath(path), 'rb')

            dds_texture = RW4Base.DDSTexture()
            dds_texture.read(RW4Base.FileReader(file))

            raster.fromDDS(dds_texture)
            data_buffer.data = dds_texture.data

            file.close()

            self.added_textures[path] = raster

        raster.textureData = data_buffer

        # Add the objects we just created
        self.renderWare.addObject(raster)
        self.renderWare.addObject(data_buffer)

        return raster

    def process_vertex_bones(self, obj, vertices, vertex):
        indices = []
        weights = []
        size = 0
        for gr in vertex.groups:
            for index, bBone in enumerate(self.bArmatureObject.data.bones):
                if bBone.name == obj.vertex_groups[gr.group].name:
                    indices.append(index * 3)
                    weights.append(gr.weight)

                    size += 1
                    if size == 4:
                        break

        for i in range(size, 4):
            indices.append(0)
            weights.append(0.0)
            
        # Special case: if there are no bone weights, we must do this or the model will be invisible
        if size == 0:
            weights[0] = 1.0

        vertices.boneIndices.append(indices)
        vertices.boneWeights.append(weights)

    def process_mesh(self, obj, mesh, use_uvCoordinates, use_bones):
        """
        Spore models only have one UV per-vertex, whereas Blender can have more than just one.
        This method converts a Blender mesh into a valid Spore mesh.
        """

        # we store the data on a namedtuple containing tuples
        # each tuple contains the data of one vertex attribute, as defined in RWVertexDeclUsageNames
        #  "pos"
        #  "normals"
        #  "uvs"
        #  "boneIndices"
        #  "boneWeights"
        #  "tangents"

        # we need it to create an instance of the namedtuple
        emtpyData = []

        namedtuple_names = ["pos", "normals"]
        emtpyData.append([])
        emtpyData.append([])

        if use_uvCoordinates:
            namedtuple_names.append("tangents")
            namedtuple_names.append("uvs")
            emtpyData.append([])
            emtpyData.append([])

        if use_bones:
            namedtuple_names.append("boneIndices")
            namedtuple_names.append("boneWeights")
            emtpyData.append([])
            emtpyData.append([])

        VerticesType = namedtuple('VerticesType', namedtuple_names)

        # the result
        triangles = [None] * len(mesh.tessfaces)
        vertices = VerticesType(*emtpyData)

        if not use_uvCoordinates:
            # no need to process if we don't have UV coords

            for t, face in enumerate(mesh.tessfaces):
                triangles[t] = (face.vertices_raw[0],
                                face.vertices_raw[1],
                                face.vertices_raw[2],
                                face.material_index)

            for vertex in mesh.vertices:
                vertices.pos.append(vertex.co)
                # Spore normals and tangents are ubytes from 0 to 255
                vertices.normals.append((
                    signed_float_to_ubyte(vertex.normal[0]),
                    signed_float_to_ubyte(vertex.normal[1]),
                    signed_float_to_ubyte(vertex.normal[2]),
                    0  # we use ubyte4, we need 4 values
                ))

                if use_bones:
                    self.process_vertex_bones(obj, vertices, vertex)

        else:
            # each item of this list is a list of all the new vertex indices that
            # represent that vertex
            new_vertex_indices = [[] for _ in range(len(mesh.vertices))]
            current_processed_index = 0

            uv_data = mesh.tessface_uv_textures.active.data

            for t, face in enumerate(mesh.tessfaces):

                triangles[t] = [-1, -1, -1, face.material_index]

                for i in range(3):
                    index = face.vertices_raw[i]

                    # has a vertex with these UV coordinates been already processed?
                    for processed_index in new_vertex_indices[index]:
                        if vertices.uvs[processed_index][0] == uv_data[t].uv[i][0] \
                                and vertices.uvs[processed_index][1] == uv_data[t].uv[i][1]:

                            triangles[t][i] = processed_index
                            break

                    # if no vertex with UVs has been processed
                    else:
                        # process vertex
                        vertices.pos.append(mesh.vertices[index].co)
                        # Spore normals and tangents are ubytes from 0 to 255
                        vertices.normals.append((
                            signed_float_to_ubyte(mesh.vertices[index].normal[0]),
                            signed_float_to_ubyte(mesh.vertices[index].normal[1]),
                            signed_float_to_ubyte(mesh.vertices[index].normal[2]),
                            0  # we use ubyte4, we need 4 values
                        ))
                        vertices.uvs.append([uv_data[t].uv[i][0], uv_data[t].uv[i][1]])
                        # we will calculate the tangents later, once we have everything

                        if use_bones:
                            self.process_vertex_bones(obj, vertices, mesh.vertices[index])

                        triangles[t][i] = current_processed_index

                        # noinspection PyTypeChecker
                        new_vertex_indices[index].append(current_processed_index)
                        current_processed_index += 1

            calculate_tangents(vertices, triangles)

            # flip vertical UV coordinates so it uses DirectX system
            for i in range(len(vertices.uvs)):
                vertices.uvs[i][1] = -vertices.uvs[i][1]

        return vertices, triangles

    def create_vertex_description(self, use_uvCoordinates, use_bones):
        description = RW4Base.VertexDescription(self.renderWare)
        offset = 0

        # position
        element = RW4Base.VertexElement(
            stream=0,
            offset=offset,
            elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT3,
            method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
            usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_POSITION,
            usageIndex=0,
            typeCode=DirectXEnums.RWVertexDeclUsage.POSITIONS
        )
        description.vertexElements.append(element)
        offset += 12  # 3 floats, 4 bytes each

        # normals
        element = RW4Base.VertexElement(
            stream=0,
            offset=offset,
            elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4,
            method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
            usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_NORMAL,
            usageIndex=0,
            typeCode=DirectXEnums.RWVertexDeclUsage.NORMALS
        )
        description.vertexElements.append(element)
        offset += 4

        if use_uvCoordinates:
            # tangents
            element = RW4Base.VertexElement(
                stream=0,
                offset=offset,
                elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4,
                method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
                usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_TANGENT,
                usageIndex=0,
                typeCode=DirectXEnums.RWVertexDeclUsage.TANGENTS
            )
            description.vertexElements.append(element)
            offset += 4

            # uvs
            element = RW4Base.VertexElement(
                stream=0,
                offset=offset,
                elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT2,
                method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
                usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_TEXCOORD,
                usageIndex=0,
                typeCode=DirectXEnums.RWVertexDeclUsage.UV
            )
            description.vertexElements.append(element)
            offset += 8

        if use_bones:
            # boneAssignments
            element = RW4Base.VertexElement(
                stream=0,
                offset=offset,
                elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4,
                method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
                usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_BLENDINDICES,
                usageIndex=0,
                typeCode=DirectXEnums.RWVertexDeclUsage.BONEASSIGNMENTS
            )
            description.vertexElements.append(element)
            offset += 4

            # skinWeights
            element = RW4Base.VertexElement(
                stream=0,
                offset=offset,
                elementType=DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4N,
                method=DirectXEnums.D3DDECLMETHOD.D3DDECLMETHOD_DEFAULT,
                usage=DirectXEnums.D3DDECLUSAGE.D3DDECLUSAGE_BLENDWEIGHT,
                usageIndex=0,
                typeCode=DirectXEnums.RWVertexDeclUsage.SKINWEIGHTS
            )
            description.vertexElements.append(element)
            offset += 4

        description.vertexSize = offset
        description.field_10 = 0x0008c045
        description.field_14 = 0x51010101

        return description

    def export_mesh_object(self, obj):
        renderWare = self.renderWare

        bpy.context.scene.objects.active = obj
        obj.modifiers.new("Triangulate", 'TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier="Triangulate")

        blender_mesh = obj.to_mesh(bpy.context.scene, False, 'PREVIEW')
        self.bMeshObjects.append(obj)

        blender_mesh.calc_tessface()

        use_uvCoordinates = blender_mesh.tessface_uv_textures.active is not None
        use_bones = self.bArmatureObject is not None

        # for each object, create a vertex and index buffer

        vertices, triangles = self.process_mesh(obj, blender_mesh, use_uvCoordinates, use_bones)

        primitive_type = DirectXEnums.D3DPRIMITIVETYPE.D3DPT_TRIANGLELIST

        # Configure INDEX BUFFER
        indexBuffer = RW4Base.IndexBuffer(
            renderWare,
            startIndex=0,
            # we are going to use triangles
            primitiveCount=len(triangles) * 3,
            usage=DirectXEnums.D3DUSAGE.D3DUSAGE_WRITEONLY,
            indexFormat=DirectXEnums.D3DFORMAT.D3DFMT_INDEX16,
            primitiveType=primitive_type
        )
        # We will set the buffer data later, after we have ordered them by material

        # Configure VERTEX BUFFER
        vertexDescription = self.create_vertex_description(use_uvCoordinates, use_bones)

        vertexBuffer = RW4Base.VertexBuffer(
            renderWare,
            vertexDescription=vertexDescription,
            baseVertexIndex=0,
            vertexCount=len(vertices.pos),
            field_10=8,
            vertexSize=vertexDescription.vertexSize
        )
        vertexBuffer.vertexData = RW4Base.BaseResource(
            renderWare,
            write_method=write_vertex_buffer,
            data=vertices,
            owner=vertexBuffer
        )

        indexData = []

        for material_index in range(len(obj.material_slots)):

            first_index = len(indexData)
            triangle_count = 0

            for tri in triangles:
                if tri[3] == material_index:
                    indexData.append(tri[0])
                    indexData.append(tri[1])
                    indexData.append(tri[2])

                    triangle_count += 1

            # There's no need to create a mesh if there are no triangles
            if triangle_count > 0:
                first_vertex = indexData[first_index]
                last_vertex = indexData[first_index]

                for i in range(first_index, first_index + triangle_count * 3):
                    if indexData[i] < first_vertex:
                        first_vertex = indexData[i]

                    elif indexData[i] > last_vertex:
                        last_vertex = indexData[i]

                mesh = RW4Base.Mesh(
                    renderWare,
                    field_0=40,  # I have no idea of what this is
                    primitiveType=primitive_type,
                    primitiveCount=triangle_count * 3,
                    triangleCount=triangle_count,
                    firstIndex=first_index,
                    firstVertex=first_vertex,
                    vertexCount=last_vertex - first_vertex + 1,
                    indexBuffer=indexBuffer
                )
                mesh.vertexBuffers.append(vertexBuffer)

                meshLink = RW4Base.MeshCompiledStateLink(
                    renderWare,
                    mesh=mesh
                )

                compiledState = RW4Base.CompiledState(
                    renderWare
                )
                meshLink.compiledStates.append(compiledState)

                material_data = obj.material_slots[material_index].material.renderWare4
                active_material = RWMaterialConfig.get_active_material(material_data)

                if active_material is not None:
                    material_builder = active_material.material_class.get_material_builder(self, material_data)

                    material_builder.vertex_description = vertexBuffer.vertexDescription
                    material_builder.primitive_type = primitive_type

                    material_builder.write(renderWare, compiledState.data)

                # Add all the objects we just created
                renderWare.addObject(mesh)
                renderWare.addObject(meshLink)
                renderWare.addObject(compiledState)

        indexBuffer.indexData = RW4Base.BaseResource(
            renderWare,
            write_method=write_index_buffer,
            data=indexData,
            owner=indexBuffer
        )

        # Add all the objects we just created
        renderWare.addObject(indexBuffer)
        renderWare.addObject(indexBuffer.indexData)
        renderWare.addObject(vertexBuffer)
        renderWare.addObject(vertexBuffer.vertexData)
        renderWare.addObject(vertexBuffer.vertexDescription)
        
        # add required things for TriangleKDTreeProcedural
        self.vertices.extend(vertices.pos)
        
        vertex_count = len(vertices)
        
        for face in triangles:
            self.triangles.append((face[0] + vertex_count, face[1] + vertex_count, face[2] + vertex_count, 0))
            self.triangle_unknowns.append(choice(range(1, 13, 2)))

    def create_animation_skin(self, bBone):
        pose = RW4Base.AnimationSkin.BonePose()
        pose.absBindPose = bBone.matrix_local.to_3x3()
        pose.invPoseTranslation = bBone.matrix_local.inverted().to_translation()
        
        base = RW4Exporter.BaseBone(pose.absBindPose, pose.invPoseTranslation)
        self.bone_bases[bBone.name] = base

        return pose

    @staticmethod
    def create_skin_matrix_buffer():
        matrix = RW4Base.RWMatrix(3, 4)

        for i in range(3):
            for j in range(4):
                matrix[i][j] = 0.0
            matrix[i][i] = 1.0

        return matrix

    def export_armature_object(self, obj):
        if self.bArmatureObject is not None:
            raise NameError("Only one skeleton supported.")

        self.bArmatureObject = obj
        bArmature = self.bArmatureObject.data

        renderWare = self.renderWare

        skinMatrixBuffer = RW4Base.SkinMatrixBuffer(
            renderWare
        )

        skeleton = RW4Base.Skeleton(
            renderWare,
            skeletonID=RW4Base.getHash(self.bArmatureObject.name)
        )

        animationSkin = RW4Base.AnimationSkin(
            renderWare
        )

        skinsInK = RW4Base.SkinsInK(
            renderWare,
            skinMatrixBuffer=skinMatrixBuffer,
            skeleton=skeleton,
            animationSkin=animationSkin,
        )

        # blender bone -> Spore bone
        bBone_to_bone = {}

        for bBone in bArmature.bones:
            bone = RW4Base.Skeleton.SkeletonBone(0, 0, None)
            bone.name = RW4Base.getHash(bBone.name)

            if bBone.parent is not None:
                bone.parent = bBone_to_bone[bBone.parent]

            # calculate flags
            if bBone.parent is not None:
                # if no children
                if len(bBone.children) == 0:
                    # if it's not the only children
                    if len(bBone.parent.children) > 1:
                        bone.flags = 3
                    else:
                        bone.flags = 1

                elif len(bBone.children) == 1:
                    bone.flags = 2

            else:
                bone.flags = 0

            skinMatrixBuffer.data.append(RW4Exporter.create_skin_matrix_buffer())
            animationSkin.data.append(self.create_animation_skin(bBone))

            bBone_to_bone[bBone] = bone

            skeleton.bones.append(bone)

        renderWare.addObject(skinMatrixBuffer)
        renderWare.addObject(skeleton)
        renderWare.addObject(animationSkin)
        renderWare.addObject(skinsInK)

        renderWare.addSubReference(skinMatrixBuffer, 16)
        
        
    def get_total_translation(self, poseBone):
        if poseBone.parent is None:
            return self.get_bone_translation(poseBone)
        else:
            return self.get_bone_translation(poseBone) + self.get_total_translation(poseBone.parent)
        
    def get_bone_translation(self, poseBone):
        # before: using matrix_basis
        # that didn't translate child bones when moving a root in a chain, however
#         if poseBone.parent is None:
#             return poseBone.matrix_basis.to_translation() - self.bone_bases[poseBone.name].inv_pose_translation
#         else:
#             return poseBone.matrix_basis.to_translation() - (self.bone_bases[poseBone.name].inv_pose_translation + self.get_total_translation(poseBone.parent))
#         if poseBone.parent is None:
#             return poseBone.matrix_basis.to_translation() - self.bone_bases[poseBone.name].inv_pose_translation
#         else:
#             return -(self.bone_bases[poseBone.name].inv_pose_translation + self.get_total_translation(poseBone.parent)) - poseBone.matrix_channel.to_translation()

        if poseBone.parent is None:
            return poseBone.matrix_basis.to_translation() - self.bone_bases[poseBone.name].inv_pose_translation
        else:
            return poseBone.parent.matrix.inverted() * poseBone.matrix.to_translation()
        
        
    def get_total_rotation(self, poseBone):
        if poseBone.parent is None:
            return self.get_bone_rotation(poseBone)
        else:
            # return self.get_bone_rotation(poseBone) * self.get_total_rotation(poseBone.parent)
            return self.get_total_rotation(poseBone.parent) * self.get_bone_rotation(poseBone)
        
    def get_bone_rotation(self, poseBone):
        if poseBone.parent is None:
            return poseBone.matrix.to_quaternion()
        else:
            # rotation = poseBone.rotation_quaternion * self.bone_bases[poseBone.parent.name].abs_bind_pose.to_quaternion().inverted()
            #rotation = poseBone.matrix.to_quaternion() * self.bone_bases[poseBone.parent.name].abs_bind_pose.to_quaternion().inverted() * poseBone.parent.rotation_quaternion
            return self.get_total_rotation(poseBone.parent).inverted() * poseBone.matrix.to_quaternion()
        
    def export_actions(self):
        if self.bArmatureObject is None:
            return
        
        renderWare = self.renderWare
        
        animationsList = RW4Base.Animations(renderWare)
        
        current_keyframe = bpy.context.scene.frame_current
        
        for bAction in bpy.data.actions:
            if len(bAction.fcurves) == 0:
                continue
            
            self.bArmatureObject.animation_data.action = bAction
            
            keyframeAnim = RW4Base.KeyframeAnim(renderWare)
            keyframeAnim.skeletonID = RW4Base.getHash(self.bArmatureObject.name)
            keyframeAnim.length = bAction.frame_range[1] / RW4Base.KeyframeAnim.frames_per_second
            keyframeAnim.flags = 3
            
            # Now, either add to animations list or to handles
            if bAction.rw4 is not None and bAction.rw4.is_morph_handle:
                handle = RW4Base.MorphHandle(renderWare)
                handle.handleID = RW4Base.getHash(bAction.name)
                handle.field_C = bAction.rw4.initial_pos[0]
                handle.field_14 = bAction.rw4.initial_pos[1]
                handle.field_1C = bAction.rw4.initial_pos[2]
                handle.field_24 = bAction.rw4.final_pos[0]
                handle.field_2C = bAction.rw4.final_pos[1]
                handle.field_34 = bAction.rw4.final_pos[2]
                handle.default_frame = bAction.rw4.default_frame / bAction.frame_range[1]
                handle.animation = keyframeAnim
                
                renderWare.addObject(handle)
                
            else:
                animationsList.add(RW4Base.getHash(bAction.name), keyframeAnim)
            
            renderWare.addObject(keyframeAnim)
            # renderWare.objects.insert(0, keyframeAnim)
            
            for group in bAction.groups:
                
                poseBone = next(b for b in self.bArmatureObject.pose.bones if b.name == group.name)
                baseBone = self.bone_bases[group.name]
                
                channel = RW4Base.KeyframeAnim.Channel(RW4Base.KeyframeAnim.Channel.LocRotScale)  # TODO
                channel.channelID = RW4Base.getHash(group.name)
                keyframeAnim.channels.append(channel)
                
                bpy.context.scene.frame_set(0)
                
                for kf in group.channels[0].keyframe_points:
                    bpy.context.scene.frame_set(int(kf.co[0]))
                    
                    keyframe = channel.newKeyframe(kf.co[0] / RW4Base.KeyframeAnim.frames_per_second)
                    
                    # baseTransform * keyframeTransform = finalTransform
                    # blenderKeyframe = finalTranform ?
                    
                    # translation = poseBone.matrix.to_translation()
                    
                    translation = self.get_bone_translation(poseBone)
                    
                    scale = poseBone.matrix.to_scale()
                    
                    rotation = self.get_bone_rotation(poseBone)
                    
#                     if poseBone.parent is None:
#                         rotation = poseBone.matrix.to_quaternion()
#                     else:
#                         # rotation = poseBone.rotation_quaternion * self.bone_bases[poseBone.parent.name].abs_bind_pose.to_quaternion().inverted()
#                         rotation = poseBone.matrix.to_quaternion() * self.bone_bases[poseBone.parent.name].abs_bind_pose.to_quaternion().inverted() * poseBone.parent.rotation_quaternion
                    
                    keyframe.setTranslation(translation)
                    keyframe.setScale(scale)
                    
                    # keyframe.setRotation(baseBone.abs_bind_pose.to_quaternion().inverted() * poseBone.matrix.to_quaternion())
                    keyframe.setRotation(rotation)
        
        
        if len(animationsList.animations) > 0:
            renderWare.addObject(animationsList)
            renderWare.addSubReference(animationsList, 8)
            
        bpy.context.scene.frame_set(current_keyframe)
        
    def calcGlobalBBox(self):
        minBBox = [self.bMeshObjects[0].bound_box[0][0], self.bMeshObjects[0].bound_box[0][1], self.bMeshObjects[0].bound_box[0][2]]
        maxBBox = [self.bMeshObjects[0].bound_box[6][0], self.bMeshObjects[0].bound_box[6][1], self.bMeshObjects[0].bound_box[6][2]]
        
        for i in range(1, len(self.bMeshObjects)):
            if self.bMeshObjects[i].bound_box[0][0] < minBBox[0]:
                minBBox[0] = self.bMeshObjects[i].bound_box[0][0]
            if self.bMeshObjects[i].bound_box[0][1] < minBBox[1]:
                minBBox[1] = self.bMeshObjects[i].bound_box[0][1]
            if self.bMeshObjects[i].bound_box[0][2] < minBBox[2]:
                minBBox[2] = self.bMeshObjects[i].bound_box[0][2]
    
            if self.bMeshObjects[i].bound_box[6][0] > maxBBox[0]:
                maxBBox[0] = self.bMeshObjects[i].bound_box[6][0]
            if self.bMeshObjects[i].bound_box[6][1] > maxBBox[1]:
                maxBBox[1] = self.bMeshObjects[i].bound_box[6][1]
            if self.bMeshObjects[i].bound_box[6][2] > maxBBox[2]:
                maxBBox[2] = self.bMeshObjects[i].bound_box[6][2]
    
        return [minBBox, maxBBox]
    
    def export_bbox(self):
        if len(self.bMeshObjects) > 0:
            self.bound_box = RW4Base.BBox(self.renderWare, bound_box=self.calcGlobalBBox())
            self.renderWare.addObject(self.bound_box)
            
    def export_kdtree(self):
        kdtree = RW4Base.TriangleKDTreeProcedural(self.renderWare)
        kdtree.bound_box = self.bound_box
        kdtree.bound_box_2 = self.bound_box
        kdtree.triangles = self.triangles
        kdtree.vertices = self.vertices
        kdtree.triangle_unknowns = self.triangle_unknowns
        
        self.renderWare.addObject(kdtree)


def exportRW4(file):

    # NOTE: We might not use Spore's conventional ordering of RW objects, since it's a lot easier to do it this way.
    # Theoretically, this has no effect on the game so it should work fine.

    exporter = RW4Exporter()

    # first find the skeleton (if any)
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            exporter.export_armature_object(obj)
            
    exporter.export_actions()

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            exporter.export_mesh_object(obj)

    exporter.export_bbox()
    exporter.export_kdtree()
    
    
#     # try ordering 
#     objects = []
#     
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.KeyframeAnim])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.MorphHandle])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.BBox])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.TriangleKDTreeProcedural])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.VertexDescription])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.AnimationSkin])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.SkinMatrixBuffer])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.SkinsInK])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.IndexBuffer])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.Mesh])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.CompiledState])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.MeshCompiledStateLink])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.Skeleton])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.VertexBuffer])
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.Raster])
# 
#     objects.extend([x for x in exporter.renderWare.objects if type(x) is RW4Base.BaseResource])
#     
#     exporter.renderWare.objects = objects
    
    print(exporter.renderWare.objects)

    exporter.renderWare.write(RW4Base.FileWriter(file))

    return {'FINISHED'}