import os
import re
import sys
import json
import math
import pprint
import shutil
import bpy
import mathutils as mt
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Operator
from . import utils as ut


def poly_indices(poly):
    if len(poly.vertices) < 4:
        return list(poly.vertices)

    return [poly.vertices[i] for i in (0, 1, 2, 2, 3, 0)]

def triform(loop_indices):
    indices = list(loop_indices)

    if len(indices) < 4:
        return indices
    
    return [indices[i] for i in (0, 1, 2, 2, 3, 0)]

class EmptyUV:
    uv = (0.0, 0.0)
    def __getitem__(self, index):
        return self

def flip_uv(uv):
    uv[1] = 1 - uv[1]
    
def vertices(mesh):
    uv_act = mesh.uv_layers.active
    uv_layer = uv_act.data if uv_act is not None else EmptyUV()

    loop_vert = {l.index: l.vertex_index for l in mesh.loops}

    verts = []

    for poly in mesh.polygons:
        for li in triform(poly.loop_indices):
            vert = mesh.vertices[loop_vert[li]]
            vert_co = list(vert.co)
            vert_normal = list(vert.normal) if poly.use_smooth else list(poly.normal)
            vert_uv = list(uv_layer[li].uv)
            flip_uv(vert_uv)
            verts += vert_co + vert_normal + vert_uv

    return verts


def in_active_layer(obj):
    if obj.name not in scene.objects:
        return False

    layer = [i for i, v in enumerate(obj.layers) if v][0]
    active_layers = [i for i, v in enumerate(scene.layers) if v]

    if layer in active_layers:
        return True

    return False


def instance(dupli_group):
    if dupli_group:
        return [o.name for o in dupli_group.objects if not o.parent][0]


def mat_tris(mesh):
    """Returns dict: mat_name -> list_of_triangle_indices"""

    m_ps = {}

    idx_tri = 0
    for p in mesh.polygons:
        mat = mesh.materials[p.material_index] if mesh.materials else None
        mat_name = mat.name if mat else "__BDX_DEFAULT"
        if not mat_name in m_ps:
            m_ps[mat_name] = []

        m_ps[mat_name].append(idx_tri)
        idx_tri += 1

        if len(p.loop_indices) > 3:
            m_ps[mat_name].append(idx_tri)
            idx_tri += 1

    return m_ps


def used_meshes(objects):
    return [o.data for o in objects 
            if o.type == "MESH"]


def srl_models(meshes):
    name_model = {}

    tfs = 3 * 8 # triangle float size: 3 verts at 8 floats each

    for mesh in meshes:
        m_tris = mat_tris(mesh)
        verts = vertices(mesh)
        m_verts = {}
        for m, tris in m_tris.items():
            m_verts[m] = sum([verts[i * tfs : i * tfs + tfs] for i in tris], [])
        name_model[mesh.name] = m_verts

    return name_model

def srl_origins(objects):
    name_origin = {}
    
    for o in objects:
        if o.type == "MESH":
            mesh_name = o.data.name
            if mesh_name not in name_origin:
                origin = sum([mt.Vector(fv) for fv in o.bound_box], mt.Vector()) / len(o.bound_box)
                name_origin[mesh_name] = list(origin)
    
    return name_origin

def srl_dimensions(objects):
    name_dimensions = {}
    
    for o in objects:
        if o.type in ("MESH", "FONT"):
            data_name = "__FNT_" + o.data.name if o.type == "FONT" else o.data.name
            if data_name not in name_dimensions:
                name_dimensions[data_name] = [d / s for d, s in zip(o.dimensions, o.scale)]
    
    return name_dimensions

def char_uvs(char, angel_code):
    """
    Return a list of uv coordinates (for a quad)
    which encompass the relevant character on the font 
    texture, as specified by the angel code format.

    """
    cm = angel_code["common"]
    W, H = cm["scaleW"], cm["scaleH"]

    try:
        c = angel_code["char"][str(ord(char))]
    except:
        c = angel_code["char"][str(ord(' '))]

    x, y = c['x'], c['y']
    w, h = c['width'], c['height']

    pu = lambda x, y: [1 / W * x, 1 / H * y]

    #u = [[0, 0],
    #     [1, 0],
    #     [1, 1],
    #     [0, 1]]

    uvs = [pu(x, y + h),
           pu(x + w, y + h),
           pu(x + w, y),
           pu(x, y)]

    #[flip_uv(uv) for uv in uvs]

    return uvs


