import bpy
import os
import io
import math
from contextlib import redirect_stdout
import sys
import bmesh


def update_progress(job_title, progress):
    length = 20
    block = int(round(length * progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title,
        "#" * block + "-" * (length-block),
        "%.2f" % (progress * 100))

    if progress >= 1:
        msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


def verts2points(verts):
    points = []
    for vert in verts:
        point = [vert.co.x, vert.co.y, vert.co.z]
        points.append(point)
    return points


def get_glyph_size(vertices):
    """
    Get the size of a glyph
    """
    x_points = []
    y_points = []
    for vert in vertices:
        x_points.append(vert.co.x)
        y_points.append(vert.co.y)

    min_x = min(x_points)
    max_x = max(x_points)

    min_y = min(y_points)
    max_y = max(y_points)

    return min_x, max_x, min_y, max_y


def get_islands(obj):
    """
    Gets a list of vertices grouped by islands
    """
    edges = list(obj.data.edges)

    islands = []
    found = False
    while len(edges) > 0:
        if found == False:
            islands.append(list(edges[0].vertices))
            edges.pop(0)

        found = False
        i = 0
        while i < len(edges):
            for vert in edges[i].vertices:
                if vert in islands[-1]:
                    islands[-1].extend(list(edges[i].vertices))
                    edges.pop(i)
                    found = True
                    break
            i += 1

    for i in range(len(islands)):
        islands[i] = list(set(islands[i]))
    return islands


def convert_curve(obj):
    """
    Duplicate a curve and convert the duplicate to a mesh
    """
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.duplicate()

    bpy.ops.object.convert(target='MESH')


def export_glyph(obj, folder):
    name = obj.name
    path = os.path.join(folder, name + '.glyph')

    convert_curve(obj)

    duplicate = bpy.context.view_layer.objects.active
    islands = get_islands(duplicate)
    left, right, bottom, top = get_glyph_size(duplicate.data.vertices)
    points = verts2points(duplicate.data.vertices)

    for i in range(len(points)):
        points[i][0] -= left

    decimals = 5
    glyph_strokes = []
    for i in range(len(islands)):
        glyph_strokes.append([])
        for p in range(len(points)):
            if p in islands[i]:
                v = points[p]
                v[0] = round(v[0], decimals)
                v[1] = round(v[1], decimals)
                v[2] = 0
                glyph_strokes[-1].append(v)

    stdout = io.StringIO()
    with redirect_stdout(stdout):
        bpy.ops.object.delete()

    text = ''
    for stroke in glyph_strokes:
        text += str(stroke) + '\n'
    text.strip()

    with open(path, 'w') as f:
        f.write(text)


if __name__ == "__main__":
    objs = bpy.data.objects
    name = os.path.basename(bpy.data.filepath).replace('.blend', '')
    folder = os.path.dirname(bpy.data.filepath)

    path = os.path.join(folder, name)

    if not os.path.isdir(path):
        os.makedirs(path)

    for i in range(len(objs)):
        export_glyph(objs[i], path)
        update_progress("Making Glyphs", i / len(objs))
    update_progress("Making Glyphs", 1)