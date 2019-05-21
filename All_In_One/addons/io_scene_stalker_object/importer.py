
import bpy
import math
import random


def random_color():
    return 0.2 + 0.6 * random.random()


def get_equal_scene_image(stalkerMaterial, texturesPath):
    bpy_image = None
    if bpy.data.images.get(stalkerMaterial.texture.split('\\')[-1] + '.dds'):
        if bpy.data.images[stalkerMaterial.texture.split('\\')[-1] + '.dds'].filepath == texturesPath + stalkerMaterial.texture + '.dds':
            bpy_image = bpy.data.images[stalkerMaterial.texture.split('\\')[-1] + '.dds']
    return bpy_image


def get_equal_scene_texture(stalkerMaterial, texturesPath):
    bpy_texture = None
    if bpy.data.textures.get(stalkerMaterial.texture):
        if bpy.data.textures[stalkerMaterial.texture].image.name == stalkerMaterial.texture.split('\\')[-1] + '.dds' and \
        bpy.data.textures[stalkerMaterial.texture].image.filepath == texturesPath + stalkerMaterial.texture + '.dds':
            bpy_texture = bpy.data.textures[stalkerMaterial.texture]
    return bpy_texture


def get_equal_scene_material(stalkerMaterial, texturesPath):
    bpy_material = None
    for material in bpy.data.materials:
        if material.name.startswith(stalkerMaterial.name):
            m = bpy.data.materials[material.name]
            if m.stalker.engine_shader == stalkerMaterial.engine_shader and \
            m.stalker.compiler_shader == stalkerMaterial.compiler_shader and \
            m.stalker.game_material == stalkerMaterial.game_material and \
            m.stalker.two_sided == stalkerMaterial.two_sided and \
            m.texture_slots[0].texture.name == stalkerMaterial.texture and \
            m.texture_slots[0].texture.image.name == stalkerMaterial.texture.split('\\')[-1] + '.dds' and \
            m.texture_slots[0].texture.image.filepath == texturesPath + stalkerMaterial.texture + '.dds':
                bpy_material = bpy.data.materials[material.name]
    return bpy_material


def create_material(stalkerMaterial, texturesPath, report):
    bpy_material = get_equal_scene_material(stalkerMaterial, texturesPath)
    if not bpy_material:
        bpy_material = bpy.data.materials.new(name=stalkerMaterial.name)
        bpy_material.diffuse_color = (random_color(), random_color(), random_color())
        bpy_material.stalker.engine_shader = stalkerMaterial.engine_shader
        bpy_material.stalker.compiler_shader = stalkerMaterial.compiler_shader
        bpy_material.stalker.game_material = stalkerMaterial.game_material
        bpy_material.stalker.two_sided = stalkerMaterial.two_sided
        bpy_material.texture_slots.add()
        bpy_texture = get_equal_scene_texture(stalkerMaterial, texturesPath)
        if not bpy_texture:
            bpy_texture = bpy.data.textures.new(name=stalkerMaterial.texture, type='IMAGE')
            bpy_image = get_equal_scene_image(stalkerMaterial, texturesPath)
            if not bpy_image:
                texturePath = texturesPath + stalkerMaterial.texture + '.dds'
                try:
                    bpy_image = bpy.data.images.load(texturePath)
                except:
                    bpy_image = bpy.data.images.new(stalkerMaterial.texture.split('\\')[-1] + '.dds', 0, 0)
                    bpy_image.source = 'FILE'
                    bpy_image.filepath = texturePath
                    report({'WARNING'}, 'Can\'t load {}'.format(texturePath))
            bpy_texture.image = bpy_image
        bpy_material.texture_slots.add()
        bpy_material.texture_slots[0].texture = bpy_texture
    return bpy_material


def create_materials(so):
    bpy_materials = {}
    for material in so.materials.values():
        bpy_material = create_material(material, so.context.texture_folder, so.context.operator.report)
        bpy_materials[material.name] = bpy_material
    return bpy_materials


