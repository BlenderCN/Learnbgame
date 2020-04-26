import bpy
import os
import mathutils
import bmesh
import math
import subprocess

from . import export_mesh
from . import export_nav

def calc_aabb(obj):
    bbox = []
    bbox.append(mathutils.Vector((obj.bound_box[0][0],obj.bound_box[0][1],obj.bound_box[0][2])))
    bbox.append(mathutils.Vector((obj.bound_box[1][0],obj.bound_box[1][1],obj.bound_box[1][2])))
    bbox.append(mathutils.Vector((obj.bound_box[2][0],obj.bound_box[2][1],obj.bound_box[2][2])))
    bbox.append(mathutils.Vector((obj.bound_box[3][0],obj.bound_box[3][1],obj.bound_box[3][2])))
    bbox.append(mathutils.Vector((obj.bound_box[4][0],obj.bound_box[4][1],obj.bound_box[4][2])))
    bbox.append(mathutils.Vector((obj.bound_box[5][0],obj.bound_box[5][1],obj.bound_box[5][2])))
    bbox.append(mathutils.Vector((obj.bound_box[6][0],obj.bound_box[6][1],obj.bound_box[6][2])))
    bbox.append(mathutils.Vector((obj.bound_box[7][0],obj.bound_box[7][1],obj.bound_box[7][2])))

    bbox = [obj.matrix_world * vert for vert in bbox]

    x = [v[0] for v in bbox]
    y = [v[1] for v in bbox]
    z = [v[2] for v in bbox]

    min_vec = (min(x), min(y), min(z))
    max_vec = (max(x), max(y), max(z))
    
    return (min_vec, max_vec)

def chunk_lightmap(mesh, chunk_index, directory):
    img_name = mesh.name + ".png"

    map_size = 512
    bpy.ops.image.new(name=img_name, width=map_size, height=map_size, color=(0.5, 0.5, 0.5, 1.0), alpha=False)
    img = bpy.data.images[img_name]

    mesh.data.uv_textures['lightmap'].active = True

    bpy.ops.object.mode_set(mode='OBJECT')

    for d in mesh.data.uv_textures['lightmap'].data:
        d.image = img

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.object.bake_image()
    img.filepath_raw = os.path.join(directory, img_name)
    img.file_format = 'PNG'
    img.save()
    bpy.ops.object.mode_set(mode='OBJECT')

    compress_name = mesh.name + ".pvr"

    compress_command = ['xcrun', '--sdk', 'iphoneos', 'texturetool', '-e', 'PVRTC', '--channel-weighting-linear', '-m', '--bits-per-pixel-4', '-f', 'pvr']
    compress_inputs = [img.filepath_raw, '-o', os.path.join(directory, compress_name)]
    subprocess.call(compress_command + compress_inputs)
    os.remove(img.filepath_raw)

def join_chunk(obj_list):
    for object in obj_list:
        if object.type == 'MESH':
            object.select=True
            bpy.context.scene.objects.active = object
        else:
            object.select=False

    bpy.ops.object.duplicate()
    bpy.ops.object.join()

    for object in obj_list:
        object.hide_render=True
        object.hide=True

    chunk_mesh = bpy.context.scene.objects.active
    chunk_mesh.hide_render=False
    chunk_mesh.hide=False

    return chunk_mesh

