import bpy
import bpy.utils.previews
from bpy.app.handlers import persistent
import math
from mathutils import Vector
import time


class CacheException(Exception):
    pass

cache = {}


def get_cache(op_pointer, key):
    if op_pointer not in cache.keys():
        raise CacheException("No operator cache")
    if key not in cache[op_pointer].keys():
        raise CacheException("No key cache")
    return cache[op_pointer][key]


def set_cache(op_pointer, key, value):
    if op_pointer not in cache.keys():
        if len(cache) > 0:
            cache.clear()
        cache[op_pointer] = {}
    cache[op_pointer][key] = value


def clear_cache(op_pointer=None, key=None):
    if op_pointer or key is None:
        cache.clear()
    else:
        if op_pointer in cache:
            if key in op_pointer:
                del cache[op_pointer][key]


def select_only(bm, geom, mode={"VERT"}):
    bm.select_mode = mode
    for ele in bm.verts[:] + bm.edges[:] + bm.faces[:]:
        ele.select_set(False)

    for ele in geom:
        if ele.is_valid:
            ele.select_set(True)


def refresh_icons():
    global draw
    global update_time
    draw = True
    update_time = time.time()


def get_icon(name, coll="shape_types"):
    pcoll = preview_collections[coll]
    preview = pcoll.get(name)
    if preview is None:
        preview = pcoll.new(name)
        preview.image_size = (200, 200)

    return preview.icon_id


preview_collections = {}
draw = False


def generate_icons():
    wm = bpy.context.window_manager
    verts_count = bpy.context.scene.perfect_shape.preview_verts_count

    verts = []
    for i in range(verts_count):
        theta = 2.0 * math.pi * i / verts_count;
        verts.append((math.cos(theta) * 0.9, math.sin(theta) * 0.9))
    generate_icon("circle", verts)

    verts = []
    if wm.operators and wm.operators[-1].bl_idname == "MESH_OT_perfect_shape":
        ratio_a = wm.operators[-1].properties.ratio_a
        ratio_b = wm.operators[-1].properties.ratio_b
    else:
        ratio_a = 1
        ratio_b = 1
    verts = []
    seg_a = (verts_count / 2) / (ratio_a + ratio_b) * ratio_a
    seg_b = int((verts_count / 2) / (ratio_a + ratio_b) * ratio_b)
    if seg_a % 1 > 0:
        seg_a += 1
        seg_b += 2
    seg_a = int(seg_a)
    size_a = 1.6
    size_b = 1.6
    seg_len_a = size_a / seg_a
    seg_len_b = size_b / seg_b
    for i in range(seg_a):
        verts.append((seg_len_a*i-(size_a/2), size_b/2*-1))
    for i in range(seg_b):
        verts.append((size_a/2, seg_len_b*i-(size_b/2)))
    for i in range(seg_a, 0, -1):
        verts.append((seg_len_a*i-(size_a/2), size_b/2))
    for i in range(seg_b, 0, -1):
        verts.append((size_a/2*-1, seg_len_b*i-(size_b/2)))

    generate_icon("rectangle", verts)

    suzanne = [[-2.421438694000244e-08, 0.7087500095367432], [0.32624995708465576, 0.6693750023841858],
               [0.5737500190734863, 0.4443749785423279], [0.5906249284744263, 0.23624998331069946],
               [0.7368749380111694, 0.34312498569488525], [0.8887499570846558, 0.3656250238418579],
               [0.9731249809265137, 0.2306250035762787], [0.9225000143051147, 0.03937500715255737],
               [0.7481249570846558, -0.0731249749660492], [0.4274999797344208, -0.0899999737739563],
               [0.22499996423721313, -0.3149999976158142], [0.23624998331069946, -0.6806250214576721],
               [-2.421438694000244e-08, -0.7087500095367432], [-0.23625002801418304, -0.6806250214576721],
               [-0.2250000238418579, -0.3149999976158142], [-0.42750003933906555, -0.0899999737739563],
               [-0.7481250762939453, -0.0731249749660492], [-0.9225000143051147, 0.03937500715255737],
               [-0.9731249809265137, 0.2306250035762787], [-0.8887500762939453, 0.3656250238418579],
               [-0.736875057220459, 0.34312498569488525], [-0.5906250476837158, 0.23624998331069946],
               [-0.5737500190734863, 0.4443749785423279], [-0.32625001668930054, 0.6693750023841858]]
    suzanne_faces = [[3, 1, 9], [0, 9, 1], [3, 7, 4], [1, 3, 2], [22, 21, 23], [19, 18, 20], [21, 15, 23], [4, 6, 5],
                     [23, 15, 0], [18, 17, 20], [16, 21, 17], [12, 14, 13], [15, 21, 16], [11, 10, 12], [17, 21, 20],
                     [12, 10, 14], [7, 3, 8], [10, 15, 14], [6, 4, 7], [9, 15, 10], [15, 9, 0], [3, 9, 8]]
    object_verts = bpy.context.scene.perfect_shape.shape.verts
    object_faces = bpy.context.scene.perfect_shape.shape.faces
    if len(object_verts) == 0:
        generate_icon("object", suzanne, suzanne_faces)
    else:
        verts = []
        length = 0
        for vert in object_verts:
            v = Vector(vert.co[:2])
            verts.append(v)
            if v.length > length:
                length = v.length
        scale = 0.9 / length
        generate_icon("object", [v*scale for v in verts], [f.indices for f in object_faces])