def vertices_text(text, angel_code):
    """Generate vertex data for a text object"""

    ac = angel_code
    o_c = ac["char"][str(ord('O'))]
    builtin = ac["info"]["face"] == "Bfont"
    scale = 0.0225 * (1.4 if builtin else 1)
    unit_height = o_c["height"] * scale

    verts = []
    pos = 0
    z = 0

    for char in text.body:
        # Make quad

        try:
            c = ac["char"][str(ord(char))]
        except:
            c = ac["char"][str(ord(' '))]

        x, y = pos + c["xoffset"], 0 - c["yoffset"]
        w, h = c["width"], c["height"]
        pos += c["xadvance"]

        q = [[x  , y-h, z],
             [x+w, y-h, z],
             [x+w, y  , z],
             [x  , y  , z]]

        z += 0.0001

        for v in q:
            v[0] *= scale
            v[1] *= scale
            v[0] -= 0.05 + (0.03 if builtin else 0)
            v[1] += unit_height * (0.76 - (0.05 if builtin else 0))

        quad = [v + [0, 0, 1] + uv for v, uv in zip(q, char_uvs(char, ac))]

        # To triangles
        tris = [quad[i] for i in (0, 1, 2, 2, 3, 0)]
        verts += sum(tris, [])

    return verts

def srl_models_text(texts, fntx_dir):
    j = os.path.join

    def fntx(t):
        with open(j(fntx_dir, t.font.name + ".fntx"), 'r') as f:
            data = json.load(f)
        return data

    def mat_name(t):
        for m in t.materials:
            if m:
                return m.name
        return ""

    return {"__FNT_"+t.name: 
                {"__FNT_"+mat_name(t)+t.font.name: vertices_text(t, fntx(t))} 
            for t in texts}

def srl_materials_text(texts):

    def mat(t):
        for m in t.materials:
            if m:
                return m

    mat_name = lambda m: m.name if m else ""

    name_gmat = {}

    for t in texts:
        m = mat(t)

        gmat = {"texture": "__FNT_"+t.font.name+".png",
                "alpha_blend": "ALPHA",
                "color": list(m.diffuse_color) if m else [1, 1, 1],
                "opacity": m.alpha if m else 1,
                "shadeless": m.use_shadeless if m else True,
                "emit": m.emit if m else 0.0,
                "backface_culling": m.game_settings.use_backface_culling if m else True}

        name_gmat["__FNT_"+mat_name(m)+t.font.name] = gmat

    return name_gmat


def view_plane(camd, winx, winy, xasp, yasp):
    """
    "DEAR GOD WHY??!!"

    Well, that's because blender doesn't expose the camera's projection matrix.
    So, in order to get it, we have to actually port the C code that generates it,
    using data that is actually available in the pyhton API.

    :(

    """

    #/* fields rendering */
    ycor = yasp / xasp
    use_fields = False
    if (use_fields):
      ycor *= 2

    def BKE_camera_sensor_size(p_sensor_fit, sensor_x, sensor_y):
        #/* sensor size used to fit to. for auto, sensor_x is both x and y. */
        if (p_sensor_fit == 'VERTICAL'):
            return sensor_y;

        return sensor_x;

    if (camd.type == 'ORTHO'):
      #/* orthographic camera */
      #/* scale == 1.0 means exact 1 to 1 mapping */
      pixsize = camd.ortho_scale
    else:
      #/* perspective camera */
      sensor_size = BKE_camera_sensor_size(camd.sensor_fit, camd.sensor_width, camd.sensor_height)
      pixsize = (sensor_size * camd.clip_start) / camd.lens

    #/* determine sensor fit */
    def BKE_camera_sensor_fit(p_sensor_fit, sizex, sizey):
        if (p_sensor_fit == 'AUTO'):
            if (sizex >= sizey):
                return 'HORIZONTAL'
            else:
                return 'VERTICAL'

        return p_sensor_fit

    sensor_fit = BKE_camera_sensor_fit(camd.sensor_fit, xasp * winx, yasp * winy)

    if (sensor_fit == 'HORIZONTAL'):
      viewfac = winx
    else:
      viewfac = ycor * winy

    pixsize /= viewfac

    #/* extra zoom factor */
    pixsize *= 1 #params->zoom

    #/* compute view plane:
    # * fully centered, zbuffer fills in jittered between -.5 and +.5 */
    xmin = -0.5 * winx
    ymin = -0.5 * ycor * winy
    xmax =  0.5 * winx
    ymax =  0.5 * ycor * winy

    #/* lens shift and offset */
    dx = camd.shift_x * viewfac # + winx * params->offsetx
    dy = camd.shift_y * viewfac # + winy * params->offsety

    xmin += dx
    ymin += dy
    xmax += dx
    ymax += dy

    #/* fields offset */
    #if (params->field_second):
    #    if (params->field_odd):
    #        ymin -= 0.5 * ycor
    #        ymax -= 0.5 * ycor
    #    else:
    #        ymin += 0.5 * ycor
    #        ymax += 0.5 * ycor

    #/* the window matrix is used for clipping, and not changed during OSA steps */
    #/* using an offset of +0.5 here would give clip errors on edges */
    xmin *= pixsize
    xmax *= pixsize
    ymin *= pixsize
    ymax *= pixsize

    return xmin, xmax, ymin, ymax


