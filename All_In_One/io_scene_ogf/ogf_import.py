from .ogf_utils import *

try:
    import bpy
except ImportError:
    bpy = None


class ImportContext:
    def __init__(self, file_name, remesh=False):
        from .settings import GAMEDATA_FOLDER
        self.gamedata = GAMEDATA_FOLDER
        self.file_name = file_name
        import os.path
        self.object_name = os.path.basename(file_name.lower())
        self.__images = {}
        self.__textures = {}

    def image(self, relpath):
        import os.path
        relpath = relpath.lower().replace('/', os.path.sep).replace('\\', os.path.sep)
        result = self.__images.get(relpath)
        if not result:
            self.__images[relpath] = result = bpy.data.images.load('{}/textures/{}.dds'.format(self.gamedata, relpath))
        return result

    def texture(self, relpath):
        result = self.__textures.get(relpath)
        if not result:
            self.__textures[relpath] = result = bpy.data.textures.new('texture', type='IMAGE')
            result.image = self.image(relpath)
        return result


def load_ogf4_m03(ogr, context, parent):
    load_ogf4_m10(ogr, context, parent)


def load_ogf4_m04(ogr, context, parent):
    vv, ii, tt, teximage = load_ogf4_m05_(ogr)
    c = rawr(cfrs(next(ogr), 0x6))  # OGF4_SWIDATA
    c.unpack('=IIII')
    sw_count = c.unpack('=I')[0]
    print(sw_count)
    for _ in range(sw_count):
        offset, num_tris, num_verts = c.unpack('=IHH')
        print(offset, num_tris, num_verts)
        render_model(context, parent, vv, ii[offset//3:], tt, teximage)  # load only first LOD
        break


def load_ogf4_m05_(ogr):
    c = rawr(cfrs(next(ogr), Chunks.OGF4_TEXTURE))
    teximage = c.unpack_asciiz()
    c.unpack_asciiz()  # shader
    c = rawr(cfrs(next(ogr), Chunks.OGF4_VERTICES))
    vertex_format, vertices_count = c.unpack('=II')
    vv, nn, tt = [], [], []
    if vertex_format == 0x12071980 or vertex_format == 0x1:  # OGF4_VERTEXFORMAT_FVF_1L or OGF4_VERTEXFORMAT_FVF_1L_CS
        for _ in range(vertices_count):
            v = c.unpack('=fff')
            vv.append(v)
            n = c.unpack('=fff')
            nn.append(n)
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            tt.append(c.unpack('=ff'))
            c.unpack('=I')
    elif vertex_format == 0x240e3300 or vertex_format == 0x2:  # OGF4_VERTEXFORMAT_FVF_2L or OGF4_VERTEXFORMAT_FVF_2L_CS
        for _ in range(vertices_count):
            c.unpack('=HH')
            vv.append(c.unpack('=fff'))
            nn.append(c.unpack('=fff'))
            c.unpack('=fff')  # tangen
            c.unpack('=fff')  # binorm
            c.unpack('=f')
            tt.append(c.unpack('=ff'))
    else:
        raise Exception('unexpected vertex format: {:#x}'.format(vertex_format))
        #~ print('vf:{:#x}, vc:{}'.format(vf, vc))
    c = rawr(cfrs(next(ogr), Chunks.OGF4_INDICES))
    ic = c.unpack('=I')[0]
    ii = []
    for _ in range(ic // 3):
        ii.append(c.unpack('=HHH'))
        #~ print('{},[],{}'.format(vv, ii))
    return vv, ii, tt, teximage


def load_ogf4_m05(ogr, context, parent):
    vv, ii, tt, teximage = load_ogf4_m05_(ogr)
    render_model(context, parent, vv, ii, tt, teximage)


def render_model(context, parent, vv, ii, tt, teximage):
    if bpy:
        # mesh
        bpy_mesh = bpy.data.meshes.new('mesh')
        bpy_mesh.from_pydata(vv, [], ii)
        # uv-map
        uvt = bpy_mesh.uv_textures.new(name='UV')
        uvl = bpy_mesh.uv_layers.active.data
        for p in bpy_mesh.polygons:
            for i in range(p.loop_start, p.loop_start + p.loop_total):
                uv = tt[bpy_mesh.loops[i].vertex_index]
                uvl[i].uv = (uv[0], 1-uv[1])
        # material
        if teximage:
            bpy_material = bpy.data.materials.new(context.object_name)
            bpy_texture = bpy_material.texture_slots.add()
            bpy_texture.texture = context.texture(teximage)
            img = bpy_texture.texture.image
            for f in uvt.data.values():
                f.image = img
            bpy_texture.texture_coords = 'UV'
            bpy_texture.use_map_color_diffuse = True
            bpy_mesh.materials.append(bpy_material)
        # object
        bpy_object = bpy.data.objects.new(context.object_name, bpy_mesh)
        bpy_object.parent = parent
        bpy.context.scene.objects.link(bpy_object)


def load_ogf4_m10(ogr, context, parent):
    def robb(r):
        return (
            r.unpack('=fffffffff'),  # obb.rotate
            r.unpack('=fff'),   # obb.translate
            r.unpack('=fff')    # obb.halfsize
        )
    bones = []
    bonemat = {}
    for cid, cdata in ogr:
        if cid == 0x12:     # OGF4_S_DESC
            c = rawr(cdata)
            c.unpack_asciiz()   # src
            c.unpack_asciiz()   # exptool
            c.unpack('=III')    # exptime, crttime, modtime
        elif cid == 0x02:   # OGF4_TEXTURE
            c = rawr(cdata)
            c.unpack_asciiz()   # texture
            c.unpack_asciiz()   # shader
        elif cid == 0x0A:   # OGF4_CHILDREN_L
            c = rawr(cdata)
            count = c.unpack('=I')
            for _ in range(count):
                c.unpack('=I')
        elif cid == 0x09:   # OGF4_CHILDREN
            if bpy:
                bpy_object = bpy.data.objects.new(context.object_name, None)
                bpy_object.parent = parent
                import math
                bpy_object.rotation_euler.x = math.pi/2
                bpy.context.scene.objects.link(bpy_object)
                parent = bpy_object
            for i, c in ogfr(cdata):
                load_ogf(c, context, parent)
        elif cid == 0x11:   # OGF4_S_USERDATA
            c = rawr(cdata)
            userdata = c.unpack_asciiz()
            print('userdata:{}'.format(userdata))
        #elif cid == 0x17:   # OGF4_S_LODS
        elif cid == 0x0D:   # OGF4_S_BONE_NAMES
            c = rawr(cdata)
            count = c.unpack('=I')[0]
            for _ in range(count):
                bone = (
                    c.unpack_asciiz(),  # name
                    c.unpack_asciiz(),  # parent
                    robb(c)
                )
                bones.append(bone)
        elif cid == 0x10:   # OGF4_S_IKDATA
            c = rawr(cdata)
            for bone in bones:
                version = c.unpack('=I')[0]
                if version != 0x1:  # OGF4_S_JOINT_IK_DATA_VERSION
                    raise Exception('unexpected ikdata version: {:#x}'.format(version))
                c.unpack_asciiz()   # gamemtl
                c.unpack('=HH')     # shape_type, shape_flags
                robb(c)             # shape_obb
                (c.unpack('=fff'), c.unpack('=f')[0])   # shape_sphere
                (c.unpack('=fff'), c.unpack('=fff'), c.unpack('=f')[0], c.unpack('=f')[0])  # shape_cylinder
                jik_type = c.unpack('=I')[0]

                def rjiklim(r):
                    return (
                        r.unpack('=ff'),
                        r.unpack('=f')[0],
                        r.unpack('=f')[0]
                    )
                jik_lims = (rjiklim(c), rjiklim(c), rjiklim(c))
                c.unpack('=ffIfff') # jik_spr, jik_dmp, jik_flags, jik_bf, jik_bt, jik_fri
                rot = c.unpack('=fff')
                ofs = c.unpack('=fff')
                c.unpack('=f')      # mass
                c.unpack('=fff')    # center of mass
                bonemat[bone[0]] = (rot, ofs, (jik_type, jik_lims))
        else:
            print('unknown chunk={:#x}'.format(cid))
    if bpy:
        import mathutils
        bpy_armature = bpy.data.armatures.new(context.object_name)
        bpy_armature_obj = bpy.data.objects.new(context.object_name, bpy_armature)
        bpy_armature_obj.parent = parent
        bpy.context.scene.objects.link(bpy_armature_obj)
        bpy.context.scene.objects.active = bpy_armature_obj
        matrices = {}
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in bones:
                name, parent, _ = bone
                bm = bonemat[name]
                mat = mathutils.Matrix.Translation(bm[1]) * mathutils.Euler(bm[0], 'ZXY').to_matrix().to_4x4()
                pm = matrices.get(parent, mathutils.Matrix.Identity(4))
                mat = pm * mat
                matrices[name] = mat
                bpy_bone = bpy_armature.edit_bones.new(name)
                tp = mat * mathutils.Vector()
                if parent:
                    bpy_bone.parent = bpy_armature.edit_bones[parent]
                    bpy_bone.head = bpy_bone.parent.tail
                else:
                    bpy_bone.head = tp - mathutils.Vector((0, -0.1, 0))
                bpy_bone.tail = tp
            bpy.ops.object.mode_set(mode='POSE')
            for bone in bones:
                name = bone[0]
                bpy_bone = bpy_armature_obj.pose.bones[name]
                bpy_constraint = bpy_bone.constraints.new('LIMIT_ROTATION')
                bpy_constraint.owner_space = 'LOCAL'
                jt, jl = bonemat[name][2]
                bpy_constraint.use_limit_z = True
                bpy_constraint.use_limit_x = True
                bpy_constraint.use_limit_y = True
                if jt != 0:   # 0=rigid
                    bpy_constraint.min_x = -jl[0][0][1]
                    bpy_constraint.max_x = -jl[0][0][0]
                    bpy_constraint.min_y = -jl[1][0][1]
                    bpy_constraint.max_y = -jl[1][0][0]
                    bpy_constraint.min_z = -jl[2][0][1]
                    bpy_constraint.max_z = -jl[2][0][0]
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')


def load_ogf4(h, ogr, context, parent):
    mt, shid = h.unpack('=BH')
    print('modeltype:{}, shaderid:{}'.format(mt, shid))
    h.unpack('=ffffff')  # bounding box
    h.unpack('=ffff')  # bounding sphere

    #noinspection PyUnusedLocal
    def unsupported(r, c, p):
        raise Exception('unsupported OGF model type: {}'.format(mt))
    return {
        3: load_ogf4_m03,
        4: load_ogf4_m04,
        5: load_ogf4_m05,
        10: load_ogf4_m10
    }.get(mt, unsupported)(ogr, context, parent)


def load_ogf(data, context, parent=None):
    ogr = ogfr(data)
    cr = rawr(cfrs(next(ogr), Chunks.OGF_HEADER))
    ver = cr.unpack('=B')[0]
    #~ print ('version:{}'.format(ver))

    #noinspection PyUnusedLocal
    def unsupported(h, _, p, oname):
        raise Exception('unsupported OGF format version: {}'.format(ver))
    return {
        4: load_ogf4
    }.get(ver, unsupported)(cr, ogr, context, parent)


def load(context):
    import io
    with io.open(context.file_name, mode='rb') as f:
        return load_ogf(f.read(), context)
