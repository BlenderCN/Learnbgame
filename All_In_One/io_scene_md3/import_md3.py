# TODO: different normals for shape keys
# TODO: merge vertices near sharp edges (there is a disconnected surface now)
# TODO: use_smooth=False for flat faces (all vertex normal equal)


import bpy
import mathutils
import os.path

from . import fmt_md3 as fmt


def guess_texture_filepath(modelpath, imagepath):
    fileexts = ('', '.png', '.tga', '.jpg', '.jpeg')
    modelpath = os.path.normpath(os.path.normcase(modelpath))
    modeldir, _ = os.path.split(modelpath)
    imagedir, imagename = os.path.split(os.path.normpath(os.path.normcase(imagepath)))
    previp = None
    ip = imagedir
    while ip != previp:
        if ip in modeldir:
            pos = modeldir.rfind(ip)
            nameguess = os.path.join(modeldir[:pos + len(ip)], imagedir[len(ip):], imagename)
            for ext in fileexts:
                yield nameguess + ext
        previp = ip
        ip, _ = os.path.split(ip)
    nameguess = os.path.join(modeldir, imagename)
    for ext in fileexts:
        yield nameguess + ext


def get_tag_matrix_basis(data):
    basis = mathutils.Matrix.Identity(4)
    for j in range(3):
        basis[j].xyz = data.axis[j::3]
    basis.translation = mathutils.Vector(data.origin)
    return basis