def projection_matrix(camd):
    r = scene.render
    left, right, bottom, top = view_plane(camd, r.resolution_x, r.resolution_y, 1, 1)

    farClip, nearClip = camd.clip_end, camd.clip_start

    Xdelta = right - left
    Ydelta = top - bottom
    Zdelta = farClip - nearClip

    mat = [[0]*4 for i in range(4)]

    if camd.type == "ORTHO":
        for i in range(4): mat[i][i] = 1; # identity
        mat[0][0] = 2 / Xdelta
        mat[3][0] = -(right + left) / Xdelta
        mat[1][1] = 2 / Ydelta
        mat[3][1] = -(top + bottom) / Ydelta
        mat[2][2] = -2 / Zdelta #/* note: negate Z	*/
        mat[3][2] = -(farClip + nearClip) / Zdelta
    else:
        mat[0][0] = nearClip * 2 / Xdelta
        mat[1][1] = nearClip * 2 / Ydelta
        mat[2][0] = (right + left) / Xdelta #/* note: negate Z	*/
        mat[2][1] = (top + bottom) / Ydelta
        mat[2][2] = -(farClip + nearClip) / Zdelta
        mat[2][3] = -1
        mat[3][2] = (-2 * nearClip * farClip) / Zdelta

    return sum([c for c in mat], [])


def get_cls_name(obj):
    if obj.bdx.cls_use_custom:
        cls_name = obj.bdx.cls_custom_name
        return cls_name.replace(".java", "") if cls_name.endswith(".java") else ""
    return obj.name


def relevant_region_3d_data():
    
    def get_areas_3d_data(areas):
        return [[a, a.height * a.width] for a in areas if a.type == "VIEW_3D"]
    
    if scene != bpy.context.scene:
        return
    r3d = bpy.context.region_data
    if r3d:
        if r3d.view_perspective == "CAMERA":
            return
    elif bpy.context.scene.camera:
        return
    else:
        a3d = get_areas_3d_data(bpy.context.screen.areas)
        if not a3d:
            screens = bpy.data.screens
            if "BDX" in screens:
                a3d = get_areas_3d_data(screens["BDX"].areas)
                if not a3d:
                    a3d = get_areas_3d_data(sum([list(scr.areas) for scr in screens], []))
            else:
                a3d = get_areas_3d_data(sum([list(scr.areas) for scr in screens], []))
            if not a3d:
                return
        if len(a3d) != 1:
            a3d.sort(key=lambda lst: lst[1])
        r3d = a3d[-1][0].spaces[0].region_3d
    return r3d


