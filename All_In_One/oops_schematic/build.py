
import os

import bpy

from . import nodes
from . import select
from .constants import *


def build_schematic_scene():
    has_node_editor = False
    for area in bpy.context.window.screen.areas:
        if area.type == 'NODE_EDITOR':
            has_node_editor = True
            if not area.spaces[0].tree_type == 'OopsSchematic':
                return

    if not has_node_editor:
        return

    s = bpy.context.window_manager.oops_schematic    # s - schematic
    schematic_nodes = {
        'Library': [],
        'Scene': [],
        'Object': [],
        'Mesh': [],
        'Camera': [],
        'Lamp': [],
        'Curve': [],
        'Surface': [],
        'Metaball': [],
        'Text': [],
        'Armature': [],
        'Lattice': [],
        'Speaker': [],
        'Force Field': [],
        'Material': [],
        'Texture': [],
        'Image': [],
        'World': []
    }
    blend_file = nodes.SchematicNode(
        'Blend File: {}'.format(os.path.basename(bpy.data.filepath)),
        list(s.color_blend_file_nodes),
        0,
        'BLEND_FILE',
        data=bpy.context.window_manager
    )
    if s.show_libraries:
        libraries_nodes = {None: blend_file}
        schematic_nodes['Library'].append(blend_file)

    scenes_nodes = {library.name: {} for library in bpy.data.libraries}
    scenes_nodes[None] = {}

    worlds_nodes = {library.name: {} for library in bpy.data.libraries}
    worlds_nodes[None] = {}

    objects_nodes = {library.name: {} for library in bpy.data.libraries}
    objects_nodes[None] = {}

    meshes_nodes = {library.name: {} for library in bpy.data.libraries}
    meshes_nodes[None] = {}

    cameras_nodes = {library.name: {} for library in bpy.data.libraries}
    cameras_nodes[None] = {}

    lamps_nodes = {library.name: {} for library in bpy.data.libraries}
    lamps_nodes[None] = {}

    materials_nodes = {library.name: {} for library in bpy.data.libraries}
    materials_nodes[None] = {}

    textures_nodes = {library.name: {} for library in bpy.data.libraries}
    textures_nodes[None] = {}

    images_nodes = {library.name: {} for library in bpy.data.libraries}
    images_nodes[None] = {}

    # Generate libraries nodes
    if s.show_libraries:
        for library_index, library in enumerate(bpy.data.libraries):
            library_node = nodes.SchematicNode('{}: {}'.format(library.name, os.path.basename(library.filepath.replace('//', ''))), list(s.color_libraries_nodes), library_index + 1, 'LIBRARY', data=library)
            libraries_nodes[library.name] = library_node
            schematic_nodes['Library'].append(library_node)

    # Generate images nodes
    if s.show_images:
        for image_index, image in enumerate(bpy.data.images):
            image_node = nodes.SchematicNode(image.name, list(s.color_images_nodes), image_index, 'IMAGE', data=image)
            library_name = getattr(image.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                image_node.parents.append(library_node)
                library_node.children.append(image_node)
            images_nodes[library_name][image.name] = image_node
            schematic_nodes['Image'].append(image_node)

    # Generate textures nodes
    if s.show_textures:
        for texture_index, texture in enumerate(bpy.data.textures):
            texture_node = nodes.SchematicNode(texture.name, list(s.color_textures_nodes), texture_index, 'TEXTURE', data=texture)
            library_name = getattr(texture.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                texture_node.parents.append(library_node)
                library_node.children.append(texture_node)

            # Assign Children and Parents
            if texture.type == 'IMAGE':
                image = texture.image
                if image:
                    image_node = images_nodes.get(getattr(image.library, 'name', None)).get(image.name, None)
                    if image_node:
                        image_node.parents.append(texture_node)
                        texture_node.children.append(image_node)

            schematic_nodes['Texture'].append(texture_node)
            textures_nodes[library_name][texture.name] = texture_node

    # Generate materials nodes
    if s.show_materials:
        for material_index, material in enumerate(bpy.data.materials):
            material_node = nodes.SchematicNode(material.name, list(s.color_materials_nodes), material_index, 'MATERIAL', data=material)
            library_name = getattr(material.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                material_node.parents.append(library_node)
                library_node.children.append(material_node)

            # Assign Children and Parents
            for texture_slot in material.texture_slots:
                if texture_slot:
                    texture = texture_slot.texture
                    texture_node = textures_nodes.get(getattr(texture.library, 'name', None)).get(texture.name, None)
                    if texture_node:
                        texture_node.parents.append(material_node)
                        material_node.children.append(texture_node)
            # Assign Images
            if s.show_images:
                node_tree = material.node_tree
                if node_tree:
                    for node in node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if image:
                                image_node = images_nodes.get(getattr(image.library, 'name', None)).get(image.name, None)
                                if image_node:
                                    image_node.parents.append(material_node)
                                    material_node.children.append(image_node)
            # Assign Textures
            if s.show_textures:
                node_tree = material.node_tree
                if node_tree:
                    for node in node_tree.nodes:
                        if node.type == 'TEXTURE':
                            texture = node.texture
                            if texture:
                                texture_node = textures_nodes.get(getattr(texture.library, 'name', None)).get(texture.name, None)
                                if texture_node:
                                    texture_node.parents.append(material_node)
                                    material_node.children.append(texture_node)
    
            schematic_nodes['Material'].append(material_node)
            materials_nodes[library_name][material.name] = material_node

    # Generate meshes nodes
    if s.show_meshes:
        for mesh_index, mesh in enumerate(bpy.data.meshes):
            mesh_node = nodes.SchematicNode(mesh.name, list(s.color_meshes_nodes), mesh_index, 'MESH', data=mesh)
            library_name = getattr(mesh.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                mesh_node.parents.append(library_node)
                library_node.children.append(mesh_node)
            # Assign Children and Parents
            for material in mesh.materials:
                if material:
                    material_node = materials_nodes.get(getattr(material.library, 'name', None)).get(material.name, None)
                    if material_node:
                        material_node.parents.append(mesh_node)
                        mesh_node.children.append(material_node)
            schematic_nodes['Mesh'].append(mesh_node)
            meshes_nodes[library_name][mesh.name] = mesh_node

    # Generate cameras nodes
    if s.show_cameras:
        for camera_index, camera in enumerate(bpy.data.cameras):
            camera_node = nodes.SchematicNode(camera.name, list(s.color_cameras_nodes), camera_index, 'CAMERA', data=camera)
            library_name = getattr(camera.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                camera_node.parents.append(library_node)
                library_node.children.append(camera_node)
            schematic_nodes['Camera'].append(camera_node)
            cameras_nodes[library_name][camera.name] = camera_node

    # Generate lamps nodes
    if s.show_lamps:
        for lamp_index, lamp in enumerate(bpy.data.lamps):
            lamp_node = nodes.SchematicNode(lamp.name, list(s.color_lamps_nodes), lamp_index, 'LAMP', data=lamp)
            library_name = getattr(lamp.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                lamp_node.parents.append(library_node)
                library_node.children.append(lamp_node)
            schematic_nodes['Camera'].append(lamp_node)
            lamps_nodes[library_name][lamp.name] = lamp_node

    # Generate objects nodes
    if s.show_objects:
        for object_index, object in enumerate(bpy.data.objects):
            object_node = nodes.SchematicNode(object.name, list(s.color_objects_nodes), object_index, 'OBJECT', data=object)

            # Assign Children and Parents
            if object.type == 'MESH':
                mesh_node = meshes_nodes.get(getattr(object.data.library, 'name', None)).get(object.data.name, None)
                if mesh_node:
                    mesh_node.parents.append(object_node)
                    object_node.children.append(mesh_node)
            elif object.type == 'CAMERA':
                camera_node = cameras_nodes.get(getattr(object.data.library, 'name', None)).get(object.data.name, None)
                if camera_node:
                    camera_node.parents.append(object_node)
                    object_node.children.append(camera_node)
            elif object.type == 'LAMP':
                lamp_node = lamps_nodes.get(getattr(object.data.library, 'name', None)).get(object.data.name, None)
                if lamp_node:
                    lamp_node.parents.append(object_node)
                    object_node.children.append(lamp_node)

            library_name = getattr(object.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                object_node.parents.append(library_node)
                library_node.children.append(object_node)

            objects_nodes[library_name][object.name] = object_node
            schematic_nodes['Object'].append(object_node)

    # Generate worlds nodes
    if s.show_worlds:
        for world_index, world in enumerate(bpy.data.worlds):
            world_node = nodes.SchematicNode(world.name, list(s.color_worlds_nodes), world_index, 'WORLD', data=world)
            library_name = getattr(world.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                world_node.parents.append(library_node)
                library_node.children.append(world_node)
            worlds_nodes[library_name][world.name] = world_node
            schematic_nodes['World'].append(world_node)

    # Generate scenes nodes
    if s.show_scenes:
        for scene_index, scene in enumerate(bpy.data.scenes):
            scene_node = nodes.SchematicNode(scene.name, list(s.color_scenes_nodes), scene_index, 'SCENE', data=scene)
            library_name = getattr(scene.library, 'name', None)
            if s.show_libraries:
                library_node = libraries_nodes[library_name]
                scene_node.parents.append(library_node)
                library_node.children.append(scene_node)
            for object in scene.objects:
                object_node = objects_nodes.get(getattr(object.library, 'name', None)).get(object.name, None)
                if object_node:
                    # Assign Children and Parent Links
                    for child in object.children:
                        child_library_name = getattr(child.library, 'name', None)
                        child_object_node = objects_nodes[child_library_name].get(child.name)
                        object_node.children.append(child_object_node)
                        child_object_node.parents.append(object_node)
                    scene_node.children.append(object_node)
                    object_node.parents.append(scene_node)
            world = scene.world
            if world:
                world_node = worlds_nodes.get(getattr(world.library, 'name', None)).get(world.name, None)
                if world_node:
                    scene_node.children.append(world_node)
                    world_node.parents.append(scene_node)
            schematic_nodes['Scene'].append(scene_node)
            scenes_nodes[library_name][scene.name] = scene_node

    for object in bpy.data.objects:
        # Select Object Node in 3D View
        if s.select_3d_view and object in bpy.context.selected_objects:
            object_node = objects_nodes.get(getattr(object.library, 'name', None)).get(object.name, None)
            object_node.active = True
            object_node.color[0] += LIGHT_ADD_COLOR
            object_node.color[1] += LIGHT_ADD_COLOR
            object_node.color[2] += LIGHT_ADD_COLOR
            object_node.border_select = True
            select.select_children(object_node)
            select.select_parents(object_node)

    nodes_keys = [
        'Library',
        'Scene',
        'Object',
        'Mesh',
        'Camera',
        'Lamp',
        'Curve',
        'Surface',
        'Metaball',
        'Text',
        'Armature',
        'Lattice',
        'Speaker',
        'Force Field',
        'Material',
        'Texture',
        'Image',
        'World'
    ]

    # Set Nodes Coordinates
    last_offset_x = 0
    last_offset_y = 0
    for node_key in nodes_keys:
        schematic_nodes_group = schematic_nodes[node_key]
        for schematic_node in schematic_nodes_group:
            if last_offset_x > s.tree_width:
                last_offset_x = 0
                last_offset_y += Y_DISTANCE
            schematic_node.offset_x = last_offset_x
            schematic_node.offset_y = last_offset_y
            if schematic_node.data:
                if schematic_node.data.oops_schematic.offset:
                    schematic_node.offset_x = schematic_node.data.oops_schematic.position_x
                    schematic_node.offset_y = schematic_node.data.oops_schematic.position_y
                else:
                    schematic_node.data.oops_schematic.position_x = last_offset_x
                    schematic_node.data.oops_schematic.position_y = last_offset_y
            # Select Node
            node_size_x = len(schematic_node.text) * CHAR_SIZE
            if not len(s.multi_click):
                schematic_node.data.oops_schematic.select = False
            for click in s.multi_click:
                if schematic_node.offset_x <= click.x <= (schematic_node.offset_x + node_size_x) and \
                        schematic_node.offset_y <= click.y <= (schematic_node.offset_y + NODE_HIGHT) and \
                        not s.select_3d_view:
                    if not schematic_node.active:
                        schematic_node.active = True
                        schematic_node.data.oops_schematic.select = True
                        schematic_node.color[0] += LIGHT_ADD_COLOR
                        schematic_node.color[1] += LIGHT_ADD_COLOR
                        schematic_node.color[2] += LIGHT_ADD_COLOR
                    if not schematic_node.border_select:
                        schematic_node.border_select = True
                        if s.grab_mode:
                            schematic_node.offset_x += s.move_offset_x
                            schematic_node.offset_y += s.move_offset_y
                        elif s.apply_location:
                            schematic_node.offset_x += s.move_offset_x
                            schematic_node.offset_y += s.move_offset_y
                            click.x += s.move_offset_x
                            click.y += s.move_offset_y
                            if schematic_node.data:
                                schematic_node.data.oops_schematic.offset = True
                                schematic_node.data.oops_schematic.position_x = schematic_node.offset_x
                                schematic_node.data.oops_schematic.position_y = schematic_node.offset_y
                    select.select_children(schematic_node)
                    select.select_parents(schematic_node)
            last_offset_x += node_size_x + X_DISTANCE
        last_offset_x = 0
        if schematic_nodes_group:
            last_offset_y += Y_DISTANCE

    s.apply_location = False

    # Draw nodes

    for node_key in nodes_keys:
        schematic_nodes_group = schematic_nodes[node_key]
        for schematic_node in schematic_nodes_group:
            schematic_node.draw_lines()

    for node_key in nodes_keys:
        schematic_nodes_group = schematic_nodes[node_key]
        for schematic_node in schematic_nodes_group:
            schematic_node.draw_box()

    for node_key in nodes_keys:
        schematic_nodes_group = schematic_nodes[node_key]
        for schematic_node in schematic_nodes_group:
            schematic_node.draw_text()
