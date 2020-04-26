
import os

import bpy
import bmesh
import mathutils

from . import format_

from io_scene_xray import utils


def create_material(level, texture, shader):
    bpy_material = bpy.data.materials.new(texture.shader)
    bpy_material.use_shadeless = True
    bpy_material.use_transparency = True
    bpy_material.alpha = 0.0
    bpy_material.xray.eshader = shader.shader
    level.bpy_materials[texture.shader] = bpy_material
    bpy_tex = bpy.data.textures.new(texture.shader, type='IMAGE')
    bpy_tex.type = 'IMAGE'
    bpy_texture_slot = bpy_material.texture_slots.add()
    bpy_texture_slot.texture = bpy_tex
    bpy_texture_slot.use_map_alpha = True
    bpy_texture_slot.uv_layer = 'Texture'
    textures_folder = bpy.context.user_preferences.addons['io_scene_xray'].preferences.textures_folder_auto
    abs_image_path = os.path.join(textures_folder, texture.shader + '.dds')
    try:
        bpy_image = bpy.data.images.load(abs_image_path)
    except RuntimeError:
        abs_image_path = os.path.join(os.path.dirname(level.file_path), texture.shader + '.dds')
        try:
            bpy_image = bpy.data.images.load(abs_image_path)
        except RuntimeError:
            bpy_image = bpy.data.images.new(texture.shader, 0, 0)
            bpy_image.source = 'FILE'
            bpy_image.filepath = abs_image_path
    bpy_tex.image = bpy_image
    return bpy_material


def get_bpy_material(level, texture, shader):
    if not level.bpy_materials.get(texture.shader, None):
        bpy_material = create_material(level, texture, shader)
    else:
        bpy_material = level.bpy_materials[texture.shader]
        if bpy_material.xray.eshader != shader.shader:
            bpy_material = create_material(level, texture, shader)
    return bpy_material