def srl_objects(objects):
    name_object = {}

    def static(obj):
        return obj.game.physics_type in ("STATIC", "SENSOR")

    def bounds_type(obj):
        t = obj.game.collision_bounds_type
        if static(obj):
            if not obj.game.use_collision_bounds:
                t = "TRIANGLE_MESH"
        elif t == "TRIANGLE_MESH":
            t = "BOX"
        return t

    for obj in objects:
        matrix = obj.matrix_world

        if obj.type == "MESH":
            mesh_name = obj.data.name
        elif obj.type == "FONT":
            mesh_name = "__FNT_"+obj.data.name
        else:
            mesh_name = None

        transform = sum([list(v) for v in matrix.col], [])

        name_object[obj.name] = {
            "class": get_cls_name(obj),
            "use_priority": obj.bdx.cls_use_priority,
            "type": obj.type,
            "properties": {n: p.value for n, p in obj.game.properties.items()},
            "transform": transform,
            "parent": obj.parent.name if obj.parent else None,
            "mesh_name": mesh_name,
            "active": in_active_layer(obj),
            "visible": not obj.hide_render,
            "instance": instance(obj.dupli_group),
            "physics": {
                "body_type": obj.game.physics_type,
                "bounds_type": bounds_type(obj),
                "margin": obj.game.collision_margin,
                "mass": 0 if static(obj) else obj.game.mass,
                "friction": obj.active_material.physics.friction if obj.active_material else 0.5,
                "restitution": obj.active_material.physics.elasticity if obj.active_material else 0,
                "ghost": obj.game.use_ghost,
                "group": sum([2**i for i, v in enumerate(obj.game.collision_group) if v]),
                "mask": sum([2**i for i, v in enumerate(obj.game.collision_mask) if v]),
                "compound": obj.game.use_collision_compound
            }
        }

        d = name_object[obj.name]

        if obj.type == "CAMERA":
            d["camera"] = {
                "projection": projection_matrix(obj.data),
                "type": obj.data.type
            }
            
        elif obj.type == "FONT":
            d["font"] = obj.data.font.name
            d["text"] = obj.data.body
            
        elif obj.type == "LAMP":
            d['lamp'] = {
                "type": obj.data.type,
                "energy": obj.data.energy,
                "color": list([obj.data.color[0], obj.data.color[1], obj.data.color[2], 1]),
                "distance": obj.data.distance
            }
    
    r3d = relevant_region_3d_data()
    if r3d:
        
        view_type = r3d.view_perspective
        view_matrix = sum([list(v) for v in r3d.view_matrix.inverted().col], [])
        view_projection = sum([list(v) for v in r3d.window_matrix.col], [])
        r = bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y
        
        if view_type == "PERSP":
            view_projection[0] = 1
            view_projection[5] = r
        else: # "ORTHO"
            view_projection[0] = 1 / r3d.view_distance
            view_projection[5] = r / r3d.view_distance

        name_object["__CAMERA__"] = {
            "class": "",
            "use_priority": False,
            "type": "CAMERA",
            "properties": {},
            "transform": view_matrix,
            "parent": None,
            "mesh_name": None,
            "active": True,
            "visible": False,
            "instance": None,
            "physics": {
                "body_type": "NO_COLLISION",
                "bounds_type": "BOX",
                "margin": 0.04,
                "mass": 1,
                "friction": 0.5,
                "restitution": 0,
                "ghost": False,
                "group": 1,
                "mask": 255,
                "compound": False
            },
            "camera": {
                "projection": view_projection,
                "type": view_type
            }
        }
    
    return name_object


def used_materials(objects):
    return sum([[m for m in o.data.materials if m] for o in objects 
                if o.type == "MESH"], [])

def srl_materials(materials):
    def texture_name(m):
        if m.active_texture and hasattr(m.active_texture, "image"):
            return os.path.basename(m.active_texture.image.filepath)
        return None

    return {m.name:
                {"texture": texture_name(m),
                 "alpha_blend": "ALPHA" if m.use_transparency else "OPAQUE",
                 "color": list(m.diffuse_color),
                 "opacity": m.alpha,
                 "shadeless": m.use_shadeless,
                 "emit": m.emit,
                 "backface_culling": m.game_settings.use_backface_culling}
            for m in materials}