def create_smoothing_groups(meshData, bpy_mesh, smoothingGroupsType):
    bpy_mesh.use_auto_smooth = True
    if smoothingGroupsType == 'SOC':
        edgesSmoothingGroups = [set() for _ in range(len(bpy_mesh.edges))]
        for polygon in bpy_mesh.polygons:
            polygon.use_smooth = True
            smoothingGroupId = meshData.smoothing_groups[polygon.index]
            for loopIndex in range(polygon.loop_start, polygon.loop_start + 3):
                edgesSmoothingGroups[bpy_mesh.loops[loopIndex].edge_index].add(smoothingGroupId)
        for edgeIndex, edgeSmoothingGroups in enumerate(edgesSmoothingGroups):
            if len(edgeSmoothingGroups) == 2:
                bpy_mesh.edges[edgeIndex].use_edge_sharp = True
    elif smoothingGroupsType == 'CS_COP':
        edgeFlags = (0x4, 0x2, 0x1)
        edgesSmoothingGroups = [[] for _ in range(len(bpy_mesh.edges))]
        for polygon in bpy_mesh.polygons:
            polygon.use_smooth = True
            smoothingGroupId = meshData.smoothing_groups[polygon.index]
            for faceEdgeIndex, loopIndex in enumerate(range(polygon.loop_start, polygon.loop_start + 3)):
                edgeIndex = bpy_mesh.loops[loopIndex].edge_index
                edgesSmoothingGroups[edgeIndex].append((faceEdgeIndex, smoothingGroupId))
                edgeSmoothingGroups = edgesSmoothingGroups[edgeIndex]
                if len(edgeSmoothingGroups) == 2:
                    edge1 = edgeSmoothingGroups[0][0]
                    edge2 = edgeSmoothingGroups[1][0]
                    group1 = edgeSmoothingGroups[0][1]
                    group2 = edgeSmoothingGroups[1][1]
                    backface1 = group1 & 0x8
                    backface2 = group2 & 0x8
                    if backface1 != backface2:
                        bpy_mesh.edges[edgeIndex].use_edge_sharp = True
                    else:
                        if backface1:
                            edgeFlagIndex1 = (4 - edge1) % 3
                        else:
                            edgeFlagIndex1 = edge1
                        edgeSharp1 = group1 & edgeFlags[edgeFlagIndex1]
                        if backface2:
                            edgeFlagIndex2 = (4 - edge2) % 3
                        else:
                            edgeFlagIndex2 = edge2
                        edgeSharp2 = group2 & edgeFlags[edgeFlagIndex2]
                        if edgeSharp1 or edgeSharp2:
                            bpy_mesh.edges[edgeIndex].use_edge_sharp = True


def append_materials(mesh, meshMaterials, bpy_materials):
    for materialName in meshMaterials:
        for bpyMaterialName in bpy_materials:
            if bpyMaterialName == materialName:
                mesh.materials.append(bpy_materials[materialName])


def assign_materials(meshMaterials, meshData, object):
    for materialID, materialName in enumerate(meshMaterials):
        for triangleID in meshData.materials[materialName]:
            object.data.polygons[triangleID].material_index = materialID
            image = object.material_slots[materialID].material.texture_slots[0].texture.image
            object.data.uv_textures[meshData.uv_map_name].data[triangleID].image = image


def load_vertex_weights(meshData, object, armatureObject):
    object.modifiers.new(name='Armature', type='ARMATURE')
    object.modifiers['Armature'].object = armatureObject
    for vertexGroupsName, weights, weightVertices in zip(meshData.vertex_groups_names, meshData.weights, meshData.weight_vertices):
        vertexGroup = object.vertex_groups.new(vertexGroupsName.lower())
        for weight, weightVertex in zip(weights, weightVertices):
            vertexGroup.add([weightVertex, ], weight, 'REPLACE')


