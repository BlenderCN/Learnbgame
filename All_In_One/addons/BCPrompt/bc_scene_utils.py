# bc_scene_utils.py
import bpy
import bmesh
import os


def enumerate_objects_starting_with(find_term):
    return (c for c in bpy.data.objects if c.name.startswith(find_term))


def select_starting(find_term):
    objs = enumerate_objects_starting_with(find_term)
    for o in objs:
        o.select = True


def select_starting2(find_term, type_object):

    shortname = {
        # easy to extend..
        'CU': 'CURVE',
        'M': 'MESH'
    }.get(type_object)

    if shortname:
        type_object = shortname

    objs = enumerate_objects_starting_with(find_term)
    for o in objs:
        if not o.type == type_object:
            continue
        o.select = True


def distance_check():
    obj = bpy.context.edit_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    verts = [v.co for v in bm.verts if v.select]
    if not len(verts) == 2:
        return 'select 2 only'
    else:
        dist = (verts[0] - verts[1]).length
        return str(dist)


def align_view_to_3dcursor():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            ctx = bpy.context.copy()
            ctx['area'] = area
            ctx['region'] = area.regions[-1]
            bpy.ops.view3d.view_center_cursor(ctx)


def parent_selected_to_new_empty():
    context = bpy.context
    scene = context.scene
    objects = bpy.data.objects

    selected_objects = context.selected_objects.copy()

    if not selected_objects:
        return

    mt = objects.new('parent_empty', None)
    scene.objects.link(mt)

    for o in selected_objects:
        o.parent = mt

    return mt


def add_mesh_2_json(kind):
    temp_root = os.path.dirname(__file__)

    file_by_name = {
        'zup': 'mesh2json.py',
        'yup': 'mesh2json2.py'
    }.get(kind)

    fp = os.path.join(temp_root, 'fast_ops', file_by_name)
    with open(fp) as ofile:
        fullstr = ''.join(ofile)
        nf = bpy.data.texts.new(file_by_name)
        nf.from_string(fullstr)


def crop_to_active():
    se = bpy.context.scene.sequence_editor
    start = se.active_strip.frame_start
    duration = se.active_strip.frame_duration
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = start + duration - 1


def v2rdim():
    SCN = bpy.context.scene
    SE = SCN.sequence_editor

    # if m == 'v2rdim':
    #     sequence = SE.active_strip
    # elif m.startswith('v2rdim '):
    #     vidname = m[7:]
    #     sequence = SE.sequences.get(vidname)
    #     if not sequence:
    #         print(vidname, 'is not a sequence - check the spelling')
    #         return True

    def get_size(sequence):

        if hasattr(sequence, "sequences") and len(sequence.sequences) > 0:
            # just pick first.
            sequence = sequence.sequences[0]

        clips = bpy.data.movieclips
        fp = sequence.filepath
        mv = clips.load(fp)
        x, y = mv.size[:]
        clips.remove(mv)
        return x, y

    sequence = SE.active_strip
    x, y = get_size(sequence)
    SCN.render.resolution_x = x
    SCN.render.resolution_y = y
    SCN.render.resolution_percentage = 100


def render_to_filepath(fp):
    bpy.context.scene.render.filepath = fp
    bpy.ops.render.opengl(animation=True, sequencer=True)


def process_size_query(m):

    def path_iterator(path_name, filetype):
        for fp in os.listdir(path_name):
            if fp.endswith("." + filetype):
                yield fp

    if m == 'sizeof':
        # this means user knows path is set and wants to list size of gifs
        fp = bpy.context.scene.render.filepath
        print(fp)
        for path in path_iterator(fp, 'gif'):
            fullpath = os.path.join(fp, path)
            print('---', path, 'kb =', os.stat(fullpath).st_size)

    # make this when you need it - not before.
    # elif len(m.split(' ')) == 2:
    #    # if you have spaces in your filename or path you are an idiot.
    #    path = m.split(' ')[1]