def camera_names(scene):
    cam_names = [o.name for o in scene.objects if o.type == "CAMERA"]
    r3d = relevant_region_3d_data()
    if scene.camera:
        if not r3d and not True in [x & y for (x, y) in zip(scene.camera.layers, scene.layers)]:
            raise Exception("No active camera in active layer(s)")
        activ_cam_name = scene.camera.name
        if activ_cam_name in cam_names:
            cam_names.remove(activ_cam_name)
            cam_names.insert(0, activ_cam_name)
    elif not r3d:
        raise Exception("No active camera or 3D View data")
    if r3d:
        cam_names.insert(0, "__CAMERA__")
    return cam_names


def instantiator(objects):
    """
    Returns list of java source lines, which encode an instantiator that
    binds classes in the root package (and subpackages) to exported objects with the same name.

    """

    j = os.path.join

    src_root = ut.src_root()

    relevant_dirs = ut.listdir(src_root, dirs_only=True, recursive=True);

    try:
        relevant_dirs.remove(j(src_root, "inst"))
    except ValueError:
        pass

    relevant_dirs.append(src_root)

    relevant_files = sum([ut.listdir(d, pattern="*.java") for d in relevant_dirs], [])

    def path_to_name(path):
        return os.path.split(path)[1].split('.')[0]

    def path_to_class(path):
        path = path[:-5] # strip ".java"
        path = os.path.relpath(path, j(ut.project_root(), "core", "src"))
        return '.'.join(ut.split_path(path))

    name_class = {path_to_name(fp): path_to_class(fp) for fp in relevant_files}

    shared_names = []
    for o in objects:
        cls_name = get_cls_name(o)
        if cls_name in name_class:
            shared_names.append(cls_name)

    if not shared_names:
        return None


    with open(j(ut.gen_root(), "Instantiator.java"), 'r') as f:
        lines = f.readlines()

    package_name = ut.package_name()
    lines[0] = "package " + package_name + ".inst;\n"
    lines[4] = "import " + package_name + ".*;\n"

    top = lines[:10]
    equals, new = lines[10:12]
    bottom = lines[12:]

    body = []
    for name in shared_names:
        body += [equals.replace("NAME", name),
                 new.replace("NAME", name_class[name])]

    new_lines = top + body + bottom

    return new_lines


def srl_actions(actions):
    relevant = {"location":0, "rotation_euler":3, "scale":6}

    index = lambda c: relevant[c.data_path] + c.array_index

    srl_keyframe = lambda kf: [list(p) 
                               for p in (kf.handle_left, kf.co, kf.handle_right)]
    return {a.name: 
                {index(c): 
                    [srl_keyframe(kf)
                     for kf in c.keyframe_points]
                 for c in a.fcurves if c.data_path in relevant}
            for a in actions}


def used_fonts(texts):
    return {t.font for t in texts}

def texts(objects):
    return [o.data for o in objects if o.type == "FONT"]

def generate_bitmap_fonts(fonts, hiero_dir, fonts_dir, textures_dir):
    j = os.path.join

    # list of fonts to export
    existing = os.listdir(fonts_dir)
    fonts_to_export = [f for f in fonts if f.name + ".fntx" not in existing]

    if not fonts_to_export:
        return

    # base hiero command
    gcr = ut.gradle_cache_root()

    ver = ut.libgdx_version()
    gdx_jars = ["gdx-"+ver+".jar",
                "gdx-platform-"+ver+"-natives-desktop.jar",
                "gdx-backend-lwjgl-"+ver+".jar"]

    badlogic = j(gcr, "com.badlogicgames.gdx")
    gdx_jars = [ut.find_file(jar, badlogic) for jar in gdx_jars]

    if None in gdx_jars:
        raise Exception("Font gen: Can't find required gdx jars \
                (try running the game without any text objects first)")

    op_sys = {"lin":"linux", "dar":"osx", "win":"windows"}[sys.platform[:3]]

    lwjgl_jars = ["lwjgl-[0-9].[0-9].[0-9].jar",
                  "lwjgl-platform-*-natives-"+op_sys+".jar"]

    lwjgl = j(gcr, "org.lwjgl.lwjgl")
    lwjgl_jars = [ut.find_file(jar, lwjgl) for jar in lwjgl_jars]

    jars = gdx_jars + lwjgl_jars + [j(hiero_dir, "gdx-tools.jar")]

    sep = ";" if op_sys == "windows" else ":"
    hiero = 'java -cp "{}" com.badlogic.gdx.tools.hiero.Hiero '.format(sep.join(jars))

    # export fonts, via hiero
    for font in fonts_to_export:
        ttf = font.filepath
        if ttf == "<builtin>":
            ttf = j(hiero_dir, "bfont.ttf")
        else:
            ttf = os.path.abspath(bpy.path.abspath(ttf))
        hiero += '"{}---{}" '.format(ttf, j(fonts_dir, font.name))
    os.system(hiero)

    # move pngs to textures dir
    for f in ut.listdir(fonts_dir, pattern="*.png"):
        shutil.move(f, j(textures_dir, "__FNT_" + os.path.basename(f)))

    # convert hiero-generated angel code files (.fnt), to proper json files (.fntx)
    fnts = ut.listdir(fonts_dir, pattern="*.fnt")
    for fnt in fnts:
        with open(fnt+'x', 'w') as f:
            json.dump(ut.angel_code(fnt), f)

    # remove fnt files
    for f in fnts:
        os.remove(f)