class MD3Importer:
    def __init__(self, context):
        self.context = context

    @property
    def scene(self):
        return self.context.scene

    def read_n_items(self, n, offset, func):
        self.file.seek(offset)
        return [func(i) for i in range(n)]

    def unpack(self, rtype):
        return rtype.funpack(self.file)

    def read_frame(self, i):
        return self.unpack(fmt.Frame)

    def create_tag(self, i):
        data = self.unpack(fmt.Tag)
        bpy.ops.object.add(type='EMPTY')
        tag = bpy.context.object
        tag.name = data.name
        tag.empty_draw_type = 'ARROWS'
        tag.rotation_mode = 'QUATERNION'
        tag.matrix_basis = get_tag_matrix_basis(data)
        return tag

    def read_tag_frame(self, i):
        tag = self.tags[i % self.header.nTags]
        data = self.unpack(fmt.Tag)
        tag.matrix_basis = get_tag_matrix_basis(data)
        frame = i // self.header.nTags
        tag.keyframe_insert('location', frame=frame, group='LocRot')
        tag.keyframe_insert('rotation_quaternion', frame=frame, group='LocRot')

    def read_surface_triangle(self, i):
        data = self.unpack(fmt.Triangle)
        ls = i * 3
        self.mesh.loops[ls].vertex_index = data.a
        self.mesh.loops[ls + 1].vertex_index = data.c  # swapped
        self.mesh.loops[ls + 2].vertex_index = data.b  # swapped
        self.mesh.polygons[i].loop_start = ls
        self.mesh.polygons[i].loop_total = 3
        self.mesh.polygons[i].use_smooth = True

    def read_surface_vert(self, i):
        data = self.unpack(fmt.Vertex)
        self.verts[i].co = mathutils.Vector((data.x, data.y, data.z))
        # ignoring data.normal here

    def read_surface_normals(self, i):
        data = self.unpack(fmt.Vertex)
        self.mesh.vertices[i].normal = mathutils.Vector(data.normal)

    def read_mesh_animation(self, obj, data, start_pos):
        obj.shape_key_add(name=self.frames[0].name)  # adding first frame, which is already loaded
        self.mesh.shape_keys.use_relative = False
        # TODO: ensure MD3 has linear frame interpolation
        for frame in range(1, data.nFrames):  # first frame skipped
            shape_key = obj.shape_key_add(name=self.frames[frame].name)
            self.verts = shape_key.data
            self.read_n_items(
                data.nVerts,
                start_pos + data.offVerts + frame * fmt.Vertex.size * data.nVerts,
                self.read_surface_vert)
        self.scene.objects.active = obj
        self.context.object.active_shape_key_index = 0
        bpy.ops.object.shape_key_retime()
        for frame in range(data.nFrames):
            self.mesh.shape_keys.eval_time = 10.0 * (frame + 1)
            self.mesh.shape_keys.keyframe_insert('eval_time', frame=frame)

    def read_surface_ST(self, i):
        data = self.unpack(fmt.TexCoord)
        return (data.s, data.t)

    def make_surface_UV_map(self, uv, uvdata):
        for poly in self.mesh.polygons:
            for i in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vidx = self.mesh.loops[i].vertex_index
                uvdata[i].uv = uv[vidx]

    def read_surface_shader(self, i):
        data = self.unpack(fmt.Shader)

        texture = bpy.data.textures.new(data.name, 'IMAGE')
        texture_slot = self.material.texture_slots.create(i)
        texture_slot.uv_layer = 'UVMap'
        texture_slot.use = True
        texture_slot.texture_coords = 'UV'
        texture_slot.texture = texture

        for fname in guess_texture_filepath(self.filename, data.name):
            if '\0' in fname:  # preventing ValueError: embedded null byte
                continue
            if os.path.isfile(fname):
                image = bpy.data.images.load(fname)
                texture.image = image
                break

    def read_surface(self, i):
        start_pos = self.file.tell()

        data = self.unpack(fmt.Surface)
        assert data.magic == b'IDP3'
        assert data.nFrames == self.header.nFrames
        assert data.nShaders <= 256
        if data.nVerts > 4096:
            print('Warning: md3 surface contains too many vertices')
        if data.nTris > 8192:
            print('Warning: md3 surface contains too many triangles')

        self.mesh = bpy.data.meshes.new(data.name)
        self.mesh.vertices.add(count=data.nVerts)
        self.mesh.polygons.add(count=data.nTris)
        self.mesh.loops.add(count=data.nTris * 3)

        self.read_n_items(data.nTris, start_pos + data.offTris, self.read_surface_triangle)
        self.verts = self.mesh.vertices
        self.read_n_items(data.nVerts, start_pos + data.offVerts, self.read_surface_vert)

        self.mesh.validate()
        self.mesh.calc_normals()

        self.material = bpy.data.materials.new('Main')
        self.mesh.materials.append(self.material)

        self.mesh.uv_textures.new('UVMap')
        self.make_surface_UV_map(
            self.read_n_items(data.nVerts, start_pos + data.offST, self.read_surface_ST),
            self.mesh.uv_layers['UVMap'].data)

        self.read_n_items(data.nShaders, start_pos + data.offShaders, self.read_surface_shader)

        obj = bpy.data.objects.new(data.name, self.mesh)
        self.scene.objects.link(obj)

        if data.nFrames > 1:
            self.read_mesh_animation(obj, data, start_pos)

        self.file.seek(start_pos + data.offEnd)

    def post_settings(self):
        self.scene.frame_set(0)
        self.scene.game_settings.material_mode = 'GLSL'  # TODO: questionable
        bpy.ops.object.lamp_add(type='SUN')  # TODO: questionable

    def __call__(self, filename):
        self.filename = filename
        with open(filename, 'rb') as file:
            self.file = file

            self.header = self.unpack(fmt.Header)
            assert self.header.magic == fmt.MAGIC
            assert self.header.version == fmt.VERSION

            bpy.ops.scene.new()
            self.scene.name = self.header.modelname
            # TODO: start from 1?
            self.scene.frame_start = 0
            self.scene.frame_end = self.header.nFrames - 1

            self.frames = self.read_n_items(self.header.nFrames, self.header.offFrames, self.read_frame)
            self.tags = self.read_n_items(self.header.nTags, self.header.offTags, self.create_tag)
            if self.header.nFrames > 1:
                self.read_n_items(self.header.nTags * self.header.nFrames, self.header.offTags, self.read_tag_frame)
            self.read_n_items(self.header.nSurfaces, self.header.offSurfaces, self.read_surface)

        self.post_settings()