def export(filepath):
    file_version = 2

    directory = os.path.dirname(os.path.abspath(filepath))
    scene = bpy.context.scene

    bpy.ops.ed.undo_push(message="Lightmap undo")

    bpy.context.scene.render.image_settings.compression = 100
    bpy.context.scene.render.bake_margin = 6

    for chunk_index, group in enumerate(bpy.data.groups):
        chunk_mesh = join_chunk(list(group.objects))
        chunk_mesh.name = "chunk%i" % chunk_index
        chunk_mesh['chunk'] = 1

        bpy.ops.mesh.uv_texture_add()

        chunk_mesh.data.uv_textures[0].name = "diffuse"
        chunk_mesh.data.uv_textures[1].name = "lightmap"

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # cleanup mesh by removing doubles
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()

        # triangulate faces
        bpy.ops.object.mode_set(mode='OBJECT')
        me = chunk_mesh.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
        bm.to_mesh(me)
        bm.free()

        # do an edge split
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        modifier = bpy.context.object.modifiers["EdgeSplit"]
        modifier.use_edge_angle = True
        modifier.use_edge_sharp = True
        modifier.split_angle = math.pi * 0.5
        bpy.ops.object.modifier_apply(modifier='EdgeSplit')

        # uv mapping
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=70.0, island_margin=0.4, user_area_weight=0.4)
        #bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_MARGIN_DIV=0.5, PREF_BOX_DIV=46)

        bpy.ops.object.mode_set(mode='OBJECT')
        chunk_lightmap(chunk_mesh, chunk_index, directory)
        chunk_mesh.select=False
        bpy.context.scene.objects.active = None
    
    chunk_index = 0

    file = open(filepath, "w")
    file.write("version: %i\n" % file_version)

    if 'data_path' in scene:
        data_path = scene['data_path']

    if 'atlas' in scene:
        file.write("atlas: %s\n" % scene['atlas'])

    if 'skulls' in scene:
        file.write('skulls: %i\n' % scene['skulls'])

    nav_filename = "main.nav"
    file.write("nav: %s\n" % (data_path + nav_filename))

    for obj in scene.objects:
        if obj.type == 'LAMP' and not 'static' in obj:
            lamp = obj.data

            forward = obj.matrix_world.to_3x3() * mathutils.Vector((0.0, 0.0, -1.0))

            point_string = "[%f, %f, %f]" % (obj.location[0], obj.location[1], obj.location[2])
            forward_string = "[%f, %f, %f]" % (forward[0], forward[1], forward[2])

            color_string = "[%f, %f, %f]" % (lamp.color[0], lamp.color[1], lamp.color[2])

            file.write("light: %f %f %s %s %s\n" % (lamp.distance, lamp.spot_size / 2.0, point_string, forward_string, color_string))
        elif obj.type == 'MESH' and 'chunk' in obj:
            chunk_filename = obj.name + ".bmesh"

            chunk_path = os.path.join(directory, chunk_filename)
            export_mesh.export_binary(obj, chunk_path)

            min_vec, max_vec = calc_aabb(obj)

            min_string = "[%f, %f, %f]" % (min_vec[0], min_vec[1], min_vec[2])
            max_string = "[%f, %f, %f]" % (max_vec[0], max_vec[1], max_vec[2])

            chunk_data = (
                chunk_index,
                data_path + chunk_filename,
                data_path + obj.name + ".pvr",
                min_string,
                max_string
            )

            file.write("chunk %i: %s %s %s %s\n" % chunk_data)
            chunk_index += 1
        elif obj.type == 'MESH' and 'nav' in obj:
            export_path = os.path.join(directory, nav_filename)
            export_nav.export(obj, export_path)
        elif (obj.type == 'MESH' or obj.type =='EMPTY') and 'prop' in obj:
            min_vec, max_vec = calc_aabb(obj)
            
            flags = obj.get('flags', 0)

            point_string = "[%f, %f, %f]" % (obj.location[0], obj.location[1], obj.location[2])
            rot_string = "[%f, %f, %f]" % (obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2])

            min_string = "[%f, %f, %f]" % (min_vec[0], min_vec[1], min_vec[2])
            max_string = "[%f, %f, %f]" % (max_vec[0], max_vec[1], max_vec[2])

            prop_data = (
                obj['prop'],
                obj.name,
                flags,
                point_string,
                rot_string,
                min_string,
                max_string
            )

            file.write("prop: %s %s %i %s %s %s %s\n" % prop_data)

            for event in obj.events:
                file.write(".event: %s %s %s %i\n" % (event.event, event.target, event.action, event.data))

            for prop_name in obj.keys():
                if prop_name not in '_RNA_UI' and not prop_name == 'prop':
                    file.write('.var: %s %s\n' % (prop_name, obj[prop_name]))    
    file.close()
