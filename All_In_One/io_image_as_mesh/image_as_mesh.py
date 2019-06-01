import bpy
import bmesh
from itertools import *
from io_image_as_mesh.rdp import rdp
from io_image_as_mesh.marching_squares import create_polygon


def create_mesh_from_image(img):
    pixels = img.pixels
    data = []

    # creates an array with info, if pixels are transparent
    # loop takes every 4th value from pixels, which is the
    # alpha value
    for alpha in islice(pixels, 3, None, 4):
        if alpha == 0:
            data.append(0)
        else:
            data.append(1)

    # split array into rows
    w = img.size[0]
    data = [data[n:n+w] for n in range(0, len(data), w)]

    # add border of empty pixels
    for row in data:
        row.insert(0, 0)
        row.append(0)
    empty_row = [0] * (w + 2)
    data.insert(0, empty_row)
    data.append(empty_row)

    poly = rdp(create_polygon(data), 1.5)

    obj = create_sprite(poly, img)

    return obj


def create_sprite(poly, img):
    w = img.size[0]
    h = img.size[1]

    scene = bpy.context.scene

    points = []
    edges = []
    for i, p in enumerate(poly):
        points.append([p[0] / w - 0.5, 0, p[1] / h - 0.5])

        if i < len(poly) - 2:
            edges.append((i, i + 1))
        else:
            edges.append((i, 0))
    mesh_data = bpy.data.meshes.new("sprite_mesh")
    mesh_data.from_pydata(points, edges, [])
    mesh_data.update()

    obj = bpy.data.objects.new(img.name, mesh_data)
    scene.objects.link(obj)
    obj.select = True
    scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.index_update()

    bmesh.ops.triangle_fill(bm, edges=bm.edges[:], use_dissolve=False, use_beauty=True)

    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()

    uvtex = bm.faces.layers.tex.new("UVMap")
    uv_lay = bm.loops.layers.uv.new("UVMap")

    for face in bm.faces:
        face[uvtex].image = img
        for loop in face.loops:
            uv = loop[uv_lay].uv
            index = loop.vert.index
            v = bm.verts[index].co
            uv.x = v.x + 0.5
            uv.y = v.z + 0.5

    # scale image to size in inches
    dpi_x = img.resolution[0] / 39.3701
    dpi_y = img.resolution[1] / 39.3701

    for vert in bm.verts:
        v = vert.co
        v.x *= w / dpi_x
        v.z *= h / dpi_y
        vert.co = v

    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode='OBJECT')

    mat = create_blender_material(obj, img)
    create_cycles_material(mat, img)

    if scene.render.engine != 'CYCLES':
        mat.use_nodes = False

    return obj


def create_blender_material(obj, img):
    tex = bpy.data.textures.new('ColorTex', type='IMAGE')
    tex.image = img

    mat = bpy.data.materials.new(name="Material")
    mat.use_transparency = True
    mat.emit = 1.0
    mat.alpha = 0.0
    obj.data.materials.append(mat)

    texslot = mat.texture_slots.add()
    texslot.texture = tex
    texslot.texture_coords = 'UV'
    texslot.use_map_color_diffuse = True
    texslot.use_map_color_emission = True
    texslot.emission_color_factor = 0.5
    texslot.use_map_density = True
    texslot.mapping = 'FLAT'
    texslot.use_map_alpha = True

    return mat


def create_cycles_material(mat, img):
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for n in nodes:
        nodes.remove(n)

    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img

    diff = nodes.new("ShaderNodeBsdfDiffuse")

    out = nodes.new('ShaderNodeOutputMaterial')

    links.new(tex.outputs[0], diff.inputs[0])
    links.new(diff.outputs[0], out.inputs[0])