def create_mesh(so, bpy_materials, meshID, armatureObject):
    meshData = so.meshes[meshID]
    mesh = bpy.data.meshes.new(meshData.name)
    object = bpy.data.objects.new(so.name, mesh)
    mesh.from_pydata(meshData.vertices, (), meshData.triangles)
    mesh.auto_smooth_angle = math.pi
    create_smoothing_groups(meshData, mesh, so.context.smoothing_groups_type)
    if armatureObject:
        load_vertex_weights(meshData, object, armatureObject)
    mesh.uv_textures.new(meshData.uv_map_name)
    UVLayerData = mesh.uv_layers[meshData.uv_map_name].data
    for uvIndex, (U, V) in enumerate(meshData.uvs):
        UVLayerData[uvIndex].uv = (U, V)
    meshMaterials = list(meshData.materials.keys())
    meshMaterials.sort()
    append_materials(mesh, meshMaterials, bpy_materials)
    assign_materials(meshMaterials, meshData, object)
    mesh.stalker.version = meshData.version
    mesh.stalker.flag_visible = meshData.flags.visible
    mesh.stalker.flag_locked = meshData.flags.locked
    mesh.stalker.flag_smooth_group_mask = meshData.flags.smooth_group_mask
    mesh.stalker.option_1 = meshData.option_1
    mesh.stalker.option_2 = meshData.option_2
    bpy.context.scene.objects.link(object)
    return object


def import_object(so):
    armatureObject = None
    if len(so.skelet.bones):
        import mathutils
        __matrix_bone = mathutils.Matrix(((1.0, 0.0, 0.0, 0.0), (0.0, 0.0, -1.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        __matrix_bone_inv = __matrix_bone.inverted()
        armature = bpy.data.armatures.new(so.name + '_armature')
        armature.draw_type = 'STICK'
        armatureObject = bpy.data.objects.new(so.name + '_skelet', armature)
        armatureObject.show_x_ray = True
        bpy.context.scene.objects.link(armatureObject)
        bpy.context.scene.objects.active = armatureObject
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in so.skelet.bones:
            bpyBone = armature.edit_bones.new(bone.name)
            mr = mathutils.Euler((-bone.rotation[0], -bone.rotation[1], -bone.rotation[2]), 'YXZ').to_matrix().to_4x4()
            mat = mathutils.Matrix.Translation(bone.position) * mr * __matrix_bone
            if bone.parent:
                bpyBone.parent = armature.edit_bones[bone.parent]
                mat = bpyBone.parent.matrix * __matrix_bone_inv * mat
            bpyBone.tail.y = 0.01
            bpyBone.matrix = mat
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy_materials = create_materials(so)
    if len(so.meshes) == 1:
        mesh = create_mesh(so, bpy_materials, 0, armatureObject)
        if not armatureObject:
            root_object = mesh
        else:
            root_object = bpy.data.objects.new(so.name, None)
            mesh.parent = root_object
            armatureObject.parent = root_object
            bpy.context.scene.objects.link(root_object)
    elif len(so.meshes) > 1:
        meshes = []
        for meshID in range(len(so.meshes)):
            meshes.append(create_mesh(so, bpy_materials, meshID, armatureObject))
        root_object = bpy.data.objects.new(so.name, None)
        bpy.context.scene.objects.link(root_object)
        for mesh in meshes:
            mesh.parent = root_object
    root_object.stalker.object_type = so.object_type
    root_object.stalker.flagDynamic = so.flags.dynamic
    root_object.stalker.flagProgressive = so.flags.progressive
    root_object.stalker.flagUsingLOD = so.flags.using_lod
    root_object.stalker.flagHOM = so.flags.hom
    root_object.stalker.flagMultipleUsage = so.flags.multiple_usage
    root_object.stalker.flagSoundOccluder = so.flags.sound_occluder
    root_object.stalker.version = so.version
    root_object.stalker.user_data = so.user_data
    root_object.location = so.position
    root_object.rotation_euler = so.rotation
    root_object.stalker.creator = so.creator
    root_object.stalker.create_time = so.create_time
    root_object.stalker.editor = so.editor
    root_object.stalker.edit_time = so.edit_time
    root_object.stalker.motion_reference = so.motion_reference
    root_object.stalker.lod_reference = so.lod_reference