def generate_patterns_icons():
    pcoll = preview_collections["patterns"]
    patterns = bpy.context.scene.perfect_shape.patterns
    for idx, pattern in enumerate(patterns):
        if str(idx) not in pcoll:
            verts= []
            length = 0
            for vert in pattern.verts:
                v = Vector(vert.co[:2])
                verts.append(v)
                if v.length > length:
                    length = v.length
            scale = 0.9 / length
            generate_icon(str(idx), [v*scale for v in verts], [f.indices for f in pattern.faces], "patterns")


def generate_icon(name, verts=None, faces=None, coll="shape_types"):
    pcoll = preview_collections[coll]
    if name in pcoll:
        thumb = pcoll.get(name)
    else:
        thumb = pcoll.new(name)
        thumb.image_size = (200, 200)

    if verts is not None:
        import bgl

        polygon_color = bpy.context.user_preferences.themes[0].view_3d.edge_facesel
        edge_color = bpy.context.user_preferences.themes[0].view_3d.edge_select
        vertex_color = bpy.context.user_preferences.themes[0].view_3d.vertex_select
        clear_color = bpy.context.user_preferences.themes[0].user_interface.wcol_menu.inner

        viewport_info = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport_info)
        buffer = bgl.Buffer(bgl.GL_FLOAT, 200 * 200 * 4)

        bgl.glDisable(bgl.GL_SCISSOR_TEST)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glEnable(bgl.GL_POINT_SMOOTH)
        bgl.glViewport(0, 0, 200, 200)

        bgl.glMatrixMode(bgl.GL_MODELVIEW)
        bgl.glPushMatrix()
        bgl.glLoadIdentity()

        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glPushMatrix()
        bgl.glLoadIdentity()
        bgl.gluOrtho2D(0, 0, 0, 0)

        bgl.glLineWidth(4.0)
        bgl.glPointSize(10.0)

        bgl.glClearColor(*clear_color)
        bgl.glClear(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_DEPTH_BUFFER_BIT)

        if faces is None:
            bgl.glBegin(bgl.GL_POLYGON)
            bgl.glColor3f(*polygon_color)
            for vert in verts:
                bgl.glVertex2f(*vert)
            bgl.glEnd()
        else:
            bgl.glBegin(bgl.GL_TRIANGLES)
            bgl.glColor3f(*polygon_color)
            for face in faces:
                bgl.glVertex2f(*verts[face[0]])
                bgl.glVertex2f(*verts[face[1]])
                bgl.glVertex2f(*verts[face[2]])
            bgl.glEnd()

        bgl.glBegin(bgl.GL_LINE_LOOP)
        bgl.glColor3f(*edge_color)
        for vert in verts:
            bgl.glVertex2f(*vert)
        bgl.glEnd()

        bgl.glBegin(bgl.GL_POINTS)
        bgl.glColor3f(*vertex_color)
        for vert in verts:
            bgl.glVertex2f(*vert)
        bgl.glEnd()

        bgl.glReadPixels(0, 0, 200, 200, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)
        bgl.glEnable(bgl.GL_SCISSOR_TEST)
        bgl.glLineWidth(1.0)
        bgl.glPointSize(1.0)

        buffer = buffer[:]
        for idx in range(0, 200 * 200 * 4, 4):
            if buffer[idx] == clear_color[0] and \
                            buffer[idx + 1] == clear_color[1] and buffer[idx + 2] == clear_color[2]:
                buffer[idx + 3] = 0.0

        thumb.image_pixels_float = buffer

update_time = None


@persistent
def handler(scene):
    global draw
    global update_time

    obj = bpy.context.object
    if draw:
        if obj is not None:
            if update_time is None:
                update_time = time.time()
            if bpy.context.object.is_updated_data:
                update_time = time.time()
            if time.time() - update_time > 0.2:
                generate_icons()
                draw = False


@persistent
def load_handler(scene):
    for pcoll in preview_collections.values():
        pcoll.clear()
        generate_patterns_icons()


def register():
    preview_collections["shape_types"] = bpy.utils.previews.new()
    preview_collections["patterns"] = bpy.utils.previews.new()
    bpy.app.handlers.scene_update_post.append(handler)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    bpy.app.handlers.scene_update_post.remove(handler)
    bpy.app.handlers.load_post.remove(load_handler)
