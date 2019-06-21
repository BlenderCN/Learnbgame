from math import fabs

from collections import namedtuple

try:
    import bpy
    from mathutils import Vector
except ImportError:
    from tests.helper_classes import Vector


TileInfo = namedtuple('TileInfo', 'x1 y1 x2 y2 color')

def create_tile_infos(width, height, num_tiles, tile_size, colors):
    x_tiles = int(width / tile_size)
    y_tiles = int(height / tile_size)
    if x_tiles * y_tiles < num_tiles:
        raise ValueError(f"Incorrect image dimensions for {num_tiles} tiles")
    infos = []
    i_colors = iter(colors)
    for y_pos in range(y_tiles):
        for x_pos in range(x_tiles):
            try:
                infos.append(TileInfo(
                        x_pos * tile_size,
                        y_pos * tile_size,
                        x_pos * tile_size + tile_size - 1,
                        y_pos * tile_size + tile_size - 1,
                        next(i_colors)
                    ))
            except StopIteration:
                break
    return infos


def paint_patch(
        tile_infos: list = [],
        pixels: list = [],
        width: int = 0) -> list:
    if width == 0:
        raise ValueError("width can't be 0")
    out = [pixels[i] for i in range(len(pixels))]
    for info in tile_infos:
        for y in range(info.y1, info.y2 + 1):
            for x in range(info.x1, info.x2 + 1):
                offset = (x + y * width) * 4
                for i, c in enumerate(info.color):
                    out[offset + i] = c
    return out


def translate_uvs(tile_info: TileInfo, uvs=[], margin=5.0):
    a_uv = uvs[0]

    min_x = min(uvs, key=lambda v: v.x).x
    min_y = min(uvs, key=lambda v: v.y).y
    max_x = max(uvs, key=lambda v: v.x).x
    max_y = max(uvs, key=lambda v: v.y).y
    out_uvs = [Vector((v.x - min_x, v.y - min_y)) for v in uvs]

    width = max_x - min_x
    height = max_y - min_y

    target_width = tile_info.x2 - tile_info.x1 - margin * 2
    target_height = tile_info.y2 - tile_info.y1 - margin * 2

    scale_x = target_width / width
    scale_y = target_height / height

    out_uvs = [Vector((v.x * scale_x, v.y * scale_y)) for v in out_uvs]

    t1 = Vector((tile_info.x1, tile_info.y1))
    margin_v = Vector((margin, margin))
    out_uvs = [v + t1 + margin_v for v in out_uvs]

    return out_uvs


def generate_texture_atlas(image_size, tile_size):
    bpy.ops.object.mode_set(mode="OBJECT")

    obj = bpy.context.active_object

    if "texture_atlas" not in bpy.data.images:
        bpy.ops.image.new(name="texture_atlas", width=image_size, height=image_size)
    image = bpy.data.images['texture_atlas']
    image.generated_width = image_size
    image.generated_height = image_size
    width = image.size[0]
    height = image.size[1]

    colors = []
    color_face_map = {}
    for face in obj.data.polygons:
        mat_index = face.material_index
        mat = obj.material_slots[mat_index].material
        color = mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value
        if not color in colors:
            colors.append(color)
        if not color in color_face_map:
            color_face_map[color] = []
        color_face_map[color].append(face)

    tile_infos = create_tile_infos(width, height, len(colors), tile_size, colors)

    print(list(color_face_map.keys()))

    for color, faces in color_face_map.items():
        uvs = []
        for face in faces:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uvs.append(obj.data.uv_layers.active.data[loop_idx].uv)
        uvs = translate_uvs(tile_infos[colors.index(color)], uvs)
        print(color, len(uvs))
        # Normalize
        i_uvs = (Vector((v.x / width, v.y / height)) for v in uvs)
        for face in faces:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                obj.data.uv_layers.active.data[loop_idx].uv = next(i_uvs)

    l = [0.0 for i in range(len(image.pixels))]
    l = paint_patch(tile_infos, l, width)

    image.pixels = l

    bpy.ops.object.mode_set(mode="EDIT")