scene = None;

def export(context, filepath, scene_name, exprun):
    global scene;
    scene = bpy.data.scenes[scene_name] if scene_name else context.scene

    objects = list(scene.objects)

    def instance_referenced(objects):
        instances = [o for o in objects if o.dupli_group]
        expanded = sum([list(o.dupli_group.objects) for o in instances], [])

        if expanded:
            return expanded + instance_referenced(expanded)
        return []

    objects = set(objects + instance_referenced(objects))

    ts = texts(objects)
    fonts = used_fonts(ts)

    if scene.world != None:
        ambient_color = list(scene.world.ambient_color)
    else:
        ambient_color = [0.0, 0.0, 0.0]

    bdx = {
        "name": scene.name,
        "gravity": scene.game_settings.physics_gravity,
        "physviz": scene.game_settings.show_physics_visualization,
        "framerateProfile": scene.game_settings.show_framerate_profile,
        "ambientColor": ambient_color,
        "models": srl_models(used_meshes(objects)),
        "origins": srl_origins(objects),
        "dimensions": srl_dimensions(objects),
        "objects": srl_objects(objects),
        "materials": srl_materials(used_materials(objects)),
        "cameras": camera_names(scene),
        "actions": srl_actions(bpy.data.actions),
        "fonts": [f.name for f in fonts]
    }

    if exprun:
        j = os.path.join

        bdx_dir = j(ut.project_root(), "android", "assets", "bdx")
        fonts_dir = j(bdx_dir, "fonts")
        textures_dir = j(bdx_dir, "textures")
        hiero_dir = j(ut.gen_root(), "hiero")

        generate_bitmap_fonts(fonts, hiero_dir, fonts_dir, textures_dir);

        bdx["models"].update(srl_models_text(ts, fonts_dir))
        bdx["materials"].update(srl_materials_text(ts))

        # Generate instantiators
        lines = instantiator(objects)

        if lines:
            class_name = ut.str_to_valid_java_class_name(scene.name)
            lines[5] = lines[5].replace("NAME", class_name)

            inst = j(ut.src_root(), "inst")

            with open(j(inst, class_name + ".java"), 'w') as f:
                f.writelines(lines)

    with open(filepath, "w") as f:
        json.dump(bdx, f)

    return {'FINISHED'}


class ExportBdx(Operator, ExportHelper):
    """Export to bdx scene format (.bdx)"""
    bl_idname = "export_scene.bdx"
    bl_label = "Export to .bdx"

    filename_ext = ".bdx"

    filter_glob = StringProperty(
            default="*.bdx",
            options={'HIDDEN'},
            )

    scene_name = StringProperty(
            default="",
            )

    exprun = BoolProperty(
            default=False,
            )

    def execute(self, context):
        return export(context, self.filepath, self.scene_name, self.exprun)


def menu_func_export(self, context):
    self.layout.operator(ExportBdx.bl_idname, text="bdx (.bdx)")


def register():
    bpy.utils.register_class(ExportBdx)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportBdx)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