def import_visuals(level):
    textures_folder = bpy.context.user_preferences.addons['io_scene_xray'].preferences.textures_folder_auto
    lmaps = set(level.lmaps)
    lmaps_0 = set(level.lmaps_0)
    lmaps_1 = set(level.lmaps_1)

    lmaps_textures = {}
    for lmap in lmaps:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_textures[lmap] = bpy_tex

    lmaps_0_textures = {}
    for lmap in lmaps_0:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_0_textures[lmap] = bpy_tex

    lmaps_1_textures = {}
    for lmap in lmaps_1:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_1_textures[lmap] = bpy_tex

    if level.format_version >= format_.XRLC_VERSION_12:
        bpy_materials = []
        bpy_materials.append(None)    # first empty shader
        for material_index, texture in enumerate(level.materials):
            lmap = level.lmaps[material_index]
            if level.format_version in {format_.XRLC_VERSION_13, format_.XRLC_VERSION_14}:
                if not lmap:
                    abs_image_path = os.path.join(textures_folder, texture + '.dds')
                else:
                    abs_image_path = os.path.join(os.path.dirname(level.file_path), texture + '.dds')
            else:
                abs_image_path = os.path.join(textures_folder, texture + '.dds')
            bpy_mat = bpy.data.materials.new(texture)
            bpy_mat.use_shadeless = True
            bpy_mat.use_transparency = True
            bpy_mat.alpha = 0.0
            bpy_tex = bpy.data.textures.new(texture, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            bpy_texture_slot = bpy_mat.texture_slots.add()
            bpy_texture_slot.texture = bpy_tex
            bpy_texture_slot.use_map_alpha = True
            bpy_texture_slot.uv_layer = 'Texture'

            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                if level.format_version <= format_.XRLC_VERSION_12:
                    abs_image_path = os.path.join(os.path.dirname(level.file_path), texture + '.dds')
                    try:
                        bpy_image = bpy.data.images.load(abs_image_path)
                    except RuntimeError:
                        bpy_image = bpy.data.images.new(texture, 0, 0)
                        bpy_image.source = 'FILE'
                        bpy_image.filepath = abs_image_path
                else:
                    bpy_image = bpy.data.images.new(texture, 0, 0)
                    bpy_image.source = 'FILE'
                    bpy_image.filepath = abs_image_path

            bpy_tex.image = bpy_image
            bpy_materials.append(bpy_mat)

            shader = level.shaders[material_index]
            if shader:
                bpy_mat.xray.eshader = shader
                bpy_mat.xray.version = utils.plugin_version_number()

            # Generate material nodes

            lmap_1 = level.lmaps_0[material_index]
            lmap_2 = level.lmaps_1[material_index]

            if (lmap_1 and lmap_2) or lmap:

                bpy_mat.use_nodes = True
                bpy_mat.texture_slots[0].use_map_color_diffuse = False
                bpy_mat.texture_slots[0].use_map_alpha = False
                node_tree = bpy_mat.node_tree

                output_node = node_tree.nodes['Output']
                output_node.location = (880.3516235351562, 375.3576965332031)
                output_node.select = False

                material_node = node_tree.nodes['Material']
                material_node.material = bpy_mat
                material_node.location = (685.1767578125, 421.38262939453125)
                material_node.select = False

                uv_lmap_node = node_tree.nodes.new('ShaderNodeGeometry')
                uv_lmap_node.name = 'UV Light Map'
                uv_lmap_node.label = 'UV Light Map'
                uv_lmap_node.uv_layer = 'Light_Map'
                uv_lmap_node.location = (-711.32177734375, -48.62998962402344)
                uv_lmap_node.select = False

                if lmap:
                    lmap_texture = lmaps_textures[lmap]

                    lmap_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                    lmap_texture_node.name = 'Light Map'
                    lmap_texture_node.label = 'Light Map'
                    lmap_texture_node.texture = lmap_texture
                    lmap_texture_node.location = (-461.5350341796875, -107.8274154663086)
                    lmap_texture_node.select = False

                if lmap_1 and lmap_2:
                    lmap_1_texture = lmaps_0_textures[lmap_1]

                    lmap_1_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                    lmap_1_texture_node.name = 'Light Map 1'
                    lmap_1_texture_node.label = 'Light Map 1'
                    lmap_1_texture_node.texture = lmap_1_texture
                    lmap_1_texture_node.location = (-461.5350341796875, -107.8274154663086)
                    lmap_1_texture_node.select = False

                    lmap_2_texture = lmaps_1_textures[lmap_2]

                    lmap_2_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                    lmap_2_texture_node.name = 'Light Map 2'
                    lmap_2_texture_node.label = 'Light Map 2'
                    lmap_2_texture_node.texture = lmap_2_texture
                    lmap_2_texture_node.location = (-460.4274597167969, 185.0209197998047)
                    lmap_2_texture_node.select = False

                uv_texture_node = node_tree.nodes.new('ShaderNodeGeometry')
                uv_texture_node.name = 'UV Texture'
                uv_texture_node.label = 'UV Texture'
                uv_texture_node.uv_layer = 'Texture'
                uv_texture_node.location = (-711.32177734375, 474.66326904296875)
                uv_texture_node.select = False

                texture_node = node_tree.nodes.new('ShaderNodeTexture')
                texture_node.name = 'Texture'
                texture_node.label = 'Texture'
                texture_node.texture = bpy_tex
                texture_node.location = (-461.5350341796875, 474.66326904296875)
                texture_node.select = False

                hemi_light_node = node_tree.nodes.new('ShaderNodeMixRGB')
                hemi_light_node.name = 'Hemi + Light'
                hemi_light_node.label = 'Hemi + Light'
                hemi_light_node.inputs['Fac'].default_value = 1.0
                hemi_light_node.blend_type = 'ADD'
                hemi_light_node.location = (-190.5177764892578, 63.71351623535156)
                hemi_light_node.select = False

                sun_node = node_tree.nodes.new('ShaderNodeMixRGB')
                sun_node.name = '+ Sun'
                sun_node.label = '+ Sun'
                sun_node.inputs['Fac'].default_value = 1.0
                sun_node.blend_type = 'ADD'
                sun_node.location = (10.250570297241211, 16.821426391601562)
                sun_node.select = False

                ambient_node = node_tree.nodes.new('ShaderNodeMixRGB')
                ambient_node.name = '+ Ambient'
                ambient_node.label = '+ Ambient'
                ambient_node.inputs['Fac'].default_value = 1.0
                ambient_node.inputs['Color2'].default_value = (0.05, 0.05, 0.05, 1.0)
                ambient_node.blend_type = 'ADD'
                ambient_node.location = (210.250570297241211, 16.821426391601562)
                ambient_node.select = False

                light_maps_node = node_tree.nodes.new('ShaderNodeMixRGB')
                light_maps_node.name = 'Light Maps'
                light_maps_node.label = 'Light Maps'
                light_maps_node.inputs['Fac'].default_value = 1.0
                light_maps_node.blend_type = 'MULTIPLY'
                light_maps_node.location = (493.79037475585938, 164.41893005371094)
                light_maps_node.select = False

                # Generate node links
                if lmap:
                    node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_texture_node.inputs['Vector'])
                    node_tree.links.new(texture_node.outputs['Value'], hemi_light_node.inputs['Color1'])
                    node_tree.links.new(lmap_texture_node.outputs['Color'], hemi_light_node.inputs['Color2'])
                    node_tree.links.new(lmap_texture_node.outputs['Value'], sun_node.inputs['Color2'])
                if lmap_1:
                    node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_1_texture_node.inputs['Vector'])
                    node_tree.links.new(lmap_1_texture_node.outputs['Color'], hemi_light_node.inputs['Color2'])
                    node_tree.links.new(lmap_1_texture_node.outputs['Value'], sun_node.inputs['Color2'])
                    node_tree.links.new(texture_node.outputs['Value'], output_node.inputs['Alpha'])
                if lmap_2:
                    node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_2_texture_node.inputs['Vector'])
                    node_tree.links.new(lmap_2_texture_node.outputs['Color'], hemi_light_node.inputs['Color1'])
                node_tree.links.new(hemi_light_node.outputs['Color'], sun_node.inputs['Color1'])
                node_tree.links.new(uv_texture_node.outputs['UV'], texture_node.inputs['Vector'])
                node_tree.links.new(sun_node.outputs['Color'], ambient_node.inputs['Color1'])
                node_tree.links.new(texture_node.outputs['Color'], light_maps_node.inputs['Color1'])
                node_tree.links.new(ambient_node.outputs['Color'], light_maps_node.inputs['Color2'])
                node_tree.links.new(light_maps_node.outputs['Color'], material_node.inputs['Color'])

    # Import meshes
    loaded_visuals = {}
    imported_visuals_names = {}
    level.bpy_materials = {}
    for visual_index, visual in enumerate(level.visuals):
        if visual.gcontainer:
            visual_key = '{0},{1},{2},{3},{4},{5}'.format(
                visual.gcontainer.vb_index,
                visual.gcontainer.vb_offset,
                visual.gcontainer.vb_size,
                visual.gcontainer.ib_index,
                visual.gcontainer.ib_offset,
                visual.gcontainer.ib_size
            )
            bpy_mesh_name = loaded_visuals.get(visual_key)
            if not bpy_mesh_name:
                b_mesh = bmesh.new()
                bpy_mesh = bpy.data.meshes.new(visual.type)
                if level.format_version >= format_.XRLC_VERSION_12:
                    bpy_mat = bpy_materials[visual.shader_id]
                else:
                    texture = level.shaders[visual.texture_l]
                    shader = level.shaders[visual.shader_l]
                    bpy_mat = get_bpy_material(level, texture, shader)
                bpy_tex = bpy_mat.texture_slots[0].texture
                bpy_mesh.materials.append(bpy_mat)

                vertex_buffer = level.vertex_buffers[visual.gcontainer.vb_index]
                vertices = vertex_buffer.position[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                uvs = vertex_buffer.uv[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                uvs_lmap = vertex_buffer.uv_lmap[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                colors_light = vertex_buffer.colors_light[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                colors_sun = vertex_buffer.colors_sun[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                for vertex in vertices:
                    b_mesh.verts.new((vertex[0], vertex[1], vertex[2]))
                b_mesh.verts.ensure_lookup_table()

                indices_buffer = level.indices_buffers[visual.gcontainer.ib_index]
                indices = indices_buffer[visual.gcontainer.ib_offset : visual.gcontainer.ib_offset + visual.gcontainer.ib_size]

                if not visual.swi_index is None:
                    visual.swidata = level.swis_buffers[visual.swi_index]

                if visual.swidata:
                    indices = indices[visual.swidata[0].offset : ]

                for i in range(0, len(indices), 3):
                    v1 = b_mesh.verts[indices[i]]
                    v2 = b_mesh.verts[indices[i + 2]]
                    v3 = b_mesh.verts[indices[i + 1]]
                    try:
                        face = b_mesh.faces.new((v1, v2, v3))
                        face.smooth = True
                    except ValueError:
                        pass
                b_mesh.faces.ensure_lookup_table()

                b_mesh.normal_update()

                uv_layer = b_mesh.loops.layers.uv.new('Texture')
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = uvs[loop.vert.index]

                if uvs_lmap:
                    uv_layer = b_mesh.loops.layers.uv.new('Light_Map')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            loop[uv_layer].uv = uvs_lmap[loop.vert.index]

                if colors_light:
                    color_layer = b_mesh.loops.layers.color.new('Light')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            bmesh_color = loop[color_layer]
                            color = colors_light[loop.vert.index]
                            bmesh_color.r = color[0]
                            bmesh_color.g = color[1]
                            bmesh_color.b = color[2]

                if colors_sun:
                    color_layer = b_mesh.loops.layers.color.new('Sun')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            bmesh_color = loop[color_layer]
                            color = colors_sun[loop.vert.index]
                            bmesh_color.r = color
                            bmesh_color.g = color
                            bmesh_color.b = color

                if colors_light and not bpy_mat.use_nodes:

                    bpy_mat.use_nodes = True
                    bpy_mat.texture_slots[0].use_map_color_diffuse = False
                    bpy_mat.texture_slots[0].use_map_alpha = False
                    node_tree = bpy_mat.node_tree

                    output_node = node_tree.nodes['Output']
                    output_node.location = (880.3516235351562, 375.3576965332031)
                    output_node.select = False

                    material_node = node_tree.nodes['Material']
                    material_node.material = bpy_mat
                    material_node.location = (685.1767578125, 421.38262939453125)
                    material_node.select = False

                    light_node = node_tree.nodes.new('ShaderNodeGeometry')
                    light_node.name = 'Light'
                    light_node.label = 'Light'
                    light_node.color_layer = 'Light'
                    light_node.location = (-111.93138122558594, 269.0376892089844)
                    light_node.select = False

                    sun_node = node_tree.nodes.new('ShaderNodeGeometry')
                    sun_node.name = 'Sun'
                    sun_node.label = 'Sun'
                    sun_node.color_layer = 'Sun'
                    sun_node.location = (-111.93138122558594, -15.771751403808594)
                    sun_node.select = False

                    uv_texture_node = node_tree.nodes.new('ShaderNodeGeometry')
                    uv_texture_node.name = 'UV Texture'
                    uv_texture_node.label = 'UV Texture'
                    uv_texture_node.uv_layer = 'Texture'
                    uv_texture_node.location = (-7.684539794921875, 624.1194458007812)
                    uv_texture_node.select = False

                    texture_node = node_tree.nodes.new('ShaderNodeTexture')
                    texture_node.name = 'Texture'
                    texture_node.label = 'Texture'
                    texture_node.texture = bpy_tex
                    texture_node.location = (215.8828887939453, 620.5947875976562)
                    texture_node.select = False

                    light_sun_node = node_tree.nodes.new('ShaderNodeMixRGB')
                    light_sun_node.name = 'Light + Sun'
                    light_sun_node.label = 'Light + Sun'
                    light_sun_node.inputs['Fac'].default_value = 1.0
                    light_sun_node.blend_type = 'ADD'
                    light_sun_node.location = (73.60041809082031, 134.22515869140625)
                    light_sun_node.select = False

                    ambient_node = node_tree.nodes.new('ShaderNodeMixRGB')
                    ambient_node.name = '+ Ambient'
                    ambient_node.label = '+ Ambient'
                    ambient_node.inputs['Fac'].default_value = 1.0
                    ambient_node.blend_type = 'ADD'
                    ambient_node.inputs['Color2'].default_value = (0.05, 0.05, 0.05, 1.0)
                    ambient_node.location = (259.86334228515625, 151.3456268310547)
                    ambient_node.select = False

                    vertex_colors_node = node_tree.nodes.new('ShaderNodeMixRGB')
                    vertex_colors_node.name = 'Vertex Colors'
                    vertex_colors_node.label = 'Vertex Colors'
                    vertex_colors_node.inputs['Fac'].default_value = 1.0
                    vertex_colors_node.blend_type = 'MULTIPLY'
                    vertex_colors_node.location = (465.1767578125, 220.51089477539062)
                    vertex_colors_node.select = False

                    # Generate links
                    node_tree.links.new(texture_node.outputs['Value'], output_node.inputs['Alpha'])
                    node_tree.links.new(texture_node.outputs['Color'], vertex_colors_node.inputs['Color1'])
                    node_tree.links.new(vertex_colors_node.outputs['Color'], material_node.inputs['Color'])
                    node_tree.links.new(ambient_node.outputs['Color'], vertex_colors_node.inputs['Color2'])
                    node_tree.links.new(uv_texture_node.outputs['UV'], texture_node.inputs['Vector'])
                    node_tree.links.new(light_sun_node.outputs['Color'], ambient_node.inputs['Color1'])
                    node_tree.links.new(light_node.outputs['Vertex Color'], light_sun_node.inputs['Color1'])
                    node_tree.links.new(sun_node.outputs['Vertex Color'], light_sun_node.inputs['Color2'])

                b_mesh.to_mesh(bpy_mesh)
                loaded_visuals[visual_key] = bpy_mesh.name

            else:
                bpy_mesh = bpy.data.meshes[bpy_mesh_name]

            bpy_object = bpy.data.objects.new(visual.type, bpy_mesh)
            bpy.context.scene.objects.link(bpy_object)
            imported_visuals_names[visual_index] = bpy_object.name

            if visual.tree_xform:
                t = visual.tree_xform
                transform_matrix = mathutils.Matrix((
                    (t[0], t[1], t[2], t[3]),
                    (t[4], t[5], t[6], t[7]),
                    (t[8], t[9], t[10], t[11]),
                    (t[12], t[13], t[14], t[15])
                    ))
                transform_matrix.transpose()
                translate, rotate, scale = transform_matrix.decompose()
                bpy_object.location = translate[0], translate[2], translate[1]
                bpy_object.scale = scale[0], scale[2], scale[1]
                rotate = rotate.to_euler('ZXY')
                bpy_object.rotation_euler = -rotate[0], -rotate[2], -rotate[1]

            # import fast path geometry
            if visual.fastpath and level.has_geomx:
                b_mesh = bmesh.new()
                bpy_mesh = bpy.data.meshes.new('FASTPATH')

                vertex_buffer = level.fastpath.vertex_buffers[visual.fastpath.gcontainer.vb_index]
                vertices = vertex_buffer.position[visual.fastpath.gcontainer.vb_offset : visual.fastpath.gcontainer.vb_offset + visual.fastpath.gcontainer.vb_size]

                for vertex in vertices:
                    b_mesh.verts.new((vertex[0], vertex[1], vertex[2]))
                b_mesh.verts.ensure_lookup_table()

                indices_buffer = level.fastpath.indices_buffers[visual.fastpath.gcontainer.ib_index]
                indices = indices_buffer[visual.fastpath.gcontainer.ib_offset : visual.fastpath.gcontainer.ib_offset + visual.fastpath.gcontainer.ib_size]

                if visual.fastpath.swidata:
                    indices = indices[visual.fastpath.swidata[0].offset : ]

                for i in range(0, len(indices), 3):
                    v1 = b_mesh.verts[indices[i]]
                    v2 = b_mesh.verts[indices[i + 2]]
                    v3 = b_mesh.verts[indices[i + 1]]
                    try:
                        face = b_mesh.faces.new((v1, v2, v3))
                        face.smooth = True
                    except ValueError:
                        pass

                b_mesh.faces.ensure_lookup_table()
                b_mesh.normal_update()

                b_mesh.to_mesh(bpy_mesh)
                bpy_object_fastpath = bpy.data.objects.new('FASTPATH', bpy_mesh)
                bpy_object_fastpath.show_wire = True
                bpy_object_fastpath.show_all_edges = True
                bpy_object_fastpath.draw_type = 'WIRE'
                bpy.context.scene.objects.link(bpy_object_fastpath)
                bpy_object_fastpath.parent = bpy_object

        else:
            bpy_object = bpy.data.objects.new(visual.type, None)
            bpy.context.scene.objects.link(bpy_object)
            if visual.type == 'LOD':
                bpy_object.empty_draw_size = 3.0
                bpy_object.empty_draw_type = 'SPHERE'
            imported_visuals_names[visual_index] = bpy_object.name
            for child in visual.children_l:
                bpy_child_object = bpy.data.objects[imported_visuals_names[child]]
                if visual.type == 'LOD':
                    bpy_object.location = bpy_child_object.location
                    bpy_object.rotation_euler = bpy_child_object.rotation_euler
                    bpy_object.scale = bpy_child_object.scale
                    bpy_child_object.location = 0, 0, 0
                    bpy_child_object.rotation_euler = 0, 0, 0
                    bpy_child_object.scale = 1, 1, 1
                bpy_child_object.parent = bpy_object

    root_level_object = bpy.data.objects.new('level', None)
    bpy.context.scene.objects.link(root_level_object)
    root_sectors_object = bpy.data.objects.new('sectors', None)
    bpy.context.scene.objects.link(root_sectors_object)
    root_sectors_object.parent = root_level_object

    max_portal_count = max(level.sectors, key=lambda sector: sector.portal_count).portal_count
    sector_index = 0
    for sector in level.sectors:
        if sector.portal_count == max_portal_count:
            sector_object_name = 'sector_default'
        else:
            sector_object_name = 'sector_{0:0>3}'.format(sector_index)
            sector_index += 1
        bpy_object = bpy.data.objects.new(sector_object_name, None)
        bpy.context.scene.objects.link(bpy_object)
        bpy_object.parent = root_sectors_object
        root_bpy_object = bpy.data.objects[imported_visuals_names[sector.root]]
        root_bpy_object.parent = bpy_object
